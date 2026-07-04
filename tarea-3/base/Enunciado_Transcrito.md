# Tarea N°3
## Simulación de un sistema estocástico real

**Pontificia Universidad Católica de Chile**
Escuela de Ingeniería

*ICS2123 – Modelos Estocásticos — Tarea N°3*

---

### Información general

| | | | |
|---|---|---|---|
| **Curso** | ICS2123 – Modelos Estocásticos | **Sección** | 2 |
| **Profesor** | Manuel Pérez | **Entrega** | 07 de Julio, 23:59 |

---

## Objetivo de la tarea

El objetivo de esta tarea es que las y los estudiantes apliquen los conceptos, resultados y herramientas estudiadas en el curso para modelar un problema real con componentes aleatorias, construir un modelo de simulación y utilizarlo para responder una pregunta concreta o apoyar una decisión.

En esta tarea la simulación debe ser la parte central del trabajo. No basta con ejecutar una sola corrida ni con usar la simulación únicamente para reproducir una fórmula conocida. El modelo computacional debe utilizarse para estimar medidas de desempeño, cuantificar incertidumbre, comparar escenarios y fundamentar una recomendación.

> **Idea central.** La tarea debe recorrer el siguiente arco:
>
> `Problema real ⟶ Modelo estocástico ⟶ Simulación ⟶ Análisis ⟶ Decisión`

---

## Instrucciones

1. La tarea tendrá un plazo de 10 días a partir de su publicación y deberá ser entregada a más tardar en la fecha indicada en el encabezado.

2. La tarea debe ser realizada en grupos de **hasta 4 integrantes**. Se deberá entregar un único archivo comprimido por grupo.

3. En esta tarea está permitido utilizar herramientas de inteligencia artificial, así como otros recursos de apoyo computacional o bibliográfico. Sin embargo, todo uso de estos recursos debe ser declarado explícitamente en una sección final titulada, por ejemplo, *"Referencias y uso de recursos"*, indicando brevemente qué herramientas se utilizaron y con qué propósito.

4. La entrega deberá contener, al menos:
   - el informe con el desarrollo y respuesta de la tarea;
   - los códigos, planillas o archivos de apoyo utilizados para simulaciones, gráficos, procesamiento de datos o cálculos realizados en Python u otro medio equivalente;
   - instrucciones breves para reproducir los resultados.

   No se aceptará una entrega que contenga solo el informe sin los archivos de respaldo utilizados en su elaboración.

5. **Foro de preguntas.** Se abrirá un foro en Canvas para que puedan realizar preguntas sobre la tarea. Las dudas deberán canalizarse preferentemente por ese medio, de modo que las respuestas sean visibles para todo el curso.

6. También podrán utilizar el foro para formar grupos.

---

## Respecto de la tarea

La tarea consiste en buscar un problema real, de libre elección, en el que sea posible estudiar una situación relevante mediante herramientas de simulación vistas en el curso. En particular, se espera que el grupo identifique una problemática concreta y formule una pregunta que pueda ser respondida o analizada a partir de un modelo estocástico y su simulación. El dominio de aplicación es libre: pueden trabajar, por ejemplo, en contextos de logística, transporte, confiabilidad, salud, finanzas, energía, deportes, telecomunicaciones, manufactura, servicios digitales u otros ámbitos de interés para el grupo. El modelo puede incorporar distintas herramientas del curso, como procesos de Poisson, cadenas de Markov, sistemas de espera o simulación de eventos discretos, entre otras, siempre que la simulación cumpla un rol central en el trabajo. En particular, no será suficiente un desarrollo meramente analítico ni una aplicación directa de una fórmula conocida. Se espera que el trabajo compare, al menos, un escenario base y dos escenarios alternativos relevantes, de modo que la simulación permita evaluar medidas de desempeño, cuantificar incertidumbre y apoyar una recomendación o decisión final.

---

## Contenido del informe

El informe debe ser autocontenido y permitir entender con claridad cuál es el problema estudiado, cómo fue modelado, cómo se simuló y qué conclusiones se obtienen. Como mínimo, debe incluir los siguientes elementos.

### 1. Problema, pregunta y modelo

Deben presentar el sistema real o fenómeno que desean estudiar, explicar brevemente por qué es relevante y formular una pregunta concreta que el trabajo buscará responder. Luego deben describir el modelo estocástico propuesto, definiendo sus componentes esenciales: variables de estado, eventos o transiciones relevantes, parámetros, entradas aleatorias, supuestos, condiciones iniciales, criterio de término y medidas de desempeño. También deben justificar por qué el modelo representa razonablemente la situación estudiada.

