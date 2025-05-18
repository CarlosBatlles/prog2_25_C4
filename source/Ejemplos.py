# -*- coding: utf-8 -*-

"""
Script de cliente de consola para interactuar con la API de Alquiler de Coches.

Este script proporciona un menú interactivo para probar las diversas
funcionalidades de la API, incluyendo la gestión de usuarios, coches y alquileres.
"""

# --------------------------------------------------------------------------
# SECCIÓN 1: IMPORTACIONES Y CONFIGURACIÓN GLOBAL
# --------------------------------------------------------------------------
import requests
import jwt # Para decodificar el token (solo fines ilustrativos/debug)
import tkinter as tk
from tkinter import filedialog
import datetime # Usado para validación de año y formato de fechas
from tabulate import tabulate
import re # Usado para validación de matrícula
from typing import Dict, Optional, List, Any, Union # Para sugerencias de tipo

# --- Constantes Globales ---
BASE_URL: str = "https://alexiss1.pythonanywhere.com/" # URL base de la API

# --- Variables Globales de Estado de Sesión ---
TOKEN: Optional[str] = None # Almacena el token JWT del usuario autenticado
ROL: Optional[str] = None   # Almacena el rol del usuario ('admin', 'cliente', 'invitado')


# --------------------------------------------------------------------------
# SECCIÓN 2: FUNCIONES AUXILIARES
# --------------------------------------------------------------------------


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
    global TOKEN
    headers: Dict[str, str] = {"Content-Type": "application/json"}
    if auth_required and TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    return headers


def decode_token(token: str) -> Dict[str, Any]:
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
    

# --------------------------------------------------------------------------
# SECCIÓN 3: GESTIÓN DE MENÚS Y NAVEGACIÓN
# --------------------------------------------------------------------------


def mostrar_menu_principal() -> None:
    """
    Muestra el menú principal y gestiona la navegación inicial del usuario.

    Las opciones del menú cambian dinámicamente según el estado de la sesión:
    - Sin sesión: Iniciar sesión, Registrarse, Entrar como invitado, Salir.
    - Con sesión: Muestra rol, opción para volver al menú de rol, Cerrar sesión, Salir.

    Returns
    -------
    None
        La función no retorna valores; ejecuta un bucle interactivo hasta
        que el usuario elige salir.

    Notes
    -----
    - Modifica y lee las variables globales `ROL` y `TOKEN`.
    - Llama a sub-menús o funciones de acción basadas en la selección del usuario.
    """
    global ROL, TOKEN 

    while True:
        print("\n🏠 --- Menú Principal --- 🏠")
        opcion_salir_numero: str
        opciones_menu_str: str # String para mostrar las opciones disponibles en el prompt

        if not TOKEN: # Sin sesión activa
            print("1. 🔐 Iniciar sesión")
            print("2. 📝 Registrarse")
            print("3. 👤 Entrar como invitado")
            print("4. 🚪 Salir")
            opcion_salir_numero = "4"
            opciones_menu_str = "1-4"
        else: # Con sesión activa 
            rol_display: str = str(ROL).capitalize() if ROL else "Usuario Desconocido"
            print(f"🟢 Sesión activa como: {rol_display}")
            
            print("M. 🛠️ Ir a mi Menú de Usuario") # Opción para volver al menú de rol
            print("4. 🔚 Cerrar sesión")
            print("5. 🚪 Salir")
            opcion_salir_numero = "5"
            opciones_menu_str = "M, 4-5"

        opcion_seleccionada: str = input(f"👉 Selecciona una opción ({opciones_menu_str}): ").strip().lower()

        # --- Lógica de Manejo de Opciones ---
        if not TOKEN: # Lógica para cuando NO hay sesión
            if opcion_seleccionada == "1":
                login_exitoso = login()
                if login_exitoso and ROL:
                    mostrar_menu_por_rol(ROL) 
            elif opcion_seleccionada == "2":
                signup()
            elif opcion_seleccionada == "3":
                entrar_como_invitado()
            elif opcion_seleccionada == opcion_salir_numero: # Salir (opción "4")
                print("👋 Saliendo del sistema. ¡Hasta pronto!")
                break
            else:
                print(f"❌ Opción no válida. Por favor, elige una opción entre 1 y {opcion_salir_numero}.")
        
        else: # Lógica para cuando SÍ hay sesión (TOKEN existe)
            if opcion_seleccionada == "m" and ROL: # Opción "M" para ir al menú de rol
                print(f"➡️ Accediendo al menú de {str(ROL).capitalize()}...")
                mostrar_menu_por_rol(ROL)
            elif opcion_seleccionada == "4": # Cerrar sesión
                logout() 
            elif opcion_seleccionada == opcion_salir_numero: # Salir (opción "5")
                print("👋 Saliendo del sistema. ¡Hasta pronto!")
                break
            else:
                print(f"❌ Opción no válida. Por favor, elige una opción del menú (M, 4, o 5).")




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
        print("2. 👥 Listar usuarios")
        print("3. 📄 Obtener detalles de usuario")
        print("4. 🛠️  Actualizar datos de coche")
        print("5. 📋 Listar alquileres")
        print("6. 🔍 Detalle específico de alquiler")
        print("7. ✅ Finalizar alquiler")
        print("8. 🚪 Volver al menú principal")
        
        opcion = input("👉 Selecciona una opción (1-8): ").strip()

        if opcion == "1":
            registrar_coche()
        elif opcion == "2":
            listar_usuarios()
        elif opcion == "3":
            detalles_usuario()
        elif opcion == "4":
            actualizar_coche()
        elif opcion == "5":
            listar_alquileres()
        elif opcion == "6":
            alquiler_detalles()
        elif opcion == "7":
            finalizar_alquiler()
        elif opcion == "8":
            print("👋 Volviendo al menú principal...")
            break
        else:
            print("❌ Opción no válida. Por favor, elige entre 1 y 8.")


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
        print("1. 🚗 Alquilar coche (como invitado)")
        print("2. 🔍 Buscar coches disponibles (filtros)")
        print("3. 📄 Ver detalles de un coche (por matrícula)")
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
            ROL = None  # Limpiar el rol al salir
            break
        else:
            print("❌ Opción no válida. Por favor, elige entre 1 y 6.")


