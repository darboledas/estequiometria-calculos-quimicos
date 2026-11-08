# Comprobaciones automáticas

## Ejecución desde la raíz del repositorio

```powershell
python -m unittest discover -s pruebas_revision -v
python -m compileall -q capitulo_02 capitulo_03 capitulo_04 capitulo_05 capitulo_06 capitulo_07 capitulo_08 capitulo_09 capitulo_10 capitulo_11 capitulo_12 capitulo_13 capitulo_14 capitulo_15
python capitulo_09/pruebas_capitulo9.py
python capitulo_11/pruebas_capitulo11.py
python -m unittest discover -s capitulo_13/pruebas -v
python capitulo_10/disoluciones_electroliticas.py --selftest
python capitulo_10/propiedades_coligativas.py --selftest
python capitulo_14/combustion.py --self-test
python capitulo_15/psicrometria.py --validar
```

La segunda línea comprueba que el código Python se compila; no equivale a una comprobación de exactitud física. Las pruebas numéricas verifican casos incluidos en los conjuntos de regresión, no todos los posibles datos. La integración continua ejecuta estas pruebas con Python 3.11 y 3.13 en Ubuntu.

Si el capítulo 9 o 11 necesita importaciones de la carpeta, sus archivos incluyen el punto de entrada necesario: ejecútelos como scripts. Los programas que requieran gráficos pueden utilizar `requirements-graficos.txt`.


## Alcance de la auditoría transversal

La batería transversal cubre los 28 puntos de entrada con pruebas de casos analíticos y de salida por consola, además de once invariantes físicos/algebraicos y las pruebas específicas existentes. El resumen por aplicación y los límites se encuentran en `REVISIONES/INFORME_AUDITORIA_INTEGRAL.md`.

## Ampliación de contrastes termodinámicos (copia local no publicada)

El directorio `pruebas_revision` contiene **99 métodos** al incorporar `test_contrastes_termodinamicos.py` (14 métodos nuevos con numerosos casos internos). Se han revisado datos no finitos, extremos de composiciones, ecuaciones cúbicas, flash, Rayleigh, actividad y psicrometría. Véase `REVISIONES/INFORME_CONTRASTES_TERMODINAMICOS.md` para conocer los límites de cobertura.

## Ampliación de balances e inversiones (copia local no publicada)

La batería transversal consta de **114 métodos**, incluidos **15 métodos nuevos** en `pruebas_revision/test_balances_combustion_ampliada.py`. Se contrastan identificadores numéricos de redes, conservación de materia en varias etapas, fórmulas químicas válidas e inválidas, cálculos inversos de combustión y escalado de sistemas lineales. Las pruebas existentes de los capítulos 9, 10, 11, 13, 14 y 15 se han repetido sin fallos. Detalles: `REVISIONES/INFORME_BALANCES_E_INVERSIONES.md`.

## Invariancia de escala y productos químicos — copia local acumulada

La batería transversal se ha ampliado a **127 métodos**. El archivo `pruebas_revision/test_escalas_y_productos_combustion.py` añade 13 pruebas de redes de reciclado, escalas muy pequeñas, gases húmedos y secos, productos de S/N y rechazo de datos no físicos. Resultados y limitaciones en `REVISIONES/INFORME_INVARIANCIA_ESCALA.md`.


### Revisión de combustión incompleta y modalidades inversas (7-11-2026)

El conjunto acumulado contiene **143 métodos transversales** (127 anteriores + 16 nuevos), incluidos 150 sistemas inversos sintéticos de cuatro componentes. Todos se han ejecutado correctamente en la copia local de trabajo. Se mantiene intacta la versión publicada `v0.9.0`.

```bash
python -m unittest pruebas_revision.test_combustion_incompleta_inversos -v
python -m unittest discover -s pruebas_revision -v
```

Consulte `REVISIONES/INFORME_COMBUSTION_INCOMPLETA_INVERSOS.md` para hipótesis, balances numéricos y limitaciones. La actualización aún no ha pasado GitHub Actions de la futura versión 1.0.0.


### Estabilidad inversa y dominios empíricos (7-11-2026, no publicado)

La revisión acumulada alcanza **157 métodos transversales** (14 adicionales).
Se incorporan pruebas con ecuaciones inversas casi singulares, 200 sistemas sintéticos bien condicionados y transformaciones termodinámicas dentro de los rangos especificados.
La comprobación de desbordamientos no valida experimentalmente las correlaciones; se mantiene la necesidad de cotejo con el libro y los datos experimentales.

```bash
python -m unittest discover -s pruebas_revision -p test_estabilidad_inversos_empiricos.py -v
```

Informe: `REVISIONES/INFORME_ESTABILIDAD_INVERSOS_CORRELACIONES.md`.


