"""
Agente: Analizador SonarQube
Responsable de verificar la calidad del código generado usando SonarQube antes de las pruebas funcionales.
"""

import re
import time
from models.state import AgentState
from config.prompts import Prompts
from config.prompt_templates import PromptTemplates
from config.settings import settings
from llm.gemini_client import call_gemini
from tools.file_utils import detectar_lenguaje_y_extension, limpiar_codigo_markdown, guardar_fichero_texto
from tools.sonarqube_mcp import analizar_codigo_con_sonarqube, formatear_reporte_sonarqube, es_codigo_aceptable
from services.azure_devops_service import azure_service
from utils.logger import setup_logger, log_agent_execution, log_llm_call, log_file_operation
from utils.agent_decorators import agent_execution_context

logger = setup_logger(__name__, level=settings.get_log_level(), agent_mode=True)



def sonarqube_node(state: AgentState) -> AgentState:
    """
    Nodo de SonarQube.
    Analiza la calidad del código generado y determina si cumple los estándares.
    """
    with agent_execution_context("🔍 SONARQUBE", logger):
        # Verificar si hay algún método de análisis habilitado
        if not settings.SONARCLOUD_ENABLED and not settings.SONARSCANNER_ENABLED:
            logger.warning("⚠️ SONARCLOUD_ENABLED=false y SONARSCANNER_ENABLED=false: omitiendo análisis de calidad y continuando el flujo")
            state['sonarqube_passed'] = True
            state['sonarqube_issues'] = ""
            state['sonarqube_attempt_count'] = 0

            log_agent_execution(logger, "SonarQube", "omitido", {
                "motivo": "Análisis de calidad deshabilitado (SONARCLOUD_ENABLED=false, SONARSCANNER_ENABLED=false)",
                "resultado": "aprobado"
            })
            return state

        log_agent_execution(logger, "SonarQube", "iniciado", {
            "requisito_id": state['attempt_count'],
            "validacion_numero": state['sonarqube_attempt_count'] + 1,
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
        
        # Construir nombre del archivo que YA FUE GUARDADO por developer_code
        # IMPORTANTE: Debe coincidir con el patrón usado en developer_code.py
        # Patrón: 2_developer_req{N}_debug{M}_sq{K}.{ext}
        nombre_archivo = f"2_developer_req{state['attempt_count']}_debug{state['debug_attempt_count']}_sq{state['sonarqube_attempt_count']}{extension}"
        
        # Verificar que el archivo existe
        import os
        ruta_archivo = os.path.join(settings.OUTPUT_DIR, nombre_archivo)
        if not os.path.exists(ruta_archivo):
            logger.error(f"❌ El archivo {nombre_archivo} no existe en {settings.OUTPUT_DIR}")
            logger.error("   El agente developer-code debería haberlo guardado antes")
            raise FileNotFoundError(f"Archivo no encontrado: {ruta_archivo}")
        
        logger.info(f"🔍 Analizando código con SonarQube - Validación #{state['sonarqube_attempt_count'] + 1}")
        logger.info(f"📄 Archivo a analizar: {nombre_archivo}")
        logger.info(f"📁 Ruta completa: {ruta_archivo}")
        
        # Leer el contenido del archivo para análisis
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            codigo_limpio = f.read()
        
        # Obtener branch del estado (creado por el Desarrollador)
        branch_name = state.get('github_branch_name')
        
        if branch_name and settings.SONARCLOUD_ENABLED:
            from services.sonarcloud_service import sonarcloud_service
            
            logger.info("=" * 60)
            logger.info("☁️  ANÁLISIS SONARCLOUD")
            logger.info("=" * 60)
            logger.info(f"Branch: {branch_name}")
            logger.info(f"Proyecto: {settings.SONARCLOUD_PROJECT_KEY}")
            logger.info(f"Organización: {settings.SONARCLOUD_ORGANIZATION}")
            logger.info(f"Timeout configurado: {settings.SONARCLOUD_ANALYSIS_TIMEOUT}s")
            logger.info("=" * 60)
            
            # Verificar integración GitHub-SonarCloud (solo en primer análisis)
            if state['sonarqube_attempt_count'] == 0:
                logger.info("🔍 Verificando integración GitHub-SonarCloud...")
                integration_check = sonarcloud_service.verify_github_integration()
                
                if not integration_check.get("success"):
                    logger.warning(f"⚠️ Problema con integración SonarCloud-GitHub:")
                    logger.warning(f"   {integration_check.get('error')}")
                    if integration_check.get('hint'):
                        logger.info(f"   💡 {integration_check.get('hint')}")
                    logger.info("🔄 Usando análisis local como fallback...")
                    branch_name = None
                else:
                    logger.info(f"✅ Integración verificada - {integration_check.get('branches_count', 0)} branches disponibles")
            
            # Si aún tenemos branch después de verificación, esperar análisis
            if branch_name:
                logger.info("⏳ Esperando a que SonarCloud complete el análisis del branch...")
                logger.info(f"   Timeout total: {settings.SONARCLOUD_ANALYSIS_TIMEOUT}s con polling adaptativo")
                
                result = sonarcloud_service.wait_for_analysis(
                    branch_name=branch_name,
                    timeout=settings.SONARCLOUD_ANALYSIS_TIMEOUT
                )
                
                if result.get("success"):
                    logger.info("✅ Análisis SonarCloud disponible")
                    logger.info(f"   Issues encontrados: {result.get('issues', {}).get('total', 0)}")
                    logger.info(f"   Quality Gate: {result.get('quality_gate', {}).get('status', 'N/A')}")
                    resultado_analisis = result
                else:
                    logger.warning(f"⚠️ Timeout esperando análisis de SonarCloud: {result.get('error')}")
                    logger.info("🔄 Fallback a análisis local...")
                    resultado_analisis = analizar_codigo_con_sonarqube(codigo_limpio, nombre_archivo, None)
            else:
                # Sin branch o integración fallida
                resultado_analisis = analizar_codigo_con_sonarqube(codigo_limpio, nombre_archivo, None)
                
        elif settings.SONARCLOUD_ENABLED:
            logger.warning("⚠️ No hay branch de GitHub disponible para SonarCloud")
            logger.info("🔄 Usando análisis local...")
            resultado_analisis = analizar_codigo_con_sonarqube(codigo_limpio, nombre_archivo, None)
        else:
            # SonarCloud deshabilitado, usar análisis local (SonarScanner CLI o estático)
            if settings.SONARSCANNER_ENABLED:
                logger.info("=" * 60)
                logger.info("🔧 ANÁLISIS CON SONARSCANNER CLI")
                logger.info("=" * 60)
                logger.info("SonarCloud deshabilitado, usando SonarScanner CLI local")
                logger.info(f"Archivo a analizar: {nombre_archivo}")
                logger.info("=" * 60)
            else:
                logger.info("🔍 Usando análisis estático local (SonarScanner CLI deshabilitado)")
            
            resultado_analisis = analizar_codigo_con_sonarqube(codigo_limpio, nombre_archivo, None)
        
        # Formatear reporte
        reporte_formateado = formatear_reporte_sonarqube(resultado_analisis)
        logger.debug(f"Reporte generado:\n{reporte_formateado[:500]}...")
        
        # Guardar reporte SIEMPRE (tanto si pasa como si falla)
        nombre_reporte = f"3_sonarqube_report_req{state['attempt_count']}_sq{state['sonarqube_attempt_count']}.txt"
        guardar_fichero_texto(
            nombre_reporte,
            reporte_formateado,
            directorio=settings.OUTPUT_DIR
        )
        
        # Determinar si el código pasa el análisis
        codigo_aceptable = es_codigo_aceptable(resultado_analisis)
        
        # Obtener contadores para logging detallado
        summary = resultado_analisis.get("summary", {})
        by_severity = summary.get("by_severity", {})
        by_type = summary.get("by_type", {})
        
        blocker_count = by_severity.get("BLOCKER", 0)
        critical_count = by_severity.get("CRITICAL", 0)
        bug_count = by_type.get("BUG", 0)
        
        if codigo_aceptable:
            logger.info("✅ Código aprobado por SonarQube")
            logger.info(f"   📊 Issues encontrados: {blocker_count} BLOCKER, {critical_count} CRITICAL, {bug_count} BUGS")
            state['sonarqube_passed'] = True
            state['sonarqube_issues'] = ""
            # Resetear contador cuando pasa
            state['sonarqube_attempt_count'] = 0
            
            # === INICIO: Agregar comentario de aprobación en Azure DevOps ===
            if settings.AZURE_DEVOPS_ENABLED and state.get('azure_implementation_task_id'):
                try:
                    task_id = state['azure_implementation_task_id']
                    azure_service.add_sonarqube_approval_comment(task_id, nombre_reporte, state)
                    logger.info(f"📝 Comentario de aprobación agregado a Task #{task_id}")
                except Exception as e:
                    logger.warning(f"⚠️ No se pudo agregar comentario en Azure DevOps: {e}")
                    logger.debug(f"Stack trace: {e}", exc_info=True)
            # === FIN: Comentario en Azure DevOps ===
            
            log_agent_execution(logger, "SonarQube", "completado", {
                "resultado": "aprobado",
                "reporte": nombre_reporte
            })
            
        else:
            # Código no pasa los criterios de calidad
            logger.warning("❌ Código rechazado por SonarQube - requiere correcciones")
            logger.warning(f"   📊 Razones de rechazo:")
            
            if blocker_count > 0:
                logger.warning(f"      🔴 {blocker_count} BLOCKER (máximo permitido: 0)")
            if critical_count > 2:
                logger.warning(f"      🟠 {critical_count} CRITICAL (máximo permitido: 2)")
            if bug_count > 0:
                logger.warning(f"      🐛 {bug_count} BUGS (máximo permitido: 0)")
            
            state['sonarqube_passed'] = False
            
            # Generar instrucciones de corrección usando el LLM
            # Usar ChatPromptTemplate
            logger.debug("🔗 Usando ChatPromptTemplate de LangChain")
            prompt_formateado = PromptTemplates.format_sonarqube(
                reporte_sonarqube=reporte_formateado,
                codigo_actual=state['codigo_generado']
            )
            
            logger.info("🤖 Generando instrucciones de corrección con LLM...")
            start_time = time.time()
            instrucciones_correccion = call_gemini(prompt_formateado, "")
            duration = time.time() - start_time
            
            log_llm_call(logger, "analisis_sonarqube", duration=duration)
            
            state['sonarqube_issues'] = instrucciones_correccion
            
            # Incrementar contador después de generar instrucciones
            state['sonarqube_attempt_count'] += 1
            
            # Guardar instrucciones de corrección (usar el contador ANTES de incrementar)
            intento_actual = state['sonarqube_attempt_count'] - 1  # Ya fue incrementado en línea 243
            nombre_instrucciones = f"3_sonarqube_instrucciones_req{state['attempt_count']}_sq{intento_actual}.txt"
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
            
            log_agent_execution(logger, "SonarQube", "completado", {
                "resultado": "rechazado",
                "intento": f"{state['sonarqube_attempt_count']}/{state['max_sonarqube_attempts']}",
                "reporte": nombre_reporte,
                "instrucciones": nombre_instrucciones
            })
        
        return state
