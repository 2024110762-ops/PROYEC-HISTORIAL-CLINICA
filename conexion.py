
import mysql.connector
from mysql.connector import Error
import os


def conectar():
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD", ""),
            database="db_historia_clinica",
            port=3306
        )

        if conexion.is_connected():
            print("Conexion a MySQL exitosa")
            return conexion

    except Error as error:
        print("Error al conectar con MySQL:", error)

    return None


if __name__ == "__main__":
    conexion = conectar()

    if conexion:
        conexion.close()
        print("Conexion cerrada correctamente")
