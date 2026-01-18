# 🚀 Quick Start - Sistema Multiagente

## ⚡ Inicio Rápido (5 minutos)

### 1. Verificar que todo está instalado
```bash
# Activar entorno virtual
.venv\Scripts\activate

# Verificar dependencias principales
pip list | findstr -i "langgraph google pydantic"

# Instalar vitest para tests de TypeScript (en directorio output/)
cd output
npm install -D vitest
cd ..

# pytest ya debería estar instalado con requirements.txt
```

### 2. Configurar variables de entorno
```bash
# Copiar archivo de ejemplo
copy .env.example .env

# Editar .env y agregar tu API key:
# - GEMINI_API_KEY (requerida)
# - Otras opcionales (SonarQube, Azure DevOps, GitHub, SonarCloud)
```

### 3. Ejecutar el sistema
```bash
# Ejecutar con prompt interactivo
python src/main.py
```

### 4. Ver resultados
```bash
# Abrir directorio de salida
explorer output\

# Buscar archivos generados:
# - 1_product_owner_req*.json           → Requisitos formales
# - 2_desarrollador_req*_debug*_sq*.ts  → Código generado
# - 3_sonarqube_report_req*_sq*.txt     → Reportes de calidad
# - unit_tests_req*_sq*.test.ts         → Tests unitarios
# - 4_testing_req*_debug*_[PASSED|FAILED].txt → Resultados de tests
# - 6_stakeholder_validacion_req*.txt   → Validación final
# - codigo_final.ts                     → Código final aprobado
# - workflow_graph.png                  → Diagrama del flujo
```

## 📋 Ejemplo de Uso

```python
from src.main import run_development_workflow

# Prompt simple
prompt = "Crea una función para calcular el factorial de un número"

# Ejecutar
final_state = run_development_workflow(prompt)

# Ver resultados
if final_state:
    print(f"✅ Validado: {final_state['validado']}")
    print(f"✅ SonarQube: {final_state['sonarqube_passed']}")
    print(f"✅ Tests: {final_state['pruebas_superadas']}")
    print(f"📊 Intentos Calidad: {final_state['sonarqube_attempt_count']}")
    print(f"📊 Intentos Debug: {final_state['debug_attempt_count']}")
    if final_state.get('azure_pbi_id'):
        print(f"🔷 PBI Azure DevOps: #{final_state['azure_pbi_id']}")
```

## 🎯 Qué Esperar

### Primera Ejecución
```
--- 1. 📋 Product Owner ---
   ✅ Requisitos formalizados
   🔷 PBI creado en Azure DevOps (si está habilitado)
--- 2. 💻 Desarrollador ---
   ✅ Código generado
   🔷 Tasks creadas en Azure DevOps (si está habilitado)
--- 3. 🔍 Analizador SonarQube ---
   -> Analizando código con SonarQube...
   ✅ Código aprobado por SonarQube
--- 4. 🧪 Developer-UnitTests ---
   ✅ Tests unitarios generados y ejecutados
   -> Ejecutando tests con vitest/pytest...
   ✅ Tests pasados (40/40)
--- 5. �‍💻 Developer2-Reviewer ---
   ✅ Código revisado y aprobado
--- 6. 📝 Developer-CompletePR ---
   ✅ PR completado en GitHub (si está habilitado)
--- 7. 👔 Stakeholder ---
   ✅ VALIDACIÓN FINAL: VALIDADO
   📎 Código final adjuntado a Azure DevOps (si está habilitado)
```

