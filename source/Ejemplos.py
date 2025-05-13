""" Ejemplos de la API"""
import requests
import jwt
import tkinter as tk
from tkinter import filedialog
import datetime
from tabulate import tabulate


BASE_URL = "https://alexiss1.pythonanywhere.com/"  # Cambiar por CarlosBatlles.pythonanywhere.com cuando queramos probar con la webapp
TOKEN = None
ROL = None


def get_headers(auth_required: bool = False) -> dict[str, str]:
    """
    Devuelve los headers necesarios para las solicitudes HTTP.

    Parameters
    ----------
    auth_required : bool, optional
        Indica si se requiere autenticación para la solicitud. 
        Por defecto es False.

    Returns
    -------
    dict[str, str]
        Diccionario con los headers HTTP, incluyendo 'Content-Type' y 
        opcionalmente 'Authorization' si se requiere autenticación y 
        existe un TOKEN.

    Notes
    -----
    - El header 'Content-Type' se establece siempre como 'application/json'.
    - El header 'Authorization' se añade solo si auth_required es True 
      y la variable global TOKEN está definida y no es None.
    """
    headers = {"Content-Type": "application/json"}
    if auth_required and TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    return headers


def decode_token(token: str) -> dict:
    """
    Decodifica un token JWT para extraer sus claims.

    Parameters
    ----------
    token : str
        El token JWT que se desea decodificar.

    Returns
    -------
    dict
        Diccionario con las claims decodificadas del token si tiene éxito,
        o un diccionario vacío si ocurre un error.

    Notes
    -----
    - La decodificación se realiza sin verificar la firma del token,
      lo cual solo debe usarse con fines educativos o de depuración.
    - Requiere que la biblioteca `jwt` (PyJWT) esté instalada.
    - Los errores durante la decodificación se capturan y se imprimen,
      retornando un diccionario vacío en tales casos.
    """
    try:
        # Decodificar el token sin verificar la firma (solo para fines educativos)
        decoded = jwt.decode(token, options={"verify_signature": False})
        return decoded
    except Exception as e:
        print(f"Error al decodificar el token: {e}")
        return {}
    


def mostrar_menu_principal() -> None:
    """
    Muestra y gestiona el menú principal interactivo del sistema.

    Returns
    -------
    None
        La función no retorna valores, solo ejecuta un bucle interactivo
        hasta que el usuario elige salir.

    Notes
    -----
    - La función utiliza un bucle infinito hasta que el usuario selecciona
      la opción de salir (5).
    - Depende de las funciones externas: login(), signup(), 
      entrar_como_invitado(), logout() y mostrar_menu_por_rol().
    - Utiliza la variable global ROL para determinar el rol del usuario tras
      el inicio de sesión.
    - Las opciones válidas son cadenas de texto del "1" al "5".
    """
    
    global ROL
    
    while True:
        print("\n🏠 --- Menú Principal --- 🏠")
        print("1. 🔐 Iniciar sesión")
        print("2. 📝 Registrarse")
        print("3. 👤 Entrar como invitado")
        print("4. 🔚 Cerrar sesión")
        print("5. 🚪 Salir")
        
        opcion = input("👉 Selecciona una opción (1-5): ").strip()

        if opcion == "1":
            if ROL:
                print("❌ Ya has iniciado sesión. Cierra sesión antes de volver a hacerlo.")
            else:
                login()
                if ROL:
                    mostrar_menu_por_rol(ROL)
        elif opcion == "2":
            signup()
        elif opcion == "3":
            entrar_como_invitado()
        elif opcion == "4":
            if not ROL:
                print("❌ No has iniciado sesión aún.")
            else:
                logout()
        elif opcion == "5":
            print("👋 Saliendo del sistema. ¡Hasta pronto!")
            break
        else:
            print("❌ Opción no válida. Por favor, elige una opción entre 1 y 5.")



def menu_admin() -> None:
    """
    Muestra y gestiona el menú interactivo para administradores.

    Returns
    -------
    None
        La función no retorna valores, ejecuta un bucle interactivo hasta
        que el usuario elige volver al menú principal (opción 9).

    Notes
    -----
    - La función presenta un bucle infinito hasta que se selecciona la opción
      de salida (9).
    - Depende de las funciones externas: registrar_coche(), eliminar_coche(),
      listar_usuarios(), detalles_usuario(), actualizar_coche(),
      listar_alquileres(), alquiler_detalles() y finalizar_alquiler().
    - Las opciones válidas son cadenas de texto del "1" al "9".
    - Diseñada para usuarios con privilegios administrativos. 
    """
    print("\n🔐 --- Menú de Administrador --- 🔐")
    print("🟢 Bienvenido, Administrador.")
    print("📌 Desde aquí puedes gestionar usuarios, coches y alquileres.")

    while True:
        print("\n--- Opciones del Administrador ---")
        print("1. 🚗 Registrar coche")
        print("2. 🚫 Eliminar coche")
        print("3. 👥 Listar usuarios")
        print("4. 📄 Obtener detalles de usuario")
        print("5. 🛠️ Actualizar datos de coche")
        print("6. 📋 Listar alquileres")
        print("7. 🔍 Detalle específico de alquiler")
        print("8. ✅ Finalizar alquiler")
        print("9. 🚪 Volver al menú principal")
        
        opcion = input("👉 Selecciona una opción (1-9): ").strip()

        if opcion == "1":
            registrar_coche()
        elif opcion == "2":
            eliminar_coche()
        elif opcion == "3":
            listar_usuarios()
        elif opcion == "4":
            detalles_usuario()
        elif opcion == "5":
            actualizar_coche()
        elif opcion == "6":
            listar_alquileres()
        elif opcion == "7":
            alquiler_detalles()
        elif opcion == "8":
            finalizar_alquiler()
        elif opcion == "9":
            print("👋 Volviendo al menú principal...")
            break
        else:
            print("❌ Opción no válida. Por favor, elige entre 1 y 9.")


