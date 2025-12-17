"""
Utilidades helper para logging consistente.
"""

import logging
from typing import Literal


def log_section(
    logger: logging.Logger, 
    title: str, 
    level: Literal["debug", "info", "warning", "error", "critical"] = "info",
    separator_char: str = "=",
    separator_length: int = 60
) -> None:
    """
    Log una sección con formato consistente.
    
    Args:
        logger: Logger instance
        title: Título de la sección
        level: Nivel de logging (debug, info, warning, error, critical)
        separator_char: Carácter para el separador
        separator_length: Longitud del separador
    
    Example:
        >>> log_section(logger, "INICIO DE PROCESO", level="info")
        ============================================================
        INICIO DE PROCESO
        ============================================================
    """
    log_func = getattr(logger, level.lower())
    separator = separator_char * separator_length
    
    log_func(separator)
    log_func(title)
    log_func(separator)
