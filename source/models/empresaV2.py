import pandas as pd
from datetime import datetime
from fpdf import FPDF
import re
import hashlib
import os
from coche import *
from usuario import *
from alquiler import *  

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
        self.coches = []
        self.usuarios = []
        self.alquileres = []
        self.data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')


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
        return os.path.join(self.data_dir, archivo)

    
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
        """
        return Coche.registrar_coche(self, marca, modelo, matricula, categoria_tipo, categoria_precio, año,
                                    precio_diario, kilometraje, color, combustible, cv, plazas, disponible)
        
        
    def actualizar_matricula(self, id_coche: str, nueva_matricula: str) -> bool:
        """
        Actualiza la matrícula de un coche llamando al método estático de la clase Coche.
        """
        return Coche.actualizar_matricula(self, id_coche, nueva_matricula)
    
    
    def eliminar_coche(self, id_coche: str) -> bool:
        """
        Elimina un coche llamando al método estático de la clase Coche.
        """
        return Coche.eliminar_coche(self, id_coche)
    
    
    def mostrar_categorias_tipo(self) -> list:
        """
        Muestra las categorías de tipo llamando al método estático de la clase Coche.
        """
        return Coche.mostrar_categorias_tipo(self)
    
    
    def mostrar_categorias_tipo(self) -> list:
        """
        Muestra las categorías de tipo llamando al método estático de la clase Coche.
        """
        return Coche.mostrar_categorias_tipo(self)
    
    
    def cargar_coches_disponibles(self) -> pd.DataFrame:
        """
        Carga los coches disponibles llamando al método estático de la clase Coche.
        """
        return Coche.cargar_coches_disponibles(self)
    
    
    def obtener_categorias_precio(self) -> list:
        """
        Obtiene las categorías de precio llamando al método estático de la clase Coche.
        """
        return Coche.obtener_categorias_precio(self)
    
    
    def filtrar_por_categoria_precio(self, categoria_precio: str) -> pd.DataFrame:
        """
        Filtra coches disponibles por categoría de precio llamando al método estático de la clase Coche.
        """
        return Coche.filtrar_por_categoria_precio(self, categoria_precio)
    
    
    def obtener_categorias_tipo(self, categoria_precio: str) -> list:
        """
        Obtiene las categorías de tipo llamando al método estático de la clase Coche.
        """
        return Coche.obtener_categorias_tipo(self, categoria_precio)
    
    
    def filtrar_por_categoria_tipo(self, categoria_precio: str, categoria_tipo: str) -> pd.DataFrame:
        """
        Filtra coches disponibles por categoría de tipo llamando al método estático de la clase Coche.
        """
        return Coche.filtrar_por_categoria_tipo(self, categoria_precio, categoria_tipo)
    
    
    def obtener_marcas(self, categoria_precio: str, categoria_tipo: str) -> list:
        """
        Obtiene las marcas llamando al método estático de la clase Coche.
        """
        return Coche.obtener_marcas(self, categoria_precio, categoria_tipo)
    
    
    def filtrar_por_marca(self, categoria_precio: str, categoria_tipo: str, marca: str) -> pd.DataFrame:
        """
        Filtra coches disponibles por marca llamando al método estático de la clase Coche.
        """
        return Coche.filtrar_por_marca(self, categoria_precio, categoria_tipo, marca)
    
    
    def obtener_modelos(self, categoria_precio: str, categoria_tipo: str, marca: str) -> list:
        """
        Obtiene los modelos llamando al método estático de la clase Coche.
        """
        return Coche.obtener_modelos(self, categoria_precio, categoria_tipo, marca)
    
    
    def filtrar_por_modelo(
        self, categoria_precio: str, categoria_tipo: str, marca: str, modelo: str
    ) -> pd.DataFrame:
        """
        Filtra coches disponibles por modelo llamando al método estático de la clase Coche.
        """
        return Coche.filtrar_por_modelo(self, categoria_precio, categoria_tipo, marca, modelo)
    
    
    def obtener_detalles_coches(
        self, categoria_precio: str, categoria_tipo: str, marca: str, modelo: str
    ) -> list[dict]:
        """
        Obtiene los detalles de los coches llamando al método estático de la clase Coche.
        """
        return Coche.obtener_detalles_coches(self, categoria_precio, categoria_tipo, marca, modelo)
    
    
    def registrar_usuario(self, nombre: str, tipo: str, email: str, contraseña: str) -> bool:
        """
        Registra un nuevo usuario llamando al método estático de la clase Usuario.
        """
        return Usuario.registrar_usuario(self, nombre, tipo, email, contraseña)
    
    
    def actualizar_usuario(self, email: str, nueva_contraseña: str = None) -> bool:
        """
        Actualiza los datos de un usuario llamando al método estático de la clase Usuario.
        """
        return Usuario.actualizar_usuario(self, email, nueva_contraseña)
    
    
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