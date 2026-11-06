#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gases_reales.py
================
Herramienta de cálculo para el capítulo 5 «Propiedades de los gases reales».

Incluye
-------
* Variables reducidas Tr y Pr.
* Gas ideal como referencia.
* Ecuaciones cúbicas: van der Waals, Redlich-Kwong (RK),
  Soave-Redlich-Kwong (SRK) y Peng-Robinson (PR).
* Cálculo y clasificación de todas las raíces reales físicamente admisibles.
* Coeficientes de fugacidad de sustancia pura para vdW, RK, SRK y PR.
* Presión de saturación predicha por una ecuación cúbica imponiendo fL = fV.
* Correlación de Lee-Kesler: Z(0), Z(r), Z(1) y Z.
* Ecuación virial truncada, en presión o en volumen molar.
* Comparación de modelos para un mismo estado.
* Inventario de un recipiente: n, masa, volumen molar y densidad.
* Evaluación cuantitativa de si el gas ideal satisface un error máximo admisible.
* Gráfica opcional del criterio de idealidad empleado en el capítulo.

Criterio de idealidad
---------------------
Si se calcula cantidad de sustancia, masa o densidad a P,V,T fijados:
    epsilon = |Z - 1|
Si se calcula volumen o volumen molar a P,T,n fijados:
    epsilon = |1 - Z| / Z
La decisión depende del error máximo que indique el usuario; no se usa un
simple umbral universal de presión.

Cifras significativas
----------------------
Las entradas se leen como texto (se admite coma decimal) y se conserva su
número de cifras significativas. Salvo --sigfigs N, la salida usa un criterio
conservador basado en los datos introducidos y en la precisión de las
propiedades críticas incorporadas. Los cálculos internos nunca se redondean.

Base de datos
-------------
Tc, Pc, Vmc y omega reproducen la tabla 5.2 del capítulo para 19 sustancias.
Las ecuaciones cúbicas calculan sus propios parámetros a partir de Tc y Pc.
BWR no se usa como calculadora universal porque requiere coeficientes ajustados
experimentalmente que no proporciona la tabla; el programa explica esta
limitación mediante la opción bwr-info.

Uso
---
Sin argumentos abre un menú interactivo.
Ejemplos:

  python gases_reales.py estado --modelo pr --gas CO2 --T 300,0 --P 50,0
  python gases_reales.py comparar --gas NC4H10 --T 510 --P 26,6
  python gases_reales.py lee-kesler --gas NC4H10 --T 510 --P 26,6
  python gases_reales.py idealidad --gas N2 --T 300 --P 50 --error 5 --magnitud n --metodo comparar
  python gases_reales.py saturacion --modelo pr --gas NC4H10 --T 380

Unidades por defecto: T en K, P en bar, volumen molar en L/mol.
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from dataclasses import dataclass
from typing import Optional

R_BAR = 0.0831446261815324      # L bar mol^-1 K^-1
R_SI = 8.31446261815324         # J mol^-1 K^-1
OMEGA_REF = 0.3978

@dataclass(frozen=True)
class Num:
    value: float
    sig: Optional[int]
    raw: str = ""

@dataclass(frozen=True)
class Gas:
    key: str
    name: str
    formula: str
    Tc: float       # K
    Pc: float       # bar
    Vc: float       # cm3/mol
    omega: float
    M: Optional[float] = None   # g/mol
    note: str = ""
    db_sig: int = 3

GAS_LIST = [
    Gas("H2", "hidrógeno normal", "H₂", 33.1, 13.0, 64.5, -0.219, 2.01588, db_sig=3),
    Gas("HE", "helio", "He", 5.2, 2.3, 57.5, -0.384, 4.002602, db_sig=2),
    Gas("N2", "nitrógeno", "N₂", 126.2, 34.0, 89.4, 0.0372, 28.0134, db_sig=3),
    Gas("O2", "oxígeno", "O₂", 154.6, 50.4, 73.4, 0.0222, 31.9988, db_sig=3),
    Gas("CO", "monóxido de carbono", "CO", 132.9, 34.9, 92.2, 0.0497, 28.0101, db_sig=3),
    Gas("CO2", "dióxido de carbono", "CO₂", 304.1, 73.8, 94.1, 0.224, 44.0095, db_sig=3),
    Gas("H2O", "agua", "H₂O", 647.1, 220.6, 55.9, 0.344, 18.01528, "polar y asociada", 4),
    Gas("NH3", "amoníaco", "NH₃", 405.6, 113.6, 73.0, 0.256, 17.03052, "polar y asociada", 4),
    Gas("SO2", "dióxido de azufre", "SO₂", 430.6, 78.9, 123.8, 0.256, 64.066, "polar", 3),
    Gas("H2S", "sulfuro de hidrógeno", "H₂S", 373.1, 90.0, 98.1, 0.101, 34.0809, "polar", 3),
    Gas("CH4", "metano", "CH₄", 190.6, 46.0, 98.6, 0.0114, 16.04246, db_sig=3),
    Gas("C2H6", "etano", "C₂H₆", 305.3, 48.7, 145.8, 0.0995, 30.06904, db_sig=3),
    Gas("C3H8", "propano", "C₃H₈", 369.9, 42.5, 200.0, 0.152, 44.09562, db_sig=3),
    Gas("NC4H10", "n-butano", "n-C₄H₁₀", 425.1, 38.0, 254.9, 0.201, 58.1222, db_sig=3),
    Gas("NC5H12", "n-pentano", "n-C₅H₁₂", 469.7, 33.7, 311.5, 0.251, 72.14878, db_sig=3),
    Gas("C2H4", "etileno", "C₂H₄", 282.4, 50.4, 130.9, 0.0866, 28.05316, db_sig=3),
    Gas("C3H6", "propileno", "C₃H₆", 364.2, 45.5, 183.3, 0.146, 42.07974, db_sig=3),
    Gas("CH3OH", "metanol", "CH₃OH", 512.6, 81.0, 116.3, 0.563, 32.04186, "polar y asociada", 3),
    Gas("C2H5OH", "etanol", "C₂H₅OH", 514.7, 62.7, 168.6, 0.646, 46.06844, "polar y asociada", 3),
]
GASES = {g.key:g for g in GAS_LIST}
ALIASES = {
    "HIDROGENO":"H2", "HIDROGENONORMAL":"H2", "HELIO":"HE", "NITROGENO":"N2", "OXIGENO":"O2",
    "MONOXIDODECARBONO":"CO", "DIOXIDODECARBONO":"CO2", "AGUA":"H2O", "VAPORDEAGUA":"H2O",
    "AMONIACO":"NH3", "DIOXIDODEAZUFRE":"SO2", "SULFURODEHIDROGENO":"H2S", "METANO":"CH4",
    "ETANO":"C2H6", "PROPANO":"C3H8", "NBUTANO":"NC4H10", "BUTANO":"NC4H10", "NPENTANO":"NC5H12",
    "PENTANO":"NC5H12", "ETILENO":"C2H4", "PROPILENO":"C3H6", "METANOL":"CH3OH", "ETANOL":"C2H5OH",
}
P_FACTORS = {"pa":1e-5, "kpa":1e-2, "mpa":10.0, "bar":1.0, "atm":1.01325, "mmhg":1.01325/760.0, "torr":1.01325/760.0}
V_FACTORS_L = {"l":1.0, "ml":1e-3, "cm3":1e-3, "m3":1000.0, "m^3":1000.0}

