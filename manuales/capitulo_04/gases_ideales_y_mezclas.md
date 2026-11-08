# Gases ideales y mezclas gaseosas

**Manual de usuario · Capítulo 4 · gases_ideales_y_mezclas.py**  
**Proyecto:** *Estequiometría y cálculos químicos*. **Estado:** documentación preliminar basada en el código recibido (6 de noviembre de 2026).

## 1. Finalidad y funciones

Aplicación de PV=nRT, ley combinada, conversiones de presión, densidad y mezclas de gases ideales.

Esta herramienta automatiza el cálculo y ayuda a verificarlo, pero no sustituye la selección del modelo químico ni la interpretación de sus hipótesis.

## 2. Requisitos e instalación

Se recomienda **Python 3.10 o posterior**. En Windows, abra PowerShell o Símbolo del sistema, entre en la carpeta del capítulo y ejecute la aplicación. Ejemplo desde la carpeta raíz del repositorio:

```bat
cd capitulo_04
python gases_ideales_y_mezclas.py
```

El programa se basa en la biblioteca estándar de Python para el cálculo principal. Las dependencias de visualización, cuando existan, se detallan en su ayuda.

## 3. Comandos y opciones de ejecución

**Iniciar con menú o con preguntas sucesivas:**

```bat
python gases_ideales_y_mezclas.py
```

**Consultar las opciones admitidas:**

```bat
python gases_ideales_y_mezclas.py --help
```

**Ejemplo de uso o comprobación del propio programa:**

```bat
python gases_ideales_y_mezclas.py --help
```

## 4. Menú principal y modos de cálculo

El menú mostrado por el programa, capturado durante esta revisión, ofrece las siguientes opciones:

```text
1. Resolver PV = nRT
2. Ley combinada entre dos estados
3. Presión manométrica -> absoluta
4. Densidad / masa molar / gravedad específica
5. Teoría cinético-molecular
6. Analizar mezcla ideal
7. Relaciones volumétricas estequiométricas
8. Lista de gases incorporados
9. Ayuda
0. Salir
```

## 5. Datos introducidos y unidades

Compruebe que P es absoluta y T está en kelvin en las ecuaciones de estado.

Algunos de los campos, selecciones o preguntas definidos explícitamente en el código son:

- `Componentes (ej. CO2:10;N2:90):`
- `Volumen de referencia:`
- `Opción:`
- `Gas para u_rms (vacío para omitir):`
- `Masas molares personalizadas, si hacen falta (ej. X:50,0; vacío = ninguna):`
- `P total (vacío si no se conoce):`
- `T (vacío si no se requiere densidad):`
- `V total (vacío si no se requieren volúmenes parciales):`
- `Unidad de P [bar]:`
- `Unidad de V [L]:`
- `Unidad de n [mol]:`
- `Unidad de T [K]:`
- `Gas (o deje vacío si introducirá M):`
- `M / (g/mol) [vacío = buscar gas]:`
- `rho / (kg m^-3):`
- `Unidad [K]:`
- `Base [molar/masa/presion] (molar):`
- `Unidad [L]:`
- `Unidad [bar]:`
- `M_media / (g/mol):`
- `Unidad T [K]:`
- `Unidad V [L]:`
- `Especies separadas por ';':`
- `Coeficientes estequiométricos en el mismo orden, separados por ';':`

La relación anterior es ilustrativa: ciertos campos solo aparecen al elegir subopciones.

## 6. Procedimiento recomendado paso a paso

1. Identifique en el capítulo el tipo de problema, las variables conocidas y las hipótesis necesarias.

2. Inicie el programa con `python gases_ideales_y_mezclas.py` desde la carpeta indicada.

3. Opción 1 para resolver la ecuación de estado; los subcomandos también permiten resolver sin menú.

4. Introduzca los datos conservando las unidades del programa y las cifras significativas correspondientes.

5. Revise las magnitudes calculadas y, cuando el modo lo permita, los residuos de balance, las composiciones y los avisos de validez.

6. Si el resultado es físicamente imposible, examine los datos y los supuestos antes de repetir el cálculo.

## 7. Resultados, verificaciones y alcance científico

Los resultados dependen de la modalidad elegida. Consulte el desarrollo técnico siguiente, extraído de la descripción que acompaña al código, para conocer el modelo que el autor ha implementado y sus limitaciones.

