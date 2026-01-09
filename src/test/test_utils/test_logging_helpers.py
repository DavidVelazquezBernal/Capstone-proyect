import pytest
import logging
from unittest.mock import Mock
from utils.logging_helpers import log_section


class TestLogSection:
    
    @pytest.fixture
    def mock_logger(self):
        """Fixture que retorna un logger mockeado"""
        return Mock(spec=logging.Logger)
    
    def test_log_section_logea_titulo(self, mock_logger):
        """Verifica que log_section logea el título"""
        log_section(mock_logger, "TEST SECTION")
        
        # Verificar que se llamó info
        assert mock_logger.info.called
        
        # Verificar que el título está en alguna de las llamadas
        calls = [str(call) for call in mock_logger.info.call_args_list]
        assert any("TEST SECTION" in str(call) for call in calls)
    
    def test_log_section_logea_separadores(self, mock_logger):
        """Verifica que logea separadores"""
        log_section(mock_logger, "TEST")
        
        # Debe haber al menos 3 llamadas (separador, título, separador)
        assert mock_logger.info.call_count >= 3
    
    def test_log_section_con_nivel_debug(self, mock_logger):
        """Verifica que funciona con nivel debug"""
        log_section(mock_logger, "DEBUG SECTION", level="debug")
        
        assert mock_logger.debug.called
    
    def test_log_section_con_nivel_warning(self, mock_logger):
        """Verifica que funciona con nivel warning"""
        log_section(mock_logger, "WARNING SECTION", level="warning")
        
        assert mock_logger.warning.called
    
    def test_log_section_con_nivel_error(self, mock_logger):
        """Verifica que funciona con nivel error"""
        log_section(mock_logger, "ERROR SECTION", level="error")
        
        assert mock_logger.error.called
    
    def test_log_section_con_nivel_critical(self, mock_logger):
        """Verifica que funciona con nivel critical"""
        log_section(mock_logger, "CRITICAL SECTION", level="critical")
        
        assert mock_logger.critical.called
    
    def test_log_section_con_separador_personalizado(self, mock_logger):
        """Verifica que usa carácter de separador personalizado"""
        log_section(mock_logger, "TEST", separator_char="-")
        
        # Verificar que se usó el separador personalizado
        calls = [call[0][0] for call in mock_logger.info.call_args_list]
        separadores = [call for call in calls if isinstance(call, str) and "-" in call]
        assert len(separadores) >= 2
    
    def test_log_section_con_longitud_personalizada(self, mock_logger):
        """Verifica que usa longitud de separador personalizada"""
        separator_length = 40
        log_section(mock_logger, "TEST", separator_length=separator_length)
        
        # Verificar que hay separadores con la longitud correcta
        calls = [call[0][0] for call in mock_logger.info.call_args_list]
        separadores = [call for call in calls if isinstance(call, str) and "=" in call and len(call) == separator_length]
        assert len(separadores) >= 2
    
    def test_log_section_formato_consistente(self, mock_logger):
        """Verifica que el formato es consistente"""
        title = "CONSISTENT FORMAT TEST"
        log_section(mock_logger, title)
        
        # Debe haber exactamente 3 llamadas
        assert mock_logger.info.call_count == 3
        
        # Verificar orden: separador, título, separador
        calls = [call[0][0] for call in mock_logger.info.call_args_list]
        assert "=" in calls[0]  # Primer separador
        assert title in calls[1]  # Título
        assert "=" in calls[2]  # Segundo separador
    
    def test_log_section_con_titulo_vacio(self, mock_logger):
        """Verifica que maneja título vacío"""
        log_section(mock_logger, "")
        
        # Debe seguir logeando separadores
        assert mock_logger.info.call_count >= 2
    
    def test_log_section_con_titulo_largo(self, mock_logger):
        """Verifica que maneja títulos largos"""
        long_title = "A" * 100
        log_section(mock_logger, long_title)
        
        # Verificar que se logeó el título completo
        calls = [call[0][0] for call in mock_logger.info.call_args_list]
        assert any(long_title in str(call) for call in calls)
    
    def test_log_section_con_caracteres_especiales(self, mock_logger):
        """Verifica que maneja caracteres especiales en el título"""
        title = "TEST 🚀 SECTION ✅"
        log_section(mock_logger, title)
        
        # Verificar que se logeó correctamente
        calls = [call[0][0] for call in mock_logger.info.call_args_list]
        assert any(title in str(call) for call in calls)
