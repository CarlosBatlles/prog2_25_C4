
# Clase Empresa que va a gestionar todo el alquiler de coches 
import pandas as pd
from datetime import datetime
import re
from fpdf import FPDF
import hashlib
import os

class Empresa():
    def __init__(self,nombre):
        self.nombre = nombre
        self.coches = []
        self.usuarios = []
        self.alquileres = []
        self.data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')

    def _ruta_archivo(self, archivo):
        """
        Construye la ruta completa al archivo CSV en la carpeta 'data'.
        """
        return os.path.join(self.data_dir, archivo)

    def _cargar_csv(self, archivo):
        """
        Carga un archivo CSV desde la carpeta 'data'.
        """
        ruta = self._ruta_archivo(archivo)
        try:
            return pd.read_csv(ruta)
        except FileNotFoundError:
            print(f"El archivo {ruta} no se encontró.")
            return None
        except Exception as e:
            print(f"Error al cargar el archivo {ruta}: {e}")
            return None

    def _guardar_csv(self, archivo, df):
        """
        Guarda un DataFrame en un archivo CSV en la carpeta 'data'.
        """
        ruta = self._ruta_archivo(archivo)
        try:
            df.to_csv(ruta, index=False)
            print(f"Archivo guardado exitosamente.")
        except Exception as e:
            print(f"Error al guardar el archivo {ruta}: {e}")
        
    # METODOS PARA VALIDAR
    
    @staticmethod
    def es_email_valido(email):
        patron = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(patron, email) is not None

    def hash_contraseña(self,contraseña):
        """
        Genera un hash SHA-256 de la contraseña proporcionada.
        """
        return hashlib.sha256(contraseña.encode()).hexdigest()
    
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
    
    def actualizar_matricula(self, id_coche, nueva_matricula):

        # Cargar los coches actuales
        df_coches = self.cargar_coches()
        if df_coches is None:
            raise ValueError("No se pudieron cargar los coches. Revisa el archivo CSV.")

        # Verificar si el ID existe en el DataFrame
        if id_coche not in df_coches['id'].values:
            raise ValueError(f"El coche con matricula {id_coche} no está registrado.")
        
        # Verificar si la nueva matrícula ya existe
        if nueva_matricula in df_coches['matricula'].values:
            raise ValueError(f"La matrícula {nueva_matricula} ya está registrada en otro coche.")

        # Actualizar la matricula en el DataFrame
        df_coches.loc[df_coches['id'] == id_coche, 'matricula'] = nueva_matricula

        # Guardar los cambios en el archivo CSV
        try:
            self._guardar_csv("coches.csv", df_coches)
            print(f"La matricula del coche con ID {id_coche} ha sido actualizada exitosamente.")
        except Exception as e:
            raise ValueError(f"Error al guardar los cambios en el archivo CSV: {e}")

        return True
    
    def eliminar_coche(self, id_coche, matricula):
        '''
        Elimina un coche del sistema basándose en su id y matricula.
        '''
        # Cargar los usuarios actuales
        df_coches = self.cargar_coches()
        if df_coches is None:
            raise ValueError("No se pudieron cargar los coches. Revisa el archivo CSV.")

        # Verificar si el ID existe en el DataFrame
        if id_coche not in df_coches['id'].values:
            raise ValueError(f"El coche con matricula {id_coche} no está registrado.")

        # Filtrar el DataFrame para excluir al coche con el id proporcionado
        df_actualizado = df_coches[df_coches['id'] != id_coche]
        
        # Guardar los cambios usando el método auxiliar
        try:
            self._guardar_csv('coches.csv', df_actualizado)
            print(f'El coche con matricula {matricula} ha sido eliminado exitosamente')
            return True
        except Exception as e:
            raise ValueError(f"Error al guardar los cambios en el archivo CSV: {e}")
    
    # Metodos para cargar las bases de datos
    def cargar_coches(self):
        ''' Carga los coches desde un archivo CSV'''
        return self._cargar_csv('coches.csv')

    def cargar_usuarios(self):
        ''' Carga los usuarios desde un archivo CSV'''
        return self._cargar_csv('clientes.csv')

    def cargar_alquileres(self):
        ''' Carga los alquileres desde un archivo CSV'''
        return self._cargar_csv('alquileres.csv')
            
    # Metodos para generar IDs de usuario y coche automaticamente  
    
    def generar_id_usuario(self):
        '''Genera un ID unico para un nuevo usuario'''
        df = self.cargar_usuarios()
        if df.empty:
            return 'U001'
        ultimo_id = df['id_usuario'].iloc[-1]
        num = int(ultimo_id[1:]) + 1 # Extraer el número y sumar 1
        return f'U{num:03d}' # Formato U001, U002, etc.
    
    def generar_id_alquiler(self):
        df = self.cargar_alquileres()
        if df.empty:
            return 'A001'
        ultimo_id = df['id_alquiler'].iloc[-1]
        num = int(ultimo_id[1:]) + 1
        return f'A{num:03d}'
    
    def generar_id_coche(self):
        df = self.cargar_coches()
        ultimo_id = df['id'].iloc[-1]
        num = int(ultimo_id[1:]) + 1
        return f'UID{num:02d}'
        
    # METODOS PARA REGISTRAR
    
    def registrar_coche(self,marca,modelo,matricula,categoria_tipo,categoria_precio,año,precio_diario,kilometraje,color,combustible,cv,plazas,disponible):
        ''' Añade un nuevo coche al sistema '''
        
        # Comprobaciones
        if not marca or not modelo or not matricula or not categoria_tipo or not categoria_precio:
            raise ValueError("Todos los campos de texto (marca, modelo, matricula, categoria_tipo, categoria_precio) deben tener un valor.")

        if precio_diario <= 0:
            raise ValueError('El precio diario debe ser mayor que 0')
        if kilometraje < 0:
            raise ValueError('El kilometraje no puede ser negativo')
        if cv <= 0:
            raise  ValueError('La potencia del coche debe ser mayor que 0')
        if plazas < 2:
            raise ValueError('Las plazas del coche deben ser mayores a 2')
        if not isinstance(disponible, bool):
            raise TypeError("El campo 'disponible' debe ser True o False")
        
        df_coches = self.cargar_coches()
        if df_coches is None:
            print("No se pudieron cargar los coches. Verifica el archivo CSV.")
            return
        
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
        
        df_nuevo_coche = pd.DataFrame([nuevo_coche])
        df_actualizado = pd.concat([df_coches,df_nuevo_coche], ignore_index=True)
        
        # Guardar los cambios usando el método auxiliar
        try:
            self._guardar_csv('coches.csv', df_actualizado)
            print(f'El coche con el ID {id_coche} ha sido registrado exitosamente')
            return True
        except Exception as e:
            print(f'Error al guardar el coche en el archivo CSV: {e}')
            return False
            
    
    def registrar_usuario(self,nombre,tipo,email,contraseña):
        
        df_usuarios = self.cargar_usuarios()
        if df_usuarios is None:
            print("No se pudieron cargar los usuarios. Verifica el archivo CSV.")
            return False
        
        # Verificaciones 
        if not nombre or not tipo or not email or not contraseña:
            raise ValueError('Debes rellenar todos los campos')
        
        if not self.es_email_valido(email):
            raise ValueError("El correo electrónico no es válido.")
        
        if email in df_usuarios['email'].values:
            print("El correo electrónico ya está registrado.")
            return False
        
        id_user = self.generar_id_usuario()
        
        contraseña_hasheada = self.hash_contraseña(contraseña)
        
        new_user = {
            'id_usuario': id_user,
            'nombre': nombre,
            'tipo': tipo,
            'email': email,
            'contraseña': contraseña_hasheada,
        }
        
        df_nuevo_usuario = pd.DataFrame([new_user])
        df_actualizado = pd.concat([df_usuarios,df_nuevo_usuario], ignore_index=True)
        
        # Guardar los cambios usando el método auxiliar
        try:
            self._guardar_csv('clientes.csv', df_actualizado)
            print(f'El usuario con el ID {id_user} ha sido registrado exitosamente')
            return True
        except Exception as e:
            print(f'Error al guardar el usuario en el archivo CSV: {e}')
            return False
    
    def dar_baja_usuario(self, email):
        '''
        Elimina un usuario del sistema basándose en su correo electrónico.
        '''
        # Cargar los usuarios actuales
        df_usuarios = self.cargar_usuarios()
        if df_usuarios is None:
            print('No se pudieron cargar los usuarios. Revisa el archivo CSV.')
            return False

        # Verificar si el email existe en el DataFrame
        if email not in df_usuarios['email'].values:
            print('El correo que has introducido no está registrado.')
            return False

        # Filtrar el DataFrame para excluir al usuario con el email proporcionado
        df_actualizado = df_usuarios[df_usuarios['email'] != email]
        
        # Guardar los cambios usando el método auxiliar
        try:
            self._guardar_csv('clientes.csv', df_actualizado)
            print(f'El usuario con email {email} ha sido eliminado exitosamente')
            return True
        except Exception as e:
            print(f'Error al guardar los cambios en el archivo CSV: {e}')
            return False
        
    def iniciar_sesion(self, email, contraseña):
        """
        Verifica si un usuario con el correo electrónico y contraseña dados existe en la base de datos.
        Devuelve True si las credenciales son válidas, False en caso contrario.
        """
        df_usuarios = self.cargar_usuarios()
        if df_usuarios is None or df_usuarios.empty:
            print(f'No se pudieron cargar los usuarios. Revisa el archivo CSV')
            return False
        
        usuario = df_usuarios[df_usuarios['email'] == email]
        if usuario.empty: 
            print(f'No se encontró ningun usuario con el correo: {email}')
            return False
        
        contraseña_almacenada = usuario.iloc[0]['contraseña']
        
        contraseña_hasheada = self.hash_contraseña(contraseña)
        
        if contraseña_almacenada == contraseña_hasheada:
            print(f"Bienvenido {usuario.iloc[0]['nombre']}")
            return True
        else:
            print('Contraseña incorrecta')
            return False
        
        
    def alquilar_coche(self,matricula, fecha_inicio:datetime, fecha_fin:datetime,email=None):
        
        # Cargar los archivos CSV
        df_coches = self.cargar_coches()
        if df_coches is None:
            raise ValueError("Error al cargar el archivo de coches.")

        df_clientes = self.cargar_usuarios()
        if df_clientes is None:
            raise ValueError("Error al cargar el archivo de usuarios.")
        
        df_alquiler = self.cargar_alquileres()
        if df_alquiler is None:
            raise ValueError('Error al cargar el archivo de alquileres')
        
        coche = df_coches[df_coches['matricula'] == matricula]
        if coche.empty:
            raise ValueError(f"No se encontró ningún coche con la matrícula: {matricula}.")
        coche = coche.iloc[0]
        
        if email and not self.es_email_valido(email):
            raise ValueError("El correo electrónico no es válido.")
        
        # Convertir las fechas a objetos datetime
        try:
            fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
            fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Las fechas deben estar en formato YYYY-MM-DD.")

        # Validar que la fecha de inicio sea anterior a la fecha de fin
        if fecha_inicio >= fecha_fin:
            raise ValueError("La fecha de inicio debe ser anterior a la fecha de fin.")
        
        # Verificar disponibilidad
        if not coche['disponible']:
            raise ValueError(f"El coche {coche['marca']} - {coche['modelo']} no está disponible para alquilar.")
        else:
            print(f'El {coche["marca"]}-{coche["modelo"]} está disponible. Procesando alquiler...')
        
        precio_total = self.calcular_precio_total(fecha_inicio,fecha_fin,matricula,email)
        df_coches.loc[df_coches['matricula'] == matricula, 'disponible'] = False
        
        id_usuario = 'INVITADO'
        if email:
            user = df_clientes[df_clientes['email'] == email]
            if user.empty:
                raise ValueError(f'No se encontro ningun usuario con el email: {email}')
            id_usuario = user.iloc[0]['id_usuario']    
            
        nuevo_alquiler = {
            'id_alquiler' : self.generar_id_alquiler(),
            'id_coche': coche['id'],
            'id_usuario': id_usuario,
            'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d'),  # Convertir a formato de cadena
            'fecha_fin': fecha_fin.strftime('%Y-%m-%d'),
            'coste_total': precio_total,
            'activo': True
        }
        
        df_nuevo_alquiler = pd.DataFrame([nuevo_alquiler])
        df_actualizado = pd.concat([df_alquiler,df_nuevo_alquiler], ignore_index = True)
        
        # Guardar los cambios usando métodos auxiliares
        try:
            self._guardar_csv('coches.csv', df_coches)
            self._guardar_csv('alquileres.csv', df_actualizado)
            print("Alquiler registrado exitosamente.")
        except Exception as e:
            print(f"Error al guardar los cambios: {e}")
            return
            
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
        self.generar_factura_pdf(datos_factura)

    
    def calcular_precio_total(self,fecha_inicio:datetime, fecha_fin:datetime, matricula, email= None):
        
        # Cargar los archivos CSV
        df_coches = self.cargar_coches()
        if df_coches is None:
            raise ValueError("Error al cargar el archivo de coches.")

        df_clientes = self.cargar_usuarios()
        if df_clientes is None:
            raise ValueError("Error al cargar el archivo de usuarios.")
        
        if fecha_inicio > fecha_fin:
            raise ValueError('La fecha de inicio no puede ser mayor a la fecha final')
        
        if email and not self.es_email_valido(email):
            raise ValueError("El correo electrónico no es válido.")
        
        coche = df_coches[df_coches['matricula'] == matricula]
        if coche.empty:
            raise ValueError(f"No se encontró ningún coche con la matrícula: {matricula}.")
        coche = coche.iloc[0]
        
        if not coche['disponible']:
            raise ValueError(f'El coche con matricula {matricula} no esta disponible para alquilar')
        
        # Calcular el rango de dias
        rango_de_dias = (fecha_fin - fecha_inicio).days
        
        descuentos = {
            'cliente': 0.94,
            'normal': 1
        }
        
        tipo_usuario = 'normal'
        if email:
            user = df_clientes[df_clientes['email'] == email]
            if user.empty:
                raise ValueError("Usuario no encontrado.")
            tipo_usuario = user.iloc[0]['tipo']
            
        descuento = descuentos.get(tipo_usuario,1)
        precio_total = coche['precio_diario'] * rango_de_dias * descuento
        
        return precio_total    
        
    def finalizar_alquiler(self, id_alquiler):
        
        # Cargar la base de datos de alquileres
        df_alquiler = self.cargar_alquileres()
        df_coches = self.cargar_coches()
        
        # Validaciones
        if df_alquiler is None or df_alquiler.empty:
            raise ValueError('No se pudo cargar el archivo de alquileres o está vacío.')
        if df_coches is None or df_coches.empty:
            raise ValueError('No se han podido cargar los coches o esta vacio')
        
        alquiler = df_alquiler[df_alquiler['id_alquiler'] == id_alquiler]
        if alquiler.empty:
            raise ValueError(f'No existe ningun alquiler con el ID: {id_alquiler}')
        
        if not alquiler.iloc[0]['activo']:
            raise ValueError(f'El alquiler con ID {id_alquiler} ya está finalizado')
        
        id_coche = alquiler.iloc[0]['id_coche']
        
        df_alquiler.loc[df_alquiler['id_alquiler'] == id_alquiler, 'activo'] = False
        df_coches.loc[df_coches['id'] == id_coche, 'disponible'] = True
        
        # Guardar los cambios usando el método auxiliar
        try:
            self._guardar_csv('alquileres.csv', df_alquiler)
            self._guardar_csv('coches.csv', df_coches)
            print(f"Alquiler con ID {id_alquiler} finalizado exitosamente.")
            print(f"El coche con ID {id_coche} ha sido marcado como disponible.")
        except Exception as e:
            raise ValueError(f"Error al guardar los cambios en los archivos CSV: {e}")
        
        
    def cargar_coches_disponibles(self):
        """Carga los coches disponibles desde el archivo CSV."""
        df = self.cargar_coches()
        if df is None or df.empty:
            raise ValueError("No hay coches disponibles o el archivo no se pudo cargar.")
        return df[df['disponible'] == True]  # Filtrar solo coches disponibles

    def obtener_categorias_precio(self):
        """Devuelve una lista de categorías de precio disponibles."""
        df = self.cargar_coches_disponibles()
        return df['categoria_precio'].unique().tolist()

    def filtrar_por_categoria_precio(self, categoria_precio):
        """Filtra coches disponibles por categoría de precio."""
        df = self.cargar_coches_disponibles()
        if categoria_precio not in df['categoria_precio'].unique():
            raise ValueError("La categoría de precio seleccionada no es válida.")
        return df[df['categoria_precio'] == categoria_precio]

    def obtener_categorias_tipo(self, categoria_precio):
        """Devuelve una lista de categorías de tipo disponibles para una categoría de precio."""
        df_filtrado = self.filtrar_por_categoria_precio(categoria_precio)
        return df_filtrado['categoria_tipo'].unique().tolist()

    def filtrar_por_categoria_tipo(self, categoria_precio, categoria_tipo):
        """Filtra coches disponibles por categoría de tipo dentro de una categoría de precio."""
        df_filtrado = self.filtrar_por_categoria_precio(categoria_precio)
        if categoria_tipo not in df_filtrado['categoria_tipo'].unique():
            raise ValueError("La categoría de tipo seleccionada no es válida.")
        return df_filtrado[df_filtrado['categoria_tipo'] == categoria_tipo]

    def obtener_marcas(self, categoria_precio, categoria_tipo):
        """Devuelve una lista de marcas disponibles para una categoría de precio y tipo."""
        df_filtrado = self.filtrar_por_categoria_tipo(categoria_precio, categoria_tipo)
        return df_filtrado['marca'].unique().tolist()

    def filtrar_por_marca(self, categoria_precio, categoria_tipo, marca):
        """Filtra coches disponibles por marca dentro de una categoría de precio y tipo."""
        df_filtrado = self.filtrar_por_categoria_tipo(categoria_precio, categoria_tipo)
        if marca not in df_filtrado['marca'].unique():
            raise ValueError("La marca seleccionada no es válida.")
        return df_filtrado[df_filtrado['marca'] == marca]

    def obtener_modelos(self, categoria_precio, categoria_tipo, marca):
        """Devuelve una lista de modelos disponibles para una marca, categoría de precio y tipo."""
        df_filtrado = self.filtrar_por_marca(categoria_precio, categoria_tipo, marca)
        return df_filtrado['modelo'].unique().tolist()

    def filtrar_por_modelo(self, categoria_precio, categoria_tipo, marca, modelo):
        """Filtra coches disponibles por modelo dentro de una marca, categoría de precio y tipo."""
        df_filtrado = self.filtrar_por_marca(categoria_precio, categoria_tipo, marca)
        if modelo not in df_filtrado['modelo'].unique():
            raise ValueError("El modelo seleccionado no está disponible.")
        return df_filtrado[df_filtrado['modelo'] == modelo]

    def obtener_detalles_coches(self, categoria_precio, categoria_tipo, marca, modelo):
        """Devuelve los detalles de los coches filtrados por modelo."""
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
    
        
    # Metodo para generar una factura en pdf
    def generar_factura_pdf(self, alquiler):
        pdf = FPDF()

        # Añadir página
        pdf.add_page()

        # Añadir logo
        try:
            logo_path = self._ruta_archivo('Logo.png')  # Usar el método auxiliar para construir la ruta
            if os.path.exists(logo_path):
                pdf.image(logo_path, x=10, y=10, w=50)
            else:
                print(f"El archivo Logo.png no se encontró en {logo_path}. Se omitirá el logo.")
        except Exception as e:
            print(f"Error al cargar el logo: {e}")

        # Título
        pdf.set_font("Arial", "B", 16)
        pdf.set_text_color(0, 0, 0)  # Azul oscuro
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

        # Guardar el archivo PDF en la carpeta 'data'
        nombre_archivo = f"factura_{alquiler['id_alquiler']}.pdf"
        ruta_factura = self._ruta_archivo(nombre_archivo)  # Construir la ruta completa
        try:
            pdf.output(ruta_factura)
            print(f"Factura generada exitosamente: {ruta_factura}")
        except Exception as e:
            print(f"Error al guardar la factura: {e}")
        
    
    def mostrar_categorias_tipo(self):
        
        df_coches = self.cargar_coches()
        
        # Validar que el DataFrame no esté vacío
        if df_coches is None or df_coches.empty:
            raise ValueError('No hay datos disponibles para mostrar categorías')
        
        categorias_tipo = df_coches['categoria_tipo'].unique()
        print("-- Categorías de tipo disponibles --")
        for categoria in categorias_tipo:
            print(f"- {categoria}")
            
    def mostrar_categorias_precio(self):
        
        df_coches = self.cargar_coches()
        
        # Validar que el DataFrame no esté vacío
        if df_coches is None or df_coches.empty:
            raise ValueError('No hay datos disponibles para mostrar categorías')
        
        categorias_precio = df_coches['categoria_precio'].unique()
        print("-- Categorías de precio disponibles --")
        for categoria in categorias_precio:
            print(f"- {categoria}")
            

a = Empresa('RentACar')

#a.registrar_usuario("Riki", "cliente", "jperez@example.com", "contraseña_segura")
#a.alquilar_coche('4195 SSY','2023-10-01','2023-10-05',"riki@example.com")
#a.finalizar_alquiler('A001')
#a.dar_baja_usuario('riki@example.com')
#a.buscar_coches_disponibles()