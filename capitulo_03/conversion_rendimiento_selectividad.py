#!/usr/bin/env python3
'Conversión, rendimiento y selectividad.\nFinalidad: distinguir las bases de cálculo de cada magnitud.\nHipótesis: en el análisis por rutas, reacciones paralelas con productos indicadores exclusivos.\nEntradas: cantidades iniciales/finales, coeficientes o rendimientos parciales.\nSalidas: conversión, rendimientos y selectividades identificadas.\nRequisitos: Python 3.10+, biblioteca estándar.'

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
DEFINICIONES
X = (nA0 - nA) / nA0.

Para una ruta a A -> p P:
A destinado a P = (a/p) * (nP - nP0).
Y_global = A destinado a P / nA0.
Y_consumido = A destinado a P / (nA0 - nA).
Y_global = X * Y_consumido.

Selectividades que se muestran por separado:
- Molar P/Q: producto P formado / producto Q formado.
- Entre rutas: A destinado a P / A destinado a Q.
No se confunden ambas cuando las estequiometrías son distintas.

Rendimiento experimental:
producto obtenido / producto teórico, con la misma base y unidad.

Varias etapas:
producto de los rendimientos fraccionarios de las etapas consecutivas.

HIPÓTESIS DEL ANÁLISIS POR RUTAS
Las rutas son paralelas y consumen el mismo reactivo clave.
Cada producto indicador identifica exclusivamente una ruta.
No hay consumo posterior de esos productos.
Si existen reacciones consecutivas, hace falta otro modelo de balance.

