# Presión de vapor y correlaciones

**Manual de usuario · Capítulo 6 · presion_vapor.py**  
**Proyecto:** *Estequiometría y cálculos químicos*. **Estado:** documentación preliminar basada en el código recibido (6 de noviembre de 2026).

## 1. Finalidad y funciones

Antoine, Clausius–Clapeyron, sublimación, Lee–Kesler, interpolación, Dühring y gráficos.

Esta herramienta automatiza el cálculo y ayuda a verificarlo, pero no sustituye la selección del modelo químico ni la interpretación de sus hipótesis.

## 2. Requisitos e instalación

Se recomienda **Python 3.10 o posterior**. En Windows, abra PowerShell o Símbolo del sistema, entre en la carpeta del capítulo y ejecute la aplicación. Ejemplo desde la carpeta raíz del repositorio:

```bat
cd capitulo_06
python presion_vapor.py
```

**Gráficos:** requieren `matplotlib` (instalable con `python -m pip install matplotlib`). Los cálculos no gráficos pueden tener menos dependencias.

## 3. Comandos y opciones de ejecución

**Iniciar con menú o con preguntas sucesivas:**

```bat
python presion_vapor.py
```

**Consultar las opciones admitidas:**

```bat
python presion_vapor.py --help
```

**Ejemplo de uso o comprobación del propio programa:**

```bat
python presion_vapor.py antoine --sustancia agua --temperatura 350
```

## 4. Menú principal y modos de cálculo

El menú mostrado por el programa, capturado durante esta revisión, ofrece las siguientes opciones:

```text
1. Ecuación de Antoine
2. Clausius-Clapeyron: vaporización
3. Sublimación
4. Correlación de Lee-Kesler
5. Interpolación de presión de vapor
6. Línea de Dühring
7. Representaciones gráficas
8. Comparación de métodos
9. Mostrar sustancias de Antoine
0. Salir
```

## 5. Datos introducidos y unidades

Antoine se utiliza con coeficientes y rangos precisos; no extrapolar sin justificación.

Algunos de los campos, selecciones o preguntas definidos explícitamente en el código son:

- `Nombre o etiqueta de la sustancia`
- `B (K)`
- `C (K)`
- `Temperatura mínima de validez (K)`
- `Temperatura máxima de validez (K)`
- `Seleccione una opción`
- `Opción`
- `Unidad de presión de los datos (Pa/kPa/bar/atm/mmHg)`
- `Unidad de Pc (Pa/kPa/bar/atm/mmHg)`
- `Factor acéntrico ω`
- `Unidad de presión de salida`
- `Unidad de temperaturas (K/C)`
- `Unidad de presiones (Pa/kPa/bar/atm/mmHg)`
- `Número de pares experimentales`
- `Unidad de T_dis (K/C)`
- `Unidad de P_dis* (Pa/kPa/bar/atm/mmHg)`
- `¿Desea estimar P_dis* a otra temperatura?`
- `¿Desea generar la gráfica de Dühring?`
- `Sustancias separadas por comas`
- `Tipo de gráfica`
- `¿Usar automáticamente el intervalo común de Antoine?`
- `¿Dispone de un punto de referencia y ΔH_vap para Clausius-Clapeyron?`
- `¿Dispone de Tc, Pc y ω para Lee-Kesler?`
- `Temperatura`

La relación anterior es ilustrativa: ciertos campos solo aparecen al elegir subopciones.

## 6. Procedimiento recomendado paso a paso

1. Identifique en el capítulo el tipo de problema, las variables conocidas y las hipótesis necesarias.

2. Inicie el programa con `python presion_vapor.py` desde la carpeta indicada.

3. Elija opción 1 y una sustancia de la base interna, después elija calcular presión a partir de temperatura.

4. Introduzca los datos conservando las unidades del programa y las cifras significativas correspondientes.

5. Revise las magnitudes calculadas y, cuando el modo lo permita, los residuos de balance, las composiciones y los avisos de validez.

6. Si el resultado es físicamente imposible, examine los datos y los supuestos antes de repetir el cálculo.

## 7. Resultados, verificaciones y alcance científico

Los resultados dependen de la modalidad elegida. Consulte el desarrollo técnico siguiente, extraído de la descripción que acompaña al código, para conocer el modelo que el autor ha implementado y sus limitaciones.

