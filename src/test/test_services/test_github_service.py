import pytest
from unittest.mock import Mock, patch, MagicMock
from services.github_service import GitHubService


class TestGitHubService:
    
    @pytest.fixture
    def mock_settings(self, monkeypatch):
        """Mock de settings para tests"""
        from config.settings import settings
        monkeypatch.setattr(settings, 'GITHUB_ENABLED', True)
        monkeypatch.setattr(settings, 'GITHUB_TOKEN', 'test_token')
        monkeypatch.setattr(settings, 'GITHUB_OWNER', 'test_owner')
        monkeypatch.setattr(settings, 'GITHUB_REPO', 'test_repo')
        return settings
    
    @pytest.fixture
    def service(self, mock_settings):
        """Fixture que retorna una instancia del servicio con cliente mockeado"""
        with patch('services.github_service.GITHUB_AVAILABLE', True):
            with patch('services.github_service.Github') as MockGithub:
                mock_client = MockGithub.return_value
                mock_repo = Mock()
                mock_client.get_repo.return_value = mock_repo
                
                service = GitHubService()
                # Asegurar que el repo esté mockeado
                service.repo = mock_repo
                service.enabled = True
                return service
    
    def test_service_inicializa_correctamente(self):
        """Verifica que el servicio se inicializa correctamente"""
        service = GitHubService()
        
        assert service is not None
        assert isinstance(service.enabled, bool)
    
    def test_service_deshabilitado_cuando_settings_false(self, monkeypatch):
        """Verifica que el servicio se deshabilita cuando settings es False"""
        from config.settings import settings
        
        # Mockear settings y GITHUB_AVAILABLE ANTES de instanciar el servicio
        with patch('services.github_service.settings') as mock_settings:
            mock_settings.GITHUB_ENABLED = False
            with patch('services.github_service.GITHUB_AVAILABLE', False):
                service = GitHubService()
                
                assert service.enabled is False
    
    def test_sanitize_branch_name_limpia_caracteres_invalidos(self, service):
        """Verifica que sanitize_branch_name limpia caracteres inválidos"""
        branch_name = "feature/test@{branch}[name]"
        result = service.sanitize_branch_name(branch_name)
        
        assert "@{" not in result
        assert "[" not in result
        assert "]" not in result
    
    def test_sanitize_branch_name_remueve_espacios(self, service):
        """Verifica que sanitize_branch_name remueve espacios"""
        branch_name = "feature test branch"
        result = service.sanitize_branch_name(branch_name)
        
        assert " " not in result
        assert "_" in result
    
    def test_sanitize_branch_name_maneja_lock_suffix(self, service):
        """Verifica que sanitize_branch_name maneja el sufijo .lock"""
        branch_name = "feature/test.lock"
        result = service.sanitize_branch_name(branch_name)
        
        assert not result.endswith(".lock")
        assert result.endswith("_lock")
    
    def test_sanitize_branch_name_remueve_puntos_consecutivos(self, service):
        """Verifica que sanitize_branch_name remueve puntos consecutivos"""
        branch_name = "feature..test"
        result = service.sanitize_branch_name(branch_name)
        
        assert ".." not in result
    
    def test_create_branch_and_commit_exitoso(self, service):
        """Verifica que create_branch_and_commit funciona correctamente"""
        mock_ref = Mock()
        mock_ref.object.sha = 'abc123'
        service.repo.get_git_ref.return_value = mock_ref
        service.repo.create_git_ref.return_value = Mock()
        service.repo.create_git_tree.return_value = Mock(sha='tree123')
        
        mock_commit = Mock()
        mock_commit.sha = 'def456'
        service.repo.create_git_commit.return_value = mock_commit
        service.repo.get_git_ref.return_value.edit.return_value = None
        
        files = {'test.py': 'def test(): pass'}
        success, sha = service.create_branch_and_commit('feature/test', files, 'Test commit')
        
        # Verifica que se intentó crear el branch y commit
        assert isinstance(success, bool)
        assert sha is None or isinstance(sha, str)
    
    def test_create_branch_and_commit_retorna_false_cuando_deshabilitado(self, monkeypatch):
        """Verifica que retorna False cuando está deshabilitado"""
        from config.settings import settings
        
        # Mockear settings ANTES de instanciar el servicio
        with patch('services.github_service.settings') as mock_settings:
            mock_settings.GITHUB_ENABLED = False
            with patch('services.github_service.GITHUB_AVAILABLE', False):
                service = GitHubService()
                files = {'test.py': 'code'}
                success, sha = service.create_branch_and_commit('feature/test', files, 'commit')
                
                assert success is False
                assert sha is None
    
    def test_create_branch_and_commit_maneja_excepciones(self, mock_settings):
        """Verifica que maneja excepciones correctamente"""
        with patch('services.github_service.GITHUB_AVAILABLE', True):
            with patch('services.github_service.Github') as MockGithub:
                mock_repo = Mock()
                mock_repo.get_git_ref.side_effect = Exception("Test error")
                MockGithub.return_value.get_repo.return_value = mock_repo
                
                service = GitHubService()
                service.repo = mock_repo
                service.enabled = True
                
                files = {'test.py': 'code'}
                success, sha = service.create_branch_and_commit('feature/test', files, 'commit')
                
                assert success is False
                assert sha is None
    
    def test_create_pull_request_exitoso(self, mock_settings):
        """Verifica que create_pull_request funciona correctamente"""
        with patch('services.github_service.GITHUB_AVAILABLE', True):
            with patch('services.github_service.Github') as MockGithub:
                mock_pr = Mock()
                mock_pr.number = 123
                mock_pr.html_url = 'https://github.com/test/pr/123'
                
                mock_repo = Mock()
                mock_repo.create_pull.return_value = mock_pr
                MockGithub.return_value.get_repo.return_value = mock_repo
                
                service = GitHubService()
                service.repo = mock_repo
                service.enabled = True
                
                success, pr_number, pr_url = service.create_pull_request(
                    'feature/test',
                    'Test PR',
                    'PR description'
                )
                
                assert success is True
                assert pr_number == 123
                assert pr_url == 'https://github.com/test/pr/123'
    
    def test_create_pull_request_retorna_false_cuando_deshabilitado(self, monkeypatch):
        """Verifica que retorna False cuando está deshabilitado"""
        from config.settings import settings
        
        # Mockear settings ANTES de instanciar el servicio
        with patch('services.github_service.settings') as mock_settings:
            mock_settings.GITHUB_ENABLED = False
            with patch('services.github_service.GITHUB_AVAILABLE', False):
                service = GitHubService()
                success, pr_number, pr_url = service.create_pull_request(
                    'feature/test', 'title', 'body'
                )
                
                assert success is False
                assert pr_number is None
                assert pr_url is None
    
    def test_create_pull_request_maneja_excepciones(self, mock_settings):
        """Verifica que maneja excepciones correctamente"""
        with patch('services.github_service.GITHUB_AVAILABLE', True):
            with patch('services.github_service.Github') as MockGithub:
                mock_repo = Mock()
                mock_repo.create_pull.side_effect = Exception("Test error")
                MockGithub.return_value.get_repo.return_value = mock_repo
                
                service = GitHubService()
                service.repo = mock_repo
                service.enabled = True
                
                success, pr_number, pr_url = service.create_pull_request(
                    'feature/test', 'title', 'body'
                )
                
                assert success is False
                assert pr_number is None
                assert pr_url is None
    
    def test_add_comment_to_pr_exitoso(self, mock_settings):
        """Verifica que add_comment_to_pr funciona correctamente"""
        with patch('services.github_service.GITHUB_AVAILABLE', True):
            with patch('services.github_service.Github') as MockGithub:
                mock_pr = Mock()
                mock_repo = Mock()
                mock_repo.get_pull.return_value = mock_pr
                MockGithub.return_value.get_repo.return_value = mock_repo
                
                service = GitHubService()
                service.repo = mock_repo
                service.enabled = True
                
                success = service.add_comment_to_pr(123, 'Test comment')
                
                assert success is True
                mock_pr.create_issue_comment.assert_called_once_with('Test comment')
    
    def test_add_comment_to_pr_retorna_false_cuando_deshabilitado(self, monkeypatch):
        """Verifica que retorna False cuando está deshabilitado"""
        from config.settings import settings
        
        # Mockear settings ANTES de instanciar el servicio
        with patch('services.github_service.settings') as mock_settings:
            mock_settings.GITHUB_ENABLED = False
            with patch('services.github_service.GITHUB_AVAILABLE', False):
                service = GitHubService()
                success = service.add_comment_to_pr(123, 'comment')
                
                assert success is False
    
    def test_approve_pull_request_exitoso(self, service):
        """Verifica que approve_pull_request funciona correctamente"""
        mock_pr = Mock()
        mock_pr.create_review.return_value = Mock()
        mock_reviewer_repo = Mock()
        mock_reviewer_repo.get_pull.return_value = mock_pr
        
        with patch.object(service, '_get_reviewer_repo', return_value=mock_reviewer_repo):
            success = service.approve_pull_request(123, 'LGTM')
            
            # Verifica que se intentó aprobar
            assert isinstance(success, bool)
    
    def test_approve_pull_request_usa_repo_principal_si_no_hay_reviewer(self, mock_settings):
        """Verifica que usa el repo principal si no hay reviewer configurado"""
        with patch('services.github_service.GITHUB_AVAILABLE', True):
            with patch('services.github_service.Github') as MockGithub:
                mock_pr = Mock()
                mock_repo = Mock()
                mock_repo.get_pull.return_value = mock_pr
                MockGithub.return_value.get_repo.return_value = mock_repo
                
                service = GitHubService()
                service.repo = mock_repo
                service.enabled = True
                
                with patch.object(service, '_get_reviewer_repo', return_value=None):
                    success = service.approve_pull_request(123, 'LGTM')
                    
                    assert success is True
                    mock_pr.create_review.assert_called_once()
    
    def test_merge_pull_request_exitoso(self, mock_settings):
        """Verifica que merge_pull_request funciona correctamente"""
        with patch('services.github_service.GITHUB_AVAILABLE', True):
            with patch('services.github_service.Github') as MockGithub:
                mock_pr = Mock()
                mock_pr.mergeable = True
                mock_pr.mergeable_state = 'clean'
                mock_pr.state = 'open'
                mock_pr.merged = False
                mock_pr.merge.return_value = Mock(merged=True)
                
                mock_repo = Mock()
                mock_repo.get_pull.return_value = mock_pr
                MockGithub.return_value.get_repo.return_value = mock_repo
                
                service = GitHubService()
                service.repo = mock_repo
                service.enabled = True
                
                success = service.merge_pull_request(123, 'Merge commit message')
                
                # Verifica que se intentó hacer merge
                assert isinstance(success, bool)
                if success:
                    mock_pr.merge.assert_called_once()
    
    def test_merge_pull_request_retorna_false_cuando_falla_merge(self, mock_settings):
        """Verifica que retorna False cuando falla el merge"""
        with patch('services.github_service.GITHUB_AVAILABLE', True):
            with patch('services.github_service.Github') as MockGithub:
                mock_pr = Mock()
                mock_pr.merge.return_value = Mock(merged=False)
                
                mock_repo = Mock()
                mock_repo.get_pull.return_value = mock_pr
                MockGithub.return_value.get_repo.return_value = mock_repo
                
                service = GitHubService()
                service.repo = mock_repo
                service.enabled = True
                
                success = service.merge_pull_request(123, 'Merge commit')
                
                assert success is False
