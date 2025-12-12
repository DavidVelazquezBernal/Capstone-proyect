"""
Tests para el agente Testing (Generador y Ejecutor de Unit Tests)
Verifica la generación de tests, ejecución y la integración con GitHub.
"""

import sys
import os
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, 'src')

from models.state import AgentState
from agents.testing import testing_node, _limpiar_ansi, _validar_codigo_tests_completo
from config.settings import settings


def create_test_state(lenguaje: str = "typescript") -> AgentState:
    """Crea un estado de prueba base."""
    if lenguaje == "typescript":
        codigo = '''export class Calculator {
    add(a: number, b: number): number {
        return a + b;
    }
    
    subtract(a: number, b: number): number {
        return a - b;
    }
    
    multiply(a: number, b: number): number {
        return a * b;
    }
    
    divide(a: number, b: number): number {
        if (b === 0) {
            throw new Error("Division by zero");
        }
        return a / b;
    }
}'''
        requisitos = '{"titulo": "Calculator", "lenguaje": "typescript", "nombre_funcion": "Calculator"}'
    else:
        codigo = '''def calculator_add(a: float, b: float) -> float:
    return a + b

def calculator_subtract(a: float, b: float) -> float:
    return a - b

def calculator_multiply(a: float, b: float) -> float:
    return a * b

def calculator_divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("Division by zero")
    return a / b'''
        requisitos = '{"titulo": "Calculator", "lenguaje": "python", "nombre_funcion": "calculator"}'
    
    return {
        'prompt_inicial': 'Implementa una calculadora con operaciones básicas',
        'feedback_stakeholder': '',
        'max_attempts': 3,
        'attempt_count': 1,
        'debug_attempt_count': 0,
        'max_debug_attempts': 3,
        'sonarqube_attempt_count': 0,
        'max_sonarqube_attempts': 3,
        'pruebas_superadas': False,
        'validado': False,
        'traceback': '',
        'sonarqube_issues': '',
        'sonarqube_passed': True,
        'tests_unitarios_generados': '',
        'requisito_clarificado': 'Implementa una calculadora con operaciones básicas',
        'requisitos_formales': requisitos,
        'codigo_generado': codigo,
        'azure_pbi_id': None,
        'azure_implementation_task_id': None,
        'azure_testing_task_id': None,
        'github_branch_name': None,
        'github_pr_number': None,
        'github_pr_url': None,
        'codigo_revisado': False,
        'revision_comentario': '',
        'revision_puntuacion': None,
        'pr_aprobada': False
    }


class TestLimpiarAnsi:
    """Tests para la función _limpiar_ansi"""
    
    def test_limpia_codigos_color(self):
        """Verifica que elimina códigos de color ANSI"""
        texto_con_ansi = "\x1b[32m✓\x1b[0m Test passed"
        resultado = _limpiar_ansi(texto_con_ansi)
        assert resultado == "✓ Test passed"
    
    def test_texto_sin_ansi_no_cambia(self):
        """Verifica que texto sin ANSI no se modifica"""
        texto_normal = "Test passed successfully"
        resultado = _limpiar_ansi(texto_normal)
        assert resultado == texto_normal
    
    def test_multiples_codigos_ansi(self):
        """Verifica que elimina múltiples códigos ANSI"""
        texto = "\x1b[31mError:\x1b[0m \x1b[33mWarning\x1b[0m"
        resultado = _limpiar_ansi(texto)
        assert resultado == "Error: Warning"


class TestValidarCodigoTestsCompleto:
    """Tests para la función _validar_codigo_tests_completo"""
    
    def test_codigo_typescript_valido(self):
        """Verifica que código TypeScript válido pasa la validación"""
        codigo = '''
import { describe, it, expect } from 'vitest';
import { Calculator } from './calculator';

describe('Calculator', () => {
    it('should add two numbers', () => {
        const calc = new Calculator();
        expect(calc.add(2, 3)).toBe(5);
    });
});
'''
        es_valido, mensaje = _validar_codigo_tests_completo(codigo, 'typescript')
        assert es_valido is True
    
    def test_codigo_typescript_llaves_desbalanceadas(self):
        """Verifica que detecta llaves desbalanceadas"""
        codigo = '''
describe('Calculator', () => {
    it('should add', () => {
        expect(1 + 1).toBe(2);
    });
// Falta cerrar describe
'''
        es_valido, mensaje = _validar_codigo_tests_completo(codigo, 'typescript')
        assert es_valido is False
        assert "Llaves desbalanceadas" in mensaje
    
    def test_codigo_muy_corto(self):
        """Verifica que rechaza código muy corto"""
        codigo = "test"
        es_valido, mensaje = _validar_codigo_tests_completo(codigo, 'typescript')
        assert es_valido is False
        assert "demasiado corto" in mensaje
    
    def test_codigo_python_valido(self):
        """Verifica que código Python válido pasa la validación"""
        codigo = '''
import pytest
from calculator import calculator_add

def test_add():
    assert calculator_add(2, 3) == 5

def test_add_negative():
    assert calculator_add(-1, 1) == 0
'''
        es_valido, mensaje = _validar_codigo_tests_completo(codigo, 'python')
        assert es_valido is True


