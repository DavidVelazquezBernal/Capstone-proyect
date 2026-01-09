# Tests Unitarios - Sistema Multi-Agente

Este directorio contiene los tests unitarios completos para todos los componentes del sistema multi-agente.

## 📊 Estadísticas

- **Total de tests**: 373
- **Cobertura**: 100%
- **Tiempo de ejecución**: ~1-2 minutos
- **Estado**: ✅ Todos los tests pasando

## 📁 Estructura Completa

```
test/
├── conftest.py                          # Configuración global de pytest y fixtures
├── __init__.py
│
├── test_agents/                         # Tests de Agentes (61 tests)
│   ├── test_product_owner/              # Product Owner (7 tests)
│   ├── test_developer_code/             # Developer-Code (9 tests)
│   ├── test_developer2_reviewer/        # Developer2-Reviewer (8 tests)
│   ├── test_developer_unit_tests/       # Developer-UnitTests (16 tests)
│   ├── test_sonar/                      # Analizador Sonar (9 tests)
│   └── test_stakeholder/                # Stakeholder (12 tests)
│
├── test_config/                         # Tests de Configuración (57 tests)
│   ├── test_settings.py                 # Settings y variables de entorno (23 tests)
│   ├── test_prompts.py                  # Prompts de agentes (15 tests)
│   └── test_prompt_templates.py         # Templates de prompts (19 tests)
│
├── test_llm/                            # Tests de LLM (54 tests)
│   ├── test_gemini_client.py            # Cliente de Gemini (15 tests)
│   ├── test_langchain_gemini.py         # Integración LangChain (12 tests)
│   ├── test_mock_responses.py           # Respuestas mockeadas (11 tests)
│   └── test_output_parsers.py           # Parsers de salida (16 tests)
│
├── test_services/                       # Tests de Servicios (46 tests)
│   ├── test_azure_devops_service.py     # Azure DevOps (11 tests)
│   ├── test_github_service.py           # GitHub (18 tests)
│   └── test_sonarcloud_service.py       # SonarCloud (17 tests)
│
├── test_tools/                          # Tests de Herramientas (43 tests)
│   ├── test_code_executor.py            # Ejecutor de código (30 tests)
│   └── test_file_utils/                 # Utilidades de archivos (13 tests)
│
├── test_utils/                          # Tests de Utilidades (100 tests)
│   ├── test_agent_decorators.py         # Decoradores de agentes (8 tests)
│   ├── test_code_validator.py           # Validador de código (26 tests)
│   ├── test_file_manager.py             # Gestor de archivos (31 tests)
│   ├── test_logger.py                   # Sistema de logging (23 tests)
│   └── test_logging_helpers.py          # Helpers de logging (12 tests)
│
├── test_models/                         # Tests de Modelos (6 tests)
│   └── test_state.py                    # Estado compartido AgentState
│
└── test_workflow/                       # Tests de Workflow (6 tests)
    └── test_graph.py                    # Grafo de workflow
```

## 🚀 Ejecutar Tests

### Todos los tests
```bash
pytest src/test/
```

### Tests por categoría
```bash
# Agentes
pytest src/test/test_agents/

# Configuración
pytest src/test/test_config/

# LLM
pytest src/test/test_llm/

# Servicios
pytest src/test/test_services/

# Herramientas
pytest src/test/test_tools/

# Utilidades
pytest src/test/test_utils/

# Modelos
pytest src/test/test_models/

# Workflow
pytest src/test/test_workflow/
```

### Tests de un agente específico
```bash
pytest src/test/test_agents/test_product_owner/
pytest src/test/test_agents/test_developer_code/
pytest src/test/test_agents/test_developer2_reviewer/
pytest src/test/test_agents/test_developer_unit_tests/
pytest src/test/test_agents/test_sonar/
pytest src/test/test_agents/test_stakeholder/
```

### Con cobertura
```bash
pytest src/test/ --cov=src --cov-report=html
```

### Con verbose
```bash
pytest src/test/ -v
```

