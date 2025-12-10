# 🔗 Guía: Work Items Relacionados en Azure DevOps

**Fecha:** 10 de diciembre de 2025  
**Versión:** 3.0 ⭐ Adjuntos Automáticos  
**Feature:** Asociación de Tasks/Bugs a PBI Padre + Adjuntos de Archivos

---

## 📋 Resumen

El sistema ahora guarda el **ID del PBI creado** en el estado compartido (`state['azure_pbi_id']`) para permitir la creación automática de work items relacionados (Tasks, Bugs) que se asocian jerárquicamente al PBI padre.

**Creación Automática de Tasks:**

- ✅ El **Codificador** crea automáticamente 2 Tasks asociadas al PBI:
  1. **Task de Implementación** - Para revisar el código generado
  2. **Task de Testing** - Para los unit tests que se generarán

---

## 🎯 Casos de Uso

### 1. **Flujo Automático** ⭐ NUEVO

```
Requirements Manager → Crea PBI #2020946
                    ↓
         state['azure_pbi_id'] = 2020946
                    ↓
Codificador → Genera código
           → Crea Task #2020950 (Implementación) asociada al PBI
           → Crea Task #2020951 (Testing) asociada al PBI
                    ↓
Generador Tests → Genera unit tests
               → Actualiza Task #2020951 con info de tests
                    ↓
Ejecutor Pruebas → Si falla: Crea Bug asociado al PBI
```

### 2. **Jerarquía de Work Items**

```
PBI #2020946: [AI-Generated] Clase Calculator
  ├── Task #2020950: [AI-Generated] Implementar Calculator ← AUTO-CREADA
  ├── Task #2020951: [AI-Generated] Crear unit tests para Calculator ← AUTO-CREADA
  └── Bug #2020952: División por cero no controlada
```

### 3. **Trazabilidad**

- Cada work item se vincula al PBI padre
- Facilita seguimiento de progreso
- Permite visualización en Azure Boards

---

## 🏗️ Arquitectura

### Estado Compartido

**Ubicación:** `src/models/state.py`

```python
class AgentState(TypedDict):
    # ... otros campos ...

    # Azure DevOps Integration
    azure_pbi_id: int | None  # ID del PBI padre creado
```

**Inicialización:** `src/main.py`

```python
initial_state = {
    # ... otros campos ...
    "azure_pbi_id": None  # Se actualiza cuando se crea el PBI
}
```

### Flujo de Datos

```
1. Requirements Manager
   ├── Crea PBI en Azure DevOps
   ├── state['azure_pbi_id'] = pbi['id']  ← GUARDADO
   └── Log: "💾 PBI ID guardado para asociar work items posteriores"

2. Codificador (Primera ejecución) ⭐ AUTO-CREACIÓN
   ├── Genera código según requisitos formales
   ├── Lee parent_id = state['azure_pbi_id']
   ├── Crea Task #1: "Implementar {nombre_funcion}" (parent_id)
   ├── Crea Task #2: "Crear unit tests para {nombre_funcion}" (parent_id)
   └── Log: "🎯 2 Tasks creadas y asociadas al PBI #{pbi_id}"

3. Otros Agentes (Opcional)
   ├── Ejecutor Pruebas: Si fallan tests → Crea Bug asociado
   ├── Analizador SonarQube: Si issues críticos → Crea Bug asociado
   └── Azure DevOps establece relación jerárquica automáticamente
```

---

## 🔧 API del Cliente Azure DevOps

### Método: `create_task()`

**Firma:**

```python
def create_task(
    self,
    title: str,
    description: str,
    parent_id: Optional[int] = None,  # ← ID del PBI padre
    assigned_to: Optional[str] = None,
    remaining_work: Optional[float] = None,
    tags: Optional[List[str]] = None
) -> Optional[Dict[str, Any]]
```

**Ejemplo de Uso:**

