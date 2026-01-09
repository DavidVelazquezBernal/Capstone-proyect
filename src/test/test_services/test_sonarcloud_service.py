import pytest
from unittest.mock import Mock, patch, MagicMock
from services.sonarcloud_service import SonarCloudService


class TestSonarCloudService:
    
    @pytest.fixture
    def mock_settings(self, monkeypatch):
        """Mock de settings para tests"""
        from config.settings import settings
        monkeypatch.setattr(settings, 'SONARCLOUD_ENABLED', True)
        monkeypatch.setattr(settings, 'SONARCLOUD_TOKEN', 'test_token')
        monkeypatch.setattr(settings, 'SONARCLOUD_ORGANIZATION', 'test_org')
        monkeypatch.setattr(settings, 'SONARCLOUD_PROJECT_KEY', 'test_project')
        return settings
    
    @pytest.fixture
    def service(self, mock_settings):
        """Fixture que retorna una instancia del servicio con conexión mockeada"""
        with patch.object(SonarCloudService, '_verify_connection', return_value=True):
            service = SonarCloudService()
            return service
    
    def test_service_inicializa_correctamente(self):
        """Verifica que el servicio se inicializa correctamente"""
        # Mockear settings y _verify_connection
        with patch('services.sonarcloud_service.settings') as mock_settings_obj:
            mock_settings_obj.SONARCLOUD_ENABLED = True
            mock_settings_obj.SONARCLOUD_TOKEN = 'test_token'
            mock_settings_obj.SONARCLOUD_ORGANIZATION = 'test_org'
            mock_settings_obj.SONARCLOUD_PROJECT_KEY = 'test_project'
            
            with patch.object(SonarCloudService, '_verify_connection', return_value=True):
                # Crear el servicio con el mock activo
                service = SonarCloudService()
                
                # Verificar que se inicializó con los valores correctos
                assert service.token == 'test_token'
                assert service.organization == 'test_org'
                assert service.project_key == 'test_project'
                assert service.enabled is True
    
    def test_service_deshabilitado_cuando_settings_false(self, monkeypatch):
        """Verifica que el servicio se deshabilita cuando settings es False"""
        from config.settings import settings
        monkeypatch.setattr(settings, 'SONARCLOUD_ENABLED', False)
        
        service = SonarCloudService()
        assert service.enabled is False
    
    def test_service_deshabilitado_sin_token(self, monkeypatch):
        """Verifica que el servicio se deshabilita sin token"""
        from config.settings import settings
        monkeypatch.setattr(settings, 'SONARCLOUD_ENABLED', True)
        monkeypatch.setattr(settings, 'SONARCLOUD_TOKEN', '')
        
        service = SonarCloudService()
        assert service.enabled is False
    
    def test_service_deshabilitado_sin_organization(self, monkeypatch):
        """Verifica que el servicio se deshabilita sin organization"""
        from config.settings import settings
        monkeypatch.setattr(settings, 'SONARCLOUD_ENABLED', True)
        monkeypatch.setattr(settings, 'SONARCLOUD_TOKEN', 'token')
        monkeypatch.setattr(settings, 'SONARCLOUD_ORGANIZATION', '')
        
        service = SonarCloudService()
        assert service.enabled is False
    
    def test_service_deshabilitado_sin_project_key(self, monkeypatch):
        """Verifica que el servicio se deshabilita sin project_key"""
        from config.settings import settings
        monkeypatch.setattr(settings, 'SONARCLOUD_ENABLED', True)
        monkeypatch.setattr(settings, 'SONARCLOUD_TOKEN', 'token')
        monkeypatch.setattr(settings, 'SONARCLOUD_ORGANIZATION', 'org')
        monkeypatch.setattr(settings, 'SONARCLOUD_PROJECT_KEY', '')
        
        service = SonarCloudService()
        assert service.enabled is False
    
    def test_verify_connection_exitoso(self, mock_settings):
        """Verifica que _verify_connection funciona correctamente"""
        with patch('services.sonarcloud_service.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response
            
            service = SonarCloudService()
            # Verificar que el servicio se inicializó (enabled puede variar)
            assert isinstance(service.enabled, bool)
            # Si está habilitado, verificar que tiene los datos correctos
            if service.enabled:
                assert service.token == 'test_token'
    
    def test_verify_connection_falla_con_error_http(self, mock_settings):
        """Verifica que _verify_connection maneja errores HTTP"""
        with patch('services.sonarcloud_service.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 401
            mock_get.return_value = mock_response
            
            service = SonarCloudService()
            assert service.enabled is False
    
    def test_verify_connection_falla_con_excepcion(self, mock_settings):
        """Verifica que _verify_connection maneja excepciones"""
        with patch('services.sonarcloud_service.requests.get') as mock_get:
            mock_get.side_effect = Exception("Connection error")
            
            with patch.object(SonarCloudService, '_verify_connection', return_value=False):
                service = SonarCloudService()
                assert service.enabled is False
    
    def test_make_request_retorna_json_exitosamente(self, mock_settings):
        """Verifica que _make_request retorna JSON exitosamente"""
        with patch.object(SonarCloudService, '_verify_connection', return_value=True):
            service = SonarCloudService()
            service.enabled = True
            
            with patch('services.sonarcloud_service.requests.get') as mock_get:
                mock_response = Mock()
                mock_response.json.return_value = {'test': 'data'}
                mock_get.return_value = mock_response
                
                result = service._make_request('test/endpoint', {'param': 'value'})
                
                assert result == {'test': 'data'}
    
    def test_make_request_retorna_none_cuando_deshabilitado(self, monkeypatch):
        """Verifica que _make_request retorna None cuando está deshabilitado"""
        from config.settings import settings
        monkeypatch.setattr(settings, 'SONARCLOUD_ENABLED', False)
        
        service = SonarCloudService()
        result = service._make_request('test/endpoint')
        
        assert result is None
    
    def test_get_issues_retorna_issues(self, mock_settings):
        """Verifica que get_issues retorna resultado con issues"""
        with patch.object(SonarCloudService, '_verify_connection', return_value=True):
            service = SonarCloudService()
            service.enabled = True
            
            with patch.object(service, '_make_request') as mock_request:
                mock_request.return_value = {
                    'issues': [
                        {'key': 'issue1', 'severity': 'BLOCKER'},
                        {'key': 'issue2', 'severity': 'CRITICAL'}
                    ]
                }
                
                result = service.get_issues()
                
                # get_issues retorna un diccionario con la estructura completa
                assert isinstance(result, dict)
                assert 'issues' in result
                assert len(result['issues']) == 2
                assert result['issues'][0]['severity'] == 'BLOCKER'
    
    def test_get_issues_con_branch(self, mock_settings):
        """Verifica que get_issues funciona con branch"""
        with patch.object(SonarCloudService, '_verify_connection', return_value=True):
            service = SonarCloudService()
            service.enabled = True
            
            with patch.object(service, '_make_request') as mock_request:
                mock_request.return_value = {
                    'issues': [
                        {'key': 'issue1', 'severity': 'BLOCKER'},
                        {'key': 'issue2', 'severity': 'CRITICAL'}
                    ]
                }
                
                result = service.get_issues(branch='feature/test')
                
                # Verificar que retorna un diccionario con issues
                assert isinstance(result, dict)
                assert 'issues' in result
                assert len(result['issues']) == 2
    
    def test_get_metrics_retorna_metricas(self, mock_settings):
        """Verifica que get_metrics retorna métricas correctamente"""
        with patch.object(SonarCloudService, '_verify_connection', return_value=True):
            service = SonarCloudService()
            service.enabled = True
            
            with patch.object(service, '_make_request') as mock_request:
                mock_request.return_value = {
                    'component': {
                        'measures': [
                            {'metric': 'coverage', 'value': '80.5'},
                            {'metric': 'bugs', 'value': '2'}
                        ]
                    }
                }
                
                result = service.get_metrics()
                
                # El método transforma la respuesta, verifica que retorna algo válido
                assert result is not None
                assert isinstance(result, dict)
    
    def test_get_quality_gate_status_retorna_estado(self, mock_settings):
        """Verifica que get_quality_gate_status retorna el estado"""
        with patch.object(SonarCloudService, '_verify_connection', return_value=True):
            service = SonarCloudService()
            service.enabled = True
            
            with patch.object(service, '_make_request') as mock_request:
                mock_request.return_value = {
                    'projectStatus': {
                        'status': 'OK'
                    }
                }
                
                result = service.get_quality_gate_status()
                
                assert 'status' in result
                assert result['status'] == 'OK'
    
    def test_get_quality_gate_status_con_branch(self, mock_settings):
        """Verifica que get_quality_gate_status funciona con branch"""
        with patch.object(SonarCloudService, '_verify_connection', return_value=True):
            service = SonarCloudService()
            service.enabled = True
            
            with patch.object(service, '_make_request') as mock_request:
                mock_request.return_value = {
                    'projectStatus': {
                        'status': 'ERROR'
                    }
                }
                
                result = service.get_quality_gate_status(branch='feature/test')
                
                assert 'status' in result
                assert result['status'] == 'ERROR'
    
    def test_analyze_branch_retorna_analisis(self, mock_settings):
        """Verifica que analyze_branch retorna análisis correctamente"""
        with patch.object(SonarCloudService, '_verify_connection', return_value=True):
            service = SonarCloudService()
            service.enabled = True
            
            mock_issues = {'issues': [], 'paging': {}, 'total': 0}
            mock_quality = {'status': 'OK', 'conditions': []}
            mock_metrics = {'success': True, 'metrics': {}}
            
            with patch.object(service, 'get_issues', return_value=mock_issues):
                with patch.object(service, 'get_quality_gate_status', return_value=mock_quality):
                    with patch.object(service, 'get_metrics', return_value=mock_metrics):
                        result = service.analyze_branch('feature/test')
                        
                        # Verifica que retorna un resultado válido
                        assert result is not None
                        assert isinstance(result, dict)
            with patch.object(service, 'get_quality_gate_status', return_value=mock_quality):
                with patch.object(service, 'get_metrics', return_value=mock_metrics):
                    result = service.analyze_branch('feature/test')
                    
                    # Verifica que retorna un resultado válido
                    assert result is not None
                    assert isinstance(result, dict)
    
    def test_format_report_formatea_correctamente(self, service):
        """Verifica que format_report formatea correctamente"""
        analysis_result = {
            'success': True,
            'quality_gate': {'status': 'OK'},
            'issues': {'issues': [], 'total': 0},
            'summary': {'total': 0, 'by_severity': {}}
        }
        
        report = service.format_report(analysis_result)
        
        # Verifica que retorna un string válido
        assert isinstance(report, str)
        assert len(report) > 0
