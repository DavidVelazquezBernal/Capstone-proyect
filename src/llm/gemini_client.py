"""
Cliente LLM para interacción con Google Gemini.
"""

import os
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
        return response.text

    except APIError as e:
        # Detectar errores 503 (Service Unavailable) o ResourceExhausted
        error_message = str(e)
        if "503" in error_message or "SERVICE_UNAVAILABLE" in error_message or "ResourceExhausted" in error_message:
            print(f"\n{'='*60}")
            print("🚫 ERROR CRÍTICO: SERVICIO NO DISPONIBLE (503)")
            print(f"{'='*60}")
            print(f"El servicio de Gemini está temporalmente no disponible.")
            print(f"Detalles del error: {e}")
            print(f"{'='*60}\n")
            # Lanzar excepción específica para cancelar el proceso
            raise SystemExit(f"PROCESO CANCELADO: Error 503 - Servicio no disponible. {e}")
        return f"ERROR_API: No se pudo conectar con Gemini. {e}"
    except Exception as e:
        return f"ERROR_GENERAL: {e}"
