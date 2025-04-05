
# Clase Empresa que va a gestionar todo el alquiler de coches 
import pandas as pd
import datetime

class Empresa():
    def __init__(self,nombre):
        self.nombre = nombre
        self.coches = []
        self.usuarios = []
        self.alquileres = []
    
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
            
    
    def registrar_usuario(self, id_usuario, nombre, email, tipo):
        # crea un objeto Usuario y añadirlo a self.usuarios (sobrecarga de operador??)
        pass
    
    def dar_baja_usuario(self, id_usuario):
        # busca un usuaro en self.usuarios y eliminarlo ( usar sobrecarga de operador??)
        pass
    
    def alquilar_coche(self,id_usuario, marca, fecha_inicio, fecha_fin):
        '''buscar el coche por marca en self.coches, si esta disponible, llamar al metodo
        alquilar y crear un Alquiler con el coche, usuario y fechas
        calcular el coste total (dias * precio por dia), y añadirlo a self.alquileres'''
        pass
        
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

    
    def mostrar_precios(self):
        '''devolver una lista/diccionario con la marca y el precio por dia de sus coches
        en funcion de su categoria '''
        pass
        
a = Empresa('RentACar')

a.buscar_coches_disponibles()
