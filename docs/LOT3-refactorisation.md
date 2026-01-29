# LOT 3 : Refactorisation de l'application

## 1. Introduction

### 1.1 Objectif
Refactoriser l'application monolithique en 3 microservices distincts selon les responsabilités fonctionnelles :
1. Service **Users** : Gestion des utilisateurs
2. Service **Quotes** : Gestion des citations
3. Service **Search** : Recherche de citations

### 1.2 Respect des 12-Factor App
La refactorisation respecte les principes des [12-Factor App](https://12factor.net/fr/).

## 2. Architecture de l'application refactorisée


### 2.2 Répartition des endpoints

| Microservice | Endpoints | Méthodes |
|--------------|-----------|----------|
| **Users** | `/users` | GET, POST |
| **Quotes** | `/quotes` | GET, POST |
|           | `/quotes/<id>` | DELETE |
| **Search** | `/search` | GET |

## 3. Service Users

### 3.1 Responsabilités
- Gestion des utilisateurs (CRUD)
- Authentification (bonus)
- Initialisation depuis CSV

### 3.2 Structure du code

**Fichier** : `microservices/users/app.py`

Points clés :
- Endpoints : `GET /users`, `POST /users`
- Connexion à Redis via variables d'environnement
- Authentification via `ADMIN_KEY`
- Health check : `GET /health`
- Documentation Swagger : `/apidocs`

## 4. Service Quotes

### 4.1 Responsabilités
- Gestion des citations (CRUD)
- Initialisation depuis CSV
- Suppression par ID

### 4.2 Structure du code

**Fichier** : `microservices/quotes/app.py`

Points clés :
- Endpoints : `GET /quotes`, `POST /quotes`, `DELETE /quotes/<id>`
- Connexion à Redis via variables d'environnement
- Authentification via `ADMIN_KEY` pour POST/DELETE
- Health check : `GET /health`
- Documentation Swagger : `/apidocs`

## 5. Service Search

### 5.1 Responsabilités
- Recherche de citations par mot-clé
- Lecture seule dans Redis

### 5.2 Structure du code

**Fichier** : `microservices/search/app.py`

Points clés :
- Endpoint : `GET /search?keyword=<mot-clé>`
- Connexion à Redis via variables d'environnement
- Authentification via `ADMIN_KEY`
- Recherche insensible à la casse
- Health check : `GET /health`
- Documentation Swagger : `/apidocs`


## 6. Bonnes pratiques appliquées

### 6.1 Principes 12-Factor

| Factor | Application |
|--------|-------------|
| **I. Codebase** | Un dépôt Git, plusieurs déploiements |
| **II. Dependencies** | `requirements.txt` explicite |
| **III. Config** | Variables d'environnement (pas de valeurs en dur) |
| **IV. Backing services** | Redis comme ressource attachée |
| **V. Build, release, run** | Séparation stricte (Docker build, K8s deploy) |
| **VI. Processes** | Services stateless, état dans Redis |
| **VII. Port binding** | Exposition sur port 5000 |
| **VIII. Concurrency** | Scaling horizontal via Kubernetes |
| **IX. Disposability** | Démarrage rapide, shutdown graceful |
| **X. Dev/prod parity** | Même conteneur partout |
| **XI. Logs** | Logs vers stdout/stderr |
| **XII. Admin processes** | Scripts séparés si nécessaire |

### 6.2 Sécurité

- **Pas de secrets dans le code** : Variables d'environnement uniquement
- **Utilisateur non-root** : USER dans Dockerfile
- **Images minimales** : slim ou alpine
- **Dépendances à jour** : Versions spécifiques dans requirements.txt
- **SecurityContext Kubernetes** : runAsNonRoot, readOnlyRootFilesystem

### 6.3 Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Utilisation
logger.info("Service démarré")
logger.error("Erreur lors de la connexion à Redis")
```

### 6.4 Health checks

Chaque service expose un endpoint `/health` :

```python
@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        redis_client.ping()
        return jsonify({"status": "healthy", "redis": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 503
```

## 7. Fichiers de données initiales

### 7.1 Format CSV

**initial_data_users.csv** :
```csv
id,name,password
1,admin,admin123
2,user1,password1
3,user2,password2
```

**initial_data_quotes.csv** :
```csv
quote
Bachi-bouzouk!
Tonnerre de Brest!
Mille millions de mille sabords!
Moule à gaufres!
Ectoplasme!
```

### 7.2 Chargement initial

Le chargement des données CSV se fait au démarrage du service si Redis est vide via le job init-redis :
