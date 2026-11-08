#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEMA 14 - COMBUSTIÓN Y ANÁLISIS DE GASES
=========================================

Funcionalidad
-------------
Herramienta interactiva para resolver y comprobar los principales cálculos
estequiométricos del capítulo 14: oxígeno estequiométrico, aire teórico y real,
combustión completa e incompleta, mezclas de combustibles, combustibles de
composición elemental, composiciones de gases en base húmeda/seca, análisis
Orsat, cálculos inversos y comprobación de balances elementales.

Tipos de problemas que admite
-----------------------------
1. Oxígeno estequiométrico y aire teórico para una sustancia de fórmula conocida.
2. Combustión completa de una sustancia con aire, O2 puro o mezcla oxidante.
3. Combustión completa de mezclas gaseosas, con componentes combustibles e inertes.
4. Combustibles especificados por composición elemental en masa.
5. Combustión incompleta de compuestos C/H/O con CO2, CO y combustible sin reaccionar.
6. Interpretación de análisis de gases, incluida una modalidad Orsat.
7. Cálculos inversos: H/C desde gases, mezcla binaria conocida y fórmula CHO.
8. Comprobación general de un problema mediante balances elementales.

Hipótesis y límites del modelo
------------------------------
- Es una aplicación ESTEQUIOMÉTRICA. No realiza balances de energía, equilibrio,
  cinética, disociación ni predicción de productos.
- El usuario debe indicar los productos cuando exista más de una posibilidad.
- En combustión completa, C -> CO2 y H -> H2O. Para S y N se solicita el modelo
  de productos si esos elementos están presentes.
- Para otros elementos, el cálculo directo permite definir un único óxido del
  elemento (producto formado solo por ese elemento y O). La opción 8, en cambio,
  comprueba balances con fórmulas químicas generales.
- Los componentes de una mezcla oxidante distintos de O2 se consideran portadores
  no reactivos y pasan a los productos sin transformación.
- No se fuerza una solución cuando faltan relaciones independientes o cuando los
  datos son incompatibles con el modelo elegido.
- El aire seco por defecto se representa como 21,0 % molar de O2 y 79,0 % de N2,
  de acuerdo con el modelo del capítulo.

Cifras significativas
----------------------
Los cálculos internos NO se redondean. La salida numérica se redondea al final,
usando como criterio conservador el menor número de cifras significativas de los
DATOS MEDIDOS que intervienen en cada modalidad. Los coeficientes estequiométricos
enteros y las bases de cálculo elegidas automáticamente se consideran exactos.
La composición por defecto del aire (0,210/0,790) se considera un dato del modelo
con 3 cifras significativas y, por tanto, puede limitar la presentación de resultados.

Entrada decimal
---------------
Se acepta coma o punto decimal. Para evitar ambigüedades, los ceros escritos al
final de un número entero se consideran significativos (por ejemplo, "100" se
interpreta con 3 cifras significativas). Puede usarse notación científica.

Uso
---
    python combustion.py
    python combustion.py --help
    python combustion.py --self-test

La ejecución normal muestra un menú y solicita únicamente magnitudes químicamente
reconocibles. No se introducen ecuaciones algebraicas ya planteadas.
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Iterable

TOL = 1e-9
COMP_TOL_PERCENT = 0.05  # tolerancia absoluta en puntos porcentuales
BAL_REL_TOL = 1e-8
DEFAULT_AIR_O2 = 0.210
DEFAULT_AIR_N2 = 0.790
DEFAULT_AIR_SF = 3

ATOMIC_MASS = {
    "H": 1.008, "He": 4.0026, "Li": 6.94, "Be": 9.0122, "B": 10.81,
    "C": 12.01, "N": 14.01, "O": 16.00, "F": 19.00, "Ne": 20.180,
    "Na": 22.99, "Mg": 24.305, "Al": 26.982, "Si": 28.085, "P": 30.974,
    "S": 32.06, "Cl": 35.45, "Ar": 39.948, "K": 39.098, "Ca": 40.078,
    "Sc": 44.956, "Ti": 47.867, "V": 50.942, "Cr": 52.00, "Mn": 54.938,
    "Fe": 55.845, "Co": 58.933, "Ni": 58.693, "Cu": 63.546, "Zn": 65.38,
    "Ga": 69.723, "Ge": 72.630, "As": 74.922, "Se": 78.971, "Br": 79.904,
    "Kr": 83.798, "Rb": 85.468, "Sr": 87.62, "Ag": 107.8682, "I": 126.90447,
    "Ba": 137.327, "Pt": 195.084, "Au": 196.96657, "Hg": 200.592,
    "Pb": 207.2,
}


class CombustionError(Exception):
    """Error químico o de consistencia en los datos del problema."""


@dataclass
class Measurement:
    value: float
    sigfigs: int
    raw: str = ""


@dataclass
class Oxidizer:
    name: str
    composition: Dict[str, float]  # fracciones molares; debe contener O2
    sigfigs: int
    assumptions: List[str] = field(default_factory=list)

    @property
    def y_o2(self) -> float:
        return self.composition.get("O2", 0.0)


@dataclass
class ProductModel:
    # cantidades de producto por mol de átomos del elemento correspondiente
    # para C y H el modelo de combustión completa es fijo.
    sulfur: Dict[str, float] = field(default_factory=dict)   # fracción de S -> SO2/SO3
    nitrogen: Dict[str, float] = field(default_factory=dict) # fracción de N -> N2/NO/NO2
    other_oxides: Dict[str, str] = field(default_factory=dict)  # elemento -> fórmula de óxido


# -----------------------------------------------------------------------------
# UTILIDADES DE ENTRADA, CIFRAS SIGNIFICATIVAS Y FORMATO
# -----------------------------------------------------------------------------

def normalize_number_text(text: str) -> str:
    s = text.strip().replace(" ", "").replace("−", "-")
    if not s:
        raise ValueError("Entrada vacía.")
    # Aceptar coma decimal española. Si aparecen coma y punto, se rechaza para evitar
    # confundir separadores decimales y de millares.
    if "," in s and "." in s:
        raise ValueError("Use coma o punto decimal, pero no ambos en el mismo número.")
    return s.replace(",", ".")


def count_sigfigs(raw: str) -> int:
    s = normalize_number_text(raw).lower()
    if "e" in s:
        mantissa = s.split("e", 1)[0]
    else:
        mantissa = s
    mantissa = mantissa.lstrip("+-")
    digits = mantissa.replace(".", "")
    digits = digits.lstrip("0")
    if digits:
        return len(digits)
    # Casos como 0,00: la precisión está indicada por los ceros decimales.
    if "." in mantissa:
        return max(1, len(mantissa.split(".", 1)[1]))
    return 1


def parse_measurement(raw: str) -> Measurement:
    s = normalize_number_text(raw)
    value = float(s)
    if not math.isfinite(value):
        raise ValueError("El valor debe ser finito.")
    return Measurement(value=value, sigfigs=count_sigfigs(raw), raw=raw.strip())


def read_measurement(prompt: str, *, min_value: Optional[float] = None,
                     max_value: Optional[float] = None, strictly_positive: bool = False) -> Measurement:
    while True:
        raw = input(prompt).strip()
        try:
            m = parse_measurement(raw)
            if strictly_positive and m.value <= 0:
                raise ValueError("El valor debe ser mayor que cero.")
            if min_value is not None and m.value < min_value:
                raise ValueError(f"El valor debe ser >= {min_value}.")
            if max_value is not None and m.value > max_value:
                raise ValueError(f"El valor debe ser <= {max_value}.")
            return m
        except ValueError as exc:
            print(f"  Dato no válido: {exc}")


def read_int(prompt: str, min_value: int = 1, max_value: Optional[int] = None) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            n = int(raw)
            if n < min_value or (max_value is not None and n > max_value):
                raise ValueError
            return n
        except ValueError:
            lim = f" entre {min_value} y {max_value}" if max_value is not None else f" >= {min_value}"
            print(f"  Introduzca un número entero{lim}.")


def read_choice(prompt: str, choices: Dict[str, str]) -> str:
    while True:
        print(prompt)
        for k, label in choices.items():
            print(f"  {k}. {label}")
        ans = input("Seleccione una opción: ").strip().lower()
        if ans in choices:
            return ans
        print("  Opción no válida.")


def read_yes_no(prompt: str, default: Optional[bool] = None) -> bool:
    suffix = " [S/n]: " if default is True else " [s/N]: " if default is False else " [s/n]: "
    while True:
        ans = input(prompt + suffix).strip().lower()
        if not ans and default is not None:
            return default
        if ans in ("s", "si", "sí", "y", "yes"):
            return True
        if ans in ("n", "no"):
            return False
        print("  Responda s o n.")


def min_sf(*items: object, default: int = 3) -> int:
    vals: List[int] = []
    for item in items:
        if item is None:
            continue
        if isinstance(item, Measurement):
            # Un cero introducido para indicar ausencia de un componente (p. ej., 0 % S)
            # no debe degradar artificialmente la precisión de todos los resultados.
            if item.value != 0.0:
                vals.append(item.sigfigs)
        elif isinstance(item, int):
            vals.append(item)
        elif isinstance(item, (list, tuple, set)):
            for sub in item:
                if isinstance(sub, Measurement):
                    if sub.value != 0.0:
                        vals.append(sub.sigfigs)
                elif isinstance(sub, int):
                    vals.append(sub)
    return min(vals) if vals else default


def format_sig(value: float, sf: int = 3) -> str:
    if not math.isfinite(value):
        return str(value)
    if value == 0.0:
        return "0"
    sf = max(1, int(sf))
    av = abs(value)
    exponent = math.floor(math.log10(av))
    if exponent >= 5 or exponent <= -4:
        s = f"{value:.{sf - 1}e}"
        mant, exp = s.split("e")
        mant = mant.replace(".", ",")
        return f"{mant}e{int(exp):+d}"
    decimals = max(0, sf - exponent - 1)
    s = f"{value:.{decimals}f}"
    return s.replace(".", ",")


def fmt_percent(frac: float, sf: int = 3) -> str:
    return f"{format_sig(100.0 * frac, sf)} %"


