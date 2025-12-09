# Integración de SonarQube con el Sistema Multiagente

## 📋 Descripción General

La integración de SonarQube añade una capa de análisis estático de calidad de código entre el **Codificador** y el **Probador/Depurador**. Esto permite detectar y corregir problemas de calidad, seguridad y mantenibilidad antes de realizar las pruebas funcionales.

## 🏗️ Arquitectura

### Flujo Actualizado

```
Codificador → AnalizadorSonarQube → ProbadorDepurador
                    ↓ (issues)
                Codificador (con feedback)
```

### Componentes Nuevos

1. **`tools/sonarqube_mcp.py`**: Herramienta de integración con SonarQube MCP
2. **`agents/analizador_sonarqube.py`**: Agente que orquesta el análisis de calidad
3. **Campos en AgentState**: 
   - `sonarqube_issues`: Reporte de issues encontrados
   - `sonarqube_passed`: Estado del análisis
   - `sonarqube_attempt_count`: Contador de intentos
   - `max_sonarqube_attempts`: Límite de correcciones

## 🔍 Análisis de Calidad

### Tipos de Issues Detectados

#### 1. **BLOCKER** (Crítico - Debe corregirse)
- Vulnerabilidades de seguridad críticas
- Bugs que causan fallos en tiempo de ejecución
- Credenciales hardcodeadas

#### 2. **CRITICAL** (Alto - Debe corregirse)
- Bugs severos
- Problemas de seguridad importantes
- Complejidad ciclomática excesiva

#### 3. **MAJOR** (Medio - Recomendado)
- Problemas de mantenibilidad significativos
- Code smells importantes

#### 4. **MINOR** (Bajo - Opcional)
- Mejoras de estilo
- Líneas muy largas

#### 5. **INFO** (Informativo)
- TODOs y FIXMEs
- Sugerencias generales

### Criterios de Aceptación

El código es **APROBADO** si cumple:
- ✅ 0 issues BLOCKER
- ✅ Máximo 2 issues CRITICAL

De lo contrario, vuelve al Codificador con instrucciones de corrección.

## 🔄 Bucle de Calidad

### Funcionamiento

1. **Codificador** genera código
2. **AnalizadorSonarQube** analiza el código:
   - Guarda código temporalmente
   - Ejecuta análisis SonarQube
   - Genera reporte formateado
   - Evalúa criterios de aceptación

3. **Si pasa**: Continúa a **ProbadorDepurador**
4. **Si falla**: 
   - LLM genera instrucciones de corrección detalladas
   - Vuelve a **Codificador** con feedback específico
   - Incrementa `sonarqube_attempt_count`

5. **Si excede límite**: Termina con `QUALITY_LIMIT_EXCEEDED`

### Límites Configurables

```python
# En src/config/settings.py
MAX_SONARQUBE_ATTEMPTS = 2  # Default: 2 intentos
```

## 📊 Reportes Generados

### Archivos de Salida

En el directorio `output/`:

1. **`3.5_sonarqube_report_req{X}_sq{Y}.txt`**
   - Reporte completo del análisis
   - Resumen por severidad y tipo
   - Detalles de issues críticos

2. **`3.5_sonarqube_instrucciones_req{X}_sq{Y}.txt`**
   - Instrucciones de corrección generadas por LLM
   - Soluciones específicas por issue
   - Código corregido sugerido

### Formato del Reporte

```
============================================================
📊 REPORTE DE ANÁLISIS SONARQUBE
============================================================

🔍 Total de issues encontrados: 5

📈 Por Severidad:
   🔴 BLOCKER:  1
   🟠 CRITICAL: 2
   🟡 MAJOR:    1
   🔵 MINOR:    1
   ⚪ INFO:     0

📊 Por Tipo:
   🐛 BUGS:             1
   🔒 VULNERABILITIES:  1
   💨 CODE SMELLS:      3
   🔥 SECURITY HOTSPOT: 0

============================================================
🚨 ISSUES CRÍTICOS Y BLOQUEANTES:
============================================================

[BLOCKER] Línea 42
Regla: python:S6437
Tipo: VULNERABILITY
Mensaje: No hardcodear credenciales sensibles en el código

[CRITICAL] Línea 78
Regla: python:S1067
Tipo: CODE_SMELL
Mensaje: Reducir el número de condiciones lógicas en esta expresión
```

## 🛠️ Herramientas MCP de SonarQube

### Integración Actual

La implementación actual incluye:

1. **Análisis estático básico** que simula SonarQube:
   - Detección de TODOs/FIXMEs
   - Complejidad de condiciones
   - Credenciales hardcodeadas
   - Líneas muy largas

2. **Interfaz preparada** para integración real con SonarQube MCP

### Futuras Mejoras

Para conectar con SonarQube real via MCP:

```python
# En tools/sonarqube_mcp.py, función _analizar_archivo_sonarqube()

# Usar las herramientas MCP de VS Code:
# - sonarqube_analyze_file(file_path)
# - sonarqube_list_potential_security_issues(file_path)

# Ejemplo de integración real:
issues = vscode_sonarqube_api.analyze_file(file_path)
security_issues = vscode_sonarqube_api.list_security_issues(file_path)
```

