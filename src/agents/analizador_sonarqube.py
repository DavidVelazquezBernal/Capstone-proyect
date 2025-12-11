"""
Agente: Analizador SonarQube
Responsable de verificar la calidad del código generado usando SonarQube antes de las pruebas funcionales.
"""

import re
import time
from models.state import AgentState
from config.prompts import Prompts
from config.settings import settings
from llm.gemini_client import call_gemini
from tools.file_utils import guardar_fichero_texto, detectar_lenguaje_y_extension
from tools.sonarqube_mcp import analizar_codigo_con_sonarqube, formatear_reporte_sonarqube, es_codigo_aceptable
from services.azure_devops_service import azure_service
from utils.logger import setup_logger, log_agent_execution, log_llm_call, log_file_operation

logger = setup_logger(__name__, level=settings.get_log_level(), agent_mode=True)



def analizador_sonarqube_node(state: AgentState) -> AgentState:
    """
    Nodo del Analizador SonarQube.
    Analiza la calidad del código generado y determina si cumple los estándares.
    """
    print()  # Línea en blanco para separación visual
    logger.info("=" * 60)
    logger.info("ANALIZADOR SONARQUBE - INICIO")
    logger.info("=" * 60)

    log_agent_execution(logger, "Analizador SonarQube", "iniciado", {
        "requisito_id": state['attempt_count'],
        "intento_sonarqube": state['sonarqube_attempt_count']
    })
    
    # === INICIO: Actualizar estado del Work Item de Implementación a "In Progress" ===
    if (settings.AZURE_DEVOPS_ENABLED and 
        state.get('azure_implementation_task_id') and 
        state['sonarqube_attempt_count'] == 0):  # Solo en el primer análisis
        
        try:
            task_id = state['azure_implementation_task_id']
            logger.info(f"🔄 Actualizando estado de Task de Implementación #{task_id} a 'In Progress'...")
            
            # Usar servicio centralizado
            success = azure_service.update_implementation_task_to_in_progress(task_id)
            
            if success:
                logger.info(f"✅ Task #{task_id} actualizada a 'In Progress'")
            else:
                logger.warning(f"⚠️ No se pudo actualizar el estado de la Task #{task_id}")
                
        except Exception as e:
            logger.warning(f"⚠️ Error al actualizar estado del work item: {e}")
            logger.debug(f"Stack trace: {e}", exc_info=True)
    # === FIN: Actualización de estado en Azure DevOps ===
    
    # Obtener información del código
    lenguaje, extension, patron_limpieza = detectar_lenguaje_y_extension(
        state.get('requisitos_formales', '')
    )
    codigo_limpio = re.sub(patron_limpieza, '', state['codigo_generado']).strip()
    
    # Generar nombre de archivo para análisis
    nombre_archivo = f"analisis_sonarqube_req{state['attempt_count']}_sq{state['sonarqube_attempt_count']}{extension}"
    
    logger.info(f"🔍 Analizando código con SonarQube - Archivo: {nombre_archivo}")
    
    # Analizar código con SonarQube
    resultado_analisis = analizar_codigo_con_sonarqube(codigo_limpio, nombre_archivo)
    
    # Formatear reporte
    reporte_formateado = formatear_reporte_sonarqube(resultado_analisis)
    logger.debug(f"Reporte generado:\n{reporte_formateado[:500]}...")
    
    # Guardar reporte
    nombre_reporte = f"3.5_sonarqube_report_req{state['attempt_count']}_sq{state['sonarqube_attempt_count']}.txt"
    guardar_fichero_texto(
        nombre_reporte,
        reporte_formateado,
        directorio=settings.OUTPUT_DIR
    )
    
    # Determinar si el código pasa el análisis
    codigo_aceptable = es_codigo_aceptable(resultado_analisis)
    
    if codigo_aceptable:
        logger.info("✅ Código aprobado por SonarQube")
        state['sonarqube_passed'] = True
        state['sonarqube_issues'] = ""
        # Resetear contador cuando pasa
        state['sonarqube_attempt_count'] = 0
        
        # === INICIO: Agregar comentario de aprobación en Azure DevOps ===
        if settings.AZURE_DEVOPS_ENABLED and state.get('azure_implementation_task_id'):
            try:
                task_id = state['azure_implementation_task_id']
                azure_service.add_sonarqube_approved_comment(task_id, nombre_reporte)
                logger.info(f"📝 Comentario de aprobación agregado a Task #{task_id}")
            except Exception as e:
                logger.warning(f"⚠️ No se pudo agregar comentario en Azure DevOps: {e}")
                logger.debug(f"Stack trace: {e}", exc_info=True)
        # === FIN: Comentario en Azure DevOps ===
        
        log_agent_execution(logger, "Analizador SonarQube", "completado", {
            "resultado": "aprobado",
            "reporte": nombre_reporte
        })
    else:
        logger.warning("❌ Código rechazado por SonarQube - requiere correcciones")
        state['sonarqube_passed'] = False
        state['sonarqube_attempt_count'] += 1
        
        # Generar instrucciones de corrección usando el LLM
        contexto_llm = (
            f"Reporte de SonarQube:\n{reporte_formateado}\n\n"
            f"Código actual:\n{state['codigo_generado']}\n\n"
            f"Requisitos formales:\n{state['requisitos_formales']}"
        )
        
        logger.info("🤖 Generando instrucciones de corrección con LLM...")
        start_time = time.time()
        instrucciones_correccion = call_gemini(Prompts.ANALIZADOR_SONARQUBE, contexto_llm)
        duration = time.time() - start_time
        
        log_llm_call(logger, "analisis_sonarqube", duration=duration)
        
        state['sonarqube_issues'] = instrucciones_correccion
        
        # Guardar instrucciones de corrección
        nombre_instrucciones = f"3.5_sonarqube_instrucciones_req{state['attempt_count']}_sq{state['sonarqube_attempt_count']}.txt"
        guardar_fichero_texto(
            nombre_instrucciones,
            instrucciones_correccion,
            directorio=settings.OUTPUT_DIR
        )
        
        logger.info(f"➡️ Instrucciones de corrección generadas - Intento {state['sonarqube_attempt_count']}/{state['max_sonarqube_attempts']}")
        
        # === INICIO: Agregar comentario de rechazo en Azure DevOps ===
        if settings.AZURE_DEVOPS_ENABLED and state.get('azure_implementation_task_id'):
            try:
                task_id = state['azure_implementation_task_id']
                azure_service.add_sonarqube_issues_comment(
                    task_id, 
                    state['sonarqube_attempt_count'], 
                    state['max_sonarqube_attempts'],
                    nombre_reporte,
                    nombre_instrucciones
                )
                logger.info(f"📝 Comentario de issues agregado a Task #{task_id}")
            except Exception as e:
                logger.warning(f"⚠️ No se pudo agregar comentario en Azure DevOps: {e}")
                logger.debug(f"Stack trace: {e}", exc_info=True)
        # === FIN: Comentario en Azure DevOps ===
        
        log_agent_execution(logger, "Analizador SonarQube", "completado", {
            "resultado": "rechazado",
            "intento": f"{state['sonarqube_attempt_count']}/{state['max_sonarqube_attempts']}",
            "reporte": nombre_reporte,
            "instrucciones": nombre_instrucciones
        })
    
    return state
