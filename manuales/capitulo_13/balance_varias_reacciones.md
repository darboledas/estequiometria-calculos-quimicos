# Balance reactivo con varias reacciones

**Manual de usuario · Capítulo 13 · balance_varias_reacciones.py**  
**Proyecto:** *Estequiometría y cálculos químicos*. **Estado:** documentación preliminar basada en el código recibido (6 de noviembre de 2026).

## 1. Finalidad y funciones

Extensiones de reacción simultáneas, balances y composición final a partir de relaciones independientes.

Esta herramienta automatiza el cálculo y ayuda a verificarlo, pero no sustituye la selección del modelo químico ni la interpretación de sus hipótesis.

## 2. Requisitos e instalación

Se recomienda **Python 3.10 o posterior**. En Windows, abra PowerShell o Símbolo del sistema, entre en la carpeta del capítulo y ejecute la aplicación. Ejemplo desde la carpeta raíz del repositorio:

```bat
cd capitulo_13
python balance_varias_reacciones.py
```

Los dos programas del capítulo 13 utilizan `cap13_apoyo.py`; conserve **los tres archivos juntos** en su carpeta.

## 3. Comandos y opciones de ejecución

**Iniciar con menú o con preguntas sucesivas:**

```bat
python balance_varias_reacciones.py
```

**Consultar las opciones admitidas:**

```bat
python balance_varias_reacciones.py --help
```

**Ejemplo de uso o comprobación del propio programa:**

```bat
python balance_varias_reacciones.py
```

## 4. Menú principal y modos de cálculo

El menú mostrado por el programa, capturado durante esta revisión, ofrece las siguientes opciones:

```text
1. Resolver las extensiones y el balance
2. Comprobar cantidades o caudales finales obtenidos manualmente/experimentalmente
```

## 5. Datos introducidos y unidades

Las reacciones deben ser estequiométricamente independientes y los datos suficientes para resolver las extensiones.

Algunos de los campos, selecciones o preguntas definidos explícitamente en el código son:

- `Unidad de cantidad de sustancia:`
- `Unidad de tiempo:`
- `Número de reacciones independientes que desea introducir:`
- `Forma de introducir la estequiometría:`
- `Comprobación elemental:`
- `Comprobación de cierre másico:`
- `¿Desea aplicar una separación posterior sencilla por recuperación?`
- `Recuperación [%]:`
- `Tipo de uso:`
- `Tipo de sistema:`
- `Número de especies adicionales inertes/acompañantes:`
- `Número total de especies:`
- `Seleccione una relación adicional o termine:`
- `Conversión [%]:`
- `Escriba la unidad de cantidad:`
- `Escriba la unidad de tiempo:`
- `Fracción molar final (0 a 1):`
- `Definición de rendimiento:`
- `Rendimiento [%]:`

## 6. Procedimiento recomendado paso a paso

1. Identifique en el capítulo el tipo de problema, las variables conocidas y las hipótesis necesarias.

2. Inicie el programa con `python balance_varias_reacciones.py` desde la carpeta indicada.

3. Seleccione 1 para resolver extensiones o 2 para contrastar datos experimentales o manuales.

4. Introduzca los datos conservando las unidades del programa y las cifras significativas correspondientes.

5. Revise las magnitudes calculadas y, cuando el modo lo permita, los residuos de balance, las composiciones y los avisos de validez.

6. Si el resultado es físicamente imposible, examine los datos y los supuestos antes de repetir el cálculo.

## 7. Resultados, verificaciones y alcance científico

Los resultados dependen de la modalidad elegida. Consulte el desarrollo técnico siguiente, extraído de la descripción que acompaña al código, para conocer el modelo que el autor ha implementado y sus limitaciones.

