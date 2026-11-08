"""Casos independientes de redes y combustión inversa.

Sin dependencias externas; se ejecuta desde la raíz del repositorio:
    python -m unittest discover -s pruebas_revision -v
"""
import contextlib
import io
import math
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'capitulo_11'))
sys.path.insert(0, str(ROOT / 'capitulo_14'))
import balances_materia as bm
import combustion as cb


class RedesDeMateria(unittest.TestCase):
    def test_identificadores_numericos_en_red_de_dos_unidades(self):
        cfg = {
            'basis': 'mass', 'components': ['A', 'B'],
            'units': [{'id': 1}, {'id': 2}],
            'streams': [
                {'id': 10, 'from': None, 'to': 1, 'total': '100,0',
                 'fractions': {'A': '0,40', 'B': '0,60'}},
                {'id': 20, 'from': 1, 'to': 2},
                {'id': 30, 'from': 2, 'to': None},
            ],
        }
        res = bm.resolver_red(cfg)
        self.assertEqual(res['estado'], 'unico', res.get('motivo'))
        for sid in ['10', '20', '30']:
            with self.subTest(corriente=sid):
                self.assertAlmostEqual(res['corrientes'][sid]['total'], 100.0, places=8)
                self.assertAlmostEqual(res['corrientes'][sid]['componentes']['A'], 40.0, places=8)
                self.assertAlmostEqual(res['corrientes'][sid]['componentes']['B'], 60.0, places=8)

    def test_identificadores_mixtos_cadena_y_numero(self):
        cfg = {
            'basis': 'mass', 'components': ['A'],
            'units': [{'id': 1}],
            'streams': [
                {'id': 'in', 'from': None, 'to': '1', 'total': '9,0'},
                {'id': 'out', 'from': 1, 'to': None},
            ],
        }
        res = bm.resolver_red(cfg)
        self.assertEqual(res['estado'], 'unico', res.get('motivo'))
        self.assertAlmostEqual(res['corrientes']['out']['total'], 9.0)

    def test_identificadores_duplicados_tras_normalizacion(self):
        cfg = {'components': ['A'], 'units': [{'id': 1}, {'id': '1'}],
               'streams': [{'id': 1, 'from': None, 'to': 1}]}
        with self.assertRaises(bm.ErrorBalance):
            bm.resolver_red(cfg)

    def test_red_reactiva_molar_de_dos_etapas(self):
        # Entrada 10 A, reactor A -> B con avance 4, separador ideal sin pérdidas.
        cfg = {
            'basis': 'molar', 'components': ['A', 'B'],
            'units': [{'id': 1, 'reactions': [{'stoich': {'A': -1, 'B': 1}, 'extent': '4,00'}]},
                      {'id': 2}],
            'streams': [
                {'id': 1, 'from': None, 'to': 1, 'total': '10,0', 'fractions': {'A': '1'}},
                {'id': 2, 'from': 1, 'to': 2},
                {'id': 3, 'from': 2, 'to': None},
            ],
        }
        r = bm.resolver_red(cfg)
        self.assertEqual(r['estado'], 'unico', r.get('motivo'))
        self.assertAlmostEqual(r['corrientes']['3']['componentes']['A'], 6)
        self.assertAlmostEqual(r['corrientes']['3']['componentes']['B'], 4)
        self.assertAlmostEqual(r['corrientes']['3']['total'], 10)

    def test_dato_no_fisico_no_se_acepta(self):
        cfg = {'basis': 'mass', 'components': ['A'], 'units': [{'id': 'R'}],
               'streams': [{'id': 'in', 'from': None, 'to': 'R', 'total': '-3'},
                           {'id': 'out', 'from': 'R', 'to': None}]}
        with self.assertRaises(bm.ErrorBalance):
            bm.resolver_red(cfg)


