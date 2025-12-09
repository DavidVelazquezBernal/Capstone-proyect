# 🔑 Cómo Obtener Credenciales de SonarQube

Esta guía te muestra cómo obtener los valores necesarios para conectar con SonarQube Server o SonarCloud.

---

## 📋 Valores Necesarios

Para usar SonarQube real necesitas 3 valores:

1. **SONARQUBE_URL** - URL de tu servidor SonarQube
2. **SONARQUBE_TOKEN** - Token de autenticación
3. **SONARQUBE_PROJECT_KEY** - Identificador del proyecto

---

## 🌐 Opción A: SonarCloud (Gratis para proyectos públicos)

### 1. Crear Cuenta en SonarCloud

```
1. Ve a: https://sonarcloud.io
2. Click en "Log in" → "Sign up with GitHub"
3. Autoriza SonarCloud para acceder a tu GitHub
```

### 2. Crear Organización

```
1. Una vez logueado, click en tu avatar → "My Organizations"
2. Click en "+ Create an organization"
3. Selecciona tu cuenta de GitHub
4. Elige nombre para tu organización (ejemplo: tu-usuario-github)
```

### 3. Importar Proyecto desde GitHub

```
1. Click en "+" → "Analyze new project"
2. Selecciona tu repositorio "Capstone-proyect"
3. Click en "Set up"
4. Elige "With GitHub Actions" o "Other CI"
5. Anota el PROJECT KEY que aparece (ejemplo: tu-usuario_Capstone-proyect)
```

### 4. Generar Token

```
1. Click en tu avatar (arriba derecha)
2. "My Account" → "Security" tab
3. En "Generate Tokens":
   - Name: "Capstone Project Token"
   - Type: "User Token"
   - Expires in: "No expiration" (o 90 días)
4. Click "Generate"
5. ⚠️ COPIA EL TOKEN - Solo se muestra una vez
   Ejemplo: squ_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0
```

### 5. Valores para tu .env

Después de estos pasos, tendrás:

```env
# SonarCloud Configuration
SONARQUBE_URL=https://sonarcloud.io
SONARQUBE_TOKEN=squ_tu_token_copiado_aqui
SONARQUBE_PROJECT_KEY=tu-usuario_Capstone-proyect
```

---

## 🖥️ Opción B: SonarQube Server Local (Instalación propia)

### 1. Instalar SonarQube Server

**Opción Docker (Recomendada):**

```bash
# Descargar e iniciar SonarQube con Docker
docker run -d --name sonarqube -p 9000:9000 sonarqube:latest

# Esperar 1-2 minutos a que inicie
```

**Opción Manual:**

```bash
# Descargar desde: https://www.sonarsource.com/products/sonarqube/downloads/
# Descomprimir y ejecutar:
# Windows: bin/windows-x86-64/StartSonar.bat
# Linux/Mac: bin/linux-x86-64/sonar.sh start
```

### 2. Acceder a la Interfaz Web

```
1. Abre: http://localhost:9000
2. Login inicial:
   - Usuario: admin
   - Contraseña: admin
3. Te pedirá cambiar la contraseña
```

### 3. Crear Proyecto

```
1. Click en "Create project" (manual setup)
2. Project key: capstone-multiagent
3. Display name: Capstone Multiagent
4. Click "Set Up"
```

### 4. Generar Token

```
1. En la página del proyecto, click "Locally"
2. Genera un token:
   - Token name: "Local Development"
   - Click "Generate"
3. ⚠️ COPIA EL TOKEN
   Ejemplo: sqp_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

### 5. Valores para tu .env

```env
# SonarQube Server Local
SONARQUBE_URL=http://localhost:9000
SONARQUBE_TOKEN=sqp_tu_token_copiado_aqui
SONARQUBE_PROJECT_KEY=capstone-multiagent
```

---

## 🔧 Configurar el Proyecto

### 1. Editar archivo .env

Abre/crea el archivo `.env` en la raíz del proyecto:

```bash
# Abre el archivo
code .env
```

Añade las variables:

```env
# API Keys existentes
GEMINI_API_KEY=tu_clave_actual
E2B_API_KEY=tu_clave_actual

