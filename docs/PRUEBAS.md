# Validación dentro de WoW

Estado: **pendiente**. Las comprobaciones locales de Lua no sustituyen estas pruebas. Registrar versión exacta del cliente, modo de juego, permisos de grupo y resultado observado.

## Flujo básico

- [ ] El addon aparece como Easy Marks y carga sin errores Lua.
- [ ] Aparece el icono EM junto al minimapa, con letras centradas y legibles sobre un disco oscuro con borde dorado; su clic izquierdo abre y cierra la rueda sin comandos.
- [ ] El atajo configurable y los comandos opcionales `/emarks` y `/easymarks` abren y cierran la rueda.
- [ ] Los ocho colores corresponden a sus símbolos nativos: azul/cuadrado, verde/triángulo, violeta/diamante, rojo/cruz, amarillo/estrella, naranja/círculo, plateado/luna y blanco/calavera.
- [ ] Elegir un color con clic izquierdo no envía ninguna acción: cambia el cursor y muestra el símbolo sin una ventana explicativa; la rueda permanece abierta.
- [ ] El siguiente clic izquierdo coloca la marca y el ping en el mismo punto al soltar y sale del modo de selección. Un segundo clic no vuelve a marcar.
- [ ] Escape y clic derecho sobre el terreno cancelan sin marca ni ping; desaparece el cursor de selección y la rueda queda abierta. Escape sin selección (también después de marcar/cancelar) nunca cierra la rueda ni queda capturado por el addon.
- [ ] El icono EM sigue accesible durante la selección y cierra/cancela sin emitir señales. No hay botón de cierre en la rueda; las pequeñas × de limpieza siguen disponibles.
- [ ] Se puede elegir otro color con la rueda abierta, antes o después de marcar; solo se usa el último color elegido.
- [ ] Tras confirmar, cancelar o recibir un rechazo de WoW, vuelven a funcionar el ratón, las barras y Escape normalmente.
- [ ] Con Shift, Ctrl y Alt, el clic izquierdo conserva el mismo color y comportamiento; no hay variantes asignadas a modificadores.
- [ ] Repetir con `/console ActionButtonUseKeyDown 0` y `1`: Easy Marks confirma siempre al soltar. Restaurar después el valor preferido del jugador.

## Objetivos y ping

- [ ] Seleccionar una unidad y hacer clic derecho en cada símbolo coloca el icono correspondiente y un ping sobre esa misma unidad. Verificar con otro jugador, no solo la macro emitida.
- [ ] Elegir otra unidad antes del clic usa el objetivo actual; no cambia el objetivo automáticamente ni usa mouseover o terreno como alternativa.
- [ ] Sin objetivo seleccionado, clic derecho no marca ni envía ping, aunque el cursor esté sobre terreno válido.
- [ ] Una selección de terreno pendiente se cancela al marcar el objetivo, liberando cursor y Escape. La rueda sigue abierta y se puede marcar terreno después.
- [ ] Repetir clic derecho en el mismo símbolo conserva la marca y permite un nuevo intento de ping; mantener el botón no repite ni ejecuta antes de soltar.
- [ ] Repetir con modificadores y ambos valores de ActionButtonUseKeyDown; comprobar el comportamiento durante combate y las restricciones de arenas/grupos.
- [ ] Probar rechazo de marca, ping silenciado o límite de pings: no hay reintentos, captura atascada ni anuncios de éxito falso.
- [ ] Los tooltips distinguen «Left click: Ground» y «Right click: Target» en inglés.

## Limpieza individual

- [ ] Pasar sobre un color revela una pequeña ×; llegar hasta ella no la oculta ni provoca parpadeos. La ayuda dice «Clear» e identifica el color en inglés.
- [ ] Pasar el cursor no arma, borra ni envía ping. Salir del icono y su × oculta el control tras una breve tolerancia.
- [ ] Colocar dos colores y marcar dos unidades. Con una unidad seleccionada, pulsar una pequeña ×: desaparecen ese color del suelo y el símbolo del objetivo, aunque sean distintos; permanecen el otro color y la otra unidad. Probar clic izquierdo y derecho, al soltar, sin ping ni cierre de rueda.
- [ ] Limpiar con selección pendiente cancela el cursor, libera Escape y no coloca esa selección; después se puede elegir y colocar otro color.
- [ ] Repetir limpieza con Shift/Ctrl/Alt y ambos valores de ActionButtonUseKeyDown. El botón medio del ratón y las pulsaciones sin soltar no borran.
- [ ] Sin objetivo, ambos botones del ratón sobre una × retiran igualmente ese color del suelo sin cambiar otras unidades ni enviar ping; cancelan cualquier selección pendiente.
- [ ] Cerrar y reabrir mientras se ve la × no deja botones de limpieza visibles fuera del hover.
- [ ] Probar en combate, sin marcador colocado y con permisos insuficientes. No hay errores por código inseguro, reintentos ni anuncios falsos; se libera cualquier selección aunque WoW deniegue la acción.

## Clear all

