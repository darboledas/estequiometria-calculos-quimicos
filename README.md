# Estequiometría y cálculos químicos — Software complementario

**Autor y titular del copyright:** David Arboledas Brihuega.
**Versión de preparación:** 0.9.0 · **Licencia:** [MIT](LICENSE).
**DOI del libro:** [10.5281/zenodo.24013068](https://doi.org/10.5281/zenodo.24013068).
**DOI del software:** pendiente de asignación por Zenodo tras publicar una versión GitHub.

El presente repositorio reúne 28 aplicaciones de cálculo y comprobación en Python, organizadas por capítulos. El contenido del libro impreso/eBook es independiente y no se distribuye en este repositorio.

## Inicio rápido (Windows)

1. Instale Python 3.10 o posterior y compruebe `python --version` (en Windows, alternativamente `py --version`).
2. Descargue o descomprima este repositorio.
3. Sitúese en el directorio de la aplicación y ejecute `python archivo.py`.
4. Consulte el manual individual en `manuales/capitulo_XX/archivo.md`.

Para gráficos y modelos que los utilicen, instale las dependencias:

```powershell
python -m pip install -r requirements-graficos.txt
```

El comando instala NumPy y Matplotlib para cálculo numérico y gráficos, y Pillow para exportaciones PNG adicionales en el capítulo 13; muchos programas pueden funcionar sin estas dependencias.

## Programas por capítulos

| Capítulo | Aplicación | Manual |
|---|---|---|
| 2 | [`unidades_y_dimensiones.py`](capitulo_02/unidades_y_dimensiones.py) | [Manual: Unidades, cifras significativas e incertidumbres](manuales/capitulo_02/unidades_y_dimensiones.md) |
| 3 | [`ajuste_ecuaciones.py`](capitulo_03/ajuste_ecuaciones.py) | [Manual: Ajuste de ecuaciones químicas](manuales/capitulo_03/ajuste_ecuaciones.md) |
| 3 | [`conversion_rendimiento_selectividad.py`](capitulo_03/conversion_rendimiento_selectividad.py) | [Manual: Conversión, rendimiento y selectividad](manuales/capitulo_03/conversion_rendimiento_selectividad.md) |
| 3 | [`densidades_y_escalas.py`](capitulo_03/densidades_y_escalas.py) | [Manual: Densidad, gravedad específica y escalas industriales](manuales/capitulo_03/densidades_y_escalas.md) |
| 3 | [`masa_molar.py`](capitulo_03/masa_molar.py) | [Manual: Masa molar de compuestos químicos](manuales/capitulo_03/masa_molar.md) |
| 3 | [`reactivo_limitante.py`](capitulo_03/reactivo_limitante.py) | [Manual: Reactivo limitante y exceso](manuales/capitulo_03/reactivo_limitante.md) |
| 4 | [`gases_ideales_y_mezclas.py`](capitulo_04/gases_ideales_y_mezclas.py) | [Manual: Gases ideales y mezclas gaseosas](manuales/capitulo_04/gases_ideales_y_mezclas.md) |
| 5 | [`gases_reales.py`](capitulo_05/gases_reales.py) | [Manual: Propiedades de los gases reales](manuales/capitulo_05/gases_reales.md) |
| 6 | [`presion_vapor.py`](capitulo_06/presion_vapor.py) | [Manual: Presión de vapor y correlaciones](manuales/capitulo_06/presion_vapor.md) |
| 6 | [`vapor_agua.py`](capitulo_06/vapor_agua.py) | [Manual: Propiedades de saturación del agua](manuales/capitulo_06/vapor_agua.md) |
| 7 | [`equilibrio_liquido_vapor.py`](capitulo_07/equilibrio_liquido_vapor.py) | [Manual: Equilibrio líquido–vapor ideal](manuales/capitulo_07/equilibrio_liquido_vapor.md) |
| 7 | [`operaciones_liquido_vapor.py`](capitulo_07/operaciones_liquido_vapor.py) | [Manual: Operaciones de equilibrio líquido–vapor](manuales/capitulo_07/operaciones_liquido_vapor.md) |
| 8 | [`disoluciones_no_ideales.py`](capitulo_08/disoluciones_no_ideales.py) | [Manual: Disoluciones no ideales y actividad](manuales/capitulo_08/disoluciones_no_ideales.md) |
| 9 | [`equilibrio_liquido_liquido.py`](capitulo_09/equilibrio_liquido_liquido.py) | [Manual: Equilibrio líquido–líquido](manuales/capitulo_09/equilibrio_liquido_liquido.md) |
| 9 | [`inmiscibles_y_arrastre_vapor.py`](capitulo_09/inmiscibles_y_arrastre_vapor.py) | [Manual: Inmiscibles y arrastre de vapor](manuales/capitulo_09/inmiscibles_y_arrastre_vapor.md) |
| 10 | [`disoluciones_electroliticas.py`](capitulo_10/disoluciones_electroliticas.py) | [Manual: Disoluciones electrolíticas](manuales/capitulo_10/disoluciones_electroliticas.md) |
| 10 | [`propiedades_coligativas.py`](capitulo_10/propiedades_coligativas.py) | [Manual: Propiedades coligativas](manuales/capitulo_10/propiedades_coligativas.md) |
| 11 | [`balances_materia.py`](capitulo_11/balances_materia.py) | [Manual: Fundamentos de balances de materia](manuales/capitulo_11/balances_materia.md) |
| 12 | [`cristalizacion.py`](capitulo_12/cristalizacion.py) | [Manual: Cristalización por enfriamiento](manuales/capitulo_12/cristalizacion.md) |
| 12 | [`evaporacion.py`](capitulo_12/evaporacion.py) | [Manual: Concentración por evaporación](manuales/capitulo_12/evaporacion.md) |
| 12 | [`extraccion_liquido_liquido.py`](capitulo_12/extraccion_liquido_liquido.py) | [Manual: Extracción líquido–líquido](manuales/capitulo_12/extraccion_liquido_liquido.md) |
| 12 | [`filtracion.py`](capitulo_12/filtracion.py) | [Manual: Filtración de una suspensión](manuales/capitulo_12/filtracion.md) |
| 12 | [`secado.py`](capitulo_12/secado.py) | [Manual: Secado de sólidos húmedos](manuales/capitulo_12/secado.md) |
| 12 | [`separacion_corrientes.py`](capitulo_12/separacion_corrientes.py) | [Manual: Separación en dos corrientes](manuales/capitulo_12/separacion_corrientes.md) |
| 13 | [`balance_una_reaccion.py`](capitulo_13/balance_una_reaccion.py) | [Manual: Balance reactivo con una reacción](manuales/capitulo_13/balance_una_reaccion.md) |
| 13 | [`balance_varias_reacciones.py`](capitulo_13/balance_varias_reacciones.py) | [Manual: Balance reactivo con varias reacciones](manuales/capitulo_13/balance_varias_reacciones.md) |
| 14 | [`combustion.py`](capitulo_14/combustion.py) | [Manual: Combustión y análisis de gases](manuales/capitulo_14/combustion.md) |
| 15 | [`psicrometria.py`](capitulo_15/psicrometria.py) | [Manual: Aire húmedo y psicrometría](manuales/capitulo_15/psicrometria.md) |

## Alcance y verificación

Las herramientas automatizan cálculo y comprobación en el marco de sus modelos. No sustituyen el planteamiento químico del problema.

**Revisión 6-11-2026:** se han comprobado la sintaxis y las salidas de ayuda y menús de los 28 programas; no implica validación científica exhaustiva de todos los modelos. Pruebas ejecutadas: 24/24 capítulo 9, 38/38 y 39/39 capítulo 10, 58/58 capítulo 11, 23/23 capítulo 14, 12 grupos capítulo 15 y autopruebas de cuatro programas del capítulo 3. En capítulo 13 se corrigió la precisión individual de las extensiones y se añadieron pruebas de regresión; consulte `COMPROBACIONES.md` y `AUDITORIA_PREPUBLICACION.md`.

**Nota editorial:** el inventario original omitía `masa_molar.py`. Los ejemplos `python script_13_1...` y otros nombres heredados de las cabeceras pueden no coincidir con los nombres reales de los archivos; los manuales y la presente tabla dan los nombres actuales. En psicrometría hay discrepancias entre el texto editorial y la ayuda real (12/15 modos; PNG 300/400 ppp).

## Organización

- `capitulo_XX/`: programas `.py` y ejemplos originales.
- `manuales/capitulo_XX/`: un manual individual por aplicación.
- [`Manual_software_estequiometria_GitHub.docx`](Manual_software_estequiometria_GitHub.docx): edición Word conjunta con Arial 10/14/12 y Consolas 9 para comandos y salidas.
- `INVENTARIO_ACTUALIZADO.md`: relación efectiva de los archivos.
- `AUDITORIA_PREPUBLICACION.md`: pruebas realizadas y aspectos pendientes.
- `COMPROBACIONES.md`: ejecución reproducible de los test.
- `GUIA_PUBLICACION_GITHUB_ZENODO.md`: instrucciones para publicación y obtención del DOI.
- `LICENSE`, `CITATION.cff`, `.zenodo.json`: licencia y metadatos de citación y archivado.

## Licencia y publicación

El código y la documentación de este repositorio se distribuyen bajo **[licencia MIT](LICENSE)**. La obra editorial independiente no se distribuye aquí ni queda cubierta por esta licencia. Los metadatos de `CITATION.cff` y `.zenodo.json` están preparados para que el software obtenga **su propio DOI** cuando se publique y archive una versión en Zenodo. Consulte [la guía de GitHub y Zenodo](GUIA_PUBLICACION_GITHUB_ZENODO.md).
