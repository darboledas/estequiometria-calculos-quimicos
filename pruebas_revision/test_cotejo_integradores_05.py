# -*- coding: utf-8 -*-
"""Bloque 05: 23 nuevos ejercicios C del libro y solucionario definitivos.

Módulos citados: llamadas reales a funciones del software y cierres analíticos
independientes. Si un módulo no hace la cadena completa, se declara explícitamente
el balance auxiliar. Las tolerancias incluyen redondeos del solucionario.
"""
import contextlib
import io
import math
import re
import unittest
from unittest.mock import patch
from test_auditoria_integral import mod


class CotejoIntegradoresCinco(unittest.TestCase):
    def test_12_C_5_tres_componentes_dos_separaciones(self):
        """12.C.5; separación A/B/C: caudales y cierres por especie."""
        b = mod('balances_materia')
        solution = b.resolver_lineal(['B_rica', 'C_rica'], [
            b.Ecuacion([1, 1], 650, 'total'),
            b.Ecuacion([.05, .9], 243, 'C')])
        self.assertEqual(solution.estado, 'unico')
        fB, fC = solution.valores['B_rica'], solution.valores['C_rica']
        self.assertAlmostEqual(fB, 402.352941176, delta=1e-7)
        self.assertAlmostEqual(fC, 247.647058824, delta=1e-7)
        xA_C = (85 - .17*fB)/fC
        xB_C = (322 - .78*fB)/fC
        self.assertAlmostEqual(xA_C, .06703, delta=.00001)
        self.assertAlmostEqual(xB_C, .03297, delta=.00001)
        for feed, top, recB, recC in [(400,315,.17*fB,xA_C*fC),(350,28,.78*fB,xB_C*fC),(250,7,.05*fB,.9*fC)]:
            self.assertAlmostEqual(b.comprobar_residuos([feed],[top,recB,recC],feed)['residuo'],0,delta=1e-9)

    def test_12_C_6_evaporacion_y_mezcla(self):
        """12.C.6: evaporación a 15%, mezcla final al 7,20%."""
        b=mod('balances_materia')
        solid=500*.06; concentrated=solid/.15; water=500-concentrated
        mixed=concentrated+300; solute=solid+300*.02
        self.assertAlmostEqual(water,300)
        self.assertAlmostEqual(solute/mixed,.072)
        self.assertAlmostEqual(b.comprobar_residuos([500,300],[water,mixed],800)['residuo'],0)

    def test_12_C_7_balance_transitorio_celular(self):
        """12.C.7: 42 nmol al minuto 10 y al 30."""
        b=mod('balances_materia')
        n10=25+(4.5-2.8)*10
        n30=n10+(3.2-3.2)*20
        self.assertAlmostEqual(n10,42)
        self.assertAlmostEqual(n30,42)
        self.assertAlmostEqual(b.comprobar_residuos([25,45],[28,n10],70)['residuo'],0,delta=1e-9)

    def test_12_C_8_evaporador_cristalizador_filtracion(self):
        """12.C.8: base de dos horas y licor retenido en torta."""
        b=mod('balances_materia')
        feed=4000; salt=720; evap=2000
        sol=b.resolver_lineal(['cristales','licor'],[
            b.Ecuacion([1,1],2000,'total'),b.Ecuacion([1,.24],720,'sal')])
        self.assertEqual(sol.estado,'unico')
        c,l=sol.valores['cristales'],sol.valores['licor']
        retained=.1*c; cake=c+retained; filtrate=l-retained
        saltcake=c+.24*retained
        self.assertAlmostEqual(c,315.789473684,delta=1e-7)
        self.assertAlmostEqual(cake,347.36842105,delta=1e-6)
        self.assertAlmostEqual(saltcake/720, .449, delta=.001)
        self.assertAlmostEqual(b.comprobar_residuos([feed],[evap,cake,filtrate],feed)['residuo'],0,delta=1e-9)
        self.assertAlmostEqual(saltcake+.24*filtrate,salt,delta=1e-9)

    def test_13_C_4_descomposicion_carbonato(self):
        """13.C.4: cantidad gas, riqueza 65,5% y masa residual 18,5g."""
        g=mod('gases_ideales_y_mezclas');mm=mod('masa_molar')
        n=g.solve_ideal(101325,.00360,None,298)['n']
        mass=n/.9*float(mm.calculate_molar_mass('CaCO3').raw_mass)
        residue=25-n*float(mm.calculate_molar_mass('CO2').raw_mass)
        self.assertAlmostEqual(n,.1472,delta=.0002)
        self.assertAlmostEqual(mass/25*100,65.5,delta=.15)
        self.assertAlmostEqual(residue,18.5,delta=.1)

    def test_13_C_5_conversion_y_recuperacion_no_iguales(self):
        """13.C.5: 70% conversión, 85% recuperación física, 59,5% global."""
        r=mod('conversion_rendimiento_selectividad')
        feed=3;reacted=.70*feed;remaining=feed-reacted;recovered=.85*reacted
        self.assertAlmostEqual(float(r.fraccion_conversion(r.Q(3),r.Q(remaining)).v),.70)
        self.assertAlmostEqual(recovered,1.785)
        self.assertAlmostEqual(recovered/feed,.595)

    def test_13_C_6_fermentacion_glucosa_carbono(self):
        """13.C.6: 1,20 mol reaccionados; 2,4 mol etanol y CO2."""
        m=mod('reactivo_limitante')
        cap,lim,xi,adv,left,prod=m.balance([m.Q(1.2)],[1],[2,2])
        self.assertAlmostEqual(float(prod[0].v),2.4)
        self.assertAlmostEqual(float(prod[1].v),2.4)
        self.assertAlmostEqual((2.1/float(prod[0].v))*100,87.5)
        self.assertAlmostEqual(6*1.5,6*.3+2*float(prod[0].v)+float(prod[1].v))

    def test_13_C_7_balance_carbono_biomasa(self):
        """13.C.7: balance elemental global del cultivo."""
        b=mod('balances_materia')
        biomass=6-2.2-1.1
        self.assertAlmostEqual(biomass,2.7)
        self.assertAlmostEqual(b.comprobar_residuos([6],[2.2,1.1,biomass],6)['residuo'],0)
        self.assertAlmostEqual(biomass/6,.45)

    def test_13_C_8_etilenglicol_fraccion_co2(self):
        """13.C.8: HCOOH=0,820 mol/h, fracción C a CO2=57,3%."""
        b=mod('balances_materia')
        leftover=1.20*(1-.8);converted=1.20-leftover
        acid=2*converted-1.10
        self.assertAlmostEqual(acid,.82)
        self.assertAlmostEqual(1.10/(2*converted)*100,57.2916667,delta=1e-6)
        self.assertAlmostEqual(b.comprobar_residuos([2*1.2],[2*leftover,1.1,acid],2*1.2)['residuo'],0,delta=1e-12)

    def test_13_C_9_dos_extensiones_no_no2_n2o4(self):
        """13.C.9: ξ1=0,8 y ξ2=0,5; oxígeno consumido 0,8."""
        b=mod('balances_materia')
        sol=b.resolver_lineal(['xi1','xi2'],[
            b.Ecuacion([2,0],1.6,'NO'),b.Ecuacion([2,-2],.6,'NO2')])
        self.assertEqual(sol.estado,'unico')
        self.assertAlmostEqual(sol.valores['xi1'],.8)
        self.assertAlmostEqual(sol.valores['xi2'],.5)
        self.assertAlmostEqual(2, .4+.6+2*sol.valores['xi2'],delta=1e-10)

    def test_13_C_10_precipitado_baso4_y_filtro(self):
        """13.C.10: BaSO4 formado 6 mol/min, recuperado 5,4 mol/min."""
        b=mod('balances_materia')
        converted=.75*8;recovered=.90*converted
        self.assertAlmostEqual(converted,6)
        self.assertAlmostEqual(recovered,5.4)
        self.assertAlmostEqual(b.comprobar_residuos([8],[8-converted,recovered,converted-recovered],8)['residuo'],0)
        self.assertAlmostEqual(b.comprobar_residuos([10],[10-converted,recovered,converted-recovered],10)['residuo'],0)

    def test_14_C_4_inversion_ch4_c2h6_orSAT(self):
        """14.C.4: 59,1/40,9 mol%, agua 17,5; exceso 20,0%."""
        c=mod('combustion')
        o2_in=85.93*(21/79);consumed=o2_in-3.81
        status,ans=c.solve_linear_system([[1,2],[2,3.5]],[10.26,consumed])
        self.assertEqual(status,'unique')
        a,b=ans
        self.assertAlmostEqual(a/(a+b),.591,delta=.001)
        self.assertAlmostEqual(2*a+3*b,17.5443,delta=.004)
        self.assertAlmostEqual((o2_in/consumed-1)*100,20,delta=.05)

    def test_14_C_6_combustible_con_co_y_n2_inerte(self):
        """14.C.6: CH4/CO/N2=23,2/11,6/65,3%; aire 28,1% exceso."""
        c=mod('combustion')
        n_ch4=9.50/1.5; n_co=.5*n_ch4
        oxygen=2*n_ch4+.5*n_co; supplied=oxygen+4
        n_n2fuel=86.5-supplied*(79/21)
        self.assertAlmostEqual(n_n2fuel,17.84524,delta=.003)
        xs=[n_ch4/n for n in [n_ch4+n_co+n_n2fuel]]
        self.assertAlmostEqual(xs[0],.2316,delta=.0003)
        self.assertAlmostEqual((supplied/oxygen-1)*100,28.1,delta=.05)
        for formula,n in [('CH4',n_ch4),('CO',n_co)]:
            o2, _=c.oxygen_stoich_formula(formula,n,c.ProductModel())
            self.assertAlmostEqual(o2,(2 if formula=='CH4' else .5)*n,delta=1e-9)

    def test_14_C_7_respirometria_glucosa(self):
        """14.C.7: oxidación de 2,50 mmol glucosa y 40,0% O2 residual."""
        c=mod('combustion'); mm=mod('masa_molar')
        quantity=.015/6
        o2, products=c.oxygen_stoich_formula('C6H12O6',quantity,c.ProductModel())
        self.assertAlmostEqual(o2,.015)
        self.assertAlmostEqual(products['CO2'],.015)
        self.assertAlmostEqual(quantity*float(mm.calculate_molar_mass('C6H12O6').raw_mass),.4504,delta=.001)
        self.assertAlmostEqual((.025-o2)/.025,.40)

    def test_14_C_8_hc_por_analisis_seco_incompleto(self):
        """14.C.8: gases con CO y O2, H/C=2,90; 108 mol aire."""
        c=mod('combustion')
        dry={'CO2':10,'CO':1.5,'O2':3.5,'N2':85}
        o2=85*21/79;h2o=2*(o2-3.5)-2*10-1.5
        self.assertAlmostEqual(h2o,16.6899,delta=.0002)
        self.assertAlmostEqual(2*h2o/(10+1.5),2.90,delta=.005)
        self.assertAlmostEqual(o2/.21,107.6,delta=.1)
        self.assertAlmostEqual(sum(dry.values()),100)
        self.assertTrue(c.balance_ok(2*o2,2*dry['O2']+2*dry['CO2']+dry['CO']+h2o))

    def test_14_C_9_composicion_ch4_propano_inversa(self):
        """14.C.9: x(C3H8)=0,65605 con 11,0% CO2 seco."""
        c=mod('combustion')
        coeff=.2+(79/21)*1.2;y=.110
        status,sol=c.solve_linear_system([[2-y*(2+3*coeff)]],[y*(1+2*coeff)-1])
        self.assertEqual(status,'unique')
        x=sol[0]
        self.assertAlmostEqual(x,.65605,delta=.0001)
        o2=2+3*x; co2=1+2*x; ox=.2*o2;n2=(79/21)*1.2*o2
        self.assertAlmostEqual(co2/(co2+ox+n2),.110,delta=1e-12)
        self.assertAlmostEqual(ox/(co2+ox+n2)*100,3.78,delta=.02)

    def test_14_C_10_sustrato_c4h8o2(self):
        """14.C.10: C4H8O2 + 5 O2 -> 4 CO2 + 4 H2O."""
        c=mod('combustion')
        sto,prod=c.oxygen_stoich_formula('C4H8O2',.001,c.ProductModel())
        self.assertAlmostEqual(sto,.005,delta=1e-12)
        self.assertAlmostEqual(prod['CO2'],.004,delta=1e-12)
        self.assertAlmostEqual(prod['H2O'],.004,delta=1e-12)
        self.assertTrue(all(c.balance_ok(a,b) for a,b,_ in c.balance_residuals({'C4H8O2':.001,'O2':sto},prod).values()))

    def test_15_C_4_humidificacion_adiabatica_invernadero(self):
        """15.C.4: W1=0,00889, h=54,9, W2=0,0125, RH2≈71%."""
        p=mod('psicrometria'); P=101.3
        w1=p.humidity_ratio_from_pw(.30*4.758,P)
        h=p.moist_air_enthalpy(32,w1)
        w2=(h-1.005*23)/(2500+1.88*23)
        rh=p.pw_from_humidity_ratio(w2,P)/2.811
        self.assertAlmostEqual(w1,.008888,delta=.00001)
        # El libro utiliza cp_da=1,005, cp_v=1,88 y hfg=2500; el programa
        # mantiene constantes ASHRAE próximas, no idénticas.
        h_libro=1.005*32+w1*(2500+1.88*32)
        self.assertAlmostEqual(h_libro,54.91,delta=.01)
        self.assertAlmostEqual(h,54.91,delta=.08)
        self.assertAlmostEqual(w2,.01250,delta=.00002)
        self.assertAlmostEqual(rh*100,71.0,delta=.2)

    def test_15_C_6_enfriamiento_recalentamiento(self):
        """15.C.6: W inicial≈0,02018, condensado≈0,01144, RH final≈53%."""
        p=mod('psicrometria');P=101.3
        w1=p.humidity_ratio_from_pw(.75*4.245,P)
        w2=p.humidity_ratio_from_pw(1.403,P)
        self.assertAlmostEqual(w1,.02018,delta=.00003)
        self.assertAlmostEqual(w2,.008734,delta=.00001)
        self.assertAlmostEqual(w1-w2,.01144,delta=.00003)
        self.assertAlmostEqual(p.pw_from_humidity_ratio(w2,P)/2.645*100,53.0,delta=.1)

    def test_15_C_7_camara_fermentacion_dos_etapas(self):
        """15.C.7: 1,89 kg/h de agua; 11,4 kg en 6h."""
        p=mod('psicrometria');P=101.3
        w1=p.humidity_ratio_from_pw(.4*2.338,P)
        w3=p.humidity_ratio_from_pw(.8*4.245,P)
        rate=120*(w3-w1)
        self.assertAlmostEqual(w1,.005794,delta=.00001)
        self.assertAlmostEqual(w3,.02157,delta=.00004)
        self.assertAlmostEqual(rate,1.893,delta=.01)
        self.assertAlmostEqual(rate*6,11.36,delta=.06)

    def test_15_C_8_condensacion_invernadero(self):
        """15.C.8: W condensada≈0,002256 kg/kg."""
        p=mod('psicrometria');P=100
        pv1=.85*2.064;ws=p.humidity_ratio_from_pw(1.403,P)
        w1=p.humidity_ratio_from_pw(pv1,P)
        self.assertGreater(pv1,1.403)
        self.assertAlmostEqual(w1-ws,.002256,delta=.00001)

    def test_15_C_9_secadero_infusiones(self):
        """15.C.9: 1,629 kg/h, 4,073 kg en 2,5h, cap. 1,35kg/h."""
        p=mod('psicrometria');P=101.3
        w1=p.humidity_ratio_from_pw(.20*7.382,P)
        w2=p.humidity_ratio_from_pw(.65*7.382,P)
        ws=p.humidity_ratio_from_pw(7.382,P)
        self.assertAlmostEqual(75*(w2-w1),1.6292,delta=.008)
        self.assertAlmostEqual(75*(w2-w1)*2.5,4.073,delta=.03)
        self.assertAlmostEqual(75*(ws-w2),1.35,delta=.01)

    def test_15_C_10_etanol_n2_interfaz_general(self):
        """15.C.10: interfaz gas-vapor general y 0,0866 kg EtOH/kg N2."""
        p=mod('psicrometria')
        inputs=['28.01','46.07','100.0','30.0','1','10.5','4','5.00']
        buf=io.StringIO()
        with patch('builtins.input',side_effect=inputs),contextlib.redirect_stdout(buf):
            p.mode_12_general_gas_vapor()
        output=buf.getvalue()
        match=re.search(r'omega\s*=\s*([0-9]+(?:,[0-9]+)?)',output)
        self.assertIsNotNone(match,output)
        self.assertAlmostEqual(float(match.group(1).replace(',','.')),.08657,delta=.0001)
        ratio=46.07/28.01
        w2=ratio*3.12/(100-3.12)
        self.assertAlmostEqual(w2,.05297,delta=.0001)
        self.assertAlmostEqual(ratio*5/95-w2,.03360,delta=.0001)

    def test_15_antoine_rechaza_nan_inf_directo(self):
        """La correlación opcional no permite presiones NaN/Inf."""
        p=mod('psicrometria')
        for params in [(20,float('nan'),1500,230),(20,7,float('nan'),230),
                       (20,7,1500,float('inf')),(float('inf'),7,1500,230)]:
            with self.subTest(params=params),self.assertRaises(p.PsychrometricError):
                p.antoine_psat_kpa(*params)

    def test_15_antoine_rechaza_desbordamiento_y_singularidad(self):
        """Coeficientes de Antoine extremos producen fallo controlado."""
        p=mod('psicrometria')
        with self.assertRaises(p.PsychrometricError):p.antoine_psat_kpa(20,400,0,230)
        with self.assertRaises(p.PsychrometricError):p.antoine_psat_kpa(20,7,1200,-20)
        with self.assertRaises(p.PsychrometricError):p.antoine_psat_kpa(20,-500,0,230)

    def test_15_antoine_convencion_kelvin_frente_a_celsius(self):
        """Antoine, capítulo 6 en K vs módulo gas-vapor general en °C."""
        p=mod('psicrometria');v=mod('presion_vapor')
        data=v.ANTOINE['n-heptano']
        T_K=350.0
        p_ref=v.antoine_pressure_kpa(T_K,data)
        p_celsius=p.antoine_psat_kpa(T_K-273.15,data.A,data.B,data.C+273.15)
        self.assertAlmostEqual(p_ref,p_celsius,delta=1e-10)
        # Copiar literalmente C=-56,510 sin convertir de K a °C sería incorrecto.
        p_wrong=p.antoine_psat_kpa(T_K-273.15,data.A,data.B,data.C)
        self.assertGreater(abs(p_wrong/p_ref-1),.05)

    def test_15_antoine_interfaz_rechaza_coeficiente_nan(self):
        """Entrada de coeficiente NaN se rechaza antes de calcular estado."""
        p=mod('psicrometria')
        inputs=['28.01','46.07','100','30','2','nan','200','230']
        with patch('builtins.input',side_effect=inputs),self.assertRaises(p.PsychrometricError):
            with contextlib.redirect_stdout(io.StringIO()):p.mode_12_general_gas_vapor()

if __name__=='__main__': unittest.main()
