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
    
    # GENERADOR DE RELEASE NOTES (debe ir PRIMERO para evitar conflictos)
    if "release note" in prompt_lower or "release notes" in prompt_lower:
        return """<h3>📋 Resumen</h3>
<p>Implementación exitosa de una función de suma aritmética con validaciones exhaustivas y manejo robusto de errores.</p>

<h3>✨ Funcionalidades Implementadas</h3>
<ul>
    <li>Función de suma para dos números con validación de tipos</li>
    <li>Manejo de errores para entradas inválidas (NaN, Infinity, tipos no numéricos)</li>
    <li>Corrección de problemas de precisión de punto flotante</li>
    <li>Documentación completa con JSDoc/TypeDoc</li>
</ul>

<h3>🔧 Detalles Técnicos</h3>
<ul>
    <li><strong>Lenguaje:</strong> TypeScript 5.0</li>
    <li><strong>Función Principal:</strong> <code>sumar(a: number, b: number): number</code></li>
    <li><strong>Validaciones:</strong> Tipo, NaN, Infinity</li>
    <li><strong>Precisión:</strong> Redondeo a 10 decimales</li>
</ul>

<h3>✅ Validaciones</h3>
<ul>
    <li>✅ Análisis de SonarQube: Aprobado sin issues bloqueantes</li>
    <li>✅ Tests Unitarios: Todos los casos de prueba pasados</li>
    <li>✅ Validación de Stakeholder: Aprobada</li>
    <li>✅ Calidad de Código: Cumple con estándares de la industria</li>
</ul>

<h3>📊 Métricas del Desarrollo</h3>
<ul>
    <li><strong>Story Points:</strong> 2</li>
    <li><strong>Iteraciones:</strong> 1</li>
    <li><strong>Intentos de Debug:</strong> 1</li>
    <li><strong>Análisis SonarQube:</strong> 1</li>
    <li><strong>Estado:</strong> ✅ Completado y listo para producción</li>
</ul>

<hr/>
<p><em>🤖 Release Note generado automáticamente por el sistema multiagente de desarrollo ágil</em></p>"""
    
    # DESARROLLADOR - Código (debe ir PRIMERO porque su contexto también contiene "Requisitos")
    if "desarrollador" in prompt_lower or "codifica" in prompt_lower or "generar código" in prompt_lower:
        # Detectar si es una corrección de SonarQube
        es_correccion_sonarqube = "sonarqube" in context_lower or "instrucciones de corrección de calidad" in context_lower
        
        # Detectar si es una corrección de tests fallidos (traceback)
        es_correccion_tests = "traceback" in context_lower or "error de ejecución" in context_lower
        
        # Detectar si son requisitos mejorados (segunda iteración completa después de Stakeholder)
        son_requisitos_mejorados = (
            "múltiples números" in context_lower or 
            "número variable" in context_lower or 
            "array" in context_lower or
            "versátil" in context_lower
        )
        
        # Detectar lenguaje
        if "typescript" in context_lower:
            # Prioridad: Requisitos mejorados (segunda iteración completa)
            if son_requisitos_mejorados and not es_correccion_tests and not es_correccion_sonarqube:
                # Código con soporte para múltiples números (segunda iteración completa)
                return (
                    "/**\n"
                    " * Suma un número variable de argumentos.\n"
                    " * \n"
                    " * @param numeros - Números a sumar\n"
                    " * @returns La suma de todos los números\n"
                    " * @throws Error si no se proporcionan argumentos o si alguno no es válido\n"
                    " * \n"
                    " * @example\n"
                    " * sumar(2, 3) // 5\n"
                    " * sumar(1, 2, 3, 4) // 10\n"
                    " * sumar(0.1, 0.2) // 0.3\n"
                    " */\n"
                    "export function sumar(...numeros: number[]): number {\n"
                    "    if (numeros.length === 0) {\n"
                    "        throw new Error('Debe proporcionar al menos un número');\n"
                    "    }\n"
                    "    \n"
                    "    // Validar cada número\n"
                    "    for (const num of numeros) {\n"
                    "        if (typeof num !== 'number') {\n"
                    "            throw new Error('Todos los argumentos deben ser números');\n"
                    "        }\n"
                    "        if (Number.isNaN(num)) {\n"
                    "            throw new Error('Los argumentos no pueden ser NaN');\n"
                    "        }\n"
                    "        if (!Number.isFinite(num)) {\n"
                    "            throw new Error('Los argumentos deben ser números finitos');\n"
                    "        }\n"
                    "    }\n"
                    "    \n"
                    "    // Sumar todos los números\n"
                    "    const resultado = numeros.reduce((acc, num) => acc + num, 0);\n"
                    "    \n"
                    "    // Redondear para evitar problemas de precisión\n"
                    "    return Math.round(resultado * 1e10) / 1e10;\n"
                    "}"
                )
            elif es_correccion_tests:
                # Tercera versión: código corregido después de fallos en tests
                return (
                    "/**\n"
                    " * Suma dos números con validación de tipos y manejo de precisión.\n"
                    " * @param a - Primer número\n"
                    " * @param b - Segundo número\n"
                    " * @returns La suma de a y b\n"
                    " * @throws Error si alguno de los argumentos no es un número\n"
                    " */\n"
                    "export function sumar(a: number, b: number): number {\n"
                    "    // Validación de tipos\n"
                    "    if (typeof a !== 'number' || typeof b !== 'number') {\n"
                    "        throw new Error('Ambos argumentos deben ser números');\n"
                    "    }\n"
                    "    \n"
                    "    // Validación de NaN e Infinity\n"
                    "    if (Number.isNaN(a) || Number.isNaN(b)) {\n"
                    "        throw new Error('Los argumentos no pueden ser NaN');\n"
                    "    }\n"
                    "    \n"
                    "    if (!Number.isFinite(a) || !Number.isFinite(b)) {\n"
                    "        throw new Error('Los argumentos deben ser números finitos');\n"
                    "    }\n"
                    "    \n"
                    "    // BUG CORREGIDO: Ahora suma correctamente (antes restaba)\n"
                    "    const resultado = a + b;\n"
                    "    \n"
                    "    // Redondear para evitar problemas de precisión\n"
                    "    return Math.round(resultado * 1e10) / 1e10;\n"
                    "}"
                )
            elif es_correccion_sonarqube:
                # Segunda versión: código corregido de SonarQube pero con BUG LÓGICO
                # Pasa SonarQube (sin issues de calidad) pero falla en tests (lógica incorrecta)
                return (
                    "/**\n"
                    " * Suma dos números con validación de tipos y manejo de precisión.\n"
                    " * @param a - Primer número\n"
                    " * @param b - Segundo número\n"
                    " * @returns La suma de a y b\n"
                    " * @throws Error si alguno de los argumentos no es un número\n"
                    " */\n"
                    "export function sumar(a: number, b: number): number {\n"
                    "    // Validación de tipos\n"
                    "    if (typeof a !== 'number' || typeof b !== 'number') {\n"
                    "        throw new Error('Ambos argumentos deben ser números');\n"
                    "    }\n"
                    "    \n"
                    "    // Validación de NaN e Infinity\n"
                    "    if (Number.isNaN(a) || Number.isNaN(b)) {\n"
                    "        throw new Error('Los argumentos no pueden ser NaN');\n"
                    "    }\n"
                    "    \n"
                    "    if (!Number.isFinite(a) || !Number.isFinite(b)) {\n"
                    "        throw new Error('Los argumentos deben ser números finitos');\n"
                    "    }\n"
                    "    \n"
                    "    // BUG LÓGICO: Resta en lugar de sumar (pasará SonarQube pero fallará tests)\n"
                    "    const resultado = a - b;\n"
                    "    \n"
                    "    // Redondear para evitar problemas de precisión\n"
                    "    return Math.round(resultado * 1e10) / 1e10;\n"
                    "}"
                )
            else:
                # Primera versión: código con bug de comparación Y bug lógico
                # Tiene 2 bugs: usa != (detectado por SonarQube) y resta en lugar de sumar (detectado por tests)
                return (
                    "export function sumar(a: number, b: number): number {\n"
                    "    if (typeof a != 'number' || typeof b != 'number') {\n"
                    "        throw new Error('Ambos argumentos deben ser números');\n"
                    "    }\n"
                    "    // BUG: Resta en lugar de sumar\n"
                    "    return Math.round((a - b) * 1e10) / 1e10;\n"
                    "}"
                )
        else:
            # Prioridad: Requisitos mejorados (segunda iteración completa) - Python
            if son_requisitos_mejorados and not es_correccion_tests and not es_correccion_sonarqube:
                return (
                    "from typing import Union\n"
                    "import math\n"
                    "\n"
                    "def sumar(*numeros: float) -> float:\n"
                    "    \"\"\"\n"
                    "    Suma un número variable de argumentos.\n"
                    "    \n"
                    "    Args:\n"
                    "        *numeros: Números a sumar (cantidad variable)\n"
                    "        \n"
                    "    Returns:\n"
                    "        La suma de todos los números con precisión de 10 decimales\n"
                    "        \n"
                    "    Raises:\n"
                    "        ValueError: Si no se proporcionan argumentos, alguno no es válido,\n"
                    "                   o es NaN/Infinity\n"
                    "        TypeError: Si alguno de los argumentos no es numérico\n"
                    "    \n"
                    "    Examples:\n"
                    "        >>> sumar(2, 3)\n"
                    "        5.0\n"
                    "        >>> sumar(1, 2, 3, 4)\n"
                    "        10.0\n"
                    "        >>> sumar(0.1, 0.2)\n"
                    "        0.3\n"
                    "    \"\"\"\n"
                    "    if len(numeros) == 0:\n"
                    "        raise ValueError('Debe proporcionar al menos un número')\n"
                    "    \n"
                    "    # Validar cada número\n"
                    "    for num in numeros:\n"
                    "        if not isinstance(num, (int, float)):\n"
                    "            raise TypeError(f'Todos los argumentos deben ser números, recibido: {type(num).__name__}')\n"
                    "        \n"
                    "        if math.isnan(num):\n"
                    "            raise ValueError('Los argumentos no pueden ser NaN')\n"
                    "        \n"
                    "        if math.isinf(num):\n"
                    "            raise ValueError('Los argumentos deben ser números finitos')\n"
                    "    \n"
                    "    # Sumar todos los números\n"
                    "    resultado = sum(numeros)\n"
                    "    \n"
                    "    # Redondear para evitar problemas de precisión\n"
                    "    return round(resultado, 10)\n"
                )
            elif es_correccion_tests:
                # Tercera versión: código Python corregido después de tests
                return (
                    "def sumar(a: float, b: float) -> float:\n"
                    "    \"\"\"\n"
                    "    Suma dos números con validación exhaustiva y precisión de punto flotante.\n"
                    "    \n"
                    "    Args:\n"
                    "        a: Primer número\n"
                    "        b: Segundo número\n"
                    "        \n"
                    "    Returns:\n"
                    "        La suma de a y b con precisión de 10 decimales\n"
                    "        \n"
                    "    Raises:\n"
                    "        TypeError: Si alguno de los argumentos no es numérico\n"
                    "        ValueError: Si alguno de los argumentos es NaN o Infinity\n"
                    "    \"\"\"\n"
                    "    import math\n"
                    "    \n"
                    "    # Validación de tipos\n"
                    "    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):\n"
                    "        raise TypeError('Ambos argumentos deben ser números')\n"
                    "    \n"
                    "    # Validación de valores especiales\n"
                    "    if math.isnan(a) or math.isnan(b):\n"
                    "        raise ValueError('Los argumentos no pueden ser NaN')\n"
                    "    \n"
                    "    if math.isinf(a) or math.isinf(b):\n"
                    "        raise ValueError('Los argumentos no pueden ser infinito')\n"
                    "    \n"
                    "    # BUG CORREGIDO: Ahora suma correctamente\n"
                    "    return round(a + b, 10)"
                )
            elif es_correccion_sonarqube:
                # Segunda versión: código Python corregido de SonarQube pero con BUG LÓGICO
                return (
                    "def sumar(a: float, b: float) -> float:\n"
                    "    \"\"\"\n"
                    "    Suma dos números con validación exhaustiva y precisión de punto flotante.\n"
                    "    \n"
                    "    Args:\n"
                    "        a: Primer número\n"
                    "        b: Segundo número\n"
                    "        \n"
                    "    Returns:\n"
                    "        La suma de a y b con precisión de 10 decimales\n"
                    "        \n"
                    "    Raises:\n"
                    "        TypeError: Si alguno de los argumentos no es numérico\n"
                    "        ValueError: Si alguno de los argumentos es NaN o Infinity\n"
                    "    \"\"\"\n"
                    "    import math\n"
                    "    \n"
                    "    # Validación de tipos\n"
                    "    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):\n"
                    "        raise TypeError('Ambos argumentos deben ser números')\n"
                    "    \n"
                    "    # Validación de valores especiales\n"
                    "    if math.isnan(a) or math.isnan(b):\n"
                    "        raise ValueError('Los argumentos no pueden ser NaN')\n"
                    "    \n"
                    "    if math.isinf(a) or math.isinf(b):\n"
                    "        raise ValueError('Los argumentos no pueden ser infinito')\n"
                    "    \n"
                    "    # BUG LÓGICO: Resta en lugar de sumar\n"
                    "    return round(a - b, 10)"
                )
            else:
                # Primera versión: código Python básico con bug lógico
                return (
                    "def sumar(a: float, b: float) -> float:\n"
                    "    \"\"\"Suma dos números con precisión de punto flotante.\"\"\"\n"
                    "    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):\n"
                    "        raise TypeError('Ambos argumentos deben ser números')\n"
                    "    # BUG: Resta en lugar de sumar\n"
                    "    return round(a - b, 10)"
                )
    
    # PRODUCT OWNER - Requisitos formales (ahora va DESPUÉS del Desarrollador)
    elif "product owner" in prompt_lower or "requirements manager" in prompt_lower:
        # Detectar si es una reingeniería (segunda iteración)
        # Debe tener feedback real del Stakeholder, no solo mencionar la palabra
        es_reingenieria = (
            ("feedback" in context_lower and "rechazado" in context_lower) or
            ("validación final: rechazado" in context_lower) or
            ("motivo:" in context_lower and "stakeholder" in context_lower)
        )
        
        # Detectar lenguaje del contexto
        if "typescript" in context_lower:
            lenguaje = "TypeScript 5.x"
            nombre_funcion = "sumar"
        else:
            lenguaje = "Python 3.12"
            nombre_funcion = "calcular"
        
        if es_reingenieria:
            # Segunda versión: Requisitos mejorados después de feedback del Stakeholder
            return (
                "{\n"
                f'  "objetivo_funcional": "Implementar una función {nombre_funcion} versátil que soporte suma de múltiples números y arrays",\n'
                f'  "lenguaje_version": "{lenguaje}",\n'
                f'  "nombre_funcion": "{nombre_funcion}",\n'
                '  "entradas_esperadas": "Número variable de argumentos (a, b, c, ...) o array de números",\n'
                '  "salidas_esperadas": "Un número que representa la suma total de todos los argumentos",\n'
                '  "casos_uso": [\n'
                '    "Sumar dos números: sumar(2, 3) = 5",\n'
                '    "Sumar múltiples números: sumar(1, 2, 3, 4) = 10",\n'
                '    "Sumar array: sumar([1, 2, 3]) = 6",\n'
                '    "Manejo de decimales con precisión",\n'
                '    "Validación de tipos y valores especiales (NaN, Infinity)"\n'
                '  ],\n'
                '  "restricciones_tecnicas": [\n'
                '    "Usar spread operator o rest parameters para argumentos variables",\n'
                '    "Manejar precisión de punto flotante correctamente",\n'
                '    "Validar cada argumento individual",\n'
                '    "Soportar mínimo 1 argumento, máximo ilimitado"\n'
                '  ],\n'
                '  "documentacion": "Función debe estar completamente documentada con JSDoc/docstring incluyendo ejemplos de uso"\n'
                "}"
            )
        else:
            # Primera versión: Requisitos básicos
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
        # Detectar si es la primera validación (attempt_count = 1)
        # Buscar "intento" o "attempt_count" en el contexto
        import re
        
        # Buscar indicadores de primera iteración
        es_primera_iteracion = False
        
        # Buscar "Intento 1" o similar en el contexto
        if re.search(r'intento[:\s]+1\b|attempt[:\s]+1\b', context_lower):
            es_primera_iteracion = True
        
        # También buscar en el código si tiene el comentario que indica primera versión
        if "intento 1" in context_lower or "iteración 1" in context_lower:
            es_primera_iteracion = True
        
        if es_primera_iteracion:
            # Primera vez: Rechazar para forzar reingeniería de requisitos
            return (
                "VALIDACIÓN FINAL: RECHAZADO\n\n"
                "Motivo: El código técnicamente funciona, pero no cumple completamente con la visión de negocio. "
                "La función implementada es demasiado básica y limitada. Se requiere una solución más versátil que:\n\n"
                "1. Soporte para más de dos números (suma de cantidad variable de argumentos)\n"
                "2. Manejo de arrays/listas de números\n"
                "3. Documentación más detallada de casos de uso\n"
                "4. Validaciones robustas para cada elemento\n\n"
                "La implementación actual solo acepta exactamente 2 parámetros, lo cual no es suficientemente flexible "
                "para las necesidades del negocio. Se necesita reingeniería de requisitos para incluir soporte de "
                "parámetros variables usando spread operators (*args en Python, ...args en TypeScript)."
            )
        else:
            # Segunda vez o posteriores: Validar
            return (
                "VALIDACIÓN FINAL: VALIDADO\n\n"
                "El código cumple con los requisitos funcionales especificados y la visión de negocio. "
                "La implementación ahora soporta:\n"
                "- Número variable de argumentos\n"
                "- Validaciones exhaustivas\n"
                "- Documentación completa\n"
                "- Manejo robusto de casos edge\n\n"
                "Aprobado para producción."
            )
    
    # RESPUESTA POR DEFECTO
    else:
        return "Respuesta mockeada por defecto. El sistema está en modo de pruebas (LLM_MOCK_MODE=true)."
