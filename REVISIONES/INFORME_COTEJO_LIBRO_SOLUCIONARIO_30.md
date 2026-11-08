# Cotejo científico inicial con libro definitivo y solucionario — 7-11-2026

Fuentes: **Estequiometría y cálculos químicos**, edición Carta definitiva, 934 páginas; y **Solucionario desarrollado**, 220 páginas, capítulos 2–15. Ninguna de las dos obras se incorpora ni distribuye con el software.

## Alcance y resultados

- Índice estructural: 556 identificadores de ejercicios correspondientes entre libro y solucionario después de normalizar dos incidencias de presentación/extracción; no significa haber comprobado sus 556 resultados.
- 30 casos de regresión comparados en los 14 capítulos (2–15); **30/30 satisfactorios**.
- Los 28 programas reciben al menos una comprobación asociada a un ejercicio real del libro. Algunos casos verifican solamente una parte del ejercicio y/o una función del programa.
- Batería transversal acumulada: **191/191 métodos** (161 previos + 30 nuevos).
- Pruebas específicas cap. 9 (24), 10 (39 y 38), 11 (58), 13 (12), 14 (23), 15 (12 grupos) repetidas sin errores; cap. 3 `--autoprueba` superada.
- La coincidencia con resultados desarrollados no valida experimentalmente los modelos ni cubre todos los menús y parámetros.

## Hallazgos y cambios

1. **Ejercicio 3.B.20, Hall (capítulo 3):** el programa original convertía °Bx a GE interpolando una tabla de sacarosa 0–60 °Bx, no mediante Hall. Para 18 °Bx la tabla da GE=1,07404253614 y Hall da GE=1,074221119568 (diferencia ≈0,00017858343). Se añadió opción explícita Hall (0–33 °Bx) en `densidades_y_escalas.py`, preservando la tabla; aporta valor GE y densidad a partir de la densidad de referencia. Ambas aproximaciones coinciden a tres decimales, pero no son el mismo modelo físico.
2. **Ejercicio 12.B.14, recuperación:** `separacion_corrientes.py` pedía ambas composiciones de salida; ahora admite el modo optativo `--recuperacion`, conservando el modo previo. El ejemplo de 600 kg/h, 15%, 45%, recuperación 90% devuelve 180 kg/h, 420 kg/h y una concentración interna 2,142857…% en la segunda corriente. El formato conservador puede mostrar 2,1%; se imprime también el valor interno para cotejo (no implica más precisión experimental).
3. **Errata editorial, libro p. 516:** el ejercicio aparece impreso **«9.B10.»** en lugar de «9.B.10.». No afecta al cálculo; conviene conservarlo en una fe de erratas de la edición cerrada.
4. El ejercicio **7.A.8** está correctamente impreso en la página 356, pero un extractor de texto lo concatena con una fórmula; no es un error del libro.

## Matriz de 30 ejercicios contrastados

