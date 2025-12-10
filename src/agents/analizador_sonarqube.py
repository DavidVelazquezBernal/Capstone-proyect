"""
Agente: Analizador SonarQube
Responsable de verificar la calidad del código generado usando SonarQube antes de las pruebas funcionales.
"""

import re
from models.state import AgentState
from config.prompts import Prompts
from config.settings import settings
from llm.gemini_client import call_gemini
from tools.file_utils import guardar_fichero_texto, detectar_lenguaje_y_extension
from tools.sonarqube_mcp import analizar_codigo_con_sonarqube, formatear_reporte_sonarqube, es_codigo_aceptable



def analizador_sonarqube_node(state: AgentState) -> AgentState:
    """
    Nodo del Analizador SonarQube.
    Analiza la calidad del código generado y determina si cumple los estándares.
    """
    print("--- 3.5 🔍 Analizador SonarQube ---")
    
    # Obtener información del código
    lenguaje, extension, patron_limpieza = detectar_lenguaje_y_extension(
        state.get('requisitos_formales', '')
    )
    codigo_limpio = re.sub(patron_limpieza, '', state['codigo_generado']).strip()
    
    # Generar nombre de archivo para análisis
    nombre_archivo = f"analisis_sonarqube_req{state['attempt_count']}_sq{state['sonarqube_attempt_count']}{extension}"
    
    print(f"   -> Analizando código con SonarQube...")
    print(f"   -> Archivo: {nombre_archivo}")
    
    # Analizar código con SonarQube
    resultado_analisis = analizar_codigo_con_sonarqube(codigo_limpio, nombre_archivo)
    
    # Formatear reporte
    reporte_formateado = formatear_reporte_sonarqube(resultado_analisis)
    print(f"\n{reporte_formateado}\n")
    
    # Guardar reporte
    nombre_reporte = f"3.5_sonarqube_report_req{state['attempt_count']}_sq{state['sonarqube_attempt_count']}.txt"
    guardar_fichero_texto(
        nombre_reporte,
        reporte_formateado,
        directorio=settings.OUTPUT_DIR
    )
    
    # Determinar si el código pasa el análisis
    codigo_aceptable = es_codigo_aceptable(resultado_analisis)
    
    if codigo_aceptable:
        print("   ✅ Código \"revisado\" por SonarQube")
        state['sonarqube_passed'] = True
        state['sonarqube_issues'] = ""
        # Resetear contador cuando pasa
        state['sonarqube_attempt_count'] = 0
    else:
        print("   ❌ Código rechazado por SonarQube - requiere correcciones")
        state['sonarqube_passed'] = False
        state['sonarqube_attempt_count'] += 1
        
        # Generar instrucciones de corrección usando el LLM
        contexto_llm = (
            f"Reporte de SonarQube:\n{reporte_formateado}\n\n"
            f"Código actual:\n{state['codigo_generado']}\n\n"
            f"Requisitos formales:\n{state['requisitos_formales']}"
        )
        
        instrucciones_correccion = call_gemini(Prompts.ANALIZADOR_SONARQUBE, contexto_llm)
        state['sonarqube_issues'] = instrucciones_correccion
        
        # Guardar instrucciones de corrección
        nombre_instrucciones = f"3.5_sonarqube_instrucciones_req{state['attempt_count']}_sq{state['sonarqube_attempt_count']}.txt"
        guardar_fichero_texto(
            nombre_instrucciones,
            instrucciones_correccion,
            directorio=settings.OUTPUT_DIR
        )
        
        print(f"   -> Instrucciones de corrección generadas")
        print(f"   -> Intento de corrección SonarQube: {state['sonarqube_attempt_count']}/{state['max_sonarqube_attempts']}")
    
    return state
