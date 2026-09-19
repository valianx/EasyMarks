## Purpose

Permitir que un jugador señale manualmente una zona del terreno o su objetivo seleccionado mediante símbolos y pings nativos, desde una misma rueda, con selección visible y cancelación clara.

## ADDED Requirements

### Requirement: Selección de marcador

Easy Marks SHALL ofrecer una rueda con los ocho marcadores de mundo nativos, accesible mediante un icono visible junto al minimapa y un atajo configurable, además de un comando opcional fuera de combate.

#### Scenario: Abrir sin comandos
- **WHEN** el addon está activado y el jugador hace clic izquierdo en el icono de Easy Marks junto al minimapa
- **THEN** se abre o cierra la rueda sin escribir comandos en el chat, también durante combate mediante mecanismos permitidos.

#### Scenario: Elegir un color
- **WHEN** el jugador abre la rueda y hace clic izquierdo en uno de los ocho colores
- **THEN** el addon conserva el símbolo/color elegido y espera un clic posterior en el terreno, sin enviar aún una marca ni un ping; la rueda permanece abierta y accesible.

#### Scenario: Rueda persistente y cierre explícito
- **WHEN** el jugador confirma o cancela la selección
- **THEN** la rueda permanece abierta para elegir otro color; el icono EM del minimapa la cierra y cancela cualquier selección pendiente sin emitir señales. La rueda no tiene título ni botón de cierre; se conservan los controles pequeños de limpieza.

#### Scenario: Abrir mediante comando
- **WHEN** el jugador escribe `/emarks` o `/easymarks` fuera de combate
- **THEN** la rueda cambia entre abierta y cerrada sin interferir con los comandos nativos de emotes.

### Requirement: Limpieza manual por color

Easy Marks SHALL revelar un botón pequeño de limpieza al pasar el cursor sobre cada icono de color. Un clic izquierdo o derecho intentará quitar ese marcador de mundo y el símbolo que tenga el objetivo seleccionado, sin distinguir botones. Cancelará cualquier selección pendiente, mantendrá la rueda abierta y no enviará ping. Pasar el cursor no ejecutará acciones.

#### Scenario: Descubrir y alcanzar el botón
- **WHEN** el jugador pasa sobre un color y mueve el cursor hasta su botón de limpieza
- **THEN** el control permanece accesible, muestra una ayuda en inglés y solo se oculta al salir del conjunto, sin armar ni borrar marcadores por hover.

#### Scenario: Limpiar un color
- **WHEN** el jugador pulsa el botón de limpieza de un color, con o sin selección pendiente
- **THEN** se intenta quitar ese marcador de suelo y el símbolo del objetivo seleccionado al soltar el clic, se libera el cursor y Escape, y la rueda permanece abierta sin colocar otra marca ni enviar ping. Los demás marcadores de suelo y otras unidades no se alteran.

#### Scenario: Limpieza en combate o denegada
- **WHEN** se revela y pulsa el control durante combate, o el juego deniega la retirada
- **THEN** se usan transiciones y acciones seguras sin reintentos automáticos ni éxito anunciado; la selección se libera aunque no exista una marca o falten permisos.

#### Scenario: Limpiar sin objetivo
- **WHEN** el jugador pulsa una pequeña × sin objetivo seleccionado
- **THEN** se intenta retirar igualmente ese marcador de suelo, sin buscar otras unidades ni enviar ping; cualquier selección pendiente se cancela y la rueda sigue abierta.

#### Scenario: Limpiar todo el grupo
- **WHEN** el jugador pulsa el botón central Clear all y suelta el clic izquierdo o derecho
- **THEN** se intenta retirar todos los marcadores del suelo y todos los símbolos de unidades del grupo mediante acciones nativas, incluso sin objetivo seleccionado; se cancela la selección pendiente, se libera Escape y la rueda sigue abierta sin ping. Los permisos del juego siguen aplicándose y no hay reintentos.

### Requirement: Objetivo y terreno desde la misma rueda

Easy Marks SHALL conservar el marcado de terreno por clic izquierdo y ofrecer marcado inmediato del objetivo seleccionado con ping mediante clic derecho sobre un símbolo. Usará el índice de icono de unidad correspondiente y acciones nativas sin cambios automáticos de objetivo. Las ayudas inglesas distinguirán Ground y Target.

