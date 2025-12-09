# 🔧 Guía de Uso de SonarLint con el Sistema

## ✅ SonarLint Instalado

Tienes **SonarQube for IDE (SonarLint)** instalado en VS Code.

## 🎯 Cómo Funciona la Integración

### Estado Actual

El sistema usa **análisis estático básico** que simula reglas de SonarQube. Esto funciona sin necesidad de servidor SonarQube y es suficiente para:

✅ Detectar TODOs y FIXMEs  
✅ Identificar complejidad ciclomática alta  
✅ Encontrar credenciales hardcodeadas  
✅ Detectar líneas muy largas  

### Para Análisis Real con SonarLint

SonarLint **ya analiza tu código automáticamente** en VS Code. Los issues aparecen en:

1. **Panel de Problemas** (Ctrl+Shift+M)
2. **Subrayados en el editor**
3. **Sugerencias al pasar el mouse**

## 🚀 Usar SonarLint Manualmente

### Opción 1: Ver Issues en VS Code

```bash
# Abre el archivo generado
code output/3_codificador_req0_debug0_sq0.py

# Abre el panel de problemas
Ctrl+Shift+M

# Los issues de SonarLint aparecerán automáticamente
```

### Opción 2: Ejecutar Análisis Manual

```bash
# Click derecho en el archivo → "SonarLint: Analyze file"
# O usa el command palette:
Ctrl+Shift+P → "SonarLint: Analyze file"
```

### Opción 3: Ver Todos los Issues

```bash
# En el panel de problemas, filtra por "SonarLint"
# Verás issues clasificados por severidad:
# - 🔴 Blocker
# - 🟠 Critical  
# - 🟡 Major
# - 🔵 Minor
# - ⚪ Info
```

## 🔗 Conectar con SonarQube Server/Cloud

Si quieres análisis más profundo con reglas personalizadas:

### 1. Configurar Connected Mode

```bash
# Abrir configuración de SonarLint
Ctrl+Shift+P → "SonarLint: Open Settings"

# O click en el icono de SonarLint en la barra lateral
```

### 2. Conectar con tu Servidor

**Para SonarQube Server:**
```
1. Click en "Add SonarQube Connection"
2. URL: http://localhost:9000 (o tu servidor)
3. Token: Generar en User > My Account > Security > Generate Token
4. Project Key: tu-proyecto-key
```

**Para SonarCloud:**
```
1. Click en "Add SonarCloud Connection"
2. Organization Key: tu-organizacion
3. Token: Generar en sonarcloud.io/account/security
4. Project Key: tu-proyecto-key
```

### 3. Vincular Proyecto

```bash
# En VS Code:
Ctrl+Shift+P → "SonarLint: Bind to SonarQube or SonarCloud"

# Selecciona tu conexión y proyecto
```

## 📊 Análisis Automático en el Sistema

El sistema multiagente ya integra análisis de calidad:

```
Codificador → AnalizadorSonarQube → Probador
                    ↓
            Análisis estático básico
            (simula reglas de SonarQube)
```

### Archivos Generados

Después de cada análisis, revisa:

```
output/
├── 3.5_sonarqube_report_req0_sq0.txt          ← Reporte del análisis
├── 3.5_sonarqube_instrucciones_req0_sq1.txt   ← Instrucciones de corrección
└── 3_codificador_req0_debug0_sq1.py           ← Código corregido
```

## 🎓 Ejemplo de Flujo Completo

### 1. Ejecuta el sistema
```bash
python src/main.py
# o
python test_sonarqube_integration.py
```

### 2. Revisa el análisis
```bash
# Abre el reporte
code output/3.5_sonarqube_report_req0_sq0.txt
```

### 3. Ve el código corregido
```bash
# Si hubo issues, abre el código corregido
code output/3_codificador_req0_debug0_sq1.py
```

### 4. Análisis manual con SonarLint
```bash
# Abre el código final en VS Code
code output/codigo_final.py

# SonarLint lo analizará automáticamente
# Ve issues en Panel de Problemas (Ctrl+Shift+M)
```

## 🔍 Diferencias Entre Análisis

### Análisis Estático Básico (Sistema)
- ✅ Rápido y sin configuración
- ✅ Detecta problemas comunes
- ✅ Funciona sin servidor
- ❌ Reglas limitadas
- ❌ No personalizable

### SonarLint en VS Code
- ✅ Análisis profundo
- ✅ Muchas más reglas
- ✅ Actualizado constantemente
- ✅ Sugerencias de corrección
- ℹ️ Manual (no integrado en el workflow)

### SonarLint Connected Mode
- ✅ Todo lo de SonarLint
- ✅ Reglas personalizadas del equipo
- ✅ Sincronización con servidor
- ✅ Métricas históricas
- ⚠️ Requiere servidor SonarQube/Cloud

## 💡 Recomendación

**Para desarrollo rápido:**
- Usa el análisis estático básico integrado (actual)

**Para revisión manual:**
- Abre los archivos generados en VS Code
- SonarLint los analizará automáticamente

**Para proyectos en equipo:**
- Configura Connected Mode con tu servidor
- Usa reglas centralizadas

## 🚧 Integración Futura

Para integrar SonarLint **directamente** en el workflow automático, necesitarías:

1. **API de SonarQube Server/Cloud** (requiere servidor)
2. **Extensión con CLI** (no disponible actualmente)
3. **Parser de VS Code Problems** (complejo)

Por ahora, el análisis estático básico es la mejor opción para automatización.

## 📚 Recursos

- [Documentación SonarLint](https://www.sonarsource.com/products/sonarlint/)
- [Reglas de SonarQube](https://rules.sonarsource.com/)
- [Connected Mode Guide](https://docs.sonarsource.com/sonarlint/vs-code/team-features/connected-mode/)

---

**En resumen:** El sistema ya tiene análisis de calidad integrado. SonarLint en VS Code es un complemento excelente para revisión manual adicional.