# SonarQube Configuration (NUEVO)
SONARQUBE_URL=https://sonarcloud.io
SONARQUBE_TOKEN=squ_tu_token_aqui
SONARQUBE_PROJECT_KEY=tu_proyecto_key
```

### 2. Verificar Configuración

```python
# Prueba en Python
from src.config.settings import settings

print(f"SonarQube URL: {settings.SONARQUBE_URL}")
print(f"Token configurado: {'✅' if settings.SONARQUBE_TOKEN else '❌'}")
print(f"Project Key: {settings.SONARQUBE_PROJECT_KEY}")
```

---

## 📊 Analizar tu Proyecto Inicialmente

Una vez configurado, analiza tu proyecto por primera vez:

### Para SonarCloud:

```bash
# Instalar sonar-scanner
npm install -g sonarqube-scanner

# Ejecutar análisis
sonar-scanner \
  -Dsonar.projectKey=tu_proyecto_key \
  -Dsonar.organization=tu_organizacion \
  -Dsonar.sources=src \
  -Dsonar.host.url=https://sonarcloud.io \
  -Dsonar.login=tu_token
```

### Para SonarQube Server Local:

```bash
# Instalar sonar-scanner
# Windows: Descargar de https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/
# Mac: brew install sonar-scanner

# Ejecutar análisis
sonar-scanner \
  -Dsonar.projectKey=capstone-multiagent \
  -Dsonar.sources=src \
  -Dsonar.host.url=http://localhost:9000 \
  -Dsonar.login=tu_token
```

---

## 🎯 Usar con el Sistema Multiagente

Una vez configurado, el sistema usará la API de SonarQube automáticamente:

```python
# En sonarqube_mcp_real.py ya está preparado
from tools.sonarqube_mcp_real import analizar_archivo_con_mejor_metodo_disponible

# Analizará con la API de SonarQube si está configurada
result = analizar_archivo_con_mejor_metodo_disponible("ruta/al/archivo.py")
```

---

## ✅ Verificación Rápida

### Test de Conexión

```python
# Crear archivo test_sonarqube_connection.py
import requests
from config.settings import settings

url = f"{settings.SONARQUBE_URL}/api/system/status"
headers = {"Authorization": f"Bearer {settings.SONARQUBE_TOKEN}"}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    print("✅ Conexión exitosa con SonarQube")
    print(f"   Status: {response.json()['status']}")
else:
    print(f"❌ Error: {response.status_code}")
```

Ejecutar:
```bash
python test_sonarqube_connection.py
```

---

## 🆓 Comparación de Opciones

### SonarCloud (Recomendado para empezar)
- ✅ **Gratis** para proyectos públicos
- ✅ Sin instalación ni mantenimiento
- ✅ Integración fácil con GitHub
- ✅ Actualizaciones automáticas
- ❌ Proyectos privados requieren pago

### SonarQube Server Local
- ✅ **Gratis** (Community Edition)
- ✅ Total control y privacidad
- ✅ Sin límites de proyectos
- ❌ Requiere instalación y mantenimiento
- ❌ Consume recursos del equipo

### Solo SonarLint (Actual)
- ✅ **Gratis** y sin configuración
- ✅ Análisis local inmediato
- ✅ Ya está funcionando
- ❌ No hay métricas centralizadas
- ❌ Reglas no personalizables en equipo

---

## 🎓 Resumen Rápido

**Para uso básico (sin configurar nada):**
- Ya tienes análisis estático básico funcionando ✅

**Para análisis profesional (5 minutos):**
1. Crea cuenta en SonarCloud.io
2. Importa tu proyecto de GitHub
3. Genera token
4. Añade al .env: URL, TOKEN, PROJECT_KEY

**Para máximo control (15 minutos):**
1. Instala SonarQube con Docker
2. Crea proyecto local
3. Genera token
4. Añade al .env

---

## 📚 Recursos Adicionales

- [SonarCloud Signup](https://sonarcloud.io)
- [SonarQube Download](https://www.sonarsource.com/products/sonarqube/downloads/)
- [Documentación API](https://docs.sonarqube.org/latest/extend/web-api/)
- [SonarScanner Guide](https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/)

---

**¿Necesitas ayuda?** Elige una opción y te guío paso a paso.
