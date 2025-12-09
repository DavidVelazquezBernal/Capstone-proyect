# 💾 Conversación: Proyecto Multiagente Capstone (LangGraph)

## 🤖 10 Ideas para Proyectos Multiagente (CrewAI / LangChain / LangGraph)

### 1\. Sistema de Investigación y Análisis de Mercado Automatizado

* **Descripción:** Un equipo de agentes simula una firma de consultoría.
    * **Agente 1 (Investigador):** Busca datos y noticias en tiempo real sobre un mercado específico (ej. energías renovables).
    * **Agente 2 (Analista de Datos):** Procesa los datos recopilados, identifica tendencias clave y realiza análisis DAFO.
    * **Agente 3 (Estratega/Reporteador):** Sintetiza las conclusiones en un informe ejecutivo bien estructurado y presenta recomendaciones.
* **Tecnología Clave:** **CrewAI** es ideal para este flujo de trabajo colaborativo.

-----

### 2\. Plataforma de Generación de Contenido SEO Optimizada

* **Descripción:** Un "equipo de marketing" crea un artículo de blog completo basado en un tema.
    * **Agente 1 (Investigador de Palabras Clave):** Utiliza herramientas externas o LLMs para encontrar palabras clave de alto volumen.
    * **Agente 2 (Redactor de Esquemas):** Diseña la estructura del artículo (títulos, subtítulos, puntos clave).
    * **Agente 3 (Escritor):** Redacta el contenido siguiendo el esquema y las directrices SEO.
    * **Agente 4 (Editor/Revisor SEO):** Revisa el borrador para mejorar la legibilidad y la densidad de palabras clave.
* **Tecnología Clave:** **CrewAI** o **LangGraph** para definir un ciclo de edición y revisión estricto.

-----

### 3\. Asistente de Codificación y Depuración con Reingeniería de Prompts

* **Descripción:** Un sistema que toma una descripción de tarea y un fragmento de código problemático.
    * **Agente 1 (Ingeniero de Requisitos):** Interactúa con el usuario para clarificar la descripción de la tarea y el *input* esperado (Reingeniería de Prompts).
    * **Agente 2 (Codificador):** Genera código inicial o corrige errores sintácticos.
    * **Agente 3 (Probador/Depurador):** Escribe pruebas unitarias, ejecuta el código y analiza los *tracebacks*, devolviendo el error al Codificador.
* **Tecnología Clave:** **LangGraph** es perfecto para este **flujo de trabajo cíclico (loop)** de prueba, análisis y corrección.

-----

### 4\. Simulador de Negociación y Contratación

* **Descripción:** Dos o más agentes con objetivos opuestos negocian un contrato o un precio.
    * **Agente 1 (Vendedor/Proveedor):** Objetivo de maximizar el precio y minimizar las concesiones.
    * **Agente 2 (Comprador/Cliente):** Objetivo de minimizar el precio y maximizar los beneficios.
    * **Agente 3 (Mediador/Observador):** Registra las ofertas, asegura el cumplimiento de las reglas y determina el resultado final.
* **Tecnología Clave:** **LangGraph** para modelar estados complejos de negociación y la toma de decisiones basada en el estado actual.

-----

### 5\. Agente de Tutoría Personalizado y Adaptativo

* **Descripción:** Un agente que enseña un concepto (ej. cálculo) adaptando su estilo y nivel de detalle a las respuestas del estudiante.
    * **Agente 1 (Evaluador de Conocimiento):** Analiza las respuestas del usuario para determinar su nivel de comprensión y las lagunas de conocimiento.
    * **Agente 2 (Generador de Contenido):** Adapta la explicación, los ejemplos y las preguntas de seguimiento en función de la evaluación.
    * **Agente 3 (Moderador de Conversación):** Asegura que la conversación se mantenga centrada y ofrece refuerzo positivo.
* **Tecnología Clave:** **LangGraph** con **memoria de conversación** para mantener el estado de aprendizaje del usuario y ramificar el flujo de enseñanza.

-----

### 6\. Sistema de Monitoreo de Redes Sociales para Gestión de Crisis