### Cotejo con tabla 6.1 y ejercicios del libro (7-11-2026, no publicado)
- Se ha corregido el registro Antoine del amoníaco para coincidir con el libro (A=6,86886; B=1113,928; C=−10,409; 240–372 K).
- 4 nuevas pruebas de regresión: los 11 juegos de coeficientes de la tabla 6.1 y los ejercicios 6.B.11, 6.B.14 y 6.B.15.
- La batería transversal acumulada asciende a **161 métodos** (143 + 18 nuevos en este bloque).
- El cotejo integral de todos los ejercicios del libro continúa pendiente.


### Cotejo con libro definitivo y solucionario — 30 casos, 7-11-2026

**191 métodos transversales superados** (161 anteriores + 30 ejercicios contrastados),
con referencias a los 28 programas y los 14 capítulos (2–15). El nuevo módulo es
`pruebas_revision/test_cotejo_libro_solucionario.py`. Ejecute:

```bash
python -m unittest discover -s pruebas_revision -p test_cotejo_libro_solucionario.py -v
python -m unittest discover -s pruebas_revision -v
```

Ajuste cúbico de Hall: opción adicional en `capitulo_03/densidades_y_escalas.py`
para 0-33 °Bx, manteniendo el procedimiento tabular anterior.
`capitulo_12/separacion_corrientes.py --recuperacion` añade la entrada directa
por recuperación porcentual (12.B.14) sin modificar el modo habitual.
Véase `REVISIONES/INFORME_COTEJO_LIBRO_SOLUCIONARIO_30.md`.
El cotejo de 30 ejercicios no equivale a comprobar todos los ejercicios del libro.


### Segunda ampliación de cotejo (7-11-2026, copia local no publicada)

La batería transversal contiene **232 métodos** (191 anteriores + 41 nuevos), correspondientes a **68 ejercicios distintos** entre los dos bloques. Ejecución con Python 3.13.5; 232/232 pruebas superadas. Las autopruebas específicas y la compilación también concluyeron sin errores.

```bat
python -m unittest discover -s pruebas_revision -p test_cotejo_libro_segundo_bloque.py -v
python -m unittest discover -s pruebas_revision -v
python capitulo_05/gases_reales.py --sigfigs 8 estado --gas CO2 --T 300 --P 10 --modelo vdw --vdw-a 3.66 --vdw-b 0.0428
```

Consulte `REVISIONES/INFORME_COTEJO_LIBRO_SOLUCIONARIO_68.md` y `REVISIONES/MATRIZ_COTEJO_BLOQUE_02.json`. Los 68 ejercicios tienen grados de contraste distintos; los resultados no validan experimentalmente los modelos.


### Tercer bloque, ejercicios integradores (7-11-2026; copia local)

**262/262 pruebas transversales** y 22 ejercicios integradores tipo C nuevos (90 distintos acumulados).
Se ejecutaron las autopruebas específicas de los capítulos 9, 10, 11, 13, 14 y 15 y la compilación general, todas con resultado correcto.
Incidencia corregida: `bubble_pressure_gamma_phi()` rechazará composiciones no físicas, factores no finitos y vectores incompletos. Ver `REVISIONES/INFORME_COTEJO_INTEGRADORES_90.md`.


### Cuarto bloque — cotejo de aplicaciones y validación física (7-11-2026, no publicado)
- 26 ejercicios tipo C nuevos con resultados cotejados y trazabilidad por número/página (116 ejercicios distintos acumulados).
- 28 nuevos métodos de prueba: 26 ejercicios + 2 validaciones; total transversal **290/290**.
- Corrección `vapor_agua.quality_from_property()`: `NaN` e infinito en propiedades de entrada o nodos de saturación generan `ValueError`, sin interpretar un título indefinido como estado bifásico.
- Se documentan operaciones encadenadas resueltas por balances algebraicos, las diferencias de precisión en galones US, y los límites científicos del contraste.
- Archivos: `REVISIONES/INFORME_COTEJO_APLICADOS_116.md`, `REVISIONES/MATRIZ_COTEJO_BLOQUE_04.json`.
- GitHub y Zenodo siguen sin modificar.

### Bloque V — Cotejo integrador y Antoine gas–vapor (copia local, 7-11-2026)
- 27 pruebas nuevas (23 ejercicios + 4 controles de Antoine); **317/317** transversales; **139** ejercicios distintos.
- Ver `REVISIONES/INFORME_COTEJO_INTEGRADORES_139.md` y matriz del bloque 05.
- Nueva prueba: `python -m unittest discover -s pruebas_revision -p test_cotejo_integradores_05.py -v`.

## Bloque VI — cotejo de 23 ejercicios (copia de trabajo no publicada)

Se han ejecutado **345/345** pruebas transversales, con 28 métodos nuevos (23 ejercicios distintos, un contraste Margules/Van Laar adicional y cuatro controles de datos). Compilación y autopruebas de los capítulos 9, 10, 11, 13, 14 y 15 superadas. Consulte `REVISIONES/INFORME_COTEJO_BLOQUE_06.md` y `REVISIONES/MATRIZ_COTEJO_BLOQUE_06.json`.

