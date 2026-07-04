# PLAN MAESTRO DE CONSTRUCCIÓN — Tarea 3 · Despacho de Recursos (Camino A)

**Destinatario:** Claude Code (constructor).
**Autoría del diseño:** el arquitecto (Claude en chat). **Cliente:** el usuario (dueño del repo).

---

## REGLAS DE OPERACIÓN PARA CLAUDE CODE (LEER PRIMERO)

1. **No tomes decisiones de diseño.** Todos los parámetros, distribuciones, rutas y criterios
   ya están fijados en este documento. Si algo parece faltar o ambiguo, **detente y pregúntale
   al cliente**; no improvises ni "elijas lo razonable".
2. **No cambies los valores fijados** (tiempo de servicio, semillas, número de réplicas, rutas,
   nombres de archivo). Están puestos a propósito.
3. **Este plan cubre solo lo NO analítico.** No redactes interpretaciones, conclusiones ni
   recomendaciones. Genera código, estructura, tablas y figuras. El análisis lo hará el grupo aparte.
4. **Trabaja rama por rama con commits pequeños** y mensajes claros. No hagas push forzado.
5. **Marca cada subpaso como hecho solo si cumple su "Criterio de hecho"** (checklist al final de cada paso).
6. Ámbito de trabajo: **exclusivamente** dentro de `tarea-3/despacho_recursos/` y `tarea-3/base/`
   y `tarea-3/index.html`. **No toques** `tarea-3/central_telefonica/`.

---

## PARÁMETROS GLOBALES FIJADOS (usar exactamente estos)

| Parámetro | Valor | Nota |
|---|---|---|
| Dataset fuente | `tarea-3/base/SIGEB_Estadisticas.xlsx` | 10.082 filas, hoja `Sheet1` |
| Columnas | Correlativo, Fecha, Clave, Calle, Esquina, Comuna, Material | — |
| Proceso de llegadas | Poisson **no homogéneo** por hora del día | thinning |
| Distribución unidades/emergencia | **empírica** (bootstrap del Excel) | media ≈ 2,15 |
| Tiempo de ocupación por unidad | **Exponencial, media = 45 min** | se sensibiliza 30/45/60 |
| Motor | **cola de eventos manual con `heapq`** | NO SimPy |
| RNG | `numpy.random.default_rng(seed)` | semillas explícitas |
| Réplicas por escenario | **30** | fijo |
| Semilla base | **42** | réplica i usa `default_rng(42 + i)` |
| Warm-up | primeros **3 días** de cada réplica se descartan | — |
| Horizonte por réplica | **60 días** simulados (tras warm-up) | — |
| Nivel de confianza | **95%** (t o z según n) | IC = media ± 1.96·s/√n |
| Comunas desagregadas | Santiago, Las Condes, Providencia, Estación Central, Renca, Independencia, Vitacura, Lo Barnechea, Recoleta | resto → "Resto RM" |
| Umbral objetivo de bloqueo | **5%** | criterio de "servicio aceptable" |
| Python | 3.11+ | — |
| Librerías | numpy, pandas, openpyxl, matplotlib | nada más |

---

## 1. PREPARACIÓN DEL ENTORNO Y DATOS

### 1.1. Verificar estructura de carpetas
- Confirmar que existen `tarea-3/base/`, `tarea-3/despacho_recursos/`.
- Si `tarea-3/base/SIGEB_Estadisticas.xlsx` no existe, **detenerse y avisar al cliente**.

### 1.2. Crear el archivo de dependencias
- Crear `tarea-3/despacho_recursos/requirements.txt` con: `numpy`, `pandas`, `openpyxl`, `matplotlib` (una por línea, sin versiones pinneadas salvo que el cliente lo pida).

### 1.3. Crear el notebook base
- Crear `tarea-3/despacho_recursos/despacho_recursos.ipynb`.
- Primera celda markdown: título + índice de secciones (Datos, Modelo, Motor, Verificación, Experimentos, Sensibilidad, Export).
- Segunda celda: imports (`numpy`, `pandas`, `heapq`, `matplotlib.pyplot`, `pathlib`).

**Criterio de hecho 1:** el notebook abre, corre las celdas de import sin error, y `requirements.txt` existe.

---

## 2. CARGA Y LIMPIEZA DE DATOS (Fase Datos)

### 2.1. Cargar el xlsx
- `pd.read_excel(ruta, sheet_name='Sheet1')`. Ruta relativa robusta con `pathlib` (que funcione desde el notebook).
- Parsear `Fecha` a datetime.

