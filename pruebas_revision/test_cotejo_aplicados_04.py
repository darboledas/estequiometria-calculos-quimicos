# -*- coding: utf-8 -*-
"""Bloque 04: nuevos ejercicios aplicados C cotejados con el libro y solucionario.

Los valores de referencia proceden de enunciados/soluciones de las ediciones
finales; se usan tolerancias explícitas por precisión de entrada y redondeos.
En operaciones encadenadas se distingue el cálculo del módulo y el balance
algebraico de interfaz, sin atribuir al módulo capacidades no implementadas.
"""
import math
import unittest
from types import SimpleNamespace
from test_auditoria_integral import mod


class CotejoAplicadosCuatro(unittest.TestCase):
    def test_2_C_1_caudal_galon_us(self):
        """2.C.1: 18,5 gal US/min -> 4,20 m³/h (3 cifras)."""
        m=mod('unidades_y_dimensiones')
        v=m.convertir_unidad(18.5,'gal/min','m3/h')
        self.assertAlmostEqual(v,4.20180708024,delta=1e-10)
        self.assertAlmostEqual(v,4.20,delta=.005)
        self.assertEqual(m.cifras_significativas_texto('18,5'),3)

    def test_2_C_3_presion_moles_y_redondeo_prematuro(self):
        """2.C.3: 18,6 psi; 2,50 L; 298,15 K -> 0,12933 mol."""
        u=mod('unidades_y_dimensiones');g=mod('gases_ideales_y_mezclas')
        P=18.6*101325/14.696 # convención redondeada del libro
        P_exact=u.convertir_unidad(18.6,'psi','Pa')
        self.assertAlmostEqual(P_exact,P,delta=2.0)
        n=g.solve_ideal(P,2.50e-3,None,298.15)['n']
        self.assertAlmostEqual(n,.1293306,delta=5e-7)
        n_early=g.solve_ideal(130000,2.50e-3,None,298.15)['n']
        self.assertAlmostEqual(n_early,.1311035,delta=5e-6)
        self.assertGreater(n_early,n)

    def test_2_C_4_R_conversion_y_P(self):
        """2.C.4: R=0,083144626 bar L mol-1 K-1; 5,16 bar."""
        u=mod('unidades_y_dimensiones')
        R=8.314462618
        rbar=R*.01
        ratm=R*1e3/101325
        self.assertAlmostEqual(rbar,.08314462618,delta=1e-11)
        self.assertAlmostEqual(ratm,.08205736608,delta=1e-10)
        p=2.5*rbar*298.15/12
        self.assertAlmostEqual(p,5.16449,delta=5e-5)
        self.assertAlmostEqual(u.convertir_unidad(p,'bar','atm'),5.09696,delta=5e-5)

    def test_3_C_1_antiacido_carbonato(self):
        """3.C.1: 1,875 g CaCO3; 1,37 g HCl; 0,464 L CO2."""
        mm=mod('masa_molar');r=mod('reactivo_limitante');g=mod('gases_ideales_y_mezclas')
        m_ca=2.5*.75
        M_ca=float(mm.calculate_molar_mass('CaCO3').raw_mass)
        M_hcl=float(mm.calculate_molar_mass('HCl').raw_mass)
        n=m_ca/M_ca
        cap,lim,xi,adv,left,prod=r.balance([r.Q(n),r.Q(2*n*1.1)],[1,2],[1])
        self.assertAlmostEqual(float(prod[0].v),n,delta=1e-11)
        self.assertAlmostEqual(2*n*M_hcl,1.366,delta=.004)
        V=g.solve_ideal(100000,None,n,298.15)['V']*1000
        self.assertAlmostEqual(V,.4644,delta=.001)

    def test_3_C_4_secado_base_humeda(self):
        """3.C.4: se conservan 140 kg de sólido, final 152,17 kg."""
        bal=mod('balances_materia')
        dry=200*(1-.30);final=dry/(1-.08);evap=200-final
        self.assertAlmostEqual(final,152.173913,delta=1e-5)
        self.assertAlmostEqual(evap,47.826087,delta=1e-5)
        self.assertAlmostEqual(bal.comprobar_residuos([200],[final,evap],200)['residuo'],0,delta=1e-10)

    def test_3_C_6_limitante_hierro_azufre(self):
        """3.C.6: Fe limitante; 31,5 g FeS y 3,52 g S remanente."""
        m=mod('reactivo_limitante')
        nfe=20/55.845; ns=15/32.06
        _,indices,_,avance,rest,formed=m.balance([m.Q(nfe),m.Q(ns)],[1,1],[1])
        self.assertEqual(indices,[0])
        self.assertAlmostEqual(float(formed[0].v)*(55.845+32.06),31.481,delta=.01)
        self.assertAlmostEqual(float(rest[1].v)*32.06,3.518,delta=.02)

    def test_3_C_7_limitante_h2_gas(self):
        """3.C.7: H2 40% en 112 L; volumen amoniaco 29,9 L."""
        m=mod('reactivo_limitante')
        _,lim,_,avance,rest,formed=m.balance([m.Q(67.2),m.Q(44.8)],[1,3],[2])
        self.assertEqual(lim,[1])
        self.assertAlmostEqual(float(formed[0].v),29.8666666667,delta=1e-8)

    def test_4_C_2_composicion_gas_natural(self):
        """4.C.2: mezcla CH4/N2/CO2; M=16,6469 y w(CH4)=92,5%."""
        m=mod('gases_ideales_y_mezclas')
        xs=[('CH4',m.parse_num('96.0')),('N2',m.parse_num('3.2')),('CO2',m.parse_num('0.8'))]
        rows=m.mixture_from_basis(xs,'molar',{'CH4':16.04,'N2':28.014,'CO2':44.01})
        sm=m.mixture_summary(rows)
        self.assertAlmostEqual(sm['Mmix'],16.6469,delta=.0001)
        self.assertAlmostEqual(rows[0]['w']*100,92.5,delta=.05)
        self.assertAlmostEqual(sum(r['w'] for r in rows),1,delta=1e-13)

    def test_4_C_3_oxigeno_so2_presion_y_volumen(self):
        """4.C.3: pO2=120,1 kPa; V=1,3827 m3; rho=1,999."""
        m=mod('gases_ideales_y_mezclas')
        y=(64.06-44.8)/(64.06-32.0)
        p=200*y
        V=m.solve_ideal(200000,None,5000/44.8,298)['V']
        self.assertAlmostEqual(p,120.1,delta=.1)
        self.assertAlmostEqual(V,1.3827,delta=.001)
        self.assertAlmostEqual(44.8/22.414,1.999,delta=.003)

    def test_4_C_4_presiones_dalton_nh3(self):
        """4.C.4: N2/H2 1:3, p=(2,50;7,50) bar, M=8,5155."""
        m=mod('gases_ideales_y_mezclas')
        r=m.mixture_from_basis([('N2',m.parse_num('1')),('H2',m.parse_num('3'))],'molar',{'N2':28.014,'H2':2.016})
        out=m.mixture_summary(r,P=1e6,T=500.1)
        self.assertAlmostEqual(r[0]['p'],250000,delta=1e-5)
        self.assertAlmostEqual(r[1]['p'],750000,delta=1e-5)
        self.assertAlmostEqual(out['Mmix'],8.5155,delta=1e-7)
        self.assertAlmostEqual(out['rho_kg_m3'],2.0479,delta=.0003)

    def test_4_C_5_absorcion_hcl_gas(self):
        """4.C.5: 70,7 m3 salida y 37,1 kg HCl absorbido."""
        m=mod('balances_materia');g=mod('gases_ideales_y_mezclas')
        out=m.convierte_volumen_gas(100,95000,320.2,90000,300)*(.7+.3*.05)
        nin=g.solve_ideal(95000,100,None,320.2)['n']
        self.assertAlmostEqual(out,70.71,delta=.04)
        self.assertAlmostEqual(.3*.95*nin*36.46/1000,37.08,delta=.07)
        self.assertAlmostEqual(.015/.715+.7/.715,1,delta=1e-12)

    def test_4_C_6_condensacion_punto_de_rocio(self):
        """4.C.6: condensación selectiva; volumen 91,92 m3 y agua 1,16 kg."""
        m=mod('balances_materia');g=mod('gases_ideales_y_mezclas')
        ratio=.97/.9861
        v=m.convierte_volumen_gas(100,100000,305,100000,285)*ratio
        nin=g.solve_ideal(100000,100,None,305)['n']
        ncond=nin*(.03-ratio*.0139)
        self.assertAlmostEqual(v,91.92,delta=.03)
        self.assertAlmostEqual(ncond*18.015/1000,1.16,delta=.02)

    def test_5_C_1_rk_pr_amoniaco(self):
        """5.C.1: Vm ideal 3,10; RK 2,97981; PR 2,96405 L/mol."""
        m=mod('gases_reales');gas=m.resolve_gas('NH3')
        ideal=m.ideal_state(373,10,gas);rk=m.cubic_state('rk',373,10,gas);pr=m.cubic_state('pr',373,10,gas)
        self.assertAlmostEqual(ideal['Vm'],3.10129,delta=.0001)
        self.assertAlmostEqual(rk['Vm'],2.97981,delta=.0001)
        self.assertAlmostEqual(pr['Vm'],2.96405,delta=.0001)
        self.assertTrue(pr['Vm']<rk['Vm']<ideal['Vm'])

    def test_5_C_2_lee_kesler_butano(self):
        """5.C.2: Lee-Kesler n-butano Z=0,9753154 (511K,5,1bar)."""
        m=mod('gases_reales');g=m.resolve_gas('NC4H10')
        out=m.lee_kesler(511,5.1,g)
        self.assertAlmostEqual(out['Z'],.9753154,delta=.0002)
        self.assertAlmostEqual(100*(1/out['Z']-1),2.53,delta=.02)

    def test_5_C_7_CO2_supercritico_pr(self):
        """5.C.7: CO2 a 313K,100bar: ZPR=0,298924 y n=321,37mol."""
        m=mod('gases_reales');g=m.resolve_gas('CO2')
        st=m.cubic_state('pr',313,100,g)
        nid=100*25/(m.R_BAR*313)
        npr=25/st['Vm']
        self.assertAlmostEqual(st['Z'],.298924,delta=.0001)
        self.assertAlmostEqual(npr,321.37,delta=.15)
        self.assertAlmostEqual(nid,96.064,delta=.1)

    def test_6_C_1_condensacion_enfriamiento(self):
        """6.C.1: 100 m3 aire húmedo, 303K, 100kPa: 0,5575 kg agua."""
        g=mod('gases_ideales_y_mezclas');p=mod('psicrometria')
        n=g.solve_ideal(100000,100,None,303)['n']
        dry=n*.98
        vapor_i=n*.02
        vapor_f=dry*1.23/(100-1.23)
        self.assertAlmostEqual((vapor_i-vapor_f)*18.015/1000,.5575,delta=.001)
        self.assertGreater(p.humidity_ratio_from_pw(2.0,100),p.humidity_ratio_from_pw(1.23,100))

    def test_6_C_3_duhring_ajuste_y_estimacion(self):
        """6.C.3: Duhring 7,2/35kPa: 16,627kPa a 335K."""
        m=mod('presion_vapor');water=m.ANTOINE['agua']
        a,b,r2,refs=m.duhring_fit([(318,7.2),(352,35)],water)
        self.assertAlmostEqual(refs[0],312.804,delta=.001)
        self.assertAlmostEqual(refs[1],345.900,delta=.001)
        tr,p=m.duhring_pressure_at_temperature(335,a,b,water)
        self.assertAlmostEqual(tr,329.352,delta=.001)
        self.assertAlmostEqual(p,16.627,delta=.003)

    def test_6_C_9_titulo_de_vapor_por_entalpia(self):
        """6.C.9: x=(2400-417,5)/(2675,5-417,5)=0,877989."""
        m=mod('vapor_agua')
        row=SimpleNamespace(hf=417.5,hg=2675.5,vf=.001,vg=.1,sf=1,sg=5)
        x,hf,hg=m.quality_from_property(row,'h',2400)
        self.assertAlmostEqual(x,.877989,delta=3e-6)
        self.assertAlmostEqual(1-x,.122011,delta=3e-6)
        self.assertAlmostEqual(m.mixture_properties(row,x)['h'],2400,delta=1e-10)

    def test_7_C_2_rocio_binario_comprimido(self):
        """7.C.2: 131,2424 kPa, x=(0,462121;0,537879)."""
        m=mod('equilibrio_liquido_vapor')
        P,x=m.dew_from_pstar([.5,.5],[142,122])
        self.assertAlmostEqual(P,131.2424,delta=.001)
        self.assertAlmostEqual(x[0],.462121,delta=2e-6)
        self.assertAlmostEqual(sum(x),1,delta=1e-12)

    def test_7_C_6_rocio_ternario_composicion_masica(self):
        """7.C.6: 3 especies, P=25kPa, x=(.2,.4,.4), w=(.125,.375,.5)."""
        m=mod('equilibrio_liquido_vapor');g=mod('gases_ideales_y_mezclas')
        P,x=m.dew_from_pstar([.4,.4,.2],[50,25,12.5])
        rows=g.mixture_from_basis([('A',g.parse_num(str(x[0]))),('B',g.parse_num(str(x[1]))),('C',g.parse_num(str(x[2])))],'molar',{'A':40,'B':60,'C':80})
        self.assertAlmostEqual(P,25,delta=1e-12)
        for v,ref in zip(x,[.2,.4,.4]):self.assertAlmostEqual(v,ref,delta=1e-12)
        for row,ref in zip(rows,[.125,.375,.5]):self.assertAlmostEqual(row['w'],ref,delta=1e-12)

    def test_10_C_2_osmolaridad_farmaceutica(self):
        """10.C.2: NaCl 308mOsm/L, glucosa 252mOsm/L, pi=7,94/6,51bar."""
        m=mod('propiedades_coligativas')
        c1=9/58.44;c2=50/198.17
        self.assertAlmostEqual(2*c1*1000,308,delta=.05)
        self.assertAlmostEqual(c2*1000,252,delta=.5)
        self.assertAlmostEqual(m.presion_osmotica(c1,310.15,2),7.943,delta=.02)
        self.assertAlmostEqual(m.presion_osmotica(c2,310.15),6.506,delta=.02)

    def test_11_C_2_inventario_sin_contabilizar(self):
        """11.C.2: distribuye 9,2L, controles 0,1, fondo 0,55 -> falta 0,15L."""
        m=mod('balances_materia');outs=[8*1.15,.1,.55]
        val=m.comprobar_residuos([10],outs,10)
        self.assertAlmostEqual(10-sum(outs),.15,delta=1e-12)
        self.assertAlmostEqual((10-sum(outs))/10*100,1.5,delta=1e-12)
        self.assertAlmostEqual(m.comprobar_residuos([10],outs+[.15],10)['residuo'],0,delta=1e-12)

    def test_12_C_2_filtracion_secado_multietapa(self):
        """12.C.2: torta húmeda 64,145 kg; sólido 35,28; producto 36kg."""
        m=mod('balances_materia')
        solid=300*.12;capt=solid*.98;cake=capt/.55
        filtrate=300-cake;prod=capt/.98;water_evap=cake-prod
        self.assertAlmostEqual(cake,64.1454545,delta=.0001)
        self.assertAlmostEqual(filtrate,235.8545455,delta=.0001)
        self.assertAlmostEqual(prod,36,delta=1e-12)
        self.assertAlmostEqual(water_evap,28.14545,delta=.0001)
        self.assertAlmostEqual(m.comprobar_residuos([300],[filtrate,prod,water_evap],300)['residuo'],0,delta=1e-10)

    def test_13_C_2_dos_rutas_etanol(self):
        """13.C.2: conversion etanol 75%; selectividad 4:1; xi=12 y 3."""
        m=mod('balances_materia')
        sol=m.resolver_lineal(['xi1','xi2'],[m.Ecuacion([1,1],15,'conversion'),m.Ecuacion([1,-4],0,'selectividad')])
        self.assertEqual(sol.estado,'unico')
        self.assertAlmostEqual(sol.valores['xi1'],12,delta=1e-12)
        self.assertAlmostEqual(sol.valores['xi2'],3,delta=1e-12)
        products=[5,12,12,3,3]
        self.assertEqual(sum(products),35)
        self.assertAlmostEqual(sum(p/sum(products) for p in products),1,delta=1e-12)

    def test_14_C_2_glucosa_oxidacion_estequiometrica(self):
        """14.C.2: 3,6mmol glucosa => 21,6mmol O2, CO2, H2O."""
        m=mod('combustion')
        o2,prod=m.oxygen_stoich_formula('C6H12O6',.0036,m.ProductModel())
        self.assertAlmostEqual(o2,.0216,delta=1e-12)
        self.assertAlmostEqual(prod.get('CO2',0),.0216,delta=1e-12)
        self.assertAlmostEqual(prod.get('H2O',0),.0216,delta=1e-12)
        self.assertAlmostEqual(.025-o2,.0034,delta=1e-12)

    def test_15_C_2_condensacion_en_vitrina(self):
        """15.C.2: agua condensa, omega 0,011895 ->0,010646, delta .001250."""
        m=mod('psicrometria')
        pin=.6*3.169;w1=m.humidity_ratio_from_pw(pin,101.3)
        w2=m.humidity_ratio_from_pw(1.705,101.3)
        self.assertAlmostEqual(pin,1.9014,delta=1e-12)
        self.assertAlmostEqual(w1,.011895,delta=4e-6)
        self.assertAlmostEqual(w2,.010646,delta=4e-6)
        self.assertAlmostEqual(w1-w2,.001250,delta=4e-6)
        td=m.temperature_from_saturation_pressure(pin)
        self.assertAlmostEqual(td,16.7,delta=.3)

    def test_6_calidad_rechaza_valor_no_finito(self):
        """Regresión: nunca presentar x=NaN/Inf como título de vapor."""
        m=mod('vapor_agua')
        row=SimpleNamespace(hf=417.5,hg=2675.5,vf=.001,vg=.1,sf=1,sg=5)
        for value in (float('nan'),float('inf'),-float('inf')):
            with self.subTest(value=value),self.assertRaises(ValueError):
                m.quality_from_property(row,'h',value)

    def test_6_calidad_rechaza_datos_de_saturacion_corruptos(self):
        """Regresión: filas de saturación no finitas son datos no físicos."""
        m=mod('vapor_agua')
        for hf,hg in ((float('nan'),2675.5),(417.5,float('inf'))):
            row=SimpleNamespace(hf=hf,hg=hg,vf=.001,vg=.1,sf=1,sg=5)
            with self.subTest(hf=hf,hg=hg),self.assertRaises(ValueError):
                m.quality_from_property(row,'h',2400)
