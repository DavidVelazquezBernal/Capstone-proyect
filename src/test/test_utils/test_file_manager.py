import pytest
import os
import json
import tempfile
from unittest.mock import Mock, patch, mock_open
from utils.file_manager import FileManager


class TestFileManager:
    
    @pytest.fixture
    def temp_dir(self):
        """Fixture que crea un directorio temporal"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def file_manager(self, temp_dir):
        """Fixture que retorna un FileManager con directorio temporal"""
        return FileManager(base_directory=temp_dir)
    
    def test_file_manager_inicializa_con_directorio_base(self, temp_dir):
        """Verifica que FileManager inicializa con directorio base"""
        fm = FileManager(base_directory=temp_dir)
        assert fm.base_directory == temp_dir
    
    def test_file_manager_crea_directorio_si_no_existe(self):
        """Verifica que crea el directorio base si no existe"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = os.path.join(tmpdir, "new_dir")
            fm = FileManager(base_directory=test_dir)
            assert os.path.exists(test_dir)
    
    def test_save_file_guarda_contenido(self, file_manager, temp_dir):
        """Verifica que save_file guarda el contenido correctamente"""
        filename = "test.txt"
        content = "Hello, World!"
        
        success, full_path = file_manager.save_file(filename, content)
        
        assert success is True
        assert os.path.exists(full_path)
        with open(full_path, 'r', encoding='utf-8') as f:
            assert f.read() == content
    
    def test_save_file_con_subdirectorio(self, file_manager, temp_dir):
        """Verifica que save_file funciona con subdirectorios"""
        filename = "test.txt"
        content = "Test content"
        subdirectory = "subdir"
        
        success, full_path = file_manager.save_file(filename, content, subdirectory=subdirectory)
        
        assert success is True
        assert os.path.exists(full_path)
        assert subdirectory in full_path
    
    def test_generate_report_filename_basico(self, file_manager):
        """Verifica que genera nombres de archivo básicos"""
        filename = file_manager.generate_report_filename("testing", 1)
        assert "testing" in filename
        assert "req1" in filename
        assert filename.endswith(".txt")
    
    def test_generate_report_filename_con_debug_attempt(self, file_manager):
        """Verifica que incluye debug_attempt en el nombre"""
        filename = file_manager.generate_report_filename("testing", 1, debug_attempt=2)
        assert "debug2" in filename
    
    def test_generate_report_filename_con_sonarqube_attempt(self, file_manager):
        """Verifica que incluye sonarqube_attempt en el nombre"""
        filename = file_manager.generate_report_filename("sonarqube", 1, sonarqube_attempt=0)
        assert "sq0" in filename
    
    def test_generate_report_filename_con_status(self, file_manager):
        """Verifica que incluye status en el nombre"""
        filename = file_manager.generate_report_filename("testing", 1, status="PASSED")
        assert "PASSED" in filename
    
    def test_generate_report_filename_con_extension_personalizada(self, file_manager):
        """Verifica que usa extensión personalizada"""
        filename = file_manager.generate_report_filename("report", 1, extension="json")
        assert filename.endswith(".json")
    
    def test_generate_code_filename_python(self, file_manager):
        """Verifica que genera nombres para Python"""
        filename = file_manager.generate_code_filename("calculator", "python")
        assert filename == "calculator.py"
    
    def test_generate_code_filename_typescript(self, file_manager):
        """Verifica que genera nombres para TypeScript"""
        filename = file_manager.generate_code_filename("calculator", "typescript")
        assert filename == "calculator.ts"
    
    def test_generate_code_filename_javascript(self, file_manager):
        """Verifica que genera nombres para JavaScript"""
        filename = file_manager.generate_code_filename("calculator", "javascript")
        assert filename == "calculator.js"
    
    def test_generate_code_filename_test_python(self, file_manager):
        """Verifica que genera nombres de test para Python"""
        filename = file_manager.generate_code_filename("calculator", "python", is_test=True)
        assert filename == "test_calculator.py"
    
    def test_generate_code_filename_test_typescript(self, file_manager):
        """Verifica que genera nombres de test para TypeScript"""
        filename = file_manager.generate_code_filename("calculator", "typescript", is_test=True)
        assert filename == "calculator.test.ts"
    
    def test_detect_language_from_requirements_typescript(self):
        """Verifica que detecta TypeScript desde requisitos"""
        requisitos = '{"lenguaje_version": "TypeScript 5.0"}'
        lenguaje, extension = FileManager.detect_language_from_requirements(requisitos)
        assert lenguaje == "typescript"
        assert extension == ".ts"
    
    def test_detect_language_from_requirements_python(self):
        """Verifica que detecta Python desde requisitos"""
        requisitos = '{"lenguaje": "Python"}'
        lenguaje, extension = FileManager.detect_language_from_requirements(requisitos)
        assert lenguaje == "python"
        assert extension == ".py"
    
    def test_detect_language_from_requirements_javascript(self):
        """Verifica que detecta JavaScript desde requisitos"""
        requisitos = '{"lenguaje_version": "JavaScript ES6"}'
        lenguaje, extension = FileManager.detect_language_from_requirements(requisitos)
        assert lenguaje == "javascript"
        assert extension == ".js"
    
    def test_detect_language_from_requirements_default(self):
        """Verifica que usa Python por defecto"""
        requisitos = '{}'
        lenguaje, extension = FileManager.detect_language_from_requirements(requisitos)
        assert lenguaje == "python"
        assert extension == ".py"
    
    def test_clean_markdown_code_con_python(self):
        """Verifica que limpia bloques markdown de Python"""
        codigo = "```python\nprint('hello')\n```"
        resultado = FileManager.clean_markdown_code(codigo)
        assert resultado == "print('hello')"
        assert "```" not in resultado
    
    def test_clean_markdown_code_con_typescript(self):
        """Verifica que limpia bloques markdown de TypeScript"""
        codigo = "```typescript\nconsole.log('hello');\n```"
        resultado = FileManager.clean_markdown_code(codigo)
        assert resultado == "console.log('hello');"
        assert "```" not in resultado
    
    def test_clean_markdown_code_sin_marcadores(self):
        """Verifica que no modifica código sin marcadores"""
        codigo = "print('hello')"
        resultado = FileManager.clean_markdown_code(codigo)
        assert resultado == "print('hello')"
    
    def test_clean_markdown_code_con_lista(self):
        """Verifica que maneja listas de código"""
        codigo = ["line1", "line2", "line3"]
        resultado = FileManager.clean_markdown_code(codigo)
        assert "line1" in resultado
        assert "line2" in resultado
        assert "line3" in resultado
    
    def test_extract_filename_from_requirements_con_nombre_funcion(self):
        """Verifica que extrae nombre desde nombre_funcion"""
        requisitos = '{"nombre_funcion": "CalcularFactorial"}'
        nombre = FileManager.extract_filename_from_requirements(requisitos)
        assert nombre == "calcular_factorial"
    
    def test_extract_filename_from_requirements_con_titulo(self):
        """Verifica que extrae nombre desde titulo"""
        requisitos = '{"titulo": "Sistema de Login"}'
        nombre = FileManager.extract_filename_from_requirements(requisitos)
        assert "sistema" in nombre.lower()
        assert "login" in nombre.lower()
    
    def test_extract_filename_from_requirements_convierte_a_snake_case(self):
        """Verifica que convierte a snake_case"""
        requisitos = '{"nombre_funcion": "MiFuncionEspecial"}'
        nombre = FileManager.extract_filename_from_requirements(requisitos)
        assert "_" in nombre
        assert nombre.islower()
    
    def test_extract_filename_from_requirements_default(self):
        """Verifica que usa nombre por defecto si no hay candidatos"""
        requisitos = '{}'
        nombre = FileManager.extract_filename_from_requirements(requisitos)
        assert nombre == "codigo_generado"
    
    def test_save_agent_report(self, file_manager, temp_dir):
        """Verifica que save_agent_report funciona correctamente"""
        content = "Test report content"
        success, full_path = file_manager.save_agent_report(
            "testing", content, attempt=1, status="PASSED"
        )
        
        assert success is True
        assert os.path.exists(full_path)
        assert "testing" in full_path
    
    def test_get_full_path_sin_subdirectorio(self, file_manager, temp_dir):
        """Verifica que get_full_path retorna ruta correcta"""
        filename = "test.txt"
        full_path = file_manager.get_full_path(filename)
        assert full_path == os.path.join(temp_dir, filename)
    
    def test_get_full_path_con_subdirectorio(self, file_manager, temp_dir):
        """Verifica que get_full_path incluye subdirectorio"""
        filename = "test.txt"
        subdirectory = "subdir"
        full_path = file_manager.get_full_path(filename, subdirectory)
        assert full_path == os.path.join(temp_dir, subdirectory, filename)
    
    def test_file_exists_retorna_false_para_archivo_inexistente(self, file_manager):
        """Verifica que file_exists retorna False para archivo inexistente"""
        assert file_manager.file_exists("nonexistent.txt") is False
    
    def test_file_exists_retorna_true_para_archivo_existente(self, file_manager):
        """Verifica que file_exists retorna True para archivo existente"""
        filename = "test.txt"
        file_manager.save_file(filename, "content")
        assert file_manager.file_exists(filename) is True
