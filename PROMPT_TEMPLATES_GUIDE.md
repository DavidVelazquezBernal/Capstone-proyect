# 🎯 Guía de Prompt Templates de LangChain

## 📋 Descripción

Los Prompt Templates de LangChain proporcionan una forma estructurada y dinámica de gestionar prompts, con validación automática de variables y mejor mantenibilidad.

## ✨ Características Implementadas

### 🎯 Funcionalidades

1. **ChatPromptTemplate** - Templates estructurados con roles (system, human)
2. **Variables Dinámicas** - Prompts parametrizados y reutilizables
3. **Validación Automática** - LangChain valida que todas las variables estén presentes
4. **Métodos de Formateo** - Funciones convenientes para cada agente
5. **Separación de Responsabilidades** - Prompts separados de la lógica de negocio

## 🚀 Uso

### Uso Básico en Agentes

```python
from config.prompt_templates import PromptTemplates

# Product Owner
prompt = PromptTemplates.format_product_owner(
    prompt_inicial="Crea una función factorial",
    feedback_stakeholder=""
)

# Desarrollador
prompt = PromptTemplates.format_desarrollador(
    requisitos_formales=requisitos_json,
    contexto_adicional="Código anterior tenía un error"
)

# SonarQube
prompt = PromptTemplates.format_sonarqube(
    reporte_sonarqube=reporte,
    codigo_actual=codigo
)

# Generador UTs
prompt = PromptTemplates.format_generador_uts(
    codigo_generado=codigo,
    requisitos_formales=requisitos,
    lenguaje="typescript"
)

# Stakeholder
prompt = PromptTemplates.format_stakeholder(
    requisitos_formales=requisitos,
    codigo_generado=codigo,
    resultado_tests=tests
)
```

### Uso Directo de Templates

```python
from config.prompt_templates import PromptTemplates

# Acceder al template directamente
template = PromptTemplates.PRODUCT_OWNER

# Formatear manualmente
messages = template.format_messages(
    prompt_inicial="Mi requisito",
    feedback_stakeholder="Feedback del stakeholder"
)

# Convertir a string
prompt_string = PromptTemplates._messages_to_string(messages)
```

### Obtener Template por Nombre

```python
from config.prompt_templates import get_prompt_template

# Obtener template dinámicamente
template = get_prompt_template("product_owner")
template = get_prompt_template("desarrollador")
template = get_prompt_template("sonarqube")
```

## 📊 Estructura de Templates

### ChatPromptTemplate con Roles

Cada template tiene dos partes:

1. **System Message**: Define el rol y las instrucciones del agente
2. **Human Message**: Contiene el contexto específico con variables

```python
PRODUCT_OWNER = ChatPromptTemplate.from_messages([
    ("system", """Rol:
Requirements Manager - Ingeniero de Requisitos y Product Owner combinados.

Objetivo:
Convertir el requisito inicial del usuario en una especificación formal..."""),
    
    ("human", """Prompt Inicial del Usuario: {prompt_inicial}

Feedback del Stakeholder: {feedback_stakeholder}

Genera los requisitos formales en formato JSON.""")
])
```

### Variables en Templates

Las variables se definen con `{nombre_variable}` y se validan automáticamente:

```python
# Variables requeridas
{prompt_inicial}           # Product Owner
{feedback_stakeholder}     # Product Owner
{requisitos_formales}      # Desarrollador, Generador UTs, Stakeholder
{contexto_adicional}       # Desarrollador
{reporte_sonarqube}        # SonarQube
{codigo_actual}            # SonarQube
{codigo_generado}          # Generador UTs, Stakeholder
{lenguaje}                 # Generador UTs
{resultado_tests}          # Stakeholder
```

## 🎨 Ventajas vs Prompts Estáticos

### Antes (Prompts Estáticos)

```python
# En config/prompts.py
PRODUCT_OWNER = """
Rol: Product Owner
...
"""

# En el agente
contexto = f"""
Prompt: {state['prompt_inicial']}
Feedback: {state['feedback_stakeholder']}
"""
respuesta = call_gemini(Prompts.PRODUCT_OWNER, contexto)
```

**Problemas:**
- ❌ No hay validación de variables
- ❌ Formato inconsistente
- ❌ Difícil de mantener
- ❌ No hay separación clara de roles

### Ahora (ChatPromptTemplate)

```python
# En config/prompt_templates.py
PRODUCT_OWNER = ChatPromptTemplate.from_messages([
    ("system", "Rol: Product Owner..."),
    ("human", "Prompt: {prompt_inicial}\nFeedback: {feedback_stakeholder}")
])

# En el agente
prompt = PromptTemplates.format_product_owner(
    prompt_inicial=state['prompt_inicial'],
    feedback_stakeholder=state['feedback_stakeholder']
)
respuesta = call_gemini(prompt, "")
```

