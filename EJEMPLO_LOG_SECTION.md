# 📝 Guía de Uso: `log_section()`

## 🎯 Propósito

La función `log_section()` proporciona un formato consistente para logging de secciones en todo el proyecto, reemplazando los separadores manuales repetitivos.

---

## ✅ Antes vs Después

### ❌ **Antes (Separadores Manuales)**

```python
logger.error(f"\n{'='*60}")
logger.error("❌ ERROR: EL LLM NO DEVOLVIÓ RESPUESTA VÁLIDA")
logger.error(f"{'='*60}")
logger.error(f"📋 Información de diagnóstico:")
# ... más logging
logger.error(f"{'='*60}\n")
```

**Problemas:**
- Código repetitivo
- Inconsistente (diferentes longitudes, caracteres)
- Difícil de mantener
- Mezcla de `\n` al inicio/final

### ✅ **Después (con `log_section()`)**

```python
from utils.logging_helpers import log_section

logger.error("")
log_section(logger, "❌ ERROR: EL LLM NO DEVOLVIÓ RESPUESTA VÁLIDA", level="error")
logger.error(f"📋 Información de diagnóstico:")
# ... más logging
logger.error("")
```

**Beneficios:**
- ✅ Código limpio y conciso
- ✅ Formato consistente
- ✅ Fácil de mantener
- ✅ Reutilizable

---

## 📚 Sintaxis

```python
log_section(
    logger: logging.Logger,           # Logger instance
    title: str,                       # Título de la sección
    level: str = "info",              # Nivel: debug, info, warning, error, critical
    separator_char: str = "=",        # Carácter del separador
    separator_length: int = 60        # Longitud del separador
)
```

---

## 💡 Ejemplos de Uso

### 1️⃣ **Sección Informativa**

```python
from utils.logging_helpers import log_section

log_section(logger, "🚀 INICIO DEL PROCESO", level="info")
logger.info("Procesando datos...")
logger.info("Configuración cargada")
```

**Salida:**
```
============================================================
🚀 INICIO DEL PROCESO
============================================================
Procesando datos...
Configuración cargada
```

---

### 2️⃣ **Sección de Error**

```python
log_section(logger, "❌ ERROR CRÍTICO", level="error")
logger.error(f"Detalles: {error_message}")
logger.error("Stack trace:")
```

**Salida:**
```
============================================================
❌ ERROR CRÍTICO
============================================================
Detalles: Connection timeout
Stack trace:
```

---

### 3️⃣ **Sección de Advertencia**

```python
log_section(logger, "⚠️ ADVERTENCIA: REINTENTOS AGOTADOS", level="warning")
logger.warning("Se alcanzó el límite de reintentos")
logger.warning("Considera aumentar MAX_API_RETRIES")
```

---

### 4️⃣ **Sección de Debug**

```python
log_section(logger, "🔍 DEBUG: ESTADO INTERNO", level="debug")
logger.debug(f"Variables: {vars()}")
logger.debug(f"Stack: {stack_trace}")
```

---

### 5️⃣ **Separador Personalizado**

```python
log_section(
    logger, 
    "🎉 PROCESO COMPLETADO", 
    level="info",
    separator_char="-",
    separator_length=80
)
```

**Salida:**
```
--------------------------------------------------------------------------------
🎉 PROCESO COMPLETADO
--------------------------------------------------------------------------------
```

---

## 🎨 Niveles de Logging

| Nivel | Uso | Emoji Sugerido |
|-------|-----|----------------|
| `debug` | Información detallada para debugging | 🔍 |
| `info` | Información general del flujo | ℹ️ 🚀 ✅ |
| `warning` | Advertencias no críticas | ⚠️ |
| `error` | Errores que requieren atención | ❌ 🔴 |
| `critical` | Errores críticos del sistema | 🚨 💥 |

---

## 📦 Archivos Refactorizados

Los siguientes archivos ya usan `log_section()`:

✅ **`src/llm/gemini_client.py`**
- Sección de error de respuesta vacía
- Sección de diagnóstico MALFORMED_FUNCTION_CALL
- Sección de error 503
- Sección de reintentos fallidos

---

## 🔄 Patrón Recomendado

### Para Secciones con Contenido

```python
# Línea vacía antes
logger.error("")

# Sección
log_section(logger, "TÍTULO DE LA SECCIÓN", level="error")

# Contenido
logger.error("Línea 1")
logger.error("Línea 2")

# Línea vacía después (opcional)
logger.error("")
```

### Para Secciones Simples

```python
log_section(logger, "TÍTULO", level="info")
# Continuar con el flujo normal
```

---

## 🚫 Qué NO Hacer

### ❌ No usar separadores manuales

```python
# MAL
logger.info("="*60)
logger.info("TÍTULO")
logger.info("="*60)
```

### ❌ No mezclar estilos

```python
# MAL - Inconsistente
logger.info("="*60)
log_section(logger, "TÍTULO", level="info")
logger.info("-"*50)
```

### ✅ Usar siempre `log_section()`

```python
# BIEN
log_section(logger, "SECCIÓN 1", level="info")
# ... contenido
log_section(logger, "SECCIÓN 2", level="info")
```

---

## 🎯 Migración Rápida

### Buscar y Reemplazar

**Patrón a buscar:**
```python
logger.LEVEL(f"\n{'='*60}")
logger.LEVEL("TÍTULO")
logger.LEVEL(f"{'='*60}")
```

**Reemplazar con:**
```python
logger.LEVEL("")
log_section(logger, "TÍTULO", level="LEVEL")
```

---

## 📊 Estadísticas de Refactorización

| Archivo | Separadores Eliminados | Líneas Reducidas |
|---------|------------------------|------------------|
| `gemini_client.py` | 12 | ~24 líneas |

**Total:** 12 separadores manuales → 4 llamadas a `log_section()`

---

## 🔗 Referencias

- **Implementación:** `src/utils/logging_helpers.py`
- **Ejemplo de uso:** `src/llm/gemini_client.py`
- **Documentación:** Este archivo

---

**¡Usa `log_section()` para un logging más limpio y consistente!** 🎉
