"""
Script de prueba para la integración de SonarQube
Genera un código simple y lo analiza con el sistema completo
"""

import sys
import os

# Añadir el directorio src al path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import run_development_workflow

if __name__ == "__main__":
    # Prompt de prueba - genera código con posibles issues de calidad
    prompt = """
    Crea una función en Python que calcule el factorial de un número.
    La función debe:
    - Aceptar un número entero no negativo
    - Retornar el factorial del número
    - Manejar errores para entradas inválidas
    """
    
    print("=" * 80)
    print("PRUEBA DE INTEGRACIÓN SONARQUBE")
    print("=" * 80)
    print(f"\nPrompt: {prompt}\n")
    print("=" * 80)
    
    # Ejecutar workflow con los nuevos límites
    final_state = run_development_workflow(prompt, max_attempts=1)
    
    print("\n" + "=" * 80)
    print("FIN DE LA PRUEBA")
    print("=" * 80)
    
    if final_state:
        print("\n✅ Ejecución completada")
        print(f"   Validado: {final_state.get('validado')}")
        print(f"   Pruebas superadas: {final_state.get('pruebas_superadas')}")
        print(f"   SonarQube aprobado: {final_state.get('sonarqube_passed')}")
        print(f"   Intentos totales: {final_state.get('attempt_count')}")
        print(f"   Intentos debug: {final_state.get('debug_attempt_count')}")
        print(f"   Intentos SonarQube: {final_state.get('sonarqube_attempt_count')}")
    else:
        print("\n❌ Ejecución fallida")
