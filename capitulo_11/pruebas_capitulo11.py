#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pruebas reproducibles con respuestas calculadas independientemente del código.

Incluye ejemplos 11.1–11.10 disponibles y ejercicios B.1–B.16 y C.1–C.11
(para preguntas cualitativas se comprueban magnitudes/casos de cierre del motor;
no se automatiza una valoración pedagógica de respuestas redactadas).
Ejecutar: python pruebas_capitulo11.py
"""
import json
from pathlib import Path
import tempfile
import unittest

from balances_materia import (
    Dato, Ecuacion, ErrorBalance, add_datos, base_masa_a_molar, base_molar_a_masa,
    base_humeda_a_seca, base_seca_a_humeda,
    caudal_gas, caudales_componentes, comprobar_residuos, convierte_volumen_gas,
    cstr_analitico, dato, guardar_datos, inventario_lineal, menor_cifra,
    mezclar_concentraciones, mul_datos, normaliza, numero, resolver_lineal,
    resolver_red, simular_mezcla,
)

DIR=Path(__file__).resolve().parent/'ejemplos'

def archivo(name):return json.loads((DIR/name).read_text(encoding='utf-8'))


class MotorYPrecision(unittest.TestCase):
    def test_precision_escritura(self):
        self.assertEqual(dato('120,0').cifras,4)
        self.assertIsNone(dato('120').cifras)
        self.assertEqual(dato('120{3}').cifras,3)
        self.assertEqual(dato('2,50e2').cifras,3)
        self.assertEqual(dato('0,0800').cifras,3)
        self.assertEqual(numero(250,3),'2,50·10^2')
        self.assertEqual(numero(19.725,3),'19,7')
        self.assertEqual(numero(0.427995,3),'0,428')
        self.assertEqual(numero(0,3),'0,00')
        self.assertEqual(numero(135,4),'135,0')

    def test_precision_operaciones(self):
        self.assertEqual(add_datos(dato('120,0'),dato('80,0')).cifras,4)
        self.assertEqual(mul_datos(dato('25,0'),dato('0,789')).cifras,3)
        self.assertEqual(menor_cifra(dato('0'),dato('20,0')),3)
        self.assertEqual(numero(591.75,3),'592')

    def test_entradas_erroneas(self):
        for invalido in ['NaN','Infinity','1+2','', '5%']:
            with self.subTest(invalido=invalido),self.assertRaises(ErrorBalance):dato(invalido)
        with self.assertRaises(ErrorBalance):caudales_componentes(20,[.2,.9])
        with self.assertRaises(ErrorBalance):caudales_componentes(-5,[.5,.5])
        with self.assertRaises(ErrorBalance):base_masa_a_molar([2,1],[18,-1])
        with self.assertRaises(ErrorBalance):caudal_gas(0,1,298)
        with self.assertRaises(ErrorBalance):convierte_volumen_gas(1,101325,298,101325,0)

    def test_gases(self):
        self.assertAlmostEqual(caudal_gas(101325,0.001,298.15),0.0408744,places=5)
        self.assertAlmostEqual(convierte_volumen_gas(1,100000,300,200000,300),.5)
        self.assertAlmostEqual(convierte_volumen_gas(1,100000,300,100000,600),2)
        self.assertAlmostEqual(convierte_volumen_gas(1,100000,300,100000,300,1,1.2),1.2)

    def test_bases_gas_humeda_seca(self):
        seca=base_humeda_a_seca([.18,.72,.10],2)
        self.assertAlmostEqual(seca[0],.20)
        self.assertAlmostEqual(seca[1],.80)
        humeda=base_seca_a_humeda([.20,.80],.10)
        for got,want in zip(humeda,[.18,.72,.10]):self.assertAlmostEqual(got,want)
        with self.assertRaises(ErrorBalance):base_humeda_a_seca([0,1],1)

    def test_rank_no_soluble(self):
        ind=resolver_lineal(['x','y'],[Ecuacion([1,1],3,'balance')])
        self.assertEqual((ind.estado,ind.grados_libertad),('indeterminado',1))
        self.assertEqual(ind.valores,{})
        inc=resolver_lineal(['x'],[Ecuacion([1],3,'a'),Ecuacion([1],4,'b')])
        self.assertEqual((inc.estado,inc.rango_ampliada),('incompatible',2))
        uni=resolver_lineal(['x','y'],[Ecuacion([1,1],3,'a'),Ecuacion([1,-1],1,'b')])
        self.assertEqual(uni.estado,'unico')
        self.assertAlmostEqual(uni.valores['x'],2)
        self.assertAlmostEqual(uni.valores['y'],1)
        redun=resolver_lineal(['x'],[Ecuacion([1],2,'a'),Ecuacion([2],4,'2a')])
        self.assertEqual(redun.redundantes,1)

    def test_inventario_y_transitorio(self):
        a=inventario_lineal(10,[(20,0)],[(8,0)],3)
        self.assertAlmostEqual(a[-1]['inventario'],46)
        a=inventario_lineal(10,[(2,1)],[(2,0)],4)
        self.assertAlmostEqual(a[-1]['inventario'],18)
        with self.assertRaises(ErrorBalance):inventario_lineal(2,[],[(3,0)],1)
        c=cstr_analitico(100,25,0,10,4)
        self.assertAlmostEqual(c[-1]['concentracion'],10*(1-2.718281828459045**(-1)),places=6)
        a=simular_mezcla({'V0':100.,'C0':0.,'Cin':10.,'qin':[25,0],
                            'qout':[25,0],'tf':4,'source':0},1e-9)
        self.assertAlmostEqual(a[-1]['concentracion'],c[-1]['concentracion'],delta=1e-6)
        self.assertAlmostEqual(a[-1]['volumen'],100,places=8)
        with self.assertRaises(ErrorBalance):simular_mezcla({'V0':2,'C0':1,'Cin':0,
            'qin':[0,0],'qout':[10,0],'tf':1})
        with self.assertRaises(ErrorBalance):simular_mezcla({'V0':1,'C0':1,'Cin':0,
            'qin':[1,0],'qout':[1,0],'tf':1},1e-15)
        with tempfile.TemporaryDirectory() as td:
            p=guardar_datos(Path(td)/'valores.csv',a)
            self.assertIn('concentracion',p.read_text(encoding='utf-8-sig'))

    def test_sistemas_imposibles(self):
        r=mezclar_concentraciones([[1,4]],[8],100)
        self.assertEqual(r.estado,'no_fisico')
        r=mezclar_concentraciones([[1,3]], [2],100)
        self.assertEqual(r.estado,'unico')
        self.assertAlmostEqual(r.valores['V_1'],50)
        r=mezclar_concentraciones([[1,3,5]], [2],100)
        self.assertEqual(r.estado,'indeterminado')

    def test_red_molar_con_reaccion(self):
        cfg={'basis':'molar','components':['A','B','C'],
         'units':[{'id':'R','reactions':[{'stoich':{'A':-1,'B':-1,'C':1},'extent':'4,00'}]}],
         'streams':[{'id':'e','from':None,'to':'R','total':'20,0',
                     'fractions':{'A':'0,5','B':'0,5','C':'0'}},
                    {'id':'s','from':'R','to':None}]}
        r=resolver_red(cfg)
        self.assertEqual(r['estado'],'unico')
        self.assertAlmostEqual(r['corrientes']['s']['total'],16)
        self.assertAlmostEqual(r['corrientes']['s']['componentes']['C'],4)
        self.assertAlmostEqual(r['corrientes']['s']['componentes']['A'],6)

    def test_red_masa_reaccion(self):
        cfg={'basis':'mass','components':['A','B'],'units':[{'id':'R',
         'reactions':[{'stoich':{'A':-1,'B':1}}]}],
         'streams':[{'id':'e','from':None,'to':'R','total':'100,0',
                     'fractions':{'A':'1'}},
                    {'id':'s','from':'R','to':None,'fractions':{'A':'0'}}]}
        r=resolver_red(cfg)
        self.assertEqual(r['estado'],'unico')
        self.assertAlmostEqual(r['valores']['extent:R:1'],100.)
        self.assertAlmostEqual(r['corrientes']['s']['componentes']['B'],100.)

    def test_reaccion_masa_incorrecta(self):
        cfg={'basis':'mass','components':['A','B'],'units':[{'id':'R',
         'reactions':[{'stoich':{'A':-1,'B':2},'extent':'1'}]}],
         'streams':[{'id':'e','from':None,'to':'R'},{'id':'s','from':'R','to':None}]}
        with self.assertRaises(ErrorBalance):resolver_red(cfg)


class EjemplosDelCapitulo(unittest.TestCase):
    def test_ejemplo_11_1_acumulacion(self):
        self.assertEqual(250-190,60)
        self.assertEqual((250-190)*10,600)

    def test_ejemplo_11_2_etanol_sin_redondeos_intermedios(self):
        qm=.789*25
        self.assertAlmostEqual(qm,19.725)
        qn=qm/46.07
        self.assertAlmostEqual(qn,.42815,delta=0.0001)
        self.assertEqual(numero(qm,3),'19,7')
        self.assertEqual(numero(qn,3),'0,428')
        self.assertEqual(numero(qm*30,3),'592')
        self.assertEqual(numero(qn*30,3),'12,8')

    def test_ejemplo_11_3_glucosa_agua(self):
        r=base_masa_a_molar([1.80,10.20],[180.156,18.0153])
        self.assertAlmostEqual(r['caudales_molares'][0],.009991,delta=.000002)
        self.assertAlmostEqual(r['caudales_molares'][1],.566,delta=.0005)
        self.assertAlmostEqual(r['fracciones_molares'][0],.01735,delta=.0001)

    def test_ejemplo_11_4_consumo(self):
        self.assertAlmostEqual(1.50*(20-6)-3,18.)

    def test_ejemplo_11_6_mezcla_y_cierre(self):
        r=resolver_red(archivo('red_mezclador.json'))
        self.assertEqual(r['estado'],'unico')
        self.assertAlmostEqual(r['corrientes']['3']['total'],200)
        self.assertAlmostEqual(r['corrientes']['3']['componentes']['NaCl'],25.6)
        self.assertAlmostEqual(r['corrientes']['3']['componentes']['H2O'],174.4)
        self.assertAlmostEqual(r['corrientes']['3']['fracciones']['NaCl'],.128)

    def test_ejemplo_11_7_base(self):
        NaCl=750*.18;KCl=750*.07;water=750*.75
        self.assertAlmostEqual(NaCl,135)
        self.assertAlmostEqual(KCl,52.5)
        self.assertAlmostEqual(water,562.5)
        self.assertAlmostEqual(NaCl+KCl+water,750)

    def test_ejemplo_11_8_grados_de_libertad(self):
        r=resolver_red(archivo('grados_libertad_11_8.json'))
        self.assertEqual(r['estado'],'indeterminado')
        self.assertEqual(r['grados_libertad'],1)
        cfg=archivo('grados_libertad_11_8.json')
        cfg['streams'][1]['total']='80,0'
        x=resolver_red(cfg)
        self.assertEqual(x['estado'],'unico')
        self.assertAlmostEqual(x['corrientes']['3']['fracciones']['Etanol'],.36)

    def test_ejemplo_11_9_dos_mezcladores(self):
        r=resolver_red(archivo('red_dos_etapas.json'))
        self.assertEqual(r['estado'],'unico')
        self.assertAlmostEqual(r['corrientes']['3']['total'],150)
        self.assertAlmostEqual(r['corrientes']['4']['total'],100)
        self.assertAlmostEqual(r['corrientes']['5']['total'],250)

    def test_ejemplo_11_10_residuos(self):
        mass=comprobar_residuos([120.,80.],[199.9],200.)
        self.assertAlmostEqual(mass['residuo'],.1)
        self.assertAlmostEqual(mass['porcentaje'],.05)
        salt=120*.3-199.9*.1801
        water=120*.7+80-199.9*.8199
        self.assertAlmostEqual(salt,-.00199,places=6)
        self.assertAlmostEqual(water,.10199,places=6)
        self.assertAlmostEqual(salt+water,mass['residuo'])


class ProblemasTipoB(unittest.TestCase):
    def test_B1(self):self.assertEqual(125+75,200)
    def test_B2(self):
        r=180-145
        self.assertEqual(r,35)
        self.assertEqual(420+r*3,525)
    def test_B3(self):
        self.assertEqual(600-24*15,240)
        self.assertEqual((600-120)/24,20)
    def test_B4(self):
        self.assertEqual(250*.12,30)
        self.assertEqual(250*(1-.12),220)
    def test_B5(self):
        self.assertEqual(36+84,120)
        self.assertAlmostEqual(36/(36+84),.3)
        self.assertAlmostEqual(84/(36+84),.7)
    def test_B6(self):
        self.assertEqual(160+240,400)
        self.assertEqual(resolver_lineal(['salida'],[Ecuacion([1],400,'balance')]).grados_libertad,0)
    def test_B7(self):
        r=resolver_red({'components':['NaCl','Agua'],'units':[{'id':'M'}],
         'streams':[{'id':'1','from':None,'to':'M','total':'150','fractions':{'NaCl':'0,10'}},
                    {'id':'2','from':None,'to':'M','total':'100','fractions':{'NaCl':'0,25'}},
                    {'id':'3','from':'M','to':None}]})
        self.assertAlmostEqual(r['corrientes']['3']['total'],250)
        self.assertAlmostEqual(r['corrientes']['3']['componentes']['NaCl'],40)
        self.assertAlmostEqual(r['corrientes']['3']['fracciones']['NaCl'],.16)
    def test_B8(self):
        self.assertEqual(200-80,120)
        self.assertAlmostEqual(80*.30/200,.12)
    def test_B9(self):
        total=100*.4/.16
        self.assertEqual(total,250)
        self.assertEqual(total-100,150)
    def test_B10(self):
        r=mezclar_concentraciones([[.10,.30]],[.18],500)
        self.assertEqual(r.estado,'unico')
        self.assertAlmostEqual(r.valores['V_1'],300)
        self.assertAlmostEqual(r.valores['V_2'],200)
    def test_B11(self):
        r=base_molar_a_masa([40,10],[28.014,31.998])
        self.assertAlmostEqual(r['caudal_molar_total'],50)
        self.assertAlmostEqual(r['fracciones_molares'][0],.8)
    def test_B12(self):self.assertAlmostEqual(2.5*28.014,70.035)
    def test_B13(self):
        self.assertAlmostEqual(300*.08/.20,120)
        self.assertAlmostEqual(300-120,180)
    def test_B14(self):
        x=comprobar_residuos([90,135,75],[297],300)
        self.assertAlmostEqual(x['residuo'],3)
        self.assertAlmostEqual(x['porcentaje'],1)
    def test_B15(self):
        r=resolver_red({'components':['A','B'],'units':[{'id':'M'}],
         'streams':[{'id':'1','from':None,'to':'M','total':'120','fractions':{'A':'.2'}},
                    {'id':'2','from':None,'to':'M','fractions':{'A':'.5'}},
                    {'id':'3','from':'M','to':None,'fractions':{'A':'.32'}}]})
        self.assertEqual(r['estado'],'unico')
        self.assertAlmostEqual(r['corrientes']['2']['total'],80)
        self.assertAlmostEqual(r['corrientes']['3']['total'],200)
    def test_B16(self):
        r=resolver_red(archivo('balance_incompatible_11_B16.json'))
        self.assertEqual(r['estado'],'incompatible')
        self.assertAlmostEqual(250*.36-250*.35,2.5)
        self.assertAlmostEqual(250*.64-250*.65,-2.5)


class ProblemasTipoC(unittest.TestCase):
    def test_C1(self):
        r=mezclar_concentraciones([[1.,4.5]],[3.],12)
        self.assertEqual(r.estado,'unico')
        self.assertAlmostEqual(r.valores['V_1'],36/7)
        self.assertAlmostEqual(r.valores['V_2'],48/7)
        self.assertAlmostEqual(r.valores['V_1']+r.valores['V_2'],12)
    def test_C2(self):
        lost=10-8*1.15-.1-.55
        self.assertAlmostEqual(lost,.15)
        self.assertAlmostEqual(100*lost/10,1.5)
    def test_C3(self):
        self.assertAlmostEqual(.1-.094-.006,0,places=9)
        self.assertAlmostEqual(.100*4.5-(.094+.006)*2.,.25)
    def test_C4(self):
        self.assertAlmostEqual(12*.015,.180)
        self.assertAlmostEqual(12*.015*1.5,.270)
        self.assertAlmostEqual(12*.015*4.5,.810)
        self.assertAlmostEqual(12*.015*(4.5-1.5),.54)
    def test_C5(self):
        salt=5.*9 # 0,9% masa/volumen, g/L
        self.assertAlmostEqual(salt,45)
        self.assertAlmostEqual(salt/90,.5)
        self.assertAlmostEqual(5-.5,4.5)
        remaining=5-.05-.12
        self.assertAlmostEqual(remaining,4.83)
        self.assertEqual(int(remaining/.1+1e-9),48)
        self.assertAlmostEqual(remaining-4.8,.03)
    def test_C6(self):
        oxygen=(.4-.2095)/(1-.2095)*60
        air=60-oxygen
        self.assertAlmostEqual(oxygen,14.4592,places=3)
        self.assertAlmostEqual(air,45.5408,places=3)
        self.assertAlmostEqual(oxygen+air*.2095,.4*60)
        self.assertAlmostEqual(air*.7905,.6*60)
    def test_C7(self):
        self.assertAlmostEqual(12+8-.020,19.98)
        salt=(12*85+8*250)/(12+8)
        self.assertAlmostEqual(salt,151)
        self.assertAlmostEqual(19.98*salt+.02*salt,12*85+8*250)
    def test_C8(self):
        cfg=archivo('formulacion_11_C8.json')
        r=mezclar_concentraciones(**cfg)
        self.assertEqual(r.estado,'unico')
        for s in ['V_1','V_2']:self.assertAlmostEqual(r.valores[s],1000/12,places=6)
        self.assertAlmostEqual(r.valores['V_3'],2500/3,places=5)
        a,b,w=(r.valores[k] for k in ['V_1','V_2','V_3'])
        self.assertAlmostEqual(10*a+2*b,1000)
        self.assertAlmostEqual(a+5*b,500)
        self.assertAlmostEqual(a+b+w,1000)
    def test_C9(self):
        r=50-20-24-.25-5.5
        self.assertAlmostEqual(r,.25)
        self.assertAlmostEqual(r/50*100,.5)
        self.assertAlmostEqual(r*.02,.005)
    def test_C10(self):
        r=30-8-9-7.5-.2-4.
        self.assertAlmostEqual(r,1.3)
        self.assertAlmostEqual(r/30*100,100*1.3/30)
        self.assertAlmostEqual(r*4.5,5.85)
    def test_C11(self):
        A=.080*(4.5-1.8)
        B=.120*(4.5-2.4)
        self.assertAlmostEqual(A,.216)
        self.assertAlmostEqual(B,.252)
        self.assertAlmostEqual(A+B,.468)
        self.assertAlmostEqual(.080*4.5+.120*4.5-(.080*1.8+.120*2.4),A+B)



class PruebasIntegracionAplicada(unittest.TestCase):
    """Comprueba que los menús/motores reproducen balances, no solo aritmética externa."""
    @staticmethod
    def mezclar(entradas, fracciones, componentes=('A','B'), fraccion_final=None, total_final=None):
        streams=[]
        for i,(q,w) in enumerate(zip(entradas,fracciones),1):
            st={'id':str(i),'from':None,'to':'M','fractions':{componentes[0]:str(w)}}
            if q is not None:st['total']=str(q)
            streams.append(st)
        out={'id':str(len(entradas)+1),'from':'M','to':None}
        if fraccion_final is not None:out['fractions']={componentes[0]:str(fraccion_final)}
        if total_final is not None:out['total']=str(total_final)
        streams.append(out)
        return resolver_red({'components':list(componentes),'units':[{'id':'M'}],'streams':streams})

    def test_balance_tipo_B1_motor(self):
        r=self.mezclar([125,75],[1,1],componentes=('Agua','Otro'))
        self.assertEqual(r['estado'],'unico')
        self.assertAlmostEqual(r['corrientes']['3']['total'],200)

    def test_balance_tipo_B2_3_motor(self):
        a=inventario_lineal(420,[(180,0)],[(145,0)],3)
        self.assertAlmostEqual(a[-1]['inventario'],525)
        b=inventario_lineal(600,[],[(24,0)],15)
        self.assertAlmostEqual(b[-1]['inventario'],240)

    def test_balance_tipo_B8_motor(self):
        r=self.mezclar([80,None],[.3,0],total_final=200)
        self.assertEqual(r['estado'],'unico')
        self.assertAlmostEqual(r['corrientes']['2']['total'],120)
        self.assertAlmostEqual(r['corrientes']['3']['fracciones']['A'],.12)

    def test_balance_tipo_B9_motor(self):
        r=self.mezclar([100,None],[.40,0],fraccion_final=.16)
        self.assertEqual(r['estado'],'unico')
        self.assertAlmostEqual(r['corrientes']['2']['total'],150)
        self.assertAlmostEqual(r['corrientes']['3']['total'],250)

    def test_balance_tipo_B13_motor(self):
        r=self.mezclar([None,None],[.20,0],fraccion_final=.08,total_final=300)
        self.assertEqual(r['estado'],'unico')
        self.assertAlmostEqual(r['corrientes']['1']['total'],120)
        self.assertAlmostEqual(r['corrientes']['2']['total'],180)

    def test_balance_tipo_C3_consumo_motor(self):
        cfg={'basis':'mass','complete_components':False,'components':['Glucosa'],
             'units':[{'id':'Cultivo','reactions':[{'stoich':{'Glucosa':-1}}]}],
             'streams':[{'id':'e','from':None,'to':'Cultivo','total':'0.45'},
                        {'id':'s1','from':'Cultivo','to':None,'total':'0.188'},
                        {'id':'s2','from':'Cultivo','to':None,'total':'0.012'}]}
        r=resolver_red(cfg)
        self.assertEqual(r['estado'],'unico')
        self.assertAlmostEqual(r['valores']['extent:Cultivo:1'],.25)

    def test_balance_tipo_C6_mezcla_gas_motor(self):
        r=mezclar_concentraciones([[.2095,1.]],[.400],60.)
        self.assertEqual(r.estado,'unico')
        self.assertAlmostEqual(r.valores['V_1'],45.5408,places=3)
        self.assertAlmostEqual(r.valores['V_2'],14.4592,places=3)

    def test_balance_tipo_C7_concentraciones_motor(self):
        r=mezclar_concentraciones([[85,250]],[151],20)
        self.assertEqual(r.estado,'unico')
        self.assertAlmostEqual(r.valores['V_1'],12)
        self.assertAlmostEqual(r.valores['V_2'],8)
        self.assertAlmostEqual(20-.020,19.98)

    def test_balance_tipo_C11_consumos_2_reactores(self):
        cfg={'basis':'mass','complete_components':False,'components':['Glucosa'],
          'units':[{'id':'A','reactions':[{'stoich':{'Glucosa':-1}}]},
                   {'id':'B','reactions':[{'stoich':{'Glucosa':-1}}]}],
          'streams':[{'id':'eA','from':None,'to':'A','total':str(.080*4.5)},
                     {'id':'eB','from':None,'to':'B','total':str(.120*4.5)},
                     {'id':'sA','from':'A','to':None,'total':str(.080*1.8)},
                     {'id':'sB','from':'B','to':None,'total':str(.120*2.4)}]}
        r=resolver_red(cfg)
        self.assertEqual(r['estado'],'unico')
        self.assertAlmostEqual(r['valores']['extent:A:1'],.216)
        self.assertAlmostEqual(r['valores']['extent:B:1'],.252)

    def test_json_reacciones_fuentes_no_fisicas(self):
        cfg={'components':['A','B'],'units':[{'id':'M','source':{'A':'10'}}],
         'streams':[{'id':'e','from':None,'to':'M'},{'id':'s','from':'M','to':None}]}
        with self.assertRaises(ErrorBalance):resolver_red(cfg)

    def test_reproducibilidad_transitorio_y_csv(self):
        cfg=archivo('transitorio_mezcla.json')
        r=simular_mezcla(cfg,1e-8)
        analytic=cstr_analitico(100,25,0,10,20)
        self.assertAlmostEqual(r[-1]['concentracion'],analytic[-1]['concentracion'],delta=1e-6)
        with tempfile.TemporaryDirectory() as td:
            dest=guardar_datos(Path(td)/'ex.csv',r)
            self.assertGreater(dest.stat().st_size,100)

if __name__=='__main__':
    unittest.main(verbosity=2)
