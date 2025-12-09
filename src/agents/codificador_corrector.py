"""Agente 3: Codificador/Corrector
Responsable de generar código según requisitos formales y corregir errores.
Corrige tanto errores de ejecución (traceback) como problemas de calidad (SonarQube).
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
    Puede corregir errores de ejecución (traceback) o issues de calidad (sonarqube_issues).
    """
    print("--- 3. 💻 Codificador ---")

    # Construir contexto con todas las correcciones necesarias
    contexto_llm = f"Requisitos Formales (JSON): {state['requisitos_formales']}\n"
    
    # Añadir traceback si hay errores de ejecución
    if state['traceback']:
        contexto_llm += f"\nTraceback para corrección de errores de ejecución:\n{state['traceback']}\n"
    
    # Añadir issues de SonarQube si hay problemas de calidad
    if state.get('sonarqube_issues'):
        contexto_llm += f"\nInstrucciones de corrección de calidad (SonarQube):\n{state['sonarqube_issues']}\n"
        print(f"   -> Corrigiendo issues de calidad de código (SonarQube)")
    
    # Añadir código previo si existe para facilitar la corrección
    if state.get('codigo_generado') and (state['traceback'] or state.get('sonarqube_issues')):
        contexto_llm += f"\nCódigo anterior a corregir:\n{state['codigo_generado']}\n"

    respuesta_llm = call_gemini(Prompts.CODIFICADOR, contexto_llm)

    # El código ya viene formateado desde el LLM
    state['codigo_generado'] = respuesta_llm
    state['traceback'] = ""
    
    print(f"   -> Código generado/corregido.")
    print(f"   ->        OUTPUT: {state['codigo_generado']}")

    # Guardar output en archivo con extensión correcta
    lenguaje, extension, patron_limpieza = detectar_lenguaje_y_extension(
        state.get('requisitos_formales', '')
    )
    codigo_limpio = re.sub(patron_limpieza, '', state['codigo_generado']).strip()
    
    # Incluir intento de requisito, de debug y de sonarqube
    nombre_archivo = f"3_codificador_req{state['attempt_count']}_debug{state['debug_attempt_count']}_sq{state['sonarqube_attempt_count']}{extension}"
    guardar_fichero_texto(
        nombre_archivo,
        codigo_limpio,
        directorio=settings.OUTPUT_DIR
    )

    return state