LK_SIMPLE = dict(b1=0.1181193,b2=0.265728,b3=0.154790,b4=0.030323,c1=0.0236744,c2=0.0186984,c3=0.0,c4=0.042724,d1=0.155488e-4,d2=0.623689e-4,beta=0.65392,gamma=0.060167)
LK_REF = dict(b1=0.2026579,b2=0.331511,b3=0.027655,b4=0.203488,c1=0.0313385,c2=0.0503618,c3=0.016901,c4=0.041577,d1=0.48736e-4,d2=0.0740336e-4,beta=1.226,gamma=0.03754)


def _key(s: str) -> str:
    trans=str.maketrans({"á":"a","é":"e","í":"i","ó":"o","ú":"u","ü":"u","ñ":"n","Á":"A","É":"E","Í":"I","Ó":"O","Ú":"U","Ü":"U","Ñ":"N","₂":"2","₃":"3","₄":"4","₅":"5","₆":"6","₇":"7","₈":"8","₉":"9","₀":"0","-":""," ":"","_":""})
    return s.translate(trans).upper().replace("(","").replace(")","")


def parse_num(x: str | float | int) -> Num:
    if isinstance(x,(float,int)): return Num(float(x),None,str(x))
    raw=str(x).strip().replace("−","-")
    s=raw.replace(" ","").replace(",",".")
    try: val=float(s)
    except ValueError as exc: raise ValueError(f"No se reconoce el número: {raw!r}") from exc
    mant=re.split(r"[eE]",s)[0].lstrip("+-")
    if "." in mant:
        digits=mant.replace(".",""); stripped=digits.lstrip("0"); sig=len(stripped) if stripped else 1
    else:
        digits=mant.lstrip("0"); sig=len(digits) if digits else 1
    return Num(val,sig,raw)


def sig_min(*nums: Optional[Num], default=6) -> int:
    vals=[n.sig for n in nums if n is not None and n.sig is not None]
    return max(1,min(vals)) if vals else default


def fmt(x: float, sig: int=5, unit: str="") -> str:
    if not math.isfinite(x): s=str(x)
    elif x==0: s="0"
    else:
        ax=abs(x)
        if ax>=1e5 or ax<1e-3: s=f"{x:.{max(sig-1,0)}e}"
        else:
            places=max(sig-int(math.floor(math.log10(ax)))-1,0); s=f"{x:.{places}f}"
    s=s.replace(".",",")
    return f"{s} {unit}".rstrip()


def p_to_bar(x: Num, unit: str) -> float:
    u=unit.strip().lower().replace(" ","")
    if u not in P_FACTORS: raise ValueError(f"Unidad de presión no admitida: {unit}")
    p=x.value*P_FACTORS[u]
    if p<=0: raise ValueError("La presión absoluta debe ser positiva.")
    return p


def bar_to(p: float, unit: str) -> float:
    return p/P_FACTORS[unit.strip().lower().replace(" ","")]


def t_to_k(x: Num, unit: str) -> float:
    u=unit.strip().lower().replace("°","")
    if u in ("k","kelvin"): T=x.value
    elif u in ("c","celsius","degc"): T=x.value+273.15
    else: raise ValueError(f"Unidad de temperatura no admitida: {unit}")
    if T<=0: raise ValueError("La temperatura absoluta debe ser mayor que 0 K.")
    return T


def v_to_l(x: Num, unit: str) -> float:
    u=unit.strip().lower().replace("³","3").replace(" ","")
    if u not in V_FACTORS_L: raise ValueError(f"Unidad de volumen no admitida: {unit}")
    if x.value<=0: raise ValueError("El volumen debe ser positivo.")
    return x.value*V_FACTORS_L[u]


def resolve_gas(name: str) -> Gas:
    k=_key(name)
    if k in GASES: return GASES[k]
    k=ALIASES.get(k,"")
    if k in GASES: return GASES[k]
    raise ValueError(f"Gas {name!r} no incluido. Use 'lista-gases' o datos personalizados.")


def gas_with_overrides(name: str, Tc_s=None, Pc_s=None, omega_s=None, M_s=None) -> Gas:
    """Usa la base de datos y permite sustituir propiedades; admite gas totalmente personalizado."""
    try:
        base=resolve_gas(name)
    except ValueError:
        if Tc_s is None or Pc_s is None or omega_s is None:
            raise ValueError("Para un gas no incluido debe indicar --Tc, --Pc (bar) y --omega.")
        Tc_n=parse_num(Tc_s); Pc_n=parse_num(Pc_s); om_n=parse_num(omega_s); M_n=parse_num(M_s) if M_s is not None else None
        if Tc_n.value<=0 or Pc_n.value<=0: raise ValueError("Tc y Pc deben ser positivas.")
        dbsig=sig_min(Tc_n,Pc_n,om_n)
        return Gas(_key(name) or "CUSTOM",name,name,Tc_n.value,Pc_n.value,float('nan'),om_n.value,M_n.value if M_n else None,"datos personalizados",dbsig)
    Tc_n=parse_num(Tc_s) if Tc_s is not None else None; Pc_n=parse_num(Pc_s) if Pc_s is not None else None; om_n=parse_num(omega_s) if omega_s is not None else None; M_n=parse_num(M_s) if M_s is not None else None
    Tc=Tc_n.value if Tc_n else base.Tc; Pc=Pc_n.value if Pc_n else base.Pc; omega=om_n.value if om_n else base.omega; M=M_n.value if M_n else base.M
    if Tc<=0 or Pc<=0: raise ValueError("Tc y Pc deben ser positivas.")
    sigs=[base.db_sig]+[n.sig for n in (Tc_n,Pc_n,om_n) if n is not None and n.sig is not None]
    return Gas(base.key,base.name,base.formula,Tc,Pc,base.Vc,omega,M,base.note,min(sigs) if sigs else base.db_sig)


