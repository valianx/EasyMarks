## Context

La motivación y el alcance están en `proposal.md`. La alpha local en `addon/EasyMarks` tiene una copia de prueba instalada, con aceptación en el cliente pendiente. Las acciones de marcado/ping están protegidas por WoW y el clic final debe ser una acción manual del jugador.

## Goals / Non-Goals

**Goals:** conservar una transición explícita entre rueda, cursor armado y confirmación/cancelación, con el mínimo código necesario y sin dependencias dentro de WoW.

**Non-Goals:** introducir un framework de interfaz, red propia, sincronización entre addons o un panel general de preferencias de presentación.

## Decisions

- Usar Lua compatible con las APIs de Retail y XML para el atajo; TOC como manifiesto. Python solo sirve para desarrollo y empaquetado.
- Separar `Domain/Markers.lua` (datos, validación y generación pura), `UI/Wheel.lua` (APIs visuales/protegidas; crea la interfaz y devuelve su función de apertura/cierre), `Core.lua` (ciclo de vida y comandos) y `Errors.lua` (diagnóstico transversal). Usar el namespace privado del addon, sin contenedor de dependencias, buses de eventos propios ni jerarquías de clases.
- Guardar pruebas unitarias en `tests/unit`, integración en `tests/integration` y la simulación de WoW en `tests/support`. Los unitarios cargan Lua 5.1 directamente; solo el logger necesita dobles mínimos de reloj, metadatos y salida de errores. No replicar el motor protegido como garantía de compatibilidad.
- Usar una rueda circular semitransparente de 200 × 200, sin título ni cierre, con marcadores a radio 68. La compactación reduce fondo y separación; conserva iconos de 29 × 29, botones de 42 × 42, bases de 40 y limpieza de 18 × 18, sin escalar la interfaz. Empieza centrada y guarda coordenadas relativas al centro en `EasyMarksDB.position`. El icono del minimapa conserva su posición fija y alterna la visibilidad.
- Clear all ocupa el centro; un agarre de 32 × 16 con dos líneas discretas queda justo debajo y permite arrastrar sin limpiar. El icono EM usa letras y círculos concéntricos nativos, anclados al centro del botón, sin texturas externas ni borde asimétrico. Los textos del producto son ingleses; documentación en español. No se modifican errores históricos ni originales del cliente.
- El agarre mueve la rueda mediante coordenadas del cursor y actualizaciones de ancla únicamente fuera de combate. Ocultar, soltar o entrar en combate termina el estado local de arrastre sin necesitar detener movimiento nativo de un frame protegido. El contenedor visual no captura ratón; sí sus botones y el pequeño agarre central.
- Mantener la rueda abierta durante selección, confirmación y cancelación. La capa de selección queda bajo la rueda y el icono para permitir elegir otro color o cerrar. La rueda posee el binding de Escape solo mientras hay selección y lo libera al cancelar/confirmar; Escape no cierra la rueda. No se muestra panel de instrucciones.
- Dejar `Bindings.xml` fuera de la lista TOC para que lo procese el cargador de atajos del cliente. Usar `SecureHandlerSetFrameRef` al configurar referencias sin depender de métodos inyectados por `OnLoad` de plantillas combinadas.
- Cargar `Errors.lua` antes del código principal; instrumentar inicialización y callbacks propios con `xpcall`, mantener 30 entradas deduplicadas en `EasyMarksDB` y exponer un visor de texto mediante clic derecho en el minimapa. Los errores XML previos a Lua se consultan en `Logs/FrameXML.log`; SavedVariables se escribe al recargar o cerrar sesión, no en tiempo real.
- Preparar botones y referencias antes de combate. La elección del color y la visibilidad protegida cambian mediante snippets seguros. El código visual solamente presenta información.
- Precrear un botón de limpieza por color con `SecureActionButtonTemplate`: ambos botones del ratón ejecutan la misma macro, `/cwm ID` y `/click [@target,exists] EasyMarksClearTarget LeftButton`. El delegado es una acción nativa `raidtarget`/`clear` sobre `target`, no otra macro. Clear all usa `/cwm ALL` (con el valor localizado de la global `ALL`) y `/click EasyMarksClearAllUnits LeftButton`; este segundo delegado es `raidtarget`/`clear-all` (`RemoveRaidTargets`), sin requerir objetivo ni recorrer unidades en Lua. Los dos delegados están precreados, sin captura física de ratón, y ejecutan al soltar independientemente del CVar. No usar `/cwm 0` como sinónimo de todos ni `/run` para APIs protegidas.
- Un wrapper seguro de cada control de limpieza cancela la selección antes del clic izquierdo o derecho. El hover envuelve `OnEnter` después del tooltip, muestra la × y usa `RegisterAutoHide(0.15)`/`AddToAutoHide` para mantenerla accesible desde ambos botones. Cerrar la rueda oculta y desregistra estas ×; Clear all permanece visible mientras la rueda esté abierta. Ningún timer retira marcadores y ninguna limpieza envía ping.
- El clic final activa una macro de marcador `[@cursor]` y ping de atención `[@cursor] 5`. Una capa transparente recibe ese clic y se cierra después de procesarlo. Se fija la ejecución al soltar para evitar dependencia del CVar global.
- Los símbolos usan botones de acción seguros: el pre-handler izquierdo arma el terreno y el derecho cancela la selección antes de ejecutar `/tm [@target,exists] !N` y `/ping [@target,exists] 5`. `N` es el índice de icono de unidad, distinto del marcador de mundo. El prefijo nativo `!` conserva el símbolo al repetir. Ambas condiciones impiden acciones sin objetivo; el parser nativo de ping corta antes de cualquier fallback. Comandos localizados suministrados por el adaptador; no se comparan datos secretos ni se toman decisiones de objetivos en Lua propio.
- Usar el cursor nativo de ping y un símbolo de color adjunto. El retículo nativo del marcador por sí solo no ofrece aquí un callback demostrado que una el ping al clic final; se conserva la confirmación explícita de la capa del prototipo.
- Separar las pruebas de transiciones simuladas de las pruebas de cliente. Se reutiliza evidencia anterior únicamente si cubre el comportamiento aprobado y la revisión no la invalida.

## Risks / Trade-offs

- Dos acciones independientes pueden tener resultados distintos → mostrar intención, respetar errores nativos y no reintentar.
- Restricciones por instancia, fase de arena o permisos → probar en el cliente real y registrar las limitaciones antes de anunciar compatibilidad.
- `@cursor` puede apuntar al mundo bajo otros paneles → documentarlo y mantener Escape/clic derecho para cancelar antes de usar la interfaz.
- Los mocks no reproducen seguridad ni eventos del cliente → exigir prueba manual de combate, cancelación, modificadores y recepción por otro jugador.
- El código público del cliente admite `/click` sobre acciones nativas; el modelo comprueba ese cableado y rechaza delegar otra macro. Aun así, la ejecución real de ambas limpiezas en un clic y sus permisos deben comprobarse en Midnight antes de declarar aceptación.

## Migration Plan

Después de la aprobación, revisar el prototipo contra los escenarios, corregir lo necesario, comprobar la versión de Retail y generar el ZIP. Instalar exclusivamente `EasyMarks` en la ruta proporcionada por Mario. Si ya existe una copia, conservarla antes de actualizarla. Para desactivar la alpha, desmarcar Easy Marks en la lista de addons; no cambiar archivos del juego ni otros addons.

La arquitectura mantenible y las instrucciones de contribución se documentan en `docs/ARCHITECTURE.md`, `CONTRIBUTING.md` y `AGENTS.md`, sin duplicar los criterios normativos del spec.
