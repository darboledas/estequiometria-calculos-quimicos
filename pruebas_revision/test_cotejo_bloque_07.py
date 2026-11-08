# -*- coding: utf-8 -*-
"""Bloque VII: libro definitivo, solucionario y aplicaciones.

Las operaciones algebraicas externas se declaran como tales; no presuponen
que una aplicación resuelva el ejercicio completo en un único comando.
"""
import math
import unittest
import numpy as np
from test_auditoria_integral import mod


class CotejoBloqueSiete(unittest.TestCase):
    def test_2_B_6_reynolds(self):
        m=mod('unidades_y_dimensiones')
        d=m.convertir_unidad(5,'cm','m')
        re=997*1.5*d/(.89e-3)
        self.assertAlmostEqual(re,84016.85,delta=.02)

    def test_3_B_14_caliza(self):
        m=mod('masa_molar')
        mmca=float(m.calculate_molar_mass('CaCO3').raw_mass)
        mmcao=float(m.calculate_molar_mass('CaO').raw_mass)
        impurezas=250*(1-.88)
        teo=250*.88/mmca*mmcao
        self.assertAlmostEqual(teo,123.3,delta=.2)
        self.assertAlmostEqual(.9*teo,110.9,delta=.2)
        self.assertAlmostEqual(impurezas,30.,delta=1e-10)

    def test_3_B_15_conversion_so2(self):
        a=mod('ajuste_ecuaciones'); r=mod('reactivo_limitante')
        self.assertEqual(a.ajustar(['SO2','O2'],['SO3']),[2,1,2])
        _,ix,_,advance,left,formed=r.balance([r.Q(10),r.Q(8)],[2,1],[2],r.Q(.75))
        self.assertEqual(ix,[0])
        self.assertAlmostEqual(float(advance.v),3.75,delta=1e-10)
        self.assertAlmostEqual(float(left[0].v),2.5,delta=1e-10)
        self.assertAlmostEqual(float(left[1].v),4.25,delta=1e-10)
        self.assertAlmostEqual(float(formed[0].v),7.5,delta=1e-10)

    def test_4_B_7_dalton(self):
        m=mod('gases_ideales_y_mezclas')
        p=[25000,35000,140000]
        n=[m.solve_ideal(pi,50,None,400)['n'] for pi in p]
        self.assertAlmostEqual(n[0],375.9,delta=.2)
        self.assertAlmostEqual(n[1],526.2,delta=.3)
        self.assertAlmostEqual(n[2],2104.5,delta=1)
        self.assertAlmostEqual(p[0]/sum(p),.125,delta=1e-12)
        self.assertAlmostEqual(50*p[0]/sum(p),6.25,delta=1e-12)

    def test_4_C_10_absorbedor_benceno(self):
        m=mod('gases_ideales_y_mezclas')
        nin=m.solve_ideal(120000,100,None,350)['n']
        nout=m.solve_ideal(101300,95,None,300)['n']
        benz1=(1/78.11)/(1/78.11+3/28.014)
        n_b1=nin*benz1
        n_b2=nout-nin*(1-benz1)
        self.assertAlmostEqual(n_b1,440.33,delta=.06)
        self.assertAlmostEqual((n_b1-n_b2)*78.11/1000,20.74,delta=.03)
        self.assertAlmostEqual((n_b1-n_b2)/n_b1*100,60.29,delta=.06)
        self.assertAlmostEqual(n_b2+nin*(1-benz1),nout,delta=1e-8)

    def test_4_C_11_absorbedor_nh3(self):
        m=mod('gases_ideales_y_mezclas')
        nin=m.solve_ideal(120000,100,None,300)['n']
        nout=nin*.8/.98
        vout=m.solve_ideal(100000,None,nout,280)['V']
        n_abs=nin*.2-nout*.02
        self.assertAlmostEqual(vout,91.43,delta=.02)
        self.assertAlmostEqual(n_abs*17.031/1000,15.05,delta=.03)
        self.assertAlmostEqual(100*n_abs/(nin*.2),91.84,delta=.03)

    def test_5_B_6_virial_isopropanol_y_errata_solu(self):
        m=mod('gases_reales')
        r=m.virial_volume(473,10,B=-.388,C=-.026)
        self.assertAlmostEqual(r['Vm'],3.48669,delta=.00005)
        self.assertAlmostEqual(r['Z'],.886581,delta=.00001)
        v=r['Vm'];rt=m.R_BAR*473
        # Polinomio correcto: P*v³ - RT*v² - RT*B*v - RT*C=0.
        self.assertAlmostEqual(10*v**3-rt*v*v+rt*.388*v+rt*.026,0,delta=1e-6)
        # En el solucionario la cúbica impresa omite los factores RT y signos.
        self.assertGreater(abs(10*v**3-rt*v*v-.388*v-.026),1.)

    def test_5_B_7_vdw_parametros_criticos_etano(self):
        m=mod('gases_reales')
        r=m.R_BAR;T=305.3;P=48.7
        a=27*r*r*T*T/(64*P);b=r*T/(8*P)
        self.assertAlmostEqual(a,5.5818,delta=.002)
        self.assertAlmostEqual(b,.065154,delta=.000002)
        self.assertAlmostEqual(3*b,.195462,delta=.000005)

    def test_5_B_12_leekesler_datos_explicitos(self):
        m=mod('gases_reales')
        g=m.Gas('TEST','fluido','X',425.125,37.96,200.,.201)
        r=m.lee_kesler(511,5.0,g)
        self.assertAlmostEqual(r['Z'],.975805,delta=.00003)
        self.assertAlmostEqual(r['Tr'],1.2020,delta=.0001)

    def test_5_B_16_fugacidad_vdw(self):
        m=mod('gases_reales')
        r=m.vdw_state_from_ab(300,50,3.64,.0427)
        self.assertAlmostEqual(r['Z'],.733202,delta=.00003)
        self.assertAlmostEqual(r['phi'],.793505,delta=.00002)
        self.assertAlmostEqual(r['fugacity'],39.6752,delta=.002)
        self.assertAlmostEqual((r['phi']-1)*100,-20.6495,delta=.003)

    def test_5_B_20_extremos_vdw_con_referencia(self):
        m=mod('gases_reales')
        a=3.64;b=.0427;rt=m.R_BAR*280.1
        # dP/dV=0 => -RT*V^3 +2a*(V-b)^2=0.
        roots=np.roots([-rt,2*a,-4*a*b,2*a*b*b])
        vm=sorted(float(z.real) for z in roots if abs(z.imag)<1e-7 and z.real>b)
        self.assertEqual(len(vm),2)
        self.assertAlmostEqual(vm[0],.0954141,delta=.000002)
        self.assertAlmostEqual(vm[1],.184871,delta=.000002)
        pressures=[rt/(v-b)-a/v**2 for v in vm]
        self.assertAlmostEqual(pressures[0],41.9639,delta=.03)
        self.assertAlmostEqual(pressures[1],57.3050,delta=.03)

    def test_6_B_8_acetona_camara(self):
        p=mod('presion_vapor');g=mod('gases_ideales_y_mezclas')
        pv=p.antoine_pressure_kpa(313,p.ANTOINE['acetona'])
        n=g.solve_ideal(pv*1000,10,None,313)['n']
        self.assertAlmostEqual(pv,56.2086,delta=.0001)
        self.assertAlmostEqual(n*58.08/1000,12.55,delta=.05)
        self.assertAlmostEqual(101.3+pv,157.5,delta=.08)

    def test_6_B_12_sublimacion_clausius(self):
        p=mod('presion_vapor')
        v=p.cc_pressure2(1.2,250,270,52000)
        self.assertAlmostEqual(v,7.65537,delta=.00005)
        self.assertAlmostEqual(p.cc_temperature2(1.2,250,v,52000),270,delta=1e-8)

    def test_6_C_2_agua_50kpa(self):
        p=mod('presion_vapor')
        t=p.antoine_temperature_k(50,p.ANTOINE['agua'])
        self.assertAlmostEqual(t,354.536,delta=.005)
        self.assertAlmostEqual(t-273.15,81.386,delta=.005)
        self.assertAlmostEqual(p.antoine_pressure_kpa(t,p.ANTOINE['agua']),50.,delta=1e-9)

    def test_7_B_6_tabla_benceno_tolueno(self):
        m=mod('equilibrio_liquido_vapor')
        P=101.3
        datos=[(101.3,39.6,1.,1.),(116.9,46.,.7800,.9001),
               (135.4,54.,.5811,.7767),(155.7,63.3,.4113,.6321),
               (179.1,74.2,.2583,.4568),(204.2,86.,.1294,.2609),
               (233.,99.,.0172,.0395),(240.,101.3,0.,0.)]
        for pa,pb,xx,yy in datos:
            x=(P-pb)/(pa-pb)
            if x>1 and x<1+1e-12:x=1.
            r=m.raoult_from_pstar([x,1-x],[pa,pb])
            self.assertAlmostEqual(r['P'],P,delta=1e-10)
            self.assertAlmostEqual(x,xx,delta=.00015)
            self.assertAlmostEqual(r['y'][0],yy,delta=.00015)

    def test_7_B_7_volatilidad_constante(self):
        m=mod('equilibrio_liquido_vapor')
        for x,y in [(.1,.2174),(.3,.5172),(.5,.7143),(.7,.8537),(.9,.9574)]:
            # Relación algebraica que usa el módulo para la volatilidad relativa.
            out=2.5*x/(1+1.5*x)
            self.assertAlmostEqual(out,y,delta=.00006)
            self.assertGreater(out,x)

    def test_7_B_8_curvas_presiones_vapor(self):
        p=mod('presion_vapor');e=mod('equilibrio_liquido_vapor')
        pa=p.antoine_pressure_kpa(373,p.ANTOINE['benceno'])
        pb=p.antoine_pressure_kpa(373,p.ANTOINE['tolueno'])
        self.assertAlmostEqual(pa,179.308,delta=.01)
        self.assertAlmostEqual(pb,73.8306,delta=.01)
        for i in range(41):
            x=i/40
            r=e.raoult_from_pstar([x,1-x],[pa,pb])
            self.assertAlmostEqual(r['P'],pb+x*(pa-pb),delta=1e-9)
            self.assertAlmostEqual(sum(r['y']),1,delta=1e-12)
            self.assertAlmostEqual(sum([x,1-x]),1,delta=1e-12)

    def test_8_B_8_rocio_margules(self):
        m=mod('disoluciones_no_ideales')
        ps=m.DirectPsat([110.,48.])
        P,x,g,it,err,res=m.dew_pressure_binary(.6,300,m.Margules1(.9),ps,1e-12)
        self.assertAlmostEqual(P,89.3067,delta=.0001)
        self.assertAlmostEqual(x[0],.322137,delta=.000002)
        self.assertAlmostEqual(g[0],1.51217,delta=.00002)
        self.assertAlmostEqual(res,0,delta=1e-9)

    def test_8_B_11_temperatura_rocio_margules(self):
        m=mod('disoluciones_no_ideales')
        ps=m.SimpleExpPsat([12.250,11.900],[2600.,2750.])
        r=m.dew_temperature([.55,.45],80.,m.Margules1(.75),ps,330,365,1e-6,1e-11)
        self.assertAlmostEqual(r[0],342.0731,delta=.002)
        self.assertAlmostEqual(r[1][0],.2877884,delta=.00005)
        self.assertAlmostEqual(r[8],1.,delta=2e-8)

    def test_10_B_5_glucosa_raoult(self):
        m=mod('propiedades_coligativas')
        r=m.composicion(18.016,180.16,180.153,18.0153)
        v=m.vapor_ideal(3.17,r['x1'])
        self.assertAlmostEqual(r['n1'],10.,delta=1e-10)
        self.assertAlmostEqual(r['n2'],.1,delta=1e-10)
        self.assertAlmostEqual(r['x1'],.99009901,delta=1e-8)
        self.assertAlmostEqual(v['presion'],3.13861,delta=.00001)
        self.assertAlmostEqual(v['descenso'],.031386,delta=.00001)

    def test_10_B_7_dh_vs_davies(self):
        m=mod('disoluciones_electroliticas')
        ions=m.iones_electrolito(.001,[('Ca',2,1),('Cl',-1,2)])
        I=m.fuerza_ionica(ions)
        self.assertAlmostEqual(I,.003,delta=1e-15)
        self.assertAlmostEqual(m.balance_carga(ions),0,delta=1e-15)
        dh=m.gamma_media_dh(I,1,2,2,-1,'dh')
        dav=m.gamma_media_dh(I,1,2,2,-1,'davies')
        self.assertAlmostEqual(dh,.8795,delta=.0007)
        self.assertAlmostEqual(dav,.8873,delta=.0007)
        self.assertGreater(dav,dh)

    def test_11_B_9_dilucion(self):
        b=mod('balances_materia')
        soluto=100*.40;out=soluto/.16;water=out-100
        self.assertAlmostEqual(out,250,delta=1e-12)
        self.assertAlmostEqual(water,150,delta=1e-12)
        self.assertAlmostEqual(b.comprobar_residuos([100,water],[out],out)['residuo'],0,delta=1e-10)

    def test_11_B_10_mezcla_dos_corrientes(self):
        b=mod('balances_materia')
        eqs=[b.Ecuacion([1.,1.],500,'total'),b.Ecuacion([.1,.3],90,'KCl')]
        s=b.resolver_lineal(['m1','m2'],eqs)
        self.assertEqual(s.estado,'unico')
        self.assertAlmostEqual(s.valores['m1'],300,delta=1e-8)
        self.assertAlmostEqual(s.valores['m2'],200,delta=1e-8)
        self.assertAlmostEqual(.1*s.valores['m1']+.3*s.valores['m2'],90,delta=1e-8)

    def test_12_B_10_reparto_fenol_agua(self):
        b=mod('balances_materia')
        eqs=[b.Ecuacion([1.,1.],100,'total'),b.Ecuacion([.703,.0842],40,'fenol')]
        s=b.resolver_lineal(['fenol','agua'],eqs)
        self.assertEqual(s.estado,'unico')
        self.assertAlmostEqual(s.valores['fenol'],51.0343,delta=.0002)
        self.assertAlmostEqual(s.valores['agua'],48.9657,delta=.0002)

    def test_14_B_11_combustion_incompleta_soporte_balance(self):
        c=mod('combustion')
        # Porcentaje de C a CO2, O2 consumido por balance elemental.
        moles=20;co2=.75*moles;co=.25*moles;h2o=2*moles
        o2=co2+co/2+h2o/2
        self.assertAlmostEqual(o2,37.5,delta=1e-12)
        self.assertAlmostEqual(co2+co,moles,delta=1e-12)
        self.assertAlmostEqual(2*h2o,4*moles,delta=1e-12)
        rr=c.balance_residuals({'CH4':20,'O2':o2}, {'CO2':co2,'CO':co,'H2O':h2o})
        for a,b,res in rr.values():
            self.assertAlmostEqual(res,0,delta=1e-9)

    def test_14_B_13_orsat(self):
        m=mod('combustion')
        co2,co,o2=10.5,1.,4.5
        nitrogen=100-co2-co-o2
        incoming=nitrogen*21/79
        self.assertEqual(nitrogen,84.)
        self.assertEqual(co2+co,11.5)
        self.assertAlmostEqual(incoming,22.329,delta=.002)
        wet,dry,nt,nd=m.gas_compositions({'CO2':co2,'CO':co,'O2':o2,'N2':nitrogen},3)
        self.assertAlmostEqual(nd,100,delta=1e-12)
        self.assertAlmostEqual(dry['CO2'],.105,delta=1e-12)

    def test_8_psat_directa_rechaza_no_finitos(self):
        m=mod('disoluciones_no_ideales')
        for vv in ([100,float('nan')],[float('inf'),50],[-1,50],[0,50],[]):
            with self.subTest(vv=vv),self.assertRaises(ValueError):m.DirectPsat(vv).psat(300)

    def test_8_psat_exp_rechaza_coefs_y_desbordamiento(self):
        m=mod('disoluciones_no_ideales')
        for v in (m.SimpleExpPsat([12,float('nan')],[2000,3000]),
                  m.SimpleExpPsat([12,11],[2000]),
                  m.SimpleExpPsat([1000,12],[2000,3000])):
            with self.subTest(v=v),self.assertRaises(ValueError):v.psat(300)
        with self.assertRaises(ValueError):m.SimpleExpPsat([12,11],[2000,3000]).psat(float('nan'))

    def test_8_psat_antoine_rechaza_datos_invalidos(self):
        m=mod('disoluciones_no_ideales')
        for v in (m.AntoinePsat([6,float('inf')],[1000,1100],[0,0],T_scale='K'),
                  m.AntoinePsat([6,5],[1000,1100],[0],T_scale='K'),
                  m.AntoinePsat([1000,5],[1000,1100],[0,0],T_scale='K'),
                  m.AntoinePsat([6,5],[1000,1100],[0,0],T_scale='F')):
            with self.subTest(v=v),self.assertRaises(ValueError):v.psat(300)
        with self.assertRaises(ValueError):m.AntoinePsat([6,5],[1000,1100],[0,0],T_scale='K').psat(float('inf'))


if __name__ == '__main__':
    unittest.main()
