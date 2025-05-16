
# --- Imports ---
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from mysql.connector.connection import MySQLConnection
from mysql.connector import Error
from source.utils import hash_contraseña, es_email_valido
# --- Clase Usuario ---
class Usuario:
    """
    Representa un usuario del sistema de alquiler de coches.

    Esta clase encapsula la información y las operaciones relacionadas con
    los usuarios, como clientes o administradores.

    Attributes
    ----------
    id_usuario : str  # O int, dependiendo de tu esquema de BD
        Identificador único del usuario.
    nombre : str
        Nombre completo del usuario.
    email : str
        Correo electrónico del usuario, utilizado para inicio de sesión y
        como identificador único en muchos contextos.
    tipo : str
        Rol del usuario en el sistema (e.g., "cliente", "admin").
    contraseña : str
        Contraseña hasheada del usuario. No se almacena la contraseña en texto plano.
    historial_alquileres : List[Dict[str, Any]]
        Lista que puede contener el historial de alquileres del usuario.
        Nota: En la implementación actual, este atributo se inicializa vacío y
        el historial se obtiene a través de un método específico.
    """
    def __init__(self, id_usuario: str, nombre: str, email: str, tipo: str,             contraseña_hasheada: str):
        """
        Inicializa una nueva instancia de Usuario.

        Parameters
        ----------
        id_usuario : str
            Identificador único para el usuario.
        nombre : str
            Nombre del usuario. No puede estar vacío.
        email : str
            Correo electrónico del usuario. Debe ser un formato válido.
        tipo : str
            Tipo de usuario (e.g., "cliente", "admin").
        contraseña_hasheada : str
            La contraseña del usuario, ya hasheada.

        Raises
        ------
        ValueError
            Si el nombre está vacío o el email no es válido.
        """
        if not nombre or not nombre.strip():
            raise ValueError("El nombre del usuario no puede estar vacío.")
        if not es_email_valido(email): # Asume que es_email_valido está disponible
            raise ValueError(f"El formato del correo electrónico '{email}' no es válido.")
        if not tipo or not tipo.strip():
            raise ValueError("El tipo de usuario no puede estar vacío.")

        self.id_usuario: str = id_usuario
        self.nombre: str = nombre
        self.email: str = email
        self.tipo: str = tipo
        self.contraseña: str = contraseña_hasheada # Contraseña ya hasheada


    @staticmethod
    def obtener_usuarios(connection: 'MySQLConnection') -> List[Dict[str, Any]]:
        """
        Obtiene todos los usuarios registrados desde la base de datos.

        Recupera una lista de todos los usuarios, incluyendo su ID, nombre,
        tipo y correo electrónico. No se recupera la contraseña hasheada por seguridad.

        Parameters
        ----------
        connection : mysql.connector.connection.MySQLConnection
            Una conexión activa a la base de datos MySQL.

        Returns
        -------
        List[Dict[str, Any]]
            Una lista de diccionarios, donde cada diccionario representa un usuario.
            Contiene los campos 'id_usuario', 'nombre', 'tipo', 'email'.
            Retorna una lista vacía si no hay usuarios registrados.

        Raises
        ------
        mysql.connector.Error
            Si ocurre un error durante la interacción con la base de datos.
        """
        try:
            with connection.cursor(dictionary=True) as cursor:
                query = """SELECT id_usuario, nombre, tipo, email 
                        FROM usuarios 
                        ORDER BY nombre ASC"""
                cursor.execute(query)
                usuarios: List[Dict[str, Any]] = cursor.fetchall()
                return usuarios
        except Error as e:
            raise e

                

    @staticmethod
    def obtener_usuario_por_email(
        connection: 'MySQLConnection',
        email: str
        ) -> Optional[Dict[str, Any]]:
        """
        Obtiene los detalles de un usuario por su correo electrónico.

        Busca un usuario en la tabla 'usuarios' que coincida con el email proporcionado.
        No se recupera la contraseña hasheada.

        Parameters
        ----------
        connection : mysql.connector.connection.MySQLConnection
            Una conexión activa a la base de datos MySQL.
        email : str
            El correo electrónico del usuario a buscar.

        Returns
        -------
        Optional[Dict[str, Any]]
            Un diccionario con los datos del usuario ('id_usuario', 'nombre', 'tipo', 'email')
            si se encuentra. Retorna `None` si no se encuentra ningún usuario con ese correo.

        Raises
        ------
        mysql.connector.Error
            Si ocurre un error durante la interacción con la base de datos.
        """
        try:
            with connection.cursor(dictionary=True) as cursor:
                query ="""
                    SELECT id_usuario, nombre, tipo, email 
                    FROM usuarios
                    WHERE email = %s
                """
                cursor.execute(query, (email,))
                usuario: Optional[Dict[str, Any]] = cursor.fetchone()
                return usuario

        except Error as e:
            raise e


    @staticmethod
    def registrar_usuario(
        connection: 'MySQLConnection',
        nombre: str,
        tipo: str,
        email: str,
        contraseña: str 
        ) -> int:
        """
        Registra un nuevo usuario en la base de datos.

        Valida los datos de entrada, verifica que el email no esté ya registrado,
        hashea la contraseña y luego inserta el nuevo usuario.

        Parameters
        ----------
        connection : mysql.connector.connection.MySQLConnection
            Una conexión activa a la base de datos MySQL.
        nombre : str
            Nombre completo del usuario.
        tipo : str
            Tipo de usuario (e.g., "cliente", "admin"). Debe ser uno de los valores permitidos.
        email : str
            Correo electrónico del usuario. Debe ser único y tener un formato válido.
        contraseña : str
            Contraseña del usuario en texto plano. Será hasheada antes de almacenarse.

        Returns
        -------
        int # o str
            El ID del usuario recién registrado, generado por la base de datos.

        Raises
        ------
        ValueError
            - Si alguno de los campos obligatorios está vacío.
            - Si el `tipo` de usuario no es válido.
            - Si el `email` no tiene un formato válido.
            - Si el `email` ya está registrado.
        mysql.connector.Error
            Si ocurre un error específico de la base de datos durante la inserción
            (e.g., problemas de conexión, violación de otras constraints).
        Exception
            Si `lastrowid` no devuelve un ID válido tras la inserción.
        """
        # Validaciones iniciales
        if not nombre or not tipo or not email or not contraseña:
            raise ValueError("Debes rellenar todos los campos.")

        if tipo not in ['admin','cliente']:
            raise ValueError(f"El tipo '{tipo}' no es válido. Opciones: admin, cliente")

        if not es_email_valido(email):
            raise ValueError(f"Correo electrónico inválido: {email}")

        try:
            with connection.cursor() as cursor:
                # Verificar si el correo ya está registrado
                query_check_email = "SELECT 1 FROM usuarios WHERE email = %s"
                cursor.execute(query_check_email, (email,))
                if cursor.fetchone() is not None:
                    raise ValueError(f"El correo electrónico '{email}' ya está registrado.")
                # Hashear la contraseña
                contraseña_hasheada = hash_contraseña(contraseña) 
                
                # Insertar el nuevo usuario
                query_insert = """
                INSERT INTO usuarios (nombre, tipo, email, contraseña)
                VALUES (%s, %s, %s, %s)
                """
                valores = (nombre, tipo, email, contraseña_hasheada)
                cursor.execute(query_insert, valores)
                connection.commit()
                
                # Devolver el ID generado por MySQL
                return cursor.lastrowid

        except Error as e:
            if connection.is_connected():
                connection.rollback()
            raise e
        
        
    @staticmethod
    def actualizar_contraseña(
        connection: 'MySQLConnection',
        email: str,
        nueva_contraseña: str # Contraseña en texto plano
        ) -> bool:
        """
        Actualiza la contraseña de un usuario existente.

        Verifica que el usuario exista, hashea la nueva contraseña y la actualiza
        en la base de datos.

        Parameters
        ----------
        connection : mysql.connector.connection.MySQLConnection
            Una conexión activa a la base de datos MySQL.
        email : str
            Correo electrónico del usuario cuya contraseña se va a actualizar.
        nueva_contraseña : str
            La nueva contraseña en texto plano. Será hasheada.

        Returns
        -------
        bool
            `True` si la contraseña se actualizó correctamente (1 fila afectada).

        Raises
        ------
        ValueError
            - Si el `email` es inválido o no está registrado.
            - Si la `nueva_contraseña` está vacía.
            - Si la actualización no afecta a ninguna fila (inesperado si el email existe).
        mysql.connector.Error
            Si ocurre un error específico de la base de datos.
        """
        if not email:
            raise ValueError("El correo electrónico es obligatorio.")
        
        if not nueva_contraseña:
            raise ValueError("La nueva contraseña no puede estar vacía.")

        try:
            with connection.cursor() as cursor:
                # Verificar si el usuario (email) existe
                query_check_email = "SELECT 1 FROM usuarios WHERE email = %s"
                cursor.execute(query_check_email, (email,))
                if cursor.fetchone() is None:
                    raise ValueError(f"No existe ningún usuario con el correo electrónico '{email}'.")

                # Hashear la nueva contraseña
                contraseña_hasheada = hash_contraseña(nueva_contraseña)

                # Actualizar la contraseña
                query_update = "UPDATE usuarios SET contraseña = %s WHERE email = %s"
                cursor.execute(query_update, (contraseña_hasheada, email))

                if cursor.rowcount > 0:
                    connection.commit()
                    return True
                else:
                    # si la nueva contraseña hasheada es igual a la antigua.
                    connection.rollback() # Revertir si no hubo cambios efectivos
                    raise ValueError(
                        f"No se pudo actualizar la contraseña para el usuario '{email}'. "
                        "Es posible que la nueva contraseña sea igual a la anterior."
                    )
        except Error as e:
            if connection.is_connected():
                connection.rollback()
            raise e
    
    
    @staticmethod 
    def dar_baja_usuario(connection: 'MySQLConnection', email: str) -> bool:
        """
        Elimina un usuario del sistema basándose en su correo electrónico.

        Parameters
        ----------
        connection : mysql.connector.connection.MySQLConnection
            Una conexión activa a la base de datos MySQL.
        email : str
            El correo electrónico del usuario que se desea eliminar.

        Returns
        -------
        bool
            `True` si el usuario se eliminó correctamente (1 fila afectada).

        Raises
        ------
        ValueError
            - Si el `email` es inválido.
            - Si el usuario con el `email` proporcionado no existe y por tanto no se puede eliminar.
        mysql.connector.Error
            Si ocurre un error específico de la base de datos (e.g., claves foráneas).
        """
        if not es_email_valido(email):
            raise ValueError("Correo electrónico inválido.")

        try:
            with connection.cursor() as cursor:
                # Eliminar al usuario por su correo electrónico
                query = "DELETE FROM usuarios WHERE email = %s"
                cursor.execute(query, (email,))

            if cursor.rowcount > 0:
                connection.commit()
                return True
            else:
                connection.rollback()
                raise ValueError(f"No se encontró ningún usuario con el correo '{email}'para eliminar.")

        except Error as e:
            if connection.is_connected():
                connection.rollback()
            raise e

        
        
    @staticmethod 
    def iniciar_sesion(
        connection: 'MySQLConnection',
        email: str,
        contraseña: str 
        ) -> Dict[str, Any]:
        """
        Autentica a un usuario comparando el hash de la contraseña proporcionada
        con el hash almacenado en la base de datos.

        Parameters
        ----------
        connection : mysql.connector.connection.MySQLConnection
            Una conexión activa a la base de datos MySQL.
        email : str
            Correo electrónico del usuario que intenta iniciar sesión.
        contraseña : str
            Contraseña proporcionada por el usuario, en texto plano.

        Returns
        -------
        Dict[str, Any]
            Un diccionario con los datos del usuario autenticado:
            `{'autenticado': True, 'id_usuario': ..., 'nombre': ..., 'rol': ...}`.

        Raises
        ------
        ValueError
            - Si el `email` es inválido.
            - Si no se encuentra un usuario con el `email` proporcionado.
            - Si la `contraseña` es incorrecta.
        mysql.connector.Error
            Si ocurre un error durante la interacción con la base de datos.
        """
        if not es_email_valido(email):
            raise ValueError("Correo electrónico inválido.")

        try:
            with connection.cursor(dictionary=True) as cursor:

                query = """
                SELECT id_usuario, nombre, tipo, contraseña FROM usuarios WHERE email = %s
                """
                cursor.execute(query, (email,))
                usuario_db: Optional[Dict[str, Any]] = cursor.fetchone()

                if not usuario_db:
                    raise ValueError(f"No se encontró ningún usuario con el correo: {email}")

                # Hashear la contraseña ingresada y comparar con la almacenada
                contraseña_hasheada_ingresada = hash_contraseña(contraseña)
                contraseña_almacenada = usuario_db['contraseña']

                if contraseña_hasheada_ingresada != contraseña_almacenada:
                    raise ValueError("Contraseña incorrecta.")

            return {
                    "autenticado": True,
                    "id_usuario": usuario_db['id_usuario'],
                    "nombre": usuario_db['nombre'],
                    "rol": usuario_db['tipo']
                }
        except Error as e: 
            raise e

    
    @staticmethod 
    def obtener_historial_alquileres(
        connection: 'MySQLConnection',
        email: str
        ) -> List[Dict[str, Any]]:
        """
        Obtiene el historial de alquileres de un usuario específico.

        Primero verifica la existencia del usuario por su email para obtener su ID,
        luego consulta todos los alquileres asociados a ese ID de usuario.

        Parameters
        ----------
        connection : mysql.connector.connection.MySQLConnection
            Una conexión activa a la base de datos MySQL.
        email : str
            Correo electrónico del usuario cuyo historial se desea obtener.

        Returns
        -------
        List[Dict[str, Any]]
            Una lista de diccionarios, donde cada diccionario representa un alquiler
            del usuario. Retorna una lista vacía si el usuario no tiene alquileres
            o si el usuario no existe (después de la verificación).

        Raises
        ------
        mysql.connector.Error
            Si ocurre un error durante la interacción con la base de datos.
        """
        try:
            with connection.cursor(dictionary=True) as cursor:
                # Obtener el id_usuario a partir del email
                query = """SELECT id_usuario FROM usuarios WHERE email = %s"""
                cursor.execute(query, (email,))
                usuario_info = cursor.fetchone()
                
                if not usuario_info:
                    raise ValueError(f"El correo {email} no está registrado.")

                id_usuario = usuario_info['id_usuario']
                print(f"DEBUG: ID del usuario obtenido: {id_usuario}")
                raise ValueError(f"Debug: ID del usuario es {id_usuario}")

                # Consultar los alquileres del usuario
               
                query_alquileres = """SELECT 
                a.id_alquiler,
                a.id_coche,
                c.matricula,
                a.fecha_inicio,
                a.fecha_fin,
                a.coste_total,
                a.activo 
                FROM alquileres a INNER JOIN coches c ON a.id_coche = c.id WHERE a.id_usuario = %s ORDER BY a.fecha_inicio DESC, a.id_alquiler DESC"""
                cursor.execute(query_alquileres, (id_usuario,))
                historial_alquileres: List[Dict[str, Any]] = cursor.fetchall()
                print(f"DEBUG Usuario.obtener_historial_alquileres para id_usuario {id_usuario}: {historial_alquileres}")
                return historial_alquileres
        except Error as e:
            print(f"Error al obtener el historial de alquileres: {e}")
            raise e