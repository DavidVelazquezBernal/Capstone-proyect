import pytest
from unittest.mock import Mock, patch, MagicMock
from models.state import AgentState
from agents.developer_code import developer_code_node


class TestDeveloperCodeNode:
    
    def test_developer_code_genera_codigo_exitosamente(self, mock_state, mock_file_utils, mock_settings):
        with patch('agents.developer_code.call_gemini') as mock_gemini:
            mock_gemini.return_value = 'def suma(a, b):\n    return a + b'
            
            result = developer_code_node(mock_state)
            
            assert result['codigo_generado'] == 'def suma(a, b):\n    return a + b'
            assert result['traceback'] == ""
    
    def test_developer_code_corrige_errores_traceback(self, mock_state, mock_file_utils, mock_settings):
        mock_state['traceback'] = 'NameError: name "x" is not defined'
        mock_state['codigo_generado'] = 'def test(): return x'
        
        with patch('agents.developer_code.call_gemini') as mock_gemini:
            mock_gemini.return_value = 'def test(): return 0'
            
            result = developer_code_node(mock_state)
            
            assert result['traceback'] == ""
            assert 'def test(): return 0' in result['codigo_generado']
    
    def test_developer_code_corrige_issues_sonar(self, mock_state, mock_file_utils, mock_settings):
        mock_state['sonarqube_issues'] = 'Variable no utilizada: temp'
        mock_state['codigo_generado'] = 'def test():\n    temp = 5\n    return 0'
        
        with patch('agents.developer_code.call_gemini') as mock_gemini:
            mock_gemini.return_value = 'def test():\n    return 0'
            
            result = developer_code_node(mock_state)
            
            assert result['codigo_generado'] is not None
    
    def test_developer_code_detecta_lenguaje_correctamente(self, mock_state, mock_settings):
        with patch('agents.developer_code.detectar_lenguaje_y_extension') as mock_detectar:
            mock_detectar.return_value = ('typescript', '.ts', None)
            with patch('agents.developer_code.guardar_fichero_texto', return_value=True):
                with patch('agents.developer_code.limpiar_codigo_markdown', side_effect=lambda x: x):
                    with patch('agents.developer_code.call_gemini') as mock_gemini:
                        mock_gemini.return_value = 'function suma(a, b) { return a + b; }'
                        
                        result = developer_code_node(mock_state)
                        
                        mock_detectar.assert_called_once()
    
    def test_developer_code_guarda_archivo_con_nombre_correcto(self, mock_state, mock_settings):
        mock_state['attempt_count'] = 2
        mock_state['debug_attempt_count'] = 1
        mock_state['sonarqube_attempt_count'] = 3
        
        with patch('agents.developer_code.guardar_fichero_texto') as mock_guardar:
            with patch('agents.developer_code.detectar_lenguaje_y_extension', return_value=('python', '.py', None)):
                with patch('agents.developer_code.limpiar_codigo_markdown', side_effect=lambda x: x):
                    with patch('agents.developer_code.call_gemini') as mock_gemini:
                        mock_gemini.return_value = 'def test(): pass'
                        
                        developer_code_node(mock_state)
                        
                        mock_guardar.assert_called()
                        filename = mock_guardar.call_args[0][0]
                        assert 'req2_debug1_sq3' in filename
    
    def test_developer_code_crea_tasks_azure_primera_generacion(self, mock_state, mock_file_utils, monkeypatch):
        from config.settings import settings
        monkeypatch.setattr(settings, 'AZURE_DEVOPS_ENABLED', True)
        
        mock_state['azure_pbi_id'] = 123
        mock_state['debug_attempt_count'] = 0
        mock_state['sonarqube_attempt_count'] = 0
        
        with patch('agents.developer_code.call_gemini') as mock_gemini:
            mock_gemini.return_value = 'def test(): pass'
            with patch('agents.developer_code.azure_service') as mock_azure:
                mock_azure.create_implementation_tasks.return_value = (456, 789)
                
                result = developer_code_node(mock_state)
                
                mock_azure.create_implementation_tasks.assert_called_once()
                assert result['azure_implementation_task_id'] == 456
                assert result['azure_testing_task_id'] == 789
    
    def test_developer_code_no_crea_tasks_en_correcciones(self, mock_state, mock_file_utils, monkeypatch):
        from config.settings import settings
        monkeypatch.setattr(settings, 'AZURE_DEVOPS_ENABLED', True)
        
        mock_state['azure_pbi_id'] = 123
        mock_state['debug_attempt_count'] = 1
        
        with patch('agents.developer_code.call_gemini') as mock_gemini:
            mock_gemini.return_value = 'def test(): pass'
            with patch('agents.developer_code.azure_service') as mock_azure:
                developer_code_node(mock_state)
                
                mock_azure.create_implementation_tasks.assert_not_called()
    
    def test_developer_code_crea_branch_github_cuando_habilitado(self, mock_state, mock_file_utils, monkeypatch):
        from config.settings import settings
        monkeypatch.setattr(settings, 'GITHUB_ENABLED', True)
        monkeypatch.setattr(settings, 'GITHUB_REPO_PATH', '/tmp/test_repo')
        
        with patch('agents.developer_code.call_gemini') as mock_gemini:
            mock_gemini.return_value = 'def test(): pass'
            with patch('agents.developer_code.github_service') as mock_github:
                mock_github.sanitize_branch_name.return_value = 'test-branch'
                mock_github.create_branch_and_commit.return_value = (True, 'abc123')
                
                with patch('builtins.open', MagicMock()):
                    with patch('os.makedirs'):
                        result = developer_code_node(mock_state)
                        
                        mock_github.create_branch_and_commit.assert_called_once()
                        assert result['github_branch_name'] is not None
    
    def test_developer_code_usa_prompt_template(self, mock_state, mock_file_utils, mock_settings):
        with patch('agents.developer_code.call_gemini') as mock_gemini:
            mock_gemini.return_value = 'def test(): pass'
            with patch('agents.developer_code.PromptTemplates.format_developer') as mock_template:
                mock_template.return_value = "Formatted prompt"
                
                developer_code_node(mock_state)
                
                mock_template.assert_called_once()
                assert mock_template.call_args[1]['requisitos_formales'] == mock_state['requisitos_formales']
