"""
Script de prueba para verificar la integración del Generador de Unit Tests
"""

import sys
sys.path.insert(0, 'src')

from models.state import AgentState
from agents.generador_unit_tests import generador_unit_tests_node
from config.settings import settings
import os

# Estado de prueba para TypeScript
test_state_ts: AgentState = {
    'prompt_inicial': 'Crear función que sume dos números',
    'feedback_stakeholder': '',
    'max_attempts': 1,
    'attempt_count': 1,
    'debug_attempt_count': 0,
    'max_debug_attempts': 3,
    'sonarqube_attempt_count': 0,
    'max_sonarqube_attempts': 2,
    'pruebas_superadas': False,
    'validado': False,
    'traceback': '',
    'sonarqube_issues': '',
    'sonarqube_passed': True,
    'tests_unitarios_generados': '',
    'requisito_clarificado': 'Crear función que sume dos números',
    'requisitos_formales': '''{
        "titulo": "Función suma",
        "lenguaje": "typescript"
    }''',
    'codigo_generado': '''```typescript
export function sumar(a: number, b: number): number {
    return a + b;
}
```'''
}

# Estado de prueba para Python
test_state_py: AgentState = {
    'prompt_inicial': 'Crear función que multiplique dos números',
    'feedback_stakeholder': '',
    'max_attempts': 1,
    'attempt_count': 1,
    'debug_attempt_count': 0,
    'max_debug_attempts': 3,
    'sonarqube_attempt_count': 0,
    'max_sonarqube_attempts': 2,
    'pruebas_superadas': False,
    'validado': False,
    'traceback': '',
    'sonarqube_issues': '',
    'sonarqube_passed': True,
    'tests_unitarios_generados': '',
    'requisito_clarificado': 'Crear función que multiplique dos números',
    'requisitos_formales': '''{
        "titulo": "Función multiplicación",
        "lenguaje": "python"
    }''',
    'codigo_generado': '''```python
def multiplicar(a: float, b: float) -> float:
    return a * b
```'''
}

def test_generador_unit_tests():
    """Prueba la generación de unit tests"""
    print("\n" + "="*60)
    print("PRUEBA: Generador de Unit Tests")
    print("="*60)
    
    # Crear directorio output si no existe
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    
    # Test 1: TypeScript
    print("\n--- Test 1: TypeScript ---")
    result_ts = generador_unit_tests_node(test_state_ts)
    assert 'tests_unitarios_generados' in result_ts
    assert len(result_ts['tests_unitarios_generados']) > 0
    print("✅ Tests TypeScript generados correctamente")
    
    # Test 2: Python
    print("\n--- Test 2: Python ---")
    result_py = generador_unit_tests_node(test_state_py)
    assert 'tests_unitarios_generados' in result_py
    assert len(result_py['tests_unitarios_generados']) > 0
    print("✅ Tests Python generados correctamente")
    
    print("\n" + "="*60)
    print("✅ TODAS LAS PRUEBAS PASARON")
    print("="*60)
    
    # Verificar archivos generados
    print("\nArchivos generados en output/:")
    for f in os.listdir(settings.OUTPUT_DIR):
        if 'test' in f.lower():
            print(f"  - {f}")

if __name__ == '__main__':
    try:
        test_generador_unit_tests()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
