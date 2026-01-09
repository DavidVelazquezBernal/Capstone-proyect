import pytest
from utils.code_validator import (
    validate_code_completeness,
    validate_test_code_completeness,
    _validate_typescript_code,
    _validate_python_code,
    _validate_generic_code,
    _strip_ts_strings_and_comments
)


class TestValidateCodeCompleteness:
    
    def test_valida_codigo_python_valido(self):
        """Verifica que valida código Python válido"""
        codigo = """
def suma(a, b):
    return a + b

def resta(a, b):
    return a - b
"""
        es_valido, mensaje = validate_code_completeness(codigo, "python")
        assert es_valido is True
        assert mensaje == ""
    
    def test_rechaza_codigo_muy_corto(self):
        """Verifica que rechaza código muy corto"""
        codigo = "def f(): pass"
        es_valido, mensaje = validate_code_completeness(codigo, "python", min_length=50)
        assert es_valido is False
        assert "corto" in mensaje.lower()
    
    def test_valida_codigo_typescript_valido(self):
        """Verifica que valida código TypeScript válido"""
        codigo = """
function suma(a: number, b: number): number {
    return a + b;
}

export { suma };
"""
        es_valido, mensaje = validate_code_completeness(codigo, "typescript")
        assert es_valido is True
        assert mensaje == ""
    
    def test_rechaza_typescript_con_llaves_desbalanceadas(self):
        """Verifica que rechaza TypeScript con llaves desbalanceadas"""
        codigo = """
function suma(a: number, b: number): number {
    return a + b;

"""
        es_valido, mensaje = validate_code_completeness(codigo, "typescript")
        assert es_valido is False
        assert "llaves" in mensaje.lower() or "desbalance" in mensaje.lower()
    
    def test_valida_codigo_con_tests_python(self):
        """Verifica que valida código Python con tests"""
        codigo = """
def test_suma():
    assert suma(1, 2) == 3

def test_resta():
    assert resta(5, 3) == 2
"""
        es_valido, mensaje = validate_code_completeness(codigo, "python", require_test_functions=True)
        assert es_valido is True
    
    def test_rechaza_python_sin_tests_cuando_requerido(self):
        """Verifica que rechaza Python sin tests cuando se requieren"""
        codigo = """
def suma(a, b):
    return a + b

def resta(a, b):
    return a - b

def multiplicar(a, b):
    return a * b
"""
        es_valido, mensaje = validate_code_completeness(codigo, "python", require_test_functions=True)
        assert es_valido is False
        assert "test_" in mensaje.lower() or "test" in mensaje.lower()
    
    def test_valida_codigo_javascript(self):
        """Verifica que valida código JavaScript"""
        codigo = """
function suma(a, b) {
    return a + b;
}

function resta(a, b) {
    return a - b;
}

function multiplicar(a, b) {
    return a * b;
}
"""
        es_valido, mensaje = validate_code_completeness(codigo, "javascript")
        assert es_valido is True


class TestValidatePythonCode:
    
    def test_valida_python_con_funcion(self):
        """Verifica que valida Python con función"""
        codigo = """
def calcular_factorial(n):
    if n <= 1:
        return 1
    return n * calcular_factorial(n - 1)
"""
        es_valido, mensaje = _validate_python_code(codigo, require_test_functions=False)
        assert es_valido is True
    
    def test_valida_python_con_clase(self):
        """Verifica que valida Python con clase"""
        codigo = """
class Calculator:
    def suma(self, a, b):
        return a + b
"""
        es_valido, mensaje = _validate_python_code(codigo, require_test_functions=False)
        assert es_valido is True
    
    def test_rechaza_python_sin_definiciones(self):
        """Verifica que rechaza Python sin definiciones"""
        codigo = """
x = 5
y = 10
print(x + y)
"""
        es_valido, mensaje = _validate_python_code(codigo, require_test_functions=False)
        assert es_valido is False
        assert "función" in mensaje.lower() or "clase" in mensaje.lower()
    
    def test_valida_python_con_test_functions(self):
        """Verifica que valida Python con funciones test_*"""
        codigo = """
def test_suma():
    assert 1 + 1 == 2

def test_resta():
    assert 5 - 3 == 2
"""
        es_valido, mensaje = _validate_python_code(codigo, require_test_functions=True)
        assert es_valido is True


