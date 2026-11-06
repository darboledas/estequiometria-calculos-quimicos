#!/usr/bin/env python3
'Reactivo limitante y balances de una reacción.\nFinalidad: calcular máximos, excesos y reactivos sobrantes.\nHipótesis: una reacción; impurezas inertes.\nEntradas: fórmulas, masas o mol, purezas y masas molares.\nSalidas: limitantes, avance, consumo, sobrantes y productos.\nRequisitos: Python 3.10+, biblioteca estándar.'

import argparse
import re
from decimal import Decimal, getcontext, ROUND_HALF_UP

getcontext().prec = 80
D = Decimal

AYUDA_NUMEROS = """
INTRODUCCIÓN DE DATOS
- Puede utilizar coma o punto decimal y notación científica: 1,20e-3.
- No utilice separadores de millares.
- Los ceros finales escritos cuentan: 1,20 tiene tres cifras.
- En enteros también cuentan: 1200 tiene cuatro cifras.
  Para indicar otra precisión escriba, por ejemplo, 1200:2.
- El sufijo ! indica un dato exacto: 100!, 0!, 2!.
  Utilícelo solo cuando el dato realmente sea exacto.
- Los coeficientes estequiométricos y factores de unidades son exactos.
- Las masas molares introducidas también intervienen en la precisión.
- No se redondean los valores intermedios.
- En sumas/restas se controla la posición decimal; en productos/cocientes,
  las cifras significativas. Esto no sustituye el cálculo de incertidumbres.
- Los resultados utilizan coma decimal y notación científica para evitar
  ambigüedades en los ceros finales.
- Escriba volver en una entrada numérica para regresar al menú.
"""

class Volver(Exception):
    pass


class Q:
    """Valor decimal y posición de su última cifra; p=None significa exacto."""

    def __init__(self, valor, p=None):
        self.v = valor if isinstance(valor, D) else D(str(valor))
        self.p = p

    @staticmethod
    def convertir(x):
        return x if isinstance(x, Q) else Q(x)

    def cifras(self):
        if self.p is None:
            return None
        if not self.v:
            return 1
        redondeado = self.v.quantize(
            D(1).scaleb(self.p), rounding=ROUND_HALF_UP
        )
        return max(1, redondeado.copy_abs().adjusted() - self.p + 1)

    def paso(self):
        return D(0) if self.p is None else D(1).scaleb(self.p)

    def __add__(self, otro):
        otro = Q.convertir(otro)
        posiciones = [p for p in (self.p, otro.p) if p is not None]
        return Q(self.v + otro.v, max(posiciones) if posiciones else None)

    __radd__ = __add__

    def __neg__(self):
        return Q(-self.v, self.p)

    def __sub__(self, otro):
        return self + (-Q.convertir(otro))

    def __rsub__(self, otro):
        return Q.convertir(otro) - self

    def producto(self, otro, dividir=False):
        otro = Q.convertir(otro)
        if dividir and otro.v == 0:
            raise ValueError("No puede dividir entre cero.")
        valor = self.v / otro.v if dividir else self.v * otro.v
        cifras = [
            n for n in (self.cifras(), otro.cifras()) if n is not None
        ]
        if not cifras:
            return Q(valor)

        if valor:
            n = min(cifras)
            p = valor.copy_abs().adjusted() - n + 1
            redondeado = valor.quantize(
                D(1).scaleb(p), rounding=ROUND_HALF_UP
            )
            if redondeado:
                p = redondeado.copy_abs().adjusted() - n + 1
            return Q(valor, p)

        # Un cero medido conserva una resolución transformada.
        posiciones = []
        if self.v == 0 and self.p is not None and otro.v:
            desplazamiento = otro.v.copy_abs().adjusted()
            posiciones.append(
                self.p - desplazamiento if dividir
                else self.p + desplazamiento
            )
        if not dividir and otro.v == 0 and otro.p is not None and self.v:
            posiciones.append(otro.p + self.v.copy_abs().adjusted())
        return Q(0, max(posiciones) if posiciones else 0)

    def __mul__(self, otro):
        return self.producto(otro)

    __rmul__ = __mul__

    def __truediv__(self, otro):
        return self.producto(otro, True)

    def __rtruediv__(self, otro):
        return Q.convertir(otro) / self

    def texto(self):
        if self.p is None:
            if self.v == self.v.to_integral_value():
                return format(self.v, "f").replace(".", ",") + " (exacto)"
            return format(self.v, ".12g").replace(".", ",")
        valor = self.v.quantize(
            D(1).scaleb(self.p), rounding=ROUND_HALF_UP
        )
        if valor == 0:
            return f"0; resolución de redondeo 1e{self.p:+d}"
        return format(valor, "E").replace(".", ",")


