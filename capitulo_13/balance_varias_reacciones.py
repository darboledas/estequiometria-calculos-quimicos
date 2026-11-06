#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script 13.2. Balance reactivo con varias reacciones

FUNCIONALIDAD
-------------
Herramienta interactiva para resolver y comprobar balances molares con varias
reacciones químicas independientes en:
- sistemas discontinuos cerrados;
- sistemas continuos en estado estacionario.

El programa asocia una extensión independiente a cada reacción y permite
determinar las extensiones a partir de relaciones químicamente interpretables:
- cantidades o caudales finales conocidos;
- conversiones de especies que solo se consumen;
- composiciones molares finales;
- cantidad o caudal molar total final;
- extensiones conocidas;
- selectividad entre cantidades netas formadas de dos productos;
- rendimiento de un producto respecto a un reactivo de referencia, con base
  en reactivo alimentado o consumido.

También:
- detecta reacciones estequiométricamente dependientes;
- detecta un número insuficiente de relaciones independientes;
- detecta especificaciones incompatibles con la precisión introducida;
- calcula la contribución de cada reacción a cada especie;
- calcula cantidades o caudales finales y composición molar;
- comprueba opcionalmente balances elementales y cierre másico;
- permite comprobar resultados manuales o experimentales;
- puede aplicar una separación posterior sencilla basada en recuperación.

TIPOS DE PROBLEMAS
------------------
- Varias reacciones simultáneas o sucesivas representadas globalmente.
- Una especie participante en varias reacciones.
- Determinación de varias extensiones mediante datos de especies,
  conversiones, composición, rendimiento o selectividad.
- Verificación de un conjunto completo de datos finales.
- Zona reactiva seguida de una separación sencilla por recuperación.

HIPÓTESIS Y LIMITACIONES
------------------------
- Las reacciones deben estar correctamente ajustadas y ser
  estequiométricamente independientes.
- Los números estequiométricos son negativos para reactivos y positivos para
  productos. Una especie inerte tiene número estequiométrico cero en todas
  las reacciones.
- En sistemas continuos se usan caudales molares totales por especie a través
  de la frontera. Si existen varias corrientes, deben agregarse por especie.
- La conversión multirreacción solo se acepta para una especie que no se forme
  en ninguna de las reacciones introducidas.
- La selectividad implementada se define explícitamente como:
      S = cantidad neta formada de P1 / cantidad neta formada de P2
  y se restringe a especies que no se consumen en ninguna reacción.
- El rendimiento obliga a elegir su base: reactivo alimentado o consumido.
  El programa no supone silenciosamente una definición.
- La separación opcional supone que la corriente P contiene únicamente la
  especie recuperada; el resto permanece en la corriente residual L.
- No se calculan equilibrios, cinética, termodinámica ni mecanismos.
- Los coeficientes estequiométricos y números de átomos se consideran exactos.
- Las cifras significativas se propagan con las reglas usuales para las
  operaciones directas. En la resolución simultánea, cada extensión se
  presenta con el mínimo de cifras significativas de las restricciones que
  intervienen en su solución (aproximación basada en sensibilidad lineal).
  El resultado no sustituye el análisis completo de incertidumbre en
  sistemas mal condicionados.
- Para declarar ceros finales significativos en enteros, use notación
  científica, por ejemplo 1,00e3.

FORMA DE USO
------------
Ejecución:
    python balance_varias_reacciones.py

Ayuda:
    python balance_varias_reacciones.py -h

