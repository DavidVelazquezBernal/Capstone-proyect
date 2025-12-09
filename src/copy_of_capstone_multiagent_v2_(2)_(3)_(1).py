

#Instalación librerías necesarias


# 'google-genai' para el LLM, 'langgraph' para la arquitectura.
#pip install -q google-genai langgraph pydantic
#pip install e2b-code-interpreter python-dotenv
#pip install ipython
#pip install -Uqq ipdb

"""Configuración entorno"""

#import ipdb
import re
import os
from dotenv import load_dotenv
load_dotenv()
from typing import TypedDict, List, Annotated
from langgraph.graph import StateGraph, END, START
from IPython.display import Image, display
from pydantic import BaseModel, Field
from google import genai
from google.genai.errors import APIError
import operator
import json
from typing import List, Dict, Any
from e2b_code_interpreter import Sandbox

# --- Configuración de la clave API ---
os.environ["GEMINI_API_KEY"] = 'AIzaSyCJt0Ln8e8ksWc15Rx7SFmuyiSp23r4pBY'   # Llevar a un SECRETO SEGURO


# Inicialización del cliente Gemini
try:
    client = genai.Client()
    print("✅ Cliente Gemini inicializado correctamente.")
except Exception as e:
    print(f"❌ ERROR: Fallo al inicializar el cliente Gemini. Asegúrate de que la clave API sea válida. {e}")
    # Nota: El código fallará en tiempo de ejecución si la clave es inválida.

"""# DEFINICIÓN DEL ESTADO DEL GRAFO (AgentState)"""

class AgentState(TypedDict):
    """
    Representa el estado compartido entre todos los agentes en el grafo.
    """
    prompt_inicial: str

    # Contexto y gestión de bucles
    max_attempts: int # Máximo de reintentos antes de fallo final
    attempt_count: int # Contador de intentos en el ciclo de depuración
    feedback_stakeholder: str

    # Datos del proyecto
    requisito_clarificado: str
    requisitos_formales: str # Ahora JSON de Pydantic
    codigo_generado: str

    # QA
    traceback: str
    pruebas_superadas: bool

    # Validación
    validado: bool

"""# PYDANTIC SCHEMAS"""

# 1 Schema para la Salida del Product Owner
class FormalRequirements(BaseModel):
    """Esquema formal de requisitos generado por el Product Owner."""
    objetivo_funcional: str = Field(description="Descripción concisa de la función del código.")
    lenguaje_version: str = Field(description="Lenguaje y versión, ej. 'Python 3.10+'.")
    nombre_funcion: str = Field(description="Firma de la función principal, ej. 'def calculate(data)'.")
    entradas_esperadas: str = Field(description="Tipos de datos y formato de entrada esperados.")
    salidas_esperadas: str = Field(description="Formato exacto de salida (ej. entero, JSON, cadena con formato).")

"""# TOOLS"""

import re

def extract_function_name(code: str) -> str:
    """
    Extrae el nombre de la primera función definida en un bloque de código Python.

    Args:
        code (str): El código Python.

    Returns:
        str: El nombre de la función si se encuentra, de lo contrario None.
    """
    function_name_match = re.search(r'def\s+(\w+)\(', code)
    if function_name_match:
        return function_name_match.group(1)
    return None

# @title
def CodeExecutionToolFake2(code: str, test_data: List[dict]) -> dict:
    """
    Simula la ejecución segura de código Python contra datos de prueba.

    Args:
        code (str): El código Python generado que se va a ejecutar.
        test_data (List[dict]): Una lista de diccionarios, donde cada diccionario representa un caso de prueba.
                                Contiene 'input' (argumentos para el código) y 'expected' (salida esperada).

    Returns:
        dict: Un diccionario que contiene:
              - 'status' (bool): True si todas las pruebas pasan, False en caso contrario.
              - 'results' (List[dict]): Una lista de resultados por cada caso de prueba, incluyendo 'success',
                                        'output', 'message', 'expected', y 'traceback' si hay un fallo.
              - 'traceback' (str): Un mensaje de traceback general si alguna prueba falla, o una cadena vacía.
    """
    print(f"\n---     🧪 TOOL: Ejecutando {len(test_data)} casos de prueba... ---")

    print(f"\n ---{code}\n\n --- {test_data} ")
    results = []
    all_tests_passed = True
    simulated_traceback = "Error tracebak simulado"

    for idx, case in enumerate(test_data, start=1):
            # Simulate success
            results.append({
                "case": idx,
                "success": True,
                "output": f"La suma es: {case.get('expected')}", # Simulating correct output
                "message": "Pruebas técnicas superadas y formato de salida correcto.",
                "expected": case.get("expected")
            })
    print(f"\n--- Results: {results}")
    return {
        "status": "PASSED",
        "results": results,
        "traceback": simulated_traceback if not all_tests_passed else ""
    }

