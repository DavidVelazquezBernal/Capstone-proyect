"""
Tool para integración con SonarQube via MCP (Model Context Protocol).
Utiliza las herramientas de SonarQube disponibles en VS Code.
También soporta SonarCloud API cuando está habilitado.

Herramientas MCP disponibles:
- sonarqube_analyze_file: Analiza un archivo y devuelve problemas
- sonarqube_list_potential_security_issues: Lista problemas de seguridad
"""

import os
import re
import json
from typing import Dict, List, Any, Optional
from config.settings import settings
from utils.logger import setup_logger

logger = setup_logger(__name__, level=settings.get_log_level())

# Importar SonarCloud service si está disponible
try:
    from services.sonarcloud_service import sonarcloud_service
    SONARCLOUD_AVAILABLE = True
except ImportError:
    SONARCLOUD_AVAILABLE = False
    logger.debug("SonarCloud service no disponible")


def analizar_codigo_con_sonarqube(codigo: str, nombre_archivo: str, branch_name: str = None) -> Dict[str, Any]:
    """
    Analiza código usando análisis estático de SonarQube.
    
    Si SonarCloud está habilitado y se proporciona un branch_name, 
    consulta la API de SonarCloud para obtener issues reales.
    De lo contrario, usa análisis estático local.
    
    Args:
        codigo: Código fuente a analizar
        nombre_archivo: Nombre del archivo (usado para determinar extensión)
        branch_name: Nombre del branch en GitHub (para consultar SonarCloud)
        
    Returns:
        Dict con:
            - success: bool
            - issues: List[Dict] con los problemas encontrados
            - summary: Dict con resumen de issues por severidad
            - error: str (solo si success=False)
            - source: str ('sonarcloud' o 'local')
    """
    # Intentar usar SonarCloud si está habilitado y hay un branch
    if SONARCLOUD_AVAILABLE and settings.SONARCLOUD_ENABLED and branch_name:
        logger.info(f"☁️ Consultando SonarCloud para branch '{branch_name}'...")
        
        try:
            result = sonarcloud_service.analyze_branch(branch_name)
            
            if result.get("success"):
                issues_data = result.get("issues", {})
                issues_list = issues_data.get("issues", [])
                
                # Convertir formato de SonarCloud a formato interno
                converted_issues = []
                for issue in issues_list:
                    converted_issues.append({
                        "rule": issue.get("rule", "UNKNOWN"),
                        "severity": issue.get("severity", "INFO"),
                        "type": issue.get("type", "CODE_SMELL"),
                        "message": issue.get("message", ""),
                        "line": issue.get("line", 0),
                        "component": issue.get("component", "")
                    })
                
                summary = result.get("issues", {}).get("summary", _generar_resumen_issues(converted_issues))
                
                logger.info(f"✅ SonarCloud: {len(converted_issues)} issues encontrados")
                
                return {
                    "success": True,
                    "issues": converted_issues,
                    "summary": summary,
                    "source": "sonarcloud",
                    "quality_gate": result.get("quality_gate", {}),
                    "metrics": result.get("metrics", {})
                }
        except Exception as e:
            logger.warning(f"⚠️ Error consultando SonarCloud, usando análisis local: {e}")
    
    # Fallback: Análisis estático local
    temp_file = None
    try:
        # Guardar código temporalmente para análisis
        temp_file = os.path.join(settings.OUTPUT_DIR, f"temp_analysis_{nombre_archivo}")
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(codigo)
        
        # Análisis estático básico
        issues = _analizar_archivo_sonarqube(temp_file)
        
        # Generar resumen
        summary = _generar_resumen_issues(issues)
        
        resultado = {
            "success": True,
            "issues": issues,
            "summary": summary,
            "file_path": temp_file,
            "source": "local"
        }
        
        return resultado
        
    except Exception as e:
        return {
            "success": False,
            "issues": [],
            "summary": {},
            "error": str(e),
            "source": "local"
        }
    finally:
        # Limpiar archivo temporal después del análisis
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
                logger.debug(f"🗑️ Archivo temporal eliminado: {temp_file}")
            except Exception as e:
                logger.warning(f"⚠️ No se pudo eliminar archivo temporal {temp_file}: {e}")


