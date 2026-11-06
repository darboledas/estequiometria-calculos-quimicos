#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Capítulo 11 · Fundamentos de balances de materia.

Programa interactivo y utilidades importables. Python >=3.10.
El motor del balance es independiente de NumPy/SciPy. Matplotlib es opcional.
No resuelve energía, cinética ni equilibrio químico.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import json
import math
from pathlib import Path
import re
import sys
from typing import Any, Callable

VERSION = "1.0.0"
EPS = 1e-10


class ErrorBalance(ValueError):
    """Entrada inválida, modelo mal definido o solución inadmisible."""


@dataclass(frozen=True)
class Dato:
    """Número con cifras significativas declaradas, sin redondeo prematuro.

    Ejemplos: '120,0' (4 cifras); '1,20e2' (3); '120{3}' (3).
    Un entero con ceros finales sin indicación explícita se marca ambiguo.
    """
    valor: Decimal
    cifras: int | None
    texto: str = ""

    def __float__(self):
        return float(self.valor)


def dato(texto: str | int | float | Decimal | Dato, exacto: bool = False) -> Dato:
    if isinstance(texto, Dato):
        return texto
    raw = str(texto).strip().replace(' ', '').replace('−', '-')
    if not raw:
        raise ErrorBalance('Falta un valor numérico.')
    match = re.fullmatch(r'(.+?)\{([1-9][0-9]*)\}', raw)
    explicit = None
    if match:
        raw, explicit = match.group(1), int(match.group(2))
    raw = raw.replace(',', '.')
    if not re.fullmatch(r'[+-]?(?:(?:\d+(?:\.\d*)?)|(?:\.\d+))(?:[eE][+-]?\d+)?', raw):
        raise ErrorBalance(f'Número no reconocido: {texto!r}')
    try:
        v = Decimal(raw)
    except InvalidOperation as exc:
        raise ErrorBalance(f'Número no reconocido: {texto!r}') from exc
    if not v.is_finite():
        raise ErrorBalance('El número debe ser finito.')
    if exacto:
        cifras = None
    elif explicit is not None:
        cifras = explicit
    else:
        mantisa = raw.lower().split('e')[0].lstrip('+-')
        digitos = mantisa.replace('.', '')
        if v == 0:
            cifras = len(mantisa.split('.')[1]) if '.' in mantisa else None
        elif '.' not in mantisa and 'e' not in raw.lower() and mantisa.rstrip('0') != mantisa:
            cifras = None
        else:
            cifras = len(digitos.lstrip('0'))
    return Dato(v, cifras, str(texto))


def numero(x: float | Decimal, cifras: int | None, coma: bool = True) -> str:
    """Redondeo final, mitad hacia fuera de cero (modo decimal convencional)."""
    v = Decimal(str(x))
    if not v.is_finite():
        raise ErrorBalance('Resultado no finito.')
    if cifras is None:
        result = f'{v:.9g}' if isinstance(x, float) else format(v, 'g')
    elif cifras <= 0:
        raise ErrorBalance('Número de cifras significativas inválido.')
    elif v == 0:
        result = '0' if cifras == 1 else '0,' + '0' * (cifras - 1)
        return result if coma else result.replace(',', '.')
    else:
        exp = v.adjusted()
        quantum = Decimal(1).scaleb(exp - cifras + 1)
        rounded = v.quantize(quantum, rounding=ROUND_HALF_UP)
        # Notación científica cuando hay ceros terminales enteros no explícitos.
        if exp >= cifras or exp <= -4 or (quantum >= 1 and rounded == rounded.to_integral() and int(rounded) % 10 == 0):
            s = f'{rounded.scaleb(-rounded.adjusted()):f}'
            dec = cifras - 1
            s = f'{Decimal(s):.{dec}f}'
            result = f'{s}·10^{rounded.adjusted()}'
        else:
            decimals = max(0, cifras - rounded.adjusted() - 1)
            result = f'{rounded:.{decimals}f}'
    return result.replace('.', ',') if coma else result


def menor_cifra(*valores: Dato) -> int | None:
    # Los ceros estructurales (ausencia de especie o reacción) se tratan exactos.
    activos = [x for x in valores if x.valor != 0]
    cifras = [x.cifras for x in activos if x.cifras is not None]
    return min(cifras) if len(cifras) == len(activos) and cifras else None


def add_datos(*valores: Dato) -> Dato:
    """Suma/resta: conserva el orden decimal menos preciso."""
    if not valores:
        return dato('0', exacto=True)
    v = sum((x.valor for x in valores), Decimal(0))
    if any(x.cifras is None for x in valores):
        return Dato(v, None)
    orden = max(x.valor.copy_abs().adjusted() - x.cifras + 1 if x.valor else -x.cifras for x in valores)
    cifras = 1 if v == 0 else max(1, v.copy_abs().adjusted() - orden + 1)
    return Dato(v, cifras)


def mul_datos(*valores: Dato) -> Dato:
    v = Decimal(1)
    for x in valores:
        v *= x.valor
    return Dato(v, menor_cifra(*valores))


def positivo(x: float, nombre: str, admite_cero: bool = False) -> float:
    if not math.isfinite(x) or (x < 0 if admite_cero else x <= 0):
        raise ErrorBalance(f'{nombre} debe ser finito y '+('no negativo.' if admite_cero else 'positivo.'))
    return x


def fraccion(x: float, nombre: str = 'fracción') -> float:
    if not math.isfinite(x) or not 0 <= x <= 1:
        raise ErrorBalance(f'{nombre}: debe estar entre 0 y 1.')
    return x


def normaliza(fracciones: list[float], tolerancia: float = 1e-8) -> None:
    if not fracciones:
        raise ErrorBalance('Es necesario indicar componentes.')
    for i, v in enumerate(fracciones):
        fraccion(v, f'Componente {i+1}')
    if abs(sum(fracciones)-1.0) > tolerancia:
        raise ErrorBalance(f'Las fracciones suman {sum(fracciones):.9g}, no la unidad.')


def caudales_componentes(total: float, fracciones: list[float]) -> list[float]:
    positivo(total, 'caudal total', admite_cero=True)
    normaliza(fracciones)
    return [total*x for x in fracciones]


def base_masa_a_molar(masas: list[float], masas_molares: list[float]) -> dict:
    if len(masas) != len(masas_molares) or not masas:
        raise ErrorBalance('Las masas y las masas molares deben corresponder a los mismos componentes.')
    for m in masas: positivo(m, 'masa o caudal másico', admite_cero=True)
    for M in masas_molares: positivo(M, 'masa molar')
    n = [m/M for m,M in zip(masas, masas_molares)]
    mt = sum(masas); nt = sum(n)
    positivo(mt, 'masa total'); positivo(nt, 'cantidad de sustancia total')
    return {'fracciones_masicas':[m/mt for m in masas],
            'fracciones_molares':[a/nt for a in n], 'masa_molar_media': mt/nt,
            'caudales_molares': n, 'caudal_molar_total':nt}


