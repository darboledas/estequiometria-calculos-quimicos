# Propiedades coligativas

**Manual de usuario · Capítulo 10 · propiedades_coligativas.py**  
**Proyecto:** *Estequiometría y cálculos químicos*. **Estado:** documentación preliminar basada en el código recibido (6 de noviembre de 2026).

## 1. Finalidad y funciones

Composición de disoluciones, Raoult, ebulloscopia, crioscopia, presión osmótica y van ’t Hoff.

Esta herramienta automatiza el cálculo y ayuda a verificarlo, pero no sustituye la selección del modelo químico ni la interpretación de sus hipótesis.

## 2. Requisitos e instalación

Se recomienda **Python 3.10 o posterior**. En Windows, abra PowerShell o Símbolo del sistema, entre en la carpeta del capítulo y ejecute la aplicación. Ejemplo desde la carpeta raíz del repositorio:

```bat
cd capitulo_10
python propiedades_coligativas.py
```

**Gráficos:** requieren `matplotlib` (instalable con `python -m pip install matplotlib`). Los cálculos no gráficos pueden tener menos dependencias.

## 3. Comandos y opciones de ejecución

**Iniciar con menú o con preguntas sucesivas:**

```bat
python propiedades_coligativas.py
```

**Consultar las opciones admitidas:**

```bat
python propiedades_coligativas.py --help
```

**Ejemplo de uso o comprobación del propio programa:**

```bat
python propiedades_coligativas.py --selftest
```

## 4. Menú principal y modos de cálculo

El menú mostrado por el programa, capturado durante esta revisión, ofrece las siguientes opciones:

```text
1. Composición (x, n, molalidad, molaridad)
2. Presión de vapor y ley de Raoult
3. Ebulloscopía
4. Crioscopía
5. Presión osmótica y osmolaridad
6. Factor de van t Hoff, disociación y asociación
7. Ajuste de datos osmóticos y extrapolación
8. Generar gráficos y CSV
9. Ejecutar pruebas del capítulo
0. Salir
```

## 5. Datos introducidos y unidades

Los modelos ideales son aproximaciones explícitas y no garantizan resultados experimentales.

Algunos de los campos, selecciones o preguntas definidos explícitamente en el código son:

- `Masa de soluto (g)`
- `Masa molar del soluto (g/mol)`
- `Masa de disolvente (g)`
- `Masa molar del disolvente (g/mol)`
- `Temperatura de cambio de fase del disolvente puro (K)`
- `Masa molar disolvente (kg/mol)`
- `Entalpía molar de cambio de fase (J/mol)`
- `Constante ebulloscópica/crioscópica K (K kg/mol)`
- `Factor de van t Hoff i (1 si no hay asociación/disociación)`
- `Temperatura (°C; no inferior a -273,15)`
- `Grado del polinomio [0=ideal, 1 o 2]`
- `Número de medidas`
- `Temperatura (°C)`
- `Volumen de disolución (L)`
- `Masa soluto (g)`
- `Masa molar soluto (g/mol)`
- `Masa disolvente (g)`
- `Masa molar disolvente (g/mol)`
- `Presión de vapor del disolvente puro (kPa)`
- `Variación experimental ΔT (K)`
- `Molalidad (mol/kg)`
- `T* del disolvente puro (°C; se admiten negativos)`
- `Diferencia de presión positiva (bar)`
- `Densidad aproximada (kg/m³)`

La relación anterior es ilustrativa: ciertos campos solo aparecen al elegir subopciones.

## 6. Procedimiento recomendado paso a paso

1. Identifique en el capítulo el tipo de problema, las variables conocidas y las hipótesis necesarias.

2. Inicie el programa con `python propiedades_coligativas.py` desde la carpeta indicada.

3. Seleccione 2 para presión de vapor, 3–4 para cambios de temperatura o 5 para ósmosis.

4. Introduzca los datos conservando las unidades del programa y las cifras significativas correspondientes.

5. Revise las magnitudes calculadas y, cuando el modo lo permita, los residuos de balance, las composiciones y los avisos de validez.

6. Si el resultado es físicamente imposible, examine los datos y los supuestos antes de repetir el cálculo.

## 7. Resultados, verificaciones y alcance científico

Los resultados dependen de la modalidad elegida. Consulte el desarrollo técnico siguiente, extraído de la descripción que acompaña al código, para conocer el modelo que el autor ha implementado y sus limitaciones.

```text
Capítulo 10. Propiedades coligativas: menú, cálculos, gráficos y pruebas.
Python >= 3.10. Matplotlib solo para gráficos. Sin dependencias numéricas.
Las cifras significativas se aplican AL FINAL de los cálculos.
Los modelos ideales no representan automáticamente valores experimentales.
```

## 8. Ayuda real de línea de comandos

La salida siguiente fue obtenida al ejecutar `--help` sobre este archivo, no deducida de la documentación del libro:

```text
usage: propiedades_coligativas.py [-h] [--selftest]

Capítulo 10. Propiedades coligativas: menú, cálculos, gráficos y pruebas.
Python >= 3.10. Matplotlib solo para gráficos. Sin dependencias numéricas. Las
cifras significativas se aplican AL FINAL de los cálculos. Los modelos ideales
no representan automáticamente valores experimentales.

options:
  -h, --help  show this help message and exit
  --selftest  Verificar resultados sin entrar al menú
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

Autoensayo: 38/38 comprobaciones correctas.

## 12. Correspondencia bibliográfica

Programa de apoyo al **capítulo 10** de *Estequiometría y cálculos químicos*. El texto del libro es una exposición científica; este manual explica la ejecución del software suministrado. El código y el manual se distribuyen bajo licencia MIT; el DOI específico del software se incorporará tras la primera publicación en Zenodo.
