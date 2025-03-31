
'''Clase Coche para representar los coches disponibles para alquilar y sus características'''

class Coche:
    def __init__(self, id_coche, marca, modelo, matricula, categoria_tipo, categoria_precio, año, precio_diario, kilometraje, color, combustible, cv, plazas, disponible):
        self.id_coche = id_coche
        self.marca = marca
        self.modelo = modelo
        self.matricula = matricula
        self.categoria_tipo = categoria_tipo
        self.categoria_precio = categoria_precio
        self.año = año
        self.precio_diario = precio_diario
        self.kilometraje = kilometraje
        self.color = color
        self.combustible = combustible
        self.cv = cv
        self.plazas = plazas
        self.disponible = disponible
        
    def alquilar(self):
        ''' Marca el coche como no disponible'''
        if not self.disponible:
            raise ValueError(f"El coche {self.id_coche} ({self.marca} {self.modelo}) no esta disponible")
        self.disponible = False
        return True
        
    
    def devolver(self):
        ''' Marca el coche como disponible'''
        if self.disponible:
            raise ValueError(f"El coche {self.id_coche} ({self.marca} {self.modelo}) ya se encuentra disponible")
        self.disponible = False
    
    
    def get_info(self):
        '''Devuelve un string con los detalles del coche en un formato legible'''
        return (f"Coche ID: {self.id_coche}\n"
                f"Marca: {self.marca}\n"
                f"Modelo: {self.modelo}\n"
                f"Matrícula: {self.matricula}\n"
                f"Categoría Tipo: {self.categoria_tipo}\n"
                f"Categoría Precio: {self.categoria_precio}\n"
                f"Año: {self.año}\n"
                f"Precio por día: {self.precio_diario} EUR\n"
                f"Kilometraje: {self.kilometraje} km\n"
                f"Color: {self.color}\n"
                f"Combustible: {self.combustible}\n"
                f"Potencia: {self.cv} CV\n"
                f"Plazas: {self.plazas}\n"
                f"Disponible: {self.disponible}")
    