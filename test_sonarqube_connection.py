"""
Script para verificar la conexión con SonarQube Server/Cloud.
Verifica que las credenciales estén correctamente configuradas.
"""

import sys
import os

# Añadir src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config.settings import settings


def verificar_configuracion():
    """Verifica que las variables de entorno estén configuradas."""
    print("=" * 60)
    print("🔍 VERIFICACIÓN DE CONFIGURACIÓN SONARQUBE")
    print("=" * 60)
    
    configurado = True
    
    # Verificar URL
    if settings.SONARQUBE_URL:
        print(f"✅ SONARQUBE_URL: {settings.SONARQUBE_URL}")
    else:
        print("❌ SONARQUBE_URL: No configurada")
        configurado = False
    
    # Verificar Token
    if settings.SONARQUBE_TOKEN:
        # Mostrar solo los primeros caracteres por seguridad
        token_preview = settings.SONARQUBE_TOKEN[:10] + "..." if len(settings.SONARQUBE_TOKEN) > 10 else settings.SONARQUBE_TOKEN
        print(f"✅ SONARQUBE_TOKEN: {token_preview}")
    else:
        print("❌ SONARQUBE_TOKEN: No configurado")
        configurado = False
    
    # Verificar Project Key
    if settings.SONARQUBE_PROJECT_KEY:
        print(f"✅ SONARQUBE_PROJECT_KEY: {settings.SONARQUBE_PROJECT_KEY}")
    else:
        print("❌ SONARQUBE_PROJECT_KEY: No configurado")
        configurado = False
    
    print("=" * 60)
    
    return configurado


def test_conexion():
    """Prueba la conexión con SonarQube."""
    try:
        import requests
    except ImportError:
        print("⚠️ Módulo 'requests' no instalado. Instalando...")
        os.system("pip install requests")
        import requests
    
    print("\n🔌 PROBANDO CONEXIÓN...")
    print("-" * 60)
    
    try:
        # Test endpoint de status
        url = f"{settings.SONARQUBE_URL}/api/system/status"
        headers = {}
        
        if settings.SONARQUBE_TOKEN:
            headers["Authorization"] = f"Bearer {settings.SONARQUBE_TOKEN}"
        
        print(f"📡 Conectando a: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Conexión exitosa")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Version: {data.get('version', 'unknown')}")
            return True
        elif response.status_code == 401:
            print(f"❌ Error de autenticación (401)")
            print(f"   El token es inválido o ha expirado")
            return False
        else:
            print(f"⚠️ Respuesta inesperada: {response.status_code}")
            print(f"   {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ No se pudo conectar a {settings.SONARQUBE_URL}")
        print(f"   Verifica que el servidor esté activo y accesible")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ Tiempo de espera agotado")
        print(f"   El servidor no responde")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        return False


def test_proyecto():
    """Verifica que el proyecto exista en SonarQube."""
    try:
        import requests
    except ImportError:
        return False
    
    print("\n📊 VERIFICANDO PROYECTO...")
    print("-" * 60)
    
    try:
        url = f"{settings.SONARQUBE_URL}/api/projects/search"
        headers = {"Authorization": f"Bearer {settings.SONARQUBE_TOKEN}"}
        params = {"projects": settings.SONARQUBE_PROJECT_KEY}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            components = data.get('components', [])
            
            if components:
                proyecto = components[0]
                print(f"✅ Proyecto encontrado")
                print(f"   Key: {proyecto.get('key')}")
                print(f"   Name: {proyecto.get('name')}")
                return True
            else:
                print(f"⚠️ Proyecto '{settings.SONARQUBE_PROJECT_KEY}' no encontrado")
                print(f"   Debes crear el proyecto en SonarQube primero")
                return False
        else:
            print(f"❌ Error al buscar proyecto: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error al verificar proyecto: {str(e)}")
        return False


def mostrar_instrucciones():
    """Muestra instrucciones para configurar SonarQube."""
    print("\n" + "=" * 60)
    print("📚 CÓMO CONFIGURAR SONARQUBE")
    print("=" * 60)
    print()
    print("1. Edita el archivo .env en la raíz del proyecto")
    print()
    print("2. Añade estas líneas:")
    print()
    print("   # SonarQube Configuration")
    print("   SONARQUBE_URL=https://sonarcloud.io")
    print("   SONARQUBE_TOKEN=tu_token_aqui")
    print("   SONARQUBE_PROJECT_KEY=tu_proyecto_key")
    print()
    print("3. Para obtener estas credenciales, consulta:")
    print("   📄 SONARQUBE_SETUP.md")
    print()
    print("=" * 60)


def main():
    """Función principal."""
    print("\n")
    
    # 1. Verificar configuración
    configurado = verificar_configuracion()
    
    if not configurado:
        print("\n⚠️ SonarQube no está configurado")
        print("   El sistema usará análisis estático básico (actual)")
        mostrar_instrucciones()
        return
    
    # 2. Probar conexión
    conexion_ok = test_conexion()
    
    if not conexion_ok:
        mostrar_instrucciones()
        return
    
    # 3. Verificar proyecto
    proyecto_ok = test_proyecto()
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📋 RESUMEN")
    print("=" * 60)
    print(f"Configuración: {'✅' if configurado else '❌'}")
    print(f"Conexión: {'✅' if conexion_ok else '❌'}")
    print(f"Proyecto: {'✅' if proyecto_ok else '⚠️'}")
    print("=" * 60)
    
    if configurado and conexion_ok and proyecto_ok:
        print("\n🎉 ¡Todo configurado correctamente!")
        print("   El sistema puede usar la API de SonarQube")
    elif configurado and conexion_ok and not proyecto_ok:
        print("\n⚠️ Conexión OK pero proyecto no encontrado")
        print("   Crea el proyecto en SonarQube o verifica el PROJECT_KEY")
    else:
        print("\n⚠️ Configuración incompleta o errónea")
        print("   El sistema usará análisis estático básico")
    
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Verificación cancelada")
    except Exception as e:
        print(f"\n❌ Error fatal: {str(e)}")
        import traceback
        traceback.print_exc()
