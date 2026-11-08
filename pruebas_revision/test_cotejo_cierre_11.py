# -*- coding: utf-8 -*-
"""Cotejo XI: problemas inéditos del libro definitivo y el solucionario de 220 pp.

Las pruebas verifican magnitudes independientes y, cuando existe, una función de
las aplicaciones. No se confunden los cálculos auxiliares con funciones nativas.
"""
import math
import unittest
from fractions import Fraction
from test_auditoria_integral import mod


class CotejoBloqueXI(unittest.TestCase):
    def cmp(self, observed, reference, tol=1e-7):
        self.assertTrue(math.isfinite(float(observed)), f'Resultado no finito {observed}')
        self.assertAlmostEqual(float(observed), reference, delta=tol)

    # Capítulo 2: dimensiones y propagación de incertidumbre
    def test_2_B_7_homogeneidad_energia(self):
        m=mod('unidades_y_dimensiones')
        r=m.combinar_dimensiones([[1,0,0,0,0,0,0],[0,1,-1,0,0,0,0]], [1,2])
        self.assertEqual(list(map(int,r)),[1,2,-2,0,0,0,0])

    def test_2_B_8_dimensiones_velocidad_sonido(self):
        m=mod('unidades_y_dimensiones')
        # Base (M,L,T): P=(1,-1,-2); rho=(1,-3,0).
        r=m.combinar_dimensiones([[1,-1,-2,0,0,0,0],[1,-3,0,0,0,0,0]],[Fraction(1,2),Fraction(-1,2)])
        self.assertEqual(r,[0,1,-1,0,0,0,0])

    def test_2_B_9_cifras_significativas(self):
        m=mod('unidades_y_dimensiones')
        for s,n in [('0,00450',3),('120,0',4),('3,020e5',4)]:
            self.assertEqual(m.cifras_significativas_texto(s),n)
        with self.assertRaises(ValueError):m.cifras_significativas_texto('1500')

    def test_2_B_10_propagar_uncertumbre_AB_sobre_C(self):
        m=mod('unidades_y_dimensiones');a,b,c=12,3.5,1.8
        res=a*b/c
        u,_,_=m.propagar_incertidumbre_estandar([b/c,a/c,-a*b/c**2],[.2,.05,.03])
        self.cmp(res,23.3333333333,1e-8);self.cmp(u,.6431,.001)

    def test_2_B_11_incertidumbre_carga(self):
        m=mod('unidades_y_dimensiones')
        u,_,_=m.propagar_incertidumbre_estandar([120,.15],[.01,1.])
        self.cmp(.15*120,18);self.cmp(u,1.2093,.0001)

    def test_2_B_12_incertidumbre_relativa(self):
        m=mod('unidades_y_dimensiones');r,p=m.incertidumbre_relativa(12.50,.02)
        self.cmp(r,.0016);self.cmp(p,.16)

    def test_2_C_2_grupos_adimensionales(self):
        m=mod('unidades_y_dimensiones')
        # Re = rho*v*D/mu; C_D=F/(rho*v^2*D^2)
        rho=(1,-3,0,0,0,0,0);v=(0,1,-1,0,0,0,0);D=(0,1,0,0,0,0,0);mu=(1,-1,-1,0,0,0,0);force=(1,1,-2,0,0,0,0)
        re=m.combinar_dimensiones([rho,v,D,mu],[1,1,1,-1])
        cd=m.combinar_dimensiones([force,rho,v,D],[1,-1,-2,-2])
        self.assertTrue(m.es_adimensional(re));self.assertTrue(m.es_adimensional(cd))

    # Capítulo 3: composiciones y estequiometría
    def test_3_B_7_masa_por_densidad(self):
        self.cmp(200.0*1.25,250.0)

    def test_3_B_8_fraccion_masica_etanol(self):
        m=mod('gases_ideales_y_mezclas')
        values=m.mixture_from_basis([('C2H6O',m.parse_num('15.0')),('H2O',m.parse_num('85.0'))],'masa',{'C2H6O':46.07})
        self.cmp(values[0]['w'],.15,1e-12);self.cmp(sum(v['w'] for v in values),1)

    def test_3_B_9_fracciones_molares_O2_N2(self):
        m=mod('gases_ideales_y_mezclas')
        values=m.mixture_from_basis([('O2',m.parse_num('2.1')),('N2',m.parse_num('6.3'))],'molar')
        self.cmp(values[0]['y'],.25);self.cmp(values[1]['y'],.75)

    def test_3_B_10_equivalente_H2SO4(self):
        m=mod('masa_molar');M=float(m.calculate_molar_mass('H2SO4').raw_mass)
        self.cmp(M/2,49.04,.015)

    def test_3_B_17_ajuste_yoduro_plomo(self):
        m=mod('ajuste_ecuaciones')
        self.assertEqual(m.ajustar(['Pb(NO3)2','KI'],['PbI2','KNO3']),[1,2,1,2])

    def test_3_B_18_urea_disolucion(self):
        m=mod('masa_molar');M=float(m.calculate_molar_mass('CO(NH2)2').raw_mass)
        n=15/M;self.cmp(15/100,.15);self.cmp(n/.085,2.94,.003)
        self.cmp(100/1.05,95.2,.04);self.cmp(n/(.1/1.05),2.62,.006)

    def test_3_B_19_permanganato_normalidad(self):
        m=mod('masa_molar');M=float(m.calculate_molar_mass('KMnO4').raw_mass)
        c=7.90/M;self.cmp(c,.0500,5e-5)
        self.cmp(M/5,31.6,.04);self.cmp(c*5,.250,.0001)

    # Capítulo 11: mezclas y diagnóstico de balances
    def test_11_B_13_dilucion(self):
        m=mod('balances_materia');f1=300*.08/.20;f2=300-f1
        self.cmp(f1,120);self.cmp(f2,180)
        a=m.comprobar_residuos([f1*.2],[300*.08],300)
        self.cmp(a['residuo'],0)

    def test_11_B_14_balance_residual(self):
        m=mod('balances_materia');r=m.comprobar_residuos([90,135,75],[297],300)
        self.cmp(r['residuo'],3);self.cmp(100*r['residuo']/300,1)

    def test_11_B_15_mezcla_dos_corrientes(self):
        m=mod('balances_materia');f2=120*(.32-.20)/(.50-.32);out=120+f2
        self.cmp(f2,80);self.cmp(out,200)
        x=m.comprobar_residuos([120*.2,f2*.5],[out*.32],out)
        self.cmp(x['residuo'],0)

    def test_11_B_16_cancelacion_residuos(self):
        m=mod('balances_materia')
        r=m.comprobar_residuos([250],[250],250)
        a=m.comprobar_residuos([250*.36],[250*.35],250)
        b=m.comprobar_residuos([250*.64],[250*.65],250)
        self.cmp(r['residuo'],0);self.cmp(a['residuo'],2.5);self.cmp(b['residuo'],-2.5)
        self.cmp(a['residuo']+b['residuo'],0)

    # Capítulo 12: reparto y acumulación
    def test_12_B_12_extraccion_dos_contactos(self):
        m=mod('extraccion_liquido_liquido')
        one=m.fraccion_restante(m.exacto(100),m.exacto(50),m.exacto(5))
        two=m.fraccion_restante(m.exacto(100),m.exacto(25),m.exacto(5))
        q1=10*(1-float(one.valor));q2=10*(1-float(two.valor)**2)
        self.cmp(q1,7.142857,1e-6);self.cmp(q2,8.02469,.00005)
        self.assertGreater(q2,q1)

    def test_12_B_13_acumulacion_membrana(self):
        m=mod('balances_materia')
        records=m.inventario_lineal(12,[(.800,0)],[(.350,0)],30,2)
        self.cmp(.800-.350,.450)
        self.cmp(records[-1]['inventario'],25.5)

    # Capítulo 13: balances elementales y extensiones
    def test_13_B_6_NH4NO3_nitrogeno(self):
        n_NH3=2*2.5-2*.600-2*1.2
        self.cmp(n_NH3,1.4)
        self.cmp(2*.6+2*1.2+n_NH3,5)

    def test_13_B_9_dos_reacciones_etanol(self):
        m=mod('balance_varias_reacciones')
        # consume 1 mol EtOH por ξ1 y 2 mol por ξ2; forma agua 1 por ξ1 y ξ2.
        consume=1.5+2*.8;water=1.5+.8
        self.cmp(consume,3.10);self.cmp(water,2.30)

    def test_13_B_10_recuperacion_filtrado(self):
        rec=4.5*.92;rest=4.5-rec
        self.cmp(rec,4.14);self.cmp(rest,.36)
        self.cmp(rec+rest,4.5)

    def test_13_B_11_extension_unica(self):
        xi_a=(10.-4.)/2;xi_b=8.-5.;xi_c=9./3
        self.cmp(xi_a,3);self.cmp(xi_b,xi_a);self.cmp(xi_c,xi_a)

    def test_13_B_12_carbono_salida(self):
        n=(8.-2.-1.5)/2
        self.cmp(n,2.25);self.cmp(2+1.5+2*n,8)

    def test_13_B_13_enzimatico_penicilina(self):
        feed=1.2+.25*20;xi=feed-.4
        self.cmp(feed,6.2);self.cmp(xi,5.8)
        self.cmp(100*xi/feed,93.548387,.0001)
        self.cmp(xi/20,.290);self.cmp(.4+xi,feed)

    # Capítulo 14: combustión
    def test_14_B_9_combustible_CHO(self):
        oxygen=80/12.011 +14/(4*1.008) -6/(2*15.999)
        self.cmp(oxygen,9.9453,.0002);self.cmp(oxygen/.21,47.4,.07)

    def test_14_B_10_azufre_e_inertes(self):
        o=72/12.011 +5/(4*1.008)-8/(2*15.999)+2/32.06
        self.cmp(o,7.04695,.0002)
        self.cmp(72/12.011,5.9945,.0002)
        self.cmp(5/(2*1.008),2.4802,.0002)
        self.cmp(2/32.06,.06238,.00002)

    def test_14_B_12_etano_conversion(self):
        m=mod('combustion');product=m.complete_products_for_formula('C2H6',10.2,m.ProductModel())
        self.cmp(10.2/12,.85);self.cmp(12-10.2,1.8)
        self.cmp(product['CO2'],20.4);self.cmp(product['H2O'],30.6)

    def test_14_B_14_base_humeda_seca(self):
        m=mod('combustion');wet,dry,_,total=m.gas_compositions({'CO2':8.5,'H2O':12,'O2':3.5,'N2':76},4)
        self.cmp(total,88)
        self.cmp(dry['CO2'],8.5/88,.000001)
        self.cmp(dry['O2'],3.5/88,.000001)
        self.cmp(dry['N2'],76/88,.000001)

    def test_14_B_15_inverso_hc_gas_seco(self):
        incoming=85*21/79;water=2*incoming-2*12-2*3
        self.cmp(water,15.18987,.0001)
        self.cmp(2*water/12,2.53165,.0001)

    # Capítulo 15: psicrometría y gas-vapor
    def test_15_B_6_rocio_tabla(self):
        m=mod('psicrometria')
        self.cmp(m.temperature_from_saturation_pressure(1.705),15.,.12)

    def test_15_B_10_humidificacion_balance_agua(self):
        self.cmp(180*.00450,.810)
        self.cmp(180*.0110,1.98)
        self.cmp(180*(.0110-.00450),1.17)

    def test_15_B_11_mezcla_vapores(self):
        vap=80*.006+120*.015
        self.cmp(vap,2.28);self.cmp(vap/200,.0114)

    def test_15_B_12_entallpia_mezcla(self):
        self.cmp((100*35+50*70)/150,46.66667,.00001)

    def test_15_B_13_entalpia_constantes_libro(self):
        m=mod('psicrometria');ref=1.005*28+.012*(2500+1.88*28)
        self.cmp(ref,58.77168,.00001)
        # Variante del programa con constantes ligeramente distintas, ya documentadas.
        self.cmp(m.moist_air_enthalpy(28,.012),ref,.06)

    def test_15_B_14_volumen_aire_humedo(self):
        m=mod('psicrometria');val=.287*305.15/95*(1+1.6078*.016)
        self.cmp(val,.94559,.00005);self.cmp(m.moist_air_specific_volume(32,.016,95),val,.001)

    def test_15_B_15_carta_30C_50RH(self):
        m=mod('psicrometria');pw=.5*4.245
        W=m.humidity_ratio_from_pw(pw,101.325)
        self.cmp(W,.01330,.00005)
        self.cmp(m.moist_air_enthalpy(30,W),64.2,.2)

    def test_15_B_16_carta_30C_20Twb(self):
        m=mod('psicrometria')
        # Los valores gráficos son aproximados; no es validación de la lectura de carta.
        self.cmp(m.moist_air_enthalpy(30,.0105),57.,.6)

    def test_15_B_17_nitrogeno_etanol(self):
        y=3/100;rh=3/7.87*100;Y=y/(1-y);omega=Y*46.07/28.01
        self.cmp(y,.03);self.cmp(rh,38.1,.03)
        self.cmp(Y,.0309278,.000001);self.cmp(omega,.050869,.00001)

    def test_15_B_18_nitrogeno_acetona(self):
        p=.15*95
        self.cmp(p,14.25);self.assertLess(p,24.7)
        self.cmp(p/24.7*100,57.7,.02)
        self.cmp(.15/.85,.17647,.00001)
        self.cmp(24.7/95,.260,.00001)

    def test_15_B_19_condensacion(self):
        cond=350*(.014-.0085)
        self.cmp(cond,1.925);self.cmp(100*cond/(350*.014),39.2857,.0001)


