#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Capítulo 9. Equilibrio líquido–líquido. Python 3.10+; matplotlib para gráficos.

Todas las funciones de cálculo devuelven valores SIN redondear: el redondeo
se reserva para la presentación. L1 y L2 son las fases parcialmente miscibles.
"""
from __future__ import annotations
import csv
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import math
from pathlib import Path


def leer_numero(mensaje: str, *, minimo=None, maximo=None, estricto_min=False) -> tuple[float, str]:
    while True:
        s = input(mensaje).strip().replace(' ', '').replace(',', '.')
        try:
            d = Decimal(s)
            if not d.is_finite():
                raise ValueError('No se admite NaN ni infinito.')
            v = float(d)
            if not math.isfinite(v):
                raise ValueError('Fuera del intervalo numérico.')
            if minimo is not None and (v <= minimo if estricto_min else v < minimo):
                raise ValueError(f'Debe ser {">" if estricto_min else ">="} {minimo}.')
            if maximo is not None and v > maximo:
                raise ValueError(f'Debe ser <= {maximo}.')
            return v, s
        except (InvalidOperation, ValueError) as exc:
            print(f'  Dato no válido: {exc}')


def cifras(s: str) -> int:
    """Cifras de un dato escrito, incluidos ceros finales decimales.

    Los enteros terminados en cero son ambiguos: se presume que esos ceros
    NO son significativos; use, por ejemplo, 500. o 5,00e2 para aclararlo.
    """
    s = s.strip().replace(' ', '').replace(',', '.').lstrip('+-')
    a = s.lower().split('e')[0]
    digits = ''.join(c for c in a if c.isdigit())
    significant = digits.lstrip('0')
    if not significant:
        return 1
    if '.' not in a:
        significant = significant.rstrip('0') or '0'
    return max(1, len(significant))


def fmt(v: float, n: int = 3) -> str:
    """Presenta n cifras significativas, coma decimal y ceros significativos."""
    if not math.isfinite(v):
        return str(v)
    if v == 0:
        return '0'
    n = max(1, min(12, int(n)))
    magnitude = math.floor(math.log10(abs(v)))
    places = n - 1 - magnitude
    d = Decimal(str(v))
    q = Decimal('1').scaleb(-places)
    d = d.quantize(q, rounding=ROUND_HALF_UP)
    if magnitude >= 6 or magnitude <= -5:
        return f'{v:.{n-1}e}'.replace('.', ',')
    return format(d, 'f').replace('.', ',')


def validar_fraccion(v: float, nombre: str) -> None:
    if not math.isfinite(v) or not 0 <= v <= 1:
        raise ValueError(f'{nombre}: la fracción debe estar entre 0 y 1.')


def conversion_masica_molar(w_a: float, m_a: float, m_b: float) -> float:
    validar_fraccion(w_a, 'w_A')
    if min(m_a, m_b) <= 0 or not all(map(math.isfinite, (m_a, m_b))):
        raise ValueError('Masas molares positivas y finitas obligatorias.')
    n_a = w_a/m_a
    n_b = (1-w_a)/m_b
    return n_a/(n_a+n_b)


def conversion_molar_masica(x_a: float, m_a: float, m_b: float) -> float:
    validar_fraccion(x_a, 'x_A')
    if min(m_a, m_b) <= 0 or not all(map(math.isfinite, (m_a, m_b))):
        raise ValueError('Masas molares positivas y finitas obligatorias.')
    return x_a*m_a/(x_a*m_a+(1-x_a)*m_b)


@dataclass(frozen=True)
class FasesLL:
    tipo: str
    z: float
    x_l1: float
    x_l2: float
    total: float
    f_l1: float
    f_l2: float
    l1: float
    l2: float
    a_l1: float
    a_l2: float
    b_l1: float
    b_l2: float
    residuo_total: float
    residuo_a: float
    residuo_b: float


def regla_palanca(total: float, z: float, x_l1: float, x_l2: float) -> FasesLL:
    """Regla general para L1 y L2, sin exigir un orden de las composiciones.

    Si la abscisa es x_A del capítulo, L1 suele ser rica en A (x_L1 > x_L2).
    Si es w_isooctano del ejemplo 9.2, L1 es pobre en isooctano
    (w_L1 < w_L2). El programa conserva ambas convenciones.
    """
    for k,v in [('z', z), ('x_L1',x_l1), ('x_L2',x_l2)]:
        validar_fraccion(v,k)
    if not math.isfinite(total) or total <= 0:
        raise ValueError('Cantidad total estrictamente positiva.')
    if x_l1 == x_l2:
        raise ValueError('L1 y L2 deben tener composiciones conjugadas distintas.')
    if not min(x_l1,x_l2) < z < max(x_l1,x_l2):
        kind='una fase líquida (o límite binodal)'
        # No se atribuye a la fase única la composición de la otra rama.
        f1,f2=(1.,0.) if abs(z-x_l1)<=abs(z-x_l2) else (0.,1.)
        xa1=xa2=z
    else:
        kind='dos fases L1 + L2'
        f1=(z-x_l2)/(x_l1-x_l2)
        f2=1-f1
        xa1=x_l1;xa2=x_l2
    l1=total*f1; l2=total*f2
    a1=l1*xa1; a2=l2*xa2
    b1=l1*(1-xa1); b2=l2*(1-xa2)
    return FasesLL(kind,z,x_l1,x_l2,total,f1,f2,l1,l2,a1,a2,b1,b2,
                   l1+l2-total,a1+a2-total*z,b1+b2-total*(1-z))


def beysens(epsilon: float, b: float=1.83, beta: float=.318, wc: float=.5350) -> tuple[float,float,float]:
    """Δw = B ε^β, aproximación simétrica únicamente en FRACCIÓN MÁSICA.
    Válida si 0 <= epsilon < 1 y 0 <= w1 <= w2 <= 1.
    La correlación corresponde al sistema nitroetano/isooctano del texto.
    """
    validar_fraccion(wc, 'w_c')
    if not all(math.isfinite(v) for v in (epsilon,b,beta)) or not 0 <= epsilon < 1:
        raise ValueError('ε debe encontrarse en 0 <= ε < 1.')
    if b <= 0 or beta <= 0:
        raise ValueError('B y β deben ser estrictamente positivos.')
    dw=b*epsilon**beta
    left,right=wc-dw/2,wc+dw/2
    if left < -1e-12 or right>1+1e-12:
        raise ValueError('El modelo produce fracciones fuera de [0,1]; NO extrapolar la correlación.')
    return dw, max(0.,left), min(1.,right)


def epsi_temperatura(t: float, tc: float) -> float:
    if tc <= 0 or t <= 0 or not all(map(math.isfinite,(t,tc))):
        raise ValueError('Temperaturas absolutas positivas (K).')
    return (tc-t)/tc


def binodal_csv(ruta: str) -> list[tuple[float,float,float]]:
    """Columnas T_K,izquierda,derecha; un solo dato por temperatura."""
    out=[]
    with open(ruta, newline='',encoding='utf-8-sig') as f:
        rows=csv.DictReader(f,delimiter=';')
        if rows.fieldnames is None or not {'T_K','izquierda','derecha'}.issubset(rows.fieldnames):
            raise ValueError('Cabeceras obligatorias: T_K;izquierda;derecha')
        for row in rows:
            t=float(row['T_K'].strip().replace(',','.'))
            lo=float(row['izquierda'].strip().replace(',','.'))
            hi=float(row['derecha'].strip().replace(',','.'))
            if t<=0 or not math.isfinite(t) or lo >= hi:
                raise ValueError('Cada fila necesita T>0 y composición izquierda < derecha.')
            validar_fraccion(lo,'izquierda'); validar_fraccion(hi,'derecha')
            out.append((t,lo,hi))
    out.sort()
    if len(out)<2 or any(out[i][0] >= out[i+1][0] for i in range(len(out)-1)):
        raise ValueError('Se necesitan al menos dos temperaturas diferentes.')
    return out


def precision_composiciones_csv(ruta: str) -> int:
    """Número mínimo de cifras significativas expresadas en las dos ramas.
    Para precisión metrológica de interpolación real se requieren incertidumbres
    experimentales: este criterio es un límite conservador de presentación.
    """
    with open(ruta,newline='',encoding='utf-8-sig') as fh:
        rows=csv.DictReader(fh,delimiter=';')
        nums=[cifras(row[k]) for row in rows for k in ('izquierda','derecha')]
    return min(nums) if nums else 1


def interpolar_binodal(datos: list[tuple[float,float,float]], t: float) -> tuple[float,float]:
    if not datos[0][0] <= t <= datos[-1][0]:
        raise ValueError('Temperatura fuera del intervalo tabulado. No se extrapola.')
    for (t0,x0,y0),(t1,x1,y1) in zip(datos,datos[1:]):
        if t0<=t<=t1:
            a=(t-t0)/(t1-t0)
            return x0+a*(x1-x0), y0+a*(y1-y0)
    raise RuntimeError('Interpolación no disponible.')


def regular_solucion(chi: float, tol: float=1e-11) -> tuple[float,float,float,float]:
    """Mezcla regular SIMÉTRICA: g/RT=x ln x+(1-x)ln(1-x)+χx(1-x).
    Binodal simétrica obtenida con igualdad de actividades; no usa datos reales.
    """
    if not math.isfinite(chi) or chi<=2:
        raise ValueError('Se necesitan χ>2 y dos fases para hallar binodal/espinodal.')
    def mu(x): return math.log(x/(1-x))+chi*(1-2*x)
    # Solución no trivial distinta de 1/2; estable cerca de x=0.
    lo=max(1e-300,math.exp(-chi)*0.01) if chi<700 else 1e-300
    hi=0.5-math.sqrt(1-2/chi)/2
    if mu(lo)>=0 or mu(hi)<=0:
        # al acercarse χ a 2, evitar cancelación en el límite de precisión
        raise ValueError('Parámetro χ muy próximo al punto crítico para precisión doble.')
    for _ in range(250):
        mid=(lo+hi)/2
        if mu(mid)>0: hi=mid
        else: lo=mid
        if hi-lo<tol: break
    a=(lo+hi)/2
    spin=(1-math.sqrt(1-2/chi))/2
    return a,1-a,spin,1-spin


def g_regular(x: float, chi: float)->float:
    if not 0<=x<=1: raise ValueError('x fuera de [0,1].')
    ent_a = x*math.log(x) if x>0 else 0.0
    ent_b = (1-x)*math.log(1-x) if x<1 else 0.0
    return ent_a+ent_b+chi*x*(1-x)



def pedir_grafica(nombre_base: str):
    import matplotlib.pyplot as plt
    print('  1. Mostrar   2. Guardar PNG (300 ppp)   3. Guardar SVG   4. Ambos formatos')
    op=input('  Selección [1]: ').strip() or '1'
    if op in ('2','3','4'):
        base=input(f'  Nombre sin extensión [{nombre_base}]: ').strip() or nombre_base
        p=Path(base)
        if op in ('2','4'):
            plt.savefig(p.with_suffix('.png'),dpi=300,bbox_inches='tight')
            print('  Guardado:',p.with_suffix('.png').resolve())
        if op in ('3','4'):
            plt.savefig(p.with_suffix('.svg'),bbox_inches='tight')
            print('  Guardado:',p.with_suffix('.svg').resolve())
    else:
        plt.show()
    plt.close()


def grafico_beysens(b: float,beta: float,wc: float,tc: float|None=None, epsilon_marca:float|None=None,z:float|None=None):
    import matplotlib.pyplot as plt
    # Solo trazar hasta la primera composición no física.
    samples=[]
    # Mostrar un tramo LOCAL alrededor del punto crítico; la correlación
    # experimental no autoriza extrapolación ilimitada en temperatura.
    e_max=min(.999, max(.03,1.25*(epsilon_marca if epsilon_marca is not None else .025)))
    for i in range(1001):
        e=i*e_max/1000
        try:
            _,lo,hi=beysens(e,b,beta,wc)
        except ValueError: break
        samples.append((e,lo,hi))
    if not samples: raise ValueError('No hay tramo físicamente admisible.')
    fig,ax=plt.subplots(figsize=(8,5.2))
    ts=[(tc*(1-e)-273.15 if tc else e) for e,_,_ in samples]
    ax.plot([v[1] for v in samples],ts,label=r'Fase izquierda $L_1$ (rica en nitroetano)')
    ax.plot([v[2] for v in samples],ts,label=r'Fase derecha $L_2$ (rica en isooctano)')
    if epsilon_marca is not None:
        _,lo,hi=beysens(epsilon_marca,b,beta,wc)
        y=tc*(1-epsilon_marca)-273.15 if tc else epsilon_marca
        ax.plot([lo,hi],[y,y],color='0.4',linestyle='--',label='Línea de reparto')
        if z is not None: ax.plot(z,y,marker='o',markersize=8,color='black',label='Composición global')
    ax.set(xlim=(0,1),xlabel=r'Fracción másica de isooctano, $w_{\mathrm{iso}}$',
           ylabel='Temperatura (°C)' if tc else 'Distancia reducida ε',
           title='Curva de coexistencia – correlación experimental (entorno crítico)')
    from matplotlib.ticker import FuncFormatter
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v,pos:f'{v:.1f}'.replace('.',',')))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v,pos:f'{v:g}'.replace('.',',')))
    ax.grid(alpha=.23);ax.legend(fontsize=9);fig.tight_layout();pedir_grafica('binodal_beysens')


def grafico_tabla(datos:list[tuple[float,float,float]],t:float|None=None,z:float|None=None):
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(8,5.2))
    ax.plot([v[1] for v in datos],[v[0] for v in datos],'-o',label='Rama izquierda')
    ax.plot([v[2] for v in datos],[v[0] for v in datos],'-o',label='Rama derecha')
    if t is not None:
        lo,hi=interpolar_binodal(datos,t)
        ax.plot([lo,hi],[t,t],linestyle='--',color='0.4',label='Línea de reparto')
        if z is not None: ax.scatter([z],[t],color='black',zorder=4,label='Mezcla global')
    ax.set(xlabel='Fracción del componente de referencia (base del CSV)',ylabel='T (K)',
           xlim=(0,1), title='Binodal interpolada a partir de datos suministrados')
    ax.grid(alpha=.25);ax.legend();fig.tight_layout();pedir_grafica('binodal_datos')


def grafico_regular(chi:float):
    import matplotlib.pyplot as plt
    lo,hi,spin1,spin2=regular_solucion(chi)
    xx=[i/1000 for i in range(1001)]
    yy=[g_regular(x,chi) for x in xx]
    ytie=g_regular(lo,chi)
    fig,ax=plt.subplots(figsize=(8,5.2))
    ax.plot(xx,yy,label='Gibbs reducida de mezcla')
    ax.plot([lo,hi],[ytie,ytie],linestyle='--',label='Tangente común')
    ax.scatter([lo,hi],[ytie,ytie],label='Binodal',zorder=5)
    ax.axvline(spin1,color='0.55',linestyle=':',label='Espinodales')
    ax.axvline(spin2,color='0.55',linestyle=':')
    ax.set(xlabel='Fracción molar x',ylabel='ΔG mezcla / RT',
           title=f'Modelo teórico simétrico χ={chi:g} (NO datos experimentales)')
    from matplotlib.ticker import FuncFormatter
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v,pos:f'{v:.1f}'.replace('.',',')))
    ax.grid(alpha=.2);ax.legend();fig.tight_layout();pedir_grafica('gibbs_regular')


def grafico_cualitativo():
    import matplotlib.pyplot as plt
    xx=[i/200 for i in range(201)]
    fig,axes=plt.subplots(1,3,figsize=(12,4))
    cases=('UCST (superior)','LCST (inferior)','Región cerrada')
    for ax,title in zip(axes,cases):
        ax.set(xlim=(0,1),ylim=(0,1),xlabel='Composición',ylabel='Temperatura reducida',title=title)
        ax.grid(alpha=.15)
    # SOLO esquemas cualitativos: funciones arbitrarias, sin unidades físicas.
    axes[0].plot(xx,[.86-2.6*(x-.5)**2 for x in xx]); axes[0].text(.48,.4,'L1 + L2',ha='center')
    axes[1].plot(xx,[.14+2.6*(x-.5)**2 for x in xx]); axes[1].text(.48,.75,'L1 + L2',ha='center')
    phi=[2*math.pi*i/300 for i in range(301)]
    axes[2].plot([.5+.34*math.cos(p) for p in phi],[.5+.38*math.sin(p) for p in phi])
    axes[2].text(.5,.5,'L1 + L2',ha='center')
    fig.suptitle('ESQUEMAS CUALITATIVOS: no representan datos medidos',fontsize=11)
    fig.tight_layout();pedir_grafica('tipos_binodal_esquema')


def presentar_fases(res:FasesLL,n:int,base:str):
    print(f'  Diagnóstico: {res.tipo}.')
    if res.tipo.startswith('una fase'):
        print(f'  Composición de la fase única = {fmt(res.z,n)}; cantidad = {fmt(res.total,n)} {base}.')
        print('  No se asignan composiciones conjugadas a una fase inexistente.')
        return
    for fase,fr,cantidad,aa,bb in [('L1',res.f_l1,res.l1,res.a_l1,res.b_l1),
                                   ('L2',res.f_l2,res.l2,res.a_l2,res.b_l2)]:
        print(f'  {fase}: fracción de fase {fmt(fr,n)}, cantidad {fmt(cantidad,n)} {base}, '
              f'componente A {fmt(aa,n)} {base}, componente B {fmt(bb,n)} {base}.')
    print(f'  Residuos sin redondear (total, A, B): '
          f'{res.residuo_total:.2e}, {res.residuo_a:.2e}, {res.residuo_b:.2e} {base}.')


def menu():
    print('\nCAPÍTULO 9 — EQUILIBRIO LÍQUIDO–LÍQUIDO')
    print('1  Conversión fracción másica ↔ molar')
    print('2  Regla de la palanca y balances L1/L2')
    print('3  Correlación de Beysens y masas de fases (con gráfica)')
    print('4  Binodal tabulada en CSV: interpolación, balances y gráfica')
    print('5  Modelo teórico de Gibbs: binodal, espinodal y gráfica')
    print('6  Gráficas cualitativas UCST / LCST / región cerrada')
    print('7  Ayuda / alcance científico')
    print('0  Salir')
    return input('Seleccione: ').strip()


def main():
    while True:
        try:
            op=menu()
            if op=='0': break
            if op=='1':
                m1,s1=leer_numero('Masa molar de A (g/mol): ',minimo=0,estricto_min=True)
                m2,s2=leer_numero('Masa molar de B (g/mol): ',minimo=0,estricto_min=True)
                kind=input('Introducir [m] fracción másica o [x] fracción molar de A [m]: ').strip().lower() or 'm'
                z,sz=leer_numero('Fracción de A: ',minimo=0,maximo=1)
                out=conversion_molar_masica(z,m1,m2) if kind=='x' else conversion_masica_molar(z,m1,m2)
                print(('  w_A = ' if kind=='x' else '  x_A = ')+fmt(out,min(map(cifras,(s1,s2,sz)))))
            elif op=='2':
                base=input('Base de los datos: kg, g, mol o kmol [kg]: ').strip() or 'kg'
                if base not in ('kg','g','mol','kmol'):
                    raise ValueError('Unidad: kg, g, mol o kmol.')
                print('  Fracciones MÁSICAS.' if base in ('kg','g') else '  Fracciones MOLARES.')
                total,st=leer_numero(f'Cantidad total ({base}): ',minimo=0,estricto_min=True)
                z,sz=leer_numero('Composición global A (misma base): ',minimo=0,maximo=1)
                lo,sl=leer_numero('Composición de A en L1 (normalmente rica en A): ',minimo=0,maximo=1)
                hi,sh=leer_numero('Composición de A en L2 (normalmente pobre en A): ',minimo=0,maximo=1)
                presentar_fases(regla_palanca(total,z,lo,hi),min(map(cifras,(st,sz,sl,sh))),base)
            elif op=='3':
                print('Beysens: nitroetano/isooctano, fracciones MÁSICAS de isooctano.')
                e,se=leer_numero('Distancia reducida ε: ',minimo=0,maximo=.999999)
                b,sb=leer_numero('B [1,83]: ',minimo=0,estricto_min=True) if input('¿Introducir B propio? [s/N]: ').strip().lower()=='s' else (1.83,'1.83')
                beta,ss=leer_numero('β [0,318]: ',minimo=0,estricto_min=True) if input('¿Introducir β propio? [s/N]: ').strip().lower()=='s' else (.318,'0.318')
                wc,sw=leer_numero('w_c [0,5350]: ',minimo=0,maximo=1) if input('¿Introducir w_c propio? [s/N]: ').strip().lower()=='s' else (.535,'0.5350')
                n=min(map(cifras,(se,sb,ss,sw)))
                dw,lo,hi=beysens(e,b,beta,wc)
                print(f'  Δw = {fmt(dw,n)}; w(L1, rica en nitroetano) ≈ {fmt(lo,n)}; '
                      f'w(L2, rica en isooctano) ≈ {fmt(hi,n)}.')
                mass,sm=leer_numero('Masa alimentación (kg), o 0 para omitir: ',minimo=0)
                z=None
                if mass>0:
                    z,sz=leer_numero('Fracción másica GLOBAL de isooctano: ',minimo=0,maximo=1)
                    presentar_fases(regla_palanca(mass,z,lo,hi),min(n,cifras(sm),cifras(sz)),'kg') if lo<hi else print('  Punto crítico: no hay dos fases distinguibles.')
                if input('¿Generar gráfica? [S/n]: ').strip().lower()!='n':
                    tc,sc=leer_numero('T crítica superior (K), 0 si no se conoce: ',minimo=0)
                    grafico_beysens(b,beta,wc,tc or None,e,z)
            elif op=='4':
                path=input('Ruta CSV (T_K;izquierda;derecha): ').strip().strip('"')
                datos=binodal_csv(path)
                nd=precision_composiciones_csv(path)
                t,st=leer_numero(f'T consulta (K, entre {datos[0][0]} y {datos[-1][0]}): ',minimo=datos[0][0],maximo=datos[-1][0])
                lo,hi=interpolar_binodal(datos,t)
                print(f'  Composiciones interpoladas: izquierda {fmt(lo,nd)}, derecha {fmt(hi,nd)}.')
                z,sz=leer_numero('Composición global de A (misma base que CSV): ',minimo=0,maximo=1)
                total,sm=leer_numero('Cantidad total (0 para no calcular masas/moles): ',minimo=0)
                if total>0:
                    base=input('Unidad del total (kg, mol ...): ').strip()
                    der=(input('  ¿L1 es la fase de la derecha (rica en el componente del eje)? [S/n]: ')
                         .strip().lower()!='n')
                    x1,x2=(hi,lo) if der else (lo,hi)
                    presentar_fases(regla_palanca(total,z,x1,x2),min(cifras(sm),cifras(sz),nd),base)
                print('  ATENCIÓN: interpolación lineal, no extrapolación ni ajuste termodinámico.')
                print(f'  Presentación limitada a {nd} cifras de la tabla; revise incertidumbres de medida.')
                if input('¿Dibujar diagrama? [S/n]: ').strip().lower()!='n': grafico_tabla(datos,t,z)
            elif op=='5':
                chi,sc=leer_numero('Parámetro adimensional χ (mayor que 2): ',minimo=2,estricto_min=True)
                lo,hi,sp1,sp2=regular_solucion(chi)
                print(f'  Binodal: ({fmt(lo,cifras(sc))}, {fmt(hi,cifras(sc))}); '
                      f'espinodal: ({fmt(sp1,cifras(sc))}, {fmt(sp2,cifras(sc))}).')
                print('  Solo modelo simétrico teórico; no predice un sistema real sin ajuste.')
                if input('¿Mostrar gráfica Gibbs? [S/n]: ').strip().lower()!='n': grafico_regular(chi)
            elif op=='6': grafico_cualitativo()
            elif op=='7':
                print('''\nA) L1 y L2: fases de una mezcla PARCIALMENTE miscible, con solubilidad mutua.
   L1 suele ser rica en A al usar x_A, pero es pobre en isooctano en el Ej. 9.2.
B) No confundir composición global z con composiciones de equilibrio.
C) Regla de la palanca: TODAS las fracciones deben usar la misma base:
   masa con masa, o moles con moles. Se verifican balances sin redondear.
D) Correlación Δw=B ε^β: solo nitroetano–isooctano y fracción MÁSICA;
   el empleo fuera de [0,1] constituye extrapolación no admisible.
E) χ regular es una DEMOSTRACIÓN teórica, no ajuste experimental.
F) El CSV usa ; como delimitador, cabeceras T_K;izquierda;derecha,
   fracciones en la misma base, temperaturas K; no se extrapola.
G) Cifras significativas: se interpretan según el texto introducido;
   escribir 500. o 5,00e2 para marcar 3 cifras, frente a 500 ambiguo.
   En cálculos de diferencias próximas y curvas críticas, la incertidumbre
   experimental puede dominar: las cifras impresas no son una garantía.
H) La gráfica en SVG conserva calidad vectorial para imprenta.''')
            else: print('  Opción inexistente.')
        except ImportError:
            print('  ERROR: faltan bibliotecas para dibujar. Instale: python -m pip install matplotlib')
        except (ValueError, ArithmeticError, OSError, OverflowError) as e:
            print(f'  ERROR CONTROLADO: {e}')
        except (KeyboardInterrupt, EOFError):
            print('\n  Interrumpido por el usuario.');break

if __name__=='__main__': main()
