"""
Agente: Generador de UTs (Generador de Unit Tests)
Responsable de generar tests unitarios (vitest para TypeScript, pytest para Python).
"""

import re
import time
from models.state import AgentState
from config.prompts import Prompts
from config.settings import settings
from llm.gemini_client import call_gemini
from tools.file_utils import guardar_fichero_texto, detectar_lenguaje_y_extension
from utils.logger import setup_logger, log_agent_execution, log_llm_call, log_file_operation

logger = setup_logger(__name__, level=settings.get_log_level(), agent_mode=True)


def generador_uts_node(state: AgentState) -> AgentState:
    """
    Nodo del Generador de UTs (Unit Tests).
    Genera tests unitarios para el código generado según el lenguaje.
    """
    print()  # Línea en blanco para separación visual
    logger.info("=" * 60)
    logger.info("GENERADOR UTs - INICIO")
    logger.info("=" * 60)

    log_agent_execution(logger, "Generador UTs", "iniciado", {
        "requisito_id": state['attempt_count']
    })
    
    # Obtener información del código
    lenguaje, extension, patron_limpieza = detectar_lenguaje_y_extension(
        state.get('requisitos_formales', '')
    )
    codigo_limpio = re.sub(patron_limpieza, '', state['codigo_generado']).strip()
    
    logger.info(f"🔍 Lenguaje detectado: {lenguaje}")
    logger.info("🧪 Generando tests unitarios...")
    
    # Determinar nombres de archivos
    attempt = state['attempt_count']
    sq_attempt = state['sonarqube_attempt_count']
    debug_attempt = state['debug_attempt_count']
    
    if lenguaje.lower() == 'typescript':
        codigo_filename = f"3_desarrollador_req{attempt}_debug{debug_attempt}_sq{sq_attempt}.ts"
        test_filename = f"unit_tests_req{attempt}_sq{sq_attempt}.test.ts"
    else:  # Python
        codigo_filename = f"3_desarrollador_req{attempt}_debug{debug_attempt}_sq{sq_attempt}.py"
        test_filename = f"test_unit_req{attempt}_sq{sq_attempt}.py"
    
    logger.debug(f"Archivo de código: {codigo_filename}")
    logger.debug(f"Archivo de tests: {test_filename}")
    
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
    logger.info("🤖 Llamando a LLM para generar tests...")
    start_time = time.time()
    tests_generados = call_gemini(Prompts.GENERADOR_UTS, contexto_llm)
    duration = time.time() - start_time
    
    log_llm_call(logger, "generacion_tests", duration=duration)
    
    # Limpiar bloques de código markdown (```typescript, ```python, etc.)
    tests_generados = re.sub(r'^```(?:typescript|python|ts|py)\s*\n?', '', tests_generados, flags=re.MULTILINE)
    tests_generados = re.sub(r'\n?```\s*$', '', tests_generados)
    
    # Limpiar etiquetas de lenguaje sueltas al inicio (typescript, python, ts, py)
    tests_generados = re.sub(r'^(?:typescript|python|ts|py)\s*\n', '', tests_generados, flags=re.MULTILINE)
    tests_generados = tests_generados.strip()
    
    # Guardar tests generados
    resultado = guardar_fichero_texto(
        test_filename,
        tests_generados,
        directorio=settings.OUTPUT_DIR
    )
    
    logger.info(f"Tests unitarios generados: {test_filename}")
    
    log_agent_execution(logger, "Generador UTs", "completado", {
        "archivo_tests": test_filename,
        "archivo_codigo": codigo_filename,
        "lenguaje": lenguaje,
        "guardado": resultado
    })
    
    # Almacenar los tests en el estado (por si se necesitan después)
    state['tests_unitarios_generados'] = tests_generados
    
    return state