- [ ] El botón está en el centro y permanece visible mientras la rueda esté abierta; no interfiere con el agarre de debajo ni las pequeñas ×.
- [ ] Colocar varios colores de suelo y símbolos sobre varias unidades del grupo, incluidos enemigos marcados por el grupo. Sin objetivo seleccionado, pulsar Clear all y confirmar con otro jugador que desaparecen todos los marcadores e iconos.
- [ ] Repetir con objetivo seleccionado, ambos clics, Shift/Ctrl/Alt, ambos valores de ActionButtonUseKeyDown y durante combate. Se limpia una vez al soltar, sin ping, y la rueda sigue abierta.
- [ ] Con una selección de terreno pendiente, Clear all cancela el cursor y libera Escape sin colocar esa selección. Se puede marcar de nuevo después.
- [ ] Verificar en cliente español que limpia todos los colores, incluida la calavera; el argumento interno de todos debe estar localizado aunque la interfaz diga Clear all.
- [ ] Probar permisos insuficientes y retirada de suelo/unidades denegada por separado: no hay reintentos ni anuncio de éxito. Revisar el visor y los mensajes nativos si una de las dos operaciones falla.

## Apariencia y arrastre

- [ ] El fondo es circular y translúcido; no hay título ni × de cierre superior. Los ocho iconos conservan contraste y quedan centrados alrededor del disco.
- [ ] En la rueda compacta, los iconos conservan su tamaño y hay menos espacio vacío. Se puede pulsar cada símbolo y alcanzar su × sin activar el vecino, Clear all ni el agarre; comprobarlo con la escala habitual de UI.
- [ ] Dos líneas pequeñas debajo de Clear all indican la zona de arrastre, sin solaparse con ese botón, los marcadores o sus ×. El icono EM se ve centrado con la escala habitual de UI.
- [ ] Tooltips, nombres de colores, atajo, mensajes propios y visor de errores están en inglés, incluso en clientes españoles; las acciones nativas siguen funcionando.
- [ ] Arrastrar el pequeño agarre fuera de combate mueve la rueda sin marcar, limpiar ni enviar ping; al soltar, deja de seguir al ratón.
- [ ] Una selección pendiente se cancela al empezar a arrastrar o hacer clic derecho en el agarre. Escape y minimapa siguen liberando la entrada.
- [ ] Cerrar y reabrir conserva la posición; recargar o volver a entrar también. Los bordes de pantalla mantienen visibles los marcadores y el agarre.
- [ ] Entrar en combate durante el arrastre lo detiene sin errores. Intentar arrastrar en combate no mueve la rueda y los botones de marcado siguen operativos.
- [ ] Comprobar el arrastre con la escala habitual de UI y a los cuatro bordes. El fondo vacío deja pasar clics y los controles siguen recibiéndolos.

## Registro de errores

- [ ] El clic derecho en EM abre el visor de errores sin armar el cursor ni enviar señales.
- [ ] Sin fallos, el visor muestra «no errors recorded»; Escape y el botón de cierre ocultan ese visor, no la rueda.
- [ ] Con un error propio reproducible, el visor incluye fecha, contexto, detalle, pila y versiones. Copiar con Ctrl+A/Ctrl+C produce el texto completo.
- [ ] Con varias entradas, funcionan desplazamiento, selección y reapertura del visor.
- [ ] Tras cerrar sesión o recargar la interfaz, se conservan los errores registrados. No se requiere provocar fallos durante una partida.
- [ ] Los errores de carga anteriores al inicio del logger se investigan según [DIAGNOSTICO.md](DIAGNOSTICO.md).

## Combate y grupos

- [ ] Abrir con el botón/atajo, seleccionar, confirmar y cancelar durante combate no provoca errores de acción bloqueada.
- [ ] `/emarks` durante combate explica que hay que usar botón/atajo sin intentar cambiar marcos protegidos.
- [ ] Comprobar con un compañero sin el addon que ve las dos señales.
- [ ] Probar como miembro y como líder; en banda, revisar también permisos de ayudante.
- [ ] Probar en una mítica+ fuera y dentro de combate, al morir y al cambiar de zona.
- [ ] Probar arenas en preparación, combate y transición de rondas. Registrar si los marcadores nativos están permitidos o se eliminan entre fases.
- [ ] Probar límites de frecuencia, pings silenciados y pings deshabilitados por el grupo. El addon debe liberar el cursor aunque una acción sea denegada.

## Superposiciones

- [ ] Probar un clic sobre una unidad: debe apuntar al terreno bajo el cursor, sin seleccionar a la unidad como destino del ping.
- [ ] Probar zona inválida o cielo: el rechazo del cliente no deja la capa de selección atascada.
- [ ] Verificar la superposición con paneles: la rueda/minimapa reciben sus propios clics; otros paneles pueden interceptar la entrada según su nivel. Cancelar antes de usarlos y comprobar que cerrar Easy Marks libera el cursor.
- [ ] Cambiar de ventana mientras está armado y volver: el modo puede seguir activo; Escape debe cancelarlo.
- [ ] Confirmar que los ocho símbolos y el icono son legibles con la escala de interfaz habitual y que no aparece un panel de instrucciones al seleccionar.

Para informar de un fallo: pasos exactos, error Lua o mensaje visible, estado de combate, color, modificadores, versión de WoW y cuál de las dos señales llegó. No marcar un caso como correcto solo porque se emitió el intento: comprobar el resultado visible.
