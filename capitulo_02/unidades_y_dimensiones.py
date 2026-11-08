#!/usr/bin/env python3
"""
HERRAMIENTAS DEL CAPÍTULO 2: UNIDADES Y DIMENSIONES

Finalidad
---------
Aplicación complementaria para efectuar y comprobar los cálculos repetitivos
del capítulo 2 de «Estequiometría y cálculos químicos»: conversiones de
unidades, cifras significativas, propagación lineal de incertidumbres y
análisis dimensional mediante el teorema pi de Buckingham.

Hipótesis y límites
-------------------
* Las conversiones utilizan los factores declarados en UNIDADES. Los factores
  son exactos salvo que la definición de la unidad indique otra cosa.
* La propagación de incertidumbres aplica una aproximación lineal de primer
  orden. Las incertidumbres estándar se combinan mediante una matriz de
  covarianzas; la estimación máxima suma valores absolutos.
* La matriz de covarianzas debe ser simétrica. El programa comprueba además
  que la varianza calculada no sea negativa, pero no sustituye un análisis
  metrológico completo.
* El análisis de Buckingham obtiene una base racional del espacio nulo de la
  matriz dimensional. La base no es única: productos y potencias de los grupos
  obtenidos también constituyen grupos adimensionales válidos.
* El programa acepta punto o coma decimal en las entradas. En pantalla muestra
  coma decimal, de acuerdo con el uso habitual en español.

Entradas y salidas
------------------
Entradas: valores introducidos por teclado o, para conversiones y redondeos,
argumentos opcionales de línea de órdenes.
Salidas: resultados numéricos, unidades, contribuciones de incertidumbre y
grupos adimensionales. No se escriben archivos ni se modifican datos externos.

Uso
---
    python unidades_y_dimensiones.py
    python unidades_y_dimensiones.py --help
    python unidades_y_dimensiones.py convertir 2,5 atm Pa
    python unidades_y_dimensiones.py redondear 12,345 4
    python unidades_y_dimensiones.py --autocomprobar

El menú interactivo reúne todas las funciones. Las funciones internas pueden
importarse desde otros programas sin iniciar el menú.
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN, localcontext
from fractions import Fraction
from typing import Iterable, Sequence


VERSION = "1.0.0"
DIMENSIONES = ("M", "L", "T", "Θ", "N", "I", "J")


@dataclass(frozen=True)
class Unidad:
    """Unidad lineal respecto de la unidad de referencia de su categoría."""

    factor: float
    nombre: str


# Cada factor transforma la unidad indicada en la unidad de referencia.
UNIDADES: dict[str, dict[str, Unidad]] = {
    "longitud": {
        "m": Unidad(1.0, "metro"),
        "km": Unidad(1e3, "kilómetro"),
        "cm": Unidad(1e-2, "centímetro"),
        "mm": Unidad(1e-3, "milímetro"),
        "µm": Unidad(1e-6, "micrómetro"),
        "nm": Unidad(1e-9, "nanómetro"),
        "in": Unidad(0.0254, "pulgada"),
        "ft": Unidad(0.3048, "pie"),
    },
    "masa": {
        "kg": Unidad(1.0, "kilogramo"),
        "g": Unidad(1e-3, "gramo"),
        "mg": Unidad(1e-6, "miligramo"),
        "µg": Unidad(1e-9, "microgramo"),
        "t": Unidad(1e3, "tonelada"),
        "lbm": Unidad(0.45359237, "libra masa"),
        "oz": Unidad(0.028349523125, "onza"),
    },
    "tiempo": {
        "s": Unidad(1.0, "segundo"),
        "min": Unidad(60.0, "minuto"),
        "h": Unidad(3600.0, "hora"),
        "d": Unidad(86400.0, "día"),
    },
    "volumen": {
        "m3": Unidad(1.0, "metro cúbico"),
        "L": Unidad(1e-3, "litro"),
        "mL": Unidad(1e-6, "mililitro"),
        "cm3": Unidad(1e-6, "centímetro cúbico"),
        "ft3": Unidad(0.028316846592, "pie cúbico"),
        "in3": Unidad(0.000016387064, "pulgada cúbica"),
        "gal_US": Unidad(0.003785411784, "galón estadounidense"),
        "gal_imp": Unidad(0.00454609, "galón imperial"),
    },
    "presión": {
        "Pa": Unidad(1.0, "pascal"),
        "kPa": Unidad(1e3, "kilopascal"),
        "MPa": Unidad(1e6, "megapascal"),
        "bar": Unidad(1e5, "bar"),
        "atm": Unidad(101325.0, "atmósfera estándar"),
        "mmHg": Unidad(101325.0 / 760.0, "milímetro de mercurio convencional"),
        "torr": Unidad(101325.0 / 760.0, "torr"),
        "psi": Unidad(6894.757293168, "libra-fuerza por pulgada cuadrada"),
    },
    "energía": {
        "J": Unidad(1.0, "julio"),
        "kJ": Unidad(1e3, "kilojulio"),
        "cal": Unidad(4.184, "caloría termoquímica"),
        "kcal": Unidad(4184.0, "kilocaloría termoquímica"),
        "Btu_IT": Unidad(1055.05585262, "Btu internacional"),
        "kWh": Unidad(3.6e6, "kilovatio hora"),
    },
    "cantidad de sustancia": {
        "mol": Unidad(1.0, "mol"),
        "mmol": Unidad(1e-3, "milimol"),
        "µmol": Unidad(1e-6, "micromol"),
        "kmol": Unidad(1e3, "kilomol"),
        "lbmol": Unidad(453.59237, "libra-mol"),
    },
    "velocidad": {
        "m/s": Unidad(1.0, "metro por segundo"),
        "cm/s": Unidad(1e-2, "centímetro por segundo"),
        "m/min": Unidad(1.0 / 60.0, "metro por minuto"),
        "m/h": Unidad(1.0 / 3600.0, "metro por hora"),
        "km/h": Unidad(1000.0 / 3600.0, "kilómetro por hora"),
        "ft/s": Unidad(0.3048, "pie por segundo"),
    },
    "caudal volumétrico": {
        "m3/s": Unidad(1.0, "metro cúbico por segundo"),
        "m3/h": Unidad(1.0 / 3600.0, "metro cúbico por hora"),
        "L/s": Unidad(1e-3, "litro por segundo"),
        "L/min": Unidad(1e-3 / 60.0, "litro por minuto"),
        "gal_US/min": Unidad(0.003785411784 / 60.0, "galón estadounidense por minuto"),
    },
    "densidad": {
        "kg/m3": Unidad(1.0, "kilogramo por metro cúbico"),
        "g/L": Unidad(1.0, "gramo por litro"),
        "g/mL": Unidad(1000.0, "gramo por mililitro"),
        "g/cm3": Unidad(1000.0, "gramo por centímetro cúbico"),
        "lbm/ft3": Unidad(16.01846337396, "libra masa por pie cúbico"),
    },
    "viscosidad dinámica": {
        "Pa·s": Unidad(1.0, "pascal segundo"),
        "mPa·s": Unidad(1e-3, "milipascal segundo"),
        "P": Unidad(0.1, "poise"),
        "cP": Unidad(1e-3, "centipoise"),
    },
    "concentración molar": {
        "mol/m3": Unidad(1.0, "mol por metro cúbico"),
        "mol/L": Unidad(1000.0, "mol por litro"),
        "mmol/L": Unidad(1.0, "milimol por litro"),
        "µmol/L": Unidad(1e-3, "micromol por litro"),
    },
}

ALIAS = {
    "um": "µm", "ug": "µg", "umol": "µmol", "umol/L": "µmol/L",
    "m^3": "m3", "cm^3": "cm3", "ft^3": "ft3", "in^3": "in3",
    "kg/m^3": "kg/m3", "g/cm^3": "g/cm3", "mol/m^3": "mol/m3",
    "Pa*s": "Pa·s", "mPa*s": "mPa·s", "gal/min": "gal_US/min",
}


def decimal_desde_texto(texto: str) -> Decimal:
    """Convierte una entrada con punto o coma decimal en Decimal."""
    limpio = texto.strip().replace(" ", "").replace("−", "-").replace(",", ".")
    try:
        valor = Decimal(limpio)
    except InvalidOperation as exc:
        raise ValueError(f"No se reconoce el número «{texto}».") from exc
    if not valor.is_finite():
        raise ValueError("El valor debe ser finito.")
    return valor


def numero(texto: str) -> float:
    """Convierte una entrada decimal española en float finito."""
    valor = float(decimal_desde_texto(texto))
    if not math.isfinite(valor):
        raise ValueError("El valor debe ser finito.")
    return valor


def fraccion(texto: str) -> Fraction:
    """Lee un entero, decimal o cociente como fracción exacta."""
    limpio = texto.strip().replace(",", ".").replace("−", "-")
    try:
        return Fraction(limpio)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError(f"No se reconoce el exponente «{texto}».") from exc


def normalizar_unidad(simbolo: str) -> str:
    """Normaliza variantes tipográficas frecuentes de símbolos de unidad."""
    limpio = simbolo.strip().replace("³", "3").replace("²", "2")
    return ALIAS.get(limpio, limpio)


def localizar_unidad(simbolo: str) -> tuple[str, Unidad]:
    """Devuelve la categoría y los datos de un símbolo inequívoco."""
    simbolo = normalizar_unidad(simbolo)
    halladas = [(cat, uds[simbolo]) for cat, uds in UNIDADES.items() if simbolo in uds]
    if not halladas:
        raise ValueError(f"La unidad «{simbolo}» no está disponible.")
    if len(halladas) > 1:
        raise ValueError(f"La unidad «{simbolo}» resulta ambigua.")
    return halladas[0]


def convertir_unidad(valor: float, origen: str, destino: str) -> float:
    """Convierte entre dos unidades lineales de la misma categoría."""
    origen = normalizar_unidad(origen)
    destino = normalizar_unidad(destino)
    cat_o, unidad_o = localizar_unidad(origen)
    cat_d, unidad_d = localizar_unidad(destino)
    if cat_o != cat_d:
        raise ValueError(f"No se puede convertir {origen} ({cat_o}) en {destino} ({cat_d}).")
    return valor * unidad_o.factor / unidad_d.factor


def convertir_temperatura(valor: float, origen: str, destino: str) -> float:
    """Convierte temperaturas, no intervalos, entre °C, K, °F y °R."""
    origen = origen.strip().upper().replace("º", "°")
    destino = destino.strip().upper().replace("º", "°")
    alias = {"C": "°C", "F": "°F", "R": "°R"}
    origen, destino = alias.get(origen, origen), alias.get(destino, destino)
    validas = {"°C", "K", "°F", "°R"}
    if origen not in validas or destino not in validas:
        raise ValueError("Las escalas disponibles son °C, K, °F y °R.")
    if origen == "°C":
        kelvin = valor + 273.15
    elif origen == "K":
        kelvin = valor
    elif origen == "°F":
        kelvin = (valor - 32.0) * 5.0 / 9.0 + 273.15
    else:
        kelvin = valor * 5.0 / 9.0
    if kelvin < 0:
        raise ValueError("La temperatura resultante queda por debajo del cero absoluto.")
    if destino == "°C":
        return kelvin - 273.15
    if destino == "K":
        return kelvin
    if destino == "°F":
        return (kelvin - 273.15) * 9.0 / 5.0 + 32.0
    return kelvin * 9.0 / 5.0


def convertir_intervalo_temperatura(valor: float, origen: str, destino: str) -> float:
    """Convierte intervalos térmicos; no aplica desplazamientos de escala."""
    origen = origen.strip().upper().replace("º", "°")
    destino = destino.strip().upper().replace("º", "°")
    alias = {"C": "°C", "F": "°F", "R": "°R"}
    origen, destino = alias.get(origen, origen), alias.get(destino, destino)
    factores = {"°C": 1.0, "K": 1.0, "°F": 5.0 / 9.0, "°R": 5.0 / 9.0}
    if origen not in factores or destino not in factores:
        raise ValueError("Las escalas disponibles son °C, K, °F y °R.")
    return valor * factores[origen] / factores[destino]


def cifras_significativas_texto(texto: str) -> int:
    """Cuenta cifras significativas y señala enteros con ceros finales ambiguos."""
    original = texto.strip().replace(" ", "").replace("−", "-")
    # Validar la expresión numérica COMPLETA, incluido el exponente.
    # Antes, «1e» y «1eXYZ» se aceptaban porque solo se inspeccionaba
    # la mantisa. La validación no altera el conteo de los ceros finales.
    decimal_desde_texto(original)
    mantisa = re.split(r"[eE]", original, maxsplit=1)[0].lstrip("+-")
    posee_decimal = "." in mantisa or "," in mantisa
    digitos = mantisa.replace(".", "").replace(",", "")
    if not digitos.isdigit():
        raise ValueError(f"No se reconoce el número «{texto}».")
    if set(digitos) == {"0"}:
        if posee_decimal:
            parte_decimal = re.split(r"[.,]", mantisa, maxsplit=1)[1]
            return max(1, len(parte_decimal))
        return 1
    significativos = digitos.lstrip("0")
    if not posee_decimal and "e" not in original.lower() and significativos.endswith("0"):
        raise ValueError(
            "Los ceros finales de un entero sin separador decimal son ambiguos. "
            "Use notación científica (por ejemplo, 1,50e3) o indique las cifras explícitamente."
        )
    return len(significativos)


def redondear_significativas(valor: Decimal | float | str, cifras: int) -> Decimal:
    """Redondea al par con el número indicado de cifras significativas."""
    if cifras < 1:
        raise ValueError("El número de cifras significativas debe ser positivo.")
    dec = valor if isinstance(valor, Decimal) else decimal_desde_texto(str(valor))
    if dec == 0:
        return Decimal(0)
    exponente = dec.copy_abs().adjusted() - cifras + 1
    cuantizador = Decimal(1).scaleb(exponente)
    with localcontext() as contexto:
        contexto.prec = max(50, len(dec.as_tuple().digits) + abs(exponente) + 5)
        return dec.quantize(cuantizador, rounding=ROUND_HALF_EVEN)


def redondear_a_orden(valor: Decimal | float | str, exponente: int) -> Decimal:
    """Redondea al orden decimal 10**exponente mediante redondeo al par."""
    dec = valor if isinstance(valor, Decimal) else decimal_desde_texto(str(valor))
    return dec.quantize(Decimal(1).scaleb(exponente), rounding=ROUND_HALF_EVEN)


def formato_decimal(valor: Decimal | float, cifras: int | None = None) -> str:
    """Da formato español legible y evita residuos binarios."""
    dec = valor if isinstance(valor, Decimal) else Decimal(str(valor))
    if cifras is not None:
        dec = redondear_significativas(dec, cifras)
    if dec == 0:
        if cifras is not None and cifras > 1:
            texto = "0," + "0" * cifras
        else:
            texto = "0"
    elif (
        dec.copy_abs().adjusted() >= 6
        or dec.copy_abs().adjusted() <= -4
        or (cifras is not None and dec.as_tuple().exponent > 0)
    ):
        texto = f"{dec.normalize():E}"
        mantisa, exp = texto.split("E")
        if cifras is not None:
            digitos_presentes = len(mantisa.replace("-", "").replace(".", ""))
            if digitos_presentes < cifras:
                if "." not in mantisa:
                    mantisa += "."
                mantisa += "0" * (cifras - digitos_presentes)
        texto = f"{mantisa} × 10^{int(exp)}"
    else:
        texto = format(dec, "f")
    return texto.replace(".", ",")


def incertidumbre_relativa(valor: float, incertidumbre: float) -> tuple[float, float]:
    """Calcula incertidumbre relativa y porcentual."""
    if valor == 0:
        raise ValueError("No se define incertidumbre relativa respecto de un valor nulo.")
    if incertidumbre < 0:
        raise ValueError("La incertidumbre no puede ser negativa.")
    relativa = incertidumbre / abs(valor)
    return relativa, 100.0 * relativa


def validar_correlaciones_semidefinidas(correlaciones: Sequence[Sequence[float]]) -> None:
    """Exige una matriz de correlación semidefinida positiva (sin NumPy).

    Utiliza eliminación simétrica (complementos de Schur) con tolerancia
    absoluta para manejar correlaciones perfectas y redondeo numérico.
    Una matriz con elementos entre -1 y 1 y diagonal 1 no es
    necesariamente una matriz de correlación físicamente admisible.
    """
    n = len(correlaciones)
    resto = [list(map(float, fila)) for fila in correlaciones]
    tolerancia = 1e-10
    for k in range(n):
        pivote = resto[k][k]
        if pivote < -tolerancia:
            raise ValueError(
                "La matriz de correlaciones no es semidefinida positiva."
            )
        if abs(pivote) <= tolerancia:
            if any(abs(resto[i][k]) > tolerancia for i in range(k + 1, n)):
                raise ValueError(
                    "La matriz de correlaciones no es semidefinida positiva."
                )
            continue
        columna = [resto[i][k] for i in range(k + 1, n)]
        for i in range(k + 1, n):
            for j in range(i, n):
                nuevo = resto[i][j] - columna[i-k-1] * columna[j-k-1] / pivote
                resto[i][j] = nuevo
                resto[j][i] = nuevo


def matriz_covarianzas(
    incertidumbres: Sequence[float],
    correlaciones: Sequence[Sequence[float]] | None = None,
) -> list[list[float]]:
    """Construye la matriz de covarianzas a partir de u y r."""
    n = len(incertidumbres)
    if any(u < 0 or not math.isfinite(u) for u in incertidumbres):
        raise ValueError("Las incertidumbres deben ser finitas y no negativas.")
    if correlaciones is None:
        correlaciones = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    if len(correlaciones) != n or any(len(fila) != n for fila in correlaciones):
        raise ValueError("La matriz de correlaciones debe ser cuadrada.")
    cov = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            r = float(correlaciones[i][j])
            if not -1.0 <= r <= 1.0:
                raise ValueError("Cada coeficiente de correlación debe estar entre -1 y 1.")
            if i == j and not math.isclose(r, 1.0, abs_tol=1e-12):
                raise ValueError("La diagonal de la matriz de correlaciones debe ser 1.")
            if not math.isclose(r, float(correlaciones[j][i]), abs_tol=1e-12):
                raise ValueError("La matriz de correlaciones debe ser simétrica.")
            cov[i][j] = r * incertidumbres[i] * incertidumbres[j]
    # Una matriz simétrica con diagonal 1 y |r_ij| <= 1 no basta:
    # debe ser semidefinida positiva, incluso si las sensibilidades
    # particulares del cálculo producen una varianza positiva.
    validar_correlaciones_semidefinidas(correlaciones)
    return cov


def propagar_incertidumbre_estandar(
    sensibilidades: Sequence[float],
    incertidumbres: Sequence[float],
    correlaciones: Sequence[Sequence[float]] | None = None,
) -> tuple[float, list[float], float]:
    """Calcula u_c = sqrt(c^T U c) y devuelve contribuciones diagonales."""
    if len(sensibilidades) != len(incertidumbres) or not sensibilidades:
        raise ValueError("Debe haber una sensibilidad por cada incertidumbre.")
    cov = matriz_covarianzas(incertidumbres, correlaciones)
    n = len(sensibilidades)
    varianza = sum(
        sensibilidades[i] * sensibilidades[j] * cov[i][j]
        for i in range(n) for j in range(n)
    )
    escala = sum((sensibilidades[i] * incertidumbres[i]) ** 2 for i in range(n))
    tolerancia = 1e-12 * max(1.0, escala)
    if varianza < -tolerancia:
        raise ValueError(
            "La matriz introducida produce una varianza negativa; revise las correlaciones."
        )
    varianza = max(0.0, varianza)
    diagonales = [(sensibilidades[i] * incertidumbres[i]) ** 2 for i in range(n)]
    covarianza_total = varianza - sum(diagonales)
    return math.sqrt(varianza), diagonales, covarianza_total


def incertidumbre_maxima(
    sensibilidades: Sequence[float], limites: Sequence[float]
) -> tuple[float, list[float]]:
    """Suma las contribuciones absolutas |c_i| Δx_i."""
    if len(sensibilidades) != len(limites) or not sensibilidades:
        raise ValueError("Debe haber una sensibilidad por cada límite.")
    if any(limite < 0 for limite in limites):
        raise ValueError("Los límites deben ser no negativos.")
    contribuciones = [abs(c * limite) for c, limite in zip(sensibilidades, limites)]
    return sum(contribuciones), contribuciones


def redondear_resultado_incertidumbre(
    valor: float, incertidumbre: float
) -> tuple[Decimal, Decimal, int]:
    """Redondea u a una cifra (dos si empieza por 1) y el valor al mismo orden."""
    if incertidumbre < 0:
        raise ValueError("La incertidumbre no puede ser negativa.")
    if incertidumbre == 0:
        return Decimal(str(valor)), Decimal(0), 0
    u_dec = Decimal(str(incertidumbre))
    primera = int(u_dec.copy_abs().scaleb(-u_dec.adjusted()).to_integral(rounding="ROUND_FLOOR"))
    cifras_u = 2 if primera == 1 else 1
    u_red = redondear_significativas(u_dec, cifras_u)
    orden = u_red.adjusted() - cifras_u + 1
    valor_red = redondear_a_orden(Decimal(str(valor)), orden)
    return valor_red, u_red, orden


def rango_matriz(matriz: Sequence[Sequence[Fraction]]) -> int:
    """Calcula el rango exacto de una matriz racional."""
    _, pivotes = rref(matriz)
    return len(pivotes)


def rref(
    matriz: Sequence[Sequence[Fraction]],
) -> tuple[list[list[Fraction]], list[int]]:
    """Obtiene la forma escalonada reducida y sus columnas pivote."""
    if not matriz:
        return [], []
    a = [list(map(Fraction, fila)) for fila in matriz]
    filas, columnas = len(a), len(a[0])
    if any(len(fila) != columnas for fila in a):
        raise ValueError("La matriz no es rectangular.")
    pivotes: list[int] = []
    fila_pivote = 0
    for col in range(columnas):
        candidata = next((f for f in range(fila_pivote, filas) if a[f][col]), None)
        if candidata is None:
            continue
        a[fila_pivote], a[candidata] = a[candidata], a[fila_pivote]
        divisor = a[fila_pivote][col]
        a[fila_pivote] = [x / divisor for x in a[fila_pivote]]
        for f in range(filas):
            if f != fila_pivote and a[f][col]:
                factor = a[f][col]
                a[f] = [x - factor * y for x, y in zip(a[f], a[fila_pivote])]
        pivotes.append(col)
        fila_pivote += 1
        if fila_pivote == filas:
            break
    return a, pivotes


def espacio_nulo(matriz: Sequence[Sequence[Fraction]]) -> list[list[Fraction]]:
    """Devuelve una base racional del espacio nulo de una matriz."""
    reducida, pivotes = rref(matriz)
    if not matriz:
        return []
    columnas = len(matriz[0])
    libres = [j for j in range(columnas) if j not in pivotes]
    base: list[list[Fraction]] = []
    for libre in libres:
        vector = [Fraction(0)] * columnas
        vector[libre] = Fraction(1)
        for fila, pivote in enumerate(pivotes):
            vector[pivote] = -reducida[fila][libre]
        base.append(simplificar_vector_entero(vector))
    return base


def mcm(a: int, b: int) -> int:
    """Mínimo común múltiplo para enteros no negativos."""
    return abs(a * b) // math.gcd(a, b) if a and b else 0


def simplificar_vector_entero(vector: Sequence[Fraction]) -> list[Fraction]:
    """Escala un vector racional hasta enteros coprimos, conservando el signo."""
    comun = 1
    for valor in vector:
        comun = mcm(comun, valor.denominator)
    enteros = [int(valor * comun) for valor in vector]
    divisor = 0
    for valor in enteros:
        divisor = math.gcd(divisor, abs(valor))
    divisor = divisor or 1
    enteros = [valor // divisor for valor in enteros]
    primer_no_nulo = next((valor for valor in enteros if valor), 1)
    if primer_no_nulo < 0:
        enteros = [-valor for valor in enteros]
    return [Fraction(valor) for valor in enteros]


def es_adimensional(exponentes: Sequence[Fraction]) -> bool:
    """Comprueba si todos los exponentes dimensionales son cero."""
    return all(exponente == 0 for exponente in exponentes)


def combinar_dimensiones(
    vectores: Sequence[Sequence[Fraction]], potencias: Sequence[Fraction]
) -> list[Fraction]:
    """Calcula la dimensión del producto de variables elevadas a potencias."""
    if len(vectores) != len(potencias) or not vectores:
        raise ValueError("Debe haber una potencia por cada variable.")
    if any(len(vector) != len(DIMENSIONES) for vector in vectores):
        raise ValueError(f"Cada vector debe tener {len(DIMENSIONES)} componentes.")
    return [
        sum(potencias[j] * vectores[j][i] for j in range(len(vectores)))
        for i in range(len(DIMENSIONES))
    ]


def grupos_buckingham(
    vectores: Sequence[Sequence[Fraction]],
) -> tuple[list[list[Fraction]], int]:
    """Obtiene una base de grupos pi a partir de columnas dimensionales."""
    if not vectores:
        raise ValueError("Debe introducir al menos una variable.")
    if any(len(vector) != len(DIMENSIONES) for vector in vectores):
        raise ValueError(f"Cada vector debe tener {len(DIMENSIONES)} componentes.")
    matriz = [[Fraction(vectores[col][fila]) for col in range(len(vectores))]
              for fila in range(len(DIMENSIONES))]
    return espacio_nulo(matriz), rango_matriz(matriz)


def formato_grupo(nombres: Sequence[str], exponentes: Sequence[Fraction]) -> str:
    """Representa un producto de variables y potencias como texto."""
    factores = []
    for nombre, exponente in zip(nombres, exponentes):
        if exponente == 0:
            continue
        if exponente == 1:
            factores.append(nombre)
        elif exponente.denominator == 1:
            factores.append(f"{nombre}^{exponente.numerator}")
        else:
            factores.append(f"{nombre}^({exponente.numerator}/{exponente.denominator})")
    return " · ".join(factores) if factores else "1"


def pedir_texto(mensaje: str, permitir_vacio: bool = False) -> str:
    """Solicita texto y evita entradas vacías accidentales."""
    while True:
        entrada = input(mensaje).strip()
        if entrada or permitir_vacio:
            return entrada
        print("La entrada no puede quedar vacía.")


def pedir_float(mensaje: str, minimo: float | None = None) -> float:
    """Solicita un número finito con validación opcional de mínimo."""
    while True:
        try:
            valor = numero(input(mensaje))
            if minimo is not None and valor < minimo:
                raise ValueError(f"El valor debe ser igual o mayor que {minimo}.")
            return valor
        except ValueError as error:
            print(f"Entrada no válida: {error}")


def pedir_entero(mensaje: str, minimo: int = 1) -> int:
    """Solicita un entero no menor que el límite indicado."""
    while True:
        try:
            valor = int(input(mensaje).strip())
            if valor < minimo:
                raise ValueError
            return valor
        except ValueError:
            print(f"Introduzca un número entero igual o mayor que {minimo}.")


def pausa() -> None:
    """Mantiene visible un resultado antes de regresar al menú."""
    input("\nPulse Intro para continuar...")


def menu_conversiones() -> None:
    """Interfaz de conversiones de unidades y temperaturas."""
    print("\nCONVERSIÓN DE UNIDADES")
    print("1. Magnitud con conversión lineal")
    print("2. Temperatura")
    print("3. Intervalo de temperatura")
    opcion = pedir_texto("Opción: ")
    valor_txt = pedir_texto("Valor: ")
    valor = numero(valor_txt)
    if opcion == "1":
        print("\nCategorías:")
        categorias = list(UNIDADES)
        for i, categoria in enumerate(categorias, 1):
            print(f"{i:2}. {categoria}")
        indice = pedir_entero("Categoría: ")
        if indice > len(categorias):
            raise ValueError("La categoría seleccionada no existe.")
        categoria = categorias[indice - 1]
        print("Unidades: " + ", ".join(UNIDADES[categoria]))
        origen = normalizar_unidad(pedir_texto("Unidad de origen: "))
        destino = normalizar_unidad(pedir_texto("Unidad de destino: "))
        if origen not in UNIDADES[categoria] or destino not in UNIDADES[categoria]:
            raise ValueError("Alguna unidad no pertenece a la categoría seleccionada.")
        resultado = convertir_unidad(valor, origen, destino)
    elif opcion in {"2", "3"}:
        print("Escalas: °C, K, °F, °R")
        origen = pedir_texto("Escala de origen: ")
        destino = pedir_texto("Escala de destino: ")
        funcion = convertir_temperatura if opcion == "2" else convertir_intervalo_temperatura
        resultado = funcion(valor, origen, destino)
    else:
        raise ValueError("La opción seleccionada no existe.")
    try:
        cifras = cifras_significativas_texto(valor_txt)
    except ValueError:
        cifras = pedir_entero("Cifras significativas que desea conservar: ")
    print(f"\nResultado: {formato_decimal(resultado, cifras)} {destino}")


def menu_cifras() -> None:
    """Interfaz de recuento, redondeo y operaciones con cifras significativas."""
    print("\nCIFRAS SIGNIFICATIVAS")
    print("1. Contar cifras significativas")
    print("2. Redondear un valor")
    print("3. Suma o resta")
    print("4. Producto o cociente")
    opcion = pedir_texto("Opción: ")
    if opcion == "1":
        texto = pedir_texto("Valor tal como está escrito: ")
        print(f"Número de cifras significativas: {cifras_significativas_texto(texto)}")
    elif opcion == "2":
        texto = pedir_texto("Valor: ")
        cifras = pedir_entero("Cifras significativas: ")
        print(f"Resultado: {formato_decimal(redondear_significativas(texto, cifras))}")
    elif opcion in {"3", "4"}:
        n = pedir_entero("Número de operandos: ", 2)
        textos = [pedir_texto(f"Operando {i + 1}: ") for i in range(n)]
        valores = [decimal_desde_texto(texto) for texto in textos]
        operador = pedir_texto("Operador (+, -, * o /): ")
        permitidos = {"3": {"+", "-"}, "4": {"*", "/"}}
        if operador not in permitidos[opcion]:
            raise ValueError("El operador no corresponde al tipo de operación.")
        resultado = valores[0]
        for valor in valores[1:]:
            if operador == "+": resultado += valor
            elif operador == "-": resultado -= valor
            elif operador == "*": resultado *= valor
            else:
                if valor == 0:
                    raise ValueError("No se puede dividir entre cero.")
                resultado /= valor
        if opcion == "3":
            ordenes = [decimal_desde_texto(t).as_tuple().exponent for t in textos]
            resultado = redondear_a_orden(resultado, max(ordenes))
        else:
            cifras = min(cifras_significativas_texto(t) for t in textos)
            resultado = redondear_significativas(resultado, cifras)
        print(f"Resultado: {formato_decimal(resultado)}")
    else:
        raise ValueError("La opción seleccionada no existe.")


def leer_datos_sensibilidad() -> tuple[list[str], list[float], list[float]]:
    """Lee nombres, coeficientes de sensibilidad e incertidumbres/límites."""
    n = pedir_entero("Número de magnitudes de entrada: ")
    nombres, sensibilidades, incertidumbres = [], [], []
    for i in range(n):
        print(f"\nMagnitud {i + 1}")
        nombres.append(pedir_texto("Nombre o símbolo: "))
        sensibilidades.append(pedir_float("Coeficiente de sensibilidad ∂R/∂x: "))
        incertidumbres.append(pedir_float("Incertidumbre estándar o límite: ", 0.0))
    return nombres, sensibilidades, incertidumbres


def menu_incertidumbres() -> None:
    """Interfaz de incertidumbres relativas, máximas y estándar."""
    print("\nINCERTIDUMBRES")
    print("1. Incertidumbre relativa y porcentual")
    print("2. Estimación máxima o conservadora")
    print("3. Incertidumbre estándar combinada")
    print("4. Expresar un resultado con su incertidumbre")
    opcion = pedir_texto("Opción: ")
    if opcion == "1":
        valor = pedir_float("Valor medido: ")
        u = pedir_float("Incertidumbre absoluta: ", 0.0)
        relativa, porcentual = incertidumbre_relativa(valor, u)
        print(f"u_r = {formato_decimal(relativa, 4)}")
        print(f"u_% = {formato_decimal(porcentual, 4)} %")
    elif opcion == "2":
        nombres, sensibilidades, limites = leer_datos_sensibilidad()
        total, contribuciones = incertidumbre_maxima(sensibilidades, limites)
        print("\nContribuciones absolutas:")
        for nombre, contribucion in zip(nombres, contribuciones):
            print(f"  {nombre}: {formato_decimal(contribucion, 6)}")
        print(f"ΔR_máx = {formato_decimal(total, 6)}")
    elif opcion == "3":
        nombres, sensibilidades, incertidumbres = leer_datos_sensibilidad()
        n = len(nombres)
        correlaciones = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
        if pedir_texto("¿Hay correlaciones entre magnitudes? (s/n): ").lower() == "s":
            for i in range(n):
                for j in range(i + 1, n):
                    r = pedir_float(f"r({nombres[i]},{nombres[j]}), entre -1 y 1: ")
                    if not -1 <= r <= 1:
                        raise ValueError("El coeficiente de correlación debe estar entre -1 y 1.")
                    correlaciones[i][j] = correlaciones[j][i] = r
        total, diagonales, cov_total = propagar_incertidumbre_estandar(
            sensibilidades, incertidumbres, correlaciones
        )
        print("\nContribuciones diagonales a la varianza:")
        for nombre, contribucion in zip(nombres, diagonales):
            print(f"  {nombre}: {formato_decimal(contribucion, 6)}")
        print(f"Términos cruzados de covarianza: {formato_decimal(cov_total, 6)}")
        print(f"u_c(R) = {formato_decimal(total, 6)}")
    elif opcion == "4":
        valor = pedir_float("Valor calculado: ")
        u = pedir_float("Incertidumbre absoluta: ", 0.0)
        valor_red, u_red, _ = redondear_resultado_incertidumbre(valor, u)
        print(f"Resultado: {formato_decimal(valor_red)} ± {formato_decimal(u_red)}")
    else:
        raise ValueError("La opción seleccionada no existe.")


def leer_vector_dimensional(nombre: str) -> list[Fraction]:
    """Lee los siete exponentes dimensionales de una variable."""
    print(f"Exponentes de {nombre} en el orden {', '.join(DIMENSIONES)}")
    while True:
        partes = pedir_texto("Sepárelos mediante espacios: ").split()
        if len(partes) != len(DIMENSIONES):
            print(f"Deben introducirse exactamente {len(DIMENSIONES)} exponentes.")
            continue
        try:
            return [fraccion(parte) for parte in partes]
        except ValueError as error:
            print(f"Entrada no válida: {error}")


def menu_dimensiones() -> None:
    """Interfaz de comprobación dimensional y teorema pi."""
    print("\nANÁLISIS DIMENSIONAL")
    print("Orden de dimensiones: M, L, T, Θ, N, I, J")
    print("1. Dimensión de un producto de potencias")
    print("2. Comparar la dimensión de varios términos")
    print("3. Obtener grupos π de Buckingham")
    opcion = pedir_texto("Opción: ")
    if opcion == "1":
        n = pedir_entero("Número de variables: ")
        nombres, vectores, potencias = [], [], []
        for i in range(n):
            nombre = pedir_texto(f"Nombre de la variable {i + 1}: ")
            nombres.append(nombre)
            vectores.append(leer_vector_dimensional(nombre))
            potencias.append(fraccion(pedir_texto(f"Potencia de {nombre}: ")))
        resultado = combinar_dimensiones(vectores, potencias)
        print("Producto: " + formato_grupo(nombres, potencias))
        print("Vector dimensional: [" + ", ".join(map(str, resultado)) + "]")
        print("El producto es adimensional." if es_adimensional(resultado)
              else "El producto no es adimensional.")
    elif opcion == "2":
        n = pedir_entero("Número de términos que desea comparar: ", 2)
        vectores = [leer_vector_dimensional(f"término {i + 1}") for i in range(n)]
        iguales = all(vector == vectores[0] for vector in vectores[1:])
        print("La ecuación es dimensionalmente homogénea." if iguales
              else "Los términos no tienen la misma dimensión.")
    elif opcion == "3":
        n = pedir_entero("Número de variables: ", 2)
        nombres, vectores = [], []
        for i in range(n):
            nombre = pedir_texto(f"Nombre de la variable {i + 1}: ")
            nombres.append(nombre)
            vectores.append(leer_vector_dimensional(nombre))
        grupos, rango = grupos_buckingham(vectores)
        print(f"\nRango dimensional: {rango}")
        print(f"Número de grupos independientes: {n - rango}")
        for i, grupo in enumerate(grupos, 1):
            print(f"π{i} = {formato_grupo(nombres, grupo)}")
    else:
        raise ValueError("La opción seleccionada no existe.")


def mostrar_unidades() -> None:
    """Muestra las unidades disponibles agrupadas por magnitud."""
    print("\nUNIDADES DISPONIBLES")
    for categoria, unidades in UNIDADES.items():
        print(f"{categoria.capitalize()}: {', '.join(unidades)}")
    print("Temperaturas e intervalos: °C, K, °F, °R")


def menu_principal() -> None:
    """Ejecuta el menú principal hasta que el usuario decide salir."""
    while True:
        print("\n" + "=" * 64)
        print("HERRAMIENTAS DEL CAPÍTULO 2: UNIDADES Y DIMENSIONES")
        print("=" * 64)
        print("1. Conversión de unidades")
        print("2. Cifras significativas y redondeo")
        print("3. Propagación y expresión de incertidumbres")
        print("4. Análisis dimensional y teorema π de Buckingham")
        print("5. Mostrar unidades disponibles")
        print("0. Salir")
        opcion = input("Opción: ").strip()
        if opcion == "0":
            print("Fin del programa.")
            return
        acciones = {
            "1": menu_conversiones,
            "2": menu_cifras,
            "3": menu_incertidumbres,
            "4": menu_dimensiones,
            "5": mostrar_unidades,
        }
        accion = acciones.get(opcion)
        if accion is None:
            print("Opción no válida.")
            continue
        try:
            accion()
        except (ValueError, ZeroDivisionError) as error:
            print(f"\nNo se pudo completar el cálculo: {error}")
        except (EOFError, KeyboardInterrupt):
            print("\nOperación cancelada.")
        pausa()


def autocomprobar() -> None:
    """Ejecuta casos numéricos representativos del capítulo."""
    pruebas = [
        ("125 ft3 → m3", convertir_unidad(125, "ft3", "m3"), 3.539605824, 1e-12),
        ("2,5 atm → Pa", convertir_unidad(2.5, "atm", "Pa"), 253312.5, 1e-12),
        ("150 cal → J", convertir_unidad(150, "cal", "J"), 627.6, 1e-12),
        ("12,5 cm/s → m/h", convertir_unidad(12.5, "cm/s", "m/h"), 450.0, 1e-12),
        ("25 °C → K", convertir_temperatura(25, "°C", "K"), 298.15, 1e-12),
    ]
    for nombre, obtenido, esperado, tolerancia in pruebas:
        if not math.isclose(obtenido, esperado, rel_tol=tolerancia, abs_tol=tolerancia):
            raise AssertionError(f"Fallo en {nombre}: {obtenido} != {esperado}")
    assert cifras_significativas_texto("0,00450") == 3
    assert cifras_significativas_texto("120,0") == 4
    assert cifras_significativas_texto("3,020e5") == 4
    assert redondear_significativas("2,345", 3) == Decimal("2.34")
    assert redondear_significativas("2,355", 3) == Decimal("2.36")
    u, _, _ = propagar_incertidumbre_estandar([1, -1], [0.03, 0.03], [[1, 0.8], [0.8, 1]])
    assert math.isclose(u, math.sqrt(0.00036), rel_tol=1e-12)
    # Reynolds: rho*v*D/mu debe ser adimensional.
    vectores = [
        [1, -3, 0, 0, 0, 0, 0],
        [0, 1, -1, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0],
        [1, -1, -1, 0, 0, 0, 0],
    ]
    assert es_adimensional(combinar_dimensiones(vectores, [1, 1, 1, -1]))
    grupos, rango = grupos_buckingham(vectores)
    assert rango == 3 and len(grupos) == 1
    print(f"Autocomprobación superada: {len(pruebas) + 7} verificaciones.")


def crear_analizador() -> argparse.ArgumentParser:
    """Construye la interfaz de línea de órdenes."""
    analizador = argparse.ArgumentParser(
        add_help=False,
        description=(
            "Herramientas del capítulo 2: conversiones, cifras significativas, "
            "incertidumbres y análisis dimensional. Sin argumentos abre el menú."
        )
    )
    analizador._positionals.title = "órdenes"
    analizador._optionals.title = "opciones"
    analizador.add_argument("-h", "--help", action="help", help="muestra esta ayuda y termina")
    analizador.add_argument(
        "--version", action="version", version=f"%(prog)s {VERSION}",
        help="muestra la versión y termina",
    )
    analizador.add_argument(
        "--autocomprobar", action="store_true",
        help="ejecuta verificaciones internas y termina",
    )
    sub = analizador.add_subparsers(dest="orden")
    conv = sub.add_parser("convertir", help="convierte una magnitud lineal")
    conv.add_argument("valor", help="valor numérico; admite coma decimal")
    conv.add_argument("origen", help="unidad de origen")
    conv.add_argument("destino", help="unidad de destino")
    conv.add_argument("-c", "--cifras", type=int, help="cifras significativas de salida")
    red = sub.add_parser("redondear", help="redondea un valor al par")
    red.add_argument("valor", help="valor numérico; admite coma decimal")
    red.add_argument("cifras", type=int, help="número de cifras significativas")
    sub.add_parser("unidades", help="muestra las unidades disponibles")
    return analizador


def main(argv: Sequence[str] | None = None) -> int:
    """Punto de entrada; devuelve un código de estado del proceso."""
    analizador = crear_analizador()
    args = analizador.parse_args(argv)
    try:
        if args.autocomprobar:
            autocomprobar()
        elif args.orden == "convertir":
            valor = numero(args.valor)
            resultado = convertir_unidad(valor, args.origen, args.destino)
            cifras = args.cifras
            if cifras is None:
                cifras = cifras_significativas_texto(args.valor)
            print(f"{formato_decimal(resultado, cifras)} {normalizar_unidad(args.destino)}")
        elif args.orden == "redondear":
            print(formato_decimal(redondear_significativas(args.valor, args.cifras)))
        elif args.orden == "unidades":
            mostrar_unidades()
        else:
            menu_principal()
    except (ValueError, ZeroDivisionError, AssertionError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
