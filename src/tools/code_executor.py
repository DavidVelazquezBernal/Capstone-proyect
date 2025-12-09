"""
Herramientas para ejecución segura de código Python.
"""

import re
from typing import List, Dict
from e2b_code_interpreter import Sandbox


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


def extract_function_name_ts(code: str) -> str:
    """
    Extrae el nombre de la primera función definida en un bloque de código TypeScript.

    Args:
        code (str): El código TypeScript.

    Returns:
        str: El nombre de la función si se encuentra, de lo contrario None.
    """
    # Busca funciones con: function name() o const/let name = function() o const/let name = () =>
    patterns = [
        r'function\s+(\w+)\s*\(',  # function name()
        r'(?:const|let|var)\s+(\w+)\s*=\s*function',  # const name = function
        r'(?:const|let|var)\s+(\w+)\s*=\s*\([^)]*\)\s*=>'  # const name = () =>
    ]
    
    for pattern in patterns:
        match = re.search(pattern, code)
        if match:
            return match.group(1)
    return None


def CodeExecutionToolWithInterpreter(code: str, test_data: List[dict]) -> dict:
    """
    Ejecución segura de código Python contra datos de prueba usando E2B Sandbox.

    Args:
        code (str): El código Python generado que se va a ejecutar.
        test_data (List[dict]): Una lista de diccionarios, donde cada diccionario representa un caso de prueba.
                                Contiene 'input' (argumentos para el código) y 'expected' (salida esperada).

    Returns:
        dict: Un diccionario que contiene:
              - 'success' (bool): True si todas las pruebas pasan, False en caso contrario.
              - 'results' (List[dict]): Una lista de resultados por cada caso de prueba
              - 'traceback' (str): Un mensaje de traceback general si alguna prueba falla
    """
    print(f"\n---     🧪 TOOL PY: Ejecutando {len(test_data)} casos de prueba... ---")

    results = []
    all_success = True
    traceback = ""

    # Crear el sandbox
    sbx = Sandbox.create()
    #time.sleep(2)  # Pausa inicial para la creación del sandbox
    exec_result = sbx.run_code(code)

    function_name = extract_function_name(code)
    if not function_name:
        #sbx.close()
        return {
            "success": False,
            "traceback": "Error: Could not find function name in the provided code.",
            "results": []
        }

    for idx, case in enumerate(test_data, start=1):
        inputs = case.get("input", [])
        expected = case.get("expected")

        try:
            function_call_str = f"print({function_name}({inputs}))"

            print(f"Sandbox test {idx}:  call: {function_call_str}  expected: {expected}")
            exec_result = sbx.run_code(function_call_str)
            #time.sleep(1)  # Pausa entre ejecuciones de test

            print(f"test {idx}:  exec_result: {exec_result}")
            print(f"           {exec_result.logs}")
            
            # exec_result es un objeto Execution, no un dict - usar atributos
            if exec_result.error:
                traceback = str(exec_result.error)
                error_value = exec_result.error.value if hasattr(exec_result.error, 'value') else str(exec_result.error)
                
                # Si hay un error, verificar si coincide con el expected
                if error_value == expected:
                    print(f"... TOOL: Error esperado coincide con el resultado")
                    results.append({
                        "case": idx,
                        "success": True,
                        "input": inputs,
                        "output": error_value,
                        "message": "Error esperado coincide correctamente.",
                        "expected": expected
                    })
                    continue
                else:
                    print(f"... TOOL: Error no esperado o no coincide")
                    results.append({
                        "case": idx,
                        "success": False,
                        "traceback": traceback,
                        "input": inputs,
                        "output": error_value,
                        "expected": expected
                    })
                    all_success = False
                    continue
            
            if not exec_result.logs.stdout:
                print(f"... TOOL ENTRÓ NO HAY STDOUT")
                results.append({
                    "case": idx,
                    "success": False,
                    "traceback": "No output generated",
                    "input": inputs,
                    "output": None,
                    "expected": expected
                })
                all_success = False
                continue

            # La salida está en logs.stdout (es una lista)
            output = exec_result.logs.stdout[0] if exec_result.logs.stdout else None
            # Limpiar salida si existe
            if output:
                output = output.strip()
            if output == expected:
                results.append({
                    "case": idx,
                    "success": True,
                    "input": inputs,
                    "output": output,
                    "message": "Salida correcta.",
                    "expected": expected
                })
            else:
                results.append({
                    "case": idx,
                    "success": True,
                    "input": inputs,
                    "output": output,
                    "message": "Salida obtenida, pero no coincide con el esperado.",
                    "expected": expected
                })
                all_success = False

        except Exception as e:
            print(f"... TOOL ENTRÓ POR EXCEPCIÓN: {e}")
            tb = getattr(e, "traceback", str(e))
            results.append({
                "case": idx,
                "success": False,
                "traceback": tb,
                "input": inputs,
                "output": None,
                "expected": expected
            })
            all_success = False

    #sbx.close()

    return {
        "success": all_success,
        "traceback": traceback,
        "results": results
    }


