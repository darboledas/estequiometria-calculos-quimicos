# -*- coding: utf-8 -*-
"""Bloque IX. Casos trazados al libro definitivo y al solucionario desarrollado.

Un test por ejercicio, más seis guardias sobre inversión de Antoine (capítulo 7).
Las cifras de referencia y tolerancias proceden de los datos impresos y se
registran en REVISIONES/MATRIZ_COTEJO_BLOQUE_09.json.
"""
import math
import unittest
from test_auditoria_integral import mod


def cerca(actual, expected, tolerance):
    if not math.isfinite(float(actual)) or abs(float(actual)-expected)>tolerance:
        raise AssertionError(f'valor obtenido {actual!r}, referencia {expected!r}, tol. {tolerance}')


def e3b4():
    m=mod('masa_molar'); mass=float(m.calculate_molar_mass('H2SO4').raw_mass)
    cerca(49*4*16/mass,32.0,.06)

def e3b6():
    m=mod('masa_molar');g=mod('gases_ideales_y_mezclas')
    n=6.50/float(m.calculate_molar_mass('Zn').raw_mass)
    V=n*8.314462618*273.15/101325*1000
    cerca(V,2.228,.007)
    cerca(g.solve_ideal(None,V/1000,n,273.15)['P'],101325,1e-3)

def e4b4():
    m=mod('gases_ideales_y_mezclas')
    r=m.mixture_from_basis([(z,m.parse_num(q)) for z,q in [('C2H6','0.600'),('H2','0.250'),('CO2','0.150')]],'molar')
    s=m.mixture_summary(r,120000,300)
    cerca(s['Mmix'],25.1475,.02)
    for i,v in enumerate((.717,.0200,.263)):cerca(r[i]['w'],v,.002)
    cerca(s['c_total_mol_m3']/1000,.04811,.00008)
    cerca(200*120000/(m.R*300)*s['Mmix']/1000,241.99,.3) # kg/h

def e4b6():
    m=mod('gases_ideales_y_mezclas')
    r=m.mixture_from_basis([(z,m.parse_num(q)) for z,q in [('CO2','.100'),('Cl2','.150'),('N2','.125'),('H2','.625')]],'molar')
    s=m.mixture_summary(r)
    cerca(s['Mmix'],19.7987,.02)
    for i,v in enumerate((.222,.537,.177,.0636)):cerca(r[i]['w'],v,.003)

def e5b13():
    m=mod('gases_reales');Z=.86571
    cerca(510/425.125,1.19965,.00002)
    cerca(26.6/37.96,.70074,.00002)
    cerca(Z*m.R_BAR*510/26.6,1.38005,.00005)
    cerca(m.ideality_error(Z,'v')*100,15.512,.005)

def e6b1():
    m=mod('presion_vapor');dh=385000*.07412
    cerca(m.cc_pressure2(25.0,273,298,dh),71.7768,.008)
    cerca(m.cc_pressure2(25.0,273,308,dh),104.3234,.014)

def e7b10():
    m=mod('equilibrio_liquido_vapor')
    c=[m.Component('acetona',6.42448,1312.253,-32.445),m.Component('acetato de etilo',6.22809,1245.702,-55.189),m.Component('tolueno',6.07827,1343.943,-53.773)]
    r,pstar,y=m.bubble_temperature(c,[.5,.3,.2],100.)
    cerca(r.root,340.55835,.005)
    cerca(sum(x*p for x,p in zip((.5,.3,.2),pstar)),100,1e-6)
    cerca(sum(y),1,1e-10)

def e7b11():
    m=mod('equilibrio_liquido_vapor');op=mod('operaciones_liquido_vapor')
    r=m.raoult_from_pstar([.4,.6],[179.1,74.2]);d,_=m.dew_from_pstar([.4,.6],[179.1,74.2])
    cerca(r['P'],116.16,.001);cerca(d,96.9026,.002)
    f=op.flash_from_K([.4,.6],[179.1/105,74.2/105],100)
    cerca(f.split.beta,.51343,.0001)
    cerca(f.split.x[0],.29361,.0001)
    cerca(f.split.y[0],.50082,.0001)
    cerca(f.split.overall_balance_error,0,1e-9)