class CombustionInversa(unittest.TestCase):
    def test_parser_rechaza_grupos_vacios_y_subindices_nulos(self):
        for f in ['Fe()2', 'CH0', 'C0H4', 'Mg(OH)0', '()', 'H2O)', '(C2H6']:
            with self.subTest(formula=f), self.assertRaises(cb.CombustionError):
                cb.parse_formula(f)

    def test_parser_conserva_subindices_y_parentesis_validos(self):
        self.assertEqual(cb.parse_formula('Ca(OH)2'), {'Ca': 1., 'O': 2., 'H': 2.})
        self.assertEqual(cb.parse_formula('C6H12O6'), {'C': 6., 'H': 12., 'O': 6.})

    def test_coeficientes_oxidacion_metanol_y_metano(self):
        ch4 = cb.cho_complete_coeffs('CH4')
        ch3oh = cb.cho_complete_coeffs('CH4O')
        self.assertAlmostEqual(ch4['CO2'], 1)
        self.assertAlmostEqual(ch4['H2O'], 2)
        self.assertAlmostEqual(ch4['O2'], 2)
        self.assertAlmostEqual(ch3oh['CO2'], 1)
        self.assertAlmostEqual(ch3oh['H2O'], 2)
        self.assertAlmostEqual(ch3oh['O2'], 1.5)

    def test_sistema_inverso_binario_exacto(self):
        # 2 mol CH4 + 3 mol C2H6 -> 8 mol CO2 y 13 mol H2O.
        a = [[1., 2.], [2., 3.], [2., 3.5]]
        b = [8., 13., 14.5]
        status, sol = cb.solve_linear_system(a, b)
        self.assertEqual(status, 'unique')
        self.assertAlmostEqual(sol[0], 2., places=8)
        self.assertAlmostEqual(sol[1], 3., places=8)

    def test_sistemas_inversos_a_escalas_muy_diferentes(self):
        # Un nanomol o picomol no implica ausencia de ecuación.
        for scale in (1.e-12, 1.e-6, 1.e6, 1.e12):
            with self.subTest(scale=scale):
                A = [[scale, 2*scale], [3*scale, 4*scale]]
                b = [5*scale, 11*scale]
                status, sol = cb.solve_linear_system(A, b)
                self.assertEqual(status, 'unique')
                self.assertAlmostEqual(sol[0], 1.0, places=7)
                self.assertAlmostEqual(sol[1], 2.0, places=7)

    def test_sistemas_inversos_con_entrada_no_finita(self):
        for A, b in [([[float('nan')]], [1.]), ([[1.]], [float('inf')])]:
            with self.assertRaises(cb.CombustionError):
                cb.solve_linear_system(A, b)

    def test_datos_redundantes_incompatibles_e_insuficientes(self):
        status, _ = cb.solve_linear_system([[1., 2.]], [8.])
        self.assertEqual(status, 'underdetermined')
        status, _ = cb.solve_linear_system([[1., 2.], [2., 4.]], [8., 17.])
        self.assertEqual(status, 'inconsistent')

    def test_opcion_inversa_7b_ejecucion_interactiva(self):
        # Dos sustancias candidatas, observables independientes CO2 y H2O.
        inputs = ['2', 'CH4', 'C2H6', '2', '1', '8,00', '2', '13,0', '0']
        with patch('builtins.input', side_effect=inputs):
            with contextlib.redirect_stdout(io.StringIO()) as buf:
                cb.inverse_known_components_observables()
        out = buf.getvalue()
        self.assertIn('CO2 producido:', out)
        self.assertIn('H2O producida:', out)
        self.assertIn('CH4:', out)
        self.assertIn('C2H6:', out)
        self.assertIn('14,5', out.replace('.', ','))

    def test_opcion_inversa_7b_rechaza_indeterminacion(self):
        inputs = ['2', 'CH4', 'C2H6', '1', '1', '8', '0']
        with patch('builtins.input', side_effect=inputs):
            with contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaisesRegex(cb.CombustionError, 'suficientes'):
                    cb.inverse_known_components_observables()

    def test_inversa_hc_a_partir_de_gas_seco(self):
        # Combustión completa CH4 con aire del modelo (21/79) y sin exceso.
        n2 = 2 * cb.DEFAULT_AIR_N2 / cb.DEFAULT_AIR_O2
        tot = 1 + n2
        comp = {'CO2': 1 / tot, 'N2': n2 / tot, 'O2': 0.0, 'CO': 0.0}
        with patch.object(cb, 'read_analysis_composition', return_value=('seca', comp, [], [])):
            with patch.object(cb, 'read_choice', return_value='1'):
                with contextlib.redirect_stdout(io.StringIO()) as buf:
                    cb.inverse_hc_from_dry()
        out = buf.getvalue()
        # 4 átomos H por átomo C y lambda 1 (según aire idealizado).
        self.assertIn('Relación atómica H/C:', out)
        self.assertIn('4,00', out.replace('.', ','))
        self.assertIn('Factor de aire lambda:', out)


if __name__ == '__main__':
    unittest.main()
