"""
Cliente LLM para interacción con Google Gemini.
Incluye manejo de errores y reintentos automáticos.
"""

import os
import time
from typing import Optional
from pydantic import BaseModel
from google import genai
from google.genai.errors import APIError
from config.settings import settings
from tools.code_executor import CodeExecutionToolWithInterpreterPY, CodeExecutionToolWithInterpreterTS

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
    print("✅ Cliente Gemini inicializado correctamente (Local).")
else:
    print("⚠️ WARNING: GEMINI_API_KEY no configurada. El cliente puede fallar.")
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
            print(f"\n{'='*60}")
            print("❌ ERROR: EL LLM NO DEVOLVIÓ RESPUESTA VÁLIDA")
            print(f"{'='*60}")
            print(f"📋 Información de diagnóstico:")
            print(f"   • Modelo usado: {settings.MODEL_NAME}")
            print(f"   • Respuesta vacía: {response.text is None or response.text == ''}")
            print(f"   • Valor de response.text: {repr(response.text)}")
            print(f"   • Tipo de response: {type(response)}")
            
            # Verificar si hay candidatos en la respuesta
            if hasattr(response, 'candidates') and response.candidates:
                print(f"   • Candidatos disponibles: {len(response.candidates)}")
                for i, candidate in enumerate(response.candidates):
                    print(f"   • Candidato {i+1}:")
                    if hasattr(candidate, 'finish_reason'):
                        finish_reason = str(candidate.finish_reason)
                        print(f"     - Finish reason: {finish_reason}")
                        
                        # Diagnóstico específico para MALFORMED_FUNCTION_CALL
                        if "MALFORMED_FUNCTION_CALL" in finish_reason:
                            print(f"\n{'='*60}")
                            print("🔧 DIAGNÓSTICO: MALFORMED_FUNCTION_CALL")
                            print(f"{'='*60}")
                            print(f"El modelo intentó llamar a una herramienta pero la llamada está mal formada.")
                            print(f"\n📊 Detalles del candidato:")
                            
                            # Mostrar contenido completo del candidato
                            if hasattr(candidate, 'content') and candidate.content:
                                print(f"   • Contenido del candidato:")
                                print(f"     {candidate.content}")
                                
                                # Verificar si hay function_calls
                                if hasattr(candidate.content, 'parts'):
                                    print(f"\n   • Partes del contenido ({len(candidate.content.parts)} partes):")
                                    for j, part in enumerate(candidate.content.parts):
                                        print(f"     - Parte {j+1}: {type(part).__name__}")
                                        if hasattr(part, 'function_call'):
                                            print(f"       → Function call detectada:")
                                            print(f"         Nombre: {part.function_call.name if hasattr(part.function_call, 'name') else 'N/A'}")
                                            print(f"         Argumentos: {part.function_call.args if hasattr(part.function_call, 'args') else 'N/A'}")
                                        elif hasattr(part, 'text'):
                                            print(f"       → Texto: {part.text[:200]}...")
                            
                            # Mostrar herramientas disponibles
                            if allow_use_tool:
                                print(f"\n   • Herramientas configuradas:")
                                if 'tools' in config:
                                    for tool in config['tools']:
                                        tool_name = tool.__name__ if hasattr(tool, '__name__') else str(tool)
                                        print(f"     - {tool_name}")
                            
                            print(f"\n💡 Posibles causas:")
                            print(f"   1. El modelo generó argumentos con formato JSON inválido")
                            print(f"   2. Los argumentos no coinciden con el schema de la herramienta")
                            print(f"   3. Falta algún argumento requerido por la herramienta")
                            print(f"   4. El nombre de la función es incorrecto")
                            print(f"{'='*60}\n")
                    
                    if hasattr(candidate, 'safety_ratings'):
                        print(f"     - Safety ratings: {candidate.safety_ratings}")
                    if hasattr(candidate, 'content'):
                        print(f"     - Content disponible: {candidate.content is not None}")
            else:
                print(f"   • No hay candidatos en la respuesta")
            
            # Verificar bloqueos de seguridad
            if hasattr(response, 'prompt_feedback'):
                print(f"   • Prompt feedback: {response.prompt_feedback}")
            
            print(f"{'='*60}\n")
            raise APIError("El LLM devolvió None o respuesta vacía.")
        return response.text

    except APIError as e:
        # Detectar errores 503 (Service Unavailable) o sobrecarga
        error_message = str(e)
        
        if "503" in error_message or "UNAVAILABLE" in error_message or "overloaded" in error_message.lower():
            print(f"\n{'='*60}")
            print("⚠️ ERROR 503: SERVICIO SOBRECARGADO")
            print(f"{'='*60}")
            print(f"❌ El modelo de Gemini está sobrecargado")
            print(f"📊 Detalles: {e}")
            print(f"\n🔄 REINTENTANDO con espera exponencial...")
            print(f"{'='*60}\n")
            
            # Reintentar con backoff exponencial
            max_retries = settings.MAX_API_RETRIES
            for attempt in range(1, max_retries + 1):
                wait_time = settings.RETRY_BASE_DELAY ** attempt  # 2, 4, 8 segundos
                print(f"🔄 Intento {attempt}/{max_retries} - Esperando {wait_time}s...")
                time.sleep(wait_time)
                
                try:
                    response = client.models.generate_content(
                        model=settings.MODEL_NAME,
                        contents=full_prompt,
                        config=config,
                    )
                    print(f"✅ Reintento exitoso en intento {attempt}")
                    return response.text
                except APIError as retry_error:
                    if attempt == max_retries:
                        print(f"\n{'='*60}")
                        print("❌ TODOS LOS REINTENTOS FALLARON")
                        print(f"{'='*60}")
                        print(f"El servicio de Gemini sigue no disponible después de {max_retries} intentos")
                        print(f"Última error: {retry_error}")
                        print(f"\n💡 RECOMENDACIONES:")
                        print(f"   1. Espera 5-10 minutos e intenta de nuevo")
                        print(f"   2. Verifica el estado de Google AI: https://status.cloud.google.com/")
                        print(f"   3. Considera usar otro modelo si está disponible")
                        print(f"{'='*60}\n")
                        raise SystemExit(f"PROCESO CANCELADO: Servicio de Gemini no disponible después de {max_retries} reintentos.")
                    else:
                        print(f"   ❌ Intento {attempt} falló: {retry_error}")
                        continue
        
        # Otros errores de API
        return f"ERROR_API: No se pudo conectar con Gemini. {e}"
        
    except Exception as e:
        return f"ERROR_GENERAL: {e}"
