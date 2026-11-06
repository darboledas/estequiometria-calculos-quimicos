# Inmiscibles y arrastre de vapor

**Manual de usuario · Capítulo 9 · inmiscibles_y_arrastre_vapor.py**  
**Proyecto:** *Estequiometría y cálculos químicos*. **Estado:** documentación preliminar basada en el código recibido (6 de noviembre de 2026).

## 1. Finalidad y funciones

Equilibrio de dos fases líquidas inmiscibles con vapor, condición trifásica y balances de arrastre.

Esta herramienta automatiza el cálculo y ayuda a verificarlo, pero no sustituye la selección del modelo químico ni la interpretación de sus hipótesis.

## 2. Requisitos e instalación

Se recomienda **Python 3.10 o posterior**. En Windows, abra PowerShell o Símbolo del sistema, entre en la carpeta del capítulo y ejecute la aplicación. Ejemplo desde la carpeta raíz del repositorio:

```bat
cd capitulo_09
python inmiscibles_y_arrastre_vapor.py
```

**Gráficos:** requieren `matplotlib` (instalable con `python -m pip install matplotlib`). Los cálculos no gráficos pueden tener menos dependencias.

## 3. Comandos y opciones de ejecución

**Iniciar con menú o con preguntas sucesivas:**

```bat
python inmiscibles_y_arrastre_vapor.py
```

**Consultar la ayuda:** use la opción 9 del menú. Este archivo no implementa una orden independiente `--help`.

**Ejemplo de uso o comprobación del propio programa:**

```bat
python inmiscibles_y_arrastre_vapor.py
```

## 4. Menú principal y modos de cálculo

El menú mostrado por el programa, capturado durante esta revisión, ofrece las siguientes opciones:

```text
1  Presiones de vapor a temperatura dada (gráfica disponible)
2  Temperatura trifásica iterativa y composición del vapor (gráfica)
3  Composición a partir de una relación másica (ejercicio B.9)
4  Consumo teórico de agua para arrastre (masas y relaciones)
5  Agotamiento de las fases en destilación discontinua
6  Condensador / decantador / reflujo
7  Comparar dos presiones o sistemas (gráfica T*–P)
8  Diagrama T–composición de líquidos inmiscibles
9  Ayuda, hipótesis y validez
0  Salir
```

## 5. Datos introducidos y unidades

Vapor ideal y presencia simultánea de dos fases líquidas; el régimen posterior al agotamiento no queda completamente modelizado.

Algunos de los campos, selecciones o preguntas definidos explícitamente en el código son:

- `Presión total:`
- `Antoine A:`
- `Antoine B (>0):`
- `Antoine C:`
- `Masa molar (g/mol):`
- `T min válida K (0 si no se conoce):`
- `T max válida K (0 si no se conoce):`
- `Tolerancia de resolución en T (K) [introduzca p.ej. 0,000001]:`
- `Máximo de iteraciones [p.ej. 250]:`
- `presiones_inmiscibles`
- `temperatura_presion`
- `diagrama_inmiscibles_Tx`
- `Opción:`
- `Nombre:`
- `Opción [1]:`
- `Destino [1]:`
- `Temperatura (K):`
- `Seleccione:`
- `Unidad [kPa/bar/Pa/atm/torr] (kPa):`
- `Relación másica m_B/m_A:`
- `M_A (g/mol):`
- `M_B (g/mol):`
- `Masa de producto B que se desea arrastrar:`
- `Cantidad inicial del líquido A:`

La relación anterior es ilustrativa: ciertos campos solo aparecen al elegir subopciones.

## 6. Procedimiento recomendado paso a paso

1. Identifique en el capítulo el tipo de problema, las variables conocidas y las hipótesis necesarias.

2. Inicie el programa con `python inmiscibles_y_arrastre_vapor.py` desde la carpeta indicada.

3. Elija 2 para temperatura trifásica o 4 para consumo teórico de agua; elija 9 para validez.

4. Introduzca los datos conservando las unidades del programa y las cifras significativas correspondientes.

5. Revise las magnitudes calculadas y, cuando el modo lo permita, los residuos de balance, las composiciones y los avisos de validez.

6. Si el resultado es físicamente imposible, examine los datos y los supuestos antes de repetir el cálculo.

## 7. Resultados, verificaciones y alcance científico

Los resultados dependen de la modalidad elegida. Consulte el desarrollo técnico siguiente, extraído de la descripción que acompaña al código, para conocer el modelo que el autor ha implementado y sus limitaciones.

```text
Capítulo 9. Equilibrio LA + LB + V y destilación por arrastre de vapor.
Hipótesis: líquidos prácticamente inmiscibles, vapor ideal y equilibrio a
P y T comunes, CON LAS DOS fases líquidas presentes. No representa un
modelo completo para el régimen posterior al agotamiento de una fase.
Los cálculos internos no se redondean; solo la presentación al alumno.
Python 3.10+. Matplotlib solo es necesario cuando se solicita una gráfica.
```

## 8. Ayuda real de línea de comandos

Estos dos programas no implementan un analizador de argumentos: `--help` inicia el menú ordinario, no una pantalla de ayuda especial. La salida capturada fue:

```text
CAPÍTULO 9 — INMISCIBLES Y ARRASTRE DE VAPOR
1  Presiones de vapor a temperatura dada (gráfica disponible)
2  Temperatura trifásica iterativa y composición del vapor (gráfica)
3  Composición a partir de una relación másica (ejercicio B.9)
4  Consumo teórico de agua para arrastre (masas y relaciones)
5  Agotamiento de las fases en destilación discontinua
6  Condensador / decantador / reflujo
7  Comparar dos presiones o sistemas (gráfica T*–P)
8  Diagrama T–composición de líquidos inmiscibles
9  Ayuda, hipótesis y validez
0  Salir
Seleccione:   Opción inexistente.

CAPÍTULO 9 — INMISCIBLES Y ARRASTRE DE VAPOR
1  Presiones de vapor a temperatura dada (gráfica disponible)
2  Temperatura trifásica iterativa y composición del vapor (gráfica)
3  Composición a partir de una relación másica (ejercicio B.9)
4  Consumo teórico de agua para arrastre (masas y relaciones)
5  Agotamiento de las fases en destilación discontinua
6  Condensador / decantador / reflujo
7  Comparar dos presiones o sistemas (gráfica T*–P)
8  Diagrama T–composición de líquidos inmiscibles
9  Ayuda, hipótesis y validez
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

Programa de apoyo al **capítulo 9** de *Estequiometría y cálculos químicos*. El texto del libro es una exposición científica; este manual explica la ejecución del software suministrado. El código y el manual se distribuyen bajo licencia MIT; el DOI específico del software se incorporará tras la primera publicación en Zenodo.
