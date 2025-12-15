"""
Script de prueba para verificar la integración del wrapper de LangChain.
Ejecutar: python test_langchain_wrapper.py
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
        from llm.gemini_client import call_gemini
        print("✅ gemini_client importado correctamente")
    except Exception as e:
        print(f"❌ Error importando gemini_client: {e}")
        return False
    
    try:
        from llm.langchain_gemini import create_langchain_llm, call_gemini_with_langchain
        print("✅ langchain_gemini importado correctamente")
    except Exception as e:
        print(f"❌ Error importando langchain_gemini: {e}")
        print("   Ejecuta: pip install langchain-google-genai")
        return False
    
    return True


def test_configuration():
    """Prueba la configuración del sistema"""
    print("\n" + "="*60)
    print("TEST 2: Verificando configuración")
    print("="*60)
    
    print(f"📋 GEMINI_API_KEY configurada: {'✅ Sí' if settings.GEMINI_API_KEY else '❌ No'}")
    print(f"📋 LLM_MOCK_MODE: {settings.LLM_MOCK_MODE}")
    print(f"📋 USE_LANGCHAIN_WRAPPER: {settings.USE_LANGCHAIN_WRAPPER}")
    print(f"📋 MODEL_NAME: {settings.MODEL_NAME}")
    print(f"📋 TEMPERATURE: {settings.TEMPERATURE}")
    print(f"📋 MAX_OUTPUT_TOKENS: {settings.MAX_OUTPUT_TOKENS}")
    
    if not settings.GEMINI_API_KEY and not settings.LLM_MOCK_MODE:
        print("\n⚠️ WARNING: GEMINI_API_KEY no configurada y LLM_MOCK_MODE=false")
        print("   Configura GEMINI_API_KEY en src/.env o activa LLM_MOCK_MODE=true")
        return False
    
    return True


def test_langchain_wrapper():
    """Prueba el wrapper de LangChain"""
    print("\n" + "="*60)
    print("TEST 3: Probando wrapper de LangChain")
    print("="*60)
    
    if not settings.USE_LANGCHAIN_WRAPPER:
        print("⚠️ USE_LANGCHAIN_WRAPPER=false")
        print("   Para probar el wrapper, configura USE_LANGCHAIN_WRAPPER=true en src/.env")
        return True  # No es un error, solo está deshabilitado
    
    try:
        from llm.langchain_gemini import create_langchain_llm
        
        print("🔧 Creando instancia del LLM de LangChain...")
        llm = create_langchain_llm()
        print(f"✅ LLM creado: {type(llm).__name__}")
        
        # Probar conteo de tokens
        from llm.langchain_gemini import get_token_count
        test_text = "Hola, este es un texto de prueba para contar tokens."
        token_info = get_token_count(test_text)
        print(f"✅ Token counting funciona: {token_info['total_tokens']} tokens")
        
        return True
    except Exception as e:
        print(f"❌ Error probando wrapper: {e}")
        return False


def test_call_gemini_compatibility():
    """Prueba que call_gemini funcione con y sin wrapper"""
    print("\n" + "="*60)
    print("TEST 4: Probando compatibilidad de call_gemini")
    print("="*60)
    
    if settings.LLM_MOCK_MODE:
        print("🧪 Modo MOCK activado - usando respuestas simuladas")
    
    try:
        from llm.gemini_client import call_gemini
        
        # Prueba simple
        role_prompt = "Eres un asistente útil."
        context = "Responde con un saludo breve."
        
        print("🔧 Realizando llamada de prueba...")
        response = call_gemini(role_prompt, context)
        
        if response and len(response) > 0:
            print(f"✅ Respuesta recibida ({len(response)} caracteres)")
            print(f"   Preview: {response[:100]}...")
            return True
        else:
            print("❌ Respuesta vacía")
            return False
            
    except Exception as e:
        print(f"❌ Error en call_gemini: {e}")
        return False


def main():
    """Ejecuta todos los tests"""
    print("\n" + "="*60)
    print("🧪 TEST SUITE: Wrapper LangChain para Gemini")
    print("="*60)
    
    results = []
    
    # Test 1: Importaciones
    results.append(("Importaciones", test_imports()))
    
    # Test 2: Configuración
    results.append(("Configuración", test_configuration()))
    
    # Test 3: Wrapper LangChain
    results.append(("Wrapper LangChain", test_langchain_wrapper()))
    
    # Test 4: Compatibilidad
    results.append(("Compatibilidad call_gemini", test_call_gemini_compatibility()))
    
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
        print("\n💡 Próximos pasos:")
        print("   1. Para usar el wrapper de LangChain:")
        print("      - Configura USE_LANGCHAIN_WRAPPER=true en src/.env")
        print("      - Ejecuta: pip install langchain-google-genai")
        print("   2. El wrapper proporciona:")
        print("      - Callbacks para debugging")
        print("      - Streaming de respuestas")
        print("      - Token counting automático")
        print("      - Integración con LangSmith")
    else:
        print("\n⚠️ Algunos tests fallaron. Revisa los errores arriba.")
        sys.exit(1)


if __name__ == "__main__":
    main()
