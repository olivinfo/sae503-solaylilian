# LOT 1 : Dossier d'Architecture Technique (DAT)

## 1. Introduction

### 1.1 Objet du document
Ce document d'architecture technique définit et documente l'architecture nécessaire pour le déploiement de l'application de gestion des citations du capitaine Haddock dans un environnement conteneurisé et orchestré.

### 1.2 Périmètre
- Définition de l'architecture applicative
- Définition de l'architecture technique
- Choix technologiques
- Architecture réseau
- Gestion de la persistance
- Sécurité

### 1.3 Références
- Cahier des charges SAE 5.03
- [12-Factor App](https://12factor.net/fr/)
- Documentation Kubernetes
- Documentation Traefik

## 2. Vue d'ensemble de l'architecture

#### Architecture microservices
L'application monolithique sera refactorisée en 3 microservices :
- **Service Users** : Gestion des utilisateurs
- **Service Quotes** : Gestion des citations
- **Service Search** : Recherche de citations

#### Conteneurisation
- Un conteneur par microservice
- Images Docker minimales ou distroless
- Respect des bonnes pratiques de sécurité

#### Orchestration
- Kubernetes comme orchestrateur
- Namespaces pour la séparation logique
- Scaling horizontal possible

## 3. Architecture applicative

### 3.1 Décomposition en microservices

#### 3.1.1 Service Users
**Responsabilités** :
- Gestion du CRUD des utilisateurs
- Authentification

**Endpoints** :
- `GET /users` : Liste des utilisateurs
- `POST /users` : Ajout d'un utilisateur

**Dépendances** :
- Redis (base de données)

#### 3.1.2 Service Quotes
**Responsabilités** :
- Gestion du CRUD des citations

**Endpoints** :
- `GET /quotes` : Liste des citations
- `POST /quotes` : Ajout d'une citation
- `DELETE /quotes/<id>` : Suppression d'une citation

**Dépendances** :
- Redis (base de données)

#### 3.1.3 Service Search
**Responsabilités** :
- Recherche de citations par mot-clé

**Endpoints** :
- `GET /search?keyword=...` : Recherche de citations

**Dépendances** :
- Redis (base de données)

### 3.2 Diagramme de flux

```
Utilisateur → Traefik → Service approprié → Redis
```

### 3.3 Base de données

**Technologie** : Redis

**Justification** :
- Base NoSQL clé-valeur performante
- Adapté aux données simples et lectures fréquentes
- Support natif des structures de données (hashes, sets)

**Structure des données** :
- `users:{id}` : Hash contenant les informations utilisateur
- `users` : Set contenant les clés des utilisateurs
- `quotes:{id}` : Hash contenant les citations
- `quotes` : Set contenant les clés des citations
- `quote_id` : Compteur pour les IDs de citations

## 4. Architecture technique

### 4.1 Infrastructure

#### 4.1.1 Environnements

**Environnement de qualification** :
- Namespace : `qualification`
- Objectif : Tests et validation avant production
- Ressources limitées pour ne pas impacter la production

**Environnement de production** :
- Namespace : `production`
- Objectif : Services en production
- Priorité sur les ressources

#### 4.1.2 Déploiement

- **Plateforme** : Kubernetes sur VM unique ( 1 par environnement )
- **Distribution K8s** : minikube
- **OS** : Debian 13

### 4.2 Orchestration Kubernetes

#### 4.2.1 Ressources Kubernetes

Pour chaque microservice :
- **Deployment** : Gestion des pods et réplicas
- **Service** : Exposition interne
- **ConfigMap** : Configuration non sensible
- **Secret** : Données sensibles (ADMIN_KEY, credentials Redis)

Pour Redis :
- **StatefulSet** : Gestion de la base de données
- **PersistentVolumeClaim** : Stockage persistant
- **Service** : Exposition interne

#### 4.2.2 Gestion des ressources

**Limites de ressources** :
```yaml
resources:
  requests:
    memory: "64Mi"
    cpu: "100m"
  limits:
    memory: "128Mi"
    cpu: "200m"
```

**ResourceQuota** par namespace :
- Production : priorité haute, ressources garanties
- Qualification : ressources limitées

#### 4.2.3 Scaling

**HorizontalPodAutoscaler** :
- Scaling basé sur CPU/mémoire
- Min replicas : 2
- Max replicas : 5

### 4.3 Réseau et exposition

#### 4.3.1 Ingress Controller : Traefik

**Choix de Traefik** :
- Reverse proxy moderne pour Kubernetes
- Support natif des annotations Kubernetes
- Dashboard intégré
- Rate limiting intégré
- TLS/HTTPS (avec let's encrypt)

#### 4.3.2 Nommage (FQDN)

Utilisation de **nip.io** pour les DNS wildcard :
- Production : `production.<IP>.nip.io`
- Qualification : `qualification.<IP>.nip.io`

Exemple avec IP 192.168.1.100 :
- `production.192.168.1.100.nip.io`
- `qualification.192.168.1.100.nip.io`

#### 4.3.3 Matrice de flux

| Source | Destination | Port | Protocole | Description |
|--------|-------------|------|-----------|-------------|
| Internet | Traefik | 80/443 | HTTP/HTTPS | Accès utilisateurs |
| Traefik | Services | 5000 | HTTP | Routage vers microservices |
| Services | Redis | 6379 | TCP | Accès base de données |

### 4.4 Stockage

#### 4.4.1 Persistance des données

**PersistentVolume** pour Redis :
- Type : `hostPath` (mono-nœud) ou `local`
- Taille : 1Gi minimum
- AccessMode : `ReadWriteOnce`

**Note pour multi-nœud** :
En environnement multi-nœuds, il faudrait utiliser :
- NFS, Ceph, ou solution de stockage partagé
- StorageClass dynamique
- AccessMode : `ReadWriteMany` si nécessaire

#### 4.4.2 Backup

[À définir : stratégie de sauvegarde Redis]

## 5. Choix techniques et justifications

### 5.1 Kubernetes
**Justification** :
- Standard de facto pour l'orchestration
- Gestion automatique du scaling
- Self-healing
- Portabilité multi-cloud

### 5.2 Traefik
**Justification** :
- Intégration native Kubernetes
- Configuration par annotations
- Rate limiting intégré
- Dashboard pour monitoring

### 5.3 Redis
**Justification** :
- Base de données déjà utilisée dans l'application
- Performance élevée
- Simple à déployer
- Adapté aux données non relationnelles

### 5.4 Flask
**Justification** :
- Framework Python léger
- Facilement découpable en microservices
- Swagger intégré (Flasgger)
- Déjà utilisé dans l'application existante

### 5.5 Docker images minimales
**Justification** :
- Surface d'attaque réduite
- Taille d'image réduite
- Meilleure sécurité
- Conformité aux bonnes pratiques

## 6. Contraintes et limitations

### 6.1 Mono-nœud

**Limitations** :
- Pas de haute disponibilité native
- Point de défaillance unique
- Stockage limité au nœud local

**Implications** :
- StatefulSet Redis limité à 1 replica
- PersistentVolume en `hostPath`
- Pas de distribution de charge physique

### 6.2 Évolution vers multi-nœuds

**Changements nécessaires** :
- Stockage partagé (NFS, Ceph, Cloud Storage)
- Redis en mode cluster ou avec sentinel
- Anti-affinity rules pour distribution des pods
- LoadBalancer externe

## 7. Conformité 12-Factor

| Factor | Mise en œuvre |
|--------|---------------|
| 1. Codebase | Git unique, multiples déploiements |
| 2. Dependencies | Requirements.txt, images Docker |
| 3. Config | Variables d'environnement, ConfigMap, Secrets |
| 4. Backing services | Redis comme service attaché |
| 5. Build, release, run | CI/CD séparé (à implémenter) |
| 6. Processes | Stateless, état dans Redis |
| 7. Port binding | Services exposés sur ports |
| 8. Concurrency | Scaling horizontal Kubernetes |
| 9. Disposability | Démarrage rapide, arrêt graceful |
| 10. Dev/prod parity | Mêmes conteneurs partout |
| 11. Logs | stdout/stderr, collecte K8s |
| 12. Admin processes | Jobs Kubernetes |

