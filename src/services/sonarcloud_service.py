"""
Servicio centralizado para operaciones de SonarCloud.
Permite analizar código y obtener métricas de calidad via API REST.
"""

import requests
from typing import Optional, Dict, Any, List, Tuple
from config.settings import settings
from utils.logger import setup_logger

logger = setup_logger(__name__, level=settings.get_log_level())


class SonarCloudService:
    """
    Servicio de alto nivel para operaciones de SonarCloud.
    Encapsula la lógica de análisis de código y consulta de issues.
    """
    
    BASE_URL = "https://sonarcloud.io/api"
    
    def __init__(self):
        """Inicializa el servicio con las credenciales de SonarCloud."""
        self.enabled = settings.SONARCLOUD_ENABLED
        self.token = settings.SONARCLOUD_TOKEN
        self.organization = settings.SONARCLOUD_ORGANIZATION
        self.project_key = settings.SONARCLOUD_PROJECT_KEY
        self.headers = {}
        
        if self.enabled:
            if not self.token:
                logger.warning("⚠️ SONARCLOUD_TOKEN no configurado")
                self.enabled = False
            elif not self.organization:
                logger.warning("⚠️ SONARCLOUD_ORGANIZATION no configurado")
                self.enabled = False
            elif not self.project_key:
                logger.warning("⚠️ SONARCLOUD_PROJECT_KEY no configurado")
                self.enabled = False
            else:
                self.headers = {"Authorization": f"Bearer {self.token}"}
                # Verificar conexión con la API antes de confirmar inicialización
                if self._verify_connection():
                    logger.info(f"✅ SonarCloud Service inicializado para {self.organization}/{self.project_key}")
                else:
                    logger.warning(f"⚠️ SonarCloud configurado pero no se pudo verificar conexión con la API")
                    self.enabled = False
    
    def _verify_connection(self) -> bool:
        """
        Verifica la conexión con la API de SonarCloud.
        
        Returns:
            bool: True si la conexión es exitosa
        """
        try:
            url = f"{self.BASE_URL}/system/status"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                # Verificar también que el proyecto existe
                project_url = f"{self.BASE_URL}/components/show"
                project_params = {"component": self.project_key}
                project_response = requests.get(project_url, headers=self.headers, params=project_params, timeout=10)
                
                if project_response.status_code == 200:
                    return True
                else:
                    logger.warning(f"⚠️ Proyecto '{self.project_key}' no encontrado en SonarCloud")
                    return False
            else:
                logger.warning(f"⚠️ Error al conectar con SonarCloud API: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logger.warning(f"⚠️ Error de conexión con SonarCloud: {e}")
            return False
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None, max_retries: int = 3) -> Optional[Dict]:
        """
        Realiza una petición GET a la API de SonarCloud con retry automático.
        
        Args:
            endpoint: Endpoint de la API (sin base URL)
            params: Parámetros de la petición
            max_retries: Número máximo de reintentos
            
        Returns:
            Dict con la respuesta JSON o None si hay error
        """
        if not self.enabled:
            return None
        
        import time
        
        for attempt in range(1, max_retries + 1):
            try:
                url = f"{self.BASE_URL}/{endpoint}"
                response = requests.get(url, headers=self.headers, params=params, timeout=30)
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.Timeout as e:
                if attempt == max_retries:
                    logger.error(f"❌ Timeout en petición a SonarCloud después de {max_retries} intentos")
                    return None
                logger.warning(f"⚠️ Timeout en intento {attempt}/{max_retries}, reintentando...")
                time.sleep(2 ** attempt)
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code in [503, 504]:
                    if attempt == max_retries:
                        logger.error(f"❌ SonarCloud no disponible después de {max_retries} intentos")
                        return None
                    logger.warning(f"⚠️ SonarCloud no disponible (intento {attempt}/{max_retries}), reintentando...")
                    time.sleep(2 ** attempt)
                else:
                    logger.error(f"❌ Error HTTP en petición a SonarCloud: {e}")
                    return None
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ Error en petición a SonarCloud: {e}")
                return None
        
        return None
    
    def verify_github_integration(self) -> Dict[str, Any]:
        """
        Verifica que SonarCloud esté configurado para analizar el repositorio de GitHub.
        
        Returns:
            Dict con resultado de verificación
        """
        if not self.enabled:
            return {"success": False, "error": "SonarCloud no está habilitado"}
        
        try:
            # Verificar que el proyecto existe
            params = {"component": self.project_key}
            result = self._make_request("components/show", params)
            
            if not result:
                return {"success": False, "error": "Proyecto no encontrado en SonarCloud"}
            
            # Verificar que hay branches (indica que está conectado a GitHub)
            branches_result = self._make_request("project_branches/list", {"project": self.project_key})
            
            if not branches_result or not branches_result.get("branches"):
                return {
                    "success": False,
                    "error": "No hay branches en SonarCloud. Verifica la integración con GitHub.",
                    "hint": "Configura GitHub App en SonarCloud: https://sonarcloud.io/projects"
                }
            
            branches = branches_result.get("branches", [])
            logger.info(f"✅ SonarCloud integrado con GitHub - {len(branches)} branches encontrados")
            
            return {
                "success": True,
                "branches_count": len(branches),
                "branches": [b.get("name") for b in branches[:5]]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_issues(self, branch: str = None, severities: str = None) -> Dict[str, Any]:
        """
        Obtiene los issues del proyecto.
        
        Args:
            branch: Nombre del branch a analizar (opcional)
            severities: Filtro de severidades separadas por coma (ej: "BLOCKER,CRITICAL")
            
        Returns:
            Dict con issues y resumen
        """
        if not self.enabled:
            return {"success": False, "error": "SonarCloud no está habilitado", "issues": []}
        
        params = {
            "componentKeys": self.project_key,
            "resolved": "false",
            "ps": 100,  # page size
            "organization": self.organization
        }
        
        if branch:
            params["branch"] = branch
        
        if severities:
            params["severities"] = severities
        
        result = self._make_request("issues/search", params)
        
        if not result:
            return {"success": False, "error": "Error al obtener issues", "issues": []}
        
        issues = result.get("issues", [])
        
        # Generar resumen
        summary = self._generate_summary(issues)
        
        return {
            "success": True,
            "issues": issues,
            "summary": summary,
            "total": result.get("total", 0),
            "paging": result.get("paging", {})
        }
    
    def get_quality_gate_status(self, branch: str = None) -> Dict[str, Any]:
        """
        Obtiene el estado del Quality Gate del proyecto.
        
        Args:
            branch: Nombre del branch (opcional)
            
        Returns:
            Dict con estado del Quality Gate
        """
        if not self.enabled:
            return {"success": False, "error": "SonarCloud no está habilitado"}
        
        params = {
            "projectKey": self.project_key,
            "organization": self.organization
        }
        
        if branch:
            params["branch"] = branch
        
        result = self._make_request("qualitygates/project_status", params)
        
        if not result:
            return {"success": False, "error": "Error al obtener Quality Gate"}
        
        project_status = result.get("projectStatus", {})
        
        return {
            "success": True,
            "status": project_status.get("status", "UNKNOWN"),
            "conditions": project_status.get("conditions", []),
            "ignoredConditions": project_status.get("ignoredConditions", False)
        }
    
    def get_metrics(self, branch: str = None) -> Dict[str, Any]:
        """
        Obtiene métricas de calidad del proyecto.
        
        Args:
            branch: Nombre del branch (opcional)
            
        Returns:
            Dict con métricas del proyecto
        """
        if not self.enabled:
            return {"success": False, "error": "SonarCloud no está habilitado"}
        
        params = {
            "component": self.project_key,
            "metricKeys": "bugs,vulnerabilities,code_smells,coverage,duplicated_lines_density,ncloc,sqale_rating,reliability_rating,security_rating"
        }
        
        if branch:
            params["branch"] = branch
        
        result = self._make_request("measures/component", params)
        
        if not result:
            return {"success": False, "error": "Error al obtener métricas"}
        
        component = result.get("component", {})
        measures = component.get("measures", [])
        
        # Convertir a diccionario más usable
        metrics = {}
        for measure in measures:
            metrics[measure.get("metric")] = measure.get("value")
        
        return {
            "success": True,
            "metrics": metrics,
            "component": component.get("key"),
            "name": component.get("name")
        }
    
    def analyze_branch(self, branch_name: str, use_main_if_branch_not_found: bool = False) -> Dict[str, Any]:
        """
        Analiza un branch específico y retorna un reporte completo.
        
        Si el branch no existe aún en SonarCloud (404), puede usar el branch main
        como referencia o retornar que no hay datos disponibles.
        
        Args:
            branch_name: Nombre del branch a analizar
            use_main_if_branch_not_found: Si True, usa main si el branch no existe
            
        Returns:
            Dict con análisis completo del branch
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "SonarCloud no está habilitado",
                "passed": False
            }
        
        logger.info(f"🔍 Analizando branch '{branch_name}' en SonarCloud...")
        
        # Primero verificar si el branch existe en SonarCloud
        # Intentar obtener issues del branch específico
        issues_result = self.get_issues(branch=branch_name)
        
        # Si el branch no tiene datos (404 o sin issues), intentar con main
        branch_used = branch_name
        if not issues_result.get("success") or issues_result.get("total", 0) == 0:
            if use_main_if_branch_not_found:
                logger.info(f"⚠️ Branch '{branch_name}' no tiene análisis en SonarCloud, usando branch principal...")
                issues_result = self.get_issues(branch=None)  # Sin branch = default/main
                branch_used = "main (default)"
            else:
                return {
                    "success": False,
                    "error": f"Branch '{branch_name}' no tiene análisis disponible en SonarCloud",
                    "passed": False,
                    "branch_not_analyzed": True
                }
        
        # Obtener Quality Gate (sin branch específico si falló)
        qg_result = self.get_quality_gate_status(branch=branch_name if branch_used == branch_name else None)
        
        # Obtener métricas (sin branch específico si falló)
        metrics_result = self.get_metrics(branch=branch_name if branch_used == branch_name else None)
        
        # Determinar si pasa el análisis
        quality_gate_passed = qg_result.get("status") == "OK" if qg_result.get("success") else False
        
        # También verificar criterios propios si el QG no está disponible
        summary = issues_result.get("summary", {})
        by_severity = summary.get("by_severity", {})
        by_type = summary.get("by_type", {})
        
        blocker_count = by_severity.get("BLOCKER", 0)
        critical_count = by_severity.get("CRITICAL", 0)
        bug_count = by_type.get("BUG", 0)
        
        # Criterios de aceptación propios
        custom_passed = (blocker_count == 0 and critical_count <= 2 and bug_count == 0)
        
        passed = quality_gate_passed if qg_result.get("success") else custom_passed
        
        return {
            "success": True,
            "passed": passed,
            "branch_analyzed": branch_used,
            "quality_gate": qg_result,
            "issues": issues_result,
            "metrics": metrics_result,
            "summary": {
                "blocker_count": blocker_count,
                "critical_count": critical_count,
                "bug_count": bug_count,
                "total_issues": issues_result.get("total", 0)
            }
        }
    
    def _generate_summary(self, issues: List[Dict]) -> Dict[str, Any]:
        """
        Genera un resumen de los issues por severidad y tipo.
        
        Args:
            issues: Lista de issues de SonarCloud
            
        Returns:
            Dict con resumen
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
    
    def format_report(self, analysis_result: Dict[str, Any]) -> str:
        """
        Formatea el resultado del análisis en texto legible.
        
        Args:
            analysis_result: Resultado de analyze_branch()
            
        Returns:
            String con reporte formateado
        """
        if not analysis_result.get("success"):
            return f"❌ Error en análisis SonarCloud: {analysis_result.get('error', 'Error desconocido')}"
        
        lines = ["=" * 60]
        lines.append("📊 REPORTE DE ANÁLISIS SONARCLOUD")
        lines.append("=" * 60)
        
        # Estado general
        passed = analysis_result.get("passed", False)
        status_emoji = "✅" if passed else "❌"
        status_text = "APROBADO" if passed else "RECHAZADO"
        lines.append(f"\n{status_emoji} Estado: {status_text}\n")
        
        # Quality Gate
        qg = analysis_result.get("quality_gate", {})
        if qg.get("success"):
            qg_status = qg.get("status", "UNKNOWN")
            qg_emoji = "✅" if qg_status == "OK" else "❌"
            lines.append(f"🚦 Quality Gate: {qg_emoji} {qg_status}")
        
        # Resumen de issues
        summary = analysis_result.get("summary", {})
        lines.append(f"\n🔍 Total de issues: {summary.get('total_issues', 0)}")
        lines.append(f"   🔴 BLOCKER:  {summary.get('blocker_count', 0)}")
        lines.append(f"   🟠 CRITICAL: {summary.get('critical_count', 0)}")
        lines.append(f"   🐛 BUGS:     {summary.get('bug_count', 0)}")
        
        # Métricas
        metrics = analysis_result.get("metrics", {})
        if metrics.get("success"):
            m = metrics.get("metrics", {})
            lines.append("\n📈 Métricas:")
            if "coverage" in m:
                lines.append(f"   📊 Cobertura: {m.get('coverage', 'N/A')}%")
            if "duplicated_lines_density" in m:
                lines.append(f"   📋 Duplicación: {m.get('duplicated_lines_density', 'N/A')}%")
            if "ncloc" in m:
                lines.append(f"   📝 Líneas de código: {m.get('ncloc', 'N/A')}")
        
        # Detalle de issues críticos
        issues_data = analysis_result.get("issues", {})
        issues_list = issues_data.get("issues", [])
        
        critical_issues = [i for i in issues_list if i.get("severity") in ["BLOCKER", "CRITICAL"]]
        
        if critical_issues:
            lines.append("\n" + "=" * 60)
            lines.append("🚨 ISSUES CRÍTICOS:")
            lines.append("-" * 60)
            
            for idx, issue in enumerate(critical_issues[:10], 1):  # Máximo 10
                lines.append(f"\n  Issue #{idx}:")
                lines.append(f"    📍 Archivo: {issue.get('component', 'N/A').split(':')[-1]}")
                lines.append(f"    📏 Línea:   {issue.get('line', 'N/A')}")
                lines.append(f"    🏷️  Regla:   {issue.get('rule', 'N/A')}")
                lines.append(f"    ⚠️  Severidad: {issue.get('severity', 'N/A')}")
                lines.append(f"    💬 Mensaje: {issue.get('message', 'Sin mensaje')}")
        
        lines.append("\n" + "=" * 60)
        
        return "\n".join(lines)
    
    def wait_for_analysis(self, branch_name: str, max_attempts: int = 10, wait_seconds: int = 30, timeout: int = None) -> Dict[str, Any]:
        """
        Espera a que el análisis de SonarCloud termine para un branch.
        Usa polling exponencial adaptativo para optimizar tiempos de espera.
        
        SonarCloud analiza automáticamente cuando se hace push a GitHub.
        Esta función espera y verifica que el análisis esté disponible.
        
        Args:
            branch_name: Nombre del branch
            max_attempts: Número máximo de intentos (usado si timeout es None)
            wait_seconds: Segundos base entre intentos (usado si timeout es None)
            timeout: Timeout total en segundos (si se especifica, usa polling adaptativo)
            
        Returns:
            Dict con resultado del análisis
        """
        import time
        
        if not self.enabled:
            return {"success": False, "error": "SonarCloud no está habilitado"}
        
        # Si se especifica timeout, usar polling exponencial adaptativo
        if timeout:
            return self._wait_with_adaptive_polling(branch_name, timeout)
        
        # Fallback a comportamiento original (para compatibilidad)
        logger.info(f"⏳ Esperando análisis de SonarCloud para branch '{branch_name}'...")
        
        for attempt in range(1, max_attempts + 1):
            logger.info(f"   Intento {attempt}/{max_attempts}...")
            
            # Intentar obtener análisis
            result = self.analyze_branch(branch_name)
            
            if result.get("success"):
                issues = result.get("issues", {})
                if issues.get("total", 0) > 0 or result.get("quality_gate", {}).get("success"):
                    logger.info(f"✅ Análisis disponible para branch '{branch_name}'")
                    return result
            
            if attempt < max_attempts:
                logger.info(f"   Esperando {wait_seconds}s...")
                time.sleep(wait_seconds)
        
        logger.warning(f"⚠️ Timeout esperando análisis de SonarCloud")
        return {
            "success": False,
            "error": f"Timeout después de {max_attempts * wait_seconds}s esperando análisis"
        }
    
    def _wait_with_adaptive_polling(self, branch_name: str, timeout: int) -> Dict[str, Any]:
        """
        Polling con backoff exponencial adaptativo.
        Empieza con intervalos cortos (5s) y los aumenta gradualmente hasta 30s.
        
        Args:
            branch_name: Nombre del branch
            timeout: Timeout total en segundos
            
        Returns:
            Dict con resultado del análisis
        """
        import time
        
        start_time = time.time()
        # Intervalos adaptativos: empieza rápido, luego más lento
        intervals = [5, 10, 15, 20, 30, 30, 30, 30, 30, 30]  # Segundos
        attempt = 0
        
        logger.info(f"⏳ Esperando análisis con polling adaptativo (timeout: {timeout}s)...")
        logger.info(f"   Estrategia: intervalos de {intervals[0]}s → {intervals[-1]}s")
        
        while time.time() - start_time < timeout:
            attempt += 1
            elapsed = time.time() - start_time
            remaining = timeout - elapsed
            
            # Determinar intervalo de espera para este intento
            wait_time = intervals[min(attempt - 1, len(intervals) - 1)]
            
            logger.info(f"   🔍 Intento {attempt} (transcurrido: {elapsed:.1f}s, restante: {remaining:.1f}s)")
            
            # Intentar obtener análisis
            result = self.analyze_branch(branch_name)
            
            if result.get("success"):
                issues = result.get("issues", {})
                total_issues = issues.get("total", 0)
                qg_available = result.get("quality_gate", {}).get("success")
                
                # Análisis disponible si hay issues o quality gate
                if total_issues > 0 or qg_available:
                    logger.info(f"✅ Análisis disponible en {elapsed:.1f}s ({attempt} intentos)")
                    logger.info(f"   📊 Issues encontrados: {total_issues}")
                    if qg_available:
                        qg_status = result.get("quality_gate", {}).get("status", "N/A")
                        logger.info(f"   🚦 Quality Gate: {qg_status}")
                    return result
                else:
                    logger.debug(f"   ⏸️ Análisis aún no disponible (sin issues ni QG)")
            else:
                logger.debug(f"   ⏸️ Branch aún no analizado")
            
            # Verificar si hay tiempo para otro intento
            if time.time() - start_time + wait_time > timeout:
                logger.info(f"   ⏱️ No hay tiempo para otro intento ({wait_time}s)")
                break
            
            logger.info(f"   ⏳ Esperando {wait_time}s antes del próximo intento...")
            time.sleep(wait_time)
        
        elapsed = time.time() - start_time
        logger.warning(f"⚠️ Timeout después de {elapsed:.1f}s ({attempt} intentos)")
        return {
            "success": False,
            "error": f"Timeout después de {elapsed:.1f}s esperando análisis",
            "elapsed_seconds": elapsed,
            "attempts": attempt
        }


# Instancia global del servicio
sonarcloud_service = SonarCloudService()


def test_sonarcloud_connection():
    """
    Función de prueba para verificar la conexión con SonarCloud.
    """
    print("🧪 Probando conexión con SonarCloud...")
    
    if not sonarcloud_service.enabled:
        print("❌ SonarCloud no está habilitado. Verifica tu configuración en .env:")
        print("   - SONARCLOUD_ENABLED=true")
        print("   - SONARCLOUD_TOKEN=squ_...")
        print("   - SONARCLOUD_ORGANIZATION=tu-organizacion")
        print("   - SONARCLOUD_PROJECT_KEY=tu-proyecto")
        return False
    
    # Probar obtener métricas
    print("\n📊 Obteniendo métricas del proyecto...")
    metrics = sonarcloud_service.get_metrics()
    
    if metrics.get("success"):
        print(f"✅ Conexión exitosa!")
        print(f"   Proyecto: {metrics.get('name', 'N/A')}")
        m = metrics.get("metrics", {})
        print(f"   Bugs: {m.get('bugs', 'N/A')}")
        print(f"   Vulnerabilities: {m.get('vulnerabilities', 'N/A')}")
        print(f"   Code Smells: {m.get('code_smells', 'N/A')}")
        return True
    else:
        print(f"❌ Error: {metrics.get('error', 'Error desconocido')}")
        return False


if __name__ == "__main__":
    test_sonarcloud_connection()