def base_molar_a_masa(moles: list[float], masas_molares: list[float]) -> dict:
    if len(moles) != len(masas_molares) or not moles:
        raise ErrorBalance('Las cantidades y masas molares no coinciden.')
    for x in moles: positivo(x, 'cantidad molar', admite_cero=True)
    for x in masas_molares: positivo(x, 'masa molar')
    masas = [n*M for n,M in zip(moles, masas_molares)]
    r = base_masa_a_molar(masas, masas_molares)
    r['caudales_masicos'] = masas
    r['caudal_masico_total'] = sum(masas)
    return r



def base_humeda_a_seca(fracciones_humedas:list[float],indice_vapor:int)->list[float]:
    """Composición molar seca, excluyendo el componente de humedad."""
    normaliza(fracciones_humedas)
    if indice_vapor<0 or indice_vapor>=len(fracciones_humedas):
        raise ErrorBalance('Índice del componente condensable fuera de rango.')
    yh=fracciones_humedas[indice_vapor]
    if yh>=1-EPS:raise ErrorBalance('No puede definirse base seca si todo el gas es humedad.')
    return [y/(1-yh) for i,y in enumerate(fracciones_humedas) if i!=indice_vapor]


def base_seca_a_humeda(fracciones_secas:list[float],fraccion_vapor:float)->list[float]:
    """Devuelve fracciones secas convertidas a húmedas, con vapor al final."""
    normaliza(fracciones_secas)
    fraccion(fraccion_vapor,'Fracción molar de vapor')
    if fraccion_vapor>=1-EPS:raise ErrorBalance('No queda fase gaseosa seca.')
    return [y*(1-fraccion_vapor) for y in fracciones_secas]+[fraccion_vapor]


def caudal_gas(P:float, Vp:float, T:float, Z:float=1., R:float=8.31446261815324)->float:
    """P Pa; Vp m3/s; T K; R J/(mol K); devuelve mol/s."""
    for value,name in [(P,'P'),(T,'T'),(Z,'Z'),(R,'R')]: positivo(value,name)
    positivo(Vp,'caudal volumétrico',admite_cero=True)
    return P*Vp/(Z*R*T)


def convierte_volumen_gas(Vp:float,P1:float,T1:float,P2:float,T2:float,Z1:float=1.,Z2:float=1.)->float:
    """P y T absolutas; mismo caudal molar entre referencias."""
    for value,name in [(P1,'P1'),(P2,'P2'),(T1,'T1'),(T2,'T2'),(Z1,'Z1'),(Z2,'Z2')]:
        positivo(value,name)
    positivo(Vp,'caudal volumétrico',admite_cero=True)
    return Vp*(P1/P2)*(T2/T1)*(Z2/Z1)


@dataclass
class Ecuacion:
    a: list[float]
    b: float
    etiqueta: str

@dataclass
class Solucion:
    estado: str
    incognitas: list[str]
    rango: int
    rango_ampliada: int
    grados_libertad: int
    redundantes: int
    valores: dict[str,float] = field(default_factory=dict)
    libres: list[str] = field(default_factory=list)
    residuos: list[tuple[str,float]] = field(default_factory=list)
    motivo: str = ''


def resolver_lineal(incognitas: list[str], ecuaciones: list[Ecuacion],
                   tolerancia:float=1e-10) -> Solucion:
    """Gauss-Jordan con pivote parcial, rango y detección de incompatibilidad.

    Se normaliza cada fila por su máximo coeficiente para reducir problemas de
    escala. No es un análisis exhaustivo de condicionamiento numérico.
    """
    positivo(tolerancia, 'tolerancia')
    n=len(incognitas); m=len(ecuaciones)
    if not n or len(set(incognitas))!=n:
        raise ErrorBalance('Las incógnitas deben existir y tener nombres únicos.')
    if not ecuaciones:
        return Solucion('indeterminado', incognitas, 0,0,n,0,libres=list(incognitas),motivo='No hay ecuaciones.')
    for e in ecuaciones:
        if len(e.a)!=n or any(not math.isfinite(v) for v in e.a+[e.b]):
            raise ErrorBalance(f'Ecuación mal definida: {e.etiqueta}')
    mat=[]
    for e in ecuaciones:
        norma=max(max(abs(v) for v in e.a),1e-300)
        mat.append([v/norma for v in e.a] + [e.b/norma])
    row=0; pivots=[]
    for col in range(n):
        p=max(range(row,m), key=lambda r:abs(mat[r][col]), default=None)
        if p is None or abs(mat[p][col]) <= tolerancia:
            continue
        mat[row],mat[p]=mat[p],mat[row]
        piv=mat[row][col]
        mat[row]=[v/piv for v in mat[row]]
        for j in range(m):
            if j!=row and abs(mat[j][col])>0:
                k=mat[j][col]
                mat[j]=[v-k*w for v,w in zip(mat[j],mat[row])]
        pivots.append(col)
        row+=1
        if row>=m:break
    rank=len(pivots)
    bad=any(max(abs(v) for v in rr[:n])<=tolerancia and abs(rr[n])>tolerancia for rr in mat)
    rank_aug=rank+int(bad)
    data=Solucion('incompatible' if bad else ('indeterminado' if rank<n else 'unico'),
                 incognitas,rank,rank_aug,n-rank,max(0,m-rank_aug),
                 libres=[incognitas[i] for i in range(n) if i not in pivots])
    if bad:
        data.motivo='Las ecuaciones son incompatibles; no existe solución que satisfaga todas las restricciones.'
        return data
    if rank<n:
        data.motivo='Faltan especificaciones independientes. No se asignan valores arbitrarios a las variables libres.'
        return data
    x=[0.]*n
    for i,c in enumerate(pivots):x[c]=mat[i][-1]
    data.valores=dict(zip(incognitas,x))
    data.residuos=[(e.etiqueta,sum(a*v for a,v in zip(e.a,x))-e.b) for e in ecuaciones]
    return data