```python
from tools.azure_devops_integration import AzureDevOpsClient

client = AzureDevOpsClient()

# Obtener PBI padre del estado
parent_pbi_id = state['azure_pbi_id']  # Ej: 2020946

# Crear Task asociada
task = client.create_task(
    title="[AI-Generated] Implementar validación de entrada",
    description="<p>Validar parámetros de entrada antes de procesarlos</p>",
    parent_id=parent_pbi_id,  # ← Asocia al PBI
    remaining_work=2.5,
    tags=["AI-Generated", "Implementation"]
)

# task['id'] → ID de la Task creada (Ej: 2020950)
```

### Método: `create_bug()`

**Firma:**

```python
def create_bug(
    self,
    title: str,
    repro_steps: str,
    parent_id: Optional[int] = None,  # ← ID del PBI padre
    severity: str = "3 - Medium",
    priority: int = 2,
    tags: Optional[List[str]] = None
) -> Optional[Dict[str, Any]]
```

**Ejemplo de Uso:**

```python
# Crear Bug asociado al PBI
bug = client.create_bug(
    title="[AI-Generated] Manejo incorrecto de entrada nula",
    repro_steps="""
        <h3>Pasos</h3>
        <ol>
            <li>Llamar función con null</li>
            <li>Observar error</li>
        </ol>
    """,
    parent_id=state['azure_pbi_id'],  # ← Asocia al PBI
    severity="2 - High",
    priority=1,
    tags=["AI-Generated", "Bug", "Error-Handling"]
)
```

---

## 🤖 Creación Automática de Tasks por el Codificador

### Comportamiento del Agente Codificador

**Ubicación:** `src/agents/codificador_corrector.py`

El agente **Codificador** ahora crea automáticamente 2 Tasks en Azure DevOps cuando:

- ✅ Azure DevOps está habilitado (`AZURE_DEVOPS_ENABLED=true`)
- ✅ Existe un PBI padre (`state['azure_pbi_id']` no es None)
- ✅ Es la primera generación de código (`debug_attempt_count == 0` y `sonarqube_attempt_count == 0`)

### Tasks Creadas Automáticamente

#### 1️⃣ Task de Implementación

**Título:** `[AI-Generated] Implementar {nombre_funcion}`

**Contenido:**

- Objetivo funcional del código
- Especificaciones técnicas (lenguaje, función, archivo)
- Checklist de tareas (revisar implementación, validar lógica, verificar manejo de errores)
- Entregables esperados
- Remaining Work: 2.0 horas

**Tags:** `AI-Generated`, `Implementation`, `{lenguaje}`, `Auto-Created`

#### 2️⃣ Task de Testing

**Título:** `[AI-Generated] Crear unit tests para {nombre_funcion}`

**Contenido:**

- Framework de testing (vitest para TypeScript, pytest para Python)
- Objetivo de cobertura (>80%)
- Casos de prueba requeridos (happy path, edge cases, error handling)
- Criterios de aceptación (todos los tests pasan, cobertura >80%)
- Entregables esperados
- Remaining Work: 1.5 horas

**Tags:** `AI-Generated`, `Testing`, `Unit-Tests`, `{lenguaje}`, `Auto-Created`

### Ejemplo de Log del Codificador

```
17:45:30 | INFO | 🔷 Creando Tasks en Azure DevOps para implementación y testing...
17:45:31 | INFO | ✅ Task de Implementación creada: #2020950
17:45:31 | INFO |    📋 [AI-Generated] Implementar Calculator
17:45:32 | INFO | ✅ Task de Testing creada: #2020951
17:45:32 | INFO |    🧪 [AI-Generated] Crear unit tests para Calculator
17:45:32 | INFO | 🎯 2 Tasks creadas y asociadas al PBI #2020946
```

### Ventajas de la Creación Automática

- ✅ **Trazabilidad completa** desde el requisito hasta el código
- ✅ **Visibilidad inmediata** del trabajo realizado en Azure Boards
- ✅ **Sin intervención manual** - El workflow crea todo automáticamente
- ✅ **Estimación incluida** - Remaining Work pre-calculado (2h + 1.5h = 3.5h)
- ✅ **Documentación rica** - Descripciones HTML detalladas
- ✅ **Tagging consistente** - Fácil filtrado y búsqueda

