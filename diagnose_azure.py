"""
Script de diagnóstico para problemas de conexión con Azure DevOps.
Ejecutar: python diagnose_azure.py
"""

import os
import sys
import base64
import requests
from pathlib import Path
from dotenv import load_dotenv

# Verificar si existe el archivo .env en src/
env_file = Path("src/.env")
env_example = Path(".env.example")

# Asegurar que el directorio src existe
src_dir = Path("src")
if not src_dir.exists():
    print(f"❌ Directorio src/ no encontrado en {os.getcwd()}")
    sys.exit(1)

if not env_file.exists():
    print("=" * 60)
    print("⚠️  ARCHIVO .env NO ENCONTRADO EN src/")
    print("=" * 60)
    print(f"\nEl archivo .env no existe en: {env_file.absolute()}")
    print(f"Directorio actual: {os.getcwd()}")
    
    if env_example.exists():
        print("\n✅ Se encontró .env.example en la raíz")
        print(f"\n📝 Se creará src/.env desde .env.example")
        respuesta = input("\n¿Deseas crear src/.env desde .env.example? (s/n): ")
        
        if respuesta.lower() in ['s', 'si', 'sí', 'y', 'yes']:
            import shutil
            shutil.copy(env_example, env_file)
            print(f"\n✅ Archivo .env creado en: {env_file.absolute()}")
            print("\n📝 Próximos pasos:")
            print(f"   1. Abre el archivo: {env_file.absolute()}")
            print("   2. Configura tus credenciales de Azure DevOps:")
            print("      • AZURE_DEVOPS_ENABLED=true")
            print("      • AZURE_DEVOPS_ORG=cegid")
            print("      • AZURE_DEVOPS_PROJECT=PeopleNet")
            print("      • AZURE_DEVOPS_PAT=tu-personal-access-token")
            print("\n   3. Para obtener el PAT:")
            print("      https://dev.azure.com/cegid/_usersSettings/tokens")
            print("\n   4. Vuelve a ejecutar: python diagnose_azure.py")
            sys.exit(0)
        else:
            print("\n📝 Para crear src/.env manualmente:")
            print(f"   1. Copia .env.example a src/.env:")
            print("      copy .env.example src\\.env")
            print("   2. Edita src/.env con tus credenciales")
            print("   3. Ejecuta de nuevo este script")
            sys.exit(1)
    else:
        print("\n❌ Tampoco se encontró .env.example en la raíz")
        print(f"\n📝 Crea un archivo en: {env_file.absolute()}")
        print("\nCon este contenido:")
        print("\n" + "-" * 60)
        print("GEMINI_API_KEY=tu-gemini-api-key")
        print("E2B_API_KEY=tu-e2b-api-key")
        print("")
        print("# Azure DevOps")
        print("AZURE_DEVOPS_ENABLED=true")
        print("AZURE_DEVOPS_ORG=tu-organizacion")
        print("AZURE_DEVOPS_PROJECT=tu-proyecto")
        print("AZURE_DEVOPS_PAT=tu-personal-access-token")
        print("-" * 60)
        sys.exit(1)

# Cargar variables de entorno desde src/.env
load_dotenv(dotenv_path=env_file)

print("=" * 60)
print("🔍 DIAGNÓSTICO DE AZURE DEVOPS")
print("=" * 60)
print(f"\n✅ Archivo .env encontrado: {env_file.absolute()}")

# 1. Verificar variables de entorno
org = os.getenv("AZURE_DEVOPS_ORG", "")
project = os.getenv("AZURE_DEVOPS_PROJECT", "")
pat = os.getenv("AZURE_DEVOPS_PAT", "")
enabled = os.getenv("AZURE_DEVOPS_ENABLED", "false")

print(f"\n1. Variables de entorno:")
print(f"   AZURE_DEVOPS_ENABLED: {enabled}")
print(f"   AZURE_DEVOPS_ORG: {org or '❌ NO CONFIGURADO'}")
print(f"   AZURE_DEVOPS_PROJECT: {project or '❌ NO CONFIGURADO'}")
print(f"   AZURE_DEVOPS_PAT: {'✅ Configurado (' + str(len(pat)) + ' chars)' if pat else '❌ NO CONFIGURADO'}")

if not all([org, project, pat]):
    print("\n❌ Configuración incompleta. Revisa tu archivo .env")
    print("\n📝 Pasos para configurar:")
    print("   1. Copia .env.example a .env")
    print("   2. Obtén un PAT de: https://dev.azure.com/{org}/_usersSettings/tokens")
    print("   3. Configura las variables en .env")
    exit(1)

# 2. Verificar codificación
credentials = f":{pat}"
encoded = base64.b64encode(credentials.encode()).decode()

print(f"\n2. Codificación PAT:")
print(f"   PAT Length: {len(pat)} caracteres")
print(f"   Encoded (primeros 20): {encoded[:20]}...")
print(f"   ℹ️  Un PAT válido tiene ~52 caracteres")

# 3. Test de conexión
url = f"https://dev.azure.com/{org}/_apis/projects/{project}?api-version=7.0"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Basic {encoded}"
}

print(f"\n3. Test de conexión:")
print(f"   URL: {url}")
print(f"   Realizando petición...")