def menu_cliente() -> None:
    """
    Muestra y gestiona el menú interactivo para clientes.

    Returns
    -------
    None
        La función no retorna valores, ejecuta un bucle interactivo hasta
        que el usuario elige volver al menú principal (opción 9).

    Notes
    -----
    - La función mantiene un bucle infinito hasta que se selecciona la opción
      de salida (9).
    - Depende de las funciones externas: alquilar_coche(), 
      ver_historial_alquileres(), buscar_coches_disponibles(), 
      detalles_usuario(), actualizar_contraseña(), detalles_coche(), 
      listar_tipos() y listar_precios().
    - Las opciones válidas son cadenas de texto del "1" al "9".
    - Diseñada para usuarios con rol de cliente en el sistema. 
    """
    print("\n🛒 --- Menú de Cliente --- 🛒")
    print("🟢 Bienvenido, Cliente.")
    print("📌 Desde aquí puedes gestionar tus alquileres y consultar información.")

    while True:
        print("\n--- Opciones del Cliente ---")
        print("1. 🚗 Alquilar coche")
        print("2. 📜 Ver historial de alquileres")
        print("3. 🔍 Buscar coches disponibles")
        print("4. 👤 Datos del usuario")
        print("5. 🔐 Actualizar contraseña")
        print("6. 📄 Detalles de un coche")
        print("7. 📁 Categorías de coche")
        print("8. 💰 Categorías de precio")
        print("9. 🚪 Volver al menú principal")

        opcion = input("👉 Selecciona una opción (1-9): ").strip()

        if opcion == "1":
            alquilar_coche()
        elif opcion == "2":
            ver_historial_alquileres()
        elif opcion == "3":
            buscar_coches_disponibles()
        elif opcion == "4":
            detalles_usuario()
        elif opcion == "5":
            actualizar_contraseña()
        elif opcion == "6":
            detalles_coche()
        elif opcion == "7":
            listar_tipos()
        elif opcion == "8":
            listar_precios()
        elif opcion == "9":
            print("👋 Volviendo al menú principal...")
            break
        else:
            print("❌ Opción no válida. Por favor, elige entre 1 y 9.")


def login() -> None:
    """
    Inicia sesión en el sistema y obtiene un token JWT.

    Returns
    -------
    None
        La función no retorna valores, pero actualiza las variables globales
        TOKEN y ROL si el inicio de sesión es exitoso.

    Notes
    -----
    - Modifica las variables globales TOKEN y ROL.
    - Requiere las bibliotecas `requests` y la función `decode_token()`.
    - Depende de la constante BASE_URL definida globalmente.
    - Realiza una solicitud POST al endpoint /login con las credenciales
    proporcionadas por el usuario.
    - Maneja diferentes códigos de estado HTTP (200, 400, 401) y excepciones
    de conexión.
    """
    global TOKEN, ROL
    print("\n🔐 --- Iniciar Sesión --- 🔐")
    email = input("📧 Correo electrónico: ").strip()
    contraseña = input("🔑 Contraseña: ").strip()

    # Validar campos obligatorios
    if not email or not contraseña:
        print("❌ Error: El correo electrónico y la contraseña son obligatorios.")
        return

    # Enviar solicitud POST al endpoint /login
    try:
        r = requests.post(
            f"{BASE_URL}/login",
            json={"email": email, "contraseña": contraseña}
        )

        # Procesar la respuesta
        if r.status_code == 200:
            respuesta = r.json()
            TOKEN = respuesta.get("token")
            claims = decode_token(TOKEN)
            ROL = claims.get("rol")  # Extraer el rol del token
            # Mostrar mensaje bonito con detalles del usuario
            print("\n✅ ¡Inicio de sesión exitoso!\n")
            print("┌────────────────────────────────────┐")
            print("│     📋 Datos del Usuario Logueado  │")
            print("├────────────────────────────────────┤")
            print(f"│ Nombre     : {respuesta.get('nombre', 'N/A')} ")
            print(f"│ Email      : {respuesta.get('email', email)} ")
            print(f"│ Rol        : {respuesta.get('rol', 'N/A')} ")
            print(f"│ ID Usuario : {respuesta.get('id_usuario', 'N/A')} ")
            print("└────────────────────────────────────┘\n")

        elif r.status_code == 400:
            error = r.json().get('error', 'No se recibió mensaje de error.')
            print(f"\n❌ Error: {error}")
        elif r.status_code == 401:
            print("\n❌ Credenciales inválidas. Inténtalo de nuevo.")
        else:
            print(f"\n⚠️ Error inesperado: {r.status_code} - {r.text}")

    except requests.exceptions.RequestException as e:
        print(f"\n🌐 Error al conectar con el servidor: {e}")


def signup() -> None:
    """
    Registra un nuevo usuario en el sistema enviando una solicitud al servidor.

    Returns
    -------
    None
        La función no retorna valores, pero imprime la respuesta del servidor.

    Notes
    -----
    - Solicita al usuario un nombre de usuario y contraseña mediante entrada estándar.
    - Realiza una solicitud POST al endpoint /signup con los datos proporcionados.
    - Requiere la biblioteca `requests` y la constante global BASE_URL.
    - Imprime el código de estado HTTP y la respuesta JSON del servidor.
    - No maneja explícitamente excepciones de red, lo que podría mejorarse.
    """
    print("\n📝 --- Registro de Nuevo Usuario --- 📝")

    nombre = input("👤 Nombre completo: ").strip()
    email = input("📧 Correo electrónico: ").strip()
    contraseña = input("🔑 Contraseña: ").strip()
    
    # Mostrar opciones de tipo de usuario
    print("\nSeleccione el tipo de usuario:")
    print("1. Cliente (por defecto)")
    print("2. Administrador")
    tipo_opcion = input("Ingrese opción (1 o 2): ").strip()

    # Validar tipo de usuario
    if tipo_opcion == "1":
        tipo_usuario = "cliente"
    elif tipo_opcion == "2":
        tipo_usuario = "admin"
    else:
        print("❌ Opción inválida. Se asignará 'cliente' por defecto.")
        tipo_usuario = "cliente"

    # Validar campos obligatorios
    if not nombre or not email or not contraseña:
        print("❌ Error: Todos los campos son obligatorios.")
        return

    try:
        # Enviar solicitud POST al endpoint /signup
        r = requests.post(
            f"{BASE_URL}/signup",
            json={
                "nombre": nombre,
                "email": email,
                "contraseña": contraseña,
                "tipo": tipo_usuario
            }
        )

        # Procesar respuesta
        if r.status_code == 201:
            respuesta = r.json()
            print("\n✅ ¡Registro exitoso!")
            print("┌──────────────────────────────┐")
            print("│     📋 Datos del Registro    │")
            print("├──────────────────────────────┤")
            print(f"│ Nombre     : {nombre}         ")
            print(f"│ Email      : {email}          ")
            print(f"│ Rol        : {tipo_usuario}   ")
            print(f"│ ID Usuario : {respuesta.get('id_usuario', 'N/A')} ")
            print("└──────────────────────────────┘\n")
        elif r.status_code == 400:
            error = r.json().get('error', 'No se recibió mensaje de error.')
            print(f"\n❌ Error: {error}")
        else:
            print(f"\n⚠️ Error inesperado: {r.status_code} - {r.text}")

    except requests.exceptions.RequestException as e:
        print(f"\n🌐 Error al conectar con el servidor: {e}")

