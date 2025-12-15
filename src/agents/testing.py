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


def _limpiar_codigo_tests_llm(code: str) -> str:
    code = re.sub(r'^```(?:typescript|python|ts|py)\s*\n?', '', code, flags=re.MULTILINE)
    code = re.sub(r'\n?```\s*$', '', code)
    code = re.sub(r'^(?:typescript|python|ts|py)\s*\n', '', code, flags=re.MULTILINE)
    return code.strip()


def _formatear_float_literal(value: str, max_decimals: int = 5) -> str:
    try:
        v = float(value)
    except Exception:
        return value
    v = round(v, max_decimals)
    txt = f"{v:.{max_decimals}f}".rstrip('0').rstrip('.')
    return txt


def _postprocesar_tests_typescript(code: str) -> str:
    code = re.sub(r'\btoBeCloseTo\(\s*([^,\n\)]+?)\s*,\s*[^\)\n]+\)', r'toBeCloseTo(\1)', code)

    code = re.sub(r'\.toBe\(\s*-0(?:\.0+)?\s*\)', '.toBe(-0)', code)
    code = re.sub(r'\.toBe\(\s*0(?:\.0+)?\s*\)', '.toBe(0)', code)

    def _repl_to_be_float(m: re.Match) -> str:
        try:
            v = float(m.group(1))
        except Exception:
            v = None
        if v is not None and v == 0.0:
            # Preservar semántica de -0 vs +0 si el autor la quería en el literal
            return f".toBe({m.group(1).strip()})"
        return f".toBeCloseTo({_formatear_float_literal(m.group(1))})"

    code = re.sub(r'\.toBe\(\s*([-+]?\d+\.\d+)\s*\)', _repl_to_be_float, code)

    def _repl_any_float(m: re.Match) -> str:
        return _formatear_float_literal(m.group(1))

    code = re.sub(r'(?<![A-Za-z0-9_])([-+]?\d+\.\d{6,})(?![A-Za-z0-9_])', _repl_any_float, code)
    return code


def _es_fallo_probablemente_de_tests(lenguaje: str, output: str, traceback: str, test_filename: str) -> tuple[bool, str]:
    combined = _limpiar_ansi((output or "") + "\n" + (traceback or ""))
    low = combined.lower()

    if lenguaje.lower() == 'typescript':
        patterns = (
            'syntaxerror',
            'unexpected token',
            'parse error',
            'parsing error',
            'failed to parse',
            'transform failed',
            'cannot find module',
            'failed to resolve import',
            'does not provide an export named',
            'ts1005',
            'ts1109',
            'error: expected',
        )
        if any(p in low for p in patterns) and (test_filename.lower() in low or '.spec.' in low):
            return True, 'Error de parsing/sintaxis en tests'

        if 'expected:' in low and 'received:' in low and ('.' in low or ' -0' in low or '-0' in low):
            if ('expected:' in low and '-0' in low) or ('received:' in low and '-0' in low):
                return True, 'Diferencia -0 vs +0 en aserciones'
            if re.search(r'expected:\s*[-+]?\d+\.\d+', combined, flags=re.IGNORECASE) or re.search(r'received:\s*[-+]?\d+\.\d+', combined, flags=re.IGNORECASE):
                return True, 'Mismatch con decimales (probable expected incorrecto)'

    else:
        if ('syntaxerror' in low or 'indentationerror' in low) and test_filename.lower() in low:
            return True, 'Error de sintaxis/indentación en tests'
        if 'assert' in low and ('expected' in low and 'got' in low) and re.search(r'\d+\.\d+', combined):
            return True, 'Mismatch con decimales (probable expected incorrecto)'
        if ('-0' in low or 'negative zero' in low) and test_filename.lower() in low:
            return True, 'Diferencia -0 vs +0 en aserciones'

    return False, ''