def mezclar_concentraciones(matriz: list[list[float]], objetivos: list[float],
                             volumen_total:float, tolerancia=1e-9)->Solucion:
    """V_j desconocidos; C_ij g/L o mol/L; V L; sum Vj=Vtotal.

    Cada fila de matriz son las concentraciones de una especie en las entradas.
    Se admite agua pura como columna de concentraciones todas cero.
    """
    positivo(volumen_total,'volumen total')
    if not matriz or len(matriz)!=len(objetivos):
        raise ErrorBalance('Indique al menos un soluto y su concentración objetivo.')
    n=len(matriz[0])
    if n<1 or any(len(r)!=n for r in matriz):
        raise ErrorBalance('Cada soluto debe tener una concentración por corriente.')
    for fila in matriz:
        for x in fila: positivo(x,'concentración de entrada',admite_cero=True)
    for x in objetivos: positivo(x,'concentración objetivo',admite_cero=True)
    eq=[Ecuacion([1.]*n,volumen_total,'volumen total')]
    eq += [Ecuacion(fila,volumen_total*y, f'soluto {i+1}') for i,(fila,y) in enumerate(zip(matriz,objetivos))]
    r=resolver_lineal([f'V_{j+1}' for j in range(n)],eq,tolerancia)
    if r.estado=='unico':
        if min(r.valores.values())< -1e-8*max(1,volumen_total):
            r.estado='no_fisico';r.motivo='Se requieren volúmenes negativos: objetivo fuera de la región de mezcla.'
        else:
            r.valores={k:max(0.,v) for k,v in r.valores.items()}
    return r


def comprobar_residuos(entradas:list[float],salidas:list[float], referencia:float,
                       incertidumbre:float|None=None)->dict:
    positivo(referencia,'referencia del residuo')
    for x in entradas+salidas:positivo(x,'caudal',admite_cero=True)
    r=sum(entradas)-sum(salidas)
    result={'residuo':r,'residuo_relativo':abs(r)/referencia,'porcentaje':100*abs(r)/referencia}
    if incertidumbre is not None:
        positivo(incertidumbre,'tolerancia de cierre',admite_cero=True)
        result['cierre_aceptable']=abs(r)<=incertidumbre
    return result


def _leer_json(ruta: str|Path)->dict:
    return json.loads(Path(ruta).read_text(encoding='utf-8'))


def _numero_cfg(c:Any)->float:
    v=float(dato(c))
    if not math.isfinite(v):raise ErrorBalance('Dato no finito.')
    return v


def resolver_red(config:dict, tolerancia:float=1e-10)->dict:
    """Red estacionaria: variables fundamentales son caudales de componente.

    Esquema JSON documentado en LEEME. `from`/`to` identifican unidades,
    null representa entorno. No admite corrientes con from==to.
    source (unidades) es generación neta conocida por componente.
    reactions (unidades): coeficientes estequiométricos y extent conocido o
    desconocido. En modo molar, extensión en mol/tiempo; en modo masa,
    coeficientes en kg de especie por unidad de avance y suma cero si el
    conjunto de componentes se declara completo.
    """
    basis=config.get('basis','mass')
    if basis not in ('mass','molar'):
        raise ErrorBalance("basis debe ser 'mass' o 'molar'.")
    comps=config.get('components',[])
    streams=config.get('streams',[])
    units=config.get('units',[])
    if not comps or not streams or not units:
        raise ErrorBalance('Se requieren components, streams y units.')
    if len(set(comps))!=len(comps) or not all(isinstance(c,str) and c for c in comps):
        raise ErrorBalance('Los nombres de componentes deben ser distintos y no vacíos.')
    ids=[str(s['id']) for s in streams]; uids=[str(u['id']) for u in units]
    if len(set(ids))!=len(ids) or len(set(uids))!=len(uids):
        raise ErrorBalance('Identificadores de corrientes/unidades duplicados.')
    if any(':' in str(v) for v in ids+comps):
        raise ErrorBalance('El carácter dos puntos está reservado para variables internas.')
    names=[f'{sid}:{c}' for sid in ids for c in comps]
    unknown_reaction=[]
    for unit in units:
        for j,reaction in enumerate(unit.get('reactions',[])):
            if reaction.get('extent') is None:
                unknown_reaction.append(f"extent:{unit['id']}:{j+1}")
    names += unknown_reaction
    idx={name:i for i,name in enumerate(names)}
    eq=[]; valor_sf=[]
    def push(terms:dict[str,float],rhs:float,label:str):
        vec=[0.]*len(names)
        for k,v in terms.items():
            vec[idx[k]]+=v
        eq.append(Ecuacion(vec,rhs,label))
    for stream in streams:
        sid=str(stream['id'])
        o=stream.get('from'); d=stream.get('to')
        if o==d or (o is None and d is None) or (o is not None and str(o) not in uids) or (d is not None and str(d) not in uids):
            raise ErrorBalance(f'Conexiones inválidas en corriente {sid}.')
        total_terms={f'{sid}:{c}':1. for c in comps}
        if stream.get('total') is not None:
            raw=dato(stream['total']); x=float(raw)
            positivo(x, f'Caudal total de {sid}',admite_cero=True)
            push(total_terms,x, f'{sid}: total')
            valor_sf.append(raw)
        fractions=stream.get('fractions',{})
        if stream.get('total') is not None and float(dato(stream['total']))==0 and fractions:
            raise ErrorBalance(f'No puede fijar composición para la corriente nula {sid}.')
        if not isinstance(fractions,dict):raise ErrorBalance('fractions debe ser objeto JSON.')
        for c,wraw in fractions.items():
            if c not in comps:raise ErrorBalance(f'Componente desconocido en corriente {sid}: {c}')
            w=float(dato(wraw));fraccion(w)
            push({f'{sid}:{cc}':(1-w if cc==c else -w) for cc in comps},0.,f'{sid}: fracción {c}')
            # Pureza declarada (w=1 o w=0) es una restricción exacta del modelo.
            if 0<w<1:valor_sf.append(dato(wraw))
        comp_flows=stream.get('component_flows',{})
        for c,value in comp_flows.items():
            if c not in comps:raise ErrorBalance(f'Componente desconocido: {c}')
            raw=dato(value);x=float(raw)
            positivo(x,f'{sid}:{c}',admite_cero=True)
            push({f'{sid}:{c}':1.},x,f'{sid}: caudal {c}')
            valor_sf.append(raw)
    for unit in units:
        uid=str(unit['id']);source=unit.get('source',{})
        if any(c not in comps for c in source):raise ErrorBalance(f'Componente ajeno al modelo en {uid}.')
        if basis=='mass' and config.get('complete_components',True) and sum(_numero_cfg(v) for v in source.values())!=0:
            if abs(sum(_numero_cfg(v) for v in source.values()))>tolerancia:
                raise ErrorBalance(f'{uid}: una generación másica neta no nula exige modelar las otras especies o usar complete_components=false.')
        reactions=unit.get('reactions',[])
        for j,r in enumerate(reactions):
            sto=r.get('stoich',{})
            if not sto or any(c not in comps for c in sto):
                raise ErrorBalance(f'Reacción incompleta en {uid}.')
            if basis=='mass' and config.get('complete_components',True) and abs(sum(_numero_cfg(v) for v in sto.values()))>tolerancia:
                raise ErrorBalance('La suma de coeficientes másicos de una reacción debe ser cero.')
        for comp in comps:
            terms={}
            for stream in streams:
                sid=str(stream['id']);name=f'{sid}:{comp}'
                if stream.get('to')==uid: terms[name]=terms.get(name,0.)+1.
                if stream.get('from')==uid:terms[name]=terms.get(name,0.)-1.
            source_value=_numero_cfg(source.get(comp,'0'))
            for j,r in enumerate(reactions):
                coefficient=_numero_cfg(r.get('stoich',{}).get(comp,'0'))
                if r.get('extent') is None:
                    key=f'extent:{uid}:{j+1}'
                    terms[key]=terms.get(key,0.)+coefficient
                else:
                    source_value+=coefficient*_numero_cfg(r['extent'])
                    valor_sf.append(dato(r['extent']))
            push(terms,-source_value,f'{uid}: balance de {comp}')
    res=resolver_lineal(names,eq,tolerancia)
    result={'estado':res.estado,'rango':res.rango,'rango_ampliada':res.rango_ampliada,
            'incognitas':len(names),'ecuaciones':len(eq),'ecuaciones_redundantes':res.redundantes,
            'grados_libertad':res.grados_libertad,'libres':res.libres,'motivo':res.motivo,
            'residuos':res.residuos, 'valores':res.valores,
            'cifras_conservadoras': menor_cifra(*valor_sf) if valor_sf else None}
    if res.estado!='unico':return result
    flows={}
    for sid in ids:
        fl={c:res.valores[f'{sid}:{c}'] for c in comps}
        total=sum(fl.values())
        if any(v < -1e-8*max(1,abs(total)) for v in fl.values()):
            result['estado']='no_fisico';result['motivo']=f'Caudal negativo en corriente {sid}.'
            return result
        fl={c:max(0,v) for c,v in fl.items()}
        total=sum(fl.values())
        flows[sid]={'total':total, 'componentes':fl,
                    'fracciones':{c:fl[c]/total for c in comps} if total>EPS else None}
    result['corrientes']=flows
    return result