def real_cubic_roots(a: float,b: float,c: float,d: float) -> list[float]:
    """Raíces reales de ax^3+bx^2+cx+d=0 sin dependencias externas."""
    if abs(a)<1e-15: raise ValueError("El coeficiente cúbico no puede ser cero.")
    b,c,d=b/a,c/a,d/a
    p=c-b*b/3.0
    q=2*b**3/27.0-b*c/3.0+d
    disc=(q/2.0)**2+(p/3.0)**3
    tol=1e-13*max(1.0,abs((q/2)**2),abs((p/3)**3))
    pq_tol=1e-12*max(1.0,abs(b),abs(c),abs(d))
    def cbrt(x): return math.copysign(abs(x)**(1/3),x)
    # En una raíz triple exacta, p=q=0. La aritmética de coma flotante
    # puede dejar residuos del orden de 1e-17 y producir dos raíces casi
    # coincidentes; se colapsan explícitamente en la raíz múltiple.
    if abs(p)<=pq_tol and abs(q)<=pq_tol:
        roots=[-b/3.0]
    elif disc>tol:
        s=math.sqrt(disc); roots=[cbrt(-q/2+s)+cbrt(-q/2-s)-b/3]
    elif disc>=-tol:
        u=cbrt(-q/2); roots=[2*u-b/3,-u-b/3]
    else:
        rho=2*math.sqrt(-p/3); arg=(-q/2)/math.sqrt(-(p/3)**3); arg=max(-1,min(1,arg)); th=math.acos(arg)
        roots=[rho*math.cos((th+2*k*math.pi)/3)-b/3 for k in range(3)]
    roots=sorted(roots)
    out=[]
    for r in roots:
        if not out or abs(r-out[-1])>1e-9*max(1,abs(r)): out.append(r)
    return out


def eos_coefficients(model: str,T: float,P: float,g: Gas) -> dict:
    model=model.lower(); Tr=T/g.Tc
    if model=="vdw":
        a=27/64*R_BAR**2*g.Tc**2/g.Pc; b=R_BAR*g.Tc/(8*g.Pc)
        A=a*P/(R_BAR**2*T**2); B=b*P/(R_BAR*T)
        poly=(1.0,-(1+B),A,-A*B); alpha=1.0
    elif model=="rk":
        a=0.42748*R_BAR**2*g.Tc**2.5/g.Pc; b=0.08664*R_BAR*g.Tc/g.Pc
        A=a*P/(R_BAR**2*T**2.5); B=b*P/(R_BAR*T)
        poly=(1.0,-1.0,A-B-B*B,-A*B); alpha=1.0
    elif model=="srk":
        a=0.42747*R_BAR**2*g.Tc**2/g.Pc; b=0.08664*R_BAR*g.Tc/g.Pc
        m=0.480+1.574*g.omega-0.176*g.omega**2; alpha=(1+m*(1-math.sqrt(Tr)))**2
        A=a*alpha*P/(R_BAR**2*T**2); B=b*P/(R_BAR*T)
        poly=(1.0,-1.0,A-B-B*B,-A*B)
    elif model=="pr":
        a=0.45724*R_BAR**2*g.Tc**2/g.Pc; b=0.07780*R_BAR*g.Tc/g.Pc
        k=0.37464+1.54226*g.omega-0.26992*g.omega**2; alpha=(1+k*(1-math.sqrt(Tr)))**2
        A=a*alpha*P/(R_BAR**2*T**2); B=b*P/(R_BAR*T)
        poly=(1.0,-(1-B),A-3*B*B-2*B,-(A*B-B*B-B**3))
    else: raise ValueError("Modelo cúbico: vdw, rk, srk o pr.")
    return {"model":model,"a":a,"b":b,"A":A,"B":B,"poly":poly,"alpha":alpha}


def eos_roots(model: str,T: float,P: float,g: Gas) -> dict:
    d=eos_coefficients(model,T,P,g); roots=real_cubic_roots(*d["poly"])
    # Para las ecuaciones tratadas, Vm>b; como Z=PVm/RT y B=bP/RT, Z>B.
    phys=[z for z in roots if z>d["B"]+1e-10 and z>0]
    d["roots_all"]=roots; d["roots"]=phys
    return d


def choose_root(roots: list[float], phase: str) -> float:
    if not roots: raise ValueError("No se ha encontrado ninguna raíz real físicamente admisible.")
    phase=phase.lower()
    if phase in ("vapor","gas"): return max(roots)
    if phase in ("liquido","líquido","liquid"): return min(roots)
    if phase in ("unica","única","auto"):
        if len(roots)==1: return roots[0]
        raise ValueError("Hay varias raíces admisibles: indique --fase vapor o --fase liquido, o compare fugacidades.")
    raise ValueError("Fase admitida: vapor, liquido o auto.")


def ln_phi(model: str,z: float,A: float,B: float) -> float:
    if z<=B: raise ValueError("Raíz no admisible: Z <= B.")
    model=model.lower()
    if model=="vdw": return z-1-math.log(z-B)-A/z
    if model in ("rk","srk"):
        if abs(B)<1e-14: return 0.0
        return z-1-math.log(z-B)-(A/B)*math.log(1+B/z)
    if model=="pr":
        if abs(B)<1e-14: return 0.0
        s=math.sqrt(2)
        return z-1-math.log(z-B)-A/(2*s*B)*math.log((z+(1+s)*B)/(z+(1-s)*B))
    raise ValueError("No hay expresión de fugacidad implementada para ese modelo.")


def cubic_state(model: str,T: float,P: float,g: Gas,phase="vapor") -> dict:
    d=eos_roots(model,T,P,g); z=choose_root(d["roots"],phase)
    vm=z*R_BAR*T/P
    out={**d,"Z":z,"Vm":vm,"Tr":T/g.Tc,"Pr":P/g.Pc,"phase":phase}
    if g.M: out["rho"]=g.M/vm  # g/L = kg/m3
    out["lnphi"]=ln_phi(model,z,d["A"],d["B"]); out["phi"]=math.exp(out["lnphi"]); out["fugacity"]=out["phi"]*P
    return out


