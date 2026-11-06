#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gases_ideales_mezclas.py
=========================
Herramienta didáctica para el capítulo 4 «Gases ideales y mezclas gaseosas».

Funciones principales
---------------------
* Ecuación del gas ideal: resuelve P, V, n o T a partir de las otras tres.
* Ley combinada para una cantidad fija de gas.
* Conversión de presión manométrica a absoluta.
* Densidad, masa molar y gravedad específica respecto al aire.
* Teoría cinético-molecular: energía cinética media y velocidad cuadrática media.
* Mezclas ideales: fracciones molares, presiones parciales (Dalton), volúmenes
  parciales (Amagat), masa molar media, fracciones másicas, densidad y GE.
* Conversión entre composición molar/volumétrica y composición másica.
* Relaciones estequiométricas de volúmenes gaseosos a igual T y P.

Criterio de cifras significativas
---------------------------------
Los valores introducidos como texto conservan su información de cifras
significativas. Todos los dígitos escritos cuentan como significativos; si un
entero termina en cero y se desea indicar menos cifras, use notación científica
(p. ej., 3e2 en lugar de 300). Por defecto, los resultados de productos, cocientes y funciones
se presentan con el menor número de cifras significativas de los datos medidos
que intervienen. Las conversiones exactas y las constantes definidas no limitan
las cifras. Puede forzarse la salida con --sigfigs N.

Unidades internas
-----------------
P: Pa; V: m³; n: mol; T: K; masa: kg. Se aceptan varias unidades de entrada.
La presión empleada en las ecuaciones de gases debe ser absoluta.

Uso
---
Sin argumentos abre un menú interactivo.
Con argumentos, use por ejemplo:

  python gases_ideales_mezclas.py estado --P 2,50 --P-unit bar --V 10,0 --V-unit L --T 298,15 --T-unit K
  python gases_ideales_mezclas.py densidad --P 1,00 --P-unit bar --T 300 --M 44,01
  python gases_ideales_mezclas.py mezcla --componentes "CO2:10;N2:90" --base molar --P 1,20 --P-unit bar --T 300

Autoría: material complementario del manual del usuario.
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from dataclasses import dataclass
from typing import Iterable, Optional

R = 8.31446261815324          # J mol^-1 K^-1, exacta por definición de R a partir de k y NA
K_B = 1.380649e-23            # J K^-1, exacta
M_AIRE = 28.97                # g mol^-1, valor convencional usado en el capítulo

# Masas molares de especies frecuentes (g/mol). Para otras sustancias el usuario
# puede introducir M explícitamente. Los alias solo facilitan la entrada.
GASES = {
    "H2": ("H₂", 2.01588), "HE": ("He", 4.002602), "N2": ("N₂", 28.0134),
    "O2": ("O₂", 31.9988), "CO": ("CO", 28.0101), "CO2": ("CO₂", 44.0095),
    "H2O": ("H₂O", 18.01528), "NH3": ("NH₃", 17.03052), "SO2": ("SO₂", 64.066),
    "H2S": ("H₂S", 34.0809), "CH4": ("CH₄", 16.04246), "C2H6": ("C₂H₆", 30.06904),
    "C3H8": ("C₃H₈", 44.09562), "NC4H10": ("n-C₄H₁₀", 58.1222),
    "NC5H12": ("n-C₅H₁₂", 72.14878), "C2H4": ("C₂H₄", 28.05316),
    "C3H6": ("C₃H₆", 42.07974), "CH3OH": ("CH₃OH", 32.04186),
    "C2H5OH": ("C₂H₅OH", 46.06844), "CL2": ("Cl₂", 70.906),
    "HCL": ("HCl", 36.46094), "CCL4": ("CCl₄", 153.82), "SO3": ("SO₃", 80.0632),
    "CH3CHO": ("CH₃CHO", 44.05256), "C6H6": ("C₆H₆", 78.11184), "AIRE": ("aire", M_AIRE),
}

ALIASES = {
    "HIDROGENO": "H2", "HELIO": "HE", "NITROGENO": "N2", "OXIGENO": "O2",
    "MONOXIDODECARBONO": "CO", "DIOXIDODECARBONO": "CO2", "AGUA": "H2O",
    "VAPORDEAGUA": "H2O", "AMONIACO": "NH3", "DIOXIDODEAZUFRE": "SO2",
    "SULFURODEHIDROGENO": "H2S", "METANO": "CH4", "ETANO": "C2H6",
    "PROPANO": "C3H8", "NBUTANO": "NC4H10", "NPENTANO": "NC5H12",
    "ETILENO": "C2H4", "PROPILENO": "C3H6", "METANOL": "CH3OH",
    "ETANOL": "C2H5OH", "CLORO": "CL2", "CLORURODEHIDROGENO": "HCL",
    "TETRACLORURODECARBONO": "CCL4", "TETRACLOROMETANO": "CCL4",
    "TRIOXIDODEAZUFRE": "SO3", "ACETALDEHIDO": "CH3CHO", "ETANAL": "CH3CHO",
    "BENCENO": "C6H6", "AIR": "AIRE",
}

