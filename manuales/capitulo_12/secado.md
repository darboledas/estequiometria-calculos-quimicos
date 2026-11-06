# Secado de sólidos húmedos

**Manual de usuario · Capítulo 12 · secado.py**  
**Proyecto:** *Estequiometría y cálculos químicos*. **Estado:** documentación preliminar basada en el código recibido (6 de noviembre de 2026).

## 1. Finalidad y funciones

Balance de sólido seco conservado y agua retirada; humedad en base húmeda o seca.

Esta herramienta automatiza el cálculo y ayuda a verificarlo, pero no sustituye la selección del modelo químico ni la interpretación de sus hipótesis.

## 2. Requisitos e instalación

Se recomienda **Python 3.10 o posterior**. En Windows, abra PowerShell o Símbolo del sistema, entre en la carpeta del capítulo y ejecute la aplicación. Ejemplo desde la carpeta raíz del repositorio:

```bat
cd capitulo_12
python secado.py
```

El programa se basa en la biblioteca estándar de Python para el cálculo principal. Las dependencias de visualización, cuando existan, se detallan en su ayuda.

## 3. Comandos y opciones de ejecución

**Iniciar con menú o con preguntas sucesivas:**

```bat
python secado.py
```

**Consultar las opciones admitidas:**

```bat
python secado.py --help
```

**Ejemplo de uso o comprobación del propio programa:**

```bat
python secado.py
```

## 4. Menú principal y modos de cálculo

El menú mostrado por el programa, capturado durante esta revisión, ofrece las siguientes opciones:

```text
1. Base húmeda
2. Base seca
0. Salir
```

## 5. Datos introducidos y unidades

No confunda humedad en base húmeda con relación agua/sólido seco.

Algunos de los campos, selecciones o preguntas definidos explícitamente en el código son:

- `Masa inicial del material húmedo:`
- `Humedad inicial [% en base húmeda]:`
- `Humedad final [% en base húmeda]:`
- `Humedad inicial [% en base seca]:`
- `Humedad final [% en base seca]:`
- `Seleccione una opción:`

## 6. Procedimiento recomendado paso a paso

1. Identifique en el capítulo el tipo de problema, las variables conocidas y las hipótesis necesarias.

2. Inicie el programa con `python secado.py` desde la carpeta indicada.

3. Seleccione 1 para base húmeda o 2 para base seca; introduzca humedad inicial y final.

4. Introduzca los datos conservando las unidades del programa y las cifras significativas correspondientes.

5. Revise las magnitudes calculadas y, cuando el modo lo permita, los residuos de balance, las composiciones y los avisos de validez.

6. Si el resultado es físicamente imposible, examine los datos y los supuestos antes de repetir el cálculo.

## 7. Resultados, verificaciones y alcance científico

Los resultados dependen de la modalidad elegida. Consulte el desarrollo técnico siguiente, extraído de la descripción que acompaña al código, para conocer el modelo que el autor ha implementado y sus limitaciones.

```text
SCRIPT 12.3. SECADO DE UN SÓLIDO HÚMEDO
Funcionalidad:
    Calcula la masa final del producto y el agua eliminada durante el secado.
Para qué sirve:
    Permite trabajar con humedades expresadas:
        1. en base húmeda;
        2. en base seca.
    El programa conserva la masa de sólido seco y calcula las cantidades
    de agua inicial y final.
Cifras significativas:
    Los resultados se redondean automáticamente según los datos introducidos.
```

## 8. Ayuda real de línea de comandos

La salida siguiente fue obtenida al ejecutar `--help` sobre este archivo, no deducida de la documentación del libro:

```text
usage: secado.py [-h]

Calcula balances de secado en base húmeda o base seca.

options:
  -h, --help  show this help message and exit

Las humedades se introducen como porcentajes. El número de dígitos escrito
determina la precisión del dato.
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
