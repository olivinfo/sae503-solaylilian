import os
import csv
from flask import Flask, request, jsonify
from redis import Redis
from flasgger import Swagger
from functools import wraps

# Configuration des variables d'environnement
REDIS_HOST = "redis"
REDIS_PORT =  6379
REDIS_DB = 0
APP_PORT = 5000
ADMIN_KEY = "default_key"
# Initialisation de Flask et Swagger
app = Flask(__name__)
swagger = Swagger(app)

# Connexion à Redis
redis_client = Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_key = request.headers.get("Authorization")
        if not auth_key or auth_key != ADMIN_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated


# Endpoint: Service des utilisateurs
@app.route('/users', methods=['GET'])
@require_auth
def get_users():
    """
    Récupérer la liste des utilisateurs
    ---
    security:
      - APIKeyAuth: []
    responses:
      200:
        description: Liste des utilisateurs
    """
    users_ids = redis_client.smembers("users")
    users=[]
    for user_id in users_ids:
        users.append(redis_client.hgetall(user_id))
    print(users)
    return jsonify(users), 200

@app.route('/users', methods=['POST'])
@require_auth
def add_user():
    """
    Ajouter un utilisateur
    ---
    security:
      - APIKeyAuth: []
    parameters:
      - name: user
        in: body
        required: true
        schema:
          type: object
          properties:
            id:
              type: string
            name:
              type: string
            password:
              type: string
    responses:
      201:
        description: Utilisateur ajouté
    """
    data = request.get_json()
    user_id = data.get("id")
    name = data.get("name")
    password = data.get("password")

    if not user_id or not name:
        return jsonify({"error": "ID et nom sont requis"}), 400

    redis_client.hset(f"users:{user_id}", mapping={"id": user_id,"name": name, "password": password})
    redis_client.sadd("users",f"users:{user_id}")
    return jsonify({"message": "Utilisateur ajouté"}), 201


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=APP_PORT)