def lk_rhs(vr: float,Tr: float,c: dict) -> float:
    if vr<=0: return math.nan
    tau=1/Tr
    B=c["b1"]-c["b2"]*tau-c["b3"]*tau**2-c["b4"]*tau**3
    C=c["c1"]-c["c2"]*tau+c["c3"]*tau**3
    D=c["d1"]+c["d2"]*tau
    expo=math.exp(-c["gamma"]/vr**2)
    return 1+B/vr+C/vr**2+D/vr**5+(c["c4"]*tau**3/vr**2)*(c["beta"]+c["gamma"]/vr**2)*expo


def lk_residual(vr: float,Pr: float,Tr: float,c: dict) -> float:
    return Pr*vr/Tr-lk_rhs(vr,Tr,c)


def _log_grid(lo: float,hi: float,n: int):
    l0,l1=math.log10(lo),math.log10(hi)
    for i in range(n+1): yield 10**(l0+(l1-l0)*i/n)


def bracket_roots(func,lo: float,hi: float,n=5000) -> list[tuple[float,float]]:
    out=[]; px=None; pf=None
    for x in _log_grid(lo,hi,n):
        try: f=func(x)
        except (ValueError,OverflowError,ZeroDivisionError): f=math.nan
        if math.isfinite(f):
            if abs(f)<1e-11: out.append((x*(1-1e-8),x*(1+1e-8)))
            if px is not None and pf*f<0: out.append((px,x))
            px,pf=x,f
    # fusionar duplicados
    merged=[]
    for a,b in out:
        if not merged or a>merged[-1][1]*(1+1e-6): merged.append([a,b])
        else: merged[-1][1]=max(merged[-1][1],b)
    return [(a,b) for a,b in merged]


def bisect(func,a: float,b: float,tol=1e-12,maxiter=200) -> float:
    fa,fb=func(a),func(b)
    if abs(fa)<tol: return a
    if abs(fb)<tol: return b
    if fa*fb>0:
        # El intervalo puede proceder de un punto casi nulo.
        m=(a+b)/2
        if abs(func(m))<1e-8: return m
        raise ValueError("El intervalo numérico no encierra una raíz.")
    for _ in range(maxiter):
        m=(a+b)/2; fm=func(m)
        if abs(fm)<tol or abs(b-a)<tol*max(1,abs(m)): return m
        if fa*fm<=0: b,fb=m,fm
        else: a,fa=m,fm
    return (a+b)/2


def lk_roots(Pr: float,Tr: float,c: dict) -> list[float]:
    if Pr<=0 or Tr<=0: raise ValueError("Pr y Tr deben ser positivos.")
    ideal_guess=Tr/Pr
    hi=max(1e3,100*ideal_guess); lo=1e-4
    brackets=bracket_roots(lambda v: lk_residual(v,Pr,Tr,c),lo,hi,4500)
    roots=[]
    for a,b in brackets:
        try: r=bisect(lambda v: lk_residual(v,Pr,Tr,c),a,b)
        except ValueError: continue
        if r>0 and (not roots or all(abs(r-q)>1e-7*max(1,r) for q in roots)): roots.append(r)
    return sorted(roots)


def lee_kesler(T: float,P: float,g: Gas,phase="vapor") -> dict:
    Tr=T/g.Tc; Pr=P/g.Pc
    r0=lk_roots(Pr,Tr,LK_SIMPLE); rr=lk_roots(Pr,Tr,LK_REF)
    if not r0 or not rr: raise ValueError("Lee-Kesler no convergió para estas condiciones.")
    if phase.lower() in ("vapor","gas"): v0=max(r0); vr=max(rr)
    elif phase.lower() in ("liquido","líquido","liquid"): v0=min(r0); vr=min(rr)
    else:
        if len(r0)!=1 or len(rr)!=1: raise ValueError("Lee-Kesler presenta varias raíces: indique fase.")
        v0,vr=r0[0],rr[0]
    z0=Pr*v0/Tr; zr=Pr*vr/Tr; z1=(zr-z0)/OMEGA_REF; z=z0+g.omega*z1
    vm=z*R_BAR*T/P
    out={"Tr":Tr,"Pr":Pr,"v0":v0,"vr":vr,"roots0":r0,"rootsr":rr,"Z0":z0,"Zr":zr,"Z1":z1,"Z":z,"Vm":vm,"phase":phase}
    if g.M: out["rho"]=g.M/vm
    return out


def ideal_state(T: float,P: float,g: Gas) -> dict:
    vm=R_BAR*T/P; out={"Tr":T/g.Tc,"Pr":P/g.Pc,"Z":1.0,"Vm":vm,"rho":g.M/vm if g.M else None}
    return out


def model_state(model: str,T: float,P: float,g: Gas,phase="vapor") -> dict:
    m=model.lower()
    if m in ("ideal","gasideal"): return ideal_state(T,P,g)
    if m in ("lk","lee-kesler","leekesler"): return lee_kesler(T,P,g,phase)
    return cubic_state(m,T,P,g,phase)


def saturation_pressure(model: str,T: float,g: Gas) -> dict:
    model=model.lower()
    if model not in ("vdw","rk","srk","pr"): raise ValueError("Saturación disponible para vdw, rk, srk y pr.")
    if T>=g.Tc: raise ValueError("T debe ser inferior a Tc para una coexistencia líquido-vapor de sustancia pura.")
    def gp(P):
        d=eos_roots(model,T,P,g)
        if len(d["roots"])<3: return None
        zl,zv=min(d["roots"]),max(d["roots"])
        return ln_phi(model,zl,d["A"],d["B"])-ln_phi(model,zv,d["A"],d["B"])
    prev=None; bracket=None
    # malla logarítmica hasta justo por debajo de Pc
    for P in _log_grid(max(g.Pc*1e-7,1e-8),g.Pc*0.9999,1200):
        val=gp(P)
        if val is None or not math.isfinite(val): continue
        if prev is not None and prev[1]*val<0: bracket=(prev[0],P)
        prev=(P,val)
    if bracket is None: raise ValueError("No se pudo encerrar la presión de saturación con tres raíces y cambio de fugacidad.")
    a,b=bracket
    for _ in range(120):
        m=(a+b)/2; ga=gp(a); gm=gp(m)
        if gm is None: break
        if abs(gm)<1e-12: a=b=m; break
        if ga*gm<=0: b=m
        else: a=m
    P=(a+b)/2; d=eos_roots(model,T,P,g); zl,zv=min(d["roots"]),max(d["roots"])
    lnl=ln_phi(model,zl,d["A"],d["B"]); lnv=ln_phi(model,zv,d["A"],d["B"])
    return {"P":P,"ZL":zl,"ZV":zv,"VmL":zl*R_BAR*T/P,"VmV":zv*R_BAR*T/P,"phiL":math.exp(lnl),"phiV":math.exp(lnv),"fL":math.exp(lnl)*P,"fV":math.exp(lnv)*P}


