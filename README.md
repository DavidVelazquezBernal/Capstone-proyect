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
│   │   ├── sonarqube_mcp.py         # Integración con SonarQube MCP
│   │   ├── azure_devops_integration.py  # 🔷 Cliente de Azure DevOps API
│   │   └── file_utils.py            # Utilidades de archivos y detección de lenguaje
│   │
│   ├── agents/                      # Agentes del sistema
│   │   ├── __init__.py
│   │   ├── ingeniero_requisitos.py  # Agente 1: Clarificación
│   │   ├── product_owner.py         # Agente 2: Formalización
│   │   ├── desarrollador.py # Agente 3: Desarrollo y corrección
│   │   ├── sonarqube.py  # Agente 3.5: Análisis de calidad
│   │   ├── generador_uts.py         # Agente 3.6: Generación de tests
│   │   ├── probador_uts.py          # Agente 4: Ejecución de tests
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

**Para testing (requerido):**

```bash
# TypeScript - Instalar en directorio output/
cd output
npm install -D vitest
cd ..

# Python
pip install pytest
```

**Nota:** El sistema crea automáticamente `package.json` en `output/` si no existe.

4. **Configurar variables de entorno**

Crear archivo `.env` en la raíz del proyecto:

```env
# APIs requeridas
GEMINI_API_KEY=tu_clave_api_aqui

# SonarQube (opcional - para análisis avanzado)
SONARQUBE_URL=https://sonarcloud.io
SONARQUBE_TOKEN=tu_token_aqui
SONARQUBE_PROJECT_KEY=tu_proyecto_key

# 🔷 Azure DevOps (opcional - para integración con ADO)
AZURE_DEVOPS_ENABLED=false
AZURE_DEVOPS_ORG=tu-organizacion
AZURE_DEVOPS_PROJECT=tu-proyecto
AZURE_DEVOPS_PAT=tu-personal-access-token
AZURE_ITERATION_PATH=MiProyecto\\Sprint 1
AZURE_AREA_PATH=MiProyecto\\Backend
```

**Nota:** E2B ya no es requerido. El sistema usa vitest/pytest directamente.

**Nota:** Las credenciales de SonarQube son **opcionales**. El sistema funciona con análisis estático básico sin ellas.

Para configurar SonarQube, consulta: [`SONARQUBE_SETUP.md`](SONARQUBE_SETUP.md)

**🔷 Azure DevOps Integration**: Para habilitar la creación automática de PBIs:

- Consulta: [`AZURE_DEVOPS_QUICKSTART.md`](AZURE_DEVOPS_QUICKSTART.md) (5 minutos)
- Documentación completa: [`AZURE_DEVOPS_INTEGRATION.md`](AZURE_DEVOPS_INTEGRATION.md)

5. **Verificar configuración de SonarQube** (opcional)

```bash
python test_sonarqube_connection.py
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

````
START → Ingeniero Requisitos → Product Owner → Codificador → SonarQube Analyzer
           ↑                                        ↑               ↓
           |                                        |          ¿Calidad OK?
           |                                        ←──────── NO (max 2 intentos)
           |                                                      ↓
           |                                              Generador Unit Tests
           |                                                      ↓
           |                                              Ejecutor de Pruebas
           |                                                      ↓
           |                                                   ¿Pasa?
           |                                                      ↓
           |                                                 Stakeholder
           |                                                      ↓
           |                                                 ¿Validado?
           |                                                      ↓
           ←──────────────────────────────────────────────────  NO
                                                                 ↓
                                                                END
```        |                                                      ↓
           ←──────────────────────────────────────────────────  NO
                                                                 ↓
                                                                END
### Agentes

1. **Ingeniero de Requisitos**: Clarifica y refina requisitos
2. **Product Owner**: Formaliza especificaciones técnicas en JSON estructurado + 🔷 crea PBIs en Azure DevOps (opcional)
3. **Codificador Corrector**: Genera y corrige código Python/TypeScript
4. **Analizador SonarQube**: Verifica calidad del código (bugs, vulnerabilidades, code smells)
5. **Generador de Unit Tests**: Genera tests unitarios profesionales con vitest/pytest
6. **Ejecutor de Pruebas**: Ejecuta tests directamente con vitest/pytest y valida funcionalidad
7. **Stakeholder**: Valida cumplimiento de visión de negocio

### Bucles de Corrección

El sistema implementa tres bucles de corrección:

1. **Bucle de Calidad** (SonarQube → Codificador):
   - Detecta issues de calidad, seguridad y code smells
   - Máximo 2 intentos de corrección (configurable)
   - Criterios: 0 BLOCKER, máximo 2 CRITICAL

2. **Bucle de Depuración** (Probador → Codificador):
   - Corrige errores de ejecución
   - Máximo 3 intentos (configurable)

3. **Bucle de Validación** (Stakeholder → Ingeniero):
   - Reingeniería de requisitos si no cumple visión de negocio
   - Máximo 1 ciclo completo (configurable)

