# SAE 5.03 : Orchestrer la conteneurisation d'une application

## Contexte

Application web de gestion des citations du capitaine Haddock (personnage de la bande dessinée "Les Aventures de Tintin" d'Hergé).

## Objectifs

Déployer l'application dans un environnement "cloud native" basé sur l'orchestration de conteneurs pour apporter flexibilité et portabilité.

## Équipe

- **Membres** : Lilian GAUDIN & SOlaymane El-Kaldaoui
- **Date limite** : 02 février 2026 à 12h00
- **Tag Git** : sae503

## Structure du projet

```
.
├── docs/
│   ├── README.md                           # Ce fichier
│   ├── LOT1-architecture-technique.md      # Dossier d'Architecture Technique (DAT)
│   ├── LOT2-installation-technique.md      # Cahier d'Installation Technique (CIT)
│   ├── LOT3-refactorisation.md             # Documentation de refactorisation
│   ├── LOT4-deploiement.md                 # Documentation de déploiement
│   └── SECURITY.md                         # Exigences de sécurité (LOT5)
├── microservices/
│   ├── users/                              # Service de gestion des utilisateurs
│   ├── quotes/                             # Service de gestion des citations
│   └── search/                             # Service de recherche
├── k8s/                                    # Manifestes Kubernetes
│   ├── qualification/
│   └── production/
└── helm/                                   # Charts Helm (optionnel)
```

## Fonctionnalités de l'application

### Points d'accès API

- **/users** : Gestion des utilisateurs
  - GET : Affiche la liste des utilisateurs
  - POST : Ajoute un utilisateur

- **/quotes** : Gestion des citations
  - GET : Affiche toutes les citations
  - POST : Ajoute une citation
  - DELETE : Supprime une citation

- **/search** : Recherche de citations
  - GET : Recherche par mot-clé

- **/apidocs** : Interface Swagger

### Authentification

Certaines opérations nécessitent un jeton d'authentification dans l'en-tête "Authorization" (paramètre `ADMIN_KEY`).

## Lots de travail

### Lot 1 : Définition de l'architecture
**Livrable** : [Dossier d'Architecture Technique](LOT1-architecture-technique.md)

### Lot 2 : Mise en place de l'orchestrateur
**Livrable** : [Cahier d'Installation Technique](LOT2-installation-technique.md)

### Lot 3 : Refactorisation de l'application
**Livrable** : Code des 3 microservices + Dockerfiles

### Lot 4 : Instanciation dans l'orchestrateur
**Livrable** : Manifestes de déploiement Kubernetes/Helm

### Lot 5 : Sécurité
**Livrable** : [Fichier SECURITY.md](../SECURITY.md)

## Technologies utilisées

- **Orchestrateur** : Kubernetes
- **Reverse Proxy** : Traefik
- **Base de données** : Redis
- **Framework** : Flask (Python)
- **Documentation API** : Swagger/Flasgger
- **Sécurité** : Trivy

## Exigences techniques

### Multiples plateformes
- 2 environnements : qualification et production
- Cloisonnement des ressources
- Un conteneur par microservice
- Reverse proxy pour l'acheminement des requêtes

### Stockage
- Persistance des données Redis assurée

### Accès
- Gestion des accès HTTP via Traefik
- Limitation : 10 requêtes par minute
- FQDN via nip.io

### Infrastructure
- Infrastructure mono-noeud 
- Un cluster par environnement

## Accès aux services
```cmd
minikube mount /home/user/sae503-solaylilian/BDD_microservice/../BDD_microservice:/data/bdd -p dev-env
kubectl port-forward svc/citation-service 30002:5000 -n sae503 --address 0.0.0.0
curl -v -H "Authorization: default_key" http://172.18.253.219:30002/quotes
```
