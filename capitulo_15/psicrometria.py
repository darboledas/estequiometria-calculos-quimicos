#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Capítulo 15 — Aire húmedo y psicrometría
=========================================

Aplicación didáctica e interactiva para cálculos psicrométricos.

Finalidad
---------
- Caracterizar estados de aire húmedo a partir de dos propiedades independientes.
- Calcular propiedades psicrométricas, punto de rocío y temperatura de bulbo húmedo.
- Estudiar calentamiento/enfriamiento, condensación, humidificación y mezcla.
- Generar cartas psicrométricas calculadas numéricamente, sin usar una imagen de fondo.
- Localizar estados y representar procesos sobre la carta.
- Comparar varios estados y exportarlos a CSV.
- Resolver, en un modo separado, sistemas gas–vapor distintos del aire–agua.

Hipótesis y unidades
--------------------
- Aire húmedo tratado como mezcla ideal de aire seco y vapor de agua.
- Presión total en kPa; temperaturas en °C.
- Razón de humedad omega en kg H2O/kg de aire seco.
- Entalpía en kJ/kg de aire seco.
- Volumen específico en m³/kg de aire seco.
- Para aire–agua se usa la correlación de presión de vapor de saturación adoptada por
  ASHRAE (forma Hyland-Wexler), válida aquí entre -100 °C y 200 °C. El cambio
  entre las expresiones para hielo y agua líquida se realiza en el punto triple
  (0,01 °C), evitando la pequeña discontinuidad que aparecería al invertirlas en 0 °C.
- La temperatura de bulbo húmedo se obtiene con la relación psicrométrica de ASHRAE
  y, cuando es implícita, mediante bisección.
- Las expresiones de entalpía y volumen específico son las habituales para aire húmedo.

Control de cifras significativas
---------------------------------
Los datos de medida se leen primero como texto. Así se distingue, por ejemplo, entre
30, 30,0 y 30,00. Las constantes internas y los coeficientes de correlación no limitan
las cifras significativas. Los cálculos se realizan con precisión de coma flotante y el
redondeo se aplica solo al presentar los resultados.

Dependencias
------------
- Python 3.10 o posterior.
- matplotlib únicamente para los modos gráficos. El resto del programa funciona sin él.

Uso
---
    python psicrometria.py
    python psicrometria.py -h

