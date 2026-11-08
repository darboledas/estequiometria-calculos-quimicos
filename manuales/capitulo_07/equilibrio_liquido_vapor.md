# Equilibrio líquido–vapor ideal

**Manual de usuario · Capítulo 7 · equilibrio_liquido_vapor.py**  
**Proyecto:** *Estequiometría y cálculos químicos*. **Estado:** documentación preliminar basada en el código recibido (6 de noviembre de 2026).

## 1. Finalidad y funciones

Raoult, puntos de burbuja y rocío, coeficientes K, volatilidad relativa y diagramas binarios.

Esta herramienta automatiza el cálculo y ayuda a verificarlo, pero no sustituye la selección del modelo químico ni la interpretación de sus hipótesis.

## 2. Requisitos e instalación

Se recomienda **Python 3.10 o posterior**. En Windows, abra PowerShell o Símbolo del sistema, entre en la carpeta del capítulo y ejecute la aplicación. Ejemplo desde la carpeta raíz del repositorio:

```bat
cd capitulo_07
python equilibrio_liquido_vapor.py
```

**Gráficos:** requieren `matplotlib` (instalable con `python -m pip install matplotlib`). Para generar diagramas se usa también `numpy`. Los cálculos no gráficos pueden tener menos dependencias.

## 3. Comandos y opciones de ejecución

**Iniciar con menú o con preguntas sucesivas:**

```bat
python equilibrio_liquido_vapor.py
```

**Consultar las opciones admitidas:**

```bat
python equilibrio_liquido_vapor.py --help
```

**Ejemplo de uso o comprobación del propio programa:**

```bat
python equilibrio_liquido_vapor.py --help
```

## 4. Menú principal y modos de cálculo

El menú mostrado por el programa, capturado durante esta revisión, ofrece las siguientes opciones:

```text
1. Ley de Raoult
2. Presión de burbuja a T conocida
3. Temperatura de burbuja a P conocida
4. Presión de rocío a T conocida
5. Temperatura de rocío a P conocida
6. Coeficiente K y volatilidad relativa
7. Diagrama P-x-y (binario)
8. Diagrama T-x-y (binario)
9. Diagrama y-x (binario)
10. Cálculos con P_i* conocidas (sin Antoine)
11. Diagramas T-x-y e y-x desde tabla P_i*(T)
0. Salir
```

## 5. Datos introducidos y unidades

La fase líquida y la fase vapor se suponen ideales; Antoine usa T en K y P* en kPa.

Algunos de los campos, selecciones o preguntas definidos explícitamente en el código son:

- `Número de componentes:`
- `Opción:`
- `P total constante (kPa):`
- `Número de filas de la tabla:`
- `Nombre del componente 1:`
- `Nombre del componente 2:`
- `T (K) =`
- `PNG T-x-y [diagrama_Txy_tabla.png]:`
- `PNG y-x [diagrama_yx_tabla.png]:`
- `Tmin (K) =`
- `Tmax (K) =`
- `P total (kPa):`
- `T (K):`
- `Nombre del PNG [diagrama_Pxy.png]:`
- `P (kPa):`
- `Nombre del PNG [diagrama_yx.png]:`
- `Índice del componente i para α_ij (1..N):`
- `Índice del componente j para α_ij (1..N):`
- `Nombre del PNG [diagrama_Txy.png]:`
- `Condición fija: [P]resión o [T]emperatura?`

## 6. Procedimiento recomendado paso a paso

1. Identifique en el capítulo el tipo de problema, las variables conocidas y las hipótesis necesarias.

2. Inicie el programa con `python equilibrio_liquido_vapor.py` desde la carpeta indicada.

3. Opción 2 para presión de burbuja o 3 para temperatura de burbuja; 7–9 para diagramas.

4. Introduzca los datos conservando las unidades del programa y las cifras significativas correspondientes.

5. Revise las magnitudes calculadas y, cuando el modo lo permita, los residuos de balance, las composiciones y los avisos de validez.

6. Si el resultado es físicamente imposible, examine los datos y los supuestos antes de repetir el cálculo.

## 7. Resultados, verificaciones y alcance científico

Los resultados dependen de la modalidad elegida. Consulte el desarrollo técnico siguiente, extraído de la descripción que acompaña al código, para conocer el modelo que el autor ha implementado y sus limitaciones.

