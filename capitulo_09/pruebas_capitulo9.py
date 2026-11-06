#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pruebas de regresión para los ejemplos 9.1–9.3 y los ejercicios B.1–B.9,
C.1–C.6 del capítulo 9. Ejecutar: python pruebas_capitulo9.py

Valores de referencia transcritos de ejemplos resueltos, o calculados
independientemente de las ecuaciones del enunciado cuando no hay solución
impresa. Se testean asimismo límites físicos, redondeo y dominio Antoine.
"""
import math
import unittest
from tempfile import TemporaryDirectory
from pathlib import Path
import csv
import equilibrio_liquido_liquido as ll
import inmiscibles_y_arrastre_vapor as iv

class VerificacionEjemplos(unittest.TestCase):
    def test_ejemplo_9_1(self):
        self.assertAlmostEqual(ll.conversion_masica_molar(.321,101.19,18.0153), .0776, delta=.00006)
        self.assertEqual(ll.conversion_molar_masica(0.0776324308933,101.19,18.0153).__round__(3),.321)

    def test_ejemplo_9_2(self):
        dw,lo,hi=ll.beysens(.02134)
        self.assertAlmostEqual(dw,.5384,delta=.00005)
        self.assertAlmostEqual(lo,.2658,delta=.00005)
        self.assertAlmostEqual(hi,.8042,delta=.00005)
        f=ll.regla_palanca(1.,.45,lo,hi)
        self.assertAlmostEqual(f.l1,.6579,delta=.0001)
        self.assertAlmostEqual(f.l2,.3421,delta=.0001)
        self.assertAlmostEqual(f.a_l1+f.a_l2,.45,delta=1e-13)
        self.assertAlmostEqual(f.b_l1+f.b_l2,.55,delta=1e-13)

    def test_ejemplo_9_3(self):
        r=iv.temperatura_trifasica(iv.AGUA_1,iv.TOLUENO,1.01325,1e-9)
        d=iv.composicion_vapor(iv.AGUA_1,iv.TOLUENO,r.t,1.01325)
        self.assertAlmostEqual(r.t,357.49,delta=.01)
        self.assertAlmostEqual(d['y_b'],.4441,delta=.00005)
        self.assertAlmostEqual(d['m_b_a'],4.09,delta=.01)
        self.assertAlmostEqual(iv.consumo_agua(1.,d['m_b_a']),.245,delta=.0005)

class VerificacionB(unittest.TestCase):
    def test_9_B_1(self):
        r=ll.regla_palanca(2.5,.6,.2658,.8042)
        self.assertAlmostEqual(r.l1,.94818,delta=1e-5)
        self.assertAlmostEqual(r.l2,1.55182,delta=1e-5)
        self.assertAlmostEqual(r.a_l1,.252026,delta=1e-6)
        self.assertAlmostEqual(r.a_l2,1.247974,delta=1e-6)
        self.assertAlmostEqual(r.b_l1,.696154,delta=1e-6)
        self.assertAlmostEqual(r.b_l2,.303846,delta=1e-6)

    def test_l1_rica_en_a_nomenclatura_general(self):
        # Apartado 9.3: si se representa x_A, la L1 rica en A está a la derecha.
        r=ll.regla_palanca(2.,.6,.8,.2)
        self.assertAlmostEqual(r.l1,2.*(0.6-0.2)/(0.8-0.2))
        self.assertAlmostEqual(r.l2,2.*(0.8-0.6)/(0.8-0.2))
        self.assertAlmostEqual(r.a_l1+r.a_l2,1.2)

    def test_9_B_2(self):
        dw,lo,hi=ll.beysens(.0100)
        self.assertAlmostEqual(dw,.423108,delta=1e-6)
        self.assertAlmostEqual(lo,.323446,delta=1e-6)
        self.assertAlmostEqual(hi,.746554,delta=1e-6)
        r=ll.regla_palanca(1.5,.5,lo,hi)
        self.assertAlmostEqual(r.l1,.874082,delta=1e-6)
        self.assertAlmostEqual(r.l2,.625918,delta=1e-6)

    def test_9_B_3(self):
        r=iv.temperatura_trifasica(iv.AGUA_1,iv.TOLUENO,.8)
        v=iv.composicion_vapor(iv.AGUA_1,iv.TOLUENO,r.t,.8)
        self.assertAlmostEqual(r.t,351.18892,delta=.0001)
        self.assertAlmostEqual(v['y_b'],.45336443,delta=1e-6)
        self.assertAlmostEqual(v['m_b_a'],4.24178576,delta=1e-5)
        self.assertLess(r.t,iv.temperatura_trifasica(iv.AGUA_1,iv.TOLUENO,1.01325).t)

    def test_9_B_4(self):
        r=iv.temperatura_trifasica(iv.AGUA_1,iv.ANILINA,1.01325)
        v=iv.composicion_vapor(iv.AGUA_1,iv.ANILINA,r.t,1.01325)
        self.assertAlmostEqual(r.t,371.52376,delta=.0001)
        self.assertAlmostEqual(v['y_b'],.0566449,delta=1e-6)
        self.assertAlmostEqual(v['m_b_a'],.310397,delta=1e-5)
        self.assertAlmostEqual(iv.consumo_agua(.5,v['m_b_a']),1.61084,delta=1e-4) # kg

    def test_9_B_5(self):
        r=iv.temperatura_trifasica(iv.AGUA_2,iv.BENCENO,1.01325)
        v=iv.composicion_vapor(iv.AGUA_2,iv.BENCENO,r.t,1.01325)
        self.assertAlmostEqual(r.t,342.2713,delta=.001)
        self.assertAlmostEqual(v['y_b'],.703811,delta=1e-5)
        self.assertAlmostEqual(v['m_b_a'],10.302953,delta=1e-5)
        self.assertAlmostEqual(iv.consumo_agua(1.,v['m_b_a']),.09705955,delta=1e-6)

    def test_9_B_6(self):
        d=iv.consumir_fases(2.,1.,.4441)
        self.assertIn('B (fase LB)',d['agotada'])
        self.assertAlmostEqual(d['n_v'],2.2517451,delta=1e-6)
        self.assertAlmostEqual(d['n_a_residual'],.7482549,delta=1e-6)

    def test_9_B_7(self):
        d=iv.condensacion(10.,.4441,18.0153,92.1384)
        self.assertAlmostEqual(d['n_a'],5.559,delta=1e-6)
        self.assertAlmostEqual(d['n_b'],4.441,delta=1e-6)
        self.assertAlmostEqual(d['m_total'],509.3336871,delta=1e-4) # g
        self.assertAlmostEqual(d['w_b'],.80337634,delta=1e-7)

    def test_9_B_8(self):
        v=[]
        for p,reference_t,reference_y in [(0.7,347.73905,.45857393),(1.2,362.15156,.43751602)]:
            r=iv.temperatura_trifasica(iv.AGUA_1,iv.TOLUENO,p)
            d=iv.composicion_vapor(iv.AGUA_1,iv.TOLUENO,r.t,p)
            self.assertAlmostEqual(r.t,reference_t,delta=.0001)
            self.assertAlmostEqual(d['y_b'],reference_y,delta=1e-6)
            v.append(r.t)
        self.assertLess(v[0],v[1])

    def test_9_B_9(self):
        d=iv.vapor_desde_relacion_masica(.310,18.0153,93.1265)
        self.assertAlmostEqual(d['p_b_a'],.05996943,delta=1e-7)
        self.assertAlmostEqual(d['y_b'],.05657656,delta=1e-7)
        self.assertAlmostEqual(d['y_a'],.94342344,delta=1e-7)

class VerificacionC(unittest.TestCase):
    def test_9_C_1(self):
        for eps,l1,l2 in [(.0200,2.41710371,1.58289629),(.0050,2.64818523,1.35181477)]:
            dw,lo,hi=ll.beysens(eps)
            res=ll.regla_palanca(4.,.480,lo,hi)
            self.assertAlmostEqual(res.l1,l1,delta=1e-6)
            self.assertAlmostEqual(res.l2,l2,delta=1e-6)
            self.assertLess(abs(res.residuo_a),1e-12)
            self.assertLess(abs(res.residuo_b),1e-12)

    def test_9_C_2(self):
        r=iv.temperatura_trifasica(iv.AGUA_2,iv.TOLUENO,.8)
        v=iv.composicion_vapor(iv.AGUA_2,iv.TOLUENO,r.t,.8)
        d=iv.consumir_fases(30.,12.,v['y_b'])
        self.assertEqual(d['agotada'],'B (fase LB)')
        self.assertAlmostEqual(d['n_v'],26.46877,delta=.05)
        self.assertAlmostEqual(d['n_a_residual'],15.53123,delta=.05)

    def test_9_C_3(self):
        r=iv.temperatura_trifasica(iv.AGUA_1,iv.ANILINA,1.01325)
        v=iv.composicion_vapor(iv.AGUA_1,iv.ANILINA,r.t)
        pure=iv.ANILINA.ebullicion_puro(1.01325)
        self.assertAlmostEqual(pure,456.99164,delta=.05)
        self.assertGreater(pure-r.t,85)
        self.assertAlmostEqual(iv.consumo_agua(250,v['m_b_a']),805.42007,delta=.3)

    def test_9_C_4(self):
        d=iv.condensacion(100.,.4441,18.0153,92.1384)
        self.assertAlmostEqual(d['n_a'],55.59)
        self.assertAlmostEqual(d['n_b'],44.41)
        self.assertAlmostEqual(d['m_a'],1001.470527,delta=.01) # kg/h
        self.assertAlmostEqual(d['m_b'],4091.866344,delta=.01) # kg/h
        self.assertAlmostEqual(d['m_total'],5093.336871,delta=.01)

    def test_9_C_5(self):
        self.assertAlmostEqual(500*.321,160.5)
        self.assertAlmostEqual(500*(1-.321),339.5)
        self.assertAlmostEqual(ll.conversion_masica_molar(.321,101.19,18.0153),.07763243,delta=1e-7)

    def test_9_C_6(self):
        for b,ref in ((iv.TOLUENO,357.4867263),(iv.BENCENO,342.2713279)):
            r=iv.temperatura_trifasica(iv.AGUA_2,b,1.01325)
            self.assertAlmostEqual(r.t,ref,delta=.0001)
            iv.AGUA_2.comprobar_validez(r.t)
            b.comprobar_validez(r.t)
        self.assertAlmostEqual(iv.AGUA_2.c,-45.854,delta=1e-12)

class Controles(unittest.TestCase):
    def test_intervalos_y_errores(self):
        for f in (lambda:ll.beysens(.8),
                  lambda:ll.regla_palanca(2,.4,.8,.8),
                  lambda:ll.regla_palanca(2,-.1,.2,.8),
                  lambda:iv.temperatura_trifasica(iv.AGUA_2,iv.TOLUENO,.1),
                  lambda:iv.ANILINA.ebullicion_puro(10),
                  lambda:iv.consumir_fases(0,1,.5),
                  lambda:iv.consumo_agua(1,0)):
            with self.assertRaises(ValueError):f()

    def test_precision_y_coma(self):
        self.assertEqual(ll.cifras('2,50'),3)
        self.assertEqual(iv.cifras('1,000'),4)
        self.assertEqual(iv.cifras('500'),1)
        self.assertEqual(iv.cifras('500.'),3)
        self.assertEqual(ll.fmt(.657864,3),'0,658')
        self.assertEqual(iv.fmt(.24471488,3),'0,245')
        r=iv.temperatura_trifasica(iv.AGUA_1,iv.TOLUENO,1.01325)
        self.assertEqual(iv.fmt_temperatura_equilibrio(r.t,1.01325,6,iv.AGUA_1,iv.TOLUENO),
                         '357,49 K (84,34 °C)')
        r2=iv.temperatura_trifasica(iv.AGUA_1,iv.TOLUENO,.8)
        self.assertEqual(iv.fmt_temperatura_equilibrio(r2.t,.8,3,iv.AGUA_1,iv.TOLUENO),
                         '351,19 K (78,04 °C)')

    def test_interpolacion_sin_extrapolar(self):
        with TemporaryDirectory() as td:
            p=Path(td)/'binodal.csv'
            p.write_text('T_K;izquierda;derecha\n300;0,2;0,8\n310;0,3;0,7\n',encoding='utf-8')
            data=ll.binodal_csv(str(p))
            self.assertEqual(ll.interpolar_binodal(data,305.),(.25,.75))
            with self.assertRaises(ValueError): ll.interpolar_binodal(data,400.)

    def test_gibbs_y_estabilidad(self):
        lo,hi,sp1,sp2=ll.regular_solucion(3.)
        self.assertAlmostEqual(lo,.07072018,delta=1e-7)
        self.assertLess(lo,sp1)
        self.assertLess(sp2,hi)
        self.assertAlmostEqual(ll.g_regular(lo,3.),ll.g_regular(hi,3.),delta=1e-12)
        with self.assertRaises(ValueError):ll.regular_solucion(2)

    def test_graficas_png_y_svg(self):
        import os
        from unittest.mock import patch
        os.environ['MPLBACKEND']='Agg'
        with TemporaryDirectory() as td:
            base=str(Path(td)/'figura')
            with patch('builtins.input',side_effect=['4',base]):
                ll.grafico_beysens(1.83,.318,.535,304.65,.02134,.45)
            self.assertGreater((Path(td)/'figura.png').stat().st_size,5000)
            self.assertGreater((Path(td)/'figura.svg').stat().st_size,5000)
            with patch('builtins.input',side_effect=['4',str(Path(td)/'tx')]):
                iv.grafico_tx(iv.AGUA_1,iv.TOLUENO,1.01325)
            self.assertGreater((Path(td)/'tx.png').stat().st_size,5000)
            self.assertGreater((Path(td)/'tx.svg').stat().st_size,5000)
            with patch('builtins.input',side_effect=['2',str(Path(td)/'presiones')]):
                r=iv.temperatura_trifasica(iv.AGUA_1,iv.TOLUENO,1.01325)
                iv.grafico_presiones(iv.AGUA_1,iv.TOLUENO,1.01325,r.t)
            self.assertGreater((Path(td)/'presiones.png').stat().st_size,5000)

if __name__=='__main__':unittest.main(verbosity=2)
