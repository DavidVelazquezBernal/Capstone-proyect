"""
Cliente LLM para interacción con Google Gemini.
Incluye manejo de errores y reintentos automáticos.
Soporta wrapper de LangChain opcional para debugging avanzado.
"""

import os
import time
from typing import Optional
from pydantic import BaseModel
from google import genai
from google.genai.errors import APIError
from config.settings import settings
from utils.logger import setup_logger
from tools.code_executor import CodeExecutionToolWithInterpreterPY, CodeExecutionToolWithInterpreterTS
from llm.mock_responses import get_mock_response

logger = setup_logger(__name__, level=settings.get_log_level())

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
# try:
#     # Intentar usar userdata de Colab
#     from google.colab import userdata
#     os.environ["GEMINI_API_KEY"] = userdata.get('gen-lang-client-0440601098')
#     client = genai.Client()
#     print("✅ Cliente Gemini inicializado correctamente (Colab).")
# except ImportError:
    # Entorno local - usar .env
if settings.GEMINI_API_KEY:
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    logger.info("✅ Cliente Gemini inicializado correctamente (Local).")
else:
    logger.warning("⚠️ WARNING: GEMINI_API_KEY no configurada. El cliente puede fallar.")
    client = None
# except Exception as e:
#     print(f"❌ ERROR: Fallo al inicializar el cliente Gemini. {e}")
#     client = None


def call_gemini(
    role_prompt: str, 
    context: str, 
    response_schema: Optional[BaseModel] = None, 
    allow_use_tool: bool = False
) -> str:
    """
    Realiza una llamada a Gemini 2.5 Flash con el prompt de rol y el contexto.
    
    Args:
        role_prompt (str): El prompt que define el rol y las instrucciones del agente
        context (str): El contexto actual del proyecto
        response_schema (BaseModel, optional): Schema Pydantic para validación de respuesta JSON
        allow_use_tool (bool): Si se permite el uso de herramientas (tools)
    
    Returns:
        str: La respuesta del modelo LLM
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

    full_prompt = (
        f"{role_prompt}\n\n"
        f"--- DATOS ACTUALES DEL PROYECTO ---\n"
        f"{context}\n\n"
        f"--- TAREA ---\n"
    )

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
    elif allow_use_tool:
        
        # Proveer ambas herramientas para que el modelo elija según el lenguaje
        available_tools = [CodeExecutionToolWithInterpreterPY, CodeExecutionToolWithInterpreterTS]
        config["tools"] = available_tools
        full_prompt += "Genera únicamente el bloque de texto solicitado en tu Output Esperado. No añadas explicaciones."
    else:
        full_prompt += "Genera únicamente el bloque de texto solicitado en tu Output Esperado. No añadas explicaciones."

    try:
        response = client.models.generate_content(
            model=settings.MODEL_NAME,
            contents=full_prompt,
            config=config,
        )
        if not response.text or response.text == "None" or response.text.lower() == "none":
            logger.error(f"\n{'='*60}")
            logger.error("❌ ERROR: EL LLM NO DEVOLVIÓ RESPUESTA VÁLIDA")
            logger.error(f"{'='*60}")
            logger.error(f"📋 Información de diagnóstico:")
            logger.error(f"   • Modelo usado: {settings.MODEL_NAME}")
            logger.error(f"   • Respuesta vacía: {response.text is None or response.text == ''}")
            logger.error(f"   • Valor de response.text: {repr(response.text)}")
            logger.error(f"   • Tipo de response: {type(response)}")
            
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
                            logger.error(f"\n{'='*60}")
                            logger.error("🔧 DIAGNÓSTICO: MALFORMED_FUNCTION_CALL")
                            logger.error(f"{'='*60}")
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
                            logger.error(f"{'='*60}\n")
                    
                    if hasattr(candidate, 'safety_ratings'):
                        logger.error(f"     - Safety ratings: {candidate.safety_ratings}")
                    if hasattr(candidate, 'content'):
                        logger.error(f"     - Content disponible: {candidate.content is not None}")
            else:
                logger.error(f"   • No hay candidatos en la respuesta")
            
            # Verificar bloqueos de seguridad
            if hasattr(response, 'prompt_feedback'):
                logger.error(f"   • Prompt feedback: {response.prompt_feedback}")
            
            logger.error(f"{'='*60}\n")
            raise APIError("El LLM devolvió None o respuesta vacía.")
        return response.text

    except APIError as e:
        # Detectar errores 503 (Service Unavailable) o sobrecarga
        error_message = str(e)
        
        if "503" in error_message or "UNAVAILABLE" in error_message or "overloaded" in error_message.lower():
            logger.error(f"\n{'='*60}")
            logger.error("⚠️ ERROR 503: SERVICIO SOBRECARGADO")
            logger.error(f"{'='*60}")
            logger.error(f"❌ El modelo de Gemini está sobrecargado")
            logger.error(f"📊 Detalles: {e}")
            logger.error(f"\n🔄 REINTENTANDO con espera exponencial...")
            logger.error(f"{'='*60}\n")
            
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
                    logger.info(f"✅ Reintento exitoso en intento {attempt}")
                    return response.text
                except APIError as retry_error:
                    if attempt == max_retries:
                        logger.error(f"\n{'='*60}")
                        logger.error("❌ TODOS LOS REINTENTOS FALLARON")
                        logger.error(f"{'='*60}")
                        logger.error(f"El servicio de Gemini sigue no disponible después de {max_retries} intentos")
                        logger.error(f"Última error: {retry_error}")
                        logger.error(f"\n💡 RECOMENDACIONES:")
                        logger.error(f"   1. Espera 5-10 minutos e intenta de nuevo")
                        logger.error(f"   2. Verifica el estado de Google AI: https://status.cloud.google.com/")
                        logger.error(f"   3. Considera usar otro modelo si está disponible")
                        logger.error(f"{'='*60}\n")
                        raise SystemExit(f"PROCESO CANCELADO: Servicio de Gemini no disponible después de {max_retries} reintentos.")
                    else:
                        logger.warning(f"   ❌ Intento {attempt} falló: {retry_error}")
                        continue
        
        # Otros errores de API
        return f"ERROR_API: No se pudo conectar con Gemini. {e}"
        
    except Exception as e:
        return f"ERROR_GENERAL: {e}"