### 2. Datos y parametrización

Deben explicar de dónde provienen los datos o parámetros utilizados, cómo fueron procesados y qué supuestos debieron introducir cuando no existió información suficiente. Se espera que utilicen datos reales siempre que sea posible y que toda fuente externa sea pública, verificable y esté correctamente citada. Además, deben indicar qué distribuciones eligieron para las principales entradas aleatorias y dar alguna justificación de esa elección. Si ciertos parámetros fueron supuestos, esto debe quedar claramente señalado.

### 3. Simulación e implementación

Deben describir el funcionamiento del simulador de manera que un tercero pueda entender cómo evoluciona el sistema. Esto incluye la lógica general de la simulación, la forma en que se actualiza el estado, el manejo del tiempo y la definición de los outputs de cada réplica. Para al menos una variable aleatoria relevante deben explicar cómo se genera, ya sea mediante transformada inversa, otro método de simulación o una función de librería bien identificada. No es necesario desarrollar un generador pseudoaleatorio desde cero, pero sí mostrar comprensión del mecanismo utilizado.

### 4. Verificación, validación y diseño experimental

Deben incluir evidencia de que el código implementa correctamente el modelo, por ejemplo mediante casos pequeños, entradas determinísticas, chequeos de consistencia o comparaciones con resultados simples conocidos. Además, deben discutir en qué sentido el modelo representa razonablemente el sistema real, indicando qué aspectos pudieron validar y cuáles no. El análisis experimental debe considerar al menos un escenario base y dos escenarios alternativos relevantes, con réplicas independientes, manejo explícito de semillas y estimación de incertidumbre. En principio, se esperan al menos 30 réplicas por escenario, salvo justificación clara en otro sentido.

### 5. Resultados, sensibilidad y conclusión

Deben presentar los principales resultados del estudio de simulación, incluyendo al menos una medida de desempeño con estimación puntual, variabilidad e intervalo de confianza. También deben comparar los escenarios mediante tablas o gráficos e interpretar los resultados en el contexto del problema. Finalmente, deben realizar un análisis de sensibilidad sobre parámetros importantes o inciertos, discutir las principales limitaciones del trabajo y cerrar con una recomendación o conclusión que responda explícitamente la pregunta inicial.

---

## Ejemplos orientadores

A modo de referencia, pueden considerar problemas de sistemas de espera, confiabilidad, mantenimiento, demanda, capacidad o gestión de operaciones, entre muchos otros. Por ejemplo, podrían estudiar cuántos servidores se requieren en una cafetería para cumplir cierto nivel de servicio, comparar políticas de mantenimiento para un equipo que falla aleatoriamente, o analizar cómo cambia el desempeño de un sistema digital al modificar su capacidad de procesamiento. También pueden trabajar en ámbitos como deportes, videojuegos, tráfico, música, redes sociales o procesos naturales. Estos ejemplos son solo orientadores: no constituyen una lista cerrada ni un molde obligatorio. La originalidad se valorará, pero no reemplaza la relevancia del problema ni el rigor del modelamiento, la simulación y el análisis.

---

## Evaluación

La tarea se evaluará sobre 100 puntos según la siguiente rúbrica:

| Criterio | Pts. |
|---|:---:|
| Relevancia del problema y claridad de la pregunta planteada | 15 |
| Formulación del modelo estocástico y justificación de supuestos | 20 |
| Implementación y calidad de la simulación | 25 |
| Diseño experimental, réplicas y manejo de la incertidumbre | 15 |
| Análisis de resultados, comparación de escenarios y recomendación final | 15 |
| Presentación, redacción y reproducibilidad de la entrega | 10 |
| **Total** | **100** |

> Se espera que el problema tenga una dificultad acorde al curso. **Proyectos demasiado simples o demasiado directos podrán ser penalizados con nota máxima 5.5**, por ejemplo cuando la solución no requiera realmente de un proceso de simulación por ejemplo un M/M/1. Trabajos sin simulación funcional, sin réplicas independientes o sin análisis de incertidumbre no podrán optar al puntaje completo.

---

## Datos y fuentes