```text
Herramienta didáctica para el capítulo 4 «Gases ideales y mezclas gaseosas».
Funciones principales
* Ecuación del gas ideal: resuelve P, V, n o T a partir de las otras tres.
* Ley combinada para una cantidad fija de gas.
* Conversión de presión manométrica a absoluta.
* Densidad, masa molar y gravedad específica respecto al aire.
* Teoría cinético-molecular: energía cinética media y velocidad cuadrática media.
* Mezclas ideales: fracciones molares, presiones parciales (Dalton), volúmenes
  parciales (Amagat), masa molar media, fracciones másicas, densidad y GE.
* Conversión entre composición molar/volumétrica y composición másica.
* Relaciones estequiométricas de volúmenes gaseosos a igual T y P.
Criterio de cifras significativas
Los valores introducidos como texto conservan su información de cifras
significativas. Todos los dígitos escritos cuentan como significativos; si un
entero termina en cero y se desea indicar menos cifras, use notación científica
(p. ej., 3e2 en lugar de 300). Por defecto, los resultados de productos, cocientes y funciones
se presentan con el menor número de cifras significativas de los datos medidos
que intervienen. Las conversiones exactas y las constantes definidas no limitan
las cifras. Puede forzarse la salida con --sigfigs N.
Unidades internas
P: Pa; V: m³; n: mol; T: K; masa: kg. Se aceptan varias unidades de entrada.
La presión empleada en las ecuaciones de gases debe ser absoluta.
Sin argumentos abre un menú interactivo.
Con argumentos, use por ejemplo:
Autoría: material complementario del manual del usuario.
```

## 8. Ayuda real de línea de comandos

La salida siguiente fue obtenida al ejecutar `--help` sobre este archivo, no deducida de la documentación del libro:

```text
usage: gases_ideales_y_mezclas.py [-h] [--sigfigs SIGFIGS]
                                  {estado,densidad,mezcla,combinada,inventario,cinetica,presion-absoluta,volumenes-reaccion,lista-gases,ayuda} ...

Cálculos de gases ideales y mezclas. Sin argumentos abre menú interactivo.

positional arguments:
  {estado,densidad,mezcla,combinada,inventario,cinetica,presion-absoluta,volumenes-reaccion,lista-gases,ayuda}
    estado              Resuelve PV=nRT; omita exactamente una variable.
    densidad            Calcula densidad ideal y GE.
    mezcla              Analiza una mezcla ideal.
    combinada           Ley combinada P1V1/T1=P2V2/T2; omita una variable.
    inventario          Cantidad de sustancia y masa en un recipiente ideal.
    cinetica            Energía cinética media y velocidad cuadrática media.
    presion-absoluta    Convierte presión manométrica en absoluta.
    volumenes-reaccion  Relaciones de volúmenes gaseosos a igual T y P.
    lista-gases         Muestra las masas molares incorporadas.
    ayuda               Muestra ayuda conceptual.

options:
  -h, --help            show this help message and exit
  --sigfigs SIGFIGS     Fuerza N cifras significativas en la salida.
```

## 9. Subcomandos disponibles

Cada subcomando dispone de ayuda propia con `python gases_ideales_y_mezclas.py SUBCOMANDO --help`. Se reproducen las opciones efectivamente declaradas:

### `estado`

```text
usage: gases_ideales_y_mezclas.py estado [-h] [--P P] [--V V] [--n N] [--T T]
                                         [--P-unit P_UNIT] [--V-unit V_UNIT]
                                         [--n-unit N_UNIT] [--T-unit T_UNIT]

options:
  -h, --help       show this help message and exit
  --P P
  --V V
  --n N
  --T T
  --P-unit P_UNIT
  --V-unit V_UNIT
  --n-unit N_UNIT
  --T-unit T_UNIT
```

### `densidad`

```text
usage: gases_ideales_y_mezclas.py densidad [-h] --P P [--P-unit P_UNIT] --T T
                                           [--T-unit T_UNIT] [--gas GAS]
                                           [--M M]

options:
  -h, --help       show this help message and exit
  --P P
  --P-unit P_UNIT
  --T T
  --T-unit T_UNIT
  --gas GAS
  --M M
```

### `mezcla`

```text
usage: gases_ideales_y_mezclas.py mezcla [-h] --componentes COMPONENTES
                                         [--base {molar,masa,presion}]
                                         [--masas-molares MASAS_MOLARES]
                                         [--P P] [--P-unit P_UNIT] [--T T]
                                         [--T-unit T_UNIT] [--V V]
                                         [--V-unit V_UNIT]

options:
  -h, --help            show this help message and exit
  --componentes COMPONENTES
                        Ej.: CO2:10;N2:90
  --base {molar,masa,presion}
  --masas-molares MASAS_MOLARES
                        Masas molares personalizadas en g/mol, ej.:
                        CCl4:153,82;X:50,0
  --P P
  --P-unit P_UNIT
  --T T
  --T-unit T_UNIT
  --V V
  --V-unit V_UNIT
```

