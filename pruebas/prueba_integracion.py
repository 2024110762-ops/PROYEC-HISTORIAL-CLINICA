
from conexion import conectar

conexion = conectar()

if conexion:
    cursor = conexion.cursor()

    try:
        print("\n===== PRUEBA DE INTEGRACION =====")

        # 1. Verificar las tablas
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = 'db_historia_clinica'
        """)

        total_tablas = cursor.fetchone()[0]
        print("Tablas encontradas:", total_tablas)

        if total_tablas == 11:
            print("OK: Las 11 tablas existen.")
        else:
            print("REVISAR: Se esperaban 11 tablas.")

        # 2. Verificar las relaciones
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.key_column_usage
            WHERE table_schema = 'db_historia_clinica'
              AND referenced_table_name IS NOT NULL
        """)

        total_relaciones = cursor.fetchone()[0]
        print("Relaciones encontradas:", total_relaciones)

        if total_relaciones > 0:
            print("OK: MySQL reconoce las relaciones.")
        else:
            print("REVISAR: No se encontraron relaciones.")

        # 3. Verificar el paciente de prueba
        cursor.execute("""
            SELECT id_paciente, dni, nombres, apellidos
            FROM pacientes
            WHERE dni = %s
        """, ("99999999",))

        paciente = cursor.fetchone()

        if paciente:
            print("OK: Paciente de prueba encontrado.")
            print("ID:", paciente[0])
            print("DNI:", paciente[1])
            print("Nombre:", paciente[2], paciente[3])
        else:
            print("REVISAR: No se encontró el paciente de prueba.")

        print("\n===== FIN DE LA PRUEBA =====")

    except Exception as error:
        print("Error durante la prueba:", error)

    finally:
        cursor.close()
        conexion.close()
        print("Conexión cerrada.")
else:
    print("No se pudo conectar con MySQL.")