```text
Herramienta de cálculo para el capítulo 7: disoluciones ideales y equilibrio
líquido-vapor.
Incluye:
    1) Ley de Raoult para mezclas ideales multicomponentes.
    2) Presión de burbuja a temperatura conocida.
    3) Temperatura de burbuja a presión conocida.
    4) Presión de rocío a temperatura conocida.
    5) Temperatura de rocío a presión conocida.
    6) Coeficientes K_i y volatilidades relativas.
    7) Diagramas P-x-y para mezclas binarias.
    8) Diagramas T-x-y para mezclas binarias.
    9) Diagramas y-x para mezclas binarias.
    10) Cálculos directos cuando se conocen P_i* sin necesidad de Antoine.
    11) Diagramas T-x-y e y-x a partir de tablas de P_i*(T).
Hipótesis:
    - Fase líquida ideal: ley de Raoult.
    - Fase vapor ideal: ley de Dalton.
    - Presiones de vapor mediante Antoine cuando la temperatura es variable.
    - Antoine en la forma:
          log10(P_i*) = A_i - B_i / (T + C_i)
      con P_i* en kPa y T en K.
      Si una correlación aparece como T - c, introduzca C = -c.
Resolución numérica:
    - En modo automático se exige una raíz físicamente acotada.
    - Se intenta Newton salvaguardado.
    - Si una iteración sale del intervalo físico, la derivada no es adecuada,
      el residuo empeora o aparece una anomalía numérica, se usa bisección.
    - La convergencia exige simultáneamente tolerancia en la variable y en el
      residuo.
    - No se extrapolan de forma silenciosa las ecuaciones de Antoine fuera de
      su intervalo de validez.
Gráficos:
    - PNG.
    - Fondo transparente.
    - 600 ppp por defecto.
    - Arial, 10 pt.
    - Los diagramas P-x-y, T-x-y e y-x se limitan a sistemas binarios.
Entrada decimal:
    - Se aceptan coma o punto decimal en el modo interactivo y en los valores
      individuales de línea de comandos.
Salida:
    - Se usa coma decimal.
Dependencias:
    - Python >= 3.10
    - matplotlib y numpy solo para generar diagramas.
```

## 8. Ayuda real de línea de comandos

La salida siguiente fue obtenida al ejecutar `--help` sobre este archivo, no deducida de la documentación del libro:

```text
usage: equilibrio_liquido_vapor.py [-h]
                                   {raoult,bubble-p,bubble-t,dew-p,dew-t,alpha,diagram-pxy,diagram-txy,diagram-yx,raoult-pstar,dew-p-pstar,state-pstar,diagram-pxy-pstar,diagram-yx-pstar,diagram-table} ...

Cálculo de equilibrio líquido-vapor ideal, puntos de burbuja y rocío y diagramas binarios del capítulo 7.

positional arguments:
  {raoult,bubble-p,bubble-t,dew-p,dew-t,alpha,diagram-pxy,diagram-txy,diagram-yx,raoult-pstar,dew-p-pstar,state-pstar,diagram-pxy-pstar,diagram-yx-pstar,diagram-table}
    raoult              Ley de Raoult a temperatura conocida.
    bubble-p            Presión de burbuja a T conocida.
    bubble-t            Temperatura de burbuja a P conocida.
    dew-p               Presión de rocío a T conocida.
    dew-t               Temperatura de rocío a P conocida.
    alpha               K_i y volatilidad relativa α_ij.
    diagram-pxy         Diagrama P-x-y binario.
    diagram-txy         Diagrama T-x-y binario.
    diagram-yx          Diagrama y-x binario.
    raoult-pstar        Ley de Raoult con P_i* introducidas directamente.
    dew-p-pstar         Presión de rocío con P_i* introducidas directamente.
    state-pstar         x_i e y_i binarias a P conocida usando P_1* y P_2*.
    diagram-pxy-pstar   Diagrama P-x-y binario a partir de P_1* y P_2*.
    diagram-yx-pstar    Diagrama y-x binario a partir de P_1* y P_2*.
    diagram-table       Genera T-x-y e y-x desde una tabla T;P_1*;P_2*.

options:
  -h, --help            show this help message and exit
```

