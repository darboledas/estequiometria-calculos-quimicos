# Masa molar de compuestos químicos

**Manual de usuario · Capítulo 3 · masa_molar.py**  
**Proyecto:** *Estequiometría y cálculos químicos*. **Estado:** documentación preliminar basada en el código recibido (6 de noviembre de 2026).

## 1. Finalidad y funciones

Interpretación de fórmulas químicas con paréntesis, corchetes e hidratos y suma de contribuciones atómicas.

Esta herramienta automatiza el cálculo y ayuda a verificarlo, pero no sustituye la selección del modelo químico ni la interpretación de sus hipótesis.

## 2. Requisitos e instalación

Se recomienda **Python 3.10 o posterior**. En Windows, abra PowerShell o Símbolo del sistema, entre en la carpeta del capítulo y ejecute la aplicación. Ejemplo desde la carpeta raíz del repositorio:

```bat
cd capitulo_03
python masa_molar.py
```

El programa se basa en la biblioteca estándar de Python para el cálculo principal. Las dependencias de visualización, cuando existan, se detallan en su ayuda.

## 3. Comandos y opciones de ejecución

**Iniciar con menú o con preguntas sucesivas:**

```bat
python masa_molar.py
```

**Consultar las opciones admitidas:**

```bat
python masa_molar.py --help
```

**Ejemplo de uso o comprobación del propio programa:**

```bat
python masa_molar.py "Al2(SO4)3" --detalles
```

El comando anterior calcula una fórmula concreta y añade el desglose elemental. También existen `--fuentes` y `--elementos`.

## 4. Menú principal y modos de cálculo

**No hay un menú principal de opciones:** el programa guía al usuario mediante preguntas consecutivas o acepta argumentos al iniciarse. No debe confundirse la ausencia de menú con ausencia de controles de validación.

## 5. Datos introducidos y unidades

Resultado en g/mol; las masas atómicas tabuladas se fundamentan en valores representativos de CIAAW citados en el código.

Algunos de los campos, selecciones o preguntas definidos explícitamente en el código son:

- `Fórmula química [Enter para salir]:`

## 6. Procedimiento recomendado paso a paso

1. Identifique en el capítulo el tipo de problema, las variables conocidas y las hipótesis necesarias.

2. Inicie el programa con `python masa_molar.py` desde la carpeta indicada.

3. Introduzca una fórmula química al iniciarse la aplicación o pásela como argumento de línea de comandos.

4. Introduzca los datos conservando las unidades del programa y las cifras significativas correspondientes.

5. Revise las magnitudes calculadas y, cuando el modo lo permita, los residuos de balance, las composiciones y los avisos de validez.

6. Si el resultado es físicamente imposible, examine los datos y los supuestos antes de repetir el cálculo.

## 7. Resultados, verificaciones y alcance científico

Los resultados dependen de la modalidad elegida. Consulte el desarrollo técnico siguiente, extraído de la descripción que acompaña al código, para conocer el modelo que el autor ha implementado y sus limitaciones.

```text
Calcula la masa molar a partir de una fórmula química, por ejemplo:
    Al2(SO4)3
    Ca(OH)2
    K4[Fe(CN)6]
    CuSO4·5H2O
    Al₂(SO₄)₃
FUENTES DE LOS DATOS
1) CIAAW — Commission on Isotopic Abundances and Atomic Weights:
   "Standard Atomic Weights 2024".
2) Para elementos sin peso atómico estándar, se usa únicamente como valor
   representativo el número másico entre corchetes que figura en la tabla
   IUPAC de pesos atómicos:
IMPORTANTE: los números entre corchetes NO son pesos atómicos estándar.
Si una fórmula contiene alguno de esos elementos, el programa lo advierte.
CRITERIO DE REDONDEO
- Los subíndices estequiométricos son números exactos.
- El cálculo interno se realiza con Decimal, sin redondeos intermedios.
- Para los pesos atómicos estándar se conservan también los márgenes ± de la
  tabla abreviada CIAAW. Se calcula un margen total conservador sumando
  linealmente n_i·u_i; no se interpreta como una incertidumbre estándar
  estadística. La masa se redondea a la misma posición decimal que ese margen.
- El margen se expresa con una cifra significativa, o con dos cuando comienza
  por 1 o 2.
- Para elementos representados únicamente por un número másico entero, el
  resultado se redondea a unidades y se emite una advertencia.
FUNCIONALIDAD
- Paréntesis, corchetes y llaves anidados.
- Hidratos/aductos con punto medio o punto: CuSO4·5H2O o CuSO4.5H2O.
- Coeficientes enteros delante de un término.
- Subíndices Unicode.
- Comprobación de símbolos químicos.
- Salida con coma decimal.
- Modo interactivo y línea de comandos.
- --help, --detalles, --fuentes y --elementos.
No admite notación isotópica explícita ni notación de carga iónica ambigua.
```

## 8. Ayuda real de línea de comandos

La salida siguiente fue obtenida al ejecutar `--help` sobre este archivo, no deducida de la documentación del libro:

```text
usage: masa_molar.py [-h] [--detalles] [--fuentes] [--elementos] [formula]

Calcula la masa molar de una fórmula química usando los pesos atómicos
estándar abreviados CIAAW 2024.

positional arguments:
  formula      Fórmula química, por ejemplo "Al2(SO4)3".

options:
  -h, --help   show this help message and exit
  --detalles   Muestra el recuento de átomos y las contribuciones elementales.
  --fuentes    Muestra las fuentes de los datos.
  --elementos  Muestra el diccionario de valores atómicos usado.
```

## 9. Submenús y opciones internas

Los submenús se muestran dentro del programa al seleccionar las opciones principales. Para la versión documentada no se ha observado una interfaz independiente de subcomandos.

## 10. Errores frecuentes y precauciones

- Ejecutar el archivo desde otra carpeta y no encontrar módulos auxiliares, tablas, ejemplos o rutas relativas.

- Mezclar unidades o bases de composición, o confundir fracciones con porcentajes.

- Utilizar ecuaciones o correlaciones fuera del intervalo para el que están previstas.

- Interpretar la precisión mostrada como una garantía experimental o física.

- Dar por único un problema con datos insuficientes o hipótesis no justificadas.

## 11. Ejemplo numérico verificado

Con el comando concreto del apartado 3 se obtuvo la siguiente salida, seleccionada literalmente entre los resultados de la ejecución real (el resto de la salida puede incluir más datos):

```text
Fórmula: Al2(SO4)3
Masa molar: 342,13 g·mol⁻¹
```

## 12. Estado de revisión

Inicio y ayuda revisados; no se ha ejecutado una batería de casos numéricos exhaustiva para esta aplicación.

**Inventario:** el `INVENTARIO.md` recibido omitía este archivo; se incorpora a la relación corregida.

## 13. Correspondencia bibliográfica

Programa de apoyo al **capítulo 3** de *Estequiometría y cálculos químicos*. El texto del libro es una exposición científica; este manual explica la ejecución del software suministrado. El código y el manual se distribuyen bajo licencia MIT; el DOI específico del software se incorporará tras la primera publicación en Zenodo.