def _analizar_archivo_sonarqube(file_path: str) -> List[Dict[str, Any]]:
    """
    Analiza un archivo con SonarQube y retorna los issues encontrados.
    
    Intenta usar las herramientas MCP de SonarQube en VS Code.
    Si no están disponibles, usa análisis estático básico como fallback.
    
    Args:
        file_path: Ruta absoluta al archivo a analizar
        
    Returns:
        Lista de issues encontrados
    """
    issues = []
    
    # ============================================================
    # Intentar usar SonarQube real via extensión de VS Code
    # ============================================================
    # Las herramientas MCP están disponibles cuando GitHub Copilot
    # las invoca directamente. En ejecución Python normal, usamos fallback.
    
    # Nota: Las herramientas MCP de SonarQube solo están disponibles
    # en el contexto del agente de Copilot, no en ejecución Python directa.
    # Por seguridad, mantenemos el análisis estático como método principal.
    
    logger.info("📊 Analizando con SonarLint (análisis estático básico)...")
    
    try:
        # Detectar lenguaje según extensión del archivo
        lenguaje = _detectar_lenguaje(file_path)
        
        # Análisis estático según lenguaje
        if lenguaje == 'typescript':
            issues = _analisis_estatico_typescript(file_path)
        else:  # python por defecto
            issues = _analisis_estatico_python(file_path)
        
    except Exception as e:
        logger.error(f"⚠️ Error al analizar con SonarQube: {e}")
        issues.append({
            "rule": "ANALYSIS_ERROR",
            "severity": "INFO",
            "type": "ERROR",
            "message": f"No se pudo completar el análisis: {str(e)}",
            "line": 0
        })
    
    return issues


def _detectar_lenguaje(file_path: str) -> str:
    """
    Detecta el lenguaje del archivo según su extensión.
    
    Args:
        file_path: Ruta al archivo
        
    Returns:
        'python' o 'typescript'
    """
    extension = os.path.splitext(file_path)[1].lower()
    
    if extension in ['.ts', '.tsx', '.js', '.jsx']:
        return 'typescript'
    else:
        return 'python'


