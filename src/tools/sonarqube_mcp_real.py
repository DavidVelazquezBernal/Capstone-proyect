"""
Ejemplo de integración directa con las herramientas MCP de SonarQube en VS Code.
Este archivo muestra cómo usar las herramientas nativas de SonarQube.
"""

from typing import Dict, List, Any


def analizar_con_sonarqube_real(file_path: str) -> Dict[str, Any]:
    """
    Ejemplo de uso de las herramientas MCP reales de SonarQube.
    
    Herramientas MCP disponibles en VS Code (desde GitHub Copilot):
    1. sonarqube_analyze_file(filePath: str)
    2. sonarqube_list_potential_security_issues(filePath: str)
    3. sonarqube_exclude_from_analysis(globPattern: str)
    4. sonarqube_setup_connected_mode(...)
    
    Args:
        file_path: Ruta al archivo a analizar
        
    Returns:
        Dict con issues encontrados
    """
    
    # ============================================================
    # MÉTODO 1: Usando las herramientas directamente desde Python
    # ============================================================
    # Las herramientas MCP están disponibles como funciones en el contexto
    # de ejecución de GitHub Copilot
    
    try:
        # NOTA: Estas llamadas funcionan cuando se ejecutan desde
        # el contexto de GitHub Copilot Agent en VS Code
        
        # 1. Analizar archivo
        # analysis = sonarqube_analyze_file(file_path)
        
        # 2. Obtener issues de seguridad
        # security = sonarqube_list_potential_security_issues(file_path)
        
        # 3. Procesar resultados
        # return {
        #     "success": True,
        #     "issues": analysis.get("issues", []) + security.get("issues", []),
        #     "summary": _generate_summary(analysis, security)
        # }
        
        pass
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "issues": []
        }


# ============================================================
# MÉTODO 2: Usando subprocess para llamar a VS Code CLI
# ============================================================

import subprocess
import json


def analizar_via_vscode_cli(file_path: str) -> Dict[str, Any]:
    """
    Analiza un archivo usando el CLI de VS Code con SonarLint.
    
    Requisito: Tener instalada la extensión SonarLint en VS Code
    """
    try:
        # Ejecutar análisis con SonarLint CLI
        # Nota: Esto requiere que SonarLint esté instalado y configurado
        result = subprocess.run(
            ["code", "--list-extensions"],
            capture_output=True,
            text=True
        )
        
        if "sonarlint-vscode" not in result.stdout.lower():
            return {
                "success": False,
                "error": "SonarLint no está instalado en VS Code",
                "issues": []
            }
        
        # Aquí se ejecutaría el análisis real
        # Por ahora, retornamos un placeholder
        return {
            "success": False,
            "error": "Análisis CLI no implementado - usar análisis básico",
            "issues": []
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "issues": []
        }


# ============================================================
# MÉTODO 3: Integración con SonarQube Server/Cloud via API
# ============================================================

import requests


def analizar_via_sonarqube_api(
    file_path: str,
    project_key: str,
    sonar_url: str = "http://localhost:9000",
    token: str = None
) -> Dict[str, Any]:
    """
    Analiza código usando la API REST de SonarQube Server/Cloud.
    
    Args:
        file_path: Archivo a analizar
        project_key: Clave del proyecto en SonarQube
        sonar_url: URL del servidor SonarQube
        token: Token de autenticación
        
    Returns:
        Dict con issues encontrados
    """
    try:
        # 1. Obtener issues del archivo
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        # Endpoint para obtener issues
        endpoint = f"{sonar_url}/api/issues/search"
        params = {
            "componentKeys": project_key,
            "resolved": "false",
            "statuses": "OPEN,CONFIRMED,REOPENED"
        }
        
        response = requests.get(endpoint, params=params, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        issues = data.get("issues", [])
        
        # 2. Filtrar issues del archivo específico
        file_issues = [
            issue for issue in issues
            if file_path in issue.get("component", "")
        ]
        
        # 3. Formatear issues
        formatted_issues = []
        for issue in file_issues:
            formatted_issues.append({
                "rule": issue.get("rule"),
                "severity": issue.get("severity"),
                "type": issue.get("type"),
                "message": issue.get("message"),
                "line": issue.get("line", 0),
                "component": issue.get("component")
            })
        
        return {
            "success": True,
            "issues": formatted_issues,
            "summary": {
                "total": len(formatted_issues)
            }
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Error de conexión con SonarQube: {str(e)}",
            "issues": []
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "issues": []
        }


# ============================================================
# INTEGRACIÓN RECOMENDADA
# ============================================================

def analizar_archivo_con_mejor_metodo_disponible(file_path: str) -> Dict[str, Any]:
    """
    Intenta analizar con el mejor método disponible en este orden:
    1. Herramientas MCP de VS Code (si están disponibles)
    2. API de SonarQube (si está configurado)
    3. Análisis estático básico (fallback)
    """
    
    # Método 1: Intentar con MCP
    try:
        result = analizar_con_sonarqube_real(file_path)
        if result.get("success"):
            return result
    except:
        pass
    
    # Método 2: Intentar con API de SonarQube
    # (requiere configuración en settings)
    try:
        from config.settings import settings
        if hasattr(settings, 'SONARQUBE_URL') and hasattr(settings, 'SONARQUBE_TOKEN'):
            result = analizar_via_sonarqube_api(
                file_path,
                settings.SONARQUBE_PROJECT_KEY,
                settings.SONARQUBE_URL,
                settings.SONARQUBE_TOKEN
            )
            if result.get("success"):
                return result
    except:
        pass
    
    # Método 3: Fallback a análisis básico
    from tools.sonarqube_mcp import _analisis_estatico_basico
    return {
        "success": True,
        "issues": _analisis_estatico_basico(file_path),
        "summary": {"total": 0},
        "method": "basic_static_analysis"
    }


# ============================================================
# CONFIGURACIÓN PARA USAR SONARQUBE REAL
# ============================================================

"""
Para usar SonarQube real, añade a src/config/settings.py:

class Settings:
    # ... configuración existente ...
    
    # SonarQube Configuration
    SONARQUBE_URL: str = os.getenv("SONARQUBE_URL", "http://localhost:9000")
    SONARQUBE_TOKEN: str = os.getenv("SONARQUBE_TOKEN", "")
    SONARQUBE_PROJECT_KEY: str = os.getenv("SONARQUBE_PROJECT_KEY", "")

Y en tu archivo .env:

SONARQUBE_URL=https://sonarcloud.io  # o tu servidor
SONARQUBE_TOKEN=squ_your_token_here
SONARQUBE_PROJECT_KEY=your-project-key
"""
