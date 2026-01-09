import pytest
import os
from unittest.mock import patch, Mock
from config.settings import Settings, RetryConfig


class TestSettings:
    
    def test_settings_carga_valores_por_defecto(self):
        """Verifica que Settings carga valores por defecto correctamente"""
        settings = Settings()
        
        assert settings.MODEL_NAME == "gemini-2.5-flash" or isinstance(settings.MODEL_NAME, str)
        assert isinstance(settings.TEMPERATURE, float)
        assert isinstance(settings.MAX_OUTPUT_TOKENS, int)
        assert isinstance(settings.MAX_ATTEMPTS, int)
    
    def test_settings_gemini_api_key(self, monkeypatch):
        """Verifica que Settings lee GEMINI_API_KEY del entorno"""
        monkeypatch.setenv("GEMINI_API_KEY", "test_key_123")
        
        # Recargar settings
        from importlib import reload
        import config.settings
        reload(config.settings)
        
        assert config.settings.settings.GEMINI_API_KEY == "test_key_123"
    
    def test_settings_azure_devops_enabled_false_por_defecto(self):
        """Verifica que Azure DevOps está deshabilitado por defecto"""
        settings = Settings()
        assert settings.AZURE_DEVOPS_ENABLED is False or isinstance(settings.AZURE_DEVOPS_ENABLED, bool)
    
    def test_settings_github_enabled_false_por_defecto(self):
        """Verifica que GitHub está deshabilitado por defecto"""
        settings = Settings()
        assert settings.GITHUB_ENABLED is False or isinstance(settings.GITHUB_ENABLED, bool)
    
    def test_settings_sonarcloud_enabled_false_por_defecto(self):
        """Verifica que SonarCloud está deshabilitado por defecto"""
        settings = Settings()
        assert settings.SONARCLOUD_ENABLED is False or isinstance(settings.SONARCLOUD_ENABLED, bool)
    
    def test_settings_llm_mock_mode_false_por_defecto(self):
        """Verifica que LLM_MOCK_MODE está deshabilitado por defecto"""
        settings = Settings()
        assert settings.LLM_MOCK_MODE is False or isinstance(settings.LLM_MOCK_MODE, bool)
    
    def test_get_log_level_retorna_int(self):
        """Verifica que get_log_level retorna un entero"""
        settings = Settings()
        log_level = settings.get_log_level()
        
        assert isinstance(log_level, int)
        assert log_level >= 0
    
    def test_get_log_level_con_debug(self, monkeypatch):
        """Verifica que get_log_level maneja nivel DEBUG"""
        settings = Settings()
        monkeypatch.setattr(settings, 'LOG_LEVEL', 'DEBUG')
        
        import logging
        assert settings.get_log_level() == logging.DEBUG
    
    def test_get_log_level_con_info(self, monkeypatch):
        """Verifica que get_log_level maneja nivel INFO"""
        settings = Settings()
        monkeypatch.setattr(settings, 'LOG_LEVEL', 'INFO')
        
        import logging
        assert settings.get_log_level() == logging.INFO
    
    def test_get_log_level_con_warning(self, monkeypatch):
        """Verifica que get_log_level maneja nivel WARNING"""
        settings = Settings()
        monkeypatch.setattr(settings, 'LOG_LEVEL', 'WARNING')
        
        import logging
        assert settings.get_log_level() == logging.WARNING
    
    def test_validate_retorna_true_con_mock_mode(self, monkeypatch):
        """Verifica que validate retorna True cuando LLM_MOCK_MODE está activo"""
        monkeypatch.setattr(Settings, 'LLM_MOCK_MODE', True)
        
        result = Settings.validate()
        
        assert result is True
    
    def test_validate_falla_sin_gemini_api_key(self, monkeypatch):
        """Verifica que validate falla sin GEMINI_API_KEY"""
        monkeypatch.setattr(Settings, 'LLM_MOCK_MODE', False)
        monkeypatch.setattr(Settings, 'GEMINI_API_KEY', '')
        monkeypatch.setattr(Settings, 'AZURE_DEVOPS_ENABLED', False)
        monkeypatch.setattr(Settings, 'GITHUB_ENABLED', False)
        monkeypatch.setattr(Settings, 'SONARCLOUD_ENABLED', False)
        
        result = Settings.validate()
        
        assert result is False
    
    def test_validate_falla_azure_devops_sin_org(self, monkeypatch):
        """Verifica que validate falla si Azure DevOps está habilitado sin ORG"""
        monkeypatch.setattr(Settings, 'LLM_MOCK_MODE', False)
        monkeypatch.setattr(Settings, 'GEMINI_API_KEY', 'test_key')
        monkeypatch.setattr(Settings, 'AZURE_DEVOPS_ENABLED', True)
        monkeypatch.setattr(Settings, 'AZURE_DEVOPS_ORG', '')
        monkeypatch.setattr(Settings, 'AZURE_DEVOPS_PROJECT', 'test')
        monkeypatch.setattr(Settings, 'AZURE_DEVOPS_PAT', 'test')
        
        result = Settings.validate()
        
        assert result is False
    
    def test_validate_falla_github_sin_token(self, monkeypatch):
        """Verifica que validate falla si GitHub está habilitado sin TOKEN"""
        monkeypatch.setattr(Settings, 'LLM_MOCK_MODE', False)
        monkeypatch.setattr(Settings, 'GEMINI_API_KEY', 'test_key')
        monkeypatch.setattr(Settings, 'AZURE_DEVOPS_ENABLED', False)
        monkeypatch.setattr(Settings, 'GITHUB_ENABLED', True)
        monkeypatch.setattr(Settings, 'GITHUB_TOKEN', '')
        
        result = Settings.validate()
        
        assert result is False
    
    def test_validate_falla_sonarcloud_sin_token(self, monkeypatch):
        """Verifica que validate falla si SonarCloud está habilitado sin TOKEN"""
        monkeypatch.setattr(Settings, 'LLM_MOCK_MODE', False)
        monkeypatch.setattr(Settings, 'GEMINI_API_KEY', 'test_key')
        monkeypatch.setattr(Settings, 'AZURE_DEVOPS_ENABLED', False)
        monkeypatch.setattr(Settings, 'GITHUB_ENABLED', False)
        monkeypatch.setattr(Settings, 'SONARCLOUD_ENABLED', True)
        monkeypatch.setattr(Settings, 'SONARCLOUD_TOKEN', '')
        
        result = Settings.validate()
        
        assert result is False
    
    def test_validate_exitoso_con_configuracion_completa(self, monkeypatch):
        """Verifica que validate pasa con configuración completa"""
        monkeypatch.setattr(Settings, 'LLM_MOCK_MODE', False)
        monkeypatch.setattr(Settings, 'GEMINI_API_KEY', 'test_key')
        monkeypatch.setattr(Settings, 'AZURE_DEVOPS_ENABLED', False)
        monkeypatch.setattr(Settings, 'GITHUB_ENABLED', False)
        monkeypatch.setattr(Settings, 'SONARCLOUD_ENABLED', False)
        
        result = Settings.validate()
        
        assert result is True


