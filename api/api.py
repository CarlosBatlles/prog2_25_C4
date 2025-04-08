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


@app.route('/invitado', methods=['GET'])
@jwt_required()
def invitado_route():
    identity = get_jwt_identity()
    user = identity.get('user', '')
    tipo = identity.get('tipo', 'invitado')
    return jsonify(msg=f"Hola {user}, estás en la zona pública para el tipo {tipo}")

if __name__ == '__main__':
    app.run(debug=True)
