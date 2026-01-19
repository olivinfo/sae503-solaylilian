# LOT 2 : Cahier d'Installation Technique (CIT)

## 1. Introduction

### 1.1 Objet du document
Ce document détaille l'installation et la configuration de l'orchestrateur de conteneurs Kubernetes pour le déploiement de l'application de citations du capitaine Haddock.

### 1.2 Architecture retenue
L'architecture comprend **2 machines virtuelles distinctes** :
- **VM Production** : Environnement de production
- **VM Qualification** : Environnement de développement/qualification

Chaque VM exécute sa propre instance Minikube, assurant une isolation complète entre les environnements.

## 2. Architecture matérielle

### 2.1 Schéma d'infrastructure


### 2.2 Spécifications

#### VM Production

| Composant | Spécification |
|-----------|--------------|
| **Rôle** | Environnement de production |
| **CPU** |2 vCPU |
| **RAM** | 6 Go |
| **Disque** | ~40 Go |
| **OS** | Debian 13 |
| **IP** | XXXXXXXXXXXX |

#### VM Qualification

| Composant | Spécification |
|-----------|--------------|
| **Rôle** | Environnement de qualification/développement |
| **CPU** | 2 vCPU  |
| **RAM** | 6 Go |
| **Disque** | ~40 Go |
| **OS** | Debian 13 |
| **IP** | XXXXXXXXXXXXXXx |

## 3. Installation de Kubernetes

### 3.1 Choix de la distribution

**Distribution sélectionnée** : Minikube

**Justification** :
- Adapté aux environnements VM individuelles
- Installation simplifiée et bien documentée
- Support natif des addons (Ingress, metrics-server, etc.)
- Idéal pour développement, tests et démonstrations
- Isolation parfaite entre environnements (1 Minikube par VM)
- Fonctionne sur une seule machine avec Docker ou autre driver
- Large communauté et documentation

**Alternatives considérées** :
- K3s : Production-ready mais plus complexe pour tests
- MicroK8s : Plus lourd, orienté Ubuntu
- Kind : Orienté tests CI/CD

### 3.2 Architecture retenue : 2 VMs indépendantes

Cette architecture offre :
- **Isolation complète** : Chaque environnement a ses propres ressources
- **Sécurité renforcée** : Pas de risque de conflit entre production et qualification
- **Flexibilité** : Possibilité de dimensionner différemment chaque environnement
- **Réalisme** : Se rapproche d'une architecture de production réelle

**Note importante** : Les étapes d'installation ci-dessous doivent être **répétées sur chaque VM** (production et qualification).

### 3.3 Installation de Minikube

**IMPORTANT** : Ces étapes sont à réaliser sur **chaque VM** (production et qualification).

#### 3.3.1 Installation de Docker (prérequis)

```bash
# Mise à jour du système
sudo apt update && sudo apt upgrade -y

# Installation de Docker
sudo apt install -y docker.io

# Ajouter l'utilisateur au groupe docker
sudo usermod -aG docker $USER
newgrp docker

# Vérifier Docker
docker --version
docker ps
```

#### 3.3.2 Installation de kubectl

```bash
# Télécharger kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

# Rendre exécutable
chmod +x kubectl

# Déplacer dans le PATH
sudo mv kubectl /usr/local/bin/

# Vérifier
kubectl version --client
```

#### 3.3.3 Installation de Minikube

```bash
# Télécharger Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64

# Installer
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Vérifier
minikube version
```

#### 3.3.4 Démarrage du cluster Minikube

**Sur la VM Production** :
```bash
# Démarrer Minikube avec Docker driver (ressources production)
minikube start --driver=docker --cpus=4 --memory=6144 --disk-size=20g

# Vérifier le statut
minikube status

# Vérifier les nœuds
kubectl get nodes

# Configuration automatique de kubectl
# Minikube configure automatiquement ~/.kube/config
kubectl cluster-info
```

**Sur la VM Qualification** :
```bash
# Démarrer Minikube avec ressources réduites (qualification)
minikube start --driver=docker --cpus=2 --memory=4096 --disk-size=15g

# Vérifier le statut
minikube status

# Vérifier les nœuds
kubectl get nodes

# Configuration automatique de kubectl
kubectl cluster-info
```

#### 3.3.5 Activation des addons nécessaires

**Sur les deux VMs** (production et qualification) :

```bash
# Activer l'Ingress Controller (NGINX par défaut)
minikube addons enable ingress

# Activer le metrics-server pour HPA
minikube addons enable metrics-server

# Voir tous les addons disponibles
minikube addons list

# Vérifier l'installation
kubectl get pods -n ingress-nginx
kubectl get pods -n kube-system | grep metrics-server
```

### 3.4 Installation des outils complémentaires

**Sur les deux VMs** :

```bash
# Installation de Helm
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-4 
chmod +x get_helm.sh
./get_helm.sh
# Vérification
helm version

# Installation de Trivy
wget https://github.com/aquasecurity/trivy/releases/download/v0.48.0/trivy_0.48.0_Linux-64bit.deb
sudo dpkg -i trivy_0.48.0_Linux-64bit.deb

# Vérification
trivy --version

```

## 4. Configuration du réseau

[À compléter]

## 5. Configuration de Kubernetes

[À compléter]

## 6. Installation et configuration de Traefik

[À compléter]

## 7. Configuration des Secrets

[À compléter]

## 8. Schéma de principe

[À compléter]

## 9. Procédure de vérification

[À compléter]

## 10. Maintenance et exploitation

[À compléter]

## 11. Avantages et limitations de l'architecture 2 VMs

[À compléter]

## 12. Sécurité de l'infrastructure

[À compléter]

## Annexes

[À compléter]
