""" Ejemplos de la API"""
import requests
import jwt
import tkinter as tk
from tkinter import filedialog


BASE_URL = "http://127.0.0.1:5000"  # Cambiar por CarlosBatlles.pythonanywhere.com cuando queramos probar con la webapp
TOKEN = None
ROL = None


def get_headers(auth_required=False):
    """Devuelve los headers necesarios para las solicitudes HTTP."""
    headers = {"Content-Type": "application/json"}
    if auth_required and TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    return headers


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
        print("4. Cerrar sesion")
        print("5. Salir")
        opcion = input("Selecciona una opción: ")

        if opcion == "1":
            login()
            if ROL:
                mostrar_menu_por_rol(ROL)
        elif opcion == "2":
            signup()
        elif opcion == "3":
            entrar_como_invitado()
        elif opcion == "4":
            logout()
        elif opcion == "5":
            print("Saliendo...")
            break
        else:
            print("Opción no válida. Inténtalo de nuevo.")


def menu_admin():
    """Menú para administradores."""
    while True:
        print("\n--- Menú de Administrador ---")
        print("1. Registrar coche")
        print("2. Eliminar coche")
        print("3. Listar usuarios")
        print('4. Obtener detalles usuario')
        print('5. Actualizar datos coches')
        print('6. Listar alquileres')
        print('7. Detalle especifico de alquiler')
        print('8. Finalizar alquiler')
        print("9. Volver al menú principal")
        opcion = input("Selecciona una opción: ")

        if opcion == "1":
            registrar_coche()
        elif opcion == "2":
            eliminar_coche()
        elif opcion == "3":
            listar_usuarios()
        elif opcion == "4":
            obtener_detalles_usuario()
        elif opcion == '5':
            actualizar_datos_coche()
        elif opcion == '6':
            listar_alquileres()
        elif opcion == '7':
            detalles_alquiler()
        elif opcion == '8':
            finalizar_alquiler()
        elif opcion == '9':
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
        print('4. Datos usuario')
        print('5. Actualizar datos usuario')
        print('6. Obtener detalles de un coche')
        print('7. Categorias de coche')
        print('8. Categorias de precio')
        print("9. Volver al menú principal")
        opcion = input("Selecciona una opción: ")

        if opcion == "1":
            alquilar_coche()
        elif opcion == "2":
            ver_historial_alquileres()
        elif opcion == "3":
            buscar_coches_disponibles()
        elif opcion == "4":
            datos_usuario()
        elif opcion == '5':
            actualizar_datos()
        elif opcion == '6':
            detalles_coche()
        elif opcion == '7':
            categoria_coche()
        elif opcion == '8':
            categoria_precio()
        elif opcion == '9':
            break
        else:
            print("Opción no válida. Inténtalo de nuevo.")


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


def signup():
    user = input("Usuario nuevo: ")
    passwd = input("Contraseña: ")
    r = requests.post(f"{BASE_URL}/signup", json={"user": user, "passwd": passwd})
    print("Respuesta:", r.status_code, r.json())


def mostrar_menu_por_rol(rol):
    """Muestra un menú específico según el rol del usuario."""
    print(f"\n--- Menú para {rol.capitalize()} ---")
    if rol == "admin":
        menu_admin()
    elif rol == "cliente":
        menu_cliente()
    else:
        print("Rol no reconocido.")


def entrar_como_invitado():
    """Entrar como invitado."""
    global ROL
    ROL = "invitado"
    print("\nHas entrado como invitado.")
    menu_cliente()  # Los invitados pueden usar el menú de cliente


def registrar_coche():
    marca = input('Marca: ')
    modelo = input('Modelo: ')
    matricula = input('Matricula: ')
    categoria_tipo = input('Categoria: ')
    categoria_precio = input('Categoria precio: ')
    año = input('Año:')
    precio_diario = float(input('Precio diario: '))
    kilometraje = int(input('Kilometraje: '))
    color = input('Color: ')
    combustible = input('Combustible: ')
    cv = int(input('Caballos: '))
    plazas = int(input('Plazas: '))
    disponible = True
    try:
        r = requests.post(f'{BASE_URL}/coches/registrar',
                          json={'marca': marca, 'modelo': modelo, 'matricula': matricula,
                                'categoria tipo': categoria_tipo, 'categoria precio': categoria_precio, 'año': año,
                                'precio diario': precio_diario, 'kilometraje': kilometraje, 'color': color,
                                'combustible': combustible, 'cv': cv, 'plazas': plazas, 'disponible': disponible})
        print('Respuesta: ', r.status_code, r.json())
    except requests.exceptions.RequestException as e:
        print(f'Error al registrar el coche: {e}')


def eliminar_coche():
    id_coche = input('Id coche: ')
    try:
        r = requests.delete(f'{BASE_URL}/coches/eliminar/<string:id_coche>', json={'id coche': id_coche})
        print('Respuesta: ', r.status_code, r.json())
    except requests.exceptions.RequestException as e:
        print(f'Error al eliminar el coche: {e}')


def buscar_coches_disponibles():
    categoria_precio = input('Categoria precio: ')
    categoria_tipo = input('Categoria tipo: ')
    marca = input('Marca: ')
    modelo = input('Modelo: ')

    try:
        r = requests.get(f'{BASE_URL}/coches-disponibles',
                         json={'categoria tipo': categoria_tipo, 'categoria precio': categoria_precio, 'marca': marca,
                               'modelo': modelo})
        print('Respuesta: ', r.status_code, r.json())
    except requests.exceptions.RequestException as e:
        print(f'Error al eliminar el coche: {e}')


def ver_historial_alquileres():
    email = input('Email: ')

    try:
        r = requests.get(f'{BASE_URL}/alquileres/historial/<string:email>', json={'email': email})
        print('Respuesta: ', r.status_code, r.json())
    except requests.exceptions.RequestException as e:
        print(f'Error al eliminar el coche: {e}')

def alquilar_coche():
    print("\n--- Alquilar Coche ---")
    matricula = input("Matrícula del coche: ").strip()
    fecha_inicio = input("Fecha de inicio (YYYY-MM-DD): ").strip()
    fecha_fin = input("Fecha de fin (YYYY-MM-DD): ").strip()
    email = input("Email del usuario (dejar en blanco para invitado): ").strip() or None

    # Preparar los datos para la solicitud
    data = {
        "matricula": matricula,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
    }
    if email:
        data["email"] = email

    # Enviar la solicitud POST al endpoint /alquilar-coche
    r = requests.post(f"{BASE_URL}/alquilar-coche", json=data)

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




def main():
    """Función principal."""
    mostrar_menu_principal()







