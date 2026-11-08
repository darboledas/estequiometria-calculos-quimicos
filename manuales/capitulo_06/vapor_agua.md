# Propiedades de saturación del agua

**Manual de usuario · Capítulo 6 · vapor_agua.py**  
**Proyecto:** *Estequiometría y cálculos químicos*. **Estado:** documentación preliminar basada en el código recibido (6 de noviembre de 2026).

## 1. Finalidad y funciones

Saturación a partir de T o P, identificación de región, calidad de vapor y diagramas T–v.

Esta herramienta automatiza el cálculo y ayuda a verificarlo, pero no sustituye la selección del modelo químico ni la interpretación de sus hipótesis.

## 2. Requisitos e instalación

Se recomienda **Python 3.10 o posterior**. En Windows, abra PowerShell o Símbolo del sistema, entre en la carpeta del capítulo y ejecute la aplicación. Ejemplo desde la carpeta raíz del repositorio:

```bat
cd capitulo_06
python vapor_agua.py
```

**Gráficos:** requieren `matplotlib` (instalable con `python -m pip install matplotlib`). Los cálculos no gráficos pueden tener menos dependencias.

## 3. Comandos y opciones de ejecución

**Iniciar con menú o con preguntas sucesivas:**

```bat
python vapor_agua.py
```

**Consultar las opciones admitidas:**

```bat
python vapor_agua.py --help
```

**Ejemplo de uso o comprobación del propio programa:**

```bat
python vapor_agua.py temperatura --T 100 --unidad-T C
```

## 4. Menú principal y modos de cálculo

El menú mostrado por el programa, capturado durante esta revisión, ofrece las siguientes opciones:

```text
1. Propiedades de saturación a partir de la temperatura
2. Propiedades de saturación a partir de la presión
3. Identificar el estado a partir de P y T
4. Calcular calidad o título de vapor
5. Calcular propiedades de una mezcla a partir de x
6. Generar diagrama T-v
7. Cambiar cifras significativas
0. Salir
```

## 5. Datos introducidos y unidades

Distingue líquido saturado, mezcla y vapor saturado; no sustituye una implementación completa de IAPWS-95.

Algunos de los campos, selecciones o preguntas definidos explícitamente en el código son:

- `Definir el estado de saturación mediante P o T`
- `Temperatura:`
- `Unidad de temperatura`
- `Presión:`
- `Unidad de presión`
- `Seleccione una opción:`
- `Unidad`
- `Tolerancia para considerar saturación (°C)`
- `Propiedad conocida`
- `Calidad x (0–1):`
- `¿Desea localizar una mezcla bifásica?`
- `Número de cifras significativas (1–8):`
- `Nombre del PNG [campana_Tv_agua.png]:`

## 6. Procedimiento recomendado paso a paso

1. Identifique en el capítulo el tipo de problema, las variables conocidas y las hipótesis necesarias.

2. Inicie el programa con `python vapor_agua.py` desde la carpeta indicada.

3. Seleccione 1 para T conocida; 2 para P conocida; 4 para calidad y 6 para diagrama T–v.

4. Introduzca los datos conservando las unidades del programa y las cifras significativas correspondientes.

5. Revise las magnitudes calculadas y, cuando el modo lo permita, los residuos de balance, las composiciones y los avisos de validez.

6. Si el resultado es físicamente imposible, examine los datos y los supuestos antes de repetir el cálculo.

## 7. Resultados, verificaciones y alcance científico

Los resultados dependen de la modalidad elegida. Consulte el desarrollo técnico siguiente, extraído de la descripción que acompaña al código, para conocer el modelo que el autor ha implementado y sus limitaciones.

