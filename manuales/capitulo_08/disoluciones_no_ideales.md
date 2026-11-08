# Disoluciones no ideales y actividad

**Manual de usuario · Capítulo 8 · disoluciones_no_ideales.py**  
**Proyecto:** *Estequiometría y cálculos químicos*. **Estado:** documentación preliminar basada en el código recibido (6 de noviembre de 2026).

## 1. Finalidad y funciones

Modelos Margules, Van Laar y Wilson; actividad, ELV modificado, azeótropos, flash, diagramas y ajuste.

Esta herramienta automatiza el cálculo y ayuda a verificarlo, pero no sustituye la selección del modelo químico ni la interpretación de sus hipótesis.

## 2. Requisitos e instalación

Se recomienda **Python 3.10 o posterior**. En Windows, abra PowerShell o Símbolo del sistema, entre en la carpeta del capítulo y ejecute la aplicación. Ejemplo desde la carpeta raíz del repositorio:

```bat
cd capitulo_08
python disoluciones_no_ideales.py
```

Este programa necesita **NumPy** y utiliza **Matplotlib** para representar diagramas. Instale las dependencias con `python -m pip install numpy matplotlib`.

## 3. Comandos y opciones de ejecución

**Iniciar con menú o con preguntas sucesivas:**

```bat
python disoluciones_no_ideales.py
```

**Consultar las opciones admitidas:**

```bat
python disoluciones_no_ideales.py --help
```

**Ejemplo de uso o comprobación del propio programa:**

```bat
python disoluciones_no_ideales.py --help
```

## 4. Menú principal y modos de cálculo

El menú mostrado por el programa, capturado durante esta revisión, ofrece las siguientes opciones:

```text
1. Actividad, coeficientes de actividad y gE
2. Presión de burbuja
3. Presión de rocío
4. Temperatura de burbuja
5. Temperatura de rocío
6. Azeótropos binarios
7. Vaporización flash binaria
8. Cálculo γ-φ con φ y Poynting constantes
9. Diagramas y gráficas
10. Ajuste de parámetros a datos ELV
11. Comprobaciones y utilidades docentes
0. Salir
```

## 5. Datos introducidos y unidades

El script no desarrolla NRTL ni UNIQUAC: el propio código delimita expresamente esa cobertura.

Algunos de los campos, selecciones o preguntas definidos explícitamente en el código son:

- `Número máximo de iteraciones [200]:`
- `¿Guardar la figura en PNG transparente a 300 ppp?`
- `¿Mostrar la figura en pantalla?`
- `T (K), si desea gE en J/mol:`
- `¿Representar γ_i y gE/RT frente a x1?`
- `Número de componentes [2]:`
- `T (K):`
- `¿Comparar con la predicción ideal?`
- `Factor de relajación (0 < r <= 1) [1]:`
- `Límite inferior de T (K):`
- `Límite superior de T (K):`
- `temperatura (K)`
- `Tolerancia interna para composición [1e-8]:`
- `Factor de relajación interno (0 < r <= 1) [1]:`
- `z1 (composición global):`
- `Número de puntos experimentales:`
- `P1* a la T experimental:`
- `P2* a la T experimental:`
- `¿Fase líquida ideal?`
- `Número de pares experimentales x-y:`
- `¿Calcular etapas desde una composición inicial?`
- `Opción:`
- `Composición líquida inicial x1:`
- `Composición líquida objetivo:`

La relación anterior es ilustrativa: ciertos campos solo aparecen al elegir subopciones.

## 6. Procedimiento recomendado paso a paso

1. Identifique en el capítulo el tipo de problema, las variables conocidas y las hipótesis necesarias.

2. Inicie el programa con `python disoluciones_no_ideales.py` desde la carpeta indicada.

3. Seleccione 1 para propiedades de actividad; 2–5 para burbuja/rocío; 9 para diagramas.

4. Introduzca los datos conservando las unidades del programa y las cifras significativas correspondientes.