## 9. Subcomandos disponibles

Cada subcomando dispone de ayuda propia con `python equilibrio_liquido_vapor.py SUBCOMANDO --help`. Se reproducen las opciones efectivamente declaradas:

### `raoult`

```text
usage: equilibrio_liquido_vapor.py raoult [-h] --component COMPONENT
                                          [--sig SIG] --x X --T T

options:
  -h, --help            show this help message and exit
  --component COMPONENT
                        Componente como 'NOMBRE;A;B;C' o
                        'NOMBRE;A;B;C;Tmin;Tmax'. Repetir una vez por
                        componente.
  --sig SIG             Cifras significativas mostradas (predeterminado: 5).
  --x X                 Fracción molar líquida.
  --T T                 Temperatura en K.
```

### `bubble-p`

```text
usage: equilibrio_liquido_vapor.py bubble-p [-h] --component COMPONENT
                                            [--sig SIG] --x X --T T

options:
  -h, --help            show this help message and exit
  --component COMPONENT
                        Componente como 'NOMBRE;A;B;C' o
                        'NOMBRE;A;B;C;Tmin;Tmax'. Repetir una vez por
                        componente.
  --sig SIG             Cifras significativas mostradas (predeterminado: 5).
  --x X
  --T T
```

### `bubble-t`

```text
usage: equilibrio_liquido_vapor.py bubble-t [-h] --component COMPONENT
                                            [--sig SIG]
                                            [--method {auto,bisection,secant,newton}]
                                            [--verbose] --x X --P P

options:
  -h, --help            show this help message and exit
  --component COMPONENT
                        Componente como 'NOMBRE;A;B;C' o
                        'NOMBRE;A;B;C;Tmin;Tmax'. Repetir una vez por
                        componente.
  --sig SIG             Cifras significativas mostradas (predeterminado: 5).
  --method {auto,bisection,secant,newton}
                        Método numérico; 'auto' usa estrategia salvaguardada.
  --verbose             Muestra método interno, iteraciones y pasos de
                        respaldo.
  --x X
  --P P                 Presión total en kPa.

Para cálculos iterativos de temperatura se recomienda especificar Tmin y Tmax
para cada correlación de Antoine.
```

### `dew-p`

```text
usage: equilibrio_liquido_vapor.py dew-p [-h] --component COMPONENT
                                         [--sig SIG] --y Y --T T

options:
  -h, --help            show this help message and exit
  --component COMPONENT
                        Componente como 'NOMBRE;A;B;C' o
                        'NOMBRE;A;B;C;Tmin;Tmax'. Repetir una vez por
                        componente.
  --sig SIG             Cifras significativas mostradas (predeterminado: 5).
  --y Y
  --T T
```

### `dew-t`

```text
usage: equilibrio_liquido_vapor.py dew-t [-h] --component COMPONENT
                                         [--sig SIG]
                                         [--method {auto,bisection,secant,newton}]
                                         [--verbose] --y Y --P P

options:
  -h, --help            show this help message and exit
  --component COMPONENT
                        Componente como 'NOMBRE;A;B;C' o
                        'NOMBRE;A;B;C;Tmin;Tmax'. Repetir una vez por
                        componente.
  --sig SIG             Cifras significativas mostradas (predeterminado: 5).
  --method {auto,bisection,secant,newton}
                        Método numérico; 'auto' usa estrategia salvaguardada.
  --verbose             Muestra método interno, iteraciones y pasos de
                        respaldo.
  --y Y
  --P P

Para cálculos iterativos de temperatura se recomienda especificar Tmin y Tmax
para cada correlación de Antoine.
```

### `alpha`

```text
usage: equilibrio_liquido_vapor.py alpha [-h] --component COMPONENT
                                         [--sig SIG] --T T --P P --i I --j J

options:
  -h, --help            show this help message and exit
  --component COMPONENT
                        Componente como 'NOMBRE;A;B;C' o
                        'NOMBRE;A;B;C;Tmin;Tmax'. Repetir una vez por
                        componente.
  --sig SIG             Cifras significativas mostradas (predeterminado: 5).
  --T T
  --P P
  --i I                 Índice i, comenzando en 1.
  --j J                 Índice j, comenzando en 1.
```