* **Descripción:** Un equipo que monitorea la opinión pública sobre una marca o tema.
    * **Agente 1 (Rastreador de Tendencias):** Busca menciones y tendencias virales en plataformas simuladas (a través de llamadas a herramientas externas/APIs).
    * **Agente 2 (Analista de Sentimiento):** Clasifica las menciones como positivas, negativas o neutras, e identifica "menciones clave".
    * **Agente 3 (Generador de Alertas):** Si el sentimiento negativo supera un umbral, redacta una alerta de crisis con el resumen de la situación y lo asigna a un Agente de Respuesta.
* **Tecnología Clave:** **CrewAI** para un flujo de trabajo de "observar, analizar, alertar".

-----

### 7\. Agente de Planificación de Viajes con Interacciones Externas

* **Descripción:** Un equipo que planifica un viaje completo (vuelos, alojamiento, actividades).
    * **Agente 1 (Requisitos del Cliente):** Recopila preferencias detalladas del usuario.
    * **Agente 2 (Buscador de Vuelos/Hoteles):** Utiliza *tools* para simular la búsqueda de disponibilidad y precios (o usa APIs reales si es posible).
    * **Agente 3 (Optimizador de Itinerarios):** Organiza la información en un itinerario lógico y ajusta las opciones si las búsquedas fallan (lo que requiere una interacción con Agente 2 y Agente 1).
* **Tecnología Clave:** **CrewAI** con un fuerte enfoque en la **definición de herramientas (`tools`)** para cada agente.

-----

### 8\. Sistema de Generación de Historias con Múltiples Puntos de Vista

* **Descripción:** Un sistema que crea una historia corta con personajes que tienen diferentes conocimientos de los hechos.
    * **Agente 1 (Escritor de Trama Principal):** Define los eventos y el clímax de la historia (el "hecho real").
    * **Agente 2 (Agente de Perspectiva A):** Escribe un capítulo basándose en el conocimiento parcial o sesgado de un personaje específico.
    * **Agente 3 (Agente de Perspectiva B):** Escribe otro capítulo desde un punto de vista diferente.
    * **Agente 4 (Narrador Final):** Fusiona las perspectivas, revelando la verdad al lector.
* **Tecnología Clave:** **LangGraph** para gestionar los estados de la historia y el conocimiento (memoria/contexto) de cada agente.

-----

### 9\. Asistente de Diseño de Bases de Datos Relacionales (Schema Generator)

* **Descripción:** Convierte una descripción de negocio en un esquema de base de datos.
    * **Agente 1 (Analista de Requisitos):** Analiza la descripción del negocio y extrae las entidades principales.
    * **Agente 2 (Modelador de Entidades):** Define las tablas, las columnas y los tipos de datos para cada entidad.
    * **Agente 3 (Modelador de Relaciones):** Determina las claves primarias/foráneas y las relaciones (uno-a-muchos, muchos-a-muchos) entre las tablas.
    * **Resultado:** Un script SQL `CREATE TABLE`.
* **Tecnología Clave:** **CrewAI** para un flujo de trabajo de análisis estructurado.

-----

### 10\. Generador de Puzzles Lógicos con Verificación de Soluciones

* **Descripción:** Un sistema que crea un puzzle lógico (ej. Sudoku o un puzzle de deducción tipo "Einstein's Riddle").
    * **Agente 1 (Diseñador de Puzzles):** Genera las reglas y la solución base.
    * **Agente 2 (Verificador de Soluciones):** Intenta resolver el puzzle basándose en las reglas. Si el puzzle no tiene una solución única o es trivial, lo devuelve al diseñador (ciclo de retroalimentación).
    * **Agente 3 (Redactor de Pistas):** Formula las pistas de forma natural y atractiva.
* **Tecnología Clave:** **LangGraph** para implementar el **ciclo de prueba y error** y asegurar que el puzzle es resoluble y bien definido antes de la presentación final.

-----

## 🛠️ Proyecto Capstone: Asistente de Desarrollo y Depuración Ágil (LangGraph)

Este sistema multiagente automatiza el proceso de toma de requisitos, formalización, codificación, prueba, depuración y validación, todo dentro de un **ciclo de retroalimentación continuo**.

### 1\. ⚙️ Arquitectura del Sistema (LangGraph)

#### **Definición de Nodos (Agentes):**

