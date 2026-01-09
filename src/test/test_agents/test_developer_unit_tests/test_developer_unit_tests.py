import pytest
import os
from unittest.mock import Mock, patch, MagicMock, mock_open
from models.state import AgentState
from agents.developer_unit_tests import (
    developer_unit_tests_node,
    developer_complete_pr_node,
    _limpiar_ansi,
    _postprocesar_tests_typescript,
    _es_fallo_probablemente_de_tests
)


class TestDeveloperUnitTestsNode:
    
    def test_unit_tests_genera_tests_exitosamente(self, mock_state, mock_file_utils, mock_settings):
        mock_state['codigo_generado'] = 'def suma(a, b): return a + b'
        
        with patch('agents.developer_unit_tests.call_gemini') as mock_gemini:
            mock_gemini.return_value = 'def test_suma(): assert suma(1, 2) == 3'
            with patch('os.path.exists', return_value=True):
                with patch('agents.developer_unit_tests._ejecutar_tests_python') as mock_exec:
                    mock_exec.return_value = {
                        'success': True,
                        'output': 'All tests passed',
                        'traceback': '',
                        'tests_run': {'total': 1, 'passed': 1, 'failed': 0}
                    }
                    
                    result = developer_unit_tests_node(mock_state)
                    
                    assert result['tests_unitarios_generados'] is not None
                    assert result['pruebas_superadas'] is True
    
    def test_unit_tests_detecta_lenguaje_typescript(self, mock_state, mock_settings):
        mock_state['requisitos_formales'] = '{"lenguaje_programacion": "typescript"}'
        
        with patch('agents.developer_unit_tests.call_gemini') as mock_gemini:
            mock_gemini.return_value = 'describe("test", () => { it("works", () => {}); });'
            with patch('agents.developer_unit_tests.detectar_lenguaje_y_extension', return_value=('typescript', '.ts', None)):
                with patch('agents.developer_unit_tests.guardar_fichero_texto', return_value=True):
                    with patch('agents.developer_unit_tests.limpiar_codigo_markdown', side_effect=lambda x: x):
                        with patch('agents.developer_unit_tests.extraer_nombre_archivo', return_value='test'):
                            with patch('os.path.exists', return_value=True):
                                with patch('agents.developer_unit_tests._ejecutar_tests_typescript') as mock_exec:
                                    mock_exec.return_value = {
                                        'success': True,
                                        'output': 'Tests passed',
                                        'traceback': '',
                                        'tests_run': {'total': 1, 'passed': 1, 'failed': 0}
                                    }
                                    
                                    result = developer_unit_tests_node(mock_state)
                                    
                                    mock_exec.assert_called_once()
    
    def test_unit_tests_actualiza_azure_task_in_progress(self, mock_state, mock_file_utils, monkeypatch):
        from config.settings import settings
        monkeypatch.setattr(settings, 'AZURE_DEVOPS_ENABLED', True)
        
        mock_state['azure_testing_task_id'] = 789
        mock_state['debug_attempt_count'] = 0
        
        with patch('agents.developer_unit_tests.call_gemini') as mock_gemini:
            mock_gemini.return_value = 'def test_example(): pass'
            with patch('agents.developer_unit_tests.azure_service') as mock_azure:
                mock_azure.update_testing_task_to_in_progress.return_value = True
                
                with patch('os.path.exists', return_value=True):
                    with patch('agents.developer_unit_tests._ejecutar_tests_python') as mock_exec:
                        mock_exec.return_value = {
                            'success': True,
                            'output': 'OK',
                            'traceback': '',
                            'tests_run': {'total': 1, 'passed': 1, 'failed': 0}
                        }
                        
                        developer_unit_tests_node(mock_state)
                        
                        mock_azure.update_testing_task_to_in_progress.assert_called_once_with(789)
    
    def test_unit_tests_incrementa_debug_count_en_fallo(self, mock_state, mock_file_utils, mock_settings):
        with patch('agents.developer_unit_tests.call_gemini') as mock_gemini:
            mock_gemini.return_value = 'def test_example(): pass'
            with patch('os.path.exists', return_value=True):
                with patch('agents.developer_unit_tests._ejecutar_tests_python') as mock_exec:
                    mock_exec.return_value = {
                        'success': False,
                        'output': 'Test failed',
                        'traceback': 'AssertionError: expected 3 got 4',
                        'tests_run': {'total': 1, 'passed': 0, 'failed': 1}
                    }
                    
                    result = developer_unit_tests_node(mock_state)
                    
                    assert result['pruebas_superadas'] is False
                    assert result['traceback'] != ""
    
    def test_unit_tests_resetea_debug_count_en_exito(self, mock_state, mock_file_utils, mock_settings):
        mock_state['debug_attempt_count'] = 2
        
        with patch('agents.developer_unit_tests.call_gemini') as mock_gemini:
            mock_gemini.return_value = 'def test_example(): pass'
            with patch('os.path.exists', return_value=True):
                with patch('agents.developer_unit_tests._ejecutar_tests_python') as mock_exec:
                    mock_exec.return_value = {
                        'success': True,
                        'output': 'OK',
                        'traceback': '',
                        'tests_run': {'total': 1, 'passed': 1, 'failed': 0}
                    }
                    
                    result = developer_unit_tests_node(mock_state)
                    
                    assert result['debug_attempt_count'] == 0
    
    def test_unit_tests_crea_pr_en_github(self, mock_state, mock_file_utils, monkeypatch):
        from config.settings import settings
        monkeypatch.setattr(settings, 'GITHUB_ENABLED', True)
        monkeypatch.setattr(settings, 'GITHUB_REPO_PATH', '/tmp/test')
        
        mock_state['github_branch_name'] = 'test-branch'
        
        with patch('agents.developer_unit_tests.call_gemini') as mock_gemini:
            mock_gemini.return_value = 'def test_example(): pass'
            with patch('os.path.exists', return_value=True):
                with patch('os.makedirs'):
                    with patch('builtins.open', mock_open()):
                        with patch('agents.developer_unit_tests._ejecutar_tests_python') as mock_exec:
                            mock_exec.return_value = {
                                'success': True,
                                'output': 'OK',
                                'traceback': '',
                                'tests_run': {'total': 1, 'passed': 1, 'failed': 0}
                            }
                            
                            with patch('agents.developer_unit_tests.github_service') as mock_github:
                                mock_github.create_branch_and_commit.return_value = (True, 'abc123')
                                mock_github.create_pull_request.return_value = (True, 123, 'https://test.com/pr/123')
                                
                                result = developer_unit_tests_node(mock_state)
                                
                                mock_github.create_pull_request.assert_called_once()


