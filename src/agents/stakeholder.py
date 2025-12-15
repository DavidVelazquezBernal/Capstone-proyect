"""
Agente 5: Stakeholder
Responsable de validar que el código cumple la visión de negocio.
"""

import re
import time
from models.state import AgentState
from config.prompts import Prompts
from config.prompt_templates import PromptTemplates
from config.settings import settings
from llm.gemini_client import call_gemini
from tools.file_utils import guardar_fichero_texto
from services.azure_devops_service import azure_service
from utils.logger import setup_logger, log_agent_execution, log_llm_call

logger = setup_logger(__name__, level=settings.get_log_level(), agent_mode=True)


def stakeholder_node(state: AgentState) -> AgentState:
    """
    Nodo del Stakeholder.
    Valida si el código cumple con la intención de negocio.
    """
    print()  # Línea en blanco para separación visual
    logger.info("=" * 60)
    logger.info("STAKEHOLDER - INICIO")
    logger.info("=" * 60)

    log_agent_execution(logger, "Stakeholder", "iniciado", {
        "intento": state['attempt_count'],
        "max_intentos": state['max_attempts']
    })

    # Comprobar si se excedió el límite de intentos (después de la última iteración)
    if state['attempt_count'] > state['max_attempts']:
        state['validado'] = False
        logger.error(f"❌ LÍMITE DE INTENTOS EXCEDIDO ({state['max_attempts']}). PROYECTO FALLIDO.")
        
        log_agent_execution(logger, "Stakeholder", "completado", {
            "resultado": "fallido",
            "razon": "limite_intentos_excedido"
        })
        return state

    logger.debug("🔗 Usando ChatPromptTemplate de LangChain")
    prompt_formateado = PromptTemplates.format_stakeholder(
        requisitos_formales=state['requisitos_formales'],
        codigo_generado=state['codigo_generado'],
        resultado_tests=state.get('resultado_tests', '')
    )
    
    logger.info(f"🔍 Validando código con stakeholder (Intento {state['attempt_count']}/{state['max_attempts']})...")
    start_time = time.time()
    respuesta_llm = call_gemini(prompt_formateado, "")
    duration = time.time() - start_time
    
    log_llm_call(logger, "validacion_stakeholder", duration=duration)

    # Lógica de transición de validación
    if "VALIDADO" in respuesta_llm:
        state['validado'] = True
        logger.info("Resultado: VALIDADO. Proyecto Terminado.")
        
        # Guardar validación exitosa
        guardar_fichero_texto(
            f"5_stakeholder_intento_{state['attempt_count']}_VALIDADO.txt",
            f"Validación: APROBADO\n\nRespuesta:\n{respuesta_llm}",
            directorio=settings.OUTPUT_DIR
        )
        
        # === AZURE DEVOPS: Adjuntar código final cuando se valida ===
        if state.get('azure_pbi_id') and state.get('azure_implementation_task_id'):
            try:
                azure_service.attach_final_code_to_work_items(state)
            except Exception as e:
                logger.warning(f"⚠️ Error al adjuntar código final: {e}")
        # === FIN: Adjuntar código final a Azure DevOps ===
        
        # === INICIO: Actualizar estados a "Done" en Azure DevOps ===
        if settings.AZURE_DEVOPS_ENABLED:
            try:
                azure_service.update_all_work_items_to_done(state)
            except Exception as e:
                logger.warning(f"⚠️ Error al actualizar estados: {e}")
        # === FIN: Actualizar estados a "Done" ===
        
        # === INICIO: Generar y agregar Release Note al PBI ===
        if settings.AZURE_DEVOPS_ENABLED and state.get('azure_pbi_id'):
            try:
                azure_service.generate_and_add_release_note(state)
            except Exception as e:
                logger.warning(f"⚠️ Error al generar Release Note: {e}")
        # === FIN: Generar Release Note ===
        
        log_agent_execution(logger, "Stakeholder", "completado", {
            "resultado": "aprobado",
            "intento": state['attempt_count']
        })
    else:
        state['validado'] = False
        # Extraer el feedback de rechazo
        feedback_match = re.search(r'Motivo: (.*)', respuesta_llm, re.DOTALL)
        if feedback_match:
            state['feedback_stakeholder'] = feedback_match.group(1).strip()
        
        logger.warning("❌ Resultado: RECHAZADO.")
        logger.info(f"📋 Motivo: {state['feedback_stakeholder']}")
        logger.info("➡️ Volviendo a Ingeniero de Requisitos.")
        
        # Guardar validación rechazada
        guardar_fichero_texto(
            f"5_stakeholder_intento_{state['attempt_count']}_RECHAZADO.txt",
            f"Validación: RECHAZADO\n\nMotivo:\n{state['feedback_stakeholder']}\n\nRespuesta completa:\n{respuesta_llm}",
            directorio=settings.OUTPUT_DIR
        )
        
        log_agent_execution(logger, "Stakeholder", "completado", {
            "resultado": "rechazado",
            "motivo": state['feedback_stakeholder'][:100],
            "intento": state['attempt_count']
        })

    logger.info("STAKEHOLDER - FIN")
    logger.info("=" * 60)
    return state

