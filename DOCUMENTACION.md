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

Este sistema multiagente automatiza el proceso de formalización de requisitos, codificación, análisis de calidad, generación de tests, prueba, depuración y validación, todo dentro de un **ciclo de retroalimentación continuo**.

### 1. ⚙️ Arquitectura del Sistema (LangGraph)

#### **Definición de Nodos (Agentes):**

| Agente | Función Principal | Rol en el Ciclo | Condición de Salida |
| :--- | :--- | :--- | :--- |
| **Agente 1: 💼 Product Owner (PO)** | Genera un conjunto de **requisitos funcionales formales** y crea PBIs en Azure DevOps (opcional). | **Formalización.** | Requisitos **formales** y **aceptados** por el PO. |
| **Agente 2: 💻 Desarrollador** | Genera el código Python/TypeScript y corrige errores. Crea Tasks en Azure DevOps (opcional). | **Desarrollo.** | Código **generado** y listo para análisis. |
| **Agente 3: 🔍 Analizador SonarQube** | Analiza calidad del código (bugs, vulnerabilidades, code smells). | **Control de Calidad.** | **Calidad OK** o **Requiere Corrección**. |
| **Agente 4: 🧪 Generador Unit Tests** | Genera tests unitarios profesionales con vitest/pytest. | **Generación de Tests.** | Tests **generados** y listos para ejecución. |
| **Agente 5: 🧪 Ejecutor de Pruebas** | Ejecuta tests unitarios y adjunta resultados a Azure DevOps (opcional). | **Ejecución de Tests.** | **Pasa Pruebas** o **Falla Pruebas**. |
| **Agente 6: ✅ Stakeholder** | Evalúa el código final y adjunta a Azure DevOps (opcional). | **Validación de Negocio.** | **Validado** o **Rechazado**. |

#### **Definición de Transiciones (Edges):**

| Origen | Destino | Condición |
| :--- | :--- | :--- |
| START | Product Owner | Siempre (Inicio del flujo) |
| Product Owner | Desarrollador | Siempre (Una vez formalizados los requisitos) |
| Desarrollador | Analizador SonarQube | Siempre (Una vez generado el código) |
| **Analizador SonarQube** | **Desarrollador** | **Si Calidad Falla** (Bucle de calidad - max 3 intentos) |
| Analizador SonarQube | Generador Unit Tests | **Si Calidad OK** |
| Generador Unit Tests | Ejecutor de Pruebas | Siempre (Una vez generados los tests) |
| **Ejecutor de Pruebas** | **Desarrollador** | **Si Falla Pruebas** (Bucle de depuración - max 3 intentos) |
| Ejecutor de Pruebas | Stakeholder | **Si Pasa Pruebas** |
| **Stakeholder** | **Product Owner** | **Si Rechazado** (Bucle de validación - max 1 intento) |
| Stakeholder | **FIN** | **Si Validado** |

-----

### 2\. 📝 Estado y Memoria del Grafo (State)

| Variable de Estado | Tipo | Propósito |
| :--- | :--- | :--- |
| `prompt_inicial` | `str` | El texto inicial del usuario. |
| `requisitos_formales` | `str` | La especificación técnica del Product Owner (JSON). |
| `codigo_generado` | `str` | El código Python/TypeScript actual. |
| `lenguaje_detectado` | `str` | Lenguaje detectado (python/typescript). |
| `sonarqube_passed` | `bool` | `True` si pasa análisis de calidad. |
| `sonarqube_report` | `str` | Reporte de análisis de SonarQube. |
| `tests_unitarios_generados` | `str` | Tests unitarios generados. |
| `pruebas_superadas` | `bool` | `True` si pasa las pruebas, `False` si falla. |
| `resultado_ejecucion` | `str` | Resultado de ejecución de tests. |
| `validado` | `bool` | `True` si Stakeholder valida. |
| `azure_pbi_id` | `int \| None` | ID del PBI en Azure DevOps. |
| `azure_implementation_task_id` | `int \| None` | ID de Task de Implementación. |
| `azure_testing_task_id` | `int \| None` | ID de Task de Testing. |
| `attempt_count` | `int` | Contador de ciclos completos. |
| `debug_attempt_count` | `int` | Contador de intentos de depuración. |
| `sonarqube_attempt_count` | `int` | Contador de intentos de calidad. |

-----

## 📝 Borrador de Prompts para Agentes del Sistema Ágil

### 1\. 💼 Product Owner (Role: Formalizador de Requisitos)

> **Tu rol es el de un Product Owner estricto y orientado a la entrega.**
>
> **Objetivo:** Recibir el prompt inicial y transformarlo en una especificación formal y ejecutable en formato JSON.
>
> **Instrucción Principal:** Desglosa el requisito en: 1. **Objetivo Funcional**. 2. **Lenguaje**. 3. **Función Principal** (Nombre y firma). 4. **Entradas Esperadas**. 5. **Salidas Esperadas**. 6. **Criterios de Aceptación**.
>
> **Output Esperado:** JSON estructurado con requisitos formales.
>
> **Integración Azure DevOps:** Si está habilitado, crea automáticamente un PBI con la especificación.

-----

### 2\. 💻 Desarrollador (Role: Desarrollador y Corrector)