# --------------------------------------------------------------------------
# SECCIÓN 4: AUTENTICACIÓN Y GESTIÓN DE SESIÓN
# --------------------------------------------------------------------------


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

            # Datos a mostrar en tabla
            user_data = [[
                claims.get('nombre', 'N/A'),
                email,
                claims.get('rol', 'N/A'),
                respuesta.get('id_usuario', 'N/A')
            ]]

            headers_table = ["Nombre", "Correo Electrónico", "Rol", "ID Usuario"]

            print("\n✅ ¡Inicio de sesión exitoso!")
            print(tabulate(user_data, headers=headers_table, tablefmt="rounded_grid"))

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
            user_data = [
                [
                    nombre,
                    email,
                    tipo_usuario.capitalize(),
                    respuesta.get('id_usuario', 'N/A')
                ]
            ]

            headers_table = ["Nombre", "Correo Electrónico", "Rol", "ID Usuario"]

            print("\n✅ ¡Registro exitoso!")
            print(tabulate(user_data, headers=headers_table, tablefmt="rounded_grid"))

        elif r.status_code == 400:
            error = r.json().get('error', 'No se recibió mensaje de error.')
            print(f"\n❌ Error: {error}")
        else:
            print(f"\n⚠️ Error inesperado: {r.status_code} - {r.text}")

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
    print("\n🔐 --- Actualizar Contraseña --- 🔐")

    email = input("📧 Correo electrónico: ").strip()
    nueva_contraseña = input("🔑 Nueva contraseña: ").strip()
    confirmacion = input("🔁 Confirmar nueva contraseña: ").strip()
    
    if nueva_contraseña != confirmacion:
        print("❌ Error: Las contraseñas no coinciden.")
        return
    
    try:
        r = requests.put(
            f"{BASE_URL}/usuarios/actualizar-contraseña/{email}",
            json={"nueva_contraseña": nueva_contraseña},
            headers=get_headers(auth_required=True)
        )
        if r.status_code == 200:
            print("\n✅ ¡Contraseña actualizada exitosamente!")
            print("🔓 Puedes iniciar sesión con tu nueva contraseña.")

        elif r.status_code == 400:
            error = r.json().get('error', 'No se pudo actualizar la contraseña.')
            print(f"\n❌ Error ({r.status_code}): {error}")

        elif r.status_code == 403:
            print("\n❌ Acceso denegado: Solo puedes cambiar tu propia contraseña.")

        else:
            print(f"\n⚠️ Error ({r.status_code}): {r.text}")

    except requests.exceptions.RequestException as e:
        print(f"\n🌐 Error al conectar con el servidor: {e}")


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
    global TOKEN, ROL
    
    try:
        r = requests.post(
            f"{BASE_URL}/logout",
            headers=get_headers(auth_required=True)
        )
        if r.status_code == 200:
            # Limpiar variables globales
            TOKEN = None
            ROL = None

            print("\n👋 Sesión cerrada exitosamente.")
            print("🔓 Ahora puedes iniciar sesión con otro usuario o salir del sistema.")

        else:
            print(f"\n⚠️ Error ({r.status_code}): {r.text}")

    except requests.exceptions.RequestException as e:
        print(f"\n🌐 Error al conectar con el servidor: {e}")


