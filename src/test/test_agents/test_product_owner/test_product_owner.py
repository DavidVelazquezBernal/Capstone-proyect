import pytest
from unittest.mock import Mock, patch, MagicMock
from models.state import AgentState
from agents.product_owner import product_owner_node
from models.schemas import FormalRequirements, AzureDevOpsMetadata


class TestProductOwnerNode:
    
    def test_product_owner_procesa_requisitos_exitosamente(self, mock_state, mock_gemini_client, mock_file_utils, mock_settings):
        mock_gemini_client.return_value = '''{
            "objetivo_funcional": "Crear calculadora",
            "descripcion_detallada": "Una calculadora simple",
            "criterios_aceptacion": ["Suma", "Resta"],
            "restricciones_tecnicas": ["Python 3.8+"],
            "casos_uso": ["Operaciones básicas"],
            "lenguaje_programacion": "python"
        }'''
        
        result = product_owner_node(mock_state)
        
        assert result['requisitos_formales'] is not None
        assert result['attempt_count'] == 1
        assert result['feedback_stakeholder'] == ""
        assert result['debug_attempt_count'] == 0
        assert result['sonarqube_attempt_count'] == 0
    
    def test_product_owner_incrementa_contador_intento(self, mock_state, mock_gemini_client, mock_file_utils, mock_settings):
        mock_state['attempt_count'] = 2
        mock_gemini_client.return_value = '''{
            "objetivo_funcional": "Test",
            "descripcion_detallada": "Test",
            "criterios_aceptacion": ["Test"],
            "restricciones_tecnicas": [],
            "casos_uso": [],
            "lenguaje_programacion": "python"
        }'''
        
        result = product_owner_node(mock_state)
        
        assert result['attempt_count'] == 3
    
    def test_product_owner_procesa_feedback_stakeholder(self, mock_state, mock_gemini_client, mock_file_utils, mock_settings):
        mock_state['feedback_stakeholder'] = "Necesita más funcionalidades"
        mock_gemini_client.return_value = '''{
            "objetivo_funcional": "Test mejorado",
            "descripcion_detallada": "Test",
            "criterios_aceptacion": ["Test"],
            "restricciones_tecnicas": [],
            "casos_uso": [],
            "lenguaje_programacion": "python"
        }'''
        
        result = product_owner_node(mock_state)
        
        assert result['feedback_stakeholder'] == ""
        assert result['requisitos_formales'] is not None
    
    def test_product_owner_limpia_variables_github(self, mock_state, mock_gemini_client, mock_file_utils, mock_settings):
        mock_state['github_pr_number'] = 123
        mock_state['github_pr_url'] = 'https://test.com'
        mock_state['github_branch_name'] = 'test-branch'
        mock_gemini_client.return_value = '''{
            "objetivo_funcional": "Test",
            "descripcion_detallada": "Test",
            "criterios_aceptacion": [],
            "restricciones_tecnicas": [],
            "casos_uso": [],
            "lenguaje_programacion": "python"
        }'''
        
        result = product_owner_node(mock_state)
        
        assert result['github_pr_number'] is None
        assert result['github_pr_url'] is None
        assert result['github_branch_name'] is None
    
    def test_product_owner_maneja_error_parsing(self, mock_state, mock_file_utils, mock_settings):
        with patch('agents.product_owner.call_gemini') as mock_gemini:
            mock_gemini.return_value = 'JSON inválido sin formato'
            
            result = product_owner_node(mock_state)
            
            assert 'ERROR_PARSING' in result['requisitos_formales']
    
    @patch('agents.product_owner.azure_service')
    def test_product_owner_integra_azure_devops_cuando_habilitado(self, mock_azure, mock_state, mock_gemini_client, mock_file_utils, monkeypatch):
        from config.settings import settings
        monkeypatch.setattr(settings, 'AZURE_DEVOPS_ENABLED', True)
        
        mock_azure.create_pbi_from_requirements.return_value = AzureDevOpsMetadata(
            work_item_id=123,
            work_item_url='https://dev.azure.com/test',
            work_item_type='Product Backlog Item'
        )
        
        mock_gemini_client.return_value = '''{
            "objetivo_funcional": "Test",
            "descripcion_detallada": "Test",
            "criterios_aceptacion": [],
            "restricciones_tecnicas": [],
            "casos_uso": [],
            "lenguaje_programacion": "python"
        }'''
        
        result = product_owner_node(mock_state)
        
        assert result['azure_pbi_id'] == 123
        assert 'azure_devops' in result['requisitos_formales']
    
    def test_product_owner_usa_prompt_template(self, mock_state, mock_gemini_client, mock_file_utils, mock_settings):
        with patch('agents.product_owner.PromptTemplates.format_product_owner') as mock_template:
            mock_template.return_value = "Formatted prompt"
            mock_gemini_client.return_value = '''{
                "objetivo_funcional": "Test",
                "descripcion_detallada": "Test",
                "criterios_aceptacion": [],
                "restricciones_tecnicas": [],
                "casos_uso": [],
                "lenguaje_programacion": "python"
            }'''
            
            product_owner_node(mock_state)
            
            mock_template.assert_called_once()
            assert mock_template.call_args[1]['prompt_inicial'] == mock_state['prompt_inicial']
