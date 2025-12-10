"""Agente 4: Ejecutor de Pruebas
Responsable de ejecutar los tests unitarios generados (vitest/pytest).
Valida que el código funcione correctamente según los requisitos.
"""

import os
import re
import json
import subprocess
import logging
from typing import Dict, Any
from models.state import AgentState
from config.settings import settings
from tools.file_utils import guardar_fichero_texto, detectar_lenguaje_y_extension
from utils.logger import setup_logger, log_agent_execution, log_file_operation

# Configurar logger para este agente
logger = setup_logger(__name__, level=settings.get_log_level(), agent_mode=True)


def _limpiar_ansi(text: str) -> str:
    """Elimina códigos de escape ANSI (colores) del texto."""
    ansi_escape = re.compile(r'\x1b\[[0-9;]*[mGKHF]')
    return ansi_escape.sub('', text)


def ejecutor_pruebas_node(state: AgentState) -> AgentState:
    """
    Nodo del Ejecutor de Pruebas.
    Ejecuta directamente los tests unitarios generados por el generador_unit_tests.
    
    Estrategia:
    1. Detectar lenguaje del código generado
    2. Localizar archivo de tests generado
    3. Ejecutar tests con el framework apropiado (vitest/pytest)
    4. Parsear resultados y actualizar estado
    """
    logger.info("=" * 60)
    logger.info("🧪 EJECUTOR DE PRUEBAS - INICIO")
    logger.info("=" * 60)
    
    # Detectar lenguaje
    lenguaje, extension, _ = detectar_lenguaje_y_extension(
        state.get('requisitos_formales', '')
    )
    
    logger.info(f"📝 Lenguaje detectado: {lenguaje}")
    
    # Construir rutas de archivos
    attempt = state['attempt_count']
    sq_attempt = state['sonarqube_attempt_count']
    debug_attempt = state['debug_attempt_count']
    
    log_agent_execution(
        logger,
        "Ejecutor Pruebas",
        "Preparando ejecución",
        {
            "lenguaje": lenguaje,
            "req": attempt,
            "debug": debug_attempt,
            "sq": sq_attempt
        }
    )
    
    # Ruta del código generado
    if lenguaje.lower() == 'typescript':
        code_filename = f"3_codificador_req{attempt}_debug{debug_attempt}_sq{sq_attempt}.ts"
        test_filename = f"unit_tests_req{attempt}_sq{sq_attempt}.test.ts"
    else:  # Python
        code_filename = f"3_codificador_req{attempt}_debug{debug_attempt}_sq{sq_attempt}.py"
        test_filename = f"test_unit_req{attempt}_sq{sq_attempt}.py"
    
    code_path = os.path.join(settings.OUTPUT_DIR, code_filename)
    test_path = os.path.join(settings.OUTPUT_DIR, test_filename)
    
    # Verificar que existen los archivos
    if not os.path.exists(test_path):
        logger.error(f"❌ No se encontró el archivo de tests: {test_path}")
        state['pruebas_superadas'] = False
        state['traceback'] = f"No se encontró el archivo de tests: {test_filename}"
        state['debug_attempt_count'] += 1
        
        guardar_fichero_texto(
            f"4_probador_req{attempt}_debug{debug_attempt}_ERROR.txt",
            f"Status: ERROR\n\nError: Archivo de tests no encontrado\n{test_path}",
            directorio=settings.OUTPUT_DIR
        )
        
        log_file_operation(logger, "buscar", test_path, success=False, error="Archivo no encontrado")
        return state
    
    if not os.path.exists(code_path):
        logger.warning(f"⚠️ No se encontró el archivo de código: {code_path}")
        # Intentar guardar el código del estado
        guardar_fichero_texto(code_filename, state['codigo_generado'], directorio=settings.OUTPUT_DIR)
        logger.info("✅ Código guardado desde el estado")
    
    logger.info(f"📄 Archivo de tests: {test_filename}")
    logger.info(f"📄 Archivo de código: {code_filename}")
    
    # Ejecutar tests según el lenguaje
    try:
        if lenguaje.lower() == 'typescript':
            result = _ejecutar_tests_typescript(test_path, code_path, state)
        else:  # Python
            result = _ejecutar_tests_python(test_path, state)
        
        # Actualizar estado con resultados
        state['pruebas_superadas'] = result['success']
        state['traceback'] = result['traceback']
        
        if result['success']:
            state['debug_attempt_count'] = 0  # Resetear contador
            
            # Obtener estadísticas
            stats = result.get('tests_run', {})
            if isinstance(stats, dict):
                total = stats.get('total', 0)
                passed = stats.get('passed', 0)
                failed = stats.get('failed', 0)
                logger.info(f"✅ Tests PASSED - Total: {total}, Pasados: {passed}, Fallidos: {failed}")
                
                log_agent_execution(
                    logger,
                    "Ejecutor Pruebas",
                    "Tests exitosos",
                    {"total": total, "passed": passed, "failed": failed}
                )
            else:
                logger.info("✅ Tests PASSED")
            
            # Guardar resultado exitoso con estadísticas legibles
            clean_output = _limpiar_ansi(result['output'])
            stats_summary = ""
            if isinstance(stats, dict):
                stats_summary = f"\nEstadísticas:\n  Total: {stats.get('total', 0)}\n  Pasados: {stats.get('passed', 0)}\n  Fallidos: {stats.get('failed', 0)}\n"
            
            output_content = f"Status: PASSED{stats_summary}\n{'='*60}\n{clean_output}"
            nombre_archivo = f"4_probador_req{attempt}_debug{debug_attempt}_PASSED.txt"
            guardar_fichero_texto(
                nombre_archivo,
                output_content,
                directorio=settings.OUTPUT_DIR
            )
            
            log_file_operation(logger, "guardar", f"{settings.OUTPUT_DIR}/{nombre_archivo}", success=True)
        else:
            state['debug_attempt_count'] += 1
            
            # Obtener estadísticas
            stats = result.get('tests_run', {})
            if isinstance(stats, dict):
                total = stats.get('total', 0)
                passed = stats.get('passed', 0)
                failed = stats.get('failed', 0)
                logger.error(f"❌ Tests FAILED - Total: {total}, Pasados: {passed}, Fallidos: {failed}")
                
                log_agent_execution(
                    logger,
                    "Ejecutor Pruebas",
                    "Tests fallidos",
                    {"total": total, "passed": passed, "failed": failed},
                    level=logging.ERROR
                )
            else:
                logger.error("Tests FAILED")
            
            logger.info(f"➡️ Intento de depuración: {state['debug_attempt_count']}/{state['max_debug_attempts']}")
            
            # Guardar resultado fallido con contenido limpio
            clean_output = _limpiar_ansi(result['output'])
            clean_traceback = _limpiar_ansi(result['traceback'])
            stats_summary = ""
            if isinstance(stats, dict):
                stats_summary = f"\nEstadísticas:\n  Total: {stats.get('total', 0)}\n  Pasados: {stats.get('passed', 0)}\n  Fallidos: {stats.get('failed', 0)}\n"
            
            output_content = f"Status: FAILED{stats_summary}\n{'='*60}\n\nTraceback:\n{clean_traceback}\n\n{'='*60}\n{clean_output}"
            nombre_archivo = f"4_probador_req{attempt}_debug{debug_attempt}_FAILED.txt"
            guardar_fichero_texto(
                nombre_archivo,
                output_content,
                directorio=settings.OUTPUT_DIR
            )
            
            log_file_operation(logger, "guardar", f"{settings.OUTPUT_DIR}/{nombre_archivo}", success=True)
        
        # Mostrar resumen
        _mostrar_resumen_ejecucion(result)
        
    except Exception as e:
        logger.exception(f"❌ ERROR durante la ejecución: {e}")
        state['pruebas_superadas'] = False
        state['traceback'] = f"ERROR de ejecución: {str(e)}"
        state['debug_attempt_count'] += 1
        
        guardar_fichero_texto(
            f"4_probador_req{attempt}_debug{debug_attempt}_ERROR.txt",
            f"Status: ERROR\n\nError de ejecución:\n{str(e)}",
            directorio=settings.OUTPUT_DIR
        )
    
    logger.info("🧪 EJECUTOR DE PRUEBAS - FIN")
    logger.info("=" * 60)
    
    return state