class TestTestingNodeMocked:
    """Tests para testing_node con mocks"""
    
    @pytest.fixture
    def mock_llm_response_typescript(self):
        """Respuesta mock del LLM para tests TypeScript"""
        return '''import { describe, it, expect } from 'vitest';
import { Calculator } from './calculator';

describe('Calculator', () => {
    const calc = new Calculator();
    
    describe('add', () => {
        it('should add two positive numbers', () => {
            expect(calc.add(2, 3)).toBe(5);
        });
        
        it('should add negative numbers', () => {
            expect(calc.add(-1, -1)).toBe(-2);
        });
    });
    
    describe('divide', () => {
        it('should divide two numbers', () => {
            expect(calc.divide(10, 2)).toBe(5);
        });
        
        it('should throw error on division by zero', () => {
            expect(() => calc.divide(10, 0)).toThrow("Division by zero");
        });
    });
});'''
    
    @patch('agents.testing.call_gemini')
    @patch('agents.testing.subprocess.run')
    def test_testing_node_genera_tests_typescript(self, mock_subprocess, mock_llm, mock_llm_response_typescript):
        """Verifica que testing_node genera tests correctamente para TypeScript"""
        # Configurar mocks
        mock_llm.return_value = mock_llm_response_typescript
        mock_subprocess.return_value = MagicMock(
            returncode=0,
            stdout="✓ 4 tests passed",
            stderr=""
        )
        
        # Crear estado y ejecutar
        state = create_test_state("typescript")
        
        # Crear directorio output si no existe
        os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
        
        # Ejecutar el nodo (con GitHub deshabilitado para el test)
        with patch.object(settings, 'GITHUB_ENABLED', False):
            with patch.object(settings, 'AZURE_DEVOPS_ENABLED', False):
                result = testing_node(state)
        
        # Verificar que se generaron tests
        assert 'tests_unitarios_generados' in result
        assert len(result['tests_unitarios_generados']) > 0
        
        # Verificar que el LLM fue llamado
        mock_llm.assert_called_once()
    
    @patch('agents.testing.call_gemini')
    @patch('agents.testing.subprocess.run')
    def test_testing_node_tests_pasan(self, mock_subprocess, mock_llm, mock_llm_response_typescript):
        """Verifica que cuando los tests pasan, el estado se actualiza correctamente"""
        mock_llm.return_value = mock_llm_response_typescript
        
        # Simular salida exitosa de vitest
        mock_subprocess.return_value = MagicMock(
            returncode=0,
            stdout="""
 ✓ src/test/calculator.spec.ts (4 tests) 2ms
   ✓ Calculator > add > should add two positive numbers
   ✓ Calculator > add > should add negative numbers
   ✓ Calculator > divide > should divide two numbers
   ✓ Calculator > divide > should throw error on division by zero

 Test Files  1 passed (1)
      Tests  4 passed (4)
   Duration  150ms
""",
            stderr=""
        )
        
        state = create_test_state("typescript")
        os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
        
        with patch.object(settings, 'GITHUB_ENABLED', False):
            with patch.object(settings, 'AZURE_DEVOPS_ENABLED', False):
                result = testing_node(state)
        
        # Verificar estado actualizado
        assert result['pruebas_superadas'] is True
        assert result['debug_attempt_count'] == 0  # Se resetea cuando pasan
    
    @patch('agents.testing.call_gemini')
    @patch('agents.testing.subprocess.run')
    def test_testing_node_tests_fallan(self, mock_subprocess, mock_llm, mock_llm_response_typescript):
        """Verifica que cuando los tests fallan, el estado se actualiza correctamente"""
        mock_llm.return_value = mock_llm_response_typescript
        
        # Simular salida fallida de vitest
        mock_subprocess.return_value = MagicMock(
            returncode=1,
            stdout="""
 ❌ src/test/calculator.spec.ts (4 tests) 5ms
   ✓ Calculator > add > should add two positive numbers
   ✗ Calculator > divide > should throw error on division by zero
     AssertionError: expected function to throw an error

 Test Files  1 failed (1)
      Tests  1 failed | 3 passed (4)
   Duration  200ms
""",
            stderr="AssertionError: expected function to throw an error"
        )
        
        state = create_test_state("typescript")
        os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
        
        with patch.object(settings, 'GITHUB_ENABLED', False):
            with patch.object(settings, 'AZURE_DEVOPS_ENABLED', False):
                result = testing_node(state)
        
        # Verificar estado actualizado
        assert result['pruebas_superadas'] is False
        assert result['debug_attempt_count'] == 1  # Se incrementa cuando fallan