P_FACTORS = {"pa": 1.0, "kpa": 1e3, "mpa": 1e6, "bar": 1e5, "atm": 101325.0, "mmhg": 101325.0/760.0, "torr": 101325.0/760.0}
V_FACTORS = {"m3": 1.0, "m^3": 1.0, "l": 1e-3, "L": 1e-3, "ml": 1e-6, "cm3": 1e-6, "cm^3": 1e-6}
N_FACTORS = {"mol": 1.0, "kmol": 1000.0}
MASS_FACTORS = {"kg": 1.0, "g": 1e-3, "mg": 1e-6}

@dataclass(frozen=True)
class Num:
    value: float
    sig: Optional[int]
    raw: str = ""


def _ascii_key(s: str) -> str:
    trans = str.maketrans({"á":"a","é":"e","í":"i","ó":"o","ú":"u","ü":"u","ñ":"n","Á":"A","É":"E","Í":"I","Ó":"O","Ú":"U","Ü":"U","Ñ":"N","₂":"2","₃":"3","₄":"4","₅":"5","₆":"6","₇":"7","₈":"8","₉":"9","₀":"0","-":""," ":"","_":""})
    return s.translate(trans).upper().replace("(", "").replace(")", "")


def parse_num(x: str | float | int) -> Num:
    """Lee números con punto o coma decimal y deduce cifras significativas."""
    if isinstance(x, (float, int)):
        return Num(float(x), None, str(x))
    raw = str(x).strip().replace("−", "-")
    s = raw.replace(" ", "").replace(",", ".")
    try:
        value = float(s)
    except ValueError as exc:
        raise ValueError(f"No se reconoce el número: {raw!r}") from exc
    mant = re.split(r"[eE]", s)[0].lstrip("+-")
    if not mant:
        return Num(value, None, raw)
    if "." in mant:
        digits = mant.replace(".", "")
        stripped = digits.lstrip("0")
        sig = len(stripped) if stripped else 1
    else:
        digits = mant.lstrip("0")
        if not digits:
            sig = 1
        else:
            # En entrada interactiva/CLI, todos los dígitos escritos cuentan como significativos.
            # Para expresar menos cifras use notación científica (p. ej. 3e2 frente a 300).
            sig = len(digits)
    return Num(value, sig, raw)


def sig_min(*nums: Optional[Num]) -> int:
    vals = [n.sig for n in nums if n is not None and n.sig is not None]
    return max(1, min(vals)) if vals else 6


def fmt(x: float, sig: int = 6, unit: str = "", decimal_comma: bool = True) -> str:
    if not math.isfinite(x):
        s = str(x)
    elif x == 0:
        s = "0"
    else:
        ax = abs(x)
        if ax >= 1e5 or ax < 1e-3:
            s = f"{x:.{max(sig-1,0)}e}"
        else:
            places = max(sig - int(math.floor(math.log10(ax))) - 1, 0)
            s = f"{x:.{places}f}"
    if decimal_comma:
        s = s.replace(".", ",")
    return f"{s} {unit}".rstrip()


def norm_unit(u: str) -> str:
    return u.strip().replace("³", "3").replace(" ", "")


def p_to_pa(x: Num, unit: str) -> float:
    u = norm_unit(unit).lower()
    if u not in P_FACTORS:
        raise ValueError(f"Unidad de presión no admitida: {unit}")
    return x.value * P_FACTORS[u]


def pa_to(p: float, unit: str) -> float:
    u = norm_unit(unit).lower()
    return p / P_FACTORS[u]


def v_to_m3(x: Num, unit: str) -> float:
    u = norm_unit(unit)
    key = u if u in V_FACTORS else u.lower()
    if key not in V_FACTORS:
        raise ValueError(f"Unidad de volumen no admitida: {unit}")
    return x.value * V_FACTORS[key]


def m3_to(v: float, unit: str) -> float:
    u = norm_unit(unit)
    key = u if u in V_FACTORS else u.lower()
    return v / V_FACTORS[key]


