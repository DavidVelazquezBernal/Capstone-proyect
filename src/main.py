"""
Punto de entrada principal del sistema multiagente de desarrollo ágil.
Orquesta el flujo completo de generación de código.
"""

import os
import re
import shutil
import time
from config.settings import settings, RetryConfig
from workflow.graph import create_workflow, visualize_graph
from tools.file_utils import guardar_fichero_texto, detectar_lenguaje_y_extension, extraer_nombre_archivo, limpiar_codigo_markdown
from utils.logger import setup_logger, log_agent_execution

logger = setup_logger(__name__, level=settings.get_log_level())


def delete_output_folder() -> None:
    """
    Limpia el contenido del directorio output/ al inicio de cada ejecución.
    Elimina todos los archivos y subdirectorios pero mantiene la carpeta.
    Preserva package.json, node_modules y logs (que contiene el archivo de log activo).
    """
    if os.path.exists(settings.OUTPUT_DIR):
        # Archivos y directorios a preservar
        preserve_items = ['package.json', 'package-lock.json', 'node_modules', 'logs']
        
        for filename in os.listdir(settings.OUTPUT_DIR):
            if filename in preserve_items:
                continue  # No eliminar estos archivos/directorios
                
            file_path = os.path.join(settings.OUTPUT_DIR, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                logger.warning(f"⚠️ No se pudo eliminar {file_path}: {e}")
        logger.info(f"🗑️ Directorio '{settings.OUTPUT_DIR}' limpiado (preservando logs)")
    else:
        os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
        logger.info(f"📁 Directorio '{settings.OUTPUT_DIR}' creado")


def run_development_workflow(
    prompt_inicial: str, 
    max_attempts: int = None,
    retry_config: RetryConfig = None
) -> dict:
    """
    Ejecuta el flujo completo de desarrollo multiagente.
    
    Args:
        prompt_inicial (str): La descripción inicial del requisito del usuario
        max_attempts (int, optional): Máximo de ciclos completos. DEPRECATED - usar retry_config
        retry_config (RetryConfig, optional): Configuración consolidada de reintentos. 
                                              Por defecto usa RetryConfig.from_settings()
    """
    # Validar configuración
    if not settings.validate():
        logger.error("❌ Configuración incompleta. Verifica las variables de entorno.")
        return None

    delete_output_folder()

    prompt_inicial_str = prompt_inicial
    if not isinstance(prompt_inicial_str, str):
        try:
            import json
            if isinstance(prompt_inicial_str, set):
                prompt_inicial_str = list(prompt_inicial_str)
            prompt_inicial_str = json.dumps(prompt_inicial_str, ensure_ascii=False, indent=2)
        except Exception:
            prompt_inicial_str = str(prompt_inicial)

    guardar_fichero_texto(
        "0_petición_inicial.txt",
        prompt_inicial_str,
        directorio=settings.OUTPUT_DIR
    )

    # Crear configuración de reintentos
    if retry_config is None:
        # Si se proporciona max_attempts (deprecated), usarlo
        if max_attempts is not None:
            retry_config = RetryConfig(max_attempts=max_attempts)
        else:
            retry_config = RetryConfig.from_settings()
    
    # Estado inicial usando RetryConfig
    initial_state = {
        "prompt_inicial": prompt_inicial,
        "feedback_stakeholder": "",
        "pruebas_superadas": False,
        "validado": False,
        "traceback": "",
        "sonarqube_issues": "",
        "sonarqube_passed": False,
        "tests_unitarios_generados": "",
        "requisito_clarificado": "",
        "requisitos_formales": "",
        "codigo_generado": "",
        "azure_pbi_id": None,
        "azure_implementation_task_id": None,
        "azure_testing_task_id": None,
        # GitHub Integration
        "github_branch_name": None,
        "github_pr_number": None,
        "github_pr_url": None,
        "codigo_revisado": False,
        "revision_comentario": "",
        "revision_puntuacion": None,
        "pr_aprobada": False,
    }
    
    # Agregar configuración de reintentos al estado
    initial_state.update(retry_config.to_state_dict())

    print()  # Línea en blanco para separación visual
    logger.info("=" * 55)
    logger.info("INICIO DEL FLUJO MULTIAGENTE DE DESARROLLO (LANGGRAPH)")
    logger.info("=" * 55)
    logger.info(f"Prompt Inicial: {prompt_inicial}")
    logger.info(f"Máximo de Intentos: {initial_state['max_attempts']}")
    logger.info("=" * 55)

    # Crear y compilar el workflow
    app = create_workflow()
    
    # Visualizar el grafo (si está disponible)
    visualize_graph(app)

    # Acumular el estado a medida que el grafo se ejecuta
    current_final_state = initial_state.copy()
    
    workflow_start = time.time()

    for step, node_output_map in enumerate(app.stream(initial_state), 1):
        logger.debug(f"===== CICLO DE TRABAJO, PASO {step} =====")
        
        # Actualizar el estado acumulado
        for node_name, delta_dict in node_output_map.items():
            current_final_state.update(delta_dict)

    workflow_duration = time.time() - workflow_start

    # El estado final es el estado acumulado después de que el stream ha terminado
    final_state = current_final_state

    print()  # Línea en blanco para separación visual
    logger.info("=" * 55)
    logger.info("ESTADO FINAL DEL PROYECTO")
    logger.info("=" * 55)
    logger.info(f"Duración total: {workflow_duration:.2f}s")

    if final_state is None:
        logger.error("❌ El flujo no produjo un estado final o falló prematuramente.")
        return None

    # Mostrar resultado
    validado = final_state.get('validado', False)
    debug_exceeded = final_state.get('debug_attempt_count', 0) >= final_state.get('max_debug_attempts', 5)
    
    if debug_exceeded:
        logger.error(f"❌ Validación Final: FALLÓ - LÍMITE DE DEPURACIÓN EXCEDIDO")
        logger.info("-" * 40)
        logger.info(f"Intentos de Depuración: {final_state.get('debug_attempt_count')}/{final_state.get('max_debug_attempts')}")
        logger.info(f"Intentos de Requisitos: {final_state['attempt_count']}")
        logger.error("❌ El código no pudo pasar las pruebas después de múltiples intentos de corrección.")
        logger.debug(f"Último traceback: {final_state.get('traceback', 'N/A')[:200]}")
    else:
        if validado:
            logger.info("✅ Validación Final: APROBADO")
        else:
            logger.warning("❌ Validación Final: FALLÓ TRAS INTENTOS")
        logger.info("-" * 40)
        logger.info(f"Intentos Totales: {final_state['attempt_count']}")
    
    if validado:
        logger.info(f"📝 Código Final Validado")
        logger.debug(f"Código: {final_state['codigo_generado'][:200]}...")
        
        # Detectar el lenguaje y guardar con la extensión correcta
        lenguaje, extension, patron_limpieza = detectar_lenguaje_y_extension(
            final_state.get('requisitos_formales', '')
        )
        
        codigo_limpio = limpiar_codigo_markdown(final_state['codigo_generado'])
        
        # Extraer nombre descriptivo del archivo desde requisitos formales
        nombre_base = extraer_nombre_archivo(final_state.get('requisitos_formales', ''))
        nombre_archivo = f"{nombre_base}{extension}"
        
        guardar_fichero_texto(
            nombre_archivo, 
            codigo_limpio, 
            directorio=settings.OUTPUT_DIR
        )
        logger.info(f"💾 Código guardado en: {settings.OUTPUT_DIR}/{nombre_archivo}")
        
        log_agent_execution(logger, "Workflow", "completado exitosamente", {
            "archivo": nombre_archivo,
            "intentos": final_state['attempt_count'],
            "duracion": f"{workflow_duration:.2f}s"
        })
    else:
        logger.warning("❌ El proyecto no fue validado después de los intentos permitidos.")
        logger.info(f"Último feedback: {final_state.get('feedback_stakeholder', 'N/A')[:200]}")
        
        log_agent_execution(logger, "Workflow", "completado sin validación", {
            "intentos": final_state['attempt_count'],
            "duracion": f"{workflow_duration:.2f}s"
        })

    return final_state


def main():
    """Función principal para ejecución directa del script."""
    
    logger.info("🚀 Iniciando sistema multiagente de desarrollo")
    
    # Ejemplos de uso - Descomentar el prompt que quieras usar
    
    # ============================================
    # EJEMPLO 1: Uso básico (configuración por defecto)
    # ============================================
    # prompt = "Crea una función para calcular el factorial de un número"
    # final_state = run_development_workflow(prompt)
    
    # ============================================
    # EJEMPLO 2: Uso con RetryConfig personalizado
    # ============================================
    # from config.settings import RetryConfig
    # 
    # prompt = "Implementa una clase Calculator con operaciones básicas"
    # retry_config = RetryConfig(
    #     max_attempts=2,              # Máximo de ciclos completos
    #     max_debug_attempts=5,        # Máximo de intentos Testing-Desarrollador
    #     max_sonarqube_attempts=2,    # Máximo de intentos SonarQube-Desarrollador
    #     max_revisor_attempts=3       # Máximo de intentos de revisión
    # )
    # final_state = run_development_workflow(prompt, retry_config=retry_config)
    
    # ============================================
    # EJEMPLO 3: Uso con max_attempts (DEPRECATED - usar retry_config)
    # ============================================
    # prompt = "Crea una función para validar emails"
    # final_state = run_development_workflow(prompt, max_attempts=3)
    
    # Opción 1: Python
    # prompt = (
    #     "Quiero una función simple en Python para sumar una lista de números, "
    #     "y quiero que la salida sea una frase."
    # )

    # prompt = (
    #     "Quiero una función simple en Python para generar el factorial de un número, "
    #     "y quiero que la salida sea un string con una frase descriptiva."
    # )    

    # prompt = (
    #     "Quiero una función simple en Python que capitalice la primera letra de cada palabra "        
    # )


    # Opción 2: TypeScript
    # prompt = (
    #     "Quiero una función simple en TypeScript para sumar un array de números, "
    #     "y quiero que la salida sea un string con una frase descriptiva."
    # )

    # prompt = (
    #     "Quiero una función simple en TypeScript para generar el factorial de un número, "
    #     "y quiero que la salida sea un string con una frase descriptiva."
    # )

    # prompt = (
    #     "Quiero una función simple en TypeScript para generar el factorial de dos números y luego los sume, "
    #     "y quiero que la salida sea un string con una frase descriptiva."
    # )

    # prompt = (
    #      "Quiero una función simple en TypeScript que capitalice la primera letra de cada palabra "        
    # )


    


    # prompt = {
    #     "Implementa una clase BinarySearchTree en TypeScript con métodos insert, search, delete, "
    #     "inorder traversal y balance check. Incluye manejo de casos edge como árboles vacíos, "
    #     "nodos duplicados y eliminación de nodos con dos hijos. Añade validación de tipos y "
    #     "documentación JSDoc completa."
    # }

    #====================
    #Básicas
    #====================
    # prompt = {
    #     "Quiero una función simple en TypeScript que valide si un correo electrónico es válido, "
    #     "y quiero que la salida sea un string con una frase descriptiva."
    # }
    # prompt = {
    #     "Implementa una clase Stack (pila) en TypeScript con métodos push, pop, peek, isEmpty y size"
    # }
    # prompt = {
    #     "Implementa una clase Calculator en typescript con las operaciones básicas (+, -, *, /)  y manejo de división por cero"
    # }

    #====================
    #Intermedias
    #====================
    # prompt = {
    #     "Implementa un algoritmo de ordenamiento QuickSort en TypeScript con análisis de complejidad"
    # }
    # prompt = {
    #     "Crea una función en typescript que valide si un string tiene paréntesis balanceados, incluyendo [], {} y ()"
    # }
    # prompt = {
    #     "Crea en typescript un sistema de caché LRU (Least Recently Used) con tiempo de expiración configurable"
    # }
    # prompt = {
    #      "Crea en typescript un Factory Pattern para generar diferentes tipos de vehículos con sus características"
    # }
    # prompt = {
    #     "Implementa en typescript el patrón Observer en TypeScript para un sistema de notificaciones"
    # }
    # prompt = {
    #     "Crea en typescript un middleware de logging que registre requests, responses y errores con diferentes niveles"
    # }
    prompt = {
        "Crea en typescript un sistema de permisos basado en roles (RBAC) con herencia de roles y permisos granulares"
    }

    final_state = run_development_workflow(prompt, max_attempts=3)
    
    if final_state and final_state.get('validado'):
        logger.info("🎉 ¡Flujo completado exitosamente!")
    else:
        logger.warning("⚠️ El flujo terminó sin validación exitosa.")


if __name__ == "__main__":
    main()
