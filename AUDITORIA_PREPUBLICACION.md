# Auditoría de prepublicación — 6 de noviembre de 2026

Esta verificación no constituye una certificación de exactitud científica. Se conservaron los programas originales salvo correcciones puntuales documentadas en `CHANGELOG.md`.

## Inventario

- 28 aplicaciones Python y 4 archivos Python auxiliares/de pruebas (32 archivos `.py`).
- 28 manuales individuales en Markdown y manual compilado en Word.
- Se inspeccionaron las ayudas principales y los menús de los programas.

## Comprobaciones y correcciones

- Capítulo 13: se corrigió la aplicación de las cifras significativas por extensión según las relaciones que contribuyen a cada variable (con aproximación de sensibilidad lineal); se incorporaron dos pruebas de regresión. Consulte `COMPROBACIONES.md` y ejecute la batería incluida.
- Capítulo 9: 24 pruebas correctas en la revisión original.
- Capítulo 10: 38 y 39 autopruebas correctas en la revisión original.
- Capítulo 11: 58 pruebas correctas en la revisión original.
- Capítulo 14: 23 pruebas correctas en la revisión original.
- Capítulo 15: 12 grupos de validación correctos en la revisión original.
- Capítulo 3: autopruebas previas correctas en ajuste, conversión/rendimiento, densidades y reactivo limitante.

## Cuestiones pendientes

- El inventario anterior omitía `capitulo_03/masa_molar.py` (incorporado).
- Los nombres antiguos del capítulo 13 en las cabeceras fueron corregidos; conviene revisar otras referencias antiguas al contrastar libro y código.
- Psicrometría: el libro planifica 12 modos y PNG 300 ppp, pero la ayuda del programa enumera 15 modos y PNG 400 ppp. Revisar el texto de la obra o normalizar la aplicación.
- Disoluciones no ideales: NRTL/UNIQUAC se mencionan en el libro, pero no están implementados en el script distribuido.
- La precisión propagada en sistemas lineales acoplados del capítulo 13 usa una heurística conservadora basada en cifras significativas; no reemplaza el cálculo de incertidumbres de sistemas mal condicionados.
- Antes de etiquetar `v1.0.0`, revisar científicamente los casos pendientes y completar los ejemplos tutoriales de los manuales si se desean.
- El DOI de Zenodo del software no se ha asignado. La licencia MIT sí está incorporada.