```text
Script 13.2. Balance reactivo con varias reacciones
FUNCIONALIDAD
Herramienta interactiva para resolver y comprobar balances molares con varias
reacciones químicas independientes en:
- sistemas discontinuos cerrados;
- sistemas continuos en estado estacionario.
El programa asocia una extensión independiente a cada reacción y permite
determinar las extensiones a partir de relaciones químicamente interpretables:
- cantidades o caudales finales conocidos;
- conversiones de especies que solo se consumen;
- composiciones molares finales;
- cantidad o caudal molar total final;
- extensiones conocidas;
- selectividad entre cantidades netas formadas de dos productos;
- rendimiento de un producto respecto a un reactivo de referencia, con base
  en reactivo alimentado o consumido.
También:
- detecta reacciones estequiométricamente dependientes;
- detecta un número insuficiente de relaciones independientes;
- detecta especificaciones incompatibles con la precisión introducida;
- calcula la contribución de cada reacción a cada especie;
- calcula cantidades o caudales finales y composición molar;
- comprueba opcionalmente balances elementales y cierre másico;
- permite comprobar resultados manuales o experimentales;
- puede aplicar una separación posterior sencilla basada en recuperación.
TIPOS DE PROBLEMAS
- Varias reacciones simultáneas o sucesivas representadas globalmente.
- Una especie participante en varias reacciones.
- Determinación de varias extensiones mediante datos de especies,
  conversiones, composición, rendimiento o selectividad.
- Verificación de un conjunto completo de datos finales.
- Zona reactiva seguida de una separación sencilla por recuperación.
HIPÓTESIS Y LIMITACIONES
- Las reacciones deben estar correctamente ajustadas y ser
  estequiométricamente independientes.
- Los números estequiométricos son negativos para reactivos y positivos para
  productos. Una especie inerte tiene número estequiométrico cero en todas
  las reacciones.
- En sistemas continuos se usan caudales molares totales por especie a través
  de la frontera. Si existen varias corrientes, deben agregarse por especie.
- La conversión multirreacción solo se acepta para una especie que no se forme
  en ninguna de las reacciones introducidas.
- La selectividad implementada se define explícitamente como:
      S = cantidad neta formada de P1 / cantidad neta formada de P2
  y se restringe a especies que no se consumen en ninguna reacción.
- El rendimiento obliga a elegir su base: reactivo alimentado o consumido.
  El programa no supone silenciosamente una definición.
- La separación opcional supone que la corriente P contiene únicamente la
  especie recuperada; el resto permanece en la corriente residual L.
- No se calculan equilibrios, cinética, termodinámica ni mecanismos.
- Los coeficientes estequiométricos y números de átomos se consideran exactos.
- Las cifras significativas se propagan con las reglas usuales para las
  operaciones directas. En la resolución simultánea, las extensiones se
  presentan con la precisión más restrictiva de las relaciones independientes
  que determinan el sistema.
- Para declarar ceros finales significativos en enteros, use notación
  científica, por ejemplo 1,00e3.
Ayuda:
No requiere bibliotecas externas.
```

## 8. Ayuda real de línea de comandos

La salida siguiente fue obtenida al ejecutar `--help` sobre este archivo, no deducida de la documentación del libro:

```text
usage: balance_varias_reacciones.py [-h]

Resuelve o comprueba balances molares con varias reacciones
estequiométricamente independientes.

options:
  -h, --help  show this help message and exit

No requiere NumPy. Las relaciones se introducen mediante menús químicamente
interpretables.
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

En la revisión inicial hubo dos fallos de precisión; se ha corregido la precisión individual de las extensiones y se añadieron pruebas de regresión. Consulte `COMPROBACIONES.md` para reproducirlas.

## 12. Correspondencia bibliográfica

Programa de apoyo al **capítulo 13** de *Estequiometría y cálculos químicos*. El texto del libro es una exposición científica; este manual explica la ejecución del software suministrado. El código y el manual se distribuyen bajo licencia MIT; el DOI específico del software se incorporará tras la primera publicación en Zenodo.
