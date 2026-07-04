# UC-2026-1 · MMEE · Tarea 3 — Despacho de Recursos de Emergencia

Simulación de eventos discretos (cola de pérdida, sin espera) del despacho de unidades de
emergencia en la Región Metropolitana, a partir de datos reales del SIGEB. Estima la
**probabilidad de bloqueo** (emergencias no atendidas por falta de unidades) y compara escenarios
de dotación y de organización (agregado vs. por comuna, con y sin refuerzo entre zonas).

**Simulador interactivo en vivo:** https://joalonsosch.github.io/UC-2026-1_MMEE-T3/

## Estructura del repositorio

```
UC-2026-1_MMEE-T3/
├── README.md                     ← este archivo
└── tarea-3/
    ├── index.html                ← simulador web (JavaScript; publicado en GitHub Pages)
    ├── base/                     ← insumos
    │   ├── Enunciado_Original.pdf / Enunciado_Transcrito.md
    │   ├── Llamadas_Emergencia.pdf
    │   └── SIGEB_Estadisticas.xlsx      (datos crudos, 10.082 emergencias 2025)
    └── despacho_recursos/
        ├── despacho_recursos.ipynb      ← notebook principal (corre de principio a fin)
        ├── requirements.txt
        ├── src/motor.py                 ← motor de simulación (idéntico a las celdas del notebook)
        ├── data/                        ← generados: datos_procesados.csv, parametros.npz
        ├── resultados/                  ← generados: resultados_escenarios.csv, sensibilidad_*.csv
        ├── figuras/                     ← generados: 6 PNG a 150 dpi
        ├── web/web_params.json          ← parámetros embebidos en index.html
        └── docs/                        ← Plan_Accion.md, RESUMEN_CONSTRUCCION.md (proceso)
```

Los contenidos de `data/`, `resultados/`, `figuras/` y `web/` se **regeneran** al ejecutar el notebook.

## Requisitos

- **Python 3.11+** (desarrollado y verificado con **3.14.0**).
- Librerías: ver [`tarea-3/despacho_recursos/requirements.txt`](tarea-3/despacho_recursos/requirements.txt) —
  `numpy`, `pandas`, `openpyxl`, `matplotlib`. Para *ejecutar* el notebook se usa además
  `ipykernel` + `nbconvert` (o Jupyter).

```bash
cd tarea-3/despacho_recursos
python -m venv .venv
# Windows:
.venv\Scripts\activate
pip install -r requirements.txt ipykernel nbconvert
```

## Origen de los datos

- **`tarea-3/base/SIGEB_Estadisticas.xlsx`** (hoja `Sheet1`): 10.082 registros de emergencias
  atendidas en la RM durante 2025 (columnas: Correlativo, Fecha, Clave, Calle, Esquina, Comuna,
  Material). El notebook lo localiza con una búsqueda robusta (`pathlib`), por lo que corre tanto
  desde `tarea-3/despacho_recursos/` como desde la raíz del repositorio.

## Cómo reproducir

1. Activar el entorno con las librerías instaladas (ver arriba).
2. Abrir `tarea-3/despacho_recursos/despacho_recursos.ipynb` y ejecutar **Kernel → Restart & Run All**.

O sin abrir Jupyter, desde `tarea-3/despacho_recursos/`:

```bash
.venv\Scripts\python -m nbconvert --to notebook --execute --inplace \
  despacho_recursos.ipynb --ExecutePreprocessor.kernel_name=python3
```

Toda la aleatoriedad usa `numpy.random.default_rng` con semillas explícitas
(réplica *i* → `default_rng(42 + i)`), por lo que **dos ejecuciones completas producen resultados
idénticos** (verificado por hash de los archivos de salida).

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

Un resumen de los números clave (bloqueo por escenario con su IC) está en
[`tarea-3/despacho_recursos/docs/RESUMEN_CONSTRUCCION.md`](tarea-3/despacho_recursos/docs/RESUMEN_CONSTRUCCION.md).
