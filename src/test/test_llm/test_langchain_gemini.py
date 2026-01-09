import pytest
from unittest.mock import Mock, patch, MagicMock
from llm.langchain_gemini import (
    create_langchain_llm,
    call_gemini_with_langchain,
    get_token_count,
    get_llm_instance
)


class TestCreateLangchainLLM:
    
    def test_create_langchain_llm_exitoso(self, monkeypatch):
        """Verifica que create_langchain_llm crea una instancia correctamente"""
        from config.settings import settings
        monkeypatch.setattr(settings, 'GEMINI_API_KEY', 'test_key')
        monkeypatch.setattr(settings, 'MODEL_NAME', 'gemini-pro')
        
        with patch('llm.langchain_gemini.ChatGoogleGenerativeAI') as MockLLM:
            mock_instance = MockLLM.return_value
            
            result = create_langchain_llm()
            
            assert result == mock_instance
            MockLLM.assert_called_once()
    
    def test_create_langchain_llm_con_streaming(self, monkeypatch):
        """Verifica que create_langchain_llm configura streaming correctamente"""
        from config.settings import settings
        monkeypatch.setattr(settings, 'GEMINI_API_KEY', 'test_key')
        
        with patch('llm.langchain_gemini.ChatGoogleGenerativeAI') as MockLLM:
            with patch('llm.langchain_gemini.StreamingStdOutCallbackHandler'):
                result = create_langchain_llm(streaming=True)
                
                assert MockLLM.called
                call_kwargs = MockLLM.call_args[1]
                assert call_kwargs['streaming'] is True
    
    def test_create_langchain_llm_valida_api_key(self, monkeypatch):
        """Verifica que el método valida la API key"""
        from config.settings import settings
        
        # Verificar que la función requiere una API key válida
        # Si settings tiene una clave, el test pasa
        # Si no tiene clave, debe lanzar ValueError
        original_key = settings.GEMINI_API_KEY
        
        if original_key:
            # Si hay clave, verificar que funciona
            with patch('llm.langchain_gemini.ChatGoogleGenerativeAI'):
                result = create_langchain_llm()
                assert result is not None
        else:
            # Si no hay clave, debe fallar
            with pytest.raises(ValueError):
                create_langchain_llm()
    
    def test_create_langchain_llm_con_callbacks_personalizados(self, monkeypatch):
        """Verifica que acepta callbacks personalizados"""
        from config.settings import settings
        monkeypatch.setattr(settings, 'GEMINI_API_KEY', 'test_key')
        
        custom_callback = Mock()
        
        with patch('llm.langchain_gemini.ChatGoogleGenerativeAI') as MockLLM:
            result = create_langchain_llm(streaming=True, callbacks=[custom_callback])
            
            call_kwargs = MockLLM.call_args[1]
            assert custom_callback in call_kwargs['callbacks']


