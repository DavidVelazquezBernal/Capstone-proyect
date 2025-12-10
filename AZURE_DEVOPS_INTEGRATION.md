# 🔷 Integración con Azure DevOps

## 📋 Descripción

Esta integración permite al **Product Owner** crear automáticamente **Product Backlog Items (PBIs)** en Azure DevOps durante el flujo de generación de código. Cada vez que se formalizan requisitos, el sistema puede:

- ✅ Crear un PBI en Azure DevOps con descripción completa
- ✅ Estimar y asignar Story Points automáticamente
- ✅ Configurar Iteration Path y Area Path
- ✅ Agregar tags descriptivos (AI-Generated, Multiagente, etc.)
- ✅ Incluir criterios de aceptación detallados
- ✅ Mantener trazabilidad completa con URLs

---

## 🚀 Configuración Inicial

### 1. Obtener Personal Access Token (PAT)

1. Ve a tu Azure DevOps: `https://dev.azure.com/{tu-organizacion}`
2. Click en tu avatar (esquina superior derecha) → **Personal access tokens**
3. Click en **+ New Token**
4. Configura el token:
   - **Name**: `Sistema-Multiagente-Integration`
   - **Organization**: Selecciona tu organización
   - **Expiration**: Configura según tus necesidades (30-90 días recomendado)
   - **Scopes**: Selecciona **Work Items** → `Read, write, & manage`
5. Click en **Create**
6. **⚠️ IMPORTANTE**: Copia el token inmediatamente (solo se muestra una vez)

### 2. Configurar Variables de Entorno

Crea o edita tu archivo `.env` en la raíz del proyecto:

```bash
# Copiar el template
cp .env.example .env

# Editar con tu configuración
nano .env  # o usa tu editor preferido
```

Configura las siguientes variables:

```bash
# ============================================
# AZURE DEVOPS
# ============================================
AZURE_DEVOPS_ENABLED=true
AZURE_DEVOPS_ORG=tu-organizacion
AZURE_DEVOPS_PROJECT=tu-proyecto
AZURE_DEVOPS_PAT=tu-personal-access-token

# Opcional: Rutas de organización
AZURE_ITERATION_PATH=MiProyecto\\Sprint 1
AZURE_AREA_PATH=MiProyecto\\Backend
```

**Ejemplo real**:
```bash
AZURE_DEVOPS_ENABLED=true
AZURE_DEVOPS_ORG=contoso
AZURE_DEVOPS_PROJECT=MyAwesomeProject
AZURE_DEVOPS_PAT=abcdefghijklmnopqrstuvwxyz1234567890abcdefghijk
AZURE_ITERATION_PATH=MyAwesomeProject\\Sprint 5
AZURE_AREA_PATH=MyAwesomeProject\\Backend\\API
```

### 3. Instalar Dependencias

```bash
# El paquete requests ya está en requirements.txt
pip install -r requirements.txt
```

---

## 🧪 Probar la Integración

### Opción 1: Script de Prueba Dedicado

```bash
python test_azure_devops_connection.py
```

Este script:
1. ✅ Verifica la configuración
2. ✅ Prueba la conexión con Azure DevOps
3. ✅ Crea un PBI de prueba (con confirmación)
4. ✅ Valida el algoritmo de estimación de Story Points

**Salida esperada**:
```
🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀
  PRUEBA DE INTEGRACIÓN CON AZURE DEVOPS
🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀

✅ Conexión exitosa con Azure DevOps
✅ PBI creado exitosamente!
   • ID: #1234
   • URL: https://dev.azure.com/contoso/MyProject/_workitems/edit/1234
```

### Opción 2: Uso en Código Python

```python
from src.tools.azure_devops_integration import AzureDevOpsClient

# Crear cliente
client = AzureDevOpsClient()

# Probar conexión
if client.test_connection():
    print("✅ Conectado")
    
    # Crear un PBI
    pbi = client.create_pbi(
        title="Implementar endpoint de autenticación",
        description="<p>Crear endpoint POST /api/auth/login</p>",
        acceptance_criteria="<ul><li>Validar credenciales</li></ul>",
        story_points=5,
        tags=["Backend", "API", "Auth"]
    )
    
    if pbi:
        print(f"PBI creado: {pbi['_links']['html']['href']}")
```

---

## 🔧 Uso en el Flujo Multiagente

### Automático (Recomendado)

La integración se ejecuta automáticamente cuando:
1. `AZURE_DEVOPS_ENABLED=true` en `.env`
2. Se ejecuta el flujo normal con `python src/main.py`
3. El **Product Owner** formaliza requisitos

