# UC-2026-1 · MMEE · Tarea 3 — Despacho de Recursos de Emergencia

Simulación de eventos discretos (**cola de pérdida**, sin espera) del despacho de unidades de
emergencia en la Región Metropolitana, a partir de datos reales del SIGEB (2025). Estima la
**probabilidad de bloqueo** (emergencias que no alcanzan a ser atendidas por falta de unidades)
y compara escenarios de dotación y de organización (una flota agregada vs. flotas por comuna,
con y sin refuerzo entre zonas).

## 🔗 Simulador interactivo en vivo

**https://joalonsosch.github.io/UC-2026-1_MMEE-T3/**

Corre en el navegador, sin instalar nada. (Ver la [guía de uso](#el-simulador-interactivo-indexhtml) más abajo.)

---

## Estructura del repositorio

```
UC-2026-1_MMEE-T3/
├── README.md                         ← este archivo
├── .github/workflows/pages.yml       ← despliega tarea-3/ a GitHub Pages en cada push a main
├── .gitignore
└── tarea-3/
    ├── index.html                    ← simulador web (JavaScript, autocontenido) · lo publica Pages
    ├── central_telefonica/           ← carpeta reservada (placeholder) para el otro camino del grupo
    │   └── .gitkeep
    ├── base/                         ← INSUMOS (no se modifican)
    │   ├── Enunciado_Original.pdf        enunciado oficial de la tarea
    │   ├── Enunciado_Transcrito.md       transcripción en texto del enunciado
    │   ├── Llamadas_Emergencia.pdf       material de apoyo sobre las llamadas
    │   └── SIGEB_Estadisticas.xlsx       datos crudos: 10.082 emergencias RM 2025
    └── despacho_recursos/            ← PROYECTO (Camino A)
        ├── despacho_recursos.ipynb      notebook principal; corre de principio a fin
        ├── requirements.txt             dependencias de Python
        ├── src/
        │   └── motor.py                 motor de simulación (idéntico a las celdas del notebook)
        ├── data/                        datos generados por el notebook
        │   ├── datos_procesados.csv         dataset limpio (10.079 filas) + columnas hora/n_unidades/zona
        │   └── parametros.npz               parámetros empíricos del modelo (tasas, distribuciones)
        ├── resultados/                  resultados numéricos generados
        │   ├── resultados_escenarios.csv    3 escenarios × 2 resoluciones, con media, sd e IC 95 %
        │   ├── sensibilidad_servicio.csv    barrido del tiempo de servicio (30/45/60 min)
        │   ├── sensibilidad_flota.csv       barrido de la flota (1→15)
        │   └── sensibilidad_demanda.csv     barrido de la demanda (×1,0 / ×1,2 / ×1,5)
        ├── figuras/                     6 figuras PNG a 150 dpi generadas por el notebook
        │   ├── val_perfil_horario.png       validación: perfil horario simulado vs real
        │   ├── fig_escenarios.png           comparación de escenarios (IC 95 %)
        │   ├── fig_bloqueo_comuna.png        bloqueo por comuna (escenario base)
        │   ├── fig_agregado_vs_zonal.png     agregado vs por comuna (escala log)
        │   ├── fig_sens_flota.png            curva de sensibilidad de flota
        │   └── fig_sens_servicio.png         curva de sensibilidad de servicio
        └── web/
            └── web_params.json          parámetros del modelo exportados para el simulador web
```

Los contenidos de `data/`, `resultados/`, `figuras/` y `web/` **se regeneran** al ejecutar el
notebook; no hace falta editarlos a mano.

---

## Cómo clonar y preparar el entorno local

Necesitas **git** y **Python 3.11+** (el proyecto se desarrolló y verificó con **3.14.0**).

```bash
# 1. Clonar el repositorio
git clone https://github.com/joalonsosch/UC-2026-1_MMEE-T3.git
cd UC-2026-1_MMEE-T3/tarea-3/despacho_recursos

# 2. Crear y activar un entorno virtual
python -m venv .venv
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Windows (cmd):        .venv\Scripts\activate.bat
# macOS / Linux:        source .venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt        # numpy, pandas, openpyxl, matplotlib
pip install ipykernel nbconvert        # para ejecutar el notebook
```

> El entorno virtual (`.venv/`) está en `.gitignore`, así que cada persona lo crea en su máquina.

---

## Cómo reproducir los resultados

Con el entorno activado:

- **Opción A (Jupyter/VS Code):** abrir `despacho_recursos.ipynb` y ejecutar
  **Kernel → Restart & Run All**.
- **Opción B (línea de comandos)**, desde `tarea-3/despacho_recursos/`:

  ```bash
  .venv\Scripts\python -m nbconvert --to notebook --execute --inplace \
    despacho_recursos.ipynb --ExecutePreprocessor.kernel_name=python3
  ```

El notebook lee el `.xlsx` de `base/` (lo localiza solo, con `pathlib`) y regenera todo lo de
`data/`, `resultados/`, `figuras/` y `web/`. Toda la aleatoriedad usa
`numpy.random.default_rng(42 + i)` con semillas explícitas, por lo que **dos ejecuciones
completas producen resultados idénticos**.

---

## El simulador interactivo (`index.html`)

Es una página **autocontenida** (todo el código y los parámetros van embebidos): funciona tanto
en la [URL pública de Pages](https://joalonsosch.github.io/UC-2026-1_MMEE-T3/) como abriendo el
archivo `tarea-3/index.html` directamente en el navegador (doble clic). No necesita servidor ni
conexión.

**Cómo usarlo:**

1. **Elige el modo** (arriba):
   - **Agregado** — una sola flota atiende toda la RM (recursos compartidos).
   - **Por comuna** — cada comuna tiene su propia flota (repartida según su volumen de emergencias).
2. **Mueve los deslizadores:**
   - **Flota** — número de unidades (en modo por comuna, es el total, que se reparte por volumen).
   - **Tiempo de servicio** — media (min) de la ocupación de cada unidad.
   - **Escala de demanda** — multiplica la tasa de llegadas (×0,5 a ×2).
3. **Refuerzo** (solo modo por comuna) — si se activa, una comuna sin unidades puede pedir prestado
   a la comuna con más unidades libres.
4. **Lee los resultados:** la probabilidad de bloqueo (con su IC 95 %), emergencias atendidas y
   bloqueadas, y utilización / % de atenciones con refuerzo. El gráfico muestra la curva de bloqueo
   vs. flota (modo agregado) o el bloqueo por comuna (modo por comuna), con la línea del umbral 5 %.

Cada cambio corre **30 réplicas** de la simulación en el navegador, con semillas fijas.

### Relación con el notebook (flujo de datos)

El flujo es **en una sola dirección: el notebook alimenta a la página, no al revés.**

```
despacho_recursos.ipynb  ──(exporta)──►  web/web_params.json  ──(se embebe en)──►  index.html
```

- El notebook calcula los parámetros empíricos (tasas horarias, distribución de unidades, etc.) y
  los **exporta** a `web/web_params.json`.
- `index.html` **reimplementa el mismo modelo en JavaScript** y trae esos parámetros embebidos, de
  modo que la web usa exactamente las mismas cifras que el notebook.
- La página **no escribe nada** de vuelta: solo lee parámetros y simula en el navegador. No modifica
  el notebook ni ningún archivo del repo.

> Es decir: si cambian el modelo en el notebook, se regenera `web_params.json` y la página se
> actualiza a partir de él. La página nunca alimenta al `.ipynb`.

---

## Parámetros del modelo (fijados)

| Parámetro | Valor |
|---|---|
| Llegadas | Poisson no homogéneo por hora del día (thinning) |
| Unidades por emergencia | distribución empírica (bootstrap), media ≈ 2,15 |
| Tiempo de ocupación por unidad | Exponencial, media 45 min (se sensibiliza 30/45/60) |
| Motor | cola de eventos manual con `heapq` |
| Réplicas por escenario | 30 (semilla base 42) |
| Warm-up / horizonte | 3 días / 60 días simulados |
| Nivel de confianza | 95 % (IC = media ± 1,96·s/√n) |
| Dotación base | `FLOTA_BASE = 7` |
| Umbral de servicio | 5 % de bloqueo |
