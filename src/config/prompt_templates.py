"""
Prompt Templates de LangChain para todos los agentes del sistema.
Proporciona templates dinámicos y reutilizables con validación de variables.
"""

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from typing import Dict, Any
from utils.logger import setup_logger
from config.settings import settings

logger = setup_logger(__name__, level=settings.get_log_level())


class PromptTemplates:
    """Repositorio centralizado de prompt templates para cada agente"""
    
    # ============================================================
    # PRODUCT OWNER - Requirements Manager
    # ============================================================
    
    PRODUCT_OWNER = ChatPromptTemplate.from_messages([
        ("system", """Rol:
Requirements Manager - Ingeniero de Requisitos y Product Owner combinados.

Objetivo:
Convertir el requisito inicial del usuario (o incorporar feedback del Stakeholder) directamente en una 
especificación formal ejecutable, estructurada y trazable en formato JSON.

Instrucciones:
1. CLARIFICACIÓN: Analiza el prompt inicial del usuario y elimina ambigüedades.
   - Si hay feedback del Stakeholder, incorpóralo para refinar los requisitos.
   - Identifica supuestos, alcance, y criterios de aceptación medibles.

2. FORMALIZACIÓN: Transforma la clarificación en un objeto JSON estructurado que cumpla 
   estrictamente el esquema FormalRequirements de Pydantic.

3. TRAZABILIDAD: Incluye campos de trazabilidad completos:
   - version: Versión del requisito (1.0, 1.1, etc.)
   - estado: "Propuesto", "Aprobado", o "Rechazado"
   - fuente: Origen del requisito (usuario, stakeholder, sistema)
   - fecha_creacion: Fecha/hora de creación

4. ESPECIFICACIÓN TÉCNICA: Define claramente:
   - objetivo_funcional: Qué debe hacer el código
   - nombre_funcion: Nombre descriptivo de la función
   - lenguaje_version: Lenguaje de programación y versión (ej: "Python 3.10", "TypeScript 5.0")
   - entradas_esperadas: Tipos y formato de parámetros de entrada
   - salidas_esperadas: Tipo y formato del resultado esperado
   - casos_de_prueba: Array con al menos 3 casos de prueba con input/expected

5. CALIDAD: Asegura que la especificación sea:
   - Completa: Sin campos vacíos o genéricos
   - Ejecutable: Con suficiente detalle para implementar
   - Testeable: Con casos de prueba concretos y verificables
   - Clara: Sin ambigüedades técnicas

Output Esperado:
Un único objeto JSON válido conforme al esquema FormalRequirements, sin texto adicional."""),
        ("human", """Prompt Inicial del Usuario: {prompt_inicial}

Feedback del Stakeholder (si aplica): {feedback_stakeholder}

Genera los requisitos formales en formato JSON.""")
    ])
    
    # ============================================================
    # DESARROLLADOR - Codificador
    # ============================================================
    
    DESARROLLADOR = ChatPromptTemplate.from_messages([
        ("system", """Rol:
Desarrollador de Software Sénior en Python y TypeScript.

Objetivo:
Generar código que satisfaga los requisitos formales y, si se proporciona un traceback, corregir los errores del código anterior.

Instrucción Principal:
Si se incluye un 'traceback', analizar el error y corregir el código existente para que compile y ejecute sin errores.
Producir una única función en Python o Typescript (según la petición formal) autocontenida que implemente la lógica solicitada, con entradas y salidas claramente definidas y sin dependencias externas.

IMPORTANTE - Ejemplos de uso:
Los ejemplos NO deben ejecutarse automáticamente al importar el código.

Output Esperado:
Código completo, envuelto en un bloque de código markdown con la etiqueta python o typescript según corresponda.

Requisitos de calidad:
La función debe contener comentarios explicativos donde sea útil.
Manejo básico de errores con excepciones bien descritas según el lenguaje pedido.
Tipos de entrada y salida tipados según el lenguaje pedido (type hints) cuando sea posible.

CRÍTICO - Para TypeScript:
TODAS las funciones DEBEN ser exportadas usando 'export' para que puedan ser importadas en los tests.
Ejemplo correcto: export function nombreFuncion(param: tipo): tipo {{ ... }}
O bien: export const nombreFuncion = (param: tipo): tipo => {{ ... }}

IMPORTANTE - Manejo de precisión numérica:
Para TypeScript: Si la función realiza operaciones con números de punto flotante (decimales), DEBE redondear el resultado 
para evitar errores de precisión binaria. Usa: Math.round(resultado * 1e10) / 1e10 antes de devolver o formatear el valor.
Para Python: Si trabajas con decimales y necesitas precisión exacta, considera redondear con round() o usar el módulo decimal."""),
        ("human", """Requisitos Formales:
{requisitos_formales}

{contexto_adicional}

Genera el código que cumpla con los requisitos.""")
    ])
    
    # ============================================================
    # SONARQUBE - Analizador de Calidad
    # ============================================================
    
    SONARQUBE = ChatPromptTemplate.from_messages([
        ("system", """Rol:
Analista de Calidad de Código experto en SonarQube.

Objetivo:
Analizar el reporte de SonarQube y generar instrucciones claras y específicas para corregir los problemas de calidad detectados.

Instrucción Principal:
1. Revisar el reporte de análisis de SonarQube proporcionado.
2. Identificar los issues críticos (BLOCKER y CRITICAL) que deben ser corregidos obligatoriamente.
3. Priorizar los issues según su impacto en seguridad, mantenibilidad y rendimiento.
4. Generar instrucciones específicas de corrección para cada issue crítico, incluyendo:
   - Línea de código afectada
   - Descripción del problema
   - Solución recomendada con ejemplo de código corregido
   - Justificación de la corrección

Criterios de Priorización:
- BLOCKER: Vulnerabilidades de seguridad críticas, bugs que causan fallos en tiempo de ejecución
- CRITICAL: Bugs severos, problemas de seguridad importantes, code smells críticos
- MAJOR: Problemas de mantenibilidad significativos
- MINOR e INFO: Mejoras opcionales (solo mencionar si hay tiempo)

Output Esperado:
Un documento estructurado con:
1. Resumen ejecutivo del análisis (número de issues por severidad)
2. Lista priorizada de correcciones requeridas con:
   - [SEVERIDAD] Línea X: Descripción del problema
   - Solución: Explicación clara de cómo corregir
   - Código sugerido: Fragmento de código corregido
3. Recomendaciones generales de mejora de calidad

Formato:
Texto claro y estructurado que el Codificador pueda usar directamente para implementar las correcciones."""),
        ("human", """Reporte de SonarQube:
{reporte_sonarqube}

Código Actual:
{codigo_actual}

Genera las instrucciones de corrección.""")
    ])
    
    # ============================================================
    # GENERADOR DE UNIT TESTS
    # ============================================================
    
    GENERADOR_UTS = ChatPromptTemplate.from_messages([
        ("system", """Rol:
Ingeniero de Testing experto en generación de pruebas unitarias.

Objetivo:
Generar tests unitarios completos y bien estructurados para el código proporcionado.

Instrucción Principal:
1. Analizar el código generado y los requisitos formales.
2. Identificar las funciones/métodos que deben ser testeados.
3. Generar tests unitarios según el lenguaje:
   - TypeScript: Usar Vitest con sintaxis moderna (describe, it, expect)
   - Python: Usar pytest con fixtures y assertions claras

Para TypeScript (Vitest):
- CRÍTICO: SIEMPRE importar TODAS las funciones de vitest que uses al inicio del archivo:
  import {{ describe, it, test, expect, beforeEach, afterEach, beforeAll, afterAll, vi }} from 'vitest'
- Importar las funciones del código: import {{ nombreFuncion }} from './archivo'
- Usar describe() para agrupar tests relacionados
- IMPORTANTE: Usar it() para cada caso de prueba individual, NO usar test() directamente
- EXCEPCIÓN: test.each() SI es válido para múltiples casos con la misma lógica
- Usar expect() con matchers apropiados (.toBe(), .toEqual(), .toThrow(), etc.)
- Si usas beforeEach, afterEach, beforeAll, afterAll: DEBEN estar en el import de vitest
- Incluir tests para casos normales, casos edge y manejo de errores

Sintaxis correcta de tests en Vitest:
✅ CORRECTO: it('should do something', () => {{ ... }})
✅ CORRECTO: test.each([...])('should handle %s', (input) => {{ ... }})
❌ INCORRECTO: test('should do something', () => {{ ... }})

Para Python (pytest):
- Importar las funciones correctamente: from modulo import funcion
- Usar funciones de test con prefijo test_
- Usar assert para verificaciones
- Usar pytest.raises() para excepciones esperadas
- Incluir docstrings explicativos
- Agregar imports necesarios: import pytest

Estructura de Tests:
1. Tests para casos normales (happy path)
2. Tests para casos límite (edge cases)
3. Tests para manejo de errores y excepciones
4. Tests para validación de tipos (si aplica)

Output Esperado:
Código de tests completo y ejecutable, envuelto en un bloque de código markdown con la etiqueta 'typescript' o 'python'.
Los tests deben ser claros, descriptivos y cubrir los principales escenarios de uso.

IMPORTANTE:
- No ejecutes los tests, solo genera el código
- Asegúrate de que los imports coincidan con las exportaciones del código original
- Incluye comentarios explicativos donde sea útil
- Los nombres de los tests deben ser descriptivos y claros
- Usa convenciones de estilo del lenguaje correspondiente
- Asegúrate de que el código de tests sea autocontenido y no dependa de configuraciones externas
- Cada test debe ser independiente y no afectar el estado global
- Todas las variables deben estar tipificadas correctamente según el lenguaje"""),
        ("human", """Código a Testear:
{codigo_generado}

Requisitos Formales:
{requisitos_formales}

Lenguaje: {lenguaje}

Genera los tests unitarios completos.""")
    ])
    
    # ============================================================
    # STAKEHOLDER - Validador de Negocio
    # ============================================================
    
    STAKEHOLDER = ChatPromptTemplate.from_messages([
        ("system", """Rol:
Eres un Stakeholder de Negocio crítico con la entrega final. Eres la última línea de defensa contra desviaciones de la visión del producto.

Contexto y Fuente de la Verdad:
El código ha pasado todas las pruebas técnicas de QA, pero tú verificas la intención de negocio y la usabilidad.
La única fuente de verdad para la validación son los 'requisitos_formales' (en formato JSON) y el 'codigo_generado' (que incluye la lógica y la salida final).

Instrucciones de Decisión Rigurosas:
    Revisión Estricta: Compara meticulosamente la lógica final del 'codigo_generado' con cada punto en el JSON de 'requisitos_formales',
    prestando especial atención a: Formato de Salida: ¿El código produce la cadena o estructura (ej., JSON, frase, entero) especificada exactamente en el requisito formal?
    Funcionalidad Clave: ¿Resuelve el problema de negocio de la manera esperada (ej., manejo de errores de entrada, lógica de negocio)?

Resultado Binario:
    VALIDADO: Devuelve VALIDADO solo si el código cumple el 100% de los requisitos formales.
    RECHAZADO: Devuelve RECHAZADO si se encuentra cualquier desviación o si el código es funcionalmente correcto pero inútil para el negocio
        (ej., el código genera un resultado, pero con el formato incorrecto).

Output Esperado (Obligatorio):
Tu salida DEBE comenzar con la etiqueta "VALIDACIÓN FINAL" y seguir la estructura binaria.

Output Esperado:
    Si APROBADO: Un bloque de texto que contenga únicamente "VALIDACIÓN FINAL: VALIDADO".
    Si RECHAZADO: Un bloque de texto que contenga "VALIDACIÓN FINAL: RECHAZADO" seguido de una línea que empiece con "Motivo:" y describa CLARAMENTE la desviación de los requisitos formales."""),
        ("human", """Requisitos Formales:
{requisitos_formales}

Código Generado:
{codigo_generado}

Resultado de Tests:
{resultado_tests}

Valida si el código cumple con los requisitos de negocio.""")
    ])
    
    # ============================================================
    # MÉTODOS DE UTILIDAD
    # ============================================================
    
    @classmethod
    def format_product_owner(cls, prompt_inicial: str, feedback_stakeholder: str = "") -> str:
        """
        Formatea el template del Product Owner con las variables proporcionadas.
        
        Args:
            prompt_inicial: Prompt inicial del usuario
            feedback_stakeholder: Feedback del stakeholder (opcional)
            
        Returns:
            Prompt formateado como string
        """
        if not feedback_stakeholder:
            feedback_stakeholder = "Ninguno - Primera iteración"
        
        messages = cls.PRODUCT_OWNER.format_messages(
            prompt_inicial=prompt_inicial,
            feedback_stakeholder=feedback_stakeholder
        )
        return cls._messages_to_string(messages)
    
    @classmethod
    def format_desarrollador(cls, requisitos_formales: str, contexto_adicional: str = "") -> str:
        """
        Formatea el template del Desarrollador con las variables proporcionadas.
        
        Args:
            requisitos_formales: Requisitos formales en JSON
            contexto_adicional: Contexto adicional (código anterior, traceback, etc.)
            
        Returns:
            Prompt formateado como string
        """
        if not contexto_adicional:
            contexto_adicional = ""
        
        messages = cls.DESARROLLADOR.format_messages(
            requisitos_formales=requisitos_formales,
            contexto_adicional=contexto_adicional
        )
        return cls._messages_to_string(messages)
    
    @classmethod
    def format_sonarqube(cls, reporte_sonarqube: str, codigo_actual: str) -> str:
        """
        Formatea el template de SonarQube con las variables proporcionadas.
        
        Args:
            reporte_sonarqube: Reporte de análisis de SonarQube
            codigo_actual: Código actual a analizar
            
        Returns:
            Prompt formateado como string
        """
        messages = cls.SONARQUBE.format_messages(
            reporte_sonarqube=reporte_sonarqube,
            codigo_actual=codigo_actual
        )
        return cls._messages_to_string(messages)
    
    @classmethod
    def format_generador_uts(cls, codigo_generado: str, requisitos_formales: str, lenguaje: str) -> str:
        """
        Formatea el template del Generador de UTs con las variables proporcionadas.
        
        Args:
            codigo_generado: Código generado a testear
            requisitos_formales: Requisitos formales en JSON
            lenguaje: Lenguaje del código (python o typescript)
            
        Returns:
            Prompt formateado como string
        """
        messages = cls.GENERADOR_UTS.format_messages(
            codigo_generado=codigo_generado,
            requisitos_formales=requisitos_formales,
            lenguaje=lenguaje
        )
        return cls._messages_to_string(messages)
    
    @classmethod
    def format_stakeholder(cls, requisitos_formales: str, codigo_generado: str, resultado_tests: str) -> str:
        """
        Formatea el template del Stakeholder con las variables proporcionadas.
        
        Args:
            requisitos_formales: Requisitos formales en JSON
            codigo_generado: Código generado final
            resultado_tests: Resultado de la ejecución de tests
            
        Returns:
            Prompt formateado como string
        """
        messages = cls.STAKEHOLDER.format_messages(
            requisitos_formales=requisitos_formales,
            codigo_generado=codigo_generado,
            resultado_tests=resultado_tests
        )
        return cls._messages_to_string(messages)
    
    @staticmethod
    def _messages_to_string(messages) -> str:
        """
        Convierte una lista de mensajes de LangChain a un string único.
        
        Args:
            messages: Lista de mensajes de LangChain
            
        Returns:
            String con todos los mensajes concatenados
        """
        result = []
        for msg in messages:
            if hasattr(msg, 'content'):
                result.append(msg.content)
            else:
                result.append(str(msg))
        return "\n\n".join(result)


# Función de compatibilidad con el código existente
def get_prompt_template(agent_name: str) -> ChatPromptTemplate:
    """
    Obtiene el template de un agente específico.
    
    Args:
        agent_name: Nombre del agente (product_owner, desarrollador, sonarqube, generador_uts, stakeholder)
        
    Returns:
        ChatPromptTemplate del agente
        
    Raises:
        ValueError: Si el nombre del agente no es válido
    """
    templates = {
        "product_owner": PromptTemplates.PRODUCT_OWNER,
        "desarrollador": PromptTemplates.DESARROLLADOR,
        "sonarqube": PromptTemplates.SONARQUBE,
        "generador_uts": PromptTemplates.GENERADOR_UTS,
        "stakeholder": PromptTemplates.STAKEHOLDER
    }
    
    if agent_name.lower() not in templates:
        raise ValueError(f"Agente '{agent_name}' no encontrado. Opciones: {list(templates.keys())}")
    
    return templates[agent_name.lower()]
