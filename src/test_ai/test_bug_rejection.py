"""
Test para verificar que SonarQube rechaza código con BUGS
"""

import sys
from pathlib import Path

# Añadir src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from tools.sonarqube_mcp import es_codigo_aceptable


def test_rechaza_bugs():
    """Verifica que se rechace código con BUGS"""
    
    print("\n🧪 Test 1: Código con 1 BUG (debe rechazar)")
    resultado_con_bug = {
        "success": True,
        "summary": {
            "by_severity": {
                "BLOCKER": 0,
                "CRITICAL": 0,
                "MAJOR": 2,
                "MINOR": 1
            },
            "by_type": {
                "BUG": 1,  # <-- HAY UN BUG
                "CODE_SMELL": 2,
                "VULNERABILITY": 0
            }
        }
    }
    
    aceptable = es_codigo_aceptable(resultado_con_bug)
    print(f"   Resultado: {'✅ RECHAZADO' if not aceptable else '❌ APROBADO (ERROR!)'}")
    assert not aceptable, "Debería rechazar código con BUGS"
    
    print("\n🧪 Test 2: Código sin BUGS, sin BLOCKERS, 2 CRITICAL (debe aprobar)")
    resultado_sin_bug = {
        "success": True,
        "summary": {
            "by_severity": {
                "BLOCKER": 0,
                "CRITICAL": 2,
                "MAJOR": 3,
                "MINOR": 5
            },
            "by_type": {
                "BUG": 0,  # <-- SIN BUGS
                "CODE_SMELL": 8,
                "VULNERABILITY": 0
            }
        }
    }
    
    aceptable = es_codigo_aceptable(resultado_sin_bug)
    print(f"   Resultado: {'✅ APROBADO' if aceptable else '❌ RECHAZADO (ERROR!)'}")
    assert aceptable, "Debería aprobar código sin BUGS y con 2 CRITICAL"
    
    print("\n🧪 Test 3: Código con 1 BLOCKER (debe rechazar)")
    resultado_con_blocker = {
        "success": True,
        "summary": {
            "by_severity": {
                "BLOCKER": 1,  # <-- HAY UN BLOCKER
                "CRITICAL": 0,
                "MAJOR": 0,
                "MINOR": 0
            },
            "by_type": {
                "BUG": 0,
                "CODE_SMELL": 1,
                "VULNERABILITY": 0
            }
        }
    }
    
    aceptable = es_codigo_aceptable(resultado_con_blocker)
    print(f"   Resultado: {'✅ RECHAZADO' if not aceptable else '❌ APROBADO (ERROR!)'}")
    assert not aceptable, "Debería rechazar código con BLOCKER"
    
    print("\n🧪 Test 4: Código con 3 CRITICAL (debe rechazar)")
    resultado_con_3_critical = {
        "success": True,
        "summary": {
            "by_severity": {
                "BLOCKER": 0,
                "CRITICAL": 3,  # <-- MÁS DE 2 CRITICAL
                "MAJOR": 0,
                "MINOR": 0
            },
            "by_type": {
                "BUG": 0,
                "CODE_SMELL": 3,
                "VULNERABILITY": 0
            }
        }
    }
    
    aceptable = es_codigo_aceptable(resultado_con_3_critical)
    print(f"   Resultado: {'✅ RECHAZADO' if not aceptable else '❌ APROBADO (ERROR!)'}")
    assert not aceptable, "Debería rechazar código con más de 2 CRITICAL"
    
    print("\n🧪 Test 5: Código perfecto (debe aprobar)")
    resultado_perfecto = {
        "success": True,
        "summary": {
            "by_severity": {
                "BLOCKER": 0,
                "CRITICAL": 0,
                "MAJOR": 0,
                "MINOR": 0
            },
            "by_type": {
                "BUG": 0,
                "CODE_SMELL": 0,
                "VULNERABILITY": 0
            }
        }
    }
    
    aceptable = es_codigo_aceptable(resultado_perfecto)
    print(f"   Resultado: {'✅ APROBADO' if aceptable else '❌ RECHAZADO (ERROR!)'}")
    assert aceptable, "Debería aprobar código perfecto"
    
    print("\n" + "=" * 60)
    print("✅ TODOS LOS TESTS PASARON")
    print("=" * 60)
    print("\n📋 Criterios de Aceptación de SonarQube:")
    print("   ✓ 0 BLOCKER")
    print("   ✓ Máximo 2 CRITICAL")
    print("   ✓ 0 BUGS (de cualquier severidad)")
    print("=" * 60)


if __name__ == "__main__":
    test_rechaza_bugs()
