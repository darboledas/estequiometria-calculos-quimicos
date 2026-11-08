# Auditoría científica — bloque VIII (sin publicar)

- 418/418 pruebas transversales superadas, incluidas 44 nuevas.
- 40 ejercicios del libro y solucionario en el bloque: 23 nuevos y 17 comprobados por un procedimiento adicional. Total acumulado: 211 de 556.
- Cuatro pruebas adicionales de validación de datos en la correlación de Antoine para líquidos inmiscibles.

## Problema reproducido y corregido

En `inmiscibles_y_arrastre_vapor.py`, un coeficiente Antoine `NaN` podía provocar una aparente convergencia de la temperatura trifásica con un residuo indefinido. Ahora se comprueban la finitud de A, B, C y masa molar, los límites físicos de temperatura, la positividad de masa molar, B no negativo y que la presión de vapor calculada sea finita y positiva. Se conserva B=0 para un caso artificial de presión constante de las pruebas existentes.

Contraste: ejercicio 9.B.3, P=0,800 bar, T=351,188919 K, fracción molar de agua en vapor ≈0,546636 y relación másica tolueno/agua ≈4,24179.

## Errata en el solucionario (PDF sin cambios)

En el ejercicio 4.B.2, el desarrollo consigna 76.015 kg. Con los datos impresos, m = (100000 Pa)(65449,84695 m³)(0,0290 kg/mol) / [(8,31446 J/(mol·K))(300 K)] = 76.094,16 kg. La respuesta final de dos cifras significativas, 7,6×10⁴ kg, es correcta. Se registra la errata de cálculo intermedio, no un defecto del software.

## Ejecución reproducible

```bash
python -m unittest discover -s pruebas_revision -p test_cotejo_bloque_08.py -v
python -m unittest discover -s pruebas_revision -q
```

La matriz `REVISIONES/MATRIZ_COTEJO_BLOQUE_08.json` documenta todos los identificadores, las páginas PDF y las pruebas. Algunos problemas se resuelven con balances algebraicos auxiliares; no se atribuye al software una funcionalidad de menú que no posee. Quedan 345 identificadores sin contraste individual. GitHub y Zenodo siguen en v0.9.0.
