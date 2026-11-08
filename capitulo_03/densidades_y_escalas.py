#!/usr/bin/env python3
'Densidad, gravedad específica y escalas industriales.\nFinalidad: calcular densidad, Brix, Baumé, Twaddell y API.\nHipótesis: referencias térmicas compatibles; Brix densimétrico basado en sacarosa.\nEntradas: valores, referencias y correcciones documentadas cuando cambie la referencia térmica.\nSalidas: magnitud calculada y GE intermedia.\nRequisitos: Python 3.10+, biblioteca estándar.'

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

AYUDA = """
ESCALAS
GE = densidad de muestra / densidad del agua de referencia.
Baumé pesado: Be = 145 - 145/GE; GE >= 1.
Baumé ligero: Be = 140/GE - 130; 0 < GE <= 1.
Twaddell: Tw = 200*(GE - 1); GE >= 1.
API: API = 141.5/GE - 131.5.

TEMPERATURAS
Baumé con estas constantes y API utilizan GE a 60 F/60 F.
Para Twaddell, GE y densidad debe indicar la referencia utilizada.
La tabla de sacarosa utiliza densidad a 20 C y GE 20/20.

No se corrige automáticamente una temperatura desconocida.
Entre referencias diferentes se solicita un factor documentado:
    factor = GE en referencia de destino / GE en referencia de origen.
Sin ese dato no se realiza la conversión física entre referencias.

BRIX
Para sacarosa y agua, Brix = porcentaje másico de sacarosa.
Para GE <-> Brix se interpola una tabla de densidad a 20 C.
Intervalo incorporado: 0 a 60 Brix. No se extrapola.
La interpolación es aproximada; la precisión de presentación no constituye
una garantía de exactitud experimental.
La opción Hall utiliza GE = 1,00001 + 0,0038661 B + 1,3488e-5 B² + 4,3074e-8 B³
y restringe la aproximación Brix/Plato a 0-33 °Bx (libro, 3.B.20).
En mezclas distintas de sacarosa/agua solo se calcula un equivalente
densimétrico de sacarosa, que puede diferir del Brix refractométrico.

FUENTES
NIST, Calibration Services for Hydrometers:
https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=832342
EIA, API gravity:
https://www.eia.gov/tools/glossary/index.php?id=Api+gravity
Anton Paar, densidad de sacarosa a 20 C:
https://wiki.anton-paar.com/us-en/density-and-density-measurement/sucrose-density/

Las constantes de las escalas son convencionales; la tabla es calibración,
no datos fijos de un problema.
"""

# Densidades en g/cm3, cada 1 % m/m de sacarosa, desde 0 hasta 60 %.
RHO = [D(x) for x in """
0.99821 1.00209 1.00599 1.00991 1.01385 1.01783 1.02183
1.02586 1.02991 1.03400 1.03811 1.04226 1.04643 1.05064
1.05487 1.05914 1.06343 1.06776 1.07212 1.07651 1.08093
1.08538 1.08987 1.09439 1.09894 1.10353 1.10814 1.11280
1.11748 1.12220 1.12695 1.13174 1.13656 1.14142 1.14631
1.15124 1.15621 1.16120 1.16624 1.17131 1.17641 1.18156
1.18674 1.19196 1.19721 1.20251 1.20784 1.21320 1.21861
1.22405 1.22953 1.23505 1.24061 1.24620 1.25183 1.25750
1.26321 1.26895 1.27474 1.28056 1.28642
""".split()]

ESCALAS = {
    "1": "Gravedad específica / densidad relativa",
    "2": "Densidad [g/mL]",
    "3": "Baumé, líquidos pesados",
    "4": "Baumé, líquidos ligeros",
    "5": "Twaddell",
    "6": "Brix densimétrico",
    "7": "API",
}


def resolver_precision(valor, entrada, pendiente, limite):
    # Transforma la resolución escrita usando la pendiente local.
    # limite impone un tope de presentación para la interpolación.
    if entrada.p is None:
        return Q(valor, limite)
    paso = abs(pendiente) * entrada.paso()
    p = paso.adjusted() if paso else limite
    return Q(valor, max(p, limite))


def brix_a_ge(bx):
    if not 0 <= bx.v <= 60:
        raise ValueError("La tabla incorporada cubre de 0 a 60 Brix.")
    i = min(int(bx.v), 59)
    pendiente = RHO[i+1] - RHO[i]
    rho = RHO[i] + (bx.v - i) * pendiente
    return resolver_precision(
        rho / RHO[0], bx, pendiente / RHO[0], -4
    )