# --------------------------------------------------------------------------
# SECCIÓN 5: OPERACIONES CON COCHES (ACCESIBLES DESDE VARIOS MENÚS)
# --------------------------------------------------------------------------


def detalles_coche() -> None:
    """
    Consulta y muestra los detalles de un coche específico utilizando su matrícula.

    Solicita al usuario la matrícula del coche a consultar. Realiza una solicitud
    GET al endpoint `/coches/detalles/{matricula}` de la API. Si la solicitud
    es exitosa (200 OK), formatea y muestra los detalles del coche en una tabla.
    Maneja errores comunes como coche no encontrado (404) o problemas de conexión.

    Notes
    -----
    - Esta función no requiere autenticación por defecto para ver detalles de un coche.
    Si el endpoint API cambiara y necesitara autenticación, se debería
    modificar la llamada a `get_headers()`.
    - La salida se imprime directamente en la consola.
    """
    print("\n📄 --- Detalles del Coche --- 📄")
    matricula = input("🔤 Matrícula del coche (p.ej: 0000 XXX): ").strip()

    if not matricula:
        print("❌ Error: La matrícula es obligatoria.")
        return
    
    try:
        r: requests.Response = requests.get(
            f"{BASE_URL}/coches/detalles/{matricula}", headers=get_headers()
        )
        if r.status_code == 200:
            datos = r.json()
            coche = datos.get('coche', {})

            # Mostrar detalles del coche en tabla bonita
            table_data = [[
                coche.get('id', 'N/A'),
                coche.get('marca', 'N/A'),
                coche.get('modelo', 'N/A'),
                coche.get('matricula', 'N/A'),
                coche.get('categoria_tipo', 'N/A'),
                coche.get('categoria_precio', 'N/A'),
                coche.get('año', 'N/A'),
                f"€{float(coche.get('precio_diario', 0)):.2f}",
                coche.get('kilometraje', 'N/A'),
                coche.get('color', 'N/A'),
                coche.get('combustible', 'N/A'),
                coche.get('cv', 'N/A'),
                coche.get('plazas', 'N/A'),
                "✅ Sí" if coche.get('disponible', False) else "❌ No"
            ]]

            headers_table = [
                "ID", "Marca", "Modelo", "Matrícula",
                "Tipo", "Categoría Precio", "Año",
                "Precio Diario", "Kilometraje", "Color",
                "Combustible", "CV", "Plazas", "Disponible"
            ]

            print("\n✅ Detalles del coche:")
            print(tabulate(table_data, headers=headers_table, tablefmt="rounded_grid"))

        elif r.status_code == 404:
            print(f"\n🔍 No se encontró ningún coche con la matrícula '{matricula}'.")
        else:
            print(f"\n⚠️ Error ({r.status_code}): {r.text}")

    except requests.exceptions.RequestException as e:
        print(f"\n🌐 Error al conectar con el servidor: {e}")


