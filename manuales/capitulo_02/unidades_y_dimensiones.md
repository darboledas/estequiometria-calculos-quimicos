# Unidades, cifras significativas e incertidumbres

**Manual de usuario · Capítulo 2 · unidades_y_dimensiones.py**  
**Proyecto:** *Estequiometría y cálculos químicos*. **Estado:** documentación preliminar basada en el código recibido (6 de noviembre de 2026).

## 1. Finalidad y funciones

Conversión de unidades, redondeo, cálculo de incertidumbres y análisis dimensional mediante Buckingham.

Esta herramienta automatiza el cálculo y ayuda a verificarlo, pero no sustituye la selección del modelo químico ni la interpretación de sus hipótesis.

## 2. Requisitos e instalación

Se recomienda **Python 3.10 o posterior**. En Windows, abra PowerShell o Símbolo del sistema, entre en la carpeta del capítulo y ejecute la aplicación. Ejemplo desde la carpeta raíz del repositorio:

```bat
cd capitulo_02
python unidades_y_dimensiones.py
```

El programa se basa en la biblioteca estándar de Python para el cálculo principal. Las dependencias de visualización, cuando existan, se detallan en su ayuda.

## 3. Comandos y opciones de ejecución

**Iniciar con menú o con preguntas sucesivas:**

```bat
python unidades_y_dimensiones.py
```

**Consultar las opciones admitidas:**

```bat
python unidades_y_dimensiones.py --help
```

**Ejemplo de uso o comprobación del propio programa:**

```bat
python unidades_y_dimensiones.py convertir 2,5 atm Pa
```

Subórdenes directas disponibles: `convertir`, `redondear` y `unidades`; también admite `--autocomprobar`.

## 4. Menú principal y modos de cálculo

El menú mostrado por el programa, capturado durante esta revisión, ofrece las siguientes opciones:

```text
1. Conversión de unidades
2. Cifras significativas y redondeo
3. Propagación y expresión de incertidumbres
4. Análisis dimensional y teorema π de Buckingham
5. Mostrar unidades disponibles
0. Salir
```

## 5. Datos introducidos y unidades

Unidades del catálogo integrado; declarar siempre la unidad de origen y destino.

Algunos de los campos, selecciones o preguntas definidos explícitamente en el código son:

- `Pulse Intro para continuar...`
- `Opción:`
- `Valor:`
- `Número de magnitudes de entrada:`
- `Categoría:`
- `Valor tal como está escrito:`
- `Valor medido:`
- `Incertidumbre absoluta:`
- `Número de variables:`
- `Unidad de origen:`
- `Unidad de destino:`
- `Escala de origen:`
- `Escala de destino:`
- `Cifras significativas que desea conservar:`
- `Cifras significativas:`
- `Nombre o símbolo:`
- `Coeficiente de sensibilidad ∂R/∂x:`
- `Incertidumbre estándar o límite:`
- `Número de términos que desea comparar:`
- `Número de operandos:`
- `Operador (+, -, * o /):`
- `Sepárelos mediante espacios:`
- `Valor calculado:`
- `¿Hay correlaciones entre magnitudes? (s/n):`

## 6. Procedimiento recomendado paso a paso

1. Identifique en el capítulo el tipo de problema, las variables conocidas y las hipótesis necesarias.

2. Inicie el programa con `python unidades_y_dimensiones.py` desde la carpeta indicada.

3. Con el menú, seleccione «1. Conversión de unidades»; elija categoría, unidad inicial y final, y escriba el valor.

4. Introduzca los datos conservando las unidades del programa y las cifras significativas correspondientes.

5. Revise las magnitudes calculadas y, cuando el modo lo permita, los residuos de balance, las composiciones y los avisos de validez.

6. Si el resultado es físicamente imposible, examine los datos y los supuestos antes de repetir el cálculo.

## 7. Resultados, verificaciones y alcance científico

Los resultados dependen de la modalidad elegida. Consulte el desarrollo técnico siguiente, extraído de la descripción que acompaña al código, para conocer el modelo que el autor ha implementado y sus limitaciones.

```text
HERRAMIENTAS DEL CAPÍTULO 2: UNIDADES Y DIMENSIONES
Finalidad
Aplicación complementaria para efectuar y comprobar los cálculos repetitivos
del capítulo 2 de «Estequiometría y cálculos químicos»: conversiones de
unidades, cifras significativas, propagación lineal de incertidumbres y
análisis dimensional mediante el teorema pi de Buckingham.
Hipótesis y límites
* Las conversiones utilizan los factores declarados en UNIDADES. Los factores
  son exactos salvo que la definición de la unidad indique otra cosa.
* La propagación de incertidumbres aplica una aproximación lineal de primer
  orden. Las incertidumbres estándar se combinan mediante una matriz de
  covarianzas; la estimación máxima suma valores absolutos.
* La matriz de covarianzas debe ser simétrica. El programa comprueba además
  que la varianza calculada no sea negativa, pero no sustituye un análisis
  metrológico completo.
* El análisis de Buckingham obtiene una base racional del espacio nulo de la
  matriz dimensional. La base no es única: productos y potencias de los grupos
  obtenidos también constituyen grupos adimensionales válidos.
* El programa acepta punto o coma decimal en las entradas. En pantalla muestra
  coma decimal, de acuerdo con el uso habitual en español.
Entradas y salidas
Entradas: valores introducidos por teclado o, para conversiones y redondeos,
argumentos opcionales de línea de órdenes.
Salidas: resultados numéricos, unidades, contribuciones de incertidumbre y
grupos adimensionales. No se escriben archivos ni se modifican datos externos.
```

