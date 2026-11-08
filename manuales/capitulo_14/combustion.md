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

Programa de apoyo al **capítulo 14** de *Estequiometría y cálculos químicos*. El texto del libro es una exposición científica; este manual explica la ejecución del software suministrado. El código y el manual se distribuyen bajo licencia MIT; DOI general del software: [10.5281/zenodo.24020474](https://doi.org/10.5281/zenodo.24020474). DOI de la versión publicada 0.9.0: [10.5281/zenodo.24020473](https://doi.org/10.5281/zenodo.24020473). DOI del libro: [10.5281/zenodo.24013068](https://doi.org/10.5281/zenodo.24013068).


## Comprobación independiente de revisión integral

Caso de referencia: **CH₄ + 2 O₂ → CO₂ + 2 H₂O**. Balance elemental de C, H y O y oxígeno teórico.

La prueba reproducible figura en `pruebas_revision/test_auditoria_integral.py`; los invariantes adicionales, cuando corresponden, están en `pruebas_revision/test_invariantes_cientificos.py`. Se trata de comprobaciones de casos seleccionados, no de una verificación exhaustiva del dominio del modelo.


## Revisión adicional de balances y combustión — 7 de noviembre de 2026

### Contrastes inversos y fórmulas químicas

El analizador de fórmulas rechaza grupos vacíos (`Fe()2`), subíndices nulos (`CH0`) y paréntesis desequilibrados. Sigue admitiendo fórmulas con paréntesis válidos, como `Ca(OH)2`.

En la modalidad inversa para mezclas conocidas se comprueba un caso sintético: **2 mol de CH₄ y 3 mol de C₂H₆** producen, en combustión completa, **8 mol de CO₂ y 13 mol de H₂O**, y consumen **14,5 mol de O₂**. El programa recupera las dos cantidades de combustible a partir de los dos observables independientes. Con un solo observable el problema queda indeterminado, y el programa no debe asignar arbitrariamente una solución.

El solucionador inverso escala ahora cada ecuación antes de la eliminación de Gauss-Jordan. Esto evita que caudales pequeños, por ejemplo del orden de `1e-12 mol`, se descarten debido a una tolerancia absoluta del sistema. Este escalado no resuelve la falta de identificabilidad ni los problemas mal condicionados: esos casos necesitan más datos o una evaluación numérica específica.

```powershell
python capitulo_14/combustion.py --self-test
python -m unittest discover -s pruebas_revision -p test_balances_combustion_ampliada.py -v
```

## Ampliación: invariancia de escala de combustión (7 de noviembre de 2026)

Se revisaron umbrales absolutos que omitían especies gaseosas y cantidades estequiométricas de O₂ cuando la base del problema era muy pequeña. Ahora se conservan las especies con cantidades estrictamente positivas, se rechazan cantidades negativas o no finitas y el cierre elemental utiliza tolerancia relativa (sin suelo numérico de 1 mol). La validación de entradas también impide cantidades negativas próximas a cero. La combustión completa no se acepta con un defecto real de O₂ solo porque su cantidad absoluta sea pequeña.

**Contrastes analíticos:** por mol de CH₄, 2 mol de O₂ producen 1 mol de CO₂ y 2 de H₂O; por mol de CH₄O, se requieren 1,5 mol de O₂. Para C₂H₆S se obtienen 4,5 mol de O₂ con SO₂ o 5 mol con SO₃. Para C₂H₅N se requieren, respectivamente, 3,25, 3,75 o 4,25 mol de O₂ cuando todo el nitrógeno origina N₂, NO o NO₂. Se han repetido algunos balances con base de 10⁻¹² mol para comprobar que la escala no cambia las proporciones.

Estos ejemplos **son balances estequiométricos con productos impuestos**, no predicciones de formación de NOₓ o SOₓ. La selección del mecanismo, los equilibrios y la cinética quedan fuera del modelo.

```powershell
python -m unittest discover -s pruebas_revision -p test_escalas_y_productos_combustion.py -v
python capitulo_14/combustion.py --self-test
```


## Contraste adicional de combustión incompleta e inversiones (revisión 7 de noviembre de 2026)

La revisión de la opción **5. Combustión incompleta** ha eliminado umbrales absolutos que ocultaban especies positivas, excedentes de O₂ y fracciones no reaccionadas cuando se utilizaban bases pequeñas. El programa muestra las cantidades positivas mediante notación científica y exige suficiente oxígeno para las cantidades de CO₂, CO y H₂O que el usuario haya impuesto. No determina por sí mismo la distribución real de productos.

**Ejemplo reproducible:** 1 mol de CH₄, conversión 80 %, reparto del carbono reaccionado 75 % a CO₂ y 25 % a CO, con 1,8 mol de O₂ puro. Se obtiene: CH₄ no convertido 0,2 mol; CO₂ 0,6 mol; CO 0,2 mol; H₂O 1,6 mol; O₂ de salida 0,3 mol. El porcentaje molar de CO₂ en base seca es 46,1538… %. El balance elemental cierra y los resultados se escalan proporcionalmente para 10⁻¹² mol de alimentación.

El modo inverso binario distingue cantidades pequeñas de cero y rechaza soluciones negativas; la modalidad de combustible puro requiere una necesidad estequiométrica de oxígeno estrictamente positiva para calcular el factor de aire. Los cálculos multicomponente se han contrastado con observables derivados de composiciones conocidas y con 150 sistemas sintéticos de cuatro componentes, con relaciones molares suficientes para obtener solución única.

```powershell
python -m unittest pruebas_revision.test_combustion_incompleta_inversos -v
python capitulo_14/combustion.py --self-test
```

Los detalles, resultados y límites del contraste figuran en `REVISIONES/INFORME_COMBUSTION_INCOMPLETA_INVERSOS.md`. Las 16 pruebas nuevas han resultado correctas localmente. El código no predice cinética, equilibrio, temperatura adiabática ni formación de NOₓ/SOₓ.


## Anexo: fiabilidad de los cálculos inversos (revisión local, 7-11-2026)

El cálculo inverso de la opción 7 utiliza un solucionador con equilibrado por filas y columnas y pivoteo completo. Ante observables prácticamente dependientes o con escalas incompatibles muestra un error de **sistema mal condicionado** en lugar de presentar una composición no fiable. Es diferente de un sistema exactamente indeterminado o de un conjunto incompatible.

Ejemplo: las ecuaciones `n1+n2=2` y `n1+1,000000001*n2=2,000000001` tienen solución algebraica (1,1). Una perturbación de 10⁻⁸ en el segundo dato modifica radicalmente las cantidades deducidas. No debe interpretarse una salida exacta del solucionador como certeza experimental.

Las salvaguardas son heurísticas (pivotes relativos `10⁻⁸`; escala de columnas `10⁹`), no un cálculo del número de condición ni de la incertidumbre de datos. Si se recibe el mensaje, aporte observables físicamente independientes, mejore la precisión o utilice un tratamiento especializado.

Comprobación local: `python -m unittest discover -s pruebas_revision -p test_estabilidad_inversos_empiricos.py -v`. La revisión todavía no se ha publicado en GitHub.
