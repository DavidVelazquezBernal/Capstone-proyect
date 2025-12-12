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
    
    # Configuración del modelo LLM
    MODEL_NAME: str = "gemini-2.5-flash"
    TEMPERATURE: float = 0.1
    MAX_OUTPUT_TOKENS: int = 4000
    
    # Modo Testing/Mock (evita llamadas reales al LLM)
    LLM_MOCK_MODE: bool = os.getenv("LLM_MOCK_MODE", "false").lower() == "true"
    
    # Usar wrapper de LangChain (proporciona callbacks, streaming, token counting)
    USE_LANGCHAIN_WRAPPER: bool = os.getenv("USE_LANGCHAIN_WRAPPER", "false").lower() == "true"
    
    # Configuración de reintentos para errores 503
    MAX_API_RETRIES: int = 3  # Número de reintentos si el servicio está sobrecargado
    RETRY_BASE_DELAY: int = 2  # Segundos base para backoff exponencial (2, 4, 8...)
    
    # Configuración del flujo de trabajo
    MAX_ATTEMPTS: int = 1  # Máximo de ciclos completos antes de fallo
    MAX_DEBUG_ATTEMPTS: int = 3 # Máximo de intentos en el bucle de depuración (Probador-Codificador)
    MAX_SONARQUBE_ATTEMPTS: int = 3  # Máximo de intentos en el bucle de calidad (SonarQube-Desarrollador)
    
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


# Instancia global de configuración
settings = Settings()