| Agente | Función Principal | Rol en el Ciclo | Condición de Salida |
| :--- | :--- | :--- | :--- |
| **Agente 1: 🙋‍♂️ Ingeniero de Requisitos** | Clarifica la necesidad del usuario, o el *feedback* de rechazo del Stakeholder. | **Inicio del Ciclo.** | Requisito inicial **clarificado** y validado. |
| **Agente 2: 💼 Product Owner (PO)** | Genera un conjunto de **requisitos funcionales formales**. | **Formalización.** | Requisitos **formales** y **aceptados** por el PO. |
| **Agente 3: 💻 Codificador** | Genera el código Python y corrige errores sintácticos o de *traceback*. | **Desarrollo.** | Código **generado** y listo para pruebas. |
| **Agente 4: 🧪 Probador/Depurador** | Escribe y ejecuta pruebas unitarias (usando una *tool* de ejecución). Analiza los *tracebacks*. | **Control de Calidad (QA).** | **Pasa Pruebas** o **Falla Pruebas** (resultado binario). |
| **Agente 5: ✅ Stakeholder** | Evalúa el código final y el resultado de las pruebas para verificar si cumple la intención de negocio. | **Validación de Negocio.** | **Validado** o **Rechazado** (resultado binario). |

#### **Definición de Transiciones (Edges):**

| Origen | Destino | Condición |
| :--- | :--- | :--- |
| Ingeniero de Requisitos | Product Owner | Siempre (Una vez clarificado el *prompt*) |
| Product Owner | Codificador | Siempre (Una vez formalizados los requisitos) |
| Codificador | Probador/Depurador | Siempre (Una vez generado el código) |
| **Probador/Depurador** | **Codificador** | **Si Falla Pruebas** (Bucle interno de corrección) |
| Probador/Depurador | Stakeholder | **Si Pasa Pruebas** |
| **Stakeholder** | **Ingeniero de Requisitos** | **Si Rechazado** (Fallo conceptual. **Bucle externo**) |
| Stakeholder | **FIN** | **Si Validado** |

-----

### 2\. 📝 Estado y Memoria del Grafo (State)

| Variable de Estado | Tipo | Propósito |
| :--- | :--- | :--- |
| `prompt_inicial` | `str` | El texto inicial del usuario. |
| `requisito_clarificado` | `str` | El *prompt* refinado por el Agente 1. |
| `requisitos_formales` | `str` | La especificación técnica del Agente 2. |
| `codigo_generado` | `str` | El código Python actual. |
| `traceback` | `str` | El resultado del error de ejecución del Agente 4 (si falla). |
| `resultado_pruebas` | `bool` | `True` si pasa las pruebas, `False` si falla. |

-----

## 📝 Borrador de Prompts para Agentes del Sistema Ágil

### 1\. 🙋‍♂️ Ingeniero de Requisitos (Role: Clarificador y Adaptador)

> **Tu rol es el de un Ingeniero de Requisitos experto.**
>
> **Objetivo:** Refinar el `prompt_inicial` o el `feedback_stakeholder` hasta convertirlo en una especificación clara, concisa y completa. Tu resultado debe incluir el lenguaje de programación, *inputs* y *outputs* esperados, y el objetivo funcional exacto.
>
> **Instrucción Principal:** Analiza el texto. Si encuentras ambigüedades, plantea preguntas de clarificación o añade detalles lógicos.
>
> **Output Esperado:** Un único bloque de texto bajo el título "**REQUISITO CLARIFICADO**".

-----

### 2\. 💼 Product Owner (Role: Formalizador de Requisitos)

> **Tu rol es el de un Product Owner estricto y orientado a la entrega.**
>
> **Objetivo:** Recibir el requisito clarificado y transformarlo en una especificación formal y ejecutable.
>
> **Instrucción Principal:** Desglosa el requisito clarificado en: 1. **Objetivo Funcional**. 2. **Lenguaje**. 3. **Función Principal** (Nombre y firma). 4. **Entradas Esperadas**. 5. **Salidas Esperadas**.
>
> **Output Esperado:** Un único bloque de texto bajo el título "**REQUISITOS FORMALES**".

-----

### 3\. 💻 Codificador (Role: Desarrollador y Corrector)

