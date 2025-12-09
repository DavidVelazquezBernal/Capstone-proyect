"""
Agente: Generador de Unit Tests
Responsable de generar tests unitarios (vitest para TypeScript, pytest para Python).
"""

import re
from models.state import AgentState
from config.prompts import Prompts
from config.settings import settings
from llm.gemini_client import call_gemini
from tools.file_utils import guardar_fichero_texto, detectar_lenguaje_y_extension


def generador_unit_tests_node(state: AgentState) -> AgentState:
    """
    Nodo del Generador de Unit Tests.
    Genera tests unitarios para el código generado según el lenguaje.
    """
    print("--- 3.6 🧪 Generador de Unit Tests ---")
    
    # Obtener información del código
    lenguaje, extension, patron_limpieza = detectar_lenguaje_y_extension(
        state.get('requisitos_formales', '')
    )
    codigo_limpio = re.sub(patron_limpieza, '', state['codigo_generado']).strip()
    
    print(f"   -> Lenguaje detectado: {lenguaje}")
    print(f"   -> Generando tests unitarios...")
    
    # Preparar contexto para el LLM
    contexto_llm = (
        f"Requisitos formales:\n{state['requisitos_formales']}\n\n"
        f"Código generado:\n{state['codigo_generado']}\n\n"
        f"Lenguaje: {lenguaje}\n"
    )
    
    # Llamar al LLM para generar los tests
    tests_generados = call_gemini(Prompts.GENERADOR_UNIT_TESTS, contexto_llm)
    
    # Limpiar bloques de código markdown (```typescript, ```python, etc.)
    tests_generados = re.sub(r'^```(?:typescript|python|ts|py)\s*\n?', '', tests_generados, flags=re.MULTILINE)
    tests_generados = re.sub(r'\n?```\s*$', '', tests_generados)
    tests_generados = tests_generados.strip()
    
    # Determinar extensión del archivo de tests
    if lenguaje.lower() == 'typescript':
        extension_test = '.test.ts'
        nombre_test = f"unit_tests_req{state['attempt_count']}_sq{state['sonarqube_attempt_count']}{extension_test}"
    else:  # Python
        extension_test = '.test.py'
        nombre_test = f"test_unit_req{state['attempt_count']}_sq{state['sonarqube_attempt_count']}{extension_test}"
    
    # Guardar tests generados
    guardar_fichero_texto(
        nombre_test,
        tests_generados,
        directorio=settings.OUTPUT_DIR
    )
    
    print(f"   ✅ Tests unitarios generados: {nombre_test}")
    print(f"   -> Los tests han sido guardados en: {settings.OUTPUT_DIR}/{nombre_test}")
    
    # Almacenar los tests en el estado (por si se necesitan después)
    state['tests_unitarios_generados'] = tests_generados
    
    return state
