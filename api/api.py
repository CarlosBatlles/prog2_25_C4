"""
API de Alquiler de Coches.

Este script implementa una API web utilizando Flask para gestionar el alquiler
de coches, incluyendo la administración de usuarios, coches y alquileres.
Utiliza Flask-JWT-Extended para la autenticación basada en tokens.
"""

# --------------------------------------------------------------------------
# SECCIÓN 1: IMPORTACIONES
# --------------------------------------------------------------------------


from flask import Flask, request, jsonify, make_response, Response
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from datetime import datetime
from mysql.connector import Error as MySQLError
from source.empresaV2 import Empresa
from source.utils import formatear_id, es_email_valido
from typing import Dict, Any, Tuple, Set, Union, Optional # Para sugerencias de tipo


# --------------------------------------------------------------------------
# SECCIÓN 2: CONFIGURACIÓN DE LA APLICACIÓN FLASK Y EXTENSIONES
# --------------------------------------------------------------------------


app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "grupo_4!"
jwt = JWTManager(app)

# Lista (conjunto) para almacenar JTI (JWT ID) de tokens revocados (para logout)
token_blocklist = set()

# Instanciación del objeto principal de la lógica de negocio
empresa = Empresa(nombre='RentAcar')


# --------------------------------------------------------------------------
# SECCIÓN 3: RUTAS DE BIENVENIDA / ÍNDICE
# --------------------------------------------------------------------------


@app.route('/')
def home() -> Tuple[str, int]:
    """
    Endpoint raíz de la API. Devuelve un mensaje de bienvenida.

    Este endpoint sirve como una prueba básica para verificar que la API
    está en funcionamiento y accesible.

    Returns
    -------
    Tuple[str, int]
        Una tupla conteniendo el mensaje de bienvenida y el código de estado HTTP 200.
    
    Examples
    --------
    Solicitud GET a `/`:
    Respuesta:
        "Bienvenido a la API de Alquiler de Coches" (status 200)
    """
    return "Bienvenido a la API de Alquiler de Coches", 200


# --------------------------------------------------------------------------
# SECCIÓN 4: CONFIGURACIÓN Y MANEJADORES DE JWT (Flask-JWT-Extended)
# --------------------------------------------------------------------------


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header: Dict[str, Any], jwt_payload: Dict[str, Any]) -> bool:
    """
    Verifica si un token JWT ha sido revocado (añadido a la blocklist).

    Este callback es utilizado por Flask-JWT-Extended para determinar si un token
    presentado es válido o si ha sido explícitamente revocado (e.g., durante
    un cierre de sesión). Comprueba si el identificador único del token (JTI)
    está presente en el `token_blocklist` global.

    Parameters
    ----------
    jwt_header : Dict[str, Any]
        El encabezado decodificado del JWT. No se usa directamente en esta implementación
        pero es proporcionado por Flask-JWT-Extended.
    jwt_payload : Dict[str, Any]
        El payload (contenido) decodificado del JWT. Se espera que contenga la claim 'jti'.

    Returns
    -------
    bool
        `True` si el JTI del token se encuentra en la `token_blocklist` (indicando
        que el token está revocado), `False` en caso contrario.
    """
    jti: Optional[str] = jwt_payload.get('jti')
    return jti in token_blocklist


# --------------------------------------------------------------------------
# SECCIÓN 5: ENDPOINTS DE AUTENTICACIÓN Y GESTIÓN DE CUENTA DE USUARIO
# --------------------------------------------------------------------------


@app.route('/signup', methods=['POST'])
def signup() -> Tuple[Response, int]:
    """
    Registra un nuevo usuario en el sistema.

    Acepta datos de usuario (nombre, tipo, email, contraseña) en formato JSON.
    Valida los datos de entrada. Si son válidos, llama a la lógica de negocio
    para registrar al usuario y devuelve el ID del nuevo usuario formateado.

    Body (JSON)
    -----------
    nombre : str
        Nombre completo del nuevo usuario.
    tipo : str, optional
        Rol del usuario. Debe ser "admin" o "cliente".
        Si no se proporciona, se asume "cliente".
    email : str
        Correo electrónico del nuevo usuario. Debe ser único y válido.
    contraseña : str
        Contraseña deseada para el nuevo usuario (en texto plano).
        Será hasheada por la lógica de negocio antes de almacenarse.

    Returns
    -------
    Tuple[Response, int]
        Una tupla conteniendo una respuesta Flask (JSON) y un código de estado HTTP.
        - 201 Created: Si el usuario se registra exitosamente.
        JSON: `{"mensaje": "Usuario registrado exitosamente", "id_usuario": "U<ID>"}`
        - 400 Bad Request: Si hay errores de validación en los datos de entrada
        (e.g., campos faltantes, email inválido, tipo de usuario incorrecto,
        o un `ValueError` de la lógica de negocio como email duplicado).
        JSON: `{"error": "mensaje descriptivo del error"}`
        - 500 Internal Server Error: Para otros errores inesperados en el servidor.
        JSON: `{"error": "Error interno del servidor"}`
    """
    data: Optional[Dict[str, Any]] = request.json
    nombre: Optional[str] = data.get('nombre')
    tipo: str = str(data.get('tipo', 'cliente')).lower().strip()
    email: Optional[str] = data.get('email')
    contraseña: Optional[str] = data.get('contraseña')

    # Validar campos obligatorios
    if not nombre or not email or not contraseña:
        return jsonify({'error': 'Todos los campos son obligatorios'}), 400

    # Validar el correo electrónico
    if not es_email_valido(email):
        return jsonify({'error': 'El correo electrónico no es válido'}), 400

    # Validar el tipo de usuario
    if tipo not in ['admin', 'cliente']:
        return jsonify({'error': 'El tipo de usuario debe ser "admin" o "cliente"'}), 400

    try:
        id_usuario: str = empresa.registrar_usuario(nombre=nombre, tipo=tipo, email=email, contraseña=contraseña)
        return jsonify({
            "mensaje": "Usuario registrado exitosamente",
            "id_usuario": formatear_id(id_usuario,'U')
        }),201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Error interno del servidor"}),500