# @title
# 3 Herramienta de Ejecución de Código (Real)
import time # Importar el módulo time para usar time.sleep()
def CodeExecutionToolWithInterpreter(code: str, test_data: List[dict]) -> dict:
    """
    Ejecución segura de código Python contra datos de prueba.

    Args:
        code (str): El código Python generado que se va a ejecutar.
        test_data (List[dict]): Una lista de diccionarios, donde cada diccionario representa un caso de prueba.
                                Contiene 'input' (argumentos para el código) y 'expected' (salida esperada).

    Returns:
        dict: Un diccionario que contiene:
              - 'success' (bool): True si todas las pruebas pasan, False en caso contrario.
              - 'results' (List[dict]): Una lista de resultados por cada caso de prueba, incluyendo 'success',
                                        'output', 'message', 'expected', y 'traceback' si hay un fallo.
              - 'traceback' (str): Un mensaje de traceback general si alguna prueba falla, o una cadena vacía.
    """
    print(f"\n---     🧪 TOOL: Ejecutando {len(test_data)} casos de prueba... ---")

    results = []
    all_success = True
    traceback = ""

    #try:
    os.environ['E2B_API_KEY'] = 'e2b_2b69990d0ae778b5c3485cd6244817c8d9062845'  # Asegurarse de definir la clave API para e2b

    # Crear el sandbox una única vez fuera del bucle de pruebas
    # 1. Iniciar el Sandbox (el entorno persiste mientras dure este contexto 'with')
    sbx = Sandbox.create()
    time.sleep(2) # Pausa inicial para la creación del sandbox
    exec_result = sbx.run_code(code)

    function_name = extract_function_name(code)
    if not function_name:
        sbx.close()
        return {
            "success": False,
            "traceback": "Error: Could not find function name in the provided code.",
            "results": []
        }


    for idx, case in enumerate(test_data, start=1):
        inputs = case.get("input", [])
        expected = case.get("expected")

        try:
            # Construct the function call string dynamically
            # This handles various types of inputs correctly for a function call
            #args_str = ", ".join(json.dumps(arg) for arg in inputs) # Use json.dumps for complex types
            function_call_str = f"print({function_name}({inputs}))"

            print(f"Sandbox inputs: {inputs}  call: {function_call_str}")
            exec_result = sbx.run_code(function_call_str) # Execute Python inside the sandbox
            time.sleep(1) # Pausa entre ejecuciones de test para evitar rate limits

            print(f"test {id}:  {exec_result}")
            print(exec_result.logs)
            traceback = exec_result.get("traceback")

            if not exec_result.get("success", False):
                results.append({
                    "case": idx,
                    "success": False,
                    "traceback": exec_result.get("traceback", "Unknown error"),
                    "input":inputs,
                    "output": None,
                    "expected": expected
                })
                all_success = False
                continue

            output = exec_result.get("OUTPUT")  # salida esperada del intérprete
            if output == expected:
                results.append({
                    "case": idx,
                    "success": True,
                    "input":inputs,
                    "output": output,
                    "message": "Salida correcta.",
                    "expected": expected
                })
            else:
                results.append({
                    "case": idx,
                    "success": True,
                    "input":inputs,
                    "output": output,
                    "message": "Salida obtenida, pero no coincide con el esperado.",
                    "expected": expected
                })
                all_success = False

        except Exception as e:
            tb = getattr(e, "traceback", str(e))
            results.append({
                "case": idx,
                "success": False,
                "traceback": tb,
                "input":inputs,
                "output": None,
                "expected": expected
            })
            all_success = False
    #finally:
    #    if 'sbx' in locals() and sbx is not None:
    #        sbx.close() # Asegurarse de cerrar el sandbox al finalizar o si hay un error

    return {
        "success": all_success,
        "traceback": traceback,
        "results": results
    }

"""# LLAMADA REAL AL LLM

"""

