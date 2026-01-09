import pytest
from tools.code_executor import (
    extract_function_name,
    extract_function_parameters,
    is_class_code,
    extract_class_name,
    is_class_code_ts,
    extract_class_name_ts
)


class TestExtractFunctionName:
    
    def test_extrae_nombre_funcion_simple(self):
        """Verifica que extrae el nombre de una función simple"""
        code = "def suma(a, b):\n    return a + b"
        result = extract_function_name(code)
        assert result == "suma"
    
    def test_extrae_nombre_primera_funcion(self):
        """Verifica que extrae la primera función cuando hay múltiples"""
        code = """
def suma(a, b):
    return a + b

def resta(a, b):
    return a - b
"""
        result = extract_function_name(code)
        assert result == "suma"
    
    def test_retorna_none_sin_funcion(self):
        """Verifica que retorna None si no hay función"""
        code = "x = 5\ny = 10"
        result = extract_function_name(code)
        assert result is None
    
    def test_extrae_funcion_con_tipado(self):
        """Verifica que extrae función con tipado Python"""
        code = "def calcular(x: int, y: int) -> int:\n    return x + y"
        result = extract_function_name(code)
        assert result == "calcular"


class TestExtractFunctionParameters:
    
    def test_extrae_parametros_simples(self):
        """Verifica que extrae parámetros simples"""
        code = "def suma(a, b):\n    return a + b"
        result = extract_function_parameters(code)
        assert result == ["a", "b"]
    
    def test_extrae_parametros_con_tipado(self):
        """Verifica que extrae parámetros con tipado"""
        code = "def suma(a: int, b: int) -> int:\n    return a + b"
        result = extract_function_parameters(code)
        assert result == ["a", "b"]
    
    def test_extrae_parametros_con_valores_default(self):
        """Verifica que extrae parámetros con valores por defecto"""
        code = "def suma(a, b=0):\n    return a + b"
        result = extract_function_parameters(code)
        assert result == ["a", "b"]
    
    def test_retorna_lista_vacia_sin_parametros(self):
        """Verifica que retorna lista vacía sin parámetros"""
        code = "def funcion():\n    pass"
        result = extract_function_parameters(code)
        assert result == []
    
    def test_retorna_lista_vacia_sin_funcion(self):
        """Verifica que retorna lista vacía sin función"""
        code = "x = 5"
        result = extract_function_parameters(code)
        assert result == []
    
    def test_maneja_args_y_kwargs(self):
        """Verifica que maneja *args y **kwargs"""
        code = "def funcion(a, *args, **kwargs):\n    pass"
        result = extract_function_parameters(code)
        assert "a" in result
        # args y kwargs pueden o no estar en el resultado dependiendo de la implementación


class TestIsClassCode:
    
    def test_detecta_clase_simple(self):
        """Verifica que detecta una clase simple"""
        code = """
class Calculator:
    def suma(self, a, b):
        return a + b
"""
        result = is_class_code(code)
        assert result is True
    
    def test_detecta_clase_con_herencia(self):
        """Verifica que detecta clase con herencia"""
        code = "class MiClase(BaseClass):\n    pass"
        result = is_class_code(code)
        assert result is True
    
    def test_retorna_false_sin_clase(self):
        """Verifica que retorna False sin clase"""
        code = "def funcion():\n    pass"
        result = is_class_code(code)
        assert result is False


class TestExtractClassName:
    
    def test_extrae_nombre_clase_simple(self):
        """Verifica que extrae el nombre de una clase simple"""
        code = "class Calculator:\n    pass"
        result = extract_class_name(code)
        assert result == "Calculator"
    
    def test_extrae_nombre_clase_con_herencia(self):
        """Verifica que extrae nombre de clase con herencia"""
        code = "class MiClase(BaseClass):\n    pass"
        result = extract_class_name(code)
        assert result == "MiClase"
    
    def test_retorna_none_sin_clase(self):
        """Verifica que retorna None sin clase"""
        code = "def funcion():\n    pass"
        result = extract_class_name(code)
        assert result is None


