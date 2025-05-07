import mysql.connector
import pandas as pd

# Configuración de la conexión a MySQL
def conectar_mysql():
    try:
        connection = mysql.connector.connect(
            host="Alexiss1.mysql.pythonanywhere-services.com",  # Reemplaza con tu nombre de usuario
            user="Alexiss1",                                    # Reemplaza con tu nombre de usuario
            password="grupoc425",                          # Usa la contraseña que configuraste
            database="Alexiss1$rentacar"                       # Nombre de la base de datos
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error al conectar a MySQL: {err}")
        return None

# Crear las tablas en la base de datos
def crear_tablas(connection):
    try:
        cursor = connection.cursor()

        # Tabla para coches
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS coches (
            id VARCHAR(10) PRIMARY KEY,
            marca VARCHAR(50) NOT NULL,
            modelo VARCHAR(50) NOT NULL,
            matricula VARCHAR(20) NOT NULL UNIQUE,
            categoria_tipo VARCHAR(50) NOT NULL,
            categoria_precio VARCHAR(50) NOT NULL,
            año INT NOT NULL,
            precio_diario DECIMAL(10, 2) NOT NULL,
            kilometraje INT NOT NULL,
            color VARCHAR(20) NOT NULL,
            combustible VARCHAR(20) NOT NULL,
            cv INT NOT NULL,
            plazas INT NOT NULL,
            disponible BOOLEAN NOT NULL
        );
        """)

        # Tabla para usuarios
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario VARCHAR(10) PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            tipo VARCHAR(20) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            contraseña VARCHAR(255) NOT NULL
        );
        """)

        # Tabla para alquileres
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS alquileres (
            id_alquiler VARCHAR(10) PRIMARY KEY,
            id_coche VARCHAR(10) NOT NULL,
            id_usuario VARCHAR(10) NOT NULL,
            fecha_inicio DATE NOT NULL,
            fecha_fin DATE NOT NULL,
            coste_total DECIMAL(10, 2) NOT NULL,
            activo BOOLEAN NOT NULL,
            FOREIGN KEY (id_coche) REFERENCES coches(id),
            FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
        );
        """)

        print("Tablas creadas exitosamente.")
    except mysql.connector.Error as err:
        print(f"Error al crear las tablas: {err}")

# Cargar datos desde un archivo CSV a una tabla
def cargar_datos_csv(connection, csv_file, table_name):
    try:
        # Leer el archivo CSV
        df = pd.read_csv(csv_file)
        
        # Convertir booleanos a 1/0 para MySQL
        if table_name == "coches":
            df['disponible'] = df['disponible'].astype(int)
        elif table_name == "alquileres":
            df['activo'] = df['activo'].astype(int)

        # Insertar datos en la tabla
        cursor = connection.cursor()
        for _, row in df.iterrows():
            values = tuple(row)
            placeholders = ", ".join(["%s"] * len(row))
            query = f"INSERT INTO {table_name} VALUES ({placeholders})"
            cursor.execute(query, values)

        connection.commit()
        print(f"Datos cargados exitosamente desde '{csv_file}' a la tabla '{table_name}'.")
    except Exception as e:
        print(f"Error al cargar datos desde el CSV: {e}")

# Función principal
def main():
    # Conexión a MySQL
    connection = conectar_mysql()
    if connection is None:
        print("No se pudo conectar a MySQL. Saliendo...")
        return

    # Crear las tablas
    crear_tablas(connection)

    # Rutas a los archivos CSV
    csv_coches = "/home/Alexiss1/prog2_25_C4/data/coches.csv"
    csv_usuarios = "/home/Alexiss1/prog2_25_C4/data/clientes.csv"
    csv_alquileres = "/home/Alexiss1/prog2_25_C4/data/alquileres.csv"

    # Cargar datos desde los CSV
    cargar_datos_csv(connection, csv_coches, "coches")
    cargar_datos_csv(connection, csv_usuarios, "usuarios")
    cargar_datos_csv(connection, csv_alquileres, "alquileres")

    # Cerrar la conexión
    connection.close()

if __name__ == "__main__":
    main()