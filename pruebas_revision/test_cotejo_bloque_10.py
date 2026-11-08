# -*- coding: utf-8 -*-
"""Bloque X: cotejos inéditos con libro definitivo y solucionario (2026-11-07).

La referencia y la tolerancia de cada ejercicio se registran en la matriz X.
No equivale a validación experimental de modelos ni a certificación del manual.
"""
import math
import unittest
from test_auditoria_integral import mod

class CotejoBloqueX(unittest.TestCase):
    def check(self, got, reference, abs_tol):
        self.assertTrue(math.isfinite(float(got)), f'No finito: {got}')
        self.assertAlmostEqual(float(got),reference,delta=abs_tol)

    def test_5_B_15_SRK_propano(self):
        m=mod('gases_reales')
        g=m.gas_with_overrides('propano','369.8','42.5','0.152')
        r=m.cubic_state('SRK',400.,30.,g)
        self.check(r['A'],0.243344,2e-6); self.check(r['B'],0.0565402,2e-7)
        self.check(r['Z'],0.789516,2e-6); self.check(r['Vm'],0.875253,2e-6)
        self.check(30*r['Vm']/(m.R_BAR*400),r['Z'],1e-9)

    def test_5_B_17_saturacion_PR(self):
        m=mod('gases_reales')
        g=m.gas_with_overrides('propano','369.8','42.5','0.152')
        r=m.saturation_pressure('PR',331.,g)
        self.check(r['P'],20.36572,.00003)
        self.check(r['ZL'],.0760207,1e-6);self.check(r['ZV'],.683357,1e-6)
        self.check(r['VmL'],.102729,1e-6);self.check(r['VmV'],.923443,1e-6)
        self.check(r['phiL']-r['phiV'],0,1e-9)

    def test_5_B_19_virial_tercer_orden(self):
        m=mod('gases_reales')
        Z=1-.19770/4+.014143/4**2
        P=Z*m.R_BAR*510/4
        r=m.virial_volume(510,P,B=-.19770,C=.014143)
        self.check(Z,.95145894,2e-8);self.check(P,10.08636,1e-5)
        self.check(r['Vm'],4.,1e-8);self.check(r['Z'],Z,1e-9)
        self.check((1/Z-1)*100,5.10,.01)

    def test_6_B_10_duhring(self):
        m=mod('presion_vapor');a,b,r2,t=m.duhring_fit([(315.,7.50),(355.,47.20)],m.find_antoine('agua'))
        tref,p=m.duhring_pressure_at_temperature(335.,a,b,m.find_antoine('agua'))
        self.check(t[0],313.566,.002);self.check(t[1],353.107,.002)
        self.check(tref,333.337,.002);self.check(p,20.0478,.001)

    def test_7_B_14_rayleigh_con_balance(self):
        m=mod('operaciones_liquido_vapor');r=m.rayleigh_from_final_x(100.,.6,.45,1.43)
        self.check(r.N,17.7627,.00008);self.check(r.D,82.2373,.00008)
        self.check(r.xD_average,.632399,2e-6);self.check(r.recovery_light,.866780,2e-6)
        self.check(r.light_residual+r.light_distillate,60.,1e-10)
        self.check(r.heavy_residual+r.heavy_distillate,40.,1e-10)

    def test_7_B_15_cuatro_etapas(self):
        m=mod('operaciones_liquido_vapor');st=m.successive_equilibrium_stages(.10,2.414,4)
        for s,reference in zip(st,[.21149,.39302,.60984,.79050]):
            self.check(s.y_eq,reference,1e-5)
            self.check(s.x_next,s.y_eq,1e-12)
        self.check(st[-1].y_eq/.1,7.905,.0001)

    def test_7_B_16_líquidos_inmiscibles(self):
        m=mod('inmiscibles_y_arrastre_vapor')
        p=56.31+44.99;y=44.99/p
        r=m.condensacion(1.,y,18.015,92.14)
        self.check(p,101.30,1e-10);self.check(y,.444126,1e-6)
        self.check(r['m_b']/r['m_a'],4.08643,.0001)
        self.check(r['residual_m'],0,1e-12)

    def test_8_B_12_azeotropo_margules1(self):
        m=mod('disoluciones_no_ideales')
        x=m.azeotrope_margules1_analytic(1.2,80,50)
        p,y,_,_=m.bubble_pressure([x,1-x],300,m.Margules1(1.2),m.DirectPsat([80.,50.]))
        self.check(x,.695835,2e-6);self.check(p,89.3934,1e-4)
        self.check(y[0],x,1e-10)

    def test_8_B_13_azeotropo_margules2(self):
        m=mod('disoluciones_no_ideales')
        roots=m.azeotrope_roots(300,m.Margules2(.8,1.3),m.DirectPsat([72.,46.]),1e-11)
        self.assertEqual(len(roots),1)
        x,p,g,it,res=roots[0]
        self.check(x,.733818,2e-6);self.check(p,80.2656,1e-4);self.check(res,0,1e-8)
        self.check(g[0]*72.,g[1]*46.,1e-8)

    def test_8_B_14_dilucion_infinita_ambos_modelos(self):
        m=mod('disoluciones_no_ideales');a,b=m.infinite_dilution_parameters(4.20,2.10)
        g=m.Margules2(a,b).gammas([.5,.5]);v=m.VanLaar(a,b).gammas([.5,.5])
        self.check(a,1.435085,2e-6);self.check(b,.741937,2e-6)
        for val,ref in zip(g,[1.20380,1.43157]):self.check(val,ref,1e-5)
        for val,ref in zip(v,[1.18138,1.38044]):self.check(val,ref,1e-5)

    def test_8_B_15_errores_modelos(self):
        m=mod('disoluciones_no_ideales')
        a=m.mae_rmse([0]*5,[-.18,-.07,-.01,.02,.02]);b=m.mae_rmse([0]*5,[-.02,-.02,.04,.05,.04])
        for val,ref in zip(a,[.0600,.0874]):self.check(val,ref,1e-4)
        for val,ref in zip(b,[.0340,.0361]):self.check(val,ref,1e-4)
        self.assertLess(b[0],a[0]);self.assertLess(b[1],a[1])

    def test_9_B_9_arrastre_condensado(self):
        m=mod('inmiscibles_y_arrastre_vapor');r=m.vapor_desde_relacion_masica(.310,18.0153,93.1265)
        self.check(r['p_b_a'],.0599694,3e-6)
        self.check(r['y_b'],.0565766,3e-6)
        self.check(r['y_a']+r['y_b'],1,1e-12)

    def test_9_B_10_palanca_interpolada(self):
        m=mod('equilibrio_liquido_liquido')
        a=m.regla_palanca(2.,.30,.820,.180)
        self.check(a.l1,.375,1e-10);self.check(a.l2,1.625,1e-10)
        x1,x2=m.interpolar_binodal([(20,.820,.180),(30,.660,.340)],25)
        b=m.regla_palanca(2.,.30,x1,x2)
        self.check(b.l1,.1666667,1e-6);self.check(b.l2,1.833333,1e-6)
        self.check(b.a_l1,.123333,1e-6);self.check(b.a_l2,.476667,1e-6)
        self.check(b.residuo_total,0,1e-12);self.check(b.residuo_a,0,1e-12)

    def test_10_B_10_etilenglicol(self):
        m=mod('propiedades_coligativas')
        n=124.14/62.07;molal=n/1.0
        self.check(m.coligativa(1.86,molal),3.72,1e-10)
        self.check(m.coligativa(.512,molal),1.024,1e-10)
        self.check(100+m.coligativa(.512,molal),101.024,1e-10)

    def test_11_B_11_mezcla_N2_O2(self):
        m=mod('balances_materia')
        r=m.caudales_componentes(50,[.8,.2])
        self.check(r[0],40,1e-12);self.check(r[1],10,1e-12)
        self.check(m.comprobar_residuos([50],r,50)['residuo'],0,1e-12)

    def test_11_B_12_caudal_masico(self):
        m=mod('balances_materia');r=m.base_molar_a_masa([2.50],[28.014])
        self.check(r['caudal_masico_total'],70.035,1e-9)
        self.check(r['caudal_molar_total'],2.5,1e-12)

    def test_12_B_9_cristalizacion_con_cierre(self):
        m=mod('cristalizacion')
        agua=m.dividir(m.multiplicar(m.exacto(1000),m.exacto(.65)),m.exacto(.35))
        licor=m.dividir(agua,m.exacto(.746))
        cristal=m.restar(m.sumar(m.exacto(1000),agua),licor)
        self.check(float(agua.valor),1857.142857,.002)
        self.check(float(licor.valor),2489.4676,.002)
        self.check(float(cristal.valor),367.6752,.002)
        self.check(float(cristal.valor)+.254*float(licor.valor),1000,1e-9)

    def test_12_B_11_extraccion_con_cierre(self):
        m=mod('extraccion_liquido_liquido')
        agua=m.exacto(57.14);refinado=m.dividir(agua,m.exacto(.8375))
        extracto=m.restar(m.exacto(200),refinado)
        acido_rest=m.multiplicar(m.exacto(.1625),refinado)
        acido_extraido=m.restar(m.exacto(42.86),acido_rest)
        self.check(float(refinado.valor),68.2269,.001)
        self.check(float(extracto.valor),131.7731,.001)
        self.check(float(acido_extraido.valor),31.7731,.001)
        self.check(float(acido_extraido.valor)/42.86*100,74.1324,.002)
        self.check(float(refinado.valor)+float(extracto.valor),200,1e-12)

    def test_14_B_8_gases_humedos_y_secos(self):
        m=mod('combustion');o,prod=m.oxygen_stoich_formula('C2H6',10,m.ProductModel())
        self.check(o,35,1e-12)
        gases={**prod,'O2':o*.2,'N2':o*1.2*79/21}
        wet,dry,nh,ns=m.gas_compositions(gases,4)
        self.check(nh,215,1e-10);self.check(ns,185,1e-10)
        for sp,expected in [('CO2',.0930),('H2O',.140),('O2',.0326),('N2',.735)]:
            self.check(wet[sp],expected,.0008)
        for sp,expected in [('CO2',.108),('O2',.0378),('N2',.854)]:
            self.check(dry[sp],expected,.0008)
        self.check(sum(wet.values()),1,1e-12);self.check(sum(dry.values()),1,1e-12)

    def test_15_B_8_enfriamiento_sin_condensacion(self):
        m=mod('psicrometria');pv=.4*5.628;w=m.humidity_ratio_from_pw(pv,101.325)
        self.assertLess(pv,3.169)
        self.check(pv,2.2512,1e-10)
        self.check(pv/3.169*100,71.0,.04)
        self.check(m.pw_from_humidity_ratio(w,101.325),pv,1e-9)

    def test_15_B_9_enfriamiento_condensacion(self):
        m=mod('psicrometria');w1=m.humidity_ratio_from_pw(.8*4.245,101.325)
        w2=m.humidity_ratio_from_pw(1.228,101.325)
        self.check(w1,.02156,.00002);self.check(w2,.007629,.00002)
        self.check(w1-w2,.01394,.00002);self.assertGreater(w1,w2)

    def test_guardia_8_mae_rechaza_nan(self):
        m=mod('disoluciones_no_ideales')
        with self.assertRaises(ValueError):m.mae_rmse([1.,float('nan')],[1.,1.])
        with self.assertRaises(ValueError):m.mae_rmse([1.,2.],[1.,float('inf')])

    def test_guardia_8_mae_rechaza_longitudes_distintas(self):
        m=mod('disoluciones_no_ideales')
        with self.assertRaises(ValueError):m.mae_rmse([1.],[1.,2.])
        with self.assertRaises(ValueError):m.mae_rmse([],[])
        with self.assertRaises(ValueError):m.mae_rmse([[1.,2.]],[1.,2.])

    def test_guardia_8_azeotropo_analitico_nan(self):
        m=mod('disoluciones_no_ideales')
        for a,p1,p2 in [(float('nan'),80,50),(1.2,float('inf'),50),(1.2,80,float('nan'))]:
            with self.assertRaises(ValueError):m.azeotrope_margules1_analytic(a,p1,p2)

    def test_guardia_8_azeotropo_umbral_nan(self):
        m=mod('disoluciones_no_ideales')
        for p1,p2 in [(float('nan'),50),(80,float('inf'))]:
            with self.assertRaises(ValueError):m.azeotrope_margules1_threshold(p1,p2)

if __name__=='__main__':unittest.main()
