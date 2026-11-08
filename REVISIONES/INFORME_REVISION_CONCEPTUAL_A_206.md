# Revisión conceptual A — 206 ejercicios (7 de noviembre de 2026)

**Alcance:** revisión individual de coherencia científica de los enunciados y respuestas A del libro definitivo de 934 páginas y del solucionario desarrollado de 220 páginas, capítulos 2–15. No se distribuyen los contenidos de dichas obras en el repositorio. La matriz adjunta contiene solo identificadores, páginas, estados y observaciones.

**Resultado:** 206/206 respuestas examinadas en primera lectura técnica; 203 sin incidencia detectada y 3 con propuesta de precisión (una afecta la definición del sistema y su frontera). Ninguna corrección se ha aplicado a los PDF editoriales. «Sin incidencia detectada» significa que no se ha observado contradicción en esta lectura, no certificación universal ni revisión externa independiente.

## Recuento por capítulos

| Cap. | Tema | Revisadas | Propuestas |
|---:|---|---:|---:|
| 2 | Unidades, dimensiones e incertidumbre | 15 | 0 |
| 3 | Estequiometría y composición | 19 | 0 |
| 4 | Gases ideales y mezclas | 10 | 0 |
| 5 | Ecuaciones de estado de gases reales | 20 | 0 |
| 6 | Vapor, saturación y correlaciones | 16 | 1 |
| 7 | Equilibrio ideal y operaciones | 12 | 0 |
| 8 | Actividad y equilibrio no ideal | 16 | 0 |
| 9 | Equilibrio líquido-líquido e inmiscibles | 10 | 0 |
| 10 | Electrolitos y coligativas | 16 | 0 |
| 11 | Balances de materia | 14 | 1 |
| 12 | Operaciones de separación | 11 | 1 |
| 13 | Balances con reacción | 16 | 0 |
| 14 | Combustión y gases | 12 | 0 |
| 15 | Psicrometría | 19 | 0 |
| **Total** | | **206** | **3** |

## Observaciones comprobadas

### 6.A.16 — precisión terminológica (solucionario)

«Propiedad específica extensiva» resulta contradictorio: volumen, entalpía, energía interna y entropía específicos son intensivos, derivados de extensivas aditivas.

**Propuesta sin aplicar:** «Para una propiedad específica asociada a una magnitud extensiva aditiva, por ejemplo v, h, u o s, se cumple q=(1−x)q_f+x q_g en la región bifásica». No cambiar la ecuación.

### 11.A.1 — frontera del sistema (solucionario)

La respuesta elige la disolución líquida como sistema pero ubica la frontera en la superficie interna del matraz. Si existe cámara de vapor, el subsistema líquido puede intercambiar materia por evaporación aun estando cerrado el matraz completo.

**Propuesta sin aplicar:** «Si se toma como sistema todo el contenido del matraz (líquido y fase gaseosa), la frontera coincide con la cara interna del recipiente y su cierre: no la atraviesa materia. Si el sistema fuera solo el líquido, la superficie libre sería parte de la frontera y podrían cruzarla moléculas hacia la cámara de vapor». El resto de los apartados se conserva.

### 12.A.6 — condición necesaria para resultados absolutos (solucionario)

Recuperación y composición de torta no bastan por sí solas para determinar caudales absolutos de filtrado: se necesita conocer el sólido alimentado y el balance de la corriente de entrada.

**Propuesta sin aplicar:** Añadir «Cuando se conocen el caudal y la composición de la alimentación, los balances permiten obtener los sólidos y el líquido presentes en el filtrado». No cambiar las definiciones R y w.

## Evidencia matemática complementaria

Se han incorporado 16 pruebas independientes en `pruebas_revision/test_consistencia_conceptual_206.py` con contrastes de exceso de aire, velocidad cuadrática media, van der Waals, Clausius–Clapeyron, título de vapor, Raoult, Rachford–Rice, Margules y Gibbs–Duhem, ebullición inmiscible, fuerza iónica, constantes coligativas, humedad, dependencia estequiométrica y psicrometría. **Estos ensayos no pretenden comprobar automáticamente 206 respuestas**: la evidencia de todos los ejercicios A es una revisión de coherencia semántica; los ensayos son apoyos específicos.

## Notas sobre el texto del PDF

La extracción automática incorpora a 14 enunciados A finales de capítulo el encabezado de los ejercicios B; no es una errata confirmada de impresión. Los identificadores son: 2.A.15, 3.A.19, 4.A.10, 5.A.20, 6.A.16, 7.A.12, 8.A.16, 9.A.10, 10.A.16, 11.A.14, 12.A.11, 13.A.16, 14.A.12, 15.A.19.

Las fórmulas con superíndices, subíndices o fracciones pueden perder su disposición en la extracción de texto. No se ha atribuido ningún error algebraico basándose únicamente en ese texto ambiguo. Se mantiene la recomendación de inspección visual de las páginas afectadas antes de cualquier fe de erratas.

## Alcance editorial y de software

El total de 556 identificadores se compone de 206 conceptuales A y 350 B/C. De los B/C, 343 tienen algún contraste numérico y siete una revisión cualitativa/gráfica según las matrices previas; esos contrastes pueden ser funciones de programas o balances auxiliares. **No equivale a que las 28 aplicaciones resuelvan automáticamente los 556 ejercicios.** Las respuestas A son esencialmente explicativas y no deben contabilizarse como 206 nuevas pruebas de código.

La revisión del material editorial no ha alterado el contenido científico del libro ni las fuentes cerradas para imprenta. Las observaciones permanecen pendientes de decisión editorial.