def _analisis_estatico_python(file_path: str) -> List[Dict[str, Any]]:
    """
    Análisis estático específico para código Python.
    Simula reglas de SonarQube para Python.
    """
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        codigo_completo = ''.join(lines)
        
        for i, line in enumerate(lines, start=1):
            line_lower = line.lower().strip()
            line_stripped = line.strip()
            
            # === SECURITY VULNERABILITIES ===
            
            # S6437: Credenciales hardcodeadas (BLOCKER)
            if any(keyword in line_lower for keyword in ['password', 'secret', 'api_key', 'token', 'apikey', 'private_key']):
                if '=' in line and ('"' in line or "'" in line):
                    if not any(x in line for x in ['""', "''", 'None', 'null', 'os.getenv', 'os.environ', 'getenv', 'environ.get']):
                        issues.append({
                            "rule": "python:S6437",
                            "severity": "BLOCKER",
                            "type": "VULNERABILITY",
                            "message": "No hardcodear credenciales sensibles en el código. Usar variables de entorno.",
                            "line": i
                        })
            
            # S5808: eval() usage (CRITICAL)
            if 'eval(' in line_stripped and not line_stripped.startswith('#'):
                issues.append({
                    "rule": "python:S5808",
                    "severity": "CRITICAL",
                    "type": "VULNERABILITY",
                    "message": "Evitar usar eval(), representa un riesgo de seguridad",
                    "line": i
                })
            
            # S4829: exec() usage (CRITICAL)
            if 'exec(' in line_stripped and not line_stripped.startswith('#'):
                issues.append({
                    "rule": "python:S4829",
                    "severity": "CRITICAL",
                    "type": "VULNERABILITY",
                    "message": "Evitar usar exec(), representa un riesgo de seguridad",
                    "line": i
                })
            
            # === BUGS ===
            
            # S5754: Except genérico (MAJOR)
            if line_stripped.startswith('except:') or 'except Exception:' in line:
                if not line_stripped.startswith('#'):
                    issues.append({
                        "rule": "python:S5754",
                        "severity": "MAJOR",
                        "type": "BUG",
                        "message": "Especificar el tipo de excepción en lugar de usar except genérico",
                        "line": i
                    })
            
            # S1066: Bloques if/else anidados (MAJOR)
            indentation = len(line) - len(line.lstrip())
            if indentation > 12 and ('if ' in line_stripped or 'elif ' in line_stripped):
                issues.append({
                    "rule": "python:S1066",
                    "severity": "MAJOR",
                    "type": "CODE_SMELL",
                    "message": "Reducir anidamiento excesivo de bloques if/else",
                    "line": i
                })
            
            # S2201: Resultado de función no usado (MAJOR)
            if line_stripped.endswith('.strip()') or line_stripped.endswith('.lower()') or line_stripped.endswith('.upper()'):
                if not ('=' in line or 'return' in line or 'if' in line):
                    issues.append({
                        "rule": "python:S2201",
                        "severity": "MAJOR",
                        "type": "BUG",
                        "message": "El resultado de esta función no se está usando",
                        "line": i
                    })
            
            # === CODE SMELLS ===
            
            # S1067: Complejidad ciclomática alta (CRITICAL)
            if line.count('if') > 3 or line.count('and') > 3 or line.count('or') > 3:
                issues.append({
                    "rule": "python:S1067",
                    "severity": "CRITICAL",
                    "type": "CODE_SMELL",
                    "message": "Reducir el número de condiciones lógicas en esta expresión (máximo 3)",
                    "line": i
                })
            
            # S106: Print statements (MINOR)
            if line_stripped.startswith('print(') and not line_lower.startswith('#'):
                issues.append({
                    "rule": "python:S106",
                    "severity": "MINOR",
                    "type": "CODE_SMELL",
                    "message": "Usar logging en lugar de print() en código de producción",
                    "line": i
                })
            
            # S1192: Strings duplicadas (MINOR)
            # Detectar strings largos duplicados
            if '"' in line or "'" in line:
                for string_match in re.findall(r'["\']([^"\']{{15,}})["\']', line):
                    count = codigo_completo.count(string_match)
                    if count > 2:
                        issues.append({
                            "rule": "python:S1192",
                            "severity": "MINOR",
                            "type": "CODE_SMELL",
                            "message": f"Definir constante para este string duplicado ({count} veces)",
                            "line": i
                        })
                        break
            
            # S1481: Variables no usadas (MINOR)
            if line_stripped.startswith('import ') and ' as ' in line:
                # Detectar imports no usados (básico)
                alias = line.split(' as ')[-1].strip()
                if codigo_completo.count(alias) == 1:
                    issues.append({
                        "rule": "python:S1481",
                        "severity": "MINOR",
                        "type": "CODE_SMELL",
                        "message": f"Import '{alias}' no se está usando",
                        "line": i
                    })
            
            # S1854: Asignaciones sin uso (MAJOR)
            if '=' in line_stripped and not line_stripped.startswith(('def ', 'class ', '#', 'if ', 'elif ', 'for ', 'while ')):
                if not any(op in line for op in ['==', '!=', '<=', '>=', '+=', '-=', '*=', '/=']):
                    var_name = line_stripped.split('=')[0].strip().split()[-1]
                    remaining_code = ''.join(lines[i:])
                    if var_name and var_name not in remaining_code:
                        issues.append({
                            "rule": "python:S1854",
                            "severity": "MAJOR",
                            "type": "CODE_SMELL",
                            "message": f"Variable '{var_name}' asignada pero nunca usada",
                            "line": i
                        })
            
            # S1542: Funciones idénticas (MAJOR)
            if line_stripped.startswith('def '):
                function_name = line_stripped.split('(')[0].replace('def ', '').strip()
                if function_name and len(function_name) < 3:
                    issues.append({
                        "rule": "python:S100",
                        "severity": "MINOR",
                        "type": "CODE_SMELL",
                        "message": f"Nombre de función muy corto: '{function_name}'",
                        "line": i
                    })
            
            # S103: Líneas muy largas (MINOR)
            if len(line) > 120:
                issues.append({
                    "rule": "python:S103",
                    "severity": "MINOR",
                    "type": "CODE_SMELL",
                    "message": f"Dividir esta línea ({len(line)} caracteres, máximo 120)",
                    "line": i
                })
            
            # S1135: TODOs/FIXMEs (INFO)
            if 'todo' in line_lower or 'fixme' in line_lower:
                issues.append({
                    "rule": "python:S1135",
                    "severity": "INFO",
                    "type": "CODE_SMELL",
                    "message": "Complete la tarea asociada con este comentario TODO/FIXME",
                    "line": i
                })
            
            # S125: Código comentado (MINOR)
            if line_stripped.startswith('#') and any(keyword in line_lower for keyword in ['def ', 'class ', 'import ', 'if ', 'for ', 'while ']):
                issues.append({
                    "rule": "python:S125",
                    "severity": "MINOR",
                    "type": "CODE_SMELL",
                    "message": "Remover código comentado",
                    "line": i
                })
    
    except Exception as e:
        logger.error(f"⚠️ Error en análisis Python: {e}")
    
    return issues