---

## 💡 Ejemplo Completo: Integración en Agente

### Escenario: El Ejecutor de Pruebas detecta un bug

**Ubicación:** `src/agents/ejecutor_pruebas.py`

```python
def ejecutor_pruebas_node(state: AgentState) -> AgentState:
    """
    Ejecuta pruebas y crea Bug en Azure DevOps si fallan.
    """
    # ... ejecutar pruebas ...

    if not pruebas_pasaron:
        # Crear Bug en Azure DevOps si está habilitado
        if settings.AZURE_DEVOPS_ENABLED and state['azure_pbi_id']:
            try:
                azure_client = AzureDevOpsClient()

                bug = azure_client.create_bug(
                    title=f"[AI-Generated] Test fallido: {nombre_test}",
                    repro_steps=f"""
                        <h3>Test Fallido</h3>
                        <pre>{traceback_error}</pre>

                        <h3>Código</h3>
                        <pre>{codigo_generado}</pre>
                    """,
                    parent_id=state['azure_pbi_id'],  # ← Asocia al PBI
                    severity="3 - Medium",
                    priority=2,
                    tags=["AI-Generated", "Test-Failure", "Auto-Detected"]
                )

                if bug:
                    logger.info(f"🐛 Bug #{bug['id']} creado y asociado al PBI #{state['azure_pbi_id']}")

            except Exception as e:
                logger.warning(f"⚠️ No se pudo crear Bug en Azure: {e}")

    return state
```

---

## 🧪 Script de Prueba

**Ubicación:** `example_create_work_items.py`

**Ejecutar:**

```bash
python example_create_work_items.py
```

**Funcionalidad:**

1. Pide el ID del PBI padre (o usa el último creado)
2. Crea 2 Tasks asociadas:
   - Implementación de lógica
   - Creación de unit tests
3. Crea 1 Bug asociado:
   - Error de división por cero
4. Muestra resumen con URLs

**Salida Esperada:**

```
📋 EJEMPLO: Creación de Work Items Asociados a PBI Padre
🔌 Verificando conexión con Azure DevOps...
✅ Conexión exitosa

📝 Ingresa el ID del PBI padre: 2020946
✅ Se asociarán los work items al PBI #2020946

🔧 Creando Task: Implementar lógica de negocio
✅ Task creada: #2020950
🔗 Asociada al PBI #2020946

🧪 Creando Task: Crear unit tests
✅ Task creada: #2020951
🔗 Asociada al PBI #2020946

🐛 Creando Bug: División por cero no controlada
✅ Bug creado: #2020952
🔗 Asociado al PBI #2020946

📊 RESUMEN
✅ PBI Padre: #2020946
✅ Task #1 (Implementación): #2020950
✅ Task #2 (Testing): #2020951
✅ Bug #1 (División por cero): #2020952
```

---

## 🔍 Verificación en Azure DevOps

### Ver Jerarquía en Azure Boards

1. **Ir a Azure DevOps:**

   ```
   https://dev.azure.com/cegid/PeopleNet/_workitems/edit/2020946
   ```

2. **Ver Work Items Relacionados:**

   - Pestaña "Links" o "Related Work"
   - Sección "Child" muestra Tasks y Bugs asociados

3. **Vista de Backlog:**
   - Los work items hijos aparecen indentados bajo el PBI padre
   - Permite colapsar/expandir jerarquía

### Queries WIQL

**Query: Obtener todos los hijos de un PBI**

```sql
SELECT
    [System.Id],
    [System.Title],
    [System.WorkItemType]
FROM WorkItemLinks
WHERE
    [Source].[System.Id] = 2020946  -- PBI Padre
    AND [System.Links.LinkType] = 'System.LinkTypes.Hierarchy-Forward'
```

---

## 📊 Relaciones en Azure DevOps

### Tipos de Relaciones

| Tipo                | Descripción              | Uso         |
| ------------------- | ------------------------ | ----------- |
| `Hierarchy-Reverse` | Este item es hijo de...  | Task → PBI  |
| `Hierarchy-Forward` | Este item es padre de... | PBI → Task  |
| `Related`           | Relacionado con...       | Bug ↔ Task  |
| `Dependency`        | Depende de...            | Task → Task |