# @title
def call_gemini_2_5_real(role_prompt: str, context: str, response_schema: BaseModel = None, allow_use_tool = False) -> str:
    """
    Realiza una llamada a Gemini 2.5 Flash con el prompt de rol y el contexto.
    Aplica Pydantic Schema si se proporciona.
    """

    full_prompt = (
        f"{role_prompt}\n\n"
        f"--- DATOS ACTUALES DEL PROYECTO ---\n"
        f"{context}\n\n"
        f"--- TAREA ---\n"
    )

    config = {
        "temperature": 0.1,   # Baja temperatura para consistencia
        "max_output_tokens": 10000
    }

    if response_schema:
        # Esta es la rama del Product Owner
        config["response_mime_type"] = "application/json"
        config["response_schema"] = response_schema.model_json_schema()
        full_prompt += f"GENERA EL OUTPUT ÚNICAMENTE EN FORMATO JSON que se adhiera al siguiente esquema Pydantic: {response_schema.__name__}. No añadas explicaciones ni texto adicional."
    elif allow_use_tool:
        available_tools = [CodeExecutionToolWithInterpreter]
        config["tools"] = available_tools
        full_prompt += "Genera únicamente el bloque de texto solicitado en tu Output Esperado. No añadas explicaciones."
    else:
        full_prompt += "Genera únicamente el bloque de texto solicitado en tu Output Esperado. No añadas explicaciones."


    #print(f"\n--- PROMPT ENVIADO AL LLM ---")
    #print(f"Rol Prompt: {role_prompt[:200]}...") # Muestra solo los primeros 200 caracteres
    #print(f"Contexto: {context[:200]}...") # Muestra solo los primeros 200 caracteres
    #print(f"Full Prompt para LLM: {full_prompt[:500]}...") # Muestra solo los primeros 500 caracteres
    #print(f"Configuración de Generación: {config}")

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=full_prompt,
            config=config, # Changed parameter name from 'config' to 'generation_config'
        )
        #print(f"✅ Respuesta del LLM: {response}")
        return response.text

    except APIError as e:
        return f"ERROR_API: No se pudo conectar con Gemini. {e}"
    except Exception as e:
        return f"ERROR_GENERAL: {e}"

# =======

"""#NODOS DE AGENTES"""

# @title
def ingeniero_de_requisitos_node(state: AgentState) -> AgentState:
    print("\n--- 1. 🙋‍♂️ Ingeniero de Requisitos ---")

    role_prompt = """
    Rol:
    Ingeniero de Requisitos experto.

    Objetivo:
    Convertir el requisito inicial o el feedback de rechazo en una especificación clara y verificable.

    Instrucciones:
    Leer el texto de entrada y eliminar ambigüedades; si hay rechazo, incorporar sus fundamentos.

    Construir la salida en la plantilla siguiente (sin dejar campos vacíos):
      Título: [Título del requisito]
      Descripción: [Descripción clara y concisa]
      Supuestos: [Lista de supuestos]
      Alcance: [Qué incluye y qué no]
      Criterios de aceptación: [Lista de criterios medibles]
      Referencias: [Fuentes o documentos relevantes]
      Output esperado: un único bloque de texto bajo el título "REQUISITO CLARIFICADO".
    """

    contexto_llm = f"Prompt Inicial: {state['prompt_inicial']}\nFeedback Anterior: {state['feedback_stakeholder']}"

    respuesta_llm = call_gemini_2_5_real(role_prompt, contexto_llm)

    state['requisito_clarificado'] = re.sub(r'## REQUISITO CLARIFICADO\n', '', respuesta_llm).strip()
    state['feedback_stakeholder'] = ""
    state['attempt_count'] += 1 # Contar el intento de corrección de alto nivel
    print(f"   -> Requisito Clarificado. Intento: {state['attempt_count']}/{state['max_attempts']}")
    print(f"   ->        OUTPUT: \n{state['requisito_clarificado']}")
    return state

