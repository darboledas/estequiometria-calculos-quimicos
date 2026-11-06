# Combustión y análisis de gases

**Manual de usuario · Capítulo 14 · combustion.py**  
**Proyecto:** *Estequiometría y cálculos químicos*. **Estado:** documentación preliminar basada en el código recibido (6 de noviembre de 2026).

## 1. Finalidad y funciones

Oxígeno estequiométrico, aire teórico y real, combustión completa/incompleta, análisis Orsat y cálculos inversos.

Esta herramienta automatiza el cálculo y ayuda a verificarlo, pero no sustituye la selección del modelo químico ni la interpretación de sus hipótesis.

## 2. Requisitos e instalación

Se recomienda **Python 3.10 o posterior**. En Windows, abra PowerShell o Símbolo del sistema, entre en la carpeta del capítulo y ejecute la aplicación. Ejemplo desde la carpeta raíz del repositorio:

```bat
cd capitulo_14
python combustion.py
```

El programa se basa en la biblioteca estándar de Python para el cálculo principal. Las dependencias de visualización, cuando existan, se detallan en su ayuda.

## 3. Comandos y opciones de ejecución

**Iniciar con menú o con preguntas sucesivas:**

```bat
python combustion.py
```

**Consultar las opciones admitidas:**

```bat
python combustion.py --help
```

**Ejemplo de uso o comprobación del propio programa:**

```bat
python combustion.py --self-test
```

`--self-test` ejecuta las comprobaciones internas; `--version` muestra la versión.

## 4. Menú principal y modos de cálculo

El menú mostrado por el programa, capturado durante esta revisión, ofrece las siguientes opciones:

```text
1. Oxígeno estequiométrico y aire/comburente teórico
2. Combustión completa con aire u otro comburente
3. Combustión de una mezcla de combustibles
4. Combustible de composición elemental conocida
5. Combustión incompleta
6. Análisis de gases de combustión / Orsat
7. Cálculo inverso a partir de un análisis gaseoso
8. Comprobación de un problema de combustión
9. Salir
```

## 5. Datos introducidos y unidades

El aire seco predeterminado se representa por 21,0 % molar de O₂ y 79,0 % de N₂; no hay cálculo energético.

Algunos de los campos, selecciones o preguntas definidos explícitamente en el código son:

- `Seleccione el comburente:`
- `Número total de componentes de la mezcla oxidante (incluido O2):`
- `¿Cómo se especifica el comburente real?`
- `Cantidad de combustible (mol o unidad molar coherente):`
- `Cantidad total de mezcla combustible (mol o unidad molar coherente):`
- `Número de componentes de la mezcla:`
- `Masa de combustible (g, kg u otra unidad de masa coherente):`
- `Número de elementos adicionales presentes (0 si no hay):`
- `Componentes inertes/cenizas (% en masa):`
- `Cantidad alimentada de combustible (mol):`
- `Conversión del combustible (%):`
- `Fracción del carbono REACCIONADO que forma CO2 (%):`
- `Suministro de comburente para la combustión incompleta:`
- `Base del análisis:`
- `Número de especies cuya composición se introducirá explícitamente:`
- `Modalidad:`
- `Oxígeno contenido en el combustible:`
- `Datos elementales disponibles:`
- `CO2 producido por mol de sustrato (mol/mol):`
- `O2 consumido por mol de sustrato (mol/mol):`
- `Número de átomos de H por molécula/unidad fórmula (y):`
- `Número de relaciones molares conocidas entre componentes (0 si no hay):`
- `Número de componentes combustibles candidatos:`
- `Número de magnitudes estequiométricas conocidas:`

La relación anterior es ilustrativa: ciertos campos solo aparecen al elegir subopciones.

## 6. Procedimiento recomendado paso a paso

1. Identifique en el capítulo el tipo de problema, las variables conocidas y las hipótesis necesarias.

2. Inicie el programa con `python combustion.py` desde la carpeta indicada.

3. Opción 1 para O₂ y aire teóricos, 5 para incompleta, 6 para análisis de gases y 8 para verificar balances.

4. Introduzca los datos conservando las unidades del programa y las cifras significativas correspondientes.

5. Revise las magnitudes calculadas y, cuando el modo lo permita, los residuos de balance, las composiciones y los avisos de validez.

