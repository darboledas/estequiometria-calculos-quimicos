# Historial de cambios

## 1.0.0 — candidata de publicación (7 de noviembre de 2026; NO publicada)

- Revisión acumulada de 28 aplicaciones con 588 pruebas transversales locales correctas; autopruebas específicas de capítulos superadas.
- Cotejo documentado de 350 ejercicios B/C (343 numéricos y siete cualitativos o gráficos); lectura de 206 A, con tres precisiones editoriales propuestas.
- Correcciones de validación, estabilidad numérica, entradas no físicas, Antoine y nuevos modos previstos en los capítulos 3, 5 y 12.
- Manuales actualizados y documentación de límites de la auditoría.
- Pendiente: comprobación remota de GitHub Actions en Python 3.11 y 3.13 y archivado en Zenodo. El DOI específico 1.0.0 **aún no existe**.


## No publicado — Bloque XII: revisión de 206 ejercicios A y 588 pruebas (7-11-2026)

- Lectura de consistencia científico-conceptual de los 206 ejercicios A: tres precisiones propuestas en solucionario, sin modificación del libro o solucionario definitivo.
- 16 comprobaciones algebraicas de relaciones conceptuales, 588/588 pruebas transversales superadas; compilación y autopruebas específicas locales superadas.
- Matriz por ejercicio y revisión de documentación, con duplicados del bloque XI eliminados en `COMPROBACIONES.md`.
- Copia no publicada: `v0.9.0` continúa como última versión con DOI específico.


## No publicado — Bloque VIII: 418 pruebas y 211 ejercicios (7-11-2026)

- 44 pruebas nuevas: 23 ejercicios inéditos en la matriz, 17 recontrastados y cuatro controles de datos no físicos.
- Corrección de Antoine de líquidos inmiscibles en capítulo 9, evitando falsas convergencias con residuo no finito.
- Errata aritmética del ejercicio 4.B.2 del solucionario, sin cambios en el resultado final redondeado.
- 418/418 pruebas y 211/556 ejercicios contrastados. GitHub y Zenodo sin modificar.


## No publicado — Bloque VII: 374 pruebas y 188 ejercicios (7-11-2026)

- 29 comprobaciones nuevas de libro y solución (26 ejercicios distintos, 3 controles de entrada).
- Validación completa de finitud y consistencia de las fuentes `DirectPsat`, `SimpleExpPsat` y `AntoinePsat` del capítulo 8.
- Contraste del ejercicio 5.B.6: el solucionario contiene un error en la cúbica impresa, pero los resultados numéricos son correctos; documentado sin modificar el PDF.
- 374/374 pruebas transversales superadas; 188/556 ejercicios contrastados al menos parcialmente.
- Documentación y manual actualizados; GitHub y Zenodo no modificados.

## No publicado — Bloque VI: 345 pruebas y 162 ejercicios (7-11-2026)

- 28 métodos transversales nuevos: 23 ejercicios adicionales (capítulos 2–11), otro ajuste en 8.C.2 y cuatro controles de entradas inválidas.
- Corrección en `disoluciones_no_ideales.py`: validación de longitud, dominio y finitud en observaciones experimentales y ajustes Margules/Van Laar; evita descartar observaciones con `zip` silenciosamente.
- 345/345 métodos transversales superados, 162 ejercicios distintos con cotejo parcial o completo; 394 identificadores pendientes.
- Nuevo informe y matriz por ejercicio en `REVISIONES/` y manual del capítulo 8 actualizado.
- No se modifica la publicación GitHub/Zenodo `v0.9.0`.

## No publicado — segundo bloque de cotejo científico (7-11-2026)

- Incorporados 41 métodos de prueba correspondientes a 38 ejercicios adicionales de los capítulos 2–15.
- Total acumulado: 232/232 pruebas transversales, 68 ejercicios distintos contrastados por lo menos parcialmente.
- Nuevo cálculo vdW con parámetros `a`, `b` explícitos (comando `estado --modelo vdw --vdw-a ... --vdw-b ...`), reproduce 5.B.2 exactamente con los parámetros del libro.
- Validación de entradas y prueba de cierre de presión para el nuevo modo.
- Segundo informe y matriz de trazabilidad en `REVISIONES/`, con límites de cobertura declarados.
- GitHub y Zenodo continúan en `v0.9.0`, sin cambios.


## No publicado — auditoría con libro y solucionario (7-11-2026)

- Añadidos 30 casos reproducibles de los capítulos 2–15, cada uno enlazado a ejercicio del libro definitivo y al solucionario; 28 aplicaciones representadas.
- Batería transversal acumulada: 191/191 métodos.
- Capítulo 3: método Hall explícito para 0–33 °Bx, separado de la interpolación de tabla de sacarosa.
- Capítulo 12: modo CLI optativo `--recuperacion` con cálculo de composición residual, conservación de entradas antiguas y aviso de cifras significativas.
- Matriz de cotejo, límites y errata tipográfica 9.B.10 documentados en `REVISIONES/`.
- No altera `VERSION` ni GitHub/Zenodo `v0.9.0`; pendiente de auditoría total para `v1.0.0`.

