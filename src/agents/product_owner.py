"""
Agente: Product Owner
Responsable de clarificar, formalizar requisitos y crear PBIs en Azure DevOps.
"""

import time
import json
from models.state import AgentState
from models.schemas import FormalRequirements, AzureDevOpsMetadata
from config.prompts import Prompts
from config.prompt_templates import PromptTemplates
from config.settings import settings
from llm.gemini_client import call_gemini
from llm.output_parsers import get_formal_requirements_parser, validate_and_parse
from tools.file_utils import guardar_fichero_texto
from services.azure_devops_service import azure_service
from utils.logger import setup_logger, log_agent_execution, log_llm_call, log_file_operation
from utils.agent_decorators import agent_execution_context

# Configurar logger para este agente
logger = setup_logger(__name__, level=settings.get_log_level(), agent_mode=True)


def product_owner_node(state: AgentState) -> AgentState:
    """
    Nodo del Product Owner.
    Procesa el input del usuario y/o feedback del stakeholder, genera especificación
    formal JSON validada, y crea PBI en Azure DevOps.
    """

    with agent_execution_context("📋 PRODUCT OWNER", logger):
        # Log del contexto de entrada
        log_agent_execution(
            logger,
            "Requirements Manager",
            "Procesando requisitos",
            {
                "intento": f"{state['attempt_count'] + 1}/{state['max_attempts']}",
                "tiene_feedback": bool(state['feedback_stakeholder'])
            }
        )

        # Construir prompt usando ChatPromptTemplate
        logger.debug("🔗 Usando ChatPromptTemplate de LangChain")
        prompt_formateado = PromptTemplates.format_product_owner(
            prompt_inicial=state['prompt_inicial'],
            feedback_stakeholder=state['feedback_stakeholder'] if state['feedback_stakeholder'] else ""
        )
        
        logger.debug(f"Prompt formateado (primeros 200 chars): {prompt_formateado[:200]}...")

        # Llamar al LLM con medición de tiempo y schema JSON
        start_time = time.time()
        respuesta_llm = call_gemini(
            prompt_formateado,
            "",  # Contexto vacío porque ya está en el prompt
            response_schema=FormalRequirements
        )
        duration = time.time() - start_time
        
        log_llm_call(logger, "PRODUCT_OWNER", duration=duration)

        try:
            # Validar y almacenar la salida JSON del LLM usando PydanticOutputParser
            logger.debug("🔍 Parseando respuesta con PydanticOutputParser...")
            parser = get_formal_requirements_parser()
            req_data = parser.parse(respuesta_llm)
            
            logger.info("✅ Requisitos formalizados y validados correctamente (con LangChain parser)")
            logger.debug(f"JSON generado: {req_data.model_dump_json(indent=2)[:200]}...")
            
            # === INICIO: Integración con Azure DevOps (usando servicio centralizado) ===
            azure_metadata = None
            if settings.AZURE_DEVOPS_ENABLED:
                logger.info("🔷 Integrando con Azure DevOps...")
                
                try:
                    # Usar servicio centralizado para crear PBI
                    azure_metadata = azure_service.create_pbi_from_requirements(req_data.model_dump())
                    
                    if azure_metadata:
                        # Guardar el PBI ID en el estado para futuros work items
                        state['azure_pbi_id'] = azure_metadata.work_item_id
                        logger.info(f"💾 PBI ID #{azure_metadata.work_item_id} guardado para asociar work items posteriores")
                    else:
                        logger.warning("⚠️ No se pudo crear el PBI en Azure DevOps")
                            
                except Exception as e:
                    logger.warning(f"⚠️ Error en integración Azure DevOps: {e}")
                    logger.debug(f"Stack trace: {e}", exc_info=True)
            # === FIN: Integración con Azure DevOps ===
            
            # Construir requisitos formales con metadatos de Azure (si existen)
            if azure_metadata:
                # Agregar metadatos de Azure al JSON
                req_dict = req_data.model_dump()
                req_dict['azure_devops'] = azure_metadata.model_dump()
                state['requisitos_formales'] = json.dumps(req_dict, indent=2)
            else:
                state['requisitos_formales'] = req_data.model_dump_json(indent=2)
            
            # Actualizar estado
            state['requisito_clarificado'] = req_data.objetivo_funcional  # Mantener retrocompatibilidad
            state['feedback_stakeholder'] = ""  # Limpiar feedback procesado
            state['attempt_count'] += 1
            state['debug_attempt_count'] = 0
            state['sonarqube_attempt_count'] = 0
            
            logger.info(f"✅ Requisitos procesados exitosamente")
            logger.info(f"Intento: {state['attempt_count']}/{state['max_attempts']}")
            
            # Guardar output en archivo
            nombre_archivo = f"1_product_owner_intento_{state['attempt_count']}.json"
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
            logger.error(f"❌ Error al validar o procesar requisitos: {e}")
            logger.error(f"   Tipo de error: {type(e).__name__}")
            logger.debug(f"   Respuesta LLM completa: {respuesta_llm}")
            
            # Intento de fallback: parsing manual sin LangChain
            logger.warning("⚠️ Intentando fallback con parsing manual...")
            try:
                req_data = FormalRequirements.model_validate_json(respuesta_llm)
                logger.info("✅ Fallback exitoso con parsing manual")
                state['requisitos_formales'] = req_data.model_dump_json(indent=2)
                state['requisito_clarificado'] = req_data.objetivo_funcional
                state['feedback_stakeholder'] = ""
                state['attempt_count'] += 1
                state['debug_attempt_count'] = 0
                state['sonarqube_attempt_count'] = 0
            except Exception as e2:
                logger.error(f"❌ Fallback también falló: {e2}")
                state['requisitos_formales'] = (
                    f"ERROR_PARSING: Fallo al validar JSON. {e}. "
                    f"LLM Output: {respuesta_llm[:100]}"
                )
                logger.error("Fallo de parsing en Requirements Manager")

    
        return state
