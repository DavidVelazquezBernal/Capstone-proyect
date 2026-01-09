import sys
import os
import pytest
from unittest.mock import Mock, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def mock_state():
    return {
        'prompt_inicial': 'Test prompt',
        'requisitos_formales': '{"objetivo_funcional": "Test"}',
        'codigo_generado': 'def test(): pass',
        'tests_unitarios_generados': 'def test_example(): assert True',
        'traceback': '',
        'feedback_stakeholder': '',
        'attempt_count': 0,
        'debug_attempt_count': 0,
        'sonarqube_attempt_count': 0,
        'max_attempts': 3,
        'max_sonarqube_attempts': 2,
        'validado': False,
        'pruebas_superadas': False,
        'sonarqube_passed': False,
        'sonarqube_issues': '',
        'azure_pbi_id': None,
        'azure_implementation_task_id': None,
        'azure_testing_task_id': None,
        'github_branch_name': None,
        'github_pr_number': None,
        'github_pr_url': None,
        'codigo_revisado': False,
        'revision_comentario': '',
        'pr_aprobada': False,
        'pr_mergeada': False
    }

@pytest.fixture
def mock_gemini_client(monkeypatch):
    mock_call = Mock(return_value='{"objetivo_funcional": "Test response"}')
    monkeypatch.setattr('llm.gemini_client.call_gemini', mock_call)
    return mock_call

@pytest.fixture
def mock_azure_service(monkeypatch):
    mock_service = MagicMock()
    mock_service.create_pbi_from_requirements.return_value = None
    mock_service.create_implementation_tasks.return_value = (None, None)
    mock_service.update_implementation_task_to_in_progress.return_value = True
    mock_service.update_testing_task_to_in_progress.return_value = True
    monkeypatch.setattr('services.azure_devops_service.azure_service', mock_service)
    return mock_service

@pytest.fixture
def mock_github_service(monkeypatch):
    mock_service = MagicMock()
    mock_service.create_branch_and_commit.return_value = (True, 'abc123')
    mock_service.sanitize_branch_name.return_value = 'test-branch'
    mock_service.create_pull_request.return_value = (123, 'https://github.com/test/pr/123')
    mock_service.approve_pull_request.return_value = True
    mock_service.merge_pull_request.return_value = True
    monkeypatch.setattr('services.github_service.github_service', mock_service)
    return mock_service

@pytest.fixture
def mock_file_utils(monkeypatch):
    monkeypatch.setattr('tools.file_utils.guardar_fichero_texto', Mock(return_value=True))
    monkeypatch.setattr('tools.file_utils.detectar_lenguaje_y_extension', Mock(return_value=('python', '.py', None)))
    monkeypatch.setattr('tools.file_utils.limpiar_codigo_markdown', Mock(side_effect=lambda x: x))
    monkeypatch.setattr('tools.file_utils.extraer_nombre_archivo', Mock(return_value='test_file'))

@pytest.fixture
def mock_settings(monkeypatch):
    from config.settings import settings
    monkeypatch.setattr(settings, 'AZURE_DEVOPS_ENABLED', False)
    monkeypatch.setattr(settings, 'GITHUB_ENABLED', False)
    monkeypatch.setattr(settings, 'SONARCLOUD_ENABLED', False)
    monkeypatch.setattr(settings, 'SONARSCANNER_ENABLED', False)
    monkeypatch.setattr(settings, 'OUTPUT_DIR', '/tmp/test_output')
    return settings
