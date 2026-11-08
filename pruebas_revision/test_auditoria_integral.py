# -*- coding: utf-8 -*-
"""Casos independientes de referencia para las 28 aplicaciones.

No sustituyen la validación de todos los modos ni la comparación con el libro.
"""
import importlib
import math
import os
import re
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
for path in ROOT.glob('capitulo_*'):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


def mod(name):
    return importlib.import_module(name)


def script(name, lines, chapter=12):
    path = ROOT / f'capitulo_{chapter:02d}' / (name+'.py')
    proc = subprocess.run([sys.executable,str(path)], input='\n'.join(lines)+'\n',
                          capture_output=True,text=True,timeout=12,env={**os.environ,'MPLBACKEND':'Agg'})
    if proc.returncode != 0:
        raise AssertionError(f'{name}: returncode {proc.returncode}; {proc.stdout[-700:]} {proc.stderr[-700:]}')
    return proc.stdout


def salida_valor(texto, etiqueta):
    """Extrae la cifra impresa detrás de un rótulo de resultados."""
    match = re.search(re.escape(etiqueta) + r':\s*([-+]?(?:\d+(?:,\d*)?|,\d+)(?:[eE][-+]?\d+)?)', texto)
    if not match:
        raise AssertionError('No se encontró ' + repr(etiqueta) + ' en la salida')
    return float(match.group(1).replace(',','.'))