def mostrar_menu_por_rol(rol: str) -> None:
    """
    Muestra un menú específico según el rol del usuario.

    Parameters
    ----------
    rol : str
        El rol del usuario, debe ser 'admin' o 'cliente'.

    Returns
    -------
    None
        La función no retorna valores, solo ejecuta el menú correspondiente.

    Notes
    -----
    - Llama a `menu_admin()` si el rol es 'admin'.
    - Llama a `menu_cliente()` si el rol es 'cliente'.
    - Muestra un mensaje de error si el rol no es reconocido.
    - El nombre del rol se muestra con la primera letra en mayúscula.
    """
    if rol == "admin":
        menu_admin()
    elif rol == "cliente":
        menu_cliente()
    else:
        print("Rol no reconocido.")


def entrar_como_invitado() -> None:
    """
    Permite al usuario entrar al sistema como invitado.

    Returns
    -------
    None
        La función no retorna valores, pero actualiza la variable global ROL

    Notes
    -----
    - Establece la variable global ROL como 'invitado'.
    - No requiere autenticación ni credenciales.
    - Diseñada para permitir exploración básica del sistema sin registro.
    """
    global ROL
    ROL = "invitado"
    print("\n👋 Has entrado como invitado.")
    print("📌 Puedes explorar algunas funcionalidades sin iniciar sesión.")

    while True:
        print("\n--- Menú de Invitado ---")
        print("1. 🚗 Alquilar coche")
        print("2. 🔍 Buscar coches disponibles")
        print("3. 📄 Obtener detalles de un coche")
        print("4. 📁 Categorías de coche")
        print("5. 💰 Categorías de precio")
        print("6. 🚪 Volver al menú principal")

        opcion = input("👉 Selecciona una opción (1-6): ").strip()

        if opcion == "1":
            alquilar_coche()
        elif opcion == "2":
            buscar_coches_disponibles()
        elif opcion == "3":
            detalles_coche()
        elif opcion == "4":
            listar_tipos()
        elif opcion == "5":
            listar_precios()
        elif opcion == "6":
            print("👋 Volviendo al menú principal...")
            break
        else:
            print("❌ Opción no válida. Por favor, elige entre 1 y 6.")

def registrar_coche() -> None:
    """
    Registra un nuevo coche en el sistema enviando los datos al servidor.

    Returns
    -------
    None
        La función no retorna valores, pero imprime la respuesta del servidor.

    Notes
    -----
    - Solicita al usuario los detalles del coche mediante entrada estándar.
    - Convierte ciertos campos a tipos específicos: precio_diario (float),
    kilometraje (int), cv (int), plazas (int).
    - Establece el campo 'disponible' como True por defecto.
    - Realiza una solicitud POST al endpoint /coches/registrar.
    - Requiere la biblioteca `requests` y la constante global BASE_URL.
    - Maneja excepciones de red e imprime errores si ocurren.
    """
    global TOKEN
    
    if not TOKEN:
        print("❌ No has iniciado sesión. Por favor, inicia sesión primero.")
        return
    
    print("\n🚗 --- Registrar Nuevo Coche --- 🚗")
    
    marca = input('Marca: ')
    modelo = input('Modelo: ')
    matricula = input('Matricula: ')
    categoria_tipo = input('Categoria tipo: ')
    categoria_precio = input('Categoria precio: ')
    
    try:
        año = int(input("Año (1900 - actual): ").strip())
        if año < 1900 or año > datetime.now().year:
            print("❌ El año debe estar entre 1900 y el año actual.")
            return
    except ValueError:
        print("❌ El año debe ser un número válido.")
        return
    
    try:
        precio_diario = float(input("Precio diario (€): ").strip())
        if precio_diario <= 0:
            print("❌ El precio diario debe ser mayor que cero.")
            return
    except ValueError:
        print("❌ El precio diario debe ser un número válido.")
        return
    
    try:
        kilometraje = float(input("Kilometraje: ").strip())
        if kilometraje < 0:
            print("❌ El kilometraje no puede ser negativo.")
            return
    except ValueError:
        print("❌ El kilometraje debe ser un número válido.")
        return

    color = input("Color: ").strip()
    combustible = input("Combustible (ej. Gasolina, Diésel): ").strip()
    
    try:
        cv = int(input("Caballos (CV): ").strip())
        if cv <= 0:
            print("❌ Los caballos deben ser un número positivo.")
            return
    except ValueError:
        print("❌ Los caballos deben ser un número válido.")
        return
    
    try:
        plazas = int(input("Número de plazas: ").strip())
        if plazas <= 0:
            print("❌ El número de plazas debe ser mayor que cero.")
            return
    except ValueError:
        print("❌ El número de plazas debe ser un número entero.")
        return
    
    disponible_input = input("¿Está disponible? (s/n, por defecto 's'): ").strip().lower()
    disponible = True if disponible_input in ('', 's', 'si', 'yes') else False
    
    # Crear el payload con los datos del coche
    data = {
        'marca': marca,
        'modelo': modelo,
        'matricula': matricula,
        'categoria_tipo': categoria_tipo,
        'categoria_precio': categoria_precio,
        'año': año,
        'precio_diario': precio_diario,
        'kilometraje': kilometraje,
        'color': color,
        'combustible': combustible,
        'cv': cv,
        'plazas': plazas,
        'disponible': disponible
    }

    # Obtener los headers con el token JWT
    headers = get_headers(auth_required=True)

    # Realizar la solicitud POST
    try:
        r = requests.post(f'{BASE_URL}/coches/registrar', json=data, headers=headers)
        if r.status_code == 201:
            respuesta = r.json()
            print("\n✅ ¡Coche registrado exitosamente!")
            print("┌──────────────────────────────┐")
            print("│     📋 Datos del Coche       │")
            print("├──────────────────────────────┤")
            print(f"│ Marca      : {marca}          ")
            print(f"│ Modelo     : {modelo}         ")
            print(f"│ Matrícula  : {matricula}      ")
            print(f"│ Año        : {año}            ")
            print(f"│ Precio     : €{precio_diario:.2f}")
            print(f"│ ID Coche   : {respuesta.get('id_coche', 'N/A')} ")
            print("└──────────────────────────────┘\n")

        elif r.status_code == 400:
            error = r.json().get('error', 'Error desconocido.')
            print(f"\n❌ Error: {error}")
        elif r.status_code == 403:
            print("\n❌ Acceso denegado. Debes ser administrador.")
        else:
            print(f"\n⚠️ Error inesperado: {r.status_code} - {r.text}")

    except requests.exceptions.RequestException as e:
        print(f"\n🌐 Error al conectar con el servidor: {e}")