El programa acepta punto o coma como separador decimal. No use separadores de miles.
"""

from __future__ import annotations

import argparse
import csv
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable, Optional, Sequence

# -----------------------------------------------------------------------------
# Constantes del modelo
# -----------------------------------------------------------------------------

EPSILON = 0.621945          # M_agua / M_aire_seco
R_DA = 0.287042             # kPa·m³/(kg·K), aire seco
CP_DA = 1.006               # kJ/(kg·K)
CP_V = 1.86                 # kJ/(kg·K)
H_FG_0 = 2501.0             # kJ/kg a 0 °C
P_STD = 101.325             # kPa; atmósfera estándar exacta por definición
T_MIN_CORR = -100.0         # °C
T_MAX_CORR = 200.0          # °C
TOL = 1e-10


# -----------------------------------------------------------------------------
# Excepciones
# -----------------------------------------------------------------------------

class PsychrometricError(ValueError):
    """Error de entrada, incompatibilidad física o fallo de resolución."""


# -----------------------------------------------------------------------------
# Lectura y control de cifras significativas
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class Measurement:
    value: float
    raw: str
    sigfigs: int
    decimals: Optional[int]
    exact: bool = False


def _normalise_numeric_text(text: str) -> str:
    s = text.strip().replace(" ", "")
    if not s:
        raise ValueError("entrada vacía")
    if s.count(",") and s.count("."):
        raise ValueError("use coma o punto decimal, pero no ambos")
    s = s.replace(",", ".")
    return s


def count_sigfigs(text: str) -> int:
    """Cuenta cifras significativas a partir de la representación escrita."""
    s = _normalise_numeric_text(text).lower()
    if "e" in s:
        mantissa, _ = s.split("e", 1)
    else:
        mantissa = s
    mantissa = mantissa.lstrip("+-")
    if not mantissa or mantissa == ".":
        raise ValueError("número no válido")

    if "." in mantissa:
        digits = mantissa.replace(".", "")
        significant = digits.lstrip("0")
        return len(significant) if significant else 1

    digits = mantissa.lstrip("0")
    if not digits:
        return 1
    digits = digits.rstrip("0")
    return len(digits) if digits else 1


def count_decimals(text: str) -> Optional[int]:
    s = _normalise_numeric_text(text).lower()
    if "e" in s:
        mantissa, exponent_text = s.split("e", 1)
        exponent = int(exponent_text)
    else:
        mantissa = s
        exponent = 0
    mantissa = mantissa.lstrip("+-")
    if "." not in mantissa:
        return max(0, -exponent) if exponent < 0 else 0
    n = len(mantissa.split(".", 1)[1]) - exponent
    return max(0, n)


def parse_measurement(text: str, *, exact: bool = False) -> Measurement:
    s = _normalise_numeric_text(text)
    try:
        value = float(s)
    except ValueError as exc:
        raise ValueError("número no válido") from exc
    if not math.isfinite(value):
        raise ValueError("el valor debe ser finito")
    return Measurement(
        value=value,
        raw=text.strip(),
        sigfigs=99 if exact else count_sigfigs(text),
        decimals=None if exact else count_decimals(text),
        exact=exact,
    )


def limiting_sigfigs(*items: Measurement, fallback: int = 5) -> int:
    vals = [x.sigfigs for x in items if x is not None and not x.exact]
    return min(vals) if vals else fallback


def fmt_sig(value: Optional[float], sigfigs: int, *, comma: bool = True) -> str:
    if value is None:
        return "—"
    if not math.isfinite(value):
        return "—"
    sigfigs = max(1, min(int(sigfigs), 12))
    if value == 0:
        s = "0" if sigfigs == 1 else "0." + "0" * (sigfigs - 1)
    else:
        order = math.floor(math.log10(abs(value)))
        decimals = sigfigs - 1 - order
        if order >= sigfigs or order <= -5:
            s = f"{value:.{sigfigs - 1}e}"
        elif decimals > 0:
            s = f"{value:.{decimals}f}"
        else:
            rounded = round(value, decimals)
            s = f"{rounded:.0f}"
            # Si los ceros finales harían ambigua la precisión, notación científica.
            body = s.lstrip("-")
            if body.endswith("0") and sigfigs > 1:
                s = f"{value:.{sigfigs - 1}e}"
    if comma:
        if "e" in s:
            mant, exp = s.split("e")
            s = mant.replace(".", ",") + "e" + exp
        else:
            s = s.replace(".", ",")
    return s


def ask_measurement(
    prompt: str,
    *,
    validator: Optional[Callable[[float], bool]] = None,
    error: str = "Valor no válido.",
) -> Measurement:
    while True:
        raw = input(prompt).strip()
        try:
            m = parse_measurement(raw)
            if validator is not None and not validator(m.value):
                raise ValueError(error)
            return m
        except (ValueError, OverflowError) as exc:
            print(f"  Error: {exc}")


def ask_int(prompt: str, low: int, high: int) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            n = int(raw)
            if low <= n <= high:
                return n
        except ValueError:
            pass
        print(f"  Introduzca un entero entre {low} y {high}.")


def ask_yes_no(prompt: str, default: bool = False) -> bool:
    suffix = " [S/n]: " if default else " [s/N]: "
    raw = input(prompt + suffix).strip().lower()
    if not raw:
        return default
    return raw in {"s", "si", "sí", "y", "yes"}


def ask_pressure() -> Measurement:
    while True:
        raw = input("Presión total P [kPa] (Enter = 101,325 kPa): ").strip()
        if not raw:
            return Measurement(P_STD, "101,325", 99, None, True)
        try:
            m = parse_measurement(raw)
            if m.value <= 0:
                raise ValueError("la presión debe ser positiva")
            return m
        except ValueError as exc:
            print(f"  Error: {exc}")


# -----------------------------------------------------------------------------
# Relaciones psicrométricas fundamentales
# -----------------------------------------------------------------------------

def saturation_pressure_water(T_c: float) -> float:
    """Presión de vapor de saturación del agua [kPa], ASHRAE/Hyland-Wexler."""
    if not (T_MIN_CORR <= T_c <= T_MAX_CORR):
        raise PsychrometricError(
            f"La correlación de presión de vapor se usa entre {T_MIN_CORR:g} y {T_MAX_CORR:g} °C."
        )
    T = T_c + 273.15
    if T_c <= 0.01:
        c1 = -5.6745359e3
        c2 = 6.3925247
        c3 = -9.677843e-3
        c4 = 6.2215701e-7
        c5 = 2.0747825e-9
        c6 = -9.484024e-13
        c7 = 4.1635019
        ln_p_pa = c1 / T + c2 + c3 * T + c4 * T**2 + c5 * T**3 + c6 * T**4 + c7 * math.log(T)
    else:
        c8 = -5.8002206e3
        c9 = 1.3914993
        c10 = -4.8640239e-2
        c11 = 4.1764768e-5
        c12 = -1.4452093e-8
        c13 = 6.5459673
        ln_p_pa = c8 / T + c9 + c10 * T + c11 * T**2 + c12 * T**3 + c13 * math.log(T)
    return math.exp(ln_p_pa) / 1000.0


def humidity_ratio_from_pw(pw: float, P: float) -> float:
    if pw < 0:
        raise PsychrometricError("La presión parcial de vapor no puede ser negativa.")
    if pw >= P:
        raise PsychrometricError("La presión parcial de vapor debe ser menor que la presión total.")
    return EPSILON * pw / (P - pw)


def pw_from_humidity_ratio(W: float, P: float) -> float:
    if W < 0:
        raise PsychrometricError("La razón de humedad no puede ser negativa.")
    return P * W / (EPSILON + W)


def saturation_humidity_ratio(T_c: float, P: float) -> float:
    pws = saturation_pressure_water(T_c)
    if pws >= P:
        raise PsychrometricError(
            "A esta temperatura la presión de saturación alcanza o supera la presión total; "
            "no existe una razón de humedad de saturación finita para este modelo."
        )
    return humidity_ratio_from_pw(pws, P)


def moist_air_enthalpy(T_c: float, W: float) -> float:
    return CP_DA * T_c + W * (H_FG_0 + CP_V * T_c)


def moist_air_specific_volume(T_c: float, W: float, P: float) -> float:
    T_k = T_c + 273.15
    if T_k <= 0:
        raise PsychrometricError("La temperatura absoluta debe ser positiva.")
    return R_DA * T_k * (1.0 + 1.607858 * W) / P


def bisection(
    f: Callable[[float], float],
    a: float,
    b: float,
    *,
    tol: float = 1e-8,
    max_iter: int = 250,
) -> float:
    tol = ITER_TOL if tol == 1e-8 else tol
    max_iter = ITER_MAX if max_iter == 250 else max_iter
    fa = f(a)
    fb = f(b)
    if not (math.isfinite(fa) and math.isfinite(fb)):
        raise PsychrometricError("La función no es finita en los extremos del intervalo de búsqueda.")
    if abs(fa) < tol:
        return a
    if abs(fb) < tol:
        return b
    if fa * fb > 0:
        raise PsychrometricError("La solución no está acotada por el intervalo de bisección.")
    lo, hi = a, b
    flo = fa
    for _ in range(max_iter):
        mid = 0.5 * (lo + hi)
        fm = f(mid)
        if abs(fm) < tol or abs(hi - lo) < tol:
            return mid
        if flo * fm <= 0:
            hi = mid
        else:
            lo = mid
            flo = fm
    return 0.5 * (lo + hi)


def temperature_from_saturation_pressure(p_target: float) -> float:
    if p_target <= 0:
        raise PsychrometricError("La presión de vapor debe ser positiva para obtener una temperatura de saturación finita.")
    p_lo = saturation_pressure_water(T_MIN_CORR)
    p_hi = saturation_pressure_water(T_MAX_CORR)
    if not (p_lo <= p_target <= p_hi):
        raise PsychrometricError(
            "La presión de vapor queda fuera del intervalo cubierto por la correlación de saturación."
        )
    f = lambda T: saturation_pressure_water(T) - p_target
    return bisection(f, T_MIN_CORR, T_MAX_CORR)


def humidity_ratio_from_tdb_twb(Tdb: float, Twb: float, P: float) -> float:
    if Twb > Tdb + 1e-10:
        raise PsychrometricError("La temperatura de bulbo húmedo no puede superar la de bulbo seco.")
    Ws_wb = saturation_humidity_ratio(Twb, P)
    if Twb >= 0.0:
        num = (2501.0 - 2.326 * Twb) * Ws_wb - 1.006 * (Tdb - Twb)
        den = 2501.0 + 1.86 * Tdb - 4.186 * Twb
    else:
        num = (2830.0 - 0.24 * Twb) * Ws_wb - 1.006 * (Tdb - Twb)
        den = 2830.0 + 1.86 * Tdb - 2.1 * Twb
    if abs(den) < 1e-14:
        raise PsychrometricError("La relación de bulbo húmedo queda singular para estos datos.")
    W = num / den
    return max(W, 0.0) if W > -1e-12 else W


def wet_bulb_temperature(Tdb: float, W: float, P: float) -> float:
    Ws_db = saturation_humidity_ratio(Tdb, P)
    if W > Ws_db * (1 + 2e-7):
        raise PsychrometricError("No puede calcularse T_bh para un estado sobresaturado monofásico.")
    if abs(W - Ws_db) <= max(1e-10, 2e-7 * max(Ws_db, 1e-12)):
        return Tdb

    # El límite inferior físico se toma en la correlación. Para W>0, el rocío
    # suele ofrecer una cota mejor; con aire idealmente seco no existe T_rocío finita.
    pw = pw_from_humidity_ratio(W, P)
    if pw > 0:
        try:
            lo = max(T_MIN_CORR, temperature_from_saturation_pressure(pw))
        except PsychrometricError:
            lo = T_MIN_CORR
    else:
        lo = T_MIN_CORR

    hi = Tdb
    f = lambda Twb: humidity_ratio_from_tdb_twb(Tdb, Twb, P) - W

    # Si la cota del rocío no cambia el signo por la formulación de bulbo húmedo,
    # se retrocede hasta el límite de la correlación.
    try:
        if f(lo) * f(hi) > 0:
            lo = T_MIN_CORR
    except PsychrometricError:
        lo = T_MIN_CORR
    return bisection(f, lo, hi)


# Configuración numérica de los métodos implícitos. Se conserva la precisión interna;
# las cifras significativas solo afectan a la presentación.
ITER_TOL = 1e-8
ITER_MAX = 250


def configure_iteration() -> None:
    """Permite especificar precisión y límite de iteraciones para bisección."""
    global ITER_TOL, ITER_MAX
    print("\nBisección: tolerancia absoluta en °C o residuo de la función.")
    print("Valor vigente:", f"{ITER_TOL:g}", "(tolerancia),", ITER_MAX, "iteraciones.")
    raw = input("Tolerancia deseada [°C] (Enter = conservar): ").strip()
    if raw:
        value = float(_normalise_numeric_text(raw))
        if not (1e-12 <= value <= 0.1):
            raise PsychrometricError("La tolerancia debe estar entre 1e-12 y 0,1 °C.")
        ITER_TOL = value
    raw = input("Máximo de iteraciones (Enter = conservar): ").strip()
    if raw:
        value = int(raw)
        if not (10 <= value <= 10000):
            raise PsychrometricError("Se admiten entre 10 y 10000 iteraciones.")
        ITER_MAX = value
    print(f"Configuración: tol={ITER_TOL:g}; máximo={ITER_MAX}.")


# -----------------------------------------------------------------------------
# Estado psicrométrico
# -----------------------------------------------------------------------------

@dataclass
class PsychState:
    P: float
    Tdb: float
    W: float
    pw: float
    rh: float
    Tdp: Optional[float]
    Twb: float
    h: float
    v: float
    Y: float
    x_v: float
    Ws: Optional[float]
    saturation_pct: Optional[float]
    sigfigs: int
    pressure_sigfigs: int
    source_pair: tuple[str, str]
    input_sigfigs: dict[str, int] = field(default_factory=dict)


def make_state(
    P: float,
    Tdb: float,
    W: float,
    *,
    sigfigs: int,
    source_pair: tuple[str, str],
    pressure_sigfigs: int = 6,
    input_sigfigs: Optional[dict[str, int]] = None,
) -> PsychState:
    if P <= 0:
        raise PsychrometricError("La presión total debe ser positiva.")
    if not (T_MIN_CORR <= Tdb <= T_MAX_CORR):
        raise PsychrometricError("La temperatura de bulbo seco queda fuera del intervalo de la correlación.")
    if W < -1e-12:
        raise PsychrometricError("La razón de humedad calculada es negativa.")
    W = max(0.0, W)
    pw = pw_from_humidity_ratio(W, P)
    pws = saturation_pressure_water(Tdb)
    rh = pw / pws
    if rh > 1.0 + 2e-8:
        raise PsychrometricError(
            "Los datos conducen a un estado sobresaturado. La hipótesis de una única fase gaseosa no es válida."
        )
    if rh < -2e-8:
        raise PsychrometricError("La humedad relativa calculada es negativa.")
    rh = min(max(rh, 0.0), 1.0)

    Tdp: Optional[float]
    if pw <= 0:
        Tdp = None
    else:
        Tdp = temperature_from_saturation_pressure(pw)
        if Tdp > Tdb + 2e-7:
            raise PsychrometricError("El punto de rocío calculado supera la temperatura de bulbo seco.")

    Twb = wet_bulb_temperature(Tdb, W, P)
    if Twb > Tdb + 1e-7:
        raise PsychrometricError("La temperatura de bulbo húmedo calculada supera la de bulbo seco.")
    if Tdp is not None and rh < 1.0 - 1e-8 and not (Tdp - 1e-6 <= Twb <= Tdb + 1e-6):
        raise PsychrometricError("El estado calculado no satisface el orden esperado T_rocío ≤ T_bh ≤ T_bs.")

    h = moist_air_enthalpy(Tdb, W)
    v = moist_air_specific_volume(Tdb, W, P)
    Y = W / EPSILON
    x_v = pw / P

    try:
        Ws = saturation_humidity_ratio(Tdb, P)
        saturation_pct = 100.0 * W / Ws if Ws > 0 else 0.0
    except PsychrometricError:
        Ws = None
        saturation_pct = None

    return PsychState(
        P=P,
        Tdb=Tdb,
        W=W,
        pw=pw,
        rh=rh,
        Tdp=Tdp,
        Twb=Twb,
        h=h,
        v=v,
        Y=Y,
        x_v=x_v,
        Ws=Ws,
        saturation_pct=saturation_pct,
        sigfigs=sigfigs,
        pressure_sigfigs=pressure_sigfigs,
        source_pair=source_pair,
        input_sigfigs=dict(input_sigfigs or {}),
    )


PAIR_OPTIONS = {
    1: ("Tdb", "RH", "T_bs y humedad relativa"),
    2: ("Tdb", "W", "T_bs y razón de humedad omega"),
    3: ("Tdb", "Twb", "T_bs y T_bh"),
    4: ("Tdb", "Tdp", "T_bs y T_rocío"),
    5: ("Tdb", "h", "T_bs y entalpía"),
    6: ("Tdb", "v", "T_bs y volumen específico"),
    7: ("RH", "W", "humedad relativa y omega"),
    8: ("RH", "Tdp", "humedad relativa y T_rocío"),
}


def print_pair_menu() -> None:
    print("\nPares de propiedades admitidos:")
    for n, (_, _, label) in PAIR_OPTIONS.items():
        print(f"  {n}. {label}")


def _ask_property(key: str) -> Measurement:
    if key == "Tdb":
        return ask_measurement("T_bs [°C]: ", validator=lambda x: T_MIN_CORR <= x <= T_MAX_CORR)
    if key == "Twb":
        return ask_measurement("T_bh [°C]: ", validator=lambda x: T_MIN_CORR <= x <= T_MAX_CORR)
    if key == "Tdp":
        return ask_measurement("T_rocío [°C]: ", validator=lambda x: T_MIN_CORR <= x <= T_MAX_CORR)
    if key == "RH":
        return ask_measurement("Humedad relativa phi [%]: ", validator=lambda x: 0 <= x <= 100)
    if key == "W":
        return ask_measurement("Razón de humedad omega [kg/kg aire seco]: ", validator=lambda x: x >= 0)
    if key == "h":
        return ask_measurement("Entalpía h [kJ/kg aire seco]: ")
    if key == "v":
        return ask_measurement("Volumen específico v [m³/kg aire seco]: ", validator=lambda x: x > 0)
    raise RuntimeError(f"Propiedad desconocida: {key}")


def state_from_pair(Pm: Measurement, key1: str, m1: Measurement, key2: str, m2: Measurement) -> PsychState:
    P = Pm.value
    values = {key1: m1.value, key2: m2.value}
    sig = limiting_sigfigs(Pm, m1, m2)
    pair = (key1, key2)
    state_kwargs = {
        "sigfigs": sig,
        "source_pair": pair,
        "pressure_sigfigs": 6 if Pm.exact else Pm.sigfigs,
        "input_sigfigs": {key1: m1.sigfigs, key2: m2.sigfigs},
    }

    if pair == ("Tdb", "RH"):
        Tdb = values["Tdb"]
        rh = values["RH"] / 100.0
        pw = rh * saturation_pressure_water(Tdb)
        W = humidity_ratio_from_pw(pw, P)
        return make_state(P, Tdb, W, **state_kwargs)

    if pair == ("Tdb", "W"):
        return make_state(P, values["Tdb"], values["W"], **state_kwargs)

    if pair == ("Tdb", "Twb"):
        Tdb, Twb = values["Tdb"], values["Twb"]
        if Twb > Tdb:
            raise PsychrometricError("T_bh no puede ser mayor que T_bs.")
        W = humidity_ratio_from_tdb_twb(Tdb, Twb, P)
        if W < 0:
            raise PsychrometricError("Los datos de T_bs y T_bh conducen a una razón de humedad negativa.")
        return make_state(P, Tdb, W, **state_kwargs)

    if pair == ("Tdb", "Tdp"):
        Tdb, Tdp = values["Tdb"], values["Tdp"]
        if Tdp > Tdb:
            raise PsychrometricError("T_rocío no puede ser mayor que T_bs.")
        pw = saturation_pressure_water(Tdp)
        W = humidity_ratio_from_pw(pw, P)
        return make_state(P, Tdb, W, **state_kwargs)

    if pair == ("Tdb", "h"):
        Tdb, h = values["Tdb"], values["h"]
        den = H_FG_0 + CP_V * Tdb
        W = (h - CP_DA * Tdb) / den
        return make_state(P, Tdb, W, **state_kwargs)

    if pair == ("Tdb", "v"):
        Tdb, v = values["Tdb"], values["v"]
        T_k = Tdb + 273.15
        W = ((v * P) / (R_DA * T_k) - 1.0) / 1.607858
        return make_state(P, Tdb, W, **state_kwargs)

    if pair == ("RH", "W"):
        rh = values["RH"] / 100.0
        W = values["W"]
        if rh <= 0:
            if W == 0:
                raise PsychrometricError("phi = 0 y omega = 0 no determinan una temperatura única.")
            raise PsychrometricError("phi = 0 es incompatible con omega > 0.")
        pw = pw_from_humidity_ratio(W, P)
        pws_target = pw / rh
        Tdb = temperature_from_saturation_pressure(pws_target)
        return make_state(P, Tdb, W, **state_kwargs)

    if pair == ("RH", "Tdp"):
        rh = values["RH"] / 100.0
        Tdp = values["Tdp"]
        if rh <= 0:
            raise PsychrometricError("phi = 0 no es compatible con un punto de rocío finito.")
        pw = saturation_pressure_water(Tdp)
        pws_target = pw / rh
        Tdb = temperature_from_saturation_pressure(pws_target)
        W = humidity_ratio_from_pw(pw, P)
        return make_state(P, Tdb, W, **state_kwargs)

    raise PsychrometricError("Par de propiedades no implementado.")


def ask_state(Pm: Optional[Measurement] = None) -> tuple[PsychState, Measurement]:
    if Pm is None:
        Pm = ask_pressure()
    while True:
        print_pair_menu()
        option = ask_int("Seleccione el par de entrada: ", 1, len(PAIR_OPTIONS))
        key1, key2, _ = PAIR_OPTIONS[option]
        m1 = _ask_property(key1)
        m2 = _ask_property(key2)
        try:
            state = state_from_pair(Pm, key1, m1, key2, m2)
            return state, Pm
        except PsychrometricError as exc:
            print(f"\n  Datos incompatibles: {exc}")
            print("  Vuelva a introducir el estado.\n")


def print_state(state: PsychState, title: str = "Estado calculado") -> None:
    s = state.sigfigs
    ps = state.input_sigfigs
    sf = lambda key: ps.get(key, s)
    print(f"\n{title}")
    print("-" * len(title))
    print(f"P                = {fmt_sig(state.P, state.pressure_sigfigs)} kPa")
    print(f"T_bs             = {fmt_sig(state.Tdb, sf('Tdb'))} °C")
    print(f"T_bh             = {fmt_sig(state.Twb, sf('Twb'))} °C")
    print(f"T_rocío          = {fmt_sig(state.Tdp, sf('Tdp'))} °C")
    print(f"phi              = {fmt_sig(100 * state.rh, sf('RH'))} %")
    print(f"p_H2O            = {fmt_sig(state.pw, s)} kPa")
    print(f"omega            = {fmt_sig(state.W, sf('W'))} kg/kg aire seco")
    print(f"omega            = {fmt_sig(1000 * state.W, sf('W'))} g/kg aire seco")
    print(f"Y                = {fmt_sig(state.Y, s)} mol H2O/mol aire seco")
    print(f"x_H2O            = {fmt_sig(state.x_v, s)}")
    print(f"h                = {fmt_sig(state.h, sf('h'))} kJ/kg aire seco")
    print(f"v                = {fmt_sig(state.v, sf('v'))} m³/kg aire seco")
    if state.Ws is not None:
        print(f"omega_s          = {fmt_sig(state.Ws, s)} kg/kg aire seco")
    if state.saturation_pct is not None:
        print(f"% saturación     = {fmt_sig(state.saturation_pct, s)} %")
    print(f"Propiedades derivadas: {s} cifra(s) significativa(s), limitadas por los datos de entrada.")
    if state.input_sigfigs:
        print("Los datos introducidos se conservan con la precisión con la que se escribieron.")


def explain_state_path(state: PsychState) -> None:
    a, b = state.source_pair
    print("\nSecuencia de cálculo usada:")
    if (a, b) == ("Tdb", "RH"):
        print("  1) P*_H2O(T_bs) → 2) p_H2O = phi·P*_H2O → 3) omega → 4) resto de propiedades.")
    elif (a, b) == ("Tdb", "W"):
        print("  1) p_H2O a partir de omega → 2) phi y T_rocío → 3) T_bh, h y v.")
    elif (a, b) == ("Tdb", "Twb"):
        print("  1) omega a partir de T_bs y T_bh → 2) p_H2O → 3) phi, T_rocío, h y v.")
    elif (a, b) == ("Tdb", "Tdp"):
        print("  1) p_H2O = P*_H2O(T_rocío) → 2) omega → 3) phi, T_bh, h y v.")
    elif (a, b) == ("Tdb", "h"):
        print("  1) omega a partir de la ecuación de entalpía → 2) p_H2O → 3) propiedades restantes.")
    elif (a, b) == ("Tdb", "v"):
        print("  1) omega a partir de la ecuación de volumen específico → 2) p_H2O → 3) propiedades restantes.")
    elif (a, b) == ("RH", "W"):
        print("  1) p_H2O a partir de omega → 2) P*_H2O = p_H2O/phi → 3) T_bs por bisección → 4) resto.")
    elif (a, b) == ("RH", "Tdp"):
        print("  1) p_H2O = P*_H2O(T_rocío) → 2) P*_H2O(T_bs)=p_H2O/phi → 3) T_bs por bisección → 4) resto.")


# -----------------------------------------------------------------------------
# Procesos
# -----------------------------------------------------------------------------

def state_at_T_constant_W(initial: PsychState, Tm: Measurement) -> PsychState:
    sig = min(initial.sigfigs, Tm.sigfigs)
    if initial.Tdp is not None and Tm.value < initial.Tdp - 1e-9:
        raise PsychrometricError(
            "La temperatura final queda por debajo del punto de rocío; debe considerarse condensación."
        )
    return make_state(initial.P, Tm.value, initial.W, sigfigs=sig, source_pair=("Tdb", "W"), pressure_sigfigs=initial.pressure_sigfigs, input_sigfigs={"Tdb": Tm.sigfigs})


def cooling_with_condensation(initial: PsychState, Tm: Measurement) -> tuple[PsychState, float, Optional[PsychState]]:
    sig = min(initial.sigfigs, Tm.sigfigs)
    T2 = Tm.value
    if T2 >= initial.Tdb:
        raise PsychrometricError("Este modo requiere una temperatura final inferior a la inicial.")

    if initial.Tdp is None or T2 >= initial.Tdp - 1e-10:
        final = make_state(initial.P, T2, initial.W, sigfigs=sig, source_pair=("Tdb", "W"), pressure_sigfigs=initial.pressure_sigfigs, input_sigfigs={"Tdb": Tm.sigfigs})
        return final, 0.0, None

    dew = make_state(initial.P, initial.Tdp, initial.W, sigfigs=sig, source_pair=("Tdb", "W"), pressure_sigfigs=initial.pressure_sigfigs)
    W2 = saturation_humidity_ratio(T2, initial.P)
    final = make_state(initial.P, T2, W2, sigfigs=sig, source_pair=("Tdb", "W"), pressure_sigfigs=initial.pressure_sigfigs, input_sigfigs={"Tdb": Tm.sigfigs})
    condensate = initial.W - W2
    if condensate < -1e-10:
        raise PsychrometricError("El balance de condensación produjo una cantidad negativa de condensado.")
    return final, max(0.0, condensate), dew


def isothermal_humidification(initial: PsychState, rhm: Measurement) -> tuple[PsychState, float]:
    rh2 = rhm.value / 100.0
    if not (0 <= rh2 <= 1):
        raise PsychrometricError("La humedad relativa final debe quedar entre 0 y 100 %.")
    pw2 = rh2 * saturation_pressure_water(initial.Tdb)
    W2 = humidity_ratio_from_pw(pw2, initial.P)
    if W2 < initial.W - 1e-10:
        raise PsychrometricError("La especificación corresponde a deshumidificación, no a humidificación.")
    sig = min(initial.sigfigs, rhm.sigfigs)
    final = make_state(initial.P, initial.Tdb, W2, sigfigs=sig, source_pair=("Tdb", "RH"), pressure_sigfigs=initial.pressure_sigfigs, input_sigfigs={"Tdb": initial.input_sigfigs.get("Tdb", initial.sigfigs), "RH": rhm.sigfigs})
    return final, W2 - initial.W


def adiabatic_humidification_to_rh(initial: PsychState, rhm: Measurement) -> tuple[PsychState, float]:
    rh2 = rhm.value / 100.0
    if not (0 < rh2 <= 1):
        raise PsychrometricError("La humedad relativa final debe ser mayor que 0 y no superar 100 %.")
    if rh2 <= initial.rh + 1e-10:
        raise PsychrometricError("La humedad relativa final debe superar la inicial en una humidificación adiabática.")
    h0 = initial.h

    def f(T: float) -> float:
        pw = rh2 * saturation_pressure_water(T)
        if pw >= initial.P:
            return 1e6
        W = humidity_ratio_from_pw(pw, initial.P)
        return moist_air_enthalpy(T, W) - h0

    lo = max(T_MIN_CORR, -80.0)
    hi = initial.Tdb
    # Acotar buscando desde la temperatura inicial hacia abajo.
    flo, fhi = f(lo), f(hi)
    if flo * fhi > 0:
        # barrido más fino para encontrar un cambio de signo
        prev_t, prev_f = lo, flo
        found = None
        for i in range(1, 401):
            t = lo + (hi - lo) * i / 400.0
            ft = f(t)
            if prev_f * ft <= 0:
                found = (prev_t, t)
                break
            prev_t, prev_f = t, ft
        if found is None:
            raise PsychrometricError("No se encontró un estado final adiabático compatible con la humedad relativa indicada.")
        lo, hi = found
    T2 = bisection(f, lo, hi)
    pw2 = rh2 * saturation_pressure_water(T2)
    W2 = humidity_ratio_from_pw(pw2, initial.P)
    if W2 < initial.W - 1e-8:
        raise PsychrometricError("La solución obtenida no corresponde a una humidificación.")
    sig = min(initial.sigfigs, rhm.sigfigs)
    final = make_state(initial.P, T2, W2, sigfigs=sig, source_pair=("Tdb", "RH"), pressure_sigfigs=initial.pressure_sigfigs, input_sigfigs={"RH": rhm.sigfigs})
    return final, W2 - initial.W


def mix_states(state1: PsychState, m1: Measurement, state2: PsychState, m2: Measurement) -> tuple[Optional[PsychState], float, float]:
    if abs(state1.P - state2.P) > max(1e-6, 1e-6 * state1.P):
        raise PsychrometricError("Las dos corrientes deben mezclarse a la misma presión total en este modelo.")
    if m1.value <= 0 or m2.value <= 0:
        raise PsychrometricError("Los caudales de aire seco deben ser positivos.")
    mt = m1.value + m2.value
    Wm = (m1.value * state1.W + m2.value * state2.W) / mt
    hm = (m1.value * state1.h + m2.value * state2.h) / mt
    Tm = (hm - H_FG_0 * Wm) / (CP_DA + CP_V * Wm)
    sig = min(state1.sigfigs, state2.sigfigs, m1.sigfigs, m2.sigfigs)
    try:
        mixed = make_state(state1.P, Tm, Wm, sigfigs=sig, source_pair=("Tdb", "W"), pressure_sigfigs=state1.pressure_sigfigs)
        return mixed, Wm, hm
    except PsychrometricError as exc:
        if "sobresaturado" in str(exc).lower():
            return None, Wm, hm
        raise


# -----------------------------------------------------------------------------
# Gráficos y carta psicrométrica
# -----------------------------------------------------------------------------

def require_matplotlib():
    try:
        import matplotlib.pyplot as plt  # type: ignore
    except ImportError as exc:
        raise PsychrometricError(
            "Este modo requiere matplotlib. Instálelo con: python -m pip install matplotlib"
        ) from exc
    return plt


def frange(start: float, stop: float, step: float) -> list[float]:
    if step <= 0:
        raise ValueError("step debe ser positivo")
    vals = []
    x = start
    while x <= stop + 1e-12:
        vals.append(x)
        x += step
    return vals


def valid_curve_xy(Ts: Iterable[float], Ws: Iterable[float], P: float, wmax: float) -> tuple[list[float], list[float]]:
    xs, ys = [], []
    for T, W in zip(Ts, Ws):
        try:
            Wsat = saturation_humidity_ratio(T, P)
        except PsychrometricError:
            continue
        if 0 <= W <= Wsat * (1 + 1e-8) and W <= wmax * 1.02:
            xs.append(T)
            ys.append(W)
    return xs, ys


def plot_chart_base(
    ax,
    P: float,
    tmin: float,
    tmax: float,
    wmax: float,
    *,
    families: set[str],
    rh_step: float = 10.0,
    twb_step: float = 5.0,
    h_step: float = 10.0,
    v_step: float = 0.05,
    tdp_step: float = 5.0,
) -> None:
    Ts = frange(tmin, tmax, max(0.15, (tmax - tmin) / 500.0 if tmax > tmin else 0.15))

    # Saturación
    sat_x, sat_y = [], []
    for T in Ts:
        try:
            W = saturation_humidity_ratio(T, P)
        except PsychrometricError:
            continue
        if W <= wmax * 1.05:
            sat_x.append(T)
            sat_y.append(W)
    if sat_x:
        ax.plot(sat_x, sat_y, linewidth=2.0, label="Saturación, φ = 100 %")

    if "rh" in families:
        rh_values = frange(rh_step, 100.0 - rh_step, rh_step) if rh_step < 100 else []
        for rh_pct in rh_values:
            r = rh_pct / 100.0
            ys = []
            for T in Ts:
                pws = saturation_pressure_water(T)
                pw = r * pws
                if pw >= P:
                    ys.append(float("nan"))
                else:
                    ys.append(humidity_ratio_from_pw(pw, P))
            x, y = valid_curve_xy(Ts, ys, P, wmax)
            if len(x) > 1:
                ax.plot(x, y, linewidth=0.8, alpha=0.75)
                # Etiqueta cerca de una abscisa común; así las distintas HR quedan
                # separadas verticalmente en lugar de acumularse en el borde superior.
                target_t = tmin + 0.62 * (tmax - tmin)
                idx = min(range(len(x)), key=lambda i: abs(x[i] - target_t))
                while idx > 0 and y[idx] > 0.92 * wmax:
                    idx -= 1
                ax.text(x[idx], y[idx], f" {rh_pct:g}%", fontsize=7, va="center")

    if "twb" in families:
        start = math.ceil(tmin / twb_step) * twb_step
        for Twb in frange(start, tmax, twb_step):
            x, y = [], []
            for Tdb in Ts:
                if Tdb < Twb:
                    continue
                try:
                    W = humidity_ratio_from_tdb_twb(Tdb, Twb, P)
                    Wsat = saturation_humidity_ratio(Tdb, P)
                except PsychrometricError:
                    continue
                if 0 <= W <= min(Wsat * 1.000001, wmax * 1.02):
                    x.append(Tdb)
                    y.append(W)
            if len(x) > 1:
                ax.plot(x, y, linewidth=0.65, alpha=0.45, linestyle="--")

    if "h" in families:
        # Intervalo de h estimado a partir del rectángulo visible.
        h_min = moist_air_enthalpy(tmin, 0.0)
        h_max = moist_air_enthalpy(tmax, wmax)
        first = math.ceil(h_min / h_step) * h_step
        for hval in frange(first, h_max, h_step):
            ys = [(hval - CP_DA * T) / (H_FG_0 + CP_V * T) for T in Ts]
            x, y = valid_curve_xy(Ts, ys, P, wmax)
            if len(x) > 1:
                ax.plot(x, y, linewidth=0.6, alpha=0.35, linestyle=":")

    if "tdp" in families:
        start = math.ceil(tmin / tdp_step) * tdp_step
        for Tdp in frange(start, tmax, tdp_step):
            try:
                Wdp = saturation_humidity_ratio(Tdp, P)
            except PsychrometricError:
                continue
            if 0 <= Wdp <= wmax:
                x0 = max(tmin, Tdp)
                ax.plot([x0, tmax], [Wdp, Wdp], linewidth=0.55, alpha=0.28)
                ax.text(min(tmax, x0 + 0.5), Wdp, f" Tr={Tdp:g}°C", fontsize=6.5, va="bottom", ha="left")

    if "v" in families:
        # Intervalo visible aproximado.
        v_candidates = [
            moist_air_specific_volume(tmin, 0.0, P),
            moist_air_specific_volume(tmax, 0.0, P),
            moist_air_specific_volume(tmin, wmax, P),
            moist_air_specific_volume(tmax, wmax, P),
        ]
        vmin, vmax = min(v_candidates), max(v_candidates)
        first = math.ceil(vmin / v_step) * v_step
        for vval in frange(first, vmax, v_step):
            ys = [((vval * P) / (R_DA * (T + 273.15)) - 1.0) / 1.607858 for T in Ts]
            x, y = valid_curve_xy(Ts, ys, P, wmax)
            if len(x) > 1:
                ax.plot(x, y, linewidth=0.6, alpha=0.30, linestyle="-.")

    ax.set_xlim(tmin, tmax)
    ax.set_ylim(0, wmax)
    ax.set_xlabel("Temperatura de bulbo seco, T_bs [°C]")
    ax.set_ylabel("Razón de humedad, ω [kg H₂O/kg aire seco]")
    ax.set_title(f"Carta psicrométrica calculada — P = {str(P).replace('.', ',')} kPa")
    # Leyenda de familias: las líneas reales conservan estilos distintos para impresión.
    if "rh" in families:
        ax.plot([], [], linewidth=0.8, label="Humedad relativa")
    if "twb" in families:
        ax.plot([], [], linewidth=0.65, linestyle="--", label="T_bh")
    if "h" in families:
        ax.plot([], [], linewidth=0.6, linestyle=":", label="Entalpía")
    if "v" in families:
        ax.plot([], [], linewidth=0.6, linestyle="-.", label="Volumen específico")
    if "tdp" in families:
        ax.plot([], [], linewidth=0.55, label="T_rocío")
    ax.legend(loc="upper left", fontsize=7, frameon=True)
    ax.grid(True, linewidth=0.4, alpha=0.30)


def ask_chart_config(P: float) -> dict:
    print("\nConfiguración de la carta (Enter conserva el valor por defecto).")

    def opt_float(prompt: str, default: float, validator: Callable[[float], bool]) -> float:
        while True:
            raw = input(f"{prompt} [{str(default).replace('.', ',')}]: ").strip()
            if not raw:
                return default
            try:
                x = float(_normalise_numeric_text(raw))
                if not validator(x):
                    raise ValueError
                return x
            except ValueError:
                print("  Valor no válido.")

    tmin = opt_float("T mínima [°C]", 0.0, lambda x: T_MIN_CORR <= x < T_MAX_CORR)
    tmax = opt_float("T máxima [°C]", 50.0, lambda x: tmin < x <= T_MAX_CORR)
    wmax = opt_float("omega máxima [kg/kg]", 0.030, lambda x: x > 0)
    width = opt_float("Anchura de figura [in]", 11.0, lambda x: x > 2)
    height = opt_float("Altura de figura [in]", 7.0, lambda x: x > 2)

    print("Familias de líneas: 1=HR, 2=T_bh, 3=h, 4=v, 5=T_rocío, 6=todas")
    fam_choice = ask_int("Selección: ", 1, 6)
    fam_map = {
        1: {"rh"}, 2: {"twb"}, 3: {"h"}, 4: {"v"}, 5: {"tdp"},
        6: {"rh", "twb", "h", "v", "tdp"},
    }
    families = fam_map[fam_choice]

    rh_step = opt_float("Separación HR [%]", 10.0, lambda x: 0 < x <= 100)
    twb_step = opt_float("Separación T_bh [°C]", 5.0, lambda x: x > 0)
    h_step = opt_float("Separación h [kJ/kg]", 10.0, lambda x: x > 0)
    v_step = opt_float("Separación v [m³/kg]", 0.05, lambda x: x > 0)
    tdp_step = opt_float("Separación T_rocío [°C]", 5.0, lambda x: x > 0)

    return {
        "P": P,
        "tmin": tmin,
        "tmax": tmax,
        "wmax": wmax,
        "figsize": (width, height),
        "families": families,
        "rh_step": rh_step,
        "twb_step": twb_step,
        "h_step": h_step,
        "v_step": v_step,
        "tdp_step": tdp_step,
    }


def save_or_show_figure(fig, default_stem: str) -> None:
    print("\nSalida gráfica: 1=mostrar, 2=PNG 400 ppp, 3=PDF, 4=SVG")
    option = ask_int("Seleccione: ", 1, 4)
    if option == 1:
        try:
            import matplotlib.pyplot as plt  # type: ignore
            plt.show()
        except Exception:
            pass
        return
    ext = {2: ".png", 3: ".pdf", 4: ".svg"}[option]
    raw = input(f"Nombre de archivo (Enter = {default_stem}{ext}): ").strip()
    path = Path(raw) if raw else Path(default_stem + ext)
    if path.suffix.lower() != ext:
        path = path.with_suffix(ext)
    kwargs = {"bbox_inches": "tight"}
    if ext == ".png":
        kwargs["dpi"] = 400
    fig.savefig(path, **kwargs)
    print(f"Figura guardada en: {path.resolve()}")


def plot_exact_property_line(ax, state: PsychState, key: str, tmin: float, tmax: float, wmax: float) -> None:
    Ts = frange(tmin, tmax, max(0.15, (tmax - tmin) / 500.0))
    P = state.P
    if key == "Tdb":
        ax.plot([state.Tdb, state.Tdb], [0, min(state.W, wmax)], linewidth=1.4)
    elif key in {"W", "Tdp"}:
        x0 = max(tmin, state.Tdp if state.Tdp is not None else tmin)
        ax.plot([x0, min(tmax, state.Tdb)], [state.W, state.W], linewidth=1.4)
    elif key == "RH":
        ys = []
        for T in Ts:
            pw = state.rh * saturation_pressure_water(T)
            ys.append(humidity_ratio_from_pw(pw, P) if pw < P else float("nan"))
        x, y = valid_curve_xy(Ts, ys, P, wmax)
        if x:
            ax.plot(x, y, linewidth=1.4)
    elif key == "Twb":
        x, y = [], []
        for T in Ts:
            if T < state.Twb:
                continue
            try:
                W = humidity_ratio_from_tdb_twb(T, state.Twb, P)
                Ws = saturation_humidity_ratio(T, P)
            except PsychrometricError:
                continue
            if 0 <= W <= min(Ws, wmax):
                x.append(T); y.append(W)
        if x:
            ax.plot(x, y, linewidth=1.4)
    elif key == "h":
        ys = [(state.h - CP_DA * T) / (H_FG_0 + CP_V * T) for T in Ts]
        x, y = valid_curve_xy(Ts, ys, P, wmax)
        if x:
            ax.plot(x, y, linewidth=1.4)
    elif key == "v":
        ys = [((state.v * P) / (R_DA * (T + 273.15)) - 1.0) / 1.607858 for T in Ts]
        x, y = valid_curve_xy(Ts, ys, P, wmax)
        if x:
            ax.plot(x, y, linewidth=1.4)


def plot_state_on_chart(state: PsychState) -> None:
    plt = require_matplotlib()
    cfg = ask_chart_config(state.P)
    fig, ax = plt.subplots(figsize=cfg.pop("figsize"))
    plot_chart_base(ax, **cfg)
    for key in state.source_pair:
        plot_exact_property_line(ax, state, key, cfg["tmin"], cfg["tmax"], cfg["wmax"])
    ax.scatter([state.Tdb], [state.W], s=48, zorder=6)
    label = f"Estado\nT={fmt_sig(state.Tdb, state.sigfigs)} °C\nω={fmt_sig(state.W, state.sigfigs)}"
    ax.annotate(label, (state.Tdb, state.W), xytext=(8, 8), textcoords="offset points", fontsize=8)
    save_or_show_figure(fig, "estado_psicrometrico")


def plot_mixing_chart(s1: PsychState, s2: PsychState, mix: PsychState) -> None:
    """Representa los dos estados de entrada, el segmento de mezcla y el estado M."""
    plt = require_matplotlib()
    cfg = ask_chart_config(s1.P)
    fig, ax = plt.subplots(figsize=cfg.pop("figsize"))
    plot_chart_base(ax, **cfg)
    ax.plot([s1.Tdb, s2.Tdb], [s1.W, s2.W], linewidth=1.6)
    ax.scatter([s1.Tdb, s2.Tdb, mix.Tdb], [s1.W, s2.W, mix.W], s=46, zorder=6)
    for st, lab in [(s1, "1"), (s2, "2"), (mix, "M")]:
        ax.annotate(lab, (st.Tdb, st.W), xytext=(6, 6), textcoords="offset points")
    save_or_show_figure(fig, "mezcla_psicrometrica")


def plot_process_states(states: Sequence[PsychState], labels: Sequence[str], *, condensation: bool = False) -> None:
    plt = require_matplotlib()
    P = states[0].P
    cfg = ask_chart_config(P)
    fig, ax = plt.subplots(figsize=cfg.pop("figsize"))
    plot_chart_base(ax, **cfg)

    xs, ys = [], []
    if condensation and len(states) == 3:
        s1, dew, s2 = states
        xs.extend([s1.Tdb, dew.Tdb])
        ys.extend([s1.W, dew.W])
        if dew.Tdb != s2.Tdb:
            step = -max(0.1, abs(dew.Tdb - s2.Tdb) / 100)
            Tvals = frange(s2.Tdb, dew.Tdb, abs(step))
            Tvals = list(reversed(Tvals))
            if not Tvals or abs(Tvals[0] - dew.Tdb) > 1e-8:
                Tvals.insert(0, dew.Tdb)
            for T in Tvals[1:]:
                try:
                    W = saturation_humidity_ratio(T, P)
                except PsychrometricError:
                    continue
                xs.append(T); ys.append(W)
    else:
        xs = [s.Tdb for s in states]
        ys = [s.W for s in states]

    ax.plot(xs, ys, linewidth=1.8, marker="o")
    for s, lab in zip(states, labels):
        ax.annotate(lab, (s.Tdb, s.W), xytext=(6, 6), textcoords="offset points")
    if len(xs) >= 2:
        ax.annotate("", xy=(xs[-1], ys[-1]), xytext=(xs[-2], ys[-2]), arrowprops={"arrowstyle": "->"})
    save_or_show_figure(fig, "proceso_psicrometrico")


# -----------------------------------------------------------------------------
# Modos de la aplicación
# -----------------------------------------------------------------------------

def mode_1_characterize() -> None:
    state, _ = ask_state()
    print_state(state)
    if ask_yes_no("¿Mostrar la secuencia de cálculo?", default=True):
        explain_state_path(state)


def mode_2_direct_property() -> None:
    state, _ = ask_state()
    props = [
        ("T_bs", state.Tdb, "°C"),
        ("T_bh", state.Twb, "°C"),
        ("T_rocío", state.Tdp, "°C"),
        ("phi", 100 * state.rh, "%"),
        ("p_H2O", state.pw, "kPa"),
        ("omega", state.W, "kg/kg aire seco"),
        ("Y", state.Y, "mol/mol aire seco"),
        ("h", state.h, "kJ/kg aire seco"),
        ("v", state.v, "m³/kg aire seco"),
    ]
    print("\nPropiedad que desea mostrar:")
    for i, (name, _, unit) in enumerate(props, 1):
        print(f"  {i}. {name} [{unit}]")
    n = ask_int("Seleccione: ", 1, len(props))
    name, val, unit = props[n - 1]
    print(f"\n{name} = {fmt_sig(val, state.sigfigs)} {unit}")


def mode_3_dew_point() -> None:
    print("\nPunto de rocío a partir de:")
    print("  1. T_bs y humedad relativa")
    print("  2. omega y presión total")
    print("  3. presión parcial de H2O")
    option = ask_int("Seleccione: ", 1, 3)
    Pm = ask_pressure()
    if option == 1:
        Tm = _ask_property("Tdb")
        rhm = _ask_property("RH")
        state = state_from_pair(Pm, "Tdb", Tm, "RH", rhm)
        sig = state.sigfigs
        tdp = state.Tdp
    elif option == 2:
        Wm = _ask_property("W")
        pw = pw_from_humidity_ratio(Wm.value, Pm.value)
        sig = limiting_sigfigs(Pm, Wm)
        tdp = None if pw <= 0 else temperature_from_saturation_pressure(pw)
    else:
        pwm = ask_measurement("p_H2O [kPa]: ", validator=lambda x: 0 <= x < Pm.value)
        sig = limiting_sigfigs(Pm, pwm)
        tdp = None if pwm.value <= 0 else temperature_from_saturation_pressure(pwm.value)
    if tdp is None:
        print("\nPara p_H2O = 0 no existe un punto de rocío finito dentro del modelo.")
    else:
        print(f"\nT_rocío = {fmt_sig(tdp, sig)} °C")


def mode_4_constant_W() -> None:
    print("\nEstado inicial")
    initial, _ = ask_state()
    Tm = _ask_property("Tdb")
    try:
        final = state_at_T_constant_W(initial, Tm)
    except PsychrometricError as exc:
        print(f"\nNo puede mantenerse omega constante hasta esa temperatura: {exc}")
        return
    print_state(initial, "Estado inicial")
    print_state(final, "Estado final")
    delta_h = final.h - initial.h
    sig = min(initial.sigfigs, final.sigfigs)
    print(f"\nΔh = {fmt_sig(delta_h, sig)} kJ/kg aire seco")


def mode_5_condensation() -> None:
    print("\nEstado inicial")
    initial, _ = ask_state()
    Tm = _ask_property("Tdb")
    try:
        final, condensate, dew = cooling_with_condensation(initial, Tm)
    except PsychrometricError as exc:
        print(f"\nError: {exc}")
        return
    print_state(initial, "Estado inicial")
    if dew is not None:
        print_state(dew, "Estado en el punto de rocío")
    print_state(final, "Estado final")
    sig = min(initial.sigfigs, Tm.sigfigs)
    print(f"\nAgua condensada = {fmt_sig(condensate, sig)} kg H2O/kg aire seco")
    print(f"                  {fmt_sig(1000 * condensate, sig)} g H2O/kg aire seco")
    if condensate == 0:
        print("No se alcanza el punto de rocío: el proceso permanece monofásico.")


def mode_6_humidification() -> None:
    print("\nHumidificación:")
    print("  1. A T_bs constante")
    print("  2. Adiabática, h ≈ constante")
    option = ask_int("Seleccione: ", 1, 2)
    print("\nEstado inicial")
    initial, _ = ask_state()
    rhm = _ask_property("RH")
    try:
        if option == 1:
            final, added = isothermal_humidification(initial, rhm)
        else:
            final, added = adiabatic_humidification_to_rh(initial, rhm)
    except PsychrometricError as exc:
        print(f"\nError: {exc}")
        return
    print_state(initial, "Estado inicial")
    print_state(final, "Estado final")
    sig = min(initial.sigfigs, rhm.sigfigs)
    print(f"\nAgua incorporada al gas = {fmt_sig(added, sig)} kg H2O/kg aire seco")
    print(f"                         {fmt_sig(1000 * added, sig)} g H2O/kg aire seco")


def mode_7_mixing() -> None:
    Pm = ask_pressure()
    print("\nCorriente 1")
    s1, _ = ask_state(Pm)
    m1 = ask_measurement("Caudal de aire seco 1 [kg/s, kg/h, ...]: ", validator=lambda x: x > 0)
    print("\nCorriente 2")
    s2, _ = ask_state(Pm)
    m2 = ask_measurement("Caudal de aire seco 2 [misma unidad]: ", validator=lambda x: x > 0)
    try:
        mix, Wm, hm = mix_states(s1, m1, s2, m2)
    except PsychrometricError as exc:
        print(f"\nError: {exc}")
        return
    print_state(s1, "Corriente 1")
    print_state(s2, "Corriente 2")
    if mix is None:
        sig = min(s1.sigfigs, s2.sigfigs, m1.sigfigs, m2.sigfigs)
        print("\nLa mezcla calculada no puede permanecer completamente en fase gaseosa.")
        print("Debe considerarse condensación de agua.")
        print(f"Composición global antes de condensar: omega = {fmt_sig(Wm, sig)} kg/kg aire seco")
        print(f"Entalpía global antes de condensar: h = {fmt_sig(hm, sig)} kJ/kg aire seco")
        return
    print_state(mix, "Mezcla")
    if ask_yes_no("¿Representar los tres estados sobre una carta?", default=False):
        plot_mixing_chart(s1, s2, mix)


def mode_8_chart() -> None:
    plt = require_matplotlib()
    Pm = ask_pressure()
    cfg = ask_chart_config(Pm.value)
    fig, ax = plt.subplots(figsize=cfg.pop("figsize"))
    plot_chart_base(ax, **cfg)
    save_or_show_figure(fig, "carta_psicrometrica")


def mode_9_locate() -> None:
    state, _ = ask_state()
    print_state(state)
    plot_state_on_chart(state)


def mode_10_process_chart() -> None:
    print("\nProceso a representar:")
    print("  1. Calentamiento/enfriamiento a omega constante")
    print("  2. Enfriamiento con condensación")
    print("  3. Humidificación a T_bs constante")
    print("  4. Humidificación adiabática")
    option = ask_int("Seleccione: ", 1, 4)
    print("\nEstado inicial")
    initial, _ = ask_state()

    try:
        if option == 1:
            Tm = _ask_property("Tdb")
            final = state_at_T_constant_W(initial, Tm)
            plot_process_states([initial, final], ["1", "2"])
        elif option == 2:
            Tm = _ask_property("Tdb")
            final, _, dew = cooling_with_condensation(initial, Tm)
            if dew is None:
                plot_process_states([initial, final], ["1", "2"])
            else:
                plot_process_states([initial, dew, final], ["1", "D", "2"], condensation=True)
        elif option == 3:
            rhm = _ask_property("RH")
            final, _ = isothermal_humidification(initial, rhm)
            plot_process_states([initial, final], ["1", "2"])
        else:
            rhm = _ask_property("RH")
            final, _ = adiabatic_humidification_to_rh(initial, rhm)
            plot_process_states([initial, final], ["1", "2"])
    except PsychrometricError as exc:
        print(f"\nError: {exc}")


def state_row(state: PsychState, label: str) -> list[str]:
    s = state.sigfigs
    return [
        label,
        fmt_sig(state.Tdb, s),
        fmt_sig(state.Twb, s),
        fmt_sig(state.Tdp, s),
        fmt_sig(100 * state.rh, s),
        fmt_sig(state.W, s),
        fmt_sig(state.h, s),
        fmt_sig(state.v, s),
    ]


def mode_11_compare() -> None:
    Pm = ask_pressure()
    n = ask_int("Número de estados a comparar [2-10]: ", 2, 10)
    states = []
    for i in range(1, n + 1):
        print(f"\nEstado {i}")
        s, _ = ask_state(Pm)
        states.append(s)

    headers = ["Estado", "T_bs [°C]", "T_bh [°C]", "T_rocío [°C]", "phi [%]", "omega [kg/kg]", "h [kJ/kg]", "v [m³/kg]"]
    rows = [state_row(s, str(i)) for i, s in enumerate(states, 1)]
    widths = [max(len(headers[j]), *(len(r[j]) for r in rows)) for j in range(len(headers))]
    print("\n" + " | ".join(headers[j].ljust(widths[j]) for j in range(len(headers))))
    print("-+-".join("-" * w for w in widths))
    for r in rows:
        print(" | ".join(r[j].ljust(widths[j]) for j in range(len(headers))))

    if ask_yes_no("¿Exportar la tabla a CSV?", default=False):
        raw = input("Nombre de archivo (Enter = estados_psicrometricos.csv): ").strip()
        path = Path(raw or "estados_psicrometricos.csv")
        if path.suffix.lower() != ".csv":
            path = path.with_suffix(".csv")
        with path.open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(headers)
            writer.writerows(rows)
        print(f"CSV guardado en: {path.resolve()}")

    if ask_yes_no("¿Representar los estados en una misma carta?", default=False):
        plt = require_matplotlib()
        cfg = ask_chart_config(Pm.value)
        fig, ax = plt.subplots(figsize=cfg.pop("figsize"))
        plot_chart_base(ax, **cfg)
        for i, s in enumerate(states, 1):
            ax.scatter([s.Tdb], [s.W], s=42, zorder=6)
            ax.annotate(str(i), (s.Tdb, s.W), xytext=(5, 5), textcoords="offset points")
        save_or_show_figure(fig, "comparacion_estados")


def antoine_psat_kpa(T_c: float, A: float, B: float, C: float) -> float:
    """log10(P_sat/kPa) = A - B/(T[°C] + C); coeficientes para estas unidades."""
    den = T_c + C
    if abs(den) < 1e-14:
        raise PsychrometricError("La correlación de Antoine es singular a esta temperatura.")
    return 10.0 ** (A - B / den)


def mode_12_general_gas_vapor() -> None:
    print("\nSistema gas–vapor general (separado del modelo aire–agua).")
    Mg = ask_measurement("Masa molar del gas no condensable [g/mol]: ", validator=lambda x: x > 0)
    Mv = ask_measurement("Masa molar del vapor [g/mol]: ", validator=lambda x: x > 0)
    Pm = ask_pressure()
    Tm = ask_measurement("Temperatura [°C]: ")

    print("\nPresión de vapor de saturación:")
    print("  1. Introducir P*_v a la temperatura actual")
    print("  2. Usar Antoine: log10(P*_v/kPa) = A - B/(T[°C] + C)")
    ps_opt = ask_int("Seleccione: ", 1, 2)
    A = B = C = None
    if ps_opt == 1:
        psm = ask_measurement("P*_v [kPa]: ", validator=lambda x: 0 < x < Pm.value)
        psat = psm.value
        corr_sig = psm
    else:
        # Los coeficientes son parámetros del modelo; no limitan por sí mismos la precisión experimental.
        A = float(_normalise_numeric_text(input("A: ")))
        B = float(_normalise_numeric_text(input("B: ")))
        C = float(_normalise_numeric_text(input("C: ")))
        psat = antoine_psat_kpa(Tm.value, A, B, C)
        if not (0 < psat < Pm.value):
            raise PsychrometricError("La correlación produce una presión de saturación no compatible con la presión total.")
        corr_sig = Measurement(psat, "correlación", 99, None, True)

    print("\nDato de composición:")
    print("  1. Humedad relativa phi [%]")
    print("  2. Razón de humedad omega [kg vapor/kg gas seco]")
    print("  3. Razón molar Y [mol vapor/mol gas seco]")
    print("  4. Presión parcial del vapor p_v [kPa]")
    opt = ask_int("Seleccione: ", 1, 4)

    ratio = Mv.value / Mg.value
    if opt == 1:
        dm = ask_measurement("phi [%]: ", validator=lambda x: 0 <= x <= 100)
        pv = (dm.value / 100.0) * psat
    elif opt == 2:
        dm = ask_measurement("omega [kg/kg gas seco]: ", validator=lambda x: x >= 0)
        Y = dm.value / ratio
        pv = Pm.value * Y / (1 + Y)
    elif opt == 3:
        dm = ask_measurement("Y [mol/mol gas seco]: ", validator=lambda x: x >= 0)
        Y = dm.value
        pv = Pm.value * Y / (1 + Y)
    else:
        dm = ask_measurement("p_v [kPa]: ", validator=lambda x: 0 <= x < Pm.value)
        pv = dm.value

    if pv > psat * (1 + 1e-9):
        raise PsychrometricError("Los datos describen un vapor sobresaturado a la temperatura indicada.")

    Y = pv / (Pm.value - pv) if pv < Pm.value else math.inf
    omega = ratio * Y
    phi = pv / psat
    Ys = psat / (Pm.value - psat)
    omegas = ratio * Ys
    pct_sat = 100.0 * Y / Ys if Ys > 0 else 0.0
    sig = limiting_sigfigs(Mg, Mv, Pm, Tm, corr_sig, dm)

    print("\nResultados")
    print("----------")
    print(f"p_v              = {fmt_sig(pv, sig)} kPa")
    print(f"phi              = {fmt_sig(100 * phi, sig)} %")
    print(f"Y                = {fmt_sig(Y, sig)} mol/mol gas seco")
    print(f"omega            = {fmt_sig(omega, sig)} kg/kg gas seco")
    print(f"Y_s              = {fmt_sig(Ys, sig)} mol/mol gas seco")
    print(f"omega_s          = {fmt_sig(omegas, sig)} kg/kg gas seco")
    print(f"% saturación     = {fmt_sig(pct_sat, sig)} %")

    if ps_opt == 2 and pv > 0 and A is not None and B is not None and C is not None:
        denom = A - math.log10(pv)
        if abs(denom) > 1e-14:
            Tsat = B / denom - C
            print(f"T de saturación  = {fmt_sig(Tsat, sig)} °C")


def mode_check_results() -> None:
    print("\nComprobación de resultados del alumno")
    state, _ = ask_state()
    print_state(state, "Estado de referencia calculado")
    print("\nPuede comprobar: 1=omega, 2=T_rocío, 3=T_bh, 4=phi, 5=h, 6=v, 7=terminar")
    while True:
        opt = ask_int("Propiedad: ", 1, 7)
        if opt == 7:
            break
        mapping = {
            1: ("omega", state.W, "kg/kg aire seco"),
            2: ("T_rocío", state.Tdp, "°C"),
            3: ("T_bh", state.Twb, "°C"),
            4: ("phi", 100 * state.rh, "%"),
            5: ("h", state.h, "kJ/kg aire seco"),
            6: ("v", state.v, "m³/kg aire seco"),
        }
        name, ref, unit = mapping[opt]
        if ref is None:
            print(f"  {name}: no tiene valor finito en este estado.")
            continue
        userm = ask_measurement(f"Su valor de {name} [{unit}]: ")
        # Tolerancia de comparación basada en el redondeo esperado a las cifras limitantes.
        sig = min(state.sigfigs, userm.sigfigs)
        scale = max(abs(ref), abs(userm.value), 1e-12)
        tol_rel = 0.5 * 10 ** (1 - sig)
        diff = userm.value - ref
        ok = abs(diff) <= tol_rel * scale + 1e-12
        if ok:
            print(f"  Compatible con el estado calculado ({sig} c.s.).")
        else:
            print(f"  Discrepancia. Valor calculado: {fmt_sig(ref, sig)} {unit}; diferencia: {fmt_sig(diff, sig)} {unit}.")


def mode_14_didactic_figures() -> None:
    """Genera las familias de diagramas de las Figuras 15.12-15.15 y 15.17."""
    plt = require_matplotlib()
    Pm = ask_pressure()
    print("\nFiguras didácticas de construcción progresiva:")
    print("  1. Curva de saturación (como Figura 15.12)")
    print("  2. Curvas de humedad relativa (Figura 15.13)")
    print("  3. Líneas de bulbo húmedo (Figura 15.14)")
    print("  4. Volumen específico (Figura 15.15)")
    print("  5. Carta completa (Figura 15.16)")
    print("  6. Carta con ejemplos de recorridos (Figura 15.17)")
    opt = ask_int("Seleccione: ", 1, 6)
    families = {
        1: set(), 2: {"rh"}, 3: {"rh", "twb"},
        4: {"rh", "twb", "v"}, 5: {"rh", "twb", "h", "v", "tdp"},
        6: {"rh", "twb", "h", "v"},
    }[opt]
    cfg = dict(P=Pm.value, tmin=0, tmax=50, wmax=0.045, families=families)
    fig, ax = plt.subplots(figsize=(12, 7.5))
    plot_chart_base(ax, **cfg)
    if opt == 6:
        # Trayectorias ilustrativas; se calculan los estados sobre la carta.
        def state(T, RH):
            pw = RH / 100 * saturation_pressure_water(T)
            return make_state(Pm.value, T, humidity_ratio_from_pw(pw, Pm.value),
                              sigfigs=3, source_pair=("Tdb", "RH"))
        s = state(25, 50)
        s_hot = state_at_T_constant_W(s, Measurement(35, "35", 2, 0))
        ax.plot([s.Tdb, s_hot.Tdb], [s.W, s_hot.W], "-o", lw=1.8, label="Calentamiento")
        ax.annotate("Calentamiento", (30, s.W), xytext=(0, 7), textcoords="offset points", fontsize=8)
        s_cold, _, dew = cooling_with_condensation(s, Measurement(10, "10", 2, 0))
        if dew:
            xs = [s.Tdb, dew.Tdb] + list(reversed(frange(10, dew.Tdb, .25)))
            ys = [s.W, s.W] + [saturation_humidity_ratio(t, Pm.value) for t in xs[2:]]
            ax.plot(xs, ys, lw=1.8, label="Enfriamiento con condensación")
        else:
            ax.plot([s.Tdb, s_cold.Tdb], [s.W, s_cold.W], lw=1.8)
        s_hum, _ = isothermal_humidification(s, Measurement(80, "80", 2, 0))
        ax.plot([s.Tdb, s_hum.Tdb], [s.W, s_hum.W], "-o", lw=1.8, label="Humidificación isoterma")
        try:
            s_ad, _ = adiabatic_humidification_to_rh(s, Measurement(90, "90", 2, 0))
            ax.plot([s.Tdb, s_ad.Tdb], [s.W, s_ad.W], "-o", lw=1.8, label="Humidificación adiabática (h≈cte.)")
        except PsychrometricError:
            pass
        ax.legend(fontsize=8, loc="upper left")
    save_or_show_figure(fig, f"figura_didactica_15_{opt}")


def self_test() -> None:
    """Pruebas de regresión calculadas, sin redondear resultados intermedios."""
    assert abs(saturation_pressure_water(30) - 4.246) < .015
    st = make_state(101.325, 30, humidity_ratio_from_pw(.5 * saturation_pressure_water(30), 101.325),
                    sigfigs=3, source_pair=("Tdb", "RH"))
    assert abs(st.pw - 2.123) < .02
    assert abs(st.W - .0133) < .0001
    assert abs(st.v - .877) < .01
    assert abs(st.h - 64.2) < .7
    assert 18 < st.Tdp < 19
    assert st.Tdp < st.Twb < st.Tdb
    cold, cond, dew = cooling_with_condensation(st, Measurement(10, "10", 2, 0))
    assert cond > 0 and dew is not None and abs(cold.rh - 1) < 1e-6
    warm = state_at_T_constant_W(st, Measurement(35, "35", 2, 0))
    assert abs(warm.W - st.W) < 1e-12 and warm.rh < st.rh
    humid, added = isothermal_humidification(st, Measurement(70, "70", 2, 0))
    assert added > 0 and humid.W > st.W
    ad, added_ad = adiabatic_humidification_to_rh(st, Measurement(80, "80", 2, 0))
    assert added_ad > 0 and ad.Tdb < st.Tdb and abs(ad.h - st.h) < 1e-5
    mix, wm, hm = mix_states(st, Measurement(100, "100", 3, 0), warm, Measurement(200, "200", 3, 0))
    assert mix is not None and abs(mix.W - st.W) < 1e-10
    assert abs(antoine_psat_kpa(30, 1, 1, 100) - 10 ** (1 - 1 / 130)) < 1e-12
    assert count_sigfigs("30,00") == 4 and count_sigfigs("0,00120") == 3
    print("Validación correcta: 12 grupos de comprobaciones físicas, numéricas y de precisión.")


# -----------------------------------------------------------------------------
# Menú principal y CLI
# -----------------------------------------------------------------------------

MODES = {
    1: ("Caracterización completa de un estado", mode_1_characterize),
    2: ("Cálculo directo de una propiedad", mode_2_direct_property),
    3: ("Punto de rocío y comienzo de la condensación", mode_3_dew_point),
    4: ("Calentamiento/enfriamiento a omega constante", mode_4_constant_W),
    5: ("Enfriamiento con condensación", mode_5_condensation),
    6: ("Humidificación", mode_6_humidification),
    7: ("Mezcla de dos corrientes de aire húmedo", mode_7_mixing),
    8: ("Generación de una carta psicrométrica", mode_8_chart),
    9: ("Localización de un estado sobre la carta", mode_9_locate),
    10: ("Representación de procesos sobre la carta", mode_10_process_chart),
    11: ("Comparación de varios estados", mode_11_compare),
    12: ("Sistemas gas–vapor distintos del aire–agua", mode_12_general_gas_vapor),
    13: ("Comprobar mis resultados", mode_check_results),
    14: ("Figuras didácticas y construcción de la carta", mode_14_didactic_figures),
    15: ("Configurar precisión de cálculo iterativo", configure_iteration),
}


def print_main_menu() -> None:
    print("\n" + "=" * 72)
    print("PSICROMETRÍA — CAPÍTULO 15")
    print("=" * 72)
    for n, (label, _) in MODES.items():
        print(f" {n:2d}. {label}")
    print("  0. Salir")


def build_parser() -> argparse.ArgumentParser:
    description = (
        "Aplicación didáctica para aire húmedo y psicrometría. "
        "Calcula estados, procesos, mezclas y cartas psicrométricas con control de cifras significativas."
    )
    epilog = """