def virial_pressure(P: float,Bp=0.0,Cp=0.0,Dp=0.0) -> float:
    return 1+Bp*P+Cp*P**2+Dp*P**3


def virial_volume(T: float,P: float,B=0.0,C=0.0,D=0.0) -> dict:
    # Z = 1 + B/Vm + C/Vm^2 + D/Vm^3; B en L/mol, C en L2/mol2, D en L3/mol3.
    def f(v): return P*v/(R_BAR*T)-(1+B/v+C/v**2+D/v**3)
    guess=R_BAR*T/P
    lo=max(1e-8,guess*1e-5); hi=max(1e3,guess*1e3)
    br=bracket_roots(f,lo,hi,4000)
    if not br: raise ValueError("No se encontró una raíz positiva para la ecuación virial truncada.")
    roots=[bisect(f,a,b) for a,b in br]
    v=max(roots)  # rama gaseosa de mayor volumen
    z=P*v/(R_BAR*T)
    return {"Vm":v,"Z":z,"roots":roots}


def ideality_error(Z: float,magnitude: str) -> float:
    if Z<=0: raise ValueError("Z debe ser positivo.")
    m=magnitude.lower()
    if m in ("n","moles","cantidad","masa","densidad","rho"):
        return abs(Z-1)
    if m in ("v","vm","volumen","volumenmolar"):
        return abs(1-Z)/Z
    raise ValueError("Magnitud: n (cantidad/masa/densidad) o v (volumen/volumen molar).")


def accepted_interval(error_fraction: float,magnitude: str) -> tuple[float,float]:
    if error_fraction<0: raise ValueError("El error máximo no puede ser negativo.")
    m=magnitude.lower()
    if m in ("n","moles","cantidad","masa","densidad","rho"):
        return max(0,1-error_fraction),1+error_fraction
    if error_fraction>=1: raise ValueError("Para volumen, el error máximo debe ser inferior al 100 %.")
    return 1/(1+error_fraction),1/(1-error_fraction)


def heuristic_warnings(T: float,P: float,g: Gas) -> list[str]:
    Tr=T/g.Tc; Pr=P/g.Pc; w=[]
    if abs(Tr-1)<0.10 and abs(Pr-1)<0.25: w.append("Estado próximo a la región crítica: Z y la densidad pueden ser muy sensibles al modelo.")
    if T<g.Tc: w.append("T < Tc: puede existir una región de coexistencia líquido-vapor; compruebe la fase y la saturación.")
    if g.note: w.append(f"{g.formula}: sustancia {g.note}; las correlaciones generalizadas/cúbicas pueden perder precisión.")
    if Pr<=0.1 and Tr>=2: w.append("Pr <= 0,1 y Tr >= 2: el gas ideal es un buen candidato de cribado, pero el criterio final debe basarse en Z y el error admitido.")
    return w


def plot_ideality(path: str,error_pct: float,magnitude: str,z_values: list[tuple[str,float]]):
    try:
        import matplotlib.pyplot as plt
        from matplotlib.ticker import FuncFormatter
    except ImportError as exc:
        raise ValueError("Para generar la gráfica instale matplotlib: pip install matplotlib") from exc
    xmax=max(20.0,error_pct*1.25,5.0); xmax=min(xmax,90.0)
    xs=[xmax*i/500 for i in range(501)]; e=[x/100 for x in xs]
    zn_min=[1-x for x in e]; zn_max=[1+x for x in e]
    zv_min=[1/(1+x) for x in e]; zv_max=[1/(1-x) if x<0.999 else math.nan for x in e]
    fig,ax=plt.subplots(figsize=(10,6))
    ax.plot(xs,zv_min,label=r"$Z_{min}=1/(1+\varepsilon_{max})$")
    ax.plot(xs,zv_max,label=r"$Z_{max}=1/(1-\varepsilon_{max})$")
    ax.plot(xs,zn_min,"--",label=r"$Z_{min}=1-\varepsilon_{max}$")
    ax.plot(xs,zn_max,"--",label=r"$Z_{max}=1+\varepsilon_{max}$")
    ax.axhline(1,linewidth=0.8,linestyle=":"); ax.axvline(error_pct,linewidth=0.8,linestyle=":")
    for label,z in z_values: ax.scatter([error_pct],[z],s=45,label=f"{label}: Z={z:.5g}")
    ax.set_xlabel(r"Error relativo máximo admisible, $\varepsilon_{max}$ (%)")
    ax.set_ylabel("Factor de compresibilidad, Z")
    ax.grid(True,alpha=0.25); ax.legend(fontsize=8,loc="best")
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x,pos: (f"{x:g}").replace(".",",")))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y,pos: (f"{y:.2f}").replace(".",",")))
    # Ajuste razonable de y para evitar que la rama 1/(1-e) aplaste el gráfico.
    vals=[v for v in zv_max if math.isfinite(v) and v<3]+zn_max+[z for _,z in z_values]
    ymin=max(0,min(zn_min+zv_min+[z for _,z in z_values])-0.05); ymax=min(3,max(vals)+0.05)
    ax.set_ylim(ymin,ymax); fig.tight_layout(); fig.savefig(path,dpi=300,bbox_inches="tight"); plt.close(fig)


def print_state(label: str,state: dict,g: Gas,sig: int):
    print(f"\n{label}")
    print("-"*58)
    print("Tr =",fmt(state["Tr"],sig)); print("Pr =",fmt(state["Pr"],sig)); print("Z  =",fmt(state["Z"],sig)); print("Vm =",fmt(state["Vm"],sig,"L mol⁻¹"))
    if state.get("rho") is not None: print("rho =",fmt(state["rho"],sig,"kg m⁻³"))
    if "roots" in state:
        print("Raíces Z admisibles:",", ".join(fmt(z,max(sig,5)) for z in state["roots"]))
        print("phi =",fmt(state["phi"],sig)); print("f =",fmt(state["fugacity"],sig,"bar"))


