"""
Test para verificar que el agente ejecutor de pruebas funciona correctamente.
Simula diferentes escenarios: tests exitosos, fallidos y errores.
"""

import os
import sys
import tempfile
import shutil

# Añadir el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.state import AgentState
from agents.ejecutor_pruebas import ejecutor_pruebas_node
from config.settings import settings


def crear_archivos_test_typescript_exitoso(output_dir: str):
    """Crea archivos de test TypeScript que deberían pasar."""
    
    # Código de la calculadora
    codigo = """export class Calculator {
  add(a: number, b: number): number {
    return a + b;
  }
  
  subtract(a: number, b: number): number {
    return a - b;
  }
}
"""
    
    # Tests que deberían pasar
    tests = """import { describe, it, expect, beforeEach } from 'vitest';
import { Calculator } from './3_codificador_req1_debug0_sq0';

describe('Calculator', () => {
  let calculator: Calculator;

  beforeEach(() => {
    calculator = new Calculator();
  });

  describe('add', () => {
    it('should add two positive numbers', () => {
      expect(calculator.add(2, 3)).toBe(5);
    });

    it('should add negative numbers', () => {
      expect(calculator.add(-5, -3)).toBe(-8);
    });
  });

  describe('subtract', () => {
    it('should subtract two numbers', () => {
      expect(calculator.subtract(10, 4)).toBe(6);
    });
  });
});
"""
    
    with open(os.path.join(output_dir, '3_codificador_req1_debug0_sq0.ts'), 'w', encoding='utf-8') as f:
        f.write(codigo)
    
    with open(os.path.join(output_dir, 'unit_tests_req1_sq0.test.ts'), 'w', encoding='utf-8') as f:
        f.write(tests)


def crear_archivos_test_typescript_fallido(output_dir: str):
    """Crea archivos de test TypeScript que deberían fallar."""
    
    # Código con bug
    codigo = """export class Calculator {
  add(a: number, b: number): number {
    return a - b;  // Bug intencional: resta en lugar de suma
  }
  
  subtract(a: number, b: number): number {
    return a - b;
  }
}
"""
    
    # Tests que deberían fallar
    tests = """import { describe, it, expect, beforeEach } from 'vitest';
import { Calculator } from './3_codificador_req1_debug0_sq0';

describe('Calculator', () => {
  let calculator: Calculator;

  beforeEach(() => {
    calculator = new Calculator();
  });

  it('should add two numbers', () => {
    expect(calculator.add(2, 3)).toBe(5);  // Fallará porque add() hace resta
  });
});
"""
    
    with open(os.path.join(output_dir, '3_codificador_req1_debug0_sq0.ts'), 'w', encoding='utf-8') as f:
        f.write(codigo)
    
    with open(os.path.join(output_dir, 'unit_tests_req1_sq0.test.ts'), 'w', encoding='utf-8') as f:
        f.write(tests)


def crear_archivos_test_python_exitoso(output_dir: str):
    """Crea archivos de test Python que deberían pasar."""
    
    # Código Python
    codigo = """def factorial(n: int) -> int:
    if n < 0:
        raise ValueError("El factorial no está definido para números negativos")
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)
"""
    
    # Tests que deberían pasar
    tests = """import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Importar desde el archivo generado
exec(open('3_codificador_req1_debug0_sq0.py').read())

def test_factorial_base_cases():
    assert factorial(0) == 1
    assert factorial(1) == 1

def test_factorial_positive_numbers():
    assert factorial(5) == 120
    assert factorial(3) == 6

def test_factorial_negative_raises_error():
    with pytest.raises(ValueError):
        factorial(-1)
"""
    
    with open(os.path.join(output_dir, '3_codificador_req1_debug0_sq0.py'), 'w', encoding='utf-8') as f:
        f.write(codigo)
    
    with open(os.path.join(output_dir, 'test_unit_req1_sq0.py'), 'w', encoding='utf-8') as f:
        f.write(tests)