### Estructura JSON de Relación

**Al crear work item hijo:**

```json
{
  "op": "add",
  "path": "/relations/-",
  "value": {
    "rel": "System.LinkTypes.Hierarchy-Reverse",
    "url": "https://dev.azure.com/cegid/_apis/wit/workItems/2020946"
  }
}
```

**Interpretación:**

- "Este work item (Task) es hijo de (Hierarchy-Reverse) el work item 2020946 (PBI)"

---

## ⚙️ Configuración

### Variables de Entorno (src/.env)

```env
# Azure DevOps
AZURE_DEVOPS_ENABLED=true
AZURE_DEVOPS_ORG=cegid
AZURE_DEVOPS_PROJECT=PeopleNet
AZURE_DEVOPS_PAT=tu-personal-access-token
AZURE_ITERATION_PATH=PeopleNet\Framework\2026Q1\Settings\Sprint 149 - Start Q12026
AZURE_AREA_PATH=PeopleNet\P280_0 Framework\[FRM] Settings\[FRM] Pop2
```

### Permisos del PAT

El Personal Access Token debe tener:

- ✅ **Work Items (Read, write, & manage)** - Para crear y vincular work items
- ✅ **Project and Team (Read)** - Para acceder a información del proyecto

---

## 🔒 Seguridad y Validación

### Validaciones Implementadas

1. **Verificar PBI existe:**

   ```python
   if state['azure_pbi_id']:
       # Verificar que el PBI existe antes de asociar
       pbi = azure_client.get_work_item(state['azure_pbi_id'])
       if pbi:
           # Crear work item asociado
   ```

2. **Manejo de Errores:**

   - Si la asociación falla, el work item se crea sin padre
   - Se registra el error en logs pero no bloquea el flujo

3. **Rollback en caso de fallo:**
   - Los work items creados permanecen aunque falle la asociación
   - Se pueden asociar manualmente después

---

## 📚 Referencias

### Documentación Microsoft

