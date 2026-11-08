# Operaciones de equilibrio líquido–vapor

**Manual de usuario · Capítulo 7 · operaciones_liquido_vapor.py**  
**Proyecto:** *Estequiometría y cálculos químicos*. **Estado:** documentación preliminar basada en el código recibido (6 de noviembre de 2026).

## 1. Finalidad y funciones

Regla de palanca, flash, Rachford–Rice, destilación diferencial de Rayleigh y etapas ideales.

Esta herramienta automatiza el cálculo y ayuda a verificarlo, pero no sustituye la selección del modelo químico ni la interpretación de sus hipótesis.

## 2. Requisitos e instalación

Se recomienda **Python 3.10 o posterior**. En Windows, abra PowerShell o Símbolo del sistema, entre en la carpeta del capítulo y ejecute la aplicación. Ejemplo desde la carpeta raíz del repositorio:

```bat
cd capitulo_07
python operaciones_liquido_vapor.py
```

El programa se basa en la biblioteca estándar de Python para el cálculo principal. Las dependencias de visualización, cuando existan, se detallan en su ayuda.

## 3. Comandos y opciones de ejecución

**Iniciar con menú o con preguntas sucesivas:**

```bat
python operaciones_liquido_vapor.py
```

**Consultar las opciones admitidas:**

```bat
python operaciones_liquido_vapor.py --help
```

**Ejemplo de uso o comprobación del propio programa:**

```bat
python operaciones_liquido_vapor.py flash-k --z 0,20 --z 0,50 --z 0,30 --K 2,584 --K 1,239 --K 0,408 --F 100
```

## 4. Menú principal y modos de cálculo

El menú mostrado por el programa, capturado durante esta revisión, ofrece las siguientes opciones:

```text
1. Regla de la palanca / balance de fases
2. Vaporización flash a partir de K_i
3. Vaporización flash ideal con Antoine, T y P
4. Destilación simple/diferencial (Rayleigh, α constante)
5. Rayleigh inverso: composición final a partir del líquido residual
6. Vaporizaciones-condensaciones sucesivas (α constante)
0. Salir
```

## 5. Datos introducidos y unidades

En flash, el algoritmo debe respetar 0≤β≤1; el modelo de Rayleigh usa volatilidad relativa constante.

Algunos de los campos, selecciones o preguntas definidos explícitamente en el código son:

- `Número de componentes:`
- `Opción:`
- `¿Desea calcular también composiciones másicas? [s/N]:`
- `Tmin (K) =`
- `Tmax (K) =`
- `¿Introducir intervalo válido de Antoine? [S/n]:`
- `Cantidad o caudal total F:`
- `Cantidad o caudal de alimentación F:`
- `T (K):`
- `P (kPa):`
- `Cantidad inicial de líquido, N0:`
- `Fracción molar inicial del componente más volátil, x0:`
- `Fracción molar final en el residuo, xf:`
- `Volatilidad relativa constante, α:`
- `Cantidad residual objetivo, N:`
- `x0 del componente más volátil:`
- `Número de vaporizaciones:`

## 6. Procedimiento recomendado paso a paso

1. Identifique en el capítulo el tipo de problema, las variables conocidas y las hipótesis necesarias.

2. Inicie el programa con `python operaciones_liquido_vapor.py` desde la carpeta indicada.

3. Elija 2 para flash con K definidos, o 4 para Rayleigh con α constante.

4. Introduzca los datos conservando las unidades del programa y las cifras significativas correspondientes.

5. Revise las magnitudes calculadas y, cuando el modo lo permita, los residuos de balance, las composiciones y los avisos de validez.

6. Si el resultado es físicamente imposible, examine los datos y los supuestos antes de repetir el cálculo.

## 7. Resultados, verificaciones y alcance científico

Los resultados dependen de la modalidad elegida. Consulte el desarrollo técnico siguiente, extraído de la descripción que acompaña al código, para conocer el modelo que el autor ha implementado y sus limitaciones.