# --- Modelos de evolución temporal ---

def inventario_lineal(m0:float,entradas:list[tuple[float,float]],
                      salidas:list[tuple[float,float]],tiempo:float,n_puntos:int=101)->list[dict]:
    """Cada caudal es q(t)=q0+pendiente*t; tiempo en unidades coherentes."""
    positivo(m0,'inventario inicial',admite_cero=True)
    positivo(tiempo,'tiempo final')
    if not (2<=n_puntos<=100001):raise ErrorBalance('Número de puntos fuera de rango [2, 100001].')
    for q0,k in entradas+salidas:
        if not all(math.isfinite(x) for x in (q0,k)) or min(q0,q0+k*tiempo)<-EPS:
            raise ErrorBalance('Caudal negativo o no finito durante el intervalo.')
    qdiff=sum(q for q,k in entradas)-sum(q for q,k in salidas)
    kdiff=sum(k for q,k in entradas)-sum(k for q,k in salidas)
    rows=[]
    for j in range(n_puntos):
        t=tiempo*j/(n_puntos-1)
        m=m0+qdiff*t+.5*kdiff*t*t
        if m < -1e-8*max(m0,1):
            raise ErrorBalance('El inventario se vuelve negativo: se agota antes del tiempo final.')
        rows.append({'t':t,'inventario':max(0.,m),'acumulacion':qdiff+kdiff*t})
    # Es posible que un mínimo interior sea negativo y no coincida con la malla.
    if kdiff!=0:
        tc=-qdiff/kdiff
        if 0<tc<tiempo and m0+qdiff*tc+.5*kdiff*tc*tc<-EPS:
            raise ErrorBalance('El inventario se hace negativo entre los puntos representados.')
    return rows


def cstr_analitico(volumen:float,caudal:float,conc_inicial:float,
                   conc_entrada:float, tiempo:float,n_puntos:int=101)->list[dict]:
    """Tanque agitado, V=cte, Qin=Qout=q, soluto conservativo."""
    for x,name in [(volumen,'volumen'),(tiempo,'tiempo')]:positivo(x,name)
    for x,name in [(caudal,'caudal'),(conc_inicial,'concentración inicial'),(conc_entrada,'concentración de entrada')]:
        positivo(x,name,admite_cero=True)
    if not (2<=n_puntos<=100001):raise ErrorBalance('Número de puntos fuera de rango.')
    return [{'t':t,'volumen':volumen,
             'concentracion':conc_entrada+(conc_inicial-conc_entrada)*math.exp(-caudal*t/volumen)}
            for t in (tiempo*j/(n_puntos-1) for j in range(n_puntos))]


def _paso_rk4(f:Callable, t:float,y:tuple[float,float],h:float)->tuple[float,float]:
    k1=f(t,y)
    k2=f(t+h/2, tuple(y[i]+h*k1[i]/2 for i in range(2)))
    k3=f(t+h/2, tuple(y[i]+h*k2[i]/2 for i in range(2)))
    k4=f(t+h,tuple(y[i]+h*k3[i] for i in range(2)))
    return tuple(y[i]+h*(k1[i]+2*k2[i]+2*k3[i]+k4[i])/6 for i in range(2))