| Ejercicio | Página libro | Programa(s) de referencia | Resultado | Observación |
|---|---:|---|---|---|
| 2.B.1 | 96 | unidades_y_dimensiones | OK | 125 ft³ = 3,54 m³ (3 cifras). |
| 3.B.5 | 158 | ajuste_ecuaciones, masa_molar | OK | 11,5 g Na => 29,2 g NaCl. |
| 3.B.11 | 158 | densidades_y_escalas | OK | 180 g sacarosa / 600 g => 30,0 Bx. |
| 3.B.12 | 159 | ajuste_ecuaciones | OK | 2 : 15 : 14 : 6. |
| 3.B.13 | 159 | reactivo_limitante | OK | H2 limitante; NH3=20 mol; N2 restante=2 mol. |
| 3.B.16 | 159 | conversion_rendimiento_selectividad | OK | 100 mol etanol, 30 finales -> X=70%. |
| 3.B.20 | 161 | densidades_y_escalas | OK | Hall B=18 -> GE=1,074221119568. |
| 4.B.1 | 190 | gases_ideales_y_mezclas | OK | 0,716 y 2,86 g/L en condiciones normales. |
| 5.B.1 | 246 | gases_reales | OK | Vm ideal 3,6376 L/mol, Z=0,92 => 3,3466. |
| 6.B.11 | 293 | presion_vapor | OK | lineal 20,25; CC 18,7372 kPa. |
| 6.B.13 | 293 | vapor_agua | OK | vapor sobrecalentado; x~0,494. |
| 6.B.15 | 294 | presion_vapor | OK | 18,6 y 48,4 kPa; delta Hvap~38,1 kJ/mol. |
| 7.B.1 | 357 | equilibrio_liquido_vapor | OK | xhep 0,853125; yhep 0,892707. |
| 7.C.8 | 366 | operaciones_liquido_vapor | OK | L/F=V/F=0,5. |
| 8.B.3 | 456 | disoluciones_no_ideales | OK | gamma=(1,80038;1,11405); gE/RT=0,252. |
| 9.B.1 | 513 | equilibrio_liquido_liquido | OK | mL1=0,94818; mL2=1,55182 kg. |
| 9.B.5 | 515 | inmiscibles_y_arrastre_vapor | OK | T=342,27133 K, yagua=.296189. |
| 10.B.1 | 586 | propiedades_coligativas | OK | m=.39964, deltaTf=.7433, deltaTb=.2046. |
| 10.B.6 | 587 | disoluciones_electroliticas | OK | I=.05; gamma monovalente=.8215; Ca2+=.4555. |
| 11.B.7 | 658 | balances_materia | OK | 250 kg/h y wNaCl=0,160. |
| 12.B.3 | 711 | secado | OK | producto 101,44 kg; evaporada 18,6 kg. |
| 12.B.4 | 712 | evaporacion | OK | masa final 100 g, agua eliminada 150 g. |
| 12.B.7 | 712 | filtracion | OK | torta 28,3 kg; filtrado 221,69 kg. |
| 12.B.8 | 712 | cristalizacion | OK | agua~251,256 kg; cristales 10,3 kg. |
| 12.B.14 | 714 | separacion_corrientes | OK | recuperación 90%, flujos 180/420 kg/h. |
| 12.C.4 | 715 | extraccion_liquido_liquido | OK | E1 62,6866; E2 70,4631; E3 73,6594 %. |
| 13.B.1 | 759 | balance_una_reaccion | OK | xi=.250 mol, NO2=1 mol, O2=.250 mol. |
| 13.B.7 | 760 | balance_varias_reacciones | OK | xi=(3;2), A=7, B=3, C=4. |
| 14.B.6 | 808 | combustion | OK | 24,5 mol O2 y 117 mol aire teórico. |
| 15.B.2 | 883 | psicrometria | OK | pv=1,5197 kPa, w=.00960, ws=.0149, S=64,5 %. |

## Reproducción local

```bash
python -m unittest discover -s pruebas_revision -p test_cotejo_libro_solucionario.py -v
python -m unittest discover -s pruebas_revision -v
python capitulo_03/densidades_y_escalas.py --autoprueba
python capitulo_12/separacion_corrientes.py --recuperacion
```

El comando `--recuperacion` solicita, por este orden: caudal de alimentación (kg/h), porcentaje másico de soluto en alimentación, porcentaje másico en la corriente concentrada y recuperación porcentual del soluto en esa corriente.

## Pendiente para versión 1.0.0

Este muestreo no es un cotejo exhaustivo de los restantes ejercicios (526 identificadores fuera de esta nueva batería), ni de todos los modos de entrada, incertidumbres, redondeos, formatos de exportación o modelos empíricos. Debe continuarse con evaluación por submodalidad, casos extremos, dependencia de constantes y comprobación de trazabilidad. La versión publicada `v0.9.0` y sus DOI no se modifican en esta fase.