def e8b1():
    m=mod('disoluciones_no_ideales');g,a,ge=m.activity_properties([.25,.75],m.ConstantGamma([1.8,1.0]),298.15)
    cerca(a[0],.45,1e-12)
    cerca(m.R*298.15*math.log(g[0]),1457.02,.4)

def e8b7():
    m=mod('disoluciones_no_ideales');p,y,_,_=m.bubble_pressure([.45,.55],330,m.ConstantGamma([1.28,1.10]),m.DirectPsat([95,42]))
    cerca(p,80.13,1e-10);cerca(y[0],.68289,.00002)
    cerca((.45*95+.55*42-p)/p*100,-17.82,.08)

def e8b9():
    m=mod('disoluciones_no_ideales');p,y,_,_=m.bubble_pressure([.3,.45,.25],300,m.ConstantGamma([1.20,.92,1.35]),m.DirectPsat([120,65,25]))
    cerca(p,78.5475,1e-9)
    for got,expected in zip(y,[.54999,.34260,.10742]):cerca(got,expected,.00003)
    cerca(sum(y),1,1e-12)

def e9b6():
    m=mod('inmiscibles_y_arrastre_vapor');r=m.consumir_fases(2,1,.4441)
    cerca(r['n_v'],2.251745,.000005);cerca(r['n_a_residual'],.748255,.00001)
    cerca(r['residual_a'],0,1e-12);cerca(r['residual_b'],0,1e-12)
    assert 'B' in r['agotada']

def e9b7():
    m=mod('inmiscibles_y_arrastre_vapor');r=m.condensacion(10,.4441,18.0153,92.1384)
    cerca(r['n_b'],4.441,1e-10);cerca(r['m_b'],409.187,.006)
    cerca(r['w_b'],.803376,.00001);cerca(r['residual_m'],0,1e-9)

def e10b2():
    m=mod('propiedades_coligativas');molal=(12.817/128.17)/.5
    cerca(m.coligativa(5.12,molal),1.024,.00001)
    cerca(m.coligativa(2.53,molal),.506,.00001)

def e10b8():
    m=mod('disoluciones_electroliticas')
    for z,I,reference_dh,reference_dav in [(1,.001,.9636,.9651),(2,.001,.8622,.8674),(1,.01,.8894,.9023)]:
        cerca(m.gamma_ion(z,I,'dh',A=.509),reference_dh,.00015)
        cerca(m.gamma_ion(z,I,'davies',A=.509),reference_dav,.003)

def e11b4():
    m=mod('balances_materia');xs=m.caudales_componentes(250,[.12,.88])
    cerca(xs[0],30,1e-10);cerca(xs[1],220,1e-10)
    cerca(m.comprobar_residuos([250],xs,250)['residuo'],0,1e-12)

def e11b5():
    m=mod('balances_materia');o=m.base_masa_a_molar([36,84],[46.06844,18.01528]);
    cerca(sum((36,84)),120,1e-10)
    cerca(36/(36+84),.3,1e-12)
    # contraste de ida y vuelta de composición en masa ↔ molar
    cerca(sum(o['fracciones_molares']),1,1e-10)

def e12b1():
    m=mod('secado'); solidos=m.multiplicar(m.exacto(1000),m.exacto(.5));final=m.dividir(solidos,m.exacto(.8))
    cerca(float(final.valor),625,1e-12)
    cerca(float(m.restar(m.exacto(1000),final).valor),375,1e-12)
    cerca(float(final.valor)/.1,6250,1e-9)

def e12b6():
    m=mod('balances_materia'); f=150;x=.35;y=.55;xL=.15
    V=f*(x-xL)/(y-xL);L=f-V
    cerca(V,75,1e-10);cerca(L,75,1e-10)
    cerca(m.comprobar_residuos([f],[V,L],f)['residuo'],0,1e-12)