def analizar_numero(texto):
    texto = texto.strip().replace(",", ".")
    if texto.lower() == "volver":
        raise Volver()
    exacto = texto.endswith("!")
    if exacto:
        texto = texto[:-1]

    partes = texto.split(":")
    if len(partes) > 2 or (exacto and len(partes) == 2):
        raise ValueError("Formato numérico no válido.")

    valor = D(partes[0])
    if not valor.is_finite():
        raise ValueError("Introduzca un número finito.")
    if len(valor.as_tuple().digits) > 18:
        raise ValueError("Máximo: 18 cifras introducidas.")
    if not -60 <= valor.as_tuple().exponent <= 60:
        raise ValueError("Exponente fuera del intervalo admitido.")

    p = None if exacto else valor.as_tuple().exponent
    if len(partes) == 2:
        n = int(partes[1])
        if not 1 <= n <= 18 or not valor:
            raise ValueError("Indique de 1 a 18 cifras para un valor no nulo.")
        p = valor.copy_abs().adjusted() - n + 1
    return Q(valor, p)


def leer(etiqueta, minimo=None, maximo=None, positivo=False):
    while True:
        try:
            q = analizar_numero(input(etiqueta + ": "))
            if positivo and q.v <= 0:
                raise ValueError("El valor debe ser mayor que cero.")
            if minimo is not None and q.v < D(str(minimo)):
                raise ValueError(f"El valor mínimo es {minimo}.")
            if maximo is not None and q.v > D(str(maximo)):
                raise ValueError(f"El valor máximo es {maximo}.")
            return q
        except Volver:
            raise
        except (ValueError, ArithmeticError) as error:
            print("Dato no válido:", error)


def entero(etiqueta, minimo=1, maximo=30):
    while True:
        s = input(etiqueta + ": ").strip()
        if s.lower() == "volver":
            raise Volver()
        try:
            n = int(s)
            if minimo <= n <= maximo:
                return n
        except ValueError:
            pass
        print(f"Introduzca un entero entre {minimo} y {maximo}.")


def elegir(etiqueta, opciones):
    while True:
        print("\n" + etiqueta)
        for clave, descripcion in opciones.items():
            print(f"  {clave}. {descripcion}")
        respuesta = input("> ").strip().lower()
        if respuesta == "volver":
            raise Volver()
        if respuesta in opciones:
            return respuesta
        print("Opción no válida.")


def mostrar(etiqueta, valor, unidad=""):
    print(f"{etiqueta}: {valor.texto()} {unidad}".rstrip())


def porcentaje(etiqueta, valor):
    mostrar(etiqueta, valor * 100, "%")


def no_supera(a, b, mensaje):
    """Tolera únicamente una discrepancia compatible con el redondeo."""
    if a.v <= b.v:
        return
    tolerancia = (a.paso() + b.paso()) / 2
    if a.v - b.v <= tolerancia:
        print("Aviso: discrepancia compatible con el redondeo:", mensaje)
    else:
        raise ValueError(mensaje)


