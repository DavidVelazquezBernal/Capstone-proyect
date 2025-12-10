# Guía Rápida - Nuevo Ejecutor de Pruebas

## 🎯 Descripción

El ejecutor de pruebas ha sido refactorizado para ejecutar directamente los tests unitarios generados usando frameworks estándar (vitest/pytest), eliminando la complejidad del sandbox E2B.

## 🚀 Inicio Rápido

### 1. Instalar Dependencias

**Para proyectos TypeScript:**
```bash
npm install -D vitest
```

**Para proyectos Python:**
```bash
pip install pytest
```

### 2. Verificar Instalación

Ejecuta el script de verificación:
```bash
python test_nuevo_ejecutor_pruebas.py
```

Debería mostrar:
```
✅ vitest instalado: vitest/2.x.x
✅ pytest instalado: pytest 8.x.x
```

### 3. Flujo Completo

El ejecutor se integra automáticamente en el workflow:

```
1. Generador Unit Tests → Crea unit_tests_req1_sq0.test.ts
2. Ejecutor Pruebas → Ejecuta npx vitest run unit_tests_req1_sq0.test.ts
3. Resultados → Estado actualizado + archivos de reporte
```

## 📁 Archivos Generados

### Archivos de Tests (input para ejecutor)
- `output/unit_tests_req1_sq0.test.ts` - Tests de TypeScript
- `output/test_unit_req1_sq0.py` - Tests de Python

### Archivos de Código (ejecutados contra los tests)
- `output/3_codificador_req1_debug0_sq0.ts` - Código TypeScript
- `output/3_codificador_req1_debug0_sq0.py` - Código Python

### Archivos de Resultados (output del ejecutor)
- `output/4_probador_req1_debug0_PASSED.txt` - Tests exitosos
- `output/4_probador_req1_debug0_FAILED.txt` - Tests fallidos
- `output/4_probador_req1_debug0_ERROR.txt` - Errores de ejecución

## 🔍 Ejemplo de Uso Manual

### TypeScript (Vitest)

```bash
cd output/
npx vitest run unit_tests_req1_sq0.test.ts --reporter=verbose
```

**Salida esperada:**
```
 ✓ should correctly add 2 and 3 to get 5
 ✓ should correctly subtract 5 from 2
 ✓ should handle edge cases

Test Files  1 passed (1)
     Tests  3 passed (3)
  Duration  0.23s
```

### Python (Pytest)

```bash
pytest output/test_unit_req1_sq0.py -v --tb=short
```

**Salida esperada:**
```
test_add_positive_numbers PASSED
test_subtract_negative_numbers PASSED
test_edge_cases PASSED

========== 3 passed in 0.12s ==========
```

## 🐛 Debugging

### Error: "No se encontró el archivo de tests"

**Causa:** El generador de tests no se ejecutó o falló.

**Solución:**
1. Verifica que `generador_unit_tests_node` se ejecutó correctamente
2. Revisa logs del generador
3. Busca el archivo en `output/` manualmente

### Error: "vitest/pytest no está instalado"

**Causa:** Framework de testing no instalado.

**Solución:**
```bash
# TypeScript
npm install -D vitest

# Python
pip install pytest
```

### Error: "TimeoutError: Test execution exceeded 60 seconds"

**Causa:** Los tests están tardando demasiado (posible bucle infinito).

**Solución:**
1. Revisa el código generado en busca de bucles infinitos
2. Aumenta el timeout en `ejecutor_pruebas.py` si es necesario
3. Ejecuta los tests manualmente para investigar

### Tests fallan localmente pero pasan en el ejecutor (o viceversa)

**Causa:** Diferencias en el entorno de ejecución.

**Solución:**
1. Verifica que estás en el mismo directorio (`output/`)
2. Comprueba las versiones de vitest/pytest
3. Revisa las importaciones relativas en los tests

## 📊 Comparación: Antes vs Después

| Aspecto | Antes (E2B Sandbox) | Después (Vitest/Pytest) |
|---------|---------------------|-------------------------|
| **Complejidad** | Alta (LLM + API + sandbox) | Baja (ejecución directa) |
| **Dependencias** | E2B API key | npm/pip install |
| **Coste** | $$ (API de pago) | Gratis |
| **Debugging** | Difícil (remoto) | Fácil (local) |
| **Performance** | 5-10 segundos | 1-3 segundos |
| **Reproducibilidad** | No (sandbox único) | Sí (local) |
| **Tests generados** | No usados | Ejecutados directamente |

## 🎓 Mejores Prácticas

### 1. Mantén los archivos de tests
Los tests generados son valiosos:
- Pueden reutilizarse en CI/CD
- Sirven como documentación del código
- Pueden ejecutarse localmente para debugging

### 2. Revisa los tests fallidos manualmente
Si un test falla:
```bash
# Ejecuta manualmente para ver el error completo
cd output/
npx vitest run unit_tests_req1_sq0.test.ts
```

### 3. Añade los tests a tu repositorio
```bash
git add output/*.test.ts output/*.py
git commit -m "Add generated unit tests"
```

### 4. Configura CI/CD
Ejemplo para GitHub Actions:
```yaml
- name: Run Generated Tests
  run: |
    cd output/
    npx vitest run *.test.ts
```

## 🔧 Configuración Avanzada

### Personalizar timeout
Edita `src/agents/ejecutor_pruebas.py`:
```python
result = subprocess.run(
    [...],
    timeout=120  # Cambiar de 60 a 120 segundos
)
```

### Añadir flags adicionales a vitest
```python
['npx', 'vitest', 'run', test_path, 
 '--reporter=verbose',
 '--coverage',  # Añadir cobertura
 '--silent']    # Modo silencioso
```

### Añadir flags adicionales a pytest
```python
['pytest', test_path, 
 '-v',
 '--tb=short',
 '--cov',       # Añadir cobertura
 '--maxfail=1'] # Detener en primer fallo
```

## 📚 Recursos

- [Vitest Documentation](https://vitest.dev/)
- [Pytest Documentation](https://docs.pytest.org/)
- [REFACTOR_EJECUTOR_PRUEBAS.md](./REFACTOR_EJECUTOR_PRUEBAS.md) - Documentación técnica completa

## ⚠️ Notas Importantes

1. **E2B ya no es necesario**: Puedes eliminar la dependencia de `e2b_code_interpreter`
2. **Function calling en LLM**: Sigue disponible si es necesario, pero el ejecutor no lo usa
3. **Compatibilidad**: Los archivos antiguos de tests no se ven afectados
4. **Migración**: No requiere cambios en otros agentes del workflow

## 🆘 Soporte

Si encuentras problemas:
1. Ejecuta `python test_nuevo_ejecutor_pruebas.py` para diagnóstico
2. Revisa los logs en `output/4_probador_*`
3. Ejecuta los tests manualmente para más detalles
4. Verifica que vitest/pytest estén instalados correctamente