### `diagram-pxy`

```text
usage: equilibrio_liquido_vapor.py diagram-pxy [-h] --component COMPONENT
                                               [--sig SIG] --T T
                                               [--output OUTPUT] [--dpi DPI]
                                               [--points POINTS]

options:
  -h, --help            show this help message and exit
  --component COMPONENT
                        Componente como 'NOMBRE;A;B;C' o
                        'NOMBRE;A;B;C;Tmin;Tmax'. Repetir una vez por
                        componente.
  --sig SIG             Cifras significativas mostradas (predeterminado: 5).
  --T T
  --output OUTPUT
  --dpi DPI
  --points POINTS
```

### `diagram-txy`

```text
usage: equilibrio_liquido_vapor.py diagram-txy [-h] --component COMPONENT
                                               [--sig SIG]
                                               [--method {auto,bisection,secant,newton}]
                                               [--verbose] --P P
                                               [--output OUTPUT] [--dpi DPI]
                                               [--points POINTS]

options:
  -h, --help            show this help message and exit
  --component COMPONENT
                        Componente como 'NOMBRE;A;B;C' o
                        'NOMBRE;A;B;C;Tmin;Tmax'. Repetir una vez por
                        componente.
  --sig SIG             Cifras significativas mostradas (predeterminado: 5).
  --method {auto,bisection,secant,newton}
                        Método numérico; 'auto' usa estrategia salvaguardada.
  --verbose             Muestra método interno, iteraciones y pasos de
                        respaldo.
  --P P
  --output OUTPUT
  --dpi DPI
  --points POINTS

Para cálculos iterativos de temperatura se recomienda especificar Tmin y Tmax
para cada correlación de Antoine.
```

### `diagram-yx`

```text
usage: equilibrio_liquido_vapor.py diagram-yx [-h] --component COMPONENT
                                              [--sig SIG]
                                              [--method {auto,bisection,secant,newton}]
                                              [--verbose] (--P P | --T T)
                                              [--output OUTPUT] [--dpi DPI]
                                              [--points POINTS]

options:
  -h, --help            show this help message and exit
  --component COMPONENT
                        Componente como 'NOMBRE;A;B;C' o
                        'NOMBRE;A;B;C;Tmin;Tmax'. Repetir una vez por
                        componente.
  --sig SIG             Cifras significativas mostradas (predeterminado: 5).
  --method {auto,bisection,secant,newton}
                        Método numérico; 'auto' usa estrategia salvaguardada.
  --verbose             Muestra método interno, iteraciones y pasos de
                        respaldo.
  --P P                 Presión constante en kPa.
  --T T                 Temperatura constante en K.
  --output OUTPUT
  --dpi DPI
  --points POINTS

Para cálculos iterativos de temperatura se recomienda especificar Tmin y Tmax
para cada correlación de Antoine.
```

### `raoult-pstar`

```text
usage: equilibrio_liquido_vapor.py raoult-pstar [-h] --pstar PSTAR
                                                [--name NAME] --x X
                                                [--sig SIG]

options:
  -h, --help     show this help message and exit
  --pstar PSTAR  Presión de vapor P_i* en kPa; repetir una vez por componente.
  --name NAME    Nombre del componente; repetir en el mismo orden que --pstar.
  --x X
  --sig SIG
```

### `dew-p-pstar`

```text
usage: equilibrio_liquido_vapor.py dew-p-pstar [-h] --pstar PSTAR
                                               [--name NAME] --y Y [--sig SIG]

options:
  -h, --help     show this help message and exit
  --pstar PSTAR  Presión de vapor P_i* en kPa; repetir una vez por componente.
  --name NAME    Nombre del componente; repetir en el mismo orden que --pstar.
  --y Y
  --sig SIG
```

### `state-pstar`

```text
usage: equilibrio_liquido_vapor.py state-pstar [-h] --pstar PSTAR
                                               [--name NAME] [--sig SIG] --P P

options:
  -h, --help     show this help message and exit
  --pstar PSTAR  Presión de vapor P_i* en kPa; repetir una vez por componente.
  --name NAME    Nombre del componente; repetir en el mismo orden que --pstar.
  --sig SIG
  --P P          Presión total en kPa.
```

### `diagram-pxy-pstar`

