"""Agente 4: Ejecutor de Pruebas
Responsable de generar casos de prueba funcionales y ejecutarlos sobre el código generado.
Valida que el código funcione correctamente según los requisitos.
"""

import re
import json
from typing import List, Dict, Any
from models.state import AgentState
from config.prompts import Prompts
from config.settings import settings
from llm.gemini_client import call_gemini
from tools.file_utils import guardar_fichero_texto


def ejecutor_pruebas_node(state: AgentState) -> AgentState:
    """
    Nodo del Ejecutor de Pruebas.
    Genera casos de prueba funcionales y ejecuta el código para validar su corrección.
    """
    # PASO 1: Generar casos de test
    print(f"\n--- 4.1 🧪 Ejecutor de Pruebas --- Generar casos de test")

    contexto_llm1 = f"Código generado: {state['codigo_generado']}"
    respuesta_llm1 = call_gemini(Prompts.PROBADOR_GENERADOR_TESTS, contexto_llm1)
    test_cases = re.sub(r'```python|```|\n', '', respuesta_llm1).strip()
    print(f"Test cases: {test_cases}")

    # PASO 2: Ejecutar casos de test
    print(f"\n--- 4.2 🧪 Ejecutor de Pruebas --- Ejecutar casos de test")

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
    
    # Validar que la respuesta no sea None o vacía
    if not respuesta_llm2 or respuesta_llm2 == "None" or respuesta_llm2.lower() == "none":
        print(f"   ❌ ERROR: El LLM no devolvió una respuesta válida (None o vacío).")
        state['pruebas_superadas'] = False
        state['traceback'] = "ERROR: El LLM de testeo devolvió None. No se pudo ejecutar las pruebas."
        state['debug_attempt_count'] += 1
        
        # Guardar el error
        output_content = f"Status: ERROR\n\nTest Cases:\n{test_cases}\n\nError:\nEl LLM devolvió None o respuesta vacía"
        guardar_fichero_texto(
            f"4_probador_req{state['attempt_count']}_debug{state['debug_attempt_count']}_ERROR.txt",
            output_content,
            directorio=settings.OUTPUT_DIR
        )
        return state
    
    # Limpiar marcadores JSON
    respuesta_llm2 = re.sub(r'```json|```', '', respuesta_llm2).strip()

    # Intentar parsear el JSON
    try:
        respuesta_dict = json.loads(respuesta_llm2)
    except json.JSONDecodeError as e:
        print(f"   ❌ ERROR al decodificar JSON: {e}")
        print(f"   Contenido recibido: {respuesta_llm2[:200]}")
        state['pruebas_superadas'] = False
        state['traceback'] = f"ERROR JSON: {str(e)}. Contenido: {respuesta_llm2[:100]}"
        state['debug_attempt_count'] += 1
        
        # Guardar el error
        output_content = f"Status: ERROR\n\nTest Cases:\n{test_cases}\n\nError de JSON:\n{str(e)}\n\nContenido recibido:\n{respuesta_llm2}"
        guardar_fichero_texto(
            f"4_probador_req{state['attempt_count']}_debug{state['debug_attempt_count']}_ERROR.txt",
            output_content,
            directorio=settings.OUTPUT_DIR
        )
        return state

    # Validar que respuesta_dict sea un diccionario válido
    if not respuesta_dict or not isinstance(respuesta_dict, dict):
        print(f"   ❌ ERROR: La respuesta parseada no es un diccionario válido.")
        state['pruebas_superadas'] = False
        state['traceback'] = f"ERROR: Respuesta inválida del LLM: {type(respuesta_dict)}"
        state['debug_attempt_count'] += 1
        
        # Guardar el error
        output_content = f"Status: ERROR\n\nTest Cases:\n{test_cases}\n\nError:\nRespuesta no es un diccionario válido: {respuesta_dict}"
        guardar_fichero_texto(
            f"4_probador_req{state['attempt_count']}_debug{state['debug_attempt_count']}_ERROR.txt",
            output_content,
            directorio=settings.OUTPUT_DIR
        )
        return state

    # Evaluar resultado
    if respuesta_dict.get("status") == "PASSED":
        state['pruebas_superadas'] = True
        state['debug_attempt_count'] = 0  # Resetear contador de depuración al pasar
        print(f"   -> Resultado: TRUE")
        print(f"   ->        OUTPUT: {state['pruebas_superadas']}")
        
        # Guardar resultado de pruebas exitosas
        output_content = f"Status: PASSED\n\nTest Cases:\n{test_cases}\n\nResultados:\n{json.dumps(respuesta_dict, indent=2)}"
        guardar_fichero_texto(
            f"4_probador_req{state['attempt_count']}_debug{state['debug_attempt_count']}_PASSED.txt",
            output_content,
            directorio=settings.OUTPUT_DIR
        )
        
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

                # Emoji según el estado
                status_emoji = "✅" if status == "PASSED" else "❌"
                
                print(f"🧪 Caso de Prueba #{case_num} - Estado: {status_emoji} {status}")
                print(f"  ➡️ Entrada (Input): {input_val}")
                print(f"  ✅ Esperado (Expected): {expected}")
                
                # Si es un error esperado que se lanzó correctamente, mostrar de forma positiva
                if status == "PASSED" and ("Error" in str(expected) or "debe ser" in str(expected)):
                    # Verificar si el error actual es diferente pero semánticamente correcto
                    if str(expected).lower() not in str(actual).lower():
                        print(f"  ✅ Error validado semánticamente (entrada inválida detectada)")
                        print(f"     Esperado: {expected}")
                        print(f"     Obtenido: {str(actual)[:80]}...")
                    else:
                        print(f"  ✅ Error lanzado correctamente: {str(actual)[:100]}...")
                else:
                    print(f"  📤 Obtenido (Actual): {actual}")

                if status != "PASSED" and traceback_case:
                    print(f"  ⚠️ Traceback del Caso: {traceback_case[:200]}...")

                print("-" * 20)

            print("=" * 60)
    else:
        state['pruebas_superadas'] = False
        state['traceback'] = respuesta_dict.get("traceback", "")
        state['debug_attempt_count'] += 1  # Incrementar contador de intentos de depuración
        print(f"   -> Resultado: FAILED. Traceback: {state['traceback']}...")
        print(f"   -> Intento de depuración: {state['debug_attempt_count']}/{state['max_debug_attempts']}")
        print(f"   ->        OUTPUT: {state['pruebas_superadas']}")
        
        # Guardar resultado de pruebas fallidas
        output_content = f"Status: FAILED\n\nTest Cases:\n{test_cases}\n\nTraceback:\n{state['traceback']}\n\nResultados:\n{json.dumps(respuesta_dict, indent=2)}"
        guardar_fichero_texto(
            f"4_probador_req{state['attempt_count']}_debug{state['debug_attempt_count']}_FAILED.txt",
            output_content,
            directorio=settings.OUTPUT_DIR
        )

    return state
