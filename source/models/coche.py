
'''Clase Coche para representar los coches disponibles para alquilar y sus características'''

class Coche:
    
    CATEGORIAS_TIPO = ['Familiar', 'Deportivo', 'SUV', 'Sedán', 'Hatchback', 'Superdeportivo', 'Luxury']
    CATEGORIAS_PRECIO = ['Premium', 'Medio', 'Básico', 'Lujo']
    COMBUSTIBLES_PERMITIDOS = ['Gasolina', 'Diésel', 'Híbrido', 'Eléctrico']
    
    def __init__(self, coche_id, marca, modelo, matricula, categoria_tipo, categoria_precio, año, precio_diario, kilometraje, color, combustible, cv, plazas, disponible):
        # Validamos algunos parametros
        if precio_diario <= 0:
            raise ValueError('El precio diario debe ser mayor que cero')
        if kilometraje < 0: 
            raise ValueError('El kilometraje no puede ser negativo')
        if plazas <= 0:
            raise ValueError('El numero de plazas debe ser mayor que cero')
        if categoria_tipo not in self.CATEGORIAS_TIPO:
            raise ValueError(f'Categoria tipo: {categoria_tipo} no está disponible')
        if categoria_precio not in self.CATEGORIAS_PRECIO:
            raise ValueError(f'Categoria precio: {categoria_precio} no está disponible')
        if combustible not in self.COMBUSTIBLES_PERMITIDOS:
            raise ValueError(f'El combustible: {combustible} no está disponible')
        
        self.coche_id = coche_id
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
        self.disponible = True
    
    def actualizar_kilometraje(self, nuevos_km):
        '''Actualiza los km del coche'''
        if nuevos_km < self.kilometraje:
            raise ValueError('Los nuevos kilómetros no pueden ser menores a los antiguos')
        self.kilometraje = nuevos_km
    
    def get_info(self):
        '''Devuelve un string con los detalles del coche en un formato legible'''
        return (f"Coche ID: {self.coche_id}\n"
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
        
    def __str__(self):
        ''' Representacion legible del coche'''
        return self.get_info()
    