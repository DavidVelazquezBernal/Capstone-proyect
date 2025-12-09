"""
Agente 1: Ingeniero de Requisitos
Responsable de clarificar y refinar los requisitos iniciales o feedback del stakeholder.
"""

import re
from models.state import AgentState
from config.prompts import Prompts
from llm.gemini_client import call_gemini


def ingeniero_de_requisitos_node(state: AgentState) -> AgentState:
    """
    Nodo del Ingeniero de Requisitos.
    Convierte el requisito inicial o feedback en una especificación clara y verificable.
    """
    print("\n--- 1. 🙋‍♂️ Ingeniero de Requisitos ---")

    contexto_llm = (
        f"Prompt Inicial: {state['prompt_inicial']}\n"
        f"Feedback Anterior: {state['feedback_stakeholder']}"
    )

    respuesta_llm = call_gemini(Prompts.INGENIERO_REQUISITOS, contexto_llm)

    state['requisito_clarificado'] = re.sub(
        r'## REQUISITO CLARIFICADO\n', '', respuesta_llm
    ).strip()
    state['feedback_stakeholder'] = ""
    state['attempt_count'] += 1
    state['debug_attempt_count'] = 0  # Resetear contador de depuración al reiniciar requisitos

    print(f"   -> Requisito Clarificado. Intento: {state['attempt_count']}/{state['max_attempts']}")
    print(f"   ->        OUTPUT: \n{state['requisito_clarificado']}")
    
    return state
