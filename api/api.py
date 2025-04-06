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
'''
@app.route('/login', methods=['GET'])
def login(): #
    user = request.args.get('user', '')
    password = request.args.get('password', '')
    hashed = hashlib.sha256(password.encode()).hexdigest()

    usuarios, tipos = cargar_usuarios()
    if user in usuarios and usuarios[user] == hashed:
        tipo = tipos.get(user,'invitado')
        identity = {'user': user, 'tipo': tipo}
        access_token= create_access_token(identity={'user': user, 'tipo': tipo})
        return access_token, 200
    else:
        return 'Usuario o contraseña incorrectos', 401


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
