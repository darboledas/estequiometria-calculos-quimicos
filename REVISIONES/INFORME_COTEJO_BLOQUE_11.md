# Bloque XI — cierre del cotejo B/C y delimitación del alcance

Fecha de trabajo: 7 de noviembre de 2026. Base privada: libro definitivo de 934 páginas y solucionario desarrollado de 220 páginas (no se incluyen ni redistribuyen en este repositorio).

## Resultados reproducibles

- Regresión anterior: 482 pruebas.
- Nuevos ejercicios B/C con comprobación numérica: **90**, no duplicados en las matrices precedentes.
- Regresión acumulada: **572 pruebas**, sin fallos (Python 3.13 en el entorno de revisión).
- Las 90 pruebas nuevas incluyen **66 con intervenciones de módulos Python** (en algún caso solo como apoyo) y **24 cálculos auxiliares independientes**. Esta clasificación no significa que las 66 representen una función completa o un flujo de interfaz del programa.
- Comprobados en los bloques I–X: 253 ejercicios B/C. Bloque XI: 90 cotejos numéricos nuevos. Total con contraste numérico: **343/350**.
- Los restantes siete C se han contrastado cualitativa o gráficamente con los enunciados y las soluciones: 5.C.5, 5.C.6, 6.C.5, 6.C.6, 6.C.7, 6.C.8 y 6.C.10. Para 6.C.8 se inspeccionó la figura 6.4 del libro. Así, los **350 ejercicios B/C disponen de algún tipo de cotejo**, de alcance variable y no equivalente a validación de todas las funciones de las aplicaciones.
- Los 206 ejercicios A tienen identificador de enunciado y respuesta presente en ambos libros. Esta verificación **no equivale a revisión individual de su exactitud científica**, que continúa pendiente.

## Casos cuantitativos representativos

- 5.B.10: iteración Lee–Kesler con oxígeno, presión ≈78,3311 bar y factor Z≈0,904422.
- 6.C.11: presión de vapor del tolueno a 298 K, 3,76288 kPa; masa de vapor en 2 L ≈0,279865 g.
- 7.C.9: rocío ternario a 60 kPa, 336,29594 K; flash a 330 K, fracción vaporizada ≈0,574595.
- 7.C.10: destilación Rayleigh, 60,9275 kmol de residuo y 39,0725 kmol de destilado.
- 8.C.6: flash no ideal Margules, fracción vaporizada ≈0,901740.
- 9.C.6: agua–tolueno, 357,48673 K; agua–benceno, 342,27133 K.
- 10.C.8: presión osmótica de alimentación ≈6,34783 bar; concentrado ≈12,69565 bar.
- 11.C.8: mezcla nutricional, 83,3333 L A + 83,3333 L B + 833,3333 L agua.

## Limitaciones y criterio editorial

1. **No hay parches nuevos del núcleo de las 28 aplicaciones en este bloque.** Se incorpora un banco adicional de prueba y la trazabilidad; se conservan las correcciones ya ensayadas en los bloques anteriores.
2. Los cotejos proceden del libro y su solucionario; no sustituyen contrastes experimentales independientes para todas las correlaciones termodinámicas.
3. La ausencia de errores en la batería no demuestra ausencia de errores en rutas de código no ejecutadas, interfaces interactivas, entradas extremas o plataformas distintas.
4. La correspondencia editorial de los 206 ejercicios A está comprobada, pero queda pendiente la revisión científica individual de sus respuestas.
5. La versión pública v0.9.0 no debe actualizarse automáticamente a v1.0.0 solo por haber completado los B/C. Deben cerrarse la revisión conceptual y el procedimiento de prepublicación.

## Reproducción

```powershell
python -m unittest discover -s pruebas_revision -p test_cotejo_cierre_11.py -v
python -m unittest discover -s pruebas_revision -q
python -m compileall -q capitulo_02 capitulo_03 capitulo_04 capitulo_05 capitulo_06 capitulo_07 capitulo_08 capitulo_09 capitulo_10 capitulo_11 capitulo_12 capitulo_13 capitulo_14 capitulo_15
```

Archivos: `MATRIZ_COTEJO_BLOQUE_11_90.json`, `COTEJO_C_CUALITATIVOS_7.json`, `INVENTARIO_CONCEPTUALES_A_206.csv`, `INVENTARIO_COBERTURA_556_ACTUALIZADO.csv`, `RESUMEN_COBERTURA_CAPITULOS_XI.csv`.