# @title
def product_owner_node(state: AgentState) -> AgentState:
    print("--- 2. 💼 Product Owner (Usando Pydantic Parser) ---")

    role_prompt = """
    Rol:
    Product Owner estricto

    Objetivo:
    Recibir el requisito clarificado y transformarlo en una especificación formal ejecutable y trazable.

    Instrucción Principal:
    Desglosa el requisito clarificado en un formato JSON estricto que cumpla el esquema FormalRequirements.

    Formato y trazabilidad:
    Incluye campos de trazabilidad: version, estado (Propuesto, Aprobado, Rechazado), fuente y fecha de creación.
    Incluye ejemplos de pruebas (tests) que validen cada criterio de aceptación relevante para el requisito.
    Evita información duplicada; cada dato debe estar referenciado por su origen.

    Output Esperado:
    Un único objeto JSON conforme al esquema Pydantic FormalRequirements, con campos de trazabilidad y pruebas.
    """

    contexto_llm = f"Requisito Clarificado: {state['requisito_clarificado']}"

    respuesta_llm = call_gemini_2_5_real(role_prompt, contexto_llm, FormalRequirements)

    try:
        # Validar y almacenar la salida JSON del LLM
        req_data = FormalRequirements.model_validate_json(respuesta_llm)
        state['requisitos_formales'] = req_data.model_dump_json(indent=2)
        print(f"   -> Requisitos Formales generados (JSON validado).")
        print(f"   ->        OUTPUT: \n{state['requisitos_formales']}")
    except Exception as e:
        state['requisitos_formales'] = f"ERROR_PARSING: Fallo al validar JSON. {e}. LLM Output: {respuesta_llm[:100]}"
        print(f"   ❌ ERROR: Fallo de parsing en Product Owner. Esto podría requerir un bucle de corrección.")

    return state

# @title
def codificador_node(state: AgentState) -> AgentState:
    print("--- 3. 💻 Codificador ---")

    role_prompt = """
    Rol:
    Desarrollador de Software Python Sénior

    Objetivo:
    Generar código Python que satisfaga los requisitos formales y, si se proporciona un traceback, corregir los errores del código anterior.

    Instrucción Principal:
    Si se incluye un 'traceback', analizar el error y corregir el código existente para que compilar y ejecutar sin errores.
    Producir una única función Python autocontenida que implemente la lógica solicitada, con entradas y salidas claramente definidas y sin dependencias externas.
    Incluir pruebas pequeñas o ejemplos de uso mínimos dentro del propio bloque de código si es pertinente.
    Formato de salida:

    Output Esperado:
    Código Python completo, envuelto en un bloque de código markdown con la etiqueta python .

    Requisitos de calidad:
    La función debe contener comentarios explicativos donde sea útil.
    Manejo básico de errores con excepciones bien descritas.
    Tipos de entrada y salida tipados (type hints) cuando sea posible.
    """
    contexto_llm = f"Requisitos Formales (JSON): {state['requisitos_formales']}\nTraceback para corrección: {state['traceback']}"

    respuesta_llm = call_gemini_2_5_real(role_prompt, contexto_llm)

    # Limpieza de bloques de código markdown
    #code = re.sub(r'```python|```|\n', '', respuesta_llm).strip()
    code= respuesta_llm
    #%pdb on
    #ipdb.set_trace(context=6)
    state['codigo_generado'] = code
    state['traceback'] = ""
    print(f"   -> Código {'CORREGIDO' if 'def safe_sum' not in code[:10] else 'GENERADO'} para pruebas.")
    print(f"   ->        OUTPUT: {state['codigo_generado']}")

    return state

