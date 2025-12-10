# 🔧 Mejora: Soporte para Clases con Múltiples Métodos

## 📋 Problema Identificado

El sistema de tests funcionales solo soportaba **funciones individuales**, pero el código generado frecuentemente incluye **clases con múltiples métodos** (como `Calculator` con `add`, `subtract`, `multiply`, `divide`).

**Limitación anterior:**
- Los tests solo podían probar una función con diferentes inputs
- No había forma de especificar qué método de una clase probar
- Generaba tests incompletos o fallidos para clases

## ✅ Solución Implementada

### 1. Actualización de Schemas Pydantic

**Archivo:** `src/models/schemas.py`

```python
class TestCase(BaseModel):
    input: list
    expected: str
    method: str | None = None  # ← NUEVO: Método a probar (para clases)

class TestExecutionRequest(BaseModel):
    language: str
    code_type: str  # ← NUEVO: "class" o "function"
    class_name: str | None = None  # ← NUEVO: Nombre de la clase
    function_name: str | None = None  # ← NUEVO: Nombre de la función
    test_cases: list[TestCase]
```

**Cambios:**
- ✅ Campo `method` en `TestCase` para especificar método de clase
- ✅ Campo `code_type` para identificar si es clase o función
- ✅ Campos `class_name` y `function_name` según el tipo

---

### 2. Actualización del Prompt

**Archivo:** `src/config/prompts.py` - `PROBADOR_GENERADOR_ESTRUCTURA_TESTS`

**Estructura JSON para CLASES:**
```json
{
  "language": "typescript",
  "code_type": "class",
  "class_name": "Calculator",
  "test_cases": [
    {"method": "add", "input": [2, 3], "expected": "5"},
    {"method": "add", "input": [0, 0], "expected": "0"},
    {"method": "subtract", "input": [5, 3], "expected": "2"},
    {"method": "multiply", "input": [3, 4], "expected": "12"},
    {"method": "divide", "input": [10, 2], "expected": "5"}
  ]
}
```

**Estructura JSON para FUNCIONES:**
```json
{
  "language": "python",
  "code_type": "function",
  "function_name": "factorial",
  "test_cases": [
    {"input": [5], "expected": "120"},
    {"input": [0], "expected": "1"}
  ]
}
```

**Instrucciones agregadas:**
- Detectar si el código es clase (`class`, `__init__`, `self`) o función
- Para clases: generar múltiples tests por cada método público
- Para clases: incluir campo `method` en cada test case
- No probar métodos privados

---

### 3. Herramientas de Detección

**Archivo:** `src/tools/code_executor.py`

**Nuevas funciones Python:**
```python
def is_class_code(code: str) -> bool:
    """Detecta si el código Python define una clase"""
    return bool(re.search(r'class\s+\w+', code))

def extract_class_name(code: str) -> str:
    """Extrae el nombre de la clase Python"""
    match = re.search(r'class\s+(\w+)', code)
    return match.group(1) if match else None
```

**Nuevas funciones TypeScript:**
```python
def is_class_code_ts(code: str) -> bool:
    """Detecta si el código TypeScript define una clase"""
    return bool(re.search(r'(?:export\s+)?class\s+\w+', code))

def extract_class_name_ts(code: str) -> str:
    """Extrae el nombre de la clase TypeScript"""
    match = re.search(r'(?:export\s+)?class\s+(\w+)', code)
    return match.group(1) if match else None
```

---

### 4. Ejecución de Tests para Clases

**Python - `CodeExecutionToolWithInterpreterPY`:**

```python
# Detectar tipo de código
is_class = is_class_code(code)

if is_class:
    # Instanciar la clase
    class_name = extract_class_name(code)
    instance_code = f"{class_name.lower()}_instance = {class_name}()"
    sbx.run_code(instance_code)
    
    # Para cada test con método
    for case in test_data:
        method_name = case.get("method")
        if method_name:
            # Llamada: instance.method(args)
            call = f"print({class_name.lower()}_instance.{method_name}({args}))"
else:
    # Función normal
    call = f"print({function_name}({args}))"
```

**TypeScript - `CodeExecutionToolWithInterpreterTS`:**

```typescript
// Si es clase, agregar instanciación al código
if (is_class) {
    const instance_code = `\nconst instance = new ${class_name}();\n`;
    // Escribir código + instanciación
    
    // Para cada test con método
    execution_code = `console.log(instance.${method_name}(${args}));`
}
```

---

### 5. Actualización del Agente Ejecutor de Pruebas

**Archivo:** `src/agents/ejecutor_pruebas.py`

```python
# Parsear estructura
test_structure = json.loads(respuesta_json)
code_type = test_structure.get('code_type', 'function')
class_name = test_structure.get('class_name')
function_name = test_structure.get('function_name')

# Logs informativos
if code_type == 'class':
    print(f"   ✅ Clase: {class_name}")
    methods = set(tc.get('method') for tc in test_cases if tc.get('method'))
    print(f"   ✅ Métodos a probar: {len(methods)} ({', '.join(methods)})")
else:
    print(f"   ✅ Función: {function_name}")
```

---

## 🎯 Ejemplo de Uso

### Código Generado (TypeScript)

```typescript
export class Calculator {
  public add(a: number, b: number): number {
    return a + b;
  }
  
  public subtract(a: number, b: number): number {
    return a - b;
  }
  
  public multiply(a: number, b: number): number {
    return a * b;
  }
  
  public divide(a: number, b: number): number {
    if (b === 0) throw new Error("No se puede dividir por cero.");
    return a / b;
  }
}
```

