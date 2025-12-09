"""
Agente 2: Product Owner
Responsable de formalizar requisitos en especificaciones técnicas ejecutables.
"""

from models.state import AgentState
from models.schemas import FormalRequirements
from config.prompts import Prompts
from llm.gemini_client import call_gemini


def product_owner_node(state: AgentState) -> AgentState:
    """
    Nodo del Product Owner.
    Transforma requisitos clarificados en especificación formal JSON validada.
    """
    print("--- 2. 💼 Product Owner (Usando Pydantic Parser) ---")

    contexto_llm = f"Requisito Clarificado: {state['requisito_clarificado']}"

    respuesta_llm = call_gemini(
        Prompts.PRODUCT_OWNER, 
        contexto_llm, 
        response_schema=FormalRequirements
    )

    try:
        # Validar y almacenar la salida JSON del LLM
        req_data = FormalRequirements.model_validate_json(respuesta_llm)
        state['requisitos_formales'] = req_data.model_dump_json(indent=2)
        print(f"   -> Requisitos Formales generados (JSON validado).")
        print(f"   ->        OUTPUT: \n{state['requisitos_formales']}")
    except Exception as e:
        state['requisitos_formales'] = (
            f"ERROR_PARSING: Fallo al validar JSON. {e}. "
            f"LLM Output: {respuesta_llm[:100]}"
        )
        print(f"   ❌ ERROR: Fallo de parsing en Product Owner.")

    return state
