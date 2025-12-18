# Matriz de Configuración de Análisis de Calidad

## 🎯 Resumen

Este documento describe cómo se comporta el sistema de análisis de calidad según las diferentes combinaciones de configuración de `SONARCLOUD_ENABLED` y `SONARSCANNER_ENABLED`.

## 📊 Matriz de Comportamiento

| SONARCLOUD_ENABLED | SONARSCANNER_ENABLED | Comportamiento | Método de Análisis |
|-------------------|---------------------|----------------|-------------------|
| ✅ true | ✅ true | Intenta SonarCloud primero, fallback a SonarScanner CLI | SonarCloud → SonarScanner CLI → Estático |
| ✅ true | ❌ false | Solo SonarCloud, fallback a estático | SonarCloud → Estático |
| ❌ false | ✅ true | **Solo SonarScanner CLI local** | SonarScanner CLI → Estático |
| ❌ false | ❌ false | Omite análisis de calidad | Ninguno (pasa automáticamente) |

## 🔍 Detalles por Configuración

### 1️⃣ Ambos Habilitados (Recomendado para producción)

```bash
SONARCLOUD_ENABLED=true
SONARCLOUD_TOKEN=squ_...
SONARCLOUD_ORGANIZATION=tu-org
SONARCLOUD_PROJECT_KEY=tu-proyecto
SONARSCANNER_ENABLED=true
SONARSCANNER_PATH=sonar-scanner.bat
```

**Flujo:**
1. Si hay branch de GitHub → Intenta análisis con SonarCloud
2. Si SonarCloud falla o timeout → Fallback a SonarScanner CLI local
3. Si SonarScanner CLI falla → Fallback a análisis estático

**Ventajas:**
- Máxima cobertura de análisis
- Análisis en la nube cuando está disponible
- Fallback robusto para desarrollo local

### 2️⃣ Solo SonarCloud

```bash
SONARCLOUD_ENABLED=true
SONARCLOUD_TOKEN=squ_...
SONARCLOUD_ORGANIZATION=tu-org
SONARCLOUD_PROJECT_KEY=tu-proyecto
SONARSCANNER_ENABLED=false
```

**Flujo:**
1. Si hay branch de GitHub → Análisis con SonarCloud
2. Si no hay branch o falla → Fallback a análisis estático

**Ventajas:**
- Análisis centralizado en la nube
- Histórico y métricas persistentes
- No requiere instalación local de SonarScanner

**Desventajas:**
- Requiere push a GitHub para cada análisis
- Depende de conectividad a internet

### 3️⃣ Solo SonarScanner CLI (Requiere servidor SonarQube)

```bash
SONARCLOUD_ENABLED=false
SONARSCANNER_ENABLED=true
SONARSCANNER_PATH=sonar-scanner.bat
# REQUERIDO: Servidor SonarQube
SONARQUBE_URL=http://localhost:9000
SONARQUBE_TOKEN=tu-token-aqui
```

**⚠️ IMPORTANTE:** SonarScanner CLI **requiere** un servidor SonarQube (local o remoto) para funcionar. No puede ejecutarse en modo "standalone".

**Flujo:**
1. Análisis con SonarScanner CLI → Envía resultados al servidor SonarQube
2. Si no hay servidor o falla → Fallback a análisis estático

**Ventajas:**
- Análisis completo con todas las reglas de SonarQube
- No requiere push a GitHub
- Dashboard web en servidor SonarQube local

**Desventajas:**
- **Requiere servidor SonarQube corriendo** (local o remoto)
- Configuración adicional necesaria
- Sin servidor → Fallback automático a análisis estático

**Logs esperados:**
```
============================================================
🔧 ANÁLISIS CON SONARSCANNER CLI
============================================================
SonarCloud deshabilitado, usando SonarScanner CLI local
Archivo a analizar: 2_developer_req1_debug0_sq0.py
============================================================
```

### 4️⃣ Ambos Deshabilitados (Solo para testing)

```bash
SONARCLOUD_ENABLED=false
SONARSCANNER_ENABLED=false
```

**Flujo:**
1. Omite completamente el análisis de calidad
2. El código pasa automáticamente

**Logs esperados:**
```
⚠️ SONARCLOUD_ENABLED=false y SONARSCANNER_ENABLED=false: omitiendo análisis de calidad y continuando el flujo
```

**⚠️ Advertencia:** Solo usar en entornos de testing donde el análisis de calidad no es necesario.

## 🔄 Orden de Prioridad del Análisis

El sistema siempre intenta usar el método más completo disponible:

```
1. SonarCloud (si SONARCLOUD_ENABLED=true y hay branch)
   ↓ (si falla o no disponible)
2. SonarScanner CLI (si SONARSCANNER_ENABLED=true)
   ↓ (si falla o no disponible)
3. Análisis Estático Local (fallback final)
```

## 🎯 Alcance del Análisis

**Independientemente del método usado**, el análisis solo procesa:
- Archivos con patrón: `2_developer_req*_debug*_sq*.*`
- Código generado por el agente developer-code

Ver [SONARSCANNER_SCOPE.md](SONARSCANNER_SCOPE.md) para más detalles.

## 🧪 Testing

Para verificar que la configuración funciona correctamente:

```powershell
# Test específico para SONARCLOUD_ENABLED=false, SONARSCANNER_ENABLED=true
python src/test_ai/test_sonarscanner_without_sonarcloud.py
```

## 📝 Cambios Recientes

### ✅ Corrección Implementada (Diciembre 2025)

**Problema anterior:**
- Cuando `SONARCLOUD_ENABLED=false`, el sistema omitía **todo** análisis de calidad, incluso si `SONARSCANNER_ENABLED=true`

**Solución:**
- Modificado `src/agents/sonarqube.py` para verificar **ambas** configuraciones
- Ahora solo omite el análisis si **ambas** están en `false`
- SonarScanner CLI funciona correctamente cuando SonarCloud está deshabilitado

**Archivos modificados:**
- `src/agents/sonarqube.py` (líneas 29-40)
- `sonar-project.properties` (agregado `sonar.inclusions`)
- `src/tools/sonarqube_mcp.py` (línea 182)

## 📚 Referencias

- [SONARSCANNER_CLI.md](SONARSCANNER_CLI.md) - Guía completa de SonarScanner CLI
- [SONARSCANNER_SCOPE.md](SONARSCANNER_SCOPE.md) - Alcance del análisis
- `src/agents/sonarqube.py` - Implementación del agente
- `src/tools/sonarqube_mcp.py` - Lógica de análisis
