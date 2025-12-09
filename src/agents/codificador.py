"""
Agente 3: Codificador
Responsable de generar y corregir código Python según requisitos formales.
"""

import re
from models.state import AgentState
from config.prompts import Prompts
from config.settings import settings
from llm.gemini_client import call_gemini
from tools.file_utils import guardar_fichero_texto, detectar_lenguaje_y_extension


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

    # Guardar output en archivo con extensión correcta
    lenguaje, extension, patron_limpieza = detectar_lenguaje_y_extension(
        state.get('requisitos_formales', '')
    )
    codigo_limpio = re.sub(patron_limpieza, '', state['codigo_generado']).strip()
    
    # Incluir intento de requisito y de debug
    nombre_archivo = f"3_codificador_req{state['attempt_count']}_debug{state['debug_attempt_count']}{extension}"
    guardar_fichero_texto(
        nombre_archivo,
        codigo_limpio,
        directorio=settings.OUTPUT_DIR
    )

    return state
