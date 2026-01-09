import pytest
from models.state import AgentState


class TestAgentState:
    
    def test_agent_state_estructura_basica(self):
        """Verifica que AgentState tenga todos los campos requeridos"""
        state: AgentState = {
            'prompt_inicial': 'Test prompt',
            'max_attempts': 3,
            'attempt_count': 0,
            'debug_attempt_count': 0,
            'max_debug_attempts': 2,
            'feedback_stakeholder': '',
            'requisito_clarificado': '',
            'requisitos_formales': '{}',
            'codigo_generado': '',
            'azure_pbi_id': None,
            'azure_implementation_task_id': None,
            'azure_testing_task_id': None,
            'traceback': '',
            'pruebas_superadas': False,
            'sonarqube_issues': '',
            'sonarqube_passed': False,
            'sonarqube_attempt_count': 0,
            'max_sonarqube_attempts': 2,
            'tests_unitarios_generados': '',
            'github_branch_name': None,
            'github_pr_number': None,
            'github_pr_url': None,
            'codigo_revisado': False,
            'revision_comentario': '',
            'revision_puntuacion': None,
            'pr_aprobada': False,
            'revisor_attempt_count': 0,
            'max_revisor_attempts': 2,
            'validado': False
        }
        
        assert state['prompt_inicial'] == 'Test prompt'
        assert state['max_attempts'] == 3
        assert state['validado'] is False
    
    def test_agent_state_con_azure_devops(self):
        """Verifica que se puedan asignar IDs de Azure DevOps"""
        state: AgentState = {
            'prompt_inicial': 'Test',
            'max_attempts': 3,
            'attempt_count': 0,
            'debug_attempt_count': 0,
            'max_debug_attempts': 2,
            'feedback_stakeholder': '',
            'requisito_clarificado': '',
            'requisitos_formales': '{}',
            'codigo_generado': '',
            'azure_pbi_id': 12345,
            'azure_implementation_task_id': 67890,
            'azure_testing_task_id': 11111,
            'traceback': '',
            'pruebas_superadas': False,
            'sonarqube_issues': '',
            'sonarqube_passed': False,
            'sonarqube_attempt_count': 0,
            'max_sonarqube_attempts': 2,
            'tests_unitarios_generados': '',
            'github_branch_name': None,
            'github_pr_number': None,
            'github_pr_url': None,
            'codigo_revisado': False,
            'revision_comentario': '',
            'revision_puntuacion': None,
            'pr_aprobada': False,
            'revisor_attempt_count': 0,
            'max_revisor_attempts': 2,
            'validado': False
        }
        
        assert state['azure_pbi_id'] == 12345
        assert state['azure_implementation_task_id'] == 67890
        assert state['azure_testing_task_id'] == 11111
    
    def test_agent_state_con_github(self):
        """Verifica que se puedan asignar datos de GitHub"""
        state: AgentState = {
            'prompt_inicial': 'Test',
            'max_attempts': 3,
            'attempt_count': 0,
            'debug_attempt_count': 0,
            'max_debug_attempts': 2,
            'feedback_stakeholder': '',
            'requisito_clarificado': '',
            'requisitos_formales': '{}',
            'codigo_generado': '',
            'azure_pbi_id': None,
            'azure_implementation_task_id': None,
            'azure_testing_task_id': None,
            'traceback': '',
            'pruebas_superadas': False,
            'sonarqube_issues': '',
            'sonarqube_passed': False,
            'sonarqube_attempt_count': 0,
            'max_sonarqube_attempts': 2,
            'tests_unitarios_generados': '',
            'github_branch_name': 'feature/test-123',
            'github_pr_number': 456,
            'github_pr_url': 'https://github.com/test/pr/456',
            'codigo_revisado': True,
            'revision_comentario': 'LGTM',
            'revision_puntuacion': 9,
            'pr_aprobada': True,
            'revisor_attempt_count': 0,
            'max_revisor_attempts': 2,
            'validado': False
        }
        
        assert state['github_branch_name'] == 'feature/test-123'
        assert state['github_pr_number'] == 456
        assert state['github_pr_url'] == 'https://github.com/test/pr/456'
        assert state['codigo_revisado'] is True
        assert state['pr_aprobada'] is True
    
    def test_agent_state_contadores_intentos(self):
        """Verifica que los contadores de intentos funcionen correctamente"""
        state: AgentState = {
            'prompt_inicial': 'Test',
            'max_attempts': 3,
            'attempt_count': 2,
            'debug_attempt_count': 1,
            'max_debug_attempts': 2,
            'feedback_stakeholder': '',
            'requisito_clarificado': '',
            'requisitos_formales': '{}',
            'codigo_generado': '',
            'azure_pbi_id': None,
            'azure_implementation_task_id': None,
            'azure_testing_task_id': None,
            'traceback': '',
            'pruebas_superadas': False,
            'sonarqube_issues': '',
            'sonarqube_passed': False,
            'sonarqube_attempt_count': 1,
            'max_sonarqube_attempts': 2,
            'tests_unitarios_generados': '',
            'github_branch_name': None,
            'github_pr_number': None,
            'github_pr_url': None,
            'codigo_revisado': False,
            'revision_comentario': '',
            'revision_puntuacion': None,
            'pr_aprobada': False,
            'revisor_attempt_count': 1,
            'max_revisor_attempts': 2,
            'validado': False
        }
        
        assert state['attempt_count'] == 2
        assert state['debug_attempt_count'] == 1
        assert state['sonarqube_attempt_count'] == 1
        assert state['revisor_attempt_count'] == 1
    
    def test_agent_state_sonarqube_fields(self):
        """Verifica que los campos de SonarQube funcionen correctamente"""
        state: AgentState = {
            'prompt_inicial': 'Test',
            'max_attempts': 3,
            'attempt_count': 0,
            'debug_attempt_count': 0,
            'max_debug_attempts': 2,
            'feedback_stakeholder': '',
            'requisito_clarificado': '',
            'requisitos_formales': '{}',
            'codigo_generado': '',
            'azure_pbi_id': None,
            'azure_implementation_task_id': None,
            'azure_testing_task_id': None,
            'traceback': '',
            'pruebas_superadas': False,
            'sonarqube_issues': 'BLOCKER: Security issue found',
            'sonarqube_passed': False,
            'sonarqube_attempt_count': 1,
            'max_sonarqube_attempts': 2,
            'tests_unitarios_generados': '',
            'github_branch_name': None,
            'github_pr_number': None,
            'github_pr_url': None,
            'codigo_revisado': False,
            'revision_comentario': '',
            'revision_puntuacion': None,
            'pr_aprobada': False,
            'revisor_attempt_count': 0,
            'max_revisor_attempts': 2,
            'validado': False
        }
        
        assert state['sonarqube_issues'] == 'BLOCKER: Security issue found'
        assert state['sonarqube_passed'] is False
        assert state['sonarqube_attempt_count'] == 1
    
    def test_agent_state_validacion_completa(self):
        """Verifica un estado completamente validado"""
        state: AgentState = {
            'prompt_inicial': 'Test',
            'max_attempts': 3,
            'attempt_count': 1,
            'debug_attempt_count': 0,
            'max_debug_attempts': 2,
            'feedback_stakeholder': 'Aprobado',
            'requisito_clarificado': 'Requisito claro',
            'requisitos_formales': '{"objetivo": "test"}',
            'codigo_generado': 'def test(): pass',
            'azure_pbi_id': 123,
            'azure_implementation_task_id': 456,
            'azure_testing_task_id': 789,
            'traceback': '',
            'pruebas_superadas': True,
            'sonarqube_issues': '',
            'sonarqube_passed': True,
            'sonarqube_attempt_count': 0,
            'max_sonarqube_attempts': 2,
            'tests_unitarios_generados': 'def test_example(): assert True',
            'github_branch_name': 'feature/test',
            'github_pr_number': 1,
            'github_pr_url': 'https://github.com/test/pr/1',
            'codigo_revisado': True,
            'revision_comentario': 'Excelente',
            'revision_puntuacion': 10,
            'pr_aprobada': True,
            'revisor_attempt_count': 0,
            'max_revisor_attempts': 2,
            'validado': True
        }
        
        assert state['validado'] is True
        assert state['pruebas_superadas'] is True
        assert state['sonarqube_passed'] is True
        assert state['pr_aprobada'] is True
        assert state['codigo_revisado'] is True
