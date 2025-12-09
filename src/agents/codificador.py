"""
Agente 3: Codificador
Responsable de generar y corregir código Python según requisitos formales.
"""

from models.state import AgentState
from config.prompts import Prompts
from llm.gemini_client import call_gemini


def codificador_node(state: AgentState) -> AgentState:
    """
    Nodo del Codificador.
    Genera código que satisface los requisitos formales o corrige errores.
    """
    print("--- 3. 💻 Codificador ---")

    contexto_llm = (
        f"Requisitos Formales (JSON): {state['requisitos_formales']}\n"
        f"Traceback para corrección: {state['traceback']}"
    )

    respuesta_llm = call_gemini(Prompts.CODIFICADOR, contexto_llm)

    # El código ya viene formateado desde el LLM
    state['codigo_generado'] = respuesta_llm
    state['traceback'] = ""
    
    print(f"   -> Código generado para pruebas.")
    print(f"   ->        OUTPUT: {state['codigo_generado']}")

    return state
