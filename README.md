# Capstone Proyecto Multiagente - Sistema de Desarrollo Ágil

Sistema multiagente para desarrollo automatizado de código Python y TypeScript usando LangGraph y Google Gemini.

## 📁 Estructura del Proyecto

```
Capstone proyect v2/
├── src/
│   ├── __init__.py
│   ├── main.py                      # Punto de entrada principal
│   │
│   ├── config/                      # Configuración
│   │   ├── __init__.py
│   │   ├── settings.py              # Variables de entorno y configuración
│   │   └── prompts.py               # Prompts centralizados de agentes
│   │
│   ├── models/                      # Modelos de datos
│   │   ├── __init__.py
│   │   ├── state.py                 # AgentState (TypedDict)
│   │   └── schemas.py               # Schemas Pydantic
│   │
│   ├── tools/                       # Herramientas
│   │   ├── __init__.py
│   │   ├── code_executor.py         # Ejecución segura de código Python/TypeScript
│   │   └── file_utils.py            # Utilidades de archivos y detección de lenguaje
│   │
│   ├── agents/                      # Agentes del sistema
│   │   ├── __init__.py
│   │   ├── ingeniero_requisitos.py  # Agente 1: Clarificación
│   │   ├── product_owner.py         # Agente 2: Formalización
│   │   ├── codificador.py           # Agente 3: Desarrollo
│   │   ├── probador_depurador.py    # Agente 4: QA
│   │   └── stakeholder.py           # Agente 5: Validación
│   │
│   ├── llm/                         # Cliente LLM
│   │   ├── __init__.py
│   │   └── gemini_client.py         # Cliente Gemini
│   │
│   └── workflow/                    # Workflow LangGraph
│       ├── __init__.py
│       └── graph.py                 # Configuración del grafo
│
├── output/                          # Salidas generadas
├── .env                             # Variables de entorno
├── requirements.txt
├── DOCUMENTACION.md
└── README.md
```

## 🚀 Instalación

1. **Clonar el repositorio**

2. **Crear entorno virtual**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**

Crear archivo `.env` en la raíz del proyecto:
```env
GEMINI_API_KEY=tu_clave_api_aqui
E2B_API_KEY=tu_clave_e2b_aqui
```

## 💻 Uso

### Ejecución básica

```bash
python src/main.py
```

### Uso programático

```python
from src.main import run_development_workflow

# Ejemplo Python
prompt = "Crea una función para calcular el factorial de un número"
final_state = run_development_workflow(prompt, max_attempts=3)

# Ejemplo TypeScript
prompt_ts = "Quiero una función en TypeScript para sumar un array de números"
final_state_ts = run_development_workflow(prompt_ts, max_attempts=3)
```

### Salida del código generado

El sistema detecta automáticamente el lenguaje del código generado:
- **Python**: Guarda como `codigo_final.py` en el directorio `output/`
- **TypeScript**: Guarda como `codigo_final.ts` en el directorio `output/`

El código se limpia automáticamente de marcadores markdown (` ```python `, ` ```typescript `, ` ``` `).

## 🏗️ Arquitectura

### Flujo de Trabajo

```
START → Ingeniero Requisitos → Product Owner → Codificador → Probador
           ↑                                                    ↓
           |                                                  ¿Pasa?
           |                                                    ↓
           |                                                Stakeholder
           |                                                    ↓
           |                                               ¿Validado?
           |                                                    ↓
           ←────────────────────────────────────────────────  NO
                                                               ↓
                                                              END
```

### Agentes

1. **Ingeniero de Requisitos**: Clarifica y refina requisitos
2. **Product Owner**: Formaliza especificaciones técnicas
3. **Codificador**: Genera y corrige código Python
4. **Probador/Depurador**: Ejecuta pruebas y valida código
5. **Stakeholder**: Valida cumplimiento de visión de negocio

## 🛠️ Tecnologías

- **LangGraph**: Framework de grafos de agentes
- **Google Gemini**: Modelo LLM
- **Pydantic**: Validación de datos
- **E2B Code Interpreter**: Sandbox de ejecución
- **Python-dotenv**: Gestión de entorno

## 📝 Configuración

Editar `src/config/settings.py` para ajustar:
- `MAX_ATTEMPTS`: Máximo de ciclos (default: 3)
- `TEMPERATURE`: Temperatura del LLM (default: 0.1)
- `MAX_OUTPUT_TOKENS`: Tokens máximos de salida (default: 10000)

## 📄 Licencia

MIT License

## 👥 Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue primero para discutir los cambios propuestos.