def simular_mezcla(variable:dict, tolerancia:float=1e-7,
                    max_pasos:int=100000)->list[dict]:
    """Balances de V y masa de soluto para mezcla perfectamente agitada.

    Qin(t) y Qout(t) son funciones lineales de t, expresadas como [q0,pendiente].
    dV/dt=Qin-Qout; dS/dt=Qin*Centrada-Qout*S/V+fuente_constante.
    La fuente es una velocidad prescrita de producción/consumo, no una ley cinética.
    Se emplea RK4 con dos medias etapas, rechazo y límite de pasos.
    """
    V0=float(variable['V0']);C0=float(variable['C0']);Cin=float(variable['Cin']);tf=float(variable['tf'])
    qin=[float(x) for x in variable['qin']];qout=[float(x) for x in variable['qout']]
    source=float(variable.get('source',0.))
    for x,n in [(V0,'V0'),(tf,'tf')]:positivo(x,n)
    for x,n in [(C0,'C0'),(Cin,'Cin')]:positivo(x,n,admite_cero=True)
    positivo(tolerancia,'tolerancia')
    if not (1e-12<=tolerancia<=0.01):raise ErrorBalance('Tolerancia fuera de [1e-12,0.01].')
    if not 10<=max_pasos<=2000000:raise ErrorBalance('max_pasos fuera de rango.')
    if len(qin)!=2 or len(qout)!=2:raise ErrorBalance('qin y qout requieren [q0, pendiente].')
    if not math.isfinite(source):raise ErrorBalance('Fuente no finita.')
    for q,name in [(qin,'entrada'),(qout,'salida')]:
        if min(q[0],q[0]+tf*q[1]) < -EPS:
            raise ErrorBalance(f'El caudal de {name} se vuelve negativo.')
    # El volumen es una función cuadrática conocida: inspección exacta de mínimos.
    a=qin[0]-qout[0];b=qin[1]-qout[1]
    vol=lambda t:V0+a*t+.5*b*t*t
    crit=[0,tf]
    if b!=0 and 0< -a/b<tf:crit.append(-a/b)
    if min(vol(t) for t in crit)<=0:
        raise ErrorBalance('El depósito se vacía: modelo no definido durante todo el intervalo.')
    def rhs(t,y):
        V,S=y
        if V<=0:raise ErrorBalance('Volumen no positivo durante integración.')
        qi=qin[0]+qin[1]*t; qo=qout[0]+qout[1]*t
        return (qi-qo, qi*Cin-qo*S/V+source)
    t=0.;y=(V0,V0*C0);h=tf/50;min_h=tf*1e-13
    rows=[{'t':0.,'volumen':V0,'concentracion':C0,'masa_soluto':y[1]}]
    steps=0
    while t<tf:
        steps+=1
        if steps>max_pasos:raise ErrorBalance('No se alcanzó la tolerancia en el número máximo de pasos.')
        h=min(h,tf-t)
        if h<min_h:raise ErrorBalance('Paso numérico insuficiente: posible rigidez o precisión excesiva.')
        full=_paso_rk4(rhs,t,y,h)
        mid=_paso_rk4(rhs,t,y,h/2)
        halves=_paso_rk4(rhs,t+h/2,mid,h/2)
        err=max(abs(halves[i]-full[i])/(15*max(1.,abs(y[i]),abs(halves[i]))) for i in range(2))
        if not math.isfinite(err):raise ErrorBalance('Divergencia de la integración.')
        if err<=tolerancia:
            corrected=tuple(halves[i]+(halves[i]-full[i])/15 for i in range(2))
            t+=h;y=corrected
            if y[0]<=0 or y[1]<-1e-8*max(1,y[0]*max(Cin,C0)):
                raise ErrorBalance('Concentración negativa o volumen no positivo: hipótesis físicas incompatibles.')
            # V(t) analítico evita deriva por acumulación de error de redondeo.
            y=(vol(t),max(0.,y[1]))
            rows.append({'t':t,'volumen':y[0],'concentracion':y[1]/y[0],
                         'masa_soluto':y[1]})
        h*=min(3.,max(.2, .9*(tolerancia/max(err,1e-30))**.2))
    return rows


def guardar_datos(ruta:str|Path,filas:list[dict])->Path:
    if not filas:raise ErrorBalance('No hay datos para exportar.')
    destino=Path(ruta)
    destino.parent.mkdir(parents=True,exist_ok=True)
    with destino.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(filas[0].keys()),delimiter=';')
        w.writeheader();w.writerows(filas)
    return destino


def guardar_grafica(ruta:str|Path,filas:list[dict],ykeys:list[str],titulo:str)->Path:
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise ErrorBalance('Para crear PNG se requiere matplotlib (pip install matplotlib).') from exc
    xkey='t' if 't' in filas[0] else list(filas[0])[0]
    fig,ax=plt.subplots(figsize=(8,5))
    try:
        for key in ykeys:
            if key not in filas[0]:raise ErrorBalance(f'Columna inexistente: {key}')
            ax.plot([r[xkey] for r in filas],[r[key] for r in filas],label=key)
        ax.set_title(titulo)
        ax.set_xlabel(xkey)
        ax.grid(alpha=.25)
        if len(ykeys)>1:ax.legend()
        fig.tight_layout()
        destino=Path(ruta);destino.parent.mkdir(parents=True,exist_ok=True)
        fig.savefig(destino,dpi=200)
    finally:
        plt.close(fig)
    return destino

# --- Interfaz educativa (entrada por terminal) ---

def pedir(texto:str, predeterminado:str|None=None)->str:
    suffix=f' [{predeterminado}]' if predeterminado is not None else ''
    s=input(texto+suffix+': ').strip()
    if not s and predeterminado is not None:return predeterminado
    if not s:raise ErrorBalance('No puede dejarse vacío.')
    return s


def pedir_dato(texto:str, predeterminado:str|None=None)->Dato:
    d=dato(pedir(texto,predeterminado))
    if d.cifras is None:
        if d.valor==0:return d
        n=pedir('Precisión no especificada por ceros enteros: indique cifras significativas')
        if not n.isdigit() or int(n)<1:raise ErrorBalance('Se requiere un entero positivo.')
        d=Dato(d.valor,int(n),d.texto)
    return d


def pedir_float(texto:str, predeterminado:str|None=None, cero:bool=False)->float:
    v=float(pedir_dato(texto,predeterminado))
    return positivo(v,texto,admite_cero=cero)


def pedir_lista(texto:str, n:int, cero:bool=True)->list[Dato]:
    print(texto)
    xs=[pedir_dato(f'  Dato {i+1}') for i in range(n)]
    for d in xs:positivo(float(d),'dato',admite_cero=cero)
    return xs


def imprimir_valor(etiqueta:str,v:float,cifras:int|None,unidad:str='')->None:
    print(f'  {etiqueta}: {numero(v,cifras)} {unidad}'.rstrip())
    if cifras is None:print('    [AVISO] Precisión incompleta: resultado orientativo, no redondeo certificado.')


def _guardar_si(filas:list[dict],ykeys:list[str],titulo:str)->None:
    if pedir('¿Exportar CSV con datos? s/n','n').lower()=='s':
        p=guardar_datos(pedir('Ruta archivo .csv','resultado_cap11.csv'),filas)
        print('CSV:',p)
    if pedir('¿Crear gráfica PNG? s/n','n').lower()=='s':
        p=guardar_grafica(pedir('Ruta archivo .png','grafica_cap11.png'),filas,ykeys,titulo)
        print('PNG:',p)