No requiere bibliotecas externas.
"""

import argparse
import itertools
import math
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, getcontext

getcontext().prec = 50
ZERO_TOL = Decimal("1e-20")
RANK_TOL = Decimal("1e-24")

SUBSCRIPT_MAP = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


def display_species(name):
    """Devuelve el nombre de la especie con dígitos en subíndice para mostrarlo."""
    return str(name).translate(SUBSCRIPT_MAP)




@dataclass
class Q:
    value: Decimal
    sf: int | None = None
    place: int | None = None
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
        exp10 = int(s.split("e", 1)[1]) if has_exp else 0
        if has_decimal:
            decimals = len(mant.split(".", 1)[1])
            return max(1, decimals), exp10 - decimals
        return 1, exp10

    if not digits_no_leading:
        sf = 1
    elif has_exp or has_decimal:
        sf = len(digits_no_leading)
    else:
        sf = max(1, len(digits_no_leading.rstrip("0")))
    place = value.copy_abs().adjusted() - sf + 1
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
    if a.exact:
        return q_from_sf(value, b.sf)
    if b.exact:
        return q_from_sf(value, a.sf)
    return q_from_sf(value, min(a.sf, b.sf))


def q_abs(a):
    return Q(abs(a.value), a.sf, a.place, a.exact)


def q_sum(values):
    total = Q.exact_value(0)
    for v in values:
        total = q_add(total, v)
    return total


def format_q(q):
    if q.exact:
        if q.value == 0:
            return "0"
        return format(q.value.normalize(), "f").replace(".", ",")

    place = q.place if q.place is not None else 0
    quantum = Decimal(1).scaleb(place)
    rounded = q.value.quantize(quantum, rounding=ROUND_HALF_UP)

    if rounded == 0:
        if place < 0:
            return ("0." + "0" * (-place)).replace(".", ",")
        return "0"

    sf = max(1, q.sf or 1)
    exponent = rounded.copy_abs().adjusted()
    if place > 0 or exponent <= -4:
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
    return q_div(
        ask_q(prompt, minimum=0, maximum=100),
        Q.exact_value(100),
    )


def parse_exact_coefficient(raw):
    s = raw.strip().replace(",", ".")
    if "/" in s:
        parts = s.split("/")
        if len(parts) != 2:
            raise ValueError
        a = Decimal(parts[0].strip())
        b = Decimal(parts[1].strip())
        if b == 0:
            raise ValueError
        return a / b
    return Decimal(s)


def parse_reaction_equation(text):
    arrow = next((a for a in ("->", "→", "=") if a in text), None)
    if arrow is None:
        raise ValueError("No se encontró flecha de reacción.")
    left, right = text.split(arrow, 1)
    if not left.strip() or not right.strip():
        raise ValueError("Faltan reactivos o productos.")

    def parse_side(side, sign):
        terms = re.split(r"\s+\+\s+", side.strip())
        out = []
        for term in terms:
            m = re.match(
                r"^\s*((?:\d+(?:[.,]\d*)?|\d*[.,]\d+)(?:[eE][+-]?\d+)?|\d+\s*/\s*\d+)?\s*(.+?)\s*$",
                term,
            )
            if not m:
                raise ValueError(f"No se pudo interpretar: {term}")
            coeff_txt, name = m.groups()
            coeff = Decimal(1) if not coeff_txt else parse_exact_coefficient(coeff_txt)
            if coeff <= 0 or not name.strip():
                raise ValueError(f"Término no válido: {term}")
            out.append((name.strip(), sign * coeff))
        return out

    combined = {}
    order = []
    for name, nu in parse_side(left, Decimal(-1)) + parse_side(right, Decimal(1)):
        if name not in combined:
            combined[name] = Decimal(0)
            order.append(name)
        combined[name] += nu
    return order, combined


def matrix_rank(A):
    if not A:
        return 0
    M = [[Decimal(x) for x in row] for row in A]
    m, n = len(M), len(M[0])
    rank = 0
    col = 0
    while rank < m and col < n:
        pivot = max(range(rank, m), key=lambda i: abs(M[i][col]))
        if abs(M[pivot][col]) <= RANK_TOL:
            col += 1
            continue
        M[rank], M[pivot] = M[pivot], M[rank]
        piv = M[rank][col]
        for j in range(col, n):
            M[rank][j] /= piv
        for i in range(m):
            if i == rank:
                continue
            factor = M[i][col]
            if abs(factor) <= RANK_TOL:
                continue
            for j in range(col, n):
                M[i][j] -= factor * M[rank][j]
        rank += 1
        col += 1
    return rank


def solve_square(A, b):
    n = len(A)
    M = [
        [Decimal(A[i][j]) for j in range(n)] + [Decimal(b[i])]
        for i in range(n)
    ]
    for col in range(n):
        pivot = max(range(col, n), key=lambda i: abs(M[i][col]))
        if abs(M[pivot][col]) <= RANK_TOL:
            raise ValueError("Sistema singular.")
        M[col], M[pivot] = M[pivot], M[col]
        piv = M[col][col]
        for j in range(col, n + 1):
            M[col][j] /= piv
        for i in range(n):
            if i == col:
                continue
            f = M[i][col]
            if abs(f) <= RANK_TOL:
                continue
            for j in range(col, n + 1):
                M[i][j] -= f * M[col][j]
    return [M[i][n] for i in range(n)]


def row_numerical_tol(row, b):
    scale = max([Decimal(1), abs(b)] + [abs(x) for x in row])
    return Decimal("1e-18") * scale


def constraint_satisfied(constraint, xi):
    row = constraint["A"]
    residual = sum(row[j] * xi[j] for j in range(len(xi))) - constraint["b"]
    tol = constraint["b_unc"]
    tol += sum(abs(xi[j]) * constraint["A_unc"][j] for j in range(len(xi)))
    tol += row_numerical_tol(row, constraint["b"])
    return abs(residual) <= tol, residual, tol


def solve_constraints(constraints, nr):
    A_all = [c["A"] for c in constraints]
    rank = matrix_rank(A_all)
    if rank < nr:
        raise ValueError(
            f"Solo se han aportado {rank} relaciones independientes para {nr} "
            "extensiones. Faltan datos independientes."
        )

    indices = range(len(constraints))
    attempts = 0
    best_failure = None

    for combo in itertools.combinations(indices, nr):
        attempts += 1
        if attempts > 1000:
            break
        A = [constraints[i]["A"] for i in combo]
        if matrix_rank(A) < nr:
            continue
        b = [constraints[i]["b"] for i in combo]
        try:
            xi = solve_square(A, b)
        except ValueError:
            continue

        failures = []
        for c in constraints:
            ok, res, tol = constraint_satisfied(c, xi)
            if not ok:
                failures.append((c["label"], res, tol))
        if not failures:
            # La precisión de cada extensión depende de las restricciones
            # que contribuyen a ella, no de todas las restricciones del sistema.
            # Invertimos la matriz de coeficientes con el mismo solucionador;
            # (A^-1)[r,j] determina la sensibilidad de xi_r al dato j.
            columnas_inversa = [
                solve_square(A, [Decimal(int(j == k)) for j in range(nr)])
                for k in range(nr)
            ]
            cifras_por_extension = []
            for r in range(nr):
                relevantes = []
                for j, idx_restriccion in enumerate(combo):
                    if abs(columnas_inversa[j][r]) > RANK_TOL:
                        relevantes.extend(constraints[idx_restriccion]["sfs"])
                cifras_por_extension.append(min(relevantes) if relevantes else 6)
            return xi, cifras_por_extension, combo
        if best_failure is None or len(failures) < len(best_failure):
            best_failure = failures

    if best_failure:
        label, res, tol = best_failure[0]
        raise ValueError(
            "Las especificaciones no son simultáneamente compatibles con la "
            f"precisión introducida. Primera discrepancia: {label} "
            f"(residuo {res}, tolerancia {tol})."
        )
    raise ValueError("No se pudo construir un sistema independiente resoluble.")


def ask_units(continuous):
    amount_options = ["mol", "mmol", "kmol", "unidad personalizada"]
    c = ask_choice("Unidad de cantidad de sustancia: ", amount_options)
    if c <= 3:
        amount = amount_options[c - 1]
    else:
        while True:
            amount = input("Escriba la unidad de cantidad: ").strip()
            if amount:
                break
    if not continuous:
        return amount
    time_options = ["s", "min", "h", "unidad personalizada"]
    c = ask_choice("Unidad de tiempo: ", time_options)
    if c <= 3:
        time = time_options[c - 1]
    else:
        while True:
            time = input("Escriba la unidad de tiempo: ").strip()
            if time:
                break
    return f"{amount} {time}^-1"


def ask_reactions():
    nr = ask_int("Número de reacciones independientes que desea introducir: ", 1)
    method = ask_choice(
        "Forma de introducir la estequiometría: ",
        [
            "Escribir las ecuaciones químicas ajustadas",
            "Introducir una matriz de números estequiométricos",
        ],
    )

    if method == 1:
        eqs = []
        names = []
        seen = set()
        maps = []
        print("\nFormato recomendado: 2 H2 + O2 -> 2 H2O")
        for r in range(nr):
            while True:
                text = input(f"Reacción {r+1}: ").strip()
                try:
                    order, mp = parse_reaction_equation(text)
                    break
                except Exception as e:
                    print(f"  Error: {e}")
            maps.append(mp)
            for name in order:
                if name not in seen:
                    seen.add(name)
                    names.append(name)

        ninert = ask_int(
            "Número de especies adicionales inertes/acompañantes: ", 0
        )
        for k in range(ninert):
            while True:
                name = input(f"Nombre de la especie inerte {k+1}: ").strip()
                if name and name not in seen:
                    seen.add(name)
                    names.append(name)
                    break
                print("  Error: nombre vacío o repetido.")

        nu = [
            [maps[r].get(name, Decimal(0)) for r in range(nr)]
            for name in names
        ]
    else:
        ns = ask_int("Número total de especies: ", 1)
        names = []
        used = set()
        for i in range(ns):
            while True:
                name = input(f"Nombre de la especie {i+1}: ").strip()
                if name and name not in used:
                    used.add(name)
                    names.append(name)
                    break
                print("  Error: nombre vacío o repetido.")
        nu = [[Decimal(0) for _ in range(nr)] for _ in range(ns)]
        for r in range(nr):
            print(f"\nReacción {r+1}")
            for i, name in enumerate(names):
                while True:
                    raw = input(
                        f"  nu({display_species(name)}, R{r+1}) "
                        "(reactivo < 0, producto > 0, ausente = 0): "
                    )
                    try:
                        nu[i][r] = parse_exact_coefficient(raw)
                        break
                    except Exception:
                        print("  Error: coeficiente no válido.")

    if any(all(nu[i][r] == 0 for i in range(len(names))) for r in range(nr)):
        raise ValueError("Alguna reacción tiene todos sus coeficientes iguales a cero.")

    # El rango por columnas de nu debe ser nr.
    rows = [[nu[i][r] for r in range(nr)] for i in range(len(names))]
    rank = matrix_rank(rows)
    if rank < nr:
        raise ValueError(
            f"Las {nr} reacciones no son estequiométricamente independientes "
            f"(rango = {rank})."
        )
    return names, nu, nr


def ask_initial(names, continuous, unit):
    label = "Caudal molar total de entrada" if continuous else "Cantidad inicial"
    vals = []
    for name in names:
        vals.append(
            ask_q(
                f"{label} de {display_species(name)} [{unit}]: ",
                minimum=0,
                exact_zero=True,
            )
        )
    return vals


def select_index(names, prompt, allowed=None):
    idxs = [i for i in range(len(names)) if allowed is None or allowed(i)]
    if not idxs:
        raise ValueError("No hay especies compatibles con esta selección.")
    print()
    for k, i in enumerate(idxs, 1):
        print(f"{k}. {display_species(names[i])}")
    while True:
        raw = input(prompt).strip()
        if raw.isdigit() and 1 <= int(raw) <= len(idxs):
            return idxs[int(raw) - 1]
        print("  Error: selección no válida.")


def select_reaction(nr, prompt="Seleccione la reacción: "):
    print()
    for r in range(nr):
        print(f"{r+1}. Reacción {r+1}")
    while True:
        raw = input(prompt).strip()
        if raw.isdigit() and 1 <= int(raw) <= nr:
            return int(raw) - 1
        print("  Error: selección no válida.")


def add_constraint(constraints, A, b_q, label, *, A_unc=None, extra_sfs=None):
    if A_unc is None:
        A_unc = [Decimal(0)] * len(A)
    sfs = []
    if not b_q.exact and b_q.sf:
        sfs.append(b_q.sf)
    if extra_sfs:
        sfs.extend(extra_sfs)
    constraints.append(
        {
            "A": [Decimal(x) for x in A],
            "A_unc": [Decimal(x) for x in A_unc],
            "b": b_q.value,
            "b_unc": b_q.half_resolution(),
            "label": label,
            "sfs": sfs,
        }
    )


def collect_constraints(names, nu, nr, initial, unit):
    constraints = []
    N0 = q_sum(initial)
    sum_nu = [
        sum(nu[i][r] for i in range(len(names)))
        for r in range(nr)
    ]

    while True:
        rank_now = matrix_rank([c["A"] for c in constraints]) if constraints else 0
        print(
            f"\nRelaciones introducidas: {len(constraints)}; "
            f"rango independiente actual: {rank_now}/{nr}."
        )
        choice = ask_choice(
            "Seleccione una relación adicional o termine: ",
            [
                "Cantidad o caudal final conocido de una especie",
                "Conversión conocida de una especie que solo se consume",
                "Fracción molar final conocida de una especie",
                "Cantidad o caudal molar total final conocido",
                "Extensión de una reacción conocida",
                "Selectividad S = formación neta de P1 / formación neta de P2",
                "Rendimiento de un producto respecto a un reactivo de referencia",
                "Terminar y resolver",
            ],
        )

        if choice == 8:
            break

        if choice == 1:
            i = select_index(names, "Seleccione la especie: ")
            nf = ask_q(
                f"Cantidad/caudal final de {names[i]} [{unit}]: ",
                minimum=0,
                exact_zero=True,
            )
            bq = q_sub(nf, initial[i])
            add_constraint(
                constraints,
                nu[i],
                bq,
                f"dato final de {names[i]}",
            )

        elif choice == 2:
            def allowed_conv(i):
                row = nu[i]
                return any(x < 0 for x in row) and all(x <= 0 for x in row)

            i = select_index(
                names,
                "Seleccione la especie cuya conversión se conoce: ",
                allowed_conv,
            )
            if initial[i].value <= 0:
                raise ValueError("La especie seleccionada no está presente en la alimentación.")
            X = ask_percent("Conversión [%]: ")
            consumed = q_mul(initial[i], X)
            bq = Q(-consumed.value, consumed.sf, consumed.place, consumed.exact)
            add_constraint(
                constraints,
                nu[i],
                bq,
                f"conversión de {names[i]}",
                extra_sfs=[] if X.exact else [X.sf],
            )

        elif choice == 3:
            i = select_index(names, "Seleccione la especie: ")
            y = ask_q("Fracción molar final (0 a 1): ", minimum=0, maximum=1)
            A = [
                nu[i][r] - y.value * sum_nu[r]
                for r in range(nr)
            ]
            A_unc = [
                y.half_resolution() * abs(sum_nu[r])
                for r in range(nr)
            ]
            bq = q_sub(q_mul(y, N0), initial[i])
            add_constraint(
                constraints,
                A,
                bq,
                f"fracción molar final de {names[i]}",
                A_unc=A_unc,
                extra_sfs=[y.sf] if y.sf else [],
            )

        elif choice == 4:
            nf_total = ask_q(
                f"Cantidad/caudal molar total final [{unit}]: ",
                minimum=0,
            )
            bq = q_sub(nf_total, N0)
            add_constraint(
                constraints,
                sum_nu,
                bq,
                "cantidad/caudal molar total final",
            )

        elif choice == 5:
            r = select_reaction(nr)
            xi = ask_q(f"Extensión de la reacción {r+1} [{unit}]: ")
            A = [Decimal(0)] * nr
            A[r] = Decimal(1)
            add_constraint(
                constraints,
                A,
                xi,
                f"extensión conocida de R{r+1}",
            )

        elif choice == 6:
            def product_only(i):
                return any(x > 0 for x in nu[i]) and all(x >= 0 for x in nu[i])

            p1 = select_index(
                names,
                "Seleccione P1 (numerador de la selectividad): ",
                product_only,
            )
            p2 = select_index(
                names,
                "Seleccione P2 (denominador de la selectividad): ",
                lambda i: product_only(i) and i != p1,
            )
            S = ask_q(
                f"Selectividad S = formado({names[p1]}) / formado({names[p2]}): ",
                minimum=0,
            )
            A = [
                nu[p1][r] - S.value * nu[p2][r]
                for r in range(nr)
            ]
            A_unc = [
                S.half_resolution() * abs(nu[p2][r])
                for r in range(nr)
            ]
            add_constraint(
                constraints,
                A,
                Q.exact_value(0),
                f"selectividad {names[p1]}/{names[p2]}",
                A_unc=A_unc,
                extra_sfs=[S.sf] if S.sf else [],
            )

        elif choice == 7:
            basis = ask_choice(
                "Definición de rendimiento: ",
                [
                    "Producto neto formado / producto teórico a partir del reactivo alimentado",
                    "Producto neto formado / producto teórico correspondiente al reactivo consumido",
                ],
            )
            rdes = select_reaction(
                nr,
                "Seleccione la reacción que define la relación estequiométrica deseada: ",
            )

            def ref_reactant(i):
                return nu[i][rdes] < 0 and all(x <= 0 for x in nu[i])

            def desired_product(i):
                return nu[i][rdes] > 0 and all(x >= 0 for x in nu[i])

            ia = select_index(
                names,
                "Seleccione el reactivo de referencia: ",
                ref_reactant,
            )
            ip = select_index(
                names,
                "Seleccione el producto cuyo rendimiento se especifica: ",
                desired_product,
            )
            Y = ask_percent("Rendimiento [%]: ")
            ratio = nu[ip][rdes] / (-nu[ia][rdes])

            if basis == 1:
                theoretical = q_mul(
                    initial[ia],
                    Q.exact_value(ratio),
                )
                bq = q_mul(Y, theoretical)
                add_constraint(
                    constraints,
                    nu[ip],
                    bq,
                    f"rendimiento de {names[ip]} sobre {names[ia]} alimentado",
                    extra_sfs=[Y.sf] if Y.sf else [],
                )
            else:
                A = [
                    nu[ip][r] + Y.value * ratio * nu[ia][r]
                    for r in range(nr)
                ]
                A_unc = [
                    Y.half_resolution() * abs(ratio * nu[ia][r])
                    for r in range(nr)
                ]
                add_constraint(
                    constraints,
                    A,
                    Q.exact_value(0),
                    f"rendimiento de {names[ip]} sobre {names[ia]} consumido",
                    A_unc=A_unc,
                    extra_sfs=[Y.sf] if Y.sf else [],
                )

    if not constraints:
        raise ValueError("No se ha introducido ninguna relación para determinar las extensiones.")
    return constraints


def calculate_final(names, nu, initial, xi_q):
    nr = len(xi_q)
    contributions = [
        [Q.exact_value(0) for _ in range(nr)]
        for _ in names
    ]
    final = []
    for i in range(len(names)):
        changes = []
        for r in range(nr):
            d = q_mul(Q.exact_value(nu[i][r]), xi_q[r])
            contributions[i][r] = d
            changes.append(d)
        total_change = q_sum(changes)
        final.append(q_add(initial[i], total_change))
    return contributions, final


def check_nonnegative(values, names):
    bad = [
        (names[i], values[i].value)
        for i in range(len(names))
        if values[i].value < -ZERO_TOL
    ]
    if bad:
        raise ValueError(
            "Las extensiones conducen a cantidades o caudales negativos: "
            + "; ".join(f"{n}={v}" for n, v in bad)
        )


def compatible(a, b):
    diff = abs(a.value - b.value)
    tol = a.half_resolution() + b.half_resolution()
    if a.exact and b.exact:
        return diff <= ZERO_TOL
    return diff <= max(tol, ZERO_TOL)


def verification_constraints(names, nu, initial, unit):
    constraints = []
    observed = []
    print("\nIntroduzca el conjunto completo de cantidades o caudales finales.")
    for i, name in enumerate(names):
        nf = ask_q(
            f"Final/salida de {name} [{unit}]: ",
            minimum=0,
            exact_zero=True,
        )
        observed.append(nf)
        bq = q_sub(nf, initial[i])
        add_constraint(
            constraints,
            nu[i],
            bq,
            f"balance de {name}",
        )
    return constraints, observed


def ask_elemental_data(names):
    c = ask_choice(
        "Comprobación elemental: ",
        ["No introducir composición elemental", "Introducir composición elemental"],
    )
    if c == 1:
        return None
    data = {}
    for name in names:
        ne = ask_int(f"Número de elementos distintos presentes en {name}: ", 1)
        comp = {}
        for j in range(ne):
            while True:
                e = input(f"  Símbolo del elemento {j+1}: ").strip()
                if e and e not in comp:
                    break
                print("  Error: símbolo vacío o repetido.")
            while True:
                raw = input(f"  Número de átomos de {e} en {name}: ").strip()
                try:
                    a = parse_exact_coefficient(raw)
                    if a <= 0:
                        raise ValueError
                    comp[e] = a
                    break
                except Exception:
                    print("  Error: valor positivo requerido.")
        data[name] = comp
    return data


def check_reaction_elements(names, nu, elemental):
    if elemental is None:
        return []
    elems = sorted({e for comp in elemental.values() for e in comp})
    nr = len(nu[0])
    for r in range(nr):
        for e in elems:
            res = sum(
                nu[i][r] * elemental[names[i]].get(e, Decimal(0))
                for i in range(len(names))
            )
            if abs(res) > ZERO_TOL:
                raise ValueError(
                    f"La reacción {r+1} no conserva el elemento {e} "
                    f"(residuo {res})."
                )
    return elems


def elemental_totals(names, values, elemental):
    totals = {}
    if elemental is None:
        return totals
    for e in sorted({x for comp in elemental.values() for x in comp}):
        totals[e] = q_sum(
            [
                q_mul(
                    Q.exact_value(elemental[names[i]].get(e, Decimal(0))),
                    values[i],
                )
                for i in range(len(names))
            ]
        )
    return totals


def ask_molar_masses(names):
    c = ask_choice(
        "Comprobación de cierre másico: ",
        ["No introducir masas molares", "Introducir masas molares"],
    )
    if c == 1:
        return None
    masses = []
    for name in names:
        q = ask_q(f"Masa molar de {display_species(name)} [g mol^-1]: ", minimum=0)
        if q.value <= 0:
            raise ValueError("Las masas molares deben ser positivas.")
        masses.append(q)
    return masses


def total_mass(values, masses):
    return q_sum([q_mul(values[i], masses[i]) for i in range(len(values))])


def display_stream(names, values, unit, title):
    print(f"\n{title}:")
    for i, name in enumerate(names):
        print(f"  {display_species(name)}: {format_q(values[i])} {unit}")
    total = q_sum(values)
    print(f"  TOTAL: {format_q(total)} {unit}")
    if total.value > 0:
        print("  Composición molar:")
        for i, name in enumerate(names):
            print(f"    {name}: {format_q(q_div(values[i], total))}")


def optional_separation(names, final, unit):
    c = ask_choice(
        "¿Desea aplicar una separación posterior sencilla por recuperación? ",
        ["No", "Sí"],
    )
    if c == 1:
        return
    i = select_index(
        names,
        "Seleccione la especie recuperada en la corriente P: ",
    )
    rec = ask_percent("Recuperación [%]: ")
    recovered = q_mul(final[i], rec)

    P = [Q.exact_value(0) for _ in names]
    L = [q for q in final]
    P[i] = recovered
    L[i] = q_sub(final[i], recovered)

    print("\nSEPARACIÓN POSTERIOR")
    print(
        "Hipótesis: P contiene únicamente la especie recuperada; "
        "las demás especies y la fracción no recuperada quedan en L."
    )
    display_stream(names, P, unit, "Corriente P")
    display_stream(names, L, unit, "Corriente L")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Resuelve o comprueba balances molares con varias reacciones "
            "estequiométricamente independientes."
        ),
        epilog=(
            "No requiere NumPy. Las relaciones se introducen mediante menús "
            "químicamente interpretables."
        ),
    )
    parser.parse_args()

    print("=" * 80)
    print("SCRIPT 13.2 - BALANCE REACTIVO CON VARIAS REACCIONES")
    print("=" * 80)

    task = ask_choice(
        "Tipo de uso: ",
        [
            "Resolver las extensiones y el balance",
            "Comprobar cantidades o caudales finales obtenidos manualmente/experimentalmente",
        ],
    )
    system = ask_choice(
        "Tipo de sistema: ",
        ["Sistema discontinuo cerrado", "Sistema continuo en estado estacionario"],
    )
    continuous = system == 2
    unit = ask_units(continuous)

    try:
        names, nu, nr = ask_reactions()
        initial = ask_initial(names, continuous, unit)

        elemental = ask_elemental_data(names)
        elems = check_reaction_elements(names, nu, elemental)

        observed = None
        if task == 1:
            constraints = collect_constraints(names, nu, nr, initial, unit)
        else:
            constraints, observed = verification_constraints(
                names, nu, initial, unit
            )

        xi_values, result_sf, independent_rows = solve_constraints(
            constraints, nr
        )
        xi_q = [q_from_sf(x, result_sf[i]) for i, x in enumerate(xi_values)]

        contributions, final = calculate_final(names, nu, initial, xi_q)
        check_nonnegative(final, names)

        if observed is not None:
            for i, name in enumerate(names):
                if not compatible(final[i], observed[i]):
                    raise ValueError(
                        f"El valor final de {display_species(name)} no es compatible con las "
                        "extensiones calculadas."
                    )
            # Para el informe de verificación se conservan exactamente los datos
            # introducidos por el usuario.
            final_report = observed
        else:
            final_report = final

        molar_masses = ask_molar_masses(names)

        print("\n" + "=" * 80)
        print("RESULTADOS")
        print("=" * 80)

        xi_label = "xi_dot" if continuous else "xi"
        print("\nExtensiones:")
        for r, q in enumerate(xi_q, 1):
            print(f"  {xi_label}_{r} = {format_q(q)} {unit}")
            if q.value < 0:
                print(
                    "    Aviso: valor negativo; el avance neto es opuesto al "
                    "sentido en que se escribió esta reacción."
                )

        print("\nContribución de cada reacción a cada especie:")
        for i, name in enumerate(names):
            print(f"  {display_species(name)}:")
            for r in range(nr):
                d = contributions[i][r]
                if d.value > 0:
                    action = "forma"
                    mag = d
                elif d.value < 0:
                    action = "consume"
                    mag = q_abs(d)
                else:
                    action = "sin cambio"
                    mag = d
                if action == "sin cambio":
                    print(f"    R{r+1}: sin cambio")
                else:
                    print(
                        f"    R{r+1}: {action} {format_q(mag)} {unit}"
                    )

        display_stream(
            names,
            final_report,
            unit,
            "Cantidades finales" if not continuous else "Caudales molares totales de salida",
        )

        print("\nCOMPROBACIONES")
        print("  Reacciones estequiométricamente independientes: sí.")
        print("  Número de relaciones independientes suficiente: sí.")
        print("  Especificaciones compatibles con su precisión: sí.")
        print("  Cantidades o caudales negativos: no.")

        if elemental is not None:
            t0 = elemental_totals(names, initial, elemental)
            tf = elemental_totals(names, final_report, elemental)
            print("  Balances elementales:")
            for e in elems:
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
            mf = total_mass(final_report, molar_masses)
            ok = compatible(m0, mf)
            print(
                f"  Cierre másico: entrada/inicial = {format_q(m0)}; "
                f"salida/final = {format_q(mf)}; "
                f"{'correcto' if ok else 'NO CIERRA'}"
            )
            if not ok:
                raise ValueError("El cierre másico no es compatible con los datos.")
        else:
            print("  Cierre másico: no comprobado.")

        optional_separation(names, final_report, unit)
        return 0

    except (ValueError, ZeroDivisionError) as e:
        print(f"\nERROR: {e}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
