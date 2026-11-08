# -*- coding: utf-8 -*-
"""Cotejo VI: libro definitivo (934 pp.) y solucionario (220 pp.).

Las llamadas de módulos ejercitan cálculos reales. Los balances externos se
identifican explícitamente: un ensayo matemático no implica que exista un menú
que resuelva automáticamente el problema completo.
"""
import math
import unittest
from test_auditoria_integral import mod


class CotejoBloqueSeis(unittest.TestCase):
    def test_2_C_5_titulacion_incertidumbre(self):
        """2.C.5, libro p.99: 0,09920 ± 0,00026 mol/L, NaOH domina varianza."""
        m=mod('unidades_y_dimensiones')
        a,vn,vh=.1,24.8,25.0
        c=a*vn/vh
        u,diag,cov=m.propagar_incertidumbre_estandar(
            [vn/vh,a/vh,-a*vn/(vh*vh)],[.0002,.03,.03])
        self.assertAlmostEqual(c,.0992,delta=1e-12)
        self.assertAlmostEqual(u,.00026064,delta=2e-8)
        self.assertAlmostEqual(diag[0]/sum(diag),.5794,delta=.005)
        self.assertAlmostEqual(cov,0,delta=1e-20)

    def test_3_C_2_butano_co2(self):
        """3.C.2, libro p.161: 6,0 kg butano, CO2≈18,17 kg y 9,26 m³ CN."""
        eq=mod('ajuste_ecuaciones');mm=mod('masa_molar');gas=mod('gases_ideales_y_mezclas')
        self.assertEqual(eq.ajustar(['C4H10','O2'],['CO2','H2O']),[2,13,8,10])
        mol_co2=4*6000/float(mm.calculate_molar_mass('C4H10').raw_mass)
        mass=mol_co2*float(mm.calculate_molar_mass('CO2').raw_mass)/1000
        vol=gas.solve_ideal(101325,None,mol_co2,273.15)['V']
        self.assertAlmostEqual(mass,18.17,delta=.05)
        self.assertAlmostEqual(vol,9.26,delta=.04)

    def test_3_C_3_aluminio_hidrogeno(self):
        """3.C.3, libro p.161: H2≈6,73 L; HCl≈21,9 g."""
        eq=mod('ajuste_ecuaciones');mm=mod('masa_molar');gas=mod('gases_ideales_y_mezclas')
        self.assertEqual(eq.ajustar(['Al','HCl'],['AlCl3','H2']),[2,6,2,3])
        na=5.40/float(mm.calculate_molar_mass('Al').raw_mass)
        v=gas.solve_ideal(101325,None,na*1.5,273.15)['V']*1000
        mh=3*na*float(mm.calculate_molar_mass('HCl').raw_mass)
        self.assertAlmostEqual(v,6.73,delta=.02)
        self.assertAlmostEqual(mh,21.9,delta=.06)

    def test_3_C_5_mezcla_salina(self):
        """3.C.5, libro p.162: 75 g NaCl, 425 g H2O, 425 mL."""
        b=mod('balances_materia');u=mod('unidades_y_dimensiones')
        m_s=500*.15; m_w=500-m_s
        self.assertEqual(m_s,75);self.assertEqual(m_w,425)
        self.assertAlmostEqual(b.comprobar_residuos([m_s,m_w],[500],500)['residuo'],0)
        self.assertEqual(u.convertir_unidad(m_w,'mL','L'),.425)

    def test_4_C_1_gases_combustion_masa_y_densidad(self):
        """4.C.1, libro p.191: Mmix≈30,35, ρ≈1,71, GE≈1,05."""
        m=mod('gases_ideales_y_mezclas')
        mm={'CO2':44.01,'CO':28.01,'O2':32.,'N2':28.014}
        rows=m.mixture_from_basis(m.parse_components('CO2:14;CO:2;O2:2.5;N2:81.5'),'molar',mm)
        s=m.mixture_summary(rows,P=1.5e5,T=320)
        self.assertAlmostEqual(s['Mmix'],30.35,delta=.02)
        self.assertAlmostEqual(s['rho_kg_m3'],1.71,delta=.01)
        self.assertAlmostEqual(s['GE'],1.05,delta=.005)
        self.assertAlmostEqual(rows[0]['w']*100,20.3,delta=.1)
        self.assertAlmostEqual(sum(r['w'] for r in rows),1,delta=1e-12)

    def test_4_C_7_secador_nitrogeno_inerte(self):
        """4.C.7, libro p.192: V2≈121,6 m³, 24,70 kg H2O evaporada."""
        gas=mod('gases_ideales_y_mezclas');b=mod('balances_materia')
        n1=gas.solve_ideal(95000,100,None,500)['n']
        n2=n1*.8/.5
        v2=gas.solve_ideal(90000,None,n2,360)['V']
        h2o=n2*.375*18.015/1000
        self.assertAlmostEqual(v2,121.6,delta=.1)
        self.assertAlmostEqual(h2o,24.70,delta=.03)
        self.assertAlmostEqual(b.comprobar_residuos([n1*.8],[n2*.5],n1*.8)['residuo'],0,delta=1e-8)

    def test_4_C_8_absorcion_amoniaco(self):
        """4.C.8, libro p.192: NH3 final 1/91, 0,649 % masa, Mfinal 28,84."""
        m=mod('gases_ideales_y_mezclas')
        rows=m.mixture_from_basis(m.parse_components('NH3:1;aire:90'),'molar',{'NH3':17.031,'aire':28.97})
        s=m.mixture_summary(rows)
        self.assertAlmostEqual(rows[0]['y'],1/91,delta=1e-12)
        self.assertAlmostEqual(rows[0]['w']*100,.649,delta=.002)
        self.assertAlmostEqual(s['Mmix'],28.84,delta=.02)

    def test_4_C_9_enriquecimiento_oxigeno(self):
        """4.C.9, libro p.192: añadir 2,78 m3/min O2 o 22,7 m3/min aire."""
        b=mod('balances_materia')
        for yo,expected in [(1.,2.77777777778),(.21,22.7272727273)]:
            s=b.resolver_lineal(['q'],[b.Ecuacion([yo-.1],50*(.1-.05),'O2')])
            self.assertEqual(s.estado,'unico')
            q=s.valores['q']
            self.assertAlmostEqual(q,expected,delta=1e-8)
            self.assertAlmostEqual((2.5+yo*q)/(50+q),.10,delta=1e-12)

    def test_5_C_3_metanopr_90bar(self):
        """5.C.3, libro p.250: PR metano Z≈0,879 y Vm≈0,260 L/mol."""
        m=mod('gases_reales');g=m.resolve_gas('CH4')
        s=m.model_state('pr',320,90,g)
        self.assertAlmostEqual(s['Z'],.879,delta=.001)
        self.assertAlmostEqual(s['Vm'],.260,delta=.001)
        self.assertAlmostEqual(s['Tr'],1.679,delta=.002)
        self.assertAlmostEqual(s['Pr'],1.957,delta=.002)

    def test_5_C_4_agua_leekesler(self):
        """5.C.4, libro p.251: LK Z≈0,92731 y Vm≈2,27219 L/mol."""
        m=mod('gases_reales');g=m.resolve_gas('H2O')
        a=m.lee_kesler(501,17,g)
        self.assertAlmostEqual(a['Z'],.92731,delta=.0002)
        self.assertAlmostEqual(a['Vm'],2.27219,delta=.001)
        self.assertAlmostEqual(m.ideal_state(501,17,g)['Vm'],2.45032,delta=.0003)

    def test_6_B_14_heptano_lee_kesler_antoine(self):
        """6.B.14, libro p.293: LK 50,8925 kPa, Antoine 51,3699 kPa."""
        m=mod('presion_vapor')
        tr,f0,f1,pr,plk=m.lee_kesler_pressure_kpa(350,540.2,2740,.349)
        pa=m.antoine_pressure_kpa(350,m.ANTOINE['n-heptano'])
        self.assertAlmostEqual(tr,.647908,delta=1e-6)
        self.assertAlmostEqual(plk,50.8925,delta=.0001)
        self.assertAlmostEqual(pa,51.3699,delta=.0001)
        self.assertAlmostEqual(100*(plk/pa-1),-.929,delta=.002)

    def test_6_C_4_cox_etanol(self):
        """6.C.4, libro p.295: interpolación Cox 29,1595 kPa a 323K."""
        m=mod('presion_vapor');a=m.ANTOINE['agua']
        w=[m.antoine_pressure_kpa(t,a) for t in (293,323,363)]
        la=math.log(w[1]/w[0])/math.log(w[2]/w[0])
        pe=5.76*(157.03/5.76)**la
        self.assertAlmostEqual(la,.49065,delta=.00001)
        self.assertAlmostEqual(pe,29.1595,delta=.003)
        self.assertAlmostEqual(100*(pe-29.5)/29.5,-1.15,delta=.03)

    def test_7_C_4_raoult_curvas_binarias(self):
        """7.C.4, libro p.365: Pbur=108,88; Proc=64,1075 kPa."""
        m=mod('equilibrio_liquido_vapor')
        b=m.raoult_from_pstar([.5,.5],[178.7,39.06])
        pr,x=m.dew_from_pstar([.5,.5],[178.7,39.06])
        self.assertAlmostEqual(b['P'],108.88,delta=1e-9)
        self.assertAlmostEqual(b['y'][0],.820628,delta=1e-6)
        self.assertAlmostEqual(pr,64.1075,delta=.0001)
        self.assertAlmostEqual(x[0],.179372,delta=.000001)

    def test_7_C_7_c_dos_fases_inmiscibles(self):
        """7.C.7, libro p.365: A/B ideal, C inmiscible; p=(2,5,2,5,95)."""
        m=mod('equilibrio_liquido_vapor')
        x=(100-95-3)/(15-3)
        b=m.raoult_from_pstar([x,1-x],[15,3])
        self.assertAlmostEqual(x,1/6,delta=1e-14)
        self.assertAlmostEqual(b['P'],5,delta=1e-12)
        self.assertAlmostEqual(b['partial'][0],2.5,delta=1e-12)
        self.assertAlmostEqual(b['partial'][1],2.5,delta=1e-12)
        self.assertAlmostEqual(sum(b['partial'])+95,100)
        self.assertEqual([round(p/100,3) for p in [*b['partial'],95]],[.025,.025,.950])

    def test_8_B_6_wilson(self):
        """8.B.6, libro p.457: Wilson gamma1≈1,02891, gE/RT≈0,032417."""
        m=mod('disoluciones_no_ideales')
        gam,act,ge=m.activity_properties([.4,.6],m.Wilson(.420,1.650))
        self.assertAlmostEqual(gam[0],1.02891,delta=.00001)
        self.assertAlmostEqual(gam[1],1.03565,delta=.00001)
        self.assertAlmostEqual(act[0],.41156,delta=.00001)
        self.assertAlmostEqual(ge,.032417,delta=.00001)

    def test_8_C_2_regresion_margules2(self):
        """8.C.2, libro p.461: A12=1,0000017, A21=0,6002903."""
        m=mod('disoluciones_no_ideales')
        x=[.1,.25,.4,.55,.7,.85]
        y=[.3661,.548,.6417,.7191,.8008,.8945]
        p=[57.547,71.544,79.622,85.670,90.938,95.708]
        gam1,gam2=m.experimental_gammas(x,y,p,100.,40.)
        a12,a21=m.fit_margules2(x,gam1,gam2)
        pp,yy=m.model_predictions(x,m.Margules2(a12,a21),100.,40.)
        errp,rmsep=m.mae_rmse(p,pp)
        self.assertAlmostEqual(a12,1.0000017,delta=.000001)
        self.assertAlmostEqual(a21,.6002903,delta=.000001)
        self.assertAlmostEqual(errp,.00312,delta=.00005)
        self.assertAlmostEqual(rmsep,.00330,delta=.00005)
        self.assertAlmostEqual(yy[0],.36612,delta=.00005)

    def test_8_C_2_regresion_van_laar_comparada(self):
        """8.C.2, libro p.461: Van Laar A12≈1,04157, A21≈0,64909.
        El error de presión resulta mayor que el de Margules para estos datos.
        """
        m=mod('disoluciones_no_ideales')
        x=[.1,.25,.4,.55,.7,.85]
        y=[.3661,.548,.6417,.7191,.8008,.8945]
        p=[57.547,71.544,79.622,85.670,90.938,95.708]
        g1,g2=m.experimental_gammas(x,y,p,100.,40.)
        a12,a21,loss,niter=m.fit_van_laar(x,g1,g2)
        predicted,ypred=m.model_predictions(x,m.VanLaar(a12,a21),100.,40.)
        mae,rmse=m.mae_rmse(p,predicted)
        self.assertAlmostEqual(a12,1.0415701,delta=.00001)
        self.assertAlmostEqual(a21,.6490926,delta=.00001)
        self.assertAlmostEqual(mae,.21624,delta=.0001)
        self.assertAlmostEqual(rmse,.23747,delta=.0001)
        self.assertGreater(mae,.00312)

    def test_8_C_4_etanol_agua_etapas(self):
        """8.C.4, libro p.462: 12 condensaciones; x12≈0,880747."""
        m=mod('disoluciones_no_ideales')
        x=[0,.019,.097,.166,.261,.397,.520,.676,.747,.894]
        y=[0,.170,.438,.509,.558,.612,.660,.739,.782,.894]
        xs=m.stage_progression(x,y,.25,.880)
        self.assertEqual(len(xs)-1,12)
        self.assertAlmostEqual(xs[1],.55233,delta=.00002)
        self.assertAlmostEqual(xs[-1],.88075,delta=.00002)

    def test_9_C_2_trifasico_consumos_inventario(self):
        """9.C.2, libro p.518: T=351,188K; vapor 26,47 mol, agua residual 15,53."""
        m=mod('inmiscibles_y_arrastre_vapor')
        t=m.temperatura_trifasica(m.AGUA_2,m.TOLUENO,.800).t
        v=m.composicion_vapor(m.AGUA_2,m.TOLUENO,t,.8)
        f=m.consumir_fases(30,12,v['y_b'])
        self.assertAlmostEqual(t,351.18770,delta=.00001)
        self.assertAlmostEqual(v['y_a'],.546655,delta=2e-6)
        self.assertAlmostEqual(v['m_b_a'],4.24145,delta=.00002)
        self.assertIn('B',f['agotada'])
        self.assertAlmostEqual(f['n_v'],26.4699,delta=.0002)
        self.assertAlmostEqual(f['n_a_residual'],15.5301,delta=.0002)
        self.assertAlmostEqual(f['residual_a'],0,delta=1e-12)

    def test_9_C_4_condensador_decantador(self):
        """9.C.4, libro p.519: 100 kmol/h: condensado 5093,337 kg/h."""
        m=mod('inmiscibles_y_arrastre_vapor')
        r=m.condensacion(100,.4441,18.0153,92.1384)
        self.assertAlmostEqual(r['m_a'],1001.471,delta=.002)
        self.assertAlmostEqual(r['m_b'],4091.866,delta=.002)
        self.assertAlmostEqual(r['m_total'],5093.337,delta=.002)
        self.assertAlmostEqual(r['w_b'],.803376,delta=.000002)
        self.assertAlmostEqual(r['residual_m'],0,delta=1e-9)

    def test_10_C_4_osmosis_agua_mar(self):
        """10.C.4, libro p.590: cosm=1,142528 mol/L, Pi ideal=28,323 bar."""
        m=mod('propiedades_coligativas')
        p=m.presion_osmotica(1.142528,298.15)
        self.assertAlmostEqual(p,28.323,delta=.002)
        self.assertAlmostEqual(63.4-p,35.1,delta=.05)

    def test_10_C_5_sales_rehidratacion(self):
        """10.C.5, libro p.590: 243,6 mOsm/L, I_c≈0,124 mol/L.
        La función fuerza_ionica pondera z²: se aplica aquí a molaridades
        solo como operación algebraica, sin atribuirles unidades de molalidad.
        """
        e=mod('disoluciones_electroliticas')
        g,na,k,cit=13.5/180.16,2.6/58.44,1.5/74.55,2.9/294.1
        naion=na+3*cit;clion=na+k
        osm=g+naion+k+clion+cit
        ci=e.fuerza_ionica([e.Ion('Na+',1,naion),e.Ion('K+',1,k),
                            e.Ion('Cl-',-1,clion),e.Ion('Cit3-',-3,cit)])
        self.assertAlmostEqual(osm*1000,243.6,delta=.1)
        self.assertAlmostEqual(ci,.12377,delta=.0001)
        self.assertAlmostEqual(naion+k-clion-3*cit,0,delta=1e-12)

    def test_11_C_4_recambio_medio_celular(self):
        """11.C.4, libro p.662: retirar/añadir 180 mL; +0,540 g glucosa."""
        m=mod('balances_materia');vol=12*.015
        removed=vol*1.5;added=vol*4.5
        self.assertAlmostEqual(vol,.180,delta=1e-12)
        self.assertAlmostEqual(added-removed,.540,delta=1e-12)
        self.assertAlmostEqual(m.comprobar_residuos([added],[removed,added-removed],added)['residuo'],0,delta=1e-12)

    def test_11_C_5_dilucion_y_envasado(self):
        """11.C.5, libro p.662: 500mL concentrado, 48 botes, 30mL."""
        m=mod('balances_materia')
        vol_conc=5*9/90;vol_water=5-vol_conc
        available=5-.050-.120
        n=int(available/.100+1e-10);rest=available-n*.100
        self.assertAlmostEqual(vol_conc,.500,delta=1e-12)
        self.assertAlmostEqual(vol_water,4.50,delta=1e-12)
        self.assertEqual(n,48)
        self.assertAlmostEqual(rest,.030,delta=1e-12)
        self.assertAlmostEqual(m.comprobar_residuos([vol_conc,vol_water],[.050,.120,n*.100,rest],5)['residuo'],0,delta=1e-10)

    def test_8_ajuste_rechaza_gamma_no_finitos(self):
        """Control nuevo de datos no físicos (no es un ejercicio adicional)."""
        m=mod('disoluciones_no_ideales')
        for vals in [([.2,float('nan')],[.4,.5],[20,30]),
                     ([.2,.4],[.4,float('inf')],[20,30]),
                     ([.2,.4],[.4,.5],[20,float('nan')]),
                     ([.2,.4],[.4,.5],[20,-1]),
                     ([.2,.4],[.4,.5],[20,30,40])]:
            with self.subTest(vals=vals):
                with self.assertRaises(ValueError):m.experimental_gammas(*vals,100.,40.)

    def test_8_ajuste_rechaza_presiones_vapor_invalidas(self):
        m=mod('disoluciones_no_ideales')
        for ps in [(float('nan'),40),(100,float('inf')),(100,0),(-1,40)]:
            with self.subTest(ps=ps):
                with self.assertRaises(ValueError):
                    m.experimental_gammas([.2,.4],[.3,.5],[30,40],*ps)

    def test_8_margules_rechaza_series_incompletas(self):
        m=mod('disoluciones_no_ideales')
        for args in [([.2,.4],[1.5],[1.1,1.3]),
                     ([.2,.4],[1.5,1.2],[1.1]),
                     ([.2,.4],[1.5,float('nan')],[1.1,1.3]),
                     ([.2],[1.5],[1.1])]:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):m.fit_margules2(*args)

    def test_8_vanlaar_rechaza_series_invalidas(self):
        m=mod('disoluciones_no_ideales')
        for args in [([.2,.4],[1.5],[1.1,1.3]),
                     ([.2,.4],[1.5,1.2],[1.1,float('inf')])]:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):m.fit_van_laar(*args)


if __name__=='__main__':unittest.main()