```text
Herramienta didáctica para trabajar con propiedades de saturación del agua en
el capítulo 6 («Presión de vapor y equilibrio de fases») de un curso de
estequiometría y cálculos químicos.
FUNCIONALIDAD
1. Obtener propiedades de saturación a partir de la temperatura.
2. Obtener propiedades de saturación a partir de la presión.
3. Interpolar propiedades entre valores tabulados.
4. Identificar el estado de una muestra de agua a partir de P y T.
5. Calcular la calidad o título de vapor x a partir de v, h o s.
6. Calcular propiedades de una mezcla líquido-vapor a partir de x.
7. Generar un diagrama T-v sencillo de la campana de saturación y, opcionalmente,
   localizar un estado bifásico.
DATOS Y MODELO
- La tabla interna contiene propiedades de saturación del agua entre el punto
  triple y el punto crítico. Los valores proceden de la tabulación NISTIR 5078,
  calculada a partir de IAPWS-95.
- Para P_sat(T) se utiliza la correlación internacional de presión de saturación
  del agua (forma de Wagner/IAPWS), lo que evita obtener la presión mediante una
  interpolación lineal grosera.
- Las propiedades v_f, v_g, h_f, h_g, s_f y s_g se interpolan linealmente entre
  los nodos tabulados. El programa es didáctico: no sustituye a una implementación
  completa de IAPWS-95 cuando se requiera alta precisión, especialmente cerca del
  punto crítico.
UNIDADES INTERNAS
Temperatura: °C (se acepta también K en la entrada)
Presión: kPa (se aceptan kPa, bar, MPa y atm)
Volumen específico: m³ kg⁻¹
Entalpía específica: kJ kg⁻¹
Entropía específica: kJ kg⁻¹ K⁻¹
Ejecución interactiva:
Ayuda:
Ejemplos de línea de comandos:
CIFRAS SIGNIFICATIVAS
Los cálculos se realizan con precisión completa. El redondeo se aplica solo a
la presentación de los resultados. Por defecto se muestran 3 cifras
significativas; puede cambiarse con --sig.
LIMITACIONES
- Solo trata el equilibrio líquido-vapor del agua desde el punto triple hasta
  el punto crítico.
- No calcula propiedades de líquido comprimido ni de vapor sobrecalentado.
- La identificación de estado mediante P y T solo clasifica la región; no
  calcula propiedades monofásicas fuera de la saturación.
- La interpolación de propiedades es lineal entre nodos de la tabla interna.
- Cerca del punto crítico las propiedades cambian con rapidez; para cálculos de
  alta precisión debe utilizarse una implementación oficial/completa de IAPWS.
FUENTE PRINCIPAL DE DATOS
Harvey, A. H. (1998). Thermodynamic Properties of Water: Tabulation from the
IAPWS Formulation 1995 for the Thermodynamic Properties of Ordinary Water
Substance for General and Scientific Use. NISTIR 5078.
https://doi.org/10.6028/NIST.IR.5078
```

## 8. Ayuda real de línea de comandos

La salida siguiente fue obtenida al ejecutar `--help` sobre este archivo, no deducida de la documentación del libro:

```text
usage: vapor_agua.py [-h] [--sig SIG]
                     {temperatura,presion,estado,titulo,mezcla,grafica} ...

Propiedades de saturación del agua, identificación de estado, calidad de vapor y diagrama T-v.

positional arguments:
  {temperatura,presion,estado,titulo,mezcla,grafica}
    temperatura         Propiedades de saturación a partir de T.
    presion             Propiedades de saturación a partir de P.
    estado              Clasifica el estado a partir de P y T.
    titulo              Calcula x a partir de v, h o s en saturación.
    mezcla              Propiedades de una mezcla saturada a partir de x.
    grafica             Genera el diagrama T-v de saturación.

options:
  -h, --help            show this help message and exit
  --sig SIG             Cifras significativas de salida (por defecto: 3).

Sin subcomando se abre un menú interactivo. Los datos internos proceden de NISTIR 5078 / IAPWS-95.
```

## 9. Subcomandos disponibles

Cada subcomando dispone de ayuda propia con `python vapor_agua.py SUBCOMANDO --help`. Se reproducen las opciones efectivamente declaradas:

### `temperatura`

```text
usage: vapor_agua.py temperatura [-h] [--sig SIG] --T T [--unidad-T {C,K}]

options:
  -h, --help        show this help message and exit
  --sig SIG         Cifras significativas de salida (también puede indicarse
                    antes del subcomando).
  --T T             Temperatura.
  --unidad-T {C,K}
```

