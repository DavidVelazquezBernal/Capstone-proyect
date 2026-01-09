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
│   │   ├── settings.py              # Variables de entorno y RetryConfig
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
│   │   ├── product_owner.py         # Agente 1: Formalización de requisitos
│   │   ├── developer_code.py        # Agente 2: Desarrollo y corrección de código
│   │   ├── sonar.py                 # Agente 3: Análisis de calidad con SonarQube
│   │   ├── developer_unit_tests.py  # Agente 4: Generación y ejecución de tests + PR completion
│   │   ├── developer2_reviewer.py   # Agente 5: Revisión de código y aprobación de PR
│   │   └── stakeholder.py           # Agente 6: Validación final de negocio
│   │
│   ├── llm/                         # Cliente LLM
│   │   ├── __init__.py
│   │   └── gemini_client.py         # Cliente Gemini
│   │
│   ├── utils/                       # Utilidades
│   │   ├── __init__.py
│   │   ├── logger.py                # Sistema de logging
│   │   └── file_manager.py          # Gestión de archivos
│   │
│   ├── services/                    # Servicios auxiliares
│   │   ├── __init__.py
│   │   ├── github_service.py        # Integración con GitHub
│   │   ├── azure_devops_service.py  # Servicio de Azure DevOps
│   │   └── sonarcloud_service.py    # Servicio de SonarCloud
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
E2B_API_KEY=tu_clave_e2b_aqui

# SonarQube (opcional - para análisis avanzado)
SONARQUBE_URL=https://sonarcloud.io
SONARQUBE_TOKEN=tu_token_aqui
SONARQUBE_PROJECT_KEY=tu_proyecto_key

# SonarCloud (opcional - para análisis en la nube)
SONARCLOUD_ENABLED=false
SONARCLOUD_TOKEN=tu_token_sonarcloud
SONARCLOUD_ORGANIZATION=tu-organizacion
SONARCLOUD_PROJECT_KEY=tu_proyecto_key

# 🔷 Azure DevOps (opcional - para integración con ADO)
AZURE_DEVOPS_ENABLED=false
AZURE_DEVOPS_ORG=tu-organizacion
AZURE_DEVOPS_PROJECT=tu-proyecto
AZURE_DEVOPS_PAT=tu-personal-access-token
AZURE_ITERATION_PATH=MiProyecto\\Sprint 1
AZURE_AREA_PATH=MiProyecto\\Backend
AZURE_ASSIGNED_TO=

# GitHub (opcional - para integración con repositorio)
GITHUB_ENABLED=false
GITHUB_OWNER=tu-usuario
GITHUB_REPO=tu-repositorio
GITHUB_TOKEN=tu-token-github
GITHUB_REVIEWER_TOKEN=token-revisor-opcional
GITHUB_BASE_BRANCH=main
GITHUB_REPO_PATH=C:/ruta/al/repo/local

# Logging
LOG_LEVEL=INFO
LOG_TO_FILE=true
```

**Nota:** Las credenciales de SonarQube son **opcionales**. El sistema funciona con análisis estático básico sin ellas.

**🔷 Azure DevOps Integration**: Para habilitar la creación automática de PBIs y Tasks:

- Configurar variables en `.env` con credenciales de Azure DevOps
- Habilitar `AZURE_DEVOPS_ENABLED=true`
- El sistema creará automáticamente PBIs y Tasks relacionadas
- Adjuntará código final y tests a los work items

**🔗 GitHub Integration**: Para integración completa con repositorio remoto:

- Configurar variables `GITHUB_*` en `.env`
- `GITHUB_TOKEN`: Token principal para crear branches, commits y PRs
- `GITHUB_REVIEWER_TOKEN`: Token opcional de otra cuenta para aprobar PRs (evita error 422)
- `GITHUB_REPO_PATH`: Ruta local al repositorio clonado
- El sistema automáticamente:
  - Crea branches sanitizados (sin caracteres inválidos)
  - Hace commits con formato estructurado (ver formato abajo)
  - Crea Pull Requests
  - Aprueba PRs (con token revisor)
  - Hace squash merge tras validación
  - Limpia branches remotos y locales tras merge

**Formato de commits:**

```
# Developer commit
feat: Add {nombre_archivo} implementation
{nombre_archivo}
Attempt: req{X}_debug{Y}_sq{Z}