class AuditoriaIndependiente(unittest.TestCase):
    def test_01_unidades(self):
        m=mod('unidades_y_dimensiones')
        self.assertAlmostEqual(m.convertir_unidad(1.0,'ft','m'),0.3048,places=8)

    def test_02_ajuste_quimico(self):
        m=mod('ajuste_ecuaciones')
        self.assertEqual(m.ajustar(['H2','O2'],['H2O']),[2,1,2])

    def test_03_conversion(self):
        m=mod('conversion_rendimiento_selectividad')
        r=m.fraccion_conversion(m.Q(10),m.Q(6))
        self.assertAlmostEqual(float(r.v),0.4,places=10)

    def test_04_densidades(self):
        m=mod('densidades_y_escalas')
        r=m.brix_a_ge(m.Q(0))
        self.assertAlmostEqual(float(r.v),1.0,places=6)

    def test_05_masa_molar(self):
        m=mod('masa_molar')
        r=m.calculate_molar_mass('H2O')
        self.assertAlmostEqual(float(r.raw_mass),18.015,delta=0.03)

    def test_06_limitante(self):
        m=mod('reactivo_limitante')
        caps,idx,maxi,adv,left,formed=m.balance([m.Q(4),m.Q(1)],[2,1],[2])
        self.assertEqual(idx,[1]);self.assertAlmostEqual(float(adv.v),1)
        self.assertAlmostEqual(float(formed[0].v),2)

    def test_07_gases_ideales(self):
        m=mod('gases_ideales_y_mezclas')
        r=m.solve_ideal(None,0.025,1.0,300.0)
        self.assertAlmostEqual(r['P'],m.R*300/0.025,places=6)
        with self.assertRaises(ValueError):m.solve_ideal(None,-1,1,300)
        with self.assertRaises(ValueError):m.solve_ideal(None,0.025,1,float('nan'))
        with self.assertRaises(ValueError):m.solve_ideal(None,0.025,1,float('inf'))

    def test_08_gases_reales_virial(self):
        m=mod('gases_reales')
        self.assertAlmostEqual(m.virial_pressure(10,Bp=-0.002),0.98,places=9)
        out=m.virial_volume(300,2)
        self.assertAlmostEqual(out['Z'],1.0,delta=1e-8)

    def test_09_antoine_y_clausius(self):
        m=mod('presion_vapor')
        d=m.AntoineData('test',5,1000,0,250,400)
        p=m.antoine_pressure_kpa(300,d)
        self.assertAlmostEqual(p,10**(5-1000/300),places=10)
        self.assertAlmostEqual(m.antoine_temperature_k(p,d),300,places=8)
        self.assertAlmostEqual(m.cc_pressure2(100,300,300,40000),100,places=9)

    def test_10_presion_saturacion_agua(self):
        m=mod('vapor_agua')
        self.assertAlmostEqual(m.psat_iapws_kpa(100),101.418,delta=0.12)
        self.assertAlmostEqual(m.tsat_from_p_kpa(101.418),100,delta=0.12)
        with self.assertRaises(ValueError):m.psat_iapws_kpa(-20)

    def test_11_equilibrio_ideal_raoult(self):
        m=mod('equilibrio_liquido_vapor')
        r=m.raoult_from_pstar([0.4,0.6],[80,40])
        self.assertAlmostEqual(r['P'],56,places=10)
        self.assertAlmostEqual(r['y'][0],32/56,places=10)

    def test_12_flash_rachford_rice(self):
        m=mod('operaciones_liquido_vapor')
        r=m.flash_from_K([0.5,0.5],[2,0.5])
        self.assertAlmostEqual(r.split.beta,0.5,delta=1e-9)
        self.assertAlmostEqual(r.split.x[0],1/3,delta=1e-9)
        self.assertAlmostEqual(r.split.y[0],2/3,delta=1e-9)

    def test_13_disoluciones_no_ideales_limite_ideal(self):
        m=mod('disoluciones_no_ideales')
        gammas,activities,gE=m.activity_properties([0.2,0.8],m.Ideal())
        self.assertAlmostEqual(float(gE),0,places=10)
        p,y,_,_=m.bubble_pressure([0.2,0.8],300,m.Ideal(),m.DirectPsat([100,50]))
        self.assertAlmostEqual(p,60,places=10)
        self.assertAlmostEqual(float(y[0]),1/3,places=10)
        with self.assertRaises(ValueError):
            m.bubble_pressure([1.5,-0.5],300,m.Ideal(),m.DirectPsat([100,50]))
        with self.assertRaises(ValueError):
            m.activity_properties([float('nan'),0.5],m.Ideal())
        with self.assertRaises(ValueError):
            m.bubble_pressure([0.5,0.5],300,m.Ideal(),m.DirectPsat([float('nan'),50]))

    def test_14_palanca_liquido_liquido(self):
        m=mod('equilibrio_liquido_liquido')
        r=m.regla_palanca(10,0.5,0.2,0.8)
        self.assertAlmostEqual(r.l1,5,places=10)
        self.assertAlmostEqual(r.l2,5,places=10)
        self.assertAlmostEqual(r.residuo_total,0,delta=1e-10)

    def test_15_inmiscibles(self):
        m=mod('inmiscibles_y_arrastre_vapor')
        a=m.Antoine('A',0,0,0,18)
        b=m.Antoine('B',0,0,0,92)
        self.assertEqual(m.presiones(a,b,300),(1,1,2))
        r=m.condensacion(10,0.4,18,92)
        self.assertAlmostEqual(r['m_total'],6*18+4*92,places=10)
        self.assertAlmostEqual(r['residual_m'],0,places=10)

    def test_16_fuerza_ionica(self):
        m=mod('disoluciones_electroliticas')
        ions=[m.Ion('Na',1,0.1),m.Ion('Cl',-1,0.1)]
        self.assertAlmostEqual(m.fuerza_ionica(ions),0.1,places=10)

    def test_17_osmosis(self):
        m=mod('propiedades_coligativas')
        self.assertAlmostEqual(m.presion_osmotica(0.1,300),0.1*m.R_BAR_L*300,places=9)
        self.assertAlmostEqual(m.vapor_ideal(10,0.8)['presion'],8,places=10)

    def test_18_balance_lineal(self):
        m=mod('balances_materia')
        out=m.resolver_lineal(['x','y'],[m.Ecuacion([1,1],3,'total'),m.Ecuacion([1,-1],1,'dif')])
        self.assertEqual(out.estado,'unico')
        self.assertAlmostEqual(out.valores['x'],2,places=10)
        self.assertAlmostEqual(out.valores['y'],1,places=10)

    def test_19_cristalizacion_consola(self):
        out=script('cristalizacion',['100','50','25'])
        self.assertIn('Cristales obtenidos',out)
        self.assertAlmostEqual(salida_valor(out,'Cristales obtenidos'),50,delta=0.1)
        self.assertAlmostEqual(salida_valor(out,'Licor madre'),250,delta=0.1)
        self.assertIn('COMPROBACIÓN',out)

    def test_20_evaporacion_consola(self):
        out=script('evaporacion',['100','20','40'])
        self.assertAlmostEqual(salida_valor(out,'Disolución concentrada'),50,delta=0.1)
        self.assertAlmostEqual(salida_valor(out,'Disolvente evaporado'),50,delta=0.1)
        self.assertIn('COMPROBACIÓN',out)

    def test_21_extraccion_consola(self):
        out=script('extraccion_liquido_liquido',['1','100,0','10,0','2,0','10,0'])
        self.assertAlmostEqual(salida_valor(out,'Soluto que permanece en el refinado'),100/3,delta=0.5)
        self.assertAlmostEqual(salida_valor(out,'Soluto transferido al extracto'),200/3,delta=0.5)

    def test_22_filtracion_consola(self):
        out=script('filtracion',['100','20','80','40'])
        self.assertAlmostEqual(salida_valor(out,'Masa de filtrado'),60,delta=0.1)
        self.assertIn('balance sólido',out)

    def test_23_secado_consola(self):
        out=script('secado',['1','100','40','20'])
        self.assertAlmostEqual(salida_valor(out,'Producto final'),75,delta=0.1)
        self.assertAlmostEqual(salida_valor(out,'Agua eliminada'),25,delta=0.1)
        self.assertIn('COMPROBACIÓN',out)

    def test_24_separacion_consola(self):
        out=script('separacion_corrientes',['100','30','50','10'])
        self.assertAlmostEqual(salida_valor(out,'Corriente 1'),50,delta=0.1)
        self.assertAlmostEqual(salida_valor(out,'Corriente 2'),50,delta=0.1)
        self.assertIn('balance total',out)

    def test_25_reaccion_unica(self):
        m=mod('balance_una_reaccion')
        sp=[{'nu':-1},{'nu':2}]
        change,final=m.calculate_final(sp,[m.Q.exact_value(3),m.Q.exact_value(0)],m.Q.exact_value(2))
        self.assertEqual(float(final[0].value),1)
        self.assertEqual(float(final[1].value),4)

    def test_26_varias_reacciones(self):
        m=mod('balance_varias_reacciones')
        # A -> B -> C con extensiones 3 y 1; alimentación A=5
        contributions,final=m.calculate_final(['A','B','C'],[[-1,0],[1,-1],[0,1]],
            [m.Q.exact_value(5),m.Q.exact_value(0),m.Q.exact_value(0)],
            [m.Q.exact_value(3),m.Q.exact_value(1)])
        self.assertEqual([float(q.value) for q in final],[2,2,1])

    def test_27_combustion_metano(self):
        m=mod('combustion')
        needed,products=m.oxygen_stoich_formula('CH4',1,m.ProductModel())
        self.assertAlmostEqual(needed,2,places=10)
        self.assertAlmostEqual(products['CO2'],1,places=10)
        self.assertAlmostEqual(products['H2O'],2,places=10)

    def test_28_psicrometria(self):
        m=mod('psicrometria')
        p=m.saturation_pressure_water(25)
        self.assertAlmostEqual(p,3.1698,delta=0.015)
        W=m.humidity_ratio_from_pw(0.5*p,101.325)
        self.assertAlmostEqual(W,0.621945*0.5*p/(101.325-0.5*p),delta=1e-6)
        self.assertAlmostEqual(m.pw_from_humidity_ratio(W,101.325),0.5*p,places=9)
        with self.assertRaises(m.PsychrometricError):m.pw_from_humidity_ratio(0.02,0)
        with self.assertRaises(m.PsychrometricError):m.pw_from_humidity_ratio(float('nan'),101.325)
        with self.assertRaises(m.PsychrometricError):m.humidity_ratio_from_pw(1,float('nan'))


if __name__=='__main__':unittest.main()
