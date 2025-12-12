"""
Agente: Testing (Generador y Ejecutor de Unit Tests)
Responsable de generar tests unitarios con LLM y ejecutarlos con vitest/pytest.
Combina las responsabilidades de generación y ejecución en un único agente cohesivo.
"""

import os
import re
import json
import time
import subprocess
import logging
from typing import Dict, Any
from models.state import AgentState
from config.prompts import Prompts
from config.prompt_templates import PromptTemplates
from config.settings import settings
from llm.gemini_client import call_gemini
from tools.file_utils import guardar_fichero_texto, detectar_lenguaje_y_extension, extraer_nombre_archivo, limpiar_codigo_markdown
from services.azure_devops_service import azure_service
from services.github_service import github_service
from utils.logger import setup_logger, log_agent_execution, log_llm_call, log_file_operation

logger = setup_logger(__name__, level=settings.get_log_level(), agent_mode=True)


def _limpiar_ansi(text: str) -> str:
    """Elimina códigos de escape ANSI (colores) del texto."""
    ansi_escape = re.compile(r'\x1b\[[0-9;]*[mGKHF]')
    return ansi_escape.sub('', text)


def _validar_codigo_tests_completo(codigo: str, lenguaje: str) -> tuple[bool, str]:
    """
    Valida que el código de tests esté completo y no truncado.
    
    Args:
        codigo: Código de tests generado
        lenguaje: 'typescript' o 'python'
        
    Returns:
        Tuple (es_valido, mensaje_error)
    """
    if not codigo or len(codigo) < 50:
        return False, "Código demasiado corto"
    
    # Contar llaves/paréntesis para detectar código truncado
    if lenguaje.lower() == 'typescript':
        # TypeScript: verificar balance de llaves y paréntesis
        llaves_abiertas = codigo.count('{')
        llaves_cerradas = codigo.count('}')
        parentesis_abiertos = codigo.count('(')
        parentesis_cerrados = codigo.count(')')
        
        if llaves_abiertas != llaves_cerradas:
            return False, f"Llaves desbalanceadas: {llaves_abiertas} abiertas, {llaves_cerradas} cerradas"
        
        if parentesis_abiertos != parentesis_cerrados:
            return False, f"Paréntesis desbalanceados: {parentesis_abiertos} abiertos, {parentesis_cerrados} cerrados"
        
        # Verificar que termina con }); o similar (cierre de describe)
        codigo_limpio = codigo.rstrip()
        if not (codigo_limpio.endswith(');') or codigo_limpio.endswith('}') or codigo_limpio.endswith('});')):
            return False, "Código no termina correctamente (esperado }); o })"
        
        # Verificar que tiene al menos un describe y un it/test
        if 'describe(' not in codigo and 'test(' not in codigo:
            return False, "No se encontró describe() o test() en el código"
            
    else:  # Python
        # Python: verificar que tiene funciones de test
        if 'def test_' not in codigo:
            return False, "No se encontraron funciones test_* en el código"
        
        # Verificar indentación consistente (no líneas cortadas)
        lineas = codigo.split('\n')
        for i, linea in enumerate(lineas):
            if linea.strip() and not linea.startswith(' ') and not linea.startswith('def ') and not linea.startswith('class ') and not linea.startswith('import ') and not linea.startswith('from ') and not linea.startswith('@') and not linea.startswith('#'):
                # Línea que no empieza con indentación ni es declaración válida
                if i > 5:  # Ignorar primeras líneas (imports)
                    return False, f"Posible código truncado en línea {i+1}"
    
    return True, ""


