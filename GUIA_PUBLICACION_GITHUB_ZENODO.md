> **Archivo histórico:** elaborado antes de la publicación de `v0.9.0`. Para el estado actual consulte `README.md`, `COMPROBACIONES.md` y `REVISIONES/INFORME_AUDITORIA_INTEGRAL.md`.

# Publicación en GitHub y asignación de DOI del software

## 1. Preparar GitHub

Este proyecto contiene más de 100 archivos. Para publicar la estructura completa, utilice Git desde PowerShell o GitHub Desktop, en lugar de intentar subir todos los archivos a la vez desde el navegador.

1. Entre en https://github.com y autentíquese.
2. Cree un repositorio público con el nombre `estequiometria-calculos-quimicos`.
3. **No** marque «Add a README», «Choose a license» ni «Add .gitignore»: ya están incluidos.
4. Abra PowerShell en la carpeta raíz del proyecto descomprimido.
5. Ejecute los comandos siguientes sustituyendo `USUARIO_GITHUB` por su usuario real:

```powershell
git init
git add .
git commit -m "Versión inicial: 28 aplicaciones, manuales, MIT y metadatos Zenodo"
git branch -M main
git remote add origin https://github.com/USUARIO_GITHUB/estequiometria-calculos-quimicos.git
git push -u origin main
```

Si no tiene Git instalado, instálelo desde https://git-scm.com/downloads y configure una vez su nombre y correo. Para autenticar operaciones `push`, siga el procedimiento que indique GitHub (navegador o gestor de credenciales); **no** incluya contraseñas ni tokens en el repositorio.

## 2. Verificar documentación y código

- Compruebe que GitHub detecta la licencia MIT.
- Abra los enlaces a manuales desde `README.md`.
- Compruebe el resultado de la acción «Comprobaciones Python».
- Revise el registro `AUDITORIA_PREPUBLICACION.md` y la validación de los modelos antes de la versión definitiva.

## 3. Conectar Zenodo

1. Abra https://zenodo.org/ y entre en su cuenta.
2. En el menú de su perfil, vincule GitHub si todavía no lo está.
3. Desde la sección **GitHub**, pulse **Sync now** si es necesario.
4. Localice y active la integración para `estequiometria-calculos-quimicos`.
5. Cuando decida publicar, use una versión coherente en `VERSION`, `CITATION.cff` y `.zenodo.json`. La preparada aquí es `0.9.0`: publíquela como `v0.9.0`, o bien, después de completar la revisión científica, actualice los tres archivos a `1.0.0` y publique `v1.0.0`. Cree una **Release** real, no solo una etiqueta Git.
6. Zenodo archivará la versión y asignará los DOI correspondientes. Compruebe que el registro indica tipo **Software**, acceso **Open** y licencia **MIT**.

El archivo `.zenodo.json` configura la relación `isSupplementTo` respecto al DOI del libro `10.5281/zenodo.24013068`. El libro no queda relicenciado por MIT: esta licencia se refiere al código y la documentación del repositorio.

## 4. Incorporar el DOI del software al repositorio

Una vez se conozca el DOI real del software:

- Añada el DOI específico de la versión publicada a `CITATION.cff` en el campo `doi:`.
- Añada al `README.md` el enlace real `https://doi.org/<DOI_REAL>` y, si desea, su distintivo (badge).
- Conserve el DOI conceptual para identificar el proyecto a través de versiones; utilice un DOI de versión para reproducibilidad.
- Si modifica código después del archivo de Zenodo, publique una nueva versión para que el DOI de versión coincida con el contenido.

**Importante:** el DOI del libro no es el DOI del software. Este paquete no contiene un DOI del software porque todavía no se ha registrado su primera versión.

## 5. Referencias oficiales

- GitHub, archivos de citación: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-citation-files
- Zenodo, conectar repositorios: https://help.zenodo.org/docs/github/enable-repository/
- Zenodo, metadatos: https://help.zenodo.org/docs/github/describe-software/zenodo-json/
- Zenodo, DOI de versión y concepto: https://zenodo.org/help/versioning