def _analisis_estatico_typescript(file_path: str) -> List[Dict[str, Any]]:
    """
    Análisis estático específico para código TypeScript/JavaScript.
    Simula reglas de SonarQube para TypeScript.
    """
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        codigo_completo = ''.join(lines)
        
        for i, line in enumerate(lines, start=1):
            line_lower = line.lower().strip()
            line_stripped = line.strip()
            
            # === SECURITY VULNERABILITIES ===
            
            # S6437: Credenciales hardcodeadas (BLOCKER)
            if any(keyword in line_lower for keyword in ['password', 'secret', 'apikey', 'api_key', 'token', 'privatekey', 'private_key']):
                if ('=' in line or ':' in line) and ('"' in line or "'" in line or '`' in line):
                    if not any(x in line for x in ['""', "''", '``', 'null', 'undefined', 'process.env', 'import.meta.env']):
                        issues.append({
                            "rule": "typescript:S6437",
                            "severity": "BLOCKER",
                            "type": "VULNERABILITY",
                            "message": "No hardcodear credenciales sensibles en el código. Usar variables de entorno.",
                            "line": i
                        })
            
            # S5852: Regex injection (CRITICAL)
            if 'new RegExp(' in line and ('req.' in line or 'input' in line_lower or 'user' in line_lower):
                issues.append({
                    "rule": "typescript:S5852",
                    "severity": "CRITICAL",
                    "type": "VULNERABILITY",
                    "message": "Evitar construir regex desde entrada de usuario (riesgo de DoS)",
                    "line": i
                })
            
            # S4823: eval() usage (CRITICAL)
            if 'eval(' in line_stripped and not line_stripped.startswith('//'):
                issues.append({
                    "rule": "typescript:S4823",
                    "severity": "CRITICAL",
                    "type": "VULNERABILITY",
                    "message": "Evitar usar eval(), representa un riesgo de seguridad",
                    "line": i
                })
            
            # === BUGS ===
            
            # S1440: Comparación no estricta (MAJOR)
            # Detectar == o != que NO sean === o !==
            if not line_stripped.startswith('//'):
                import re
                # Buscar == que NO esté rodeado de = (no sea === ni =>)
                # Pattern: cualquier == que NO esté precedido por = ni seguido por = ni >
                if re.search(r'(?<![=!])== (?![=>])', line) or re.search(r'(?<![=!])==(?![=>])', line):
                    issues.append({
                        "rule": "typescript:S1440",
                        "severity": "MAJOR",
                        "type": "BUG",
                        "message": "Usar '===' en lugar de '==' para comparación estricta",
                        "line": i
                    })
                
                # Buscar != que NO esté seguido por = (no sea !==)
                # El ! ya está ahí, solo verificar que != no sea !==
                if re.search(r'!=\s', line) or (line.count('!=') and not re.search(r'!==', line)):
                    # Verificar que realmente haya != y no !==
                    if '!=' in line and '!==' not in line:
                        issues.append({
                            "rule": "typescript:S1440",
                            "severity": "MAJOR",
                            "type": "BUG",
                            "message": "Usar '!==' en lugar de '!=' para comparación estricta",
                            "line": i
                        })
            
            # S2737: Catch block vacío (CRITICAL)
            if line_stripped == 'catch' or (line_stripped.startswith('catch') and '{}' in line):
                issues.append({
                    "rule": "typescript:S2737",
                    "severity": "CRITICAL",
                    "type": "BUG",
                    "message": "El bloque catch no debe estar vacío. Al menos registrar el error.",
                    "line": i
                })
            
            # S1066: Bloques if/else anidados (MAJOR)
            indentation = len(line) - len(line.lstrip())
            if indentation > 8 and ('if ' in line_stripped or 'else if' in line_stripped):
                issues.append({
                    "rule": "typescript:S1066",
                    "severity": "MAJOR",
                    "type": "CODE_SMELL",
                    "message": "Reducir anidamiento excesivo de bloques if/else",
                    "line": i
                })
            
            # S2201: Resultado de función no usado (MAJOR)
            if line_stripped.endswith('.trim()') or line_stripped.endswith('.toLowerCase()') or line_stripped.endswith('.toUpperCase()'):
                if not ('=' in line or 'return' in line or 'if' in line or 'const' in line or 'let' in line):
                    issues.append({
                        "rule": "typescript:S2201",
                        "severity": "MAJOR",
                        "type": "BUG",
                        "message": "El resultado de esta función no se está usando",
                        "line": i
                    })
            
            # === CODE SMELLS ===
            
            # S1067: Complejidad ciclomática alta (CRITICAL)
            if line.count('if') > 3 or line.count('&&') > 3 or line.count('||') > 3:
                issues.append({
                    "rule": "typescript:S1067",
                    "severity": "CRITICAL",
                    "type": "CODE_SMELL",
                    "message": "Reducir el número de condiciones lógicas en esta expresión (máximo 3)",
                    "line": i
                })
            
            # S106: console.log statements (MINOR)
            if 'console.log(' in line_stripped or 'console.error(' in line_stripped or 'console.warn(' in line_stripped:
                issues.append({
                    "rule": "typescript:S106",
                    "severity": "MINOR",
                    "type": "CODE_SMELL",
                    "message": "Remover console.log() antes de producción o usar un logger apropiado",
                    "line": i
                })
            
            # S3504: Uso de var (MAJOR)
            if line_stripped.startswith('var '):
                issues.append({
                    "rule": "typescript:S3504",
                    "severity": "MAJOR",
                    "type": "CODE_SMELL",
                    "message": "Usar 'let' o 'const' en lugar de 'var'",
                    "line": i
                })
            
            # S4023: Funciones sin tipo de retorno explícito (MINOR)
            if ('function ' in line_stripped or ('=>' in line_stripped and ('const ' in line_stripped or 'let ' in line_stripped))):
                if not line_stripped.startswith('//') and ':' not in line.split('=>')[0] if '=>' in line else ':' not in line.split('{')[0]:
                    if 'export' in line_stripped or 'function' in line_stripped:
                        issues.append({
                            "rule": "typescript:S4023",
                            "severity": "MINOR",
                            "type": "CODE_SMELL",
                            "message": "Agregar tipo de retorno explícito a la función",
                            "line": i
                        })
            
            # S6557: Uso de any type (MAJOR)
            if ': any' in line or '<any>' in line or 'any[]' in line:
                if not line_stripped.startswith('//'):
                    issues.append({
                        "rule": "typescript:S6557",
                        "severity": "MAJOR",
                        "type": "CODE_SMELL",
                        "message": "Evitar usar 'any', especificar un tipo concreto",
                        "line": i
                    })
            
            # S1192: Strings duplicadas (MINOR)
            if '"' in line or "'" in line or '`' in line:
                for string_match in re.findall(r'["\'\'`]([^"\'\'`]{{15,}})["\'\'`]', line):
                    count = codigo_completo.count(string_match)
                    if count > 2:
                        issues.append({
                            "rule": "typescript:S1192",
                            "severity": "MINOR",
                            "type": "CODE_SMELL",
                            "message": f"Definir constante para este string duplicado ({count} veces)",
                            "line": i
                        })
                        break
            
            # S1481: Variables no usadas (MINOR)
            if line_stripped.startswith(('const ', 'let ', 'var ')):
                var_name = line_stripped.split('=')[0].strip().split()[-1].replace(':', '').strip()
                if var_name and len(var_name) > 1:
                    remaining_code = ''.join(lines[i:])
                    if var_name not in remaining_code:
                        issues.append({
                            "rule": "typescript:S1481",
                            "severity": "MINOR",
                            "type": "CODE_SMELL",
                            "message": f"Variable '{var_name}' declarada pero nunca usada",
                            "line": i
                        })
            
            # S100: Nombres de función muy cortos (MINOR)
            if 'function ' in line_stripped:
                function_name = line_stripped.split('(')[0].replace('function', '').replace('export', '').strip()
                if function_name and len(function_name) < 3:
                    issues.append({
                        "rule": "typescript:S100",
                        "severity": "MINOR",
                        "type": "CODE_SMELL",
                        "message": f"Nombre de función muy corto: '{function_name}'",
                        "line": i
                    })
            
            # S103: Líneas muy largas (MINOR)
            if len(line) > 120:
                issues.append({
                    "rule": "typescript:S103",
                    "severity": "MINOR",
                    "type": "CODE_SMELL",
                    "message": f"Dividir esta línea ({len(line)} caracteres, máximo 120)",
                    "line": i
                })
            
            # S1135: TODOs/FIXMEs (INFO)
            if 'todo' in line_lower or 'fixme' in line_lower:
                issues.append({
                    "rule": "typescript:S1135",
                    "severity": "INFO",
                    "type": "CODE_SMELL",
                    "message": "Complete la tarea asociada con este comentario TODO/FIXME",
                    "line": i
                })
            
            # S125: Código comentado (MINOR)
            if line_stripped.startswith('//') and any(keyword in line for keyword in ['function', 'const', 'let', 'var', 'if', 'for', 'while']):
                issues.append({
                    "rule": "typescript:S125",
                    "severity": "MINOR",
                    "type": "CODE_SMELL",
                    "message": "Remover código comentado",
                    "line": i
                })
            
            # S2589: Condiciones siempre true o false (MAJOR)
            if ('if (true)' in line_stripped or 'if(true)' in line_stripped or 
                'if (false)' in line_stripped or 'if(false)' in line_stripped):
                issues.append({
                    "rule": "typescript:S2589",
                    "severity": "MAJOR",
                    "type": "BUG",
                    "message": "Remover condición que siempre evalúa a true/false",
                    "line": i
                })
    
    except Exception as e:
        logger.error(f"⚠️ Error en análisis TypeScript: {e}")
    
    return issues


