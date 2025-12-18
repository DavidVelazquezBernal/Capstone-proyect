# SonarScanner CLI - Guía de Configuración y Uso

## 📋 Descripción

El sistema ahora soporta análisis de calidad de código usando **SonarScanner CLI**, que proporciona análisis real de código en lugar del análisis estático simulado.

**⚠️ Importante:** SonarScanner CLI está configurado para analizar **únicamente el código generado por el agente developer-code** (archivos con patrón `2_developer_req*_debug*_sq*.*`). Ver [SONARSCANNER_SCOPE.md](SONARSCANNER_SCOPE.md) para más detalles.

## 🔧 Instalación

### Windows

SonarScanner CLI ya está instalado en: `C:\sonar-scanner\sonar-scanner-6.2.1.4610-windows-x64\bin`

El PATH del usuario ya ha sido actualizado para incluir esta ruta.

### Verificar Instalación

```powershell
sonar-scanner.bat --version
```

Deberías ver algo como:
```
INFO: Scanner configuration file: C:\sonar-scanner\...\conf\sonar-scanner.properties
INFO: Project root configuration file: NONE
INFO: SonarScanner 6.2.1.4610
```

## ⚙️ Configuración

### 1. Variables de Entorno (.env)

Añade las siguientes variables a tu archivo `src/.env`:

```bash
# Habilitar SonarScanner CLI
SONARSCANNER_ENABLED=true

# Ruta al ejecutable (opcional si está en PATH)
SONARSCANNER_PATH=sonar-scanner.bat

# Configuración de SonarQube Server (REQUERIDO para SonarScanner CLI)
# SonarScanner CLI necesita un servidor para enviar resultados
SONARQUBE_URL=http://localhost:9000
SONARQUBE_TOKEN=tu-token-aqui
```

### 2. Servidor SonarQube (REQUERIDO para SonarScanner CLI)

**⚠️ IMPORTANTE:** SonarScanner CLI **requiere** un servidor SonarQube para funcionar. No puede ejecutarse en modo standalone.

Para análisis completo con servidor SonarQube:

#### Opción A: SonarQube Local

1. Descargar SonarQube Community Edition:
   ```
   https://www.sonarsource.com/products/sonarqube/downloads/
   ```

2. Iniciar servidor:
   ```powershell
   cd C:\sonarqube\bin\windows-x86-64
   StartSonar.bat
   ```

3. Acceder a: `http://localhost:9000`
   - Usuario: `admin`
   - Contraseña: `admin` (cambiar en primer acceso)

4. Generar token:
   - My Account > Security > Generate Tokens
   - Copiar token y añadir a `.env`

#### Opción B: SonarCloud (Recomendado)

Si prefieres usar SonarCloud en lugar de SonarScanner CLI local:

```bash
SONARCLOUD_ENABLED=true
SONARCLOUD_TOKEN=squ_tu-token
SONARCLOUD_ORGANIZATION=tu-org
SONARCLOUD_PROJECT_KEY=tu-proyecto
```

## 🚀 Uso

### Modo Automático

El sistema usa SonarScanner CLI automáticamente cuando:

1. `SONARSCANNER_ENABLED=true` en `.env`
2. El agente SonarQube ejecuta el análisis de código

### Flujo de Análisis

```
1. SonarCloud (si está habilitado y hay branch)
   ↓ (si falla o no disponible)
2. SonarScanner CLI (si está habilitado)
   ↓ (si falla o no disponible)
3. Análisis Estático Local (fallback)
```

### Configuración del Proyecto

El archivo `sonar-project.properties` en la raíz del proyecto contiene la configuración:

```properties
sonar.projectKey=multiagentes-coding
sonar.projectName=Multiagentes Coding System
sonar.projectVersion=1.0
sonar.sources=output
sonar.inclusions=**/2_developer_req*_debug*_sq*.*
sonar.exclusions=**/node_modules/**,**/.venv/**,**/0_*.txt,**/1_*.txt,**/3_*.txt,...
sonar.sourceEncoding=UTF-8
```

**Nota:** La propiedad `sonar.inclusions` asegura que solo se analiza código del agente developer-code.

## 📊 Tipos de Análisis

### 1. Con Servidor SonarQube

**Ventajas:**
- Análisis completo con todas las reglas
- Histórico de análisis
- Quality Gates
- Métricas detalladas
- Dashboard web

**Configuración:**
```bash
SONARSCANNER_ENABLED=true
SONARQUBE_URL=http://localhost:9000
SONARQUBE_TOKEN=tu-token
```

### 2. Sin Servidor (Local)

**Ventajas:**
- No requiere servidor
- Análisis rápido
- Sin configuración adicional

**Limitaciones:**
- Análisis básico del output del scanner
- Sin histórico
- Sin métricas avanzadas

**Configuración:**
```bash
SONARSCANNER_ENABLED=true
# No configurar SONARQUBE_URL ni SONARQUBE_TOKEN
```

### 3. Análisis Estático (Fallback)

Si SonarScanner CLI no está disponible, el sistema usa análisis estático con reglas simuladas.

## 🔍 Reglas de Análisis

El análisis detecta:

- **BLOCKER**: Vulnerabilidades críticas de seguridad
- **CRITICAL**: Bugs críticos y vulnerabilidades
- **MAJOR**: Bugs y code smells importantes
- **MINOR**: Code smells menores
- **INFO**: Información y sugerencias

### Criterios de Aprobación

El código pasa si:
- 0 issues BLOCKER
- ≤ 2 issues CRITICAL
- 0 BUGS

## 🐛 Troubleshooting

### Error: "SonarScanner CLI no encontrado"

**Solución:**
1. Verificar instalación:
   ```powershell
   sonar-scanner.bat --version
   ```

2. Si no funciona, especificar ruta completa en `.env`:
   ```bash
   SONARSCANNER_PATH=C:\sonar-scanner\sonar-scanner-6.2.1.4610-windows-x64\bin\sonar-scanner.bat
   ```

3. Reiniciar terminal/IDE para cargar nuevo PATH

### Error: "Timeout ejecutando SonarScanner CLI"

**Causas:**
- Análisis muy largo (>120s)
- Servidor SonarQube no responde

**Solución:**
- Reducir tamaño del código a analizar
- Verificar que servidor SonarQube esté activo
- Usar análisis local sin servidor

### Error: "No se pudo obtener issues de SonarQube"

**Causas:**
- Token inválido
- Servidor no accesible
- Project key incorrecto

**Solución:**
1. Verificar servidor: `http://localhost:9000`
2. Verificar token en SonarQube
3. Revisar logs para más detalles

## 📝 Logs

Los logs del análisis se guardan en:
- `output/3_sonarqube_report_req{N}_sq{M}.txt` - Reporte de issues
- `output/3_sonarqube_instrucciones_req{N}_sq{M}.txt` - Instrucciones de corrección

## 🔄 Desactivar SonarScanner CLI

Para volver al análisis estático:

```bash
SONARSCANNER_ENABLED=false
```

O simplemente comentar la línea en `.env`:
```bash
# SONARSCANNER_ENABLED=true
```

## 📚 Referencias

- [SonarScanner CLI Documentation](https://docs.sonarsource.com/sonarqube/latest/analyzing-source-code/scanners/sonarscanner/)
- [SonarQube Documentation](https://docs.sonarsource.com/sonarqube/latest/)
- [SonarCloud](https://sonarcloud.io/)
