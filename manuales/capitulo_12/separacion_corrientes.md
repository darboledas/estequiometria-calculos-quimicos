# Separación en dos corrientes

**Manual de usuario · Capítulo 12 · separacion_corrientes.py**  
**Proyecto:** *Estequiometría y cálculos químicos*. **Estado:** documentación preliminar basada en el código recibido (6 de noviembre de 2026).

## 1. Finalidad y funciones

Balance de materia de una corriente de alimentación y dos salidas con composiciones dadas.

Esta herramienta automatiza el cálculo y ayuda a verificarlo, pero no sustituye la selección del modelo químico ni la interpretación de sus hipótesis.

## 2. Requisitos e instalación

Se recomienda **Python 3.10 o posterior**. En Windows, abra PowerShell o Símbolo del sistema, entre en la carpeta del capítulo y ejecute la aplicación. Ejemplo desde la carpeta raíz del repositorio:

```bat
cd capitulo_12
python separacion_corrientes.py
```

El programa se basa en la biblioteca estándar de Python para el cálculo principal. Las dependencias de visualización, cuando existan, se detallan en su ayuda.

## 3. Comandos y opciones de ejecución

**Iniciar con menú o con preguntas sucesivas:**

```bat
python separacion_corrientes.py
```

**Consultar las opciones admitidas:**

```bat
python separacion_corrientes.py --help
```

**Ejemplo de uso o comprobación del propio programa:**

```bat
python separacion_corrientes.py
```

## 4. Menú principal y modos de cálculo

**No hay un menú principal de opciones:** el programa guía al usuario mediante preguntas consecutivas o acepta argumentos al iniciarse. No debe confundirse la ausencia de menú con ausencia de controles de validación.

## 5. Datos introducidos y unidades

Use caudales y fracciones másicas con la misma base; no se considera reacción química.

Algunos de los campos, selecciones o preguntas definidos explícitamente en el código son:

- `Caudal de alimentación [kg/h]:`
- `Soluto en la alimentación [% masa]:`
- `Soluto en la corriente 1 [% masa]:`
- `Soluto en la corriente 2 [% masa]:`

## 6. Procedimiento recomendado paso a paso

1. Identifique en el capítulo el tipo de problema, las variables conocidas y las hipótesis necesarias.

2. Inicie el programa con `python separacion_corrientes.py` desde la carpeta indicada.

3. El programa no tiene un menú de modos: solicite alimentación, su composición y las composiciones de ambas salidas.

4. Introduzca los datos conservando las unidades del programa y las cifras significativas correspondientes.

5. Revise las magnitudes calculadas y, cuando el modo lo permita, los residuos de balance, las composiciones y los avisos de validez.

6. Si el resultado es físicamente imposible, examine los datos y los supuestos antes de repetir el cálculo.

## 7. Resultados, verificaciones y alcance científico

Los resultados dependen de la modalidad elegida. Consulte el desarrollo técnico siguiente, extraído de la descripción que acompaña al código, para conocer el modelo que el autor ha implementado y sus limitaciones.

```text
SCRIPT 12.1. SEPARACIÓN EN DOS CORRIENTES
Funcionalidad:
    Calcula los caudales de dos corrientes de salida obtenidas al separar
    una alimentación de composición conocida.
Para qué sirve:
    Para problemas de separación sin reacción química en los que se conocen
    el caudal y composición de la alimentación y las composiciones de las
    dos corrientes de salida.
Cifras significativas:
    Los resultados se redondean automáticamente según las cifras
    significativas de los datos introducidos y las reglas de las operaciones.
```

## 8. Ayuda real de línea de comandos

La salida siguiente fue obtenida al ejecutar `--help` sobre este archivo, no deducida de la documentación del libro:

```text
usage: separacion_corrientes.py [-h]

Balance de una alimentación que se separa en dos corrientes.

options:
  -h, --help  show this help message and exit

Introduzca porcentajes como números (por ejemplo 20,0 para 20,0 %). Todos los
dígitos escritos se consideran significativos; use notación científica si
desea indicar otra precisión.
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

Programa de apoyo al **capítulo 12** de *Estequiometría y cálculos químicos*. El texto del libro es una exposición científica; este manual explica la ejecución del software suministrado. El código y el manual se distribuyen bajo licencia MIT; DOI general del software: [10.5281/zenodo.24020474](https://doi.org/10.5281/zenodo.24020474). DOI de la versión publicada 0.9.0: [10.5281/zenodo.24020473](https://doi.org/10.5281/zenodo.24020473). DOI del libro: [10.5281/zenodo.24013068](https://doi.org/10.5281/zenodo.24013068).


## Comprobación independiente de revisión integral

Caso de referencia: **100 kg/h al 30 %, salidas al 50 % y 10 % ⇒ 50 kg/h en cada corriente**. Balance total y de soluto.

La prueba reproducible figura en `pruebas_revision/test_auditoria_integral.py`; los invariantes adicionales, cuando corresponden, están en `pruebas_revision/test_invariantes_cientificos.py`. Se trata de comprobaciones de casos seleccionados, no de una verificación exhaustiva del dominio del modelo.


### Entrada por recuperación del soluto, ejercicio 12.B.14

El nuevo comando `python capitulo_12/separacion_corrientes.py --recuperacion`
solicita caudal de alimentación, porcentaje másico de soluto en la alimentación,
porcentaje másico de soluto en la corriente concentrada y porcentaje de recuperación
del soluto en dicha corriente. Calcula ambas salidas y la concentración del rechazo.

Ejemplo: `600`, `15,0`, `45,0`, `90,0` produce **180 kg/h** en la corriente
concentrada, **420 kg/h** en la segunda corriente y **2,142857… %** de soluto
en esta última, de acuerdo con el solucionario. El uso sin `--recuperacion`
conserva la interacción anterior por dos composiciones de salida.

Por propagación conservadora de las cifras significativas, la pantalla puede presentar
la composición de rechazo como `2,1 %`; la línea *Valor interno aproximado para
cotejo* permite verificar el `2,14 %` publicado en el solucionario. El valor interno
no debe interpretarse como precisión experimental adicional.