#### Scenario: Marcar y avisar sobre el objetivo
- **WHEN** el jugador tiene un objetivo seleccionado y suelta el clic derecho en uno de los ocho símbolos
- **THEN** se intenta aplicar ese símbolo y enviar un ping de atención a esa misma unidad, sin elegir terreno, abrir captura de cursor ni cerrar la rueda. Una selección de terreno pendiente se cancela y Escape se libera.

#### Scenario: No hay objetivo o es rechazado
- **WHEN** no existe objetivo seleccionado o el cliente rechaza la marca o el ping
- **THEN** no se usa el terreno ni mouseover como destino alternativo, no hay reintentos ni anuncios falsos y el cursor queda libre; sin objetivo no se emite ninguna señal.

#### Scenario: Entrada y repetición
- **WHEN** se usa clic derecho con modificadores, ambos valores de ActionButtonUseKeyDown o durante combate, o se repite sobre un objetivo ya marcado
- **THEN** cada clic manual ejecuta como máximo un intento de marca y uno de ping, al soltar; mantener el botón no repite acciones y limpiar permanece separado del marcado.

### Requirement: Cursor de selección visible

Easy Marks SHALL distinguir visualmente el estado armado con un cursor de selección y el símbolo/color elegido, sin ventana explicativa. La indicación representa intención, no una garantía de que el punto sea válido.

#### Scenario: Mover el puntero armado
- **WHEN** el jugador mueve el puntero tras seleccionar un color
- **THEN** el símbolo elegido acompaña al cursor hasta confirmar o cancelar y no aparece una ventana con instrucciones.

### Requirement: Presentación discreta y posición de la rueda

Easy Marks SHALL mostrar la rueda con fondo circular semitransparente, sin título, cabecera ni botón de cierre. Clear all ocupará el centro y un pequeño agarre justo debajo permitirá moverla fuera de combate y guardar su posición, sin activar limpieza al arrastrar; el resto del fondo vacío no capturará clics del juego. El icono del minimapa mostrará EM centrado y legible. Los textos propios del addon se mostrarán en inglés.

#### Scenario: Abrir la rueda circular
- **WHEN** el jugador abre Easy Marks
- **THEN** ve ocho marcadores alrededor del centro de un fondo circular translúcido compacto, sin título ni cierre superior. Se reduce el espacio vacío conservando el tamaño de iconos y botones y el acceso separado a sus ×, Clear all y agarre; el icono EM del minimapa sigue accesible para cerrar, también con una selección pendiente.

#### Scenario: Agarre e idioma
- **WHEN** el jugador abre la rueda, consulta ayudas, atajos o el visor de errores
- **THEN** reconoce la zona de arrastre por las pequeñas líneas debajo de Clear all y lee los textos propios del addon en inglés, sin cambiar el idioma ni los comandos nativos del cliente. Los errores históricos y el contenido original recibido del cliente conservan su texto.

#### Scenario: Arrastrar y recordar posición
- **WHEN** el jugador arrastra el pequeño agarre central fuera de combate y suelta el ratón
- **THEN** la rueda se mueve dentro de la pantalla, cualquier selección pendiente se cancela sin señales y la posición se conserva al cerrar/abrir la rueda o recargar la interfaz.

#### Scenario: Combatir u ocultar durante el arrastre
- **WHEN** el jugador entra en combate o cierra la rueda mientras la arrastra
- **THEN** termina el arrastre sin acciones protegidas desde código inseguro, sin dejar captura de ratón pendiente y sin impedir marcar/cancelar mediante los controles habituales. No se inicia un nuevo arrastre durante combate.

### Requirement: Confirmación manual de marca y ping

Easy Marks SHALL intentar colocar el marcador elegido y enviar un único ping nativo de atención en el punto del mundo bajo el cursor al soltar el siguiente clic izquierdo. No elegirá posiciones ni emitirá señales automáticamente.

#### Scenario: Punto permitido
- **WHEN** el jugador confirma sobre terreno válido y el juego permite ambas acciones
- **THEN** aparecen la marca del color elegido y el ping en el mismo punto, se sale del modo armado, la rueda queda abierta y los compañeros con señales habilitadas pueden verlos sin instalar Easy Marks. Los clics siguientes no marcan hasta elegir de nuevo un color.

#### Scenario: Configuración de pulsación
- **WHEN** el jugador confirma con ActionButtonUseKeyDown en 0 o 1, con o sin Shift, Ctrl o Alt
- **THEN** el intento ocurre una sola vez al soltar el clic izquierdo y conserva el marcador seleccionado.

### Requirement: Cancelación y liberación del cursor