def _strip_ts_strings_and_comments(code: str) -> str:
    i = 0
    n = len(code)
    out_chars: list[str] = []

    NORMAL = 0
    SQ = 1
    DQ = 2
    BT = 3
    LINE_COMMENT = 4
    BLOCK_COMMENT = 5

    state = NORMAL
    while i < n:
        ch = code[i]
        nxt = code[i + 1] if i + 1 < n else ""

        if state == NORMAL:
            if ch == "'":
                state = SQ
                out_chars.append(' ')
                i += 1
                continue
            if ch == '"':
                state = DQ
                out_chars.append(' ')
                i += 1
                continue
            if ch == '`':
                state = BT
                out_chars.append(' ')
                i += 1
                continue
            if ch == '/' and nxt == '/':
                state = LINE_COMMENT
                out_chars.append(' ')
                out_chars.append(' ')
                i += 2
                continue
            if ch == '/' and nxt == '*':
                state = BLOCK_COMMENT
                out_chars.append(' ')
                out_chars.append(' ')
                i += 2
                continue

            out_chars.append(ch)
            i += 1
            continue

        if state in (SQ, DQ, BT):
            quote = "'" if state == SQ else ('"' if state == DQ else '`')
            if ch == '\\':
                out_chars.append(' ')
                if i + 1 < n:
                    out_chars.append(' ')
                    i += 2
                else:
                    i += 1
                continue
            if ch == quote:
                out_chars.append(' ')
                state = NORMAL
                i += 1
                continue

            out_chars.append('\n' if ch == '\n' else ' ')
            i += 1
            continue

        if state == LINE_COMMENT:
            if ch == '\n':
                out_chars.append('\n')
                state = NORMAL
                i += 1
            else:
                out_chars.append(' ')
                i += 1
            continue

        if state == BLOCK_COMMENT:
            if ch == '*' and nxt == '/':
                out_chars.append(' ')
                out_chars.append(' ')
                state = NORMAL
                i += 2
            else:
                out_chars.append('\n' if ch == '\n' else ' ')
                i += 1
            continue

    return ''.join(out_chars)


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
        codigo_sin_strings = _strip_ts_strings_and_comments(codigo)
        llaves_abiertas = codigo_sin_strings.count('{')
        llaves_cerradas = codigo_sin_strings.count('}')
        parentesis_abiertos = codigo_sin_strings.count('(')
        parentesis_cerrados = codigo_sin_strings.count(')')
        
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
        test_filename = f"{nombre_base}.spec.ts"
    else:  # Python
        codigo_filename = f"{nombre_base}.py"
        test_filename = f"{nombre_base}.spec.py"
    
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

    prompt_formateado = (
        prompt_formateado
        + "\n\nIMPORTANTE: Devuelve el CÓDIGO COMPLETO y BIEN FORMADO (sin truncar). "
          "No uses Markdown ni fences ```; responde únicamente con código TypeScript. "
          "Genera un archivo de tests CORTO: un solo bloque describe() y como máximo 6 tests (it/test). Evita describe anidados y evita bloques enormes. "
          "Evita tests innecesarios: cada test debe aportar cobertura NUEVA. Elimina/evita tests repetidos, duplicados o equivalentes. "
          "Cierra todas las llaves `{}` y paréntesis `()` y finaliza correctamente los bloques (por ejemplo `describe(...) { ... });`). "
          "La ÚLTIMA línea del archivo debe ser exactamente: `});`"
    )

    if lenguaje.lower() == 'typescript':
        prompt_formateado += (
            "\n\nRegla de decimales: si usas números en coma flotante (con decimales), usa como máximo 5 decimales en los literales. "
            "Si comparas resultados con decimales, usa siempre `toBeCloseTo(valor)` con UN SOLO argumento (no uses el segundo parámetro), y no uses `toBe()` para decimales."
            "\nNota sobre -0: en JavaScript existe `-0` y es un valor válido. Si el resultado correcto puede ser `-0`, es válido escribir expectativas como `toBe(-0)` (no lo fuerces a `0`). "
            "Si NO te importa distinguir entre `0` y `-0`, usa `toBeCloseTo(0)` o normaliza con `Math.abs(valor)` antes de comparar."
        )
    
    # Llamar al LLM para generar los tests
    logger.info("🤖 Llamando a LLM para generar tests...")
    start_time = time.time()
    tests_generados = call_gemini(prompt_formateado, "")
    duration = time.time() - start_time
    
    log_llm_call(logger, "generacion_tests", duration=duration)
    
    tests_generados = _limpiar_codigo_tests_llm(tests_generados)
    if lenguaje.lower() == 'typescript':
        tests_generados = _postprocesar_tests_typescript(tests_generados)
    
    # Validar que el código de tests esté completo (no truncado)
    codigo_valido, error_validacion = _validar_codigo_tests_completo(tests_generados, lenguaje)
    if not codigo_valido:
        logger.warning(f"⚠️ Código de tests posiblemente incompleto: {error_validacion}")
        logger.info("🔄 Intentando regenerar tests con más tokens...")
        
        # Reintentar con instrucción de código completo
        prompt_retry = (
            prompt_formateado
            + "\n\nREINTENTO: El código anterior estaba incompleto o mal cerrado. "
              "Devuelve un archivo de tests MÁS CORTO (máximo 6 tests) y SIN describe anidados. "
              "Evita tests innecesarios y elimina/evita casos repetidos o duplicados; cada test debe ser único y aportar cobertura nueva. "
              "No incluyas explicaciones. La ÚLTIMA línea del archivo debe ser exactamente: `});`"
        )
        tests_generados = call_gemini(prompt_retry, "")
        tests_generados = _limpiar_codigo_tests_llm(tests_generados)
        if lenguaje.lower() == 'typescript':
            tests_generados = _postprocesar_tests_typescript(tests_generados)
        
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
        #logger.warning(f"⚠️ No se encontró el archivo de código: {code_path}")
        guardar_fichero_texto(codigo_filename, codigo_limpio, directorio=settings.OUTPUT_DIR)
        logger.info("✅ Código guardado desde el estado")
    
    logger.info(f"📄 Archivo de tests: {test_filename}")
    logger.info(f"📄 Archivo de código: {codigo_filename}")
    
    # Ejecutar tests según el lenguaje
    try:
        max_test_fix_attempts = max(0, int(getattr(settings, 'MAX_TEST_FIX_ATTEMPTS', 0)))
        test_fix_attempt = 0
        result: Dict[str, Any] | None = None

        while True:
            if lenguaje.lower() == 'typescript':
                result = _ejecutar_tests_typescript(test_path, code_path, state)
            else:  # Python
                result = _ejecutar_tests_python(test_path, state)

            if result.get('success'):
                break

            should_fix, reason = _es_fallo_probablemente_de_tests(
                lenguaje=lenguaje,
                output=result.get('output', ''),
                traceback=result.get('traceback', ''),
                test_filename=test_filename
            )
            if (not should_fix) or (test_fix_attempt >= max_test_fix_attempts):
                break

            test_fix_attempt += 1
            logger.warning(f"⚠️ Tests fallaron por causa probable de tests ({reason}). Regenerando tests {test_fix_attempt}/{max_test_fix_attempts}...")

            fallo_ctx = _limpiar_ansi((result.get('traceback', '') or '') + "\n" + (result.get('output', '') or ''))
            if len(fallo_ctx) > 3500:
                fallo_ctx = fallo_ctx[-3500:]

            prompt_fix = (
                prompt_formateado
                + "\n\nFALLO AL EJECUTAR TESTS. Analiza el error y REGENERA el archivo de tests corrigiendo exclusivamente el código de tests."
                  "\nNo modifiques el código de producción. No uses Markdown. Mantén el archivo muy corto (máximo 6 tests, sin describe anidados) y bien cerrado."
                  "\n\nSalida del runner (resumen):\n"
                + fallo_ctx
            )
            tests_nuevos = call_gemini(prompt_fix, "")
            tests_nuevos = _limpiar_codigo_tests_llm(tests_nuevos)
            if lenguaje.lower() == 'typescript':
                tests_nuevos = _postprocesar_tests_typescript(tests_nuevos)

            codigo_valido_fix, error_fix = _validar_codigo_tests_completo(tests_nuevos, lenguaje)
            if not codigo_valido_fix:
                logger.warning(f"⚠️ Tests regenerados posiblemente incompletos: {error_fix}")

            resultado_guardado_fix = guardar_fichero_texto(
                test_filename,
                tests_nuevos,
                directorio=settings.OUTPUT_DIR
            )
            log_file_operation(logger, "guardar", test_path, success=resultado_guardado_fix)
            tests_generados = tests_nuevos
            state['tests_unitarios_generados'] = tests_generados

        # ============================================
        # FASE 3: EVALUACIÓN Y ACTUALIZACIÓN DE ESTADO
        # ============================================
        if result is None:
            raise RuntimeError('No se pudo ejecutar tests')

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
            
            # === GITHUB: Agregar tests al branch existente y crear PR ===
            if settings.GITHUB_ENABLED:
                try:
                    from datetime import datetime
                    
                    logger.info("=" * 60)
                    logger.info("🐙 GITHUB - Agregando tests y creando PR")
                    logger.info("-" * 60)
                    
                    # 1. Copiar archivo de tests al repositorio local (GITHUB_REPO_PATH/src/test/)
                    repo_path = settings.GITHUB_REPO_PATH
                    test_dir = os.path.join(repo_path, "src", "test")
                    os.makedirs(test_dir, exist_ok=True)
                    
                    test_dest = os.path.join(test_dir, test_filename)
                    with open(test_dest, 'w', encoding='utf-8') as f:
                        f.write(tests_generados)
                    logger.info(f"🧪 Tests copiados a: {test_dest}")
                    
                    # 2. Usar el branch existente (creado por Desarrollador) o crear uno nuevo
                    branch_name = state.get('github_branch_name')
                    if not branch_name:
                        # Si no hay branch previo, crear uno nuevo
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        branch_name = f"AI_TEST_{nombre_base}_{timestamp}"
                        logger.info(f"📌 Creando nuevo branch: {branch_name}")
                    else:
                        logger.info(f"📌 Usando branch existente: {branch_name}")
                    
                    # 3. Preparar SOLO el archivo de tests para commit
                    files_to_commit = {
                        f"src/test/{test_filename}": tests_generados
                    }
                    
                    # 4. Crear commit con tests y push a remoto
                    commit_message = f"test: Add unit tests for {nombre_base}\n\nGenerated by AI Testing Agent\n- Tests: {test_filename}\n- Total: {stats.get('total', 0)} tests passed"
                    
                    success_commit, commit_sha = github_service.create_branch_and_commit(
                        branch_name=branch_name,
                        files=files_to_commit,
                        commit_message=commit_message
                    )
                    
                    if success_commit:
                        state['github_branch_name'] = branch_name
                        logger.info(f"✅ Tests pusheados a branch '{branch_name}'")
                        logger.info(f"   🧪 Archivo: src/test/{test_filename}")
                        logger.info(f"   🔗 Commit SHA: {commit_sha[:7]}")
                        
                        # 5. Crear Pull Request (solo si no existe ya)
                        if not state.get('github_pr_number'):
                            pr_title = f"AI_PR_{nombre_base.replace('_', ' ').title()}"
                            pr_body = f"""## 🤖 Pull Request Generada Automáticamente

### 📋 Descripción
Este código fue generado automáticamente por el sistema de desarrollo multiagente.

### 📁 Archivos incluidos
- `src/{codigo_filename}` - Implementación principal (por Desarrollador)
- `src/test/{test_filename}` - Tests unitarios (por Testing)

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
                            logger.info(f"ℹ️ PR #{state['github_pr_number']} ya existe")
                    else:
                        logger.warning("⚠️ No se pudo agregar tests al branch")
                    
                    logger.info("=" * 60)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error en operaciones de GitHub: {e}")
                    logger.debug(f"Stack trace: {e}", exc_info=True)
            # === FIN: GitHub tests y PR ===
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