Modos interactivos:
   1 caracterización completa; 2 propiedad directa; 3 punto de rocío;
   4 calentamiento/enfriamiento a omega constante; 5 condensación;
   6 humidificación; 7 mezcla; 8 generar carta; 9 localizar estado;
  10 representar procesos; 11 comparar estados; 12 gas-vapor general;
  13 comprobar resultados del alumno; 14 figuras didácticas por etapas;
   15 tolerancia y máximo de iteraciones.

Propiedades de entrada admitidas para un estado aire–agua:
  T_bs + phi, T_bs + omega, T_bs + T_bh, T_bs + T_rocío,
  T_bs + h, T_bs + v, phi + omega, phi + T_rocío.

Unidades:
  P en kPa; T en °C; omega en kg H2O/kg aire seco;
  h en kJ/kg aire seco; v en m³/kg aire seco; phi en %.

Modelo:
  Mezcla ideal aire seco–vapor de agua. Presión de saturación ASHRAE/Hyland-Wexler
  entre -100 y 200 °C. En los modos gráficos, matplotlib es obligatorio.

Gráficos:
  PNG a 400 ppp, PDF y SVG vectoriales. La carta se calcula numéricamente y puede
  incluir saturación, humedad relativa, T_bh, T_rocío, entalpía y volumen específico.

Cifras significativas:
  Los datos se leen como texto; 30, 30,0 y 30,00 no tienen la misma precisión.
  El redondeo se aplica solo a la salida. Punto y coma decimal están admitidos.
"""
    return argparse.ArgumentParser(
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )


def main() -> int:
    parser = build_parser()
    parser.add_argument("--validar", action="store_true", help="Ejecuta pruebas internas numéricas y físicas y sale")
    args = parser.parse_args()
    if args.validar:
        self_test()
        return 0

    while True:
        print_main_menu()
        option = ask_int("Seleccione una opción: ", 0, max(MODES))
        if option == 0:
            print("Fin del programa.")
            return 0
        label, func = MODES[option]
        print(f"\n>>> {label}")
        try:
            func()
        except PsychrometricError as exc:
            print(f"\nError físico o numérico: {exc}")
        except KeyboardInterrupt:
            print("\nOperación cancelada por el usuario.")
        except EOFError:
            print("\nFin de la entrada.")
            return 0

        if not ask_yes_no("\n¿Volver al menú principal?", default=True):
            print("Fin del programa.")
            return 0


if __name__ == "__main__":
    sys.exit(main())
