# Revisión científica: combustión incompleta, mezclas multicomponente y cálculos inversos

**Fecha de trabajo:** 7 de noviembre de 2026.  
**Estado:** revisión local acumulada, no publicada; la versión 0.9.0 de GitHub/Zenodo permanece intacta.  
**Código base:** paquete acumulado de 127 pruebas transversales.  
**Objeto del cambio:** `capitulo_14/combustion.py` y nueva batería `pruebas_revision/test_combustion_incompleta_inversos.py`.

## Incidencias reproducidas y corregidas

1. La combustión incompleta eliminaba el combustible no convertido y el O₂ sobrante cuando sus cantidades quedaban por debajo de 10⁻⁹ mol. Para 10⁻¹² mol de CH₄, conversión del 80 % y 75 % del carbono reaccionado a CO₂, se producían balances elementales incorrectos.
2. La comprobación del oxígeno suministrado utilizaba un margen absoluto de 10⁻¹⁰ mol, capaz de admitir un déficit del orden de 10⁻¹³ mol.
3. El redondeador general mostraba como «0» valores válidos de módulo inferior a 10⁻⁹, en vez de notación científica. La selección de cifras significativas omitía entradas positivas de esa escala.
4. Un sustrato con exceso de oxígeno propio podía producir un requerimiento negativo de O₂ que no se rechazaba cuando la escala era muy pequeña. Ahora se compara el residuo con la escala del balance de oxígeno.
5. En el cálculo inverso de mezcla binaria se descartaban cantidades positivas muy pequeñas por un umbral absoluto; en el inverso de combustible puro se mostraba `nan` para ciertos cálculos de exceso de aire. La necesidad estequiométrica nula se rechaza en ese modo inverso, pues el factor de aire no está definido.
6. Se han corregido en la cabecera de ayuda del programa tres referencias al antiguo nombre `tema14_combustion.py`; el archivo real es `combustion.py`.

## Contrastes analíticos

**Combustión incompleta de metano:** 1 mol CH₄ alimentado, conversión 80 %, 75 % del carbono reaccionado a CO₂ y 25 % a CO, suministro de 1,8 mol de O₂ puro:

- CH₄ sin reaccionar = 0,2 mol;
- CO₂ = 0,6 mol; CO = 0,2 mol; H₂O = 1,6 mol;
- O₂ consumido = 1,5 mol; O₂ de salida = 0,3 mol;
- total de gas húmedo = 2,9 mol; total seco = 1,3 mol;
- fracción molar seca de CO₂ = 0,6/1,3 = 0,461538…;
- todos los balances de C, H y O cierran.

Los mismos cocientes deben reproducirse con 10⁻⁶, 10⁻⁹ y 10⁻¹² mol de CH₄. Un suministro de 1,4 mol O₂ por mol de CH₄ es insuficiente para los productos especificados, también cuando la base es 10⁻¹² mol.

**Mezcla con inertes:** 2 mol CH₄ + 1 mol C₂H₆ + 0,4 mol CO₂ inerte + 0,8 mol N₂ inerte. Para oxidación completa: 7,5 mol O₂ teóricos, 4,4 mol CO₂ y 7 mol H₂O; el N₂ del combustible pasa sin reaccionar. Se ha contrastado la conservación elemental añadiendo aire con 20 % de exceso.

**Orsat:** V₀ = 100, V₁ = 88, V₂ = 83, V₃ = 81, al absorber sucesivamente CO₂, O₂ y CO. Resultado: 12 % CO₂, 5 % O₂, 2 % CO y 81 % residuo etiquetado N₂. Esta última identificación es una hipótesis del método, no una medición selectiva del gas residual.

**Inversiones:** se han reconstruido proporciones de CH₄, C₂H₆ y N₂ inerte a partir de un análisis seco y una relación molar conocida; y las proporciones de CH₄ y C₂H₆ desde CO₂ seco y factor de aire. Se incluyen verificaciones de indeterminación e incompatibilidad algebraica.

**Prueba de amplitud:** 150 composiciones sintéticas reproducibles de cuatro componentes (CH₄, C₂H₆, N₂ y CO₂ inertes) con dos relaciones molares conocidas y factor de aire entre 1 y 2. El sistema lineal reconstruye la solución de partida con errores relativos inferiores a 10⁻⁹ en los casos muestreados. No se prueba por ello su estabilidad general en sistemas casi singulares.

## Resultado de la batería

- 143 métodos transversales `unittest` superados (**127 anteriores + 16 nuevos**, uno de ellos con 150 subcasos).
- Pruebas propias del capítulo 9: 24; capítulo 10: 77; capítulo 11: 58; capítulo 13: 12; capítulo 14: 23; capítulo 15: 12 grupos de validación.
- Compilación sintáctica de módulos y pruebas: correcta.
- Ejecución local en Python 3.13; pendiente ejecutar el conjunto actualizado en GitHub Actions (Python 3.11 y 3.13) cuando se publique la próxima revisión.

## Reproducción

```bash
python -m unittest discover -s pruebas_revision -v
python -m unittest pruebas_revision.test_combustion_incompleta_inversos -v
python capitulo_14/combustion.py --self-test
```

Se conservan registros de la ejecución en `REVISIONES/logs_2026_11_07_b/`.

## Referencias de contraste

- ASHRAE, *Handbook — Combustion and Fuels*, cap. 28: https://handbook.ashrae.org/Handbooks/F21/SI/f21_ch28/F21_Ch28_si.aspx
- Agencia Europea de Medio Ambiente (EEA), *EMEP/EEA air pollutant emission inventory guidebook*, sección de combustión estacionaria: https://www.eea.europa.eu/publications/emep-eea-guidebook-2016/part-b-sectoral-guidance-chapters/1-energy/1-a-combustion/1-a-4-small-combustion/

Las ecuaciones contrastadas emplean conservación de C, H, O y N, además de la composición de aire que adopta el capítulo (21,0 % O₂; 79,0 % N₂). No se han alterado ni las constantes del libro ni su modelo químico.

## Límites para v1.0.0

Aún quedan sin contrastar sistemáticamente todas las entradas de composición elemental, matrices inversas mal condicionadas, correlaciones termodinámicas en todo su dominio, cálculo energético (no implementado) y todos los ejercicios del libro. Esta revisión demuestra consistencia para los casos listados; no constituye una certificación científica universal.
