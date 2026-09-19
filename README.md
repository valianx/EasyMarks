# Easy Marks

Addon personal de World of Warcraft Retail / Midnight. Versión **0.1.11-alpha**. Los textos de la interfaz del addon están en inglés.

Repositorio público: [valianx/EasyMarks](https://github.com/valianx/EasyMarks). GitHub Actions ejecuta las pruebas y genera el ZIP en cada push/PR. La subida a CurseForge está preparada y espera la configuración del proyecto de autor.

**Clic izquierdo en un símbolo:** apunta al terreno y haz clic para intentar colocar un marcador de mundo y enviar un ping de «Mira aquí» en el mismo lugar. **Cada selección sirve para marcar una sola vez**; después vuelve el cursor normal. Mientras seleccionas, el cursor lleva el símbolo del color, sin una ventana de instrucciones.

**Clic derecho en un símbolo:** intenta marcar y enviar un ping al **objetivo seleccionado**, al soltar, sin elegir terreno ni cambiar de modo. Cancela cualquier selección de terreno pendiente y mantiene la rueda abierta. Sin objetivo no envía señales ni usa el cursor como alternativa. Repetir el símbolo conserva la marca y vuelve a intentar el ping únicamente por ese nuevo clic manual.

**La rueda permanece abierta** al seleccionar, marcar y cancelar. Escape o clic derecho sobre el terreno cancelan la selección sin colocar nada. **Escape no cierra la rueda**; sin selección, queda libre para el juego. Un nuevo clic izquierdo en el icono **EM** del minimapa cierra la rueda y cancela cualquier selección pendiente. La rueda no tiene título ni botón de cierre.

La rueda tiene **fondo circular translúcido y compacto**: los botones están más cerca del centro y hay menos margen exterior, conservando el tamaño de los iconos. Dos líneas discretas debajo de Clear all indican el agarre. **Arrástralo con el botón izquierdo para moverla fuera de combate**; recuerda su posición entre sesiones. Si entras en combate, el arrastre se detiene. Los demás huecos del fondo dejan pasar los clics; solo los botones y el agarre reciben entrada propia.

Para **limpiar**, pasa el cursor sobre un color: aparece una pequeña × en la esquina del icono. **Clic izquierdo o derecho hacen lo mismo:** intentan quitar ese color del suelo **y** el símbolo del objetivo seleccionado, aunque tenga otro color. Sin objetivo, se limpia igualmente ese marcador del suelo; las otras unidades y colores permanecen.

**Clear all**, en el centro, intenta retirar **todos los marcadores del suelo y todos los símbolos de unidades del grupo**, incluso sin objetivo seleccionado. Ambas formas de limpieza cancelan la selección pendiente, sin ping y sin cerrar la rueda. Pasar el cursor o arrastrar no borra nada; se mantienen los permisos nativos del grupo.

Estado: **alpha en desarrollo; pendiente de probar dentro de WoW**. La versión 0.1.11 añade la licencia al paquete; la última copia instalada localmente es 0.1.10-alpha. La copia de Mario está en `C:\Program Files (x86)\World of Warcraft\_retail_\Interface\AddOns\EasyMarks`. Se contrastó la cabecera `120100` con Retail 12.1.0.69814. No se ha publicado en CurseForge.

El trabajo continúa mediante Team Harness `spec`: [propuesta](openspec/changes/manual-ground-marks/proposal.md) aprobada y [tareas](openspec/changes/manual-ground-marks/tasks.md) con la validación manual pendiente. Las pruebas locales no sustituyen la aceptación dentro del cliente.

Documentación del proyecto: [stack y arquitectura](docs/ARCHITECTURE.md), [cómo contribuir](CONTRIBUTING.md), [errores y diagnóstico](docs/DIAGNOSTICO.md) y [convenciones para agentes](AGENTS.md). Consulta también el [código de conducta](CODE_OF_CONDUCT.md) y la [licencia MIT](LICENSE).

## Instalar la versión local

1. Extrae `dist/EasyMarks-0.1.11-alpha.zip` dentro de `World of Warcraft/_retail_/Interface/AddOns/`.
2. Comprueba que queda `Interface/AddOns/EasyMarks/EasyMarks.toc`, sin otra carpeta entre medio.
3. Abre WoW y activa **Easy Marks** en la lista de addons. Si el juego ya estaba abierto y no lo detecta, vuelve a iniciarlo.
4. Dentro del juego, haz **clic izquierdo en el icono EM junto al minimapa** para abrir o cerrar la rueda. Tiene letras centradas sobre fondo oscuro y borde dorado. No necesitas escribir comandos.
5. Para terreno, elige el color con clic izquierdo y confirma en una zona despejada. Para unidades, selecciona un objetivo y haz clic derecho en el símbolo. Las acciones se ejecutan al soltar.

También puedes copiar directamente la carpeta `addon/EasyMarks` y añadir dentro una copia del archivo `LICENSE` de la raíz. Después de editar código, vuelve a copiarla al juego y ejecuta `/reload`.

Puedes asignar una tecla buscando **Easy Marks → Toggle marker wheel** en las opciones de asignación de teclas. Ese atajo y el icono del minimapa están preparados para usarse en combate. Como alternativa opcional, `/emarks` y `/easymarks` abren o cierran la rueda fuera de combate.

El **clic derecho en EM** abre el registro de errores propios. Puedes copiarlo con Ctrl+A y Ctrl+C. Conserva hasta 30 entradas mediante `SavedVariables`; WoW las escribe en disco al recargar la interfaz o cerrar sesión. Los fallos que impiden cargar el Lua requieren revisar el registro nativo: [diagnóstico](docs/DIAGNOSTICO.md).

No hay que instalar dependencias para usar el addon. Tus compañeros reciben marcadores y pings nativos; no necesitan Easy Marks para verlos, siempre que el juego y su configuración permitan mostrarlos.

## Qué probar primero

En un grupo, fuera de combate: selecciona azul, cancela con Escape, vuelve a seleccionarlo y confirma en el terreno. Comprueba con otro jugador que ve tanto el cuadrado azul como el ping. Después repite en combate y revisa [la lista de pruebas](docs/PRUEBAS.md).

Para objetivos: selecciona una unidad que el juego permita marcar, haz clic derecho en la calavera y comprueba que aparece el símbolo y el ping sobre ella. Pulsa una pequeña × y comprueba que limpia el objetivo y ese color del suelo sin ping. Después coloca varios colores y símbolos sobre unidades; quita tu objetivo y pulsa Clear all para comprobar que desaparecen todos y la rueda sigue abierta.

El marcador y el ping son dos acciones independientes: una puede ser rechazada aunque la otra funcione. El addon no confirma un éxito que no puede observar ni repite pings automáticamente. Las restricciones de la instancia, los permisos del grupo y los límites de pings siguen aplicándose. En arenas hay que validar tanto la preparación como el combate y los cambios de ronda en el cliente real.

Mientras el cursor está armado, una capa transparente recibe el clic de terreno; la rueda y el icono del minimapa permanecen por encima para permitir cambiar el color o cerrar. Apunta a terreno visible y cancela antes de usar bolsas, mapa u otros paneles, que pueden interceptar la entrada según su nivel. No es una previsualización de una posición válida; WoW valida el punto al confirmar. Cambiar de ventana no cancela automáticamente: al volver, usa Escape si no quieres marcar.

## Estructura

```text
EasyMarks/
├── addon/EasyMarks/
│   ├── EasyMarks.toc       # Metadatos y orden de carga
│   ├── Errors.lua          # Errores propios, persistencia y visor
│   ├── Domain/Markers.lua  # Colores, validación y acción; sin APIs de WoW
│   ├── UI/Wheel.lua        # Rueda, minimapa, cursor y acciones seguras
│   ├── Core.lua            # Inicio, eventos y comandos opcionales
│   └── Bindings.xml        # Atajo; WoW lo carga por separado del TOC
├── docs/                   # Pruebas y publicación
├── tests/
│   ├── unit/               # Lógica y logger aislados
│   ├── integration/        # Flujo con contrato WoW simulado
│   └── support/            # Un único mock de WoW
├── tools/package.py        # ZIP, sin dependencias externas
├── tools/release.py        # Preparación y subida del ZIP a CurseForge
├── .github/workflows/      # Pruebas, artefactos y publicación
├── branding/               # Logo para la ficha; fuera del addon
└── dist/                   # Paquete instalable
```

La rueda empieza centrada y puede moverse; el icono conserva una posición fija del minimapa. Se guardan la posición de la rueda y el registro de errores; no se necesitan bibliotecas externas ni servidores. Las barras de acción quedan como una función futura separada.

## Desarrollo

Para generar el ZIP desde la raíz del proyecto:

```powershell
python tools/package.py
```

Las pruebas de desarrollo usan Python y `lupa==2.8` con Lua 5.1. Se recomienda un entorno virtual. Ejecutarlas no requiere WoW, pero tampoco reproduce sus restricciones de seguridad ni la validación del servidor:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

Solo unitarias: `.\.venv\Scripts\python.exe -B -m unittest discover -s tests/unit -v`. Preparación y comandos por nivel en [CONTRIBUTING.md](CONTRIBUTING.md).

El clic del jugador activa un botón seguro con dos comandos: marcador `[@cursor]` y ping `[@cursor] 5`. Las transiciones protegidas de selección y cancelación viven en snippets seguros. El Lua visual solamente dibuja la interfaz y cambia el cursor. No se intenta automatizar decisiones ni localizar pilares por coordenadas.

Para objetivos, el clic derecho usa los comandos localizados equivalentes a `/tm [@target,exists] !N` y `/ping [@target,exists] 5`. El símbolo usa su índice de unidad y `!` evita quitarlo al repetir. El parser nativo de ping detiene la acción si no hay objetivo; no se comparan datos secretos de la unidad desde Lua propio. La marca y el ping siguen siendo intentos independientes sujetos a las reglas del cliente.

La limpieza combina el comando nativo de suelo con `/click` a un botón precreado de acción nativa `raidtarget`, sin ejecutar otra macro ni recorrer unidades. Clear all usa el valor localizado de `ALL` para el suelo y `clear-all` para los iconos del grupo. Los permisos y la ejecución real en combate requieren las pruebas de cliente documentadas.

Referencias técnicas: [acciones seguras del cliente](https://github.com/Gethe/wow-ui-source/blob/live/Interface/AddOns/Blizzard_FrameXML/SecureTemplates.lua), [comandos de marcadores](https://github.com/Gethe/wow-ui-source/blob/live/Interface/AddOns/Blizzard_ChatFrameBase/Shared/SlashCommands.lua), [implementación de pings](https://github.com/Gethe/wow-ui-source/blob/live/Interface/AddOns/Blizzard_PingUI/Blizzard_PingManager.lua). Son fuentes del cliente reflejadas en un repositorio comunitario.

## Publicación

La [guía de publicación](docs/PUBLICACION.md) explica cómo crear el proyecto de CurseForge, conectar su ID y token en GitHub, probar el flujo sin subir nada y activar publicaciones desde GitHub Releases. El [logo original](branding/easy-marks-curseforge.png) está preparado. La ficha ya fue creada; faltan conectar su ID y token, confirmar la licencia MIT también en CurseForge y comprobar el addon dentro del juego antes de distribuirlo.

Este proyecto tiene código propio y usa recursos incluidos en WoW. No contiene código copiado de FastMarks. El código y la documentación propios se distribuyen bajo [MIT](LICENSE). Los materiales de terceros conservan sus [avisos y licencias](THIRD_PARTY_NOTICES.md); los recursos del juego pertenecen a sus respectivos titulares.