def menu_conversiones()->None:
    print('\n1 Másico / molar / volumétrico | 2 Composiciones | 3 Concentración x caudal')
    print('4 Caudal de gas real/ideal | 5 Cambio condiciones gas | 6 Caudal medio temporal')
    print('7 Conversión composición gaseosa húmeda/seca')
    opc=pedir('Opción')
    if opc=='1':
        q=pedir_dato('Caudal másico [kg/h]')
        rho=pedir_dato('Densidad [kg/m3]')
        MM=pedir_dato('Masa molar [kg/kmol] (pura o MEDIA para mezcla)')
        for x,n in [(rho,'Densidad'),(MM,'Masa molar')]:positivo(float(x),n)
        imprimir_valor('Caudal volumétrico',float(q)/float(rho),menor_cifra(q,rho),'m3/h')
        imprimir_valor('Caudal molar',float(q)/float(MM),menor_cifra(q,MM),'kmol/h')
    elif opc=='2':
        n=int(pedir('Número de componentes','2'))
        if not 1<=n<=50:raise ErrorBalance('Número de componentes fuera de rango.')
        c=pedir_lista('Caudal/masa de cada componente [misma unidad]',n)
        MM=pedir_lista('Masa molar de cada componente [misma unidad]',n,False)
        r=base_masa_a_molar([float(x) for x in c],[float(x) for x in MM])
        sf=menor_cifra(*(c+MM))
        for i,(w,x) in enumerate(zip(r['fracciones_masicas'],r['fracciones_molares']),1):
            imprimir_valor(f'Componente {i}, w',w,sf)
            imprimir_valor(f'Componente {i}, x',x,sf)
        imprimir_valor('Masa molar media',r['masa_molar_media'],sf,'unidad de M')
    elif opc=='3':
        c=pedir_dato('Concentración [g/L o mol/L]')
        q=pedir_dato('Caudal volumétrico [L/h]')
        imprimir_valor('Caudal del componente',float(c)*float(q),menor_cifra(c,q),'g/h o mol/h')
    elif opc=='4':
        P=pedir_dato('Presión ABSOLUTA [Pa]');V=pedir_dato('Caudal [m3/s]')
        T=pedir_dato('Temperatura ABSOLUTA [K]');Z=pedir_dato('Compresibilidad Z [1 ideal]','1,000')
        imprimir_valor('Caudal molar',caudal_gas(float(P),float(V),float(T),float(Z)),menor_cifra(*([P,V,T] if float(Z)==1 else [P,V,T,Z])),'mol/s')
    elif opc=='5':
        V=pedir_dato('Caudal inicial [m3/h]');P1=pedir_dato('Presión 1 [Pa]')
        T1=pedir_dato('Temperatura 1 [K]');P2=pedir_dato('Presión 2 [Pa]')
        T2=pedir_dato('Temperatura 2 [K]');Z1=pedir_dato('Z1','1,000');Z2=pedir_dato('Z2','1,000')
        v=convierte_volumen_gas(*(float(x) for x in [V,P1,T1,P2,T2,Z1,Z2]))
        props=[V,P1,T1,P2,T2]+([Z1] if float(Z1)!=1 else [])+([Z2] if float(Z2)!=1 else [])
        imprimir_valor('Caudal referido a condiciones 2',v,menor_cifra(*props),'m3/h')
    elif opc=='6':
        q=pedir_dato('Caudal inicial [kg/h]'); k=pedir_dato('Pendiente caudal [kg/h2]','0,00')
        t=pedir_dato('Intervalo [h]')
        av=float(q)+.5*float(k)*float(t)
        imprimir_valor('Caudal medio',av,menor_cifra(q,k,t),'kg/h')
        imprimir_valor('Masa transferida',av*float(t),menor_cifra(q,k,t),'kg')
    elif opc=='7':
        modo=pedir('Modo: 1 húmeda a seca / 2 seca a húmeda','1')
        n=int(pedir('Número de componentes secos','2'))
        if n<1 or n>50:raise ErrorBalance('Componentes fuera de rango.')
        if modo=='1':
            comp=pedir_lista('Fracciones molares de componentes secos EN GAS HÚMEDO',n)
            vapor=pedir_dato('Fracción molar de humedad EN GAS HÚMEDO')
            r=base_humeda_a_seca([float(x) for x in comp]+[float(vapor)],n)
            sf=menor_cifra(*(comp+[vapor]))
            for i,x in enumerate(r,1):imprimir_valor(f'Componente seco {i}, y seca',x,sf)
        elif modo=='2':
            comp=pedir_lista('Fracciones molares sobre BASE SECA',n)
            vapor=pedir_dato('Fracción molar de humedad en el gas húmedo')
            r=base_seca_a_humeda([float(x) for x in comp],float(vapor))
            sf=menor_cifra(*(comp+[vapor]))
            for i,x in enumerate(r[:-1],1):imprimir_valor(f'Componente {i}, y húmeda',x,sf)
            imprimir_valor('Componente humedad, y húmeda',r[-1],sf)
        else:raise ErrorBalance('Modo no reconocido.')
    else:raise ErrorBalance('Opción no reconocida.')


def menu_balance_total()->None:
    en=pedir_lista('Caudales de entrada [kg/h]',int(pedir('Número entradas','1')))
    sa=pedir_lista('Caudales de salida [kg/h]',int(pedir('Número salidas','1')))
    t=pedir_dato('Tiempo de operación [h]','1,00')
    vals=[float(x) for x in en];outs=[float(x) for x in sa]
    d=sum(vals)-sum(outs)
    sf=menor_cifra(*(en+sa))
    print('dm/dt = suma(entradas) - suma(salidas)')
    imprimir_valor('Acumulación instantánea',d,sf,'kg/h')
    imprimir_valor('Cambio en el inventario',d*float(t),menor_cifra(*(en+sa+[t])),'kg')
    m0=pedir_dato('Inventario inicial [kg]','0,00')
    imprimir_valor('Inventario final',float(m0)+d*float(t),menor_cifra(*(en+sa+[t,m0])),'kg')
    if float(m0)+d*float(t)<-EPS:raise ErrorBalance('El inventario final negativo indica agotamiento durante el intervalo.')