### Con Correcciones de Calidad
```
--- 1. 📋 Product Owner ---
--- 2. 💻 Desarrollador ---
--- 3. 🔍 Analizador SonarQube ---
   ❌ Código rechazado por SonarQube - requiere correcciones
   -> Instrucciones de corrección generadas
   -> Intento de corrección SonarQube: 1/3

--- 2. 💻 Desarrollador ---
   -> Corrigiendo issues de calidad de código (SonarQube)
--- 3. 🔍 Analizador SonarQube ---
   ✅ Código aprobado por SonarQube
--- 4. 🧪 Developer-UnitTests ---
   ✅ Tests pasados
--- 5. 👨‍💻 Developer2-Reviewer ---
   ✅ Código aprobado
--- 6. 📝 Developer-CompletePR ---
--- 7. 👔 Stakeholder ---
   ✅ VALIDADO
```

## 📊 Archivos Generados

Después de cada ejecución, revisa `output/`:

```
output/
├── workflow_graph.png                          ← Diagrama visual del flujo
├── 1_product_owner_req0.json                   ← Requisitos formales
├── 2_desarrollador_req0_debug0_sq0.ts          ← Código inicial
├── 3_sonarqube_report_req0_sq0.txt             ← Reporte de calidad
├── 2_desarrollador_req0_debug0_sq1.ts          ← Código corregido (si hay issues)
├── 3_sonarqube_report_req0_sq1.txt             ← Segundo análisis
├── 3_sonarqube_instrucciones_req0_sq1.txt      ← Instrucciones de corrección
├── unit_tests_req0_sq1.test.ts                 ← Tests unitarios generados
├── 4_testing_req0_debug0_PASSED.txt            ← Resultado de tests
├── 5_reviewer_feedback_req0.txt                ← Feedback del revisor (si aplica)
├── 6_stakeholder_validacion_req0.txt           ← Validación final
└── codigo_final.ts                             ← Código final aprobado
```

## � Bucles de Corrección

El sistema tiene **3 bucles de corrección automática** que mejoran iterativamente el código:

### 1. Bucle de Calidad (Sonar ↔ Developer-Code)
- **Trigger**: Código con issues críticos de SonarQube
- **Límite**: `MAX_SONARQUBE_ATTEMPTS` (default: 3)
- **Proceso**: 
  1. Sonar analiza código con sonar-scanner.bat
  2. Si detecta issues BLOCKER/CRITICAL → genera instrucciones
  3. Developer-Code corrige según instrucciones
  4. Vuelve a Sonar para nuevo análisis

### 2. Bucle de Debug (Developer-UnitTests ↔ Developer-Code)
- **Trigger**: Tests unitarios fallan
- **Límite**: `MAX_DEBUG_ATTEMPTS` (default: 3)
- **Proceso**:
  1. Developer-UnitTests ejecuta tests con vitest/pytest
  2. Si fallan → captura traceback
  3. Developer-Code corrige basándose en el error
  4. Vuelve a Sonar → Developer-UnitTests

### 3. Bucle de Revisión (Developer2-Reviewer ↔ Developer-Code)
- **Trigger**: Revisor rechaza el código
- **Límite**: `MAX_REVISOR_ATTEMPTS` (default: 2)
- **Proceso**:
  1. Developer2-Reviewer analiza diseño y arquitectura
  2. Si rechaza → genera feedback detallado
  3. Developer-Code aplica mejoras
  4. Vuelve a Sonar → Developer-UnitTests → Developer2-Reviewer

**Importante**: Cada corrección pasa por **Sonar nuevamente**, garantizando que las correcciones no introducen nuevos problemas de calidad.

## �🔧 Configuración Rápida

### Ajustar límites de intentos
Edita `src/config/settings.py`:

```python
class Settings:
    MAX_ATTEMPTS = 1               # Ciclos completos (Product Owner → Stakeholder)
    MAX_DEBUG_ATTEMPTS = 3         # Bucle debug (Developer-UnitTests ↔ Developer-Code)
    MAX_SONARQUBE_ATTEMPTS = 3     # Bucle calidad (Sonar ↔ Developer-Code)
    MAX_REVISOR_ATTEMPTS = 2       # Bucle revisión (Developer2-Reviewer ↔ Developer-Code)
    LOG_LEVEL = "INFO"             # Nivel de logging
    LOG_TO_FILE = True             # Guardar logs en archivo
```

