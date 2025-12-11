"""
Paquete de servicios de alto nivel para lógica de negocio.
Centraliza operaciones complejas que requieren coordinación entre múltiples componentes.
"""

from .azure_devops_service import azure_service, AzureDevOpsService

__all__ = ['azure_service', 'AzureDevOpsService']
