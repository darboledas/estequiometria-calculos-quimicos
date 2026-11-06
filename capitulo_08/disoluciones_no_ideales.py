#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
capitulo8.py
============

Herramienta docente para el capítulo 8: disoluciones no ideales y
coeficientes de actividad.

Incluye:
- Actividad, g^E y potencial químico de exceso.
- Margules de un parámetro.
- Margules de dos parámetros (tres sufijos).
- Van Laar.
- Wilson.
- Ley de Raoult modificada.
- Formulación gamma-phi con correcciones constantes.
- Presión de burbuja y de rocío.
- Temperatura de burbuja y de rocío.
- Azeótropos binarios.
- Vaporización flash binaria.
- Diagramas gamma-x, g^E/RT-x, y-x, P-x-y y T-x-y.
- Ajuste de Margules de dos parámetros y Van Laar a datos ELV.
- Control explícito de convergencia.
- Redondeo final atendiendo a las cifras significativas de los datos.

Dependencias:
    Python >= 3.9
    numpy
    matplotlib

Uso:
    python capitulo8.py
    python capitulo8.py --help

Criterio de precisión:
    Los cálculos internos se realizan sin redondeos intermedios deliberados.
    El redondeo se aplica al presentar el resultado final. Las cifras
    significativas se deducen de las cadenas introducidas por el usuario.
    Para ceros finales significativos, use decimal o notación científica:
        330      -> se interpreta con 2 cifras significativas
        330.     -> 3 cifras significativas
        3.30e2   -> 3 cifras significativas

Nota:
    El capítulo presenta NRTL y UNIQUAC de forma introductoria, sin desarrollar
    sus ecuaciones completas. Por ese motivo este programa no inventa una
    implementación de dichos modelos. Sí permite usar coeficientes de actividad
    introducidos directamente para cálculos de ELV.
