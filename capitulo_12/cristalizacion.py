#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SCRIPT 12.4. CRISTALIZACIÓN POR ENFRIAMIENTO

Funcionalidad:
    Calcula la masa de cristales y de licor madre obtenidos al enfriar
    una disolución inicialmente saturada.

Para qué sirve:
    Para problemas en los que las solubilidades se expresan como:
        kg de soluto / 100 kg de disolvente

    Hipótesis:
        - no se evapora disolvente;
        - los cristales son soluto puro;
        - la disolución inicial está saturada;
        - el licor madre queda saturado a la temperatura final.

Cifras significativas:
    Los resultados se redondean según la precisión de los datos introducidos.

Uso:
    python 12_4_cristalizacion.py
    python 12_4_cristalizacion.py -h
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
        description="Cristalización por enfriamiento a partir de datos de solubilidad.",
        epilog=(
            "Introduzca las solubilidades en kg de soluto por 100 kg de disolvente."
        )
    )
    parser.parse_args()

    print("\nCRISTALIZACIÓN POR ENFRIAMIENTO")
    print("-" * 32)
    print("Solubilidades: kg de soluto / 100 kg de disolvente\n")

    m_si = pedir_medida("Masa inicial de soluto [kg]: ", minimo=0, estricto_min=True)
    s_i = pedir_medida(
        "Solubilidad inicial [kg/100 kg disolvente]: ",
        minimo=0,
        estricto_min=True
    )
    s_f = pedir_medida(
        "Solubilidad final [kg/100 kg disolvente]: ",
        minimo=0
    )

    if s_f.valor >= s_i.valor:
        raise SystemExit(
            "La solubilidad final debe ser menor que la inicial para que cristalice soluto."
        )

    m_disolvente = dividir(multiplicar(exacto(100), m_si), s_i)
    m_s_disuelto = dividir(multiplicar(s_f, m_disolvente), exacto(100))
    fraccion_disuelta = dividir(s_f, s_i)
    fraccion_cristalizada = restar(exacto(1), fraccion_disuelta)
    m_cristales = multiplicar(m_si, fraccion_cristalizada)
    m_licor = sumar(m_disolvente, m_s_disuelto)
    rendimiento = porcentaje_de(m_cristales, m_si)

    print("\nRESULTADOS")
    print("-" * 10)
    print(f"Disolvente inicial:       {formato(m_disolvente)} kg")
    print(f"Soluto en el licor madre: {formato(m_s_disuelto)} kg")
    print(f"Cristales obtenidos:      {formato(m_cristales)} kg")
    print(f"Licor madre:              {formato(m_licor)} kg")
    print(f"Soluto cristalizado:      {formato(rendimiento)} %")

    err = (m_cristales.valor + m_licor.valor) - (m_si.valor + m_disolvente.valor)
    print("\nCOMPROBACIÓN")
    print("-" * 12)
    print(f"Error numérico de cierre: {error_cierre(err, 'kg')}")


if __name__ == "__main__":
    main()
