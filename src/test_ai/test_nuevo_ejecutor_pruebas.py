"""
Script de prueba para verificar el nuevo ejecutor_pruebas.
Simula la ejecución de tests sin necesidad de ejecutar todo el workflow.
"""

import os
import sys

# Añadir el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.state import AgentState
from agents.ejecutor_pruebas import ejecutor_pruebas_node
from config.settings import settings

def test_ejecutor_con_archivo_existente():
    """
    Prueba el ejecutor asumiendo que existe un archivo de tests.
    Requiere tener los archivos generados en output/
    """
    print("=" * 80)
    print("TEST: Ejecutor de Pruebas con archivo existente")
    print("=" * 80)
    
    # Crear estado simulado
    state = AgentState(
        prompt_inicial="Crea una calculadora con suma y resta",
        max_attempts=3,
        attempt_count=1,
        debug_attempt_count=0,
        max_debug_attempts=3,
        feedback_stakeholder="",
        requisito_clarificado="",
        requisitos_formales='{"language": "TypeScript"}',
        codigo_generado="""
export class Calculator {
  add(a: number, b: number): number {
    return a + b;
  }
  
  subtract(a: number, b: number): number {
    return a - b;
  }
}
""",
        traceback="",
        pruebas_superadas=False,
        sonarqube_issues="",
        sonarqube_passed=True,
        sonarqube_attempt_count=0,
        max_sonarqube_attempts=2,
        tests_unitarios_generados="",
        validado=False
    )
    
    # Verificar si existe el archivo de tests
    test_file = "unit_tests_req1_sq0.test.ts"
    test_path = os.path.join(settings.OUTPUT_DIR, test_file)
    
    if not os.path.exists(test_path):
        print(f"\n⚠️ ADVERTENCIA: No existe {test_path}")
        print("Este test requiere que primero se haya ejecutado el generador de tests.")
        print("\nPara probarlo completamente, ejecuta primero el workflow completo o")
        print("crea manualmente un archivo de tests en output/")
        return False
    
    print(f"\n✅ Archivo de tests encontrado: {test_file}")
    
    # Ejecutar el nodo
    resultado = ejecutor_pruebas_node(state)
    
    # Verificar resultados
    print("\n" + "=" * 80)
    print("RESULTADOS:")
    print("=" * 80)
    print(f"Pruebas superadas: {resultado['pruebas_superadas']}")
    print(f"Debug attempt count: {resultado['debug_attempt_count']}")
    
    if resultado['traceback']:
        print(f"\nTraceback:")
        print(resultado['traceback'][:500])
    
    return resultado['pruebas_superadas']


def test_verificar_dependencias():
    """
    Verifica que estén instaladas las dependencias necesarias.
    """
    print("\n" + "=" * 80)
    print("TEST: Verificar dependencias de testing")
    print("=" * 80)
    
    import subprocess
    
    # Verificar vitest (TypeScript)
    try:
        result = subprocess.run(
            ['npx', 'vitest', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"✅ vitest instalado: {result.stdout.strip()}")
        else:
            print(f"⚠️ vitest no encontrado o error: {result.stderr}")
    except FileNotFoundError:
        print("❌ npx no encontrado (Node.js no instalado)")
    except subprocess.TimeoutExpired:
        print("⚠️ Timeout verificando vitest")
    except Exception as e:
        print(f"❌ Error verificando vitest: {e}")
    
    # Verificar pytest (Python)
    try:
        result = subprocess.run(
            ['pytest', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"✅ pytest instalado: {result.stdout.strip()}")
        else:
            print(f"⚠️ pytest no encontrado: {result.stderr}")
    except FileNotFoundError:
        print("❌ pytest no encontrado (ejecute: pip install pytest)")
    except subprocess.TimeoutExpired:
        print("⚠️ Timeout verificando pytest")
    except Exception as e:
        print(f"❌ Error verificando pytest: {e}")


def test_estructura_archivos():
    """
    Verifica que existe la estructura de directorios correcta.
    """
    print("\n" + "=" * 80)
    print("TEST: Verificar estructura de archivos")
    print("=" * 80)
    
    if os.path.exists(settings.OUTPUT_DIR):
        print(f"✅ Directorio output existe: {settings.OUTPUT_DIR}")
        
        # Listar archivos de tests
        archivos = os.listdir(settings.OUTPUT_DIR)
        test_files = [f for f in archivos if 'test' in f.lower() and (f.endswith('.ts') or f.endswith('.py'))]
        
        if test_files:
            print(f"\n📄 Archivos de tests encontrados ({len(test_files)}):")
            for f in test_files:
                print(f"   - {f}")
        else:
            print("\n⚠️ No se encontraron archivos de tests en output/")
    else:
        print(f"❌ Directorio output NO existe: {settings.OUTPUT_DIR}")
        print("Será creado automáticamente al ejecutar el workflow")


if __name__ == "__main__":
    print("\n🧪 SUITE DE PRUEBAS - NUEVO EJECUTOR DE PRUEBAS")
    print("=" * 80)
    
    # Test 1: Verificar dependencias
    test_verificar_dependencias()
    
    # Test 2: Verificar estructura
    test_estructura_archivos()
    
    # Test 3: Ejecutar pruebas (si existen archivos)
    try:
        success = test_ejecutor_con_archivo_existente()
        
        print("\n" + "=" * 80)
        if success:
            print("✅ TODOS LOS TESTS PASARON")
        else:
            print("⚠️ ALGUNOS TESTS FALLARON (revisar logs arriba)")
        print("=" * 80)
    except Exception as e:
        print(f"\n❌ ERROR durante la ejecución de tests: {e}")
        import traceback
        traceback.print_exc()
