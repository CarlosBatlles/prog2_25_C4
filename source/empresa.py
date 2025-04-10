import pandas as pd
from datetime import datetime
from fpdf import FPDF
import re
import hashlib
import os

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


    def _guardar_csv(self, archivo: str, df: pd.DataFrame) -> None:
        """
        Guarda un DataFrame en un archivo CSV en la carpeta 'data'.

        Parameters
        ----------
        archivo : str
            Nombre del archivo CSV donde se guardará el DataFrame.
        df : pd.DataFrame
            DataFrame que se desea guardar.

        Raises
        ------
        ValueError
            Si ocurre un error al guardar el archivo.

        Notes
        -----
        Este método utiliza la función `_ruta_archivo` para construir la ruta completa del archivo.
        """
        ruta = self._ruta_archivo(archivo)
        try:
            df.to_csv(ruta, index=False)
        except Exception as e:
            raise ValueError(f"Error al guardar el archivo {ruta}: {e}") from e
            
            
    def cargar_coches(self) -> pd.DataFrame:
        """
        Carga los coches desde un archivo CSV.

        Este método utiliza el método auxiliar `_cargar_csv` para cargar los datos 
        de los coches desde el archivo 'coches.csv'.

        Returns
        -------
        pd.DataFrame
            DataFrame que contiene los datos de los coches almacenados en el archivo CSV.

        Notes
        -----
        Este método delega la carga del archivo CSV al método `_cargar_csv`, 
        el cual maneja las excepciones relacionadas con la lectura del archivo.
        """
        return self._cargar_csv('coches.csv')
    

    def cargar_usuarios(self) -> pd.DataFrame:
        """
        Carga los usuarios desde un archivo CSV.

        Este método utiliza el método auxiliar `_cargar_csv` para cargar los datos 
        de los usuarios desde el archivo 'clientes.csv'.

        Returns
        -------
        pd.DataFrame
            DataFrame que contiene los datos de los usuarios almacenados en el archivo CSV.

        Notes
        -----
        Este método delega la carga del archivo CSV al método `_cargar_csv`, 
        el cual maneja las excepciones relacionadas con la lectura del archivo.
        """
        return self._cargar_csv('clientes.csv')
    

    def cargar_alquileres(self) -> pd.DataFrame:
        """
        Carga los alquileres desde un archivo CSV.

        Este método utiliza el método auxiliar `_cargar_csv` para cargar los datos 
        de los alquileres desde el archivo 'alquileres.csv'.

        Returns
        -------
        pd.DataFrame
            DataFrame que contiene los datos de los alquileres almacenados en el archivo CSV.

        Notes
        -----
        Este método delega la carga del archivo CSV al método `_cargar_csv`, 
        el cual maneja las excepciones relacionadas con la lectura del archivo.
        """
        return self._cargar_csv('alquileres.csv')
    
    
    # ---------------------------------------
    # Métodos de Validación
    # ---------------------------------------
    
    
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
    

    def hash_contraseña(self, contraseña: str) -> str:
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
    
    
    # ---------------------------------------
    # Métodos de Generación de IDs
    # ---------------------------------------
    
    
    def generar_id_usuario(self) -> str:
        """
        Genera un ID único para un nuevo usuario.

        Este método carga los usuarios existentes desde el archivo CSV y genera un 
        nuevo ID basado en el último ID registrado. Si no hay usuarios registrados, 
        el primer ID será 'U001'.

        Returns
        -------
        str
            Un ID único para el nuevo usuario en formato 'UXXX', donde XXX es un 
            número de tres dígitos (por ejemplo, U001, U002).

        Notes
        -----
        - El ID se genera incrementando en 1 el número del último ID registrado.
        - Si no hay usuarios, el ID generado será 'U001'.
        """
        df = self.cargar_usuarios()
        if df.empty:
            return 'U001'
        ultimo_id = df['id_usuario'].iloc[-1]
        num = int(ultimo_id[1:]) + 1  # Extraer el número y sumar 1
        return f'U{num:03d}'  # Formato U001, U002, etc.
        
        
    def generar_id_alquiler(self) -> str:
        """
        Genera un ID único para un nuevo alquiler.

        Este método carga los alquileres existentes desde el archivo CSV y genera un 
        nuevo ID basado en el último ID registrado. Si no hay alquileres registrados, 
        el primer ID será 'A001'.

        Returns
        -------
        str
            Un ID único para el nuevo alquiler en formato 'AXXX', donde XXX es un 
            número de tres dígitos (por ejemplo, A001, A002).

        Notes
        -----
        - El ID se genera incrementando en 1 el número del último ID registrado.
        - Si no hay alquileres, el ID generado será 'A001'.
        """
        df = self.cargar_alquileres()
        if df.empty:
            return 'A001'
        ultimo_id = df['id_alquiler'].iloc[-1]
        num = int(ultimo_id[1:]) + 1
        return f'A{num:03d}'
    
    
    def generar_id_coche(self) -> str:
        """
        Genera un ID único para un nuevo coche.

        Este método carga los coches existentes desde el archivo CSV y genera un 
        nuevo ID basado en el último ID registrado. Si no hay coches registrados, 
        el primer ID será 'UID01'.

        Returns
        -------
        str
            Un ID único para el nuevo coche en formato 'UIDXX', donde XX es un 
            número de dos dígitos (por ejemplo, UID01, UID02).

        Notes
        -----
        - El ID se genera incrementando en 1 el número del último ID registrado.
        - Si no hay coches, el ID generado será 'UID01'.
        """
        df = self.cargar_coches()
        ultimo_id = df['id'].iloc[-1]
        num = int(ultimo_id[3:]) + 1  # Extraer el número después de 'UID'
        return f'UID{num:02d}'
    
    
    # ---------------------------------------------------------
    # Métodos de Registro/Actualización/Eliminación de Entidades
    # ----------------------------------------------------------
    
    
    def registrar_coche(
        self,
        marca: str,
        modelo: str,
        matricula: str,
        categoria_tipo: str,
        categoria_precio: str,
        año: int,
        precio_diario: float,
        kilometraje: float,
        color: str,
        combustible: str,
        cv: int,
        plazas: int,
        disponible: bool
    ) -> bool:
        """
        Añade un nuevo coche al sistema.

        Este método registra un coche con los datos proporcionados y lo guarda en el archivo CSV 
        correspondiente. Realiza varias validaciones para asegurarse de que los datos sean correctos.

        Parameters
        ----------
        marca : str
            Marca del coche.
        modelo : str
            Modelo del coche.
        matricula : str
            Matrícula del coche.
        categoria_tipo : str
            Categoría de tipo del coche (por ejemplo, SUV, Sedán, etc.).
        categoria_precio : str
            Categoría de precio del coche (por ejemplo, Lujo, Premium, etc.).
        año : int
            Año de fabricación del coche.
        precio_diario : float
            Precio diario de alquiler del coche.
        kilometraje : float
            Kilometraje del coche.
        color : str
            Color del coche.
        combustible : str
            Tipo de combustible del coche (por ejemplo, Gasolina, Diésel, etc.).
        cv : int
            Potencia del coche en caballos de vapor (CV).
        plazas : int
            Número de plazas del coche.
        disponible : bool
            Indica si el coche está disponible para alquilar (True o False).

        Returns
        -------
        bool
            True si el coche se registró correctamente, False en caso contrario.

        Raises
        ------
        ValueError
            Si alguno de los campos obligatorios no tiene un valor válido.
        TypeError
            Si el campo 'disponible' no es un valor booleano.

        Notes
        -----
        - Todos los campos de texto deben tener un valor no vacío.
        - El precio diario debe ser mayor que 0.
        - El kilometraje no puede ser negativo.
        - La potencia del coche debe ser mayor que 0.
        - El número de plazas debe ser mayor o igual a 2.
        """
        # Validaciones de campos obligatorios
        if not all([marca, modelo, matricula, categoria_tipo, categoria_precio]):
            raise ValueError("Todos los campos de texto (marca, modelo, matricula, categoria_tipo, categoria_precio) deben tener un valor.")

        if precio_diario <= 0:
            raise ValueError("El precio diario debe ser mayor que 0.")
        if kilometraje < 0:
            raise ValueError("El kilometraje no puede ser negativo.")
        if cv <= 0:
            raise ValueError("La potencia del coche debe ser mayor que 0.")
        if plazas < 2:
            raise ValueError("Las plazas del coche deben ser mayores o iguales a 2.")
        if not isinstance(disponible, bool):
            raise TypeError("El campo 'disponible' debe ser True o False.")

        # Cargar los coches existentes
        df_coches = self.cargar_coches()
        if df_coches is None:
            raise ValueError("No se pudieron cargar los coches. Verifica el archivo CSV.")

        # Generar un ID único para el coche
        id_coche = self.generar_id_coche()

        # Crear un diccionario con los datos del nuevo coche
        nuevo_coche = {
            'id': id_coche,
            'marca': marca,
            'modelo': modelo,
            'matricula': matricula,
            'categoria_tipo': categoria_tipo,
            'categoria_precio': categoria_precio,
            'año': año,
            'precio_diario': precio_diario,
            'kilometraje': kilometraje,
            'color': color,
            'combustible': combustible,
            'cv': cv,
            'plazas': plazas,
            'disponible': disponible
        }

        # Crear un DataFrame con el nuevo coche y actualizar el archivo CSV
        df_nuevo_coche = pd.DataFrame([nuevo_coche])
        df_actualizado = pd.concat([df_coches, df_nuevo_coche], ignore_index=True)

        try:
            self._guardar_csv('coches.csv', df_actualizado)
            return True
        except Exception as e:
            raise ValueError(f"Error al guardar el coche en el archivo CSV: {e}")
        
        
    def actualizar_matricula(self, id_coche: str, nueva_matricula: str) -> bool:
        """
        Actualiza la matrícula de un coche existente en el sistema.

        Este método verifica si el ID del coche existe y si la nueva matrícula no está duplicada 
        antes de realizar la actualización en el archivo CSV correspondiente.

        Parameters
        ----------
        id_coche : str
            El ID único del coche cuya matrícula se desea actualizar.
        nueva_matricula : str
            La nueva matrícula que se asignará al coche.

        Returns
        -------
        bool
            True si la matrícula se actualizó correctamente.

        Raises
        ------
        ValueError
            Si el ID del coche no está registrado o si la nueva matrícula ya está en uso.
        Exception
            Si ocurre un error al guardar los cambios en el archivo CSV.

        Notes
        -----
        - Antes de actualizar la matrícula, se verifica que el ID del coche exista en el sistema.
        - También se asegura que la nueva matrícula no esté registrada en otro coche.
        """
        # Cargar los coches actuales
        df_coches = self.cargar_coches()
        if df_coches is None:
            raise ValueError("No se pudieron cargar los coches. Revisa el archivo CSV.")

        # Verificar si el ID existe en el DataFrame
        if id_coche not in df_coches['id'].values:
            raise ValueError(f"El coche con ID {id_coche} no está registrado.")
        
        # Verificar si la nueva matrícula ya existe
        if nueva_matricula in df_coches['matricula'].values:
            raise ValueError(f"La matrícula {nueva_matricula} ya está registrada en otro coche.")

        # Actualizar la matrícula en el DataFrame
        df_coches.loc[df_coches['id'] == id_coche, 'matricula'] = nueva_matricula

        # Guardar los cambios en el archivo CSV
        try:
            self._guardar_csv("coches.csv", df_coches)
        except Exception as e:
            raise ValueError(f"Error al guardar los cambios en el archivo CSV: {e}")

        return True   
    
    
    def eliminar_coche(self, id_coche: str, matricula: str) -> bool:
        """
        Elimina un coche del sistema basándose en su ID y matrícula.

        Este método verifica si el coche con el ID proporcionado existe en el sistema 
        y lo elimina del archivo CSV correspondiente.

        Parameters
        ----------
        id_coche : str
            El ID único del coche que se desea eliminar.
        matricula : str
            La matrícula del coche que se desea eliminar (usada solo para mensajes).

        Returns
        -------
        bool
            True si el coche se eliminó correctamente.

        Raises
        ------
        ValueError
            Si el coche con el ID proporcionado no está registrado o si ocurre un error al guardar los cambios.

        Notes
        -----
        - Antes de eliminar el coche, se verifica que el ID exista en el sistema.
        - El método utiliza el archivo CSV como fuente de datos, por lo que los cambios son persistentes.
        """
        # Cargar los coches actuales
        df_coches = self.cargar_coches()
        if df_coches is None:
            raise ValueError("No se pudieron cargar los coches. Revisa el archivo CSV.")

        # Verificar si el ID existe en el DataFrame
        if id_coche not in df_coches['id'].values:
            raise ValueError(f"El coche con ID {id_coche} no está registrado.")

        # Filtrar el DataFrame para excluir al coche con el ID proporcionado
        df_actualizado = df_coches[df_coches['id'] != id_coche]

        # Guardar los cambios usando el método auxiliar
        try:
            self._guardar_csv('coches.csv', df_actualizado)
            return True
        except Exception as e:
            raise ValueError(f"Error al guardar los cambios en el archivo CSV: {e}")
        
    
    def registrar_usuario(
        self,
        nombre: str,
        tipo: str,
        email: str,
        contraseña: str
    ) -> bool:
        """
        Registra un nuevo usuario en el sistema.

        Este método verifica si el correo electrónico ya está registrado, hashea la contraseña 
        y guarda los datos del usuario en el archivo CSV correspondiente.

        Parameters
        ----------
        nombre : str
            Nombre completo del usuario.
        tipo : str
            Tipo de usuario (por ejemplo, 'cliente', 'admin').
        email : str
            Correo electrónico del usuario. Debe ser único y válido.
        contraseña : str
            Contraseña del usuario. Se almacenará como un hash seguro.

        Returns
        -------
        bool
            True si el usuario se registró correctamente.

        Raises
        ------
        ValueError
            Si algún campo obligatorio está vacío, si el correo electrónico no es válido 
            o si el correo electrónico ya está registrado.
        Exception
            Si ocurre un error al guardar los cambios en el archivo CSV.

        Notes
        -----
        - El correo electrónico debe ser único en el sistema.
        - La contraseña se almacena como un hash SHA-256 para mayor seguridad.
        """
        # Cargar los usuarios actuales
        df_usuarios = self.cargar_usuarios()
        if df_usuarios is None:
            raise ValueError("No se pudieron cargar los usuarios. Verifica el archivo CSV.")

        # Validaciones de campos obligatorios
        if not all([nombre, tipo, email, contraseña]):
            raise ValueError("Debes rellenar todos los campos.")

        if not self.es_email_valido(email):
            raise ValueError("El correo electrónico no es válido.")

        if email in df_usuarios['email'].values:
            raise ValueError("El correo electrónico ya está registrado.")

        # Generar un ID único para el usuario
        id_user = self.generar_id_usuario()

        # Hashear la contraseña
        contraseña_hasheada = self.hash_contraseña(contraseña)

        # Crear un diccionario con los datos del nuevo usuario
        new_user = {
            'id_usuario': id_user,
            'nombre': nombre,
            'tipo': tipo,
            'email': email,
            'contraseña': contraseña_hasheada,
        }

        # Crear un DataFrame con el nuevo usuario y actualizar el archivo CSV
        df_nuevo_usuario = pd.DataFrame([new_user])
        df_actualizado = pd.concat([df_usuarios, df_nuevo_usuario], ignore_index=True)

        try:
            self._guardar_csv('clientes.csv', df_actualizado)
            return True
        except Exception as e:
            raise ValueError(f"Error al guardar el usuario en el archivo CSV: {e}")
        
                
    def actualizar_usuario(self, email, nueva_contraseña=None):
        """
        Actualiza los datos de un usuario existente.
        Solo permite cambiar la contraseña del usuario autenticado.
        """
        # Cargar los usuarios actuales
        df_usuarios = self.cargar_usuarios()
        if df_usuarios is None:
            raise ValueError("No se pudieron cargar los usuarios. Revisa el archivo CSV.")

        # Verificar si el email existe en el DataFrame
        if email not in df_usuarios['email'].values:
            raise ValueError(f"El correo electrónico {email} no está registrado.")

        # Si se proporciona una nueva contraseña, validarla y actualizarla
        if nueva_contraseña:
            # Hashear la nueva contraseña
            contraseña_hasheada = self.hash_contraseña(nueva_contraseña)

            # Actualizar la contraseña en el DataFrame
            df_usuarios.loc[df_usuarios['email'] == email, 'contraseña'] = contraseña_hasheada

            # Guardar los cambios en el archivo CSV
            try:
                self._guardar_csv('clientes.csv', df_usuarios)
                print(f"La contraseña del usuario con email {email} ha sido actualizada exitosamente.")
            except Exception as e:
                raise ValueError(f"Error al guardar los cambios en el archivo CSV: {e}")

        return True
    
    
    def dar_baja_usuario(self, email: str) -> bool:
        """
        Elimina un usuario del sistema basándose en su correo electrónico.

        Este método verifica si el correo electrónico existe en el sistema y elimina 
        al usuario correspondiente del archivo CSV.

        Parameters
        ----------
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
        df_usuarios = self.cargar_usuarios()
        if df_usuarios is None:
            raise ValueError("No se pudieron cargar los usuarios. Revisa el archivo CSV.")

        # Verificar si el email existe en el DataFrame
        if email not in df_usuarios['email'].values:
            raise ValueError("El correo que has introducido no está registrado.")

        # Filtrar el DataFrame para excluir al usuario con el email proporcionado
        df_actualizado = df_usuarios[df_usuarios['email'] != email]

        # Guardar los cambios usando el método auxiliar
        try:
            self._guardar_csv('clientes.csv', df_actualizado)
            return True
        except Exception as e:
            raise ValueError(f"Error al guardar los cambios en el archivo CSV: {e}")
        
    
    def alquilar_coche(
        self,
        matricula: str,
        fecha_inicio: str,
        fecha_fin: str,
        email: str = None
    ) -> bytes:
        """
        Registra un nuevo alquiler de coche en el sistema.

        Este método verifica la disponibilidad del coche, calcula el precio total del alquiler, 
        actualiza el estado del coche y guarda el alquiler en el archivo CSV correspondiente. 
        También genera una factura en formato PDF.

        Parameters
        ----------
        matricula : str
            La matrícula del coche que se desea alquilar.
        fecha_inicio : str
            Fecha de inicio del alquiler en formato 'YYYY-MM-DD'.
        fecha_fin : str
            Fecha de fin del alquiler en formato 'YYYY-MM-DD'.
        email : str, optional
            Correo electrónico del usuario que realiza el alquiler (por defecto es None para invitados).

        Returns
        -------
        bytes
            Los bytes del archivo PDF generado como factura del alquiler.

        Raises
        ------
        ValueError
            Si ocurre algún error durante la validación de datos o el proceso de alquiler.
        Exception
            Si ocurre un error al guardar los cambios en los archivos CSV o al generar la factura.

        Notes
        -----
        - El coche debe estar disponible para poder ser alquilado.
        - Las fechas deben estar en formato 'YYYY-MM-DD' y la fecha de inicio debe ser anterior a la fecha de fin.
        - Si no se proporciona un correo electrónico, el alquiler se registra como invitado.
        """
        # Cargar los archivos CSV
        df_coches = self.cargar_coches()
        if df_coches is None:
            raise ValueError("Error al cargar el archivo de coches.")

        df_clientes = self.cargar_usuarios()
        if df_clientes is None:
            raise ValueError("Error al cargar el archivo de usuarios.")

        df_alquiler = self.cargar_alquileres()
        if df_alquiler is None:
            raise ValueError("Error al cargar el archivo de alquileres.")

        # Verificar si existe un coche con la matrícula proporcionada
        coche = df_coches[df_coches['matricula'] == matricula]
        if coche.empty:
            raise ValueError(f"No se encontró ningún coche con la matrícula: {matricula}.")
        coche = coche.iloc[0]

        # Validar el correo electrónico si se proporciona
        if email and not self.es_email_valido(email):
            raise ValueError("El correo electrónico no es válido.")

        # Convertir las fechas a objetos datetime
        try:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, "%Y-%m-%d")
            fecha_fin_dt = datetime.strptime(fecha_fin, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Las fechas deben estar en formato YYYY-MM-DD.")

        # Validar que la fecha de inicio sea anterior a la fecha de fin
        if fecha_inicio_dt >= fecha_fin_dt:
            raise ValueError("La fecha de inicio debe ser anterior a la fecha de fin.")

        # Verificar disponibilidad del coche
        if not coche['disponible']:
            raise ValueError(f"El coche {coche['marca']} - {coche['modelo']} no está disponible para alquilar.")

        # Calcular el precio total del alquiler
        precio_total = self.calcular_precio_total(fecha_inicio_dt, fecha_fin_dt, matricula, email)

        # Actualizar el estado del coche a no disponible
        df_coches.loc[df_coches['matricula'] == matricula, 'disponible'] = False

        # Determinar el ID del usuario (invitado o registrado)
        id_usuario = 'INVITADO'
        if email:
            user = df_clientes[df_clientes['email'] == email]
            if user.empty:
                raise ValueError(f"No se encontró ningún usuario con el email: {email}")
            id_usuario = user.iloc[0]['id_usuario']

        # Crear un diccionario con los datos del nuevo alquiler
        nuevo_alquiler = {
            'id_alquiler': self.generar_id_alquiler(),
            'id_coche': coche['id'],
            'id_usuario': id_usuario,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'coste_total': precio_total,
            'activo': True
        }

        # Agregar el nuevo alquiler al DataFrame de alquileres
        df_nuevo_alquiler = pd.DataFrame([nuevo_alquiler])
        df_actualizado = pd.concat([df_alquiler, df_nuevo_alquiler], ignore_index=True)

        # Guardar los cambios en los archivos CSV
        try:
            self._guardar_csv('coches.csv', df_coches)
            self._guardar_csv('alquileres.csv', df_actualizado)
        except Exception as e:
            raise ValueError(f"Error al guardar los cambios en los archivos CSV: {e}")

        # Generar la factura en PDF
        datos_factura = {
            'id_alquiler': nuevo_alquiler['id_alquiler'],
            'marca': coche['marca'],
            'modelo': coche['modelo'],
            'matricula': coche['matricula'],
            'fecha_inicio': nuevo_alquiler['fecha_inicio'],
            'fecha_fin': nuevo_alquiler['fecha_fin'],
            'coste_total': nuevo_alquiler['coste_total'],
            'id_usuario': id_usuario
        }

        try:
            pdf_bytes = self.generar_factura_pdf(datos_factura)
            return pdf_bytes
        except Exception as e:
            raise ValueError(f"Error al generar la factura en PDF: {e}")
        
        
    def finalizar_alquiler(self, id_alquiler: str) -> bool:
        """
        Finaliza un alquiler existente y marca el coche como disponible.

        Este método verifica si el alquiler con el ID proporcionado existe y está activo. 
        Si es así, finaliza el alquiler y actualiza el estado del coche correspondiente 
        en los archivos CSV.

        Parameters
        ----------
        id_alquiler : str
            El ID único del alquiler que se desea finalizar.

        Returns
        -------
        bool
            True si el alquiler se finalizó correctamente.

        Raises
        ------
        ValueError
            Si no se pueden cargar los datos, si el alquiler no existe, 
            si ya está finalizado o si ocurre un error al guardar los cambios.
        Exception
            Si ocurre un error inesperado durante el proceso.

        Notes
        -----
        - El método utiliza los archivos CSV como fuente de datos, por lo que los cambios son persistentes.
        - El coche asociado al alquiler se marca automáticamente como disponible.
        """
        # Cargar la base de datos de alquileres y coches
        df_alquiler = self.cargar_alquileres()
        df_coches = self.cargar_coches()

        # Validaciones
        if df_alquiler is None or df_alquiler.empty:
            raise ValueError('No se pudo cargar el archivo de alquileres o está vacío.')
        if df_coches is None or df_coches.empty:
            raise ValueError('No se han podido cargar los coches o está vacío.')

        alquiler = df_alquiler[df_alquiler['id_alquiler'] == id_alquiler]
        if alquiler.empty:
            raise ValueError(f'No existe ningún alquiler con el ID: {id_alquiler}')

        if not alquiler.iloc[0]['activo']:
            raise ValueError(f'El alquiler con ID {id_alquiler} ya está finalizado.')

        id_coche = alquiler.iloc[0]['id_coche']

        # Actualizar el estado del alquiler y del coche
        df_alquiler.loc[df_alquiler['id_alquiler'] == id_alquiler, 'activo'] = False
        df_coches.loc[df_coches['id'] == id_coche, 'disponible'] = True

        # Guardar los cambios usando el método auxiliar
        try:
            self._guardar_csv('alquileres.csv', df_alquiler)
            self._guardar_csv('coches.csv', df_coches)
            return True
        except Exception as e:
            raise ValueError(f"Error al guardar los cambios en los archivos CSV: {e}")
        
        
    # -------------------------------
    # Métodos de Sesión e Historial
    # -------------------------------
    
    
    def iniciar_sesion(self, email: str, contraseña: str) -> bool:
        """
        Verifica si un usuario con el correo electrónico y contraseña dados existe en la base de datos.

        Parameters
        ----------
        email : str
            Correo electrónico del usuario.
        contraseña : str
            Contraseña proporcionada por el usuario.

        Returns
        -------
        bool
            True si las credenciales son válidas, False en caso contrario.

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
        df_usuarios = self.cargar_usuarios()
        if df_usuarios is None or df_usuarios.empty:
            raise ValueError("No se pudieron cargar los usuarios. Revisa el archivo CSV.")

        # Buscar el usuario por correo electrónico
        usuario = df_usuarios[df_usuarios['email'] == email]
        if usuario.empty:
            raise ValueError(f"No se encontró ningún usuario con el correo: {email}.")

        # Obtener la contraseña almacenada y compararla con la contraseña hasheada
        contraseña_almacenada = usuario.iloc[0]['contraseña']
        contraseña_hasheada = self.hash_contraseña(contraseña)

        if contraseña_almacenada != contraseña_hasheada:
            raise ValueError("Contraseña incorrecta.")

        return True
        
        
    def obtener_historial_alquileres(self, id_usuario: str) -> list[dict]:
        """
        Obtiene el historial de alquileres de un usuario específico.

        Parameters
        ----------
        id_usuario : str
            ID único del usuario cuyo historial de alquileres se desea obtener.

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
        # Cargar los alquileres
        df_alquileres = self.cargar_alquileres()
        if df_alquileres is None or df_alquileres.empty:
            raise ValueError("No hay alquileres registrados.")

        # Filtrar los alquileres por el ID del usuario
        alquileres_usuario = df_alquileres[df_alquileres['id_usuario'] == id_usuario]

        # Si no hay alquileres, lanzar una excepción
        if alquileres_usuario.empty:
            raise ValueError(f"No se encontraron alquileres para el usuario con ID {id_usuario}.")

        # Convertir el DataFrame a una lista de diccionarios
        return alquileres_usuario.to_dict(orient='records')

    
    # -------------------------------
    # Métodos de Cálculo
    # -------------------------------
    
    
    def calcular_precio_total(
        self,
        fecha_inicio: datetime,
        fecha_fin: datetime,
        matricula: str,
        email: str = None
    ) -> float:
        """
        Calcula el precio total del alquiler de un coche en función de las fechas, la matrícula 
        y el correo electrónico del usuario (opcional).

        Este método calcula el costo total del alquiler considerando el rango de días, 
        el precio diario del coche y un descuento basado en el tipo de usuario (si se proporciona un correo).

        Parameters
        ----------
        fecha_inicio : datetime
            Fecha de inicio del alquiler.
        fecha_fin : datetime
            Fecha de fin del alquiler.
        matricula : str
            Matrícula del coche que se desea alquilar.
        email : str, optional
            Correo electrónico del usuario que realiza el alquiler. Si no se proporciona, 
            se asume un tipo de usuario "normal" sin descuento.

        Returns
        -------
        float
            El precio total del alquiler en euros.

        Raises
        ------
        ValueError
            Si ocurre algún error durante la validación de datos o el cálculo del precio.
        Exception
            Si ocurre un error inesperado durante el proceso.

        Notes
        -----
        - El descuento aplicado depende del tipo de usuario:
            - 'cliente': 6% de descuento (factor = 0.94).
            - 'normal': Sin descuento (factor = 1).
        - El coche debe estar disponible para poder calcular el precio.
        """
        # Cargar los archivos CSV
        df_coches = self.cargar_coches()
        if df_coches is None:
            raise ValueError("Error al cargar el archivo de coches.")

        df_clientes = self.cargar_usuarios()
        if df_clientes is None:
            raise ValueError("Error al cargar el archivo de usuarios.")

        # Validar que la fecha de inicio sea anterior a la fecha de fin
        if fecha_inicio > fecha_fin:
            raise ValueError("La fecha de inicio no puede ser mayor a la fecha final.")

        # Validar el correo electrónico si se proporciona
        if email and not self.es_email_valido(email):
            raise ValueError("El correo electrónico no es válido.")

        # Buscar el coche por matrícula
        coche = df_coches[df_coches['matricula'] == matricula]
        if coche.empty:
            raise ValueError(f"No se encontró ningún coche con la matrícula: {matricula}.")
        coche = coche.iloc[0]

        # Verificar disponibilidad del coche
        if not coche['disponible']:
            raise ValueError(f"El coche con matrícula {matricula} no está disponible para alquilar.")

        # Calcular el rango de días
        rango_de_dias = (fecha_fin - fecha_inicio).days

        # Definir descuentos según el tipo de usuario
        descuentos = {
            'cliente': 0.94,  # 6% de descuento
            'normal': 1       # Sin descuento
        }

        # Determinar el tipo de usuario
        tipo_usuario = 'normal'
        if email:
            user = df_clientes[df_clientes['email'] == email]
            if user.empty:
                raise ValueError("Usuario no encontrado.")
            tipo_usuario = user.iloc[0]['tipo']

        # Obtener el factor de descuento
        descuento = descuentos.get(tipo_usuario, 1)

        # Calcular el precio total
        precio_total = coche['precio_diario'] * rango_de_dias * descuento

        return precio_total 
        
     
    # -------------------------------
    # Métodos de Búsqueda/Filtrado
    # -------------------------------    
    
    
    def mostrar_categorias_tipo(self) -> list:
        """
        Muestra las categorías de tipo de los coches disponibles en el sistema.

        Este método carga los datos de los coches desde el archivo CSV y devuelve una lista 
        de las categorías de tipo únicas disponibles.

        Returns
        -------
        list
            Una lista de las categorías de tipo únicas de los coches.

        Raises
        ------
        ValueError
            Si no se pueden cargar los datos o si no hay coches disponibles.

        Notes
        -----
        - Las categorías de tipo son únicas y se extraen del campo 'categoria_tipo' del DataFrame.
        """
        # Cargar los datos de los coches
        df_coches = self.cargar_coches()

        # Validar que el DataFrame no esté vacío
        if df_coches is None or df_coches.empty:
            raise ValueError('No hay datos disponibles para mostrar categorías.')

        # Obtener las categorías de tipo únicas
        categorias_tipo = df_coches['categoria_tipo'].unique()

        return list(categorias_tipo)
            
            
    def mostrar_categorias_precio(self) -> list:
        """
        Muestra las categorías de precio de los coches disponibles en el sistema.

        Este método carga los datos de los coches desde el archivo CSV y devuelve una lista 
        de las categorías de precio únicas disponibles.

        Returns
        -------
        list
            Una lista de las categorías de precio únicas de los coches.

        Raises
        ------
        ValueError
            Si no se pueden cargar los datos o si no hay coches disponibles.

        Notes
        -----
        - Las categorías de precio son únicas y se extraen del campo 'categoria_precio' del DataFrame.
        """
        # Cargar los datos de los coches
        df_coches = self.cargar_coches()

        # Validar que el DataFrame no esté vacío
        if df_coches is None or df_coches.empty:
            raise ValueError('No hay datos disponibles para mostrar categorías.')

        # Obtener las categorías de precio únicas
        categorias_precio = df_coches['categoria_precio'].unique()

        return list(categorias_precio)
            
            
    def cargar_coches_disponibles(self) -> pd.DataFrame:
        """
        Carga los coches disponibles desde el archivo CSV.

        Este método carga los datos de los coches desde el archivo CSV y filtra solo 
        aquellos que están marcados como disponibles.

        Returns
        -------
        pd.DataFrame
            Un DataFrame que contiene los coches disponibles.

        Raises
        ------
        ValueError
            Si no hay coches disponibles o si el archivo CSV no se pudo cargar.

        Notes
        -----
        - Los coches disponibles son aquellos donde el campo 'disponible' es True.
        - El método utiliza el archivo CSV como fuente de datos, por lo que los cambios son persistentes.
        """
        df = self.cargar_coches()
        if df is None or df.empty:
            raise ValueError("No hay coches disponibles o el archivo no se pudo cargar.")
        return df[df['disponible'] == True]  # Filtrar solo coches disponibles
    
    
    def obtener_categorias_precio(self) -> list:
        """
        Devuelve una lista de categorías de precio disponibles.

        Este método carga los coches disponibles y extrae las categorías de precio únicas.

        Returns
        -------
        list
            Una lista de las categorías de precio únicas disponibles.

        Raises
        ------
        ValueError
            Si no hay coches disponibles o si el archivo CSV no se pudo cargar.

        Notes
        -----
        - Las categorías de precio son únicas y se extraen del campo 'categoria_precio' del DataFrame.
        """
        df = self.cargar_coches_disponibles()
        return df['categoria_precio'].unique().tolist()

    
    def filtrar_por_categoria_precio(self, categoria_precio: str) -> pd.DataFrame:
        """
        Filtra coches disponibles por categoría de precio.

        Este método carga los coches disponibles y filtra aquellos que pertenecen 
        a la categoría de precio especificada.

        Parameters
        ----------
        categoria_precio : str
            La categoría de precio por la cual se desea filtrar los coches.

        Returns
        -------
        pd.DataFrame
            Un DataFrame que contiene los coches filtrados por la categoría de precio.

        Raises
        ------
        ValueError
            Si la categoría de precio seleccionada no es válida o si no hay coches disponibles.

        Notes
        -----
        - La categoría de precio debe ser una de las categorías disponibles en el sistema.
        - El método utiliza el archivo CSV como fuente de datos, por lo que los cambios son persistentes.
        """
        df = self.cargar_coches_disponibles()
        if categoria_precio not in df['categoria_precio'].unique():
            raise ValueError("La categoría de precio seleccionada no es válida.")
        return df[df['categoria_precio'] == categoria_precio]

    
    def obtener_categorias_tipo(self, categoria_precio: str) -> list:
        """
        Devuelve una lista de categorías de tipo disponibles para una categoría de precio.

        Este método filtra los coches disponibles por la categoría de precio especificada 
        y devuelve una lista de las categorías de tipo únicas dentro de esa categoría de precio.

        Parameters
        ----------
        categoria_precio : str
            La categoría de precio por la cual se desea filtrar los coches.

        Returns
        -------
        list
            Una lista de las categorías de tipo únicas disponibles para la categoría de precio especificada.

        Raises
        ------
        ValueError
            Si la categoría de precio seleccionada no es válida o si no hay coches disponibles.

        Notes
        -----
        - Las categorías de tipo son únicas y se extraen del campo 'categoria_tipo' del DataFrame filtrado.
        """
        df_filtrado = self.filtrar_por_categoria_precio(categoria_precio)
        return df_filtrado['categoria_tipo'].unique().tolist()

    
    def filtrar_por_categoria_tipo(self, categoria_precio: str, categoria_tipo: str) -> pd.DataFrame:
        """
        Filtra coches disponibles por categoría de tipo dentro de una categoría de precio.

        Este método filtra los coches disponibles primero por la categoría de precio y luego 
        por la categoría de tipo especificada.

        Parameters
        ----------
        categoria_precio : str
            La categoría de precio por la cual se desea filtrar los coches.
        categoria_tipo : str
            La categoría de tipo por la cual se desea filtrar los coches.

        Returns
        -------
        pd.DataFrame
            Un DataFrame que contiene los coches filtrados por la categoría de tipo dentro de la categoría de precio.

        Raises
        ------
        ValueError
            Si la categoría de precio o la categoría de tipo seleccionadas no son válidas.

        Notes
        -----
        - La categoría de tipo debe ser una de las categorías disponibles dentro de la categoría de precio especificada.
        """
        df_filtrado = self.filtrar_por_categoria_precio(categoria_precio)
        if categoria_tipo not in df_filtrado['categoria_tipo'].unique():
            raise ValueError("La categoría de tipo seleccionada no es válida.")
        return df_filtrado[df_filtrado['categoria_tipo'] == categoria_tipo]

    
    def obtener_marcas(self, categoria_precio: str, categoria_tipo: str) -> list:
        """
        Devuelve una lista de marcas disponibles para una categoría de precio y tipo.

        Este método filtra los coches disponibles por la categoría de precio y tipo especificadas, 
        y devuelve una lista de las marcas únicas dentro de esa combinación de categorías.

        Parameters
        ----------
        categoria_precio : str
            La categoría de precio por la cual se desea filtrar los coches.
        categoria_tipo : str
            La categoría de tipo por la cual se desea filtrar los coches.

        Returns
        -------
        list
            Una lista de las marcas únicas disponibles para la categoría de precio y tipo especificadas.

        Raises
        ------
        ValueError
            Si la categoría de precio o la categoría de tipo seleccionadas no son válidas.

        Notes
        -----
        - Las marcas son únicas y se extraen del campo 'marca' del DataFrame filtrado.
        """
        df_filtrado = self.filtrar_por_categoria_tipo(categoria_precio, categoria_tipo)
        return df_filtrado['marca'].unique().tolist()


    def filtrar_por_marca(self, categoria_precio: str, categoria_tipo: str, marca: str) -> pd.DataFrame:
        """
        Filtra coches disponibles por marca dentro de una categoría de precio y tipo.

        Este método filtra los coches disponibles primero por la categoría de precio y tipo, 
        y luego por la marca especificada.

        Parameters
        ----------
        categoria_precio : str
            La categoría de precio por la cual se desea filtrar los coches.
        categoria_tipo : str
            La categoría de tipo por la cual se desea filtrar los coches.
        marca : str
            La marca por la cual se desea filtrar los coches.

        Returns
        -------
        pd.DataFrame
            Un DataFrame que contiene los coches filtrados por la marca dentro de la categoría de precio y tipo.

        Raises
        ------
        ValueError
            Si la categoría de precio, la categoría de tipo o la marca seleccionadas no son válidas.

        Notes
        -----
        - La marca debe ser una de las marcas disponibles dentro de la combinación de categoría de precio y tipo especificadas.
        """
        df_filtrado = self.filtrar_por_categoria_tipo(categoria_precio, categoria_tipo)
        if marca not in df_filtrado['marca'].unique():
            raise ValueError("La marca seleccionada no es válida.")
        return df_filtrado[df_filtrado['marca'] == marca]


    def obtener_modelos(self, categoria_precio: str, categoria_tipo: str, marca: str) -> list:
        """
        Devuelve una lista de modelos disponibles para una marca, categoría de precio y tipo.

        Este método filtra los coches disponibles por la categoría de precio, tipo y marca especificadas, 
        y devuelve una lista de los modelos únicos dentro de esa combinación de categorías.

        Parameters
        ----------
        categoria_precio : str
            La categoría de precio por la cual se desea filtrar los coches.
        categoria_tipo : str
            La categoría de tipo por la cual se desea filtrar los coches.
        marca : str
            La marca por la cual se desea filtrar los coches.

        Returns
        -------
        list
            Una lista de los modelos únicos disponibles para la combinación de categoría de precio, tipo y marca.

        Raises
        ------
        ValueError
            Si la categoría de precio, la categoría de tipo o la marca seleccionadas no son válidas.

        Notes
        -----
        - Los modelos son únicos y se extraen del campo 'modelo' del DataFrame filtrado.
        """
        df_filtrado = self.filtrar_por_marca(categoria_precio, categoria_tipo, marca)
        return df_filtrado['modelo'].unique().tolist()


    def filtrar_por_modelo(
        self, categoria_precio: str, categoria_tipo: str, marca: str, modelo: str
    ) -> pd.DataFrame:
        """
        Filtra coches disponibles por modelo dentro de una marca, categoría de precio y tipo.

        Este método filtra los coches disponibles primero por la categoría de precio, tipo y marca, 
        y luego por el modelo especificado.

        Parameters
        ----------
        categoria_precio : str
            La categoría de precio por la cual se desea filtrar los coches.
        categoria_tipo : str
            La categoría de tipo por la cual se desea filtrar los coches.
        marca : str
            La marca por la cual se desea filtrar los coches.
        modelo : str
            El modelo por el cual se desea filtrar los coches.

        Returns
        -------
        pd.DataFrame
            Un DataFrame que contiene los coches filtrados por el modelo dentro de la combinación de categoría de precio, tipo y marca.

        Raises
        ------
        ValueError
            Si la categoría de precio, la categoría de tipo, la marca o el modelo seleccionados no son válidos.

        Notes
        -----
        - El modelo debe ser uno de los modelos disponibles dentro de la combinación de categoría de precio, tipo y marca especificadas.
        """
        df_filtrado = self.filtrar_por_marca(categoria_precio, categoria_tipo, marca)
        if modelo not in df_filtrado['modelo'].unique():
            raise ValueError("El modelo seleccionado no está disponible.")
        return df_filtrado[df_filtrado['modelo'] == modelo]


    def obtener_detalles_coches(
        self,
        categoria_precio: str,
        categoria_tipo: str,
        marca: str,
        modelo: str
    ) -> list[dict]:
        """
        Devuelve los detalles de los coches filtrados por modelo.

        Este método filtra los coches disponibles por la combinación de categoría de precio, 
        categoría de tipo, marca y modelo, y devuelve una lista de diccionarios con los detalles 
        de cada coche que cumple con los criterios.

        Parameters
        ----------
        categoria_precio : str
            La categoría de precio por la cual se desea filtrar los coches.
        categoria_tipo : str
            La categoría de tipo por la cual se desea filtrar los coches.
        marca : str
            La marca por la cual se desea filtrar los coches.
        modelo : str
            El modelo por el cual se desea filtrar los coches.

        Returns
        -------
        list[dict]
            Una lista de diccionarios que contienen los detalles de los coches filtrados. 
            Cada diccionario incluye las siguientes claves:
            - matricula (str)
            - marca (str)
            - modelo (str)
            - categoria_precio (str)
            - categoria_tipo (str)
            - disponible (bool)
            - año (int)
            - precio_diario (float)
            - kilometraje (float)
            - color (str)
            - combustible (str)
            - cv (int)
            - plazas (int)

        Raises
        ------
        ValueError
            Si la categoría de precio, la categoría de tipo, la marca o el modelo seleccionados no son válidos.

        Notes
        -----
        - Los detalles de los coches se extraen del DataFrame filtrado y se formatean como una lista de diccionarios.
        """
        df_filtrado = self.filtrar_por_modelo(categoria_precio, categoria_tipo, marca, modelo)
        detalles = []
        for _, coche in df_filtrado.iterrows():
            detalles.append({
                "matricula": coche['matricula'],
                "marca": coche['marca'],
                "modelo": coche['modelo'],
                "categoria_precio": coche['categoria_precio'],
                "categoria_tipo": coche['categoria_tipo'],
                "disponible": coche['disponible'],
                "año": coche['año'],
                "precio_diario": coche['precio_diario'],
                "kilometraje": coche['kilometraje'],
                "color": coche['color'],
                "combustible": coche['combustible'],
                "cv": coche['cv'],
                "plazas": coche['plazas']
            })
        return detalles
    
        
    # -------------------------------
    # Métodos de Generación de Informes
    # ------------------------------- 


    def generar_factura_pdf(self, alquiler: dict) -> bytes:
        """
        Genera una factura en formato PDF para un alquiler específico.

        Este método crea un archivo PDF que contiene los detalles del alquiler, 
        incluyendo información del coche, fechas de alquiler y el costo total. 
        El PDF se devuelve como bytes para su posterior uso o almacenamiento.

        Parameters
        ----------
        alquiler : dict
            Un diccionario que contiene los detalles del alquiler. Debe incluir las siguientes claves:
            - id_alquiler (str): ID único del alquiler.
            - marca (str): Marca del coche.
            - modelo (str): Modelo del coche.
            - matricula (str): Matrícula del coche.
            - fecha_inicio (str): Fecha de inicio del alquiler en formato 'YYYY-MM-DD'.
            - fecha_fin (str): Fecha de fin del alquiler en formato 'YYYY-MM-DD'.
            - coste_total (float): Costo total del alquiler.

        Returns
        -------
        bytes
            Los bytes del archivo PDF generado.

        Raises
        ------
        ValueError
            Si falta algún dato obligatorio en el diccionario `alquiler`.
        Exception
            Si ocurre un error inesperado durante la generación del PDF.

        Notes
        -----
        - El logo del archivo 'Logo.png' es opcional. Si no se encuentra, se omitirá sin interrumpir la generación del PDF.
        - El PDF se genera en memoria y se devuelve como bytes para evitar escribir archivos en el servidor.
        """
        # Crear una instancia de FPDF
        pdf = FPDF()

        # Añadir página
        pdf.add_page()

        # Intentar cargar el logo
        try:
            logo_path = 'Logo.png'  # Ruta relativa al logo
            if os.path.exists(logo_path):
                pdf.image(logo_path, x=10, y=10, w=50)
        except Exception as e:
            raise Exception(f"Error al cargar el logo: {e}")

        # Título
        pdf.set_font("Arial", "B", 16)
        pdf.set_text_color(0, 0, 0)  # Negro
        pdf.cell(0, 20, txt="Factura de Alquiler", ln=True, align="C")

        # Restaurar color de texto
        pdf.set_text_color(0, 0, 0)

        # Espacio adicional antes de la fecha de emisión
        pdf.ln(10)  # Bajar el texto de la fecha de emisión
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, txt=f"Fecha de Emisión: {datetime.now().strftime('%Y-%m-%d')}", ln=True, align="C")

        # Tabla con detalles del alquiler
        pdf.set_fill_color(240, 240, 240)  # Gris claro para el encabezado

        # Calcular la posición inicial para centrar la tabla
        ancho_tabla = 150  # Ancho total de la tabla (50 + 100)
        posicion_x = (pdf.w - ancho_tabla) / 2  # Centrar horizontalmente

        # Encabezado de la tabla
        pdf.set_x(posicion_x)  # Establecer la posición X
        pdf.cell(50, 10, "Campo", border=1, fill=True)
        pdf.cell(100, 10, "Valor", border=1, fill=True, ln=True)

        # Datos de la tabla
        for campo, valor in [
            ("ID de Alquiler", alquiler['id_alquiler']),
            ("Marca", alquiler['marca']),
            ("Modelo", alquiler['modelo']),
            ("Matrícula", alquiler['matricula']),
            ("Fecha de Inicio", alquiler['fecha_inicio']),
            ("Fecha de Fin", alquiler['fecha_fin'])
        ]:
            pdf.set_x(posicion_x)  # Centrar cada fila
            pdf.cell(50, 10, campo, border=1)
            pdf.cell(100, 10, str(valor), border=1, ln=True)

        pdf.ln(10)

        # Precio total con formato destacado
        pdf.set_font("Arial", "B", 14)
        pdf.set_text_color(255, 0, 0)  # Rojo para el precio
        precio_formateado = f"{alquiler['coste_total']:.2f} EUR"
        pdf.cell(0, 10, txt=f"Precio Total: {precio_formateado}", ln=True, align="R")

        # Mensaje de agradecimiento
        pdf.set_font("Arial", "I", 12)
        pdf.set_text_color(0, 0, 0)  # Negro
        pdf.cell(0, 10, txt="Gracias por elegirnos. ¡Esperamos verte pronto!", ln=True, align="C")

        # Devolver el PDF como bytes
        return pdf.output(dest='S').encode('latin1')