def brix_a_ge_hall(bx):
    """Ajuste cúbico de Hall del libro, ec. cap. 3 y ejercicio 3.B.20.

    Nota: Hall fue ajustado para grados Plato y 0-33 °P. El empleo con Brix
    es la aproximación didáctica que el propio libro explicita; no sustituye
    la conversión tabulada Brix-densidad del programa.
    """
    bx = Q.convertir(bx)
    if not bx.v.is_finite() or not D(0) <= bx.v <= D(33):
        raise ValueError("El ajuste de Hall se restringe a 0–33 °Bx (aproximación Brix/Plato).")
    b = bx.v
    ge = D("1.00001") + D("0.0038661")*b + D("0.000013488")*b*b + D("0.000000043074")*b*b*b
    derivada = D("0.0038661") + D("0.000026976")*b + D("0.000000129222")*b*b
    return resolver_precision(ge, bx, derivada, -5)


def calcular_brix_hall():
    print("Ajuste cúbico de Hall (aproximación Brix/Plato, 0-33 °Bx, referencia 20 °C).")
    bx = leer("Grados Brix", minimo=0, maximo=33)
    ge = brix_a_ge_hall(bx)
    mostrar("Gravedad específica por Hall", ge)
    rho_agua = leer("Densidad del agua de referencia [g/mL]", positivo=True)
    mostrar("Densidad estimada del jarabe", ge * rho_agua, "g/mL")
    print("Modelo empírico: no equivale a interpolar la tabla de sacarosa.")

def ge_a_brix(ge):
    rho = ge.v * RHO[0]
    if not RHO[0] <= rho <= RHO[-1]:
        raise ValueError("GE fuera de la tabla de 0 a 60 Brix.")
    i = next(
        (j for j in range(60) if RHO[j] <= rho <= RHO[j+1]), 59
    )
    pendiente = RHO[i+1] - RHO[i]
    bx = D(i) + (rho - RHO[i]) / pendiente
    return resolver_precision(
        bx, ge, RHO[0] / pendiente, -1
    )


def a_ge(escala, valor, agua=None):
    if escala == "1":
        ge = valor
    elif escala == "2":
        if agua is None or agua.v <= 0:
            raise ValueError("Falta la densidad del agua de referencia.")
        ge = valor / agua
    elif escala == "3":
        if not 0 <= valor.v < 145:
            raise ValueError("Baumé pesado debe cumplir 0 <= Be < 145.")
        ge = 145 / (145 - valor)
    elif escala == "4":
        if valor.v < 10:
            raise ValueError("Baumé ligero requiere Be >= 10.")
        ge = 140 / (valor + 130)
    elif escala == "5":
        if valor.v < 0:
            raise ValueError("Twaddell no puede ser negativo.")
        ge = 1 + valor / 200
    elif escala == "6":
        ge = brix_a_ge(valor)
    elif escala == "7":
        if valor.v <= D("-131.5"):
            raise ValueError("API debe ser mayor que -131,5.")
        ge = Q("141.5") / (valor + Q("131.5"))
    else:
        raise ValueError("Escala desconocida.")
    if ge.v <= 0:
        raise ValueError("La gravedad específica debe ser positiva.")
    return ge


def desde_ge(escala, ge, agua=None):
    if ge.v <= 0:
        raise ValueError("GE debe ser positiva.")
    if escala == "1":
        return ge
    if escala == "2":
        if agua is None or agua.v <= 0:
            raise ValueError("Falta la densidad del agua de referencia.")
        return ge * agua
    if escala == "3":
        if ge.v < 1:
            raise ValueError("Baumé pesado requiere GE >= 1.")
        return 145 - 145 / ge
    if escala == "4":
        if ge.v > 1:
            raise ValueError("Baumé ligero requiere GE <= 1.")
        return 140 / ge - 130
    if escala == "5":
        if ge.v < 1:
            raise ValueError("Twaddell requiere GE >= 1.")
        return 200 * (ge - 1)
    if escala == "6":
        return ge_a_brix(ge)
    if escala == "7":
        return Q("141.5") / ge - Q("131.5")
    raise ValueError("Escala desconocida.")


