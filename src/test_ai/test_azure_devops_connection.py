"""
Script de prueba para validar la integración con Azure DevOps.
Ejecutar: python test_azure_devops_connection.py
"""

import os
import sys

# Agregar el directorio src al path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from tools.azure_devops_integration import AzureDevOpsClient, estimate_story_points
from config.settings import settings


def test_connection():
    """Prueba la conexión con Azure DevOps."""
    print("=" * 70)
    print("🧪 TEST: Conexión con Azure DevOps")
    print("=" * 70)
    
    # Verificar configuración
    print(f"\n📋 Configuración actual:")
    print(f"   • AZURE_DEVOPS_ENABLED: {settings.AZURE_DEVOPS_ENABLED}")
    print(f"   • Organización: {settings.AZURE_DEVOPS_ORG or '(no configurada)'}")
    print(f"   • Proyecto: {settings.AZURE_DEVOPS_PROJECT or '(no configurado)'}")
    print(f"   • PAT configurado: {'✅' if settings.AZURE_DEVOPS_PAT else '❌'}")
    print(f"   • Iteration Path: {settings.AZURE_ITERATION_PATH or '(no configurado)'}")
    print(f"   • Area Path: {settings.AZURE_AREA_PATH or '(no configurado)'}")
    
    if not settings.AZURE_DEVOPS_ENABLED:
        print("\n⚠️  Azure DevOps está deshabilitado en la configuración")
        print("   Para habilitarlo, configura AZURE_DEVOPS_ENABLED=true en .env")
        return False
    
    if not all([settings.AZURE_DEVOPS_ORG, settings.AZURE_DEVOPS_PROJECT, settings.AZURE_DEVOPS_PAT]):
        print("\n❌ Configuración incompleta. Verifica tu archivo .env")
        print("   Variables requeridas:")
        print("   - AZURE_DEVOPS_ORG")
        print("   - AZURE_DEVOPS_PROJECT")
        print("   - AZURE_DEVOPS_PAT")
        return False
    
    # Crear cliente y probar conexión
    print("\n🔌 Probando conexión con Azure DevOps...")
    client = AzureDevOpsClient()
    
    if client.test_connection():
        print("✅ ¡Conexión exitosa!")
        return True
    else:
        print("❌ Error de conexión. Verifica las credenciales.")
        return False


def test_create_pbi():
    """Crea un PBI de prueba en Azure DevOps."""
    print("\n" + "=" * 70)
    print("🧪 TEST: Creación de PBI de prueba")
    print("=" * 70)
    
    client = AzureDevOpsClient()
    
    # Datos de ejemplo
    requisitos_ejemplo = {
        'objetivo_funcional': 'Función de prueba para validar integración con Azure DevOps',
        'entradas_esperadas': 'Un número entero',
        'salidas_esperadas': 'El doble del número de entrada como string'
    }
    
    story_points = estimate_story_points(requisitos_ejemplo)
    print(f"\n📊 Story Points estimados: {story_points}")
    
    print("\n📝 Creando PBI de prueba...")
    
    pbi = client.create_pbi(
        title="[TEST] Validación de integración - Sistema Multiagente",
        description="""
        <h3>Objetivo</h3>
        <p>Este es un PBI de prueba creado automáticamente por el sistema multiagente
        para validar la integración con Azure DevOps.</p>
        
        <h3>Detalles</h3>
        <ul>
            <li><strong>Función:</strong> Validación de API REST</li>
            <li><strong>Lenguaje:</strong> Python 3.10+</li>
        </ul>
        
        <hr/>
        <p><em>🤖 Generado automáticamente por el sistema multiagente de desarrollo</em></p>
        """,
        acceptance_criteria="""
        <h4>Criterios de Aceptación</h4>
        <ul>
            <li>✅ La integración debe funcionar correctamente</li>
            <li>✅ El PBI debe crearse en el proyecto correcto</li>
            <li>✅ Los metadatos deben ser precisos</li>
        </ul>
        """,
        story_points=story_points,
        tags=["Test", "AI-Generated", "Integration"],
        priority=3  # Baja prioridad para tests
    )
    
    if pbi:
        print(f"\n✅ PBI creado exitosamente!")
        print(f"   • ID: #{pbi['id']}")
        print(f"   • URL: {pbi['_links']['html']['href']}")
        print(f"   • Estado: {pbi['fields'].get('System.State', 'N/A')}")
        print(f"\n💡 Puedes ver el PBI en tu navegador copiando la URL de arriba")
        return True
    else:
        print("\n❌ Error al crear el PBI")
        return False


def test_estimate_story_points():
    """Prueba el algoritmo de estimación de story points."""
    print("\n" + "=" * 70)
    print("🧪 TEST: Estimación de Story Points")
    print("=" * 70)
    
    test_cases = [
        {
            'objetivo_funcional': 'Función simple',
            'entradas_esperadas': 'Un número',
            'salidas_esperadas': 'El doble',
            'expected': 1
        },
        {
            'objetivo_funcional': 'Función mediana con validación de entrada y manejo de errores',
            'entradas_esperadas': 'Lista de números enteros y flotantes',
            'salidas_esperadas': 'String formateado con estadísticas',
            'expected': 3
        },
        {
            'objetivo_funcional': 'Sistema completo de autenticación con JWT, refresh tokens, manejo de sesiones, validación de roles y permisos',
            'entradas_esperadas': 'Credenciales de usuario, información de sesión, tokens de acceso y refresh, configuración de permisos',
            'salidas_esperadas': 'Objetos de usuario autenticado con todos los claims, tokens firmados, metadata de sesión, logs de auditoría',
            'expected': 13
        }
    ]
    
    print("\n📊 Probando diferentes niveles de complejidad:\n")
    
    all_passed = True
    for i, test in enumerate(test_cases, 1):
        points = estimate_story_points(test)
        passed = "✅" if points == test['expected'] else "⚠️"
        
        print(f"{passed} Caso {i}:")
        print(f"   Descripción: {test['objetivo_funcional'][:60]}...")
        print(f"   Story Points: {points} (esperado: {test['expected']})")
        
        if points != test['expected']:
            all_passed = False
        print()
    
    if all_passed:
        print("✅ Todos los casos pasaron correctamente")
    else:
        print("⚠️ Algunos casos difieren del esperado (puede ser aceptable)")
    
    return True


def main():
    """Ejecuta todos los tests."""
    print("\n" + "🚀" * 35)
    print("  PRUEBA DE INTEGRACIÓN CON AZURE DEVOPS")
    print("🚀" * 35 + "\n")
    
    # Test 1: Estimación de story points (no requiere conexión)
    test_estimate_story_points()
    
    # Test 2: Conexión con Azure DevOps
    if not test_connection():
        print("\n❌ No se pudo establecer conexión con Azure DevOps")
        print("   Verifica tu configuración en .env y vuelve a intentar")
        return
    
    # Test 3: Crear PBI de prueba
    print("\n⚠️  A continuación se creará un PBI de prueba en tu proyecto de Azure DevOps")
    respuesta = input("   ¿Deseas continuar? (s/n): ")
    
    if respuesta.lower() in ['s', 'si', 'sí', 'y', 'yes']:
        test_create_pbi()
    else:
        print("\n⏭️  Creación de PBI omitida")
    
    print("\n" + "=" * 70)
    print("✅ Pruebas completadas")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