try:
    response = requests.get(url, headers=headers, timeout=10)
    
    print(f"\n   Status Code: {response.status_code}")
    print(f"   Reason: {response.reason}")
    
    if response.status_code == 200:
        print("\n✅ ¡CONEXIÓN EXITOSA!")
        data = response.json()
        print(f"\n   📊 Información del Proyecto:")
        print(f"   • Nombre: {data.get('name', 'N/A')}")
        print(f"   • ID: {data.get('id', 'N/A')}")
        print(f"   • Estado: {data.get('state', 'N/A')}")
        print(f"   • URL: {data.get('url', 'N/A')}")
        
        print(f"\n   🎉 Todo está configurado correctamente!")
        print(f"   Ahora puedes ejecutar: python test_azure_devops_connection.py")
        
    elif response.status_code == 401:
        print("\n❌ ERROR 401: UNAUTHORIZED")
        print("\n   🔍 Diagnóstico:")
        print("   El servidor rechazó tus credenciales.")
        
        print("\n   ⚠️  Posibles causas:")
        print("   1. El PAT es inválido o expiró")
        print("   2. El PAT no tiene permisos de 'Work Items'")
        print("   3. El formato del PAT está corrupto (espacios, comillas, etc.)")
        print("   4. El PAT fue revocado")
        
        print("\n   ✅ Solución paso a paso:")
        print(f"   1. Ve a: https://dev.azure.com/{org}/_usersSettings/tokens")
        print("   2. Genera un NUEVO token:")
        print("      • Name: Sistema-Multiagente")
        print("      • Organization: Selecciona tu organización")
        print("      • Expiration: 90 días (recomendado)")
        print("      • Scopes: Work Items (Read, write, & manage)")
        print("   3. Click 'Create' y COPIA el token inmediatamente")
        print("   4. Actualiza .env:")
        print(f"      AZURE_DEVOPS_PAT=<pega-el-token-aqui>")
        print("   5. Reinicia el terminal y vuelve a ejecutar este script")
        
    elif response.status_code == 404:
        print("\n❌ ERROR 404: NOT FOUND")
        print(f"\n   🔍 Diagnóstico:")
        print(f"   El proyecto '{project}' no existe en la organización '{org}'")
        
        print("\n   ⚠️  Posibles causas:")
        print("   1. El nombre del proyecto está mal escrito (es case-sensitive)")
        print("   2. No tienes permisos para ver este proyecto")
        print("   3. El proyecto fue eliminado o movido")
        
        print("\n   ✅ Solución:")
        print(f"   1. Ve a: https://dev.azure.com/{org}")
        print("   2. Verifica el nombre EXACTO del proyecto")
        print("   3. Actualiza AZURE_DEVOPS_PROJECT en .env con el nombre correcto")
        
    elif response.status_code == 203:
        print("\n⚠️  WARNING 203: Non-Authoritative Information")
        print("   La conexión funciona pero puede haber un proxy intermedio")
        print("   Esto generalmente está bien, continúa con el test")
        
    else:
        print(f"\n❌ ERROR {response.status_code}")
        print(f"\n   Respuesta del servidor:")
        print(f"   {response.text[:300]}")
        print(f"\n   🔍 Consulta la documentación:")
        print(f"   https://learn.microsoft.com/en-us/rest/api/azure/devops/")
        
except requests.exceptions.Timeout:
    print("\n❌ TIMEOUT: No se pudo conectar en 10 segundos")
    print("\n   ⚠️  Posibles causas:")
    print("   1. Problemas de conexión a internet")
    print("   2. Firewall bloqueando dev.azure.com")
    print("   3. VPN o proxy interferiendo")
    
    print("\n   ✅ Solución:")
    print("   1. Verifica tu conexión a internet")
    print("   2. Intenta abrir https://dev.azure.com en tu navegador")
    print("   3. Si usas VPN, intenta desactivarla temporalmente")
    
except requests.exceptions.ConnectionError as e:
    print("\n❌ CONNECTION ERROR: No se pudo conectar al servidor")
    print(f"\n   Error: {str(e)[:200]}")
    print("\n   ⚠️  Posibles causas:")
    print("   1. Sin conexión a internet")
    print("   2. DNS no resuelve dev.azure.com")
    print("   3. Firewall bloqueando conexiones HTTPS")
    
except Exception as e:
    print(f"\n❌ EXCEPCIÓN INESPERADA: {type(e).__name__}")
    print(f"   Mensaje: {str(e)[:200]}")
    print(f"\n   Por favor reporta este error en GitHub Issues")

print("\n" + "=" * 60)
print("🔍 Fin del diagnóstico")
print("=" * 60)

# 4. Sugerencias adicionales
if response.status_code == 401:
    print("\n💡 Tip: Si acabas de crear el PAT, espera 1-2 minutos")
    print("   Los cambios en Azure DevOps pueden tardar en propagarse")
    
print("\n📚 Documentación adicional:")
print("   • Guía completa: AZURE_DEVOPS_INTEGRATION.md")
print("   • Quick start: AZURE_DEVOPS_QUICKSTART.md")
print("   • Troubleshooting: TROUBLESHOOTING_401.md")
