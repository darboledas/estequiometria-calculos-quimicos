# Disoluciones electrolíticas

**Manual de usuario · Capítulo 10 · disoluciones_electroliticas.py**  
**Proyecto:** *Estequiometría y cálculos químicos*. **Estado:** documentación preliminar basada en el código recibido (6 de noviembre de 2026).

## 1. Finalidad y funciones

Composición iónica, electroneutralidad, fuerza iónica, Debye–Hückel, Davies, SIT y Pitzer simplificados.

Esta herramienta automatiza el cálculo y ayuda a verificarlo, pero no sustituye la selección del modelo químico ni la interpretación de sus hipótesis.

## 2. Requisitos e instalación

Se recomienda **Python 3.10 o posterior**. En Windows, abra PowerShell o Símbolo del sistema, entre en la carpeta del capítulo y ejecute la aplicación. Ejemplo desde la carpeta raíz del repositorio:

```bat
cd capitulo_10
python disoluciones_electroliticas.py
```

Mantenga `propiedades_coligativas.py` en la **misma carpeta**; se importa como módulo auxiliar. Para generar gráficos se necesita Matplotlib.

## 3. Comandos y opciones de ejecución

**Iniciar con menú o con preguntas sucesivas:**

```bat
python disoluciones_electroliticas.py
```

**Consultar las opciones admitidas:**

```bat
python disoluciones_electroliticas.py --help
```

**Ejemplo de uso o comprobación del propio programa:**

```bat
python disoluciones_electroliticas.py --selftest
```

## 4. Menú principal y modos de cálculo

El menú mostrado por el programa, capturado durante esta revisión, ofrece las siguientes opciones:

```text
1. Composición iónica, electroneutralidad y fuerza iónica
2. Actividad individual DH límite / extendida / Davies
3. Molalidad, actividad y coeficiente IÓNICOS MEDIOS
4. SIT simplificado con parámetros aportados
5. Pitzer simplificado con parámetros aportados
6. Despeje ITERATIVO de fuerza iónica desde γ objetivo
7. Gráficos y CSV (incluido cotejo con datos importados)
8. Pruebas numéricas de los ejemplos del capítulo
9. Aplicaciones integradas: agua de mar, formulaciones y eritrocitos
0. Salir
```

## 5. Datos introducidos y unidades

Los coeficientes individuales de actividad son convencionales; algunos modelos necesitan parámetros externos.

Algunos de los campos, selecciones o preguntas definidos explícitamente en el código son:

- `Coeficiente estequiométrico del ion`
- `Número de especies iónicas presentes`
- `Número de tipos de iones generados por la fórmula`
- `Valor absoluto de carga |z|`
- `Fuerza iónica MOLAL I (mol/kg)`
- `ν+ cationes por unidad fórmula`
- `z+ (módulo positivo)`
- `ν- aniones por unidad fórmula`
- `Molalidad FORMAL de la sal (mol/kg)`
- `Carga absoluta del ion objetivo`
- `I MOLAL (mol/kg)`
- `Número de especies k consideradas para interacciones específicas`
- `β^(0) (parámetro específico, kg/mol)`
- `β^(1) (parámetro específico, kg/mol)`
- `α de Pitzer (no grado de disociación; usualmente 2,0)`
- `Molalidad formal (mol/kg)`
- `Gamma_i objetivo (0 < gamma < 1)`
- `Extremo inferior de I (mol/kg; admite 0)`
- `Extremo superior de I (mol/kg)`
- `Tolerancia absoluta en I (mol/kg)`
- `Iteraciones máximas`
- `Molalidad formal del electrolito (mol/kg disolvente)`
- `Coeficiente gamma_i > 0`
- `Molalidad del ion (mol/kg)`

La relación anterior es ilustrativa: ciertos campos solo aparecen al elegir subopciones.

## 6. Procedimiento recomendado paso a paso

1. Identifique en el capítulo el tipo de problema, las variables conocidas y las hipótesis necesarias.

2. Inicie el programa con `python disoluciones_electroliticas.py` desde la carpeta indicada.

3. Opción 1 para composición y fuerza iónica; 2 para DH/Davies; 4–5 para SIT/Pitzer.

4. Introduzca los datos conservando las unidades del programa y las cifras significativas correspondientes.

5. Revise las magnitudes calculadas y, cuando el modo lo permita, los residuos de balance, las composiciones y los avisos de validez.

6. Si el resultado es físicamente imposible, examine los datos y los supuestos antes de repetir el cálculo.

## 7. Resultados, verificaciones y alcance científico

Los resultados dependen de la modalidad elegida. Consulte el desarrollo técnico siguiente, extraído de la descripción que acompaña al código, para conocer el modelo que el autor ha implementado y sus limitaciones.

```text
Capítulo 10. Iones, fuerza iónica y modelos de actividad (menú y autoensayos).
REQUIERE que propiedades_coligativas.py esté en la MISMA carpeta.
Los coeficientes individuales de actividad son CONVENCIONALES (no medibles
independientemente). SIT/Pitzer requieren parámetros externos identificados.
```

## 8. Ayuda real de línea de comandos

La salida siguiente fue obtenida al ejecutar `--help` sobre este archivo, no deducida de la documentación del libro:

```text
usage: disoluciones_electroliticas.py [-h] [--selftest]

Capítulo 10. Iones, fuerza iónica y modelos de actividad (menú y autoensayos).
REQUIERE que propiedades_coligativas.py esté en la MISMA carpeta. Los
coeficientes individuales de actividad son CONVENCIONALES (no medibles
independientemente). SIT/Pitzer requieren parámetros externos identificados.

options:
  -h, --help  show this help message and exit
  --selftest  Ejecutar verificación automática y salir
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

Autoensayo: 39/39 comprobaciones correctas.

## 12. Correspondencia bibliográfica

Programa de apoyo al **capítulo 10** de *Estequiometría y cálculos químicos*. El texto del libro es una exposición científica; este manual explica la ejecución del software suministrado. El código y el manual se distribuyen bajo licencia MIT; DOI general del software: [10.5281/zenodo.24020474](https://doi.org/10.5281/zenodo.24020474). DOI de la versión publicada 0.9.0: [10.5281/zenodo.24020473](https://doi.org/10.5281/zenodo.24020473). DOI del libro: [10.5281/zenodo.24013068](https://doi.org/10.5281/zenodo.24013068).


## Comprobación independiente de revisión integral

Caso de referencia: **NaCl 0,1 mol/kg idealmente disociado ⇒ I = 0,1 mol/kg**. Fuerza iónica calculada con z².

La prueba reproducible figura en `pruebas_revision/test_auditoria_integral.py`; los invariantes adicionales, cuando corresponden, están en `pruebas_revision/test_invariantes_cientificos.py`. Se trata de comprobaciones de casos seleccionados, no de una verificación exhaustiva del dominio del modelo.
