# -*- coding: utf-8 -*-
"""Bloque VIII: comparación de 40 ejercicios identificados y cuatro controles Antoine.

No todos los ejercicios se resuelven en un único comando: algunos contrastes
combinan llamadas directas con balances algebraicos auxiliares explícitos.
"""
import math
import unittest
from test_auditoria_integral import mod


def ck(*triples):
    """(valor, referencia, tolerancia absoluta), conservando valores internos."""
    return list(triples)


def v2b3():
    u=mod('unidades_y_dimensiones');return ck((u.convertir_unidad(150,'cal','J'),627.6,1e-10))
def v2b4():
    u=mod('unidades_y_dimensiones');return ck((u.convertir_unidad(12.5,'cm/s','m/h'),450,1e-10))
def v2b5():
    u=mod('unidades_y_dimensiones');return ck((.365*u.convertir_unidad(1,'Pa','atm')*1e6,3.6022699,1e-6),(4.28e-5*u.convertir_unidad(1,'m3','L'),.0428,1e-12))
def v3b1():
    m=float(mod('masa_molar').calculate_molar_mass('CO2').raw_mass);return ck((m,44.01,.02),(44/m,.99977,.0005))
def v3b2():return ck((.50*6.02214076e23,3.01107038e23,1e14))
def v3b3():
    m=float(mod('masa_molar').calculate_molar_mass('H2O').raw_mass)
    return ck((3.01e23/6.02214076e23*m,9.0043,.025))
def v4b2():
    m=mod('gases_ideales_y_mezclas');v=4/3*math.pi*25**3
    n=m.solve_ideal(100000,v,None,300)['n']
    return ck((n*.029,76094.1605,.04),(m.solve_ideal(None,v,n,300)['P'],100000,1e-8))
def v4b3():
    m=mod('gases_ideales_y_mezclas');n=m.solve_ideal(120000,100,None,293)['n']
    return ck((n*16.04/1000,79.010,.04))
def v4b5():
    m=mod('gases_ideales_y_mezclas');n=m.solve_ideal(415000,.020,None,320)['n']
    he=(10-2.016*n)/(4.0026-2.016);h2=n-he
    return ck((n,3.1196,.001),(he*4.0026,7.477,.04),(h2*2.016,2.523,.04))
def v5b4():
    m=mod('gases_reales');g=m.gas_with_overrides('metano','190.6','45.99','0.0114')
    o=m.cubic_state('pr',300,50,g)
    return ck((o['A'],.162589,.0002),(o['B'],.053739,.0001),(o['Z'],.901756,.0002))
def v5b9():
    m=mod('gases_reales');g=m.gas_with_overrides('gas personal','416.3','66.8','0')
    r=sorted(m.eos_roots('rk',333,13.91,g)['roots']);l=m.cubic_state('rk',333,13.91,g,'liquido');v=m.cubic_state('rk',333,13.91,g,'vapor')
    assert len(r)==3 and abs(l['phi']-v['phi'])>.1
    return ck((r[0],.0358163,.0001),(r[-1],.848778,.0002),(l['Vm'],.0712905,.0003),(v['Vm'],1.68945,.003))
def v6b2():
    p=mod('presion_vapor');dh=p.cc_enthalpy(25,273,58.4,293)
    return ck((dh/1000,28.2134,.01),(dh/1000/.07412,380.645,.12))
def v6b3():
    p=mod('presion_vapor')
    return ck((p.cc_pressure2(.61,273,293,45050),2.36,.12),
              (p.cc_pressure2(.61,273,353,45050),54.80,.12),
              (p.cc_pressure2(101.3,373,293,40660),2.82,.12),
              (p.cc_pressure2(101.3,373,353,40660),48.20,.12))
def v6b4():
    g=mod('gases_ideales_y_mezclas');n=g.solve_ideal(110000,2e-4,None,323)['n']
    pN=g.solve_ideal(None,3.83e-4,n,308)['P']/1000
    return ck((101.3-pN,46.5263,.005))
def v6b5():
    dv=1/13690-1/14193
    return ck((dv,2.58875e-6,3e-11),(234.33*math.exp(dv*9e5/9787.6),234.3858,.002))
def v6b6():
    m=mod('presion_vapor');a=m.AntoineData('6.B.6',6.06197,1171.20,-46.16,200,400)
    return ck((m.antoine_temperature_k(50,a),314.599,.004),(m.antoine_pressure_kpa(300,a),28.0569,.003))
def v6b7():
    m=mod('presion_vapor');a=m.AntoineData('6.B.7',6.04117,1208.30,-51.15,250,400)
    return ck((m.antoine_pressure_kpa(300,a),15.3333,.004))
