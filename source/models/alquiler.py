
'''Clase Alquiler para representar y gestionar un alquiler de coche'''

import datetime
from .coche import Coche  # Importar la clase Coche
from .usuario import Usuario  # Importar la clase Usuario

class Alquiler():
    
    def __init__(self, id_alquiler: str, coche: Coche, usuario: Usuario, fecha_inicio: datetime.datetime, fecha_fin: datetime.datetime, coste_total: float, activo: bool = True):
        # Validar que fecha_inicio sea menor que fecha_fin
        self.id_alquiler = id_alquiler
        self.coche = coche
        self.usuario = usuario
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.coste_total = coste_total
        self.activo = activo
        
    def finalizar(self):
        # cambia activo a false
        pass
    
    def get_info(self):
        # mostrar la informacion del alquiler
        pass