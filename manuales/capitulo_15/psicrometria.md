# Aire húmedo y psicrometría

**Manual de usuario · Capítulo 15 · psicrometria.py**  
**Proyecto:** *Estequiometría y cálculos químicos*. **Estado:** documentación preliminar basada en el código recibido (6 de noviembre de 2026).

## 1. Finalidad y funciones

Estados a partir de dos propiedades, punto de rocío, bulbo húmedo, procesos, mezcla y cartas calculadas.

Esta herramienta automatiza el cálculo y ayuda a verificarlo, pero no sustituye la selección del modelo químico ni la interpretación de sus hipótesis.

## 2. Requisitos e instalación

Se recomienda **Python 3.10 o posterior**. En Windows, abra PowerShell o Símbolo del sistema, entre en la carpeta del capítulo y ejecute la aplicación. Ejemplo desde la carpeta raíz del repositorio:

```bat
cd capitulo_15
python psicrometria.py
```

**Gráficos:** requieren `matplotlib` (instalable con `python -m pip install matplotlib`). Los cálculos no gráficos pueden tener menos dependencias.

## 3. Comandos y opciones de ejecución

**Iniciar con menú o con preguntas sucesivas:**

```bat
python psicrometria.py
```

**Consultar las opciones admitidas:**

```bat
python psicrometria.py --help
```

**Ejemplo de uso o comprobación del propio programa:**

```bat
python psicrometria.py --validar
```

`--validar` ejecuta las verificaciones numéricas y físicas internas y termina sin abrir el menú.

## 4. Menú principal y modos de cálculo

El menú mostrado por el programa, capturado durante esta revisión, ofrece las siguientes opciones:

```text
1. Caracterización completa de un estado
2. Cálculo directo de una propiedad
3. Punto de rocío y comienzo de la condensación
4. Calentamiento/enfriamiento a omega constante
5. Enfriamiento con condensación
6. Humidificación
7. Mezcla de dos corrientes de aire húmedo
8. Generación de una carta psicrométrica
9. Localización de un estado sobre la carta
10. Representación de procesos sobre la carta
11. Comparación de varios estados
12. Sistemas gas–vapor distintos del aire–agua
13. Comprobar mis resultados
14. Figuras didácticas y construcción de la carta
15. Configurar precisión de cálculo iterativo
0. Salir
```

## 5. Datos introducidos y unidades

El módulo usa la correlación ASHRAE/Hyland–Wexler en el intervalo documentado; la salida gráfica especifica PNG a 400 ppp.

Algunos de los campos, selecciones o preguntas definidos explícitamente en el código son:

- `Selección:`
- `Seleccione:`
- `¿Mostrar la secuencia de cálculo?`
- `Caudal de aire seco 1 [kg/s, kg/h, ...]:`
- `Caudal de aire seco 2 [misma unidad]:`
- `¿Representar los tres estados sobre una carta?`
- `Número de estados a comparar [2-10]:`
- `¿Exportar la tabla a CSV?`
- `¿Representar los estados en una misma carta?`
- `Masa molar del gas no condensable [g/mol]:`
- `Masa molar del vapor [g/mol]:`
- `Temperatura [°C]:`
- `T_bs [°C]:`
- `T_bh [°C]:`
- `T_rocío [°C]:`
- `Humedad relativa phi [%]:`
- `Razón de humedad omega [kg/kg aire seco]:`
- `Entalpía h [kJ/kg aire seco]:`
- `Volumen específico v [m³/kg aire seco]:`
- `Seleccione el par de entrada:`
- `P*_v [kPa]:`
- `phi [%]:`
- `Propiedad:`
- `Seleccione una opción:`

La relación anterior es ilustrativa: ciertos campos solo aparecen al elegir subopciones.

## 6. Procedimiento recomendado paso a paso

1. Identifique en el capítulo el tipo de problema, las variables conocidas y las hipótesis necesarias.

2. Inicie el programa con `python psicrometria.py` desde la carpeta indicada.

3. Opción 1 para caracterizar el estado; 8 para una carta; 11 para comparar estados y 13 para comprobación del alumno.

4. Introduzca los datos conservando las unidades del programa y las cifras significativas correspondientes.

5. Revise las magnitudes calculadas y, cuando el modo lo permita, los residuos de balance, las composiciones y los avisos de validez.

6. Si el resultado es físicamente imposible, examine los datos y los supuestos antes de repetir el cálculo.

## 7. Resultados, verificaciones y alcance científico

Los resultados dependen de la modalidad elegida. Consulte el desarrollo técnico siguiente, extraído de la descripción que acompaña al código, para conocer el modelo que el autor ha implementado y sus limitaciones.