Easy Marks SHALL cancelar el modo armado con Escape o clic derecho sobre el terreno, sin enviar ninguna señal, y liberar sus indicaciones visuales y captura temporal de entrada. El clic derecho sobre los símbolos pertenece al marcado de objetivos.

#### Scenario: Cancelar una selección
- **WHEN** el jugador pulsa Escape o hace clic derecho sobre el terreno mientras el cursor está armado
- **THEN** no se emite marca ni ping, desaparece el indicador, la rueda permanece abierta y los controles habituales vuelven a estar disponibles. Escape nunca cierra la rueda.

#### Scenario: Escape sin selección
- **WHEN** el jugador pulsa Escape con la rueda abierta y sin selección pendiente, incluso después de confirmar o cancelar
- **THEN** Easy Marks deja la rueda visible y no captura esa tecla; el jugador puede cerrarla con el icono EM del minimapa.

### Requirement: Uso durante combate

Easy Marks SHALL permitir abrir la rueda con el botón o atajo, seleccionar y cancelar durante combate usando los mecanismos permitidos por WoW. La aceptación de marcas y pings depende de las restricciones del cliente y de la instancia.

#### Scenario: Interacción en combate
- **WHEN** el jugador abre la rueda, selecciona un color y confirma o cancela durante combate
- **THEN** el addon no provoca errores por mutaciones protegidas desde código inseguro; si el juego permite la señal, se ejecuta como fuera de combate.

### Requirement: Rechazos del juego

Easy Marks SHALL liberar el modo armado después de un intento aunque la marca o el ping sean rechazados. No repetirá acciones automáticamente ni afirmará un éxito sin confirmación observable.

#### Scenario: Señal denegada
- **WHEN** WoW rechaza una o ambas acciones por permisos, instancia, punto inválido o límite de pings
- **THEN** no quedan el cursor ni la captura atascados y el addon no reintenta ni anuncia que las dos señales se colocaron correctamente.

### Requirement: Entrega local documentada

Easy Marks SHALL entregarse como una alpha instalable en Retail, sin dependencias externas en ejecución, con documentación del stack, arquitectura, contribución y pruebas pendientes.

#### Scenario: Instalación de la alpha
- **WHEN** se extrae el ZIP en la carpeta de addons de Retail
- **THEN** WoW encuentra `EasyMarks/EasyMarks.toc`, se conservan los demás addons y la guía permite abrir la rueda y ejecutar las pruebas manuales; los modos no comprobados permanecen identificados como pendientes.

### Requirement: Registro de errores propios

Easy Marks SHALL conservar un registro acotado de errores capturados en su inicialización y callbacks instrumentados, y de acciones bloqueadas o prohibidas atribuidas al addon. Cada entrada incluirá fecha, contexto, detalle y versiones; el registro se guardará mediante SavedVariables al cerrar sesión o recargar la interfaz. No sustituirá el manejador global de errores ni recopilará eventos de combate ajenos.

#### Scenario: Error capturado
- **WHEN** falla un callback instrumentado de Easy Marks o WoW notifica un bloqueo atribuido al addon
- **THEN** se registra el error con su contexto y versiones, agrupando repeticiones consecutivas y conservando como máximo 30 entradas; la inicialización posterior no borra las entradas guardadas.

#### Scenario: Consulta sin comandos
- **WHEN** el jugador hace clic derecho en el icono de Easy Marks junto al minimapa
- **THEN** se abre un panel de errores con texto seleccionable para copiar, sin armar el cursor ni colocar señales.

### Requirement: Módulos y pruebas unitarias ligeras

Easy Marks SHALL separar la lógica pura de marcadores, la interfaz con APIs de WoW y el arranque. Las pruebas unitarias del dominio y del registro de errores se ejecutarán sin el cliente; las pruebas de integración del flujo conservarán explícitos sus límites como simulación.

#### Scenario: Dominio independiente
- **WHEN** un desarrollador carga el módulo de marcadores sin definir APIs de WoW
- **THEN** puede consultar los colores y generar la acción para un marcador válido con comandos suministrados; los identificadores inválidos se rechazan sin efectos externos.

#### Scenario: Ejecutar pruebas por nivel
- **WHEN** un desarrollador sigue la guía desde un entorno Python con las dependencias de desarrollo
- **THEN** puede ejecutar por separado las pruebas unitarias y las de integración, o toda la suite, sin iniciar WoW. La guía indica qué comportamiento requiere validación real.