Generated by AI Developer Agent

# Testing commit
test: Add unit tests for {nombre_archivo}
{test_filename}
Total: {N} tests passed

Generated by AI Testing Agent
```

## 💻 Uso

### Ejecución básica

```bash
python src/main.py
```

### Uso programático

```python
from src.main import run_development_workflow
from src.config.settings import RetryConfig

# Ejemplo básico (usa configuración por defecto)
prompt = "Crea una función para calcular el factorial de un número"
final_state = run_development_workflow(prompt)

# Ejemplo con configuración personalizada de reintentos
retry_config = RetryConfig(
    max_attempts=3,              # Máximo de ciclos completos (Stakeholder loop)
    max_debug_attempts=5,        # Máximo de intentos Testing-Desarrollador
    max_sonarqube_attempts=2,    # Máximo de intentos SonarQube-Desarrollador
    max_revisor_attempts=3       # Máximo de intentos de revisión de código
)
final_state = run_development_workflow(prompt, retry_config=retry_config)

# Ejemplo TypeScript con configuración por defecto
prompt_ts = "Quiero una función en TypeScript para sumar un array de números"
final_state_ts = run_development_workflow(prompt_ts)
```

### Configuración de Reintentos (RetryConfig)

La clase `RetryConfig` centraliza toda la configuración de límites de reintentos:

```python
from src.config.settings import RetryConfig

# Crear configuración desde valores por defecto de settings.py
config = RetryConfig.from_settings()

# Crear configuración personalizada
config = RetryConfig(
    max_attempts=2,              # Ciclos completos antes de fallo
    max_debug_attempts=4,        # Intentos en bucle Testing-Desarrollador
    max_sonarqube_attempts=3,    # Intentos en bucle SonarQube-Desarrollador
    max_revisor_attempts=2       # Intentos de revisión de código
)

# Convertir a diccionario para inicializar estado
state_dict = config.to_state_dict()
# Retorna: {
#   'max_attempts': 2, 'attempt_count': 0,
#   'max_debug_attempts': 4, 'debug_attempt_count': 0,
#   'max_sonarqube_attempts': 3, 'sonarqube_attempt_count': 0,
#   'max_revisor_attempts': 2, 'revisor_attempt_count': 0
# }
```

**Valores por defecto** (definidos en `settings.py`):
- `MAX_ATTEMPTS = 1` - Ciclos completos
- `MAX_DEBUG_ATTEMPTS = 3` - Testing-Desarrollador
- `MAX_SONARQUBE_ATTEMPTS = 3` - SonarQube-Desarrollador
- `MAX_REVISOR_ATTEMPTS = 2` - Revisión de código

### Salida del código generado

El sistema detecta automáticamente el lenguaje del código generado:

- **Python**: Guarda como `codigo_final.py` en el directorio `output/`
- **TypeScript**: Guarda como `codigo_final.ts` en el directorio `output/`

El código se limpia automáticamente de marcadores markdown (` ```python `, ` ```typescript `, ` ``` `).

## 🔄 Flujo de Trabajo

```
START → ProductOwner → Developer-Code → Sonar
           ↑                ↑               ↓
           |                |          ¿Calidad OK?
           |                ←──────── NO (max 3 intentos)
           |                                ↓
           |                      Developer-UnitTests
           |                                ↓
           |                             ¿Pasa?
           |                ←──────── NO (max 3 intentos)
           |                                ↓
           |                      Developer2-Reviewer
           |                                ↓
           |                           ¿Aprobado?
           |                ←──────── NO (max 3 intentos)
           |                                ↓
           |                    Developer-CompletePR
           |                                ↓
           |                      Squash & Merge PR
           |                      Cleanup branches
           |                                ↓
           |                           Stakeholder
           |                                ↓
           |                           ¿Validado?
           ←──────────────────────────── NO
                                           ↓
                                          END
```

### Agentes