### Tests Generados Automáticamente

```json
{
  "language": "typescript",
  "code_type": "class",
  "class_name": "Calculator",
  "test_cases": [
    {"method": "add", "input": [2, 3], "expected": "5"},
    {"method": "add", "input": [0, 0], "expected": "0"},
    {"method": "add", "input": [-5, 3], "expected": "-2"},
    
    {"method": "subtract", "input": [5, 3], "expected": "2"},
    {"method": "subtract", "input": [0, 5], "expected": "-5"},
    
    {"method": "multiply", "input": [3, 4], "expected": "12"},
    {"method": "multiply", "input": [0, 5], "expected": "0"},
    
    {"method": "divide", "input": [10, 2], "expected": "5"},
    {"method": "divide", "input": [7, 0], "expected": "Error: No se puede dividir por cero."}
  ]
}
```

### Ejecución

```
--- 4.1 🧪 Ejecutor de Pruebas --- Generar estructura de tests
   ✅ Lenguaje detectado: typescript
   ✅ Tipo de código: class
   ✅ Clase: Calculator
   ✅ Métodos a probar: 4 (add, subtract, multiply, divide)
   ✅ Casos de prueba generados: 9

--- 4.2 🧪 Ejecutor de Pruebas --- Ejecutar casos de test (typescript)
   📦 Detectada clase: Calculator
   ✅ Ejecución completada
   Resultado: True
```

---

## 📊 Comparación Antes vs Ahora

### ❌ Antes (Solo Funciones)

```json
{
  "language": "typescript",
  "test_cases": [
    {"input": [2, 3], "expected": "5"}  // ¿Qué método?
  ]
}
```

**Problemas:**
- No se especifica qué método de la clase probar
- Solo se podía probar el primer método encontrado
- Tests incompletos para clases con múltiples métodos

### ✅ Ahora (Clases + Funciones)

```json
{
  "language": "typescript",
  "code_type": "class",
  "class_name": "Calculator",
  "test_cases": [
    {"method": "add", "input": [2, 3], "expected": "5"},
    {"method": "subtract", "input": [5, 3], "expected": "2"},
    {"method": "multiply", "input": [3, 4], "expected": "12"}
  ]
}
```

**Ventajas:**
- ✅ Especifica exactamente qué método probar
- ✅ Soporta múltiples métodos en la misma clase
- ✅ Tests completos y organizados por método
- ✅ Retrocompatible con funciones individuales

---

## 🔧 Compatibilidad con Código Existente

### Funciones Individuales (Sigue Funcionando)

```python
# Código
def factorial(n: int) -> int:
    if n == 0:
        return 1
    return n * factorial(n - 1)

# Tests generados
{
  "language": "python",
  "code_type": "function",
  "function_name": "factorial",
  "test_cases": [
    {"input": [5], "expected": "120"},
    {"input": [0], "expected": "1"}
  ]
}
```

**Campo `method` es opcional** - se ignora para funciones.

---

## 🧪 Casos de Prueba Cubiertos

### 1. Clase con Múltiples Métodos
✅ Calculator (add, subtract, multiply, divide)

### 2. Clase con Constructor
✅ Instanciación automática antes de probar métodos

### 3. Métodos con Diferentes Aridades
✅ add(a, b) - 2 argumentos
✅ sqrt(x) - 1 argumento

### 4. Métodos que Lanzan Excepciones
✅ divide(a, 0) → Error esperado

### 5. Funciones Individuales
✅ factorial(n) - Retrocompatibilidad

---

## 📝 Archivos Modificados

1. ✅ `src/models/schemas.py` - Schemas actualizados
2. ✅ `src/config/prompts.py` - Prompt actualizado con instrucciones para clases
3. ✅ `src/tools/code_executor.py` - Funciones de detección y ejecución
4. ✅ `src/agents/ejecutor_pruebas.py` - Logs informativos mejorados

---

## 🚀 Mejoras Futuras Posibles

1. **Métodos estáticos:**
   ```json
   {"method": "static:parse", "input": ["2024-01-01"], "expected": "..."}
   ```

2. **Métodos privados (para testing interno):**
   ```json
   {"method": "_private_helper", "input": [...], "expected": "..."}
   ```

3. **Setup/Teardown por clase:**
   ```json
   {
     "setup": "instance.initialize()",
     "test_cases": [...],
     "teardown": "instance.cleanup()"
   }
   ```

4. **Estado entre tests:**
   ```json
   {"method": "push", "input": [5], "expected": "5", "order": 1},
   {"method": "pop", "input": [], "expected": "5", "order": 2}
   ```

---

## ✅ Checklist de Implementación

- [x] Actualizar schemas Pydantic con campos para clases
- [x] Actualizar prompt con instrucciones para clases vs funciones
- [x] Crear funciones de detección de clases (Python y TypeScript)
- [x] Actualizar `CodeExecutionToolWithInterpreterPY` para clases
- [x] Actualizar `CodeExecutionToolWithInterpreterTS` para clases
- [x] Actualizar ejecutor_pruebas con logs informativos
- [x] Verificar compatibilidad con funciones existentes
- [x] Documentar cambios

---

**Fecha:** 10 de diciembre de 2025  
**Estado:** ✅ Implementado y probado  
**Impacto:** Alto - Expande significativamente las capacidades de testing
