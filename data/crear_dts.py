import pandas as pd
import numpy as np
from faker import Faker

'''# Configuración
np.random.seed(1935)
fake = Faker('es_ES')
num_coches = 90  # Entre 80-100 filas

# Marcas y modelos con formato correcto
marcas_modelos = {
    # Marcas estándar
    'Audi': ['A3', 'A4', 'A5', 'A6', 'Q3', 'Q5', 'Q7', 'R8'],
    'BMW': ['Serie 1', 'Serie 3', 'Serie 5', 'X1', 'X3', 'X5', 'M3', 'M5'],
    'Mercedes': ['Clase A', 'Clase C', 'Clase S', 'GLA', 'GLC', 'GLE', 'AMG GT'],
    'Volkswagen': ['Golf', 'Passat', 'Tiguan', 'Polo', 'Arteon', 'T-Roc'],
    'Seat': ['Leon', 'Ibiza', 'Arona', 'Ateca', 'Tarraco'],
    'Renault': ['Clio', 'Megane', 'Kadjar', 'Captur', 'Zoe'],
    'Peugeot': ['208', '308', '3008', '5008', 'RCZ'],
    'Ford': ['Fiesta', 'Focus', 'Kuga', 'Mustang', 'Puma'],
    'Toyota': ['Corolla', 'RAV4', 'Yaris', 'Prius', 'C-HR'],
    'Hyundai': ['i30', 'Tucson', 'Kona', 'Ioniq', 'Santa Fe'],
    
    # Marcas de lujo
    'Porsche': ['911', 'Taycan', 'Cayenne', 'Panamera', 'Macan'],
    'Ferrari': ['488 GTB', 'F8 Tributo', 'Roma', 'SF90 Stradale', 'Portofino'],
    'Lamborghini': ['Huracán', 'Aventador', 'Urus'],
    'Bentley': ['Continental GT', 'Bentayga', 'Flying Spur'],
    'McLaren': ['720S', '570S', 'GT', 'Artura'],
    'Aston Martin': ['DB11', 'Vantage', 'DBS Superleggera', 'Valhalla'],
    'Rolls Royce': ['Phantom', 'Ghost', 'Wraith', 'Dawn'],
    'Maserati': ['Ghibli', 'Quattroporte', 'Levante', 'MC20']
}

categorias_tipo = ['Familiar', 'Deportivo', 'SUV', 'Sedán', 'Hatchback', 'Superdeportivo', 'Luxury']
categorias_precio = ['Premium', 'Medio', 'Básico', 'Lujo']
colores = ['Blanco', 'Negro', 'Gris', 'Rojo', 'Azul', 'Plateado', 'Verde', 'Amarillo', 'Naranja']

# Rangos de CV por categoría
cv_rangos = {
    'Familiar': (90, 150),
    'Sedán': (110, 250),
    'Hatchback': (75, 180),
    'SUV': (120, 400),
    'Deportivo': (200, 500),
    'Superdeportivo': (500, 1000),
    'Luxury': (300, 600)
}

# Generar datos
datos = []
for i in range(1, num_coches + 1):
    marca = np.random.choice(list(marcas_modelos.keys()))
    modelo = np.random.choice(marcas_modelos[marca])
    
    # Determinar categorías según la marca
    if marca in ['Ferrari', 'Lamborghini', 'McLaren', 'Aston Martin', 'Rolls Royce']:
        categoria_tipo = 'Superdeportivo' if marca != 'Rolls Royce' else 'Luxury'
        categoria_precio = 'Lujo'
    elif marca in ['Porsche', 'Bentley', 'Maserati']:
        categoria_tipo = np.random.choice(['Deportivo', 'SUV', 'Luxury'])
        categoria_precio = 'Lujo' if marca in ['Bentley'] else 'Premium'
    elif marca in ['Audi', 'BMW', 'Mercedes']:
        categoria_tipo = np.random.choice(categorias_tipo[:5])
        categoria_precio = 'Premium'
    else:
        categoria_tipo = np.random.choice(categorias_tipo[:5])
        categoria_precio = np.random.choice(['Medio', 'Básico'], p=[0.7, 0.3])
    
    # Precio diario (€/día)
    if categoria_precio == 'Lujo':
        precio_diario = np.random.randint(500, 2000)
    elif categoria_precio == 'Premium':
        precio_diario = np.random.randint(150, 500)
    elif categoria_precio == 'Medio':
        precio_diario = np.random.randint(60, 150)
    else:
        precio_diario = np.random.randint(30, 60)
    
    # Combustible (sin eléctricos en Lujo)
    if categoria_precio == 'Lujo':
        combustible = np.random.choice(['Gasolina', 'Diésel'], p=[0.9, 0.1])
    elif categoria_precio == 'Premium':
        combustible = np.random.choice(['Gasolina', 'Diésel', 'Híbrido'], p=[0.6, 0.3, 0.1])
    else:
        combustible = np.random.choice(['Gasolina', 'Diésel', 'Híbrido', 'Eléctrico'], p=[0.5, 0.3, 0.15, 0.05])
    
    # Generar matrícula española moderna (0000 XXX)
    letras = ''.join([chr(np.random.randint(66, 91)) for _ in range(3)])  # Letras B-Z (sin vocales)
    numeros = f"{np.random.randint(0, 10000):04d}"
    matricula = f"{numeros} {letras}"
    
    # Asignar CV según categoría
    min_cv, max_cv = cv_rangos[categoria_tipo]
    cv = np.random.randint(min_cv, max_cv + 1)
    if combustible == 'Eléctrico':
        cv = int(cv * 1.3)
    
    datos.append({
        'id': f"UID{i}",
        'marca': marca,
        'modelo': modelo,
        'matricula': matricula,
        'categoria_tipo': categoria_tipo,
        'categoria_precio': categoria_precio,
        'año': np.random.randint(2018, 2024),
        'precio_diario': precio_diario,
        'kilometraje': np.random.randint(0, 50000),
        'color': np.random.choice(colores),
        'combustible': combustible,
        'cv': cv,
        'plazas': np.random.randint(2, 8) if categoria_tipo not in ['Superdeportivo'] else 2,
        'disponible': True
    })

# Crear DataFrame
df_coches = pd.DataFrame(datos)

# Ordenar por categoría de precio
df_coches = df_coches.sort_values(by='categoria_precio', ascending=False)


# Guardar en CSV
df_coches.to_csv('data/coches.csv', index=False, encoding='utf-8-sig')'''

