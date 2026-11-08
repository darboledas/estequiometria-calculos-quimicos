#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
presion_vapor.py
=================

Herramienta didáctica para el capítulo 6 «Presión de vapor y equilibrio de fases»
del manual «Estequiometría y cálculos químicos».

FUNCIONALIDAD
-------------
El programa reúne en una sola aplicación los cálculos y representaciones más
habituales del capítulo:

1. Ecuación de Antoine
   - cálculo de presión de vapor P* a partir de T;
   - cálculo de T a partir de P*;
   - base interna de constantes de la Tabla 6.1;
   - introducción manual de A, B y C.

2. Ecuación integrada de Clausius-Clapeyron
   - cálculo de P2*;
   - cálculo de T2;
   - estimación de la entalpía molar de vaporización.

3. Sublimación
   - mismos tipos de cálculo que Clausius-Clapeyron, usando P_sub y
     Delta H_sub.

4. Correlación de Lee-Kesler
   - cálculo de Tr, Pr y P* a partir de Tc, Pc y factor acéntrico.

5. Interpolación de datos de presión de vapor
   - interpolación lineal directa de P* frente a T;
   - interpolación lineal de ln(P*) frente a 1/T;
   - comparación de ambos resultados.

6. Líneas de Dühring
   - construcción a partir de datos (T_dis, P_dis*);
   - conversión de P a temperatura equivalente de una sustancia de referencia;
   - ajuste lineal;
   - estimación de P_dis* a una T_dis dada;
   - gráfica opcional.

7. Representaciones gráficas
   - P* frente a T;
   - escala semilogarítmica P* frente a T;
   - ln(P*/kPa) frente a 1/T;
   - comparación entre sustancias;
   - exportación PNG a 300 ppp y fondo transparente.

8. Comparación de métodos
   - Antoine, Clausius-Clapeyron y Lee-Kesler cuando se proporcionan los
     datos necesarios.

HIPÓTESIS Y LIMITACIONES
------------------------
- Antoine es una correlación empírica y solo debe utilizarse dentro del
  intervalo de validez de sus coeficientes. El programa bloquea por defecto
  la extrapolación, salvo autorización explícita.
- La forma integrada de Clausius-Clapeyron supone, entre otras aproximaciones,
  vapor ideal, volumen del líquido despreciable frente al del vapor y entalpía
  molar de cambio de fase aproximadamente constante en el intervalo.
- Lee-Kesler se usa aquí en la forma de presión de vapor del capítulo. No se
  permite Tr >= 1. Para Tr fuera de 0,3 < Tr < 1,0 se solicita autorización
  explícita porque se abandona el intervalo didáctico recomendado.
- Una línea de Dühring es una correlación aproximada válida para una composición
  y un intervalo limitados. No debe extrapolarse sin justificación.

UNIDADES
--------
El programa acepta temperaturas en K o °C y presiones en Pa, kPa, bar, atm o
mmHg. Internamente se convierten a K y kPa. Los resultados se presentan con un
número configurable de cifras significativas (3 por defecto); los cálculos
internos no se redondean prematuramente.

REQUISITOS
----------
- Python 3.9 o posterior.
- Solo para las gráficas: matplotlib.

USO
---
Modo interactivo:
    python presion_vapor.py

Ayuda:
    python presion_vapor.py --help

Ejemplos de línea de comandos:
    python presion_vapor.py antoine --sustancia agua --temperatura 350
    python presion_vapor.py antoine --sustancia agua --presion 50
    python presion_vapor.py clausius --p1 25 --t1 273 --t2 298 --dh 28.5
    python presion_vapor.py lee-kesler --t 350 --tc 540.2 --pc 27.4 \
        --pc-unidad bar --omega 0.349
    python presion_vapor.py interpolar --t1 320 --p1 12 --t2 340 --p2 28.5 \
        --t 330
    python presion_vapor.py grafica --sustancias agua,etanol,tolueno \
        --tipo semilog --tmin 280 --tmax 370 --salida presiones.png

FUENTES DE LAS CORRELACIONES
----------------------------
- Antoine: constantes de la Tabla 6.1 del capítulo 6.
- Lee, B. I. & Kesler, M. G. (1975), AIChE Journal, 21(3), 510-527.
- La formulación de Clausius-Clapeyron, Dühring y las restantes expresiones se
  ajusta al desarrollo del capítulo 6.