**Flujo**:
```
Usuario → main.py → Ingeniero de Requisitos → Product Owner
                                                    ↓
                                        [Formaliza Requisitos]
                                                    ↓
                                        [Estima Story Points]
                                                    ↓
                                        [Crea PBI en Azure DevOps]
                                                    ↓
                                        [Agrega metadatos al JSON]
                                                    ↓
                                              Codificador →
```

### Logs Esperados

```
💼 PRODUCT OWNER - INICIO
🔷 Integrando con Azure DevOps...
✅ Conexión exitosa con Azure DevOps
📊 Story Points estimados: 3
✅ PBI creado exitosamente: ID 1234
🔗 https://dev.azure.com/contoso/MyProject/_workitems/edit/1234
✅ PBI #1234 creado en Azure DevOps
✅ Requisitos formales generados y validados
💼 PRODUCT OWNER - FIN
```

### Salida JSON (con metadatos de Azure)

```json
{
  "objetivo_funcional": "Función para calcular factorial",
  "lenguaje_version": "Python 3.10+",
  "nombre_funcion": "def factorial(n: int) -> int",
  "entradas_esperadas": "Un entero positivo",
  "salidas_esperadas": "El factorial como entero",
  "azure_devops": {
    "work_item_id": 1234,
    "work_item_url": "https://dev.azure.com/contoso/MyProject/_workitems/edit/1234",
    "work_item_type": "Product Backlog Item",
    "area_path": "MyProject\\Backend",
    "iteration_path": "MyProject\\Sprint 5",
    "story_points": 3
  }
}
```

---

## 📊 Estimación de Story Points

El sistema utiliza una heurística basada en la complejidad de los requisitos:

| Complejidad | Story Points | Criterio |
|-------------|--------------|----------|
| Muy Simple | 1 | < 100 caracteres totales |
| Simple | 2 | 100-200 caracteres |
| Media | 3 | 200-350 caracteres |
| Media-Alta | 5 | 350-500 caracteres |
| Alta | 8 | 500-700 caracteres |
| Muy Alta | 13 | > 700 caracteres |

**Ejemplo**:
```python
from src.tools.azure_devops_integration import estimate_story_points

requisitos = {
    'objetivo_funcional': 'Validar email con regex',
    'entradas_esperadas': 'String',
    'salidas_esperadas': 'Boolean'
}

points = estimate_story_points(requisitos)  # → 1 (Muy Simple)
```

---

## 🔌 API del Cliente Azure DevOps

### `AzureDevOpsClient`

#### `test_connection() -> bool`
Prueba la conexión con Azure DevOps.

```python
client = AzureDevOpsClient()
if client.test_connection():
    print("Conectado")
```

#### `create_pbi(...) -> dict | None`
Crea un Product Backlog Item.

**Parámetros**:
- `title` (str): Título del PBI
- `description` (str): Descripción HTML
- `acceptance_criteria` (str): Criterios HTML
- `story_points` (int, opcional): 1-100
- `tags` (list[str], opcional): Lista de tags
- `priority` (int, opcional): 1=Alta, 2=Media, 3=Baja, 4=Muy Baja
- `custom_fields` (dict, opcional): Campos adicionales

**Retorna**: Dict con información del work item o `None` si falla

**Ejemplo**:
```python
pbi = client.create_pbi(
    title="[API] Implementar endpoint users",
    description="<h3>Objetivo</h3><p>CRUD de usuarios</p>",
    acceptance_criteria="<ul><li>GET /users</li><li>POST /users</li></ul>",
    story_points=5,
    tags=["Backend", "API"],
    priority=2
)
```

#### `update_work_item(work_item_id, fields) -> dict | None`
Actualiza un Work Item existente.

**Ejemplo**:
```python
client.update_work_item(
    1234,
    {
        "System.State": "Active",
        "System.AssignedTo": "usuario@dominio.com",
        "Microsoft.VSTS.Scheduling.RemainingWork": 8
    }
)
```

#### `get_work_item(work_item_id) -> dict | None`
Obtiene información de un Work Item.

```python
work_item = client.get_work_item(1234)
print(work_item['fields']['System.Title'])
```

#### `add_comment(work_item_id, comment) -> bool`
Agrega un comentario a un Work Item.

```python
client.add_comment(1234, "✅ Tests pasaron exitosamente")
```

---

## 🛠️ Troubleshooting

### Error: "❌ Error de conexión: 401"

**Causa**: Token inválido o expirado

**Solución**:
1. Verifica que el PAT sea correcto (cópialo de nuevo)
2. Asegúrate de que el token no haya expirado
3. Verifica que tenga permisos de Work Items (Read & Write)

### Error: "❌ Error de conexión: 404"

