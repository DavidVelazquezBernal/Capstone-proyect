"""
Test para verificar que el mock del LLM genera código corregido en la segunda iteración.
"""

import sys
from pathlib import Path

# Añadir src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from llm.mock_responses import get_mock_response


def test_desarrollador_primera_vs_segunda_iteracion():
    """Verifica que el Desarrollador genera código diferente en primera y segunda iteración"""
    
    print("\n" + "=" * 80)
    print("🧪 TEST: Mock del Desarrollador - Primera vs Segunda Iteración")
    print("=" * 80)
    
    # Simular primera ejecución (sin feedback de SonarQube)
    prompt_desarrollador = "Eres un desarrollador experto. Codifica la solución."
    contexto_primera_vez = """
Requisitos Formales (JSON): {
  "objetivo_funcional": "Implementar una función sumar",
  "lenguaje_version": "TypeScript 5.x",
  "nombre_funcion": "sumar"
}
"""
    
    print("\n📝 Primera Iteración (sin feedback de SonarQube):")
    print("-" * 80)
    codigo_v1 = get_mock_response(prompt_desarrollador, contexto_primera_vez)
    print(codigo_v1)
    print("-" * 80)
    
    # Simular segunda ejecución (con feedback de SonarQube)
    contexto_con_sonarqube = """
Requisitos Formales (JSON): {
  "objetivo_funcional": "Implementar una función sumar",
  "lenguaje_version": "TypeScript 5.x",
  "nombre_funcion": "sumar"
}

Instrucciones de corrección de calidad (SonarQube):
El código debe manejar casos edge como NaN e Infinity.
Agregar validaciones adicionales para evitar bugs.

Código anterior a corregir:
export function sumar(a: number, b: number): number {
    if (typeof a !== 'number' || typeof b !== 'number') {
        throw new Error('Ambos argumentos deben ser números');
    }
    return Math.round((a + b) * 1e10) / 1e10;
}
"""
    
    print("\n📝 Segunda Iteración (con feedback de SonarQube):")
    print("-" * 80)
    codigo_v2 = get_mock_response(prompt_desarrollador, contexto_con_sonarqube)
    print(codigo_v2)
    print("-" * 80)
    
    # Verificaciones
    print("\n✅ VERIFICACIONES:")
    print("-" * 80)
    
    # 1. El código debe ser diferente
    assert codigo_v1 != codigo_v2, "El código de la segunda iteración debe ser diferente"
    print("✓ El código cambió entre iteraciones")
    
    # 2. La segunda versión debe tener validaciones adicionales
    assert "isNaN" in codigo_v2 or "NaN" in codigo_v2, "La segunda versión debe validar NaN"
    print("✓ La segunda versión valida NaN")
    
    assert "isFinite" in codigo_v2 or "Infinity" in codigo_v2 or "isinf" in codigo_v2, "La segunda versión debe validar Infinity"
    print("✓ La segunda versión valida Infinity")
    
    # 3. La segunda versión debe tener más líneas (más completa)
    lineas_v1 = len(codigo_v1.split('\n'))
    lineas_v2 = len(codigo_v2.split('\n'))
    assert lineas_v2 > lineas_v1, "La segunda versión debe ser más completa"
    print(f"✓ La segunda versión es más completa ({lineas_v1} líneas → {lineas_v2} líneas)")
    
    # 4. Ambas versiones deben exportar la función
    assert "export function sumar" in codigo_v1, "Primera versión debe exportar la función"
    assert "export function sumar" in codigo_v2, "Segunda versión debe exportar la función"
    print("✓ Ambas versiones exportan correctamente la función")
    
    print("-" * 80)
    print("\n✅ TODOS LOS TESTS PASARON")
    print("=" * 80)
    print("\n📋 Comportamiento del Mock:")
    print("   ✓ Primera ejecución: Genera código básico (puede tener bugs menores)")
    print("   ✓ Segunda ejecución: Genera código corregido con validaciones adicionales")
    print("   ✓ Detecta contexto de SonarQube automáticamente")
    print("=" * 80)


def test_python_tambien():
    """Verifica que también funciona para Python"""
    
    print("\n" + "=" * 80)
    print("🧪 TEST EXTRA: Mock del Desarrollador Python")
    print("=" * 80)
    
    prompt = "Eres un desarrollador experto. Codifica la solución."
    
    # Primera vez
    contexto_1 = "Requisitos: función sumar en Python 3.12"
    codigo_py_v1 = get_mock_response(prompt, contexto_1)
    
    # Segunda vez con SonarQube
    contexto_2 = """
Requisitos: función sumar en Python 3.12

Instrucciones de corrección de calidad (SonarQube):
Agregar validaciones para NaN e Infinity.
"""
    codigo_py_v2 = get_mock_response(prompt, contexto_2)
    
    print("\n📝 Python - Primera versión:")
    print(codigo_py_v1[:200] + "...")
    
    print("\n📝 Python - Segunda versión (con SonarQube):")
    print(codigo_py_v2[:200] + "...")
    
    assert codigo_py_v1 != codigo_py_v2
    assert "isnan" in codigo_py_v2 or "NaN" in codigo_py_v2
    assert "isinf" in codigo_py_v2 or "Infinity" in codigo_py_v2
    
    print("\n✅ También funciona correctamente para Python")
    print("=" * 80)


if __name__ == "__main__":
    test_desarrollador_primera_vs_segunda_iteracion()
    test_python_tambien()
