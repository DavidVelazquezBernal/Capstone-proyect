"""
Verificar el contenido del campo Custom.ReleaseNote
"""

from src.tools.azure_devops_integration import AzureDevOpsClient

# Primero buscar un PBI de prueba
client = AzureDevOpsClient()

print("Buscando PBI de prueba...")
pbis = client.search_work_items(
    title_contains="AI-Generated",
    work_item_type="Product Backlog Item",
    tags=["AI-Generated"],
    max_results=1
)

if not pbis:
    print("❌ No se encontraron PBIs de prueba")
else:
    pbi_id = pbis[0]['id']
    print(f"✅ PBI encontrado: #{pbi_id}")
    
    pbi = client.get_work_item(pbi_id)
    
    if pbi:
        release_note = pbi['fields'].get('Custom.ReleaseNote', 'NO ENCONTRADO')
        print("=" * 70)
        print(f"📝 Campo Custom.ReleaseNote del PBI #{pbi_id}:")
        print("=" * 70)
        print(release_note)
        print("\n" + "=" * 70)
        print(f"Longitud total: {len(release_note)} caracteres")
    else:
        print("❌ Error al obtener el PBI")