def menu_componente()->None:
    print('Balance de un componente: acumulación = entrada - salida + generación - consumo.')
    en=pedir_dato('Caudal del componente de entrada [kg/h o mol/h]')
    sa=pedir_dato('Caudal del componente de salida [misma unidad]')
    ge=pedir_dato('Generación [misma unidad]','0,00')
    co=pedir_dato('Consumo [misma unidad]','0,00')
    acum=float(en)-float(sa)+float(ge)-float(co)
    imprimir_valor('Acumulación',acum,menor_cifra(en,sa,ge,co),'unidad/h')
    if pedir('¿Calcular el consumo desconocido a partir de una acumulación conocida? s/n','n').lower()=='s':
        ac=pedir_dato('Acumulación conocida [misma unidad]')
        consumption=float(en)-float(sa)+float(ge)-float(ac)
        if consumption<-EPS:raise ErrorBalance('Consumo negativo: hipótesis o datos incompatibles.')
        imprimir_valor('Consumo',max(0,consumption),menor_cifra(en,sa,ge,ac),'unidad/h')


def mostrar_solucion_red(resultado:dict, unidad:str='kg/h')->None:
    print('\nESTADO:',resultado['estado'].upper())
    print('Incógnitas:',resultado['incognitas'],'| rango:',resultado['rango'],
          '| rango ampliado:',resultado['rango_ampliada'],
          '| GL:',resultado['grados_libertad'],'| ecuaciones:',resultado['ecuaciones'])
    if resultado['ecuaciones_redundantes']:
        print('Hay dependencias entre ecuaciones (o incompatibilidades si el rango ampliado crece).')
    if resultado['estado']!='unico':
        print(resultado['motivo'])
        if resultado['libres']:print('Libres:',', '.join(resultado['libres']))
        return
    sf=resultado['cifras_conservadoras']
    print('Precisión global orientativa, conservadora:',sf if sf else 'no definida')
    for sid,data in resultado['corrientes'].items():
        print(f'Corriente {sid}:')
        imprimir_valor('  Caudal total',data['total'],sf,unidad)
        for c,rate in data['componentes'].items():
            imprimir_valor('  '+c,rate,sf,unidad)
            if data['fracciones'] is not None:
                imprimir_valor('  Fracción '+c,data['fracciones'][c],sf)
    if resultado['residuos']:
        print('Residuo algebraico máximo (sin redondear):', max(abs(v) for _,v in resultado['residuos']))
    print('ADVERTENCIA: el redondeo del solucionador general es conservador;')
    print('compruebe la propagación particular de precisión si el ejercicio la exige.')


def menu_red()->None:
    print('\nSOLUCIONADOR GENERAL: red de corrientes/etapas, estacionaria.')
    print('  Puede trabajar con un JSON o crear uno de manera guiada.')
    if pedir('¿Cargar un archivo JSON? s/n','s').lower()=='s':
        ruta=pedir('Ruta al JSON del problema','ejemplos/red_mezclador.json')
        cfg=_leer_json(ruta)
    else:
        basis=pedir('Base (mass/molar)','mass')
        comps=[x.strip() for x in pedir('Componentes separados por ;','NaCl;H2O').split(';')]
        units=[{'id':pedir('Nombre de la unidad','M1')}]
        nr=int(pedir('Número de corrientes','3'))
        if nr>30 or nr<1:raise ErrorBalance('Máximo 30 corrientes en modo guiado.')
        streams=[]
        for j in range(nr):
            print(f'CORRIENTE {j+1}')
            ori=pedir('Origen (EXTERIOR o unidad)','EXTERIOR')
            dst=pedir('Destino (EXTERIOR o unidad)','M1' if ori=='EXTERIOR' else 'EXTERIOR')
            s={'id':str(j+1),'from':None if ori.upper()=='EXTERIOR' else ori,
               'to':None if dst.upper()=='EXTERIOR' else dst,'fractions':{}}
            raw=pedir('Caudal total conocido (número o ?)','?')
            if raw!='?':s['total']=raw
            for comp in comps:
                w=pedir(f'Fracción conocida de {comp} (? si no)','?')
                if w!='?':s['fractions'][comp]=w
            streams.append(s)
        cfg={'basis':basis,'components':comps,'units':units,'streams':streams}
    resultado=resolver_red(cfg)
    mostrar_solucion_red(resultado,'kg/h' if cfg.get('basis','mass')=='mass' else 'mol/h')
    if pedir('¿Guardar resultado JSON? s/n','n').lower()=='s':
        filename=Path(pedir('Ruta de salida','resultado_red.json'))
        filename.write_text(json.dumps(resultado,ensure_ascii=False,indent=2),encoding='utf-8')
        print('Guardado en',filename)


def menu_formulaciones()->None:
    nc=int(pedir('Número de solutos','2'))
    ns=int(pedir('Número de corrientes de alimentación (incluya agua)','3'))
    if nc<1 or nc>20 or ns<1 or ns>30:raise ErrorBalance('Dimensiones fuera de rango.')
    V=pedir_dato('Volumen final [L]')
    matriz=[]; targets=[]; props=[V]
    for i in range(nc):
        print(f'SOLUTO {i+1}')
        row=pedir_lista('Concentración de cada alimentación [g/L o mol/L]',ns)
        target=pedir_dato('Concentración objetivo [misma unidad]')
        matriz.append([float(x) for x in row]);targets.append(float(target));props+=row+[target]
    res=mezclar_concentraciones(matriz,targets,float(V))
    print('Estado:',res.estado,'| GL:',res.grados_libertad,'| Rango:',res.rango)
    if res.motivo:print(res.motivo)
    if res.estado=='unico':
        sf=menor_cifra(*props)
        for k,v in res.valores.items():imprimir_valor(k,v,sf,'L')
        print('Máximo residuo algebraico:',max(abs(v) for _,v in res.residuos))


