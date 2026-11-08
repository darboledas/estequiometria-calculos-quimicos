# -*- coding: utf-8 -*-
"""Tercer bloque: cotejo libro definitivo/solucionario, ejercicios de tipo C.

Se prueban magnitudes concretas identificadas; no debe confundirse con una
validación de todos los apartados, gráficos o hipótesis experimentales.
"""
import math
import unittest
from test_auditoria_integral import mod, script, salida_valor

class CotejoIntegradoresTres(unittest.TestCase):
    def test_7_C_1_ideal_metoh_agua(self):
        """7.C.1: Raoult predice P=78,7809 kPa, yMeOH=0,425053."""
        v=mod('presion_vapor'); r=mod('equilibrio_liquido_vapor')
        ps=[v.antoine_pressure_kpa(356.55,v.ANTOINE[q]) for q in ('metanol','agua')]
        out=r.raoult_from_pstar([.164,.836],ps)
        self.assertAlmostEqual(out['P'],78.7809,delta=.003)
        self.assertAlmostEqual(out['y'][0],.425053,delta=4e-5)
        self.assertAlmostEqual(100*(out['P']/101.3-1),-22.2301,delta=.01)

    def test_7_C_3_flash_rachford_rice(self):
        """7.C.3: flash bifásico, V/F=0,3791652 y balances de ambas especies."""
        m=mod('operaciones_liquido_vapor')
        o=m.flash_from_K([.65,.35],[136.09/101.3,54.21/101.3],F=100)
        self.assertEqual(o.state,'BIFASICO')
        self.assertAlmostEqual(o.split.beta,.3791652,delta=1e-7)
        self.assertAlmostEqual(o.split.x[0],.5751099,delta=1e-6)
        self.assertAlmostEqual(o.split.y[0],.7726230,delta=1e-6)
        self.assertAlmostEqual(o.split.L+o.split.V,100,places=8)
        self.assertTrue(all(abs(e)<1e-9 for e in o.split.component_balance_error))

    def test_7_C_5_antoine_pxy(self):
        """7.C.5a: Pbur(370 K,xA=.5)=97,8379 kPa."""
        m=mod('equilibrio_liquido_vapor')
        c=[m.parse_component('benceno;6.0305;1211.03;-52.41;320;450'),
           m.parse_component('etilbenceno;6.0821;1424.26;-60.00;320;450')]
        P,_,y=m.bubble_pressure(c,[.5,.5],370)
        self.assertAlmostEqual(P,97.8379,delta=.02)
        self.assertAlmostEqual(y[0],.842900,delta=.0001)

    def test_7_C_5_antoine_txy(self):
        """7.C.5b: Tbur(xA=.5, 100kPa)=370,764 K."""
        m=mod('equilibrio_liquido_vapor')
        c=[m.parse_component('benceno;6.0305;1211.03;-52.41;320;450'),
           m.parse_component('etilbenceno;6.0821;1424.26;-60.00;320;450')]
        root,_,y=m.bubble_temperature(c,[.5,.5],100)
        self.assertAlmostEqual(root.root,370.764,delta=.025)
        self.assertAlmostEqual(y[0],.8422,delta=.0003)

    def test_8_C_1_azeotropo_margules(self):
        """8.C.1: azeótropo 0,695835; presión máxima mayor que ambos puros."""
        m=mod('disoluciones_no_ideales'); vp=m.DirectPsat([80,50]); model=m.Margules1(1.20)
        x=m.azeotrope_margules1_analytic(1.20,80,50)
        P,y,g,_=m.bubble_pressure([x,1-x],300,model,vp)
        self.assertAlmostEqual(x,.695835,delta=2e-6)
        self.assertAlmostEqual(y[0],x,delta=1e-9)
        self.assertGreater(P,80)
        self.assertAlmostEqual(g[0]*80,g[1]*50,delta=1e-7)

    def test_8_C_1_curva_presion(self):
        """8.C.1a: punto x1=.50, Pbur=87,741, y1=.6154."""
        m=mod('disoluciones_no_ideales');P,y,_,_=m.bubble_pressure([.5,.5],300,m.Margules1(1.2),m.DirectPsat([80,50]))
        self.assertAlmostEqual(P,87.741,delta=.005)
        self.assertAlmostEqual(y[0],.6154,delta=.0002)

    def test_8_C_3_gibbs_duhem_diferencial(self):
        """8.C.3: derivadas de ln γ en 0,2, 0,5 y 0,8; residuo cero."""
        m=mod('disoluciones_no_ideales')
        for x,d1,d2 in ((.2,-2.016,.504),(.5,-.9,.9),(.8,-.216,.864)):
            a,b=m.margules2_dln_dx(x,1.10,.70)
            self.assertAlmostEqual(a,d1,delta=1e-9)
            self.assertAlmostEqual(b,d2,delta=1e-9)
            self.assertAlmostEqual(x*a+(1-x)*b,0,delta=1e-10)

    def test_8_C_5_gamma_phi(self):
        """8.C.5: 395 kPa Raoult modificado; 424,5867 kPa γ-φ."""
        m=mod('disoluciones_no_ideales');model=m.ConstantGamma([1.3,.9]);vp=m.DirectPsat([500,250]);x=[.4,.6]
        P1,y1,_,_=m.bubble_pressure(x,300,model,vp)
        P2,y2,_,_,_=m.bubble_pressure_gamma_phi(x,300,model,vp,[.98,.99],[.92,.95],[1.02,1.01])
        self.assertAlmostEqual(P1,395,delta=1e-8)
        self.assertAlmostEqual(P2,424.5867,delta=.0002)
        self.assertAlmostEqual(y2[0],.665343,delta=2e-6)
        self.assertAlmostEqual(100*(P1-P2)/P2,-6.97,delta=.02)

    def test_8_C_5_rechaza_composicion_no_fisica(self):
        """Validación añadida: x negativa, suma distinta de uno y valores NaN."""
        m=mod('disoluciones_no_ideales');model=m.ConstantGamma([1.3,.9]);vp=m.DirectPsat([500,250]);
        for x in ([-.1,1.1],[.3,.6],[float('nan'),.6],[float('inf'),.6]):
            with self.subTest(x=x),self.assertRaises(ValueError):
                m.bubble_pressure_gamma_phi(x,300,model,vp,[.98,.99],[.92,.95],[1.02,1.01])

    def test_8_C_5_rechaza_coeficientes_incompletos_y_no_finitos(self):
        """Validación añadida: vectores de longitud incorrecta, inf, NaN y ceros."""
        m=mod('disoluciones_no_ideales');model=m.ConstantGamma([1.3,.9]);vp=m.DirectPsat([500,250]);
        cases=[([.98], [.92,.95],[1.02,1.01]),
               ([float('nan'),.99],[.92,.95],[1.02,1.01]),
               ([.98,float('inf')],[.92,.95],[1.02,1.01]),
               ([.98,.99],[0,.95],[1.02,1.01]),
               ([.98,.99],[.92,.95],[float('inf'),1.01])]
        for phis,phiv,pi in cases:
            with self.subTest(phis=phis,phiv=phiv,pi=pi),self.assertRaises(ValueError):
                m.bubble_pressure_gamma_phi([.4,.6],300,model,vp,phis,phiv,pi)

    def test_8_C_5_rechaza_temperatura_invalidas(self):
        """El modo γ–φ no admite temperaturas no positivas ni no finitas."""
        m=mod('disoluciones_no_ideales');model=m.ConstantGamma([1.3,.9]);vp=m.DirectPsat([500,250])
        for T in (0,-1,float('nan'),float('inf')):
            with self.subTest(T=T),self.assertRaises(ValueError):
                m.bubble_pressure_gamma_phi([.4,.6],T,model,vp,[.98,.99],[.92,.95],[1.02,1.01])

    def test_9_C_1_coexistencia_002(self):
        """9.C.1: epsilon=.0200; fases 2,417104 y 1,582896 kg."""
        m=mod('equilibrio_liquido_liquido');dw,x1,x2=m.beysens(.0200)
        r=m.regla_palanca(4,.480,x1,x2)
        self.assertAlmostEqual(dw,.527447,delta=2e-6)
        self.assertAlmostEqual(r.l1,2.417104,delta=.00003)
        self.assertAlmostEqual(r.l2,1.582896,delta=.00003)
        self.assertAlmostEqual(r.a_l1+r.a_l2,1.92,delta=1e-9)

    def test_9_C_1_coexistencia_0005(self):
        """9.C.1: epsilon=.0050; fases 2,648185 y 1,351815 kg."""
        m=mod('equilibrio_liquido_liquido');dw,x1,x2=m.beysens(.005)
        r=m.regla_palanca(4,.480,x1,x2)
        self.assertAlmostEqual(dw,.339409,delta=2e-6)
        self.assertAlmostEqual(r.l1,2.648185,delta=.00003)
        self.assertAlmostEqual(r.l2,1.351815,delta=.00003)
        self.assertAlmostEqual(r.a_l1+r.a_l2,1.92,delta=1e-9)

    def test_9_C_3_arrastre_vapor_anilina(self):
        """9.C.3: T trifásica 371,52376 K; agua teórica para 250 kg =805,42 kg."""
        m=mod('inmiscibles_y_arrastre_vapor');root=m.temperatura_trifasica(m.AGUA_1,m.ANILINA,1.01325)
        v=m.composicion_vapor(m.AGUA_1,m.ANILINA,root.t,1.01325)
        self.assertAlmostEqual(root.t,371.52376,delta=.00002)
        self.assertAlmostEqual(v['y_b'],.05664492,delta=2e-7)
        self.assertAlmostEqual(v['m_b_a'],.310397,delta=1e-6)
        self.assertAlmostEqual(250/v['m_b_a'],805.42,delta=.02)
        self.assertAlmostEqual(m.ANILINA.ebullicion_puro(1.01325),456.99164,delta=.00005)

    def test_10_C_1_nacl_fundente(self):
        """10.C.1: NaCl puro 157,10 g, comercial 160,30 g; I=2,68817."""
        c=mod('propiedades_coligativas');e=mod('disoluciones_electroliticas')
        m=10/(2*1.86)
        pure=m*58.44
        ions=e.iones_electrolito(m,[('Na+',1,1),('Cl-',-1,1)])
        self.assertAlmostEqual(c.coligativa(1.86,m,2),10,delta=1e-9)
        self.assertAlmostEqual(pure,157.10,delta=.03)
        self.assertAlmostEqual(pure/.98,160.30,delta=.03)
        self.assertAlmostEqual(e.fuerza_ionica(ions),2.68817,delta=1e-5)

    def test_10_C_1_cacl2_fundente(self):
        """10.C.1: CaCl2 puro 198,89 g, comercial 205,04 g; I=5,37634."""
        c=mod('propiedades_coligativas');e=mod('disoluciones_electroliticas')
        m=10/(3*1.86);ions=e.iones_electrolito(m,[('Ca2+',2,1),('Cl-',-1,2)])
        self.assertAlmostEqual(c.coligativa(1.86,m,3),10,delta=1e-9)
        self.assertAlmostEqual(m*110.98,198.89,delta=.02)
        self.assertAlmostEqual(m*110.98/.97,205.04,delta=.02)
        self.assertAlmostEqual(e.fuerza_ionica(ions),5.37634,delta=.0001)

    def test_10_C_3_agua_mar_ideal_limitaciones(self):
        """10.C.3: molalidad principal 1,15696 e I=.72046, sin imponer electroneutralidad."""
        e=mod('disoluciones_electroliticas');c=mod('propiedades_coligativas')
        mol=[.54586,.46906,.05282,.02824,.01028,.01021];charges=[-1,1,2,-2,2,1]
        ions=[e.Ion(n,z,nmol/.965) for n,z,nmol in zip(('Cl','Na','Mg','SO4','Ca','K'),charges,mol)]
        m_total=sum(i.molalidad for i in ions)
        self.assertAlmostEqual(m_total,1.15696,delta=1e-5)
        self.assertAlmostEqual(e.fuerza_ionica(ions),.72046,delta=1e-5)
        self.assertAlmostEqual(c.coligativa(1.86,m_total),2.15195,delta=2e-5)

    def test_11_C_1_mezcla_medio_dmem(self):
        """11.C.1: dos formulaciones de glucosa, 5,14286 y 6,85714 L."""
        m=mod('balances_materia')
        out=m.resolver_lineal(['V1','V2'],[m.Ecuacion([1,1],12,'volumen'),m.Ecuacion([1,4.5],36,'glucosa')])
        self.assertEqual(out.estado,'unico')
        self.assertAlmostEqual(out.valores['V1'],5.14285714,delta=1e-7)
        self.assertAlmostEqual(out.valores['V2'],6.85714286,delta=1e-7)
        self.assertAlmostEqual(out.valores['V1']+4.5*out.valores['V2'],36,delta=1e-9)

    def test_11_C_3_biorreactor_consumo_glucosa(self):
        """11.C.3: caudales de salida cierran el total, glucosa consumida .250 g/h."""
        m=mod('balances_materia');o=m.resolver_lineal(['consumo'],[m.Ecuacion([1],.1*4.5-(.094+.006)*2,'especie')])
        self.assertEqual(o.estado,'unico')
        self.assertAlmostEqual(o.valores['consumo'],.25,delta=1e-12)
        self.assertAlmostEqual(.1-.094-.006,0,delta=1e-12)

    def test_12_C_1_evaporador_kcl(self):
        """12.C.1: evaporador con KCl a 15% ->30%, producto 600 kg/h."""
        s=script('evaporacion',['1200','15','30'])
        self.assertAlmostEqual(salida_valor(s,'Disolución concentrada'),600,delta=1)
        self.assertAlmostEqual(salida_valor(s,'Disolvente evaporado'),600,delta=1)

    def test_12_C_1_cristalizador_kcl(self):
        """12.C.1: sobre 600kg de solución, 75kg cristales, 525kg licor."""
        s=script('cristalizacion',['180.00000','42.857142857','25.000000'])
        # El programa recibe masa de SOLUTO (180 kg), no masa total (600 kg).
        # 30% inicial equivale a 42.8571 g/100g, 20% final a 25 g/100g.
        self.assertAlmostEqual(salida_valor(s,'Cristales obtenidos'),75,delta=.8)
        self.assertAlmostEqual(salida_valor(s,'Licor madre'),525,delta=.8)
        self.assertAlmostEqual(75+525+600,1200,delta=1e-9) # evap 600 + fases

    def test_12_C_3_cristalizacion_filtracion_secado(self):
        """12.C.3: cristalización 27,95876 g; sal recuperada 28,56522 g."""
        s=script('cristalizacion',['120.00000','48.5','37.2'])
        # El programa recibe 120 g de sal; gramos como unidad coherente.
        m=salida_valor(s,'Cristales obtenidos')
        self.assertAlmostEqual(m,27.95876,delta=.1)
        water=120/48.5*100
        kcl_c=120-water*.372
        licor_ret=.080*kcl_c
        w=37.2/137.2
        self.assertAlmostEqual(kcl_c+licor_ret*w,28.56522,delta=.0001)
        self.assertAlmostEqual(100*(kcl_c+licor_ret*w)/120,23.8043,delta=.0001)

    def test_13_C_1_precipitacion_filtro(self):
        """13.C.1: avance 4,4 mol/min, recuperación 4,224 mol/min, Ca cierra."""
        m=mod('balances_materia');o=m.resolver_lineal(['xi','CaCl2_final'],[
            m.Ecuacion([1,0],.88*5,'conversion'),
            m.Ecuacion([1,1],5,'balance')])
        self.assertEqual(o.estado,'unico')
        xi=o.valores['xi']
        self.assertAlmostEqual(xi,4.4,delta=1e-9)
        self.assertAlmostEqual(xi*.96,4.224,delta=1e-9)
        self.assertAlmostEqual(o.valores['CaCl2_final']+xi*.96+xi*.04,5,delta=1e-9)

    def test_13_C_3_oxidacion_dos_rutas(self):
        """13.C.3: dos extensiones, 6,5 y 1,5 mol/min; O2 total 11."""
        m=mod('balances_materia');o=m.resolver_lineal(['xi_acetico','xi_co2'],[
            m.Ecuacion([1,1],8,'etanol desaparecido'),
            m.Ecuacion([0,2],3,'co2 producido')])
        self.assertEqual(o.estado,'unico')
        a,b=o.valores['xi_acetico'],o.valores['xi_co2']
        self.assertAlmostEqual(a,6.5,delta=1e-9)
        self.assertAlmostEqual(b,1.5,delta=1e-9)
        self.assertAlmostEqual(a+3*b,11,delta=1e-9)
        self.assertAlmostEqual(2*2+2*a+2*b,20,delta=1e-9)

    def test_14_C_1_combustible_con_co2_inerte(self):
        """14.C.1: 12 CH4+5 C2H6+3 CO2 inerte, O2 teórico 41,5."""
        m=mod('combustion');fuel=[('CH4',12,True),('C2H6',5,True),('CO2',3,False)]
        o2,prod=m.complete_products_for_mixture(fuel,m.ProductModel())
        self.assertAlmostEqual(o2,41.5,delta=1e-9)
        self.assertAlmostEqual(prod['CO2'],25,delta=1e-9)
        self.assertAlmostEqual(prod['H2O'],39,delta=1e-9)
        gases=dict(prod);gases['N2']=o2*1.25*79/21;gases['O2']=o2*.25
        wet,dry,total,drytotal=m.gas_compositions(gases,4)
        self.assertAlmostEqual(total,269.524,delta=.002)
        self.assertAlmostEqual(dry['CO2']*100,10.8,delta=.1)

    def test_14_C_3_combustion_incompleta_propano(self):
        """14.C.3: 21 CO2+9 CO+40 H2O => 45,5 mol O2, defecto 9%."""
        m=mod('combustion');o2,full=m.oxygen_stoich_formula('C3H8',10,m.ProductModel())
        self.assertAlmostEqual(o2,50,delta=1e-9)
        gas={'CO2':21,'CO':9,'H2O':40,'N2':45.5*79/21}
        wet,dry,_,drytot=m.gas_compositions(gas,4)
        o2_consumed=(2*gas['CO2']+gas['CO']+gas['H2O'])/2
        self.assertAlmostEqual(o2_consumed,45.5,delta=1e-9)
        self.assertAlmostEqual(100*(1-o2_consumed/o2),9,delta=1e-9)
        self.assertAlmostEqual(dry['CO2']*100,10.4,delta=.06)
        self.assertAlmostEqual(dry['CO']*100,4.47,delta=.02)

    def test_14_C_5_biocombustibles_inversion(self):
        """14.C.5: glucosa y ácido palmítico, 0,190476 y 1,428571 mmol."""
        m=mod('combustion')
        for sp,o2,co2 in [('C6H12O6',6,6),('C16H32O2',23,16)]:
            oo,p=m.oxygen_stoich_formula(sp,1,m.ProductModel())
            self.assertAlmostEqual(oo,o2,delta=1e-9)
            self.assertAlmostEqual(p['CO2'],co2,delta=1e-9)
        state,vals=m.solve_linear_system([[6,23],[6,16]],[34,24])
        self.assertEqual(state,'unique')
        self.assertAlmostEqual(vals[0],.19047619,delta=1e-7)
        self.assertAlmostEqual(vals[1],1.42857143,delta=1e-7)
        self.assertAlmostEqual(6*vals[0]+16*vals[1],24,delta=1e-9)

    def test_15_C_1_calentar_humidificar(self):
        """15.C.1: razones de humedad .004855 y .008226; aporte .8426 kg/h."""
        m=mod('psicrometria'); W1=m.humidity_ratio_from_pw(.9*.872,101.3)
        state=m.make_state(101.3,5,W1,sigfigs=5,source_pair=('Tdb','W'))
        t22=m.parse_measurement('22.0');state2=m.state_at_T_constant_W(state,t22)
        state3,dW=m.isothermal_humidification(state2,m.parse_measurement('50.0'))
        self.assertAlmostEqual(W1,.004855,delta=2e-6)
        self.assertAlmostEqual(state2.rh*100,29.7,delta=.03)
        self.assertAlmostEqual(state3.W,.008226,delta=1e-5)
        self.assertAlmostEqual(250*dW,.84264,delta=.003)

    def test_15_C_3_enfriamiento_camara(self):
        """15.C.3: aire 20°C 70% pasa a 4°C saturado; agua condensada ~3.108 kg/h."""
        m=mod('psicrometria');W1=m.humidity_ratio_from_pw(.7*2.338,101.3)
        state=m.make_state(101.3,20,W1,sigfigs=5,source_pair=('Tdb','W'))
        end,dW,dew=m.cooling_with_condensation(state,m.parse_measurement('4.0'))
        self.assertIsNotNone(dew)
        self.assertAlmostEqual(W1,.010212,delta=2e-5)
        self.assertAlmostEqual(end.W,.005031,delta=2e-5)
        self.assertAlmostEqual(600*dW,3.108,delta=.01)
        self.assertAlmostEqual(100*dW/W1,50.7,delta=.3)

    def test_15_C_5_mezcla_adiabatica(self):
        """15.C.5: mezcla 3:1 a partir de estados T,W; contraste tolera h tabulada."""
        m=mod('psicrometria');s1=m.make_state(101.3,24,.0095,sigfigs=5,source_pair=('Tdb','W'))
        s2=m.make_state(101.3,35,.016,sigfigs=5,source_pair=('Tdb','W'))
        mixed,W,h=m.mix_states(s1,m.parse_measurement('300'),s2,m.parse_measurement('100'))
        self.assertIsNotNone(mixed)
        self.assertAlmostEqual(W,.011125,delta=1e-9)
        # Libro usa h1=48,2 y h2=76,3 expresamente; software calcula
        # h por su propia correlación y por eso difiere ~0,1 kJ/kg.
        self.assertAlmostEqual(h,55.225,delta=.15)
        self.assertAlmostEqual(mixed.Tdb,26.72,delta=.15)
        self.assertAlmostEqual(mixed.rh*100,50.9,delta=.5)

if __name__=='__main__':unittest.main()
