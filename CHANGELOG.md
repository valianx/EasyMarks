# Cambios

## 0.1.11

- Versión 0.1.11 sin sufijo alpha; el paquete se prepara con tipo release.
- Metadatos de compatibilidad para WoW 12.1.5 (Interface 120105).
- README breve en inglés sin números de versión; las versiones se declaran en el TOC y en los metadatos de publicación.
- Se conserva el comportamiento de 0.1.11-alpha; las comprobaciones dentro del juego siguen pendientes.

## 0.1.11-alpha

- Licencia MIT para el código y la documentación propios; el ZIP incluye una copia del archivo LICENSE de la raíz.
- Código de conducta y guía para reportar errores, probar el addon y enviar contribuciones desde GitHub.
- Validación del paquete ampliada para rechazar licencias ausentes o modificadas antes de una subida.
- Sin cambios en las acciones ni en la interfaz del addon; las pruebas reales pendientes siguen abiertas.

## 0.1.10-alpha

- Rueda compacta: fondo de 232 a 200 y radio de botones de 80 a 68, alrededor de un 26 % menos de superficie cubierta.
- Iconos, botones, × de limpieza, Clear all y agarre conservan sus tamaños; se aprovecha el espacio sin escalar la interfaz.
- Se conservan las acciones de marcado, limpieza, cancelación y arrastre. Apariencia y comodidad con la escala real de WoW pendientes de comprobar.

## 0.1.9-alpha

- La pequeña × retira ese color del suelo y el símbolo del objetivo con clic izquierdo o derecho; sin objetivo sigue limpiando el suelo.
- Clear all central retira todos los marcadores de suelo y símbolos de unidades del grupo, incluso sin objetivo, mediante acciones nativas y sin ping.
- El agarre queda debajo de Clear all; arrastrar no activa limpieza. Ambas limpiezas cancelan la selección y mantienen la rueda abierta.
- Comandos y argumento de limpieza global adaptados al idioma del cliente; la interfaz conserva textos ingleses.
- 58 pruebas locales correctas: 17 unitarias, 39 de integración y 2 de manifiesto/spec. Se reprodujo el fallo de limpieza del objetivo antes de corregirlo; validación real en WoW pendiente.

## 0.1.8-alpha

- Rueda sin título ni × de cierre; el icono del minimapa alterna su visibilidad y cancela selecciones pendientes.
- Icono EM centrado sobre fondo oscuro y borde dorado, dibujado con recursos nativos.
- Agarre pequeño en el centro para conservar el arrastre fuera de combate; se mantienen las × de limpieza por marcador.
- Adaptadas las regresiones de cierre al minimapa; 49 pruebas locales correctas. Apariencia y entrada real pendientes de comprobar en WoW.

## 0.1.7-alpha

- Clic derecho en un símbolo marca y envía ping al objetivo seleccionado; clic izquierdo conserva el marcado de terreno.
- Clic derecho en la pequeña × limpia el objetivo sin ping; clic izquierdo limpia ese marcador de mundo.
- Sin objetivo no hay señales ni destino alternativo; marcar o limpiar un objetivo cancela la selección pendiente sin cerrar la rueda.
- Repetir el símbolo lo conserva; nuevos pings requieren nuevos clics manuales. Ayudas en inglés para Ground/Target.
- 49 pruebas locales correctas: 13 unitarias, 34 de integración y 2 de manifiesto/spec. Validación dentro de WoW pendiente.

## 0.1.6-alpha

- Botón × de limpieza individual al pasar el cursor sobre cada color; solo borra al hacer clic.
- Quita únicamente ese marcador sin ping, cancela cualquier selección pendiente y mantiene la rueda abierta.
- Controles preparados mediante acciones y transiciones seguras; permisos e interacción en combate pendientes de validación real.
- Retirado el óvalo del título; dos líneas discretas indican el arrastre.
- 39 pruebas locales correctas, incluidas cinco nuevas de limpieza, hover y liberación del cursor.

## 0.1.5-alpha

- Fondo ovalado sutil detrás del título para identificar la zona arrastrable, manteniendo la legibilidad.
- Textos propios del addon en inglés: ayudas, colores, atajo, mensajes y visor de errores.
- Escape solo cancela una selección pendiente; la rueda permanece visible y se cierra con × o minimapa.
- Regresión de Escape comprobada dentro/fuera de combate simulado; 34 pruebas locales correctas.

## 0.1.4-alpha

- Fondo circular con 32 % de opacidad y bases translúcidas para los iconos, sin bordes cuadrados opacos.
- Título elevado por encima del círculo y cierre alineado en la cabecera.
- Arrastre desde el título fuera de combate, con posición recordada entre sesiones.
- El arrastre se detiene al soltar, ocultar o entrar en combate; no usa movimiento nativo de frames protegidos.
- Las zonas vacías de la rueda dejan pasar clics. Se conservan marcado único, Escape y rueda persistente.
- Cuatro pruebas de integración nuevas para arrastre, interrupción y restauración: 33 pruebas locales correctas.

## 0.1.3-alpha

- Separación ligera: dominio de marcadores, interfaz WoW, arranque y diagnóstico.
- Diez pruebas unitarias sin cliente WoW; diecisiete de integración y dos de manifiesto/spec.
- Mock del cliente extraído a `tests/support`; comandos para ejecutar cada nivel por separado.
- Paquete actualizado para incluir los módulos y conservar su orden de carga.

## 0.1.2-alpha

- Corregido el cursor de marcado permanente: el pre-handler ahora habilita el post-handler que libera la selección.
- Una selección permite marcar una sola vez; Escape y clic derecho cancelan y restauran el cursor.
- La rueda permanece abierta y accesible hasta cerrarla; × e icono del minimapa cancelan cualquier selección pendiente.
- Escape cancela primero la selección; sin selección pendiente, cierra la rueda.
- Retirada la ventana explicativa y los textos de instrucciones dentro de la rueda.
- Corregido el contrato del mock que ocultaba el fallo del post-handler; regresión reproducida antes de aplicar la solución.

## 0.1.1-alpha

- Estrella amarilla junto al minimapa: clic izquierdo para la rueda y derecho para los errores.
- Registro de hasta 30 errores propios con contexto, pila y versiones, persistencia local y texto copiable.
- Corregida la inclusión de `Bindings.xml` en el TOC, que causaba errores del cargador XML del cliente.
- Referencias seguras entre marcos sin depender de métodos añadidos por `OnLoad` de las plantillas.
- Comandos opcionales registrados antes de construir la interfaz para informar de fallos de inicio.
- Validación de esta actualización dentro de WoW pendiente.

## 0.1.0-alpha

- Rueda de ocho marcadores de mundo con iconos nativos.
- Cursor de ping y símbolo del color mientras se elige el terreno.
- Confirmación manual con marcador y ping «Mira aquí» al soltar el clic izquierdo.
- Cancelación con Escape o clic derecho.
- Botón EM, atajo configurable y comandos `/emarks` y `/easymarks`.
- Primera versión local; validación en WoW pendiente.
