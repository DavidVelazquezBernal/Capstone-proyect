"""
Utilidades para validación de código generado.
Proporciona funciones reutilizables para verificar que el código esté completo y bien formado.
"""

from typing import Tuple


def validate_code_completeness(
    codigo: str, 
    lenguaje: str,
    min_length: int = 50,
    require_test_functions: bool = False
) -> Tuple[bool, str]:
    """
    Valida que el código esté completo y no truncado.
    
    Args:
        codigo: Código a validar
        lenguaje: 'typescript', 'python', 'javascript', etc.
        min_length: Longitud mínima del código
        require_test_functions: Si True, requiere funciones de test (test_* o describe/it)
        
    Returns:
        Tuple (es_valido, mensaje_error)
        - es_valido: True si el código es válido
        - mensaje_error: Descripción del error si no es válido, "" si es válido
    """
    if not codigo or len(codigo) < min_length:
        return False, f"Código demasiado corto (mínimo {min_length} caracteres)"
    
    lenguaje_lower = lenguaje.lower()
    
    if lenguaje_lower in ('typescript', 'javascript', 'ts', 'js'):
        return _validate_typescript_code(codigo, require_test_functions)
    elif lenguaje_lower in ('python', 'py'):
        return _validate_python_code(codigo, require_test_functions)
    else:
        # Para otros lenguajes, solo validación básica
        return _validate_generic_code(codigo)


def _validate_typescript_code(codigo: str, require_test_functions: bool) -> Tuple[bool, str]:
    """
    Valida código TypeScript/JavaScript.
    
    Args:
        codigo: Código TypeScript/JavaScript
        require_test_functions: Si True, requiere funciones de test
        
    Returns:
        Tuple (es_valido, mensaje_error)
    """
    # Eliminar strings y comentarios para análisis preciso
    codigo_sin_strings = _strip_ts_strings_and_comments(codigo)
    
    # Verificar balance de llaves
    llaves_abiertas = codigo_sin_strings.count('{')
    llaves_cerradas = codigo_sin_strings.count('}')
    
    if llaves_abiertas != llaves_cerradas:
        return False, f"Llaves desbalanceadas: {llaves_abiertas} abiertas, {llaves_cerradas} cerradas"
    
    # Verificar balance de paréntesis
    parentesis_abiertos = codigo_sin_strings.count('(')
    parentesis_cerrados = codigo_sin_strings.count(')')
    
    if parentesis_abiertos != parentesis_cerrados:
        return False, f"Paréntesis desbalanceados: {parentesis_abiertos} abiertos, {parentesis_cerrados} cerrados"
    
    # Verificar balance de corchetes
    corchetes_abiertos = codigo_sin_strings.count('[')
    corchetes_cerrados = codigo_sin_strings.count(']')
    
    if corchetes_abiertos != corchetes_cerrados:
        return False, f"Corchetes desbalanceados: {corchetes_abiertos} abiertos, {corchetes_cerrados} cerrados"
    
    # Verificar que termina correctamente
    codigo_limpio = codigo.rstrip()
    if not codigo_limpio:
        return False, "Código vacío después de limpiar espacios"
    
    # Si requiere funciones de test
    if require_test_functions:
        if 'describe(' not in codigo and 'test(' not in codigo and 'it(' not in codigo:
            return False, "No se encontró describe(), test() o it() en el código de tests"
        
        # Verificar que termina con }); o similar (cierre de describe)
        if not (codigo_limpio.endswith(');') or codigo_limpio.endswith('}') or codigo_limpio.endswith('});')):
            return False, "Código de tests no termina correctamente (esperado }); o })"
    
    return True, ""


def _validate_python_code(codigo: str, require_test_functions: bool) -> Tuple[bool, str]:
    """
    Valida código Python.
    
    Args:
        codigo: Código Python
        require_test_functions: Si True, requiere funciones de test
        
    Returns:
        Tuple (es_valido, mensaje_error)
    """
    # Si requiere funciones de test
    if require_test_functions:
        if 'def test_' not in codigo:
            return False, "No se encontraron funciones test_* en el código"
    
    # Verificar indentación consistente (no líneas cortadas)
    lineas = codigo.split('\n')
    for i, linea in enumerate(lineas):
        if linea.strip() and not linea.startswith(' ') and not linea.startswith('def ') and not linea.startswith('class ') and not linea.startswith('import ') and not linea.startswith('from ') and not linea.startswith('@') and not linea.startswith('#'):
            # Línea que no empieza con indentación ni es declaración válida
            if i > 5:  # Ignorar primeras líneas (imports)
                return False, f"Posible código truncado en línea {i+1}"
    
    # Verificar que tiene al menos una definición de función o clase
    if 'def ' not in codigo and 'class ' not in codigo:
        return False, "No se encontraron definiciones de función o clase"
    
    return True, ""


def _validate_generic_code(codigo: str) -> Tuple[bool, str]:
    """
    Validación genérica para lenguajes no específicamente soportados.
    
    Args:
        codigo: Código a validar
        
    Returns:
        Tuple (es_valido, mensaje_error)
    """
    # Validación básica: verificar que no está vacío y tiene contenido significativo
    lineas_significativas = [l for l in codigo.split('\n') if l.strip() and not l.strip().startswith('//') and not l.strip().startswith('#')]
    
    if len(lineas_significativas) < 3:
        return False, "Código tiene muy pocas líneas significativas"
    
    return True, ""


def _strip_ts_strings_and_comments(codigo: str) -> str:
    """
    Elimina strings y comentarios de código TypeScript/JavaScript para análisis sintáctico.
    
    Args:
        codigo: Código TypeScript/JavaScript
        
    Returns:
        Código sin strings ni comentarios
    """
    resultado = []
    i = 0
    in_string = False
    string_char = None
    in_comment = False
    in_multiline_comment = False
    
    while i < len(codigo):
        char = codigo[i]
        
        # Manejo de comentarios multilínea
        if not in_string and not in_comment and i < len(codigo) - 1:
            if codigo[i:i+2] == '/*':
                in_multiline_comment = True
                i += 2
                continue
        
        if in_multiline_comment:
            if i < len(codigo) - 1 and codigo[i:i+2] == '*/':
                in_multiline_comment = False
                i += 2
                continue
            i += 1
            continue
        
        # Manejo de comentarios de línea
        if not in_string and not in_comment and i < len(codigo) - 1:
            if codigo[i:i+2] == '//':
                in_comment = True
                i += 2
                continue
        
        if in_comment:
            if char == '\n':
                in_comment = False
                resultado.append(char)
            i += 1
            continue
        
        # Manejo de strings
        if char in ('"', "'", '`') and (i == 0 or codigo[i-1] != '\\'):
            if not in_string:
                in_string = True
                string_char = char
            elif char == string_char:
                in_string = False
                string_char = None
            i += 1
            continue
        
        if not in_string:
            resultado.append(char)
        
        i += 1
    
    return ''.join(resultado)


def validate_test_code_completeness(codigo: str, lenguaje: str) -> Tuple[bool, str]:
    """
    Valida que el código de tests esté completo y no truncado.
    Wrapper específico para tests que usa validate_code_completeness con require_test_functions=True.
    
    Args:
        codigo: Código de tests generado
        lenguaje: 'typescript' o 'python'
        
    Returns:
        Tuple (es_valido, mensaje_error)
    """
    return validate_code_completeness(
        codigo=codigo,
        lenguaje=lenguaje,
        min_length=50,
        require_test_functions=True
    )
