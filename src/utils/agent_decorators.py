"""
Decoradores y context managers para agentes.
Proporciona utilidades para logging consistente y gestión de ejecución de agentes.
"""

from contextlib import contextmanager
from typing import Optional
import logging


@contextmanager
def agent_execution_context(agent_name: str, logger: logging.Logger):
    """
    Context manager para logging consistente de inicio y fin de agentes.
    
    Proporciona un formato estandarizado para todos los agentes:
    - Línea en blanco para separación visual
    - Separador de 60 caracteres
    - Mensaje de INICIO
    - Separador de 60 caracteres
    - ... ejecución del agente ...
    - Separador de 60 caracteres
    - Mensaje de FIN
    - Separador de 60 caracteres
    
    Args:
        agent_name: Nombre del agente con emoji opcional (ej: "💻 DESARROLLADOR")
        logger: Logger configurado para el agente
    
    Usage:
        with agent_execution_context("💻 DESARROLLADOR", logger):
            # Lógica del agente aquí
            state['codigo_generado'] = "..."
            return state
    """
    print()  # Línea en blanco para separación visual
    logger.info("=" * 60)
    logger.info(f"{agent_name} - INICIO")
    logger.info("=" * 60)
    
    try:
        yield
    finally:
        logger.info("=" * 60)
        logger.info(f"{agent_name} - FIN")
        logger.info("=" * 60)