Este programa es una herramienta docente. No sustituye bases de datos ni
correlaciones de referencia cuando se requiere alta precisión.
"""

from __future__ import annotations

import argparse
import math
import os
import sys
import unicodedata
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


R = 8.31446261815324  # J mol^-1 K^-1


@dataclass(frozen=True)
class AntoineData:
    nombre: str
    A: float
    B: float
    C: float
    Tmin: float
    Tmax: float
    aliases: Tuple[str, ...] = ()


# Tabla 6.1 del capítulo 6.
ANTOINE: Dict[str, AntoineData] = {
    "agua": AntoineData("Agua", 7.06252, 1650.270, -46.854, 284.0, 441.0, ("water",)),
    "acetona": AntoineData("Acetona", 6.25017, 1214.208, -43.198, 241.0, 350.0, ("acetone",)),
    "acetonitrilo": AntoineData("Acetonitrilo", 6.27873, 1355.374, -37.853, 288.0, 362.0, ("acetonitrile",)),
    "amoniaco": AntoineData("Amoníaco", 6.86886, 1113.928, -10.409, 240.0, 372.0, ("ammonia",)),
    "benceno": AntoineData("Benceno", 6.03053, 1211.035, -52.360, 280.0, 377.0, ("benzene",)),
    "etanol": AntoineData("Etanol", 7.16985, 1554.301, -50.500, 270.0, 369.0, ("alcohol etilico", "alcohol_etilico", "ethyl alcohol")),
    "n-heptano": AntoineData("n-Heptano", 6.01876, 1264.370, -56.510, 270.0, 400.0, ("heptano", "nheptano", "n-heptane")),
    "n-hexano": AntoineData("n-Hexano", 6.00265, 1171.531, -48.780, 245.0, 370.0, ("hexano", "nhexano", "n-hexane")),
    "metanol": AntoineData("Metanol", 7.19735, 1574.991, -34.290, 257.0, 364.0, ("alcohol metilico", "alcohol_metilico", "methanol")),
    "tolueno": AntoineData("Tolueno", 6.07956, 1344.802, -53.670, 280.0, 410.0, ("toluene",)),
    "acido benzoico": AntoineData("Ácido benzoico", 6.57885, 1819.998, -125.200, 405.0, 560.0, ("benzoico", "benzoic acid")),
}


PRESSURE_TO_KPA = {
    "pa": 0.001,
    "kpa": 1.0,
    "bar": 100.0,
    "atm": 101.325,
    "mmhg": 0.13332236842105263,
}


# ---------------------------------------------------------------------------
# Utilidades generales
# ---------------------------------------------------------------------------


def norm_text(text: str) -> str:
    text = unicodedata.normalize("NFD", text.strip().lower())
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return " ".join(text.replace("_", " ").split())


def parse_number(value: str) -> float:
    """Acepta coma o punto como separador decimal."""
    try:
        result = float(value.strip().replace(" ", "").replace(",", "."))
    except Exception as exc:
        raise ValueError(f"No se reconoce como número: {value!r}") from exc
    if not math.isfinite(result):
        raise ValueError("El dato debe ser un número finito.")
    return result


def require_positive(value: float, name: str) -> float:
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} debe ser mayor que cero.")
    return value


def require_finite(value: float, name: str) -> float:
    if not math.isfinite(value):
        raise ValueError(f"{name} debe ser un número finito.")
    return value


def temperature_to_k(value: float, unit: str) -> float:
    unit_n = norm_text(unit)
    if unit_n in {"k", "kelvin"}:
        T = value
    elif unit_n in {"c", "°c", "celsius", "grado celsius", "grados celsius"}:
        T = value + 273.15
    else:
        raise ValueError("Unidad de temperatura no reconocida. Use K o C.")
    if T <= 0:
        raise ValueError("La temperatura debe ser superior a 0 K.")
    return T


def temperature_from_k(value: float, unit: str) -> float:
    unit_n = norm_text(unit)
    if unit_n in {"k", "kelvin"}:
        return value
    if unit_n in {"c", "°c", "celsius", "grado celsius", "grados celsius"}:
        return value - 273.15
    raise ValueError("Unidad de temperatura no reconocida. Use K o C.")


def pressure_to_kpa(value: float, unit: str) -> float:
    require_positive(value, "La presión")
    key = norm_text(unit).replace(" ", "")
    if key not in PRESSURE_TO_KPA:
        raise ValueError("Unidad de presión no reconocida. Use Pa, kPa, bar, atm o mmHg.")
    return value * PRESSURE_TO_KPA[key]


def pressure_from_kpa(value: float, unit: str) -> float:
    require_positive(value, "La presión")
    key = norm_text(unit).replace(" ", "")
    if key not in PRESSURE_TO_KPA:
        raise ValueError("Unidad de presión no reconocida. Use Pa, kPa, bar, atm o mmHg.")
    return value / PRESSURE_TO_KPA[key]


def pressure_unit_label(unit: str) -> str:
    key = norm_text(unit).replace(" ", "")
    labels = {"pa": "Pa", "kpa": "kPa", "bar": "bar", "atm": "atm", "mmhg": "mmHg"}
    if key not in labels:
        raise ValueError("Unidad de presión no reconocida.")
    return labels[key]


def enthalpy_to_j_per_mol(
    value: float,
    unit: str,
    molar_mass_g_mol: Optional[float] = None,
) -> float:
    require_positive(value, "La entalpía")
    key = norm_text(unit).replace(" ", "")
    if key in {"j/mol", "jmol-1", "jmol^-1"}:
        return value
    if key in {"kj/mol", "kjmol-1", "kjmol^-1"}:
        return value * 1000.0
    if key in {"j/kg", "jkg-1", "jkg^-1"}:
        if molar_mass_g_mol is None:
            raise ValueError("Para convertir una entalpía específica se necesita la masa molar.")
        require_positive(molar_mass_g_mol, "La masa molar")
        return value * (molar_mass_g_mol / 1000.0)
    if key in {"kj/kg", "kjkg-1", "kjkg^-1"}:
        if molar_mass_g_mol is None:
            raise ValueError("Para convertir una entalpía específica se necesita la masa molar.")
        require_positive(molar_mass_g_mol, "La masa molar")
        return value * 1000.0 * (molar_mass_g_mol / 1000.0)
    raise ValueError("Unidad de entalpía no reconocida. Use J/mol, kJ/mol, J/kg o kJ/kg.")


def _exp_to_pretty(text: str) -> str:
    """Convierte 1.23e+04 en 1,23 × 10^4."""
    if "e" not in text.lower():
        return text.replace(".", ",")
    mantissa, exponent = text.lower().split("e")
    exponent_i = int(exponent)
    return f"{mantissa.replace('.', ',')} × 10^{exponent_i}"


def format_sig(value: float, sig: int = 3) -> str:
    """Formatea conservando explícitamente las cifras significativas pedidas."""
    if not math.isfinite(value):
        return str(value)
    sig = max(1, min(int(sig), 12))
    if value == 0:
        return "0"
    exponent = int(math.floor(math.log10(abs(value))))
    # Notación científica para valores muy grandes o muy pequeños.
    if exponent >= sig or exponent <= -4:
        text = f"{value:.{sig - 1}e}"
        return _exp_to_pretty(text)
    decimals = max(sig - exponent - 1, 0)
    return f"{value:.{decimals}f}".replace(".", ",")


def format_fixed(value: float, decimals: int = 2) -> str:
    return f"{value:.{decimals}f}".replace(".", ",")


def ask(prompt: str, default: Optional[str] = None) -> str:
    suffix = f" [{default}]" if default is not None else ""
    while True:
        value = input(f"{prompt}{suffix}: ").strip()
        if value:
            return value
        if default is not None:
            return default
        print("Debe introducir un valor.")


def ask_float(prompt: str, default: Optional[float] = None) -> float:
    d = None if default is None else str(default).replace(".", ",")
    while True:
        try:
            return parse_number(ask(prompt, d))
        except ValueError as exc:
            print(f"Error: {exc}")


def ask_int(prompt: str, default: Optional[int] = None, minimum: Optional[int] = None) -> int:
    d = None if default is None else str(default)
    while True:
        try:
            value = int(ask(prompt, d))
            if minimum is not None and value < minimum:
                raise ValueError(f"El valor debe ser >= {minimum}.")
            return value
        except ValueError as exc:
            print(f"Error: {exc}")


def ask_yes_no(prompt: str, default: bool = False) -> bool:
    d = "s" if default else "n"
    while True:
        value = norm_text(ask(prompt + " [s/n]", d))
        if value in {"s", "si", "sí", "y", "yes"}:
            return True
        if value in {"n", "no"}:
            return False
        print("Responda s o n.")


def print_header(title: str) -> None:
    print("\n" + title)
    print("=" * len(title))


def print_warning(message: str) -> None:
    print(f"ADVERTENCIA: {message}")


def ensure_matplotlib():
    try:
        import matplotlib.pyplot as plt  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "Para generar gráficas se necesita matplotlib. Instálelo con: pip install matplotlib"
        ) from exc
    return plt


def save_figure(fig, filename: str, dpi: int = 300, transparent: bool = True) -> str:
    filename = filename.strip()
    if not filename.lower().endswith(".png"):
        filename += ".png"
    fig.savefig(filename, dpi=dpi, transparent=transparent, bbox_inches="tight")
    return os.path.abspath(filename)


# ---------------------------------------------------------------------------
# Antoine
# ---------------------------------------------------------------------------


def find_antoine(name: str) -> AntoineData:
    key = norm_text(name)
    for canonical, data in ANTOINE.items():
        candidates = {norm_text(canonical), norm_text(data.nombre), *(norm_text(a) for a in data.aliases)}
        if key in candidates:
            return data
    raise ValueError(
        "Sustancia no incluida. Use 'listar' para ver la base interna o introduzca coeficientes manualmente."
    )


def antoine_pressure_kpa(T: float, data: AntoineData) -> float:
    require_positive(T, "La temperatura absoluta")
    denom = T + data.C
    if denom == 0:
        raise ValueError("T + C no puede ser cero en la ecuación de Antoine.")
    exponent = data.A - data.B / denom
    try:
        P = 10.0 ** exponent
    except OverflowError as exc:
        raise ValueError("La presión calculada por Antoine excede el rango numérico representable.") from exc
    return require_positive(P, "La presión calculada")


def antoine_temperature_k(P_kpa: float, data: AntoineData) -> float:
    require_positive(P_kpa, "La presión")
    denom = data.A - math.log10(P_kpa)
    if denom == 0:
        raise ValueError("La presión introducida hace singular la ecuación inversa de Antoine.")
    T = data.B / denom - data.C
    return require_positive(T, "La temperatura calculada")


def check_antoine_range(T: float, data: AntoineData, allow_extrapolation: bool = False) -> None:
    if not (data.Tmin <= T <= data.Tmax):
        msg = (
            f"T = {T:.3f} K queda fuera del intervalo de validez de Antoine para {data.nombre} "
            f"({data.Tmin:g}-{data.Tmax:g} K)."
        )
        if not allow_extrapolation:
            raise ValueError(msg + " No se realiza la extrapolación sin autorización explícita.")
        print_warning(msg + " El resultado es una extrapolación.")


def manual_antoine_data() -> AntoineData:
    print("Introduzca los coeficientes para la forma log10(P*/kPa) = A - B/(T + C).")
    nombre = ask("Nombre o etiqueta de la sustancia", "Sustancia")
    A = ask_float("A")
    B = ask_float("B (K)")
    C = ask_float("C (K)")
    Tmin = ask_float("Temperatura mínima de validez (K)")
    Tmax = ask_float("Temperatura máxima de validez (K)")
    if Tmax <= Tmin:
        raise ValueError("Tmax debe ser mayor que Tmin.")
    return AntoineData(nombre, A, B, C, Tmin, Tmax)


def choose_antoine_data() -> AntoineData:
    print("Sustancias disponibles:")
    names = list(ANTOINE.values())
    for i, data in enumerate(names, 1):
        print(f"  {i:2d}. {data.nombre:16s}  {data.Tmin:g}-{data.Tmax:g} K")
    print(f"  {len(names)+1:2d}. Introducir coeficientes manualmente")
    choice = ask_int("Seleccione una opción", 1, 1)
    if 1 <= choice <= len(names):
        return names[choice - 1]
    if choice == len(names) + 1:
        return manual_antoine_data()
    raise ValueError("Opción no válida.")


# ---------------------------------------------------------------------------
# Clausius-Clapeyron y sublimación
# ---------------------------------------------------------------------------


def cc_pressure2(P1_kpa: float, T1: float, T2: float, dh_j_mol: float) -> float:
    require_positive(P1_kpa, "P1")
    require_positive(T1, "T1")
    require_positive(T2, "T2")
    require_positive(dh_j_mol, "La entalpía molar")
    ln_ratio = (dh_j_mol / R) * (1.0 / T1 - 1.0 / T2)
    try:
        P2 = P1_kpa * math.exp(ln_ratio)
    except OverflowError as exc:
        raise ValueError("La presión obtenida por Clausius-Clapeyron excede el rango numérico.") from exc
    return require_positive(P2, "La presión calculada")


def cc_temperature2(P1_kpa: float, T1: float, P2_kpa: float, dh_j_mol: float) -> float:
    require_positive(P1_kpa, "P1")
    require_positive(P2_kpa, "P2")
    require_positive(T1, "T1")
    require_positive(dh_j_mol, "La entalpía molar")
    inv_T2 = 1.0 / T1 - (R / dh_j_mol) * math.log(P2_kpa / P1_kpa)
    if inv_T2 <= 0:
        raise ValueError("Los datos conducen a una temperatura absoluta no física.")
    return 1.0 / inv_T2


def cc_enthalpy(P1_kpa: float, T1: float, P2_kpa: float, T2: float) -> float:
    require_positive(P1_kpa, "P1")
    require_positive(P2_kpa, "P2")
    require_positive(T1, "T1")
    require_positive(T2, "T2")
    denominator = 1.0 / T1 - 1.0 / T2
    if abs(denominator) < 1e-15:
        raise ValueError("T1 y T2 no pueden ser iguales para estimar la entalpía.")
    dh = R * math.log(P2_kpa / P1_kpa) / denominator
    if dh <= 0:
        raise ValueError(
            "Los datos producen una entalpía no positiva. Compruebe el orden de las temperaturas y presiones."
        )
    return dh


def print_cc_hypotheses(kind: str = "vaporización") -> None:
    print(f"Método: Clausius-Clapeyron integrada ({kind}).")
    print("Hipótesis principales: vapor aproximadamente ideal; volumen de la fase condensada")
    print("despreciable frente al del vapor; entalpía molar de cambio de fase aproximadamente")
    print("constante en el intervalo de temperaturas considerado.")


# ---------------------------------------------------------------------------
# Lee-Kesler
# ---------------------------------------------------------------------------


def lee_kesler_ln_pr_terms(Tr: float) -> Tuple[float, float]:
    require_positive(Tr, "Tr")
    f0 = 5.92714 - 6.09648 / Tr - 1.28862 * math.log(Tr) + 0.169347 * Tr**6
    f1 = 15.2518 - 15.6875 / Tr - 13.4721 * math.log(Tr) + 0.43577 * Tr**6
    return f0, f1


def lee_kesler_pressure_kpa(
    T: float,
    Tc: float,
    Pc_kpa: float,
    omega: float,
    allow_extrapolation: bool = False,
) -> Tuple[float, float, float, float, float]:
    require_positive(T, "T")
    require_positive(Tc, "Tc")
    require_positive(Pc_kpa, "Pc")
    require_finite(omega, "El factor acéntrico")
    Tr = T / Tc
    if Tr >= 1.0:
        raise ValueError(
            "Tr >= 1. La correlación de presión de vapor no debe utilizarse por encima de la temperatura crítica."
        )
    if Tr <= 0.3:
        msg = f"Tr = {Tr:.4f} queda fuera del intervalo didáctico 0,3 < Tr < 1,0."
        if not allow_extrapolation:
            raise ValueError(msg + " Use autorización explícita si desea extrapolar.")
        print_warning(msg + " El resultado debe interpretarse con cautela.")
    f0, f1 = lee_kesler_ln_pr_terms(Tr)
    ln_Pr = f0 + omega * f1
    try:
        Pr = math.exp(ln_Pr)
        P_kpa = Pr * Pc_kpa
    except OverflowError as exc:
        raise ValueError("La presión estimada por Lee-Kesler excede el rango numérico.") from exc
    require_positive(P_kpa, "La presión de vapor estimada")
    return Tr, f0, f1, Pr, P_kpa


# ---------------------------------------------------------------------------
# Interpolación
# ---------------------------------------------------------------------------


def linear_interpolation(T1: float, P1: float, T2: float, P2: float, T: float) -> float:
    require_positive(T1, "T1")
    require_positive(T2, "T2")
    require_positive(T, "T")
    require_positive(P1, "P1")
    require_positive(P2, "P2")
    if T1 == T2:
        raise ValueError("T1 y T2 no pueden ser iguales.")
    return P1 + (P2 - P1) * (T - T1) / (T2 - T1)


def cc_interpolation(T1: float, P1: float, T2: float, P2: float, T: float) -> float:
    require_positive(T1, "T1")
    require_positive(T2, "T2")
    require_positive(T, "T")
    require_positive(P1, "P1")
    require_positive(P2, "P2")
    x1, x2, x = 1.0 / T1, 1.0 / T2, 1.0 / T
    if x1 == x2:
        raise ValueError("T1 y T2 no pueden ser iguales.")
    lnP = math.log(P1) + (x - x1) / (x2 - x1) * math.log(P2 / P1)
    return math.exp(lnP)


def is_inside_interval(value: float, a: float, b: float) -> bool:
    lo, hi = sorted((a, b))
    return lo <= value <= hi


# ---------------------------------------------------------------------------
# Dühring
# ---------------------------------------------------------------------------


def linear_regression(x: Sequence[float], y: Sequence[float]) -> Tuple[float, float, Optional[float]]:
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("Se necesitan al menos dos pares de datos.")
    n = len(x)
    xbar = sum(x) / n
    ybar = sum(y) / n
    sxx = sum((xi - xbar) ** 2 for xi in x)
    if sxx <= 0:
        raise ValueError("Los valores de la variable independiente no pueden ser todos iguales.")
    sxy = sum((xi - xbar) * (yi - ybar) for xi, yi in zip(x, y))
    slope = sxy / sxx
    intercept = ybar - slope * xbar
    if n == 2:
        r2 = None
    else:
        yhat = [slope * xi + intercept for xi in x]
        ss_res = sum((yi - yh) ** 2 for yi, yh in zip(y, yhat))
        ss_tot = sum((yi - ybar) ** 2 for yi in y)
        r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else None
    return slope, intercept, r2


def duhring_fit(
    data_points: Sequence[Tuple[float, float]],
    reference: AntoineData,
    allow_extrapolation: bool = False,
) -> Tuple[float, float, Optional[float], List[float]]:
    """
    Ajusta T_dis = a*T_ref + b, coherente con el desarrollo del capítulo.
    data_points: (T_dis [K], P_dis* [kPa]).
    """
    if len(data_points) < 2:
        raise ValueError("Se necesitan al menos dos datos de la disolución.")
    T_dis_values: List[float] = []
    T_ref_values: List[float] = []
    for T_dis, P in data_points:
        require_positive(T_dis, "T_dis")
        require_positive(P, "P_dis*")
        T_ref = antoine_temperature_k(P, reference)
        check_antoine_range(T_ref, reference, allow_extrapolation)
        T_dis_values.append(T_dis)
        T_ref_values.append(T_ref)
    a, b, r2 = linear_regression(T_ref_values, T_dis_values)
    if abs(a) < 1e-15:
        raise ValueError("El ajuste produce una pendiente nula y no puede invertirse.")
    return a, b, r2, T_ref_values


def duhring_pressure_at_temperature(
    T_dis: float,
    a: float,
    b: float,
    reference: AntoineData,
    allow_extrapolation: bool = False,
) -> Tuple[float, float]:
    require_positive(T_dis, "T_dis")
    T_ref = (T_dis - b) / a
    check_antoine_range(T_ref, reference, allow_extrapolation)
    P = antoine_pressure_kpa(T_ref, reference)
    return T_ref, P


def plot_duhring(
    data_points: Sequence[Tuple[float, float]],
    T_ref_values: Sequence[float],
    a: float,
    b: float,
    label: str,
    target: Optional[Tuple[float, float]] = None,
    filename: Optional[str] = None,
) -> None:
    plt = ensure_matplotlib()
    xs = [p[0] for p in data_points]  # T_dis, eje horizontal como en la figura 6.7
    ys = list(T_ref_values)
    xmin, xmax = min(xs), max(xs)
    margin = max((xmax - xmin) * 0.08, 1.0)
    xline = [xmin - margin + i * (xmax - xmin + 2 * margin) / 199 for i in range(200)]
    yline = [(x - b) / a for x in xline]

    fig, ax = plt.subplots(figsize=(7.0, 4.8))
    ax.plot(xline, yline, label=f"Línea de Dühring — {label}")
    ax.scatter(xs, ys, marker="s", label="Datos")
    if target is not None:
        ax.scatter([target[0]], [target[1]], marker="s", label="Estimación")
    ax.set_xlabel("Temperatura de ebullición de la disolución (K)")
    ax.set_ylabel("Temperatura de ebullición de la referencia (K)")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    if filename:
        path = save_figure(fig, filename, dpi=300, transparent=True)
        print(f"Gráfica guardada en: {path}")
    else:
        plt.show()
    plt.close(fig)


# ---------------------------------------------------------------------------
# Gráficas generales
# ---------------------------------------------------------------------------


def linspace(a: float, b: float, n: int = 200) -> List[float]:
    if n < 2:
        return [a]
    return [a + (b - a) * i / (n - 1) for i in range(n)]


def plot_antoine_curves(
    substances: Sequence[AntoineData],
    kind: str,
    Tmin: Optional[float],
    Tmax: Optional[float],
    filename: Optional[str],
    allow_extrapolation: bool,
) -> None:
    plt = ensure_matplotlib()
    if not substances:
        raise ValueError("Debe seleccionar al menos una sustancia.")

    auto_tmin = Tmin is None
    auto_tmax = Tmax is None
    if auto_tmin:
        Tmin = max(d.Tmin for d in substances)
    if auto_tmax:
        Tmax = min(d.Tmax for d in substances)
    if Tmax <= Tmin:
        if not allow_extrapolation:
            raise ValueError(
                "Las sustancias seleccionadas no comparten un intervalo de Antoine común. "
                "Indique Tmin/Tmax y autorice la extrapolación si procede."
            )
        if auto_tmin:
            Tmin = min(d.Tmin for d in substances)
        if auto_tmax:
            Tmax = max(d.Tmax for d in substances)

    require_positive(Tmin, "Tmin")
    require_positive(Tmax, "Tmax")
    if Tmax <= Tmin:
        raise ValueError("Tmax debe ser mayor que Tmin.")

    fig, ax = plt.subplots(figsize=(8.0, 5.2))
    for data in substances:
        if Tmin < data.Tmin or Tmax > data.Tmax:
            if not allow_extrapolation:
                raise ValueError(
                    f"El intervalo {Tmin:g}-{Tmax:g} K sale del rango de Antoine de {data.nombre} "
                    f"({data.Tmin:g}-{data.Tmax:g} K)."
                )
            print_warning(
                f"La curva de {data.nombre} incluye extrapolación fuera de {data.Tmin:g}-{data.Tmax:g} K."
            )
        Ts = linspace(Tmin, Tmax, 250)
        Ps = [antoine_pressure_kpa(T, data) for T in Ts]
        kind_n = norm_text(kind)
        if kind_n in {"pt", "p-t", "lineal", "p"}:
            ax.plot(Ts, Ps, label=data.nombre)
            ax.set_xlabel("T (K)")
            ax.set_ylabel("P* (kPa)")
        elif kind_n in {"semilog", "semi", "logp"}:
            ax.semilogy(Ts, Ps, label=data.nombre)
            ax.set_xlabel("T (K)")
            ax.set_ylabel("P* (kPa)")
        elif kind_n in {"clausius", "lnp", "lnp-1/t", "lnp1t"}:
            xs = [1.0 / T for T in Ts]
            ys = [math.log(P) for P in Ps]
            ax.plot(xs, ys, label=data.nombre)
            ax.set_xlabel("1/T (K⁻¹)")
            ax.set_ylabel("ln(P*/kPa)")
        else:
            raise ValueError("Tipo de gráfica no reconocido: use pt, semilog o clausius.")

    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    if filename:
        path = save_figure(fig, filename, dpi=300, transparent=True)
        print(f"Gráfica guardada en: {path}")
    else:
        plt.show()
    plt.close(fig)


# ---------------------------------------------------------------------------
# Modos interactivos
# ---------------------------------------------------------------------------


def interactive_antoine(sig: int) -> None:
    print_header("ECUACIÓN DE ANTOINE")
    data = choose_antoine_data()
    print(f"\n{data.nombre}: A={data.A}, B={data.B} K, C={data.C} K; rango {data.Tmin:g}-{data.Tmax:g} K.")
    print("1. Calcular P* a partir de T")
    print("2. Calcular T a partir de P*")
    option = ask_int("Opción", 1, 1)
    if option == 1:
        Tval = ask_float("Temperatura")
        Tunit = ask("Unidad de temperatura (K/C)", "K")
        T = temperature_to_k(Tval, Tunit)
        try:
            check_antoine_range(T, data, False)
        except ValueError as exc:
            print_warning(str(exc))
            if not ask_yes_no("¿Desea continuar como extrapolación?", False):
                return
        P = antoine_pressure_kpa(T, data)
        out_unit = ask("Unidad de presión de salida (Pa/kPa/bar/atm/mmHg)", "kPa")
        out = pressure_from_kpa(P, out_unit)
        print(f"P* = {format_sig(out, sig)} {pressure_unit_label(out_unit)}")
    elif option == 2:
        Pval = ask_float("Presión de vapor")
        Punit = ask("Unidad de presión (Pa/kPa/bar/atm/mmHg)", "kPa")
        P = pressure_to_kpa(Pval, Punit)
        T = antoine_temperature_k(P, data)
        try:
            check_antoine_range(T, data, False)
        except ValueError as exc:
            print_warning(str(exc))
            if not ask_yes_no("¿Desea aceptar el resultado como extrapolación?", False):
                return
        out_unit = ask("Unidad de temperatura de salida (K/C)", "K")
        out = temperature_from_k(T, out_unit)
        label = "K" if norm_text(out_unit) == "k" else "°C"
        print(f"T = {format_sig(out, sig)} {label}")
    else:
        print("Opción no válida.")


def interactive_cc(sig: int, sublimation: bool = False) -> None:
    title = "SUBLIMACIÓN — CLAUSIUS-CLAPEYRON" if sublimation else "CLAUSIUS-CLAPEYRON — VAPORIZACIÓN"
    print_header(title)
    print("1. Calcular P2")
    print("2. Calcular T2")
    print("3. Calcular entalpía molar de cambio de fase")
    option = ask_int("Opción", 1, 1)
    Punit = ask("Unidad de presión de los datos (Pa/kPa/bar/atm/mmHg)", "kPa")

    if option == 1:
        P1 = pressure_to_kpa(ask_float("P1"), Punit)
        T1 = temperature_to_k(ask_float("T1"), ask("Unidad de T1 (K/C)", "K"))
        T2 = temperature_to_k(ask_float("T2"), ask("Unidad de T2 (K/C)", "K"))
        dh_value = ask_float("Entalpía de cambio de fase")
        dh_unit = ask("Unidad (J/mol, kJ/mol, J/kg o kJ/kg)", "kJ/mol")
        M = None
        if "/kg" in dh_unit.lower() or "kg-1" in dh_unit.lower() or "kg^-1" in dh_unit.lower():
            M = ask_float("Masa molar (g/mol)")
        dh = enthalpy_to_j_per_mol(dh_value, dh_unit, M)
        P2 = cc_pressure2(P1, T1, T2, dh)
        out = pressure_from_kpa(P2, Punit)
        print_cc_hypotheses("sublimación" if sublimation else "vaporización")
        symbol = "P_sub,2" if sublimation else "P2*"
        print(f"{symbol} = {format_sig(out, sig)} {pressure_unit_label(Punit)}")

    elif option == 2:
        P1 = pressure_to_kpa(ask_float("P1"), Punit)
        P2 = pressure_to_kpa(ask_float("P2"), Punit)
        T1 = temperature_to_k(ask_float("T1"), ask("Unidad de T1 (K/C)", "K"))
        dh_value = ask_float("Entalpía de cambio de fase")
        dh_unit = ask("Unidad (J/mol, kJ/mol, J/kg o kJ/kg)", "kJ/mol")
        M = None
        if "/kg" in dh_unit.lower() or "kg-1" in dh_unit.lower() or "kg^-1" in dh_unit.lower():
            M = ask_float("Masa molar (g/mol)")
        dh = enthalpy_to_j_per_mol(dh_value, dh_unit, M)
        T2 = cc_temperature2(P1, T1, P2, dh)
        out_unit = ask("Unidad de temperatura de salida (K/C)", "K")
        Tout = temperature_from_k(T2, out_unit)
        label = "K" if norm_text(out_unit) == "k" else "°C"
        print_cc_hypotheses("sublimación" if sublimation else "vaporización")
        print(f"T2 = {format_sig(Tout, sig)} {label}")

    elif option == 3:
        P1 = pressure_to_kpa(ask_float("P1"), Punit)
        P2 = pressure_to_kpa(ask_float("P2"), Punit)
        Tunit = ask("Unidad de T1 y T2 (K/C)", "K")
        T1 = temperature_to_k(ask_float("T1"), Tunit)
        T2 = temperature_to_k(ask_float("T2"), Tunit)
        dh = cc_enthalpy(P1, T1, P2, T2)
        print_cc_hypotheses("sublimación" if sublimation else "vaporización")
        symbol = "ΔH_sub" if sublimation else "ΔH_vap"
        print(f"{symbol} = {format_sig(dh / 1000.0, sig)} kJ mol⁻¹")
    else:
        print("Opción no válida.")


def interactive_lee_kesler(sig: int) -> None:
    print_header("CORRELACIÓN DE LEE-KESLER")
    T = temperature_to_k(ask_float("Temperatura"), ask("Unidad de T (K/C)", "K"))
    Tc = temperature_to_k(ask_float("Temperatura crítica Tc"), ask("Unidad de Tc (K/C)", "K"))
    pc_unit = ask("Unidad de Pc (Pa/kPa/bar/atm/mmHg)", "bar")
    Pc = pressure_to_kpa(ask_float("Presión crítica Pc"), pc_unit)
    omega = ask_float("Factor acéntrico ω")
    allow = False
    Tr = T / Tc
    if Tr <= 0.3:
        print_warning(f"Tr = {Tr:.4f} queda fuera del intervalo didáctico 0,3 < Tr < 1,0.")
        allow = ask_yes_no("¿Desea continuar?", False)
        if not allow:
            return
    Tr, f0, f1, Pr, P = lee_kesler_pressure_kpa(T, Tc, Pc, omega, allow)
    print(f"Tr = {format_sig(Tr, sig)}")
    print(f"(ln Pr)^(0) = {format_sig(f0, sig)}")
    print(f"(ln Pr)^(1) = {format_sig(f1, sig)}")
    print(f"Pr = {format_sig(Pr, sig)}")
    out_unit = ask("Unidad de presión de salida", "kPa")
    print(f"P* = {format_sig(pressure_from_kpa(P, out_unit), sig)} {pressure_unit_label(out_unit)}")
    print("Nota: la correlación es generalizada; su exactitud depende de la naturaleza del fluido.")


def interactive_interpolation(sig: int) -> None:
    print_header("INTERPOLACIÓN DE PRESIÓN DE VAPOR")
    Tunit = ask("Unidad de temperaturas (K/C)", "K")
    Punit = ask("Unidad de presiones (Pa/kPa/bar/atm/mmHg)", "kPa")
    T1 = temperature_to_k(ask_float("T1"), Tunit)
    P1 = pressure_to_kpa(ask_float("P1*"), Punit)
    T2 = temperature_to_k(ask_float("T2"), Tunit)
    P2 = pressure_to_kpa(ask_float("P2*"), Punit)
    T = temperature_to_k(ask_float("Temperatura objetivo T"), Tunit)
    if not is_inside_interval(T, T1, T2):
        print_warning("La temperatura objetivo queda fuera del intervalo de los datos: esto es extrapolación.")
        if not ask_yes_no("¿Desea continuar?", False):
            return
    P_lin = linear_interpolation(T1, P1, T2, P2, T)
    P_cc = cc_interpolation(T1, P1, T2, P2, T)
    out_lin = pressure_from_kpa(P_lin, Punit)
    out_cc = pressure_from_kpa(P_cc, Punit)
    diff = abs(P_cc - P_lin)
    pct = 100.0 * diff / P_cc
    print(f"Interpolación directa P*-T:      {format_sig(out_lin, sig)} {pressure_unit_label(Punit)}")
    print(f"Interpolación ln(P*) frente 1/T: {format_sig(out_cc, sig)} {pressure_unit_label(Punit)}")
    print(f"Diferencia absoluta:             {format_sig(pressure_from_kpa(diff, Punit), sig)} {pressure_unit_label(Punit)}")
    print(f"Diferencia relativa:             {format_sig(pct, sig)} %")
    print("La segunda interpolación es coherente con la forma integrada de Clausius-Clapeyron.")


def interactive_duhring(sig: int) -> None:
    print_header("LÍNEA DE DÜHRING")
    print("La correlación se ajusta en la forma T_dis = a·T_ref + b.")
    print("Para cada dato se introduce T_dis y la presión de vapor de la disolución a esa temperatura.")
    reference = choose_antoine_data()
    n = ask_int("Número de pares experimentales", 2, 2)
    Tunit = ask("Unidad de T_dis (K/C)", "K")
    Punit = ask("Unidad de P_dis* (Pa/kPa/bar/atm/mmHg)", "kPa")
    points: List[Tuple[float, float]] = []
    for i in range(1, n + 1):
        print(f"Dato {i}")
        Tdis = temperature_to_k(ask_float("  T_dis"), Tunit)
        P = pressure_to_kpa(ask_float("  P_dis*"), Punit)
        points.append((Tdis, P))
    try:
        a, b, r2, Trefs = duhring_fit(points, reference, False)
    except ValueError as exc:
        print_warning(str(exc))
        if not ask_yes_no("¿Desea permitir extrapolación de la correlación de referencia?", False):
            return
        a, b, r2, Trefs = duhring_fit(points, reference, True)

    print(f"Ajuste: T_dis = ({format_sig(a, sig)}) T_ref + ({format_sig(b, sig)})")
    if r2 is None:
        print("R²: no se usa como diagnóstico con solo dos puntos, ya que la recta queda determinada exactamente.")
    else:
        print(f"R² = {format_sig(r2, max(sig, 4))}")

    for i, ((Tdis, P), Tref) in enumerate(zip(points, Trefs), 1):
        print(
            f"Dato {i}: T_dis={format_sig(Tdis, sig)} K; "
            f"P*={format_sig(P, sig)} kPa -> T_ref={format_sig(Tref, sig)} K"
        )

    target_tuple: Optional[Tuple[float, float]] = None
    if ask_yes_no("¿Desea estimar P_dis* a otra temperatura?", True):
        Ttarget = temperature_to_k(ask_float("T_dis objetivo"), Tunit)
        if not is_inside_interval(Ttarget, min(p[0] for p in points), max(p[0] for p in points)):
            print_warning("T_dis objetivo queda fuera del intervalo experimental: se trata de extrapolación de Dühring.")
            if not ask_yes_no("¿Desea continuar?", False):
                return
        try:
            Tref, Ptarget = duhring_pressure_at_temperature(Ttarget, a, b, reference, False)
        except ValueError as exc:
            print_warning(str(exc))
            if not ask_yes_no("¿Desea permitir extrapolación de Antoine para la referencia?", False):
                return
            Tref, Ptarget = duhring_pressure_at_temperature(Ttarget, a, b, reference, True)
        outP = pressure_from_kpa(Ptarget, Punit)
        print(f"T_ref equivalente = {format_sig(Tref, sig)} K")
        print(f"P_dis* = {format_sig(outP, sig)} {pressure_unit_label(Punit)}")
        target_tuple = (Ttarget, Tref)

    if ask_yes_no("¿Desea generar la gráfica de Dühring?", True):
        filename = ask("Nombre del PNG (vacío no permitido)", "duhring.png")
        plot_duhring(points, Trefs, a, b, reference.nombre, target_tuple, filename)


def interactive_graphs() -> None:
    print_header("REPRESENTACIONES GRÁFICAS")
    print("Sustancias disponibles:")
    for data in ANTOINE.values():
        print(f"  - {data.nombre}")
    raw = ask("Sustancias separadas por comas", "agua,etanol,tolueno")
    names = [x.strip() for x in raw.split(",") if x.strip()]
    substances = [find_antoine(name) for name in names]
    print("Tipos: pt | semilog | clausius")
    kind = ask("Tipo de gráfica", "semilog")
    use_common = ask_yes_no("¿Usar automáticamente el intervalo común de Antoine?", True)
    if use_common:
        Tmin = None
        Tmax = None
    else:
        Tmin = temperature_to_k(ask_float("Tmin"), ask("Unidad de Tmin (K/C)", "K"))
        Tmax = temperature_to_k(ask_float("Tmax"), ask("Unidad de Tmax (K/C)", "K"))
    allow = False
    try:
        # La comprobación se hace dentro de la función.
        filename = ask("Nombre del archivo PNG", "presion_vapor.png")
        plot_antoine_curves(substances, kind, Tmin, Tmax, filename, False)
    except ValueError as exc:
        print_warning(str(exc))
        if ask_yes_no("¿Desea permitir extrapolación para generar la gráfica?", False):
            filename = ask("Nombre del archivo PNG", "presion_vapor.png")
            plot_antoine_curves(substances, kind, Tmin, Tmax, filename, True)


def interactive_compare(sig: int) -> None:
    print_header("COMPARACIÓN DE MÉTODOS")
    data = choose_antoine_data()
    T = temperature_to_k(ask_float("Temperatura objetivo"), ask("Unidad (K/C)", "K"))
    methods: List[Tuple[str, float, str]] = []

    try:
        check_antoine_range(T, data, False)
        P_ant = antoine_pressure_kpa(T, data)
        methods.append(("Antoine", P_ant, "Dentro del intervalo de coeficientes"))
    except ValueError as exc:
        print_warning(str(exc))
        if ask_yes_no("¿Incluir Antoine como extrapolación?", False):
            P_ant = antoine_pressure_kpa(T, data)
            methods.append(("Antoine", P_ant, "EXTRAPOLACIÓN"))

    if ask_yes_no("¿Dispone de un punto de referencia y ΔH_vap para Clausius-Clapeyron?", True):
        Punit = ask("Unidad de P_ref", "kPa")
        Pref = pressure_to_kpa(ask_float("P_ref*"), Punit)
        Tref = temperature_to_k(ask_float("T_ref"), ask("Unidad de T_ref (K/C)", "K"))
        dh_val = ask_float("ΔH_vap")
        dh_unit = ask("Unidad de ΔH_vap", "kJ/mol")
        M = None
        if "/kg" in dh_unit.lower() or "kg-1" in dh_unit.lower() or "kg^-1" in dh_unit.lower():
            M = ask_float("Masa molar (g/mol)")
        dh = enthalpy_to_j_per_mol(dh_val, dh_unit, M)
        Pcc = cc_pressure2(Pref, Tref, T, dh)
        methods.append(("Clausius-Clapeyron", Pcc, "ΔH considerada constante"))

    if ask_yes_no("¿Dispone de Tc, Pc y ω para Lee-Kesler?", False):
        Tc = temperature_to_k(ask_float("Tc"), ask("Unidad de Tc (K/C)", "K"))
        pc_unit = ask("Unidad de Pc", "bar")
        Pc = pressure_to_kpa(ask_float("Pc"), pc_unit)
        omega = ask_float("ω")
        allow = False
        Tr = T / Tc
        if Tr <= 0.3:
            print_warning(f"Tr={Tr:.4f} queda fuera del intervalo didáctico recomendado.")
            allow = ask_yes_no("¿Incluir Lee-Kesler como extrapolación?", False)
        if Tr >= 1:
            print_warning("Tr >= 1: no se añadirá Lee-Kesler para presión de vapor.")
        elif Tr > 0.3 or allow:
            _, _, _, _, Plk = lee_kesler_pressure_kpa(T, Tc, Pc, omega, allow)
            methods.append(("Lee-Kesler", Plk, "Correlación generalizada" + ("; extrapolación" if allow and Tr <= 0.3 else "")))

    if not methods:
        print("No hay métodos calculables con los datos disponibles.")
        return

    print("\nResultados a la misma temperatura:")
    print(f"{'Método':24s} {'P* (kPa)':>16s}  Observación")
    print("-" * 72)
    for name, P, note in methods:
        print(f"{name:24s} {format_sig(P, sig):>16s}  {note}")

    if len(methods) > 1:
        reference_name, reference_P, _ = methods[0]
        print(f"\nDiferencias respecto a {reference_name}:")
        for name, P, _ in methods[1:]:
            pct = 100.0 * (P - reference_P) / reference_P
            print(f"  {name}: {format_sig(pct, sig)} %")


def interactive_menu(sig: int) -> None:
    while True:
        print_header("PRESIÓN DE VAPOR — MENÚ PRINCIPAL")
        print("1. Ecuación de Antoine")
        print("2. Clausius-Clapeyron: vaporización")
        print("3. Sublimación")
        print("4. Correlación de Lee-Kesler")
        print("5. Interpolación de presión de vapor")
        print("6. Línea de Dühring")
        print("7. Representaciones gráficas")
        print("8. Comparación de métodos")
        print("9. Mostrar sustancias de Antoine")
        print("0. Salir")
        choice = ask("Seleccione una opción", "1")
        try:
            if choice == "1":
                interactive_antoine(sig)
            elif choice == "2":
                interactive_cc(sig, False)
            elif choice == "3":
                interactive_cc(sig, True)
            elif choice == "4":
                interactive_lee_kesler(sig)
            elif choice == "5":
                interactive_interpolation(sig)
            elif choice == "6":
                interactive_duhring(sig)
            elif choice == "7":
                interactive_graphs()
            elif choice == "8":
                interactive_compare(sig)
            elif choice == "9":
                print("\nBase interna de Antoine:")
                for data in ANTOINE.values():
                    print(
                        f"- {data.nombre}: A={data.A}, B={data.B}, C={data.C}; "
                        f"{data.Tmin:g}-{data.Tmax:g} K"
                    )
            elif choice == "0":
                print("Fin del programa.")
                return
            else:
                print("Opción no válida.")
        except (ValueError, RuntimeError, OverflowError) as exc:
            print(f"ERROR: {exc}")
        except KeyboardInterrupt:
            print("\nOperación cancelada por el usuario.")


# ---------------------------------------------------------------------------
# Línea de comandos
# ---------------------------------------------------------------------------


def add_common_sig(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--cifras",
        type=int,
        default=3,
        help="Cifras significativas de los resultados (por defecto: 3).",
    )


def add_sub_sig(parser: argparse.ArgumentParser) -> None:
    """Permite escribir --cifras también después del subcomando."""
    parser.add_argument(
        "--cifras",
        type=int,
        default=argparse.SUPPRESS,
        help="Cifras significativas de los resultados.",
    )


def build_parser() -> argparse.ArgumentParser:
    examples = """
