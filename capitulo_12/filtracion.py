#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SCRIPT 12.5. FILTRACIÓN DE UNA SUSPENSIÓN

Funcionalidad:
    Calcula la masa de torta y filtrado y la distribución del sólido
    entre ambas corrientes.

Para qué sirve:
    Para problemas en los que se conocen:
        - masa o caudal de alimentación;
        - porcentaje de sólido en la alimentación;
        - recuperación del sólido en la torta;
        - porcentaje de sólido en la torta.

Cifras significativas:
    Los resultados se redondean automáticamente según los datos introducidos.

Uso:
    python 12_5_filtracion.py
    python 12_5_filtracion.py -h
"""

import argparse


from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import re


@dataclass(frozen=True)
class Medida:
    """Valor numérico acompañado de su precisión experimental."""
    valor: Decimal
    cifras: int | None
    exponente_ultima_cifra: int | None
    exacto: bool = False


def exacto(valor) -> Medida:
    """Crea una constante exacta, que no limita la precisión del resultado."""
    return Medida(Decimal(str(valor)), None, None, True)


def _redondear_posicion(valor: Decimal, exp: int) -> Decimal:
    """Redondea al orden 10**exp usando ROUND_HALF_UP."""
    if valor == 0:
        return Decimal(0).quantize(Decimal(f"1e{exp}"))
    return valor.quantize(Decimal(f"1e{exp}"), rounding=ROUND_HALF_UP)


def _desde_cifras(valor: Decimal, cifras: int) -> Medida:
    """Asigna precisión por cifras significativas sin redondear el valor interno."""
    if cifras < 1:
        cifras = 1
    if valor == 0:
        exp = -(cifras - 1)
        return Medida(valor, cifras, exp, False)
    exp = valor.copy_abs().adjusted() - cifras + 1
    # El valor interno conserva dígitos de guarda; solo se redondea al mostrarlo.
    return Medida(valor, cifras, exp, False)


def _desde_posicion(valor: Decimal, exp: int) -> Medida:
    """Asigna precisión decimal sin redondear el valor interno."""
    red = _redondear_posicion(valor, exp)
    if red == 0:
        cifras = max(1, -exp)
    else:
        cifras = max(1, red.copy_abs().adjusted() - exp + 1)
    return Medida(valor, cifras, exp, False)


def leer_medida(texto: str) -> Medida:
    """
    Interpreta un número escrito por el usuario y deduce su precisión.

    Reglas:
    - Se acepta coma o punto decimal.
    - Todos los dígitos escritos, salvo los ceros iniciales, se consideran
      significativos. Por tanto, 1000 se interpreta con 4 cifras significativas.
    - La notación científica permite indicar otra precisión: 1e3 tiene 1 cifra
      significativa y 1,00e3 tiene 3.
    """
    s = texto.strip().replace(",", ".")
    if not re.fullmatch(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", s):
        raise ValueError("formato numérico no válido")

    try:
        valor = Decimal(s)
    except InvalidOperation as exc:
        raise ValueError("formato numérico no válido") from exc

    sin_signo = s.lstrip("+-")
    if "e" in sin_signo.lower():
        mantisa, exp_txt = re.split("[eE]", sin_signo)
        exp10 = int(exp_txt)
    else:
        mantisa, exp10 = sin_signo, 0

    if "." in mantisa:
        parte_entera, parte_decimal = mantisa.split(".", 1)
    else:
        parte_entera, parte_decimal = mantisa, ""

    digitos = parte_entera + parte_decimal
    no_ceros_iniciales = digitos.lstrip("0")

    if no_ceros_iniciales:
        cifras = len(no_ceros_iniciales)
    else:
        # Para cero, la posición decimal sigue expresando precisión.
        cifras = max(1, len(parte_decimal))

    exp_ultima = exp10 - len(parte_decimal)

    # En notación sin decimal, todos los dígitos introducidos cuentan como
    # significativos; la última cifra está en unidades.
    if "." not in mantisa and "e" not in sin_signo.lower():
        exp_ultima = 0

    return Medida(valor, cifras, exp_ultima, False)


def pedir_medida(mensaje: str, minimo=None, maximo=None,
                 estricto_min=False, estricto_max=False) -> Medida:
    """Solicita una medida y valida un intervalo cuando se especifica."""
    while True:
        bruto = input(mensaje)
        try:
            dato = leer_medida(bruto)
        except ValueError:
            print("Entrada no válida. Use un número, por ejemplo 12,0 o 1,20e2.")
            continue

        v = dato.valor
        if minimo is not None:
            minimo_d = Decimal(str(minimo))
            if (estricto_min and v <= minimo_d) or (not estricto_min and v < minimo_d):
                print(f"El valor debe ser {'mayor que' if estricto_min else 'igual o mayor que'} {minimo}.")
                continue
        if maximo is not None:
            maximo_d = Decimal(str(maximo))
            if (estricto_max and v >= maximo_d) or (not estricto_max and v > maximo_d):
                print(f"El valor debe ser {'menor que' if estricto_max else 'igual o menor que'} {maximo}.")
                continue
        return dato


def pedir_porcentaje(mensaje: str, permitir_cero=True, permitir_cien=True) -> Medida:
    """Solicita un porcentaje y lo convierte a fracción sin perder sus cifras significativas."""
    p = pedir_medida(
        mensaje,
        minimo=0,
        maximo=100,
        estricto_min=not permitir_cero,
        estricto_max=not permitir_cien
    )
    return dividir(p, exacto(100))


def pedir_entero_positivo(mensaje: str) -> int:
    """Solicita un número entero exacto mayor o igual que 1."""
    while True:
        bruto = input(mensaje).strip()
        try:
            n = int(bruto)
        except ValueError:
            print("Introduzca un número entero.")
            continue
        if n >= 1:
            return n
        print("El número debe ser igual o superior a 1.")


def _cifras_limitantes(*datos: Medida) -> int:
    medidos = [d.cifras for d in datos if not d.exacto and d.cifras is not None]
    return min(medidos) if medidos else 15


def sumar(a: Medida, b: Medida) -> Medida:
    """Suma: se conserva la posición decimal menos precisa."""
    valor = a.valor + b.valor
    posiciones = [
        d.exponente_ultima_cifra
        for d in (a, b)
        if not d.exacto and d.exponente_ultima_cifra is not None
    ]
    if not posiciones:
        return exacto(valor)
    return _desde_posicion(valor, max(posiciones))


def restar(a: Medida, b: Medida) -> Medida:
    """Resta: se conserva la posición decimal menos precisa."""
    valor = a.valor - b.valor
    posiciones = [
        d.exponente_ultima_cifra
        for d in (a, b)
        if not d.exacto and d.exponente_ultima_cifra is not None
    ]
    if not posiciones:
        return exacto(valor)
    return _desde_posicion(valor, max(posiciones))


def multiplicar(a: Medida, b: Medida) -> Medida:
    """Producto: se conserva el menor número de cifras significativas."""
    valor = a.valor * b.valor
    if a.exacto and b.exacto:
        return exacto(valor)
    return _desde_cifras(valor, _cifras_limitantes(a, b))


def dividir(a: Medida, b: Medida) -> Medida:
    """Cociente: se conserva el menor número de cifras significativas."""
    if b.valor == 0:
        raise ZeroDivisionError("división por cero")
    valor = a.valor / b.valor
    if a.exacto and b.exacto:
        return exacto(valor)
    return _desde_cifras(valor, _cifras_limitantes(a, b))


def potencia_entera(a: Medida, n: int) -> Medida:
    """Potencia con exponente entero exacto."""
    valor = a.valor ** n
    if a.exacto:
        return exacto(valor)
    return _desde_cifras(valor, a.cifras)


def porcentaje_de(a: Medida, b: Medida) -> Medida:
    """Calcula 100*a/b tratando 100 como constante exacta."""
    return multiplicar(dividir(a, b), exacto(100))


def _notacion_cientifica(dato: Medida) -> str:
    """Formatea en notación científica conservando las cifras significativas."""
    if dato.valor == 0:
        return "0"
    cifras = dato.cifras or 1
    exp = dato.valor.copy_abs().adjusted()
    mantisa = dato.valor / (Decimal(10) ** exp)
    decimales = max(0, cifras - 1)
    mantisa = mantisa.quantize(
        Decimal("1") if decimales == 0 else Decimal("1." + "0" * decimales),
        rounding=ROUND_HALF_UP
    )
    texto = f"{mantisa:.{decimales}f}".replace(".", ",")
    return f"{texto}e{exp:+d}"


def formato(dato: Medida) -> str:
    """
    Devuelve el valor con la precisión calculada.

    Cuando un entero terminado en cero sería ambiguo, usa notación científica
    para que las cifras significativas queden explícitas.
    """
    if dato.exacto:
        return str(dato.valor).replace(".", ",")

    exp = dato.exponente_ultima_cifra or 0
    valor = _redondear_posicion(dato.valor, exp)
    dato_mostrado = Medida(valor, dato.cifras, exp, False)

    if exp > 0:
        return _notacion_cientifica(dato_mostrado)

    decimales = max(0, -exp)
    texto = f"{valor:.{decimales}f}".replace(".", ",")

    # Evita que un entero como 500 con tres cifras significativas parezca tener
    # una sola cifra significativa.
    if decimales == 0 and valor != 0:
        entero = texto.lstrip("-")
        if entero.endswith("0") and (dato.cifras or 1) > len(entero.rstrip("0")):
            return _notacion_cientifica(dato_mostrado)

    return texto


def error_cierre(valor: Decimal, unidad="") -> str:
    """Formatea un error numérico de cierre; no es una magnitud experimental."""
    if abs(valor) < Decimal("1e-20"):
        valor = Decimal(0)
    sufijo = f" {unidad}" if unidad else ""
    return f"{valor:.3E}{sufijo}".replace(".", ",")


def main():
    parser = argparse.ArgumentParser(
        description="Balance de filtración con recuperación de sólido y composición de torta.",
        epilog="Los porcentajes se introducen como números, por ejemplo 95,0 para 95,0 %."
    )
    parser.parse_args()

    print("\nFILTRACIÓN DE UNA SUSPENSIÓN")
    print("-" * 29)

    m_f = pedir_medida("Masa o caudal de alimentación: ", minimo=0, estricto_min=True)
    w_sf = pedir_porcentaje(
        "Sólido en la alimentación [% masa]: ",
        permitir_cero=False
    )
    rec = pedir_porcentaje("Recuperación del sólido en la torta [%]: ")
    w_st = pedir_porcentaje(
        "Sólido en la torta [% masa]: ",
        permitir_cero=False
    )

    m_s_f = multiplicar(m_f, w_sf)
    m_s_t = multiplicar(rec, m_s_f)
    m_torta = dividir(m_s_t, w_st)
    m_filtrado = restar(m_f, m_torta)

    if m_filtrado.valor < 0:
        raise SystemExit(
            "Los datos implican una torta mayor que la alimentación. Revise los datos."
        )

    fraccion_no_recuperada = restar(exacto(1), rec)
    m_s_filtrado = multiplicar(m_s_f, fraccion_no_recuperada)
    w_s_filtrado = dividir(m_s_filtrado, m_filtrado) if m_filtrado.valor != 0 else exacto(0)
    pct_filtrado = multiplicar(w_s_filtrado, exacto(100))
    liquido_torta = multiplicar(m_torta, restar(exacto(1), w_st))

    print("\nRESULTADOS")
    print("-" * 10)
    print(f"Sólido alimentado:     {formato(m_s_f)}")
    print(f"Sólido en la torta:    {formato(m_s_t)}")
    print(f"Líquido en la torta:   {formato(liquido_torta)}")
    print(f"Masa de torta:         {formato(m_torta)}")
    print(f"Masa de filtrado:      {formato(m_filtrado)}")
    print(f"Sólido en el filtrado: {formato(m_s_filtrado)}")
    print(f"Sólido en el filtrado: {formato(pct_filtrado)} % masa")

    err_total = (m_torta.valor + m_filtrado.valor) - m_f.valor
    err_solido = (m_s_t.valor + m_s_filtrado.valor) - m_s_f.valor

    print("\nCOMPROBACIÓN")
    print("-" * 12)
    print(f"Error numérico balance total:  {error_cierre(err_total)}")
    print(f"Error numérico balance sólido: {error_cierre(err_solido)}")


if __name__ == "__main__":
    main()
