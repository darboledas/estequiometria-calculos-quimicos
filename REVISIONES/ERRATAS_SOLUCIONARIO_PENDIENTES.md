# Erratas contrastadas del solucionario desarrollado (no corregidas en el PDF)

## Ejercicio 5.B.6 — virial de isopropanol (solucionario, PDF página 54)

El solucionario imprime la ecuación cúbica equivalente a:

`10 V_m³ − (0,0831446)(473) V_m² − 0,388 V_m − 0,026 = 0`.

La ecuación del modelo que se ha declarado, `Z=1+B/V_m+C/V_m²` y `Z=P V_m/(RT)`, conduce por multiplicación a:

`P V_m³ − RT V_m² − RT B V_m − RT C = 0`.

Sustituyendo `P=10 bar`, `T=473 K`, `B=−0,388 L/mol`, `C=−0,026 L²/mol²` y `R=0,0831446 L·bar/(mol·K)`:

`10 V_m³ − 39,3273958 V_m² + 15,2590296 V_m + 1,0225123 = 0`.

La raíz gaseosa mayor `V_m=3,48669 L/mol` y `Z=0,886581` que proporciona el solucionario **sí son correctas**; satisfacen la cúbica correcta. La ecuación impresa no se anula con esa raíz. Por tanto, se trata de una **errata de desarrollo algebraico** y no de un resultado final erróneo ni de un fallo del programa.

Los PDFs del libro y el solucionario no se alteran. Confirmación reproducible:
`python -m unittest discover -s pruebas_revision -p test_cotejo_bloque_07.py -v`.

## Ejercicio 4.B.2 — Masa de aire en depósito esférico

El valor intermedio correcto es **76.094,16 kg**; el solucionario imprime **76.015 kg**. La respuesta final redondeada **7,6×10⁴ kg** no cambia. Datos: D=50,0 m, P=100000 Pa, T=300 K, M=0,0290 kg/mol, R=8,31446 J/(mol·K). No se altera el PDF.
