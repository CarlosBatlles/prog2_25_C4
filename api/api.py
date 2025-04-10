import sys
import os
from flask import Flask, request, jsonify, make_response
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from datetime import *

# Agrega el directorio raíz del proyecto al PATH (para que encuentre `source`)
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

# Ahora la importación debería funcionar
from source.empresa import Empresa

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "grupo_4!"
jwt = JWTManager(app)
token_blocklist = set()

empresa = Empresa(nombre='RentAcar')

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return jti in token_blocklist

# ---------------------------------------
# ENDPOINTS RELACIONADOS CON BUSQUEDAS
# ---------------------------------------

@app.route('/signup', methods=['POST'])
def signup() -> tuple[dict, int]:
    """
    Endpoint para registrar un nuevo usuario en el sistema.

    Este endpoint permite registrar un nuevo usuario con un nombre, correo electrónico, 
    contraseña y tipo de usuario. El tipo de usuario puede ser "admin" o "cliente". 
    Si no se especifica, el tipo predeterminado será "cliente".

    Methods
    -------
    POST
        Registra un nuevo usuario en el sistema.

    Parameters
    ----------
    nombre : str
        Nombre del usuario.
    tipo : str, optional
        Tipo de usuario ("admin" o "cliente"). Por defecto es "cliente".
    email : str
        Correo electrónico del usuario.
    contraseña : str
        Contraseña del usuario (se almacenará como hash).

    Returns
    -------
    JSON
        Un objeto JSON con la siguiente estructura:
        {
            "mensaje": "Usuario registrado exitosamente"
        }

    Raises
    ------
    HTTP 400 Bad Request
        Si faltan campos obligatorios, el correo electrónico no es válido o el tipo de usuario no es correcto.
    HTTP 500 Internal Server Error
        Si ocurre un error inesperado durante la ejecución.
    """
    data = request.json
    nombre = data.get('nombre')
    tipo = data.get('tipo', 'cliente')  # Por defecto aplicamos cliente
    email = data.get('email')
    contraseña = data.get('contraseña')

    # Validar campos obligatorios
    if not nombre or not email or not contraseña:
        return jsonify({'error': 'Todos los campos son obligatorios'}), 400

    # Validar el correo electrónico
    if not empresa.es_email_valido(email):
        return jsonify({'error': 'El correo electrónico no es válido'}), 400

    # Validar el tipo de usuario
    if tipo not in ['admin', 'cliente']:
        return jsonify({'error': 'El tipo de usuario debe ser "admin" o "cliente"'}), 400

    try:
        # Registrar el usuario
        if empresa.registrar_usuario(nombre=nombre, tipo=tipo, email=email, contraseña=contraseña):
            return jsonify({'mensaje': 'Usuario registrado exitosamente'}), 201
        else:
            return jsonify({'error': 'No se pudo registrar el usuario'}), 500
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@app.route('/login', methods=['POST'])
def login() -> tuple[dict, int]:
    """
    Endpoint para iniciar sesión en el sistema.

    Este endpoint permite a un usuario iniciar sesión proporcionando su correo electrónico 
    y contraseña. Si las credenciales son válidas, se genera un token JWT que incluye el 
    rol del usuario (por ejemplo, "admin" o "cliente").

    Methods
    -------
    POST
        Inicia sesión en el sistema.

    Parameters
    ----------
    email : str
        Correo electrónico del usuario.
    contraseña : str
        Contraseña del usuario.

    Returns
    -------
    JSON
        Un objeto JSON con la siguiente estructura:
        {
            "mensaje": "Inicio de sesion exitoso",
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        }

    Raises
    ------
    HTTP 400 Bad Request
        Si faltan campos obligatorios o el correo electrónico no es válido.
    HTTP 401 Unauthorized
        Si las credenciales son inválidas.
    HTTP 500 Internal Server Error
        Si ocurre un error inesperado durante la ejecución.
    """
    data = request.json
    email = data.get('email')
    contraseña = data.get('contraseña')

    # Validar campos obligatorios
    if not email or not contraseña:
        return jsonify({'error': 'Correo electronico y contraseña son obligatorios'}), 400

    # Validar el formato del correo electrónico
    if not empresa.es_email_valido(email):
        return jsonify({'error': 'El correo electrónico no es válido'}), 400

    try:
        # Verificar las credenciales
        if empresa.iniciar_sesion(email, contraseña):
            # Obtener el rol de usuario
            df_usuarios = empresa.cargar_usuarios()
            usuario = df_usuarios[df_usuarios['email'] == email]
            rol = usuario.iloc[0]['tipo']

            # Generar token con el rol
            token = create_access_token(identity=email, additional_claims={'rol': rol})
            return jsonify({'mensaje': 'Inicio de sesion exitoso', 'token': token}), 200
        else:
            return jsonify({'error': 'Credenciales invalidas'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/logout', methods=['POST'])
@jwt_required()
def logout() -> tuple[dict, int]:
    """
    Endpoint para cerrar sesión en el sistema.

    Este endpoint permite al usuario cerrar su sesión actual. Cuando se llama a este endpoint,
    el token JWT utilizado para autenticar la solicitud se invalida agregándolo a una lista 
    de tokens revocados (blocklist). Esto asegura que el token no pueda ser utilizado nuevamente.

    Methods
    -------
    POST
        Cierra la sesión del usuario.

    Returns
    -------
    JSON
        Un objeto JSON con la siguiente estructura:
        {
            "mensaje": "Sesion cerrada exitosamente"
        }

    Raises
    ------
    HTTP 401 Unauthorized
        Si el token JWT no es válido o está ausente.
    HTTP 500 Internal Server Error
        Si ocurre un error inesperado durante la ejecución.
    """
    try:
        # Obtener el identificador único del token JWT
        jti = get_jwt()['jti']

        # Agregar el token a la lista de tokens usados (blocklist)
        token_blocklist.add(jti)

        return jsonify({'mensaje': 'Sesion cerrada exitosamente'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/usuarios/eliminar', methods=['DELETE'])
@jwt_required()
def eliminar_usuario() -> tuple[dict, int]:
    """
    Endpoint para eliminar un usuario del sistema.

    Este endpoint permite a un administrador eliminar un usuario del sistema 
    proporcionando su correo electrónico. Solo los usuarios con rol "admin" pueden 
    acceder a este endpoint. El correo electrónico se obtiene como parámetro de la URL.

    Methods
    -------
    DELETE
        Elimina un usuario del sistema.

    Parameters
    ----------
    email : str
        Correo electrónico del usuario que se desea eliminar. Se pasa como parámetro 
        en la URL (query string).

    Headers
    -------
    Authorization : str
        Token JWT válido con claims que incluyan el rol del usuario. El token debe 
        ser proporcionado en el encabezado de la solicitud en el formato:
        `Authorization: Bearer <token_jwt>`.

    Returns
    -------
    JSON
        Un objeto JSON con la siguiente estructura:
        {
            "mensaje": "Usuario con correo usuario@example.com eliminado con éxito"
        }

    Raises
    ------
    HTTP 400 Bad Request
        Si falta el parámetro `email` o el correo electrónico no es válido.
    HTTP 403 Forbidden
        Si el usuario que realiza la solicitud no tiene rol de administrador.
    HTTP 404 Not Found
        Si no se encuentra ningún usuario con el correo electrónico proporcionado.
    HTTP 500 Internal Server Error
        Si ocurre un error inesperado durante la ejecución.
    """
    # Obtener las claims del token
    claims = get_jwt()

    # Verificar si las claims son un diccionario
    if not isinstance(claims, dict):
        return jsonify({'error': 'Error al leer las claims del token'}), 500

    # Obtener el rol del usuario
    rol = claims.get('rol')

    # Verificar si el rol es admin
    if rol != 'admin':
        return jsonify({'error': 'Acceso no autorizado'}), 403

    # Obtener el correo del usuario a eliminar desde los parámetros
    email = request.args.get('email')
    if not email:
        return jsonify({'mensaje': 'El correo electrónico es obligatorio'}), 400

    # Validar el formato del correo electrónico
    if not empresa.es_email_valido(email):
        return jsonify({'error': 'El correo electrónico no es válido'}), 400

    try:
        # Llamar al método dar_baja_usuario de la clase Empresa
        if empresa.dar_baja_usuario(email):
            return jsonify({'mensaje': f'Usuario con correo {email} eliminado con éxito'}), 200
        else:
            return jsonify({'error': 'No se pudo eliminar el usuario'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/listar-usuarios', methods=['GET'])
@jwt_required()
def listar_usuarios() -> tuple[dict, int]:
    """
    Endpoint para listar todos los usuarios registrados en el sistema.

    Este endpoint permite a un administrador obtener una lista de todos los usuarios 
    registrados en el sistema. Solo los usuarios con rol "admin" pueden acceder a este 
    endpoint. Los datos de los usuarios se devuelven en formato JSON.

    Methods
    -------
    GET
        Obtiene una lista de todos los usuarios registrados.

    Headers
    -------
    Authorization : str
        Token JWT válido con claims que incluyan el rol del usuario. El token debe 
        ser proporcionado en el encabezado de la solicitud en el formato:
        `Authorization: Bearer <token_jwt>`.

    Returns
    -------
    JSON
        Un objeto JSON con la siguiente estructura:
        {
            "mensaje": "Lista de usuarios obtenida exitosamente",
            "usuarios": [
                {
                    "id_usuario": "U001",
                    "nombre": "Juan Pérez",
                    "tipo": "cliente",
                    "email": "juan@example.com",
                    "contraseña": "hash_contraseña"
                },
                ...
            ]
        }

    Raises
    ------
    HTTP 403 Forbidden
        Si el usuario que realiza la solicitud no tiene rol de administrador.
    HTTP 404 Not Found
        Si no hay usuarios registrados en el sistema.
    HTTP 500 Internal Server Error
        Si ocurre un error inesperado durante la ejecución.
    """
    # Obtener las claims del token
    claims = get_jwt()

    # Verificar si las claims son un diccionario
    if not isinstance(claims, dict):
        return jsonify({'error': 'Error al leer las claims del token'}), 500

    # Obtener el rol del usuario
    rol = claims.get('rol')

    # Verificar si el rol es admin
    if rol != 'admin':
        return jsonify({'error': 'Acceso no autorizado'}), 403

    try:
        # Cargar usuarios
        df_usuarios = empresa.cargar_usuarios()
        if df_usuarios is None or df_usuarios.empty:
            return jsonify({'error': 'No hay usuarios registrados'}), 200

        usuarios = df_usuarios.to_dict(orient='records')

        return jsonify({
            'mensaje': 'Lista de usuarios obtenida exitosamente',
            'usuarios': usuarios
        }), 200

    except FileNotFoundError:
        return jsonify({'error': 'Archivo de usuarios no encontrado'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/usuarios/detalles/<string:email>', methods=['GET'])
@jwt_required()
def detalles_usuario(email: str) -> tuple[dict, int]:
    """
    Endpoint para obtener los detalles de un usuario específico.

    Este endpoint permite a un administrador o al propio usuario autenticado obtener 
    los detalles de un usuario específico mediante su correo electrónico. Solo los 
    usuarios con rol "admin" pueden acceder a los detalles de otros usuarios, mientras 
    que un usuario normal solo puede acceder a sus propios detalles.

    Methods
    -------
    GET
        Obtiene los detalles de un usuario específico.

    Parameters
    ----------
    email : str
        Correo electrónico del usuario cuyos detalles se desean obtener. Se pasa como 
        parte de la URL.

    Headers
    -------
    Authorization : str
        Token JWT válido con claims que incluyan el rol del usuario. El token debe 
        ser proporcionado en el encabezado de la solicitud en el formato:
        `Authorization: Bearer <token_jwt>`.

    Returns
    -------
    JSON
        Un objeto JSON con la siguiente estructura:
        {
            "mensaje": "Detalles del usuario obtenidos exitosamente",
            "usuario": {
                "id_usuario": "U001",
                "nombre": "Juan Pérez",
                "tipo": "cliente",
                "email": "juan@example.com",
                "contraseña": "hash_contraseña"
            }
        }

    Raises
    ------
    HTTP 403 Forbidden
        Si el usuario no tiene permiso para acceder a los detalles del usuario solicitado.
    HTTP 404 Not Found
        Si no se encuentra ningún usuario con el correo electrónico proporcionado.
    HTTP 500 Internal Server Error
        Si ocurre un error inesperado durante la ejecución.
    """
    # Obtener las claims del token
    claims = get_jwt()

    # Verificar si las claims son un diccionario
    if not isinstance(claims, dict):
        return jsonify({'error': 'Error al leer las claims del token'}), 500

    # Obtener el rol del usuario
    rol = claims.get('rol')
    email_usuario_autenticado = get_jwt_identity()

    try:
        # Cargar usuarios
        df_usuarios = empresa.cargar_usuarios()
        if df_usuarios is None or df_usuarios.empty:
            return jsonify({'error': 'No hay usuarios registrados'}), 200

        usuario = df_usuarios[df_usuarios['email'] == email]
        if usuario.empty:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        # Verificar permisos
        if rol != 'admin' and email_usuario_autenticado != email:
            return jsonify({'error': 'Acceso no autorizado'}), 403

        usuario = usuario.iloc[0].to_dict()
        return jsonify({
            'mensaje': 'Detalles del usuario obtenidos exitosamente',
            'usuario': usuario
        }), 200

    except FileNotFoundError:
        return jsonify({'error': 'Archivo de usuarios no encontrado'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/usuarios/actualizar-contraseña/<string:email>', methods=['PUT'])
@jwt_required()
def actualizar_usuario(email: str) -> tuple[dict, int]:
    """
    Endpoint para actualizar la contraseña de un usuario.

    Este endpoint permite a un usuario autenticado actualizar su propia contraseña. 
    Solo el usuario autenticado puede cambiar su propia contraseña. Se requiere que 
    el correo electrónico del usuario coincida con el correo electrónico asociado 
    al token JWT.

    Methods
    -------
    PUT
        Actualiza la contraseña de un usuario.

    Parameters
    ----------
    email : str
        Correo electrónico del usuario cuya contraseña se desea actualizar. Se pasa 
        como parte de la URL.

    Headers
    -------
    Authorization : str
        Token JWT válido con claims que incluyan la identidad del usuario. El token 
        debe ser proporcionado en el encabezado de la solicitud en el formato:
        `Authorization: Bearer <token_jwt>`.

    Body
    ----
    nueva_contraseña : str
        La nueva contraseña que se desea establecer para el usuario.

    Returns
    -------
    JSON
        Un objeto JSON con la siguiente estructura:
        {
            "mensaje": "Contraseña actualizada exitosamente"
        }

    Raises
    ------
    HTTP 400 Bad Request
        Si falta el campo `nueva_contraseña` o si los datos proporcionados son inválidos.
    HTTP 403 Forbidden
        Si el usuario no tiene permiso para actualizar la contraseña de otro usuario.
    HTTP 500 Internal Server Error
        Si ocurre un error inesperado durante la ejecución.
    """
    # Obtener las claims del token
    claims = get_jwt()

    # Verificar si las claims son un diccionario
    if not isinstance(claims, dict):
        return jsonify({'error': 'Error al leer las claims del token'}), 500

    email_usuario_autenticado = get_jwt_identity()

    # Comprobar que el usuario está intentando cambiar sus propios datos
    if email_usuario_autenticado != email:
        return jsonify({'error': 'Acceso no autorizado'}), 403

    data = request.json
    nueva_contraseña = data.get('nueva_contraseña')

    if not nueva_contraseña:
        return jsonify({'error': 'Debes proporcionar una nueva contraseña'}), 400

    try:
        # Llamar al método actualizar_usuario de la clase Empresa
        empresa.actualizar_usuario(email=email, nueva_contraseña=nueva_contraseña)
        return jsonify({'mensaje': 'Contraseña actualizada exitosamente'}), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ---------------------------------------
# ENDPOINTS RELACIONADOS CON BUSQUEDAS
# ---------------------------------------

@app.route('/coches-disponibles', methods=['GET'])
def buscar_coches_disponibles() -> tuple[dict, int]:
    """
    Endpoint para buscar coches disponibles filtrados por categoría de precio, 
    categoría de tipo, marca y modelo.

    Este endpoint permite a los usuarios buscar coches disponibles en el sistema 
    utilizando filtros opcionales como categoría de precio, categoría de tipo, 
    marca y modelo. Los resultados se devuelven en formato JSON.

    Methods
    -------
    GET
        Busca coches disponibles según los filtros proporcionados.

    Parameters
    ----------
    categoria_precio : str, optional
        Categoría de precio para filtrar los coches (por ejemplo, "Bajo", "Medio", "Alto").
    categoria_tipo : str, optional
        Categoría de tipo para filtrar los coches (por ejemplo, "Compacto", "SUV", "Deportivo").
    marca : str, optional
        Marca del coche para filtrar los resultados.
    modelo : str, optional
        Modelo del coche para filtrar los resultados.

    Returns
    -------
    JSON
        Un objeto JSON con la siguiente estructura:
        {
            "detalles": [
                {
                    "matricula": "8237 SPL",
                    "marca": "Toyota",
                    "modelo": "Corolla",
                    "categoria_precio": "Medio",
                    "categoria_tipo": "Compacto",
                    "disponible": true,
                    "año": 2022,
                    "precio_diario": 50.0,
                    "kilometraje": 15000,
                    "color": "Blanco",
                    "combustible": "Gasolina",
                    "cv": 120,
                    "plazas": 5
                },
                ...
            ]
        }

    Raises
    ------
    HTTP 400 Bad Request
        Si los parámetros proporcionados son inválidos o no coinciden con los datos disponibles.
    HTTP 500 Internal Server Error
        Si ocurre un error inesperado durante la ejecución.
    """
    try:
        # Obtener los parámetros de la solicitud
        categoria_precio = request.args.get('categoria_precio')
        categoria_tipo = request.args.get('categoria_tipo')
        marca = request.args.get('marca')
        modelo = request.args.get('modelo')

        # Obtener los detalles de los coches
        detalles = empresa.obtener_detalles_coches(categoria_precio=categoria_precio, categoria_tipo=categoria_tipo, marca=marca, modelo=modelo)
        return jsonify(detalles), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Error interno del servidor"}), 500


# ---------------------------------------
# ENDPOINTS RELACIONADOS CON ALQUILERES
# ---------------------------------------


@app.route('/alquilar-coche', methods=['POST'])
@jwt_required(optional=True)
def alquilar_coches() -> tuple[dict | int]:
    """
    Endpoint para registrar un alquiler de coche.

    Este endpoint permite a los usuarios (autenticados o invitados) registrar un nuevo 
    alquiler de coche. Si el usuario está autenticado, se utiliza su correo electrónico 
    del token JWT. Los administradores no pueden alquilar coches. Al finalizar el proceso, 
    se genera una factura en formato PDF que se devuelve como archivo adjunto.

    Methods
    -------
    POST
        Registra un nuevo alquiler de coche.

    Parameters
    ----------
    matricula : str
        La matrícula del coche que se desea alquilar.
    fecha_inicio : str
        Fecha de inicio del alquiler en formato YYYY-MM-DD.
    fecha_fin : str
        Fecha de fin del alquiler en formato YYYY-MM-DD.
    email : str, optional
        Correo electrónico del usuario que realiza el alquiler. Si el usuario está 
        autenticado, este campo es opcional.

    Headers
    -------
    Authorization : str, optional
        Token JWT válido con claims que incluyan el rol del usuario. El token debe 
        ser proporcionado en el encabezado de la solicitud en el formato:
        `Authorization: Bearer <token_jwt>`.

    Returns
    -------
    JSON
        En caso de error, se devuelve un objeto JSON con la siguiente estructura:
        {
            "error": "Mensaje de error descriptivo"
        }

    File
        En caso de éxito, se devuelve un archivo PDF con la factura del alquiler. 
        El archivo se adjunta con el nombre `factura.pdf`.

    Raises
    ------
    HTTP 400 Bad Request
        Si faltan campos obligatorios, las fechas tienen un formato incorrecto o los 
        datos proporcionados son inválidos.
    HTTP 403 Forbidden
        Si el usuario es un administrador (los administradores no pueden alquilar coches).
    HTTP 500 Internal Server Error
        Si ocurre un error inesperado durante la ejecución.
    """
    data = request.json
    matricula = data.get('matricula')
    fecha_inicio = data.get('fecha_inicio')
    fecha_fin = data.get('fecha_fin')
    email = data.get('email')

    # Validaciones necesarias
    if not matricula or not fecha_inicio or not fecha_fin:
        return jsonify({'error': 'Debes introducir la matrícula, la fecha de inicio y la fecha de fin'}), 400

    # Validar formato de las fechas
    try:
        fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
    except ValueError:
        return jsonify({'error': 'Las fechas deben estar en formato YYYY-MM-DD'}), 400

    try:
        # Obtener claims del token si existe
        claims = get_jwt() if get_jwt() else {}
        rol = claims.get('rol')

        # Verificar si el usuario es admin
        if rol == 'admin':
            return jsonify({'error': 'Los administradores no pueden alquilar coches'}), 403

        # Si el usuario está autenticado, obtener su email del token
        if rol and not email:
            email = get_jwt_identity()

        # Registrar el alquiler y obtener el PDF
        pdf_bytes = empresa.alquilar_coche(
            matricula=matricula,
            fecha_inicio=fecha_inicio.strftime('%Y-%m-%d'),
            fecha_fin=fecha_fin.strftime('%Y-%m-%d'),
            email=email
        )

        # Crear una respuesta con el archivo PDF
        response = make_response(pdf_bytes)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=factura.pdf'
        return response

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"Error interno: {str(e)}")
        return jsonify({'error': 'Error interno del servidor. Por favor, inténtalo de nuevo más tarde.'}), 500
    

@app.route('/alquileres/listar', methods=['GET'])
@jwt_required()
def listar_alquileres() -> tuple[dict, int]:
    """
    Endpoint para listar todos los alquileres registrados en el sistema.

    Este endpoint permite a un administrador obtener una lista de todos los alquileres 
    registrados en el sistema. Solo los usuarios con rol "admin" pueden acceder a este 
    endpoint. Los datos de los alquileres se devuelven en formato JSON.

    Methods
    -------
    GET
        Obtiene una lista de todos los alquileres registrados.

    Headers
    -------
    Authorization : str
        Token JWT válido con claims que incluyan el rol del usuario. El token debe 
        ser proporcionado en el encabezado de la solicitud en el formato:
        `Authorization: Bearer <token_jwt>`.

    Returns
    -------
    JSON
        Un objeto JSON con la siguiente estructura:
        {
            "mensaje": "Lista de alquileres obtenida exitosamente",
            "alquileres": [
                {
                    "id_alquiler": "A001",
                    "id_coche": "UID01",
                    "id_usuario": "U001",
                    "fecha_inicio": "2025-04-10",
                    "fecha_fin": "2025-04-11",
                    "coste_total": 100.0,
                    "activo": true
                },
                ...
            ]
        }

    Raises
    ------
    HTTP 403 Forbidden
        Si el usuario que realiza la solicitud no tiene rol de administrador.
    HTTP 404 Not Found
        Si no hay alquileres registrados en el sistema.
    HTTP 500 Internal Server Error
        Si ocurre un error inesperado durante la ejecución.
    """
    # Obtener las claims del token
    claims = get_jwt()

    # Verificar si las claims son un diccionario
    if not isinstance(claims, dict):
        return jsonify({'error': 'Error al leer las claims del token'}), 500

    # Obtener el rol del usuario
    rol = claims.get('rol')

    # Verificar si el rol es admin
    if rol != 'admin':
        return jsonify({'error': 'Acceso no autorizado'}), 403

    try:
        # Cargar alquileres
        df_alquileres = empresa.cargar_alquileres()
        if df_alquileres is None or df_alquileres.empty:
            return jsonify({
                'mensaje': 'No hay alquileres registrados',
                'alquileres': []
            }), 200

        alquileres = df_alquileres.to_dict(orient='records')

        return jsonify({
            'mensaje': 'Lista de alquileres obtenida exitosamente',
            'alquileres': alquileres
        }), 200

    except FileNotFoundError:
        return jsonify({'error': 'Archivo de alquileres no encontrado'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/alquileres/detalles/<string:id_alquiler>', methods=['GET'])
@jwt_required()
def detalles_alquiler(id_alquiler: str) -> tuple[dict, int]:
    """
    Endpoint para obtener los detalles de un alquiler específico.

    Este endpoint permite a un administrador o al usuario autenticado obtener los 
    detalles de un alquiler específico mediante su ID. Solo los usuarios con rol 
    "admin" pueden acceder a los detalles de cualquier alquiler, mientras que un 
    usuario normal solo puede acceder a los detalles de sus propios alquileres.

    Methods
    -------
    GET
        Obtiene los detalles de un alquiler específico.

    Parameters
    ----------
    id_alquiler : str
        ID único del alquiler cuyos detalles se desean obtener. Se pasa como parte 
        de la URL.

    Headers
    -------
    Authorization : str
        Token JWT válido con claims que incluyan el rol y la identidad del usuario. 
        El token debe ser proporcionado en el encabezado de la solicitud en el formato:
        `Authorization: Bearer <token_jwt>`.

    Returns
    -------
    JSON
        Un objeto JSON con la siguiente estructura:
        {
            "mensaje": "Detalles del alquiler obtenidos exitosamente",
            "alquiler": {
                "id_alquiler": "A001",
                "id_coche": "UID01",
                "id_usuario": "U001",
                "fecha_inicio": "2025-04-10",
                "fecha_fin": "2025-04-11",
                "coste_total": 100.0,
                "activo": true
            }
        }

    Raises
    ------
    HTTP 403 Forbidden
        Si el usuario no tiene permiso para acceder a los detalles del alquiler.
    HTTP 404 Not Found
        Si no se encuentra ningún alquiler con el ID proporcionado.
    HTTP 500 Internal Server Error
        Si ocurre un error inesperado durante la ejecución.
    """
    # Obtener las claims del token
    claims = get_jwt()

    # Verificar si las claims son un diccionario
    if not isinstance(claims, dict):
        return jsonify({'error': 'Error al leer las claims del token'}), 500

    # Obtener el rol y el email del usuario autenticado
    rol = claims.get('rol')
    email_usuario_autenticado = get_jwt_identity()

    try:
        # Cargar los alquileres
        df_alquileres = empresa.cargar_alquileres()
        if df_alquileres is None or df_alquileres.empty:
            return jsonify({'error': 'No hay alquileres registrados'}), 404

        # Buscar el alquiler por ID
        alquiler = df_alquileres[df_alquileres['id_alquiler'] == id_alquiler]
        if alquiler.empty:
            return jsonify({'error': 'Alquiler no encontrado'}), 404

        # Extraer el ID del usuario asociado al alquiler
        id_usuario_alquiler = alquiler.iloc[0]['id_usuario']

        # Verificar permisos
        if rol != 'admin' and email_usuario_autenticado != id_usuario_alquiler:
            return jsonify({'error': 'Acceso no autorizado'}), 403

        # Convertir el alquiler a un diccionario
        alquiler = alquiler.iloc[0].to_dict()

        return jsonify({
            'mensaje': 'Detalles del alquiler obtenidos exitosamente',
            'alquiler': alquiler
        }), 200

    except FileNotFoundError:
        return jsonify({'error': 'Archivo de alquileres no encontrado'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/alquileres/finalizar/<string:id_alquiler>', methods=['PUT'])
@jwt_required()
def finalizar_alquiler(id_alquiler: str) -> tuple[dict, int]:
    """
    Endpoint para finalizar un alquiler específico.

    Este endpoint permite a un administrador o al usuario autenticado finalizar un 
    alquiler específico mediante su ID. Solo los usuarios con rol "admin" pueden 
    finalizar cualquier alquiler, mientras que un usuario normal solo puede finalizar 
    sus propios alquileres. Una vez finalizado, el coche asociado al alquiler se marca 
    como disponible nuevamente.

    Methods
    -------
    PUT
        Finaliza un alquiler específico.

    Parameters
    ----------
    id_alquiler : str
        ID único del alquiler que se desea finalizar. Se pasa como parte de la URL.

    Headers
    -------
    Authorization : str
        Token JWT válido con claims que incluyan el rol y la identidad del usuario. 
        El token debe ser proporcionado en el encabezado de la solicitud en el formato:
        `Authorization: Bearer <token_jwt>`.

    Returns
    -------
    JSON
        Un objeto JSON con la siguiente estructura:
        {
            "mensaje": "Alquiler con id A001 finalizado con exito"
        }

    Raises
    ------
    HTTP 400 Bad Request
        Si el alquiler ya está finalizado.
    HTTP 403 Forbidden
        Si el usuario no tiene permiso para finalizar el alquiler.
    HTTP 404 Not Found
        Si no se encuentra ningún alquiler con el ID proporcionado.
    HTTP 500 Internal Server Error
        Si ocurre un error inesperado durante la ejecución.
    """
    # Obtener las claims del token
    claims = get_jwt()

    # Verificar si las claims son un diccionario
    if not isinstance(claims, dict):
        return jsonify({'error': 'Error al leer las claims del token'}), 500

    # Obtener el rol y el email del usuario autenticado
    rol = claims.get('rol')
    email_usuario_autenticado = get_jwt_identity()

    try:
        # Cargar los alquileres
        df_alquileres = empresa.cargar_alquileres()
        if df_alquileres is None or df_alquileres.empty:
            return jsonify({'error': 'No se encontraron alquileres registrados'}), 404

        # Buscar el alquiler por ID
        alquiler = df_alquileres[df_alquileres['id_alquiler'] == id_alquiler]
        if alquiler.empty:
            return jsonify({'error': 'Alquiler no encontrado'}), 404

        # Verificar el estado del alquiler
        if not alquiler.iloc[0]['activo']:
            return jsonify({'error': 'El alquiler ya está finalizado'}), 400

        # Extraer el ID del usuario asociado al alquiler
        id_usuario_alquiler = alquiler.iloc[0]['id_usuario']

        # Verificar permisos
        if rol != 'admin' and email_usuario_autenticado != id_usuario_alquiler:
            return jsonify({'error': 'Acceso no autorizado'}), 403

        # Finalizar el alquiler
        empresa.finalizar_alquiler(id_alquiler)
        return jsonify({'mensaje': f'Alquiler con id {id_alquiler} finalizado con exito'}), 200

    except FileNotFoundError:
        return jsonify({'error': 'Archivo de alquileres no encontrado'}), 500
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500


@app.route('/alquileres/historial/<string:email>', methods=['GET'])
@jwt_required()
def historial_alquileres(email: str) -> tuple[dict, int]:
    """
    Endpoint para obtener el historial de alquileres de un usuario específico.

    Este endpoint permite a un administrador o al usuario autenticado obtener el 
    historial de alquileres de un usuario mediante su correo electrónico. Solo los 
    usuarios con rol "admin" pueden acceder al historial de cualquier usuario, mientras 
    que un usuario normal solo puede acceder a su propio historial de alquileres.

    Methods
    -------
    GET
        Obtiene el historial de alquileres de un usuario específico.

    Parameters
    ----------
    email : str
        Correo electrónico del usuario cuyo historial de alquileres se desea obtener. 
        Se pasa como parte de la URL.

    Headers
    -------
    Authorization : str
        Token JWT válido con claims que incluyan el rol y la identidad del usuario. 
        El token debe ser proporcionado en el encabezado de la solicitud en el formato:
        `Authorization: Bearer <token_jwt>`.

    Returns
    -------
    JSON
        Un objeto JSON con la siguiente estructura:
        {
            "mensaje": "Historial de alquileres del usuario con email usuario@example.com",
            "alquileres": [
                {
                    "id_alquiler": "A001",
                    "id_coche": "UID01",
                    "fecha_inicio": "2025-04-10",
                    "fecha_fin": "2025-04-11",
                    "coste_total": 100.0,
                    "activo": true
                },
                ...
            ]
        }

    Raises
    ------
    HTTP 403 Forbidden
        Si el usuario no tiene permiso para acceder al historial del usuario solicitado.
    HTTP 404 Not Found
        Si el usuario con el correo electrónico proporcionado no está registrado.
    HTTP 500 Internal Server Error
        Si ocurre un error inesperado durante la ejecución.
    """
    # Obtener las claims del token
    claims = get_jwt()

    # Verificar si las claims son un diccionario
    if not isinstance(claims, dict):
        return jsonify({'error': 'Error al leer las claims del token'}), 500

    # Obtener el rol y el email del usuario autenticado
    rol = claims.get('rol')
    email_usuario_autenticado = get_jwt_identity()

    try:
        # Cargar los usuarios para validar el email
        df_usuarios = empresa.cargar_usuarios()
        if df_usuarios is None or df_usuarios.empty:
            return jsonify({'error': 'No se pudieron cargar los usuarios'}), 500

        # Verificar si el email existe en el sistema
        if email not in df_usuarios['email'].values:
            return jsonify({'error': f'El usuario con email {email} no está registrado'}), 404

        # Verificar permisos
        if rol != 'admin' and email != email_usuario_autenticado:
            return jsonify({'error': 'Acceso no autorizado'}), 403

        # Obtener el historial de alquileres del usuario
        historial = empresa.obtener_historial_alquileres(email)

        return jsonify({
            'mensaje': f'Historial de alquileres del usuario con email {email}',
            'alquileres': historial
        }), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------------------------------------
# ENDPOINTS RELACIONADOS CON COCHES
# ---------------------------------------

@app.route('/coches/registrar', methods=['POST'])
@jwt_required()
def registrar_coche() -> tuple[dict, int]:
    """
    Endpoint para registrar un nuevo coche en el sistema.

    Este endpoint permite a un administrador registrar un nuevo coche en el sistema. 
    Solo los usuarios con rol "admin" pueden acceder a este endpoint. Todos los campos 
    obligatorios deben ser proporcionados en el cuerpo de la solicitud. El campo 
    'disponible' debe ser un valor booleano (True o False).

    Methods
    -------
    POST
        Registra un nuevo coche en el sistema.

    Headers
    -------
    Authorization : str
        Token JWT válido con claims que incluyan el rol del usuario. El token debe 
        ser proporcionado en el encabezado de la solicitud en el formato:
        `Authorization: Bearer <token_jwt>`.

    Body
    ----
    marca : str
        Marca del coche.
    modelo : str
        Modelo del coche.
    matricula : str
        Matrícula única del coche.
    categoria_tipo : str
        Categoría de tipo del coche (por ejemplo, "Compacto", "SUV").
    categoria_precio : str
        Categoría de precio del coche (por ejemplo, "Bajo", "Medio", "Alto").
    año : int
        Año de fabricación del coche. Debe estar entre 1900 y el año actual.
    precio_diario : float
        Precio diario de alquiler del coche.
    kilometraje : float
        Kilometraje actual del coche.
    color : str
        Color del coche.
    combustible : str
        Tipo de combustible del coche (por ejemplo, "Gasolina", "Diésel").
    cv : int
        Potencia del coche en caballos de vapor (CV).
    plazas : int
        Número de plazas del coche.
    disponible : bool
        Indica si el coche está disponible para alquilar (True o False).

    Returns
    -------
    JSON
        Un objeto JSON con la siguiente estructura:
        {
            "mensaje": "Coche registrado con éxito"
        }

    Raises
    ------
    HTTP 400 Bad Request
        Si faltan campos obligatorios, los datos proporcionados son inválidos o el 
        campo 'disponible' no es un valor booleano.
    HTTP 403 Forbidden
        Si el usuario que realiza la solicitud no tiene rol de administrador.
    HTTP 500 Internal Server Error
        Si ocurre un error inesperado durante la ejecución.
    """
    # Obtener las claims del token
    claims = get_jwt()

    # Verificar si las claims son un diccionario
    if not isinstance(claims, dict):
        return jsonify({'error': 'Error al leer las claims del token'}), 500

    # Obtener el rol del usuario
    rol = claims.get('rol')

    # Verificar si el rol es admin
    if rol != 'admin':
        return jsonify({'error': 'Acceso no autorizado'}), 403

    # Obtener los datos enviados en la solicitud
    data = request.json
    marca = data.get('marca')
    modelo = data.get('modelo')
    matricula = data.get('matricula')
    categoria_tipo = data.get('categoria_tipo')
    categoria_precio = data.get('categoria_precio')
    año = data.get('año')
    precio_diario = data.get('precio_diario')
    kilometraje = data.get('kilometraje')
    color = data.get('color')
    combustible = data.get('combustible')
    cv = data.get('cv')
    plazas = data.get('plazas')
    disponible = data.get('disponible')

    # Validar campos obligatorios
    if not all([marca, modelo, matricula, categoria_tipo, categoria_precio, año, precio_diario, kilometraje, color, combustible, cv, plazas]):
        return jsonify({'error': 'Faltan campos obligatorios en la solicitud'}), 400

    # Validar el campo 'disponible'
    if disponible not in [True, False]:
        return jsonify({'error': 'El campo "disponible" debe ser True o False'}), 400

    try:
        # Convertir el año a entero y validar su rango
        try:
            año = int(año)
            if año < 1900 or año > datetime.now().year:
                raise ValueError("El año debe estar entre 1900 y el año actual.")
        except ValueError:
            return jsonify({'error': 'El campo "año" debe ser un número entero válido'}), 400
        
        # Llamar al método registrar_coche de la clase Empresa
        if empresa.registrar_coche(
            marca=marca,
            modelo=modelo,
            matricula=matricula,
            categoria_tipo=categoria_tipo,
            categoria_precio=categoria_precio,
            año=año,
            precio_diario=precio_diario,
            kilometraje=kilometraje,
            color=color,
            combustible=combustible,
            cv=cv,
            plazas=plazas,
            disponible=disponible
        ):
            return jsonify({'mensaje': 'Coche registrado con éxito'}), 201
        else:
            return jsonify({'error': 'Error al registrar el coche'}), 500

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500


@app.route('/coches/detalles/<string:matricula>', methods=['GET'])
def detalles_coche(matricula: str) -> tuple[dict, int]:
    """
    Endpoint para obtener los detalles de un coche específico mediante su matrícula.

    Este endpoint permite a cualquier usuario (sin necesidad de autenticación) obtener 
    los detalles de un coche específico utilizando su matrícula. Si el coche no se 
    encuentra registrado, se devuelve un error 404.

    Methods
    -------
    GET
        Obtiene los detalles de un coche específico.

    Parameters
    ----------
    matricula : str
        Matrícula única del coche cuyos detalles se desean obtener. Se pasa como parte 
        de la URL.

    Returns
    -------
    JSON
        Un objeto JSON con la siguiente estructura:
        {
            "mensaje": "Detalles del coche obtenidos exitosamente",
            "coche": {
                "id": "UID01",
                "marca": "Toyota",
                "modelo": "Corolla",
                "matricula": "8237 SPL",
                "categoria_tipo": "Compacto",
                "categoria_precio": "Medio",
                "año": 2022,
                "precio_diario": 50.0,
                "kilometraje": 15000,
                "color": "Blanco",
                "combustible": "Gasolina",
                "cv": 120,
                "plazas": 5,
                "disponible": true
            }
        }

    Raises
    ------
    HTTP 404 Not Found
        Si no se encuentra ningún coche con la matrícula proporcionada.
    HTTP 500 Internal Server Error
        Si ocurre un error inesperado durante la ejecución.
    """
    try:
        # Cargar los coches
        df_coches = empresa.cargar_coches()
        if df_coches is None or df_coches.empty:
            return jsonify({'error': 'No se encontraron coches registrados'}), 404

        # Buscar el coche por matrícula
        coche = df_coches[df_coches['matricula'] == matricula]
        if coche.empty:
            return jsonify({'error': 'Coche no encontrado'}), 404

        # Convertir el coche a un diccionario
        coche = coche.iloc[0].to_dict()

        return jsonify({
            'mensaje': 'Detalles del coche obtenidos exitosamente',
            'coche': coche
        }), 200

    except FileNotFoundError:
        return jsonify({'error': 'Archivo de coches no encontrado'}), 500
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500
    
    
@app.route('/coches/actualizar-matricula/<string:id_coche>', methods=['PUT'])
@jwt_required()
def actualizar_matricula(id_coche: str) -> tuple[dict, int]:
    """
    Endpoint para actualizar la matrícula de un coche específico.

    Este endpoint permite a un administrador actualizar la matrícula de un coche 
    registrado en el sistema. Solo los usuarios con rol "admin" pueden acceder a este 
    endpoint. Se debe proporcionar una nueva matrícula válida en el cuerpo de la solicitud.

    Methods
    -------
    PUT
        Actualiza la matrícula de un coche específico.

    Parameters
    ----------
    id_coche : str
        ID único del coche cuya matrícula se desea actualizar. Se pasa como parte de la URL.

    Headers
    -------
    Authorization : str
        Token JWT válido con claims que incluyan el rol del usuario. El token debe 
        ser proporcionado en el encabezado de la solicitud en el formato:
        `Authorization: Bearer <token_jwt>`.

    Body
    ----
    nueva_matricula : str
        La nueva matrícula que se desea asignar al coche.

    Returns
    -------
    JSON
        Un objeto JSON con la siguiente estructura:
        {
            "mensaje": "Matrícula del coche con ID UID01 actualizada exitosamente"
        }

    Raises
    ------
    HTTP 400 Bad Request
        Si no se proporciona una nueva matrícula en la solicitud.
    HTTP 403 Forbidden
        Si el usuario que realiza la solicitud no tiene rol de administrador.
    HTTP 500 Internal Server Error
        Si ocurre un error inesperado durante la ejecución.
    """
    claims = get_jwt()

    # Verificar si las claims son un diccionario
    if not isinstance(claims, dict):
        return jsonify({'error': 'Error al leer las claims del token'}), 500

    rol = claims.get('rol')

    # Comprobar que el usuario es admin
    if rol != 'admin':
        return jsonify({'error': 'Acceso no autorizado'}), 403

    data = request.json
    nueva_matricula = data.get('nueva_matricula')

    if not nueva_matricula:
        return jsonify({'error': 'Debes proporcionar una nueva matricula'}), 400

    try:
        # Llamar al método actualizar_matricula de la clase Empresa
        empresa.actualizar_matricula(id_coche=id_coche, nueva_matricula=nueva_matricula)

        return jsonify({'mensaje': f'Matrícula del coche con ID {id_coche} actualizada exitosamente'}), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/coches/eliminar/<string:id_coche>', methods=['DELETE'])
@jwt_required()
def eliminar_coche(id_coche: str) -> tuple[dict, int]:
    """
    Endpoint para eliminar un coche específico mediante su ID.

    Este endpoint permite a un administrador eliminar un coche registrado en el sistema. 
    Solo los usuarios con rol "admin" pueden acceder a este endpoint. Si el coche no se 
    encuentra registrado, se devuelve un error 404.

    Methods
    -------
    DELETE
        Elimina un coche específico.

    Parameters
    ----------
    id_coche : str
        ID único del coche que se desea eliminar. Se pasa como parte de la URL.

    Headers
    -------
    Authorization : str
        Token JWT válido con claims que incluyan el rol del usuario. El token debe 
        ser proporcionado en el encabezado de la solicitud en el formato:
        `Authorization: Bearer <token_jwt>`.

    Returns
    -------
    JSON
        Un objeto JSON con la siguiente estructura:
        {
            "mensaje": "Coche con ID UID01 eliminado con éxito"
        }

    Raises
    ------
    HTTP 403 Forbidden
        Si el usuario que realiza la solicitud no tiene rol de administrador.
    HTTP 404 Not Found
        Si no se encuentra ningún coche con el ID proporcionado.
    HTTP 500 Internal Server Error
        Si ocurre un error inesperado durante la ejecución.
    """
    # Obtener las claims del token
    claims = get_jwt()

    # Verificar si las claims son un diccionario
    if not isinstance(claims, dict):
        return jsonify({'error': 'Error al leer las claims del token'}), 500

    # Obtener el rol del usuario
    rol = claims.get('rol')

    # Verificar si el rol es admin
    if rol != 'admin':
        return jsonify({'error': 'Acceso no autorizado'}), 403

    try:
        # Llamar al método eliminar_coche de la clase Empresa
        if empresa.eliminar_coche(id_coche=id_coche):
            return jsonify({'mensaje': f'Coche con ID {id_coche} eliminado con éxito'}), 200
        else:
            return jsonify({'error': f'No se encontró ningún coche con ID {id_coche}'}), 404

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500
    
    
# ---------------------------------------
# ENDPOINTS ADICIONALES
# ---------------------------------------


@app.route('/coches/categorias/precio', methods=['GET'])
def categorias_precio():
    """
    Endpoint para obtener las categorías de precio disponibles.

    Returns:
        JSON: Una lista de categorías de precio únicas disponibles.
    """
    try:
        # Llamar al método de la clase Empresa para obtener las categorías de precio
        categorias = empresa.mostrar_categorias_precio()

        return jsonify({
            'mensaje': 'Categorías de precio obtenidas exitosamente',
            'categorias_precio': categorias
        }), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500
    
    
@app.route('/coches/categorias/tipo', methods=['GET'])
def categorias_tipo():
    """
    Endpoint para obtener las categorías de tipo disponibles.

    Este endpoint permite recuperar una lista de todas las categorías de tipo 
    de coches disponibles en el sistema. Las categorías se obtienen a través del 
    método `mostrar_categorias_tipo` de la clase `Empresa`.

    Methods
    -------
    GET
        Obtiene una lista de categorías de tipo disponibles.

    Returns
    -------
    JSON
        Un objeto JSON con la siguiente estructura:
        {
            "mensaje": "Categorías de tipo obtenidas exitosamente",
            "categorias_tipo": ["Compacto", "SUV", "Deportivo", "Familiar"]
        }

    Raises
    ------
    HTTP 404 Not Found
        Si no hay datos disponibles o si ocurre un error al cargar las categorías.
    HTTP 500 Internal Server Error
        Si ocurre un error inesperado durante la ejecución.
    """
    try:
        # Llamar al método de la clase Empresa para obtener las categorías de tipo
        categorias = empresa.mostrar_categorias_tipo()

        return jsonify({
            'mensaje': 'Categorías de tipo obtenidas exitosamente',
            'categorias_tipo': categorias
        }), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)