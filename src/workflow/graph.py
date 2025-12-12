"""
Configuración y compilación del grafo LangGraph.
Define el flujo de trabajo entre agentes y las transiciones condicionales.
"""

from langgraph.graph import StateGraph, END, START
from models.state import AgentState
from config.settings import settings
from utils.logger import setup_logger
from agents.product_owner import product_owner_node
from agents.desarrollador import desarrollador_node
from agents.sonarqube import sonarqube_node
from agents.testing import testing_node
from agents.revisor_codigo import revisor_codigo_node
from agents.stakeholder import stakeholder_node

logger = setup_logger(__name__, level=settings.get_log_level())


def create_workflow() -> StateGraph:
    """
    Crea y configura el grafo de trabajo con todos los agentes y transiciones.
    
    Returns:
        StateGraph: El grafo compilado listo para ejecución
    """
    workflow = StateGraph(AgentState)

    # 1. Añadir Nodos (Agentes)
    workflow.add_node("ProductOwner", product_owner_node)
    workflow.add_node("Desarrollador", desarrollador_node)
    workflow.add_node("SonarQube", sonarqube_node)
    workflow.add_node("Testing", testing_node)
    workflow.add_node("RevisorCodigo", revisor_codigo_node)
    workflow.add_node("Stakeholder", stakeholder_node)

    # 2. Definir Transiciones Iniciales y Lineales
    workflow.add_edge(START, "ProductOwner")
    workflow.add_edge("ProductOwner", "Desarrollador")
    workflow.add_edge("Desarrollador", "SonarQube")

    # 3. Transiciones Condicionales

    # A. Bucle de Calidad de Código (SonarQube: Corrección de Issues de Calidad)
    # Incluye control de límite de intentos
    workflow.add_conditional_edges(
        "SonarQube",
        lambda x: (
            "QUALITY_PASSED" if x['sonarqube_passed']
            else ("QUALITY_LIMIT_EXCEEDED" if x['sonarqube_attempt_count'] >= x['max_sonarqube_attempts']
                  else "QUALITY_FAILED")
        ),
        {
            "QUALITY_FAILED": "Desarrollador",
            "QUALITY_PASSED": "Testing",
            "QUALITY_LIMIT_EXCEEDED": END
        }
    )

    # B. Bucle de Depuración (Testing: Corrección de Código)
    # Incluye control de límite de intentos
    # Si pasa los tests y GitHub está habilitado, va a RevisorCodigo; si no, va a Stakeholder
    workflow.add_conditional_edges(
        "Testing",
        lambda x: (
            ("PASSED_WITH_GITHUB" if settings.GITHUB_ENABLED else "PASSED") if x['pruebas_superadas']
            else ("DEBUG_LIMIT_EXCEEDED" if x['debug_attempt_count'] >= x['max_debug_attempts']
                  else "FAILED")
        ),
        {
            "FAILED": "Desarrollador",
            "PASSED": "Stakeholder",
            "PASSED_WITH_GITHUB": "RevisorCodigo",
            "DEBUG_LIMIT_EXCEEDED": END
        }
    )
    
    # C. Transición del Revisor de Código al Stakeholder
    workflow.add_edge("RevisorCodigo", "Stakeholder")

    # C. Bucle de Validación (Externo: Reingeniería de Requisitos / Fallo Final)
    workflow.add_conditional_edges(
        "Stakeholder",
        lambda x: (
            "VALIDADO" if x['validado'] 
            else ("FAILED_FINAL" if x['attempt_count'] >= x['max_attempts'] 
                  else "RECHAZADO")
        ),
        {
            "RECHAZADO": "ProductOwner",
            "VALIDADO": END,
            "FAILED_FINAL": END,
        }
    )

    # 4. Compilar el Grafo
    return workflow.compile()


def visualize_graph(app):
    """
    Visualiza el grafo en formato Mermaid y lo guarda como imagen PNG.
    
    Args:
        app: El grafo compilado
    """
    # try:
    #     # Intentar usar IPython.display (para notebooks)
    #     from IPython.display import Image, display
    #     display(Image(app.get_graph().draw_mermaid_png()))
    #     print("✅ Grafo visualizado en notebook.")
    # except ImportError:
        # Si no está en notebook, guardar como archivo PNG
    try:
        import os
        from config.settings import settings
        
        output_path = os.path.join(settings.OUTPUT_DIR, "workflow_graph.png")
        png_data = app.get_graph().draw_mermaid_png()
        
        with open(output_path, "wb") as f:
            f.write(png_data)
        
        logger.info(f"✅ Grafo guardado en: {output_path}")
        logger.info(f"   Abre el archivo para visualizar el flujo de trabajo.")
    except Exception as e:
        logger.warning(f"⚠️ No se pudo guardar el grafo como imagen: {e}")
    # except Exception as e:
    #     print(f"⚠️ No se pudo visualizar el grafo: {e}")
