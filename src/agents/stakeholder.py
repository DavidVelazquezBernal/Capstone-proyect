"""
Agente 5: Stakeholder
Responsable de validar que el código cumple la visión de negocio.
"""

import re
import time
from models.state import AgentState
from config.prompts import Prompts
from config.settings import settings
from llm.gemini_client import call_gemini
from tools.file_utils import guardar_fichero_texto
from utils.logger import setup_logger, log_agent_execution, log_llm_call

logger = setup_logger(__name__, level=settings.get_log_level(), agent_mode=True)


def stakeholder_node(state: AgentState) -> AgentState:
    """
    Nodo del Stakeholder.
    Valida si el código cumple con la intención de negocio.
    """
    logger.info("")
    logger.info("=" * 60)
    logger.info("🙋‍♂️ STAKEHOLDER - INICIO")
    logger.info("=" * 60)

    log_agent_execution(logger, "✅ Stakeholder", "iniciado", {
        "intento": state['attempt_count'],
        "max_intentos": state['max_attempts']
    })

    # Comprobar si se excedió el límite de intentos
    if state['attempt_count'] >= state['max_attempts']:
        state['validado'] = False
        logger.error(f"❌ LÍMITE DE INTENTOS EXCEDIDO ({state['max_attempts']}). PROYECTO FALLIDO.")
        
        log_agent_execution(logger, "Stakeholder", "completado", {
            "resultado": "fallido",
            "razon": "limite_intentos_excedido"
        })
        return state

    contexto_llm = (
        f"Código aprobado técnicamente: {state['codigo_generado']}\n"
        f"Requisitos Formales (JSON): {state['requisitos_formales']}"
    )
    
    logger.info("🔍 Validando código con stakeholder...")
    start_time = time.time()
    respuesta_llm = call_gemini(Prompts.STAKEHOLDER, contexto_llm)
    duration = time.time() - start_time
    
    log_llm_call(logger, "validacion_stakeholder", duration=duration)

    # Lógica de transición de validación
    if "VALIDADO" in respuesta_llm:
        state['validado'] = True
        logger.info("✅ Resultado: VALIDADO. Proyecto Terminado.")
        
        # Guardar validación exitosa
        guardar_fichero_texto(
            f"5_stakeholder_intento_{state['attempt_count']}_VALIDADO.txt",
            f"Validación: APROBADO\n\nRespuesta:\n{respuesta_llm}",
            directorio=settings.OUTPUT_DIR
        )
        
        # === AZURE DEVOPS: Adjuntar código final cuando se valida ===
        if state.get('azure_pbi_id') and state.get('azure_implementation_task_id'):
            _adjuntar_codigo_final_azure_devops(state)
        # === FIN: Adjuntar código final a Azure DevOps ===
        
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

    return state


def _adjuntar_codigo_final_azure_devops(state: AgentState) -> None:
    """
    Adjunta el archivo codigo_final.ts al PBI y a la Task de Implementación en Azure DevOps.
    
    Args:
        state: Estado compartido con azure_pbi_id y azure_implementation_task_id
    """
    try:
        from tools.azure_devops_integration import AzureDevOpsClient
        from tools.file_utils import detectar_lenguaje_y_extension
        import os
        
        # Detectar lenguaje para construir nombre del archivo
        lenguaje, extension, _ = detectar_lenguaje_y_extension(
            state.get('requisitos_formales', '')
        )
        
        # Ruta del archivo codigo_final
        codigo_final_path = os.path.join(settings.OUTPUT_DIR, f"codigo_final{extension}")
        
        # Validar que el archivo existe
        if not os.path.exists(codigo_final_path):
            logger.warning(f"⚠️ Archivo codigo_final{extension} no encontrado")
            return
        
        azure_client = AzureDevOpsClient()
        
        pbi_id = state['azure_pbi_id']
        task_id = state['azure_implementation_task_id']
        
        logger.info("")
        logger.info("=" * 60)
        logger.info("📎 ADJUNTANDO CÓDIGO FINAL A AZURE DEVOPS")
        logger.info("-" * 60)
        logger.info(f"📄 Archivo: codigo_final{extension}")
        logger.info(f"🎯 PBI: #{pbi_id}")
        logger.info(f"⚙️ Task Implementación: #{task_id}")
        
        # Adjuntar al PBI
        success_pbi = azure_client.attach_file(
            work_item_id=pbi_id,
            file_path=codigo_final_path,
            comment="✅ Código final validado por el Stakeholder - Listo para producción"
        )
        
        if success_pbi:
            logger.info(f"✅ Código final adjuntado al PBI #{pbi_id}")
        else:
            logger.warning(f"⚠️ No se pudo adjuntar al PBI #{pbi_id}")
        
        # Adjuntar a la Task de Implementación
        success_task = azure_client.attach_file(
            work_item_id=task_id,
            file_path=codigo_final_path,
            comment=f"✅ Implementación completa y validada - {os.path.getsize(codigo_final_path)} bytes"
        )
        
        if success_task:
            logger.info(f"✅ Código final adjuntado a Task #{task_id}")
        else:
            logger.warning(f"⚠️ No se pudo adjuntar a Task #{task_id}")
        
        if success_pbi and success_task:
            logger.info("🎉 Código final adjuntado exitosamente a ambos work items")
        
        logger.info("=" * 60)
        
    except Exception as e:
        logger.warning(f"⚠️ No se pudo adjuntar código final a Azure DevOps: {e}")
        logger.debug(f"Stack trace: {e}", exc_info=True)