- [Work Item Tracking API](https://learn.microsoft.com/en-us/rest/api/azure/devops/wit/work-items)
- [Link Types](https://learn.microsoft.com/en-us/azure/devops/boards/queries/link-type-reference)
- [Hierarchy Links](https://learn.microsoft.com/en-us/azure/devops/boards/queries/link-work-items-support-traceability)

### Archivos del Proyecto

- `src/models/state.py` - Estado con `azure_pbi_id`, `azure_implementation_task_id`, `azure_testing_task_id`
- `src/agents/requirements_manager.py` - Creación y guardado del PBI
- `src/agents/codificador_corrector.py` - Creación de Tasks y guardado de IDs
- `src/agents/ejecutor_pruebas.py` - Adjunto de tests cuando pasan
- `src/agents/stakeholder.py` - Adjunto de código final cuando valida
- `src/tools/azure_devops_integration.py` - API cliente con `create_task()`, `create_bug()`, `attach_file()`
- `example_create_work_items.py` - Script de demostración de creación de work items
- `test_attach_files.py` - Script de prueba de adjuntos ⭐ NUEVO

---

## 📎 Adjuntar Archivos a Work Items

**Versión:** 3.0 ⭐ NUEVO  
**Feature:** Adjuntar código y tests generados automáticamente

### Funcionalidad

El sistema ahora **adjunta automáticamente** los archivos generados a los work items correspondientes:

#### 1. **Ejecutor de Pruebas** 🧪

Cuando los tests unitarios **pasan exitosamente**, adjunta el archivo de tests:

- ✅ Adjunta `unit_tests_req1_sq0.test.ts` al **PBI**
- ✅ Adjunta el mismo archivo a la **Task de Testing**
- 📝 Comentario: "Tests unitarios generados (req1_sq0) - Todos los tests pasaron"

#### 2. **Stakeholder** 👤

Cuando el código es **validado** por el stakeholder, adjunta el código final:

- ✅ Adjunta `codigo_final.ts` al **PBI**
- ✅ Adjunta el mismo archivo a la **Task de Implementación**
- 📝 Comentario: "Código final validado por el Stakeholder - Listo para producción"

### Proceso Técnico

El sistema utiliza la API de Azure DevOps en dos pasos:

**Paso 1: Subir archivo al attachment storage**

```http
POST /_apis/wit/attachments?fileName={name}&api-version=7.0
Content-Type: application/octet-stream

[binary file content]
```

**Paso 2: Vincular attachment al work item**

```http
PATCH /_apis/wit/workitems/{id}?api-version=7.0
Content-Type: application/json-patch+json

[{
  "op": "add",
  "path": "/relations/-",
  "value": {
    "rel": "AttachedFile",
    "url": "{attachment_url}",
    "attributes": {
      "comment": "Descripción del adjunto"
    }
  }
}]
```

### Ejemplo de Ejecución

```python
# Ejecutor Pruebas (cuando tests pasan)
azure_client.attach_file(
    work_item_id=state['azure_pbi_id'],
    file_path="output/unit_tests_req1_sq0.test.ts",
    comment="✅ Tests unitarios generados - Todos los tests pasaron"
)

azure_client.attach_file(
    work_item_id=state['azure_testing_task_id'],
    file_path="output/unit_tests_req1_sq0.test.ts",
    comment="✅ Suite de tests unitarios completa - 2048 bytes"
)

# Stakeholder (cuando valida)
azure_client.attach_file(
    work_item_id=state['azure_pbi_id'],
    file_path="output/codigo_final.ts",
    comment="✅ Código final validado por el Stakeholder - Listo para producción"
)

azure_client.attach_file(
    work_item_id=state['azure_implementation_task_id'],
    file_path="output/codigo_final.ts",
    comment="✅ Implementación completa y validada - 1536 bytes"
)
```

### Tracking de Task IDs

Para permitir adjuntos, el estado ahora incluye:

```python
class AgentState(TypedDict):
    # ...
    azure_pbi_id: int | None  # ID del PBI padre
    azure_implementation_task_id: int | None  # ⭐ NUEVO
    azure_testing_task_id: int | None  # ⭐ NUEVO
```

El **Codificador** guarda los IDs cuando crea las Tasks:

```python
state['azure_implementation_task_id'] = task_implementation['id']
state['azure_testing_task_id'] = task_testing['id']
```

### Resultado Final

```
PBI #2020946: [AI-Generated] Clase Calculator
  📎 codigo_final.ts (1536 bytes) - Código validado
  📎 unit_tests_req1_sq0.test.ts (2048 bytes) - Tests pasados
  ├── Task #2020950: [AI-Generated] Implementar Calculator
  │   📎 codigo_final.ts (1536 bytes) - Implementación completa
  └── Task #2020951: [AI-Generated] Crear unit tests para Calculator
      📎 unit_tests_req1_sq0.test.ts (2048 bytes) - Suite completa
```

### Script de Prueba

```bash
# Probar funcionalidad de adjuntos
python test_attach_files.py
```

El script:

1. Crea un PBI de prueba
2. Crea 2 Tasks asociadas
3. Crea archivos de ejemplo (código + tests)
4. Adjunta los archivos a los work items correspondientes
5. Muestra resumen y enlace a Azure DevOps

---

## 🎯 Próximos Pasos

### Posibles Mejoras

1. **Adjuntos con metadata enriquecida:** ✅ IMPLEMENTADO

   - Adjuntar código final y tests a PBI y Tasks
   - Comentarios descriptivos automáticos

2. **Detección inteligente de Bugs:**

   - Cuando SonarQube detecte issues críticos → Crear Bugs automáticos

3. **Actualización de PBI:**

   - Actualizar estado del PBI cuando todos los hijos estén completados

4. **Adjuntos de reportes:**
   - Adjuntar reportes de SonarQube como PDF
   - Adjuntar logs de ejecución de tests

---

**Autor:** Sistema de Desarrollo Multiagente  
**Estado:** ✅ Implementado y Documentado