def masa_molar(nombre):
    return leer(f"Masa molar de {nombre} [g/mol]", positivo=True)


def cantidad(nombre):
    modo = elegir(
        f"Datos de {nombre}",
        {"1": "Cantidad de sustancia [mol]", "2": "Masa [g]"}
    )
    if modo == "1":
        return leer(f"Cantidad de {nombre} [mol]", minimo=0)
    m = leer(f"Masa de {nombre} [g]", minimo=0)
    return m / masa_molar(nombre)


def ejecutar(titulo, ayuda, acciones, pruebas):
    parser = argparse.ArgumentParser(
        description=titulo + "\n\n" + ayuda + "\n" + AYUDA_NUMEROS,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--autoprueba", action="store_true",
        help="Ejecuta las comprobaciones internas y termina."
    )
    args = parser.parse_args()
    if args.autoprueba:
        pruebas()
        print("Comprobaciones internas superadas.")
        return

    opciones = {
        str(i): nombre for i, (nombre, _) in enumerate(acciones, 1)
    }
    opciones.update({"h": "Ayuda", "0": "Salir"})

    while True:
        try:
            op = elegir(titulo, opciones)
            if op == "0":
                return
            if op == "h":
                print(ayuda + "\n" + AYUDA_NUMEROS)
            else:
                acciones[int(op) - 1][1]()
        except Volver:
            pass
        except (ValueError, ArithmeticError) as error:
            print("No se puede completar el cálculo:", error)
        except (EOFError, KeyboardInterrupt):
            print("\nPrograma terminado.")
            return

from fractions import Fraction
from functools import reduce
from math import gcd, lcm

ELEMENTOS = set("""
H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe
Co Ni Cu Zn Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In
Sn Sb Te I Xe Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu
Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn Fr Ra Ac Th Pa U Np Pu
Am Cm Bk Cf Es Fm Md No Lr Rf Db Sg Bh Hs Mt Ds Rg Cn Nh Fl Mc Lv Ts Og
""".split())

AYUDA_FORMULAS = """
FÓRMULAS Y AJUSTE
- Introduzca las especies de cada lado separadas por punto y coma:
  Ca(OH)2; HCl
- No anteponga coeficientes a las fórmulas.
- Se admiten paréntesis, corchetes y grupos anidados.
- Hidratos: CuSO4·5H2O; utilice el punto central ·.
- Cargas: Fe^3+, SO4^2-, H^+, OH^-; electrón: e^-.
- Se admiten los sufijos (s), (l), (g), (aq) y (ac).
- Los subíndices deben escribirse con dígitos normales.
- El ajuste conserva átomos y carga mediante aritmética racional exacta.
- No añade automáticamente agua, protones, hidróxido ni electrones:
  introduzca todas las especies que deban intervenir.
- Si hay varias soluciones independientes, el programa lo indica y permite
  introducir coeficientes para comprobar un ajuste concreto.
- Un ajuste algebraico no demuestra que la reacción sea químicamente viable.
"""