### 2.2. Limpiar
- Eliminar/filtrar filas con `Comuna` nula (son 3) y `Material` nulo (1) — dejar registrado cuántas se quitan en un `print`.
- Normalizar `Comuna` a string sin espacios extra.

### 2.3. Derivar columnas de apoyo
- `hora` = hora del día (0–23) desde `Fecha`.
- `n_unidades` = número de unidades en `Material` (contar elementos separados por coma).
- `zona` = `Comuna` si está en la lista de 9 desagregadas, si no `"Resto RM"`.

### 2.4. Guardar dataset procesado
- Exportar a `tarea-3/despacho_recursos/datos_procesados.csv` (UTF-8).

**Criterio de hecho 2:** `datos_procesados.csv` existe, tiene ~10.078 filas, y las columnas `hora`, `n_unidades`, `zona` están pobladas.

---

## 3. PARÁMETROS EMPÍRICOS PARA EL MODELO

### 3.1. Tasa horaria de llegada
- Calcular, por hora del día (0–23), el promedio de emergencias por día = (conteo en esa hora) / 365.
- Guardar como array `tasa_horaria` de largo 24 (unidad: emergencias/hora, es decir el valor/día ya es la tasa media de esa hora).
- Repetir el cálculo **por zona** (matriz 10 zonas × 24 horas) para el modo desagregado.

### 3.2. Distribución empírica de unidades por emergencia
- Guardar el vector `n_unidades` completo para muestrear por bootstrap.
- Guardar también la versión por zona.

### 3.3. Exportar parámetros
- Guardar los arrays en `tarea-3/despacho_recursos/parametros.npz` (numpy) para que el motor los cargue sin recomputar.

**Criterio de hecho 3:** `parametros.npz` existe y contiene `tasa_horaria`, `tasa_horaria_zona`, `unidades_muestra`, `unidades_muestra_zona`.

---

## 4. MOTOR DE SIMULACIÓN (núcleo — heapq)

> Implementar como funciones puras y testeables, no como script suelto. Todo en celdas del notebook,
> pero también copiado a `tarea-3/despacho_recursos/src/motor.py` para reutilización e importación.

### 4.1. Generador de llegadas no homogéneo (thinning)
- Función `generar_llegadas(tasa_horaria, dias, rng) -> lista de tiempos (min)`.
- Método: thinning con `lambda_max = max(tasa_horaria)/60` por minuto; aceptar con prob `tasa(hora)/lambda_max`.
- **Comentario en código** explicando el mecanismo de transformada inversa exponencial:
  `t += -ln(1-U)/lambda_max`. (Esto satisface el requisito del enunciado de explicar la generación de una VA.)

### 4.2. Muestreo de unidades por emergencia
- Función `muestrear_unidades(muestra, rng) -> int` por bootstrap (elige un valor al azar del vector empírico).

### 4.3. Muestreo del tiempo de ocupación
- Función `muestrear_servicio(media, rng) -> float` con `rng.exponential(media)`. Media por defecto = 45.

### 4.4. Motor de una réplica (modo AGREGADO)
- Función `simular_replica_agregado(flota, tasa_horaria, unidades_muestra, media_serv, dias, warmup, rng) -> dict`.
- Lógica con `heapq` (calendario de eventos):
  - Evento tipo "llegada" y evento tipo "liberación".
  - Estado: `ocupadas` (int), `flota` (int).
  - Al llegar emergencia (después de warm-up): muestrear `need` unidades.
    - Si `ocupadas + need <= flota`: ocupar, agendar liberaciones (una por unidad), contar `atendida`.
    - Si no: contar `bloqueada` (no se atiende / no espera — bloqueo puro).
  - Métrica de salida: `p_bloqueo = bloqueadas / (atendidas + bloqueadas)` en %, además de utilización media.
- Las llegadas del periodo warm-up **se procesan** (para calentar el sistema) pero **no se cuentan** en las métricas.

### 4.5. Motor de una réplica (modo POR COMUNA)
- Función `simular_replica_zonas(flota_por_zona: dict, tasa_horaria_zona, unidades_muestra_zona, media_serv, dias, warmup, rng, refuerzo: bool) -> dict`.
- Cada zona tiene su propia flota y su propio contador de ocupadas.
- Al llegar emergencia a zona Z:
  - Si la zona Z tiene unidades suficientes → atender localmente.
  - Si no y `refuerzo=True` → intentar tomar de la zona con más unidades libres (registrar como "atendida con refuerzo").
  - Si no hay en ninguna → bloqueada.
