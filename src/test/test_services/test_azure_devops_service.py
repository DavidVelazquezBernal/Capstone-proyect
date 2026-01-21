import pytest
from unittest.mock import Mock, patch, MagicMock
from services.azure_devops_service import AzureDevOpsService


class TestAzureDevOpsService:
    
    @pytest.fixture
    def mock_settings(self, monkeypatch):
        """Mock de settings para tests"""
        from config.settings import settings
        monkeypatch.setattr(settings, 'AZURE_DEVOPS_ENABLED', True)
        return settings
    
    @pytest.fixture
    def service(self, mock_settings):
        """Fixture que retorna una instancia del servicio con cliente mockeado"""
        with patch('services.azure_devops_service.AzureDevOpsClient') as MockClient:
            mock_client = MockClient.return_value
            mock_client.test_connection.return_value = True
            service = AzureDevOpsService()
            service.client = mock_client
            service.enabled = True
            return service
    
    def test_service_inicializa_correctamente(self):
        """Verifica que el servicio se inicializa correctamente"""
        service = AzureDevOpsService()
        
        assert service is not None
        assert isinstance(service.enabled, bool)
        # El cliente puede ser None si el servicio está deshabilitado
        if service.enabled:
            assert service.client is not None
    
    def test_service_deshabilitado_cuando_settings_false(self, monkeypatch):
        """Verifica que el servicio se deshabilita cuando settings es False"""
        from config.settings import settings
        
        # Mockear settings ANTES de importar/instanciar el servicio
        with patch('services.azure_devops_service.settings') as mock_settings:
            mock_settings.AZURE_DEVOPS_ENABLED = False
            service = AzureDevOpsService()
            
            assert service.enabled is False
            assert service.client is None
    
    def test_is_enabled_retorna_true_cuando_habilitado(self, service):
        """Verifica que is_enabled retorna True cuando está habilitado"""
        assert service.is_enabled() is True
    
    def test_is_enabled_retorna_false_cuando_deshabilitado(self, monkeypatch):
        """Verifica que is_enabled retorna False cuando está deshabilitado"""
        from config.settings import settings
        
        # Mockear settings ANTES de instanciar el servicio
        with patch('services.azure_devops_service.settings') as mock_settings:
            mock_settings.AZURE_DEVOPS_ENABLED = False
            service = AzureDevOpsService()
            
            assert service.is_enabled() is False
    
    def test_create_pbi_from_requirements_retorna_none_cuando_deshabilitado(self, monkeypatch):
        """Verifica que create_pbi_from_requirements retorna None cuando está deshabilitado"""
        from config.settings import settings
        
        # Mockear settings ANTES de instanciar el servicio
        with patch('services.azure_devops_service.settings') as mock_settings:
            mock_settings.AZURE_DEVOPS_ENABLED = False
            service = AzureDevOpsService()
            requisitos = {'objetivo_funcional': 'Test'}
            
            result = service.create_pbi_from_requirements(requisitos)
            assert result is None
    
    def test_create_pbi_retorna_none_cuando_falla_conexion(self, service):
        """Verifica que retorna None cuando falla la conexión"""
        service.client.test_connection.return_value = False
        requisitos = {'objetivo_funcional': 'Test'}
        
        result = service.create_pbi_from_requirements(requisitos)
        
        assert result is None
    
    def test_update_implementation_task_to_in_progress_actualiza_correctamente(self, service):
        """Verifica que actualiza una task de implementación a In Progress"""
        service.client.update_work_item.return_value = True
        
        result = service.update_implementation_task_to_in_progress(123)
        
        assert result is True
        service.client.update_work_item.assert_called_once()
    
    def test_update_testing_task_to_in_progress_actualiza_correctamente(self, service):
        """Verifica que actualiza una task de testing a In Progress"""
        service.client.update_work_item.return_value = True
        
        result = service.update_testing_task_to_in_progress(123)
        
        assert result is True
        service.client.update_work_item.assert_called_once()
    
    def test_add_sonarqube_approval_comment_agrega_comentario(self, service):
        """Verifica que agrega un comentario de aprobación de SonarQube"""
        service.client.add_comment.return_value = True
        
        mock_state = {
            'sonarqube_issues': '',
            'codigo_generado': 'def test(): pass'
        }
        
        result = service.add_sonarqube_approval_comment(123, 'report.txt', mock_state)
        
        assert result is True
    
    def test_update_all_work_items_to_done_actualiza_todos(self, service):
        """Verifica que actualiza todos los work items a Done"""
        service.client.update_work_item.return_value = True
        
        mock_state = {
            'azure_pbi_id': 123,
            'azure_implementation_task_id': 456,
            'azure_testing_task_id': 789
        }
        
        result = service.update_all_work_items_to_done(mock_state)
        
        assert result is True
        assert service.client.update_work_item.call_count >= 1
    
    def test_generate_and_add_release_note_retorna_false_cuando_deshabilitado(self, monkeypatch):
        """Verifica que retorna False cuando está deshabilitado"""
        from config.settings import settings
        
        # Mockear settings ANTES de instanciar el servicio
        with patch('services.azure_devops_service.settings') as mock_settings:
            mock_settings.AZURE_DEVOPS_ENABLED = False
            service = AzureDevOpsService()
            mock_state = {
                'azure_pbi_id': 123,
                'requisitos_formales': '{"objetivo": "test"}',
                'codigo_generado': 'def test(): pass'
            }
            
            result = service.generate_and_add_release_note(mock_state)
            
            assert result is False
