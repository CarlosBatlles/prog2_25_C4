
'''Clase Usuario para representar a los clientes y sus datos'''
import hashlib
import re
import pandas as pd
from mysql.connector import Error

class Usuario:
    TIPOS_USUARIOS = ['Cliente', 'Admin']

    def __init__(self, id_usuario, nombre, email, tipo, contraseña_hasheada):
        if not nombre:
            raise ValueError("El nombre no puede estar vacío")

        if not self.es_email_valido(email):
            raise ValueError(f"Email '{email}' no es válido")

        if tipo not in self.TIPOS_USUARIOS:
            raise ValueError(f"El tipo '{tipo}' no es válido. Opciones: {self.TIPOS_USUARIOS}")

        self.id_usuario = id_usuario
        self.nombre = nombre
        self.email = email
        self.tipo = tipo
        self.contraseña = contraseña_hasheada
        self.historial_alquileres = []


    @staticmethod
    def hash_contraseña(contraseña: str) -> str:
        """
        Genera un hash SHA-256 de la contraseña proporcionada.

        Parameters
        ----------
        contraseña : str
            La contraseña que se desea hashear.

        Returns
        -------
        str
            Un hash SHA-256 de la contraseña en formato hexadecimal.

        Notes
        -----
        Este método utiliza la biblioteca hashlib para generar un hash seguro de la contraseña.
        El resultado es una cadena hexadecimal de 64 caracteres.
        """
        return hashlib.sha256(contraseña.encode()).hexdigest()
    
    
    @staticmethod
    def es_email_valido(email: str) -> bool:
        """
        Verifica si un correo electrónico es válido utilizando una expresión regular.

        Parameters
        ----------
        email : str
            El correo electrónico que se desea validar.

        Returns
        -------
        bool
            True si el correo electrónico es válido, False en caso contrario.

        Notes
        -----
        Esta función utiliza una expresión regular para validar el formato del correo electrónico.
        El patrón utilizado sigue las reglas estándar para correos electrónicos válidos.
        """
        patron = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(patron, email) is not None


    @staticmethod
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

        if tipo not in Usuario.TIPOS_USUARIOS:
            raise ValueError(f"El tipo '{tipo}' no es válido. Opciones: {Usuario.TIPOS_USUARIOS}")

        if not Usuario.es_email_valido(email):
            raise ValueError(f"Correo electrónico inválido: {email}")

        try:
            cursor = connection.cursor()

            # Verificar si el correo ya está registrado
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE email = %s", (email,))
            if cursor.fetchone()[0] > 0:
                raise ValueError(f"El correo {email} ya está registrado.")

            # Hashear la contraseña
            contraseña_hasheada = Usuario.hash_contraseña(contraseña)

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
            contraseña_hasheada = Usuario.hash_contraseña(nueva_contraseña)

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
    
    
    @staticmethod
    def dar_baja_usuario(empresa, email: str) -> bool:
        """
        Elimina un usuario del sistema basándose en su correo electrónico.

        Este método verifica si el correo electrónico existe en el sistema y elimina 
        al usuario correspondiente del archivo CSV.

        Parameters
        ----------
        empresa : Empresa
            Instancia de la clase Empresa para cargar/guardar datos.
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
            Si ocurre un error al guardar los cambios en el archivo CSV.

        Notes
        -----
        - Antes de eliminar el usuario, se verifica que el correo electrónico exista en el sistema.
        - El método utiliza el archivo CSV como fuente de datos, por lo que los cambios son persistentes.
        """
        # Cargar los usuarios actuales
        df_usuarios = Usuario.cargar_usuarios(empresa)
        if df_usuarios is None:
            raise ValueError("No se pudieron cargar los usuarios. Revisa el archivo CSV.")

        # Verificar si el email existe en el DataFrame
        if email not in df_usuarios['email'].values:
            raise ValueError("El correo que has introducido no está registrado.")

        # Filtrar el DataFrame para excluir al usuario con el email proporcionado
        df_actualizado = df_usuarios[df_usuarios['email'] != email]

        # Guardar los cambios usando el método auxiliar
        try:
            Usuario.guardar_usuarios(empresa, df_actualizado)
            return True
        except Exception as e:
            raise ValueError(f"Error al guardar los cambios en el archivo CSV: {e}")
        
        
    @staticmethod
    def iniciar_sesion(empresa, email: str, contraseña: str) -> bool:
        """
        Verifica si un usuario con el correo electrónico y contraseña dados existe en la base de datos.

        Parameters
        ----------
        empresa : Empresa
            Instancia de la clase Empresa para cargar los datos.
        email : str
            Correo electrónico del usuario.
        contraseña : str
            Contraseña proporcionada por el usuario.

        Returns
        -------
        bool
            True si las credenciales son válidas.

        Raises
        ------
        ValueError
            Si no se pueden cargar los usuarios o si el correo electrónico no está registrado.
        Exception
            Si ocurre un error inesperado durante el proceso.

        Notes
        -----
        - La contraseña se compara en formato hasheado para mayor seguridad.
        - El método utiliza el archivo CSV como fuente de datos, por lo que los cambios son persistentes.
        """
        # Cargar los usuarios
        df_usuarios = Usuario.cargar_usuarios(empresa)
        if df_usuarios is None or df_usuarios.empty:
            raise ValueError("No se pudieron cargar los usuarios. Revisa el archivo CSV.")

        # Buscar el usuario por correo electrónico
        usuario = df_usuarios[df_usuarios['email'] == email]
        if usuario.empty:
            raise ValueError(f"No se encontró ningún usuario con el correo: {email}.")

        # Obtener la contraseña almacenada y compararla con la contraseña hasheada
        contraseña_almacenada = usuario.iloc[0]['contraseña']
        contraseña_hasheada = Usuario.hash_contraseña(contraseña)

        if contraseña_almacenada != contraseña_hasheada:
            raise ValueError("Contraseña incorrecta.")

        return True
    
    
    @staticmethod
    def obtener_historial_alquileres(empresa, email: str) -> list[dict]:
        """
        Obtiene el historial de alquileres de un usuario específico basándose en su email.

        Parameters
        ----------
        empresa : Empresa
            Instancia de la clase Empresa para cargar los datos.
        email : str
            Correo electrónico del usuario cuyo historial de alquileres se desea obtener.

        Returns
        -------
        list[dict]
            Una lista de diccionarios que contiene los detalles de los alquileres del usuario.

        Raises
        ------
        ValueError
            Si no hay alquileres registrados o si no se encuentran alquileres para el usuario especificado.
        Exception
            Si ocurre un error inesperado durante el proceso.

        Notes
        -----
        - El método utiliza el archivo CSV como fuente de datos, por lo que los cambios son persistentes.
        - Si el usuario no tiene alquileres registrados, se lanza una excepción.
        """
        # Cargar los usuarios y verificar si el email existe
        df_usuarios = Usuario.cargar_usuarios(empresa)
        if df_usuarios is None or df_usuarios.empty:
            raise ValueError("No se pudieron cargar los usuarios.")

        # Verificar si el email existe en el sistema
        if email not in df_usuarios['email'].values:
            raise ValueError(f"El usuario con email {email} no está registrado.")

        # Obtener el ID del usuario a partir del email
        id_usuario = df_usuarios[df_usuarios['email'] == email].iloc[0]['id_usuario']

        # Cargar los alquileres
        df_alquileres = empresa.cargar_alquileres()
        if df_alquileres is None or df_alquileres.empty:
            raise ValueError("No hay alquileres registrados.")

        # Filtrar los alquileres por el ID del usuario
        alquileres_usuario = df_alquileres[df_alquileres['id_usuario'] == id_usuario]

        # Si no hay alquileres, lanzar una excepción
        if alquileres_usuario.empty:
            raise ValueError(f"No se encontraron alquileres para el usuario con email {email}.")

        # Convertir el DataFrame a una lista de diccionarios
        return alquileres_usuario.to_dict(orient='records')