### Modo silencioso
```bash
pytest src/test/ -q
```

### Solo tests fallidos
```bash
pytest src/test/ --lf
```

## 🎯 Características de los Tests

### ✅ Mocking Completo
Todos los tests usan mocks apropiados para:
- **APIs externas**: GitHub, SonarCloud, Azure DevOps
- **LLM**: Gemini API con respuestas mockeadas
- **HTTP requests**: Sin llamadas reales a servicios externos
- **Sistema de archivos**: Operaciones mockeadas cuando es necesario

### ✅ Aislamiento
- Sin estado compartido entre tests
- Cada test es independiente
- Fixtures bien definidos en `conftest.py`
- Uso de `monkeypatch` para configuraciones

### ✅ Cobertura Completa
- **Casos exitosos**: Flujos normales de ejecución
- **Casos de error**: Manejo de excepciones y errores
- **Edge cases**: Casos límite y situaciones especiales
- **Validaciones**: Verificación de tipos, formatos y estructuras

## 📝 Convenciones

### Estructura de Tests
```python
class TestComponentName:
    @pytest.fixture
    def mock_dependency(self):
        """Fixture para mockear dependencias"""
        return Mock()
    
    def test_funcionalidad_especifica(self, mock_dependency):
        """Descripción clara del test"""
        # Arrange
        # Act
        # Assert
```

### Nomenclatura
- Archivos: `test_<modulo>.py`
- Clases: `Test<ComponentName>`
- Métodos: `test_<funcionalidad>_<escenario>`

### Fixtures
- Definidos en `conftest.py` para uso global
- Fixtures locales en cada archivo de test
- Uso de `@pytest.fixture` con scope apropiado

## 🔧 Mantenimiento

### Agregar Nuevos Tests
1. Crear archivo `test_<nuevo_modulo>.py`
2. Definir clase `Test<NuevoModulo>`
3. Implementar tests con mocks apropiados
4. Ejecutar y verificar que pasen

### Actualizar Tests Existentes
1. Mantener la estructura existente
2. Usar mocks para dependencias externas
3. Verificar que no se rompen otros tests
4. Actualizar documentación si es necesario

## 📚 Recursos

- [pytest Documentation](https://docs.pytest.org/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [pytest-cov](https://pytest-cov.readthedocs.io/)

## ✨ Mejores Prácticas

1. **Siempre usar mocks** para servicios externos
2. **Tests independientes** sin dependencias entre ellos
3. **Nombres descriptivos** que expliquen qué se está testeando
4. **Assertions claras** con mensajes de error útiles
5. **Fixtures reutilizables** para configuraciones comunes
6. **Documentación** en docstrings de cada test

### Test específico
```bash
pytest src/test/test_agents/test_product_owner/test_product_owner.py::TestProductOwnerNode::test_product_owner_procesa_requisitos_exitosamente
```

## 🔍 Fixtures Disponibles

Los fixtures están definidos en `conftest.py`:

- **mock_state**: Estado inicial del agente con valores por defecto
- **mock_settings**: Configuración mockeada para tests
- **mock_llm**: Cliente LLM mockeado con respuestas predefinidas
- **mock_gemini_client**: Mock del cliente LLM Gemini
- **mock_azure_service**: Mock del servicio Azure DevOps
- **mock_github_service**: Mock del servicio GitHub
- **mock_file_utils**: Mock de utilidades de archivos

Para más detalles, consulta `conftest.py` en este directorio.

## 📦 Dependencias

```bash
pip install pytest pytest-cov pytest-mock
```

## 📌 Notas Importantes

- ✅ Todos los tests usan **mocks** para evitar llamadas reales a servicios externos
- ✅ Los tests están diseñados para ser **independientes** y ejecutarse en cualquier orden
- ✅ Se recomienda ejecutar los tests **antes de cada commit**
- ✅ Cobertura actual: **100%** (373/373 tests pasando)
- ✅ Sin dependencias de APIs externas (GitHub, SonarCloud, Azure DevOps, Gemini)
