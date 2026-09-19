## Why

Mario necesita señalar rápidamente una zona de juego a su grupo en arenas y míticas+, por ejemplo el espacio junto a un pilar. Easy Marks permitirá elegir un color y confirmar un punto del terreno, con una indicación clara del cursor y un ping para llamar la atención.

## What Changes

- Introducir una rueda de ocho marcadores nativos, abierta con un icono EM centrado en el minimapa; conservar atajo y comando opcionales.
- Dar a la rueda un fondo circular semitransparente compacto, conservando el tamaño de los iconos y acceso a los controles; arrastrarla desde un pequeño agarre central fuera de combate y conservar su posición.
- Presentar en inglés los textos propios del addon.
- Mostrar un cursor de selección con el símbolo/color elegido hasta confirmar o cancelar.
- Revelar limpieza al pasar sobre cada color: un clic retira ese marcador de terreno y el símbolo del objetivo seleccionado, sin ping.
- Añadir Clear all central para retirar todos los marcadores de suelo y símbolos de unidades del grupo; conservar el agarre debajo.
- Mantener la rueda abierta al seleccionar, confirmar o cancelar; el icono del minimapa es su control visible de apertura/cierre. Escape solo cancela la selección. Sin ventana explicativa.
- Clic izquierdo prepara terreno con marca y ping; Escape o clic derecho sobre el terreno cancelan. Clic derecho en un símbolo marca y envía ping al objetivo seleccionado, sin cambiar de modo.
- Validar el comportamiento dentro del cliente, incluidos combate, restricciones del grupo y diferencias entre arenas y míticas+.
- Entregar una alpha local instalable, con documentación del stack, arquitectura, contribución y convenciones para agentes.
- Separar lógica de marcadores, interfaz e inicio en módulos pequeños, con pruebas unitarias sin WoW y pruebas de integración del flujo; evitar frameworks y capas sin uso.
- Registrar errores propios y bloqueos atribuidos al addon, consultables con clic derecho en el icono del minimapa y conservados mediante SavedVariables.

El prototipo inicial es material de revisión, no evidencia de aceptación. Mario autorizó implementación e instalación local, minimapa y diagnóstico. Las pruebas simuladas no sustituyen la validación en WoW.

## Capabilities

### New Capabilities

- `ground-marking`: selección manual, indicación del cursor, marcado con ping, cancelación y entrega local de Easy Marks.

### Modified Capabilities

Ninguna; no hay especificaciones previas en este proyecto.

## Impact

El código afectado está en `addon/EasyMarks`: Lua, metadatos TOC y atajos XML. Se revisarán las pruebas existentes, el empaquetador Python y la documentación. No se añadirán dependencias al addon en ejecución.

Proyecto: `C:\Users\mario\projects\EasyMarks`. Tras aprobar el plan, destino local: `C:\Program Files (x86)\World of Warcraft\_retail_\Interface\AddOns\EasyMarks`.

La fuente está en GitHub público con Actions para pruebas y publicación preparada. El proyecto CurseForge fue creado; conectar credenciales y publicar siguen pendientes.

## Non-Goals

Editar barras de acción, elegir puntos automáticamente, reconocer pilares, marcar por coordenadas programadas, eludir restricciones de Blizzard, copiar código de FastMarks, publicar en CurseForge sin preparación o prometer compatibilidad con modos no comprobados.
