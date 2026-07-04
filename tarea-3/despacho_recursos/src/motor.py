# -*- coding: utf-8 -*-
"""Motor de simulación de despacho de recursos de emergencia (Camino A).

Funciones puras y testeables. Este módulo es una copia EXACTA de las funciones
definidas en el notebook `despacho_recursos.ipynb` (sección 3, Motor), para
reutilización e importación. Se irá extendiendo con los motores de réplica.
"""
import heapq

import numpy as np


def generar_llegadas(tasa_horaria, dias, rng):
    """Genera tiempos de llegada (en minutos) de un proceso de Poisson NO homogéneo
    por hora del día, usando el método de thinning (adelgazamiento).

    `tasa_horaria` es un array de largo 24 con la tasa media (emergencias/hora) de
    cada hora del día. Se toma una cota superior constante `lam_max` y se generan
    candidatos con esa tasa; cada candidato en el minuto t se acepta con probabilidad
    tasa(hora(t)) / lam_max, lo que reproduce la intensidad variable.

    Los tiempos entre candidatos se generan por TRANSFORMADA INVERSA de la
    exponencial: si U ~ Uniforme(0,1), entonces  t += -ln(1 - U) / lam_max  es una
    inter-llegada Exponencial(lam_max). (Requisito del enunciado: explicar cómo se
    genera una variable aleatoria relevante.)
    """
    lam_max = tasa_horaria.max() / 60.0          # cota superior (emergencias/minuto)
    T = dias * 24 * 60                            # horizonte en minutos
    llegadas = []
    t = 0.0
    while True:
        u = rng.random()
        t += -np.log(1.0 - u) / lam_max          # transformada inversa exponencial
        if t >= T:
            break
        hora = int((t // 60) % 24)
        if rng.random() < (tasa_horaria[hora] / 60.0) / lam_max:  # aceptación (thinning)
            llegadas.append(t)
    return llegadas


def muestrear_unidades(muestra, rng):
    """Número de unidades que requiere una emergencia, por bootstrap: se elige un
    valor al azar del vector empírico observado (distribución empírica)."""
    return int(muestra[rng.integers(len(muestra))])


def muestrear_servicio(media, rng):
    """Tiempo de ocupación de UNA unidad, Exponencial de media `media` (min)."""
    return float(rng.exponential(media))


def simular_replica_agregado(flota, tasa_horaria, unidades_muestra, media_serv,
                             dias, warmup, rng, debug=False):
    """Simula UNA réplica del sistema en modo AGREGADO (una sola flota para toda la RM).

    Cola de pérdida: si al llegar una emergencia no hay unidades suficientes libres,
    se bloquea (no espera). Motor de eventos discretos con `heapq`.

    Parámetros
    ----------
    flota : int              -- número total de unidades disponibles.
    tasa_horaria : array(24) -- tasa media de llegadas por hora del día.
    unidades_muestra : array -- vector empírico de unidades/emergencia (bootstrap).
    media_serv : float       -- media de la Exponencial del tiempo de ocupación (min).
    dias : int               -- días medidos (horizonte tras el warm-up).
    warmup : int             -- días iniciales que se procesan pero NO se cuentan.
    rng : Generator          -- numpy.random.default_rng(semilla).
    debug : bool             -- si True, chequea la invariante 0 <= ocupadas <= flota.

    Devuelve
    --------
    dict con p_bloqueo (%), utilizacion (0-1), atendidas, bloqueadas, n_contadas.
    """
    warmup_min = warmup * 24 * 60
    T_fin = (warmup + dias) * 24 * 60
    llegadas = generar_llegadas(tasa_horaria, warmup + dias, rng)

    # Calendario de eventos: (tiempo, orden, tipo, k). orden = desempate estable.
    # tipo 'A' = llegada (k=0), tipo 'L' = liberación de k unidades.
    heap = []
    orden = 0
    for t in llegadas:
        heapq.heappush(heap, (t, orden, 'A', 0)); orden += 1

    ocupadas = 0
    atendidas = 0
    bloqueadas = 0
    area = 0.0          # integral de ocupadas(t) dt en la ventana medida
    t_prev = 0.0

    while heap:
        t, _, tipo, k = heapq.heappop(heap)
        # Acumular utilización sobre [t_prev, t] recortado a la ventana [warmup_min, T_fin]
        lo = max(t_prev, warmup_min)
        hi = min(t, T_fin)
        if hi > lo:
            area += ocupadas * (hi - lo)
        t_prev = t

        if tipo == 'A':
            need = muestrear_unidades(unidades_muestra, rng)
            if ocupadas + need <= flota:
                ocupadas += need
                for _ in range(need):                       # una liberación por unidad
                    dur = muestrear_servicio(media_serv, rng)
                    heapq.heappush(heap, (t + dur, orden, 'L', 1)); orden += 1
                if t >= warmup_min:
                    atendidas += 1
            else:
                if t >= warmup_min:
                    bloqueadas += 1
        else:                                               # liberación
            ocupadas -= k

        if debug:
            assert 0 <= ocupadas <= flota, f'invariante rota: ocupadas={ocupadas}, flota={flota}'

    n_contadas = atendidas + bloqueadas
    p_bloqueo = 100.0 * bloqueadas / n_contadas if n_contadas else 0.0
    utilizacion = area / (flota * (T_fin - warmup_min)) if flota else 0.0
    return {'p_bloqueo': p_bloqueo, 'utilizacion': utilizacion,
            'atendidas': atendidas, 'bloqueadas': bloqueadas, 'n_contadas': n_contadas}


def simular_replica_zonas(flota_por_zona, tasa_horaria_zona, unidades_muestra_zona,
                          media_serv, dias, warmup, rng, zonas, refuerzo=True, debug=False):
    """Simula UNA réplica en modo POR ZONA. Cada zona tiene su propia flota y su
    propio contador de unidades ocupadas.

    Al llegar una emergencia a la zona Z (índice zi):
      - si Z tiene suficientes unidades libres -> se atiende localmente;
      - si no y `refuerzo=True` -> se usan TODAS las libres locales y el faltante lo
        cubre la ÚNICA zona con más unidades libres (un solo donante); si ese donante
        no alcanza para el faltante, la emergencia se bloquea;
      - si no hay refuerzo o el donante no alcanza -> bloqueada.

    `zonas` es la lista ordenada de nombres de zona que fija el orden de las filas de
    `tasa_horaria_zona` (Z x 24) y de `unidades_muestra_zona` (lista de Z vectores).
    Las unidades prestadas se devuelven a su zona dueña al liberarse.

    Devuelve dict: p_bloqueo global (%), p_bloqueo_zona (dict), pct_refuerzo (%),
    atendidas, bloqueadas, refuerzos.
    """
    Z = len(zonas)
    flota = np.array([flota_por_zona[z] for z in zonas], dtype=np.int64)
    ocup = np.zeros(Z, dtype=np.int64)

    warmup_min = warmup * 24 * 60
    # Calendario: (tiempo, orden, tipo, dato). 'A'=llegada (dato=zona), 'L'=liberación (dato=zona dueña).
    heap = []
    orden = 0
    for zi in range(Z):
        for t in generar_llegadas(tasa_horaria_zona[zi], warmup + dias, rng):
            heapq.heappush(heap, (t, orden, 'A', zi)); orden += 1

    atendidas_z = np.zeros(Z, dtype=np.int64)
    bloqueadas_z = np.zeros(Z, dtype=np.int64)
    refuerzos = 0

    def agendar(owner, n, t):
        nonlocal orden
        for _ in range(n):
            dur = muestrear_servicio(media_serv, rng)
            heapq.heappush(heap, (t + dur, orden, 'L', owner)); orden += 1
        ocup[owner] += n

    while heap:
        t, _, tipo, dato = heapq.heappop(heap)
        if tipo == 'L':
            ocup[dato] -= 1
            if debug:
                assert 0 <= ocup[dato] <= flota[dato]
            continue

        zi = dato
        contar = t >= warmup_min
        need = muestrear_unidades(unidades_muestra_zona[zi], rng)
        libres_z = int(flota[zi] - ocup[zi])

        if libres_z >= need:                      # atención local
            agendar(zi, need, t)
            if contar:
                atendidas_z[zi] += 1
        elif refuerzo:                            # local + 1 donante
            faltan = need - libres_z
            donor, best = -1, -1
            for y in range(Z):
                if y == zi:
                    continue
                lib = int(flota[y] - ocup[y])
                if lib > best:
                    best, donor = lib, y
            if best >= faltan:
                if libres_z > 0:
                    agendar(zi, libres_z, t)
                agendar(donor, faltan, t)
                if contar:
                    atendidas_z[zi] += 1
                    refuerzos += 1
            elif contar:
                bloqueadas_z[zi] += 1
        elif contar:                              # sin refuerzo, sin cupo
            bloqueadas_z[zi] += 1

        if debug:
            assert 0 <= ocup[zi] <= flota[zi]

    atend_tot = int(atendidas_z.sum())
    bloq_tot = int(bloqueadas_z.sum())
    n_tot = atend_tot + bloq_tot
    p_bloqueo = 100.0 * bloq_tot / n_tot if n_tot else 0.0
    p_bloqueo_zona = {}
    for zi, z in enumerate(zonas):
        d = int(atendidas_z[zi] + bloqueadas_z[zi])
        p_bloqueo_zona[z] = 100.0 * bloqueadas_z[zi] / d if d else 0.0
    pct_refuerzo = 100.0 * refuerzos / atend_tot if atend_tot else 0.0
    return {'p_bloqueo': p_bloqueo, 'p_bloqueo_zona': p_bloqueo_zona,
            'pct_refuerzo': pct_refuerzo, 'atendidas': atend_tot,
            'bloqueadas': bloq_tot, 'refuerzos': refuerzos}
