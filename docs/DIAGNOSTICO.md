# Errores y diagnóstico

Haz **clic derecho en el icono EM de Easy Marks junto al minimapa**. El visor muestra los errores más recientes primero. Puedes seleccionar el texto y copiarlo con **Ctrl+A y Ctrl+C**; Escape o el botón de cierre ocultan la ventana. No se necesitan comandos para consultarlo.

## Qué se registra

- Fallos de inicialización y de los callbacks de Easy Marks instrumentados con `Errors:Run` o `Errors:Wrap`.
- Eventos `ADDON_ACTION_BLOCKED` y `ADDON_ACTION_FORBIDDEN` atribuidos por WoW a `EasyMarks`.
- Fecha y hora local, contexto, mensaje, pila de llamadas y versiones de Easy Marks y WoW.

Se conservan hasta **30 entradas**; las repeticiones consecutivas del mismo error se agrupan mediante un contador. El mensaje y la pila tienen límites de longitud. El registro no recoge chats, nombres de jugadores ni eventos de combate, y no envía información a ningún servidor propio.

El manejador global de errores del cliente se conserva. Si falla un callback instrumentado, también se informa en el chat y se entrega el error al manejador existente de WoW, que puede estar integrado con otra herramienta de diagnóstico.

## Archivo en disco

WoW guarda `EasyMarksDB` mediante `SavedVariables` al recargar la interfaz o cerrar sesión. No es un archivo escrito en tiempo real y un cierre inesperado puede perder los errores recientes.

Además de `errors`, la misma tabla contiene `position`, con las coordenadas de la rueda movida por el jugador. Guardar una posición no borra el registro de errores.

La ruta habitual de esta instalación es:

```text
C:\Program Files (x86)\World of Warcraft\_retail_\WTF\Account\<cuenta>\SavedVariables\EasyMarks.lua
```

`<cuenta>` es la carpeta de la cuenta usada. Este archivo es distinto del código en `Interface/AddOns/EasyMarks`; no se incluye en el ZIP ni debe añadirse al repositorio. Para informar de un fallo, normalmente basta con copiar el texto del visor.

## Si no aparece el icono

Un error de sintaxis o carga puede ocurrir antes de que se inicie el logger; el registro propio no puede garantizar su captura. Revisa el mensaje Lua del cliente y, para fallos del cargador XML, este registro nativo:

```text
C:\Program Files (x86)\World of Warcraft\_retail_\Logs\FrameXML.log
```

Si un fallo ocurre durante la construcción de la interfaz, se intenta guardar con contexto `startup`, aunque el icono todavía no exista. Cierra sesión para que WoW escriba las variables guardadas y revisa `EasyMarks.lua`. Los comandos `/emarks` y `/easymarks` también pueden mostrar ese fallo de inicio; son una alternativa de diagnóstico, no un requisito de uso.

El visor, sus mensajes y los contextos nuevos de Easy Marks están en inglés. Los registros de versiones anteriores y los mensajes recibidos de WoW conservan su idioma original.

## Límites

No se interceptan todos los errores del juego ni de otros addons. Los errores en código protegido o callbacks sin instrumentar pueden quedar únicamente en el manejador nativo. Los eventos de bloqueo pueden atribuir una cadena de modificaciones a otro addon, por lo que el filtro de Easy Marks no cubre todos los casos relacionados.

Un marcador o ping rechazado por permisos, límites o restricciones de instancia no siempre genera un error Lua. Un registro vacío **no confirma que las señales hayan llegado**: hay que observar el resultado en el cliente y con otro jugador.

Al reportar un fallo, añade los pasos, modo de juego, estado de combate y si falló el marcador, el ping o ambos. Ver [PRUEBAS.md](PRUEBAS.md).