def eliminar_coche() -> None:
    """
    Elimina un coche del sistema enviando una solicitud al servidor.

    Returns
    -------
    None
        La función no retorna valores, pero imprime la respuesta del servidor.

    Notes
    -----
    - Solicita al usuario el ID del coche a eliminar mediante entrada estándar.
    - Realiza una solicitud DELETE al endpoint /coches/eliminar/{id_coche}.
    - Requiere la biblioteca `requests`, las variables globales BASE_URL y TOKEN,
    y la función get_headers para generar los encabezados con autenticación.
    - Maneja excepciones de red e imprime errores si ocurren.
    """
    global TOKEN  # Acceder a la variable global TOKEN

    # Verificar si hay un token JWT válido
    if not TOKEN:
        print("❌ No has iniciado sesión. Por favor, inicia sesión primero.")
        return

    # Solicitar el ID del coche a eliminar
    id_coche = int(input('🆔 Introduce el ID del coche a eliminar: '))
    # Validar que se haya introducido algo
    if not id_coche:
        print("❌ Error: El ID del coche es obligatorio.")
        return
    
    try:
        if id_coche <= 0:
            print("❌ Error: El ID debe ser un número entero positivo.")
            return
    except ValueError:
        print("❌ Error: El ID debe ser un número válido.")
        return

    # Obtener los headers con el token JWT
    headers = get_headers(auth_required=True)

    # Realizar la solicitud DELETE
    try:
        r = requests.delete(
            f'{BASE_URL}/coches/eliminar/{id_coche}',
            headers=headers  # Incluir los headers con el token JWT
        )
        if r.status_code == 200:
            print("\n✅ Éxito:")
            print("┌──────────────────────────────┐")
            print(f"│ Coche con ID {id_coche} eliminado │")
            print("└──────────────────────────────┘\n")
        elif r.status_code == 404:
            error = r.json().get('error', 'Coche no encontrado')
            print(f"\n❌ Error ({r.status_code}): {error}")
        elif r.status_code == 403:
            print("\n❌ Acceso denegado. Solo los administradores pueden eliminar coches.")
        else:
            print(f"\n⚠️ Error ({r.status_code}): {r.text}")

    except requests.exceptions.RequestException as e:
        print(f"\n🌐 Error al conectar con el servidor: {e}")


def buscar_coches_disponibles() -> None:
    """
    Busca coches disponibles en el sistema según criterios especificados.

    Returns
    -------
    None
        La función no retorna valores, pero imprime la respuesta del servidor.

    Notes
    -----
    - Solicita al usuario criterios de búsqueda (categoría de precio, tipo,
    marca y modelo) mediante entrada estándar.
    - Realiza una solicitud GET al endpoint /coches-disponibles con los
    parámetros como query parameters en la URL.
    - Requiere la biblioteca requests y la constante global BASE_URL.
    - Maneja excepciones de red e imprime errores si ocurren.
    """
    # Solicitar los criterios de búsqueda al usuario
    print("\n🔍 --- Buscar Coches Disponibles --- 🔍")

    categoria_precio = input('Categoría de precio (obligatoria): ').strip()
    categoria_tipo = input('Categoría de tipo (opcional): ').strip()
    marca = input('Marca (opcional): ').strip()
    modelo = input('Modelo (opcional): ').strip()

    if not categoria_precio:
        print("❌ Error: La categoría de precio es obligatoria.")
        return

    try:
        params = {
            'categoria_precio': categoria_precio or None,
            'categoria_tipo': categoria_tipo or None,
            'marca': marca or None,
            'modelo': modelo or None
        }

        # Eliminar parámetros vacíos
        params = {k: v for k, v in params.items() if v is not None}

        r = requests.get(f'{BASE_URL}/coches-disponibles', params=params)

        if r.status_code == 200:
            try:
                datos = r.json()

                # Mostrar resultados dependiendo de la estructura devuelta
                if 'detalles' in datos:
                    coches = datos['detalles']
                    if not coches:
                        print("\n🚫 No se encontraron coches con esos criterios.")
                        return

                    headers = {
                        "matricula": "Matrícula",
                        "marca": "Marca",
                        "modelo": "Modelo",
                        "categoria_precio": "Precio",
                        "categoria_tipo": "Tipo",
                        "año": "Año",
                        "precio_diario": "Precio Diario",
                        "disponible": "Disponible"
                    }

                    table_data = [[c.get(k) for k in headers.keys()] for c in coches]
                    print("\n🚗 Resultados de búsqueda:")
                    print(tabulate(table_data, headers=headers.values(), tablefmt="rounded_grid"))

                elif 'categorias_tipo' in datos:
                    categorias = datos['categorias_tipo']
                    print("\n📁 Categorías de tipo disponibles:")
                    for cat in categorias:
                        print(f" - {cat}")

                elif 'marcas' in datos:
                    marcas = datos['marcas']
                    print("\n🏭 Marcas disponibles:")
                    for m in marcas:
                        print(f" - {m}")

                elif 'modelos' in datos:
                    modelos = datos['modelos']
                    print("\n🛻 Modelos disponibles:")
                    for mod in modelos:
                        print(f" - {mod}")

            except ValueError:
                print("❌ Error al procesar los datos recibidos del servidor.")
        elif r.status_code == 400:
            error = r.json().get('error', 'Solicitud incorrecta.')
            print(f"\n❌ Error ({r.status_code}): {error}")
        else:
            print(f"\n⚠️ Error ({r.status_code}): {r.text}")

    except requests.exceptions.RequestException as e:
        print(f"\n🌐 Error al conectar con el servidor: {e}")


