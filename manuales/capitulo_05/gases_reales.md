# Propiedades de los gases reales

**Manual de usuario · Capítulo 5 · gases_reales.py**  
**Proyecto:** *Estequiometría y cálculos químicos*. **Estado:** documentación preliminar basada en el código recibido (6 de noviembre de 2026).

## 1. Finalidad y funciones

Cálculos y comparaciones de ecuaciones de estado reales, factores de compresibilidad, saturación e idealidad.

Esta herramienta automatiza el cálculo y ayuda a verificarlo, pero no sustituye la selección del modelo químico ni la interpretación de sus hipótesis.

## 2. Requisitos e instalación

Se recomienda **Python 3.10 o posterior**. En Windows, abra PowerShell o Símbolo del sistema, entre en la carpeta del capítulo y ejecute la aplicación. Ejemplo desde la carpeta raíz del repositorio:

```bat
cd capitulo_05
python gases_reales.py
```

**Gráficos:** requieren `matplotlib` (instalable con `python -m pip install matplotlib`). Los cálculos no gráficos pueden tener menos dependencias.

## 3. Comandos y opciones de ejecución

**Iniciar con menú o con preguntas sucesivas:**

```bat
python gases_reales.py
```

**Consultar las opciones admitidas:**

```bat
python gases_reales.py --help
```

**Ejemplo de uso o comprobación del propio programa:**

```bat
python gases_reales.py --help
```

## 4. Menú principal y modos de cálculo

El menú mostrado por el programa, capturado durante esta revisión, ofrece las siguientes opciones:

```text
1. Estado con una ecuación/modelo
2. Comparar ideal, vdW, RK, SRK, PR y Lee-Kesler
3. Evaluar si puede usarse gas ideal
4. Presión de saturación por fugacidad (vdW/RK/SRK/PR)
5. Inventario de un recipiente
6. Ecuación virial
7. Lista de gases
8. Ayuda científica
9. Información sobre BWR
0. Salir
```

## 5. Datos introducidos y unidades

Se requieren propiedades críticas y, en ciertos modelos, el factor acéntrico; verifique las regiones de validez.

Algunos de los campos, selecciones o preguntas definidos explícitamente en el código son:

- `T / K:`
- `P / bar:`
- `Opción:`
- `B' / bar^-1 [0]:`
- `C' / bar^-2 [0]:`
- `D' / bar^-3 [0]:`
- `B / (L mol^-1) [0]:`
- `C / (L^2 mol^-2) [0]:`
- `D / (L^3 mol^-3) [0]:`
- `Gas (clave, fórmula o nombre):`
- `P absoluta:`
- `Forma [presion/volumen] (volumen):`
- `Unidad T [K]:`
- `Unidad P [bar]:`
- `Fase [vapor/liquido/auto] (vapor):`
- `Error relativo máximo admisible (%):`
- `Fase [vapor/liquido] (vapor):`
- `Modelo [ideal/vdw/rk/srk/pr/lk] (pr):`
- `Magnitud [n=cantidad/masa/densidad, v=volumen] (n):`
- `PNG de la gráfica (vacío = no generar):`
- `Volumen del recipiente:`
- `Método de Z [vdw/rk/srk/pr/lk/comparar] (comparar):`
- `Unidad V [L]:`
- `Modelo [vdw/rk/srk/pr] (pr):`

## 6. Procedimiento recomendado paso a paso

1. Identifique en el capítulo el tipo de problema, las variables conocidas y las hipótesis necesarias.

2. Inicie el programa con `python gases_reales.py` desde la carpeta indicada.

3. Opción 1 para estado real; opción 2 para comparar modelos; opción 3 para evaluar la aproximación ideal.

4. Introduzca los datos conservando las unidades del programa y las cifras significativas correspondientes.

5. Revise las magnitudes calculadas y, cuando el modo lo permita, los residuos de balance, las composiciones y los avisos de validez.

6. Si el resultado es físicamente imposible, examine los datos y los supuestos antes de repetir el cálculo.

## 7. Resultados, verificaciones y alcance científico

Los resultados dependen de la modalidad elegida. Consulte el desarrollo técnico siguiente, extraído de la descripción que acompaña al código, para conocer el modelo que el autor ha implementado y sus limitaciones.

