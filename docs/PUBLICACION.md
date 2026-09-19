# Publicar Easy Marks

La fuente está en el repositorio privado [valianx/EasyMarks](https://github.com/valianx/EasyMarks). El ZIP publicado en CurseForge será distribuible aunque GitHub permanezca privado. No se ha subido todavía ningún archivo a CurseForge: falta crear el proyecto, conectar sus credenciales y completar las pruebas reales.

## Crear la ficha una vez

1. Entrar en el [portal de autores](https://authors.curseforge.com/), crear un proyecto de **World of Warcraft → Addons** y comprobar el nombre **Easy Marks**.
2. Usar [branding/easy-marks-curseforge.png](../branding/easy-marks-curseforge.png): PNG original de 1254 × 1254, unos 3 MB. Las imágenes deben cumplir las reglas del formulario; este diseño no utiliza archivos gráficos del juego. No anunciarlo como producto oficial de Blizzard.
3. Añadir una descripción, categorías correspondientes a la coordinación del grupo y capturas reales. Elegir la licencia en el formulario; el proyecto todavía no tiene una licencia pública elegida.
4. Guardar el proyecto y copiar su **Project ID** numérico. No es el slug de la URL ni el ID de una versión de WoW.
5. Generar un token en [API tokens del portal de autores](https://authors.curseforge.com/#/settings/api-tokens). No pegarlo en chat, código o capturas.

La ficha y los archivos requieren moderación. No volver a subir un archivo que siga bajo revisión manual. Las versiones alpha no tienen la misma visibilidad en la app que beta/release; para que un proyecto nuevo sincronice con la app hace falta una beta o release aprobada. Fuentes: [envío de proyectos](https://support.curseforge.com/support/solutions/articles/9000199552-project-submission-guide-and-tips), [estados de archivos y proyectos](https://support.curseforge.com/support/solutions/articles/9000197242), [revisión de archivos](https://support.curseforge.com/support/solutions/articles/9000197905).

Descripción inicial en inglés:

> Easy Marks puts manual ground and target marking in one compact wheel. Left-click a symbol to choose a ground point for a marker and ping; right-click to mark and ping your selected target. Clear one ground color and your target, or clear all group markers without pinging. Move the wheel outside combat and open it from the EM minimap button. Uses native game signals; teammates do not need the addon. Game permissions and instance restrictions apply.

No anunciar compatibilidad específica con arenas o míticas+ hasta registrar los resultados en [PRUEBAS.md](PRUEBAS.md).

## Conectar GitHub Actions

En el repositorio: **Settings → Secrets and variables → Actions**.

| Tipo | Nombre | Valor |
| --- | --- | --- |
| Repository secret | `CF_API_TOKEN` | Token de autor de CurseForge |
| Repository variable | `CURSEFORGE_PROJECT_ID` | ID numérico del proyecto |
| Repository variable | `CURSEFORGE_ENABLED` | `true` para subir automáticamente cuando se publique una GitHub Release |

No hace falta un token personal de GitHub para estos workflows. La clave de autores es distinta de la API para terceros de CurseForge for Studios. No configurar simultáneamente el webhook de autoempaquetado de CurseForge: produciría otra ruta de publicación junto a Actions.

## Probar sin publicar

En **Actions → CurseForge release → Run workflow**, elegir `main` y dejar `publish` en `false`. Ejecuta las pruebas, construye el ZIP y conserva los metadatos como artefactos, sin necesitar ID ni token y sin llamadas a CurseForge.

Equivalente local desde la raíz:

```powershell
python -m tools.release
```

El workflow **Test and package** hace pruebas y ZIP en cada push/PR; sus artefactos duran 14 días. Los de preparación/publicación duran 30 días. Al descargarlos desde Actions, extraer el ZIP exterior del artefacto para encontrar el ZIP instalable `EasyMarks-<version>.zip`.

## Publicar una versión

1. Comprobar el addon en WoW. Actualizar `## Version` del TOC y su sección exacta `## <version>` en `CHANGELOG.md`. Mantener `## Interface` en la versión Retail realmente probada.
2. Subir el commit a `main` y esperar a que CI pase.
3. Crear un tag `v<version>`: por ejemplo `v0.1.10-alpha` para TOC `0.1.10-alpha`. Crear y publicar una **GitHub Release** con ese tag. Marcarla como prerelease si es alpha/beta.
4. Si `CURSEFORGE_ENABLED=true`, Actions prueba, prepara y sube el ZIP a CurseForge. Si la variable está ausente o es `false`, solo prepara artefactos.
5. Revisar en la ejecución el recibo `curseforge-receipt.json`, con `fileId` y SHA-256; después revisar el estado de moderación en CurseForge.

Canales derivados del TOC: `1.0.0-alpha` o `1.0.0-alpha.1` → alpha; `1.0.0-beta` o `1.0.0-beta.1` → beta; `1.0.0` → release. El tag debe coincidir exactamente con el TOC. No cambiar un tag ya publicado para reutilizar una versión.

También se puede subir con **Run workflow** seleccionando un tag existente y `publish=true`. Esa acción manual publica aunque `CURSEFORGE_ENABLED` esté desactivado. El commit debe pertenecer a `main`; un tag arbitrario de otra rama no pasa la comprobación. Publicar una GitHub Release dispara el flujo incluso si es prerelease; los borradores no lo disparan. [Eventos de GitHub Actions](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#release).

## Paquete y API

`tools/package.py` crea exclusivamente `EasyMarks/EasyMarks.toc`, `Errors.lua`, `Domain/Markers.lua`, `UI/Wheel.lua`, `Core.lua` y `Bindings.xml`. Ni logo, documentación, tests, `.git`, registros, SavedVariables ni credenciales entran en el ZIP. El cargador implícito de WoW recibe `Bindings.xml`; no se enumera en el TOC.

`tools/release.py` reutiliza ese ZIP y vuelve a contrastarlo con la fuente antes de subir. Sigue la [API de autores](https://support.curseforge.com/support/solutions/articles/9000197321) y los endpoints específicos WoW usados por [BigWigsMods/packager](https://github.com/BigWigsMods/packager/blob/master/release.sh): `https://wow.curseforge.com/api/game/wow/versions` y `/api/projects/{id}/upload-file`. Envía el token en una cabecera, resuelve el ID de la versión exacta con tipo Retail 517 y hace un POST multipart con metadatos y archivo. No infiere un ID ni elige otra versión como alternativa. La subida autenticada real queda pendiente hasta conectar el proyecto.

No se usa BigWigs para reconstruir el paquete: así la lista de archivos y los bytes que probamos son los que se envían. GitHub guarda el ZIP como artefacto de Actions, no como adjunto automático de la Release.

Si una subida devuelve error o timeout, revisar **Files** en CurseForge antes de repetir: la API no documenta una clave de idempotencia. No usar **Re-run jobs** para reintentar una subida; el script lo rechaza. Si se confirma que no se creó el archivo, iniciar una nueva ejecución manual sobre el mismo tag. `concurrency` evita ejecuciones simultáneas del mismo ref, pero no sustituye esa comprobación ante resultados inciertos.
