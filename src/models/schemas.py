"""
Schemas de Pydantic para validación de datos estructurados.
"""

from pydantic import BaseModel, Field


class FormalRequirements(BaseModel):
    """Esquema formal de requisitos generado por el Product Owner."""
    
    objetivo_funcional: str = Field(
        description="Descripción concisa de la función del código."
    )
    lenguaje_version: str = Field(
        description="Lenguaje y versión, ej. 'Python 3.10+'."
    )
    nombre_funcion: str = Field(
        description="Firma de la función principal, ej. 'def calculate(data)'."
    )
    entradas_esperadas: str = Field(
        description="Tipos de datos y formato de entrada esperados."
    )
    salidas_esperadas: str = Field(
        description="Formato exacto de salida (ej. entero, JSON, cadena con formato)."
    )


class TestCase(BaseModel):
    """Un caso de prueba individual para validación de código."""
    
    input: list = Field(
        description="Lista de argumentos de entrada para la función. Ej: [5], [2, 3], ['hello']"
    )
    expected: str = Field(
        description="Resultado esperado de la ejecución como string. Ej: '120', 'Hello World'"
    )
    method: str | None = Field(
        default=None,
        description="Nombre del método a probar (solo para clases). Ej: 'add', 'subtract'"
    )


class TestExecutionRequest(BaseModel):
    """Solicitud de ejecución de código con casos de prueba."""
    
    language: str = Field(
        description="Lenguaje del código: 'python' o 'typescript'"
    )
    code_type: str = Field(
        description="Tipo de código: 'class' o 'function'"
    )
    class_name: str | None = Field(
        default=None,
        description="Nombre de la clase (solo para code_type='class')"
    )
    function_name: str | None = Field(
        default=None,
        description="Nombre de la función (solo para code_type='function')"
    )
    test_cases: list[TestCase] = Field(
        description="Lista de casos de prueba a ejecutar"
    )
