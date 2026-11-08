#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
equilibrio_vle_ideal.py
=======================

Herramienta de cálculo para el capítulo 7: disoluciones ideales y equilibrio
líquido-vapor.

Incluye:
    1) Ley de Raoult para mezclas ideales multicomponentes.
    2) Presión de burbuja a temperatura conocida.
    3) Temperatura de burbuja a presión conocida.
    4) Presión de rocío a temperatura conocida.
    5) Temperatura de rocío a presión conocida.
    6) Coeficientes K_i y volatilidades relativas.
    7) Diagramas P-x-y para mezclas binarias.
    8) Diagramas T-x-y para mezclas binarias.
    9) Diagramas y-x para mezclas binarias.
    10) Cálculos directos cuando se conocen P_i* sin necesidad de Antoine.
    11) Diagramas T-x-y e y-x a partir de tablas de P_i*(T).

Hipótesis:
    - Fase líquida ideal: ley de Raoult.
    - Fase vapor ideal: ley de Dalton.
    - Presiones de vapor mediante Antoine cuando la temperatura es variable.
    - Antoine en la forma:
          log10(P_i*) = A_i - B_i / (T + C_i)
      con P_i* en kPa y T en K.
      Si una correlación aparece como T - c, introduzca C = -c.

Resolución numérica:
    - En modo automático se exige una raíz físicamente acotada.
    - Se intenta Newton salvaguardado.
    - Si una iteración sale del intervalo físico, la derivada no es adecuada,
      el residuo empeora o aparece una anomalía numérica, se usa bisección.
    - La convergencia exige simultáneamente tolerancia en la variable y en el
      residuo.
    - No se extrapolan de forma silenciosa las ecuaciones de Antoine fuera de
      su intervalo de validez.

Gráficos:
    - PNG.
    - Fondo transparente.
    - 600 ppp por defecto.
    - Arial, 10 pt.
    - Los diagramas P-x-y, T-x-y e y-x se limitan a sistemas binarios.

Entrada decimal:
    - Se aceptan coma o punto decimal en el modo interactivo y en los valores
      individuales de línea de comandos.
Salida:
    - Se usa coma decimal.

Ejemplos:
    python equilibrio_vle_ideal.py
    python equilibrio_vle_ideal.py --help

    python equilibrio_vle_ideal.py bubble-p \
        --component "A;6,42448;1312,253;-32,445;250;500" \
        --component "B;6,22809;1245,702;-55,189;250;500" \
        --x 0,40 --x 0,60 --T 330

    python equilibrio_vle_ideal.py bubble-t \
        --component "A;6,42448;1312,253;-32,445;250;500" \
        --component "B;6,22809;1245,702;-55,189;250;500" \
        --x 0,50 --x 0,50 --P 100

Dependencias:
    - Python >= 3.10
    - matplotlib y numpy solo para generar diagramas.

Autoría:
    Material complementario del capítulo 7.
