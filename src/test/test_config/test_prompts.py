import pytest
from config.prompts import Prompts


class TestPrompts:
    
    def test_product_owner_prompt_existe(self):
        """Verifica que el prompt de PRODUCT_OWNER existe y no está vacío"""
        assert hasattr(Prompts, 'PRODUCT_OWNER')
        assert isinstance(Prompts.PRODUCT_OWNER, str)
        assert len(Prompts.PRODUCT_OWNER) > 100
    
    def test_codificador_prompt_existe(self):
        """Verifica que el prompt de CODIFICADOR existe y no está vacío"""
        assert hasattr(Prompts, 'CODIFICADOR')
        assert isinstance(Prompts.CODIFICADOR, str)
        assert len(Prompts.CODIFICADOR) > 100
    
    def test_sonarqube_prompt_existe(self):
        """Verifica que el prompt de SONARQUBE existe y no está vacío"""
        assert hasattr(Prompts, 'SONARQUBE')
        assert isinstance(Prompts.SONARQUBE, str)
        assert len(Prompts.SONARQUBE) > 100
    
    def test_generador_uts_prompt_existe(self):
        """Verifica que el prompt de GENERADOR_UTS existe y no está vacío"""
        assert hasattr(Prompts, 'GENERADOR_UTS')
        assert isinstance(Prompts.GENERADOR_UTS, str)
        assert len(Prompts.GENERADOR_UTS) > 100
    
    def test_stakeholder_prompt_existe(self):
        """Verifica que el prompt de STAKEHOLDER existe y no está vacío"""
        assert hasattr(Prompts, 'STAKEHOLDER')
        assert isinstance(Prompts.STAKEHOLDER, str)
        assert len(Prompts.STAKEHOLDER) > 100
    
    def test_product_owner_contiene_instrucciones_clave(self):
        """Verifica que el prompt de PRODUCT_OWNER contiene instrucciones clave"""
        prompt = Prompts.PRODUCT_OWNER
        
        # Debe contener referencias a requisitos o análisis
        assert any(keyword in prompt.lower() for keyword in ['requisito', 'analizar', 'funcional'])
    
    def test_codificador_contiene_instrucciones_codigo(self):
        """Verifica que el prompt de CODIFICADOR contiene instrucciones sobre código"""
        prompt = Prompts.CODIFICADOR
        
        # Debe contener referencias a código o implementación
        assert any(keyword in prompt.lower() for keyword in ['código', 'codigo', 'implementa', 'función', 'funcion', 'desarrollador'])
    
    def test_sonarqube_contiene_instrucciones_calidad(self):
        """Verifica que el prompt de SONARQUBE contiene instrucciones sobre calidad"""
        prompt = Prompts.SONARQUBE
        
        # Debe contener referencias a calidad o issues
        assert any(keyword in prompt.lower() for keyword in ['calidad', 'issue', 'sonar', 'análisis', 'analisis'])
    
    def test_generador_uts_contiene_instrucciones_tests(self):
        """Verifica que el prompt de GENERADOR_UTS contiene instrucciones sobre tests"""
        prompt = Prompts.GENERADOR_UTS
        
        # Debe contener referencias a tests o pruebas
        assert any(keyword in prompt.lower() for keyword in ['test', 'prueba', 'unit', 'pytest'])
    
    def test_stakeholder_contiene_instrucciones_validacion(self):
        """Verifica que el prompt de STAKEHOLDER contiene instrucciones sobre validación"""
        prompt = Prompts.STAKEHOLDER
        
        # Debe contener referencias a validación o aprobación
        assert any(keyword in prompt.lower() for keyword in ['validar', 'aprobar', 'revisar', 'stakeholder'])
    
    def test_todos_los_prompts_son_strings(self):
        """Verifica que todos los prompts son strings"""
        prompts_attrs = [attr for attr in dir(Prompts) if not attr.startswith('_') and attr.isupper()]
        
        for attr_name in prompts_attrs:
            attr_value = getattr(Prompts, attr_name)
            assert isinstance(attr_value, str), f"{attr_name} debe ser un string"
    
    def test_todos_los_prompts_tienen_contenido_significativo(self):
        """Verifica que todos los prompts tienen contenido significativo (>50 chars)"""
        prompts_attrs = [attr for attr in dir(Prompts) if not attr.startswith('_') and attr.isupper()]
        
        for attr_name in prompts_attrs:
            attr_value = getattr(Prompts, attr_name)
            if isinstance(attr_value, str):
                assert len(attr_value) > 50, f"{attr_name} debe tener contenido significativo"
    
    def test_probador_ejecutor_menciona_herramientas_ejecucion(self):
        """Verifica que el prompt de PROBADOR_EJECUTOR_TESTS menciona herramientas de ejecución"""
        prompt = Prompts.PROBADOR_EJECUTOR_TESTS
        
        # Debe mencionar las herramientas de ejecución de código
        assert 'CodeExecutionTool' in prompt or 'herramienta' in prompt.lower()
    
    def test_codificador_menciona_lenguajes(self):
        """Verifica que el prompt de CODIFICADOR menciona lenguajes soportados"""
        prompt = Prompts.CODIFICADOR
        
        # Debe mencionar Python o TypeScript
        assert 'Python' in prompt or 'TypeScript' in prompt
    
    def test_prompts_principales_no_estan_vacios(self):
        """Verifica que los prompts principales no están vacíos"""
        prompts_principales = ['PRODUCT_OWNER', 'CODIFICADOR', 'SONARQUBE', 'GENERADOR_UTS', 'STAKEHOLDER']
        
        for attr_name in prompts_principales:
            if hasattr(Prompts, attr_name):
                attr_value = getattr(Prompts, attr_name)
                assert isinstance(attr_value, str)
                assert len(attr_value) > 50