def _ejecutar_tests_typescript(test_path: str, code_path: str, state: AgentState) -> Dict[str, Any]:
    """
    Ejecuta tests TypeScript usando vitest.
    
    Args:
        test_path: Ruta al archivo de tests
        code_path: Ruta al archivo de código
        state: Estado actual del agente
        
    Returns:
        Dict con 'success', 'output', 'traceback'
    """
    logger.info("▶️ Ejecutando vitest...")
    
    # Cambiar al directorio output para que las importaciones relativas funcionen
    original_dir = os.getcwd()
    output_dir = os.path.abspath(settings.OUTPUT_DIR)
    
    try:
        os.chdir(output_dir)
        logger.debug(f"Directorio de trabajo: {output_dir}")
        
        # Asegurar que existe package.json para que npx encuentre vitest
        package_json_path = os.path.join(output_dir, 'package.json')
        if not os.path.exists(package_json_path):
            package_json_content = {
                "name": "capstone-tests",
                "version": "1.0.0",
                "type": "module",
                "devDependencies": {
                    "vitest": "^4.0.15"
                }
            }
            with open(package_json_path, 'w') as f:
                json.dump(package_json_content, f, indent=2)
            logger.info(f" ℹ️ package.json creado en {output_dir}")
        
        # Ejecutar vitest con el archivo de tests
        # Usar --run para modo no-watch, --reporter=verbose para detalles
        # En Windows, usar shell=True para que encuentre npx correctamente
        result = subprocess.run(
            ['npx', 'vitest', 'run', os.path.basename(test_path), '--reporter=verbose'],
            capture_output=True,
            text=True,
            timeout=60,  # 60 segundos de timeout
            shell=True  # Necesario en Windows para encontrar npx
        )
        
        os.chdir(original_dir)
        
        success = result.returncode == 0
        stdout = result.stdout or ""
        stderr = result.stderr or ""
        output = stdout + "\n" + stderr
        traceback = stderr if not success else ""
        
        return {
            'success': success,
            'output': output,
            'traceback': traceback,
            'tests_run': _parsear_resultados_vitest(output)
        }
        
    except subprocess.TimeoutExpired:
        os.chdir(original_dir)
        return {
            'success': False,
            'output': "Timeout: Los tests tardaron más de 60 segundos",
            'traceback': "TimeoutError: Test execution exceeded 60 seconds",
            'tests_run': 0
        }
    except FileNotFoundError as e:
        os.chdir(original_dir)
        # Error al ejecutar npx - el comando no existe
        return {
            'success': False,
            'output': f"Node.js/npx no está instalado o no está en el PATH.\n\nVerifique:\n  1. Node.js instalado: node --version\n  2. npx disponible: npx --version\n  3. Vitest instalado en output/: cd output && npm install -D vitest",
            'traceback': f"FileNotFoundError: npx command not found - {str(e)}",
            'tests_run': 0
        }
    except OSError as e:
        os.chdir(original_dir)
        # Error del sistema operativo (permisos, directorio no existe, etc.)
        return {
            'success': False,
            'output': f"Error del sistema operativo:\n{str(e)}\n\nDirectorio de trabajo: {output_dir}\nArchivo de tests: {test_path}",
            'traceback': f"OSError: {str(e)}",
            'tests_run': 0
        }
    except Exception as e:
        os.chdir(original_dir)
        return {
            'success': False,
            'output': f"Error inesperado al ejecutar vitest:\n{str(e)}\n\nTipo: {type(e).__name__}",
            'traceback': f"Exception ({type(e).__name__}): {str(e)}",
            'tests_run': 0
        }


