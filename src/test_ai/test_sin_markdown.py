"""
Script simple para probar la generación de tests sin marcadores markdown
"""

import sys
sys.path.insert(0, 'src')

from models.state import AgentState
from agents.generador_unit_tests import generador_unit_tests_node
from config.settings import settings
import os

# Limpiar archivos de test anteriores
import glob
for f in glob.glob(os.path.join(settings.OUTPUT_DIR, "*.test.*")):
    os.remove(f)
    print(f"🗑️  Eliminado: {f}")

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
    'requisitos_formales': '{"titulo": "Función suma", "lenguaje": "typescript"}',
    'codigo_generado': '''```typescript
export function sumar(a: number, b: number): number {
    return a + b;
}
```'''
}

print("\n" + "="*60)
print("Generando tests de TypeScript...")
print("="*60)

result = generador_unit_tests_node(test_state_ts)

print("\n" + "="*60)
print("Verificando contenido del archivo...")
print("="*60)

# Buscar el archivo generado
test_files = glob.glob(os.path.join(settings.OUTPUT_DIR, "*.test.ts"))
if test_files:
    test_file = test_files[0]
    print(f"\n📄 Archivo: {test_file}\n")
    
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
        first_lines = content.split('\n')[:5]
        
        print("Primeras 5 líneas:")
        for i, line in enumerate(first_lines, 1):
            print(f"{i}: {line}")
        
        # Verificar si contiene marcadores markdown
        if content.startswith('```'):
            print("\n❌ ERROR: El archivo contiene marcadores markdown al inicio")
        elif '```typescript' in content or '```python' in content:
            print("\n❌ ERROR: El archivo contiene marcadores markdown en el contenido")
        else:
            print("\n✅ CORRECTO: El archivo NO contiene marcadores markdown")
else:
    print("\n❌ ERROR: No se encontró archivo de test generado")
