# 🔧 Solución Error 401 (Unauthorized) - Azure DevOps

## 🎯 Diagnóstico del Problema

**Error**: `<Response [401]>` al intentar conectar con Azure DevOps  
**URL**: `https://dev.azure.com/cegid/PeopleNet/_apis/projects?api-version=7.0`  
**Organización**: `cegid`  
**Proyecto**: `PeopleNet`

---

## ✅ Checklist de Solución

### 1. Verificar el Personal Access Token (PAT)

El error 401 generalmente significa que el PAT es inválido, expiró o no tiene permisos.

#### Paso 1.1: Verificar que el PAT está configurado

```bash
# En PowerShell
$env:AZURE_DEVOPS_PAT
```

Si está vacío, verifica tu archivo `.env`:

```bash
cat .env | Select-String "AZURE_DEVOPS"
```

#### Paso 1.2: Crear un NUEVO Personal Access Token

1. Ve a Azure DevOps: `https://dev.azure.com/cegid`
2. Click en tu **avatar** (esquina superior derecha)
3. Selecciona **Personal access tokens**
4. Click **+ New Token**

**Configuración del token**:
```
Name: Sistema-Multiagente-PeopleNet
Organization: cegid
Expiration: 90 days (recomendado)

Scopes: 
  ✅ Work Items: Read, write, & manage
  
  Opcional (para funciones futuras):
  ⬜ Code: Read
  ⬜ Project and Team: Read
```

5. Click **Create**
6. **⚠️ IMPORTANTE**: Copia el token INMEDIATAMENTE (solo se muestra una vez)

#### Paso 1.3: Actualizar el .env

```bash
# Abrir .env
notepad .env

# Actualizar con el NUEVO token
AZURE_DEVOPS_ENABLED=true
AZURE_DEVOPS_ORG=cegid
AZURE_DEVOPS_PROJECT=PeopleNet
AZURE_DEVOPS_PAT=el-token-que-copiaste-en-paso-1.2

# Opcional (si tienes sprints configurados)
AZURE_ITERATION_PATH=PeopleNet\\Sprint 1
AZURE_AREA_PATH=PeopleNet\\Backend
```

---

### 2. Verificar Permisos del Usuario

Tu cuenta debe tener permisos para:
- ✅ Ver el proyecto `PeopleNet`
- ✅ Crear Work Items
- ✅ Modificar Work Items

Para verificar:
1. Ve a `https://dev.azure.com/cegid/PeopleNet`
2. Si puedes ver el proyecto → tienes acceso básico ✅
3. Ve a **Boards** → **Work Items**
4. Intenta crear un PBI manualmente
5. Si puedes → tienes permisos correctos ✅

---

### 3. Probar la Conexión

Después de actualizar el PAT:

```python
# Test manual rápido
python -c "
from src.tools.azure_devops_integration import AzureDevOpsClient
client = AzureDevOpsClient()
if client.test_connection():
    print('✅ Conexión exitosa!')
else:
    print('❌ Aún hay problemas')
"
```

O usa el script de prueba:

```bash
python test_azure_devops_connection.py
```

---

### 4. Verificar el Formato del PAT

El PAT debe ser una cadena larga de caracteres (aproximadamente 52 caracteres):

```
Ejemplo válido:
abcdefghijklmnopqrstuvwxyz0123456789abcdefghijklmnop

❌ Incorrecto:
- Vacío: ""
- Con espacios: "abc def ghi"
- Con comillas extra: '"abc..."'
- Parcial: "abc..." (cortado)
```

---

### 5. Verificar la Codificación del PAT

El código usa autenticación Basic con formato `:{PAT}` en Base64.

**Verificación manual**:

```python
import base64

# Tu PAT
pat = "tu-token-aqui"

# Codificar (como lo hace el código)
credentials = f":{pat}"
encoded = base64.b64encode(credentials.encode()).decode()

print(f"Encoded: {encoded}")
print(f"Authorization: Basic {encoded}")
```

Debería producir algo como:
```
Encoded: OmFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6...
Authorization: Basic OmFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6...
```

---

### 6. Test con cURL (Diagnóstico directo)

```bash
# En PowerShell
$pat = "tu-pat-aqui"
$base64 = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes(":$pat"))

curl -H "Authorization: Basic $base64" `
     "https://dev.azure.com/cegid/PeopleNet/_apis/projects?api-version=7.0"
```

**Resultado esperado**:
- ✅ Código 200 + JSON con información del proyecto
- ❌ Código 401 → PAT inválido o expirado

---

### 7. Alternativa: Usar API con Browser (Validación)

1. Abre tu navegador
2. Asegúrate de estar logueado en `dev.azure.com/cegid`
3. Ve a: `https://dev.azure.com/cegid/PeopleNet/_apis/projects?api-version=7.0`

Si ves JSON → Tu cuenta tiene acceso  
Si ves error → Problema de permisos de cuenta

---

## 🔍 Diagnóstico Avanzado

### Script de Diagnóstico Completo

Guarda esto como `diagnose_azure.py`:

