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
from config.prompt_templates import PromptTemplates
from config.settings import settings
from llm.gemini_client import call_gemini
from tools.file_utils import guardar_fichero_texto, detectar_lenguaje_y_extension, limpiar_codigo_markdown
from services.azure_devops_service import azure_service
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

    # Construir contexto adicional con correcciones necesarias
    contexto_adicional = ""
    
    # Añadir traceback si hay errores de ejecución
    if state['traceback']:
        contexto_adicional += f"\nTraceback para corrección de errores de ejecución:\n{state['traceback']}\n"
        logger.info("🔧 Corrigiendo errores de ejecución basados en traceback")
    
    # Añadir issues de SonarQube si hay problemas de calidad
    if state.get('sonarqube_issues'):
        contexto_adicional += f"\nInstrucciones de corrección de calidad (SonarQube):\n{state['sonarqube_issues']}\n"
        logger.info("🔧 Corrigiendo issues de calidad de código (SonarQube)")
    
    # Añadir código previo si existe para facilitar la corrección
    if state.get('codigo_generado') and (state['traceback'] or state.get('sonarqube_issues')):
        contexto_adicional += f"\nCódigo anterior a corregir:\n{state['codigo_generado']}\n"
        logger.debug("Incluyendo código anterior para contexto de corrección")

    # Usar ChatPromptTemplate
    logger.debug("🔗 Usando ChatPromptTemplate de LangChain")
    prompt_formateado = PromptTemplates.format_desarrollador(
        requisitos_formales=state['requisitos_formales'],
        contexto_adicional=contexto_adicional
    )

    start_time = time.time()
    respuesta_llm = call_gemini(prompt_formateado, "")
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
    codigo_limpio = limpiar_codigo_markdown(state['codigo_generado'])
    
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
            # Usar servicio centralizado para crear Tasks
            impl_task_id, test_task_id = azure_service.create_implementation_tasks(
                state=state,
                lenguaje=lenguaje
            )
            
            # Guardar IDs en el estado
            if impl_task_id:
                state['azure_implementation_task_id'] = impl_task_id
            if test_task_id:
                state['azure_testing_task_id'] = test_task_id
            
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