## 💡 Prompt Especializado

### ANALIZADOR_SONARQUBE

El prompt del agente está diseñado para:

1. **Interpretar reportes** de SonarQube
2. **Priorizar issues** por impacto
3. **Generar instrucciones claras** de corrección
4. **Proporcionar ejemplos** de código corregido
5. **Justificar correcciones** desde perspectiva de calidad

### Ejemplo de Output del Prompt

```
RESUMEN EJECUTIVO
=================
Total issues: 3 (1 BLOCKER, 2 CRITICAL)

CORRECCIONES REQUERIDAS
=======================

1. [BLOCKER] Línea 15: Credencial hardcodeada
   
   Problema: Se detectó "api_key = 'abc123'" en el código
   
   Solución: Usar variables de entorno
   
   Código sugerido:
   ```python
   import os
   api_key = os.getenv('API_KEY')
   ```
   
   Justificación: Las credenciales en código fuente son vulnerabilidades
   de seguridad críticas que pueden exponerse en control de versiones.

2. [CRITICAL] Línea 42: Complejidad excesiva
   ...
```

## 🔧 Actualización del Codificador

### Manejo de Feedback de SonarQube

El **Codificador** ahora procesa dos tipos de feedback:

1. **Traceback** (errores de ejecución)
2. **sonarqube_issues** (problemas de calidad)

```python
# En agents/codificador.py

contexto_llm = f"Requisitos Formales: {state['requisitos_formales']}\n"

if state['traceback']:
    contexto_llm += f"\nTraceback: {state['traceback']}\n"

if state.get('sonarqube_issues'):
    contexto_llm += f"\nIssues SonarQube: {state['sonarqube_issues']}\n"
    contexto_llm += f"\nCódigo a corregir: {state['codigo_generado']}\n"
```

## 📝 Nomenclatura de Archivos

Los archivos generados incluyen tres contadores:

```
3_codificador_req{R}_debug{D}_sq{S}.py
```

Donde:
- **R**: Intento de requisito (ciclo externo)
- **D**: Intento de depuración (bucle probador-codificador)
- **S**: Intento de SonarQube (bucle calidad-codificador)

Ejemplos:
- `3_codificador_req0_debug0_sq0.py` - Primera generación
- `3_codificador_req0_debug0_sq1.py` - Primera corrección de calidad
- `3_codificador_req0_debug1_sq0.py` - Corrección de bug funcional

## 🎯 Beneficios de la Integración

### 1. **Detección Temprana**
- Issues de calidad detectados antes de pruebas funcionales
- Reduce iteraciones del bucle de depuración

### 2. **Código Más Seguro**
- Detecta vulnerabilidades de seguridad
- Previene credenciales expuestas

### 3. **Mejor Mantenibilidad**
- Code smells corregidos proactivamente
- Complejidad controlada desde el inicio

### 4. **Estándares Profesionales**
- Código que cumple estándares industriales
- Preparado para entornos corporativos

### 5. **Trazabilidad**
- Reportes detallados de cada análisis
- Instrucciones de corrección documentadas

## 🚀 Uso

### Ejecución Normal

El análisis SonarQube se ejecuta automáticamente:

```python
from src.main import run_development_workflow

prompt = "Crea una función para validar emails"
final_state = run_development_workflow(prompt)
```

### Verificar Resultados

```python
if final_state:
    print(f"SonarQube aprobado: {final_state['sonarqube_passed']}")
    print(f"Intentos de corrección: {final_state['sonarqube_attempt_count']}")
    
    # Ver reportes en output/
    # - 3.5_sonarqube_report_*.txt
    # - 3.5_sonarqube_instrucciones_*.txt
```

### Ajustar Límites

```python
# En src/config/settings.py
class Settings:
    MAX_SONARQUBE_ATTEMPTS = 3  # Aumentar límite
```

## 🔬 Testing

### Script de Prueba

```bash
python test_sonarqube_integration.py
```

Este script:
1. Genera código con posibles issues
2. Ejecuta el flujo completo con SonarQube
3. Muestra métricas de calidad

### Casos de Prueba Sugeridos

1. **Código con vulnerabilidades**: Credenciales hardcodeadas
2. **Complejidad alta**: Muchas condiciones anidadas
3. **Code smells**: TODOs sin resolver
4. **Código limpio**: Debe pasar en primer intento

## 📚 Referencias

- [SonarQube Rules](https://rules.sonarsource.com/)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [VS Code SonarQube Extension](https://marketplace.visualstudio.com/items?itemName=SonarSource.sonarlint-vscode)

## 🤝 Contribuciones

Para mejorar la integración de SonarQube:

1. Conectar con SonarQube Server/Cloud real
2. Añadir más reglas de análisis estático
3. Implementar análisis incremental
4. Generar métricas de calidad históricas