'''# BASE DE DATOS DE USUARIOS

# Definir las columnas del DataFrame de usuarios
columnas_usuarios = ["id_usuario", "nombre", "email", "tipo"]

# Crear un DataFrame vacío con las columnas
clientes_df = pd.DataFrame(columns=columnas_usuarios)

# Guardar el DataFrame en data/clientes.csv
clientes_df.to_csv("data/clientes.csv", index=False)'''


'''# BASE DE DATOS DE ALQUILER 
# Definir las columnas del DataFrame de alquileres
columnas_alquileres = ["id_alquiler", "id_coche", "id_usuario", "fecha_inicio", "fecha_fin", "coste_total", "activo"]

# Crear un DataFrame vacío con las columnas
alquileres_df = pd.DataFrame(columns=columnas_alquileres)


# Guardar el DataFrame en data/alquileres.csv
alquileres_df.to_csv("data/alquileres.csv", index=False)
'''

'''import pandas as pd

# Cargar el archivo CSV
df = pd.read_csv('coches.csv')

# Reemplazar 'Sedán' por 'Sedan' en la columna 'categoria_tipo'
df['marca'] = df['marca'].replace({'BMW': 'Bmw'})

# Guardar los cambios en el archivo CSV
df.to_csv('coches.csv', index=False)

print("El archivo CSV ha sido actualizado correctamente.")

import pandas as pd'''

# BASE DE DATOS DE USUARIOS

# Definir las columnas del DataFrame de usuarios (incluyendo "contraseña")
columnas_usuarios = ["id_usuario", "nombre", "tipo", "email", "contraseña"]

# Crear un DataFrame vacío con las columnas
clientes_df = pd.DataFrame(columns=columnas_usuarios)

# Guardar el DataFrame en data/clientes.csv
clientes_df.to_csv("data/clientes.csv", index=False)

print("Archivo 'clientes.csv' creado con éxito, incluyendo la columna 'contraseña'.")