"""

from __future__ import annotations

import argparse
import csv
import math
import os
import sys
from dataclasses import dataclass
from typing import Callable, Iterable, List, Optional, Sequence, Tuple

try:
    import numpy as np
except ImportError as exc:
    raise SystemExit("Falta numpy. Instale con: pip install numpy matplotlib") from exc

R = 8.31446261815324  # J mol^-1 K^-1; constante física, no limita las cifras significativas.


# ---------------------------------------------------------------------------
# Precisión y formato
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Measured:
    value: float
    raw: str
    sigfigs: int
    lsd_order: int  # orden decimal del último dígito significativo: 10^lsd_order


def normalize_number_text(text: str) -> str:
    s = text.strip().replace(" ", "").replace(",", ".")
    if not s:
        raise ValueError("Entrada vacía.")
    return s


def infer_sigfigs(text: str) -> Tuple[float, int, int]:
    """Devuelve valor, número de cifras significativas y orden del LSD.

    Ejemplos:
      0,250 -> 0.25, 3, -3
      95,0  -> 95.0, 3, -1
      330   -> 330.0, 2, 1
      330.  -> 330.0, 3, 0
      3.30e2 -> 330.0, 3, 0
    """
    s = normalize_number_text(text)
    try:
        value = float(s)
    except ValueError as exc:
        raise ValueError(f"No es un número válido: {text!r}") from exc
    if not math.isfinite(value):
        raise ValueError("El número debe ser finito.")

    mantissa, exp_part = (s.lower().split("e", 1) + [None])[:2]
    exp10 = int(exp_part) if exp_part is not None else 0
    signless = mantissa.lstrip("+-")

    if "." in signless:
        left, right = signless.split(".", 1)
        digits = left + right
        nz = next((i for i, c in enumerate(digits) if c != "0"), None)
        if nz is None:
            sig = max(1, len(right))
        else:
            sig = len(digits) - nz
        decimals = len(right)
        lsd = exp10 - decimals
    else:
        digits = signless
        stripped_left = digits.lstrip("0")
        if not stripped_left:
            sig = 1
            lsd = exp10
        else:
            trailing = len(stripped_left) - len(stripped_left.rstrip("0"))
            sig = len(stripped_left) - trailing
            sig = max(1, sig)
            lsd = exp10 + trailing
    return value, sig, lsd


def measured(text: str) -> Measured:
    v, sf, lsd = infer_sigfigs(text)
    return Measured(v, text, sf, lsd)


def sf_for_values(values: Iterable[Measured], default: int = 4) -> int:
    vals = [v.sigfigs for v in values if v is not None]
    return min(vals) if vals else default


def round_sig(x: float, sig: int) -> float:
    if x == 0 or not math.isfinite(x):
        return x
    return round(x, sig - 1 - int(math.floor(math.log10(abs(x)))))


def format_sig(x: float, sig: int, decimal_comma: bool = True) -> str:
    if not math.isfinite(x):
        return str(x)
    if x == 0:
        out = "0"
    else:
        ax = abs(x)
        exponent = int(math.floor(math.log10(ax)))
        if exponent >= sig or exponent <= -4:
            out = f"{x:.{sig-1}e}"
        else:
            decimals = max(0, sig - exponent - 1)
            out = f"{x:.{decimals}f}"
    if decimal_comma:
        out = out.replace(".", ",")
    return out


def lsd_from_value_sig(x: float, sig: int) -> int:
    if x == 0:
        return 0
    return int(math.floor(math.log10(abs(x)))) - sig + 1


def format_sum_of_products(total: float, terms: Sequence[Tuple[float, int]]) -> Tuple[str, str]:
    """Aplica: producto/división -> cifras significativas; suma -> posición decimal."""
    if not terms:
        return format_sig(total, 4), "4 cifras significativas (criterio por defecto)"
    lsd_orders = [lsd_from_value_sig(v, sf) for v, sf in terms if v != 0]
    if not lsd_orders:
        return "0", "resultado nulo"
    final_lsd = max(lsd_orders)
    decimals = max(0, -final_lsd)
    rounded = round(total, decimals) if final_lsd <= 0 else round(total, -final_lsd)
    if final_lsd <= 0:
        out = f"{rounded:.{decimals}f}"
    else:
        out = f"{rounded:.0f}"
    out = out.replace(".", ",")
    criterion = f"regla de suma: última posición significativa = 10^{final_lsd}"
    return out, criterion


def show_result(label: str, value: float, sig: int, unit: str = "", criterion: str = "") -> None:
    raw = f"{value:.12g}".replace(".", ",")
    final = format_sig(value, sig)
    print(f"\n{label}")
    print(f"  Valor interno: {raw}{(' ' + unit) if unit else ''}")
    print(f"  Resultado final: {final}{(' ' + unit) if unit else ''}")
    print(f"  Cifras significativas: {sig}")
    if criterion:
        print(f"  Criterio: {criterion}")


# ---------------------------------------------------------------------------
# Entrada segura
# ---------------------------------------------------------------------------

def input_measured(prompt: str, *, positive: bool = False,
                   min_value: Optional[float] = None,
                   max_value: Optional[float] = None) -> Measured:
    while True:
        try:
            raw = input(prompt)
            m = measured(raw)
            nr = normalize_number_text(raw)
            mant = nr.lower().split("e", 1)[0].lstrip("+-")
            if "e" not in nr.lower() and "." not in mant and len(mant) > 1 and mant.endswith("0") and any(c != "0" for c in mant):
                print("  Aviso: los ceros finales de un entero son ambiguos.")
                print(f"  Se interpreta {raw.strip()} con {m.sigfigs} cifras significativas.")
                print("  Escriba un punto decimal o notación científica si desea declarar esos ceros como significativos.")
            if positive and m.value <= 0:
                raise ValueError("Debe ser mayor que cero.")
            if min_value is not None and m.value < min_value:
                raise ValueError(f"Debe ser >= {min_value}.")
            if max_value is not None and m.value > max_value:
                raise ValueError(f"Debe ser <= {max_value}.")
            return m
        except ValueError as exc:
            print(f"  Error: {exc}")


def input_float(prompt: str, *, positive: bool = False,
                min_value: Optional[float] = None,
                max_value: Optional[float] = None,
                default: Optional[float] = None) -> float:
    while True:
        raw = input(prompt)
        if default is not None and raw.strip() == "":
            return default
        try:
            v = float(normalize_number_text(raw))
            if not math.isfinite(v):
                raise ValueError("Debe ser finito.")
            if positive and v <= 0:
                raise ValueError("Debe ser mayor que cero.")
            if min_value is not None and v < min_value:
                raise ValueError(f"Debe ser >= {min_value}.")
            if max_value is not None and v > max_value:
                raise ValueError(f"Debe ser <= {max_value}.")
            return v
        except ValueError as exc:
            print(f"  Error: {exc}")


def input_int(prompt: str, *, min_value: Optional[int] = None,
              default: Optional[int] = None) -> int:
    while True:
        raw = input(prompt)
        if default is not None and raw.strip() == "":
            return default
        try:
            v = int(raw)
            if min_value is not None and v < min_value:
                raise ValueError(f"Debe ser >= {min_value}.")
            return v
        except ValueError as exc:
            print(f"  Error: {exc}")


def ask_tolerance(kind: str = "composición", default: float = 1e-8) -> Tuple[float, int]:
    print("\nTolerancia de convergencia.")
    print("No determina las cifras significativas del resultado; solo controla la iteración.")
    tol = input_float(f"Tolerancia absoluta para {kind} [{default:g}]: ",
                      positive=True, default=default)
    maxiter = input_int("Número máximo de iteraciones [200]: ", min_value=1, default=200)
    return tol, maxiter


def ask_yes_no(prompt: str, default: bool = True) -> bool:
    suffix = " [S/n]: " if default else " [s/N]: "
    raw = input(prompt + suffix).strip().lower()
    if not raw:
        return default
    return raw in {"s", "si", "sí", "y", "yes"}


# ---------------------------------------------------------------------------
# Modelos de actividad
# ---------------------------------------------------------------------------

class ActivityModel:
    name = "Modelo"

    def gammas(self, x: Sequence[float], T: Optional[float] = None) -> np.ndarray:
        raise NotImplementedError


@dataclass
class Ideal(ActivityModel):
    name = "Ideal"
    def gammas(self, x, T=None):
        return np.ones(len(x), dtype=float)


@dataclass
class ConstantGamma(ActivityModel):
    gamma: Sequence[float]
    name = "γ introducidos"

    def gammas(self, x, T=None):
        g = np.asarray(self.gamma, dtype=float)
        if np.any(g <= 0):
            raise ValueError("Todos los coeficientes de actividad deben ser positivos.")
        return g


@dataclass
class Margules1(ActivityModel):
    A: float
    name = "Margules de un parámetro"

    def gammas(self, x, T=None):
        x1 = float(x[0]); x2 = 1.0 - x1
        return np.array([math.exp(self.A*x2*x2), math.exp(self.A*x1*x1)])


@dataclass
class Margules2(ActivityModel):
    A12: float
    A21: float
    name = "Margules de dos parámetros"

    def gammas(self, x, T=None):
        x1 = float(x[0]); x2 = 1.0 - x1
        ln1 = x2*x2 * (self.A12 + 2.0*(self.A21-self.A12)*x1)
        ln2 = x1*x1 * (self.A21 + 2.0*(self.A12-self.A21)*x2)
        return np.exp([ln1, ln2])


@dataclass
class VanLaar(ActivityModel):
    A12: float
    A21: float
    name = "Van Laar"

    def gammas(self, x, T=None):
        x1 = float(x[0]); x2 = 1.0 - x1
        den = self.A12*x1 + self.A21*x2
        if abs(den) < 1e-15:
            raise ValueError("Denominador nulo o casi nulo en Van Laar.")
        ln1 = self.A12 * (self.A21*x2/den)**2
        ln2 = self.A21 * (self.A12*x1/den)**2
        return np.exp([ln1, ln2])


@dataclass
class Wilson(ActivityModel):
    L12: float
    L21: float
    name = "Wilson"

    def gammas(self, x, T=None):
        if self.L12 <= 0 or self.L21 <= 0:
            raise ValueError("Los parámetros Λ12 y Λ21 de Wilson deben ser positivos.")
        x1 = float(x[0]); x2 = 1.0 - x1
        d1 = x1 + self.L12*x2
        d2 = x2 + self.L21*x1
        if d1 <= 0 or d2 <= 0:
            raise ValueError("Argumento logarítmico no positivo en Wilson.")
        common = self.L12/d1 - self.L21/d2
        ln1 = -math.log(d1) + x2*common
        ln2 = -math.log(d2) - x1*common
        return np.exp([ln1, ln2])


def activity_properties(x: Sequence[float], model: ActivityModel, T: Optional[float] = None):
    x = np.asarray(x, dtype=float)
    if np.any(x < 0) or np.any(x > 1) or abs(float(np.sum(x))-1.0) > 1e-9:
        raise ValueError("Las fracciones molares deben estar entre 0 y 1 y sumar 1.")
    g = model.gammas(x, T)
    if np.any(g <= 0) or not np.all(np.isfinite(g)):
        raise ValueError("Coeficientes de actividad no físicos.")
    a = x*g
    ge_rt = float(np.dot(x, np.log(g)))
    return g, a, ge_rt


# ---------------------------------------------------------------------------
# Presión de vapor
# ---------------------------------------------------------------------------

class VaporPressure:
    unit = "kPa"
    def psat(self, T: float) -> np.ndarray:
        raise NotImplementedError


@dataclass
class DirectPsat(VaporPressure):
    values: Sequence[float]
    unit: str = "kPa"
    def psat(self, T: float = 298.15):
        p = np.asarray(self.values, dtype=float)
        if np.any(p <= 0):
            raise ValueError("Las presiones de vapor deben ser positivas.")
        return p


@dataclass
class SimpleExpPsat(VaporPressure):
    """Correlación del cap. 8: ln(P_i*/unidad)=A_i-B_i/T."""
    A: Sequence[float]
    B: Sequence[float]
    unit: str = "kPa"
    Tmin: Optional[float] = None
    Tmax: Optional[float] = None

    def psat(self, T: float):
        if T <= 0:
            raise ValueError("La temperatura absoluta debe ser positiva.")
        if self.Tmin is not None and T < self.Tmin:
            raise ValueError("Temperatura por debajo del intervalo de validez declarado.")
        if self.Tmax is not None and T > self.Tmax:
            raise ValueError("Temperatura por encima del intervalo de validez declarado.")
        return np.exp(np.asarray(self.A, dtype=float) - np.asarray(self.B, dtype=float)/T)


@dataclass
class AntoinePsat(VaporPressure):
    """log10(P*) = A - B/(T + C). T puede introducirse en K o °C."""
    A: Sequence[float]
    B: Sequence[float]
    C: Sequence[float]
    T_scale: str = "C"
    unit: str = "kPa"
    Tmin: Optional[float] = None
    Tmax: Optional[float] = None

    def psat(self, T: float):
        Tin = T - 273.15 if self.T_scale.upper() == "C" else T
        if self.Tmin is not None and Tin < self.Tmin:
            raise ValueError("Temperatura por debajo del intervalo de validez declarado.")
        if self.Tmax is not None and Tin > self.Tmax:
            raise ValueError("Temperatura por encima del intervalo de validez declarado.")
        A, B, C = map(lambda z: np.asarray(z, dtype=float), (self.A, self.B, self.C))
        den = Tin + C
        if np.any(abs(den) < 1e-14):
            raise ValueError("Singularidad en la ecuación de Antoine.")
        return 10.0**(A - B/den)


# ---------------------------------------------------------------------------
# Métodos numéricos
# ---------------------------------------------------------------------------

def bisection(f: Callable[[float], float], a: float, b: float,
              tol: float, maxiter: int = 200) -> Tuple[float, int, float]:
    fa, fb = f(a), f(b)
    if not (math.isfinite(fa) and math.isfinite(fb)):
        raise ValueError("La función no es finita en los extremos del intervalo.")
    if fa == 0:
        return a, 0, fa
    if fb == 0:
        return b, 0, fb
    if fa*fb > 0:
        raise ValueError("El intervalo no encierra un cambio de signo.")
    c = (a+b)/2
    fc = f(c)
    for it in range(1, maxiter+1):
        c = 0.5*(a+b)
        fc = f(c)
        if not math.isfinite(fc):
            raise ValueError("La función dejó de ser finita durante la iteración.")
        # tol controla la precisión de la variable independiente (x o T).
        # No se compara directamente con |f| porque el residuo puede tener
        # unidades o escala distintas.
        if fc == 0.0 or 0.5*abs(b-a) <= tol:
            return c, it, fc
        if fa*fc <= 0:
            b, fb = c, fc
        else:
            a, fa = c, fc
    raise RuntimeError(f"No hubo convergencia en {maxiter} iteraciones.")


def find_brackets(f: Callable[[float], float], lo: float, hi: float,
                  n: int = 500, eps: float = 1e-9) -> List[Tuple[float, float]]:
    xs = np.linspace(lo, hi, n+1)
    out = []
    prevx, prevf = None, None
    for x in xs:
        try:
            fx = float(f(float(x)))
        except Exception:
            prevx = prevf = None
            continue
        if not math.isfinite(fx):
            prevx = prevf = None
            continue
        if abs(fx) < eps:
            a = max(lo, x-(hi-lo)/n)
            b = min(hi, x+(hi-lo)/n)
            out.append((float(a), float(b)))
        elif prevf is not None and prevf*fx < 0:
            out.append((float(prevx), float(x)))
        prevx, prevf = float(x), fx
    # fusionar solapes
    merged = []
    for a,b in out:
        if not merged or a > merged[-1][1] + 1e-12:
            merged.append([a,b])
        else:
            merged[-1][1] = max(merged[-1][1], b)
    return [tuple(z) for z in merged]


# ---------------------------------------------------------------------------
# ELV
# ---------------------------------------------------------------------------

def bubble_pressure(x: Sequence[float], T: float, model: ActivityModel,
                    vp: VaporPressure) -> Tuple[float, np.ndarray, np.ndarray, np.ndarray]:
    x = np.asarray(x, dtype=float)
    g = model.gammas(x, T)
    pstar = vp.psat(T)
    if len(pstar) != len(x) or len(g) != len(x):
        raise ValueError("Número de componentes inconsistente.")
    contrib = x*g*pstar
    P = float(np.sum(contrib))
    if P <= 0:
        raise ValueError("Presión de burbuja no positiva.")
    y = contrib/P
    return P, y, g, pstar


def bubble_pressure_gamma_phi(x: Sequence[float], T: float, model: ActivityModel,
                              vp: VaporPressure, phi_sat: Sequence[float],
                              phi_v: Sequence[float], poynting: Sequence[float]):
    x = np.asarray(x, dtype=float)
    g = model.gammas(x, T)
    ps = vp.psat(T)
    phis = np.asarray(phi_sat, dtype=float)
    phiv = np.asarray(phi_v, dtype=float)
    pi = np.asarray(poynting, dtype=float)
    if np.any(phis <= 0) or np.any(phiv <= 0) or np.any(pi <= 0):
        raise ValueError("φ y factores de Poynting deben ser positivos.")
    contrib = x*g*ps*phis*pi/phiv
    P = float(np.sum(contrib))
    y = contrib/P
    return P, y, g, ps, contrib


def dew_pressure_binary(y1: float, T: float, model: ActivityModel, vp: VaporPressure,
                        tol: float, maxiter: int = 200, relax: float = 1.0):
    y = np.array([y1, 1-y1], dtype=float)
    ps = vp.psat(T)
    P = 1.0/float(np.sum(y/ps))
    x = y*P/ps
    x /= np.sum(x)
    for it in range(1, maxiter+1):
        g = model.gammas(x, T)
        Pnew = 1.0/float(np.sum(y/(g*ps)))
        xraw = y*Pnew/(g*ps)
        xnew = xraw/np.sum(xraw)
        xupd = relax*xnew + (1-relax)*x
        err = float(np.max(np.abs(xupd-x)))
        x = xupd
        P = Pnew
        if err <= tol:
            residual = float(np.sum(y*P/(g*ps)) - 1.0)
            return P, x, g, it, err, residual
    raise RuntimeError(f"El cálculo de rocío no convergió en {maxiter} iteraciones.")


def bubble_temperature(x: Sequence[float], P: float, model: ActivityModel,
                       vp: VaporPressure, Tlo: float, Thi: float,
                       tol: float, maxiter: int = 200):
    x = np.asarray(x, dtype=float)
    def f(T):
        g = model.gammas(x, T)
        return float(np.sum(x*g*vp.psat(T)) - P)
    T, it, res = bisection(f, Tlo, Thi, tol, maxiter)
    Pb, y, g, ps = bubble_pressure(x, T, model, vp)
    return T, y, g, ps, it, res, Pb


def dew_inner_at_T(y: np.ndarray, T: float, model: ActivityModel, vp: VaporPressure,
                   x0: Optional[np.ndarray], tol_x: float, maxiter: int,
                   relax: float = 1.0):
    ps = vp.psat(T)
    if x0 is None:
        x = y/ps
        x /= np.sum(x)
    else:
        x = np.asarray(x0, dtype=float)
        x = np.clip(x, 1e-14, 1)
        x /= np.sum(x)
    for it in range(1, maxiter+1):
        g = model.gammas(x, T)
        xraw = y/(g*ps)
        S = float(np.sum(xraw))
        if S <= 0 or not math.isfinite(S):
            raise ValueError("Suma de rocío no válida.")
        xnew = xraw/S
        xupd = relax*xnew + (1-relax)*x
        err = float(np.max(np.abs(xupd-x)))
        x = xupd
        if err <= tol_x:
            g = model.gammas(x, T)
            xraw = y/(g*ps)
            S = float(np.sum(xraw))
            return x, g, S, it, err
    raise RuntimeError("La iteración interna de composición no convergió.")


def dew_temperature(y: Sequence[float], P: float, model: ActivityModel,
                    vp: VaporPressure, Tlo: float, Thi: float,
                    tol_T: float, tol_x: float, maxiter: int = 200,
                    relax: float = 1.0):
    y = np.asarray(y, dtype=float)
    def f(T):
        _, _, S0, _, _ = dew_inner_at_T(y, T, model, vp, None, tol_x, maxiter, relax)
        return P*S0 - 1.0
    T, itT, res = bisection(f, Tlo, Thi, tol_T, maxiter)
    x, g, S0, itx, errx = dew_inner_at_T(y, T, model, vp, None, tol_x, maxiter, relax)
    ps = vp.psat(T)
    check = float(np.sum(y*P/(g*ps)))
    return T, x, g, ps, itT, itx, res, errx, check

def azeotrope_roots(T: float, model: ActivityModel, vp: VaporPressure,
                    tol: float, maxiter: int = 200):
    ps = vp.psat(T)
    if len(ps) != 2:
        raise ValueError("La búsqueda de azeótropos implementada es binaria.")
    def f(x1):
        g = model.gammas([x1, 1-x1], T)
        return math.log(g[0]*ps[0]) - math.log(g[1]*ps[1])
    brackets = find_brackets(f, 1e-8, 1-1e-8, 800)
    roots = []
    for a,b in brackets:
        try:
            r,it,res = bisection(f,a,b,tol,maxiter)
        except ValueError:
            continue
        if 1e-6 < r < 1-1e-6 and all(abs(r-q[0])>1e-5 for q in roots):
            g = model.gammas([r,1-r], T)
            Paz = g[0]*ps[0]
            roots.append((r,Paz,g,it,res))
    return roots


def flash_binary(z1: float, T: float, P: float, model: ActivityModel,
                 vp: VaporPressure, tol: float, maxiter: int = 200):
    ps = vp.psat(T)
    def f(x1):
        g = model.gammas([x1,1-x1], T)
        yraw = np.array([x1,1-x1])*g*ps/P
        return float(np.sum(yraw)-1.0)
    brackets = find_brackets(f, 1e-8, 1-1e-8, 1000)
    candidates = []
    for a,b in brackets:
        try:
            x1,it,res = bisection(f,a,b,tol,maxiter)
        except ValueError:
            continue
        x = np.array([x1,1-x1])
        g = model.gammas(x,T)
        y = x*g*ps/P
        y /= np.sum(y)
        if abs(y[0]-x[0]) < 1e-12:
            continue
        beta = (z1-x[0])/(y[0]-x[0])
        candidates.append((x,y,g,beta,it,res))
    physical = [c for c in candidates if -1e-9 <= c[3] <= 1+1e-9]
    if physical:
        x,y,g,beta,it,res = physical[0]
        beta = min(1.0,max(0.0,beta))
        return "bifásico", x,y,g,beta,it,res
    # clasificación aproximada mediante burbuja/rocío de la composición global
    z = np.array([z1,1-z1])
    Pb,_,_,_ = bubble_pressure(z,T,model,vp)
    try:
        Pd,_,_,_,_,_ = dew_pressure_binary(z1,T,model,vp,tol,maxiter)
    except Exception:
        Pd = float("nan")
    if math.isfinite(Pd):
        lo,hi = min(Pb,Pd),max(Pb,Pd)
        if P > hi:
            return "líquido", None,None,None,0.0,0,float("nan")
        if P < lo:
            return "vapor", None,None,None,1.0,0,float("nan")
    return "sin raíz bifásica física", None,None,None,float("nan"),0,float("nan")


# ---------------------------------------------------------------------------
# Ajuste de datos
# ---------------------------------------------------------------------------

def experimental_gammas(x1, y1, P, ps1, ps2):
    x1=np.asarray(x1,float); y1=np.asarray(y1,float); P=np.asarray(P,float)
    x2=1-x1; y2=1-y1
    if np.any((x1<=0)|(x1>=1)|(y1<=0)|(y1>=1)):
        raise ValueError("Para calcular γ experimentales se requieren 0 < x_i,y_i < 1.")
    g1=y1*P/(x1*ps1)
    g2=y2*P/(x2*ps2)
    return g1,g2


def fit_margules2(x1, g1, g2):
    rows=[]; obs=[]
    for x,g_1,g_2 in zip(x1,g1,g2):
        x2=1-x
        # lnγ1 = x2²[(1-2x1) A12 + 2x1 A21]
        rows.append([x2*x2*(1-2*x), x2*x2*(2*x)])
        obs.append(math.log(g_1))
        # lnγ2 = x1²[2x2 A12 + (1-2x2) A21]
        rows.append([x*x*(2*x2), x*x*(1-2*x2)])
        obs.append(math.log(g_2))
    A=np.asarray(rows,float); b=np.asarray(obs,float)
    p,*_=np.linalg.lstsq(A,b,rcond=None)
    return float(p[0]),float(p[1])


def objective_van_laar(params, x1, lng1, lng2):
    a12,a21=params
    if abs(a12)<1e-10 or abs(a21)<1e-10:
        return 1e100
    s=0.0
    try:
        m=VanLaar(a12,a21)
        for x,l1,l2 in zip(x1,lng1,lng2):
            g=m.gammas([x,1-x])
            s+=(math.log(g[0])-l1)**2+(math.log(g[1])-l2)**2
    except Exception:
        return 1e100
    return s


def nelder_mead_2d(fun, x0, step=0.2, tol=1e-10, maxiter=2000):
    simplex=np.array([x0,[x0[0]+step,x0[1]],[x0[0],x0[1]+step]],float)
    vals=np.array([fun(p) for p in simplex])
    for it in range(maxiter):
        idx=np.argsort(vals); simplex=simplex[idx]; vals=vals[idx]
        if np.max(np.linalg.norm(simplex-simplex[0],axis=1))<tol:
            return simplex[0],vals[0],it+1
        best,second,worst=simplex
        centroid=(best+second)/2
        xr=centroid+(centroid-worst); fr=fun(xr)
        if vals[0] <= fr < vals[1]:
            simplex[2]=xr; vals[2]=fr; continue
        if fr < vals[0]:
            xe=centroid+2*(xr-centroid); fe=fun(xe)
            if fe<fr: simplex[2],vals[2]=xe,fe
            else: simplex[2],vals[2]=xr,fr
            continue
        xc=centroid+0.5*(worst-centroid); fc=fun(xc)
        if fc<vals[2]:
            simplex[2],vals[2]=xc,fc; continue
        simplex[1]=best+0.5*(simplex[1]-best)
        simplex[2]=best+0.5*(simplex[2]-best)
        vals[1]=fun(simplex[1]); vals[2]=fun(simplex[2])
    raise RuntimeError("El ajuste de Van Laar no convergió.")


def fit_van_laar(x1,g1,g2,initial=(1.0,1.0)):
    lng1=np.log(g1); lng2=np.log(g2)
    fun=lambda p: objective_van_laar(p,x1,lng1,lng2)
    p,val,it=nelder_mead_2d(fun,np.array(initial,float))
    return float(p[0]),float(p[1]),val,it


def model_predictions(x1, model, ps1, ps2):
    P=[]; y=[]
    for x in x1:
        g=model.gammas([x,1-x])
        p=x*g[0]*ps1+(1-x)*g[1]*ps2
        yy=x*g[0]*ps1/p
        P.append(p); y.append(yy)
    return np.array(P),np.array(y)


def mae_rmse(obs,pred):
    d=np.asarray(pred)-np.asarray(obs)
    return float(np.mean(np.abs(d))),float(np.sqrt(np.mean(d*d)))


# ---------------------------------------------------------------------------
# Comprobaciones y utilidades docentes
# ---------------------------------------------------------------------------

def infinite_dilution_parameters(gamma1_inf: float, gamma2_inf: float) -> Tuple[float,float]:
    if gamma1_inf <= 0 or gamma2_inf <= 0:
        raise ValueError("Los coeficientes a dilución infinita deben ser positivos.")
    return math.log(gamma1_inf), math.log(gamma2_inf)

def margules2_dln_dx(x1: float, A12: float, A21: float) -> Tuple[float,float]:
    x=x1
    d1 = 2*(x-1)*(A12 + 2*x*(A21-A12)) + (1-x)**2*2*(A21-A12)
    d2 = 2*x*(A21 + 2*(A12-A21)*(1-x)) - 2*x*x*(A12-A21)
    return d1,d2

def gibbs_duhem_residual_margules2(x1: float, A12: float, A21: float) -> float:
    d1,d2=margules2_dln_dx(x1,A12,A21)
    return x1*d1 + (1-x1)*d2

def azeotrope_margules1_analytic(A: float, ps1: float, ps2: float) -> Optional[float]:
    if A == 0 or ps1 <= 0 or ps2 <= 0:
        return None
    x = 0.5*(1.0 + math.log(ps1/ps2)/A)
    return x if 0.0 < x < 1.0 else None

def azeotrope_margules1_threshold(ps1: float, ps2: float) -> float:
    if ps1 <= 0 or ps2 <= 0:
        raise ValueError("Las presiones de vapor deben ser positivas.")
    return abs(math.log(ps1/ps2))

def experimental_azeotrope_properties(x1: float, T: float, P: float, vp: VaporPressure):
    ps=vp.psat(T)
    if len(ps)!=2:
        raise ValueError("Se requiere un sistema binario.")
    g=np.array([P/ps[0],P/ps[1]],float)
    x=np.array([x1,1-x1],float)
    ge_rt=float(np.dot(x,np.log(g)))
    ge=R*T*ge_rt
    Pideal=float(np.dot(x,ps))
    K=g*ps/P
    return ps,g,ge_rt,ge,Pideal,K

def stage_progression(xdata: Sequence[float], ydata: Sequence[float], x0: float, target: float, max_stages: int=100):
    x=np.asarray(xdata,float); y=np.asarray(ydata,float)
    if len(x)!=len(y) or len(x)<2:
        raise ValueError("Se requieren al menos dos pares x-y.")
    idx=np.argsort(x); x=x[idx]; y=y[idx]
    if np.any(np.diff(x)<=0):
        raise ValueError("Los valores de x deben ser estrictamente crecientes.")
    if not (x[0] <= x0 <= x[-1]) or not (x[0] <= target <= x[-1]):
        raise ValueError("La composición inicial y el objetivo deben estar dentro de los datos.")
    stages=[x0]; cur=x0
    for _ in range(max_stages):
        nxt=float(np.interp(cur,x,y)); stages.append(nxt)
        if nxt >= target: return stages
        if nxt <= cur + 1e-12: break
        cur=nxt
    return stages

def plot_experimental_yx(xdata, ydata, stages=None):
    plt,comma=setup_plot()
    x=np.asarray(xdata,float); y=np.asarray(ydata,float)
    fig,ax=plt.subplots()
    ax.plot(x,y,"o-",label="Datos de equilibrio")
    ax.plot([0,1],[0,1],"--",label=r"$y=x$")
    if stages and len(stages)>1:
        for a,b in zip(stages[:-1],stages[1:]):
            ax.plot([a,a],[a,b],":"); ax.plot([a,b],[b,b],":")
    ax.set_xlabel(r"$x_1$"); ax.set_ylabel(r"$y_1$")
    ax.set_xlim(0,1); ax.set_ylim(0,1)
    ax.xaxis.set_major_formatter(comma); ax.yaxis.set_major_formatter(comma)
    ax.legend(); ax.grid(alpha=0.2)
    save_or_show(fig,"diagrama_yx_experimental.png")

# ---------------------------------------------------------------------------
# Gráficas
# ---------------------------------------------------------------------------

def setup_plot():
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter
    plt.rcParams.update({"font.family":"Arial","font.size":10})
    comma=FuncFormatter(lambda x,pos: f"{x:g}".replace(".",","))
    return plt,comma


def save_or_show(fig, default_name):
    plt,_=setup_plot()
    if ask_yes_no("¿Guardar la figura en PNG transparente a 300 ppp?", True):
        name=input(f"Nombre del archivo [{default_name}]: ").strip() or default_name
        if not name.lower().endswith(".png"):
            name += ".png"
        fig.savefig(name,dpi=300,transparent=True,bbox_inches="tight")
        print(f"Figura guardada: {os.path.abspath(name)}")
    if ask_yes_no("¿Mostrar la figura en pantalla?", True):
        plt.show()
    else:
        plt.close(fig)


def graph_activity(model):
    plt,comma=setup_plot()
    xs=np.linspace(0.001,0.999,400)
    g1=[];g2=[];ge=[]
    for x in xs:
        g=model.gammas([x,1-x])
        g1.append(g[0]);g2.append(g[1])
        ge.append(x*math.log(g[0])+(1-x)*math.log(g[1]))
    fig,ax=plt.subplots()
    ax.plot(xs,g1,label=r"$\gamma_1$")
    ax.plot(xs,g2,label=r"$\gamma_2$")
    ax.set_xlabel(r"$x_1$")
    ax.set_ylabel(r"$\gamma_i$")
    ax.xaxis.set_major_formatter(comma); ax.yaxis.set_major_formatter(comma)
    ax.legend(); ax.grid(alpha=0.2)
    save_or_show(fig,"coeficientes_actividad.png")

    fig,ax=plt.subplots()
    ax.plot(xs,ge)
    ax.set_xlabel(r"$x_1$")
    ax.set_ylabel(r"$g^E/RT$")
    ax.xaxis.set_major_formatter(comma); ax.yaxis.set_major_formatter(comma)
    ax.grid(alpha=0.2)
    save_or_show(fig,"gE_RT.png")


def graph_pxy(T,model,vp):
    plt,comma=setup_plot()
    xs=np.linspace(0,1,301)
    Pb=[];ys=[]
    for x in xs:
        P,y,_,_=bubble_pressure([x,1-x],T,model,vp)
        Pb.append(P);ys.append(y[0])
    fig,ax=plt.subplots()
    ax.plot(xs,Pb,label="Burbuja")
    ax.plot(ys,Pb,label="Rocío")
    ax.set_xlabel(r"$x_1$ (líquido) / $y_1$ (vapor)")
    ax.set_ylabel(f"P ({vp.unit})")
    ax.xaxis.set_major_formatter(comma); ax.yaxis.set_major_formatter(comma)
    ax.legend(); ax.grid(alpha=0.2)
    save_or_show(fig,"diagrama_Pxy.png")


def graph_yx(T,model,vp):
    plt,comma=setup_plot()
    xs=np.linspace(0,1,301); ys=[]
    for x in xs:
        _,y,_,_=bubble_pressure([x,1-x],T,model,vp); ys.append(y[0])
    fig,ax=plt.subplots()
    ax.plot(xs,ys,label="Equilibrio")
    ax.plot([0,1],[0,1],"--",label=r"$y_1=x_1$")
    ax.set_xlabel(r"$x_1$"); ax.set_ylabel(r"$y_1$")
    ax.set_xlim(0,1); ax.set_ylim(0,1)
    ax.xaxis.set_major_formatter(comma); ax.yaxis.set_major_formatter(comma)
    ax.legend(); ax.grid(alpha=0.2)
    save_or_show(fig,"diagrama_yx.png")


def graph_txy(P,model,vp,Tlo,Thi,tol,maxiter):
    plt,comma=setup_plot()
    xs=np.linspace(0.001,0.999,101)
    Ts=[];ys=[]
    for x in xs:
        try:
            T,y,*_=bubble_temperature([x,1-x],P,model,vp,Tlo,Thi,tol,maxiter)
            Ts.append(T);ys.append(y[0])
        except Exception:
            Ts.append(np.nan);ys.append(np.nan)
    fig,ax=plt.subplots()
    ax.plot(xs,Ts,label="Burbuja")
    ax.plot(ys,Ts,label="Rocío")
    ax.set_xlabel(r"$x_1$ (líquido) / $y_1$ (vapor)")
    ax.set_ylabel("T (K)")
    ax.xaxis.set_major_formatter(comma); ax.yaxis.set_major_formatter(comma)
    ax.legend(); ax.grid(alpha=0.2)
    save_or_show(fig,"diagrama_Txy.png")


# ---------------------------------------------------------------------------
# Construcción interactiva de modelos y correlaciones
# ---------------------------------------------------------------------------

def choose_activity_model(return_measured=False):
    print("\nModelo de actividad")
    print("  1. Ideal")
    print("  2. γ constantes introducidos por el usuario")
    print("  3. Margules de un parámetro")
    print("  4. Margules de dos parámetros")
    print("  5. Van Laar")
    print("  6. Wilson")
    print("Nota: NRTL y UNIQUAC se presentan en el capítulo de forma introductoria,")
    print("sin sus expresiones completas; no se implementan ecuaciones no desarrolladas en el texto.")
    op=input("Opción: ").strip()
    ms=[]
    if op=="1": model=Ideal()
    elif op=="2":
        g1=input_measured("γ1: ",positive=True); g2=input_measured("γ2: ",positive=True)
        ms=[g1,g2]; model=ConstantGamma([g1.value,g2.value])
    elif op=="3":
        A=input_measured("A: "); ms=[A]; model=Margules1(A.value)
    elif op=="4":
        a12=input_measured("A12: "); a21=input_measured("A21: "); ms=[a12,a21]
        model=Margules2(a12.value,a21.value)
    elif op=="5":
        a12=input_measured("A12: "); a21=input_measured("A21: "); ms=[a12,a21]
        model=VanLaar(a12.value,a21.value)
    elif op=="6":
        l12=input_measured("Λ12: ",positive=True); l21=input_measured("Λ21: ",positive=True)
        ms=[l12,l21]; model=Wilson(l12.value,l21.value)
    else:
        raise ValueError("Opción no válida.")
    return (model,ms) if return_measured else model


def vp_precision_inputs(vp, vpms, Tm=None):
    """Datos que realmente limitan la precisión de P_i*.

    Si P_i* se introduce directamente, la temperatura solo describe la
    condición y no participa en el cálculo. Si P_i* procede de una
    correlación, T sí forma parte de la evaluación y limita la precisión.
    """
    data = list(vpms)
    if not isinstance(vp, DirectPsat) and Tm is not None:
        data.append(Tm)
    return data


def choose_vapor_pressure(n=2, return_measured=False):
    print("\nPresión de vapor")
    print("  1. Introducir P_i* directamente (T fija)")
    print("  2. Correlación del capítulo: ln(P_i*/unidad) = A_i - B_i/T")
    print("  3. Antoine: log10(P_i*) = A_i - B_i/(T + C_i)")
    op=input("Opción: ").strip()
    unit=input("Unidad de presión [kPa]: ").strip() or "kPa"
    ms=[]
    if op=="1":
        vals=[]
        for i in range(n):
            m=input_measured(f"P{i+1}* ({unit}): ",positive=True); ms.append(m); vals.append(m.value)
        vp=DirectPsat(vals,unit)
    elif op=="2":
        A=[];B=[]
        for i in range(n):
            ma=input_measured(f"A{i+1}: "); mb=input_measured(f"B{i+1} (K): ",positive=True)
            ms += [ma,mb]; A.append(ma.value); B.append(mb.value)
        vp=SimpleExpPsat(A,B,unit)
    elif op=="3":
        scale=(input("Temperatura usada por Antoine: C para °C, K para K [C]: ").strip() or "C").upper()
        A=[];B=[];C=[]
        for i in range(n):
            ma=input_measured(f"A{i+1}: "); mb=input_measured(f"B{i+1}: "); mc=input_measured(f"C{i+1}: ")
            ms += [ma,mb,mc]; A.append(ma.value); B.append(mb.value); C.append(mc.value)
        if ask_yes_no("¿Desea declarar el intervalo de validez de Antoine?", True):
            tmin=input_float(f"T mínima ({'°C' if scale=='C' else 'K'}): ")
            tmax=input_float(f"T máxima ({'°C' if scale=='C' else 'K'}): ")
        else:
            tmin=tmax=None
        vp=AntoinePsat(A,B,C,scale,unit,tmin,tmax)
    else:
        raise ValueError("Opción no válida.")
    return (vp,ms) if return_measured else vp


# ---------------------------------------------------------------------------
# Menús
# ---------------------------------------------------------------------------

def menu_activity():
    model,mp=choose_activity_model(True)
    x1=input_measured("x1: ",min_value=0,max_value=1)
    Tm=input_measured("T (K), si desea gE en J/mol: ",positive=True)
    x=[x1.value,1-x1.value]
    g,a,ge_rt=activity_properties(x,model,Tm.value)
    sf_dimless=sf_for_values([x1]+mp)
    sf_ge=sf_for_values([x1,Tm]+mp)
    print(f"\nModelo: {model.name}")
    print(f"γ1 = {format_sig(g[0],sf_dimless)}")
    print(f"γ2 = {format_sig(g[1],sf_dimless)}")
    print(f"a1 = {format_sig(a[0],sf_dimless)}")
    print(f"a2 = {format_sig(a[1],sf_dimless)}")
    print(f"gE/RT = {format_sig(ge_rt,sf_dimless)}")
    ge=R*Tm.value*ge_rt
    show_result("gE",ge,sf_ge,"J mol^-1",
                "sin redondeos intermedios; precisión limitada por los datos introducidos")
    mu=R*Tm.value*np.log(g)
    print(f"μ1^E = RT ln γ1 = {format_sig(mu[0],sf_ge)} J mol^-1")
    print(f"μ2^E = RT ln γ2 = {format_sig(mu[1],sf_ge)} J mol^-1")
    if ask_yes_no("¿Representar γ_i y gE/RT frente a x1?",False):
        graph_activity(model)


def menu_bubble_pressure():
    n=input_int("Número de componentes [2]: ",min_value=2,default=2)
    if n==2:
        model,mp=choose_activity_model(True)
    else:
        print("\nPara más de dos componentes se permiten γ_i introducidos directamente o fase líquida ideal.")
        ideal=ask_yes_no("¿Fase líquida ideal?",False)
        mp=[]
        if ideal: model=Ideal()
        else:
            gs=[]
            for i in range(n):
                mg=input_measured(f"γ{i+1}: ",positive=True); mp.append(mg); gs.append(mg.value)
            model=ConstantGamma(gs)
    vp,vpms=choose_vapor_pressure(n,True)
    xms=[]; xs=[]; remaining=1.0
    for i in range(n-1):
        mx=input_measured(f"x{i+1}: ",min_value=0,max_value=remaining)
        xms.append(mx); xs.append(mx.value); remaining-=mx.value
    xs.append(max(0.0,remaining)); print(f"x{n} por cierre = {xs[-1]:.12g}")
    Tm=input_measured("T (K): ",positive=True)
    P,y,g,ps=bubble_pressure(xs,Tm.value,model,vp)
    base_sf=sf_for_values(xms+mp+vp_precision_inputs(vp,vpms,Tm))
    terms=[(xs[i]*g[i]*ps[i],base_sf) for i in range(n)]
    out,crit=format_sum_of_products(P,terms)
    print(f"\nP_burbuja = {out} {vp.unit}"); print(f"Criterio de redondeo: {crit}")
    for i,yy in enumerate(y,1): print(f"y{i} = {format_sig(float(yy),base_sf)}")
    print(f"Comprobación Σy_i = {sum(y):.12g}")
    if ask_yes_no("¿Comparar con la predicción ideal?",True):
        Pi,_,_,_=bubble_pressure(xs,Tm.value,Ideal(),vp)
        print(f"P_burbuja ideal = {format_sig(Pi,base_sf)} {vp.unit}")
        print(f"Error relativo al usar ideal = {format_sig(100*(Pi-P)/P,base_sf)} %")

def menu_dew_pressure():
    model,mp=choose_activity_model(True)
    vp,vpms=choose_vapor_pressure(2,True)
    y1=input_measured("y1: ",min_value=0,max_value=1)
    Tm=input_measured("T (K): ",positive=True)
    tol,maxiter=ask_tolerance("x1",1e-8)
    relax=input_float("Factor de relajación (0 < r <= 1) [1]: ",min_value=1e-6,max_value=1,default=1)
    P,x,g,it,err,res=dew_pressure_binary(y1.value,Tm.value,model,vp,tol,maxiter,relax)
    sf=sf_for_values([y1]+mp+vp_precision_inputs(vp,vpms,Tm))
    show_result("Presión de rocío",P,sf,vp.unit,
                "cifras significativas de los datos; la tolerancia solo controla la convergencia")
    print(f"x1 = {format_sig(x[0],sf)}, x2 = {format_sig(x[1],sf)}")
    print(f"Iteraciones: {it}; cambio final en x = {err:.3e}; residuo = {res:.3e}")


def menu_bubble_temperature():
    model,mp=choose_activity_model(True)
    vp,vpms=choose_vapor_pressure(2,True)
    if isinstance(vp,DirectPsat):
        raise ValueError("Para calcular temperatura se necesita una correlación P_i*(T), no valores constantes.")
    x1=input_measured("x1: ",min_value=0,max_value=1)
    Pm=input_measured(f"P ({vp.unit}): ",positive=True)
    Tlo=input_float("Límite inferior de T (K): ",positive=True)
    Thi=input_float("Límite superior de T (K): ",positive=True)
    if Thi<=Tlo: raise ValueError("El límite superior debe superar al inferior.")
    tol,maxiter=ask_tolerance("temperatura (K)",1e-6)
    T,y,g,ps,it,res,Pcalc=bubble_temperature([x1.value,1-x1.value],Pm.value,model,vp,Tlo,Thi,tol,maxiter)
    sf=sf_for_values([x1,Pm]+mp+vpms)
    show_result("Temperatura de burbuja",T,sf,"K",
                "precisión de los datos, no del número de iteraciones")
    print(f"y1 = {format_sig(y[0],sf)}, y2 = {format_sig(y[1],sf)}")
    print(f"Iteraciones: {it}; residuo de presión = {res:.3e} {vp.unit}")


def menu_dew_temperature():
    model,mp=choose_activity_model(True)
    vp,vpms=choose_vapor_pressure(2,True)
    if isinstance(vp,DirectPsat):
        raise ValueError("Para calcular temperatura se necesita una correlación P_i*(T).")
    y1=input_measured("y1: ",min_value=0,max_value=1)
    Pm=input_measured(f"P ({vp.unit}): ",positive=True)
    Tlo=input_float("Límite inferior de T (K): ",positive=True)
    Thi=input_float("Límite superior de T (K): ",positive=True)
    tolT,maxiter=ask_tolerance("temperatura (K)",1e-6)
    tolx=input_float("Tolerancia interna para composición [1e-8]: ",positive=True,default=1e-8)
    relax=input_float("Factor de relajación interno (0 < r <= 1) [1]: ",
                      min_value=1e-6,max_value=1,default=1)
    T,x,g,ps,itT,itx,res,errx,check=dew_temperature(
        [y1.value,1-y1.value],Pm.value,model,vp,Tlo,Thi,tolT,tolx,maxiter,relax)
    sf=sf_for_values([y1,Pm]+mp+vpms)
    show_result("Temperatura de rocío",T,sf,"K",
                "precisión de los datos; tolerancias externa e interna se informan por separado")
    print(f"x1 = {format_sig(x[0],sf)}, x2 = {format_sig(x[1],sf)}")
    print(f"Iteraciones externas: {itT}; internas finales: {itx}")
    print(f"Residuo externo = {res:.3e}; cambio interno = {errx:.3e}")
    print(f"Comprobación Σ[y_i P/(γ_i P_i*)] = {check:.12g}")


def menu_azeotrope():
    model,mp=choose_activity_model(True)
    if isinstance(model,(Ideal,ConstantGamma)):
        print("Aviso: con γ constantes, la existencia de una raíz interior no representa")
        print("la dependencia composicional propia de un modelo de actividad.")
    vp,vpms=choose_vapor_pressure(2,True)
    Tm=input_measured("T (K): ",positive=True)
    tol,maxiter=ask_tolerance("x1",1e-8)
    roots=azeotrope_roots(Tm.value,model,vp,tol,maxiter)
    if not roots:
        print("No se ha encontrado una raíz azeotrópica interior en 0 < x1 < 1.")
        return
    sf=sf_for_values(mp+vp_precision_inputs(vp,vpms,Tm))
    for j,(x,Paz,g,it,res) in enumerate(roots,1):
        print(f"\nAzeótropo {j}")
        print(f"x1 = y1 = {format_sig(x,sf)}")
        print(f"γ1 = {format_sig(g[0],sf)}, γ2 = {format_sig(g[1],sf)}")
        print(f"P_az = {format_sig(Paz,sf)} {vp.unit}")
        print(f"Iteraciones: {it}; residuo logarítmico = {res:.3e}")
        ps=vp.psat(Tm.value)
        print(f"γ1 P1* = {g[0]*ps[0]:.10g}; γ2 P2* = {g[1]*ps[1]:.10g}")


def menu_flash():
    model,mp=choose_activity_model(True)
    vp,vpms=choose_vapor_pressure(2,True)
    z1=input_measured("z1 (composición global): ",min_value=0,max_value=1)
    Tm=input_measured("T (K): ",positive=True)
    Pm=input_measured(f"P ({vp.unit}): ",positive=True)
    tol,maxiter=ask_tolerance("x1",1e-9)
    state,x,y,g,beta,it,res=flash_binary(z1.value,Tm.value,Pm.value,model,vp,tol,maxiter)
    sf=sf_for_values([z1,Pm]+mp+vp_precision_inputs(vp,vpms,Tm))
    print(f"\nEstado calculado: {state}")
    if state=="bifásico":
        print(f"x1 = {format_sig(x[0],sf)}, x2 = {format_sig(x[1],sf)}")
        print(f"y1 = {format_sig(y[0],sf)}, y2 = {format_sig(y[1],sf)}")
        print(f"β = V/F = {format_sig(beta,sf)}")
        zcalc=(1-beta)*x+beta*y
        print(f"Comprobación z1 = {(zcalc[0]):.12g}; z2 = {(zcalc[1]):.12g}")
        print(f"Residuo de equilibrio = {res:.3e}")


def menu_gamma_phi():
    model,mp=choose_activity_model(True)
    vp,vpms=choose_vapor_pressure(2,True)
    x1=input_measured("x1: ",min_value=0,max_value=1)
    Tm=input_measured("T (K): ",positive=True)
    print("Introduzca correcciones constantes para el estado calculado.")
    phis=[];phiv=[];poy=[];cms=[]
    for i in range(2):
        a=input_measured(f"φ{i+1}* (vapor saturado): ",positive=True)
        b=input_measured(f"φ{i+1}^(V) (fase vapor): ",positive=True)
        c=input_measured(f"Π{i+1} (Poynting): ",positive=True)
        phis.append(a.value);phiv.append(b.value);poy.append(c.value);cms += [a,b,c]
    P,y,g,ps,contrib=bubble_pressure_gamma_phi(
        [x1.value,1-x1.value],Tm.value,model,vp,phis,phiv,poy)
    sf=sf_for_values([x1]+mp+vp_precision_inputs(vp,vpms,Tm)+cms)
    print(f"P_burbuja γ-φ = {format_sig(P,sf)} {vp.unit}")
    print(f"y1 = {format_sig(y[0],sf)}, y2 = {format_sig(y[1],sf)}")
    Pmr,ymr,_,_=bubble_pressure([x1.value,1-x1.value],Tm.value,model,vp)
    print(f"P_burbuja Raoult modificada = {format_sig(Pmr,sf)} {vp.unit}")
    err=100*(Pmr-P)/P
    print(f"Error relativo al omitir φ y Π = {format_sig(err,sf)} %")


def menu_graphs():
    model=choose_activity_model()
    print("\nGráfica")
    print("  1. γ_i-x y gE/RT-x")
    print("  2. P-x-y a T fija")
    print("  3. y-x a T fija")
    print("  4. T-x-y a P fija")
    print("  5. Diagrama y-x experimental y etapas de enriquecimiento")
    op=input("Opción: ").strip()
    if op=="1":
        graph_activity(model); return
    if op=="5":
        n=input_int("Número de pares experimentales x-y: ",min_value=2)
        xd=[]; yd=[]
        for i in range(n):
            xd.append(input_float(f"x1, punto {i+1}: ",min_value=0,max_value=1))
            yd.append(input_float(f"y1, punto {i+1}: ",min_value=0,max_value=1))
        stages=None
        if ask_yes_no("¿Calcular etapas desde una composición inicial?",True):
            x0=input_float("Composición líquida inicial x1: ",min_value=0,max_value=1)
            target=input_float("Composición líquida objetivo: ",min_value=0,max_value=1)
            stages=stage_progression(xd,yd,x0,target)
            print("Secuencia: " + " -> ".join(f"{z:.6f}".replace(".",",") for z in stages))
            if stages[-1] >= target: print(f"Etapas teóricas necesarias: {len(stages)-1}")
            else: print("No se alcanzó el objetivo.")
        plot_experimental_yx(xd,yd,stages); return
    vp=choose_vapor_pressure(2)
    if op in {"2","3"}:
        T=input_float("T (K): ",positive=True)
        if op=="2": graph_pxy(T,model,vp)
        else: graph_yx(T,model,vp)
    elif op=="4":
        if isinstance(vp,DirectPsat):
            raise ValueError("T-x-y requiere P_i*(T).")
        P=input_float(f"P ({vp.unit}): ",positive=True)
        Tlo=input_float("T mínima de búsqueda (K): ",positive=True)
        Thi=input_float("T máxima de búsqueda (K): ",positive=True)
        tol,maxiter=ask_tolerance("temperatura (K)",1e-5)
        graph_txy(P,model,vp,Tlo,Thi,tol,maxiter)
    else:
        raise ValueError("Opción no válida.")


def read_dataset_manual():
    n=input_int("Número de puntos experimentales: ",min_value=2)
    x=[];y=[];P=[];ms=[]
    print("Introduzca x1, y1 y P para cada punto.")
    for i in range(n):
        print(f"Punto {i+1}")
        mx=input_measured("  x1: ",min_value=1e-12,max_value=1-1e-12)
        my=input_measured("  y1: ",min_value=1e-12,max_value=1-1e-12)
        mp=input_measured("  P: ",positive=True)
        x.append(mx.value);y.append(my.value);P.append(mp.value);ms += [mx,my,mp]
    return np.array(x),np.array(y),np.array(P),ms


def read_dataset_csv(path):
    x=[];y=[];P=[]
    with open(path,newline="",encoding="utf-8-sig") as f:
        rd=csv.DictReader(f)
        required={"x1","y1","P"}
        if not required.issubset(rd.fieldnames or []):
            raise ValueError("El CSV debe contener las columnas: x1,y1,P")
        for row in rd:
            x.append(float(normalize_number_text(row["x1"])))
            y.append(float(normalize_number_text(row["y1"])))
            P.append(float(normalize_number_text(row["P"])))
    return np.array(x),np.array(y),np.array(P)


def menu_fit():
    print("\nAjuste de datos ELV")
    print("  1. Introducción manual")
    print("  2. Archivo CSV con columnas x1,y1,P")
    op=input("Opción: ").strip()
    ms=[]
    if op=="1":
        x,y,P,ms=read_dataset_manual()
    elif op=="2":
        path=input("Ruta del CSV: ").strip()
        x,y,P=read_dataset_csv(path)
    else:
        raise ValueError("Opción no válida.")
    ps1=input_measured("P1* a la T experimental: ",positive=True)
    ps2=input_measured("P2* a la T experimental: ",positive=True)
    g1,g2=experimental_gammas(x,y,P,ps1.value,ps2.value)
    print("\nCoeficientes de actividad experimentales:")
    print("  x1          γ1          γ2")
    for xx,a,b in zip(x,g1,g2):
        print(f"  {xx:8.5f}  {a:10.6f}  {b:10.6f}")
    print("\nModelo a ajustar")
    print("  1. Margules de dos parámetros")
    print("  2. Van Laar")
    print("  3. Ambos")
    sel=input("Opción [3]: ").strip() or "3"
    models=[]
    if sel in {"1","3"}:
        a12,a21=fit_margules2(x,g1,g2)
        models.append(("Margules",Margules2(a12,a21),a12,a21))
    if sel in {"2","3"}:
        init=(max(0.1,math.log(max(g1[0],1e-9))),max(0.1,math.log(max(g2[-1],1e-9))))
        a12,a21,val,it=fit_van_laar(x,g1,g2,init)
        models.append(("Van Laar",VanLaar(a12,a21),a12,a21))
    for name,m,a12,a21 in models:
        Pp,yp=model_predictions(x,m,ps1.value,ps2.value)
        maeP,rmseP=mae_rmse(P,Pp); maey,rmsey=mae_rmse(y,yp)
        print(f"\n{name}")
        print(f"A12 = {a12:.8g}; A21 = {a21:.8g}")
        print(f"MAE(P) = {maeP:.8g}; RMSE(P) = {rmseP:.8g}")
        print(f"MAE(y1) = {maey:.8g}; RMSE(y1) = {rmsey:.8g}")
        print("Residuos P (predicho - experimental):")
        print("  " + "  ".join(f"{d:+.5g}" for d in (Pp-P)))


def menu_utilities():
    print("\nComprobaciones y utilidades")
    print("  1. Parámetros a partir de γ_i a dilución infinita")
    print("  2. MAE y RMSE de dos series")
    print("  3. Comprobación numérica de Gibbs-Duhem (Margules 2 parámetros)")
    print("  4. Propiedades de un azeótropo experimental conocido")
    print("  5. Sensibilidad/umbral del azeótropo con Margules de un parámetro")
    op=input("Opción: ").strip()
    if op=="1":
        g1=input_measured("γ1∞: ",positive=True); g2=input_measured("γ2∞: ",positive=True)
        a12,a21=infinite_dilution_parameters(g1.value,g2.value); sf=sf_for_values([g1,g2])
        print(f"A12 = {format_sig(a12,sf)}"); print(f"A21 = {format_sig(a21,sf)}")
    elif op=="2":
        n=input_int("Número de pares: ",min_value=1); obs=[]; pred=[]
        for i in range(n): obs.append(input_float(f"Experimental {i+1}: ")); pred.append(input_float(f"Calculado {i+1}: "))
        mae,rmse=mae_rmse(obs,pred); print(f"MAE = {mae:.10g}".replace(".",",")); print(f"RMSE = {rmse:.10g}".replace(".",","))
        print("Residuos: "+"  ".join(f"{d:+.6g}".replace(".",",") for d in (np.asarray(pred)-np.asarray(obs))))
    elif op=="3":
        a12=input_float("A12: "); a21=input_float("A21: "); n=input_int("Número de composiciones: ",min_value=1)
        for i in range(n):
            x=input_float(f"x1 ({i+1}): ",min_value=0,max_value=1); d1,d2=margules2_dln_dx(x,a12,a21); res=gibbs_duhem_residual_margules2(x,a12,a21)
            print(f"x1={x:.6g}: dlnγ1/dx1={d1:.10g}, dlnγ2/dx1={d2:.10g}, residuo={res:.3e}")
    elif op=="4":
        x1=input_measured("x1,az = y1,az: ",min_value=0,max_value=1); T=input_measured("T_az (K): ",positive=True); P=input_measured("P_az: ",positive=True)
        vp,vpms=choose_vapor_pressure(2,True); ps,g,ge_rt,ge,Pideal,K=experimental_azeotrope_properties(x1.value,T.value,P.value,vp)
        sf=sf_for_values([x1,T,P]+vp_precision_inputs(vp,vpms,T))
        print(f"P1* = {format_sig(ps[0],sf)} {vp.unit}; P2* = {format_sig(ps[1],sf)} {vp.unit}")
        print(f"γ1 = {format_sig(g[0],sf)}; γ2 = {format_sig(g[1],sf)}")
        print(f"K1 = {format_sig(K[0],sf)}; K2 = {format_sig(K[1],sf)}")
        print(f"gE/RT = {format_sig(ge_rt,sf)}; gE = {format_sig(ge,sf)} J mol^-1")
        print(f"P_burbuja ideal = {format_sig(Pideal,sf)} {vp.unit}")
    elif op=="5":
        ps1=input_measured("P1*: ",positive=True); ps2=input_measured("P2*: ",positive=True); n=input_int("Número de valores de A: ",min_value=1); vals=[]
        for i in range(n): vals.append(input_measured(f"A ({i+1}): "))
        pts=[]
        for A in vals:
            x=azeotrope_margules1_analytic(A.value,ps1.value,ps2.value)
            if x is None: print(f"A={A.raw}: no existe raíz interior.")
            else:
                Paz=Margules1(A.value).gammas([x,1-x])[0]*ps1.value; print(f"A={A.raw}: x1,az={x:.10g}; P_az={Paz:.10g}"); pts.append((A.value,x))
        print(f"|A| umbral = {azeotrope_margules1_threshold(ps1.value,ps2.value):.10g}")
        if len(pts)>=2: print(f"Δx/ΔA ≈ {(pts[-1][1]-pts[0][1])/(pts[-1][0]-pts[0][0]):.10g}")
    else: raise ValueError("Opción no válida.")


def main_menu():
    while True:
        print("\n" + "="*72)
        print("CAPÍTULO 8 — DISOLUCIONES NO IDEALES Y COEFICIENTES DE ACTIVIDAD")
        print("="*72)
        print("1. Actividad, coeficientes de actividad y gE")
        print("2. Presión de burbuja")
        print("3. Presión de rocío")
        print("4. Temperatura de burbuja")
        print("5. Temperatura de rocío")
        print("6. Azeótropos binarios")
        print("7. Vaporización flash binaria")
        print("8. Cálculo γ-φ con φ y Poynting constantes")
        print("9. Diagramas y gráficas")
        print("10. Ajuste de parámetros a datos ELV")
        print("11. Comprobaciones y utilidades docentes")
        print("0. Salir")
        op=input("Seleccione una opción: ").strip()
        if op=="0":
            print("Fin.")
            break
        funcs={
            "1":menu_activity,"2":menu_bubble_pressure,"3":menu_dew_pressure,
            "4":menu_bubble_temperature,"5":menu_dew_temperature,"6":menu_azeotrope,
            "7":menu_flash,"8":menu_gamma_phi,"9":menu_graphs,"10":menu_fit,
            "11":menu_utilities
        }
        if op not in funcs:
            print("Opción no válida.")
            continue
        try:
            funcs[op]()
        except (ValueError,RuntimeError,OverflowError,ZeroDivisionError) as exc:
            print(f"\nNo se pudo completar el cálculo: {exc}")


def build_parser():
    p=argparse.ArgumentParser(
        description="Cálculos del capítulo 8: disoluciones no ideales y ELV.",
        epilog=("El programa deduce las cifras significativas de los datos escritos por "
                "el usuario y redondea solo al presentar los resultados. "
                "NRTL y UNIQUAC no se implementan porque el capítulo no desarrolla "
                "sus ecuaciones completas.")
    )
    p.add_argument("--version",action="version",version="capitulo8.py 1.1")
    return p


def main():
    build_parser().parse_args()
    main_menu()


if __name__ == "__main__":
    main()
