import pytest
import logging
from unittest.mock import Mock, patch
from utils.agent_decorators import agent_execution_context


class TestAgentExecutionContext:
    
    @pytest.fixture
    def mock_logger(self):
        """Fixture que retorna un logger mockeado"""
        return Mock(spec=logging.Logger)
    
    def test_agent_execution_context_logs_inicio_y_fin(self, mock_logger):
        """Verifica que el context manager logea inicio y fin"""
        with agent_execution_context("TEST_AGENT", mock_logger):
            pass
        
        # Verificar que se llamó info al menos 6 veces (3 para inicio, 3 para fin)
        assert mock_logger.info.call_count >= 6
    
    def test_agent_execution_context_logs_nombre_agente(self, mock_logger):
        """Verifica que el context manager incluye el nombre del agente"""
        agent_name = "💻 DESARROLLADOR"
        
        with agent_execution_context(agent_name, mock_logger):
            pass
        
        # Verificar que se logeó el nombre del agente
        calls = [str(call) for call in mock_logger.info.call_args_list]
        assert any(agent_name in str(call) for call in calls)
    
    def test_agent_execution_context_logs_separadores(self, mock_logger):
        """Verifica que el context manager logea separadores"""
        with agent_execution_context("TEST", mock_logger):
            pass
        
        # Verificar que se logearon separadores (líneas de =)
        calls = [call[0][0] for call in mock_logger.info.call_args_list]
        separadores = [call for call in calls if '=' in str(call)]
        assert len(separadores) >= 4  # Al menos 4 separadores
    
    def test_agent_execution_context_ejecuta_codigo_interno(self, mock_logger):
        """Verifica que el context manager ejecuta el código interno"""
        ejecutado = False
        
        with agent_execution_context("TEST", mock_logger):
            ejecutado = True
        
        assert ejecutado is True
    
    def test_agent_execution_context_maneja_excepciones(self, mock_logger):
        """Verifica que el context manager maneja excepciones y logea fin"""
        with pytest.raises(ValueError):
            with agent_execution_context("TEST", mock_logger):
                raise ValueError("Test error")
        
        # Verificar que se logeó el fin incluso con excepción
        calls = [call[0][0] for call in mock_logger.info.call_args_list]
        assert any("FIN" in str(call) for call in calls)
    
    def test_agent_execution_context_con_emoji(self, mock_logger):
        """Verifica que funciona con emojis en el nombre"""
        agent_name = "🔍 SONARQUBE"
        
        with agent_execution_context(agent_name, mock_logger):
            pass
        
        # Verificar que se procesó correctamente
        assert mock_logger.info.called
    
    def test_agent_execution_context_imprime_linea_blanco(self, mock_logger):
        """Verifica que imprime una línea en blanco al inicio"""
        with patch('builtins.print') as mock_print:
            with agent_execution_context("TEST", mock_logger):
                pass
            
            # Verificar que se llamó print() para la línea en blanco
            mock_print.assert_called()
    
    def test_agent_execution_context_formato_consistente(self, mock_logger):
        """Verifica que el formato es consistente"""
        with agent_execution_context("TEST_AGENT", mock_logger):
            pass
        
        calls = [call[0][0] for call in mock_logger.info.call_args_list]
        
        # Verificar que hay mensajes de INICIO y FIN
        mensajes_inicio = [call for call in calls if "INICIO" in str(call)]
        mensajes_fin = [call for call in calls if "FIN" in str(call)]
        
        assert len(mensajes_inicio) >= 1
        assert len(mensajes_fin) >= 1
