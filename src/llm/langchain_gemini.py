"""
Wrapper de LangChain para Google Gemini.
Proporciona integración con el ecosistema LangChain manteniendo compatibilidad con el cliente directo.
"""

from typing import Optional, List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from config.settings import settings
from utils.logger import setup_logger

logger = setup_logger(__name__, level=settings.get_log_level())

# Importar _safe_get_text para compatibilidad con Gemini 3
# Evitar import circular usando import tardío dentro de la función


def create_langchain_llm(
    streaming: bool = False,
    callbacks: Optional[List] = None
) -> ChatGoogleGenerativeAI:
    """
    Crea una instancia del LLM de Gemini usando LangChain.
    
    Args:
        streaming: Si se debe habilitar streaming de respuestas
        callbacks: Lista de callbacks personalizados
    
    Returns:
        ChatGoogleGenerativeAI: Instancia del LLM configurada
    """
    if not settings.GEMINI_API_KEY:
        logger.warning("⚠️ GEMINI_API_KEY no configurada")
        raise ValueError("GEMINI_API_KEY no está configurada en settings")
    
    # Configurar callbacks si se solicita streaming
    if streaming and callbacks is None:
        callbacks = [StreamingStdOutCallbackHandler()]
    
    llm = ChatGoogleGenerativeAI(
        model=settings.MODEL_NAME,
        google_api_key=settings.GEMINI_API_KEY,
        temperature=settings.TEMPERATURE,
        max_output_tokens=settings.MAX_OUTPUT_TOKENS,
        streaming=streaming,
        callbacks=callbacks,
        convert_system_message_to_human=True  # Gemini requiere esto
    )
    
    logger.info(f"✅ LangChain LLM inicializado: {settings.MODEL_NAME}")
    return llm


def call_gemini_with_langchain(
    role_prompt: str,
    context: str,
    streaming: bool = False,
    callbacks: Optional[List] = None
) -> str:
    """
    Realiza una llamada a Gemini usando el wrapper de LangChain.
    
    Args:
        role_prompt: El prompt que define el rol y las instrucciones del agente
        context: El contexto actual del proyecto
        streaming: Si se debe habilitar streaming de respuestas
        callbacks: Lista de callbacks personalizados
    
    Returns:
        str: La respuesta del modelo LLM
    """
    try:
        llm = create_langchain_llm(streaming=streaming, callbacks=callbacks)
        
        # Construir mensajes
        messages = [
            SystemMessage(content=role_prompt),
            HumanMessage(content=f"""--- DATOS ACTUALES DEL PROYECTO ---
{context}

--- TAREA ---
Genera únicamente el bloque de texto solicitado en tu Output Esperado. No añadas explicaciones.""")
        ]
        
        # Invocar el LLM
        response = llm.invoke(messages)
        
        # Importar _safe_get_text aquí para evitar import circular
        from llm.gemini_client import _safe_get_text
        
        # Extraer el contenido de la respuesta usando _safe_get_text para compatibilidad con Gemini 3
        # En Gemini 3, response.content puede ser {'type': 'text', 'text': '...', 'extras': {...}}
        if hasattr(response, 'content'):
            return _safe_get_text(response.content)
        else:
            return _safe_get_text(response)
            
    except Exception as e:
        logger.error(f"❌ Error en llamada LangChain: {e}")
        raise


def get_token_count(text: str) -> Dict[str, int]:
    """
    Obtiene el conteo de tokens para un texto usando el modelo de Gemini.
    
    Args:
        text: Texto a analizar
    
    Returns:
        Dict con información de tokens
    """
    try:
        llm = create_langchain_llm()
        
        # LangChain proporciona método para contar tokens
        token_count = llm.get_num_tokens(text)
        
        return {
            "total_tokens": token_count,
            "model": settings.MODEL_NAME
        }
    except Exception as e:
        logger.warning(f"⚠️ No se pudo contar tokens: {e}")
        return {"total_tokens": -1, "model": settings.MODEL_NAME}


# Instancia global del LLM (lazy loading)
_llm_instance: Optional[ChatGoogleGenerativeAI] = None


def get_llm_instance() -> ChatGoogleGenerativeAI:
    """
    Obtiene una instancia singleton del LLM de LangChain.
    
    Returns:
        ChatGoogleGenerativeAI: Instancia del LLM
    """
    global _llm_instance
    
    if _llm_instance is None:
        _llm_instance = create_langchain_llm()
        logger.info("✅ Instancia singleton de LLM creada")
    
    return _llm_instance
