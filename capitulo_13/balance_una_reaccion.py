#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script 13.1. Balance reactivo con una reacción

FUNCIONALIDAD
-------------
Herramienta interactiva para resolver y comprobar balances molares con una
única reacción química en:
- sistemas discontinuos cerrados;
- sistemas continuos en estado estacionario.

Puede determinar la extensión de reacción (xi) o la velocidad de extensión
(xi_dot) a partir de:
- una extensión conocida;
- una conversión conocida de un reactivo;
- una cantidad o caudal final conocido de una especie.

También permite:
- calcular cantidades o caudales finales;
- calcular cantidades consumidas o formadas;
- obtener la composición molar final;
- comprobar la consistencia de resultados calculados manualmente;
- comprobar opcionalmente balances elementales y cierre másico;
- aplicar, de forma opcional, una separación posterior sencilla basada en la
  recuperación de una especie.

TIPOS DE PROBLEMAS
------------------
- Una reacción en un sistema discontinuo.
- Una reacción en un sistema continuo estacionario.
- Alimentación conocida directamente o con un reactivo alimentado en exceso.
- Resolución mediante extensión, conversión o un dato final.
- Verificación de un conjunto completo de cantidades o caudales finales.
- Reactor seguido de una separación simple con recuperación de una especie.

HIPÓTESIS Y LIMITACIONES
------------------------
- La reacción debe estar correctamente ajustada.
- Los números estequiométricos son negativos para reactivos y positivos para
  productos; una especie inerte tiene número estequiométrico cero.
- En sistemas continuos se trabaja con los caudales molares totales que
  atraviesan la frontera considerada. Si hay varias corrientes de entrada o de
  salida, deben sumarse previamente por especie.
- La separación opcional supone que la corriente de producto recuperado
  contiene únicamente la especie seleccionada; el resto de las especies y la
  fracción no recuperada permanecen en la corriente residual.
- No se calculan equilibrios, cinética, termodinámica ni mecanismos.
- Los coeficientes estequiométricos y los números de átomos se consideran
  exactos.
- Las cifras significativas se propagan con las reglas usuales: en sumas y
  restas limita la posición decimal menos precisa; en productos y cocientes
  limita el menor número de cifras significativas. Los ceros que representan
  ausencia exacta de una especie no limitan la precisión.
- Para expresar ceros finales significativos en enteros, use notación
  científica (por ejemplo, 1,00e3).

FORMA DE USO
------------
Ejecución interactiva:
    python balance_una_reaccion.py

Ayuda:
    python balance_una_reaccion.py -h