## 🛠️ Tecnologías

- **LangGraph**: Framework de grafos de agentes
- **Google Gemini**: Modelo LLM
- **Pydantic**: Validación de datos
- **Vitest**: Testing framework para TypeScript/JavaScript
- **Pytest**: Testing framework para Python
- **SonarQube MCP**: Análisis estático de calidad de código
- **🔷 Azure DevOps REST API**: Integración con Azure DevOps (opcional)
- **Python-dotenv**: Gestión de entorno

## 📝 Configuración

Editar `src/config/settings.py` para ajustar:
- `MAX_ATTEMPTS`: Máximo de ciclos completos (default: 1)
- `MAX_DEBUG_ATTEMPTS`: Máximo intentos de depuración (default: 3)
- `MAX_SONARQUBE_ATTEMPTS`: Máximo intentos de corrección de calidad (default: 2)
- `TEMPERATURE`: Temperatura del LLM (default: 0.1)
- `MAX_OUTPUT_TOKENS`: Tokens máximos de salida (default: 4000)

### Ejecución de Tests Moderna (Refactorizado)

El sistema ejecuta directamente tests unitarios generados usando frameworks estándar:

**Características:**
- ✅ **TypeScript**: Ejecución directa con `vitest` (sin E2B)
- ✅ **Python**: Ejecución directa con `pytest` (sin E2B)
- ✅ **Sin dependencias externas**: No requiere E2B Sandbox
- ✅ **Debugging local**: Tests ejecutables manualmente en `output/`
- ✅ **Performance mejorada**: ~3x más rápido que sandbox
- ✅ **Reportes profesionales**: Salida estándar con estadísticas detalladas
- ✅ **Estadísticas completas**: Total, pasados, fallidos para cada ejecución
- ✅ **Output limpio**: Sin códigos ANSI en archivos guardados

**Proceso:**
1. `generador_unit_tests.py` genera tests con sintaxis moderna:
   - TypeScript: `describe()`, `it()`, `test.each()`, `beforeEach()`, etc.
   - Python: `pytest` con fixtures y assertions
2. `ejecutor_pruebas.py` ejecuta tests directamente:
   - Cambia al directorio `output/` para imports relativos
   - Ejecuta `npx vitest run` o `pytest` según lenguaje
   - Parsea resultados y extrae estadísticas
3. Guarda reportes legibles en `4_probador_req{X}_debug{Y}_[PASSED|FAILED].txt`

**Mejoras de calidad:**
- Imports automáticos de funciones vitest/pytest necesarias
- Validación de instalación de vitest/pytest
- Mensajes de error específicos y accionables
- Manejo robusto de errores (FileNotFoundError, OSError, TimeoutExpired)

**Más información:** [`GUIA_NUEVO_EJECUTOR.md`](GUIA_NUEVO_EJECUTOR.md) | [`REFACTOR_EJECUTOR_PRUEBAS.md`](REFACTOR_EJECUTOR_PRUEBAS.md)

**Más información:** [`GUIA_NUEVO_EJECUTOR.md`](GUIA_NUEVO_EJECUTOR.md) | [`REFACTOR_EJECUTOR_PRUEBAS.md`](REFACTOR_EJECUTOR_PRUEBAS.md)

### Análisis de Calidad con SonarQube

El sistema integra SonarQube mediante Model Context Protocol (MCP) para:
- ✅ Detectar bugs potenciales
- ✅ Identificar vulnerabilidades de seguridad
- ✅ Encontrar code smells
- ✅ Verificar complejidad ciclomática
- ✅ Validar estándares de código

Los reportes de SonarQube se guardan en `output/` junto con instrucciones de corrección detalladas.

### 🔷 Integración con Azure DevOps (NUEVO)

El sistema ahora puede crear automáticamente **Product Backlog Items (PBIs)** en Azure DevOps durante la formalización de requisitos por el Product Owner.

**Características:**
- ✅ Creación automática de PBIs con descripción HTML enriquecida
- ✅ Estimación inteligente de Story Points (1, 2, 3, 5, 8, 13)
- ✅ Asignación automática a Iteration y Area Path
- ✅ Tags descriptivos (AI-Generated, Multiagente, Lenguaje)
- ✅ Criterios de aceptación detallados
- ✅ Trazabilidad completa con URLs en requisitos formales
- ✅ Modo degradado (funciona sin Azure DevOps si está deshabilitado)

**Quick Start:**
1. Ver guía rápida: [`AZURE_DEVOPS_QUICKSTART.md`](AZURE_DEVOPS_QUICKSTART.md) (5 minutos)
2. Configurar `.env` con credenciales de Azure DevOps
3. Ejecutar `python test_azure_devops_connection.py` para validar
4. El flujo normal creará PBIs automáticamente

**Documentación completa:** [`AZURE_DEVOPS_INTEGRATION.md`](AZURE_DEVOPS_INTEGRATION.md)

## 📄 Licencia

MIT License

## 👥 Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue primero para discutir los cambios propuestos.
````
