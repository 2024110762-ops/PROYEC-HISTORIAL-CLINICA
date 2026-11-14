# Pruebas Manuales - Módulo 2: Programación de Consultas

| N° | Caso de prueba | Datos de entrada | Resultado esperado | Resultado obtenido | ¿Pasó? |
|---|---|---|---|---|---|
| 1 | Registro normal de consulta médica | Paciente: DNI 71234567, Especialidad: Medicina General, Fecha: 20/11/2026, Hora: 10:00 | El sistema registra la consulta y muestra confirmación. | Consulta registrada correctamente en la lista. | Sí |
| 2 | Consulta y modificación de cita | Buscar consulta por DNI 71234567 y reprogramar hora a 11:30 | Actualiza el horario de la consulta sin errores. | Horario actualizado correctamente. | Sí |
| 3 | Registro con campo obligatorio vacío (inválido) | Paciente: "", Especialidad: Pediatría, Fecha: 20/11/2026 | Muestra mensaje "Debe seleccionar o ingresar un paciente" y no guarda. | Mostró alerta de campo obligatorio. | Sí |
| 4 | Formato de fecha u hora incorrecto (inválido) | Paciente: 71234567, Fecha: "32/13/2026" | Rechaza el formato inválido e indica corregir la fecha. | Indicó error de formato de fecha. | Sí |
| 5 | Dato límite en motivo de consulta | Motivo de consulta de 150 caracteres (límite máximo) | Guarda el registro completo sin truncar ni arrojar error. | Guardó el registro sin errores. | Sí |
