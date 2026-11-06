# Extracción líquido–líquido

**Manual de usuario · Capítulo 12 · extraccion_liquido_liquido.py**  
**Proyecto:** *Estequiometría y cálculos químicos*. **Estado:** documentación preliminar basada en el código recibido (6 de noviembre de 2026).

## 1. Finalidad y funciones

Distribución de soluto en una o varias extracciones y comparación de extracciones sucesivas.

Esta herramienta automatiza el cálculo y ayuda a verificarlo, pero no sustituye la selección del modelo químico ni la interpretación de sus hipótesis.

## 2. Requisitos e instalación

Se recomienda **Python 3.10 o posterior**. En Windows, abra PowerShell o Símbolo del sistema, entre en la carpeta del capítulo y ejecute la aplicación. Ejemplo desde la carpeta raíz del repositorio:

```bat
cd capitulo_12
python extraccion_liquido_liquido.py
```

El programa se basa en la biblioteca estándar de Python para el cálculo principal. Las dependencias de visualización, cuando existan, se detallan en su ayuda.

## 3. Comandos y opciones de ejecución

**Iniciar con menú o con preguntas sucesivas:**

```bat
python extraccion_liquido_liquido.py
```

**Consultar las opciones admitidas:**

```bat
python extraccion_liquido_liquido.py --help
```

**Ejemplo de uso o comprobación del propio programa:**

```bat
python extraccion_liquido_liquido.py
```

## 4. Menú principal y modos de cálculo

El menú mostrado por el programa, capturado durante esta revisión, ofrece las siguientes opciones:

```text
1. Una extracción
2. Varias extracciones iguales
3. Comparar distintos números de extracciones
0. Salir
```

## 5. Datos introducidos y unidades

Modelo de fases portadoras prácticamente inmiscibles y coeficiente de distribución constante.

Algunos de los campos, selecciones o preguntas definidos explícitamente en el código son:

- `Cantidad inicial de soluto:`
- `Volumen de la fase refinado:`
- `Coeficiente de distribución K_D:`
- `Volumen de disolvente empleado:`
- `Volumen total de disolvente disponible:`
- `Número de extracciones:`
- `Número máximo de extracciones que desea comparar:`
- `Seleccione una opción:`

## 6. Procedimiento recomendado paso a paso

1. Identifique en el capítulo el tipo de problema, las variables conocidas y las hipótesis necesarias.

2. Inicie el programa con `python extraccion_liquido_liquido.py` desde la carpeta indicada.

3. Opción 1 para una extracción, 2 para varias de igual volumen o 3 para comparar números de extracciones.

4. Introduzca los datos conservando las unidades del programa y las cifras significativas correspondientes.

5. Revise las magnitudes calculadas y, cuando el modo lo permita, los residuos de balance, las composiciones y los avisos de validez.

6. Si el resultado es físicamente imposible, examine los datos y los supuestos antes de repetir el cálculo.

## 7. Resultados, verificaciones y alcance científico

Los resultados dependen de la modalidad elegida. Consulte el desarrollo técnico siguiente, extraído de la descripción que acompaña al código, para conocer el modelo que el autor ha implementado y sus limitaciones.

```text
SCRIPT 12.6. EXTRACCIÓN LÍQUIDO-LÍQUIDO
Funcionalidad:
    Calcula la cantidad de soluto que permanece en el refinado y la que
    pasa al extracto en una o varias extracciones líquido-líquido.
Para qué sirve:
    Permite:
        1. resolver una extracción;
        2. resolver varias extracciones con porciones iguales de disolvente;
        3. comparar el efecto del número de extracciones para un volumen
           total fijo de disolvente.
Hipótesis:
    - líquidos portadores prácticamente inmiscibles;
    - volúmenes aproximadamente constantes;
    - disolvente fresco inicialmente libre de soluto;
    - coeficiente de distribución constante.
Cifras significativas:
    Los resultados se redondean automáticamente según los datos introducidos.
```

## 8. Ayuda real de línea de comandos

La salida siguiente fue obtenida al ejecutar `--help` sobre este archivo, no deducida de la documentación del libro:

```text
usage: extraccion_liquido_liquido.py [-h]

Cálculo de una o varias extracciones líquido-líquido.

options:
  -h, --help  show this help message and exit

Use unidades coherentes para los volúmenes. La cantidad de soluto conserva la
unidad introducida. El número de extracciones es un conteo exacto y no limita
las cifras significativas.
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

Inicio y ayuda revisados; no se ha ejecutado una batería de casos numéricos exhaustiva para esta aplicación.

## 12. Correspondencia bibliográfica

Programa de apoyo al **capítulo 12** de *Estequiometría y cálculos químicos*. El texto del libro es una exposición científica; este manual explica la ejecución del software suministrado. El código y el manual se distribuyen bajo licencia MIT; el DOI específico del software se incorporará tras la primera publicación en Zenodo.
