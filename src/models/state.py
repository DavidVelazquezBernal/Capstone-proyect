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
    debug_attempt_count: int  # Contador de intentos en el bucle de depuración (probador-codificador)
    max_debug_attempts: int  # Máximo de intentos en el bucle de depuración
    feedback_stakeholder: str

    # Datos del proyecto
    requisito_clarificado: str
    requisitos_formales: str  # JSON de Pydantic
    codigo_generado: str

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

    # Validación
    validado: bool