## No publicado — Redes de materia y cálculos inversos de combustión (7 de noviembre de 2026)

- Corrige la comparación de conexiones `from`/`to` del capítulo 11 con ID de unidades numéricos o texto.
- Rechaza fórmulas químicas con grupos vacíos o subíndices nulos en combustión.
- Escala por ecuación la resolución inversa para evitar falsas indeterminaciones con cantidades pequeñas.
- Añade 15 pruebas de regresión y el caso JSON `red_ids_numericos.json` (114 pruebas transversales en total).
- Informa de límites científicos pendientes en `REVISIONES/INFORME_BALANCES_E_INVERSIONES.md`.

**Estado:** cambios en copia local, no publicados en GitHub ni Zenodo.


## No publicado — Ampliación de contrastes termodinámicos (7 de noviembre de 2026)

- 14 métodos nuevos de pruebas de dominio, fugacidad, presión de vapor, VLE, flash, Rayleigh, Gibbs–Duhem y psicrometría.
- 99 métodos de revisión transversales acumulados, con bucles internos de casos múltiples.
- Correcciones de gases reales, límites puros de VLE, parsers de entradas y razón de humedad no finita.
- Detalles y cautelas en `REVISIONES/INFORME_CONTRASTES_TERMODINAMICOS.md`.

**Estado:** cambios locales de revisión; todavía no publicados ni considerados versión estable.

## No publicado — Revisión transversal (7 de noviembre de 2026)

- Comprobación de los 28 puntos de entrada con casos de referencia independientes.
- Ampliación de las pruebas en `pruebas_revision` a 85 casos, con invariantes y rechazo de datos no físicos.
- Correcciones de validación de finitud y dominios en los capítulos 4, 8 y 15, además de las correcciones anteriores de los capítulos 2 y 3.
- Actualización de los 28 manuales y de la información bibliográfica con los DOI verificados.
- Documento de trazabilidad `REVISIONES/INFORME_AUDITORIA_INTEGRAL.md` y guía de integración única.

**Estado:** cambios locales pendientes de incorporación a GitHub y posterior publicación de una versión nueva, tras comprobar CI. La revisión no certifica exhaustivamente todos los modelos.

## 0.9.0 — Primera versión pública (6 de noviembre de 2026)

- Inventario unificado: 28 aplicaciones y 4 archivos Python auxiliares/de pruebas.
- Manuales de usuario independientes por aplicación.
- Integración de la edición Word maquetada del manual completo (Arial y Consolas).
- Introducción de licencia MIT, CITATION.cff y metadatos Zenodo.
- Corrección de los nombres de ejecución heredados en el capítulo 13.
- Corrección de la individualidad de precisión de las extensiones del capítulo 13.
- Incorporación de dos pruebas específicas de regresión al capítulo 13.
- Automatización de la batería principal de comprobaciones en GitHub Actions.

**Estado:** release pública archivada en Zenodo, DOI de versión 10.5281/zenodo.24020473.

### Revisión local no publicada — 7 de noviembre de 2026, ampliación de escala
- Corregidos umbrales absolutos en redes de materia que ocultaban caudales negativos y composiciones de corrientes positivas pequeñas.
- Corregidos umbrales absolutos en cantidades, productos, balances elementales y suministros de comburente de combustión.
- Incorporadas 13 nuevas pruebas de regresión (127 transversales en total) y casos analíticos de reciclado y S/N.
- Aún **no** se crea ni recomienda publicar `v1.0.0` sin completar las comprobaciones pendientes.


### Cambios acumulados pendientes de publicación (revisión local 2026-11-07, bloque de combustión incompleta)
- Corrige pérdidas de especies y déficit de O₂ en cálculos de combustión incompleta de pequeña escala.
- Evita presentar como cero las magnitudes positivas inferiores a 10⁻⁹ al formatearlas.
- Refuerza inversos de combustible puro y binario con valores pequeños y rechazo de razón de aire indefinida.
- Añade 16 pruebas transversales, incluidas 150 reconstrucciones inversas sintéticas de mezclas de cuatro componentes.
- Actualiza el manual del capítulo 14 y añade un informe independiente de contrastes.

**Nota:** estos cambios pertenecen a la copia de trabajo; no se ha creado una nueva release.


### No publicado — Sistemas casi singulares y correlaciones empíricas (7 de noviembre de 2026)
- Equilibrado de filas y columnas, pivoteo completo, control de residuos y rechazo conservador de cálculos inversos casi singulares en el capítulo 14.
- Gestión informativa de desbordamientos exponenciales en Antoine, Clausius-Clapeyron y Lee-Kesler (capítulo 6).
- 14 pruebas nuevas (157 métodos transversales acumulados), incluidos 200 sistemas inversos de referencia y 231 parejas Antoine calculadas dentro de su dominio.
- Manuales de capítulos 6 y 14 e informe científico actualizados. Sin publicación remota.


