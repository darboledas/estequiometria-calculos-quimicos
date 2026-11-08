# Informe científico: estabilidad de sistemas inversos y correlaciones empíricas

**Fecha:** 7 de noviembre de 2026. **Estado:** copia de trabajo local no publicada.  
**Versión archivada que permanece inalterada:** `v0.9.0` (DOI 10.5281/zenodo.24020473).  
**Programas examinados en esta fase:** `capitulo_14/combustion.py` y `capitulo_06/presion_vapor.py`.

## 1. Defecto reproducido: sistemas casi singulares

El solucionador anterior normalizaba las ecuaciones por filas, pero clasificaba como solución única sistemas de ecuaciones prácticamente dependientes. Por ejemplo:

```text
n1 +          n2 = 2
n1 + 1,000000001 n2 = 2,000000001
```

La solución algebraica es `n1 = 1`, `n2 = 1`. Si únicamente se perturba el segundo dato en `+0,000000010` (un cambio relativo del orden de 5 × 10⁻⁹), la solución cambia aproximadamente a `n1 = −9`, `n2 = 11`. La ausencia de un residuo alto NO garantiza que una composición deducida sea fiable.

Se ha implementado un solucionador de Gauss-Jordan **con equilibrado de filas y columnas, pivoteo completo, comprobación de residuos sobre las ecuaciones originales y rechazo heurístico de soluciones mal condicionadas**. El criterio de rechazo de pivotes relativos inferiores a `10⁻⁸`, así como el umbral de desequilibrio de columnas `10⁹`, son salvaguardas conservadoras del programa, no estimaciones exactas del número de condición ni de la incertidumbre experimental. Pueden rechazar casos matemáticamente invertibles que necesiten un tratamiento numérico especializado. Los sistemas exactamente indeterminados e incompatibles conservan mensajes distintos.

Un segundo ejemplo con coeficientes `10¹²` y `1` muestra que las ecuaciones pueden ser casi incapaces de identificar un componente minoritario debido al rango limitado de la precisión de coma flotante, aunque el algoritmo dé un residuo pequeño. La versión actual informa de observables insuficientemente discriminantes en lugar de devolver una cantidad arbitraria.

## 2. Verificaciones de regresión

- **18 métodos transversales nuevos:** 8 para cálculos inversos, 6 para correlaciones y dominios y 4 para el cotejo con el libro.
- **200 sistemas aleatorios de hasta seis incógnitas**, construidos con soluciones conocidas y matrices estrictamente dominantes en diagonal; reconstrucción correcta en los casos ensayados.
- Sistemas rectangulares con observables redundantes compatibles e incompatibles.
- Casos bien condicionados con escalas de `10⁻¹²` a `10¹²`, y casos casi singulares con pequeñas perturbaciones de datos.
- **Antoine:** 231 pares de presión y temperatura (11 sustancias, 21 temperaturas por sustancia) reproducidos mediante evaluación e inversión dentro de los intervalos declarados; se comprueba rechazo de extrapolación no autorizada.
- **Clausius-Clapeyron:** inversión analítica y recuperación de entalpía bajo su hipótesis de entalpía constante.
- **Dühring:** ajuste e inversión de cuatro observaciones sintéticas obtenidas de una recta conocida.
- **Lee-Kesler:** rechazo en y por encima de la temperatura crítica; control de rango didáctico inferior y de salidas positivas.
- Los exponentes de Antoine, Clausius-Clapeyron y Lee-Kesler que desbordan el rango representable producen ahora una excepción `ValueError` descriptiva, sin un desbordamiento bruto.

**Resultado local:** 161 métodos transversales superados (143 anteriores + 18 nuevos), además de las baterías del capítulo 9 (24), 10 (39 + 38), 11 (58), 13 (12), 14 (23) y 15 (12 grupos). Pruebas ejecutadas en Python 3.13; falta repetirlas en GitHub Actions con Python 3.11 y 3.13 cuando se publique la revisión. Compilación sintáctica correcta.

## 3. Alcance y restricciones