def list_gases():
    print(f"{'Clave':<9}{'Sustancia':<24}{'Tc/K':>9}{'Pc/bar':>10}{'Vc/cm3mol':>12}{'omega':>10}")
    for g in GAS_LIST: print(f"{g.key:<9}{g.name:<24}{g.Tc:>9.4g}{g.Pc:>10.4g}{g.Vc:>12.5g}{g.omega:>10.4g}")


def conceptual_help():
    print(r"""
AYUDA CIENTÍFICA
================
1. Variables reducidas: Tr=T/Tc y Pr=P/Pc.
2. El factor de compresibilidad se define por PV=ZnRT.
3. Raíces de ecuaciones cúbicas:
   - se descartan las que no cumplen Vm>b (equivalentemente Z>B);
   - si queda una raíz real, es la única solución volumétrica real admisible;
   - con tres raíces admisibles subcríticas, la menor es de tipo líquido,
     la mayor de tipo vapor y la intermedia es inestable;
   - la fase estable se identifica comparando fugacidades de las raíces externas.
4. Lee-Kesler calcula por separado el fluido simple y el de referencia:
      Z = Z(0) + omega Z(1)
      Z(1) = [Z(r)-Z(0)]/0,3978
   y resuelve numéricamente una ecuación implícita en volumen pseudorreducido.
5. Criterio de gas ideal:
   - cantidad/masa/densidad: error = |Z-1|;
   - volumen/volumen molar: error = |1-Z|/Z.
   La aceptación depende del error máximo especificado por el usuario.
6. Cerca del punto crítico, en coexistencia o para sustancias polares/asociadas,
   las ecuaciones cúbicas y Lee-Kesler pueden no ser métodos de referencia.
7. BWR requiere parámetros ajustados experimentalmente; no deben sustituirse
   por los parámetros a y b de las ecuaciones cúbicas.
""")


def bwr_info():
    print("""
BWR — decisión de implementación
--------------------------------
La ecuación de Benedict-Webb-Rubin original utiliza ocho parámetros ajustados
experimentalmente (A0, B0, C0, a, b, c, alpha y gamma). La tabla de propiedades
críticas del capítulo no proporciona esos ocho coeficientes para cada fluido y
sus dimensiones dependen de la forma/unidades de la ecuación empleada.

Por ello este script NO fabrica parámetros BWR a partir de Tc, Pc u omega. Para
cálculos de alta precisión debe usarse un conjunto de coeficientes publicado y
compatible con la forma exacta de BWR, o una ecuación multiparamétrica de
referencia (p. ej., datos/tablas específicos del fluido).
""")


def output_ideality(g,T,P,error_pct,magnitude,method,phase,sig,plot_path=None,z_user=None):
    emax=error_pct/100; low,high=accepted_interval(emax,magnitude)
    vals=[]
    if z_user is not None: vals=[("Z introducido",z_user)]
    elif method=="comparar":
        for m in ("vdw","rk","srk","pr","lk"):
            try: vals.append((m.upper() if m!="lk" else "Lee-Kesler",model_state(m,T,P,g,phase)["Z"]))
            except Exception as ex: vals.append((m.upper()+" (sin resultado)",math.nan))
    else:
        vals=[(method.upper() if method!="lk" else "Lee-Kesler",model_state(method,T,P,g,phase)["Z"])]
    print("\nEVALUACIÓN DE LA APROXIMACIÓN DE GAS IDEAL")
    print("="*67); print(f"Sustancia: {g.name} ({g.formula})"); print("T =",fmt(T,sig,"K")); print("P =",fmt(P,sig,"bar")); print("Tr =",fmt(T/g.Tc,sig)); print("Pr =",fmt(P/g.Pc,sig))
    magtxt="cantidad de sustancia / masa / densidad" if magnitude.lower() in ("n","moles","cantidad","masa","densidad","rho") else "volumen / volumen molar"
    print("Magnitud evaluada:",magtxt); print("Error máximo admisible:",fmt(error_pct,max(2,sig),"%")); print("Intervalo admisible de Z:",fmt(low,max(4,sig)),"a",fmt(high,max(4,sig)))
    print("\nModelo                      Z          error estimado       decisión")
    print("-"*72)
    valid=[]
    for label,z in vals:
        if not math.isfinite(z): print(f"{label:<26}{'—':>10}{'—':>20}{'sin resultado':>16}"); continue
        err=ideality_error(z,magnitude); ok=err<=emax+1e-15; valid.append((label,z,ok,err))
        print(f"{label:<26}{fmt(z,max(sig,4)):>10}{fmt(err*100,max(sig,3),'%'):>20}{('ACEPTABLE' if ok else 'NO ACEPTABLE'):>16}")
    if method=="comparar" and valid:
        oks={x[2] for x in valid}
        if len(oks)==1: print("\nConclusión de los modelos calculados:","todos satisfacen el criterio." if True in oks else "ninguno satisface el criterio.")
        else: print("\nConclusión: los modelos no conducen a la misma decisión. No es apropiado imponer un sí/no único; use datos de referencia o un modelo más adecuado.")
    for w in heuristic_warnings(T,P,g): print("ADVERTENCIA:",w)
    if plot_path:
        plot_ideality(plot_path,error_pct,magnitude,[(a,z) for a,z,_,_ in valid]); print("Gráfica guardada en:",plot_path)


