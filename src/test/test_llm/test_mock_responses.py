import pytest
from llm.mock_responses import get_mock_response


class TestGetMockResponse:
    
    def test_get_mock_response_para_release_notes(self):
        """Verifica que retorna respuesta para release notes"""
        prompt = "Genera una release note para el siguiente código"
        response = get_mock_response(prompt)
        
        assert isinstance(response, str)
        assert len(response) > 100
        assert "Release Note" in response or "release note" in response.lower()
    
    def test_get_mock_response_para_generador_tests_typescript(self):
        """Verifica que retorna tests TypeScript"""
        prompt = """Rol:
Ingeniero de TDD
Generar tests unitarios para TypeScript
Nombre del archivo de código: calculator.ts"""
        response = get_mock_response(prompt)
        
        assert isinstance(response, str)
        assert "import" in response
        assert "describe" in response or "test" in response
    
    def test_get_mock_response_para_generador_tests_python(self):
        """Verifica que retorna tests Python"""
        prompt = """Rol:
Ingeniero de TDD
Generar tests unitarios para Python
Nombre del archivo de código: calculator.py"""
        response = get_mock_response(prompt)
        
        assert isinstance(response, str)
        assert "def test_" in response or "import pytest" in response
    
    def test_get_mock_response_para_product_owner(self):
        """Verifica que retorna respuesta para product owner"""
        prompt = "Eres un Product Owner. Analiza los siguientes requisitos"
        response = get_mock_response(prompt)
        
        assert isinstance(response, str)
        assert len(response) > 50
    
    def test_get_mock_response_para_desarrollador(self):
        """Verifica que retorna código para desarrollador"""
        prompt = "Eres un desarrollador. Implementa una función de suma"
        response = get_mock_response(prompt)
        
        assert isinstance(response, str)
        assert len(response) > 50
    
    def test_get_mock_response_para_sonarqube(self):
        """Verifica que retorna análisis de SonarQube"""
        prompt = "Analiza la calidad del código con SonarQube"
        response = get_mock_response(prompt)
        
        assert isinstance(response, str)
        assert len(response) > 50
    
    def test_get_mock_response_para_stakeholder(self):
        """Verifica que retorna validación de stakeholder"""
        prompt = "Eres un stakeholder. Valida el siguiente código"
        response = get_mock_response(prompt)
        
        assert isinstance(response, str)
        assert len(response) > 50
    
    def test_get_mock_response_con_context_vacio(self):
        """Verifica que funciona con context vacío"""
        prompt = "Test prompt"
        response = get_mock_response(prompt, context="")
        
        assert isinstance(response, str)
    
    def test_get_mock_response_retorna_string(self):
        """Verifica que siempre retorna un string"""
        prompt = "Any prompt"
        response = get_mock_response(prompt)
        
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_get_mock_response_detecta_calculator_class(self):
        """Verifica que detecta clases Calculator"""
        prompt = """Rol:
Ingeniero de TDD
Generar tests para Calculator class en TypeScript
Nombre del archivo de código: calculator.ts"""
        response = get_mock_response(prompt)
        
        assert "Calculator" in response or "calculator" in response.lower()
    
    def test_get_mock_response_maneja_prompt_largo(self):
        """Verifica que maneja prompts largos"""
        prompt = "A" * 1000 + " Genera release notes"
        response = get_mock_response(prompt)
        
        assert isinstance(response, str)
        assert len(response) > 0
