# Auditoría transversal de las 28 aplicaciones Python

**Proyecto:** Estequiometría y cálculos químicos — software complementario  
**Autor:** David Arboledas Brihuega  
**Fecha de la revisión:** 7 de noviembre de 2026  
**Fuente de partida:** paquete de código de la versión pública 0.9.0 y correcciones locales del bloque 01.  
**DOI general:** https://doi.org/10.5281/zenodo.24020474  
**DOI de la versión archivada 0.9.0:** https://doi.org/10.5281/zenodo.24020473

## 1. Resultado y límites

Se han inventariado e inspeccionado las 28 aplicaciones y comprobado el lanzamiento desde consola con `--help` (algunas aplicaciones no implementan esa opción y muestran su menú). Para cada aplicación se ha ejecutado al menos un caso independiente con solución conocida o comprobación de conservación. Se han añadido invariantes transversales y controles de entrada no física, además de repetir las pruebas ya incluidas en el proyecto.

**No se ha efectuado una validación científica exhaustiva de todas las modalidades, rangos de temperatura y presión, tablas de parámetros, modelos empíricos, salidas gráficas o problemas del libro.** La expresión «28 aplicaciones revisadas» significa cobertura de inventario, ejecución y al menos un caso de referencia por programa; no una certificación universal de resultados.

La copia preparada para entrega es una propuesta de actualización del repositorio; no se ha modificado el repositorio GitHub remoto ni el registro permanente de Zenodo.

## 2. Batería ejecutada

| Grupo | Alcance | Resultado |
|---|---|---|
| Pruebas de revisión en `pruebas_revision/` | 46 casos anteriores + 28 casos independientes (uno por aplicación) + 11 invariantes | **85 pruebas correctas** |
| Capítulo 9 | 24 casos de equilibrio líquido–líquido e inmiscibles | **24/24** |
| Capítulo 10A | Soluciones electrolíticas | **39/39** |
| Capítulo 10B | Propiedades coligativas | **38/38** |
| Capítulo 11 | Balances de materia | **58/58** |
| Capítulo 13 | Balances reactivos y precisión | **12/12** |
| Capítulo 14 | Combustión | **23/23** |
| Capítulo 15 | Validación interna de estados psicrométricos | **12 grupos correctos** |
| Interfaz de ayuda | 28 lanzamientos con `--help` sin error de salida; no todos proporcionan ayuda específica | **28/28** |
| Compilación | `compileall` de los capítulos 2 a 15 | **Correcta** |

Las 85 pruebas incluyen iteraciones internas sobre varios estados y composiciones, pero se cuentan como 85 métodos de prueba, no como un número artificialmente multiplicado de casos. Los recuentos de las autopruebas propias de cada capítulo siguen el formato de sus autores.

## 3. Incidencias verificadas y cambios introducidos

### H01. Capítulo 2

**Diagnóstico reproducible:** La matriz de correlación no semidefinida positiva pasaba las verificaciones simples.

**Intervención:** Rechazo de matrices incompatibles y pruebas de matrices singulares físicamente posibles.

### H02. Capítulo 3

**Diagnóstico reproducible:** La función auxiliar de cifras significativas aceptaba exponentes incompletos.

**Intervención:** Validación de número completo antes de computar precisión.

### H03. Capítulo 3

**Diagnóstico reproducible:** La interpretación de fórmulas permitía grupos vacíos internos.

**Intervención:** Rechazo de Fe()₂ y otros grupos vacíos.

### H04. Capítulo 4

**Diagnóstico reproducible:** La ecuación de gases ideales aceptaba NaN e infinito.

**Intervención:** Rechazo de todas las entradas no finitas o no positivas.

### H05. Capítulo 8

**Diagnóstico reproducible:** Presión de burbuja no ideal aceptaba fracciones molares negativas y valores no finitos; en un caso devolvía y negativa.

**Intervención:** Validación de dimensión, suma unitaria, dominio físico, coeficientes de actividad y presiones de vapor.

