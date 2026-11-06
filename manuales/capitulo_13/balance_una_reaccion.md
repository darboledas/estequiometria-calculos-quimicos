# Balance reactivo con una reacción

**Manual de usuario · Capítulo 13 · balance_una_reaccion.py**  
**Proyecto:** *Estequiometría y cálculos químicos*. **Estado:** documentación preliminar basada en el código recibido (6 de noviembre de 2026).

## 1. Finalidad y funciones

Resolución y verificación de balances molares con extensión o conversión para sistemas discontinuos o continuos.

Esta herramienta automatiza el cálculo y ayuda a verificarlo, pero no sustituye la selección del modelo químico ni la interpretación de sus hipótesis.

## 2. Requisitos e instalación

Se recomienda **Python 3.10 o posterior**. En Windows, abra PowerShell o Símbolo del sistema, entre en la carpeta del capítulo y ejecute la aplicación. Ejemplo desde la carpeta raíz del repositorio:

```bat
cd capitulo_13
python balance_una_reaccion.py
```

Los dos programas del capítulo 13 utilizan `cap13_apoyo.py`; conserve **los tres archivos juntos** en su carpeta.

## 3. Comandos y opciones de ejecución

**Iniciar con menú o con preguntas sucesivas:**

```bat
python balance_una_reaccion.py
```

**Consultar las opciones admitidas:**

```bat
python balance_una_reaccion.py --help
```

**Ejemplo de uso o comprobación del propio programa:**

```bat
python balance_una_reaccion.py
```

## 4. Menú principal y modos de cálculo

El menú mostrado por el programa, capturado durante esta revisión, ofrece las siguientes opciones:

```text
1. Resolver un balance
2. Comprobar resultados obtenidos manualmente o experimentalmente
```

## 5. Datos introducidos y unidades

La reacción debe estar ajustada; no se calculan cinética ni equilibrio ni se adivinan especies.

Algunos de los campos, selecciones o preguntas definidos explícitamente en el código son:

- `Seleccione cómo introducir la reacción:`
- `Unidad de cantidad de sustancia:`
- `Unidad de tiempo:`
- `Forma de introducir la alimentación/inventario inicial:`
- `Exceso del reactivo seleccionado [%]:`
- `Comprobación elemental:`
- `Comprobación de cierre másico:`
- `¿Desea aplicar una separación posterior sencilla por recuperación?`
- `Recuperación de esa especie [%]:`
- `Dato utilizado para determinar la extensión:`
- `Tipo de uso:`
- `Tipo de sistema:`
- `Número de especies adicionales inertes/acompañantes:`
- `Número total de especies (incluidos inertes si los hay):`
- `Conversión del reactivo [%]:`
- `Ecuación ajustada:`
- `Escriba la unidad de cantidad:`
- `Escriba la unidad de tiempo:`

## 6. Procedimiento recomendado paso a paso

1. Identifique en el capítulo el tipo de problema, las variables conocidas y las hipótesis necesarias.

2. Inicie el programa con `python balance_una_reaccion.py` desde la carpeta indicada.

3. Seleccione 1 para resolver y luego defina sistema, reacción y alimentación; opción 2 para comprobar resultados.

4. Introduzca los datos conservando las unidades del programa y las cifras significativas correspondientes.

5. Revise las magnitudes calculadas y, cuando el modo lo permita, los residuos de balance, las composiciones y los avisos de validez.

6. Si el resultado es físicamente imposible, examine los datos y los supuestos antes de repetir el cálculo.

## 7. Resultados, verificaciones y alcance científico

Los resultados dependen de la modalidad elegida. Consulte el desarrollo técnico siguiente, extraído de la descripción que acompaña al código, para conocer el modelo que el autor ha implementado y sus limitaciones.

```text
Script 13.1. Balance reactivo con una reacción
FUNCIONALIDAD
Herramienta interactiva para resolver y comprobar balances molares con una
única reacción química en:
- sistemas discontinuos cerrados;
- sistemas continuos en estado estacionario.
Puede determinar la extensión de reacción (xi) o la velocidad de extensión
(xi_dot) a partir de:
- una extensión conocida;
- una conversión conocida de un reactivo;
- una cantidad o caudal final conocido de una especie.
También permite:
- calcular cantidades o caudales finales;
- calcular cantidades consumidas o formadas;
- obtener la composición molar final;
- comprobar la consistencia de resultados calculados manualmente;
- comprobar opcionalmente balances elementales y cierre másico;
- aplicar, de forma opcional, una separación posterior sencilla basada en la
  recuperación de una especie.
TIPOS DE PROBLEMAS
- Una reacción en un sistema discontinuo.
- Una reacción en un sistema continuo estacionario.
- Alimentación conocida directamente o con un reactivo alimentado en exceso.
- Resolución mediante extensión, conversión o un dato final.
- Verificación de un conjunto completo de cantidades o caudales finales.
- Reactor seguido de una separación simple con recuperación de una especie.
HIPÓTESIS Y LIMITACIONES
- La reacción debe estar correctamente ajustada.
- Los números estequiométricos son negativos para reactivos y positivos para
  productos; una especie inerte tiene número estequiométrico cero.
- En sistemas continuos se trabaja con los caudales molares totales que
  atraviesan la frontera considerada. Si hay varias corrientes de entrada o de
  salida, deben sumarse previamente por especie.
- La separación opcional supone que la corriente de producto recuperado
  contiene únicamente la especie seleccionada; el resto de las especies y la
  fracción no recuperada permanecen en la corriente residual.
- No se calculan equilibrios, cinética, termodinámica ni mecanismos.
- Los coeficientes estequiométricos y los números de átomos se consideran
  exactos.
- Las cifras significativas se propagan con las reglas usuales: en sumas y
  restas limita la posición decimal menos precisa; en productos y cocientes
  limita el menor número de cifras significativas. Los ceros que representan
  ausencia exacta de una especie no limitan la precisión.
- Para expresar ceros finales significativos en enteros, use notación
  científica (por ejemplo, 1,00e3).
Ejecución interactiva:
Ayuda:
```

## 8. Ayuda real de línea de comandos

La salida siguiente fue obtenida al ejecutar `--help` sobre este archivo, no deducida de la documentación del libro:

```text
usage: balance_una_reaccion.py [-h]

Resuelve o comprueba balances de materia con una única reacción en sistemas
discontinuos o continuos estacionarios.

options:
  -h, --help  show this help message and exit

Las entradas se realizan interactivamente. Use coma o punto decimal. Los
coeficientes estequiométricos se consideran exactos.
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

En la revisión inicial hubo dos fallos relacionados con precisión individual; la implementación ha sido corregida y vuelta a comprobar. Consulte `COMPROBACIONES.md`.

## 12. Correspondencia bibliográfica

Programa de apoyo al **capítulo 13** de *Estequiometría y cálculos químicos*. El texto del libro es una exposición científica; este manual explica la ejecución del software suministrado. El código y el manual se distribuyen bajo licencia MIT; el DOI específico del software se incorporará tras la primera publicación en Zenodo.
