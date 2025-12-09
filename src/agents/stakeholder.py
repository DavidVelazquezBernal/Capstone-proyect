"""
Agente 5: Stakeholder
Responsable de validar que el código cumple la visión de negocio.
"""

import re
from models.state import AgentState
from config.prompts import Prompts
from config.settings import settings
from llm.gemini_client import call_gemini
from tools.file_utils import guardar_fichero_texto


def stakeholder_node(state: AgentState) -> AgentState:
    """
    Nodo del Stakeholder.
    Valida si el código cumple con la intención de negocio.
    """
    print("--- 5. ✅ Stakeholder ---")

    # Comprobar si se excedió el límite de intentos
    if state['attempt_count'] >= state['max_attempts']:
        state['validado'] = False
        print(f"   ❌ LÍMITE DE INTENTOS EXCEDIDO ({state['max_attempts']}). PROYECTO FALLIDO.")
        return state

    contexto_llm = (
        f"Código aprobado técnicamente: {state['codigo_generado']}\n"
        f"Requisitos Formales (JSON): {state['requisitos_formales']}"
    )
    
    respuesta_llm = call_gemini(Prompts.STAKEHOLDER, contexto_llm)

    # Lógica de transición de validación
    if "VALIDADO" in respuesta_llm:
        state['validado'] = True
        print("   -> Resultado: VALIDADO. Proyecto Terminado.")
        
        # Guardar validación exitosa
        guardar_fichero_texto(
            f"5_stakeholder_intento_{state['attempt_count']}_VALIDADO.txt",
            f"Validación: APROBADO\n\nRespuesta:\n{respuesta_llm}",
            directorio=settings.OUTPUT_DIR
        )
    else:
        state['validado'] = False
        # Extraer el feedback de rechazo
        feedback_match = re.search(r'Motivo: (.*)', respuesta_llm, re.DOTALL)
        if feedback_match:
            state['feedback_stakeholder'] = feedback_match.group(1).strip()
        print(f"   -> Resultado: RECHAZADO.")
        print(f"   -> Motivo: {state['feedback_stakeholder']}")
        print("   -> Volviendo a Ingeniero de Requisitos.")
        
        # Guardar validación rechazada
        guardar_fichero_texto(
            f"5_stakeholder_intento_{state['attempt_count']}_RECHAZADO.txt",
            f"Validación: RECHAZADO\n\nMotivo:\n{state['feedback_stakeholder']}\n\nRespuesta completa:\n{respuesta_llm}",
            directorio=settings.OUTPUT_DIR
        )

    return state