```text
usage: equilibrio_liquido_vapor.py diagram-pxy-pstar [-h] --pstar PSTAR
                                                     [--name NAME] [--sig SIG]
                                                     [--output OUTPUT]
                                                     [--dpi DPI]
                                                     [--points POINTS]

options:
  -h, --help       show this help message and exit
  --pstar PSTAR    Presión de vapor P_i* en kPa; repetir una vez por
                   componente.
  --name NAME      Nombre del componente; repetir en el mismo orden que
                   --pstar.
  --sig SIG
  --output OUTPUT
  --dpi DPI
  --points POINTS
```

### `diagram-yx-pstar`

```text
usage: equilibrio_liquido_vapor.py diagram-yx-pstar [-h] --pstar PSTAR
                                                    [--name NAME] [--sig SIG]
                                                    [--output OUTPUT]
                                                    [--dpi DPI]
                                                    [--points POINTS]

options:
  -h, --help       show this help message and exit
  --pstar PSTAR    Presión de vapor P_i* en kPa; repetir una vez por
                   componente.
  --name NAME      Nombre del componente; repetir en el mismo orden que
                   --pstar.
  --sig SIG
  --output OUTPUT
  --dpi DPI
  --points POINTS
```

### `diagram-table`

```text
usage: equilibrio_liquido_vapor.py diagram-table [-h] --name NAME --P P
                                                 --row ROW
                                                 [--output-txy OUTPUT_TXY]
                                                 [--output-yx OUTPUT_YX]
                                                 [--dpi DPI] [--sig SIG]

options:
  -h, --help            show this help message and exit
  --name NAME           Dos nombres de componentes.
  --P P                 Presión total constante, kPa.
  --row ROW             Fila 'T;P1*;P2*'; repetir para cada temperatura.
  --output-txy OUTPUT_TXY
  --output-yx OUTPUT_YX
  --dpi DPI
  --sig SIG
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

Programa de apoyo al **capítulo 7** de *Estequiometría y cálculos químicos*. El texto del libro es una exposición científica; este manual explica la ejecución del software suministrado. El código y el manual se distribuyen bajo licencia MIT; DOI general del software: [10.5281/zenodo.24020474](https://doi.org/10.5281/zenodo.24020474). DOI de la versión publicada 0.9.0: [10.5281/zenodo.24020473](https://doi.org/10.5281/zenodo.24020473). DOI del libro: [10.5281/zenodo.24013068](https://doi.org/10.5281/zenodo.24013068).


## Comprobación independiente de revisión integral

Caso de referencia: **Raoult: x = (0,4; 0,6), P* = (80; 40) kPa ⇒ P = 56 kPa**. Comprobación de presión parcial y fracciones de vapor.

La prueba reproducible figura en `pruebas_revision/test_auditoria_integral.py`; los invariantes adicionales, cuando corresponden, están en `pruebas_revision/test_invariantes_cientificos.py`. Se trata de comprobaciones de casos seleccionados, no de una verificación exhaustiva del dominio del modelo.

### Nota de verificación científica adicional

Revisión adicional (7-11-2026): cuando la fracción molar de un componente es exactamente cero, no se requiere evaluar su presión de vapor si Antoine está fuera de su intervalo. El campo P_i* y el coeficiente K_i de esa especie ausente se indican con una raya (no disponible), nunca con un cero físico. Para mezclas con ambos componentes presentes se sigue exigiendo intersección de intervalos válidos. Se han contrastado 200 casos de reversibilidad T-burbuja/T-rocío.


## Nota de validación — Bloque IX (2026-11-07)

Se ha reforzado la comprobación de los datos en los objetos `Component` creados por código: los coeficientes A, B, C y los límites de temperatura deben ser finitos, la temperatura absoluta es positiva y la presión utilizada para invertir Antoine debe ser positiva y finita. Una presión `NaN` o infinita produce `ValueError` y no un resultado numérico aparente. Las entradas válidas de los ejercicios 7.B.10 (T_bur = 340,55835 K), 7.B.11 (fracción vaporizada β ≈ 0,51343) y 7.B.13 (β = 0,57898986) conservan sus resultados.

Comprobación: `python -m unittest discover -s pruebas_revision -p test_cotejo_bloque_09.py -v`.
