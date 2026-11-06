#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vapor_agua.py
===============

Herramienta didáctica para trabajar con propiedades de saturación del agua en
el capítulo 6 («Presión de vapor y equilibrio de fases») de un curso de
estequiometría y cálculos químicos.

FUNCIONALIDAD
-------------
1. Obtener propiedades de saturación a partir de la temperatura.
2. Obtener propiedades de saturación a partir de la presión.
3. Interpolar propiedades entre valores tabulados.
4. Identificar el estado de una muestra de agua a partir de P y T.
5. Calcular la calidad o título de vapor x a partir de v, h o s.
6. Calcular propiedades de una mezcla líquido-vapor a partir de x.
7. Generar un diagrama T-v sencillo de la campana de saturación y, opcionalmente,
   localizar un estado bifásico.

DATOS Y MODELO
--------------
- La tabla interna contiene propiedades de saturación del agua entre el punto
  triple y el punto crítico. Los valores proceden de la tabulación NISTIR 5078,
  calculada a partir de IAPWS-95.
- Para P_sat(T) se utiliza la correlación internacional de presión de saturación
  del agua (forma de Wagner/IAPWS), lo que evita obtener la presión mediante una
  interpolación lineal grosera.
- Las propiedades v_f, v_g, h_f, h_g, s_f y s_g se interpolan linealmente entre
  los nodos tabulados. El programa es didáctico: no sustituye a una implementación
  completa de IAPWS-95 cuando se requiera alta precisión, especialmente cerca del
  punto crítico.

UNIDADES INTERNAS
-----------------
Temperatura: °C (se acepta también K en la entrada)
Presión: kPa (se aceptan kPa, bar, MPa y atm)
Volumen específico: m³ kg⁻¹
Entalpía específica: kJ kg⁻¹
Entropía específica: kJ kg⁻¹ K⁻¹

USO
---
Ejecución interactiva:
    python vapor_agua.py

Ayuda:
    python vapor_agua.py --help

Ejemplos de línea de comandos:
    python vapor_agua.py temperatura --T 100 --unidad-T C
    python vapor_agua.py presion --P 500 --unidad-P kPa
    python vapor_agua.py estado --P 300 --unidad-P kPa --T 160 --unidad-T C
    python vapor_agua.py titulo --P 500 --unidad-P kPa --prop h --valor 2100
    python vapor_agua.py mezcla --P 500 --unidad-P kPa --x 0.75
    python vapor_agua.py grafica --salida campana_Tv.png

CIFRAS SIGNIFICATIVAS
---------------------
Los cálculos se realizan con precisión completa. El redondeo se aplica solo a
la presentación de los resultados. Por defecto se muestran 3 cifras
significativas; puede cambiarse con --sig.

LIMITACIONES
------------
- Solo trata el equilibrio líquido-vapor del agua desde el punto triple hasta
  el punto crítico.
- No calcula propiedades de líquido comprimido ni de vapor sobrecalentado.
- La identificación de estado mediante P y T solo clasifica la región; no
  calcula propiedades monofásicas fuera de la saturación.
- La interpolación de propiedades es lineal entre nodos de la tabla interna.
- Cerca del punto crítico las propiedades cambian con rapidez; para cálculos de
  alta precisión debe utilizarse una implementación oficial/completa de IAPWS.

