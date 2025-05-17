
# --- Imports ---
from datetime import date
import os
import mysql.connector 
from mysql.connector import Error as MySQLError 
from typing import List, Dict, Any, Optional, Union
from mysql.connector.connection import MySQLConnection

from .models.coche import Coche
from .models.usuario import Usuario
from .models.alquiler import Alquiler


# --- Clase Empresa ---
class Empresa:
    """
    Clase principal para gestionar el sistema de alquiler de coches.

    Actúa como una capa de servicio que coordina las operaciones con la base de datos
    a través de las clases de modelo (Coche, Usuario, Alquiler). Gestiona la
    conexión a la base de datos para cada operación.

    Attributes
    ----------
    nombre : str
        El nombre de la empresa de alquiler de coches.
    db_config : Dict[str, str]
        Diccionario con los parámetros de configuración para la conexión MySQL.
    connection : Optional[MySQLConnection]
        La conexión activa a la base de datos MySQL. Se gestiona internamente.
        (Nota: En la implementación actual, cada método gestiona su propia conexión,
        por lo que este atributo podría no mantenerse abierto constantemente).

    """
    
    # --------------------------------------------------------------------------
    # SECCIÓN 1: INICIALIZACIÓN Y GESTIÓN DE CONEXIÓN A BD
    # --------------------------------------------------------------------------
    
    
    def __init__(self,nombre: str):
        """
        Inicializa una nueva instancia de la clase RentACar.

        Parameters
        ----------
        nombre : str
            El nombre de la empresa de alquiler de coches.
        """
        self.nombre = nombre
        self.connection: Optional['MySQLConnection'] = None 
        
        
    # ---------------------------------------
    # Métodos de Inicialización y Configuración
    # ---------------------------------------
        
    
    def _conectar_mysql(self) -> Optional['MySQLConnection']:
        """
        Establece una nueva conexión con la base de datos MySQL.

        Utiliza los parámetros de configuración almacenados en `self.db_config`.

        Returns
        -------
        Optional[mysql.connector.connection.MySQLConnection]
            Un objeto de conexión MySQL si la conexión es exitosa,
            `None` en caso de error.

        Raises
        ------
        # Este método ahora imprime el error y devuelve None, pero podría propagar MySQLError
        """
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
            raise err
        
    def get_connection(self) -> 'MySQLConnection':
        """
        Proporciona una conexión activa a la base de datos.

        Si la conexión existente (self.connection) está cerrada o no existe,
        intenta establecer una nueva.

        Returns
        -------
        mysql.connector.connection.MySQLConnection
            Una conexión activa a la base de datos MySQL.

        Raises
        ------
        MySQLError
            Si no se puede establecer una conexión a la base de datos.
        """
        if self.connection is None or not self.connection.is_connected():
            self.connection = self._conectar_mysql()
            
        if self.connection is None: 
            raise MySQLError("Fallo al obtener la conexión a la base de datos desde get_connection.")
        
        return self.connection


    # --------------------------------------------------------------------------
    # SECCIÓN 2: OPERACIONES RELACIONADAS CON COCHES
    # --------------------------------------------------------------------------


    def registrar_coche(
        self, marca: str, modelo: str, matricula: str, categoria_tipo: str, 
        categoria_precio: str, año: int, precio_diario: float, kilometraje: float, 
        color: str, combustible: str, cv: int, plazas: int, disponible: bool
    ) -> int:
        """
        Registra un nuevo coche en el sistema.

        Delega la operación al método estático `Coche.registrar_coche` después
        de obtener una conexión a la base de datos.

        Parameters
        ----------
        marca : str
            Marca del coche.
        modelo : str
            Modelo del coche.
        matricula : str
            Matrícula única del coche.
        categoria_tipo : str
            Tipo de categoría del coche (e.g., "SUV", "Sedán").
        categoria_precio : str
            Categoría de precio del coche (e.g., "Lujo", "Premium").
        año : int
            Año de fabricación del coche.
        precio_diario : float
            Precio del alquiler por día.
        kilometraje : float
            Kilometraje actual del coche.
        color : str
            Color del coche.
        combustible : str
            Tipo de combustible del coche.
        cv : int
            Caballos de vapor (potencia) del coche.
        plazas : int
            Número de plazas del coche.
        disponible : bool
            Estado de disponibilidad inicial del coche.

        Returns
        -------
        int
            El ID del coche recién registrado, generado por la base de datos.

        Raises
        ------
        ValueError
            Si las validaciones de datos fallan en `Coche.registrar_coche`.
        MySQLError
            Si ocurre un error de base de datos durante el registro.
        Exception
            Si no se puede obtener el ID del coche tras la inserción.
        """
        connection: Optional['MySQLConnection'] = None

        try:
            connection = self.get_connection()
            id_coche_generado = Coche.registrar_coche(
                connection, marca, modelo, matricula, categoria_tipo, categoria_precio,
                año, precio_diario, kilometraje, color, combustible, cv, plazas, disponible
            )
            return id_coche_generado
        finally:
            if connection and connection.is_connected():
                connection.close()
        

    def obtener_detalle_coche_por_matricula(self, matricula: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene los detalles de un coche específico por su matrícula.

        Delega la operación a `Coche.obtener_por_matricula`.

        Parameters
        ----------
        matricula : str
            Matrícula del coche a buscar.

        Returns
        -------
        Optional[Dict[str, Any]]
            Un diccionario con los datos del coche si se encuentra, `None` en caso contrario.

        Raises
        ------
        ValueError
            Si la matrícula es inválida (según `Coche.obtener_por_matricula`).
        MySQLError
            Si ocurre un error de base de datos.
        """
        connection: Optional['MySQLConnection'] = None

        try:
            connection = self.get_connection()
            return Coche.obtener_por_matricula(connection, matricula)
        finally:
            if connection and connection.is_connected():
                connection.close() # Empresa cierra la conexión que abrió   
    
    
    def actualizar_matricula(self, id_coche: str, nueva_matricula: str) -> bool:
        """
        Actualiza la matrícula de un coche llamando al método estático de la clase Coche.
        
        Valida el formato del ID del coche, lo convierte a numérico y delega
        la operación a `Coche.actualizar_matricula`.

        Parameters
        ----------
        id_coche_str : str
            ID del coche formateado (e.g., "UID001").
        nueva_matricula : str
            La nueva matrícula a asignar.

        Returns
        -------
        bool
            `True` si la actualización fue exitosa, `False` en caso contrario
            (si `Coche.actualizar_matricula` devolviera `False`).

        Raises
        ------
        ValueError
            Si el ID no puede convertirse a entero o si hay errores en la actualización.
        """
        connection = None
        try:
            # Validar y convertir el ID formateado ("UID001") a su parte numérica (1)
            if not isinstance(id_coche, str) or not id_coche.upper().startswith("UID") or not id_coche[3:].isdigit() or int(id_coche[3:]) <= 0:
                raise ValueError("Formato de ID de coche inválido. Debe ser 'UID' seguido de números (e.g., 'UID001').")
            
            id_numero = int(id_coche[3:])

            connection = self.get_connection()
            return Coche.actualizar_matricula(connection, id_numero, nueva_matricula)

        except ValueError as ve:
            # Captura errores de formato de ID o conversiones fallidas
            raise ValueError(f"ID de coche inválido: {ve}")
        finally:
            if connection and connection.is_connected():
                connection.close() # Empresa cierra la conexión que abrió
    
    
    def mostrar_categorias_precio(self) -> List[str]:
        """
        Obtiene una lista de todas las categorías de precio disponibles.

        Delega a `Coche.mostrar_categorias_precio`

        Returns
        -------
        List[str]
            Lista de categorías de precio. Vacía si no hay.

        Raises
        ------
        MySQLError
            Si ocurre un error de base de datos.
        """
        connection: Optional['MySQLConnection'] = None

        try:
            connection = self.get_connection()
            return Coche.mostrar_categorias_precio(connection)
        finally:
            if connection and connection.is_connected():
                connection.close() # Empresa cierra la conexión que abrió
    
    
    def mostrar_categorias_tipo(self) -> List[str]: 
        """
        Obtiene una lista de todas las categorías de tipo disponibles.

        Delega a `Coche.mostrar_categorias_tipo`

        Returns
        -------
        List[str]
            Lista de tipos de categoría. Vacía si no hay.

        Raises
        ------
        MySQLError
            Si ocurre un error de base de datos.
        """
        connection: Optional['MySQLConnection'] = None
        try:
            connection = self.get_connection()
            return Coche.mostrar_categorias_tipo(connection)
        finally:
            if connection and connection.is_connected():
                connection.close() # Empresa cierra la conexión que abrió
    
    
    def buscar_coches_por_filtros(
        self, categoria_precio: str, categoria_tipo: Optional[str] = None, 
        marca: Optional[str] = None, modelo: Optional[str] = None
    ) -> Union[List[str], List[Dict[str, Any]]]:
        """
        Realiza una búsqueda progresiva de coches o sus atributos.

        Dependiendo de los filtros proporcionados, devuelve:
        - Lista de tipos de categoría (si solo se da `categoria_precio`).
        - Lista de marcas (si se da `categoria_precio` y `categoria_tipo`).
        - Lista de modelos (si se da `categoria_precio`, `categoria_tipo` y `marca`).
        - Lista de coches (diccionarios) (si se dan todos los filtros).

        Parameters
        ----------
        categoria_precio : str
            Categoría de precio (obligatoria).
        categoria_tipo : Optional[str], optional
            Tipo de categoría del coche.
        marca : Optional[str], optional
            Marca del coche.
        modelo : Optional[str], optional
            Modelo del coche.

        Returns
        -------
        Union[List[str], List[Dict[str, Any]]]
            Una lista de strings (tipos, marcas o modelos) o una lista de
            diccionarios (coches), según los filtros aplicados.

        Raises
        ------
        ValueError
            Si los parámetros de filtro son inválidos.
        MySQLError
            Si ocurre un error de base de datos.
        """
        connection: Optional['MySQLConnection'] = None
        try:
            connection = self.get_connection()

            # Flujo progresivo
            if not categoria_tipo:
                return Coche.obtener_categorias_tipo(connection, categoria_precio)
            elif not marca:
                return Coche.obtener_marcas(connection, categoria_precio, categoria_tipo)
            elif not modelo:
                return Coche.obtener_modelos(connection, categoria_precio, categoria_tipo, marca)
            else:
                return Coche.filtrar_por_modelo(connection, categoria_precio, categoria_tipo, marca, modelo)
        finally:
            if connection and connection.is_connected():
                connection.close() # Empresa cierra la conexión que abrió


    # --------------------------------------------------------------------------
    # SECCIÓN 3: OPERACIONES RELACIONADAS CON USUARIOS
    # --------------------------------------------------------------------------
    
    
    def registrar_usuario(self, nombre: str, tipo: str, email: str, contraseña: str) ->int:
        """
        Registra un nuevo usuario en el sistema.

        Delega a `Usuario.registrar_usuario`.

        Parameters
        ----------
        nombre : str
            Nombre del usuario.
        tipo : str
            Tipo de usuario (e.g., "cliente", "admin").
        email : str
            Correo electrónico del usuario.
        contraseña : str
            Contraseña en texto plano.

        Returns
        -------
        int
            ID del usuario recién registrado.

        Raises
        ------
        ValueError
            Si las validaciones de datos fallan.
        MySQLError
            Si ocurre un error de base de datos.
        """
        connection: Optional['MySQLConnection'] = None
        try:
            connection = self.get_connection()
            return Usuario.registrar_usuario(connection, nombre, tipo, email, contraseña)
        finally:
            if connection and connection.is_connected():
                connection.close() # Empresa cierra la conexión que abrió
    
    def actualizar_contraseña_usuario(self, email: str, nueva_contraseña: str) -> bool:
        """
        Actualiza la contraseña de un usuario.

        Delega a `Usuario.actualizar_contraseña`.

        Parameters
        ----------
        email : str
            Email del usuario.
        nueva_contraseña : str
            Nueva contraseña en texto plano.

        Returns
        -------
        bool
            `True` si la actualización fue exitosa.

        Raises
        ------
        ValueError
            Si el email es inválido, no existe, o la nueva contraseña está vacía.
        MySQLError
            Si ocurre un error de base de datos.
        """
        connection: Optional['MySQLConnection'] = None
        try:
            connection = self.get_connection()
            return Usuario.actualizar_contraseña(connection, email, nueva_contraseña)
        finally:
            if connection and connection.is_connected():
                connection.close() # Empresa cierra la conexión que abrió
    
    
    def iniciar_sesion(self, email: str, contraseña: str) -> Dict[str, Any]:
        """
        Autentica a un usuario.

        Delega a `Usuario.iniciar_sesion`.

        Parameters
        ----------
        email : str
            Email del usuario.
        contraseña : str
            Contraseña en texto plano.

        Returns
        -------
        Dict[str, Any]
            Diccionario con información del usuario autenticado si es exitoso.

        Raises
        ------
        ValueError
            Si el email es inválido, no existe, o la contraseña es incorrecta.
        MySQLError
            Si ocurre un error de base de datos.
        """
        connection: Optional['MySQLConnection'] = None
        try:
            connection = self.get_connection()
            return Usuario.iniciar_sesion(connection, email, contraseña)
        finally:
            if connection and connection.is_connected():
                connection.close() # Empresa cierra la conexión que abrió
    
    
    def obtener_usuarios(self) -> List[Dict[str, Any]]:
        """
        Obtiene una lista de todos los usuarios registrados.

        Delega a `Usuario.obtener_usuarios`.

        Returns
        -------
        List[Dict[str, Any]]
            Lista de diccionarios, cada uno representando un usuario.

        Raises
        ------
        MySQLError
            Si ocurre un error de base de datos.
        """
        connection: Optional['MySQLConnection'] = None
        try:
            connection = self.get_connection()
            return Usuario.obtener_usuarios(connection)
        finally:
            if connection and connection.is_connected():
                connection.close() # Empresa cierra la conexión que abrió
    

    def obtener_usuario_por_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene los detalles de un usuario por su email.

        Delega a `Usuario.obtener_usuario_por_email`.

        Parameters
        ----------
        email : str
            Email del usuario a buscar.

        Returns
        -------
        Optional[Dict[str, Any]]
            Diccionario con datos del usuario si se encuentra, `None` si no.

        Raises
        ------
        ValueError
            Si el email es inválido.
        MySQLError
            Si ocurre un error de base de datos.
        """
        connection: Optional['MySQLConnection'] = None
        try:
            connection = self.get_connection()
            return Usuario.obtener_usuario_por_email(connection, email)
        finally:
            if connection and connection.is_connected():
                connection.close() # Empresa cierra la conexión que abrió
    
    def obtener_historial_alquileres(self, email: str) -> List[Dict[str, Any]]:
        """
        Obtiene el historial de alquileres de un usuario específico.

        Delega a `Usuario.obtener_historial_alquileres`.

        Parameters
        ----------
        email : str
            Email del usuario.

        Returns
        -------
        List[Dict[str, Any]]
            Lista de alquileres del usuario.

        Raises
        ------
        ValueError
            Si el email es inválido o no está registrado.
        MySQLError
            Si ocurre un error de base de datos.
        """
        connection: Optional['MySQLConnection'] = None
        try:
            connection = self.get_connection()
            return Usuario.obtener_historial_alquileres(connection, email)
        finally:
            if connection and connection.is_connected():
                connection.close() # Empresa cierra la conexión que abrió


    # --------------------------------------------------------------------------
    # SECCIÓN 4: OPERACIONES RELACIONADAS CON ALQUILERES
    # --------------------------------------------------------------------------

    
    def cargar_alquileres(self) -> List[Dict[str, Any]]:
        """
        Obtiene una lista de todos los alquileres registrados.

        Delega a `Alquiler.obtener_todos`.

        Returns
        -------
        List[Dict[str, Any]]
            Lista de diccionarios, cada uno representando un alquiler.

        Raises
        ------
        MySQLError
            Si ocurre un error de base de datos.
        """
        connection: Optional['MySQLConnection'] = None
        try:
            connection = self.get_connection()
            return Alquiler.obtener_todos(connection)
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    
    def obtener_alquiler_por_id(self, id_alquiler: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene los detalles de un alquiler por su ID formateado.

        Delega a `Alquiler.obtener_por_id`.

        Parameters
        ----------
        id_alquiler_str : str
            ID del alquiler formateado (e.g., "A001").

        Returns
        -------
        Optional[Dict[str, Any]]
            Diccionario con datos del alquiler si se encuentra, `None` si no.

        Raises
        ------
        ValueError
            Si el formato del ID es inválido.
        MySQLError
            Si ocurre un error de base de datos.
        """
        connection: Optional['MySQLConnection'] = None
        try:
            connection = self.get_connection()
            return Alquiler.obtener_por_id(connection, id_alquiler)
        finally:
            if connection and connection.is_connected():
                connection.close() # Empresa cierra la conexión que abrió
        
    
    def alquilar_coche( self, matricula: str, fecha_inicio: str, fecha_fin: str, 
        email: Optional[str] = None
    ) -> bytes:
        """
        Registra un nuevo alquiler y genera la factura.

        Convierte las fechas de string a objetos `date` antes de delegar
        a `Alquiler.alquilar_coche`.

        Parameters
        ----------
        matricula : str
            Matrícula del coche.
        fecha_inicio : str
            Fecha de inicio en formato 'YYYY-MM-DD'.
        fecha_fin : str
            Fecha de fin en formato 'YYYY-MM-DD'.
        email : Optional[str], optional
            Email del usuario.

        Returns
        -------
        bytes
            Contenido binario del PDF de la factura.

        Raises
        ------
        ValueError
            Si las fechas son inválidas o la lógica en `Alquiler.alquilar_coche` falla.
        TypeError
            Si las fechas no pueden convertirse a objetos `date`.
        MySQLError
            Si ocurre un error de base de datos.
        """
        connection: Optional['MySQLConnection'] = None
        try:
            connection = self.get_connection()
            
            # Convertir fechas de string a objetos date
            try:
                fecha_inicio_dt = date.fromisoformat(fecha_inicio)
                fecha_fin_dt = date.fromisoformat(fecha_fin)
            except ValueError:
                raise ValueError("Formato de fecha inválido. Use 'YYYY-MM-DD'.")

            return Alquiler.alquilar_coche(connection, matricula, fecha_inicio_dt, fecha_fin_dt, email)
        finally:
            if connection and connection.is_connected():
                connection.close()

    def finalizar_alquiler(self, id_alquiler: str) -> bool:
        """
        Finaliza un alquiler existente.

        Delega a `Alquiler.finalizar_alquiler`.

        Parameters
        ----------
        id_alquiler_str : str
            ID del alquiler formateado (e.g., "A001").

        Returns
        -------
        bool
            `True` si la finalización fue exitosa.

        Raises
        ------
        ValueError
            Si el formato del ID es inválido o la lógica en `Alquiler.finalizar_alquiler` falla.
        MySQLError
            Si ocurre un error de base de datos.
        """
        connection: Optional['MySQLConnection'] = None
        try:
            connection = self.get_connection()
            return Alquiler.finalizar_alquiler(connection, id_alquiler)
        finally:
            if connection and connection.is_connected():
                connection.close()