"""

import argparse
import math
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, getcontext

getcontext().prec = 40

ZERO_TOL = Decimal("1e-20")

SUBSCRIPT_MAP = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


def display_species(name):
    """Devuelve el nombre de la especie con dígitos en subíndice para mostrarlo."""
    return str(name).translate(SUBSCRIPT_MAP)




@dataclass
class Q:
    """Número con metadatos de precisión para propagar cifras significativas."""
    value: Decimal
    sf: int | None = None
    place: int | None = None   # potencia de 10 de la última cifra significativa
    exact: bool = False

    @staticmethod
    def exact_value(value):
        return Q(Decimal(str(value)), exact=True)

    @staticmethod
    def measured(value, sf, place):
        return Q(Decimal(value), int(sf), int(place), False)

    def half_resolution(self):
        if self.exact or self.place is None:
            return Decimal(0)
        return Decimal("0.5") * (Decimal(10) ** self.place)


def _normalize_number_text(raw):
    s = raw.strip().replace(" ", "").replace(",", ".")
    if not s:
        raise ValueError
    return s


def _sigfig_metadata(raw, value):
    s = _normalize_number_text(raw).lower()
    mant = s.split("e", 1)[0]
    has_exp = "e" in s
    mant = mant.lstrip("+-")
    has_decimal = "." in mant
    digits = mant.replace(".", "")
    digits_no_leading = digits.lstrip("0")
    if value == 0:
        # Para un cero medido, la posición decimal se deduce de lo escrito.
        if has_exp:
            exp10 = int(s.split("e", 1)[1])
        else:
            exp10 = 0
        if has_decimal:
            decimals = len(mant.split(".", 1)[1])
            place = exp10 - decimals
            sf = max(1, decimals)
        else:
            place = exp10
            sf = 1
        return sf, place

    if not digits_no_leading:
        sf = 1
    elif has_exp:
        sf = len(digits_no_leading)
    elif has_decimal:
        sf = len(digits_no_leading)
    else:
        # En enteros sin coma decimal, los ceros finales no se consideran
        # significativos; use notación científica para declararlos.
        sf = max(1, len(digits_no_leading.rstrip("0")))

    adjusted = value.copy_abs().adjusted()
    place = adjusted - sf + 1
    return sf, place


def parse_q_text(raw, *, exact_zero=False):
    s = _normalize_number_text(raw)
    try:
        value = Decimal(s)
    except InvalidOperation:
        raise ValueError
    if not value.is_finite():
        raise ValueError
    if exact_zero and value == 0:
        return Q.exact_value(0)
    sf, place = _sigfig_metadata(raw, value)
    return Q.measured(value, sf, place)


def q_from_place(value, place):
    value = Decimal(value)
    if value == 0:
        return Q(value, sf=1, place=place, exact=False)
    sf = max(1, value.copy_abs().adjusted() - place + 1)
    return Q(value, sf=sf, place=place, exact=False)


def q_from_sf(value, sf):
    value = Decimal(value)
    if value == 0:
        return Q(value, sf=max(1, sf), place=0, exact=False)
    place = value.copy_abs().adjusted() - sf + 1
    return Q(value, sf=sf, place=place, exact=False)


def q_add(a, b):
    value = a.value + b.value
    if a.exact and b.exact:
        return Q.exact_value(value)
    if a.exact:
        return Q(value, b.sf, b.place, False)
    if b.exact:
        return Q(value, a.sf, a.place, False)
    return q_from_place(value, max(a.place, b.place))


def q_sub(a, b):
    return q_add(a, Q(-b.value, b.sf, b.place, b.exact))


def q_mul(a, b):
    value = a.value * b.value
    if (a.exact and a.value == 0) or (b.exact and b.value == 0):
        return Q.exact_value(0)
    if a.exact and b.exact:
        return Q.exact_value(value)
    if a.exact:
        return q_from_sf(value, b.sf)
    if b.exact:
        return q_from_sf(value, a.sf)
    return q_from_sf(value, min(a.sf, b.sf))


def q_div(a, b):
    if b.value == 0:
        raise ZeroDivisionError
    if a.exact and a.value == 0:
        return Q.exact_value(0)
    value = a.value / b.value
    if a.exact and b.exact:
        return Q.exact_value(value)
    if b.exact and not a.exact:
        return q_from_sf(value, a.sf)
    if a.exact and not b.exact:
        return q_from_sf(value, b.sf)
    return q_from_sf(value, min(a.sf, b.sf))


def q_abs(a):
    return Q(abs(a.value), a.sf, a.place, a.exact)


def q_sum(values):
    total = Q.exact_value(0)
    for v in values:
        total = q_add(total, v)
    return total


def format_q(q):
    """Formatea con la precisión almacenada y coma decimal."""
    if q.exact:
        if q.value == 0:
            return "0"
        txt = format(q.value.normalize(), "f")
        return txt.replace(".", ",")

    place = q.place if q.place is not None else 0
    quantum = Decimal(1).scaleb(place)
    rounded = q.value.quantize(quantum, rounding=ROUND_HALF_UP)

    if rounded == 0:
        if place < 0:
            return ("0." + "0" * (-place)).replace(".", ",")
        return "0"

    sf = max(1, q.sf or 1)
    exponent = rounded.copy_abs().adjusted()

    # Evita ambigüedad de ceros finales significativos en enteros grandes.
    use_scientific = (place > 0) or (exponent <= -4)
    if use_scientific:
        mant = rounded.scaleb(-exponent)
        decimals = max(0, sf - 1)
        txt = f"{mant:.{decimals}f}".replace(".", ",")
        sign = "+" if exponent >= 0 else ""
        return f"{txt}e{sign}{exponent}"

    decimals = max(0, -place)
    return f"{rounded:.{decimals}f}".replace(".", ",")


def ask_int(prompt, minimum=1):
    while True:
        raw = input(prompt).strip()
        try:
            n = int(raw)
        except ValueError:
            print("  Error: introduzca un número entero.")
            continue
        if n < minimum:
            print(f"  Error: el valor debe ser >= {minimum}.")
            continue
        return n


def ask_choice(prompt, options):
    valid = {str(i) for i in range(1, len(options) + 1)}
    while True:
        print()
        for i, text in enumerate(options, 1):
            print(f"{i}. {text}")
        c = input(prompt).strip()
        if c in valid:
            return int(c)
        print("  Error: selección no válida.")


def ask_q(prompt, *, minimum=None, maximum=None, exact_zero=False):
    while True:
        raw = input(prompt).strip()
        try:
            q = parse_q_text(raw, exact_zero=exact_zero)
        except ValueError:
            print("  Error: introduzca un número válido.")
            continue
        if minimum is not None and q.value < Decimal(str(minimum)):
            print(f"  Error: el valor debe ser >= {minimum}.")
            continue
        if maximum is not None and q.value > Decimal(str(maximum)):
            print(f"  Error: el valor debe ser <= {maximum}.")
            continue
        return q


def ask_percent(prompt):
    """Pide un porcentaje entre 0 y 100 y devuelve la fracción correspondiente."""
    q_pct = ask_q(prompt, minimum=0, maximum=100)
    return q_div(q_pct, Q.exact_value(100))


def parse_exact_coefficient(raw):
    s = raw.strip().replace(",", ".")
    if "/" in s:
        p = s.split("/")
        if len(p) != 2:
            raise ValueError
        num = Decimal(p[0].strip())
        den = Decimal(p[1].strip())
        if den == 0:
            raise ValueError
        return num / den
    return Decimal(s)


def parse_reaction_equation(text):
    arrow = None
    for candidate in ("->", "→", "="):
        if candidate in text:
            arrow = candidate
            break
    if arrow is None:
        raise ValueError("No se encontró una flecha de reacción (->, → o =).")
    left, right = text.split(arrow, 1)
    if not left.strip() or not right.strip():
        raise ValueError("La ecuación debe contener reactivos y productos.")

    def parse_side(side, sign):
        terms = re.split(r"\s+\+\s+", side.strip())
        result = []
        for term in terms:
            term = term.strip()
            if not term:
                raise ValueError("Hay un término vacío en la ecuación.")
            m = re.match(r"^\s*((?:\d+(?:[.,]\d*)?|\d*[.,]\d+)(?:[eE][+-]?\d+)?|\d+\s*/\s*\d+)?\s*(.+?)\s*$", term)
            if not m:
                raise ValueError(f"No se pudo interpretar el término: {term}")
            coeff_txt, name = m.groups()
            coeff = Decimal(1) if not coeff_txt else parse_exact_coefficient(coeff_txt)
            if coeff <= 0 or not name.strip():
                raise ValueError(f"Término no válido: {term}")
            result.append((name.strip(), sign * coeff))
        return result

    combined = {}
    order = []
    for name, nu in parse_side(left, Decimal(-1)) + parse_side(right, Decimal(1)):
        if name not in combined:
            combined[name] = Decimal(0)
            order.append(name)
        combined[name] += nu

    species = [{"name": name, "nu": combined[name]} for name in order]
    if all(s["nu"] == 0 for s in species):
        raise ValueError("La ecuación no produce ningún cambio estequiométrico neto.")
    return species


def ask_reaction():
    method = ask_choice(
        "Seleccione cómo introducir la reacción: ",
        [
            "Escribir la ecuación química ajustada",
            "Introducir especies y números estequiométricos",
        ],
    )
    if method == 1:
        print("\nFormato recomendado: 2 H2 + O2 -> 2 H2O")
        print("Puede usar coeficientes fraccionarios, por ejemplo 1/2 O2.")
        print("Para especies iónicas, separe los términos con espacios alrededor de '+'.")
        while True:
            text = input("Ecuación ajustada: ").strip()
            try:
                species = parse_reaction_equation(text)
                break
            except Exception as e:
                print(f"  Error: {e}")
        used = {s["name"] for s in species}
        ninert = ask_int(
            "Número de especies adicionales inertes/acompañantes: ", 0
        )
        for k in range(ninert):
            while True:
                name = input(f"Nombre de la especie inerte {k+1}: ").strip()
                if name and name not in used:
                    used.add(name)
                    species.append({"name": name, "nu": Decimal(0)})
                    break
                print("  Error: nombre vacío o repetido.")
        return species
    else:
        n = ask_int("Número total de especies (incluidos inertes si los hay): ", 1)
        species = []
        used = set()
        for i in range(n):
            while True:
                name = input(f"Nombre de la especie {i+1}: ").strip()
                if not name or name in used:
                    print("  Error: nombre vacío o repetido.")
                    continue
                used.add(name)
                break
            while True:
                raw = input(
                    f"Número estequiométrico de {display_species(name)} "
                    "(reactivo < 0, producto > 0, inerte = 0): "
                )
                try:
                    nu = parse_exact_coefficient(raw)
                    break
                except Exception:
                    print("  Error: introduzca un coeficiente válido.")
            species.append({"name": name, "nu": nu})
        if all(s["nu"] == 0 for s in species):
            raise ValueError("Todos los números estequiométricos son cero.")
        return species


def ask_units(continuous):
    amount_options = ["mol", "mmol", "kmol", "unidad personalizada"]
    c = ask_choice("Unidad de cantidad de sustancia: ", amount_options)
    if c <= 3:
        amount_unit = amount_options[c - 1]
    else:
        while True:
            amount_unit = input("Escriba la unidad de cantidad: ").strip()
            if amount_unit:
                break
    if not continuous:
        return amount_unit, amount_unit

    time_options = ["s", "min", "h", "unidad personalizada"]
    c = ask_choice("Unidad de tiempo: ", time_options)
    if c <= 3:
        time_unit = time_options[c - 1]
    else:
        while True:
            time_unit = input("Escriba la unidad de tiempo: ").strip()
            if time_unit:
                break
    return amount_unit, f"{amount_unit} {time_unit}^-1"


def reaction_participants(species, sign):
    if sign == "reactant":
        return [s for s in species if s["nu"] < 0]
    return [s for s in species if s["nu"] > 0]


def ask_species_selection(species, prompt, predicate=None):
    candidates = [
        (i, s) for i, s in enumerate(species)
        if predicate is None or predicate(s)
    ]
    if not candidates:
        raise ValueError("No existen especies compatibles con esta selección.")
    print()
    for k, (idx, s) in enumerate(candidates, 1):
        print(f"{k}. {display_species(s['name'])}")
    while True:
        raw = input(prompt).strip()
        if raw.isdigit() and 1 <= int(raw) <= len(candidates):
            return candidates[int(raw) - 1][0]
        print("  Error: selección no válida.")


def ask_initial(species, continuous, unit):
    label = "Caudal molar total de entrada" if continuous else "Cantidad inicial"
    method = ask_choice(
        "Forma de introducir la alimentación/inventario inicial: ",
        [
            "Introducir directamente todas las cantidades o caudales",
            "Calcular un reactivo alimentado en exceso respecto a otro reactivo",
        ],
    )
    initial = [None] * len(species)

    if method == 1:
        for i, s in enumerate(species):
            initial[i] = ask_q(
                f"{label} de {display_species(s['name'])} [{unit}]: ",
                minimum=0,
                exact_zero=True,
            )
        return initial

    reactants = [i for i, s in enumerate(species) if s["nu"] < 0]
    if len(reactants) < 2:
        print("  No hay al menos dos reactivos. Se usarán datos directos.")
        for i, s in enumerate(species):
            initial[i] = ask_q(
                f"{label} de {display_species(s['name'])} [{unit}]: ",
                minimum=0,
                exact_zero=True,
            )
        return initial

    idx_excess = ask_species_selection(
        species,
        "Seleccione el reactivo que se alimenta en exceso: ",
        lambda s: s["nu"] < 0,
    )
    idx_ref = ask_species_selection(
        species,
        "Seleccione el reactivo de referencia: ",
        lambda s: s["nu"] < 0 and s["name"] != species[idx_excess]["name"],
    )
    excess = ask_percent("Exceso del reactivo seleccionado [%]: ")

    for i, s in enumerate(species):
        if i == idx_excess:
            continue
        initial[i] = ask_q(
            f"{label} de {display_species(s['name'])} [{unit}]: ",
            minimum=0,
            exact_zero=True,
        )

    nref = initial[idx_ref]
    if nref.value <= 0:
        raise ValueError("El reactivo de referencia debe estar presente en cantidad positiva.")

    ratio = Q.exact_value(
        abs(species[idx_excess]["nu"] / species[idx_ref]["nu"])
    )
    stoich = q_mul(nref, ratio)
    factor = q_add(Q.exact_value(1), excess)
    initial[idx_excess] = q_mul(stoich, factor)

    print(
        f"\n{label} calculado de {species[idx_excess]['name']}: "
        f"{format_q(initial[idx_excess])} {unit}"
    )
    return initial


def xi_interval(species, initial):
    """Intervalo de xi que mantiene no negativas todas las especies."""
    lower = None
    upper = None
    for i, s in enumerate(species):
        nu = s["nu"]
        if nu > 0:
            bound = q_div(
                Q(-initial[i].value, initial[i].sf, initial[i].place, initial[i].exact),
                Q.exact_value(nu),
            )
            if lower is None or bound.value > lower.value:
                lower = bound
        elif nu < 0:
            bound = q_div(initial[i], Q.exact_value(-nu))
            if upper is None or bound.value < upper.value:
                upper = bound
    return lower, upper


def calculate_final(species, initial, xi):
    delta = []
    final = []
    for i, s in enumerate(species):
        d = q_mul(Q.exact_value(s["nu"]), xi)
        f = q_add(initial[i], d)
        delta.append(d)
        final.append(f)
    return delta, final


def check_nonnegative(values, names):
    bad = [(names[i], q.value) for i, q in enumerate(values) if q.value < -ZERO_TOL]
    if bad:
        txt = "; ".join(f"{n} = {v}" for n, v in bad)
        raise ValueError("Se obtienen cantidades o caudales negativos: " + txt)


def compatible(a, b):
    """Compatibilidad según la resolución implícita en los datos."""
    diff = abs(a.value - b.value)
    tol = a.half_resolution() + b.half_resolution()
    if a.exact and b.exact:
        return diff <= ZERO_TOL
    return diff <= max(tol, ZERO_TOL)


def ask_elemental_data(species):
    c = ask_choice(
        "Comprobación elemental: ",
        ["No introducir composición elemental", "Introducir composición elemental"],
    )
    if c == 1:
        return None

    elements = {}
    for s in species:
        name = s["name"]
        ne = ask_int(
            f"Número de elementos distintos presentes en {name}: ", 1
        )
        comp = {}
        for j in range(ne):
            while True:
                el = input(f"  Símbolo del elemento {j+1}: ").strip()
                if el and el not in comp:
                    break
                print("  Error: símbolo vacío o repetido.")
            while True:
                raw = input(f"  Número de átomos de {el} en {name}: ").strip()
                try:
                    a = parse_exact_coefficient(raw)
                    if a <= 0:
                        raise ValueError
                    comp[el] = a
                    break
                except Exception:
                    print("  Error: el número de átomos debe ser positivo.")
        elements[name] = comp
    return elements


def check_reaction_elements(species, elemental):
    if elemental is None:
        return None
    all_elements = sorted({e for d in elemental.values() for e in d})
    residuals = {}
    for e in all_elements:
        res = Decimal(0)
        for s in species:
            res += s["nu"] * elemental[s["name"]].get(e, Decimal(0))
        residuals[e] = res
    bad = {e: v for e, v in residuals.items() if abs(v) > ZERO_TOL}
    if bad:
        msg = ", ".join(f"{e}: {v}" for e, v in bad.items())
        raise ValueError(
            "La reacción introducida no satisface el balance elemental: " + msg
        )
    return all_elements


def elemental_totals(species, values, elemental):
    totals = {}
    if elemental is None:
        return totals
    for e in sorted({x for d in elemental.values() for x in d}):
        terms = []
        for i, s in enumerate(species):
            a = Q.exact_value(elemental[s["name"]].get(e, Decimal(0)))
            terms.append(q_mul(a, values[i]))
        totals[e] = q_sum(terms)
    return totals


def ask_molar_masses(species):
    c = ask_choice(
        "Comprobación de cierre másico: ",
        ["No introducir masas molares", "Introducir masas molares"],
    )
    if c == 1:
        return None
    masses = []
    for s in species:
        q = ask_q(f"Masa molar de {display_species(s['name'])} [g mol^-1]: ", minimum=0)
        if q.value <= 0:
            raise ValueError("Todas las masas molares deben ser positivas.")
        masses.append(q)
    return masses


def total_mass(values, molar_masses):
    return q_sum([q_mul(values[i], molar_masses[i]) for i in range(len(values))])


def display_stream(species, values, unit, title):
    print(f"\n{title}:")
    for i, s in enumerate(species):
        print(f"  {display_species(s['name'])}: {format_q(values[i])} {unit}")
    total = q_sum(values)
    print(f"  TOTAL: {format_q(total)} {unit}")
    if total.value > 0:
        print("  Composición molar:")
        for i, s in enumerate(species):
            y = q_div(values[i], total)
            print(f"    {display_species(s['name'])}: {format_q(y)}")


def optional_separation(species, final, unit):
    c = ask_choice(
        "¿Desea aplicar una separación posterior sencilla por recuperación? ",
        ["No", "Sí"],
    )
    if c == 1:
        return

    idx = ask_species_selection(
        species,
        "Seleccione la especie que se recupera en la corriente de producto P: ",
    )
    recovery = ask_percent("Recuperación de esa especie [%]: ")
    recovered = q_mul(final[idx], recovery)

    P = [Q.exact_value(0) for _ in species]
    L = [q for q in final]
    P[idx] = recovered
    L[idx] = q_sub(final[idx], recovered)

    print("\nSEPARACIÓN POSTERIOR")
    print(
        "Hipótesis aplicada: P contiene únicamente la especie recuperada; "
        "el resto permanece en L."
    )
    display_stream(species, P, unit, "Corriente P")
    display_stream(species, L, unit, "Corriente L")


def solve_mode(species, initial, continuous, unit):
    xi_name = "xi_dot" if continuous else "xi"
    mode = ask_choice(
        "Dato utilizado para determinar la extensión: ",
        [
            f"{xi_name} conocida",
            "Conversión conocida de un reactivo",
            "Cantidad o caudal final conocido de una especie",
        ],
    )

    if mode == 1:
        xi = ask_q(f"Valor de {xi_name} [{unit}]: ")
    elif mode == 2:
        idx = ask_species_selection(
            species,
            "Seleccione el reactivo cuya conversión se conoce: ",
            lambda s: s["nu"] < 0,
        )
        X = ask_percent("Conversión del reactivo [%]: ")
        if initial[idx].value == 0 and X.value > 0:
            raise ValueError("No puede convertirse un reactivo ausente.")
        consumed = q_mul(initial[idx], X)
        xi = q_div(consumed, Q.exact_value(-species[idx]["nu"]))
    else:
        idx = ask_species_selection(
            species,
            "Seleccione la especie con dato final conocido: ",
            lambda s: s["nu"] != 0,
        )
        nf = ask_q(
            f"Cantidad o caudal final de {display_species(species[idx]['name'])} [{unit}]: ",
            minimum=0,
            exact_zero=True,
        )
        change = q_sub(nf, initial[idx])
        xi = q_div(change, Q.exact_value(species[idx]["nu"]))
        if abs(xi.value) <= ZERO_TOL:
            xi = Q.exact_value(0)

    xmin, xmax = xi_interval(species, initial)
    if xmin is not None and xi.value < xmin.value - max(
        xi.half_resolution(), xmin.half_resolution(), ZERO_TOL
    ):
        raise ValueError(
            "La extensión exige consumir, en el sentido inverso, más producto "
            "del disponible. "
            f"Mínimo compatible: {format_q(xmin)} {unit}"
        )
    if xmax is not None and xi.value > xmax.value + max(
        xi.half_resolution(), xmax.half_resolution(), ZERO_TOL
    ):
        raise ValueError(
            "La extensión exige consumir más reactivo del disponible. "
            f"Máximo compatible: {format_q(xmax)} {unit}"
        )

    delta, final = calculate_final(species, initial, xi)
    check_nonnegative(final, [s["name"] for s in species])
    return xi, delta, final


def verification_mode(species, initial, continuous, unit):
    """Comprueba datos finales introducidos por el usuario."""
    print("\nIntroduzca las cantidades o caudales finales que desea comprobar.")
    observed = []
    for s in species:
        observed.append(
            ask_q(
                f"Final/salida de {s['name']} [{unit}]: ",
                minimum=0,
                exact_zero=True,
            )
        )

    xi_estimates = []
    print("\nExtensiones obtenidas de cada especie participante:")
    for i, s in enumerate(species):
        if s["nu"] == 0:
            if not compatible(observed[i], initial[i]):
                raise ValueError(
                    f"La especie inerte {display_species(s['name'])} no conserva su cantidad/caudal."
                )
            continue
        xi_i = q_div(
            q_sub(observed[i], initial[i]),
            Q.exact_value(s["nu"]),
        )
        xi_estimates.append((i, xi_i))
        print(f"  {s['name']}: {format_q(xi_i)} {unit}")

    if not xi_estimates:
        raise ValueError("No hay especies participantes para determinar la extensión.")

    ref_idx, xi_ref = xi_estimates[0]
    for idx, xi_i in xi_estimates[1:]:
        if not compatible(xi_i, xi_ref):
            raise ValueError(
                "Las especies no conducen a una extensión compatible. "
                f"Revise {display_species(species[ref_idx]['name'])} y {display_species(species[idx]['name'])}."
            )

    # Se usa la estimación más precisa (menor resolución) como referencia.
    xi = min(
        (q for _, q in xi_estimates),
        key=lambda q: q.half_resolution() if not q.exact else Decimal(0),
    )
    delta, predicted = calculate_final(species, initial, xi)
    for i, s in enumerate(species):
        if not compatible(predicted[i], observed[i]):
            raise ValueError(
                f"El valor final de {s['name']} no es compatible con la extensión común."
            )

    check_nonnegative(observed, [s["name"] for s in species])
    return xi, delta, observed


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Resuelve o comprueba balances de materia con una única reacción "
            "en sistemas discontinuos o continuos estacionarios."
        ),
        epilog=(
            "Las entradas se realizan interactivamente. Use coma o punto decimal. "
            "Los coeficientes estequiométricos se consideran exactos."
        ),
    )
    parser.parse_args()

    print("=" * 78)
    print("SCRIPT 13.1 - BALANCE REACTIVO CON UNA REACCIÓN")
    print("=" * 78)

    task = ask_choice(
        "Tipo de uso: ",
        ["Resolver un balance", "Comprobar resultados obtenidos manualmente o experimentalmente"],
    )
    system = ask_choice(
        "Tipo de sistema: ",
        ["Sistema discontinuo cerrado", "Sistema continuo en estado estacionario"],
    )
    continuous = system == 2
    amount_unit, working_unit = ask_units(continuous)

    try:
        species = ask_reaction()
        initial = ask_initial(species, continuous, working_unit)

        elemental = ask_elemental_data(species)
        elements = check_reaction_elements(species, elemental)

        if task == 1:
            xi, delta, final = solve_mode(
                species, initial, continuous, working_unit
            )
        else:
            xi, delta, final = verification_mode(
                species, initial, continuous, working_unit
            )

        molar_masses = ask_molar_masses(species)

        print("\n" + "=" * 78)
        print("RESULTADOS")
        print("=" * 78)
        xi_name = "xi_dot" if continuous else "xi"
        print(f"\n{xi_name} = {format_q(xi)} {working_unit}")
        if xi.value < 0:
            print(
                "  Aviso: la extensión es negativa; el avance neto es opuesto "
                "al sentido en que se escribió la reacción."
            )

        print("\nCambio debido a la reacción:")
        for i, s in enumerate(species):
            d = delta[i]
            if d.value < 0:
                print(
                    f"  {s['name']}: consumido = {format_q(q_abs(d))} {working_unit}"
                )
            elif d.value > 0:
                print(
                    f"  {s['name']}: formado = {format_q(d)} {working_unit}"
                )
            else:
                print(f"  {s['name']}: sin cambio")

        display_stream(
            species,
            final,
            working_unit,
            "Cantidades finales" if not continuous else "Caudales molares totales de salida",
        )

        print("\nCOMPROBACIONES")
        print("  Cantidades o caudales negativos: no.")
        print("  Compatibilidad estequiométrica: correcta.")

        if elemental is not None:
            t0 = elemental_totals(species, initial, elemental)
            tf = elemental_totals(species, final, elemental)
            print("  Balances elementales:")
            for e in elements:
                ok = compatible(t0[e], tf[e])
                print(
                    f"    {e}: entrada/inicial = {format_q(t0[e])}; "
                    f"salida/final = {format_q(tf[e])}; "
                    f"{'correcto' if ok else 'NO CIERRA'}"
                )
                if not ok:
                    raise ValueError(f"El balance elemental de {e} no cierra.")
        else:
            print("  Balances elementales: no comprobados.")

        if molar_masses is not None:
            m0 = total_mass(initial, molar_masses)
            mf = total_mass(final, molar_masses)
            ok = compatible(m0, mf)
            print(
                f"  Cierre másico: inicial/entrada = {format_q(m0)}; "
                f"final/salida = {format_q(mf)}; "
                f"{'correcto' if ok else 'NO CIERRA'}"
            )
            if not ok:
                raise ValueError(
                    "Las masas molares y los datos introducidos no producen cierre másico."
                )
        else:
            print("  Cierre másico: no comprobado.")

        optional_separation(species, final, working_unit)
        return 0

    except (ValueError, ZeroDivisionError) as e:
        print(f"\nERROR: {e}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
