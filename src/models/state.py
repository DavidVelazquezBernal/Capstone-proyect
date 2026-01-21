"""
Definición del estado compartido entre agentes (AgentState).
"""

from typing import TypedDict


class AgentState(TypedDict):
    """
    Representa el estado compartido entre todos los agentes en el grafo.
    """
    prompt_inicial: str

    # Contexto y gestión de bucles
    max_attempts: int  # Máximo de reintentos antes de fallo final
    attempt_count: int  # Contador de intentos en el ciclo externo (stakeholder)
    debug_attempt_count: int  # Contador de intentos en el bucle de depuración (ejecutor_pruebas-desarrollador)
    max_debug_attempts: int  # Máximo de intentos en el bucle de depuración
    feedback_stakeholder: str

    # Datos del proyecto
    requisito_clarificado: str
    requisitos_formales: str  # JSON de Pydantic
    codigo_generado: str

    # Azure DevOps Integration
    azure_pbi_id: int | None  # ID del PBI padre creado en Azure DevOps
    azure_implementation_task_id: int | None  # ID de la Task de implementación
    azure_testing_task_id: int | None  # ID de la Task de testing

    # QA
    traceback: str
    pruebas_superadas: bool

    # SonarQube Analysis
    sonarqube_issues: str  # Reporte de issues de SonarQube
    sonarqube_passed: bool  # Si el análisis de calidad pasó
    sonarqube_attempt_count: int  # Contador de intentos de corrección de SonarQube
    max_sonarqube_attempts: int  # Máximo de intentos de corrección de calidad

    # Unit Tests Generation
    tests_unitarios_generados: str  # Tests unitarios generados (vitest/pytest)
    test_regeneration_needed: bool  # Si los tests fallaron por estar mal construidos (no por código de producción)

    # GitHub Integration
    github_branch_name: str | None  # Nombre del branch creado
    github_pr_number: int | None  # Número de la PR creada
    github_pr_url: str | None  # URL de la PR
    codigo_revisado: bool  # Si el código fue revisado
    revision_comentario: str  # Comentario de la revisión
    revision_puntuacion: int | None  # Puntuación de la revisión (1-10)
    pr_aprobada: bool  # Si la PR fue aprobada
    
    # Code Review Limits
    revisor_attempt_count: int  # Contador de intentos de revisión de código
    max_revisor_attempts: int  # Máximo de intentos de revisión antes de fallo

    # Validación
    validado: bool
