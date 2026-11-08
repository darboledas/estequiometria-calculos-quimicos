# Equilibrio líquido–líquido

**Manual de usuario · Capítulo 9 · equilibrio_liquido_liquido.py**  
**Proyecto:** *Estequiometría y cálculos químicos*. **Estado:** documentación preliminar basada en el código recibido (6 de noviembre de 2026).

## 1. Finalidad y funciones

Conversión entre bases másica/molar, regla de palanca, binodales tabuladas, modelo de Gibbs y gráficas UCST/LCST.

Esta herramienta automatiza el cálculo y ayuda a verificarlo, pero no sustituye la selección del modelo químico ni la interpretación de sus hipótesis.

## 2. Requisitos e instalación

Se recomienda **Python 3.10 o posterior**. En Windows, abra PowerShell o Símbolo del sistema, entre en la carpeta del capítulo y ejecute la aplicación. Ejemplo desde la carpeta raíz del repositorio:

```bat
cd capitulo_09
python equilibrio_liquido_liquido.py
```

**Gráficos:** requieren `matplotlib` (instalable con `python -m pip install matplotlib`). Los cálculos no gráficos pueden tener menos dependencias.

## 3. Comandos y opciones de ejecución

**Iniciar con menú o con preguntas sucesivas:**

```bat
python equilibrio_liquido_liquido.py
```

**Consultar la ayuda:** use la opción 7 del menú. Este archivo no implementa una orden independiente `--help`.

**Ejemplo de uso o comprobación del propio programa:**

```bat
python equilibrio_liquido_liquido.py
```

## 4. Menú principal y modos de cálculo

El menú mostrado por el programa, capturado durante esta revisión, ofrece las siguientes opciones:

```text
1  Conversión fracción másica ↔ molar
2  Regla de la palanca y balances L1/L2
3  Correlación de Beysens y masas de fases (con gráfica)
4  Binodal tabulada en CSV: interpolación, balances y gráfica
5  Modelo teórico de Gibbs: binodal, espinodal y gráfica
6  Gráficas cualitativas UCST / LCST / región cerrada
7  Ayuda / alcance científico
0  Salir
```

## 5. Datos introducidos y unidades

Es necesario distinguir fracción molar y másica; para binodales tabuladas use el CSV con estructura requerida.

Algunos de los campos, selecciones o preguntas definidos explícitamente en el código son:

- `binodal_beysens`
- `binodal_datos`
- `gibbs_regular`
- `tipos_binodal_esquema`
- `Seleccione:`
- `Selección [1]:`
- `Masa molar de A (g/mol):`
- `Masa molar de B (g/mol):`
- `Fracción de A:`
- `Composición global A (misma base):`
- `Composición de A en L1 (normalmente rica en A):`
- `Composición de A en L2 (normalmente pobre en A):`
- `Distancia reducida ε:`
- `Masa alimentación (kg), o 0 para omitir:`
- `B [1,83]:`
- `β [0,318]:`
- `w_c [0,5350]:`
- `Fracción másica GLOBAL de isooctano:`
- `T crítica superior (K), 0 si no se conoce:`
- `Composición global de A (misma base que CSV):`
- `Cantidad total (0 para no calcular masas/moles):`
- `Base de los datos: kg, g, mol o kmol [kg]:`
- `Parámetro adimensional χ (mayor que 2):`
- `Introducir [m] fracción másica o [x] fracción molar de A [m]:`

La relación anterior es ilustrativa: ciertos campos solo aparecen al elegir subopciones.

## 6. Procedimiento recomendado paso a paso

1. Identifique en el capítulo el tipo de problema, las variables conocidas y las hipótesis necesarias.

2. Inicie el programa con `python equilibrio_liquido_liquido.py` desde la carpeta indicada.

3. Seleccione 2 para balances entre fases, 4 para datos CSV y 5 para un modelo teórico de binodal.

4. Introduzca los datos conservando las unidades del programa y las cifras significativas correspondientes.

5. Revise las magnitudes calculadas y, cuando el modo lo permita, los residuos de balance, las composiciones y los avisos de validez.

6. Si el resultado es físicamente imposible, examine los datos y los supuestos antes de repetir el cálculo.

## 7. Resultados, verificaciones y alcance científico

Los resultados dependen de la modalidad elegida. Consulte el desarrollo técnico siguiente, extraído de la descripción que acompaña al código, para conocer el modelo que el autor ha implementado y sus limitaciones.

```text
Capítulo 9. Equilibrio líquido–líquido. Python 3.10+; matplotlib para gráficos.
Todas las funciones de cálculo devuelven valores SIN redondear: el redondeo
se reserva para la presentación. L1 y L2 son las fases parcialmente miscibles.
```

## 8. Ayuda real de línea de comandos

Estos dos programas no implementan un analizador de argumentos: `--help` inicia el menú ordinario, no una pantalla de ayuda especial. La salida capturada fue:

```text
CAPÍTULO 9 — EQUILIBRIO LÍQUIDO–LÍQUIDO
1  Conversión fracción másica ↔ molar
2  Regla de la palanca y balances L1/L2
3  Correlación de Beysens y masas de fases (con gráfica)
4  Binodal tabulada en CSV: interpolación, balances y gráfica
5  Modelo teórico de Gibbs: binodal, espinodal y gráfica
6  Gráficas cualitativas UCST / LCST / región cerrada
7  Ayuda / alcance científico
0  Salir
Seleccione:   Opción inexistente.

CAPÍTULO 9 — EQUILIBRIO LÍQUIDO–LÍQUIDO
1  Conversión fracción másica ↔ molar
2  Regla de la palanca y balances L1/L2
3  Correlación de Beysens y masas de fases (con gráfica)
4  Binodal tabulada en CSV: interpolación, balances y gráfica
5  Modelo teórico de Gibbs: binodal, espinodal y gráfica
6  Gráficas cualitativas UCST / LCST / región cerrada
7  Ayuda / alcance científico
0  Salir
Seleccione: 
  Interrumpido por el usuario.
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

El archivo de pruebas del capítulo 9 superó 24 pruebas; comprueba ambos programas del capítulo.

## 12. Correspondencia bibliográfica

Programa de apoyo al **capítulo 9** de *Estequiometría y cálculos químicos*. El texto del libro es una exposición científica; este manual explica la ejecución del software suministrado. El código y el manual se distribuyen bajo licencia MIT; DOI general del software: [10.5281/zenodo.24020474](https://doi.org/10.5281/zenodo.24020474). DOI de la versión publicada 0.9.0: [10.5281/zenodo.24020473](https://doi.org/10.5281/zenodo.24020473). DOI del libro: [10.5281/zenodo.24013068](https://doi.org/10.5281/zenodo.24013068).


## Comprobación independiente de revisión integral

Caso de referencia: **Regla de la palanca: z = 0,5, extremos 0,2 y 0,8, total 10 ⇒ L₁ = L₂ = 5**. Cierres total y de componente.

La prueba reproducible figura en `pruebas_revision/test_auditoria_integral.py`; los invariantes adicionales, cuando corresponden, están en `pruebas_revision/test_invariantes_cientificos.py`. Se trata de comprobaciones de casos seleccionados, no de una verificación exhaustiva del dominio del modelo.