```text
Herramienta didáctica para el capítulo 6 «Presión de vapor y equilibrio de fases»
del manual «Estequiometría y cálculos químicos».
FUNCIONALIDAD
El programa reúne en una sola aplicación los cálculos y representaciones más
habituales del capítulo:
1. Ecuación de Antoine
   - cálculo de presión de vapor P* a partir de T;
   - cálculo de T a partir de P*;
   - base interna de constantes de la Tabla 6.1;
   - introducción manual de A, B y C.
2. Ecuación integrada de Clausius-Clapeyron
   - cálculo de P2*;
   - cálculo de T2;
   - estimación de la entalpía molar de vaporización.
3. Sublimación
   - mismos tipos de cálculo que Clausius-Clapeyron, usando P_sub y
     Delta H_sub.
4. Correlación de Lee-Kesler
   - cálculo de Tr, Pr y P* a partir de Tc, Pc y factor acéntrico.
5. Interpolación de datos de presión de vapor
   - interpolación lineal directa de P* frente a T;
   - interpolación lineal de ln(P*) frente a 1/T;
   - comparación de ambos resultados.
6. Líneas de Dühring
   - construcción a partir de datos (T_dis, P_dis*);
   - conversión de P a temperatura equivalente de una sustancia de referencia;
   - ajuste lineal;
   - estimación de P_dis* a una T_dis dada;
   - gráfica opcional.
7. Representaciones gráficas
   - P* frente a T;
   - escala semilogarítmica P* frente a T;
   - ln(P*/kPa) frente a 1/T;
   - comparación entre sustancias;
   - exportación PNG a 300 ppp y fondo transparente.
8. Comparación de métodos
   - Antoine, Clausius-Clapeyron y Lee-Kesler cuando se proporcionan los
     datos necesarios.
HIPÓTESIS Y LIMITACIONES
- Antoine es una correlación empírica y solo debe utilizarse dentro del
  intervalo de validez de sus coeficientes. El programa bloquea por defecto
  la extrapolación, salvo autorización explícita.
- La forma integrada de Clausius-Clapeyron supone, entre otras aproximaciones,
  vapor ideal, volumen del líquido despreciable frente al del vapor y entalpía
  molar de cambio de fase aproximadamente constante en el intervalo.
- Lee-Kesler se usa aquí en la forma de presión de vapor del capítulo. No se
  permite Tr >= 1. Para Tr fuera de 0,3 < Tr < 1,0 se solicita autorización
  explícita porque se abandona el intervalo didáctico recomendado.
- Una línea de Dühring es una correlación aproximada válida para una composición
  y un intervalo limitados. No debe extrapolarse sin justificación.
UNIDADES
El programa acepta temperaturas en K o °C y presiones en Pa, kPa, bar, atm o
mmHg. Internamente se convierten a K y kPa. Los resultados se presentan con un
número configurable de cifras significativas (3 por defecto); los cálculos
internos no se redondean prematuramente.
REQUISITOS
- Python 3.9 o posterior.
- Solo para las gráficas: matplotlib.
Modo interactivo:
Ayuda:
Ejemplos de línea de comandos:
FUENTES DE LAS CORRELACIONES
- Antoine: constantes de la Tabla 6.1 del capítulo 6.
- Lee, B. I. & Kesler, M. G. (1975), AIChE Journal, 21(3), 510-527.
- La formulación de Clausius-Clapeyron, Dühring y las restantes expresiones se
  ajusta al desarrollo del capítulo 6.
Este programa es una herramienta docente. No sustituye bases de datos ni
correlaciones de referencia cuando se requiere alta precisión.
```

## 8. Ayuda real de línea de comandos

La salida siguiente fue obtenida al ejecutar `--help` sobre este archivo, no deducida de la documentación del libro:

