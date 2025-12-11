"""
Test para verificar el bucle del Stakeholder:
1. Primera validación: RECHAZA (requisitos insuficientes)
2. Segunda validación: VALIDA (requisitos mejorados)
"""

import sys
from pathlib import Path

# Añadir src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm.mock_responses import get_mock_response


def test_stakeholder_dos_iteraciones():
    """Verifica que el Stakeholder rechaza la primera vez y valida la segunda"""
    
    print("\n" + "=" * 80)
    print("🧪 TEST: Bucle del Stakeholder - Dos Iteraciones")
    print("=" * 80)
    
    prompt_stakeholder = "Eres un stakeholder. Valida el código."
    
    # ========================================================================
    # ITERACIÓN 1: Primera validación (debe rechazar)
    # ========================================================================
    print("\n📝 ITERACIÓN 1: Primera validación del Stakeholder")
    print("-" * 80)
    
    contexto_1 = """
Intento: 1/3
Código aprobado técnicamente:
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
    
    const resultado = a + b;
    return Math.round(resultado * 1e10) / 1e10;
}

Requisitos Formales (JSON): {
  "objetivo_funcional": "Implementar una función sumar",
  "lenguaje_version": "TypeScript 5.x"
}
"""
    
    respuesta_1 = get_mock_response(prompt_stakeholder, contexto_1)
    print(respuesta_1)
    print("-" * 80)
    
    # Verificar que rechaza
    assert "RECHAZADO" in respuesta_1, "Primera iteración debe RECHAZAR"
    assert "VALIDADO" not in respuesta_1, "Primera iteración NO debe validar"
    print("✅ Stakeholder RECHAZA en primera iteración")
    print("✅ Proporciona feedback para mejorar requisitos")
    print("📊 Flujo volverá al Product Owner para reingeniería de requisitos")
    
    # ========================================================================
    # ITERACIÓN 2: Segunda validación (debe validar)
    # ========================================================================
    print("\n📝 ITERACIÓN 2: Segunda validación del Stakeholder")
    print("-" * 80)
    
    contexto_2 = """
Intento: 2/3
Código aprobado técnicamente:
export function sumar(...numeros: number[]): number {
    if (numeros.length === 0) {
        throw new Error('Debe proporcionar al menos un número');
    }
    
    for (const num of numeros) {
        if (typeof num !== 'number') {
            throw new Error('Todos los argumentos deben ser números');
        }
        if (Number.isNaN(num)) {
            throw new Error('Los argumentos no pueden ser NaN');
        }
        if (!Number.isFinite(num)) {
            throw new Error('Los argumentos deben ser números finitos');
        }
    }
    
    const resultado = numeros.reduce((acc, num) => acc + num, 0);
    return Math.round(resultado * 1e10) / 1e10;
}

Requisitos Formales (JSON): {
  "objetivo_funcional": "Implementar una función sumar con soporte para múltiples números",
  "lenguaje_version": "TypeScript 5.x",
  "casos_uso": [
    "Sumar dos números",
    "Sumar arrays de números",
    "Suma variable de argumentos"
  ]
}
"""
    
    respuesta_2 = get_mock_response(prompt_stakeholder, contexto_2)
    print(respuesta_2)
    print("-" * 80)
    
    # Verificar que valida
    assert "VALIDADO" in respuesta_2, "Segunda iteración debe VALIDAR"
    assert "RECHAZADO" not in respuesta_2, "Segunda iteración NO debe rechazar"
    print("✅ Stakeholder VALIDA en segunda iteración")
    print("✅ Acepta requisitos mejorados y código ampliado")
    print("📊 Flujo termina exitosamente")
    
    # ========================================================================
    # RESUMEN
    # ========================================================================
    print("\n" + "=" * 80)
    print("✅ TEST PASADO: Bucle del Stakeholder funciona correctamente")
    print("=" * 80)
    
    print("\n📋 RESUMEN DEL FLUJO:")
    print("   1️⃣ Primera iteración:")
    print("      - Código técnicamente correcto")
    print("      - Requisitos básicos (solo suma de 2 números)")
    print("      - Stakeholder: RECHAZA (visión de negocio incompleta)")
    print("      - Acción: Vuelve al Product Owner")
    print()
    print("   2️⃣ Segunda iteración:")
    print("      - Requisitos mejorados (suma variable, arrays)")
    print("      - Código ampliado (spread operator, reduce)")
    print("      - Stakeholder: VALIDA (cumple visión de negocio)")
    print("      - Acción: Proyecto TERMINADO")
    print("=" * 80)


def test_deteccion_intento():
    """Verifica que el mock detecta correctamente el número de intento"""
    
    print("\n" + "=" * 80)
    print("🧪 TEST: Detección del Número de Intento")
    print("=" * 80)
    
    prompt = "Eres un stakeholder. Valida el código."
    
    # Test con diferentes formatos de intento
    casos = [
        ("Intento: 1/3", True, "Formato 'Intento: 1/3'"),
        ("intento 1", True, "Formato 'intento 1'"),
        ("Iteración 1 de 3", True, "Formato 'iteración 1'"),
        ("Intento: 2/3", False, "Formato 'Intento: 2/3'"),
        ("intento 2", False, "Formato 'intento 2'"),
        ("Sin indicador de intento", False, "Sin indicador"),
    ]
    
    for contexto, debe_rechazar, descripcion in casos:
        contexto_completo = f"{contexto}\nCódigo: function test() {{ return true; }}"
        respuesta = get_mock_response(prompt, contexto_completo)
        
        es_rechazado = "RECHAZADO" in respuesta
        
        if debe_rechazar:
            assert es_rechazado, f"{descripcion} debe RECHAZAR"
            print(f"✅ {descripcion}: RECHAZA correctamente")
        else:
            assert not es_rechazado, f"{descripcion} NO debe RECHAZAR"
            print(f"✅ {descripcion}: VALIDA correctamente")
    
    print("\n✅ Todos los casos de detección funcionan correctamente")
    print("=" * 80)


if __name__ == "__main__":
    test_stakeholder_dos_iteraciones()
    test_deteccion_intento()
    
    print("\n" + "=" * 80)
    print("🎉 TODOS LOS TESTS DEL STAKEHOLDER PASARON")
    print("=" * 80)
    print("\n📋 Conclusión:")
    print("   ✓ El Stakeholder rechaza en la primera iteración")
    print("   ✓ El Stakeholder valida en iteraciones posteriores")
    print("   ✓ El sistema detecta correctamente el número de intento")
    print("   ✓ El bucle de reingeniería de requisitos funciona")
    print("=" * 80)
