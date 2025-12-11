"""
Test para verificar la generación de Release Notes en PBIs de Azure DevOps.
"""

import os
import sys

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.config.settings import settings
from src.services.azure_devops_service import azure_service
from src.models.state import AgentState

def test_release_note_generation():
    """
    Verifica que se genera y agrega correctamente un Release Note al PBI
    cuando el proyecto termina exitosamente.
    """
    print("=" * 70)
    print("🧪 TEST: Generación de Release Note para PBI")
    print("=" * 70)
    
    # Verificar configuración
    print(f"\n📋 Configuración actual:")
    print(f"   • LLM_MOCK_MODE: {settings.LLM_MOCK_MODE}")
    print(f"   • AZURE_DEVOPS_ENABLED: {settings.AZURE_DEVOPS_ENABLED}")
    
    if not settings.AZURE_DEVOPS_ENABLED:
        print("\n⚠️  AZURE_DEVOPS_ENABLED debe estar en true para este test")
        print("   Saltando test...")
        return True
    
    # Estado simulado de un proyecto completado
    state: AgentState = {
        "prompt_inicial": "Crea una función para sumar dos números en TypeScript",
        "feedback_stakeholder": "",
        "max_attempts": 2,
        "attempt_count": 1,
        "debug_attempt_count": 1,
        "max_debug_attempts": 2,
        "sonarqube_attempt_count": 1,
        "max_sonarqube_attempts": 2,
        "pruebas_superadas": True,
        "validado": True,
        "traceback": "",
        "sonarqube_issues": "",
        "sonarqube_passed": True,
        "tests_unitarios_generados": """
describe('sumar', () => {
  test('suma dos números positivos', () => {
    expect(sumar(2, 3)).toBe(5);
  });
  
  test('suma números negativos', () => {
    expect(sumar(-2, -3)).toBe(-5);
  });
  
  test('maneja punto flotante', () => {
    expect(sumar(0.1, 0.2)).toBeCloseTo(0.3);
  });
});
        """,
        "requisito_clarificado": "Implementar una función sumar que realice operaciones aritméticas básicas",
        "requisitos_formales": """{
  "objetivo_funcional": "Implementar una función sumar que realice operaciones aritméticas básicas",
  "nombre_funcion": "sumar",
  "lenguaje_version": "TypeScript 5.0",
  "entradas_esperadas": "Dos parámetros numéricos (a: number, b: number)",
  "salidas_esperadas": "Un número que representa la suma (number)",
  "casos_de_prueba": [
    {"input": "sumar(2, 3)", "expected": "5"},
    {"input": "sumar(-5, 3)", "expected": "-2"},
    {"input": "sumar(0.1, 0.2)", "expected": "~0.3"}
  ],
  "azure_devops": {
    "work_item_id": 2021496,
    "work_item_url": "https://dev.azure.com/cegid/dd7a6fad-5d82-4142-8618-f64fbb0f7670/_workitems/edit/2021496",
    "work_item_type": "Product Backlog Item",
    "story_points": 2
  }
}""",
        "codigo_generado": """export function sumar(a: number, b: number): number {
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
}""",
        "azure_pbi_id": 2021496,
        "azure_implementation_task_id": 2021497,
        "azure_testing_task_id": 2021498
    }
    
    print("\n" + "=" * 70)
    print("📝 Generando Release Note para PBI #2021496")
    print("=" * 70)
    
    try:
        success = azure_service.generate_and_add_release_note(state)
        
        if success:
            print("\n" + "=" * 70)
            print("✅ TEST EXITOSO: Release Note generado y agregado correctamente")
            print("=" * 70)
            print(f"\n🔗 Verifica el PBI en Azure DevOps:")
            print(f"   https://dev.azure.com/cegid/dd7a6fad-5d82-4142-8618-f64fbb0f7670/_workitems/edit/2021496")
            print(f"\n📋 El Release Note debería estar visible en la sección de comentarios del PBI")
            return True
        else:
            print("\n" + "=" * 70)
            print("❌ TEST FALLIDO: No se pudo generar/agregar el Release Note")
            print("=" * 70)
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR durante el test: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    resultado = test_release_note_generation()
    sys.exit(0 if resultado else 1)
