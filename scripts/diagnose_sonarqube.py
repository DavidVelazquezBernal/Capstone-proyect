"""
Script de diagnóstico para SonarQube/SonarCloud
Ayuda a identificar exactamente cuál es el problema de configuración
"""
import os
import sys
from pathlib import Path

# Añadir src al path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from config.settings import settings

def diagnose():
    print("=" * 70)
    print("🔍 DIAGNÓSTICO DE CONFIGURACIÓN SONARQUBE/SONARCLOUD")
    print("=" * 70)
    print()
    
    # 1. Verificar SonarScanner CLI
    print("📋 1. SONARSCANNER CLI")
    print(f"   SONARSCANNER_ENABLED: {settings.SONARSCANNER_ENABLED}")
    print(f"   SONARSCANNER_PATH: {settings.SONARSCANNER_PATH}")
    print()
    
    # 2. Verificar SonarCloud
    print("☁️  2. SONARCLOUD")
    print(f"   SONARCLOUD_ENABLED: {settings.SONARCLOUD_ENABLED}")
    print(f"   SONARCLOUD_TOKEN: {'✅ Configurado' if settings.SONARCLOUD_TOKEN else '❌ NO configurado'}")
    if settings.SONARCLOUD_TOKEN:
        print(f"   Token (primeros 10 chars): {settings.SONARCLOUD_TOKEN[:10]}...")
    print(f"   SONARCLOUD_ORGANIZATION: {settings.SONARCLOUD_ORGANIZATION if settings.SONARCLOUD_ORGANIZATION else '❌ NO configurado'}")
    print(f"   SONARCLOUD_PROJECT_KEY: {settings.SONARCLOUD_PROJECT_KEY if settings.SONARCLOUD_PROJECT_KEY else '❌ NO configurado'}")
    print()
    
    # 3. Verificar SonarQube local
    print("🖥️  3. SONARQUBE LOCAL")
    print(f"   SONARQUBE_URL: {settings.SONARQUBE_URL}")
    print(f"   SONARQUBE_TOKEN: {'✅ Configurado' if settings.SONARQUBE_TOKEN else '❌ NO configurado'}")
    if settings.SONARQUBE_TOKEN:
        print(f"   Token (primeros 10 chars): {settings.SONARQUBE_TOKEN[:10]}...")
    print(f"   SONARQUBE_PROJECT_KEY: {settings.SONARQUBE_PROJECT_KEY if settings.SONARQUBE_PROJECT_KEY else '❌ NO configurado'}")
    print(f"   SONARQUBE_PROJECT_NAME: {settings.SONARQUBE_PROJECT_NAME if settings.SONARQUBE_PROJECT_NAME else '❌ NO configurado'}")
    print()
    
    # 4. Análisis del problema
    print("=" * 70)
    print("🔍 ANÁLISIS DEL PROBLEMA")
    print("=" * 70)
    
    # Detectar configuración actual
    if settings.SONARSCANNER_ENABLED and settings.SONARQUBE_URL == "https://sonarcloud.io":
        print("⚠️  PROBLEMA DETECTADO:")
        print("   - SONARSCANNER_ENABLED=true")
        print("   - SONARQUBE_URL apunta a SonarCloud")
        print("   - Pero SONARCLOUD_ENABLED=false")
        print()
        print("🔧 SOLUCIÓN:")
        print("   Opción A: Usar SonarCloud")
        print("   - Cambiar: SONARSCANNER_ENABLED=false")
        print("   - Cambiar: SONARCLOUD_ENABLED=true")
        print("   - Configurar: SONARCLOUD_ORGANIZATION y SONARCLOUD_PROJECT_KEY")
        print()
        print("   Opción B: Usar servidor local")
        print("   - Cambiar: SONARQUBE_URL=http://localhost:9000")
        print("   - Iniciar servidor local con StartSonar-Java21.bat")
        print("   - Generar token en http://localhost:9000")
        print()
        print("   Opción C: Deshabilitar análisis de calidad")
        print("   - Cambiar: SONARSCANNER_ENABLED=false")
        print("   - Sistema usará análisis estático local")
    
    elif settings.SONARSCANNER_ENABLED and settings.SONARQUBE_URL.startswith("http://localhost"):
        print("⚠️  CONFIGURACIÓN DETECTADA:")
        print("   - SONARSCANNER_ENABLED=true")
        print("   - SONARQUBE_URL apunta a servidor local")
        print()
        print("🔍 VERIFICAR:")
        print("   1️⃣ ¿Está el servidor SonarQube corriendo?")
        print("      Ejecutar: C:\\sonarqube\\sonarqube-25.12.0.117093\\bin\\windows-x86-64\\StartSonar-Java21.bat")
        print("      Verificar: http://localhost:9000")
        print()
        print("   2️⃣ ¿El token es correcto?")
        print("      - Debe ser generado en http://localhost:9000 > My Account > Security")
        print("      - NO usar token de SonarCloud")
        print()
        print("   3️⃣ ¿El proyecto existe en el servidor?")
        print("      - Crear proyecto en http://localhost:9000")
        print("      - O dar permisos para crear proyectos automáticamente")
    
    elif settings.SONARCLOUD_ENABLED:
        if not settings.SONARCLOUD_ORGANIZATION or not settings.SONARCLOUD_PROJECT_KEY:
            print("⚠️  PROBLEMA DETECTADO:")
            print("   - SONARCLOUD_ENABLED=true")
            print("   - Pero faltan credenciales completas")
            print()
            print("🔧 SOLUCIÓN:")
            print("   1. Ir a https://sonarcloud.io")
            print("   2. Importar repositorio DavidVelazquezBernal/Multiagentes-Coding")
            print("   3. Obtener SONARCLOUD_ORGANIZATION y SONARCLOUD_PROJECT_KEY")
            print("   4. Configurar en .env")
        else:
            print("✅ Configuración de SonarCloud parece correcta")
    
    elif not settings.SONARSCANNER_ENABLED and not settings.SONARCLOUD_ENABLED:
        print("ℹ️  ANÁLISIS DE CALIDAD DESHABILITADO")
        print("   - Sistema usa análisis estático local como fallback")
        print("   - Esto es correcto si no quieres usar SonarQube/SonarCloud")
    
    print()
    print("=" * 70)

if __name__ == "__main__":
    diagnose()
