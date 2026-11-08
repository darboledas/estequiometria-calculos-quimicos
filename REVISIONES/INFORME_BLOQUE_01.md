# Revisión científica y documental. Bloque 01

**Proyecto:** *Estequiometría y cálculos químicos — Software complementario*  
**Autor:** David Arboledas Brihuega  
**Base revisada:** versión pública `v0.9.0`, DOI `10.5281/zenodo.24020473`  
**Ámbito:** seis aplicaciones de los capítulos 2 y 3  
**Estado de las modificaciones:** propuesta de corrección para una futura actualización; no se modifica el depósito de Zenodo ya publicado.

## 1. Alcance y procedimiento

Se han inspeccionado las seis aplicaciones Python de los capítulos 2 y 3. Se han ejecutado sus autocomprobaciones, cuando existen, y se ha creado una batería independiente de 46 pruebas de regresión basada en operaciones conocidas y casos de entrada inválida. También se han repetido las comprobaciones disponibles de los capítulos 9, 10, 11, 13, 14 y 15 para detectar regresiones relacionadas con los cambios. Se ha inspeccionado la correspondencia operativa de sus manuales Markdown y se ha detectado una referencia bibliográfica obsoleta compartida por los 28 manuales.

El resultado no constituye una validación universal de todos los cálculos posibles. No se ha auditado aún la exactitud de todas las constantes tabuladas ni se han comparado sistemáticamente las respuestas con cada problema del libro impreso.

## 2. Resumen de resultados

| Archivo | Cálculos comprobados | Resultado de la revisión |
| --- | --- | --- |
| `capitulo_02/unidades_y_dimensiones.py` | Conversión de unidades, temperatura e intervalos, cifras significativas, propagación de incertidumbres y análisis dimensional | Cálculos de referencia satisfactorios; corregidos dos casos de validación insuficiente |
| `capitulo_03/ajuste_ecuaciones.py` | Ajustes de combustión, neutralización, redox y verificación de balances | Casos analizados correctos; pendientes otros tipos de reacción |
| `capitulo_03/conversion_rendimiento_selectividad.py` | Conversión, porcentajes, reglas de precisión y rendimiento por etapas | Casos analizados correctos |
| `capitulo_03/densidades_y_escalas.py` | Conversión API, interpolación Brix y conversiones inversas | Casos analizados correctos; pendiente auditar toda la tabla de densidad de sacarosa y sus condiciones de referencia |
| `capitulo_03/masa_molar.py` | Agua, sulfato de aluminio, hidratos, subíndices Unicode y símbolos desconocidos | Resultados analizados correctos; corregida aceptación de grupos vacíos internos |
| `capitulo_03/reactivo_limitante.py` | Identificación de limitante, exceso estequiométrico, sobrantes y conversión parcial | Casos analizados correctos; pendientes mezclas con purezas y casos próximos a colimitancia |

## 3. Hallazgos y correcciones

### H01. Matrices de correlación inadmisibles — importancia alta

La función `matriz_covarianzas` comprobaba intervalos, simetría y diagonal igual a 1, pero no que la matriz de correlación fuese semidefinida positiva. Una matriz con correlaciones `0,9`, `0,9` y `−0,9` entre tres variables satisface esas tres condiciones superficiales, pero no puede representar simultáneamente tres variables reales. Para sensibilidades `(1, 1, 1)` y desviaciones estándar unitarias, el programa anterior devolvía una varianza positiva (4,8), sin detectar la inconsistencia física de la matriz.

**Corrección:** se ha añadido la validación de semidefinición positiva mediante eliminación simétrica (complementos de Schur), sin introducir NumPy como dependencia del capítulo. La validación admite matrices semidefinidas, incluidas correlaciones perfectas con matriz singular. Se han agregado pruebas con correlación perfecta positiva, negativa y una matriz imposible.

**Fundamento técnico:** las matrices de correlación y covarianza utilizadas en propagación de incertidumbres han de ser semidefinidas positivas. Referencia: Kessel y Kacker, *Correlation in Uncertainty of Measurement* (NIST, 2009), https://www.nist.gov/publications/correlation-uncertainty-measurement-discussion-state-art-techniques.

### H02. Exponentes científicos mal formados — importancia baja

La función interna `cifras_significativas_texto` contaba las cifras de la mantisa sin comprobar el exponente. Expresiones incompletas (`1e`) o mal formadas (`1eXYZ`) podían recibir un recuento numérico aunque no representasen magnitudes válidas. La conversión principal ya rechazaba esas entradas, pero la función reutilizable no lo hacía.

