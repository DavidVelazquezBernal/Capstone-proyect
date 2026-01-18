"""
Cliente LLM para interacción con Google Gemini.
Incluye manejo de errores y reintentos automáticos.
Soporta wrapper de LangChain opcional para debugging avanzado.
"""

import os
import time
from typing import Optional, Any, Union, List, Dict
from pydantic import BaseModel
from google import genai
from google.genai.errors import APIError
from config.settings import settings
from utils.logger import setup_logger
from utils.logging_helpers import log_section
from llm.mock_responses import get_mock_response

logger = setup_logger(__name__, level=settings.get_log_level())


def _list_available_models() -> list[str]:
    """
    Lista los modelos disponibles en la API de Gemini.
    
    Returns:
        list[str]: Lista de nombres de modelos disponibles
    """
    try:
        if not client:
            return []
        
        models = client.models.list()
        available_models = []
        
        for model in models:
            # Filtrar solo modelos que soporten generateContent
            if hasattr(model, 'supported_generation_methods'):
                if 'generateContent' in model.supported_generation_methods:
                    available_models.append(model.name)
            else:
                # Si no tiene el atributo, incluirlo por defecto
                available_models.append(model.name)
        
        return available_models
    except Exception as e:
        logger.warning(f"⚠️ No se pudo listar modelos disponibles: {e}")
        return []


def _safe_get_text(response: Any) -> str:
    """
    Extrae texto de forma segura de cualquier tipo de respuesta (objeto Response, str, dict, list).
    Garantiza compatibilidad hacia atrás y con nuevas versiones de API (gemini-3).
    
    Args:
        response: Respuesta del LLM en cualquier formato
        
    Returns:
        str: Texto extraído o string vacío si no se puede extraer
    """
    try:
        if response is None:
            return ""
            
        # 1. Si ya es string
        if isinstance(response, str):
            return response
            
        # 2. Si es lista (caso gemini-3 content list o LangChain messages)
        if isinstance(response, list):
            logger.debug(f"ℹ️ Respuesta es lista, uniendo elementos: {len(response)}")
            parts = []
            for item in response:
                if isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, dict):
                    # Caso Gemini 3: {'type': 'text', 'text': '...'}
                    if item.get('type') == 'text' and 'text' in item:
                        parts.append(str(item['text']))
                    elif 'text' in item:
                        parts.append(str(item['text']))
                    else:
                        parts.append(str(item))
                elif hasattr(item, 'text'):
                    parts.append(item.text or "")
                else:
                    parts.append(str(item))
            return "\n".join(parts)
            
        # 3. Si es diccionario
        if isinstance(response, dict):
            # Caso específico Gemini 3: {'type': 'text', 'text': '...'}
            if response.get('type') == 'text' and 'text' in response:
                logger.debug(f"ℹ️ Detectado formato Gemini 3: {{'type': 'text', 'text': '...'}}")
                return str(response['text'])
            
            # Prioridad de claves comunes en APIs de LLM
            for key in ['text', 'content', 'output', 'response', 'code']:
                if key in response:
                    val = response[key]
                    return _safe_get_text(val)
            # Si es un dict desconocido, convertir a str
            return str(response)

        # 4. Objeto Response de Google GenAI (prioridad a .text)
        if hasattr(response, 'text'):
            try:
                # En algunas versiones .text puede lanzar error si fue bloqueado
                text = response.text
                if text:
                    return text
            except Exception:
                pass # Intentar otras formas

        # 5. Intentar extraer de candidates (estructura interna de Gemini)
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            # Caso standard: content.parts
            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                parts = [part.text for part in candidate.content.parts if hasattr(part, 'text') and part.text]
                if parts:
                    return "\n".join(parts)
            # Caso fallback: content directo
            if hasattr(candidate, 'content') and isinstance(candidate.content, str):
                return candidate.content

        # 6. Objeto LangChain AIMessage
        if hasattr(response, 'content'):
            return _safe_get_text(response.content)

        # Fallback final: representación string del objeto
        return str(response)
        
    except Exception as e:
        logger.error(f"❌ Error extrayendo texto de respuesta: {e}")
        return str(response)


# Importación condicional del wrapper de LangChain
_langchain_available = False
if settings.USE_LANGCHAIN_WRAPPER:
    try:
        from llm.langchain_gemini import call_gemini_with_langchain, get_token_count
        _langchain_available = True
        logger.info("✅ Wrapper de LangChain habilitado")
    except ImportError as e:
        logger.warning(f"⚠️ No se pudo importar wrapper de LangChain: {e}")
        logger.warning("   Instala: pip install langchain-google-genai")
        _langchain_available = False

