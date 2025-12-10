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


def extract_function_parameters(code: str) -> list:
    """
    Extrae los nombres de los parámetros de la primera función Python.
    
    Args:
        code (str): El código Python.
        
    Returns:
        list: Lista de nombres de parámetros.
    """
    # Buscar la definición de función: def nombre(params):
    match = re.search(r'def\s+\w+\s*\(([^)]*)\)', code)
    if match:
        params_str = match.group(1).strip()
        if not params_str:
            return []
        # Extraer nombres de parámetros (antes de : o = si hay tipado o valor por defecto)
        params = []
        for param in params_str.split(','):
            param = param.strip()
            # Extraer nombre antes de : o = (tipado o valor por defecto)
            param_name = re.split(r'[:\s=]', param)[0].strip()
            if param_name and param_name != '*' and param_name != '**':
                # Remover * o ** de *args, **kwargs
                param_name = param_name.lstrip('*')
                if param_name:
                    params.append(param_name)
        return params
    return []


def is_class_code(code: str) -> bool:
    """
    Detecta si el código define una clase.
    
    Args:
        code (str): El código Python.
        
    Returns:
        bool: True si el código contiene una clase.
    """
    return bool(re.search(r'class\s+\w+', code))


def extract_class_name(code: str) -> str:
    """
    Extrae el nombre de la clase del código Python.
    
    Args:
        code (str): El código Python.
        
    Returns:
        str: Nombre de la clase o None.
    """
    match = re.search(r'class\s+(\w+)', code)
    return match.group(1) if match else None


def is_class_code_ts(code: str) -> bool:
    """
    Detecta si el código TypeScript define una clase.
    
    Args:
        code (str): El código TypeScript.
        
    Returns:
        bool: True si el código contiene una clase.
    """
    return bool(re.search(r'(?:export\s+)?class\s+\w+', code))


def extract_class_name_ts(code: str) -> str:
    """
    Extrae el nombre de la clase del código TypeScript.
    
    Args:
        code (str): El código TypeScript.
        
    Returns:
        str: Nombre de la clase o None.
    """
    match = re.search(r'(?:export\s+)?class\s+(\w+)', code)
    return match.group(1) if match else None


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


def extract_function_parameters_ts(code: str) -> list:
    """
    Extrae los nombres de los parámetros de la primera función TypeScript.
    
    Args:
        code (str): El código TypeScript.
        
    Returns:
        list: Lista de nombres de parámetros.
    """
    # Buscar diferentes patrones de funciones
    patterns = [
        r'function\s+\w+\s*\(([^)]*)\)',  # function name(params)
        r'(?:const|let|var)\s+\w+\s*=\s*function\s*\(([^)]*)\)',  # const name = function(params)
        r'(?:const|let|var)\s+\w+\s*=\s*\(([^)]*)\)\s*=>'  # const name = (params) =>
    ]
    
    for pattern in patterns:
        match = re.search(pattern, code)
        if match:
            params_str = match.group(1).strip()
            if not params_str:
                return []
            # Extraer nombres de parámetros (antes del : si hay tipado)
            params = []
            for param in params_str.split(','):
                param = param.strip()
                # Extraer nombre antes de : o = (tipado o valor por defecto)
                param_name = re.split(r'[:\s=]', param)[0].strip()
                if param_name:
                    params.append(param_name)
            return params
    return []