@app.route('/login', methods=['POST'])
def login() -> Tuple[Response, int]:
    """
    Autentica a un usuario y devuelve un token JWT si las credenciales son válidas.

    Acepta 'email' y 'contraseña' en el cuerpo JSON de la solicitud.
    Valida la entrada y llama a la lógica de negocio para verificar las credenciales.
    Si la autenticación es exitosa, genera un token JWT que incluye el rol del
    usuario como una claim adicional y lo devuelve junto con otros datos del usuario.

    Body (JSON)
    -----------
    email : str
        Correo electrónico del usuario.
    contraseña : str
        Contraseña del usuario en texto plano.

    Returns
    -------
    Tuple[Response, int]
        Una tupla conteniendo una respuesta Flask (JSON) y un código de estado HTTP.
        - 200 OK: Si el inicio de sesión es exitoso.
        JSON: `{"mensaje": "Inicio de sesion exitoso.", "token": "...", "rol": "...", "nombre": "...", "id_usuario": "..."}`
        - 400 Bad Request: Si faltan campos, el email es inválido, o la lógica de
        negocio devuelve un `ValueError` (e.g., usuario no encontrado).
        JSON: `{"error": "mensaje descriptivo del error"}`
        - 401 Unauthorized: Si la autenticación falla (e.g., contraseña incorrecta).
        JSON: `{"error": "No se pudo autenticar al usuario"}`
        - 500 Internal Server Error: Para otros errores inesperados en el servidor.
        JSON: `{"error": "Error interno del servidor <detalle_error>"}`
    """
    data: Optional[Dict[str, Any]] = request.json
    email: Optional[str] = data.get('email')
    contraseña: Optional[str] = data.get('contraseña')


    # Validar campos obligatorios
    if not email or not contraseña:
        return jsonify({'error': 'Correo electronico y contraseña son obligatorios'}), 400

    # Validar el formato del correo electrónico
    if not es_email_valido(email):
        return jsonify({'error': 'El correo electrónico no es válido'}), 400

    try:
        resultado: Dict[str, Any] = empresa.iniciar_sesion(email,contraseña)
        
        if resultado.get('autenticado'):
            claims: Dict[str, Any] = {'rol': resultado['rol']}
            token: str = create_access_token(identity=email, additional_claims=claims)
            
            return jsonify ({
                'mensaje':'Inicio de sesion exitoso.',
                'token': token,
                'rol': resultado['rol'],
                'nombre': resultado['nombre'],
                'id_usuario': formatear_id(resultado['id_usuario'], 'U')
            }), 200
        
        else:
            return jsonify({'error': 'No se pudo autenticar al usuario'}), 401
        
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor {e}'}), 500
        

