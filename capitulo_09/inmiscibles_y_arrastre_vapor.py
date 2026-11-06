#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Capítulo 9. Equilibrio LA + LB + V y destilación por arrastre de vapor.

Hipótesis: líquidos prácticamente inmiscibles, vapor ideal y equilibrio a
P y T comunes, CON LAS DOS fases líquidas presentes. No representa un
modelo completo para el régimen posterior al agotamiento de una fase.
Los cálculos internos no se redondean; solo la presentación al alumno.
Python 3.10+. Matplotlib solo es necesario cuando se solicita una gráfica.
"""
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from pathlib import Path
import math


@dataclass(frozen=True)
class Antoine:
    nombre: str
    a: float
    b: float
    c: float
    m: float           # g/mol
    t_min: float|None = None
    t_max: float|None = None
    origen: str = 'Coeficientes introducidos por el usuario'
    ncoef: int = 5

    def presion_bar(self, t:float, *,estricto=True)->float:
        if not math.isfinite(t) or t<=0:
            raise ValueError('La temperatura Kelvin debe ser positiva.')
        if estricto: self.comprobar_validez(t)
        if t+self.c <=0:
            raise ValueError(f'{self.nombre}: T+C <= 0, Antoine fuera de dominio.')
        expo=self.a-self.b/(t+self.c)
        if expo>300: raise ValueError(f'{self.nombre}: desbordamiento de presión.')
        return 10**expo

    def comprobar_validez(self,t:float):
        if self.t_min is not None and t < self.t_min-1e-9:
            raise ValueError(f'{self.nombre}: T={t:.3f} K fuera de Antoine: T < {self.t_min} K.')
        if self.t_max is not None and t > self.t_max+1e-9:
            raise ValueError(f'{self.nombre}: T={t:.3f} K fuera de Antoine: T > {self.t_max} K.')

    def ebullicion_puro(self,p_bar:float)->float:
        if p_bar<=0 or not math.isfinite(p_bar):
            raise ValueError('Presión de ebullición positiva obligatoria.')
        den=self.a-math.log10(p_bar)
        if den<=0:
            raise ValueError(f'{self.nombre}: imposible invertir Antoine en este dominio.')
        temp=self.b/den-self.c
        self.comprobar_validez(temp)
        if temp<=0: raise ValueError('Temperatura absoluta no física.')
        return temp


# Juegos de coeficientes utilizados en el capítulo 9; P*(bar), T(K).
# Los intervalos solo se anotan cuando constan explícitamente en el capítulo.
AGUA_1 = Antoine('Agua (juego de Ej. 9.3/B.3)', 5.08354,1663.125,-45.622,
                  18.0153,None,None,'Capítulo 9, ejemplo 9.3 y ejercicios B.3/C.3',5)
AGUA_2 = Antoine('Agua (juego de 9.B.5/C.6)',5.07680,1659.793,-45.854,
                  18.0153,334.,363.,'Capítulo 9, ejercicio 9.C.6',5)
TOLUENO = Antoine('Tolueno',4.07827,1343.943,-53.773,
                  92.1384,308.52,384.66,'Capítulo 9, ejemplo 9.3',5)
BENCENO = Antoine('Benceno',4.72583,1660.652,-1.461,
                  78.1118,333.4,373.5,'Capítulo 9, ejercicios B.5/C.6',4)
ANILINA = Antoine('Anilina',4.34541,1661.858,-74.048,
                  93.1265,304.,457.,'Capítulo 9, ejercicios B.4/C.3',5)
PRESETS = {'1':AGUA_1,'2':AGUA_2,'3':TOLUENO,'4':BENCENO,'5':ANILINA}


def cifras(s:str)->int:
    a=s.strip().replace(' ','').replace(',','.').lstrip('+-').lower().split('e')[0]
    digits=''.join(c for c in a if c.isdigit()).lstrip('0')
    if not digits: return 1
    if '.' not in a: digits=digits.rstrip('0') or '0'
    return len(digits)


def fmt(v:float,n:int=4)->str:
    if not math.isfinite(v): return str(v)
    if v==0: return '0'
    n=max(1,min(12,int(n)))
    magnitude=math.floor(math.log10(abs(v)))
    if magnitude>=6 or magnitude<=-5:
        return f'{v:.{n-1}e}'.replace('.',',')
    q=Decimal('1').scaleb(-(n-1-magnitude))
    return format(Decimal(str(v)).quantize(q,rounding=ROUND_HALF_UP),'f').replace('.',',')


def fmt_temperatura(t_k:float,n:int)->str:
    """°C conserva la última posición decimal de Kelvin (273,15 exacto)."""
    order=math.floor(math.log10(abs(t_k)))
    nd=max(0,n-1-order)
    q=Decimal('1').scaleb(-nd)
    kel=Decimal(str(t_k)).quantize(q,rounding=ROUND_HALF_UP)
    cel=(Decimal(str(t_k))-Decimal('273.15')).quantize(q,rounding=ROUND_HALF_UP)
    return f'{format(kel,"f").replace(".",",")} K ({format(cel,"f").replace(".",",")} °C)'


def fmt_temperatura_equilibrio(t_k:float,p_bar:float,n_presion:int,a:Antoine,b:Antoine)->str:
    """Decimales coherentes con la sensibilidad dT/dP de la ecuación implícita.

    La presión introducida tiene un último dígito de resolución ∆P; como
    T* es una raíz y no un producto, forzar a T* al mismo número de cifras
    significativas de P es incorrecto. Limitamos además la precisión de T*
    por los dígitos documentados de los coeficientes Antoine.
    Esto no presupone conocer incertidumbres estadísticas de los ajustes.
    """
    pa,pb,_=presiones(a,b,t_k)
    deriv=math.log(10)*(pa*a.b/(t_k+a.c)**2 + pb*b.b/(t_k+b.c)**2)
    step_p=10**(math.floor(math.log10(p_bar))-n_presion+1)
    if deriv<=0: raise ValueError('Presión de saturación no monótona en el intervalo.')
    delta_t=step_p/deriv
    # Resolución de presión propagada; no más de ncoef cifras en Kelvin.
    decimals_from_p=max(0,math.ceil(-math.log10(delta_t)))
    decimals_from_coeff=max(0,min(a.ncoef,b.ncoef)-1-math.floor(math.log10(t_k)))
    decimals=min(6,decimals_from_p,decimals_from_coeff)
    q=Decimal('1').scaleb(-decimals)
    kel=Decimal(str(t_k)).quantize(q,rounding=ROUND_HALF_UP)
    cel=(Decimal(str(t_k))-Decimal('273.15')).quantize(q,rounding=ROUND_HALF_UP)
    return f'{format(kel,"f").replace(".",",")} K ({format(cel,"f").replace(".",",")} °C)'


def leer_numero(prompt:str,*,minimo=None,maximo=None,estricto_min=False)->tuple[float,str]:
    while True:
        s=input(prompt).strip().replace(' ','').replace(',','.')
        try:
            d=Decimal(s)
            if not d.is_finite(): raise ValueError('No se permite NaN ni infinito.')
            x=float(d)
            if not math.isfinite(x): raise ValueError('Número demasiado grande.')
            if minimo is not None and (x<=minimo if estricto_min else x<minimo):
                raise ValueError(f'Valor fuera del límite inferior {minimo}.')
            if maximo is not None and x>maximo: raise ValueError(f'Valor mayor que {maximo}.')
            return x,s
        except (InvalidOperation,ValueError) as exc:
            print('  Dato incorrecto:',exc)


def bar(p:float,unidad:str)->float:
    f={'bar':1.0,'kpa':.01,'pa':1e-5,'atm':1.01325,'torr':1.01325/760}
    if unidad.lower() not in f: raise ValueError('Unidades: bar, kPa, Pa, atm o torr.')
    if p<=0 or not math.isfinite(p): raise ValueError('Presión estrictamente positiva.')
    return p*f[unidad.lower()]


def leer_presion()->tuple[float,int,str]:
    p,sp=leer_numero('Presión total: ',minimo=0,estricto_min=True)
    u=input('Unidad [kPa/bar/Pa/atm/torr] (kPa): ').strip().lower() or 'kpa'
    return bar(p,u),cifras(sp),sp


def check_rango(a:Antoine,b:Antoine,t:float):
    a.comprobar_validez(t);b.comprobar_validez(t)


def presiones(a:Antoine,b:Antoine,t:float)->tuple[float,float,float]:
    p1=a.presion_bar(t);p2=b.presion_bar(t)
    return p1,p2,p1+p2


def intervalo_comun(a:Antoine,b:Antoine,tmin:float|None=None,tmax:float|None=None):
    lo=max(v for v in (250.,a.t_min,b.t_min,tmin) if v is not None)
    hi=min(v for v in (600.,a.t_max,b.t_max,tmax) if v is not None)
    if lo>=hi: raise ValueError('No hay solapamiento de intervalos Antoine.')
    return lo,hi


@dataclass(frozen=True)
class Raiz:
    t:float
    iteraciones:int
    residual_bar:float
    cota_error_t:float


def temperatura_trifasica(a:Antoine,b:Antoine,p_bar:float,tol_k:float=1e-7,
                            iter_max:int=250,tmin=None,tmax=None)->Raiz:
    """Bisección estable con garantía de error abs(T) <= tol_K.
    Rechaza explícitamente raíces fuera de intervalos declarados.
    """
    if p_bar<=0 or not math.isfinite(p_bar): raise ValueError('Presión no válida.')
    if tol_k<=0 or not math.isfinite(tol_k): raise ValueError('Tolerancia positiva obligatoria.')
    if tol_k<1e-12: raise ValueError('Tolerancia menor que la precisión numérica fiable en K.')
    if iter_max<=0 or iter_max>100000: raise ValueError('Iteraciones permitidas: 1–100000.')
    lo,hi=intervalo_comun(a,b,tmin,tmax)
    def resid(t):return sum((a.presion_bar(t),b.presion_bar(t)))-p_bar
    fl=resid(lo);fh=resid(hi)
    if fl==0: return Raiz(lo,0,0.,0.)
    if fh==0: return Raiz(hi,0,0.,0.)
    if fl*fh>0:
        raise ValueError('No hay raíz en el intervalo de validez común. '
                         f'R({lo:g} K)={fl:g} bar; R({hi:g} K)={fh:g} bar. '
                         'Introduzca otra correlación válida; no se extrapola.')
    mid=lo
    for it in range(1,iter_max+1):
        mid=(lo+hi)/2
        fm=resid(mid)
        if fm==0: return Raiz(mid,it,0.,0.)
        if fl*fm<=0: hi=mid
        else: lo=mid;fl=fm
        if (hi-lo)/2<=tol_k:
            mid=(lo+hi)/2
            return Raiz(mid,it,resid(mid),(hi-lo)/2)
    raise ValueError(f'Sin convergencia en {iter_max} iteraciones, '
                     f'cota pendiente {(hi-lo)/2:g} K (tolerancia {tol_k:g} K).')


def composicion_vapor(a:Antoine,b:Antoine,t:float,p_bar:float|None=None)->dict:
    pa,pb,p=presiones(a,b,t)
    if p_bar is not None and abs(p-p_bar)>max(1e-7,p_bar*1e-6):
        raise ValueError('La presión introducida no coincide con la presión de saturación conjunta.')
    ya=pa/p;yb=pb/p
    wa=ya*a.m/(ya*a.m+yb*b.m); wb=1-wa
    return dict(t=t,p_a=pa,p_b=pb,p=p,y_a=ya,y_b=yb,w_a=wa,w_b=wb,
                n_b_a=pb/pa,m_b_a=pb*b.m/(pa*a.m))


def vapor_desde_relacion_masica(r_b_a:float,m_a:float,m_b:float)->dict:
    if not math.isfinite(r_b_a) or r_b_a<=0 or m_a<=0 or m_b<=0:
        raise ValueError('Relación y masas molares positivas.')
    rb=r_b_a*m_a/m_b
    ya=1/(1+rb);yb=1-ya
    return dict(p_b_a=rb,y_b_a=rb,y_a=ya,y_b=yb,w_b=r_b_a/(1+r_b_a))


def consumir_fases(n_a:float,n_b:float,y_b:float)->dict:
    if not all(math.isfinite(v) for v in (n_a,n_b,y_b)) or min(n_a,n_b)<=0 or not 0<y_b<1:
        raise ValueError('Dos cantidades iniciales positivas y 0 < y_B < 1.')
    ya=1-y_b
    limite_a=n_a/ya;limite_b=n_b/y_b
    ret=min(limite_a,limite_b)
    a_rest=max(0.,n_a-ret*ya)
    b_rest=max(0.,n_b-ret*y_b)
    agotada=('ambas simultáneamente' if abs(limite_a-limite_b)<1e-10*max(limite_a,limite_b)
             else 'A (fase LA)' if limite_a<limite_b else 'B (fase LB)')
    return dict(agotada=agotada,n_v=ret,n_a_v=ret*ya,n_b_v=ret*y_b,
                n_a_residual=a_rest,n_b_residual=b_rest,
                residual_a=n_a-(a_rest+ret*ya),residual_b=n_b-(b_rest+ret*y_b))


def condensacion(n_v:float,y_b:float,m_a:float,m_b:float)->dict:
    if n_v<=0 or not math.isfinite(n_v) or not 0<=y_b<=1 or min(m_a,m_b)<=0:
        raise ValueError('Datos incompatibles con caudal positivo y fracciones físicas.')
    na=n_v*(1-y_b);nb=n_v*y_b
    # n_v en mol o kmol; las masas devueltas son g o kg respectivamente.
    ma=na*m_a;mb=nb*m_b;mt=ma+mb
    return dict(n_a=na,n_b=nb,m_a=ma,m_b=mb,m_total=mt,w_b=mb/mt,
                f_m_a=ma/mt,f_m_b=mb/mt,residual_m=mt-ma-mb)


def consumo_agua(m_org:float,r_org_agua:float)->float:
    if m_org<=0 or r_org_agua<=0 or not all(map(math.isfinite,(m_org,r_org_agua))):
        raise ValueError('La cantidad y la relación deben ser positivas.')
    return m_org/r_org_agua


def avisos_rangos(a:Antoine,b:Antoine):
    for comp in (a,b):
        if comp.t_min is None or comp.t_max is None:
            print(f'  ADVERTENCIA: no consta intervalo de validez de Antoine para {comp.nombre}; '
                  'compruébelo antes de aplicar los resultados fuera del ejemplo del libro.')


def seleccionar_componente(letra:str)->Antoine:
    print(f'\nComponente {letra}: 1 Agua (Ej. 9.3) | 2 Agua (B.5/C.6) | '
          '3 Tolueno | 4 Benceno | 5 Anilina | 6 Personalizado')
    op=input('  Opción: ').strip()
    if op in PRESETS:return PRESETS[op]
    if op!='6':raise ValueError('Componente inexistente.')
    nombre=input('Nombre: ').strip() or letra
    x,s1=leer_numero('Antoine A: ')
    y,s2=leer_numero('Antoine B (>0): ',minimo=0,estricto_min=True)
    z,s3=leer_numero('Antoine C: ')
    mm,sm=leer_numero('Masa molar (g/mol): ',minimo=0,estricto_min=True)
    low,sl=leer_numero('T min válida K (0 si no se conoce): ',minimo=0)
    high,sh=leer_numero('T max válida K (0 si no se conoce): ',minimo=0)
    if low and high and high<=low:raise ValueError('Tmax debe superar Tmin.')
    if not low or not high: low=high=None
    return Antoine(nombre,x,y,z,mm,low,high,'Datos del usuario',min(map(cifras,(s1,s2,s3,sm))))


def elegir_par():
    print('  Sistema de cálculo:')
    print('   1 Agua (Ej. 9.3) / tolueno')
    print('   2 Agua (Ej. 9.3) / anilina')
    print('   3 Agua (B.5/C.6) / benceno')
    print('   4 Agua (B.5/C.6) / tolueno')
    print('   5 Dos componentes a elegir')
    op=input('  Opción [1]: ').strip() or '1'
    if op=='1':return AGUA_1,TOLUENO
    if op=='2':return AGUA_1,ANILINA
    if op=='3':return AGUA_2,BENCENO
    if op=='4':return AGUA_2,TOLUENO
    if op=='5':return seleccionar_componente('A'),seleccionar_componente('B')
    raise ValueError('Sistema inexistente.')


def pedir_tolerancia():
    tol,st=leer_numero('Tolerancia de resolución en T (K) [introduzca p.ej. 0,000001]: ',minimo=0,estricto_min=True)
    it,si=leer_numero('Máximo de iteraciones [p.ej. 250]: ',minimo=1)
    if not float(it).is_integer():raise ValueError('Número de iteraciones entero.')
    return tol,int(it)


def pedir_grafica(base:str):
    import matplotlib.pyplot as plt
    print('  1. Mostrar | 2. PNG 300 ppp | 3. SVG vectorial | 4. PNG y SVG')
    op=input('  Destino [1]: ').strip() or '1'
    if op in ('2','3','4'):
        path=Path(input(f'  Nombre de archivo [{base}]: ').strip() or base)
        if op in ('2','4'):
            p=path.with_suffix('.png');plt.savefig(p,dpi=300,bbox_inches='tight');print('  Guardado',p.resolve())
        if op in ('3','4'):
            p=path.with_suffix('.svg');plt.savefig(p,bbox_inches='tight');print('  Guardado',p.resolve())
    else:plt.show()
    plt.close()


def grafico_presiones(a:Antoine,b:Antoine,p_bar:float,t:float):
    import matplotlib.pyplot as plt
    lo,hi=intervalo_comun(a,b)
    # Foco sobre punto de cruce, sin violar el intervalo validado.
    lo=max(lo,t-25.);hi=min(hi,t+25.)
    xs=[lo+(hi-lo)*i/500 for i in range(501)]
    pas=[a.presion_bar(x)*100 for x in xs]
    pbs=[b.presion_bar(x)*100 for x in xs]
    fig,ax=plt.subplots(figsize=(8,5.2))
    ax.plot(xs,pas,label=f'P* {a.nombre}')
    ax.plot(xs,pbs,label=f'P* {b.nombre}')
    ax.plot(xs,[u+v for u,v in zip(pas,pbs)],label='P* A + P* B')
    ax.axhline(p_bar*100,color='0.35',linestyle='--',label='P impuesta')
    ax.scatter([t],[p_bar*100],color='black',zorder=5)
    ax.annotate(f'T* = {t-273.15:.2f} °C',(t,p_bar*100),xytext=(8,12),textcoords='offset points')
    ax.set(xlabel='T (K)',ylabel='Presión (kPa)',title='Ebullición conjunta de líquidos prácticamente inmiscibles')
    from matplotlib.ticker import FuncFormatter
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v,pos:f'{v:g}'.replace('.',',')))
    ax.legend();ax.grid(alpha=.25);fig.tight_layout();pedir_grafica('presiones_inmiscibles')


def grafico_t_presion(a:Antoine,b:Antoine,pa:float,pb:float):
    import matplotlib.pyplot as plt
    rs=[]
    for i in range(101):
        p=pa+(pb-pa)*i/100
        try:
            r=temperatura_trifasica(a,b,p,1e-8)
            rs.append((100*p,r.t-273.15))
        except ValueError:
            continue
    if len(rs)<2:raise ValueError('No se puede representar un intervalo válido con los coeficientes dados.')
    fig,ax=plt.subplots(figsize=(8,5.2))
    ax.plot([r[0] for r in rs],[r[1] for r in rs])
    ax.set(xlabel='Presión total (kPa)',ylabel='T* (°C)',title='Efecto de la presión en la temperatura trifásica')
    from matplotlib.ticker import FuncFormatter
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v,pos:f'{v:g}'.replace('.',',')))
    ax.grid(alpha=.2);fig.tight_layout();pedir_grafica('temperatura_presion')


def grafico_tx(a:Antoine,b:Antoine,p_bar:float,tol:float=1e-6):
    """T–y a P constante: curvas de rocío para LA+V y LB+V.
    Para LA+V: p_A=P*(1-y_B); para LB+V: p_B=P*y_B.
    La línea trifásica es el segmento horizontal en T* (solo 0<z_B<1).
    """
    import matplotlib.pyplot as plt
    root=temperatura_trifasica(a,b,p_bar,tol)
    t=root.t
    ystar=b.presion_bar(t)/p_bar
    # Si el punto puro excede los intervalos Antoine, recortar segmento.
    ls=[(ystar*i/300) for i in range(301)]
    rs=[ystar+(1-ystar)*i/300 for i in range(301)]
    pts_left=[];pts_right=[]
    for y in ls:
        try:
            tv=a.ebullicion_puro(p_bar*(1-y))
            pts_left.append((y,tv-273.15))
        except ValueError:pass
    for y in rs:
        try:
            tv=b.ebullicion_puro(p_bar*y)
            pts_right.append((y,tv-273.15))
        except ValueError:pass
    if len(pts_left)<2 or len(pts_right)<2:
        raise ValueError('Intervalo Antoine insuficiente para dibujar las dos ramas sin extrapolar.')
    fig,ax=plt.subplots(figsize=(9,5.5))
    tstar=t-273.15
    ax.plot([u for u,v in pts_left],[v for u,v in pts_left],label=r'Frontera $L_A+V$ / $V$')
    ax.plot([u for u,v in pts_right],[v for u,v in pts_right],label=r'Frontera $L_B+V$ / $V$')
    ax.hlines(tstar,0,1,color='0.3',linestyle='--',label=r'Línea trifásica $L_A+L_B+V$')
    ax.scatter([ystar],[tstar],color='black',zorder=4)
    ax.annotate(r'$E:\ y_B^*='+f'{ystar:.4f}'.replace('.',r'{,}')+r'$',(ystar,tstar),
                xytext=(8,12),textcoords='offset points',fontsize=9)
    ax.text(.14,tstar+3,r'$L_A+V$',ha='center',fontsize=12)
    ax.text(.84,tstar+3,r'$L_B+V$',ha='center',fontsize=12)
    ax.text(.5,tstar-3,r'$L_A+L_B$',ha='center',fontsize=12)
    max_temp=max(v for _,v in pts_right+pts_left)
    ax.text(.52,tstar+.72*(max_temp-tstar),'Solo vapor',ha='center',fontsize=12)
    ax.set(xlim=(0,1),ylim=(tstar-6,max_temp+3),
           xlabel=r'Fracción molar global $z_B$ (en curva de rocío: $y_B$)',
           ylabel='Temperatura (°C)',
           title=f'Diagrama T–composición a P={p_bar*100:.3f}'.replace('.',',')+' kPa (inmiscibles)')
    from matplotlib.ticker import FuncFormatter
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v,pos:f'{v:.1f}'.replace('.',',')))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v,pos:f'{v:g}'.replace('.',',')))
    ax.grid(alpha=.19)
    ax.legend(loc='upper left',fontsize=8,framealpha=.8)
    fig.tight_layout();pedir_grafica('diagrama_inmiscibles_Tx')


def informe_eq(a:Antoine,b:Antoine,p:float,prec:int,tol:float=1e-7,itmax:int=250):
    r=temperatura_trifasica(a,b,p,tol,itmax)
    v=composicion_vapor(a,b,r.t,p)
    n=min(prec,a.ncoef,b.ncoef)
    print(f'  T* = {fmt_temperatura_equilibrio(r.t,p,prec,a,b)}')
    print(f'  p_A = {fmt(v["p_a"],n)} bar, p_B = {fmt(v["p_b"],n)} bar; '
          f'suma calculada = {fmt(v["p"],max(n,prec))} bar; '
          f'P impuesta = {fmt(p,prec)} bar.')
    print(f'  y_A = {fmt(v["y_a"],n)}, y_B = {fmt(v["y_b"],n)} (suma = 1).')
    print(f'  w_A = {fmt(v["w_a"],n)}, w_B = {fmt(v["w_b"],n)} (suma = 1).')
    print(f'  n_B/n_A (vapor) = {fmt(v["n_b_a"],n)}; '
          f'm_B/m_A = {fmt(v["m_b_a"],n)}.')
    print(f'  Iteraciones: {r.iteraciones}; cota de error <={r.cota_error_t:.2e} K; '
          f'residuo={r.residual_bar:.3e} bar.')
    avisos_rangos(a,b)
    return r,v


def main():
    while True:
        try:
            print('''\nCAPÍTULO 9 — INMISCIBLES Y ARRASTRE DE VAPOR
1  Presiones de vapor a temperatura dada (gráfica disponible)
2  Temperatura trifásica iterativa y composición del vapor (gráfica)
3  Composición a partir de una relación másica (ejercicio B.9)
4  Consumo teórico de agua para arrastre (masas y relaciones)
5  Agotamiento de las fases en destilación discontinua
6  Condensador / decantador / reflujo
7  Comparar dos presiones o sistemas (gráfica T*–P)
8  Diagrama T–composición de líquidos inmiscibles
9  Ayuda, hipótesis y validez
0  Salir''')
            op=input('Seleccione: ').strip()
            if op=='0':break
            if op=='1':
                a,b=elegir_par();t,st=leer_numero('Temperatura (K): ',minimo=0,estricto_min=True)
                pa,pb,pt=presiones(a,b,t)
                n=min(cifras(st),a.ncoef,b.ncoef)
                print(f'  P*_A={fmt(pa,n)} bar; P*_B={fmt(pb,n)} bar; '
                      f'suma={fmt(pt,n)} bar; {fmt(pt*100,n)} kPa.')
                print('  Presiones de vapor SOLO si ambas fases líquidas permanecen presentes.')
                avisos_rangos(a,b)
                if input('¿Mostrar gráfico P*(T)? [S/n]: ').strip().lower()!='n':
                    grafico_presiones(a,b,pt,t)
            elif op=='2':
                a,b=elegir_par();p,np,_=leer_presion();tol,it=pedir_tolerancia()
                r,v=informe_eq(a,b,p,np,tol,it)
                if input('¿Gráfica P*(T) y suma? [S/n]: ').strip().lower()!='n':
                    grafico_presiones(a,b,p,r.t)
            elif op=='3':
                mr,sm=leer_numero('Relación másica m_B/m_A: ',minimo=0,estricto_min=True)
                ma,sa=leer_numero('M_A (g/mol): ',minimo=0,estricto_min=True)
                mb,sb=leer_numero('M_B (g/mol): ',minimo=0,estricto_min=True)
                v=vapor_desde_relacion_masica(mr,ma,mb)
                n=min(map(cifras,(sm,sa,sb)))
                print(f'  P*_B/P*_A = n_B/n_A = y_B/y_A = {fmt(v["p_b_a"],n)}.')
                print(f'  y_B = {fmt(v["y_b"],n)}; y_A = {fmt(v["y_a"],n)}.')
                print(f'  w_B = {fmt(v["w_b"],n)}. Presiones absolutas no deducibles solo de la relación.')
            elif op=='4':
                print('  [1] Desde dos correlaciones Antoine (encuentra T*), [2] desde m_B/m_A conocido')
                sub=input('  Opción [1]: ').strip() or '1'
                if sub=='1':
                    a,b=elegir_par();p,np,_=leer_presion();tol,it=pedir_tolerancia()
                    r,v=informe_eq(a,b,p,np,tol,it)
                    ratio=v['m_b_a'];nr=min(np,a.ncoef,b.ncoef)
                elif sub=='2':
                    ratio,sr=leer_numero('Relación másica producto/agua: ',minimo=0,estricto_min=True)
                    nr=cifras(sr)
                else:raise ValueError('Opción inexistente.')
                mass,sm=leer_numero('Masa de producto B que se desea arrastrar: ',minimo=0,estricto_min=True)
                unit=input('Unidad de masa [kg]: ').strip() or 'kg'
                print(f'  Consumo teórico de agua A: {fmt(consumo_agua(mass,ratio),min(nr,cifras(sm)))} {unit}; '
                      f'consumo específico: {fmt(1/ratio,nr)} {unit}/{unit}.')
                print('  Teórico de equilibrio, no consumo real de planta.')
            elif op=='5':
                a,b=elegir_par()
                print('  [1] Calcular y_B con Antoine  [2] Introducir y_B conocido')
                sub=input('  Opción [1]: ').strip() or '1'
                if sub=='1':
                    p,np,_=leer_presion();tol,it=pedir_tolerancia()
                    r,v=informe_eq(a,b,p,np,tol,it)
                    y=v['y_b'];ny=min(np,a.ncoef,b.ncoef)
                elif sub=='2':
                    y,sy=leer_numero('Fracción molar y_B del vapor: ',minimo=0,maximo=1)
                    ny=cifras(sy)
                else:raise ValueError('Opción no reconocida.')
                if not 0<y<1: raise ValueError('Para tres fases se necesita 0 < y_B < 1.')
                na,sa=leer_numero('Cantidad inicial del líquido A: ',minimo=0,estricto_min=True)
                nb,sb=leer_numero('Cantidad inicial del líquido B: ',minimo=0,estricto_min=True)
                base=input('Unidades mol o kmol (ambos datos iguales) [mol]: ').strip() or 'mol'
                v=consumir_fases(na,nb,y);n=min(ny,cifras(sa),cifras(sb))
                print('  Primera fase agotada:',v['agotada'])
                print(f'  Vapor retirado: {fmt(v["n_v"],n)} {base}; '
                      f'A retirado: {fmt(v["n_a_v"],n)}, B retirado: {fmt(v["n_b_v"],n)} {base}.')
                print(f'  Líquido restante: A={fmt(v["n_a_residual"],n)}, '
                      f'B={fmt(v["n_b_residual"],n)} {base}.')
                print(f'  Comprobación balances (A,B) {v["residual_a"]:.2e}, {v["residual_b"]:.2e} {base}.')
                print('  Después del agotamiento ya no se aplica P = P*_A + P*_B: '
                      'cambia el régimen a L_A + V o L_B + V.')
            elif op=='6':
                n,ns=leer_numero('Caudal molar total de vapor: ',minimo=0,estricto_min=True)
                base=input('Unidad de caudal [kmol/h] (o mol/h): ').strip() or 'kmol/h'
                y,sy=leer_numero('Fracción molar de B en vapor: ',minimo=0,maximo=1)
                ma,sa=leer_numero('M_A (g/mol o kg/kmol): ',minimo=0,estricto_min=True)
                mb,sb=leer_numero('M_B (g/mol o kg/kmol): ',minimo=0,estricto_min=True)
                res=condensacion(n,y,ma,mb)
                nout=min(map(cifras,(ns,sy,sa,sb)))
                print(f'  Alimentación al condensador: n_A={fmt(res["n_a"],nout)}, '
                      f'n_B={fmt(res["n_b"],nout)} {base}.')
                if not (base.startswith('kmol') or base.startswith('mol')):
                    raise ValueError('Usar unidades de caudal molar, por ejemplo mol/h, kmol/h o mol/s.')
                mass_unit=base.replace('kmol','kg',1) if base.startswith('kmol') else base.replace('mol','g',1)
                print(f'  Masa del destilado: {fmt(res["m_total"],nout)} {mass_unit}; '
                      f'w_B (global)={fmt(res["w_b"],nout)}.')
                print('  Separación ideal en dos capas casi puras:')
                print(f'  Fase rica en A: {fmt(res["m_a"],nout)} {mass_unit}; '
                      f'orgánica/B: {fmt(res["m_b"],nout)} {mass_unit}.')
                print(f'  Porcentaje en masa de B: {fmt(100*res["f_m_b"],nout)} %.')
                print('  Si toda B vuelve a la columna: reflujo=B; retirada=A.')
                print('  Si hay solubilidad mutua apreciable, hacen falta composiciones LL de ambas fases.')
            elif op=='7':
                print('  [1] Mismo sistema, dos presiones  [2] Sistemas diferentes, presión común')
                sub=input('  Opción: ').strip()
                tol,it=pedir_tolerancia()
                if sub=='1':
                    a,b=elegir_par();p1,n1,_=leer_presion();p2,n2,_=leer_presion()
                    r1,v1=informe_eq(a,b,p1,n1,tol,it)
                    r2,v2=informe_eq(a,b,p2,n2,tol,it)
                    print(f'  Cambio de T*: {fmt(r2.t-r1.t,min(n1,n2,a.ncoef,b.ncoef))} K.')
                    if input('¿Mostrar T* frente a P? [S/n]: ').strip().lower()!='n':
                        grafico_t_presion(a,b,min(p1,p2),max(p1,p2))
                elif sub=='2':
                    p,np,_=leer_presion()
                    a,b=elegir_par();print('\n  SISTEMA 1:');r1,v1=informe_eq(a,b,p,np,tol,it)
                    c,d=elegir_par();print('\n  SISTEMA 2:');r2,v2=informe_eq(c,d,p,np,tol,it)
                    print(f'  Relación másica B/A sistema 1: {fmt(v1["m_b_a"],min(np,a.ncoef,b.ncoef))}; '
                          f'sistema 2: {fmt(v2["m_b_a"],min(np,c.ncoef,d.ncoef))}.')
                else:raise ValueError('Opción incorrecta.')
            elif op=='8':
                a,b=elegir_par();p,np,_=leer_presion();tol,it=pedir_tolerancia()
                r,v=informe_eq(a,b,p,np,tol,it)
                grafico_tx(a,b,p,tol)
            elif op=='9':
                print('''\nMODELO DEL CAPÍTULO 9 (LA/LB son fases prácticamente inmiscibles):
P = P*_A(T) + P*_B(T), y_i = P*_i / P; solo mientras coexistan LA+LB+V.
Antoine: log10(P*[bar]) = A - B/(T[K]+C). Presión SIEMPRE bar internamente.
Los límites de validez documentados se comprueban; no se extrapola a
puntos de ebullición puro fuera del rango de una correlación.
Si el libro no proporciona los límites de un juego de Antoine, se advierte;
el usuario ha de contrastarlos antes de usarlo lejos de sus ejemplos.
Punto inicial y tolerancia: bisección; el error de iteración y el residuo
se muestran por separado de las cifras significativas de los resultados.
Los cálculos completos usan valores SIN redondeo; solo se redondea al mostrar.
Se aceptan puntos o comas decimales. 500 es ambiguo: use 500. o 5,00e2
para expresar de forma inequívoca 3 cifras significativas.
Las relaciones másicas presuponen completa condensación y sin pérdidas.
El modelo no calcula eficiencias industriales reales ni transitorios térmicos.
Las gráficas PNG se exportan a 300 ppp y SVG como vectores.
El diagrama T–x usa la curva de rocío, no confunde z_B con y_B.''')
            else:print('  Opción inexistente.')
        except ImportError:
            print('  ERROR: faltan bibliotecas para dibujar. Instale: python -m pip install matplotlib')
        except (ValueError,ArithmeticError,OSError,OverflowError) as exc:
            print('  ERROR CONTROLADO:',exc)
        except (KeyboardInterrupt,EOFError):
            print('\n  Interrumpido por el usuario.');break

if __name__=='__main__':main()
