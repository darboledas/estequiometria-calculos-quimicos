# -*- coding: utf-8 -*-
"""Contrastes de invariancia de escala, redes y balances elementales.

Referencia analítica: conservación de átomos y de caudales por componente.
Los modelos de oxidación de azufre y nitrógeno se especifican expresamente.
"""
import contextlib
import io
import math
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "capitulo_11"))
sys.path.insert(0, str(ROOT / "capitulo_14"))
import balances_materia as bm
import combustion as cb


class EscaladoYRedes(unittest.TestCase):
    def _red_fuente(self, n, sink=1):
        return {
            'basis':'mass', 'complete_components':False,
            'components':['A'], 'units':[{'id':'X','source':{'A':str(-sink*n)}}],
            'streams':[
                {'id':'in','from':None,'to':'X','total':str(n),'fractions':{'A':'1'}},
                {'id':'out','from':'X','to':None},
            ],
        }

    def test_corriente_negativa_rechazada_sin_dependencia_de_unidades(self):
        for n in (100.,1.,1e-6,1e-9,1e-12):
            with self.subTest(cantidad=n):
                r = bm.resolver_red(self._red_fuente(n,sink=2))
                self.assertEqual(r['estado'],'no_fisico',r)

    def test_corriente_pequena_positiva_conserva_fracciones(self):
        for n in (100.,1.,1e-9,1e-12):
            with self.subTest(cantidad=n):
                r=bm.resolver_red(self._red_fuente(n,sink=0.2))
                self.assertEqual(r['estado'],'unico',r.get('motivo'))
                self.assertAlmostEqual(r['corrientes']['out']['total']/n,0.8,places=9)
                self.assertAlmostEqual(r['corrientes']['out']['fracciones']['A'],1.0,places=10)

    def test_red_reciclo_con_purga_conocida(self):
        cfg = {'basis':'mass', 'components':['A'],
               'units':[{'id':'mezclador'},{'id':'divisor'}],
               'streams':[
                    {'id':'entrada','from':None,'to':'mezclador','total':'100'},
                    {'id':'reciclo','from':'divisor','to':'mezclador','total':'30'},
                    {'id':'intermedio','from':'mezclador','to':'divisor'},
                    {'id':'producto','from':'divisor','to':None},
                ]}
        r=bm.resolver_red(cfg)
        self.assertEqual(r['estado'],'unico',r.get('motivo'))
        self.assertAlmostEqual(r['corrientes']['intermedio']['total'],130)
        self.assertAlmostEqual(r['corrientes']['producto']['total'],100)

    def test_red_reciclo_sin_especificar_es_indeterminada(self):
        cfg = {'basis':'mass', 'components':['A'],
               'units':[{'id':'mezclador'},{'id':'divisor'}],
               'streams':[
                    {'id':'entrada','from':None,'to':'mezclador','total':'100'},
                    {'id':'reciclo','from':'divisor','to':'mezclador'},
                    {'id':'intermedio','from':'mezclador','to':'divisor'},
                    {'id':'producto','from':'divisor','to':None},
                ]}
        self.assertEqual(bm.resolver_red(cfg)['estado'],'indeterminado')


