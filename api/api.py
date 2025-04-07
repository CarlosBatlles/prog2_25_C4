import sys
import os
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

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
    tipo = data.get('tipo','ciiente') # Por defecto aplicamos cliente
    email = data.get('email')
    contraseña = data.get('contraseña')
    
    if not nombre or not email or not contraseña:
        return jsonify({'error': 'Todos los campos son obligatorios'}), 400
    
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
def obtener_coches_disponibles():
    try:
        # Obtener los parámetros de la solicitud
        categoria_precio = request.args.get('categoria_precio')
        categoria_tipo = request.args.get('categoria_tipo')
        marca = request.args.get('marca')
        modelo = request.args.get('modelo')

        # Llamar al método buscar_coches_disponibles1 de la clase Empresa
        coches = empresa.buscar_coches_disponibles1(
            categoria_precio=categoria_precio,
            categoria_tipo=categoria_tipo,
            marca=marca,
            modelo=modelo
        )

        if not coches:
            return jsonify({'mensaje': 'No se encontraron coches disponibles que coincidan con los criterios'}), 200

        return jsonify(coches), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
'''
@app.route('/admin', methods=['GET'])
@jwt_required()
def admin_route():
    identity = get_jwt_identity()
    tipo = identity.get('tipo', 'invitado')

    if tipo != 'administrador':
        return jsonify(msg="Acceso denegado: necesitas ser administrador"), 403
    else:
        return jsonify(msg="Bienvenido al panel de administración")


@app.route('/cliente', methods=['GET'])
@jwt_required()
def cliente_route():
    identity = get_jwt_identity()
    tipo = identity.get('tipo', 'invitado')

    if tipo not in ['cliente', 'administrador']:
        return jsonify(msg="Acceso denegado: necesitas ser cliente"), 403

    return jsonify(msg="Bienvenido a la zona de clientes")


@app.route('/invitado', methods=['GET'])
@jwt_required()
def invitado_route():
    identity = get_jwt_identity()
    user = identity.get('user', '')
    tipo = identity.get('tipo', 'invitado')
    return jsonify(msg=f"Hola {user}, estás en la zona pública para el tipo {tipo}")'''

if __name__ == '__main__':
    app.run(debug=True)
