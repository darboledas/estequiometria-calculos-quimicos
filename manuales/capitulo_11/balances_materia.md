# Fundamentos de balances de materia

**Manual de usuario · Capítulo 11 · balances_materia.py**  
**Proyecto:** *Estequiometría y cálculos químicos*. **Estado:** documentación preliminar basada en el código recibido (6 de noviembre de 2026).

## 1. Finalidad y funciones

Balances globales y de componente, redes de equipos, mezclas, acumulación y transitorios con entrada JSON opcional.

Esta herramienta automatiza el cálculo y ayuda a verificarlo, pero no sustituye la selección del modelo químico ni la interpretación de sus hipótesis.

## 2. Requisitos e instalación

Se recomienda **Python 3.10 o posterior**. En Windows, abra PowerShell o Símbolo del sistema, entre en la carpeta del capítulo y ejecute la aplicación. Ejemplo desde la carpeta raíz del repositorio:

```bat
cd capitulo_11
python balances_materia.py
```

**Gráficos:** requieren `matplotlib` (instalable con `python -m pip install matplotlib`). Los cálculos no gráficos pueden tener menos dependencias.

## 3. Comandos y opciones de ejecución

**Iniciar con menú o con preguntas sucesivas:**

```bat
python balances_materia.py
```

**Consultar las opciones admitidas:**

```bat
python balances_materia.py --help
```

**Ejemplo de uso o comprobación del propio programa:**

```bat
python balances_materia.py --red ejemplos/red_mezclador.json
```

La aplicación acepta casos `--red`, `--mezcla` o `--transitorio` desde JSON; admite asimismo `--salida` y `--grafica`. Consulte su ayuda para conocer las combinaciones admitidas.

## 4. Menú principal y modos de cálculo

El menú mostrado por el programa, capturado durante esta revisión, ofrece las siguientes opciones:

```text
1 Caudales, gases y composiciones
2 Balance total e inventario | 3 Balance de componente
4 Solucionador general de redes y grados de libertad
5 Preparación de mezclas por concentraciones
6 Acumulación, transitorios y gráficas
7 Residuos y cierre | 8 Ayuda | 0 Salir
```

## 5. Datos introducidos y unidades

No resuelve energía, cinética ni equilibrio; una red debe tener suficientes restricciones independientes.

Algunos de los campos, selecciones o preguntas definidos explícitamente en el código son:

- `Opción`
- `Caudales de entrada [kg/h]`
- `Caudales de salida [kg/h]`
- `Tiempo de operación [h]`
- `Inventario inicial [kg]`
- `Caudal del componente de entrada [kg/h o mol/h]`
- `Caudal del componente de salida [misma unidad]`
- `Generación [misma unidad]`
- `Consumo [misma unidad]`
- `Volumen final [L]`
- `Caudales de entrada [misma unidad]`
- `Caudales de salida [misma unidad]`
- `Caudal de referencia positivo [misma unidad]`
- `Tolerancia absoluta aceptable`
- `Precisión no especificada por ceros enteros: indique cifras significativas`
- `Caudal másico [kg/h]`
- `Densidad [kg/m3]`
- `Masa molar [kg/kmol] (pura o MEDIA para mezcla)`
- `Acumulación conocida [misma unidad]`
- `Ruta al JSON del problema`
- `Base (mass/molar)`
- `Número de solutos`
- `Número de corrientes de alimentación (incluya agua)`
- `Concentración de cada alimentación [g/L o mol/L]`

La relación anterior es ilustrativa: ciertos campos solo aparecen al elegir subopciones.

## 6. Procedimiento recomendado paso a paso

1. Identifique en el capítulo el tipo de problema, las variables conocidas y las hipótesis necesarias.

2. Inicie el programa con `python balances_materia.py` desde la carpeta indicada.

3. Seleccione 4 para redes de corrientes; opcionalmente cargue un ejemplo JSON desde la línea de comandos.

4. Introduzca los datos conservando las unidades del programa y las cifras significativas correspondientes.

5. Revise las magnitudes calculadas y, cuando el modo lo permita, los residuos de balance, las composiciones y los avisos de validez.

6. Si el resultado es físicamente imposible, examine los datos y los supuestos antes de repetir el cálculo.

## 7. Resultados, verificaciones y alcance científico

Los resultados dependen de la modalidad elegida. Consulte el desarrollo técnico siguiente, extraído de la descripción que acompaña al código, para conocer el modelo que el autor ha implementado y sus limitaciones.

```text
Capítulo 11 · Fundamentos de balances de materia.
Programa interactivo y utilidades importables. Python >=3.10.
El motor del balance es independiente de NumPy/SciPy. Matplotlib es opcional.
No resuelve energía, cinética ni equilibrio químico.
```

## 8. Ayuda real de línea de comandos

La salida siguiente fue obtenida al ejecutar `--help` sobre este archivo, no deducida de la documentación del libro:

```text
usage: balances_materia.py [-h] [--red ARCHIVO.json] [--mezcla ARCHIVO.json]
                           [--transitorio ARCHIVO.json]
                           [--tolerancia TOLERANCIA] [--max-pasos MAX_PASOS]
                           [--salida SALIDA] [--grafica GRAFICA] [--version]

Capítulo 11: balances de materia; menú interactivo o JSON.

options:
  -h, --help            show this help message and exit
  --red ARCHIVO.json    Resuelve una red estacionaria descrita en JSON
  --mezcla ARCHIVO.json
                        Resuelve volúmenes de mezcla por concentraciones
  --transitorio ARCHIVO.json
                        Integra un depósito agitado por RK4 adaptativo
  --tolerancia TOLERANCIA
                        Tolerancia numérica
  --max-pasos MAX_PASOS
                        Límite de iteraciones de integración
  --salida SALIDA       Guardar resultado en archivo JSON o CSV (transitorios)
  --grafica GRAFICA     Crear gráfica PNG (solo transitorios)
  --version             show program's version number and exit
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

Archivo de pruebas del capítulo 11: 58 pruebas correctas.

## 12. Correspondencia bibliográfica

Programa de apoyo al **capítulo 11** de *Estequiometría y cálculos químicos*. El texto del libro es una exposición científica; este manual explica la ejecución del software suministrado. El código y el manual se distribuyen bajo licencia MIT; el DOI específico del software se incorporará tras la primera publicación en Zenodo.