class CombustionAtomica(unittest.TestCase):
    def test_metanol_metano_y_propano_escalan_con_cantidad(self):
        for f, unit_oxygen, prods in (
            ('CH4',2.0,{'CO2':1,'H2O':2}),
            ('CH4O',1.5,{'CO2':1,'H2O':2}),
            ('C3H8',5.0,{'CO2':3,'H2O':4}),
        ):
            for n in (1.,1e-8,1e-12):
                with self.subTest(formula=f,moles=n):
                    o2,p=cb.oxygen_stoich_formula(f,n,cb.ProductModel())
                    self.assertAlmostEqual(o2/n,unit_oxygen,places=9)
                    for sp,mol in prods.items():
                        self.assertAlmostEqual(p[sp]/n,mol,places=9)
                    residues=cb.balance_residuals({f:n,'O2':o2},p)
                    self.assertTrue(all(cb.balance_ok(a,b) for a,b,_ in residues.values()),residues)

    def test_azufre_seleccion_oxidos(self):
        for oxide,oxygen in [('SO2',4.5),('SO3',5.0)]:
            with self.subTest(oxide=oxide):
                m=cb.ProductModel(sulfur={oxide:1.})
                o,p=cb.oxygen_stoich_formula('C2H6S',1.0,m)
                self.assertAlmostEqual(o,oxygen)
                self.assertAlmostEqual(p[oxide],1)
                self.assertTrue(all(cb.balance_ok(a,b) for a,b,_ in cb.balance_residuals({'C2H6S':1,'O2':o},p).values()))

    def test_nitrogeno_a_n2_no_no2(self):
        for gas,oxygen,amount in [('N2',3.25,0.5),('NO',3.75,1.0),('NO2',4.25,1.0)]:
            with self.subTest(gas=gas):
                m=cb.ProductModel(nitrogen={gas:1.})
                o,p=cb.oxygen_stoich_formula('C2H5N',1,m)
                self.assertAlmostEqual(o,oxygen)
                self.assertAlmostEqual(p[gas],amount)
                self.assertTrue(all(cb.balance_ok(a,b) for a,b,_ in cb.balance_residuals({'C2H5N':1,'O2':o},p).values()))

    def test_nitrogeno_y_azufre_fracciones_conservan_atoms(self):
        m=cb.ProductModel(sulfur={'SO2':0.7,'SO3':0.3},nitrogen={'N2':0.5,'NO':0.25,'NO2':0.25})
        for n in (1.,1e-12):
            with self.subTest(cantidad=n):
                o,p=cb.oxygen_stoich_formula('C2H5NS',n,m)
                self.assertTrue(all(cb.balance_ok(a,b) for a,b,_ in cb.balance_residuals({'C2H5NS':n,'O2':o},p).values()))
                self.assertAlmostEqual(p['SO2']/n,0.7)
                self.assertAlmostEqual(p['N2']/n,0.25)

    def test_composicion_gaseosa_pequena_no_desaparece(self):
        for n in (1.0,1e-9,1e-12):
            with self.subTest(n=n):
                wet,dry,tw,td=cb.gas_compositions({'CO2':n,'H2O':2*n,'N2':3*n},3)
                self.assertAlmostEqual(wet['CO2'],1/6)
                self.assertAlmostEqual(dry['CO2'],1/4)
                self.assertAlmostEqual(tw/n,6)
                self.assertAlmostEqual(td/n,4)

    def test_oxigeno_deficiente_detectado_en_escala_micro(self):
        ox=cb.Oxidizer('puro',{'O2':1.0},999)
        for n in (1.0,1e-12):
            with self.subTest(n=n):
                with patch.object(cb,'read_choice',return_value='4'):
                    with patch.object(cb,'read_measurement',return_value=cb.Measurement(n,3)):
                        with self.assertRaisesRegex(cb.CombustionError,'insuficiente'):
                            cb.choose_supply(2*n,ox,complete_required=True)

    def test_limites_no_admiten_cantidades_negativas_micro(self):
        with patch('builtins.input',side_effect=['-1e-12','0']):
            with contextlib.redirect_stdout(io.StringIO()) as captured:
                m=cb.read_measurement('x',min_value=0)
        self.assertEqual(m.value,0)
        self.assertIn('>= 0',captured.getvalue())

    def test_no_finitos_y_distribuciones_invalidas(self):
        for vals in ({'SO2':float('nan')},{'SO2':float('inf')},{'SO2':-0.1,'SO3':1.1}):
            with self.subTest(vals=vals),self.assertRaises(cb.CombustionError):
                cb.validate_distribution(vals,'S')
        for n in (-1e-12,float('nan')):
            with self.subTest(n=n),self.assertRaises(cb.CombustionError):
                cb.complete_products_for_formula('CH4',n,cb.ProductModel())

    def test_balance_elemental_micro_no_oculta_perdida(self):
        self.assertFalse(cb.balance_ok(1e-12,0.0))
        self.assertTrue(cb.balance_ok(1e-12,1e-12*(1+1e-10)))


if __name__ == '__main__':
    unittest.main()