Los denominadores nulos producen resultados indefinidos, no ceros ficticios.
"""


def fraccion_conversion(n0, nf):
    if n0.v <= 0 or nf.v < 0:
        raise ValueError("Cantidades inicial/final no válidas.")
    no_supera(nf, n0, "La cantidad final de A supera la inicial.")
    return (n0 - nf) / n0


def conversion():
    n0 = cantidad("reactivo inicial")
    nf = cantidad("reactivo final")
    porcentaje("Conversión", fraccion_conversion(n0, nf))


def rendimiento():
    print("Introduzca ambas cantidades en la misma unidad y base.")
    real = leer("Producto obtenido", minimo=0)
    teorico = leer("Producto teórico", positivo=True)
    no_supera(
        real, teorico,
        "El producto obtenido supera el teórico: revise pureza, "
        "humedad, unidad o base de cálculo."
    )
    porcentaje("Rendimiento experimental", real / teorico)


def cociente(etiqueta, numerador, denominador, en_porcentaje=False):
    if denominador.v == 0:
        if numerador.v > 0:
            print(etiqueta + ": sin valor finito; denominador nulo.")
        else:
            print(etiqueta + ": indefinido (0/0).")
    elif en_porcentaje:
        porcentaje(etiqueta, numerador / denominador)
    else:
        mostrar(etiqueta, numerador / denominador)


def rutas():
    n0 = cantidad("A inicial")
    nf = cantidad("A final")
    X = fraccion_conversion(n0, nf)
    consumido = n0 - nf
    numero = entero("Número de rutas que va a caracterizar", 1, 20)
    nombres, formados, destinados = [], [], []

    for i in range(numero):
        nombre = input(f"Nombre del producto indicador de la ruta {i+1}: ")
        nombres.append(nombre or f"Producto {i+1}")
        a = entero("Coeficiente de A en esa ruta", 1, 10000)
        p = entero("Coeficiente del producto indicador", 1, 10000)
        inicial = cantidad(f"{nombres[-1]} inicial")
        final = cantidad(f"{nombres[-1]} final")
        no_supera(
            inicial, final,
            "El producto indicador presenta consumo neto: "
            "el modelo de rutas paralelas no es aplicable."
        )
        delta = final - inicial
        if delta.v < 0:
            raise ValueError(
                "El incremento nominal del producto es negativo; "
                "revise los datos antes de calcular la selectividad."
            )
        formados.append(delta)
        destinados.append(delta * a / p)

    total = sum(destinados, Q(0))
    no_supera(
        total, consumido,
        "Los productos requieren más A que el consumido: "
        "revise coeficientes o la identificación de las rutas."
    )
    porcentaje("Conversión total de A", X)
    mostrar("A consumido", consumido, "mol")

    for nombre, delta, destino in zip(nombres, formados, destinados):
        print("\nProducto:", nombre)
        mostrar("Cantidad neta formada", delta, "mol")
        mostrar("A destinado a esta ruta", destino, "mol")
        porcentaje("Conversión parcial / rendimiento global", destino / n0)
        cociente(
            "Rendimiento respecto a A consumido",
            destino, consumido, True
        )

    restante = consumido - total
    mostrar("A consumido no asignado a las rutas introducidas", restante, "mol")
    if restante.v > (restante.paso() / 2):
        print(
            "El balance de las rutas introducidas no está cerrado. "
            "Puede haber rutas no caracterizadas o datos incompatibles."
        )

    if numero > 1:
        i = entero("Número del producto deseado", 1, numero) - 1
        j = entero("Número del subproducto de comparación", 1, numero) - 1
        if i == j:
            raise ValueError("Seleccione dos productos distintos.")
        cociente(
            f"Selectividad molar {nombres[i]}/{nombres[j]}",
            formados[i], formados[j]
        )
        cociente(
            "Selectividad entre rutas, sobre A consumido en cada una",
            destinados[i], destinados[j]
        )


def etapas():
    numero = entero("Número de etapas consecutivas", 1, 100)
    global_ = Q(1)
    for i in range(numero):
        y = leer(
            f"Rendimiento de la etapa {i+1} [%]", minimo=0, maximo=100
        ) / 100
        global_ = global_ * y
    porcentaje("Rendimiento global de la secuencia", global_)


def relacion():
    op = elegir(
        "Magnitud desconocida",
        {"1": "Rendimiento global",
         "2": "Conversión",
         "3": "Rendimiento respecto al reactivo consumido"}
    )
    if op == "1":
        x = leer("Conversión [%]", minimo=0, maximo=100) / 100
        y = leer("Rendimiento sobre consumido [%]", minimo=0, maximo=100) / 100
        porcentaje("Rendimiento global", x * y)
    else:
        yg = leer("Rendimiento global [%]", minimo=0, maximo=100) / 100
        etiqueta = "Rendimiento sobre consumido" if op == "2" else "Conversión"
        conocido = leer(etiqueta + " [%]", minimo=0, maximo=100) / 100
        if conocido.v == 0:
            raise ValueError(
                "Con denominador cero no se puede determinar "
                "la magnitud solicitada."
            )
        resultado = yg / conocido
        no_supera(resultado, Q(1), "El resultado supera el 100 %.")
        porcentaje(
            "Conversión" if op == "2" else "Rendimiento sobre consumido",
            resultado
        )


def autoprueba():
    assert fraccion_conversion(Q(100), Q(20)).v == D("0.8")
    assert (Q(60) / Q(100)).v == D("0.6")
    assert (Q(60) / Q(80)).v == D("0.75")
    assert (Q(60) / Q(20)).v == 3
    assert (Q("0.9") * Q("0.8") * Q("0.75")).v == D("0.54")
    # Dos rutas con distinta producción molar por mol de A.
    assert ((Q("0.70") / 1) / (Q("0.20") / 2)).v == 7
    assert (Q("0.70") / Q("0.20")).v == D("3.5")
    assert (analizar_numero("12,30") - analizar_numero("12,20")).p == -2


if __name__ == "__main__":
    ejecutar(
        "Conversión, rendimiento y selectividad", AYUDA,
        [
            ("Conversión de un reactivo", conversion),
            ("Rendimiento experimental", rendimiento),
            ("Reacción simple o análisis de rutas paralelas", rutas),
            ("Rendimiento global de varias etapas", etapas),
            ("Relación entre conversión y rendimientos", relacion),
        ],
        autoprueba
    )
