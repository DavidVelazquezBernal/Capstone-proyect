# 🔍 Guía de Output Parsers de LangChain

## 📋 Descripción

Los Output Parsers de LangChain proporcionan validación robusta y parsing automático de respuestas del LLM, con manejo inteligente de errores y limpieza de formato.

## ✨ Características Implementadas

### 🎯 Funcionalidades

1. **PydanticOutputParser Robusto** - Validación automática con schemas Pydantic
2. **Limpieza de Markdown** - Elimina bloques ```json automáticamente
3. **Extracción de JSON** - Encuentra JSON en texto con contenido extra
4. **Manejo de Errores** - Múltiples intentos con fallback
5. **Instrucciones de Formato** - Genera instrucciones para incluir en prompts

## 🚀 Uso

### Parsing Básico

```python
from llm.output_parsers import validate_and_parse
from models.schemas import FormalRequirements

# Parsear respuesta del LLM
json_response = call_gemini(prompt, context)
result = validate_and_parse(json_response, FormalRequirements)

# Usar el objeto validado
print(result.objetivo_funcional)
print(result.lenguaje_version)
```

### Crear Parser Personalizado

```python
from llm.output_parsers import create_parser_for_schema
from models.schemas import FormalRequirements

# Crear parser
parser = create_parser_for_schema(FormalRequirements)

# Usar parser
result = parser.parse(llm_response)
```

### Parsers Pre-configurados

```python
from llm.output_parsers import (
    get_formal_requirements_parser,
    get_azure_metadata_parser,
    get_test_execution_parser
)

# Product Owner
po_parser = get_formal_requirements_parser()
requirements = po_parser.parse(response)

# Azure DevOps
azure_parser = get_azure_metadata_parser()
metadata = azure_parser.parse(response)

# Test Execution
test_parser = get_test_execution_parser()
test_request = test_parser.parse(response)
```

### Instrucciones de Formato para Prompts

```python
from llm.output_parsers import get_format_instructions
from models.schemas import FormalRequirements

# Generar instrucciones
instructions = get_format_instructions(FormalRequirements)

# Incluir en el prompt
prompt = f"""
Tu tarea es generar requisitos formales.

{instructions}

Genera los requisitos para: {user_request}
"""
```

## 🛡️ Manejo Robusto de Errores

### Limpieza Automática de Markdown

El parser limpia automáticamente bloques markdown:

```python
# Entrada con markdown
response = """```json
{
    "objetivo_funcional": "Calcular factorial",
    "lenguaje_version": "Python 3.10"
}
```"""

# El parser limpia automáticamente
result = parser.parse(response)  # ✅ Funciona
```

### Extracción de JSON

Extrae JSON de texto con contenido adicional:

```python
# Entrada con texto extra
response = """Aquí está el JSON:

{
    "objetivo_funcional": "Sumar números",
    "lenguaje_version": "TypeScript"
}

Espero que sea útil."""

# El parser extrae el JSON automáticamente
result = parser.parse(response)  # ✅ Funciona
```

### Múltiples Intentos

El parser intenta 3 estrategias diferentes:

1. **Intento 1**: Parsing directo
2. **Intento 2**: Limpiar markdown y parsear
3. **Intento 3**: Extraer JSON y parsear

```python
# Cualquiera de estos formatos funciona
responses = [
    '{"key": "value"}',                    # JSON directo
    '```json\n{"key": "value"}\n```',      # Con markdown
    'Aquí: {"key": "value"} Listo.'        # Con texto extra
]

for response in responses:
    result = parser.parse(response)  # ✅ Todos funcionan
```

## 📊 Integración con Product Owner

El Product Owner usa automáticamente el parser robusto:

```python
# En product_owner.py
from llm.output_parsers import get_formal_requirements_parser

def product_owner_node(state):
    # Llamar al LLM
    response = call_gemini(prompt, context, response_schema=FormalRequirements)
    
    # Parsear con LangChain (automático)
    parser = get_formal_requirements_parser()
    req_data = parser.parse(response)
    
    # Fallback si falla
    if error:
        req_data = FormalRequirements.model_validate_json(response)
```

## 🎨 Crear Parsers para Nuevos Schemas

### 1. Definir Schema Pydantic

```python
# En models/schemas.py
from pydantic import BaseModel, Field

