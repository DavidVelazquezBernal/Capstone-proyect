# Guía de Instalación de SonarQube Local

## 📥 Instalación

### 1. Descargar SonarQube Community Edition

1. Ir a: https://www.sonarsource.com/products/sonarqube/downloads/
2. Descargar **Community Edition** (gratuita)
3. Versión recomendada: SonarQube 10.x o última LTS

### 2. Extraer e Instalar

```powershell
# Crear directorio
New-Item -ItemType Directory -Force -Path "C:\sonarqube"

# Extraer el ZIP descargado a C:\sonarqube
# Resultado: C:\sonarqube\sonarqube-10.x\
```

### 3. Iniciar SonarQube

**Opción A: Desde PowerShell**
```powershell
cd C:\sonarqube\sonarqube-10.x\bin\windows-x86-64
.\StartSonar.bat
```

**Opción B: Script de inicio rápido**
```powershell
# Guardar como start-sonarqube.ps1
$sonarPath = "C:\sonarqube\sonarqube-10.x\bin\windows-x86-64"
if (Test-Path $sonarPath) {
    Write-Host "🚀 Iniciando SonarQube..." -ForegroundColor Green
    Set-Location $sonarPath
    .\StartSonar.bat
} else {
    Write-Host "❌ SonarQube no encontrado en: $sonarPath" -ForegroundColor Red
    Write-Host "   Verifica la ruta de instalación" -ForegroundColor Yellow
}
```

### 4. Esperar Inicio (2-3 minutos)

SonarQube tarda en iniciar. Verás mensajes como:
```
SonarQube is operational
```

### 5. Acceder a la Interfaz Web

1. Abrir navegador: http://localhost:9000
2. **Credenciales por defecto:**
   - Usuario: `admin`
   - Contraseña: `admin`
3. **Cambiar contraseña** (obligatorio en primer acceso)

## 🔑 Generar Token

### Paso 1: Acceder a Security

1. Hacer clic en tu avatar (esquina superior derecha)
2. Ir a **My Account** > **Security**

### Paso 2: Generar Token

1. En la sección **Generate Tokens**:
   - **Name:** `multiagentes-coding-cli`
   - **Type:** `User Token`
   - **Expires in:** `No expiration` (o el tiempo que prefieras)
2. Hacer clic en **Generate**
3. **COPIAR EL TOKEN** (solo se muestra una vez)

Ejemplo de token: `squ_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0`

### Paso 3: Crear Proyecto

1. Ir a **Projects** > **Create Project**
2. Seleccionar **Manually**
3. Configurar:
   - **Project key:** `multiagentes-coding`
   - **Display name:** `Multiagentes Coding System`
4. Hacer clic en **Set Up**

## ⚙️ Configurar .env

Agregar a tu archivo `src/.env`:

```bash
# SonarScanner CLI con servidor local
SONARSCANNER_ENABLED=true
SONARSCANNER_PATH=sonar-scanner.bat

# Configuración del servidor SonarQube local
SONARQUBE_URL=http://localhost:9000
SONARQUBE_TOKEN=squ_tu_token_aqui  # Token generado en paso anterior
SONARQUBE_PROJECT_KEY=multiagentes-coding
```

## ✅ Verificar Instalación

### Test 1: Verificar que el servidor está corriendo

```powershell
# Debe devolver código 200
curl http://localhost:9000/api/system/status
```

### Test 2: Ejecutar test de SonarScanner CLI

```powershell
python src/test_ai/test_sonarscanner_without_sonarcloud.py
```

**Salida esperada:**
```
✅ SonarScanner CLI: X issues encontrados
Source: sonarscanner-cli
```

## 🛑 Detener SonarQube

**Opción A: Ctrl+C en la terminal donde se ejecuta**

**Opción B: Script de detención**
```powershell
# Detener proceso de SonarQube
Get-Process | Where-Object {$_.ProcessName -like "*java*" -and $_.CommandLine -like "*sonar*"} | Stop-Process -Force
```

## 🔧 Troubleshooting

### Error: "Port 9000 already in use"

Otro proceso está usando el puerto 9000:
```powershell
# Ver qué proceso usa el puerto 9000
netstat -ano | findstr :9000

# Detener el proceso (reemplazar PID)
Stop-Process -Id PID -Force
```

### Error: "Elasticsearch failed to start"

Elasticsearch (incluido en SonarQube) necesita:
- **Mínimo 2GB RAM disponible**
- **Java 17** instalado

Verificar Java:
```powershell
java -version
# Debe mostrar: Java 17.x o superior
```

### Error: "Access denied" al iniciar

Ejecutar PowerShell/CMD **como Administrador**

### SonarQube no inicia

Revisar logs:
```powershell
# Ver logs de SonarQube
Get-Content C:\sonarqube\sonarqube-10.x\logs\sonar.log -Tail 50
```

## 📊 Uso con el Sistema Multiagente

Una vez configurado:

1. **SonarQube debe estar corriendo** antes de ejecutar el sistema
2. El sistema automáticamente:
   - Ejecuta SonarScanner CLI
   - Envía código al servidor SonarQube
   - Obtiene issues y métricas
   - Genera reportes de calidad

## 🔄 Workflow Típico

```powershell
# 1. Iniciar SonarQube
cd C:\sonarqube\sonarqube-10.x\bin\windows-x86-64
.\StartSonar.bat

# 2. Esperar 2-3 minutos hasta que esté operacional

# 3. Ejecutar sistema multiagente
cd C:\ACADEMIA\IIA\Capstone proyect v2
python src/main.py

# 4. Al terminar, detener SonarQube (Ctrl+C)
```

## 📚 Referencias

- [Documentación oficial de SonarQube](https://docs.sonarsource.com/sonarqube/latest/)
- [Guía de instalación](https://docs.sonarsource.com/sonarqube/latest/setup-and-upgrade/install-the-server/)
- [API de SonarQube](https://docs.sonarsource.com/sonarqube/latest/extension-guide/web-api/)

## 💡 Alternativa: SonarCloud

Si no quieres mantener un servidor local, considera usar **SonarCloud** (gratuito para proyectos open source):

```bash
SONARCLOUD_ENABLED=true
SONARCLOUD_TOKEN=squ_tu_token
SONARCLOUD_ORGANIZATION=tu_org
SONARCLOUD_PROJECT_KEY=tu_proyecto
SONARSCANNER_ENABLED=false
```

Ver: [SONARSCANNER_CONFIGURATION_MATRIX.md](SONARSCANNER_CONFIGURATION_MATRIX.md)