**Beneficios:**
- ✅ Validación automática de variables
- ✅ Formato consistente
- ✅ Fácil de mantener
- ✅ Separación clara de roles (system/human)
- ✅ Reutilizable y extensible

## 🔧 Extender Templates

### Crear Nuevo Template

```python
# En config/prompt_templates.py

NUEVO_AGENTE = ChatPromptTemplate.from_messages([
    ("system", """Rol:
Tu nuevo rol aquí...

Objetivo:
Tu objetivo aquí..."""),
    
    ("human", """Variable 1: {variable1}

Variable 2: {variable2}

Instrucción final.""")
])

@classmethod
def format_nuevo_agente(cls, variable1: str, variable2: str) -> str:
    """Formatea el template del nuevo agente."""
    messages = cls.NUEVO_AGENTE.format_messages(
        variable1=variable1,
        variable2=variable2
    )
    return cls._messages_to_string(messages)
```

### Usar en Agente

```python
from config.prompt_templates import PromptTemplates

def nuevo_agente_node(state):
    prompt = PromptTemplates.format_nuevo_agente(
        variable1=state['dato1'],
        variable2=state['dato2']
    )
    
    respuesta = call_gemini(prompt, "")
    return state
```

## 🧪 Testing

Ejecuta el script de prueba:

```bash
python test_prompt_templates.py
```

Tests incluidos:
- ✅ Importaciones
- ✅ Creación de templates
- ✅ Formateo de Product Owner
- ✅ Formateo de Desarrollador
- ✅ Formateo de SonarQube
- ✅ Formateo de Generador UTs
- ✅ Formateo de Stakeholder
- ✅ Función get_prompt_template
- ✅ Integración con agentes

## 📈 Migración Completada

### Agentes Actualizados

| Agente | Archivo | Template | Estado |
|--------|---------|----------|--------|
| **Product Owner** | `product_owner.py` | `PRODUCT_OWNER` | ✅ Migrado |
| **Desarrollador** | `desarrollador.py` | `DESARROLLADOR` | ✅ Migrado |
| **SonarQube** | `sonarqube.py` | `SONARQUBE` | ✅ Migrado |
| **Generador UTs** | `generador_uts.py` | `GENERADOR_UTS` | ✅ Migrado |
| **Stakeholder** | `stakeholder.py` | `STAKEHOLDER` | ✅ Migrado |

### Cambios en Agentes

**Antes:**
```python
contexto_llm = f"Requisitos: {state['requisitos']}\nCódigo: {state['codigo']}"
respuesta = call_gemini(Prompts.AGENTE, contexto_llm)
```

**Ahora:**
```python
prompt = PromptTemplates.format_agente(
    requisitos=state['requisitos'],
    codigo=state['codigo']
)
respuesta = call_gemini(prompt, "")
```

## 🐛 Troubleshooting

### Error: "Missing required variable"

**Causa**: Falta una variable requerida en el template

**Solución**:
```python
# Asegúrate de pasar todas las variables
prompt = PromptTemplates.format_product_owner(
    prompt_inicial="...",
    feedback_stakeholder=""  # Pasar string vacío si no hay feedback
)
```

### Error: "Template not found"

**Causa**: Nombre de agente incorrecto en `get_prompt_template()`

**Solución**:
```python
# Usar nombres válidos
template = get_prompt_template("product_owner")  # ✅
template = get_prompt_template("ProductOwner")   # ❌
```

### Prompts no se formatean correctamente

**Causa**: Variables con nombres incorrectos

**Solución**:
```python
# Verificar nombres de variables en el template
print(PromptTemplates.PRODUCT_OWNER.input_variables)
# Output: ['prompt_inicial', 'feedback_stakeholder']
```

## 📚 Referencias

- [LangChain Prompt Templates](https://python.langchain.com/docs/modules/model_io/prompts/)
- [ChatPromptTemplate](https://python.langchain.com/docs/modules/model_io/prompts/prompt_templates/msg_prompt_templates)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

## 🎉 Resumen

Los Prompt Templates de LangChain proporcionan:

✅ **Estructura clara** con roles system/human
✅ **Validación automática** de variables
✅ **Mantenibilidad** mejorada
✅ **Reutilización** de templates
✅ **Separación de responsabilidades** entre prompts y lógica

**Implementado en:**
- ✅ Product Owner (requisitos formales)
- ✅ Desarrollador (generación de código)
- ✅ SonarQube (análisis de calidad)
- ✅ Generador UTs (generación de tests)
- ✅ Stakeholder (validación de negocio)

**Listo para producción** con todos los agentes migrados y tests completos.
