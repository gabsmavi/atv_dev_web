from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
from bson import ObjectId
from flask import render_template

# Carregar variáveis do arquivo .env
load_dotenv()

# Criar a instância do app Flask
app = Flask(__name__)

# Habilitar CORS
CORS(app)

# Conectar ao MongoDB
MONGO_URI = os.getenv('MONGO_URI')

# Criar o cliente do MongoDB com a URI
client = MongoClient(MONGO_URI)

# Acessar o banco de dados 'NavegaWEB'
db = client['NavegaWEB']

# Acessar a coleção de usuários
users_collection = db["usuarios"]

# Endpoint para exibir a página inicial
@app.route('/')
def index():
    return render_template('index.html')

# Endpoint para exibir a página de login
@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

# Endpoint para exibir a página do admin
@app.route('/admin', methods=['GET'])
def admin_page():
    return render_template('admin.html')

# Endpoint para exibir a página de registro
@app.route('/register', methods=['GET'])
def register_page():
    return render_template('registro.html')

# Endpoint para registrar um novo usuário
@app.route('/registro', methods=['POST'])
def register_user():
    try:
        import json
        
        # Logar todas as informações da requisição
        print("Método da Requisição:", request.method)
        print("Cabeçalhos da Requisição:", dict(request.headers))
        print("Dados da Requisição (raw):", request.data)
        
        # Tentar múltiplas formas de interpretar os dados da requisição
        try:
            # Tentar interpretar como JSON com force=True
            data = request.get_json(force=True)
            print("JSON Interpretado (force=True):", data)
        except Exception as json_error:
            print(f"Erro ao interpretar JSON (force=True): {json_error}")
            try:
                # Tentar interpretar os dados brutos manualmente
                data = json.loads(request.data.decode('utf-8'))
                print("JSON Interpretado (manual):", data)
            except Exception as manual_error:
                print(f"Erro ao interpretar JSON manualmente: {manual_error}")
                return jsonify({"mensagem": "Erro ao processar dados JSON"}), 400

        # Verificar se todos os campos obrigatórios estão presentes
        required_fields = ["name", "email", "senha"]
        for field in required_fields:
            if field not in data:
                print(f"Campo ausente: {field}")
                return jsonify({"mensagem": f"Campo obrigatório ausente: {field}"}), 400

        email = data["email"].strip().lower()

        # Verificar conexão com o banco de dados e usuários existentes
        try:
            # Verificar conexão com o MongoDB
            client.admin.command('ismaster')
            print("Conexão com MongoDB bem-sucedida")
        except Exception as db_error:
            print(f"Erro de Conexão com o MongoDB: {db_error}")
            return jsonify({"mensagem": "Erro de conexão com o banco de dados"}), 500

        # Verificar se o e-mail já existe
        existing_user = users_collection.find_one({"email": email})
        if existing_user:
            print(f"Usuário já existente: {existing_user}")
            return jsonify({"mensagem": "Este e-mail já está registrado."}), 400

        # Hash da senha
        hashed_password = generate_password_hash(data["senha"], method="sha256")

        # Criar novo usuário
        new_user = {
            "email": email,
            "name": data["name"],
            "senha": hashed_password
        }

        # Inserir usuário no banco de dados
        result = users_collection.insert_one(new_user)
        print(f"Usuário inserido com ID: {result.inserted_id}")
        
        return jsonify({
            "mensagem": "Usuário registrado com sucesso!", 
            "user_id": str(result.inserted_id)
        }), 201

    except Exception as e:
        # Logar o erro completo
        print(f"Erro Completo no Registro: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "mensagem": "Erro ao registrar o usuário", 
            "erro": str(e)
        }), 500

# Endpoint para login de usuários
@app.route('/login', methods=['POST'])
def login_user():
    try:
        data = request.get_json()
        print(f"Dados da Requisição: {data}")  # Verificar se os dados estão sendo mostrados corretamente

        if not data or not data.get("email") or not data.get("senha"):
            print("Campos de e-mail ou senha ausentes")
            return jsonify({"message": "Credenciais inválidas"}), 400

        user = users_collection.find_one({"email": data["email"]})
        print(f"Usuário: {user}")  # Verificar se o usuário está sendo encontrado na coleção

        if not user:
            print("E-mail não encontrado")
            return jsonify({"message": "E-mail não encontrado"}), 404

        if not check_password_hash(user["senha"], data["senha"]):
            print("Senha incorreta")
            return jsonify({"message": "Senha incorreta"}), 401

        print("Login bem-sucedido")
        return jsonify({"message": "Login realizado com sucesso!"}), 200

    except Exception as e:
        print(f"Erro no servidor: {str(e)}")
        return jsonify({"message": "Erro no servidor", "error": str(e)}), 500

# Endpoint para listar usuários
@app.route('/users', methods=['GET'])
def get_users():
    users = list(users_collection.find({}, {"senha": 0}))  # Excluindo a senha da resposta
    return jsonify(users), 200

@app.route('/recent-data')
def recent_data():
    return render_template('recent_data.html')  # ou qualquer outra lógica

@app.route('/edit')
def edit():
    return render_template('edit.html')  # ou qualquer outra lógica

# Endpoint para editar um usuário
@app.route('/users/edit/<id>', methods=['GET'])
def edit_user(id):
    # Verificar se o ID é válido
    if not ObjectId.is_valid(id):
        return "ID inválido", 400
    
    # Buscar o usuário pelo ID
    user = users_collection.find_one({"_id": ObjectId(id)})
    
    if user:
        # Se o usuário for encontrado, renderize o template de edição
        return render_template('edit.html', user=user)
    else:
        # Se o usuário não for encontrado, retornar erro
        return "Usuário não encontrado", 404

# Endpoint para excluir um usuário
@app.route('/users/<id>', methods=['DELETE'])
def delete_user(id):
    result = users_collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count > 0:
        return jsonify({"message": "Usuário excluído com sucesso!"}), 204
    else:
        return jsonify({"message": "Usuário não encontrado!"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