**Corrección:** validación previa de la expresión completa mediante `decimal_desde_texto`. Se han incluido casos válidos e inválidos en las pruebas.

### H03. Grupos químicos vacíos internos — importancia media

El analizador de `masa_molar.py` rechazaba `()` como fórmula única, pero aceptaba, por ejemplo, `Fe()2`, ignorando el grupo vacío y devolviendo la masa molar del hierro. Esa entrada debería rechazarse por sintaxis incorrecta.

**Corrección:** cada subgrupo entre paréntesis, corchetes o llaves debe contener al menos una especie. Se prueban `Fe()2`, `Ca[]2` y `Al{}2`.

### H04. Referencias bibliográficas desactualizadas — importancia editorial

Los 28 manuales Markdown afirmaban que el DOI del software se incorporaría más adelante. Ese dato ya no era correcto después del archivado en Zenodo.

**Corrección:** se han actualizado las secciones bibliográficas de los 28 manuales con el DOI general del software (`10.5281/zenodo.24020474`), el DOI de la versión 0.9.0 (`10.5281/zenodo.24020473`) y el DOI del libro (`10.5281/zenodo.24013068`). **El manual general en Word permanece sin revisar**, a la espera de su nueva edición conjunta.

### H05. Nombre de archivo antiguo en la cabecera del capítulo 2 — importancia editorial

La cabecera de `unidades_y_dimensiones.py` todavía ofrecía ejemplos con `herramientas_capitulo_2.py`, nombre que no corresponde al archivo distribuido.

**Corrección:** ejemplos de cabecera actualizados a `unidades_y_dimensiones.py`.

## 4. Verificaciones ejecutadas

- **46 pruebas nuevas:** todas superadas con Python 3.13.5.
- **Autopruebas de las cinco herramientas de los capítulos 2 y 3 que las incorporan:** correctas.
- **Capítulo 9:** suite original ejecutada sin fallos (24 pruebas).
- **Capítulo 10:** dos autopruebas (39/39 y 38/38), correctas.
- **Capítulo 11:** 58 pruebas, correctas.
- **Capítulo 13:** 12 pruebas, correctas.
- **Capítulo 14:** 23 comprobaciones, correctas.
- **Capítulo 15:** 12 grupos de validación, correctos.
- **Compilación sintáctica:** sin errores en los capítulos 2 a 15.

**Importante:** estas comprobaciones se han ejecutado sobre la copia de trabajo modificada. La batería adicional todavía no se ha publicado ni ejecutado en GitHub Actions; el archivo de flujo de trabajo del paquete está preparado para integrarla. Las comprobaciones científicas existentes de otros capítulos no constituyen su auditoría científica integral.

## 5. Próximas revisiones pendientes

1. **Capítulo 2:** contrastar reglas de presentación de cifras significativas y propagación de incertidumbres con los ejercicios del libro, y revisar entradas límite de gran magnitud.
2. **Capítulo 3, ajuste:** ampliar casos redox, ambigüedad estequiométrica, conservación de carga y reacciones con iones espectadores.
3. **Capítulo 3, rendimientos:** validar exhaustivamente rutas paralelas, selectividad y casos experimentales con productos iniciales.
4. **Capítulo 3, densidades:** comprobar tabla Brix, origen, interpolación y referencias 20/20 y 60/60, sin extrapolación.
5. **Capítulo 3, masa molar:** cotejar la tabla de pesos atómicos y sus incertidumbres con la fuente CIAAW incorporada en el código.
6. **Capítulo 3, reactivo limitante:** probar purezas másicas, exceso y colimitancia con precisiones experimentales distintas.
7. **Documentación general:** actualizar `CITATION.cff`, `.zenodo.json` y el manual Word al cerrar la revisión completa y preparar una futura versión. No asignar el DOI específico de 0.9.0 a código que ya haya sido modificado.

## 6. Publicación y trazabilidad

Estas correcciones se entregan en un paquete incremental con las rutas relativas originales. Es necesario recuperar los cambios remotos (`Fetch origin` y `Pull origin`) en GitHub Desktop **antes** de copiarlo, porque el repositorio público ya contiene modificaciones en el README y en GitHub Actions que no estaban en el ZIP inicial.

La versión `v0.9.0` ya archivada debe permanecer intacta. Tras incorporar la revisión a la rama `main` se ejecutarán las pruebas en GitHub Actions. Se decidirá después cuándo preparar una nueva versión archivada (`v0.9.1` o superior) y actualizar sus metadatos.