```python
import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("🔍 DIAGNÓSTICO DE AZURE DEVOPS")
print("=" * 60)

# 1. Verificar variables de entorno
org = os.getenv("AZURE_DEVOPS_ORG", "")
project = os.getenv("AZURE_DEVOPS_PROJECT", "")
pat = os.getenv("AZURE_DEVOPS_PAT", "")
enabled = os.getenv("AZURE_DEVOPS_ENABLED", "false")

print(f"\n1. Variables de entorno:")
print(f"   AZURE_DEVOPS_ENABLED: {enabled}")
print(f"   AZURE_DEVOPS_ORG: {org or '❌ NO CONFIGURADO'}")
print(f"   AZURE_DEVOPS_PROJECT: {project or '❌ NO CONFIGURADO'}")
print(f"   AZURE_DEVOPS_PAT: {'✅ Configurado (' + str(len(pat)) + ' chars)' if pat else '❌ NO CONFIGURADO'}")

if not all([org, project, pat]):
    print("\n❌ Configuración incompleta. Revisa tu archivo .env")
    exit(1)

# 2. Verificar codificación
credentials = f":{pat}"
encoded = base64.b64encode(credentials.encode()).decode()

print(f"\n2. Codificación PAT:")
print(f"   PAT Length: {len(pat)} caracteres")
print(f"   Encoded (primeros 20): {encoded[:20]}...")

# 3. Test de conexión
url = f"https://dev.azure.com/{org}/{project}/_apis/projects?api-version=7.0"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Basic {encoded}"
}

print(f"\n3. Test de conexión:")
print(f"   URL: {url}")

try:
    response = requests.get(url, headers=headers, timeout=10)
    
    print(f"   Status Code: {response.status_code}")
    print(f"   Reason: {response.reason}")
    
    if response.status_code == 200:
        print("\n✅ ¡CONEXIÓN EXITOSA!")
        data = response.json()
        print(f"\n   Proyecto encontrado:")
        print(f"   - Nombre: {data.get('name', 'N/A')}")
        print(f"   - ID: {data.get('id', 'N/A')}")
        print(f"   - Estado: {data.get('state', 'N/A')}")
    elif response.status_code == 401:
        print("\n❌ ERROR 401: UNAUTHORIZED")
        print("\n   Posibles causas:")
        print("   1. El PAT es inválido o expiró")
        print("   2. El PAT no tiene permisos de Work Items")
        print("   3. El formato del PAT está corrupto")
        print("\n   Solución:")
        print("   1. Ve a https://dev.azure.com/cegid/_usersSettings/tokens")
        print("   2. Genera un NUEVO token con 'Work Items: Read, write, & manage'")
        print("   3. Actualiza AZURE_DEVOPS_PAT en .env con el nuevo token")
    elif response.status_code == 404:
        print("\n❌ ERROR 404: NOT FOUND")
        print(f"\n   El proyecto '{project}' no existe en la organización '{org}'")
        print("\n   Verifica:")
        print(f"   1. Nombre correcto del proyecto (case-sensitive)")
        print(f"   2. URL correcta: https://dev.azure.com/{org}/{project}")
    else:
        print(f"\n❌ ERROR {response.status_code}")
        print(f"   Respuesta: {response.text[:200]}")
        
except requests.exceptions.Timeout:
    print("\n❌ TIMEOUT: No se pudo conectar (revisa tu internet)")
except Exception as e:
    print(f"\n❌ EXCEPCIÓN: {e}")

print("\n" + "=" * 60)
```

Ejecutar:
```bash
python diagnose_azure.py
```

---

## 🎯 Solución Paso a Paso Recomendada

### Para tu caso específico (cegid/PeopleNet):

1. **Genera un nuevo PAT**:
   ```
   https://dev.azure.com/cegid/_usersSettings/tokens
   → New Token
   → Name: "Multiagente-PeopleNet"
   → Scope: Work Items (Read, write, & manage)
   → Create
   → COPIAR TOKEN INMEDIATAMENTE
   ```

2. **Actualiza tu .env**:
   ```ini
   AZURE_DEVOPS_ENABLED=true
   AZURE_DEVOPS_ORG=cegid
   AZURE_DEVOPS_PROJECT=PeopleNet
   AZURE_DEVOPS_PAT=<pegar-token-aqui-sin-comillas>
   ```

3. **Reinicia el entorno Python**:
   ```bash
   # En VS Code, reinicia el terminal Python
   # O cierra y vuelve a abrir VS Code
   ```

4. **Prueba la conexión**:
   ```bash
   python test_azure_devops_connection.py
   ```

---

## 📞 Si Aún Tienes Problemas

### Opción 1: Deshabilitar Azure DevOps temporalmente

```ini
# En .env
AZURE_DEVOPS_ENABLED=false
```

El sistema funcionará normalmente sin crear PBIs.

### Opción 2: Validar permisos con tu admin

Contacta al administrador de Azure DevOps de `cegid` y solicita:
- Acceso de **Contributor** al proyecto `PeopleNet`
- Permisos de **Work Items: Read & Write**

### Opción 3: Test con proyecto de prueba

Si tienes tu propia organización de Azure DevOps:
```ini
AZURE_DEVOPS_ORG=tu-organizacion-personal
AZURE_DEVOPS_PROJECT=tu-proyecto-de-prueba
```

---

## ✅ Checklist Final

- [ ] Generé un NUEVO PAT en dev.azure.com
- [ ] El PAT tiene scope "Work Items (Read, write, & manage)"
- [ ] Copié el PAT completo sin espacios
- [ ] Actualicé AZURE_DEVOPS_PAT en .env
- [ ] Reinicié el terminal/IDE
- [ ] Ejecuté `python test_azure_devops_connection.py`
- [ ] Recibí "✅ Conexión exitosa"

---

**Última actualización**: 10 diciembre 2025  
**Error diagnosticado**: 401 Unauthorized con cegid/PeopleNet
