# 🔧 Guía de Configuración - Nuevas Variables

## 📋 Resumen

Se han agregado **3 nuevas variables configurables** al sistema que te permiten personalizar el comportamiento sin modificar código:

| Variable | Valor por Defecto | Descripción |
|----------|-------------------|-------------|
| `MODEL_NAME` | `gemini-2.5-flash` | Modelo de Gemini a utilizar |
| `TEMPERATURE` | `0.1` | Temperatura del modelo (0.0-1.0) |
| `TEST_EXECUTION_TIMEOUT` | `60` | Timeout en segundos para tests |

---

## 🚀 Cómo Actualizar tu `.env`

### Opción 1: Agregar Manualmente

Abre tu archivo `src/.env` y agrega estas líneas:

```env
# ============================================================
# CONFIGURACIÓN DEL MODELO LLM (NUEVAS VARIABLES)
# ============================================================
# Modelo a usar (gemini-2.5-flash, gemini-1.5-pro, etc.)
MODEL_NAME=gemini-2.5-flash

# Temperatura del modelo (0.0 = determinista, 1.0 = creativo)
TEMPERATURE=0.1

# Timeout en segundos para ejecución de tests (vitest/pytest)
TEST_EXECUTION_TIMEOUT=60
```

### Opción 2: Usar el Archivo de Ejemplo

Si no tienes un `.env`, copia el archivo de ejemplo:

```bash
# En PowerShell
Copy-Item "src\.env.example" "src\.env"
```

Luego edita `src/.env` con tus valores reales.

---

## 🎯 Casos de Uso

### 1️⃣ Cambiar a un Modelo Más Potente

```env
MODEL_NAME=gemini-1.5-pro
TEMPERATURE=0.2
```

### 2️⃣ Aumentar Timeout para Tests Complejos

```env
TEST_EXECUTION_TIMEOUT=120
```

### 3️⃣ Modo Más Creativo (Mayor Temperatura)

```env
TEMPERATURE=0.7
```

### 4️⃣ Modo Determinista (Temperatura Mínima)

```env
TEMPERATURE=0.0
```

---

## ✅ Verificación

Después de actualizar tu `.env`, verifica que las variables se carguen correctamente:

```python
from config.settings import settings

print(f"Modelo: {settings.MODEL_NAME}")
print(f"Temperatura: {settings.TEMPERATURE}")
print(f"Timeout: {settings.TEST_EXECUTION_TIMEOUT}s")
```

---

## 📚 Documentación de Variables

### `MODEL_NAME`

**Valores posibles:**
- `gemini-2.5-flash` (rápido, económico) ⚡
- `gemini-1.5-pro` (más potente, más caro) 💪
- `gemini-1.5-flash` (balance) ⚖️

**Cuándo cambiar:**
- Usa `pro` para tareas complejas de razonamiento
- Usa `flash` para desarrollo rápido y económico

### `TEMPERATURE`

**Rango:** `0.0` - `1.0`

**Recomendaciones:**
- `0.0-0.2`: Código determinista, respuestas consistentes ✅
- `0.3-0.5`: Balance creatividad/consistencia ⚖️
- `0.6-1.0`: Respuestas creativas, menos predecibles 🎨

### `TEST_EXECUTION_TIMEOUT`

**Rango:** `30` - `300` segundos

**Recomendaciones:**
- `30-60s`: Tests unitarios simples ⚡
- `60-120s`: Tests de integración 🔧
- `120-300s`: Tests E2E o complejos 🐢

---

## ⚠️ Notas Importantes

1. **No commitear `.env`**: El archivo `.env` está en `.gitignore` por seguridad
2. **Usar `.env.example`**: Commitea cambios en `.env.example` para el equipo
3. **Validación automática**: El sistema valida las configuraciones al inicio
4. **Valores por defecto**: Si no defines una variable, se usa el valor por defecto

---

## 🔗 Archivos Relacionados

- **Configuración:** `src/config/settings.py`
- **Ejemplo:** `src/.env.example`
- **Tu configuración:** `src/.env` (no versionado)

---

## 🆘 Solución de Problemas

### Error: "GEMINI_API_KEY no configurada"

```env
# Asegúrate de tener esto en tu .env
GEMINI_API_KEY=tu_api_key_real_aqui
```

### Tests fallan por timeout

```env
# Aumenta el timeout
TEST_EXECUTION_TIMEOUT=120
```

### Respuestas inconsistentes del LLM

```env
# Reduce la temperatura
TEMPERATURE=0.0
```

---

## 📊 Mejoras Implementadas

Además de las nuevas variables, se implementaron:

✅ **Validación completa** de configuraciones por servicio  
✅ **Manejo robusto** de errores 503  
✅ **Validación de precondiciones** en MOCK mode  
✅ **Helper de logging** reutilizable  
✅ **Type hints** completos  
✅ **Código limpio** sin comentarios obsoletos  

---

**¡Listo para usar!** 🚀