### Habilitar integración con Azure DevOps
Edita `.env`:

```env
AZURE_DEVOPS_ENABLED=true
AZURE_DEVOPS_ORG=tu-organizacion
AZURE_DEVOPS_PROJECT=tu-proyecto
AZURE_DEVOPS_PAT=tu-personal-access-token
AZURE_ITERATION_PATH=MiProyecto\Sprint 1
AZURE_AREA_PATH=MiProyecto\Backend
```

### Habilitar integración con GitHub
Edita `.env`:

```env
GITHUB_ENABLED=true
GITHUB_TOKEN=ghp_tu-token-aqui
GITHUB_OWNER=tu-usuario-u-organizacion
GITHUB_REPO=nombre-del-repositorio
GITHUB_BASE_BRANCH=main
GITHUB_REPO_PATH=C:\ruta\al\repositorio
```

### Habilitar SonarCloud
Edita `.env`:

```env
SONARCLOUD_ENABLED=true
SONARCLOUD_TOKEN=squ_tu-token-aqui
SONARCLOUD_ORGANIZATION=tu-organizacion
SONARCLOUD_PROJECT_KEY=usuario_nombre-repo
```

## 🎓 Casos de Prueba

### 1. Código Limpio (debe pasar directo)
```python
prompt = "Crea una función en TypeScript que sume dos números"
```

### 2. Con Issues de Calidad
```python
prompt = """
Crea una función en Python que valide contraseñas con estas reglas:
- Mínimo 8 caracteres
- Al menos una mayúscula
- Al menos un número
"""
```
*Puede detectar issues de complejidad o seguridad*

### 3. Con Tests Complejos
```python
prompt = """
Crea una clase Calculator en TypeScript con métodos:
- add(a, b)
- subtract(a, b)
- multiply(a, b)
- divide(a, b) - debe manejar división por cero
"""
```
*Generará tests completos con casos edge*

## 🐛 Troubleshooting

### Error: "GEMINI_API_KEY not configured"
```bash
# Crear/editar .env en la raíz del proyecto
echo GEMINI_API_KEY=tu_clave_aqui > .env
```

### Error: "vitest not found"
```bash
# Instalar vitest en directorio output/
cd output
npm install -D vitest
cd ..
```

### Error: "pytest not found"
```bash
# Instalar pytest
pip install pytest
```

### No se genera el grafo PNG
```bash
# Instalar graphviz
# Windows: choco install graphviz
# O descargar desde https://graphviz.org/download/
```

## 📚 Documentación Completa

- **README.md** - Visión general del proyecto
- **DOCUMENTACION.md** - Arquitectura técnica completa
- **FLOW_DIAGRAM.md** - Diagramas y flujos detallados
- **IMPLEMENTACION_ADJUNTOS_AZURE.md** - Integración con Azure DevOps
- **IMPLEMENTACION_GENERADOR_TESTS.md** - Generación de tests unitarios

## 🎯 Próximos Pasos

1. ✅ Configura `.env` con tus API keys
2. ✅ Ejecuta `python src/main.py`
3. ✅ Revisa los archivos en `output/`
4. ✅ Abre `workflow_graph.png` para ver el flujo visual
5. ✅ Prueba con tus propios prompts
6. ✅ (Opcional) Habilita Azure DevOps para integración completa

## 💡 Tips

- Los reportes de SonarQube son muy informativos - léelos para aprender
- Los archivos `_sq{N}` muestran la evolución del código con correcciones de calidad
- Los archivos `_debug{N}` muestran la evolución con correcciones de bugs
- El grafo visual (`workflow_graph.png`) ayuda a entender el flujo completo
- Los tests generados son ejecutables manualmente para debugging
- Ajusta los límites en `src/config/settings.py` según tus necesidades
- Revisa los logs en `output/` para debugging detallado

**¡Listo para usar! 🎉**