```bash
python -m unittest discover -s pruebas_revision -p test_cotejo_bloque_06.py -v
python -m unittest discover -s pruebas_revision -q
```

La cobertura de 162 ejercicios no implica haber comprobado el resto del solucionario ni las condiciones experimentales de los modelos.

## Bloque VII — presión de vapor y 26 ejercicios nuevos (7-11-2026, no publicado)

- **374/374** pruebas transversales superadas; **29 métodos nuevos**, de los que 26 son ejercicios concretos del libro y 3 son validaciones físicas del capítulo 8. Acumulado de **188/556** ejercicios con algún cotejo, **368** pendientes.
- `disoluciones_no_ideales.py`: validaciones de finitud, longitud, temperatura, unidad y dominio en `DirectPsat`, `SimpleExpPsat` y `AntoinePsat`, sin alterar el cálculo válido de 8.B.8 y 8.B.11.
- Errata algebraica del solucionario **5.B.6** contrastada, conservando su resultado correcto.
- Matriz: `REVISIONES/MATRIZ_COTEJO_BLOQUE_07.json`. Informe: `REVISIONES/INFORME_COTEJO_BLOQUE_07.md`.
- Se mantiene `v0.9.0` en GitHub y Zenodo; esta copia es local, sin publicar.


## Bloque VIII — 418 pruebas, 211 ejercicios

`python -m unittest discover -s pruebas_revision -p test_cotejo_bloque_08.py -v`

`python -m unittest discover -s pruebas_revision -q`

Detalles: `REVISIONES/INFORME_COTEJO_BLOQUE_08.md` y matriz JSON. No publicado.


## Bloque IX — 457 pruebas, 232 ejercicios (sin publicar)

Se han añadido 39 pruebas: 33 ejercicios (21 nuevos y 12 recontrastados) y seis controles de entrada de Antoine en el capítulo 7. La regresión transversal acumulada pasó **457/457**; se mantiene `v0.9.0` publicada. 
Consulta `REVISIONES/INFORME_COTEJO_BLOQUE_09.md` y la matriz JSON.

## Bloque X — pruebas y cobertura (copia local no publicada)

La batería transversal supera **482 pruebas**, incluyendo 21 contrastes numéricos nuevos y 4 controles de entradas inválidas del capítulo 8. Reproducción: `python -m unittest discover -s pruebas_revision -q`. La matriz individual está en `REVISIONES/MATRIZ_COTEJO_BLOQUE_10.json`; el inventario de 556 ejercicios, en `REVISIONES/INVENTARIO_COBERTURA_556.csv`.

De 350 ejercicios numéricos/aplicados (tipos B+C), **253** tienen un cotejo específico y **97** continúan pendientes. Aparte, quedan **206** ejercicios conceptuales A por revisar. Los métodos algebraicos auxiliares no equivalen a nuevas funciones automáticas del software.


## Bloque XI — 572 pruebas

`python -m unittest discover -s pruebas_revision -q` — **572 pruebas superadas**.

La prueba nueva está en `pruebas_revision/test_cotejo_cierre_11.py` y se acompaña de `REVISIONES/INFORME_COTEJO_BLOQUE_11.md`. Los 350 ejercicios B/C tienen algún cotejo, de tipo numérico o cualitativo; los 206 A solo tienen comprobación de correspondencia editorial y quedan por revisar científicamente.

## Bloque XII — revisión conceptual A y verificación regresiva (copia local, sin publicar)

- 206 respuestas conceptuales A examinadas individualmente en primera lectura técnica; 203 sin observación, tres mejoras propuestas, sin modificar el libro ni el solucionario.
- 16 pruebas algebraicas independientes añadidas en `pruebas_revision/test_consistencia_conceptual_206.py`.
- Regresión transversal acumulada: **588/588 pruebas superadas**. Las pruebas matemáticas seleccionadas no equivalen a una certificación automática de los 206 ejercicios A.
- Sintaxis de capítulos 2–15 y autopruebas específicas de capítulos 9, 10, 11, 13, 14 y 15 comprobadas en el entorno local.
- Fuente: `REVISIONES/INFORME_REVISION_CONCEPTUAL_A_206.md` y `REVISIONES/MATRIZ_REVISION_CONCEPTUAL_A_206.csv`.

```bash
python -m unittest discover -s pruebas_revision -q
python -m unittest pruebas_revision.test_consistencia_conceptual_206 -v
python -m compileall -q capitulo_02 capitulo_03 capitulo_04 capitulo_05 capitulo_06 capitulo_07 capitulo_08 capitulo_09 capitulo_10 capitulo_11 capitulo_12 capitulo_13 capitulo_14 capitulo_15
```

**Nota:** Las pruebas locales han pasado en Python 3.13. La nueva copia aún no se ha ejecutado en GitHub Actions con Python 3.11 y 3.13 ni se ha publicado con el tag `v1.0.0`.