@app.route('/logout', methods=['POST'])
@jwt_required()
def logout() -> Tuple[Response, int]:
    """
    Invalida el token JWT actual del usuario añadiéndolo a una blocklist.

    Este endpoint permite a un usuario autenticado cerrar su sesión.
    El JTI (JWT ID) del token actual se extrae y se añade a `token_blocklist`.
    Flask-JWT-Extended, a través del `token_in_blocklist_loader`
    (la función `check_if_token_revoked`), verificará esta lista en futuras
    solicitudes para rechazar tokens revocados.

    Requiere
    --------
    Una cabecera `Authorization: Bearer <token_jwt>` válida.

    Returns
    -------
    Tuple[Response, int]
        Una tupla conteniendo una respuesta Flask (JSON) y un código de estado HTTP.
        - 200 OK: Si la sesión se cierra (token añadido a la blocklist) exitosamente.
        JSON: `{"mensaje": "Sesion cerrada exitosamente"}`
        - 500 Internal Server Error: Si ocurre un error inesperado al procesar el token.
        JSON: `{"error": "mensaje del error"}`
    """

    try:
        # Obtener el identificador único del token JWT
        jti = get_jwt()['jti']

        # Agregar el token a la lista de tokens usados (blocklist)
        token_blocklist.add(jti)

        return jsonify({'mensaje': 'Sesion cerrada exitosamente'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/usuarios/actualizar-contraseña/<string:email>', methods=['PUT'])
@jwt_required()
def actualizar_usuario(email: str) -> Tuple[Response, int]:
    """
    Actualiza la contraseña del usuario autenticado.

    Permite a un usuario cambiar su propia contraseña. El `email` proporcionado
    en la ruta DEBE coincidir con la identidad (email) del token JWT para autorizar
    la operación. La nueva contraseña se recibe en el cuerpo JSON de la solicitud.

    Parameters (URL)
    ----------------
    email : str  # Corresponde a <string:email> en la ruta
        El correo electrónico del usuario cuya contraseña se va a actualizar.
        Este email debe coincidir con el del usuario autenticado.

    Body (JSON)
    -----------
    nueva_contraseña : str
        La nueva contraseña deseada, en texto plano. Será hasheada por la
        lógica de negocio.

    Headers
    -------
    Authorization : str
        Token JWT válido. `Bearer <token_jwt>`.

    Returns
    -------
    Tuple[Response, int]
        Una tupla conteniendo una respuesta Flask (JSON) y un código de estado HTTP.
        - 200 OK: Si la contraseña se actualiza exitosamente.
        JSON: `{"mensaje": "Contraseña actualizada exitosamente"}`
        - 400 Bad Request: Si falta `nueva_contraseña` en el cuerpo JSON,
        o si la lógica de negocio devuelve un `ValueError`.
        JSON: `{"error": "mensaje descriptivo del error"}`
        - 401 Unauthorized: Si el token JWT no es válido o está ausente (manejado por `@jwt_required`).
        - 403 Forbidden: Si el `email` de la URL no coincide con la identidad del token JWT.
        JSON: `{"error": "Acceso no autorizado"}`
        - 500 Internal Server Error: Para otros errores inesperados en el servidor,
        incluyendo problemas al leer las claims del token o errores genéricos.
        JSON: `{"error": "mensaje del error"}`
    
    Notes
    -----
    - Utiliza `get_jwt()` para obtener las claims del token y `get_jwt_identity()` para la identidad.
    - Llama a `empresa.actualizar_contraseña_usuario` para la lógica de negocio.
    """


# --------------------------------------------------------------------------
# SECCIÓN 6: ENDPOINTS DE ADMINISTRACIÓN DE USUARIOS
# --------------------------------------------------------------------------    


@app.route('/listar-usuarios', methods=['GET'])
@jwt_required()
def listar_usuarios() -> Tuple[Response, int]:
    """
    Obtiene una lista de todos los usuarios registrados en el sistema.

    Este endpoint es accesible solo por usuarios con rol "admin".
    Devuelve información básica de cada usuario (ID formateado, nombre, tipo, email).
    La contraseña hasheada no se incluye.

    Headers
    -------
    Authorization : str
        Token JWT válido con la claim 'rol'="admin". `Bearer <token_jwt>`.

    Returns
    -------
    Tuple[Response, int]
        Una tupla conteniendo una respuesta Flask (JSON) y un código de estado HTTP.
        - 200 OK: Si la lista de usuarios se obtiene exitosamente.
        JSON: `{"mensaje": "Lista de usuarios obtenida exitosamente", "usuarios": [{"id_usuarios": "U001", "nombre": ..., "tipo": ..., "email": ...}, ...]}`
        - 403 Forbidden: Si el usuario autenticado no tiene rol "admin".
        JSON: `{"error": "Acceso no autorizado"}`
        - 404 Not Found: Si no hay usuarios registrados en el sistema.
        JSON: `{"error": "No hay usuarios registrados"}`
        - 500 Internal Server Error: Para errores al leer claims del token o
        errores internos inesperados durante la obtención de datos.
        JSON: `{"error": "mensaje del error"}`
    
    Notes
    -----
    - Llama a `empresa.obtener_usuarios()` para la lógica de negocio.
    - Utiliza `formatear_id` para el ID de usuario en la respuesta.
    """
    # Obtener las claims del token
    claims: Optional[Dict[str, Any]] = get_jwt()

    # Verificar si las claims son un diccionario
    if not isinstance(claims, dict):
        return jsonify({'error': 'Error al leer las claims del token'}), 500

    # Obtener el rol del usuario
    rol: Optional[str] = claims.get('rol')


    # Verificar si el rol es admin
    if rol != 'admin':
        return jsonify({'error': 'Acceso no autorizado'}), 403

    try:
        usuarios = empresa.obtener_usuarios()
        
        if not usuarios:
            return jsonify({'error': 'No hay usuarios registrados'}), 404
        
        usuarios_formateados = [
            {
                'id_usuarios' : formatear_id(usuario['id_usuario'], 'U'),
                'nombre':usuario['nombre'],
                'tipo': usuario['tipo'],
                'email': usuario['email']
            } for usuario in usuarios
        ]
        
        return jsonify({
            'mensaje': 'Lista de usuarios obtenida exitosamente',
            'usuarios':usuarios_formateados
        }), 200
    
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 404
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {e}'}), 500


@app.route('/usuarios/detalles/<string:email>', methods=['GET'])
@jwt_required()
def detalles_usuario(email: str) -> Tuple[Response, int]:
    """
    Obtiene los detalles de un usuario específico por su email.

    Permite a un administrador ver los detalles de cualquier usuario, o a un
    usuario cliente ver sus propios detalles. La autorización se basa en el rol
    del token JWT y si el `email` de la URL coincide con la identidad del token.

    Parameters (URL)
    ----------------
    email_param : str # Corresponde a <string:email> en la ruta
        Correo electrónico del usuario cuyos detalles se desean obtener.

    Headers
    -------
    Authorization : str
        Token JWT válido. `Bearer <token_jwt>`.

    Returns
    -------
    Tuple[Response, int]
        Una tupla conteniendo una respuesta Flask (JSON) y un código de estado HTTP.
        - 200 OK: Si los detalles se obtienen exitosamente.
        JSON: `{"mensaje": "Detalles del usuario ...", "usuario": {"id_usuario": "U001", "nombre": ..., ...}}`
        - 403 Forbidden: Si el usuario no tiene permiso para ver los detalles solicitados.
        JSON: `{"error": "Acceso no autorizado"}`
        - 404 Not Found: Si no se encuentra un usuario con el `email_param`
        (devuelto por `ValueError` de la capa de negocio).
        JSON: `{"error": "mensaje del error de ValueError"}`
        - 500 Internal Server Error: Para errores al leer claims o errores internos inesperados.
        JSON: `{"error": "mensaje del error"}`
    
    Notes
    -----
    - Llama a `empresa.obtener_usuario_por_email` para la lógica de negocio.
    - Utiliza `formatear_id` para el ID de usuario en la respuesta.
    """
    # Obtener las claims del token
    claims: Optional[Dict[str, Any]] = get_jwt()


    # Verificar si las claims son un diccionario
    if not isinstance(claims, dict):
        return jsonify({'error': 'Error al leer las claims del token'}), 500

    # Obtener el rol del usuario
    rol: Optional[str] = claims.get('rol')
    email_usuario_autenticado: Optional[str] = get_jwt_identity()

    # Verificar permisos
    if rol != 'admin' and email_usuario_autenticado != email:
        return jsonify({'error': 'Acceso no autorizado'}), 403

    try:
        
        usuario = empresa.obtener_usuario_por_email(email)
        
        usuario_formateado = {
            'id_usuario': formatear_id(usuario['id_usuario'],'U'),
            'nombre': usuario['nombre'],
            'tipo': usuario['tipo'],
            'email': usuario['email']
        }
        
        return jsonify({
            'mensaje': f'Detalles del usuario {email} obtenidos exitosamente',
            'usuario': usuario_formateado
        }), 200

    except ValueError as ve:
        return jsonify({'error': str(ve)}), 404
    except Exception:
        return jsonify({'error': 'Error interno del servidor'}), 500
    

# --------------------------------------------------------------------------
# SECCIÓN 7: ENDPOINTS DE GESTIÓN Y CONSULTA DE COCHES
# --------------------------------------------------------------------------


@app.route('/coches/registrar', methods=['POST'])
@jwt_required()
def registrar_coche() -> Tuple[Response, int]:
    """
    Registra un nuevo coche en el sistema.

    Este endpoint permite a un usuario con rol "admin" registrar un nuevo coche
    Todos los campos detallados en el cuerpo de la solicitud son obligatorios,
    y el campo `disponible` debe ser un valor booleano. Las validaciones de
    tipo y rango para campos como `año` se realizan en este endpoint.

    Body (JSON)
    -----------
    marca : str
        Marca del coche.
    modelo : str
        Modelo del coche.
    matricula : str
        Matrícula única del coche.
    categoria_tipo : str
        Tipo de categoría del coche (e.g., "Compacto", "SUV").
    categoria_precio : str
        Categoría de precio del coche (e.g., "Bajo", "Medio", "Alto").
    año : int or str
        Año de fabricación del coche. Se convertirá a entero.
        Debe estar entre 1900 y el año actual.
    precio_diario : float or str
        Precio diario de alquiler del coche. Se convertirá a float.
    kilometraje : float or str
        Kilometraje actual del coche. Se convertirá a float.
    color : str
        Color del coche.
    combustible : str
        Tipo de combustible del coche (e.g., "Gasolina", "Diésel").
    cv : int or str
        Potencia del coche en caballos de vapor (CV). Se convertirá a entero.
    plazas : int or str
        Número de plazas del coche. Se convertirá a entero.
    disponible : bool
        Indica si el coche está disponible para alquilar (`true` o `false` en JSON).

    Headers
    -------
    Authorization : str
        Token JWT válido con la claim 'rol'="admin". `Bearer <token_jwt>`.

    Returns
    -------
    Tuple[Response, int]
        Una tupla conteniendo una respuesta Flask (JSON) y un código de estado HTTP.
        - 201 Created: Si el coche se registra exitosamente.
        JSON: `{"mensaje": "Coche registrado con éxito", "id_coche": "UID<ID>"}`
        - 400 Bad Request: Si faltan campos obligatorios, los datos son inválidos
        (e.g., `año` fuera de rango, `disponible` no booleano), o si la lógica
        de negocio devuelve un `ValueError` (e.g., matrícula duplicada).
        JSON: `{"error": "mensaje descriptivo del error"}`
        - 403 Forbidden: Si el usuario autenticado no tiene rol "admin".
        JSON: `{"error": "Acceso no autorizado"}`
        - 500 Internal Server Error: Para errores al leer claims del token o
        errores internos inesperados durante la operación.
        JSON: `{"error": "mensaje del error"}`
    
    Notes
    -----
    - Llama a `empresa.registrar_coche` para la lógica de negocio.
    - Utiliza `formatear_id` para el ID del coche en la respuesta.
    - El endpoint realiza validaciones de tipo y rango para varios campos antes
    de pasarlos a la capa de negocio.
    """
    # Obtener las claims del token
    claims: Optional[Dict[str, Any]] = get_jwt()

    # Verificar si las claims son un diccionario
    if not isinstance(claims, dict):
        return jsonify({'error': 'Error al leer las claims del token'}), 500

    # Obtener el rol del usuario
    rol: Optional[str] = claims.get('rol')

    # Verificar si el rol es admin
    if rol != 'admin':
        return jsonify({'error': 'Acceso no autorizado'}), 403

    # Obtener los datos enviados en la solicitud
    data: Optional[Dict[str, Any]] = request.json
    marca: Optional[str] = data.get('marca')
    modelo: Optional[str] = data.get('modelo')
    matricula: Optional[str] = data.get('matricula')
    categoria_tipo: Optional[str] = data.get('categoria_tipo')
    categoria_precio: Optional[str] = data.get('categoria_precio')
    año: Optional[Union[int, str]] = data.get('año')
    precio_diario: Optional[Union[float, str, int]] = data.get('precio_diario')
    kilometraje: Optional[Union[float, str, int]] = data.get('kilometraje')
    color: Optional[str] = data.get('color')
    combustible: Optional[str] = data.get('combustible')
    cv: Optional[Union[int, str]] = data.get('cv')
    plazas: Optional[Union[int, str]] = data.get('plazas')
    disponible: Optional[bool] = data.get('disponible') 

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
        
        # Registrar el coche usando Empresa
        id_coche_generado = empresa.registrar_coche(
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
        )

        return jsonify({
            "mensaje": "Coche registrado con éxito",
            "id_coche": formatear_id(id_coche_generado, "UID")
        }), 201

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print(f"Error interno: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route('/coches/actualizar-matricula/<string:id_coche>', methods=['PUT'])
@jwt_required()
def actualizar_matricula(id_coche: str) -> Tuple[Response, int]:
    """
    Actualiza la matrícula de un coche específico.

    Este endpoint permite a un usuario con rol "admin" actualizar la matrícula
    de un coche existente, identificado por su `id_coche_url` (formato "UIDXXX").
    La nueva matrícula se proporciona en el cuerpo JSON de la solicitud.

    Parameters (URL)
    ----------------
    id_coche_url : str # Corresponde a <string:id_coche> en la ruta
        ID formateado del coche (e.g., "UID001") cuya matrícula se desea actualizar.

    Body (JSON)
    -----------
    nueva_matricula : str
        La nueva matrícula que se asignará al coche.

    Headers
    -------
    Authorization : str
        Token JWT válido con la claim 'rol'="admin". `Bearer <token_jwt>`.

    Returns
    -------
    Tuple[Response, int]
        Una tupla conteniendo una respuesta Flask (JSON) y un código de estado HTTP.
        - 200 OK: Si la matrícula se actualiza exitosamente.
        JSON: `{"mensaje": "Matrícula del coche con ID <id_coche_url> actualizada exitosamente"}`
        - 400 Bad Request: Si falta `nueva_matricula` en el cuerpo JSON,
        si la nueva matrícula es inválida, o si la lógica de negocio
        devuelve un `ValueError` (e.g., ID de coche inválido, coche no encontrado,
        nueva matrícula ya en uso).
        JSON: `{"error": "mensaje descriptivo del error"}`
        - 403 Forbidden: Si el usuario autenticado no tiene rol "admin".
        JSON: `{"error": "Acceso no autorizado"}`
        - 404 Not Found: (No explícito aquí, pero `ValueError` podría cubrirlo si `empresa` lo lanza)
        - 500 Internal Server Error: Para errores al leer claims o errores internos inesperados.
        JSON: `{"error": "mensaje del error"}`
    
    Notes
    -----
    - Llama a `empresa.actualizar_matricula` para la lógica de negocio.
    - El `id_coche_url` se pasa a la capa de negocio, que es responsable de
    convertirlo al ID numérico si es necesario.
    """
    
    claims: Optional[Dict[str, Any]] = get_jwt()

    # Verificar si las claims son un diccionario
    if not isinstance(claims, dict):
        return jsonify({'error': 'Error al leer las claims del token'}), 500

    rol: Optional[str] = claims.get('rol')

    # Comprobar que el usuario es admin
    if rol != 'admin':
        return jsonify({'error': 'Acceso no autorizado'}), 403

    data: Optional[Dict[str, Any]] = request.json
    nueva_matricula: Optional[str] = data.get('nueva_matricula')

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
    

@app.route('/coches-disponibles', methods=['GET'])
def buscar_coches_disponibles() -> Tuple[Response, int]:
    """
    Busca coches disponibles o atributos de coches (tipos, marcas, modelos)
    basado en una serie de filtros progresivos.

    Este endpoint público permite a los usuarios buscar coches.
    - Si solo se proporciona `categoria_precio`, devuelve los tipos de categoría disponibles.
    - Si se proporcionan `categoria_precio` y `categoria_tipo`, devuelve las marcas disponibles.
    - Si se proporcionan `categoria_precio`, `categoria_tipo` y `marca`, devuelve los modelos disponibles.
    - Si se proporcionan todos los filtros (`categoria_precio`, `categoria_tipo`, `marca`, `modelo`),
    devuelve los detalles de los coches que coinciden.

    Query Parameters (URL)
    ----------------------
    categoria_precio : str
        Categoría de precio para filtrar (obligatoria).
    categoria_tipo : str, optional
        Tipo de categoría para filtrar.
    marca : str, optional
        Marca del coche para filtrar.
    modelo : str, optional
        Modelo del coche para filtrar.

    Returns
    -------
    Tuple[Response, int]
        Una tupla conteniendo una respuesta Flask (JSON) y un código de estado HTTP.
        - 200 OK: Si la búsqueda es exitosa. El contenido del JSON varía:
            - `{"categorias_tipo": ["Tipo1", "Tipo2", ...]}`
            - `{"marcas": ["Marca1", "Marca2", ...]}`
            - `{"modelos": ["Modelo1", "Modelo2", ...]}`
            - `{"detalles": [{"id": ..., "marca": ..., "modelo": ..., ...}, ...]}`
        - 400 Bad Request: Si `categoria_precio` no se proporciona o si la lógica de negocio
        devuelve un `ValueError` (e.g., filtros inválidos o no se encuentran resultados
        si la capa inferior lanza error en lugar de lista vacía).
        JSON: `{"error": "mensaje descriptivo del error"}`
        - 500 Internal Server Error: Para errores de base de datos u otros errores inesperados.
        JSON: `{"error": "mensaje del error"}`
    
    Notes
    -----
    - Llama a `empresa.buscar_coches_por_filtros` que implementa la lógica de
    búsqueda progresiva y devuelve diferentes tipos de datos.
    - No requiere autenticación.
    """
    try:
        # Obtener los parámetros de la solicitud
        categoria_precio: Optional[str] = request.args.get('categoria_precio')
        categoria_tipo: Optional[str] = request.args.get('categoria_tipo')
        marca: Optional[str] = request.args.get('marca')
        modelo: Optional[str] = request.args.get('modelo')
        
        # Validar que al menos se proporcione una categoría de precio
        if not categoria_precio:
            raise ValueError("Se requiere al menos el parámetro 'categoria_precio'.")

        # Obtener los detalles de los coches
        coches_filtrados = empresa.buscar_coches_por_filtros(categoria_precio=categoria_precio, categoria_tipo=categoria_tipo, marca=marca, modelo=modelo)
        # Estructura de respuesta según nivel de filtro
        if modelo and marca and categoria_tipo: # Implica que todos están presentes
            return jsonify({'detalles': coches_filtrados}), 200
        elif marca and categoria_tipo: # Implica que modelo es None o vacío
            return jsonify({'modelos': coches_filtrados}), 200
        elif categoria_tipo: # Implica que marca y modelo son None o vacíos
            return jsonify({'marcas': coches_filtrados}), 200
        else: # Solo categoria_precio está presente
            return jsonify({'categorias_tipo': coches_filtrados}), 200

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except MySQLError as dbe: # Captura errores de MySQL específicamente
        # print(f"DEBUG Endpoint: Error de BD capturado: {dbe}") # Para el log del servidor
        return jsonify({"error": f"Error de base de datos: {dbe}"}), 500
    except Exception:
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route('/coches/detalles/<string:matricula>', methods=['GET'])
def detalles_coche(matricula: str) -> Tuple[Response, int]:
    """
    Obtiene y devuelve los detalles de un coche específico mediante su matrícula.

    Este endpoint público permite a cualquier usuario consultar la información
    completa de un coche proporcionando su matrícula en la URL.
    Los datos del coche se formatean antes de ser devueltos.

    Parameters (URL)
    ----------------
    matricula : str # Corresponde a <string:matricula> en la ruta
        La matrícula del coche cuyos detalles se desean obtener.

    Returns
    -------
    Tuple[Response, int]
        Una tupla conteniendo una respuesta Flask (JSON) y un código de estado HTTP.
        - 200 OK: Si se encuentran los detalles del coche.
        JSON: `{"mensaje": "Detalles del coche obtenidos exitosamente", "coche": {"id": "UID...", "marca": ..., ...}}`
        - 404 Not Found: Si no se encuentra ningún coche con la matrícula proporcionada
        (ya sea porque `empresa.obtener_detalle_coche_por_matricula` devuelve `None`
        o porque lanza un `ValueError` que indica "no encontrado").
        JSON: `{"error": "Coche no encontrado"}` o el mensaje de `ValueError`.
        - 500 Internal Server Error: Para otros errores inesperados, incluyendo
        errores de base de datos si no son capturados como `ValueError`.
        JSON: `{"error": "<detalle_del_error>"}`
    
    Notes
    -----
    - No requiere autenticación.
    - Llama a `empresa.obtener_detalle_coche_por_matricula` para la lógica de negocio.
    - Utiliza `formatear_id` para el ID del coche en la respuesta.
    - Realiza conversiones de tipo explícitas (e.g., `float()`, `bool()`) para los
    campos en la respuesta formateada.
    """
    try:
        # Llamar a Empresa para obtener el coche por matricula
        coche = empresa.obtener_detalle_coche_por_matricula(matricula)

        if not coche:
            return jsonify({'error': 'Coche no encontrado'}), 404

        # Formatear respuesta final
        coche_formateado = {
            "id": formatear_id(coche['id'], "UID"),
            "marca": coche['marca'],
            "modelo": coche['modelo'],
            "matricula": coche['matricula'],
            "categoria_tipo": coche['categoria_tipo'],
            "categoria_precio": coche['categoria_precio'],
            "año": coche['año'],
            "precio_diario": float(coche['precio_diario']),
            "kilometraje": float(coche['kilometraje']),
            "color": coche['color'],
            "combustible": coche['combustible'],
            "cv": coche['cv'],
            "plazas": coche['plazas'],
            "disponible": bool(coche['disponible'])
        }

        return jsonify({
            "mensaje": "Detalles del coche obtenidos exitosamente",
            "coche": coche_formateado
        }), 200

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404
    except Exception as e:
        return jsonify({"error": f"{e}"}), 500


@app.route('/coches/categorias/precio', methods=['GET'])
def categorias_precio() -> Tuple[Response, int]:
    """
    Obtiene una lista de todas las categorías de precio de coches disponibles.

    Este endpoint público consulta y devuelve una lista única y ordenada de las
    categorías de precio existentes para los coches disponibles en el sistema.

    Returns
    -------
    Tuple[Response, int]
        Una tupla conteniendo una respuesta Flask (JSON) y un código de estado HTTP.
        - 200 OK: Si las categorías se obtienen exitosamente (incluso si la lista está vacía).
        JSON: `{"mensaje": "Categorías de precio obtenidas exitosamente", "categorias_precio": ["Precio1", "Precio2", ...]}`
        - 404 Not Found: Si `empresa.mostrar_categorias_precio` lanza un `ValueError`
        (por ejemplo, si la lógica de negocio considera un error no encontrar categorías,
        aunque típicamente devolvería una lista vacía).
        JSON: `{"error": "mensaje del ValueError"}`
        - 500 Internal Server Error: Para errores de base de datos u otros errores inesperados.
        JSON: `{"error": "Error interno del servidor: <detalle_del_error>"}`
    
    Notes
    -----
    - No requiere autenticación.
    - Llama a `empresa.mostrar_categorias_precio` (o `empresa.obtener_categorias_precio`)
    para la lógica de negocio.
    - Si no hay categorías, se devuelve una lista vacía con un mensaje de éxito.
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
def categorias_tipo()-> Tuple[Response, int]:
    """
    Obtiene una lista de todas las categorías de tipo de coches disponibles.

    Este endpoint público consulta y devuelve una lista única y ordenada de los
    tipos de categoría existentes para los coches disponibles en el sistema.

    Returns
    -------
    Tuple[Response, int]
        Una tupla conteniendo una respuesta Flask (JSON) y un código de estado HTTP.
        - 200 OK: Si las categorías se obtienen exitosamente (incluso si la lista está vacía).
        JSON: `{"mensaje": "Categorías de tipo obtenidas exitosamente", "categorias_tipo": ["Tipo1", "Tipo2", ...]}`
        - 404 Not Found: Si `empresa.mostrar_categorias_tipo` lanza un `ValueError`.
        JSON: `{"error": "mensaje del ValueError"}`
        - 500 Internal Server Error: Para errores de base de datos u otros errores inesperados.
        JSON: `{"error": "Error interno del servidor: <detalle_del_error>"}`
    Notes
    -----
    - No requiere autenticación.
    - Llama a `empresa.mostrar_categorias_tipo` (o `empresa.obtener_categorias_tipo`)
    para la lógica de negocio.
    - Si no hay categorías, se devuelve una lista vacía con un mensaje de éxito.
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


# --------------------------------------------------------------------------
# SECCIÓN 8: ENDPOINTS DE GESTIÓN Y CONSULTA DE ALQUILERES
# --------------------------------------------------------------------------


@app.route('/alquilar-coche', methods=['POST'])
@jwt_required(optional=True)
def alquilar_coches()-> Union[Response, Tuple[Response, int]]:
    """
    Registra un nuevo alquiler de coche y devuelve la factura en PDF.

    Permite a usuarios autenticados (clientes) o invitados registrar un alquiler.
    - Si se proporciona un token JWT y el usuario no es admin, se usa su identidad (email).
    - Si se proporciona un email en el cuerpo JSON, se usa ese (prioridad si está logueado y también lo envía).
    - Si no hay token ni email en el cuerpo, se considera un alquiler de invitado.
    - Administradores no pueden alquilar coches.

    Body (JSON)
    -----------
    matricula : str
        Matrícula del coche a alquilar.
    fecha_inicio : str
        Fecha de inicio del alquiler en formato 'YYYY-MM-DD'.
    fecha_fin : str
        Fecha de fin del alquiler en formato 'YYYY-MM-DD'.
    email : str, optional
        Correo electrónico del usuario. Si el usuario está autenticado y este campo
        no se proporciona, se intentará usar el email del token. Si no hay token
        y no se proporciona email, se considera un alquiler de invitado.

    Headers
    -------
    Authorization : str, optional
        Token JWT. Si está presente y es válido, se usa para identificar al usuario
        y su rol. `Bearer <token_jwt>`.

    Returns
    -------
    Union[Response, Tuple[Response, int]]
        - Response (con contenido PDF): Si el alquiler es exitoso, se devuelve
        directamente el archivo PDF de la factura con `Content-Type: application/pdf`
        y `Content-Disposition: attachment; filename=factura.pdf`. El código de estado
        será 200 OK por defecto si no se especifica.
        - Tuple[Response, int] (con JSON y código de estado): En caso de error.
            - 400 Bad Request: Campos faltantes, formato de fecha incorrecto, o
            `ValueError` de la lógica de negocio (e.g., coche no disponible,
            usuario no encontrado, fechas inválidas).
            JSON: `{"error": "mensaje descriptivo"}`
            - 403 Forbidden: Si el usuario autenticado es un administrador.
            JSON: `{"error": "Los administradores no pueden alquilar coches"}`
            - 500 Internal Server Error: Para otros errores inesperados.
            JSON: `{"error": "Error interno del servidor..."}`
    
    Notes
    -----
    - Llama a `empresa.alquilar_coche` para la lógica de negocio, que a su vez
    genera el PDF.
    - Utiliza `make_response` para construir la respuesta HTTP con el archivo PDF.
    """
    data: Optional[Dict[str, Any]] = request.json
    matricula: Optional[str] = data.get('matricula')
    fecha_inicio: Optional[str] = data.get('fecha_inicio') # Recibido como string
    fecha_fin: Optional[str] = data.get('fecha_fin')       # Recibido como string
    email: Optional[str] = data.get('email')          

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
        return jsonify({'error': f'Error interno del servidor. Por favor, inténtalo de nuevo más tarde: {e}'}), 500
    

@app.route('/alquileres/listar', methods=['GET'])
@jwt_required()
def listar_alquileres() -> Tuple[Response, int]:
    """
    Obtiene una lista de todos los alquileres registrados en el sistema.

    Este endpoint es accesible solo por usuarios con rol "admin". Devuelve una lista
    completa de los alquileres, incluyendo información formateada del alquiler,
    coche (ID y matrícula) y usuario asociado.

    Headers
    -------
    Authorization : str
        Token JWT válido con la claim 'rol'="admin". `Bearer <token_jwt>`.

    Returns
    -------
    Tuple[Response, int]
        Una tupla conteniendo una respuesta Flask (JSON) y un código de estado HTTP.
        - 200 OK: Si la lista de alquileres se obtiene exitosamente.
        JSON: `{"mensaje": "Lista de alquileres obtenida exitosamente.", "alquileres": [...]}`
        (la estructura de cada alquiler en la lista se detalla en el código).
        - 403 Forbidden: Si el usuario autenticado no tiene rol "admin".
        JSON: `{"error": "Acceso no autorizado"}`
        - 404 Not Found: Si `empresa.cargar_alquileres` lanza un `ValueError` (por ejemplo,
        si la lógica de negocio considera un error no encontrar alquileres, aunque
        típicamente devolvería una lista vacía).
        JSON: `{"error": "mensaje del ValueError"}`
        - 500 Internal Server Error: Para errores al leer claims o errores internos
        inesperados durante la obtención o formateo de datos.
        JSON: `{"error": "mensaje del error"}`
    
    Notes
    -----
    - Llama a `empresa.cargar_alquileres()` para obtener los datos de los alquileres.
    - Se asume que `empresa.cargar_alquileres()` devuelve una lista de diccionarios,
    donde cada diccionario ya incluye `id_alquiler`, `id_coche`, `id_usuario`,
    `matricula`, `fecha_inicio` (como objeto date/datetime), `fecha_fin` (como
    objeto date/datetime), `coste_total`, y `activo`.
    - Utiliza `formatear_id` para los IDs en la respuesta.
    - Las fechas se formatean como strings 'YYYY-MM-DD'.
    - `coste_total` y `activo` se convierten a `float` y `bool` respectivamente.
    """
    # Obtener las claims del token
    claims: Optional[Dict[str, Any]] = get_jwt()

    # Verificar si las claims son un diccionario
    if not isinstance(claims, dict):
        return jsonify({'error': 'Error al leer las claims del token'}), 500

    # Obtener el rol del usuario
    rol: Optional[str] = claims.get('rol')

    # Verificar si el rol es admin
    if rol != 'admin':
        return jsonify({'error': 'Acceso no autorizado'}), 403

    try:
        # Cargar alquileres
        alquileres = empresa.cargar_alquileres()
        
        # Formatear IDs solo al mostrarlos al cliente
        alquileres_formateados = []
        for alquiler in alquileres:
            alquiler_formateado = {
                "id_alquiler": formatear_id(alquiler["id_alquiler"], "A"),
                "id_coche": formatear_id(alquiler["id_coche"], "UID"),
                "id_usuario": formatear_id(alquiler["id_usuario"], "U") if alquiler["id_usuario"] else "INVITADO",
                "matricula": alquiler["matricula"],
                "fecha_inicio": alquiler["fecha_inicio"].strftime("%Y-%m-%d"),
                "fecha_fin": alquiler["fecha_fin"].strftime("%Y-%m-%d"),
                "coste_total": float(alquiler["coste_total"]),
                "activo": bool(alquiler["activo"])
            }
            alquileres_formateados.append(alquiler_formateado)

        return jsonify({
            "mensaje": "Lista de alquileres obtenida exitosamente.",
            "alquileres": alquileres_formateados
        }), 200

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404
    except Exception as e:
        print(f"Error interno: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500
        
    

@app.route('/alquileres/detalles/<string:id_alquiler>', methods=['GET'])
@jwt_required()
def detalles_alquiler(id_alquiler: str) -> Tuple[Response, int]:
    """
    Obtiene los detalles de un alquiler específico por su ID.

    Permite a un administrador ver los detalles de cualquier alquiler.
    Un usuario cliente solo puede ver los detalles de un alquiler si el `id_usuario`
    asociado al alquiler (obtenido de la base de datos) coincide con la identidad
    (email) del usuario autenticado.
    El ID del alquiler se espera en formato "AXXX" (e.g., "A001").

    Parameters (URL)
    ----------------
    id_alquiler : str # Corresponde a <string:id_alquiler> en la ruta
        ID único del alquiler (formato "AXXX") cuyos detalles se desean obtener.

    Headers
    -------
    Authorization : str
        Token JWT válido. `Bearer <token_jwt>`. Debe contener claims para 'rol'
        y la identidad del usuario (email).

    Returns
    -------
    Tuple[Response, int]
        Una tupla conteniendo una respuesta Flask (JSON) y un código de estado HTTP.
        - 200 OK: Si los detalles del alquiler se obtienen y formatean exitosamente.
        JSON: `{"mensaje": "Detalles del alquiler...", "alquiler": {"id_alquiler": "A...", ...}}`
        (la estructura de `alquiler` se detalla en el código).
        - 403 Forbidden: Si el usuario autenticado no es "admin" y el `id_usuario`
        del alquiler no coincide con la identidad del token.
        JSON: `{"error": "Acceso no autorizado"}`
        - 404 Not Found: Si no se encuentra ningún alquiler con el ID proporcionado
        (generalmente capturado como `ValueError` desde la capa de negocio).
        JSON: `{"error": "mensaje del ValueError"}`
        - 500 Internal Server Error: Para errores al leer claims, errores de base de datos
        no capturados como `ValueError`, o errores internos inesperados durante
        el procesamiento o formateo.
        JSON: `{"error": "mensaje del error"}`

    Notes
    -----
    - Llama a `empresa.obtener_alquiler_por_id` para la lógica de negocio.
    - Es crucial que `empresa.obtener_alquiler_por_id` devuelva el `id_usuario`
    (numérico, no el email) del alquiler para la verificación de permisos.
    Si `empresa.obtener_alquiler_por_id` devuelve `None` o lanza `ValueError`
    cuando el alquiler no se encuentra, este endpoint lo manejará como 404.
    - El `id_usuario` en la respuesta JSON se formatea, pero la comparación para
    autorización se hace con el `id_usuario` numérico del alquiler vs el `email_usuario_autenticado`.
      **Esto implica que la lógica de autorización `email_usuario_autenticado != id_usuario_alquiler`
    necesita una revisión si `id_usuario_alquiler` es un ID numérico y
    `email_usuario_autenticado` es un email. Se necesitaría obtener el email del
    usuario del alquiler para una comparación directa, o comparar IDs numéricos.**
    (Mantendré la lógica original, pero esto es un punto importante).
    """
    # Obtener las claims del token
    claims: Optional[Dict[str, Any]] = get_jwt()

    # Verificar si las claims son un diccionario
    if not isinstance(claims, dict):
        return jsonify({'error': 'Error al leer las claims del token'}), 500

    # Obtener el rol y el email del usuario autenticado
    rol: Optional[str] = claims.get('rol')
    email_usuario_autenticado: Optional[str] = get_jwt_identity()

    try:
        # Llamar a Empresa para obtener el alquiler por ID
        alquiler = empresa.obtener_alquiler_por_id(id_alquiler)

        # Extraer datos del alquiler
        id_usuario_alquiler = alquiler.get("id_usuario")

        # Validar permisos
        if rol != 'admin' and email_usuario_autenticado != id_usuario_alquiler:
            return jsonify({'error': 'Acceso no autorizado'}), 403

        # Formatear IDs solo al mostrarlos al usuario final
        alquiler_formateado = {
            "id_alquiler": formatear_id(alquiler["id_alquiler"], "A"),
            "id_coche": formatear_id(alquiler["id_coche"], "UID"),
            "id_usuario": formatear_id(alquiler["id_usuario"], "U") if id_usuario_alquiler else "INVITADO",
            "fecha_inicio": alquiler["fecha_inicio"].strftime("%Y-%m-%d"),
            "fecha_fin": alquiler["fecha_fin"].strftime("%Y-%m-%d"),
            "coste_total": float(alquiler["coste_total"]),
            "activo": bool(alquiler["activo"])
        }

        return jsonify({
            "mensaje": f"Detalles del alquiler {id_alquiler} obtenidos exitosamente.",
            "alquiler": alquiler_formateado
        }), 200

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404
    except Exception as e:
        print(f"Error interno: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500
    

@app.route('/alquileres/finalizar/<string:id_alquiler>', methods=['PUT'])
@jwt_required()
def finalizar_alquiler(id_alquiler: str)-> Tuple[Response, int]:
    """
    Finaliza un alquiler específico, marcándolo como inactivo y liberando el coche.

    Permite a un administrador finalizar cualquier alquiler, o a un usuario cliente
    finalizar sus propios alquileres. La autorización se basa en el rol del token JWT
    y si el `id_usuario` asociado al alquiler (obtenido de la BD) coincide con la
    identidad del usuario autenticado.
    El ID del alquiler se espera en formato "AXXX" (e.g., "A001").

    Parameters (URL)
    ----------------
    id_alquiler : str # Corresponde a <string:id_alquiler> en la ruta
        ID único del alquiler (formato "AXXX") que se desea finalizar.

    Headers
    -------
    Authorization : str
        Token JWT válido. `Bearer <token_jwt>`. Debe contener claims para 'rol'
        y la identidad del usuario (email).

    Returns
    -------
    Tuple[Response, int]
        Una tupla conteniendo una respuesta Flask (JSON) y un código de estado HTTP.
        - 200 OK: Si el alquiler se finaliza exitosamente.
        JSON: `{"mensaje": "Alquiler <id_alquiler_url> finalizado correctamente.", "id_coche": "UID<ID_COCHE>"}`
        - 400 Bad Request: Si el alquiler ya está finalizado.
        JSON: `{"error": "El alquiler ya está finalizado."}`
        - 403 Forbidden: Si el usuario autenticado no tiene permiso para finalizar
        el alquiler solicitado.
        JSON: `{"error": "Acceso no autorizado"}`
        - 404 Not Found: Si no se encuentra ningún alquiler con el ID proporcionado
        (generalmente capturado como `ValueError` desde la capa de negocio).
        JSON: `{"error": "mensaje del ValueError"}`
        - 500 Internal Server Error: Para errores al leer claims, errores de base de datos
        no capturados como `ValueError`, o si `empresa.finalizar_alquiler` devuelve `False`
        inesperadamente, o para otros errores internos.
        JSON: `{"error": "mensaje del error"}`
    
    Notes
    -----
    - Primero llama a `empresa.obtener_alquiler_por_id` para verificar el estado
    del alquiler y obtener datos para la autorización.
    - Luego llama a `empresa.finalizar_alquiler` para la lógica de negocio.
    - La misma advertencia sobre la comparación `email_usuario_autenticado != id_usuario_alquiler`
    aplica aquí como en `detalles_alquiler` si los tipos/valores no son directamente comparables.
    """
    # Obtener las claims del token
    claims: Optional[Dict[str, Any]] = get_jwt()

    # Verificar si las claims son un diccionario
    if not isinstance(claims, dict):
        return jsonify({'error': 'Error al leer las claims del token'}), 500

    # Obtener el rol y el email del usuario autenticado
    rol: Optional[str] = claims.get('rol')
    email_usuario_autenticado: Optional[str] = get_jwt_identity()

    try:
        
        alquiler = empresa.obtener_alquiler_por_id(id_alquiler)
        # Validar si el alquiler ya está terminado
        if not alquiler['activo']:
            return jsonify({"error": "El alquiler ya está finalizado."}), 400

        # Extraer datos del alquiler
        id_usuario_alquiler = alquiler.get("id_usuario")
        id_coche_alquiler = alquiler.get("id_coche")

        # Verificar autorización
        if rol != 'admin' and email_usuario_autenticado != id_usuario_alquiler:
            return jsonify({"error": "Acceso no autorizado"}), 403

        # Llamar al método para finalizar el alquiler
        resultado = empresa.finalizar_alquiler(id_alquiler)

        if resultado:
            return jsonify({
                "mensaje": f"Alquiler {id_alquiler} finalizado correctamente.",
                "id_coche": formatear_id(id_coche_alquiler, prefijo="UID")
            }), 200
        else:
            return jsonify({"error": "No se pudo finalizar el alquiler."}), 500

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404
    except Exception as e:
        print(f"Error interno: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route('/alquileres/historial/<string:email>', methods=['GET'])
@jwt_required()
def historial_alquileres(email: str) -> Tuple[Response, int]:
    """
    Obtiene el historial de alquileres de un usuario específico por su email.

    Permite a un administrador ver el historial de cualquier usuario, o a un
    usuario cliente ver su propio historial. La autorización se basa en el rol
    del token JWT y si el `email` de la URL coincide con la identidad
    (email) del usuario autenticado.

    Parameters (URL)
    ----------------
    email : str # Corresponde a <string:email> en la ruta
        Correo electrónico del usuario cuyo historial de alquileres se desea obtener.

    Headers
    -------
    Authorization : str
        Token JWT válido. `Bearer <token_jwt>`. Debe contener claims para 'rol'
        y la identidad del usuario (email).

    Returns
    -------
    Tuple[Response, int]
        Una tupla conteniendo una respuesta Flask (JSON) y un código de estado HTTP.
        - 200 OK: Si el historial se obtiene y formatea exitosamente (incluso si está vacío).
        JSON: `{"mensaje": "Historial de alquileres del usuario...", "alquileres": [...]}`
        (la estructura de cada alquiler en la lista se detalla en el código de formateo).
        - 403 Forbidden: Si el usuario autenticado no es "admin" y el `email_param`
        no coincide con la identidad del token.
        JSON: `{"error": "Acceso no autorizado"}`
        - 404 Not Found: Si no se encuentra un usuario con el `email_param` (generalmente
        capturado como `ValueError` desde la capa de negocio).
        JSON: `{"error": "mensaje del ValueError"}`
        - 500 Internal Server Error: Para errores al leer claims, errores de base de datos
        no capturados como `ValueError`, o errores internos inesperados durante
        el procesamiento o formateo.
        JSON: `{"error": "mensaje del error"}`
    
    Notes
    -----
    - Llama a `empresa.obtener_historial_alquileres` para la lógica de negocio.
    - Se asume que `empresa.obtener_historial_alquileres` devuelve una lista de
    diccionarios, donde cada diccionario ya incluye todos los datos necesarios,
    incluida la `matricula` del coche.
    - Utiliza `formatear_id` para los IDs en la respuesta.
    - Las fechas se formatean como strings 'YYYY-MM-DD'.
    """
    claims = get_jwt()
    rol = claims.get('rol')
    email_usuario_autenticado = get_jwt_identity()

    # Verificar autorización
    if rol != 'admin' and email != email_usuario_autenticado:
        return jsonify({'error': 'Acceso no autorizado'}), 403

    try:
        connection = empresa.get_connection()

        # Obtener el historial desde MySQL usando el método adaptado
        resultados = empresa.obtener_historial_alquileres(email)

        # Formatear los resultados antes de devolverlos
        historial_formateado = []
        for alquiler in resultados:
            historial_formateado.append({
                "id_alquiler": formatear_id(alquiler["id_alquiler"], prefijo="A"),
                "id_coche": formatear_id(alquiler["id_coche"], prefijo="UID"),
                "matricula": alquiler["matricula"],
                "fecha_inicio": alquiler["fecha_inicio"].strftime("%Y-%m-%d"),
                "fecha_fin": alquiler["fecha_fin"].strftime("%Y-%m-%d"),
                "coste_total": float(alquiler["coste_total"]),
                "activo": bool(alquiler["activo"])
            })

        return jsonify({
            "mensaje": f"Historial de alquileres del usuario {email}",
            "alquileres": historial_formateado #cuando acabe debug cambiar a historial_formateado
        }), 200

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404
    except Exception as e:
        return jsonify({"error": f"{e}"}), 500
        


if __name__ == '__main__':
    app.run(debug=True)