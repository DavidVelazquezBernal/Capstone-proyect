"""
Configuración global del proyecto.
Gestión de variables de entorno y parámetros del sistema.
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


class Settings:
    """Configuración centralizada del proyecto"""
    
    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    E2B_API_KEY: str = os.getenv("E2B_API_KEY", "")
    
    # Configuración de SonarQube (opcional - para análisis real)
    SONARQUBE_URL: str = os.getenv("SONARQUBE_URL", "")
    SONARQUBE_TOKEN: str = os.getenv("SONARQUBE_TOKEN", "")
    SONARQUBE_PROJECT_KEY: str = os.getenv("SONARQUBE_PROJECT_KEY", "")
    
    # Configuración del modelo LLM
    MODEL_NAME: str = "gemini-2.5-flash"
    TEMPERATURE: float = 0.1
    MAX_OUTPUT_TOKENS: int = 4000
    
    # Configuración de reintentos para errores 503
    MAX_API_RETRIES: int = 3  # Número de reintentos si el servicio está sobrecargado
    RETRY_BASE_DELAY: int = 2  # Segundos base para backoff exponencial (2, 4, 8...)
    
    # Configuración del flujo de trabajo
    MAX_ATTEMPTS: int = 1  # Máximo de ciclos completos antes de fallo
    MAX_DEBUG_ATTEMPTS: int = 3 # Máximo de intentos en el bucle de depuración (Probador-Codificador)
    MAX_SONARQUBE_ATTEMPTS: int = 2 # Máximo de intentos en el bucle de calidad (SonarQube-Codificador)
    
    # Directorios
    OUTPUT_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "output")
    
    @classmethod
    def validate(cls) -> bool:
        """Valida que las configuraciones críticas estén presentes"""
        if not cls.GEMINI_API_KEY:
            print("⚠️ WARNING: GEMINI_API_KEY no está configurada")
            return False
        return True


# Instancia global de configuración
settings = Settings()
