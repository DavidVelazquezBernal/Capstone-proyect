"""
Test de funciones de estimación con valores de Fibonacci.
Valida que story_points y effort_hours usen valores enteros de Fibonacci.
"""

from src.tools.azure_devops_integration import estimate_story_points, estimate_effort_hours


def test_story_points_fibonacci():
    """Prueba que los story points sean valores de Fibonacci."""
    print("=" * 80)
    print("📊 TEST: Estimación de Story Points (Serie de Fibonacci)")
    print("=" * 80)
    
    # Valores válidos de Fibonacci para story points
    valid_fibonacci = [1, 2, 3, 5, 8, 13, 21]
    
    test_cases = [
        {
            "objetivo_funcional": "Calcular suma",
            "entradas_esperadas": "a, b",
            "salidas_esperadas": "suma",
            "expected_sp": 1
        },
        {
            "objetivo_funcional": "Implementar una función que calcule el factorial de un número entero positivo",
            "entradas_esperadas": "número entero positivo n",
            "salidas_esperadas": "factorial de n como entero",
            "expected_sp": 2
        },
        {
            "objetivo_funcional": "Crear una clase Calculator con métodos para suma, resta, multiplicación y división",
            "entradas_esperadas": "dos operandos numéricos y el tipo de operación",
            "salidas_esperadas": "resultado de la operación, o error si división por cero",
            "expected_sp": 3
        },
        {
            "objetivo_funcional": "Implementar un algoritmo de ordenamiento QuickSort que ordene un array de números enteros de forma ascendente o descendente según parámetro",
            "entradas_esperadas": "array de números enteros, dirección de ordenamiento (asc/desc)",
            "salidas_esperadas": "array ordenado según criterio especificado, preservando array original",
            "expected_sp": 5
        },
        {
            "objetivo_funcional": "Desarrollar un sistema de autenticación de usuarios con JWT que incluya registro, login, logout, refresh token, validación de permisos basada en roles (admin, user, guest), hash seguro de contraseñas con bcrypt, y middleware de protección de rutas",
            "entradas_esperadas": "credenciales de usuario (email, password), tokens JWT, roles de usuario",
            "salidas_esperadas": "tokens de autenticación (access y refresh), información de usuario autenticado, respuestas de autorización para endpoints protegidos",
            "expected_sp": 13
        }
    ]
    
    print("\n📋 Probando diferentes niveles de complejidad:\n")
    
    all_passed = True
    for i, test in enumerate(test_cases, 1):
        story_points = estimate_story_points(test)
        is_fibonacci = story_points in valid_fibonacci
        
        print(f"Test {i}:")
        print(f"  Objetivo: {test['objetivo_funcional'][:60]}...")
        print(f"  Story Points: {story_points} {'✅' if is_fibonacci else '❌'}")
        print(f"  Es Fibonacci: {'Sí' if is_fibonacci else 'No'}")
        print(f"  Esperado: {test['expected_sp']}")
        
        if not is_fibonacci:
            all_passed = False
            print(f"  ⚠️ ERROR: {story_points} no está en la serie de Fibonacci")
        elif story_points != test['expected_sp']:
            print(f"  ℹ️ INFO: Valor diferente al esperado (pero válido)")
        
        print()
    
    if all_passed:
        print("✅ TODOS los story points usan valores de Fibonacci")
    else:
        print("❌ FALLÓ: Algunos valores NO son de Fibonacci")
    
    return all_passed


def test_effort_hours_fibonacci():
    """Prueba que las horas de esfuerzo sean valores de Fibonacci."""
    print("\n" + "=" * 80)
    print("⏱️ TEST: Estimación de Horas de Esfuerzo (Serie de Fibonacci)")
    print("=" * 80)
    
    # Valores válidos de Fibonacci para effort
    valid_fibonacci = [1, 2, 3, 5, 8, 13, 21]
    
    task_types = [
        "implementation",
        "testing",
        "review",
        "bugfix",
        "research",
        "refactor",
        "documentation",
        "unknown_type"  # Para probar el default
    ]
    
    print("\n📋 Probando diferentes tipos de tareas:\n")
    
    all_passed = True
    for task_type in task_types:
        effort = estimate_effort_hours(task_type)
        is_fibonacci = effort in valid_fibonacci
        is_integer = isinstance(effort, int)
        
        print(f"  Tipo de tarea: {task_type:20} → {effort} horas ", end="")
        
        if is_fibonacci and is_integer:
            print("✅")
        else:
            print("❌")
            all_passed = False
            if not is_integer:
                print(f"    ⚠️ ERROR: {effort} no es un entero")
            if not is_fibonacci:
                print(f"    ⚠️ ERROR: {effort} no está en la serie de Fibonacci")
    
    print()
    if all_passed:
        print("✅ TODAS las estimaciones usan enteros de Fibonacci")
    else:
        print("❌ FALLÓ: Algunas estimaciones son inválidas")
    
    return all_passed


def test_values_are_positive_integers():
    """Verifica que todos los valores sean enteros positivos."""
    print("\n" + "=" * 80)
    print("🔢 TEST: Valores Enteros Positivos")
    print("=" * 80)
    
    # Test story points
    test_req = {
        "objetivo_funcional": "Test",
        "entradas_esperadas": "test",
        "salidas_esperadas": "test"
    }
    
    sp = estimate_story_points(test_req)
    effort = estimate_effort_hours("implementation")
    
    print(f"\n  Story Points: {sp}")
    print(f"    - Es entero: {'✅' if isinstance(sp, int) else '❌'}")
    print(f"    - Es positivo: {'✅' if sp > 0 else '❌'}")
    
    print(f"\n  Effort Hours: {effort}")
    print(f"    - Es entero: {'✅' if isinstance(effort, int) else '❌'}")
    print(f"    - Es positivo: {'✅' if effort > 0 else '❌'}")
    
    all_positive_integers = (
        isinstance(sp, int) and sp > 0 and
        isinstance(effort, int) and effort > 0
    )
    
    print()
    if all_positive_integers:
        print("✅ Todos los valores son enteros positivos")
    else:
        print("❌ Algunos valores NO son enteros positivos")
    
    return all_positive_integers


if __name__ == "__main__":
    print("\n🧮 VALIDACIÓN DE ESTIMACIONES CON FIBONACCI\n")
    
    try:
        test1 = test_story_points_fibonacci()
        test2 = test_effort_hours_fibonacci()
        test3 = test_values_are_positive_integers()
        
        print("\n" + "=" * 80)
        print("📊 RESUMEN DE RESULTADOS")
        print("=" * 80)
        print(f"  Story Points (Fibonacci): {'✅ PASSED' if test1 else '❌ FAILED'}")
        print(f"  Effort Hours (Fibonacci): {'✅ PASSED' if test2 else '❌ FAILED'}")
        print(f"  Enteros Positivos:        {'✅ PASSED' if test3 else '❌ FAILED'}")
        
        if test1 and test2 and test3:
            print("\n✅ TODAS LAS PRUEBAS PASARON")
            print("🎯 El sistema usa correctamente valores de Fibonacci para estimaciones")
        else:
            print("\n⚠️ ALGUNAS PRUEBAS FALLARON")
        
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()