> **Tu rol es el de un Desarrollador de Software Python sénior.**
>
> **Objetivo:** Generar el código Python que **satisface exactamente** todos los puntos de los `requisitos_formales`. Si se proporciona un `traceback`, tu objetivo principal es **identificar la causa raíz de ese error y corregir el código**.
>
> **Instrucción Principal:**
>
> 1.  Si **NO** hay `traceback`, escribe el código desde cero.
> 2.  Si **SÍ** hay `traceback`, analiza el error y corrige el código anterior.
> 3.  El código debe ser una única función autocontenida.
>
> **Output Esperado:** El código Python completo envuelto en un único bloque de código markdown (e.g., \`\`\`python ... \`\`\`).

-----

### 4\. 🧪 Probador/Depurador (Role: QA y Ejecutor de Código)

> **Tu rol es el de un Ingeniero de Control de Calidad (QA) extremadamente riguroso.**
>
> **Objetivo:** Verificar la funcionalidad del `codigo_generado` contra los `requisitos_formales` usando la `CodeExecutorTool`.
>
> **Instrucción Principal:**
>
> 1.  **Genera al menos 2 casos de prueba** (éxito y borde/falla).
> 2.  **Simula la ejecución del código** con los casos de prueba. Analiza la salida o el error.
> 3.  **Determina el resultado:** **PASSED** o **FAILED**.
>
> **Output Esperado:** Un reporte de análisis bajo el título "**REPORTE DE PRUEBAS**". Si es FAILED, debe contener el `traceback` simulado.

-----

### 5\. ✅ Stakeholder (Role: Validador de Negocio Final)

> **Tu rol es el de un Stakeholder de negocio de alto nivel.**
>
> **Objetivo:** Validar si el `codigo_generado`, que ha **pasado las pruebas técnicas**, cumple con la **visión de negocio**.
>
> **Instrucción Principal:** Evalúa si la implementación satisface la necesidad de negocio.
>
>   * **Si es SÍ:** El resultado es **VALIDADO**.
>   * **Si es NO:** El resultado es **RECHAZADO**. Proporciona un **feedback claro** sobre el motivo conceptual.
>
> **Output Esperado:** Un único bloque de texto bajo el título "**VALIDACIÓN FINAL**" que contenga **VALIDADO** o **RECHAZADO** y el **motivo** si es rechazado.

-----

## 🧪 Herramienta para el Probador/Depurador

El **Agente 4** utiliza una herramienta simulada:

| Propiedad | Descripción |
| :--- | :--- |
| **Nombre** | `CodeExecutorTool` |
| **Descripción** | Ejecuta el código Python proporcionado (`code`) con argumentos de prueba (`test_args`) y devuelve el resultado, o un `traceback` si falla. |
| **Inputs** | `code` (string), `test_args` (lista de argumentos de prueba) |
| **Output** | Un diccionario con `{'success': bool, 'output': str, 'error': str}` |

-----

## 🏗️ Estructura de Código LangGraph

### Componentes Principales

1. **Estado del Grafo (AgentState)**: Define las variables compartidas entre agentes
2. **Schemas de Pydantic**: Valida y estructura los requisitos formales
3. **Herramientas (Tools)**: Ejecuta código de forma segura
4. **Nodos de Agentes**: Implementa la lógica de cada agente
5. **Configuración del Grafo**: Define transiciones y flujo de trabajo

### Flujo de Trabajo

```
START → Ingeniero de Requisitos → Product Owner → Codificador → Probador/Depurador
                ↑                                                      ↓
                |                                                   ¿Pasa?
                |                                                      ↓
                |                                                  Stakeholder
                |                                                      ↓
                |                                                 ¿Validado?
                |                                                      ↓
                ←──────────────────────────────────────────────────── NO
                                                                       ↓
                                                                      END
```

### Tecnologías Utilizadas

- **LangGraph**: Framework para construcción de grafos de agentes
- **Google Gemini**: Modelo LLM para generación de contenido
- **Pydantic**: Validación de esquemas JSON
- **E2B Code Interpreter**: Sandbox para ejecución segura de código
- **Python-dotenv**: Gestión de variables de entorno

### Variables de Entorno Requeridas

- `GEMINI_API_KEY`: Clave API de Google Gemini
- `E2B_API_KEY`: Clave API de E2B Code Interpreter

-----

*Documentación extraída del proyecto Capstone Multiagente V2*
