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
    # Patrón genérico para eliminar bloques markdown
    patron_limpieza = r'UNUSED'  # Ya no se usa, ver limpiar_codigo_markdown()
    
    try:
        requisitos = json.loads(requisitos_formales or '{}')
        # Buscar en varios campos posibles
        lenguaje_version = requisitos.get('lenguaje_version', '').lower()
        lenguaje_campo = requisitos.get('lenguaje', '').lower()
        lenguaje_detectado = lenguaje_version or lenguaje_campo
        
        if 'typescript' in lenguaje_detectado or 'ts' in lenguaje_detectado:
            lenguaje = "typescript"
            extension = ".ts"
        
        logger.debug(f"Lenguaje detectado: {lenguaje}, extensión: {extension}")
    except (json.JSONDecodeError, AttributeError) as e:
        # Si hay error al parsear, se mantiene Python por defecto
        logger.warning(f"Error al detectar lenguaje: {e}. Usando Python por defecto.")
        pass
    
    return lenguaje, extension, patron_limpieza


def limpiar_codigo_markdown(codigo: str) -> str:
    """
    Elimina los marcadores de bloque de código markdown del código.
    
    Elimina:
    - ```typescript, ```python, ```ts, ```py, ``` al inicio
    - ``` al final
    
    Args:
        codigo (str): Código que puede contener marcadores markdown
        
    Returns:
        str: Código limpio sin marcadores markdown
    """
    if not codigo:
        return codigo
    
    resultado = codigo.strip()
    
    # Eliminar bloque de apertura al inicio: ```typescript, ```python, etc.
    if resultado.startswith('```'):
        # Encontrar el final de la primera línea
        primera_linea_fin = resultado.find('\n')
        if primera_linea_fin != -1:
            resultado = resultado[primera_linea_fin + 1:]
        else:
            # Solo hay una línea con ```
            resultado = resultado[3:]
    
    # Eliminar bloque de cierre al final: ```
    if resultado.rstrip().endswith('```'):
        resultado = resultado.rstrip()
        resultado = resultado[:-3]
    
    return resultado.strip()


def extraer_nombre_archivo(requisitos_formales: str) -> str:
    """
    Extrae un nombre descriptivo para el archivo desde los requisitos formales.
    
    Busca en orden: nombre_funcion, titulo, objetivo_funcional.
    Convierte el nombre a snake_case para usarlo como nombre de archivo.
    
    Args:
        requisitos_formales (str): JSON string con los requisitos formales del proyecto
        
    Returns:
        str: Nombre base del archivo en snake_case (sin extensión)
    """
    import re as regex
    
    nombre_base = "codigo_generado"  # Nombre por defecto
    
    try:
        requisitos = json.loads(requisitos_formales or '{}')
        
        # Buscar nombre en orden de prioridad
        nombre_candidato = (
            requisitos.get('nombre_funcion') or
            requisitos.get('titulo') or
            requisitos.get('objetivo_funcional', '')
        )
        
        if nombre_candidato:
            # Convertir a snake_case
            # 1. Reemplazar espacios y caracteres especiales por guiones bajos
            nombre_limpio = regex.sub(r'[^a-zA-Z0-9áéíóúñÁÉÍÓÚÑ]', '_', nombre_candidato)
            # 2. Convertir camelCase a snake_case
            nombre_limpio = regex.sub(r'([a-z])([A-Z])', r'\1_\2', nombre_limpio)
            # 3. Convertir a minúsculas
            nombre_limpio = nombre_limpio.lower()
            # 4. Eliminar guiones bajos múltiples y al inicio/final
            nombre_limpio = regex.sub(r'_+', '_', nombre_limpio).strip('_')
            # 5. Limitar longitud
            nombre_limpio = nombre_limpio[:50]
            
            if nombre_limpio:
                nombre_base = nombre_limpio
                
        logger.debug(f"Nombre de archivo extraído: {nombre_base}")
    except (json.JSONDecodeError, AttributeError) as e:
        logger.warning(f"Error al extraer nombre de archivo: {e}. Usando nombre por defecto.")
    
    return nombre_base
