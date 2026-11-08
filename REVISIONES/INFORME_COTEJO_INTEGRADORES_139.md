# Bloque V — Cotejo integrador y control de Antoine gas–vapor (7 de noviembre de 2026)

**Copia de trabajo local pendiente de publicar**. Libro: edición definitiva de 934 páginas; solucionario desarrollado: 220 páginas. Ambas obras son fuentes de verificación y **no se redistribuyen** en el paquete del software.

## Resultado comprobado

- 23 ejercicios C nuevos de los capítulos 12–15; total acumulado: **139 ejercicios distintos** (116+23).
- 27 métodos de prueba nuevos: 23 ejercicios + 4 comprobaciones de dominio/unidades de Antoine.
- **317/317** pruebas transversales superadas en la copia de trabajo; compila el código de los 14 capítulos y pasan las autopruebas de capítulos 9, 10, 11, 13, 14 y 15.
- Ejercicios destacables: 12.C.5 separación ternaria encadenada (A, B, C); 12.C.8 evaporación, cristalización y filtración en dos horas; 13.C.9 reacciones sucesivas NO/NO₂/N₂O₄; 14.C.4 combustible CH₄/C₂H₆ inverso a partir de Orsat; 14.C.9 inversión CH₄/C₃H₈ a partir de 11,0 % CO₂; 15.C.10 condensación de etanol en N₂.

## Incidencia corregida — capítulo 15

En `psicrometria.antoine_psat_kpa()` la entrada de coeficientes de Antoine no finitos podía producir presión NaN. También un exponente excesivo podía provocar `OverflowError` no controlado. Ahora la función rechaza temperatura, constantes y resultados no finitos, singularidades y desbordamientos mediante `PsychrometricError`, sin modificar los resultados de entrada válida. La prueba con la interfaz de gas–vapor general rechaza el coeficiente NaN antes de calcular el estado.

**Convenciones de temperatura:** en la tabla 6.1 del libro se usa `log10(P*/kPa) = A − B/(T_K + C_K)` (K). La opción de gas–vapor del capítulo 15 utiliza `log10(P*/kPa) = A − B/(T_°C + C_°C)`; para trasladar coeficientes compatibles, `C_°C = C_K + 273,15`, con A, B inalterados. Usar C_K directamente en la segunda opción introduce un error.

## Diferencias científicas que no son errores

15.C.4 utiliza en el libro `c_p,a=1,005`, `c_p,v=1,88`, `h_fg=2500` (kJ/kg y kJ/(kg·K)); el programa conserva `1,006`, `1,86` y `2501`. Para los datos del ejercicio, las entalpías son aproximadamente 54,914 y 54,949 kJ/kg, respectivamente: diferencia de 0,035 kJ/kg (~0,064 %). Se distingue la aproximación bibliográfica de la correlación del programa, sin sustituir constantes silenciosamente.

## Alcance y pendientes

- Las pruebas invocan funciones reales, pero los ejercicios con varias etapas y balances externos no suponen una operación única ejecutable en la interfaz. El ensayo de 15.C.10 sí ejercita el modo gas–vapor general interactivamente mediante entradas simuladas.
- 139/556 ejercicios identificados tienen algún contraste numérico documentado; **417 aún no tienen cotejo específico**. Parte de los restantes son conceptuales y requieren una revisión editorial diferente de la numérica.
- Tampoco se ha validado experimentalmente todo el dominio de los modelos ni ejecutado CI remoto con la copia local. GitHub y Zenodo conservan la publicación pública `v0.9.0`.

## Reproducción desde la raíz

```bash
python -m unittest discover -s pruebas_revision -p test_cotejo_integradores_05.py -v
python -m unittest discover -s pruebas_revision -q
python -m compileall -q capitulo_02 capitulo_03 capitulo_04 capitulo_05 capitulo_06 capitulo_07 capitulo_08 capitulo_09 capitulo_10 capitulo_11 capitulo_12 capitulo_13 capitulo_14 capitulo_15
python capitulo_10/propiedades_coligativas.py --selftest
python capitulo_10/disoluciones_electroliticas.py --selftest
python capitulo_14/combustion.py --self-test
python capitulo_15/psicrometria.py --validar
```

Detalle por caso: `MATRIZ_COTEJO_BLOQUE_05.json`.
