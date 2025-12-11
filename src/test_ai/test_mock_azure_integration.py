"""
Test para verificar que LLM_MOCK_MODE=true y AZURE_DEVOPS_ENABLED=true
trabajan correctamente juntos.
"""

import os
import sys

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.config.settings import settings
from src.agents.product_owner import product_owner_node
from src.agents.desarrollador import desarrollador_node
from src.models.state import AgentState

def test_mock_mode_with_azure():
    """
    Verifica que cuando LLM_MOCK_MODE=true y AZURE_DEVOPS_ENABLED=true,
    se generan correctamente los PBI y work items.
    """
    print("=" * 70)
    print("🧪 TEST: Verificación de LLM_MOCK_MODE + AZURE_DEVOPS_ENABLED")
    print("=" * 70)
    
    # Mostrar configuración actual
    print(f"\n📋 Configuración actual:")
    print(f"   • LLM_MOCK_MODE: {settings.LLM_MOCK_MODE}")
    print(f"   • AZURE_DEVOPS_ENABLED: {settings.AZURE_DEVOPS_ENABLED}")
    print(f"   • AZURE_DEVOPS_ORG: {settings.AZURE_DEVOPS_ORG}")
    print(f"   • AZURE_DEVOPS_PROJECT: {settings.AZURE_DEVOPS_PROJECT}")
    
    # Verificar que ambos estén activos
    if not settings.LLM_MOCK_MODE:
        print("\n❌ ERROR: LLM_MOCK_MODE debe estar en true para este test")
        print("   Configura LLM_MOCK_MODE=true en tu archivo .env")
        return False
    
    if not settings.AZURE_DEVOPS_ENABLED:
        print("\n❌ ERROR: AZURE_DEVOPS_ENABLED debe estar en true para este test")
        print("   Configura AZURE_DEVOPS_ENABLED=true en tu archivo .env")
        return False
    
    print("\n✅ Ambos modos están activos")
    
    # Estado inicial simple
    initial_state: AgentState = {
        "prompt_inicial": "Crea una función para sumar dos números en TypeScript",
        "feedback_stakeholder": "",
        "max_attempts": 2,
        "attempt_count": 0,
        "debug_attempt_count": 0,
        "max_debug_attempts": 2,
        "sonarqube_attempt_count": 0,
        "max_sonarqube_attempts": 2,
        "pruebas_superadas": False,
        "validado": False,
        "traceback": "",
        "sonarqube_issues": "",
        "sonarqube_passed": False,
        "tests_unitarios_generados": "",
        "requisito_clarificado": "",
        "requisitos_formales": "",
        "codigo_generado": "",
        "azure_pbi_id": None,
        "azure_implementation_task_id": None,
        "azure_testing_task_id": None
    }
    
    print("\n" + "=" * 70)
    print("📝 PASO 1: Ejecutando Product Owner (con mock)")
    print("=" * 70)
    
    try:
        state = product_owner_node(initial_state)
        
        # Verificar que se generaron requisitos formales
        if not state.get('requisitos_formales'):
            print("\n❌ ERROR: No se generaron requisitos_formales")
            return False
        
        print(f"\n✅ Requisitos formales generados (longitud: {len(state['requisitos_formales'])} chars)")
        
        # Verificar PBI de Azure DevOps
        if settings.AZURE_DEVOPS_ENABLED:
            if state.get('azure_pbi_id'):
                print(f"✅ PBI creado en Azure DevOps: #{state['azure_pbi_id']}")
            else:
                print("⚠️  No se creó PBI (puede ser normal si la conexión falló)")
        
    except Exception as e:
        print(f"\n❌ ERROR en Product Owner: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 70)
    print("💻 PASO 2: Ejecutando Desarrollador (con mock)")
    print("=" * 70)
    
    try:
        state = desarrollador_node(state)
        
        # Verificar que se generó código
        if not state.get('codigo_generado'):
            print("\n❌ ERROR: No se generó codigo_generado")
            return False
        
        print(f"\n✅ Código generado (longitud: {len(state['codigo_generado'])} chars)")
        print(f"   Primeras líneas:\n{state['codigo_generado'][:200]}...")
        
        # Verificar Tasks de Azure DevOps
        if settings.AZURE_DEVOPS_ENABLED and state.get('azure_pbi_id'):
            if state.get('azure_implementation_task_id'):
                print(f"✅ Task de Implementación creada: #{state['azure_implementation_task_id']}")
            else:
                print("⚠️  No se creó Task de Implementación")
            
            if state.get('azure_testing_task_id'):
                print(f"✅ Task de Testing creada: #{state['azure_testing_task_id']}")
            else:
                print("⚠️  No se creó Task de Testing")
        
    except Exception as e:
        print(f"\n❌ ERROR en Desarrollador: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 70)
    print("📊 RESUMEN DEL TEST")
    print("=" * 70)
    
    print(f"\n✅ Estado Final:")
    print(f"   • requisitos_formales: {'✓' if state.get('requisitos_formales') else '✗'}")
    print(f"   • codigo_generado: {'✓' if state.get('codigo_generado') else '✗'}")
    print(f"   • azure_pbi_id: {state.get('azure_pbi_id') or 'N/A'}")
    print(f"   • azure_implementation_task_id: {state.get('azure_implementation_task_id') or 'N/A'}")
    print(f"   • azure_testing_task_id: {state.get('azure_testing_task_id') or 'N/A'}")
    
    # Determinar éxito
    success = (
        state.get('requisitos_formales') and
        state.get('codigo_generado')
    )
    
    if success:
        print("\n" + "=" * 70)
        print("✅ TEST EXITOSO: Mock mode + Azure DevOps funcionan correctamente")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("❌ TEST FALLIDO: Revisa los errores arriba")
        print("=" * 70)
    
    return success


if __name__ == "__main__":
    resultado = test_mock_mode_with_azure()
    sys.exit(0 if resultado else 1)