def probador_depurador_node(state: AgentState) -> AgentState: # Changed return type to AgentState
    print("--- 4.1 🧪 Probador/Depurador --- Generar casos de test")

    role_prompt1 = """
    Tu rol es el de un Ingeniero de Control de Calidad (QA) riguroso.
    Objetivo: Definir casos de prueba para el 'Código generado' tomando como ejemplo el 'Ejemplo de tests'

    Instrucción Principal:
    1. Genera un Diccionario python de dos elementos con la forma especificada en el siguiente ejemplo:
      test_data_simulada = [
          {"input": [1, 5, 2, -3], "expected": 5},
          {"input": [10, -5], "expected": 5}
      ]
    2. Asegúra que el diccionario contiene DIEZ CASOS DE TEST.
    """

    # Primero queremos que genere los casos de test
    contexto_llm1 = f"Código generado: {state['codigo_generado']}"
    respuesta_llm1 = call_gemini_2_5_real(role_prompt1, contexto_llm1)
    test_cases = re.sub(r'```python|```|\n', '', respuesta_llm1).strip()
    print(f"Test cases: {test_cases}")

    print("--- 4.2 🧪 Probador/Depurador --- Probar casos de test")
    #segundo queremos que use los casos de test con el código generado a través de la tool
    role_prompt2 = """
    Tu rol es el de un Ingeniero de Control de Calidad (QA) riguroso.
    Objetivo: Simula la ejecución segura de código Python contra datos de prueba.

    Instrucción Principal:
    #1. Simula la ejecución segura de código Python contra datos de prueba con los argumentos de Test a usar.
    #2. Evalúa la salida de la herramienta.

    Evaluar la salida:
    Si todos los casos pasan, generar un informe con estado "PASSED".
    Si alguno falla, generar un informe con estado "FAILED" e incluir el Traceback/proveniencia del fallo proporcionado por la herramienta.

    Formato de salida:
    Un diccionario que contiene:
      "status": "PASSED" | "FAILED",
      "traceback": "<traceback global si corresponde>"
      "results": Un List[dict] que contiene:
          "case": <número de caso>,
          "input": <entrada>,
          "expected": <salida esperada>,
          "actual": <salida obtenida>,
          "result": "PASSED" | "FAILED",
          "traceback": "<traceback si hay fallo>"

    Notas:
    Si algún caso falla, include el traceback asociado en el detalle correspondiente.
    """

    contexto_llm2 = f"Código-generado: {state['codigo_generado']}\n Tests a usar: {test_cases}"
    respuesta_llm2 = call_gemini_2_5_real(role_prompt2, contexto_llm2, None, True)

    #print("--- Respuesta del Modelo (Paso 1: Llamada a Tool) ---")
    #print(f"El modelo solicita una llamada a la herramienta: {respuesta_llm2.function_calls[0].name}")
    #print(f"Argumentos proporcionados: {dict(respuesta_llm2.function_calls[0].args)}")
    #print("-" * 40)
    print(f"Respuesta del LLM de testeo: {respuesta_llm2}")
    respuesta_llm2 = re.sub(r'```json|```', '', respuesta_llm2).strip()

    try:
        respuesta_dict = json.loads(respuesta_llm2)
    except json.JSONDecodeError as e:
        print(f"Error al decodificar JSON: {e}")
        print("La cadena JSON de entrada no tiene el formato correcto.")
        # datos_dict_seguro no está definido, o puedes inicializarlo a un valor seguro (ej: {})
        respuesta_dict = {}

    if respuesta_dict == "None":
        state['pruebas_superadas'] = False
        print(f"   -> Resultado: FAILED. No se pudo parsear la respuesta del LLM.")
        return state

    if respuesta_dict["status"]:
        state['pruebas_superadas'] = True
        print(f"   -> Resultado: TRUE")
        print(f"   ->        OUTPUT: {state['pruebas_superadas']}")
        if respuesta_dict["results"]:
          # Acceder a la lista de resultados
          results: List[Dict[str, Any]] = respuesta_dict.get("results", [])

          # 4. Bucle para mostrar la información de depuración
          print("=" * 60)
          print(f"📋 Resumen General de la Ejecución: {respuesta_dict.get('status')}")
          print(f"🚨 Traceback General: {respuesta_dict.get('traceback') if respuesta_dict.get('traceback') else 'Ninguno'}")
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

              if status != "PASSED": # o si hay un traceback específico del caso
                  print(f"  ⚠️ Traceback del Caso: {traceback_case if traceback_case else 'N/A'}")

              print("-" * 20)

          print("=" * 60)


    else:
        state['pruebas_superadas'] = False
        state['traceback'] = respuesta_dict["traceback"]
        print(f"   -> Resultado: FAILED. Traceback: {respuesta_dict['traceback'][:50]}...")
        print(f"   ->        OUTPUT: {state['pruebas_superadas']}")

    return state # Return the modified state

