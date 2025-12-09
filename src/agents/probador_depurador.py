"""
Agente 4: Probador/Depurador
Responsable de generar y ejecutar casos de prueba sobre el código generado.
"""

import re
import json
from typing import List, Dict, Any
from models.state import AgentState
from config.prompts import Prompts
from llm.gemini_client import call_gemini


def probador_depurador_node(state: AgentState) -> AgentState:
    """
    Nodo del Probador/Depurador.
    Genera casos de prueba y ejecuta el código para validar su corrección.
    """
    # PASO 1: Generar casos de test
    print("--- 4.1 🧪 Probador/Depurador --- Generar casos de test")

    contexto_llm1 = f"Código generado: {state['codigo_generado']}"
    respuesta_llm1 = call_gemini(Prompts.PROBADOR_GENERADOR_TESTS, contexto_llm1)
    test_cases = re.sub(r'```python|```|\n', '', respuesta_llm1).strip()
    print(f"Test cases: {test_cases}")

    # PASO 2: Probar casos de test
    print("--- 4.2 🧪 Probador/Depurador --- Probar casos de test")

    contexto_llm2 = (
        f"Código-generado: {state['codigo_generado']}\n"
        f"Tests a usar: {test_cases}"
    )
    respuesta_llm2 = call_gemini(
        Prompts.PROBADOR_EJECUTOR_TESTS, 
        contexto_llm2, 
        allow_use_tool=True
    )

    print(f"Respuesta del LLM de testeo: {respuesta_llm2}")
    respuesta_llm2 = re.sub(r'```json|```', '', respuesta_llm2).strip()

    try:
        respuesta_dict = json.loads(respuesta_llm2)
    except json.JSONDecodeError as e:
        print(f"Error al decodificar JSON: {e}")
        state['pruebas_superadas'] = False
        return state

    if not respuesta_dict or respuesta_dict == "None":
        state['pruebas_superadas'] = False
        print(f"   -> Resultado: FAILED. No se pudo parsear la respuesta del LLM.")
        return state

    # Evaluar resultado
    if respuesta_dict.get("status") == "PASSED":
        state['pruebas_superadas'] = True
        state['debug_attempt_count'] = 0  # Resetear contador de depuración al pasar
        print(f"   -> Resultado: TRUE")
        print(f"   ->        OUTPUT: {state['pruebas_superadas']}")
        
        # Mostrar información de depuración
        if respuesta_dict.get("results"):
            results: List[Dict[str, Any]] = respuesta_dict.get("results", [])

            print("=" * 60)
            print(f"📋 Resumen General de la Ejecución: {respuesta_dict.get('status')}")
            print(f"🚨 Traceback General: {respuesta_dict.get('traceback') or 'Ninguno'}")
            print("-" * 60)

            for result_case in results:
                case_num = result_case.get("case", "N/A")
                input_val = result_case.get("input", "N/A")
                expected = result_case.get("expected", "N/A")
                actual = result_case.get("actual", "N/A")
                status = result_case.get("result", "N/A")
                traceback_case = result_case.get("traceback", "")

                print(f"🧪 Caso de Prueba #{case_num} - Estado: {status}")
                print(f"  ➡️ Entrada (Input): {input_val}")
                print(f"  ✅ Esperado (Expected): {expected}")
                print(f"  ❌ Obtenido (Actual): {actual}")

                if status != "PASSED":
                    print(f"  ⚠️ Traceback del Caso: {traceback_case or 'N/A'}")

                print("-" * 20)

            print("=" * 60)
    else:
        state['pruebas_superadas'] = False
        state['traceback'] = respuesta_dict.get("traceback", "")
        state['debug_attempt_count'] += 1  # Incrementar contador de intentos de depuración
        print(f"   -> Resultado: FAILED. Traceback: {state['traceback'][:50]}...")
        print(f"   -> Intento de depuración: {state['debug_attempt_count']}/{state['max_debug_attempts']}")
        print(f"   ->        OUTPUT: {state['pruebas_superadas']}")

    return state
