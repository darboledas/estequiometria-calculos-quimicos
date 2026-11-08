# Bloque 4: cotejo de aplicaciones y validación de títulos de vapor (7-11-2026)

**Copia de trabajo no publicada en GitHub ni Zenodo.** Fuente editorial: edición definitiva de 934 páginas y solucionario desarrollado de 220 páginas, ambos excluidos del paquete de código por derechos de edición.

## Resultados verificados

- 26 ejercicios nuevos tipo C, de los capítulos 2, 3, 4, 5, 6, 7, 10, 11, 12, 13, 14 y 15.
- 28 nuevas pruebas transversales: 26 comprobaciones de ejercicios + 2 regresiones de validación de valores no finitos.
- Batería transversal: **290/290 pruebas correctas** en Python 3.13.5; 116 ejercicios distintos acumulados (90+26).
- Compilación de los 14 capítulos sin incidencias y pruebas específicas de los capítulos 9, 10, 11, 13, 14 y 15 correctas.
- Las pruebas comparan resultados publicados con funciones reales de los programas; donde el programa no tiene un flujo único para todo el enunciado, se distingue explícitamente el balance algebraico suplementario.

## Incidencia corregida: vapor de agua (capítulo 6)

`quality_from_property()` de `capitulo_06/vapor_agua.py` devolvía valores `NaN` o infinitos cuando la propiedad de entrada o los valores de saturación no eran finitos. Esto podía inducir a imprimir un título de vapor indefinido. La función ahora comprueba la finitud de la propiedad y de las dos referencias antes de calcular el título; rechaza los valores inválidos mediante `ValueError`.

Se conserva el criterio anterior de clasificación: si el título formal resulta menor que cero o mayor que uno a partir de **datos finitos**, el programa informa de que el estado no corresponde a mezcla bifásica. El ejercicio 6.C.9 sigue reproduciendo x=0,877989 para h=2400, hf=417,5 y hg=2675,5 kJ/kg.

## Particularidades y límites

- **2.C.1**: el libro utiliza 3,785 L/gal estadounidense como factor redondeado; el programa utiliza el valor exacto 3,785411784 L/gal. Ambos resultados dan 4,20 m³/h con tres cifras significativas. No es un error físico.
- **3.C.4, 4.C.5, 4.C.6, 6.C.1, 12.C.2 y 13.C.2**: la prueba encadena funciones o balances externos. No atribuir a cada aplicación una interfaz integrada que no existe.
- **5.C.1, 5.C.2 y 5.C.7**: son coincidencias con modelos de gases reales, no certificados experimentales de RK/PR/Lee–Kesler en otros estados.
- **6.C.3**: el ajuste de Dühring reproduce 16,627 kPa; el resultado no es una validación empírica fuera de los dos puntos medidos.
- **7.C.6**: el método verifica presión, composiciones molares y másicas de una mezcla ternaria ideal.
- **10.C.2 y 15.C.2**: los valores obtenidos corresponden a modelos ideales y no deben extrapolarse a usos clínicos o a predicción de conservación real sin validación.
- **556 identificadores** en el inventario editorial; tras esta ampliación, **116** cuentan con comprobación numérica documentada. Quedan alrededor de **440** sin ese tipo de contraste; parte de ellos son conceptuales.
- No se han comprobado todos los subapartados, interfaces interactivas, gráficas, incertidumbres ni intervalos experimentales. No se ha ejecutado GitHub Actions para esta copia de trabajo.

## Reproducción

```bash
python -m unittest discover -s pruebas_revision -p test_cotejo_aplicados_04.py -v
python -m unittest discover -s pruebas_revision -q
python -m compileall -q capitulo_02 capitulo_03 capitulo_04 capitulo_05 capitulo_06 capitulo_07 capitulo_08 capitulo_09 capitulo_10 capitulo_11 capitulo_12 capitulo_13 capitulo_14 capitulo_15
python capitulo_10/propiedades_coligativas.py --selftest
python capitulo_10/disoluciones_electroliticas.py --selftest
python capitulo_14/combustion.py --self-test
python capitulo_15/psicrometria.py --validar
```

Consulte `MATRIZ_COTEJO_BLOQUE_04.json` para los 26 ejercicios y la función/composición de funciones comprobada.
