# Ejemplos de Uso del Sistema Multiagente

Este documento contiene ejemplos de cómo usar el sistema multiagente de desarrollo.

## Tabla de Contenidos

- [Uso Básico](#uso-básico)
- [Configuración Avanzada](#configuración-avanzada)
- [Ejemplos por Lenguaje](#ejemplos-por-lenguaje)
  - [Python](#python)
  - [TypeScript](#typescript)
- [Ejemplos por Complejidad](#ejemplos-por-complejidad)
  - [Básicos](#básicos)
  - [Intermedios](#intermedios)
  - [Avanzados](#avanzados)

---

## Uso Básico

### Ejemplo 1: Configuración por Defecto

```python
from main import run_development_workflow

prompt = "Crea una función para calcular el factorial de un número"
final_state = run_development_workflow(prompt)
```

### Ejemplo 2: Con max_attempts (DEPRECATED)

```python
prompt = "Crea una función para validar emails"
final_state = run_development_workflow(prompt, max_attempts=3)
```

---

## Configuración Avanzada

### Uso con RetryConfig Personalizado

```python
from main import run_development_workflow
from config.settings import RetryConfig

prompt = "Implementa una clase Calculator con operaciones básicas"

retry_config = RetryConfig(
    max_attempts=2,              # Máximo de ciclos completos
    max_debug_attempts=5,        # Máximo de intentos Testing-Desarrollador
    max_sonarqube_attempts=2,    # Máximo de intentos SonarQube-Desarrollador
    max_revisor_attempts=3       # Máximo de intentos de revisión
)

final_state = run_development_workflow(prompt, retry_config=retry_config)
```

---

## Ejemplos por Lenguaje

### Python

#### Suma de Lista
```python
prompt = (
    "Quiero una función simple en Python para sumar una lista de números, "
    "y quiero que la salida sea una frase."
)
final_state = run_development_workflow(prompt)
```

#### Factorial
```python
prompt = (
    "Quiero una función simple en Python para generar el factorial de un número, "
    "y quiero que la salida sea un string con una frase descriptiva."
)
final_state = run_development_workflow(prompt)
```

#### Capitalización
```python
prompt = (
    "Quiero una función simple en Python que capitalice la primera letra de cada palabra"
)
final_state = run_development_workflow(prompt)
```

### TypeScript

#### Suma de Array
```python
prompt = (
    "Quiero una función simple en TypeScript para sumar un array de números, "
    "y quiero que la salida sea un string con una frase descriptiva."
)
final_state = run_development_workflow(prompt)
```

#### Factorial
```python
prompt = (
    "Quiero una función simple en TypeScript para generar el factorial de un número, "
    "y quiero que la salida sea un string con una frase descriptiva."
)
final_state = run_development_workflow(prompt)
```

#### Factorial Doble con Suma
```python
prompt = (
    "Quiero una función simple en TypeScript para generar el factorial de dos números y luego los sume, "
    "y quiero que la salida sea un string con una frase descriptiva."
)
final_state = run_development_workflow(prompt)
```

#### Capitalización
```python
prompt = (
    "Quiero una función simple en TypeScript que capitalice la primera letra de cada palabra"
)
final_state = run_development_workflow(prompt)
```

---

## Ejemplos por Complejidad

### Básicos

#### Validación de Email
```python
prompt = (
    "Quiero una función simple en TypeScript que valide si un correo electrónico es válido, "
    "y quiero que la salida sea un string con una frase descriptiva."
)
final_state = run_development_workflow(prompt)
```

#### Stack (Pila)
```python
prompt = "Implementa una clase Stack (pila) en TypeScript con métodos push, pop, peek, isEmpty y size"
final_state = run_development_workflow(prompt)
```

#### Calculadora
```python
prompt = (
    "Implementa una clase Calculator en TypeScript con las operaciones básicas (+, -, *, /) "
    "y manejo de división por cero"
)
final_state = run_development_workflow(prompt)
```

### Intermedios

#### QuickSort
```python
prompt = "Implementa un algoritmo de ordenamiento QuickSort en TypeScript con análisis de complejidad"
final_state = run_development_workflow(prompt)
```

#### Validación de Paréntesis Balanceados
```python
prompt = (
    "Crea una función en TypeScript que valide si un string tiene paréntesis balanceados, "
    "incluyendo [], {} y ()"
)
final_state = run_development_workflow(prompt)
```

#### Caché LRU
```python
prompt = (
    "Crea en TypeScript un sistema de caché LRU (Least Recently Used) "
    "con tiempo de expiración configurable"
)
final_state = run_development_workflow(prompt)
```

#### Factory Pattern
```python
prompt = (
    "Crea en TypeScript un Factory Pattern para generar diferentes tipos de vehículos "
    "con sus características"
)
final_state = run_development_workflow(prompt)
```

#### Patrón Observer
```python
prompt = (
    "Implementa en TypeScript el patrón Observer para un sistema de notificaciones"
)
final_state = run_development_workflow(prompt)
```

#### Middleware de Logging
```python
prompt = (
    "Crea en TypeScript un middleware de logging que registre requests, responses y errores "
    "con diferentes niveles"
)
final_state = run_development_workflow(prompt)
```

#### Sistema RBAC
```python
prompt = (
    "Crea en TypeScript un sistema de permisos basado en roles (RBAC) "
    "con herencia de roles y permisos granulares"
)
final_state = run_development_workflow(prompt)
```

#### Rate Limiter
```python
prompt = (
    "Implementa en TypeScript un rate limiter (limitador de peticiones) "
    "con ventana deslizante"
)
final_state = run_development_workflow(prompt)
```

#### Singleton Thread-Safe
```python
prompt = (
    "Crea en TypeScript un Singleton thread-safe para gestionar configuración de aplicación"
)
final_state = run_development_workflow(prompt)
```

#### Cliente HTTP con Retry
```python
prompt = (
    "Crea en TypeScript un cliente HTTP con retry logic, timeout y manejo de errores"
)
final_state = run_development_workflow(prompt)
```

### Avanzados

#### Binary Search Tree
```python
prompt = (
    "Implementa una clase BinarySearchTree en TypeScript con métodos insert, search, delete, "
    "inorder traversal y balance check. Incluye manejo de casos edge como árboles vacíos, "
    "nodos duplicados y eliminación de nodos con dos hijos. Añade validación de tipos y "
    "documentación JSDoc completa."
)
final_state = run_development_workflow(prompt)
```

---

## Verificación de Resultados

Después de ejecutar el workflow, puedes verificar el resultado:

```python
if final_state and final_state.get('validado'):
    print("🎉 ¡Flujo completado exitosamente!")
    print(f"Intentos totales: {final_state['attempt_count']}")
    print(f"Código generado guardado en: output/")
else:
    print("⚠️ El flujo terminó sin validación exitosa.")
    print(f"Último feedback: {final_state.get('feedback_stakeholder', 'N/A')}")
```

---

## Notas Importantes

1. **max_attempts está DEPRECATED**: Usa `RetryConfig` en su lugar para mayor control
2. **Salida**: Los archivos generados se guardan en el directorio `output/`
3. **Logs**: Los logs se guardan en `output/logs/`
4. **Tests**: Los tests unitarios se generan automáticamente con vitest (TypeScript) o pytest (Python)
5. **Calidad**: El código pasa por análisis de SonarQube y revisión de código automática