def e13b3():
    m=mod('reactivo_limitante');_,_,_,xi,left,formed=m.balance([m.Q(5),m.Q(7)],[1,1],[1],m.Q(.72))
    cerca(float(xi.v),3.6,1e-12)
    cerca(float(left[0].v),1.4,1e-12);cerca(float(left[1].v),3.4,1e-12)
    cerca(float(formed[0].v),3.6,1e-12)

def e14b1():
    m=mod('combustion');o,p=m.oxygen_stoich_formula('C2H6',12,m.ProductModel())
    cerca(o,42,1e-12);cerca(p['CO2'],24,1e-12);cerca(p['H2O'],36,1e-12)
    assert all(m.balance_ok(a,b) for a,b,_ in m.balance_residuals({'C2H6':12,'O2':o},{'CO2':24,'H2O':36}).values())

def e14b4():
    m=mod('combustion');o,p=m.oxygen_stoich_formula('C3H8',15,m.ProductModel());real=1.3*o
    cerca(o,75,1e-12);cerca(real,97.5,1e-12)
    cerca(real/.21,464.2857,.002);cerca(real*79/21,366.7857,.002)
    cerca(real-o,22.5,1e-12)

def e15b5():
    m=mod('psicrometria');p=.45*2.645;W=m.humidity_ratio_from_pw(p,98.)
    cerca(p,1.19025,1e-10);cerca(W,.0076455,.000006)
    cerca(2*W,.015291,.000012)

EJERCICIOS={
 '3.B.4':e3b4,'3.B.6':e3b6,'4.B.4':e4b4,'4.B.6':e4b6,
 '5.B.13':e5b13,'6.B.1':e6b1,'7.B.10':e7b10,'7.B.11':e7b11,
 '8.B.1':e8b1,'8.B.7':e8b7,'8.B.9':e8b9,'9.B.6':e9b6,'9.B.7':e9b7,
 '10.B.2':e10b2,'10.B.8':e10b8,'11.B.4':e11b4,'11.B.5':e11b5,
 '12.B.1':e12b1,'12.B.6':e12b6,'13.B.3':e13b3,'14.B.1':e14b1,
 '14.B.4':e14b4,'15.B.5':e15b5}

class CotejoBloqueNueve(unittest.TestCase):
    def test_guardia_presion_nan(self):
        with self.assertRaises(ValueError):mod('equilibrio_liquido_vapor').Component('A',6,1250,-45).boiling_temperature(float('nan'))
    def test_guardia_presion_infinita(self):
        with self.assertRaises(ValueError):mod('equilibrio_liquido_vapor').Component('A',6,1250,-45).boiling_temperature(float('inf'))
    def test_guardia_temperatura_nan(self):
        with self.assertRaises(ValueError):mod('equilibrio_liquido_vapor').Component('A',6,1250,-45).psat(float('nan'))
    def test_guardia_temperatura_infinita(self):
        with self.assertRaises(ValueError):mod('equilibrio_liquido_vapor').Component('A',6,1250,-45).psat(float('inf'))
    def test_guardia_coeficientes_no_finitos(self):
        for var in ['A','B','C']:
            p={'A':6.,'B':1250.,'C':-45.};p[var]=float('nan')
            with self.subTest(var=var), self.assertRaises(ValueError):
                mod('equilibrio_liquido_vapor').Component('invalido',p['A'],p['B'],p['C'])
    def test_guardia_intervalos_invalidos(self):
        for a,b in [(400,300),(float('inf'),400),(200,float('nan'))]:
            with self.subTest(a=a,b=b), self.assertRaises(ValueError):
                mod('equilibrio_liquido_vapor').Component('A',6,1250,-45,a,b)


def generar(fn):
    def prueba(self):fn()
    return prueba

for codigo,funcion in EJERCICIOS.items():
    setattr(CotejoBloqueNueve,'test_'+codigo.replace('.','_'),generar(funcion))

if __name__ == '__main__':unittest.main()

