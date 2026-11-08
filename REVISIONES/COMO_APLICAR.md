# Incorporar el bloque 01 con GitHub Desktop

Este ZIP es **incremental**. Contiene únicamente archivos nuevos o corregidos, no las 28 aplicaciones completas.

1. Abra GitHub Desktop y seleccione `darboledas/estequiometria-calculos-quimicos`.
2. Pulse **Fetch origin**. Si aparece **Pull origin**, púlselo. Es importante recuperar antes los commits hechos en la web de GitHub, especialmente `README.md` y `.github/workflows/comprobaciones.yml`.
3. Abra **Repository → Show in Explorer**. Esa es la raíz del repositorio local (en su equipo, `E:\GitHub\estequiometria-calculos-quimicos`).
4. Descomprima este ZIP fuera de esa carpeta y copie **su contenido**, conservando las rutas originales, sobre la carpeta del repositorio. Acepte sustituir los archivos indicados. **No copie la carpeta contenedora ni el ZIP.**
5. Regrese a GitHub Desktop. Verifique que solo figuran los archivos esperados: los dos `.py` corregidos, los 28 manuales Markdown, el flujo de Actions y los nuevos archivos `pruebas_revision` y `REVISIONES`.
6. Para probar en Windows desde la raíz del repositorio, ejecute `python -m unittest discover -s pruebas_revision -v`. Se esperan 46 pruebas correctas.
7. Escriba como mensaje de commit: `Revisión científica inicial: capítulos 2 y 3, 46 pruebas y DOI en manuales`.
8. Pulse **Commit to main** y después **Push origin**. Revise que GitHub Actions termine en verde.

**No cree todavía una release nueva ni modifique los registros de Zenodo.** La versión archivada `v0.9.0` continúa siendo la referencia estable mientras se revisa el resto del proyecto.
