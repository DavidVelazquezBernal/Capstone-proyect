import pytest
import json
from unittest.mock import Mock, patch, mock_open
from tools.file_utils import (
    guardar_fichero_texto,
    detectar_lenguaje_y_extension,
    limpiar_codigo_markdown,
    extraer_nombre_archivo
)


class TestFileUtils:
    
    def test_guardar_fichero_texto_exitoso(self):
        with patch('tools.file_utils.FileManager') as MockFileManager:
            mock_instance = MockFileManager.return_value
            mock_instance.save_file.return_value = (True, '/path/to/file.txt')
            
            result = guardar_fichero_texto('test.txt', 'contenido de prueba')
            
            assert result is True
    
    def test_guardar_fichero_texto_con_directorio(self):
        with patch('tools.file_utils.FileManager') as MockFileManager:
            mock_instance = MockFileManager.return_value
            mock_instance.save_file.return_value = (True, '/custom/path/test.txt')
            
            result = guardar_fichero_texto('test.txt', 'contenido', directorio='/custom/path')
            
            assert result is True
            MockFileManager.assert_called_with(base_directory='/custom/path')
    
    def test_guardar_fichero_texto_falla(self):
        with patch('tools.file_utils._file_manager') as mock_file_manager:
            mock_file_manager.save_file.return_value = (False, None)
            
            result = guardar_fichero_texto('test.txt', 'contenido')
            
            assert result is False
    
    def test_detectar_lenguaje_python(self):
        requisitos = json.dumps({
            'lenguaje_programacion': 'python',
            'objetivo_funcional': 'Test'
        })
        
        with patch('tools.file_utils.FileManager.detect_language_from_requirements') as mock_detect:
            mock_detect.return_value = ('python', '.py')
            
            lenguaje, extension, patron = detectar_lenguaje_y_extension(requisitos)
            
            assert lenguaje == 'python'
            assert extension == '.py'
            assert patron == 'UNUSED'
    
    def test_detectar_lenguaje_typescript(self):
        requisitos = json.dumps({
            'lenguaje_programacion': 'typescript',
            'objetivo_funcional': 'Test'
        })
        
        with patch('tools.file_utils.FileManager.detect_language_from_requirements') as mock_detect:
            mock_detect.return_value = ('typescript', '.ts')
            
            lenguaje, extension, patron = detectar_lenguaje_y_extension(requisitos)
            
            assert lenguaje == 'typescript'
            assert extension == '.ts'
    
    def test_detectar_lenguaje_javascript(self):
        requisitos = json.dumps({
            'lenguaje_programacion': 'javascript',
            'objetivo_funcional': 'Test'
        })
        
        with patch('tools.file_utils.FileManager.detect_language_from_requirements') as mock_detect:
            mock_detect.return_value = ('javascript', '.js')
            
            lenguaje, extension, patron = detectar_lenguaje_y_extension(requisitos)
            
            assert lenguaje == 'javascript'
            assert extension == '.js'
    
    def test_limpiar_codigo_markdown_python(self):
        codigo_con_markdown = '''```python
def suma(a, b):
    return a + b
```'''
        
        with patch('tools.file_utils.FileManager.clean_markdown_code') as mock_clean:
            mock_clean.return_value = 'def suma(a, b):\n    return a + b'
            
            resultado = limpiar_codigo_markdown(codigo_con_markdown)
            
            assert '```' not in resultado
            assert 'def suma(a, b):' in resultado
    
    def test_limpiar_codigo_markdown_typescript(self):
        codigo_con_markdown = '''```typescript
function suma(a: number, b: number): number {
    return a + b;
}
```'''
        
        with patch('tools.file_utils.FileManager.clean_markdown_code') as mock_clean:
            mock_clean.return_value = 'function suma(a: number, b: number): number {\n    return a + b;\n}'
            
            resultado = limpiar_codigo_markdown(codigo_con_markdown)
            
            assert '```' not in resultado
            assert 'function suma' in resultado
    
    def test_limpiar_codigo_sin_markdown(self):
        codigo_limpio = 'def test(): pass'
        
        with patch('tools.file_utils.FileManager.clean_markdown_code') as mock_clean:
            mock_clean.return_value = codigo_limpio
            
            resultado = limpiar_codigo_markdown(codigo_limpio)
            
            assert resultado == codigo_limpio
    
    def test_extraer_nombre_archivo_con_nombre_funcion(self):
        requisitos = json.dumps({
            'nombre_funcion': 'calcular_promedio',
            'objetivo_funcional': 'Calcular promedio'
        })
        
        with patch('tools.file_utils.FileManager.extract_filename_from_requirements') as mock_extract:
            mock_extract.return_value = 'calcular_promedio'
            
            nombre = extraer_nombre_archivo(requisitos)
            
            assert nombre == 'calcular_promedio'
    
    def test_extraer_nombre_archivo_con_titulo(self):
        requisitos = json.dumps({
            'titulo': 'Validador de Email',
            'objetivo_funcional': 'Validar emails'
        })
        
        with patch('tools.file_utils.FileManager.extract_filename_from_requirements') as mock_extract:
            mock_extract.return_value = 'validador_de_email'
            
            nombre = extraer_nombre_archivo(requisitos)
            
            assert nombre == 'validador_de_email'
    
    def test_extraer_nombre_archivo_con_objetivo(self):
        requisitos = json.dumps({
            'objetivo_funcional': 'Procesar Datos JSON'
        })
        
        with patch('tools.file_utils.FileManager.extract_filename_from_requirements') as mock_extract:
            mock_extract.return_value = 'procesar_datos_json'
            
            nombre = extraer_nombre_archivo(requisitos)
            
            assert nombre == 'procesar_datos_json'
    
    def test_extraer_nombre_archivo_fallback(self):
        requisitos = json.dumps({})
        
        with patch('tools.file_utils.FileManager.extract_filename_from_requirements') as mock_extract:
            mock_extract.return_value = 'codigo'
            
            nombre = extraer_nombre_archivo(requisitos)
            
            assert nombre == 'codigo'