def v7b4():
    m=mod('equilibrio_liquido_vapor');c=[m.Component('hexano',6.00265,1171.531,-48.780,245,370),m.Component('heptano',6.01876,1264.370,-56.510,270,400)]
    r,ps,y=m.bubble_temperature(c,[.1,.9],100)
    return ck((r.root,366.82004,.002),(y[0],.208475,.00004),(.1*ps[0]+.9*ps[1],100,1e-7))
def v7b5():
    m=mod('equilibrio_liquido_vapor');c=[m.Component('acetona',6.25017,1214.208,-43.198,241,350),m.Component('acetonitrilo',6.27873,1355.374,-37.853,288,362)]
    r,ps,x=m.dew_temperature(c,[.4,.6],65)
    return ck((r.root,333.81047,.004),(x[0],.220244,.00004),(.4*65/ps[0]+.6*65/ps[1],1,1e-9))
def v7b9():
    m=mod('equilibrio_liquido_vapor');r=m.raoult_from_pstar([.25,.5,.25],[103.36,49.56,16.33]);return ck((r['P'],54.7025,1e-10),(r['y'][0],.472373,.000003),(r['y'][1],.452996,.000003))
def v8b2():
    m=mod('disoluciones_no_ideales');g,a,ge=m.activity_properties([.4,.6],m.ConstantGamma([1.35,1.12]),310)
    return ck((ge,.188039,.00002),(ge*8.314*310,484.64,.07))
def v8b4():
    m=mod('disoluciones_no_ideales');g,_,ge=m.activity_properties([.35,.65],m.Margules2(1.45,.65))
    return ck((g[0],1.45648,.00002),(g[1],1.23001,.00002),(ge,.266175,.00002))
def v8b5():
    m=mod('disoluciones_no_ideales');a,_,_=m.activity_properties([.2,.8],m.Margules2(1.2,.8));b,_,_=m.activity_properties([.2,.8],m.VanLaar(1.2,.8))
    return ck((a[0],1.946,.002),(a[1],1.059,.002),(b[0],1.886,.002),(b[1],1.061,.002))
def v9b2():
    m=mod('equilibrio_liquido_liquido');dw,lo,hi=m.beysens(.01);r=m.regla_palanca(1.5,.5,lo,hi)
    return ck((dw,.42310786,.000002),(lo,.323446,.000002),(r.l1,.874082,.00001),(r.residuo_a,0,1e-12))
def v9b3():
    m=mod('inmiscibles_y_arrastre_vapor');r=m.temperatura_trifasica(m.AGUA_1,m.TOLUENO,.8);v=m.composicion_vapor(m.AGUA_1,m.TOLUENO,r.t,.8)
    assert math.isfinite(r.residual_bar)
    return ck((r.t,351.1889,.0002),(v['y_a'],.546636,.00006),(v['m_b_a'],4.24179,.0005))
def v9b4():
    m=mod('inmiscibles_y_arrastre_vapor');r=m.temperatura_trifasica(m.AGUA_1,m.ANILINA,1.01325);v=m.composicion_vapor(m.AGUA_1,m.ANILINA,r.t,1.01325)
    return ck((r.t,371.52376,.0004),(v['y_a'],.943355,.00004),(v['m_b_a'],.310397,.00003))
def v10b3():
    m=mod('propiedades_coligativas');i=m.factor_vanthoff(3.4,1.86,1)
    return ck((i,1.82795698,1e-8),((i/2-1)*100,-8.60215,.005))
def v10b4():
    m=mod('propiedades_coligativas');return ck((m.presion_osmotica(9/180.16,298.15),1.23838,.0007))
def v11b1():
    m=mod('balances_materia');r=m.comprobar_residuos([125,75],[200],200)
    return ck((r['residuo'],0,1e-12))
def v11b2():
    m=mod('balances_materia');r=m.inventario_lineal(420,[(180,0)],[(145,0)],3,4)
    return ck((r[-1]['inventario'],525,1e-12),(r[-1]['acumulacion'],35,1e-12))
def v11b3():
    m=mod('balances_materia');r=m.inventario_lineal(600,[],[(24,0)],15,4)
    return ck((r[-1]['inventario'],240,1e-10))
def v12b2():
    m=mod('secado');w=m.multiplicar(m.exacto(100),m.exacto(.7));e=m.multiplicar(w,m.exacto(.6));res=m.restar(w,e);fin=m.sumar(m.exacto(30),res)
    return ck((float(e.valor),42,1e-12),(float(fin.valor),58,1e-12))
def v12b5():
    m=mod('balances_materia');sol=4000*.1;p1=sol/.2;p2=sol/.5;e1=4000-p1;e2=p1-p2;r=m.comprobar_residuos([4000],[e1,e2,p2],4000)
    return ck((e1,2000,1e-12),(e2,1200,1e-12),(p2,800,1e-12),(r['residuo'],0,1e-12))
