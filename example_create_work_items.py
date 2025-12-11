"""
Script de ejemplo: Crear Tasks y Bugs asociados a un PBI padre.
Demuestra cómo usar el PBI ID guardado en el estado para crear work items relacionados.
"""

import sys
sys.path.insert(0, 'src')

from tools.azure_devops_integration import AzureDevOpsClient
from config.settings import settings

def example_create_related_work_items():
    """
    Ejemplo de creación de Tasks y Bugs asociados a un PBI padre.
    """
    print("=" * 70)
    print("📋 EJEMPLO: Creación de Work Items Asociados a PBI Padre")
    print("=" * 70)
    
    if not settings.AZURE_DEVOPS_ENABLED:
        print("❌ Azure DevOps no está habilitado en .env")
        return
    
    # Inicializar cliente
    client = AzureDevOpsClient()
    
    # Verificar conexión
    print("\n🔌 Verificando conexión con Azure DevOps...")
    if not client.test_connection():
        print("❌ No se pudo conectar con Azure DevOps")
        return
    
    print("✅ Conexión exitosa\n")
    
    # En un flujo real, este ID vendría de state['azure_pbi_id']
    # Para este ejemplo, pediremos al usuario que ingrese el PBI ID
    pbi_id_str = input("📝 Ingresa el ID del PBI padre (o presiona Enter para omitir): ").strip()
    
    parent_pbi_id = None
    if pbi_id_str:
        try:
            parent_pbi_id = int(pbi_id_str)
            print(f"✅ Se asociarán los work items al PBI #{parent_pbi_id}\n")
        except ValueError:
            print("⚠️ ID inválido, se crearán work items sin padre\n")
    else:
        print("⚠️ No se especificó PBI padre, se crearán work items independientes\n")
    
    # === EJEMPLO 1: Crear Task de Implementación ===
    print("=" * 70)
    print("🔧 Creando Task: Implementar lógica de negocio")
    print("=" * 70)
    
    task1 = client.create_task(
        title="[AI-Generated] Implementar función calculadora",
        description="""
        <h3>Descripción</h3>
        <p>Implementar la lógica de la función calculadora con las operaciones básicas.</p>
        
        <h3>Tareas específicas</h3>
        <ul>
            <li>Implementar método add()</li>
            <li>Implementar método subtract()</li>
            <li>Implementar método multiply()</li>
            <li>Implementar método divide() con manejo de división por cero</li>
        </ul>
        """,
        parent_id=parent_pbi_id,
        remaining_work=5,  # Fibonacci: 5 horas estimadas
        tags=["AI-Generated", "Implementation", "TypeScript"]
    )
    
    if task1:
        print(f"\n✅ Task creada: #{task1['id']}")
        print(f"   URL: {task1['_links']['html']['href']}")
    
    # === EJEMPLO 2: Crear Task de Testing ===
    print("\n" + "=" * 70)
    print("🧪 Creando Task: Crear unit tests")
    print("=" * 70)
    
    task2 = client.create_task(
        title="[AI-Generated] Crear unit tests para calculadora",
        description="""
        <h3>Descripción</h3>
        <p>Crear suite completa de unit tests para la clase Calculator.</p>
        
        <h3>Cobertura requerida</h3>
        <ul>
            <li>Tests para operaciones normales</li>
            <li>Tests para casos límite (números negativos, cero)</li>
            <li>Tests para manejo de errores (división por cero)</li>
            <li>Alcanzar >80% de cobertura de código</li>
        </ul>
        """,
        parent_id=parent_pbi_id,
        remaining_work=3,  # Fibonacci: 3 horas estimadas
        tags=["AI-Generated", "Testing", "Unit-Tests"]
    )
    
    if task2:
        print(f"\n✅ Task creada: #{task2['id']}")
        print(f"   URL: {task2['_links']['html']['href']}")
    
    # === EJEMPLO 3: Crear Bug (si se detecta un problema) ===
    print("\n" + "=" * 70)
    print("🐛 Creando Bug: División por cero no controlada")
    print("=" * 70)
    
    bug1 = client.create_bug(
        title="[AI-Generated] División por cero no lanza excepción",
        repro_steps="""
        <h3>Pasos para Reproducir</h3>
        <ol>
            <li>Crear instancia de Calculator: <code>const calc = new Calculator();</code></li>
            <li>Llamar al método divide con divisor cero: <code>calc.divide(10, 0);</code></li>
            <li>Observar el resultado</li>
        </ol>
        
        <h3>Resultado Esperado</h3>
        <p>Debe lanzar una excepción <code>Error</code> con mensaje "División por cero no permitida"</p>
        
        <h3>Resultado Actual</h3>
        <p>Retorna <code>Infinity</code> sin lanzar excepción</p>
        
        <h3>Impacto</h3>
        <p>Puede causar cálculos incorrectos en producción</p>
        """,
        parent_id=parent_pbi_id,
        severity="2 - High",  # Alta severidad
        priority=1,  # Prioridad alta
        tags=["AI-Generated", "Bug", "Error-Handling"]
    )
    
    if bug1:
        print(f"\n✅ Bug creado: #{bug1['id']}")
        print(f"   URL: {bug1['_links']['html']['href']}")
    
    # === RESUMEN ===
    print("\n" + "=" * 70)
    print("📊 RESUMEN")
    print("=" * 70)
    
    if parent_pbi_id:
        print(f"✅ PBI Padre: #{parent_pbi_id}")
        print(f"   https://dev.azure.com/{settings.AZURE_DEVOPS_ORG}/{settings.AZURE_DEVOPS_PROJECT}/_workitems/edit/{parent_pbi_id}")
    
    if task1:
        print(f"\n✅ Task #1 (Implementación): #{task1['id']}")
    if task2:
        print(f"✅ Task #2 (Testing): #{task2['id']}")
    if bug1:
        print(f"✅ Bug #1 (División por cero): #{bug1['id']}")
    
    print("\n💡 Los work items creados ahora aparecen en el backlog de Azure DevOps")
    if parent_pbi_id:
        print(f"   y están asociados jerárquicamente al PBI #{parent_pbi_id}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    example_create_related_work_items()