### Cotejo con tabla 6.1 y ejercicios del libro (7-11-2026, no publicado)
- Se ha corregido el registro Antoine del amoníaco para coincidir con el libro (A=6,86886; B=1113,928; C=−10,409; 240–372 K).
- 4 nuevas pruebas de regresión: los 11 juegos de coeficientes de la tabla 6.1 y los ejercicios 6.B.11, 6.B.14 y 6.B.15.
- La batería transversal acumulada asciende a **161 métodos** (143 + 18 nuevos en este bloque).
- El cotejo integral de todos los ejercicios del libro continúa pendiente.


### Cotejo integrador, bloque 3 — no publicado (7 de noviembre de 2026)

- Corrección de la validación de composición, temperatura, dimensionalidad y factores no finitos en `bubble_pressure_gamma_phi()` (capítulo 8).
- 30 nuevas pruebas (262 acumuladas): 22 ejercicios tipo C nuevos, total 90 ejercicios distintos cotejados.
- Revisión de dos operaciones en cascada y balances de fases, con aclaración de redondeos y de los límites del contraste.


### Cuarto bloque — cotejo de aplicaciones y validación física (7-11-2026, no publicado)
- 26 ejercicios tipo C nuevos con resultados cotejados y trazabilidad por número/página (116 ejercicios distintos acumulados).
- 28 nuevos métodos de prueba: 26 ejercicios + 2 validaciones; total transversal **290/290**.
- Corrección `vapor_agua.quality_from_property()`: `NaN` e infinito en propiedades de entrada o nodos de saturación generan `ValueError`, sin interpretar un título indefinido como estado bifásico.
- Se documentan operaciones encadenadas resueltas por balances algebraicos, las diferencias de precisión en galones US, y los límites científicos del contraste.
- Archivos: `REVISIONES/INFORME_COTEJO_APLICADOS_116.md`, `REVISIONES/MATRIZ_COTEJO_BLOQUE_04.json`.
- GitHub y Zenodo siguen sin modificar.

### Bloque V — Revisión local no publicada (7-11-2026)
- Capítulo 15: protección de Antoine gas–vapor frente a coeficientes no finitos, desbordamientos y presiones inválidas.
- Contraste adicional de 23 ejercicios C de capítulos 12–15, más cuatro pruebas de dominio y de unidades; 317 pruebas transversales y 139 ejercicios distintos acumulados.
- Diferencia de convención de entalpía 15.C.4 documentada, sin cambiar indebidamente el modelo.
- La publicación pública 0.9.0 permanece intacta.


### Auditoría de trabajo — Bloque IX (sin publicar, 2026-11-07)
- Capítulo 7: rechazo de presión, temperatura, coeficientes e intervalos Antoine no finitos en la construcción directa y la inversión.
- 39 pruebas nuevas; 457/457 acumuladas. 21 ejercicios nuevos y 12 recontrastes.
- Ningún cambio en la etiqueta pública ni en el DOI.

### Bloque X — auditoría local no publicada (7-11-2026)
- Corregida la validación de datos finitos y de longitudes de series en los índices EMA/RECM y utilidades analíticas de azeótropo del capítulo 8.
- 21 ejercicios numéricos inéditos del libro cotejados mediante funciones directas o combinadas con balances auxiliares, más 4 guardias; **482/482** pruebas acumuladas.
- Cobertura: 253/556 ejercicios con cotejo específico; pendientes 97 B/C y 206 A conceptuales.
- Sin publicar ni alterar versión pública/DOI.


### Auditoría pre-v1.0.0 — bloque XI (2026-11-07)

- Añadidas 90 pruebas nuevas de ejercicios, acumulado 572/572.
- Completado el cotejo numérico de 343/350 ejercicios B/C y el cualitativo/gráfico de otros 7.
- Comprobada la existencia en libro y solucionario de los 206 ejercicios A; su revisión científica individual sigue abierta.
- Se han añadido matrices de trazabilidad, resultados por capítulo y anexo del manual.
- Sin cambios en el núcleo de las aplicaciones ni publicación de una nueva versión.


### Auditoría pre-v1.0.0 — bloque XI (2026-11-07)

- Añadidas 90 pruebas nuevas de ejercicios, acumulado 572/572.
- Completado el cotejo numérico de 343/350 ejercicios B/C y el cualitativo/gráfico de otros 7.
- Comprobada la existencia en libro y solucionario de los 206 ejercicios A; su revisión científica individual sigue abierta.
- Se han añadido matrices de trazabilidad, resultados por capítulo y anexo del manual.
- Sin cambios en el núcleo de las aplicaciones ni publicación de una nueva versión.


### Auditoría pre-v1.0.0 — bloque XI (2026-11-07)

- Añadidas 90 pruebas nuevas de ejercicios, acumulado 572/572.
- Completado el cotejo numérico de 343/350 ejercicios B/C y el cualitativo/gráfico de otros 7.
- Comprobada la existencia en libro y solucionario de los 206 ejercicios A; su revisión científica individual sigue abierta.
- Se han añadido matrices de trazabilidad, resultados por capítulo y anexo del manual.
- Sin cambios en el núcleo de las aplicaciones ni publicación de una nueva versión.
