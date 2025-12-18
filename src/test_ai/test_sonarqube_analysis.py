"""
Script de prueba para verificar que SonarQube detecta errores
"""
import sys
from pathlib import Path

# Añadir src al path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from config.settings import settings
from tools.sonarqube_mcp import analizar_codigo_con_sonarqube
from utils.logger import setup_logger

logger = setup_logger(__name__, level=settings.get_log_level())

def test_sonarqube_error_detection():
    """Prueba que SonarQube detecta errores en código problemático"""
    
    print("=" * 70)
    print("🧪 TEST: DETECCIÓN DE ERRORES CON SONARQUBE")
    print("=" * 70)
    print()
    
    # Leer el archivo con errores
    test_file = Path(__file__).parent / "test_sonarqube_errors.js"
    
    if not test_file.exists():
        print(f"❌ Archivo de prueba no encontrado: {test_file}")
        return False
    
    print(f"📄 Leyendo archivo: {test_file.name}")
    with open(test_file, 'r', encoding='utf-8') as f:
        codigo_con_errores = f.read()
    
    print(f"📏 Tamaño del código: {len(codigo_con_errores)} caracteres")
    print()
    
    # Analizar con SonarQube
    print("🔍 Iniciando análisis con SonarQube...")
    print(f"   SONARSCANNER_ENABLED: {settings.SONARSCANNER_ENABLED}")
    print(f"   SONARQUBE_URL: {settings.SONARQUBE_URL}")
    print(f"   SONARQUBE_TOKEN: {'✅ Configurado' if settings.SONARQUBE_TOKEN else '❌ NO configurado'}")
    print()
    
    resultado = analizar_codigo_con_sonarqube(
        codigo=codigo_con_errores,
        nombre_archivo="test_sonarqube_errors.js",
        branch_name=None
    )
    
    # Analizar resultados
    print("=" * 70)
    print("📊 RESULTADOS DEL ANÁLISIS")
    print("=" * 70)
    print()
    
    success = resultado.get("success", False)
    issues = resultado.get("issues", [])
    summary = resultado.get("summary", {})
    source = resultado.get("source", "unknown")
    
    print(f"✅ Análisis exitoso: {success}")
    print(f"📍 Fuente: {source}")
    print(f"🔍 Issues encontrados: {len(issues)}")
    print()
    
    if summary:
        print("📈 RESUMEN POR SEVERIDAD:")
        by_severity = summary.get("by_severity", {})
        for severity, count in sorted(by_severity.items(), reverse=True):
            emoji = {
                "BLOCKER": "🔴",
                "CRITICAL": "🟠",
                "MAJOR": "🟡",
                "MINOR": "🔵",
                "INFO": "⚪"
            }.get(severity, "⚫")
            print(f"   {emoji} {severity}: {count}")
        
        print()
        print("📊 RESUMEN POR TIPO:")
        by_type = summary.get("by_type", {})
        for issue_type, count in sorted(by_type.items()):
            emoji = {
                "BUG": "🐛",
                "VULNERABILITY": "🔓",
                "CODE_SMELL": "👃",
                "SECURITY_HOTSPOT": "🔥"
            }.get(issue_type, "❓")
            print(f"   {emoji} {issue_type}: {count}")
    
    print()
    
    # Mostrar algunos issues de ejemplo
    if issues:
        print("=" * 70)
        print("🔍 EJEMPLOS DE ISSUES DETECTADOS (primeros 5)")
        print("=" * 70)
        print()
        
        for i, issue in enumerate(issues[:5], 1):
            print(f"{i}. [{issue.get('severity', 'UNKNOWN')}] {issue.get('rule', 'UNKNOWN')}")
            print(f"   📝 {issue.get('message', 'Sin mensaje')}")
            if issue.get('line'):
                print(f"   📍 Línea: {issue.get('line')}")
            print()
    
    # Verificar que se detectaron errores
    print("=" * 70)
    print("🎯 VERIFICACIÓN")
    print("=" * 70)
    print()
    
    if len(issues) > 0:
        print(f"✅ TEST EXITOSO: Se detectaron {len(issues)} issues")
        print("   El análisis de SonarQube está funcionando correctamente")
        return True
    else:
        print("⚠️  ADVERTENCIA: No se detectaron issues")
        print("   Posibles causas:")
        print("   - SonarScanner CLI no está conectado al servidor")
        print("   - Análisis estático tiene reglas limitadas")
        print("   - El código no tiene errores detectables")
        return False

if __name__ == "__main__":
    try:
        success = test_sonarqube_error_detection()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