class TestDeveloperCompletePRNode:
    
    def test_complete_pr_omite_merge_sin_github(self, mock_state, mock_file_utils, mock_settings):
        mock_state['pruebas_superadas'] = True
        mock_state['codigo_revisado'] = True
        
        result = developer_complete_pr_node(mock_state)
        
        assert result['pr_mergeada'] is True
    
    def test_complete_pr_omite_merge_sin_tests_pasados(self, mock_state, mock_file_utils, monkeypatch):
        from config.settings import settings
        monkeypatch.setattr(settings, 'GITHUB_ENABLED', True)
        
        mock_state['github_pr_number'] = 123
        mock_state['pruebas_superadas'] = False
        mock_state['codigo_revisado'] = True
        
        result = developer_complete_pr_node(mock_state)
        
        assert result['pr_mergeada'] is False
    
    def test_complete_pr_omite_merge_sin_codigo_aprobado(self, mock_state, mock_file_utils, monkeypatch):
        from config.settings import settings
        monkeypatch.setattr(settings, 'GITHUB_ENABLED', True)
        
        mock_state['github_pr_number'] = 123
        mock_state['pruebas_superadas'] = True
        mock_state['codigo_revisado'] = False
        
        result = developer_complete_pr_node(mock_state)
        
        assert result['pr_mergeada'] is False
    
    def test_complete_pr_mergea_exitosamente(self, mock_state, mock_file_utils, monkeypatch):
        from config.settings import settings
        monkeypatch.setattr(settings, 'GITHUB_ENABLED', True)
        
        mock_state['github_pr_number'] = 123
        mock_state['pruebas_superadas'] = True
        mock_state['codigo_revisado'] = True
        mock_state['github_branch_name'] = 'test-branch'
        
        with patch('agents.developer_unit_tests.github_service') as mock_github:
            mock_github.merge_pull_request.return_value = True
            
            result = developer_complete_pr_node(mock_state)
            
            assert result['pr_mergeada'] is True
            mock_github.merge_pull_request.assert_called_once()
    
    def test_complete_pr_elimina_branch_despues_merge(self, mock_state, mock_file_utils, monkeypatch):
        from config.settings import settings
        monkeypatch.setattr(settings, 'GITHUB_ENABLED', True)
        monkeypatch.setattr(settings, 'GITHUB_REPO_PATH', '/tmp/test')
        
        mock_state['github_pr_number'] = 123
        mock_state['pruebas_superadas'] = True
        mock_state['codigo_revisado'] = True
        mock_state['github_branch_name'] = 'test-branch'
        
        with patch('agents.developer_unit_tests.github_service') as mock_github:
            mock_github.merge_pull_request.return_value = True
            mock_github.sanitize_branch_name.return_value = 'test-branch'
            
            developer_complete_pr_node(mock_state)
            
            mock_github.delete_branch.assert_called_once_with('test-branch')
    
    def test_complete_pr_mock_mode_valida_precondiciones(self, mock_state, mock_file_utils, monkeypatch):
        from config.settings import settings
        monkeypatch.setattr(settings, 'LLM_MOCK_MODE', True)
        
        mock_state['pruebas_superadas'] = True
        mock_state['codigo_revisado'] = True
        
        result = developer_complete_pr_node(mock_state)
        
        assert result['pr_mergeada'] is True
        assert result['validado'] is True


class TestHelperFunctions:
    
    def test_limpiar_ansi_elimina_codigos_escape(self):
        text = '\x1b[31mError\x1b[0m'
        result = _limpiar_ansi(text)
        assert result == 'Error'
    
    def test_postprocesar_tests_typescript_ajusta_decimales(self):
        code = 'expect(result).toBe(3.14159265359);'
        result = _postprocesar_tests_typescript(code)
        assert '3.14159265359' not in result or 'toBeCloseTo' in result
    
    def test_es_fallo_probablemente_de_tests_detecta_syntax_error(self):
        output = 'SyntaxError: Unexpected token in test.spec.ts'
        is_test_fault, reason = _es_fallo_probablemente_de_tests('typescript', output, '', 'test.spec.ts')
        assert is_test_fault is True
    
    def test_es_fallo_probablemente_de_tests_no_detecta_assertion_error(self):
        output = 'AssertionError: expected 3 received 4'
        is_test_fault, reason = _es_fallo_probablemente_de_tests('typescript', output, '', 'test.spec.ts')
        assert is_test_fault is False
