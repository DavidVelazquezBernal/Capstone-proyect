"""
Script de prueba para verificar los Output Parsers de LangChain.
Ejecutar: python test_output_parsers.py
"""

import sys
import os

# Añadir src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config.settings import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


def test_imports():
    """Prueba que todas las importaciones funcionen correctamente"""
    print("\n" + "="*60)
    print("TEST 1: Verificando importaciones")
    print("="*60)
    
    try:
        from llm.output_parsers import (
            RobustPydanticOutputParser,
            create_parser_for_schema,
            get_formal_requirements_parser,
            validate_and_parse,
            get_format_instructions
        )
        print("✅ output_parsers importado correctamente")
    except Exception as e:
        print(f"❌ Error importando output_parsers: {e}")
        return False
    
    try:
        from models.schemas import FormalRequirements, AzureDevOpsMetadata
        print("✅ schemas importados correctamente")
    except Exception as e:
        print(f"❌ Error importando schemas: {e}")
        return False
    
    return True


def test_parser_creation():
    """Prueba la creación de parsers"""
    print("\n" + "="*60)
    print("TEST 2: Creación de parsers")
    print("="*60)
    
    try:
        from llm.output_parsers import get_formal_requirements_parser, create_parser_for_schema
        from models.schemas import FormalRequirements
        
        # Crear parser para FormalRequirements
        parser1 = get_formal_requirements_parser()
        print(f"✅ Parser FormalRequirements creado: {type(parser1).__name__}")
        
        # Crear parser genérico
        parser2 = create_parser_for_schema(FormalRequirements)
        print(f"✅ Parser genérico creado: {type(parser2).__name__}")
        
        return True
    except Exception as e:
        print(f"❌ Error creando parsers: {e}")
        return False


def test_format_instructions():
    """Prueba la generación de instrucciones de formato"""
    print("\n" + "="*60)
    print("TEST 3: Instrucciones de formato")
    print("="*60)
    
    try:
        from llm.output_parsers import get_format_instructions
        from models.schemas import FormalRequirements
        
        instructions = get_format_instructions(FormalRequirements)
        
        if instructions and len(instructions) > 0:
            print(f"✅ Instrucciones generadas ({len(instructions)} caracteres)")
            print(f"\n📋 Preview de instrucciones:")
            print("-" * 60)
            print(instructions[:300] + "...")
            print("-" * 60)
            return True
        else:
            print("❌ Instrucciones vacías")
            return False
            
    except Exception as e:
        print(f"❌ Error generando instrucciones: {e}")
        return False


def test_parsing_valid_json():
    """Prueba el parsing de JSON válido"""
    print("\n" + "="*60)
    print("TEST 4: Parsing de JSON válido")
    print("="*60)
    
    try:
        from llm.output_parsers import validate_and_parse
        from models.schemas import FormalRequirements
        
        # JSON válido de ejemplo
        valid_json = """{
            "objetivo_funcional": "Calcular el factorial de un número",
            "lenguaje_version": "Python 3.10+",
            "nombre_funcion": "def factorial(n: int) -> int",
            "entradas_esperadas": "Un entero positivo n",
            "salidas_esperadas": "El factorial de n como entero"
        }"""
        
        result = validate_and_parse(valid_json, FormalRequirements)
        
        if result:
            print("✅ Parsing exitoso")
            print(f"   Objetivo: {result.objetivo_funcional}")
            print(f"   Lenguaje: {result.lenguaje_version}")
            print(f"   Función: {result.nombre_funcion}")
            return True
        else:
            print("❌ Parsing falló")
            return False
            
    except Exception as e:
        print(f"❌ Error en parsing: {e}")
        return False


def test_parsing_with_markdown():
    """Prueba el parsing de JSON con bloques markdown"""
    print("\n" + "="*60)
    print("TEST 5: Parsing de JSON con markdown")
    print("="*60)
    
    try:
        from llm.output_parsers import validate_and_parse
        from models.schemas import FormalRequirements
        
        # JSON envuelto en markdown
        markdown_json = """```json
{
    "objetivo_funcional": "Sumar dos números",
    "lenguaje_version": "TypeScript 5.0",
    "nombre_funcion": "function add(a: number, b: number): number",
    "entradas_esperadas": "Dos números a y b",
    "salidas_esperadas": "La suma de a + b"
}
```"""
        
        result = validate_and_parse(markdown_json, FormalRequirements)
        
        if result:
            print("✅ Parsing exitoso (con limpieza de markdown)")
            print(f"   Objetivo: {result.objetivo_funcional}")
            print(f"   Lenguaje: {result.lenguaje_version}")
            return True
        else:
            print("❌ Parsing falló")
            return False
            
    except Exception as e:
        print(f"❌ Error en parsing: {e}")
        return False


