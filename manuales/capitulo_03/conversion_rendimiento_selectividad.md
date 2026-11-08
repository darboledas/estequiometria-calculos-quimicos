# Conversión, rendimiento y selectividad

**Manual de usuario · Capítulo 3 · conversion_rendimiento_selectividad.py**  
**Proyecto:** *Estequiometría y cálculos químicos*. **Estado:** documentación preliminar basada en el código recibido (6 de noviembre de 2026).

## 1. Finalidad y funciones

Cálculo de conversiones, rendimientos experimentales, distribución por rutas y rendimiento global en etapas sucesivas.

Esta herramienta automatiza el cálculo y ayuda a verificarlo, pero no sustituye la selección del modelo químico ni la interpretación de sus hipótesis.

## 2. Requisitos e instalación

Se recomienda **Python 3.10 o posterior**. En Windows, abra PowerShell o Símbolo del sistema, entre en la carpeta del capítulo y ejecute la aplicación. Ejemplo desde la carpeta raíz del repositorio:

```bat
cd capitulo_03
python conversion_rendimiento_selectividad.py
```

El programa se basa en la biblioteca estándar de Python para el cálculo principal. Las dependencias de visualización, cuando existan, se detallan en su ayuda.

## 3. Comandos y opciones de ejecución

**Iniciar con menú o con preguntas sucesivas:**

```bat
python conversion_rendimiento_selectividad.py
```

**Consultar las opciones admitidas:**

```bat
python conversion_rendimiento_selectividad.py --help
```

**Ejemplo de uso o comprobación del propio programa:**

```bat
python conversion_rendimiento_selectividad.py --autoprueba
```

## 4. Menú principal y modos de cálculo

El menú mostrado por el programa, capturado durante esta revisión, ofrece las siguientes opciones:

```text
1. Conversión de un reactivo
2. Rendimiento experimental
3. Reacción simple o análisis de rutas paralelas
4. Rendimiento global de varias etapas
5. Relación entre conversión y rendimientos
h. Ayuda
0. Salir
```

## 5. Datos introducidos y unidades

Atienda a la base de cada rendimiento: alimentado frente a consumido, con valores en tanto por uno o porcentaje según la pregunta.

Algunos de los campos, selecciones o preguntas definidos explícitamente en el código son:

- `Producto obtenido`
- `Producto teórico`
- `Conversión [%]`
- `Rendimiento sobre consumido [%]`
- `Rendimiento global [%]`

## 6. Procedimiento recomendado paso a paso

1. Identifique en el capítulo el tipo de problema, las variables conocidas y las hipótesis necesarias.

2. Inicie el programa con `python conversion_rendimiento_selectividad.py` desde la carpeta indicada.

3. Elija el concepto en el menú; anote alimentación y producto de interés antes de introducir los datos.

4. Introduzca los datos conservando las unidades del programa y las cifras significativas correspondientes.

5. Revise las magnitudes calculadas y, cuando el modo lo permita, los residuos de balance, las composiciones y los avisos de validez.

6. Si el resultado es físicamente imposible, examine los datos y los supuestos antes de repetir el cálculo.

## 7. Resultados, verificaciones y alcance científico

Los resultados dependen de la modalidad elegida. Consulte el desarrollo técnico siguiente, extraído de la descripción que acompaña al código, para conocer el modelo que el autor ha implementado y sus limitaciones.

```text
Conversión, rendimiento y selectividad.
Finalidad: distinguir las bases de cálculo de cada magnitud.
Hipótesis: en el análisis por rutas, reacciones paralelas con productos indicadores exclusivos.
Entradas: cantidades iniciales/finales, coeficientes o rendimientos parciales.
Salidas: conversión, rendimientos y selectividades identificadas.
Requisitos: Python 3.10+, biblioteca estándar.
```

## 8. Ayuda real de línea de comandos

La salida siguiente fue obtenida al ejecutar `--help` sobre este archivo, no deducida de la documentación del libro:

```text
usage: conversion_rendimiento_selectividad.py [-h] [--autoprueba]

Conversión, rendimiento y selectividad

DEFINICIONES
X = (nA0 - nA) / nA0.

Para una ruta a A -> p P:
A destinado a P = (a/p) * (nP - nP0).
Y_global = A destinado a P / nA0.
Y_consumido = A destinado a P / (nA0 - nA).
Y_global = X * Y_consumido.

Selectividades que se muestran por separado:
- Molar P/Q: producto P formado / producto Q formado.
- Entre rutas: A destinado a P / A destinado a Q.
No se confunden ambas cuando las estequiometrías son distintas.

Rendimiento experimental:
producto obtenido / producto teórico, con la misma base y unidad.

Varias etapas:
producto de los rendimientos fraccionarios de las etapas consecutivas.

HIPÓTESIS DEL ANÁLISIS POR RUTAS
Las rutas son paralelas y consumen el mismo reactivo clave.
Cada producto indicador identifica exclusivamente una ruta.
No hay consumo posterior de esos productos.
Si existen reacciones consecutivas, hace falta otro modelo de balance.

Los denominadores nulos producen resultados indefinidos, no ceros ficticios.

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

Programa de apoyo al **capítulo 3** de *Estequiometría y cálculos químicos*. El texto del libro es una exposición científica; este manual explica la ejecución del software suministrado. El código y el manual se distribuyen bajo licencia MIT; DOI general del software: [10.5281/zenodo.24020474](https://doi.org/10.5281/zenodo.24020474). DOI de la versión publicada 0.9.0: [10.5281/zenodo.24020473](https://doi.org/10.5281/zenodo.24020473). DOI del libro: [10.5281/zenodo.24013068](https://doi.org/10.5281/zenodo.24013068).


## Comprobación independiente de revisión integral

Caso de referencia: **10 mol iniciales y 6 mol finales ⇒ X = 0,4**. Conversión de un reactivo.

La prueba reproducible figura en `pruebas_revision/test_auditoria_integral.py`; los invariantes adicionales, cuando corresponden, están en `pruebas_revision/test_invariantes_cientificos.py`. Se trata de comprobaciones de casos seleccionados, no de una verificación exhaustiva del dominio del modelo.
