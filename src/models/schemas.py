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
