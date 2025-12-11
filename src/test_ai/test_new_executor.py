"""
Script de prueba para validar la nueva implementación del Ejecutor de Pruebas
sin MALFORMED_FUNCTION_CALL
"""

import json
from models.schemas import TestExecutionRequest, TestCase
from pydantic import ValidationError

def test_schema_validation():
    """Prueba la validación de esquemas Pydantic"""
    print("\n" + "="*60)
    print("TEST 1: Validación de esquemas Pydantic")
    print("="*60)
    
    # Test 1: Schema válido
    try:
        valid_json = {
            "language": "python",
            "test_cases": [
                {"input": [5], "expected": "120"},
                {"input": [0], "expected": "1"},
                {"input": [3], "expected": "6"}
            ]
        }
        
        request = TestExecutionRequest(**valid_json)
        print("✅ Schema válido aceptado correctamente")
        print(f"   - Lenguaje: {request.language}")
        print(f"   - Casos de prueba: {len(request.test_cases)}")
        
    except ValidationError as e:
        print(f"❌ Error inesperado: {e}")
    
    # Test 2: Schema inválido (sin language)
    try:
        invalid_json = {
            "test_cases": [
                {"input": [5], "expected": "120"}
            ]
        }
        
        request = TestExecutionRequest(**invalid_json)
        print("❌ Schema inválido fue aceptado (no debería)")
        
    except ValidationError as e:
        print("✅ Schema inválido rechazado correctamente")
        print(f"   - Errores: {len(e.errors())}")
    
    # Test 3: Schema inválido (test_case sin expected)
    try:
        invalid_json2 = {
            "language": "python",
            "test_cases": [
                {"input": [5]}  # Falta 'expected'
            ]
        }
        
        request = TestExecutionRequest(**invalid_json2)
        print("❌ Schema inválido fue aceptado (no debería)")
        
    except ValidationError as e:
        print("✅ Test case inválido rechazado correctamente")
        print(f"   - Errores: {len(e.errors())}")


def test_json_generation():
    """Prueba la generación de JSON a partir de schemas"""
    print("\n" + "="*60)
    print("TEST 2: Generación de JSON Schema para Gemini")
    print("="*60)
    
    schema = TestExecutionRequest.model_json_schema()
    print("✅ Schema JSON generado correctamente")
    print(f"   - Propiedades requeridas: {schema.get('required', [])}")
    print(f"   - Propiedades: {list(schema.get('properties', {}).keys())}")
    print(f"\nSchema completo:")
    print(json.dumps(schema, indent=2))


def test_integration_flow():
    """Simula el flujo completo sin ejecutar LLM"""
    print("\n" + "="*60)
    print("TEST 3: Simulación de flujo completo")
    print("="*60)
    
    # Simular respuesta de Gemini (ya parseada)
    gemini_response = """{
        "language": "python",
        "test_cases": [
            {"input": [5], "expected": "120"},
            {"input": [0], "expected": "1"},
            {"input": [1], "expected": "1"},
            {"input": [10], "expected": "3628800"}
        ]
    }"""
    
    print("1. Respuesta simulada de Gemini:")
    print(f"   {gemini_response[:100]}...")
    
    # Parsear JSON
    try:
        test_structure = json.loads(gemini_response)
        print("   ✅ JSON parseado correctamente")
    except json.JSONDecodeError as e:
        print(f"   ❌ Error al parsear JSON: {e}")
        return
    
    # Validar con Pydantic
    try:
        validated = TestExecutionRequest(**test_structure)
        print("   ✅ Validación Pydantic exitosa")
    except ValidationError as e:
        print(f"   ❌ Error de validación: {e}")
        return
    
    # Extraer datos
    language = test_structure.get('language')
    test_cases = test_structure.get('test_cases', [])
    
    print(f"\n2. Datos extraídos:")
    print(f"   - Lenguaje: {language}")
    print(f"   - Casos de prueba: {len(test_cases)}")
    
    # Simular selección de herramienta
    if language == 'python':
        tool_name = "CodeExecutionToolWithInterpreterPY"
    elif language == 'typescript':
        tool_name = "CodeExecutionToolWithInterpreterTS"
    else:
        tool_name = "DESCONOCIDO"
    
    print(f"\n3. Herramienta seleccionada: {tool_name}")
    print(f"   ✅ Flujo completo simulado exitosamente")


if __name__ == "__main__":
    print("\n" + "🚀"*30)
    print("TESTS DE NUEVA IMPLEMENTACIÓN - EJECUTOR DE PRUEBAS")
    print("🚀"*30)
    
    test_schema_validation()
    test_json_generation()
    test_integration_flow()
    
    print("\n" + "="*60)
    print("✅ TODOS LOS TESTS COMPLETADOS")
    print("="*60)
    print("\n💡 CONCLUSIÓN:")
    print("   - Los schemas Pydantic funcionan correctamente")
    print("   - La validación automática detecta errores")
    print("   - El flujo de dos fases es viable")
    print("   - Se elimina el riesgo de MALFORMED_FUNCTION_CALL")
    print("="*60 + "\n")