5. Revise las magnitudes calculadas y, cuando el modo lo permita, los residuos de balance, las composiciones y los avisos de validez.

6. Si el resultado es físicamente imposible, examine los datos y los supuestos antes de repetir el cálculo.

## 7. Resultados, verificaciones y alcance científico

Los resultados dependen de la modalidad elegida. Consulte el desarrollo técnico siguiente, extraído de la descripción que acompaña al código, para conocer el modelo que el autor ha implementado y sus limitaciones.

```text
Herramienta docente para el capítulo 8: disoluciones no ideales y
coeficientes de actividad.
Incluye:
- Actividad, g^E y potencial químico de exceso.
- Margules de un parámetro.
- Margules de dos parámetros (tres sufijos).
- Van Laar.
- Wilson.
- Ley de Raoult modificada.
- Formulación gamma-phi con correcciones constantes.
- Presión de burbuja y de rocío.
- Temperatura de burbuja y de rocío.
- Azeótropos binarios.
- Vaporización flash binaria.
- Diagramas gamma-x, g^E/RT-x, y-x, P-x-y y T-x-y.
- Ajuste de Margules de dos parámetros y Van Laar a datos ELV.
- Control explícito de convergencia.
- Redondeo final atendiendo a las cifras significativas de los datos.
Dependencias:
    Python >= 3.9
    numpy
    matplotlib
Criterio de precisión:
    Los cálculos internos se realizan sin redondeos intermedios deliberados.
    El redondeo se aplica al presentar el resultado final. Las cifras
    significativas se deducen de las cadenas introducidas por el usuario.
    Para ceros finales significativos, use decimal o notación científica:
        330      -> se interpreta con 2 cifras significativas
        330.     -> 3 cifras significativas
        3.30e2   -> 3 cifras significativas
Nota:
    El capítulo presenta NRTL y UNIQUAC de forma introductoria, sin desarrollar
    sus ecuaciones completas. Por ese motivo este programa no inventa una
    implementación de dichos modelos. Sí permite usar coeficientes de actividad
    introducidos directamente para cálculos de ELV.
```

## 8. Ayuda real de línea de comandos

La salida siguiente fue obtenida al ejecutar `--help` sobre este archivo, no deducida de la documentación del libro:

```text
usage: disoluciones_no_ideales.py [-h] [--version]

Cálculos del capítulo 8: disoluciones no ideales y ELV.

options:
  -h, --help  show this help message and exit
  --version   show program's version number and exit

El programa deduce las cifras significativas de los datos escritos por el
usuario y redondea solo al presentar los resultados. NRTL y UNIQUAC no se
implementan porque el capítulo no desarrolla sus ecuaciones completas.
```

## 9. Submenús y opciones internas

Los submenús se muestran dentro del programa al seleccionar las opciones principales. Para la versión documentada no se ha observado una interfaz independiente de subcomandos.

## 10. Errores frecuentes y precauciones

- Ejecutar el archivo desde otra carpeta y no encontrar módulos auxiliares, tablas, ejemplos o rutas relativas.

- Mezclar unidades o bases de composición, o confundir fracciones con porcentajes.

- Utilizar ecuaciones o correlaciones fuera del intervalo para el que están previstas.

- Interpretar la precisión mostrada como una garantía experimental o física.

- Dar por único un problema con datos insuficientes o hipótesis no justificadas.

## 11. Estado de revisión

Inicio y ayuda revisados; no se ha ejecutado una batería de casos numéricos exhaustiva para esta aplicación.

## 12. Correspondencia bibliográfica