### H06. Capítulo 15

**Diagnóstico reproducible:** Dos funciones de razón de humedad aceptaban presión total nula o valores no finitos.

**Intervención:** Rechazo explícito de P ≤ 0, NaN e infinito y de W no físico.

### H07. Documentación

**Diagnóstico reproducible:** El Word contenía referencias al DOI aún pendiente y resultados antiguos de pruebas de cap. 13.

**Intervención:** Actualización del DOI, notas de comprobación por aplicación y anexo de revisión.

## 4. Comprobación de cada aplicación

| Cap. | Aplicación | Referencia de contraste reproducida |
|---|---|---|
| 2 | `unidades_y_dimensiones.py` | 1 pie = 0,3048 m |
| 3 | `ajuste_ecuaciones.py` | 2 H₂ + O₂ → 2 H₂O |
| 3 | `conversion_rendimiento_selectividad.py` | 10 mol iniciales y 6 mol finales ⇒ X = 0,4 |
| 3 | `densidades_y_escalas.py` | 0 °Brix en la tabla incorporada ⇒ GE = 1 |
| 3 | `masa_molar.py` | M(H₂O) ≈ 18,015 g/mol |
| 3 | `reactivo_limitante.py` | Alimentación 4 A y 1 B, reacción 2 A + B → 2 C ⇒ ξ = 1; C = 2 mol |
| 4 | `gases_ideales_y_mezclas.py` | P = nRT/V con n = 1 mol, T = 300 K y V = 0,025 m³ |
| 5 | `gases_reales.py` | Z = 1 + B′P con B′ = −0,002 bar⁻¹ y P = 10 bar ⇒ Z = 0,98 |
| 6 | `presion_vapor.py` | Antoine directo e inverso a 300 K; Clausius–Clapeyron con T₁ = T₂ ⇒ P₂ = P₁ |
| 6 | `vapor_agua.py` | A 100 °C, presión de saturación ≈ 101,418 kPa |
| 7 | `equilibrio_liquido_vapor.py` | Raoult: x = (0,4; 0,6), P* = (80; 40) kPa ⇒ P = 56 kPa |
| 7 | `operaciones_liquido_vapor.py` | Flash: z = (0,5; 0,5), K = (2; 0,5) ⇒ β = 0,5 |
| 8 | `disoluciones_no_ideales.py` | Límite ideal γ = 1: x = (0,2; 0,8), P* = (100; 50) kPa ⇒ P = 60 kPa |
| 9 | `equilibrio_liquido_liquido.py` | Regla de la palanca: z = 0,5, extremos 0,2 y 0,8, total 10 ⇒ L₁ = L₂ = 5 |
| 9 | `inmiscibles_y_arrastre_vapor.py` | Condensación de 10 mol de vapor con yB = 0,4, M_A = 18 y M_B = 92 g/mol |
| 10 | `disoluciones_electroliticas.py` | NaCl 0,1 mol/kg idealmente disociado ⇒ I = 0,1 mol/kg |
| 10 | `propiedades_coligativas.py` | π = i c R T, c = 0,1 mol/L y T = 300 K |
| 11 | `balances_materia.py` | x + y = 3, x − y = 1 ⇒ (x, y) = (2, 1) |
| 12 | `cristalizacion.py` | 100 kg de soluto, solubilidades 50→25 kg/100 kg de disolvente ⇒ 50 kg de cristales |
| 12 | `evaporacion.py` | 100 kg de alimentación al 20 % y salida al 40 % ⇒ 50 kg de evaporado |
| 12 | `extraccion_liquido_liquido.py` | 100 unidades de soluto; V_R = V_D = 10, K_D = 2 ⇒ 33,3 en refinado |
| 12 | `filtracion.py` | 100 kg al 20 % de sólidos, recuperación 80 % y torta al 40 % ⇒ 60 kg de filtrado |
| 12 | `secado.py` | 100 kg con humedad inicial 40 % y final 20 % (base húmeda) ⇒ 25 kg de agua eliminada |
| 12 | `separacion_corrientes.py` | 100 kg/h al 30 %, salidas al 50 % y 10 % ⇒ 50 kg/h en cada corriente |
| 13 | `balance_una_reaccion.py` | A → 2 B; nA0 = 3 mol, ξ = 2 mol ⇒ nA = 1, nB = 4 mol |
| 13 | `balance_varias_reacciones.py` | A → B → C; nA0 = 5, ξ₁ = 3, ξ₂ = 1 ⇒ (A,B,C)=(2,2,1) |
| 14 | `combustion.py` | CH₄ + 2 O₂ → CO₂ + 2 H₂O |
| 15 | `psicrometria.py` | A 25 °C, p*H₂O ≈ 3,17 kPa; W = 0,621945 pw/(P−pw) |

