"""
Cliente para integración con Azure DevOps REST API.
Permite crear, actualizar y obtener Work Items (PBIs, Tasks, Bugs).
"""

import base64
import json
import requests
from typing import Optional, Dict, Any, List
from config.settings import settings
from utils.logger import setup_logger, log_agent_execution

logger = setup_logger(__name__, level=settings.get_log_level())

# Límite de caracteres para System.Title en Azure DevOps
AZURE_DEVOPS_TITLE_MAX_LENGTH = 255

def _truncate_title(title: str, max_length: int = AZURE_DEVOPS_TITLE_MAX_LENGTH) -> str:
    """
    Trunca un título para que no exceda el límite de Azure DevOps.
    
    Args:
        title: Título original
        max_length: Longitud máxima permitida (default: 255)
    
    Returns:
        str: Título truncado si es necesario, con '...' al final
    """
    if len(title) <= max_length:
        return title
    
    # Truncar dejando espacio para '...'
    truncated = title[:max_length - 3] + '...'
    logger.warning(f"⚠️ Título truncado de {len(title)} a {len(truncated)} caracteres")
    logger.debug(f"   Original: {title}")
    logger.debug(f"   Truncado: {truncated}")
    
    return truncated


class AzureDevOpsClient:
    """
    Cliente para interactuar con Azure DevOps API.
    Documentación: https://learn.microsoft.com/en-us/rest/api/azure/devops/
    """
    
    def __init__(self):
        """Inicializa el cliente con configuración de settings."""
        self.organization = settings.AZURE_DEVOPS_ORG
        self.project = settings.AZURE_DEVOPS_PROJECT
        self.pat = settings.AZURE_DEVOPS_PAT
        self.iteration_path = settings.AZURE_ITERATION_PATH
        self.area_path = settings.AZURE_AREA_PATH
        
        self.base_url = f"https://dev.azure.com/{self.organization}"
        self.api_version = "7.0"
        
        # Validar configuración
        if not self._validate_config():
            logger.warning("⚠️ Configuración de Azure DevOps incompleta")
    
    def _validate_config(self) -> bool:
        """Valida que las configuraciones mínimas estén presentes."""
        required = [self.organization, self.project, self.pat]
        return all(required)
    
    def _encode_pat(self) -> str:
        """Codifica el Personal Access Token para autenticación."""
        # Azure DevOps requiere formato: base64(":{PAT}")
        credentials = f":{self.pat}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return encoded
    
    def _get_headers(self, content_type: str = "application/json") -> Dict[str, str]:
        """Genera headers para las peticiones HTTP."""
        return {
            "Content-Type": content_type,
            "Authorization": f"Basic {self._encode_pat()}"
        }
    
    def test_connection(self) -> bool:
        """
        Prueba la conexión con Azure DevOps.
        
        Returns:
            bool: True si la conexión es exitosa
        """
        try:
            url = f"{self.base_url}/_apis/projects/{self.project}?api-version={self.api_version}"
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            
            if response.status_code == 200:
                logger.info("✅ Conexión exitosa con Azure DevOps")
                return True
            else:
                logger.error(f"❌ Error de conexión: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error al conectar con Azure DevOps: {e}")
            return False
    
    def search_work_items(
        self,
        title_contains: str = "",
        work_item_type: str = "Product Backlog Item",
        tags: Optional[List[str]] = None,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Busca work items en Azure DevOps usando WIQL (Work Item Query Language).
        
        Args:
            title_contains: Texto que debe contener el título
            work_item_type: Tipo de work item ("Product Backlog Item", "Task", "Bug")
            tags: Lista de tags para filtrar (opcional)
            max_results: Número máximo de resultados
        
        Returns:
            Lista de work items encontrados
        """
        if not self._validate_config():
            logger.error("❌ Configuración de Azure DevOps incompleta")
            return []
        
        try:
            # Construir query WIQL
            wiql_query = f"""
            SELECT [System.Id], [System.Title], [System.State], [System.Tags], [System.CreatedDate]
            FROM WorkItems
            WHERE [System.TeamProject] = '{self.project}'
            AND [System.WorkItemType] = '{work_item_type}'
            """
            
            # Agregar filtro por título si se especifica
            if title_contains:
                wiql_query += f" AND [System.Title] CONTAINS '{title_contains}'"
            
            # Agregar filtro por tags si se especifica
            if tags:
                for tag in tags:
                    wiql_query += f" AND [System.Tags] CONTAINS '{tag}'"
            
            # Ordenar por fecha de creación descendente
            wiql_query += " ORDER BY [System.CreatedDate] DESC"
            
            # Ejecutar query WIQL
            wiql_url = f"{self.base_url}/{self.project}/_apis/wit/wiql?api-version={self.api_version}"
            wiql_body = {"query": wiql_query}
            
            wiql_response = requests.post(
                wiql_url,
                json=wiql_body,
                headers=self._get_headers(),
                timeout=30
            )
            
            if wiql_response.status_code != 200:
                logger.error(f"❌ Error en query WIQL: {wiql_response.status_code}")
                logger.error(f"Respuesta: {wiql_response.text}")
                return []
            
            wiql_result = wiql_response.json()
            work_item_refs = wiql_result.get('workItems', [])
            
            if not work_item_refs:
                logger.debug("No se encontraron work items")
                return []
            
            # Limitar resultados
            work_item_refs = work_item_refs[:max_results]
            
            # Obtener detalles completos de los work items
            work_item_ids = [str(ref['id']) for ref in work_item_refs]
            ids_param = ",".join(work_item_ids)
            
            details_url = (
                f"{self.base_url}/{self.project}/_apis/wit/workitems?"
                f"ids={ids_param}&api-version={self.api_version}"
            )
            
            details_response = requests.get(
                details_url,
                headers=self._get_headers(),
                timeout=30
            )
            
            if details_response.status_code == 200:
                result = details_response.json()
                work_items = result.get('value', [])
                logger.debug(f"✅ Encontrados {len(work_items)} work items")
                return work_items
            else:
                logger.error(f"❌ Error al obtener detalles: {details_response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Excepción al buscar work items: {e}")
            logger.debug(f"Stack trace: {e}", exc_info=True)
            return []
    
    def get_child_work_items(self, parent_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene los work items hijos de un work item padre.
        
        Args:
            parent_id: ID del work item padre
        
        Returns:
            Lista de work items hijos
        """
        if not self._validate_config():
            logger.error("❌ Configuración de Azure DevOps incompleta")
            return []
        
        try:
            # Obtener el work item padre con sus relaciones
            url = (
                f"{self.base_url}/{self.project}/_apis/wit/workitems/{parent_id}?"
                f"$expand=relations&api-version={self.api_version}"
            )
            
            response = requests.get(
                url,
                headers=self._get_headers(),
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"❌ Error al obtener work item #{parent_id}: {response.status_code}")
                return []
            
            work_item = response.json()
            relations = work_item.get('relations', [])
            
            # Filtrar relaciones de tipo hijo (System.LinkTypes.Hierarchy-Forward)
            child_refs = [
                rel for rel in relations
                if rel.get('rel') == 'System.LinkTypes.Hierarchy-Forward'
            ]
            
            if not child_refs:
                logger.debug(f"No se encontraron work items hijos para #{parent_id}")
                return []
            
            # Extraer IDs de los hijos
            child_ids = []
            for ref in child_refs:
                url = ref.get('url', '')
                # URL format: https://dev.azure.com/org/project/_apis/wit/workItems/123
                if url:
                    child_id = url.split('/')[-1]
                    child_ids.append(child_id)
            
            if not child_ids:
                return []
            
            # Obtener detalles completos de los work items hijos
            ids_param = ",".join(child_ids)
            details_url = (
                f"{self.base_url}/{self.project}/_apis/wit/workitems?"
                f"ids={ids_param}&api-version={self.api_version}"
            )
            
            details_response = requests.get(
                details_url,
                headers=self._get_headers(),
                timeout=30
            )
            
            if details_response.status_code == 200:
                result = details_response.json()
                children = result.get('value', [])
                logger.debug(f"✅ Encontrados {len(children)} work items hijos para #{parent_id}")
                return children
            else:
                logger.error(f"❌ Error al obtener detalles de hijos: {details_response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Excepción al obtener work items hijos: {e}")
            logger.debug(f"Stack trace: {e}", exc_info=True)
            return []
    
    def update_work_item(
        self,
        work_item_id: int,
        fields: Dict[str, Any],
        comment: Optional[str] = None
    ) -> bool:
        """
        Actualiza campos de un work item en Azure DevOps.
        
        Args:
            work_item_id: ID del work item a actualizar
            fields: Diccionario con los campos a actualizar {"System.State": "Done", "System.AssignedTo": "user@domain.com"}
            comment: Comentario opcional para agregar al work item
        
        Returns:
            bool: True si se actualizó exitosamente
        """
        if not self._validate_config():
            logger.error("❌ Configuración de Azure DevOps incompleta")
            return False
        
        try:
            url = (
                f"{self.base_url}/{self.project}/_apis/wit/workitems/{work_item_id}?"
                f"api-version={self.api_version}"
            )
            
            # Construir operaciones JSON Patch
            operations = []
            
            for field_path, value in fields.items():
                operations.append({
                    "op": "add",
                    "path": f"/fields/{field_path}",
                    "value": value
                })
            
            # Agregar comentario si se especifica
            if comment:
                operations.append({
                    "op": "add",
                    "path": "/fields/System.History",
                    "value": comment
                })
            
            headers = self._get_headers("application/json-patch+json")
            response = requests.patch(
                url,
                json=operations,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Work item #{work_item_id} actualizado exitosamente")
                
                # Log de campos actualizados
                updated_fields = ", ".join([f"{k}={v}" for k, v in fields.items()])
                logger.debug(f"   Campos actualizados: {updated_fields}")
                
                log_agent_execution(
                    logger,
                    "AzureDevOps",
                    "Work item actualizado",
                    {"id": work_item_id, "fields": fields}
                )
                
                return True
            else:
                logger.error(f"❌ Error al actualizar work item #{work_item_id}: {response.status_code}")
                logger.error(f"Respuesta: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Excepción al actualizar work item: {e}")
            logger.debug(f"Stack trace: {e}", exc_info=True)
            return False
    
    def create_pbi(
        self,
        title: str,
        description: str,
        acceptance_criteria: str,
        story_points: Optional[int] = None,
        tags: Optional[List[str]] = None,
        priority: Optional[int] = 2,
        nature: Optional[str] = None,
        cir: Optional[str] = "No",
        assigned_to: Optional[str] = None,
        custom_fields: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Crea un Product Backlog Item en Azure DevOps.
        
        Args:
            title: Título del PBI
            description: Descripción detallada (soporta HTML)
            acceptance_criteria: Criterios de aceptación (soporta HTML)
            story_points: Puntos de historia (1-100)
            tags: Lista de etiquetas ["AI-Generated", "Backend"]
            priority: Prioridad (1=Alta, 2=Media, 3=Baja, 4=Muy Baja)
            nature: Naturaleza del PBI (por defecto: "3. Technical Debt")
            cir: Campo CIR (por defecto: "No")
            assigned_to: Usuario asignado (None = sin asignar, usar settings.AZURE_ASSIGNED_TO si está configurado)
            custom_fields: Campos personalizados adicionales
        
        Returns:
            Dict con información del work item creado o None si falla
        """
        if not self._validate_config():
            logger.error("❌ Configuración de Azure DevOps incompleta")
            return None
        
        # Valores por defecto para campos requeridos del proyecto
        if nature is None:
            nature = "3. Technical Debt"
        
        # Si assigned_to no se especifica, usar el de configuración (si existe)
        if assigned_to is None and hasattr(settings, 'AZURE_ASSIGNED_TO') and settings.AZURE_ASSIGNED_TO:
            assigned_to = settings.AZURE_ASSIGNED_TO
        
        try:
            # Validar y truncar título si es necesario
            title = _truncate_title(title)
            
            url = (
                f"{self.base_url}/{self.project}/_apis/wit/workitems/"
                f"$Product Backlog Item?api-version={self.api_version}"
            )
            
            # Construir el body según el formato JSON Patch de Azure DevOps
            operations = [
                {"op": "add", "path": "/fields/System.Title", "value": title},
                {"op": "add", "path": "/fields/System.Description", "value": description},
                {"op": "add", "path": "/fields/Microsoft.VSTS.Common.AcceptanceCriteria", "value": acceptance_criteria},
                {"op": "add", "path": "/fields/Microsoft.VSTS.Common.Priority", "value": priority},
                {"op": "add", "path": "/fields/Custom.Nature", "value": nature},
                {"op": "add", "path": "/fields/Custom.CIR", "value": cir}
            ]
            
            # Agregar iteration path si está configurado
            if self.iteration_path:
                operations.append({
                    "op": "add",
                    "path": "/fields/System.IterationPath",
                    "value": self.iteration_path
                })
            
            # Agregar area path si está configurado
            if self.area_path:
                operations.append({
                    "op": "add",
                    "path": "/fields/System.AreaPath",
                    "value": self.area_path
                })
            
            # Agregar story points
            if story_points is not None:
                operations.append({
                    "op": "add",
                    "path": "/fields/Microsoft.VSTS.Scheduling.StoryPoints",
                    "value": story_points
                })
            
            # Agregar asignación
            if assigned_to:
                operations.append({
                    "op": "add",
                    "path": "/fields/System.AssignedTo",
                    "value": assigned_to
                })
            
            # Agregar tags
            if tags:
                tags_str = "; ".join(tags)  # Azure DevOps usa ; como separador
                operations.append({
                    "op": "add",
                    "path": "/fields/System.Tags",
                    "value": tags_str
                })
            
            # Agregar campos personalizados
            if custom_fields:
                for field_path, value in custom_fields.items():
                    operations.append({
                        "op": "add",
                        "path": f"/fields/{field_path}",
                        "value": value
                    })
            
            headers = self._get_headers("application/json-patch+json")
            response = requests.post(url, json=operations, headers=headers, timeout=30)
            
            if response.status_code == 200:
                work_item = response.json()
                work_item_id = work_item['id']
                work_item_url = work_item['_links']['html']['href']
                
                logger.info(f"✅ PBI creado exitosamente: ID {work_item_id}")
                logger.info(f"🔗 URL: {work_item_url}")
                
                log_agent_execution(
                    logger,
                    "AzureDevOps",
                    "PBI creado",
                    {"id": work_item_id, "title": title}
                )
                
                return work_item
            else:
                logger.error(f"❌ Error al crear PBI: {response.status_code}")
                logger.error(f"Respuesta: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Excepción al crear PBI: {e}")
            return None
    
    def create_task(
        self,
        title: str,
        description: str,
        parent_id: Optional[int] = None,
        assigned_to: Optional[str] = None,
        remaining_work: Optional[int] = None,
        tags: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Crea una Task en Azure DevOps, opcionalmente asociada a un PBI padre.
        
        Args:
            title: Título de la tarea
            description: Descripción detallada
            parent_id: ID del PBI padre (opcional)
            assigned_to: Usuario asignado (None = sin asignar, usar settings.AZURE_ASSIGNED_TO si está configurado)
            remaining_work: Horas de trabajo restante (entero positivo, preferiblemente de Fibonacci: 1, 2, 3, 5, 8, 13)
            tags: Lista de etiquetas (opcional)
        
        Returns:
            Dict con información del work item creado o None si falla
        """
        if not self._validate_config():
            logger.error("❌ Configuración de Azure DevOps incompleta")
            return None
        
        # Si assigned_to no se especifica, usar el de configuración (si existe)
        if assigned_to is None and hasattr(settings, 'AZURE_ASSIGNED_TO') and settings.AZURE_ASSIGNED_TO:
            assigned_to = settings.AZURE_ASSIGNED_TO
        
        try:
            # Validar y truncar título si es necesario
            title = _truncate_title(title)
            
            url = (
                f"{self.base_url}/{self.project}/_apis/wit/workitems/"
                f"$Task?api-version={self.api_version}"
            )
            
            operations = [
                {"op": "add", "path": "/fields/System.Title", "value": title},
                {"op": "add", "path": "/fields/System.Description", "value": description}
            ]
            
            # Agregar iteration y area path si están configurados
            if self.iteration_path:
                operations.append({
                    "op": "add",
                    "path": "/fields/System.IterationPath",
                    "value": self.iteration_path
                })
            
            if self.area_path:
                operations.append({
                    "op": "add",
                    "path": "/fields/System.AreaPath",
                    "value": self.area_path
                })
            
            # Agregar remaining work
            if remaining_work is not None:
                operations.append({
                    "op": "add",
                    "path": "/fields/Microsoft.VSTS.Scheduling.RemainingWork",
                    "value": remaining_work
                })
            
            # Agregar asignación
            if assigned_to:
                operations.append({
                    "op": "add",
                    "path": "/fields/System.AssignedTo",
                    "value": assigned_to
                })
            
            # Agregar tags
            if tags:
                tags_str = "; ".join(tags)
                operations.append({
                    "op": "add",
                    "path": "/fields/System.Tags",
                    "value": tags_str
                })
            
            # Agregar relación padre-hijo si se especifica parent_id
            if parent_id:
                operations.append({
                    "op": "add",
                    "path": "/relations/-",
                    "value": {
                        "rel": "System.LinkTypes.Hierarchy-Reverse",
                        "url": f"{self.base_url}/_apis/wit/workItems/{parent_id}"
                    }
                })
            
            headers = self._get_headers("application/json-patch+json")
            response = requests.post(url, json=operations, headers=headers, timeout=30)
            
            if response.status_code == 200:
                work_item = response.json()
                work_item_id = work_item['id']
                work_item_url = work_item['_links']['html']['href']
                
                logger.info(f"✅ Task creada exitosamente: ID {work_item_id}")
                if parent_id:
                    logger.info(f"🔗 Asociada al PBI #{parent_id}")
                logger.info(f"🔗 URL: {work_item_url}")
                
                log_agent_execution(
                    logger,
                    "AzureDevOps",
                    "Task creada",
                    {"id": work_item_id, "title": title, "parent_id": parent_id}
                )
                
                return work_item
            else:
                logger.error(f"❌ Error al crear Task: {response.status_code}")
                logger.error(f"Respuesta: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Excepción al crear Task: {e}")
            return None
    
    def create_bug(
        self,
        title: str,
        repro_steps: str,
        parent_id: Optional[int] = None,
        severity: str = "3 - Medium",
        priority: int = 2,
        tags: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Crea un Bug en Azure DevOps, opcionalmente asociado a un PBI padre.
        
        Args:
            title: Título del bug
            repro_steps: Pasos para reproducir (soporta HTML)
            parent_id: ID del PBI padre (opcional)
            severity: Severidad ("1 - Critical", "2 - High", "3 - Medium", "4 - Low")
            priority: Prioridad (1-4)
            tags: Lista de etiquetas (opcional)
        
        Returns:
            Dict con información del work item creado o None si falla
        """
        if not self._validate_config():
            logger.error("❌ Configuración de Azure DevOps incompleta")
            return None
        
        try:
            # Validar y truncar título si es necesario
            title = _truncate_title(title)
            
            url = (
                f"{self.base_url}/{self.project}/_apis/wit/workitems/"
                f"$Bug?api-version={self.api_version}"
            )
            
            operations = [
                {"op": "add", "path": "/fields/System.Title", "value": title},
                {"op": "add", "path": "/fields/Microsoft.VSTS.TCM.ReproSteps", "value": repro_steps},
                {"op": "add", "path": "/fields/Microsoft.VSTS.Common.Severity", "value": severity},
                {"op": "add", "path": "/fields/Microsoft.VSTS.Common.Priority", "value": priority}
            ]
            
            # Agregar iteration y area path si están configurados
            if self.iteration_path:
                operations.append({
                    "op": "add",
                    "path": "/fields/System.IterationPath",
                    "value": self.iteration_path
                })
            
            if self.area_path:
                operations.append({
                    "op": "add",
                    "path": "/fields/System.AreaPath",
                    "value": self.area_path
                })
            
            # Agregar tags
            if tags:
                tags_str = "; ".join(tags)
                operations.append({
                    "op": "add",
                    "path": "/fields/System.Tags",
                    "value": tags_str
                })
            
            # Agregar relación padre-hijo si se especifica parent_id
            if parent_id:
                operations.append({
                    "op": "add",
                    "path": "/relations/-",
                    "value": {
                        "rel": "System.LinkTypes.Hierarchy-Reverse",
                        "url": f"{self.base_url}/_apis/wit/workItems/{parent_id}"
                    }
                })
            
            headers = self._get_headers("application/json-patch+json")
            response = requests.post(url, json=operations, headers=headers, timeout=30)
            
            if response.status_code == 200:
                work_item = response.json()
                work_item_id = work_item['id']
                work_item_url = work_item['_links']['html']['href']
                
                logger.info(f"✅ Bug creado exitosamente: ID {work_item_id}")
                if parent_id:
                    logger.info(f"🔗 Asociado al PBI #{parent_id}")
                logger.info(f"🔗 URL: {work_item_url}")
                
                log_agent_execution(
                    logger,
                    "AzureDevOps",
                    "Bug creado",
                    {"id": work_item_id, "title": title, "parent_id": parent_id}
                )
                
                return work_item
            else:
                logger.error(f"❌ Error al crear Bug: {response.status_code}")
                logger.error(f"Respuesta: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Excepción al crear Bug: {e}")
            return None
    
    def add_comment(
        self,
        work_item_id: int,
        comment: str
    ) -> bool:
        """
        Agrega un comentario a un work item en Azure DevOps.
        
        Args:
            work_item_id: ID del work item
            comment: Texto del comentario (soporta HTML)
        
        Returns:
            bool: True si se agregó exitosamente
        """
        if not self._validate_config():
            logger.error("❌ Configuración de Azure DevOps incompleta")
            return False
        
        try:
            url = (
                f"{self.base_url}/{self.project}/_apis/wit/workitems/{work_item_id}?"
                f"api-version={self.api_version}"
            )
            
            # Agregar comentario usando el campo System.History
            operations = [{
                "op": "add",
                "path": "/fields/System.History",
                "value": comment
            }]
            
            headers = self._get_headers("application/json-patch+json")
            response = requests.patch(
                url,
                json=operations,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.debug(f"✅ Comentario agregado al work item #{work_item_id}")
                return True
            else:
                logger.error(f"❌ Error al agregar comentario: {response.status_code}")
                logger.error(f"Respuesta: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Excepción al agregar comentario: {e}")
            logger.debug(f"Stack trace: {e}", exc_info=True)
            return False
    
    def attach_file(
        self,
        work_item_id: int,
        file_path: str,
        comment: Optional[str] = None
    ) -> bool:
        """
        Adjunta un archivo a un Work Item en Azure DevOps.
        
        Args:
            work_item_id: ID del work item
            file_path: Ruta completa del archivo a adjuntar
            comment: Comentario opcional para el adjunto
        
        Returns:
            bool: True si se adjuntó exitosamente
        """
        if not self._validate_config():
            logger.error("❌ Configuración de Azure DevOps incompleta")
            return False
        
        try:
            import os
            
            # Verificar que el archivo existe
            if not os.path.exists(file_path):
                logger.error(f"❌ Archivo no encontrado: {file_path}")
                return False
            
            # Paso 1: Subir el archivo al attachment storage
            upload_url = f"{self.base_url}/_apis/wit/attachments?fileName={os.path.basename(file_path)}&api-version={self.api_version}"
            
            with open(file_path, 'rb') as file:
                file_content = file.read()
            
            upload_headers = {
                "Content-Type": "application/octet-stream",
                "Authorization": f"Basic {self._encode_pat()}"
            }
            
            upload_response = requests.post(
                upload_url,
                data=file_content,
                headers=upload_headers,
                timeout=60
            )
            
            if upload_response.status_code != 201:
                logger.error(f"❌ Error al subir archivo: {upload_response.status_code}")
                logger.error(f"Respuesta: {upload_response.text}")
                return False
            
            attachment_data = upload_response.json()
            attachment_url = attachment_data['url']
            
            # Paso 2: Vincular el attachment al work item
            link_url = f"{self.base_url}/_apis/wit/workitems/{work_item_id}?api-version={self.api_version}"
            
            operations = [{
                "op": "add",
                "path": "/relations/-",
                "value": {
                    "rel": "AttachedFile",
                    "url": attachment_url,
                    "attributes": {
                        "comment": comment or f"Archivo adjunto: {os.path.basename(file_path)}"
                    }
                }
            }]
            
            link_headers = self._get_headers("application/json-patch+json")
            link_response = requests.patch(
                link_url,
                json=operations,
                headers=link_headers,
                timeout=30
            )
            
            if link_response.status_code == 200:
                logger.info(f"✅ Archivo '{os.path.basename(file_path)}' adjuntado al Work Item #{work_item_id}")
                
                log_agent_execution(
                    logger,
                    "AzureDevOps",
                    "Archivo adjuntado",
                    {
                        "work_item_id": work_item_id,
                        "file_name": os.path.basename(file_path),
                        "file_size": len(file_content)
                    }
                )
                
                return True
            else:
                logger.error(f"❌ Error al vincular archivo: {link_response.status_code}")
                logger.error(f"Respuesta: {link_response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Excepción al adjuntar archivo: {e}")
            return False


def estimate_story_points(requisitos: Dict[str, Any]) -> int:
    """
    Estima story points basado en la complejidad de los requisitos.
    Usa valores de la serie de Fibonacci: 1, 2, 3, 5, 8, 13, 21
    
    Args:
        requisitos: Diccionario con requisitos formales
    
    Returns:
        int: Story points estimados (valores de Fibonacci)
    """
    # Heurística simple: basado en longitud de descripción y complejidad
    objetivo = requisitos.get('objetivo_funcional', '')
    entradas = requisitos.get('entradas_esperadas', '')
    salidas = requisitos.get('salidas_esperadas', '')
    
    total_length = len(objetivo) + len(entradas) + len(salidas)
    
    # Escala de Fibonacci (valores enteros positivos)
    if total_length < 100:
        return 1
    elif total_length < 200:
        return 2
    elif total_length < 350:
        return 3
    elif total_length < 500:
        return 5
    elif total_length < 700:
        return 8
    elif total_length < 1000:
        return 13
    else:
        return 21


def estimate_effort_hours(task_type: str = "implementation") -> int:
    """
    Estima horas de esfuerzo para una tarea usando valores de Fibonacci.
    Usa valores de la serie de Fibonacci: 1, 2, 3, 5, 8, 13
    
    Args:
        task_type: Tipo de tarea ("implementation", "testing", "review", "bugfix")
    
    Returns:
        int: Horas estimadas (valores enteros positivos de Fibonacci)
    """
    # Estimaciones estándar basadas en tipo de tarea
    effort_map = {
        "implementation": 5,    # Implementación estándar
        "testing": 3,           # Creación de tests
        "review": 2,            # Revisión de código
        "bugfix": 2,            # Corrección de bugs
        "research": 8,          # Investigación/spike
        "refactor": 5,          # Refactorización
        "documentation": 2      # Documentación
    }
    
    # Retornar valor de Fibonacci según el tipo, por defecto 3
    return effort_map.get(task_type.lower(), 3)
