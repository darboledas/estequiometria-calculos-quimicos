# Bloque VI — Cotejo de 23 ejercicios y validación del ajuste de actividad

**Fecha:** 7 de noviembre de 2026. **Estado:** copia de trabajo, NO publicada.

## Fuentes y alcance

Se contrastó el libro definitivo de 934 páginas con el solucionario desarrollado de 220 páginas. Ambos son propiedad editorial y **no se incluyen** en esta distribución de software. Se incorporaron 23 ejercicios nuevos de los capítulos 2–11, además de cinco métodos extra (un segundo ajuste para 8.C.2 y cuatro controles de entradas inválidas). Las pruebas invocan funciones reales del software; algunos problemas requieren balances algebraicos auxiliares. En ningún caso debe confundirse este muestreo con una validación experimental de las correlaciones.

## Resultados ejecutados

- **345/345** pruebas transversales superadas (317 anteriores + 28 métodos).
- **162** ejercicios distintos tienen algún cotejo reproducible acumulado sobre 556 identificadores inventariados. **394** sin cotejo individual.
- Compilación de capítulos 2–15 sin errores. Autopruebas propias de capítulos 9, 10, 11, 13, 14 y 15 superadas (véanse registros de ejecución de esta entrega).
- Se ha conservado el resultado de **8.C.2** al ajustar experimentalmente Margules con A12=1,0000017 y A21=0,6002903, y Van Laar con A12=1,0415701 y A21=0,6490926. El error medio absoluto de presión para Margules es ≈0,00312 kPa, frente a ≈0,21624 kPa para Van Laar, para la tabla concreta del libro.

## Incidencias corregidas — capítulo 8

En `disoluciones_no_ideales.py`, `experimental_gammas` admitía valores NaN/infinito y presiones no físicas, sin garantizar longitudes iguales. `fit_margules2` utilizaba `zip(x1,g1,g2)` sin comprobar longitudes, con posibilidad de **descartar puntos silenciosamente**. La ruta `fit_van_laar` también carecía de estas comprobaciones. Se han añadido condiciones explícitas de forma, longitud, finitud, dominio 0 < x,y < 1, presiones positivas, gamma positivos y diseño de Margules con rango suficiente. Las entradas inválidas producen ahora `ValueError` antes del ajuste; las series válidas reproducen 8.C.2 dentro de tolerancias de redondeo.

## Cotejo por ejercicio

| Ejercicio | Página PDF | Contraste | Resultado |
|---|---:|---|---|
| 2.C.5 | 99 | Propagación de incertidumbre de titulación | PASS |
| 3.C.2 | 161 | Combustión estequiométrica de butano | PASS |
| 3.C.3 | 161 | Producción de H₂ por reacción de aluminio | PASS |
| 3.C.5 | 162 | Preparación gravimétrica de disolución | PASS |
| 4.C.1 | 191 | Propiedades de gas de combustión multicomponente | PASS |
| 4.C.7 | 192 | Secador con balance de nitrógeno | PASS |
| 4.C.8 | 192 | Absorción parcial de amoníaco | PASS |
| 4.C.9 | 192 | Mezcla para enriquecimiento de oxígeno | PASS |
| 5.C.3 | 250 | Peng–Robinson a 90 bar para metano | PASS |
| 5.C.4 | 251 | Lee–Kesler para vapor de agua | PASS |
| 6.B.14 | 293 | Lee–Kesler frente a Antoine para n-heptano | PASS |
| 6.C.4 | 295 | Interpolación mediante diagrama de Cox | PASS |
| 7.C.4 | 365 | Curvas de burbuja y rocío binario | PASS |
| 7.C.7 | 365 | Dos fases líquidas con C inmiscible | PASS |
| 8.B.6 | 457 | Modelo de Wilson y energía libre de exceso | PASS |
| 8.C.2 | 461 | Ajustes Margules y Van Laar de datos VLE | PASS |
| 8.C.4 | 462 | Enriquecimiento etapa a etapa de etanol | PASS |
| 9.C.2 | 518 | Equilibrio trifásico con agotamiento | PASS |
| 9.C.4 | 519 | Condensador y decantador de heteroazeótropo | PASS |
| 10.C.4 | 590 | Presión osmótica ideal del agua de mar | PASS |
| 10.C.5 | 590 | Osmolaridad e intensidad iónica de SRO | PASS |
| 11.C.4 | 662 | Balance de glucosa en recambio de medio | PASS |
| 11.C.5 | 662 | Dilución salina y envasado | PASS |

## Límites de interpretación

1. Algunos ejercicios reúnen operaciones que se contrastan por separado, no mediante una orden única de interfaz. Estas situaciones se identifican como «función + álgebra auxiliar» en la matriz JSON.
2. En el ejercicio 10.C.5, la función `fuerza_ionica` recibe formalmente **molalidades**; para el cotejo se utilizó únicamente la operación algebraica ½Σcᵢzᵢ² sobre concentraciones molares. No se ha supuesto identidad física entre molaridad y molalidad.
3. Se compararon valores internos con la precisión del solucionario, respetando cifras significativas. No se alteraron las constantes termodinámicas de los modelos.
4. Quedan por cotejar 394 identificadores de ejercicios; algunos son conceptuales y deben examinarse por revisión editorial, no por cálculo numérico.

## Reproducción

```bash
python -m unittest discover -s pruebas_revision -p test_cotejo_bloque_06.py -v
python -m unittest discover -s pruebas_revision -q
python -m compileall -q capitulo_02 capitulo_03 capitulo_04 capitulo_05 capitulo_06 capitulo_07 capitulo_08 capitulo_09 capitulo_10 capitulo_11 capitulo_12 capitulo_13 capitulo_14 capitulo_15
```

El resultado de las 345 pruebas consta en `REGISTRO_TEST_345.txt`. La publicación 0.9.0 de GitHub/Zenodo sigue intacta.
