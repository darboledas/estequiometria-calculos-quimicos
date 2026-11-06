#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
masa_molar.py
=============

Calcula la masa molar a partir de una fórmula química, por ejemplo:

    Al2(SO4)3
    Ca(OH)2
    K4[Fe(CN)6]
    CuSO4·5H2O
    Al₂(SO₄)₃

FUENTES DE LOS DATOS
--------------------
1) CIAAW — Commission on Isotopic Abundances and Atomic Weights:
   "Standard Atomic Weights 2024".
   https://ciaaw.org/atomic-weights.htm

2) Para elementos sin peso atómico estándar, se usa únicamente como valor
   representativo el número másico entre corchetes que figura en la tabla
   IUPAC de pesos atómicos:
   https://iupac.org/what-we-do/periodic-table-of-elements/
   https://iupac.qmul.ac.uk/AtWt/

IMPORTANTE: los números entre corchetes NO son pesos atómicos estándar.
Si una fórmula contiene alguno de esos elementos, el programa lo advierte.

CRITERIO DE REDONDEO
--------------------
- Los subíndices estequiométricos son números exactos.
- El cálculo interno se realiza con Decimal, sin redondeos intermedios.
- Para los pesos atómicos estándar se conservan también los márgenes ± de la
  tabla abreviada CIAAW. Se calcula un margen total conservador sumando
  linealmente n_i·u_i; no se interpreta como una incertidumbre estándar
  estadística. La masa se redondea a la misma posición decimal que ese margen.
- El margen se expresa con una cifra significativa, o con dos cuando comienza
  por 1 o 2.
- Para elementos representados únicamente por un número másico entero, el
  resultado se redondea a unidades y se emite una advertencia.

FUNCIONALIDAD
-------------
- Paréntesis, corchetes y llaves anidados.
- Hidratos/aductos con punto medio o punto: CuSO4·5H2O o CuSO4.5H2O.
- Coeficientes enteros delante de un término.
- Subíndices Unicode.
- Comprobación de símbolos químicos.
- Salida con coma decimal.
- Modo interactivo y línea de comandos.
- --help, --detalles, --fuentes y --elementos.

No admite notación isotópica explícita ni notación de carga iónica ambigua.

Ejemplos:
    python masa_molar.py
    python masa_molar.py "Al2(SO4)3"
    python masa_molar.py "CuSO4·5H2O" --detalles
    python masa_molar.py --fuentes
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict


@dataclass(frozen=True)
class AtomicData:
    value: Decimal
    display: str
    uncertainty: Decimal | None
    kind: str = "standard"

    @property
    def decimal_places(self) -> int:
        if self.kind == "mass_number":
            return 0
        if "." not in self.display:
            return 0
        return len(self.display.split(".")[1])


def A(value: str, uncertainty: str) -> AtomicData:
    return AtomicData(Decimal(value), value, Decimal(uncertainty), "standard")


def R(mass_number: int) -> AtomicData:
    return AtomicData(Decimal(mass_number), str(mass_number), None, "mass_number")


