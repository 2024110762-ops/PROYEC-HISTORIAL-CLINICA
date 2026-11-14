# Pruebas Manuales - Módulo 1: Gestión de Pacientes

| N° | Caso de prueba | Datos de entrada | Resultado esperado | Resultado obtenido | ¿Pasó? |
|---|---|---|---|---|---|
| 1 | Registro normal de paciente | DNI: 71234567, Nombres: Ana Torres, Edad: 28, Teléfono: 987654321 | Guarda el paciente en el sistema y lo muestra en el listado. | Paciente registrado y listado correctamente. | Sí |
| 2 | Búsqueda y edición de paciente | Buscar DNI 71234567 y actualizar Teléfono a 912345678 | Modifica el teléfono y guarda el cambio. | Datos actualizados sin errores. | Sí |
| 3 | Registro con DNI vacío (inválido) | DNI: "", Nombres: Carlos Ruiz, Edad: 35 | Muestra mensaje "El campo DNI es obligatorio" y bloquea el registro. | Mostró mensaje de validación correctamente. | Sí |
| 4 | DNI con letras (inválido) | DNI: "7123ABCD", Nombres: Luis Gómez | Rechaza el registro indicando que el DNI solo acepta números. | Validación impidió guardar el registro. | Sí |
| 5 | Dato límite en DNI | DNI con exactamente 8 dígitos numéricos ("76543210") | Acepta el DNI de 8 dígitos y guarda el paciente. | Aceptó el registro sin errores. | Sí |
