# RentACar

Este proyecto es una aplicación Python con una API RESTful que gestiona una empresa de renting de coches. Permite registrar y listar coches según marcas, categorías (como deportivos, familiares, SUV) y niveles (lujo, intermedios, accesibles), gestionar usuarios (clientes que alquilan coches), registrar alquileres con fechas y precios, y consultar la disponibilidad de coches mediante operaciones CRUD (Crear, Leer, Actualizar, Eliminar).

## Autores

* (Coordinador) [Carlos Batllés Ortuño](https://github.com/CarlosBatlles)
* [Alexis Angulo Polan](https://github.com/AAlexxis222)
* [Óscar Antón Campillo](https://github.com/Oscar125841)
* [Nicolas Grima Hernández](https://github.com/Nicolas77gh)

## Profesor
[Cristina Cachero](https://github.com/ccacheroc)

## Requisitos
Crearemos una aplicación Python con una API RESTful que gestione una empresa de renting de coches.

La aplicación permitirá: Registrar y listar coches según marcas, categorías (deportivos, familiares, SUV) y niveles (lujo, intermedios, accesibles). 

Gestionar usuarios (clientes que alquilan coches).

Registrar alquileres (con fechas, precios, etc.).

Consultar disponibilidad de coches y realizar operaciones CRUD (Crear, Leer, Actualizar, Eliminar). 

Uso de una API RESTful (usando Flask o FastAPI) 

Uso de archivos JSON y CSV junto a SQL para almacenar los datos 

Alexis Angulo: Creación de las clases principales y la lógica general de estas

Carlos Batllés: Desarrollo de la API

Nicolas Grima: Creación de la documentación y Debugging

Óscar: Creación de Ejemplos.py y bases de datos.

## Instrucciones de instalación y ejecución

Es necesario instalar todas las librerias del requirements.txt y ejecutar el ejecutable de Ejemplos.py

## Resumen de la API

Iniciar sesión (opción 1 del menú principal)
/login: Está función permite a un usuario creado iniciar sesión
Registrarse (opción 2 del menú principal)
/signup: Esta función permite crear un usuario

Cerrar Sesión (opción 4 del menú)
/logout: Esta función permite al usuario cerrar su sesión
Registrar coche (opción 1 del menú de admin)
/coches/registrar: Esta función permite al administrador registrar un nuevo coche a alquilar

Eliminar coche (opción 2 del menú de admin)
/coches/eliminar: Esta función permite al administrador eliminar un coche a alquilar

Listar usuarios (opción 3 del de admin)
/listar-usuarios: Esta función le permite al administrador ver la lista de usuarios registrados

Obtener detalles usuario (opción 4 del menú de admin)
/usuarios/detalles: Esta función le permite al administrador obtener los detalles de un usuario en específico

Actualizar datos coches (opción 5 del menú de admin)
/coches/actualizar-matricula: Esta función le permite al administrador actualizar los datos de uno de los coches a alquilar

Listar alquileres (opción 6 del menú de admin)
/alquileres/listar: Esta función le permite al administrador ver la lista de alquileres realizados por los clientes

Detalle específico de alquiler (opción 7 del menú de admin)
/alquileres/detalles: Esta función le permite a un administrador ver los detalles de un alquiler específico

Finalizar alquiler (opción 8 del menú de admin)
/alquileres/finalizar: Esta opción le permite a un administrador finalizar un alquiler en específico

Alquilar coche (opción 1 del menú de cliente)
/alquilar-coche: Esta opción le permite a un cliente alquilar un coche

Ver historial de alquileres (opción 2 del menú de cliente)
/alquileres/historial: Esta opción le permite a un cliente ver el historial de sus alquileres realizados

Buscar coches disponibles (opción 3 del menú de cliente)
/coches-disponibles: Esta opción le permite a un cliente ver los coches disponibles a alquilar

Datos usuarios (opción 4 del menú de cliente)
/usuarios/Detalles: Esta opción le permite a un cliente ver sus datos

Actualizar contraseña (opción 5 del menú de cliente)
/usuarios/actualizar-contraseña: Esta opción le permite a un cliente cambiar su contraseña

Obtener detalles de un coche (opción 6 del menú de cliente)
/coches/detalles: Esta opción le permite a un cliente obtener los detalles de un coche a alquilar en específico

Categorias de coche (opción 7 del menú de cliente)
/coches/categorias/tipo: Muestra a un cliente las categorias de coches
Categorias de precio (opción 8 del menú de cliente)
/coches/categorias/precio: Muestra a un cliente las categorias de precio






