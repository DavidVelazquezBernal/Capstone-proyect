"""Agente: Desarrollador
Responsable de generar código según requisitos formales y corregir errores.
Corrige tanto errores de ejecución (traceback) como problemas de calidad (SonarQube).
Crea Tasks en Azure DevOps para implementación y testing.
"""

import re
import time
import json
from models.state import AgentState
from config.prompts import Prompts
from config.settings import settings
from llm.gemini_client import call_gemini
from tools.file_utils import guardar_fichero_texto, detectar_lenguaje_y_extension
from tools.azure_devops_integration import AzureDevOpsClient, estimate_effort_hours
from utils.logger import setup_logger, log_agent_execution, log_llm_call, log_file_operation

logger = setup_logger(__name__, level=settings.get_log_level(), agent_mode=True)


def desarrollador_node(state: AgentState) -> AgentState:
    """
    Nodo del Desarrollador.
    Genera código que satisface los requisitos formales o corrige errores.
    Puede corregir errores de ejecución (traceback) o issues de calidad (sonarqube_issues).
    """
    print()  # Línea en blanco para separación visual
    logger.info("=" * 60)
    logger.info("💻 DESARROLLADOR - INICIO")
    logger.info("=" * 60)

    log_agent_execution(logger, "Desarrollador", "iniciado", {
        "requisito_id": state['attempt_count'],
        "debug_attempt": state['debug_attempt_count'],
        "sonarqube_attempt": state['sonarqube_attempt_count']
    })

    # Construir contexto con todas las correcciones necesarias
    contexto_llm = f"Requisitos Formales (JSON): {state['requisitos_formales']}\n"
    
    # Añadir traceback si hay errores de ejecución
    if state['traceback']:
        contexto_llm += f"\nTraceback para corrección de errores de ejecución:\n{state['traceback']}\n"
        logger.info("🔧 Corrigiendo errores de ejecución basados en traceback")
    
    # Añadir issues de SonarQube si hay problemas de calidad
    if state.get('sonarqube_issues'):
        contexto_llm += f"\nInstrucciones de corrección de calidad (SonarQube):\n{state['sonarqube_issues']}\n"
        logger.info("🔧 Corrigiendo issues de calidad de código (SonarQube)")
    
    # Añadir código previo si existe para facilitar la corrección
    if state.get('codigo_generado') and (state['traceback'] or state.get('sonarqube_issues')):
        contexto_llm += f"\nCódigo anterior a corregir:\n{state['codigo_generado']}\n"
        logger.debug("Incluyendo código anterior para contexto de corrección")

    start_time = time.time()
    respuesta_llm = call_gemini(Prompts.CODIFICADOR, contexto_llm)
    duration = time.time() - start_time
    
    log_llm_call(logger, "codificacion", duration=duration)

    # El código ya viene formateado desde el LLM
    state['codigo_generado'] = respuesta_llm
    state['traceback'] = ""
    
    logger.info("Código generado/corregido exitosamente")
    logger.debug(f"Código generado: {state['codigo_generado'][:200]}...")

    # Guardar output en archivo con extensión correcta
    lenguaje, extension, patron_limpieza = detectar_lenguaje_y_extension(
        state.get('requisitos_formales', '')
    )
    codigo_limpio = re.sub(patron_limpieza, '', state['codigo_generado']).strip()
    
    # Incluir intento de requisito, de debug y de sonarqube
    nombre_archivo = f"3_desarrollador_req{state['attempt_count']}_debug{state['debug_attempt_count']}_sq{state['sonarqube_attempt_count']}{extension}"
    resultado = guardar_fichero_texto(
        nombre_archivo,
        codigo_limpio,
        directorio=settings.OUTPUT_DIR
    )
    
    # === INICIO: Crear Tasks en Azure DevOps (solo en primera generación) ===
    if (settings.AZURE_DEVOPS_ENABLED and state.get('azure_pbi_id') and 
        state['debug_attempt_count'] == 0 and state['sonarqube_attempt_count'] == 0):
        
        logger.info("🔷 Creando Tasks en Azure DevOps para implementación y testing...")
        
        try:
            azure_client = AzureDevOpsClient()
            pbi_id = state['azure_pbi_id']
            
            # === VERIFICAR SI YA EXISTEN TASKS PARA ESTE PBI ===
            logger.info(f"🔍 Verificando tasks existentes para el PBI #{pbi_id}...")
            existing_children = azure_client.get_child_work_items(pbi_id)
            
            # Filtrar por tipo Task y tag AI-Generated
            existing_tasks = [
                child for child in existing_children 
                if child['fields'].get('System.WorkItemType') == 'Task' and
                   'AI-Generated' in child['fields'].get('System.Tags', '')
            ]
            
            if existing_tasks:
                logger.warning(f"⚠️ Ya existen {len(existing_tasks)} Task(s) AI-Generated asociadas al PBI #{pbi_id}")
                for task in existing_tasks:
                    task_title = task['fields'].get('System.Title', 'Sin título')
                    logger.info(f"   📋 Task #{task['id']}: {task_title}")
                
                logger.info(f"♻️ Reutilizando Tasks existentes en lugar de crear duplicados")
                
                # Guardar IDs de tasks existentes en el estado
                for task in existing_tasks:
                    task_title = task['fields'].get('System.Title', '')
                    if 'Implementar' in task_title or 'Implementation' in task_title:
                        state['azure_implementation_task_id'] = task['id']
                        logger.info(f"   ✅ Task de Implementación reutilizada: #{task['id']}")
                    elif 'test' in task_title.lower():
                        state['azure_testing_task_id'] = task['id']
                        logger.info(f"   ✅ Task de Testing reutilizada: #{task['id']}")
            else:
                # No existen tasks, crear nuevas
                logger.info("✨ No se encontraron Tasks existentes, creando nuevas...")
                
                # Parsear requisitos formales para obtener detalles
                try:
                    requisitos = json.loads(state['requisitos_formales'])
                    objetivo = requisitos.get('objetivo_funcional', 'Implementar funcionalidad')
                    nombre_funcion = requisitos.get('nombre_funcion', 'función')
                    lenguaje_req = requisitos.get('lenguaje_version', lenguaje)
                except:
                    objetivo = "Implementar funcionalidad según requisitos"
                    nombre_funcion = "función/clase"
                    lenguaje_req = lenguaje
                
                # TASK 1: Implementación de código
                task_implementation = azure_client.create_task(
                    title=f"[AI-Generated] Implementar {nombre_funcion}",
                    description=f"""
                    <h3>Objetivo</h3>
                    <p>{objetivo}</p>
                    
                    <h3>Especificaciones Técnicas</h3>
                    <ul>
                        <li><strong>Lenguaje:</strong> {lenguaje_req}</li>
                        <li><strong>Función/Clase:</strong> <code>{nombre_funcion}</code></li>
                        <li><strong>Archivo generado:</strong> <code>{nombre_archivo}</code></li>
                    </ul>
                    
                    <h3>Tareas</h3>
                    <ul>
                        <li>✅ Código generado automáticamente por IA</li>
                        <li>⏳ Revisar implementación</li>
                        <li>⏳ Validar lógica de negocio</li>
                        <li>⏳ Verificar manejo de errores</li>
                    </ul>
                    
                    <h3>Entregables</h3>
                    <ul>
                        <li>Código fuente implementado y revisado</li>
                        <li>Documentación inline (comentarios)</li>
                    </ul>
                    
                    <hr/>
                    <p><em>🤖 Task creada automáticamente por el sistema multiagente</em></p>
                    """,
                    parent_id=pbi_id,
                    remaining_work=estimate_effort_hours("implementation"),
                    tags=["AI-Generated", "Implementation", lenguaje, "Auto-Created"]
                )
                
                if task_implementation:
                    logger.info(f"✅ Task de Implementación creada: #{task_implementation['id']}")
                    logger.info(f"   📋 {task_implementation['fields']['System.Title']}")
                    # Guardar ID en el estado
                    state['azure_implementation_task_id'] = task_implementation['id']
                
                # TASK 2: Generación de Unit Tests
                task_testing = azure_client.create_task(
                    title=f"[AI-Generated] Crear unit tests para {nombre_funcion}",
                    description=f"""
                    <h3>Objetivo</h3>
                    <p>Crear suite completa de unit tests para validar la implementación de {nombre_funcion}</p>
                    
                    <h3>Especificaciones de Testing</h3>
                    <ul>
                        <li><strong>Framework:</strong> {"vitest" if lenguaje.lower() == "typescript" else "pytest"}</li>
                        <li><strong>Cobertura objetivo:</strong> &gt;80%</li>
                        <li><strong>Código a testear:</strong> <code>{nombre_archivo}</code></li>
                    </ul>
                    
                    <h3>Casos de Prueba Requeridos</h3>
                    <ul>
                        <li>⏳ Tests para flujo normal (happy path)</li>
                        <li>⏳ Tests para casos límite (edge cases)</li>
                        <li>⏳ Tests para manejo de errores</li>
                        <li>⏳ Tests para validación de entrada</li>
                        <li>⏳ Tests para validación de salida</li>
                    </ul>
                    
                    <h3>Criterios de Aceptación</h3>
                    <ul>
                        <li>Todos los tests deben pasar (green)</li>
                        <li>Cobertura de código &gt;80%</li>
                        <li>No hay warnings o deprecations</li>
                        <li>Tests ejecutables con un solo comando</li>
                    </ul>
                    
                    <h3>Entregables</h3>
                    <ul>
                        <li>Archivo de tests unitarios</li>
                        <li>Reporte de cobertura</li>
                        <li>Documentación de ejecución</li>
                    </ul>
                    
                    <hr/>
                    <p><em>🤖 Task creada automáticamente por el sistema multiagente</em></p>
                    <p><em>📊 Los tests serán generados automáticamente en el siguiente paso del workflow</em></p>
                    """,
                    parent_id=pbi_id,
                    remaining_work=estimate_effort_hours("testing"),
                    tags=["AI-Generated", "Testing", "Unit-Tests", lenguaje, "Auto-Created"]
                )
                
                if task_testing:
                    logger.info(f"✅ Task de Testing creada: #{task_testing['id']}")
                    logger.info(f"   🧪 {task_testing['fields']['System.Title']}")
                    # Guardar ID en el estado
                    state['azure_testing_task_id'] = task_testing['id']
                
                if task_implementation and task_testing:
                    logger.info(f"🎯 2 Tasks creadas y asociadas al PBI #{pbi_id}")
            
        except Exception as e:
            logger.warning(f"⚠️ No se pudieron crear Tasks en Azure DevOps: {e}")
            logger.debug(f"Stack trace: {e}", exc_info=True)
    # === FIN: Creación de Tasks en Azure DevOps ===
    
    log_agent_execution(logger, "Desarrollador", "completado", {
        "archivo": nombre_archivo,
        "lenguaje": lenguaje,
        "guardado": resultado
    })

    return state
