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
    
    # Configuración del modelo LLM
    MODEL_NAME: str = "gemini-2.5-flash"
    TEMPERATURE: float = 0.1
    MAX_OUTPUT_TOKENS: int = 4000
    
    # Configuración del flujo de trabajo
    MAX_ATTEMPTS: int = 1  # Máximo de ciclos completos antes de fallo
    MAX_DEBUG_ATTEMPTS: int = 1  # Máximo de intentos en el bucle de depuración (Probador-Codificador)
    
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
