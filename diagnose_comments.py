"""
Script de diagnóstico para verificar permisos de comentarios en Azure DevOps.
"""

import os
import sys

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.config.settings import settings
from src.tools.azure_devops_integration import AzureDevOpsClient

def diagnose_comment_permissions():
    """
    Diagnostica por qué no se pueden agregar comentarios a work items.
    """
    print("=" * 70)
    print("🔍 DIAGNÓSTICO: Permisos de Comentarios en Azure DevOps")
    print("=" * 70)
    
    if not settings.AZURE_DEVOPS_ENABLED:
        print("\n❌ AZURE_DEVOPS_ENABLED está deshabilitado")
        return
    
    print(f"\n📋 Configuración actual:")
    print(f"   • Organización: {settings.AZURE_DEVOPS_ORG}")
    print(f"   • Proyecto: {settings.AZURE_DEVOPS_PROJECT}")
    print(f"   • Area Path: {settings.AZURE_AREA_PATH or '(no configurado)'}")
    print(f"   • Iteration Path: {settings.AZURE_ITERATION_PATH or '(no configurado)'}")
    
    client = AzureDevOpsClient()
    
    # Test 1: Verificar conexión
    print("\n" + "=" * 70)
    print("TEST 1: Verificar conexión básica")
    print("-" * 70)
    if client.test_connection():
        print("✅ Conexión exitosa")
    else:
        print("❌ Error de conexión")
        return
    
    # Test 2: Buscar un PBI existente
    print("\n" + "=" * 70)
    print("TEST 2: Buscar PBI de prueba")
    print("-" * 70)
    
    pbis = client.search_work_items(
        title_contains="AI-Generated",
        work_item_type="Product Backlog Item",
        tags=["AI-Generated"],
        max_results=1
    )
    
    if not pbis:
        print("❌ No se encontraron PBIs de prueba")
        print("   Crea un PBI primero usando el sistema multiagente")
        return
    
    pbi = pbis[0]
    pbi_id = pbi['id']
    pbi_title = pbi['fields'].get('System.Title', 'N/A')
    pbi_area = pbi['fields'].get('System.AreaPath', 'N/A')
    pbi_state = pbi['fields'].get('System.State', 'N/A')
    
    print(f"✅ PBI encontrado:")
    print(f"   • ID: #{pbi_id}")
    print(f"   • Título: {pbi_title}")
    print(f"   • Area Path: {pbi_area}")
    print(f"   • Estado: {pbi_state}")
    print(f"   • URL: {pbi['_links']['html']['href']}")
    
    # Test 3: Intentar agregar un comentario de prueba
    print("\n" + "=" * 70)
    print("TEST 3: Intentar agregar comentario de prueba")
    print("-" * 70)
    
    test_comment = "🧪 Test de permisos - Este es un comentario de prueba para verificar permisos."
    
    print(f"Intentando agregar comentario al PBI #{pbi_id}...")
    success = client.add_comment(pbi_id, test_comment)
    
    if success:
        print("✅ Comentario agregado exitosamente")
        print("   El PAT tiene los permisos correctos")
    else:
        print("❌ No se pudo agregar el comentario")
        print("\n📋 Posibles causas:")
        print("   1. El PAT no tiene el scope 'Work Items (Read, Write & Manage)'")
        print("   2. El usuario no tiene permisos en el Area Path específico")
        print("   3. El proyecto tiene restricciones de seguridad especiales")
        
    # Test 4: Verificar información del usuario actual
    print("\n" + "=" * 70)
    print("TEST 4: Verificar información del usuario")
    print("-" * 70)
    
    try:
        import requests
        url = f"https://vssps.dev.azure.com/{settings.AZURE_DEVOPS_ORG}/_apis/profile/profiles/me?api-version=6.0"
        headers = {"Authorization": f"Basic {client._encode_pat()}"}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            profile = response.json()
            print(f"✅ Usuario autenticado:")
            print(f"   • Display Name: {profile.get('displayName', 'N/A')}")
            print(f"   • Email: {profile.get('emailAddress', 'N/A')}")
            print(f"   • ID: {profile.get('id', 'N/A')}")
        else:
            print(f"⚠️  No se pudo obtener información del perfil: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Error al obtener perfil: {e}")
    
    # Test 5: Listar comentarios existentes (sin crear)
    print("\n" + "=" * 70)
    print("TEST 5: Verificar si puede LEER comentarios")
    print("-" * 70)
    
    try:
        url = f"{client.base_url}/{client.project}/_apis/wit/workitems/{pbi_id}/comments?api-version=7.0-preview.3"
        headers = {"Authorization": f"Basic {client._encode_pat()}"}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            comments_data = response.json()
            comment_count = comments_data.get('count', 0)
            print(f"✅ Puede leer comentarios")
            print(f"   • Total de comentarios en el PBI: {comment_count}")
            
            if comment_count > 0:
                print("\n   Últimos comentarios:")
                for comment in comments_data.get('comments', [])[:3]:
                    text = comment.get('text', '')[:100]
                    print(f"   - {text}...")
        else:
            print(f"❌ No puede leer comentarios: {response.status_code}")
            print(f"   Respuesta: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Error al leer comentarios: {e}")
    
    # Resumen
    print("\n" + "=" * 70)
    print("📊 RESUMEN DEL DIAGNÓSTICO")
    print("=" * 70)
    
    print("\n💡 Recomendaciones:")
    print("   1. Verifica que el PAT tenga el scope 'Work Items (Read, Write & Manage)'")
    print("   2. Verifica permisos del usuario en el Area Path del proyecto")
    print("   3. Si el problema persiste, intenta:")
    print("      - Crear un nuevo PAT con todos los scopes")
    print("      - Verificar permisos a nivel de proyecto en Azure DevOps")
    print("      - Contactar al administrador del proyecto")
    
    print("\n🔗 Enlaces útiles:")
    print(f"   • Proyecto: https://dev.azure.com/{settings.AZURE_DEVOPS_ORG}/{settings.AZURE_DEVOPS_PROJECT}")
    print(f"   • Security: https://dev.azure.com/{settings.AZURE_DEVOPS_ORG}/{settings.AZURE_DEVOPS_PROJECT}/_settings/")
    print(f"   • PAT Management: https://dev.azure.com/{settings.AZURE_DEVOPS_ORG}/_usersSettings/tokens")


if __name__ == "__main__":
    diagnose_comment_permissions()
