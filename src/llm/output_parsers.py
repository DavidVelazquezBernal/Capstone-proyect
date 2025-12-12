"""
Output Parsers de LangChain para validación y parsing de respuestas del LLM.
Proporciona parsers reutilizables para diferentes tipos de respuestas estructuradas.
"""

from typing import Type, Optional
from pydantic import BaseModel, ValidationError
from langchain_core.output_parsers import PydanticOutputParser, JsonOutputParser
from langchain_core.exceptions import OutputParserException
from utils.logger import setup_logger
from config.settings import settings

logger = setup_logger(__name__, level=settings.get_log_level())


class RobustPydanticOutputParser(PydanticOutputParser):
    """
    Parser robusto que extiende PydanticOutputParser con mejor manejo de errores.
    Intenta recuperarse de errores comunes de formato JSON.
    """
    
    def parse(self, text: str):
        """
        Parsea el texto a un objeto Pydantic con manejo robusto de errores.
        
        Args:
            text: Texto a parsear (debe ser JSON válido)
            
        Returns:
            Objeto Pydantic validado
            
        Raises:
            OutputParserException: Si el parsing falla después de todos los intentos
        """
        try:
            # Intento 1: Parsing directo
            return super().parse(text)
        except (ValidationError, OutputParserException, ValueError) as e:
            logger.warning(f"⚠️ Primer intento de parsing falló: {e}")
            
            # Intento 2: Limpiar markdown code blocks
            cleaned_text = self._clean_markdown_blocks(text)
            try:
                return super().parse(cleaned_text)
            except (ValidationError, OutputParserException, ValueError) as e2:
                logger.warning(f"⚠️ Segundo intento de parsing falló: {e2}")
                
                # Intento 3: Extraer JSON del texto
                json_text = self._extract_json(cleaned_text)
                try:
                    return super().parse(json_text)
                except (ValidationError, OutputParserException, ValueError) as e3:
                    logger.error(f"❌ Todos los intentos de parsing fallaron")
                    logger.error(f"   Texto original (primeros 200 chars): {text[:200]}")
                    raise OutputParserException(
                        f"No se pudo parsear la respuesta después de 3 intentos. "
                        f"Último error: {e3}"
                    )
    
    def _clean_markdown_blocks(self, text: str) -> str:
        """
        Limpia bloques de código markdown del texto.
        
        Args:
            text: Texto con posibles bloques markdown
            
        Returns:
            Texto limpio sin bloques markdown
        """
        # Remover ```json ... ```
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            if end != -1:
                return text[start:end].strip()
        
        # Remover ``` ... ```
        if "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            if end != -1:
                return text[start:end].strip()
        
        return text.strip()
    
    def _extract_json(self, text: str) -> str:
        """
        Intenta extraer JSON válido del texto.
        
        Args:
            text: Texto que contiene JSON
            
        Returns:
            JSON extraído
        """
        # Buscar el primer { y el último }
        start = text.find("{")
        end = text.rfind("}")
        
        if start != -1 and end != -1 and start < end:
            return text[start:end+1]
        
        return text


def create_parser_for_schema(schema: Type[BaseModel]) -> RobustPydanticOutputParser:
    """
    Crea un parser robusto para un schema Pydantic específico.
    
    Args:
        schema: Clase Pydantic que define el schema
        
    Returns:
        Parser configurado para el schema
    """
    parser = RobustPydanticOutputParser(pydantic_object=schema)
    logger.debug(f"✅ Parser creado para schema: {schema.__name__}")
    return parser


def parse_with_retry(
    text: str,
    schema: Type[BaseModel],
    max_retries: int = 3
) -> Optional[BaseModel]:
    """
    Intenta parsear texto a un schema Pydantic con reintentos.
    
    Args:
        text: Texto a parsear
        schema: Schema Pydantic objetivo
        max_retries: Número máximo de reintentos
        
    Returns:
        Objeto Pydantic validado o None si falla
    """
    parser = create_parser_for_schema(schema)
    
    for attempt in range(max_retries):
        try:
            result = parser.parse(text)
            logger.info(f"✅ Parsing exitoso en intento {attempt + 1}")
            return result
        except Exception as e:
            logger.warning(f"⚠️ Intento {attempt + 1}/{max_retries} falló: {e}")
            if attempt == max_retries - 1:
                logger.error(f"❌ Parsing falló después de {max_retries} intentos")
                return None
    
    return None


def get_format_instructions(schema: Type[BaseModel]) -> str:
    """
    Obtiene las instrucciones de formato para un schema Pydantic.
    Estas instrucciones se pueden incluir en el prompt para guiar al LLM.
    
    Args:
        schema: Schema Pydantic
        
    Returns:
        Instrucciones de formato como string
    """
    parser = create_parser_for_schema(schema)
    instructions = parser.get_format_instructions()
    logger.debug(f"📋 Instrucciones de formato generadas para {schema.__name__}")
    return instructions


# Parsers pre-configurados para schemas comunes del proyecto
def get_formal_requirements_parser() -> RobustPydanticOutputParser:
    """
    Obtiene el parser para FormalRequirements (Product Owner).
    
    Returns:
        Parser configurado
    """
    from models.schemas import FormalRequirements
    return create_parser_for_schema(FormalRequirements)


def get_azure_metadata_parser() -> RobustPydanticOutputParser:
    """
    Obtiene el parser para AzureDevOpsMetadata.
    
    Returns:
        Parser configurado
    """
    from models.schemas import AzureDevOpsMetadata
    return create_parser_for_schema(AzureDevOpsMetadata)


def get_test_execution_parser() -> RobustPydanticOutputParser:
    """
    Obtiene el parser para TestExecutionRequest.
    
    Returns:
        Parser configurado
    """
    from models.schemas import TestExecutionRequest
    return create_parser_for_schema(TestExecutionRequest)


# Función de utilidad para validación directa
def validate_and_parse(text: str, schema: Type[BaseModel]) -> BaseModel:
    """
    Valida y parsea texto a un schema Pydantic.
    Lanza excepción si falla.
    
    Args:
        text: Texto JSON a parsear
        schema: Schema Pydantic objetivo
        
    Returns:
        Objeto Pydantic validado
        
    Raises:
        OutputParserException: Si el parsing falla
    """
    parser = create_parser_for_schema(schema)
    return parser.parse(text)