def buscar_coches_disponibles() -> None:
    """
    Busca coches disponibles según múltiples criterios opcionales.

    Solicita al usuario una categoría de precio (obligatoria) y, opcionalmente,
    tipo de categoría, marca y modelo. Realiza una solicitud GET al endpoint
    `/coches-disponibles` de la API. La respuesta de la API puede variar:
    puede devolver una lista de tipos de categoría, marcas, modelos o
    detalles completos de coches, dependiendo de cuántos filtros se proporcionen.
    La función formatea y muestra la información recibida.

    Notes
    -----
    - Este endpoint no requiere autenticación.
    - La salida se imprime directamente en la consola.
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


def listar_tipos() -> None:
    """
    Muestra una lista de todas las categorías de tipo de coches disponibles.

    Realiza una solicitud GET al endpoint `/coches/categorias/tipo` de la API.
    Si la solicitud es exitosa, formatea y muestra las categorías en una tabla numerada.
    """
    
    print("\n📁 --- Categorías de Tipo de Coche --- 📁")
    
    try:
        r: requests.Response = requests.get(f"{BASE_URL}/coches/categorias/tipo")
        if r.status_code == 200:
            datos = r.json()
            categorias = datos.get("categorias_tipo", [])

            if not categorias:
                print("\n🚫 No hay categorías de tipo disponibles.")
                return

            # Mostrar las categorías en formato tabla
            table_data = [[idx + 1, categoria] for idx, categoria in enumerate(categorias)]
            headers_table = ["#", "Categoría de Tipo"]

            print("\n🔢 Categorías disponibles:")
            print(tabulate(table_data, headers=headers_table, tablefmt="rounded_grid"))

        elif r.status_code == 404:
            print(f"\n🔍 No se encontraron categorías de tipo: {r.json().get('error', 'No hay categorías disponibles')}")
        else:
            print(f"\n⚠️ Error ({r.status_code}): {r.text}")

    except requests.exceptions.RequestException as e:
        print(f"\n🌐 Error al conectar con el servidor: {e}")
        print("Error de conexión:", e)


def listar_precios() -> None:
    """
    Muestra una lista de todas las categorías de precio de coches disponibles.

    Realiza una solicitud GET al endpoint `/coches/categorias/precio` de la API.
    Si la solicitud es exitosa, formatea y muestra las categorías en una tabla numerada.
    """
    
    print("\n💰 --- Categorías de Precio --- 💰")
    
    try:
        r: requests.Response = requests.get(f"{BASE_URL}/coches/categorias/precio")
        if r.status_code == 200:
            datos = r.json()
            categorias = datos.get("categorias_precio", [])

            if not categorias:
                print("\n🚫 No hay categorías de precio disponibles.")
                return

            # Mostrar categorías en tabla
            table_data = [[idx + 1, categoria] for idx, categoria in enumerate(categorias)]
            headers_table = ["#", "Categoría de Precio"]

            print("\n🏷️ Categorías de precio disponibles:")
            print(tabulate(table_data, headers=headers_table, tablefmt="rounded_grid"))

        elif r.status_code == 404:
            error = r.json().get('error', 'No hay categorías de precio disponibles.')
            print(f"\n🔍 Error ({r.status_code}): {error}")

        else:
            print(f"\n⚠️ Error inesperado ({r.status_code}): {r.text}")

    except requests.exceptions.RequestException as e:
        print(f"\n🌐 Error al conectar con el servidor: {e}")


# --------------------------------------------------------------------------
# SECCIÓN 6: OPERACIONES DE ADMINISTRACIÓN DE COCHES (SOLO MENÚ ADMIN)
# --------------------------------------------------------------------------


def registrar_coche() -> None:
    """
    Solicita datos al usuario y registra un nuevo coche a través de la API.

    Esta función es interactiva y guía al administrador a través del proceso
    de introducción de todos los detalles necesarios para un nuevo coche.
    Valida las entradas numéricas y de fecha antes de enviar una solicitud POST
    al endpoint `/coches/registrar` de la API. Requiere autenticación.

    Notes
    -----
    - La función imprime mensajes de estado y resultados directamente en la consola.
    - Modifica el estado de la aplicación si el registro es exitoso (implícitamente,
    ya que un nuevo coche existe en el backend).
    - Las validaciones de entrada se realizan en el cliente antes de la llamada API
    para mejorar la experiencia del usuario y reducir llamadas inválidas.
    """
    global TOKEN
    
    if not TOKEN:
        print("❌ No has iniciado sesión. Por favor, inicia sesión primero.")
        return
    
    print("\n🚗 --- Registrar Nuevo Coche --- 🚗")
    
    marca = input('Marca: ').strip()
    modelo = input('Modelo: ').strip()
    matricula = input('Matricula (p.ej: 0000 XXX): ').strip()
    categoria_tipo = input('Categoria tipo: ').strip()
    categoria_precio = input('Categoria precio: ').strip()
    
    try:
        año = int(input("Año (1900 - actual): ").strip())
        if año < 1900 or año > datetime.datetime.now().year:
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
            coche_data = [
                [
                    marca,
                    modelo,
                    matricula,
                    año,
                    f"€{precio_diario:.2f}",
                    categoria_tipo,
                    categoria_precio,
                    "Sí" if disponible else "No",
                    respuesta.get('id_coche', 'N/A')
                ]
            ]

            headers_table = [
                "Marca", "Modelo", "Matrícula", "Año", "Precio", 
                "Tipo", "Categoría", "Disponible", "ID Coche"
            ]

            print("\n✅ ¡Coche registrado exitosamente!")
            print(tabulate(coche_data, headers=headers_table, tablefmt="rounded_grid"))

        elif r.status_code == 400:
            error = r.json().get('error', 'Error desconocido.')
            print(f"\n❌ Error: {error}")
        elif r.status_code == 403:
            print("\n❌ Acceso denegado. Solo los administradores pueden registrar coches.")
        else:
            print(f"\n⚠️ Error inesperado: {r.status_code} - {r.text}")

    except requests.exceptions.RequestException as e:
        print(f"\n🌐 Error al conectar con el servidor: {e}")


def actualizar_coche() -> None:
    """
    Permite al administrador actualizar la matrícula de un coche existente.

    Solicita el ID del coche (formato "UIDXXX") y la nueva matrícula.
    Valida el formato de la nueva matrícula antes de enviar una solicitud PUT
    al endpoint `/coches/actualizar-matricula/{id_coche}` de la API.
    Requiere autenticación de administrador.

    Notes
    -----
    - La función imprime mensajes de estado y resultados directamente en la consola.
    """
    
    print("\n🛠️ --- Actualizar Matrícula de Coche --- 🛠️")

    id_coche = input("🆔 ID del coche a actualizar (p.ej: UID001): ").strip()
    nueva_matricula = input("🔤 Nueva matrícula (p.ej: 0000 XXX): ").strip()
    
    if not id_coche:
        print("❌ Error: El ID del coche es obligatorio.")
        return

    if not nueva_matricula:
        print("❌ Error: La nueva matrícula es obligatoria.")
        return
    
    # Validar formato de matrícula
    patron_matricula = r'^\d{4} [A-Z]{3}$'
    if not re.match(patron_matricula, nueva_matricula):
        print("❌ Error: El formato de la matrícula debe ser '0000 XXX', donde:")
        print("     - 4 dígitos seguidos de un espacio")
        print("     - 3 letras mayúsculas después del espacio")
        print("     Ejemplo: 1234 ABC")
        return
    
    headers = get_headers(auth_required=True)
    
    try:
        r: requests.Response = requests.put(
            f"{BASE_URL}/coches/actualizar-matricula/{id_coche}",
            json={"nueva_matricula": nueva_matricula},
            headers=headers
        )
        if r.status_code == 200:
            print("\n✅ ¡Matrícula actualizada exitosamente!")

            # Mostrar detalles de la actualización en formato tabla
            data_table = [[
                id_coche,
                nueva_matricula,
                "✅ Éxito"
            ]]
            headers_table = ["ID Coche", "Nueva Matrícula", "Estado"]

            print(tabulate(data_table, headers=headers_table, tablefmt="rounded_grid"))

        elif r.status_code == 400:
            error = r.json().get('error', 'No se pudo procesar la solicitud.')
            print(f"\n❌ Error ({r.status_code}): {error}")

        elif r.status_code == 403:
            print("\n❌ Acceso denegado: Solo los administradores pueden realizar esta acción.")

        elif r.status_code == 404:
            error = r.json().get('error', 'Coche no encontrado.')
            print(f"\n🔍 Error ({r.status_code}): {error}")

        else:
            print(f"\n⚠️ Error inesperado ({r.status_code}): {r.text}")

    except requests.exceptions.RequestException as e:
        print(f"\n🌐 Error al conectar con el servidor: {e}")


# --------------------------------------------------------------------------
# SECCIÓN 7: OPERACIONES DE ADMINISTRACIÓN DE USUARIOS (SOLO MENÚ ADMIN)
# --------------------------------------------------------------------------


def listar_usuarios() -> None:
    """
    Solicita y muestra una lista de todos los usuarios registrados en el sistema.

    Realiza una solicitud GET al endpoint `/listar-usuarios` de la API,
    que requiere autenticación de administrador. Si la solicitud es exitosa,
    formatea y muestra los datos de los usuarios en una tabla.

    Notes
    -----
    - La función asume que el usuario actual ya está autenticado como administrador
    (verificado antes de llamar a `menu_admin`).
    - La salida se imprime directamente en la consola.
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
    Solicita el email de un usuario y muestra sus detalles obtenidos de la API.

    Realiza una solicitud GET al endpoint `/usuarios/detalles/{email}` de la API,
    que requiere autenticación de administrador. Si la solicitud es exitosa,
    formatea y muestra los detalles del usuario en una tabla.

    Notes
    -----
    - La función asume que el usuario actual ya está autenticado como administrador.
    - La salida se imprime directamente en la consola.
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


