#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Capítulo 10. Propiedades coligativas: menú, cálculos, gráficos y pruebas.

Python >= 3.10. Matplotlib solo para gráficos. Sin dependencias numéricas.
Las cifras significativas se aplican AL FINAL de los cálculos.
Los modelos ideales no representan automáticamente valores experimentales.
"""
from __future__ import annotations

import argparse
import csv
import math
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Callable

R_BAR_L = 0.0831446261815324  # L bar mol^-1 K^-1, CODATA aproximado
R_J = 8.31446261815324       # J mol^-1 K^-1
M_STD = 1.0                   # mol kg^-1, valor convencional exacto


class DatosInvalidos(ValueError):
    """Entrada no física, ambigua o insuficiente."""


@dataclass(frozen=True)
class Medida:
    valor: float
    cifras: int
    literal: str


def sig_figs(txt: str) -> int:
    """Cuenta cifras significativas explícitas, incluidos ceros decimales finales.

    En enteros, los ceros finales sin coma decimal son ambiguos: se consideran
    significativos y se recomienda notación científica para otra intención.
    """
    s = txt.strip().replace(',', '.').lower()
    s = s.lstrip('+-').split('e')[0]
    dig = ''.join(c for c in s if c.isdigit())
    relevant = dig.lstrip('0')
    return len(relevant) if relevant else 1


def leer_numero_texto(txt: str, *, minimo: float | None = None,
                      maximo: float | None = None, estricto: bool = False) -> Medida:
    s = txt.strip().replace(' ', '').replace(',', '.')
    if not re.fullmatch(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?', s):
        raise DatosInvalidos('Escriba un número decimal; se admiten coma y notación científica.')
    try:
        val = float(Decimal(s))
    except (InvalidOperation, OverflowError):
        raise DatosInvalidos('Número no válido.') from None
    if not math.isfinite(val):
        raise DatosInvalidos('No se aceptan valores infinitos ni NaN.')
    if minimo is not None and (val <= minimo if estricto else val < minimo):
        raise DatosInvalidos(f'Debe ser {">" if estricto else ">="} {minimo}.')
    if maximo is not None and val > maximo:
        raise DatosInvalidos(f'Debe ser <= {maximo}.')
    return Medida(val, sig_figs(s), txt.strip())


def pedir(etiqueta: str, *, minimo: float | None = None,
          maximo: float | None = None, estricto: bool = False) -> Medida:
    while True:
        try:
            return leer_numero_texto(input(f'{etiqueta}: '), minimo=minimo,
                                     maximo=maximo, estricto=estricto)
        except DatosInvalidos as exc:
            print(f'  ERROR: {exc}')


def pedir_factor(etiqueta: str = 'Factor de van t Hoff (1 exacto para soluto molecular ideal)') -> Medida:
    """La entrada textual '1' se toma como hipótesis i=1 EXACTA; '1,0' no."""
    v = pedir(etiqueta, minimo=0, estricto=True)
    return Medida(v.valor, 15, v.literal) if v.literal.strip()=='1' else v


def temperatura_absoluta(T_celsius: Medida) -> Medida:
    """Celsius -> Kelvin exacta; conserva DECIMALES de lectura (no sig de °C)."""
    val=Decimal(T_celsius.literal.replace(',','.'))+Decimal('273.15')
    # Conversión afín: redondeo al último decimal escrito en Celsius.
    raw=T_celsius.literal.replace(',','.').lower().split('e')[0]
    decimals=len(raw.split('.')[1]) if '.' in raw else 0
    val=val.quantize(Decimal(1).scaleb(-decimals),rounding=ROUND_HALF_UP)
    return Medida(float(Decimal(T_celsius.literal.replace(',','.'))+Decimal('273.15')),
                  sig_figs(format(val,'f')),str(val))


def pedir_entero(etiqueta: str, minimo: int = 1, maximo: int | None = None) -> int:
    while True:
        s = input(f'{etiqueta}: ').strip()
        if re.fullmatch(r'[+]?\d+', s):
            n = int(s)
            if n >= minimo and (maximo is None or n <= maximo):
                return n
        print(f'  ERROR: introduzca un entero >= {minimo}' +
              (f' y <= {maximo}.' if maximo is not None else '.'))


def menu(titulo: str, opciones: dict[str, str]) -> str:
    print('\n' + '=' * 72)
    print(titulo)
    for k, v in opciones.items():
        print(f' {k}. {v}')
    while True:
        s = input('Opción: ').strip()
        if s in opciones:
            return s
        print('  ERROR: opción inexistente.')


def numero(valor: float, cifras: int = 3) -> str:
    """Redondeo decimal half-up y presentación española, conservando ceros."""
    if not math.isfinite(valor):
        raise DatosInvalidos('Resultado no finito.')
    if cifras < 1 or cifras > 15:
        raise DatosInvalidos('El número de cifras significativas debe estar entre 1 y 15.')
    if valor == 0:
        return ('0' if cifras == 1 else '0,' + '0' * (cifras - 1))
    d = Decimal(str(valor))
    paso = Decimal('1').scaleb(d.adjusted() - cifras + 1)
    r = d.quantize(paso, rounding=ROUND_HALF_UP)
    exponent = r.adjusted()
    if exponent >= 4 or exponent <= -4:
        mantissa = r.scaleb(-exponent).quantize(Decimal('1').scaleb(1-cifras),
                                             rounding=ROUND_HALF_UP)
        return format(mantissa, 'f').replace('.', ',') + ' × 10^' + str(exponent)
    return format(r, 'f').replace('.', ',')


def cifras(*medidas: Medida, minimo: int = 1) -> int:
    return max(minimo, min(x.cifras for x in medidas))


def mostrar(nombre: str, valor: float, unidad: str = '', n: int = 3,
            formula: str = '', aviso: str = '') -> None:
    if formula:
        print('  Relación: ' + formula)
    print('  ' + nombre + ' = ' + numero(valor, n) + (f' {unidad}' if unidad else ''))
    if aviso:
        print('  AVISO: ' + aviso)


def validar_pos(*valores: float) -> None:
    if any(not math.isfinite(v) or v <= 0 for v in valores):
        raise DatosInvalidos('Se requieren valores positivos y finitos.')


def composicion(m2_g: float, M2_gmol: float, m1_g: float, M1_gmol: float) -> dict:
    validar_pos(m2_g, M2_gmol, m1_g, M1_gmol)
    n2 = m2_g / M2_gmol
    n1 = m1_g / M1_gmol
    return {'n1': n1, 'n2': n2, 'nt': n1+n2, 'x1': n1/(n1+n2),
            'x2': n2/(n1+n2), 'molalidad': n2/(m1_g/1000)}


def vapor_ideal(p_estrella: float, x1: float) -> dict:
    validar_pos(p_estrella)
    if not 0 < x1 <= 1:
        raise DatosInvalidos('La fracción molar debe pertenecer a (0, 1].')
    p = p_estrella*x1
    return {'presion': p, 'descenso': p_estrella-p,
            'descenso_relativo': 1-x1}


def molar_raith_exacto(m2_g: float, M1_gmol: float, m1_g: float,
                        descenso_relativo: float) -> float:
    validar_pos(m2_g, M1_gmol, m1_g)
    if not 0 < descenso_relativo < 1:
        raise DatosInvalidos('Descenso relativo fuera de (0, 1): masa molar indeterminada.')
    return m2_g*M1_gmol*(1-descenso_relativo)/(m1_g*descenso_relativo)


def termica_k(Tpuro_K: float, M1_kgmol: float, entalpia_Jmol: float) -> float:
    validar_pos(Tpuro_K, M1_kgmol, entalpia_Jmol)
    return R_J * Tpuro_K**2 * M1_kgmol / entalpia_Jmol


def coligativa(K: float, m: float, i: float = 1.) -> float:
    validar_pos(K, m, i)
    return K*m*i


def masa_molar_coligativa(K: float, m2_g: float, masa_disolvente_kg: float,
                          delta_K: float, i: float = 1.) -> float:
    validar_pos(K, m2_g, masa_disolvente_kg, delta_K, i)
    return i*K*m2_g/(delta_K*masa_disolvente_kg)


def presion_osmotica(c_mol_l: float, T_K: float, i: float = 1.) -> float:
    validar_pos(c_mol_l, T_K, i)
    return i*c_mol_l*R_BAR_L*T_K  # bar


def masa_molar_osmotica(masa_g: float, T_K: float, P_bar: float,
                         volumen_L: float, i: float = 1.) -> float:
    validar_pos(masa_g, T_K, P_bar, volumen_L, i)
    return i*masa_g*R_BAR_L*T_K/(P_bar*volumen_L)


def factor_vanthoff(delta: float, K: float, molalidad: float) -> float:
    validar_pos(delta, K, molalidad)
    return delta/(K*molalidad)


def alpha_disociacion(i: float, nu: int) -> float:
    if nu < 2:
        raise DatosInvalidos('Para disociación se necesita nu >= 2.')
    return (i-1)/(nu-1)


def alpha_asociacion(i: float, p: int) -> float:
    if p < 2:
        raise DatosInvalidos('Para asociación se necesita p >= 2.')
    return p*(1-i)/(p-1)


def resolver_biseccion(f: Callable[[float], float], a: float, b: float,
                       tolerancia: float, iter_max: int) -> tuple[float, int]:
    """Bisección con comprobación de intervalo, continuidad a cargo del modelo."""
    if not (math.isfinite(a) and math.isfinite(b) and a < b and
            math.isfinite(tolerancia) and tolerancia > 0 and iter_max > 0):
        raise DatosInvalidos('Intervalo, tolerancia o iteraciones inválidos.')
    fa, fb = f(a), f(b)
    if not all(map(math.isfinite, (fa, fb))):
        raise DatosInvalidos('El modelo no es válido en los extremos.')
    if fa == 0: return (a, 0)
    if fb == 0: return (b, 0)
    if fa*fb > 0:
        raise DatosInvalidos('No se encierra una raíz (f(a) y f(b) con igual signo).')
    for n in range(1, iter_max+1):
        c = (a+b)/2
        fc = f(c)
        if not math.isfinite(fc):
            raise DatosInvalidos('El modelo deja de estar definido en el intervalo.')
        if fc == 0 or abs(b-a)/2 <= tolerancia:
            return c, n
        if fa*fc < 0:
            b, fb = c, fc
        else:
            a, fa = c, fc
    raise DatosInvalidos(f'No convergió en {iter_max} iteraciones; intervalo final [{a}, {b}].')


def ajuste_polinomio(puntos: list[tuple[float, float]], grado: int) -> list[float]:
    """Mínimos cuadrados mediante QR de Gram-Schmidt modificado.

    Devuelve coeficientes desde el término independiente; se normaliza la x
    para reducir el condicionamiento numérico y se reescala al final.
    """
    if grado not in (0, 1, 2) or len(puntos) < grado+1:
        raise DatosInvalidos('Grado permitido 0, 1 o 2; faltan puntos.')
    if any(not (math.isfinite(x) and math.isfinite(y) and x>0 and y>0)
           for x, y in puntos):
        raise DatosInvalidos('Todos los datos experimentales deben ser positivos.')
    xs = [p[0] for p in puntos]
    center = sum(xs)/len(xs)
    scale = max(abs(x-center) for x in xs) or 1.
    xx = [(x-center)/scale for x in xs]
    cols = [[x**j for x in xx] for j in range(grado+1)]
    q: list[list[float]] = []
    r = [[0.0]*(grado+1) for _ in range(grado+1)]
    for j, orig in enumerate(cols):
        v = orig.copy()
        for k in range(j):
            r[k][j] = sum(q[k][t]*v[t] for t in range(len(v)))
            v = [v[t]-r[k][j]*q[k][t] for t in range(len(v))]
        norm = math.sqrt(sum(t*t for t in v))
        if norm < 1e-10:
            raise DatosInvalidos('Concentraciones insuficientemente distintas: ajuste singular.')
        r[j][j] = norm
        q.append([t/norm for t in v])
    y = [p[1] for p in puntos]
    rhs = [sum(v*w for v, w in zip(qj,y)) for qj in q]
    b = [0.0]*(grado+1)
    for j in range(grado, -1, -1):
        b[j] = (rhs[j]-sum(r[j][k]*b[k] for k in range(j+1, grado+1)))/r[j][j]
    # Polynomial b0 + b1 ((x-c)/s) + b2 ((x-c)/s)^2.
    c0 = b[0] - (b[1]*center/scale if grado>=1 else 0) + (b[2]*(center/scale)**2 if grado>=2 else 0)
    c1 = (b[1]/scale if grado>=1 else 0) - (2*b[2]*center/scale**2 if grado>=2 else 0)
    c2 = b[2]/scale**2 if grado>=2 else 0
    return [c0,c1,c2][:grado+1]


def obtener_graficas():
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from matplotlib.ticker import FuncFormatter
        return plt, FuncFormatter
    except ImportError as exc:
        raise DatosInvalidos('Falta Matplotlib. Instalar: python -m pip install matplotlib') from exc


def exportar_grafica(xs: list[float], series: list[tuple[str, list[float], str]],
                     eje_x: str, eje_y: str, nombre: str, *, ver: bool = False) -> Path:
    plt, FuncFormatter = obtener_graficas()
    if len(xs)<2 or any(len(ys)!=len(xs) for _,ys,_ in series):
        raise DatosInvalidos('Longitudes incoherentes para el gráfico.')
    carpeta = Path('resultados_capitulo10')
    carpeta.mkdir(parents=True, exist_ok=True)
    base = carpeta / re.sub(r'[^a-zA-Z0-9_-]+','_', nombre)
    fig, ax = plt.subplots(figsize=(8,5.3))
    for label, ys, estilo in series:
        ax.plot(xs,ys,estilo,label=label,linewidth=1.9)
    ax.set(xlabel=eje_x,ylabel=eje_y)
    ax.grid(True,linestyle=':',alpha=.45)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:g}'.replace('.',',')))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f'{y:g}'.replace('.',',')))
    if len(series)>1: ax.legend()
    fig.tight_layout()
    fig.savefig(base.with_suffix('.png'),dpi=400)
    fig.savefig(base.with_suffix('.svg'))
    with base.with_suffix('.csv').open('w',newline='',encoding='utf-8-sig') as f:
        wr = csv.writer(f,delimiter=';')
        wr.writerow([eje_x]+[name for name,_,_ in series])
        for n,x in enumerate(xs):
            wr.writerow([f'{x:.12g}'.replace('.',',')]+
                        [f'{ys[n]:.12g}'.replace('.',',') for _,ys,_ in series])
    if ver:
        print('En modo interactivo puede abrir los archivos generados con su visor.')
    plt.close(fig)
    print(f'Guardados: {base}.png (400 ppp), {base}.svg y {base}.csv')
    return base


def pasos_composicion() -> None:
    print('Soluto 2 y disolvente 1; las masas y masas molares se expresan en g y g/mol.')
    m2=pedir('Masa de soluto (g)',minimo=0,estricto=True)
    M2=pedir('Masa molar del soluto (g/mol)',minimo=0,estricto=True)
    m1=pedir('Masa de disolvente (g)',minimo=0,estricto=True)
    M1=pedir('Masa molar del disolvente (g/mol)',minimo=0,estricto=True)
    a=composicion(m2.valor,M2.valor,m1.valor,M1.valor)
    s=cifras(m2,M2,m1,M1)
    mostrar('n_soluto',a['n2'],'mol',s,'n2 = m2/M2')
    mostrar('n_disolvente',a['n1'],'mol',s,'n1 = m1/M1')
    mostrar('x2',a['x2'],n=s,formula='x2 = n2/(n1+n2)')
    mostrar('x1',a['x1'],n=min(10,max(5,s+2)),formula='x1 = 1-x2 (cifras de guarda)')
    mostrar('molalidad',a['molalidad'],'mol/kg',s,'m = n2/(m1/1000)')
    if input('¿Se conoce el volumen final para calcular molaridad? [s/N] ').strip().lower()=='s':
        V=pedir('Volumen de disolución (L)',minimo=0,estricto=True)
        mostrar('c2',a['n2']/V.valor,'mol/L',cifras(m2,M2,V),'c2=n2/V')


def pasos_vapor() -> None:
    o=menu('Presión de vapor (disolución binaria ideal, soluto no volátil)',{
        '1':'Cálculo de P, descenso y descenso relativo desde masas',
        '2':'Obtener M2 mediante descenso relativo (relación exacta)',
        '3':'Obtener M2 desde presión del disolvente puro y disolución',
        '0':'Volver'})
    if o=='0':return
    if o=='1':
        m2=pedir('Masa soluto (g)',minimo=0,estricto=True)
        M2=pedir('Masa molar soluto (g/mol)',minimo=0,estricto=True)
        m1=pedir('Masa disolvente (g)',minimo=0,estricto=True)
        M1=pedir('Masa molar disolvente (g/mol)',minimo=0,estricto=True)
        pstar=pedir('Presión de vapor del disolvente puro (kPa)',minimo=0,estricto=True)
        x=composicion(m2.valor,M2.valor,m1.valor,M1.valor)
        r=vapor_ideal(pstar.valor,x['x1'])
        n=cifras(m2,M2,m1,M1,pstar)
        mostrar('x2',x['x2'],n=n,formula='x2=(m2/M2)/[(m1/M1)+(m2/M2)]')
        mostrar('x1',x['x1'],n=min(10,n+3),formula='x1=1-x2 (guarda)')
        mostrar('P',r['presion'],'kPa',n,'P=x1 P*')
        mostrar('Descenso ΔP',r['descenso']*1000,'Pa',n,'ΔP=P* x2')
        mostrar('Descenso relativo',100*r['descenso_relativo'],'%',n,'100 ΔP/P*=100 x2')
    else:
        m2=pedir('Masa soluto (g)',minimo=0,estricto=True)
        m1=pedir('Masa disolvente (g)',minimo=0,estricto=True)
        M1=pedir('Masa molar disolvente (g/mol)',minimo=0,estricto=True)
        if o=='2':
            r=pedir('Descenso relativo ΔP/P* (adimensional)',minimo=0,estricto=True,maximo=1)
            rr=r.valor; ins=(m2,m1,M1,r)
        else:
            pstar=pedir('P* del disolvente puro (kPa)',minimo=0,estricto=True)
            p=pedir('P de la disolución (kPa)',minimo=0,estricto=True)
            if p.valor >= pstar.valor:
                raise DatosInvalidos('En el modelo considerado 0 < P < P*.')
            rr=(pstar.valor-p.valor)/pstar.valor; ins=(m2,m1,M1,pstar,p)
            mostrar('Descenso relativo',rr,n=cifras(pstar,p),formula='r=(P*-P)/P*; no redondear antes de despejar')
        mostrar('M2',molar_raith_exacto(m2.valor,M1.valor,m1.valor,rr),'g/mol',cifras(*ins),
                'M2=m2 M1(1-r)/(m1 r)')


def pasos_termodinamica() -> None:
    o=menu('Elevar / descender T: K = R (T*)² M1 / ΔH',{'1':'Calcular K a partir de ΔH','0':'Volver'})
    if o=='0':return
    T=pedir('Temperatura de cambio de fase del disolvente puro (K)',minimo=0,estricto=True)
    M=pedir('Masa molar disolvente (kg/mol)',minimo=0,estricto=True)
    H=pedir('Entalpía molar de cambio de fase (J/mol)',minimo=0,estricto=True)
    mostrar('K',termica_k(T.valor,M.valor,H.valor),'K kg/mol',cifras(T,M,H),
            'K=R(T*)² M1/ΔH; R=8,314462618 J/(mol K)')


def pasos_temperaturas(ebullicion: bool) -> None:
    nombre='ebulloscopía' if ebullicion else 'crioscopía'
    print('\n'+nombre.upper()+': para solutos moleculares i=1; para electrolitos i experimental.')
    o=menu('Cálculos con ΔT = i K m',{
        '1':'Conocida molalidad: descenso/elevación y temperatura final',
        '2':'Conocidas masas y masa molar: ΔT y temperatura final',
        '3':'Despejar masa molar del soluto M2',
        '4':'Despejar molalidad m (y opcionalmente masa de soluto)',
        '5':'Despejar K o i',
        '6':'Calcular K termodinámica desde T*, M1 y entalpía',
        '0':'Volver'})
    if o=='0':return
    if o=='6': pasos_termodinamica();return
    if o=='5':
        d=pedir('Variación experimental ΔT (K)',minimo=0,estricto=True)
        m=pedir('Molalidad (mol/kg)',minimo=0,estricto=True)
        sub=menu('Incógnita',{'1':'K (i conocido)','2':'i (K conocida)'})
        if sub=='1':
            i=pedir_factor('Factor i (>0)')
            mostrar('K',d.valor/(i.valor*m.valor),'K kg/mol',cifras(d,i,m),'K=ΔT/(i m)')
        else:
            K=pedir('K (K kg/mol)',minimo=0,estricto=True)
            mostrar('i',d.valor/(K.valor*m.valor),n=cifras(d,K,m),formula='i=ΔT/(K m)')
        return
    K=pedir('Constante ebulloscópica/crioscópica K (K kg/mol)',minimo=0,estricto=True)
    i=pedir_factor('Factor de van t Hoff i (1 si no hay asociación/disociación)')
    if o=='1':
        m=pedir('Molalidad (mol/kg)',minimo=0,estricto=True)
        d=coligativa(K.valor,m.valor,i.valor)
        sf=cifras(K,m,i)
    elif o=='2':
        m2=pedir('Masa soluto (g)',minimo=0,estricto=True)
        M2=pedir('Masa molar soluto (g/mol)',minimo=0,estricto=True)
        m1=pedir('Masa disolvente (kg)',minimo=0,estricto=True)
        m=m2.valor/M2.valor/m1.valor
        sf=cifras(K,i,m2,M2,m1)
        mostrar('Molalidad',m,'mol/kg',sf,'m=(m2/M2)/m1')
        d=coligativa(K.valor,m,i.valor)
    elif o=='3':
        m2=pedir('Masa soluto (g)',minimo=0,estricto=True)
        m1=pedir('Masa disolvente (kg)',minimo=0,estricto=True)
        dM=pedir('Descenso/elevación ΔT (K)',minimo=0,estricto=True)
        sf=cifras(K,i,m2,m1,dM)
        mostrar('M2',masa_molar_coligativa(K.valor,m2.valor,m1.valor,dM.valor,i.valor),
                'g/mol',sf,'M2=i K m2/(ΔT m1)')
        return
    elif o=='4':
        dM=pedir('Descenso/elevación ΔT (K)',minimo=0,estricto=True)
        sf=cifras(K,i,dM)
        m=dM.valor/(i.valor*K.valor)
        mostrar('Molalidad',m,'mol/kg',sf,'m=ΔT/(i K)')
        if input('¿Calcular masa de soluto? [s/N] ').strip().lower()=='s':
            M2=pedir('Masa molar soluto (g/mol)',minimo=0,estricto=True)
            m1=pedir('Masa disolvente (kg)',minimo=0,estricto=True)
            mostrar('Masa soluto',m*M2.valor*m1.valor,'g',cifras(K,i,dM,M2,m1),'m2=m M2 m1')
        return
    mostrar('Variación ΔT',d,'K',sf,'ΔT=i K m')
    if input('¿Obtener temperatura final desde T*? [s/N] ').strip().lower()=='s':
        t=pedir('T* del disolvente puro (°C; se admiten negativos)')
        final=t.valor+d if ebullicion else t.valor-d
        mostrar('Temperatura final',final,'°C',max(1,sf),
                ('Tb=Tb*+ΔTb' if ebullicion else 'Tf=Tf*-ΔTf'),
                'La resolución decimal de la temperatura medida puede limitar la presentación.')


def pasos_osmosis() -> None:
    o=menu('Presión osmótica: Pi = i c R T, R = 0,083144626 L bar/(mol K)',{
        '1':'Presión desde c, T e i',
        '2':'Presión desde masa, M2 y volumen de disolución',
        '3':'Masa molar desde presión, masa, volumen y T',
        '4':'Osmolaridad y presión desde g/L o % m/V',
        '5':'Despejar concentración, masa o volumen desde Pi',
        '6':'Altura hidrostática equivalente a una diferencia de presión',
        '0':'Volver'})
    if o=='0':return
    if o=='6':
        DP=pedir('Diferencia de presión positiva (bar)',minimo=0,estricto=True)
        rho=pedir('Densidad aproximada (kg/m³)',minimo=0,estricto=True)
        g=pedir('Gravedad (m/s²; normalmente 9,81)',minimo=0,estricto=True)
        mostrar('Diferencia de alturas Δh',DP.valor*1e5/(rho.valor*g.valor),'m',cifras(DP,rho,g),
                'Δh = ΔP/(ρ g); supuesto de densidades iguales')
        return
    T=pedir('Temperatura (°C; no inferior a -273,15)',minimo=-273.15,estricto=True)
    TK=temperatura_absoluta(T)
    tk=TK.valor
    if o=='3':
        g=pedir('Masa de soluto (g)',minimo=0,estricto=True)
        V=pedir('Volumen final de disolución (L)',minimo=0,estricto=True)
        P=pedir('Presión osmótica (bar)',minimo=0,estricto=True)
        i=pedir_factor('Factor i')
        mostrar('M2',masa_molar_osmotica(g.valor,tk,P.valor,V.valor,i.valor),
                'g/mol',cifras(g,V,P,TK,i),'M2=i m2 R T/(Π V)')
    elif o=='5':
        p=pedir('Presión osmótica (bar)',minimo=0,estricto=True)
        i=pedir_factor('Factor i')
        c=p.valor/(i.valor*R_BAR_L*tk)
        mostrar('Concentración molar',c,'mol/L',cifras(p,i,TK),'c=Π/(iRT)')
        if input('¿Convertir a masa para volumen conocido? [s/N] ').strip().lower()=='s':
            M=pedir('Masa molar (g/mol)',minimo=0,estricto=True)
            V=pedir('Volumen de disolución (L)',minimo=0,estricto=True)
            mostrar('Masa',c*M.valor*V.valor,'g',cifras(p,i,TK,M,V),'m2=c M2 V')
    else:
        if o=='1':
            c=pedir('Concentración analítica (mol/L)',minimo=0,estricto=True)
            i=pedir_factor('Factor i')
            val=c.valor; s=cifras(c,TK,i)
        elif o=='2':
            m2=pedir('Masa de soluto (g)',minimo=0,estricto=True)
            M2=pedir('Masa molar (g/mol)',minimo=0,estricto=True)
            V=pedir('Volumen final (L)',minimo=0,estricto=True)
            i=pedir_factor('Factor i')
            val=m2.valor/M2.valor/V.valor
            s=cifras(m2,M2,V,TK,i)
            mostrar('Concentración analítica',val,'mol/L',s,'c=(m2/M2)/V')
        else:
            tipo=menu('Formato de entrada',{'1':'Concentración másica g/L',
                                           '2':'Porcentaje masa/volumen (% m/V)'})
            cm=pedir('Concentración (g/L o g/100 mL)',minimo=0,estricto=True)
            M2=pedir('Masa molar soluto (g/mol)',minimo=0,estricto=True)
            i=pedir_factor('Factor i (límite ideal si electrolito)')
            val=cm.valor*(10 if tipo=='2' else 1)/M2.valor
            s=cifras(cm,M2,TK,i)
            mostrar('Concentración analítica',val,'mol/L',s,'c=(g/L)/M2')
        pi=presion_osmotica(val,tk,i.valor)
        mostrar('Osmolaridad ideal',val*i.valor,'Osm/L',s,'c_part = i c')
        mostrar('Π',pi,'bar',s,'Π=i c R T')
        mostrar('Π',pi*1e5,'Pa',s,'1 bar = 100000 Pa')
        print('  AVISO: la osmolaridad ideal no equivale necesariamente a tonicidad.')


def pasos_factor() -> None:
    o=menu('Factor de van t Hoff / grado de asociación',{
        '1':'i experimental por crioscopía o ebulloscopía',
        '2':'i experimental por presión osmótica',
        '3':'Grado de disociación ideal α para ν especies',
        '4':'Grado de asociación ideal α para agregados de p monómeros',
        '5':'Diferencia frente al límite estequiométrico ideal',
        '0':'Volver'})
    if o=='0':return
    if o=='1':
        d=pedir('ΔT experimental (K)',minimo=0,estricto=True)
        K=pedir('K (K kg/mol)',minimo=0,estricto=True)
        m=pedir('Molalidad formal (mol/kg)',minimo=0,estricto=True)
        mostrar('i experimental',factor_vanthoff(d.valor,K.valor,m.valor),n=cifras(d,K,m),
                formula='i=ΔT_exp/(K m)')
    elif o=='2':
        pi=pedir('Π experimental (bar)',minimo=0,estricto=True)
        c=pedir('Concentración analítica (mol/L)',minimo=0,estricto=True)
        T=pedir('Temperatura (°C)',minimo=-273.15,estricto=True)
        mostrar('i experimental',pi.valor/(c.valor*R_BAR_L*(T.valor+273.15)),
                n=cifras(pi,c,temperatura_absoluta(T)),formula='i=Π/(cRT)')
    elif o in ('3','4'):
        i=pedir('Factor experimental i',minimo=0,estricto=True)
        count=pedir_entero('Número ν de iones o p de monómeros agregados (>= 2)',2)
        alpha=alpha_disociacion(i.valor,count) if o=='3' else alpha_asociacion(i.valor,count)
        mostrar('α',alpha,n=i.cifras,formula=('α=(i-1)/(ν-1)' if o=='3' else 'α=p(1-i)/(p-1)'))
        mostrar('Porcentaje de unidades iniciales transformadas',100*alpha,'%',i.cifras)
        if not (0<=alpha<=1):
            print('  AVISO: α fuera de [0,1]; la relación ideal no explica estos datos.')
        else:
            print('  AVISO: solo es grado químico real bajo modelo ideal de partículas independientes.')
    else:
        iexp=pedir('i experimental',minimo=0,estricto=True)
        nu=pedir_entero('ν estequiométrico entero',1)
        mostrar('Diferencia ν-i',nu-iexp.valor,n=iexp.cifras,formula='Δi=ν-i_exp')
        mostrar('Desviación respecto a ν',100*(nu-iexp.valor)/nu,'%',iexp.cifras,
                '100(ν-i_exp)/ν', 'No atribuir automáticamente a disociación incompleta.')


def pasos_ajuste() -> None:
    print('Ajuste osmótico Π/c_m = RT/M + B c_m + C c_m² (c_m en g/L, Π en bar).')
    print('La concentración debe ser baja; el intercepto a c_m=0 determina M_n.')
    grado=pedir_entero('Grado del polinomio [0=ideal, 1 o 2]',0,2)
    n=pedir_entero('Número de medidas',max(3,grado+2))
    puntos=[]
    for k in range(1,n+1):
        cm=pedir(f'Punto {k} concentración másica (g/L)',minimo=0,estricto=True)
        pi=pedir(f'Punto {k} presión osmótica (bar)',minimo=0,estricto=True)
        puntos.append((cm.valor,pi.valor/cm.valor))
    T=pedir('Temperatura (°C)',minimo=-273.15,estricto=True)
    coeff=ajuste_polinomio(puntos,grado)
    for k,c in enumerate(coeff):
        mostrar(('Intercepto RT/M' if k==0 else ('B' if k==1 else 'C')),
                c,n=6,formula=('ajuste por mínimos cuadrados' if k==0 else ''))
    if coeff[0] <= 0: raise DatosInvalidos('El ajuste produce intercepto no positivo; masa molar no física.')
    mostrar('M_n extrapolada',R_BAR_L*(T.valor+273.15)/coeff[0],'g/mol',temperatura_absoluta(T).cifras,
            'M_n=RT / lim_(c_m→0)(Π/c_m)')
    xs=[min(x for x,_ in puntos)+j*(max(x for x,_ in puntos)-min(x for x,_ in puntos))/150
        for j in range(151)]
    if input('¿Guardar gráfica y CSV del ajuste? [s/N] ').strip().lower()=='s':
        obsx=[x for x,_ in sorted(puntos)]
        # Plot requires same x arrays; interpolate measured data as markers separately.
        _, _ = obtener_graficas()
        pred=[sum(c*x**j for j,c in enumerate(coeff)) for x in xs]
        exportar_grafica(xs,[('Ajuste Π/c_m',pred,'-')],
                         'Concentración másica / g L⁻¹','Π/c_m / bar L g⁻¹','ajuste_osmometrico')
        print('  Datos originales (c_m; Π/c_m):',puntos)


def pasos_graficos() -> None:
    o=menu('Gráficas (PNG 400 ppp, SVG vectorial, CSV)',{
        '1':'Descenso crioscópico y elevación ebulloscópica frente a molalidad',
        '2':'Presión de vapor frente a fracción molar del soluto',
        '3':'Presión osmótica frente a concentración',
        '4':'Factor i frente a grado α de disociación/asociación',
        '0':'Volver'})
    if o=='0':return
    if o=='1':
        kb=pedir('K_b (K kg/mol)',minimo=0,estricto=True)
        kf=pedir('K_f (K kg/mol)',minimo=0,estricto=True)
        i=pedir_factor('Factor i')
        fin=pedir('Molalidad máxima (mol/kg)',minimo=0,estricto=True)
        xs=[fin.valor*k/150 for k in range(151)]
        data=[('ΔTb', [i.valor*kb.valor*x for x in xs],'-'),
              ('ΔTf',[i.valor*kf.valor*x for x in xs],'--')]
        exportar_grafica(xs,data,'Molalidad / mol kg⁻¹','ΔT / K','curvas_ebulloscopia_crioscopia')
    elif o=='2':
        p=pedir('P* disolvente puro (kPa)',minimo=0,estricto=True)
        xs=[k/150 for k in range(151)]
        exportar_grafica(xs,[('Raoult: P=(1-x2)P*',[(1-x)*p.valor for x in xs],'-')],
                         'Fracción molar de soluto x2','P / kPa','ley_raoult')
    elif o=='3':
        T=pedir('T (°C)',minimo=-273.15,estricto=True)
        cmax=pedir('c máxima (mol/L)',minimo=0,estricto=True)
        i=pedir_factor('Factor i')
        xs=[cmax.valor*k/150 for k in range(151)]
        exportar_grafica(xs,[('Π ideal',[i.valor*R_BAR_L*(T.valor+273.15)*x for x in xs],'-')],
                         'Concentración analítica / mol L⁻¹','Π / bar','curva_osmotica')
    else:
        sub=menu('Mecanismo',{'1':'Disociación','2':'Asociación'})
        n=pedir_entero('Número ν de iones o p del agregado',2)
        xs=[k/150 for k in range(151)]
        ys=([1+x*(n-1) for x in xs] if sub=='1'
            else [1-x*(1-1/n) for x in xs])
        exportar_grafica(xs,[('i ideal',ys,'-')],
                         'Fracción α de moléculas iniciales','Factor i','factor_vanthoff_alpha')


def pruebas() -> tuple[int,int]:
    tests=[]
    def check(nombre, obtenido, esperado, atol):
        ok=math.isclose(obtenido,esperado,rel_tol=0,abs_tol=atol)
        tests.append((nombre,ok,obtenido,esperado))
    check('10.1 x_sacarosa',composicion(10,342.2965,100,18.0153)['x2'],0.005236,0.000001)
    ra=composicion(10,342.2965,100,18.0153)
    check('10.1 P disolución',vapor_ideal(3.167,ra['x1'])['presion'],3.150,0.001)
    check('10.1 ΔP Pa',vapor_ideal(3.167,ra['x1'])['descenso']*1000,16.6,0.12)
    check('10.2 M',masa_molar_coligativa(20.,0.5580,0.03350,2.18),153.,0.25)
    check('10.3 M_n',masa_molar_osmotica(2.05,298.15,1.21/100,0.100),42000.,80.)  # 1.21 kPa=0.0121 bar
    check('10.4 i',factor_vanthoff(.348,1.86,.100),1.87,.005)
    m=.200/60.05/.020
    i=.450/(5.12*m)
    check('10.5 i dimerización',i,.528,.001)
    check('10.5 α asociación',alpha_asociacion(i,2),.944,.003)
    check('10.6 fuerza iónica',.5*(.0400+.0150*4+.0200*4+.0300),.105,1e-12)
    check('C2 p osmótica 0.9% NaCl',presion_osmotica(9/58.44,310.15,2),7.95,.03)
    check('C5 OMS osmolaridad nominal',(75+75+65+20+10)/1000,.245,1e-12)
    check('Raoult inversa',molar_raith_exacto(10,18.0153,100,ra['x2']),342.2965,1e-8)
    check('C3 agua mar ideal m',1.1235/.965,1.164,.001)
    # Ejercicios finales tipo B (valores del enunciado, comparados con cálculo independiente).
    check('10.B.1 molalidad D-glucosa',composicion(36.0,180.16,500.0,18.0153)['molalidad'],.399645,1e-6)
    check('10.B.1 descenso crioscópico',coligativa(1.86,36/180.16/.5),.74334,1e-5)
    check('10.B.1 elevación ebulloscópica',coligativa(.512,36/180.16/.5),.20462,1e-5)
    check('10.B.2 molalidad naftaleno',composicion(12.817,128.17,500,78.11)['molalidad'],.2,1e-12)
    check('10.B.2 ΔTf',coligativa(5.12,.2),1.024,1e-12)
    check('10.B.2 ΔTb',coligativa(2.53,.2),.506,1e-12)
    check('10.B.3 NaCl factor',factor_vanthoff(3.4,1.86,1.00),1.827956989,1e-8)
    check('10.B.4 9g glucosa 1L presión',presion_osmotica(9/180.16,298.15),1.23838,1e-5)
    check('10.B.5 fracción molar glucosa',composicion(18.016,180.16,180.153,18.0153)['x2'],1/101,1e-14)
    check('10.B.5 descenso presión kPa',vapor_ideal(3.17,100/101)['descenso'],3.17/101,1e-14)
    check('10.B.9 masa molar muestra',masa_molar_coligativa(1.86,3.423,.100,.186),342.3,1e-9)
    check('10.B.10 etilenglicol ΔTf IDEAL',coligativa(1.86,124.14/62.07),3.72,1e-12)
    check('10.B.10 etilenglicol ΔTb IDEAL',coligativa(.512,124.14/62.07),1.024,1e-12)
    # Ejercicios tipo C, límite ideal (no deben interpretarse como medidas experimentales).
    check('10.C.1 NaCl producto 98%',10/(1.86*2)*58.44/.98,160.303,.001)
    check('10.C.1 CaCl2 producto 97%',10/(1.86*3)*110.98/.97,205.040,.001)
    check('10.C.2 NaCl solución comercial 0,9%',presion_osmotica(2*9/58.44,310.15),7.94270,.00002)
    check('10.C.2 glucosa monohidratada 5%',presion_osmotica(50/198.17,310.15),6.50636,.00002)
    check('10.C.5 osmolaridad desde masas OMS',13.5/180.16+2*2.6/58.44+
          2*1.5/74.5513+4*2.9/294.10,.243597,.000002)
    check('10.C.6 cociente Π(glucosa)/Π(BSA)',66400/180.16,368.5613,.0001)
    check('Conversión 25,0°C -> Kelvin 4 cifras',temperatura_absoluta(leer_numero_texto('25,0')).cifras,4,0)
    check('cifras coma',sig_figs('0,0500'),3,0)
    check('cifras ceros',sig_figs('0,00200'),3,0)
    check('formato',1 if numero(0.034567,3)=='0,0346' else 0,1,0)
    check('bisección',resolver_biseccion(lambda x:x*x-2,1,2,1e-10,100)[0],math.sqrt(2),1e-10)
    check('ajuste QR',ajuste_polinomio([(1,3),(2,5),(3,7)],1)[0],1,1e-10)
    for n,ok,got,expected in tests:
        print(('PASS' if ok else 'FAIL')+' '+n+' | calculado='+str(got)+' | referencia='+str(expected))
    ok_count=sum(p[1] for p in tests)
    print(f'RESULTADO: {ok_count}/{len(tests)} comprobaciones correctas.')
    return ok_count,len(tests)


def principal() -> None:
    print('CAPÍTULO 10 — PROPIEDADES COLIGATIVAS')
    print('Disoluciones ideales o aproximaciones explícitas; magnitudes y unidades visibles.')
    print('Introduzca valores con sus ceros significativos: 0,100 conserva 3 cifras.')
    while True:
        op=menu('MENÚ PRINCIPAL',{
            '1':'Composición (x, n, molalidad, molaridad)',
            '2':'Presión de vapor y ley de Raoult',
            '3':'Ebulloscopía',
            '4':'Crioscopía',
            '5':'Presión osmótica y osmolaridad',
            '6':'Factor de van t Hoff, disociación y asociación',
            '7':'Ajuste de datos osmóticos y extrapolación',
            '8':'Generar gráficos y CSV',
            '9':'Ejecutar pruebas del capítulo',
            '0':'Salir'})
        if op=='0':break
        try:
            {'1':pasos_composicion,'2':pasos_vapor,
             '3':lambda:pasos_temperaturas(True),'4':lambda:pasos_temperaturas(False),
             '5':pasos_osmosis,'6':pasos_factor,'7':pasos_ajuste,'8':pasos_graficos,
             '9':pruebas}[op]()
        except (DatosInvalidos, OverflowError, ZeroDivisionError) as exc:
            print('  ERROR DE CÁLCULO: '+str(exc))
        except (EOFError,KeyboardInterrupt):
            print('\nFin de la sesión.');break


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--selftest',action='store_true',help='Verificar resultados sin entrar al menú')
    args=ap.parse_args()
    if args.selftest:
        ok,total=pruebas()
        raise SystemExit(0 if ok==total else 1)
    principal()
