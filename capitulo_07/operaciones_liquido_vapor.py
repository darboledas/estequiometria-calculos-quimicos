#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
operaciones_vle_ideal.py
========================

Herramienta de cálculo para operaciones de equilibrio líquido-vapor del
capítulo 7.

Incluye:
    1) Regla de la palanca / balance de fases:
       - binaria y multicomponente;
       - fracción líquida y fracción vapor;
       - cantidades molares de cada fase;
       - cantidad de cada componente en cada fase;
       - porcentaje de cada componente recuperado en líquido y vapor;
       - comprobación de balances.

    2) Vaporización flash:
       - binaria y multicomponente;
       - entrada directa de K_i;
       - o cálculo de K_i = P_i*(T)/P mediante Antoine para mezcla ideal;
       - clasificación automática: líquido, vapor, punto de burbuja,
         punto de rocío o región bifásica;
       - resolución de Rachford-Rice con método salvaguardado;
       - comprobación de normalización y balances;
       - composición másica opcional si se proporcionan masas molares.

    3) Destilación simple o diferencial (Rayleigh), binaria:
       - volatilidad relativa constante;
       - cálculo de líquido residual, destilado total, composición media
         del destilado y recuperación del componente más volátil;
       - posibilidad de calcular la composición final del residuo a partir
         de una cantidad residual objetivo.

    4) Vaporizaciones-condensaciones ideales sucesivas, binaria:
       - modelo con volatilidad relativa constante;
       - útil para estudiar el enriquecimiento por etapas;
       - no representa una columna de destilación completa.

Hipótesis:
    - Equilibrio líquido-vapor ideal cuando se usa Antoine:
          K_i = P_i*(T) / P
    - Antoine:
          log10(P_i*) = A_i - B_i / (T + C_i)
      con P_i* en kPa y T en K.
      Si la correlación aparece como T - c, introduzca C = -c.
    - La destilación diferencial se limita a sistemas binarios y utiliza
      una volatilidad relativa constante, tal como se plantea en los
      ejercicios del capítulo.

Resolución numérica:
    - Rachford-Rice se resuelve exclusivamente dentro de 0 <= beta <= 1.
    - Se intenta Newton salvaguardado.
    - Si el paso sale del intervalo, la derivada no es adecuada, aparece
      una anomalía numérica o el residuo empeora, se usa bisección.
    - La convergencia exige simultáneamente tolerancia en beta y en el
      residuo.
    - Si no existe raíz bifásica, el programa no la fuerza: identifica la
      alimentación como monofásica o situada sobre una frontera de fase.

Entrada decimal:
    - En modo interactivo se aceptan coma o punto decimal.
    - En línea de comandos también se aceptan ambos formatos.
Salida:
    - Se utiliza coma decimal.

Ejemplos:
    python operaciones_vle_ideal.py
    python operaciones_vle_ideal.py --help

    python operaciones_vle_ideal.py flash-k \
        --z 0,20 --z 0,50 --z 0,30 \
        --K 2,584 --K 1,239 --K 0,408 \
        --F 100

    python operaciones_vle_ideal.py rayleigh-alpha \
        --F0 100,0 --x0 0,60 --xf 0,45 --alpha 1,43

Dependencias:
    - Solo biblioteca estándar de Python.

Autoría:
    Material complementario del capítulo 7.