**Causa**: Organización o proyecto no encontrado

**Solución**:
1. Verifica `AZURE_DEVOPS_ORG` (debe ser exactamente como aparece en la URL)
2. Verifica `AZURE_DEVOPS_PROJECT` (sensible a mayúsculas/minúsculas)

### Error: "VS402337: Cannot find area with path..."

**Causa**: Area Path o Iteration Path inválido

**Solución**:
1. Ve a Azure DevOps → Project Settings → Project configuration
2. Copia el path exacto de la iteración/área
3. Usa formato: `Proyecto\\Ruta\\Subruta` (doble backslash)
4. O deja vacío para usar valores por defecto

### Warning: "⚠️ No se pudo conectar con Azure DevOps, continuando sin integración"

**Causa**: Configuración incorrecta o servicio no disponible

**Efecto**: El flujo continúa normalmente sin crear PBIs

**Solución**: Revisa logs detallados con `LOG_LEVEL=DEBUG`

---

## 📝 Campos de Azure DevOps Soportados

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `System.Title` | string | Título del work item |
| `System.Description` | HTML | Descripción detallada |
| `System.AreaPath` | string | Ruta del área |
| `System.IterationPath` | string | Ruta de la iteración/sprint |
| `System.State` | string | Estado (New, Active, Resolved, Closed) |
| `System.Tags` | string | Tags separados por `;` |
| `Microsoft.VSTS.Common.Priority` | int | 1-4 (1=Alta) |
| `Microsoft.VSTS.Common.AcceptanceCriteria` | HTML | Criterios de aceptación |
| `Microsoft.VSTS.Scheduling.StoryPoints` | int | Story points |

---

## 🔐 Seguridad

### Mejores Prácticas

1. **Nunca commitees el archivo `.env`** (ya está en `.gitignore`)
2. **Rota el PAT periódicamente** (cada 30-90 días)
3. **Usa permisos mínimos** (solo Work Items Read & Write)
4. **Scope del token**: Limítalo a la organización específica
5. **Monitorea el uso**: Azure DevOps > User Settings > Personal Access Tokens

### Revocar Token

Si el token se compromete:
1. Ve a Azure DevOps → User Settings → Personal Access Tokens
2. Encuentra el token comprometido
3. Click en **Revoke**
4. Genera un nuevo token y actualiza `.env`

---

## 📚 Referencias

- [Azure DevOps REST API Docs](https://learn.microsoft.com/en-us/rest/api/azure/devops/)
- [Work Items API](https://learn.microsoft.com/en-us/rest/api/azure/devops/wit/)
- [Personal Access Tokens](https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate)

---

## ✨ Próximas Mejoras

Posibles extensiones futuras:

- [ ] Actualizar el estado del PBI cuando el código pase todas las pruebas
- [ ] Agregar comentarios automáticos con resultados de SonarQube
- [ ] Crear Tasks automáticamente bajo cada PBI
- [ ] Sincronizar Issues de SonarQube como Bugs en Azure DevOps
- [ ] Soporte para Epic y Features (jerarquía completa)
- [ ] Webhooks para notificaciones en tiempo real
- [ ] Dashboard de métricas de generación de código

---

## 💡 Ejemplos de Uso Avanzado

### Crear múltiples Work Items

```python
from src.tools.azure_devops_integration import AzureDevOpsClient

client = AzureDevOpsClient()

requisitos = [
    {"titulo": "Auth API", "story_points": 8},
    {"titulo": "User CRUD", "story_points": 5},
    {"titulo": "Reporting", "story_points": 13}
]

for req in requisitos:
    pbi = client.create_pbi(
        title=req["titulo"],
        description=f"<p>Implementar {req['titulo']}</p>",
        acceptance_criteria="<ul><li>Tests pasan</li></ul>",
        story_points=req["story_points"]
    )
    print(f"✅ {pbi['id']}: {req['titulo']}")
```

### Actualizar PBI después de validación

```python
# En stakeholder.py o después del flujo completo
if state['validado']:
    azure_metadata = json.loads(state['requisitos_formales']).get('azure_devops')
    
    if azure_metadata and azure_metadata['work_item_id']:
        client = AzureDevOpsClient()
        client.update_work_item(
            azure_metadata['work_item_id'],
            {
                "System.State": "Resolved",
                "System.Tags": "AI-Generated; Validated; Production-Ready"
            }
        )
        client.add_comment(
            azure_metadata['work_item_id'],
            "✅ Código validado y tests superados automáticamente"
        )
```

---

**¿Necesitas ayuda?** Abre un issue en el repositorio o consulta los logs con `LOG_LEVEL=DEBUG`.