# --------------------------------------------------------------------------
# SECCIÓN 8: OPERACIONES CON ALQUILERES
# --------------------------------------------------------------------------


def listar_alquileres() -> None:
    """
    Solicita y muestra una lista de todos los alquileres registrados en el sistema.

    Esta función es típicamente para administradores. Realiza una solicitud GET
    al endpoint `/alquileres/listar` de la API, que requiere autenticación.
    Si la solicitud es exitosa, formatea y muestra los datos de los alquileres
    en una tabla.

    Notes
    -----
    - Requiere que el usuario esté autenticado (variable global `TOKEN` debe estar definida).
    - La salida se imprime directamente en la consola.
    """

    print("\n📋 --- Listado de Alquileres --- 📋")
    headers = get_headers(auth_required=True)
    
    
    try:
        r: requests.Response = requests.get(
            f"{BASE_URL}/alquileres/listar", headers=headers)
        if r.status_code == 200:
            datos = r.json()
            alquileres = datos.get('alquileres', [])

            if not alquileres:
                print("\n🚫 No hay alquileres registrados.")
                return

            # Preparar encabezados y datos para mostrar
            headers_table = {
                'id_alquiler': 'ID',
                'id_usuario': 'ID Usuario',
                'id_coche': 'ID Coche',
                'matricula': 'Matrícula',
                'fecha_inicio': 'Inicio',
                'fecha_fin': 'Fin',
                'coste_total': 'Precio Total',
                'activo': 'Activo'
            }

            table_data = [[a[k] for k in headers_table.keys()] for a in alquileres]

            print("\n📦 Alquileres encontrados:")
            print(tabulate(table_data, headers=headers_table.values(), tablefmt="rounded_grid"))

        elif r.status_code == 403:
            print("\n❌ Acceso denegado: Solo los administradores pueden ver los alquileres.")

        elif r.status_code == 404:
            print("\n🔍 No se encontraron alquileres registrados.")

        else:
            print(f"\n⚠️ Error ({r.status_code}): {r.text}")

    except requests.exceptions.RequestException as e:
        print(f"\n🌐 Error al conectar con el servidor: {e}")


