# Cómo contribuir a Easy Marks

El proyecto empieza como una alpha personal en [valianx/EasyMarks](https://github.com/valianx/EasyMarks), repositorio público. La licencia de distribución sigue pendiente. Los cambios se desarrollan en la carpeta del proyecto; la copia instalada en WoW se utiliza para probarlos.

## Entender el cambio

1. Leer [README](README.md), [arquitectura](docs/ARCHITECTURE.md) y [AGENTS.md](AGENTS.md).
2. Revisar el cambio activo bajo `openspec/changes/` y sus escenarios de aceptación.
3. Trabajar sobre el alcance aprobado mediante Team Harness `spec`. Una idea nueva puede requerir ajustar la propuesta antes de implementarla.
4. Crear ramas con prefijo `codex/` para el trabajo de agentes; conservar los cambios locales existentes.

## Preparar desarrollo en Windows

Se usa Python 3.10 o posterior. Desde la raíz:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
.\.venv\Scripts\python.exe tools/package.py
```

El paquete final está en `dist/`. El empaquetador usa solo la biblioteca estándar; Lupa se necesita únicamente para las pruebas. No se incluyen el entorno virtual, las pruebas ni las herramientas en el ZIP.

## Pruebas por nivel

```powershell
# Unitarias: dominio sin WoW y logger con dobles mínimos
.\.venv\Scripts\python.exe -B -m unittest discover -s tests/unit -v

# Integración: carga, botones, Escape y cursor con contrato simulado
.\.venv\Scripts\python.exe -B -m unittest discover -s tests/integration -v

# Todo, incluidos manifiesto y límites OpenSpec
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

`tests/support/wow_mock.lua` concentra la simulación. Las unitarias no lo cargan: el dominio solo necesita Lua; el logger usa dobles de reloj, metadatos y salida de errores. No se replica la interfaz completa para probar una función pura.

El motor protegido, el orden real de eventos, la apariencia, el portapapeles y la recepción por otros jugadores requieren [pruebas en WoW](docs/PRUEBAS.md). El defecto del cursor permanente mostró un límite concreto: el mock ejecutaba siempre un post-handler que el cliente solo ejecuta si hay un segundo retorno del pre-handler. Esa condición ahora forma parte de la regresión.

Para OpenSpec se necesita Node 20.19 o posterior y npm. Se mantiene la versión fijada por Team Harness:

```powershell
npx --yes @fission-ai/openspec@1.9.0 validate manual-ground-marks --strict
```

El nombre del cambio se sustituye cuando se trabaje en otro. No actualizar la versión de OpenSpec incidentalmente junto con una función del addon.

## Cambiar y probar

- Editar `addon/EasyMarks`, sin modificar archivos originales del cliente ni otros addons.
- Colocar reglas/datos puros en `Domain/Markers.lua`, APIs de interfaz en `UI/Wheel.lua` y ciclo de vida en `Core.lua`. El namespace privado del addon enlaza los módulos; no hay un framework de inyección.
- Añadir pruebas cuando aporten evidencia de una conducta o de un fallo concreto; no imitar la implementación como único criterio.
- Mantener las acciones protegidas vinculadas a entrada manual y probar confirmación/cancelación tanto fuera como dentro de combate.
- Comprobar XML, metadatos TOC y contenido del ZIP cuando cambie la entrega.
- Mantener `Errors.lua` antes de `Core.lua` en el TOC. `Bindings.xml` se distribuye sin incluirlo en ese listado. Consultar [diagnóstico](docs/DIAGNOSTICO.md) para errores y limitaciones de captura.
- Instalar la copia de prueba según el alcance autorizado y ejecutar `/reload` después de actualizar archivos. Al añadir un addon nuevo puede ser necesario reiniciar el juego.
- Seguir [PRUEBAS.md](docs/PRUEBAS.md). Registrar los escenarios que no se pudieron ejecutar; una suite simulada correcta no los reemplaza.

## Describir una contribución

`main` es la rama remota principal; usar ramas `codex/…` para nuevos cambios. El workflow **Test and package** ejecuta la suite y conserva el ZIP como artefacto durante 14 días. La carpeta `dist/` y las credenciales no se versionan. Las Actions están fijadas por SHA; al actualizarlas, comprobar la versión de origen y volver a validar el YAML con actionlint.

Para preparar una publicación sin token ni red: `python -m tools.release`. Para comprobar su tag: `python -m tools.release --tag v0.1.10-alpha`, sustituyéndolo por la versión exacta del TOC. Las reglas de publicación y configuración están en [PUBLICACION.md](docs/PUBLICACION.md).

Indicar el problema observable, el comportamiento resultante, los archivos afectados y la verificación realizada. Un informe de error útil incluye versión de WoW, modo de juego, estado de combate, pasos, mensaje Lua y si falló la marca, el ping o ambos. Omitir datos personales innecesarios.

Actualizar las instrucciones cuando cambie lo que hace el addon. No incluir credenciales, carpetas WTF ni código de terceros sin una licencia compatible. Subir código al repositorio público no autoriza por sí solo una publicación en CurseForge; revisar la versión en juego y seguir el flujo de Releases acordado.
