"""
Agente 2: Product Owner
Responsable de formalizar requisitos en especificaciones técnicas ejecutables.
"""

import time
from models.state import AgentState
from models.schemas import FormalRequirements
from config.prompts import Prompts
from config.settings import settings
from llm.gemini_client import call_gemini
from tools.file_utils import guardar_fichero_texto
from utils.logger import setup_logger, log_agent_execution, log_llm_call, log_file_operation

# Configurar logger para este agente
logger = setup_logger(__name__, level=settings.get_log_level(), agent_mode=True)


def product_owner_node(state: AgentState) -> AgentState:
    """
    Nodo del Product Owner.
    Transforma requisitos clarificados en especificación formal JSON validada.
    """
    logger.info("=" * 60)
    logger.info("💼 PRODUCT OWNER - INICIO")
    logger.info("=" * 60)
    
    log_agent_execution(
        logger,
        "Product Owner",
        "Formalizando requisitos",
        {"intento": state['attempt_count']}
    )

    contexto_llm = f"Requisito Clarificado: {state['requisito_clarificado']}"
    logger.debug(f"Contexto LLM: {contexto_llm[:200]}...")

    # Llamar al LLM con medición de tiempo
    start_time = time.time()
    respuesta_llm = call_gemini(
        Prompts.PRODUCT_OWNER, 
        contexto_llm, 
        response_schema=FormalRequirements
    )
    duration = time.time() - start_time
    
    log_llm_call(logger, "PRODUCT_OWNER", duration=duration)

    try:
        # Validar y almacenar la salida JSON del LLM
        req_data = FormalRequirements.model_validate_json(respuesta_llm)
        state['requisitos_formales'] = req_data.model_dump_json(indent=2)
        
        logger.info("✅ Requisitos formales generados y validados")
        logger.debug(f"Output JSON (primeros 200 chars): {state['requisitos_formales'][:200]}...")
        
        # Guardar output en archivo
        nombre_archivo = f"2_product_owner_intento_{state['attempt_count']}.json"
        success = guardar_fichero_texto(
            nombre_archivo,
            state['requisitos_formales'],
            directorio=settings.OUTPUT_DIR
        )
        
        log_file_operation(
            logger,
            "guardar",
            f"{settings.OUTPUT_DIR}/{nombre_archivo}",
            success=success
        )
        
    except Exception as e:
        logger.error(f"Error al validar JSON: {e}")
        state['requisitos_formales'] = (
            f"ERROR_PARSING: Fallo al validar JSON. {e}. "
            f"LLM Output: {respuesta_llm[:100]}"
        )
        logger.error("Fallo de parsing en Product Owner")

    logger.info("💼 PRODUCT OWNER - FIN")
    logger.info("=" * 60)
    
    return state