def print_header(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def print_data_assumptions(data_lines: Iterable[str], assumptions: Iterable[str]) -> None:
    print("\nDATOS UTILIZADOS")
    for line in data_lines:
        print(f"  - {line}")
    print("\nHIPÓTESIS / MODELO")
    found = False
    for line in assumptions:
        found = True
        print(f"  - {line}")
    if not found:
        print("  - No se han añadido hipótesis distintas de los datos indicados.")


def print_checks(checks: Iterable[Tuple[bool, str]]) -> None:
    print("\nCOMPROBACIONES")
    for ok, msg in checks:
        print(f"  [{'OK' if ok else 'ERROR'}] {msg}")


# -----------------------------------------------------------------------------
# FÓRMULAS QUÍMICAS Y BALANCES ELEMENTALES
# -----------------------------------------------------------------------------

FORMULA_TOKEN = re.compile(r"([A-Z][a-z]?|\(|\)|\d+(?:\.\d+)?)")


def canonical_formula(formula: str) -> str:
    return formula.strip().replace("₂", "2").replace("₃", "3").replace("₄", "4").replace("₅", "5").replace("₆", "6").replace("₇", "7").replace("₈", "8").replace("₉", "9").replace("₀", "0").replace(" ", "")


def parse_formula(formula: str) -> Dict[str, float]:
    """Analiza fórmulas como C2H6O, Ca(OH)2 o Fe2(SO4)3."""
    f = canonical_formula(formula)
    if not f:
        raise CombustionError("La fórmula química está vacía.")
    tokens = FORMULA_TOKEN.findall(f)
    if "".join(tokens) != f:
        raise CombustionError(f"No se pudo interpretar la fórmula '{formula}'.")

    stack: List[Dict[str, float]] = [dict()]
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok == "(":
            stack.append({})
            i += 1
        elif tok == ")":
            if len(stack) == 1:
                raise CombustionError(f"Paréntesis no equilibrados en '{formula}'.")
            group = stack.pop()
            if not group:
                raise CombustionError(f"Grupo vacío en la fórmula '{formula}'.")
            mult = 1.0
            if i + 1 < len(tokens) and re.fullmatch(r"\d+(?:\.\d+)?", tokens[i + 1]):
                mult = float(tokens[i + 1])
                if not math.isfinite(mult) or mult <= 0:
                    raise CombustionError(f"Subíndice no positivo o no finito en '{formula}'.")
                i += 1
            for el, n in group.items():
                stack[-1][el] = stack[-1].get(el, 0.0) + n * mult
            i += 1
        elif re.fullmatch(r"[A-Z][a-z]?", tok):
            el = tok
            mult = 1.0
            if i + 1 < len(tokens) and re.fullmatch(r"\d+(?:\.\d+)?", tokens[i + 1]):
                mult = float(tokens[i + 1])
                if not math.isfinite(mult) or mult <= 0:
                    raise CombustionError(f"Subíndice no positivo o no finito en '{formula}'.")
                i += 1
            stack[-1][el] = stack[-1].get(el, 0.0) + mult
            i += 1
        else:
            raise CombustionError(f"Subíndice inesperado en '{formula}'.")
    if len(stack) != 1:
        raise CombustionError(f"Paréntesis no equilibrados en '{formula}'.")
    if not stack[0] or any(not math.isfinite(n) or n <= 0 for n in stack[0].values()):
        raise CombustionError(f"Fórmula no válida: '{formula}'.")
    return stack[0]


def molar_mass(formula: str) -> float:
    comp = parse_formula(formula)
    missing = [el for el in comp if el not in ATOMIC_MASS]
    if missing:
        raise CombustionError("No hay masa atómica incorporada para: " + ", ".join(missing))
    return sum(ATOMIC_MASS[el] * n for el, n in comp.items())


def element_totals(species: Dict[str, float]) -> Dict[str, float]:
    totals: Dict[str, float] = {}
    for formula, amount in species.items():
        if not math.isfinite(amount) or amount < 0:
            raise CombustionError(f"Cantidad negativa o no finita de {formula}.")
        comp = parse_formula(formula)
        for el, coeff in comp.items():
            totals[el] = totals.get(el, 0.0) + coeff * amount
    return totals


def balance_residuals(reactants: Dict[str, float], products: Dict[str, float]) -> Dict[str, Tuple[float, float, float]]:
    e_in = element_totals(reactants)
    e_out = element_totals(products)
    elements = sorted(set(e_in) | set(e_out))
    result = {}
    for el in elements:
        a = e_in.get(el, 0.0)
        b = e_out.get(el, 0.0)
        result[el] = (a, b, b - a)
    return result


def balance_ok(a: float, b: float) -> bool:
    if not (math.isfinite(a) and math.isfinite(b)):
        return False
    scale = max(abs(a), abs(b))
    return abs(a - b) <= BAL_REL_TOL * scale if scale > 0 else True


# -----------------------------------------------------------------------------
# MODELO DE PRODUCTOS DE COMBUSTIÓN COMPLETA
# -----------------------------------------------------------------------------

def validate_distribution(d: Dict[str, float], label: str) -> None:
    if any(not math.isfinite(v) or v < 0 or v > 1 for v in d.values()):
        raise CombustionError(f"Las fracciones de {label} deben estar entre 0 y 1.")
    if abs(sum(d.values()) - 1.0) > 1e-8:
        raise CombustionError(f"Las fracciones de {label} deben sumar 1.")


def choose_product_model(elements: Dict[str, float]) -> Tuple[ProductModel, List[Measurement], List[str]]:
    model = ProductModel()
    measurements: List[Measurement] = []
    assumptions = ["En combustión completa, todo el C se expresa como CO2 y todo el H como H2O."]

    if elements.get("S", 0.0) > 0:
        choice = read_choice("El combustible contiene S. Indique los productos de azufre:", {
            "1": "Todo el S forma SO2",
            "2": "Todo el S forma SO3",
            "3": "Distribución especificada entre SO2 y SO3",
        })
        if choice == "1":
            model.sulfur = {"SO2": 1.0}
            assumptions.append("Todo el S del combustible forma SO2.")
        elif choice == "2":
            model.sulfur = {"SO3": 1.0}
            assumptions.append("Todo el S del combustible forma SO3.")
        else:
            m = read_measurement("Porcentaje del S que forma SO2 (%): ", min_value=0, max_value=100)
            measurements.append(m)
            f = m.value / 100.0
            model.sulfur = {"SO2": f, "SO3": 1.0 - f}
            assumptions.append(f"Distribución del S: {format_sig(m.value, m.sigfigs)} % a SO2 y el resto a SO3.")

    if elements.get("N", 0.0) > 0:
        choice = read_choice("El combustible contiene N. El programa NO asignará su producto automáticamente:", {
            "1": "Todo el N forma N2",
            "2": "Todo el N forma NO",
            "3": "Todo el N forma NO2",
            "4": "Distribución entre N2, NO y NO2",
        })
        if choice == "1":
            model.nitrogen = {"N2": 1.0}
            assumptions.append("Todo el N del combustible forma N2.")
        elif choice == "2":
            model.nitrogen = {"NO": 1.0}
            assumptions.append("Todo el N del combustible forma NO.")
        elif choice == "3":
            model.nitrogen = {"NO2": 1.0}
            assumptions.append("Todo el N del combustible forma NO2.")
        else:
            n2 = read_measurement("Porcentaje del N que termina como N2 (%): ", min_value=0, max_value=100)
            no = read_measurement("Porcentaje del N que termina como NO (%): ", min_value=0, max_value=100)
            no2 = read_measurement("Porcentaje del N que termina como NO2 (%): ", min_value=0, max_value=100)
            measurements += [n2, no, no2]
            total = n2.value + no.value + no2.value
            if abs(total - 100.0) > COMP_TOL_PERCENT:
                raise CombustionError(f"La distribución del N suma {total:.6g} %, no 100 %.")
            # normalización solo dentro de la pequeña tolerancia admitida
            model.nitrogen = {"N2": n2.value/total, "NO": no.value/total, "NO2": no2.value/total}
            assumptions.append("La distribución del N entre N2, NO y NO2 es la introducida por el usuario.")

    standard = {"C", "H", "O", "S", "N"}
    for el in sorted(set(elements) - standard):
        if elements[el] <= 0:
            continue
        print(f"\nEl combustible contiene {el}. Debe especificarse su producto oxidado.")
        formula = input(f"Fórmula del óxido que contiene {el} (p. ej., P2O5): ").strip()
        comp = parse_formula(formula)
        if el not in comp or "O" not in comp or set(comp) - {el, "O"}:
            raise CombustionError(
                f"Para el cálculo directo, el producto de {el} debe ser un óxido formado solo por {el} y O."
            )
        model.other_oxides[el] = canonical_formula(formula)
        assumptions.append(f"Todo el {el} forma {canonical_formula(formula)} (producto especificado por el usuario).")

    return model, measurements, assumptions


def complete_products_for_formula(formula: str, n_fuel: float, model: ProductModel) -> Dict[str, float]:
    atoms = parse_formula(formula)
    if not math.isfinite(n_fuel) or n_fuel < 0:
        raise CombustionError("La cantidad de combustible debe ser finita y no negativa.")
    products: Dict[str, float] = {}
    c = atoms.get("C", 0.0) * n_fuel
    h = atoms.get("H", 0.0) * n_fuel
    if c > 0:
        products["CO2"] = products.get("CO2", 0.0) + c
    if h > 0:
        products["H2O"] = products.get("H2O", 0.0) + h / 2.0

    s = atoms.get("S", 0.0) * n_fuel
    if s > 0:
        if not model.sulfur:
            raise CombustionError("No se ha definido el producto del S.")
        validate_distribution(model.sulfur, "S")
        for prod, frac in model.sulfur.items():
            # SO2/SO3 contienen un átomo de S
            products[prod] = products.get(prod, 0.0) + s * frac

    n = atoms.get("N", 0.0) * n_fuel
    if n > 0:
        if not model.nitrogen:
            raise CombustionError("No se ha definido el producto del N.")
        validate_distribution(model.nitrogen, "N")
        for prod, frac in model.nitrogen.items():
            nat = parse_formula(prod).get("N", 0.0)
            products[prod] = products.get(prod, 0.0) + n * frac / nat

    for el, oxide in model.other_oxides.items():
        amount_el = atoms.get(el, 0.0) * n_fuel
        if amount_el > 0:
            coeff = parse_formula(oxide)[el]
            products[oxide] = products.get(oxide, 0.0) + amount_el / coeff
    return products


def oxygen_stoich_formula(formula: str, n_fuel: float, model: ProductModel) -> Tuple[float, Dict[str, float]]:
    products = complete_products_for_formula(formula, n_fuel, model)
    o_products = element_totals(products).get("O", 0.0)
    o_fuel = parse_formula(formula).get("O", 0.0) * n_fuel
    o2 = (o_products - o_fuel) / 2.0
    escala_oxigeno = max(abs(o_products), abs(o_fuel))
    if o2 < -BAL_REL_TOL * escala_oxigeno:
        raise CombustionError(
            "El modelo especificado conduce a una necesidad externa de O2 negativa. "
            "Revise la sustancia y los productos adoptados."
        )
    return max(0.0, o2), products


def total_atoms_from_mixture(components: List[Tuple[str, float, bool]]) -> Dict[str, float]:
    # bool = reactivo; los inertes se contabilizan aparte cuando se construyen las corrientes.
    totals: Dict[str, float] = {}
    for formula, n, reactive in components:
        if not reactive:
            continue
        for el, a in parse_formula(formula).items():
            totals[el] = totals.get(el, 0.0) + a*n
    return totals


def complete_products_for_mixture(components: List[Tuple[str, float, bool]], model: ProductModel) -> Tuple[float, Dict[str, float]]:
    products: Dict[str, float] = {}
    o_fuel = 0.0
    for formula, n, reactive in components:
        if reactive:
            p = complete_products_for_formula(formula, n, model)
            for sp, v in p.items():
                products[sp] = products.get(sp, 0.0) + v
            o_fuel += parse_formula(formula).get("O", 0.0) * n
        else:
            products[formula] = products.get(formula, 0.0) + n
    o_products_reaction = element_totals({k: v for k, v in products.items() if True}).get("O", 0.0)
    # Restar oxígeno de componentes inertes que pasan sin reaccionar, para que no influya
    # en la necesidad de O2 de los reactivos.
    inert_o = sum(parse_formula(f).get("O", 0.0)*n for f, n, r in components if not r)
    o2 = (o_products_reaction - inert_o - o_fuel) / 2.0
    escala_oxigeno = max(abs(o_products_reaction), abs(inert_o), abs(o_fuel))
    if o2 < -BAL_REL_TOL * escala_oxigeno:
        raise CombustionError("La mezcla conduce a una necesidad externa de O2 negativa.")
    return max(0.0, o2), products


# -----------------------------------------------------------------------------
# OXIDANTE / AIRE
# -----------------------------------------------------------------------------

def choose_oxidizer(*, allow_custom: bool = True) -> Oxidizer:
    choices = {
        "1": "Aire seco del capítulo: 21,0 % O2 y 79,0 % N2",
        "2": "Oxígeno puro",
    }
    if allow_custom:
        choices["3"] = "Mezcla oxidante de composición especificada"
    choice = read_choice("Seleccione el comburente:", choices)
    if choice == "1":
        return Oxidizer(
            "aire seco",
            {"O2": DEFAULT_AIR_O2, "N2": DEFAULT_AIR_N2},
            DEFAULT_AIR_SF,
            ["Aire seco representado por 21,0 % molar de O2 y 79,0 % molar de N2."],
        )
    if choice == "2":
        return Oxidizer("O2 puro", {"O2": 1.0}, 999, ["El comburente es O2 puro."])

    ncomp = read_int("Número total de componentes de la mezcla oxidante (incluido O2): ", 1, 20)
    comp: Dict[str, float] = {}
    ms: List[Measurement] = []
    for i in range(ncomp):
        formula = canonical_formula(input(f"  Fórmula del componente {i+1}: ").strip())
        parse_formula(formula)
        m = read_measurement(f"  Porcentaje molar de {formula} (%): ", min_value=0, max_value=100)
        comp[formula] = comp.get(formula, 0.0) + m.value
        ms.append(m)
    total = sum(comp.values())
    if abs(total - 100.0) > COMP_TOL_PERCENT:
        raise CombustionError(f"La composición del comburente suma {total:.6g} %, no 100 %.")
    comp = {k: v/total for k, v in comp.items()}
    if comp.get("O2", 0.0) <= 0:
        raise CombustionError("La mezcla oxidante debe contener O2.")
    sf = min_sf(ms)
    return Oxidizer(
        "mezcla oxidante",
        comp,
        sf,
        ["Los componentes distintos de O2 de la mezcla oxidante se consideran no reactivos y pasan sin transformación."],
    )


def oxidizer_amount_for_o2(o2: float, oxidizer: Oxidizer) -> float:
    if oxidizer.y_o2 <= 0:
        raise CombustionError("El comburente no contiene O2.")
    return o2 / oxidizer.y_o2


def carrier_products(oxidizer: Oxidizer, n_oxidizer: float) -> Dict[str, float]:
    return {sp: y*n_oxidizer for sp, y in oxidizer.composition.items() if sp != "O2" and y*n_oxidizer > 0}


def choose_supply(o2_st: float, oxidizer: Oxidizer, *, complete_required: bool) -> Tuple[float, float, List[Measurement], List[str]]:
    """Devuelve n_oxidizer_real, o2_real, mediciones, hipótesis."""
    n_theor = oxidizer_amount_for_o2(o2_st, oxidizer)
    mode = read_choice("¿Cómo se especifica el comburente real?", {
        "1": "Cantidad teórica (sin exceso)",
        "2": "Porcentaje de exceso",
        "3": "Porcentaje de defecto",
        "4": "Cantidad real total de comburente",
        "5": "Cantidad real de O2 suministrado",
    })
    ms: List[Measurement] = []
    assumptions: List[str] = []
    if mode == "1":
        n_real = n_theor
    elif mode == "2":
        m = read_measurement("Exceso de comburente (% sobre el teórico): ", min_value=0)
        ms.append(m)
        n_real = n_theor * (1.0 + m.value/100.0)
    elif mode == "3":
        m = read_measurement("Defecto de comburente (% sobre el teórico): ", min_value=0, max_value=100)
        ms.append(m)
        n_real = n_theor * (1.0 - m.value/100.0)
    elif mode == "4":
        m = read_measurement("Cantidad real total de comburente (mol o unidad molar coherente): ", min_value=0)
        ms.append(m)
        n_real = m.value
    else:
        m = read_measurement("Cantidad real de O2 suministrado (mol o unidad molar coherente): ", min_value=0)
        ms.append(m)
        n_real = m.value / oxidizer.y_o2
    o2_real = n_real * oxidizer.y_o2
    if complete_required and o2_real + BAL_REL_TOL * o2_st < o2_st:
        deficit = 100*(1-o2_real/o2_st) if o2_st > 0 else 0.0
        raise CombustionError(
            f"El O2 suministrado es insuficiente para la combustión completa especificada "
            f"(defecto aproximado {deficit:.6g} %). Use la opción 5 y defina los productos de combustión incompleta."
        )
    return n_real, o2_real, ms, assumptions


# -----------------------------------------------------------------------------
# COMPOSICIONES DE GASES
# -----------------------------------------------------------------------------

def gas_compositions(products: Dict[str, float], sf: int) -> Tuple[Dict[str, float], Dict[str, float], float, float]:
    # Se consideran gaseosas todas las especies de esta corriente. En un problema de
    # combustión del capítulo, esta función se usa con especies gaseosas explícitas.
    if any(not math.isfinite(n) or n < 0 for n in products.values()):
        raise CombustionError("Las cantidades de gases deben ser finitas y no negativas.")
    wet_total = sum(v for v in products.values() if v > 0)
    if wet_total <= 0:
        raise CombustionError("No hay gases de salida para calcular una composición.")
    wet = {sp: n/wet_total for sp, n in products.items() if n > 0}
    dry_total = sum(v for sp, v in products.items() if sp != "H2O" and v > 0)
    dry = {sp: n/dry_total for sp, n in products.items() if sp != "H2O" and n > 0} if dry_total > 0 else {}
    return wet, dry, wet_total, dry_total


def print_species_amounts(species: Dict[str, float], sf: int, unit: str = "mol") -> None:
    for sp in sorted(species):
        if species[sp] > 0:
            print(f"  {sp:>10s}: {format_sig(species[sp], sf)} {unit}")


def print_composition(comp: Dict[str, float], sf: int) -> None:
    for sp in sorted(comp):
        print(f"  {sp:>10s}: {fmt_percent(comp[sp], sf)}")


# -----------------------------------------------------------------------------
# OPCIÓN 1
# -----------------------------------------------------------------------------

def option1_stoich_air() -> None:
    print_header("1. OXÍGENO ESTEQUIOMÉTRICO Y AIRE TEÓRICO")
    formula = canonical_formula(input("Fórmula del combustible: ").strip())
    atoms = parse_formula(formula)
    amount = read_measurement("Cantidad de combustible (mol o unidad molar coherente): ", min_value=0)
    model, model_ms, assumptions = choose_product_model(atoms)
    oxidizer = choose_oxidizer()
    o2_st, products = oxygen_stoich_formula(formula, amount.value, model)
    n_ox_theor = oxidizer_amount_for_o2(o2_st, oxidizer)
    sf = min_sf(amount, model_ms, oxidizer.sigfigs)

    print_data_assumptions(
        [f"Combustible: {formula}", f"Cantidad: {amount.raw} mol (o unidad molar coherente)", f"Comburente: {oxidizer.name}"],
        assumptions + oxidizer.assumptions,
    )
    print("\nRESULTADOS")
    print(f"  O2 estequiométrico: {format_sig(o2_st, sf)} mol")
    print(f"  Comburente teórico: {format_sig(n_ox_theor, sf)} mol")
    if oxidizer.name == "aire seco":
        print(f"  N2 asociado: {format_sig(n_ox_theor*oxidizer.composition['N2'], sf)} mol")
    print("  Productos de combustión completa correspondientes:")
    print_species_amounts(products, sf)

    react = {formula: amount.value, "O2": o2_st}
    prod = dict(products)
    residuals = balance_residuals(react, prod)
    checks = [(balance_ok(a,b), f"Balance de {el}: entrada={format_sig(a,sf)}, salida={format_sig(b,sf)}") for el,(a,b,_) in residuals.items()]
    print_checks(checks)


# -----------------------------------------------------------------------------
# OPCIÓN 2
# -----------------------------------------------------------------------------

def option2_complete() -> None:
    print_header("2. COMBUSTIÓN COMPLETA CON COMBURENTE")
    formula = canonical_formula(input("Fórmula del combustible: ").strip())
    atoms = parse_formula(formula)
    amount = read_measurement("Cantidad de combustible (mol o unidad molar coherente): ", min_value=0)
    model, model_ms, assumptions = choose_product_model(atoms)
    oxidizer = choose_oxidizer()
    o2_st, reaction_products = oxygen_stoich_formula(formula, amount.value, model)
    n_theor = oxidizer_amount_for_o2(o2_st, oxidizer)
    n_real, o2_real, supply_ms, supply_ass = choose_supply(o2_st, oxidizer, complete_required=True)

    products = dict(reaction_products)
    for sp, n in carrier_products(oxidizer, n_real).items():
        products[sp] = products.get(sp, 0.0) + n
    o2_out = o2_real - o2_st
    if o2_out > TOL:
        products["O2"] = products.get("O2", 0.0) + o2_out

    sf = min_sf(amount, model_ms, supply_ms, oxidizer.sigfigs)
    lam = o2_real/o2_st if o2_st > TOL else float("nan")
    excess = (lam-1)*100 if o2_st > TOL else float("nan")
    wet, dry, ntw, ntd = gas_compositions(products, sf)

    print_data_assumptions(
        [f"Combustible: {formula}", f"Cantidad: {amount.raw} mol", f"Comburente: {oxidizer.name}"],
        assumptions + oxidizer.assumptions + supply_ass + ["Se exige combustión completa; un suministro inferior al O2 estequiométrico se rechaza."],
    )
    print("\nRESULTADOS")
    print(f"  O2 estequiométrico: {format_sig(o2_st, sf)} mol")
    print(f"  Comburente teórico: {format_sig(n_theor, sf)} mol")
    print(f"  Comburente real: {format_sig(n_real, sf)} mol")
    print(f"  O2 real suministrado: {format_sig(o2_real, sf)} mol")
    if o2_st > TOL:
        print(f"  Factor de aire lambda: {format_sig(lam, sf)}")
        print(f"  Exceso de comburente: {format_sig(excess, sf)} %")
    print(f"  O2 sin reaccionar: {format_sig(max(0.0,o2_out), sf)} mol")
    print("\n  Gases/productos de salida:")
    print_species_amounts(products, sf)
    print(f"  Total en base húmeda: {format_sig(ntw, sf)} mol")
    print(f"  Total en base seca:   {format_sig(ntd, sf)} mol")
    print("\n  Composición molar, base húmeda:")
    print_composition(wet, sf)
    print("\n  Composición molar, base seca:")
    print_composition(dry, sf)

    react = {formula: amount.value}
    for sp, y in oxidizer.composition.items():
        react[sp] = react.get(sp, 0.0) + y*n_real
    residuals = balance_residuals(react, products)
    checks = [(balance_ok(a,b), f"Balance de {el}: entrada={format_sig(a,sf)}, salida={format_sig(b,sf)}") for el,(a,b,_) in residuals.items()]
    checks.append((all(n >= -TOL for n in products.values()), "No aparecen cantidades negativas en los productos."))
    print_checks(checks)


# -----------------------------------------------------------------------------
# OPCIÓN 3
# -----------------------------------------------------------------------------

def option3_mixture() -> None:
    print_header("3. COMBUSTIÓN DE UNA MEZCLA DE COMBUSTIBLES")
    n_total = read_measurement("Cantidad total de mezcla combustible (mol o unidad molar coherente): ", min_value=0)
    ncomp = read_int("Número de componentes de la mezcla: ", 1, 20)
    entries = []
    frac_ms: List[Measurement] = []
    total_pct = 0.0
    for i in range(ncomp):
        formula = canonical_formula(input(f"Fórmula del componente {i+1}: ").strip())
        parse_formula(formula)
        pct = read_measurement(f"Porcentaje molar de {formula} (%): ", min_value=0, max_value=100)
        reactive = read_yes_no(f"¿{formula} se considera combustible/reactivo en este modelo?", default=True)
        entries.append((formula, pct, reactive))
        frac_ms.append(pct)
        total_pct += pct.value
    if abs(total_pct - 100.0) > COMP_TOL_PERCENT:
        raise CombustionError(f"La composición de la mezcla suma {total_pct:.6g} %, no 100 %.")
    components: List[Tuple[str, float, bool]] = [
        (f, n_total.value * p.value/total_pct, r) for f,p,r in entries
    ]
    reactive_atoms = total_atoms_from_mixture(components)
    model, model_ms, assumptions = choose_product_model(reactive_atoms)
    oxidizer = choose_oxidizer()
    o2_st, reaction_products = complete_products_for_mixture(components, model)
    n_theor = oxidizer_amount_for_o2(o2_st, oxidizer)
    n_real, o2_real, supply_ms, _ = choose_supply(o2_st, oxidizer, complete_required=True)

    products = dict(reaction_products)
    for sp, n in carrier_products(oxidizer, n_real).items():
        products[sp] = products.get(sp, 0.0) + n
    if o2_real - o2_st > TOL:
        products["O2"] = products.get("O2", 0.0) + (o2_real-o2_st)

    sf = min_sf(n_total, frac_ms, model_ms, supply_ms, oxidizer.sigfigs)
    wet, dry, ntw, ntd = gas_compositions(products, sf)
    data = [f"Cantidad total de mezcla: {n_total.raw} mol", f"Comburente: {oxidizer.name}"]
    for f,p,r in entries:
        data.append(f"{f}: {p.raw} % molar ({'reactivo' if r else 'no reactivo'})")
    print_data_assumptions(data, assumptions + oxidizer.assumptions + ["Los componentes marcados como no reactivos atraviesan el sistema sin transformación."])

    print("\nRESULTADOS")
    print(f"  O2 estequiométrico: {format_sig(o2_st,sf)} mol")
    print(f"  Comburente teórico: {format_sig(n_theor,sf)} mol")
    print(f"  Comburente real: {format_sig(n_real,sf)} mol")
    print("\n  Productos/gases de salida:")
    print_species_amounts(products, sf)
    print(f"  Total húmedo: {format_sig(ntw,sf)} mol; total seco: {format_sig(ntd,sf)} mol")
    print("\n  Composición húmeda:")
    print_composition(wet, sf)
    print("\n  Composición seca:")
    print_composition(dry, sf)

    react: Dict[str,float] = {}
    for f,n,_ in components:
        react[f] = react.get(f,0.0)+n
    for sp,y in oxidizer.composition.items():
        react[sp]=react.get(sp,0.0)+y*n_real
    res=balance_residuals(react,products)
    print_checks([(balance_ok(a,b),f"Balance de {el}: entrada={format_sig(a,sf)}, salida={format_sig(b,sf)}") for el,(a,b,_) in res.items()])


# -----------------------------------------------------------------------------
# OPCIÓN 4 - COMPOSICIÓN ELEMENTAL
# -----------------------------------------------------------------------------

def read_elemental_composition() -> Tuple[Measurement, Dict[str, Measurement], Measurement]:
    mass = read_measurement("Masa de combustible (g, kg u otra unidad de masa coherente): ", min_value=0)
    print("Introduzca la composición másica. Para elementos ausentes, escriba 0.")
    elem_ms: Dict[str, Measurement] = {}
    for el in ("C","H","O","S","N"):
        elem_ms[el] = read_measurement(f"  {el} (% en masa): ", min_value=0, max_value=100)
    nextra = read_int("  Número de elementos adicionales presentes (0 si no hay): ", 0, 10)
    for i in range(nextra):
        el = input(f"  Símbolo químico del elemento adicional {i+1}: ").strip()
        if el not in ATOMIC_MASS:
            raise CombustionError(f"No hay masa atómica incorporada para el elemento '{el}'.")
        if el in elem_ms:
            raise CombustionError(f"El elemento {el} ya se ha introducido.")
        elem_ms[el] = read_measurement(f"  {el} (% en masa): ", min_value=0, max_value=100)
    inert = read_measurement("  Componentes inertes/cenizas (% en masa): ", min_value=0, max_value=100)
    total = sum(m.value for m in elem_ms.values()) + inert.value
    if abs(total - 100.0) > COMP_TOL_PERCENT:
        raise CombustionError(f"La composición másica suma {total:.6g} %, no 100 %.")
    return mass, elem_ms, inert


def option4_elemental() -> None:
    print_header("4. COMBUSTIBLE DE COMPOSICIÓN ELEMENTAL CONOCIDA")
    mass, elem_ms, inert = read_elemental_composition()
    # Cantidades de átomos en 'mol' si la masa está en g. Si la masa está en kg,
    # numéricamente serían kmol. Se mantiene unidad molar coherente.
    atom_moles: Dict[str,float] = {}
    for el,m in elem_ms.items():
        if m.value > TOL:
            atom_moles[el] = mass.value*(m.value/100.0)/ATOMIC_MASS[el]
    model, model_ms, assumptions = choose_product_model(atom_moles)
    oxidizer = choose_oxidizer()

    products: Dict[str,float] = {}
    if atom_moles.get("C",0)>TOL: products["CO2"] = atom_moles["C"]
    if atom_moles.get("H",0)>TOL: products["H2O"] = atom_moles["H"]/2
    s=atom_moles.get("S",0)
    if s>TOL:
        for sp,fr in model.sulfur.items(): products[sp]=products.get(sp,0)+s*fr
    n=atom_moles.get("N",0)
    if n>TOL:
        for sp,fr in model.nitrogen.items():
            products[sp]=products.get(sp,0)+n*fr/parse_formula(sp)["N"]
    for el,oxide in model.other_oxides.items():
        if atom_moles.get(el,0)>TOL:
            products[oxide]=atom_moles[el]/parse_formula(oxide)[el]
    o_prod=element_totals(products).get("O",0.0)
    o_fuel=atom_moles.get("O",0.0)
    o2_st=(o_prod-o_fuel)/2
    if o2_st < -TOL:
        raise CombustionError("La composición y los productos especificados conducen a O2 estequiométrico negativo.")
    o2_st=max(0,o2_st)
    n_theor=oxidizer_amount_for_o2(o2_st,oxidizer)

    sf=min_sf(mass,list(elem_ms.values()),inert,model_ms,oxidizer.sigfigs)
    data=[f"Masa de combustible: {mass.raw}", "Composición elemental en masa: " + ", ".join(f"{el}={m.raw} %" for el,m in elem_ms.items()), f"Inertes/cenizas={inert.raw} %", f"Comburente={oxidizer.name}"]
    print_data_assumptions(data, assumptions+oxidizer.assumptions+["Las cantidades molares resultan en mol si la masa se introdujo en g y en kmol si se introdujo en kg."])
    print("\nRESULTADOS")
    for el,nv in atom_moles.items(): print(f"  Átomos de {el}: {format_sig(nv,sf)} mol de átomos (o unidad molar coherente)")
    print(f"  O2 estequiométrico: {format_sig(o2_st,sf)} mol")
    print(f"  Comburente teórico: {format_sig(n_theor,sf)} mol")
    print("  Productos formados a partir de los elementos combustibles:")
    print_species_amounts(products,sf)
    # comprobación solo de C,H,O,S,N convertidos; los inertes no tienen fórmula definida
    eout=element_totals(products)
    checks=[]
    for el,nin in atom_moles.items():
        if el=="O":
            nin_total=nin+2*o2_st
            nout=eout.get("O",0)
        else:
            nin_total=nin; nout=eout.get(el,0)
        checks.append((balance_ok(nin_total,nout),f"Balance de {el}: entrada={format_sig(nin_total,sf)}, salida={format_sig(nout,sf)}"))
    print_checks(checks)


# -----------------------------------------------------------------------------
# OPCIÓN 5 - INCOMPLETA
# -----------------------------------------------------------------------------

def option5_incomplete() -> None:
    print_header("5. COMBUSTIÓN INCOMPLETA")
    formula=canonical_formula(input("Fórmula del combustible (modelo C/H/O): ").strip())
    atoms=parse_formula(formula)
    extra=set(atoms)-{"C","H","O"}
    if extra:
        raise CombustionError("Esta modalidad de combustión incompleta admite compuestos C/H/O. Para otros elementos use un planteamiento explícito y la opción 8 para comprobarlo.")
    if atoms.get("C",0)<=TOL:
        raise CombustionError("La modalidad CO2/CO requiere un combustible que contenga carbono.")
    amount=read_measurement("Cantidad alimentada de combustible (mol): ",min_value=0)
    conv=read_measurement("Conversión del combustible (%): ",min_value=0,max_value=100)
    frac_co2=read_measurement("Fracción del carbono REACCIONADO que forma CO2 (%): ",min_value=0,max_value=100)
    x=conv.value/100
    f=frac_co2.value/100
    n_reac=amount.value*x
    n_unreact=amount.value-n_reac
    c_reac=atoms.get("C",0)*n_reac
    h_reac=atoms.get("H",0)*n_reac
    o_reac=atoms.get("O",0)*n_reac
    co2=c_reac*f
    co=c_reac*(1-f)
    h2o=h_reac/2
    o_atoms_products=2*co2+co+h2o
    o2_consumed=(o_atoms_products-o_reac)/2
    escala_oxigeno = max(abs(o_atoms_products), abs(o_reac))
    if o2_consumed < -BAL_REL_TOL * escala_oxigeno:
        raise CombustionError("La distribución indicada conduce a consumo de O2 negativo. Revise las hipótesis.")
    o2_consumed=max(0,o2_consumed)
    # O2 estequiométrico para combustión completa del combustible ALIMENTADO
    full_model=ProductModel()
    o2_st,_=oxygen_stoich_formula(formula,amount.value,full_model)
    oxidizer=choose_oxidizer()
    mode=read_choice("Suministro de comburente para la combustión incompleta:",{
        "1":"La cantidad justa para formar los productos especificados (O2 de salida = 0)",
        "2":"Cantidad real total de comburente conocida",
        "3":"Cantidad real de O2 conocida",
    })
    supply_ms=[]
    if mode=="1":
        o2_real=o2_consumed
        n_oxid=o2_real/oxidizer.y_o2
    elif mode=="2":
        m=read_measurement("Cantidad real total de comburente (mol): ",min_value=0); supply_ms=[m]
        n_oxid=m.value; o2_real=n_oxid*oxidizer.y_o2
    else:
        m=read_measurement("Cantidad real de O2 suministrado (mol): ",min_value=0); supply_ms=[m]
        o2_real=m.value; n_oxid=o2_real/oxidizer.y_o2
    escala_suministro = max(abs(o2_real), abs(o2_consumed))
    if o2_real < o2_consumed and o2_consumed - o2_real > BAL_REL_TOL * escala_suministro:
        raise CombustionError("El O2 suministrado no basta para producir simultáneamente las cantidades de CO2, CO y H2O especificadas.")
    products={"CO2":co2,"CO":co,"H2O":h2o}
    if n_unreact>0: products[formula]=n_unreact
    for sp,nv in carrier_products(oxidizer,n_oxid).items(): products[sp]=products.get(sp,0)+nv
    if o2_real-o2_consumed>0: products["O2"]=products.get("O2",0)+(o2_real-o2_consumed)
    sf=min_sf(amount,conv,frac_co2,supply_ms,oxidizer.sigfigs)
    lam=o2_real/o2_st if o2_st>0 else float("nan")
    deviation=(lam-1)*100 if o2_st>0 else float("nan")
    wet,dry,ntw,ntd=gas_compositions(products,sf)

    print_data_assumptions([
        f"Combustible={formula}; alimentado={amount.raw} mol",
        f"Conversión={conv.raw} %",
        f"Carbono reaccionado a CO2={frac_co2.raw} %; el resto a CO",
        f"Comburente={oxidizer.name}",
    ],oxidizer.assumptions+[
        "El H del combustible que reacciona forma H2O.",
        "El combustible no convertido abandona el sistema sin reaccionar.",
        "La distribución CO2/CO ha sido especificada por el usuario; el programa no la predice.",
    ])
    print("\nRESULTADOS")
    print(f"  Combustible reaccionado: {format_sig(n_reac,sf)} mol")
    print(f"  Combustible sin reaccionar: {format_sig(n_unreact,sf)} mol")
    print(f"  O2 consumido para los productos especificados: {format_sig(o2_consumed,sf)} mol")
    print(f"  O2 estequiométrico para combustión completa de la alimentación: {format_sig(o2_st,sf)} mol")
    print(f"  O2 realmente suministrado: {format_sig(o2_real,sf)} mol")
    if o2_st>0:
        if deviation>=-TOL: print(f"  Exceso respecto a combustión completa: {format_sig(max(0,deviation),sf)} %")
        else: print(f"  Defecto respecto a combustión completa: {format_sig(-deviation,sf)} %")
    print("  Productos/gases:"); print_species_amounts(products,sf)
    print("\n  Composición en base seca:"); print_composition(dry,sf)
    print("\n  Composición en base húmeda:"); print_composition(wet,sf)
    react={formula:amount.value}
    for sp,y in oxidizer.composition.items(): react[sp]=react.get(sp,0)+y*n_oxid
    res=balance_residuals(react,products)
    print_checks([(balance_ok(a,b),f"Balance de {el}: entrada={format_sig(a,sf)}, salida={format_sig(b,sf)}") for el,(a,b,_) in res.items()])


# -----------------------------------------------------------------------------
# OPCIÓN 6 - ANÁLISIS DE GASES / ORSAT
# -----------------------------------------------------------------------------

def read_analysis_composition() -> Tuple[str, Dict[str,float], List[Measurement], List[str]]:
    basis=read_choice("Base del análisis:",{"1":"Base seca","2":"Base húmeda"})
    basis_name="seca" if basis=="1" else "húmeda"
    nsp=read_int("Número de especies cuya composición se introducirá explícitamente: ",1,30)
    comp_pct:Dict[str,float]={}; ms=[]
    for i in range(nsp):
        sp=canonical_formula(input(f"Especie {i+1}: ").strip()); parse_formula(sp)
        m=read_measurement(f"Porcentaje molar de {sp} (%): ",min_value=0,max_value=100)
        comp_pct[sp]=comp_pct.get(sp,0)+m.value; ms.append(m)
    assumptions=[]
    total=sum(comp_pct.values())
    if total < 100-COMP_TOL_PERCENT:
        if read_yes_no(f"La suma es {total:.6g} %. ¿Desea asignar el resto a una especie por diferencia?",default=True):
            sp=canonical_formula(input("Especie correspondiente al resto: ").strip()); parse_formula(sp)
            comp_pct[sp]=comp_pct.get(sp,0)+(100-total)
            assumptions.append(f"{sp} se ha obtenido por diferencia hasta 100 %.")
            total=100.0
        else:
            raise CombustionError("La composición no está completa. No se normaliza automáticamente.")
    if abs(total-100)>COMP_TOL_PERCENT:
        raise CombustionError(f"La composición suma {total:.6g} %, no 100 %.")
    # pequeña normalización por redondeo analítico
    comp={sp:p/total for sp,p in comp_pct.items()}
    return basis_name,comp,ms,assumptions


def option6_analysis() -> None:
    print_header("6. ANÁLISIS DE GASES DE COMBUSTIÓN")
    mode=read_choice("Modalidad:",{
        "1":"Composición molar/volumétrica conocida",
        "2":"Análisis Orsat a partir de volúmenes sucesivos",
    })
    assumptions=[]; ms=[]
    if mode=="1":
        basis,comp,ms,ass=read_analysis_composition(); assumptions+=ass
        base_moles=100.0  # base exacta elegida por el programa
        amounts={sp:y*base_moles for sp,y in comp.items()}
    else:
        basis="seca"
        v0=read_measurement("Volumen inicial V0 de gas seco: ",strictly_positive=True)
        v1=read_measurement("Volumen tras absorber CO2 (V1): ",min_value=0)
        v2=read_measurement("Volumen tras absorber después O2 (V2): ",min_value=0)
        v3=read_measurement("Volumen tras absorber después CO (V3): ",min_value=0)
        ms=[v0,v1,v2,v3]
        if not (v0.value+TOL>=v1.value>=v2.value-TOL and v2.value>=v3.value-TOL):
            raise CombustionError("En un Orsat ideal debe cumplirse V0 >= V1 >= V2 >= V3.")
        comp={"CO2":(v0.value-v1.value)/v0.value,"O2":(v1.value-v2.value)/v0.value,"CO":(v2.value-v3.value)/v0.value,"N2":v3.value/v0.value}
        amounts={sp:y*100 for sp,y in comp.items()}
        assumptions += ["Análisis Orsat clásico en base seca: absorción sucesiva de CO2, O2 y CO.","El gas residual se etiqueta N2 según el modelo elegido; si existen otros gases no absorbidos, esta identificación no sería válida."]
    sf=min_sf(ms)
    print_data_assumptions([f"Base del análisis: {basis}","Base de cálculo adoptada: 100 mol de gas analizado"],assumptions)
    print("\nRESULTADOS")
    print("  Composición del análisis:"); print_composition(comp,sf)
    print("  Cantidades sobre la base elegida:"); print_species_amounts(amounts,sf)
    c_atoms=element_totals({sp:n for sp,n in amounts.items() if "C" in parse_formula(sp)}).get("C",0.0)
    print(f"  Carbono contenido en la corriente analizada: {format_sig(c_atoms,sf)} mol de átomos C")

    if basis=="húmeda" and amounts.get("H2O",0)<100-TOL:
        dry_total=100-amounts.get("H2O",0)
        dry={sp:n/dry_total for sp,n in amounts.items() if sp!="H2O"} if dry_total>TOL else {}
        print("\n  Composición equivalente en base seca:"); print_composition(dry,sf)
    elif basis=="seca":
        print("\n  El análisis seco, por sí solo, no determina la cantidad de H2O.")

    if "N2" in amounts and read_yes_no("¿Se puede suponer que todo el N2 procede de aire seco 21,0/79,0?",default=True):
        o2_in=amounts["N2"]*(DEFAULT_AIR_O2/DEFAULT_AIR_N2)
        air=o2_in/DEFAULT_AIR_O2
        sf2=min(sf,DEFAULT_AIR_SF)
        print(f"  O2 que entró con el aire: {format_sig(o2_in,sf2)} mol")
        print(f"  Aire seco suministrado: {format_sig(air,sf2)} mol")
        print_checks([(True,"La inferencia de aire usa exclusivamente la hipótesis de que todo el N2 procede del aire seco del modelo.")])


# -----------------------------------------------------------------------------
# ÁLGEBRA LINEAL PEQUEÑA PARA CÁLCULO INVERSO
# -----------------------------------------------------------------------------

def solve_linear_system(A: List[List[float]], b: List[float], tol: float=1e-10) -> Tuple[str, Optional[List[float]]]:
    """Resuelve pequeños problemas lineales inversos sin dependencias externas.

    Equilibra filas y columnas y utiliza pivoteo completo. Rechaza sistemas
    numéricamente mal condicionados antes de dar una composición aparentemente
    única; no confunde esa decisión con una indeterminación química exacta.

    Devuelve ('unique'|'underdetermined'|'inconsistent', solución opcional).
    Un sistema casi singular provoca CombustionError con mensaje específico.
    La prueba de condicionamiento es NUMÉRICA; no sustituye el análisis de
    incertidumbre de datos experimentales.
    """
    if not A:
        return "underdetermined", None
    m = len(A)
    n = len(A[0])
    if n == 0 or len(b) != m or any(len(row) != n for row in A):
        raise CombustionError("Dimensiones incompatibles del sistema lineal inverso.")
    if not math.isfinite(tol) or tol <= 0 or tol >= 1:
        raise CombustionError("La tolerancia del solucionador debe ser finita y estar entre 0 y 1.")
    original = []
    rhs = []
    M = []
    for row, value in zip(A, b):
        coeffs = [float(v) for v in row]
        y = float(value)
        if not all(math.isfinite(v) for v in coeffs + [y]):
            raise CombustionError("El sistema inverso contiene coeficientes no finitos.")
        original.append(coeffs)
        rhs.append(y)
        row_scale = max(abs(v) for v in coeffs)
        if row_scale == 0.0:
            # Una ecuación 0 = b solo es compatible si b es exactamente 0.
            M.append([0.0] * n + [0.0 if y == 0.0 else math.copysign(1.0, y)])
        else:
            normalized = [v / row_scale for v in coeffs] + [y / row_scale]
            if not all(math.isfinite(v) for v in normalized):
                raise CombustionError("El sistema inverso excede el rango numérico de doble precisión.")
            M.append(normalized)

    # Preacondicionamiento de columnas: distingue escalas de las variables de
    # una dependencia real entre ecuaciones; no cambia las soluciones físicas.
    col_scales = [max(abs(M[r][c]) for r in range(m)) for c in range(n)]
    nonzero_col_scales = [value for value in col_scales if value > 0.0]
    if nonzero_col_scales and max(nonzero_col_scales) / min(nonzero_col_scales) > 1e9:
        raise CombustionError(
            "Sistema inverso con observables muy desiguales: no se pueden "
            "determinar de forma fiable todos los componentes con esta escala ")
    for r in range(m):
        for c in range(n):
            if col_scales[c] != 0.0:
                M[r][c] /= col_scales[c]
    perm = list(range(n))
    rank = 0
    near_singular_cutoff = 1e-8
    numerical_zero = min(1e-12, tol * 0.01)
    for k in range(min(m, n)):
        # Pivoteo completo para no favorecer un orden arbitrario de componentes.
        pivot_r, pivot_c = max(((r, c) for r in range(k, m) for c in range(k, n)),
                               key=lambda rc: abs(M[rc[0]][rc[1]]))
        largest = abs(M[pivot_r][pivot_c])
        if largest <= numerical_zero:
            break
        if largest < near_singular_cutoff:
            raise CombustionError(
                "Sistema inverso numéricamente mal condicionado: las magnitudes "
                "no permiten distinguir de forma fiable las cantidades de los componentes. "
                "Se requieren observables independientes de mayor precisión.")
        M[k], M[pivot_r] = M[pivot_r], M[k]
        for row in M:
            row[k], row[pivot_c] = row[pivot_c], row[k]
        perm[k], perm[pivot_c] = perm[pivot_c], perm[k]
        pivot_value = M[k][k]
        M[k] = [value / pivot_value for value in M[k]]
        for r in range(m):
            if r == k:
                continue
            factor = M[r][k]
            if factor != 0.0:
                M[r] = [M[r][c] - factor * M[k][c] for c in range(n+1)]
        rank += 1

    # Evaluación de ecuaciones sobrantes, incluidas restricciones redundantes.
    for r in range(rank, m):
        if all(abs(M[r][c]) <= tol for c in range(n)) and abs(M[r][n]) > tol:
            return "inconsistent", None
    if rank < n:
        return "underdetermined", None

    solution = [0.0] * n
    for k in range(n):
        original_col = perm[k]
        solution[original_col] = M[k][n] / col_scales[original_col]
    if not all(math.isfinite(value) for value in solution):
        raise CombustionError("La solución inversa no es representable con precisión finita.")

    # Contraste de residuos en unidades originales, sin un umbral absoluto de
    # moles que haga desaparecer datos cuando cambia la base de cálculo.
    for coeffs, observed in zip(original, rhs):
        estimated = math.fsum(c*x for c, x in zip(coeffs, solution))
        scale = max(abs(observed), math.fsum(abs(c*x) for c, x in zip(coeffs, solution)))
        if scale == 0.0:
            if estimated != 0.0:
                return "inconsistent", None
        elif abs(estimated-observed) > max(2e-9, 10*tol) * scale:
            return "inconsistent", None
    return "unique", solution


# -----------------------------------------------------------------------------
# OPCIÓN 7 - INVERSO
# -----------------------------------------------------------------------------

def inverse_hc_from_dry() -> None:
    print_header("7A. RELACIÓN H/C A PARTIR DE UN ANÁLISIS SECO")
    print("Modelo: combustible formado únicamente por C, H (y, opcionalmente, O conocido); productos carbonados CO2/CO; todo H -> H2O; todo N2 del gas procede del aire.")
    basis,comp,ms,ass=read_analysis_composition()
    if basis!="seca": raise CombustionError("Esta modalidad está formulada para un análisis en base seca.")
    # La inferencia H/C no es válida si hay especies ausentes del modelo.
    extra={sp for sp, frac in comp.items()
           if sp not in {"CO2", "CO", "O2", "N2"} and frac > TOL}
    if extra:
        raise CombustionError("El análisis seco contiene especies no admitidas en este modelo inverso: "
                              + ", ".join(sorted(extra)))
    for sp in ("CO2","CO","O2","N2"): comp.setdefault(sp,0.0)
    amounts={sp:100*y for sp,y in comp.items()}
    if comp["N2"]<=TOL: raise CombustionError("Se necesita N2 en el análisis para inferir el aire suministrado.")
    o2_in=amounts["N2"]*(DEFAULT_AIR_O2/DEFAULT_AIR_N2)
    c=amounts["CO2"]+amounts["CO"]
    if c<=TOL: raise CombustionError("No hay carbono en CO2/CO para calcular H/C.")
    mode=read_choice("Oxígeno contenido en el combustible:",{"1":"El combustible no contiene O","2":"Se conoce la relación atómica O/C del combustible"})
    extra_ms=[]
    if mode=="1": o_fuel_atoms=0.0; oc=0.0
    else:
        om=read_measurement("Relación atómica O/C: ",min_value=0); extra_ms=[om]; oc=om.value; o_fuel_atoms=oc*c
    # O balance: O fuel + 2 O2in = 2CO2 + CO + H2O + 2O2out
    h2o=o_fuel_atoms+2*o2_in-2*amounts["CO2"]-amounts["CO"]-2*amounts["O2"]
    if h2o < -1e-8:
        raise CombustionError("El balance de O exige una cantidad negativa de H2O: análisis o hipótesis incompatibles.")
    h2o=max(0,h2o); h=2*h2o; hc=h/c
    air=o2_in/DEFAULT_AIR_O2
    # Oxígeno teórico para llevar todo el combustible a CO2 y H2O. Como la base
    # de 100 mol de gas seco fija C, H y O del combustible, puede evaluarse aun
    # cuando el gas real contenga CO.
    o2_st = c + h/4.0 - o_fuel_atoms/2.0
    if o2_st <= TOL:
        raise CombustionError("No puede obtenerse un O2 estequiométrico positivo con las relaciones elementales deducidas.")
    air_factor = o2_in/o2_st
    air_deviation = 100.0*(air_factor-1.0)
    sf=min(min_sf(ms,extra_ms),DEFAULT_AIR_SF)
    print_data_assumptions(["Base: 100 mol de gas seco","Todo el N2 procede del aire seco","Composición seca: "+", ".join(f"{sp}={fmt_percent(y,min_sf(ms))}" for sp,y in comp.items())],ass+["El H del combustible aparece como H2O.","Las únicas especies carbonadas consideradas son CO2 y CO."])
    print("\nRESULTADOS")
    print(f"  O2 suministrado: {format_sig(o2_in,sf)} mol")
    print(f"  Aire suministrado: {format_sig(air,sf)} mol")
    print(f"  H2O calculada por balance de O: {format_sig(h2o,sf)} mol")
    print(f"  C del combustible: {format_sig(c,sf)} mol de átomos")
    print(f"  H del combustible: {format_sig(h,sf)} mol de átomos")
    print(f"  Relación atómica H/C: {format_sig(hc,sf)}")
    print(f"  O2 estequiométrico para combustión completa del combustible deducido: {format_sig(o2_st,sf)} mol")
    print(f"  Factor de aire lambda: {format_sig(air_factor,sf)}")
    if air_deviation >= -TOL:
        print(f"  Exceso de aire: {format_sig(max(0.0,air_deviation),sf)} %")
    else:
        print(f"  Defecto de aire: {format_sig(-air_deviation,sf)} %")
    # Balance O explícito
    oin=o_fuel_atoms+2*o2_in; oout=2*amounts["CO2"]+amounts["CO"]+h2o+2*amounts["O2"]
    print_checks([(balance_ok(oin,oout),f"Balance de O: entrada={format_sig(oin,sf)}, salida={format_sig(oout,sf)}"),(h2o>=-TOL,"La cantidad calculada de H2O es físicamente admisible.")])


def inverse_binary_fuel() -> None:
    print_header("7B. COMPOSICIÓN DE UNA MEZCLA BINARIA A PARTIR DE C Y H")
    print("Esta modalidad reproduce el planteamiento del apartado 14.10.2: se conocen las dos especies posibles del combustible y se deducen sus proporciones a partir de C y H totales.")
    f1=canonical_formula(input("Fórmula del componente 1: ").strip()); a1=parse_formula(f1)
    f2=canonical_formula(input("Fórmula del componente 2: ").strip()); a2=parse_formula(f2)
    if any(el not in {"C","H"} for el in set(a1)|set(a2)):
        raise CombustionError("Esta submodalidad binaria usa componentes formados solo por C y H. Para otros casos se necesitan relaciones adicionales explícitas.")
    source=read_choice("Datos elementales disponibles:",{"1":"Introducir directamente moles de átomos C y H","2":"Deducir C y H desde un análisis seco completo con aire"})
    ms=[]; assumptions=[]
    if source=="1":
        cm=read_measurement("Moles de átomos de C en la base elegida: ",min_value=0)
        hm=read_measurement("Moles de átomos de H en la base elegida: ",min_value=0)
        ms=[cm,hm]; c,h=cm.value,hm.value
    else:
        basis,comp,ams,ass=read_analysis_composition(); ms+=ams; assumptions+=ass
        if basis!="seca": raise CombustionError("Se requiere análisis seco en esta submodalidad.")
        for sp in ("CO2","CO","O2","N2"): comp.setdefault(sp,0)
        amounts={sp:100*y for sp,y in comp.items()}
        o2in=amounts["N2"]*DEFAULT_AIR_O2/DEFAULT_AIR_N2
        h2o=2*o2in-2*amounts["CO2"]-amounts["CO"]-2*amounts["O2"]
        if h2o<-TOL: raise CombustionError("El análisis conduce a H2O negativa bajo las hipótesis indicadas.")
        c=amounts["CO2"]+amounts["CO"]; h=2*max(0,h2o)
        assumptions += ["Todo el N2 procede del aire seco 21,0/79,0.","El combustible no contiene O; todo su H aparece como H2O."]
    A=[[a1.get("C",0),a2.get("C",0)],[a1.get("H",0),a2.get("H",0)]]
    status,sol=solve_linear_system(A,[c,h])
    if status=="underdetermined": raise CombustionError("Las dos especies tienen relaciones C/H linealmente dependientes; los datos no determinan una composición única.")
    if status=="inconsistent" or sol is None: raise CombustionError("Los balances de C y H son incompatibles con las especies propuestas.")
    escala_solucion = max(abs(v) for v in sol)
    if any(v < -BAL_REL_TOL * escala_solucion for v in sol):
        raise CombustionError("La solución exige una cantidad negativa de un componente: datos o modelo incompatibles.")
    n1,n2=max(0,sol[0]),max(0,sol[1]); nt=n1+n2
    if nt<=0: raise CombustionError("La cantidad total de combustible calculada es cero.")
    sf=min_sf(ms,DEFAULT_AIR_SF if source=="2" else None)
    print_data_assumptions([f"Especies candidatas: {f1}, {f2}",f"C total={format_sig(c,sf)}; H total={format_sig(h,sf)} mol de átomos"],assumptions)
    print("\nRESULTADOS")
    print(f"  {f1}: {format_sig(n1,sf)} mol; {fmt_percent(n1/nt,sf)}")
    print(f"  {f2}: {format_sig(n2,sf)} mol; {fmt_percent(n2/nt,sf)}")
    print_checks([(n1>=-TOL and n2>=-TOL,"Las cantidades deducidas son no negativas."),(abs(n1*a1.get('C',0)+n2*a2.get('C',0)-c)<1e-7*max(1,c),"Cierre del balance de C."),(abs(n1*a1.get('H',0)+n2*a2.get('H',0)-h)<1e-7*max(1,h),"Cierre del balance de H.")])


def inverse_cho_formula() -> None:
    print_header("7C. FÓRMULA CHO A PARTIR DE DATOS DE OXIDACIÓN COMPLETA")
    print("Modelo: CxHyOz + a O2 -> x CO2 + (y/2) H2O, por mol de sustrato.")
    co2=read_measurement("CO2 producido por mol de sustrato (mol/mol): ",min_value=0)
    o2=read_measurement("O2 consumido por mol de sustrato (mol/mol): ",min_value=0)
    h=read_measurement("Número de átomos de H por molécula/unidad fórmula (y): ",min_value=0)
    x=co2.value; y=h.value
    z=2*(x+y/4-o2.value)
    sf=min_sf(co2,o2,h)
    if z<-1e-8: raise CombustionError("Los datos exigirían z < 0; no son compatibles con una fórmula CxHyOz bajo este modelo.")
    z=max(0,z); h2o=y/2
    print_data_assumptions([f"CO2/sustrato={co2.raw}",f"O2/sustrato={o2.raw}",f"y={h.raw}"],["Oxidación completa: todo C -> CO2 y todo H -> H2O.","No se introducen otros elementos en la fórmula empírica."])
    print("\nRESULTADOS")
    print(f"  x = {format_sig(x,sf)}")
    print(f"  y = {format_sig(y,sf)}")
    print(f"  z = {format_sig(z,sf)}")
    print(f"  Fórmula obtenida (sin forzar subíndices enteros): C({format_sig(x,sf)})H({format_sig(y,sf)})O({format_sig(z,sf)})")
    print(f"  H2O producida: {format_sig(h2o,sf)} mol por mol de sustrato")
    oin=z+2*o2.value; oout=2*x+h2o
    print_checks([(balance_ok(oin,oout),f"Balance de O por mol de sustrato: entrada={format_sig(oin,sf)}, salida={format_sig(oout,sf)}"),(x>=-TOL and y>=-TOL and z>=-TOL,"Los subíndices deducidos son no negativos.")])



def cho_complete_coeffs(formula: str) -> Dict[str, float]:
    atoms = parse_formula(formula)
    if set(atoms) - {"C", "H", "O"}:
        raise CombustionError(
            f"La modalidad inversa lineal de combustión completa admite componentes C/H/O; {formula} contiene otros elementos."
        )
    c = atoms.get("C", 0.0)
    h = atoms.get("H", 0.0)
    o = atoms.get("O", 0.0)
    nu_o2 = c + h/4.0 - o/2.0
    if nu_o2 < -TOL:
        raise CombustionError(f"{formula} conduce a una necesidad de O2 negativa bajo el modelo CO2/H2O.")
    return {"C": c, "H": h, "O": o, "CO2": c, "H2O": h/2.0, "O2": max(0.0, nu_o2), "M": molar_mass(formula)}


def read_ratio_constraints(formulas: List[str]) -> Tuple[List[List[float]], List[float], List[Measurement], List[str]]:
    A: List[List[float]] = []
    b: List[float] = []
    ms: List[Measurement] = []
    labels: List[str] = []
    if len(formulas) < 2:
        return A, b, ms, labels
    nr = read_int("Número de relaciones molares conocidas entre componentes (0 si no hay): ", 0, 20)
    for k in range(nr):
        print("  Componentes disponibles:")
        for i, f in enumerate(formulas, 1):
            print(f"    {i}. {f}")
        i = read_int("  Índice del componente del numerador: ", 1, len(formulas)) - 1
        j = read_int("  Índice del componente del denominador: ", 1, len(formulas)) - 1
        if i == j:
            raise CombustionError("Una relación entre un componente y sí mismo no aporta una ecuación independiente.")
        r = read_measurement(f"  Relación n({formulas[i]})/n({formulas[j]}): ", min_value=0)
        row = [0.0] * len(formulas)
        row[i] = 1.0
        row[j] = -r.value
        A.append(row); b.append(0.0); ms.append(r)
        labels.append(f"n({formulas[i]})/n({formulas[j]})={r.raw}")
    return A, b, ms, labels


def inverse_known_components_observables() -> None:
    print_header("7B. MEZCLA CON ESPECIES CONOCIDAS A PARTIR DE MAGNITUDES ESTEQUIOMÉTRICAS")
    print("Se introducen especies químicas candidatas y magnitudes medibles (CO2, H2O, O2 consumido, cantidad total, etc.). El programa construye y comprueba el sistema lineal; no se introducen ecuaciones algebraicas.")
    ncomp = read_int("Número de componentes combustibles candidatos: ", 1, 10)
    formulas: List[str] = []
    coeffs: List[Dict[str,float]] = []
    for i in range(ncomp):
        f = canonical_formula(input(f"Fórmula del componente {i+1}: ").strip())
        if f in formulas:
            raise CombustionError("No repita la misma especie como dos componentes distintos.")
        formulas.append(f); coeffs.append(cho_complete_coeffs(f))

    neq = read_int("Número de magnitudes estequiométricas conocidas: ", 1, 20)
    A: List[List[float]] = []
    b: List[float] = []
    ms: List[Measurement] = []
    obs_labels: List[str] = []
    choices = {
        "1": "CO2 producido",
        "2": "H2O producida",
        "3": "O2 consumido",
        "4": "Cantidad total de combustible reaccionado",
        "5": "Moles de átomos de C del combustible",
        "6": "Moles de átomos de H del combustible",
        "7": "Moles de átomos de O del combustible",
        "8": "Masa total del combustible (g si las cantidades están en mol)",
    }
    for k in range(neq):
        ch = read_choice(f"Magnitud conocida {k+1}:", choices)
        if ch == "1": row = [c["CO2"] for c in coeffs]; label = "CO2 producido"
        elif ch == "2": row = [c["H2O"] for c in coeffs]; label = "H2O producida"
        elif ch == "3": row = [c["O2"] for c in coeffs]; label = "O2 consumido"
        elif ch == "4": row = [1.0 for _ in coeffs]; label = "cantidad total de combustible"
        elif ch == "5": row = [c["C"] for c in coeffs]; label = "átomos de C"
        elif ch == "6": row = [c["H"] for c in coeffs]; label = "átomos de H"
        elif ch == "7": row = [c["O"] for c in coeffs]; label = "átomos de O"
        else: row = [c["M"] for c in coeffs]; label = "masa total"
        m = read_measurement(f"Valor de {label} en la base elegida: ", min_value=0)
        A.append(row); b.append(m.value); ms.append(m); obs_labels.append(f"{label}={m.raw}")

    Ar, br, rms, rlabels = read_ratio_constraints(formulas)
    A.extend(Ar); b.extend(br); ms.extend(rms)
    status, sol = solve_linear_system(A, b)
    if status == "underdetermined":
        raise CombustionError("Las relaciones introducidas no son suficientes para determinar de forma única todas las cantidades de combustible.")
    if status == "inconsistent" or sol is None:
        raise CombustionError("Las magnitudes introducidas son incompatibles con las especies candidatas y el modelo de combustión completa.")
    if any(v < -1e-8 for v in sol):
        raise CombustionError("La única solución algebraica contiene una cantidad negativa de combustible; el modelo o los datos no son físicamente compatibles.")
    sol = [max(0.0, v) for v in sol]
    nt = sum(sol)
    if nt <= TOL:
        raise CombustionError("La solución conduce a cantidad total de combustible nula.")
    sf = min_sf(ms)

    co2 = sum(sol[i]*coeffs[i]["CO2"] for i in range(ncomp))
    h2o = sum(sol[i]*coeffs[i]["H2O"] for i in range(ncomp))
    o2st = sum(sol[i]*coeffs[i]["O2"] for i in range(ncomp))
    print_data_assumptions(
        ["Especies candidatas: " + ", ".join(formulas), "Magnitudes: " + "; ".join(obs_labels + rlabels)],
        ["Todas las especies candidatas se oxidan completamente: C -> CO2 y H -> H2O.", "Los datos se tratan como relaciones independientes; si no determinan una solución única, el programa se detiene."],
    )
    print("\nRESULTADOS")
    for f, n in zip(formulas, sol):
        print(f"  {f}: {format_sig(n,sf)}; fracción molar={fmt_percent(n/nt,sf)}")
    print(f"  Cantidad total de combustible reaccionado: {format_sig(nt,sf)}")
    print(f"  CO2 producido: {format_sig(co2,sf)}")
    print(f"  H2O producida: {format_sig(h2o,sf)}")
    print(f"  O2 consumido/estequiométrico: {format_sig(o2st,sf)}")

    react = {f:n for f,n in zip(formulas,sol)}
    react["O2"] = react.get("O2",0.0) + o2st
    prod = {"CO2":co2,"H2O":h2o}
    res = balance_residuals(react,prod)
    checks = [(balance_ok(a,bv),f"Balance de {el}: entrada={format_sig(a,sf)}, salida={format_sig(bv,sf)}") for el,(a,bv,_) in res.items()]
    print_checks(checks)


def inverse_complete_dry_known_components() -> None:
    print_header("7C. MEZCLA CONOCIDA A PARTIR DE UN ANÁLISIS SECO COMPLETO")
    print("Modelo lineal para combustión completa con aire seco. Permite incluir N2 o CO2 en el combustible como componentes no reactivos y relaciones molares conocidas entre componentes.")
    basis, comp, ams, ass = read_analysis_composition()
    if basis != "seca":
        raise CombustionError("Esta modalidad requiere análisis en base seca.")
    allowed = {"CO2","O2","N2"}
    extra = {sp for sp,y in comp.items() if y > TOL and sp not in allowed}
    if extra:
        raise CombustionError("Esta modalidad de combustión completa admite como gas seco CO2, O2 y N2. Especies adicionales: " + ", ".join(sorted(extra)))
    for sp in allowed: comp.setdefault(sp,0.0)
    observed = {sp:100.0*comp[sp] for sp in allowed}

    ncomp = read_int("Número de componentes posibles en el combustible: ",1,10)
    formulas: List[str] = []
    reactive: List[bool] = []
    coeffs: List[Optional[Dict[str,float]]] = []
    for i in range(ncomp):
        f = canonical_formula(input(f"Fórmula del componente {i+1}: ").strip()); parse_formula(f)
        if f in formulas: raise CombustionError("No repita componentes.")
        r = read_yes_no(f"¿{f} se oxida durante la combustión?", default=(f not in {"N2","CO2"}))
        if r:
            c = cho_complete_coeffs(f)
        else:
            if f not in {"N2","CO2"}:
                raise CombustionError("En esta modalidad inversa, los componentes no reactivos del combustible deben ser N2 o CO2.")
            c = None
        formulas.append(f); reactive.append(r); coeffs.append(c)

    # incógnitas: n_1 ... n_k, nO2_entrada
    A: List[List[float]] = []
    b: List[float] = []
    # CO2 de salida
    row=[]
    for f,r,c in zip(formulas,reactive,coeffs):
        row.append(c["CO2"] if r and c is not None else (1.0 if f=="CO2" else 0.0))
    row.append(0.0); A.append(row); b.append(observed["CO2"])
    # O2 de salida = O2 entrada - consumo
    row=[]
    for r,c in zip(reactive,coeffs): row.append(-c["O2"] if r and c is not None else 0.0)
    row.append(1.0); A.append(row); b.append(observed["O2"])
    # N2 de salida = N2 del aire + N2 del combustible
    air_ratio = DEFAULT_AIR_N2/DEFAULT_AIR_O2
    row=[1.0 if (not r and f=="N2") else 0.0 for f,r in zip(formulas,reactive)] + [air_ratio]
    A.append(row); b.append(observed["N2"])

    # Relaciones de componentes: se amplían con coeficiente 0 para O2 de entrada.
    Ar, br, rms, rlabels = read_ratio_constraints(formulas)
    for rr in Ar: A.append(rr+[0.0])
    b.extend(br)
    ms = list(ams)+rms

    if read_yes_no("¿Se conoce además la cantidad total de combustible en esta base?", default=False):
        tm = read_measurement("Cantidad total de combustible: ", min_value=0)
        A.append([1.0]*ncomp+[0.0]); b.append(tm.value); ms.append(tm)

    status, sol = solve_linear_system(A,b)
    if status=="underdetermined": raise CombustionError("El análisis y las relaciones adicionales no bastan para determinar de forma única la composición del combustible.")
    if status=="inconsistent" or sol is None: raise CombustionError("El análisis es incompatible con las especies y relaciones propuestas.")
    if any(v < -1e-8 for v in sol): raise CombustionError("La solución requiere una cantidad negativa de alguna especie o de O2 de entrada.")
    sol=[max(0.0,v) for v in sol]
    fuel=sol[:-1]; o2in=sol[-1]; nt=sum(fuel)
    if nt<=TOL: raise CombustionError("La cantidad de combustible calculada es nula.")
    o2st=sum(fuel[i]*coeffs[i]["O2"] for i in range(ncomp) if reactive[i] and coeffs[i] is not None)
    h2o=sum(fuel[i]*coeffs[i]["H2O"] for i in range(ncomp) if reactive[i] and coeffs[i] is not None)
    lam=o2in/o2st if o2st>TOL else float('nan')
    dev=100*(lam-1) if o2st>TOL else float('nan')
    sf=min(min_sf(ms),DEFAULT_AIR_SF)

    print_data_assumptions(
        ["Base: 100 mol de gas seco", "Análisis: "+", ".join(f"{sp}={fmt_percent(comp[sp],min_sf(ams))}" for sp in ("CO2","O2","N2")), "Componentes candidatos: "+", ".join(formulas)],
        ass+["Aire seco: 21,0 % O2 y 79,0 % N2.","Los componentes reactivos se queman completamente a CO2 y H2O; los N2/CO2 marcados no reactivos pasan sin transformación."],
    )
    print("\nRESULTADOS")
    for f,n in zip(formulas,fuel): print(f"  {f}: {format_sig(n,sf)} mol; fracción molar en combustible={fmt_percent(n/nt,sf)}")
    print(f"  O2 de entrada: {format_sig(o2in,sf)} mol")
    print(f"  Aire seco de entrada: {format_sig(o2in/DEFAULT_AIR_O2,sf)} mol")
    print(f"  H2O (no incluida en el análisis seco): {format_sig(h2o,sf)} mol")
    print(f"  O2 estequiométrico para combustión completa: {format_sig(o2st,sf)} mol")
    if o2st>TOL:
        if dev>=-TOL: print(f"  Exceso de aire: {format_sig(max(0.0,dev),sf)} %")
        else: print(f"  Defecto de aire: {format_sig(-dev,sf)} %")

    react={}
    for f,n in zip(formulas,fuel): react[f]=react.get(f,0)+n
    react["O2"]=react.get("O2",0)+o2in
    react["N2"]=react.get("N2",0)+air_ratio*o2in
    prod={"CO2":observed["CO2"],"O2":observed["O2"],"N2":observed["N2"],"H2O":h2o}
    res=balance_residuals(react,prod)
    checks=[(balance_ok(a,bv),f"Balance de {el}: entrada={format_sig(a,sf)}, salida={format_sig(bv,sf)}") for el,(a,bv,_) in res.items()]
    print_checks(checks)


def inverse_dry_co2_known_air_factor() -> None:
    print_header("7D. COMPOSICIÓN DE UNA MEZCLA DESDE CO2 SECO Y EXCESO DE AIRE")
    print("Modelo: combustión completa de componentes C/H/O con aire seco. Se conoce el porcentaje de CO2 en el gas seco y el factor de aire (o exceso).")
    co2pct=read_measurement("CO2 en el gas seco (% molar): ",min_value=0,max_value=100)
    spec=read_choice("Especificación del aire:",{"1":"Porcentaje de exceso de aire","2":"Factor de aire lambda"})
    if spec=="1":
        em=read_measurement("Exceso de aire (%): ",min_value=0); lam=1+em.value/100; lms=[em]
    else:
        lm=read_measurement("Factor de aire lambda: ",strictly_positive=True); lam=lm.value; lms=[lm]
    if lam < 1-TOL:
        raise CombustionError("Con lambda < 1 no puede imponerse simultáneamente combustión completa sin especificar otros productos.")
    ncomp=read_int("Número de componentes combustibles candidatos: ",1,10)
    formulas=[]; coeffs=[]
    for i in range(ncomp):
        f=canonical_formula(input(f"Fórmula del componente {i+1}: ").strip())
        if f in formulas: raise CombustionError("No repita componentes.")
        formulas.append(f); coeffs.append(cho_complete_coeffs(f))
    co2=co2pct.value  # sobre base 100 mol secos
    air_ratio=DEFAULT_AIR_N2/DEFAULT_AIR_O2
    factor=(lam-1)+air_ratio*lam
    A=[ [c["CO2"] for c in coeffs], [factor*c["O2"] for c in coeffs] ]
    b=[co2,100.0-co2]
    Ar,br,rms,rlabels=read_ratio_constraints(formulas)
    A.extend(Ar); b.extend(br)
    ms=[co2pct]+lms+rms
    status,sol=solve_linear_system(A,b)
    if status=="underdetermined": raise CombustionError("El CO2 seco y el factor de aire no bastan para determinar de forma única todos los componentes propuestos.")
    if status=="inconsistent" or sol is None: raise CombustionError("Los datos son incompatibles con las especies candidatas.")
    if any(v < -1e-8 for v in sol): raise CombustionError("La solución contiene una cantidad negativa de combustible.")
    sol=[max(0,v) for v in sol]; nt=sum(sol)
    o2st=sum(sol[i]*coeffs[i]["O2"] for i in range(ncomp)); o2in=lam*o2st
    o2out=o2in-o2st; n2=air_ratio*o2in; h2o=sum(sol[i]*coeffs[i]["H2O"] for i in range(ncomp))
    drytot=co2+o2out+n2
    sf=min(min_sf(ms),DEFAULT_AIR_SF)
    print_data_assumptions(["Base: 100 mol de gas seco",f"CO2 seco={co2pct.raw} %",f"lambda={format_sig(lam,sf)}","Componentes candidatos: "+", ".join(formulas)], ["Combustión completa: C -> CO2, H -> H2O.","Aire seco: 21,0 % O2 y 79,0 % N2."])
    print("\nRESULTADOS")
    for f,n in zip(formulas,sol): print(f"  {f}: {format_sig(n,sf)} mol; fracción molar={fmt_percent(n/nt,sf)}")
    print(f"  O2 estequiométrico: {format_sig(o2st,sf)} mol")
    print(f"  O2 real: {format_sig(o2in,sf)} mol")
    print(f"  H2O formada: {format_sig(h2o,sf)} mol")
    dry={"CO2":co2/drytot,"O2":o2out/drytot,"N2":n2/drytot}
    print("  Composición completa del gas seco:"); print_composition(dry,sf)
    checks=[(abs(drytot-100.0)<=1e-7,"La base seca reconstruida suma 100 mol."),(abs(100*dry["CO2"]-co2pct.value)<=1e-7,"Se reproduce el porcentaje de CO2 especificado."),(abs(o2in/o2st-lam)<=1e-9,"Se reproduce el factor de aire especificado.")]
    print_checks(checks)


def inverse_pure_from_stoich_o2() -> None:
    print_header("7E. CANTIDAD DE UN COMBUSTIBLE PURO A PARTIR DEL O2 ESTEQUIOMÉTRICO")
    formula=canonical_formula(input("Fórmula del combustible: ").strip()); atoms=parse_formula(formula)
    model,model_ms,ass=choose_product_model(atoms)
    o2per,_=oxygen_stoich_formula(formula,1.0,model)
    if o2per<=TOL: raise CombustionError("El combustible no requiere O2 positivo bajo el modelo especificado.")
    o2tot=read_measurement("Cantidad total de O2 estequiométrico indicada en el problema: ",min_value=0)
    if o2tot.value <= 0:
        raise CombustionError("El cálculo inverso requiere una cantidad estequiométrica de O2 estrictamente positiva.")
    nf=o2tot.value/o2per
    oxidizer=choose_oxidizer()
    realmode=read_choice("Dato de comburente real:",{"1":"Cantidad total de comburente","2":"Cantidad de O2 real"})
    if realmode=="1":
        rm=read_measurement("Cantidad real total de comburente: ",min_value=0); nreal=rm.value; o2real=nreal*oxidizer.y_o2
    else:
        rm=read_measurement("Cantidad real de O2: ",min_value=0); o2real=rm.value; nreal=o2real/oxidizer.y_o2
    lam=o2real/o2tot.value; dev=100*(lam-1)
    sf=min_sf(o2tot,rm,model_ms,oxidizer.sigfigs)
    print_data_assumptions([f"Combustible={formula}",f"O2 estequiométrico total={o2tot.raw}",f"Comburente real={oxidizer.name}"],ass+oxidizer.assumptions)
    print("\nRESULTADOS")
    print(f"  O2 estequiométrico por mol de {formula}: {format_sig(o2per,sf)} mol/mol")
    print(f"  Cantidad de {formula}: {format_sig(nf,sf)} mol")
    print(f"  Comburente real: {format_sig(nreal,sf)} mol; O2 real={format_sig(o2real,sf)} mol")
    if dev>=-TOL: print(f"  Exceso de aire/comburente: {format_sig(max(0,dev),sf)} %")
    else: print(f"  Defecto de aire/comburente: {format_sig(-dev,sf)} %")
    print_checks([(nf>=-TOL,"La cantidad de combustible calculada es no negativa."),(o2real>=-TOL,"La cantidad de O2 real es no negativa.")])

def option7_inverse() -> None:
    choice=read_choice("7. CÁLCULO INVERSO A PARTIR DE UN ANÁLISIS/DATOS GASEOSOS",{
        "1":"Determinar H/C, aire y exceso/defecto desde un análisis seco",
        "2":"Determinar cantidades de especies conocidas desde CO2/H2O/O2 u otras magnitudes",
        "3":"Determinar una mezcla (incluidos inertes N2/CO2) desde un análisis seco completo",
        "4":"Determinar una mezcla desde CO2 seco y un exceso/factor de aire conocido",
        "5":"Determinar una fórmula CxHyOz a partir de CO2, O2 y H conocido",
        "6":"Determinar cantidad de combustible puro desde su O2 estequiométrico total",
    })
    if choice=="1": inverse_hc_from_dry()
    elif choice=="2": inverse_known_components_observables()
    elif choice=="3": inverse_complete_dry_known_components()
    elif choice=="4": inverse_dry_co2_known_air_factor()
    elif choice=="5": inverse_cho_formula()
    else: inverse_pure_from_stoich_o2()


# -----------------------------------------------------------------------------
# OPCIÓN 8 - COMPROBADOR GENERAL
# -----------------------------------------------------------------------------

def read_species_stream(label: str) -> Tuple[Dict[str,float],List[Measurement]]:
    nsp=read_int(f"Número de especies en {label}: ",1,50)
    species={}; ms=[]
    for i in range(nsp):
        f=canonical_formula(input(f"  Fórmula de la especie {i+1}: ").strip()); parse_formula(f)
        m=read_measurement(f"  Cantidad de {f} (mol o unidad molar coherente): ",min_value=0)
        species[f]=species.get(f,0)+m.value; ms.append(m)
    return species,ms


def option8_check() -> None:
    print_header("8. COMPROBACIÓN DE UN PROBLEMA DE COMBUSTIÓN")
    print("Introduzca las cantidades de entrada y salida obtenidas en su resolución manual. El programa comprobará los balances elementales sin imponer una distribución de productos.")
    react,rms=read_species_stream("la entrada")
    prod,pms=read_species_stream("la salida")
    sf=min_sf(rms,pms)
    res=balance_residuals(react,prod)
    print_data_assumptions(["Corriente(s) de entrada: "+", ".join(f"{sp}={format_sig(n,sf)}" for sp,n in react.items()),"Corriente(s) de salida: "+", ".join(f"{sp}={format_sig(n,sf)}" for sp,n in prod.items())],["No se asignan productos automáticamente; se comprueba exactamente el modelo introducido por el usuario."])
    print("\nRESULTADOS DE LOS BALANCES")
    checks=[]
    for el,(a,b,r) in res.items():
        ok=balance_ok(a,b); checks.append((ok,f"{el}: entrada={format_sig(a,sf)}, salida={format_sig(b,sf)}, residuo(salida-entrada)={format_sig(r,sf)}"))
    # Comprobación opcional del aire si hay O2 y N2 en la entrada
    if react.get("O2",0)>TOL and react.get("N2",0)>TOL:
        ratio=react["N2"]/react["O2"]
        if read_yes_no("¿Desea comprobar si el O2/N2 de entrada corresponde al aire seco 21,0/79,0?",default=True):
            target=DEFAULT_AIR_N2/DEFAULT_AIR_O2
            rel=abs(ratio-target)/target
            checks.append((rel<=0.005,f"Relación N2/O2 de entrada={format_sig(ratio,sf)}; modelo de aire seco={format_sig(target,3)}."))
    checks.append((all(v>=-TOL for v in react.values()) and all(v>=-TOL for v in prod.values()),"No existen cantidades negativas."))
    print_checks(checks)
    if all(ok for ok,_ in checks):
        print("\n  Resultado: el conjunto de datos supera las comprobaciones seleccionadas.")
    else:
        print("\n  Resultado: existe al menos una incompatibilidad. No debe aceptarse la solución sin revisar el planteamiento.")


# -----------------------------------------------------------------------------
# AUTOPRUEBAS NUMÉRICAS BASADAS EN EJEMPLOS/PROBLEMAS DEL CAPÍTULO
# -----------------------------------------------------------------------------

def approx(a: float,b: float,rtol=2e-3,atol=1e-9) -> bool:
    return abs(a-b)<=max(atol,rtol*max(abs(a),abs(b)))


def run_self_tests(verbose: bool=True) -> bool:
    tests=[]
    def check(name,condition): tests.append((name,bool(condition)))

    # Ejemplo 14.3: 10 mol propano, 20% exceso de aire
    model=ProductModel(); o2,p=oxygen_stoich_formula("C3H8",10.0,model)
    o2_real=o2*1.2; n2=o2_real*(DEFAULT_AIR_N2/DEFAULT_AIR_O2)
    products=dict(p); products["O2"]=o2_real-o2; products["N2"]=n2
    wet,dry,_,_=gas_compositions(products,3)
    check("14.3 O2 estequiométrico",approx(o2,50.0))
    check("14.3 CO2",approx(p["CO2"],30.0))
    check("14.3 H2O",approx(p["H2O"],40.0))
    check("14.3 N2 ~226",approx(n2,225.714,rtol=3e-3))
    check("14.3 yCO2 seca ~0.113",approx(dry["CO2"],0.1129,rtol=4e-3))

    # Ejemplo 14.4: 2 mol C2H6S -> SO2
    model=ProductModel(sulfur={"SO2":1.0})
    o2,p=oxygen_stoich_formula("C2H6S",2.0,model)
    check("14.4 O2=9",approx(o2,9.0))
    check("14.4 productos",approx(p["CO2"],4.0) and approx(p["H2O"],6.0) and approx(p["SO2"],2.0))

    # Ejemplo 14.5: composición elemental 84%C 12%H 4%O sobre 100g
    nc=84/ATOMIC_MASS["C"]; nh=12/ATOMIC_MASS["H"]; no=4/ATOMIC_MASS["O"]
    o2=nc+nh/4-no/2
    check("14.5 O2 ~9.84",approx(o2,9.84,rtol=5e-3))

    # Ejemplo 14.6: CH4, 60% CO2 40% CO => O2 consumido 18 mol para 10 mol
    n=10; co2=0.6*n; co=0.4*n; h2o=2*n; o2cons=(2*co2+co+h2o)/2
    check("14.6 O2 consumido=18",approx(o2cons,18.0))

    # Ejemplo 14.8: análisis 11.41 CO2, 2.09 O2, 86.50 N2, base 100
    o2in=86.50*(DEFAULT_AIR_O2/DEFAULT_AIR_N2)
    h2o=2*o2in-2*11.41-2*2.09
    hc=2*h2o/11.41
    status,sol=solve_linear_system([[1,2],[4,6]],[11.41,2*h2o])
    check("14.8 O2 in ~23.0",approx(o2in,23.0,rtol=5e-3))
    check("14.8 H/C ~3.33",approx(hc,3.33,rtol=5e-3))
    check("14.8 mezcla binaria resoluble",status=="unique" and sol is not None and sol[0]>0 and sol[1]>0)

    # C.5: glucosa + palmítico, O2=34, CO2=24 mmol
    # glucosa: O2=6, CO2=6; palmítico: O2=23, CO2=16
    status,sol=solve_linear_system([[6,23],[6,16]],[34,24])
    check("14.C.5 sistema único",status=="unique")
    if sol:
        check("14.C.5 cantidades positivas",sol[0]>=0 and sol[1]>=0)

    # C.10: x=4, y=8, a=5 -> z=2
    z=2*(4+8/4-5)
    check("14.C.10 CH8O2",approx(z,2.0))

    # Ejercicio 14.C.4 tal como está redactado: el sistema para CH4/C2H6
    # exige una cantidad negativa de CH4. La aplicación debe detectar que el
    # conjunto de datos no representa una mezcla físicamente posible.
    o2in_c4 = 85.4*(DEFAULT_AIR_O2/DEFAULT_AIR_N2)
    o2cons_c4 = o2in_c4 - 2.80
    st_c4, sol_c4 = solve_linear_system([[1,2],[2,3.5]],[11.8,o2cons_c4])
    check("14.C.4 detecta mezcla no física", st_c4=="unique" and sol_c4 is not None and any(v < 0 for v in sol_c4))

    # Ejercicio 14.C.7: para glucosa completamente oxidada, O2 consumido y CO2
    # producido tienen el mismo coeficiente (6 mol/mol). 18 y 15 no pueden
    # proceder de una única cantidad completamente oxidada bajo las hipótesis dadas.
    st_c7, _ = solve_linear_system([[6],[6]],[18,15])
    check("14.C.7 detecta datos incompatibles", st_c7=="inconsistent")

    # 14.C.6: CH4 + CO + N2 en el combustible, relación CO/CH4=0.5.
    # Incógnitas [CH4, CO, N2_fuel, O2_in].
    rair = DEFAULT_AIR_N2/DEFAULT_AIR_O2
    A_c6 = [
        [1,1,0,0],          # CO2 seco
        [-2,-0.5,0,1],      # O2 salida
        [0,0,1,rair],       # N2 salida
        [-0.5,1,0,0],       # CO/CH4 = 0.5
    ]
    b_c6 = [9.50,4.00,86.5,0.0]
    st_c6, sol_c6 = solve_linear_system(A_c6,b_c6)
    check("14.C.6 sistema inverso resoluble",st_c6=="unique" and sol_c6 is not None and all(v>=0 for v in sol_c6))

    # 14.C.9: CH4/C3H8, 20 % de exceso, 11 % CO2 seco.
    lam=1.20; fac=(lam-1)+rair*lam
    st_c9, sol_c9 = solve_linear_system([[1,3],[fac*2,fac*5]],[11,89])
    check("14.C.9 mezcla inversa resoluble",st_c9=="unique" and sol_c9 is not None and all(v>=0 for v in sol_c9))

    # 14.B.5: 65 mol O2 estequiométrico corresponden a 10 mol de butano.
    o2_butane,_ = oxygen_stoich_formula("C4H10",1.0,ProductModel())
    check("14.B.5 cantidad de butano",approx(65.0/o2_butane,10.0))

    # Entrada española y cifras significativas.
    check("Entrada con coma decimal",approx(parse_measurement("0,00450").value,0.00450) and parse_measurement("0,00450").sigfigs==3)
    check("Cero de composición no limita cifras",min_sf(parse_measurement("12,0"),parse_measurement("0"))==3)

    # Parser
    check("Parser Ca(OH)2",parse_formula("Ca(OH)2")=={"Ca":1.0,"O":2.0,"H":2.0})

    ok=all(v for _,v in tests)
    if verbose:
        print("AUTOPRUEBAS DEL PROGRAMA")
        for name,result in tests: print(f"  [{'OK' if result else 'FALLO'}] {name}")
        print(f"\nResultado global: {'CORRECTO' if ok else 'HAY FALLOS'} ({sum(v for _,v in tests)}/{len(tests)})")
    return ok


# -----------------------------------------------------------------------------
# MENÚ PRINCIPAL
# -----------------------------------------------------------------------------

def main_menu() -> None:
    while True:
        print_header("TEMA 14 - COMBUSTIÓN Y ANÁLISIS DE GASES")
        print("1. Oxígeno estequiométrico y aire/comburente teórico")
        print("2. Combustión completa con aire u otro comburente")
        print("3. Combustión de una mezcla de combustibles")
        print("4. Combustible de composición elemental conocida")
        print("5. Combustión incompleta")
        print("6. Análisis de gases de combustión / Orsat")
        print("7. Cálculo inverso a partir de un análisis gaseoso")
        print("8. Comprobación de un problema de combustión")
        print("9. Salir")
        choice=input("Seleccione una opción: ").strip()
        if choice=="9":
            print("Fin del programa.")
            return
        funcs={"1":option1_stoich_air,"2":option2_complete,"3":option3_mixture,"4":option4_elemental,"5":option5_incomplete,"6":option6_analysis,"7":option7_inverse,"8":option8_check}
        if choice not in funcs:
            print("Opción no válida.")
            continue
        try:
            funcs[choice]()
        except (CombustionError,ValueError,ZeroDivisionError) as exc:
            print("\n*** PROBLEMA NO RESUELTO ***")
            print(f"{exc}")
            print("El programa no generará una solución arbitraria con estos datos.")
        except KeyboardInterrupt:
            print("\nOperación cancelada por el usuario.")
        input("\nPulse Intro para volver al menú principal...")


def build_arg_parser() -> argparse.ArgumentParser:
    p=argparse.ArgumentParser(
        description="Aplicación didáctica del tema 14: combustión, aire y análisis de gases.",
        epilog=(
            "La ejecución normal es interactiva. Se aceptan coma y punto decimal. "
            "Los cálculos se realizan sin redondeos intermedios y los resultados se presentan "
            "con cifras significativas coherentes con los datos introducidos."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--self-test",action="store_true",help="ejecuta una batería interna de comprobaciones numéricas y termina")
    p.add_argument("--version",action="version",version="tema14_combustion 1.0")
    return p


def main(argv: Optional[List[str]]=None) -> int:
    args=build_arg_parser().parse_args(argv)
    if args.self_test:
        return 0 if run_self_tests(True) else 1
    main_menu()
    return 0


if __name__=="__main__":
    sys.exit(main())