No se entregará una base de datos única. Parte de la tarea consiste en encontrar, seleccionar y justificar una fuente adecuada de información. Pueden utilizar datos públicos, estadísticas oficiales, repositorios académicos, registros levantados por el propio grupo o, si corresponde, datos sintéticos debidamente justificados. Un posible punto de partida es https://datos.gob.cl. Toda fuente utilizada debe citarse correctamente. Si la base de datos no puede adjuntarse por su tamaño, deberán incluir un enlace estable y explicar brevemente cómo acceder a ella.

---

## Entrega y aspectos formales

La tarea se realiza en grupos de hasta cuatro personas y tiene un plazo de diez días. Deben entregar un informe de máximo diez páginas, sin contar anexos, junto con el código y los archivos de apoyo necesarios para reproducir los resultados. El material entregado debe ser autocontenido y permitir que un tercero pueda ejecutar el trabajo y obtener los principales resultados. Se debe utilizar Python y se recomienda entregar un archivo `.ipynb`.

La entrega debe consistir en una carpeta comprimida que incluya, al menos, el informe, el código, un archivo `README.md` con instrucciones de ejecución y, cuando corresponda, los datos utilizados. La carpeta `src/` es opcional si todo el código está contenido en el notebook.

El archivo `README.md` debe indicar, de manera breve, la versión de Python utilizada, las librerías necesarias, el origen de los datos y los pasos básicos para reproducir los resultados.

Además, deben adjuntar todo lo necesario para corregir el trabajo. El código debe ejecutarse de principio a fin, las tablas y figuras deben estar correctamente rotuladas, las ecuaciones relevantes deben estar definidas e interpretadas, y los resultados deben ser reproducibles.

Finalmente, si utilizan herramientas de inteligencia artificial, deben reconocerlo explícitamente en la entrega e indicar en qué parte del trabajo fueron usadas y qué rol cumplieron. El uso de estas herramientas no reemplaza la responsabilidad del grupo sobre la corrección, comprensión y trazabilidad de lo entregado.

---
---

## Consideraciones de Opus 4.8 Alto

**Núcleo del trabajo:** recorrer el arco completo **Problema real → Modelo estocástico → Simulación → Análisis → Decisión**. La simulación debe ser la parte central, no un adorno para reproducir una fórmula conocida.

**Restricciones clave a tener presente:**
- Problema real de **libre elección** (logística, salud, finanzas, deportes, etc.).
- Debe formularse **una pregunta concreta** que la simulación responda.
- Herramientas del curso disponibles: procesos de Poisson, cadenas de Markov, colas, simulación de eventos discretos, etc.
- **Obligatorio:** comparar 1 escenario base + al menos 2 escenarios alternativos.
- **≥30 réplicas independientes** por escenario, con manejo explícito de semillas.
- Reportar medida de desempeño con **estimación puntual, variabilidad e intervalo de confianza**.
- Incluir **análisis de sensibilidad** sobre parámetros inciertos.
- **Python obligatorio** (recomendado `.ipynb`).

**Trampa importante:** proyectos demasiado simples (ej. un M/M/1 directo que se resuelve analíticamente) tienen **nota máxima 5.5**. La simulación debe ser realmente necesaria.

**Rúbrica (100 pts):**
- Relevancia del problema y claridad de la pregunta: 15
- Formulación del modelo y justificación de supuestos: 20
- Implementación y calidad de la simulación: 25
- Diseño experimental, réplicas e incertidumbre: 15
- Análisis, comparación de escenarios y recomendación: 15
- Presentación, redacción y reproducibilidad: 10

**Entregables (carpeta comprimida):**
- Informe (máx. 10 páginas sin anexos).
- Código (`.ipynb`) que corra de principio a fin.
- `README.md` (versión de Python, librerías, origen de datos, pasos de reproducción).
- Datos usados (o enlace estable si son muy grandes).
- Sección final de **"Referencias y uso de recursos"** declarando uso de IA y fuentes (todo dato debe ser público, verificable y citado; punto de partida sugerido: datos.gob.cl).

**Consideraciones formales adicionales:**
- Grupos de **hasta 4 integrantes** (según el PDF; según Canvas, ideal 4, excepcionalmente 3 o 5 con autorización por correo a Felipe Rodríguez).
- Plazo de 10 días, entrega **07 de julio, 23:59**.
- La entrega **cuenta para todo el grupo** y **no se acepta** solo el informe sin archivos de respaldo.