"""

from __future__ import annotations

import argparse
import math
import sys
from dataclasses import dataclass
from typing import Callable, Sequence


EPS = 1.0e-12


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def parse_decimal(value: str | float | int) -> float:
    """Convierte un número con coma o punto decimal a float."""
    text = str(value).strip().replace(" ", "").replace(",", ".")
    try:
        result = float(text)
    except ValueError as exc:
        raise ValueError(f"No se reconoce como número: {value!r}") from exc
    if not math.isfinite(result):
        raise ValueError("El dato debe ser un número finito.")
    return result


def format_sig(value: float, sig: int = 5) -> str:
    """Formatea con cifras significativas y coma decimal."""
    if not math.isfinite(value):
        return str(value)
    if value == 0:
        return "0"
    s = f"{value:.{max(1, sig)}g}"
    if "e" in s:
        mantissa, exponent = s.split("e")
        mantissa = mantissa.replace(".", ",")
        return f"{mantissa}×10^{int(exponent)}"
    return s.replace(".", ",")


def validate_fraction_vector(
    values: Sequence[float],
    label: str,
    *,
    minimum_length: int = 2
) -> list[float]:
    vals = [float(v) for v in values]
    if len(vals) < minimum_length:
        raise ValueError(f"Se requieren al menos {minimum_length} valores {label}.")
    if any((not math.isfinite(v)) or v < -EPS or v > 1.0 + EPS for v in vals):
        raise ValueError(f"Todas las fracciones {label} deben estar entre 0 y 1.")
    total = sum(vals)
    if total <= EPS:
        raise ValueError(f"La suma de {label} debe ser positiva.")
    if abs(total - 1.0) > 1.0e-6:
        raise ValueError(
            f"Las fracciones {label} deben sumar 1. "
            f"Suma introducida = {total:.10g}."
        )
    return [max(0.0, min(1.0, v / total)) for v in vals]


def validate_positive_vector(values: Sequence[float], label: str) -> list[float]:
    vals = [float(v) for v in values]
    if any((not math.isfinite(v)) or v <= 0 for v in vals):
        raise ValueError(f"Todos los valores {label} deben ser positivos.")
    return vals


def percent(value: float) -> float:
    return 100.0 * value


# ---------------------------------------------------------------------------
# Antoine
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Component:
    name: str
    A: float
    B: float
    C: float
    Tmin: float | None = None
    Tmax: float | None = None

    def ensure_temperature(self, T: float) -> None:
        if self.Tmin is not None and T < self.Tmin - 1.0e-10:
            raise ValueError(
                f"T={T:g} K está por debajo de Tmin={self.Tmin:g} K "
                f"para {self.name}."
            )
        if self.Tmax is not None and T > self.Tmax + 1.0e-10:
            raise ValueError(
                f"T={T:g} K está por encima de Tmax={self.Tmax:g} K "
                f"para {self.name}."
            )

    def psat(self, T: float) -> float:
        self.ensure_temperature(T)
        denom = T + self.C
        if abs(denom) < EPS:
            raise ValueError(f"Singularidad en Antoine para {self.name}: T + C = 0.")
        P = 10.0 ** (self.A - self.B / denom)
        if not math.isfinite(P) or P <= 0:
            raise ValueError(f"Presión de vapor no física para {self.name}.")
        return P


def parse_component(spec: str) -> Component:
    """
    Formato:
        NOMBRE;A;B;C
    o:
        NOMBRE;A;B;C;Tmin;Tmax
    """
    parts = [p.strip() for p in spec.split(";")]
    if len(parts) not in (4, 6):
        raise ValueError(
            "Formato de --component: "
            "'NOMBRE;A;B;C' o 'NOMBRE;A;B;C;Tmin;Tmax'."
        )
    if not parts[0]:
        raise ValueError("El nombre del componente no puede quedar vacío.")
    A, B, C = map(parse_decimal, parts[1:4])
    Tmin = Tmax = None
    if len(parts) == 6:
        Tmin = parse_decimal(parts[4])
        Tmax = parse_decimal(parts[5])
        if Tmin >= Tmax:
            raise ValueError(f"Para {parts[0]}, Tmin debe ser menor que Tmax.")
    return Component(parts[0], A, B, C, Tmin, Tmax)


# ---------------------------------------------------------------------------
# Regla de la palanca y balances
# ---------------------------------------------------------------------------

@dataclass
class PhaseSplit:
    beta: float
    liquid_fraction: float
    F: float
    L: float
    V: float
    z: list[float]
    x: list[float] | None
    y: list[float] | None
    n_liquid: list[float]
    n_vapor: list[float]
    recovery_liquid: list[float]
    recovery_vapor: list[float]
    component_balance_error: list[float]
    overall_balance_error: float


def phase_split_from_beta(
    z: Sequence[float],
    beta: float,
    F: float,
    x: Sequence[float] | None,
    y: Sequence[float] | None,
) -> PhaseSplit:
    z = validate_fraction_vector(z, "z_i")
    if F <= 0 or not math.isfinite(F):
        raise ValueError("F debe ser positivo.")
    if beta < -1.0e-10 or beta > 1.0 + 1.0e-10:
        raise ValueError("beta debe encontrarse entre 0 y 1.")
    beta = max(0.0, min(1.0, beta))
    L = F * (1.0 - beta)
    V = F * beta

    if x is None:
        xvals = None
        nL = [0.0] * len(z)
    else:
        xvals = validate_fraction_vector(x, "x_i")
        if len(xvals) != len(z):
            raise ValueError("z_i y x_i deben tener la misma longitud.")
        nL = [L * xi for xi in xvals]

    if y is None:
        yvals = None
        nV = [0.0] * len(z)
    else:
        yvals = validate_fraction_vector(y, "y_i")
        if len(yvals) != len(z):
            raise ValueError("z_i y y_i deben tener la misma longitud.")
        nV = [V * yi for yi in yvals]

    errors = []
    recL = []
    recV = []
    for i, zi in enumerate(z):
        feed_i = F * zi
        balance_i = nL[i] + nV[i] - feed_i
        errors.append(balance_i)
        if feed_i > EPS:
            recL.append(nL[i] / feed_i)
            recV.append(nV[i] / feed_i)
        else:
            recL.append(0.0)
            recV.append(0.0)

    return PhaseSplit(
        beta=beta,
        liquid_fraction=1.0 - beta,
        F=F,
        L=L,
        V=V,
        z=list(z),
        x=xvals,
        y=yvals,
        n_liquid=nL,
        n_vapor=nV,
        recovery_liquid=recL,
        recovery_vapor=recV,
        component_balance_error=errors,
        overall_balance_error=L + V - F,
    )


def lever_rule(
    z: Sequence[float],
    x: Sequence[float],
    y: Sequence[float],
    F: float = 1.0,
    consistency_tol: float = 1.0e-7,
) -> PhaseSplit:
    """
    Regla de la palanca generalizada a balances multicomponentes.

    Para una mezcla binaria coincide con la construcción geométrica habitual.
    En una mezcla multicomponente, todos los componentes con x_i != y_i
    deben proporcionar el mismo beta:
        beta_i = (z_i - x_i)/(y_i - x_i)
    """
    z = validate_fraction_vector(z, "z_i")
    x = validate_fraction_vector(x, "x_i")
    y = validate_fraction_vector(y, "y_i")
    if not (len(z) == len(x) == len(y)):
        raise ValueError("z_i, x_i e y_i deben tener la misma longitud.")

    candidates = []
    for zi, xi, yi in zip(z, x, y):
        denom = yi - xi
        if abs(denom) > 1.0e-10:
            candidates.append((zi - xi) / denom)
        elif abs(zi - xi) > consistency_tol:
            raise ValueError(
                "Las composiciones suministradas no satisfacen el balance de fases."
            )

    if not candidates:
        raise ValueError(
            "No puede aplicarse la regla de la palanca porque x_i e y_i "
            "son indistinguibles para todos los componentes."
        )

    beta = sum(candidates) / len(candidates)
    spread = max(abs(b - beta) for b in candidates)
    if spread > consistency_tol:
        raise ValueError(
            "Las composiciones x_i, y_i y z_i no proporcionan una única "
            "fracción vaporizada. Revise los datos."
        )
    if beta < -consistency_tol or beta > 1.0 + consistency_tol:
        raise ValueError(
            "La composición global no se encuentra entre las composiciones "
            "de las fases; no hay una división física con 0 <= beta <= 1."
        )

    return phase_split_from_beta(z, beta, F, x, y)


# ---------------------------------------------------------------------------
# Flash y Rachford-Rice
# ---------------------------------------------------------------------------

def rr_function(beta: float, z: Sequence[float], K: Sequence[float]) -> float:
    total = 0.0
    for zi, Ki in zip(z, K):
        denom = 1.0 + beta * (Ki - 1.0)
        if denom <= 0:
            raise ValueError("Denominador no físico en Rachford-Rice.")
        total += zi * (Ki - 1.0) / denom
    return total


def rr_derivative(beta: float, z: Sequence[float], K: Sequence[float]) -> float:
    total = 0.0
    for zi, Ki in zip(z, K):
        term = Ki - 1.0
        denom = 1.0 + beta * term
        if denom <= 0:
            raise ValueError("Denominador no físico en Rachford-Rice.")
        total -= zi * term * term / (denom * denom)
    return total


@dataclass
class RRResult:
    beta: float
    residual: float
    iterations: int
    method_used: str
    fallback_count: int


def solve_rr_auto(
    z: Sequence[float],
    K: Sequence[float],
    xtol: float = 1.0e-12,
    ftol: float = 1.0e-12,
    max_iter: int = 200,
) -> RRResult:
    """
    Newton salvaguardado en [0,1] con sustitución por bisección.
    Solo debe llamarse cuando f(0)>0 y f(1)<0.
    """
    a, b = 0.0, 1.0
    fa = rr_function(a, z, K)
    fb = rr_function(b, z, K)
    if not (fa > 0 and fb < 0):
        raise ValueError(
            "Rachford-Rice no presenta una raíz bifásica estricta en (0,1)."
        )

    x = 0.5
    fx = rr_function(x, z, K)
    fallback = 0
    prev_abs = abs(fx)

    for it in range(1, max_iter + 1):
        dfx = rr_derivative(x, z, K)
        use_bisect = (not math.isfinite(dfx)) or abs(dfx) < 1.0e-16

        if not use_bisect:
            candidate = x - fx / dfx
            if (not math.isfinite(candidate)) or not (a < candidate < b):
                use_bisect = True

        if use_bisect:
            candidate = 0.5 * (a + b)
            fallback += 1

        fc = rr_function(candidate, z, K)

        if (
            not use_bisect
            and abs(fc) > 1.25 * prev_abs
            and (b - a) > xtol
        ):
            candidate = 0.5 * (a + b)
            fc = rr_function(candidate, z, K)
            fallback += 1

        dx = abs(candidate - x)

        if fc > 0:
            a, fa = candidate, fc
        else:
            b, fb = candidate, fc

        if abs(fc) <= ftol and (dx <= xtol or (b - a) <= 2 * xtol):
            return RRResult(candidate, fc, it, "Newton salvaguardado", fallback)

        x, fx = candidate, fc
        prev_abs = abs(fc)

    # Respaldo final por bisección pura.
    for jt in range(1, max_iter + 1):
        candidate = 0.5 * (a + b)
        fc = rr_function(candidate, z, K)
        fallback += 1
        if fc > 0:
            a = candidate
        else:
            b = candidate
        if abs(fc) <= ftol and (b - a) <= 2 * xtol:
            return RRResult(
                candidate,
                fc,
                max_iter + jt,
                "Newton salvaguardado + bisección",
                fallback,
            )

    raise RuntimeError("Rachford-Rice no alcanzó la convergencia.")


@dataclass
class FlashResult:
    state: str
    z: list[float]
    K: list[float]
    split: PhaseSplit
    f0: float
    f1: float
    rr: RRResult | None


def flash_from_K(
    z: Sequence[float],
    K: Sequence[float],
    F: float = 1.0,
    phase_tol: float = 1.0e-10,
) -> FlashResult:
    z = validate_fraction_vector(z, "z_i")
    K = validate_positive_vector(K, "K_i")
    if len(z) != len(K):
        raise ValueError("Debe haber un K_i por cada componente.")
    if F <= 0:
        raise ValueError("F debe ser positivo.")

    f0 = rr_function(0.0, z, K)
    f1 = rr_function(1.0, z, K)

    # Punto de burbuja: beta = 0, y_i = K_i z_i y la suma es 1.
    if abs(f0) <= phase_tol:
        y = [Ki * zi for zi, Ki in zip(z, K)]
        y = validate_fraction_vector(y, "y_i")
        split = phase_split_from_beta(z, 0.0, F, z, y)
        return FlashResult("PUNTO_DE_BURBUJA", z, K, split, f0, f1, None)

    # Punto de rocío: beta = 1, x_i = z_i/K_i y la suma es 1.
    if abs(f1) <= phase_tol:
        x = [zi / Ki for zi, Ki in zip(z, K)]
        x = validate_fraction_vector(x, "x_i")
        split = phase_split_from_beta(z, 1.0, F, x, z)
        return FlashResult("PUNTO_DE_ROCIO", z, K, split, f0, f1, None)

    # f(beta) es decreciente. Si f(0)<0, la raíz quedaría a beta<0:
    # alimentación estable como líquido. Si f(1)>0, quedaría a beta>1:
    # alimentación estable como vapor.
    if f0 < 0:
        split = phase_split_from_beta(z, 0.0, F, z, None)
        return FlashResult("LIQUIDO", z, K, split, f0, f1, None)

    if f1 > 0:
        split = phase_split_from_beta(z, 1.0, F, None, z)
        return FlashResult("VAPOR", z, K, split, f0, f1, None)

    if not (f0 > 0 and f1 < 0):
        raise RuntimeError(
            "Clasificación de fase inconsistente. Revise K_i y composición."
        )

    rr = solve_rr_auto(z, K)
    beta = rr.beta
    x = [
        zi / (1.0 + beta * (Ki - 1.0))
        for zi, Ki in zip(z, K)
    ]
    y = [Ki * xi for Ki, xi in zip(K, x)]
    x = validate_fraction_vector(x, "x_i calculadas")
    y = validate_fraction_vector(y, "y_i calculadas")
    split = phase_split_from_beta(z, beta, F, x, y)

    return FlashResult("BIFASICO", z, K, split, f0, f1, rr)


def flash_ideal_antoine(
    components: Sequence[Component],
    z: Sequence[float],
    T: float,
    P: float,
    F: float = 1.0,
) -> tuple[FlashResult, list[float]]:
    z = validate_fraction_vector(z, "z_i")
    if len(components) != len(z):
        raise ValueError("Debe haber un componente por cada z_i.")
    if T <= 0 or P <= 0:
        raise ValueError("T y P deben ser positivos.")
    pstar = [c.psat(T) for c in components]
    K = [pi / P for pi in pstar]
    return flash_from_K(z, K, F), pstar


# ---------------------------------------------------------------------------
# Conversión molar -> másica
# ---------------------------------------------------------------------------

def mass_fractions(mole_fractions: Sequence[float], molar_masses: Sequence[float]) -> list[float]:
    x = validate_fraction_vector(mole_fractions, "fracciones molares")
    M = validate_positive_vector(molar_masses, "masas molares")
    if len(x) != len(M):
        raise ValueError("Debe haber una masa molar por componente.")
    weights = [xi * Mi for xi, Mi in zip(x, M)]
    total = sum(weights)
    return [w / total for w in weights]


# ---------------------------------------------------------------------------
# Destilación diferencial: Rayleigh
# ---------------------------------------------------------------------------

def equilibrium_y_constant_alpha(x: float, alpha: float) -> float:
    if not 0.0 <= x <= 1.0:
        raise ValueError("x debe encontrarse entre 0 y 1.")
    if alpha <= 0:
        raise ValueError("alpha debe ser positiva.")
    denom = 1.0 + (alpha - 1.0) * x
    return alpha * x / denom


def rayleigh_integrand_constant_alpha(x: float, alpha: float) -> float:
    y = equilibrium_y_constant_alpha(x, alpha)
    denom = y - x
    if denom <= 0:
        raise ValueError(
            "Para retirar el componente 1 como más volátil se requiere y(x) > x "
            "en el intervalo de integración; normalmente alpha > 1."
        )
    return 1.0 / denom


def adaptive_simpson(
    f: Callable[[float], float],
    a: float,
    b: float,
    tol: float = 1.0e-10,
    max_depth: int = 20,
) -> float:
    """Integración de Simpson adaptativa sin dependencias externas."""
    if a == b:
        return 0.0
    if a > b:
        return -adaptive_simpson(f, b, a, tol, max_depth)

    fa = f(a)
    fb = f(b)
    c = 0.5 * (a + b)
    fc = f(c)
    whole = (b - a) * (fa + 4.0 * fc + fb) / 6.0

    def recurse(a, b, fa, fb, fc, whole, tol, depth):
        c = 0.5 * (a + b)
        left_mid = 0.5 * (a + c)
        right_mid = 0.5 * (c + b)
        f1 = f(left_mid)
        f2 = f(right_mid)
        left = (c - a) * (fa + 4.0 * f1 + fc) / 6.0
        right = (b - c) * (fc + 4.0 * f2 + fb) / 6.0
        delta = left + right - whole
        if depth <= 0 or abs(delta) <= 15.0 * tol:
            return left + right + delta / 15.0
        return (
            recurse(a, c, fa, fc, f1, left, tol / 2.0, depth - 1)
            + recurse(c, b, fc, fb, f2, right, tol / 2.0, depth - 1)
        )

    return recurse(a, b, fa, fb, fc, whole, tol, max_depth)


@dataclass
class RayleighResult:
    F0: float
    N: float
    D: float
    x0: float
    xf: float
    alpha: float
    integral: float
    xD_average: float
    recovery_light: float
    light_initial: float
    light_residual: float
    light_distillate: float
    heavy_initial: float
    heavy_residual: float
    heavy_distillate: float


def rayleigh_from_final_x(
    F0: float,
    x0: float,
    xf: float,
    alpha: float,
) -> RayleighResult:
    if F0 <= 0:
        raise ValueError("La cantidad inicial debe ser positiva.")
    if not (0.0 < xf < x0 < 1.0):
        raise ValueError(
            "Para el componente 1 más volátil debe cumplirse 0 < xf < x0 < 1."
        )
    if alpha <= 1.0:
        raise ValueError(
            "Este modo supone que el componente 1 es el más volátil; "
            "se requiere alpha > 1."
        )

    integral = adaptive_simpson(
        lambda xx: rayleigh_integrand_constant_alpha(xx, alpha),
        xf,
        x0,
        tol=1.0e-11,
    )
    N = F0 * math.exp(-integral)
    D = F0 - N
    if D <= 0:
        raise RuntimeError("La cantidad destilada calculada no es positiva.")

    light_initial = F0 * x0
    light_residual = N * xf
    light_distillate = light_initial - light_residual

    heavy_initial = F0 * (1.0 - x0)
    heavy_residual = N * (1.0 - xf)
    heavy_distillate = heavy_initial - heavy_residual

    xD_average = light_distillate / D
    recovery = light_distillate / light_initial if light_initial > EPS else 0.0

    return RayleighResult(
        F0=F0,
        N=N,
        D=D,
        x0=x0,
        xf=xf,
        alpha=alpha,
        integral=integral,
        xD_average=xD_average,
        recovery_light=recovery,
        light_initial=light_initial,
        light_residual=light_residual,
        light_distillate=light_distillate,
        heavy_initial=heavy_initial,
        heavy_residual=heavy_residual,
        heavy_distillate=heavy_distillate,
    )


def solve_final_x_for_residual(
    F0: float,
    N_target: float,
    x0: float,
    alpha: float,
    xtol: float = 1.0e-10,
    max_iter: int = 200,
) -> RayleighResult:
    if not (0 < N_target < F0):
        raise ValueError("Debe cumplirse 0 < N_objetivo < F0.")
    if not (0 < x0 < 1):
        raise ValueError("x0 debe estar entre 0 y 1.")
    if alpha <= 1:
        raise ValueError("Se requiere alpha > 1.")

    target = math.log(F0 / N_target)

    # xf pertenece a (0, x0). Evitamos exactamente 0 por la singularidad.
    a = max(1.0e-12, x0 * 1.0e-10)
    b = x0 - max(1.0e-12, x0 * 1.0e-10)

    def g(xf):
        val = adaptive_simpson(
            lambda xx: rayleigh_integrand_constant_alpha(xx, alpha),
            xf,
            x0,
            tol=1.0e-10,
        )
        return val - target

    ga = g(a)
    gb = g(b)
    if ga * gb > 0:
        raise ValueError(
            "No se ha podido acotar una composición final para la cantidad "
            "residual solicitada."
        )

    for _ in range(max_iter):
        m = 0.5 * (a + b)
        gm = g(m)
        if abs(gm) <= 1.0e-10 and abs(b - a) <= 2 * xtol:
            return rayleigh_from_final_x(F0, x0, m, alpha)
        if ga * gm <= 0:
            b, gb = m, gm
        else:
            a, ga = m, gm

    m = 0.5 * (a + b)
    if abs(g(m)) > 1.0e-8:
        raise RuntimeError("No convergió el cálculo inverso de Rayleigh.")
    return rayleigh_from_final_x(F0, x0, m, alpha)


# ---------------------------------------------------------------------------
# Vaporizaciones-condensaciones ideales sucesivas
# ---------------------------------------------------------------------------

@dataclass
class StageResult:
    stage: int
    x_in: float
    y_eq: float
    x_next: float


def successive_equilibrium_stages(
    x0: float,
    alpha: float,
    stages: int,
) -> list[StageResult]:
    if not 0 <= x0 <= 1:
        raise ValueError("x0 debe estar entre 0 y 1.")
    if alpha <= 0:
        raise ValueError("alpha debe ser positiva.")
    if stages < 1:
        raise ValueError("El número de etapas debe ser al menos 1.")

    results = []
    x = x0
    for n in range(1, stages + 1):
        y = equilibrium_y_constant_alpha(x, alpha)
        # Condensación total: la composición del condensado coincide con la
        # del vapor que alimenta la etapa siguiente.
        x_next = y
        results.append(StageResult(n, x, y, x_next))
        x = x_next
    return results


# ---------------------------------------------------------------------------
# Presentación
# ---------------------------------------------------------------------------

def default_names(n: int) -> list[str]:
    return [f"Componente {i+1}" for i in range(n)]


def print_flash(
    result: FlashResult,
    names: Sequence[str] | None,
    sig: int,
    molar_masses: Sequence[float] | None = None,
    verbose: bool = False,
):
    n = len(result.z)
    names = list(names) if names is not None else default_names(n)
    if len(names) != n:
        raise ValueError("El número de nombres debe coincidir con el de componentes.")

    split = result.split

    print(f"Estado: {result.state.replace('_', ' ')}")
    print(f"f(0) = {format_sig(result.f0, sig)}")
    print(f"f(1) = {format_sig(result.f1, sig)}")
    print(f"Fracción vapor, β = {format_sig(split.beta, sig)} "
          f"({format_sig(percent(split.beta), sig)} %)")
    print(f"Fracción líquida = {format_sig(split.liquid_fraction, sig)} "
          f"({format_sig(percent(split.liquid_fraction), sig)} %)")
    print(f"F = {format_sig(split.F, sig)}")
    print(f"L = {format_sig(split.L, sig)}")
    print(f"V = {format_sig(split.V, sig)}")

    print("\nComposiciones y reparto por componente")
    headers = ["Componente", "z_i", "K_i", "x_i", "y_i",
               "n_i,L", "n_i,V", "% i en L", "% i en V"]
    rows = []
    for i in range(n):
        xi = split.x[i] if split.x is not None else None
        yi = split.y[i] if split.y is not None else None
        rows.append([
            names[i],
            format_sig(result.z[i], sig),
            format_sig(result.K[i], sig),
            "—" if xi is None else format_sig(xi, sig),
            "—" if yi is None else format_sig(yi, sig),
            format_sig(split.n_liquid[i], sig),
            format_sig(split.n_vapor[i], sig),
            format_sig(percent(split.recovery_liquid[i]), sig),
            format_sig(percent(split.recovery_vapor[i]), sig),
        ])
    widths = [max(len(headers[j]), max(len(r[j]) for r in rows)) for j in range(len(headers))]
    print("  ".join(h.ljust(widths[j]) for j, h in enumerate(headers)))
    print("  ".join("-" * widths[j] for j in range(len(headers))))
    for row in rows:
        print("  ".join(row[j].ljust(widths[j]) for j in range(len(headers))))

    print("\nComprobaciones")
    print(f"Σz_i = {format_sig(sum(result.z), sig)}")
    if split.x is not None:
        print(f"Σx_i = {format_sig(sum(split.x), sig)}")
    if split.y is not None:
        print(f"Σy_i = {format_sig(sum(split.y), sig)}")
    max_err = max(abs(e) for e in split.component_balance_error)
    print(f"Error máximo de balance de componente = {format_sig(max_err, sig)}")
    print(f"Error de balance global = {format_sig(split.overall_balance_error, sig)}")

    if molar_masses is not None:
        M = validate_positive_vector(molar_masses, "masas molares")
        if len(M) != n:
            raise ValueError("Debe introducir una masa molar por componente.")
        print("\nComposición másica")
        if split.x is not None:
            wL = mass_fractions(split.x, M)
            print("Líquido:")
            for name, wi in zip(names, wL):
                print(f"  {name}: {format_sig(wi, sig)} "
                      f"({format_sig(percent(wi), sig)} % m/m)")
        if split.y is not None:
            wV = mass_fractions(split.y, M)
            print("Vapor:")
            for name, wi in zip(names, wV):
                print(f"  {name}: {format_sig(wi, sig)} "
                      f"({format_sig(percent(wi), sig)} % m/m)")

    if verbose and result.rr is not None:
        print("\nResolución numérica")
        print(f"Método interno: {result.rr.method_used}")
        print(f"Iteraciones: {result.rr.iterations}")
        print(f"Pasos de respaldo: {result.rr.fallback_count}")
        print(f"Residuo final: {format_sig(result.rr.residual, max(sig, 4))}")


def print_lever(split: PhaseSplit, names: Sequence[str] | None, sig: int):
    n = len(split.z)
    names = list(names) if names is not None else default_names(n)
    if len(names) != n:
        raise ValueError("El número de nombres no coincide con el de componentes.")

    print(f"Fracción vapor, V/F = {format_sig(split.beta, sig)} "
          f"({format_sig(percent(split.beta), sig)} %)")
    print(f"Fracción líquida, L/F = {format_sig(split.liquid_fraction, sig)} "
          f"({format_sig(percent(split.liquid_fraction), sig)} %)")
    if split.L > EPS:
        print(f"V/L = {format_sig(split.V / split.L, sig)}")
    else:
        print("V/L = ∞")
    print(f"F = {format_sig(split.F, sig)}")
    print(f"L = {format_sig(split.L, sig)}")
    print(f"V = {format_sig(split.V, sig)}")

    print("\nReparto de componentes")
    headers = ["Componente", "z_i", "x_i", "y_i", "n_i,L", "n_i,V",
               "% i en L", "% i en V"]
    rows = []
    for i in range(n):
        rows.append([
            names[i],
            format_sig(split.z[i], sig),
            format_sig(split.x[i], sig),
            format_sig(split.y[i], sig),
            format_sig(split.n_liquid[i], sig),
            format_sig(split.n_vapor[i], sig),
            format_sig(percent(split.recovery_liquid[i]), sig),
            format_sig(percent(split.recovery_vapor[i]), sig),
        ])
    widths = [max(len(headers[j]), max(len(r[j]) for r in rows)) for j in range(len(headers))]
    print("  ".join(h.ljust(widths[j]) for j, h in enumerate(headers)))
    print("  ".join("-" * widths[j] for j in range(len(headers))))
    for row in rows:
        print("  ".join(row[j].ljust(widths[j]) for j in range(len(headers))))

    max_err = max(abs(e) for e in split.component_balance_error)
    print("\nComprobaciones")
    print(f"Error máximo de balance de componente = {format_sig(max_err, sig)}")
    print(f"Error de balance global = {format_sig(split.overall_balance_error, sig)}")


def print_rayleigh(result: RayleighResult, sig: int):
    print(f"Líquido inicial, N0 = {format_sig(result.F0, sig)}")
    print(f"Líquido residual, N = {format_sig(result.N, sig)}")
    print(f"Destilado total, D = {format_sig(result.D, sig)}")
    print(f"x0 = {format_sig(result.x0, sig)}")
    print(f"xf = {format_sig(result.xf, sig)}")
    print(f"α = {format_sig(result.alpha, sig)}")
    print(f"Integral de Rayleigh = {format_sig(result.integral, sig)}")
    print(f"Composición media del destilado, xD = {format_sig(result.xD_average, sig)}")
    print(
        f"Recuperación del componente 1 en el destilado = "
        f"{format_sig(percent(result.recovery_light), sig)} %"
    )
    print("\nBalance por componentes")
    print(
        f"Componente 1: inicial={format_sig(result.light_initial, sig)}, "
        f"residuo={format_sig(result.light_residual, sig)}, "
        f"destilado={format_sig(result.light_distillate, sig)}"
    )
    print(
        f"Componente 2: inicial={format_sig(result.heavy_initial, sig)}, "
        f"residuo={format_sig(result.heavy_residual, sig)}, "
        f"destilado={format_sig(result.heavy_distillate, sig)}"
    )


# ---------------------------------------------------------------------------
# Entrada interactiva
# ---------------------------------------------------------------------------

def ask(prompt: str) -> str:
    return input(prompt).strip()


def ask_float(prompt: str, *, positive: bool = False) -> float:
    while True:
        try:
            val = parse_decimal(ask(prompt))
            if positive and val <= 0:
                raise ValueError("Debe ser positivo.")
            return val
        except ValueError as exc:
            print(f"Entrada no válida: {exc}")


def ask_int(prompt: str, minimum: int = 1) -> int:
    while True:
        try:
            val = int(ask(prompt))
            if val < minimum:
                raise ValueError
            return val
        except ValueError:
            print(f"Introduzca un entero >= {minimum}.")


def ask_vector(names: Sequence[str], symbol: str) -> list[float]:
    vals = [ask_float(f"  {symbol}({name}) = ") for name in names]
    return validate_fraction_vector(vals, symbol)


def ask_K(names: Sequence[str]) -> list[float]:
    vals = [ask_float(f"  K({name}) = ", positive=True) for name in names]
    return validate_positive_vector(vals, "K_i")


def ask_optional_mw(names: Sequence[str]) -> list[float] | None:
    answer = ask("¿Desea calcular también composiciones másicas? [s/N]: ").lower()
    if not answer.startswith("s"):
        return None
    return [ask_float(f"  M({name}) [g/mol] = ", positive=True) for name in names]


def ask_antoine_components() -> list[Component]:
    n = ask_int("Número de componentes: ", 2)
    comps = []
    print(
        "\nAntoine: log10(P*) = A - B/(T + C), "
        "P* en kPa y T en K."
    )
    print("Si su expresión usa T - c, introduzca C = -c.\n")
    for i in range(n):
        name = ask(f"Nombre del componente {i+1}: ") or f"Componente {i+1}"
        A = ask_float("  A = ")
        B = ask_float("  B = ")
        C = ask_float("  C = ")
        use_range = ask("  ¿Introducir intervalo válido de Antoine? [S/n]: ").lower()
        Tmin = Tmax = None
        if not use_range.startswith("n"):
            Tmin = ask_float("    Tmin (K) = ")
            Tmax = ask_float("    Tmax (K) = ")
            if Tmin >= Tmax:
                raise ValueError("Tmin debe ser menor que Tmax.")
        comps.append(Component(name, A, B, C, Tmin, Tmax))
    return comps


def interactive_menu():
    sig = 5
    verbose = False

    while True:
        print("\nOPERACIONES DE EQUILIBRIO LÍQUIDO-VAPOR — CAPÍTULO 7")
        print("=" * 58)
        print("1. Regla de la palanca / balance de fases")
        print("2. Vaporización flash a partir de K_i")
        print("3. Vaporización flash ideal con Antoine, T y P")
        print("4. Destilación simple/diferencial (Rayleigh, α constante)")
        print("5. Rayleigh inverso: composición final a partir del líquido residual")
        print("6. Vaporizaciones-condensaciones sucesivas (α constante)")
        print("0. Salir")

        option = ask("\nOpción: ")

        try:
            if option == "0":
                return

            if option == "1":
                n = ask_int("Número de componentes: ", 2)
                names = [
                    ask(f"Nombre del componente {i+1}: ") or f"Componente {i+1}"
                    for i in range(n)
                ]
                print("\nComposición global:")
                z = ask_vector(names, "z")
                print("\nComposición líquida:")
                x = ask_vector(names, "x")
                print("\nComposición vapor:")
                y = ask_vector(names, "y")
                F = ask_float("Cantidad o caudal total F: ", positive=True)
                split = lever_rule(z, x, y, F)
                print()
                print_lever(split, names, sig)

            elif option == "2":
                n = ask_int("Número de componentes: ", 2)
                names = [
                    ask(f"Nombre del componente {i+1}: ") or f"Componente {i+1}"
                    for i in range(n)
                ]
                print("\nComposición global:")
                z = ask_vector(names, "z")
                print("\nConstantes de equilibrio:")
                K = ask_K(names)
                F = ask_float("Cantidad o caudal de alimentación F: ", positive=True)
                mw = ask_optional_mw(names)
                result = flash_from_K(z, K, F)
                print()
                print_flash(result, names, sig, mw, verbose)

            elif option == "3":
                comps = ask_antoine_components()
                names = [c.name for c in comps]
                print("\nComposición global:")
                z = ask_vector(names, "z")
                T = ask_float("T (K): ", positive=True)
                P = ask_float("P (kPa): ", positive=True)
                F = ask_float("Cantidad o caudal de alimentación F: ", positive=True)
                mw = ask_optional_mw(names)
                result, pstar = flash_ideal_antoine(comps, z, T, P, F)
                print("\nPresiones de vapor y K_i:")
                for c, ps, Ki in zip(comps, pstar, result.K):
                    print(
                        f"  {c.name}: P*={format_sig(ps, sig)} kPa, "
                        f"K={format_sig(Ki, sig)}"
                    )
                print()
                print_flash(result, names, sig, mw, verbose)

            elif option == "4":
                F0 = ask_float("Cantidad inicial de líquido, N0: ", positive=True)
                x0 = ask_float("Fracción molar inicial del componente más volátil, x0: ")
                xf = ask_float("Fracción molar final en el residuo, xf: ")
                alpha = ask_float("Volatilidad relativa constante, α: ", positive=True)
                result = rayleigh_from_final_x(F0, x0, xf, alpha)
                print()
                print_rayleigh(result, sig)

            elif option == "5":
                F0 = ask_float("Cantidad inicial de líquido, N0: ", positive=True)
                N = ask_float("Cantidad residual objetivo, N: ", positive=True)
                x0 = ask_float("Fracción molar inicial del componente más volátil, x0: ")
                alpha = ask_float("Volatilidad relativa constante, α: ", positive=True)
                result = solve_final_x_for_residual(F0, N, x0, alpha)
                print()
                print_rayleigh(result, sig)

            elif option == "6":
                x0 = ask_float("x0 del componente más volátil: ")
                alpha = ask_float("Volatilidad relativa constante, α: ", positive=True)
                stages = ask_int("Número de vaporizaciones: ", 1)
                results = successive_equilibrium_stages(x0, alpha, stages)
                print("\nEtapa    x_entrada    y_equilibrio    x_siguiente")
                print("-----    ---------    ------------    -----------")
                for r in results:
                    print(
                        f"{r.stage:<8}"
                        f"{format_sig(r.x_in, sig):<13}"
                        f"{format_sig(r.y_eq, sig):<16}"
                        f"{format_sig(r.x_next, sig)}"
                    )
                print(
                    f"\nEnriquecimiento global: "
                    f"{format_sig(results[-1].x_next / x0 if x0 > 0 else math.nan, sig)}"
                )

            else:
                print("Opción no reconocida.")

        except (ValueError, RuntimeError, ZeroDivisionError) as exc:
            print(f"\nERROR: {exc}")


# ---------------------------------------------------------------------------
# Línea de comandos
# ---------------------------------------------------------------------------

def add_output_args(parser):
    parser.add_argument(
        "--sig",
        type=int,
        default=5,
        help="Cifras significativas mostradas (predeterminado: 5).",
    )


def build_parser():
    parser = argparse.ArgumentParser(
        description=(
            "Regla de la palanca, flash multicomponente, Rachford-Rice y "
            "destilación diferencial del capítulo 7."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("lever", help="Regla de la palanca / balance de fases.")
    p.add_argument("--z", action="append", required=True, help="Fracción global z_i.")
    p.add_argument("--x", action="append", required=True, help="Fracción líquida x_i.")
    p.add_argument("--y", action="append", required=True, help="Fracción vapor y_i.")
    p.add_argument("--name", action="append", help="Nombre del componente.")
    p.add_argument("--F", default="1", help="Cantidad/caudal total.")
    add_output_args(p)

    p = sub.add_parser("flash-k", help="Flash a partir de z_i y K_i.")
    p.add_argument("--z", action="append", required=True)
    p.add_argument("--K", action="append", required=True)
    p.add_argument("--name", action="append", help="Nombre del componente.")
    p.add_argument("--mw", action="append", help="Masa molar opcional, g/mol.")
    p.add_argument("--F", default="1")
    p.add_argument("--verbose", action="store_true")
    add_output_args(p)

    p = sub.add_parser(
        "flash-antoine",
        help="Flash ideal con Antoine a T y P dadas.",
    )
    p.add_argument(
        "--component",
        action="append",
        required=True,
        help=(
            "'NOMBRE;A;B;C' o 'NOMBRE;A;B;C;Tmin;Tmax'. "
            "Repetir una vez por componente."
        ),
    )
    p.add_argument("--z", action="append", required=True)
    p.add_argument("--T", required=True, help="Temperatura en K.")
    p.add_argument("--P", required=True, help="Presión total en kPa.")
    p.add_argument("--F", default="1")
    p.add_argument("--mw", action="append", help="Masa molar opcional, g/mol.")
    p.add_argument("--verbose", action="store_true")
    add_output_args(p)

    p = sub.add_parser(
        "rayleigh-alpha",
        help="Destilación diferencial con α constante y xf conocida.",
    )
    p.add_argument("--F0", required=True, help="Cantidad inicial.")
    p.add_argument("--x0", required=True, help="Composición inicial del volátil.")
    p.add_argument("--xf", required=True, help="Composición final del residuo.")
    p.add_argument("--alpha", required=True, help="Volatilidad relativa constante.")
    add_output_args(p)

    p = sub.add_parser(
        "rayleigh-target",
        help="Calcula xf para una cantidad residual objetivo.",
    )
    p.add_argument("--F0", required=True)
    p.add_argument("--N", required=True, help="Cantidad residual objetivo.")
    p.add_argument("--x0", required=True)
    p.add_argument("--alpha", required=True)
    add_output_args(p)

    p = sub.add_parser(
        "stages-alpha",
        help="Vaporizaciones-condensaciones ideales sucesivas con α constante.",
    )
    p.add_argument("--x0", required=True)
    p.add_argument("--alpha", required=True)
    p.add_argument("--stages", type=int, required=True)
    add_output_args(p)

    return parser


def main_cli(args):
    sig = args.sig

    if args.command == "lever":
        z = [parse_decimal(v) for v in args.z]
        x = [parse_decimal(v) for v in args.x]
        y = [parse_decimal(v) for v in args.y]
        F = parse_decimal(args.F)
        split = lever_rule(z, x, y, F)
        print_lever(split, args.name, sig)

    elif args.command == "flash-k":
        z = [parse_decimal(v) for v in args.z]
        K = [parse_decimal(v) for v in args.K]
        F = parse_decimal(args.F)
        mw = [parse_decimal(v) for v in args.mw] if args.mw else None
        result = flash_from_K(z, K, F)
        print_flash(result, args.name, sig, mw, args.verbose)

    elif args.command == "flash-antoine":
        comps = [parse_component(s) for s in args.component]
        z = [parse_decimal(v) for v in args.z]
        T = parse_decimal(args.T)
        P = parse_decimal(args.P)
        F = parse_decimal(args.F)
        mw = [parse_decimal(v) for v in args.mw] if args.mw else None
        result, pstar = flash_ideal_antoine(comps, z, T, P, F)
        print("Presiones de vapor y K_i:")
        for c, ps, Ki in zip(comps, pstar, result.K):
            print(
                f"  {c.name}: P*={format_sig(ps, sig)} kPa, "
                f"K={format_sig(Ki, sig)}"
            )
        print()
        print_flash(result, [c.name for c in comps], sig, mw, args.verbose)

    elif args.command == "rayleigh-alpha":
        result = rayleigh_from_final_x(
            parse_decimal(args.F0),
            parse_decimal(args.x0),
            parse_decimal(args.xf),
            parse_decimal(args.alpha),
        )
        print_rayleigh(result, sig)

    elif args.command == "rayleigh-target":
        result = solve_final_x_for_residual(
            parse_decimal(args.F0),
            parse_decimal(args.N),
            parse_decimal(args.x0),
            parse_decimal(args.alpha),
        )
        print_rayleigh(result, sig)

    elif args.command == "stages-alpha":
        results = successive_equilibrium_stages(
            parse_decimal(args.x0),
            parse_decimal(args.alpha),
            args.stages,
        )
        print("Etapa    x_entrada    y_equilibrio    x_siguiente")
        print("-----    ---------    ------------    -----------")
        for r in results:
            print(
                f"{r.stage:<8}"
                f"{format_sig(r.x_in, sig):<13}"
                f"{format_sig(r.y_eq, sig):<16}"
                f"{format_sig(r.x_next, sig)}"
            )


def main():
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command is None:
            interactive_menu()
        else:
            main_cli(args)
    except (ValueError, RuntimeError, ZeroDivisionError, IndexError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(2)
    except KeyboardInterrupt:
        print("\nOperación cancelada por el usuario.", file=sys.stderr)
        sys.exit(130)


if __name__ == "__main__":
    main()
