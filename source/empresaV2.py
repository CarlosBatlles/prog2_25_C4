
from datetime import date
from fpdf import FPDF
import os
import mysql.connector
from .models.coche import *
from .models.usuario import *
from .models.alquiler import *

class Empresa():
    """
    Clase principal para gestionar el sistema de alquiler de coches.

    Attributes
    ----------
    nombre : str
        El nombre de la empresa de alquiler de coches.
    coches : list
        Lista temporal para almacenar coches cargados en memoria.
    usuarios : list
        Lista temporal para almacenar usuarios cargados en memoria.
    alquileres : list
        Lista temporal para almacenar alquileres cargados en memoria.
    data_dir : str
        Ruta relativa al directorio 'data' donde se almacenan los archivos CSV.
    """
    
    
    def __init__(self,nombre: str):
        """
        Inicializa una nueva instancia de la clase RentACar.

        Parameters
        ----------
        nombre : str
            El nombre de la empresa de alquiler de coches.
        """
        self.nombre = nombre
        self.connection = self.conectar_mysql()
        
        
    # ---------------------------------------
    # Métodos de Inicialización y Configuración
    # ---------------------------------------
        
    
    def conectar_mysql(self):
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
        
    def get_connection(self):
        """
        Reutiliza la conexión activa o vuelve a conectarse si es necesario.
        """
        if self.connection is None or not self.connection.is_connected():
            self.connection = self.conectar_mysql()
        return self.connection
        

    def _ruta_archivo(self, archivo: str) -> str:
        """
        Construye la ruta completa al archivo CSV en la carpeta 'data'.

        Este método genera la ruta absoluta al archivo especificado dentro del directorio 'data'. 
        Es útil para acceder a los archivos CSV de manera consistente desde cualquier ubicación, 
        independientemente del sistema operativo.

        Parameters
        ----------
        archivo : str
            Nombre del archivo (por ejemplo, 'coches.csv') o ruta relativa dentro del directorio 'data'.

        Returns
        -------
        str
            Ruta completa al archivo en el sistema de archivos.

        Example
        -------
        >>> rentacar = RentACar("MiEmpresa")
        >>> rentacar._ruta_archivo('coches.csv')
        '/ruta/al/proyecto/data/coches.csv'
        
        Notes
        -----
        - El método utiliza `os.path.join` para asegurar que la ruta sea compatible con el sistema operativo.
        - El atributo `self.data_dir` debe estar correctamente configurado para apuntar al directorio 'data'.
        """
        # Asumimos que el directorio 'data' está en el mismo nivel que 'source'
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', archivo)

    
    # ---------------------------------------
    # Métodos de Carga/Guardado de Datos
    # ---------------------------------------

        
    def registrar_coche(self, marca: str, modelo: str, matricula: str, categoria_tipo: str, categoria_precio: str,
                    año: int, precio_diario: float, kilometraje: float, color: str, combustible: str, cv: int,
                    plazas: int, disponible: bool) -> bool:
        """
        Registra un nuevo coche llamando al método estático de la clase Coche.
        
        Parameters
        ----------
        marca : str
            Marca del coche.
        modelo : str
            Modelo del coche.
        matricula : str
            Matrícula única del coche.
        categoria_tipo : str
            Categoría tipo del coche (ej. SUV, Compacto).
        categoria_precio : str
            Categoría de precio del coche (ej. Económico, Medio, Lujo).
        año : int
            Año de fabricación del coche.
        precio_diario : float
            Precio diario del coche.
        kilometraje : float
            Kilometraje actual del coche.
        color : str
            Color del coche.
        combustible : str
            Tipo de combustible del coche.
        cv : int
            Potencia del coche en caballos de vapor.
        plazas : int
            Número de plazas del coche.
        disponible : bool
            Indica si el coche está disponible para alquilar.

        Returns
        -------
        bool or int
            Devuelve el ID generado por MySQL si se registró correctamente.

        Raises
        ------
        ValueError
            Si hay un error al registrar el coche.
        """
        connection = None
        try:
            connection = self.get_connection()
            return Coche.registrar_coche(connection, marca, modelo, matricula, categoria_tipo, categoria_precio,
                                    año, precio_diario, kilometraje, color, combustible, cv, plazas, disponible)
        finally:
            if connection and connection.is_connected():
                connection.close() # Empresa cierra la conexión que abrió
        

    def obtener_detalle_coche_por_matricula(self, matricula: str) -> dict:
        """
        Obtiene los detalles de un coche por su matrícula desde MySQL.
        """
        connection = None
        try:
            connection = self.get_connection()
            return Coche.obtener_detalle_por_matricula(connection, matricula)
        finally:
            if connection and connection.is_connected():
                connection.close() # Empresa cierra la conexión que abrió   
    
    
    def actualizar_matricula(self, id_coche: str, nueva_matricula: str) -> bool:
        """
        Actualiza la matrícula de un coche llamando al método estático de la clase Coche.
        
        Parameters
        ----------
        id_coche : str
            El ID del coche como cadena (ej. "UID01").
        nueva_matricula : str
            Nueva matrícula que se asignará al coche.

        Returns
        -------
        bool
            True si la matrícula se actualizó correctamente.

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
    
    
    def mostrar_categorias_precio(self) -> list:
        """
        Muestra las categorías de precio llamando al método estático de la clase Coche.
        """
        connection = None
        try:
            connection = self.get_connection()
            return Coche.mostrar_categorias_precio(connection)
        finally:
            if connection and connection.is_connected():
                connection.close() # Empresa cierra la conexión que abrió
    
    
    def mostrar_categorias_tipo(self) -> list:
        """
        Muestra las categorías de tipo llamando al método estático de la clase Coche.
        """
        connection = None
        try:
            connection = self.get_connection()
            return Coche.mostrar_categorias_tipo(connection)
        finally:
            if connection and connection.is_connected():
                connection.close() # Empresa cierra la conexión que abrió
    
    
    def buscar_coches_por_filtros(self, categoria_precio: str, categoria_tipo: str = None, marca: str = None, modelo: str = None) -> list:
        """
        Realiza una búsqueda progresiva de coches basada en los filtros proporcionados.

        Parameters
        ----------
        categoria_precio : str
            Categoría de precio obligatoria.
        categoria_tipo : str, optional
            Categoría de tipo del coche.
        marca : str, optional
            Marca del coche.
        modelo : str, optional
            Modelo del coche.

        Returns
        -------
        list
            Lista de diccionarios con los coches que cumplen los criterios de búsqueda.
        """
        connection = None
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
    
    
    def registrar_usuario(self, nombre: str, tipo: str, email: str, contraseña: str) -> int:
        """
        Llama al método estático de `Usuario.registrar_usuario()` pasando la conexión.
        """
        connection = None
        try:
            connection = self.get_connection()
            return Usuario.registrar_usuario(connection, nombre, tipo, email, contraseña)
        finally:
            if connection and connection.is_connected():
                connection.close() # Empresa cierra la conexión que abrió
    
    def actualizar_usuario(self, email: str, nueva_contraseña: str) -> bool:
        """
        Llama al método estático de `Usuario.actualizar_contraseña(...)`.
        """
        connection = None
        try:
            connection = self.get_connection()
            return Usuario.actualizar_contraseña(connection, email, nueva_contraseña)
        finally:
            if connection and connection.is_connected():
                connection.close() # Empresa cierra la conexión que abrió
    
    
    def dar_baja_usuario(self, email: str) -> bool:
        """
        Llama al método estático de `Usuario.dar_baja_usuario(...)` pasando la conexión.
        """
        connection = None
        try:
            connection = self.get_connection()
            return Usuario.dar_baja_usuario(connection, email)
        finally:
            if connection and connection.is_connected():
                connection.close() # Empresa cierra la conexión que abrió
    
    
    def iniciar_sesion(self, email: str, contraseña: str) -> dict:
        """
        Llama al método estático `Usuario.iniciar_sesion(...)` pasando la conexión.
        """
        connection = None
        try:
            connection = self.get_connection()
            return Usuario.iniciar_sesion(connection, email, contraseña)
        finally:
            if connection and connection.is_connected():
                connection.close() # Empresa cierra la conexión que abrió
    
    
    def obtener_usuarios(self) -> list[dict]:
        """
        Llama al método `usuario.obtener_usuarios(...)` pasando la conexión.
        """
        connection = None
        try:
            connection = self.get_connection()
            return Usuario.obtener_usuarios(connection)
        finally:
            if connection and connection.is_connected():
                connection.close() # Empresa cierra la conexión que abrió
    

    def obtener_usuario_por_email(self, email: str) -> dict:
        """
        Llama al método `usuario.obtener_usuario_por_email(...)` pasando la conexión.
        """
        connection = None
        try:
            connection = self.get_connection()
            return Usuario.obtener_usuario_por_email(connection, email)
        finally:
            if connection and connection.is_connected():
                connection.close() # Empresa cierra la conexión que abrió
    
    def obtener_historial_alquileres(self, email: str) -> List[Dict[str, Any]]:
        """
        Llama al método estático `Usuario.obtener_historial_alquileres(...)` pasando la conexión.
        """
        connection = None
        try:
            connection = self.get_connection()
            return Usuario.obtener_historial_alquileres(connection, email)
        finally:
            if connection and connection.is_connected():
                connection.close() # Empresa cierra la conexión que abrió

    
    def cargar_alquileres(self) -> list[dict]:
        """
        Llama al método `Alquiler.obtener_todos(...)` pasando la conexión.
        """
        connection = None
        try:
            connection = self.get_connection()
            return Alquiler.obtener_todos(connection)
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    
    def obtener_alquiler_por_id(self, id_alquiler: str) -> dict:
        """
        Obtiene un alquiler por su ID desde la base de datos.
        """
        connection = None
        try:
            connection = self.get_connection()
            return Alquiler.obtener_por_id(connection, id_alquiler)
        finally:
            if connection and connection.is_connected():
                connection.close() # Empresa cierra la conexión que abrió
        
    
    def alquilar_coche(self, matricula: str, fecha_inicio: str, fecha_fin: str, email: str = None):
        connection = None
        try:
            connection = self.get_connection()
            
            # Convertir fechas de string a objetos date
            fecha_inicio_dt = date.fromisoformat(fecha_inicio)
            fecha_fin_dt = date.fromisoformat(fecha_fin)

            return Alquiler.alquilar_coche(connection, matricula, fecha_inicio_dt, fecha_fin_dt, email)
        finally:
            if connection and connection.is_connected():
                connection.close() # Empresa cierra la conexión que abrió
        

    def finalizar_alquiler(self, id_alquiler: str) -> bool:
        """
        Llama al método estático `Alquiler.finalizar_alquiler(...)` pasando la conexión.
        """
        connection = None
        try:
            connection = self.get_connection()
            return Alquiler.finalizar_alquiler(connection, id_alquiler)
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    
    def calcular_precio_total(self, matricula: str, fecha_inicio: date, fecha_fin: date, email: str = None) -> float:
        """
        Llama al método estático `Alquiler.calcular_precio_total(...)` pasando la conexión.
        """
        connection = None
        try:
            connection = self.get_connection()
            return Alquiler.calcular_precio_total(connection, matricula, fecha_inicio, fecha_fin, email)
        finally:
            if connection and connection.is_connected():
                connection.close() # Empresa cierra la conexión que abrió
    
    def generar_factura_pdf(self, alquiler: dict) -> bytes:
        """
        Genera una factura llamando al método estático de la clase Alquiler.
        """
        return Alquiler.generar_factura_pdf(alquiler)