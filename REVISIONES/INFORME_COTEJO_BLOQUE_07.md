# Bloque VII — nuevos casos del libro y seguridad numérica del capítulo 8

**7 de noviembre de 2026. Copia de trabajo local; no publicada.**

## Resultado medido

- **29/29** métodos nuevos superados: **26 ejercicios** del libro y **3 pruebas de rechazo de datos físicamente inválidos**.
- **374/374** métodos transversales acumulados, `unittest discover` con Python local.
- Ejercicios distintos acumulados con algún contraste **188/556**; quedan **368** sin cotejo individual.
- Todas las pruebas específicas existentes de los capítulos 9, 10, 11, 13, 14 y 15 ejecutadas sin fallos. Compilación de los capítulos 2–15 superada.
- Las cifras de contraste numérico provienen del solucionario, comprobadas con funciones del programa o balances algebraicos independientes según se indica en la matriz.

## Incidencia corregida en el programa

`capitulo_08/disoluciones_no_ideales.py`: `DirectPsat`, `SimpleExpPsat`, `AntoinePsat` permiten antes transmitir presiones indefinidas al cálculo VLE. Se añaden comprobaciones de valores finitos, longitudes coincidentes, presión positiva, escala `C`/`K` válida, desbordamiento y singularidades. Las entradas físicas anteriores conservan su resultado. Los ejercicios **8.B.8 y 8.B.11** han sido recalculados mediante los solvers existentes (P_roc≈89,3067 kPa; T_roc≈342,0731 K).

## Incidencia editorial en el solucionario

El apartado **5.B.6** imprime incorrectamente la ecuación polinómica de la virial de tercer orden. El resultado final sí coincide con la cúbica bien formulada. Véase `ERRATAS_SOLUCIONARIO_PENDIENTES.md`. No se altera el original.

## Matriz de los 26 ejercicios nuevos

| Ejercicio | Página PDF del libro | Tipo de cotejo |
|---|---:|---|
| 2.B.6 | 97 | cálculo algebraico y conversión mediante programa |
| 3.B.14 | 159 | masa molar del programa + cálculo algebraico |
| 3.B.15 | 159 | ajuste químico y balance de reactivo limitante |
| 4.B.7 | 190 | ley de gases ideales + balance Dalton |
| 4.C.10 | 193 | gas ideal mediante programa + balance de absorción auxiliar |
| 4.C.11 | 193 | gas ideal mediante programa + balance de absorción auxiliar |
| 5.B.6 | 247 | virial de tercer orden: función del programa y residuo polinómico independiente |
| 5.B.7 | 247 | cálculo de parámetros vdW desde constantes incorporadas; álgebra auxiliar |
| 5.B.12 | 248 | Lee–Kesler: propiedades críticas explícitas |
| 5.B.16 | 249 | vdW con parámetros explícitos: estado y fugacidad |
| 5.B.20 | 249 | extremos vdW: derivación y raíces polinómicas auxiliares; no interfaz directa |
| 6.B.8 | 292 | Antoine e inventario de gas ideal |
| 6.B.12 | 293 | Clausius–Clapeyron directo e inversión de temperatura |
| 6.C.2 | 294 | Antoine: inversión y cierre de presión |
| 7.B.6 | 359 | Raoult directo, ocho filas y suma de fracciones |
| 7.B.7 | 359 | volatilidad relativa: relación algebraica auxiliar |
| 7.B.8 | 359 | Antoine + Raoult, malla 41 composiciones y puntos puros |
| 8.B.8 | 458 | rocío Margules: iteración real del programa |
| 8.B.11 | 459 | rocío térmico: correlación exponencial e iteración real |
| 10.B.5 | 587 | composición molar y descenso Raoult, funciones directas |
| 10.B.7 | 588 | fuerza iónica y coeficiente medio Debye–Hückel/Davies directos |
| 11.B.9 | 659 | balance de disolución con cierre de materia |
| 11.B.10 | 659 | solución de dos ecuaciones de balance, función lineal |
| 12.B.10 | 713 | palanca con dos balances lineales, función del programa |
| 14.B.11 | 808 | combustión incompleta: balance elemental auxiliar + cierre del programa |
| 14.B.13 | 808 | Orsat: base seca mediante programa + relación de aire auxiliar |

## Reproducción

```powershell
python -m unittest discover -s pruebas_revision -p test_cotejo_bloque_07.py -v
python -m unittest discover -s pruebas_revision -p "test_*.py" -q
python -m compileall -q capitulo_02 capitulo_03 capitulo_04 capitulo_05 capitulo_06 capitulo_07 capitulo_08 capitulo_09 capitulo_10 capitulo_11 capitulo_12 capitulo_13 capitulo_14 capitulo_15
```

La matriz contiene el identificador exacto de prueba, la página y el tipo de intervención. No equivale a certificar todo el software. Las pruebas que incluyen balances auxiliares no implican existencia de un modo único de menú para ese ejercicio. Quedan pendientes verificaciones adicionales y una ejecución independiente del CI en los entornos de publicación antes de la versión v1.0.0.
