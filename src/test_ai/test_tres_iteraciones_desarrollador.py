"""
Test del flujo completo con tres iteraciones del desarrollador:
1. Primera versión: Bug de comparación (!= vs !==) → SonarQube rechaza
2. Segunda versión: Bug lógico (resta en lugar de suma) → Tests fallan
3. Tercera versión: Código correcto → Todo pasa
"""

import sys
from pathlib import Path

# Añadir src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm.mock_responses import get_mock_response


def test_tres_iteraciones_desarrollador():
    """Verifica las tres versiones del código generado por el desarrollador"""
    
    print("\n" + "=" * 80)
    print("🧪 TEST: Tres Iteraciones del Desarrollador en Mock")
    print("=" * 80)
    
    prompt_dev = "Eres un desarrollador experto. Codifica la solución."
    
    # ========================================================================
    # ITERACIÓN 1: Primera versión (sin feedback) - Bug de comparación Y bug lógico
    # ========================================================================
    print("\n📝 ITERACIÓN 1: Código inicial (sin feedback)")
    print("-" * 80)
    
    contexto_1 = """
Requisitos Formales (JSON): {
  "objetivo_funcional": "Implementar una función sumar",
  "lenguaje_version": "TypeScript 5.x"
}
"""
    
    codigo_v1 = get_mock_response(prompt_dev, contexto_1)
    print(codigo_v1)
    print("-" * 80)
    
    # Verificar que tiene ambos bugs
    assert "!=" in codigo_v1 and "!==" not in codigo_v1, "V1 debe tener bug de comparación (!=)"
    assert "a - b" in codigo_v1, "V1 debe tener bug lógico (resta en lugar de suma)"
    print("✅ V1: Tiene bug de comparación (!= en lugar de !==)")
    print("✅ V1: Tiene bug lógico (a - b en lugar de a + b)")
    print("📊 V1 será rechazada por SonarQube (BUG de comparación detectado)")
    print("📊 Si pasara SonarQube, fallaría en tests (bug lógico)")
    
    # ========================================================================
    # ITERACIÓN 2: Con feedback de SonarQube - Bug lógico
    # ========================================================================
    print("\n📝 ITERACIÓN 2: Después de corrección de SonarQube")
    print("-" * 80)
    
    contexto_2 = """
Requisitos Formales (JSON): {
  "objetivo_funcional": "Implementar una función sumar",
  "lenguaje_version": "TypeScript 5.x"
}

Instrucciones de corrección de calidad (SonarQube):
Usar '!==' en lugar de '!=' para comparación estricta.
Agregar validaciones adicionales.

Código anterior a corregir:
export function sumar(a: number, b: number): number {
    if (typeof a != 'number' || typeof b != 'number') {
        throw new Error('Ambos argumentos deben ser números');
    }
    return Math.round((a + b) * 1e10) / 1e10;
}
"""
    
    codigo_v2 = get_mock_response(prompt_dev, contexto_2)
    print(codigo_v2)
    print("-" * 80)
    
    # Verificar que corrigió el bug de comparación pero tiene bug lógico
    assert "!==" in codigo_v2, "V2 debe usar comparación estricta (!==)"
    assert "a - b" in codigo_v2, "V2 debe tener bug lógico (resta en lugar de suma)"
    assert "Number.isNaN" in codigo_v2, "V2 debe tener validación de NaN"
    assert "Number.isFinite" in codigo_v2, "V2 debe tener validación de Infinity"
    print("✅ V2: Bug de comparación corregido (!==)")
    print("✅ V2: Validaciones adicionales agregadas")
    print("❌ V2: Tiene bug lógico (a - b en lugar de a + b)")
    print("📊 V2 pasará SonarQube pero FALLARÁ en tests unitarios")
    
    # ========================================================================
    # ITERACIÓN 3: Con feedback de tests fallidos - Código correcto
    # ========================================================================
    print("\n📝 ITERACIÓN 3: Después de corrección de tests")
    print("-" * 80)
    
    contexto_3 = """
Requisitos Formales (JSON): {
  "objetivo_funcional": "Implementar una función sumar",
  "lenguaje_version": "TypeScript 5.x"
}

Traceback para corrección de errores de ejecución:
AssertionError: Expected 5 but got -1
Test failed: sumar(2, 3) should return 5

La función está restando en lugar de sumar.

Código anterior a corregir:
export function sumar(a: number, b: number): number {
    if (typeof a !== 'number' || typeof b !== 'number') {
        throw new Error('Ambos argumentos deben ser números');
    }
    
    if (Number.isNaN(a) || Number.isNaN(b)) {
        throw new Error('Los argumentos no pueden ser NaN');
    }
    
    if (!Number.isFinite(a) || !Number.isFinite(b)) {
        throw new Error('Los argumentos deben ser números finitos');
    }
    
    const resultado = a - b;  // BUG: Debería ser a + b
    
    return Math.round(resultado * 1e10) / 1e10;
}
"""
    
    codigo_v3 = get_mock_response(prompt_dev, contexto_3)
    print(codigo_v3)
    print("-" * 80)
    
    # Verificar que el código final es correcto
    assert "!==" in codigo_v3, "V3 debe usar comparación estricta (!==)"
    assert "a + b" in codigo_v3, "V3 debe sumar correctamente"
    assert "Number.isNaN" in codigo_v3, "V3 debe mantener validación de NaN"
    assert "Number.isFinite" in codigo_v3, "V3 debe mantener validación de Infinity"
    assert "a - b" not in codigo_v3 or "a + b" in codigo_v3, "V3 NO debe restar"
    print("✅ V3: Bug de comparación corregido (!==)")
    print("✅ V3: Validaciones completas")
    print("✅ V3: Bug lógico corregido (a + b)")
    print("📊 V3 pasará SonarQube Y los tests unitarios")
    
    # ========================================================================
    # RESUMEN
    # ========================================================================
    print("\n" + "=" * 80)
    print("✅ TEST PASADO: Las tres iteraciones funcionan correctamente")
    print("=" * 80)
    
    print("\n📋 RESUMEN DEL FLUJO:")
    print("   1️⃣ Primera iteración:")
    print("      - Bug 1: Comparación no estricta (!=)")
    print("      - Bug 2: Lógica incorrecta (a - b)")
    print("      - Resultado: SonarQube RECHAZA (detecta bug de comparación)")
    print()
    print("   2️⃣ Segunda iteración:")
    print("      - Corrección: Usa !== (pasa SonarQube)")
    print("      - Bug persistente: Lógica incorrecta (resta en lugar de suma)")
    print("      - Resultado: SonarQube PASA pero Tests FALLAN")
    print()
    print("   3️⃣ Tercera iteración:")
    print("      - Corrección: Lógica correcta (suma)")
    print("      - Resultado: TODO PASA ✅")
    print("=" * 80)