# @title
def stakeholder_node(state: AgentState) -> AgentState:
    print("--- 5. ✅ Stakeholder ---")

    # Comprobar si se excedió el límite de intentos (EVOLUCIÓN CLAVE)
    if state['attempt_count'] >= state['max_attempts']:
        state['validado'] = False
        print(f"   ❌ LÍMITE DE INTENTOS EXCEDIDO ({state['max_attempts']}). PROYECTO FALLIDO.")
        # In LangGraph, to exit with a specific state and avoid further transitions, you return the state.
        # The conditional edges from 'Stakeholder' will handle routing based on 'validado' and 'attempt_count'.
        return state

   # role_prompt = """
   # Tu rol es el de un Stakeholder de negocio.
   # Objetivo: Validar si el código cumple con la intención de negocio (formato, usabilidad, etc.).
   # Instrucción Principal: Revisa el 'codigo_generado'. Si cumple *todos* los puntos de los 'requisitos_formales' (incluyendo formato de salida), devuelve VALIDADO. Si falta algo (ej. formato), devuelve RECHAZADO con un motivo claro.
   # Output Esperado: Un bloque de texto que contenga "VALIDACIÓN FINAL" y el resultado (VALIDADO/RECHAZADO) con el "Motivo:" si es rechazado.
   # """

    role_prompt = """
    Rol:
    Eres un Stakeholder de Negocio crítico con la entrega final. Eres la última línea de defensa contra desviaciones de la visión del producto.

    Contexto y Fuente de la Verdad:
    El código ha pasado todas las pruebas técnicas de QA, pero tú verificas la intención de negocio y la usabilidad.
    La única fuente de verdad para la validación son los 'requisitos_formales' (en formato JSON) y el 'codigo_generado' (que incluye la lógica y la salida final).

    Instrucciones de Decisión Rigurosas:
        Revisión Estricta: Compara meticulosamente la lógica final del 'codigo_generado' con cada punto en el JSON de 'requisitos_formales',
        prestando especial atención a: Formato de Salida: ¿El código produce la cadena o estructura (ej., JSON, frase, entero) especificada exactamente en el requisito formal?
        Funcionalidad Clave: ¿Resuelve el problema de negocio de la manera esperada (ej., manejo de errores de entrada, lógica de negocio)?

    Resultado Binario:
        VALIDADO: Devuelve VALIDADO solo si el código cumple el 100% de los requisitos formales.
        RECHAZADO: Devuelve RECHAZADO si se encuentra cualquier desviación o si el código es funcionalmente correcto pero inútil para el negocio
            (ej., el código genera un resultado, pero con el formato incorrecto).

    Output Esperado (Obligatorio):
    Tu salida DEBE comenzar con la etiqueta "VALIDACIÓN FINAL" y seguir la estructura binaria.

    Output Esperado:
        Si APROBADO: Un bloque de texto que contenga únicamente "VALIDACIÓN FINAL: VALIDADO".
        Si RECHAZADO: Un bloque de texto que contenga "VALIDACIÓN FINAL: RECHAZADO" seguido de una línea que empiece con "Motivo:" y describa CLARAMENTE la desviación de los requisitos formales.
    """

    contexto_llm = f"Código aprobado técnicamente: {state['codigo_generado']}\nRequisitos Formales (JSON): {state['requisitos_formales']}"
    respuesta_llm = call_gemini_2_5_real(role_prompt, contexto_llm)

    # Lógica de transición de validación
    if "VALIDADO" in respuesta_llm:
        state['validado'] = True
        print("   -> Resultado: VALIDADO. Proyecto Terminado.")
    else:
        state['validado'] = False
        # Extraer el feedback de rechazo
        feedback_match = re.search(r'Motivo: (.*)', respuesta_llm)
        if feedback_match:
            state['feedback_stakeholder'] = feedback_match.group(1).strip()
        print(f"   -> Resultado: RECHAZADO. Motivo: {state['feedback_stakeholder'][:50]}... Volviendo a Ingeniero de Requisitos.")

    return state

"""CONFIGURACIÓN Y COMPILACIÓN DEL GRAFO (LANGGRAPH)

"""

# @title
workflow = StateGraph(AgentState)

# 1. Añadir Nodos
workflow.add_node("IngenieroRequisitos", ingeniero_de_requisitos_node)
workflow.add_node("ProductOwner", product_owner_node)
workflow.add_node("Codificador", codificador_node)
workflow.add_node("ProbadorDepurador", probador_depurador_node)
workflow.add_node("Stakeholder", stakeholder_node)

# 2. Definir Transiciones Iniciales y Lineales
workflow.add_edge(START, "IngenieroRequisitos")
workflow.add_edge("IngenieroRequisitos", "ProductOwner")
workflow.add_edge("ProductOwner", "Codificador")
workflow.add_edge("Codificador", "ProbadorDepurador")
workflow.add_edge("ProbadorDepurador", "Stakeholder")

# 3. Transiciones Condicionales