### `combinada`

```text
usage: gases_ideales_y_mezclas.py combinada [-h] [--P1 P1] [--V1 V1] [--T1 T1]
                                            [--P2 P2] [--V2 V2] [--T2 T2]
                                            [--P-unit P_UNIT]
                                            [--V-unit V_UNIT]
                                            [--T-unit T_UNIT]

options:
  -h, --help       show this help message and exit
  --P1 P1
  --V1 V1
  --T1 T1
  --P2 P2
  --V2 V2
  --T2 T2
  --P-unit P_UNIT
  --V-unit V_UNIT
  --T-unit T_UNIT
```

### `inventario`

```text
usage: gases_ideales_y_mezclas.py inventario [-h] --P P [--P-unit P_UNIT]
                                             --T T [--T-unit T_UNIT] --V V
                                             [--V-unit V_UNIT] [--gas GAS]
                                             [--M M]

options:
  -h, --help       show this help message and exit
  --P P
  --P-unit P_UNIT
  --T T
  --T-unit T_UNIT
  --V V
  --V-unit V_UNIT
  --gas GAS
  --M M
```

### `cinetica`

```text
usage: gases_ideales_y_mezclas.py cinetica [-h] --T T [--T-unit T_UNIT]
                                           [--gas GAS] [--M M]

options:
  -h, --help       show this help message and exit
  --T T
  --T-unit T_UNIT
  --gas GAS
  --M M
```

### `presion-absoluta`

```text
usage: gases_ideales_y_mezclas.py presion-absoluta [-h] --Pman PMAN
                                                   [--Patm PATM]
                                                   [--P-unit P_UNIT]
                                                   [--Patm-unit PATM_UNIT]

options:
  -h, --help            show this help message and exit
  --Pman PMAN
  --Patm PATM
  --P-unit P_UNIT
  --Patm-unit PATM_UNIT
```

### `volumenes-reaccion`

```text
usage: gases_ideales_y_mezclas.py volumenes-reaccion [-h] --especies ESPECIES
                                                     --coeficientes COEFICIENTES
                                                     --referencia REFERENCIA
                                                     --V V [--V-unit V_UNIT]

options:
  -h, --help            show this help message and exit
  --especies ESPECIES   Ej.: N2;H2;NH3
  --coeficientes COEFICIENTES
                        Ej.: 1;3;2
  --referencia REFERENCIA
                        Índice 1..N de la especie de referencia
  --V V
  --V-unit V_UNIT
```

### `lista-gases`

```text
usage: gases_ideales_y_mezclas.py lista-gases [-h]

options:
  -h, --help  show this help message and exit
```

### `ayuda`

```text
usage: gases_ideales_y_mezclas.py ayuda [-h]

options:
  -h, --help  show this help message and exit
```

## 10. Errores frecuentes y precauciones

- Ejecutar el archivo desde otra carpeta y no encontrar módulos auxiliares, tablas, ejemplos o rutas relativas.

- Mezclar unidades o bases de composición, o confundir fracciones con porcentajes.

- Utilizar ecuaciones o correlaciones fuera del intervalo para el que están previstas.

- Interpretar la precisión mostrada como una garantía experimental o física.

- Dar por único un problema con datos insuficientes o hipótesis no justificadas.

## 11. Estado de revisión

Inicio y ayuda revisados; no se ha ejecutado una batería de casos numéricos exhaustiva para esta aplicación.

## 12. Correspondencia bibliográfica

Programa de apoyo al **capítulo 4** de *Estequiometría y cálculos químicos*. El texto del libro es una exposición científica; este manual explica la ejecución del software suministrado. El código y el manual se distribuyen bajo licencia MIT; DOI general del software: [10.5281/zenodo.24020474](https://doi.org/10.5281/zenodo.24020474). DOI de la versión publicada 0.9.0: [10.5281/zenodo.24020473](https://doi.org/10.5281/zenodo.24020473). DOI del libro: [10.5281/zenodo.24013068](https://doi.org/10.5281/zenodo.24013068).


## Comprobación independiente de revisión integral

Caso de referencia: **P = nRT/V con n = 1 mol, T = 300 K y V = 0,025 m³**. Comprobación de la ecuación de estado ideal.

La prueba reproducible figura en `pruebas_revision/test_auditoria_integral.py`; los invariantes adicionales, cuando corresponden, están en `pruebas_revision/test_invariantes_cientificos.py`. Se trata de comprobaciones de casos seleccionados, no de una verificación exhaustiva del dominio del modelo.
