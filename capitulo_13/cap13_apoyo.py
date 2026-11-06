#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Funciones comunes de los scripts del capítulo 13: fórmulas, esquemas e informes.

Sin dependencias externas para SVG/HTML/CSV/JSON. Para PNG a 400 ppp:
    pip install cairosvg
No se emplean las figuras para efectuar cálculos.
"""
from __future__ import annotations

import csv
import json
import re
import textwrap
from datetime import datetime
from decimal import Decimal
from html import escape as html_escape
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

# Símbolos químicos oficiales; los nombres de especies genéricas, como A, B y C,
# no se validan como fórmulas si hay algún término no reconocido.
ELEMENTOS = set((
    'H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn '
    'Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba '
    'La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au Hg '
    'Tl Pb Bi Po At Rn Fr Ra Ac Th Pa U Np Pu Am Cm Bk Cf Es Fm Md No Lr '
    'Rf Db Sg Bh Hs Mt Ds Rg Cn Nh Fl Mc Lv Ts Og'
).split())


def formula_elemental(nombre: str):
    """Parsea fórmulas neutras con grupos (), [] y subíndices enteros.

    Devuelve None si se trata de etiqueta o fórmula no soportada, en lugar de
    presentar falsamente una comprobación elemental como satisfactoria.
    """
    s = nombre.strip().replace('₀','0').replace('₁','1').replace('₂','2').replace('₃','3').replace('₄','4').replace('₅','5').replace('₆','6').replace('₇','7').replace('₈','8').replace('₉','9')
    s = re.sub(r'\((aq|s|l|g)\)$', '', s, flags=re.I)
    if not s or any(x in s for x in ('·', '•', '^', '+', '-', ' ', '*', '.')):
        return None
    tokens = re.findall(r'[A-Z][a-z]?|\d+|[()\[\]]', s)
    if ''.join(tokens) != s:
        return None
    groups = [{}]
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t in ('(', '['):
            groups.append({})
            i += 1
        elif t in (')', ']'):
            if len(groups) == 1:
                return None
            inner = groups.pop()
            i += 1
            mult = int(tokens[i]) if i < len(tokens) and tokens[i].isdigit() else 1
            if mult < 1:
                return None
            if i < len(tokens) and tokens[i].isdigit():
                i += 1
            for element, count in inner.items():
                groups[-1][element] = groups[-1].get(element, 0) + count * mult
        elif t in ELEMENTOS:
            i += 1
            mult = int(tokens[i]) if i < len(tokens) and tokens[i].isdigit() else 1
            if mult < 1:
                return None
            if i < len(tokens) and tokens[i].isdigit():
                i += 1
            groups[-1][t] = groups[-1].get(t, 0) + mult
        else:
            return None
    return groups[0] if len(groups) == 1 and groups[0] else None


def comprobar_formulas(nombres, matriz_nu):
    """Devuelve (estado, detalle); no certifica ecuaciones simbólicas.

    matriz_nu: filas especie, columnas reacción. Coeficientes exactos Decimal.
    """
    # A/B/C son etiquetas habituales de especies en problemas simbólicos.
    # No confundirlas con los símbolos de boro/carbono, etc.
    if all(re.fullmatch(r'[A-Z]',n.strip()) for n in nombres):
        return 'no_verificado', 'Ecuaciones simbólicas con letras: no se puede verificar un balance elemental sin fórmulas.'
    formulas = [formula_elemental(n) for n in nombres]
    if any(f is None for f in formulas):
        ignoradas = ', '.join(n for n, f in zip(nombres, formulas) if f is None)
        return 'no_verificado', f'Fórmulas sin análisis automático: {ignoradas}. Utilice verificación elemental manual cuando proceda.'
    nr = len(matriz_nu[0])
    for r in range(nr):
        elementos = set().union(*(f.keys() for f in formulas))
        errores = {}
        for e in sorted(elementos):
            balance = sum(Decimal(matriz_nu[i][r]) * formulas[i].get(e, 0) for i in range(len(nombres)))
            if balance != 0:
                errores[e] = str(balance)
        if errores:
            msg = ', '.join(f'{e}: {v}' for e, v in errores.items())
            return 'incorrecto', f'La reacción {r+1} NO está ajustada. Residuos elementales: {msg}'
    return 'correcto', f'Conservación de todos los elementos verificada para {nr} reacción(es).'


def _safe_name(s: str):
    return re.sub(r'[^A-Za-z0-9_\-]+', '_', s).strip('_')[:50] or 'balance'


def _svg_text(x, y, content, size=21, weight='normal', anchor='start', fill='#17263a'):
    return f'<text x="{x}" y="{y}" font-family="DejaVu Sans, Arial, sans-serif" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{fill}">{xml_escape(str(content))}</text>'


def _box(x, y, w, h, title, lines, color='#e5f2fd'):
    s = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{color}" stroke="#2e5675" stroke-width="2.7"/>',
         _svg_text(x+w/2,y+36,title,23,'bold','middle')]
    for k,line in enumerate(lines):
        size = 16 if len(line) < 36 else 14
        s.append(_svg_text(x+w/2,y+70+27*k,line,size,anchor='middle'))
    return '\n'.join(s)


def crear_svg_esquema(datos, formato):
    """Esquema de flujos de información y materias, NO reconstrucción geométrica de planta."""
    es_batch = datos['tipo_sistema'] != 'continuo'
    sep = datos.get('separacion') is not None
    nombres = datos['especies']
    in_ = datos['disponible']
    out = datos['final']
    titulo = 'Balance de materia con reacción química'
    width=1400
    dy = max(34, 30)
    table_y = 495 if sep else (500 if datos.get('alimentacion') else 455)
    height = table_y + 112 + len(nombres)*dy + 115
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="180mm" height="{height*180/width:.2f}mm" viewBox="0 0 {width} {height}">',
         '<rect width="100%" height="100%" fill="white"/>',
         '<defs><marker id="flecha" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto" markerUnits="strokeWidth"><path d="M0,1 L11,6 L0,11 Z" fill="#2e5675"/></marker></defs>',
         _svg_text(700,55,titulo,32,'bold','middle'),
         _svg_text(700,89,datos['descripcion'],19,anchor='middle',fill='#496073')]
    # La representación se ajusta al ancho del reactor, sin invadir las flechas.
    # Toda la ecuación sigue disponible en HTML/JSON aunque aquí se resuma.
    rlines=[]
    max_caracteres = 27 if sep else 37
    for reaccion in datos['reacciones']:
        segmentos = reaccion.replace(' → ', '  →  ').split('  →  ')
        cadena = segmentos[0]
        parts = textwrap.wrap(cadena, max_caracteres, break_long_words=False) or [cadena]
        if len(segmentos)>1:
            parts += textwrap.wrap('→ '+ segmentos[1],max_caracteres,break_long_words=False)
        rlines.extend(parts)
        if len(rlines) >= 4:
            break
    if len(rlines)>4:
        rlines=rlines[:3]+['(véanse todas las reacciones en el informe)']
    elif len(datos['reacciones'])>2:
        rlines=rlines[:3]+['(otras reacciones en el informe)']
    if sep:
        svg += [
          _box(405,165,330,190,'Zona de reacción',rlines),
          _box(875,165,300,190,'Separación',['Recuperación en P', 'Resto de especies a L'],'#fff2dd'),
          '<path d="M140 255 H390" stroke="#2e5675" stroke-width="3" fill="none" marker-end="url(#flecha)"/>',
          '<path d="M735 255 H860" stroke="#2e5675" stroke-width="3" fill="none" marker-end="url(#flecha)"/>',
          '<path d="M1175 225 H1290" stroke="#2e5675" stroke-width="3" fill="none" marker-end="url(#flecha)"/>',
          '<path d="M1175 305 H1290" stroke="#2e5675" stroke-width="3" fill="none" marker-end="url(#flecha)"/>',
          _svg_text(145,243,'F / inventario',20,'bold'),
          _svg_text(790,241,'M',20,'bold'),
          _svg_text(1293,211,'P',20,'bold'),
          _svg_text(1293,296,'L',20,'bold')
        ]
    else:
        svg += [ _box(500,155,410,195,'Sistema reactivo',rlines),
                 '<path d="M130 245 H480" stroke="#2e5675" stroke-width="3" fill="none" marker-end="url(#flecha)"/>',
                 '<path d="M910 245 H1270" stroke="#2e5675" stroke-width="3" fill="none" marker-end="url(#flecha)"/>',
                 _svg_text(155,229,'Entrada' if not es_batch else 'Inventario + alimentación',18,'bold'),
                 _svg_text(1070,229,'Salida' if not es_batch else 'Cantidad final',18,'bold')]
    if datos.get('alimentacion'):
        svg.append(_svg_text(700,415,datos['alimentacion'],18,anchor='middle'))
    svg.append(_svg_text(70,table_y-25,f'Extensiones: {"; ".join(datos["extensiones"])}',20,'bold'))
    cols = [75,410,710,1030]
    colheaders=['Especie','Antes de reaccionar','Después de reaccionar','Unidad']
    svg += [f'<rect x="55" y="{table_y}" width="1280" height="53" rx="7" fill="#d8ecf9"/>']
    for c, h in zip(cols,colheaders):
        svg.append(_svg_text(c,table_y+34,h,19,'bold'))
    for i,n in enumerate(nombres):
        yy = table_y + 80 + i*dy
        if i % 2 == 0:
            svg.append(f'<rect x="55" y="{yy-26}" width="1280" height="32" fill="#f5f8fb"/>')
        for x, val in zip(cols,[n,in_[i],out[i],datos['unidad']]):
            svg.append(_svg_text(x, yy, str(val),19))
    sy= table_y + 91 + len(nombres)*dy
    if sep:
        sv=datos['separacion']
        svg.append(_svg_text(70,sy,f"Separación: {sv['especie']} → P: {sv['producto']} {datos['unidad']}; L: {sv['residual']} {datos['unidad']}",19))
        sy+=31
    nota = ('Esquema de estados: las flechas no representan entradas ni salidas físicas.'
            if es_batch else 'Esquema conceptual: las corrientes se agregan por especie.')
    svg.append(_svg_text(70,sy+24,nota,17,fill='#566579'))
    svg.append('</svg>')
    return '\n'.join(svg)


def crear_svg_variaciones(datos):
    """Gráfico de cambios estequiométricos: no representa cinética temporal."""
    initial = [Decimal(v) for v in datos['antes_sin_redondeo']]
    final = [Decimal(v) for v in datos['final_sin_redondeo']]
    deltas = [b-a for a,b in zip(initial,final)]
    top=170
    dy=66
    h=top+dy*len(deltas)+92
    w=1400
    maxabs = max((abs(d) for d in deltas),default=Decimal(0)) or Decimal(1)
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="180mm" height="{h*180/w:.2f}mm" viewBox="0 0 {w} {h}">',
           '<rect width="100%" height="100%" fill="white"/>',
           _svg_text(700,55,'Variaciones netas debidas a las reacciones',29,'bold','middle'),
           _svg_text(700,88,'Consumo (izquierda)  ·  Formación (derecha)',20,anchor='middle'),
           f'<path d="M700 120 V{h-80}" stroke="#506b80" stroke-width="2"/>']
    for j,(n,d) in enumerate(zip(datos['especies'],deltas)):
        cy=top+j*dy
        length=float(abs(d)/maxabs)*360
        if d < 0:
            x=700-length
            col='#e6ad76'
        else:
            x=700
            col='#5eacd6'
        parts.append(f'<rect x="{x:.1f}" y="{cy-28}" width="{max(length,1):.1f}" height="38" rx="4" fill="{col}"/>')
        parts.append(_svg_text(40,cy-1,n,22))
        val=datos['deltas_etiquetas'][j]
        parts.append(_svg_text(1085,cy-1,f'{val} {datos["unidad"]}',21))
    parts.append(_svg_text(50,h-38,'Gráfico calculado con los valores internos, antes del redondeo final.',16,fill='#566579'))
    parts.append('</svg>')
    return '\n'.join(parts)


def exportar(datos, modo: int, carpeta='informes_cap13'):
    """Escribe SVG, HTML, CSV, JSON y opcionalmente PNG a 400 ppp.

    modo: 1 = no exportar; 2 = ficheros vectoriales/informes; 3 = además PNG.
    """
    if modo == 1:
        return []
    p = Path(carpeta).expanduser().resolve()
    p.mkdir(parents=True, exist_ok=True)
    nombre = _safe_name(datos['script']) + '_' + datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    path = p / nombre
    unidad = datos['unidad']
    registros=[{'especie':n,'antes':a,'despues':b,'unidad':unidad} for n,a,b in zip(datos['especies'],datos['disponible'],datos['final'])]
    paquete = {'script': datos['script'], 'descripcion': datos['descripcion'], 'tipo_sistema': datos['tipo_sistema'], 'unidad':unidad,
               'reacciones':datos['reacciones'],'extensiones':datos['extensiones'],'valores':registros,
               'validacion_estequiometrica':datos['validacion_estequiometrica'], 'separacion':datos.get('separacion'),
               'alimentacion':datos.get('alimentacion'), 'advertencias': datos.get('advertencias',[]),
               'nota_precision': 'Los valores presentados se redondean al final; la precisión multirreacción puede requerir revisión en sistemas mal condicionados.'}
    sf = str(path)+'.svg'
    svg=crear_svg_esquema(datos, None)
    Path(sf).write_text(svg,encoding='utf-8')
    chart = crear_svg_variaciones(datos)
    plot_svg = str(path)+'_variaciones.svg'
    Path(plot_svg).write_text(chart,encoding='utf-8')
    jf=str(path)+'.json'
    Path(jf).write_text(json.dumps(paquete,indent=2,ensure_ascii=False),encoding='utf-8')
    cf=str(path)+'.csv'
    with open(cf, 'w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f,delimiter=';')
        w.writerow(['Especie','Antes','Después','Unidad'])
        for item in registros:
            w.writerow(item.values())
    hf=str(path)+'.html'
    filas='\n'.join('<tr>'+''.join(f'<td>{html_escape(str(v))}</td>' for v in row.values())+'</tr>' for row in registros)
    esqs=''.join(f'<li>{html_escape(v)}</li>' for v in datos['extensiones'])
    aviso=''.join(f'<p>{html_escape(v)}</p>' for v in datos.get('advertencias',[]))
    html=('<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><title>Balance capítulo 13</title>'
          '<style>body{font-family:Georgia,serif;max-width:1060px;margin:2em auto;color:#17304a;line-height:1.5}'
          'table{border-collapse:collapse;width:100%}td,th{border:1px solid #bed1df;padding:.6em;text-align:left}th{background:#d8ecf9}'
          'svg{width:100%;height:auto}h1{font-size:1.5em}@media print{body{margin:1cm}svg{page-break-inside:avoid}}</style></head><body>'
          f'<h1>{html_escape(datos["descripcion"])}</h1><p>Unidad: {html_escape(unidad)}. '
          f'Validación: {html_escape(datos["validacion_estequiometrica"])}</p><ul>{esqs}</ul>{aviso}'
          f'{svg}<h2>Variaciones estequiométricas</h2>{chart}<h2>Resultados</h2><table><thead><tr><th>Especie</th><th>Antes</th><th>Después</th><th>Unidad</th></tr></thead><tbody>{filas}</tbody></table>'
          '<p>Comprobar los datos y el modelo físico antes de utilizar los resultados.</p></body></html>')
    Path(hf).write_text(html,encoding='utf-8')
    rutas=[sf,plot_svg,hf,cf,jf]
    if modo == 3:
        try:
            import cairosvg
            png=str(path)+'.png'
            # 180 mm en el SVG; output_width = 180/25,4 × 400 ppp.
            cairosvg.svg2png(bytestring=svg.encode('utf-8'),write_to=png,output_width=round(180/25.4*400))
            # También escribimos la resolución nominal en los metadatos PNG.
            try:
                from PIL import Image
                with Image.open(png) as im:
                    im.save(png, dpi=(400,400))
            except ImportError:
                print('  Nota: PNG tiene píxeles para 400 ppp a 180 mm; instale Pillow para metadatos DPI.')
            rutas.append(png)
            png_bar = str(path)+'_variaciones.png'
            cairosvg.svg2png(bytestring=chart.encode('utf-8'),write_to=png_bar,output_width=round(180/25.4*400))
            try:
                from PIL import Image
                with Image.open(png_bar) as im:
                    im.save(png_bar,dpi=(400,400))
            except ImportError:
                pass
            rutas.append(png_bar)
        except (ImportError, OSError, ValueError) as exc:
            print(f'  Aviso: no se creó PNG ({exc}); el SVG sigue disponible. Instale cairosvg si lo necesita.')
    return rutas