# CIAAW, Standard Atomic Weights 2024 (tabla completa y tabla abreviada).
# Los elementos sin peso atómico estándar usan R(A), donde A es el número
# másico del isótopo de vida media más larga indicado por IUPAC.
ATOMIC_WEIGHTS: Dict[str, AtomicData] = {
    "H": A("1.0080", "0.0002"), "He": A("4.0026", "0.0001"),
    "Li": A("6.94", "0.06"), "Be": A("9.0122", "0.0001"),
    "B": A("10.81", "0.02"), "C": A("12.011", "0.002"),
    "N": A("14.007", "0.001"), "O": A("15.999", "0.001"),
    "F": A("18.998", "0.001"), "Ne": A("20.180", "0.001"),
    "Na": A("22.990", "0.001"), "Mg": A("24.305", "0.002"),
    "Al": A("26.982", "0.001"), "Si": A("28.085", "0.001"),
    "P": A("30.974", "0.001"), "S": A("32.06", "0.02"),
    "Cl": A("35.45", "0.01"), "Ar": A("39.95", "0.16"),
    "K": A("39.098", "0.001"), "Ca": A("40.078", "0.004"),
    "Sc": A("44.956", "0.001"), "Ti": A("47.867", "0.001"),
    "V": A("50.942", "0.001"), "Cr": A("51.996", "0.001"),
    "Mn": A("54.938", "0.001"), "Fe": A("55.845", "0.002"),
    "Co": A("58.933", "0.001"), "Ni": A("58.693", "0.001"),
    "Cu": A("63.546", "0.003"), "Zn": A("65.38", "0.02"),
    "Ga": A("69.723", "0.001"), "Ge": A("72.630", "0.008"),
    "As": A("74.922", "0.001"), "Se": A("78.971", "0.008"),
    "Br": A("79.904", "0.003"), "Kr": A("83.798", "0.002"),
    "Rb": A("85.468", "0.001"), "Sr": A("87.62", "0.01"),
    "Y": A("88.906", "0.001"), "Zr": A("91.222", "0.003"),
    "Nb": A("92.906", "0.001"), "Mo": A("95.95", "0.01"),
    "Tc": R(97), "Ru": A("101.07", "0.02"),
    "Rh": A("102.91", "0.01"), "Pd": A("106.42", "0.01"),
    "Ag": A("107.87", "0.01"), "Cd": A("112.41", "0.01"),
    "In": A("114.82", "0.01"), "Sn": A("118.71", "0.01"),
    "Sb": A("121.76", "0.01"), "Te": A("127.60", "0.03"),
    "I": A("126.90", "0.01"), "Xe": A("131.29", "0.01"),
    "Cs": A("132.91", "0.01"), "Ba": A("137.33", "0.01"),
    "La": A("138.91", "0.01"), "Ce": A("140.12", "0.01"),
    "Pr": A("140.91", "0.01"), "Nd": A("144.24", "0.01"),
    "Pm": R(145), "Sm": A("150.36", "0.02"),
    "Eu": A("151.96", "0.01"), "Gd": A("157.25", "0.01"),
    "Tb": A("158.93", "0.01"), "Dy": A("162.50", "0.01"),
    "Ho": A("164.93", "0.01"), "Er": A("167.26", "0.01"),
    "Tm": A("168.93", "0.01"), "Yb": A("173.05", "0.02"),
    "Lu": A("174.97", "0.01"), "Hf": A("178.49", "0.01"),
    "Ta": A("180.95", "0.01"), "W": A("183.84", "0.01"),
    "Re": A("186.21", "0.01"), "Os": A("190.23", "0.03"),
    "Ir": A("192.22", "0.01"), "Pt": A("195.08", "0.02"),
    "Au": A("196.97", "0.01"), "Hg": A("200.59", "0.01"),
    "Tl": A("204.38", "0.01"), "Pb": A("207.2", "1.1"),
    "Bi": A("208.98", "0.01"), "Po": R(209), "At": R(210),
    "Rn": R(222), "Fr": R(223), "Ra": R(226), "Ac": R(227),
    "Th": A("232.04", "0.01"), "Pa": A("231.04", "0.01"),
    "U": A("238.03", "0.01"), "Np": R(237), "Pu": R(244),
    "Am": R(243), "Cm": R(247), "Bk": R(247), "Cf": R(251),
    "Es": R(252), "Fm": R(257), "Md": R(258), "No": R(259),
    "Lr": R(262), "Rf": R(267), "Db": R(270), "Sg": R(269),
    "Bh": R(270), "Hs": R(270), "Mt": R(278), "Ds": R(281),
    "Rg": R(281), "Cn": R(285), "Nh": R(286), "Fl": R(289),
    "Mc": R(289), "Lv": R(293), "Ts": R(293), "Og": R(294),
}


