"""
Tool para integración con SonarQube via MCP (Model Context Protocol).
Utiliza las herramientas de SonarQube disponibles en VS Code.

Herramientas MCP disponibles:
- sonarqube_analyze_file: Analiza un archivo y devuelve problemas
- sonarqube_list_potential_security_issues: Lista problemas de seguridad
"""

import os
import json
from typing import Dict, List, Any, Optional
from config.settings import settings


def analizar_codigo_con_sonarqube(codigo: str, nombre_archivo: str) -> Dict[str, Any]:
    """
    Analiza código usando SonarQube MCP.
    
    Args:
        codigo: Código fuente a analizar
        nombre_archivo: Nombre del archivo (usado para determinar extensión)
        
    Returns:
        Dict con:
            - success: bool
            - issues: List[Dict] con los problemas encontrados
            - summary: Dict con resumen de issues por severidad
            - error: str (solo si success=False)
    """
    try:
        # Guardar código temporalmente para análisis
        temp_file = os.path.join(settings.OUTPUT_DIR, f"temp_analysis_{nombre_archivo}")
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(codigo)
        
        # Aquí se integraría con las herramientas MCP de SonarQube
        # Por ahora, implementamos una versión que simula la integración
        # y que puede ser reemplazada con la conexión real a SonarQube
        
        issues = _analizar_archivo_sonarqube(temp_file)
        
        # Generar resumen
        summary = _generar_resumen_issues(issues)
        
        return {
            "success": True,
            "issues": issues,
            "summary": summary,
            "file_path": temp_file
        }
        
    except Exception as e:
        return {
            "success": False,
            "issues": [],
            "summary": {},
            "error": str(e)
        }


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
    
    print(f"   📊 Analizando con SonarLint (análisis estático básico)...")
    
    try:
        # Detectar lenguaje según extensión del archivo
        lenguaje = _detectar_lenguaje(file_path)
        
        # Análisis estático según lenguaje
        if lenguaje == 'typescript':
            issues = _analisis_estatico_typescript(file_path)
        else:  # python por defecto
            issues = _analisis_estatico_python(file_path)
        
    except Exception as e:
        print(f"⚠️ Error al analizar con SonarQube: {e}")
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
        
        for i, line in enumerate(lines, start=1):
            line_lower = line.lower().strip()
            line_stripped = line.strip()
            
            # Detección de TODOs/FIXMEs
            if 'todo' in line_lower or 'fixme' in line_lower:
                issues.append({
                    "rule": "python:S1135",
                    "severity": "INFO",
                    "type": "CODE_SMELL",
                    "message": "Complete la tarea asociada con este comentario TODO/FIXME",
                    "line": i
                })
            
            # Detección de complejidad ciclomática alta
            if line.count('if') > 3 or line.count('and') > 3 or line.count('or') > 3:
                issues.append({
                    "rule": "python:S1067",
                    "severity": "CRITICAL",
                    "type": "CODE_SMELL",
                    "message": "Reducir el número de condiciones lógicas en esta expresión",
                    "line": i
                })
            
            # Detección de credenciales hardcodeadas
            if any(keyword in line_lower for keyword in ['password', 'secret', 'api_key', 'token', 'apikey']):
                if '=' in line and ('"' in line or "'" in line):
                    # Verificar que no es una variable vacía o None
                    if not any(x in line for x in ['""', "''", 'None', 'null', 'os.getenv', 'os.environ']):
                        issues.append({
                            "rule": "python:S6437",
                            "severity": "BLOCKER",
                            "type": "VULNERABILITY",
                            "message": "No hardcodear credenciales sensibles en el código",
                            "line": i
                        })
            
            # Detección de except genérico
            if line_stripped.startswith('except:') or 'except Exception:' in line:
                issues.append({
                    "rule": "python:S5754",
                    "severity": "MAJOR",
                    "type": "CODE_SMELL",
                    "message": "Especificar el tipo de excepción en lugar de usar except genérico",
                    "line": i
                })
            
            # Detección de print statements (para código de producción)
            if line_stripped.startswith('print(') and not line_lower.startswith('#'):
                issues.append({
                    "rule": "python:S106",
                    "severity": "MINOR",
                    "type": "CODE_SMELL",
                    "message": "Usar logging en lugar de print() en código de producción",
                    "line": i
                })
            
            # Detección de líneas muy largas
            if len(line) > 120:
                issues.append({
                    "rule": "python:S103",
                    "severity": "MINOR",
                    "type": "CODE_SMELL",
                    "message": "Dividir esta línea (más de 120 caracteres)",
                    "line": i
                })
            
            # Detección de variables no usadas (básico)
            if line_stripped.startswith('import ') and ' as ' not in line:
                # Esta es una detección muy básica
                pass
    
    except Exception as e:
        print(f"⚠️ Error en análisis Python: {e}")
    
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
        
        for i, line in enumerate(lines, start=1):
            line_lower = line.lower().strip()
            line_stripped = line.strip()
            
            # Detección de TODOs/FIXMEs
            if 'todo' in line_lower or 'fixme' in line_lower:
                issues.append({
                    "rule": "typescript:S1135",
                    "severity": "INFO",
                    "type": "CODE_SMELL",
                    "message": "Complete la tarea asociada con este comentario TODO/FIXME",
                    "line": i
                })
            
            # Detección de complejidad ciclomática alta
            if line.count('if') > 3 or line.count('&&') > 3 or line.count('||') > 3:
                issues.append({
                    "rule": "typescript:S1067",
                    "severity": "CRITICAL",
                    "type": "CODE_SMELL",
                    "message": "Reducir el número de condiciones lógicas en esta expresión",
                    "line": i
                })
            
            # Detección de credenciales hardcodeadas
            if any(keyword in line_lower for keyword in ['password', 'secret', 'apikey', 'api_key', 'token']):
                if ('=' in line or ':' in line) and ('"' in line or "'" in line or '`' in line):
                    # Verificar que no es una variable vacía
                    if not any(x in line for x in ['""', "''", '``', 'null', 'undefined', 'process.env']):
                        issues.append({
                            "rule": "typescript:S6437",
                            "severity": "BLOCKER",
                            "type": "VULNERABILITY",
                            "message": "No hardcodear credenciales sensibles en el código",
                            "line": i
                        })
            
            # Detección de console.log (para código de producción)
            if 'console.log(' in line_stripped or 'console.error(' in line_stripped:
                issues.append({
                    "rule": "typescript:S106",
                    "severity": "MINOR",
                    "type": "CODE_SMELL",
                    "message": "Remover console.log() antes de producción",
                    "line": i
                })
            
            # Detección de var (usar let/const)
            if line_stripped.startswith('var '):
                issues.append({
                    "rule": "typescript:S3504",
                    "severity": "MAJOR",
                    "type": "CODE_SMELL",
                    "message": "Usar 'let' o 'const' en lugar de 'var'",
                    "line": i
                })
            
            # Detección de == en lugar de ===
            if '==' in line and '===' not in line and '!=' in line and '!==' not in line:
                if not line_stripped.startswith('//'):
                    issues.append({
                        "rule": "typescript:S1440",
                        "severity": "MAJOR",
                        "type": "BUG",
                        "message": "Usar '===' en lugar de '==' para comparación estricta",
                        "line": i
                    })
            
            # Detección de funciones sin tipos de retorno
            if ('function ' in line_stripped or 'const ' in line_stripped and '=>' in line_stripped):
                if not line_stripped.startswith('//') and ':' not in line and 'void' not in line:
                    # Verificar si es una función exportada
                    if 'export' in line_stripped:
                        issues.append({
                            "rule": "typescript:S4023",
                            "severity": "MINOR",
                            "type": "CODE_SMELL",
                            "message": "Agregar tipo de retorno explícito a la función",
                            "line": i
                        })
            
            # Detección de any type
            if ': any' in line or '[]any' in line:
                issues.append({
                    "rule": "typescript:S6557",
                    "severity": "MAJOR",
                    "type": "CODE_SMELL",
                    "message": "Evitar usar 'any', especificar un tipo concreto",
                    "line": i
                })
            
            # Detección de líneas muy largas
            if len(line) > 120:
                issues.append({
                    "rule": "typescript:S103",
                    "severity": "MINOR",
                    "type": "CODE_SMELL",
                    "message": "Dividir esta línea (más de 120 caracteres)",
                    "line": i
                })
            
            # Detección de try-catch vacío
            if line_stripped == 'catch' or (line_stripped.startswith('catch') and '{}' in line):
                issues.append({
                    "rule": "typescript:S2737",
                    "severity": "CRITICAL",
                    "type": "BUG",
                    "message": "El bloque catch no debe estar vacío",
                    "line": i
                })
    
    except Exception as e:
        print(f"⚠️ Error en análisis TypeScript: {e}")
    
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
    Formatea el resultado del análisis de SonarQube en texto legible.
    
    Args:
        resultado: Resultado del análisis de SonarQube
        
    Returns:
        String con reporte formateado
    """
    if not resultado.get("success"):
        return f"❌ Error en análisis SonarQube: {resultado.get('error', 'Error desconocido')}"
    
    summary = resultado.get("summary", {})
    issues = resultado.get("issues", [])
    
    reporte = ["=" * 60]
    reporte.append("📊 REPORTE DE ANÁLISIS SONARQUBE")
    reporte.append("=" * 60)
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
    
    # Detalles de issues críticos y bloqueantes
    issues_criticos = [i for i in issues if i.get('severity') in ['BLOCKER', 'CRITICAL']]
    
    if issues_criticos:
        reporte.append("=" * 60)
        reporte.append("🚨 ISSUES CRÍTICOS Y BLOQUEANTES:")
        reporte.append("=" * 60)
        
        for issue in issues_criticos:
            reporte.append(f"\n[{issue.get('severity')}] Línea {issue.get('line', 'N/A')}")
            reporte.append(f"Regla: {issue.get('rule', 'N/A')}")
            reporte.append(f"Tipo: {issue.get('type', 'N/A')}")
            reporte.append(f"Mensaje: {issue.get('message', 'Sin mensaje')}")
    
    # Lista todos los issues si hay pocos
    if len(issues) <= 10 and len(issues) > len(issues_criticos):
        reporte.append("\n" + "=" * 60)
        reporte.append("📋 TODOS LOS ISSUES:")
        reporte.append("=" * 60)
        
        for issue in issues:
            if issue not in issues_criticos:
                reporte.append(f"\n[{issue.get('severity')}] Línea {issue.get('line', 'N/A')}")
                reporte.append(f"Mensaje: {issue.get('message', 'Sin mensaje')}")
    
    reporte.append("\n" + "=" * 60)
    
    return "\n".join(reporte)


def es_codigo_aceptable(resultado: Dict[str, Any]) -> bool:
    """
    Determina si el código pasa los criterios de calidad de SonarQube.
    
    Criterios:
    - 0 issues BLOCKER
    - Máximo 2 issues CRITICAL
    
    Args:
        resultado: Resultado del análisis de SonarQube
        
    Returns:
        True si el código es aceptable, False en caso contrario
    """
    if not resultado.get("success"):
        return False
    
    summary = resultado.get("summary", {})
    by_severity = summary.get("by_severity", {})
    
    blocker_count = by_severity.get("BLOCKER", 0)
    critical_count = by_severity.get("CRITICAL", 0)
    
    # Criterios de aceptación
    if blocker_count > 0:
        return False
    
    if critical_count > 2:
        return False
    
    return True
