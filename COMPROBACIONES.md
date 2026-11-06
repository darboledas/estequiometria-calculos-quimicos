# Comprobaciones automáticas

## Ejecución desde la raíz del repositorio

```powershell
python -m compileall -q capitulo_02 capitulo_03 capitulo_04 capitulo_05 capitulo_06 capitulo_07 capitulo_08 capitulo_09 capitulo_10 capitulo_11 capitulo_12 capitulo_13 capitulo_14 capitulo_15
python capitulo_09/pruebas_capitulo9.py
python capitulo_11/pruebas_capitulo11.py
python -m unittest discover -s capitulo_13/pruebas -v
python capitulo_10/disoluciones_electroliticas.py --selftest
python capitulo_10/propiedades_coligativas.py --selftest
python capitulo_14/combustion.py --self-test
python capitulo_15/psicrometria.py --validar
```

La primera línea comprueba que el código Python se compila; no equivale a una comprobación de exactitud física. Las pruebas numéricas verifican casos incluidos en los conjuntos de regresión, no todos los posibles datos. La integración continua ejecuta estas pruebas con Python 3.11 y 3.13 en Ubuntu.

Si el capítulo 9 o 11 necesita importaciones de la carpeta, sus archivos incluyen el punto de entrada necesario: ejecútelos como scripts. Los programas que requieran gráficos pueden utilizar `requirements-graficos.txt`.