class CotejoAplicadosTresCuatro(unittest.TestCase):
    def cmp(self, value, reference, tolerance=1e-6):
        self.assertTrue(math.isfinite(float(value)))
        self.assertAlmostEqual(float(value),reference,delta=tolerance)

    def test_3_C_8_reduccion_hematita(self):
        m=mod('ajuste_ecuaciones')
        self.assertEqual(m.ajustar(['Fe2O3','CO'],['Fe','CO2']),[1,3,2,3])
        self.cmp(500*.7/159.69*2*55.845,244.8,.1)
        self.cmp(500*.7/159.69*3*44.01,289.4,.1)

    def test_3_C_9_hidroxido_sulfato(self):
        m=mod('ajuste_ecuaciones')
        self.assertEqual(m.ajustar(['NaOH','H2SO4'],['Na2SO4','H2O']),[2,1,1,2])
        self.cmp(250*.8/39.997/2*98.079,245.2,.1)
        self.cmp(250*.8/39.997/2*142.04,355.1,.1)

    def test_3_C_10_densidad_API(self):
        m=mod('densidades_y_escalas')
        ge=.820/.999
        self.cmp(ge,.820821,.000001)
        got=m.desde_ge('7',m.Q(str(ge)))
        self.cmp(got.v,40.888,.001)

    def test_3_C_11_grados_Baume(self):
        m=mod('densidades_y_escalas')
        ge=m.a_ge('3',m.Q('30.0'))
        self.cmp(ge.v,145/(145-30))
        self.cmp(float(ge.v)*.999,1.25961,.00001)

    def test_3_C_12_etanol_agua(self):
        m=mod('gases_ideales_y_mezclas')
        rows=m.mixture_from_basis([('C2H6O',m.parse_num('78900')),('H2O',m.parse_num('150000'))],
                                 'masa',{'C2H6O':46.07})
        self.cmp(rows[0]['w'],.34469,.00002)
        self.cmp(rows[0]['y'],.17060,.00003)
        self.cmp(sum(r['y'] for r in rows),1)

    def test_3_C_13_fosforo_horno_y_escoria(self):
        m=mod('ajuste_ecuaciones')
        self.assertEqual(m.ajustar(['Ca3(PO4)2','C','SiO2'],['P4','CaSiO3','CO']),
                         [2,10,6,1,6,10])
        n=100/310.174;xi=.95*n
        C_in=n*5*12.011*1.25;Si_in=n*3*60.0843*1.5
        product=.5*xi*123.896
        slag_phosphate=100*(1-.95)
        slag_C=n*5*(1.25-.95)*12.011
        slag_Si=n*3*(1.5-.95)*60.0843
        slag_silicate=xi*3*(40.078+28.0855+3*15.999)
        self.cmp(C_in,24.20,.03);self.cmp(Si_in,87.17,.05)
        self.cmp(product,18.97,.02)
        self.cmp(slag_phosphate,5)
        self.cmp(slag_C,5.81,.02);self.cmp(slag_Si,31.96,.03)
        self.cmp(slag_phosphate+slag_C+slag_Si+slag_silicate,149.5,1)

    def test_3_C_14_selectividad_etileno(self):
        xi1=.70;xi2=.20/2
        self.cmp((xi1+xi2)/1.0,.80)
        self.cmp(xi1/1.,.70)
        self.cmp(xi1/xi2,7)

    def test_3_C_15_fosgeno_inerte(self):
        m=mod('gases_ideales_y_mezclas');xi=6-2
        x=[10-xi,6-xi,xi,4]
        r=m.mixture_from_basis([(s,m.parse_num(str(n))) for s,n in zip(['CO','Cl2','COCl2','N2'],x)],'molar',
                               {m._ascii_key(z):M for z,M in [('CO',28.01),('Cl2',70.90),('COCl2',98.91),('N2',28.014)]})
        self.cmp(xi,4);self.cmp(xi/6,.6666667,1e-7)
        for got,ref in zip(r,[.375,.125,.25,.25]): self.cmp(got['y'],ref)

    def test_3_C_16_efervescente_acido_limitante(self):
        m=mod('ajuste_ecuaciones');self.assertEqual(m.ajustar(['NaHCO3','C6H8O7'],['Na3C6H5O7','CO2','H2O']),[3,1,1,3,3])
        bicarbonate=1.5*.96/84.01;acid=1./192.12
        self.assertGreater(bicarbonate,3*acid)
        vol=3*acid*8.314*298.15/100
        self.cmp(vol,.3871,.0002);self.cmp(100*.330/vol,85.25,.1)

    def test_3_C_17_sulfato_agua_precipitacion(self):
        n=.466/233.39
        self.cmp(n,.00199666,.00000001)
        self.cmp(n*96.06*1000/.5,383.6,.1)
        self.cmp(.025*.1-n,.00050334,.00000002)
        self.cmp(1*.1*208.23,20.823)

    def test_3_C_18_aspirina_pureza_y_recuperacion(self):
        n_sal=5*.98/138.12;n_anh=7*1.08*.95/102.09
        self.assertLess(n_sal,n_anh)
        self.cmp(100*(n_anh/n_sal-1),98.3,.1)
        formed=n_sal*.92*180.16
        recovered=5.20*.97
        self.cmp(formed,5.880,.01);self.cmp(recovered,5.044)
        self.cmp(100*recovered/(n_sal*180.16),78.92,.1)
        self.cmp(100*recovered/formed,85.78,.1)

    def test_3_C_19_fermentacion_etanol(self):
        m=mod('ajuste_ecuaciones')
        self.assertEqual(m.ajustar(['C6H12O6'],['C2H6O','CO2']),[1,2,2])
        mass_feed=1000*.18;mass_remaining=mass_feed*(1-.92)
        mass_route=mass_feed*.92*.95;n=mass_route/180.16
        etoh=2*n*46.07;co2=2*n*44.01
        self.cmp(mass_remaining,14.4);self.cmp(mass_route,157.32)
        self.cmp(etoh,80.459,.01);self.cmp(co2,76.861,.02)
        self.cmp(etoh*.88,70.804,.02);self.cmp(.92*.95*.88, .76912)

    def test_3_C_20_Baume_Brix_correlacion_extrapolada(self):
        m=mod('densidades_y_escalas');ge=float(m.a_ge('3',m.Q('20')).v)
        b=182.4601*ge**3-775.6821*ge**2+1262.7794*ge-669.5622
        mass=800*ge*.9982;sucrose0=mass*b/100
        mass_sucrose=sucrose0+180*.995
        final_mass=mass_sucrose/.65
        water=(mass-sucrose0)+180*.005
        ev=water-(final_mass-mass_sucrose)
        vol=final_mass/1.3163
        be_final=145-145/(1.3163/.9982)
        self.cmp(b,36.3053,.0001)
        self.cmp(mass,926.3296,.0001)
        self.cmp(mass_sucrose,515.4068,.0005)
        self.cmp(ev,313.396,.001)
        self.cmp(vol,602.3958,.002)
        self.cmp(be_final,35.041,.01)
        # Correlación directa fuera del rango seguro del ajuste inverso Hall: orientativo.
        with self.assertRaises(ValueError):m.brix_a_ge_hall(m.Q(str(b)))

    def test_3_C_21_biorreactor_CH0(self):
        n0=5*4.5/180.16;consumed=5*(4.5-1.2)/180.16
        lactate_route=.78*consumed;oxid_route=.22*consumed
        lac_theor=2*lactate_route*90.08
        oxygen=6*oxid_route
        air=oxygen*1.15/.209
        air_vol=air*8.314*310.15/101.3
        self.cmp(n0,.12489,.00002);self.cmp(consumed,.091585,.00002)
        self.cmp(lac_theor,12.87,.02)
        self.cmp(100*2.35/(lac_theor/5),91.298,.02)
        self.cmp(oxygen,.120893,.000003)
        self.cmp(air_vol,16.93,.05)

    def test_4_C_12_hidrogenacion_presion(self):
        n0=1.;nfin=n0*.9;xi=n0-nfin
        self.cmp(xi,.1)
        self.cmp(100*xi/.5,20)
        self.cmp((.5-xi)*2+xi,nfin)

    def test_4_C_13_metano_combustion_seca(self):
        m=mod('combustion');o,p=m.oxygen_stoich_formula('CH4',1,m.ProductModel())
        self.cmp(o,2)
        o2feed=o*1.10
        n_nitrogen=o2feed*79/21
        n_dry=p['CO2']+(o2feed-o)+n_nitrogen
        V=n_dry*8.31446*275/110300
        self.cmp(n_dry,9.4762,.0001)
        self.cmp(V,.19644,.0001)
        self.cmp(p['H2O']*18.015,36.03,.0001)

    def test_4_C_14_oxidacion_SO2(self):
        m=mod('gases_ideales_y_mezclas')
        n0=100_000/64.06;o2feed=n0
        extent=.6*n0
        o2vol=o2feed*8.31446*300/150000
        so3vol=extent*8.31446*800/500000
        self.cmp(o2vol,25.96,.02);self.cmp(so3vol,12.46,.02)
        product={'SO2':n0-extent,'O2':o2feed-extent/2,'SO3':extent}
        self.cmp(sum(product.values()),n0+o2feed-extent/2)
        self.cmp(product['SO3'],936.62,.05)

