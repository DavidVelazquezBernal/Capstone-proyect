"""
Script de prueba para demostrar el adjunto de archivos a work items en Azure DevOps.

Este script:
1. Crea un PBI de prueba
2. Crea 2 Tasks asociadas (Implementación y Testing)
3. Adjunta archivos de ejemplo a los work items

Autor: Sistema Multiagente
Fecha: 2024
"""

import os
from src.tools.azure_devops_integration import AzureDevOpsClient
from src.config.settings import settings


def main():
    """Función principal de demostración."""
    print("=" * 60)
    print("🔬 TEST: Adjuntar archivos a Work Items en Azure DevOps")
    print("=" * 60)
    
    # Inicializar cliente
    azure_client = AzureDevOpsClient()
    
    # Probar conexión
    if not azure_client.test_connection():
        print("❌ Error: No se pudo conectar a Azure DevOps")
        return
    
    # 1. Crear PBI de prueba
    print("\n📋 PASO 1: Creando PBI de prueba...")
    pbi = azure_client.create_pbi(
        title="[TEST] PBI para probar adjuntos de archivos",
        description="""
        <h3>Objetivo</h3>
        <p>Este PBI es una prueba del sistema de adjuntos automáticos</p>
        
        <h3>Funcionalidad a Probar</h3>
        <ul>
            <li>Adjuntar archivos al PBI</li>
            <li>Adjuntar archivos a Tasks relacionadas</li>
            <li>Validar integridad de los adjuntos</li>
        </ul>
        """,
        acceptance_criteria="""
        1. El código final se adjunta al PBI y Task de Implementación
        2. Los tests unitarios se adjuntan al PBI y Task de Testing
        3. Los adjuntos tienen comentarios descriptivos
        """,
        story_points=2
    )
    
    if not pbi:
        print("❌ Error: No se pudo crear el PBI")
        return
    
    pbi_id = pbi['id']
    print(f"✅ PBI creado: #{pbi_id}")
    print(f"   📋 {pbi['fields']['System.Title']}")
    
    # 2. Crear Tasks
    print("\n⚙️ PASO 2: Creando Task de Implementación...")
    task_impl = azure_client.create_task(
        title="[TEST] Implementar función de prueba",
        description="<p>Tarea de prueba para adjuntar código</p>",
        parent_id=pbi_id,
        remaining_work=5,  # Fibonacci: 5 horas
        tags=["Test", "Implementation"]
    )
    
    if not task_impl:
        print("❌ Error: No se pudo crear Task de Implementación")
        return
    
    task_impl_id = task_impl['id']
    print(f"✅ Task Implementación creada: #{task_impl_id}")
    
    print("\n🧪 PASO 3: Creando Task de Testing...")
    task_test = azure_client.create_task(
        title="[TEST] Crear tests unitarios de prueba",
        description="<p>Tarea de prueba para adjuntar tests</p>",
        parent_id=pbi_id,
        remaining_work=3,  # Fibonacci: 3 horas
        tags=["Test", "Testing"]
    )
    
    if not task_test:
        print("❌ Error: No se pudo crear Task de Testing")
        return
    
    task_test_id = task_test['id']
    print(f"✅ Task Testing creada: #{task_test_id}")
    
    # 3. Crear archivos de prueba temporales
    print("\n📄 PASO 4: Creando archivos de prueba...")
    
    codigo_test_path = os.path.join(settings.OUTPUT_DIR, "codigo_test.ts")
    with open(codigo_test_path, 'w', encoding='utf-8') as f:
        f.write("""// Código de prueba generado por IA
export function sumarNumeros(a: number, b: number): number {
    return a + b;
}

export function restarNumeros(a: number, b: number): number {
    return a - b;
}
""")
    print(f"✅ Archivo creado: {codigo_test_path}")
    
    tests_test_path = os.path.join(settings.OUTPUT_DIR, "codigo_test.test.ts")
    with open(tests_test_path, 'w', encoding='utf-8') as f:
        f.write("""// Tests unitarios de prueba
import { describe, it, expect } from 'vitest';
import { sumarNumeros, restarNumeros } from './codigo_test';

describe('sumarNumeros', () => {
    it('debería sumar dos números positivos', () => {
        expect(sumarNumeros(2, 3)).toBe(5);
    });
    
    it('debería manejar números negativos', () => {
        expect(sumarNumeros(-1, -2)).toBe(-3);
    });
});

describe('restarNumeros', () => {
    it('debería restar dos números', () => {
        expect(restarNumeros(5, 3)).toBe(2);
    });
});
""")
    print(f"✅ Archivo creado: {tests_test_path}")
    
    # 4. Adjuntar archivos
    print("\n📎 PASO 5: Adjuntando archivos a work items...")
    print("-" * 60)
    
    # Adjuntar código al PBI
    print(f"\n📌 Adjuntando código al PBI #{pbi_id}...")
    if azure_client.attach_file(
        work_item_id=pbi_id,
        file_path=codigo_test_path,
        comment="✅ Código de implementación generado automáticamente"
    ):
        print(f"   ✅ Código adjuntado al PBI")
    else:
        print(f"   ❌ Error al adjuntar código al PBI")
    
    # Adjuntar código a Task Implementación
    print(f"\n📌 Adjuntando código a Task Implementación #{task_impl_id}...")
    if azure_client.attach_file(
        work_item_id=task_impl_id,
        file_path=codigo_test_path,
        comment="✅ Implementación completa - Revisión requerida"
    ):
        print(f"   ✅ Código adjuntado a Task Implementación")
    else:
        print(f"   ❌ Error al adjuntar código a Task Implementación")
    
    # Adjuntar tests al PBI
    print(f"\n📌 Adjuntando tests al PBI #{pbi_id}...")
    if azure_client.attach_file(
        work_item_id=pbi_id,
        file_path=tests_test_path,
        comment="✅ Tests unitarios - Cobertura completa"
    ):
        print(f"   ✅ Tests adjuntados al PBI")
    else:
        print(f"   ❌ Error al adjuntar tests al PBI")
    
    # Adjuntar tests a Task Testing
    print(f"\n📌 Adjuntando tests a Task Testing #{task_test_id}...")
    if azure_client.attach_file(
        work_item_id=task_test_id,
        file_path=tests_test_path,
        comment="✅ Suite de tests unitarios - Todos pasando"
    ):
        print(f"   ✅ Tests adjuntados a Task Testing")
    else:
        print(f"   ❌ Error al adjuntar tests a Task Testing")
    
    # 5. Resumen final
    print("\n" + "=" * 60)
    print("🎉 PRUEBA COMPLETADA")
    print("=" * 60)
    print(f"📋 PBI creado: #{pbi_id}")
    print(f"⚙️ Task Implementación: #{task_impl_id}")
    print(f"🧪 Task Testing: #{task_test_id}")
    print(f"\n🔗 Ver en Azure DevOps:")
    print(f"   https://dev.azure.com/cegid/PeopleNet/_workitems/edit/{pbi_id}")
    print("=" * 60)


if __name__ == "__main__":
    main()