def menu_transitorios()->None:
    print('1 Inventario con caudales lineales (analítico)')
    print('2 Mezcla continua con V constante (analítico)')
    print('3 Mezcla con volumen variable (RK4 adaptativo)')
    op=pedir('Opción')
    if op=='1':
        m0=pedir_float('Inventario inicial [kg]',cero=True)
        nin=int(pedir('Número de entradas','1'));nout=int(pedir('Número de salidas','1'))
        def pares(n,name):
            r=[]
            for i in range(n):
                print(f'{name} {i+1}')
                q=pedir_float('Caudal inicial [kg/h]',cero=True)
                k=float(pedir_dato('Pendiente [kg/h2]','0,00'))
                r.append((q,k))
            return r
        en=pares(nin,'Entrada');sa=pares(nout,'Salida')
        t=pedir_float('Tiempo final [h]')
        filas=inventario_lineal(m0,en,sa,t)
        imprimir_valor('Inventario final',filas[-1]['inventario'],None,'kg')
        _guardar_si(filas,['inventario'],'Inventario en el tiempo')
    elif op=='2':
        V=pedir_float('Volumen [L]');q=pedir_float('Entrada=salida [L/h]',cero=True)
        C0=pedir_float('Concentración inicial [g/L]',cero=True)
        Cin=pedir_float('Concentración de entrada [g/L]',cero=True)
        t=pedir_float('Tiempo final [h]')
        filas=cstr_analitico(V,q,C0,Cin,t)
        imprimir_valor('Concentración final',filas[-1]['concentracion'],None,'g/L')
        _guardar_si(filas,['concentracion'],'Composición en mezclador continuo')
    elif op=='3':
        cfg={'V0':pedir_float('Volumen inicial [L]'),
             'C0':pedir_float('Concentración inicial [g/L]',cero=True),
             'Cin':pedir_float('Concentración entrada [g/L]',cero=True),
             'qin':[pedir_float('Q entrada inicial [L/h]',cero=True),float(pedir_dato('Pendiente entrada [L/h2]','0,00'))],
             'qout':[pedir_float('Q salida inicial [L/h]',cero=True),float(pedir_dato('Pendiente salida [L/h2]','0,00'))],
             'source':float(pedir_dato('Generación (+) / consumo (-) de soluto [g/h]','0,00')),
             'tf':pedir_float('Tiempo final [h]')}
        tol=pedir_float('Tolerancia relativa de integración','1e-7')
        maxsteps=int(pedir('Máximo número de pasos','100000'))
        filas=simular_mezcla(cfg,tol,maxsteps)
        print('Pasos aceptados:',len(filas)-1)
        imprimir_valor('Volumen final',filas[-1]['volumen'],None,'L')
        imprimir_valor('Concentración final',filas[-1]['concentracion'],None,'g/L')
        _guardar_si(filas,['concentracion'],'Composición con caudales variables')
    else:raise ErrorBalance('Opción no reconocida.')


def menu_cierre()->None:
    n=int(pedir('Número de entradas','2')); m=int(pedir('Número de salidas','1'))
    en=pedir_lista('Caudales de entrada [misma unidad]',n)
    sa=pedir_lista('Caudales de salida [misma unidad]',m)
    q=pedir_float('Caudal de referencia positivo [misma unidad]')
    umbral=pedir_float('Tolerancia absoluta aceptable',cero=True)
    r=comprobar_residuos([float(x) for x in en],[float(x) for x in sa],q,umbral)
    sf=menor_cifra(*(en+sa))
    imprimir_valor('Residuo (entradas - salidas)',r['residuo'],sf)
    imprimir_valor('Residuo relativo (%)',r['porcentaje'],sf,'%')
    print('Cumple tolerancia declarada:', 'SÍ' if r['cierre_aceptable'] else 'NO')
    print('No confunda residuo numérico con incertidumbre de medida.')
    if pedir('¿Gráfico de comparación entradas / salidas? s/n','n').lower()=='s':
        filas=[{'corriente':i+1,'caudal':v} for i,v in enumerate([float(x) for x in en+sa])]
        # Comparación por índice de corriente (solo presentación, no figura de evolución).
        guardar_grafica(pedir('Ruta PNG','comparacion.png'),filas,['caudal'],'Caudales de corrientes')


def principal_interactivo()->int:
    print('BALANCES DE MATERIA · CAPÍTULO 11 ·',VERSION)
    print('Usar coma decimal o punto. Escribir 120{3} si 120 tiene 3 cifras significativas.')
    print('La precisión se muestra y no se redondean internamente los cálculos.')
    while True:
        print('\n1 Caudales, gases y composiciones')
        print('2 Balance total e inventario | 3 Balance de componente')
        print('4 Solucionador general de redes y grados de libertad')
        print('5 Preparación de mezclas por concentraciones')
        print('6 Acumulación, transitorios y gráficas')
        print('7 Residuos y cierre | 8 Ayuda | 0 Salir')
        try:
            op=pedir('Seleccione opción','0')
            if op=='0':break
            handlers={'1':menu_conversiones,'2':menu_balance_total,'3':menu_componente,
                      '4':menu_red,'5':menu_formulaciones,'6':menu_transitorios,'7':menu_cierre}
            if op=='8':
                print('Consulte LEEME_capitulo11.txt. Ejecute pruebas_capitulo11.py para validar.')
                print('El solucionador general no infiere reacciones ni balances de energía.')
                continue
            if op not in handlers:raise ErrorBalance('Opción desconocida.')
            handlers[op]()
        except (ErrorBalance,ValueError,ZeroDivisionError,KeyError,TypeError) as exc:
            print('\n[ERROR DE DATOS O MODELO]',exc)
        except (KeyboardInterrupt,EOFError):
            print('\nFin de la sesión.');break
    return 0


def cli()->int:
    ap=argparse.ArgumentParser(description='Capítulo 11: balances de materia; menú interactivo o JSON.')
    ap.add_argument('--red',metavar='ARCHIVO.json',help='Resuelve una red estacionaria descrita en JSON')
    ap.add_argument('--mezcla',metavar='ARCHIVO.json',help='Resuelve volúmenes de mezcla por concentraciones')
    ap.add_argument('--transitorio',metavar='ARCHIVO.json',help='Integra un depósito agitado por RK4 adaptativo')
    ap.add_argument('--tolerancia',type=float,default=1e-8,help='Tolerancia numérica')
    ap.add_argument('--max-pasos',type=int,default=100000,help='Límite de iteraciones de integración')
    ap.add_argument('--salida',help='Guardar resultado en archivo JSON o CSV (transitorios)')
    ap.add_argument('--grafica',help='Crear gráfica PNG (solo transitorios)')
    ap.add_argument('--version',action='version',version=VERSION)
    args=ap.parse_args()
    try:
        if args.red:
            resultado=resolver_red(_leer_json(args.red),args.tolerancia)
        elif args.mezcla:
            data=_leer_json(args.mezcla)
            resultado=mezclar_concentraciones(data['matriz'],data['objetivos'],data['volumen_total'],args.tolerancia)
            resultado=vars(resultado)
        elif args.transitorio:
            resultado=simular_mezcla(_leer_json(args.transitorio),args.tolerancia,args.max_pasos)
            if args.grafica:
                guardar_grafica(args.grafica,resultado,['concentracion'],'Mezcla transitoria')
        else:
            return principal_interactivo()
        if args.salida:
            if args.transitorio:guardar_datos(args.salida,resultado)
            else:Path(args.salida).write_text(json.dumps(resultado,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps(resultado,ensure_ascii=False,indent=2))
        if isinstance(resultado,dict) and resultado.get('estado') not in (None,'unico'):
            return 2
        return 0
    except (ErrorBalance,ValueError,KeyError,TypeError) as exc:
        print(f'ERROR: {exc}',file=sys.stderr);return 2

if __name__=='__main__':
    sys.exit(cli())
