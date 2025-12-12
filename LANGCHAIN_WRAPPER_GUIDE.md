# 🔗 Guía del Wrapper LangChain para Gemini

## 📋 Descripción

Esta implementación añade un wrapper opcional de LangChain para el cliente de Google Gemini, proporcionando capacidades avanzadas de debugging, monitoreo y análisis sin modificar el código existente.

## ✨ Características

### 🎯 Funcionalidades Añadidas

1. **Callbacks Integrados** - Monitoreo de llamadas al LLM
2. **Streaming de Respuestas** - Respuestas en tiempo real
3. **Token Counting** - Conteo automático de tokens
4. **LangSmith Integration** - Debugging avanzado (opcional)
5. **Compatibilidad Total** - Funciona con el código existente sin cambios

## 🚀 Instalación

### 1. Instalar Dependencia

```bash
pip install langchain-google-genai
```

O actualizar todas las dependencias:

```bash
pip install -r requirements.txt
```

### 2. Habilitar el Wrapper

Edita `src/.env` y añade:

```env
USE_LANGCHAIN_WRAPPER=true
```

## 📊 Uso

### Modo Básico (Sin Cambios en el Código)

El wrapper se activa automáticamente cuando `USE_LANGCHAIN_WRAPPER=true`:

```python
from llm.gemini_client import call_gemini

# Esta llamada usará el wrapper de LangChain automáticamente
response = call_gemini(role_prompt, context)
```

**Nota:** El wrapper solo se usa para llamadas simples (sin `response_schema` ni `allow_use_tool`).

### Modo Avanzado (Uso Directo)

Para usar características avanzadas, importa directamente:

```python
from llm.langchain_gemini import create_langchain_llm, call_gemini_with_langchain

# Crear instancia del LLM
llm = create_langchain_llm(streaming=True)

# Usar con streaming
response = call_gemini_with_langchain(
    role_prompt="Eres un asistente útil",
    context="Explica qué es LangChain",
    streaming=True
)
```

### Token Counting

```python
from llm.langchain_gemini import get_token_count

text = "Este es un texto de ejemplo para contar tokens."
token_info = get_token_count(text)

print(f"Tokens: {token_info['total_tokens']}")
print(f"Modelo: {token_info['model']}")
```

### Callbacks Personalizados

```python
from langchain_core.callbacks import BaseCallbackHandler
from llm.langchain_gemini import create_langchain_llm

class MyCustomCallback(BaseCallbackHandler):
    def on_llm_start(self, serialized, prompts, **kwargs):
        print(f"🚀 Iniciando llamada al LLM...")
    
    def on_llm_end(self, response, **kwargs):
        print(f"✅ Llamada completada")

# Usar con callbacks personalizados
llm = create_langchain_llm(callbacks=[MyCustomCallback()])
```

## 🧪 Testing

Ejecuta el script de prueba:

```bash
python test_langchain_wrapper.py
```

Este script verifica:
- ✅ Importaciones correctas
- ✅ Configuración válida
- ✅ Funcionamiento del wrapper
- ✅ Compatibilidad con código existente

## 🔄 Modos de Operación

### 1. Cliente Directo (Por Defecto)

```env
USE_LANGCHAIN_WRAPPER=false
```

- Usa `google.genai.Client` directamente
- Menor overhead
- Ideal para producción

### 2. Wrapper LangChain (Opcional)

```env
USE_LANGCHAIN_WRAPPER=true
```

- Usa `ChatGoogleGenerativeAI` de LangChain
- Callbacks y streaming
- Ideal para desarrollo y debugging

### 3. Modo Mock (Testing)

```env
LLM_MOCK_MODE=true
```

- No hace llamadas reales al LLM
- Usa respuestas simuladas
- Ideal para testing sin API key

## 📈 Ventajas del Wrapper

### Para Desarrollo

- **Debugging Mejorado**: Callbacks para rastrear cada llamada
- **Monitoreo**: Métricas automáticas de uso
- **Streaming**: Ver respuestas en tiempo real
- **Token Tracking**: Optimizar costos

### Para Producción

- **Compatibilidad**: Funciona con código existente
- **Fallback Automático**: Si falla, usa cliente directo
- **Configuración Flexible**: Activar/desactivar sin cambios de código

## 🎯 Casos de Uso

### 1. Debugging de Prompts

```python
from langchain_core.callbacks import StdOutCallbackHandler
from llm.langchain_gemini import create_langchain_llm

# Ver todas las llamadas en consola
llm = create_langchain_llm(
    streaming=True,
    callbacks=[StdOutCallbackHandler()]
)
```

### 2. Análisis de Costos

```python
from llm.langchain_gemini import get_token_count

# Estimar tokens antes de llamar
prompt = "Tu prompt muy largo aquí..."
tokens = get_token_count(prompt)

if tokens['total_tokens'] > 1000:
    print("⚠️ Prompt muy largo, considera resumir")
```

### 3. Integración con LangSmith

```bash
# Configurar LangSmith (opcional)
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=tu-api-key
export LANGCHAIN_PROJECT=capstone-multiagente
```

Todas las llamadas se registrarán automáticamente en LangSmith para análisis.

## 🔧 Configuración Avanzada

### Variables de Entorno

```env
# Wrapper LangChain
USE_LANGCHAIN_WRAPPER=true

# LangSmith (opcional - para debugging avanzado)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=tu-langsmith-api-key
LANGCHAIN_PROJECT=mi-proyecto

# Configuración del modelo (heredada)
MODEL_NAME=gemini-2.5-flash
TEMPERATURE=0.1
MAX_OUTPUT_TOKENS=4000
```

## 🐛 Troubleshooting

### Error: "No module named 'langchain_google_genai'"

```bash
pip install langchain-google-genai
```

### El wrapper no se activa

1. Verifica que `USE_LANGCHAIN_WRAPPER=true` en `src/.env`
2. Revisa los logs: debe aparecer "✅ Wrapper de LangChain habilitado"
3. Asegúrate de que no estés usando `response_schema` o `allow_use_tool`

### Fallback al cliente directo

El wrapper automáticamente usa el cliente directo si:
- Hay un error en la importación
- La llamada usa `response_schema` (Product Owner)
- La llamada usa `allow_use_tool` (herramientas)

Esto es intencional para mantener compatibilidad.

## 📚 Referencias

- [LangChain Documentation](https://python.langchain.com/)
- [ChatGoogleGenerativeAI](https://python.langchain.com/docs/integrations/chat/google_generative_ai)
- [LangSmith](https://docs.smith.langchain.com/)
- [Google Gemini API](https://ai.google.dev/docs)

## 🎉 Resumen

El wrapper de LangChain es **opcional** y proporciona:

✅ **Debugging avanzado** sin modificar código
✅ **Monitoreo de tokens** para optimizar costos
✅ **Streaming** para mejor UX
✅ **Compatibilidad total** con el sistema existente
✅ **Fallback automático** si hay problemas

**Recomendación:**
- **Desarrollo**: `USE_LANGCHAIN_WRAPPER=true` para debugging
- **Producción**: `USE_LANGCHAIN_WRAPPER=false` para performance
