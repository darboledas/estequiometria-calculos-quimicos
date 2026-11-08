"""Comprobaciones algebraicas independientes asociadas a ejercicios A del libro.

No prueban semánticamente los 206 ejercicios: son invariantes seleccionados.
Usan solo la biblioteca estándar y no modifican los programas de producción.
"""
import math
import unittest


class ConsistenciaConceptual(unittest.TestCase):
    def test_3A14_y_14A5_porcentaje_exceso(self):
        teorico = 100.0
        alimentado = teorico * 1.25
        sobrante = alimentado - teorico
        self.assertAlmostEqual(100.0 * sobrante / alimentado, 20.0)
        self.assertAlmostEqual(100.0 * sobrante / teorico, 25.0)

    def test_4A10_velocidades_cuadraticas(self):
        self.assertAlmostEqual(math.sqrt(28.0 / 4.0), 2.6457513110645907)

    def test_5A3_y_5A1_van_der_waals(self):
        R, T, a, b, vm = .0831446, 300.0, 3.66, .0428, 2.3865283
        pressure = R*T/(vm-b) - a/vm**2
        self.assertAlmostEqual(pressure, 10.0, places=4)
        self.assertLess(pressure*vm/(R*T), 1.0)

    def test_6A5_clausius_clapeyron_sentido_pendiente(self):
        H, R = 40000.0, 8.314462618
        T1, T2 = 300.0, 320.0
        ln_ratio = -H/R*(1/T2 - 1/T1)
        self.assertGreater(ln_ratio, 0)
        self.assertAlmostEqual(-ln_ratio/(1/T2-1/T1)*R, H, places=7)

    def test_6A16_calidad_vapor(self):
        x, vf, vg = .25, .001073, .6058
        v = (1-x)*vf + x*vg
        self.assertAlmostEqual((v-vf)/(vg-vf), x, places=12)

    def test_7A5_enriquecimiento_vapor_raoult(self):
        x, pa, pb = .4, 60., 20.
        y = x*pa/(x*pa+(1-x)*pb)
        self.assertGreater(y, x)
        self.assertAlmostEqual(y-x, x*(1-x)*(pa-pb)/(x*pa+(1-x)*pb))

    def test_7A9_rachford_rice_raiz_y_monotonia(self):
        z = [.5, .5]
        K = [2.0, .5]
        f = lambda beta: sum(z[i]*(K[i]-1)/(1+beta*(K[i]-1)) for i in range(2))
        self.assertGreater(f(0), 0)
        self.assertLess(f(1), 0)
        self.assertAlmostEqual(f(.5), 0, places=12)
        self.assertLess(f(.75), f(.25))

    def test_8A6_margules_y_gibbs_duhem(self):
        x1, A = .3, 1.7
        x2 = 1-x1
        log_gamma1, log_gamma2 = A*x2**2, A*x1**2
        self.assertGreater(log_gamma1, 0)
        self.assertAlmostEqual(x1*(-2*A*x2)+x2*(2*A*x1), 0.0, places=12)
        self.assertAlmostEqual(x1*log_gamma1+x2*log_gamma2,A*x1*x2,places=12)

    def test_9A7_ebullicion_inmiscibles_por_debajo_puros(self):
        pA = lambda t: 50*math.exp(.03*(t-350))
        pB = lambda t: 20*math.exp(.025*(t-350))
        P = 101.325
        lo, hi = 300.0, 400.0
        for _ in range(80):
            mid = (lo+hi)/2
            if pA(mid)+pB(mid) < P:lo=mid
            else:hi=mid
        t_mix = (lo+hi)/2
        pure_a = 350+math.log(P/50)/.03
        pure_b = 350+math.log(P/20)/.025
        self.assertLess(t_mix, pure_a)
        self.assertLess(t_mix, pure_b)

    def test_10A8_fuerza_ionica_na_cl_y_ca_cl2(self):
        m = .01
        i_nacl = .5*(m*1 + m*1)
        i_cacl2 = .5*(m*4 + 2*m*1)
        self.assertAlmostEqual(i_cacl2/i_nacl, 3.0)

    def test_10A16_constantes_coligativas_agua(self):
        R, mw = 8.314462618, .01801528
        kf = R*273.15**2*mw/6010
        kb = R*373.15**2*mw/40660
        self.assertAlmostEqual(kf, 1.86, delta=.03)
        self.assertAlmostEqual(kb, .513, delta=.02)

    def test_12A4_humedad_base_seca(self):
        bh = .2
        bs = bh/(1-bh)
        self.assertAlmostEqual(bs,.25)
        self.assertAlmostEqual(bs/(1+bs),bh)

    def test_13A16_rango_estequiometrico(self):
        r1 = [-1,1,0]
        r2 = [0,-1,1]
        r3 = [-1,0,1]
        self.assertEqual([a+b for a,b in zip(r1,r2)],r3)
        self.assertNotEqual(r1,r2)

    def test_14A4_oxigeno_para_etanol(self):
        c, h, o = 2,6,1
        oxygen = c + h/4 - o/2
        self.assertAlmostEqual(oxygen,3.)

    def test_15A2_humedad_relativa_vs_absoluta(self):
        P, ps = 101.325, 3.17
        w = lambda rh: .62198*(rh*ps)/(P-rh*ps)
        self.assertGreater(w(.8),2*w(.4))

    def test_15A14_mezcla_psicrometrica_adiabatica(self):
        m1, m2 = 2., 3.
        w1,w2 = .008,.018
        h1,h2 = 30.,60.
        wm=(m1*w1+m2*w2)/(m1+m2)
        hm=(m1*h1+m2*h2)/(m1+m2)
        self.assertAlmostEqual(wm,.014)
        self.assertAlmostEqual(hm,48.)


if __name__ == '__main__':
    unittest.main()
