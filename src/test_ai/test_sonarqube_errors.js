// Archivo de prueba con errores comunes detectables por SonarQube

// ERROR 1: Variables no usadas
var unusedVariable = "esto no se usa";
let anotherUnused = 42;

// ERROR 2: Uso de var en lugar de let/const
var oldStyleVar = "debería ser let o const";

// ERROR 3: Comparación con == en lugar de ===
function compareValues(a, b) {
    if (a == b) {  // Debería ser ===
        return true;
    }
    return false;
}

// ERROR 4: Función compleja con muchos parámetros
function complexFunction(param1, param2, param3, param4, param5, param6, param7, param8) {
    return param1 + param2 + param3 + param4 + param5 + param6 + param7 + param8;
}

// ERROR 5: Código duplicado
function calculateSum1(a, b) {
    var result = a + b;
    console.log("Result: " + result);
    return result;
}

function calculateSum2(x, y) {
    var result = x + y;
    console.log("Result: " + result);
    return result;
}

// ERROR 6: Función vacía
function emptyFunction() {
}

// ERROR 7: Console.log en código de producción
console.log("Debug message");
console.error("Error message");

// ERROR 8: Try-catch vacío
try {
    riskyOperation();
} catch (e) {
    // Catch vacío - mala práctica
}

// ERROR 9: Función con demasiada complejidad cognitiva
function complexLogic(x, y, z) {
    if (x > 0) {
        if (y > 0) {
            if (z > 0) {
                if (x > y) {
                    if (y > z) {
                        return x + y + z;
                    } else {
                        return x - y - z;
                    }
                } else {
                    return y + z;
                }
            } else {
                return x + y;
            }
        } else {
            return x;
        }
    } else {
        return 0;
    }
}

// ERROR 10: Uso de eval (muy peligroso)
function dangerousEval(code) {
    return eval(code);
}

// ERROR 11: Comparación con NaN incorrecta
function checkNaN(value) {
    if (value == NaN) {  // Siempre false, debería usar isNaN()
        return true;
    }
    return false;
}

// ERROR 12: Array vacío como default
function processArray(arr = []) {
    arr.push("item");
    return arr;
}

// ERROR 13: Función que siempre retorna el mismo valor
function alwaysTrue() {
    return true;
    console.log("Esto nunca se ejecuta");  // Código inalcanzable
}

// ERROR 14: Uso de arguments (deprecated)
function oldStyleFunction() {
    console.log(arguments);
}

// ERROR 15: Callback hell
function callbackHell() {
    setTimeout(function () {
        setTimeout(function () {
            setTimeout(function () {
                console.log("Done");
            }, 100);
        }, 100);
    }, 100);
}

module.exports = {
    compareValues,
    complexFunction,
    calculateSum1,
    calculateSum2
};
