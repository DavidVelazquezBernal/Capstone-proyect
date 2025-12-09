# 🚀 Quick Start - SonarQube Integration

## ⚡ Inicio Rápido (5 minutos)

### 1. Verificar que todo está instalado
```bash
# Activar entorno virtual
.venv\Scripts\activate

# Verificar dependencias
pip list | findstr -i "langgraph google pydantic"
```

### 2. Probar la integración
```bash
# Ejecutar script de prueba
python test_sonarqube_integration.py
```

### 3. Ver resultados
```bash
# Abrir directorio de salida
explorer output\

# Buscar archivos:
# - 3.5_sonarqube_report_*.txt      → Reportes de análisis
# - 3.5_sonarqube_instrucciones_*.txt → Correcciones sugeridas
# - workflow_graph.png              → Diagrama del flujo
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
    print(f"📊 Intentos SQ: {final_state['sonarqube_attempt_count']}")
```

## 🎯 Qué Esperar

### Primera Ejecución
```
--- 1. 📝 Ingeniero Requisitos ---
--- 2. 📋 Product Owner ---
--- 3. 💻 Codificador ---
--- 3.5 🔍 Analizador SonarQube ---
   -> Analizando código con SonarQube...
   ✅ Código aprobado por SonarQube
--- 4.1 🧪 Probador/Depurador --- Generar casos de test
--- 4.2 🧪 Probador/Depurador --- Probar casos de test
--- 5. 👔 Stakeholder ---
   ✅ VALIDACIÓN FINAL: VALIDADO
```

### Con Correcciones de Calidad
```
--- 3. 💻 Codificador ---
--- 3.5 🔍 Analizador SonarQube ---
   ❌ Código rechazado por SonarQube - requiere correcciones
   -> Instrucciones de corrección generadas
   -> Intento de corrección SonarQube: 1/2

--- 3. 💻 Codificador ---
   -> Corrigiendo issues de calidad de código (SonarQube)
--- 3.5 🔍 Analizador SonarQube ---
   ✅ Código aprobado por SonarQube
[Continúa...]
```

## 📊 Archivos Generados

Después de cada ejecución, revisa `output/`:

```
output/
├── workflow_graph.png                          ← Diagrama visual
├── 1_ingeniero_requisitos_req0.txt
├── 2_product_owner_req0.json
├── 3_codificador_req0_debug0_sq0.py           ← Código inicial
├── 3.5_sonarqube_report_req0_sq0.txt          ← Reporte SQ
├── 3_codificador_req0_debug0_sq1.py           ← Código corregido (si hay issues)
├── 3.5_sonarqube_report_req0_sq1.txt          ← Segundo análisis
├── 3.5_sonarqube_instrucciones_req0_sq1.txt   ← Instrucciones de corrección
├── 4_probador_tests_req0_debug0.txt
├── 4_probador_resultado_req0_debug0.json
├── 5_stakeholder_validacion_req0.txt
└── codigo_final.py                             ← Código final aprobado
```

## 🔧 Configuración Rápida

### Ajustar límites de intentos
Edita `src/config/settings.py`:

```python
class Settings:
    MAX_ATTEMPTS = 1               # Ciclos completos
    MAX_DEBUG_ATTEMPTS = 3         # Bucle debug
    MAX_SONARQUBE_ATTEMPTS = 2     # Bucle calidad ← NUEVO
```

### Cambiar criterios de calidad
Edita `src/tools/sonarqube_mcp.py`:

```python
def es_codigo_aceptable(resultado):
    blocker_count = resultado['summary']['by_severity']['BLOCKER']
    critical_count = resultado['summary']['by_severity']['CRITICAL']
    
    # Personalizar criterios aquí
    if blocker_count > 0:
        return False
    if critical_count > 2:  # ← Cambiar este número
        return False
    
    return True
```

## 🎓 Casos de Prueba

### 1. Código Limpio (debe pasar directo)
```python
prompt = "Función que suma dos números"
```

### 2. Con Issues de Calidad
```python
prompt = """
Función que valide contraseñas con estas reglas:
- Mínimo 8 caracteres
- Al menos una mayúscula
- Al menos un número
Incluye la contraseña de prueba password='Test1234' en el código
"""
```
*Debería detectar credencial hardcodeada*

### 3. Con Complejidad Alta
```python
prompt = """
Función con muchas condiciones anidadas para 
clasificar un número según múltiples criterios
"""
```
*Debería detectar complejidad ciclomática*

## 🐛 Troubleshooting

### Error: "No module named 'models'"
```bash
# Ejecutar desde src/
cd src
python -c "from main import run_development_workflow; ..."

# O usar importación absoluta desde raíz
python -m src.main
```

### Error: "GEMINI_API_KEY not configured"
```bash
# Crear/editar .env en la raíz
echo GEMINI_API_KEY=tu_clave_aqui > .env
echo E2B_API_KEY=tu_clave_e2b >> .env
```

### No se genera el grafo PNG
```bash
# Instalar graphviz
# Windows: choco install graphviz
# O descargar desde https://graphviz.org/download/
```

## 📚 Documentación Completa

- **README.md** - Visión general del proyecto
- **SONARQUBE_INTEGRATION.md** - Detalles técnicos completos
- **FLOW_DIAGRAM.md** - Diagramas y flujos detallados
- **RESUMEN_IMPLEMENTACION.md** - Resumen ejecutivo
- **DOCUMENTACION.md** - Documentación original del proyecto

## 🎯 Próximos Pasos

1. ✅ Ejecuta `python test_sonarqube_integration.py`
2. ✅ Revisa los archivos en `output/`
3. ✅ Abre `workflow_graph.png` para ver el flujo visual
4. ✅ Lee `SONARQUBE_INTEGRATION.md` para detalles
5. ✅ Prueba con tus propios prompts

## 💡 Tips

- Los reportes de SonarQube son muy informativos - léelos para aprender
- Los archivos `_sq{N}` muestran la evolución del código
- El grafo visual ayuda a entender el flujo completo
- Ajusta los límites según tus necesidades

**¡Listo para usar! 🎉**
