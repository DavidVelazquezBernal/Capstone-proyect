"""
Agente 2: Product Owner
Responsable de formalizar requisitos en especificaciones técnicas ejecutables.
"""

import time
import json
from models.state import AgentState
from models.schemas import FormalRequirements, AzureDevOpsMetadata
from config.prompts import Prompts
from config.settings import settings
from llm.gemini_client import call_gemini
from tools.file_utils import guardar_fichero_texto
from tools.azure_devops_integration import AzureDevOpsClient, estimate_story_points
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
        
        # === INICIO: Integración con Azure DevOps ===
        azure_metadata = None
        if settings.AZURE_DEVOPS_ENABLED:
            logger.info("🔷 Integrando con Azure DevOps...")
            
            try:
                azure_client = AzureDevOpsClient()
                
                # Probar conexión
                if not azure_client.test_connection():
                    logger.warning("⚠️ No se pudo conectar con Azure DevOps, continuando sin integración")
                else:
                    # Estimar story points
                    story_points = estimate_story_points(req_data.model_dump())
                    logger.info(f"📊 Story Points estimados: {story_points}")
                    
                    # Preparar descripción y criterios de aceptación
                    description = f"""
                    <h3>Objetivo Funcional</h3>
                    <p>{req_data.objetivo_funcional}</p>
                    
                    <h3>Especificaciones Técnicas</h3>
                    <ul>
                        <li><strong>Lenguaje:</strong> {req_data.lenguaje_version}</li>
                        <li><strong>Función:</strong> <code>{req_data.nombre_funcion}</code></li>
                    </ul>
                    
                    <h3>Entradas Esperadas</h3>
                    <p>{req_data.entradas_esperadas}</p>
                    
                    <h3>Salidas Esperadas</h3>
                    <p>{req_data.salidas_esperadas}</p>
                    
                    <hr/>
                    <p><em>🤖 Generado automáticamente por el sistema multiagente</em></p>
                    """
                    
                    acceptance_criteria = f"""
                    <h4>Criterios de Aceptación</h4>
                    <ul>
                        <li>✅ El código debe implementar: {req_data.objetivo_funcional}</li>
                        <li>✅ Las entradas deben cumplir: {req_data.entradas_esperadas}</li>
                        <li>✅ Las salidas deben cumplir: {req_data.salidas_esperadas}</li>
                        <li>✅ Todos los tests unitarios deben pasar</li>
                        <li>✅ El código debe pasar el análisis de SonarQube sin issues bloqueantes</li>
                    </ul>
                    """
                    
                    # Crear PBI en Azure DevOps
                    pbi = azure_client.create_pbi(
                        title=f"[AI-Generated] {req_data.objetivo_funcional[:80]}",
                        description=description,
                        acceptance_criteria=acceptance_criteria,
                        story_points=story_points,
                        tags=["AI-Generated", "Multiagente", req_data.lenguaje_version.split()[0]],
                        priority=2  # Media por defecto
                    )
                    
                    if pbi:
                        # Crear metadatos de Azure DevOps
                        azure_metadata = AzureDevOpsMetadata(
                            work_item_id=pbi['id'],
                            work_item_url=pbi['_links']['html']['href'],
                            work_item_type="Product Backlog Item",
                            area_path=settings.AZURE_AREA_PATH or None,
                            iteration_path=settings.AZURE_ITERATION_PATH or None,
                            story_points=story_points
                        )
                        
                        logger.info(f"✅ PBI #{pbi['id']} creado en Azure DevOps")
                        logger.info(f"🔗 {pbi['_links']['html']['href']}")
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