```text
Herramienta de cálculo para el capítulo 5 «Propiedades de los gases reales».
Incluye
* Variables reducidas Tr y Pr.
* Gas ideal como referencia.
* Ecuaciones cúbicas: van der Waals, Redlich-Kwong (RK),
  Soave-Redlich-Kwong (SRK) y Peng-Robinson (PR).
* Cálculo y clasificación de todas las raíces reales físicamente admisibles.
* Coeficientes de fugacidad de sustancia pura para vdW, RK, SRK y PR.
* Presión de saturación predicha por una ecuación cúbica imponiendo fL = fV.
* Correlación de Lee-Kesler: Z(0), Z(r), Z(1) y Z.
* Ecuación virial truncada, en presión o en volumen molar.
* Comparación de modelos para un mismo estado.
* Inventario de un recipiente: n, masa, volumen molar y densidad.
* Evaluación cuantitativa de si el gas ideal satisface un error máximo admisible.
* Gráfica opcional del criterio de idealidad empleado en el capítulo.
Criterio de idealidad
Si se calcula cantidad de sustancia, masa o densidad a P,V,T fijados:
    epsilon = |Z - 1|
Si se calcula volumen o volumen molar a P,T,n fijados:
    epsilon = |1 - Z| / Z
La decisión depende del error máximo que indique el usuario; no se usa un
simple umbral universal de presión.
Cifras significativas
Las entradas se leen como texto (se admite coma decimal) y se conserva su
número de cifras significativas. Salvo --sigfigs N, la salida usa un criterio
conservador basado en los datos introducidos y en la precisión de las
propiedades críticas incorporadas. Los cálculos internos nunca se redondean.
Base de datos
Tc, Pc, Vmc y omega reproducen la tabla 5.2 del capítulo para 19 sustancias.
Las ecuaciones cúbicas calculan sus propios parámetros a partir de Tc y Pc.
BWR no se usa como calculadora universal porque requiere coeficientes ajustados
experimentalmente que no proporciona la tabla; el programa explica esta
limitación mediante la opción bwr-info.
Sin argumentos abre un menú interactivo.
```

## 8. Ayuda real de línea de comandos

La salida siguiente fue obtenida al ejecutar `--help` sobre este archivo, no deducida de la documentación del libro:

```text
usage: gases_reales.py [-h] [--sigfigs SIGFIGS]
                       {estado,comparar,lee-kesler,idealidad,saturacion,inventario,virial,lista-gases,ayuda,bwr-info} ...

Cálculos de gases reales. Sin argumentos abre menú interactivo.

positional arguments:
  {estado,comparar,lee-kesler,idealidad,saturacion,inventario,virial,lista-gases,ayuda,bwr-info}
    estado              Calcula Z, Vm, densidad, raíces y fugacidad.
    comparar            Compara todos los modelos disponibles para un estado.
    lee-kesler          Muestra Z(0), Z(r), Z(1) y Z.
    idealidad           Decide si gas ideal cumple el error máximo indicado.
    saturacion          Calcula P* imponiendo igualdad de fugacidades.
    inventario          Calcula cantidad y masa en un recipiente.
    virial              Ecuación virial truncada.
    lista-gases         Muestra la tabla de sustancias incorporadas.
    ayuda               Ayuda científica y criterios.
    bwr-info            Explica por qué BWR no se parametriza automáticamente.

options:
  -h, --help            show this help message and exit
  --sigfigs SIGFIGS     Fuerza N cifras significativas en la salida.
```

## 9. Subcomandos disponibles

Cada subcomando dispone de ayuda propia con `python gases_reales.py SUBCOMANDO --help`. Se reproducen las opciones efectivamente declaradas:

### `estado`

```text
usage: gases_reales.py estado [-h] --gas GAS --T T [--T-unit T_UNIT] --P P
                              [--P-unit P_UNIT] [--Tc TC] [--Pc PC]
                              [--omega OMEGA] [--M M]
                              [--modelo {ideal,vdw,rk,srk,pr,lk}]
                              [--fase {vapor,liquido,auto}]

options:
  -h, --help            show this help message and exit
  --gas GAS
  --T T
  --T-unit T_UNIT
  --P P
  --P-unit P_UNIT
  --Tc TC               Temperatura crítica personalizada, K
  --Pc PC               Presión crítica personalizada, bar
  --omega OMEGA         Factor acéntrico personalizado
  --M M                 Masa molar personalizada, g/mol
  --modelo {ideal,vdw,rk,srk,pr,lk}
  --fase {vapor,liquido,auto}
```

### `comparar`

```text
usage: gases_reales.py comparar [-h] --gas GAS --T T [--T-unit T_UNIT] --P P
                                [--P-unit P_UNIT] [--Tc TC] [--Pc PC]
                                [--omega OMEGA] [--M M]
                                [--fase {vapor,liquido}]

options:
  -h, --help            show this help message and exit
  --gas GAS
  --T T
  --T-unit T_UNIT
  --P P
  --P-unit P_UNIT
  --Tc TC               Temperatura crítica personalizada, K
  --Pc PC               Presión crítica personalizada, bar
  --omega OMEGA         Factor acéntrico personalizado
  --M M                 Masa molar personalizada, g/mol
  --fase {vapor,liquido}
```

