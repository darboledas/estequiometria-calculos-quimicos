# Capítulo 8 — Herramientas de cálculo del capítulo 8

Programas de apoyo a *Estequiometría y cálculos químicos*.

## Programas

- `disoluciones_no_ideales.py`: calculos capitulo 8.

## Instalación y uso

Se recomienda Python 3.10 o posterior. Desde esta carpeta, ejecutar:

```bash
python disoluciones_no_ideales.py
```

Para los demás programas, sustituir el nombre del archivo por el indicado en la lista.

Algunos módulos requieren paquetes adicionales para cálculos matriciales o gráficos (por ejemplo, `numpy`, `scipy` o `matplotlib`). Consultar las instrucciones de cada programa y verificar las dependencias antes de utilizarlo.

Se admiten las unidades indicadas en cada menú. Comprobar especialmente las cifras significativas y las hipótesis físicas de cada modelo.

## Material complementario

Los directorios `ejemplos`, `muestras` y `pruebas`, cuando existan, contienen recursos auxiliares y no constituyen programas adicionales del alumnado. En el capítulo 13, `cap13_apoyo.py` es una dependencia compartida que debe permanecer junto a los dos programas.

## Referencia y licencia

Código y documentación de este repositorio: **licencia MIT** (`../LICENSE`). DOI general del software: **10.5281/zenodo.24020474**; DOI de la versión 0.9.0: **10.5281/zenodo.24020473**. DOI del libro relacionado: **10.5281/zenodo.24013068**.


### Validación adicional de las fuentes de presión de vapor (bloque VII)

`DirectPsat`, `SimpleExpPsat` y `AntoinePsat` rechazan datos `NaN`, infinitos, presiones no positivas, series de distinta longitud y desbordamientos. `AntoinePsat` exige indicar la escala de temperatura en `C` o `K`. No se cambia la fórmula de los modelos ni su rango experimental de validez: estos controles evitan resultados indefinidos, pero **no** garantizan que las constantes ajustadas sean adecuadas para otra sustancia o intervalo.

Referencias reproducibles: ejercicios **8.B.8** y **8.B.11** (rocío con Margules). El test se ejecuta desde la raíz:

```bash
python -m unittest discover -s pruebas_revision -p test_cotejo_bloque_07.py -v
```