def test_ejecutor_typescript_exitoso():
    """Test 1: Verificar que el ejecutor detecta tests TypeScript exitosos."""
    print("\n" + "="*80)
    print("TEST 1: Tests TypeScript exitosos")
    print("="*80)
    
    # Crear directorio temporal
    temp_dir = tempfile.mkdtemp()
    original_output_dir = settings.OUTPUT_DIR
    
    try:
        settings.OUTPUT_DIR = temp_dir
        crear_archivos_test_typescript_exitoso(temp_dir)
        
        # Crear estado con el campo correcto: "lenguaje" en lugar de "language"
        state = AgentState(
            prompt_inicial="Crear calculadora",
            max_attempts=3,
            attempt_count=1,
            debug_attempt_count=0,
            max_debug_attempts=3,
            feedback_stakeholder="",
            requisito_clarificado="",
            requisitos_formales='{"lenguaje": "TypeScript", "descripcion": "Clase Calculator"}',
            codigo_generado="export class Calculator { ... }",
            traceback="",
            pruebas_superadas=False,
            sonarqube_issues="",
            sonarqube_passed=True,
            sonarqube_attempt_count=0,
            max_sonarqube_attempts=2,
            tests_unitarios_generados="",
            validado=False
        )
        
        # Ejecutar el nodo
        resultado = ejecutor_pruebas_node(state)
        
        # Verificaciones
        print(f"\n📊 Resultados:")
        print(f"   Pruebas superadas: {resultado['pruebas_superadas']}")
        print(f"   Debug attempt count: {resultado['debug_attempt_count']}")
        print(f"   Traceback: {resultado['traceback'][:100] if resultado['traceback'] else 'Ninguno'}")
        
        if resultado['pruebas_superadas']:
            print("\n✅ TEST PASADO: El ejecutor detectó correctamente tests exitosos")
            return True
        else:
            print("\n❌ TEST FALLIDO: El ejecutor no detectó tests exitosos")
            print(f"   Error: {resultado['traceback']}")
            return False
            
    finally:
        settings.OUTPUT_DIR = original_output_dir
        shutil.rmtree(temp_dir)


def test_ejecutor_typescript_fallido():
    """Test 2: Verificar que el ejecutor detecta tests TypeScript fallidos."""
    print("\n" + "="*80)
    print("TEST 2: Tests TypeScript fallidos (esperado)")
    print("="*80)
    
    temp_dir = tempfile.mkdtemp()
    original_output_dir = settings.OUTPUT_DIR
    
    try:
        settings.OUTPUT_DIR = temp_dir
        crear_archivos_test_typescript_fallido(temp_dir)
        
        state = AgentState(
            prompt_inicial="Crear calculadora",
            max_attempts=3,
            attempt_count=1,
            debug_attempt_count=0,
            max_debug_attempts=3,
            feedback_stakeholder="",
            requisito_clarificado="",
            requisitos_formales='{"lenguaje": "TypeScript", "descripcion": "Clase Calculator"}',
            codigo_generado="export class Calculator { ... }",
            traceback="",
            pruebas_superadas=False,
            sonarqube_issues="",
            sonarqube_passed=True,
            sonarqube_attempt_count=0,
            max_sonarqube_attempts=2,
            tests_unitarios_generados="",
            validado=False
        )
        
        resultado = ejecutor_pruebas_node(state)
        
        print(f"\n📊 Resultados:")
        print(f"   Pruebas superadas: {resultado['pruebas_superadas']}")
        print(f"   Debug attempt count: {resultado['debug_attempt_count']}")
        print(f"   Traceback presente: {len(resultado['traceback']) > 0}")
        
        if not resultado['pruebas_superadas'] and resultado['debug_attempt_count'] == 1:
            print("\n✅ TEST PASADO: El ejecutor detectó correctamente tests fallidos")
            return True
        else:
            print("\n❌ TEST FALLIDO: El ejecutor no detectó correctamente los fallos")
            return False
            
    finally:
        settings.OUTPUT_DIR = original_output_dir
        shutil.rmtree(temp_dir)


def test_ejecutor_python_exitoso():
    """Test 3: Verificar que el ejecutor maneja tests Python exitosos."""
    print("\n" + "="*80)
    print("TEST 3: Tests Python exitosos")
    print("="*80)
    
    temp_dir = tempfile.mkdtemp()
    original_output_dir = settings.OUTPUT_DIR
    
    try:
        settings.OUTPUT_DIR = temp_dir
        crear_archivos_test_python_exitoso(temp_dir)
        
        state = AgentState(
            prompt_inicial="Crear función factorial",
            max_attempts=3,
            attempt_count=1,
            debug_attempt_count=0,
            max_debug_attempts=3,
            feedback_stakeholder="",
            requisito_clarificado="",
            requisitos_formales='{"lenguaje": "Python", "descripcion": "Función factorial"}',
            codigo_generado="def factorial(n): ...",
            traceback="",
            pruebas_superadas=False,
            sonarqube_issues="",
            sonarqube_passed=True,
            sonarqube_attempt_count=0,
            max_sonarqube_attempts=2,
            tests_unitarios_generados="",
            validado=False
        )
        
        resultado = ejecutor_pruebas_node(state)
        
        print(f"\n📊 Resultados:")
        print(f"   Pruebas superadas: {resultado['pruebas_superadas']}")
        print(f"   Debug attempt count: {resultado['debug_attempt_count']}")
        print(f"   Traceback: {resultado['traceback'][:100] if resultado['traceback'] else 'Ninguno'}")
        
        if resultado['pruebas_superadas']:
            print("\n✅ TEST PASADO: El ejecutor manejó correctamente tests Python")
            return True
        else:
            print("\n❌ TEST FALLIDO: El ejecutor no manejó tests Python correctamente")
            print(f"   Error: {resultado['traceback']}")
            return False
            
    finally:
        settings.OUTPUT_DIR = original_output_dir
        shutil.rmtree(temp_dir)


