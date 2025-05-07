
'''Clase Usuario para representar a los clientes y sus datos'''
import hashlib
import re
import pandas as pd
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
    def hash_contraseña(self, contraseña: str) -> str:
        """
        Genera un hash SHA-256 de la contraseña proporcionada.

        Parameters
        ----------
        contraseña : str
            La contraseña que se desea hashear.

        Returns
        -------
        str
            Un hash SHA-256 de la contraseña en formato hexadecimal.

        Notes
        -----
        Este método utiliza la biblioteca hashlib para generar un hash seguro de la contraseña.
        El resultado es una cadena hexadecimal de 64 caracteres.
        """
        return hashlib.sha256(contraseña.encode()).hexdigest()
    
    
    @staticmethod
    def es_email_valido(email: str) -> bool:
        """
        Verifica si un correo electrónico es válido utilizando una expresión regular.

        Parameters
        ----------
        email : str
            El correo electrónico que se desea validar.

        Returns
        -------
        bool
            True si el correo electrónico es válido, False en caso contrario.

        Notes
        -----
        Esta función utiliza una expresión regular para validar el formato del correo electrónico.
        El patrón utilizado sigue las reglas estándar para correos electrónicos válidos.
        """
        patron = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(patron, email) is not None
    
    
    @staticmethod
    def registrar_usuario(
        empresa, 
        nombre: str, 
        tipo: str, 
        email: str, 
        contraseña: str
    ) -> bool:
        """
        Registra un nuevo usuario en el sistema.

        Este método verifica si el correo electrónico ya está registrado, hashea la contraseña 
        y guarda los datos del usuario en el archivo CSV correspondiente.

        Parameters
        ----------
        empresa : Empresa
            Instancia de la clase Empresa para cargar/guardar datos.
        nombre : str
            Nombre completo del usuario.
        tipo : str
            Tipo de usuario (por ejemplo, 'cliente', 'admin').
        email : str
            Correo electrónico del usuario. Debe ser único y válido.
        contraseña : str
            Contraseña del usuario. Se almacenará como un hash seguro.

        Returns
        -------
        bool
            True si el usuario se registró correctamente.

        Raises
        ------
        ValueError
            Si algún campo obligatorio está vacío, si el correo electrónico no es válido 
            o si el correo electrónico ya está registrado.
        Exception
            Si ocurre un error al guardar los cambios en el archivo CSV.

        Notes
        -----
        - El correo electrónico debe ser único en el sistema.
        - La contraseña se almacena como un hash SHA-256 para mayor seguridad.
        """
        # Cargar los usuarios actuales
        df_usuarios = empresa.cargar_usuarios()
        if df_usuarios is None or df_usuarios.empty:
            df_usuarios = pd.DataFrame(columns=['id_usuario', 'nombre', 'tipo', 'email', 'contraseña'])

        # Validaciones de campos obligatorios
        if not all([nombre, tipo, email, contraseña]):
            raise ValueError("Debes rellenar todos los campos.")

        if not Usuario.es_email_valido(email):
            raise ValueError("El correo electrónico no es válido.")

        if email in df_usuarios['email'].values:
            raise ValueError("El correo electrónico ya está registrado.")

        # Generar un ID único para el usuario
        id_user = empresa.generar_id_usuario()

        # Hashear la contraseña
        contraseña_hasheada = Usuario.hash_contraseña(contraseña)

        # Crear un diccionario con los datos del nuevo usuario
        new_user = {
            'id_usuario': id_user,
            'nombre': nombre,
            'tipo': tipo,
            'email': email,
            'contraseña': contraseña_hasheada,
        }

        # Crear un DataFrame con el nuevo usuario y actualizar el archivo CSV
        df_nuevo_usuario = pd.DataFrame([new_user])
        df_actualizado = pd.concat([df_usuarios, df_nuevo_usuario], ignore_index=True)

        try:
            empresa._guardar_csv('clientes.csv', df_actualizado)
            return True
        except Exception as e:
            raise ValueError(f"Error al guardar el usuario en el archivo CSV: {e}")
        
        
    @staticmethod
    def actualizar_usuario(empresa, email: str, nueva_contraseña: str = None) -> bool:
        """
        Actualiza los datos de un usuario existente.
        Solo permite cambiar la contraseña del usuario autenticado.

        Parameters
        ----------
        empresa : Empresa
            Instancia de la clase Empresa para cargar/guardar datos.
        email : str
            Correo electrónico del usuario cuya información se desea actualizar.
        nueva_contraseña : str, optional
            La nueva contraseña que se asignará al usuario. Si no se proporciona, no se realizará ninguna actualización.

        Returns
        -------
        bool
            True si la actualización se realizó correctamente.

        Raises
        ------
        ValueError
            Si el correo electrónico no está registrado o si ocurre un error al guardar los cambios.
        """
        # Cargar los usuarios actuales
        df_usuarios = Usuario.cargar_usuarios(empresa)
        if df_usuarios is None:
            raise ValueError("No se pudieron cargar los usuarios. Revisa el archivo CSV.")

        # Verificar si el email existe en el DataFrame
        if email not in df_usuarios['email'].values:
            raise ValueError(f"El correo electrónico {email} no está registrado.")

        # Si se proporciona una nueva contraseña, validarla y actualizarla
        if nueva_contraseña:
            # Hashear la nueva contraseña
            contraseña_hasheada = Usuario.hash_contraseña(nueva_contraseña)

            # Actualizar la contraseña en el DataFrame
            df_usuarios.loc[df_usuarios['email'] == email, 'contraseña'] = contraseña_hasheada

            # Guardar los cambios en el archivo CSV
            try:
                Usuario.guardar_usuarios(empresa, df_usuarios)
                print(f"La contraseña del usuario con email {email} ha sido actualizada exitosamente.")
            except Exception as e:
                raise ValueError(f"Error al guardar los cambios en el archivo CSV: {e}")

        return True
    
    
    @staticmethod
    def dar_baja_usuario(empresa, email: str) -> bool:
        """
        Elimina un usuario del sistema basándose en su correo electrónico.

        Este método verifica si el correo electrónico existe en el sistema y elimina 
        al usuario correspondiente del archivo CSV.

        Parameters
        ----------
        empresa : Empresa
            Instancia de la clase Empresa para cargar/guardar datos.
        email : str
            El correo electrónico del usuario que se desea eliminar.

        Returns
        -------
        bool
            True si el usuario se eliminó correctamente.

        Raises
        ------
        ValueError
            Si no se pueden cargar los usuarios o si el correo electrónico no está registrado.
        Exception
            Si ocurre un error al guardar los cambios en el archivo CSV.

        Notes
        -----
        - Antes de eliminar el usuario, se verifica que el correo electrónico exista en el sistema.
        - El método utiliza el archivo CSV como fuente de datos, por lo que los cambios son persistentes.
        """
        # Cargar los usuarios actuales
        df_usuarios = Usuario.cargar_usuarios(empresa)
        if df_usuarios is None:
            raise ValueError("No se pudieron cargar los usuarios. Revisa el archivo CSV.")

        # Verificar si el email existe en el DataFrame
        if email not in df_usuarios['email'].values:
            raise ValueError("El correo que has introducido no está registrado.")

        # Filtrar el DataFrame para excluir al usuario con el email proporcionado
        df_actualizado = df_usuarios[df_usuarios['email'] != email]

        # Guardar los cambios usando el método auxiliar
        try:
            Usuario.guardar_usuarios(empresa, df_actualizado)
            return True
        except Exception as e:
            raise ValueError(f"Error al guardar los cambios en el archivo CSV: {e}")
        
        
    @staticmethod
    def iniciar_sesion(empresa, email: str, contraseña: str) -> bool:
        """
        Verifica si un usuario con el correo electrónico y contraseña dados existe en la base de datos.

        Parameters
        ----------
        empresa : Empresa
            Instancia de la clase Empresa para cargar los datos.
        email : str
            Correo electrónico del usuario.
        contraseña : str
            Contraseña proporcionada por el usuario.

        Returns
        -------
        bool
            True si las credenciales son válidas.

        Raises
        ------
        ValueError
            Si no se pueden cargar los usuarios o si el correo electrónico no está registrado.
        Exception
            Si ocurre un error inesperado durante el proceso.

        Notes
        -----
        - La contraseña se compara en formato hasheado para mayor seguridad.
        - El método utiliza el archivo CSV como fuente de datos, por lo que los cambios son persistentes.
        """
        # Cargar los usuarios
        df_usuarios = Usuario.cargar_usuarios(empresa)
        if df_usuarios is None or df_usuarios.empty:
            raise ValueError("No se pudieron cargar los usuarios. Revisa el archivo CSV.")

        # Buscar el usuario por correo electrónico
        usuario = df_usuarios[df_usuarios['email'] == email]
        if usuario.empty:
            raise ValueError(f"No se encontró ningún usuario con el correo: {email}.")

        # Obtener la contraseña almacenada y compararla con la contraseña hasheada
        contraseña_almacenada = usuario.iloc[0]['contraseña']
        contraseña_hasheada = Usuario.hash_contraseña(contraseña)

        if contraseña_almacenada != contraseña_hasheada:
            raise ValueError("Contraseña incorrecta.")

        return True
    
    
    @staticmethod
    def obtener_historial_alquileres(empresa, email: str) -> list[dict]:
        """
        Obtiene el historial de alquileres de un usuario específico basándose en su email.

        Parameters
        ----------
        empresa : Empresa
            Instancia de la clase Empresa para cargar los datos.
        email : str
            Correo electrónico del usuario cuyo historial de alquileres se desea obtener.

        Returns
        -------
        list[dict]
            Una lista de diccionarios que contiene los detalles de los alquileres del usuario.

        Raises
        ------
        ValueError
            Si no hay alquileres registrados o si no se encuentran alquileres para el usuario especificado.
        Exception
            Si ocurre un error inesperado durante el proceso.

        Notes
        -----
        - El método utiliza el archivo CSV como fuente de datos, por lo que los cambios son persistentes.
        - Si el usuario no tiene alquileres registrados, se lanza una excepción.
        """
        # Cargar los usuarios y verificar si el email existe
        df_usuarios = Usuario.cargar_usuarios(empresa)
        if df_usuarios is None or df_usuarios.empty:
            raise ValueError("No se pudieron cargar los usuarios.")

        # Verificar si el email existe en el sistema
        if email not in df_usuarios['email'].values:
            raise ValueError(f"El usuario con email {email} no está registrado.")

        # Obtener el ID del usuario a partir del email
        id_usuario = df_usuarios[df_usuarios['email'] == email].iloc[0]['id_usuario']

        # Cargar los alquileres
        df_alquileres = empresa.cargar_alquileres()
        if df_alquileres is None or df_alquileres.empty:
            raise ValueError("No hay alquileres registrados.")

        # Filtrar los alquileres por el ID del usuario
        alquileres_usuario = df_alquileres[df_alquileres['id_usuario'] == id_usuario]

        # Si no hay alquileres, lanzar una excepción
        if alquileres_usuario.empty:
            raise ValueError(f"No se encontraron alquileres para el usuario con email {email}.")

        # Convertir el DataFrame a una lista de diccionarios
        return alquileres_usuario.to_dict(orient='records')