La inversión de Antoine y el ajuste sintético de Dühring demuestran **consistencia algebraica interna**, no que la correlación reproduzca todos los datos experimentales. La correlación de Antoine requiere conservar los rangos de temperatura, la base logarítmica y las unidades propias de cada conjunto de coeficientes; no deben sustituirse constantes de `P[bar]` por las del programa `P[kPa]` sin convertirlas.

El rechazo de sistemas inversos mal condicionados es un mecanismo de seguridad numérica y **no sustituye un estudio de incertidumbres, análisis de sensibilidad por componente, mínimos cuadrados ponderados ni regularización**. El código conserva la distinción entre modelos físicos especificados y resultados deducibles de los observables disponibles.

El PDF del libro comercial, edición Carta de 934 páginas, ha sido localizado en la biblioteca del proyecto y se han cotejado la tabla 6.1 y tres ejercicios del capítulo 6. **No** se ha verificado todavía la totalidad de las modalidades, ejercicios, tablas ni constantes de las 28 aplicaciones. El PDF completo no forma parte del ZIP de software (licencia y distribución independientes).

## 4. Reproducción

```bash
python -m unittest discover -s pruebas_revision -p test_estabilidad_inversos_empiricos.py -v
python -m unittest discover -s pruebas_revision -v
python capitulo_14/combustion.py --self-test
```

Los registros íntegros están disponibles en `REVISIONES/logs_estabilidad_2026_11_07/`. **No se ha publicado ninguna actualización en GitHub ni en Zenodo.**

## 5. Referencias metodológicas

- NIST Chemistry WebBook, parámetros Antoine del agua y sus intervalos de temperatura: https://webbook.nist.gov/cgi/cbook.cgi?ID=C7732185&Type=ANTOINE
- University of Illinois, *Condition Numbers*, explicación de sensibilidad a perturbaciones de datos: https://cs357.cs.illinois.edu/textbook/notes/condition.html
- Kenney, Laub y Reese, *Statistical Condition Estimation for Linear Systems* (SIAM): https://doi.org/10.1137/S1064827595282519

## 6. Primer cotejo real con el libro

Referencia: *Estequiometría y cálculos químicos: Fundamentos, balances de materia y aplicaciones*, edición Carta, 934 páginas, tabla 6.1 (página impresa 271), ejercicios 6.B.11, 6.B.14 y 6.B.15 (página impresa 293), apéndice E de respuestas seleccionadas (página impresa 917). La comparación se ha realizado con la copia del libro disponible en la biblioteca del proyecto.

**Discrepancia corregida — Amoníaco.** El código anterior tenía para el amoníaco `A=6,48536`, `B=1277,026`, `C=−56,340` y rango `179–261 K`, que **no coinciden** con la tabla 6.1 del libro. Se han sustituido por **`A=6,86886`, `B=1113,928`, `C=−10,409` y `240–372 K`** (presión en kPa y temperatura en K). Los otros diez juegos de constantes y los once intervalos ahora coinciden con la tabla impresa. A 300 K, la correlación corregida da aproximadamente **1052,7 kPa**, dentro de su intervalo. No debe utilizarse la antigua correlación fuera del rango para el que fue ajustada.

**Contraste de ejercicios:**

| Ejercicio | Resultado reproducido | Comparación |
|---|---|---|
| 6.B.11 | Interpolación lineal: 20,25 kPa; Clausius: 18,737 kPa | Apéndice: 20,3 y 18,7 kPa |
| 6.B.14 | n-heptano a 350 K: Lee-Kesler 50,893 kPa; Antoine 51,370 kPa | Enunciado y constantes del libro |
| 6.B.15 | Metanol a 300/320 K: 18,615/48,395 kPa; ΔHvap=38,130 kJ/mol | Apéndice: 18,6/48,4 kPa y 38,1 kJ/mol |

Se han incorporado **cuatro pruebas nuevas de cotejo**, incluida una comprobación de las 11 entradas de la tabla 6.1. La identificación de una discrepancia no demuestra que las constantes antiguas sean inválidas para *otro* intervalo; demuestra que eran incompatibles con la edición del libro y con el rango declarado para sus ejercicios.