def test_ejecutor_sin_archivo_tests():
    """Test 4: Verificar que el ejecutor maneja la ausencia de archivos de tests."""
    print("\n" + "="*80)
    print("TEST 4: Archivo de tests no encontrado")
    print("="*80)
    
    temp_dir = tempfile.mkdtemp()
    original_output_dir = settings.OUTPUT_DIR
    
    try:
        settings.OUTPUT_DIR = temp_dir
        # No crear ningún archivo
        
        state = AgentState(
            prompt_inicial="Test sin archivos",
            max_attempts=3,
            attempt_count=1,
            debug_attempt_count=0,
            max_debug_attempts=3,
            feedback_stakeholder="",
            requisito_clarificado="",
            requisitos_formales='{"lenguaje": "TypeScript"}',
            codigo_generado="export class Test {}",
            traceback="",
            pruebas_superadas=False,
            sonarqube_issues="",
            sonarqube_passed=True,
            sonarqube_attempt_count=0,
            max_sonarqube_attempts=2,
            tests_unitarios_generados="",
            validado=False
        )
        
        resultado = ejecutor_pruebas_node(state)
        
        print(f"\n📊 Resultados:")
        print(f"   Pruebas superadas: {resultado['pruebas_superadas']}")
        print(f"   Traceback: {resultado['traceback'][:100]}")
        
        if not resultado['pruebas_superadas'] and 'No se encontró' in resultado['traceback']:
            print("\n✅ TEST PASADO: El ejecutor manejó correctamente la ausencia de archivos")
            return True
        else:
            print("\n❌ TEST FALLIDO: El ejecutor no manejó correctamente la ausencia de archivos")
            return False
            
    finally:
        settings.OUTPUT_DIR = original_output_dir
        shutil.rmtree(temp_dir)


def main():
    """Ejecuta todos los tests del ejecutor de pruebas."""
    print("\n" + "█"*80)
    print("█" + " "*78 + "█")
    print("█" + " "*20 + "SUITE DE TESTS - EJECUTOR DE PRUEBAS" + " "*22 + "█")
    print("█" + " "*78 + "█")
    print("█"*80)
    
    resultados = []
    
    # Test 1: TypeScript exitoso
    try:
        resultados.append(("TypeScript Exitoso", test_ejecutor_typescript_exitoso()))
    except Exception as e:
        print(f"\n❌ ERROR en test TypeScript exitoso: {e}")
        resultados.append(("TypeScript Exitoso", False))
    
    # Test 2: TypeScript fallido
    try:
        resultados.append(("TypeScript Fallido", test_ejecutor_typescript_fallido()))
    except Exception as e:
        print(f"\n❌ ERROR en test TypeScript fallido: {e}")
        resultados.append(("TypeScript Fallido", False))
    
    # Test 3: Python exitoso
    try:
        resultados.append(("Python Exitoso", test_ejecutor_python_exitoso()))
    except Exception as e:
        print(f"\n❌ ERROR en test Python exitoso: {e}")
        resultados.append(("Python Exitoso", False))
    
    # Test 4: Sin archivos
    try:
        resultados.append(("Sin Archivos", test_ejecutor_sin_archivo_tests()))
    except Exception as e:
        print(f"\n❌ ERROR en test sin archivos: {e}")
        resultados.append(("Sin Archivos", False))
    
    # Resumen final
    print("\n" + "█"*80)
    print("█" + " "*78 + "█")
    print("█" + " "*30 + "RESUMEN FINAL" + " "*35 + "█")
    print("█" + " "*78 + "█")
    print("█"*80)
    print()
    
    tests_pasados = sum(1 for _, passed in resultados if passed)
    tests_totales = len(resultados)
    
    for nombre, passed in resultados:
        status = "✅ PASADO" if passed else "❌ FALLADO"
        print(f"   {status:12} - {nombre}")
    
    print()
    print(f"   Total: {tests_pasados}/{tests_totales} tests pasados")
    
    if tests_pasados == tests_totales:
        print("\n   🎉 ¡TODOS LOS TESTS PASARON!")
        print("   El ejecutor de pruebas funciona correctamente.")
    else:
        print(f"\n   ⚠️  {tests_totales - tests_pasados} test(s) fallaron")
        print("   Revisa los logs anteriores para más detalles.")
    
    print("\n" + "█"*80 + "\n")
    
    return tests_pasados == tests_totales


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
