# Publicar Easy Marks

La fuente está en el repositorio público [valianx/EasyMarks](https://github.com/valianx/EasyMarks). Mario creó el proyecto CurseForge y eligió su empaquetador nativo para publicar tags. Falta confirmar la conexión y el primer archivo generado. GitHub Actions se conserva para pruebas y preparación; la subida por API sigue desactivada.

## Crear la ficha una vez

1. Entrar en el [portal de autores](https://authors.curseforge.com/), crear un proyecto de **World of Warcraft → Addons** y comprobar el nombre **Easy Marks**.
2. Usar [branding/easy-marks-curseforge.png](../branding/easy-marks-curseforge.png): PNG original de 1254 × 1254, unos 3 MB; es el archivo fuente del logo. El avatar que se suba debe tener 400 × 400 píxeles, según las [políticas de moderación](https://support.curseforge.com/support/solutions/articles/9000197279-moderation-policies). Las imágenes deben cumplir las reglas del formulario; este diseño no utiliza archivos gráficos del juego. No anunciarlo como producto oficial de Blizzard.
3. Añadir una descripción, categorías correspondientes a la coordinación del grupo y capturas reales. Seleccionar MIT License en el formulario, coherente con LICENSE del repositorio. Si antes se eligió All Rights Reserved, actualizar ese campo antes de subir esta versión.
4. Guardar el proyecto y copiar su **Project ID** numérico. No es el slug de la URL ni el ID de una versión de WoW.
5. Solo si se elige la alternativa de subida por API, generar un token en [API tokens del portal de autores](https://authors.curseforge.com/#/settings/api-tokens). No pegarlo en chat, código o capturas.

La ficha y los archivos requieren moderación. No volver a subir un archivo que siga bajo revisión manual. Las versiones alpha no tienen la misma visibilidad en la app que beta/release; para que un proyecto nuevo sincronice con la app hace falta una beta o release aprobada. Fuentes: [envío de proyectos](https://support.curseforge.com/support/solutions/articles/9000199552-project-submission-guide-and-tips), [estados de archivos y proyectos](https://support.curseforge.com/support/solutions/articles/9000197242), [revisión de archivos](https://support.curseforge.com/support/solutions/articles/9000197905).

Descripción inicial en inglés:

> Easy Marks puts manual ground and target marking in one compact wheel. Left-click a symbol to choose a ground point for a marker and ping; right-click to mark and ping your selected target. Clear one ground color and your target, or clear all group markers without pinging. Move the wheel outside combat and open it from the EM minimap button. Uses native game signals; teammates do not need the addon. Game permissions and instance restrictions apply.

No anunciar compatibilidad específica con arenas o míticas+ hasta registrar los resultados en [PRUEBAS.md](PRUEBAS.md).

## Compatibilidad de WoW

El TOC declara `## Interface: 120105`, correspondiente a WoW Retail 12.1.5. La versión del addon (`## Version: 0.1.11`) es independiente. En el formulario de cada archivo en CurseForge, seleccionar Retail y 12.1.5 en **Game Versions / Supported Version**; [CurseForge permite indicar las versiones compatibles del archivo](https://support.curseforge.com/support/solutions/articles/9000197242).

El README no muestra números de versión; la compatibilidad se declara en el TOC y en los campos de cada archivo en CurseForge. `tools/release.py` deriva `gameVersionNames: ["12.1.5"]` del TOC y resuelve el ID Retail exacto al subir por API. 12.1.5 es la versión de destino declarada por el mantenedor; la validación dentro de ese cliente sigue pendiente. Cambiar el número del TOC no sustituye esa comprobación. Las pruebas de combate e instancias pendientes están en [PRUEBAS.md](PRUEBAS.md).

## Empaquetado nativo de CurseForge

Es la ruta elegida para publicar desde tags: enlazar `https://github.com/valianx/EasyMarks` y seleccionar el empaquetado de commits etiquetados en **Source Code → Automatic Packaging**. No requiere una Action de subida ni crear una GitHub Release. El tag `v0.1.11`, sin alpha/beta, corresponde al canal Release.

Antes de dar por conectada esta ruta, comprobar el webhook y su entrega en GitHub, preparar `.pkgmeta` para convertir `addon/EasyMarks` en la carpeta instalable `EasyMarks`, y revisar el archivo generado en CurseForge. El repositorio aún no incluye esa configuración del empaquetador; el ZIP local de `tools/package.py` ya tiene la estructura instalable correcta. Véanse [Automatic Packaging](https://support.curseforge.com/support/solutions/articles/9000197281) y [PackageMeta](https://support.curseforge.com/support/solutions/articles/9000197952-preparing-the-packagemeta-file).

Mantener `CURSEFORGE_ENABLED=false` mientras se use el empaquetador nativo, para evitar dos rutas de subida. El aviso de moderación limita la visibilidad y sincronización del proyecto; no indica un fallo de compatibilidad. En **Files**, comprobar que el resultado indique Retail, 12.1.5 y Release.

## Alternativa: conectar GitHub Actions

En el repositorio: **Settings → Secrets and variables → Actions**.

| Tipo | Nombre | Valor |
| --- | --- | --- |
| Repository secret | `CF_API_TOKEN` | Token de autor de CurseForge |
| Repository variable | `CURSEFORGE_PROJECT_ID` | ID numérico del proyecto |
| Repository variable | `CURSEFORGE_ENABLED` | `true` para subir automáticamente cuando se publique una GitHub Release |

No hace falta un token personal de GitHub para estos workflows. La clave de autores es distinta de la API para terceros de CurseForge for Studios. En Source Code se puede enlazar el repositorio público, manteniendo Automatic Packaging desactivado para usar Actions como única ruta de subida. No configurar simultáneamente el webhook de autoempaquetado de CurseForge: produciría otra ruta de publicación junto a Actions. El empaquetador de CurseForge requiere su propia configuración de webhook y PackageMeta para adaptar la carpeta addon/EasyMarks; hacer público el repositorio no crea ni sube tags. Véase [Automatic Packaging](https://support.curseforge.com/support/solutions/articles/9000197281).

## Probar sin publicar

En **Actions → CurseForge release → Run workflow**, elegir `main` y dejar `publish` en `false`. Ejecuta las pruebas, construye el ZIP y conserva los metadatos como artefactos, sin necesitar ID ni token y sin llamadas a CurseForge.

Equivalente local desde la raíz:

```powershell
python -m tools.release
```

El workflow **Test and package** hace pruebas y ZIP en cada push/PR; sus artefactos duran 14 días. Los de preparación/publicación duran 30 días. Al descargarlos desde Actions, extraer el ZIP exterior del artefacto para encontrar el ZIP instalable `EasyMarks-<version>.zip`.

## Publicar una versión mediante la alternativa de Actions

1. Comprobar el addon en WoW. Actualizar `## Version` del TOC y su sección exacta `## <version>` en `CHANGELOG.md`. Mantener `## Interface` coherente con la versión de destino y registrar por separado las pruebas realizadas en el cliente.
2. Subir el commit a `main` y esperar a que CI pase.
3. Crear un tag `v<version>`: por ejemplo `v0.1.11` para TOC `0.1.11`. Crear y publicar una **GitHub Release** con ese tag. Marcarla como prerelease si es alpha/beta.
4. Si `CURSEFORGE_ENABLED=true`, Actions prueba, prepara y sube el ZIP a CurseForge. Si la variable está ausente o es `false`, solo prepara artefactos.
5. Revisar en la ejecución el recibo `curseforge-receipt.json`, con `fileId` y SHA-256; después revisar el estado de moderación en CurseForge.

Canales derivados del TOC: `1.0.0-alpha` o `1.0.0-alpha.1` → alpha; `1.0.0-beta` o `1.0.0-beta.1` → beta; `1.0.0` → release. El tag debe coincidir exactamente con el TOC. No cambiar un tag ya publicado para reutilizar una versión.

También se puede subir con **Run workflow** seleccionando un tag existente y `publish=true`. Esa acción manual publica aunque `CURSEFORGE_ENABLED` esté desactivado. El commit debe pertenecer a `main`; un tag arbitrario de otra rama no pasa la comprobación. Publicar una GitHub Release dispara el flujo incluso si es prerelease; los borradores no lo disparan. [Eventos de GitHub Actions](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#release).

## Paquete y API

`tools/package.py` crea exclusivamente `EasyMarks/EasyMarks.toc`, `Errors.lua`, `Domain/Markers.lua`, `UI/Wheel.lua`, `Core.lua`, `Bindings.xml` y una copia de `LICENSE` desde la raíz. Ni logo, documentación, tests, `.git`, registros, SavedVariables ni credenciales entran en el ZIP. El cargador implícito de WoW recibe `Bindings.xml`; no se enumera en el TOC.

`tools/release.py` reutiliza ese ZIP y vuelve a contrastarlo con la fuente antes de subir. Sigue la [API de autores](https://support.curseforge.com/support/solutions/articles/9000197321) y los endpoints específicos WoW usados por [BigWigsMods/packager](https://github.com/BigWigsMods/packager/blob/master/release.sh): `https://wow.curseforge.com/api/game/wow/versions` y `/api/projects/{id}/upload-file`. Envía el token en una cabecera, resuelve el ID de la versión exacta con tipo Retail 517 y hace un POST multipart con metadatos y archivo. No infiere un ID ni elige otra versión como alternativa. La subida autenticada real queda pendiente hasta conectar el proyecto.

No se usa BigWigs para reconstruir el paquete: así la lista de archivos y los bytes que probamos son los que se envían. GitHub guarda el ZIP como artefacto de Actions, no como adjunto automático de la Release.

Si una subida devuelve error o timeout, revisar **Files** en CurseForge antes de repetir: la API no documenta una clave de idempotencia. No usar **Re-run jobs** para reintentar una subida; el script lo rechaza. Si se confirma que no se creó el archivo, iniciar una nueva ejecución manual sobre el mismo tag. `concurrency` evita ejecuciones simultáneas del mismo ref, pero no sustituye esa comprobación ante resultados inciertos.