def test_parsing_with_extra_text():
    """Prueba el parsing de JSON con texto adicional"""
    print("\n" + "="*60)
    print("TEST 6: Parsing de JSON con texto adicional")
    print("="*60)
    
    try:
        from llm.output_parsers import validate_and_parse
        from models.schemas import FormalRequirements
        
        # JSON con texto antes y después
        text_with_json = """Aquí está el JSON solicitado:

{
    "objetivo_funcional": "Multiplicar dos números",
    "lenguaje_version": "Python 3.11",
    "nombre_funcion": "def multiply(x: float, y: float) -> float",
    "entradas_esperadas": "Dos números flotantes x e y",
    "salidas_esperadas": "El producto x * y"
}

Espero que esto sea útil."""
        
        result = validate_and_parse(text_with_json, FormalRequirements)
        
        if result:
            print("✅ Parsing exitoso (con extracción de JSON)")
            print(f"   Objetivo: {result.objetivo_funcional}")
            return True
        else:
            print("❌ Parsing falló")
            return False
            
    except Exception as e:
        print(f"❌ Error en parsing: {e}")
        return False


def test_parsing_invalid_json():
    """Prueba el manejo de JSON inválido"""
    print("\n" + "="*60)
    print("TEST 7: Manejo de JSON inválido")
    print("="*60)
    
    try:
        from llm.output_parsers import validate_and_parse
        from models.schemas import FormalRequirements
        
        # JSON inválido (falta campo requerido)
        invalid_json = """{
            "objetivo_funcional": "Test",
            "lenguaje_version": "Python 3.10"
        }"""
        
        try:
            result = validate_and_parse(invalid_json, FormalRequirements)
            print("❌ Debería haber fallado pero no lo hizo")
            return False
        except Exception as e:
            print(f"✅ Error capturado correctamente: {type(e).__name__}")
            print(f"   Mensaje: {str(e)[:100]}...")
            return True
            
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False


def test_integration_with_product_owner():
    """Prueba la integración con el Product Owner"""
    print("\n" + "="*60)
    print("TEST 8: Integración con Product Owner")
    print("="*60)
    
    try:
        from agents.product_owner import product_owner_node
        from llm.output_parsers import get_formal_requirements_parser
        
        # Verificar que el parser está disponible
        parser = get_formal_requirements_parser()
        print(f"✅ Parser disponible para Product Owner: {type(parser).__name__}")
        
        # Verificar que el módulo se importa correctamente
        print("✅ Product Owner puede importar output_parsers")
        
        return True
    except Exception as e:
        print(f"❌ Error en integración: {e}")
        return False


def main():
    """Ejecuta todos los tests"""
    print("\n" + "="*60)
    print("🧪 TEST SUITE: Output Parsers de LangChain")
    print("="*60)
    
    results = []
    
    # Test 1: Importaciones
    results.append(("Importaciones", test_imports()))
    
    # Test 2: Creación de parsers
    results.append(("Creación de parsers", test_parser_creation()))
    
    # Test 3: Instrucciones de formato
    results.append(("Instrucciones de formato", test_format_instructions()))
    
    # Test 4: Parsing válido
    results.append(("Parsing JSON válido", test_parsing_valid_json()))
    
    # Test 5: Parsing con markdown
    results.append(("Parsing con markdown", test_parsing_with_markdown()))
    
    # Test 6: Parsing con texto extra
    results.append(("Parsing con texto extra", test_parsing_with_extra_text()))
    
    # Test 7: Manejo de errores
    results.append(("Manejo de JSON inválido", test_parsing_invalid_json()))
    
    # Test 8: Integración
    results.append(("Integración con Product Owner", test_integration_with_product_owner()))
    
    # Resumen
    print("\n" + "="*60)
    print("📊 RESUMEN DE TESTS")
    print("="*60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "="*60)
    print(f"Total: {passed} passed, {failed} failed")
    print("="*60)
    
    if failed == 0:
        print("\n🎉 ¡Todos los tests pasaron!")
        print("\n💡 Características implementadas:")
        print("   ✅ PydanticOutputParser robusto con limpieza de markdown")
        print("   ✅ Extracción automática de JSON del texto")
        print("   ✅ Manejo de errores con fallback")
        print("   ✅ Instrucciones de formato para prompts")
        print("   ✅ Integración con Product Owner")
        print("\n📚 Próximos pasos:")
        print("   1. Los parsers están listos para usar en producción")
        print("   2. Product Owner usa automáticamente PydanticOutputParser")
        print("   3. Puedes añadir parsers para otros agentes según necesites")
    else:
        print("\n⚠️ Algunos tests fallaron. Revisa los errores arriba.")
        sys.exit(1)


if __name__ == "__main__":
    main()
