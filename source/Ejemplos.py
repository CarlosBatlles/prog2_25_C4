""" Ejemplos de la API"""
from os import login_tty

import requests
import jwt

BASE_URL="http://127.0.0.1:5050" # Cambiar por CarlosBatlles.pythonanywhere.com cuando queramos probar con la webapp
TOKEN = None


def get_headers(auth_required=False):
    """Devuelve los headers necesarios para las solicitudes HTTP."""
    headers = {"Content-Type": "application/json"}
    if auth_required and TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    return headers

def login():
    """Iniciar sesión y obtener el token JWT."""
    global TOKEN, ROL
    print("\n--- Iniciar Sesión ---")
    email = input("Correo electrónico: ").strip()
    contraseña = input("Contraseña: ").strip()

    # Validar campos obligatorios
    if not email or not contraseña:
        print("El correo electrónico y la contraseña son obligatorios.")
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
            print("Inicio de sesión exitoso!")
            print(f"Rol: {ROL}")
        elif r.status_code == 400:
            print(f"Error: {r.json().get('error')}")
        elif r.status_code == 401:
            print("Credenciales inválidas. Inténtalo de nuevo.")
        else:
            print(f"Error inesperado: {r.status_code} - {r.text}")

    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con el servidor: {e}")

def decode_token(token):
    """Decodifica el token JWT para extraer las claims."""
    try:
        # Decodificar el token sin verificar la firma (solo para fines educativos)
        decoded = jwt.decode(token, options={"verify_signature": False})
        return decoded
    except Exception as e:
        print(f"Error al decodificar el token: {e}")
        return {}

def mostrar_menu_principal():
    """Muestra el menú principal."""
    while True:
        print("\n--- Menú Principal ---")
        print("1. Iniciar sesión")
        print("2. Registrarse")
        print("3. Entrar como invitado")
        print("4. Salir")
        opcion = input("Selecciona una opción: ")

        if opcion == "1":
            login()
            if ROL:
                mostrar_menu_por_rol(ROL)
        elif opcion == "2":
            registrar_usuario()
        elif opcion == "3":
            entrar_como_invitado()
        elif opcion == "4":
            print("Saliendo...")
            break
        else:
            print("Opción no válida. Inténtalo de nuevo.")

def mostrar_menu_por_rol(rol):
    """Muestra un menú específico según el rol del usuario."""
    print(f"\n--- Menú para {rol.capitalize()} ---")
    if rol == "admin":
        menu_admin()
    elif rol == "cliente":
        menu_cliente()
    else:
        print("Rol no reconocido.")

def menu_admin():
    """Menú para administradores."""
    while True:
        print("\n--- Menú de Administrador ---")
        print("1. Registrar coche")
        print("2. Eliminar coche")
        print("3. Listar usuarios")
        print("4. Volver al menú principal")
        opcion = input("Selecciona una opción: ")

        if opcion == "1":
            registrar_coche()
        elif opcion == "2":
            eliminar_coche()
        elif opcion == "3":
            listar_usuarios()
        elif opcion == "4":
            break
        else:
            print("Opción no válida. Inténtalo de nuevo.")

def menu_cliente():
    """Menú para clientes."""
    while True:
        print("\n--- Menú de Cliente ---")
        print("1. Alquilar coche")
        print("2. Ver historial de alquileres")
        print("3. Buscar coches disponibles")
        print("4. Volver al menú principal")
        opcion = input("Selecciona una opción: ")

        if opcion == "1":
            alquilar_coche()
        elif opcion == "2":
            ver_historial_alquileres()
        elif opcion == "3":
            buscar_coches_disponibles()
        elif opcion == "4":
            break
        else:
            print("Opción no válida. Inténtalo de nuevo.")

def entrar_como_invitado():
    """Entrar como invitado."""
    global ROL
    ROL = "invitado"
    print("\nHas entrado como invitado.")
    menu_cliente()  # Los invitados pueden usar el menú de cliente

def main():
    """Función principal."""
    mostrar_menu_principal()


def menu_principal():
    print("\n Bienvenido a RentAcar:")
    print("1. Iniciar sesión como Cliente")
    print("2. Iniciar sesión como Administrador")
    print("3. Entrar como invitado")
    print("0. Salir")

acciones_principales = {
    "1": iniciar_sesion_cliente,
    "2": iniciar_sesion_admin,
    "3": entrar_como_invitado,
}

def menu_cliente():
    print("\n Menú Cliente:")
    print("1. Buscar Coches")
    print("2. Alquilar Coches")
    print("3. Ver Historial de Alquileres")
    print("0. Volver al Menú Principal")

acciones_cliente = {
    "1": registro_usuario()
    "2": iniciar_sesion()
    "3": ver_detalles_usuario()
    "4": actualizar_contraseña_usuario()
    "5": alquilar_coche()
    "6": ver_detalles_alquiler_usuario()
    "7": finalizar_alquiler_usuario()
}

def menu_admin():
    print("\n Menú Administrador:")
    print("1. Gestionar coches")
    print("2. Consultar Bases de Datos")
    print("3. Generar informes")
    print("0. Volver al Menú Principal")

acciones_admin = {

"1": eliminar_usuario,
"2": listar_usuarios,
"3": registrar_coche,
"4": actualizar_coche,
"5": eliminar_coche,
"6": listar_alquileres,
"7": ver_detalles_alquiler_admin,
"8": finalizar_alquiler_admin,

}

acciones_invitado = {
    "1": entrar_como_invitado,
    "2": signup,
    # resto de funciones relacionadas con los invitados
}
# Funciones de autenticación y de la API

def login():
    global Token
    user = input("Usuario: ")
    passwd = input("Contraseña: ")
    r = requests.get(f"{BASE_URL}/login", params={"user": user, "passwd": passwd})
    print("Respuesta:", r.status_code, r.json())
    if r.status_code == 200:
        Token = r.json()["access_token"]
        print(f"Bienvenido, {user}!")
    else:
        print("Error al iniciar sesión.")

def signup():
    user = input("Usuario nuevo: ")
    passwd = input("Contraseña: ")
    r = requests.post(f"{BASE_URL}/signup", json={"user": user, "passwd": passwd})
    print("Respuesta:", r.status_code, r.json())

def iniciar_sesion_cliente():
    print("Iniciando sesión como Cliente...")
    login()
    while True:
        menu_cliente()
        opcion = input("Elige una opción: ")
        if opcion == "0":
            break
        accion = acciones_cliente.get(opcion)
        if accion:
            accion()
        else:
            print("Opción no válida.")

def iniciar_sesion_admin():
    print("Iniciando sesión como Administrador...")
    login()
    while True:
        menu_admin()
        opcion = input("Elige una opción: ")
        if opcion == "0":
            break
        accion = acciones_admin.get(opcion)
        if accion:
            accion()
        else:
            print("Opción no válida.")

def entrar_como_invitado():
    pass

# Resto de endpoints

if __name__ == "__main__":
    while True:
        menu_principal()
        opcion = input("Elige una opción: ")
        if opcion == "0":
            print("👋 Saliendo...")
            break
        accion = acciones_principales.get(opcion)
        if accion:
            accion()
        else:
            print("Opción no válida.")