Las pruebas se encuentran en `pruebas_revision/test_auditoria_integral.py` y `pruebas_revision/test_invariantes_cientificos.py`. Las aplicaciones del capítulo 12 se han ejecutado mediante respuestas reales suministradas por la entrada estándar; se han verificado cantidades de salida y no solo el código de salida.

## 5. Validaciones que aún deben ampliarse antes de una certificación científica completa

1. **Propiedades reales, gas y vapor (capítulos 5 y 6):** contrastar cada conjunto de constantes, dominio de Antoine y modelos de virial/cúbicos en varias zonas del diagrama de fases, especialmente cerca del punto crítico.
2. **Equilibrios VLE y LLE (capítulos 7 a 9):** verificar sistemáticamente todos los menús de flash, métodos iterativos, Wilson, Van Laar, Margules, límites de miscibilidad y correlaciones experimentales.
3. **Electrólitos y coligativas (capítulo 10):** comparar SIT/Pitzer y parámetros externos con fuentes primarias y límites de fuerza iónica; las comprobaciones actuales no cubren todas las sales.
4. **Balances complejos y operaciones (capítulos 11 a 13):** ampliar los datos de entrada con composiciones redundantes, flujos recirculados, separaciones no lineales y sistemas mal condicionados.
5. **Combustión y psicrometría (capítulos 14 y 15):** contrastar todos los modos inversos, temperaturas extremas, cambios de fase y salidas gráficas con referencias externas.
6. **Manual respecto al libro:** todavía hay que cotejar uno por uno los valores de los ejercicios del volumen impreso con las salidas, no solo con los casos de prueba independientes.

Por tanto, se recomienda considerar el presente paquete **candidato a integración y pruebas en GitHub**, no una certificación definitiva ni una demostración de que los 28 programas son correctos para cualquier entrada.

## 6. Referencias para los contrastes y los límites de los modelos

- IAPWS, lista oficial de releases y formulaciones termodinámicas del agua: https://iapws.org/documents/release
- ASHRAE Handbook, capítulo de psicrometría y razón de humedad: https://handbook.ashrae.org/Handbooks/F17/SI/f17_ch01/f17_ch01_si.aspx
- NIST Chemistry WebBook, ecuación de Antoine con identificación explícita de unidades e intervalos: https://webbook.nist.gov/cgi/cbook.cgi?ID=C7732185&Type=ANTOINE
- La referencia de incertidumbres y matrices de correlación consta en `REVISIONES/INFORME_BLOQUE_01.md`.

## 7. Entrega y publicación diferida

El paquete integral se debe copiar en una sola operación a una copia GitHub Desktop sincronizada. Una vez que GitHub Actions termine con éxito, puede crearse una nueva versión con un número distinto de `v0.9.0`. No se ha generado ni reservado aún DOI de esa nueva versión; Zenodo lo asignará cuando se publique una nueva release y la integración siga activa.

**Nota de trazabilidad:** la release `v0.9.0` y su DOI específico no deben alterarse retroactivamente.