> **Tu rol es el de un Desarrollador de Software sénior (Python/TypeScript).**
>
> **Objetivo:** Generar código que **satisface exactamente** todos los puntos de los `requisitos_formales`. Si hay feedback de SonarQube o errores de tests, corregir el código.
>
> **Instrucción Principal:**
>
> 1.  Si es primera ejecución, escribe el código desde cero.
> 2.  Si hay issues de SonarQube, corrige los problemas de calidad.
> 3.  Si hay errores de tests, corrige los bugs funcionales.
> 4.  El código debe seguir mejores prácticas y estándares.
>
> **Output Esperado:** Código Python/TypeScript completo en bloque markdown.
>
> **Integración Azure DevOps:** En primera ejecución, crea Tasks de Implementación y Testing.

-----

### 3\. 🔍 Analizador SonarQube (Role: Control de Calidad)

> **Tu rol es el de un Analista de Calidad de Código.**
>
> **Objetivo:** Analizar el código generado en busca de bugs, vulnerabilidades y code smells.
>
> **Instrucción Principal:**
>
> 1.  Ejecutar análisis estático del código.
> 2.  Identificar issues por severidad (BLOCKER, CRITICAL, MAJOR, MINOR).
> 3.  Generar reporte detallado con instrucciones de corrección.
>
> **Criterios de Aceptación:**
> - 0 issues BLOCKER
> - Máximo 2 issues CRITICAL
>
> **Output Esperado:** Reporte de análisis y decisión PASSED/FAILED.

-----

### 4\. 🧪 Generador Unit Tests (Role: Generador de Tests)

> **Tu rol es el de un Ingeniero de Testing experto.**
>
> **Objetivo:** Generar tests unitarios profesionales para el código generado.
>
> **Instrucción Principal:**
>
> 1.  Detectar lenguaje del código (Python/TypeScript).
> 2.  Generar tests con framework apropiado (pytest/vitest).
> 3.  Incluir casos normales, edge cases y manejo de errores.
> 4.  Usar sintaxis moderna y mejores prácticas.
>
> **Output Esperado:** Archivo de tests completo y ejecutable.

-----

### 5\. 🧪 Ejecutor de Pruebas (Role: QA y Ejecutor de Tests)

> **Tu rol es el de un Ejecutor de Tests automatizado.**
>
> **Objetivo:** Ejecutar los tests unitarios generados y reportar resultados.
>
> **Instrucción Principal:**
>
> 1.  Ejecutar tests con vitest (TypeScript) o pytest (Python).
> 2.  Parsear resultados y extraer estadísticas.
> 3.  Generar reporte con tests pasados/fallidos.
> 4.  Si hay errores, proporcionar traceback detallado.
>
> **Output Esperado:** Reporte de ejecución con estadísticas y decisión PASSED/FAILED.
>
> **Integración Azure DevOps:** Si tests pasan, adjuntar archivo de tests al PBI y Task de Testing.

-----

### 6\. ✅ Stakeholder (Role: Validador de Negocio Final)

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
>
> **Integración Azure DevOps:** Si valida, adjuntar código final al PBI y Task de Implementación.

-----

## 🧪 Herramientas del Sistema

### CodeExecutorTool
Ejecuta código Python/TypeScript de forma segura usando E2B Code Interpreter.

### SonarQubeMCP
Analiza calidad de código mediante Model Context Protocol.

### AzureDevOpsClient
Integración con Azure DevOps para crear PBIs, Tasks y adjuntar archivos.

### GitHubService
Integración con GitHub para commits y push automáticos (opcional).

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
START → Product Owner → Desarrollador → SonarQube → Generador Tests → Ejecutor Tests → Stakeholder
           ↑                ↑              ↓                                    ↓              ↓
           |                |         ¿Calidad OK?                           ¿Pasa?       ¿Validado?
           |                ←─── NO (max 3)                        ← NO (max 3)              ↓
           |                                                                                 ↓
           ←─────────────────────────────────────────────────────────────────────────── NO
                                                                                          ↓
                                                                                         END
```

### Tecnologías Utilizadas

- **LangGraph**: Framework para construcción de grafos de agentes
- **Google Gemini 2.5 Flash**: Modelo LLM para generación de contenido
- **Pydantic**: Validación de esquemas JSON
- **E2B Code Interpreter**: Sandbox para ejecución segura de código
- **Vitest**: Framework de testing para TypeScript
- **Pytest**: Framework de testing para Python
- **SonarQube MCP**: Análisis estático de calidad de código
- **Azure DevOps REST API**: Integración con Azure DevOps (opcional)
- **Python-dotenv**: Gestión de variables de entorno

### Variables de Entorno Requeridas

- `GEMINI_API_KEY`: Clave API de Google Gemini (requerida)
- `E2B_API_KEY`: Clave API de E2B Code Interpreter (requerida)
- `SONARQUBE_URL`: URL de SonarQube (opcional)
- `SONARQUBE_TOKEN`: Token de SonarQube (opcional)
- `SONARQUBE_PROJECT_KEY`: Clave de proyecto SonarQube (opcional)
- `AZURE_DEVOPS_ENABLED`: Habilitar integración con Azure DevOps (opcional)
- `AZURE_DEVOPS_ORG`: Organización de Azure DevOps (opcional)
- `AZURE_DEVOPS_PROJECT`: Proyecto de Azure DevOps (opcional)
- `AZURE_DEVOPS_PAT`: Personal Access Token de Azure DevOps (opcional)
- `LOG_LEVEL`: Nivel de logging (opcional, default: INFO)
- `LOG_TO_FILE`: Guardar logs en archivo (opcional, default: true)

-----

*Documentación extraída del proyecto Capstone Multiagente V2*