def composicion(formula):
    s = re.sub(r"\((?:s|l|g|aq|ac)\)$", "", formula.strip())
    s = s.replace(" ", "")
    if s == "e^-":
        return {}, -1

    carga = 0
    encontrado = re.search(r"\^(\d*)([+-])$", s)
    if encontrado:
        magnitud = int(encontrado.group(1) or "1")
        if magnitud <= 0:
            raise ValueError("La magnitud de la carga debe ser positiva.")
        carga = magnitud * (1 if encontrado.group(2) == "+" else -1)
        s = s[:encontrado.start()]

    total = {}
    partes = s.split("·")
    if any(not parte for parte in partes):
        raise ValueError("Fórmula o hidrato incompleto.")

    for numero, parte in enumerate(partes):
        factor = 1
        if numero:
            inicio = re.match(r"(\d+)", parte)
            if inicio:
                factor = int(inicio.group())
                parte = parte[inicio.end():]
            if factor <= 0:
                raise ValueError("Factor de hidratación no válido.")

        tokens = re.findall(r"[A-Z][a-z]?|\d+|[()\[\]]", parte)
        if "".join(tokens) != parte:
            raise ValueError(f"Notación no admitida: {formula}")
        pos = 0

        def grupo(cierre=None):
            nonlocal pos
            atoms = {}
            hubo = False
            while pos < len(tokens):
                t = tokens[pos]
                if t in (")", "]"):
                    if t != cierre:
                        raise ValueError("Paréntesis o corchetes incompatibles.")
                    if not hubo:
                        raise ValueError("Grupo vacío.")
                    pos += 1
                    return atoms
                if t in ("(", "["):
                    pos += 1
                    pieza = grupo(")" if t == "(" else "]")
                elif t in ELEMENTOS:
                    pieza = {t: 1}
                    pos += 1
                else:
                    raise ValueError(f"Elemento o posición no válida: {t}")

                multiplicador = 1
                if pos < len(tokens) and tokens[pos].isdigit():
                    multiplicador = int(tokens[pos])
                    pos += 1
                    if multiplicador <= 0:
                        raise ValueError("Un subíndice debe ser positivo.")

                for elemento, cantidad_ in pieza.items():
                    atoms[elemento] = (
                        atoms.get(elemento, 0) + cantidad_ * multiplicador
                    )
                hubo = True

            if cierre is not None:
                raise ValueError("Falta cerrar un grupo.")
            if not hubo:
                raise ValueError("Fórmula vacía.")
            return atoms

        atoms = grupo()
        for elemento, n in atoms.items():
            total[elemento] = total.get(elemento, 0) + factor * n

    return total, carga


def matriz_reaccion(reactivos, productos):
    especies = reactivos + productos
    datos = [composicion(s) for s in especies]
    elementos = sorted(set().union(*(set(a) for a, _ in datos)))
    signos = [1] * len(reactivos) + [-1] * len(productos)
    filas = [
        [Fraction(signos[j] * datos[j][0].get(e, 0))
         for j in range(len(especies))]
        for e in elementos
    ]
    etiquetas = elementos[:]
    if any(carga for _, carga in datos):
        filas.append([
            Fraction(signos[j] * datos[j][1])
            for j in range(len(especies))
        ])
        etiquetas.append("carga")
    return etiquetas, filas


def nucleo(matriz):
    if not matriz:
        raise ValueError("No existen balances que resolver.")
    a = [fila[:] for fila in matriz]
    m, n = len(a), len(a[0])
    pivotes = []
    fila = 0

    for col in range(n):
        k = next((k for k in range(fila, m) if a[k][col]), None)
        if k is None:
            continue
        a[fila], a[k] = a[k], a[fila]
        pivote = a[fila][col]
        a[fila] = [v / pivote for v in a[fila]]
        for k in range(m):
            if k != fila and a[k][col]:
                factor = a[k][col]
                a[k] = [
                    a[k][j] - factor * a[fila][j] for j in range(n)
                ]
        pivotes.append(col)
        fila += 1
        if fila == m:
            break

    libres = [j for j in range(n) if j not in pivotes]
    base = []
    for libre in libres:
        v = [Fraction(0)] * n
        v[libre] = Fraction(1)
        for i, pivote in enumerate(pivotes):
            v[pivote] = -a[i][libre]
        base.append(v)
    return base, a


