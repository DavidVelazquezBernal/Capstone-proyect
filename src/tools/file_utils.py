"""
Utilidades para manejo de archivos y operaciones de I/O.
DEPRECATED: Usar FileManager de utils.file_manager para nuevas implementaciones.
Este módulo mantiene compatibilidad hacia atrás con código existente.
"""

import json
import os
from utils.logger import setup_logger, log_file_operation
from config.settings import settings
from utils.file_manager import FileManager

logger = setup_logger(__name__, level=settings.get_log_level())

# Instancia global para compatibilidad
_file_manager = FileManager()


def guardar_fichero_texto(nombre_fichero: str, contenido: str, directorio: str = None) -> bool:
    """
    Guarda el contenido proporcionado en un fichero de texto.
    DEPRECATED: Usar FileManager.save_file() para nuevas implementaciones.

    Si el fichero existe, su contenido será sobrescrito.

    Args:
        nombre_fichero (str): El nombre del fichero a guardar (ej: "datos.txt").
        contenido (str): El texto que se va a escribir en el fichero.
        directorio (str, optional): Directorio donde guardar el archivo. Si no se proporciona,
                                    se guarda en el directorio actual.

    Returns:
        bool: True si la operación fue exitosa, False en caso contrario.
    """
    # Delegar al FileManager
    if directorio:
        fm = FileManager(base_directory=directorio)
        success, _ = fm.save_file(nombre_fichero, contenido)
    else:
        success, _ = _file_manager.save_file(nombre_fichero, contenido)
    
    return success


def detectar_lenguaje_y_extension(requisitos_formales: str) -> tuple[str, str, str]:
    """
    Detecta el lenguaje de programación y determina la extensión y patrón de limpieza.
    DEPRECATED: Usar FileManager.detect_language_from_requirements() para nuevas implementaciones.
    
    Args:
        requisitos_formales (str): JSON string con los requisitos formales del proyecto
        
    Returns:
        tuple: (lenguaje, extension, patron_limpieza)
    """
    # Delegar al FileManager
    lenguaje, extension = FileManager.detect_language_from_requirements(requisitos_formales)
    patron_limpieza = r'UNUSED'  # Ya no se usa, mantenido por compatibilidad
    
    return lenguaje, extension, patron_limpieza


def limpiar_codigo_markdown(codigo: str) -> str:
    """
    Elimina los marcadores de bloque de código markdown del código.
    DEPRECATED: Usar FileManager.clean_markdown_code() para nuevas implementaciones.
    
    Elimina:
    - ```typescript, ```python, ```ts, ```py, ``` al inicio
    - ``` al final
    
    Args:
        codigo (str): Código que puede contener marcadores markdown
        
    Returns:
        str: Código limpio sin marcadores markdown
    """
    # Delegar al FileManager
    return FileManager.clean_markdown_code(codigo)


def extraer_nombre_archivo(requisitos_formales: str) -> str:
    """
    Extrae un nombre descriptivo para el archivo desde los requisitos formales.
    DEPRECATED: Usar FileManager.extract_filename_from_requirements() para nuevas implementaciones.
    
    Busca en orden: nombre_funcion, titulo, objetivo_funcional.
    Convierte el nombre a snake_case para usarlo como nombre de archivo.
    
    Args:
        requisitos_formales (str): JSON string con los requisitos formales del proyecto
        
    Returns:
        str: Nombre base del archivo en snake_case (sin extensión)
    """
    # Delegar al FileManager
    return FileManager.extract_filename_from_requirements(requisitos_formales)
