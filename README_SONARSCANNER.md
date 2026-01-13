# 🔍 SonarScanner CLI - Guía de Configuración

## ⚠️ IMPORTANTE: Requisito de Servidor SonarQube

**Si configuras `SONARSCANNER_ENABLED=true`, DEBES tener un servidor SonarQube ejecutándose localmente.**

Sin un servidor corriendo, obtendrás errores como:
```
java.net.ConnectException: Connection refused: getsockopt
```

## 🚀 Inicio Rápido

### Arrancar Servidor SonarQube Local

**Opción 1: Docker (Recomendado)**
```bash
docker run -d --name sonarqube -p 9000:9000 sonarqube:latest
```

**Opción 2: Manual**
```bash
# Descargar desde: https://www.sonarsource.com/products/sonarqube/downloads/
# Ejecutar:
C:\sonarqube\bin\windows-x86-64\StartSonar.bat
```

### Verificar que el Servidor está Corriendo
- Abre: `http://localhost:9000`
- Login: `admin` / `admin`
- Genera un token en: **My Account** → **Security** → **Generate Token**

## ✅ Instalación de SonarScanner CLI

- **Ubicación**: `C:\sonar-scanner\sonar-scanner-6.2.1.4610-windows-x64\`
- **Ejecutable**: `C:\sonar-scanner\sonar-scanner-6.2.1.4610-windows-x64\bin\sonar-scanner.bat`
- **Versión**: 6.2.1.4610

### 2. Archivos Modificados

#### `src/config/settings.py`
- Añadidas variables: `SONARSCANNER_ENABLED`, `SONARSCANNER_PATH`
- URL de SonarQube por defecto: `http://localhost:9000`

#### `src/tools/sonarqube_mcp.py`
- Nueva función: `_ejecutar_sonarscanner_cli()` - Ejecuta SonarScanner CLI
- Nueva función: `_obtener_issues_desde_sonarqube()` - Obtiene issues del servidor
- Nueva función: `_parsear_output_sonarscanner()` - Parsea output local
- Flujo actualizado: SonarCloud → SonarScanner CLI → Análisis Estático

#### `.env.example`
- Nuevas variables de configuración para SonarScanner CLI
- Documentación de opciones de configuración

#### `sonar-project.properties` (nuevo)
- Configuración del proyecto para SonarScanner
- Exclusiones de directorios (node_modules, .venv, etc.)

### 3. Documentación

- **`docs/SONARSCANNER_CLI.md`**: Guía completa de uso
- **`README_SONARSCANNER.md`**: Este archivo (resumen de cambios)

## 🚀 Cómo Usar

### Opción 1: SonarScanner CLI con Servidor Local

⚠️ **REQUISITO**: Servidor SonarQube debe estar corriendo en `http://localhost:9000`

```bash
# 1. Arrancar servidor SonarQube (ver sección anterior)
docker run -d --name sonarqube -p 9000:9000 sonarqube:latest

# 2. Configurar en src/.env
SONARSCANNER_ENABLED=true
SONARSCANNER_PATH=C:\sonar-scanner\sonar-scanner-6.2.1.4610-windows-x64\bin\sonar-scanner.bat
SONARQUBE_URL=http://localhost:9000
SONARQUBE_TOKEN=tu-token-aqui
SONARQUBE_PROJECT_KEY=capstone-project
```

**Resultado**: Análisis completo con todas las reglas, métricas y Quality Gates.

**Comando para verificar scanner:**
```bash
C:\sonar-scanner\sonar-scanner-6.2.1.4610-windows-x64\bin\sonar-scanner.bat --version
```

### Opción 2: Análisis Estático Local (Sin Servidor)

```bash
# En src/.env
SONARSCANNER_ENABLED=false
```

**Resultado**: Análisis básico local sin necesidad de servidor SonarQube.

### Opción 3: Usar SonarCloud (Recomendado para proyectos públicos)

```bash
# En src/.env
SONARCLOUD_ENABLED=true
SONARCLOUD_TOKEN=squ_tu-token
SONARCLOUD_ORGANIZATION=tu-org
SONARCLOUD_PROJECT_KEY=tu-proyecto
```

**Resultado**: Análisis en la nube sin necesidad de servidor local.

## 📊 Flujo de Análisis

```
┌─────────────────────────────────────────┐
│  Agente SonarQube ejecuta análisis     │
└─────────────┬───────────────────────────┘
              │
              ▼
    ┌─────────────────────┐
    │ ¿SonarCloud activo? │
    └──────┬──────────────┘
           │ Sí
           ▼
    ┌─────────────────────┐
    │ Análisis SonarCloud │──── ✅ Issues reales
    └─────────────────────┘
           │ No/Falla
           ▼
    ┌─────────────────────────┐
    │ ¿SonarScanner habilitado?│
    └──────┬──────────────────┘
           │ Sí
           ▼
    ┌─────────────────────────┐
    │ Ejecutar SonarScanner   │
    └──────┬──────────────────┘
           │
           ├─── ¿Servidor configurado?
           │    │ Sí
           │    ▼
           │    Obtener issues del servidor ✅
           │    │ No
           │    ▼
           │    Parsear output local ⚠️
           │
           │ No/Falla
           ▼
    ┌─────────────────────────┐
    │ Análisis Estático Local │──── ⚠️ Reglas simuladas
    └─────────────────────────┘
```

## 🔧 Configuración Rápida

### Para Empezar Inmediatamente

1. Copiar `.env.example` a `src/.env`
2. Añadir tu `GEMINI_API_KEY`
3. Habilitar SonarScanner:
   ```bash
   SONARSCANNER_ENABLED=true
   ```
4. Ejecutar: `python src/main.py`

### Para Análisis Completo (Opcional)

1. Instalar SonarQube Community Edition (o usar SonarCloud)
2. Iniciar servidor: `http://localhost:9000`
3. Generar token en SonarQube
4. Configurar en `.env`:
   ```bash
   SONARQUBE_URL=http://localhost:9000
   SONARQUBE_TOKEN=tu-token
   ```

## 📝 Verificar Instalación

```powershell
# Verificar SonarScanner CLI
sonar-scanner.bat --version

# Debería mostrar:
# INFO: SonarScanner 6.2.1.4610
```

Si no funciona, reinicia tu terminal/IDE para cargar el nuevo PATH.

## 🎯 Ventajas de SonarScanner CLI

### vs Análisis Estático Local
- ✅ Reglas reales de SonarQube
- ✅ Análisis más preciso
- ✅ Soporte para más lenguajes
- ✅ Actualizable (nuevas reglas)

### vs SonarCloud
- ✅ Funciona sin conexión a internet
- ✅ No requiere configuración de GitHub
- ✅ Análisis más rápido (local)
- ❌ Sin histórico ni dashboard web

## 🐛 Solución de Problemas

### "SonarScanner CLI no encontrado"

```bash
# Especificar ruta completa en .env
SONARSCANNER_PATH=C:\sonar-scanner\sonar-scanner-6.2.1.4610-windows-x64\bin\sonar-scanner.bat
```

### "Timeout ejecutando SonarScanner"

- Reducir tamaño del código
- Verificar servidor SonarQube
- Usar análisis local sin servidor

### Desactivar SonarScanner CLI

```bash
# En .env
SONARSCANNER_ENABLED=false
```

## 📚 Más Información

Ver documentación completa en: `docs/SONARSCANNER_CLI.md`

## 🔄 Rollback

Para volver al análisis estático anterior:

```bash
# En .env
SONARSCANNER_ENABLED=false
SONARCLOUD_ENABLED=false
```

El sistema usará automáticamente el análisis estático local.