FUENTE PRINCIPAL DE DATOS
-------------------------
Harvey, A. H. (1998). Thermodynamic Properties of Water: Tabulation from the
IAPWS Formulation 1995 for the Thermodynamic Properties of Ordinary Water
Substance for General and Scientific Use. NISTIR 5078.
https://doi.org/10.6028/NIST.IR.5078
"""

from __future__ import annotations

import argparse
import math
import os
import sys
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


# ---------------------------------------------------------------------------
# Constantes y tabla interna
# ---------------------------------------------------------------------------

T_TRIPLE_C = 0.01
T_CRIT_C = 373.946
T_CRIT_K = 647.096
P_CRIT_KPA = 22064.0
P_TRIPLE_KPA = 0.611657

# Coeficientes de la correlación IAPWS para la presión de saturación.
_PSAT_A = (
    -7.85951783,
    1.84408259,
    -11.7866497,
    22.6807411,
    -15.9618719,
    1.80122502,
)


@dataclass(frozen=True)
class SatRow:
    """Fila de propiedades de saturación del agua."""

    T_C: float
    P_kPa: float
    vf: float       # m3/kg
    vg: float       # m3/kg
    hf: float       # kJ/kg
    hg: float       # kJ/kg
    sf: float       # kJ/(kg K)
    sg: float       # kJ/(kg K)


# Valores seleccionados de NISTIR 5078, Tabla 1 (Saturation - Temperature).
# La tabla original es más densa; se incluyen nodos suficientes para una
# herramienta de interpolación didáctica en el ámbito de este capítulo.
SAT_TABLE: Tuple[SatRow, ...] = (
    SatRow(0.01, 0.6117, 0.00100021, 205.991, 0.00, 2500.9, 0.00000, 9.1555),
    SatRow(10.0, 1.2282, 0.00100035, 106.303, 42.02, 2519.2, 0.15109, 8.8998),
    SatRow(20.0, 2.3393, 0.00100184, 57.757, 83.91, 2537.4, 0.29648, 8.6660),
    SatRow(30.0, 4.2470, 0.00100441, 32.878, 125.73, 2555.5, 0.43675, 8.4520),
    SatRow(40.0, 7.3849, 0.00100789, 19.515, 167.53, 2573.5, 0.57240, 8.2555),
    SatRow(50.0, 12.352, 0.00101215, 12.027, 209.34, 2591.3, 0.70381, 8.0748),
    SatRow(60.0, 19.946, 0.00101713, 7.6672, 251.18, 2608.8, 0.83129, 7.9081),
    SatRow(70.0, 31.201, 0.00102277, 5.0395, 293.07, 2626.1, 0.95513, 7.7540),
    SatRow(80.0, 47.414, 0.00102905, 3.4052, 335.01, 2643.0, 1.0756, 7.6111),
    SatRow(90.0, 70.182, 0.00103595, 2.3591, 377.04, 2659.5, 1.1929, 7.4781),
    # Nodo adicional de la tabla por presión: 0,10 MPa.
    SatRow(99.606, 100.0, 0.00104315, 1.6939, 417.50, 2674.9, 1.3028, 7.3588),
    SatRow(100.0, 101.42, 0.00104346, 1.6718, 419.17, 2675.6, 1.3072, 7.3541),
    SatRow(110.0, 143.38, 0.00105158, 1.2093, 461.42, 2691.1, 1.4188, 7.2381),
    SatRow(120.0, 198.67, 0.00106033, 0.89121, 503.81, 2705.9, 1.5279, 7.1291),
    SatRow(130.0, 270.28, 0.00106971, 0.66800, 546.38, 2720.1, 1.6346, 7.0264),
    # Nodo adicional de la tabla por presión: 0,30 MPa.
    SatRow(133.522, 300.0, 0.00107317, 0.60576, 561.43, 2724.9, 1.6717, 6.9916),
    SatRow(140.0, 361.54, 0.00107976, 0.50845, 589.16, 2733.4, 1.7392, 6.9293),
    SatRow(150.0, 476.16, 0.00109050, 0.39245, 632.18, 2745.9, 1.8418, 6.8371),
    # Nodo adicional de la tabla por presión: 0,50 MPa.
    SatRow(151.831, 500.0, 0.00109255, 0.37481, 640.09, 2748.1, 1.8604, 6.8207),
    SatRow(160.0, 618.23, 0.00110199, 0.30678, 675.47, 2757.4, 1.9426, 6.7491),
    SatRow(170.0, 792.19, 0.00111427, 0.24259, 719.08, 2767.9, 2.0417, 6.6650),
    SatRow(180.0, 1002.8, 0.00112740, 0.19384, 763.05, 2777.2, 2.1392, 6.5840),
    SatRow(190.0, 1255.2, 0.00114145, 0.15636, 807.43, 2785.3, 2.2355, 6.5059),
    SatRow(200.0, 1554.9, 0.00115653, 0.12721, 852.27, 2792.0, 2.3305, 6.4302),
    SatRow(210.0, 1907.7, 0.00117272, 0.10429, 897.63, 2797.3, 2.4245, 6.3563),
    SatRow(220.0, 2319.6, 0.00119017, 0.086092, 943.58, 2800.9, 2.5177, 6.2840),
    SatRow(230.0, 2797.1, 0.00120902, 0.071503, 990.19, 2802.9, 2.6101, 6.2128),
    SatRow(240.0, 3346.9, 0.00122946, 0.059705, 1037.6, 2803.0, 2.7020, 6.1423),
    SatRow(250.0, 3976.2, 0.00125173, 0.050083, 1085.8, 2800.9, 2.7935, 6.0721),
    SatRow(260.0, 4692.3, 0.00127612, 0.042173, 1135.0, 2796.6, 2.8849, 6.0016),
    SatRow(270.0, 5503.0, 0.00130300, 0.035621, 1185.3, 2789.7, 2.9765, 5.9304),
    SatRow(280.0, 6416.6, 0.00133284, 0.030153, 1236.9, 2779.9, 3.0685, 5.8579),
    SatRow(290.0, 7441.8, 0.00136630, 0.025555, 1290.0, 2766.7, 3.1612, 5.7834),
    SatRow(300.0, 8587.9, 0.00140423, 0.021660, 1345.0, 2749.6, 3.2552, 5.7059),
    SatRow(310.0, 9865.1, 0.00144787, 0.018335, 1402.2, 2727.9, 3.3510, 5.6244),
    SatRow(320.0, 11284.0, 0.00149904, 0.015471, 1462.2, 2700.6, 3.4494, 5.5372),
    SatRow(330.0, 12858.0, 0.00156061, 0.012979, 1525.9, 2666.0, 3.5518, 5.4422),
    SatRow(340.0, 14601.0, 0.00163755, 0.010781, 1594.5, 2621.8, 3.6601, 5.3356),
    SatRow(350.0, 16529.0, 0.00174002, 0.0088024, 1670.9, 2563.6, 3.7784, 5.2110),
    SatRow(360.0, 18666.0, 0.00189541, 0.0069493, 1761.7, 2481.5, 3.9167, 5.0536),
    SatRow(370.0, 21044.0, 0.00221520, 0.0049544, 1890.7, 2334.5, 4.1112, 4.8012),
    SatRow(373.946, 22064.0, 0.00310560, 0.0031056, 2084.3, 2084.3, 4.4070, 4.4070),
)


# ---------------------------------------------------------------------------
# Utilidades de entrada, unidades y formato
# ---------------------------------------------------------------------------

def parse_float(text: str) -> float:
    """Convierte una entrada numérica, aceptando coma o punto decimal."""
    return float(str(text).strip().replace(" ", "").replace(",", "."))


def fmt_sig(value: float, sig: int = 3) -> str:
    """Formatea un número con cifras significativas y coma decimal."""
    if not math.isfinite(value):
        return str(value)
    if value == 0:
        return "0"
    sig = max(1, min(int(sig), 12))
    exponent = math.floor(math.log10(abs(value)))
    decimals = sig - exponent - 1
    if -3 <= exponent < sig:
        s = f"{value:.{max(decimals, 0)}f}"
    else:
        s = f"{value:.{sig - 1}e}"
    return s.replace(".", ",")


def temp_to_c(value: float, unit: str) -> float:
    unit = unit.upper()
    if unit == "C":
        return value
    if unit == "K":
        return value - 273.15
    raise ValueError("Unidad de temperatura no reconocida. Use C o K.")


def c_to_temp(value_c: float, unit: str) -> float:
    unit = unit.upper()
    if unit == "C":
        return value_c
    if unit == "K":
        return value_c + 273.15
    raise ValueError("Unidad de temperatura no reconocida. Use C o K.")


def pressure_to_kpa(value: float, unit: str) -> float:
    unit = unit.lower()
    factors = {
        "kpa": 1.0,
        "bar": 100.0,
        "mpa": 1000.0,
        "atm": 101.325,
    }
    if unit not in factors:
        raise ValueError("Unidad de presión no reconocida. Use kPa, bar, MPa o atm.")
    return value * factors[unit]


def kpa_to_pressure(value_kpa: float, unit: str) -> float:
    unit = unit.lower()
    factors = {
        "kpa": 1.0,
        "bar": 100.0,
        "mpa": 1000.0,
        "atm": 101.325,
    }
    if unit not in factors:
        raise ValueError("Unidad de presión no reconocida. Use kPa, bar, MPa o atm.")
    return value_kpa / factors[unit]


def ask_float(prompt: str, *, positive: bool = False,
              minimum: Optional[float] = None,
              maximum: Optional[float] = None) -> float:
    while True:
        try:
            value = parse_float(input(prompt))
            if positive and value <= 0:
                raise ValueError("El valor debe ser positivo.")
            if minimum is not None and value < minimum:
                raise ValueError(f"El valor debe ser ≥ {minimum}.")
            if maximum is not None and value > maximum:
                raise ValueError(f"El valor debe ser ≤ {maximum}.")
            return value
        except ValueError as exc:
            print(f"Entrada no válida: {exc}")


def ask_float_default(prompt: str, default: float, *, minimum: Optional[float] = None,
                      maximum: Optional[float] = None) -> float:
    """Solicita un número permitiendo aceptar un valor por defecto con Intro."""
    while True:
        raw = input(f"{prompt} [{str(default).replace('.', ',')}]: ").strip()
        if not raw:
            return default
        try:
            value = parse_float(raw)
            if minimum is not None and value < minimum:
                raise ValueError(f"El valor debe ser ≥ {minimum}.")
            if maximum is not None and value > maximum:
                raise ValueError(f"El valor debe ser ≤ {maximum}.")
            return value
        except ValueError as exc:
            print(f"Entrada no válida: {exc}")


def ask_choice(prompt: str, options: Sequence[str], default: Optional[str] = None) -> str:
    opts_lower = {o.lower(): o for o in options}
    suffix = f" [{default}]" if default else ""
    while True:
        raw = input(f"{prompt}{suffix}: ").strip()
        if not raw and default is not None:
            return default
        key = raw.lower()
        if key in opts_lower:
            return opts_lower[key]
        print("Opciones válidas: " + ", ".join(options))


# ---------------------------------------------------------------------------
# Presión de saturación y su inversa
# ---------------------------------------------------------------------------

def psat_iapws_kpa(T_C: float) -> float:
    """Presión de saturación del agua en kPa entre triple y crítico."""
    if not (T_TRIPLE_C <= T_C <= T_CRIT_C):
        raise ValueError(
            f"La temperatura debe estar entre {T_TRIPLE_C} y {T_CRIT_C} °C."
        )
    T = T_C + 273.15
    tau = 1.0 - T / T_CRIT_K
    a1, a2, a3, a4, a5, a6 = _PSAT_A
    series = (
        a1 * tau
        + a2 * tau ** 1.5
        + a3 * tau ** 3
        + a4 * tau ** 3.5
        + a5 * tau ** 4
        + a6 * tau ** 7.5
    )
    ln_pr = (T_CRIT_K / T) * series
    return P_CRIT_KPA * math.exp(ln_pr)


def tsat_from_p_kpa(P_kPa: float) -> float:
    """Temperatura de saturación en °C a partir de P, por bisección."""
    if not (P_TRIPLE_KPA <= P_kPa <= P_CRIT_KPA):
        raise ValueError(
            f"La presión debe estar entre {P_TRIPLE_KPA:.6g} y {P_CRIT_KPA:g} kPa."
        )
    if math.isclose(P_kPa, P_CRIT_KPA, rel_tol=0, abs_tol=1e-10):
        return T_CRIT_C

    lo, hi = T_TRIPLE_C, T_CRIT_C
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        pmid = psat_iapws_kpa(mid)
        if pmid < P_kPa:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# ---------------------------------------------------------------------------
# Interpolación de propiedades
# ---------------------------------------------------------------------------

def _bracket_by_temperature(T_C: float) -> Tuple[SatRow, SatRow]:
    if not (SAT_TABLE[0].T_C <= T_C <= SAT_TABLE[-1].T_C):
        raise ValueError(
            f"T fuera del intervalo de la tabla ({SAT_TABLE[0].T_C}–{SAT_TABLE[-1].T_C} °C)."
        )
    for left, right in zip(SAT_TABLE[:-1], SAT_TABLE[1:]):
        if left.T_C <= T_C <= right.T_C:
            return left, right
    return SAT_TABLE[-1], SAT_TABLE[-1]


def _lerp(x: float, x1: float, x2: float, y1: float, y2: float) -> float:
    if math.isclose(x1, x2):
        return y1
    return y1 + (x - x1) * (y2 - y1) / (x2 - x1)


def saturated_properties_at_T(T_C: float) -> SatRow:
    """Obtiene propiedades de saturación a T mediante interpolación lineal."""
    left, right = _bracket_by_temperature(T_C)
    if left == right or math.isclose(T_C, left.T_C, abs_tol=0.002):
        P = psat_iapws_kpa(T_C)
        return SatRow(T_C, P, left.vf, left.vg, left.hf, left.hg, left.sf, left.sg)
    if math.isclose(T_C, right.T_C, abs_tol=0.002):
        P = psat_iapws_kpa(T_C)
        return SatRow(T_C, P, right.vf, right.vg, right.hf, right.hg, right.sf, right.sg)

    P = psat_iapws_kpa(T_C)
    values = {}
    for name in ("vf", "vg", "hf", "hg", "sf", "sg"):
        values[name] = _lerp(
            T_C, left.T_C, right.T_C, getattr(left, name), getattr(right, name)
        )
    return SatRow(T_C, P, **values)


def saturated_properties_at_P(P_kPa: float) -> SatRow:
    T_C = tsat_from_p_kpa(P_kPa)
    row = saturated_properties_at_T(T_C)
    return SatRow(T_C, P_kPa, row.vf, row.vg, row.hf, row.hg, row.sf, row.sg)


def interpolation_info(T_C: float) -> Tuple[SatRow, SatRow, float]:
    """Devuelve nodos utilizados y fracción de interpolación."""
    left, right = _bracket_by_temperature(T_C)
    if left == right:
        f = 0.0
    else:
        f = (T_C - left.T_C) / (right.T_C - left.T_C)
    return left, right, f


# ---------------------------------------------------------------------------
# Cálculos de estado y mezcla
# ---------------------------------------------------------------------------

def identify_state(P_kPa: float, T_C: float, tol_C: float = 0.10) -> Dict[str, object]:
    """Clasifica el estado a partir de P y T dentro del alcance del capítulo."""
    if P_kPa <= 0:
        raise ValueError("La presión debe ser positiva.")
    if T_C < T_TRIPLE_C:
        return {
            "estado": "fuera del equilibrio líquido-vapor tratado",
            "detalle": "T está por debajo del punto triple; debe considerarse el equilibrio sólido-vapor o sólido-líquido.",
            "Tsat_C": None,
        }

    if T_C > T_CRIT_C:
        if P_kPa > P_CRIT_KPA:
            estado = "fluido supercrítico"
            detalle = "T > Tc y P > Pc; no existe frontera líquido-vapor."
        else:
            estado = "gas (región monofásica por encima de Tc)"
            detalle = "T > Tc; no puede obtenerse líquido por simple compresión isotérmica mientras T permanezca por encima de Tc."
        return {"estado": estado, "detalle": detalle, "Tsat_C": None}

    if P_kPa > P_CRIT_KPA:
        return {
            "estado": "líquido comprimido",
            "detalle": "Para T < Tc, una presión superior a Pc se encuentra por encima de la presión de saturación.",
            "Tsat_C": None,
        }

    if P_kPa < P_TRIPLE_KPA:
        return {
            "estado": "vapor / región sin equilibrio líquido-vapor estable",
            "detalle": "P está por debajo de la presión del punto triple; la fase líquida no es estable en equilibrio.",
            "Tsat_C": None,
        }

    Tsat = tsat_from_p_kpa(P_kPa)
    delta = T_C - Tsat
    if abs(delta) <= tol_C:
        estado = "condición de saturación"
        detalle = (
            "P y T son compatibles con la curva de saturación dentro de la tolerancia. "
            "Con solo P y T no puede saberse si se trata de líquido saturado, vapor saturado o mezcla bifásica."
        )
    elif delta > 0:
        estado = "vapor sobrecalentado"
        detalle = "T es superior a la temperatura de saturación correspondiente a la presión dada."
    else:
        estado = "líquido comprimido o subenfriado"
        detalle = "T es inferior a la temperatura de saturación correspondiente a la presión dada."
    return {"estado": estado, "detalle": detalle, "Tsat_C": Tsat, "delta_T_C": delta}


def quality_from_property(row: SatRow, prop: str, value: float) -> Tuple[float, float, float]:
    """Calcula x a partir de v, h o s. Devuelve (x, yf, yg)."""
    prop = prop.lower()
    mapping = {
        "v": (row.vf, row.vg),
        "h": (row.hf, row.hg),
        "s": (row.sf, row.sg),
    }
    if prop not in mapping:
        raise ValueError("Propiedad no válida. Use v, h o s.")
    yf, yg = mapping[prop]
    if math.isclose(yg, yf):
        raise ValueError("En el punto crítico no puede definirse la calidad de vapor.")
    x = (value - yf) / (yg - yf)
    return x, yf, yg


def mixture_properties(row: SatRow, x: float) -> Dict[str, float]:
    if not (0.0 <= x <= 1.0):
        raise ValueError("La calidad x debe estar entre 0 y 1.")
    return {
        "v": row.vf + x * (row.vg - row.vf),
        "h": row.hf + x * (row.hg - row.hf),
        "s": row.sf + x * (row.sg - row.sf),
    }


# ---------------------------------------------------------------------------
# Presentación
# ---------------------------------------------------------------------------

def print_sat_row(row: SatRow, sig: int = 3, show_interp: bool = True) -> None:
    print("\nPROPIEDADES DE SATURACIÓN DEL AGUA")
    print("=" * 40)
    print(f"T_sat : {fmt_sig(row.T_C, sig)} °C  ({fmt_sig(row.T_C + 273.15, sig)} K)")
    print(f"P_sat : {fmt_sig(row.P_kPa, sig)} kPa")
    print(f"v_f   : {fmt_sig(row.vf, sig)} m³ kg⁻¹")
    print(f"v_g   : {fmt_sig(row.vg, sig)} m³ kg⁻¹")
    print(f"h_f   : {fmt_sig(row.hf, sig)} kJ kg⁻¹")
    print(f"h_g   : {fmt_sig(row.hg, sig)} kJ kg⁻¹")
    print(f"h_fg  : {fmt_sig(row.hg - row.hf, sig)} kJ kg⁻¹")
    print(f"s_f   : {fmt_sig(row.sf, sig)} kJ kg⁻¹ K⁻¹")
    print(f"s_g   : {fmt_sig(row.sg, sig)} kJ kg⁻¹ K⁻¹")
    print(f"s_fg  : {fmt_sig(row.sg - row.sf, sig)} kJ kg⁻¹ K⁻¹")

    if show_interp:
        left, right, frac = interpolation_info(row.T_C)
        if (not math.isclose(row.T_C, left.T_C, abs_tol=0.002)
                and not math.isclose(row.T_C, right.T_C, abs_tol=0.002)
                and left != right):
            print("\nInterpolación de propiedades:")
            print(f"  nodo inferior: {fmt_sig(left.T_C, sig)} °C")
            print(f"  nodo superior: {fmt_sig(right.T_C, sig)} °C")
            print(f"  fracción de interpolación: {fmt_sig(frac, sig)}")
            print("  P_sat se calcula con la correlación IAPWS; v, h y s se interpolan linealmente.")

    if row.T_C > 350:
        print("\nADVERTENCIA: se trabaja cerca del punto crítico; use una implementación completa de IAPWS si necesita alta precisión.")


def print_quality_result(row: SatRow, prop: str, value: float, sig: int = 3) -> None:
    x, yf, yg = quality_from_property(row, prop, value)
    unit = {"v": "m³ kg⁻¹", "h": "kJ kg⁻¹", "s": "kJ kg⁻¹ K⁻¹"}[prop]
    print("\nCÁLCULO DEL TÍTULO DE VAPOR")
    print("=" * 34)
    print(f"T_sat = {fmt_sig(row.T_C, sig)} °C")
    print(f"P_sat = {fmt_sig(row.P_kPa, sig)} kPa")
    print(f"{prop}_f = {fmt_sig(yf, sig)} {unit}")
    print(f"{prop}_g = {fmt_sig(yg, sig)} {unit}")
    print(f"{prop}   = {fmt_sig(value, sig)} {unit}")
    print(f"x = ({prop} - {prop}_f)/({prop}_g - {prop}_f) = {fmt_sig(x, sig)}")

    if x < 0:
        print("\nRESULTADO: x < 0. El estado no pertenece a la región bifásica; el valor es compatible con una región líquida.")
    elif x > 1:
        print("\nRESULTADO: x > 1. El estado no pertenece a la región bifásica; el valor es compatible con una región de vapor.")
    else:
        print(f"Fracción másica de vapor : {fmt_sig(100*x, sig)} %")
        print(f"Fracción másica de líquido: {fmt_sig(100*(1-x), sig)} %")
        if math.isclose(x, 0.0, abs_tol=1e-12):
            print("Estado: líquido saturado.")
        elif math.isclose(x, 1.0, abs_tol=1e-12):
            print("Estado: vapor saturado seco.")
        else:
            print("Estado: mezcla líquido-vapor (vapor húmedo).")


def print_mixture_result(row: SatRow, x: float, sig: int = 3) -> None:
    props = mixture_properties(row, x)
    print("\nPROPIEDADES DE LA MEZCLA SATURADA")
    print("=" * 39)
    print(f"T_sat = {fmt_sig(row.T_C, sig)} °C")
    print(f"P_sat = {fmt_sig(row.P_kPa, sig)} kPa")
    print(f"x     = {fmt_sig(x, sig)}")
    print(f"v     = {fmt_sig(props['v'], sig)} m³ kg⁻¹")
    print(f"h     = {fmt_sig(props['h'], sig)} kJ kg⁻¹")
    print(f"s     = {fmt_sig(props['s'], sig)} kJ kg⁻¹ K⁻¹")


# ---------------------------------------------------------------------------
# Gráfica T-v
# ---------------------------------------------------------------------------

def plot_tv(output: str = "campana_Tv_agua.png",
            state: Optional[Tuple[float, float]] = None,
            dpi: int = 300) -> str:
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise RuntimeError(
            "Para generar gráficas es necesario instalar matplotlib."
        ) from exc

    vf = [r.vf for r in SAT_TABLE]
    vg = [r.vg for r in SAT_TABLE]
    T = [r.T_C for r in SAT_TABLE]

    fig, ax = plt.subplots(figsize=(7.2, 5.2))
    ax.semilogx(vf, T, marker="o", markersize=2.5, label="Líquido saturado")
    ax.semilogx(vg, T, marker="o", markersize=2.5, label="Vapor saturado")

    if state is not None:
        v_state, T_state = state
        ax.semilogx([v_state], [T_state], marker="o", markersize=7, linestyle="None", label="Estado")

    ax.set_xlabel(r"Volumen específico, $v$ (m$^3$ kg$^{-1}$)")
    ax.set_ylabel(r"Temperatura, $T$ (°C)")
    ax.set_title("Diagrama T–v de saturación del agua")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output, dpi=dpi, transparent=True, bbox_inches="tight")
    plt.close(fig)
    return os.path.abspath(output)


# ---------------------------------------------------------------------------
# Modos de ejecución
# ---------------------------------------------------------------------------

def resolve_row_from_args_or_prompt(args, *, interactive: bool) -> SatRow:
    """Obtiene una fila de saturación por P o T desde argumentos o diálogo."""
    if getattr(args, "P", None) is not None:
        unit_p = getattr(args, "unidad_P", "kPa")
        return saturated_properties_at_P(pressure_to_kpa(args.P, unit_p))
    if getattr(args, "T", None) is not None:
        unit_t = getattr(args, "unidad_T", "C")
        return saturated_properties_at_T(temp_to_c(args.T, unit_t))

    if not interactive:
        raise ValueError("Debe indicar --P o --T.")

    mode = ask_choice("Definir el estado de saturación mediante P o T", ["P", "T"], "P")
    if mode == "P":
        P = ask_float("Presión: ", positive=True)
        u = ask_choice("Unidad de presión", ["kPa", "bar", "MPa", "atm"], "kPa")
        return saturated_properties_at_P(pressure_to_kpa(P, u))
    T = ask_float("Temperatura: ")
    u = ask_choice("Unidad de temperatura", ["C", "K"], "C")
    return saturated_properties_at_T(temp_to_c(T, u))


def cmd_temperature(args) -> None:
    T_C = temp_to_c(args.T, args.unidad_T)
    print_sat_row(saturated_properties_at_T(T_C), args.sig)


def cmd_pressure(args) -> None:
    P_kPa = pressure_to_kpa(args.P, args.unidad_P)
    print_sat_row(saturated_properties_at_P(P_kPa), args.sig)


def cmd_state(args) -> None:
    P_kPa = pressure_to_kpa(args.P, args.unidad_P)
    T_C = temp_to_c(args.T, args.unidad_T)
    result = identify_state(P_kPa, T_C, args.tol)
    print("\nIDENTIFICACIÓN DEL ESTADO")
    print("=" * 31)
    print(f"P = {fmt_sig(P_kPa, args.sig)} kPa")
    print(f"T = {fmt_sig(T_C, args.sig)} °C")
    if result.get("Tsat_C") is not None:
        Tsat = float(result["Tsat_C"])
        print(f"T_sat(P) = {fmt_sig(Tsat, args.sig)} °C")
        print(f"T - T_sat = {fmt_sig(T_C - Tsat, args.sig)} °C")
    print(f"Estado: {result['estado']}")
    print(str(result["detalle"]))


def cmd_quality(args) -> None:
    row = resolve_row_from_args_or_prompt(args, interactive=False)
    print_quality_result(row, args.prop, args.valor, args.sig)


def cmd_mixture(args) -> None:
    row = resolve_row_from_args_or_prompt(args, interactive=False)
    print_mixture_result(row, args.x, args.sig)


def cmd_plot(args) -> None:
    state = None
    if args.x is not None and args.P is None and args.T is None:
        raise ValueError("Para localizar una mezcla con --x debe indicar también --P o --T.")
    if args.P is not None and args.x is not None:
        row = saturated_properties_at_P(pressure_to_kpa(args.P, args.unidad_P))
        props = mixture_properties(row, args.x)
        state = (props["v"], row.T_C)
    elif args.T is not None and args.x is not None:
        row = saturated_properties_at_T(temp_to_c(args.T, args.unidad_T))
        props = mixture_properties(row, args.x)
        state = (props["v"], row.T_C)
    path = plot_tv(args.salida, state=state, dpi=args.dpi)
    print(f"Gráfica guardada en: {path}")


# ---------------------------------------------------------------------------
# Menú interactivo
# ---------------------------------------------------------------------------

def interactive_menu(sig: int = 3) -> None:
    while True:
        print("\n" + "=" * 64)
        print("VAPOR DE AGUA — PROPIEDADES DE SATURACIÓN")
        print("=" * 64)
        print("1. Propiedades de saturación a partir de la temperatura")
        print("2. Propiedades de saturación a partir de la presión")
        print("3. Identificar el estado a partir de P y T")
        print("4. Calcular calidad o título de vapor")
        print("5. Calcular propiedades de una mezcla a partir de x")
        print("6. Generar diagrama T-v")
        print("7. Cambiar cifras significativas")
        print("0. Salir")

        choice = input("\nSeleccione una opción: ").strip()
        try:
            if choice == "0":
                print("Fin del programa.")
                return

            if choice == "1":
                T = ask_float("Temperatura: ")
                unit = ask_choice("Unidad", ["C", "K"], "C")
                row = saturated_properties_at_T(temp_to_c(T, unit))
                print_sat_row(row, sig)

            elif choice == "2":
                P = ask_float("Presión: ", positive=True)
                unit = ask_choice("Unidad", ["kPa", "bar", "MPa", "atm"], "kPa")
                row = saturated_properties_at_P(pressure_to_kpa(P, unit))
                print_sat_row(row, sig)

            elif choice == "3":
                P = ask_float("Presión: ", positive=True)
                up = ask_choice("Unidad de presión", ["kPa", "bar", "MPa", "atm"], "kPa")
                T = ask_float("Temperatura: ")
                ut = ask_choice("Unidad de temperatura", ["C", "K"], "C")
                tol = ask_float_default("Tolerancia para considerar saturación (°C)", 0.10, minimum=0.0)
                result = identify_state(pressure_to_kpa(P, up), temp_to_c(T, ut), tol)
                print("\nRESULTADO")
                print("=" * 20)
                if result.get("Tsat_C") is not None:
                    print(f"T_sat = {fmt_sig(float(result['Tsat_C']), sig)} °C")
                print(f"Estado: {result['estado']}")
                print(result["detalle"])

            elif choice == "4":
                class Obj: pass
                dummy = Obj()
                dummy.P = dummy.T = None
                row = resolve_row_from_args_or_prompt(dummy, interactive=True)
                prop = ask_choice("Propiedad conocida", ["v", "h", "s"], "h")
                units = {"v": "m³ kg⁻¹", "h": "kJ kg⁻¹", "s": "kJ kg⁻¹ K⁻¹"}
                value = ask_float(f"Valor de {prop} ({units[prop]}): ")
                print_quality_result(row, prop, value, sig)

            elif choice == "5":
                class Obj: pass
                dummy = Obj()
                dummy.P = dummy.T = None
                row = resolve_row_from_args_or_prompt(dummy, interactive=True)
                x = ask_float("Calidad x (0–1): ", minimum=0.0, maximum=1.0)
                print_mixture_result(row, x, sig)

            elif choice == "6":
                output = input("Nombre del PNG [campana_Tv_agua.png]: ").strip() or "campana_Tv_agua.png"
                locate = ask_choice("¿Desea localizar una mezcla bifásica?", ["si", "no"], "no")
                state = None
                if locate == "si":
                    class Obj: pass
                    dummy = Obj()
                    dummy.P = dummy.T = None
                    row = resolve_row_from_args_or_prompt(dummy, interactive=True)
                    x = ask_float("Calidad x (0–1): ", minimum=0.0, maximum=1.0)
                    v = mixture_properties(row, x)["v"]
                    state = (v, row.T_C)
                path = plot_tv(output, state=state)
                print(f"Gráfica guardada en: {path}")

            elif choice == "7":
                sig = int(ask_float("Número de cifras significativas (1–8): ", minimum=1, maximum=8))
                print(f"Se utilizarán {sig} cifras significativas.")

            else:
                print("Opción no válida.")

        except (ValueError, RuntimeError) as exc:
            print(f"\nERROR: {exc}")


# ---------------------------------------------------------------------------
# argparse
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Propiedades de saturación del agua, identificación de estado, "
            "calidad de vapor y diagrama T-v."
        ),
        epilog=(
            "Sin subcomando se abre un menú interactivo. Los datos internos "
            "proceden de NISTIR 5078 / IAPWS-95."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--sig", type=int, default=3,
                        help="Cifras significativas de salida (por defecto: 3).")

    sub = parser.add_subparsers(dest="command")

    def add_sig_option(p):
        p.add_argument("--sig", type=int, default=argparse.SUPPRESS,
                       help="Cifras significativas de salida (también puede indicarse antes del subcomando).")

    p_t = sub.add_parser("temperatura", help="Propiedades de saturación a partir de T.")
    add_sig_option(p_t)
    p_t.add_argument("--T", type=parse_float, required=True, help="Temperatura.")
    p_t.add_argument("--unidad-T", choices=["C", "K"], default="C")
    p_t.set_defaults(func=cmd_temperature)

    p_p = sub.add_parser("presion", help="Propiedades de saturación a partir de P.")
    add_sig_option(p_p)
    p_p.add_argument("--P", type=parse_float, required=True, help="Presión.")
    p_p.add_argument("--unidad-P", choices=["kPa", "bar", "MPa", "atm"], default="kPa")
    p_p.set_defaults(func=cmd_pressure)

    p_s = sub.add_parser("estado", help="Clasifica el estado a partir de P y T.")
    add_sig_option(p_s)
    p_s.add_argument("--P", type=parse_float, required=True)
    p_s.add_argument("--unidad-P", choices=["kPa", "bar", "MPa", "atm"], default="kPa")
    p_s.add_argument("--T", type=parse_float, required=True)
    p_s.add_argument("--unidad-T", choices=["C", "K"], default="C")
    p_s.add_argument("--tol", type=parse_float, default=0.10,
                     help="Tolerancia en °C para considerar saturación (defecto: 0,10).")
    p_s.set_defaults(func=cmd_state)

    p_q = sub.add_parser("titulo", help="Calcula x a partir de v, h o s en saturación.")
    add_sig_option(p_q)
    group_q = p_q.add_mutually_exclusive_group(required=True)
    group_q.add_argument("--P", type=parse_float)
    group_q.add_argument("--T", type=parse_float)
    p_q.add_argument("--unidad-P", choices=["kPa", "bar", "MPa", "atm"], default="kPa")
    p_q.add_argument("--unidad-T", choices=["C", "K"], default="C")
    p_q.add_argument("--prop", choices=["v", "h", "s"], required=True)
    p_q.add_argument("--valor", type=parse_float, required=True,
                     help="Valor de la propiedad específica.")
    p_q.set_defaults(func=cmd_quality)

    p_m = sub.add_parser("mezcla", help="Propiedades de una mezcla saturada a partir de x.")
    add_sig_option(p_m)
    group_m = p_m.add_mutually_exclusive_group(required=True)
    group_m.add_argument("--P", type=parse_float)
    group_m.add_argument("--T", type=parse_float)
    p_m.add_argument("--unidad-P", choices=["kPa", "bar", "MPa", "atm"], default="kPa")
    p_m.add_argument("--unidad-T", choices=["C", "K"], default="C")
    p_m.add_argument("--x", type=parse_float, required=True)
    p_m.set_defaults(func=cmd_mixture)

    p_g = sub.add_parser("grafica", help="Genera el diagrama T-v de saturación.")
    add_sig_option(p_g)
    p_g.add_argument("--salida", default="campana_Tv_agua.png")
    p_g.add_argument("--dpi", type=int, default=300)
    p_g.add_argument("--x", type=parse_float, help="Calidad para localizar una mezcla.")
    group_g = p_g.add_mutually_exclusive_group(required=False)
    group_g.add_argument("--P", type=parse_float)
    group_g.add_argument("--T", type=parse_float)
    p_g.add_argument("--unidad-P", choices=["kPa", "bar", "MPa", "atm"], default="kPa")
    p_g.add_argument("--unidad-T", choices=["C", "K"], default="C")
    p_g.set_defaults(func=cmd_plot)

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not (1 <= args.sig <= 12):
        parser.error("--sig debe estar entre 1 y 12.")

    if args.command is None:
        interactive_menu(args.sig)
        return 0

    try:
        args.func(args)
    except (ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