def v13b2():
    m=mod('reactivo_limitante');_,_,_,xi,left,formed=m.balance([m.Q(8)],[2],[1,3],m.Q(.6))
    return ck((float(xi.v),2.4,1e-12),(float(left[0].v),3.2,1e-12),(float(formed[1].v),7.2,1e-12))
def v13b4():
    m=mod('reactivo_limitante');_,_,_,xi,left,formed=m.balance([m.Q(4),m.Q(14.4)],[1,3],[2],m.Q(.65))
    return ck((float(xi.v),2.6,1e-12),(float(left[0].v),1.4,1e-12),(float(left[1].v),6.6,1e-12),(float(formed[0].v),5.2,1e-12))
def v14b2():
    m=mod('combustion');o,p=m.oxygen_stoich_formula('C3H8O',5,m.ProductModel())
    return ck((o,22.5,1e-12),(p['CO2'],15,1e-12),(p['H2O'],20,1e-12))
def v14b3():
    m=mod('combustion');o,p=m.oxygen_stoich_formula('CH4',25,m.ProductModel())
    return ck((o,50,1e-12),(o/.21,238.09524,.0001))
def v15b1():
    m=mod('psicrometria');return ck((1.8/101.3,.01777,.00002),(1.8/(101.3-1.8),.018090,.00001),(m.humidity_ratio_from_pw(1.8,101.3),.01125,.00002))
def v15b3():
    m=mod('psicrometria');p=5.628;P=101.325
    return ck((p/P,.055544,.000006),(p/(P-p),.058811,.00001),(m.humidity_ratio_from_pw(p,P),.03657,.00003))
def v15b4():
    m=mod('psicrometria');P=101.325;W=.01;p=m.pw_from_humidity_ratio(W,P);ws=m.humidity_ratio_from_pw(4.245,P)
    return ck((p,1.604,.002),(100*p/4.245,37.8,.2),(100*W/ws,36.8,.25))

EXERCISES={
 '2.B.3':v2b3,'2.B.4':v2b4,'2.B.5':v2b5,'3.B.1':v3b1,'3.B.2':v3b2,'3.B.3':v3b3,
 '4.B.2':v4b2,'4.B.3':v4b3,'4.B.5':v4b5,'5.B.4':v5b4,'5.B.9':v5b9,
 '6.B.2':v6b2,'6.B.3':v6b3,'6.B.4':v6b4,'6.B.5':v6b5,'6.B.6':v6b6,'6.B.7':v6b7,
 '7.B.4':v7b4,'7.B.5':v7b5,'7.B.9':v7b9,'8.B.2':v8b2,'8.B.4':v8b4,'8.B.5':v8b5,
 '9.B.2':v9b2,'9.B.3':v9b3,'9.B.4':v9b4,'10.B.3':v10b3,'10.B.4':v10b4,
 '11.B.1':v11b1,'11.B.2':v11b2,'11.B.3':v11b3,'12.B.2':v12b2,'12.B.5':v12b5,
 '13.B.2':v13b2,'13.B.4':v13b4,'14.B.2':v14b2,'14.B.3':v14b3,
 '15.B.1':v15b1,'15.B.3':v15b3,'15.B.4':v15b4}
assert len(EXERCISES)==40

class CotejoBloqueOcho(unittest.TestCase):
    def test_guardia_nan(self):
        m=mod('inmiscibles_y_arrastre_vapor')
        with self.assertRaises(ValueError):m.Antoine('nulo',float('nan'),1000,-40,18)
        with self.assertRaises(ValueError):m.Antoine('nulo',5,float('nan'),-40,18)
    def test_guardia_infinito(self):
        m=mod('inmiscibles_y_arrastre_vapor')
        with self.assertRaises(ValueError):m.Antoine('nulo',float('inf'),1000,-40,18)
        with self.assertRaises(ValueError):m.Antoine('nulo',5,1000,float('inf'),18)
    def test_guardia_intervalos(self):
        m=mod('inmiscibles_y_arrastre_vapor')
        with self.assertRaises(ValueError):m.Antoine('nulo',5,1000,-40,18,400,300)
        with self.assertRaises(ValueError):m.Antoine('nulo',5,1000,-40,-1)
        with self.assertRaises(ValueError):m.Antoine('nulo',5,1000,-40,18,float('nan'),400)
    def test_guardia_subdesbordamiento(self):
        m=mod('inmiscibles_y_arrastre_vapor')
        a=m.Antoine('extremo',5,100000,0,18)
        with self.assertRaises(ValueError):a.presion_bar(100)


def make_test(fn):
    def test(self):
        for actual,reference,tolerance in fn():
            self.assertAlmostEqual(actual,reference,delta=tolerance)
    return test

for exercise,fn in EXERCISES.items():
    setattr(CotejoBloqueOcho,'test_'+exercise.replace('.','_'),make_test(fn))

if __name__=='__main__':unittest.main()
