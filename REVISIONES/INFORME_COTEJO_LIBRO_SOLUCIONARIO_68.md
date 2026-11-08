# Segunda ampliación del cotejo libro–solucionario–software (7-11-2026)

**Estado:** copia acumulada de trabajo para v1.0.0. No se ha alterado GitHub ni Zenodo.

## Resultado de ejecución

- 41 métodos nuevos en `pruebas_revision/test_cotejo_libro_segundo_bloque.py`: **41/41 superados**.
- Cotejo de **38 ejercicios distintos adicionales**, capítulos 2–15.
- Total de ejercicios distintos en las dos matrices: **68** (30 + 38).
- Batería transversal acumulada: **232/232 métodos superados** en Python 3.13.5.
- Compilación completa de los capítulos 2–15: correcta.
- Autopruebas cap. 3, 9, 10 (dos módulos), 11, 13, 14 y 15: superadas.

## Hallazgo funcional y corrección: ejercicio 5.B.2

La resolución de van der Waals del libro proporciona **a = 3,66 L²·bar·mol⁻²** y **b = 0,0428 L·mol⁻¹** para CO₂ a 300 K y 10 bar. La versión anterior del programa obtenía a y b a partir de propiedades críticas, por lo que se aproximaba, pero no reproducía exactamente esos parámetros.

Se añadió `vdw_state_from_ab(T, P, a, b, M=None, phase="vapor")` y el modo CLI `estado --modelo vdw --vdw-a ... --vdw-b ...`, conservando la parametrización tradicional.

Resultado: `Z = 0,95677794`, `Vm = 2,3865283 L/mol`, `P_reconstructed = 10,000000 bar`.

Comando Windows:

```bat
python capitulo_05/gases_reales.py --sigfigs 8 estado --gas CO2 --T 300 --P 10 --modelo vdw --vdw-a 3.66 --vdw-b 0.0428
```

Se rechazan entradas no finitas, negativas, ceros y opciones incompletas. Las unidades de a y b son explícitas; el método no extrapola automáticamente parámetros a otras sustancias ni constituye validación experimental.

## Matriz abreviada (38 ejercicios adicionales)

| Ejercicio | Página PDF libro | Prueba asociada | Estado |
|---|---:|---|---|
| 2.B.2 | 96 | `test_2_B_2_presion_atm_pa_psi` | OK |
| 2.B.3 | 96 | `test_2_B_3_calorias` | OK |
| 2.B.4 | 96 | `test_2_B_4_velocidad` | OK |
| 3.B.1 | 158 | `test_3_B_1_moles_co2` | OK |
| 3.B.6 | 158 | `test_3_B_6_cinc_hidrogeno` | OK |
| 4.B.3 | 190 | `test_4_B_3_gasometro_metano` | OK |
| 4.B.4 | 190 | `test_4_B_4_mezcla_ideal_molar_y_masica` | OK |
| 4.B.5 | 190 | `test_4_B_5_mezcla_binaria_resuelta_por_balances` | OK |
| 4.B.6 | 190 | `test_4_B_6_masa_molar_porcentajes` | OK |
| 5.B.2 | 246 | `test_5_B_2_vdw_co2_casi_mismos_parametros` | OK |
| 5.B.3 | 246 | `test_5_B_3_rk_amoniaco` | OK |
| 5.B.5 | 247 | `test_5_B_5_virial_rama_vapor` | OK |
| 6.B.1 | 291 | `test_6_B_1_clausius_eter` | OK |
| 6.B.7 | 292 | `test_6_B_7_antoine_acrilonitrilo` | OK |
| 6.B.9 | 292 | `test_6_B_9_titulo_vapor_entalpia_tabla_enunciado` | OK |
| 7.B.2 | 358 | `test_7_B_2_raoult_masas_iguales` | OK |
| 7.B.3 | 358 | `test_7_B_3_rocio_ideal` | OK |
| 7.B.4 | 358 | `test_7_B_4_burbuja_antoine` | OK |
| 8.B.4 | 457 | `test_8_B_4_margules_asimetrico` | OK |
| 9.B.2 | 513 | `test_9_B_2_coexistencia_beysens` | OK |
| 10.B.2 | 587 | `test_10_B_2_naftaleno_crioscopia` | OK |
| 10.B.3 | 587 | `test_10_B_3_vant_hoff_experimental` | OK |
| 10.B.4 | 587 | `test_10_B_4_osmosis_glucosa` | OK |
| 11.B.5 | 658 | `test_11_B_5_corriente_etanol_agua` | OK |
| 11.B.8 | 658 | `test_11_B_8_dilucion_glucosa` | OK |
| 12.B.1 | 711 | `test_12_B_1_secado_jabon` | OK |
| 12.B.5 | 712 | `test_12_B_5_dos_evaporadores` | OK |
| 13.B.2 | 759 | `test_13_B_2_descomposicion_amoniaco` | OK |
| 13.B.3 | 759 | `test_13_B_3_hidrogenacion_acetaldehido` | OK |
| 13.B.8 | 760 | `test_13_B_8_reacciones_sucesivas` | OK |
| 14.B.1 | 807 | `test_14_B_1_combustion_etano` | OK |
| 14.B.2 | 807 | `test_14_B_2_combustion_propanol` | OK |
| 14.B.3 | 807 | `test_14_B_3_aire_teorico_metano` | OK |
| 14.B.4 | 807 | `test_14_B_4_exceso_aire_propano` | OK |
| 14.B.7 | 808 | `test_14_B_7_mezcla_inertes_aire` | OK |
| 15.B.3 | 883 | `test_15_B_3_saturacion_35_grados` | OK |
| 15.B.4 | 884 | `test_15_B_4_humedad_relativa_saturacion` | OK |
| 15.B.5 | 884 | `test_15_B_5_vapor_por_masa_aire_seco` | OK |

## Métodos completos e inferencias

En algunos ejercicios se utiliza una función pública del programa para obtener las magnitudes principales y una operación algebraica adicional para completar el enunciado; en otros se comprueba directamente la salida por consola. En 5.B.2 hay varias pruebas de un mismo ejercicio (biblioteca, datos explícitos, validación de parámetros y CLI), que no deben contarse como ejercicios distintos.

No se ha comprobado cada apartado de los 68 ejercicios con el mismo grado de cobertura; la matriz identifica la magnitud comprobada. Algunos métodos usan valores aportados directamente por el enunciado (por ejemplo, la presión de saturación de agua en 15.B.3) en lugar de validar una correlación.

## Reproducción y límites

```bat
python -m unittest discover -s pruebas_revision -p test_cotejo_libro_segundo_bloque.py -v
python -m unittest discover -s pruebas_revision -v
python -m compileall -q capitulo_02 capitulo_03 capitulo_04 capitulo_05 capitulo_06 capitulo_07 capitulo_08 capitulo_09 capitulo_10 capitulo_11 capitulo_12 capitulo_13 capitulo_14 capitulo_15
```

El conjunto corresponde a una **revisión de regresión reproducible**, no a una certificación universal. Quedan sin contraste numérico específico aproximadamente 488 de los 556 identificadores inventariados; algunos ejercicios son conceptuales y no están destinados a ejecución informática. No se han efectuado pruebas completas del nuevo paquete en GitHub Actions ni en Python 3.11 en esta fase.

Los PDF del libro y del solucionario no se empaquetan ni se publican en el repositorio.
