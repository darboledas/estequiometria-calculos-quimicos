# Ajuste de ecuaciones químicas

**Manual de usuario · Capítulo 3 · ajuste_ecuaciones.py**  
**Proyecto:** *Estequiometría y cálculos químicos*. **Estado:** documentación preliminar basada en el código recibido (6 de noviembre de 2026).

## 1. Finalidad y funciones

Ajuste exacto de coeficientes estequiométricos y comprobación de conservación atómica y de carga mediante matrices.

Esta herramienta automatiza el cálculo y ayuda a verificarlo, pero no sustituye la selección del modelo químico ni la interpretación de sus hipótesis.

## 2. Requisitos e instalación

Se recomienda **Python 3.10 o posterior**. En Windows, abra PowerShell o Símbolo del sistema, entre en la carpeta del capítulo y ejecute la aplicación. Ejemplo desde la carpeta raíz del repositorio:

```bat
cd capitulo_03
python ajuste_ecuaciones.py
```

El programa se basa en la biblioteca estándar de Python para el cálculo principal. Las dependencias de visualización, cuando existan, se detallan en su ayuda.

## 3. Comandos y opciones de ejecución

**Iniciar con menú o con preguntas sucesivas:**

```bat
python ajuste_ecuaciones.py
```

**Consultar las opciones admitidas:**

```bat
python ajuste_ecuaciones.py --help
```

**Ejemplo de uso o comprobación del propio programa:**

```bat
python ajuste_ecuaciones.py --autoprueba
```

## 4. Menú principal y modos de cálculo

El menú mostrado por el programa, capturado durante esta revisión, ofrece las siguientes opciones:

```text
1. Ajustar automáticamente
2. Comprobar coeficientes
3. Mostrar matriz y desarrollo algebraico
h. Ayuda
0. Salir
```

## 5. Datos introducidos y unidades

Introduzca reactivos y productos mediante sus fórmulas químicas; los coeficientes son enteros exactos.

Algunos de los campos, selecciones o preguntas definidos explícitamente en el código son:

- `Reactivos separados por ;:`
- `Productos separados por ;:`

## 6. Procedimiento recomendado paso a paso

1. Identifique en el capítulo el tipo de problema, las variables conocidas y las hipótesis necesarias.

2. Inicie el programa con `python ajuste_ecuaciones.py` desde la carpeta indicada.

3. Seleccione 1 para ajustar, 2 para verificar coeficientes propuestos o 3 para observar la matriz.

4. Introduzca los datos conservando las unidades del programa y las cifras significativas correspondientes.

5. Revise las magnitudes calculadas y, cuando el modo lo permita, los residuos de balance, las composiciones y los avisos de validez.

6. Si el resultado es físicamente imposible, examine los datos y los supuestos antes de repetir el cálculo.

## 7. Resultados, verificaciones y alcance científico

Los resultados dependen de la modalidad elegida. Consulte el desarrollo técnico siguiente, extraído de la descripción que acompaña al código, para conocer el modelo que el autor ha implementado y sus limitaciones.

```text
Ajuste de ecuaciones químicas mediante álgebra matricial.
Finalidad: obtener o comprobar coeficientes exactos.
Hipótesis: conservación de átomos y carga; especies conocidas.
Entradas: fórmulas y, opcionalmente, coeficientes.
Salidas: ecuación ajustada, matriz y diagnóstico de unicidad.
Requisitos: Python 3.10+, biblioteca estándar.
```

## 8. Ayuda real de línea de comandos

La salida siguiente fue obtenida al ejecutar `--help` sobre este archivo, no deducida de la documentación del libro:

```text
usage: ajuste_ecuaciones.py [-h] [--autoprueba]

Ajuste de ecuaciones químicas

Ajuste matricial exacto y comprobación de ecuaciones químicas.
La matriz utiliza columnas positivas para reactivos y negativas para productos.
Los coeficientes son enteros exactos: no se redondean por cifras significativas.

FÓRMULAS Y AJUSTE
- Introduzca las especies de cada lado separadas por punto y coma:
  Ca(OH)2; HCl
- No anteponga coeficientes a las fórmulas.
- Se admiten paréntesis, corchetes y grupos anidados.
- Hidratos: CuSO4·5H2O; utilice el punto central ·.
- Cargas: Fe^3+, SO4^2-, H^+, OH^-; electrón: e^-.
- Se admiten los sufijos (s), (l), (g), (aq) y (ac).
- Los subíndices deben escribirse con dígitos normales.
- El ajuste conserva átomos y carga mediante aritmética racional exacta.
- No añade automáticamente agua, protones, hidróxido ni electrones:
  introduzca todas las especies que deban intervenir.
- Si hay varias soluciones independientes, el programa lo indica y permite
  introducir coeficientes para comprobar un ajuste concreto.
- Un ajuste algebraico no demuestra que la reacción sea químicamente viable.

INTRODUCCIÓN DE DATOS
- Puede utilizar coma o punto decimal y notación científica: 1,20e-3.
- No utilice separadores de millares.
- Los ceros finales escritos cuentan: 1,20 tiene tres cifras.
- En enteros también cuentan: 1200 tiene cuatro cifras.
  Para indicar otra precisión escriba, por ejemplo, 1200:2.
- El sufijo ! indica un dato exacto: 100!, 0!, 2!.
  Utilícelo solo cuando el dato realmente sea exacto.
- Los coeficientes estequiométricos y factores de unidades son exactos.
- Las masas molares introducidas también intervienen en la precisión.
- No se redondean los valores intermedios.
- En sumas/restas se controla la posición decimal; en productos/cocientes,
  las cifras significativas. Esto no sustituye el cálculo de incertidumbres.
- Los resultados utilizan coma decimal y notación científica para evitar
  ambigüedades en los ceros finales.
- Escriba volver en una entrada numérica para regresar al menú.

options:
  -h, --help    show this help message and exit
  --autoprueba  Ejecuta las comprobaciones internas y termina.
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

Autoprueba incorporada: correcta en la revisión.

## 12. Correspondencia bibliográfica

Programa de apoyo al **capítulo 3** de *Estequiometría y cálculos químicos*. El texto del libro es una exposición científica; este manual explica la ejecución del software suministrado. El código y el manual se distribuyen bajo licencia MIT; el DOI específico del software se incorporará tras la primera publicación en Zenodo.