# Valores completos de la tabla CIAAW «Standard Atomic Weights 2024».
# X("valor", "incertidumbre") usa la notación publicada A_r ± u.
# Para los elementos con intervalo se conserva el valor representativo abreviado
# de CIAAW, y se registra por separado el intervalo de variabilidad natural.
FULL_2024 = {
    "He": ("4.002602", "0.000002"), "Be": ("9.0121831", "0.0000005"),
    "F": ("18.998403162", "0.000000005"), "Ne": ("20.1797", "0.0006"),
    "Na": ("22.98976928", "0.00000002"), "Al": ("26.9815384", "0.0000003"),
    "P": ("30.973761998", "0.000000005"), "K": ("39.0983", "0.0001"),
    "Ca": ("40.078", "0.004"), "Sc": ("44.955907", "0.000004"),
    "Ti": ("47.867", "0.001"), "V": ("50.9415", "0.0001"),
    "Cr": ("51.9961", "0.0006"), "Mn": ("54.938043", "0.000002"),
    "Fe": ("55.845", "0.002"), "Co": ("58.933194", "0.000003"),
    "Ni": ("58.6934", "0.0004"), "Cu": ("63.546", "0.003"),
    "Zn": ("65.38", "0.02"), "Ga": ("69.723", "0.001"),
    "Ge": ("72.630", "0.008"), "As": ("74.921595", "0.000006"),
    "Se": ("78.971", "0.008"), "Kr": ("83.798", "0.002"),
    "Rb": ("85.4678", "0.0003"), "Sr": ("87.62", "0.01"),
    "Y": ("88.905838", "0.000002"), "Zr": ("91.222", "0.003"),
    "Nb": ("92.90637", "0.00001"), "Mo": ("95.95", "0.01"),
    "Ru": ("101.07", "0.02"), "Rh": ("102.90549", "0.00002"),
    "Pd": ("106.42", "0.01"), "Ag": ("107.8682", "0.0002"),
    "Cd": ("112.414", "0.004"), "In": ("114.818", "0.001"),
    "Sn": ("118.710", "0.007"), "Sb": ("121.760", "0.001"),
    "Te": ("127.60", "0.03"), "I": ("126.90447", "0.00003"),
    "Xe": ("131.293", "0.006"), "Cs": ("132.90545196", "0.00000006"),
    "Ba": ("137.327", "0.007"), "La": ("138.90547", "0.00007"),
    "Ce": ("140.116", "0.001"), "Pr": ("140.90766", "0.00001"),
    "Nd": ("144.242", "0.003"), "Sm": ("150.36", "0.02"),
    "Eu": ("151.964", "0.001"), "Gd": ("157.249", "0.002"),
    "Tb": ("158.925354", "0.000007"), "Dy": ("162.500", "0.001"),
    "Ho": ("164.930329", "0.000005"), "Er": ("167.259", "0.003"),
    "Tm": ("168.934219", "0.000005"), "Yb": ("173.045", "0.010"),
    "Lu": ("174.96669", "0.00005"), "Hf": ("178.486", "0.006"),
    "Ta": ("180.94788", "0.00002"), "W": ("183.84", "0.01"),
    "Re": ("186.207", "0.001"), "Os": ("190.23", "0.03"),
    "Ir": ("192.217", "0.002"), "Pt": ("195.084", "0.009"),
    "Au": ("196.966570", "0.000004"), "Hg": ("200.592", "0.003"),
    "Bi": ("208.98040", "0.00001"), "Th": ("232.0377", "0.0004"),
    "Pa": ("231.03588", "0.00001"), "U": ("238.02891", "0.00003"),
}
for _symbol, (_mass, _uncertainty) in FULL_2024.items():
    ATOMIC_WEIGHTS[_symbol] = A(_mass, _uncertainty)