def t_to_k(x: Num, unit: str) -> float:
    u = unit.strip().lower().replace("°", "")
    if u in ("k", "kelvin"):
        T = x.value
    elif u in ("c", "celsius", "degc"):
        T = x.value + 273.15
    else:
        raise ValueError(f"Unidad de temperatura no admitida: {unit}")
    if T <= 0:
        raise ValueError("La temperatura absoluta debe ser mayor que 0 K.")
    return T


def k_to_t(T: float, unit: str) -> float:
    return T if unit.strip().lower() in ("k", "kelvin") else T - 273.15


def gas_key(name: str) -> Optional[str]:
    key = _ascii_key(name)
    if key in GASES:
        return key
    return ALIASES.get(key)


def molar_mass(name: str, custom: Optional[Num] = None) -> float:
    if custom is not None:
        if custom.value <= 0:
            raise ValueError("La masa molar debe ser positiva.")
        return custom.value
    k = gas_key(name)
    if not k:
        raise ValueError(f"Gas {name!r} no incluido. Introduzca su masa molar con --M.")
    return GASES[k][1]


def solve_ideal(P: Optional[float], V: Optional[float], n: Optional[float], T: Optional[float]) -> dict:
    missing = [k for k, v in {"P":P,"V":V,"n":n,"T":T}.items() if v is None]
    if len(missing) != 1:
        raise ValueError("Debe proporcionar exactamente tres de P, V, n y T.")
    if any(v is not None and v <= 0 for v in (P,V,n,T)):
        raise ValueError("P, V, n y T deben ser positivos.")
    if P is None: P = n*R*T/V
    elif V is None: V = n*R*T/P
    elif n is None: n = P*V/(R*T)
    else: T = P*V/(n*R)
    return {"P":P,"V":V,"n":n,"T":T}


def combined_unknown(P1,V1,T1,P2,V2,T2) -> dict:
    vals = {"P1":P1,"V1":V1,"T1":T1,"P2":P2,"V2":V2,"T2":T2}
    missing=[k for k,v in vals.items() if v is None]
    if len(missing)!=1:
        raise ValueError("Debe faltar exactamente una de P1, V1, T1, P2, V2 o T2.")
    if any(v is not None and v<=0 for v in vals.values()):
        raise ValueError("Todas las magnitudes deben ser positivas en escala absoluta.")
    k=missing[0]
    if k=="P1": P1=P2*V2*T1/(V1*T2)
    elif k=="V1": V1=P2*V2*T1/(P1*T2)
    elif k=="T1": T1=P1*V1*T2/(P2*V2)
    elif k=="P2": P2=P1*V1*T2/(T1*V2)
    elif k=="V2": V2=P1*V1*T2/(T1*P2)
    else: T2=P2*V2*T1/(P1*V1)
    return {"P1":P1,"V1":V1,"T1":T1,"P2":P2,"V2":V2,"T2":T2}


def parse_components(spec: str) -> list[tuple[str, Num]]:
    out=[]
    for part in spec.split(";"):
        if not part.strip(): continue
        if ":" not in part:
            raise ValueError("Formato de componentes: 'CO2:10;N2:90'.")
        name,val=part.split(":",1)
        out.append((name.strip(), parse_num(val)))
    if not out: raise ValueError("No se han indicado componentes.")
    return out


def parse_molar_mass_map(spec: str) -> dict[str, float]:
    """Lee 'ESPECIE:M;ESPECIE:M' con M en g/mol para componentes no incluidos."""
    out: dict[str, float] = {}
    if not spec or not spec.strip():
        return out
    for part in spec.split(";"):
        if not part.strip():
            continue
        if ":" not in part:
            raise ValueError("Formato de masas molares: 'CCl4:153,82;X:50,0'.")
        name, val = part.split(":", 1)
        num = parse_num(val)
        if num.value <= 0:
            raise ValueError("Las masas molares deben ser positivas.")
        out[_ascii_key(name.strip())] = num.value
    return out


def mixture_from_basis(components: list[tuple[str, Num]], basis: str, custom_M: Optional[dict[str,float]]=None) -> list[dict]:
    """Devuelve composición en moles, masa, y, w. basis: molar, masa, presion."""
    custom_M=custom_M or {}
    basis=basis.lower()
    rows=[]
    for name,q in components:
        M=custom_M.get(_ascii_key(name))
        if M is None:
            M=molar_mass(name)
        if q.value < 0: raise ValueError("Las cantidades/composiciones no pueden ser negativas.")
        if basis in ("molar","mol","volumen","volumetrica","presion","parcial"):
            n=q.value
            m=n*M
        elif basis in ("masa","mass"):
            m=q.value
            n=m/M
        else:
            raise ValueError("Base admitida: molar, masa o presion.")
        rows.append({"name":name,"q":q,"M":M,"n":n,"m":m})
    nt=sum(r["n"] for r in rows); mt=sum(r["m"] for r in rows)
    if nt<=0 or mt<=0: raise ValueError("La suma de la composición debe ser positiva.")
    for r in rows:
        r["y"]=r["n"]/nt; r["w"]=r["m"]/mt
    return rows


