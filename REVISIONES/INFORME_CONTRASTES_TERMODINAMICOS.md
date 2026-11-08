# Revisión termodinámica ampliada — 7 de noviembre de 2026

**Estado:** candidato local pendiente de integrar. No modificar la release archivada `v0.9.0` ni asignar aún `v1.0.0`.

## Alcance

Se ha ampliado la auditoría de los capítulos 5 a 8 y 15, manteniendo las anteriores verificaciones de las 28 aplicaciones. Se han incorporado 14 métodos nuevos de prueba (que ejecutan cientos de casos individuales en bucles), alcanzando **99 métodos de prueba transversal**. Se han repetido las pruebas ya existentes de los capítulos 9, 10, 11, 13, 14 y la validación del 15.

## Incidencias corregidas en esta ampliación

- **Capítulo 5, gases reales.** Rechazo explícito de `NaN`, `inf` y `-inf` y de estados con temperatura o presión no positivas. Anteriormente se aceptaban en `parse_num` y determinados cálculos terminaban en excepciones no interpretables o resultados indefinidos.
- **Capítulo 7, equilibrio líquido-vapor.** Un componente de fracción molar cero no debe imponer su intervalo de Antoine cuando la propiedad solicitada corresponde al componente presente. Se han corregido los casos puros y añadido una marca `—` para presión de vapor no evaluable de la especie ausente. No se fuerza `P_i*=0`. En mezclas verdaderamente multicomponentes, los intervalos deben ser compatibles.
- **Capítulos 6 y 7.** Rechazo de números no finitos en los conversores de las entradas de línea de órdenes.
- **Capítulo 15, psicrometría.** Rechazo de razones de humedad no finitas antes de normalizar valores cercanos a cero.

## Contrastes numéricos adicionales

- **Ecuaciones cúbicas:** 200 estados gaseosos diluidos con control del residuo de la ecuación polinómica y del límite `Z → 1`, más 12 condiciones de coexistencia del metano con comprobación de igualdad de fugacidades.
- **Antoine frente a IAPWS:** 11 puntos del agua entre 284 y 441 K. Error relativo absoluto de la tabla docente del 0,13 % al 2,33 %; la correlación no puede sustituir una formulación de referencia en aplicaciones de mayor precisión.
- **Antoine NIST:** cuatro puntos con parámetros de agua de 273–303 K, convertidos de bar a kPa, contrastados con IAPWS. Se usan como referencias externas, no como constantes nuevas del programa.
- **Burbuja/rocío de Raoult:** 200 casos con recuperación de temperatura y composición mediante inversión de las condiciones de equilibrio.
- **Flash con Rachford–Rice:** 500 composiciones y conjuntos de coeficientes de reparto, con verificaciones de los cierres molares, de fracciones y de la región bifásica.
- **Rayleigh, α constante:** 200 problemas contrastados con la integral analítica `(ln(x0/xf) - α ln((1-x0)/(1-xf)))/(α-1)`.
- **Modelos de actividad:** cinco composiciones por modelo, Margules 1, Margules 2, Van Laar y Wilson, con comprobación diferencial de Gibbs–Duhem.
- **Psicrometría:** conservación de vapor y entalpía al mezclar dos corrientes, y coherencia del orden del punto de rocío y temperatura de bulbo húmedo en veinte estados.

## Pruebas y documentación

Pruebas reproducibles en `pruebas_revision/test_contrastes_termodinamicos.py`. La ejecución conjunta usa `python -m unittest discover -s pruebas_revision -v`. Los manuales individuales de seis aplicaciones incorporan una nota con límites y resultados de esta ampliación.

**Limitación fundamental:** estas comprobaciones demuestran consistencia de los casos elegidos, no validación universal de correlaciones, parámetros empíricos, representaciones gráficas o modalidades no contrastadas. Continúa pendiente la comparación detallada con todos los ejercicios del libro y una validación externa más amplia de SIT/Pitzer, gases reales próximos al punto crítico, redes complejas e inversiones de combustión.

## Referencias externas consultadas

- IAPWS, *Revised Supplementary Release on Saturation Properties of Ordinary Water Substance* (1992): https://www.iapws.org/relguide/Supp-sat.html
- NIST Chemistry WebBook, *Antoine Equation Parameters: Water*: https://webbook.nist.gov/cgi/cbook.cgi?ID=C7732185&Type=ANTOINE
- ASHRAE, *Handbook — Fundamentals, Chapter 1: Psychrometrics*: https://handbook.ashrae.org/Handbooks/F17/SI/f17_ch01/f17_ch01_si.aspx
