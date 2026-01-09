import pytest
import os
from unittest.mock import Mock, patch, MagicMock, mock_open
from models.state import AgentState
from agents.sonar import sonar_node


class TestSonarNode:
    
    def test_sonar_omite_analisis_cuando_deshabilitado(self, mock_state, mock_file_utils, mock_settings):
        result = sonar_node(mock_state)
        
        assert result['sonarqube_passed'] is True
        assert result['sonarqube_issues'] == ""
        assert result['sonarqube_attempt_count'] == 0
    
    def test_sonar_aprueba_codigo_sin_issues_criticos(self, mock_state, mock_file_utils, monkeypatch):
        from config.settings import settings
        monkeypatch.setattr(settings, 'SONARSCANNER_ENABLED', True)
        monkeypatch.setattr(settings, 'OUTPUT_DIR', '/tmp/test')
        
        mock_state['codigo_generado'] = 'def suma(a, b): return a + b'
        
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data='def suma(a, b): return a + b')):
                with patch('agents.sonar.analizar_codigo_con_sonarqube') as mock_analizar:
                    mock_analizar.return_value = {
                        'success': True,
                        'summary': {
                            'total_issues': 2,
                            'by_severity': {'BLOCKER': 0, 'CRITICAL': 1, 'MAJOR': 1},
                            'by_type': {'BUG': 0, 'CODE_SMELL': 2}
                        },
                        'issues': []
                    }
                    
                    with patch('agents.sonar.formatear_reporte_sonarqube', return_value='Reporte OK'):
                        with patch('agents.sonar.es_codigo_aceptable', return_value=True):
                            with patch('agents.sonar.guardar_fichero_texto'):
                                result = sonar_node(mock_state)
                                
                                assert result['sonarqube_passed'] is True
                                assert result['sonarqube_issues'] == ""
                                assert result['sonarqube_attempt_count'] == 0
    
    def test_sonar_rechaza_codigo_con_blockers(self, mock_state, mock_file_utils, monkeypatch):
        from config.settings import settings
        monkeypatch.setattr(settings, 'SONARSCANNER_ENABLED', True)
        monkeypatch.setattr(settings, 'OUTPUT_DIR', '/tmp/test')
        
        mock_state['codigo_generado'] = 'def test(): pass'
        
        with patch('agents.sonar.call_gemini') as mock_gemini:
            mock_gemini.return_value = 'Instrucciones de corrección'
            with patch('os.path.exists', return_value=True):
                with patch('builtins.open', mock_open(read_data='def test(): pass')):
                    with patch('agents.sonar.analizar_codigo_con_sonarqube') as mock_analizar:
                        mock_analizar.return_value = {
                            'success': True,
                            'summary': {
                                'total_issues': 5,
                                'by_severity': {'BLOCKER': 2, 'CRITICAL': 3},
                                'by_type': {'BUG': 2, 'CODE_SMELL': 3}
                            },
                            'issues': []
                        }
                        
                        with patch('agents.sonar.formatear_reporte_sonarqube', return_value='Reporte con errores'):
                            with patch('agents.sonar.es_codigo_aceptable', return_value=False):
                                with patch('agents.sonar.guardar_fichero_texto'):
                                    result = sonar_node(mock_state)
                                    
                                    assert result['sonarqube_passed'] is False
                                    assert result['sonarqube_issues'] != ""
                                    assert result['sonarqube_attempt_count'] == 1
    
    def test_sonar_incrementa_contador_en_rechazo(self, mock_state, mock_file_utils, monkeypatch):
        from config.settings import settings
        monkeypatch.setattr(settings, 'SONARSCANNER_ENABLED', True)
        monkeypatch.setattr(settings, 'OUTPUT_DIR', '/tmp/test')
        
        mock_state['sonarqube_attempt_count'] = 0
        
        with patch('agents.sonar.call_gemini') as mock_gemini:
            mock_gemini.return_value = 'Corregir issues'
            with patch('os.path.exists', return_value=True):
                with patch('builtins.open', mock_open(read_data='code')):
                    with patch('agents.sonar.analizar_codigo_con_sonarqube') as mock_analizar:
                        mock_analizar.return_value = {
                            'success': True,
                            'summary': {
                                'total_issues': 3,
                                'by_severity': {'BLOCKER': 1, 'CRITICAL': 2},
                                'by_type': {'BUG': 1, 'CODE_SMELL': 2}
                            },
                            'issues': []
                        }
                        
                        with patch('agents.sonar.formatear_reporte_sonarqube', return_value='Reporte'):
                            with patch('agents.sonar.es_codigo_aceptable', return_value=False):
                                with patch('agents.sonar.guardar_fichero_texto'):
                                    result = sonar_node(mock_state)
                                    
                                    assert result['sonarqube_attempt_count'] == 1
    
    def test_sonar_actualiza_azure_task_in_progress(self, mock_state, mock_file_utils, monkeypatch):
        from config.settings import settings
        monkeypatch.setattr(settings, 'AZURE_DEVOPS_ENABLED', True)
        monkeypatch.setattr(settings, 'SONARSCANNER_ENABLED', True)
        monkeypatch.setattr(settings, 'OUTPUT_DIR', '/tmp/test')
        
        mock_state['azure_implementation_task_id'] = 456
        mock_state['sonarqube_attempt_count'] = 0
        
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data='code')):
                with patch('agents.sonar.analizar_codigo_con_sonarqube') as mock_analizar:
                    mock_analizar.return_value = {
                        'success': True,
                        'summary': {
                            'total_issues': 0,
                            'by_severity': {'BLOCKER': 0, 'CRITICAL': 0},
                            'by_type': {'BUG': 0}
                        },
                        'issues': []
                    }
                    
                    with patch('agents.sonar.formatear_reporte_sonarqube', return_value='OK'):
                        with patch('agents.sonar.es_codigo_aceptable', return_value=True):
                            with patch('agents.sonar.guardar_fichero_texto'):
                                with patch('agents.sonar.azure_service') as mock_azure:
                                    mock_azure.update_implementation_task_to_in_progress.return_value = True
                                    
                                    sonar_node(mock_state)
                                    
                                    mock_azure.update_implementation_task_to_in_progress.assert_called_once_with(456)
    
    def test_sonar_agrega_comentario_aprobacion_azure(self, mock_state, mock_file_utils, monkeypatch):
        from config.settings import settings
        monkeypatch.setattr(settings, 'AZURE_DEVOPS_ENABLED', True)
        monkeypatch.setattr(settings, 'SONARSCANNER_ENABLED', True)
        monkeypatch.setattr(settings, 'OUTPUT_DIR', '/tmp/test')
        
        mock_state['azure_implementation_task_id'] = 456
        
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data='code')):
                with patch('agents.sonar.analizar_codigo_con_sonarqube') as mock_analizar:
                    mock_analizar.return_value = {
                        'success': True,
                        'summary': {
                            'total_issues': 0,
                            'by_severity': {'BLOCKER': 0, 'CRITICAL': 0},
                            'by_type': {'BUG': 0}
                        },
                        'issues': []
                    }
                    
                    with patch('agents.sonar.formatear_reporte_sonarqube', return_value='OK'):
                        with patch('agents.sonar.es_codigo_aceptable', return_value=True):
                            with patch('agents.sonar.guardar_fichero_texto'):
                                with patch('agents.sonar.azure_service') as mock_azure:
                                    sonar_node(mock_state)
                                    
                                    mock_azure.add_sonarqube_approval_comment.assert_called_once()
    
    def test_sonar_usa_sonarcloud_con_branch(self, mock_state, mock_file_utils, monkeypatch):
        from config.settings import settings
        monkeypatch.setattr(settings, 'SONARCLOUD_ENABLED', True)
        monkeypatch.setattr(settings, 'OUTPUT_DIR', '/tmp/test')
        
        mock_state['github_branch_name'] = 'test-branch'
        
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data='code')):
                with patch('agents.sonar.analizar_codigo_con_sonarqube') as mock_analizar:
                    mock_analizar.return_value = {
                        'success': True,
                        'summary': {
                            'total_issues': 0,
                            'by_severity': {'BLOCKER': 0, 'CRITICAL': 0},
                            'by_type': {'BUG': 0}
                        },
                        'issues': []
                    }
                    
                    with patch('agents.sonar.formatear_reporte_sonarqube', return_value='OK'):
                        with patch('agents.sonar.es_codigo_aceptable', return_value=True):
                            with patch('agents.sonar.guardar_fichero_texto'):
                                result = sonar_node(mock_state)
                                
                                assert result['sonarqube_passed'] is True
    
    def test_sonar_fallback_analisis_local_sin_branch(self, mock_state, mock_file_utils, monkeypatch):
        from config.settings import settings
        monkeypatch.setattr(settings, 'SONARCLOUD_ENABLED', True)
        monkeypatch.setattr(settings, 'OUTPUT_DIR', '/tmp/test')
        
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data='code')):
                with patch('agents.sonar.analizar_codigo_con_sonarqube') as mock_analizar:
                    mock_analizar.return_value = {
                        'success': True,
                        'summary': {
                            'total_issues': 0,
                            'by_severity': {'BLOCKER': 0, 'CRITICAL': 0},
                            'by_type': {'BUG': 0}
                        },
                        'issues': []
                    }
                    
                    with patch('agents.sonar.formatear_reporte_sonarqube', return_value='OK'):
                        with patch('agents.sonar.es_codigo_aceptable', return_value=True):
                            with patch('agents.sonar.guardar_fichero_texto'):
                                result = sonar_node(mock_state)
                                
                                mock_analizar.assert_called_once()
                                assert result['sonarqube_passed'] is True
    
    def test_sonar_guarda_reporte_siempre(self, mock_state, monkeypatch):
        from config.settings import settings
        monkeypatch.setattr(settings, 'SONARSCANNER_ENABLED', True)
        monkeypatch.setattr(settings, 'OUTPUT_DIR', '/tmp/test')
        
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data='code')):
                with patch('agents.sonar.analizar_codigo_con_sonarqube') as mock_analizar:
                    mock_analizar.return_value = {
                        'success': True,
                        'summary': {
                            'total_issues': 0,
                            'by_severity': {'BLOCKER': 0, 'CRITICAL': 0},
                            'by_type': {'BUG': 0}
                        },
                        'issues': []
                    }
                    
                    with patch('agents.sonar.formatear_reporte_sonarqube', return_value='Reporte'):
                        with patch('agents.sonar.es_codigo_aceptable', return_value=True):
                            with patch('agents.sonar.guardar_fichero_texto') as mock_guardar:
                                sonar_node(mock_state)
                                
                                assert mock_guardar.call_count >= 1
                                filename = mock_guardar.call_args_list[0][0][0]
                                assert 'sonar_report' in filename
