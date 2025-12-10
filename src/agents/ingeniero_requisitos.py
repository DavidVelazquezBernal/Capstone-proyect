"""
Agente 1: Ingeniero de Requisitos
Responsable de clarificar y refinar los requisitos iniciales o feedback del stakeholder.
"""

import re
import time
from models.state import AgentState
from config.prompts import Prompts
from config.settings import settings
from llm.gemini_client import call_gemini
from tools.file_utils import guardar_fichero_texto
from utils.logger import setup_logger, log_agent_execution, log_llm_call, log_file_operation

# Configurar logger para este agente
logger = setup_logger(__name__, level=settings.get_log_level(), agent_mode=True)


def ingeniero_de_requisitos_node(state: AgentState) -> AgentState:
    """
    Nodo del Ingeniero de Requisitos.
    Convierte el requisito inicial o feedback en una especificación clara y verificable.
    """
    logger.info("=" * 60)
    logger.info("🙋‍♂️ INGENIERO DE REQUISITOS - INICIO")
    logger.info("=" * 60)
    
    # Log del contexto de entrada
    log_agent_execution(
        logger,
        "Ingeniero Requisitos",
        "Procesando requisito",
        {
            "intento": f"{state['attempt_count'] + 1}/{state['max_attempts']}",
            "tiene_feedback": bool(state['feedback_stakeholder'])
        }
    )

    contexto_llm = (
        f"Prompt Inicial: {state['prompt_inicial']}\n"
        f"Feedback Anterior: {state['feedback_stakeholder']}"
    )
    
    logger.debug(f"Contexto LLM: {contexto_llm[:200]}...")

    # Llamar al LLM con medición de tiempo
    start_time = time.time()
    respuesta_llm = call_gemini(Prompts.INGENIERO_REQUISITOS, contexto_llm)
    duration = time.time() - start_time
    
    log_llm_call(logger, "INGENIERO_REQUISITOS", duration=duration)

    # Procesar respuesta
    state['requisito_clarificado'] = re.sub(
        r'## REQUISITO CLARIFICADO\n', '', respuesta_llm
    ).strip()
    state['feedback_stakeholder'] = ""
    state['attempt_count'] += 1
    state['debug_attempt_count'] = 0
    state['sonarqube_attempt_count'] = 0
    
    logger.info(f"✅ Requisito clarificado exitosamente")
    logger.info(f"Intento: {state['attempt_count']}/{state['max_attempts']}")
    logger.debug(f"Output (primeros 200 chars): {state['requisito_clarificado'][:200]}...")
    
    # Guardar output en archivo
    nombre_archivo = f"1_ingeniero_requisitos_intento_{state['attempt_count']}.txt"
    success = guardar_fichero_texto(
        nombre_archivo,
        state['requisito_clarificado'],
        directorio=settings.OUTPUT_DIR
    )
    
    log_file_operation(
        logger,
        "guardar",
        f"{settings.OUTPUT_DIR}/{nombre_archivo}",
        success=success
    )
    
    logger.info("🙋‍♂️ INGENIERO DE REQUISITOS - FIN")
    logger.info("=" * 60)
    
    return state