1. **ProductOwner**: Formaliza especificaciones técnicas en JSON estructurado + 🔷 crea PBIs en Azure DevOps (opcional)
2. **Developer-Code**: Genera y corrige código Python/TypeScript + 🐙 crea branch y commit en GitHub (opcional) + 🔷 crea Tasks en Azure DevOps (opcional)
3. **Sonar**: Verifica calidad del código con SonarQube/SonarCloud (bugs, vulnerabilidades, code smells)
4. **Developer-UnitTests**: Genera y ejecuta tests unitarios con vitest/pytest + 🐙 pushea tests a GitHub (opcional)
5. **Developer2-Reviewer**: Revisa código con LLM, evalúa calidad y aprueba/rechaza PR + 🐙 aprueba PR en GitHub (opcional)
6. **Developer-CompletePR**: Hace squash merge de PR + 🐙 limpia branches remotos y locales (opcional)
7. **Stakeholder**: Valida cumplimiento de visión de negocio + 📎 adjunta código final a Azure DevOps (opcional)

### Bucles de Corrección

El sistema implementa tres bucles de corrección:

1. **Bucle de Calidad** (SonarQube → Desarrollador):
   - Detecta issues de calidad, seguridad y code smells
   - Máximo 3 intentos de corrección (configurable)
   - Criterios: 0 BLOCKER, máximo 2 CRITICAL

2. **Bucle de Depuración** (Testing → Desarrollador):
   - Corrige errores de ejecución
   - Máximo 3 intentos (configurable)

3. **Bucle de Revisión** (Developer2-Reviewer → Developer-Code):
   - Corrige problemas de calidad detectados por revisión de código
   - Máximo 3 intentos (configurable)

4. **Bucle de Validación** (Stakeholder → ProductOwner):
   - Reingeniería de requisitos si no cumple visión de negocio
   - Máximo 1 ciclo completo (configurable)

## 🛠️ Tecnologías

- **LangGraph**: Framework de grafos de agentes
- **Google Gemini**: Modelo LLM
- **Pydantic**: Validación de datos
- **Vitest**: Testing framework para TypeScript/JavaScript
- **Pytest**: Testing framework para Python
- **SonarQube MCP**: Análisis estático de calidad de código
- **SonarCloud**: Análisis de calidad en la nube (opcional)
- **🔷 Azure DevOps REST API**: Integración con Azure DevOps (opcional)
- **🐙 PyGithub**: Integración con GitHub API (opcional)
- **Python-dotenv**: Gestión de entorno

## 📝 Configuración

Editar `src/config/settings.py` para ajustar:
- `MAX_ATTEMPTS`: Máximo de ciclos completos (default: 3)
- `MAX_DEBUG_ATTEMPTS`: Máximo intentos de depuración (default: 3)
- `MAX_SONARQUBE_ATTEMPTS`: Máximo intentos de corrección de calidad (default: 3)
- `MAX_REVISOR_ATTEMPTS`: Máximo intentos de revisión de código (default: 3)
- `TEMPERATURE`: Temperatura del LLM (default: 0.1)
- `MAX_OUTPUT_TOKENS`: Tokens máximos de salida (default: 4000)
- `LOG_LEVEL`: Nivel de logging (default: INFO)
- `LOG_TO_FILE`: Guardar logs en archivo (default: true)

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
- ✅ Creación automática de Tasks relacionadas (Implementación + Testing)
- ✅ Adjuntos automáticos de código final y tests a work items
- ✅ Estimación inteligente de Story Points (1, 2, 3, 5, 8, 13)
- ✅ Asignación automática a Iteration y Area Path
- ✅ Tags descriptivos (AI-Generated, Multiagente, Lenguaje)
- ✅ Criterios de aceptación detallados
- ✅ Trazabilidad completa con URLs en requisitos formales
- ✅ Modo degradado (funciona sin Azure DevOps si está deshabilitado)

**Configuración:**
1. Configurar `.env` con credenciales de Azure DevOps
2. Habilitar `AZURE_DEVOPS_ENABLED=true`
3. El flujo normal creará PBIs, Tasks y adjuntará archivos automáticamente

**Documentación completa:** [`IMPLEMENTACION_ADJUNTOS_AZURE.md`](IMPLEMENTACION_ADJUNTOS_AZURE.md)

## 📄 Licencia

MIT License

## 👥 Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue primero para discutir los cambios propuestos.
````
