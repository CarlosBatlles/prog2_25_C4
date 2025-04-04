
'''Clase Alquiler para representar y gestionar un alquiler de coche'''
import datetime

class Alquiler:
    def __init__(self, id_alquiler, id_coche, id_usuario, fecha_inicio, fecha_fin, tarifa_diaria, activo=True):
        # Validar que fecha_inicio sea menor que fecha_fin
        if fecha_inicio >= fecha_fin:
            raise ValueError("Error: La fecha de inicio debe ser anterior a la fecha de fin.")
        
        self.id_alquiler = id_alquiler
        self.id_coche = id_coche
        self.id_usuario = id_usuario
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.tarifa_diaria = tarifa_diaria
        self.activo = activo
        
        # Calcular el coste total automáticamente
        self.calcular_coste()

    def calcular_coste(self):
        """Calcula el coste total del alquiler en función de la duración y la tarifa diaria."""
        dias = (self.fecha_fin - self.fecha_inicio).days
        self.coste_total = dias * self.tarifa_diaria

    def finalizar(self):
        """Marca el alquiler como no activo."""
        self.activo = False

    def get_info(self):
        """Devuelve detalles del alquiler."""
        return (f"Alquiler ID: {self.id_alquiler}\n"
                f"Coche: {self.id_coche}\n"
                f"Usuario: {self.id_usuario}\n"
                f"Fechas: {self.fecha_inicio} - {self.fecha_fin}\n"
                f"Coste: {self.coste_total} EUR\n"
                f"Activo: {self.activo}")

    def __str__(self):
        """Representación legible del alquiler."""
        return self.get_info()