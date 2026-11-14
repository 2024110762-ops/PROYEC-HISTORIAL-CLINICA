
from conexion import conectar
from mysql.connector import IntegrityError

conexion = conectar()

if conexion:
    cursor = conexion.cursor()

    try:
        sql = """
            INSERT INTO pacientes
            (dni, nombres, apellidos, fecha_nacimiento,
             sexo, telefono, direccion, correo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        datos = (
            "99999999",
            "PRUEBA DUPLICADA",
            "NO REAL",
            "2000-01-01",
            "Masculino",
            "999999999",
            "DIRECCION DE PRUEBA",
            "duplicado@ejemplo.com"
        )

        cursor.execute(sql, datos)
        conexion.rollback()
        print("ERROR: Se permitió un DNI duplicado.")

    except IntegrityError:
        conexion.rollback()
        print("OK: MySQL rechazó el DNI duplicado.")

    except Exception as error:
        conexion.rollback()
        print("Error en la prueba:", error)

    finally:
        cursor.close()
        conexion.close()
        print("Conexión cerrada.")