def interactive():
    while True:
        print("\nGASES REALES")
        print("1. Estado con una ecuación/modelo")
        print("2. Comparar ideal, vdW, RK, SRK, PR y Lee-Kesler")
        print("3. Evaluar si puede usarse gas ideal")
        print("4. Presión de saturación por fugacidad (vdW/RK/SRK/PR)")
        print("5. Inventario de un recipiente")
        print("6. Ecuación virial")
        print("7. Lista de gases")
        print("8. Ayuda científica")
        print("9. Información sobre BWR")
        print("0. Salir")
        op=input("Opción: ").strip()
        try:
            if op=="0": return
            if op in ("1","2","3","4","5"):
                g=resolve_gas(input("Gas (clave, fórmula o nombre): ")); Tn=parse_num(input("T: ")); Tu=input("Unidad T [K]: ").strip() or "K"; T=t_to_k(Tn,Tu)
            if op in ("1","2","3","5"):
                Pn=parse_num(input("P absoluta: ")); Pu=input("Unidad P [bar]: ").strip() or "bar"; P=p_to_bar(Pn,Pu); sig=min(sig_min(Tn,Pn),g.db_sig)
            if op=="1":
                m=input("Modelo [ideal/vdw/rk/srk/pr/lk] (pr): ").strip().lower() or "pr"; phase=input("Fase [vapor/liquido/auto] (vapor): ").strip() or "vapor"; print_state(m.upper(),model_state(m,T,P,g,phase),g,sig)
            elif op=="2":
                phase=input("Fase [vapor/liquido] (vapor): ").strip() or "vapor"
                for m in ("ideal","vdw","rk","srk","pr","lk"):
                    try: print_state(m.upper(),model_state(m,T,P,g,phase),g,sig)
                    except Exception as e: print(f"{m.upper()}: {e}")
            elif op=="3":
                err=parse_num(input("Error relativo máximo admisible (%): ")); mag=input("Magnitud [n=cantidad/masa/densidad, v=volumen] (n): ").strip() or "n"; method=input("Método de Z [vdw/rk/srk/pr/lk/comparar] (comparar): ").strip().lower() or "comparar"; phase=input("Fase [vapor/liquido] (vapor): ").strip() or "vapor"; path=input("PNG de la gráfica (vacío = no generar): ").strip() or None
                output_ideality(g,T,P,err.value,mag,method,phase,sig,path)
            elif op=="4":
                m=input("Modelo [vdw/rk/srk/pr] (pr): ").strip().lower() or "pr"; r=saturation_pressure(m,T,g); sig=min(Tn.sig or 6,g.db_sig); print("P* =",fmt(r['P'],sig,"bar")); print("ZL =",fmt(r['ZL'],max(sig,5))," ZV =",fmt(r['ZV'],max(sig,5))); print("Vm,L =",fmt(r['VmL'],sig,"L mol⁻¹")," Vm,V =",fmt(r['VmV'],sig,"L mol⁻¹")); print("fL =",fmt(r['fL'],sig,"bar")," fV =",fmt(r['fV'],sig,"bar"))
            elif op=="5":
                m=input("Modelo [ideal/vdw/rk/srk/pr/lk] (pr): ").strip().lower() or "pr"; phase=input("Fase [vapor/liquido] (vapor): ").strip() or "vapor"; Vn=parse_num(input("Volumen del recipiente: ")); Vu=input("Unidad V [L]: ").strip() or "L"; V=v_to_l(Vn,Vu); st=model_state(m,T,P,g,phase); n=V/st['Vm']; print_state(m.upper(),st,g,sig); print("n =",fmt(n,min(sig,Vn.sig or 99),"mol"));
                if g.M: print("m =",fmt(n*g.M/1000,min(sig,Vn.sig or 99),"kg"))
            elif op=="6": interactive_virial()
            elif op=="7": list_gases()
            elif op=="8": conceptual_help()
            elif op=="9": bwr_info()
            else: print("Opción no válida.")
        except (ValueError,ZeroDivisionError,OverflowError) as e: print("ERROR:",e)


def interactive_virial():
    form=input("Forma [presion/volumen] (volumen): ").strip().lower() or "volumen"
    Tn=parse_num(input("T / K: ")); Pn=parse_num(input("P / bar: ")); T=Tn.value; P=Pn.value
    if form.startswith("p"):
        B=parse_num(input("B' / bar^-1 [0]: ") or "0"); C=parse_num(input("C' / bar^-2 [0]: ") or "0"); D=parse_num(input("D' / bar^-3 [0]: ") or "0"); z=virial_pressure(P,B.value,C.value,D.value); print("Z =",fmt(z,sig_min(Tn,Pn,B,C,D))); print("Vm =",fmt(z*R_BAR*T/P,sig_min(Tn,Pn,B,C,D),"L mol⁻¹"))
    else:
        B=parse_num(input("B / (L mol^-1) [0]: ") or "0"); C=parse_num(input("C / (L^2 mol^-2) [0]: ") or "0"); D=parse_num(input("D / (L^3 mol^-3) [0]: ") or "0"); r=virial_volume(T,P,B.value,C.value,D.value); print("Z =",fmt(r['Z'],sig_min(Tn,Pn,B,C,D))); print("Vm =",fmt(r['Vm'],sig_min(Tn,Pn,B,C,D),"L mol⁻¹"))


def add_gas_property_args(s):
    s.add_argument("--Tc",help="Temperatura crítica personalizada, K")
    s.add_argument("--Pc",help="Presión crítica personalizada, bar")
    s.add_argument("--omega",help="Factor acéntrico personalizado")
    s.add_argument("--M",help="Masa molar personalizada, g/mol")

def common_tp(s):
    s.add_argument("--gas",required=True); s.add_argument("--T",required=True); s.add_argument("--T-unit",default="K"); s.add_argument("--P",required=True); s.add_argument("--P-unit",default="bar"); add_gas_property_args(s)