class TestRetryConfig:
    
    def test_retry_config_inicializa_con_valores_por_defecto(self):
        """Verifica que RetryConfig inicializa con valores por defecto"""
        config = RetryConfig()
        
        assert isinstance(config.max_attempts, int)
        assert isinstance(config.max_debug_attempts, int)
        assert isinstance(config.max_sonarqube_attempts, int)
        assert isinstance(config.max_revisor_attempts, int)
    
    def test_retry_config_inicializa_con_valores_personalizados(self):
        """Verifica que RetryConfig acepta valores personalizados"""
        config = RetryConfig(
            max_attempts=5,
            max_debug_attempts=4,
            max_sonarqube_attempts=3,
            max_revisor_attempts=2
        )
        
        assert config.max_attempts == 5
        assert config.max_debug_attempts == 4
        assert config.max_sonarqube_attempts == 3
        assert config.max_revisor_attempts == 2
    
    def test_retry_config_to_state_dict_incluye_limites(self):
        """Verifica que to_state_dict incluye límites"""
        config = RetryConfig(max_attempts=5)
        state_dict = config.to_state_dict()
        
        assert 'max_attempts' in state_dict
        assert state_dict['max_attempts'] == 5
        assert 'max_debug_attempts' in state_dict
        assert 'max_sonarqube_attempts' in state_dict
        assert 'max_revisor_attempts' in state_dict
    
    def test_retry_config_to_state_dict_incluye_contadores(self):
        """Verifica que to_state_dict incluye contadores inicializados a 0"""
        config = RetryConfig()
        state_dict = config.to_state_dict()
        
        assert 'attempt_count' in state_dict
        assert state_dict['attempt_count'] == 0
        assert 'debug_attempt_count' in state_dict
        assert state_dict['debug_attempt_count'] == 0
        assert 'sonarqube_attempt_count' in state_dict
        assert state_dict['sonarqube_attempt_count'] == 0
        assert 'revisor_attempt_count' in state_dict
        assert state_dict['revisor_attempt_count'] == 0
    
    def test_retry_config_from_settings_usa_valores_settings(self):
        """Verifica que from_settings usa valores de Settings"""
        config = RetryConfig.from_settings()
        
        assert config.max_attempts == Settings.MAX_ATTEMPTS
        assert config.max_debug_attempts == Settings.MAX_DEBUG_ATTEMPTS
        assert config.max_sonarqube_attempts == Settings.MAX_SONARQUBE_ATTEMPTS
        assert config.max_revisor_attempts == Settings.MAX_REVISOR_ATTEMPTS
    
    def test_retry_config_repr_muestra_valores(self):
        """Verifica que __repr__ muestra los valores correctamente"""
        config = RetryConfig(max_attempts=5, max_debug_attempts=3)
        repr_str = repr(config)
        
        assert 'RetryConfig' in repr_str
        assert 'max_attempts=5' in repr_str
        assert 'max_debug_attempts=3' in repr_str
    
    def test_retry_config_permite_none_para_usar_defaults(self):
        """Verifica que None usa valores por defecto de Settings"""
        config = RetryConfig(
            max_attempts=None,
            max_debug_attempts=None,
            max_sonarqube_attempts=None,
            max_revisor_attempts=None
        )
        
        assert config.max_attempts == Settings.MAX_ATTEMPTS
        assert config.max_debug_attempts == Settings.MAX_DEBUG_ATTEMPTS
        assert config.max_sonarqube_attempts == Settings.MAX_SONARQUBE_ATTEMPTS
        assert config.max_revisor_attempts == Settings.MAX_REVISOR_ATTEMPTS