def alquiler_detalles() -> None:
    """
    Solicita el ID de un alquiler y muestra sus detalles obtenidos de la API.

    Esta función es típicamente para administradores. Realiza una solicitud GET
    al endpoint `/alquileres/detalles/{id_alquiler}` de la API, que requiere
    autenticación. Si la solicitud es exitosa, formatea y muestra los detalles
    del alquiler en una tabla.

    Notes
    -----
    - Requiere que el usuario esté autenticado.
    - La salida se imprime directamente en la consola.
    """
    
    print("\n📄 --- Detalles del Alquiler --- 📄")
    id_alquiler = input("🆔 ID del alquiler (p.ej: A001): ").strip()
    
    headers = get_headers(auth_required=True)
    
    try:
        r: requests.Response = requests.get(
            f"{BASE_URL}/alquileres/detalles/{id_alquiler}", headers=headers)
        if r.status_code == 200:
            datos = r.json()
            alquiler = datos.get('alquiler', {})

            # Datos del alquiler formateados para mostrar
            table_data = [[
                alquiler.get('id_alquiler', 'N/A'),
                alquiler.get('id_coche', 'N/A'),
                alquiler.get('id_usuario', 'N/A'),
                alquiler.get('fecha_inicio', 'N/A'),
                alquiler.get('fecha_fin', 'N/A'),
                f"€{alquiler.get('coste_total', 0):.2f}",
                "✅ Sí" if alquiler.get('activo', False) else "❌ No"
            ]]

            headers_table = ["ID Alquiler", "ID Coche", "ID Usuario", "Fecha Inicio", "Fecha Fin", "Coste Total", "Activo"]

            print("\n✅ Detalles del alquiler:")
            print(tabulate(table_data, headers=headers_table, tablefmt="rounded_grid"))

        elif r.status_code == 403:
            print("\n❌ Acceso denegado: No tienes permiso para ver este alquiler.")

        elif r.status_code == 404:
            print(f"\n🔍 No se encontró ningún alquiler con el ID '{id_alquiler}'.")

        else:
            print(f"\n⚠️ Error ({r.status_code}): {r.text}")

    except requests.exceptions.RequestException as e:
        print(f"\n🌐 Error al conectar con el servidor: {e}")