- Métricas: `p_bloqueo` global y por zona, `%` de atenciones con refuerzo.

**Criterio de hecho 4:** ambas funciones corren una réplica sin error y devuelven un dict con `p_bloqueo` numérico en [0,100].

---

## 5. VERIFICACIÓN Y VALIDACIÓN (construcción de la evidencia)

### 5.1. Test determinístico
- Con `flota` muy grande (ej. 200) y demanda normal → `p_bloqueo` debe ser 0. Assert.

### 5.2. Test de saturación
- Con `flota` muy chica (ej. 2) → `p_bloqueo` alto (>30%). Assert de monotonía: más flota ⇒ menos bloqueo (probar 3 niveles).

### 5.3. Test de conservación
- En ningún instante `ocupadas > flota`. Añadir chequeo interno (assert dentro del motor en modo debug).

### 5.4. Validación de volumen
- Simular 365 días sin warm-up y comparar el nº de llegadas generadas con **10.082** (real). Debe caer en ±3%. Imprimir ambos números.

### 5.5. Validación de perfil horario
- Graficar perfil horario simulado vs real (barras). Guardar figura en `tarea-3/despacho_recursos/figuras/val_perfil_horario.png`.

**Criterio de hecho 5:** los 3 asserts pasan, el volumen cae en ±3%, y la figura de validación existe.

---

## 6. DISEÑO EXPERIMENTAL — 3 ESCENARIOS × 2 RESOLUCIONES

> Semilla réplica i = `default_rng(42 + i)`, i = 0..29. Mismos streams entre escenarios para comparabilidad.

### 6.1. Fijar dotación base
- Definir `FLOTA_BASE_AGREGADO` como un valor que deje el sistema en régimen realista (arrancar en el nº que dé p_bloqueo cercano pero por encima del umbral 5% en base; si no se conoce, correr un barrido rápido 8→40 y elegir el que quede ~5–8%). **Documentar el valor elegido en una celda markdown.**
- Definir `FLOTA_BASE_POR_ZONA` como dict, repartiendo la flota base proporcional al volumen de cada zona (redondear).

### 6.2. Escenario Base
- Correr 30 réplicas en modo agregado y 30 en modo por-zona con la dotación base.

### 6.3. Escenario Alt-1 (Recorte −20%)
- Reducir cada flota en 20% (redondeo). Correr 30+30 réplicas.

### 6.4. Escenario Alt-2 (Redistribución)
- Misma flota total que base, pero movida de zonas ociosas a saturadas (regla: asignar proporcional al *bloqueo* observado en base, no al volumen). Correr 30+30 réplicas. Activar `refuerzo=True`.

### 6.5. Recolectar resultados
- Para cada escenario×resolución: media, desviación estándar, IC 95% de `p_bloqueo`.
- Consolidar en un DataFrame y exportar `tarea-3/despacho_recursos/resultados_escenarios.csv`.

**Criterio de hecho 6:** `resultados_escenarios.csv` tiene 6 filas (3 escenarios × 2 resoluciones) con columnas media, sd, ic_low, ic_high.

---

## 7. ANÁLISIS DE SENSIBILIDAD (solo generación de datos, no interpretación)

### 7.1. Barrido de tiempo de servicio
- Repetir el escenario Base (agregado) con media de servicio 30, 45, 60 min. 30 réplicas cada uno.
- Exportar `tarea-3/despacho_recursos/sensibilidad_servicio.csv`.

### 7.2. Barrido de flota
- En modo agregado, barrer flota desde `FLOTA_BASE−8` hasta `FLOTA_BASE+8`, 20 réplicas cada punto, media de p_bloqueo.
- Exportar `tarea-3/despacho_recursos/sensibilidad_flota.csv`.

### 7.3. (Opcional) Barrido de demanda
- Escalar la tasa ×1.0, ×1.2, ×1.5. Exportar `sensibilidad_demanda.csv`.

**Criterio de hecho 7:** los CSV de sensibilidad existen y están poblados.

---

## 8. FIGURAS Y TABLAS (rotuladas, para el informe)

> Todas las figuras en `tarea-3/despacho_recursos/figuras/`, PNG a 150 dpi, con título, ejes rotulados y leyenda.

