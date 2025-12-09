# Generador de Unit Tests - Documentación

## Descripción General

El **Generador de Unit Tests** es un nuevo nodo en el flujo de trabajo multiagente que se ejecuta después del análisis de SonarQube y antes del Probador/Depurador. Su función es generar automáticamente tests unitarios para el código generado.

## Posición en el Flujo

```
Codificador → AnalizadorSonarQube → GeneradorUnitTests → ProbadorDepurador → Stakeholder
                ↑                                              ↓
                └──────────────────────────────────────────────┘
                        (bucle de depuración)
```

## Características

### 1. Generación Automática de Tests

El nodo genera tests unitarios según el lenguaje del código:

- **TypeScript**: Tests con formato **Vitest**
  - Usa `describe()` para agrupar tests
  - Usa `it()` o `test()` para casos individuales
  - Usa `expect()` con matchers apropiados
  - Incluye imports necesarios de vitest

- **Python**: Tests con formato **pytest**
  - Funciones de test con prefijo `test_`
  - Usa `assert` para verificaciones
  - Usa `pytest.raises()` para excepciones
  - Incluye docstrings explicativos

### 2. Cobertura de Tests

Los tests generados cubren:
- ✅ Casos normales (happy path)
- ✅ Casos límite (edge cases)
- ✅ Manejo de errores y excepciones
- ✅ Validación de tipos (cuando aplica)

### 3. Almacenamiento

Los tests se guardan en el directorio `output/` con el formato:
- TypeScript: `unit_tests_req{attempt}_sq{sonarqube_attempt}.test.ts`
- Python: `test_unit_req{attempt}_sq{sonarqube_attempt}.test.py`

## Configuración

### Estado Requerido

El nodo necesita los siguientes campos del estado:
```python
{
    'requisitos_formales': str,  # Requisitos en formato JSON
    'codigo_generado': str,      # Código generado por el Codificador
    'attempt_count': int,         # Contador de intentos globales
    'sonarqube_attempt_count': int  # Contador de intentos SonarQube
}
```

### Estado Actualizado

El nodo actualiza:
```python
{
    'tests_unitarios_generados': str  # Tests generados en formato código
}
```

## Prompt del Agente

El prompt `GENERADOR_UNIT_TESTS` en `config/prompts.py` instruye al LLM a:

1. Analizar el código generado y requisitos formales
2. Identificar funciones/métodos a testear
3. Generar tests según el lenguaje detectado
4. Incluir casos normales, edge cases y manejo de errores
5. Usar sintaxis y convenciones apropiadas del framework

## Ejemplo de Uso

### Input (TypeScript)
```typescript
export function sumar(a: number, b: number): number {
    return a + b;
}
```

### Output Generado
```typescript
import { describe, it, expect } from 'vitest'
import { sumar } from './codigo'

describe('sumar', () => {
    it('debe sumar dos números positivos', () => {
        expect(sumar(2, 3)).toBe(5)
    })
    
    it('debe manejar números negativos', () => {
        expect(sumar(-2, 3)).toBe(1)
    })
    
    it('debe manejar cero', () => {
        expect(sumar(0, 5)).toBe(5)
    })
})
```

## Integración con el Workflow

### Transición desde AnalizadorSonarQube

Cuando el código pasa el análisis de SonarQube:
```python
workflow.add_conditional_edges(
    "AnalizadorSonarQube",
    lambda x: "QUALITY_PASSED" if x['sonarqube_passed'] else ...,
    {
        "QUALITY_PASSED": "GeneradorUnitTests",
        ...
    }
)
```

### Transición a ProbadorDepurador

Siempre continúa al Probador:
```python
workflow.add_edge("GeneradorUnitTests", "ProbadorDepurador")
```

## Notas Importantes

- ⚠️ **Los tests NO se ejecutan**: Este nodo solo genera el código de los tests
- 📁 **Almacenamiento**: Los tests se guardan para referencia futura
- 🔄 **Sin bucles**: No hay lógica de reintentos en este nodo
- ✅ **Siempre exitoso**: El nodo siempre continúa al siguiente paso

## Beneficios

1. **Documentación viva**: Los tests sirven como documentación del comportamiento esperado
2. **Regresión**: Facilita la detección de regresiones en futuras modificaciones
3. **Cobertura**: Asegura que se consideran múltiples escenarios
4. **Estándares**: Usa frameworks y convenciones estándar de la industria

## Archivo de Implementación

`src/agents/generador_unit_tests.py`

## Configuración en el Estado

Se agregó el campo en `src/models/state.py`:
```python
tests_unitarios_generados: str  # Tests unitarios generados (vitest/pytest)
```