def referencia(escala):
    if escala in ("3", "4", "7"):
        print("Referencia: GE a 60 F/60 F.")
        return "60F/60F"
    if escala == "6":
        print("Referencia: GE a 20 C/20 C.")
        return "20C/20C"
    op = elegir(
        "Referencia de GE: temperatura de muestra / temperatura del agua",
        {"1": "20 C / 20 C", "2": "60 F / 60 F", "3": "Otra"}
    )
    if op == "1":
        return "20C/20C"
    if op == "2":
        return "60F/60F"
    t = input("Temperatura de la muestra [C]: ").strip().replace(",", ".")
    tw = input("Temperatura del agua de referencia [C]: ").strip().replace(",", ".")
    a, b = D(t), D(tw)
    if not a.is_finite() or not b.is_finite():
        raise ValueError("Temperaturas no válidas.")
    return f"{a.normalize()}C/{b.normalize()}C"


def agua_para(escala):
    if escala != "2":
        return None
    return leer(
        "Densidad del agua a la temperatura de referencia [g/mL]",
        positivo=True
    )


def convertir():
    origen = elegir("Magnitud de origen", ESCALAS)
    ref_origen = referencia(origen)
    agua_origen = agua_para(origen)
    valor = leer("Valor de origen")
    ge = a_ge(origen, valor, agua_origen)
    mostrar("GE de origen", ge)
    print("Referencia de origen:", ref_origen)

    destino = elegir("Magnitud de destino", ESCALAS)
    ref_destino = referencia(destino)
    agua_destino = agua_para(destino)

    if ref_origen != ref_destino:
        print(
            "Las referencias son diferentes. Se necesita un factor "
            "obtenido de datos de densidad o de una correlación válida "
            "para esta misma muestra."
        )
        print("Si no dispone de él, escriba volver.")
        factor = leer(
            "Factor GE_destino / GE_origen", positivo=True
        )
        ge = ge * factor
        mostrar("GE a la referencia de destino", ge)

    if "6" in (origen, destino):
        print(
            "Resultado basado en la tabla de sacarosa a 20 C. "
            "En otras mezclas representa un equivalente densimétrico."
        )
    resultado = desde_ge(destino, ge, agua_destino)
    mostrar(ESCALAS[destino], resultado)
    print("Referencia de destino:", ref_destino)


def densidad():
    unidad = elegir("Unidades de entrada", {
        "1": "Masa en g y volumen en mL",
        "2": "Masa en kg y volumen en L"
    })
    m = leer("Masa", minimo=0)
    v = leer("Volumen", positivo=True)
    rho = m / v
    # kg/L y g/mL tienen el mismo valor numérico.
    mostrar("Densidad", rho, "g/mL")
    mostrar("Densidad", rho * 1000, "kg/m3")


def brix_masas():
    op = elegir(
        "Cálculo de Brix por composición, para sacarosa y agua",
        {
            "1": "Brix a partir de masas",
            "2": "Masas de sacarosa y agua a partir de Brix",
        }
    )
    if op == "1":
        sacarosa = leer("Masa de sacarosa [g]", minimo=0)
        agua = leer("Masa de agua [g]", minimo=0)
        total = sacarosa + agua
        if total.v == 0:
            raise ValueError("La masa total debe ser positiva.")
        mostrar("Grados Brix por composición", sacarosa / total * 100, "°Bx")
    else:
        bx = leer("Grados Brix", minimo=0, maximo=100)
        total = leer("Masa total [g]", positivo=True)
        mostrar("Masa de sacarosa", total * bx / 100, "g")
        mostrar("Masa de agua", total * (1 - bx / 100), "g")
    print(
        "El balance de masas no comprueba solubilidad ni garantiza "
        "que toda la sacarosa forme una única fase líquida."
    )


def autoprueba():
    assert len(RHO) == 61
    assert abs(brix_a_ge_hall(Q(18)).v - D("1.074221119568")) < D("1e-10")
    assert desde_ge("3", Q("1.25")).v == 29
    assert desde_ge("5", Q("1.25")).v == 50
    assert a_ge("5", Q(100)).v == D("1.5")
    assert desde_ge("7", Q(1)).v == 10
    assert a_ge("4", Q(10)).v == 1
    for bx in ("0", "10", "20.5", "40", "60"):
        vuelta = ge_a_brix(brix_a_ge(Q(bx))).v
        assert abs(vuelta - D(bx)) < D("1e-60")


if __name__ == "__main__":
    ejecutar(
        "Densidad, gravedad específica y escalas", AYUDA,
        [
            ("Calcular o convertir escalas pasando por GE", convertir),
            ("Calcular densidad mediante masa y volumen", densidad),
            ("Calcular Brix o masas de sacarosa y agua", brix_masas),
            ("Calcular GE por el ajuste cúbico de Hall (3.B.20)", calcular_brix_hall),
        ],
        autoprueba
    )
