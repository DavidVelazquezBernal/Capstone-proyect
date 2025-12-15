"""
Script de verificación: Confirma que no hay archivos temp_analysis después de la ejecución.
"""

import sys
import os
from pathlib import Path

# Añadir src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config.settings import settings


def verificar_limpieza_output():
    """Verifica que no existan archivos temp_analysis en el directorio output"""
    
    print("\n" + "=" * 80)
    print("🔍 VERIFICACIÓN: Archivos Temporales en Output")
    print("=" * 80)
    
    output_dir = Path(settings.OUTPUT_DIR)
    print(f"\n📁 Directorio: {output_dir}")
    
    # Buscar archivos temp_analysis
    archivos_temp = list(output_dir.glob("temp_analysis_*"))
    
    if archivos_temp:
        print(f"\n❌ PROBLEMA: Encontrados {len(archivos_temp)} archivos temporales:")
        for archivo in archivos_temp:
            tamaño = archivo.stat().st_size
            print(f"   - {archivo.name} ({tamaño} bytes)")
        
        print("\n⚠️ Estos archivos deberían haberse eliminado automáticamente.")
        print("💡 Solución: Ejecutar 'Remove-Item output/temp_analysis_* -Force'")
        
        return False
    else:
        print("\n✅ No se encontraron archivos temporales")
        print("✅ El sistema está limpiando correctamente")
        
        return True


def listar_archivos_output():
    """Lista todos los archivos en output para inspección"""
    
    print("\n" + "=" * 80)
    print("📋 CONTENIDO DEL DIRECTORIO OUTPUT")
    print("=" * 80)
    
    output_dir = Path(settings.OUTPUT_DIR)
    
    # Agrupar por tipo
    archivos_por_tipo = {
        'Requisitos (Product Owner)': [],
        'Código (Desarrollador)': [],
        'Reportes SonarQube': [],
        'Instrucciones SonarQube': [],
        'Tests': [],
        'Resultados': [],
        'Temporales': [],
        'Otros': []
    }
    
    for archivo in sorted(output_dir.iterdir()):
        if archivo.is_file():
            nombre = archivo.name
            if nombre.startswith('1_product_owner'):
                archivos_por_tipo['Requisitos (Product Owner)'].append(nombre)
            elif nombre.startswith('2_desarrollador'):
                archivos_por_tipo['Código (Desarrollador)'].append(nombre)
            elif nombre.startswith('3_sonarqube_report'):
                archivos_por_tipo['Reportes SonarQube'].append(nombre)
            elif nombre.startswith('3_sonarqube_instrucciones'):
                archivos_por_tipo['Instrucciones SonarQube'].append(nombre)
            elif nombre.startswith('unit_tests'):
                archivos_por_tipo['Tests'].append(nombre)
            elif nombre.startswith('4_probador') or nombre.startswith('5_stakeholder'):
                archivos_por_tipo['Resultados'].append(nombre)
            elif nombre.startswith('temp_analysis'):
                archivos_por_tipo['Temporales'].append(nombre)
            else:
                archivos_por_tipo['Otros'].append(nombre)
    
    for categoria, archivos in archivos_por_tipo.items():
        if archivos:
            print(f"\n📂 {categoria} ({len(archivos)}):")
            for archivo in archivos:
                print(f"   - {archivo}")
    
    # Contar temporales
    temporales = archivos_por_tipo['Temporales']
    if temporales:
        print(f"\n⚠️ ATENCIÓN: {len(temporales)} archivos temporales encontrados")
    else:
        print(f"\n✅ Sin archivos temporales")


if __name__ == "__main__":
    limpio = verificar_limpieza_output()
    listar_archivos_output()
    
    print("\n" + "=" * 80)
    if limpio:
        print("✅ VERIFICACIÓN EXITOSA")
    else:
        print("⚠️ REQUIERE LIMPIEZA")
    print("=" * 80)
