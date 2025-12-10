"""
Punto de entrada principal del sistema multiagente de desarrollo ágil.
Orquesta el flujo completo de generación de código.
"""

import os
import re
import shutil
from config.settings import settings
from workflow.graph import create_workflow, visualize_graph
from tools.file_utils import guardar_fichero_texto, detectar_lenguaje_y_extension


def delete_output_folder():
    """
    Limpia el contenido del directorio output/ al inicio de cada ejecución.
    Elimina todos los archivos y subdirectorios pero mantiene la carpeta.
    """
    if os.path.exists(settings.OUTPUT_DIR):
        for filename in os.listdir(settings.OUTPUT_DIR):
            file_path = os.path.join(settings.OUTPUT_DIR, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"⚠️ No se pudo eliminar {file_path}: {e}")
        print(f"🗑️  Directorio '{settings.OUTPUT_DIR}' limpiado.\n")
    else:
        os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
        print(f"📁 Directorio '{settings.OUTPUT_DIR}' creado.\n")


def run_development_workflow(prompt_inicial: str, max_attempts: int = None):
    """
    Ejecuta el flujo completo de desarrollo multiagente.
    
    Args:
        prompt_inicial (str): La descripción inicial del requisito del usuario
        max_attempts (int, optional): Máximo de ciclos completos. Por defecto usa settings.MAX_ATTEMPTS
    """
    # Validar configuración
    if not settings.validate():
        print("❌ ERROR: Configuración incompleta. Verifica las variables de entorno.")
        return None

    delete_output_folder()

    # Estado inicial
    initial_state = {
        "prompt_inicial": prompt_inicial,
        "feedback_stakeholder": "",
        "max_attempts": max_attempts or settings.MAX_ATTEMPTS,
        "attempt_count": 0,
        "debug_attempt_count": 0,
        "max_debug_attempts": settings.MAX_DEBUG_ATTEMPTS,
        "sonarqube_attempt_count": 0,
        "max_sonarqube_attempts": settings.MAX_SONARQUBE_ATTEMPTS,
        "pruebas_superadas": False,
        "validado": False,
        "traceback": "",
        "sonarqube_issues": "",
        "sonarqube_passed": False,
        "tests_unitarios_generados": "",
        "requisito_clarificado": "",
        "requisitos_formales": "",
        "codigo_generado": ""
    }

    print("\n\n#####################################################")
    print("INICIO DEL FLUJO MULTIAGENTE DE DESARROLLO (LANGGRAPH)")
    print("#####################################################")
    print(f"Prompt Inicial: {prompt_inicial}")
    print(f"Máximo de Intentos: {initial_state['max_attempts']}")
    print("#####################################################\n")

    # Crear y compilar el workflow
    app = create_workflow()
    
    # Visualizar el grafo (si está disponible)
    visualize_graph(app)

    # Acumular el estado a medida que el grafo se ejecuta
    current_final_state = initial_state.copy()

    for step, node_output_map in enumerate(app.stream(initial_state), 1):
        print(f"\n===== CICLO DE TRABAJO, PASO {step} =====")
        
        # Actualizar el estado acumulado
        for node_name, delta_dict in node_output_map.items():
            current_final_state.update(delta_dict)

    # El estado final es el estado acumulado después de que el stream ha terminado
    final_state = current_final_state

    print("\n\n#####################################################")
    print("ESTADO FINAL DEL PROYECTO")
    print("#####################################################")

    if final_state is None:
        print("❌ El flujo no produjo un estado final o falló prematuramente.")
        return None

    # Mostrar resultado
    validado = final_state.get('validado', False)
    debug_exceeded = final_state.get('debug_attempt_count', 0) >= final_state.get('max_debug_attempts', 5)
    
    if debug_exceeded:
        print(f"❌ Validación Final: FALLÓ - LÍMITE DE DEPURACIÓN EXCEDIDO ✗")
        print("-" * 40)
        print(f"Intentos de Depuración: {final_state.get('debug_attempt_count')}/{final_state.get('max_debug_attempts')}")
        print(f"Intentos de Requisitos: {final_state['attempt_count']}")
        print("\n❌ El código no pudo pasar las pruebas después de múltiples intentos de corrección.")
        print(f"Último traceback: {final_state.get('traceback', 'N/A')[:200]}")
    else:
        print(f"✅ Validación Final: {'APROBADO ✓' if validado else 'FALLÓ TRAS INTENTOS ✗'}")
        print("-" * 40)
        print(f"Intentos Totales: {final_state['attempt_count']}")
    
    if validado:
        print("\n📝 Código Final Validado:")
        print(f"\n{final_state['codigo_generado']}\n")
        
        # Detectar el lenguaje y guardar con la extensión correcta
        lenguaje, extension, patron_limpieza = detectar_lenguaje_y_extension(
            final_state.get('requisitos_formales', '')
        )
        
        codigo_limpio = re.sub(patron_limpieza, '', final_state['codigo_generado']).strip()
        nombre_archivo = f"codigo_final{extension}"
        
        guardar_fichero_texto(
            nombre_archivo, 
            codigo_limpio, 
            directorio=settings.OUTPUT_DIR
        )
        print(f"\n💾 Código guardado en: {settings.OUTPUT_DIR}/{nombre_archivo}")
    else:
        print("\n❌ El proyecto no fue validado después de los intentos permitidos.")
        print(f"Último feedback: {final_state.get('feedback_stakeholder', 'N/A')}")

    return final_state


def main():
    """Función principal para ejecución directa del script."""
    
    # Ejemplos de uso - Descomentar el prompt que quieras usar
    
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

    prompt = (
        "Quiero una función simple en TypeScript para generar el factorial de dos números y luego los sume, "
        "y quiero que la salida sea un string con una frase descriptiva."
    )

    # prompt = (
    #      "Quiero una función simple en TypeScript que capitalice la primera letra de cada palabra "        
    # )

    # prompt = {
    #     "Quiero una función simple en TypeScript que valide si un correo electrónico es válido, "
    #     "y quiero que la salida sea un string con una frase descriptiva."
    # }
    
    final_state = run_development_workflow(prompt, max_attempts=3)
    
    if final_state and final_state.get('validado'):
        print("\n🎉 ¡Flujo completado exitosamente!")
    else:
        print("\n⚠️ El flujo terminó sin validación exitosa.")


if __name__ == "__main__":
    main()
