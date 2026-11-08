# -*- coding: utf-8 -*-
"""Contrastes de sensibilidad inversa y dominios empíricos.

Se utilizan soluciones analíticas o conjuntos sintéticos con solución conocida.
No equivalen a validación experimental de las correlaciones termodinámicas.
"""
import math
import random
import unittest
from test_auditoria_integral import mod


class SistemasInversosSensibles(unittest.TestCase):
    def test_pivoteo_completo_y_equilibrado_2x2(self):
        cb = mod('combustion')
        for scale in (1e-12, 1e-6, 1, 1e6, 1e12):
            with self.subTest(scale=scale):
                A = [[0, 2*scale], [3*scale, 4*scale]]
                b = [4*scale, 11*scale]
                estado, sol = cb.solve_linear_system(A, b)
                self.assertEqual(estado, 'unique')
                self.assertAlmostEqual(sol[0], 1, delta=1e-9)
                self.assertAlmostEqual(sol[1], 2, delta=1e-9)

    def test_rechaza_falsas_composiciones_unicas_casi_singulares(self):
        cb = mod('combustion')
        for delta in (1e-8, 1e-9, 1e-10, 1e-11):
            for magnitud in (1e-12, 1, 1e12):
                with self.subTest(delta=delta, magnitud=magnitud):
                    A = [[magnitud, magnitud], [magnitud, magnitud*(1+delta)]]
                    b = [2*magnitud, (2+delta)*magnitud]
                    with self.assertRaisesRegex(cb.CombustionError, 'mal condicionado'):
                        cb.solve_linear_system(A,b)

    def test_perturbacion_minima_cambiaria_fracciones(self):
        # Perturbación relativa de ~1e-8 puede alterar drásticamente las
        # cantidades deducidas, aun con residuos algebraicos muy pequeños.
        cb=mod('combustion')
        A=[[1,1],[1,1+1e-9]]
        b=[2,2+1e-9+1e-8]
        with self.assertRaises(cb.CombustionError):
            cb.solve_linear_system(A,b)

    def test_disparidad_de_observables_se_detecta(self):
        cb=mod('combustion')
        A=[[1e12,1],[1e12,1.000001]]
        b=[1e12+1,1e12+1.000001]
        with self.assertRaisesRegex(cb.CombustionError, 'muy desiguales'):
            cb.solve_linear_system(A,b)

    def test_escalas_heterogeneas_pero_independientes(self):
        cb=mod('combustion')
        A=[[1e-12,0],[0,1e12]]
        b=[3e-12,2e12]
        estado,sol=cb.solve_linear_system(A,b)
        self.assertEqual(estado,'unique')
        self.assertAlmostEqual(sol[0],3,places=10)
        self.assertAlmostEqual(sol[1],2,places=10)

    def test_exactamente_dependientes_vs_incompatibles(self):
        cb=mod('combustion')
        self.assertEqual(cb.solve_linear_system([[1,1],[2,2]],[2,4]),('underdetermined',None))
        self.assertEqual(cb.solve_linear_system([[1,1],[2,2]],[2,5]),('inconsistent',None))

    def test_sistemas_rectangulares_redundantes(self):
        cb=mod('combustion')
        A=[[1,2],[3,4],[4,6],[1,0]]
        estado,sol=cb.solve_linear_system(A,[5,11,16,1])
        self.assertEqual(estado,'unique')
        self.assertAlmostEqual(sol[0],1,places=10)
        self.assertAlmostEqual(sol[1],2,places=10)
        estado,_=cb.solve_linear_system(A,[5,11,16.001,1])
        self.assertEqual(estado,'inconsistent')

    def test_reconstrucciones_aleatorias_con_coeficientes_enteros(self):
        cb=mod('combustion')
        r=random.Random(20261107)
        for idx in range(200):
            # Construir matriz estrictamente diagonal dominante (bien condicionada)
            n=2+idx%5
            A=[[r.randint(-3,3) for _ in range(n)] for __ in range(n)]
            for i in range(n): A[i][i]=12+n
            x=[r.uniform(0,5) for _ in range(n)]
            b=[math.fsum(a*v for a,v in zip(row,x)) for row in A]
            estado,sol=cb.solve_linear_system(A,b)
            self.assertEqual(estado,'unique')
            for esperado,observado in zip(x,sol):
                self.assertAlmostEqual(esperado,observado,delta=1e-9)


