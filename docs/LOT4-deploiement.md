# LOT 4 : Instanciation de l'application dans l'orchestrateur

## 1. Introduction

### 1.1 Objectif
Déployer l'application Haddock (gestion des citations du Capitaine Haddock) dans Kubernetes en utilisant :
- Des manifests Kubernetes simples
- Un chart Helm pour un déploiement flexible

### 1.2 Prérequis
- Cluster Kubernetes opérationnel (voir LOT2)
- Images Docker disponibles sur Docker Hub (`solaymane/sae503-*`)
- Helm installé (pour le déploiement via Helm)

## 2. Structure du repository

```
sae503-solaylilian/
├── manifest/                    # Manifests Kubernetes
│   ├── redis.yml               # PV, PVC, Deployment et Service Redis
│   ├── citation-service.yml    # Deployment et Service Citation
│   ├── user-service.yml        # Deployment et Service User
│   ├── recherche-service.yml   # Deployment et Service Recherche
│   ├── init_redis.yml          # Job d'initialisation des données
│   └── traefik.yml             # Ingress Controller Traefik
├── helm/
│   └── haddock/                # Chart Helm
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
├── citation_microservice/      # Code source + Dockerfile
├── user_microservice/          # Code source + Dockerfile
├── recherche_microservice/     # Code source + Dockerfile
├── init_redis_job/             # Job d'init + Dockerfile
└── BDD_microservice/           # Données CSV initiales
    ├── initial_data_quotes.csv
    └── initial_data_users.csv
```

## 3. Méthode 1 : Déploiement avec Kubectl (Manifests)

### 3.1 Manifest Redis

**Fichier** : `manifest/redis.yml`

Ce manifest crée :
- Un PersistentVolume (1Gi) avec hostPath
- Un PersistentVolumeClaim
- Un Deployment Redis
- Un Service ClusterIP

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
    name: my-pv
spec:
  capacity:
    storage: 1Gi
  accessModes:
  - ReadWriteOnce
  hostPath:
    path: /home/user/sae503-solaylilian/BDD_microservice/data
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: db-data
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:alpine
        ports:
        - containerPort: 6379
        volumeMounts:
        - name: db-data
          mountPath: /data
      volumes:
      - name: db-data
        persistentVolumeClaim:
          claimName: db-data
---
apiVersion: v1
kind: Service
metadata:
  name: redis
spec:
  ports:
  - port: 6379
    targetPort: 6379
  selector:
    app: redis
```

### 3.2 Manifest Service Citation

**Fichier** : `manifest/citation-service.yml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: citation-service
spec:
  replicas: 1
  selector:
    matchLabels:
      app: citation-service
  template:
    metadata:
      labels:
        app: citation-service
    spec:
      containers:
      - name: citation-service
        image: solaymane/sae503-citation:1.0.0
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 5000
---
apiVersion: v1
kind: Service
metadata:
  name: citation-service
spec:
  type: LoadBalancer
  ports:
  - port: 5000
    targetPort: 5000
    nodePort: 30002
  selector:
    app: citation-service
```

### 3.3 Manifest Service User

**Fichier** : `manifest/user-service.yml`

Structure identique au service Citation avec :
- Image : `solaymane/sae503-user:1.0.0`
- NodePort : `30001`

### 3.4 Manifest Service Recherche

**Fichier** : `manifest/recherche-service.yml`

Structure identique au service Citation avec :
- Image : `solaymane/sae503-recherche:1.0.0`
- NodePort : `30003`

### 3.5 Job d'initialisation Redis

**Fichier** : `manifest/init_redis.yml`

Ce Job charge les données CSV initiales dans Redis :

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: init-redis
  namespace: sae503
spec:
  template:
    spec:
      containers:
      - name: init-redis
        image: solaymane/sae503-init-redis:1.0.0
        volumeMounts:
        - name: csv-data
          mountPath: /BDD_microservice
          readOnly: true
      volumes:
      - name: csv-data
        hostPath:
          path: /data/bdd
          type: Directory
      restartPolicy: OnFailure
```

### 3.6 Commandes de déploiement

```bash
# Créer le namespace (si nécessaire)
kubectl create namespace sae503

# Déployer Redis en premier
kubectl apply -f manifest/redis.yml

# Attendre que Redis soit prêt
kubectl wait --for=condition=ready pod -l app=redis --timeout=60s

# Déployer les microservices
kubectl apply -f manifest/citation-service.yml
kubectl apply -f manifest/user-service.yml
kubectl apply -f manifest/recherche-service.yml

# Initialiser les données
kubectl apply -f manifest/init_redis.yml

# Déployer Traefik (optionnel)
kubectl apply -f manifest/traefik.yml

# Vérifier le déploiement
kubectl get pods
kubectl get svc
```

## 4. Méthode 2 : Déploiement avec Helm

### 4.1 Pourquoi Helm ?

| Avantage | Description |
|----------|-------------|
| **Templating** | Les valeurs sont centralisées dans `values.yaml` |
| **Versioning** | Chaque déploiement est versionné, facilitant les rollbacks |
| **Reproductibilité** | Un seul fichier de valeurs définit tout l'environnement |
| **Simplicité** | Une commande pour déployer toute l'application |