# Inicialización del cliente Gemini
if settings.LLM_MOCK_MODE:
    client = None
    logger.info("🧪 LLM_MOCK_MODE=true: saltando inicialización del cliente Gemini")
elif settings.GEMINI_API_KEY:
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    logger.info("✅ Cliente Gemini inicializado correctamente.")
else:
    logger.warning("⚠️ WARNING: GEMINI_API_KEY no configurada. El cliente puede fallar.")
    client = None


def _log_warning_if_truncated(response, max_output_tokens: int) -> None:
    try:
        candidates = getattr(response, "candidates", None)
        if not candidates:
            return

        finish_reason = getattr(candidates[0], "finish_reason", None)
        finish_reason_str = str(finish_reason) if finish_reason is not None else ""
        fr = finish_reason_str.lower()

        if fr in {"max_tokens", "length", "token_limit"} or ("max" in fr and "token" in fr):
            logger.warning(
                "⚠️ Respuesta del LLM posiblemente TRUNCADA por límite de tokens "
                f"(finish_reason={finish_reason_str}, max_output_tokens={max_output_tokens}). "
                "Considera aumentar MAX_OUTPUT_TOKENS o pedir una salida más corta."
            )
    except Exception:
        return


def call_gemini(
    role_prompt: str, 
    context: str = "", 
    response_schema: Optional[BaseModel] = None, 
    allow_use_tool: bool = False
) -> str:
    """
    Realiza una llamada a Gemini 2.5 Flash con el prompt formateado.
    
    Args:
        role_prompt (str): El prompt completo (puede incluir system + human de ChatPromptTemplate)
        context (str, optional): Contexto adicional (DEPRECATED - usar ChatPromptTemplate)
        response_schema (BaseModel, optional): Schema Pydantic para validación de respuesta JSON
        allow_use_tool (bool): Si se permite el uso de herramientas (tools)
    
    Returns:
        str: La respuesta del modelo LLM
        
    Note:
        Con ChatPromptTemplate, el parámetro 'context' ya no es necesario porque
        todo el prompt se construye en el template. Se mantiene por compatibilidad.
    """
    # MODO MOCK - Evitar llamadas reales al LLM durante testing
    if settings.LLM_MOCK_MODE:
        logger.info("🧪 [MOCK] Devolviendo respuesta mockeada (LLM_MOCK_MODE=true)")
        return get_mock_response(role_prompt, context)
    
    # MODO LANGCHAIN - Usar wrapper de LangChain si está habilitado
    # Nota: Solo para llamadas simples sin response_schema ni tools
    if settings.USE_LANGCHAIN_WRAPPER and _langchain_available:
        if response_schema is None and not allow_use_tool:
            logger.debug("🔗 Usando wrapper de LangChain")
            try:
                return call_gemini_with_langchain(role_prompt, context)
            except Exception as e:
                logger.warning(f"⚠️ Error con wrapper LangChain, fallback a cliente directo: {e}")
                # Continuar con el cliente directo si falla
    
    if not client:
        return "ERROR: Cliente Gemini no inicializado correctamente."

    # Con ChatPromptTemplate, role_prompt ya contiene todo el prompt formateado
    # Solo añadir context si se proporciona (para compatibilidad con código antiguo)
    if context:
        full_prompt = (
            f"{role_prompt}\n\n"
            f"--- DATOS ACTUALES DEL PROYECTO ---\n"
            f"{context}\n\n"
            f"--- TAREA ---\n"
        )
    else:
        # Prompt ya está completo desde ChatPromptTemplate
        full_prompt = role_prompt

    config = {
        "temperature": settings.TEMPERATURE,
        "max_output_tokens": settings.MAX_OUTPUT_TOKENS
    }

    if response_schema:
        # Rama del Product Owner - salida JSON estructurada
        config["response_mime_type"] = "application/json"
        config["response_schema"] = response_schema.model_json_schema()
        full_prompt += (
            f"GENERA EL OUTPUT ÚNICAMENTE EN FORMATO JSON que se adhiera al siguiente "
            f"esquema Pydantic: {response_schema.__name__}. "
            f"No añadas explicaciones ni texto adicional."
        )
    else:
        full_prompt += "Genera únicamente el bloque de texto solicitado en tu Output Esperado. No añadas explicaciones."

    try:
        response = client.models.generate_content(
            model=settings.MODEL_NAME,
            contents=full_prompt,
            config=config,
        )
        _log_warning_if_truncated(response, config.get("max_output_tokens", settings.MAX_OUTPUT_TOKENS))
        
        # Extraer texto de forma segura usando la nueva función compatible con Gemini 3
        text_response = _safe_get_text(response)
        
        if not text_response or text_response == "None" or text_response.lower() == "none":
            logger.error("")
            log_section(logger, "❌ ERROR: EL LLM NO DEVOLVIÓ RESPUESTA VÁLIDA", level="error")
            logger.error(f"📋 Información de diagnóstico:")
            logger.error(f"   • Modelo usado: {settings.MODEL_NAME}")
            logger.error(f"   • Respuesta vacía: {not text_response}")
            logger.error(f"   • Valor extraído: {repr(text_response)}")
            logger.error(f"   • Tipo de response original: {type(response)}")
            
            # Verificar si hay candidatos en la respuesta
            if hasattr(response, 'candidates') and response.candidates:
                logger.error(f"   • Candidatos disponibles: {len(response.candidates)}")
                for i, candidate in enumerate(response.candidates):
                    logger.error(f"   • Candidato {i+1}:")
                    if hasattr(candidate, 'finish_reason'):
                        finish_reason = str(candidate.finish_reason)
                        logger.error(f"     - Finish reason: {finish_reason}")
                        
                        # Diagnóstico específico para MALFORMED_FUNCTION_CALL
                        if "MALFORMED_FUNCTION_CALL" in finish_reason:
                            logger.error("")
                            log_section(logger, "🔧 DIAGNÓSTICO: MALFORMED_FUNCTION_CALL", level="error")
                            logger.error(f"El modelo intentó llamar a una herramienta pero la llamada está mal formada.")
                            logger.error(f"\n📊 Detalles del candidato:")
                            
                            # Mostrar contenido completo del candidato
                            if hasattr(candidate, 'content') and candidate.content:
                                logger.error(f"   • Contenido del candidato:")
                                logger.error(f"     {candidate.content}")
                                
                                # Verificar si hay function_calls
                                if hasattr(candidate.content, 'parts'):
                                    logger.error(f"\n   • Partes del contenido ({len(candidate.content.parts)} partes):")
                                    for j, part in enumerate(candidate.content.parts):
                                        logger.error(f"     - Parte {j+1}: {type(part).__name__}")
                                        if hasattr(part, 'function_call'):
                                            logger.error(f"       → Function call detectada:")
                                            logger.error(f"         Nombre: {part.function_call.name if hasattr(part.function_call, 'name') else 'N/A'}")
                                            logger.error(f"         Argumentos: {part.function_call.args if hasattr(part.function_call, 'args') else 'N/A'}")
                                        elif hasattr(part, 'text'):
                                            logger.error(f"       → Texto: {part.text[:200]}...")
                            
                            # Mostrar herramientas disponibles
                            if allow_use_tool:
                                logger.error(f"\n   • Herramientas configuradas:")
                                if 'tools' in config:
                                    for tool in config['tools']:
                                        tool_name = tool.__name__ if hasattr(tool, '__name__') else str(tool)
                                        logger.error(f"     - {tool_name}")
                            
                            logger.error(f"\n💡 Posibles causas:")
                            logger.error(f"   1. El modelo generó argumentos con formato JSON inválido")
                            logger.error(f"   2. Los argumentos no coinciden con el schema de la herramienta")
                            logger.error(f"   3. Falta algún argumento requerido por la herramienta")
                            logger.error(f"   4. El nombre de la función es incorrecto")
                    
                    if hasattr(candidate, 'safety_ratings'):
                        logger.error(f"     - Safety ratings: {candidate.safety_ratings}")
                    if hasattr(candidate, 'content'):
                        logger.error(f"     - Content disponible: {candidate.content is not None}")
            else:
                logger.error(f"   • No hay candidatos en la respuesta")
            
            # Verificar bloqueos de seguridad
            if hasattr(response, 'prompt_feedback'):
                logger.error(f"   • Prompt feedback: {response.prompt_feedback}")
            logger.error("")
            raise APIError("El LLM devolvió None o respuesta vacía.")
        return text_response
    
    except APIError as e:
        # Detectar errores críticos que deben detener el flujo
        error_message = str(e)
        
        # Error 404: Modelo no encontrado - DETENER FLUJO
        if "404" in error_message or "NOT_FOUND" in error_message or "is not found" in error_message.lower():
            logger.error("")
            log_section(logger, "❌ ERROR 404: MODELO NO ENCONTRADO", level="error")
            logger.error(f"❌ El modelo especificado no existe o no está disponible")
            logger.error(f"📊 Detalles: {e}")
            logger.error(f"� Modelo solicitado: {settings.MODEL_NAME}")
            
            # Intentar listar modelos disponibles
            logger.error(f"\n🔍 Consultando modelos disponibles en tu API key...")
            available_models = _list_available_models()
            
            if available_models:
                logger.error(f"\n✅ Modelos disponibles con generateContent:")
                for i, model in enumerate(available_models, 1):
                    logger.error(f"   {i}. {model}")
            else:
                logger.error(f"\n⚠️ No se pudo obtener la lista de modelos disponibles")
                logger.error(f"   Modelos comunes: gemini-2.0-flash-exp, gemini-1.5-flash, gemini-1.5-pro")
            
            logger.error(f"\n💡 RECOMENDACIONES:")
            logger.error(f"   1. Verifica el nombre del modelo en .env (MODEL_NAME)")
            logger.error(f"   2. Usa uno de los modelos listados arriba")
            logger.error(f"   3. Consulta la documentación: https://ai.google.dev/gemini-api/docs/models")
            logger.error(f"   4. Verifica que tu API key tenga acceso al modelo")
            logger.error("")
            raise RuntimeError(f"ERROR_404_MODEL_NOT_FOUND: {e}")
        
        # Detectar errores 503 (Service Unavailable) o sobrecarga
        if "503" in error_message or "UNAVAILABLE" in error_message or "overloaded" in error_message.lower():
            logger.error("")
            log_section(logger, "⚠️ ERROR 503: SERVICIO SOBRECARGADO", level="error")
            logger.error(f"❌ El modelo de Gemini está sobrecargado")
            logger.error(f"📊 Detalles: {e}")
            logger.error(f"\n🔄 REINTENTANDO con espera exponencial...")
            logger.error("")
            
            # Reintentar con backoff exponencial
            max_retries = settings.MAX_API_RETRIES
            for attempt in range(1, max_retries + 1):
                wait_time = settings.RETRY_BASE_DELAY ** attempt  # 2, 4, 8 segundos
                logger.warning(f"🔄 Intento {attempt}/{max_retries} - Esperando {wait_time}s...")
                time.sleep(wait_time)
                
                try:
                    response = client.models.generate_content(
                        model=settings.MODEL_NAME,
                        contents=full_prompt,
                        config=config,
                    )
                    _log_warning_if_truncated(response, config.get("max_output_tokens", settings.MAX_OUTPUT_TOKENS))
                    logger.info(f"✅ Reintento exitoso en intento {attempt}")
                    # Usar _safe_get_text también en reintentos para compatibilidad con Gemini 3
                    return _safe_get_text(response)
                except APIError as retry_error:
                    if attempt == max_retries:
                        logger.error("")
                        log_section(logger, "❌ TODOS LOS REINTENTOS FALLARON", level="error")
                        logger.error(f"El servicio de Gemini sigue no disponible después de {max_retries} intentos")
                        logger.error(f"Última error: {retry_error}")
                        logger.error(f"\n💡 RECOMENDACIONES:")
                        logger.error(f"   1. Espera 5-10 minutos e intenta de nuevo")
                        logger.error(f"   2. Verifica el estado de Google AI: https://status.cloud.google.com/")
                        logger.error(f"   3. Considera usar otro modelo si está disponible")
                        logger.error(f"   4. Activa LLM_MOCK_MODE=true en .env para testing sin API")
                        logger.error("")
                        
                        # Retornar error estructurado en lugar de SystemExit
                        return f"ERROR_503_MAX_RETRIES: Servicio no disponible después de {max_retries} intentos. {retry_error}"
                    else:
                        logger.warning(f"   ❌ Intento {attempt} falló: {retry_error}")
                        continue
        
        # Otros errores de API
        return f"ERROR_API: No se pudo conectar con Gemini. {e}"
        
    except Exception as e:
        return f"ERROR_GENERAL: {e}"
