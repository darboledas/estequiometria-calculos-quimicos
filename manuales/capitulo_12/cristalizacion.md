# Cristalización por enfriamiento

**Manual de usuario · Capítulo 12 · cristalizacion.py**  
**Proyecto:** *Estequiometría y cálculos químicos*. **Estado:** documentación preliminar basada en el código recibido (6 de noviembre de 2026).

## 1. Finalidad y funciones

Masa de cristales puros y licor madre a partir de solubilidades inicial y final.

Esta herramienta automatiza el cálculo y ayuda a verificarlo, pero no sustituye la selección del modelo químico ni la interpretación de sus hipótesis.

## 2. Requisitos e instalación

Se recomienda **Python 3.10 o posterior**. En Windows, abra PowerShell o Símbolo del sistema, entre en la carpeta del capítulo y ejecute la aplicación. Ejemplo desde la carpeta raíz del repositorio:

```bat
cd capitulo_12
python cristalizacion.py
```

El programa se basa en la biblioteca estándar de Python para el cálculo principal. Las dependencias de visualización, cuando existan, se detallan en su ayuda.

## 3. Comandos y opciones de ejecución

**Iniciar con menú o con preguntas sucesivas:**

```bat
python cristalizacion.py
```

**Consultar las opciones admitidas:**

```bat
python cristalizacion.py --help
```

**Ejemplo de uso o comprobación del propio programa:**

```bat
python cristalizacion.py
```

## 4. Menú principal y modos de cálculo

**No hay un menú principal de opciones:** el programa guía al usuario mediante preguntas consecutivas o acepta argumentos al iniciarse. No debe confundirse la ausencia de menú con ausencia de controles de validación.

## 5. Datos introducidos y unidades

La disolución inicial y el licor madre final se consideran saturados; no se evapora disolvente.

Algunos de los campos, selecciones o preguntas definidos explícitamente en el código son:

- `Masa inicial de soluto [kg]:`
- `Solubilidad inicial [kg/100 kg disolvente]:`
- `Solubilidad final [kg/100 kg disolvente]:`

## 6. Procedimiento recomendado paso a paso

1. Identifique en el capítulo el tipo de problema, las variables conocidas y las hipótesis necesarias.

2. Inicie el programa con `python cristalizacion.py` desde la carpeta indicada.

3. Introduzca masa de soluto y solubilidades (kg de soluto/100 kg de disolvente).

4. Introduzca los datos conservando las unidades del programa y las cifras significativas correspondientes.

5. Revise las magnitudes calculadas y, cuando el modo lo permita, los residuos de balance, las composiciones y los avisos de validez.

6. Si el resultado es físicamente imposible, examine los datos y los supuestos antes de repetir el cálculo.

## 7. Resultados, verificaciones y alcance científico

Los resultados dependen de la modalidad elegida. Consulte el desarrollo técnico siguiente, extraído de la descripción que acompaña al código, para conocer el modelo que el autor ha implementado y sus limitaciones.

```text
SCRIPT 12.4. CRISTALIZACIÓN POR ENFRIAMIENTO
Funcionalidad:
    Calcula la masa de cristales y de licor madre obtenidos al enfriar
    una disolución inicialmente saturada.
Para qué sirve:
    Para problemas en los que las solubilidades se expresan como:
        kg de soluto / 100 kg de disolvente
    Hipótesis:
        - no se evapora disolvente;
        - los cristales son soluto puro;
        - la disolución inicial está saturada;
        - el licor madre queda saturado a la temperatura final.
Cifras significativas:
    Los resultados se redondean según la precisión de los datos introducidos.
```

## 8. Ayuda real de línea de comandos

La salida siguiente fue obtenida al ejecutar `--help` sobre este archivo, no deducida de la documentación del libro:

```text
usage: cristalizacion.py [-h]

Cristalización por enfriamiento a partir de datos de solubilidad.

options:
  -h, --help  show this help message and exit

Introduzca las solubilidades en kg de soluto por 100 kg de disolvente.
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
