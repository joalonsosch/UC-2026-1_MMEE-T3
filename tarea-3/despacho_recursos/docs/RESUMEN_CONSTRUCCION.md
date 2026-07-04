# Resumen de construcción — Despacho de Recursos (Camino A)

> Documento de **datos**, sin interpretación. Lista los artefactos generados, el valor de
> `FLOTA_BASE` elegido y los números clave (probabilidad de bloqueo por escenario con su IC 95%).
> El análisis, la comparación y la recomendación los redacta el grupo aparte.

## Archivos creados

| Archivo | Contenido |
|---|---|
| `despacho_recursos.ipynb` | Notebook principal (Datos → Modelo → Motor → Verificación → Experimentos → Sensibilidad → Figuras → Export web). |
| `src/motor.py` | Motor de simulación (copia idéntica a las celdas del notebook): `generar_llegadas`, `muestrear_unidades`, `muestrear_servicio`, `simular_replica_agregado`, `simular_replica_zonas`. |
| `requirements.txt` | numpy, pandas, openpyxl, matplotlib. |
| `data/datos_procesados.csv` | Dataset limpio (10.079 filas; columnas de apoyo `hora`, `n_unidades`, `zona`). |
| `data/parametros.npz` | Parámetros empíricos: `tasa_horaria`, `tasa_horaria_zona`, `unidades_muestra`, `unidades_muestra_zona`, `zonas_orden`. |
| `resultados/resultados_escenarios.csv` | 3 escenarios × 2 resoluciones, con media, sd e IC 95%. |
| `resultados/sensibilidad_servicio.csv` | Barrido de media de servicio (30/45/60 min). |
| `resultados/sensibilidad_flota.csv` | Barrido de flota (1→15). |
| `resultados/sensibilidad_demanda.csv` | Barrido de escala de demanda (×1,0 / ×1,2 / ×1,5). |
| `figuras/` | 6 PNG a 150 dpi: `val_perfil_horario`, `fig_escenarios`, `fig_bloqueo_comuna`, `fig_agregado_vs_zonal`, `fig_sens_flota`, `fig_sens_servicio`. |
| `web/web_params.json` | Parámetros exportados para la página web. |
| `../../README.md` (raíz del repo) | Instrucciones de reproducción. |
| `../../index.html` | Simulador interactivo (JavaScript). Publicado en GitHub Pages. |

## Configuración fijada

- **`FLOTA_BASE` (agregado) = 7** unidades (menor dotación con bloqueo apenas > 5 %; barrido: flota 6 → 8,44 %, flota 7 → 5,14 %, flota 8 → 3,28 %).
- **`FLOTA_BASE_POR_ZONA`** (mismo total 7, proporcional al volumen): Santiago 3; Las Condes, Providencia, Estación Central, Renca 1 c/u; Independencia, Vitacura, Lo Barnechea, Recoleta, Resto RM 0.
- Media de servicio 45 min; 30 réplicas por escenario; semilla réplica *i* = `default_rng(42+i)`; warm-up 3 días; horizonte 60 días; IC 95 % = media ± 1,96·s/√n; umbral de servicio 5 %.
- Escenario Alt-1 = recorte −20 % (agregado: flota 6). Escenario Alt-2 = redistribución proporcional al bloqueo observado por zona en Base + refuerzo activado.

## Resultados — probabilidad de bloqueo (%) por escenario

| Escenario | Resolución | Media | sd | IC 95 % |
|---|---|---:|---:|---|
| Base | agregado | 5,21 | 0,62 | [4,99 – 5,43] |
| Base | por comuna | 60,21 | 1,21 | [59,78 – 60,64] |
| Alt-1 (recorte −20 %) | agregado | 8,52 | 0,76 | [8,25 – 8,79] |
| Alt-1 (recorte −20 %) | por comuna | 65,77 | 1,10 | [65,38 – 66,17] |
| Alt-2 (redistribución) | agregado | 5,21 | 0,62 | [4,99 – 5,43] |
| Alt-2 (redistribución) | por comuna | 46,37 | 1,34 | [45,89 – 46,85] |

Nota: en modo agregado, "Alt-2 (redistribución)" es idéntico a "Base" (con un solo pool no hay
zonas entre las cuales redistribuir). En Alt-2 por comuna, la fracción media de atenciones con
refuerzo fue 68,6 %.

## Sensibilidad (modo agregado, escenario Base)

**Tiempo de servicio:** 30 min → 3,08 % [2,93 – 3,22]; 45 min → 5,21 % [4,99 – 5,43]; 60 min → 7,87 % [7,60 – 8,14].

**Flota:** 1 → 75,45 %; 6 → 8,44 %; 7 → 5,14 %; 8 → 3,28 %; 10 → 1,53 %; 15 → 0,75 %.

**Demanda:** ×1,0 → 5,21 % [4,99 – 5,43]; ×1,2 → 6,95 % [6,71 – 7,19]; ×1,5 → 9,55 % [9,25 – 9,84].

## Validación

- Volumen simulado (365 días, media de 10 réplicas): 10.107 vs 10.082 real → +0,25 % (dentro de ±3 %).
- Perfil horario simulado vs real: ver `figuras/val_perfil_horario.png`.
- Tests: determinístico (flota 200 → 0 %), saturación (flota 2 → 49,6 %), monotonía y conservación (0 ≤ ocupadas ≤ flota) pasan.
- Reproducibilidad: dos ejecuciones completas producen artefactos idénticos (hash).
