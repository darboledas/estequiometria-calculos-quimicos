# Lista de verificación previa a publicar v1.0.0

**Estado:** candidata local de auditoría. No publicada. Última release pública: `v0.9.0`.

## Revisión efectuada en la copia local

- [x] Mantener los 28 programas y manuales.
- [x] Contrastar 343 ejercicios B/C numéricamente (algunos mediante balances auxiliares; ver matrices anteriores).
- [x] Revisar cualitativamente los siete B/C restantes.
- [x] Lectura individual de las 206 respuestas A; 3 observaciones documentadas sin edición de las fuentes.
- [x] Ejecutar las 588 pruebas transversales en el entorno local.
- [x] Compilar capítulos 2–15 y ejecutar las autopruebas locales existentes.
- [x] Documentar hipótesis, límites de los modelos y diferencia entre cotejo manual y función automatizada.
- [x] Excluir del repositorio los PDF del libro y solucionario.

## Antes de una release pública

- [ ] Decidir editorialmente las tres observaciones de las respuestas A; pueden quedar para una futura fe de erratas, pero deben registrarse.
- [ ] Revisar el manual y README finales después de cualquier nueva modificación de código.
- [ ] En el commit definitivo de publicación, ajustar de forma coordinada versión y fecha en `CITATION.cff`, `.zenodo.json`, `README.md` y `CHANGELOG.md` a 1.0.0. No cambiar antes los metadatos de la v0.9.0 publicada.
- [ ] Crear commit, hacer push y comprobar que la matriz de CI pasa realmente con Python 3.11 y 3.13 en GitHub Actions.
- [ ] Crear la release `v1.0.0` y comprobar el depósito de esa versión en Zenodo y su DOI específico; no inventarlo ni darlo por creado antes de confirmación.
- [ ] Inspeccionar el contenido público para comprobar que no incluye soluciones extensas del libro o datos experimentales con derechos de terceros.

## Límites de interpretación

La aprobación de pruebas automatizadas demuestra conformidad de los casos ensayados, no corrección universal de ecuaciones, bases de datos o extrapolaciones empíricas. La revisión conceptual de 206 ejercicios no implica que el código resuelva 206 problemas adicionales. Una auditoría externa es opcional, pero la validación experimental de correlaciones requiere fuentes independientes y una campaña específica.
