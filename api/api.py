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
def signup(): # Registrar
    data = request.json
    nombre = data.get('nombre')
    tipo = data.get('tipo','cliente') # Por defecto aplicamos cliente
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
        if empresa.registrar_usuario(nombre=nombre,tipo=tipo,email=email,contraseña=contraseña):
            return jsonify({'mensaje': 'Usuario registrado exitosamente' }), 201
        else:
            return jsonify({'error': 'No se pudo registrar el usuario'}), 500
    except ValueError as e:
        return jsonify({'error':str(e)}), 400


@app.route('/login', methods=['POST'])
def login(): # iniciar sesion
    data = request.json
    email = data.get('email')
    contraseña = data.get('contraseña')
    
    # validar campos 
    if not email or not contraseña:
        return jsonify({'error': 'Correo electronico y contraseña son obligatorios'}), 400
    
    # Validar el formato del correo electrónico
    if not empresa.es_email_valido(email):
        return jsonify({'error': 'El correo electrónico no es válido'}), 400
    
    try:
        # verificar las credenciales
        if empresa.iniciar_sesion(email,contraseña):
            # Obtener el rol de usuario
            df_usuarios = empresa.cargar_usuarios()
            usuario = df_usuarios[df_usuarios['email'] == email]
            rol = usuario.iloc[0]['tipo']
            
            # generar token con el rol
            token = create_access_token(identity=email, additional_claims={'rol':rol})
            return jsonify({'mensaje': 'Inicio de sesion exitoso', 'token':token}), 200
        else:
            return jsonify({'error':'Credenciales invalidas'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/logout',methods=['POST'])
@jwt_required()
def logout():
    # Obtener el identificar unico
    jti = get_jwt()['jti']
    
    # Agregamos el token a la lista de tokens usados
    token_blocklist.add(jti)
    
    return jsonify({'mensaje':'Sesion cerrada exitosamente'}), 200

@app.route('/usuarios/eliminar', methods=['DELETE'])
@jwt_required()
def eliminar_usuario():
    # Obtener las claims del token
    claims = get_jwt()

    # Verificar si las claims son un diccionario
    if not isinstance(claims, dict):
        return jsonify({'error': 'Error al leer las claims del token'}), 500

    if not empresa.es_email_valido(email):
        return jsonify({'error': 'El correo electrónico no es válido'}), 400
    # Obtener el rol del usuario
    rol = claims.get('rol')

    # Verificar si el rol es admin
    if rol != 'admin':
        return jsonify({'error': 'Acceso no autorizado'}), 403

    # Obtener el correo del usuario a eliminar desde los parámetros
    email = request.args.get('email')
    if not email:
        return jsonify({'mensaje': 'El correo electrónico es obligatorio'}), 400

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
def listar_usuarios():
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
        # cargar usuarios
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
        return jsonify({'error':{str(e)}}), 500


@app.route('/usuarios/detalles/<string:email>', methods=['GET'])
@jwt_required()
def detalles_usuario(email):
    # Obtener las claims del token
    claims = get_jwt()

    # Verificar si las claims son un diccionario
    if not isinstance(claims, dict):
        return jsonify({'error': 'Error al leer las claims del token'}), 500
    
    # Obtener el rol del usuario
    rol = claims.get('rol')
    email_usuario_autenticado = get_jwt_identity()
    try: 
        # cargar usuarios
        df_usuarios = empresa.cargar_usuarios()
        if df_usuarios is None or df_usuarios.empty:
            return jsonify({'error': 'No hay usuarios registrados'}), 200
        
        usuario = df_usuarios[df_usuarios['email'] == email]
        if usuario.empty:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        if rol != 'admin' and email_usuario_autenticado != email:
            return jsonify({'error':'Acceso no autorizado'}), 403
        
        usuario = usuario.iloc[0].to_dict
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
def actualizar_usuario(email):
    claims = get_jwt()

    # Verificar si las claims son un diccionario
    if not isinstance(claims, dict):
        return jsonify({'error': 'Error al leer las claims del token'}), 500
    
    email_usuario_autenticado = get_jwt_identity()
    
    # Comprobar que el usuario esta intentando cambiar sus propios datos
    if email_usuario_autenticado != email:
        return jsonify({'error': 'Acceso no autorizado'}),403
    
    data = request.json
    nueva_contraseña = data.get('nueva_contraseña')
    
    if not nueva_contraseña:
        return jsonify({'error': 'Debes proporcionar una nueva contraseña'}), 400
    
    try: 
        empresa.actualizar_usuario(email=email, nueva_contraseña=nueva_contraseña)
        return jsonify({'mensaje': 'Contraseña actualizada exitosamente'}), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error':{str(e)}}), 500

# ---------------------------------------
# ENDPOINTS RELACIONADOS CON BUSQUEDAS
# ---------------------------------------

@app.route('/coches-disponibles', methods=['GET'])
def buscar_coches_disponibles():
    try:
        categoria_precio = request.args.get('categoria_precio')
        categoria_tipo = request.args.get('categoria_tipo')
        marca = request.args.get('marca')
        modelo = request.args.get('modelo')

        # Obtener los detalles de los coches
        detalles = empresa.obtener_detalles_coches(categoria_precio, categoria_tipo, marca, modelo)
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
def alquilar_coches():
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
def listar_alquileres():
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
        # cargar usuarios
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

@app.route('/alquileres/detalles/<string:id>', methods=['GET'])
@jwt_required()
def detalles_alquiler(id_alquiler):
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
def finalizar_alquiler(id_alquiler):
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

        # Extraer el ID del alquiler asociado al alquiler
        id_usuario_alquiler = alquiler.iloc[0]['id_usuario']

        # Verificar permisos
        if rol != 'admin' and email_usuario_autenticado != id_usuario_alquiler:
            return jsonify({'error': 'Acceso no autorizado'}), 403
    
    
        empresa.finalizar_alquiler(id_alquiler)
        return jsonify({'mensaje': f'Alquiler con id {id_alquiler} finalizado con exito'}), 200
    
    except FileNotFoundError:
        return jsonify({'error': 'Archivo de alquileres no encontrado'}), 500
    except Exception as e:
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500


@app.route('/alquileres/historial/<string:email>', methods=['GET'])
@jwt_required()
def historial_alquileres(email):
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
def registrar_coche():
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
def detalles_coche(matricula):
    try:
        # Cargar los alquileres
        df_coches = empresa.cargar_coches()
        if df_coches is None or df_coches.empty:
            return jsonify({'error': 'No se encontraron coches registrados'}), 404

        # Buscar el alquiler por ID
        coche = df_coches[df_coches['matricula'] == matricula]
        if coche.empty:
            return jsonify({'error': 'Coche no encontrado'}), 404

        # Convertir el alquiler a un diccionario
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
def actualizar_matricula(id_coche):
    claims = get_jwt()

    # Verificar si las claims son un diccionario
    if not isinstance(claims, dict):
        return jsonify({'error': 'Error al leer las claims del token'}), 500
    
    rol = claims.get('rol')
    
    # Comprobar que el usuario esta intentando cambiar sus propios datos
    if rol != 'admin':
        return jsonify({'error': 'Acceso no autorizado'}),403
    
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
def eliminar_coche(id_coche):
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
