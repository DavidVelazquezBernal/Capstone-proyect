"""
Configuración global del proyecto.
Gestión de variables de entorno y parámetros del sistema.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Obtener el directorio actual (config/) y subir a src/
current_dir = Path(__file__).parent
src_dir = current_dir.parent
env_path = src_dir / ".env"

# Cargar variables de entorno desde src/.env
load_dotenv(dotenv_path=env_path)


class Settings:
    """Configuración centralizada del proyecto"""
    
    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    E2B_API_KEY: str = os.getenv("E2B_API_KEY", "")
    
    # Configuración de SonarQube (opcional - para análisis real)
    SONARQUBE_URL: str = os.getenv("SONARQUBE_URL", "")
    SONARQUBE_TOKEN: str = os.getenv("SONARQUBE_TOKEN", "")
    SONARQUBE_PROJECT_KEY: str = os.getenv("SONARQUBE_PROJECT_KEY", "")
    
    # Configuración de Azure DevOps (opcional - para integración con ADO)
    AZURE_DEVOPS_ENABLED: bool = os.getenv("AZURE_DEVOPS_ENABLED", "false").lower() == "true"
    AZURE_DEVOPS_ORG: str = os.getenv("AZURE_DEVOPS_ORG", "")
    AZURE_DEVOPS_PROJECT: str = os.getenv("AZURE_DEVOPS_PROJECT", "")
    AZURE_DEVOPS_PAT: str = os.getenv("AZURE_DEVOPS_PAT", "")
    AZURE_ITERATION_PATH: str = os.getenv("AZURE_ITERATION_PATH", "")  # ej: "MyProject\\Sprint 1"
    AZURE_AREA_PATH: str = os.getenv("AZURE_AREA_PATH", "")  # ej: "MyProject\\Backend"
    AZURE_ASSIGNED_TO: str = os.getenv("AZURE_ASSIGNED_TO", "")  # Usuario asignado por defecto (vacío = sin asignar)
    
    # Configuración de GitHub (opcional - para integración con repositorios)
    GITHUB_ENABLED: bool = os.getenv("GITHUB_ENABLED", "false").lower() == "true"
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")  # Personal Access Token con permisos repo
    GITHUB_REVIEWER_TOKEN: str = os.getenv("GITHUB_REVIEWER_TOKEN", "")  # Token opcional para aprobar reviews (cuenta distinta)
    GITHUB_OWNER: str = os.getenv("GITHUB_OWNER", "")  # Usuario u organización dueña del repo
    GITHUB_REPO: str = os.getenv("GITHUB_REPO", "")  # Nombre del repositorio
    GITHUB_BASE_BRANCH: str = os.getenv("GITHUB_BASE_BRANCH", "main")  # Branch base para PRs
    GITHUB_REPO_PATH: str = os.getenv("GITHUB_REPO_PATH", r"C:\ACADEMIA\IIA\Output\Multiagentes-Coding")  # Ruta física del repo local
    
    # Configuración de SonarCloud (opcional - para análisis de calidad en la nube)
    SONARCLOUD_ENABLED: bool = os.getenv("SONARCLOUD_ENABLED", "false").lower() == "true"
    SONARCLOUD_TOKEN: str = os.getenv("SONARCLOUD_TOKEN", "")  # Token de SonarCloud
    SONARCLOUD_ORGANIZATION: str = os.getenv("SONARCLOUD_ORGANIZATION", "")  # Organización en SonarCloud
    SONARCLOUD_PROJECT_KEY: str = os.getenv("SONARCLOUD_PROJECT_KEY", "")  # Project key en SonarCloud
    
    # Configuración del modelo LLM
    MODEL_NAME: str = "gemini-2.5-flash"
    TEMPERATURE: float = 0.1
    MAX_OUTPUT_TOKENS: int = int(os.getenv("MAX_OUTPUT_TOKENS", "8192"))

    MAX_TEST_FIX_ATTEMPTS: int = int(os.getenv("MAX_TEST_FIX_ATTEMPTS", "2"))
    
    # Modo Testing/Mock (evita llamadas reales al LLM)
    LLM_MOCK_MODE: bool = os.getenv("LLM_MOCK_MODE", "false").lower() == "true"
    
    # Usar wrapper de LangChain (proporciona callbacks, streaming, token counting)
    USE_LANGCHAIN_WRAPPER: bool = os.getenv("USE_LANGCHAIN_WRAPPER", "false").lower() == "true"
    
    # Configuración de reintentos para errores 503
    MAX_API_RETRIES: int = 3  # Número de reintentos si el servicio está sobrecargado
    RETRY_BASE_DELAY: int = 2  # Segundos base para backoff exponencial (2, 4, 8...)
    
    # Configuración del flujo de trabajo (DEPRECATED - usar RetryConfig)
    MAX_ATTEMPTS: int = 1  # Máximo de ciclos completos antes de fallo
    MAX_DEBUG_ATTEMPTS: int = 3 # Máximo de intentos en el bucle de depuración (Probador-Codificador)
    MAX_SONARQUBE_ATTEMPTS: int = 3  # Máximo de intentos en el bucle de calidad (SonarQube-Desarrollador)
    MAX_REVISOR_ATTEMPTS: int = 2  # Máximo de intentos de revisión de código antes de fallo
    
    # Directorios
    OUTPUT_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "output")
    
    # Configuración de Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_TO_FILE: bool = os.getenv("LOG_TO_FILE", "true").lower() == "true"
    
    def get_log_level(self) -> int:
        """Convierte string de nivel a constante de logging"""
        import logging
        return getattr(logging, self.LOG_LEVEL.upper(), logging.INFO)
    
    @classmethod
    def validate(cls) -> bool:
        """Valida que las configuraciones críticas estén presentes"""
        # En modo mock, no se requiere API key
        if cls.LLM_MOCK_MODE:
            print("🧪 INFO: LLM_MOCK_MODE activado - usando respuestas mockeadas")
            return True
            
        if not cls.GEMINI_API_KEY:
            print("⚠️ WARNING: GEMINI_API_KEY no está configurada")
            return False
        return True


class RetryConfig:
    """
    Configuración consolidada de reintentos y límites para el flujo de trabajo.
    Centraliza todos los contadores y límites de reintentos en un solo lugar.
    """
    
    def __init__(
        self,
        max_attempts: int | None = None,
        max_debug_attempts: int | None = None,
        max_sonarqube_attempts: int | None = None,
        max_revisor_attempts: int | None = None
    ):
        """
        Inicializa la configuración de reintentos.
        
        Args:
            max_attempts: Máximo de ciclos completos antes de fallo (Stakeholder loop)
            max_debug_attempts: Máximo de intentos en el bucle de depuración (Testing-Desarrollador)
            max_sonarqube_attempts: Máximo de intentos en el bucle de calidad (SonarQube-Desarrollador)
            max_revisor_attempts: Máximo de intentos de revisión de código antes de fallo
        """
        self.max_attempts = max_attempts if max_attempts is not None else Settings.MAX_ATTEMPTS
        self.max_debug_attempts = max_debug_attempts if max_debug_attempts is not None else Settings.MAX_DEBUG_ATTEMPTS
        self.max_sonarqube_attempts = max_sonarqube_attempts if max_sonarqube_attempts is not None else Settings.MAX_SONARQUBE_ATTEMPTS
        self.max_revisor_attempts = max_revisor_attempts if max_revisor_attempts is not None else Settings.MAX_REVISOR_ATTEMPTS
    
    def to_state_dict(self) -> dict:
        """
        Convierte la configuración a un diccionario compatible con AgentState.
        Incluye tanto los límites (max_*) como los contadores inicializados a 0.
        
        Returns:
            dict: Diccionario con límites y contadores para inicializar el estado
        """
        return {
            # Límites
            "max_attempts": self.max_attempts,
            "max_debug_attempts": self.max_debug_attempts,
            "max_sonarqube_attempts": self.max_sonarqube_attempts,
            "max_revisor_attempts": self.max_revisor_attempts,
            # Contadores (inicializados a 0)
            "attempt_count": 0,
            "debug_attempt_count": 0,
            "sonarqube_attempt_count": 0,
            "revisor_attempt_count": 0
        }
    
    @classmethod
    def from_settings(cls) -> 'RetryConfig':
        """
        Crea una configuración de reintentos usando los valores por defecto de Settings.
        
        Returns:
            RetryConfig: Instancia con valores por defecto
        """
        return cls()
    
    def __repr__(self) -> str:
        return (
            f"RetryConfig("
            f"max_attempts={self.max_attempts}, "
            f"max_debug_attempts={self.max_debug_attempts}, "
            f"max_sonarqube_attempts={self.max_sonarqube_attempts}, "
            f"max_revisor_attempts={self.max_revisor_attempts})"
        )


# Instancia global de configuración
settings = Settings()
