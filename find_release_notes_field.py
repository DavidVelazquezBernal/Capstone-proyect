"""
Script para buscar el campo de Release Notes en Azure DevOps.
"""

import requests
from src.tools.azure_devops_integration import AzureDevOpsClient

client = AzureDevOpsClient()

# Obtener todos los campos del tipo PBI
url = f"{client.base_url}/{client.project}/_apis/wit/workitemtypes/Product Backlog Item/fields?api-version=7.0"
headers = {"Authorization": f"Basic {client._encode_pat()}"}

response = requests.get(url, headers=headers, timeout=30)

if response.status_code == 200:
    fields = response.json()['value']
    
    print("=" * 70)
    print("Campos disponibles para Product Backlog Item:")
    print("=" * 70)
    
    # Buscar campos relacionados con notes o release
    relevant_fields = [
        f for f in fields 
        if 'note' in f['name'].lower() 
        or 'release' in f['name'].lower() 
        or 'description' in f['name'].lower()
        or 'acceptance' in f['name'].lower()
    ]
    
    if relevant_fields:
        print("\nCampos relacionados con notas/release/descripción:")
        for field in relevant_fields:
            print(f"\n• {field['name']}")
            print(f"  Reference Name: {field['referenceName']}")
            print(f"  Type: {field.get('type', 'N/A')}")
            print(f"  Can Sort By: {field.get('canSortBy', 'N/A')}")
    
    # Buscar campos personalizados (Custom)
    print("\n" + "=" * 70)
    print("Campos personalizados del proyecto:")
    print("=" * 70)
    
    custom_fields = [f for f in fields if f['referenceName'].startswith('Custom.')]
    
    if custom_fields:
        for field in custom_fields[:20]:  # Primeros 20
            print(f"\n• {field['name']}")
            print(f"  Reference Name: {field['referenceName']}")
            print(f"  Type: {field.get('type', 'N/A')}")
    else:
        print("No se encontraron campos personalizados")
    
else:
    print(f"Error: {response.status_code}")
    print(response.text[:500])