def _ejecutar_tests_python(test_path: str, state: AgentState) -> Dict[str, Any]:
    """
    Ejecuta tests Python usando pytest.
    
    Args:
        test_path: Ruta al archivo de tests
        state: Estado actual del agente
        
    Returns:
        Dict con 'success', 'output', 'traceback'
    """
    logger.info("▶️ Ejecutando pytest...")
    
    try:
        # Ejecutar pytest con verbose para detalles
        logger.debug(f"Test path: {test_path}")
        result = subprocess.run(
            ['pytest', test_path, '-v', '--tb=short'],
            capture_output=True,
            text=True,
            timeout=60  # 60 segundos de timeout
        )
        
        success = result.returncode == 0
        output = result.stdout + "\n" + result.stderr
        traceback = result.stderr if not success else ""
        
        return {
            'success': success,
            'output': output,
            'traceback': traceback,
            'tests_run': _parsear_resultados_pytest(output)
        }
        
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'output': "Timeout: Los tests tardaron más de 60 segundos",
            'traceback': "TimeoutError: Test execution exceeded 60 seconds",
            'tests_run': 0
        }
    except FileNotFoundError as e:
        # Error al ejecutar pytest
        error_msg = str(e)
        if 'pytest' in error_msg.lower():
            return {
                'success': False,
                'output': f"pytest no está instalado.\n\nEjecute:\n  pip install pytest\n\nO si usa entorno virtual:\n  .venv\\Scripts\\activate\n  pip install pytest",
                'traceback': f"FileNotFoundError: pytest command not found - {error_msg}",
                'tests_run': 0
            }
        else:
            return {
                'success': False,
                'output': f"Archivo no encontrado: {error_msg}\n\nVerifique que existe: {test_path}",
                'traceback': f"FileNotFoundError: Test file not found - {error_msg}",
                'tests_run': 0
            }
    except OSError as e:
        # Error del sistema operativo
        return {
            'success': False,
            'output': f"Error del sistema operativo:\n{str(e)}\n\nArchivo de tests: {test_path}",
            'traceback': f"OSError: {str(e)}",
            'tests_run': 0
        }
    except Exception as e:
        return {
            'success': False,
            'output': f"Error inesperado al ejecutar pytest:\n{str(e)}\n\nTipo: {type(e).__name__}",
            'traceback': f"Exception ({type(e).__name__}): {str(e)}",
            'tests_run': 0
        }


