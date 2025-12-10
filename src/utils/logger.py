"""
Sistema de logging centralizado para el proyecto.
Proporciona loggers configurados para cada módulo con diferentes niveles y handlers.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


# Variable global para almacenar el archivo de log de la sesión
_SESSION_LOG_FILE = None


def get_session_log_file():
    """Obtiene o crea el archivo de log para la sesión actual"""
    global _SESSION_LOG_FILE
    if _SESSION_LOG_FILE is None:
        # Importar aquí para evitar importación circular
        from config.settings import settings
        
        log_dir = Path(settings.OUTPUT_DIR) / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        _SESSION_LOG_FILE = log_dir / f'workflow_{timestamp}.log'
    return _SESSION_LOG_FILE


class ColoredFormatter(logging.Formatter):
    """Formatter con colores para consola (solo si el terminal lo soporta)"""
    
    # Códigos ANSI para colores
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Verde
        'WARNING': '\033[33m',    # Amarillo
        'ERROR': '\033[31m',      # Rojo
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'
    }
    
    def format(self, record):
        # Añadir color solo si es un terminal interactivo
        if sys.stdout.isatty():
            color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
            record.levelname = f"{color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


class AgentFormatter(logging.Formatter):
    """Formatter especializado para logs de agentes con emojis"""
    
    AGENT_EMOJIS = {
        'ingeniero_requisitos': '🙋‍♂️',
        'product_owner': '💼',
        'desarrollador': '💻',
        'analizador_sonarqube': '🔍',
        'generador_unit_tests': '🧪',
        'ejecutor_pruebas': '⚡',
        'stakeholder': '✅',
        'workflow': '⚙️',
        'main': '🚀'
    }
    
    def format(self, record):
        # Detectar el módulo del agente
        module_name = record.name.split('.')[-1]
        emoji = self.AGENT_EMOJIS.get(module_name, '📝')
        
        # Solo añadir emoji si el mensaje no tiene emojis ya
        # Detectamos emojis buscando caracteres Unicode en rangos típicos de emojis
        msg_str = str(record.msg)
        has_emoji = any(ord(char) > 0x1F300 for char in msg_str[:5])  # Revisar primeros 5 caracteres
        
        if not has_emoji:
            # Añadir emoji al mensaje
            if hasattr(record, 'agent_context'):
                record.msg = f"{emoji} [{record.agent_context}] {record.msg}"
            else:
                record.msg = f"{emoji} {record.msg}"
        
        return super().format(record)


def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_to_file: bool = True,
    agent_mode: bool = False
) -> logging.Logger:
    """
    Configura y retorna un logger personalizado.
    
    Args:
        name: Nombre del logger (usualmente __name__ del módulo)
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Si True, también guarda logs en archivo
        agent_mode: Si True, usa formato especializado para agentes
        
    Returns:
        Logger configurado
        
    Example:
        >>> logger = setup_logger(__name__)
        >>> logger.info("Iniciando proceso")
    """
    logger = logging.getLogger(name)
    
    # Evitar duplicar handlers si ya está configurado
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    logger.propagate = False
    
    # === Handler para CONSOLA ===
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    if agent_mode:
        console_format = AgentFormatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )
    else:
        console_format = ColoredFormatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%H:%M:%S'
        )
    
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # === Handler para ARCHIVO ===
    if log_to_file:
        # Usar el archivo de log compartido de la sesión
        log_file = get_session_log_file()
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)  # En archivo guardamos todo
        
        file_format = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
    
    return logger


def log_state_transition(logger: logging.Logger, from_node: str, to_node: str, state: dict):
    """
    Log estructurado para transiciones de estado en el workflow.
    
    Args:
        logger: Logger a usar
        from_node: Nodo de origen
        to_node: Nodo de destino
        state: Estado actual (solo se loguean campos clave)
    """
    logger.info(
        f"Transición: {from_node} → {to_node}",
        extra={
            'transition': {
                'from': from_node,
                'to': to_node,
                'attempt': state.get('attempt_count', 0),
                'debug_attempt': state.get('debug_attempt_count', 0),
                'sonarqube_attempt': state.get('sonarqube_attempt_count', 0)
            }
        }
    )


def log_agent_execution(
    logger: logging.Logger,
    agent_name: str,
    action: str,
    details: Optional[dict] = None,
    level: int = logging.INFO
):
    """
    Log estructurado para ejecución de agentes.
    
    Args:
        logger: Logger a usar
        agent_name: Nombre del agente
        action: Acción realizada
        details: Detalles adicionales opcionales
        level: Nivel del log
        
    Example:
        >>> log_agent_execution(logger, "Codificador", "Código generado", 
        ...                     {"lines": 50, "language": "python"})
    """
    message = f"{action}"
    if details:
        detail_str = ", ".join(f"{k}={v}" for k, v in details.items())
        message = f"{action} ({detail_str})"
    
    logger.log(level, message, extra={'agent_context': agent_name})


def log_llm_call(
    logger: logging.Logger,
    prompt_type: str,
    tokens_used: Optional[int] = None,
    duration: Optional[float] = None
):
    """
    Log específico para llamadas al LLM.
    
    Args:
        logger: Logger a usar
        prompt_type: Tipo de prompt (ej: "INGENIERO_REQUISITOS")
        tokens_used: Tokens consumidos (si disponible)
        duration: Duración en segundos
    """
    details = {"prompt": prompt_type}
    if tokens_used:
        details["tokens"] = tokens_used
    if duration:
        details["duration_s"] = f"{duration:.2f}"
    
    detail_str = ", ".join(f"{k}={v}" for k, v in details.items())
    logger.debug(f"LLM llamada: {detail_str}")


def log_file_operation(
    logger: logging.Logger,
    operation: str,
    filepath: str,
    success: bool = True,
    error: Optional[str] = None
):
    """
    Log para operaciones de archivos.
    
    Args:
        logger: Logger a usar
        operation: Tipo de operación ("guardar", "leer", "eliminar")
        filepath: Ruta del archivo
        success: Si la operación fue exitosa
        error: Mensaje de error si falló
    """
    if success:
        logger.debug(f"Archivo {operation}: {filepath}")
    else:
        logger.error(f"Error al {operation} archivo {filepath}: {error}")


# === Logger global para el sistema ===
system_logger = setup_logger('capstone_system', level=logging.INFO)


# === Ejemplo de uso ===
if __name__ == "__main__":
    # Test del sistema de logging
    logger = setup_logger(__name__, agent_mode=True)
    
    logger.debug("Mensaje de debug")
    logger.info("Mensaje de info")
    logger.warning("Mensaje de warning")
    logger.error("Mensaje de error")
    logger.critical("Mensaje crítico")
    
    # Test de logs estructurados
    log_agent_execution(logger, "TestAgent", "Acción de prueba", {"param": "valor"})
    log_llm_call(logger, "TEST_PROMPT", tokens_used=150, duration=1.5)
    log_file_operation(logger, "guardar", "output/test.txt", success=True)
