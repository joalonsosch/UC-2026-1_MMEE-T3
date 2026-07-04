# Despacho de Recursos de Emergencia — Simulación (Camino A)

Simulación de eventos discretos (cola de pérdida, sin espera) del despacho de unidades de
emergencia en la Región Metropolitana, a partir de datos reales del SIGEB. Estima la
**probabilidad de bloqueo** (emergencias no atendidas por falta de unidades) y compara
escenarios de dotación y de organización (agregado vs. por comuna, con y sin refuerzo).

## Requisitos

- **Python 3.11+** (desarrollado y verificado con **3.14.0**).
- Librerías: ver [`requirements.txt`](requirements.txt) — `numpy`, `pandas`, `openpyxl`, `matplotlib`.
  Para *ejecutar* el notebook se usa además `ipykernel` + `nbconvert` (o Jupyter).

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
pip install -r requirements.txt ipykernel nbconvert
```

## Origen de los datos

- Fuente: **`../base/SIGEB_Estadisticas.xlsx`** (hoja `Sheet1`), 10.082 registros de emergencias
  atendidas en la RM durante 2025 (columnas: Correlativo, Fecha, Clave, Calle, Esquina, Comuna,
  Material). El enunciado transcrito está en `../base/Enunciado_Transcrito.md`.
- El notebook carga ese archivo mediante una búsqueda robusta con `pathlib`, de modo que corre
  tanto desde `tarea-3/despacho_recursos/` como desde la raíz del repositorio.

## Cómo reproducir

1. Activar el entorno con las librerías instaladas (ver arriba).
2. Abrir `despacho_recursos.ipynb` y ejecutar **Kernel → Restart & Run All**.

O bien, sin abrir Jupyter, desde `tarea-3/despacho_recursos/`:

```bash
.venv\Scripts\python -m nbconvert --to notebook --execute --inplace \
  despacho_recursos.ipynb --ExecutePreprocessor.kernel_name=python3
```

Toda la aleatoriedad usa `numpy.random.default_rng` con semillas explícitas
(réplica *i* → `default_rng(42 + i)`), por lo que **dos ejecuciones completas producen resultados
idénticos** (verificado por hash de los CSV de salida).

## Estructura

```
despacho_recursos/
├── despacho_recursos.ipynb   # Notebook principal (Datos → Modelo → Motor → Verif. → Exp. → Sens. → Figs)
├── src/motor.py              # Motor de simulación (copia idéntica a las celdas del notebook)
├── requirements.txt
├── datos_procesados.csv      # Dataset limpio (generado)
├── parametros.npz            # Parámetros empíricos del modelo (generado)
├── resultados_escenarios.csv # 3 escenarios × 2 resoluciones, con IC 95% (generado)
├── sensibilidad_*.csv        # Barridos de servicio, flota y demanda (generado)
└── figuras/                  # Figuras PNG a 150 dpi (generado)
```

Los archivos marcados como *(generado)* se recrean al ejecutar el notebook.

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
