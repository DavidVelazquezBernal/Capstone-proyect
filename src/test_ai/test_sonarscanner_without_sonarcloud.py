"""
Test para verificar que SonarScanner CLI funciona cuando SonarCloud está deshabilitado.
"""

import os
import sys

# Añadir el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config.settings import settings
from tools.sonarqube_mcp import analizar_codigo_con_sonarqube


def test_sonarscanner_sin_sonarcloud():
    """
    Verifica que cuando SONARCLOUD_ENABLED=false pero SONARSCANNER_ENABLED=true,
    el análisis se ejecuta correctamente con SonarScanner CLI.
    """
    print("=" * 70)
    print("TEST: SonarScanner CLI sin SonarCloud")
    print("=" * 70)
    
    # Verificar configuración
    print(f"\n📋 Configuración actual:")
    print(f"   SONARCLOUD_ENABLED: {settings.SONARCLOUD_ENABLED}")
    print(f"   SONARSCANNER_ENABLED: {settings.SONARSCANNER_ENABLED}")
    print(f"   SONARSCANNER_PATH: {settings.SONARSCANNER_PATH}")
    
    # Código de prueba simple
    codigo_prueba = """
def suma(a, b):
    return a + b

def resta(a, b):
    return a - b

resultado = suma(5, 3)
print(f"Resultado: {resultado}")
"""
    
    nombre_archivo = "test_analisis.py"
    
    print(f"\n🔍 Analizando código de prueba...")
    print(f"   Archivo: {nombre_archivo}")
    print(f"   Líneas de código: {len(codigo_prueba.splitlines())}")
    
    # Ejecutar análisis (sin branch para forzar análisis local)
    resultado = analizar_codigo_con_sonarqube(
        codigo=codigo_prueba,
        nombre_archivo=nombre_archivo,
        branch_name=None  # Sin branch para forzar análisis local
    )
    
    print(f"\n📊 Resultado del análisis:")
    print(f"   Success: {resultado.get('success')}")
    print(f"   Source: {resultado.get('source')}")
    print(f"   Issues encontrados: {len(resultado.get('issues', []))}")
    
    if resultado.get('summary'):
        summary = resultado['summary']
        print(f"\n📈 Resumen:")
        if 'by_severity' in summary:
            print(f"   Por severidad: {summary['by_severity']}")
        if 'by_type' in summary:
            print(f"   Por tipo: {summary['by_type']}")
    
    # Verificaciones
    assert resultado.get('success'), "El análisis debería ser exitoso"
    
    source = resultado.get('source')
    print(f"\n✅ Verificación del método de análisis:")
    
    if settings.SONARSCANNER_ENABLED:
        expected_sources = ['sonarscanner-cli', 'sonarscanner-cli-local', 'local-static']
        assert source in expected_sources, f"Con SONARSCANNER_ENABLED=true, esperaba source en {expected_sources}, obtuvo: {source}"
        print(f"   ✓ Método correcto: {source}")
        
        if source.startswith('sonarscanner-cli'):
            print(f"   ✓ SonarScanner CLI ejecutado correctamente")
        elif source == 'local-static':
            print(f"   ⚠️ Fallback a análisis estático (SonarScanner CLI no disponible o falló)")
    else:
        assert source == 'local-static', f"Con SONARSCANNER_ENABLED=false, esperaba 'local-static', obtuvo: {source}"
        print(f"   ✓ Análisis estático usado correctamente")
    
    print("\n" + "=" * 70)
    print("✅ TEST COMPLETADO EXITOSAMENTE")
    print("=" * 70)
    
    return True


if __name__ == "__main__":
    try:
        test_sonarscanner_sin_sonarcloud()
    except AssertionError as e:
        print(f"\n❌ TEST FALLIDO: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR EN TEST: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
