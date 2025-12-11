"""
Respuestas mockeadas para el modo de pruebas del LLM.
Evita llamadas reales a la API de Gemini durante testing.
"""

def get_mock_response(role_prompt: str, context: str) -> str:
    """
    Devuelve una respuesta mockeada según el tipo de agente detectado en el prompt.
    
    Args:
        role_prompt: El prompt que define el rol del agente
        context: El contexto actual del proyecto
        
    Returns:
        str: Respuesta mockeada apropiada para el agente
    """
    
    # Detectar tipo de agente por palabras clave en el prompt
    # IMPORTANTE: El orden importa - debemos detectar el agente más específico primero
    prompt_lower = role_prompt.lower()
    context_lower = context.lower()
    
    # DESARROLLADOR - Código (debe ir PRIMERO porque su contexto también contiene "Requisitos")
    if "desarrollador" in prompt_lower or "codifica" in prompt_lower or "generar código" in prompt_lower:
        # Detectar lenguaje
        if "typescript" in context_lower:
            return (
                "export function sumar(a: number, b: number): number {\n"
                "    if (typeof a !== 'number' || typeof b !== 'number') {\n"
                "        throw new Error('Ambos argumentos deben ser números');\n"
                "    }\n"
                "    // Redondear para evitar problemas de precisión de punto flotante\n"
                "    return Math.round((a + b) * 1e10) / 1e10;\n"
                "}"
            )
        else:
            return (
                "def sumar(a: float, b: float) -> float:\n"
                "    \"\"\"Suma dos números con precisión de punto flotante.\"\"\"\n"
                "    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):\n"
                "        raise TypeError('Ambos argumentos deben ser números')\n"
                "    return round(a + b, 10)"
            )
    
    # PRODUCT OWNER - Requisitos formales (ahora va DESPUÉS del Desarrollador)
    elif "product owner" in prompt_lower or "requirements manager" in prompt_lower:
        # Detectar lenguaje del contexto
        if "typescript" in context_lower:
            lenguaje = "TypeScript 5.x"
            nombre_funcion = "sumar"
        else:
            lenguaje = "Python 3.12"
            nombre_funcion = "calcular"
            
        return (
            "{\n"
            f'  "objetivo_funcional": "Implementar una función {nombre_funcion} que realice operaciones aritméticas básicas",\n'
            f'  "lenguaje_version": "{lenguaje}",\n'
            f'  "nombre_funcion": "{nombre_funcion}",\n'
            '  "entradas_esperadas": "Dos números (a, b) de tipo number/int",\n'
            '  "salidas_esperadas": "Un número que representa el resultado de la operación",\n'
            '  "casos_uso": ["Sumar dos números positivos", "Sumar números negativos", "Manejar decimales"],\n'
            '  "restricciones_tecnicas": "La función debe manejar precisión de punto flotante correctamente"\n'
            "}"
        )
    
    # GENERADOR DE TESTS
    elif "test" in prompt_lower and ("generar" in prompt_lower or "unitarios" in prompt_lower):
        # Extraer el nombre del archivo de código del contexto
        import re
        filename_match = re.search(r"archivo de código se llama '([^']+)'", context)
        if filename_match:
            codigo_filename = filename_match.group(1)
            # Remover extensión para el import
            codigo_module = codigo_filename.replace('.ts', '').replace('.py', '')
        else:
            # Fallback si no se encuentra el nombre
            codigo_module = "codigo_generado"
        
        if "typescript" in context_lower:
            return (
                "import { describe, it, expect } from 'vitest';\n"
                f"import {{ sumar }} from './{codigo_module}';\n\n"
                "describe('sumar', () => {\n"
                "    it('should sum two positive numbers', () => {\n"
                "        expect(sumar(2, 3)).toBe(5);\n"
                "    });\n\n"
                "    it('should sum with zero', () => {\n"
                "        expect(sumar(5, 0)).toBe(5);\n"
                "        expect(sumar(0, 5)).toBe(5);\n"
                "    });\n\n"
                "    it('should sum negative numbers', () => {\n"
                "        expect(sumar(-2, -3)).toBe(-5);\n"
                "    });\n\n"
                "    it('should sum positive and negative', () => {\n"
                "        expect(sumar(5, -2)).toBe(3);\n"
                "    });\n\n"
                "    it('should handle floating point precision', () => {\n"
                "        expect(sumar(0.1, 0.2)).toBeCloseTo(0.3);\n"
                "    });\n\n"
                "    it('should throw error for invalid input', () => {\n"
                "        expect(() => sumar('a' as any, 5)).toThrow();\n"
                "        expect(() => sumar(5, null as any)).toThrow();\n"
                "    });\n"
                "});"
            )
        else:
            return (
                "import pytest\n"
                f"from {codigo_module} import sumar\n\n"
                "def test_sumar_positivos():\n"
                "    # Test suma de números positivos\n"
                "    assert sumar(2, 3) == 5\n\n"
                "def test_sumar_con_cero():\n"
                "    # Test suma con cero\n"
                "    assert sumar(5, 0) == 5\n"
                "    assert sumar(0, 5) == 5\n\n"
                "def test_sumar_negativos():\n"
                "    # Test suma de números negativos\n"
                "    assert sumar(-2, -3) == -5\n\n"
                "def test_sumar_positivo_negativo():\n"
                "    # Test suma de positivo y negativo\n"
                "    assert sumar(5, -2) == 3\n\n"
                "def test_sumar_flotantes():\n"
                "    # Test suma con números de punto flotante\n"
                "    assert abs(sumar(0.1, 0.2) - 0.3) < 1e-10\n\n"
                "def test_tipo_invalido():\n"
                "    # Test con tipos de datos inválidos\n"
                "    with pytest.raises(TypeError):\n"
                "        sumar('a', 5)\n"
                "    with pytest.raises(TypeError):\n"
                "        sumar(5, None)"
            )
    
    # STAKEHOLDER - Validación
    elif "stakeholder" in prompt_lower or "validar" in prompt_lower:
        return "VALIDADO: El código cumple con los requisitos funcionales especificados y la visión de negocio."
    
    # RESPUESTA POR DEFECTO
    else:
        return "Respuesta mockeada por defecto. El sistema está en modo de pruebas (LLM_MOCK_MODE=true)."
