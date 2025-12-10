"""Agente 3: Codificador/Corrector
Responsable de generar código según requisitos formales y corregir errores.
Corrige tanto errores de ejecución (traceback) como problemas de calidad (SonarQube).
"""

import re
import time
from models.state import AgentState
from config.prompts import Prompts
from config.settings import settings
from llm.gemini_client import call_gemini
from tools.file_utils import guardar_fichero_texto, detectar_lenguaje_y_extension
from utils.logger import setup_logger, log_agent_execution, log_llm_call, log_file_operation

logger = setup_logger(__name__, level=settings.get_log_level(), agent_mode=True)


def codificador_node(state: AgentState) -> AgentState:
    """
    Nodo del Codificador.
    Genera código que satisface los requisitos formales o corrige errores.
    Puede corregir errores de ejecución (traceback) o issues de calidad (sonarqube_issues).
    """
    log_agent_execution(logger, "Codificador", "iniciado", {
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
    nombre_archivo = f"3_codificador_req{state['attempt_count']}_debug{state['debug_attempt_count']}_sq{state['sonarqube_attempt_count']}{extension}"
    resultado = guardar_fichero_texto(
        nombre_archivo,
        codigo_limpio,
        directorio=settings.OUTPUT_DIR
    )
    
    log_agent_execution(logger, "Codificador", "completado", {
        "archivo": nombre_archivo,
        "lenguaje": lenguaje,
        "guardado": resultado
    })

    return state