class MiNuevoSchema(BaseModel):
    campo1: str = Field(description="Descripción del campo 1")
    campo2: int = Field(description="Descripción del campo 2")
```

### 2. Crear Parser

```python
# En llm/output_parsers.py
def get_mi_nuevo_parser() -> RobustPydanticOutputParser:
    """Parser para MiNuevoSchema"""
    from models.schemas import MiNuevoSchema
    return create_parser_for_schema(MiNuevoSchema)
```

### 3. Usar en Agente

```python
from llm.output_parsers import get_mi_nuevo_parser

def mi_agente_node(state):
    response = call_gemini(prompt, context)
    parser = get_mi_nuevo_parser()
    result = parser.parse(response)
    return result
```

## 🧪 Testing

Ejecuta el script de prueba:

```bash
python test_output_parsers.py
```

Tests incluidos:
- ✅ Importaciones
- ✅ Creación de parsers
- ✅ Instrucciones de formato
- ✅ Parsing JSON válido
- ✅ Parsing con markdown
- ✅ Parsing con texto extra
- ✅ Manejo de JSON inválido
- ✅ Integración con Product Owner

## 🔧 Configuración Avanzada

### Parser con Retry Automático

```python
from llm.output_parsers import parse_with_retry
from models.schemas import FormalRequirements

# Intentar hasta 3 veces
result = parse_with_retry(
    text=llm_response,
    schema=FormalRequirements,
    max_retries=3
)

if result:
    print("✅ Parsing exitoso")
else:
    print("❌ Parsing falló después de 3 intentos")
```

### Logging Detallado

Los parsers incluyen logging automático:

```python
# Nivel DEBUG muestra detalles del parsing
import logging
logging.basicConfig(level=logging.DEBUG)

parser = get_formal_requirements_parser()
result = parser.parse(response)

# Output:
# DEBUG: ✅ Parser creado para schema: FormalRequirements
# WARNING: ⚠️ Primer intento de parsing falló: ...
# INFO: ✅ Parsing exitoso en intento 2
```

## 📈 Ventajas vs Parsing Manual

### Antes (Parsing Manual)

```python
import json

try:
    data = json.loads(response)
    req = FormalRequirements(**data)
except json.JSONDecodeError as e:
    # Manejar error manualmente
    print(f"Error: {e}")
except ValidationError as e:
    # Manejar validación manualmente
    print(f"Error: {e}")
```

### Ahora (Con Parser LangChain)

```python
from llm.output_parsers import validate_and_parse

# Todo el manejo de errores está incluido
req = validate_and_parse(response, FormalRequirements)
```

**Beneficios:**
- ✅ Limpieza automática de markdown
- ✅ Extracción de JSON del texto
- ✅ Múltiples intentos de parsing
- ✅ Logging detallado
- ✅ Menos código boilerplate

## 🐛 Troubleshooting

### Error: "OutputParserException"

**Causa**: El texto no contiene JSON válido

**Solución**:
```python
# Verificar la respuesta del LLM
print(f"Respuesta: {response}")

# Usar parse_with_retry para más intentos
result = parse_with_retry(response, schema, max_retries=5)
```

### Error: "ValidationError"

**Causa**: El JSON no cumple con el schema Pydantic

**Solución**:
```python
# Verificar el schema
instructions = get_format_instructions(FormalRequirements)
print(instructions)

# Incluir instrucciones en el prompt
prompt = f"{base_prompt}\n\n{instructions}"
```

### Parser no limpia markdown

**Causa**: Formato de markdown no estándar

**Solución**:
```python
# Limpiar manualmente antes de parsear
cleaned = response.replace("```json", "").replace("```", "")
result = parser.parse(cleaned)
```

## 📚 Referencias

- [LangChain Output Parsers](https://python.langchain.com/docs/modules/model_io/output_parsers/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [JSON Schema](https://json-schema.org/)

## 🎉 Resumen

Los Output Parsers de LangChain proporcionan:

✅ **Validación automática** con Pydantic
✅ **Limpieza robusta** de formatos
✅ **Manejo de errores** inteligente
✅ **Logging detallado** para debugging
✅ **Fácil integración** con agentes existentes

**Implementado en:**
- ✅ Product Owner (requisitos formales)
- ✅ Parsers pre-configurados para Azure DevOps y Tests
- ✅ Framework extensible para nuevos schemas

**Listo para producción** con fallback automático al parsing manual si es necesario.
