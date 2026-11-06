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

Programa de apoyo al **capítulo 8** de *Estequiometría y cálculos químicos*. El texto del libro es una exposición científica; este manual explica la ejecución del software suministrado. El código y el manual se distribuyen bajo licencia MIT; el DOI específico del software se incorporará tras la primera publicación en Zenodo.
