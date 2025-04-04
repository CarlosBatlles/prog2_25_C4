
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
     
    def cargar_coches(self,ruta_archivo):
        ''' Carga los coches desde un archivo CSV'''
        try:
            self.coches = pd.read_csv('C:\Users\Alexis Angulo Polan\Documents\GitHub\prog2-25-C4\data\coches.csv')
        except FileNotFoundError:
            print(f'El archivo {ruta_archivo} no se encontró')
        except Exception as e:
            print(f'Error al cargar coches {e}')
    
    def cargar_usuarios(self,ruta_archivo):
        try:
            self.usuarios = pd.read_csv('C:\Users\Alexis Angulo Polan\Documents\GitHub\prog2-25-C4\data\clientes.csv')
        except FileNotFoundError:
            print(f'El archivo {ruta_archivo} no se encontró')
        except Exception as e:
            print(f'Error al cargar usuarios {e}')
            
    def cargar_alquileres(self,ruta_archivo):
        try:
            self.alquileres = pd.read_csv('C:\Users\Alexis Angulo Polan\Documents\GitHub\prog2-25-C4\data\alquileres.csv')
        except FileNotFoundError:
            print(f'El archivo {ruta_archivo} no se encontro')
        except Exception as e:
            print(f'Error al cargar alquileres {e}')
            
    # Metodos para generar IDs de usuario y coche automaticamente  
    
    def generar_id_usuario(self):
        '''Genera un ID unico para un nuevo usuario'''
        df = self.cargar_usuarios
        if df.empty:
            return 'U001'
        ultimo_id = df['id_usuario'].iloc[-1]
        num = int(ultimo_id[1:]) + 1 # Extraer el número y sumar 1
        return f'U{num:03d}' # Formato U001, U002, etc.
    
    def generar_id_alquiler(self):
        df = self.cargar_alquileres
        if df.empty:
            return 'A001'
        ultimo_id = df['id_alquiler'].iloc[-1]
        num = int(ultimo_id[1:]) + 1
        return f'A{num:03d}'
    
    def generar_id_coche(self):
        df = self.cargar_coches
        ultimo_id = df['id'].iloc[-1]
        num = int(ultimo_id[1:]) + 1
        return f'UID{num:02d}'
        
    
    def registrar_coche(self,marca, categoria, nivel, precio_dia):
        # crear objeto Coche y añadirlo a self.coches
        pass
    
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
    
    def mostrar_coches_disponibles(self, marca=None, categoria=None):
        '''mostrar una lista de los coches disponibles, devulver una lista de coches donde 
        disponible sea True para que se muestre en esta lista'''
        pass
    
    def mostrar_precios(self):
        '''devolver una lista/diccionario con la marca y el precio por dia de sus coches
        en funcion de su categoria '''
        pass
        