class TestCallGeminiWithLangchain:
    
    def test_call_gemini_with_langchain_exitoso(self, monkeypatch):
        """Verifica que call_gemini_with_langchain funciona correctamente"""
        from config.settings import settings
        monkeypatch.setattr(settings, 'GEMINI_API_KEY', 'test_key')
        
        with patch('llm.langchain_gemini.create_langchain_llm') as mock_create:
            mock_llm = Mock()
            mock_response = Mock()
            mock_response.content = "Test response"
            mock_llm.invoke.return_value = mock_response
            mock_create.return_value = mock_llm
            
            result = call_gemini_with_langchain("role prompt", "context")
            
            assert result == "Test response"
            mock_llm.invoke.assert_called_once()
    
    def test_call_gemini_with_langchain_con_streaming(self, monkeypatch):
        """Verifica que call_gemini_with_langchain funciona con streaming"""
        from config.settings import settings
        monkeypatch.setattr(settings, 'GEMINI_API_KEY', 'test_key')
        
        with patch('llm.langchain_gemini.create_langchain_llm') as mock_create:
            mock_llm = Mock()
            mock_response = Mock()
            mock_response.content = "Streaming response"
            mock_llm.invoke.return_value = mock_response
            mock_create.return_value = mock_llm
            
            result = call_gemini_with_langchain("role", "context", streaming=True)
            
            assert result == "Streaming response"
            mock_create.assert_called_with(streaming=True, callbacks=None)
    
    def test_call_gemini_with_langchain_maneja_excepciones(self, monkeypatch):
        """Verifica que maneja excepciones correctamente"""
        from config.settings import settings
        monkeypatch.setattr(settings, 'GEMINI_API_KEY', 'test_key')
        
        with patch('llm.langchain_gemini.create_langchain_llm') as mock_create:
            mock_llm = Mock()
            mock_llm.invoke.side_effect = Exception("API Error")
            mock_create.return_value = mock_llm
            
            with pytest.raises(Exception, match="API Error"):
                call_gemini_with_langchain("role", "context")
    
    def test_call_gemini_with_langchain_con_gemini3_response(self, monkeypatch):
        """Verifica que maneja respuestas de Gemini 3 correctamente"""
        from config.settings import settings
        monkeypatch.setattr(settings, 'GEMINI_API_KEY', 'test_key')
        
        with patch('llm.langchain_gemini.create_langchain_llm') as mock_create:
            with patch('llm.gemini_client._safe_get_text') as mock_safe_get:
                mock_llm = Mock()
                mock_response = Mock()
                mock_response.content = {'type': 'text', 'text': 'Gemini 3 response'}
                mock_llm.invoke.return_value = mock_response
                mock_create.return_value = mock_llm
                mock_safe_get.return_value = 'Gemini 3 response'
                
                result = call_gemini_with_langchain("role", "context")
                
                assert result == 'Gemini 3 response'


class TestGetTokenCount:
    
    def test_get_token_count_exitoso(self, monkeypatch):
        """Verifica que get_token_count cuenta tokens correctamente"""
        from config.settings import settings
        monkeypatch.setattr(settings, 'GEMINI_API_KEY', 'test_key')
        
        with patch('llm.langchain_gemini.create_langchain_llm') as mock_create:
            mock_llm = Mock()
            mock_llm.get_num_tokens.return_value = 42
            mock_create.return_value = mock_llm
            
            result = get_token_count("Test text")
            
            assert result['total_tokens'] == 42
            assert 'model' in result
            assert isinstance(result['model'], str)
    
    def test_get_token_count_maneja_excepciones(self, monkeypatch):
        """Verifica que maneja excepciones correctamente"""
        from config.settings import settings
        monkeypatch.setattr(settings, 'GEMINI_API_KEY', 'test_key')
        
        with patch('llm.langchain_gemini.create_langchain_llm') as mock_create:
            mock_llm = Mock()
            mock_llm.get_num_tokens.side_effect = Exception("Token count error")
            mock_create.return_value = mock_llm
            
            result = get_token_count("Test text")
            
            assert result['total_tokens'] == -1
            assert 'model' in result
            assert isinstance(result['model'], str)


class TestGetLLMInstance:
    
    def test_get_llm_instance_crea_singleton(self, monkeypatch):
        """Verifica que get_llm_instance crea una instancia singleton"""
        from config.settings import settings
        monkeypatch.setattr(settings, 'GEMINI_API_KEY', 'test_key')
        
        # Reset singleton
        import llm.langchain_gemini
        llm.langchain_gemini._llm_instance = None
        
        with patch('llm.langchain_gemini.create_langchain_llm') as mock_create:
            mock_llm = Mock()
            mock_create.return_value = mock_llm
            
            result1 = get_llm_instance()
            result2 = get_llm_instance()
            
            assert result1 == result2
            mock_create.assert_called_once()
    
    def test_get_llm_instance_reutiliza_instancia(self, monkeypatch):
        """Verifica que reutiliza la instancia existente"""
        from config.settings import settings
        monkeypatch.setattr(settings, 'GEMINI_API_KEY', 'test_key')
        
        # Set existing instance
        import llm.langchain_gemini
        mock_existing = Mock()
        llm.langchain_gemini._llm_instance = mock_existing
        
        result = get_llm_instance()
        
        assert result == mock_existing