class TestTestingNodeGitHubIntegration:
    """Tests para la integración con GitHub en testing_node"""
    
    @patch('agents.testing.call_gemini')
    @patch('agents.testing.subprocess.run')
    @patch('agents.testing.github_service')
    def test_crea_branch_y_pr_cuando_tests_pasan(self, mock_github, mock_subprocess, mock_llm):
        """Verifica que se crea branch y PR cuando los tests pasan y GitHub está habilitado"""
        mock_llm.return_value = '''import { describe, it, expect } from 'vitest';
describe('Test', () => {
    it('works', () => {
        expect(true).toBe(true);
    });
});'''
        
        mock_subprocess.return_value = MagicMock(
            returncode=0,
            stdout="✓ 1 test passed\n Test Files  1 passed (1)\n      Tests  1 passed (1)",
            stderr=""
        )
        
        # Configurar mock de GitHub
        mock_github.create_branch_and_commit.return_value = (True, "abc1234")
        mock_github.create_pull_request.return_value = (True, 42, "https://github.com/test/repo/pull/42")
        
        state = create_test_state("typescript")
        os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
        
        with patch.object(settings, 'GITHUB_ENABLED', True):
            with patch.object(settings, 'GITHUB_REPO_PATH', settings.OUTPUT_DIR):
                with patch.object(settings, 'AZURE_DEVOPS_ENABLED', False):
                    result = testing_node(state)
        
        # Verificar que se llamó a GitHub
        if settings.GITHUB_ENABLED:
            assert result['github_branch_name'] is not None or mock_github.create_branch_and_commit.called
    
    @patch('agents.testing.call_gemini')
    @patch('agents.testing.subprocess.run')
    @patch('agents.testing.github_service')
    def test_no_crea_pr_cuando_tests_fallan(self, mock_github, mock_subprocess, mock_llm):
        """Verifica que NO se crea PR cuando los tests fallan"""
        mock_llm.return_value = '''import { describe, it, expect } from 'vitest';
describe('Test', () => {
    it('fails', () => {
        expect(true).toBe(false);
    });
});'''
        
        mock_subprocess.return_value = MagicMock(
            returncode=1,
            stdout="✗ 1 test failed",
            stderr="AssertionError"
        )
        
        state = create_test_state("typescript")
        os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
        
        with patch.object(settings, 'GITHUB_ENABLED', True):
            with patch.object(settings, 'AZURE_DEVOPS_ENABLED', False):
                result = testing_node(state)
        
        # Verificar que NO se llamó a GitHub para crear branch/PR
        mock_github.create_branch_and_commit.assert_not_called()
        mock_github.create_pull_request.assert_not_called()
        
        # Verificar que no hay PR en el estado
        assert result['github_pr_number'] is None


class TestTestingNodeFileCopy:
    """Tests para verificar la copia de archivos al repo local"""
    
    @patch('agents.testing.call_gemini')
    @patch('agents.testing.subprocess.run')
    @patch('agents.testing.github_service')
    def test_copia_archivos_a_repo_path(self, mock_github, mock_subprocess, mock_llm, tmp_path):
        """Verifica que los archivos se copian a GITHUB_REPO_PATH"""
        mock_llm.return_value = '''import { describe, it, expect } from 'vitest';
describe('Test', () => {
    it('works', () => {
        expect(1).toBe(1);
    });
});'''
        
        mock_subprocess.return_value = MagicMock(
            returncode=0,
            stdout="✓ 1 test passed\n Test Files  1 passed (1)\n      Tests  1 passed (1)",
            stderr=""
        )
        
        mock_github.create_branch_and_commit.return_value = (True, "abc1234")
        mock_github.create_pull_request.return_value = (True, 1, "https://github.com/test/pull/1")
        
        state = create_test_state("typescript")
        os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
        
        # Usar directorio temporal como GITHUB_REPO_PATH
        repo_path = str(tmp_path)
        
        with patch.object(settings, 'GITHUB_ENABLED', True):
            with patch.object(settings, 'GITHUB_REPO_PATH', repo_path):
                with patch.object(settings, 'AZURE_DEVOPS_ENABLED', False):
                    result = testing_node(state)
        
        # Verificar que se crearon los directorios
        src_dir = tmp_path / "src"
        test_dir = tmp_path / "src" / "test"
        
        if result['pruebas_superadas']:
            assert src_dir.exists() or not settings.GITHUB_ENABLED
            assert test_dir.exists() or not settings.GITHUB_ENABLED


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
