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
        
        try:
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
    
    def update_work_item(
        self,
        work_item_id: int,
        fields: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Actualiza un Work Item existente.
        
        Args:
            work_item_id: ID del work item a actualizar
            fields: Diccionario con campos a actualizar
                    Ej: {"System.State": "Active", "System.AssignedTo": "user@domain.com"}
        
        Returns:
            Dict con información del work item actualizado o None si falla
        """
        if not self._validate_config():
            logger.error("❌ Configuración de Azure DevOps incompleta")
            return None
        
        try:
            url = (
                f"{self.base_url}/{self.project}/_apis/wit/workitems/"
                f"{work_item_id}?api-version={self.api_version}"
            )
            
            # Construir operaciones de actualización
            operations = [
                {"op": "add", "path": f"/fields/{field_path}", "value": value}
                for field_path, value in fields.items()
            ]
            
            headers = self._get_headers("application/json-patch+json")
            response = requests.patch(url, json=operations, headers=headers, timeout=30)
            
            if response.status_code == 200:
                work_item = response.json()
                logger.info(f"✅ Work Item {work_item_id} actualizado exitosamente")
                
                log_agent_execution(
                    logger,
                    "AzureDevOps",
                    "Work Item actualizado",
                    {"id": work_item_id, "fields": list(fields.keys())}
                )
                
                return work_item
            else:
                logger.error(f"❌ Error al actualizar Work Item: {response.status_code}")
                logger.error(f"Respuesta: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Excepción al actualizar Work Item: {e}")
            return None
    
    def get_work_item(self, work_item_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene información de un Work Item por ID.
        
        Args:
            work_item_id: ID del work item
        
        Returns:
            Dict con información del work item o None si falla
        """
        if not self._validate_config():
            logger.error("❌ Configuración de Azure DevOps incompleta")
            return None
        
        try:
            url = (
                f"{self.base_url}/{self.project}/_apis/wit/workitems/"
                f"{work_item_id}?api-version={self.api_version}"
            )
            
            response = requests.get(url, headers=self._get_headers(), timeout=30)
            
            if response.status_code == 200:
                work_item = response.json()
                logger.info(f"✅ Work Item {work_item_id} obtenido exitosamente")
                return work_item
            else:
                logger.error(f"❌ Error al obtener Work Item: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Excepción al obtener Work Item: {e}")
            return None
    
    def add_comment(self, work_item_id: int, comment: str) -> bool:
        """
        Agrega un comentario a un Work Item.
        
        Args:
            work_item_id: ID del work item
            comment: Texto del comentario
        
        Returns:
            bool: True si se agregó exitosamente
        """
        if not self._validate_config():
            logger.error("❌ Configuración de Azure DevOps incompleta")
            return False
        
        try:
            url = (
                f"{self.base_url}/{self.project}/_apis/wit/workitems/"
                f"{work_item_id}/comments?api-version={self.api_version}-preview.3"
            )
            
            body = {"text": comment}
            
            response = requests.post(url, json=body, headers=self._get_headers(), timeout=30)
            
            if response.status_code == 200:
                logger.info(f"✅ Comentario agregado al Work Item {work_item_id}")
                return True
            else:
                logger.error(f"❌ Error al agregar comentario: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Excepción al agregar comentario: {e}")
            return False


def estimate_story_points(requisitos: Dict[str, Any]) -> int:
    """
    Estima story points basado en la complejidad de los requisitos.
    
    Args:
        requisitos: Diccionario con requisitos formales
    
    Returns:
        int: Story points estimados (1, 2, 3, 5, 8, 13)
    """
    # Heurística simple: basado en longitud de descripción y complejidad
    objetivo = requisitos.get('objetivo_funcional', '')
    entradas = requisitos.get('entradas_esperadas', '')
    salidas = requisitos.get('salidas_esperadas', '')
    
    total_length = len(objetivo) + len(entradas) + len(salidas)
    
    # Escala de Fibonacci
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
    else:
        return 13