def finalizar_alquiler() -> None:
    """
    Permite a un administrador finalizar un alquiler existente por su ID.

    Solicita el ID del alquiler a finalizar. Realiza una solicitud PUT al endpoint
    `/alquileres/finalizar/{id_alquiler}` de la API, que requiere autenticación
    de administrador. Muestra una confirmación si la operación es exitosa.

    Notes
    -----
    - Requiere que el usuario esté autenticado como administrador.
    - La salida se imprime directamente en la consola.
    """
    
    print("\n✅ --- Finalizar Alquiler --- ✅")
    id_alquiler = input("🆔 ID del alquiler a finalizar (ej: A001): ").strip()
    
    if not id_alquiler:
        print("❌ Error: El ID del alquiler es obligatorio.")
        return
    
    
    headers = get_headers(auth_required=True)

    try:
        r: requests.Response = requests.put(
            f"{BASE_URL}/alquileres/finalizar/{id_alquiler}", headers=headers)
        if r.status_code == 200:
            respuesta = r.json()
            alquiler = respuesta.get('mensaje', '')
            id_coche = respuesta.get('id_coche', 'N/A')

            # Mostrar confirmación bonita con tabla
            table_data = [[
                id_alquiler,
                id_coche,
                "✅ Sí"
            ]]

            headers_table = ["ID Alquiler", "ID Coche", "Finalizado"]

            print("\n🎉 ¡Alquiler finalizado exitosamente!")
            print(tabulate(table_data, headers=headers_table, tablefmt="rounded_grid"))

        elif r.status_code == 400:
            error = r.json().get('error', 'No se pudo finalizar el alquiler.')
            print(f"\n❌ Error ({r.status_code}): {error}")

        elif r.status_code == 403:
            print("\n❌ Acceso denegado: No tienes permiso para finalizar este alquiler.")

        elif r.status_code == 404:
            print(f"\n🔍 No se encontró ningún alquiler con el ID '{id_alquiler}'.")

        else:
            print(f"\n⚠️ Error inesperado ({r.status_code}): {r.text}")

    except requests.exceptions.RequestException as e:
        print(f"\n🌐 Error al conectar con el servidor: {e}")


