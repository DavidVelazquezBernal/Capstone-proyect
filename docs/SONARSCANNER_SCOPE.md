# Configuración de Alcance de SonarScanner CLI

## 📋 Objetivo

Asegurar que SonarScanner CLI **solo analiza el código generado por el agente developer-code**, excluyendo:
- Archivos de otros agentes (product-owner, testing, etc.)
- Archivos temporales
- Reportes y logs
- Configuraciones del proyecto

## 🎯 Implementación

### 1. Configuración Global (`sonar-project.properties`)

El archivo de configuración principal incluye:

```properties
# Directorio de código fuente
sonar.sources=output

# Archivos a INCLUIR en el análisis (solo código del agente developer-code)
# Patrón: 2_developer_req*_debug*_sq*.{py,ts,js}
sonar.inclusions=**/2_developer_req*_debug*_sq*.*

# Archivos a excluir del análisis
sonar.exclusions=**/node_modules/**,**/.venv/**,**/venv/**,**/__pycache__/**,**/*.pyc,**/logs/**,**/.git/**,**/0_*.txt,**/1_*.txt,**/3_*.txt,**/4_*.txt,**/5_*.txt,**/temp_*.*,**/*.png,**/*.json
```

### 2. Análisis Temporal (SonarScanner CLI)

Cuando se ejecuta análisis temporal en `src/tools/sonarqube_mcp.py`, la configuración incluye:

```properties
sonar.inclusions={nombre_archivo}
```

Esto asegura que solo se analiza el archivo específico del developer-code.

## 📁 Patrón de Archivos del Developer-Code

El agente developer-code genera archivos con el siguiente patrón:

```
2_developer_req{N}_debug{M}_sq{K}.{ext}
```

Donde:
- `N` = número de requisito/intento
- `M` = número de intento de corrección de errores de ejecución
- `K` = número de intento de corrección de calidad (SonarQube)
- `ext` = extensión del lenguaje (.py, .ts, .js, etc.)

**Ejemplos:**
- `2_developer_req1_debug0_sq0.py`
- `2_developer_req2_debug1_sq0.ts`
- `2_developer_req1_debug0_sq2.js`

## 🚫 Archivos Excluidos

### Por Prefijo Numérico
- `0_*` - Peticiones iniciales del usuario
- `1_*` - Requisitos formales del product-owner
- `3_*` - Reportes de SonarQube
- `4_*` - Tests del developer-unit-tests
- `5_*` - Resultados de ejecución del testing-agent

### Por Patrón
- `temp_*.*` - Archivos temporales
- `**/*.png` - Imágenes (diagramas de flujo)
- `**/*.json` - Configuraciones (package.json, etc.)
- `**/node_modules/**` - Dependencias
- `**/__pycache__/**` - Cache de Python

## ⚙️ Configuraciones Válidas

### Opción 1: Solo SonarScanner CLI (sin SonarCloud)
```bash
SONARCLOUD_ENABLED=false
SONARSCANNER_ENABLED=true
SONARSCANNER_PATH=sonar-scanner.bat
```
**Resultado:** Análisis local con SonarScanner CLI

### Opción 2: Solo SonarCloud (sin SonarScanner CLI local)
```bash
SONARCLOUD_ENABLED=true
SONARCLOUD_TOKEN=squ_...
SONARCLOUD_ORGANIZATION=tu-org
SONARCLOUD_PROJECT_KEY=tu-proyecto
SONARSCANNER_ENABLED=false
```
**Resultado:** Análisis en la nube con SonarCloud

### Opción 3: Ambos habilitados (prioridad a SonarCloud)
```bash
SONARCLOUD_ENABLED=true
SONARCLOUD_TOKEN=squ_...
SONARSCANNER_ENABLED=true
SONARSCANNER_PATH=sonar-scanner.bat
```
**Resultado:** Intenta SonarCloud primero, fallback a SonarScanner CLI

### Opción 4: Ambos deshabilitados
```bash
SONARCLOUD_ENABLED=false
SONARSCANNER_ENABLED=false
```
**Resultado:** Análisis estático básico (fallback)

## ✅ Verificación

Para verificar que la configuración funciona correctamente:

1. **Listar archivos en output:**
   ```powershell
   Get-ChildItem output -Recurse -File | Select-Object Name
   ```

2. **Verificar que solo se analizan archivos del developer-code:**
   - Los archivos deben empezar con `2_developer_`
   - Deben incluir los contadores `req`, `debug`, y `sq`

3. **Ejecutar test de verificación:**
   ```powershell
   python src/test_ai/test_sonarscanner_without_sonarcloud.py
   ```

4. **Ejecutar análisis manual de prueba:**
   ```powershell
   sonar-scanner.bat -Dsonar.verbose=true
   ```

## 🔧 Mantenimiento

Si se agregan nuevos agentes o patrones de archivos:

1. Actualizar `sonar.inclusions` si cambia el patrón del developer-code
2. Actualizar `sonar.exclusions` para nuevos tipos de archivos a excluir
3. Documentar los cambios en este archivo

## 📚 Referencias

- Configuración principal: `sonar-project.properties`
- Implementación temporal: `src/tools/sonarqube_mcp.py` (línea 182)
- Agente developer-code: `src/agents/developer_code.py` (línea 85)