### 8.1. Figura: comparación de escenarios (barras con barras de error = IC 95%).
### 8.2. Figura: bloqueo por comuna en escenario base (barras).
### 8.3. Figura: agregado vs por-comuna (mostrar que el agregado subestima).
### 8.4. Figura: curva de sensibilidad de flota (línea).
### 8.5. Figura: curva de sensibilidad de servicio (línea).
### 8.6. Tabla resumen: exportar `resultados_escenarios.csv` también como tabla markdown en el notebook.

**Criterio de hecho 8:** las 5 figuras PNG existen y son legibles; la tabla markdown se renderiza en el notebook.

---

## 9. REPRODUCIBILIDAD DEL NOTEBOOK

### 9.1. Ejecutar de principio a fin
- "Restart & Run All". Debe correr sin errores desde cero.

### 9.2. Sembrar todo
- Verificar que no hay aleatoriedad sin semilla: dos ejecuciones completas dan resultados idénticos.

### 9.3. README técnico del camino
- Crear `tarea-3/despacho_recursos/README.md` con: versión de Python, librerías (apuntar a requirements.txt), origen de datos (xlsx en base/), y pasos para reproducir ("Restart & Run All").

**Criterio de hecho 9:** Restart & Run All limpio; dos corridas idénticas; README existe.

---

## 10. PÁGINA DE SIMULACIÓN INTERACTIVA (el extra)

> Base de partida: ya existe un `index.html` funcional (motor JS que replica el modelo A).
> Este paso lo **adapta a los números finales** del notebook y lo publica.

### 10.1. Colocar la página
- Colocar/actualizar `tarea-3/index.html` con la versión del simulador de Despacho de Recursos.
- **Eliminar del landing la opción de Central Telefónica** (el grupo trabaja solo Camino A): dejar la página entrando directo al simulador de recursos, o el landing con una sola tarjeta.

### 10.2. Sincronizar parámetros con el notebook
- Ajustar en el JS: `tasa_horaria` (los 24 valores reales), distribución de unidades, media de servicio 45, umbral 5%, y `FLOTA_BASE` = el valor elegido en 6.1. Los números de la web deben coincidir con los del notebook.

### 10.3. Verificar responsive y que corre
- Abrir localmente; confirmar que corre la simulación en el navegador y el gráfico se dibuja. Revisar en viewport móvil (≤400px).

### 10.4. Publicar
- Commit + push a `main`. El workflow de Pages ya está configurado para publicar `tarea-3/`.
- Confirmar en la pestaña Actions que el deploy queda verde y que la URL de Pages muestra la página nueva.

**Criterio de hecho 10:** la URL de GitHub Pages muestra el simulador de recursos funcionando, sin rastro de Central Telefónica.

---

## 11. ENTREGA DEL BLOQUE CONSTRUIDO

### 11.1. Commit final del notebook y artefactos
- Asegurar que están versionados: `despacho_recursos.ipynb`, `src/motor.py`, `requirements.txt`,
  `datos_procesados.csv`, `parametros.npz`, los CSV de resultados/sensibilidad, la carpeta `figuras/`, el `README.md`.

### 11.2. Resumen de salida para el cliente
- Generar un `tarea-3/despacho_recursos/RESUMEN_CONSTRUCCION.md` que liste: qué archivos se crearon,
  el valor de `FLOTA_BASE` elegido, y los números clave (p_bloqueo por escenario con su IC).
  **Solo datos, sin interpretación.**

**Criterio de hecho 11:** todo versionado y pusheado; `RESUMEN_CONSTRUCCION.md` existe.

---

## MAPA A LA RÚBRICA (referencia para el cliente, no acción de Claude Code)

| Pasos del plan | Rúbrica cubierta | Pts |
|---|---|---|
| 4 (formalización en código) + celdas markdown del modelo | Formulación del modelo y supuestos | 20 |
| 2, 3, 4, 8, 9 | Implementación y calidad de la simulación | 25 |
| 5, 6, 7 | Diseño experimental, réplicas, incertidumbre | 15 |
| 9, 10, 11 | (contribuye a) Presentación y reproducibilidad | 10 |

Lo NO cubierto aquí a propósito (lo hará el grupo, es analítico): relevancia/pregunta (15) y
análisis/comparación/recomendación (15).

---

**FIN DEL PLAN. Claude Code: ejecuta en orden, respeta los "Criterio de hecho", y ante cualquier
ambigüedad, detente y pregunta al cliente.**