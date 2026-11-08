# Capítulo 6 — Presión de vapor y propiedades del vapor de agua

Programas de apoyo a *Estequiometría y cálculos químicos*.

## Programas

- `presion_vapor.py`: presion vapor.
- `vapor_agua.py`: vapor agua.

## Instalación y uso

Se recomienda Python 3.10 o posterior. Desde esta carpeta, ejecutar:

```bash
python presion_vapor.py
```

Para los demás programas, sustituir el nombre del archivo por el indicado en la lista.

Algunos módulos requieren paquetes adicionales para cálculos matriciales o gráficos (por ejemplo, `numpy`, `scipy` o `matplotlib`). Consultar las instrucciones de cada programa y verificar las dependencias antes de utilizarlo.

Se admiten las unidades indicadas en cada menú. Comprobar especialmente las cifras significativas y las hipótesis físicas de cada modelo.

## Material complementario

Los directorios `ejemplos`, `muestras` y `pruebas`, cuando existan, contienen recursos auxiliares y no constituyen programas adicionales del alumnado. En el capítulo 13, `cap13_apoyo.py` es una dependencia compartida que debe permanecer junto a los dos programas.

## Referencia y licencia

Código y documentación de este repositorio: **licencia MIT** (`../LICENSE`). DOI general del software: **10.5281/zenodo.24020474**; DOI de la versión 0.9.0: **10.5281/zenodo.24020473**. DOI del libro relacionado: **10.5281/zenodo.24013068**.


## Nota de validación local: títulos de vapor (7-11-2026)

`vapor_agua.py`: al calcular el título a partir de volumen, entalpía o entropía de saturación, la propiedad y las referencias `f` y `g` deben ser finitas. Valores `NaN` e infinitos se rechazan. Valores finitos que conduzcan a un título fuera de `[0, 1]` indican que el estado no pertenece a la región bifásica y se explican en la salida. El caso 6.C.9 (entalpía 2400 kJ/kg, referencias 417,5 y 2675,5 kJ/kg) produce `x=0,877989`.

Pruebas: `python -m unittest discover -s pruebas_revision -p test_cotejo_aplicados_04.py -v` desde la raíz.