"""

from __future__ import annotations

import argparse
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Sequence


# ---------------------------------------------------------------------------
# Utilidades numéricas y de formato
# ---------------------------------------------------------------------------

EPS = 1.0e-12


def parse_decimal(value: str | float | int) -> float:
    """Convierte un número escrito con coma o punto decimal a float."""
    s = str(value).strip().replace(" ", "").replace(",", ".")
    try:
        result = float(s)
    except ValueError as exc:
        raise ValueError(f"No se reconoce como número: {value!r}") from exc
    if not math.isfinite(result):
        raise ValueError("El dato debe ser un número finito.")
    return result


def format_sig(value: float | None, sig: int = 5) -> str:
    """Devuelve un número con cifras significativas y coma decimal; — si no procede."""
    if value is None:
        return "—"
    if not math.isfinite(value):
        return str(value)
    if value == 0:
        return "0"
    s = f"{value:.{max(1, sig)}g}"
    if "e" in s:
        mantissa, exponent = s.split("e")
        mantissa = mantissa.replace(".", ",")
        exponent = exponent.replace("+", "")
        return f"{mantissa}×10^{int(exponent)}"
    return s.replace(".", ",")


def format_fixed(value: float, decimals: int = 3) -> str:
    return f"{value:.{decimals}f}".replace(".", ",")


def validate_fraction_vector(values: Sequence[float], label: str) -> list[float]:
    """Valida y normaliza, solo por redondeo, un vector de fracciones molares."""
    vals = [float(v) for v in values]
    if len(vals) < 1:
        raise ValueError(f"Debe introducir al menos una fracción molar {label}.")
    if any((not math.isfinite(v)) or v < -EPS or v > 1.0 + EPS for v in vals):
        raise ValueError(f"Todas las fracciones molares {label} deben estar entre 0 y 1.")
    total = sum(vals)
    if total <= EPS:
        raise ValueError(f"La suma de las fracciones molares {label} debe ser positiva.")
    if abs(total - 1.0) > 1.0e-6:
        raise ValueError(
            f"Las fracciones molares {label} deben sumar 1. "
            f"Suma introducida = {total:.10g}."
        )
    # Se normaliza exclusivamente para eliminar pequeñas diferencias de redondeo.
    return [max(0.0, min(1.0, v / total)) for v in vals]


# ---------------------------------------------------------------------------
# Modelo de componente y ecuación de Antoine
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Component:
    name: str
    A: float
    B: float
    C: float
    Tmin: float | None = None
    Tmax: float | None = None

    def __post_init__(self) -> None:
        # En el modo de biblioteca los objetos pueden construirse directamente,
        # sin pasar por parse_component() y su validación numérica.
        if not self.name.strip():
            raise ValueError("El nombre del componente no puede estar vacío.")
        if any(not math.isfinite(float(v)) for v in (self.A, self.B, self.C)):
            raise ValueError(f"Los coeficientes Antoine de {self.name} deben ser finitos.")
        if self.Tmin is not None and (not math.isfinite(self.Tmin) or self.Tmin <= 0):
            raise ValueError(f"Tmin de {self.name} debe ser positiva y finita.")
        if self.Tmax is not None and (not math.isfinite(self.Tmax) or self.Tmax <= 0):
            raise ValueError(f"Tmax de {self.name} debe ser positiva y finita.")
        if self.Tmin is not None and self.Tmax is not None and self.Tmin >= self.Tmax:
            raise ValueError(f"Para {self.name}, Tmin debe ser menor que Tmax.")

    def valid_temperature(self, T: float) -> bool:
        if not math.isfinite(T) or T <= 0:
            return False
        if self.Tmin is not None and T < self.Tmin - 1.0e-10:
            return False
        if self.Tmax is not None and T > self.Tmax + 1.0e-10:
            return False
        return True

    def ensure_temperature(self, T: float) -> None:
        if not self.valid_temperature(T):
            bounds = []
            if self.Tmin is not None:
                bounds.append(f"Tmin={self.Tmin:g} K")
            if self.Tmax is not None:
                bounds.append(f"Tmax={self.Tmax:g} K")
            txt = ", ".join(bounds) if bounds else "intervalo no especificado"
            raise ValueError(
                f"T={T:g} K queda fuera del intervalo válido de Antoine "
                f"para {self.name} ({txt})."
            )

    def psat(self, T: float) -> float:
        """Presión de vapor en kPa, con Antoine log10(P*)=A-B/(T+C)."""
        self.ensure_temperature(T)
        denom = T + self.C
        if abs(denom) < EPS:
            raise ValueError(f"Singularidad en Antoine para {self.name}: T + C = 0.")
        exponent = self.A - self.B / denom
        P = 10.0 ** exponent
        if not math.isfinite(P) or P <= 0:
            raise ValueError(f"Presión de vapor no física calculada para {self.name}.")
        return P

    def dpsat_dT(self, T: float) -> float:
        """Derivada dP*/dT correspondiente a la forma de Antoine empleada."""
        P = self.psat(T)
        denom = T + self.C
        return P * math.log(10.0) * self.B / (denom * denom)

    def boiling_temperature(self, P: float) -> float:
        """Inversión analítica de Antoine para P* = P."""
        if not math.isfinite(P) or P <= 0:
            raise ValueError("La presión debe ser positiva y finita.")
        denom = self.A - math.log10(P)
        if abs(denom) < EPS:
            raise ValueError(
                f"No puede invertirse Antoine para {self.name} a P={P:g} kPa."
            )
        T = self.B / denom - self.C
        self.ensure_temperature(T)
        return T


def parse_component(spec: str) -> Component:
    """
    Lee:
        NOMBRE;A;B;C[;Tmin;Tmax]

    Ejemplo:
        "Acetona;6,42448;1312,253;-32,445;250;500"
    """
    parts = [p.strip() for p in spec.split(";")]
    if len(parts) not in (4, 6):
        raise ValueError(
            "Cada --component debe tener el formato "
            "'NOMBRE;A;B;C' o 'NOMBRE;A;B;C;Tmin;Tmax'."
        )
    name = parts[0]
    if not name:
        raise ValueError("El nombre del componente no puede quedar vacío.")
    A, B, C = map(parse_decimal, parts[1:4])
    Tmin = Tmax = None
    if len(parts) == 6:
        Tmin = parse_decimal(parts[4])
        Tmax = parse_decimal(parts[5])
        if Tmin >= Tmax:
            raise ValueError(f"Para {name}, Tmin debe ser menor que Tmax.")
    return Component(name, A, B, C, Tmin, Tmax)


# ---------------------------------------------------------------------------
# Relaciones de equilibrio ideal
# ---------------------------------------------------------------------------

def psats(components: Sequence[Component], T: float) -> list[float]:
    return [c.psat(T) for c in components]


def psats_presentes(
    components: Sequence[Component], T: float, fractions: Sequence[float]
) -> list[float | None]:
    """Evalúa Antoine solo para especies presentes.

    Para una especie ausente con Antoine fuera de intervalo, None indica
    propiedad no disponible: no se inventa una presión de vapor cero.
    """
    return [c.psat(T) if zi > EPS else None
            for c, zi in zip(components, fractions)]


def bubble_pressure(
    components: Sequence[Component], x: Sequence[float], T: float
) -> tuple[float, list[float], list[float]]:
    x = validate_fraction_vector(x, "x_i")
    if len(components) != len(x):
        raise ValueError("El número de componentes no coincide con el número de x_i.")
    pstar = psats_presentes(components, T, x)
    partial = [xi * pi if pi is not None else 0.0
               for xi, pi in zip(x, pstar)]
    P = sum(partial)
    if P <= 0:
        raise ValueError("La presión de burbuja calculada no es positiva.")
    y = [pi / P for pi in partial]
    y = validate_fraction_vector(y, "y_i calculadas")
    return P, partial, y


def dew_pressure(
    components: Sequence[Component], y: Sequence[float], T: float
) -> tuple[float, list[float]]:
    y = validate_fraction_vector(y, "y_i")
    if len(components) != len(y):
        raise ValueError("El número de componentes no coincide con el número de y_i.")
    pstar = psats_presentes(components, T, y)
    denom = sum(yi / pi for yi, pi in zip(y, pstar) if pi is not None)
    if denom <= 0:
        raise ValueError("No puede calcularse una presión de rocío física.")
    P = 1.0 / denom
    x = [yi * P / pi if pi is not None else 0.0
         for yi, pi in zip(y, pstar)]
    x = validate_fraction_vector(x, "x_i calculadas")
    return P, x


def raoult(
    components: Sequence[Component], x: Sequence[float], T: float
) -> dict:
    P, partial, y = bubble_pressure(components, x, T)
    pstar = psats_presentes(components, T, x)
    K = [pi / P if pi is not None else None for pi in pstar]
    return {
        "P": P,
        "psat": pstar,
        "partial": partial,
        "x": list(x),
        "y": y,
        "K": K,
    }


def relative_volatility(
    components: Sequence[Component], T: float, i: int, j: int
) -> float:
    pstar = psats(components, T)
    if not (0 <= i < len(components) and 0 <= j < len(components)):
        raise IndexError("Índice de componente fuera de rango.")
    return pstar[i] / pstar[j]


def validate_pstar(values: Sequence[float]) -> list[float]:
    vals = [float(v) for v in values]
    if len(vals) < 2:
        raise ValueError("Se requieren al menos dos presiones de vapor P_i*.")
    if any((not math.isfinite(v)) or v <= 0 for v in vals):
        raise ValueError("Todas las presiones de vapor P_i* deben ser positivas.")
    return vals


def raoult_from_pstar(
    x: Sequence[float], pstar: Sequence[float]
) -> dict:
    """Ley de Raoult cuando las P_i* se introducen directamente."""
    x = validate_fraction_vector(x, "x_i")
    pstar = validate_pstar(pstar)
    if len(x) != len(pstar):
        raise ValueError("Debe introducir una P_i* por cada fracción molar x_i.")
    partial = [xi * pi for xi, pi in zip(x, pstar)]
    P = sum(partial)
    if P <= 0:
        raise ValueError("La presión total calculada no es positiva.")
    y = [pi / P for pi in partial]
    y = validate_fraction_vector(y, "y_i calculadas")
    K = [pi / P for pi in pstar]
    return {"P": P, "psat": list(pstar), "partial": partial,
            "x": list(x), "y": y, "K": K}


def dew_from_pstar(
    y: Sequence[float], pstar: Sequence[float]
) -> tuple[float, list[float]]:
    """Presión de rocío y x_i cuando se conocen directamente P_i*."""
    y = validate_fraction_vector(y, "y_i")
    pstar = validate_pstar(pstar)
    if len(y) != len(pstar):
        raise ValueError("Debe introducir una P_i* por cada fracción molar y_i.")
    denom = sum(yi / pi for yi, pi in zip(y, pstar))
    P = 1.0 / denom
    x = [yi * P / pi for yi, pi in zip(y, pstar)]
    x = validate_fraction_vector(x, "x_i calculadas")
    return P, x


def binary_state_from_pstar_pressure(
    pstar: Sequence[float], P: float
) -> tuple[list[float], list[float]]:
    """
    Obtiene x e y para una mezcla binaria ideal a T conocida, cuando se
    conocen P_1*, P_2* y la presión total P.
    """
    pstar = validate_pstar(pstar)
    if len(pstar) != 2:
        raise ValueError("Este cálculo inverso requiere exactamente dos componentes.")
    if P <= 0:
        raise ValueError("La presión total debe ser positiva.")
    p1, p2 = pstar
    if abs(p1 - p2) <= 1.0e-14:
        if abs(P - p1) <= 1.0e-10 * max(1.0, P):
            raise ValueError(
                "P_1* y P_2* son iguales: la presión no determina una composición única."
            )
        raise ValueError("La presión indicada no es compatible con estas P_i*.")
    x1 = (P - p2) / (p1 - p2)
    tol = 1.0e-10
    if x1 < -tol or x1 > 1.0 + tol:
        raise ValueError(
            "La presión total queda fuera del intervalo entre P_1* y P_2*; "
            "no existe una composición líquida binaria ideal física."
        )
    x1 = min(1.0, max(0.0, x1))
    x = [x1, 1.0 - x1]
    y1 = x1 * p1 / P
    y = validate_fraction_vector([y1, 1.0 - y1], "y_i calculadas")
    return x, y


# ---------------------------------------------------------------------------
# Acotación física y solucionador salvaguardado
# ---------------------------------------------------------------------------

@dataclass
class RootResult:
    root: float
    residual: float
    iterations: int
    converged: bool
    method_used: str
    fallback_count: int


def common_temperature_interval(
    components: Sequence[Component]
) -> tuple[float | None, float | None]:
    lows = [c.Tmin for c in components if c.Tmin is not None]
    highs = [c.Tmax for c in components if c.Tmax is not None]
    lo = max(lows) if lows else None
    hi = min(highs) if highs else None
    if lo is not None and hi is not None and lo >= hi:
        raise ValueError("Los intervalos de Antoine de los componentes no se solapan.")
    return lo, hi


def physical_temperature_bracket(
    components: Sequence[Component],
    P: float,
    composition: Sequence[float],
) -> tuple[float, float]:
    """
    Acota T con las temperaturas de ebullición de los componentes presentes.
    Solo usa componentes con fracción molar > 0.
    """
    if P <= 0:
        raise ValueError("La presión total debe ser positiva.")
    temps = []
    for comp, frac in zip(components, composition):
        if frac > EPS:
            temps.append(comp.boiling_temperature(P))
    if not temps:
        raise ValueError("No hay componentes presentes para construir la acotación.")
    lo = min(temps)
    hi = max(temps)
    if abs(hi - lo) < 1.0e-10:
        delta = max(1.0e-4, abs(lo) * 1.0e-8)
        lo -= delta
        hi += delta
    common_lo, common_hi = common_temperature_interval(
        [c for c, zi in zip(components, composition) if zi > EPS]
    )
    if common_lo is not None:
        lo = max(lo, common_lo)
    if common_hi is not None:
        hi = min(hi, common_hi)
    if not lo < hi:
        raise ValueError(
            "No puede construirse un intervalo físico válido común para la raíz."
        )
    return lo, hi


def _check_bracket(
    f: Callable[[float], float], a: float, b: float
) -> tuple[float, float]:
    fa = f(a)
    fb = f(b)
    if not (math.isfinite(fa) and math.isfinite(fb)):
        raise ValueError("El residuo no es finito en los extremos del intervalo.")
    if abs(fa) < EPS:
        return fa, fb
    if abs(fb) < EPS:
        return fa, fb
    if fa * fb > 0:
        raise ValueError(
            "La función residual no cambia de signo dentro del intervalo físico. "
            "Revise datos, unidades, composición e intervalos de Antoine."
        )
    return fa, fb


def solve_bisection(
    f: Callable[[float], float],
    a: float,
    b: float,
    xtol: float,
    ftol: float,
    max_iter: int,
) -> RootResult:
    fa, fb = _check_bracket(f, a, b)
    if abs(fa) <= ftol:
        return RootResult(a, fa, 0, True, "bisección", 0)
    if abs(fb) <= ftol:
        return RootResult(b, fb, 0, True, "bisección", 0)

    x_old = None
    for it in range(1, max_iter + 1):
        x = 0.5 * (a + b)
        fx = f(x)
        if not math.isfinite(fx):
            raise ValueError("El residuo dejó de ser finito durante la bisección.")

        dx_ok = (x_old is not None and abs(x - x_old) <= xtol) or abs(b - a) <= 2 * xtol
        if abs(fx) <= ftol and dx_ok:
            return RootResult(x, fx, it, True, "bisección", 0)

        if fa * fx <= 0:
            b, fb = x, fx
        else:
            a, fa = x, fx
        x_old = x

    x = 0.5 * (a + b)
    fx = f(x)
    return RootResult(x, fx, max_iter, False, "bisección", 0)


def solve_secant_safeguarded(
    f: Callable[[float], float],
    a: float,
    b: float,
    xtol: float,
    ftol: float,
    max_iter: int,
) -> RootResult:
    fa, fb = _check_bracket(f, a, b)
    x0, f0 = a, fa
    x1, f1 = b, fb
    fallback = 0

    for it in range(1, max_iter + 1):
        denom = f1 - f0
        if abs(denom) <= EPS:
            x2 = 0.5 * (a + b)
            fallback += 1
        else:
            x2 = x1 - f1 * (x1 - x0) / denom
            if (not math.isfinite(x2)) or not (a < x2 < b):
                x2 = 0.5 * (a + b)
                fallback += 1

        f2 = f(x2)
        if not math.isfinite(f2):
            x2 = 0.5 * (a + b)
            f2 = f(x2)
            fallback += 1

        if abs(f2) <= ftol and abs(x2 - x1) <= xtol:
            return RootResult(x2, f2, it, True, "secante salvaguardada", fallback)

        if fa * f2 <= 0:
            b, fb = x2, f2
        else:
            a, fa = x2, f2

        x0, f0 = x1, f1
        x1, f1 = x2, f2

    return RootResult(x1, f1, max_iter, False, "secante salvaguardada", fallback)


def solve_newton_safeguarded(
    f: Callable[[float], float],
    df: Callable[[float], float],
    a: float,
    b: float,
    xtol: float,
    ftol: float,
    max_iter: int,
) -> RootResult:
    fa, fb = _check_bracket(f, a, b)
    if abs(fa) <= ftol:
        return RootResult(a, fa, 0, True, "Newton salvaguardado", 0)
    if abs(fb) <= ftol:
        return RootResult(b, fb, 0, True, "Newton salvaguardado", 0)

    x = 0.5 * (a + b)
    fx = f(x)
    fallback = 0
    previous_abs_f = abs(fx)

    for it in range(1, max_iter + 1):
        dfx = df(x)
        use_bisection = (
            (not math.isfinite(dfx))
            or abs(dfx) < 1.0e-14
        )

        if not use_bisection:
            candidate = x - fx / dfx
            if (not math.isfinite(candidate)) or not (a < candidate < b):
                use_bisection = True
        if use_bisection:
            candidate = 0.5 * (a + b)
            fallback += 1

        fc = f(candidate)
        if not math.isfinite(fc):
            candidate = 0.5 * (a + b)
            fc = f(candidate)
            fallback += 1

        # Si Newton empeora claramente el residuo, se sustituye por bisección.
        if (
            not use_bisection
            and abs(fc) > previous_abs_f * 1.25
            and abs(b - a) > xtol
        ):
            candidate = 0.5 * (a + b)
            fc = f(candidate)
            fallback += 1

        dx = abs(candidate - x)

        if fa * fc <= 0:
            b, fb = candidate, fc
        else:
            a, fa = candidate, fc

        if abs(fc) <= ftol and (dx <= xtol or abs(b - a) <= 2 * xtol):
            return RootResult(
                candidate, fc, it, True, "Newton salvaguardado", fallback
            )

        x, fx = candidate, fc
        previous_abs_f = abs(fc)

    return RootResult(x, fx, max_iter, False, "Newton salvaguardado", fallback)


def solve_root(
    f: Callable[[float], float],
    df: Callable[[float], float] | None,
    bracket: tuple[float, float],
    method: str = "auto",
    xtol: float = 1.0e-8,
    ftol: float = 1.0e-8,
    max_iter: int = 200,
) -> RootResult:
    a, b = bracket
    method = method.lower()

    if method == "bisection":
        result = solve_bisection(f, a, b, xtol, ftol, max_iter)
    elif method == "secant":
        result = solve_secant_safeguarded(f, a, b, xtol, ftol, max_iter)
    elif method == "newton":
        if df is None:
            raise ValueError("Newton requiere la derivada de la función residual.")
        result = solve_newton_safeguarded(f, df, a, b, xtol, ftol, max_iter)
    elif method == "auto":
        if df is not None:
            result = solve_newton_safeguarded(f, df, a, b, xtol, ftol, max_iter)
            if not result.converged:
                result = solve_bisection(f, a, b, xtol, ftol, max_iter)
        else:
            result = solve_secant_safeguarded(f, a, b, xtol, ftol, max_iter)
            if not result.converged:
                result = solve_bisection(f, a, b, xtol, ftol, max_iter)
    else:
        raise ValueError(f"Método desconocido: {method}")

    if not result.converged:
        raise RuntimeError(
            "No se alcanzó la convergencia con los criterios establecidos."
        )
    return result


# ---------------------------------------------------------------------------
# Temperaturas de burbuja y rocío
# ---------------------------------------------------------------------------

def bubble_temperature(
    components: Sequence[Component],
    x: Sequence[float],
    P: float,
    method: str = "auto",
    xtol: float = 1.0e-8,
    ftol: float | None = None,
    max_iter: int = 200,
) -> tuple[RootResult, list[float], list[float]]:
    x = validate_fraction_vector(x, "x_i")
    if len(components) != len(x):
        raise ValueError("El número de componentes no coincide con el número de x_i.")
    if P <= 0:
        raise ValueError("La presión debe ser positiva.")
    if ftol is None:
        ftol = max(1.0e-10, abs(P) * 1.0e-10)

    bracket = physical_temperature_bracket(components, P, x)

    def f(T: float) -> float:
        return sum(xi * c.psat(T) for xi, c in zip(x, components)
                   if xi > EPS) - P

    def df(T: float) -> float:
        return sum(xi * c.dpsat_dT(T) for xi, c in zip(x, components)
                   if xi > EPS)

    result = solve_root(f, df, bracket, method, xtol, ftol, max_iter)
    pstar = psats_presentes(components, result.root, x)
    y = [xi * pi / P if pi is not None else 0.0
         for xi, pi in zip(x, pstar)]
    y = validate_fraction_vector(y, "y_i calculadas")
    return result, pstar, y


def dew_temperature(
    components: Sequence[Component],
    y: Sequence[float],
    P: float,
    method: str = "auto",
    xtol: float = 1.0e-8,
    ftol: float = 1.0e-10,
    max_iter: int = 200,
) -> tuple[RootResult, list[float], list[float]]:
    y = validate_fraction_vector(y, "y_i")
    if len(components) != len(y):
        raise ValueError("El número de componentes no coincide con el número de y_i.")
    if P <= 0:
        raise ValueError("La presión debe ser positiva.")

    bracket = physical_temperature_bracket(components, P, y)

    def f(T: float) -> float:
        return sum(yi * P / c.psat(T) for yi, c in zip(y, components)
                   if yi > EPS) - 1.0

    def df(T: float) -> float:
        total = 0.0
        for yi, c in zip(y, components):
            if yi <= EPS:
                continue
            pi = c.psat(T)
            dpi = c.dpsat_dT(T)
            total += -yi * P * dpi / (pi * pi)
        return total

    result = solve_root(f, df, bracket, method, xtol, ftol, max_iter)
    pstar = psats_presentes(components, result.root, y)
    x = [yi * P / pi if pi is not None else 0.0
         for yi, pi in zip(y, pstar)]
    x = validate_fraction_vector(x, "x_i calculadas")
    return result, pstar, x


# ---------------------------------------------------------------------------
# Gráficos binarios
# ---------------------------------------------------------------------------

def _load_plotting():
    try:
        import numpy as np
        import matplotlib
        import matplotlib.pyplot as plt
        from matplotlib.ticker import FuncFormatter
    except ImportError as exc:
        raise RuntimeError(
            "Para generar diagramas se necesitan numpy y matplotlib."
        ) from exc

    matplotlib.rcParams["font.family"] = "Arial"
    matplotlib.rcParams["font.size"] = 10
    # Intenta mantener Arial también en las expresiones matemáticas.
    matplotlib.rcParams["mathtext.fontset"] = "custom"
    matplotlib.rcParams["mathtext.rm"] = "Arial"
    matplotlib.rcParams["mathtext.it"] = "Arial:italic"
    matplotlib.rcParams["mathtext.bf"] = "Arial:bold"
    return np, plt, FuncFormatter


def _apply_decimal_comma_ticks(ax, FuncFormatter) -> None:
    def comma_formatter(value, _position):
        # Evita -0 y usa coma decimal sin ceros innecesarios.
        if abs(value) < 5e-13:
            value = 0.0
        return f"{value:g}".replace(".", ",")

    formatter = FuncFormatter(comma_formatter)
    ax.xaxis.set_major_formatter(formatter)
    ax.yaxis.set_major_formatter(formatter)


def _binary_curves_from_pstar(pstar: Sequence[float], points: int = 201):
    pstar = validate_pstar(pstar)
    if len(pstar) != 2:
        raise ValueError("Se requieren exactamente dos P_i* para un diagrama binario.")
    np, _, _ = _load_plotting()
    p1, p2 = pstar
    x = np.linspace(0.0, 1.0, points)
    pb = x * p1 + (1.0 - x) * p2
    y_from_bubble = x * p1 / pb
    y = np.linspace(0.0, 1.0, points)
    pd = 1.0 / (y / p1 + (1.0 - y) / p2)
    return x, pb, y_from_bubble, y, pd


def _save_figure(fig, output: str | Path, dpi: int = 600) -> Path:
    path = Path(output)
    if path.suffix.lower() != ".png":
        path = path.with_suffix(".png")
    fig.savefig(
        path,
        dpi=dpi,
        transparent=True,
        bbox_inches="tight",
        pad_inches=0.05,
    )
    return path


def diagram_pxy(
    components: Sequence[Component],
    T: float,
    output: str | Path,
    dpi: int = 600,
    points: int = 201,
):
    if len(components) != 2:
        raise ValueError("El diagrama P-x-y solo se genera para mezclas binarias.")
    np, plt, FuncFormatter = _load_plotting()
    c1, c2 = components
    p1, p2 = c1.psat(T), c2.psat(T)

    x = np.linspace(0.0, 1.0, points)
    pb = x * p1 + (1.0 - x) * p2
    y_from_bubble = x * p1 / pb

    y = np.linspace(0.0, 1.0, points)
    pd = 1.0 / (y / p1 + (1.0 - y) / p2)

    fig, ax = plt.subplots(figsize=(6.5, 4.6))
    ax.plot(x, pb, label="Curva de burbuja")
    ax.plot(y, pd, label="Curva de rocío")
    ax.set_xlabel(f"Fracción molar de {c1.name}, $x_1$ (líquido) / $y_1$ (vapor)")
    ax.set_ylabel("P (kPa)")
    ax.set_xlim(0, 1)
    ax.legend()
    ax.grid(True, alpha=0.25)
    _apply_decimal_comma_ticks(ax, FuncFormatter)
    fig.tight_layout()
    path = _save_figure(fig, output, dpi)
    plt.close(fig)
    return path, (x, pb, y_from_bubble, y, pd)


def diagram_txy(
    components: Sequence[Component],
    P: float,
    output: str | Path,
    dpi: int = 600,
    points: int = 101,
    method: str = "auto",
):
    if len(components) != 2:
        raise ValueError("El diagrama T-x-y solo se genera para mezclas binarias.")
    np, plt, FuncFormatter = _load_plotting()
    c1, _ = components

    xgrid = np.linspace(0.0, 1.0, points)
    ygrid = np.linspace(0.0, 1.0, points)
    Tb = []
    Td = []

    for xv in xgrid:
        comp = [float(xv), float(1.0 - xv)]
        if xv <= EPS:
            Tb.append(components[1].boiling_temperature(P))
        elif xv >= 1.0 - EPS:
            Tb.append(components[0].boiling_temperature(P))
        else:
            r, _, _ = bubble_temperature(components, comp, P, method=method)
            Tb.append(r.root)

    for yv in ygrid:
        comp = [float(yv), float(1.0 - yv)]
        if yv <= EPS:
            Td.append(components[1].boiling_temperature(P))
        elif yv >= 1.0 - EPS:
            Td.append(components[0].boiling_temperature(P))
        else:
            r, _, _ = dew_temperature(components, comp, P, method=method)
            Td.append(r.root)

    fig, ax = plt.subplots(figsize=(6.5, 4.6))
    ax.plot(xgrid, Tb, label="Curva de burbuja")
    ax.plot(ygrid, Td, label="Curva de rocío")
    ax.set_xlabel(f"Fracción molar de {c1.name}, $x_1$ (líquido) / $y_1$ (vapor)")
    ax.set_ylabel("T (K)")
    ax.set_xlim(0, 1)
    ax.legend()
    ax.grid(True, alpha=0.25)
    _apply_decimal_comma_ticks(ax, FuncFormatter)
    fig.tight_layout()
    path = _save_figure(fig, output, dpi)
    plt.close(fig)
    return path, (xgrid, Tb, ygrid, Td)


def diagram_yx_at_pressure(
    components: Sequence[Component],
    P: float,
    output: str | Path,
    dpi: int = 600,
    points: int = 201,
    method: str = "auto",
):
    if len(components) != 2:
        raise ValueError("El diagrama y-x solo se genera para mezclas binarias.")
    np, plt, FuncFormatter = _load_plotting()
    c1, _ = components

    xgrid = np.linspace(0.0, 1.0, points)
    yvals = []
    for xv in xgrid:
        comp = [float(xv), float(1.0 - xv)]
        if xv <= EPS:
            yvals.append(0.0)
        elif xv >= 1.0 - EPS:
            yvals.append(1.0)
        else:
            r, pstar, _ = bubble_temperature(components, comp, P, method=method)
            yvals.append(comp[0] * pstar[0] / P)

    fig, ax = plt.subplots(figsize=(5.3, 5.0))
    ax.plot(xgrid, yvals, label="Equilibrio")
    ax.plot([0, 1], [0, 1], linestyle="--", label=r"$y_1=x_1$")
    ax.set_xlabel(f"$x_1$ ({c1.name}, líquido)")
    ax.set_ylabel(f"$y_1$ ({c1.name}, vapor)")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal", adjustable="box")
    ax.legend()
    ax.grid(True, alpha=0.25)
    _apply_decimal_comma_ticks(ax, FuncFormatter)
    fig.tight_layout()
    path = _save_figure(fig, output, dpi)
    plt.close(fig)
    return path, (xgrid, yvals)


def diagram_yx_at_temperature(
    components: Sequence[Component],
    T: float,
    output: str | Path,
    dpi: int = 600,
    points: int = 201,
):
    if len(components) != 2:
        raise ValueError("El diagrama y-x solo se genera para mezclas binarias.")
    np, plt, FuncFormatter = _load_plotting()
    c1, c2 = components
    p1, p2 = c1.psat(T), c2.psat(T)

    xgrid = np.linspace(0.0, 1.0, points)
    P = xgrid * p1 + (1.0 - xgrid) * p2
    yvals = xgrid * p1 / P

    fig, ax = plt.subplots(figsize=(5.3, 5.0))
    ax.plot(xgrid, yvals, label="Equilibrio")
    ax.plot([0, 1], [0, 1], linestyle="--", label=r"$y_1=x_1$")
    ax.set_xlabel(f"$x_1$ ({c1.name}, líquido)")
    ax.set_ylabel(f"$y_1$ ({c1.name}, vapor)")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal", adjustable="box")
    ax.legend()
    ax.grid(True, alpha=0.25)
    _apply_decimal_comma_ticks(ax, FuncFormatter)
    fig.tight_layout()
    path = _save_figure(fig, output, dpi)
    plt.close(fig)
    return path, (xgrid, yvals)


def diagram_pxy_from_pstar(
    names: Sequence[str],
    pstar: Sequence[float],
    output: str | Path,
    dpi: int = 600,
    points: int = 201,
):
    if len(names) != 2:
        raise ValueError("El diagrama P-x-y requiere exactamente dos nombres.")
    np, plt, FuncFormatter = _load_plotting()
    x, pb, y_from_bubble, y, pd = _binary_curves_from_pstar(pstar, points)
    fig, ax = plt.subplots(figsize=(6.5, 4.6))
    ax.plot(x, pb, label="Curva de burbuja")
    ax.plot(y, pd, label="Curva de rocío")
    ax.set_xlabel(f"Fracción molar de {names[0]}, $x_1$ (líquido) / $y_1$ (vapor)")
    ax.set_ylabel("P (kPa)")
    ax.set_xlim(0, 1)
    ax.legend()
    ax.grid(True, alpha=0.25)
    _apply_decimal_comma_ticks(ax, FuncFormatter)
    fig.tight_layout()
    path = _save_figure(fig, output, dpi)
    plt.close(fig)
    return path, (x, pb, y_from_bubble, y, pd)


def diagram_yx_from_pstar(
    names: Sequence[str],
    pstar: Sequence[float],
    output: str | Path,
    dpi: int = 600,
    points: int = 201,
):
    if len(names) != 2:
        raise ValueError("El diagrama y-x requiere exactamente dos nombres.")
    np, plt, FuncFormatter = _load_plotting()
    pstar = validate_pstar(pstar)
    if len(pstar) != 2:
        raise ValueError("El diagrama y-x requiere exactamente dos P_i*.")
    p1, p2 = pstar
    x = np.linspace(0.0, 1.0, points)
    P = x * p1 + (1.0 - x) * p2
    y = x * p1 / P
    fig, ax = plt.subplots(figsize=(5.3, 5.0))
    ax.plot(x, y, label="Equilibrio")
    ax.plot([0, 1], [0, 1], linestyle="--", label=r"$y_1=x_1$")
    ax.set_xlabel(f"$x_1$ ({names[0]}, líquido)")
    ax.set_ylabel(f"$y_1$ ({names[0]}, vapor)")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal", adjustable="box")
    ax.legend()
    ax.grid(True, alpha=0.25)
    _apply_decimal_comma_ticks(ax, FuncFormatter)
    fig.tight_layout()
    path = _save_figure(fig, output, dpi)
    plt.close(fig)
    return path, (x, y)


def diagram_from_pstar_table(
    names: Sequence[str],
    rows: Sequence[tuple[float, float, float]],
    P: float,
    output_txy: str | Path,
    output_yx: str | Path,
    dpi: int = 600,
):
    """
    Construye T-x-y e y-x a partir de una tabla (T, P_1*, P_2*) a P constante.
    Conserva solo filas físicamente pertenecientes al intervalo bifásico.
    """
    if len(names) != 2:
        raise ValueError("Se requieren exactamente dos componentes.")
    if P <= 0:
        raise ValueError("La presión debe ser positiva.")
    if len(rows) < 2:
        raise ValueError("Se requieren al menos dos filas de datos.")

    data = []
    for T, p1, p2 in rows:
        if T <= 0 or p1 <= 0 or p2 <= 0:
            raise ValueError("T y P_i* deben ser positivas en todas las filas.")
        if abs(p1 - p2) < 1.0e-14:
            continue
        x1 = (P - p2) / (p1 - p2)
        if -1.0e-10 <= x1 <= 1.0 + 1.0e-10:
            x1 = min(1.0, max(0.0, x1))
            y1 = x1 * p1 / P
            if -1.0e-10 <= y1 <= 1.0 + 1.0e-10:
                y1 = min(1.0, max(0.0, y1))
                data.append((T, x1, y1))
    if len(data) < 2:
        raise ValueError(
            "La tabla no contiene suficientes puntos físicos a la presión indicada."
        )
    data.sort(key=lambda r: r[1])
    Tvals = [r[0] for r in data]
    xvals = [r[1] for r in data]
    yvals = [r[2] for r in data]

    np, plt, FuncFormatter = _load_plotting()
    fig, ax = plt.subplots(figsize=(6.5, 4.6))
    ax.plot(xvals, Tvals, marker="o", label="Curva de burbuja")
    ax.plot(yvals, Tvals, marker="o", label="Curva de rocío")
    ax.set_xlabel(f"Fracción molar de {names[0]}, $x_1$ (líquido) / $y_1$ (vapor)")
    ax.set_ylabel("T (K)")
    ax.set_xlim(0, 1)
    ax.legend()
    ax.grid(True, alpha=0.25)
    _apply_decimal_comma_ticks(ax, FuncFormatter)
    fig.tight_layout()
    path_txy = _save_figure(fig, output_txy, dpi)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(5.3, 5.0))
    ax.plot(xvals, yvals, marker="o", label="Equilibrio")
    ax.plot([0, 1], [0, 1], linestyle="--", label=r"$y_1=x_1$")
    ax.set_xlabel(f"$x_1$ ({names[0]}, líquido)")
    ax.set_ylabel(f"$y_1$ ({names[0]}, vapor)")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal", adjustable="box")
    ax.legend()
    ax.grid(True, alpha=0.25)
    _apply_decimal_comma_ticks(ax, FuncFormatter)
    fig.tight_layout()
    path_yx = _save_figure(fig, output_yx, dpi)
    plt.close(fig)
    return path_txy, path_yx, data


# ---------------------------------------------------------------------------
# Presentación de resultados
# ---------------------------------------------------------------------------

def print_components_table(
    components: Sequence[Component],
    rows: Sequence[Sequence[float]],
    headers: Sequence[str],
    sig: int,
):
    widths = [max(len("Componente"), max(len(c.name) for c in components))]
    for j, header in enumerate(headers):
        col = [format_sig(row[j], sig) for row in rows]
        widths.append(max(len(header), max(len(v) for v in col)))

    head = ["Componente", *headers]
    print("  ".join(h.ljust(w) for h, w in zip(head, widths)))
    print("  ".join("-" * w for w in widths))
    for comp, row in zip(components, rows):
        vals = [comp.name] + [format_sig(v, sig) for v in row]
        print("  ".join(v.ljust(w) for v, w in zip(vals, widths)))


def print_named_table(
    names: Sequence[str],
    rows: Sequence[Sequence[float]],
    headers: Sequence[str],
    sig: int,
):
    if len(names) != len(rows):
        raise ValueError("El número de nombres no coincide con el número de filas.")
    widths = [max(len("Componente"), max(len(n) for n in names))]
    for j, header in enumerate(headers):
        col = [format_sig(row[j], sig) for row in rows]
        widths.append(max(len(header), max(len(v) for v in col)))
    head = ["Componente", *headers]
    print("  ".join(h.ljust(w) for h, w in zip(head, widths)))
    print("  ".join("-" * w for w in widths))
    for name, row in zip(names, rows):
        vals = [name] + [format_sig(v, sig) for v in row]
        print("  ".join(v.ljust(w) for v, w in zip(vals, widths)))


def show_root_info(result: RootResult, sig: int, verbose: bool):
    print(f"Residuo final: {format_sig(result.residual, max(sig, 4))}")
    print("Convergencia: correcta")
    if verbose:
        print(f"Método interno: {result.method_used}")
        print(f"Iteraciones: {result.iterations}")
        print(f"Pasos de respaldo: {result.fallback_count}")


# ---------------------------------------------------------------------------
# Entrada interactiva
# ---------------------------------------------------------------------------

def ask(prompt: str) -> str:
    return input(prompt).strip()


def ask_float(prompt: str, positive: bool = False) -> float:
    while True:
        try:
            value = parse_decimal(ask(prompt))
            if positive and value <= 0:
                raise ValueError("Debe ser positivo.")
            return value
        except ValueError as exc:
            print(f"Entrada no válida: {exc}")


def ask_int(prompt: str, minimum: int = 1) -> int:
    while True:
        try:
            value = int(ask(prompt))
            if value < minimum:
                raise ValueError
            return value
        except ValueError:
            print(f"Introduzca un entero >= {minimum}.")


def ask_components(require_ranges: bool = True) -> list[Component]:
    n = ask_int("Número de componentes: ", 2)
    comps = []
    print(
        "\nEcuación de Antoine: log10(P*) = A - B/(T + C), "
        "con P* en kPa y T en K."
    )
    print("Si su ecuación usa T - c, introduzca C = -c.\n")
    for i in range(n):
        name = ask(f"Nombre del componente {i+1}: ") or f"Componente {i+1}"
        A = ask_float("  A = ")
        B = ask_float("  B = ")
        C = ask_float("  C = ")
        Tmin = Tmax = None
        if require_ranges:
            print("  Intervalo de validez de Antoine:")
            Tmin = ask_float("    Tmin (K) = ")
            Tmax = ask_float("    Tmax (K) = ")
            if Tmin >= Tmax:
                raise ValueError("Tmin debe ser menor que Tmax.")
        comps.append(Component(name, A, B, C, Tmin, Tmax))
    return comps


def ask_composition(components: Sequence[Component], symbol: str) -> list[float]:
    vals = []
    print(f"\nIntroduzca las fracciones molares {symbol}:")
    for c in components:
        vals.append(ask_float(f"  {symbol}({c.name}) = "))
    return validate_fraction_vector(vals, symbol)


def ask_names_and_pstar() -> tuple[list[str], list[float]]:
    n = ask_int("Número de componentes: ", 2)
    names = []
    pstar = []
    for i in range(n):
        name = ask(f"Nombre del componente {i+1}: ") or f"Componente {i+1}"
        names.append(name)
        pstar.append(ask_float(f"  P*({name}) [kPa] = ", positive=True))
    return names, pstar


def ask_composition_names(names: Sequence[str], symbol: str) -> list[float]:
    vals = []
    print(f"\nIntroduzca las fracciones molares {symbol}:")
    for name in names:
        vals.append(ask_float(f"  {symbol}({name}) = "))
    return validate_fraction_vector(vals, symbol)


def interactive_pstar_mode(sig: int) -> None:
    names, pstar = ask_names_and_pstar()
    print("\n1. Ley de Raoult / presión de burbuja a partir de x_i")
    print("2. Presión de rocío a partir de y_i")
    print("3. x_i e y_i a P conocida (solo binaria)")
    print("4. Diagrama P-x-y (solo binaria)")
    print("5. Diagrama y-x (solo binaria)")
    sub = ask("Opción: ")

    if sub == "1":
        x = ask_composition_names(names, "x")
        data = raoult_from_pstar(x, pstar)
        print(f"\nP = {format_sig(data['P'], sig)} kPa")
        rows = [[xi, ps, pp, yi, ki] for xi, ps, pp, yi, ki in zip(
            data["x"], data["psat"], data["partial"], data["y"], data["K"])]
        print_named_table(names, rows,
                          ["x_i", "P_i* (kPa)", "p_i (kPa)", "y_i", "K_i"], sig)
    elif sub == "2":
        y = ask_composition_names(names, "y")
        P, x = dew_from_pstar(y, pstar)
        print(f"\nP_rocío = {format_sig(P, sig)} kPa")
        rows = [[yi, ps, xi] for yi, ps, xi in zip(y, pstar, x)]
        print_named_table(names, rows, ["y_i", "P_i* (kPa)", "x_i"], sig)
    elif sub == "3":
        if len(names) != 2:
            raise ValueError("Este cálculo requiere exactamente dos componentes.")
        P = ask_float("P total (kPa): ", positive=True)
        x, y = binary_state_from_pstar_pressure(pstar, P)
        rows = [[x[i], pstar[i], y[i]] for i in range(2)]
        print_named_table(names, rows, ["x_i", "P_i* (kPa)", "y_i"], sig)
    elif sub == "4":
        if len(names) != 2:
            raise ValueError("El diagrama P-x-y requiere exactamente dos componentes.")
        output = ask("Nombre del PNG [diagrama_Pxy.png]: ") or "diagrama_Pxy.png"
        path, _ = diagram_pxy_from_pstar(names, pstar, output)
        print(f"Figura guardada: {path}")
    elif sub == "5":
        if len(names) != 2:
            raise ValueError("El diagrama y-x requiere exactamente dos componentes.")
        output = ask("Nombre del PNG [diagrama_yx.png]: ") or "diagrama_yx.png"
        path, _ = diagram_yx_from_pstar(names, pstar, output)
        print(f"Figura guardada: {path}")
    else:
        raise ValueError("Opción no reconocida.")


def interactive_table_mode() -> None:
    name1 = ask("Nombre del componente 1: ") or "Componente 1"
    name2 = ask("Nombre del componente 2: ") or "Componente 2"
    P = ask_float("P total constante (kPa): ", positive=True)
    n = ask_int("Número de filas de la tabla: ", 2)
    rows = []
    for i in range(n):
        print(f"Fila {i+1}:")
        T = ask_float("  T (K) = ", positive=True)
        p1 = ask_float(f"  P*({name1}) (kPa) = ", positive=True)
        p2 = ask_float(f"  P*({name2}) (kPa) = ", positive=True)
        rows.append((T, p1, p2))
    out1 = ask("PNG T-x-y [diagrama_Txy_tabla.png]: ") or "diagrama_Txy_tabla.png"
    out2 = ask("PNG y-x [diagrama_yx_tabla.png]: ") or "diagrama_yx_tabla.png"
    p1, p2, data = diagram_from_pstar_table([name1, name2], rows, P, out1, out2)
    print(f"Figuras guardadas: {p1} ; {p2}")
    print(f"Puntos físicos utilizados: {len(data)}")


def interactive_menu():
    sig = 5
    method = "auto"
    verbose = False

    while True:
        print("\nEQUILIBRIO LÍQUIDO-VAPOR IDEAL — CAPÍTULO 7")
        print("=" * 51)
        print("1. Ley de Raoult")
        print("2. Presión de burbuja a T conocida")
        print("3. Temperatura de burbuja a P conocida")
        print("4. Presión de rocío a T conocida")
        print("5. Temperatura de rocío a P conocida")
        print("6. Coeficiente K y volatilidad relativa")
        print("7. Diagrama P-x-y (binario)")
        print("8. Diagrama T-x-y (binario)")
        print("9. Diagrama y-x (binario)")
        print("10. Cálculos con P_i* conocidas (sin Antoine)")
        print("11. Diagramas T-x-y e y-x desde tabla P_i*(T)")
        print("0. Salir")

        option = ask("\nOpción: ")

        try:
            if option == "0":
                return

            if option == "10":
                interactive_pstar_mode(sig)
                continue

            if option == "11":
                interactive_table_mode()
                continue

            if option not in {"1", "2", "3", "4", "5", "6", "7", "8", "9"}:
                print("Opción no reconocida.")
                continue

            if option in {"1", "2", "4", "6", "7"}:
                comps = ask_components(require_ranges=False)
            else:
                comps = ask_components(require_ranges=True)

            if option == "1":
                T = ask_float("T (K): ", positive=True)
                x = ask_composition(comps, "x")
                data = raoult(comps, x, T)
                print(f"\nPresión total: {format_sig(data['P'], sig)} kPa")
                rows = [
                    [xi, ps, pp, yi, ki]
                    for xi, ps, pp, yi, ki in zip(
                        data["x"], data["psat"], data["partial"], data["y"], data["K"]
                    )
                ]
                print_components_table(
                    comps, rows, ["x_i", "P_i* (kPa)", "p_i (kPa)", "y_i", "K_i"], sig
                )

            elif option == "2":
                T = ask_float("T (K): ", positive=True)
                x = ask_composition(comps, "x")
                P, partial, y = bubble_pressure(comps, x, T)
                print(f"\nP_burbuja = {format_sig(P, sig)} kPa")
                pstar = psats_presentes(comps, T, x)
                rows = [[xi, ps, pp, yi] for xi, ps, pp, yi in zip(x, pstar, partial, y)]
                print_components_table(
                    comps, rows, ["x_i", "P_i* (kPa)", "p_i (kPa)", "y_i"], sig
                )

            elif option == "3":
                P = ask_float("P (kPa): ", positive=True)
                x = ask_composition(comps, "x")
                result, pstar, y = bubble_temperature(comps, x, P, method=method)
                print(f"\nT_burbuja = {format_sig(result.root, sig)} K")
                rows = [[xi, ps, yi] for xi, ps, yi in zip(x, pstar, y)]
                print_components_table(comps, rows, ["x_i", "P_i* (kPa)", "y_i"], sig)
                show_root_info(result, sig, verbose)

            elif option == "4":
                T = ask_float("T (K): ", positive=True)
                y = ask_composition(comps, "y")
                P, x = dew_pressure(comps, y, T)
                pstar = psats_presentes(comps, T, y)
                print(f"\nP_rocío = {format_sig(P, sig)} kPa")
                rows = [[yi, ps, xi] for yi, ps, xi in zip(y, pstar, x)]
                print_components_table(comps, rows, ["y_i", "P_i* (kPa)", "x_i"], sig)

            elif option == "5":
                P = ask_float("P (kPa): ", positive=True)
                y = ask_composition(comps, "y")
                result, pstar, x = dew_temperature(comps, y, P, method=method)
                print(f"\nT_rocío = {format_sig(result.root, sig)} K")
                rows = [[yi, ps, xi] for yi, ps, xi in zip(y, pstar, x)]
                print_components_table(comps, rows, ["y_i", "P_i* (kPa)", "x_i"], sig)
                show_root_info(result, sig, verbose)

            elif option == "6":
                T = ask_float("T (K): ", positive=True)
                pstar = psats(comps, T)
                P = ask_float("P total (kPa): ", positive=True)
                K = [p / P for p in pstar]
                print()
                rows = [[ps, ki] for ps, ki in zip(pstar, K)]
                print_components_table(comps, rows, ["P_i* (kPa)", "K_i"], sig)
                i = ask_int("Índice del componente i para α_ij (1..N): ", 1) - 1
                j = ask_int("Índice del componente j para α_ij (1..N): ", 1) - 1
                alpha = relative_volatility(comps, T, i, j)
                print(
                    f"α({comps[i].name}/{comps[j].name}) = "
                    f"{format_sig(alpha, sig)}"
                )

            elif option == "7":
                if len(comps) != 2:
                    raise ValueError("El diagrama P-x-y requiere exactamente 2 componentes.")
                T = ask_float("T (K): ", positive=True)
                output = ask("Nombre del PNG [diagrama_Pxy.png]: ") or "diagrama_Pxy.png"
                path, _ = diagram_pxy(comps, T, output)
                print(f"Figura guardada: {path}")

            elif option == "8":
                if len(comps) != 2:
                    raise ValueError("El diagrama T-x-y requiere exactamente 2 componentes.")
                P = ask_float("P (kPa): ", positive=True)
                output = ask("Nombre del PNG [diagrama_Txy.png]: ") or "diagrama_Txy.png"
                path, _ = diagram_txy(comps, P, output, method=method)
                print(f"Figura guardada: {path}")

            elif option == "9":
                if len(comps) != 2:
                    raise ValueError("El diagrama y-x requiere exactamente 2 componentes.")
                mode = ask("Condición fija: [P]resión o [T]emperatura? ").lower()
                output = ask("Nombre del PNG [diagrama_yx.png]: ") or "diagrama_yx.png"
                if mode.startswith("p"):
                    P = ask_float("P (kPa): ", positive=True)
                    path, _ = diagram_yx_at_pressure(comps, P, output, method=method)
                elif mode.startswith("t"):
                    T = ask_float("T (K): ", positive=True)
                    path, _ = diagram_yx_at_temperature(comps, T, output)
                else:
                    raise ValueError("Elija P o T.")
                print(f"Figura guardada: {path}")

            else:
                print("Opción no reconocida.")

        except (ValueError, RuntimeError, IndexError) as exc:
            print(f"\nERROR: {exc}")


# ---------------------------------------------------------------------------
# Línea de comandos
# ---------------------------------------------------------------------------

def add_common_component_args(parser, need_ranges: bool = False):
    parser.add_argument(
        "--component",
        action="append",
        required=True,
        help=(
            "Componente como 'NOMBRE;A;B;C' o "
            "'NOMBRE;A;B;C;Tmin;Tmax'. Repetir una vez por componente."
        ),
    )
    parser.add_argument(
        "--sig",
        type=int,
        default=5,
        help="Cifras significativas mostradas (predeterminado: 5).",
    )
    if need_ranges:
        parser.epilog = (
            "Para cálculos iterativos de temperatura se recomienda especificar "
            "Tmin y Tmax para cada correlación de Antoine."
        )


def add_solver_args(parser):
    parser.add_argument(
        "--method",
        choices=["auto", "bisection", "secant", "newton"],
        default="auto",
        help="Método numérico; 'auto' usa estrategia salvaguardada.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Muestra método interno, iteraciones y pasos de respaldo.",
    )


def add_direct_pstar_args(parser, require_composition: str | None = None):
    parser.add_argument(
        "--pstar", action="append", required=True,
        help="Presión de vapor P_i* en kPa; repetir una vez por componente."
    )
    parser.add_argument(
        "--name", action="append",
        help="Nombre del componente; repetir en el mismo orden que --pstar."
    )
    if require_composition == "x":
        parser.add_argument("--x", action="append", required=True)
    elif require_composition == "y":
        parser.add_argument("--y", action="append", required=True)
    parser.add_argument("--sig", type=int, default=5)


def direct_names(args, n: int) -> list[str]:
    if args.name is None:
        return [f"Componente {i+1}" for i in range(n)]
    if len(args.name) != n:
        raise ValueError("Debe introducir un --name por cada --pstar.")
    return list(args.name)


def parse_table_rows(specs: Sequence[str]) -> list[tuple[float, float, float]]:
    rows = []
    for spec in specs:
        parts = [p.strip() for p in spec.split(";")]
        if len(parts) != 3:
            raise ValueError("Cada --row debe tener el formato 'T;P1*;P2*'.")
        T, p1, p2 = map(parse_decimal, parts)
        rows.append((T, p1, p2))
    return rows


def build_parser():
    parser = argparse.ArgumentParser(
        description=(
            "Cálculo de equilibrio líquido-vapor ideal, puntos de burbuja y rocío "
            "y diagramas binarios del capítulo 7."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("raoult", help="Ley de Raoult a temperatura conocida.")
    add_common_component_args(p)
    p.add_argument("--x", action="append", required=True, help="Fracción molar líquida.")
    p.add_argument("--T", required=True, help="Temperatura en K.")

    p = sub.add_parser("bubble-p", help="Presión de burbuja a T conocida.")
    add_common_component_args(p)
    p.add_argument("--x", action="append", required=True)
    p.add_argument("--T", required=True)

    p = sub.add_parser("bubble-t", help="Temperatura de burbuja a P conocida.")
    add_common_component_args(p, need_ranges=True)
    add_solver_args(p)
    p.add_argument("--x", action="append", required=True)
    p.add_argument("--P", required=True, help="Presión total en kPa.")

    p = sub.add_parser("dew-p", help="Presión de rocío a T conocida.")
    add_common_component_args(p)
    p.add_argument("--y", action="append", required=True)
    p.add_argument("--T", required=True)

    p = sub.add_parser("dew-t", help="Temperatura de rocío a P conocida.")
    add_common_component_args(p, need_ranges=True)
    add_solver_args(p)
    p.add_argument("--y", action="append", required=True)
    p.add_argument("--P", required=True)

    p = sub.add_parser("alpha", help="K_i y volatilidad relativa α_ij.")
    add_common_component_args(p)
    p.add_argument("--T", required=True)
    p.add_argument("--P", required=True)
    p.add_argument("--i", type=int, required=True, help="Índice i, comenzando en 1.")
    p.add_argument("--j", type=int, required=True, help="Índice j, comenzando en 1.")

    p = sub.add_parser("diagram-pxy", help="Diagrama P-x-y binario.")
    add_common_component_args(p)
    p.add_argument("--T", required=True)
    p.add_argument("--output", default="diagrama_Pxy.png")
    p.add_argument("--dpi", type=int, default=600)
    p.add_argument("--points", type=int, default=201)

    p = sub.add_parser("diagram-txy", help="Diagrama T-x-y binario.")
    add_common_component_args(p, need_ranges=True)
    add_solver_args(p)
    p.add_argument("--P", required=True)
    p.add_argument("--output", default="diagrama_Txy.png")
    p.add_argument("--dpi", type=int, default=600)
    p.add_argument("--points", type=int, default=101)

    p = sub.add_parser("diagram-yx", help="Diagrama y-x binario.")
    add_common_component_args(p, need_ranges=True)
    add_solver_args(p)
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--P", help="Presión constante en kPa.")
    group.add_argument("--T", help="Temperatura constante en K.")
    p.add_argument("--output", default="diagrama_yx.png")
    p.add_argument("--dpi", type=int, default=600)
    p.add_argument("--points", type=int, default=201)

    p = sub.add_parser(
        "raoult-pstar",
        help="Ley de Raoult con P_i* introducidas directamente."
    )
    add_direct_pstar_args(p, require_composition="x")

    p = sub.add_parser(
        "dew-p-pstar",
        help="Presión de rocío con P_i* introducidas directamente."
    )
    add_direct_pstar_args(p, require_composition="y")

    p = sub.add_parser(
        "state-pstar",
        help="x_i e y_i binarias a P conocida usando P_1* y P_2*."
    )
    add_direct_pstar_args(p)
    p.add_argument("--P", required=True, help="Presión total en kPa.")

    p = sub.add_parser(
        "diagram-pxy-pstar",
        help="Diagrama P-x-y binario a partir de P_1* y P_2*."
    )
    add_direct_pstar_args(p)
    p.add_argument("--output", default="diagrama_Pxy.png")
    p.add_argument("--dpi", type=int, default=600)
    p.add_argument("--points", type=int, default=201)

    p = sub.add_parser(
        "diagram-yx-pstar",
        help="Diagrama y-x binario a partir de P_1* y P_2*."
    )
    add_direct_pstar_args(p)
    p.add_argument("--output", default="diagrama_yx.png")
    p.add_argument("--dpi", type=int, default=600)
    p.add_argument("--points", type=int, default=201)

    p = sub.add_parser(
        "diagram-table",
        help="Genera T-x-y e y-x desde una tabla T;P_1*;P_2*."
    )
    p.add_argument("--name", action="append", required=True,
                   help="Dos nombres de componentes.")
    p.add_argument("--P", required=True, help="Presión total constante, kPa.")
    p.add_argument("--row", action="append", required=True,
                   help="Fila 'T;P1*;P2*'; repetir para cada temperatura.")
    p.add_argument("--output-txy", default="diagrama_Txy_tabla.png")
    p.add_argument("--output-yx", default="diagrama_yx_tabla.png")
    p.add_argument("--dpi", type=int, default=600)
    p.add_argument("--sig", type=int, default=5)

    return parser


def parse_components_from_args(args) -> list[Component]:
    comps = [parse_component(s) for s in args.component]
    if len(comps) < 2:
        raise ValueError("Se requieren al menos dos componentes.")
    return comps


def main_cli(args):
    sig = args.sig
    cmd = args.command

    direct_commands = {
        "raoult-pstar", "dew-p-pstar", "state-pstar",
        "diagram-pxy-pstar", "diagram-yx-pstar", "diagram-table"
    }

    if cmd == "raoult-pstar":
        pstar = validate_pstar([parse_decimal(v) for v in args.pstar])
        names = direct_names(args, len(pstar))
        x = validate_fraction_vector([parse_decimal(v) for v in args.x], "x_i")
        data = raoult_from_pstar(x, pstar)
        print(f"P = {format_sig(data['P'], sig)} kPa")
        rows = [[xi, ps, pp, yi, ki] for xi, ps, pp, yi, ki in zip(
            data["x"], data["psat"], data["partial"], data["y"], data["K"])]
        print_named_table(names, rows,
                          ["x_i", "P_i* (kPa)", "p_i (kPa)", "y_i", "K_i"], sig)
        return

    if cmd == "dew-p-pstar":
        pstar = validate_pstar([parse_decimal(v) for v in args.pstar])
        names = direct_names(args, len(pstar))
        y = validate_fraction_vector([parse_decimal(v) for v in args.y], "y_i")
        P, x = dew_from_pstar(y, pstar)
        print(f"P_rocío = {format_sig(P, sig)} kPa")
        rows = [[yi, ps, xi] for yi, ps, xi in zip(y, pstar, x)]
        print_named_table(names, rows, ["y_i", "P_i* (kPa)", "x_i"], sig)
        return

    if cmd == "state-pstar":
        pstar = validate_pstar([parse_decimal(v) for v in args.pstar])
        names = direct_names(args, len(pstar))
        P = parse_decimal(args.P)
        x, y = binary_state_from_pstar_pressure(pstar, P)
        rows = [[x[i], pstar[i], y[i]] for i in range(2)]
        print_named_table(names, rows, ["x_i", "P_i* (kPa)", "y_i"], sig)
        return

    if cmd == "diagram-pxy-pstar":
        pstar = validate_pstar([parse_decimal(v) for v in args.pstar])
        names = direct_names(args, len(pstar))
        path, _ = diagram_pxy_from_pstar(names, pstar, args.output, args.dpi, args.points)
        print(f"Figura guardada: {path}")
        return

    if cmd == "diagram-yx-pstar":
        pstar = validate_pstar([parse_decimal(v) for v in args.pstar])
        names = direct_names(args, len(pstar))
        path, _ = diagram_yx_from_pstar(names, pstar, args.output, args.dpi, args.points)
        print(f"Figura guardada: {path}")
        return

    if cmd == "diagram-table":
        if len(args.name) != 2:
            raise ValueError("--name debe indicarse exactamente dos veces.")
        rows = parse_table_rows(args.row)
        P = parse_decimal(args.P)
        p1, p2, data = diagram_from_pstar_table(
            args.name, rows, P, args.output_txy, args.output_yx, args.dpi
        )
        print(f"Figuras guardadas: {p1} ; {p2}")
        print(f"Puntos físicos utilizados: {len(data)}")
        return

    if cmd not in direct_commands:
        comps = parse_components_from_args(args)

    if cmd == "raoult":
        x = validate_fraction_vector([parse_decimal(v) for v in args.x], "x_i")
        T = parse_decimal(args.T)
        data = raoult(comps, x, T)
        print(f"P = {format_sig(data['P'], sig)} kPa")
        rows = [
            [xi, ps, pp, yi, ki]
            for xi, ps, pp, yi, ki in zip(
                data["x"], data["psat"], data["partial"], data["y"], data["K"]
            )
        ]
        print_components_table(
            comps, rows, ["x_i", "P_i* (kPa)", "p_i (kPa)", "y_i", "K_i"], sig
        )

    elif cmd == "bubble-p":
        x = validate_fraction_vector([parse_decimal(v) for v in args.x], "x_i")
        T = parse_decimal(args.T)
        P, partial, y = bubble_pressure(comps, x, T)
        pstar = psats_presentes(comps, T, x)
        print(f"P_burbuja = {format_sig(P, sig)} kPa")
        rows = [[xi, ps, pp, yi] for xi, ps, pp, yi in zip(x, pstar, partial, y)]
        print_components_table(
            comps, rows, ["x_i", "P_i* (kPa)", "p_i (kPa)", "y_i"], sig
        )

    elif cmd == "bubble-t":
        x = validate_fraction_vector([parse_decimal(v) for v in args.x], "x_i")
        P = parse_decimal(args.P)
        result, pstar, y = bubble_temperature(comps, x, P, method=args.method)
        print(f"T_burbuja = {format_sig(result.root, sig)} K")
        rows = [[xi, ps, yi] for xi, ps, yi in zip(x, pstar, y)]
        print_components_table(comps, rows, ["x_i", "P_i* (kPa)", "y_i"], sig)
        show_root_info(result, sig, args.verbose)

    elif cmd == "dew-p":
        y = validate_fraction_vector([parse_decimal(v) for v in args.y], "y_i")
        T = parse_decimal(args.T)
        P, x = dew_pressure(comps, y, T)
        pstar = psats_presentes(comps, T, y)
        print(f"P_rocío = {format_sig(P, sig)} kPa")
        rows = [[yi, ps, xi] for yi, ps, xi in zip(y, pstar, x)]
        print_components_table(comps, rows, ["y_i", "P_i* (kPa)", "x_i"], sig)

    elif cmd == "dew-t":
        y = validate_fraction_vector([parse_decimal(v) for v in args.y], "y_i")
        P = parse_decimal(args.P)
        result, pstar, x = dew_temperature(comps, y, P, method=args.method)
        print(f"T_rocío = {format_sig(result.root, sig)} K")
        rows = [[yi, ps, xi] for yi, ps, xi in zip(y, pstar, x)]
        print_components_table(comps, rows, ["y_i", "P_i* (kPa)", "x_i"], sig)
        show_root_info(result, sig, args.verbose)

    elif cmd == "alpha":
        T = parse_decimal(args.T)
        P = parse_decimal(args.P)
        pstar = psats(comps, T)
        K = [p / P for p in pstar]
        rows = [[ps, ki] for ps, ki in zip(pstar, K)]
        print_components_table(comps, rows, ["P_i* (kPa)", "K_i"], sig)
        i, j = args.i - 1, args.j - 1
        alpha = relative_volatility(comps, T, i, j)
        print(
            f"α({comps[i].name}/{comps[j].name}) = {format_sig(alpha, sig)}"
        )

    elif cmd == "diagram-pxy":
        T = parse_decimal(args.T)
        path, _ = diagram_pxy(comps, T, args.output, args.dpi, args.points)
        print(f"Figura guardada: {path}")

    elif cmd == "diagram-txy":
        P = parse_decimal(args.P)
        path, _ = diagram_txy(
            comps, P, args.output, args.dpi, args.points, args.method
        )
        print(f"Figura guardada: {path}")

    elif cmd == "diagram-yx":
        if args.P is not None:
            P = parse_decimal(args.P)
            path, _ = diagram_yx_at_pressure(
                comps, P, args.output, args.dpi, args.points, args.method
            )
        else:
            T = parse_decimal(args.T)
            path, _ = diagram_yx_at_temperature(
                comps, T, args.output, args.dpi, args.points
            )
        print(f"Figura guardada: {path}")


def main():
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command is None:
            interactive_menu()
        else:
            main_cli(args)
    except (ValueError, RuntimeError, IndexError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(2)
    except KeyboardInterrupt:
        print("\nOperación cancelada por el usuario.", file=sys.stderr)
        sys.exit(130)


if __name__ == "__main__":
    main()