def eliminar_usuario() -> None:
    """
    Elimina un usuario del sistema enviando una solicitud al servidor.

    Returns
    -------
    None
        La función no retorna valores, pero imprime la respuesta del servidor.

    Notes
    -----
    - Solicita el correo electrónico del usuario a eliminar mediante entrada estándar.
    - Realiza una solicitud DELETE al endpoint /usuarios/eliminar con el email como
    parámetro de consulta.
    - Utiliza `get_headers()` para incluir autenticación en los headers si es necesario.
    - Requiere la biblioteca `requests` y la constante global BASE_URL.
    - Maneja excepciones de red e imprime errores si ocurren.
    """
    global TOKEN

    if not TOKEN:
        print("❌ No has iniciado sesión. Por favor, inicia sesión primero.")
        return

    print("\n🗑️ --- Eliminar Usuario --- 🗑️")
    email = input("📧 Correo electrónico del usuario a eliminar: ").strip()
    
    try:
        
        r = requests.delete(
            f"{BASE_URL}/usuarios/eliminar",
            params={"email": email},
            headers=get_headers(auth_required=True)
        )
        if r.status_code == 200:
            print("\n✅ ¡Usuario eliminado exitosamente!")
            print("┌──────────────────────────────┐")
            print(f"│ Correo eliminado: {email}   │")
            print("└──────────────────────────────┘\n")

        elif r.status_code == 400:
            error = r.json().get('error', 'El correo no es válido.')
            print(f"\n❌ Error ({r.status_code}): {error}")

        elif r.status_code == 403:
            print("\n❌ Acceso denegado: Solo los administradores pueden eliminar usuarios.")

        elif r.status_code == 404:
            error = r.json().get('error', 'Usuario no encontrado.')
            print(f"\n🔍 No se encontró ningún usuario con el correo: {email}")
            
        else:
            print(f"\n⚠️ Error ({r.status_code}): {r.text}")

    except requests.exceptions.RequestException as e:
        print(f"\n🌐 Error al conectar con el servidor: {e}")


def listar_usuarios() -> None:
    """
    Lista todos los usuarios registrados en el sistema mediante una solicitud al servidor.

    Returns
    -------
    None
        La función no retorna valores, pero imprime la respuesta del servidor.

    Notes
    -----
    - Realiza una solicitud GET al endpoint /listar-usuarios.
    - Utiliza `get_headers()` con autenticación requerida para incluir el token en los headers.
    - Requiere la biblioteca `requests` y la constante global BASE_URL.
    - Maneja excepciones de red e imprime errores si ocurren.
    - Se asume que el endpoint retorna una lista de usuarios en formato JSON.
    """
    global TOKEN

    if not TOKEN:
        print("❌ No has iniciado sesión. Por favor, inicia sesión primero.")
        return

    print("\n👥 --- Listado de Usuarios --- 👤")
    
    try:
        r = requests.get(
            f"{BASE_URL}/listar-usuarios",
            headers=get_headers(auth_required=True)
        )
        if r.status_code == 200:
            datos = r.json()
            usuarios = datos.get('usuarios', [])

            if not usuarios:
                print("\n🚫 No hay usuarios registrados en el sistema.")
                return

            # Mostrar usuarios en tabla
            headers_table = {
                'id_usuarios': 'ID',
                'nombre': 'Nombre',
                'tipo': 'Rol',
                'email': 'Correo Electrónico'
            }

            table_data = [[usuario[k] for k in headers_table.keys()] for usuario in usuarios]

            print("\n📋 Usuarios registrados:")
            print(tabulate(table_data, headers=headers_table.values(), tablefmt="rounded_grid"))

        elif r.status_code == 403:
            print("\n❌ Acceso denegado: Solo los administradores pueden ver este contenido.")

        elif r.status_code == 404:
            print("\n🔍 No se encontraron usuarios registrados.")

        else:
            print(f"\n⚠️ Error ({r.status_code}): {r.text}")

    except requests.exceptions.RequestException as e:
        print(f"\n🌐 Error al conectar con el servidor: {e}")

