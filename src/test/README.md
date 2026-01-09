# Tests Unitarios - Agentes AI

Este directorio contiene los tests unitarios para todos los agentes del sistema multi-agente.

## Estructura

```
test/
├── conftest.py                          # Configuración global de pytest y fixtures
├── __init__.py
├── test_product_owner/                  # Tests del Product Owner
│   ├── __init__.py
│   └── test_product_owner.py
├── test_developer_code/                 # Tests del Developer-Code
│   ├── __init__.py
│   └── test_developer_code.py
├── test_developer2_reviewer/            # Tests del Developer2-Reviewer
│   ├── __init__.py
│   └── test_developer2_reviewer.py
├── test_developer_unit_tests/           # Tests del Developer-UnitTests
│   ├── __init__.py
│   └── test_developer_unit_tests.py
├── test_sonar/                          # Tests del Analizador Sonar
│   ├── __init__.py
│   └── test_sonar.py
└── test_stakeholder/                    # Tests del Stakeholder
    ├── __init__.py
    └── test_stakeholder.py
```

## Ejecutar Tests

### Todos los tests
```bash
pytest src/test/
```

### Tests de un agente específico
```bash
pytest src/test/test_product_owner/
pytest src/test/test_developer_code/
pytest src/test/test_developer2_reviewer/
pytest src/test/test_developer_unit_tests/
pytest src/test/test_sonar/
pytest src/test/test_stakeholder/
```

### Con cobertura
```bash
pytest src/test/ --cov=src/agents --cov-report=html
```

### Con verbose
```bash
pytest src/test/ -v
```

### Tests específicos
```bash
pytest src/test/test_product_owner/test_product_owner.py::TestProductOwnerNode::test_product_owner_procesa_requisitos_exitosamente
```

## Fixtures Disponibles

Los fixtures están definidos en `conftest.py`:

- **mock_state**: Estado inicial del agente con valores por defecto
- **mock_gemini_client**: Mock del cliente LLM Gemini
- **mock_azure_service**: Mock del servicio Azure DevOps
- **mock_github_service**: Mock del servicio GitHub
- **mock_file_utils**: Mock de utilidades de archivos
- **mock_settings**: Mock de configuración con servicios deshabilitados

## Cobertura de Tests

### Product Owner (test_product_owner.py)
- ✅ Procesamiento exitoso de requisitos
- ✅ Incremento de contador de intentos
- ✅ Procesamiento de feedback del stakeholder
- ✅ Limpieza de variables de GitHub
- ✅ Manejo de errores de parsing
- ✅ Integración con Azure DevOps
- ✅ Uso de prompt templates

### Developer-Code (test_developer_code.py)
- ✅ Generación exitosa de código
- ✅ Corrección de errores de traceback
- ✅ Corrección de issues de Sonar
- ✅ Detección de lenguaje
- ✅ Guardado de archivos con nombres correctos
- ✅ Creación de Tasks en Azure DevOps
- ✅ Creación de branches en GitHub
- ✅ Uso de prompt templates

### Developer2-Reviewer (test_developer2_reviewer.py)
- ✅ Omisión de revisión cuando GitHub está deshabilitado
- ✅ Aprobación de código de calidad aceptable
- ✅ Rechazo de código de baja calidad
- ✅ Incremento de contador en rechazo
- ✅ Manejo de errores de parsing JSON
- ✅ Limpieza de markdown en respuestas
- ✅ Guardado de archivos de resultado

### Developer-UnitTests (test_developer_unit_tests.py)
- ✅ Generación exitosa de tests
- ✅ Detección de lenguaje TypeScript/Python
- ✅ Actualización de Azure Task a "In Progress"
- ✅ Incremento de debug count en fallo
- ✅ Reset de debug count en éxito
- ✅ Creación de PR en GitHub
- ✅ Merge de PR con precondiciones
- ✅ Eliminación de branch después de merge
- ✅ Funciones helper (limpiar ANSI, postprocesar tests, detectar fallos)

### Sonar (test_sonar.py)
- ✅ Omisión de análisis cuando está deshabilitado
- ✅ Aprobación de código sin issues críticos
- ✅ Rechazo de código con blockers
- ✅ Incremento de contador en rechazo
- ✅ Actualización de Azure Task a "In Progress"
- ✅ Comentarios de aprobación en Azure
- ✅ Uso de SonarCloud con branch
- ✅ Fallback a análisis local
- ✅ Guardado de reportes

### Stakeholder (test_stakeholder.py)
- ✅ Validación exitosa de código
- ✅ Rechazo de código con feedback
- ✅ Fallo al exceder intentos máximos
- ✅ Guardado de archivos (validado/rechazado)
- ✅ Uso de prompt templates
- ✅ Actualización de Azure a "Done" en validación
- ✅ Generación de Release Note
- ✅ Extracción de feedback con regex
- ✅ Validación en primer y último intento

## Dependencias

```bash
pip install pytest pytest-cov pytest-mock
```

## Notas

- Todos los tests usan mocks para evitar llamadas reales a servicios externos (LLM, Azure DevOps, GitHub, SonarCloud)
- Los tests están diseñados para ser independientes y ejecutarse en cualquier orden
- Se recomienda ejecutar los tests antes de cada commit
- La cobertura objetivo es >80% para cada agente
