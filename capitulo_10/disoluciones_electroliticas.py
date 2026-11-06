#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Capítulo 10. Iones, fuerza iónica y modelos de actividad (menú y autoensayos).

REQUIERE que propiedades_coligativas.py esté en la MISMA carpeta.
Los coeficientes individuales de actividad son CONVENCIONALES (no medibles
independientemente). SIT/Pitzer requieren parámetros externos identificados.
"""
from __future__ import annotations

import argparse
import csv
import math
import re
from dataclasses import dataclass
from pathlib import Path

from propiedades_coligativas import (
    DatosInvalidos, Medida, R_BAR_L, coligativa, cifras, exportar_grafica,
    leer_numero_texto, menu, mostrar, numero, pedir, pedir_entero,
    presion_osmotica, resolver_biseccion, validar_pos,
)

A_DH_25C = 0.509    # (mol/kg)^-1/2; log10, agua ~25°C
B_DH_25C = 0.3281  # Å^-1 (mol/kg)^-1/2, agua ~25°C
A_SIT_25C = 0.5109 # (mol/kg)^-1/2, agua 25°C
A_PHI_25C = 0.392  # (mol/kg)^-1/2, agua 25°C


@dataclass(frozen=True)
class Ion:
    nombre: str
    z: int
    molalidad: float  # mol/kg de disolvente


def fuerza_ionica(iones: list[Ion]) -> float:
    if not iones:
        raise DatosInvalidos('Se necesita al menos un ion.')
    if any(i.z==0 or i.molalidad<0 or not math.isfinite(i.molalidad) for i in iones):
        raise DatosInvalidos('Cada ion debe tener carga no nula y molalidad >=0.')
    return .5*sum(i.molalidad*i.z*i.z for i in iones)


def balance_carga(iones: list[Ion]) -> float:
    return sum(i.molalidad*i.z for i in iones)  # mol_carga/kg de disolvente


def fusionar_iones(iones: list[Ion]) -> list[Ion]:
    """Combina nombres idénticos, impidiendo asignarles cargas incompatibles."""
    acumulados: dict[str,tuple[int,float]]={}
    for i in iones:
        nombre=i.nombre.strip()
        if not nombre:
            raise DatosInvalidos('Un ion necesita identificador.')
        if nombre in acumulados:
            z,m=acumulados[nombre]
            if z!=i.z: raise DatosInvalidos('El mismo ion aparece con dos cargas distintas.')
            acumulados[nombre]=(z,m+i.molalidad)
        else:
            acumulados[nombre]=(i.z,i.molalidad)
    return [Ion(nombre,z,m) for nombre,(z,m) in acumulados.items()]


def iones_electrolito(m_formal: float, especificacion: list[tuple[str,int,int]]) -> list[Ion]:
    validar_pos(m_formal)
    if not especificacion or len(especificacion)<2:
        raise DatosInvalidos('Para un electrolito neutro se necesitan >=2 especies iónicas.')
    if any(nu<1 or z==0 for _,z,nu in especificacion):
        raise DatosInvalidos('Cargas no nulas y coeficientes estequiométricos positivos.')
    if sum(z*nu for _,z,nu in especificacion)!=0:
        raise DatosInvalidos('La fórmula del electrolito no satisface la electroneutralidad.')
    return fusionar_iones([Ion(name,z,m_formal*nu) for name,z,nu in especificacion])


def modelo_log_gamma(z: int, I: float, metodo: str,
                     A: float = A_DH_25C,
                     B: float = B_DH_25C,
                     a_angstrom: float | None = None) -> float:
    """Log10(gamma_i), método dh, davies, extendida; I mol/kg."""
    if z==0 or I<0 or not math.isfinite(I):
        raise DatosInvalidos('Ion debe tener carga y fuerza iónica >=0.')
    validar_pos(A)
    r=math.sqrt(I)
    if metodo=='dh':
        return -A*z*z*r
    if metodo=='davies':
        return -A*z*z*(r/(1+r)-.3*I)
    if metodo=='extendida':
        if a_angstrom is None:
            raise DatosInvalidos('La ecuación extendida necesita radio efectivo (Å).')
        validar_pos(B,a_angstrom)
        return -A*z*z*r/(1+B*a_angstrom*r)
    raise DatosInvalidos('Modelo no reconocido: dh, davies o extendida.')


def gamma_ion(z: int,I:float,metodo:str,**kwargs)->float:
    lg=modelo_log_gamma(z,I,metodo,**kwargs)
    if abs(lg)>300: raise DatosInvalidos('Exponente desbordado; valores fuera del modelo.')
    return 10**lg


def validar_sal(nu_p:int,z_p:int,nu_n:int,z_n:int)->int:
    if nu_p<1 or nu_n<1 or z_p<=0 or z_n>=0:
        raise DatosInvalidos('Debe haber cationes z+>0 y aniones z-<0.')
    if nu_p*z_p+nu_n*z_n!=0:
        raise DatosInvalidos('La combinación iónica no satisface electroneutralidad.')
    return nu_p+nu_n


def molalidad_media(m_formal:float,nu_p:int,nu_n:int)->float:
    validar_pos(m_formal)
    if nu_p<1 or nu_n<1: raise DatosInvalidos('Coeficientes positivos.')
    nu=nu_p+nu_n
    return math.exp((nu_p*math.log(nu_p)+nu_n*math.log(nu_n))/nu)*m_formal


def gamma_media(ln_gammas:list[float], coeficientes:list[int])->float:
    if len(ln_gammas)!=len(coeficientes) or not coeficientes:
        raise DatosInvalidos('Deben corresponder actividades y estequiometría.')
    if any(nu<=0 or not math.isfinite(v) for nu,v in zip(coeficientes,ln_gammas)):
        raise DatosInvalidos('Coeficientes o logaritmos no válidos.')
    return math.exp(sum(nu*v for nu,v in zip(coeficientes,ln_gammas))/sum(coeficientes))


def gamma_media_dh(I:float, nu_p:int,z_p:int,nu_n:int,z_n:int,
                   metodo:str='dh', **kwargs)->float:
    validar_sal(nu_p,z_p,nu_n,z_n)
    logp=modelo_log_gamma(z_p,I,metodo,**kwargs)
    logn=modelo_log_gamma(z_n,I,metodo,**kwargs)
    return 10**((nu_p*logp+nu_n*logn)/(nu_p+nu_n))


def termino_sit(I:float)->float:
    if I<0: raise DatosInvalidos('I negativa.')
    r=math.sqrt(I)
    return A_SIT_25C*r/(1+1.5*r)


def log_gamma_sit(z_j:int,I:float,interacciones:list[tuple[float,float]])->float:
    """SIT: epsilon (kg/mol), m_k (mol/kg). Lista COMPLETA del modelo."""
    if z_j==0 or I<0: raise DatosInvalidos('Carga/ I imposibles.')
    if any(m<0 or not math.isfinite(e) or not math.isfinite(m)
           for e,m in interacciones):
        raise DatosInvalidos('Interacciones SIT inválidas.')
    return -(z_j**2)*termino_sit(I) + sum(e*m for e,m in interacciones)


def pitzer_bg(I:float,beta0:float,beta1:float,alpha:float)->float:
    """B^gamma del libro. Serie en x->0 para evitar cancelación catastrófica."""
    if I<0 or alpha<=0: raise DatosInvalidos('I o alfa de Pitzer inválidos.')
    x=alpha*math.sqrt(I)
    if abs(x)<.01:
        f=1-5*x/6+3*x*x/8-7*x**3/60+x**4/36-3*x**5/560+x**6/1152
    else:
        f=(1-(1+x-x*x/2)*math.exp(-x))/(x*x)
    return 2*(beta0+beta1*f)


def pitzer_fgamma(I:float,Aphi:float=A_PHI_25C,b:float=1.2)->float:
    if I<0: raise DatosInvalidos('I negativa.')
    validar_pos(Aphi,b)
    r=math.sqrt(I)
    return -Aphi*(r/(1+b*r)+2*math.log1p(b*r)/b)


def pitzer_log_gamma_media(m:float,nu_p:int,z_p:int,nu_n:int,z_n:int,
                           beta0:float,beta1:float,Cphi:float,
                           Aphi:float=A_PHI_25C,b:float=1.2,alpha:float=2.)->float:
    """Forma simplificada de Pitzer mostrada en §10.13.2.

    No se aplica a 2:2: requiere beta(2) y funciones adicionales.
    Parámetros beta0, beta1 y Cphi son externos y específicos de electrolito/T.
    Los valores deben corresponder a esta convención precisa.
    """
    nu=validar_sal(nu_p,z_p,nu_n,z_n)
    validar_pos(m,Aphi,b,alpha)
    if abs(z_p)>1 and abs(z_n)>1:
        raise DatosInvalidos('Pitzer 2:2 requiere beta(2): fuera del modelo simplificado.')
    I=.5*m*(nu_p*z_p*z_p+nu_n*z_n*z_n)
    bg=pitzer_bg(I,beta0,beta1,alpha)
    cg=1.5*Cphi
    return (abs(z_p*z_n)*pitzer_fgamma(I,Aphi,b) +
            (2*nu_p*nu_n/nu)*m*bg +
            (2*(nu_p*nu_n)**1.5/nu)*m*m*cg)


def pitzer_gamma_media(*args,**kwargs)->float:
    ln=pitzer_log_gamma_media(*args,**kwargs)
    if abs(ln)>700: raise DatosInvalidos('Resultado desbordado en Pitzer.')
    return math.exp(ln)


def limpiar_nombre(txt:str)->str:
    s=txt.strip()
    if not s or any(x in s for x in [';', '\n']):
        raise DatosInvalidos('Nombre de ion vacío o con delimitador no admitido.')
    return s


def pedir_ion(n:int)->tuple[str,int,int]:
    while True:
        try:
            nombre=limpiar_nombre(input(f'Ion {n} (ej. Na+, SO4^2-): '))
            break
        except DatosInvalidos as exc: print('  ERROR: '+str(exc))
    while True:
        try:
            z=int(input('Carga algebraica z (ej. +1, -2): ').strip())
            if z!=0 and -10<=z<=10:break
        except ValueError:pass
        print('  ERROR: número entero entre -10 y 10 distinto de 0.')
    nu=pedir_entero('Coeficiente estequiométrico del ion',1,20)
    return nombre,z,nu


def pedir_iones_directos()->tuple[list[Ion],bool]:
    clase=menu('Escala de entrada de las concentraciones',{
        '1':'Molalidad de cada ion (mol/kg de disolvente)',
        '2':'Mol por kg de disolución y masa de disolvente por kg de disolución',
        '3':'Molaridad de cada ion (mol/L de disolución)'})
    agua=1.
    if clase=='2':
        agua=pedir('kg de disolvente por kg de disolución',minimo=0,estricto=True,maximo=1).valor
    n=pedir_entero('Número de especies iónicas presentes',2,25)
    items=[]
    for j in range(n):
        while True:
            try:
                nombre=limpiar_nombre(input(f'Ion {j+1} (nombre único): '))
                break
            except DatosInvalidos as exc:print(' ERROR: '+str(exc))
        while True:
            try:
                z=int(input('Carga con signo z: ').strip())
                if z!=0 and abs(z)<=10:break
            except ValueError:pass
            print('  ERROR: carga entera no nula entre -10 y 10.')
        m=pedir(f'{nombre}: concentración ({"mol/kg disolución" if clase=="2" else "mol/L" if clase=="3" else "mol/kg disolvente"})',
                minimo=0).valor
        items.append(Ion(nombre,z,m/agua if clase=='2' else m))
    print('  Escala introducida:',('molaridad mol/L' if clase=='3' else 'molalidad mol/kg'))
    return fusionar_iones(items), clase=='3'


def informar_iones(items:list[Ion], *, escala_molar:bool=False)->None:
    print('  Composición:')
    for i in items:
        print(f'  {i.nombre:>12} : z={i.z:+d}; concentración={numero(i.molalidad,6)} '
              +('mol/L' if escala_molar else 'mol/kg'))
    Ic=fuerza_ionica(items)
    balance=balance_carga(items)
    imprimir_escala='mol/L' if escala_molar else 'mol/kg'
    mostrar('Concentración total de partículas ideal',sum(x.molalidad for x in items),
            imprimir_escala,5,'Σ_i c_i o Σ_i m_i')
    mostrar('Fuerza iónica (escala de entrada)',Ic,imprimir_escala,5,'I = 1/2 Σ_i c_i z_i²')
    mostrar('Balance de carga con signo',balance,imprimir_escala,5,'Σ_i c_i z_i')
    totalcharge=sum(abs(x.z)*x.molalidad for x in items)
    if abs(balance)>max(totalcharge*1e-10,1e-13):
        print('  ADVERTENCIA: no se satisface electroneutralidad; podría ser un inventario parcial')
        print('  de iones (p. ej., agua de mar sin especies minoritarias).')
    print('  Contribuciones 1/2 c_i z_i²:')
    for q in items:
        print('   ',q.nombre, '=',numero(.5*q.molalidad*q.z*q.z,5),imprimir_escala)
    if escala_molar:
        print('  AVISO: I se calculó con mol/L; para usar modelos MOLALES hace falta la')
        print('  masa de disolvente y efectuar la conversión pertinente.')


def leer_sal()->tuple[float,list[Ion]]:
    m=pedir('Molalidad formal del electrolito (mol/kg disolvente)',minimo=0,estricto=True).valor
    n=pedir_entero('Número de tipos de iones generados por la fórmula',2,6)
    spec=[pedir_ion(j+1) for j in range(n)]
    return m,iones_electrolito(m,spec)


def pasos_composicion()->None:
    o=menu('Composición y fuerza iónica',{
        '1':'Una sal: deducir concentración de cada ion y comprobar cargas',
        '2':'Mezcla de sales: sumar contribuciones por especie',
        '3':'Introducir inventario iónico directamente (molal, por kg disolución o molar)',
        '0':'Volver'})
    if o=='0':return
    if o=='1':
        _,iones=leer_sal();informar_iones(iones)
    elif o=='2':
        n=pedir_entero('Número de electrolitos de la mezcla',2,12)
        todos=[]
        for j in range(n):
            print(f'\n--- Electrolito {j+1}/{n} ---')
            _,items=leer_sal();todos.extend(items)
        informar_iones(fusionar_iones(todos))
    else:
        items,molar=pedir_iones_directos()
        informar_iones(items,escala_molar=molar)


def advertir_I(metodo:str,I:float)->None:
    if metodo=='dh' and I>0.01:
        print('  ADVERTENCIA: ley límite fuera del intervalo orientativo I <=0,01 mol/kg.')
    if metodo in ('extendida','davies') and I>0.1:
        print('  ADVERTENCIA: fuera del intervalo orientativo I <=0,1 mol/kg.')
    if metodo=='davies' and I>0.5:
        print('  ADVERTENCIA: Davies puede dar comportamiento artefactual a I alta.')


def pasos_actividad()->None:
    op=menu('Actividad de un ion, modelos convencionales',{
        '1':'Ley límite Debye–Hückel (25°C agua)',
        '2':'Ecuación extendida Debye–Hückel (radio efectivo)',
        '3':'Davies (25°C agua)',
        '4':'Pasar de gamma y molalidad a actividad adimensional',
        '0':'Volver'})
    if op=='0':return
    if op=='4':
        gamma=pedir('Coeficiente gamma_i > 0',minimo=0,estricto=True)
        molal=pedir('Molalidad del ion (mol/kg)',minimo=0)
        mostrar('a_i',gamma.valor*molal.valor,n=cifras(gamma,molal),
                formula='a_i=gamma_i (m_i/m°), m°=1 mol/kg')
        return
    z=pedir_entero('Valor absoluto de carga |z|',1,10)
    I=pedir('Fuerza iónica MOLAL I (mol/kg)',minimo=0)
    modelo={'1':'dh','2':'extendida','3':'davies'}[op]
    kwargs={}
    if modelo=='extendida':
        a=pedir('Radio iónico efectivo a_i^(DH) (Å)',minimo=0,estricto=True)
        kwargs={'a_angstrom':a.valor}
    lg=modelo_log_gamma(z,I.valor,modelo,**kwargs)
    mostrar('log10 gamma_i',lg,n=I.cifras,formula='Modelo '+modelo)
    mostrar('gamma_i',10**lg,n=I.cifras,formula='gamma_i=10^(log10 gamma_i)')
    print('  Nota: gamma_i individual no es directamente observable sin convención.')
    advertir_I(modelo,I.valor)


def pedir_formula_binaria()->tuple[int,int,int,int]:
    print('Fórmula general M_(ν+) X_(ν-): z+ positivo, z- negativo.')
    np=pedir_entero('ν+ cationes por unidad fórmula',1,20)
    zp=pedir_entero('z+ (módulo positivo)',1,10)
    nn=pedir_entero('ν- aniones por unidad fórmula',1,20)
    zn=-pedir_entero('|z-| (módulo positivo)',1,10)
    validar_sal(np,zp,nn,zn)
    return np,zp,nn,zn


def pasos_media()->None:
    np,zp,nn,zn=pedir_formula_binaria()
    m=pedir('Molalidad FORMAL de la sal (mol/kg)',minimo=0,estricto=True)
    I=.5*m.valor*(np*zp*zp+nn*zn*zn)
    mm=molalidad_media(m.valor,np,nn)
    mostrar('I',I,'mol/kg',m.cifras,'I = m(ν+z+²+ν-z-²)/2')
    mostrar('m±',mm,'mol/kg',m.cifras,'m±=[(ν+m)^(ν+) (ν-m)^(ν-)]^(1/ν)')
    modelo=menu('Modelo para gamma±',{'1':'Debye–Hückel límite',
                                    '2':'Davies','3':'Debye–Hückel extendida'})
    tag={'1':'dh','2':'davies','3':'extendida'}[modelo]
    extras={}
    if modelo=='3':
        ap=pedir('Radio efectivo del catión (Å)',minimo=0,estricto=True).valor
        an=pedir('Radio efectivo del anión (Å)',minimo=0,estricto=True).valor
        l1=modelo_log_gamma(zp,I,'extendida',a_angstrom=ap)
        l2=modelo_log_gamma(zn,I,'extendida',a_angstrom=an)
        g=10**((np*l1+nn*l2)/(np+nn))
    else:
        g=gamma_media_dh(I,np,zp,nn,zn,tag,**extras)
    mostrar('gamma±',g,n=m.cifras,formula='gamma±=(gamma+^ν+ gamma-^ν-)^(1/ν)')
    mostrar('a±',g*mm,n=m.cifras,formula='a±=gamma± (m±/m°)')
    advertir_I(tag,I)


def pasos_sit()->None:
    print('SIT OECD/NEA, agua 25 °C: log10 γ_j = -z_j² D(I) + Σ ε(j,k) m_k.')
    print('SE EXIGEN coeficientes ε(j,k) proporcionados por el usuario; no se inventan.')
    z=pedir_entero('Carga absoluta del ion objetivo',1,10)
    I=pedir('I MOLAL (mol/kg)',minimo=0)
    n=pedir_entero('Número de especies k consideradas para interacciones específicas',1,30)
    pares=[]
    for j in range(n):
        print(f' Especie k={j+1}:')
        m=pedir('Molalidad m_k (mol/kg)',minimo=0)
        eps=pedir('ε(j,k) específico (kg/mol, puede ser negativo)')
        pares.append((eps.valor,m.valor))
    r=log_gamma_sit(z,I.valor,pares)
    mostrar('D(I)',termino_sit(I.valor),n=5,formula='D=0,5109√I/(1+1,5√I)')
    mostrar('log10 γ_j',r,n=5,formula='-z_j² D + Σ ε(j,k) m_k')
    mostrar('γ_j',10**r,n=5,formula='γ=10^logγ')
    print('  Modelo simplificado: interacciones entre pares opuestos; si se omiten')
    print('  especies relevantes, el resultado queda incompleto.')


def recoger_pitzer()->dict:
    print('Pitzer simplificado: solo electrolito binario con al menos un ion monovalente.')
    np,zp,nn,zn=pedir_formula_binaria()
    if abs(zp)>1 and abs(zn)>1:
        raise DatosInvalidos('Pitzer 2:2 no implementado: falta β(2) y sus funciones.')
    b0=pedir('β^(0) (parámetro específico, kg/mol)')
    b1=pedir('β^(1) (parámetro específico, kg/mol)')
    cphi=pedir('C^φ (parámetro específico en convención Pitzer)').valor
    alpha=pedir('α de Pitzer (no grado de disociación; usualmente 2,0)',minimo=0,estricto=True)
    return dict(nu_p=np,z_p=zp,nu_n=nn,z_n=zn,
                beta0=b0.valor,beta1=b1.valor,Cphi=cphi,alpha=alpha.valor)


def pasos_pitzer()->None:
    cfg=recoger_pitzer()
    m=pedir('Molalidad formal (mol/kg)',minimo=0,estricto=True)
    I=.5*m.valor*(cfg['nu_p']*cfg['z_p']**2+cfg['nu_n']*cfg['z_n']**2)
    l=pitzer_log_gamma_media(m.valor,**cfg)
    mostrar('I',I,'mol/kg',m.cifras,'I=m(ν+ z+²+ν- z-²)/2')
    mostrar('f^γ',pitzer_fgamma(I),n=6)
    mostrar('B^γ',pitzer_bg(I,cfg['beta0'],cfg['beta1'],cfg['alpha']),n=6)
    mostrar('C^γ',1.5*cfg['Cphi'],n=6,formula='C^γ=(3/2)C^φ')
    mostrar('ln gamma±',l,n=6,formula='Ecuación simplificada 10.13.2 (log natural)')
    mostrar('gamma±',math.exp(l),n=m.cifras,formula='γ±=exp(ln γ±)')
    print('  AVISO: parámetros del mismo sistema, temperatura, referencia y')
    print('  parametrización son imprescindibles; no se valida experimentalmente.')


def pasos_inversos()->None:
    print('Resolver gamma objetivo mediante bisección; Davies puede no ser monótono.')
    metodo=menu('Modelo',{'1':'Debye–Hückel límite','2':'Davies'})
    tag='dh' if metodo=='1' else 'davies'
    z=pedir_entero('Valor absoluto de carga |z|',1,10)
    objetivo=pedir('Gamma_i objetivo (0 < gamma < 1)',minimo=0,estricto=True,maximo=1)
    if objetivo.valor>=1: raise DatosInvalidos('Para esta búsqueda se exige γ<1.')
    ai=pedir('Extremo inferior de I (mol/kg; admite 0)',minimo=0)
    bi=pedir('Extremo superior de I (mol/kg)',minimo=0,estricto=True)
    tol=pedir('Tolerancia absoluta en I (mol/kg)',minimo=0,estricto=True)
    lim=pedir_entero('Iteraciones máximas',1,100000)
    f=lambda x:gamma_ion(z,x,tag)-objetivo.valor
    valor,n=resolver_biseccion(f,ai.valor,bi.valor,tol.valor,lim)
    mostrar('I estimada',valor,'mol/kg',min(tol.cifras+2,10),
            'γ_modelo(I)-γ_objetivo=0 mediante bisección')
    print(f'  Iteraciones: {n}. Residuo: {f(valor):.8g}')
    advertir_I(tag,valor)
    print('  ADVERTENCIA: solo se identifica raíz dentro del intervalo suministrado.')


def leer_datos_experimentales()->tuple[list[float],list[float]]:
    file=input('Ruta de CSV con encabezado I;gamma (vacío = sin datos): ').strip().strip('"')
    if not file:return [],[]
    ruta=Path(file)
    if not ruta.is_file():raise DatosInvalidos('Archivo CSV no encontrado.')
    if ruta.stat().st_size>10_000_000:
        raise DatosInvalidos('CSV demasiado grande (límite 10 MB).')
    out=[]
    with ruta.open(encoding='utf-8-sig',newline='') as f:
        dr=csv.DictReader(f,delimiter=';')
        if not dr.fieldnames or not {'I','gamma'}.issubset(set(dr.fieldnames)):
            raise DatosInvalidos('El CSV debe usar ; como separador y encabezados I;gamma.')
        for n,row in enumerate(dr,1):
            if n>20000:raise DatosInvalidos('Demasiados puntos CSV.')
            I=leer_numero_texto(row['I'],minimo=0).valor
            g=leer_numero_texto(row['gamma'],minimo=0,estricto=True).valor
            out.append((I,g))
    if not out:raise DatosInvalidos('CSV vacío.')
    return [I for I,_ in out],[g for _,g in out]


def pasos_graficos()->None:
    op=menu('Gráficos exportables PNG 400 ppp / SVG / CSV',{
        '1':'Comparación DH límite, Davies, DH extendida (gamma± vs √I)',
        '2':'Contribución iónica a I para mezcla introducida manualmente',
        '3':'Comportamiento Pitzer frente a molalidad (parámetros de usuario)',
        '0':'Volver'})
    if op=='0':return
    if op=='1':
        np,zp,nn,zn=pedir_formula_binaria()
        maxI=pedir('I máxima (mol/kg)',minimo=0,estricto=True)
        xs=[math.sqrt(maxI.valor)*k/200 for k in range(201)]
        ii=[x*x for x in xs]
        plots=[('DH límite',[gamma_media_dh(v,np,zp,nn,zn,'dh') for v in ii],'-'),
               ('Davies',[gamma_media_dh(v,np,zp,nn,zn,'davies') for v in ii],'--')]
        if input('¿Añadir DH extendida (radios efectivos)? [s/N] ').strip().lower()=='s':
            rp=pedir('Radio efectivo catión (Å)',minimo=0,estricto=True).valor
            rn=pedir('Radio efectivo anión (Å)',minimo=0,estricto=True).valor
            pp=[]
            for I in ii:
                lp=modelo_log_gamma(zp,I,'extendida',a_angstrom=rp)
                ln=modelo_log_gamma(zn,I,'extendida',a_angstrom=rn)
                pp.append(10**((np*lp+nn*ln)/(np+nn)))
            plots.append(('DH extendida',pp,':'))
        # CSV experiments require extra plot overlay. Do not say "experimental" for unsourced input.
        obs_I, obs_g=leer_datos_experimentales()
        if obs_I:
            # Preserve user dataset as separate file and draw observed points on existing domain,
            # interpolated? Better scatter saved separately when Matplotlib available.
            from propiedades_coligativas import obtener_graficas
            plt,F=obtener_graficas()
            folder=Path('resultados_capitulo10');folder.mkdir(exist_ok=True)
            base=folder/'gamma_actividad_con_datos_importados'
            fig,ax=plt.subplots(figsize=(8,5.5))
            for name,ys,sty in plots:ax.plot(xs,ys,sty,label=name,linewidth=2)
            ax.scatter([math.sqrt(v) for v in obs_I],obs_g,label='Datos CSV (origen usuario)',s=34,zorder=3)
            ax.set(xlabel=r'$\sqrt{I}\,/\,(\mathrm{mol\,kg^{-1}})^{1/2}$',ylabel=r'$\gamma_{\pm}$')
            ax.grid(alpha=.3,ls=':');ax.legend()
            ax.xaxis.set_major_formatter(F(lambda v,_:f'{v:g}'.replace('.',',')))
            ax.yaxis.set_major_formatter(F(lambda v,_:f'{v:g}'.replace('.',',')))
            fig.tight_layout();fig.savefig(base.with_suffix('.svg'))
            fig.savefig(base.with_suffix('.png'),dpi=400);plt.close(fig)
            with base.with_suffix('.csv').open('w',encoding='utf-8-sig',newline='') as f:
                wr=csv.writer(f,delimiter=';');wr.writerow(['I (mol/kg)','gamma (origen usuario)'])
                for i,g in zip(obs_I,obs_g):wr.writerow([str(i).replace('.',','),str(g).replace('.',',')])
            print('  Creados SVG, PNG y CSV de datos importados en',folder)
        else:
            exportar_grafica(xs,plots,r'$\sqrt{I}\,/\,(\mathrm{mol\,kg^{-1}})^{1/2}$',r'$\gamma_{\pm}$',
                             'comparacion_actividad_DH_Davies')
        advertir_I('dh',maxI.valor);advertir_I('davies',maxI.valor)
        print('  Las curvas fuera de rango se muestran solo como extrapolaciones matemáticas.')
    elif op=='2':
        ions,molar=pedir_iones_directos()
        valores=[.5*i.molalidad*i.z*i.z for i in ions]
        xs=list(range(1,len(ions)+1))
        exportar_grafica(xs,[('Aportación a I',valores,'o-')],
                         'Índice de especie (etiquetas en CSV)','1/2 c_i z_i² (escala introducida)' if molar else '1/2 m_i z_i² (mol/kg)',
                         'contribuciones_fuerza_ionica')
        print('  Índices:',', '.join(f'{n}={ion.nombre}' for n,ion in enumerate(ions,1)))
    elif op=='3':
        cfg=recoger_pitzer()
        fin=pedir('Molalidad máxima (mol/kg)',minimo=0,estricto=True)
        xs=[fin.valor*k/200 for k in range(201)]
        ys=[]
        for m in xs:
            if m==0:ys.append(1.)
            else:ys.append(pitzer_gamma_media(m,**cfg))
        exportar_grafica(xs,[('Pitzer simplificado',ys,'-')],
                         'Molalidad formal / mol kg⁻¹','γ±','pitzer_gamma_media')
        print('  Los resultados dependen de parámetros específicos provistos por el usuario.')


def pasos_integrados()->None:
    """Ejercicios C: modelo inicial de partículas, no una predicción real."""
    op=menu('Aplicaciones integradas de los ejercicios C',{
        '1':'Agua de mar/salmueras: iones -> I -> crioscopía y presión osmótica IDEALES',
        '2':'Soluciones con concentración conocida de especies iónicas (mol/L): I y Π',
        '3':'Eritrocitos: medios de NaCl en % m/V frente a osmolaridad interna',
        '0':'Volver'})
    if op=='0':return
    if op=='3':
        M=pedir('Masa molar de NaCl (g/mol)',minimo=0,estricto=True)
        T=pedir('Temperatura del ensayo (°C)',minimo=-273.15,estricto=True)
        interno=pedir('Osmolaridad eficaz intracelular (mOsm/L)',minimo=0,estricto=True)
        n=pedir_entero('Número de disoluciones de NaCl que se compararán',1,20)
        pi_in=presion_osmotica(interno.valor/1000,T.valor+273.15)
        mostrar('Π intracelular ideal',pi_in,'bar',3,'Π=(Osm/L) RT')
        for j in range(n):
            pct=pedir(f'Disolución {j+1}: NaCl % m/V',minimo=0,estricto=True)
            c=pct.valor*10/M.valor
            osm=2*c  # NaCl ideal con disociación completa
            pi=presion_osmotica(osm,T.valor+273.15)
            diferencia=pi-pi_in
            mostrar('NaCl c',c,'mol/L',3,'c=10 (% m/V)/M_NaCl')
            mostrar('Osmolaridad exterior IDEAL',osm*1000,'mOsm/L',3,'2c (límite ideal)')
            mostrar('Π exterior',pi,'bar',3)
            mostrar('Π exterior - Π interior',diferencia,'bar',3)
            if abs(diferencia)<1e-12:
                print('  Modelo ideal: sin impulso osmótico inicial.')
            elif diferencia>0:
                print('  Modelo ideal: exterior HIPERTÓNICO, agua sale del eritrocito.')
            else:
                print('  Modelo ideal: exterior HIPOTÓNICO, agua entra al eritrocito.')
        print('  ALERTA CIENTÍFICA: tonacidad fisiológica ≠ osmolaridad analítica ideal;')
        print('  coeficientes osmóticos, permeabilidades y solutos efectivos importan.')
        print('  La clasificación de NaCl al 0,9 % como isotónico es fisiológica/APROXIMADA.')
        return
    if op=='1':
        print('Introduzca molalidades o inventario de iones en kg de disolución.')
        items,molar=pedir_iones_directos()
        if molar:
            raise DatosInvalidos('Para crioscopía se necesitan molalidades. Vuelva a elegir escala 1 o 2.')
        informar_iones(items)
        Kf=pedir('Constante crioscópica Kf (K kg/mol)',minimo=0,estricto=True)
        TF=pedir('Temperatura de congelación del disolvente puro (°C)')
        mol_total=sum(i.molalidad for i in items)
        delta=Kf.valor*mol_total
        mostrar('Descenso crioscópico IDEAL',delta,'K',3,'ΔTf=Kf Σm_i (iones independientes)')
        mostrar('Tf modelo IDEAL',TF.valor-delta,'°C',3,'Tf=Tf*-ΔTf')
        f=pedir('Fracción másica de disolvente (kg/kg disolución)',minimo=0,estricto=True,maximo=1)
        rho=pedir('Densidad disolución (kg/L)',minimo=0,estricto=True)
        T=pedir('Temperatura para Π (°C)',minimo=-273.15,estricto=True)
        cmol=mol_total*f.valor*rho.valor
        pi=presion_osmotica(cmol,T.valor+273.15)
        mostrar('Concentración de partículas IDEAL',cmol,'mol/L',3,
                'c_part=(Σm_i) × kg disolvente/kg disolución × kg disolución/L')
        mostrar('Π modelo IDEAL',pi,'bar',3,'Π=c_part R T')
        if fuerza_ionica(items)>.1:
            print('  ADVERTENCIA: I alta, ley límite y Davies INADECUADOS y las estimaciones')
            print('  coligativas ideales no son predicciones experimentales fiables.')
    else:
        print('Datos molares. No convertir directamente esta I (mol/L) a I molal.')
        items,molar=pedir_iones_directos()
        if not molar:
            raise DatosInvalidos('Se requieren concentraciones MOLARES: seleccione escala 3.')
        informar_iones(items,escala_molar=True)
        T=pedir('Temperatura (°C)',minimo=-273.15,estricto=True)
        mostrar('Π IDEAL',presion_osmotica(sum(i.molalidad for i in items),T.valor+273.15),
                'bar',3,'Π=R T Σc_i')
        print('  Los resultados se basan en disociación completa y comportamiento ideal.')


def pruebas()->tuple[int,int]:
    checks=[]
    def check(nombre, got, ref, tol):
        checks.append((nombre,math.isclose(got,ref,rel_tol=0,abs_tol=tol),got,ref))
    Na=iones_electrolito(.02,[('Na+',1,1),('Cl-',-1,1)])
    check('NaCl I=m',fuerza_ionica(Na),.02,1e-14)
    check('NaCl electroneutral',balance_carga(Na),0,1e-14)
    Ca=iones_electrolito(.02,[('Ca2+',2,1),('Cl-',-1,2)])
    check('CaCl2 I=3m',fuerza_ionica(Ca),.06,1e-14)
    check('MgSO4 I=4m',fuerza_ionica(iones_electrolito(.05,[('Mg2+',2,1),('SO4^2-',-2,1)])),.2,1e-14)
    check('10.6 I',fuerza_ionica(fusionar_iones(
        iones_electrolito(.02,[('Na+',1,2),('SO4^2-',-2,1)])+
        iones_electrolito(.015,[('Mg2+',2,1),('Cl-',-1,2)]))),.105,1e-12)
    check('10.7 I',fuerza_ionica(iones_electrolito(.002,[('Ca2+',2,1),('Cl-',-1,2)])),.006,1e-14)
    check('10.7 gamma±',gamma_media_dh(.006,1,2,2,-1),.834,.001)
    check('10.7 m±',molalidad_media(.002,1,2),.003175,1e-6)
    check('10.7 a±',gamma_media_dh(.006,1,2,2,-1)*molalidad_media(.002,1,2),.00265,3e-6)
    check('10.8 I NaCl',fuerza_ionica(iones_electrolito(.05,[('Na+',1,1),('Cl-',-1,1)])),.05,1e-14)
    check('10.8 DH',gamma_media_dh(.05,1,1,1,-1),.769,.001)
    check('10.8 Davies',gamma_media_dh(.05,1,1,1,-1,'davies'),.822,.001)
    check('10.8 discrepancia %',100*(gamma_media_dh(.05,1,1,1,-1,'davies')-
                        gamma_media_dh(.05,1,1,1,-1))/gamma_media_dh(.05,1,1,1,-1,'davies'),
          6.34,.08)
    check('Electro-neutralidad sal de 2:1',validar_sal(1,2,2,-1),3,0)
    check('DH límite I->0',gamma_ion(2,0,'dh'),1,1e-14)
    check('Davies límite I->0',gamma_ion(1,0,'davies'),1,1e-14)
    check('SIT D I=0',termino_sit(0),0,1e-14)
    check('SIT sin término específico',log_gamma_sit(1,.01,[]),-termino_sit(.01),1e-14)
    check('Pitzer B^gamma I->0',pitzer_bg(0,.08,.27,2),.70,1e-12)
    check('Pitzer fγ I->0',pitzer_fgamma(0),0,1e-14)
    check('Pitzer gamma m baja',pitzer_gamma_media(.0000001,1,1,1,-1,.0765,.2664,.00127),1,.001)
    check('actividad media 1:1',gamma_media([math.log(.8),math.log(.9)],[1,1]),math.sqrt(.72),1e-12)
    # Sea water (partial ions) salinity 35 per 1 kg of solution; convert mol/kg solution -> mol/kg water.
    sea=[Ion(n,z,v/.965) for n,z,v in [
        ('Na+',1,.46906),('Cl-',-1,.54586),('Mg2+',2,.05282),
        ('SO4^2-',-2,.02824),('Ca2+',2,.01028),('K+',1,.01021)]]
    check('C3 agua mar I (seis iones)',fuerza_ionica(sea),.719,.004)
    check('C3 agua mar balance parcial no nulo',1 if abs(balance_carga(sea))>1e-4 else 0,1,0)
    check('bisec inversa DH',resolver_biseccion(lambda I:gamma_ion(1,I,'dh')-.9,
          0,.04,1e-10,100)[0], (math.log10(.9)/(-A_DH_25C))**2,1e-10)
    # Ejercicios finales B y C con resultados analíticos independientes.
    check('10.B.6 NaCl+CaCl2 I',fuerza_ionica(fusionar_iones(
          iones_electrolito(.02,[('Na+',1,1),('Cl-',-1,1)])+
          iones_electrolito(.01,[('Ca2+',2,1),('Cl-',-1,2)]))),.05,1e-14)
    check('10.B.6 Davies Ca2+ < Na+',1 if gamma_ion(2,.05,'davies')<gamma_ion(1,.05,'davies') else 0,1,0)
    check('10.B.7 I CaCl2',fuerza_ionica(iones_electrolito(.001,[('Ca2+',2,1),('Cl-',-1,2)])),.003,1e-14)
    check('10.B.8 DH z2 más desviación',1 if gamma_ion(2,.01,'dh')<gamma_ion(1,.01,'dh') else 0,1,0)
    check('10.C.1 fuerza iónica NaCl',10/(2*1.86),2.688172,1e-6)
    check('10.C.1 fuerza iónica CaCl2',3*10/(3*1.86),5.376344,1e-6)
    check('10.C.3 total molalidad partículas',sum(i.molalidad for i in sea),1.156964,1e-6)
    check('10.C.4 concentración total partículas',sum(i.molalidad for i in sea)*.965*1.02334,1.14254,.00002)
    check('10.C.4 presión osmótica ideal bar',sum(i.molalidad for i in sea)*.965*1.02334*
          R_BAR_L*298.15,28.32279,.00002)
    check('10.C.5 OMS concentración ionic molar (por litro)',.075+.065+.020+.010,.170,1e-14)
    check('10.C.7 NaCl 0,45% c_osm',2*4.5/58.44,.154004,1e-6)
    check('10.C.7 NaCl 0,90% c_osm',2*9.0/58.44,.308008,1e-6)
    check('10.C.7 NaCl 3,00% c_osm',2*30.0/58.44,1.026694,1e-6)
    check('formato actividad',1 if numero(.002648,3)=='0,00265' else 0,1,0)
    for name,ok,got,ref in checks:
        print(('PASS' if ok else 'FAIL')+' '+name+' | calculado='+str(got)+' | referencia='+str(ref))
    passed=sum(c[1] for c in checks)
    print(f'RESULTADO: {passed}/{len(checks)} pruebas correctas.')
    return passed,len(checks)


def principal()->None:
    print('CAPÍTULO 10 — DISOLUCIONES ELECTROLÍTICAS')
    print('Escala por defecto: MOLAL (mol/kg de disolvente). Agua a 25 °C.')
    print('Los cálculos fuera del intervalo recomendado se etiquetan como orientativos.')
    print('Los coeficientes de actividad individuales solo son convencionales.')
    while True:
        op=menu('MENÚ PRINCIPAL',{
            '1':'Composición iónica, electroneutralidad y fuerza iónica',
            '2':'Actividad individual DH límite / extendida / Davies',
            '3':'Molalidad, actividad y coeficiente IÓNICOS MEDIOS',
            '4':'SIT simplificado con parámetros aportados',
            '5':'Pitzer simplificado con parámetros aportados',
            '6':'Despeje ITERATIVO de fuerza iónica desde γ objetivo',
            '7':'Gráficos y CSV (incluido cotejo con datos importados)',
            '8':'Pruebas numéricas de los ejemplos del capítulo',
            '9':'Aplicaciones integradas: agua de mar, formulaciones y eritrocitos',
            '0':'Salir'})
        if op=='0':return
        try:
            {'1':pasos_composicion,'2':pasos_actividad,'3':pasos_media,
             '4':pasos_sit,'5':pasos_pitzer,'6':pasos_inversos,
             '7':pasos_graficos,'8':pruebas,'9':pasos_integrados}[op]()
        except (DatosInvalidos, OverflowError, ZeroDivisionError) as exc:
            print('  ERROR DE CÁLCULO: '+str(exc))
        except (KeyboardInterrupt,EOFError):
            print('\nFin de la sesión.');return


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--selftest',action='store_true',help='Ejecutar verificación automática y salir')
    args=parser.parse_args()
    if args.selftest:
        pasa,total=pruebas()
        raise SystemExit(0 if pasa==total else 1)
    principal()
