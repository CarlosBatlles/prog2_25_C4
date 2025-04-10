
'''Clase Usuario para representar a los clientes y sus datos'''
from werkzeug.security import check_password_hash
import re
class Usuario:
    
    TIPOS_USUARIOS = ['Cliente', 'Admin']
    
    def __init__(self, id_usuario, nombre, email, tipo,contraseña_hasheada):
        
        if not nombre:
            raise ValueError('El nombre no puede estar vacio')
        self.validar_email(email)
        if tipo not in self.TIPOS_USUARIOS:
            raise ValueError(f'El tipo: {tipo} no esta disponible: Opciones: {self.TIPOS_USUARIOS}')
        
        self.id_usuario = id_usuario
        self.nombre = nombre
        self.email = email
        self.tipo = tipo
        self.contraseña = contraseña_hasheada
        self.historial_alquileres = []

    @staticmethod
    def validar_email(self,email):
        """Valida que el email tenga un formato básico correcto."""
        patron = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(patron, email):
            raise ValueError("El email no tiene un formato válido.")
    
    def verificar_contraseña(self,contraseña):
        '''Verifica si la contraseña que le pasamos coincide con la almacenada'''
        return check_password_hash(self,contraseña,contraseña)
    
    def get_info(self):
        """Devuelve un string con los detalles del usuario."""
        return (f"Usuario: {self.nombre}\n"
                f"(ID: {self.id_usuario})\n"
                f"Email: {self.email}\n"
                f"Tipo: {self.tipo}\n"
                f"Historial de Alquileres: {self.historial_alquileres}")

    def __str__(self):
        """Representación legible del usuario."""
        return self.get_info()