def CodeExecutionToolWithInterpreterPY(code: str, test_data: List[dict]) -> dict:
    """
    Ejecución segura de código Python contra datos de prueba usando E2B Sandbox.
    Soporta tanto funciones individuales como clases con múltiples métodos.

    Args:
        code (str): El código Python generado que se va a ejecutar.
        test_data (List[dict]): Una lista de diccionarios, donde cada diccionario representa un caso de prueba.
                                Contiene 'input' (argumentos para el código), 'expected' (salida esperada),
                                y opcionalmente 'method' (para clases).

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
    exec_result = sbx.run_code(code)

    # Detectar si es una clase o función
    is_class = is_class_code(code)
    
    if is_class:
        # Código de clase
        class_name = extract_class_name(code)
        if not class_name:
            return {
                "success": False,
                "traceback": "Error: Could not find class name in the provided code.",
                "results": []
            }
        print(f"   📦 Detectada clase: {class_name}")
        
        # Instanciar la clase
        instance_code = f"{class_name.lower()}_instance = {class_name}()"
        exec_result = sbx.run_code(instance_code)
        if exec_result.error:
            return {
                "success": False,
                "traceback": f"Error al instanciar la clase: {exec_result.error}",
                "results": []
            }
    else:
        # Código de función
        function_name = extract_function_name(code)
        if not function_name:
            return {
                "success": False,
                "traceback": "Error: Could not find function name in the provided code.",
                "results": []
            }
        print(f"   🔧 Detectada función: {function_name}")
    
    for idx, case in enumerate(test_data, start=1):
        inputs = case.get("input", [])
        expected = case.get("expected")
        method_name = case.get("method")  # Para clases

        try:
            # Preparar los argumentos según el tipo de inputs
            if isinstance(inputs, list):
                # Lista de argumentos: usar directamente
                args_str = ", ".join(repr(arg) for arg in inputs)
            elif isinstance(inputs, dict):
                # Si es un diccionario, buscar propiedades que coincidan con parámetros de la función
                function_params = extract_function_parameters(code)
                matched_values = []
                for param in function_params:
                    if param in inputs:
                        value = inputs[param]
                        matched_values.append(repr(value))
                
                if matched_values:
                    # Si encontramos coincidencias, usar esos valores
                    args_str = ", ".join(matched_values)
                else:
                    # Si no hay coincidencias, intentar con 'n' como fallback
                    value = inputs.get('n', inputs)
                    args_str = repr(value)
            else:
                # Valor único: usar repr() para mantener el tipo
                args_str = repr(inputs)
            
            # Construir la llamada según si es clase o función
            if is_class and method_name:
                # Llamada a método de clase
                function_call_str = f"print({class_name.lower()}_instance.{method_name}({args_str}))"
            else:
                # Llamada a función
                function_call_str = f"print({function_name}({args_str}))"

            #print(f"Sandbox test {idx}:  call: {function_call_str}  expected: {expected}")
            exec_result = sbx.run_code(function_call_str)
            #time.sleep(1)  # Pausa entre ejecuciones de test

            # print(f"test {idx}:  exec_result: {exec_result}")
            # print(f"           {exec_result.logs}")
            
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
    Soporta tanto funciones individuales como clases con múltiples métodos.

    Args:
        code (str): El código TypeScript generado que se va a ejecutar.
        test_data (List[dict]): Una lista de diccionarios, donde cada diccionario representa un caso de prueba.
                                Contiene 'input' (argumentos para el código), 'expected' (salida esperada),
                                y opcionalmente 'method' (para clases).

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
    
    # Detectar si es una clase o función
    is_class = is_class_code_ts(code)
    
    if is_class:
        # Código de clase
        class_name = extract_class_name_ts(code)
        if not class_name:
            return {
                "success": False,
                "traceback": "Error: Could not find class name in the provided TypeScript code.",
                "results": []
            }
        print(f"   📦 Detectada clase: {class_name}")
    else:
        # Código de función
        function_name = extract_function_name_ts(code)
        if not function_name:
            return {
                "success": False,
                "traceback": "Error: Could not find function name in the provided TypeScript code.",
                "results": []
            }
        print(f"   🔧 Detectada función: {function_name}")
    
    # Escribir el código TypeScript en un archivo
    sbx.files.write("/tmp/code.ts", code)
    
    # Intentar instalar esbuild si no está disponible
    try:
        sbx.commands.run("cd /tmp && npm list esbuild || npm install esbuild", timeout=30)
    except Exception as e:
        print(f"Warning: Could not verify/install esbuild: {e}")
    
    # Si es una clase, crear código adicional para instanciarla
    if is_class:
        instance_code = f"\nconst instance = new {class_name}();\n"
        sbx.files.write("/tmp/code.ts", code + instance_code)
    
    for idx, case in enumerate(test_data, start=1):
        inputs = case.get("input", [])
        expected = case.get("expected")
        method_name = case.get("method")  # Para clases

        try:
            # Preparar los argumentos para TypeScript
            # Convertir inputs de Python a formato TypeScript/JavaScript
            if isinstance(inputs, list):
                args_str = ", ".join([repr(arg) if isinstance(arg, str) else str(arg) for arg in inputs])
            elif isinstance(inputs, dict):
                # Si es un diccionario, buscar propiedades que coincidan con parámetros de la función
                function_params = extract_function_parameters_ts(code)
                matched_values = []
                for param in function_params:
                    if param in inputs:
                        value = inputs[param]
                        matched_values.append(str(value) if not isinstance(value, str) else repr(value))
                
                if matched_values:
                    # Si encontramos coincidencias, usar esos valores
                    args_str = ", ".join(matched_values)
                else:
                    # Si no hay coincidencias, intentar con 'n' como fallback
                    args_str = str(inputs.get('n', inputs))            
            else:
                args_str = repr(inputs) if isinstance(inputs, str) else str(inputs)

            # Construir código de ejecución según si es clase o función
            if is_class and method_name:
                # Llamada a método de clase
                execution_code = f"console.log(instance.{method_name}({args_str}));"
            else:
                # Llamada a función
                execution_code = f"const {{ {function_name} }} = require('./code');\nconsole.log({function_name}({args_str}));"

            # Usar esbuild para transpilar TypeScript a JavaScript en memoria y ejecutar
            transpile_and_run = f"""
                const esbuild = require('esbuild');
                const fs = require('fs');
                
                // Leer el código TypeScript
                const tsCode = fs.readFileSync('/tmp/code.ts', 'utf8');
                
                // Transpilar a JavaScript
                const result = esbuild.transformSync(tsCode, {{
                    loader: 'ts',
                    format: 'cjs',
                }});
                
                // Guardar el JavaScript transpilado
                fs.writeFileSync('/tmp/code.js', result.code);
                
                // Importar y ejecutar
                {execution_code}
            """
            
            sbx.files.write("/tmp/run.js", transpile_and_run)
            
            # Ejecutar el script que transpila y ejecuta
            exec_result = sbx.commands.run("cd /tmp && node run.js")

            print(f"Sandbox test {idx}:  call: {function_name}({args_str})  expected: {expected}")
            #print(f"test {idx}:  exec_result: {exec_result}")
            #print(f"           stdout: {exec_result.stdout}")
            #print(f"           stderr: {exec_result.stderr}")
            
            # Manejar errores - commands.run() retorna un objeto diferente
            if exec_result.exit_code != 0 or exec_result.stderr:
                traceback = exec_result.stderr if exec_result.stderr else "Error desconocido"
                error_value = traceback
                
                # Si hay un error, verificar si coincide con el expected
                if error_value == expected:
                    #print(f"... TOOL TS: Error esperado coincide con el resultado")
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
            
            if not exec_result.stdout:
                #print(f"... TOOL TS ENTRÓ NO HAY STDOUT")
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

            # La salida está en stdout (es un string, no una lista)
            output = exec_result.stdout.strip()
            
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
            #print(f"... TOOL TS ENTRÓ POR EXCEPCIÓN: {e}")
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

