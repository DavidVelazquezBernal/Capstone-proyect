"""
Utilidades para manejo de archivos y operaciones de I/O.
"""

import json
import os
from utils.logger import setup_logger, log_file_operation
from config.settings import settings

logger = setup_logger(__name__, level=settings.get_log_level())


def guardar_fichero_texto(nombre_fichero: str, contenido: str, directorio: str = None) -> bool:
    """
    Guarda el contenido proporcionado en un fichero de texto.

    Si el fichero existe, su contenido será sobrescrito.

    Args:
        nombre_fichero (str): El nombre del fichero a guardar (ej: "datos.txt").
        contenido (str): El texto que se va a escribir en el fichero.
        directorio (str, optional): Directorio donde guardar el archivo. Si no se proporciona,
                                    se guarda en el directorio actual.

    Returns:
        bool: True si la operación fue exitosa, False en caso contrario.
    """
    try:
        # Construir la ruta completa
        if directorio:
            os.makedirs(directorio, exist_ok=True)
            ruta_completa = os.path.join(directorio, nombre_fichero)
        else:
            ruta_completa = nombre_fichero

        # Guardar el archivo
        with open(ruta_completa, "w", encoding="utf-8") as file:
            file.write(contenido)

        log_file_operation(logger, "guardar", ruta_completa, success=True)
        return True

    except IOError as e:
        log_file_operation(logger, "guardar", nombre_fichero, success=False, error=str(e))
        return False


def detectar_lenguaje_y_extension(requisitos_formales: str) -> tuple[str, str, str]:
    """
    Detecta el lenguaje de programación y determina la extensión y patrón de limpieza.
    
    Args:
        requisitos_formales (str): JSON string con los requisitos formales del proyecto
        
    Returns:
        tuple: (lenguaje, extension, patron_limpieza)
    """
    lenguaje = "python"  # Por defecto
    extension = ".py"
    patron_limpieza = r'```python|```'
    
    try:
        requisitos = json.loads(requisitos_formales or '{}')
        # Buscar en varios campos posibles
        lenguaje_version = requisitos.get('lenguaje_version', '').lower()
        lenguaje_campo = requisitos.get('lenguaje', '').lower()
        lenguaje_detectado = lenguaje_version or lenguaje_campo
        
        if 'typescript' in lenguaje_detectado or 'ts' in lenguaje_detectado:
            lenguaje = "typescript"
            extension = ".ts"
            patron_limpieza = r'```typescript|```'
        
        logger.debug(f"Lenguaje detectado: {lenguaje}, extensión: {extension}")
    except (json.JSONDecodeError, AttributeError) as e:
        # Si hay error al parsear, se mantiene Python por defecto
        logger.warning(f"Error al detectar lenguaje: {e}. Usando Python por defecto.")
        pass
    
    return lenguaje, extension, patron_limpieza
