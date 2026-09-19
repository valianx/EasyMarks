## 1. Revisar el prototipo

- [x] 1.1 Contrastar rueda, colores, cursor y confirmación con los escenarios de `specs/ground-marking/spec.md`; corregir las diferencias sin ampliar el alcance.
- [x] 1.2 Revisar cancelación, liberación de entrada y transiciones durante combate; conservar las restricciones nativas y la ejecución única al soltar.
- [x] 1.3 Corregir el error de carga observado, añadir el acceso por icono del minimapa solicitado por Mario y comprobar las regresiones antes de actualizar la copia instalada.
- [x] 1.4 Añadir registro acotado de errores propios, persistencia SavedVariables y consulta/copia desde el icono, con pruebas de captura y límites.
- [x] 1.5 Corregir el marcado de un solo uso y Escape según el contrato nativo; mantener la rueda abierta y accesible hasta cerrarla, retirar la ventana explicativa y comprobar/instalar la actualización local.
- [x] 1.6 Separar lógica pura, interfaz y arranque con módulos pequeños; añadir pruebas unitarias independientes de WoW, conservar regresiones de integración y documentar/entregar la estructura sin frameworks adicionales.
- [x] 1.7 Hacer la rueda circular y semitransparente, elevar el título y permitir arrastre con posición guardada fuera de combate; comprobar interrupción del arrastre, regresiones y entrega local.
- [x] 1.8 Añadir fondo sutil a la cabecera, traducir los textos propios al inglés y limitar Escape a cancelar la selección sin cerrar la rueda; verificar y actualizar la copia local.
- [x] 1.9 Añadir limpieza individual mediante un botón visible al pasar sobre cada color; conservar acceso durante combate, cancelar selección pendiente sin ping y verificar/instalar la actualización local.
- [x] 1.10 Retirar el óvalo del título según la nueva captura, conservando una pista discreta de arrastre y el comportamiento de la cabecera.
- [x] 1.11 Añadir marcado con ping del objetivo seleccionado mediante clic derecho, limpieza del objetivo sin ping y ayudas inglesas; conservar terreno por clic izquierdo y validar/entregar localmente.
- [x] 1.12 Retirar título y cierre de la rueda, mover el agarre al centro y sustituir el icono del minimapa por EM centrado; adaptar regresiones/documentación y entregar localmente.
- [x] 1.13 Unificar limpieza de suelo y objetivo en un clic, añadir Clear all central para todo el suelo y símbolos de unidades del grupo, conservar el arrastre y comprobar/entregar la actualización local.

## 2. Verificar

- [x] 2.1 Revisar y ejecutar las pruebas Lua de interacción, reutilizando evidencia válida y distinguiendo explícitamente mocks de validación en WoW.
- [x] 2.2 Añadir la comprobación de límites de OpenSpec en `tests/test_openspec_scope.py`, ejecutar la validación estricta y registrar los resultados seleccionados en el plan.

## 3. Preparar la entrega local

- [x] 3.1 Verificar que README, stack/arquitectura, CONTRIBUTING y AGENTS describen el resultado final y que la guía de CurseForge deja la publicación para después.
- [x] 3.2 Contrastar TOC con la versión instalada de Retail y generar un ZIP con solo los archivos de ejecución y la estructura de carpeta correcta.

## 4. Instalar y validar en cliente

- [x] 4.1 Instalar únicamente EasyMarks en la carpeta Retail indicada por Mario, conservando cualquier copia previa y sin modificar otros addons.
- [ ] 4.2 Completar con Mario las pruebas manuales de carga, rueda, puntero, confirmación, cancelación, combate, recepción por otro jugador y restricciones de arenas/míticas+; registrar cualquier escenario no ejecutado como pendiente.
- [ ] 4.3 Actualizar documentación y plan con los resultados reales, entregar localmente y evaluar el archivo del cambio solo cuando la evidencia permita cerrar los criterios.
