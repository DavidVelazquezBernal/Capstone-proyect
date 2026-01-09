import pytest
from unittest.mock import Mock, patch
from config.prompt_templates import PromptTemplates, get_prompt_template


class TestPromptTemplates:
    
    def test_format_product_owner_sin_feedback(self):
        """Verifica que format_product_owner funciona sin feedback"""
        prompt_inicial = "Crear una función de suma"
        
        result = PromptTemplates.format_product_owner(prompt_inicial)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "suma" in result.lower()
    
    def test_format_product_owner_con_feedback(self):
        """Verifica que format_product_owner funciona con feedback"""
        prompt_inicial = "Crear una función de suma"
        feedback = "Agregar validación de tipos"
        
        result = PromptTemplates.format_product_owner(prompt_inicial, feedback)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "suma" in result.lower()
        assert "validación" in result.lower() or "validacion" in result.lower()
    
    def test_format_developer_sin_contexto(self):
        """Verifica que format_developer funciona sin contexto adicional"""
        requisitos = '{"objetivo": "Crear función de suma"}'
        
        result = PromptTemplates.format_developer(requisitos)
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_format_developer_con_contexto(self):
        """Verifica que format_developer funciona con contexto adicional"""
        requisitos = '{"objetivo": "Crear función de suma"}'
        contexto = "Usar TypeScript"
        
        result = PromptTemplates.format_developer(requisitos, contexto)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "typescript" in result.lower()
    
    def test_format_sonarqube_con_reporte_y_codigo(self):
        """Verifica que format_sonarqube formatea correctamente"""
        reporte = "Se encontraron 3 issues de seguridad"
        codigo = "def suma(a, b): return a + b"
        
        result = PromptTemplates.format_sonarqube(reporte, codigo)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "issues" in result.lower() or "seguridad" in result.lower()
    
    def test_format_generador_uts_sin_nombre_archivo(self):
        """Verifica que format_generador_uts funciona sin nombre de archivo"""
        codigo = "def suma(a, b): return a + b"
        requisitos = '{"objetivo": "Función de suma"}'
        lenguaje = "Python"
        
        result = PromptTemplates.format_generador_uts(codigo, requisitos, lenguaje)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "python" in result.lower()
    
    def test_format_generador_uts_con_nombre_archivo(self):
        """Verifica que format_generador_uts funciona con nombre de archivo"""
        codigo = "def suma(a, b): return a + b"
        requisitos = '{"objetivo": "Función de suma"}'
        lenguaje = "Python"
        nombre_archivo = "suma.py"
        
        result = PromptTemplates.format_generador_uts(codigo, requisitos, lenguaje, nombre_archivo)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "suma.py" in result or "python" in result.lower()
    
    def test_format_stakeholder_con_todos_parametros(self):
        """Verifica que format_stakeholder formatea correctamente"""
        requisitos = '{"objetivo": "Función de suma"}'
        codigo = "def suma(a, b): return a + b"
        resultado_tests = "All tests passed"
        
        result = PromptTemplates.format_stakeholder(requisitos, codigo, resultado_tests)
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_format_release_note_generator_con_parametros_basicos(self):
        """Verifica que format_release_note_generator funciona con parámetros básicos"""
        requisitos = '{"objetivo": "Función de suma"}'
        codigo = "def suma(a, b): return a + b"
        
        result = PromptTemplates.format_release_note_generator(requisitos, codigo)
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_format_release_note_generator_con_todos_parametros(self):
        """Verifica que format_release_note_generator funciona con todos los parámetros"""
        requisitos = '{"objetivo": "Función de suma"}'
        codigo = "def suma(a, b): return a + b"
        resultado_tests = "All tests passed"
        issues_sonarqube = "No issues found"
        
        result = PromptTemplates.format_release_note_generator(
            requisitos, codigo, resultado_tests, issues_sonarqube
        )
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_messages_to_string_convierte_lista_a_string(self):
        """Verifica que _messages_to_string convierte lista de mensajes a string"""
        messages = [
            Mock(content="Message 1"),
            Mock(content="Message 2")
        ]
        
        result = PromptTemplates._messages_to_string(messages)
        
        assert isinstance(result, str)
        assert "Message 1" in result
        assert "Message 2" in result
    
    def test_messages_to_string_con_lista_vacia(self):
        """Verifica que _messages_to_string maneja lista vacía"""
        messages = []
        
        result = PromptTemplates._messages_to_string(messages)
        
        assert isinstance(result, str)
    
    def test_get_prompt_template_retorna_template(self):
        """Verifica que get_prompt_template retorna un template"""
        result = get_prompt_template("product_owner")
        
        assert result is not None
    
    def test_format_product_owner_retorna_string_no_vacio(self):
        """Verifica que todos los métodos format retornan strings no vacíos"""
        result = PromptTemplates.format_product_owner("test")
        
        assert isinstance(result, str)
        assert len(result) > 10  # Debe tener contenido significativo
    
    def test_format_developer_retorna_string_no_vacio(self):
        """Verifica que format_developer retorna string no vacío"""
        result = PromptTemplates.format_developer("test")
        
        assert isinstance(result, str)
        assert len(result) > 10
    
    def test_format_sonarqube_retorna_string_no_vacio(self):
        """Verifica que format_sonarqube retorna string no vacío"""
        result = PromptTemplates.format_sonarqube("reporte", "codigo")
        
        assert isinstance(result, str)
        assert len(result) > 10
    
    def test_format_generador_uts_retorna_string_no_vacio(self):
        """Verifica que format_generador_uts retorna string no vacío"""
        result = PromptTemplates.format_generador_uts("codigo", "requisitos", "Python")
        
        assert isinstance(result, str)
        assert len(result) > 10
    
    def test_format_stakeholder_retorna_string_no_vacio(self):
        """Verifica que format_stakeholder retorna string no vacío"""
        result = PromptTemplates.format_stakeholder("requisitos", "codigo", "tests")
        
        assert isinstance(result, str)
        assert len(result) > 10
    
    def test_format_release_note_generator_retorna_string_no_vacio(self):
        """Verifica que format_release_note_generator retorna string no vacío"""
        result = PromptTemplates.format_release_note_generator("requisitos", "codigo")
        
        assert isinstance(result, str)
        assert len(result) > 10