### 4.2 Structure du chart Helm

```
helm/haddock/
├── Chart.yaml              # Métadonnées du chart
├── values.yaml             # Valeurs par défaut
└── templates/
    ├── _helpers.tpl        # Fonctions de templating
    ├── redis-pv.yaml
    ├── redis-deployment.yaml
    ├── redis-service.yaml
    ├── citation-deployment.yaml
    ├── citation-service.yaml
    ├── user-deployment.yaml
    ├── user-service.yaml
    ├── recherche-deployment.yaml
    ├── recherche-service.yaml
    └── init-redis-job.yaml
```

### 4.3 Chart.yaml

```yaml
apiVersion: v2
name: haddock
description: Application de gestion des citations du Capitaine Haddock
type: application
version: 1.0.0
appVersion: "1.0.0"
maintainers:
  - name: Lilian GAUDIN
  - name: Solaymane El-Kaldaoui
```

### 4.4 values.yaml

```yaml
# Configuration globale
global:
  imagePullPolicy: IfNotPresent

# Redis
redis:
  image: redis:alpine
  port: 6379
  storage:
    size: 1Gi
    hostPath: /home/user/sae503-solaylilian/BDD_microservice/data

# Service Citation
citation:
  enabled: true
  replicaCount: 1
  image:
    name: solaymane/sae503-citation
    tag: "1.0.0"
  service:
    type: LoadBalancer
    port: 5000
    nodePort: 30002

# Service User
user:
  enabled: true
  replicaCount: 1
  image:
    name: solaymane/sae503-user
    tag: "1.0.0"
  service:
    type: LoadBalancer
    port: 5000
    nodePort: 30001

# Service Recherche
recherche:
  enabled: true
  replicaCount: 1
  image:
    name: solaymane/sae503-recherche
    tag: "1.0.0"
  service:
    type: LoadBalancer
    port: 5000
    nodePort: 30003

# Job d'initialisation Redis
initRedis:
  enabled: true
  image:
    name: solaymane/sae503-init-redis
    tag: "1.0.0"
  dataPath: /data/bdd
```

### 4.5 Commandes Helm

```bash
# Vérifier la syntaxe du chart (dry-run)
helm template haddock ./helm/haddock

# Installer l'application
helm install haddock ./helm/haddock

# Installer avec un namespace spécifique
helm install haddock ./helm/haddock --namespace sae503 --create-namespace

# Voir le statut
helm status haddock

# Lister les releases
helm list

# Mettre à jour après modification des values
helm upgrade haddock ./helm/haddock

# Désinstaller
helm uninstall haddock
```

### 4.6 Personnalisation des valeurs

```bash
# Changer le nombre de réplicas
helm install haddock ./helm/haddock --set citation.replicaCount=3

# Changer le tag de l'image
helm install haddock ./helm/haddock --set citation.image.tag="2.0.0"

# Désactiver un service
helm install haddock ./helm/haddock --set recherche.enabled=false

# Combiner plusieurs modifications
helm install haddock ./helm/haddock \
  --set citation.replicaCount=2 \
  --set user.replicaCount=2
```

### 4.7 Rollback avec Helm

```bash
# Voir l'historique
helm history haddock

# Revenir à une version précédente
helm rollback haddock 1
```

## 5. Services exposés

| Service | Port interne | Type | NodePort | Description |
|---------|--------------|------|----------|-------------|
| Redis | 6379 | ClusterIP | - | Base de données |
| Citation | 5000 | LoadBalancer | 30002 | Gestion des citations |
| User | 5000 | LoadBalancer | 30001 | Gestion des utilisateurs |
| Recherche | 5000 | LoadBalancer | 30003 | Recherche de citations |

## 6. Vérifications

### 6.1 État des déploiements

```bash
# Voir tous les pods
kubectl get pods

# Voir tous les services
kubectl get svc

# Voir les détails d'un pod
kubectl describe pod <nom-du-pod>
```

### 6.2 Logs

```bash
# Logs d'un service
kubectl logs -f deployment/citation-service

# Logs de Redis
kubectl logs -f deployment/redis
```

### 6.3 Tests des endpoints

```bash
# Test Service Citation (via NodePort)
curl http://<IP-NODE>:30002/citations

# Test Service User
curl http://<IP-NODE>:30001/users

# Test Service Recherche
curl http://<IP-NODE>:30003/search?q=tonnerre
```


## 7. Mise à jour de l'application

### 7.1 Avec Kubectl

```bash
# Mettre à jour l'image
kubectl set image deployment/citation-service citation-service=solaymane/sae503-citation:2.0.0

# Suivre le rollout
kubectl rollout status deployment/citation-service

# Rollback si nécessaire
kubectl rollout undo deployment/citation-service
```

### 7.2 Avec Helm

```bash
# Mettre à jour les values et upgrader
helm upgrade haddock ./helm/haddock --set citation.image.tag="2.0.0"

# Rollback
helm rollback haddock 1
```
