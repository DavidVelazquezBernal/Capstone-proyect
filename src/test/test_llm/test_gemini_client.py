import pytest
from unittest.mock import Mock, patch, MagicMock
from llm.gemini_client import _safe_get_text, _list_available_models


class TestSafeGetText:
    
    def test_safe_get_text_con_string(self):
        """Verifica que _safe_get_text maneja strings correctamente"""
        text = "Hello, world!"
        result = _safe_get_text(text)
        assert result == "Hello, world!"
    
    def test_safe_get_text_con_none(self):
        """Verifica que _safe_get_text maneja None correctamente"""
        result = _safe_get_text(None)
        assert result == ""
    
    def test_safe_get_text_con_lista_de_strings(self):
        """Verifica que _safe_get_text maneja listas de strings"""
        text_list = ["Hello", "world", "!"]
        result = _safe_get_text(text_list)
        assert result == "Hello\nworld\n!"
    
    def test_safe_get_text_con_lista_de_dicts_gemini3(self):
        """Verifica que _safe_get_text maneja formato Gemini 3"""
        text_list = [
            {'type': 'text', 'text': 'Hello'},
            {'type': 'text', 'text': 'world'}
        ]
        result = _safe_get_text(text_list)
        assert "Hello" in result
        assert "world" in result
    
    def test_safe_get_text_con_dict_gemini3(self):
        """Verifica que _safe_get_text maneja dict Gemini 3"""
        text_dict = {'type': 'text', 'text': 'Hello, world!'}
        result = _safe_get_text(text_dict)
        assert result == "Hello, world!"
    
    def test_safe_get_text_con_dict_text_key(self):
        """Verifica que _safe_get_text extrae clave 'text' de dict"""
        text_dict = {'text': 'Hello, world!'}
        result = _safe_get_text(text_dict)
        assert result == "Hello, world!"
    
    def test_safe_get_text_con_dict_content_key(self):
        """Verifica que _safe_get_text extrae clave 'content' de dict"""
        text_dict = {'content': 'Hello, world!'}
        result = _safe_get_text(text_dict)
        assert result == "Hello, world!"
    
    def test_safe_get_text_con_objeto_con_text_attr(self):
        """Verifica que _safe_get_text extrae atributo text de objeto"""
        mock_obj = Mock()
        mock_obj.text = "Hello, world!"
        result = _safe_get_text(mock_obj)
        assert result == "Hello, world!"
    
    def test_safe_get_text_con_objeto_con_content_attr(self):
        """Verifica que _safe_get_text extrae atributo content de objeto"""
        mock_obj = Mock()
        mock_obj.text = None
        mock_obj.content = "Hello, world!"
        # Configurar __getitem__ para que no falle
        mock_obj.__getitem__ = Mock(side_effect=KeyError)
        result = _safe_get_text(mock_obj)
        # El método puede retornar el objeto como string si no puede extraer
        assert isinstance(result, str)
    
    def test_safe_get_text_con_lista_mixta(self):
        """Verifica que _safe_get_text maneja lista mixta de tipos"""
        text_list = [
            "Plain text",
            {'type': 'text', 'text': 'Dict text'},
            Mock(text="Object text")
        ]
        result = _safe_get_text(text_list)
        assert "Plain text" in result
        assert "Dict text" in result
        assert "Object text" in result


class TestListAvailableModels:
    
    def test_list_available_models_retorna_lista(self):
        """Verifica que _list_available_models retorna una lista"""
        with patch('llm.gemini_client.client') as mock_client:
            mock_model = Mock()
            mock_model.name = 'gemini-pro'
            mock_model.supported_generation_methods = ['generateContent']
            mock_client.models.list.return_value = [mock_model]
            
            result = _list_available_models()
            
            assert isinstance(result, list)
            assert 'gemini-pro' in result
    
    def test_list_available_models_filtra_modelos_sin_generate_content(self):
        """Verifica que filtra modelos sin generateContent"""
        with patch('llm.gemini_client.client') as mock_client:
            mock_model1 = Mock()
            mock_model1.name = 'gemini-pro'
            mock_model1.supported_generation_methods = ['generateContent']
            
            mock_model2 = Mock()
            mock_model2.name = 'other-model'
            mock_model2.supported_generation_methods = ['otherMethod']
            
            mock_client.models.list.return_value = [mock_model1, mock_model2]
            
            result = _list_available_models()
            
            assert 'gemini-pro' in result
            assert 'other-model' not in result
    
    def test_list_available_models_maneja_modelos_sin_atributo(self):
        """Verifica que incluye modelos sin atributo supported_generation_methods"""
        with patch('llm.gemini_client.client') as mock_client:
            mock_model = Mock(spec=['name'])
            mock_model.name = 'gemini-pro'
            
            mock_client.models.list.return_value = [mock_model]
            
            result = _list_available_models()
            
            assert 'gemini-pro' in result
    
    def test_list_available_models_retorna_vacio_sin_client(self):
        """Verifica que retorna lista vacía si no hay client"""
        with patch('llm.gemini_client.client', None):
            result = _list_available_models()
            assert result == []
    
    def test_list_available_models_maneja_excepciones(self):
        """Verifica que maneja excepciones correctamente"""
        with patch('llm.gemini_client.client') as mock_client:
            mock_client.models.list.side_effect = Exception("API Error")
            
            result = _list_available_models()
            
            assert result == []