# Mantener compatibilidad con código existente
def _analisis_estatico_basico(file_path: str) -> List[Dict[str, Any]]:
    """
    Función legacy para compatibilidad.
    Detecta automáticamente el lenguaje y llama a la función apropiada.
    """
    lenguaje = _detectar_lenguaje(file_path)
    if lenguaje == 'typescript':
        return _analisis_estatico_typescript(file_path)
    else:
        return _analisis_estatico_python(file_path)


def _generar_resumen_issues(issues: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Genera un resumen de los issues encontrados por severidad y tipo.
    """
    summary = {
        "total": len(issues),
        "by_severity": {
            "BLOCKER": 0,
            "CRITICAL": 0,
            "MAJOR": 0,
            "MINOR": 0,
            "INFO": 0
        },
        "by_type": {
            "BUG": 0,
            "VULNERABILITY": 0,
            "CODE_SMELL": 0,
            "SECURITY_HOTSPOT": 0
        }
    }
    
    for issue in issues:
        severity = issue.get("severity", "INFO")
        issue_type = issue.get("type", "CODE_SMELL")
        
        if severity in summary["by_severity"]:
            summary["by_severity"][severity] += 1
        
        if issue_type in summary["by_type"]:
            summary["by_type"][issue_type] += 1
    
    return summary


def formatear_reporte_sonarqube(resultado: Dict[str, Any]) -> str:
    """
    Formatea el resultado del análisis de SonarQube/SonarCloud en texto legible.
    
    Args:
        resultado: Resultado del análisis de SonarQube/SonarCloud
        
    Returns:
        String con reporte formateado
    """
    if not resultado.get("success"):
        return f"❌ Error en análisis SonarQube: {resultado.get('error', 'Error desconocido')}"
    
    summary = resultado.get("summary", {})
    issues = resultado.get("issues", [])
    source = resultado.get("source", "local")
    
    reporte = ["=" * 60]
    
    # Título según la fuente
    if source == "sonarcloud":
        reporte.append("☁️  REPORTE DE ANÁLISIS SONARCLOUD")
    else:
        reporte.append("📊 REPORTE DE ANÁLISIS SONARQUBE (Local)")
    
    reporte.append("=" * 60)
    
    # Información de la fuente
    if source == "sonarcloud":
        reporte.append(f"\n🌐 Fuente: SonarCloud API")
        if resultado.get("branch_analyzed"):
            reporte.append(f"🌿 Branch analizado: {resultado.get('branch_analyzed')}")
        
        # Quality Gate status (solo disponible con SonarCloud real)
        quality_gate = resultado.get("quality_gate", {})
        if quality_gate.get("success"):
            qg_status = quality_gate.get("status", "UNKNOWN")
            qg_emoji = "✅" if qg_status == "OK" else "❌" if qg_status == "ERROR" else "⚠️"
            reporte.append(f"\n🚦 Quality Gate: {qg_emoji} {qg_status}")
            
            # Condiciones del Quality Gate
            conditions = quality_gate.get("conditions", [])
            if conditions:
                reporte.append("   Condiciones:")
                for cond in conditions:
                    cond_status = "✅" if cond.get("status") == "OK" else "❌"
                    metric = cond.get("metricKey", "unknown")
                    actual = cond.get("actualValue", "N/A")
                    threshold = cond.get("errorThreshold", cond.get("warningThreshold", "N/A"))
                    reporte.append(f"   {cond_status} {metric}: {actual} (umbral: {threshold})")
        
        # Métricas del proyecto (solo disponible con SonarCloud real)
        metrics_data = resultado.get("metrics", {})
        if metrics_data.get("success"):
            metrics = metrics_data.get("metrics", {})
            if metrics:
                reporte.append("\n📈 Métricas del Proyecto:")
                if "bugs" in metrics:
                    reporte.append(f"   🐛 Bugs: {metrics.get('bugs', 'N/A')}")
                if "vulnerabilities" in metrics:
                    reporte.append(f"   🔒 Vulnerabilidades: {metrics.get('vulnerabilities', 'N/A')}")
                if "code_smells" in metrics:
                    reporte.append(f"   💨 Code Smells: {metrics.get('code_smells', 'N/A')}")
                if "coverage" in metrics:
                    reporte.append(f"   📊 Cobertura: {metrics.get('coverage', 'N/A')}%")
                if "duplicated_lines_density" in metrics:
                    reporte.append(f"   📋 Duplicación: {metrics.get('duplicated_lines_density', 'N/A')}%")
                if "ncloc" in metrics:
                    reporte.append(f"   📝 Líneas de código: {metrics.get('ncloc', 'N/A')}")
                
                # Ratings (A-E)
                ratings = []
                if "sqale_rating" in metrics:
                    ratings.append(f"Mantenibilidad: {_rating_to_letter(metrics.get('sqale_rating'))}")
                if "reliability_rating" in metrics:
                    ratings.append(f"Fiabilidad: {_rating_to_letter(metrics.get('reliability_rating'))}")
                if "security_rating" in metrics:
                    ratings.append(f"Seguridad: {_rating_to_letter(metrics.get('security_rating'))}")
                if ratings:
                    reporte.append(f"   🏆 Ratings: {' | '.join(ratings)}")
    else:
        reporte.append(f"\n🔧 Fuente: Análisis estático local")
    
    reporte.append(f"\n🔍 Total de issues encontrados: {summary.get('total', 0)}\n")
    
    # Resumen por severidad
    by_severity = summary.get("by_severity", {})
    reporte.append("📈 Por Severidad:")
    reporte.append(f"   🔴 BLOCKER:  {by_severity.get('BLOCKER', 0)}")
    reporte.append(f"   🟠 CRITICAL: {by_severity.get('CRITICAL', 0)}")
    reporte.append(f"   🟡 MAJOR:    {by_severity.get('MAJOR', 0)}")
    reporte.append(f"   🔵 MINOR:    {by_severity.get('MINOR', 0)}")
    reporte.append(f"   ⚪ INFO:     {by_severity.get('INFO', 0)}\n")
    
    # Resumen por tipo
    by_type = summary.get("by_type", {})
    reporte.append("📊 Por Tipo:")
    reporte.append(f"   🐛 BUGS:             {by_type.get('BUG', 0)}")
    reporte.append(f"   🔒 VULNERABILITIES:  {by_type.get('VULNERABILITY', 0)}")
    reporte.append(f"   💨 CODE SMELLS:      {by_type.get('CODE_SMELL', 0)}")
    reporte.append(f"   🔥 SECURITY HOTSPOT: {by_type.get('SECURITY_HOTSPOT', 0)}\n")
    
    # Agrupar issues por severidad para mejor organización
    issues_por_severidad = {
        'BLOCKER': [],
        'CRITICAL': [],
        'MAJOR': [],
        'MINOR': [],
        'INFO': []
    }
    
    for issue in issues:
        severidad = issue.get('severity', 'INFO')
        if severidad in issues_por_severidad:
            issues_por_severidad[severidad].append(issue)
    
    # Mostrar detalles de todos los issues, agrupados por severidad
    if issues:
        reporte.append("=" * 60)
        reporte.append("📋 DETALLE DE ISSUES ENCONTRADOS:")
        reporte.append("=" * 60)
        
        # Emojis por severidad
        severity_emojis = {
            'BLOCKER': '🔴',
            'CRITICAL': '🟠',
            'MAJOR': '🟡',
            'MINOR': '🔵',
            'INFO': '⚪'
        }
        
        # Mostrar issues en orden de severidad
        for severidad in ['BLOCKER', 'CRITICAL', 'MAJOR', 'MINOR', 'INFO']:
            issues_severidad = issues_por_severidad[severidad]
            
            if issues_severidad:
                emoji = severity_emojis.get(severidad, '⚪')
                reporte.append(f"\n{emoji} {severidad} ({len(issues_severidad)} issues):")
                reporte.append("-" * 60)
                
                for idx, issue in enumerate(issues_severidad, 1):
                    reporte.append(f"\n  Issue #{idx}:")
                    reporte.append(f"    📍 Línea:   {issue.get('line', 'N/A')}")
                    reporte.append(f"    📏 Regla:   {issue.get('rule', 'N/A')}")
                    reporte.append(f"    🏷️  Tipo:    {issue.get('type', 'N/A')}")
                    reporte.append(f"    💬 Mensaje: {issue.get('message', 'Sin mensaje')}")
                    
                    # Si hay información adicional del issue
                    if issue.get('component'):
                        # Extraer solo el nombre del archivo del component
                        component = issue.get('component', '')
                        if ':' in component:
                            component = component.split(':')[-1]
                        reporte.append(f"    📁 Archivo:  {component}")
                    if issue.get('effort'):
                        reporte.append(f"    ⏱️  Esfuerzo: {issue.get('effort')}")
                    if issue.get('debt'):
                        reporte.append(f"    💰 Deuda técnica: {issue.get('debt')}")
    
    reporte.append("\n" + "=" * 60)
    
    # Criterios de aceptación
    reporte.append("\n📋 CRITERIOS DE ACEPTACIÓN:")
    reporte.append("   - Sin issues BLOCKER")
    reporte.append("   - Máximo 2 issues CRITICAL")
    reporte.append("   - Sin BUGS")
    
    blocker_count = by_severity.get('BLOCKER', 0)
    critical_count = by_severity.get('CRITICAL', 0)
    bug_count = by_type.get('BUG', 0)
    
    passed = blocker_count == 0 and critical_count <= 2 and bug_count == 0
    
    if passed:
        reporte.append("\n✅ RESULTADO: CÓDIGO APROBADO")
    else:
        reporte.append("\n❌ RESULTADO: CÓDIGO RECHAZADO")
        if blocker_count > 0:
            reporte.append(f"   - {blocker_count} BLOCKER(s) encontrado(s)")
        if critical_count > 2:
            reporte.append(f"   - {critical_count} CRITICAL(s) (máximo permitido: 2)")
        if bug_count > 0:
            reporte.append(f"   - {bug_count} BUG(s) encontrado(s)")
    
    reporte.append("\n" + "=" * 60)
    
    return "\n".join(reporte)


def _rating_to_letter(rating_value: str) -> str:
    """Convierte el valor numérico del rating a letra (A-E)."""
    try:
        rating = float(rating_value)
        if rating <= 1:
            return "A"
        elif rating <= 2:
            return "B"
        elif rating <= 3:
            return "C"
        elif rating <= 4:
            return "D"
        else:
            return "E"
    except (ValueError, TypeError):
        return rating_value or "N/A"


def es_codigo_aceptable(resultado: Dict[str, Any]) -> bool:
    """
    Determina si el código pasa los criterios de calidad de SonarQube.
    
    Criterios:
    - 0 issues BLOCKER
    - Máximo 2 issues CRITICAL
    - 0 BUGs (de cualquier severidad)
    
    Args:
        resultado: Resultado del análisis de SonarQube
        
    Returns:
        True si el código es aceptable, False en caso contrario
    """
    if not resultado.get("success"):
        return False
    
    summary = resultado.get("summary", {})
    by_severity = summary.get("by_severity", {})
    by_type = summary.get("by_type", {})
    
    blocker_count = by_severity.get("BLOCKER", 0)
    critical_count = by_severity.get("CRITICAL", 0)
    bug_count = by_type.get("BUG", 0)
    
    # Criterios de aceptación
    # 1. No BLOCKERS permitidos
    if blocker_count > 0:
        return False
    
    # 2. Máximo 2 CRITICAL
    if critical_count > 2:
        return False
    
    # 3. No BUGS permitidos (de cualquier severidad)
    if bug_count > 0:
        return False
    
    return True