def detalles_usuario() -> None:
    """
    Obtiene los detalles de un usuario específico enviando una solicitud al servidor.

    Returns
    -------
    None
        La función no retorna valores, pero imprime la respuesta del servidor.

    Notes
    -----
    - Solicita el correo electrónico del usuario mediante entrada estándar.
    - Realiza una solicitud GET al endpoint /usuarios/detalles/{email}.
    - Utiliza `get_headers()` con autenticación requerida para incluir el token en los headers.
    - Requiere la biblioteca `requests` y la constante global BASE_URL.
    - Maneja excepciones de red e imprime errores si ocurren.
    - Se asume que el endpoint retorna los detalles del usuario en formato JSON.
    """
    
    global TOKEN

    if not TOKEN:
        print("❌ No has iniciado sesión. Por favor, inicia sesión primero.")
        return

    print("\n📄 --- Detalles del Usuario --- 📄")
    email = input("📧 Correo del usuario: ").strip()
    
    try:
        r = requests.get(
            f"{BASE_URL}/usuarios/detalles/{email}",
            headers=get_headers(auth_required=True)
        )
        if r.status_code == 200:
            datos = r.json()
            usuario = datos.get('usuario', {})

            # Preparar los datos para mostrarlos en tabla
            table_data = [[
                usuario.get('id_usuario', 'N/A'),
                usuario.get('nombre', 'N/A'),
                usuario.get('email', 'N/A'),
                usuario.get('tipo', 'N/A')
            ]]

            headers_table = ['ID', 'Nombre', 'Email', 'Rol']

            print("\n✅ Detalles del usuario:")
            print(tabulate(table_data, headers=headers_table, tablefmt="rounded_grid"))

        elif r.status_code == 403:
            print("\n❌ Acceso denegado: No tienes permiso para ver estos detalles.")

        elif r.status_code == 404:
            print(f"\n🔍 No se encontró ningún usuario con el correo: {email}")

        else:
            print(f"\n⚠️ Error ({r.status_code}): {r.text}")

    except requests.exceptions.RequestException as e:
        print(f"\n🌐 Error al conectar con el servidor: {e}")

def actualizar_contraseña() -> None:
    """
    Actualiza la contraseña de un usuario enviando una solicitud al servidor.

    Returns
    -------
    None
        La función no retorna valores, pero imprime la respuesta del servidor.

    Notes
    -----
    - Solicita la nueva contraseña y el correo electrónico del usuario mediante entrada estándar.
    - Realiza una solicitud PUT al endpoint /usuarios/actualizar-contraseña/{email}.
    - Envía la nueva contraseña en el cuerpo JSON.
    - Utiliza `get_headers()` con autenticación requerida para incluir el token en los headers.
    - Requiere la biblioteca `requests` y la constante global BASE_URL.
    - Maneja excepciones de red e imprime errores si ocurren.
    """
    try:
        nueva_contraseña = input("Nueva contraseña: ").strip()
        email = input("Tu correo electrónico: ").strip()
        r = requests.put(
            f"{BASE_URL}/usuarios/actualizar-contraseña/{email}",
            json={"nueva_contraseña": nueva_contraseña},
            headers=get_headers(auth_required=True)
        )
        print("Respuesta:", r.status_code, r.json())
    except requests.exceptions.RequestException as e:
        print("Error de conexión:", e)

def logout() -> None:
    """
    Cierra la sesión del usuario enviando una solicitud al servidor.

    Returns
    -------
    None
        La función no retorna valores, pero imprime la respuesta del servidor.

    Notes
    -----
    - Realiza una solicitud POST al endpoint /logout.
    - Utiliza `get_headers()` con autenticación requerida para incluir el token en los headers.
    - Requiere la biblioteca `requests` y la constante global BASE_URL.
    - Maneja excepciones de red e imprime errores si ocurren.
    - Se asume que el servidor invalida el token tras esta solicitud.
    """
    try:
        r = requests.post(
            f"{BASE_URL}/logout",
            headers=get_headers(auth_required=True)
        )
        print("Respuesta:", r.status_code, r.json())
    except requests.exceptions.RequestException as e:
        print("Error de conexión:", e)

def detalles_coche() -> None:
    """
    Consulta y muestra los detalles de un coche utilizando su matrícula.

    Esta función solicita al usuario la matrícula de un coche, realiza una petición GET a una API 
    para obtener los detalles del coche correspondiente y muestra la respuesta. Si ocurre un error 
    de conexión durante la solicitud, se captura la excepción y se muestra un mensaje de error.

    La URL de la API se construye utilizando la variable global `BASE_URL` y los encabezados necesarios 
    se obtienen mediante la función `get_headers()`.

    Raises
    ------
    requests.exceptions.RequestException
        Si ocurre un error durante la solicitud HTTP (por ejemplo, problemas de conexión, 
        timeout, o errores de red), se captura la excepción y se imprime un mensaje de error.

    Notes
    -----
    - Se utiliza el método `strip()` para eliminar espacios en blanco innecesarios en la entrada de la matrícula.
    - La función imprime directamente la respuesta o el mensaje de error en lugar de devolver valores.
    """
    try:
        matricula: str = input("Matrícula del coche: ").strip()
        r: requests.Response = requests.get(
            f"{BASE_URL}/coches/detalles/{matricula}", headers=get_headers()
        )
        print("Respuesta:", r.status_code, r.json())
    except requests.exceptions.RequestException as e:
        print("Error de conexión:", e)

def actualizar_coche() -> None:
    """
    Actualiza la matrícula de un coche identificado por su ID.

    Esta función solicita al usuario el ID del coche y la nueva matrícula, realiza una petición PUT 
    a una API para actualizar la matrícula del coche correspondiente y muestra la respuesta. Si ocurre 
    un error de conexión durante la solicitud, se captura la excepción y se muestra un mensaje de error.

    La URL de la API se construye utilizando la variable global `BASE_URL`, y los encabezados necesarios 
    se obtienen mediante la función `get_headers()` con el parámetro `auth_required=True`.

    Raises
    ------
    requests.exceptions.RequestException
        Si ocurre un error durante la solicitud HTTP (por ejemplo, problemas de conexión, 
        timeout, o errores de red), se captura la excepción y se imprime un mensaje de error.

    Notes
    -----
    - Se utiliza el método `strip()` para eliminar espacios en blanco innecesarios en las entradas del ID y la nueva matrícula.
    - La función imprime directamente la respuesta o el mensaje de error en lugar de devolver valores.
    - El cuerpo de la solicitud contiene un objeto JSON con la clave `"nueva_matricula"` y el valor proporcionado por el usuario.
    """
    try:
        id_coche: str = input("ID del coche a actualizar: ").strip()
        nueva_matricula: str = input("Nueva matrícula: ").strip()
        r: requests.Response = requests.put(
            f"{BASE_URL}/coches/actualizar-matricula/{id_coche}",
            json={"nueva_matricula": nueva_matricula},
            headers=get_headers(auth_required=True)
        )
        print("Respuesta:", r.status_code, r.json())
    except requests.exceptions.RequestException as e:
        print("Error de conexión:", e)