class CotejoCapituloCinco(unittest.TestCase):
    def cmp(self, observed, reference, delta=1e-9):
        self.assertTrue(math.isfinite(float(observed)))
        self.assertAlmostEqual(float(observed), reference, delta=delta)

    def gas(self,name,tc,pc,omega):
        return mod('gases_reales').gas_with_overrides(name,str(tc),str(pc),str(omega))

    def test_5_B_8_diagrama_Z_reducido(self):
        m=mod('gases_reales');g=self.gas('Gas X',100,10,0)
        z=m.lee_kesler(130.,25.,g)['Z']
        self.cmp(z,.6467,.002)  # lectura gráfica Z~0.65; contraste Lee-Kesler

    def test_5_B_10_oxigeno_baja_densidad_iteracion(self):
        m=mod('gases_reales');g=self.gas('O2',154.6,50.5,.02)
        n=4000/32;v=30/n;p=m.R_BAR*250/v
        for _ in range(25):pnew=m.lee_kesler(250,p,g)['Z']*m.R_BAR*250/v;p=pnew
        self.cmp(v,.24,1e-12)
        self.assertTrue(0<p<200)
        self.cmp(p*v/(m.R_BAR*250),.90442213,.0001)
        self.cmp(p,78.33108,.001)
        self.cmp(p*v/(m.R_BAR*250),m.lee_kesler(250,p,g)['Z'],.0001)

    def test_5_B_11_factor_acentrico(self):
        pr=.20*math.exp(-580/(.7*550))
        self.cmp(-math.log10(pr)-1,.35323,.0001)

    def test_5_B_14_Raices_PR_butano(self):
        m=mod('gases_reales')
        vml=.07224*m.R_BAR*380/17.5108
        vmv=.69375*m.R_BAR*380/17.5108
        self.cmp(vml,.13034,.00003);self.cmp(vmv,1.25174,.0001)
        self.assertGreater(vmv,vml)

    def test_5_B_18_Lee_Kesler_nitrogeno_etanol(self):
        m=mod('gases_reales')
        n=self.gas('N2',130.,10.,.040)
        e=self.gas('C2H5OH',130.,10.,.644)
        r1=m.lee_kesler(169.,8.,n);r2=m.lee_kesler(169.,8.,e)
        self.cmp(r1['Z0'],.876356,.00005);self.cmp(r2['Z1'],.0612238,.0001)
        self.cmp(r1['Z'],.878805,.0001);self.cmp(r2['Z'],.915784,.0001)

    def test_5_C_8_PR_bombona_oxigeno(self):
        m=mod('gases_reales');g=self.gas('O2',154.6,50.4,.020)
        a=m.cubic_state('PR',293,200,g);n=200*10/(a['Z']*m.R_BAR*293)
        self.cmp(a['Z'],.917239,.00001)
        self.cmp(n,89.5047,.001);self.cmp(n*32/1000,2.86415,.0001)
        self.cmp(200*10/(m.R_BAR*293),82.0972,.001)

    def test_5_C_9_PR_CO2_denso(self):
        m=mod('gases_reales');g=self.gas('CO2',304.1,73.8,.225)
        r=m.cubic_state('PR',311,80,g)
        self.cmp(r['Z'],.438021,.00002);self.cmp(r['Vm'],.141579,.00002)
        self.cmp(m.R_BAR*311/80,.32324,.00005)

    def test_5_C_10_PR_metano_deposito(self):
        m=mod('gases_reales');g=m.resolve_gas('CH4')
        r=m.cubic_state('PR',298,200,g)
        self.cmp(r['Z'],.806667,.00005)
        n=80/r['Vm'];self.cmp(n,800.53,.2)
        self.cmp(100*(r['Z']-1),-19.3,.1)

    def test_5_C_11_propano_saturacion_fugacidad(self):
        m=mod('gases_reales');g=self.gas('propano',369.8,42.5,.152)
        r=m.saturation_pressure('PR',300,g)
        self.cmp(r['P'],9.99235,.0001)
        self.cmp(r['ZL'],.0347442,.00001);self.cmp(r['ZV'],.814950,.00002)
        self.cmp(r['VmL'],.0867302,.00002);self.cmp(r['VmV'],2.03432,.0001)
        self.cmp(r['phiL']-r['phiV'],0,1e-8)

    def test_5_C_12_butano_presion_saturacion_dos_T(self):
        m=mod('gases_reales');g=self.gas('n-butano',425.125,37.96,.201)
        p=[]
        for t,psat in [(298.15,2.42335),(313.15,3.77216)]:
            r=m.saturation_pressure('PR',t,g)
            self.cmp(r['P'],psat,.0001)
            self.cmp(r['phiL']-r['phiV'],0,1e-8)
            p.append(r['P'])
        self.cmp(100*(p[1]/p[0]-1),55.7,.1)

    def test_5_C_13_CO2_alta_temperatura(self):
        m=mod('gases_reales');g=self.gas('CO2',304.1,73.8,.225)
        r=m.cubic_state('PR',700,90,g)
        self.cmp(r['Z'],1.003837,.00002)
        self.cmp(r['Vm'],.649162,.00001)
        self.cmp(g.M/r['Vm'],67.8,.07)

    def test_5_C_14_agua_dos_estados(self):
        m=mod('gases_reales');g=self.gas('H2O',647.096,220.64,.344)
        a=m.cubic_state('PR',273.15,.005,g)
        b=m.cubic_state('PR',500,20,g)
        self.cmp(a['Z'],.999905,.000005)
        self.cmp(b['Z'],.919523,.00001)
        self.assertGreater(abs(1-b['Z']),100*abs(1-a['Z']))

    def test_5_C_15_CO2_tabla_PR_SRK(self):
        m=mod('gases_reales');g=self.gas('CO2',304.1,73.8,.225)
        cases=[(280,20,.856,.867,.996),(300,50,.671,.695,.335),
               (304,70,.470,.499,.170),(320,100,.392,.418,.104)]
        for T,P,zpr,zsrk,vm in cases:
            with self.subTest(T=T,P=P):
                a=m.cubic_state('PR',T,P,g);b=m.cubic_state('SRK',T,P,g)
                self.cmp(a['Z'],zpr,.001);self.cmp(b['Z'],zsrk,.001)
                self.cmp(a['Vm'],vm,.001)

    def test_5_C_16_CO2_oxigeno_mismo_recipiente(self):
        m=mod('gases_reales')
        nid=100*20/(m.R_BAR*300)
        self.cmp(nid,80.1816,.001)
        for name,tc,pc,om,z,molmass,nref in [('O2',154.6,50.4,.02,.936444,32.,85.6234),
                                               ('CO2',304.1,73.8,.225,.232326,44.01,345.125)]:
            with self.subTest(name=name):
                r=m.cubic_state('PR',300,100,self.gas(name,tc,pc,om))
                self.cmp(r['Z'],z,.00002)
                n=nid/r['Z'];self.cmp(n,nref,.05)
                self.cmp(n*molmass/1000,nref*molmass/1000,.005)

    # Complemento del bloque XI: ejercicios integradores B/C aún sin cotejo.
    def test_6_C_11_saturacion_tolueno_y_masa_vapor(self):
        m=mod('presion_vapor')
        ps=m.antoine_pressure_kpa(298,m.find_antoine('tolueno'))
        self.cmp(ps,3.76288,0.00001)
        n=ps*.002/(.00831446*298);mass=n*92.14
        self.cmp(n,.0030374,3e-7);self.cmp(mass,.279865,.0001)
        self.cmp(2-mass,1.72014,.0001)
        self.cmp(95+ps,98.76288,.00001)

    def test_7_C_9_rocío_ternario_y_flash(self):
        eq=mod('equilibrio_liquido_vapor');op=mod('operaciones_liquido_vapor')
        a=[('acetona',6.42448,1312.253,-32.445),('acetato',6.22809,1245.702,-55.189),('tolueno',6.07827,1343.943,-53.773)]
        cs=[eq.Component(n,A,B,C) for n,A,B,C in a]
        z=[.50,.35,.15]
        rt,_,x=eq.dew_temperature(cs,z,60.0)
        self.cmp(rt.root,336.29594,.00003)
        for got,expect in zip(x,[.235169,.335387,.429444]):self.cmp(got,expect,2e-6)
        k=[c.psat(330.)/60. for c in cs]
        r=op.flash_from_K(z,k,F=1.0)
        self.cmp(r.split.beta,.5745947,3e-6)
        for got,expect in zip(r.split.x,[.353292,.388872,.257836]):self.cmp(got,expect,2e-6)
        for got,expect in zip(r.split.y,[.608616,.321221,.070163]):self.cmp(got,expect,2e-6)
        self.assertLess(max(abs(t) for t in r.split.component_balance_error),1e-10)
        M=[58.08,88.11,92.14]
        w=[xi*mi/sum(xj*mj for xj,mj in zip(r.split.x,M)) for xi,mi in zip(r.split.x,M)]
        for got,expect in zip(w,[.261259,.436257,.302484]):self.cmp(got,expect,2e-6)

    def test_7_C_10_destilacion_rayleigh(self):
        m=mod('operaciones_liquido_vapor')
        r=m.rayleigh_from_final_x(100.,.35,.10,10.28)
        self.cmp(r.N,60.9275,.0001);self.cmp(r.D,39.0725,.0001)
        self.cmp(r.xD_average,.739836,2e-6)
        self.cmp(r.recovery_light,.8259214,1e-6)
        self.cmp(r.N+r.D,100.,1e-10)

    def test_8_C_6_flash_margules_balance(self):
        m=mod('disoluciones_no_ideales')
        model=m.Margules1(1.05);vp=m.DirectPsat([125.,55.])
        state,x,y,g,beta,it,res=m.flash_binary(.35,300.,80.,model,vp,1e-11)
        self.assertEqual(state,'bifásico')
        self.cmp(x[0],.1037629,3e-7);self.cmp(y[0],.3768317,3e-7)
        self.cmp(beta,.9017401,2e-6)
        self.cmp((1-beta)*x[0]+beta*y[0],.35,1e-8)
        self.cmp((1-beta)*x[1]+beta*y[1],.65,1e-8)

    def test_8_C_7_sensibilidad_azeotropo(self):
        m=mod('disoluciones_no_ideales')
        for A,xref,pref in [(1.15,.70435,88.46),(1.20,.69583,89.39),(1.25,.68800,90.35)]:
            x=m.azeotrope_margules1_analytic(A,80.,50.)
            self.cmp(x,xref,2e-5)
            self.cmp(80*math.exp(A*(1-x)**2),pref,.02)
        self.cmp(m.azeotrope_margules1_threshold(80.,50.),math.log(1.6),1e-12)
        x1=m.azeotrope_margules1_analytic(1.15,80.,50.)
        x2=m.azeotrope_margules1_analytic(1.25,80.,50.)
        self.cmp((x2-x1)/.1,-.1632,.001)

    def test_8_C_8_azeotropo_acetona_cloroformo(self):
        m=mod('disoluciones_no_ideales')
        x=.3393;T=337.63;P=101.325
        p1=100*10**(4.42448-1312.253/(T-32.445))
        p2=100*10**(4.56992-1486.455/(T-8.612))
        self.cmp(p1,133.2353,.003);self.cmp(p2,112.7371,.003)
        gammas=[P/p1,P/p2]
        self.cmp(gammas[0],.760497,.00003);self.cmp(gammas[1],.898772,.00003)
        vp=m.DirectPsat([p1,p2]);r=m.experimental_azeotrope_properties(x,T,P,vp)
        self.cmp(r[3],-458.70,.12);self.cmp(r[4],119.6921,.01)
        for Ki in r[5]:self.cmp(Ki,1.,1e-12)

    def test_9_C_5_liquido_liquido_fraccion_molar_global(self):
        # Balance de composición, no se inventan composiciones conjugadas a partir de LCST.
        mt=500*.321;mw=500-mt
        nt=mt/101.19;nw=mw/18.0153;z=nt/(nt+nw)
        self.cmp(mt,160.5);self.cmp(mw,339.5)
        self.cmp(nt,1.586125,.00002);self.cmp(nw,18.84509,.00003)
        self.cmp(z,.0776324,.000002)

    def test_9_C_6_trifasico_agua_tolueno_benceno(self):
        m=mod('inmiscibles_y_arrastre_vapor')
        water=m.Antoine('agua',5.07680,1659.793,-45.854,18.0153,334.,363.)
        cases=[('tolueno',4.07827,1343.943,-53.773,92.1384,357.48673,.555859,4.08654),
               ('benceno',4.72583,1660.652,-1.461,78.1118,342.27133,.296189,10.30295)]
        for name,A,B,C,M,T,ya,ratio in cases:
            with self.subTest(name=name):
                org=m.Antoine(name,A,B,C,M,333.4 if name=='benceno' else 280.,373.5 if name=='benceno' else 410.)
                r=m.temperatura_trifasica(water,org,1.01325)
                self.cmp(r.t,T,.00005)
                pw=water.presion_bar(r.t);po=org.presion_bar(r.t)
                self.cmp(pw+po,1.01325,1e-7)
                self.cmp(pw/1.01325,ya,2e-6)
                mr=po*M/(pw*water.m)
                self.cmp(mr,ratio,.00005)
                self.cmp(1/mr,1/ratio,1e-6)

    def test_10_C_6_proteina_glucosa_osmosis_y_crioscopia(self):
        m=mod('propiedades_coligativas')
        cb=5/66400;cg=5/180.16
        pb=m.presion_osmotica(cb,298.15)
        pg=m.presion_osmotica(cg,298.15)
        self.cmp(pb,.001867,.000003);self.cmp(pg,.68799,.00015)
        self.cmp(pg/pb,66400/180.16,1e-9)
        self.cmp(1.86*cb,.000140,.000002)
        self.cmp(1.86*cg,.0516,.0001)

    def test_10_C_7_eritrocitos_tonicidad_modelo_ideal(self):
        m=mod('propiedades_coligativas')
        pin=m.presion_osmotica(.290,310.15)
        self.cmp(pin,7.48,.02)
        for gL,osm_ref,p_ref,diff_ref in [(4.5,.154,3.97,-3.51),(9.,.308,7.94,.464),(30.,1.027,26.48,19.)]:
            with self.subTest(gL=gL):
                osm=2*gL/58.44;p=m.presion_osmotica(osm,310.15)
                self.cmp(osm,osm_ref,.001)
                self.cmp(p,p_ref,.02);self.cmp(p-pin,diff_ref,.03)

    def test_10_C_8_osmosis_inversa_iones_y_presion(self):
        m=mod('propiedades_coligativas');d=mod('disoluciones_electroliticas')
        na=5/58.44;ca=1.5/110.98;glu=8/180.16;cl=na+2*ca
        osm=na+ca+cl+glu
        self.cmp(osm,.256068,.000003)
        self.cmp(m.presion_osmotica(osm,298.15),6.34783,.00015)
        I=d.fuerza_ionica([d.Ion('Na+',1,na),d.Ion('Ca2+',2,ca),d.Ion('Cl-',-1,cl)])
        self.cmp(I,.126106,.000004)
        self.cmp(2*osm,.512137,.00001)
        self.cmp(m.presion_osmotica(2*osm,298.15),12.69565,.0003)
        self.assertGreater(34-m.presion_osmotica(2*osm,298.15),0)

    def test_11_C_6_mezcla_oxigeno_aire_puro(self):
        air=(60*.40-60*.2095)/(1.-.2095)
        pure=air;air=60-pure
        self.cmp(air,45.5408,.0001);self.cmp(pure,14.4592,.0001)
        self.cmp(air*.7905,36.,1e-10)
        self.cmp(air*.2095+pure,24.,1e-10)

    def test_11_C_7_cloruros_estacionario_muestreo(self):
        m=mod('balances_materia')
        c=(12*85+8*250)/20
        self.cmp(c,151.);self.cmp(20-.020,19.98)
        closure=m.comprobar_residuos([12*85,8*250],[19.98*c,.02*c],3020)
        self.cmp(closure['residuo'],0,1e-10)

    def test_11_C_8_mezclado_dos_solutos_y_agua(self):
        m=mod('balances_materia')
        result=m.mezclar_concentraciones([[10.,2.,0.],[1.,5.,0.]],[1.0,.5],1000.)
        self.assertEqual(result.estado,'unico')
        a,b,w=[result.valores[k] for k in ['V_1','V_2','V_3']]
        self.cmp(a,83.3333333333,1e-8);self.cmp(b,a,1e-8);self.cmp(w,833.3333333333,1e-8)
        self.cmp(10*a+2*b,1000.,1e-8);self.cmp(a+5*b,500.,1e-8)

    def test_11_C_9_transferencia_farmaceutica_perdidas(self):
        m=mod('balances_materia')
        x=m.comprobar_residuos([50.],[20.,24.,.25,5.50],50.)
        self.cmp(x['residuo'],.25);self.cmp(x['porcentaje'],.5)
        self.cmp(x['residuo']*.02*1000,5.)

    def test_11_C_10_bioproceso_balance_medio(self):
        m=mod('balances_materia')
        x=m.comprobar_residuos([30.],[8.,9.,7.5,.2,4.],30.)
        self.cmp(x['residuo'],1.3);self.cmp(x['porcentaje'],4.333333333,1e-7)
        self.cmp(x['residuo']*4.5,5.85)

    def test_11_C_11_consumo_glucosa_reactores(self):
        a=.080*(4.50-1.80);b=.120*(4.50-2.40)
        self.cmp(a,.216);self.cmp(b,.252)
        self.cmp(a+b,.468)
        self.cmp((.08+.12)*4.50-(.08*1.80+.12*2.40),.468)