## 8. Ayuda real de línea de comandos

La salida siguiente fue obtenida al ejecutar `--help` sobre este archivo, no deducida de la documentación del libro:

```text
usage: unidades_y_dimensiones.py [-h] [--version] [--autocomprobar]
                                 {convertir,redondear,unidades} ...

Herramientas del capítulo 2: conversiones, cifras significativas,
incertidumbres y análisis dimensional. Sin argumentos abre el menú.

órdenes:
  {convertir,redondear,unidades}
    convertir           convierte una magnitud lineal
    redondear           redondea un valor al par
    unidades            muestra las unidades disponibles

opciones:
  -h, --help            muestra esta ayuda y termina
  --version             muestra la versión y termina
  --autocomprobar       ejecuta verificaciones internas y termina
```

## 9. Subcomandos disponibles

Cada subcomando dispone de ayuda propia con `python unidades_y_dimensiones.py SUBCOMANDO --help`. Se reproducen las opciones efectivamente declaradas:

### `convertir`

```text
usage: unidades_y_dimensiones.py convertir [-h] [-c CIFRAS]
                                           valor origen destino

positional arguments:
  valor                valor numérico; admite coma decimal
  origen               unidad de origen
  destino              unidad de destino

options:
  -h, --help           show this help message and exit
  -c, --cifras CIFRAS  cifras significativas de salida
```

### `redondear`

```text
usage: unidades_y_dimensiones.py redondear [-h] valor cifras

positional arguments:
  valor       valor numérico; admite coma decimal
  cifras      número de cifras significativas

options:
  -h, --help  show this help message and exit
```

### `unidades`

```text
usage: unidades_y_dimensiones.py unidades [-h]

options:
  -h, --help  show this help message and exit
```

## 10. Errores frecuentes y precauciones

- Ejecutar el archivo desde otra carpeta y no encontrar módulos auxiliares, tablas, ejemplos o rutas relativas.

- Mezclar unidades o bases de composición, o confundir fracciones con porcentajes.

- Utilizar ecuaciones o correlaciones fuera del intervalo para el que están previstas.

- Interpretar la precisión mostrada como una garantía experimental o física.

- Dar por único un problema con datos insuficientes o hipótesis no justificadas.

## 11. Ejemplo numérico verificado

Con el comando concreto del apartado 3 se obtuvo la siguiente salida, seleccionada literalmente entre los resultados de la ejecución real (el resto de la salida puede incluir más datos):

```text
2,5 × 10^5 Pa
```

## 12. Estado de revisión

Inicio y ayuda revisados; no se ha ejecutado una batería de casos numéricos exhaustiva para esta aplicación.

## 13. Correspondencia bibliográfica

Programa de apoyo al **capítulo 2** de *Estequiometría y cálculos químicos*. El texto del libro es una exposición científica; este manual explica la ejecución del software suministrado. El código y el manual se distribuyen bajo licencia MIT; DOI general del software: [10.5281/zenodo.24020474](https://doi.org/10.5281/zenodo.24020474). DOI de la versión publicada 0.9.0: [10.5281/zenodo.24020473](https://doi.org/10.5281/zenodo.24020473). DOI del libro: [10.5281/zenodo.24013068](https://doi.org/10.5281/zenodo.24013068).

## Anexo: validaciones incorporadas en la revisión posterior a 0.9.0

La función de propagación comprueba que la matriz de correlación introducida sea **semidefinida positiva**, además de simétrica, con diagonal unitaria y coeficientes entre −1 y 1. Una matriz que incumpla esta condición no describe correlaciones compatibles y se rechaza, incluso cuando una combinación concreta de sensibilidades produzca una varianza numéricamente positiva.

La función de cómputo de cifras significativas valida toda la notación científica, incluido el exponente; por ejemplo, `1e` y `1eXYZ` producen un error de entrada.

Estas modificaciones se incorporan como propuesta de actualización del código posterior a la versión archivada 0.9.0.


## Comprobación independiente de revisión integral

Caso de referencia: **1 pie = 0,3048 m**. Conversión de longitud; unidad de origen ft y destino m.

La prueba reproducible figura en `pruebas_revision/test_auditoria_integral.py`; los invariantes adicionales, cuando corresponden, están en `pruebas_revision/test_invariantes_cientificos.py`. Se trata de comprobaciones de casos seleccionados, no de una verificación exhaustiva del dominio del modelo.
