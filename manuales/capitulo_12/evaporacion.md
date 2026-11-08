# Concentración por evaporación

**Manual de usuario · Capítulo 12 · evaporacion.py**  
**Proyecto:** *Estequiometría y cálculos químicos*. **Estado:** documentación preliminar basada en el código recibido (6 de noviembre de 2026).

## 1. Finalidad y funciones

Balance de un soluto no volátil y un disolvente evaporado considerado puro.

Esta herramienta automatiza el cálculo y ayuda a verificarlo, pero no sustituye la selección del modelo químico ni la interpretación de sus hipótesis.

## 2. Requisitos e instalación

Se recomienda **Python 3.10 o posterior**. En Windows, abra PowerShell o Símbolo del sistema, entre en la carpeta del capítulo y ejecute la aplicación. Ejemplo desde la carpeta raíz del repositorio:

```bat
cd capitulo_12
python evaporacion.py
```

El programa se basa en la biblioteca estándar de Python para el cálculo principal. Las dependencias de visualización, cuando existan, se detallan en su ayuda.

## 3. Comandos y opciones de ejecución

**Iniciar con menú o con preguntas sucesivas:**

```bat
python evaporacion.py
```

**Consultar las opciones admitidas:**

```bat
python evaporacion.py --help
```

**Ejemplo de uso o comprobación del propio programa:**

```bat
python evaporacion.py
```

## 4. Menú principal y modos de cálculo

**No hay un menú principal de opciones:** el programa guía al usuario mediante preguntas consecutivas o acepta argumentos al iniciarse. No debe confundirse la ausencia de menú con ausencia de controles de validación.

## 5. Datos introducidos y unidades

La concentración inicial y final se introducen en porcentaje másico.

Algunos de los campos, selecciones o preguntas definidos explícitamente en el código son:

- `Masa o caudal de alimentación:`
- `Concentración inicial de soluto [% masa]:`
- `Concentración final de soluto [% masa]:`

## 6. Procedimiento recomendado paso a paso

1. Identifique en el capítulo el tipo de problema, las variables conocidas y las hipótesis necesarias.

2. Inicie el programa con `python evaporacion.py` desde la carpeta indicada.

3. Introduzca alimentación, concentración inicial y concentración final cuando aparezcan los campos.

4. Introduzca los datos conservando las unidades del programa y las cifras significativas correspondientes.

5. Revise las magnitudes calculadas y, cuando el modo lo permita, los residuos de balance, las composiciones y los avisos de validez.

6. Si el resultado es físicamente imposible, examine los datos y los supuestos antes de repetir el cálculo.

## 7. Resultados, verificaciones y alcance científico

Los resultados dependen de la modalidad elegida. Consulte el desarrollo técnico siguiente, extraído de la descripción que acompaña al código, para conocer el modelo que el autor ha implementado y sus limitaciones.

```text
SCRIPT 12.2. CONCENTRACIÓN POR EVAPORACIÓN
Funcionalidad:
    Calcula la cantidad de disolución concentrada y de disolvente evaporado.
Para qué sirve:
    Para problemas en los que el soluto es no volátil y la corriente
    evaporada puede considerarse disolvente puro.
Cifras significativas:
    Los resultados se redondean automáticamente según la precisión
    de los datos introducidos.
```

## 8. Ayuda real de línea de comandos

La salida siguiente fue obtenida al ejecutar `--help` sobre este archivo, no deducida de la documentación del libro:

```text
usage: evaporacion.py [-h]

Balance de concentración de una disolución por evaporación.

options:
  -h, --help  show this help message and exit

Puede trabajar con kg o con kg/h, siempre que mantenga la misma base. Los
porcentajes se introducen como 20,0 para 20,0 %.
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

Caso de referencia: **100 kg de alimentación al 20 % y salida al 40 % ⇒ 50 kg de evaporado**. Balance de soluto y materia.

La prueba reproducible figura en `pruebas_revision/test_auditoria_integral.py`; los invariantes adicionales, cuando corresponden, están en `pruebas_revision/test_invariantes_cientificos.py`. Se trata de comprobaciones de casos seleccionados, no de una verificación exhaustiva del dominio del modelo.
