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
    print(f"\n--- 3.6 🧪 Generador de Unit Tests ---")
    
    # Obtener información del código
    lenguaje, extension, patron_limpieza = detectar_lenguaje_y_extension(
        state.get('requisitos_formales', '')
    )
    codigo_limpio = re.sub(patron_limpieza, '', state['codigo_generado']).strip()
    
    print(f"   -> Lenguaje detectado: {lenguaje}")
    print(f"   -> Generando tests unitarios...")
    
    # Determinar nombres de archivos
    attempt = state['attempt_count']
    sq_attempt = state['sonarqube_attempt_count']
    debug_attempt = state['debug_attempt_count']
    
    if lenguaje.lower() == 'typescript':
        codigo_filename = f"3_codificador_req{attempt}_debug{debug_attempt}_sq{sq_attempt}.ts"
        test_filename = f"unit_tests_req{attempt}_sq{sq_attempt}.test.ts"
    else:  # Python
        codigo_filename = f"3_codificador_req{attempt}_debug{debug_attempt}_sq{sq_attempt}.py"
        test_filename = f"test_unit_req{attempt}_sq{sq_attempt}.py"
    
    # Preparar contexto para el LLM con nombre de archivo correcto
    contexto_llm = (
        f"Requisitos formales:\n{state['requisitos_formales']}\n\n"
        f"Código generado:\n{state['codigo_generado']}\n\n"
        f"Lenguaje: {lenguaje}\n\n"
        f"IMPORTANTE: El archivo de código se llama '{codigo_filename}' (sin extensión en el import).\n"
        f"Para TypeScript: import {{ ClassName }} from './{codigo_filename.replace('.ts', '')}';\n"
        f"Para Python: from {codigo_filename.replace('.py', '')} import function_or_class\n"
    )
    
    # Llamar al LLM para generar los tests
    tests_generados = call_gemini(Prompts.GENERADOR_UNIT_TESTS, contexto_llm)
    
    # Limpiar bloques de código markdown (```typescript, ```python, etc.)
    tests_generados = re.sub(r'^```(?:typescript|python|ts|py)\s*\n?', '', tests_generados, flags=re.MULTILINE)
    tests_generados = re.sub(r'\n?```\s*$', '', tests_generados)
    tests_generados = tests_generados.strip()
    
    # Guardar tests generados
    guardar_fichero_texto(
        test_filename,
        tests_generados,
        directorio=settings.OUTPUT_DIR
    )
    
    print(f"   ✅ Tests unitarios generados: {test_filename}")
    print(f"   -> Los tests han sido guardados en: {settings.OUTPUT_DIR}/{test_filename}")
    
    # Almacenar los tests en el estado (por si se necesitan después)
    state['tests_unitarios_generados'] = tests_generados
    
    return state
