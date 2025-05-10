
'''Clase Usuario para representar a los clientes y sus datos'''
from mysql.connector import Error
from source.utils import hash_contraseña, es_email_valido
class Usuario:

    def __init__(self, id_usuario, nombre, email, tipo, contraseña_hasheada):
        if not nombre:
            raise ValueError("El nombre no puede estar vacío")

        if not es_email_valido(email):
            raise ValueError(f"Email '{email}' no es válido")

        self.id_usuario = id_usuario
        self.nombre = nombre
        self.email = email
        self.tipo = tipo
        self.contraseña = contraseña_hasheada
        self.historial_alquileres = []


    def obtener_usuarios(connection) -> list[dict]:
        """
        Obtiene todos los usuarios registrados desde la base de datos.

        Parameters
        ----------
        connection : mysql.connector.connection.MySQLConnection
            Conexión activa a la base de datos.

        Returns
        -------
        list[dict]
            Una lista de diccionarios con los campos id_usuario, nombre, tipo, email.

        Raises
        ------
        ValueError
            Si no hay usuarios registrados o si ocurre un error en la consulta.
        Exception
            Si hay un fallo en la conexión.
        """
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT id_usuario, nombre, tipo, email FROM usuarios"
            cursor.execute(query)

            resultados = cursor.fetchall()
            if not resultados:
                raise ValueError("No hay usuarios registrados.")

            return resultados

        except Error as e:
            raise ValueError(f"Error al obtener la lista de usuarios: {e}")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()


    def registrar_usuario(connection, nombre: str, tipo: str, email: str, contraseña: str) -> int:
        """
        Registra un nuevo usuario en la base de datos MySQL.

        Parameters
        ----------
        connection : mysql.connection.MySQLConnection
            Conexión activa a la base de datos.
        nombre : str
            Nombre completo del usuario.
        tipo : str
            Tipo de usuario (debe ser 'Cliente' o 'Admin').
        email : str
            Correo electrónico del usuario (único y válido).
        contraseña : str
            Contraseña del usuario (se guardará como hash SHA-256).

        Returns
        -------
        int
            El ID del usuario recién registrado.

        Raises
        ------
        ValueError
            Si hay errores en los datos proporcionados o si el correo ya existe.
        Exception
            Si ocurre un error al insertar en la base de datos.
        """
        # Validaciones iniciales
        if not nombre or not tipo or not email or not contraseña:
            raise ValueError("Debes rellenar todos los campos.")

        if tipo not in ['admin','cliente']:
            raise ValueError(f"El tipo '{tipo}' no es válido. Opciones: admin, cliente")

        if not es_email_valido(email):
            raise ValueError(f"Correo electrónico inválido: {email}")

        try:
            cursor = connection.cursor()

            # Verificar si el correo ya está registrado
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE email = %s", (email,))
            if cursor.fetchone()[0] > 0:
                raise ValueError(f"El correo {email} ya está registrado.")

            # Hashear la contraseña
            contraseña_hasheada = hash_contraseña(contraseña)

            # Insertar el nuevo usuario
            query = """
            INSERT INTO usuarios (nombre, tipo, email, contraseña)
            VALUES (%s, %s, %s, %s)
            """
            valores = (nombre, tipo, email, contraseña_hasheada)

            cursor.execute(query, valores)
            connection.commit()

            # Devolver el ID generado por MySQL
            return cursor.lastrowid

        except Error as e:
            connection.rollback()
            raise ValueError(f"Error al registrar usuario: {e}")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
        
        
    @staticmethod
    def actualizar_contraseña(connection, email: str, nueva_contraseña: str) -> bool:
        """
        Actualiza la contraseña de un usuario en la base de datos usando su correo electrónico.

        Parameters
        ----------
        connection : mysql.connector.connection.MySQLConnection
            Conexión activa a la base de datos.
        email : str
            Correo electrónico del usuario que se desea actualizar.
        nueva_contraseña : str
            Nueva contraseña del usuario (se guardará como hash).

        Returns
        -------
        bool
            True si la contraseña se actualizó correctamente.

        Raises
        ------
        ValueError
            Si el correo no existe o si ocurre un error al actualizar la contraseña.
        """
        if not email:
            raise ValueError("El correo electrónico es obligatorio.")
        
        if not nueva_contraseña:
            raise ValueError("La nueva contraseña no puede estar vacía.")

        try:
            cursor = connection.cursor()

            # Verificar si el correo existe
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE email = %s", (email,))
            if cursor.fetchone()[0] == 0:
                raise ValueError(f"No hay ningún usuario con el correo {email}")

            # Generar hash de la nueva contraseña
            contraseña_hasheada = hash_contraseña(nueva_contraseña)

            # Actualizar en la base de datos
            query = "UPDATE usuarios SET contraseña = %s WHERE email = %s"
            cursor.execute(query, (contraseña_hasheada, email))
            connection.commit()

            if cursor.rowcount > 0:
                return True
            else:
                raise ValueError(f"No se pudo actualizar la contraseña del correo {email}")

        except Error as e:
            connection.rollback()
            raise ValueError(f"Error al actualizar la contraseña: {e}")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
    
    
    def dar_baja_usuario(connection, email: str) -> bool:
        """
        Elimina un usuario del sistema basándose en su correo electrónico.

        Este método verifica si el correo existe en la base de datos y elimina 
        al usuario correspondiente.

        Parameters
        ----------
        connection : mysql.connector.connection.MySQLConnection
            Conexión activa a la base de datos.
        email : str
            El correo electrónico del usuario que se desea eliminar.

        Returns
        -------
        bool
            True si el usuario se eliminó correctamente.

        Raises
        ------
        ValueError
            Si no se pueden cargar los usuarios o si el correo electrónico no está registrado.
        Exception
            Si ocurre un error al guardar los cambios en la base de datos.

        Notes
        -----
        - Antes de eliminar el usuario, se verifica que el correo exista en la base de datos.
        - El método utiliza MySQL como fuente de datos, por lo que los cambios son persistentes.
        """
        if not es_email_valido(email):
            raise ValueError("Correo electrónico inválido.")

        try:
            cursor = connection.cursor()

            # Verificar si el correo existe
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE email = %s", (email,))
            if cursor.fetchone()[0] == 0:
                raise ValueError(f"El correo {email} no está registrado.")

            # Eliminar al usuario por su correo electrónico
            query = "DELETE FROM usuarios WHERE email = %s"
            cursor.execute(query, (email,))
            connection.commit()

            if cursor.rowcount > 0:
                return True
            else:
                raise ValueError(f"No se pudo eliminar el usuario con email {email}")

        except Error as e:
            connection.rollback()
            raise ValueError(f"Error al eliminar el usuario: {e}")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
        
        
    def iniciar_sesion(connection, email: str, contraseña: str) -> dict:
        """
        Verifica si un usuario con el correo electrónico y contraseña dados existe en la base de datos.

        Parameters
        ----------
        connection : mysql.connector.connection.MySQLConnection
            Conexión activa a la base de datos.
        email : str
            Correo electrónico del usuario.
        contraseña : str
            Contraseña proporcionada por el usuario (sin hashear).

        Returns
        -------
        bool
            True si las credenciales son correctas.

        Raises
        ------
        ValueError
            Si el correo no existe o la contraseña es incorrecta.
        Exception
            Si ocurre un error de conexión o consulta.
        """
        if not es_email_valido(email):
            raise ValueError("Correo electrónico inválido.")

        try:
            cursor = connection.cursor(dictionary=True)

            # Buscar al usuario por su email
            query = "SELECT * FROM usuarios WHERE email = %s"
            cursor.execute(query, (email,))
            usuario = cursor.fetchone()

            if not usuario:
                raise ValueError(f"No se encontró ningún usuario con el correo: {email}")

            # Hashear la contraseña ingresada y comparar con la almacenada
            contraseña_hasheada_ingresada = hash_contraseña(contraseña)
            contraseña_almacenada = usuario['contraseña']

            if contraseña_hasheada_ingresada != contraseña_almacenada:
                raise ValueError("Contraseña incorrecta.")

            return {
                "autenticado": True,
                "rol": usuario['tipo'],
                "nombre": usuario['nombre'],
            }

        except Error as e:
            raise ValueError(f"Error al iniciar sesión: {e}")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
    
    
    @staticmethod
    def obtener_historial_alquileres(connection, email: str) -> list[dict]:
        """
        Obtiene el historial de alquileres de un usuario desde la base de datos.

        Parameters
        ----------
        connection : mysql.connector.connection.MySQLConnection
            Conexión activa a la base de datos.
        email : str
            Correo electrónico del usuario cuyo historial se desea obtener.

        Returns
        -------
        list[dict]
            Una lista de diccionarios con los detalles de cada alquiler.

        Raises
        ------
        ValueError
            Si no hay alquileres para el usuario o si ocurre un error en la consulta.
        Exception
            Si hay un fallo en la conexión o en la consulta SQL.
        """
        try:
            cursor = connection.cursor(dictionary=True)

            # Verificar si el usuario existe
            cursor.execute("SELECT id_usuario FROM usuarios WHERE email = %s", (email,))
            resultado = cursor.fetchone()
            if not resultado:
                raise ValueError(f"El correo {email} no está registrado.")

            id_usuario = resultado['id_usuario']

            # Consultar los alquileres del usuario
            query = "SELECT * FROM alquileres WHERE id_usuario = %s ORDER BY fecha_inicio DESC"
            cursor.execute(query, (id_usuario,))
            resultados = cursor.fetchall()

            if not resultados:
                raise ValueError(f"No hay alquileres registrados para el usuario {email}")

            return resultados

        except Error as e:
            raise ValueError(f"Error al obtener el historial de alquileres: {e}")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()