def ver_historial_alquileres() -> None:
    """
    Muestra el historial de alquileres de un usuario específico, identificado por su email.

    Esta función es accesible tanto por clientes (para ver su propio historial)
    como por administradores (para ver el historial de cualquier usuario).
    Solicita el email del usuario cuyo historial se desea consultar. Realiza una
    solicitud GET al endpoint `/alquileres/historial/{email}` de la API, que
    requiere autenticación. Muestra los alquileres en una tabla.

    Notes
    -----
    - Requiere que el usuario esté autenticado (TOKEN global).
    - La autorización (si el usuario puede ver el historial del email solicitado)
    la maneja el backend.
    - La salida se imprime directamente en la consola.
    """
    global TOKEN  # Acceder a la variable global TOKEN

    # Verificar si hay un token JWT válido
    if not TOKEN:
        print("❌ No has iniciado sesión. Por favor, inicia sesión primero.")
        return

    print("\n📦 --- Historial de Alquileres --- 📦")
    email = input("📧 Email del usuario: ").strip()

    # Validar que el email no esté vacío
    if not email:
        print("❌ Error: El email es obligatorio.")
        return

    # Obtener los headers con el token JWT
    headers = get_headers(auth_required=True)

    # Realizar la solicitud GET
    try:
        r = requests.get(
            f'{BASE_URL}/alquileres/historial/{email}',  # Incluir el email en la URL
            headers=headers  # Incluir los headers con el token JWT
        )
        if r.status_code == 200:
            datos = r.json()
            alquileres = datos.get('alquileres', [])

            if not alquileres:
                print(f"\n🚫 No se encontró historial de alquileres para '{email}'.")
                return

            # Mostrar datos en formato tabla
            headers_table = [
                "ID Alquiler", "ID Coche", "Matrícula", 
                "Fecha Inicio", "Fecha Fin", "Coste Total", "Activo"
            ]

            table_data = [[
                a.get('id_alquiler', 'N/A'),
                a.get('id_coche', 'N/A'),
                a.get('matricula', 'N/A'),
                a.get('fecha_inicio', 'N/A'),
                a.get('fecha_fin', 'N/A'),
                f"€{a.get('coste_total', 0):.2f}",
                "✅ Sí" if a.get('activo') else "❌ No"
            ] for a in alquileres]

            print(f"\n📅 Historial de alquileres para {email}:")
            print(tabulate(table_data, headers=headers_table, tablefmt="rounded_grid"))

        elif r.status_code == 403:
            print("\n❌ Acceso denegado: No tienes permiso para ver este historial.")

        elif r.status_code == 404:
            error = r.json().get('error', 'Usuario no encontrado.')
            print(f"\n🔍 No se encontró ningún historial de alquileres para '{email}'.")
            print(f"Mensaje del servidor: {error}")

        elif r.status_code == 500:
            try:
                respuesta = r.json()
                mensaje_error = respuesta.get('error', 'Error desconocido')
            except ValueError:
                mensaje_error = r.text  # Si no es JSON, muestra el texto plano

            print(f"\n🚨 Error interno del servidor (500):")
            print(f"❌ Mensaje del servidor: {mensaje_error}")
            print("📢 Revisa los datos introducidos o contacta con el administrador.")

        else:
            print(f"\n⚠️ Error inesperado ({r.status_code}): {r.text}")

    except requests.exceptions.RequestException as e:
        print(f"\n🌐 Error al conectar con el servidor: {e}")


def alquilar_coche() -> None:
    """
    Permite al usuario (invitado o cliente) alquilar un coche y descargar la factura PDF.

    Solicita matrícula, fechas de inicio/fin y opcionalmente un email.
    Envía una solicitud POST al endpoint `/alquilar-coche` de la API.
    Si es exitoso (200 OK y la respuesta es un PDF), pide al usuario dónde guardar
    la factura.

    Notes
    -----
    - Utiliza Tkinter para el diálogo de "Guardar como".
    - La lógica de autenticación (si el usuario es un cliente logueado o un invitado)
    la maneja el backend basado en si se envía un token y/o un email.
    """
    print("\n🚗 --- Alquilar Coche --- 🚗")
    matricula = input("🔤 Matrícula del coche (p.ej: 0000 XXX): ").strip()
    fecha_inicio = input("📅 Fecha de inicio (YYYY-MM-DD): ").strip()
    fecha_fin = input("📆 Fecha de fin (YYYY-MM-DD): ").strip()
    email = input("📧 Email del usuario (dejar en blanco para invitado): ").strip() or None

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
                print("✅Factura descargada exitosamente.")
                print("\n🎉 ¡Alquiler realizado exitosamente!")
            else:
                print("🚫 Descarga cancelada por el usuario.")
        elif r.status_code == 200 and 'application/json' in r.headers.get('Content-Type', ''):
            # Si el servidor responde con JSON en lugar de PDF (por ejemplo, error o info)
            respuesta = r.json()
            error = respuesta.get('error')
            if error:
                print(f"\n❌ Error del servidor: {error}")
            else:
                print(f"\n📦 Respuesta del servidor: {respuesta}")

        elif r.status_code == 400:
            error = r.json().get('error', 'Datos incorrectos.')
            print(f"\n❌ Error ({r.status_code}): {error}")

        elif r.status_code == 403:
            print("\n❌ Acceso denegado: Los administradores no pueden alquilar coches.")

        else:
            print(f"\n⚠️ Error inesperado ({r.status_code}): {r.text}")

    except requests.exceptions.RequestException as e:
        print(f"\n🌐 Error al conectar con el servidor: {e}")


# --------------------------------------------------------------------------
# SECCIÓN 9: PUNTO DE ENTRADA PRINCIPAL
# --------------------------------------------------------------------------


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