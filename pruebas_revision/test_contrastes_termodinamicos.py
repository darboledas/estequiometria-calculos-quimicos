# -*- coding: utf-8 -*-
"""Contrastes independientes de ecuaciones termodinámicas y validación de dominios.

Pruebas deterministas que no sustituyen una calibración experimental ni
la comparación de todos los ejercicios del libro.
"""
import math
import random
import unittest
from test_auditoria_integral import mod


class ContrastesTermodinamicos(unittest.TestCase):
    def test_gas_real_rechaza_valores_no_finitos(self):
        m=mod('gases_reales'); g=m.resolve_gas('N2')
        for s in ('nan','inf','-inf','NaN'):
            with self.subTest(s=s),self.assertRaises(ValueError):m.parse_num(s)
        for model in ('ideal','vdw','rk','srk','pr','lk'):
            for t,p in ((0,10),(300,0),(float('nan'),10),(300,float('inf'))):
                with self.subTest(model=model,T=t,P=p),self.assertRaises(ValueError):
                    m.model_state(model,t,p,g)
        for t,p in ((0,10),(300,0),(300,float('nan'))):
            with self.subTest(T=t,P=p),self.assertRaises(ValueError):m.virial_volume(t,p)

    def test_eos_cubicas_residuo_y_limite_diluido(self):
        m=mod('gases_reales');rng=random.Random(1983)
        for i in range(200):
            gas=m.resolve_gas(rng.choice(['CH4','N2','CO2','C3H8','O2']))
            model=('vdw','rk','srk','pr')[i%4]
            t=gas.Tc*rng.uniform(1.1,3.5)
            p=gas.Pc*10**rng.uniform(-5,-2)
            r=m.cubic_state(model,t,p,gas)
            a,b,c,d=r['poly'];z=r['Z']
            self.assertLess(abs(((a*z+b)*z+c)*z+d),1e-9)
            self.assertLess(abs(z-1),.08)
            self.assertGreater(r['Vm'],r['b'])

    def test_eos_coexistencia_igualdad_de_fugacidades(self):
        m=mod('gases_reales');g=m.resolve_gas('CH4')
        for model in ('vdw','rk','srk','pr'):
            for frac in (.72,.82,.88):
                r=m.saturation_pressure(model,frac*g.Tc,g)
                self.assertGreater(r['P'],0)
                self.assertLess(r['P'],g.Pc)
                self.assertAlmostEqual(r['fL']/r['fV'],1,delta=3e-7)
                self.assertLess(r['VmL'],r['VmV'])

    def test_antoine_agua_contraste_iapws_1992(self):
        a=mod('presion_vapor');w=mod('vapor_agua');coef=a.ANTOINE['agua']
        # La tabla docente no es una reproducción exacta de IAPWS.
        for T in (284.0,290,300,320,340,360,373.15,400,420,440,441):
            with self.subTest(T=T):
                aprox=a.antoine_pressure_kpa(T,coef)
                ref=w.psat_iapws_kpa(T-273.15)
                self.assertLess(abs(aprox/ref-1),.025)

    def test_nist_antoine_agua_conversion_bar_a_kpa(self):
        a=mod('presion_vapor');w=mod('vapor_agua')
        # NIST WebBook: 273–303 K, P en bar, A=5.40221, B=1838.675, C=-31.737.
        for T in (273.16,285,298,302):
            reference=100.0*10**(5.40221-1838.675/(T-31.737))
            iapws=w.psat_iapws_kpa(T-273.15)
            self.assertLess(abs(reference/iapws-1),.007)
            # Anticipa error frecuente: confundir bar con kPa.
            pdoc=a.antoine_pressure_kpa(T,a.ANTOINE['agua']) if T>=284 else None
            if pdoc is not None:self.assertLess(abs(pdoc/iapws-1),.025)

    def test_antoine_y_calculos_de_equilibrio_rechazan_nan(self):
        a=mod('presion_vapor'); v=mod('equilibrio_liquido_vapor'); op=mod('operaciones_liquido_vapor')
        for x in ('nan','inf','-inf'):
            for m in (a.parse_number,v.parse_decimal,op.parse_decimal):
                with self.subTest(parser=m.__name__,input=x),self.assertRaises(ValueError):m(x)

    def test_puntos_puros_fuera_del_intervalo_del_componente_ausente(self):
        v=mod('equilibrio_liquido_vapor')
        p=101.325;A=6.0
        c1=v.Component('Componente A',A,(A-math.log10(p))*350,0,300,370)
        c2=v.Component('Componente B',A,(A-math.log10(p))*410,0,390,430)
        for x,expected in (([1.,0.],350),([0.,1.],410)):
            T,P1,Y=v.bubble_temperature([c1,c2],x,p)
            Td,P2,X=v.dew_temperature([c1,c2],x,p)
            self.assertAlmostEqual(T.root,expected,delta=1e-7)
            self.assertAlmostEqual(Td.root,expected,delta=1e-7)
            self.assertEqual(Y,x);self.assertEqual(X,x)
            self.assertIsNone(P1[1] if x[0] else P1[0])
            P,partials,y=v.bubble_pressure([c1,c2],x,expected)
            Pr,xr=v.dew_pressure([c1,c2],x,expected)
            self.assertAlmostEqual(P,p,delta=1e-8)
            self.assertAlmostEqual(Pr,p,delta=1e-8)
            self.assertEqual(y,x);self.assertEqual(xr,x)
            self.assertEqual(partials[1] if x[0] else partials[0],0)
        with self.assertRaises(ValueError):
            v.bubble_temperature([c1,c2],[.5,.5],p)

    def test_vle_ideal_burbuja_rocio_reversibles(self):
        v=mod('equilibrio_liquido_vapor');P=101.325;A=6
        c1=v.Component('A',A,(A-math.log10(P))*350,0,300,430)
        c2=v.Component('B',A,(A-math.log10(P))*390,0,300,430)
        rng=random.Random(63014)
        for i in range(200):
            x=rng.uniform(.002,.998); comp=[x,1-x]
            method=('newton','secant','bisection')[i%3]
            rb,_,y=v.bubble_temperature([c1,c2],comp,P,method=method)
            rd,_,xr=v.dew_temperature([c1,c2],y,P,method=method)
            self.assertAlmostEqual(rb.root,rd.root,delta=2e-6)
            self.assertAlmostEqual(xr[0],x,delta=2e-7)

    def test_flash_multicomponente_y_cierre_de_materia(self):
        m=mod('operaciones_liquido_vapor');rng=random.Random(771)
        biphases=0
        for _ in range(500):
            n=rng.randint(2,6);z=[rng.random() for i in range(n)];z=[zi/sum(z) for zi in z]
            k=[10**rng.uniform(-1.5,1.5) for i in range(n)]
            r=m.flash_from_K(z,k,10)
            self.assertLessEqual(r.split.beta,1)
            self.assertGreaterEqual(r.split.beta,0)
            if r.state=='BIFASICO':
                biphases+=1;s=r.split
                self.assertAlmostEqual(sum(s.x),1,delta=1e-8)
                self.assertAlmostEqual(sum(s.y),1,delta=1e-8)
                for zi,xi,yi in zip(z,s.x,s.y):
                    self.assertAlmostEqual(zi,(1-s.beta)*xi+s.beta*yi,delta=3e-8)
        self.assertGreater(biphases,50)

    def test_rayleigh_con_solucion_analitica_independiente(self):
        m=mod('operaciones_liquido_vapor');rng=random.Random(240)
        for _ in range(200):
            alpha=rng.uniform(1.02,15); x0=rng.uniform(.08,.93);xf=x0*rng.uniform(.13,.91)
            r=m.rayleigh_from_final_x(15,x0,xf,alpha)
            integral=(math.log(x0/xf)-alpha*math.log((1-x0)/(1-xf)))/(alpha-1)
            self.assertAlmostEqual(r.integral,integral,delta=3e-8)
            self.assertAlmostEqual(r.N/15,math.exp(-integral),delta=3e-8)
            self.assertAlmostEqual(r.N+r.D,15,delta=1e-8)

    def test_gibbs_duhem_modelos_actividad(self):
        m=mod('disoluciones_no_ideales')
        models=(m.Margules1(.8),m.Margules2(.4,1.1),m.VanLaar(.5,.9),m.Wilson(.75,1.5))
        h=1e-6
        for model in models:
            for x in (.05,.2,.5,.77,.95):
                def lng(u):
                    g=model.gammas([u,1-u]);return [math.log(float(t)) for t in g]
                plus=lng(x+h);minus=lng(x-h)
                deriv=[(a-b)/(2*h) for a,b in zip(plus,minus)]
                # Gibbs–Duhem binario: x1 d(lnγ1)/dx1 + x2 d(lnγ2)/dx1=0.
                self.assertAlmostEqual(x*deriv[0]+(1-x)*deriv[1],0,delta=2e-7)

    def test_psicrometria_rechazo_de_no_finitos(self):
        m=mod('psicrometria')
        for w in (float('nan'),float('inf'),-float('inf')):
            with self.subTest(W=w),self.assertRaises(m.PsychrometricError):
                m.make_state(101.325,25,w,sigfigs=5,source_pair=('Tdb','W'))

    def test_psicrometria_mezcla_conservacion_materia_y_entalpia(self):
        m=mod('psicrometria')
        a=m.make_state(101.325,15,.004,sigfigs=5,source_pair=('Tdb','W'))
        b=m.make_state(101.325,32,.010,sigfigs=5,source_pair=('Tdb','W'))
        m1=m.Measurement(2.0,'2',3,0,False)
        m2=m.Measurement(3.0,'3',3,0,False)
        result,W,h=m.mix_states(a,m1,b,m2)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(W,(2*a.W+3*b.W)/5,delta=1e-12)
        self.assertAlmostEqual(h,(2*a.h+3*b.h)/5,delta=1e-12)
        self.assertAlmostEqual(result.h,h,delta=1e-9)
        self.assertAlmostEqual(result.W,W,delta=1e-9)

    def test_wet_bulb_dew_point_order(self):
        m=mod('psicrometria'); P=101.325
        for T in (10,20,30,40):
            for rh in (.2,.4,.6,.8,.95):
                pw=rh*m.saturation_pressure_water(T)
                w=m.humidity_ratio_from_pw(pw,P)
                s=m.make_state(P,T,w,sigfigs=5,source_pair=('Tdb','W'))
                self.assertLessEqual(s.Tdp,s.Twb+1e-6)
                self.assertLessEqual(s.Twb,T+1e-6)

if __name__=='__main__':unittest.main()