Ejemplos:
  python presion_vapor.py
  python presion_vapor.py antoine --sustancia agua --temperatura 350
  python presion_vapor.py antoine --sustancia agua --presion 50
  python presion_vapor.py clausius --p1 25 --t1 273 --t2 298 --dh 28.5
  python presion_vapor.py lee-kesler --t 350 --tc 540.2 --pc 27.4 --pc-unidad bar --omega 0.349
  python presion_vapor.py interpolar --t1 320 --p1 12 --t2 340 --p2 28.5 --t 330
  python presion_vapor.py grafica --sustancias agua,etanol,tolueno --tipo semilog --tmin 280 --tmax 369 --salida presiones.png
"""
    parser = argparse.ArgumentParser(
        description="Cálculos y gráficas de presión de vapor, equilibrio y correlaciones del capítulo 6.",
        epilog=examples,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    add_common_sig(parser)
    sub = parser.add_subparsers(dest="command")

    p_ant = sub.add_parser("antoine", help="Calcular P* o T mediante Antoine.")
    add_sub_sig(p_ant)
    p_ant.add_argument("--sustancia", required=True, help="Nombre de una sustancia de la base interna.")
    g_ant = p_ant.add_mutually_exclusive_group(required=True)
    g_ant.add_argument("--temperatura", type=parse_number, help="Temperatura para calcular P*.")
    g_ant.add_argument("--presion", type=parse_number, help="Presión para calcular T.")
    p_ant.add_argument("--t-unidad", default="K", choices=["K", "C"], help="Unidad de temperatura.")
    p_ant.add_argument("--p-unidad", default="kPa", choices=["Pa", "kPa", "bar", "atm", "mmHg"], help="Unidad de presión.")
    p_ant.add_argument("--permitir-extrapolacion", action="store_true", help="Permitir el uso fuera del intervalo de Antoine.")

    p_cc = sub.add_parser("clausius", help="Clausius-Clapeyron integrada para vaporización.")
    add_sub_sig(p_cc)
    p_cc.add_argument("--p1", required=True, type=parse_number)
    p_cc.add_argument("--t1", required=True, type=parse_number)
    p_cc.add_argument("--t2", type=parse_number, help="Segunda temperatura. Con --dh calcula P2; con --p2 y sin --dh permite estimar ΔH.")
    p_cc.add_argument("--p2", type=parse_number, help="Segunda presión. Con --dh calcula T2; con --t2 y sin --dh permite estimar ΔH.")
    p_cc.add_argument("--dh", type=parse_number, help="Entalpía de vaporización.")
    p_cc.add_argument("--dh-unidad", default="kJ/mol", help="J/mol, kJ/mol, J/kg o kJ/kg.")
    p_cc.add_argument("--masa-molar", type=parse_number, help="g/mol, necesaria si ΔH se da por kg.")
    p_cc.add_argument("--p-unidad", default="kPa", choices=["Pa", "kPa", "bar", "atm", "mmHg"])
    p_cc.add_argument("--t-unidad", default="K", choices=["K", "C"])

    p_sub = sub.add_parser("sublimacion", help="Clausius-Clapeyron integrada para sublimación.")
    add_sub_sig(p_sub)
    p_sub.add_argument("--p1", required=True, type=parse_number)
    p_sub.add_argument("--t1", required=True, type=parse_number)
    p_sub.add_argument("--t2", type=parse_number, help="Segunda temperatura. Con --dh calcula P2; con --p2 y sin --dh permite estimar ΔH_sub.")
    p_sub.add_argument("--p2", type=parse_number, help="Segunda presión. Con --dh calcula T2; con --t2 y sin --dh permite estimar ΔH_sub.")
    p_sub.add_argument("--dh", type=parse_number, help="Entalpía de sublimación.")
    p_sub.add_argument("--dh-unidad", default="kJ/mol")
    p_sub.add_argument("--masa-molar", type=parse_number)
    p_sub.add_argument("--p-unidad", default="kPa", choices=["Pa", "kPa", "bar", "atm", "mmHg"])
    p_sub.add_argument("--t-unidad", default="K", choices=["K", "C"])

    p_lk = sub.add_parser("lee-kesler", help="Presión de vapor mediante Lee-Kesler.")
    add_sub_sig(p_lk)
    p_lk.add_argument("--t", required=True, type=parse_number)
    p_lk.add_argument("--tc", required=True, type=parse_number)
    p_lk.add_argument("--pc", required=True, type=parse_number)
    p_lk.add_argument("--omega", required=True, type=parse_number)
    p_lk.add_argument("--t-unidad", default="K", choices=["K", "C"])
    p_lk.add_argument("--pc-unidad", default="bar", choices=["Pa", "kPa", "bar", "atm", "mmHg"])
    p_lk.add_argument("--salida-unidad", default="kPa", choices=["Pa", "kPa", "bar", "atm", "mmHg"])
    p_lk.add_argument("--permitir-extrapolacion", action="store_true")

    p_int = sub.add_parser("interpolar", help="Comparar interpolación P-T y ln(P)-1/T.")
    add_sub_sig(p_int)
    for arg in ("t1", "p1", "t2", "p2", "t"):
        p_int.add_argument(f"--{arg}", required=True, type=parse_number)
    p_int.add_argument("--t-unidad", default="K", choices=["K", "C"])
    p_int.add_argument("--p-unidad", default="kPa", choices=["Pa", "kPa", "bar", "atm", "mmHg"])
    p_int.add_argument("--permitir-extrapolacion", action="store_true")

    p_duh = sub.add_parser("duhring", help="Construir y usar una línea de Dühring.")
    add_sub_sig(p_duh)
    p_duh.add_argument(
        "--puntos",
        required=True,
        help='Pares "T,P;T,P;...". Ejemplo: "313,6.08;353,39.33". Use punto decimal aquí para evitar ambigüedad.',
    )
    p_duh.add_argument("--referencia", default="agua")
    p_duh.add_argument("--temperatura", type=parse_number, help="T_dis objetivo para estimar P_dis*.")
    p_duh.add_argument("--t-unidad", default="K", choices=["K", "C"])
    p_duh.add_argument("--p-unidad", default="kPa", choices=["Pa", "kPa", "bar", "atm", "mmHg"])
    p_duh.add_argument("--grafica", help="Archivo PNG de salida.")
    p_duh.add_argument("--permitir-extrapolacion", action="store_true")

    p_graph = sub.add_parser("grafica", help="Generar curvas de Antoine.")
    add_sub_sig(p_graph)
    p_graph.add_argument("--sustancias", required=True, help="Nombres separados por comas.")
    p_graph.add_argument("--tipo", default="semilog", choices=["pt", "semilog", "clausius"])
    p_graph.add_argument("--tmin", type=parse_number)
    p_graph.add_argument("--tmax", type=parse_number)
    p_graph.add_argument("--t-unidad", default="K", choices=["K", "C"])
    p_graph.add_argument("--salida", default="presion_vapor.png")
    p_graph.add_argument("--permitir-extrapolacion", action="store_true")

    p_list = sub.add_parser("listar", help="Mostrar la base interna de constantes de Antoine.")
    add_sub_sig(p_list)
    return parser


def run_cc_cli(args, sublimation: bool, sig: int) -> None:
    P1 = pressure_to_kpa(args.p1, args.p_unidad)
    T1 = temperature_to_k(args.t1, args.t_unidad)

    # Caso 1: P1, T1, T2 y ΔH -> P2
    if args.t2 is not None and args.p2 is None and args.dh is not None:
        T2 = temperature_to_k(args.t2, args.t_unidad)
        dh = enthalpy_to_j_per_mol(args.dh, args.dh_unidad, args.masa_molar)
        P2 = cc_pressure2(P1, T1, T2, dh)
        print_cc_hypotheses("sublimación" if sublimation else "vaporización")
        print(f"P2 = {format_sig(pressure_from_kpa(P2, args.p_unidad), sig)} {pressure_unit_label(args.p_unidad)}")
        return

    # Caso 2: P1, T1, P2 y ΔH -> T2
    if args.p2 is not None and args.t2 is None and args.dh is not None:
        P2 = pressure_to_kpa(args.p2, args.p_unidad)
        dh = enthalpy_to_j_per_mol(args.dh, args.dh_unidad, args.masa_molar)
        T2 = cc_temperature2(P1, T1, P2, dh)
        print_cc_hypotheses("sublimación" if sublimation else "vaporización")
        out = temperature_from_k(T2, args.t_unidad)
        label = "K" if args.t_unidad == "K" else "°C"
        print(f"T2 = {format_sig(out, sig)} {label}")
        return

    # Caso 3: P1, T1, P2 y T2, sin ΔH -> ΔH
    if args.p2 is not None and args.t2 is not None and args.dh is None:
        P2 = pressure_to_kpa(args.p2, args.p_unidad)
        T2 = temperature_to_k(args.t2, args.t_unidad)
        dh = cc_enthalpy(P1, T1, P2, T2)
        symbol = "ΔH_sub" if sublimation else "ΔH_vap"
        print_cc_hypotheses("sublimación" if sublimation else "vaporización")
        print(f"{symbol} = {format_sig(dh / 1000.0, sig)} kJ mol⁻¹")
        return

    if args.p2 is not None and args.t2 is not None and args.dh is not None:
        raise ValueError("Los datos están sobredeterminados. Para comprobar consistencia, use el menú de comparación o elimine uno de --p2, --t2 o --dh.")

    raise ValueError(
        "Combinaciones válidas: --t2 + --dh para calcular P2; --p2 + --dh para calcular T2; "
        "o --p2 + --t2 sin --dh para estimar la entalpía."
    )


def parse_duhring_points(raw: str, t_unit: str, p_unit: str) -> List[Tuple[float, float]]:
    points: List[Tuple[float, float]] = []
    chunks = [c.strip() for c in raw.split(";") if c.strip()]
    if len(chunks) < 2:
        raise ValueError("Se necesitan al menos dos pares T,P separados por punto y coma.")
    for chunk in chunks:
        parts = [p.strip() for p in chunk.split(",")]
        if len(parts) != 2:
            raise ValueError(
                f"No se reconoce el par {chunk!r}. En --puntos use punto decimal y coma solo entre T y P."
            )
        T = temperature_to_k(parse_number(parts[0]), t_unit)
        P = pressure_to_kpa(parse_number(parts[1]), p_unit)
        points.append((T, P))
    return points


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    sig = max(1, min(args.cifras, 12))

    if args.command is None:
        interactive_menu(sig)
        return 0

    try:
        if args.command == "listar":
            for data in ANTOINE.values():
                print(
                    f"{data.nombre:16s} A={data.A:<9g} B={data.B:<10g} C={data.C:<10g} "
                    f"rango={data.Tmin:g}-{data.Tmax:g} K"
                )
            return 0

        if args.command == "antoine":
            data = find_antoine(args.sustancia)
            if args.temperatura is not None:
                T = temperature_to_k(args.temperatura, args.t_unidad)
                check_antoine_range(T, data, args.permitir_extrapolacion)
                P = antoine_pressure_kpa(T, data)
                print(f"Sustancia: {data.nombre}")
                print(f"P* = {format_sig(pressure_from_kpa(P, args.p_unidad), sig)} {pressure_unit_label(args.p_unidad)}")
            else:
                P = pressure_to_kpa(args.presion, args.p_unidad)
                T = antoine_temperature_k(P, data)
                check_antoine_range(T, data, args.permitir_extrapolacion)
                out = temperature_from_k(T, args.t_unidad)
                label = "K" if args.t_unidad == "K" else "°C"
                print(f"Sustancia: {data.nombre}")
                print(f"T = {format_sig(out, sig)} {label}")
            return 0

        if args.command == "clausius":
            run_cc_cli(args, False, sig)
            return 0

        if args.command == "sublimacion":
            run_cc_cli(args, True, sig)
            return 0

        if args.command == "lee-kesler":
            T = temperature_to_k(args.t, args.t_unidad)
            Tc = temperature_to_k(args.tc, args.t_unidad)
            Pc = pressure_to_kpa(args.pc, args.pc_unidad)
            Tr, f0, f1, Pr, P = lee_kesler_pressure_kpa(
                T, Tc, Pc, args.omega, args.permitir_extrapolacion
            )
            print(f"Tr = {format_sig(Tr, sig)}")
            print(f"(ln Pr)^(0) = {format_sig(f0, sig)}")
            print(f"(ln Pr)^(1) = {format_sig(f1, sig)}")
            print(f"Pr = {format_sig(Pr, sig)}")
            print(
                f"P* = {format_sig(pressure_from_kpa(P, args.salida_unidad), sig)} "
                f"{pressure_unit_label(args.salida_unidad)}"
            )
            return 0

        if args.command == "interpolar":
            T1 = temperature_to_k(args.t1, args.t_unidad)
            T2 = temperature_to_k(args.t2, args.t_unidad)
            T = temperature_to_k(args.t, args.t_unidad)
            P1 = pressure_to_kpa(args.p1, args.p_unidad)
            P2 = pressure_to_kpa(args.p2, args.p_unidad)
            if not is_inside_interval(T, T1, T2) and not args.permitir_extrapolacion:
                raise ValueError("T queda fuera del intervalo [T1,T2]. Use --permitir-extrapolacion si procede.")
            if not is_inside_interval(T, T1, T2):
                print_warning("Se está extrapolando fuera del intervalo de los datos.")
            P_lin = linear_interpolation(T1, P1, T2, P2, T)
            P_cc = cc_interpolation(T1, P1, T2, P2, T)
            print(
                f"P* por interpolación lineal P-T = "
                f"{format_sig(pressure_from_kpa(P_lin, args.p_unidad), sig)} {pressure_unit_label(args.p_unidad)}"
            )
            print(
                f"P* por ln(P*) frente a 1/T      = "
                f"{format_sig(pressure_from_kpa(P_cc, args.p_unidad), sig)} {pressure_unit_label(args.p_unidad)}"
            )
            pct = 100.0 * abs(P_cc - P_lin) / P_cc
            print(f"Diferencia relativa = {format_sig(pct, sig)} %")
            return 0

        if args.command == "duhring":
            reference = find_antoine(args.referencia)
            points = parse_duhring_points(args.puntos, args.t_unidad, args.p_unidad)
            a, b, r2, Trefs = duhring_fit(points, reference, args.permitir_extrapolacion)
            print(f"T_dis = ({format_sig(a, sig)}) T_ref + ({format_sig(b, sig)})")
            if r2 is not None:
                print(f"R² = {format_sig(r2, max(sig, 4))}")
            else:
                print("R² no se usa como diagnóstico con solo dos puntos.")
            target_tuple = None
            if args.temperatura is not None:
                Ttarget = temperature_to_k(args.temperatura, args.t_unidad)
                if not is_inside_interval(Ttarget, min(p[0] for p in points), max(p[0] for p in points)):
                    if not args.permitir_extrapolacion:
                        raise ValueError(
                            "La temperatura objetivo está fuera del intervalo experimental de Dühring. "
                            "Use --permitir-extrapolacion si procede."
                        )
                    print_warning("Se extrapola la línea de Dühring fuera del intervalo experimental.")
                Tref, Ptarget = duhring_pressure_at_temperature(
                    Ttarget, a, b, reference, args.permitir_extrapolacion
                )
                print(f"T_ref equivalente = {format_sig(Tref, sig)} K")
                print(
                    f"P_dis* = {format_sig(pressure_from_kpa(Ptarget, args.p_unidad), sig)} "
                    f"{pressure_unit_label(args.p_unidad)}"
                )
                target_tuple = (Ttarget, Tref)
            if args.grafica:
                plot_duhring(points, Trefs, a, b, reference.nombre, target_tuple, args.grafica)
            return 0

        if args.command == "grafica":
            names = [x.strip() for x in args.sustancias.split(",") if x.strip()]
            substances = [find_antoine(n) for n in names]
            Tmin = temperature_to_k(args.tmin, args.t_unidad) if args.tmin is not None else None
            Tmax = temperature_to_k(args.tmax, args.t_unidad) if args.tmax is not None else None
            plot_antoine_curves(
                substances,
                args.tipo,
                Tmin,
                Tmax,
                args.salida,
                args.permitir_extrapolacion,
            )
            return 0

        parser.error("Comando no reconocido.")
        return 2

    except (ValueError, RuntimeError, OverflowError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
