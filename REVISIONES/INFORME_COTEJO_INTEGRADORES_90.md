# Tercer bloque: cotejo de ejercicios integradores (7 de noviembre de 2026)

**Versión de trabajo, no publicada.** Basado en el PDF definitivo de 934 páginas y el solucionario desarrollado de 220 páginas, ambos conservados únicamente en el entorno de auditoría y **no incluidos en este repositorio**.

**Resultados:** 30 métodos nuevos; 22 ejercicios tipo C distintos de los capítulos 7–15. Total acumulado: **262 pruebas** y **90 ejercicios distintos cotejados** (68 previos + 22). Todas las 262 pruebas transversales pasan en el entorno local; pasan también las pruebas específicas de los capítulos 9, 10, 11, 13, 14 y 15. Sintaxis compilable. No se ejecutó esta copia en GitHub Actions ni en Python 3.11.

## Incidencia verificada y corregida en el capítulo 8

La función `bubble_pressure_gamma_phi()` aceptaba `x` negativos o sin suma uno, factores `NaN`/infinitos, y arrays de una componente difundidos por NumPy a dos componentes, generando presiones y fracciones molares sin significado físico. Se ha incorporado validación de dimensiones, composición, temperatura, finitud, positividad y salida, conservando los resultados correctos del ejercicio **8.C.5**: `P_mod = 395,0 kPa`, `P_gamma_phi = 424,586704805492 kPa`, `y1 = 0,66534267`.

La formulación considera factores tabulados constantes como exige el enunciado. No equivale a γ–φ con auto-consistencia presión/composición ni certifica parámetros experimentales.

## Trazabilidad de los ejercicios

| Ejercicio | Pág. PDF libro | Magnitud contrastada |
|---|---:|---|
| 7.C.1 | 363 | Raoult (metanol/agua), presión, vapor y desviación |
| 7.C.3 | 364 | Flash binario, Rachford–Rice y balances de componente |
| 7.C.5 | 364 | Antoine, presión y temperatura de burbuja (puntos seleccionados) |
| 8.C.1 | 461 | Azeótropo Margules y punto de la curva P–x–y |
| 8.C.3 | 462 | Derivadas de Margules y Gibbs–Duhem |
| 8.C.5 | 463 | γ–φ, presión y composición; ocho familias de entradas inválidas |
| 9.C.1 | 517 | Dos estados de coexistencia; masas y cierre |
| 9.C.3 | 518 | Arrastre agua–anilina, proporción másica y temperatura |
| 10.C.1 | 589 | Dos fundentes, pureza, crioscopía y fuerza iónica |
| 10.C.3 | 589 | Agua de mar ideal, molalidades y fuerza iónica (aproximación) |
| 11.C.1 | 661 | Mezcla de medios DMEM, balances simultáneos |
| 11.C.3 | 662 | Biorreactor, cierre de caudal y consumo de glucosa |
| 12.C.1 | 714 | Evaporador y cristalizador en cascada; recuperación |
| 12.C.3 | 715 | Cristalización, retención de licor y secado (última etapa algebraica) |
| 13.C.1 | 762 | Precipitación y filtración; balances equivalentes |
| 13.C.3 | 763 | Dos rutas de reacción, extensiones y carbono |
| 14.C.1 | 809 | Mezcla combustible con inerte, aire y gases secos |
| 14.C.3 | 809 | Combustión incompleta, defecto de aire y gas seco |
| 14.C.5 | 809 | Inversión de glucosa y ácido palmítico |
| 15.C.1 | 887 | Calentamiento y humidificación isoterma |
| 15.C.3 | 888 | Condensación frigorífica y agua separada |
| 15.C.5 | 888 | Mezcla adiabática; contraste con entalpías tabuladas redondeadas |

Se mantuvo el número de métodos distinto del número de ejercicios: 8.C.5 tiene métodos adicionales de validación, y otros ejercicios se contrastan en dos estados o etapas. Las 22 referencias son **nuevas y no duplican** las 68 anteriores.

## Precisiones y límites

- **12.C.1:** el programa de cristalización recibe **masa inicial de soluto**, no masa total de disolución. La equivalencia entre 30,0 y 20,0 % en masa y solubilidades es 42,8571 y 25,0 g de KCl/100 g de agua; el modelo reproduce 75 kg de cristales y 525 kg de licor sobre 600 kg alimentados. Si se introducen menos cifras significativas (por ejemplo `25` en lugar de `25,0000`), cambia únicamente la representación redondeada.
- **12.C.3:** el programa obtiene directamente la masa cristalizada; la recuperación de sal retenida y el secado se completan con un balance algebraico verificado, no con una función única integrada del programa.
- **13.C.1 y 13.C.3:** la prueba utiliza el solucionador lineal de balances para las ecuaciones equivalentes al modelo del libro; no automatiza el diálogo completo del módulo reactivo.
- **15.C.5:** el solucionario adopta entalpías suministradas (48,2 y 76,3 kJ/kg); el programa calcula entalpía mediante su correlación con T y razón de humedad. Se emplea tolerancia explícita por la pequeña diferencia entre datos tabulados y modelo.
- **10.C.1 y 10.C.3:** los valores idealizados de crioscopía y fuerza iónica no son predicciones válidas de salmueras concentradas; no se ha comprobado un modelo Pitzer.
- No se han verificado todos los apartados narrativos, representaciones gráficas, rangos experimentales o incertidumbres de los 90 ejercicios. Entre los 556 identificadores inventariados, siguen pendientes de cotejo **466**; algunos son conceptuales y no son objeto directo del software.

## Reproducir

```bat
python -m unittest discover -s pruebas_revision -p test_cotejo_integradores_03.py -v
python -m unittest discover -s pruebas_revision -v
python -m compileall -q capitulo_02 capitulo_03 capitulo_04 capitulo_05 capitulo_06 capitulo_07 capitulo_08 capitulo_09 capitulo_10 capitulo_11 capitulo_12 capitulo_13 capitulo_14 capitulo_15
```

Los registros de ejecución están en `REVISIONES/logs_integradores_03/`. GitHub y Zenodo no se han actualizado.