def testing_node(state: AgentState) -> AgentState:
    """
    Nodo de Testing - Genera y ejecuta tests unitarios.
    
    Flujo:
    1. Generar tests unitarios con LLM (vitest/pytest)
    2. Guardar archivo de tests
    3. Ejecutar tests con el framework apropiado
    4. Parsear resultados y actualizar estado
    """
    print()  # Línea en blanco para separación visual
    logger.info("=" * 60)
    logger.info("🧪 TESTING - INICIO")
    logger.info("=" * 60)
    
    log_agent_execution(logger, "Testing", "iniciado", {
        "requisito_id": state['attempt_count'],
        "debug_attempt": state['debug_attempt_count']
    })
    
    # === INICIO: Actualizar estado del Work Item de Testing a "In Progress" ===
    if (settings.AZURE_DEVOPS_ENABLED and 
        state.get('azure_testing_task_id') and 
        state['debug_attempt_count'] == 0):  # Solo en la primera ejecución
        
        try:
            task_id = state['azure_testing_task_id']
            logger.info(f"🔄 Actualizando estado de Task de Testing #{task_id} a 'In Progress'...")
            
            success = azure_service.update_testing_task_to_in_progress(task_id)
            
            if success:
                logger.info(f"✅ Task #{task_id} actualizada a 'In Progress'")
            else:
                logger.warning(f"⚠️ No se pudo actualizar el estado de la Task #{task_id}")
                
        except Exception as e:
            logger.warning(f"⚠️ Error al actualizar estado del work item: {e}")
            logger.debug(f"Stack trace: {e}", exc_info=True)
    # === FIN: Actualización de estado en Azure DevOps ===
    
    # Detectar lenguaje del código
    lenguaje, extension, patron_limpieza = detectar_lenguaje_y_extension(
        state.get('requisitos_formales', '')
    )
    codigo_limpio = limpiar_codigo_markdown(state['codigo_generado'])
    
    logger.info(f"🔍 Lenguaje detectado: {lenguaje}")
    
    # Determinar nombres de archivos
    attempt = state['attempt_count']
    sq_attempt = state['sonarqube_attempt_count']
    debug_attempt = state['debug_attempt_count']
    
    # Extraer nombre descriptivo del archivo desde requisitos formales
    nombre_base = extraer_nombre_archivo(state.get('requisitos_formales', ''))
    
    if lenguaje.lower() == 'typescript':
        codigo_filename = f"{nombre_base}.ts"
        test_filename = f"test_{nombre_base}.spec.ts"
    else:  # Python
        codigo_filename = f"{nombre_base}.py"
        test_filename = f"test_{nombre_base}.spec.py"
    
    code_path = os.path.join(settings.OUTPUT_DIR, codigo_filename)
    test_path = os.path.join(settings.OUTPUT_DIR, test_filename)
    
    logger.debug(f"Archivo de código: {codigo_filename}")
    logger.debug(f"Archivo de tests: {test_filename}")
    
    # ============================================
    # FASE 1: GENERACIÓN DE TESTS (LLM)
    # ============================================
    logger.info("🧪 Generando tests unitarios...")
    
    # Usar ChatPromptTemplate
    logger.debug("🔗 Usando ChatPromptTemplate de LangChain")
    prompt_formateado = PromptTemplates.format_generador_uts(
        codigo_generado=state['codigo_generado'],
        requisitos_formales=state['requisitos_formales'],
        lenguaje=lenguaje,
        nombre_archivo_codigo=codigo_filename
    )
    
    # Llamar al LLM para generar los tests
    logger.info("🤖 Llamando a LLM para generar tests...")
    start_time = time.time()
    tests_generados = call_gemini(prompt_formateado, "")
    duration = time.time() - start_time
    
    log_llm_call(logger, "generacion_tests", duration=duration)
    
    # Limpiar bloques de código markdown
    tests_generados = re.sub(r'^```(?:typescript|python|ts|py)\s*\n?', '', tests_generados, flags=re.MULTILINE)
    tests_generados = re.sub(r'\n?```\s*$', '', tests_generados)
    tests_generados = re.sub(r'^(?:typescript|python|ts|py)\s*\n', '', tests_generados, flags=re.MULTILINE)
    tests_generados = tests_generados.strip()
    
    # Validar que el código de tests esté completo (no truncado)
    codigo_valido, error_validacion = _validar_codigo_tests_completo(tests_generados, lenguaje)
    if not codigo_valido:
        logger.warning(f"⚠️ Código de tests posiblemente incompleto: {error_validacion}")
        logger.info("🔄 Intentando regenerar tests con más tokens...")
        
        # Reintentar con instrucción de código completo
        prompt_retry = prompt_formateado + "\n\nIMPORTANTE: Asegúrate de generar el código COMPLETO. No lo cortes. Cierra todos los bloques y funciones."
        tests_generados = call_gemini(prompt_retry, "")
        
        # Limpiar de nuevo
        tests_generados = re.sub(r'^```(?:typescript|python|ts|py)\s*\n?', '', tests_generados, flags=re.MULTILINE)
        tests_generados = re.sub(r'\n?```\s*$', '', tests_generados)
        tests_generados = re.sub(r'^(?:typescript|python|ts|py)\s*\n', '', tests_generados, flags=re.MULTILINE)
        tests_generados = tests_generados.strip()
        
        # Validar de nuevo
        codigo_valido2, error2 = _validar_codigo_tests_completo(tests_generados, lenguaje)
        if not codigo_valido2:
            logger.error(f"❌ Tests siguen incompletos después de reintento: {error2}")
    
    # Guardar tests generados
    resultado_guardado = guardar_fichero_texto(
        test_filename,
        tests_generados,
        directorio=settings.OUTPUT_DIR
    )
    
    logger.info(f"✅ Tests generados y guardados: {test_filename}")
    log_file_operation(logger, "guardar", test_path, success=resultado_guardado)
    
    # Almacenar los tests en el estado
    state['tests_unitarios_generados'] = tests_generados
    
    # ============================================
    # FASE 2: EJECUCIÓN DE TESTS
    # ============================================
    logger.info("⚡ Ejecutando tests unitarios...")
    
    # Verificar que existe el archivo de tests
    if not os.path.exists(test_path):
        logger.error(f"❌ No se encontró el archivo de tests: {test_path}")
        state['pruebas_superadas'] = False
        state['traceback'] = f"No se encontró el archivo de tests: {test_filename}"
        state['debug_attempt_count'] += 1
        
        guardar_fichero_texto(
            f"4_testing_req{attempt}_debug{debug_attempt}_ERROR.txt",
            f"Status: ERROR\n\nError: Archivo de tests no encontrado\n{test_path}",
            directorio=settings.OUTPUT_DIR
        )
        
        log_file_operation(logger, "buscar", test_path, success=False, error="Archivo no encontrado")
        return state
    
    # Verificar que existe el archivo de código
    if not os.path.exists(code_path):
        logger.warning(f"⚠️ No se encontró el archivo de código: {code_path}")
        guardar_fichero_texto(codigo_filename, codigo_limpio, directorio=settings.OUTPUT_DIR)
        logger.info("✅ Código guardado desde el estado")
    
    logger.info(f"📄 Archivo de tests: {test_filename}")
    logger.info(f"📄 Archivo de código: {codigo_filename}")
    
    # Ejecutar tests según el lenguaje
    try:
        if lenguaje.lower() == 'typescript':
            result = _ejecutar_tests_typescript(test_path, code_path, state)
        else:  # Python
            result = _ejecutar_tests_python(test_path, state)
        
        # ============================================
        # FASE 3: EVALUACIÓN Y ACTUALIZACIÓN DE ESTADO
        # ============================================
        state['pruebas_superadas'] = result['success']
        state['traceback'] = result['traceback']
        
        if result['success']:
            # Tests pasaron - resetear contador de debug
            state['debug_attempt_count'] = 0
            
            # Obtener estadísticas
            stats = result.get('tests_run', {})
            if isinstance(stats, dict):
                total = stats.get('total', 0)
                passed = stats.get('passed', 0)
                failed = stats.get('failed', 0)
                logger.info(f"✅ Tests PASSED - Total: {total}, Pasados: {passed}, Fallidos: {failed}")
                
                log_agent_execution(
                    logger,
                    "Testing",
                    "Tests exitosos",
                    {"total": total, "passed": passed, "failed": failed}
                )
            else:
                logger.info("✅ Tests PASSED")
            
            # Guardar resultado exitoso
            clean_output = _limpiar_ansi(result['output'])
            stats_summary = ""
            if isinstance(stats, dict):
                stats_summary = f"\nEstadísticas:\n  Total: {stats.get('total', 0)}\n  Pasados: {stats.get('passed', 0)}\n  Fallidos: {stats.get('failed', 0)}\n"
            
            output_content = f"Status: PASSED{stats_summary}\n{'='*60}\n{clean_output}"
            nombre_archivo = f"4_testing_req{attempt}_debug{debug_attempt}_PASSED.txt"
            guardar_fichero_texto(
                nombre_archivo,
                output_content,
                directorio=settings.OUTPUT_DIR
            )
            
            log_file_operation(logger, "guardar", f"{settings.OUTPUT_DIR}/{nombre_archivo}", success=True)
            
            # === AZURE DEVOPS: Adjuntar archivo de tests cuando pasen ===
            if state.get('azure_pbi_id') and state.get('azure_testing_task_id'):
                try:
                    total = stats.get('total', 0) if isinstance(stats, dict) else 0
                    
                    azure_service.attach_tests_and_add_success_comment(
                        state=state,
                        test_file_path=test_path,
                        total_tests=total
                    )
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error en operaciones de Azure DevOps: {e}")
            # === FIN: Adjuntar tests a Azure DevOps ===
            
            # === GITHUB: Crear branch, commit y PR cuando tests pasen ===
            if settings.GITHUB_ENABLED:
                try:
                    from datetime import datetime
                    import shutil
                    
                    # Generar nombre del branch
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    branch_name = f"feature/ai-generated-{nombre_base}-{timestamp}"
                    
                    logger.info("=" * 60)
                    logger.info("🐙 GITHUB - Creando branch y PR")
                    logger.info("-" * 60)
                    
                    # Copiar archivos al repositorio local antes de crear el branch
                    repo_path = settings.GITHUB_REPO_PATH
                    src_dir = os.path.join(repo_path, "src")
                    test_dir = os.path.join(repo_path, "src", "test")
                    
                    # Crear directorios si no existen
                    os.makedirs(src_dir, exist_ok=True)
                    os.makedirs(test_dir, exist_ok=True)
                    
                    # Copiar archivo de código a src/
                    codigo_dest = os.path.join(src_dir, codigo_filename)
                    with open(codigo_dest, 'w', encoding='utf-8') as f:
                        f.write(codigo_limpio)
                    logger.info(f"📄 Código copiado a: {codigo_dest}")
                    
                    # Copiar archivo de tests a src/test/
                    test_dest = os.path.join(test_dir, test_filename)
                    with open(test_dest, 'w', encoding='utf-8') as f:
                        f.write(tests_generados)
                    logger.info(f"🧪 Tests copiados a: {test_dest}")
                    
                    # Preparar archivos para commit (rutas relativas en el repo)
                    files_to_commit = {
                        f"src/{codigo_filename}": codigo_limpio,
                        f"src/test/{test_filename}": tests_generados
                    }
                    
                    # Crear branch y commit
                    commit_message = f"feat: Add {nombre_base} implementation and tests\n\nGenerated by AI Development Agent\n- Implementation: {codigo_filename}\n- Tests: {test_filename} ({stats.get('total', 0)} tests passed)"
                    
                    success_commit, commit_sha = github_service.create_branch_and_commit(
                        branch_name=branch_name,
                        files=files_to_commit,
                        commit_message=commit_message
                    )
                    
                    if success_commit:
                        state['github_branch_name'] = branch_name
                        logger.info(f"✅ Branch '{branch_name}' creado con commit {commit_sha[:7]}")
                        
                        # Crear Pull Request
                        pr_title = f"[AI-Generated] {nombre_base.replace('_', ' ').title()}"
                        pr_body = f"""## 🤖 Pull Request Generada Automáticamente

### 📋 Descripción
Este código fue generado automáticamente por el sistema de desarrollo multiagente.

### 📁 Archivos incluidos
- `src/{codigo_filename}` - Implementación principal
- `src/test/{test_filename}` - Tests unitarios

### ✅ Estado de Tests
- **Total:** {stats.get('total', 0)}
- **Pasados:** {stats.get('passed', 0)}
- **Fallidos:** {stats.get('failed', 0)}

### 🔍 Revisión
Esta PR será revisada automáticamente por el agente RevisorCodigo.

---
*Generado por AI Development Agent*
"""
                        
                        success_pr, pr_number, pr_url = github_service.create_pull_request(
                            branch_name=branch_name,
                            title=pr_title,
                            body=pr_body
                        )
                        
                        if success_pr:
                            state['github_pr_number'] = pr_number
                            state['github_pr_url'] = pr_url
                            logger.info(f"✅ PR #{pr_number} creada: {pr_url}")
                        else:
                            logger.warning("⚠️ No se pudo crear la PR")
                    else:
                        logger.warning("⚠️ No se pudo crear el branch y commit")
                    
                    logger.info("=" * 60)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error en operaciones de GitHub: {e}")
                    logger.debug(f"Stack trace: {e}", exc_info=True)
            # === FIN: GitHub branch y PR ===
        else:
            # Tests fallaron - incrementar contador de debug
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
                    "Testing",
                    "Tests fallidos",
                    {"total": total, "passed": passed, "failed": failed},
                    level=logging.ERROR
                )
            else:
                logger.error("❌ Tests FAILED")
            
            logger.info(f"🔄 Intento de depuración: {state['debug_attempt_count']}/{state['max_debug_attempts']}")
            
            # Guardar resultado fallido
            clean_output = _limpiar_ansi(result['output'])
            clean_traceback = _limpiar_ansi(result['traceback'])
            stats_summary = ""
            if isinstance(stats, dict):
                stats_summary = f"\nEstadísticas:\n  Total: {stats.get('total', 0)}\n  Pasados: {stats.get('passed', 0)}\n  Fallidos: {stats.get('failed', 0)}\n"
            
            output_content = f"Status: FAILED{stats_summary}\n{'='*60}\n\nTraceback:\n{clean_traceback}\n\n{'='*60}\n{clean_output}"
            nombre_archivo = f"4_testing_req{attempt}_debug{debug_attempt}_FAILED.txt"
            guardar_fichero_texto(
                nombre_archivo,
                output_content,
                directorio=settings.OUTPUT_DIR
            )
            
            log_file_operation(logger, "guardar", f"{settings.OUTPUT_DIR}/{nombre_archivo}", success=True)
            
            # === AZURE DEVOPS: Agregar comentario de fallo ===
            if settings.AZURE_DEVOPS_ENABLED and state.get('azure_testing_task_id'):
                try:
                    azure_service.add_test_failure_comment(
                        task_id=state['azure_testing_task_id'],
                        attempt=state['debug_attempt_count'],
                        max_attempts=state['max_debug_attempts'],
                        total=total,
                        passed=passed,
                        failed=failed,
                        report_file=nombre_archivo
                    )
                    logger.info(f"📝 Comentario de fallo agregado a Task #{state['azure_testing_task_id']}")
                except Exception as e:
                    logger.warning(f"⚠️ No se pudo agregar comentario en Azure DevOps: {e}")
            # === FIN: Comentario en Azure DevOps ===
        
        # Mostrar resumen
        _mostrar_resumen_ejecucion(result)
        
    except Exception as e:
        logger.exception(f"❌ ERROR durante la ejecución: {e}")
        state['pruebas_superadas'] = False
        state['traceback'] = f"ERROR de ejecución: {str(e)}"
        state['debug_attempt_count'] += 1
        
        guardar_fichero_texto(
            f"4_testing_req{attempt}_debug{debug_attempt}_ERROR.txt",
            f"Status: ERROR\n\nError de ejecución:\n{str(e)}",
            directorio=settings.OUTPUT_DIR
        )
    
    logger.info("=" * 60)
    logger.info("🧪 TESTING - FIN")
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
        Dict con 'success', 'output', 'traceback', 'tests_run'
    """
    logger.info("▶️ Ejecutando vitest...")
    
    original_dir = os.getcwd()
    output_dir = os.path.abspath(settings.OUTPUT_DIR)
    
    try:
        os.chdir(output_dir)
        logger.debug(f"Directorio de trabajo: {output_dir}")
        
        # Asegurar que existe package.json
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
            logger.info(f"ℹ️ package.json creado en {output_dir}")
        
        # Ejecutar vitest con idioma inglés para mensajes consistentes
        env = os.environ.copy()
        env['LANG'] = 'en_US.UTF-8'
        env['LC_ALL'] = 'en_US.UTF-8'
        
        result = subprocess.run(
            ['npx', 'vitest', 'run', os.path.basename(test_path), '--reporter=verbose'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=60,
            shell=True,
            env=env
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
            'tests_run': {'total': 0, 'passed': 0, 'failed': 0}
        }
    except FileNotFoundError as e:
        os.chdir(original_dir)
        return {
            'success': False,
            'output': f"Node.js/npx no está instalado o no está en el PATH.\n\nVerifique:\n  1. Node.js instalado: node --version\n  2. npx disponible: npx --version\n  3. Vitest instalado en output/: cd output && npm install -D vitest",
            'traceback': f"FileNotFoundError: npx command not found - {str(e)}",
            'tests_run': {'total': 0, 'passed': 0, 'failed': 0}
        }
    except Exception as e:
        os.chdir(original_dir)
        return {
            'success': False,
            'output': f"Error inesperado al ejecutar vitest:\n{str(e)}\n\nTipo: {type(e).__name__}",
            'traceback': f"Exception ({type(e).__name__}): {str(e)}",
            'tests_run': {'total': 0, 'passed': 0, 'failed': 0}
        }


def _ejecutar_tests_python(test_path: str, state: AgentState) -> Dict[str, Any]:
    """
    Ejecuta tests Python usando pytest.
    
    Args:
        test_path: Ruta al archivo de tests
        state: Estado actual del agente
        
    Returns:
        Dict con 'success', 'output', 'traceback', 'tests_run'
    """
    logger.info("▶️ Ejecutando pytest...")
    
    try:
        logger.debug(f"Test path: {test_path}")
        result = subprocess.run(
            ['pytest', test_path, '-v', '--tb=short'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=60
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
            'tests_run': {'total': 0, 'passed': 0, 'failed': 0}
        }
    except FileNotFoundError as e:
        error_msg = str(e)
        if 'pytest' in error_msg.lower():
            return {
                'success': False,
                'output': f"pytest no está instalado.\n\nEjecute:\n  pip install pytest\n\nO si usa entorno virtual:\n  .venv\\Scripts\\activate\n  pip install pytest",
                'traceback': f"FileNotFoundError: pytest command not found - {error_msg}",
                'tests_run': {'total': 0, 'passed': 0, 'failed': 0}
            }
        else:
            return {
                'success': False,
                'output': f"Archivo no encontrado: {error_msg}\n\nVerifique que existe: {test_path}",
                'traceback': f"FileNotFoundError: Test file not found - {error_msg}",
                'tests_run': {'total': 0, 'passed': 0, 'failed': 0}
            }
    except Exception as e:
        return {
            'success': False,
            'output': f"Error inesperado al ejecutar pytest:\n{str(e)}\n\nTipo: {type(e).__name__}",
            'traceback': f"Exception ({type(e).__name__}): {str(e)}",
            'tests_run': {'total': 0, 'passed': 0, 'failed': 0}
        }


def _parsear_resultados_vitest(output: str) -> Dict[str, int]:
    """Parsea la salida de vitest para extraer estadísticas."""
    clean_output = _limpiar_ansi(output)
    stats = {'total': 0, 'passed': 0, 'failed': 0}
    
    if 'no tests' in clean_output.lower():
        return stats
    
    # Buscar línea como: "Tests  33 passed (33)" o "Tests  5 passed | 2 failed (7)"
    tests_match = re.search(r'Tests\s+(?:(\d+)\s+failed\s+\|\s+)?(\d+)\s+passed(?:\s+\|\s+(\d+)\s+failed)?\s+\((\d+)\)', clean_output)
    if tests_match:
        failed_first = tests_match.group(1)
        passed = tests_match.group(2)
        failed_last = tests_match.group(3)
        total = tests_match.group(4)
        
        stats['passed'] = int(passed)
        stats['failed'] = int(failed_first) if failed_first else (int(failed_last) if failed_last else 0)
        stats['total'] = int(total)
        return stats
    
    # Fallback: contar por símbolos
    stats['passed'] = output.count('✓')
    stats['failed'] = output.count('✗') + output.count('×')
    stats['total'] = stats['passed'] + stats['failed']
    
    return stats


def _parsear_resultados_pytest(output: str) -> Dict[str, int]:
    """Parsea la salida de pytest para extraer estadísticas."""
    stats = {'total': 0, 'passed': 0, 'failed': 0}
    
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
    print()
    logger.info("=" * 60)
    logger.info("📊 RESUMEN DE EJECUCIÓN DE TESTS")
    logger.info("-" * 60)
    logger.info(f"Estado: {'✅ PASSED' if result['success'] else '❌ FAILED'}")
    
    stats = result.get('tests_run', {})
    if isinstance(stats, dict):
        total = stats.get('total', 0)
        passed = stats.get('passed', 0)
        failed = stats.get('failed', 0)
        logger.info(f"Tests totales: {total}")
        logger.info(f"  ✅ Pasados: {passed}")
        if failed > 0:
            logger.info(f"  ❌ Fallidos: {failed}")
    
    if not result['success'] and result['traceback']:
        logger.error("🚨 Error principal:")
        traceback_lines = result['traceback'].split('\n')[:10]
        for line in traceback_lines:
            logger.error(f"  {line}")
        if len(result['traceback'].split('\n')) > 10:
            logger.error("  ...")
    
    logger.info("=" * 60)