def mixture_summary(rows: list[dict], P: Optional[float]=None, T: Optional[float]=None, V: Optional[float]=None) -> dict:
    Mmix=sum(r["y"]*r["M"] for r in rows)
    out={"Mmix":Mmix,"GE":Mmix/M_AIRE}
    if P is not None:
        for r in rows: r["p"]=r["y"]*P
    if V is not None:
        for r in rows: r["Vpartial"]=r["y"]*V
    if P is not None and T is not None:
        out["rho_kg_m3"]=P*(Mmix/1000)/(R*T)
        out["c_total_mol_m3"]=P/(R*T)
        for r in rows: r["c_mol_m3"]=r["y"]*P/(R*T)
    return out


def print_mixture(rows, summary, sig=5, P_unit="bar", V_unit="L"):
    print("\nANÁLISIS DE MEZCLA IDEAL")
    print("-"*79)
    head=f"{'Componente':<15}{'y_i':>11}{'w_i':>11}{'M / g mol⁻¹':>16}"
    if any("p" in r for r in rows): head += f"{'p_i / '+P_unit:>16}"
    if any("Vpartial" in r for r in rows): head += f"{'V_i / '+V_unit:>16}"
    print(head)
    for r in rows:
        line=f"{r['name']:<15}{fmt(r['y'],sig):>11}{fmt(r['w'],sig):>11}{fmt(r['M'],sig):>16}"
        if "p" in r: line += f"{fmt(pa_to(r['p'],P_unit),sig):>16}"
        if "Vpartial" in r: line += f"{fmt(m3_to(r['Vpartial'],V_unit),sig):>16}"
        print(line)
    print("-"*79)
    print("Masa molar media:", fmt(summary["Mmix"],sig,"g mol⁻¹"))
    print("Gravedad específica respecto al aire:", fmt(summary["GE"],sig))
    if "rho_kg_m3" in summary:
        print("Densidad:", fmt(summary["rho_kg_m3"],sig,"kg m⁻³"))
        print("Concentración molar total:", fmt(summary["c_total_mol_m3"],sig,"mol m⁻³"))


def menu_help():
    print("""
AYUDA RÁPIDA
============
1) Estado ideal: PV = nRT. Introduzca exactamente tres variables.
2) Ley combinada: P1 V1/T1 = P2 V2/T2, con n constante.
3) Densidad: rho = P M/(R T). Para mezclas use M_media = sum(y_i M_i).
4) GE respecto al aire = M_media/28,97 para gases ideales a igual T y P.
5) Dalton: p_i = y_i P; Amagat: V_i = y_i V.
6) Teoría cinética: <Ec> = 3 k T/2; u_rms = sqrt(3 R T/M).
7) La presión de la ecuación de gases es absoluta. Si dispone de presión
   manométrica: P_abs = P_man + P_atm.
8) En relaciones de volúmenes de reacción, los coeficientes estequiométricos
   equivalen a relaciones volumétricas solo si todos los gases se comparan a
   la misma temperatura y presión y el comportamiento es ideal.
""")


def interactive():
    while True:
        print("\nGASES IDEALES Y MEZCLAS")
        print("1. Resolver PV = nRT")
        print("2. Ley combinada entre dos estados")
        print("3. Presión manométrica -> absoluta")
        print("4. Densidad / masa molar / gravedad específica")
        print("5. Teoría cinético-molecular")
        print("6. Analizar mezcla ideal")
        print("7. Relaciones volumétricas estequiométricas")
        print("8. Lista de gases incorporados")
        print("9. Ayuda")
        print("0. Salir")
        op=input("Opción: ").strip()
        try:
            if op=="0": return
            if op=="1": interactive_state()
            elif op=="2": interactive_combined()
            elif op=="3":
                pm=parse_num(input("Presión manométrica: ")); u=input("Unidad [bar]: ").strip() or "bar"
                pa=parse_num(input("Presión atmosférica [1,01325 bar]: ") or "1,01325")
                patm_u=input(f"Unidad de P_atm [{u}]: ").strip() or u
                pabs=p_to_pa(pm,u)+p_to_pa(pa,patm_u)
                print("P absoluta =",fmt(pa_to(pabs,u),sig_min(pm,pa),u))
            elif op=="4": interactive_density()
            elif op=="5": interactive_kinetic()
            elif op=="6": interactive_mixture()
            elif op=="7": interactive_stoich_volumes()
            elif op=="8": list_gases()
            elif op=="9": menu_help()
            else: print("Opción no válida.")
        except (ValueError, ZeroDivisionError) as e:
            print("ERROR:",e)


