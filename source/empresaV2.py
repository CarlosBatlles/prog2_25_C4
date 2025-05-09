import pandas as pd
from datetime import datetime
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
    
    
    # ---------------------------------------
    # Métodos de Inicialización y Configuración
    # ---------------------------------------
    
    
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
        
    def get_connection(self):
        if not self.connection.is_connected():
            self.connection.reconnect()
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


    def _cargar_csv(self, archivo: str) -> pd.DataFrame:
        """
        Carga un archivo CSV desde la carpeta 'data'.

        Parameters
        ----------
        archivo : str
            Nombre del archivo CSV a cargar.

        Returns
        -------
        pd.DataFrame
            DataFrame cargado desde el archivo CSV.

        Raises
        ------
        FileNotFoundError
            Si el archivo no se encuentra en la ruta especificada.
        ValueError
            Si ocurre un error al cargar el archivo.

        Notes
        -----
        Este método utiliza la función `_ruta_archivo` para construir la ruta completa del archivo.
        """
        ruta = self._ruta_archivo(archivo)
        try:
            return pd.read_csv(ruta)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"El archivo {ruta} no se encontró.") from e
        except Exception as e:
            raise ValueError(f"Error al cargar el archivo {ruta}: {e}") from e
        
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
        connection = self.get_connection()
        return Coche.registrar_coche(connection, marca, modelo, matricula, categoria_tipo, categoria_precio,
                                año, precio_diario, kilometraje, color, combustible, cv, plazas, disponible)
        
        
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
        try:
            # Convertir el ID formateado ("UID01") a su parte numérica (1)
            if not id_coche.startswith("UID"):
                raise ValueError("Formato de ID inválido. Debe comenzar con 'UID'")
            
            id_numero = int(id_coche[3:])  # UID01 → 1

            # Pasar solo los valores necesarios
            connection = self.get_connection()
            return Coche.actualizar_matricula(connection, id_numero, nueva_matricula)

        except ValueError as ve:
            # Captura errores de formato de ID o conversiones fallidas
            raise ValueError(f"ID de coche inválido: {ve}")
    
    
    def eliminar_coche(self, id_coche: str) -> bool:
        """
        Elimina un coche llamando al método estático de la clase Coche.
        """
        connection = self.get_connection()
        return Coche.eliminar_coche(connection, id_coche)
    
    
    def mostrar_categorias_precio(self) -> list:
        """
        Muestra las categorías de precio llamando al método estático de la clase Coche.
        """
        connection = self.get_connection()
        return Coche.mostrar_categorias_precio(connection)
    
    
    def mostrar_categorias_tipo(self) -> list:
        """
        Muestra las categorías de tipo llamando al método estático de la clase Coche.
        """
        connection = self.get_connection()
        return Coche.mostrar_categorias_tipo(connection)
    
    
    def buscar_coches_por_filtros(self, categoria_precio, categoria_tipo, marca, modelo):
        connection = self.get_connection()
        return Coche.filtrar_por_modelo(connection, categoria_precio, categoria_tipo, marca, modelo)
    
    
    
    
    
    
    
    
    def registrar_usuario(self, nombre: str, tipo: str, email: str, contraseña: str) -> int:
        """
        Llama al método estático de `Usuario.registrar_usuario()` pasando la conexión.
        """
        connection = self.get_connection()
        return Usuario.registrar_usuario(connection, nombre, tipo, email, contraseña)
    
    
    def actualizar_usuario(self, email: str, nueva_contraseña: str) -> bool:
        """
        Llama al método estático de `Usuario.actualizar_contraseña(...)`.
        """
        connection = self.get_connection()
        return Usuario.actualizar_contraseña(connection, email, nueva_contraseña)
    
    
    def dar_baja_usuario(self, email: str) -> bool:
        """
        Elimina un usuario llamando al método estático de la clase Usuario.
        """
        return Usuario.dar_baja_usuario(self, email)
    
    
    def iniciar_sesion(self, email: str, contraseña: str) -> bool:
        """
        Inicia sesión llamando al método estático de la clase Usuario.
        """
        return Usuario.iniciar_sesion(self, email, contraseña)
    
    
    def obtener_historial_alquileres(self, email: str) -> list[dict]:
        """
        Obtiene el historial de alquileres de un usuario llamando al método estático de la clase Usuario.
        """
        return Usuario.obtener_historial_alquileres(self, email)
    

    def alquilar_coche(self, matricula: str, fecha_inicio: str, fecha_fin: str, 
                        email: str = None) -> bytes:
        """
        Registra un nuevo alquiler llamando al método estático de la clase Alquiler.
        """
        return Alquiler.alquilar_coche(self, matricula, fecha_inicio, fecha_fin, email)
    

    def finalizar_alquiler(self, id_alquiler: str) -> bool:
        """
        Finaliza un alquiler llamando al método estático de la clase Alquiler.
        """
        return Alquiler.finalizar_alquiler(self, id_alquiler)
    
    
    def calcular_precio_total(self,fecha_inicio: datetime,fecha_fin: datetime,matricula: str,
                            email: str = None) -> float:
        """
        Calcula el precio total del alquiler llamando al método estático de la clase Alquiler.
        """
        return Alquiler.calcular_precio_total(self, fecha_inicio, fecha_fin, matricula, email)
    
    
    def generar_factura_pdf(self, alquiler: dict) -> bytes:
        """
        Genera una factura llamando al método estático de la clase Alquiler.
        """
        return Alquiler.generar_factura_pdf(alquiler)