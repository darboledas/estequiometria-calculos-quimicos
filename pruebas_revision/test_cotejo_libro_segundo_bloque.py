# -*- coding: utf-8 -*-
"""Segundo bloque de cotejo libro definitivo + solucionario desarrollado.

Casos independientes de la primera matriz. Se emplean las funciones implementadas
cuando reproducen la operación del ejercicio. Se diferencia la magnitud interna
del redondeo editorial y se indican límites del modelo, si los hay.
Los PDF de las obras no forman parte de este repositorio.
"""
import math
import unittest
from types import SimpleNamespace
from test_auditoria_integral import mod, script, salida_valor

class CotejoLibroBloqueDos(unittest.TestCase):
    def test_2_B_2_presion_atm_pa_psi(self):
        """2.B.2, libro p.96; solucionario p.4: 2,5 atm = 253312,5 Pa = 36,74 psi."""
        m=mod('unidades_y_dimensiones')
        self.assertAlmostEqual(m.convertir_unidad(2.5,'atm','Pa'),253312.5,places=5)
        self.assertAlmostEqual(m.convertir_unidad(2.5,'atm','psi'),36.74,delta=.02)

    def test_2_B_3_calorias(self):
        """2.B.3, p.96: 150,0 cal termoquímicas = 627,6 J."""
        self.assertAlmostEqual(mod('unidades_y_dimensiones').convertir_unidad(150,'cal','J'),627.6,places=8)

    def test_2_B_4_velocidad(self):
        """2.B.4, p.96: 12,5 cm/s = 4,50·10² m/h."""
        self.assertAlmostEqual(mod('unidades_y_dimensiones').convertir_unidad(12.5,'cm/s','m/h'),450,places=9)

    def test_3_B_1_moles_co2(self):
        """3.B.1, p.158: 44,0 g CO₂ ~ 1,00 mol."""
        M=float(mod('masa_molar').calculate_molar_mass('CO2').raw_mass)
        self.assertAlmostEqual(44/M,.99977,delta=.0003)

    def test_3_B_6_cinc_hidrogeno(self):
        """3.B.6, p.158: 6,50 g Zn producen 2,23 L de H₂ (CN)."""
        mm=mod('masa_molar');gas=mod('gases_ideales_y_mezclas')
        nz=6.50/float(mm.calculate_molar_mass('Zn').raw_mass)
        # La ecuación química está incorporada como coeficientes de la reacción.
        c=mod('ajuste_ecuaciones').ajustar(['Zn','HCl'],['ZnCl2','H2'])
        self.assertEqual(c,[1,2,1,1]);self.assertAlmostEqual(gas.solve_ideal(101325,None,nz,273.15)['V']*1000,2.228,delta=.005)

    def test_4_B_3_gasometro_metano(self):
        """4.B.3, p.190: Pabs=120 kPa, masa CH₄≈79,0 kg."""
        m=mod('gases_ideales_y_mezclas')
        n=m.solve_ideal(120000,100,None,293)['n']
        self.assertAlmostEqual(n*m.molar_mass('CH4')/1000,79.0,delta=.20)

    def test_4_B_4_mezcla_ideal_molar_y_masica(self):
        """4.B.4, p.190: M≈25,1475 g/mol; composición w y caudal ≈242 kg/h."""
        m=mod('gases_ideales_y_mezclas');rows=m.mixture_from_basis(m.parse_components('C2H6:60;H2:25;CO2:15'),'molar')
        v=m.mixture_summary(rows,P=120000,T=300,V=200)
        self.assertAlmostEqual(v['Mmix'],25.1475,delta=.003)
        self.assertAlmostEqual(rows[0]['w']*100,71.7,delta=.15)
        self.assertAlmostEqual(rows[1]['w']*100,2.00,delta=.02)
        self.assertAlmostEqual(rows[2]['w']*100,26.3,delta=.1)
        self.assertAlmostEqual(v['c_total_mol_m3']/1000,.04811,delta=2e-5)
        self.assertAlmostEqual(v['rho_kg_m3']*200,241.96,delta=.08)

    def test_4_B_5_mezcla_binaria_resuelta_por_balances(self):
        """4.B.5, p.190: H₂≈2,52 g y He≈7,48 g para masa total de 10 g."""
        m=mod('gases_ideales_y_mezclas');bl=mod('balances_materia')
        nt=m.solve_ideal(415000,.02,None,320)['n']
        mh=m.molar_mass('H2');me=m.molar_mass('He')
        eq=[bl.Ecuacion([1,1],nt,'moles'),bl.Ecuacion([mh,me],10,'masa')]
        r=bl.resolver_lineal(['nH2','nHe'],eq)
        self.assertEqual(r.estado,'unico')
        self.assertAlmostEqual(r.valores['nH2']*mh,2.52,delta=.02)
        self.assertAlmostEqual(r.valores['nHe']*me,7.48,delta=.02)

    def test_4_B_6_masa_molar_porcentajes(self):
        """4.B.6, p.190: Mmix≈19,8 g/mol; cuatro fracciones másicas."""
        m=mod('gases_ideales_y_mezclas')
        rows=m.mixture_from_basis(m.parse_components('CO2:10;Cl2:15;N2:12.5;H2:62.5'),'molar')
        s=m.mixture_summary(rows)
        self.assertAlmostEqual(s['Mmix'],19.7987,delta=.02)
        for row,expected in zip(rows,[22.2,53.7,17.7,6.36]):
            self.assertAlmostEqual(row['w']*100,expected,delta=.2)

    def test_5_B_2_vdw_co2_casi_mismos_parametros(self):
        """5.B.2, p.246: vapor CO₂ van der Waals ~2,38653 L/mol.
        El programa infiere a,b de Tc,Pc de biblioteca, no acepta a,b del enunciado.
        """
        g=mod('gases_reales');r=g.cubic_state('vdw',300,10,g.resolve_gas('CO2'),'vapor')
        self.assertAlmostEqual(r['Vm'],2.38653,delta=.001)
        self.assertAlmostEqual(r['Z'],.95678,delta=.0005)

    def test_5_B_2_vdw_parametros_del_enunciado(self):
        """5.B.2, p.246: a=3,66, b=0,0428 reproducen Vm=2,38653 L/mol."""
        g=mod('gases_reales')
        r=g.vdw_state_from_ab(300,10,3.66,.0428,M=44.01)
        self.assertAlmostEqual(r['Z'],.956778,delta=2e-6)
        self.assertAlmostEqual(r['Vm'],2.38653,delta=2e-5)
        self.assertAlmostEqual(r['P_reconstructed'],10,delta=1e-9)
        self.assertGreater(r['Vm'],r['b'])

    def test_5_B_2_vdw_rechaza_coeficientes_no_fisicos(self):
        """El modo de parámetros directos no acepta a,b negativos, cero, NaN."""
        g=mod('gases_reales')
        for vals in [(300,10,-3.66,.0428),(300,10,3.66,0),
                     (float('nan'),10,3.66,.0428),(300,10,float('inf'),.0428)]:
            with self.subTest(vals=vals):
                with self.assertRaises(ValueError):g.vdw_state_from_ab(*vals)

    def test_5_B_2_vdw_interfaz_cli_parametros_directos(self):
        """La interfaz pública entrega los valores del ejercicio y valida opciones."""
        import subprocess,sys
        from test_auditoria_integral import ROOT
        args=[sys.executable,str(ROOT/'capitulo_05/gases_reales.py'),
              '--sigfigs','8','estado','--gas','CO2','--T','300',
              '--P','10','--modelo','vdw','--vdw-a','3.66','--vdw-b','0.0428']
        p=subprocess.run(args,capture_output=True,text=True,timeout=12)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertIn('Vm = 2,3865283',p.stdout)
        p2=subprocess.run(args[:-2],capture_output=True,text=True,timeout=12)
        self.assertEqual(p2.returncode,2)

    def test_5_B_3_rk_amoniaco(self):
        """5.B.3, p.246: RK NH₃, Z≈0,960829 y Vm≈2,97981 L/mol."""
        g=mod('gases_reales');r=g.cubic_state('rk',373,10,g.resolve_gas('NH3'),'vapor')
        self.assertAlmostEqual(r['Z'],.960829,delta=2e-6)
        self.assertAlmostEqual(r['Vm'],2.97981,delta=5e-5)

    def test_5_B_5_virial_rama_vapor(self):
        """5.B.5, p.247: n-butano, raíz de vapor ≈8,2959 L/mol, no la pequeña."""
        g=mod('gases_reales');r=g.virial_volume(511,5,-.19667)
        self.assertAlmostEqual(r['Vm'],8.2959,delta=.0001)
        self.assertAlmostEqual(r['Z'],.97629,delta=.0001)
        self.assertGreater(r['Vm'],8)

    def test_6_B_1_clausius_eter(self):
        """6.B.1, p.291: éter 385 kJ/kg, P(298)=71,8, P(308)=104 kPa."""
        m=mod('presion_vapor');H=385000*.07412
        self.assertAlmostEqual(m.cc_pressure2(25,273,298,H),71.7768,delta=.01)
        self.assertAlmostEqual(m.cc_pressure2(25,273,308,H),104.3234,delta=.02)

    def test_6_B_7_antoine_acrilonitrilo(self):
        """6.B.7, p.292: Antoine ad hoc acrilonitrilo P(300)≈15,3333 kPa."""
        m=mod('presion_vapor');a=m.AntoineData('acrilonitrilo',6.04117,1208.30,-51.15,250,400)
        self.assertAlmostEqual(m.antoine_pressure_kpa(300,a),15.3333,delta=.0001)
        self.assertAlmostEqual(m.antoine_temperature_k(m.antoine_pressure_kpa(300,a),a),300,places=8)

    def test_6_B_9_titulo_vapor_entalpia_tabla_enunciado(self):
        """6.B.9, p.292: x=(2100−640,1)/(2748,1−640,1)≈0,692552."""
        m=mod('vapor_agua')
        # El ejercicio proporciona datos tabulares expresos, no la tabla integrada.
        row=SimpleNamespace(vf=1,vg=2,hf=640.1,hg=2748.1,sf=1,sg=2)
        x,_,_=m.quality_from_property(row,'h',2100)
        self.assertAlmostEqual(x,.692552,delta=.00001)
        self.assertAlmostEqual(1-x,.307448,delta=.00001)

    def test_7_B_2_raoult_masas_iguales(self):
        """7.B.2, p.358: benz/tol masa igual, P=9,38808 kPa, ybenz≈0,79618."""
        vp=mod('presion_vapor');eq=mod('equilibrio_liquido_vapor')
        x=(1/78.11)/((1/78.11)+(1/92.14)); t=300
        ps=[vp.antoine_pressure_kpa(t,vp.ANTOINE[k]) for k in ('benceno','tolueno')]
        r=eq.raoult_from_pstar([x,1-x],ps)
        self.assertAlmostEqual(r['P'],9.38808,delta=.003)
        self.assertAlmostEqual(r['y'][0],.796178,delta=.0002)
        w=r['y'][0]*78.11/(r['y'][0]*78.11+r['y'][1]*92.14)
        self.assertAlmostEqual(w,.768059,delta=.0002)

    def test_7_B_3_rocio_ideal(self):
        """7.B.3, p.358: rocío P=57,55396 kPa, xA=.251799."""
        p,x=mod('equilibrio_liquido_vapor').dew_from_pstar([.35,.65],[80,50])
        self.assertAlmostEqual(p,57.55396,delta=2e-5)
        self.assertAlmostEqual(x[0],.251799,delta=3e-6)

    def test_7_B_4_burbuja_antoine(self):
        """7.B.4, p.358: Tbur=366,82004 K yhex=.208475."""
        m=mod('equilibrio_liquido_vapor')
        comps=[m.parse_component('hexano;6.00265;1171.531;-48.780;245;370'),
               m.parse_component('heptano;6.01876;1264.370;-56.510;270;400')]
        root,pstar,y=m.bubble_temperature(comps,[.1,.9],100)
        self.assertAlmostEqual(root.root,366.82004,delta=.0002)
        self.assertAlmostEqual(y[0],.208475,delta=.00002)

    def test_8_B_4_margules_asimetrico(self):
        """8.B.4, p.457: γ1≈1,45648; γ2≈1,23001; gE/RT=.266175."""
        m=mod('disoluciones_no_ideales')
        gam,act,ge=m.activity_properties([.35,.65],m.Margules2(1.45,.65))
        self.assertAlmostEqual(float(gam[0]),1.45648,delta=1e-5)
        self.assertAlmostEqual(float(gam[1]),1.23001,delta=1e-5)
        self.assertAlmostEqual(float(ge),.266175,delta=1e-7)
        self.assertAlmostEqual(math.exp(1.45),4.263,delta=.003)

    def test_9_B_2_coexistencia_beysens(self):
        """9.B.2, p.513: epsilon=.0100; Δw=.42310786; mL1=.874082 kg."""
        m=mod('equilibrio_liquido_liquido')
        dw,w1,w2=m.beysens(.01,1.83,.318,.5350)
        r=m.regla_palanca(1.5,.5,w1,w2)
        self.assertAlmostEqual(dw,.42310786,delta=1e-7)
        self.assertAlmostEqual(w1,.323446,delta=3e-6)
        self.assertAlmostEqual(r.l1,.874082,delta=1e-5)
        self.assertAlmostEqual(r.l2,.625918,delta=1e-5)

    def test_10_B_2_naftaleno_crioscopia(self):
        """10.B.2, p.587: 0,2 mol/kg, ΔTf=1,024 K, ΔTb=.506 K."""
        m=mod('propiedades_coligativas'); mol=(12.817/128.17)/.5000
        self.assertAlmostEqual(m.coligativa(5.12,mol,1),1.024,delta=1e-9)
        self.assertAlmostEqual(m.coligativa(2.53,mol,1),.506,delta=1e-9)

    def test_10_B_3_vant_hoff_experimental(self):
        """10.B.3, p.587: i≈1,828 y desviación ≈−8,6 %."""
        m=mod('propiedades_coligativas')
        i=m.factor_vanthoff(3.4,1.86,1.00)
        self.assertAlmostEqual(i,1.827957,delta=.00001)
        self.assertAlmostEqual(100*(i-2)/2,-8.602,delta=.01)

    def test_10_B_4_osmosis_glucosa(self):
        """10.B.4, p.587: 9,00 g/L glucosa, π≈1,23838 bar."""
        m=mod('propiedades_coligativas')
        c=9/180.16
        self.assertAlmostEqual(m.presion_osmotica(c,298.15),1.23838,delta=.0004)

    def test_11_B_5_corriente_etanol_agua(self):
        """11.B.5, p.658: 36+84=120 kg/h, wEtOH=.300."""
        m=mod('balances_materia')
        r=m.resolver_lineal(['F','wEtOH_masa'],[
            m.Ecuacion([1,0],36+84,'total'),m.Ecuacion([0,1],36,'etanol')])
        self.assertEqual(r.estado,'unico')
        self.assertAlmostEqual(r.valores['F'],120,places=8)
        self.assertAlmostEqual(r.valores['wEtOH_masa']/r.valores['F'],.3,places=8)

    def test_11_B_8_dilucion_glucosa(self):
        """11.B.8, p.658: 80 kg/h w=.3 + agua = 200 kg/h w=.12."""
        m=mod('balances_materia')
        r=m.resolver_lineal(['agua','glucosa'],[
            m.Ecuacion([1,0],200-80,'total'),m.Ecuacion([0,1],80*.30,'glucosa')])
        self.assertEqual(r.estado,'unico')
        self.assertAlmostEqual(r.valores['agua'],120,places=9)
        self.assertAlmostEqual(r.valores['glucosa']/200,.12,places=9)

    def test_12_B_1_secado_jabon(self):
        """12.B.1, p.711: 1000 kg al 50 % agua -> 625 kg al 20 %, 375 evaporada."""
        s=script('secado',['1','1000.0','50.0','20.0'])
        self.assertAlmostEqual(salida_valor(s,'Producto final'),625,delta=2)
        self.assertAlmostEqual(salida_valor(s,'Agua eliminada'),375,delta=2)

    def test_12_B_5_dos_evaporadores(self):
        """12.B.5, p.712: F1=2000, F2=800, vapor 2000+1200 kg/h."""
        s1=script('evaporacion',['4000.0','10.0','20.0'])
        s2=script('evaporacion',['2000.0','20.0','50.0'])
        self.assertAlmostEqual(salida_valor(s1,'Disolución concentrada'),2000,delta=3)
        self.assertAlmostEqual(salida_valor(s2,'Disolución concentrada'),800,delta=3)
        self.assertAlmostEqual(salida_valor(s1,'Disolvente evaporado'),2000,delta=3)
        self.assertAlmostEqual(salida_valor(s2,'Disolvente evaporado'),1200,delta=3)

    def test_13_B_2_descomposicion_amoniaco(self):
        """13.B.2, p.759: ξ=2,40; N₂=2,40 H₂=7,20 y NH₃ rem=3,20."""
        m=mod('balance_una_reaccion'); Q=m.Q.exact_value
        species=[{'name':'NH3','nu':-2},{'name':'N2','nu':1},{'name':'H2','nu':3}]
        delta,final=m.calculate_final(species,[Q(8),Q(0),Q(0)],Q('2.4'))
        for x,v in zip(final,[3.2,2.4,7.2]): self.assertAlmostEqual(float(x.value),v,places=10)

    def test_13_B_3_hidrogenacion_acetaldehido(self):
        """13.B.3, p.759: X=.72, salida 1,4 CH3CHO; 3,4 H₂ y 3,6 etanol."""
        m=mod('balance_una_reaccion');Q=m.Q.exact_value
        species=[{'name':'acetaldehido','nu':-1},{'name':'H2','nu':-1},{'name':'etanol','nu':1}]
        delta,final=m.calculate_final(species,[Q(5),Q(7),Q(0)],Q(5*.72))
        for x,v in zip(final,[1.4,3.4,3.6]):self.assertAlmostEqual(float(x.value),v,places=10)

    def test_13_B_8_reacciones_sucesivas(self):
        """13.B.8, p.760: A→B→C, ξ=(8;5) y salida (2;3;5)."""
        m=mod('balance_varias_reacciones');Q=m.Q.exact_value
        names=['A','B','C'];nu=[[-1,0],[1,-1],[0,1]]
        changes,final=m.calculate_final(names,nu,[Q(10),Q(0),Q(0)],[Q(8),Q(5)])
        for x,v in zip(final,[2,3,5]):self.assertAlmostEqual(float(x.value),v,places=10)

    def test_14_B_1_combustion_etano(self):
        """14.B.1, p.807: 12 mol etano -> 42 O₂, 24 CO₂, 36 H₂O."""
        m=mod('combustion');o,p=m.oxygen_stoich_formula('C2H6',12,m.ProductModel())
        self.assertAlmostEqual(o,42,places=9)
        self.assertEqual(p,{'CO2':24,'H2O':36})

    def test_14_B_2_combustion_propanol(self):
        """14.B.2, p.807: 5 mol C3H8O -> 22,5 O₂, 15 CO₂, 20 H₂O."""
        m=mod('combustion');o,p=m.oxygen_stoich_formula('C3H8O',5,m.ProductModel())
        self.assertAlmostEqual(o,22.5,places=9)
        self.assertEqual(p,{'CO2':15,'H2O':20})

    def test_14_B_3_aire_teorico_metano(self):
        """14.B.3, p.807: 25 mol CH₄, 50 mol O₂, 238,095 aire y 188,095 N₂."""
        m=mod('combustion');o,p=m.oxygen_stoich_formula('CH4',25,m.ProductModel())
        self.assertAlmostEqual(o,50,places=9)
        self.assertAlmostEqual(o/.21,238.095238,delta=.001)
        self.assertAlmostEqual(o*.79/.21,188.095238,delta=.001)

    def test_14_B_4_exceso_aire_propano(self):
        """14.B.4, p.807: 15 mol propano, aire real≈464,3; O₂ sobrante=22,5."""
        m=mod('combustion');o,_=m.oxygen_stoich_formula('C3H8',15,m.ProductModel())
        self.assertAlmostEqual(o,75,places=9)
        self.assertAlmostEqual(o*1.30/.21,464.285714,delta=.001)
        self.assertAlmostEqual(o*.30,22.5,delta=1e-9)

    def test_14_B_7_mezcla_inertes_aire(self):
        """14.B.7, p.808: mezcla CH₄/C₂H₆/CO₂/N₂ da O₂=40 y CO₂=23."""
        m=mod('combustion');comps=[('CH4',13,True),('C2H6',4,True),('CO2',2,False),('N2',1,False)]
        o,p=m.complete_products_for_mixture(comps,m.ProductModel())
        self.assertAlmostEqual(o,40,places=9)
        self.assertAlmostEqual(p['CO2'],23,places=9)
        self.assertAlmostEqual(p['H2O'],38,places=9)
        self.assertAlmostEqual(o*.79/.21+p['N2'],151.47619,delta=.002)

    def test_15_B_3_saturacion_35_grados(self):
        """15.B.3, p.883: pv*=5,628 kPa, yv=.05554, W=.03657 kg/kg."""
        m=mod('psicrometria');p=101.325;pv=5.628
        W=m.humidity_ratio_from_pw(pv,p)
        self.assertAlmostEqual(pv/p,.055544,delta=.000002)
        self.assertAlmostEqual(pv/(p-pv),.058811,delta=.00001)
        self.assertAlmostEqual(W,.03657,delta=.00002)

    def test_15_B_4_humedad_relativa_saturacion(self):
        """15.B.4, p.884: W=.010, pv≈1,604 kPa, RH≈37,8%, S≈36,8%."""
        m=mod('psicrometria');pv=m.pw_from_humidity_ratio(.0100,101.325)
        self.assertAlmostEqual(pv,1.604,delta=.003)
        self.assertAlmostEqual(100*pv/4.245,37.8,delta=.15)
        Wsat=m.humidity_ratio_from_pw(4.245,101.325)
        self.assertAlmostEqual(100*.0100/Wsat,36.8,delta=.15)

    def test_15_B_5_vapor_por_masa_aire_seco(self):
        """15.B.5, p.884: 2 kg aire seco RH=.45 -> 15,3 g de vapor."""
        m=mod('psicrometria');w=m.humidity_ratio_from_pw(.45*2.645,98.0)
        self.assertAlmostEqual(2*w*1000,15.3,delta=.06)

if __name__ == '__main__':
    unittest.main()