```text
Herramienta de cálculo para operaciones de equilibrio líquido-vapor del
capítulo 7.
Incluye:
    1) Regla de la palanca / balance de fases:
       - binaria y multicomponente;
       - fracción líquida y fracción vapor;
       - cantidades molares de cada fase;
       - cantidad de cada componente en cada fase;
       - porcentaje de cada componente recuperado en líquido y vapor;
       - comprobación de balances.
    2) Vaporización flash:
       - binaria y multicomponente;
       - entrada directa de K_i;
       - o cálculo de K_i = P_i*(T)/P mediante Antoine para mezcla ideal;
       - clasificación automática: líquido, vapor, punto de burbuja,
         punto de rocío o región bifásica;
       - resolución de Rachford-Rice con método salvaguardado;
       - comprobación de normalización y balances;
       - composición másica opcional si se proporcionan masas molares.
    3) Destilación simple o diferencial (Rayleigh), binaria:
       - volatilidad relativa constante;
       - cálculo de líquido residual, destilado total, composición media
         del destilado y recuperación del componente más volátil;
       - posibilidad de calcular la composición final del residuo a partir
         de una cantidad residual objetivo.
    4) Vaporizaciones-condensaciones ideales sucesivas, binaria:
       - modelo con volatilidad relativa constante;
       - útil para estudiar el enriquecimiento por etapas;
       - no representa una columna de destilación completa.
Hipótesis:
    - Equilibrio líquido-vapor ideal cuando se usa Antoine:
          K_i = P_i*(T) / P
    - Antoine:
          log10(P_i*) = A_i - B_i / (T + C_i)
      con P_i* en kPa y T en K.
      Si la correlación aparece como T - c, introduzca C = -c.
    - La destilación diferencial se limita a sistemas binarios y utiliza
      una volatilidad relativa constante, tal como se plantea en los
      ejercicios del capítulo.
Resolución numérica:
    - Rachford-Rice se resuelve exclusivamente dentro de 0 <= beta <= 1.
    - Se intenta Newton salvaguardado.
    - Si el paso sale del intervalo, la derivada no es adecuada, aparece
      una anomalía numérica o el residuo empeora, se usa bisección.
    - La convergencia exige simultáneamente tolerancia en beta y en el
      residuo.
    - Si no existe raíz bifásica, el programa no la fuerza: identifica la
      alimentación como monofásica o situada sobre una frontera de fase.
Entrada decimal:
    - En modo interactivo se aceptan coma o punto decimal.
    - En línea de comandos también se aceptan ambos formatos.
Salida:
    - Se utiliza coma decimal.
Dependencias:
    - Solo biblioteca estándar de Python.
```

## 8. Ayuda real de línea de comandos

La salida siguiente fue obtenida al ejecutar `--help` sobre este archivo, no deducida de la documentación del libro:

```text
usage: operaciones_liquido_vapor.py [-h]
                                    {lever,flash-k,flash-antoine,rayleigh-alpha,rayleigh-target,stages-alpha} ...

Regla de la palanca, flash multicomponente, Rachford-Rice y destilación diferencial del capítulo 7.

positional arguments:
  {lever,flash-k,flash-antoine,rayleigh-alpha,rayleigh-target,stages-alpha}
    lever               Regla de la palanca / balance de fases.
    flash-k             Flash a partir de z_i y K_i.
    flash-antoine       Flash ideal con Antoine a T y P dadas.
    rayleigh-alpha      Destilación diferencial con α constante y xf conocida.
    rayleigh-target     Calcula xf para una cantidad residual objetivo.
    stages-alpha        Vaporizaciones-condensaciones ideales sucesivas con α constante.

options:
  -h, --help            show this help message and exit
```

## 9. Subcomandos disponibles

Cada subcomando dispone de ayuda propia con `python operaciones_liquido_vapor.py SUBCOMANDO --help`. Se reproducen las opciones efectivamente declaradas:

### `lever`

```text
usage: operaciones_liquido_vapor.py lever [-h] --z Z --x X --y Y [--name NAME]
                                          [--F F] [--sig SIG]

options:
  -h, --help   show this help message and exit
  --z Z        Fracción global z_i.
  --x X        Fracción líquida x_i.
  --y Y        Fracción vapor y_i.
  --name NAME  Nombre del componente.
  --F F        Cantidad/caudal total.
  --sig SIG    Cifras significativas mostradas (predeterminado: 5).
```

### `flash-k`

