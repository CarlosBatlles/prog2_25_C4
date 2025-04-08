""" Ejemplos de la API"""

def menu():
    print("\n Bienvenido a RentAcar:")
    print("1. Login")
    print("2. Signup")
    print("3. Entrar como invitado")
    print("4. Buscar Coches (como cliente)")
    print("5. Alquilar Coches (como cliente)")
    print("6. Ver Historial de Alquileres (como cliente)")
    print("7. Gestionar coches (como admin)")
    print("8. Consultar Bases de Datos (como admin)")
    print("9. Generar informes (como admin)")
    print("10. Buscar Coches (como invitado)")
    print("11. Alquilar Coches (como invitado)")
    print("0. Salir")

# ----------------------------
# Bucle principal
# ----------------------------
acciones = {
    "1": login,
    "2": signup,
    "3": entrar_como_invitado,
    "4": buscar_coches_cliente,
    "5": alquilar_coches_cliente,
    "6": ver_historial_alquiler_cliente,
    "7": gestionar_coches_admin,
    "8": consultar_base_datos_admin,
    "9": generar_informes_admin,
    "10": buscar_coches_invitado,
    "11": alquilar_coches_invitado,
}

if __name__ == "__main__":
    while True:
        menu()
        opcion = input("Elige una opción: ")
        if opcion == "0":
            print("👋 Saliendo...")
            break
        accion = acciones.get(opcion)
        if accion:
            accion()
        else:
            print("Opción no válida.")