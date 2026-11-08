# Cotejo científico — Bloque X (copia local no publicada)

**Fecha:** 7 de noviembre de 2026. **Base:** revisión de 457 pruebas; **resultado:** 482/482 pruebas transversales correctas.

Se incorporan **21 ejercicios numéricos diferentes** de los capítulos 5–15 y cuatro controles de entradas no físicas en el capítulo 8. La matriz individual está en `MATRIZ_COTEJO_BLOQUE_10.json`; la cobertura de los 556 identificadores, en `INVENTARIO_COBERTURA_556.csv` y `RESUMEN_COBERTURA_CAPITULOS.csv`.

## Incidencia reproducible y corrección

En `disoluciones_no_ideales.py`, `mae_rmse()` devolvía resultados no finitos ante observaciones `NaN`; asimismo, por difusión de NumPy podía comparar vectores de longitud desigual sin advertencia. `azeotrope_margules1_analytic()` trataba un parámetro `NaN` como ausencia de azeótropo, y `azeotrope_margules1_threshold()` podía devolver `NaN`. Ahora estas funciones rechazan explícitamente entradas no finitas y series estadísticas incompatibles.

El caso positivo **8.B.12** conserva `x_az=0,695835` y `P_az=89,3934 kPa`; el **8.B.15** reproduce EMA/RECM de los dos ajustes dentro de sus tolerancias. Esta corrección no altera los modelos físicos ni introduce nuevas ecuaciones.

## Balance de cobertura

| Tipo | Inventario | Con cotejo específico | Pendientes |
|---|---:|---:|---:|
| A — conceptuales | 206 | 0 | 206 |
| B — numéricos | 202 | 156 | 46 |
| C — aplicados e integradores | 148 | 97 | 51 |
| **Total** | **556** | **253** | **303** |

**Importante:** los 206 ejercicios A se han inventariado, pero siguen pendientes de lectura y validación conceptual. La revisión de los B/C compara casos seleccionados con las respuestas impresas; cuando un problema utiliza funciones más operaciones externas, la matriz lo indica. La ejecución de `unittest` no certifica experimentalmente las correlaciones ni que todos los recorridos de la interfaz estén cubiertos.

## Reproducción desde la raíz del repositorio

```bash
python -m unittest discover -s pruebas_revision -p test_cotejo_bloque_10.py -v
python -m unittest discover -s pruebas_revision -q
python -m compileall -q capitulo_* pruebas_revision
```

Se han ejecutado correctamente las autopruebas de los capítulos 9, 10, 11, 13, 14 y 15, con registro en `REVISIONES/logs_cotejo_10/autopruebas.log`. La compilación termina sin errores. La release pública `v0.9.0` y los DOI no han sido modificados.