def CodeExecutionToolWithInterpreterTS(code: str, test_data: List[dict]) -> dict:
    """
    Ejecución segura de código TypeScript contra datos de prueba usando E2B Sandbox.

    Args:
        code (str): El código TypeScript generado que se va a ejecutar.
        test_data (List[dict]): Una lista de diccionarios, donde cada diccionario representa un caso de prueba.
                                Contiene 'input' (argumentos para el código) y 'expected' (salida esperada).

    Returns:
        dict: Un diccionario que contiene:
              - 'success' (bool): True si todas las pruebas pasan, False en caso contrario.
              - 'results' (List[dict]): Una lista de resultados por cada caso de prueba
              - 'traceback' (str): Un mensaje de traceback general si alguna prueba falla
    """
    print(f"\n---     🧪 TOOL TS: Ejecutando {len(test_data)} casos de prueba... ---")

    results = []
    all_success = True
    traceback = ""

    # Crear el sandbox
    sbx = Sandbox.create()
    
    function_name = extract_function_name_ts(code)
    if not function_name:
        return {
            "success": False,
            "traceback": "Error: Could not find function name in the provided TypeScript code.",
            "results": []
        }

    # Escribir el código TypeScript en un archivo
    sbx.files.write("/tmp/code.ts", code)
    
    for idx, case in enumerate(test_data, start=1):
        inputs = case.get("input", [])
        expected = case.get("expected")

        try:
            # Preparar los argumentos para TypeScript
            # Convertir inputs de Python a formato TypeScript/JavaScript
            if isinstance(inputs, list):
                args_str = ", ".join([repr(arg) if isinstance(arg, str) else str(arg) for arg in inputs])
            else:
                args_str = repr(inputs) if isinstance(inputs, str) else str(inputs)

            # Crear un script de prueba que importa y ejecuta la función
            test_script = f"""
                import {{ {function_name} }} from './code';
                console.log({function_name}({args_str}));
            """
            
            sbx.files.write("/tmp/test.ts", test_script)
            
            # Ejecutar con ts-node
            exec_result = sbx.run_code(f"cd /tmp && npx ts-node test.ts")

            print(f"Sandbox test {idx}:  call: {function_name}({args_str})  expected: {expected}")
            print(f"test {idx}:  exec_result: {exec_result}")
            print(f"           {exec_result.logs}")
            
            # Manejar errores
            if exec_result.error:
                traceback = str(exec_result.error)
                error_value = exec_result.error.value if hasattr(exec_result.error, 'value') else str(exec_result.error)
                
                # Si hay un error, verificar si coincide con el expected
                if error_value == expected:
                    print(f"... TOOL TS: Error esperado coincide con el resultado")
                    results.append({
                        "case": idx,
                        "success": True,
                        "input": inputs,
                        "output": error_value,
                        "message": "Error esperado coincide correctamente.",
                        "expected": expected
                    })
                    continue
                else:
                    print(f"... TOOL TS: Error no esperado o no coincide")
                    results.append({
                        "case": idx,
                        "success": False,
                        "traceback": traceback,
                        "input": inputs,
                        "output": error_value,
                        "expected": expected
                    })
                    all_success = False
                    continue
            
            if not exec_result.logs.stdout:
                print(f"... TOOL TS ENTRÓ NO HAY STDOUT")
                results.append({
                    "case": idx,
                    "success": False,
                    "traceback": "No output generated",
                    "input": inputs,
                    "output": None,
                    "expected": expected
                })
                all_success = False
                continue

            # La salida está en logs.stdout (es una lista)
            output = exec_result.logs.stdout[0] if exec_result.logs.stdout else None
            # Limpiar salida si existe
            if output:
                output = output.strip()
            
            if output == expected:
                results.append({
                    "case": idx,
                    "success": True,
                    "input": inputs,
                    "output": output,
                    "message": "Salida correcta.",
                    "expected": expected
                })
            else:
                results.append({
                    "case": idx,
                    "success": True,
                    "input": inputs,
                    "output": output,
                    "message": "Salida obtenida, pero no coincide con el esperado.",
                    "expected": expected
                })
                all_success = False

        except Exception as e:
            print(f"... TOOL TS ENTRÓ POR EXCEPCIÓN: {e}")
            tb = getattr(e, "traceback", str(e))
            results.append({
                "case": idx,
                "success": False,
                "traceback": tb,
                "input": inputs,
                "output": None,
                "expected": expected
            })
            all_success = False

    #sbx.close()

    return {
        "success": all_success,
        "traceback": traceback,
        "results": results
    }