# Estos son intervalos de pesos atómicos estándar, NO cantidades exactas.
STANDARD_INTERVALS_2024 = {
    "H": ("1.00784", "1.00811"), "Li": ("6.938", "6.997"),
    "B": ("10.806", "10.821"), "C": ("12.0096", "12.0116"),
    "N": ("14.00643", "14.00728"), "O": ("15.99903", "15.99977"),
    "Mg": ("24.304", "24.307"), "Si": ("28.084", "28.086"),
    "S": ("32.059", "32.076"), "Cl": ("35.446", "35.457"),
    "Ar": ("39.792", "39.963"), "Br": ("79.901", "79.907"),
    "Tl": ("204.382", "204.385"), "Pb": ("206.14", "207.94"),
}
for _symbol, (_lo, _hi) in STANDARD_INTERVALS_2024.items():
    _central = ATOMIC_WEIGHTS[_symbol].value
    _bound = max(abs(_central - Decimal(_lo)), abs(Decimal(_hi) - _central))
    ATOMIC_WEIGHTS[_symbol] = A(str(_central), str(_bound))
assert len(ATOMIC_WEIGHTS) == 118

SUBSCRIPTS = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")
OPEN_TO_CLOSE = {"(": ")", "[": "]", "{": "}"}
CLOSERS = set(OPEN_TO_CLOSE.values())


def normalize_formula(formula: str) -> str:
    formula = formula.translate(SUBSCRIPTS)
    formula = formula.replace(" ", "")
    formula = formula.replace("•", "·").replace("∙", "·")
    if not formula:
        raise ValueError("La fórmula está vacía.")
    if "^" in formula or formula.endswith("+") or formula.endswith("-"):
        raise ValueError(
            "La notación de carga iónica no se admite. Introduzca la fórmula sin carga."
        )
    return formula


class FormulaParser:
    def __init__(self, text: str):
        self.text = text
        self.i = 0

    def parse(self) -> Counter:
        result = self._parse_sequence(stop=None)
        if self.i != len(self.text):
            raise ValueError(
                f"Carácter inesperado en la posición {self.i + 1}: {self.text[self.i]!r}"
            )
        return result

    def _parse_sequence(self, stop: str | None) -> Counter:
        total = Counter()
        while self.i < len(self.text):
            ch = self.text[self.i]

            if stop is not None and ch == stop:
                self.i += 1
                return total

            if ch in CLOSERS:
                if stop is None:
                    raise ValueError(
                        f"Cierre {ch!r} sin apertura en la posición {self.i + 1}."
                    )
                raise ValueError(
                    f"Se esperaba {stop!r}, pero aparece {ch!r} "
                    f"en la posición {self.i + 1}."
                )

            if ch in OPEN_TO_CLOSE:
                close = OPEN_TO_CLOSE[ch]
                self.i += 1
                group = self._parse_sequence(stop=close)
                multiplier = self._parse_number()
                for symbol, count in group.items():
                    total[symbol] += count * multiplier
                continue

            if ch.isupper():
                symbol = ch
                self.i += 1
                if self.i < len(self.text) and self.text[self.i].islower():
                    symbol += self.text[self.i]
                    self.i += 1
                if symbol not in ATOMIC_WEIGHTS:
                    raise ValueError(f"Símbolo químico desconocido: {symbol!r}.")
                count = self._parse_number()
                total[symbol] += count
                continue

            if ch.isdigit():
                raise ValueError(
                    f"Número inesperado en la posición {self.i + 1}. "
                    "Los coeficientes solo se permiten al comienzo de cada término."
                )

            raise ValueError(
                f"Carácter no válido {ch!r} en la posición {self.i + 1}."
            )

        if stop is not None:
            raise ValueError(f"Falta el cierre {stop!r}.")
        return total

    def _parse_number(self) -> int:
        start = self.i
        while self.i < len(self.text) and self.text[self.i].isdigit():
            self.i += 1
        if start == self.i:
            return 1
        number = int(self.text[start:self.i])
        if number <= 0:
            raise ValueError("Los subíndices deben ser enteros positivos.")
        return number


def parse_term(term: str) -> Counter:
    if not term:
        raise ValueError("Hay un término vacío en la fórmula.")
    match = re.match(r"^(\d+)(?=[A-Z(\[{])", term)
    coefficient = 1
    if match:
        coefficient = int(match.group(1))
        if coefficient <= 0:
            raise ValueError("Los coeficientes deben ser positivos.")
        term = term[match.end():]
    counts = FormulaParser(term).parse()
    if not counts:
        raise ValueError("No se han encontrado elementos en un término.")
    if coefficient != 1:
        for symbol in list(counts):
            counts[symbol] *= coefficient
    return counts


