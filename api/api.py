import sys
import os
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt

# Agrega el directorio raíz del proyecto al PATH (para que encuentre `source`)
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

# Ahora la importación debería funcionar
from source.empresa import Empresa

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "grupo_4!"
jwt = JWTManager(app)

empresa = Empresa(nombre='RentAcar')

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
        return jsonify({'error': 'Debes introducir la matricula, la fecha de inicio y la fecha de fin'}), 400
    
    try:
        # Obtener claims del token si existe
        claims = get_jwt() if get_jwt() else {}
        rol = claims.get('rol')
        
        if rol and not email:
            email = get_jwt_identity()
        
        empresa.alquilar_coche(matricula=matricula,fecha_inicio=fecha_inicio,fecha_fin=fecha_fin, email=email)
        
        return jsonify({'mensaje': 'Alquiler registrado exitosamente'}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error':f'Error interno del servidor: {str(e)}'}), 500


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
    

if __name__ == '__main__':
    app.run(debug=True)