def test_python_tambien():
    """Verifica que también funciona para Python"""
    
    print("\n" + "=" * 80)
    print("🧪 TEST EXTRA: Tres Iteraciones para Python")
    print("=" * 80)
    
    prompt = "Eres un desarrollador experto. Codifica la solución."
    
    # Primera vez
    contexto_1 = "Requisitos: función sumar en Python 3.12"
    codigo_py_v1 = get_mock_response(prompt, contexto_1)
    print("\n📝 Python V1 (primera línea):")
    print(codigo_py_v1.split('\n')[0])
    assert "def sumar" in codigo_py_v1
    assert "a - b" in codigo_py_v1
    print("✅ Python V1: Tiene bug lógico (resta en lugar de suma)")
    
    # Segunda vez con SonarQube
    contexto_2 = """
Requisitos: función sumar en Python 3.12

Instrucciones de corrección de calidad (SonarQube):
Agregar validaciones para NaN e Infinity.
"""
    codigo_py_v2 = get_mock_response(prompt, contexto_2)
    print("\n📝 Python V2:")
    print("   - Tiene validación NaN:", "isnan" in codigo_py_v2)
    print("   - Tiene validación Infinity:", "isinf" in codigo_py_v2)
    print("   - Bug lógico (resta):", "a - b" in codigo_py_v2)
    assert "isnan" in codigo_py_v2
    assert "isinf" in codigo_py_v2
    assert "a - b" in codigo_py_v2
    print("✅ Python V2: Validaciones agregadas pero tiene bug lógico")
    
    # Tercera vez con traceback
    contexto_3 = """
Requisitos: función sumar en Python 3.12

Traceback para corrección de errores de ejecución:
AssertionError: Expected 5 but got -1
"""
    codigo_py_v3 = get_mock_response(prompt, contexto_3)
    print("\n📝 Python V3:")
    print("   - Tiene validación NaN:", "isnan" in codigo_py_v3)
    print("   - Suma correctamente:", "a + b" in codigo_py_v3)
    assert "isnan" in codigo_py_v3
    assert "a + b" in codigo_py_v3
    print("✅ Python V3: Todo correcto")
    
    print("\n✅ También funciona correctamente para Python")
    print("=" * 80)


if __name__ == "__main__":
    test_tres_iteraciones_desarrollador()
    test_python_tambien()
