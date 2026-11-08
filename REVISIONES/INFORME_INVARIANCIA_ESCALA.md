# Contrastes adicionales — Invariancia de escala y productos de combustión

**Fecha:** 7 de noviembre de 2026  
**Estado:** copia local acumulada para futura revisión 1.0.0; NO publicada en GitHub o Zenodo.  
**Base:** revisión acumulada de redes de materia e inversiones (114 pruebas transversales).

## Problema detectado y solución aplicada

### Capítulo 11, redes de materia

`resolver_red` aplicaba a los caudales negativos una tolerancia de `1e-8·max(1, |total|)`. Para una alimentación de 1·10⁻¹² y un consumo de 2·10⁻¹² podía declarar «único» y sustituir una salida de −1·10⁻¹² por cero, aunque la salida era físicamente imposible. Además, consideraba nula cualquier composición con caudal inferior a `EPS = 1e-10`, aunque fuera una corriente positiva válida.

**Corrección:** criterio de rechazo de corrientes negativas proporcional al mayor caudal calculado en la red, sin suelo absoluto de 1; cálculo de fracciones para todo caudal positivo. Se conserva una pequeña tolerancia relativa para absorber el redondeo numérico. Esto no resuelve por sí solo problemas mal condicionados.

### Capítulo 14, combustión

Diversos umbrales absolutos (`TOL=1e-9`) trataban cantidades positivas pequeñas como ausentes: para 1·10⁻¹² mol de CH₄ se obtenían erróneamente 0 mol de O₂ y ningún producto. Los mismos umbrales afectaban a SOₓ/NOₓ elegidos, composiciones húmedas/secas, déficit de comburente y ciertos controles de entrada.

**Corrección:** no eliminar cantidades positivas por su pequeña magnitud, validar explícitamente finitud y signo, comprobar déficit relativo de O₂ y utilizar control relativo del cierre elemental. Se mantienen tolerancias específicas de composición para porcentajes experimentales. El usuario sigue siendo responsable de especificar los productos de S y N, y no se predice su distribución química.

## Casos de contraste independientes

| Cálculo | Base | Referencia analítica | Estado |
| --- | --- | --- | --- |
| Red: consumo mayor que alimentación | 1·10⁻¹² | Salida −1·10⁻¹²; rechazar | Correcto |
| Red: consumo del 20 % | 1·10⁻¹² | Salida 8·10⁻¹³; fracción A=1 | Correcto |
| Mezclador con reciclado especificado | 100 + 30 | Corriente intermedia 130; producto neto 100 | Correcto |
| Reciclado no especificado | 100 | Problema indeterminado | Correcto |
| CH₄ + 2 O₂ → CO₂ + 2 H₂O | 1 y 10⁻¹² mol | O₂=2·n; CO₂=n; H₂O=2·n | Correcto |
| CH₄O + 1,5 O₂ → CO₂ + 2 H₂O | 1 y 10⁻¹² mol | O₂=1,5·n | Correcto |
| C₂H₆S, S→SO₂ | 1 mol | 4,5 mol O₂ | Correcto |
| C₂H₆S, S→SO₃ | 1 mol | 5 mol O₂ | Correcto |
| C₂H₅N, N→N₂ / NO / NO₂ | 1 mol | O₂ = 3,25 / 3,75 / 4,25 mol | Correcto |
| Gases húmedos (CO₂, H₂O, N₂) = (1,2,3) | 1 y 10⁻¹² | yCO₂ húmeda 1/6; seca 1/4 | Correcto |

## Batería acumulada

- 127 pruebas transversales mediante `python -m unittest discover -s pruebas_revision -v` (**114 anteriores + 13 nuevas**).
- Capítulo 9: 24 pruebas.
- Capítulo 10: 39 comprobaciones de electrolitos y 38 de coligativas.
- Capítulo 11: 58 pruebas.
- Capítulo 13: 12 pruebas.
- Capítulo 14: 23 autocomprobaciones.
- Capítulo 15: 12 grupos de validación.
- Compilación sintáctica completa de los capítulos 2–15 y de las pruebas.

Todos estos conjuntos han terminado sin errores **en el entorno local actual**. La ejecución en GitHub Actions/Python 3.11 y 3.13 requerirá subir y probar la futura revisión; la versión pública `v0.9.0` y sus DOI no cambian.

## Reproducción

```bash
python -m unittest discover -s pruebas_revision -v
python -m unittest discover -s pruebas_revision -p test_escalas_y_productos_combustion.py -v
```

Logs originales: `REVISIONES/logs_2026_11_07/`.

## Límites pendientes antes de una versión 1.0.0

No se han certificado todos los intervalos empíricos, todos los escenarios de combustión incompleta ni todas las composiciones multicomponente. Tampoco se ha cotejado sistemáticamente cada ejercicio del libro. Los casos numéricos de esta revisión comprueban consistencia algebraica y conservación de materia; no garantizan idoneidad de un modelo químico para cualquier temperatura o condición real.
