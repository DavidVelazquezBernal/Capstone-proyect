"""Agente: Desarrollador
Responsable de generar código según requisitos formales y corregir errores.
Corrige tanto errores de ejecución (traceback) como problemas de calidad (SonarQube).
Crea Tasks en Azure DevOps para implementación y testing.
Crea branch en GitHub para análisis de SonarCloud.
"""

import re
import time
import json
from datetime import datetime
from models.state import AgentState
from config.prompts import Prompts
from config.prompt_templates import PromptTemplates
from config.settings import settings
from llm.gemini_client import call_gemini
from tools.file_utils import guardar_fichero_texto, detectar_lenguaje_y_extension, limpiar_codigo_markdown, extraer_nombre_archivo
from services.azure_devops_service import azure_service
from services.github_service import github_service
from utils.logger import setup_logger, log_agent_execution, log_llm_call, log_file_operation
from utils.agent_decorators import agent_execution_context

logger = setup_logger(__name__, level=settings.get_log_level(), agent_mode=True)


def desarrollador_node(state: AgentState) -> AgentState:
    """
    Nodo del Desarrollador.
    Genera código que satisface los requisitos formales o corrige errores.
    Puede corregir errores de ejecución (traceback) o issues de calidad (sonarqube_issues).
    """

    with agent_execution_context("💻 DESARROLLADOR", logger):
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
        nombre_archivo = f"2_desarrollador_req{state['attempt_count']}_debug{state['debug_attempt_count']}_sq{state['sonarqube_attempt_count']}{extension}"
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
        
        # === INICIO: Crear branch en GitHub  ===
        if settings.GITHUB_ENABLED:
            import os
            
            # Solo crear branch si no existe uno previo o si es una corrección de SonarQube
            branch_existente = state.get('github_branch_name')
            es_correccion_sonarqube = state['sonarqube_attempt_count'] > 0
            
            if not branch_existente or es_correccion_sonarqube:
                logger.info("🐙 Creando branch en GitHub...")
                
                try:
                    # Generar nombre del branch
                    nombre_base = extraer_nombre_archivo(state.get('requisitos_formales', ''))
                    # Sanitizar nombre_base para evitar caracteres inválidos en el branch
                    nombre_base_sanitizado = github_service.sanitize_branch_name(nombre_base)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    branch_name = f"AI_Generated_Developer_{nombre_base_sanitizado}_{timestamp}"
                    
                    # 1. Copiar archivo al repositorio local (GITHUB_REPO_PATH/src/)
                    repo_path = settings.GITHUB_REPO_PATH
                    src_dir = os.path.join(repo_path, "src")
                    os.makedirs(src_dir, exist_ok=True)
                    
                    codigo_local_path = os.path.join(src_dir, f"{nombre_base}{extension}")
                    with open(codigo_local_path, 'w', encoding='utf-8') as f:
                        f.write(codigo_limpio)
                    logger.info(f"📄 Código copiado a: {codigo_local_path}")

                    state['github_local_code_path'] = codigo_local_path
                    
                    # 2. Preparar archivo para commit remoto
                    codigo_filename = f"src/{nombre_base}{extension}"
                    files_to_commit = {
                        codigo_filename: codigo_limpio
                    }

                    state['github_code_filename'] = codigo_filename
                    
                    commit_message = f"feat: Add {nombre_base} implementation\n{nombre_base}\nAttempt: req{state['attempt_count']}_debug{state['debug_attempt_count']}_sq{state['sonarqube_attempt_count']}\n\nGenerated by AI Developer Agent"
                    
                    # 3. Crear branch, commit y push a remoto (GitHub API)
                    success_commit, commit_sha = github_service.create_branch_and_commit(
                        branch_name=branch_name,
                        files=files_to_commit,
                        commit_message=commit_message
                    )
                    
                    if success_commit:
                        state['github_branch_name'] = branch_name
                        logger.info(f"✅ Branch '{branch_name}' creado y pusheado a GitHub")
                        logger.info(f"   📄 Archivo remoto: {codigo_filename}")
                        logger.info(f"   🔗 Commit SHA: {commit_sha[:7]}")
                    else:
                        logger.warning("⚠️ No se pudo crear branch en GitHub")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Error al crear branch en GitHub: {e}")
                    logger.debug(f"Stack trace: {e}", exc_info=True)
        # === FIN: Crear branch en GitHub ===
        
        log_agent_execution(logger, "Desarrollador", "completado", {
            "archivo": nombre_archivo,
            "lenguaje": lenguaje,
            "guardado": resultado
        })

        return state
