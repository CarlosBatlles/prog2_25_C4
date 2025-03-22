
# clase Usuario para crear usuarios, definir sus propiedades y demas

class Usuario():
    def __init__(self, id_usuario: str, nombre: str, email: str, tipo: str):
        self.id_usuario = id_usuario
        self.nombre = nombre
        self.email = email
        self.tipo = tipo
        
    def get_info(self):
        ''' devuelve la informacion del usuario
        "Usuario: nombre (ID: id_usuario), Email: email, Tipo: tipo"'''
        pass