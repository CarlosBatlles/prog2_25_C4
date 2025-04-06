
# Clase Empresa que va a gestionar todo el alquiler de coches 
import pandas as pd
from datetime import datetime
import re
from fpdf import FPDF

class Empresa():
    def __init__(self,nombre):
        self.nombre = nombre
        self.coches = []
        self.usuarios = []
        self.alquileres = []
        
    # METODOS PARA VALIDAR
    
    @staticmethod
    def es_email_valido(email):
        patron = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(patron, email) is not None
    
     # Metodos para cargar las bases de datos
     
    def cargar_coches(self):
        ''' Carga los coches desde un archivo CSV'''
        try:
            df = pd.read_csv('coches.csv')
            return df 
        except FileNotFoundError:
            print(f'El archivo no se encontró')
        except Exception as e:
            print(f'Error al cargar coches {e}')
    
    def cargar_usuarios(self):
        try:
            df = pd.read_csv('clientes.csv')
            return df 
        except FileNotFoundError:
            print(f'El archivo no se encontró')
        except Exception as e:
            print(f'Error al cargar usuarios {e}')
            
    def cargar_alquileres(self):
        try:
            df = pd.read_csv('alquileres.csv')
            return df 
        except FileNotFoundError:
            print(f'El archivo no se encontro')
        except Exception as e:
            print(f'Error al cargar alquileres {e}')
            
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
        
        try:
            df_actualizado.to_csv('coches.csv',index=False)
            print(f'El coche con el ID {id_coche} ha sido registrado exitosamente')
        except Exception as e:
            print(f'Error al guardar el coche en el archivo CSV: {e}')
            
    
    def registrar_usuario(self,nombre,tipo,email,contraseña_hasheada):
        
        df_usuarios = self.cargar_usuarios()
        if df_usuarios is None:
            print("No se pudieron cargar los usuarios. Verifica el archivo CSV.")
            return
        
        # Verificaciones 
        if not nombre or not tipo or not email or not contraseña_hasheada:
            raise ValueError('Debes rellenar todos los campos')
        
        if not self.es_email_valido(email):
            raise ValueError("El correo electrónico no es válido.")
        
        if email in df_usuarios['email'].values:
            print("El correo electrónico ya está registrado.")
            return False
        
        id_user = self.generar_id_usuario()
        
        new_user = {
            'id_usuario': id_user,
            'nombre': nombre,
            'tipo': tipo,
            'email': email,
            'contraseña': contraseña_hasheada,
        }
        
        df_nuevo_usuario = pd.DataFrame([new_user])
        df_actualizado = pd.concat([df_usuarios,df_nuevo_usuario], ignore_index=True)
        
        try:
            df_actualizado.to_csv('clientes.csv',index=False)
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
        
        try:
            df_actualizado.to_csv('clientes.csv',index = True)   
            print(f'El usuario con email {email} ha sido eliminado exitosamente') 
            return True
        except Exception as e:
            print(f'Error al guardar los cambios en el archivo CSV: {e}')
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
        
        # Guardar los cambios en los archivos CSV
        try:
            df_coches.to_csv('coches.csv', index=False)
            df_actualizado.to_csv('alquileres.csv', index=False)
            print("Alquiler registrado exitosamente.")
        except Exception as e:
            print(f"Error al guardar los cambios: {e}")
            
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
        '''Busca el alquiler en self.alquileres, llama a devolver() del coche
        y elimina o marca el alquiler como terminado.'''
        pass
    
    def buscar_coches_disponibles(self):
        '''mostrar una lista de los coches disponibles, devulver una lista de coches donde 
        disponible sea True para que se muestre en esta lista'''
        df = self.cargar_coches()
        if df is None or df.empty:
            print("No hay coches disponibles o el archivo no se pudo cargar.")
            return
        
        # Paso 1: Mostrar categorías de precio disponibles
        categorias_precio = df['categoria_precio'].unique()
        print("Categorías de precio disponibles:")
        for categoria in categorias_precio:
            print(f"- {categoria}")

        # Pedir al usuario que seleccione una categoría de precio
        opcion_precio = input("\nIntroduce la categoría de precio por la que quieres buscar: ").capitalize()
        if opcion_precio not in categorias_precio:
            print("La categoría de precio seleccionada no es válida.")
            return

        # Filtrar coches por la categoría de precio seleccionada
        df_filtrado_precios = df[df['categoria_precio'] == opcion_precio]

        # Paso 2: Mostrar categorías de tipo disponibles
        categorias_tipos = df_filtrado_precios['categoria_tipo'].unique()
        print("\nCategorías de tipo disponibles:")
        for categoria in categorias_tipos:
            print(f"- {categoria}")

        # Pedir al usuario que seleccione una categoría de tipo
        opcion_tipo = input("\nIntroduce la categoría de tipo por la que quieres buscar: ").capitalize()
        if opcion_tipo not in categorias_tipos:
            print("La categoría de tipo seleccionada no es válida.")
            return

        # Filtrar coches por la categoría de tipo seleccionada
        df_filtrado_tipos = df_filtrado_precios[df_filtrado_precios['categoria_tipo'] == opcion_tipo]

        # Paso 3: Mostrar marcas disponibles
        marcas = df_filtrado_tipos['marca'].unique()
        print("\nMarcas disponibles:")
        for marca in marcas:
            print(f"- {marca}")
            
        opcion_marca = input('\nIntroduce la marca por la que quieres buscar: ').capitalize()
        if opcion_marca not in marcas:
            print('La marca seleccionada no es válida')
            return
        
        # filtrar coches por la marca seleccionada
        df_filtrado_marcas = df_filtrado_tipos[df_filtrado_tipos['marca'] == opcion_marca]
        
        # paso 4 mostrar modelos disponibles
        modelos = df_filtrado_marcas['modelo'].unique()
        print(f'\nCoches de {opcion_marca} dispomibles: ')
        for modelo in modelos:
            cantidad = len(df_filtrado_marcas[df_filtrado_marcas['modelo'] == modelo])
            print(f'- {modelo} ({cantidad} coche(s) disponible(s))')
            
        opcion_modelo = input('\nIntroduce el modelo que quieres: ').capitalize()
        if opcion_modelo not in modelos:
            print(f'El modelo {opcion_modelo} no esta disponible')
            return
        
        df_filtrado_modelos = df_filtrado_marcas[df_filtrado_marcas['modelo'] == opcion_modelo]
        
        print(f"\nInformación de los coches del modelo '{opcion_modelo}':")
        for _, coche in df_filtrado_modelos.iterrows():
            print("-" * 50)
            print(f"Matrícula: {coche['matricula']}")
            print(f"Marca: {coche['marca']}")
            print(f"Modelo: {coche['modelo']}")
            print(f"Categoría de Precio: {coche['categoria_precio']}")
            print(f"Categoría de Tipo: {coche['categoria_tipo']}")
            print(f"Disponible: {'Sí' if coche['disponible'] else 'No'}")
            print(f"Año: {coche['año']}")
            print(f"Precio Diario: {coche['precio_diario']}€")
            print(f"Kilometraje: {coche['kilometraje']} km")
            print(f"Color: {coche['color']}")
            print(f"Combustible: {coche['combustible']}")
            print(f"CV: {coche['cv']}")
            print(f"Plazas: {coche['plazas']}")

    
    # Metodo para generar una factura en pdf
    def generar_factura_pdf(self, alquiler):
        pdf = FPDF()

        # Añadir página
        pdf.add_page()

        # Añadir logo
        pdf.image('Logo.png', x=10, y=10, w=50)

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
            pdf.cell(100, 10, valor, border=1, ln=True)

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

        # Guardar el archivo PDF
        nombre_archivo = f"factura_{alquiler['id_alquiler']}.pdf"
        pdf.output(nombre_archivo)
        print(f"Factura generada exitosamente: {nombre_archivo}")
        
    
    def mostrar_precios(self):
        '''devolver una lista/diccionario con la marca y el precio por dia de sus coches
        en funcion de su categoria '''
        pass
        
a = Empresa('RentACar')

#a.registrar_usuario("Juan Perez", "cliente", "jperez@example.com", "contraseña_segura")
a.alquilar_coche('9676 LRX','2023-10-01','2023-10-05',"jperez@example.com")