def parse_formula(formula: str) -> Counter:
    formula = normalize_formula(formula)
    parts = re.split(r"[·.]", formula)
    if any(not part for part in parts):
        raise ValueError("Uso incorrecto del punto de hidratación/adición.")
    total = Counter()
    for part in parts:
        total.update(parse_term(part))
    return total


@dataclass
class MolarMassResult:
    formula: str
    counts: Counter
    raw_mass: Decimal
    rounded_mass: Decimal
    decimal_places: int
    contains_mass_number: bool
    conservative_uncertainty: Decimal | None
    rounded_uncertainty: Decimal | None


def quantize_places(value: Decimal, places: int) -> Decimal:
    quantum = Decimal("1").scaleb(-places)
    return value.quantize(quantum, rounding=ROUND_HALF_UP)



def uncertainty_rounding(uncertainty: Decimal) -> tuple[Decimal, int]:
    """Redondea un margen positivo y devuelve (margen, decimales).

    Se usan dos cifras significativas si la primera cifra es 1 o 2; en otro
    caso, una. Es una regla de presentación metrológica habitual.
    """
    if uncertainty <= 0:
        return Decimal("0"), 6
    exponent = uncertainty.adjusted()
    first_digit = int(uncertainty.scaleb(-exponent).to_integral_value(rounding="ROUND_FLOOR"))
    sig = 2 if first_digit in (1, 2) else 1
    places = max(0, sig - 1 - exponent)
    return quantize_places(uncertainty, places), places

def calculate_molar_mass(formula: str) -> MolarMassResult:
    counts = parse_formula(formula)
    raw_mass = Decimal("0")
    contains_mass_number = False
    conservative_uncertainty = Decimal("0")

    for symbol, count in counts.items():
        data = ATOMIC_WEIGHTS[symbol]
        raw_mass += data.value * count
        if data.kind == "mass_number":
            contains_mass_number = True
        elif data.uncertainty is not None:
            conservative_uncertainty += data.uncertainty * count

    if contains_mass_number:
        decimal_places = 0
        rounded_uncertainty = None
    else:
        rounded_uncertainty, decimal_places = uncertainty_rounding(
            conservative_uncertainty
        )

    rounded = quantize_places(raw_mass, decimal_places)
    return MolarMassResult(
        normalize_formula(formula), counts, raw_mass, rounded,
        decimal_places, contains_mass_number,
        None if contains_mass_number else conservative_uncertainty,
        rounded_uncertainty
    )


def decimal_comma(value: Decimal, places: int | None = None) -> str:
    if places is None:
        text = format(value, "f")
    else:
        text = f"{value:.{places}f}"
    return text.replace(".", ",")


