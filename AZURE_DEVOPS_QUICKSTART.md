# 🚀 Guía Rápida: Integración con Azure DevOps

## ⚡ Quick Start (5 minutos)

### 1. Obtener Personal Access Token (PAT)

```
1. https://dev.azure.com/{tu-org}
2. Avatar (arriba derecha) → Personal Access Tokens
3. + New Token
4. Name: "Sistema-Multiagente"
   Scopes: Work Items (Read, write, & manage)
5. Create → COPIAR TOKEN
```

### 2. Configurar Variables de Entorno

```bash
# Copiar template
cp .env.example .env

# Editar .env
AZURE_DEVOPS_ENABLED=true
AZURE_DEVOPS_ORG=tu-organizacion
AZURE_DEVOPS_PROJECT=tu-proyecto
AZURE_DEVOPS_PAT=token-copiado-en-paso-1

# Opcional (rutas de organización)
AZURE_ITERATION_PATH=MiProyecto\\Sprint 1
AZURE_AREA_PATH=MiProyecto\\Backend
```

### 3. Probar Conexión

```bash
python test_azure_devops_connection.py
```

**✅ Salida esperada**:
```
✅ Conexión exitosa con Azure DevOps
✅ PBI creado exitosamente!
   • ID: #1234
   • URL: https://dev.azure.com/...
```

### 4. Ejecutar el Flujo Completo

```bash
python src/main.py
```

El **Product Owner** ahora creará automáticamente PBIs en Azure DevOps.

---

## 📋 Verificar Configuración

```python
# En Python
from src.config.settings import settings
print(f"Habilitado: {settings.AZURE_DEVOPS_ENABLED}")
print(f"Org: {settings.AZURE_DEVOPS_ORG}")
print(f"Proyecto: {settings.AZURE_DEVOPS_PROJECT}")
```

---

## 🔧 Troubleshooting

| Error | Solución |
|-------|----------|
| 401 Unauthorized | Verifica el PAT (puede estar expirado) |
| 404 Not Found | Verifica nombres de Org y Proyecto |
| Connection timeout | Verifica tu conexión a internet |
| PAT inválido | Regenera el token con permisos correctos |

---

## 📚 Documentación Completa

Ver: **[AZURE_DEVOPS_INTEGRATION.md](AZURE_DEVOPS_INTEGRATION.md)**

- API completa del cliente
- Ejemplos avanzados
- Campos soportados
- Seguridad y mejores prácticas

---

## 🎯 Flujo Automático

```
Usuario ejecuta main.py
    ↓
Ingeniero de Requisitos clarifica
    ↓
Product Owner formaliza requisitos
    ↓
🔷 [SI AZURE_DEVOPS_ENABLED=true]
    ├─ Estima Story Points
    ├─ Crea PBI en Azure DevOps
    ├─ Agrega URL al JSON
    └─ Continúa flujo normal
    ↓
Codificador genera código
    ↓
...resto del flujo...
```

---

## ✨ Características

- ✅ **Creación automática de PBIs** durante la formalización
- ✅ **Estimación inteligente** de Story Points
- ✅ **Trazabilidad completa** con URLs en los requisitos
- ✅ **Metadatos enriquecidos** (HTML, tags, prioridad)
- ✅ **Modo degradado** (funciona sin Azure si está deshabilitado)
- ✅ **Logging profesional** de todas las operaciones

---

## 💡 Ejemplo de PBI Generado

**Título**: `[AI-Generated] Función para validar emails`

**Descripción**:
```html
<h3>Objetivo Funcional</h3>
<p>Validar formato de correo electrónico usando regex</p>

<h3>Especificaciones Técnicas</h3>
<ul>
    <li><strong>Lenguaje:</strong> Python 3.10+</li>
    <li><strong>Función:</strong> <code>def validate_email(email: str) -> bool</code></li>
</ul>

<h3>Entradas Esperadas</h3>
<p>String con email a validar</p>

<h3>Salidas Esperadas</h3>
<p>Boolean: True si es válido, False si no</p>
```

**Criterios de Aceptación**:
```html
<ul>
    <li>✅ El código debe validar formato RFC 5322</li>
    <li>✅ Todos los tests unitarios deben pasar</li>
    <li>✅ Sin issues bloqueantes en SonarQube</li>
</ul>
```

**Metadatos**:
- Story Points: 2
- Tags: `AI-Generated; Multiagente; Python`
- Priority: Media
- State: New

---

## 🔐 Seguridad

- ⚠️ **NUNCA** commitees el archivo `.env`
- 🔄 Rota el PAT cada 30-90 días
- 🔒 Usa permisos mínimos necesarios
- 📝 Monitorea el uso del token en Azure DevOps

---

## 📞 Soporte

**Issues**: Abre un issue en GitHub con:
- Logs completos (con `LOG_LEVEL=DEBUG`)
- Configuración sanitizada (sin tokens)
- Mensaje de error específico

**Tests**: Ejecuta `test_azure_devops_connection.py` antes de reportar problemas.

---

**Última actualización**: Diciembre 2025  
**Versión**: 1.0.0