def build_parser():
    p=argparse.ArgumentParser(description="Cálculos de gases reales. Sin argumentos abre menú interactivo.",formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument("--sigfigs",type=int,default=None,help="Fuerza N cifras significativas en la salida.")
    sub=p.add_subparsers(dest="cmd")
    s=sub.add_parser("estado",help="Calcula Z, Vm, densidad, raíces y fugacidad."); common_tp(s); s.add_argument("--modelo",default="pr",choices=["ideal","vdw","rk","srk","pr","lk"]); s.add_argument("--fase",default="vapor",choices=["vapor","liquido","auto"])
    s=sub.add_parser("comparar",help="Compara todos los modelos disponibles para un estado."); common_tp(s); s.add_argument("--fase",default="vapor",choices=["vapor","liquido"])
    s=sub.add_parser("lee-kesler",help="Muestra Z(0), Z(r), Z(1) y Z."); common_tp(s); s.add_argument("--fase",default="vapor",choices=["vapor","liquido"])
    s=sub.add_parser("idealidad",help="Decide si gas ideal cumple el error máximo indicado."); common_tp(s); s.add_argument("--error",required=True,help="Error máximo admisible, en %%"); s.add_argument("--magnitud",default="n",choices=["n","v"],help="n: cantidad/masa/densidad; v: volumen/volumen molar"); s.add_argument("--metodo",default="comparar",choices=["vdw","rk","srk","pr","lk","comparar","z"]); s.add_argument("--z",help="Z introducido por el usuario si --metodo z"); s.add_argument("--fase",default="vapor",choices=["vapor","liquido"]); s.add_argument("--grafica",help="Ruta PNG opcional para la gráfica del criterio.")
    s=sub.add_parser("saturacion",help="Calcula P* imponiendo igualdad de fugacidades."); s.add_argument("--gas",required=True); s.add_argument("--T",required=True); s.add_argument("--T-unit",default="K"); s.add_argument("--modelo",default="pr",choices=["vdw","rk","srk","pr"]); add_gas_property_args(s)
    s=sub.add_parser("inventario",help="Calcula cantidad y masa en un recipiente."); common_tp(s); s.add_argument("--V",required=True); s.add_argument("--V-unit",default="L"); s.add_argument("--modelo",default="pr",choices=["ideal","vdw","rk","srk","pr","lk"]); s.add_argument("--fase",default="vapor",choices=["vapor","liquido"])
    s=sub.add_parser("virial",help="Ecuación virial truncada."); s.add_argument("--forma",default="volumen",choices=["volumen","presion"]); s.add_argument("--T",required=True); s.add_argument("--P",required=True,help="bar"); s.add_argument("--B",default="0"); s.add_argument("--C",default="0"); s.add_argument("--D",default="0")
    sub.add_parser("lista-gases",help="Muestra la tabla de sustancias incorporadas."); sub.add_parser("ayuda",help="Ayuda científica y criterios."); sub.add_parser("bwr-info",help="Explica por qué BWR no se parametriza automáticamente.")
    return p


def main(argv=None):
    parser=build_parser(); args=parser.parse_args(argv)
    if args.sigfigs is not None and args.sigfigs<1: parser.error("--sigfigs debe ser >= 1")
    if not args.cmd: interactive(); return 0
    try:
        if args.cmd=="lista-gases": list_gases(); return 0
        if args.cmd=="ayuda": conceptual_help(); return 0
        if args.cmd=="bwr-info": bwr_info(); return 0
        if args.cmd=="virial":
            Tn=parse_num(args.T); Pn=parse_num(args.P); B=parse_num(args.B); C=parse_num(args.C); D=parse_num(args.D); sig=args.sigfigs or sig_min(Tn,Pn,B,C,D)
            if Tn.value<=0 or Pn.value<=0: raise ValueError("T y P deben ser positivas.")
            if args.forma=="presion": z=virial_pressure(Pn.value,B.value,C.value,D.value); vm=z*R_BAR*Tn.value/Pn.value
            else: r=virial_volume(Tn.value,Pn.value,B.value,C.value,D.value); z,vm=r['Z'],r['Vm']
            print("Z =",fmt(z,sig)); print("Vm =",fmt(vm,sig,"L mol⁻¹")); return 0
        g=gas_with_overrides(args.gas,getattr(args,'Tc',None),getattr(args,'Pc',None),getattr(args,'omega',None),getattr(args,'M',None)); Tn=parse_num(args.T); T=t_to_k(Tn,args.T_unit)
        if args.cmd=="saturacion":
            sig=args.sigfigs or min(Tn.sig or 6,g.db_sig); r=saturation_pressure(args.modelo,T,g)
            print(f"{g.name} ({g.formula}), modelo {args.modelo.upper()}"); print("P* =",fmt(r['P'],sig,"bar")); print("ZL =",fmt(r['ZL'],max(sig,5))); print("ZV =",fmt(r['ZV'],max(sig,5))); print("Vm,L =",fmt(r['VmL'],sig,"L mol⁻¹")); print("Vm,V =",fmt(r['VmV'],sig,"L mol⁻¹")); print("phiL =",fmt(r['phiL'],max(sig,5))); print("phiV =",fmt(r['phiV'],max(sig,5))); print("fL =",fmt(r['fL'],sig,"bar")); print("fV =",fmt(r['fV'],sig,"bar")); return 0
        Pn=parse_num(args.P); P=p_to_bar(Pn,args.P_unit); sig=args.sigfigs or min(sig_min(Tn,Pn),g.db_sig)
        if args.cmd=="estado":
            st=model_state(args.modelo,T,P,g,args.fase); print_state(args.modelo.upper(),st,g,sig); [print("ADVERTENCIA:",w) for w in heuristic_warnings(T,P,g)]; return 0
        if args.cmd=="lee-kesler":
            st=lee_kesler(T,P,g,args.fase); print(f"Tr = {fmt(st['Tr'],sig)}; Pr = {fmt(st['Pr'],sig)}"); print("Z(0) =",fmt(st['Z0'],max(sig,5))); print("Z(r) =",fmt(st['Zr'],max(sig,5))); print("Z(1) =",fmt(st['Z1'],max(sig,5))); print("Z =",fmt(st['Z'],sig)); print("Vm =",fmt(st['Vm'],sig,"L mol⁻¹")); return 0
        if args.cmd=="comparar":
            print(f"\nComparación para {g.name} ({g.formula}), T={fmt(T,sig,'K')}, P={fmt(P,sig,'bar')}")
            print(f"{'Modelo':<16}{'Z':>12}{'Vm/L mol-1':>16}{'rho/kg m-3':>16}")
            print("-"*60)
            for m in ("ideal","vdw","rk","srk","pr","lk"):
                try:
                    st=model_state(m,T,P,g,args.fase); rho=st.get('rho'); print(f"{m.upper():<16}{fmt(st['Z'],max(sig,4)):>12}{fmt(st['Vm'],sig):>16}{(fmt(rho,sig) if rho is not None else '—'):>16}")
                except Exception as e: print(f"{m.upper():<16}{'—':>12}{'—':>16}{'—':>16}  ({e})")
            [print("ADVERTENCIA:",w) for w in heuristic_warnings(T,P,g)]; return 0
        if args.cmd=="idealidad":
            err=parse_num(args.error); z_user=parse_num(args.z).value if args.metodo=="z" and args.z is not None else None
            if args.metodo=="z" and z_user is None: raise ValueError("Con --metodo z debe indicar --z.")
            output_ideality(g,T,P,err.value,args.magnitud,args.metodo,args.fase,sig,args.grafica,z_user); return 0
        if args.cmd=="inventario":
            Vn=parse_num(args.V); V=v_to_l(Vn,args.V_unit); st=model_state(args.modelo,T,P,g,args.fase); n=V/st['Vm']; outsig=args.sigfigs or min(sig,Vn.sig or 99); print_state(args.modelo.upper(),st,g,sig); print("Volumen del recipiente =",fmt(V/V_FACTORS_L[args.V_unit.lower().replace('³','3')],outsig,args.V_unit)); print("n =",fmt(n,outsig,"mol"));
            if g.M: print("m =",fmt(n*g.M/1000,outsig,"kg"))
            return 0
    except (ValueError,ZeroDivisionError,OverflowError) as e:
        print("ERROR:",e,file=sys.stderr); return 2
    return 0

if __name__=="__main__":
    raise SystemExit(main())
