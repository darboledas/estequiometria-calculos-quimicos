# Densidad, gravedad específica y escalas industriales

**Manual de usuario · Capítulo 3 · densidades_y_escalas.py**  
**Proyecto:** *Estequiometría y cálculos químicos*. **Estado:** documentación preliminar basada en el código recibido (6 de noviembre de 2026).

## 1. Finalidad y funciones

Cálculo de densidad y conversiones entre gravedad específica, Baumé, Twaddell, API y escala Brix.

Esta herramienta automatiza el cálculo y ayuda a verificarlo, pero no sustituye la selección del modelo químico ni la interpretación de sus hipótesis.

## 2. Requisitos e instalación

Se recomienda **Python 3.10 o posterior**. En Windows, abra PowerShell o Símbolo del sistema, entre en la carpeta del capítulo y ejecute la aplicación. Ejemplo desde la carpeta raíz del repositorio:

```bat
cd capitulo_03
python densidades_y_escalas.py
```

El programa se basa en la biblioteca estándar de Python para el cálculo principal. Las dependencias de visualización, cuando existan, se detallan en su ayuda.

## 3. Comandos y opciones de ejecución

**Iniciar con menú o con preguntas sucesivas:**

```bat
python densidades_y_escalas.py
```

**Consultar las opciones admitidas:**

```bat
python densidades_y_escalas.py --help
```

**Ejemplo de uso o comprobación del propio programa:**

```bat
python densidades_y_escalas.py --autoprueba
```

## 4. Menú principal y modos de cálculo

El menú mostrado por el programa, capturado durante esta revisión, ofrece las siguientes opciones:

```text
1. Calcular o convertir escalas pasando por GE
2. Calcular densidad mediante masa y volumen
3. Calcular Brix o masas de sacarosa y agua
h. Ayuda
0. Salir
```

## 5. Datos introducidos y unidades

Las condiciones térmicas de referencia importan; no confunda densidad absoluta con gravedad específica.

Algunos de los campos, selecciones o preguntas definidos explícitamente en el código son:

- `Densidad del agua a la temperatura de referencia [g/mL]`
- `Valor de origen`
- `Volumen`
- `Factor GE_destino / GE_origen`
- `Masa de sacarosa [g]`
- `Masa de agua [g]`
- `Grados Brix`
- `Masa total [g]`
- `Temperatura de la muestra [C]:`
- `Temperatura del agua de referencia [C]:`

## 6. Procedimiento recomendado paso a paso

1. Identifique en el capítulo el tipo de problema, las variables conocidas y las hipótesis necesarias.

2. Inicie el programa con `python densidades_y_escalas.py` desde la carpeta indicada.

3. Seleccione 1 para convertir escalas; 2 para densidad masa/volumen; 3 para Brix y masa de componentes.

4. Introduzca los datos conservando las unidades del programa y las cifras significativas correspondientes.

5. Revise las magnitudes calculadas y, cuando el modo lo permita, los residuos de balance, las composiciones y los avisos de validez.

6. Si el resultado es físicamente imposible, examine los datos y los supuestos antes de repetir el cálculo.

## 7. Resultados, verificaciones y alcance científico

Los resultados dependen de la modalidad elegida. Consulte el desarrollo técnico siguiente, extraído de la descripción que acompaña al código, para conocer el modelo que el autor ha implementado y sus limitaciones.

```text
Densidad, gravedad específica y escalas industriales.
Finalidad: calcular densidad, Brix, Baumé, Twaddell y API.
Hipótesis: referencias térmicas compatibles; Brix densimétrico basado en sacarosa.
Entradas: valores, referencias y correcciones documentadas cuando cambie la referencia térmica.
Salidas: magnitud calculada y GE intermedia.
Requisitos: Python 3.10+, biblioteca estándar.
```

## 8. Ayuda real de línea de comandos

La salida siguiente fue obtenida al ejecutar `--help` sobre este archivo, no deducida de la documentación del libro:

```text
usage: densidades_y_escalas.py [-h] [--autoprueba]

Densidad, gravedad específica y escalas

ESCALAS
GE = densidad de muestra / densidad del agua de referencia.
Baumé pesado: Be = 145 - 145/GE; GE >= 1.
Baumé ligero: Be = 140/GE - 130; 0 < GE <= 1.
Twaddell: Tw = 200*(GE - 1); GE >= 1.
API: API = 141.5/GE - 131.5.

TEMPERATURAS
Baumé con estas constantes y API utilizan GE a 60 F/60 F.
Para Twaddell, GE y densidad debe indicar la referencia utilizada.
La tabla de sacarosa utiliza densidad a 20 C y GE 20/20.

No se corrige automáticamente una temperatura desconocida.
Entre referencias diferentes se solicita un factor documentado:
    factor = GE en referencia de destino / GE en referencia de origen.
Sin ese dato no se realiza la conversión física entre referencias.

BRIX
Para sacarosa y agua, Brix = porcentaje másico de sacarosa.
Para GE <-> Brix se interpola una tabla de densidad a 20 C.
Intervalo incorporado: 0 a 60 Brix. No se extrapola.
La interpolación es aproximada; la precisión de presentación no constituye
una garantía de exactitud experimental.
En mezclas distintas de sacarosa/agua solo se calcula un equivalente
densimétrico de sacarosa, que puede diferir del Brix refractométrico.

FUENTES
NIST, Calibration Services for Hydrometers:
https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=832342
EIA, API gravity:
https://www.eia.gov/tools/glossary/index.php?id=Api+gravity
Anton Paar, densidad de sacarosa a 20 C:
https://wiki.anton-paar.com/us-en/density-and-density-measurement/sucrose-density/

Las constantes de las escalas son convencionales; la tabla es calibración,
no datos fijos de un problema.

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
