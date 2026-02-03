import sqlite3

conexion = sqlite3.connect('backend/sql_app.db')
cursor = conexion.cursor()

try:

    cursor.execute("SELECT * FROM users")

    nombres_columnas = [descripcion[0] for descripcion in cursor.description]
    print(f"COLUMNAS: {nombres_columnas}")
    print("-" * 30)

    usuarios = cursor.fetchall()
    for usuario in usuarios:
        print(usuario)

except sqlite3.OperationalError:
    print("Error: No se encontró la tabla 'users'.")
    print("\nLas tablas que existen en tu base de datos son:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print(cursor.fetchall())

conexion.close()