```text
usage: presion_vapor.py [-h] [--cifras CIFRAS]
                        {antoine,clausius,sublimacion,lee-kesler,interpolar,duhring,grafica,listar} ...

Cálculos y gráficas de presión de vapor, equilibrio y correlaciones del capítulo 6.

positional arguments:
  {antoine,clausius,sublimacion,lee-kesler,interpolar,duhring,grafica,listar}
    antoine             Calcular P* o T mediante Antoine.
    clausius            Clausius-Clapeyron integrada para vaporización.
    sublimacion         Clausius-Clapeyron integrada para sublimación.
    lee-kesler          Presión de vapor mediante Lee-Kesler.
    interpolar          Comparar interpolación P-T y ln(P)-1/T.
    duhring             Construir y usar una línea de Dühring.
    grafica             Generar curvas de Antoine.
    listar              Mostrar la base interna de constantes de Antoine.

options:
  -h, --help            show this help message and exit
  --cifras CIFRAS       Cifras significativas de los resultados (por defecto:
                        3).

Ejemplos:
  python presion_vapor.py
  python presion_vapor.py antoine --sustancia agua --temperatura 350
  python presion_vapor.py antoine --sustancia agua --presion 50
  python presion_vapor.py clausius --p1 25 --t1 273 --t2 298 --dh 28.5
  python presion_vapor.py lee-kesler --t 350 --tc 540.2 --pc 27.4 --pc-unidad bar --omega 0.349
  python presion_vapor.py interpolar --t1 320 --p1 12 --t2 340 --p2 28.5 --t 330
  python presion_vapor.py grafica --sustancias agua,etanol,tolueno --tipo semilog --tmin 280 --tmax 369 --salida presiones.png
```

## 9. Subcomandos disponibles

Cada subcomando dispone de ayuda propia con `python presion_vapor.py SUBCOMANDO --help`. Se reproducen las opciones efectivamente declaradas:

### `antoine`

```text
usage: presion_vapor.py antoine [-h] [--cifras CIFRAS] --sustancia SUSTANCIA
                                (--temperatura TEMPERATURA |
                                --presion PRESION) [--t-unidad {K,C}]
                                [--p-unidad {Pa,kPa,bar,atm,mmHg}]
                                [--permitir-extrapolacion]

options:
  -h, --help            show this help message and exit
  --cifras CIFRAS       Cifras significativas de los resultados.
  --sustancia SUSTANCIA
                        Nombre de una sustancia de la base interna.
  --temperatura TEMPERATURA
                        Temperatura para calcular P*.
  --presion PRESION     Presión para calcular T.
  --t-unidad {K,C}      Unidad de temperatura.
  --p-unidad {Pa,kPa,bar,atm,mmHg}
                        Unidad de presión.
  --permitir-extrapolacion
                        Permitir el uso fuera del intervalo de Antoine.
```

### `clausius`

```text
usage: presion_vapor.py clausius [-h] [--cifras CIFRAS] --p1 P1 --t1 T1
                                 [--t2 T2] [--p2 P2] [--dh DH]
                                 [--dh-unidad DH_UNIDAD]
                                 [--masa-molar MASA_MOLAR]
                                 [--p-unidad {Pa,kPa,bar,atm,mmHg}]
                                 [--t-unidad {K,C}]

options:
  -h, --help            show this help message and exit
  --cifras CIFRAS       Cifras significativas de los resultados.
  --p1 P1
  --t1 T1
  --t2 T2               Segunda temperatura. Con --dh calcula P2; con --p2 y
                        sin --dh permite estimar ΔH.
  --p2 P2               Segunda presión. Con --dh calcula T2; con --t2 y sin
                        --dh permite estimar ΔH.
  --dh DH               Entalpía de vaporización.
  --dh-unidad DH_UNIDAD
                        J/mol, kJ/mol, J/kg o kJ/kg.
  --masa-molar MASA_MOLAR
                        g/mol, necesaria si ΔH se da por kg.
  --p-unidad {Pa,kPa,bar,atm,mmHg}
  --t-unidad {K,C}
```

### `sublimacion`

```text
usage: presion_vapor.py sublimacion [-h] [--cifras CIFRAS] --p1 P1 --t1 T1
                                    [--t2 T2] [--p2 P2] [--dh DH]
                                    [--dh-unidad DH_UNIDAD]
                                    [--masa-molar MASA_MOLAR]
                                    [--p-unidad {Pa,kPa,bar,atm,mmHg}]
                                    [--t-unidad {K,C}]

options:
  -h, --help            show this help message and exit
  --cifras CIFRAS       Cifras significativas de los resultados.
  --p1 P1
  --t1 T1
  --t2 T2               Segunda temperatura. Con --dh calcula P2; con --p2 y
                        sin --dh permite estimar ΔH_sub.
  --p2 P2               Segunda presión. Con --dh calcula T2; con --t2 y sin
                        --dh permite estimar ΔH_sub.
  --dh DH               Entalpía de sublimación.
  --dh-unidad DH_UNIDAD
  --masa-molar MASA_MOLAR
  --p-unidad {Pa,kPa,bar,atm,mmHg}
  --t-unidad {K,C}
```

