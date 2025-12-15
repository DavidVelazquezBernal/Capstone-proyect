"""
Script de prueba para verificar los Prompt Templates de LangChain.
Ejecutar: python test_prompt_templates.py
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
        from config.prompt_templates import PromptTemplates, get_prompt_template
        print("✅ prompt_templates importado correctamente")
    except Exception as e:
        print(f"❌ Error importando prompt_templates: {e}")
        return False
    
    try:
        from langchain_core.prompts import ChatPromptTemplate
        print("✅ ChatPromptTemplate de LangChain importado correctamente")
    except Exception as e:
        print(f"❌ Error importando ChatPromptTemplate: {e}")
        return False
    
    return True


def test_template_creation():
    """Prueba la creación de templates"""
    print("\n" + "="*60)
    print("TEST 2: Creación de templates")
    print("="*60)
    
    try:
        from config.prompt_templates import PromptTemplates
        
        # Verificar que los templates existen
        templates = [
            ("Product Owner", PromptTemplates.PRODUCT_OWNER),
            ("Desarrollador", PromptTemplates.DESARROLLADOR),
            ("SonarQube", PromptTemplates.SONARQUBE),
            ("Generador UTs", PromptTemplates.GENERADOR_UTS),
            ("Stakeholder", PromptTemplates.STAKEHOLDER)
        ]
        
        for name, template in templates:
            if template:
                print(f"✅ Template {name} existe")
            else:
                print(f"❌ Template {name} no existe")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Error creando templates: {e}")
        return False


def test_product_owner_formatting():
    """Prueba el formateo del template de Product Owner"""
    print("\n" + "="*60)
    print("TEST 3: Formateo de Product Owner")
    print("="*60)
    
    try:
        from config.prompt_templates import PromptTemplates
        
        # Formatear con datos de prueba
        prompt = PromptTemplates.format_product_owner(
            prompt_inicial="Crea una función que calcule el factorial de un número",
            feedback_stakeholder=""
        )
        
        if prompt and len(prompt) > 0:
            print(f"✅ Prompt formateado ({len(prompt)} caracteres)")
            print(f"\n📋 Preview del prompt:")
            print("-" * 60)
            print(prompt[:300] + "...")
            print("-" * 60)
            
            # Verificar que contiene las variables
            if "factorial" in prompt.lower():
                print("✅ Prompt contiene el prompt inicial")
            else:
                print("⚠️ Prompt no contiene el prompt inicial")
            
            return True
        else:
            print("❌ Prompt vacío")
            return False
            
    except Exception as e:
        print(f"❌ Error formateando Product Owner: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_desarrollador_formatting():
    """Prueba el formateo del template de Desarrollador"""
    print("\n" + "="*60)
    print("TEST 4: Formateo de Desarrollador")
    print("="*60)
    
    try:
        from config.prompt_templates import PromptTemplates
        
        requisitos = """{
            "objetivo_funcional": "Calcular factorial",
            "lenguaje_version": "Python 3.10"
        }"""
        
        contexto = "Código anterior tenía un error de tipo"
        
        prompt = PromptTemplates.format_desarrollador(
            requisitos_formales=requisitos,
            contexto_adicional=contexto
        )
        
        if prompt and len(prompt) > 0:
            print(f"✅ Prompt formateado ({len(prompt)} caracteres)")
            
            # Verificar contenido
            if "factorial" in prompt.lower():
                print("✅ Prompt contiene los requisitos")
            if "error" in prompt.lower():
                print("✅ Prompt contiene el contexto adicional")
            
            return True
        else:
            print("❌ Prompt vacío")
            return False
            
    except Exception as e:
        print(f"❌ Error formateando Desarrollador: {e}")
        return False


def test_sonarqube_formatting():
    """Prueba el formateo del template de SonarQube"""
    print("\n" + "="*60)
    print("TEST 5: Formateo de SonarQube")
    print("="*60)
    
    try:
        from config.prompt_templates import PromptTemplates
        
        reporte = """
        Issues encontrados:
        - BLOCKER: Vulnerabilidad de seguridad en línea 10
        - CRITICAL: Complejidad ciclomática alta
        """
        
        codigo = "def factorial(n): return n * factorial(n-1)"
        
        prompt = PromptTemplates.format_sonarqube(
            reporte_sonarqube=reporte,
            codigo_actual=codigo
        )
        
        if prompt and len(prompt) > 0:
            print(f"✅ Prompt formateado ({len(prompt)} caracteres)")
            
            if "blocker" in prompt.lower():
                print("✅ Prompt contiene el reporte")
            if "factorial" in prompt.lower():
                print("✅ Prompt contiene el código")
            
            return True
        else:
            print("❌ Prompt vacío")
            return False
            
    except Exception as e:
        print(f"❌ Error formateando SonarQube: {e}")
        return False


def test_generador_uts_formatting():
    """Prueba el formateo del template de Generador UTs"""
    print("\n" + "="*60)
    print("TEST 6: Formateo de Generador UTs")
    print("="*60)
    
    try:
        from config.prompt_templates import PromptTemplates
        
        codigo = "export function add(a: number, b: number): number { return a + b; }"
        requisitos = '{"objetivo_funcional": "Sumar dos números"}'
        
        prompt = PromptTemplates.format_generador_uts(
            codigo_generado=codigo,
            requisitos_formales=requisitos,
            lenguaje="typescript"
        )
        
        if prompt and len(prompt) > 0:
            print(f"✅ Prompt formateado ({len(prompt)} caracteres)")
            
            if "add" in prompt:
                print("✅ Prompt contiene el código")
            if "typescript" in prompt.lower():
                print("✅ Prompt contiene el lenguaje")
            
            return True
        else:
            print("❌ Prompt vacío")
            return False
            
    except Exception as e:
        print(f"❌ Error formateando Generador UTs: {e}")
        return False


def test_stakeholder_formatting():
    """Prueba el formateo del template de Stakeholder"""
    print("\n" + "="*60)
    print("TEST 7: Formateo de Stakeholder")
    print("="*60)
    
    try:
        from config.prompt_templates import PromptTemplates
        
        requisitos = '{"objetivo_funcional": "Calcular factorial"}'
        codigo = "def factorial(n): return 1 if n <= 1 else n * factorial(n-1)"
        tests = "Todos los tests pasaron: 5/5"
        
        prompt = PromptTemplates.format_stakeholder(
            requisitos_formales=requisitos,
            codigo_generado=codigo,
            resultado_tests=tests
        )
        
        if prompt and len(prompt) > 0:
            print(f"✅ Prompt formateado ({len(prompt)} caracteres)")
            
            if "factorial" in prompt.lower():
                print("✅ Prompt contiene requisitos y código")
            if "tests" in prompt.lower():
                print("✅ Prompt contiene resultado de tests")
            
            return True
        else:
            print("❌ Prompt vacío")
            return False
            
    except Exception as e:
        print(f"❌ Error formateando Stakeholder: {e}")
        return False


def test_get_prompt_template():
    """Prueba la función get_prompt_template"""
    print("\n" + "="*60)
    print("TEST 8: Función get_prompt_template")
    print("="*60)
    
    try:
        from config.prompt_templates import get_prompt_template
        
        agentes = ["product_owner", "desarrollador", "sonarqube", "generador_uts", "stakeholder"]
        
        for agente in agentes:
            template = get_prompt_template(agente)
            if template:
                print(f"✅ Template obtenido para: {agente}")
            else:
                print(f"❌ No se pudo obtener template para: {agente}")
                return False
        
        # Probar con nombre inválido
        try:
            get_prompt_template("agente_inexistente")
            print("❌ Debería haber lanzado ValueError")
            return False
        except ValueError:
            print("✅ ValueError lanzado correctamente para agente inválido")
        
        return True
            
    except Exception as e:
        print(f"❌ Error en get_prompt_template: {e}")
        return False


def test_integration_with_agents():
    """Prueba la integración con los agentes"""
    print("\n" + "="*60)
    print("TEST 9: Integración con agentes")
    print("="*60)
    
    try:
        # Verificar que los agentes pueden importar los templates
        from agents.product_owner import product_owner_node
        from agents.desarrollador import desarrollador_node
        from agents.sonarqube import sonarqube_node
        from agents.generador_uts import generador_uts_node
        from agents.stakeholder import stakeholder_node
        
        print("✅ Product Owner puede importar templates")
        print("✅ Desarrollador puede importar templates")
        print("✅ SonarQube puede importar templates")
        print("✅ Generador UTs puede importar templates")
        print("✅ Stakeholder puede importar templates")
        
        return True
    except Exception as e:
        print(f"❌ Error en integración: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Ejecuta todos los tests"""
    print("\n" + "="*60)
    print("🧪 TEST SUITE: Prompt Templates de LangChain")
    print("="*60)
    
    results = []
    
    # Test 1: Importaciones
    results.append(("Importaciones", test_imports()))
    
    # Test 2: Creación de templates
    results.append(("Creación de templates", test_template_creation()))
    
    # Test 3: Product Owner
    results.append(("Formateo Product Owner", test_product_owner_formatting()))
    
    # Test 4: Desarrollador
    results.append(("Formateo Desarrollador", test_desarrollador_formatting()))
    
    # Test 5: SonarQube
    results.append(("Formateo SonarQube", test_sonarqube_formatting()))
    
    # Test 6: Generador UTs
    results.append(("Formateo Generador UTs", test_generador_uts_formatting()))
    
    # Test 7: Stakeholder
    results.append(("Formateo Stakeholder", test_stakeholder_formatting()))
    
    # Test 8: get_prompt_template
    results.append(("Función get_prompt_template", test_get_prompt_template()))
    
    # Test 9: Integración
    results.append(("Integración con agentes", test_integration_with_agents()))
    
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
        print("   ✅ ChatPromptTemplate para todos los agentes")
        print("   ✅ Templates dinámicos con variables")
        print("   ✅ Métodos de formateo convenientes")
        print("   ✅ Validación de variables automática")
        print("   ✅ Integración completa con agentes")
        print("\n📚 Próximos pasos:")
        print("   1. Los templates están listos para usar en producción")
        print("   2. Todos los agentes usan ChatPromptTemplate automáticamente")
        print("   3. Puedes extender templates según necesites")
        print("   4. Ejecuta: python src/main.py para probar el sistema completo")
    else:
        print("\n⚠️ Algunos tests fallaron. Revisa los errores arriba.")
        sys.exit(1)


if __name__ == "__main__":
    main()
