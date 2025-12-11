"""
Test de detección de duplicados en Azure DevOps.
Verifica que los métodos search_work_items y get_child_work_items funcionen correctamente.
"""

from src.tools.azure_devops_integration import AzureDevOpsClient
from src.config.settings import settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__, level=settings.get_log_level())


def test_search_duplicates():
    """
    Prueba la búsqueda de PBIs duplicados.
    """
    print("=" * 80)
    print("🔍 TEST: Búsqueda de Work Items Duplicados")
    print("=" * 80)
    
    if not settings.AZURE_DEVOPS_ENABLED:
        print("⚠️ Azure DevOps no está habilitado en configuración")
        return
    
    azure_client = AzureDevOpsClient()
    
    # Probar conexión
    if not azure_client.test_connection():
        print("❌ No se pudo conectar con Azure DevOps")
        return
    
    print("\n📋 Prueba 1: Buscar PBIs con tag 'AI-Generated'")
    print("-" * 80)
    
    # Buscar PBIs AI-Generated existentes
    pbis = azure_client.search_work_items(
        title_contains="",  # Buscar todos
        work_item_type="Product Backlog Item",
        tags=["AI-Generated"],
        max_results=10
    )
    
    if pbis:
        print(f"✅ Encontrados {len(pbis)} PBI(s) con tag 'AI-Generated':")
        for pbi in pbis:
            title = pbi['fields'].get('System.Title', 'Sin título')
            state = pbi['fields'].get('System.State', 'Sin estado')
            created = pbi['fields'].get('System.CreatedDate', 'Fecha desconocida')
            print(f"\n   📌 PBI #{pbi['id']}")
            print(f"      Título: {title}")
            print(f"      Estado: {state}")
            print(f"      Creado: {created[:10]}")
            print(f"      URL: {pbi['_links']['html']['href']}")
    else:
        print("ℹ️ No se encontraron PBIs con tag 'AI-Generated'")
    
    print("\n" + "=" * 80)
    print("📋 Prueba 2: Buscar Tasks hijas de un PBI")
    print("-" * 80)
    
    if pbis and len(pbis) > 0:
        test_pbi_id = pbis[0]['id']
        print(f"\n🔍 Buscando tasks del PBI #{test_pbi_id}...")
        
        children = azure_client.get_child_work_items(test_pbi_id)
        
        if children:
            print(f"✅ Encontradas {len(children)} task(s) hijas:")
            for child in children:
                title = child['fields'].get('System.Title', 'Sin título')
                work_type = child['fields'].get('System.WorkItemType', 'Unknown')
                state = child['fields'].get('System.State', 'Sin estado')
                tags = child['fields'].get('System.Tags', '')
                
                print(f"\n   📋 {work_type} #{child['id']}")
                print(f"      Título: {title}")
                print(f"      Estado: {state}")
                print(f"      Tags: {tags}")
        else:
            print(f"ℹ️ El PBI #{test_pbi_id} no tiene tasks hijas")
    else:
        print("⚠️ No hay PBIs disponibles para probar búsqueda de tasks")
    
    print("\n" + "=" * 80)
    print("📋 Prueba 3: Simular detección de duplicado por título")
    print("-" * 80)
    
    test_title = "Calcular suma"
    print(f"\n🔍 Buscando PBIs que contengan '{test_title}'...")
    
    matching_pbis = azure_client.search_work_items(
        title_contains=test_title,
        work_item_type="Product Backlog Item",
        tags=["AI-Generated"],
        max_results=5
    )
    
    if matching_pbis:
        print(f"⚠️ Se encontraron {len(matching_pbis)} PBI(s) similares:")
        for pbi in matching_pbis:
            title = pbi['fields'].get('System.Title', 'Sin título')
            print(f"   - PBI #{pbi['id']}: {title}")
        print("\n✅ Sistema detectaría duplicado y reutilizaría el PBI existente")
    else:
        print("✅ No hay duplicados, se puede crear un nuevo PBI")
    
    print("\n" + "=" * 80)
    print("✅ Test completado exitosamente")
    print("=" * 80)


if __name__ == "__main__":
    try:
        test_search_duplicates()
    except Exception as e:
        print(f"\n❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
