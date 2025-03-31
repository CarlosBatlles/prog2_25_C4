
'''Clase Usuario para representar a los clientes y sus datos'''

class Usuario:
    def __init__(self, id_usuario, nombre, email, tipo):
        self.id_usuario = id_usuario
        self.nombre = nombre
        self.email = email
        self.tipo = tipo

    def get_info(self):
        '''Devuelve un string con los detalles del usuario'''
        return (f"Usuario: {self.nombre}\n"
                f"(ID: {self.id_usuario})\n"
                f"Email: {self.email}\n"
                f"Tipo: {self.tipo}")