def _parsear_resultados_vitest(output: str) -> Dict[str, int]:
    """Parsea la salida de vitest para extraer estadísticas de tests.
    
    Returns:
        Dict con 'total', 'passed', 'failed'
    """
    # Limpiar códigos ANSI primero
    clean_output = _limpiar_ansi(output)
    
    stats = {'total': 0, 'passed': 0, 'failed': 0}
    
    # Verificar si hay "no tests"
    if 'no tests' in clean_output.lower():
        return stats
    
    # Buscar línea como: "Tests  33 passed (33)" o "Tests  5 passed | 2 failed (7)"
    # También puede ser: "Tests  3 failed | 27 passed (30)" cuando hay fallos
    tests_match = re.search(r'Tests\s+(?:(\d+)\s+failed\s+\|\s+)?(\d+)\s+passed(?:\s+\|\s+(\d+)\s+failed)?\s+\((\d+)\)', clean_output)
    if tests_match:
        # Grupo 1: failed al principio (si existe)
        # Grupo 2: passed (siempre existe)
        # Grupo 3: failed al final (si existe)
        # Grupo 4: total
        failed_first = tests_match.group(1)
        passed = tests_match.group(2)
        failed_last = tests_match.group(3)
        total = tests_match.group(4)
        
        stats['passed'] = int(passed)
        stats['failed'] = int(failed_first) if failed_first else (int(failed_last) if failed_last else 0)
        stats['total'] = int(total)
        return stats
    
    # Buscar "Test Files X failed (Y)" cuando no se ejecutan tests individuales
    test_files_match = re.search(r'Test Files\s+(\d+)\s+failed\s+\((\d+)\)', clean_output)
    if test_files_match:
        stats['failed'] = int(test_files_match.group(1))
        stats['total'] = int(test_files_match.group(2))
        return stats
    
    # Fallback: contar por símbolos
    stats['passed'] = output.count('✓')
    stats['failed'] = output.count('✗') + output.count('×')
    stats['total'] = stats['passed'] + stats['failed']
    
    return stats


def _parsear_resultados_pytest(output: str) -> Dict[str, int]:
    """Parsea la salida de pytest para extraer estadísticas de tests.
    
    Returns:
        Dict con 'total', 'passed', 'failed'
    """
    stats = {'total': 0, 'passed': 0, 'failed': 0}
    
    # Buscar líneas como: "3 passed, 1 failed in 0.12s" o "5 passed in 0.12s"
    passed_match = re.search(r'(\d+)\s+passed', output)
    failed_match = re.search(r'(\d+)\s+failed', output)
    
    if passed_match:
        stats['passed'] = int(passed_match.group(1))
    if failed_match:
        stats['failed'] = int(failed_match.group(1))
    
    stats['total'] = stats['passed'] + stats['failed']
    return stats


def _mostrar_resumen_ejecucion(result: Dict[str, Any]) -> None:
    """Muestra un resumen visual de la ejecución de tests."""
    logger.info("=" * 60)
    logger.info("📋 RESUMEN DE EJECUCIÓN DE TESTS")
    logger.info("-" * 60)
    logger.info(f"Estado: {'✅ PASSED' if result['success'] else '❌ FAILED'}")
    
    # Mostrar estadísticas detalladas si están disponibles
    stats = result.get('tests_run', {})
    if isinstance(stats, dict):
        total = stats.get('total', 0)
        passed = stats.get('passed', 0)
        failed = stats.get('failed', 0)
        logger.info(f"Tests totales: {total}")
        logger.info(f"  ✅ Pasados: {passed}")
        if failed > 0:
            logger.info(f"  ❌ Fallidos: {failed}")
    else:
        # Fallback para formato antiguo (solo número)
        logger.info(f"Tests ejecutados: {stats}")
    
    if not result['success'] and result['traceback']:
        logger.error("🚨 Error principal:")
        # Mostrar solo las primeras líneas del traceback
        traceback_lines = result['traceback'].split('\n')[:10]
        for line in traceback_lines:
            logger.error(f"  {line}")
        if len(result['traceback'].split('\n')) > 10:
            logger.error("  ...")
    
    logger.info("=" * 60)