# Diez ejercicios nuevos adicionales, identificados después de contrastar la
# matriz de los ocho bloques previos (no se duplican identificadores).
def e7b12():
    m=mod('equilibrio_liquido_vapor'); ps=[.626*86.6/.4,.374*86.6/.6]
    r=m.raoult_from_pstar([.4,.6],ps)
    cerca(r['P'],86.6,1e-9);cerca(ps[0],135.529,.003)
    cerca(ps[1],53.9807,.003);cerca(r['K'][0]/r['K'][1],2.5107,.0003)

def e7b13():
    m=mod('operaciones_liquido_vapor');r=m.flash_from_K([.2,.5,.3],[2.584,1.239,.408],100)
    cerca(r.split.beta,.57898986,.00001)
    for a,b in zip(r.split.x,[.10432,.43922,.45646]):cerca(a,b,.00003)
    for a,b in zip(r.split.y,[.26957,.54420,.18623]):cerca(a,b,.00003)
    cerca(r.split.overall_balance_error,0,1e-9)

def e8b10():
    m=mod('disoluciones_no_ideales');vp=m.SimpleExpPsat([12.250,11.900],[2600,2750])
    r=m.bubble_temperature([.4,.6],100,m.ConstantGamma([1.25,1.1]),vp,340,360,1e-9)
    cerca(r[0],350.14607,.006);cerca(r[1][0],.622638,.00004)
    ideal=m.bubble_temperature([.4,.6],100,m.Ideal(),vp,350,365,1e-9)
    cerca(ideal[0],358.29973,.006)

def e9b8():
    m=mod('inmiscibles_y_arrastre_vapor')
    for presion,t,ya in [(.7,347.7391,.541426),(1.2,362.1516,.562484)]:
        r=m.temperatura_trifasica(m.AGUA_1,m.TOLUENO,presion)
        v=m.composicion_vapor(m.AGUA_1,m.TOLUENO,r.t,presion)
        cerca(r.t,t,.001);cerca(v['y_a'],ya,.00005)

def e10b9():
    m=mod('propiedades_coligativas')
    cerca(m.masa_molar_coligativa(1.86,3.423,.1,.186),342.3,.001)

def e11b6():
    m=mod('balances_materia');c=m.comprobar_residuos([160,240],[400],400)
    cerca(c['residuo'],0,1e-12)

def e12b7():
    m=mod('balances_materia');feed=250;ca=feed*.08;cake_ca=ca*.92
    cake=cake_ca/.65; filtrate=feed-cake;frac=(ca-cake_ca)/filtrate
    cerca(cake_ca,18.4,1e-9);cerca(cake,28.3077,.0001)
    cerca(frac,.00722,.00001)
    cerca(m.comprobar_residuos([feed],[cake,filtrate],feed)['residuo'],0,1e-9)

def e13b5():
    m=mod('combustion');rin=m.element_totals({'CH3OH':6})
    rout=m.element_totals({'CH3OH':1.2,'CO2':.8})
    hcho=rin['C']-rout['C']
    cerca(hcho,4,1e-12)
    cerca(rout['C']+hcho,rin['C'],1e-12)

def e14b5():
    m=mod('combustion');oxygen,_=m.oxygen_stoich_formula('C4H10',1,m.ProductModel())
    n=65/oxygen;air=350
    cerca(n,10,1e-12);cerca((air*.21/65-1)*100,13.0769,.0002)

def e15b7():
    m=mod('psicrometria');Pw=.7*2.338;W=m.humidity_ratio_from_pw(Pw,101.3)
    cerca(W,.01021,.000015)
    cerca(m.pw_from_humidity_ratio(W,101.3),1.6366,1e-10)
    cerca(Pw/7.382*100,22.2,.05)

EXTRAS={'7.B.12':e7b12,'7.B.13':e7b13,'8.B.10':e8b10,'9.B.8':e9b8,
 '10.B.9':e10b9,'11.B.6':e11b6,'12.B.7':e12b7,'13.B.5':e13b5,
 '14.B.5':e14b5,'15.B.7':e15b7}
for codigo,funcion in EXTRAS.items():
    assert codigo not in EJERCICIOS
    setattr(CotejoBloqueNueve,'test_'+codigo.replace('.','_'),generar(funcion))