def enteros_minimos(vector):
    denominador = lcm(*(x.denominator for x in vector))
    valores = [int(x * denominador) for x in vector]
    if all(x < 0 for x in valores):
        valores = [-x for x in valores]
    if not all(x > 0 for x in valores):
        raise ValueError(
            "No hay un ajuste con todas las especies presentes y "
            "coeficientes positivos en los lados indicados."
        )
    divisor = reduce(gcd, valores)
    return [x // divisor for x in valores]


def ajustar(reactivos, productos):
    _, matriz = matriz_reaccion(reactivos, productos)
    base, _ = nucleo(matriz)
    if not base:
        raise ValueError("Solo existe la solución nula: revise las especies.")
    if len(base) != 1:
        raise ValueError(
            f"Hay {len(base)} parámetros independientes. "
            "El ajuste no es único salvo un factor común."
        )
    return enteros_minimos(base[0])


def comprobar(reactivos, productos, coeficientes):
    _, a = matriz_reaccion(reactivos, productos)
    if len(coeficientes) != len(reactivos) + len(productos):
        raise ValueError("Número de coeficientes incorrecto.")
    return all(
        sum(x * y for x, y in zip(fila, coeficientes)) == 0
        for fila in a
    )


def especies_entrada():
    r = [s.strip() for s in input("Reactivos separados por ;: ").split(";")]
    p = [s.strip() for s in input("Productos separados por ;: ").split(";")]
    if not all(r + p) or len(r + p) > 30:
        raise ValueError("Introduzca entre 2 y 30 especies, sin huecos.")
    matriz_reaccion(r, p)
    return r, p


def coeficientes_entrada(r, p):
    valores = []
    for especie in r + p:
        s = input(f"Coeficiente exacto de {especie}: ").replace(",", ".")
        if s.strip().lower() == "volver":
            raise Volver()
        c = Fraction(s)
        if c <= 0:
            raise ValueError("Los coeficientes deben ser positivos.")
        valores.append(c)
    if not comprobar(r, p, valores):
        raise ValueError("Los coeficientes no conservan átomos y carga.")
    return enteros_minimos(valores)


def escribir_reaccion(r, p, c):
    def lado(especies, valores):
        return " + ".join(
            ("" if k == 1 else str(k) + " ") + s
            for s, k in zip(especies, valores)
        )
    print(lado(r, c[:len(r)]) + " -> " + lado(p, c[len(r):]))


def reaccion_entrada():
    print(AYUDA_FORMULAS)
    r, p = especies_entrada()
    modo = elegir(
        "Coeficientes",
        {"1": "Ajuste automático", "2": "Introducir y comprobar"}
    )
    c = ajustar(r, p) if modo == "1" else coeficientes_entrada(r, p)
    escribir_reaccion(r, p, c)
    return r, p, c

AYUDA = """
HIPÓTESIS
Una sola reacción, con coeficientes comprobados. Las impurezas son inertes.
El máximo estequiométrico supone consumo completo del reactivo limitante
por esa reacción. No calcula equilibrio ni reacciones secundarias.

ENTRADAS
Cada reactivo puede introducirse en mol o mediante masa y pureza másica.
Se solicitan las masas molares necesarias, en g/mol.

SALIDAS
Reactivo limitante, posibles colimitantes, excesos, cantidades consumidas,
reactivos sobrantes y formación máxima de cada producto.
Puede calcular una composición a conversión parcial del reactivo limitante.

El producto calculado es producto formado, sin sumar una carga inicial.
La masa sobrante de reactivo puro se distingue de las impurezas inertes.
""" + AYUDA_FORMULAS


def balance(n, a, b, fraccion=Q(1)):
    capacidades = [ni / ai for ni, ai in zip(n, a)]
    k = min(range(len(n)), key=lambda i: capacidades[i].v)
    maximo = capacidades[k]
    avance = maximo * fraccion
    limites = [
        i for i, capacidad in enumerate(capacidades)
        if capacidad.v == maximo.v
    ]
    restos = []
    for i, (ni, ai) in enumerate(zip(n, a)):
        if fraccion.v == 1 and i in limites:
            restos.append(Q(0))
        else:
            restos.append(ni - avance * ai)
    productos = [avance * bi for bi in b]
    return capacidades, limites, maximo, avance, restos, productos


def calcular(parcial=False):
    r, p, coef = reaccion_entrada()
    a, b = coef[:len(r)], coef[len(r):]
    n, masas_molares, inertes = [], [], []

    for nombre in r:
        modo = elegir(
            f"Alimentación de {nombre}",
            {"1": "mol de reactivo puro", "2": "Masa y pureza másica"}
        )
        M = masa_molar(nombre)
        masas_molares.append(M)
        if modo == "1":
            n.append(leer("Cantidad [mol]", minimo=0))
            inertes.append(Q(0))
        else:
            unidad = elegir("Unidad de masa", {"1": "g", "2": "kg"})
            masa = leer("Masa de muestra", minimo=0)
            if unidad == "2":
                masa = masa * 1000
            print("Para sustancia pura idealizada puede escribir 100!.")
            pureza = leer("Pureza [% m/m]", minimo=0, maximo=100) / 100
            n.append(masa * pureza / M)
            inertes.append(masa * (1 - pureza))

    Mproductos = [masa_molar(nombre) for nombre in p]
    fraccion = (
        leer("Conversión del limitante [%]", minimo=0, maximo=100) / 100
        if parcial else Q(1)
    )
    capacidades, limites, xmax, xi, restos, formados = balance(
        n, a, b, fraccion
    )

    print("\nComparación n inicial / coeficiente:")
    for nombre, capacidad in zip(r, capacidades):
        mostrar(nombre, capacidad, "mol")
    print("Limitante(s), según los valores centrales:",
          ", ".join(r[i] for i in limites))

    referencia = capacidades[limites[0]]
    for i, capacidad in enumerate(capacidades):
        if i not in limites:
            margen = (capacidad.paso() + referencia.paso()) / 2
            if capacidad.v - referencia.v <= margen:
                print(
                    "Aviso: la precisión introducida no permite distinguir "
                    f"con seguridad {r[i]} del limitante."
                )

    mostrar("Avance máximo estequiométrico", xmax, "mol")
    mostrar("Avance utilizado", xi, "mol")

    for i, nombre in enumerate(r):
        print("\nReactivo:", nombre)
        consumido = xi * a[i]
        mostrar("Cantidad consumida", consumido, "mol")
        mostrar("Masa consumida", consumido * masas_molares[i], "g")
        mostrar("Cantidad sobrante de reactivo puro", restos[i], "mol")
        mostrar(
            "Masa sobrante de reactivo puro",
            restos[i] * masas_molares[i], "g"
        )
        mostrar("Impurezas inertes de la muestra", inertes[i], "g")
        if xmax.v:
            necesario = xmax * a[i]
            porcentaje(
                "Exceso alimentado respecto al máximo estequiométrico",
                (n[i] - necesario) / necesario
            )
        else:
            print("Porcentaje de exceso indefinido: base necesaria nula.")

    for nombre, bi, formado, M in zip(p, b, formados, Mproductos):
        print("\nProducto:", nombre)
        mostrar("Formación máxima", xmax * bi, "mol")
        mostrar("Masa máxima", xmax * bi * M, "g")
        if parcial:
            mostrar("Formación a la conversión indicada", formado, "mol")
            mostrar("Masa a la conversión indicada", formado * M, "g")


def autoprueba():
    datos = balance([Q(3), Q(1)], [2, 1], [2])
    assert datos[1] == [1]
    assert datos[2].v == 1
    assert [x.v for x in datos[4]] == [1, 0]
    assert datos[5][0].v == 2
    datos = balance([Q(2), Q(1)], [2, 1], [2], Q("0.5"))
    assert datos[1] == [0, 1]
    assert [x.v for x in datos[4]] == [1, D("0.5")]
    assert datos[5][0].v == 1


if __name__ == "__main__":
    ejecutar(
        "Reactivo limitante y balance estequiométrico", AYUDA,
        [
            ("Máximo estequiométrico y reactivos sobrantes", calcular),
            ("Balance con conversión parcial", lambda: calcular(True)),
        ],
        autoprueba
    )