```text
usage: operaciones_liquido_vapor.py flash-k [-h] --z Z --K K [--name NAME]
                                            [--mw MW] [--F F] [--verbose]
                                            [--sig SIG]

options:
  -h, --help   show this help message and exit
  --z Z
  --K K
  --name NAME  Nombre del componente.
  --mw MW      Masa molar opcional, g/mol.
  --F F
  --verbose
  --sig SIG    Cifras significativas mostradas (predeterminado: 5).
```

### `flash-antoine`

```text
usage: operaciones_liquido_vapor.py flash-antoine [-h] --component COMPONENT
                                                  --z Z --T T --P P [--F F]
                                                  [--mw MW] [--verbose]
                                                  [--sig SIG]

options:
  -h, --help            show this help message and exit
  --component COMPONENT
                        'NOMBRE;A;B;C' o 'NOMBRE;A;B;C;Tmin;Tmax'. Repetir una
                        vez por componente.
  --z Z
  --T T                 Temperatura en K.
  --P P                 Presión total en kPa.
  --F F
  --mw MW               Masa molar opcional, g/mol.
  --verbose
  --sig SIG             Cifras significativas mostradas (predeterminado: 5).
```

### `rayleigh-alpha`

```text
usage: operaciones_liquido_vapor.py rayleigh-alpha [-h] --F0 F0 --x0 X0
                                                   --xf XF --alpha ALPHA
                                                   [--sig SIG]

options:
  -h, --help     show this help message and exit
  --F0 F0        Cantidad inicial.
  --x0 X0        Composición inicial del volátil.
  --xf XF        Composición final del residuo.
  --alpha ALPHA  Volatilidad relativa constante.
  --sig SIG      Cifras significativas mostradas (predeterminado: 5).
```

### `rayleigh-target`

```text
usage: operaciones_liquido_vapor.py rayleigh-target [-h] --F0 F0 --N N --x0 X0
                                                    --alpha ALPHA [--sig SIG]

options:
  -h, --help     show this help message and exit
  --F0 F0
  --N N          Cantidad residual objetivo.
  --x0 X0
  --alpha ALPHA
  --sig SIG      Cifras significativas mostradas (predeterminado: 5).
```

### `stages-alpha`

```text
usage: operaciones_liquido_vapor.py stages-alpha [-h] --x0 X0 --alpha ALPHA
                                                 --stages STAGES [--sig SIG]

options:
  -h, --help       show this help message and exit
  --x0 X0
  --alpha ALPHA
  --stages STAGES
  --sig SIG        Cifras significativas mostradas (predeterminado: 5).
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
Estado: BIFASICO
Fracción vapor, β = 0,57899 (57,899 %)
Fracción líquida = 0,42101 (42,101 %)
```

## 12. Estado de revisión

Inicio y ayuda revisados; no se ha ejecutado una batería de casos numéricos exhaustiva para esta aplicación.

## 13. Correspondencia bibliográfica

Programa de apoyo al **capítulo 7** de *Estequiometría y cálculos químicos*. El texto del libro es una exposición científica; este manual explica la ejecución del software suministrado. El código y el manual se distribuyen bajo licencia MIT; DOI general del software: [10.5281/zenodo.24020474](https://doi.org/10.5281/zenodo.24020474). DOI de la versión publicada 0.9.0: [10.5281/zenodo.24020473](https://doi.org/10.5281/zenodo.24020473). DOI del libro: [10.5281/zenodo.24013068](https://doi.org/10.5281/zenodo.24013068).


## Comprobación independiente de revisión integral

Caso de referencia: **Flash: z = (0,5; 0,5), K = (2; 0,5) ⇒ β = 0,5**. Raíz de Rachford–Rice y cierre de fases.

La prueba reproducible figura en `pruebas_revision/test_auditoria_integral.py`; los invariantes adicionales, cuando corresponden, están en `pruebas_revision/test_invariantes_cientificos.py`. Se trata de comprobaciones de casos seleccionados, no de una verificación exhaustiva del dominio del modelo.

### Nota de verificación científica adicional

Revisión adicional (7-11-2026): comprobados 500 repartos aleatorios del flash multicomponente mediante cierres de composición y materia, y 200 integrales de Rayleigh frente a su solución analítica para volatilidad relativa constante. Los ejemplos constituyen pruebas de consistencia algebraica y no abarcan equipos reales ni coeficientes K dependientes de composición.
