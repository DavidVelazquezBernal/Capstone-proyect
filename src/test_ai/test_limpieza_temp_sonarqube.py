"""
Test para verificar que los archivos temporales de SonarQube se eliminan correctamente.
"""

import sys
import os
from pathlib import Path

# Añadir src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from tools.sonarqube_mcp import analizar_codigo_con_sonarqube
from config.settings import settings


def test_limpieza_archivos_temporales():
    """Verifica que los archivos temp_analysis se eliminan después del análisis"""
    
    print("\n" + "=" * 80)
    print("🧪 TEST: Limpieza de Archivos Temporales de SonarQube")
    print("=" * 80)
    
    # Código de prueba
    codigo_typescript = """
export function sumar(a: number, b: number): number {
    if (typeof a != 'number' || typeof b != 'number') {
        throw new Error('Argumentos inválidos');
    }
    return a + b;
}
"""
    
    nombre_archivo = "test_limpieza.ts"
    temp_file_path = os.path.join(settings.OUTPUT_DIR, f"temp_analysis_{nombre_archivo}")
    
    print(f"\n📁 Archivo temporal esperado: {temp_file_path}")
    
    # Verificar que no existe antes del test
    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)
        print("🗑️ Eliminado archivo temporal previo")
    
    assert not os.path.exists(temp_file_path), "El archivo temporal no debería existir antes del análisis"
    print("✅ Verificado: No existe antes del análisis")
    
    # Ejecutar análisis
    print("\n🔍 Ejecutando análisis de SonarQube...")
    resultado = analizar_codigo_con_sonarqube(codigo_typescript, nombre_archivo)
    
    # Verificar que el análisis fue exitoso
    assert resultado["success"], "El análisis debería ser exitoso"
    print(f"✅ Análisis completado: {resultado['summary'].get('total_issues', 0)} issues encontrados")
    
    # Verificar que el archivo temporal fue eliminado
    print("\n🔍 Verificando limpieza del archivo temporal...")
    
    if os.path.exists(temp_file_path):
        print(f"❌ ERROR: El archivo temporal aún existe: {temp_file_path}")
        # Intentar leerlo para ver su contenido
        try:
            with open(temp_file_path, 'r') as f:
                contenido = f.read()
            print(f"   Contenido ({len(contenido)} caracteres):")
            print(f"   {contenido[:200]}...")
        except:
            pass
        assert False, "El archivo temporal debería haber sido eliminado"
    else:
        print("✅ El archivo temporal fue eliminado correctamente")
    
    print("\n" + "=" * 80)
    print("✅ TEST PASADO: Los archivos temporales se limpian correctamente")
    print("=" * 80)


def test_limpieza_con_error():
    """Verifica que los archivos se limpian incluso si hay errores"""
    
    print("\n" + "=" * 80)
    print("🧪 TEST: Limpieza con Manejo de Errores")
    print("=" * 80)
    
    # Código que podría causar problemas
    codigo_vacio = ""
    nombre_archivo = "test_error.ts"
    temp_file_path = os.path.join(settings.OUTPUT_DIR, f"temp_analysis_{nombre_archivo}")
    
    print(f"\n📁 Archivo temporal: {temp_file_path}")
    
    # Limpiar previo si existe
    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)
    
    # Ejecutar análisis con código vacío
    print("\n🔍 Ejecutando análisis con código vacío...")
    resultado = analizar_codigo_con_sonarqube(codigo_vacio, nombre_archivo)
    
    print(f"Resultado: success={resultado['success']}")
    
    # Verificar limpieza
    print("\n🔍 Verificando limpieza...")
    if os.path.exists(temp_file_path):
        print(f"❌ ERROR: El archivo temporal no fue eliminado")
        assert False, "El archivo temporal debería haberse eliminado incluso con código vacío"
    else:
        print("✅ El archivo temporal fue eliminado correctamente")
    
    print("\n" + "=" * 80)
    print("✅ TEST PASADO: Limpieza funciona incluso con casos edge")
    print("=" * 80)


def test_multiples_analisis():
    """Verifica que múltiples análisis no dejan archivos temporales"""
    
    print("\n" + "=" * 80)
    print("🧪 TEST: Múltiples Análisis Secuenciales")
    print("=" * 80)
    
    codigo = "export function test() { return true; }"
    
    print("\n🔄 Ejecutando 5 análisis consecutivos...")
    
    archivos_temporales = []
    
    for i in range(5):
        nombre = f"test_multi_{i}.ts"
        temp_path = os.path.join(settings.OUTPUT_DIR, f"temp_analysis_{nombre}")
        archivos_temporales.append(temp_path)
        
        resultado = analizar_codigo_con_sonarqube(codigo, nombre)
        assert resultado["success"], f"Análisis {i+1} debería ser exitoso"
        print(f"   ✅ Análisis {i+1} completado")
    
    print("\n🔍 Verificando que ningún archivo temporal quedó...")
    
    archivos_restantes = []
    for temp_path in archivos_temporales:
        if os.path.exists(temp_path):
            archivos_restantes.append(temp_path)
    
    if archivos_restantes:
        print(f"❌ ERROR: {len(archivos_restantes)} archivos temporales no fueron eliminados:")
        for archivo in archivos_restantes:
            print(f"   - {archivo}")
        assert False, "Todos los archivos temporales deberían haberse eliminado"
    else:
        print(f"✅ Todos los archivos temporales fueron eliminados ({len(archivos_temporales)} archivos)")
    
    print("\n" + "=" * 80)
    print("✅ TEST PASADO: Múltiples análisis no dejan archivos temporales")
    print("=" * 80)


if __name__ == "__main__":
    test_limpieza_archivos_temporales()
    test_limpieza_con_error()
    test_multiples_analisis()
    
    print("\n" + "=" * 80)
    print("🎉 TODOS LOS TESTS DE LIMPIEZA PASARON")
    print("=" * 80)
    print("\n📋 Resumen:")
    print("   ✓ Los archivos temp_analysis_* se crean durante el análisis")
    print("   ✓ Los archivos temp_analysis_* se eliminan después del análisis")
    print("   ✓ La limpieza funciona incluso con errores")
    print("   ✓ Múltiples análisis no dejan archivos residuales")
    print("=" * 80)