def print_result(result: MolarMassResult, details: bool = False) -> None:
    print(f"Fórmula: {result.formula}")
    if result.rounded_uncertainty is not None:
        print(
            "Masa molar: "
            f"{decimal_comma(result.rounded_mass, result.decimal_places)} g·mol⁻¹"
        )
    else:
        print(
            "Masa formula aproximada: "
            f"{decimal_comma(result.rounded_mass, result.decimal_places)} g·mol⁻¹"
        )

    if details:
        print("\nComposición:")
        order = {symbol: i for i, symbol in enumerate(ATOMIC_WEIGHTS)}
        for symbol in sorted(result.counts, key=lambda s: order[s]):
            count = result.counts[symbol]
            data = ATOMIC_WEIGHTS[symbol]
            contribution = data.value * count
            source_value = (
                f"[{data.display}]" if data.kind == "mass_number" else data.display
            )
            print(
                f"  {symbol:>2}: {count:>4} × {source_value:<8} "
                f"= {decimal_comma(contribution)}"
            )
        print(
            "\nSuma sin redondeo: "
            f"{decimal_comma(result.raw_mass)} g·mol⁻¹"
        )
        if result.rounded_uncertainty is not None:
            print(
                "Margen conservador acumulado (CIAAW 2024): ±"
                f"{decimal_comma(result.rounded_uncertainty, result.decimal_places)} "
                "g·mol⁻¹"
            )
            print(
                "Redondeo final: masa y margen expresados hasta la misma "
                "posición decimal."
            )
        else:
            print(
                "Redondeo final: a unidades, porque interviene al menos un "
                "elemento sin peso atómico estándar."
            )

    interval_symbols = [x for x in result.counts if x in STANDARD_INTERVALS_2024]
    if interval_symbols:
        print("NOTA: " + ", ".join(interval_symbols) +
              " presenta(n) un intervalo natural de peso atómico estándar. "
              "Se usa el valor representativo CIAAW; sin composición isotópica "
              "no existe una masa molar exacta única.")
    if result.contains_mass_number:
        symbols = [
            s for s in result.counts if ATOMIC_WEIGHTS[s].kind == "mass_number"
        ]
        print(
            "\nADVERTENCIA: " + ", ".join(symbols)
            + " no dispone(n) de peso atómico estándar. Se ha usado el número "
              "másico IUPAC del isótopo de vida media más larga. El resultado "
              "no debe interpretarse como una masa molar estándar de composición "
              "isotópica natural."
        )


def print_sources() -> None:
    print("FUENTES")
    print("=======")
    print(
        "CIAAW — Standard Atomic Weights 2024:\n"
        "https://ciaaw.org/atomic-weights.htm"
    )
    print(
        "\nIUPAC — Periodic Table of the Elements:\n"
        "https://iupac.org/what-we-do/periodic-table-of-elements/"
    )
    print(
        "\nIUPAC/CIAAW atomic-weight table:\n"
        "https://iupac.qmul.ac.uk/AtWt/"
    )


def print_elements() -> None:
    print("Símbolo  Valor usado")
    print("-------  ----------")
    for symbol, data in ATOMIC_WEIGHTS.items():
        if data.kind == "standard":
            if symbol in STANDARD_INTERVALS_2024:
                lo, hi = STANDARD_INTERVALS_2024[symbol]
                print(f"{symbol:<7}  {data.display}  [intervalo {lo}–{hi}]")
            else:
                print(f"{symbol:<7}  {data.display} ± {data.uncertainty}")
        else:
            print(
                f"{symbol:<7}  [{data.display}]  "
                "(número másico; no peso atómico estándar)"
            )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Calcula la masa molar de una fórmula química usando los pesos "
            "atómicos estándar abreviados CIAAW 2024."
        )
    )
    parser.add_argument(
        "formula", nargs="?", help='Fórmula química, por ejemplo "Al2(SO4)3".'
    )
    parser.add_argument(
        "--detalles", action="store_true",
        help="Muestra el recuento de átomos y las contribuciones elementales."
    )
    parser.add_argument(
        "--fuentes", action="store_true", help="Muestra las fuentes de los datos."
    )
    parser.add_argument(
        "--elementos", action="store_true",
        help="Muestra el diccionario de valores atómicos usado."
    )
    return parser


def interactive() -> None:
    print("CÁLCULO DE MASA MOLAR")
    print("=====================")
    print("Ejemplo: Al2(SO4)3")
    print("También se admiten paréntesis, corchetes e hidratos.\n")
    while True:
        formula = input("Fórmula química [Enter para salir]: ").strip()
        if not formula:
            return
        try:
            result = calculate_molar_mass(formula)
            print()
            print_result(result, details=True)
        except ValueError as exc:
            print(f"\nERROR: {exc}")
        print()


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.fuentes:
        print_sources()
        return
    if args.elementos:
        print_elements()
        return

    try:
        if args.formula is None:
            interactive()
        else:
            result = calculate_molar_mass(args.formula)
            print_result(result, details=args.detalles)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(2)
    except KeyboardInterrupt:
        print("\nOperación cancelada.", file=sys.stderr)
        sys.exit(130)


if __name__ == "__main__":
    main()
