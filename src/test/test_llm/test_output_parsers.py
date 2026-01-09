import pytest
from unittest.mock import Mock, patch
from pydantic import BaseModel
from langchain_core.exceptions import OutputParserException
from llm.output_parsers import RobustPydanticOutputParser


class TestModel(BaseModel):
    """Modelo de prueba para testing"""
    name: str
    value: int


class TestRobustPydanticOutputParser:
    
    @pytest.fixture
    def parser(self):
        """Fixture que retorna un parser configurado"""
        return RobustPydanticOutputParser(pydantic_object=TestModel)
    
    def test_parse_json_valido(self, parser):
        """Verifica que parsea JSON válido correctamente"""
        json_text = '{"name": "test", "value": 42}'
        result = parser.parse(json_text)
        
        assert isinstance(result, TestModel)
        assert result.name == "test"
        assert result.value == 42
    
    def test_parse_json_con_markdown_json_block(self, parser):
        """Verifica que limpia bloques markdown ```json"""
        json_text = '''```json
{
    "name": "test",
    "value": 42
}
```'''
        result = parser.parse(json_text)
        
        assert isinstance(result, TestModel)
        assert result.name == "test"
        assert result.value == 42
    
    def test_parse_json_con_markdown_block_simple(self, parser):
        """Verifica que limpia bloques markdown ```"""
        json_text = '''```
{
    "name": "test",
    "value": 42
}
```'''
        result = parser.parse(json_text)
        
        assert isinstance(result, TestModel)
        assert result.name == "test"
        assert result.value == 42
    
    def test_parse_detecta_error_api(self, parser):
        """Verifica que detecta errores de API en la respuesta"""
        error_text = 'ERROR_API: Service unavailable'
        
        with pytest.raises(OutputParserException, match="error de API"):
            parser.parse(error_text)
    
    def test_parse_detecta_error_404(self, parser):
        """Verifica que detecta errores 404"""
        error_text = 'ERROR_404: Not found'
        
        with pytest.raises(OutputParserException, match="error de API"):
            parser.parse(error_text)
    
    def test_parse_detecta_error_503(self, parser):
        """Verifica que detecta errores 503"""
        error_text = 'ERROR_503: Service temporarily unavailable'
        
        with pytest.raises(OutputParserException, match="error de API"):
            parser.parse(error_text)
    
    def test_parse_detecta_error_general(self, parser):
        """Verifica que detecta errores generales"""
        error_text = 'ERROR_GENERAL: Something went wrong'
        
        with pytest.raises(OutputParserException, match="error de API"):
            parser.parse(error_text)
    
    def test_parse_json_con_texto_adicional(self, parser):
        """Verifica que extrae JSON de texto con contenido adicional"""
        json_text = '''Here is the response:
{
    "name": "test",
    "value": 42
}
That's all!'''
        
        result = parser.parse(json_text)
        
        assert isinstance(result, TestModel)
        assert result.name == "test"
        assert result.value == 42
    
    def test_parse_falla_con_json_invalido(self, parser):
        """Verifica que falla con JSON inválido después de todos los intentos"""
        invalid_json = 'This is not JSON at all'
        
        with pytest.raises(OutputParserException):
            parser.parse(invalid_json)
    
    def test_clean_markdown_blocks_con_json_block(self, parser):
        """Verifica que _clean_markdown_blocks limpia bloques json"""
        text = '```json\n{"test": "value"}\n```'
        result = parser._clean_markdown_blocks(text)
        
        assert '```' not in result
        assert '{"test": "value"}' in result
    
    def test_clean_markdown_blocks_con_block_simple(self, parser):
        """Verifica que _clean_markdown_blocks limpia bloques simples"""
        text = '```\n{"test": "value"}\n```'
        result = parser._clean_markdown_blocks(text)
        
        assert '```' not in result
        assert '{"test": "value"}' in result
    
    def test_clean_markdown_blocks_sin_bloques(self, parser):
        """Verifica que _clean_markdown_blocks retorna texto sin cambios"""
        text = '{"test": "value"}'
        result = parser._clean_markdown_blocks(text)
        
        assert result == '{"test": "value"}'
    
    def test_extract_json_encuentra_json_en_texto(self, parser):
        """Verifica que _extract_json extrae JSON del texto"""
        text = 'Some text before\n{"name": "test", "value": 42}\nSome text after'
        result = parser._extract_json(text)
        
        assert '{"name": "test", "value": 42}' in result
    
    def test_extract_json_con_json_multilinea(self, parser):
        """Verifica que _extract_json extrae JSON multilínea"""
        text = '''Some text
{
    "name": "test",
    "value": 42
}
More text'''
        result = parser._extract_json(text)
        
        assert '"name"' in result
        assert '"value"' in result
    
    def test_parse_con_espacios_extra(self, parser):
        """Verifica que parsea JSON con espacios extra"""
        json_text = '''
        
        {"name": "test", "value": 42}
        
        '''
        result = parser.parse(json_text)
        
        assert isinstance(result, TestModel)
        assert result.name == "test"
        assert result.value == 42
    
    def test_parse_intenta_multiples_estrategias(self, parser):
        """Verifica que intenta múltiples estrategias de parsing"""
        # JSON válido pero con markdown y texto extra
        json_text = '''Here's your data:
```json
{
    "name": "test",
    "value": 42
}
```
Hope this helps!'''
        
        result = parser.parse(json_text)
        
        assert isinstance(result, TestModel)
        assert result.name == "test"
        assert result.value == 42