### `lee-kesler`

```text
usage: gases_reales.py lee-kesler [-h] --gas GAS --T T [--T-unit T_UNIT] --P P
                                  [--P-unit P_UNIT] [--Tc TC] [--Pc PC]
                                  [--omega OMEGA] [--M M]
                                  [--fase {vapor,liquido}]

options:
  -h, --help            show this help message and exit
  --gas GAS
  --T T
  --T-unit T_UNIT
  --P P
  --P-unit P_UNIT
  --Tc TC               Temperatura crítica personalizada, K
  --Pc PC               Presión crítica personalizada, bar
  --omega OMEGA         Factor acéntrico personalizado
  --M M                 Masa molar personalizada, g/mol
  --fase {vapor,liquido}
```

### `idealidad`

```text
usage: gases_reales.py idealidad [-h] --gas GAS --T T [--T-unit T_UNIT] --P P
                                 [--P-unit P_UNIT] [--Tc TC] [--Pc PC]
                                 [--omega OMEGA] [--M M] --error ERROR
                                 [--magnitud {n,v}]
                                 [--metodo {vdw,rk,srk,pr,lk,comparar,z}]
                                 [--z Z] [--fase {vapor,liquido}]
                                 [--grafica GRAFICA]

options:
  -h, --help            show this help message and exit
  --gas GAS
  --T T
  --T-unit T_UNIT
  --P P
  --P-unit P_UNIT
  --Tc TC               Temperatura crítica personalizada, K
  --Pc PC               Presión crítica personalizada, bar
  --omega OMEGA         Factor acéntrico personalizado
  --M M                 Masa molar personalizada, g/mol
  --error ERROR         Error máximo admisible, en %
  --magnitud {n,v}      n: cantidad/masa/densidad; v: volumen/volumen molar
  --metodo {vdw,rk,srk,pr,lk,comparar,z}
  --z Z                 Z introducido por el usuario si --metodo z
  --fase {vapor,liquido}
  --grafica GRAFICA     Ruta PNG opcional para la gráfica del criterio.
```

### `saturacion`

```text
usage: gases_reales.py saturacion [-h] --gas GAS --T T [--T-unit T_UNIT]
                                  [--modelo {vdw,rk,srk,pr}] [--Tc TC]
                                  [--Pc PC] [--omega OMEGA] [--M M]

options:
  -h, --help            show this help message and exit
  --gas GAS
  --T T
  --T-unit T_UNIT
  --modelo {vdw,rk,srk,pr}
  --Tc TC               Temperatura crítica personalizada, K
  --Pc PC               Presión crítica personalizada, bar
  --omega OMEGA         Factor acéntrico personalizado
  --M M                 Masa molar personalizada, g/mol
```

### `inventario`

```text
usage: gases_reales.py inventario [-h] --gas GAS --T T [--T-unit T_UNIT] --P P
                                  [--P-unit P_UNIT] [--Tc TC] [--Pc PC]
                                  [--omega OMEGA] [--M M] --V V
                                  [--V-unit V_UNIT]
                                  [--modelo {ideal,vdw,rk,srk,pr,lk}]
                                  [--fase {vapor,liquido}]

options:
  -h, --help            show this help message and exit
  --gas GAS
  --T T
  --T-unit T_UNIT
  --P P
  --P-unit P_UNIT
  --Tc TC               Temperatura crítica personalizada, K
  --Pc PC               Presión crítica personalizada, bar
  --omega OMEGA         Factor acéntrico personalizado
  --M M                 Masa molar personalizada, g/mol
  --V V
  --V-unit V_UNIT
  --modelo {ideal,vdw,rk,srk,pr,lk}
  --fase {vapor,liquido}
```

### `virial`

```text
usage: gases_reales.py virial [-h] [--forma {volumen,presion}] --T T --P P
                              [--B B] [--C C] [--D D]

options:
  -h, --help            show this help message and exit
  --forma {volumen,presion}
  --T T
  --P P                 bar
  --B B
  --C C
  --D D
```

### `lista-gases`

```text
usage: gases_reales.py lista-gases [-h]

options:
  -h, --help  show this help message and exit
```

### `ayuda`

```text
usage: gases_reales.py ayuda [-h]

options:
  -h, --help  show this help message and exit
```

### `bwr-info`

```text
usage: gases_reales.py bwr-info [-h]

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

Programa de apoyo al **capítulo 5** de *Estequiometría y cálculos químicos*. El texto del libro es una exposición científica; este manual explica la ejecución del software suministrado. El código y el manual se distribuyen bajo licencia MIT; el DOI específico del software se incorporará tras la primera publicación en Zenodo.
