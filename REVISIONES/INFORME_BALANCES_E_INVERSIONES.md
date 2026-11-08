# Revisión adicional — Redes de materia y cálculo inverso de combustión

**Fecha:** 7 de noviembre de 2026  
**Estado:** copia local, todavía no incorporada al repositorio público; no constituye una nueva versión Zenodo.

## Alcance

Se ha examinado el tratamiento de identificadores numéricos y cadenas en las redes del capítulo 11 y la interpretación de fórmulas y solución de problemas inversos del capítulo 14. Se mantienen acumuladas las correcciones termodinámicas y de validación de las fases anteriores.

## Incidencias reproducibles y correcciones

1. **Capítulo 11 — Conexiones con identificadores numéricos.** El solver convertía los ID de unidades a texto para construir su lista interna, pero comparaba `from` y `to` sin esa conversión en algunos balances. Así, una red válida con unidades `1` y `2` podía perder conexiones y resultar falsamente indeterminada. Ahora se normalizan los extremos de las conexiones antes de evaluar cada balance. Se comprueba también el rechazo de identificadores duplicados tras la normalización.
2. **Capítulo 14 — Fórmulas químicas no válidas.** Se rechazaron explícitamente grupos vacíos, factores no positivos y multiplicadores no finitos. Ejemplos rechazados: `Fe()2`, `CH0`, `Mg(OH)0`; continúan admitiéndose fórmulas válidas como `Ca(OH)2` y `C6H12O6`.
3. **Capítulo 14 — Escalado de sistemas inversos.** La eliminación de Gauss-Jordan usaba umbral absoluto (`1e-10`) incluso sobre coeficientes de cantidades muy pequeñas. En el caso `1e-12·x = 2e-12`, con solución única `x=2`, el programa clasificaba el problema como indeterminado. Ahora se escala cada ecuación por el mayor coeficiente absoluto antes de la eliminación y se comprueba la finitud de coeficientes y términos independientes. Este cambio no constituye una garantía para sistemas casi singulares.

## Referencias numéricas independientes

- **Red material no reactiva de dos unidades:** alimentación de 100,0 kg/h, con 40 % A y 60 % B. Los tres tramos conservan 40 kg/h de A y 60 kg/h de B, sin pérdidas ni generación.
- **Red material reactiva molar:** A → B, con alimentación de 10 mol de A y extensión 4 mol, produce 6 mol de A y 4 mol de B.
- **Mezcla binaria de combustibles:** 2 mol CH₄ y 3 mol C₂H₆ forman 8 mol CO₂ y 13 mol H₂O, y requieren 14,5 mol O₂. La aplicación invierte los observables de CO₂ y H₂O y recupera la composición. Con una sola ecuación se reconoce la indeterminación.
- **Análisis seco con aire del modelo 21/79:** el problema de combustión completa de CH₄ reproduce una relación H/C = 4 y factor de aire λ = 1 bajo las hipótesis del programa.
- **Control de escala:** soluciones matemáticamente equivalentes al multiplicar las ecuaciones por `1e-12`, `1e-6`, `1e6` y `1e12`.

## Estado de las pruebas

- **114 métodos transversales:** correctos (99 previos + 15 adicionales).
- **Capítulo 9:** 24 pruebas correctas.
- **Capítulo 10:** 39 verificaciones del programa de electrolitos y 38 del programa de coligativas, correctas.
- **Capítulo 11:** 58 pruebas correctas.
- **Capítulo 13:** 12 pruebas correctas.
- **Capítulo 14:** 23 verificaciones internas correctas.
- **Capítulo 15:** 12 grupos de validación correctos.
- **Sintaxis Python:** comprobada en los capítulos 2 a 15 y las nuevas pruebas.

Las pruebas y sus resultados se han ejecutado con Python de este entorno. La ejecución automática con Python 3.11 y 3.13 en GitHub Actions solo podrá confirmarse cuando se integre la revisión en GitHub; todavía no se ha hecho.

## Archivos reproducibles

- `pruebas_revision/test_balances_combustion_ampliada.py`: 15 nuevos métodos de prueba, sin bibliotecas adicionales.
- `capitulo_11/ejemplos/red_ids_numericos.json`: red de referencia reproducible con el comando `python capitulo_11/balances_materia.py --red capitulo_11/ejemplos/red_ids_numericos.json`.
- Manuales actualizados: `manuales/capitulo_11/balances_materia.md` y `manuales/capitulo_14/combustion.md`.

## Límites científicos pendientes

Las pruebas presentes son casos representativos de validación algebraica, estequiométrica y de ejecución. Quedan pendientes los contrastes amplios de mecanismos de combustión incompleta, mezclas con especies nitrogenadas y azufradas, análisis seco con más especies, redes con reciclados, acumulación y purga, así como el cotejo sistemático con todos los problemas impresos del libro. La versión `v0.9.0` archivada en Zenodo permanece sin cambios.
