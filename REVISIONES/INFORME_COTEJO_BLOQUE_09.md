# Auditoría científica del software — Bloque IX (copia de trabajo)

**Fecha:** 7 de noviembre de 2026. **Estado:** no publicado en GitHub ni Zenodo.

## Resultados verificables

- Batería anterior: 418/418 pruebas. Batería nueva: 39/39. **Acumulado: 457/457**, ejecutado localmente con `unittest`.
- 33 ejercicios del libro contrastados en este bloque: **21 identificadores nuevos** y 12 recontrastes independientes. Acumulado: **232 de 556**; quedan 324 sin cotejo individual.
- También pasan las autopruebas existentes de los capítulos 9, 10, 11, 13, 14 y 15 y la compilación de los programas. Las autocomprobaciones específicas se registran por separado de las 457 pruebas transversales.
- El conjunto no valida experimentalmente todas las correlaciones ni demuestra que todos los modos de uso hayan sido cubiertos.

## Defecto corregido: inversión de Antoine en el capítulo 7

La clase `Component` de `equilibrio_liquido_vapor.py`, al construirse directamente desde una biblioteca, admitía coeficientes o límites de Antoine no finitos. Su método `boiling_temperature()` permitía una presión `NaN` y devolvía `NaN`, y con presión infinita podía entregar una temperatura finita sin significado físico. `psat()` podía evaluar temperatura infinita sin rechazarla. **Antes de la corrección**, la inversión con presión infinita devolvía 45,0 K para los coeficientes de prueba A=6, B=1250 y C=-45. La corrección rechaza estos casos con `ValueError`, comprueba temperatura absoluta positiva y límites válidos. Las soluciones normales se conservan.

El contraste positivo 7.B.10 sigue dando una temperatura de burbuja de 340,55835 K; para 7.B.11, el cálculo de dos fases por Rachford–Rice da fracción vaporizada cercana a 0,51343. En 7.B.13 la fracción vaporizada es 0,57898986.

## Límites de interpretación

La matriz distingue **función del programa** de **función + cálculo auxiliar**. Los problemas de balances encadenados no significan que exista un menú automático para todas sus operaciones. El cotejo es contra los datos y soluciones impresos, con tolerancias explicitadas en el código de las pruebas. No sustituye a una validación frente a resultados experimentales o normas metrológicas aplicables.

## Reproducción

```bash
python -m unittest discover -s pruebas_revision -p test_cotejo_bloque_09.py -v
python -m unittest discover -s pruebas_revision -q
python -m compileall -q .
```

Matriz: `REVISIONES/MATRIZ_COTEJO_BLOQUE_09.json`; código de pruebas: `pruebas_revision/test_cotejo_bloque_09.py`. La edición pública `v0.9.0` permanece sin cambios.