6. Si el resultado es físicamente imposible, examine los datos y los supuestos antes de repetir el cálculo.

## 7. Resultados, verificaciones y alcance científico

Los resultados dependen de la modalidad elegida. Consulte el desarrollo técnico siguiente, extraído de la descripción que acompaña al código, para conocer el modelo que el autor ha implementado y sus limitaciones.

```text
TEMA 14 - COMBUSTIÓN Y ANÁLISIS DE GASES
Funcionalidad
Herramienta interactiva para resolver y comprobar los principales cálculos
estequiométricos del capítulo 14: oxígeno estequiométrico, aire teórico y real,
combustión completa e incompleta, mezclas de combustibles, combustibles de
composición elemental, composiciones de gases en base húmeda/seca, análisis
Orsat, cálculos inversos y comprobación de balances elementales.
Tipos de problemas que admite
1. Oxígeno estequiométrico y aire teórico para una sustancia de fórmula conocida.
2. Combustión completa de una sustancia con aire, O2 puro o mezcla oxidante.
3. Combustión completa de mezclas gaseosas, con componentes combustibles e inertes.
4. Combustibles especificados por composición elemental en masa.
5. Combustión incompleta de compuestos C/H/O con CO2, CO y combustible sin reaccionar.
6. Interpretación de análisis de gases, incluida una modalidad Orsat.
7. Cálculos inversos: H/C desde gases, mezcla binaria conocida y fórmula CHO.
8. Comprobación general de un problema mediante balances elementales.
Hipótesis y límites del modelo
- Es una aplicación ESTEQUIOMÉTRICA. No realiza balances de energía, equilibrio,
  cinética, disociación ni predicción de productos.
- El usuario debe indicar los productos cuando exista más de una posibilidad.
- En combustión completa, C -> CO2 y H -> H2O. Para S y N se solicita el modelo
  de productos si esos elementos están presentes.
- Para otros elementos, el cálculo directo permite definir un único óxido del
  elemento (producto formado solo por ese elemento y O). La opción 8, en cambio,
  comprueba balances con fórmulas químicas generales.
- Los componentes de una mezcla oxidante distintos de O2 se consideran portadores
  no reactivos y pasan a los productos sin transformación.
- No se fuerza una solución cuando faltan relaciones independientes o cuando los
  datos son incompatibles con el modelo elegido.
- El aire seco por defecto se representa como 21,0 % molar de O2 y 79,0 % de N2,
  de acuerdo con el modelo del capítulo.
Cifras significativas
Los cálculos internos NO se redondean. La salida numérica se redondea al final,
usando como criterio conservador el menor número de cifras significativas de los
DATOS MEDIDOS que intervienen en cada modalidad. Los coeficientes estequiométricos
enteros y las bases de cálculo elegidas automáticamente se consideran exactos.
La composición por defecto del aire (0,210/0,790) se considera un dato del modelo
con 3 cifras significativas y, por tanto, puede limitar la presentación de resultados.
Entrada decimal
Se acepta coma o punto decimal. Para evitar ambigüedades, los ceros escritos al
final de un número entero se consideran significativos (por ejemplo, "100" se
interpreta con 3 cifras significativas). Puede usarse notación científica.
```

## 8. Ayuda real de línea de comandos

La salida siguiente fue obtenida al ejecutar `--help` sobre este archivo, no deducida de la documentación del libro:

```text
usage: combustion.py [-h] [--self-test] [--version]

Aplicación didáctica del tema 14: combustión, aire y análisis de gases.

options:
  -h, --help   show this help message and exit
  --self-test  ejecuta una batería interna de comprobaciones numéricas y
               termina
  --version    show program's version number and exit

La ejecución normal es interactiva. Se aceptan coma y punto decimal. Los cálculos se realizan sin redondeos intermedios y los resultados se presentan con cifras significativas coherentes con los datos introducidos.
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

Comprobaciones internas: 23/23 correctas.

## 12. Correspondencia bibliográfica

Programa de apoyo al **capítulo 14** de *Estequiometría y cálculos químicos*. El texto del libro es una exposición científica; este manual explica la ejecución del software suministrado. El código y el manual se distribuyen bajo licencia MIT; el DOI específico del software se incorporará tras la primera publicación en Zenodo.
