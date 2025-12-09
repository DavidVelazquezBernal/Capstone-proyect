"""
Cliente LLM para interacción con Google Gemini.
"""

import os
from typing import Optional
from pydantic import BaseModel
from google import genai
from google.genai.errors import APIError
from config.settings import settings

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
        # Importación local para evitar dependencia circular
        from tools.code_executor import CodeExecutionToolWithInterpreter
        available_tools = [CodeExecutionToolWithInterpreter]
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
        return f"ERROR_API: No se pudo conectar con Gemini. {e}"
    except Exception as e:
        return f"ERROR_GENERAL: {e}"
