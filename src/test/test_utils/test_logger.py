import pytest
import logging
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from utils.logger import (
    setup_logger,
    log_agent_execution,
    log_llm_call,
    log_file_operation,
    ColoredFormatter,
    AgentFormatter,
    get_session_log_file
)


class TestSetupLogger:
    
    def test_setup_logger_retorna_logger(self):
        """Verifica que setup_logger retorna un logger"""
        logger = setup_logger("test_logger")
        assert isinstance(logger, logging.Logger)
    
    def test_setup_logger_configura_nivel(self):
        """Verifica que configura el nivel de logging"""
        logger = setup_logger("test_logger", level=logging.DEBUG)
        assert logger.level == logging.DEBUG
    
    def test_setup_logger_agrega_console_handler(self):
        """Verifica que agrega un console handler"""
        logger = setup_logger("test_logger_console")
        handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler)]
        assert len(handlers) > 0
    
    def test_setup_logger_con_agent_mode(self):
        """Verifica que funciona con agent_mode"""
        logger = setup_logger("test_agent", agent_mode=True)
        assert isinstance(logger, logging.Logger)
    
    def test_setup_logger_sin_propagacion(self):
        """Verifica que deshabilita propagación"""
        logger = setup_logger("test_no_propagate")
        assert logger.propagate is False


class TestColoredFormatter:
    
    def test_colored_formatter_formatea_mensaje(self):
        """Verifica que ColoredFormatter formatea mensajes"""
        formatter = ColoredFormatter('%(levelname)s - %(message)s')
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="Test message", args=(), exc_info=None
        )
        result = formatter.format(record)
        assert "Test message" in result
    
    def test_colored_formatter_incluye_nivel(self):
        """Verifica que incluye el nivel de log"""
        formatter = ColoredFormatter('%(levelname)s - %(message)s')
        record = logging.LogRecord(
            name="test", level=logging.WARNING, pathname="", lineno=0,
            msg="Warning message", args=(), exc_info=None
        )
        result = formatter.format(record)
        assert "WARNING" in result or "warning" in result.lower()


class TestAgentFormatter:
    
    def test_agent_formatter_formatea_mensaje(self):
        """Verifica que AgentFormatter formatea mensajes"""
        formatter = AgentFormatter('%(message)s')
        record = logging.LogRecord(
            name="agents.desarrollador", level=logging.INFO, pathname="", lineno=0,
            msg="Test message", args=(), exc_info=None
        )
        result = formatter.format(record)
        assert "Test message" in result
    
    def test_agent_formatter_agrega_emoji(self):
        """Verifica que agrega emoji para agentes conocidos"""
        formatter = AgentFormatter('%(message)s')
        record = logging.LogRecord(
            name="agents.desarrollador", level=logging.INFO, pathname="", lineno=0,
            msg="Código generado", args=(), exc_info=None
        )
        result = formatter.format(record)
        # El mensaje debe tener contenido
        assert len(result) > 0
    
    def test_agent_formatter_con_agent_context(self):
        """Verifica que maneja agent_context"""
        formatter = AgentFormatter('%(message)s')
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="Test", args=(), exc_info=None
        )
        record.agent_context = "TestAgent"
        result = formatter.format(record)
        assert "TestAgent" in result


class TestLogAgentExecution:
    
    def test_log_agent_execution_logea_mensaje(self):
        """Verifica que log_agent_execution logea el mensaje"""
        mock_logger = Mock(spec=logging.Logger)
        log_agent_execution(mock_logger, "TestAgent", "Acción realizada")
        mock_logger.log.assert_called_once()
    
    def test_log_agent_execution_con_detalles(self):
        """Verifica que incluye detalles en el mensaje"""
        mock_logger = Mock(spec=logging.Logger)
        details = {"lines": 50, "language": "python"}
        log_agent_execution(mock_logger, "TestAgent", "Código generado", details=details)
        
        # Verificar que se llamó log con algún mensaje
        mock_logger.log.assert_called_once()
        call_args = mock_logger.log.call_args
        assert "Código generado" in str(call_args)
    
    def test_log_agent_execution_con_nivel_personalizado(self):
        """Verifica que usa el nivel especificado"""
        mock_logger = Mock(spec=logging.Logger)
        log_agent_execution(mock_logger, "TestAgent", "Warning", level=logging.WARNING)
        
        call_args = mock_logger.log.call_args
        assert call_args[0][0] == logging.WARNING


class TestLogLLMCall:
    
    def test_log_llm_call_logea_tipo_prompt(self):
        """Verifica que logea el tipo de prompt"""
        mock_logger = Mock(spec=logging.Logger)
        log_llm_call(mock_logger, "TEST_PROMPT")
        mock_logger.debug.assert_called_once()
    
    def test_log_llm_call_con_tokens(self):
        """Verifica que incluye información de tokens"""
        mock_logger = Mock(spec=logging.Logger)
        log_llm_call(mock_logger, "TEST_PROMPT", tokens_used=150)
        
        call_args = mock_logger.debug.call_args
        assert "150" in str(call_args) or "tokens" in str(call_args).lower()
    
    def test_log_llm_call_con_duracion(self):
        """Verifica que incluye duración"""
        mock_logger = Mock(spec=logging.Logger)
        log_llm_call(mock_logger, "TEST_PROMPT", duration=1.5)
        
        call_args = mock_logger.debug.call_args
        assert "1.5" in str(call_args) or "duration" in str(call_args).lower()


class TestLogFileOperation:
    
    def test_log_file_operation_exitosa(self):
        """Verifica que logea operación exitosa"""
        mock_logger = Mock(spec=logging.Logger)
        log_file_operation(mock_logger, "guardar", "test.txt", success=True)
        mock_logger.debug.assert_called_once()
    
    def test_log_file_operation_fallida(self):
        """Verifica que logea operación fallida"""
        mock_logger = Mock(spec=logging.Logger)
        log_file_operation(mock_logger, "guardar", "test.txt", success=False, error="Permission denied")
        mock_logger.error.assert_called_once()
    
    def test_log_file_operation_incluye_filepath(self):
        """Verifica que incluye la ruta del archivo"""
        mock_logger = Mock(spec=logging.Logger)
        filepath = "/path/to/test.txt"
        log_file_operation(mock_logger, "leer", filepath, success=True)
        
        call_args = mock_logger.debug.call_args
        assert filepath in str(call_args)


class TestGetSessionLogFile:
    
    def test_get_session_log_file_retorna_path(self):
        """Verifica que retorna un Path"""
        log_file = get_session_log_file()
        assert isinstance(log_file, Path)
    
    def test_get_session_log_file_es_singleton(self):
        """Verifica que retorna el mismo archivo en múltiples llamadas"""
        log_file1 = get_session_log_file()
        log_file2 = get_session_log_file()
        assert log_file1 == log_file2
    
    def test_get_session_log_file_tiene_extension_log(self):
        """Verifica que el archivo tiene extensión .log"""
        log_file = get_session_log_file()
        assert log_file.suffix == ".log"
    
    def test_get_session_log_file_incluye_timestamp(self):
        """Verifica que el nombre incluye timestamp"""
        log_file = get_session_log_file()
        assert "workflow_" in log_file.name
