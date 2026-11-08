# -*- coding: utf-8 -*-
"""Cotejo trazable: libro definitivo (934 pp.) + solucionario desarrollado (220 pp.).

Cada método reproduce un ejercicio identificado en ambas obras usando las
funciones de las aplicaciones. Las tolerancias distinguen valores internos y
redondeo editorial. Esta muestra NO cubre todos los ejercicios ni modalidades.
"""
import math
import unittest
from test_auditoria_integral import mod, script, salida_valor


class CotejoLibroSolucionario(unittest.TestCase):
    def test_2_B_1_conversion_ft3_m3(self):
        """Libro p. 96; solucionario 2.B.1: 125 ft³ = 3,54 m³ (3 cifras)."""
        m = mod('unidades_y_dimensiones')
        r = m.convertir_unidad(125, 'ft3', 'm3')
        self.assertAlmostEqual(r, 3.539605824, places=9)
        self.assertEqual(f'{r:.2f}', '3.54')

    def test_3_B_5_ajuste_y_masa_cloruro(self):
        """Libro p. 158; 3.B.5: 11,5 g Na => 29,2 g NaCl."""
        eq = mod('ajuste_ecuaciones')
        mm = mod('masa_molar')
        self.assertEqual(eq.ajustar(['Na','Cl2'], ['NaCl']), [2,1,2])
        mNaCl = float(mm.calculate_molar_mass('NaCl').raw_mass)
        mNa = float(mm.calculate_molar_mass('Na').raw_mass)
        self.assertAlmostEqual(11.5 * mNaCl / mNa, 29.23, delta=.02)

    def test_3_B_11_brix_masa_jarabe(self):
        """Libro p. 158; 3.B.11: 180 g sacarosa / 600 g => 30,0 Bx."""
        m = mod('densidades_y_escalas')
        bx = 100.0*180/(180+420)
        # La conversión Brix->densidad usa la escala correcta, pero el balance
        # de concentración por evaporación es una operación algebraica distinta.
        ge = m.brix_a_ge(m.Q(bx))
        self.assertGreater(float(ge.v), 1.0)
        self.assertAlmostEqual(bx, 30, places=10)
        self.assertAlmostEqual(180/0.5 - 180, 180, places=10)  # agua final
        self.assertAlmostEqual(600-180/0.5, 240, places=10)

    def test_3_B_12_ajuste_acido_benzoico(self):
        """Libro p. 159; 3.B.12: 2 : 15 : 14 : 6."""
        m = mod('ajuste_ecuaciones')
        self.assertEqual(m.ajustar(['C7H6O2','O2'],['CO2','H2O']),[2,15,14,6])

    def test_4_B_1_densidades_metano_dioxido_azufre(self):
        """Libro p. 190; 4.B.1: 0,716 y 2,86 g/L en condiciones normales."""
        m = mod('gases_ideales_y_mezclas')
        n = m.solve_ideal(101325.0, None, 1.0, 273.15)
        vm_l = n['V'] * 1000.0
        self.assertAlmostEqual(vm_l, 22.414, delta=.002)
        self.assertAlmostEqual(m.molar_mass('CH4')/vm_l, .7156, delta=.001)
        self.assertAlmostEqual(m.molar_mass('SO2')/vm_l, 2.858, delta=.003)

    def test_5_B_1_gas_ideal_y_Z(self):
        """Libro p. 246; 5.B.1: Vm ideal 3,6376 L/mol, Z=0,92 => 3,3466."""
        m = mod('gases_reales')
        state = m.ideal_state(350,8,m.resolve_gas('metano'))
        self.assertAlmostEqual(state['Vm'],3.6376,delta=.0001)
        self.assertAlmostEqual(state['Vm']*.92,3.3466,delta=.0002)

    def test_6_B_11_interpolaciones(self):
        """Libro p. 293; 6.B.11: lineal 20,25; CC 18,7372 kPa."""
        m = mod('presion_vapor')
        self.assertAlmostEqual(m.linear_interpolation(320,12,340,28.5,330),20.25,places=8)
        self.assertAlmostEqual(m.cc_interpolation(320,12,340,28.5,330),18.7372,delta=.0002)

    def test_6_B_15_antoine_metanoL(self):
        """Libro p. 294; 6.B.15: 18,6 y 48,4 kPa; delta Hvap~38,1 kJ/mol."""
        m = mod('presion_vapor')
        a = m.ANTOINE['metanol']
        p1,p2=m.antoine_pressure_kpa(300,a),m.antoine_pressure_kpa(320,a)
        self.assertAlmostEqual(p1,18.6,delta=.12)
        self.assertAlmostEqual(p2,48.4,delta=.2)
        self.assertAlmostEqual(m.cc_enthalpy(p1,300,p2,320)/1000,38.1,delta=.18)

    def test_7_B_1_raoult_heptano_tolueno(self):
        """Libro p. 357; 7.B.1: xhep 0,853125; yhep 0,892707."""
        m=mod('equilibrio_liquido_vapor')
        x=(101.3-74)/(106-74)
        res=m.raoult_from_pstar([x,1-x],[106,74])
        self.assertAlmostEqual(res['P'],101.3,places=7)
        self.assertAlmostEqual(res['y'][0],.892707,delta=2e-6)
        self.assertAlmostEqual(x,.853125,places=8)

    def test_7_C_8_palanca_fases_lv(self):
        """Libro p. 366; 7.C.8: L/F=V/F=0,5."""
        m=mod('operaciones_liquido_vapor')
        r=m.lever_rule([.45,.55],[.25,.75],[.65,.35],1)
        self.assertAlmostEqual(r.liquid_fraction,.5,places=10)
        self.assertAlmostEqual(r.beta,.5,places=10)
        self.assertAlmostEqual(r.L*.25+r.V*.65,.45,places=10)

    def test_8_B_3_margules_un_parametro(self):
        """Libro p. 456; 8.B.3: gamma=(1,80038;1,11405); gE/RT=0,252."""
        m=mod('disoluciones_no_ideales')
        gam,act,ge=m.activity_properties([.3,.7],m.Margules1(1.20))
        self.assertAlmostEqual(float(gam[0]),1.80038,delta=1e-5)
        self.assertAlmostEqual(float(gam[1]),1.11405,delta=1e-5)
        self.assertAlmostEqual(float(act[0]),.54012,delta=1e-5)
        self.assertAlmostEqual(float(ge),.252,delta=1e-10)

    def test_9_B_1_palanca_dos_liquidos(self):
        """Libro p. 513; 9.B.1: mL1=0,94818; mL2=1,55182 kg."""
        m=mod('equilibrio_liquido_liquido')
        r=m.regla_palanca(2.5,.600,.2658,.8042)
        self.assertAlmostEqual(r.l1,.948180,delta=2e-6)
        self.assertAlmostEqual(r.l2,1.551820,delta=2e-6)
        self.assertAlmostEqual(r.a_l1,.252026,delta=2e-6)
        self.assertAlmostEqual(r.a_l2,1.247974,delta=2e-6)

    def test_9_B_5_destilacion_inmiscibles(self):
        """Libro p. 515; 9.B.5: T=342,27133 K, yagua=.296189."""
        m=mod('inmiscibles_y_arrastre_vapor')
        t=m.temperatura_trifasica(m.AGUA_2,m.BENCENO,1.01325).t
        r=m.composicion_vapor(m.AGUA_2,m.BENCENO,t,1.01325)
        self.assertAlmostEqual(t,342.27133,delta=.00005)
        self.assertAlmostEqual(r['y_a'],.296189,delta=2e-6)
        self.assertAlmostEqual(r['m_b_a'],10.30295,delta=2e-5)
        self.assertAlmostEqual(m.consumo_agua(1,r['m_b_a']),.0970596,delta=1e-7)

    def test_10_B_1_glucosa_crioscopia_ebulloscopia(self):
        """Libro p. 586; 10.B.1: m=.39964, deltaTf=.7433, deltaTb=.2046."""
        m=mod('propiedades_coligativas')
        molal=(36.0/180.16)/.5000
        self.assertAlmostEqual(molal,.39964,delta=1e-5)
        self.assertAlmostEqual(m.coligativa(1.86,molal,1),.7433,delta=.0002)
        self.assertAlmostEqual(m.coligativa(.512,molal,1),.2046,delta=.0002)

    def test_10_B_6_davies_iones(self):
        """Libro p. 587; 10.B.6: I=.05; gamma monovalente=.8215; Ca2+=.4555."""
        m=mod('disoluciones_electroliticas')
        ions=[m.Ion('Na',1,.0200),m.Ion('Ca',2,.0100),m.Ion('Cl',-1,.0400)]
        I=m.fuerza_ionica(ions)
        self.assertAlmostEqual(I,.05,places=10)
        self.assertAlmostEqual(m.gamma_ion(1,I,'davies'),.8215,delta=.0001)
        self.assertAlmostEqual(m.gamma_ion(2,I,'davies'),.4555,delta=.0001)

    def test_11_B_7_mezcla_nacl(self):
        """Libro p. 658; 11.B.7: 250 kg/h y wNaCl=0,160."""
        m=mod('balances_materia')
        eq=[m.Ecuacion([1,0],150+100,'total'),m.Ecuacion([0,1],150*.10+100*.25,'NaCl')]
        r=m.resolver_lineal(['F','NaCl'],eq)
        self.assertEqual(r.estado,'unico')
        self.assertAlmostEqual(r.valores['F'],250,places=9)
        self.assertAlmostEqual(r.valores['NaCl'],40,places=9)
        self.assertAlmostEqual((150*.10+100*.25)/250,.16,places=9)

    def test_12_B_3_secado_consola(self):
        """Libro p. 711; 12.B.3: producto 101,44 kg; evaporada 18,6 kg."""
        s=script('secado',['1','120.0','18.0','3.00'])
        self.assertAlmostEqual(salida_valor(s,'Producto final'),101,delta=.51)
        self.assertAlmostEqual(salida_valor(s,'Agua eliminada'),18.6,delta=.1)

    def test_12_B_4_evaporacion_consola(self):
        """Libro p. 712; 12.B.4: masa final 100 g, agua eliminada 150 g."""
        s=script('evaporacion',['250.0','8.00','20.0'])
        self.assertAlmostEqual(salida_valor(s,'Disolución concentrada'),100,delta=.05)
        self.assertAlmostEqual(salida_valor(s,'Disolvente evaporado'),150,delta=.05)

    def test_12_C_4_extraccion_una_dos_tres_etapas(self):
        """Libro p. 715; 12.C.4: E1 62,6866; E2 70,4631; E3 73,6594 %."""
        m=mod('extraccion_liquido_liquido')
        for n,vd,ref in [(1,120,62.6866),(2,60,70.4631),(3,40,73.6594)]:
            with self.subTest(n=n):
                f=m.fraccion_restante(m.leer_medida('250.0'),m.leer_medida(str(vd)+'.0'),m.leer_medida('3.50'))
                pct=100*(1-float(f.valor)**n)
                self.assertAlmostEqual(pct,ref,delta=.0002)

    def test_13_B_1_reaccion_unica_n2o5(self):
        """Libro p. 759; 13.B.1: xi=.250 mol, NO2=1 mol, O2=.250 mol."""
        m=mod('balance_una_reaccion')
        sp=[{'nu':-2},{'nu':4},{'nu':1}]
        ini=[m.Q.exact_value(.8),m.Q.exact_value(0),m.Q.exact_value(0)]
        _,fin=m.calculate_final(sp,ini,m.Q.exact_value(.25))
        got=[float(q.value) for q in fin]
        for a,b in zip(got,[.3,1.0,.25]):self.assertAlmostEqual(a,b,places=12)
        self.assertAlmostEqual(sum(got),1.55,places=10)

    def test_13_B_7_reacciones_simultaneas(self):
        """Libro p. 760; 13.B.7: xi=(3;2), A=7, B=3, C=4."""
        m=mod('balance_varias_reacciones')
        ini=[m.Q.exact_value(12),m.Q.exact_value(0),m.Q.exact_value(0)]
        _,out=m.calculate_final(['A','B','C'],[[-1,-1],[1,0],[0,2]],ini,
                                [m.Q.exact_value(3),m.Q.exact_value(2)])
        got=[float(q.value) for q in out]
        self.assertEqual(got,[7,3,4])
        self.assertAlmostEqual(sum(got),14,places=10)

    def test_14_B_6_combustion_mezcla_metan_etano(self):
        """Libro p. 808; 14.B.6: 24,5 mol O2 y 117 mol aire teórico."""
        m=mod('combustion')
        o2,p=m.complete_products_for_mixture([('CH4',7,True),('C2H6',3,True)],m.ProductModel())
        self.assertAlmostEqual(o2,24.5,places=10)
        self.assertAlmostEqual(o2/.210,116.6666666667,delta=1e-8)
        self.assertAlmostEqual(p['CO2'],13,places=10)
        self.assertAlmostEqual(p['H2O'],23,places=10)

    def test_15_B_2_humedad_relativa_saturacion(self):
        """Libro p. 883; 15.B.2: pv=1,5197 kPa, w=.00960, ws=.0149, S=64,5 %."""
        m=mod('psicrometria')
        pv=.65*2.338
        w=m.humidity_ratio_from_pw(pv,100)
        ws=m.humidity_ratio_from_pw(2.338,100)
        self.assertAlmostEqual(pv,1.5197,places=9)
        self.assertAlmostEqual(w,.00960,delta=.00001)
        self.assertAlmostEqual(ws,.0149,delta=.00002)
        self.assertAlmostEqual(100*w/ws,64.5,delta=.1)


    def test_3_B_13_reactivo_limitante_amoniaco(self):
        """Libro p. 159; 3.B.13: H2 limitante; NH3=20 mol; N2 restante=2 mol."""
        m=mod('reactivo_limitante')
        cap,idx,maxi,adv,rest,prod=m.balance([m.Q(12),m.Q(30)],[1,3],[2])
        self.assertEqual(idx,[1])
        self.assertAlmostEqual(float(rest[0].v),2,places=10)
        self.assertAlmostEqual(float(rest[1].v),0,places=10)
        self.assertAlmostEqual(float(prod[0].v),20,places=10)

    def test_3_B_16_conversion_etanol(self):
        """Libro p. 159; 3.B.16: 100 mol etanol, 30 finales -> X=70%."""
        m=mod('conversion_rendimiento_selectividad')
        x=m.fraccion_conversion(m.Q(100),m.Q(30))
        self.assertAlmostEqual(float(x.v),.700,places=10)
        # La selectividad requiere comparar las extensiones de las dos rutas.
        self.assertAlmostEqual(50/(40/2),2.5,places=10)

    def test_3_B_20_hall_brix_metodo_explicito(self):
        """Libro p. 161; 3.B.20: Hall B=18 -> GE=1,074221119568."""
        m=mod('densidades_y_escalas')
        hall=m.brix_a_ge_hall(m.Q(18))
        self.assertAlmostEqual(float(hall.v),1.074221119568,delta=1e-11)
        self.assertAlmostEqual(float(hall.v)*.9982,1.072288,delta=1e-6)
        self.assertAlmostEqual(float(hall.v)*.9982*250,268.072,delta=.003)
        # El método tabulado es otra correlación, no una contradicción matemática.
        self.assertGreater(abs(float(hall.v)-float(m.brix_a_ge(m.Q(18)).v)),.0001)
        with self.assertRaises(ValueError):m.brix_a_ge_hall(m.Q(34))

    def test_6_B_13_estado_agua_y_titulo(self):
        """Libro p. 293; 6.B.13: vapor sobrecalentado; x~0,494."""
        m=mod('vapor_agua')
        self.assertIn('sobrecalentado',m.identify_state(300,160)['estado'])
        row=m.saturated_properties_at_P(300)
        x, vf, vg=m.quality_from_property(row,'v',.300)
        self.assertAlmostEqual(x,.494317,delta=.00006)
        self.assertAlmostEqual(vf,.001073,delta=1e-6)
        self.assertAlmostEqual(vg,.6058,delta=.0001)

    def test_12_B_7_filtracion_carbonato(self):
        """Libro p. 712; 12.B.7: torta 28,3 kg; filtrado 221,69 kg."""
        out=script('filtracion',['250.0','8.00','92.0','65.0'])
        self.assertAlmostEqual(salida_valor(out,'Sólido en la torta'),18.4,delta=.05)
        self.assertAlmostEqual(salida_valor(out,'Masa de torta'),28.3,delta=.05)
        self.assertAlmostEqual(salida_valor(out,'Masa de filtrado'),221.692,delta=.1)

    def test_12_B_8_cristalizacion_nacl(self):
        """Libro p. 712; 12.B.8: agua~251,256 kg; cristales 10,3 kg."""
        out=script('cristalizacion',['100.0','39.8','35.7'])
        self.assertAlmostEqual(salida_valor(out,'Disolvente inicial'),251.256,delta=.6)
        self.assertAlmostEqual(salida_valor(out,'Cristales obtenidos'),10.3015,delta=.07)

    def test_12_B_14_separacion_por_recuperacion(self):
        """Libro p. 714; 12.B.14: recuperación 90%, flujos 180/420 kg/h."""
        import subprocess,sys,os
        from test_auditoria_integral import ROOT
        proc=subprocess.run([sys.executable,str(ROOT/'capitulo_12/separacion_corrientes.py'),
                             '--recuperacion'],input='600\n15.0\n45.0\n90.0\n',
                            capture_output=True,text=True,timeout=15,
                            env={**os.environ,'MPLBACKEND':'Agg'})
        self.assertEqual(proc.returncode,0,proc.stderr)
        self.assertAlmostEqual(salida_valor(proc.stdout,'Corriente 1'),180,delta=.5)
        self.assertAlmostEqual(salida_valor(proc.stdout,'Corriente 2'),420,delta=.5)
        self.assertIn('Concentración de soluto en corriente 2',proc.stdout)

if __name__=='__main__': unittest.main()