### `lee-kesler`

```text
usage: presion_vapor.py lee-kesler [-h] [--cifras CIFRAS] --t T --tc TC
                                   --pc PC --omega OMEGA [--t-unidad {K,C}]
                                   [--pc-unidad {Pa,kPa,bar,atm,mmHg}]
                                   [--salida-unidad {Pa,kPa,bar,atm,mmHg}]
                                   [--permitir-extrapolacion]

options:
  -h, --help            show this help message and exit
  --cifras CIFRAS       Cifras significativas de los resultados.
  --t T
  --tc TC
  --pc PC
  --omega OMEGA
  --t-unidad {K,C}
  --pc-unidad {Pa,kPa,bar,atm,mmHg}
  --salida-unidad {Pa,kPa,bar,atm,mmHg}
  --permitir-extrapolacion
```

### `interpolar`

```text
usage: presion_vapor.py interpolar [-h] [--cifras CIFRAS] --t1 T1 --p1 P1
                                   --t2 T2 --p2 P2 --t T [--t-unidad {K,C}]
                                   [--p-unidad {Pa,kPa,bar,atm,mmHg}]
                                   [--permitir-extrapolacion]

options:
  -h, --help            show this help message and exit
  --cifras CIFRAS       Cifras significativas de los resultados.
  --t1 T1
  --p1 P1
  --t2 T2
  --p2 P2
  --t T
  --t-unidad {K,C}
  --p-unidad {Pa,kPa,bar,atm,mmHg}
  --permitir-extrapolacion
```

### `duhring`

```text
usage: presion_vapor.py duhring [-h] [--cifras CIFRAS] --puntos PUNTOS
                                [--referencia REFERENCIA]
                                [--temperatura TEMPERATURA] [--t-unidad {K,C}]
                                [--p-unidad {Pa,kPa,bar,atm,mmHg}]
                                [--grafica GRAFICA] [--permitir-extrapolacion]

options:
  -h, --help            show this help message and exit
  --cifras CIFRAS       Cifras significativas de los resultados.
  --puntos PUNTOS       Pares "T,P;T,P;...". Ejemplo: "313,6.08;353,39.33".
                        Use punto decimal aquí para evitar ambigüedad.
  --referencia REFERENCIA
  --temperatura TEMPERATURA
                        T_dis objetivo para estimar P_dis*.
  --t-unidad {K,C}
  --p-unidad {Pa,kPa,bar,atm,mmHg}
  --grafica GRAFICA     Archivo PNG de salida.
  --permitir-extrapolacion
```

### `grafica`

```text
usage: presion_vapor.py grafica [-h] [--cifras CIFRAS] --sustancias SUSTANCIAS
                                [--tipo {pt,semilog,clausius}] [--tmin TMIN]
                                [--tmax TMAX] [--t-unidad {K,C}]
                                [--salida SALIDA] [--permitir-extrapolacion]

options:
  -h, --help            show this help message and exit
  --cifras CIFRAS       Cifras significativas de los resultados.
  --sustancias SUSTANCIAS
                        Nombres separados por comas.
  --tipo {pt,semilog,clausius}
  --tmin TMIN
  --tmax TMAX
  --t-unidad {K,C}
  --salida SALIDA
  --permitir-extrapolacion
```

### `listar`

```text
usage: presion_vapor.py listar [-h] [--cifras CIFRAS]

options:
  -h, --help       show this help message and exit
  --cifras CIFRAS  Cifras significativas de los resultados.
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
Sustancia: Agua
P* = 41,6 kPa
```

## 12. Estado de revisión

Inicio y ayuda revisados; no se ha ejecutado una batería de casos numéricos exhaustiva para esta aplicación.

## 13. Correspondencia bibliográfica

Programa de apoyo al **capítulo 6** de *Estequiometría y cálculos químicos*. El texto del libro es una exposición científica; este manual explica la ejecución del software suministrado. El código y el manual se distribuyen bajo licencia MIT; el DOI específico del software se incorporará tras la primera publicación en Zenodo.