class TestValidateTypescriptCode:
    
    def test_valida_typescript_basico(self):
        """Verifica que valida TypeScript básico"""
        codigo = """
function suma(a: number, b: number): number {
    return a + b;
}
"""
        es_valido, mensaje = _validate_typescript_code(codigo, require_test_functions=False)
        assert es_valido is True
    
    def test_rechaza_parentesis_desbalanceados(self):
        """Verifica que rechaza paréntesis desbalanceados"""
        codigo = """
function suma(a: number, b: number {
    return a + b;
}
"""
        es_valido, mensaje = _validate_typescript_code(codigo, require_test_functions=False)
        assert es_valido is False
        assert "paréntesis" in mensaje.lower() or "parentesis" in mensaje.lower()
    
    def test_rechaza_corchetes_desbalanceados(self):
        """Verifica que rechaza corchetes desbalanceados"""
        codigo = """
const array = [1, 2, 3;
"""
        es_valido, mensaje = _validate_typescript_code(codigo, require_test_functions=False)
        assert es_valido is False
        assert "corchete" in mensaje.lower()
    
    def test_valida_typescript_con_tests(self):
        """Verifica que valida TypeScript con tests"""
        codigo = """
describe('Calculator', () => {
    test('suma correctamente', () => {
        expect(suma(1, 2)).toBe(3);
    });
});
"""
        es_valido, mensaje = _validate_typescript_code(codigo, require_test_functions=True)
        assert es_valido is True
    
    def test_rechaza_typescript_sin_tests_cuando_requerido(self):
        """Verifica que rechaza TypeScript sin tests cuando se requieren"""
        codigo = """
function suma(a: number, b: number): number {
    return a + b;
}
"""
        es_valido, mensaje = _validate_typescript_code(codigo, require_test_functions=True)
        assert es_valido is False
        assert "describe" in mensaje.lower() or "test" in mensaje.lower()


class TestValidateGenericCode:
    
    def test_valida_codigo_generico_valido(self):
        """Verifica que valida código genérico con contenido"""
        codigo = """
line 1
line 2
line 3
line 4
"""
        es_valido, mensaje = _validate_generic_code(codigo)
        assert es_valido is True
    
    def test_rechaza_codigo_con_pocas_lineas(self):
        """Verifica que rechaza código con muy pocas líneas"""
        codigo = "line 1\nline 2"
        es_valido, mensaje = _validate_generic_code(codigo)
        assert es_valido is False
        assert "pocas líneas" in mensaje.lower() or "pocas lineas" in mensaje.lower()


class TestStripTsStringsAndComments:
    
    def test_elimina_comentarios_linea(self):
        """Verifica que elimina comentarios de línea"""
        codigo = """
function suma(a, b) { // comentario
    return a + b;
}
"""
        resultado = _strip_ts_strings_and_comments(codigo)
        assert "//" not in resultado or "comentario" not in resultado
    
    def test_elimina_comentarios_multilinea(self):
        """Verifica que elimina comentarios multilínea"""
        codigo = """
/* Este es un
   comentario multilínea */
function suma(a, b) {
    return a + b;
}
"""
        resultado = _strip_ts_strings_and_comments(codigo)
        assert "comentario multilínea" not in resultado
    
    def test_elimina_strings_dobles(self):
        """Verifica que elimina strings con comillas dobles"""
        codigo = 'const mensaje = "Hola mundo";'
        resultado = _strip_ts_strings_and_comments(codigo)
        assert "Hola mundo" not in resultado
    
    def test_elimina_strings_simples(self):
        """Verifica que elimina strings con comillas simples"""
        codigo = "const mensaje = 'Hola mundo';"
        resultado = _strip_ts_strings_and_comments(codigo)
        assert "Hola mundo" not in resultado
    
    def test_mantiene_estructura_codigo(self):
        """Verifica que mantiene la estructura del código"""
        codigo = """
function suma(a, b) {
    return a + b;
}
"""
        resultado = _strip_ts_strings_and_comments(codigo)
        assert "{" in resultado
        assert "}" in resultado
        assert "function" in resultado


class TestValidateTestCodeCompleteness:
    
    def test_valida_tests_python(self):
        """Verifica que valida tests Python"""
        codigo = """
def test_suma():
    assert suma(1, 2) == 3

def test_resta():
    assert resta(5, 3) == 2
"""
        es_valido, mensaje = validate_test_code_completeness(codigo, "python")
        assert es_valido is True
    
    def test_valida_tests_typescript(self):
        """Verifica que valida tests TypeScript"""
        codigo = """
describe('Calculator', () => {
    test('suma', () => {
        expect(suma(1, 2)).toBe(3);
    });
});
"""
        es_valido, mensaje = validate_test_code_completeness(codigo, "typescript")
        assert es_valido is True
    
    def test_rechaza_codigo_sin_tests(self):
        """Verifica que rechaza código sin tests"""
        codigo = """
def suma(a, b):
    return a + b
"""
        es_valido, mensaje = validate_test_code_completeness(codigo, "python")
        assert es_valido is False