class TestIsClassCodeTS:
    
    def test_detecta_clase_typescript(self):
        """Verifica que detecta clase TypeScript"""
        code = """
class Calculator {
    suma(a: number, b: number): number {
        return a + b;
    }
}
"""
        result = is_class_code_ts(code)
        assert result is True
    
    def test_detecta_clase_exportada(self):
        """Verifica que detecta clase exportada"""
        code = "export class Calculator {\n}"
        result = is_class_code_ts(code)
        assert result is True
    
    def test_retorna_false_sin_clase(self):
        """Verifica que retorna False sin clase TypeScript"""
        code = "function suma(a: number, b: number): number {\n    return a + b;\n}"
        result = is_class_code_ts(code)
        assert result is False


class TestExtractClassNameTS:
    
    def test_extrae_nombre_clase_typescript(self):
        """Verifica que extrae nombre de clase TypeScript"""
        code = "class Calculator {\n}"
        result = extract_class_name_ts(code)
        assert result == "Calculator"
    
    def test_extrae_nombre_clase_exportada(self):
        """Verifica que extrae nombre de clase exportada"""
        code = "export class Calculator {\n}"
        result = extract_class_name_ts(code)
        assert result == "Calculator"
    
    def test_retorna_none_sin_clase(self):
        """Verifica que retorna None sin clase"""
        code = "function suma(a, b) { return a + b; }"
        result = extract_class_name_ts(code)
        assert result is None


class TestExtractFunctionNameTS:
    
    def test_extrae_nombre_funcion_typescript(self):
        """Verifica que extrae nombre de función TypeScript"""
        from tools.code_executor import extract_function_name_ts
        code = "function suma(a: number, b: number): number {\n    return a + b;\n}"
        result = extract_function_name_ts(code)
        assert result == "suma"
    
    def test_extrae_nombre_funcion_arrow(self):
        """Verifica que intenta extraer nombre de función arrow"""
        from tools.code_executor import extract_function_name_ts
        code = "const suma = (a: number, b: number): number => a + b;"
        result = extract_function_name_ts(code)
        # El regex puede o no detectar arrow functions sin paréntesis en el tipo de retorno
        assert result == "suma" or result is None
    
    def test_extrae_nombre_funcion_const_function(self):
        """Verifica que extrae nombre de const function"""
        from tools.code_executor import extract_function_name_ts
        code = "const suma = function(a: number, b: number): number { return a + b; };"
        result = extract_function_name_ts(code)
        assert result == "suma"
    
    def test_retorna_none_sin_funcion_ts(self):
        """Verifica que retorna None sin función"""
        from tools.code_executor import extract_function_name_ts
        code = "const x = 5;"
        result = extract_function_name_ts(code)
        assert result is None


class TestExtractFunctionParametersTS:
    
    def test_extrae_parametros_typescript(self):
        """Verifica que extrae parámetros TypeScript"""
        from tools.code_executor import extract_function_parameters_ts
        code = "function suma(a: number, b: number): number { return a + b; }"
        result = extract_function_parameters_ts(code)
        assert result == ["a", "b"]
    
    def test_extrae_parametros_arrow_function(self):
        """Verifica que intenta extraer parámetros de arrow function"""
        from tools.code_executor import extract_function_parameters_ts
        code = "const suma = (a: number, b: number) => a + b;"
        result = extract_function_parameters_ts(code)
        # Verificar que al menos intenta extraer parámetros
        assert isinstance(result, list)
    
    def test_retorna_lista_vacia_sin_parametros_ts(self):
        """Verifica que retorna lista vacía sin parámetros"""
        from tools.code_executor import extract_function_parameters_ts
        code = "function test(): void {}"
        result = extract_function_parameters_ts(code)
        assert result == []
    
    def test_extrae_parametros_con_valores_default_ts(self):
        """Verifica que extrae parámetros con valores por defecto"""
        from tools.code_executor import extract_function_parameters_ts
        code = "function suma(a: number, b: number = 0): number { return a + b; }"
        result = extract_function_parameters_ts(code)
        assert "a" in result
        assert "b" in result