def listar_alquileres() -> None:
    """
    Lista todos los alquileres disponibles realizando una solicitud GET a la API.

    Esta función realiza una petición GET a una API para obtener una lista de todos los alquileres 
    registrados. La URL de la API se construye utilizando la variable global `BASE_URL`, y los encabezados 
    necesarios se obtienen mediante la función `get_headers()` con el parámetro `auth_required=True`.

    Si la solicitud es exitosa, se imprime la respuesta de la API, que incluye el código de estado HTTP 
    y los datos en formato JSON. Si ocurre un error de conexión durante la solicitud, se captura la excepción 
    y se muestra un mensaje de error.

    Raises
    ------
    requests.exceptions.RequestException
        Si ocurre un error durante la solicitud HTTP (por ejemplo, problemas de conexión, 
        timeout, o errores de red), se captura la excepción y se imprime un mensaje de error.

    Notes
    -----
    - La función imprime directamente la respuesta o el mensaje de error en lugar de devolver valores.
    - Se requiere autenticación para acceder a este endpoint, por lo que se utiliza `auth_required=True` 
      en la función `get_headers()`.
    """
    try:
        r: requests.Response = requests.get(
            f"{BASE_URL}/alquileres/listar", headers=get_headers(auth_required=True)
        )
        print("Respuesta:", r.status_code, r.json())
    except requests.exceptions.RequestException as e:
        print("Error de conexión:", e)

def alquiler_detalles() -> None:
    """
    Obtiene y muestra los detalles de un alquiler específico utilizando su ID.

    Esta función solicita al usuario el ID de un alquiler, realiza una petición GET a una API 
    para obtener los detalles del alquiler correspondiente y muestra la respuesta. Si ocurre un error 
    de conexión durante la solicitud, se captura la excepción y se muestra un mensaje de error.

    La URL de la API se construye utilizando la variable global `BASE_URL`, y los encabezados necesarios 
    se obtienen mediante la función `get_headers()` con el parámetro `auth_required=True`.

    Raises
    ------
    requests.exceptions.RequestException
        Si ocurre un error durante la solicitud HTTP (por ejemplo, problemas de conexión, 
        timeout, o errores de red), se captura la excepción y se imprime un mensaje de error.

    Notes
    -----
    - Se utiliza el método `strip()` para eliminar espacios en blanco innecesarios en la entrada del ID.
    - La función imprime directamente la respuesta o el mensaje de error en lugar de devolver valores.
    - Se requiere autenticación para acceder a este endpoint, por lo que se utiliza `auth_required=True` 
      en la función `get_headers()`.
    """
    try:
        id_alquiler: str = input("ID del alquiler: ").strip()
        r: requests.Response = requests.get(
            f"{BASE_URL}/alquileres/detalles/{id_alquiler}", headers=get_headers(auth_required=True)
        )
        print("Respuesta:", r.status_code, r.json())
    except requests.exceptions.RequestException as e:
        print("Error de conexión:", e)

def finalizar_alquiler() -> None:
    """
    Finaliza un alquiler específico identificado por su ID.

    Esta función solicita al usuario el ID del alquiler que se desea finalizar, realiza una petición PUT 
    a una API para marcar el alquiler como finalizado y muestra la respuesta. Si ocurre un error de conexión 
    durante la solicitud, se captura la excepción y se muestra un mensaje de error.

    La URL de la API se construye utilizando la variable global `BASE_URL`, y los encabezados necesarios 
    se obtienen mediante la función `get_headers()` con el parámetro `auth_required=True`.

    Raises
    ------
    requests.exceptions.RequestException
        Si ocurre un error durante la solicitud HTTP (por ejemplo, problemas de conexión, 
        timeout, o errores de red), se captura la excepción y se imprime un mensaje de error.

    Notes
    -----
    - Se utiliza el método `strip()` para eliminar espacios en blanco innecesarios en la entrada del ID.
    - La función imprime directamente la respuesta o el mensaje de error en lugar de devolver valores.
    - Se requiere autenticación para acceder a este endpoint, por lo que se utiliza `auth_required=True` 
      en la función `get_headers()`.
    """
    try:
        id_alquiler: str = input("🆔 ID del alquiler a finalizar: ").strip()
        r: requests.Response = requests.put(
            f"{BASE_URL}/alquileres/finalizar/{id_alquiler}", headers=get_headers(auth_required=True)
        )
        print("Respuesta:", r.status_code, r.json())
    except requests.exceptions.RequestException as e:
        print("Error de conexión:", e)


def ver_historial_alquileres() -> None:
    """
    Muestra el historial de alquileres de un usuario identificado por su email.

    Esta función solicita al usuario el email asociado a los alquileres que desea consultar, 
    realiza una petición GET a una API para obtener el historial de alquileres correspondiente 
    y muestra la respuesta. Si ocurre un error de conexión durante la solicitud, se captura la 
    excepción y se muestra un mensaje de error.

    La URL de la API se construye utilizando la variable global `BASE_URL`. El email se incluye 
    como parte de la URL del endpoint.

    Raises
    ------
    requests.exceptions.RequestException
        Si ocurre un error durante la solicitud HTTP (por ejemplo, problemas de conexión, 
        timeout, o errores de red), se captura la excepción y se imprime un mensaje de error.

    Notes
    -----
    - La función imprime directamente la respuesta o el mensaje de error en lugar de devolver valores.
    """
    global TOKEN  # Acceder a la variable global TOKEN

    # Verificar si hay un token JWT válido
    if not TOKEN:
        print("No has iniciado sesión. Por favor, inicia sesión primero.")
        return

    # Solicitar el email del usuario
    email = input('Email: ').strip()

    # Validar que el email no esté vacío
    if not email:
        print("El email es obligatorio.")
        return

    # Obtener los headers con el token JWT
    headers = get_headers(auth_required=True)

    # Realizar la solicitud GET
    try:
        r = requests.get(
            f'{BASE_URL}/alquileres/historial/{email}',  # Incluir el email en la URL
            headers=headers  # Incluir los headers con el token JWT
        )
        print('Respuesta: ', r.status_code, r.json())
    except requests.exceptions.RequestException as e:
        print(f'Error al obtener el historial de alquileres: {e}')

