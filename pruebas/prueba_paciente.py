
from conexion import conectar

conexion = conectar()

if conexion:
    cursor = conexion.cursor()

    try:
        dni_prueba = "99999999"

        # Comprobar si el paciente de prueba ya existe
        cursor.execute(
            "SELECT id_paciente, nombres FROM pacientes WHERE dni = %s",
            (dni_prueba,)
        )

        paciente = cursor.fetchone()

        if paciente:
            print("El paciente de prueba ya existe.")
            print("ID:", paciente[0])
            print("Nombre:", paciente[1])

        else:
            sql = """
                INSERT INTO pacientes
                (dni, nombres, apellidos, fecha_nacimiento,
                 sexo, telefono, direccion, correo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """

            datos = (
                dni_prueba,
                "PACIENTE DE PRUEBA",
                "NO REAL",
                "2000-01-01",
                "Masculino",
                "999999999",
                "DATO FICTICIO",
                "prueba@ejemplo.com"
            )

            cursor.execute(sql, datos)
            conexion.commit()

            print("Paciente registrado correctamente.")
            print("ID del paciente:", cursor.lastrowid)

    except Exception as error:
        conexion.rollback()
        print("Error al registrar paciente:", error)

    finally:
        cursor.close()
        conexion.close()
        print("Conexion cerrada.")
