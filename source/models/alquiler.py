
'''Clase Alquiler para representar y gestionar un alquiler de coche'''
import datetime
import pandas as pd 
from fpdf import FPDF
import os


class Alquiler:
    def __init__(self,id_alquiler: str,id_coche: str,id_usuario: str,
                fecha_inicio: str,fecha_fin: str,coste_total: float,
                activo: bool = True):
        
        # Validar que fecha_inicio sea menor que fecha_fin
        if fecha_inicio >= fecha_fin:
            raise ValueError("Error: La fecha de inicio debe ser anterior a la fecha de fin.")
        
        """
        Inicializa un nuevo objeto de tipo Alquiler.

        Parameters
        ----------
        id_alquiler : str
            ID único del alquiler.
        id_coche : str
            ID del coche asociado al alquiler.
        id_usuario : str
            ID del usuario que realiza el alquiler (o 'INVITADO').
        fecha_inicio : str
            Fecha de inicio del alquiler en formato 'YYYY-MM-DD'.
        fecha_fin : str
            Fecha de fin del alquiler en formato 'YYYY-MM-DD'.
        coste_total : float
            Costo total del alquiler.
        activo : bool, optional
            Estado del alquiler (True si está activo, False si ha finalizado).
        """
        self.id_alquiler = id_alquiler
        self.id_coche = id_coche
        self.id_usuario = id_usuario
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.coste_total = coste_total
        self.activo = activo
        
        
    @staticmethod
    def alquilar_coche(empresa, matricula: str, fecha_inicio: str, fecha_fin: str, 
                        email: str = None) -> bytes:
        """
        Registra un nuevo alquiler de coche en el sistema.

        Este método verifica la disponibilidad del coche, calcula el precio total del alquiler, 
        actualiza el estado del coche y guarda el alquiler en el archivo CSV correspondiente. 
        También genera una factura en formato PDF.

        Parameters
        ----------
        empresa : Empresa
            Instancia de la clase Empresa para cargar/guardar datos.
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
        df_coches = empresa.cargar_coches()
        if df_coches is None:
            raise ValueError("Error al cargar el archivo de coches.")

        df_clientes = empresa.cargar_usuarios()
        if df_clientes is None:
            raise ValueError("Error al cargar el archivo de usuarios.")

        df_alquiler = empresa.cargar_alquileres()
        if df_alquiler is None:
            raise ValueError("Error al cargar el archivo de alquileres.")

        # Verificar si existe un coche con la matrícula proporcionada
        coche = df_coches[df_coches['matricula'] == matricula]
        if coche.empty:
            raise ValueError(f"No se encontró ningún coche con la matrícula: {matricula}.")
        coche = coche.iloc[0]

        # Validar el correo electrónico si se proporciona
        if email and not empresa.es_email_valido(email):
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
        precio_total = empresa.calcular_precio_total(fecha_inicio_dt, fecha_fin_dt, matricula, email)

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
            'id_alquiler': empresa.generar_id_alquiler(),
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
            empresa._guardar_csv('coches.csv', df_coches)
            empresa._guardar_csv('alquileres.csv', df_actualizado)
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
            pdf_bytes = empresa.generar_factura_pdf(datos_factura)
            return pdf_bytes
        except Exception as e:
            raise ValueError(f"Error al generar la factura en PDF: {e}")
        
    
    @staticmethod
    def finalizar_alquiler(empresa, id_alquiler: str) -> bool:
        """
        Finaliza un alquiler existente y marca el coche como disponible.

        Este método verifica si el alquiler con el ID proporcionado existe y está activo. 
        Si es así, finaliza el alquiler y actualiza el estado del coche correspondiente 
        en los archivos CSV.

        Parameters
        ----------
        empresa : Empresa
            Instancia de la clase Empresa para cargar/guardar datos.
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
        df_alquiler = empresa.cargar_alquileres()
        df_coches = empresa.cargar_coches()

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
            empresa._guardar_csv('alquileres.csv', df_alquiler)
            empresa._guardar_csv('coches.csv', df_coches)
            return True
        except Exception as e:
            raise ValueError(f"Error al guardar los cambios en los archivos CSV: {e}")
        
        
    @staticmethod
    def calcular_precio_total(
        empresa,
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
        empresa : Empresa
            Instancia de la clase Empresa para cargar los datos.
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
        df_coches = empresa.cargar_coches()
        if df_coches is None:
            raise ValueError("Error al cargar el archivo de coches.")

        df_clientes = empresa.cargar_usuarios()
        if df_clientes is None:
            raise ValueError("Error al cargar el archivo de usuarios.")

        # Validar que la fecha de inicio sea anterior a la fecha de fin
        if fecha_inicio > fecha_fin:
            raise ValueError("La fecha de inicio no puede ser mayor a la fecha final.")

        # Validar el correo electrónico si se proporciona
        if email and not empresa.es_email_valido(email):
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
    
    
    
    @staticmethod
    def generar_factura_pdf(alquiler: dict) -> bytes:
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