```text
Capítulo 15 — Aire húmedo y psicrometría
Aplicación didáctica e interactiva para cálculos psicrométricos.
Finalidad
- Caracterizar estados de aire húmedo a partir de dos propiedades independientes.
- Calcular propiedades psicrométricas, punto de rocío y temperatura de bulbo húmedo.
- Estudiar calentamiento/enfriamiento, condensación, humidificación y mezcla.
- Generar cartas psicrométricas calculadas numéricamente, sin usar una imagen de fondo.
- Localizar estados y representar procesos sobre la carta.
- Comparar varios estados y exportarlos a CSV.
- Resolver, en un modo separado, sistemas gas–vapor distintos del aire–agua.
Hipótesis y unidades
- Aire húmedo tratado como mezcla ideal de aire seco y vapor de agua.
- Presión total en kPa; temperaturas en °C.
- Razón de humedad omega en kg H2O/kg de aire seco.
- Entalpía en kJ/kg de aire seco.
- Volumen específico en m³/kg de aire seco.
- Para aire–agua se usa la correlación de presión de vapor de saturación adoptada por
  ASHRAE (forma Hyland-Wexler), válida aquí entre -100 °C y 200 °C. El cambio
  entre las expresiones para hielo y agua líquida se realiza en el punto triple
  (0,01 °C), evitando la pequeña discontinuidad que aparecería al invertirlas en 0 °C.
- La temperatura de bulbo húmedo se obtiene con la relación psicrométrica de ASHRAE
  y, cuando es implícita, mediante bisección.
- Las expresiones de entalpía y volumen específico son las habituales para aire húmedo.
Control de cifras significativas
Los datos de medida se leen primero como texto. Así se distingue, por ejemplo, entre
30, 30,0 y 30,00. Las constantes internas y los coeficientes de correlación no limitan
las cifras significativas. Los cálculos se realizan con precisión de coma flotante y el
redondeo se aplica solo al presentar los resultados.
Dependencias
- Python 3.10 o posterior.
- matplotlib únicamente para los modos gráficos. El resto del programa funciona sin él.
```

## 8. Ayuda real de línea de comandos

La salida siguiente fue obtenida al ejecutar `--help` sobre este archivo, no deducida de la documentación del libro:

```text
usage: psicrometria.py [-h] [--validar]

Aplicación didáctica para aire húmedo y psicrometría. Calcula estados, procesos, mezclas y cartas psicrométricas con control de cifras significativas.

options:
  -h, --help  show this help message and exit
  --validar   Ejecuta pruebas internas numéricas y físicas y sale

Modos interactivos:
   1 caracterización completa; 2 propiedad directa; 3 punto de rocío;
   4 calentamiento/enfriamiento a omega constante; 5 condensación;
   6 humidificación; 7 mezcla; 8 generar carta; 9 localizar estado;
  10 representar procesos; 11 comparar estados; 12 gas-vapor general;
  13 comprobar resultados del alumno; 14 figuras didácticas por etapas;
   15 tolerancia y máximo de iteraciones.

Propiedades de entrada admitidas para un estado aire–agua:
  T_bs + phi, T_bs + omega, T_bs + T_bh, T_bs + T_rocío,
  T_bs + h, T_bs + v, phi + omega, phi + T_rocío.

Unidades:
  P en kPa; T en °C; omega en kg H2O/kg aire seco;
  h en kJ/kg aire seco; v en m³/kg aire seco; phi en %.

Modelo:
  Mezcla ideal aire seco–vapor de agua. Presión de saturación ASHRAE/Hyland-Wexler
  entre -100 y 200 °C. En los modos gráficos, matplotlib es obligatorio.

Gráficos:
  PNG a 400 ppp, PDF y SVG vectoriales. La carta se calcula numéricamente y puede
  incluir saturación, humedad relativa, T_bh, T_rocío, entalpía y volumen específico.

Cifras significativas:
  Los datos se leen como texto; 30, 30,0 y 30,00 no tienen la misma precisión.
  El redondeo se aplica solo a la salida. Punto y coma decimal están admitidos.
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

Validación interna: 12 grupos correctos.

**Discrepancia editorial:** el texto preliminar del libro habla de PNG a 300 ppp y doce modos; la ayuda del script declara PNG a 400 ppp y quince modos. Se debe armonizar antes de publicar.

## 12. Correspondencia bibliográfica

Programa de apoyo al **capítulo 15** de *Estequiometría y cálculos químicos*. El texto del libro es una exposición científica; este manual explica la ejecución del software suministrado. El código y el manual se distribuyen bajo licencia MIT; el DOI específico del software se incorporará tras la primera publicación en Zenodo.
