
'''Clase Alquiler para representar y gestionar un alquiler de coche'''

import datetime

class Alquiler():
    
    def __init__(self, id_alquiler, id_coche, id_usuario, fecha_inicio, fecha_fin, coste_total, activo = True):
        # Validar que fecha_inicio sea menor que fecha_fin
        if fecha_inicio >= fecha_fin:
            raise ValueError("La fecha de inicio debe ser anterior a la fecha de fin")
        
        self.id_alquiler = id_alquiler
        self.id_coche = id_coche
        self.id_usuario = id_usuario
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.coste_total = coste_total
        self.activo = activo
        
    def finalizar(self):
        ''' Marca el alquiler como no activo'''
        self.activo = False
    
    def get_info(self):
        '''Devuelve detalles del alquiler '''
        return (f"Alquiler ID: {self.id_alquiler}\n"
                f"Coche: {self.id_coche}\n"
                f"Usuario: {self.id_usuario}\n"
                f"Fechas: {self.fecha_inicio} - {self.fecha_fin}\n"
                f"Coste: {self.coste_total} EUR\n"
                f"Activo: {self.activo}")
                    