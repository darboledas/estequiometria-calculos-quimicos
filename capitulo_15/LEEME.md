# Capítulo 15 — Gases húmedos y psicrometría

Programas de apoyo a *Estequiometría y cálculos químicos*.

## Programas

- `psicrometria.py`: psicrometria.

## Instalación y uso

Se recomienda Python 3.10 o posterior. Desde esta carpeta, ejecutar:

```bash
python psicrometria.py
```

Para los demás programas, sustituir el nombre del archivo por el indicado en la lista.

Algunos módulos requieren paquetes adicionales para cálculos matriciales o gráficos (por ejemplo, `numpy`, `scipy` o `matplotlib`). Consultar las instrucciones de cada programa y verificar las dependencias antes de utilizarlo.

Se admiten las unidades indicadas en cada menú. Comprobar especialmente las cifras significativas y las hipótesis físicas de cada modelo.

## Material complementario

Los directorios `ejemplos`, `muestras` y `pruebas`, cuando existan, contienen recursos auxiliares y no constituyen programas adicionales del alumnado. En el capítulo 13, `cap13_apoyo.py` es una dependencia compartida que debe permanecer junto a los dos programas.

## Referencia y licencia

Código y documentación de este repositorio: **licencia MIT** (`../LICENSE`). DOI general del software: **10.5281/zenodo.24020474**; DOI de la versión 0.9.0: **10.5281/zenodo.24020473**. DOI del libro relacionado: **10.5281/zenodo.24013068**.


## Contraste adicional con el libro definitivo — Bloque V

Ejercicio **15.C.10**: gas no condensable N₂ (28,01 g/mol) con vapor de etanol (46,07 g/mol), `P=100,0 kPa`, `T=30,0 °C`, `P*EtOH=10,5 kPa`, `p_v=5,00 kPa`. En el **modo 12 — gas–vapor general** la razón de humedad inicial calculada es aproximadamente `0,08657 kg EtOH/kg N₂`. Tras enfriar a 10,0 °C, usando `P*EtOH=3,12 kPa`, la razón final es `0,05297`; condensado `0,03360 kg/kg N₂`, calculado al encadenar dos estados del modelo.

El modo general de Antoine está formulado con **T en °C**: `log10(P*/kPa) = A − B/(T_°C+C_°C)`. La tabla 6.1 del libro y el programa `presion_vapor.py` emplean **T en K**. Si las constantes están dadas para K, se debe transformar `C_°C=C_K+273,15`, conservando A y B, antes de introducirlas en el modo general. No se deben copiar sin conversión.

A partir de esta revisión, valores `NaN`, infinitos, parámetros singulares y presiones calculadas no finitas se rechazan con un error explicativo en la modalidad Antoine. Las pruebas reproducibles están en `pruebas_revision/test_cotejo_integradores_05.py`.

**Nota de convención, ejercicio 15.C.4:** el solucionario usa `c_p,aire=1,005`, `c_p,vapor=1,88` y `h_fg=2500`, mientras el programa usa `1,006`, `1,86` y `2501`. Se obtienen, respectivamente, ≈54,914 y ≈54,949 kJ/kg, diferencia ≈0,035 kJ/kg. Es una diferencia de constantes del modelo, no un fallo del cálculo.
