"""
Test end-to-end del flujo completo con mock:
ProductOwner → Desarrollador → SonarQube (rechaza) → Desarrollador (corrige) → SonarQube (aprueba)
"""

import sys
from pathlib import Path

# Añadir src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from llm.mock_responses import get_mock_response
from tools.sonarqube_mcp import analizar_codigo_con_sonarqube, es_codigo_aceptable


def simular_flujo_completo():
    """Simula el flujo completo del sistema con mock"""
    
    print("\n" + "=" * 80)
    print("🚀 SIMULACIÓN COMPLETA DEL FLUJO CON MOCK")
    print("=" * 80)
    
    # PASO 1: Product Owner genera requisitos
    print("\n📋 PASO 1: Product Owner genera requisitos formales")
    print("-" * 80)
    
    prompt_po = "Eres un Product Owner. Analiza los requisitos."
    contexto_po = "Necesito una función sumar en TypeScript"
    
    requisitos = get_mock_response(prompt_po, contexto_po)
    print(requisitos[:150] + "...")
    
    # PASO 2: Desarrollador genera código (primera vez)
    print("\n💻 PASO 2: Desarrollador genera código inicial")
    print("-" * 80)
    
    prompt_dev = "Eres un desarrollador experto. Codifica la solución."
    contexto_dev_1 = f"{requisitos}\n\nLenguaje: TypeScript 5.x"
    
    codigo_v1 = get_mock_response(prompt_dev, contexto_dev_1)
    print(codigo_v1)
    
    # PASO 3: SonarQube analiza código (primera vez)
    print("\n🔍 PASO 3: SonarQube analiza código inicial")
    print("-" * 80)
    
    resultado_sq_1 = analizar_codigo_con_sonarqube(codigo_v1, "test_sumar_v1.ts")
    aceptable_v1 = es_codigo_aceptable(resultado_sq_1)
    
    summary_1 = resultado_sq_1.get("summary", {})
    issues_1 = resultado_sq_1.get("issues", [])
    
    print(f"Issues totales: {summary_1.get('total_issues', 0)}")
    print(f"BLOCKER: {summary_1.get('by_severity', {}).get('BLOCKER', 0)}")
    print(f"CRITICAL: {summary_1.get('by_severity', {}).get('CRITICAL', 0)}")
    print(f"BUGS: {summary_1.get('by_type', {}).get('BUG', 0)}")
    
    # Mostrar detalles de los bugs
    if issues_1:
        print(f"\n📋 Detalle de issues ({len(issues_1)} encontrados):")
        for idx, issue in enumerate(issues_1, 1):
            print(f"   {idx}. [{issue['type']}] {issue['rule']}: {issue['message']} (línea {issue['line']})")
    
    print(f"\n{'✅ APROBADO' if aceptable_v1 else '❌ RECHAZADO'}")
    
    if not aceptable_v1:
        print("\n⚠️ El código tiene issues que deben corregirse")
        
        # PASO 4: Desarrollador corrige código
        print("\n💻 PASO 4: Desarrollador corrige el código basándose en feedback de SonarQube")
        print("-" * 80)
        
        contexto_dev_2 = f"""
{requisitos}

Instrucciones de corrección de calidad (SonarQube):
El análisis detectó problemas de calidad. Debes agregar validaciones adicionales
para manejar casos edge como NaN e Infinity.

Código anterior a corregir:
{codigo_v1}
"""
        
        codigo_v2 = get_mock_response(prompt_dev, contexto_dev_2)
        print(codigo_v2)
        
        # PASO 5: SonarQube analiza código corregido
        print("\n🔍 PASO 5: SonarQube analiza código corregido")
        print("-" * 80)
        
        resultado_sq_2 = analizar_codigo_con_sonarqube(codigo_v2, "test_sumar_v2.ts")
        aceptable_v2 = es_codigo_aceptable(resultado_sq_2)
        
        summary_2 = resultado_sq_2.get("summary", {})
        issues_2 = resultado_sq_2.get("issues", [])
        
        print(f"Issues totales: {summary_2.get('total_issues', 0)}")
        print(f"BLOCKER: {summary_2.get('by_severity', {}).get('BLOCKER', 0)}")
        print(f"CRITICAL: {summary_2.get('by_severity', {}).get('CRITICAL', 0)}")
        print(f"BUGS: {summary_2.get('by_type', {}).get('BUG', 0)}")
        
        # Mostrar detalles de los bugs
        if issues_2:
            print(f"\n📋 Detalle de issues ({len(issues_2)} encontrados):")
            for idx, issue in enumerate(issues_2, 1):
                print(f"   {idx}. [{issue['type']}] {issue['rule']}: {issue['message']} (línea {issue['line']})")
        
        print(f"\n{'✅ APROBADO' if aceptable_v2 else '❌ RECHAZADO'}")
        
        # VERIFICACIÓN FINAL
        print("\n" + "=" * 80)
        print("📊 RESULTADO FINAL")
        print("=" * 80)
        
        if aceptable_v2:
            print("✅ El flujo funcionó correctamente:")
            print("   1️⃣ Primera versión rechazada por SonarQube")
            print("   2️⃣ Desarrollador recibió feedback y corrigió")
            print("   3️⃣ Segunda versión aprobada por SonarQube")
            print("\n🎉 EL SISTEMA DE CORRECCIÓN AUTOMÁTICA FUNCIONA!")
        else:
            print("❌ El código aún tiene problemas después de la corrección")
            print("⚠️ El mock necesita ajustes")
            
    else:
        print("\n✅ El código pasó en la primera iteración")
        print("ℹ️ Este test esperaba un rechazo inicial para demostrar la corrección")
    
    print("=" * 80)


if __name__ == "__main__":
    simular_flujo_completo()