def ask_optional(prompt: str) -> Optional[Num]:
    s=input(prompt).strip()
    return None if s=="" else parse_num(s)


def interactive_state():
    print("Deje vacía la magnitud que desea calcular.")
    Pn=ask_optional("P: "); Pu=input("Unidad de P [bar]: ").strip() or "bar"
    Vn=ask_optional("V: "); Vu=input("Unidad de V [L]: ").strip() or "L"
    nn=ask_optional("n: "); nu=input("Unidad de n [mol]: ").strip() or "mol"
    Tn=ask_optional("T: "); Tu=input("Unidad de T [K]: ").strip() or "K"
    P=p_to_pa(Pn,Pu) if Pn else None; V=v_to_m3(Vn,Vu) if Vn else None
    n=nn.value*N_FACTORS.get(nu.lower(),1) if nn else None; T=t_to_k(Tn,Tu) if Tn else None
    res=solve_ideal(P,V,n,T); sig=sig_min(Pn,Vn,nn,Tn)
    print("P =",fmt(pa_to(res['P'],Pu),sig,Pu)); print("V =",fmt(m3_to(res['V'],Vu),sig,Vu))
    print("n =",fmt(res['n']/N_FACTORS.get(nu.lower(),1),sig,nu)); print("T =",fmt(k_to_t(res['T'],Tu),sig,Tu))


def interactive_combined():
    print("Deje vacía exactamente una magnitud.")
    vals={}
    for state in (1,2):
        vals[f"P{state}n"]=ask_optional(f"P{state}: "); vals[f"P{state}u"]=input(f"Unidad P{state} [bar]: ").strip() or "bar"
        vals[f"V{state}n"]=ask_optional(f"V{state}: "); vals[f"V{state}u"]=input(f"Unidad V{state} [L]: ").strip() or "L"
        vals[f"T{state}n"]=ask_optional(f"T{state}: "); vals[f"T{state}u"]=input(f"Unidad T{state} [K]: ").strip() or "K"
    def pp(i): return p_to_pa(vals[f"P{i}n"],vals[f"P{i}u"]) if vals[f"P{i}n"] else None
    def vv(i): return v_to_m3(vals[f"V{i}n"],vals[f"V{i}u"]) if vals[f"V{i}n"] else None
    def tt(i): return t_to_k(vals[f"T{i}n"],vals[f"T{i}u"]) if vals[f"T{i}n"] else None
    r=combined_unknown(pp(1),vv(1),tt(1),pp(2),vv(2),tt(2)); sig=sig_min(*[vals[k] for k in vals if k.endswith('n')])
    for i in (1,2):
        print(f"P{i} =",fmt(pa_to(r[f'P{i}'],vals[f'P{i}u']),sig,vals[f'P{i}u']))
        print(f"V{i} =",fmt(m3_to(r[f'V{i}'],vals[f'V{i}u']),sig,vals[f'V{i}u']))
        print(f"T{i} =",fmt(k_to_t(r[f'T{i}'],vals[f'T{i}u']),sig,vals[f'T{i}u']))


def interactive_density():
    print("1) Calcular densidad; 2) Calcular masa molar; 3) Calcular GE respecto al aire")
    op=input("Opción: ").strip()
    if op=="1":
        Pn=parse_num(input("P: ")); Pu=input("Unidad [bar]: ").strip() or "bar"; Tn=parse_num(input("T: ")); Tu=input("Unidad [K]: ").strip() or "K"
        gas=input("Gas (o deje vacío si introducirá M): ").strip(); Ms=input("M / (g/mol) [vacío = buscar gas]: ").strip()
        Mn=parse_num(Ms) if Ms else None; M=molar_mass(gas,Mn); rho=p_to_pa(Pn,Pu)*(M/1000)/(R*t_to_k(Tn,Tu)); sig=sig_min(Pn,Tn,Mn)
        print("rho =",fmt(rho,sig,"kg m⁻³")); print("GE =",fmt(M/M_AIRE,sig))
    elif op=="2":
        Pn=parse_num(input("P: ")); Pu=input("Unidad [bar]: ").strip() or "bar"; Tn=parse_num(input("T: ")); Tu=input("Unidad [K]: ").strip() or "K"; rn=parse_num(input("rho / (kg m^-3): "))
        M=rn.value*R*t_to_k(Tn,Tu)/p_to_pa(Pn,Pu)*1000
        print("M =",fmt(M,sig_min(Pn,Tn,rn),"g mol⁻¹"))
    elif op=="3":
        Ms=parse_num(input("M_media / (g/mol): ")); print("GE =",fmt(Ms.value/M_AIRE,Ms.sig or 6))