Programa de apoyo al **capítulo 8** de *Estequiometría y cálculos químicos*. El texto del libro es una exposición científica; este manual explica la ejecución del software suministrado. El código y el manual se distribuyen bajo licencia MIT; DOI general del software: [10.5281/zenodo.24020474](https://doi.org/10.5281/zenodo.24020474). DOI de la versión publicada 0.9.0: [10.5281/zenodo.24020473](https://doi.org/10.5281/zenodo.24020473). DOI del libro: [10.5281/zenodo.24013068](https://doi.org/10.5281/zenodo.24013068).


## Comprobación independiente de revisión integral

Caso de referencia: **Límite ideal γ = 1: x = (0,2; 0,8), P* = (100; 50) kPa ⇒ P = 60 kPa**. Coincidencia con Raoult y rechazo de composiciones no físicas.

La prueba reproducible figura en `pruebas_revision/test_auditoria_integral.py`; los invariantes adicionales, cuando corresponden, están en `pruebas_revision/test_invariantes_cientificos.py`. Se trata de comprobaciones de casos seleccionados, no de una verificación exhaustiva del dominio del modelo.

### Nota de verificación científica adicional

Revisión adicional (7-11-2026): se ha comprobado numéricamente la relación diferencial de Gibbs–Duhem para Margules de uno y dos parámetros, Van Laar y Wilson en cinco composiciones binarias cada uno. Esto contrasta la consistencia termodinámica local del modelo implementado, pero no valida parámetros ajustados a datos experimentales.


## 13. Cotejo integrador y control de datos γ–φ (7-11-2026, no publicado)

Se verificó la formulación a factores tabulados del ejercicio **8.C.5** del libro definitivo:

- Raoult modificado: **395,0 kPa**, composición del vapor `(0,65823; 0,34177)`.
- γ–φ: **424,5867 kPa**, composición `(0,665343; 0,334657)`.
- Error relativo tomando γ–φ como referencia: **−6,97 %**.

`bubble_pressure_gamma_phi` comprueba que `x` contenga fracciones molares válidas que sumen la unidad, temperatura absoluta positiva y finita, un valor de cada factor por componente, y que presiones, actividades, fugacidades y Poynting sean estrictamente positivos y finitos. Se rechazan `NaN`, infinito, dimensiones no coincidentes y resultados no físicos. Las entradas válidas conservan sus valores numéricos.

La función trata los factores como constantes **porque así lo impone el ejercicio**; en un cálculo real dependen en general de presión, temperatura y composición. La prueba no valida valores experimentales ni el rango de aplicación de modelos γ–φ.

Referencias: `pruebas_revision/test_cotejo_integradores_03.py` y `REVISIONES/INFORME_COTEJO_INTEGRADORES_90.md`.

### Bloque VI (7-11-2026) — ajuste de datos experimentales de actividad

La función `experimental_gammas(x1, y1, P, ps1, ps2)` requiere vectores de idéntica longitud, valores finitos y físicamente válidos: 0 < x1,y1 < 1, P>0 y presiones de vapor positivas. No se permiten NaN, infinito ni vectores incompletos. Las funciones `fit_margules2` y `fit_van_laar` exigen al menos dos observaciones completas y gamma finitos y positivos. El ajuste de Margules también rechaza un sistema incapaz de identificar sus dos parámetros.

**Ejercicio 8.C.2:** con las seis parejas experimentales del libro, Margules da A12≈1,0000017; A21≈0,6002903, y Van Laar A12≈1,0415701; A21≈0,6490926. El error medio absoluto de presión es ≈0,00312 kPa (Margules) y ≈0,21624 kPa (Van Laar). Estas cifras se refieren solo a la tabla de ese ejercicio.

Reproducción: `python -m unittest discover -s pruebas_revision -p test_cotejo_bloque_06.py -v`.

## Revisión de controles científicos — Bloque X

Las utilidades para el ajuste de modelos (EMA/RECM) rechazan ahora conjuntos experimentales de distinta longitud, vectores vacíos y datos `NaN` o infinitos. Las utilidades de azeótropos de Margules de un parámetro rechazan coeficientes o presiones de vapor no finitos, en lugar de devolver composiciones indefinidas o interpretar `NaN` como ausencia de azeótropo.

**Controles positivos:** ejercicios 8.B.12, 8.B.13, 8.B.14 y 8.B.15 del libro. El resultado de un ajuste no prueba su aplicabilidad fuera del intervalo experimental ni su adecuación termodinámica.