### `presion`

```text
usage: vapor_agua.py presion [-h] [--sig SIG] --P P
                             [--unidad-P {kPa,bar,MPa,atm}]

options:
  -h, --help            show this help message and exit
  --sig SIG             Cifras significativas de salida (también puede
                        indicarse antes del subcomando).
  --P P                 Presión.
  --unidad-P {kPa,bar,MPa,atm}
```

### `estado`

```text
usage: vapor_agua.py estado [-h] [--sig SIG] --P P
                            [--unidad-P {kPa,bar,MPa,atm}] --T T
                            [--unidad-T {C,K}] [--tol TOL]

options:
  -h, --help            show this help message and exit
  --sig SIG             Cifras significativas de salida (también puede
                        indicarse antes del subcomando).
  --P P
  --unidad-P {kPa,bar,MPa,atm}
  --T T
  --unidad-T {C,K}
  --tol TOL             Tolerancia en °C para considerar saturación (defecto:
                        0,10).
```

### `titulo`

```text
usage: vapor_agua.py titulo [-h] [--sig SIG] (--P P | --T T)
                            [--unidad-P {kPa,bar,MPa,atm}] [--unidad-T {C,K}]
                            --prop {v,h,s} --valor VALOR

options:
  -h, --help            show this help message and exit
  --sig SIG             Cifras significativas de salida (también puede
                        indicarse antes del subcomando).
  --P P
  --T T
  --unidad-P {kPa,bar,MPa,atm}
  --unidad-T {C,K}
  --prop {v,h,s}
  --valor VALOR         Valor de la propiedad específica.
```

### `mezcla`

```text
usage: vapor_agua.py mezcla [-h] [--sig SIG] (--P P | --T T)
                            [--unidad-P {kPa,bar,MPa,atm}] [--unidad-T {C,K}]
                            --x X

options:
  -h, --help            show this help message and exit
  --sig SIG             Cifras significativas de salida (también puede
                        indicarse antes del subcomando).
  --P P
  --T T
  --unidad-P {kPa,bar,MPa,atm}
  --unidad-T {C,K}
  --x X
```

### `grafica`

```text
usage: vapor_agua.py grafica [-h] [--sig SIG] [--salida SALIDA] [--dpi DPI]
                             [--x X] [--P P | --T T]
                             [--unidad-P {kPa,bar,MPa,atm}] [--unidad-T {C,K}]

options:
  -h, --help            show this help message and exit
  --sig SIG             Cifras significativas de salida (también puede
                        indicarse antes del subcomando).
  --salida SALIDA
  --dpi DPI
  --x X                 Calidad para localizar una mezcla.
  --P P
  --T T
  --unidad-P {kPa,bar,MPa,atm}
  --unidad-T {C,K}
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
T_sat : 100 °C  (373 K)
P_sat : 101 kPa
```

## 12. Estado de revisión

Inicio y ayuda revisados; no se ha ejecutado una batería de casos numéricos exhaustiva para esta aplicación.

## 13. Correspondencia bibliográfica

Programa de apoyo al **capítulo 6** de *Estequiometría y cálculos químicos*. El texto del libro es una exposición científica; este manual explica la ejecución del software suministrado. El código y el manual se distribuyen bajo licencia MIT; DOI general del software: [10.5281/zenodo.24020474](https://doi.org/10.5281/zenodo.24020474). DOI de la versión publicada 0.9.0: [10.5281/zenodo.24020473](https://doi.org/10.5281/zenodo.24020473). DOI del libro: [10.5281/zenodo.24013068](https://doi.org/10.5281/zenodo.24013068).


## Comprobación independiente de revisión integral

Caso de referencia: **A 100 °C, presión de saturación ≈ 101,418 kPa**. Punto de referencia de agua saturada; tolerancia 0,12 kPa.

La prueba reproducible figura en `pruebas_revision/test_auditoria_integral.py`; los invariantes adicionales, cuando corresponden, están en `pruebas_revision/test_invariantes_cientificos.py`. Se trata de comprobaciones de casos seleccionados, no de una verificación exhaustiva del dominio del modelo.
