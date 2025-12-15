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
    # Cuando pasa los tests siempre va a RevisorCodigo (que decide si va a Stakeholder o vuelve a Desarrollador)
    workflow.add_conditional_edges(
        "Testing",
        lambda x: (
            "PASSED" if x['pruebas_superadas']
            else ("DEBUG_LIMIT_EXCEEDED" if x['debug_attempt_count'] >= x['max_debug_attempts']
                  else "FAILED")
        ),
        {
            "FAILED": "Desarrollador",
            "PASSED": "RevisorCodigo",
            "DEBUG_LIMIT_EXCEEDED": END
        }
    )
    
    # C. Transición condicional del Revisor de Código
    # Si aprueba el código va a Stakeholder, si no vuelve a Desarrollador (con límite de intentos)
    workflow.add_conditional_edges(
        "RevisorCodigo",
        lambda x: (
            "CODE_APPROVED" if x.get('codigo_revisado', False)
            else ("REVISOR_LIMIT_EXCEEDED" if x.get('revisor_attempt_count', 0) >= x.get('max_revisor_attempts', 2)
                  else "CODE_REJECTED")
        ),
        {
            "CODE_APPROVED": "Stakeholder",
            "CODE_REJECTED": "Desarrollador",
            "REVISOR_LIMIT_EXCEEDED": END
        }
    )

    # D. Bucle de Validación (Externo: Reingeniería de Requisitos / Fallo Final)
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
        # Usar más reintentos y mayor delay para evitar errores 204 de la API de Mermaid
        try:
            png_data = app.get_graph().draw_mermaid_png(max_retries=5, retry_delay=2.0)
        except Exception as e:
            logger.warning(f"⚠️ Falló el render Mermaid remoto, reintentando con PYPPETEER: {e}")
            download_host = os.environ.get("PYPPETEER_DOWNLOAD_HOST")
            if download_host and download_host.startswith("httpss://"):
                os.environ["PYPPETEER_DOWNLOAD_HOST"] = "https://" + download_host[len("httpss://"):]

            if "PYPPETEER_EXECUTABLE_PATH" not in os.environ:
                candidates = [
                    r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                    r"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
                    r"C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
                    r"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
                ]
                for candidate in candidates:
                    if os.path.exists(candidate):
                        os.environ["PYPPETEER_EXECUTABLE_PATH"] = candidate
                        break

            from langchain_core.runnables.graph import MermaidDrawMethod

            png_data = app.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.PYPPETEER)
        
        with open(output_path, "wb") as f:
            f.write(png_data)
        
        logger.info(f"✅ Grafo guardado en: {output_path}")
        logger.info(f"   Abre el archivo para visualizar el flujo de trabajo.")
    except Exception as e:
        logger.warning(f"⚠️ No se pudo guardar el grafo como imagen: {e}")
        logger.debug("   Tip: Verifica tu conexión a internet o usa MermaidDrawMethod.PYPPETEER para renderizado local")
    # except Exception as e:
    #     print(f"⚠️ No se pudo visualizar el grafo: {e}")
