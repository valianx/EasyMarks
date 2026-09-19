# Cómo contribuir a Easy Marks

Gracias por ayudar a mejorar Easy Marks. Puedes reportar errores, proponer mejoras, probar el addon en WoW o enviar código y documentación. Aceptamos issues y pull requests en español o inglés; los textos visibles del addon permanecen en inglés.

El proyecto está en fase alpha. Lee el [README](README.md), el [código de conducta](CODE_OF_CONDUCT.md) y la [arquitectura](docs/ARCHITECTURE.md) antes de empezar. La licencia aplicable está en [LICENSE](LICENSE); conserva los [avisos de terceros](THIRD_PARTY_NOTICES.md) que correspondan.

## Reportar errores y proponer mejoras

Busca primero en los [issues existentes](https://github.com/valianx/EasyMarks/issues). Si el problema no está reportado, abre un [issue nuevo](https://github.com/valianx/EasyMarks/issues/new) con:

- Versión de Easy Marks y versión/build de WoW Retail.
- Pasos para reproducirlo, resultado esperado y resultado observado.
- Modo de juego, estado de combate y permisos de líder/asistente, si son relevantes.
- Si falló el marcador, el ping, la limpieza o la interfaz.
- Mensaje de error y captura, cuando ayuden a entenderlo.

El clic derecho en EM abre los errores propios del addon. Revisa el texto antes de compartirlo: omite nombres de jugadores, conversaciones, rutas personales y cualquier credencial. No adjuntes carpetas WTF ni SavedVariables completas. Consulta [diagnóstico](docs/DIAGNOSTICO.md) para los límites del registro.

Para una función nueva, describe qué quieres conseguir y un ejemplo dentro del juego. Conviene acordar las funciones grandes en un issue antes de invertir tiempo en implementarlas. Las pruebas manuales y mejoras de documentación también son contribuciones útiles.

## Preparar el proyecto

Necesitas Git y Python 3.10 o posterior. WoW solo es necesario para verificar el comportamiento real del addon. Haz un fork del repositorio y clona tu fork; si ya tienes permiso de escritura, puedes trabajar en una rama del repositorio original.

Desde la raíz del checkout, en PowerShell:

```powershell
git switch -c fix/short-description
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
.\.venv\Scripts\python.exe tools/package.py
```

En Linux/macOS utiliza `.venv/bin/python` en lugar de `.\.venv\Scripts\python.exe`. El paquete queda en `dist/`; Python, Lupa y las herramientas de desarrollo no se distribuyen dentro del addon. El ZIP incluye los archivos de ejecución y una copia de la licencia del proyecto.

## Organización y cambios

- Edita la fuente en `addon/EasyMarks`. La copia de `Interface/AddOns/EasyMarks` se utiliza para probar, no para desarrollar.
- Coloca reglas y datos puros en `Domain/Markers.lua`, integración con WoW en `UI/Wheel.lua`, arranque en `Core.lua` y diagnóstico en `Errors.lua`. Conserva módulos pequeños y evita capas sin una responsabilidad concreta.
- Mantén las acciones protegidas vinculadas a una entrada manual. No automatices posiciones, decisiones de combate ni acciones protegidas mediante timers.
- Conserva `Bindings.xml` fuera de la lista de carga del TOC: WoW tiene un cargador específico para atajos.
- Mantén los textos propios de la interfaz en inglés. El código y los nombres de APIs usan sus identificadores originales; la documentación del proyecto está en español.
- No incluyas dependencias de ejecución ni código de otros addons sin revisar antes su licencia, atribución y necesidad. Las ideas de otros proyectos no autorizan copiar sus archivos.

## Verificar el cambio

Ejecuta las pruebas relevantes para lo que cambiaste. Para una corrección, intenta reproducir primero el fallo y conserva una prueba que compruebe el comportamiento esperado, cuando sea viable.

```powershell
# Lógica aislada
.\.venv\Scripts\python.exe -B -m unittest discover -s tests/unit -v

# Flujo de interfaz contra un contrato simulado de WoW
.\.venv\Scripts\python.exe -B -m unittest discover -s tests/integration -v

# Suite completa, manifiesto y límites de especificaciones
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v

# Preparación local del ZIP y metadatos, sin subir archivos
.\.venv\Scripts\python.exe -m tools.release
```

`tests/support/wow_mock.lua` concentra la simulación. Las pruebas unitarias del dominio no requieren APIs de WoW. Los mocks no demuestran seguridad en combate, apariencia, recepción de pings ni permisos reales.

Para probar dentro de WoW, copia el addon según el [README](README.md), ejecuta `/reload` y sigue [PRUEBAS.md](docs/PRUEBAS.md). Al instalar por primera vez puede ser necesario reiniciar el juego. Indica en tu PR qué escenarios probaste y cuáles quedaron pendientes.

## Enviar un pull request

1. Mantén cada PR centrado en un problema o mejora. Usa una rama descriptiva, como `fix/short-description` o `docs/installation`.
2. Actualiza la documentación si cambia el comportamiento o la forma de usar el addon. Las versiones y publicaciones las coordina el mantenedor.
3. Publica la rama en tu fork y abre el PR hacia `valianx/EasyMarks:main`.
4. Describe el problema, el resultado del cambio, cómo lo verificaste y cualquier limitación pendiente. Para cambios visuales, incluye una captura real del juego si es posible.
5. Revisa el resultado de **Test and package** y responde a los comentarios del mantenedor.

CI ejecuta las pruebas y guarda un ZIP como artefacto durante 14 días. No necesita credenciales de CurseForge para validar una contribución. No subas `dist/`, entornos virtuales, registros de ejecución ni secretos.

Al enviar una contribución, confirma que tienes derecho a aportarla bajo la licencia del proyecto; conservas la autoría de tus cambios. No se exige una cesión de copyright ni un CLA adicional.

## Especificaciones y mantenimiento

El mantenedor utiliza Team Harness `spec` y OpenSpec para registrar decisiones y escenarios del addon. No necesitas instalar Team Harness ni usar un agente para reportar un error o enviar un PR. Si tu cambio modifica una especificación existente en `openspec/changes/`, coordina su actualización en el issue o PR. Los cambios de documentación y las tareas del repositorio no requieren inventar una capacidad nueva.

Para validar especificaciones se necesita Node 20.19 o posterior y la versión fijada de OpenSpec:

```powershell
npx --yes @fission-ai/openspec@1.9.0 validate manual-ground-marks --strict
```

Sustituye el nombre al trabajar en otro cambio. No actualices las herramientas incidentalmente junto con una función del addon. Los agentes siguen además [AGENTS.md](AGENTS.md) y utilizan ramas `codex/…`; ese prefijo no es obligatorio para contribuciones humanas.

La [guía de publicación](docs/PUBLICACION.md) explica los tags, Releases y credenciales. Un PR o un push no publica por sí solo en CurseForge. No crees tags ni actives subidas como parte de una contribución corriente.
