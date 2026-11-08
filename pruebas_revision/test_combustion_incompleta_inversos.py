# -*- coding: utf-8 -*-
"""Verificación independiente de combustión incompleta, mezclas e inversos.

Referencias: balances de C, H, O, N; gas seco/húmedo; y relación lambda.
El oráculo analítico se calcula de forma independiente de las funciones bajo prueba.
"""
import contextlib
import io
import math
import re
import random
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'capitulo_14'))
import combustion as cb


def medida(n,sf=8):
    return cb.Measurement(n,sf,repr(n))


def cantidad(texto, etiqueta):
    patrones=[r'^\s*'+re.escape(etiqueta)+r':\s*([+\-0-9,eE.]+)\s*mol',
              r'^\s*'+re.escape(etiqueta)+r':\s*([+\-0-9,eE.]+)\b']
    for linea in texto.splitlines():
        for p in patrones:
            m=re.search(p,linea)
            if m:
                return float(m.group(1).replace(',','.'))
    raise AssertionError('No se encontró la cantidad de '+etiqueta+' en '+texto[-3000:])


def ejecutar_incompleta(n, o2_real, *, formula='CH4', conv=80.0, co2_fraccion=75.0):
    ms=[medida(n),medida(conv),medida(co2_fraccion),medida(o2_real)]
    b=io.StringIO()
    with patch('builtins.input',return_value=formula),\
         patch.object(cb,'read_measurement',side_effect=ms),\
         patch.object(cb,'choose_oxidizer',return_value=cb.Oxidizer('oxígeno puro',{'O2':1.0},999)),\
         patch.object(cb,'read_choice',return_value='3'),\
         contextlib.redirect_stdout(b):
        cb.option5_incomplete()
    return b.getvalue()


class CombustionIncompleta(unittest.TestCase):
    def test_microcombustion_misma_estequiometria(self):
        # CH4: 80 % reacciona; del C reaccionado 75 % a CO2, 25 % a CO.
        # En 1 mol alimentado: CO2=0.6, CO=0.2, H2O=1.6,
        # CH4 no reaccionado=0.2; O2 consumido=1.5, sobrante=0.3.
        for n in (1.0, 1e-6, 1e-9, 1e-12):
            with self.subTest(n=n):
                texto=ejecutar_incompleta(n,1.8*n)
                self.assertNotIn('[ERROR]',texto)
                self.assertAlmostEqual(cantidad(texto,'CH4')/n,0.2,places=6)
                self.assertAlmostEqual(cantidad(texto,'CO2')/n,0.6,places=6)
                self.assertAlmostEqual(cantidad(texto,'CO')/n,0.2,places=6)
                self.assertAlmostEqual(cantidad(texto,'H2O')/n,1.6,places=6)
                self.assertAlmostEqual(cantidad(texto,'O2')/n,0.3,places=6)

    def test_oxigeno_insuficiente_a_cualquier_escala(self):
        for n in (1.0,1e-12):
            with self.subTest(n=n),self.assertRaisesRegex(cb.CombustionError,'no basta'):
                ejecutar_incompleta(n,1.4*n)

    def test_distribucion_con_consumo_negativo_oxigeno(self):
        # En CH2O8, incluso si todo C -> CO2 y H -> H2O, sobran átomos O.
        for n in (1.0,1e-12):
            with self.subTest(n=n),self.assertRaisesRegex(cb.CombustionError,'negativo'):
                ejecutar_incompleta(n,0.0,formula='CH2O8',conv=100,co2_fraccion=100)

    def test_cifras_significativas_en_valores_pequenos(self):
        self.assertNotEqual(cb.format_sig(1.23e-12,3),'0')
        self.assertEqual(cb.format_sig(0.0,3),'0')
        self.assertEqual(cb.min_sf(medida(1e-12,sf=2),medida(5.0,sf=5)),2)

    def test_mezcla_con_inertes_y_exceso_aire(self):
        # 2 CH4 + C2H6 + 0.4 CO2 + 0.8 N2: O2=7.5,
        # CO2=4.4; H2O=7.0. Inertes pasan intactos.
        fuel=[('CH4',2.0,True),('C2H6',1.0,True),('CO2',0.4,False),('N2',0.8,False)]
        o2,productos=cb.complete_products_for_mixture(fuel,cb.ProductModel())
        self.assertAlmostEqual(o2,7.5)
        self.assertAlmostEqual(productos['CO2'],4.4)
        self.assertAlmostEqual(productos['H2O'],7.0)
        self.assertAlmostEqual(productos['N2'],0.8)
        suministro=1.2*o2
        entrada={sp:0.0 for sp in ('CH4','C2H6','CO2','N2','O2')}
        for f,n,_ in fuel:entrada[f]+=n
        entrada['O2']+=suministro
        entrada['N2']+=suministro*79/21
        salida=dict(productos)
        salida['N2']+=suministro*79/21
        salida['O2']=suministro-o2
        r=cb.balance_residuals(entrada,salida)
        self.assertTrue(all(cb.balance_ok(a,b) for a,b,_ in r.values()),r)
        seco={k:v for k,v in salida.items() if k!='H2O'}
        fraccion_co2=seco['CO2']/sum(seco.values())
        self.assertAlmostEqual(fraccion_co2,4.4/sum(seco.values()))

    def test_orsat_analitico(self):
        texto=io.StringIO()
        with patch.object(cb,'read_choice',return_value='2'),\
             patch.object(cb,'read_measurement',side_effect=list(map(medida,[100.0,88.0,83.0,81.0]))),\
             patch.object(cb,'read_yes_no',return_value=False),\
             contextlib.redirect_stdout(texto):
            cb.option6_analysis()
        salida=texto.getvalue()
        for especie,porcentaje in [('CO2',12),('O2',5),('CO',2),('N2',81)]:
            m=re.search(r'^\s*'+especie+r':\s*([0-9,]+) %',salida,re.MULTILINE)
            self.assertIsNotNone(m,especie)
            self.assertAlmostEqual(float(m.group(1).replace(',','.')),porcentaje,places=5)


