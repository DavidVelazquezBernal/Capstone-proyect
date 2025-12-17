"""
Gestor consolidado de operaciones de archivos.
Centraliza patrones comunes de gestión de archivos usados por los agentes.
"""

import os
import json
from typing import Tuple, Optional
from pathlib import Path

from config.settings import settings
from utils.logger import setup_logger, log_file_operation

logger = setup_logger(__name__, level=settings.get_log_level())


class FileManager:
    """
    Gestor centralizado de operaciones de archivos.
    Proporciona métodos para guardar, nombrar y gestionar archivos de forma consistente.
    """
    
    def __init__(self, base_directory: str = None):
        """
        Inicializa el gestor de archivos.
        
        Args:
            base_directory: Directorio base para operaciones. Por defecto usa settings.OUTPUT_DIR
        """
        self.base_directory = base_directory or settings.OUTPUT_DIR
        self._ensure_directory_exists(self.base_directory)
    
    def _ensure_directory_exists(self, directory: str) -> None:
        """Crea el directorio si no existe."""
        os.makedirs(directory, exist_ok=True)
    
    def save_file(
        self, 
        filename: str, 
        content: str, 
        subdirectory: str = None
    ) -> Tuple[bool, str]:
        """
        Guarda contenido en un archivo con logging automático.
        
        Args:
            filename: Nombre del archivo
            content: Contenido a guardar
            subdirectory: Subdirectorio opcional dentro del base_directory
            
        Returns:
            Tuple (success, full_path)
        """
        try:
            # Construir ruta completa
            if subdirectory:
                directory = os.path.join(self.base_directory, subdirectory)
                self._ensure_directory_exists(directory)
            else:
                directory = self.base_directory
            
            full_path = os.path.join(directory, filename)
            
            # Guardar archivo
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            log_file_operation(logger, "guardar", full_path, success=True)
            return True, full_path
        
        except IOError as e:
            log_file_operation(logger, "guardar", filename, success=False, error=str(e))
            return False, ""
    
    def generate_report_filename(
        self,
        prefix: str,
        attempt: int,
        debug_attempt: int = None,
        sonarqube_attempt: int = None,
        status: str = None,
        extension: str = "txt"
    ) -> str:
        """
        Genera nombres de archivo consistentes para reportes.
        
        Args:
            prefix: Prefijo del archivo (ej: "testing", "sonarqube")
            attempt: Número de intento del requisito
            debug_attempt: Número de intento de debug (opcional)
            sonarqube_attempt: Número de intento de SonarQube (opcional)
            status: Estado del reporte (ej: "PASSED", "FAILED", "ERROR")
            extension: Extensión del archivo (sin punto)
            
        Returns:
            Nombre del archivo generado
            
        Examples:
            >>> fm.generate_report_filename("testing", 1, debug_attempt=2, status="PASSED")
            "4_testing_req1_debug2_PASSED.txt"
            
            >>> fm.generate_report_filename("sonarqube", 1, sonarqube_attempt=0)
            "3_sonarqube_report_req1_sq0.txt"
        """
        parts = [prefix, f"req{attempt}"]
        
        if debug_attempt is not None:
            parts.append(f"debug{debug_attempt}")
        
        if sonarqube_attempt is not None:
            parts.append(f"sq{sonarqube_attempt}")
        
        if status:
            parts.append(status)
        
        filename = "_".join(parts)
        return f"{filename}.{extension}"
    
    def generate_code_filename(
        self,
        base_name: str,
        language: str,
        is_test: bool = False
    ) -> str:
        """
        Genera nombres de archivo para código.
        
        Args:
            base_name: Nombre base del archivo (sin extensión)
            language: Lenguaje de programación ('typescript', 'python', etc.)
            is_test: Si es un archivo de tests
            
        Returns:
            Nombre del archivo con extensión apropiada
            
        Examples:
            >>> fm.generate_code_filename("calculator", "typescript", is_test=False)
            "calculator.ts"
            
            >>> fm.generate_code_filename("calculator", "python", is_test=True)
            "test_calculator.py"
        """
        # Determinar extensión
        language_lower = language.lower()
        if language_lower in ('typescript', 'ts'):
            extension = '.ts'
        elif language_lower in ('python', 'py'):
            extension = '.py'
        elif language_lower in ('javascript', 'js'):
            extension = '.js'
        else:
            extension = '.txt'
        
        # Agregar prefijo de test si aplica
        if is_test:
            if language_lower in ('typescript', 'ts', 'javascript', 'js'):
                # TypeScript/JavaScript: calculator.test.ts
                return f"{base_name}.test{extension}"
            else:
                # Python: test_calculator.py
                return f"test_{base_name}{extension}"
        
        return f"{base_name}{extension}"
    
    @staticmethod
    def detect_language_from_requirements(requisitos_formales: str) -> Tuple[str, str]:
        """
        Detecta el lenguaje de programación desde los requisitos formales.
        
        Args:
            requisitos_formales: JSON string con los requisitos formales
            
        Returns:
            Tuple (lenguaje, extension)
            
        Examples:
            >>> FileManager.detect_language_from_requirements('{"lenguaje": "TypeScript"}')
            ("typescript", ".ts")
        """
        lenguaje = "python"
        extension = ".py"
        
        try:
            requisitos = json.loads(requisitos_formales or '{}')
            lenguaje_version = requisitos.get('lenguaje_version', '').lower()
            lenguaje_campo = requisitos.get('lenguaje', '').lower()
            lenguaje_detectado = lenguaje_version or lenguaje_campo
            
            if 'typescript' in lenguaje_detectado or 'ts' in lenguaje_detectado:
                lenguaje = "typescript"
                extension = ".ts"
            elif 'javascript' in lenguaje_detectado or 'js' in lenguaje_detectado:
                lenguaje = "javascript"
                extension = ".js"
            
            logger.debug(f"Lenguaje detectado: {lenguaje}, extensión: {extension}")
        except (json.JSONDecodeError, AttributeError) as e:
            logger.warning(f"Error al detectar lenguaje: {e}. Usando Python por defecto.")
        
        return lenguaje, extension
    
    @staticmethod
    def clean_markdown_code(codigo: str) -> str:
        """
        Elimina marcadores de bloque de código markdown.
        
        Args:
            codigo: Código que puede contener marcadores markdown
            
        Returns:
            Código limpio sin marcadores markdown
            
        Examples:
            >>> FileManager.clean_markdown_code("```python\\nprint('hello')\\n```")
            "print('hello')"
        """
        if not codigo:
            return codigo
        
        resultado = codigo.strip()
        
        # Eliminar bloque de apertura: ```typescript, ```python, etc.
        if resultado.startswith('```'):
            primera_linea_fin = resultado.find('\n')
            if primera_linea_fin != -1:
                resultado = resultado[primera_linea_fin + 1:]
            else:
                resultado = resultado[3:]
        
        # Eliminar bloque de cierre: ```
        if resultado.rstrip().endswith('```'):
            resultado = resultado.rstrip()[:-3]
        
        return resultado.strip()
    
    @staticmethod
    def extract_filename_from_requirements(requisitos_formales: str) -> str:
        """
        Extrae un nombre descriptivo para el archivo desde los requisitos formales.
        
        Busca en orden: nombre_funcion, titulo, objetivo_funcional.
        Convierte el nombre a snake_case.
        
        Args:
            requisitos_formales: JSON string con los requisitos formales
            
        Returns:
            Nombre base del archivo en snake_case (sin extensión)
            
        Examples:
            >>> FileManager.extract_filename_from_requirements('{"nombre_funcion": "CalcularFactorial"}')
            "calcular_factorial"
        """
        import re
        
        nombre_base = "codigo_generado"
        
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
                nombre_limpio = re.sub(r'[^a-zA-Z0-9áéíóúñÁÉÍÓÚÑ]', '_', nombre_candidato)
                nombre_limpio = re.sub(r'([a-z])([A-Z])', r'\1_\2', nombre_limpio)
                nombre_limpio = nombre_limpio.lower()
                nombre_limpio = re.sub(r'_+', '_', nombre_limpio).strip('_')
                nombre_limpio = nombre_limpio[:50]
                
                if nombre_limpio:
                    nombre_base = nombre_limpio
            
            logger.debug(f"Nombre de archivo extraído: {nombre_base}")
        except (json.JSONDecodeError, AttributeError) as e:
            logger.warning(f"Error al extraer nombre de archivo: {e}. Usando nombre por defecto.")
        
        return nombre_base
    
    def save_agent_report(
        self,
        agent_name: str,
        content: str,
        attempt: int,
        status: str = None,
        **kwargs
    ) -> Tuple[bool, str]:
        """
        Guarda un reporte de agente con nombre consistente.
        
        Args:
            agent_name: Nombre del agente (ej: "testing", "sonarqube")
            content: Contenido del reporte
            attempt: Número de intento
            status: Estado opcional (ej: "PASSED", "FAILED")
            **kwargs: Argumentos adicionales para generate_report_filename
            
        Returns:
            Tuple (success, full_path)
        """
        filename = self.generate_report_filename(
            prefix=agent_name,
            attempt=attempt,
            status=status,
            **kwargs
        )
        return self.save_file(filename, content)
    
    def get_full_path(self, filename: str, subdirectory: str = None) -> str:
        """
        Obtiene la ruta completa de un archivo.
        
        Args:
            filename: Nombre del archivo
            subdirectory: Subdirectorio opcional
            
        Returns:
            Ruta completa del archivo
        """
        if subdirectory:
            return os.path.join(self.base_directory, subdirectory, filename)
        return os.path.join(self.base_directory, filename)
    
    def file_exists(self, filename: str, subdirectory: str = None) -> bool:
        """
        Verifica si un archivo existe.
        
        Args:
            filename: Nombre del archivo
            subdirectory: Subdirectorio opcional
            
        Returns:
            True si el archivo existe
        """
        full_path = self.get_full_path(filename, subdirectory)
        return os.path.exists(full_path)


# Instancia global del gestor de archivos
file_manager = FileManager()
