
'''Clase Coche para representar los coches disponibles para alquilar y sus características'''

class Coche():
    
    def __init__(self, marca: str, categoria: str, nivel: str, precio_dia: float, disponible: bool = True):
        self.marca = marca
        self.categoria = categoria
        self.nivel = nivel
        self.precio_dia = precio_dia
        self.disponible = disponible
        
    def alquilar(self):
        '''cambia disponible a false y devuelve true si se pudo alquilar, false si no'''
        pass
    
    def devolver(self):
        '''cambia disponible a true'''
        pass
    
    def get_info(self):
        '''devuelve un str con los detalles del coche, para mostrar en coches disponibles'''
        pass
    