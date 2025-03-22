
# Clase Empresa que va a gestionar todo el alquiler de coches 

import datetime

class Empresa():
    def __init__(self,nombre):
        self.nombre = nombre
        self.coches = []
        self.usuarios = []
        self.alquileres = []
    
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
        