class InversionesConBalancesDirectos(unittest.TestCase):
    def test_matriz_composicion_indeterminada(self):
        estado,sol=cb.solve_linear_system([[1,2,2],[2,4,4]],[5,10])
        self.assertEqual(estado,'underdetermined')
        self.assertIsNone(sol)

    def test_matriz_incompatible(self):
        estado,sol=cb.solve_linear_system([[1,1],[1,1]],[2,3])
        self.assertEqual(estado,'inconsistent')
        self.assertIsNone(sol)

    def test_inversa_especies_conocidas_tres_componentes(self):
        # CH4 (2 mol), C2H6 (1 mol), C2H4 (3 mol):
        # CO2=10 mol, H2O=13 mol, combustible=6 mol.
        texto=io.StringIO()
        with patch.object(cb,'read_int',side_effect=[3,3]),\
             patch('builtins.input',side_effect=['CH4','C2H6','C2H4']),\
             patch.object(cb,'read_choice',side_effect=['1','2','4']),\
             patch.object(cb,'read_measurement',side_effect=list(map(medida,[10,13,6]))),\
             patch.object(cb,'read_ratio_constraints',return_value=([],[],[],[])),\
             contextlib.redirect_stdout(texto):
            cb.inverse_known_components_observables()
        salida=texto.getvalue()
        self.assertNotIn('[ERROR]',salida)
        for f,val in [('CH4',2.0),('C2H6',1.0),('C2H4',3.0)]:
            self.assertAlmostEqual(cantidad(salida,f),val,places=5)

    def test_inversa_seca_con_inerte_n2(self):
        # Mezcla conocida: CH4=2, C2H6=1, N2 de combustible=0.5.
        # Aire con lambda 1.2 y 21% O2; base seca convertida a 100 mol.
        o2st=2*2+3.5
        o2in=o2st*1.2
        dry={'CO2':4.0,'O2':o2in-o2st,'N2':o2in*79/21+0.5}
        total=sum(dry.values()); comp={k:v/total for k,v in dry.items()}
        b=io.StringIO()
        with patch.object(cb,'read_analysis_composition',return_value=('seca',comp,[medida(comp['CO2']*100)],[])),\
             patch.object(cb,'read_int',return_value=3),\
             patch('builtins.input',side_effect=['CH4','C2H6','N2']),\
             patch.object(cb,'read_yes_no',side_effect=[True,True,False,False]),\
             patch.object(cb,'read_ratio_constraints',return_value=([[1,-2,0]],[0.0],[],[])),\
             contextlib.redirect_stdout(b):
            cb.inverse_complete_dry_known_components()
        out=b.getvalue()
        self.assertNotIn('[ERROR]',out)
        scale=100/total
        for f,n in [('CH4',2),('C2H6',1),('N2',0.5)]:
            self.assertAlmostEqual(cantidad(out,f),float(cb.format_sig(n*scale,3).replace(',','.')),places=8)

    def test_inversa_desde_co2_seco_y_lambda(self):
        n1,n2,lam=2,1,1.2
        o2st=2*n1+3.5*n2
        co2=n1+2*n2
        total=co2+(lam-1)*o2st+lam*o2st*79/21
        percent=100*co2/total
        out=io.StringIO()
        with patch.object(cb,'read_measurement',side_effect=[medida(percent),medida(lam)]),\
             patch.object(cb,'read_choice',return_value='2'),\
             patch.object(cb,'read_int',return_value=2),\
             patch('builtins.input',side_effect=['CH4','C2H6']),\
             patch.object(cb,'read_ratio_constraints',return_value=([],[],[],[])),\
             contextlib.redirect_stdout(out):
            cb.inverse_dry_co2_known_air_factor()
        txt=out.getvalue()
        self.assertNotIn('[ERROR]',txt)
        for f,n in [('CH4',n1),('C2H6',n2)]:
            self.assertAlmostEqual(cantidad(txt,f)/(n*100/total),1,delta=0.0008)

    def test_inversa_binaria_con_cantidades_micro(self):
        # 2e-12 mol CH4 y 1e-12 mol C2H6: C=4e-12 y H=14e-12.
        b=io.StringIO()
        with patch('builtins.input',side_effect=['CH4','C2H6']),\
             patch.object(cb,'read_choice',return_value='1'),\
             patch.object(cb,'read_measurement',side_effect=[medida(4e-12),medida(14e-12)]),\
             contextlib.redirect_stdout(b):
            cb.inverse_binary_fuel()
        out=b.getvalue()
        self.assertNotIn('[ERROR]',out)
        self.assertAlmostEqual(cantidad(out,'CH4')/1e-12,2,places=5)
        self.assertAlmostEqual(cantidad(out,'C2H6')/1e-12,1,places=5)

    def test_inversa_pura_microsuministro(self):
        # 1e-12 mol CH4 implica 2e-12 mol O2 estequiometrico.
        b=io.StringIO()
        with patch('builtins.input',return_value='CH4'),\
             patch.object(cb,'choose_product_model',return_value=(cb.ProductModel(),[],[])),\
             patch.object(cb,'read_measurement',side_effect=[medida(2e-12),medida(2.4e-12)]),\
             patch.object(cb,'choose_oxidizer',return_value=cb.Oxidizer('O2 puro',{'O2':1.0},999)),\
             patch.object(cb,'read_choice',return_value='2'),\
             contextlib.redirect_stdout(b):
            cb.inverse_pure_from_stoich_o2()
        self.assertIn('20,',b.getvalue())
        self.assertNotIn('nan',b.getvalue().lower())
        self.assertNotIn('[ERROR]',b.getvalue())

    def test_inversa_pura_oxigeno_nulo_rechazado(self):
        with patch('builtins.input',return_value='CH4'),\
             patch.object(cb,'choose_product_model',return_value=(cb.ProductModel(),[],[])),\
             patch.object(cb,'read_measurement',return_value=medida(0.0)):
            with self.assertRaisesRegex(cb.CombustionError,'estrictamente positiva'):
                cb.inverse_pure_from_stoich_o2()

    def test_multicomponente_aleatorio_150_casos_reconstruccion(self):
        # Cuatro componentes (dos reactivos, dos inertes) y cinco incógnitas,
        # incluidos moles de O2 de aire. Dos relaciones adicionales hacen
        # identificable el problema. El vector esperado se construye sin
        # utilizar el solucionador inverso.
        rnd=random.Random(20261107)
        air_ratio=79/21
        for i in range(150):
            n1,n2,nN2,nCO2=[rnd.uniform(0.2,12) for _ in range(4)]
            lam=rnd.uniform(1.0,2.0)
            oxygen_theor=2*n1+3.5*n2
            o2in=lam*oxygen_theor
            y_co2=n1+2*n2+nCO2
            y_o2=o2in-oxygen_theor
            y_n2=nN2+air_ratio*o2in
            matrix=[
                [1,2,0,1,0],
                [-2,-3.5,0,0,1],
                [0,0,1,0,air_ratio],
                [1,-n1/n2,0,0,0],
                [0,0,1,-nN2/nCO2,0],
            ]
            status,sol=cb.solve_linear_system(matrix,[y_co2,y_o2,y_n2,0,0])
            with self.subTest(indice=i):
                self.assertEqual(status,'unique')
                for got,expected in zip(sol,[n1,n2,nN2,nCO2,o2in]):
                    self.assertAlmostEqual(got/expected,1.0,delta=1e-9)

    def test_inversa_especies_insuficientes(self):
        with patch.object(cb,'read_int',side_effect=[3,1]),\
             patch('builtins.input',side_effect=['CH4','C2H6','C2H4']),\
             patch.object(cb,'read_choice',return_value='1'),\
             patch.object(cb,'read_measurement',return_value=medida(10)),\
             patch.object(cb,'read_ratio_constraints',return_value=([],[],[],[])):
            with self.assertRaisesRegex(cb.CombustionError,'no son suficientes'):
                cb.inverse_known_components_observables()


if __name__=='__main__': unittest.main()
