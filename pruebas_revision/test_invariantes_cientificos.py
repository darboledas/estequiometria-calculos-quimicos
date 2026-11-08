# -*- coding: utf-8 -*-
"""Pruebas de invariantes físicas y algebraicas, sin datos tomados del código."""
import unittest
import math
from test_auditoria_integral import mod, script, salida_valor

class InvariantesFisicos(unittest.TestCase):
    def test_antoine_inversa_en_diferentes_temperaturas(self):
        m=mod('presion_vapor'); coeff=m.AntoineData('prueba',6,1250,-30,250,450)
        for T in (280,300,325,360,400):
            with self.subTest(T=T):
                self.assertAlmostEqual(m.antoine_temperature_k(m.antoine_pressure_kpa(T,coeff),coeff),T,delta=1e-8)

    def test_vapor_agua_monotonia_y_inversa(self):
        m=mod('vapor_agua')
        Ts=(1,20,50,80,100,150)
        Ps=[m.psat_iapws_kpa(T) for T in Ts]
        self.assertTrue(all(a < b for a,b in zip(Ps,Ps[1:])))
        for T,P in zip(Ts,Ps):
            with self.subTest(T=T):self.assertAlmostEqual(m.tsat_from_p_kpa(P),T,delta=2e-5)

    def test_raoult_cierre_y_rocío(self):
        m=mod('equilibrio_liquido_vapor')
        for x1 in (0.1,0.3,0.5,0.75,0.9):
            r=m.raoult_from_pstar([x1,1-x1],[70,30])
            self.assertAlmostEqual(sum(r['y']),1,delta=1e-12)
            self.assertAlmostEqual(sum(r['partial']),r['P'],delta=1e-12)
            self.assertAlmostEqual(1/sum(yi/pi for yi,pi in zip(r['y'],r['psat'])),r['P'],delta=1e-10)

    def test_palanca_generalizada_cierre(self):
        m=mod('operaciones_liquido_vapor')
        x=[0.2,0.8];y=[0.8,0.2]
        for beta in (.1,.25,.5,.75,.9):
            z=[(1-beta)*xi+beta*yi for xi,yi in zip(x,y)]
            out=m.lever_rule(z,x,y,F=10)
            self.assertAlmostEqual(out.beta,beta,delta=1e-12)
            self.assertAlmostEqual(out.L+out.V,10,delta=1e-10)
            self.assertLess(max(abs(v) for v in out.component_balance_error),1e-10)

    def test_gamma_unidad_es_limite_raoult(self):
        m=mod('disoluciones_no_ideales')
        for x1 in (.01,.2,.5,.9,.99):
            p,y,g,pstar=m.bubble_pressure([x1,1-x1],300,m.Ideal(),m.DirectPsat([70,30]))
            self.assertAlmostEqual(p,70*x1+30*(1-x1),delta=1e-10)
            self.assertAlmostEqual(sum(y),1,delta=1e-10)

    def test_regla_palanca_binodal_conserva_componentes(self):
        m=mod('equilibrio_liquido_liquido')
        for z in (.2,.3,.5,.7,.8):
            r=m.regla_palanca(12,z,.1,.9)
            self.assertAlmostEqual(r.residuo_total,0,delta=1e-10)
            self.assertAlmostEqual(r.residuo_a,0,delta=1e-10)
            self.assertAlmostEqual(r.residuo_b,0,delta=1e-10)

    def test_combustion_alcanos_balance_oxigeno(self):
        m=mod('combustion')
        for n in (1,2,3,4,5,6):
            oxygen,products=m.oxygen_stoich_formula(f'C{n}H{2*n+2}',1,m.ProductModel())
            self.assertAlmostEqual(oxygen,n+(2*n+2)/4,places=10)
            self.assertAlmostEqual(products['CO2'],n,places=10)
            self.assertAlmostEqual(products['H2O'],n+1,places=10)

    def test_psicrometria_razon_humedad_monotona(self):
        m=mod('psicrometria')
        ps=m.saturation_pressure_water(25)
        vals=[m.humidity_ratio_from_pw(phi*ps,101.325) for phi in (0,.25,.5,.75,1)]
        self.assertTrue(all(a < b for a,b in zip(vals,vals[1:])))
        for phi,w in zip((0,.25,.5,.75,1),vals):
            self.assertAlmostEqual(m.pw_from_humidity_ratio(w,101.325),phi*ps,places=9)

    def test_balance_materia_incompatible_no_da_solucion(self):
        m=mod('balances_materia')
        result=m.resolver_lineal(['a'],[m.Ecuacion([1],1,'i'),m.Ecuacion([1],2,'j')])
        self.assertEqual(result.estado,'incompatible')

    def test_interfaz_coligativas_datos_no_fisicos(self):
        m=mod('propiedades_coligativas')
        with self.assertRaises(Exception):m.presion_osmotica(-1,300)

    def test_separacion_sin_solucion_rechazada(self):
        # No puede producirse una corriente más concentrada que ambas salidas.
        # El programa debe interrumpir la ejecución con diagnóstico.
        from pathlib import Path
        import subprocess,sys
        root=Path(__file__).resolve().parents[1]
        proc=subprocess.run([sys.executable,str(root/'capitulo_12/separacion_corrientes.py')],input='100\n80\n50\n10\n',capture_output=True,text=True,timeout=10)
        self.assertNotEqual(proc.returncode,0)
        self.assertIn('negativo',proc.stdout+proc.stderr)

if __name__ == '__main__':unittest.main()