def interactive_kinetic():
    Tn=parse_num(input("T: ")); Tu=input("Unidad [K]: ").strip() or "K"; T=t_to_k(Tn,Tu); sig=Tn.sig or 6
    E=1.5*K_B*T; print("<Ec> por molécula =",fmt(E,sig,"J")); print("<Ec> por mol =",fmt(1.5*R*T,sig,"J mol⁻¹"))
    gas=input("Gas para u_rms (vacío para omitir): ").strip()
    if gas:
        Ms=input("M / (g/mol) [vacío = buscar gas]: ").strip(); Mn=parse_num(Ms) if Ms else None; M=molar_mass(gas,Mn)/1000
        u=math.sqrt(3*R*T/M); print("u_rms =",fmt(u,sig_min(Tn,Mn),"m s⁻¹"))


def interactive_mixture():
    spec=input("Componentes (ej. CO2:10;N2:90): ")
    base=input("Base [molar/masa/presion] (molar): ").strip() or "molar"
    mm_spec=input("Masas molares personalizadas, si hacen falta (ej. X:50,0; vacío = ninguna): ").strip()
    rows=mixture_from_basis(parse_components(spec),base,parse_molar_mass_map(mm_spec))
    Ps=input("P total (vacío si no se conoce): ").strip(); P=None; Pu="bar"
    if Ps:
        Pn=parse_num(Ps); Pu=input("Unidad de P [bar]: ").strip() or "bar"; P=p_to_pa(Pn,Pu)
    Ts=input("T (vacío si no se requiere densidad): ").strip(); T=None
    if Ts:
        Tn=parse_num(Ts); Tu=input("Unidad T [K]: ").strip() or "K"; T=t_to_k(Tn,Tu)
    Vs=input("V total (vacío si no se requieren volúmenes parciales): ").strip(); V=None; Vu="L"
    if Vs:
        Vn=parse_num(Vs); Vu=input("Unidad V [L]: ").strip() or "L"; V=v_to_m3(Vn,Vu)
    sm=mixture_summary(rows,P,T,V); sig=min([r['q'].sig or 99 for r in rows]+[6])
    print_mixture(rows,sm,sig,Pu,Vu)


def interactive_stoich_volumes():
    names=[x.strip() for x in input("Especies separadas por ';': ").split(';') if x.strip()]
    coeff=[parse_num(x).value for x in input("Coeficientes estequiométricos en el mismo orden, separados por ';': ").split(';')]
    if len(names)!=len(coeff) or not names: raise ValueError("Número de especies y coeficientes incompatible.")
    ref=int(input(f"Índice de especie de referencia [1-{len(names)}]: "))-1
    V=parse_num(input("Volumen de referencia: ")); unit=input("Unidad [L]: ").strip() or "L"
    print("A igual T y P, las relaciones de volumen son las relaciones de coeficientes:")
    for n,c in zip(names,coeff): print(f"{n}: {fmt(V.value*c/coeff[ref],V.sig or 6,unit)}")


def list_gases():
    print(f"{'Clave':<10}{'Nombre':<14}{'M / g mol⁻¹':>14}")
    for k,(name,M) in sorted(GASES.items()): print(f"{k:<10}{name:<14}{M:>14.6g}")


