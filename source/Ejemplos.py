""" Ejemplos de la API"""
from os import login_tty

import requests

BASE_URL="http://127.0.0.1:5050" # Cambiar por CarlosBatlles.pythonanywhere.com cuando queramos probar con la webapp
Token=None

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