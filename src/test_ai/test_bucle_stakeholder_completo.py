"""
Test del Bucle Completo del Stakeholder con Reingeniería de Requisitos

Valida que el sistema maneja correctamente el rechazo del Stakeholder y la 
reingeniería de requisitos por el Product Owner, seguido de una nueva implementación
con requisitos mejorados.

Flujo esperado:
1. Product Owner genera requisitos básicos (2 parámetros)
2. Desarrollador genera código básico
3. Pasa SonarQube y Tests
4. Stakeholder RECHAZA (requisitos insuficientes)
5. Product Owner regenera requisitos mejorados (parámetros variables)
6. Desarrollador genera código mejorado (con spread/args)
7. Pasa SonarQube y Tests
8. Stakeholder VALIDA
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.llm.mock_responses import get_mock_response

def test_product_owner_reingenieria():
    """Test: Product Owner genera requisitos mejorados después de feedback"""
    print("\n" + "="*80)
    print("TEST 1: Product Owner - Reingeniería de Requisitos")
    print("="*80)
    
    # Primera iteración: requisitos básicos
    context_inicial = "Requisitos iniciales para función sumar"
    prompt = "Product Owner, genera los requisitos para la nueva funcionalidad"
    
    response_basica = get_mock_response(prompt, context_inicial)
    print("\n📋 Requisitos Básicos (Primera Iteración):")
    print(response_basica[:200] + "...")
    
    # Verificar que son requisitos básicos (menciona 2 números/parámetros)
    assert "Dos números" in response_basica or "dos números" in response_basica or "(a, b)" in response_basica
    assert "operación" in response_basica.lower() or "suma" in response_basica.lower()
    print("✅ Requisitos básicos generados correctamente (2 parámetros)")
    
    # Segunda iteración: con feedback del Stakeholder
    context_feedback = (
        "Feedback del Stakeholder: Los requisitos son insuficientes. "
        "El código RECHAZADO debe mejorar para:\n"
        "1. Aceptar múltiples números (no solo 2)\n"
        "2. Soportar arrays o listas\n"
        "3. Incluir documentación detallada"
    )
    
    response_mejorada = get_mock_response(prompt, context_feedback)
    print("\n📋 Requisitos Mejorados (Segunda Iteración):")
    print(response_mejorada[:300] + "...")
    
    # Verificar que son requisitos mejorados
    assert "múltiples números" in response_mejorada.lower() or "número variable" in response_mejorada.lower()
    assert "array" in response_mejorada.lower() or "lista" in response_mejorada.lower()
    assert len(response_mejorada) > len(response_basica) * 1.5  # Significativamente más detallada
    print("✅ Requisitos mejorados generados correctamente (parámetros variables)")
    
    print("\n" + "="*80)


def test_desarrollador_implementa_requisitos_mejorados():
    """Test: Desarrollador genera código con parámetros variables"""
    print("\n" + "="*80)
    print("TEST 2: Desarrollador - Implementación con Requisitos Mejorados")
    print("="*80)
    
    # Context con requisitos mejorados (TypeScript)
    context_mejorado_ts = """
    Lenguaje: TypeScript
    Requisitos del sistema:
    {
        "funcionalidad": "Función suma versátil",
        "descripcion": "Debe aceptar múltiples números (número variable de argumentos)",
        "casos_uso": [
            "Sumar 2 números: sumar(2, 3) = 5",
            "Sumar 4 números: sumar(1, 2, 3, 4) = 10",
            "Sumar array: sumar(...[1,2,3]) = 6"
        ]
    }
    """
    
    prompt = "Desarrollador, codifica la función"
    response_ts = get_mock_response(prompt, context_mejorado_ts)
    
    print("\n💻 Código TypeScript Generado:")
    print(response_ts[:400] + "...")
    
    # Verificar características del código mejorado
    assert "...numeros" in response_ts  # Spread operator
    assert "number[]" in response_ts    # Array type
    assert "reduce" in response_ts or "for" in response_ts  # Iteración sobre array
    assert "numeros.length" in response_ts  # Validación de cantidad
    print("✅ Código TypeScript con spread operator generado")
    
    # Context con requisitos mejorados (Python)
    context_mejorado_py = """
    Lenguaje: Python
    Requisitos del sistema:
    {
        "funcionalidad": "Función suma versátil",
        "descripcion": "Debe aceptar múltiples números (número variable de argumentos)",
        "casos_uso": [
            "Sumar 2 números: sumar(2, 3) = 5",
            "Sumar 4 números: sumar(1, 2, 3, 4) = 10"
        ]
    }
    """
    
    prompt_py = "Desarrollador, codifica la función"
    response_py = get_mock_response(prompt_py, context_mejorado_py)
    
    print("\n💻 Código Python Generado:")
    print(response_py[:400] + "...")
    
    # Verificar características del código mejorado
    assert "*numeros" in response_py  # Args variable
    assert "len(numeros)" in response_py  # Validación de cantidad
    assert "sum(numeros)" in response_py or "for num in numeros" in response_py
    print("✅ Código Python con *args generado")
    
    print("\n" + "="*80)


def test_stakeholder_rechaza_y_acepta():
    """Test: Stakeholder rechaza primera iteración y acepta segunda"""
    print("\n" + "="*80)
    print("TEST 3: Stakeholder - Rechazo y Aceptación")
    print("="*80)
    
    prompt = "Stakeholder, valida el código implementado"
    
    # Primera iteración (attempt_count = 1)
    context_intento1 = """
    Código implementado:
    export function sumar(a: number, b: number): number {
        return a + b;
    }
    
    Intento: 1/3
    """
    
    response1 = get_mock_response(prompt, context_intento1)
    print("\n🔍 Primera Validación (Intento 1):")
    print(response1[:300] + "...")
    
    # Verificar rechazo con formato correcto
    assert "VALIDACIÓN FINAL: RECHAZADO" in response1
    assert "Motivo:" in response1
    assert "más de dos números" in response1.lower() or "suma variable" in response1.lower() or "cantidad variable" in response1.lower()
    print("✅ Stakeholder RECHAZA primera iteración con motivo")
    
    # Segunda iteración (attempt_count = 2) - después de reingeniería
    context_intento2 = """
    Código implementado:
    export function sumar(...numeros: number[]): number {
        if (numeros.length === 0) throw new Error('Debe proporcionar al menos un número');
        return numeros.reduce((acc, num) => acc + num, 0);
    }
    
    Intento: 2/3
    """
    
    response2 = get_mock_response(prompt, context_intento2)
    print("\n🔍 Segunda Validación (Intento 2):")
    print(response2[:300] + "...")
    
    # Verificar aceptación con formato correcto
    assert "VALIDACIÓN FINAL: VALIDADO" in response2
    assert "RECHAZADO" not in response2
    print("✅ Stakeholder VALIDA segunda iteración")
    
    print("\n" + "="*80)


def test_flujo_completo_reingenieria():
    """Test: Flujo completo desde requisitos básicos hasta validación final"""
    print("\n" + "="*80)
    print("TEST 4: Flujo Completo de Reingeniería")
    print("="*80)
    
    print("\n📍 FASE 1: Requisitos Básicos")
    context = "Requisitos iniciales"
    req_basicos = get_mock_response("Product Owner, genera requisitos", context)
    assert "Dos números" in req_basicos or "(a, b)" in req_basicos
    print("✅ Product Owner genera requisitos básicos")
    
    print("\n📍 FASE 2: Código Básico")
    context_dev = f"Lenguaje: TypeScript\nRequisitos:\n{req_basicos}"
    codigo_basico = get_mock_response("Desarrollador, codifica", context_dev)
    assert "function" in codigo_basico.lower() and ("sumar" in codigo_basico or "calcular" in codigo_basico)
    print("✅ Desarrollador implementa código básico (2 parámetros)")
    
    print("\n📍 FASE 3: Stakeholder Rechaza")
    context_stake = f"Código:\n{codigo_basico}\nIntento: 1/3"
    validacion1 = get_mock_response("Stakeholder, valida", context_stake)
    assert "VALIDACIÓN FINAL: RECHAZADO" in validacion1
    assert "Motivo:" in validacion1
    print("✅ Stakeholder RECHAZA por requisitos insuficientes (con motivo)")
    
    print("\n📍 FASE 4: Reingeniería de Requisitos")
    context_reingeniera = f"Feedback del Stakeholder: {validacion1}"
    req_mejorados = get_mock_response("Product Owner, mejora requisitos", context_reingeniera)
    assert "múltiples" in req_mejorados.lower() or "variable" in req_mejorados.lower()
    print("✅ Product Owner genera requisitos mejorados")
    
    print("\n📍 FASE 5: Código Mejorado")
    context_dev2 = f"Lenguaje: TypeScript\nRequisitos mejorados:\n{req_mejorados}"
    codigo_mejorado = get_mock_response("Desarrollador, codifica", context_dev2)
    assert "...numeros" in codigo_mejorado or "*numeros" in codigo_mejorado
    assert "number[]" in codigo_mejorado or "reduce" in codigo_mejorado or "for" in codigo_mejorado
    print("✅ Desarrollador implementa código mejorado (spread operator)")
    
    print("\n📍 FASE 6: Stakeholder Acepta")
    context_stake2 = f"Código:\n{codigo_mejorado}\nIntento: 2/3"
    validacion2 = get_mock_response("Stakeholder, valida", context_stake2)
    assert "VALIDACIÓN FINAL: VALIDADO" in validacion2
    print("✅ Stakeholder VALIDA implementación mejorada")
    
    print("\n" + "="*80)
    print("🎉 FLUJO COMPLETO DE REINGENIERÍA VALIDADO")
    print("="*80)


if __name__ == "__main__":
    try:
        test_product_owner_reingenieria()
        test_desarrollador_implementa_requisitos_mejorados()
        test_stakeholder_rechaza_y_acepta()
        test_flujo_completo_reingenieria()
        
        print("\n" + "🎉 "*20)
        print("TODOS LOS TESTS DEL BUCLE STAKEHOLDER COMPLETO PASARON")
        print("🎉 "*20)
    except AssertionError as e:
        print(f"\n❌ TEST FALLIDO: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