# A. Bucle de Depuración (Interno: Corrección de Código)
workflow.add_conditional_edges(
    "ProbadorDepurador",
    lambda x: "PASSED" if x['pruebas_superadas'] else "FAILED",
    {
        "FAILED": "Codificador",
        "PASSED": "Stakeholder"
    }
)

# B. Bucle de Validación (Externo: Reingeniería de Requisitos / Fallo Final)
workflow.add_conditional_edges(
    "Stakeholder",
    lambda x: "VALIDADO" if x['validado'] else ("FAILED_FINAL" if x['attempt_count'] >= x['max_attempts'] else "RECHAZADO"),
    {
        "RECHAZADO": "IngenieroRequisitos",
        "VALIDADO": END,
        "FAILED_FINAL": END, # Nuevo nodo de terminación por límite excedido
    }
)

# 4. Compilar el Grafo
app = workflow.compile()


# mostramos el grafo en formato mermaid como imagen dentro del notebook
display(
    Image(
        app.get_graph().draw_mermaid_png()
    )
)



"""# AUXILIARES"""

def guardar_fichero_texto(nombre_fichero: str, contenido: str) -> bool:
    """
    Guarda el contenido proporcionado en un fichero de texto.

    Si el fichero existe, su contenido será sobrescrito.

    Args:
        nombre_fichero (str): El nombre o ruta del fichero a guardar (ej: "datos.txt").
        contenido (str): El texto que se va a escribir en el fichero.

    Returns:
        bool: True si la operación fue exitosa, False en caso contrario.
    """
    try:
        # Usamos 'with open(..., "w")' para:
        # 1. Abrir el fichero en modo 'w' (write - escritura).
        # 2. Asegurar que el fichero se cierre automáticamente, incluso si hay errores.
        # 3. 'w' sobrescribe el contenido anterior si el fichero ya existe.
        with open(nombre_fichero, "w", encoding="utf-8") as file:
            file.write(contenido)

        print(f"✅ Fichero '{nombre_fichero}' guardado exitosamente.")
        return True

    except IOError as e:
        # Captura errores relacionados con la entrada/salida (permisos, ruta incorrecta, etc.)
        print(f"❌ Error al guardar el fichero '{nombre_fichero}': {e}")
        return False

"""# EJECUCIÓN DEL FLUJO"""

# @title
initial_state = {
    "prompt_inicial": "Quiero una función simple en Python para sumar una lista de números, y quiero que la salida sea una frase.",
    "feedback_stakeholder": "",
    "max_attempts": 3, # Permitimos 3 ciclos completos (alto nivel)
    "attempt_count": 0,
    "pruebas_superadas": False,
    "validado": False,
    "traceback": "",
    "requisito_clarificado": "",
    "requisitos_formales": "",
    "codigo_generado": ""
}

print("\n\n#####################################################")
print("INICIO DEL FLUJO MULTIAGENTE DE DESARROLLO (LANGGRAPH)")
print("#####################################################")

# Acumular el estado a medida que el grafo se ejecuta
current_final_state = initial_state.copy()

for step, node_output_map in enumerate(app.stream(initial_state), 1):
    print(f"\n===== CICLO DE TRABAJO, PASO {step} ====")
    print(node_output_map)

    # El 'node_output_map' es un diccionario donde la clave es el nombre del nodo
    # que acaba de ejecutarse y el valor son los cambios de estado que retornó ese nodo.
    # Actualizamos nuestro estado acumulado con estos cambios.
    for node_name, delta_dict in node_output_map.items():
        current_final_state.update(delta_dict)

# El estado final es el estado acumulado después de que el stream ha terminado.
final_state = current_final_state

print("\n\n#####################################################")
print("ESTADO FINAL DEL PROYECTO")
print("#####################################################")

# Aseguramos que final_state no sea None si el stream estaba vacío o falló antes de un output.
if final_state is None:
    print("❌ El flujo no produjo un estado final o falló prematuramente.")
else:
    print(f"✅ Validación Final: {'APROBADO' if final_state['validado'] else 'FALLÓ TRAS INTENTOS'}")
    print("-" * 40)
    print(f"Intentos Totales: {final_state['attempt_count']}")
    print("Código Final y Corregido:")
    # Envolver la salida en un bloque de código Markdown para una mejor visualización
    print(f"\n{final_state['codigo_generado']}\n")
    codeToPrint = re.sub(r'```python|```', '', final_state['codigo_generado']).strip()
    guardar_fichero_texto("codigo_final.py", codeToPrint)