class CorrelacionesEmpiricas(unittest.TestCase):
    def test_antoine_inversion_en_intervalos_declarados(self):
        a=mod('presion_vapor')
        for name, data in a.ANTOINE.items():
            for j in range(21):
                T=data.Tmin+(data.Tmax-data.Tmin)*j/20
                with self.subTest(name=name,T=T):
                    a.check_antoine_range(T,data)
                    P=a.antoine_pressure_kpa(T,data)
                    self.assertTrue(math.isfinite(P) and P>0)
                    self.assertAlmostEqual(a.antoine_temperature_k(P,data),T,delta=2e-9)

    def test_antoine_rechaza_fuera_de_intervalo(self):
        a=mod('presion_vapor')
        for data in a.ANTOINE.values():
            with self.assertRaises(ValueError):a.check_antoine_range(data.Tmin-0.01,data)
            with self.assertRaises(ValueError):a.check_antoine_range(data.Tmax+0.01,data)

    def test_clausius_clapeyron_inversion_analitica(self):
        a=mod('presion_vapor')
        for T1 in (220,290,350):
            for delta in (-30,5,20):
                T2=T1+delta
                P1=101.325;dh=38000.
                P2=a.cc_pressure2(P1,T1,T2,dh)
                self.assertAlmostEqual(a.cc_temperature2(P1,T1,P2,dh),T2,delta=2e-10)
                self.assertAlmostEqual(a.cc_enthalpy(P1,T1,P2,T2),dh,delta=1e-5)

    def test_duhring_regresion_sintetica_e_inversion(self):
        a=mod('presion_vapor')
        data=a.ANTOINE['agua']
        temps=[data.Tmin+(data.Tmax-data.Tmin)*j/5 for j in range(1,5)]
        samples=[(1.08*t+4.5,a.antoine_pressure_kpa(t,data)) for t in temps]
        slope, intercept, r2, refs=a.duhring_fit(samples,data)
        self.assertAlmostEqual(slope,1.08,delta=1e-11)
        self.assertAlmostEqual(intercept,4.5,delta=1e-8)
        self.assertAlmostEqual(r2,1,delta=1e-12)
        for td,p in samples:
            ref,calc=a.duhring_pressure_at_temperature(td,slope,intercept,data)
            self.assertAlmostEqual(p,calc,delta=1e-7*max(1,p))

    def test_exponentes_fuera_de_rango_no_generan_traceback_inesperado(self):
        a=mod('presion_vapor')
        data=a.AntoineData('extremo',400,0,0,280,320)
        with self.assertRaisesRegex(ValueError,'Antoine'):
            a.antoine_pressure_kpa(300,data)
        with self.assertRaisesRegex(ValueError,'Clausius'):
            a.cc_pressure2(100,200,500,1e9)
        with self.assertRaisesRegex(ValueError,'Lee-Kesler'):
            a.lee_kesler_pressure_kpa(450,500,5000,-5000)

    def test_lee_kesler_limite_critico(self):
        a=mod('presion_vapor')
        with self.assertRaises(ValueError):a.lee_kesler_pressure_kpa(500,500,5000,.2)
        with self.assertRaises(ValueError):a.lee_kesler_pressure_kpa(100,500,5000,.2)
        # Comprobación de salida físicamente positiva dentro del dominio didáctico.
        r=a.lee_kesler_pressure_kpa(350,500,5000,.2)
        self.assertGreater(r[-1],0)
        self.assertLess(r[-1],5000)


class CorrespondenciaConLibro(unittest.TestCase):
    """Contraste con el libro, tabla 6.1, ejercicios 6.B.11, 6.B.14, 6.B.15.

    Fuente: Estequiometría y cálculos químicos, edición Carta, 934 páginas.
    Estas comprobaciones no abarcan todos los ejercicios del capítulo.
    """

    def test_tabla_6_1_once_correlaciones_antoine(self):
        a=mod('presion_vapor')
        libro = {
            'agua':(7.06252,1650.270,-46.854,284,441),
            'acetona':(6.25017,1214.208,-43.198,241,350),
            'acetonitrilo':(6.27873,1355.374,-37.853,288,362),
            'amoniaco':(6.86886,1113.928,-10.409,240,372),
            'benceno':(6.03053,1211.035,-52.360,280,377),
            'etanol':(7.16985,1554.301,-50.500,270,369),
            'n-heptano':(6.01876,1264.370,-56.510,270,400),
            'n-hexano':(6.00265,1171.531,-48.780,245,370),
            'metanol':(7.19735,1574.991,-34.290,257,364),
            'tolueno':(6.07956,1344.802,-53.670,280,410),
            'acido benzoico':(6.57885,1819.998,-125.200,405,560),
        }
        self.assertEqual(set(libro),set(a.ANTOINE))
        for nombre,ref in libro.items():
            with self.subTest(sustancia=nombre):
                got=a.ANTOINE[nombre]
                for expected,actual in zip(ref,(got.A,got.B,got.C,got.Tmin,got.Tmax)):
                    self.assertAlmostEqual(actual,expected,places=6)

    def test_ejercicio_6_b_11_interpolacion(self):
        a=mod('presion_vapor')
        self.assertAlmostEqual(a.linear_interpolation(320,12,340,28.5,330),20.3,delta=.1)
        self.assertAlmostEqual(a.cc_interpolation(320,12,340,28.5,330),18.7,delta=.1)

    def test_ejercicio_6_b_14_heptano(self):
        a=mod('presion_vapor')
        r=a.lee_kesler_pressure_kpa(350,540.2,2740,.349)
        pa=a.antoine_pressure_kpa(350,a.ANTOINE['n-heptano'])
        self.assertAlmostEqual(r[0],350/540.2,places=12)
        self.assertAlmostEqual(r[-1],50.8925458748,delta=2e-7)
        self.assertAlmostEqual(pa,51.3698879413,delta=2e-7)
        self.assertAlmostEqual(abs(r[-1]-pa)/pa*100,.929,delta=.005)

    def test_ejercicio_6_b_15_metanol(self):
        a=mod('presion_vapor')
        pa=a.antoine_pressure_kpa(300,a.ANTOINE['metanol'])
        pb=a.antoine_pressure_kpa(320,a.ANTOINE['metanol'])
        dh=a.cc_enthalpy(pa,300,pb,320)/1000
        self.assertAlmostEqual(pa,18.6,delta=.1)
        self.assertAlmostEqual(pb,48.4,delta=.1)
        self.assertAlmostEqual(dh,38.1,delta=.1)


if __name__=='__main__': unittest.main()
