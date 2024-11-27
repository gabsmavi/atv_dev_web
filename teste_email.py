from pymongo import MongoClient

# Conectar ao MongoDB (ajuste a URI de conexão conforme necessário)
client = MongoClient("mongodb+srv://gabsmavi:viana123321@cluster0.n0ofp.mongodb.net/")  # Coloque a URL entre aspas

# Selecionar o banco de dados
db = client["NavegaWEB"]  # Nome do banco de dados entre aspas

# Selecionar a coleção de usuários
users_collection = db["usuarios"]  # Nome da coleção entre aspas

# Certifique-se de que db.usuarios está correto e é uma coleção do MongoDB
usuarios_collection = db["usuarios"]  # Certifique-se de que a coleção foi corretamente atribuída

client.close()
client = MongoClient("MONGO_URI")
db = client['NavegaWEB']
users_collection = db["usuarios"]