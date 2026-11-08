# Integración en GitHub de la revisión integral

Esta carpeta representa una **copia de trabajo** creada a partir del paquete fuente de `v0.9.0` y las revisiones locales. No es una clonación en tiempo real del repositorio remoto. Antes de subirla, hay que comparar el estado actual de GitHub con esta copia, especialmente `.github/workflows/comprobaciones.yml`, `README.md`, `CITATION.cff` y `.zenodo.json`.

1. En GitHub Desktop, abrir `darboledas/estequiometria-calculos-quimicos` y pulsar **Fetch origin** y **Pull origin** si corresponde. Es recomendable guardar una copia de seguridad local del repositorio.
2. Descomprimir el ZIP de revisión y copiar **su contenido** a `E:\GitHub\estequiometria-calculos-quimicos`, preservando carpetas y archivos ocultos (incluido `.github`). **No copiar el ZIP dentro del propio repositorio.**
3. Revisar las modificaciones en GitHub Desktop. Evitar que la actualización sobrescriba ediciones posteriores realizadas directamente en GitHub y no presentes en este paquete. Se ha incluido una versión del `README` con los DOI confirmados.
4. Ejecutar en la raíz `python -m pip install -r requirements-graficos.txt` y `python -m unittest discover -s pruebas_revision -v`.
5. Hacer un único commit: `Auditoría transversal de las 28 aplicaciones y revisión de manuales`, seguido de **Push origin**.
6. En la pestaña **Actions**, comprobar la matriz de Python 3.11 y 3.13. Ante un error, revisar el log y resolverlo antes de publicar una nueva release.
7. La publicación de una nueva versión y su DOI en Zenodo debe hacerse después de comprobar los metadatos y decidir expresamente el número de versión. La `v0.9.0` permanece archivada.

**No afirmar que el software ha sido validado científicamente en todas sus condiciones de uso:** consulte el alcance de `INFORME_AUDITORIA_INTEGRAL.md`.