def alquilar_coche() -> None:
    """
    Permite al usuario alquilar un coche y descargar la factura en formato PDF.

    Esta función solicita al usuario la matrícula del coche, las fechas de inicio y fin del alquiler, 
    y el email del usuario (opcional). Luego, envía una solicitud POST a una API para registrar el alquiler. 
    Si la solicitud es exitosa (código de estado 200), se descarga un archivo PDF con la factura del alquiler 
    utilizando un cuadro de diálogo para elegir la ubicación de guardado.

    La URL de la API se construye utilizando la variable global `BASE_URL`. Los datos del alquiler se envían 
    en formato JSON en el cuerpo de la solicitud.

    Raises
    ------
    requests.exceptions.RequestException
        Si ocurre un error durante la solicitud HTTP (por ejemplo, problemas de conexión, 
        timeout, o errores de red), se captura la excepción y se imprime un mensaje de error.

    Notes
    -----
    - Se utiliza el método `strip()` para eliminar espacios en blanco innecesarios en las entradas del usuario.
    - Si el campo de email se deja en blanco, se asume que el usuario es un invitado y no se incluye el email en la solicitud.
    - Para guardar el archivo PDF, se utiliza el módulo `tkinter.filedialog`, que abre un cuadro de diálogo gráfico.
    - La función imprime mensajes informativos sobre el resultado de la operación.
    """
    print("\n--- Alquilar Coche ---")
    matricula: str = input("Matrícula del coche: ").strip()
    fecha_inicio: str = input("Fecha de inicio (YYYY-MM-DD): ").strip()
    fecha_fin: str = input("Fecha de fin (YYYY-MM-DD): ").strip()
    email: str | None = input("Email del usuario (dejar en blanco para invitado): ").strip() or None

    # Preparar los datos para la solicitud
    data: dict[str, str | None] = {
        "matricula": matricula,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
    }
    if email:
        data["email"] = email

    try:
        # Enviar la solicitud POST al endpoint /alquilar-coche
        r: requests.Response = requests.post(f"{BASE_URL}/alquilar-coche", json=data)

        # Procesar la respuesta
        if r.status_code == 200:
            # Guardar el archivo PDF recibido
            root = tk.Tk()
            root.withdraw()  # Ocultar la ventana principal

            # Abrir un cuadro de diálogo para elegir la ubicación
            ruta_guardado = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF Files", "*.pdf")],
                initialdir="~/Downloads",
                title="Guardar factura PDF",
                initialfile="factura.pdf"
            )

            if ruta_guardado:
                with open(ruta_guardado, "wb") as f:
                    f.write(r.content)
                print("Factura descargada exitosamente.")
            else:
                print("Guardado cancelado por el usuario.")
        else:
            print(f"Error: {r.status_code} - {r.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")


def listar_tipos() -> None:
    """
    Lista los tipos de categorías de coches disponibles realizando una solicitud GET a la API.

    Esta función realiza una petición GET a una API para obtener una lista de los tipos de categorías 
    de coches registrados. La URL de la API se construye utilizando la variable global `BASE_URL`.

    Si la solicitud es exitosa, se imprime la respuesta de la API, que incluye el código de estado HTTP 
    y los datos en formato JSON. Si ocurre un error de conexión durante la solicitud, se captura la excepción 
    y se muestra un mensaje de error.

    Raises
    ------
    requests.exceptions.RequestException
        Si ocurre un error durante la solicitud HTTP (por ejemplo, problemas de conexión, 
        timeout, o errores de red), se captura la excepción y se imprime un mensaje de error.
    """
    try:
        r: requests.Response = requests.get(f"{BASE_URL}/coches/categorias/tipo")
        print("Respuesta:", r.status_code, r.json())
    except requests.exceptions.RequestException as e:
        print("Error de conexión:", e)

def listar_precios() -> None:
    """
    Lista los precios de las categorías de coches disponibles realizando una solicitud GET a la API.

    Esta función realiza una petición GET a una API para obtener una lista de los precios asociados 
    a las categorías de coches registradas. La URL de la API se construye utilizando la variable global `BASE_URL`.

    Si la solicitud es exitosa, se imprime la respuesta de la API, que incluye el código de estado HTTP 
    y los datos en formato JSON. Si ocurre un error de conexión durante la solicitud, se captura la excepción 
    y se muestra un mensaje de error.

    Raises
    ------
    requests.exceptions.RequestException
        Si ocurre un error durante la solicitud HTTP (por ejemplo, problemas de conexión, 
        timeout, o errores de red), se captura la excepción y se imprime un mensaje de error.
    """
    try:
        r: requests.Response = requests.get(f"{BASE_URL}/coches/categorias/precio")
        print("Respuesta:", r.status_code, r.json())
    except requests.exceptions.RequestException as e:
        print("Error de conexión:", e)

def main() -> None:
    """
    Función principal que inicia la aplicación.

    Esta función es el punto de entrada de la aplicación. Llama a la función `mostrar_menu_principal()` 
    para presentar al usuario un menú interactivo desde el cual puede realizar diversas operaciones, como 
    gestionar coches, alquileres o consultar información.

    Notes
    -----
    - La función no devuelve ningún valor.
    - Dependiendo de la implementación de `mostrar_menu_principal()`, esta función podría incluir un bucle 
      infinito hasta que el usuario decida salir de la aplicación.
    """
    mostrar_menu_principal()

main()