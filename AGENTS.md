# Easy Marks

## Proyecto y alcance

Addon personal para WoW Retail/Midnight. Fuente en `C:\Users\mario\projects\EasyMarks`; el directorio `Interface/AddOns/EasyMarks` del juego es una copia para probar, no el lugar para desarrollar. Responder en español. Mantener README.md breve, completamente en inglés y sin números de versión del addon o de WoW; la documentación técnica restante se mantiene en español, con nombres de APIs e identificadores de código en su forma original.

Los textos visibles propios del addon van en inglés, incluidos tooltips, atajos, chat, nombres de marcadores y visor de errores. Conservar el idioma original de errores históricos o recibidos del cliente; los comandos de WoW siguen usando sus nombres localizados.

## Flujo de trabajo

- Seguir Team Harness `spec`. Leer el cambio activo en `openspec/changes/` y las especificaciones vigentes antes de modificar comportamiento.
- Conservar cambios ajenos. La existencia del prototipo o un ZIP no demuestra aprobación ni aceptación del cambio.
- Mantener tareas y evidencia coherentes. El plan vive en el destino de trabajo configurado en Team Harness; no crear estado de pipeline para este flujo.
- La fuente se aloja en el repositorio público `valianx/EasyMarks`; Mario autorizó expresamente cambiar su visibilidad a público. El proyecto de autor ya fue creado y Mario eligió el empaquetador nativo de CurseForge por tags. Falta registrar su enlace/ID y validar su configuración y el primer archivo. La alternativa de subida por Actions sigue desactivada; publicar el repositorio no publica automáticamente el addon en CurseForge.
- El código y la documentación propios se distribuyen bajo MIT. Mantener LICENSE en la raíz y dentro del ZIP; no relicenciar materiales de terceros. CONTRIBUTING.md explica el flujo público y CODE_OF_CONDUCT.md las normas de participación.
- CI comprueba y empaqueta cada push/PR. El flujo CurseForge ofrece preparación sin credenciales; la subida usa el ZIP validado, un tag coherente con el TOC y secretos solo en el paso de subida. No imprimir tokens, guardarlos en archivos ni repetir a ciegas una subida de resultado incierto.

## Código

- Lua y XML del cliente, sin dependencias externas en ejecución. Usar recursos nativos de WoW.
- Respetar el entorno protegido: acciones manuales mediante botones seguros y transiciones seguras; nunca automatizar puntos ni llamar acciones protegidas desde timers.
- No alterar marcos protegidos desde callbacks inseguros durante combate.
- El hover de limpieza usa un wrapper seguro y auto-hide nativo; no sustituirlo por `Show`/`Hide` inseguros ni retirar marcadores al pasar el cursor. Conservar tooltip, grupo icono/× y limpieza de registros al cerrar.
- Ambas pulsaciones sobre una × limpian ese color del suelo y el objetivo; Clear all retira todo el suelo y los símbolos de unidades del grupo, incluso sin objetivo. Conservar los delegados de acción nativa y la global localizada `ALL`; no encadenar macros ni usar `/run` para acciones protegidas. Arrastrar nunca limpia.
- El arrastre de la rueda actualiza anclas solo fuera de combate y limpia su estado al soltar, ocultar o entrar en combate. No sustituirlo por `StartMoving` sin resolver cómo detener el movimiento protegido si empieza combate.
- Los marcadores de mundo y los iconos de objetivo tienen índices distintos; conservar el mapeo explícito.
- Clic izquierdo en símbolos prepara terreno; derecho ejecuta marca y ping sobre `target`, con condición `exists` en ambas líneas. Mantener la limpieza sin ping y no introducir fallback a mouseover/terreno ni comparar valores secretos de unidad en Lua propio.
- Mantener el addon pequeño. Separar módulos cuando exista una responsabilidad concreta que lo justifique.
- `Domain/Markers.lua` debe cargarse sin APIs de WoW. `UI/Wheel.lua` integra la interfaz con el cliente; `Core.lua` coordina el arranque; `Errors.lua` concentra diagnóstico. No añadir frameworks, contenedores o capas vacías.
- Mantener `Bindings.xml` fuera del listado del TOC: WoW usa un cargador específico para los atajos.
- Instrumentar los callbacks propios relevantes mediante `Errors:Wrap` o `Errors:Run`. No sustituir el manejador global de errores ni registrar datos de combate, chat o jugadores. Mantener el registro acotado.

## Verificación

Consultar `CONTRIBUTING.md` para comandos. Ejecutar las comprobaciones relevantes y revisar el ZIP. No presentar mocks Lua como prueba de seguridad, apariencia o compatibilidad del cliente. Registrar versión de WoW y escenarios pendientes en las pruebas manuales.

Separar pruebas unitarias (`tests/unit`) de integración (`tests/integration`). Mantener el contrato simulado de WoW en `tests/support/wow_mock.lua`; cuando un fallo revele una diferencia con el cliente, corregir el mock y reproducir el fallo antes de validar la solución. En `SecureHandlerWrapScript`, el post-handler requiere un segundo retorno no nil del pre-handler.

No copiar código de otros addons sin comprobar su licencia. No guardar credenciales, ajustes personales de WoW ni registros de ejecución dentro del paquete.
