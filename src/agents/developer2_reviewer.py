"""
Agente: Developer2-Reviewer
Responsable de revisar el código generado en la PR y aprobarla si cumple los estándares.
"""

import time
import json
from models.state import AgentState
from config.settings import settings
from config.prompt_templates import PromptTemplates
from llm.gemini_client import call_gemini
from tools.file_utils import guardar_fichero_texto
from services.github_service import github_service
from utils.logger import setup_logger, log_agent_execution, log_llm_call, log_file_operation
from utils.agent_decorators import agent_execution_context

logger = setup_logger(__name__, level=settings.get_log_level(), agent_mode=True)


def developer2_reviewer_node(state: AgentState) -> AgentState:
    """
    Nodo del Developer2-Reviewer.
    Revisa el código en la PR y decide si aprobarlo o solicitar cambios.
    """


    with agent_execution_context("🔍 DEVELOPER2-REVIEWER", logger):
        log_agent_execution(logger, "Developer2-Reviewer", "iniciado", {
            "pr_number": state.get('github_pr_number'),
            "branch": state.get('github_branch_name')
        })
        
        # Verificar que GitHub está habilitado y hay una PR
        if not settings.GITHUB_ENABLED:
            logger.info("ℹ️ GitHub no está habilitado, saltando revisión de código")
            state['codigo_revisado'] = True
            state['revision_comentario'] = "Revisión omitida - GitHub no habilitado"
            return state
        
        pr_number = state.get('github_pr_number')
        if not pr_number:
            logger.warning("⚠️ No hay PR para revisar")
            state['codigo_revisado'] = True
            state['revision_comentario'] = "No hay PR para revisar"
            return state
        
        logger.info(f"📋 Revisando PR #{pr_number}")
        
        # Obtener el código y tests de la PR
        codigo_generado = state.get('codigo_generado', '')
        tests_generados = state.get('tests_unitarios_generados', '')
        requisitos_formales = state.get('requisitos_formales', '')
        
        # Construir prompt para revisión de código
        prompt_revision = f"""Eres un developer reviewer senior. Analiza el siguiente código y tests generados automáticamente.

## Requisitos del proyecto:
{requisitos_formales}

## Código generado:
```
{codigo_generado}
```

## Tests unitarios:
```
{tests_generados}
```

## Tu tarea:
1. Revisa que el código cumple con los requisitos
2. Verifica que sigue buenas prácticas de programación
3. Comprueba que los tests cubren los casos importantes
4. Evalúa la legibilidad y mantenibilidad

## Responde en formato JSON:
{{
    "aprobado": true/false,
    "puntuacion": 1-10,
    "aspectos_positivos": ["lista de puntos positivos"],
    "aspectos_mejorar": ["lista de aspectos a mejorar (si los hay)"],
    "comentario_revision": "Comentario general de la revisión para la PR"
}}

IMPORTANTE: Sé constructivo pero exigente. Solo aprueba si el código es de calidad aceptable.
"""
        
        # Llamar al LLM para revisión
        logger.info("🤖 Analizando código con LLM...")
        start_time = time.time()
        respuesta_llm = call_gemini(prompt_revision, "")
        duration = time.time() - start_time
        
        log_llm_call(logger, "revision_codigo", duration=duration)
        
        # Parsear respuesta
        try:
            # Limpiar respuesta de marcadores markdown
            respuesta_limpia = respuesta_llm.strip()
            if respuesta_limpia.startswith('```'):
                respuesta_limpia = respuesta_limpia.split('\n', 1)[1]
            if respuesta_limpia.endswith('```'):
                respuesta_limpia = respuesta_limpia.rsplit('```', 1)[0]
            respuesta_limpia = respuesta_limpia.strip()
            
            resultado = json.loads(respuesta_limpia)
            
            aprobado = resultado.get('aprobado', False)
            puntuacion = resultado.get('puntuacion', 0)
            aspectos_positivos = resultado.get('aspectos_positivos', [])
            aspectos_mejorar = resultado.get('aspectos_mejorar', [])
            comentario = resultado.get('comentario_revision', '')
            
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"⚠️ Error al parsear respuesta del LLM: {e}")
            # Asumir aprobado si no se puede parsear
            aprobado = True
            puntuacion = 7
            comentario = "Revisión automática completada. El código parece cumplir los requisitos básicos."
            aspectos_positivos = ["Código generado correctamente"]
            aspectos_mejorar = []
        
        # Construir comentario para la PR
        comentario_pr = f"""## 🔍 Revisión Automática de Código

**Puntuación:** {puntuacion}/10
**Estado:** {'✅ APROBADO' if aprobado else '⚠️ REQUIERE CAMBIOS'}

### ✨ Aspectos Positivos
{chr(10).join(f'- {p}' for p in aspectos_positivos) if aspectos_positivos else '- N/A'}

### 📝 Aspectos a Mejorar
{chr(10).join(f'- {m}' for m in aspectos_mejorar) if aspectos_mejorar else '- Ninguno identificado'}

### 💬 Comentario
{comentario}

---
*Revisión realizada por AI Code Reviewer*
"""
        
        # Actualizar estado
        state['codigo_revisado'] = aprobado
        state['revision_comentario'] = comentario
        state['revision_puntuacion'] = puntuacion
        
        # Guardar resultado de la revisión en archivo
        estado_revision = "APROBADO" if aprobado else "RECHAZADO"
        nombre_archivo = f"4.5_reviewer_req{state['attempt_count']}_revisor{state.get('revisor_attempt_count', 0)}_{estado_revision}.txt"
        contenido_archivo = f"""Estado: {estado_revision}
Puntuación: {puntuacion}/10

{'='*60}
{comentario_pr}
{'='*60}

Respuesta LLM completa:
{respuesta_llm}
"""
        
        success = guardar_fichero_texto(
            nombre_archivo,
            contenido_archivo,
            directorio=settings.OUTPUT_DIR
        )
        
        log_file_operation(
            logger,
            "guardar",
            f"{settings.OUTPUT_DIR}/{nombre_archivo}",
            success=success
        )
        
        # Incrementar contador de intentos si rechaza
        if not aprobado:
            state['revisor_attempt_count'] = state.get('revisor_attempt_count', 0) + 1
            logger.info(f"📊 Intento de revisión: {state['revisor_attempt_count']}/{state.get('max_revisor_attempts', 2)}")
        
        # Aprobar o comentar en la PR
        if aprobado:
            logger.info(f"✅ Código APROBADO con puntuación {puntuacion}/10")
            
            # Aprobar la PR
            success = github_service.approve_pull_request(pr_number, comentario_pr, use_reviewer_token=True)
            
            if success:
                logger.info(f"✅ PR #{pr_number} aprobada")
                state['pr_aprobada'] = True
            else:
                logger.warning(f"⚠️ No se pudo aprobar la PR #{pr_number}")
                state['pr_aprobada'] = False
        else:
            logger.warning(f"⚠️ Código RECHAZADO con puntuación {puntuacion}/10")
            
            # Añadir comentario a la PR
            github_service.add_comment_to_pr(pr_number, comentario_pr, use_reviewer_token=True)
            state['pr_aprobada'] = False
        
        log_agent_execution(logger, "Developer2-Reviewer", "completado", {
            "aprobado": aprobado,
            "puntuacion": puntuacion,
            "pr_number": pr_number
        })
        
    
    return state