def build_parser():
    p=argparse.ArgumentParser(description="Cálculos de gases ideales y mezclas. Sin argumentos abre menú interactivo.", formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument("--sigfigs",type=int,default=None,help="Fuerza N cifras significativas en la salida.")
    sub=p.add_subparsers(dest="cmd")
    s=sub.add_parser("estado",help="Resuelve PV=nRT; omita exactamente una variable.")
    for k in ("P","V","n","T"): s.add_argument(f"--{k}")
    s.add_argument("--P-unit",default="bar"); s.add_argument("--V-unit",default="L"); s.add_argument("--n-unit",default="mol"); s.add_argument("--T-unit",default="K")
    s=sub.add_parser("densidad",help="Calcula densidad ideal y GE.")
    s.add_argument("--P",required=True); s.add_argument("--P-unit",default="bar"); s.add_argument("--T",required=True); s.add_argument("--T-unit",default="K"); s.add_argument("--gas",default=""); s.add_argument("--M")
    s=sub.add_parser("mezcla",help="Analiza una mezcla ideal.")
    s.add_argument("--componentes",required=True,help="Ej.: CO2:10;N2:90"); s.add_argument("--base",default="molar",choices=["molar","masa","presion"])
    s.add_argument("--masas-molares",default="",help="Masas molares personalizadas en g/mol, ej.: CCl4:153,82;X:50,0")
    s.add_argument("--P"); s.add_argument("--P-unit",default="bar"); s.add_argument("--T"); s.add_argument("--T-unit",default="K"); s.add_argument("--V"); s.add_argument("--V-unit",default="L")
    s=sub.add_parser("combinada",help="Ley combinada P1V1/T1=P2V2/T2; omita una variable.")
    for k in ("P1","V1","T1","P2","V2","T2"): s.add_argument(f"--{k}")
    s.add_argument("--P-unit",default="bar"); s.add_argument("--V-unit",default="L"); s.add_argument("--T-unit",default="K")
    s=sub.add_parser("inventario",help="Cantidad de sustancia y masa en un recipiente ideal.")
    s.add_argument("--P",required=True); s.add_argument("--P-unit",default="bar"); s.add_argument("--T",required=True); s.add_argument("--T-unit",default="K"); s.add_argument("--V",required=True); s.add_argument("--V-unit",default="L"); s.add_argument("--gas",default=""); s.add_argument("--M")
    s=sub.add_parser("cinetica",help="Energía cinética media y velocidad cuadrática media.")
    s.add_argument("--T",required=True); s.add_argument("--T-unit",default="K"); s.add_argument("--gas",default=""); s.add_argument("--M")
    s=sub.add_parser("presion-absoluta",help="Convierte presión manométrica en absoluta.")
    s.add_argument("--Pman",required=True); s.add_argument("--Patm",default="1,01325"); s.add_argument("--P-unit",default="bar"); s.add_argument("--Patm-unit",default=None)
    s=sub.add_parser("volumenes-reaccion",help="Relaciones de volúmenes gaseosos a igual T y P.")
    s.add_argument("--especies",required=True,help="Ej.: N2;H2;NH3"); s.add_argument("--coeficientes",required=True,help="Ej.: 1;3;2"); s.add_argument("--referencia",type=int,required=True,help="Índice 1..N de la especie de referencia"); s.add_argument("--V",required=True); s.add_argument("--V-unit",default="L")
    sub.add_parser("lista-gases",help="Muestra las masas molares incorporadas.")
    sub.add_parser("ayuda",help="Muestra ayuda conceptual.")
    return p


def main(argv=None):
    parser=build_parser(); args=parser.parse_args(argv)
    if args.sigfigs is not None and args.sigfigs<1: parser.error("--sigfigs debe ser >= 1")
    if not args.cmd: interactive(); return 0
    try:
        if args.cmd=="lista-gases": list_gases(); return 0
        if args.cmd=="ayuda": menu_help(); return 0
        if args.cmd=="presion-absoluta":
            pm=parse_num(args.Pman); pa=parse_num(args.Patm); pu=args.P_unit; au=args.Patm_unit or pu; pabs=p_to_pa(pm,pu)+p_to_pa(pa,au); sig=args.sigfigs or sig_min(pm,pa); print("P_abs =",fmt(pa_to(pabs,pu),sig,pu)); return 0
        if args.cmd=="cinetica":
            Tn=parse_num(args.T); T=t_to_k(Tn,args.T_unit); Mn=parse_num(args.M) if args.M else None; sig=args.sigfigs or sig_min(Tn,Mn); print("<Ec> por molécula =",fmt(1.5*K_B*T,sig,"J")); print("<Ec> por mol =",fmt(1.5*R*T,sig,"J mol⁻¹"));
            if args.gas or Mn is not None:
                M=molar_mass(args.gas,Mn)/1000; print("u_rms =",fmt(math.sqrt(3*R*T/M),sig,"m s⁻¹"))
            return 0
        if args.cmd=="inventario":
            Pn=parse_num(args.P); Tn=parse_num(args.T); Vn=parse_num(args.V); Mn=parse_num(args.M) if args.M else None; P=p_to_pa(Pn,args.P_unit); T=t_to_k(Tn,args.T_unit); V=v_to_m3(Vn,args.V_unit); n=P*V/(R*T); sig=args.sigfigs or sig_min(Pn,Tn,Vn,Mn); print("n =",fmt(n,sig,"mol"));
            if args.gas or Mn is not None:
                M=molar_mass(args.gas,Mn); print("m =",fmt(n*M/1000,sig,"kg"))
            return 0
        if args.cmd=="combinada":
            ns={k:(parse_num(getattr(args,k)) if getattr(args,k) is not None else None) for k in ("P1","V1","T1","P2","V2","T2")}
            cv=lambda k: (p_to_pa(ns[k],args.P_unit) if k.startswith("P") else v_to_m3(ns[k],args.V_unit) if k.startswith("V") else t_to_k(ns[k],args.T_unit)) if ns[k] else None
            r=combined_unknown(cv("P1"),cv("V1"),cv("T1"),cv("P2"),cv("V2"),cv("T2")); sig=args.sigfigs or sig_min(*ns.values())
            for i in (1,2): print(f"P{i} =",fmt(pa_to(r[f'P{i}'],args.P_unit),sig,args.P_unit)); print(f"V{i} =",fmt(m3_to(r[f'V{i}'],args.V_unit),sig,args.V_unit)); print(f"T{i} =",fmt(k_to_t(r[f'T{i}'],args.T_unit),sig,args.T_unit))
            return 0
        if args.cmd=="volumenes-reaccion":
            names=[x.strip() for x in args.especies.split(';') if x.strip()]; coeff=[parse_num(x).value for x in args.coeficientes.split(';') if x.strip()]; Vn=parse_num(args.V);
            if len(names)!=len(coeff) or not names or not (1<=args.referencia<=len(names)): raise ValueError("Especies, coeficientes o referencia no válidos.")
            c0=coeff[args.referencia-1]; sig=args.sigfigs or Vn.sig or 6
            for n,c in zip(names,coeff): print(f"{n}: {fmt(Vn.value*c/c0,sig,args.V_unit)}")
            return 0
        if args.cmd=="estado":
            Pn=parse_num(args.P) if args.P is not None else None; Vn=parse_num(args.V) if args.V is not None else None; nn=parse_num(args.n) if args.n is not None else None; Tn=parse_num(args.T) if args.T is not None else None
            P=p_to_pa(Pn,args.P_unit) if Pn else None; V=v_to_m3(Vn,args.V_unit) if Vn else None; n=nn.value*N_FACTORS.get(args.n_unit.lower(),1) if nn else None; T=t_to_k(Tn,args.T_unit) if Tn else None
            r=solve_ideal(P,V,n,T); sig=args.sigfigs or sig_min(Pn,Vn,nn,Tn)
            print("P =",fmt(pa_to(r['P'],args.P_unit),sig,args.P_unit)); print("V =",fmt(m3_to(r['V'],args.V_unit),sig,args.V_unit)); print("n =",fmt(r['n']/N_FACTORS.get(args.n_unit.lower(),1),sig,args.n_unit)); print("T =",fmt(k_to_t(r['T'],args.T_unit),sig,args.T_unit)); return 0
        if args.cmd=="densidad":
            Pn=parse_num(args.P); Tn=parse_num(args.T); Mn=parse_num(args.M) if args.M else None; M=molar_mass(args.gas,Mn); rho=p_to_pa(Pn,args.P_unit)*(M/1000)/(R*t_to_k(Tn,args.T_unit)); sig=args.sigfigs or sig_min(Pn,Tn,Mn)
            print("rho =",fmt(rho,sig,"kg m⁻³")); print("GE_aire =",fmt(M/M_AIRE,sig)); return 0
        if args.cmd=="mezcla":
            rows=mixture_from_basis(parse_components(args.componentes),args.base,parse_molar_mass_map(args.masas_molares))
            Pn=parse_num(args.P) if args.P else None; Tn=parse_num(args.T) if args.T else None; Vn=parse_num(args.V) if args.V else None
            P=p_to_pa(Pn,args.P_unit) if Pn else None; T=t_to_k(Tn,args.T_unit) if Tn else None; V=v_to_m3(Vn,args.V_unit) if Vn else None
            sm=mixture_summary(rows,P,T,V); sig=args.sigfigs or min([r['q'].sig or 99 for r in rows]+[sig_min(Pn,Tn,Vn)])
            print_mixture(rows,sm,sig,args.P_unit,args.V_unit); return 0
    except ValueError as e:
        print("ERROR:",e,file=sys.stderr); return 2
    return 0

if __name__=="__main__":
    raise SystemExit(main())
