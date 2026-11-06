"""Pruebas reproducibles. Ejecutar desde la carpeta principal:
    python -m unittest discover -s pruebas -v
"""
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from xml.etree import ElementTree

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import cap13_apoyo as apoyo
import balance_una_reaccion as s1
import balance_varias_reacciones as s2


class BalanceCap13Tests(unittest.TestCase):
    def test_balances_formula_penicilina(self):
        n=['C16H18N2O4S','H2O','C8H12N2O3S','C8H8O2']
        estado,_=apoyo.comprobar_formulas(n,[[-1],[-1],[1],[1]])
        self.assertEqual(estado,'correcto')
        estado,_=apoyo.comprobar_formulas(n,[[-1],[-1],[1],[2]])
        self.assertEqual(estado,'incorrecto')

    def test_grupos_formula_quimica(self):
        self.assertEqual(apoyo.formula_elemental('Fe2(SO4)3'),{'Fe':2,'S':3,'O':12})
        self.assertEqual(apoyo.formula_elemental('Ca(OH)2'),{'Ca':1,'O':2,'H':2})
        self.assertIsNone(apoyo.formula_elemental('A'))
        estado,_=apoyo.comprobar_formulas(['A','B','C'],[[-1],[1],[0]])
        self.assertEqual(estado,'no_verificado')

    def test_semicontinuo_farmaceutico_B13(self):
        n0=s1.parse_q_text('1,20')
        alim=s1.q_mul(s1.parse_q_text('0,250'),s1.parse_q_text('20,0'))
        total=s1.q_add(n0,alim)
        xi=s1.q_sub(total,s1.parse_q_text('0,400'))
        self.assertEqual(s1.format_q(total),'6,20')
        self.assertEqual(s1.format_q(xi),'5,80')
        self.assertEqual(s1.format_q(s1.q_div(xi,s1.parse_q_text('20,0'))),'0,290')

    def test_una_reaccion_ejemplo_13_4(self):
        sp=[{'name':'C2H4','nu':Decimal(-1)}, {'name':'H2','nu':Decimal(-1)},
            {'name':'C2H6','nu':Decimal(1)}]
        arr=[s1.parse_q_text('12,0'),s1.parse_q_text('15,0'),s1.Q.exact_value(0)]
        X=s1.q_div(s1.parse_q_text('80,0'),s1.Q.exact_value(100))
        xi=s1.q_mul(arr[0],X)
        self.assertEqual(s1.format_q(xi),'9,60')
        ds, fin=s1.calculate_final(sp,arr,xi)
        self.assertEqual([str(q.value) for q in fin],['2.40','5.40','9.60'])
        # En las restas se conserva la posición decimal menos precisa.
        self.assertEqual(s1.format_q(fin[0]),'2,4')

    def test_independencia_de_reacciones(self):
        self.assertEqual(s2.matrix_rank([[-1,0,-1],[1,-1,0],[0,1,1]]),2)
        self.assertEqual(s2.matrix_rank([[-1,-1],[1,0],[0,2]]),2)

    def test_ejemplo_13_5_dos_reacciones(self):
        sp=['C2H5OH','C2H4','C2H5OC2H5','H2O']
        nu=[[-1,-2],[1,0],[0,1],[1,1]]
        inicial=[s2.parse_q_text('10,0')]+[s2.Q.exact_value(0)]*3
        restricciones=[]
        s2.add_constraint(restricciones,[1,0],s2.parse_q_text('2,00'),'eteno')
        s2.add_constraint(restricciones,[0,1],s2.parse_q_text('1,50'),'eter')
        valores,cifras,_=s2.solve_constraints(restricciones,2)
        self.assertEqual(valores,[Decimal('2.00'),Decimal('1.50')])
        self.assertEqual(cifras,[3,3])
        contrib,fin=s2.calculate_final(sp,nu,inicial,[s2.q_from_sf(v,cifras[i]) for i,v in enumerate(valores)])
        self.assertEqual([q.value for q in fin],[Decimal(5),Decimal(2),Decimal('1.50'),Decimal('3.50')])
        self.assertEqual(s2.format_q(s2.q_sum(fin)),'12,0')

    def test_individualidad_de_precision(self):
        r=[]
        s2.add_constraint(r,[1,0],s2.parse_q_text('2,00'),'resultado1')
        s2.add_constraint(r,[0,1],s2.parse_q_text('1,5'),'resultado2')
        _,sfs,_=s2.solve_constraints(r,2)
        self.assertEqual(sfs,[3,2])

    def test_precision_sistema_acoplado(self):
        # xi1 = 2,00 y xi2 = 1,5: solo xi2 depende de la segunda medida.
        r = []
        s2.add_constraint(r, [1, 0], s2.parse_q_text('2,00'), 'xi1')
        s2.add_constraint(r, [1, 1], s2.parse_q_text('3,5'), 'suma')
        valores, cifras, _ = s2.solve_constraints(r, 2)
        self.assertEqual(valores, [Decimal('2.00'), Decimal('1.50')])
        self.assertEqual(cifras, [3, 2])

    def test_precision_restricciones_compartidas(self):
        # Ambas extensiones dependen de la medida menos precisa.
        r = []
        s2.add_constraint(r, [1, 1], s2.parse_q_text('3,5'), 'suma')
        s2.add_constraint(r, [1, -1], s2.parse_q_text('0,50'), 'diferencia')
        _, cifras, _ = s2.solve_constraints(r, 2)
        self.assertEqual(cifras, [2, 2])

    def test_falta_datos(self):
        r=[]
        s2.add_constraint(r,[1,1],s2.parse_q_text('5,00'),'unica')
        with self.assertRaisesRegex(ValueError,'Faltan datos'):
            s2.solve_constraints(r,2)

    def test_datos_incompatibles(self):
        r=[]
        s2.add_constraint(r,[1],s2.parse_q_text('2,00'),'uno')
        s2.add_constraint(r,[1],s2.parse_q_text('4,00'),'otro')
        with self.assertRaisesRegex(ValueError,'no son simultáneamente compatibles'):
            s2.solve_constraints(r,1)

    def test_esquemas_y_exportaciones(self):
        data={'script':'prueba','descripcion':'Balance de prueba', 'tipo_sistema':'continuo',
              'reacciones':['2 A + B → 3 C'], 'especies':['A','B','C'],
              'unidad':'mol min^-1', 'disponible':['4,00','2,00','0'],
              'final':['2,00','1,00','3,00'],
              'antes_sin_redondeo':['4','2','0'],
              'final_sin_redondeo':['2','1','3'],
              'deltas_etiquetas':['-2,00','-1,00','3,00'],
              'extensiones':['xi_dot = 1,00 mol min^-1'],
              'validacion_estequiometrica':'No comprobado'}
        with tempfile.TemporaryDirectory() as td:
            files=apoyo.exportar(data,2,td)
            self.assertEqual(len(files),5)
            for f in files:
                self.assertTrue(Path(f).is_file())
            for f in files:
                if f.endswith('.svg'):
                    ElementTree.parse(f)
            self.assertIn('mol min^-1',Path(next(f for f in files if f.endswith('.csv'))).read_text('utf-8-sig'))

if __name__=='__main__':
    unittest.main()
