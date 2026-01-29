# LOT 4 : Instanciation de l'application dans l'orchestrateur

## 1. Introduction

### 1.1 Objectif
Déployer l'application refactorisée dans Kubernetes avec :
- 2 environnements (production et qualification)
- Gestion via Traefik pour l'accès HTTP
- Rate limiting configuré
- Scaling horizontal

### 1.2 Prérequis
- Cluster Kubernetes opérationnel (voir LOT2)
- Images Docker des 3 microservices disponibles
- Namespaces créés

## 2. Structure du repository

```
k8s/
├── base/
│   ├── redis/
│   │   ├── statefulset.yaml
│   │   ├── service.yaml
│   │   └── pvc.yaml
│   ├── users/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── configmap.yaml
│   ├── quotes/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── configmap.yaml
│   └── search/
│       ├── deployment.yaml
│       ├── service.yaml
│       └── configmap.yaml
├── production/
│   ├── namespace.yaml
│   ├── secrets.yaml
│   ├── resourcequota.yaml
│   ├── ingress.yaml
│   └── kustomization.yaml
└── qualification/
    ├── namespace.yaml
    ├── secrets.yaml
    ├── resourcequota.yaml
    ├── ingress.yaml
    └── kustomization.yaml
```

## 3. Manifestes Redis

### 3.1 PersistentVolumeClaim

**Fichier** : `k8s/base/redis/pvc.yaml`

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: redis-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

### 3.2 StatefulSet

**Fichier** : `k8s/base/redis/statefulset.yaml`

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis
spec:
  serviceName: redis
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      securityContext:
        fsGroup: 999
        runAsUser: 999
        runAsNonRoot: true
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
          name: redis
        volumeMounts:
        - name: redis-data
          mountPath: /data
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          tcpSocket:
            port: 6379
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - redis-cli
            - ping
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: redis-data
        persistentVolumeClaim:
          claimName: redis-pvc
```

### 3.3 Service

**Fichier** : `k8s/base/redis/service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: redis
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
  clusterIP: None
```

## 4. Manifestes Service Users

### 4.1 ConfigMap

**Fichier** : `k8s/base/users/configmap.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: users-config
data:
  REDIS_HOST: redis
  REDIS_PORT: "6379"
  REDIS_DB: "0"
  APP_PORT: "5000"
  CSV_FILE_USERS: "initial_data_users.csv"
```

### 4.2 Deployment

**Fichier** : `k8s/base/users/deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: users
spec:
  replicas: 2
  selector:
    matchLabels:
      app: users
  template:
    metadata:
      labels:
        app: users
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
      - name: users
        image: haddock-users:latest
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 5000
        envFrom:
        - configMapRef:
            name: users-config
        env:
        - name: ADMIN_KEY
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: ADMIN_KEY
        resources:
          requests:
            memory: "64Mi"
            cpu: "100m"
          limits:
            memory: "128Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: false
          runAsNonRoot: true
```

### 4.3 Service

**Fichier** : `k8s/base/users/service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: users
spec:
  selector:
    app: users
  ports:
  - port: 5000
    targetPort: 5000
  type: ClusterIP
```

### 4.4 HorizontalPodAutoscaler

**Fichier** : `k8s/base/users/hpa.yaml`

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: users-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: users
  minReplicas: 2
  maxReplicas: 5
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## 5. Manifestes Service Quotes

### 5.1 ConfigMap

**Fichier** : `k8s/base/quotes/configmap.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: quotes-config
data:
  REDIS_HOST: redis
  REDIS_PORT: "6379"
  REDIS_DB: "0"
  APP_PORT: "5000"
  CSV_FILE_QUOTES: "initial_data_quotes.csv"
```

### 5.2 Deployment

**Fichier** : `k8s/base/quotes/deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: quotes
spec:
  replicas: 2
  selector:
    matchLabels:
      app: quotes
  template:
    metadata:
      labels:
        app: quotes
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
      - name: quotes
        image: haddock-quotes:latest
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 5000
        envFrom:
        - configMapRef:
            name: quotes-config
        env:
        - name: ADMIN_KEY
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: ADMIN_KEY
        resources:
          requests:
            memory: "64Mi"
            cpu: "100m"
          limits:
            memory: "128Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: false
          runAsNonRoot: true
```

### 5.3 Service et HPA

Similaires au service Users (adapter les noms).

## 6. Manifestes Service Search

Structure similaire aux services Users et Quotes (voir sections 4 et 5).

## 7. Configuration par environnement

### 7.1 Production

**Fichier** : `k8s/production/namespace.yaml`

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
```

**Fichier** : `k8s/production/secrets.yaml`

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: production
type: Opaque
stringData:
  ADMIN_KEY: "production_secret_key_change_me"
```

**Fichier** : `k8s/production/resourcequota.yaml`

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: production-quota
  namespace: production
spec:
  hard:
    requests.cpu: "2"
    requests.memory: 4Gi
    limits.cpu: "4"
    limits.memory: 8Gi
    pods: "20"
```

**Fichier** : `k8s/production/ingress.yaml`

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: haddock-ingress
  namespace: production
  annotations:
    traefik.ingress.kubernetes.io/router.entrypoints: web
    traefik.ingress.kubernetes.io/router.middlewares: production-ratelimit@kubernetescrd
spec:
  rules:
  - host: production.192.168.1.100.nip.io  # Adapter l'IP
    http:
      paths:
      - path: /users
        pathType: Prefix
        backend:
          service:
            name: users
            port:
              number: 5000
      - path: /quotes
        pathType: Prefix
        backend:
          service:
            name: quotes
            port:
              number: 5000
      - path: /search
        pathType: Prefix
        backend:
          service:
            name: search
            port:
              number: 5000
---
apiVersion: traefik.containo.us/v1alpha1
kind: Middleware
metadata:
  name: ratelimit
  namespace: production
spec:
  rateLimit:
    average: 10
    period: 1m
    burst: 5
```

### 7.2 Qualification

Structure similaire à Production avec :
- Namespace : `qualification`
- Host : `qualification.192.168.1.100.nip.io`
- Secrets différents
- ResourceQuota plus restrictifs

## 8. Déploiement avec Kustomize

### 8.1 Base kustomization

**Fichier** : `k8s/base/kustomization.yaml`

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - redis/pvc.yaml
  - redis/statefulset.yaml
  - redis/service.yaml
  - users/configmap.yaml
  - users/deployment.yaml
  - users/service.yaml
  - users/hpa.yaml
  - quotes/configmap.yaml
  - quotes/deployment.yaml
  - quotes/service.yaml
  - quotes/hpa.yaml
  - search/configmap.yaml
  - search/deployment.yaml
  - search/service.yaml
  - search/hpa.yaml
```

### 8.2 Production kustomization

**Fichier** : `k8s/production/kustomization.yaml`

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: production

resources:
  - namespace.yaml
  - ../base
  - secrets.yaml
  - resourcequota.yaml
  - ingress.yaml

namePrefix: prod-

commonLabels:
  environment: production
```

### 8.3 Qualification kustomization

**Fichier** : `k8s/qualification/kustomization.yaml`

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: qualification

resources:
  - namespace.yaml
  - ../base
  - secrets.yaml
  - resourcequota.yaml
  - ingress.yaml

namePrefix: qual-

commonLabels:
  environment: qualification

replicas:
  - name: users
    count: 1
  - name: quotes
    count: 1
  - name: search
    count: 1
```

## 9. Déploiement

### 9.1 Avec Kustomize

```bash
# Production
kubectl apply -k k8s/production/

# Qualification
kubectl apply -k k8s/qualification/

# Vérification
kubectl get all -n production
kubectl get all -n qualification
```

### 9.2 Sans Kustomize

```bash
# Production
kubectl apply -f k8s/production/namespace.yaml
kubectl apply -f k8s/production/secrets.yaml
kubectl apply -f k8s/production/resourcequota.yaml
kubectl apply -f k8s/base/redis/ -n production
kubectl apply -f k8s/base/users/ -n production
kubectl apply -f k8s/base/quotes/ -n production
kubectl apply -f k8s/base/search/ -n production
kubectl apply -f k8s/production/ingress.yaml

# Qualification
# Répéter avec namespace qualification
```

## 10. Déploiement avec Helm

### 10.1 Pourquoi Helm ?

Helm est le gestionnaire de paquets pour Kubernetes. Voici pourquoi nous l'utilisons :

| Avantage | Description |
|----------|-------------|
| **Templating** | Les valeurs sont centralisées dans `values.yaml`, évitant la duplication |
| **Versioning** | Chaque déploiement est versionné, facilitant les rollbacks |
| **Reproductibilité** | Un seul fichier de valeurs définit tout l'environnement |
| **Simplicité** | Une commande pour déployer toute l'application |
| **Gestion des releases** | Helm garde l'historique des déploiements |

### 10.2 Structure du chart Helm

Le chart Helm créé pour ce projet suit une structure simple et minimaliste :

```
helm/
└── haddock/
    ├── Chart.yaml              # Métadonnées du chart
    ├── values.yaml             # Valeurs par défaut
    └── templates/
        ├── _helpers.tpl        # Fonctions de templating réutilisables
        ├── redis-pv.yaml       # PersistentVolume et PVC pour Redis
        ├── redis-deployment.yaml
        ├── redis-service.yaml
        ├── citation-deployment.yaml
        ├── citation-service.yaml
        ├── user-deployment.yaml
        ├── user-service.yaml
        ├── recherche-deployment.yaml
        ├── recherche-service.yaml
        └── init-redis-job.yaml # Job d'initialisation des données
```

### 10.3 Chart.yaml

Le fichier `Chart.yaml` contient les métadonnées du chart :

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

### 10.4 values.yaml

Le fichier `values.yaml` centralise toutes les valeurs configurables :

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
    name: citation-image
    tag: "124"
  service:
    type: LoadBalancer
    port: 5000
    nodePort: 30002

# Service User
user:
  enabled: true
  replicaCount: 1
  image:
    name: user-image
    tag: "124"
  service:
    type: LoadBalancer
    port: 5000
    nodePort: 30001

# Service Recherche
recherche:
  enabled: true
  replicaCount: 1
  image:
    name: recherche-image
    tag: "124"
  service:
    type: LoadBalancer
    port: 5000
    nodePort: 30003

# Job d'initialisation Redis
initRedis:
  enabled: true
  image:
    name: init-redis-image
    tag: "125"
  dataPath: /data/bdd
```

### 10.5 Comment fonctionne le templating ?

Chaque template utilise les valeurs de `values.yaml` via la syntaxe Go :

```yaml
# Exemple : citation-deployment.yaml
{{- if .Values.citation.enabled }}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-citation
spec:
  replicas: {{ .Values.citation.replicaCount }}
  # ...
          image: {{ .Values.citation.image.name }}:{{ .Values.citation.image.tag }}
{{- end }}
```

**Explications :**
- `{{ .Values.xxx }}` : Accède aux valeurs du fichier `values.yaml`
- `{{ .Release.Name }}` : Nom de la release Helm (passé lors du `helm install`)
- `{{- if ... }}` : Condition pour activer/désactiver un composant
- `{{- include "haddock.labels" . }}` : Inclut les labels définis dans `_helpers.tpl`

### 10.6 Commandes de déploiement

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

### 10.7 Personnalisation des valeurs

Pour modifier les valeurs sans éditer `values.yaml`, utilisez `--set` :

```bash
# Changer le nombre de réplicas
helm install haddock ./helm/haddock --set citation.replicaCount=3

# Changer le tag de l'image
helm install haddock ./helm/haddock --set citation.image.tag="125"

# Désactiver un service
helm install haddock ./helm/haddock --set recherche.enabled=false

# Combiner plusieurs modifications
helm install haddock ./helm/haddock \
  --set citation.replicaCount=2 \
  --set user.replicaCount=2 \
  --set recherche.replicaCount=2
```

### 10.8 Création de fichiers values par environnement

Pour gérer plusieurs environnements, créez des fichiers de valeurs spécifiques :

**values-production.yaml :**
```yaml
citation:
  replicaCount: 2
user:
  replicaCount: 2
recherche:
  replicaCount: 2
```

**values-qualification.yaml :**
```yaml
citation:
  replicaCount: 1
user:
  replicaCount: 1
recherche:
  replicaCount: 1
```

**Déploiement :**
```bash
# Production
helm install haddock-prod ./helm/haddock -f ./helm/haddock/values-production.yaml

# Qualification
helm install haddock-qual ./helm/haddock -f ./helm/haddock/values-qualification.yaml
```

### 10.9 Rollback

Helm conserve l'historique des déploiements :

```bash
# Voir l'historique
helm history haddock

# Revenir à une version précédente
helm rollback haddock 1
```

## 11. Vérifications

### 11.1 État des déploiements

```bash
# Production
kubectl get pods -n production
kubectl get svc -n production
kubectl get ingress -n production

# Qualification
kubectl get pods -n qualification
kubectl get svc -n qualification
kubectl get ingress -n qualification
```

### 11.2 Logs

```bash
# Logs d'un service
kubectl logs -f deployment/users -n production

# Logs de tous les pods d'un déploiement
kubectl logs -f -l app=users -n production
```

### 11.3 Tests des endpoints

```bash
# Variables
PROD_HOST="production.192.168.1.100.nip.io"
QUAL_HOST="qualification.192.168.1.100.nip.io"
ADMIN_KEY="production_secret_key_change_me"

# Test Production - Users
curl http://$PROD_HOST/users -H "Authorization: $ADMIN_KEY"

# Test Production - Quotes
curl http://$PROD_HOST/quotes

# Test Production - Search
curl "http://$PROD_HOST/search?keyword=tonnerre" -H "Authorization: $ADMIN_KEY"

# Test Qualification
curl http://$QUAL_HOST/users -H "Authorization: $ADMIN_KEY"
```

### 11.4 Test du rate limiting

```bash
# Envoyer plus de 10 requêtes en 1 minute
for i in {1..15}; do
  echo "Request $i:"
  curl -w " - Status: %{http_code}\n" http://$PROD_HOST/quotes
  sleep 1
done

# Les requêtes 11-15 devraient être limitées (429 Too Many Requests)
```

## 12. Troubleshooting

### 12.1 Pods en erreur

```bash
# Describe pour voir les événements
kubectl describe pod <pod-name> -n production

# Logs
kubectl logs <pod-name> -n production

# Logs du conteneur précédent (si crash)
kubectl logs <pod-name> -n production --previous
```

### 12.2 Service inaccessible

```bash
# Vérifier l'Ingress
kubectl describe ingress haddock-ingress -n production

# Vérifier le Service
kubectl describe svc users -n production

# Vérifier les endpoints
kubectl get endpoints users -n production

# Tester depuis un pod interne
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -n production -- sh
# Dans le pod :
curl http://users:5000/health
```

### 12.3 Problèmes de persistance

```bash
# Vérifier les PV/PVC
kubectl get pv
kubectl get pvc -n production

# Describe pour voir les problèmes
kubectl describe pvc redis-pvc -n production
```

## 13. Mise à jour de l'application

### 13.1 Rolling update

```bash
# Nouvelle version de l'image
docker build -t haddock-users:v1.1 ./microservices/users

# Update du deployment
kubectl set image deployment/users users=haddock-users:v1.1 -n production

# Suivre le rollout
kubectl rollout status deployment/users -n production

# Historique
kubectl rollout history deployment/users -n production
```

### 13.2 Rollback

```bash
# Rollback à la version précédente
kubectl rollout undo deployment/users -n production

# Rollback à une version spécifique
kubectl rollout undo deployment/users -n production --to-revision=2
```

## 14. Monitoring

### 14.1 Dashboard Traefik

```bash
# Port-forward vers le dashboard Traefik
kubectl port-forward -n kube-system $(kubectl get pods -n kube-system | grep traefik | awk '{print $1}') 9000:9000

# Accès : http://localhost:9000/dashboard/
```

### 14.2 Métriques Kubernetes

```bash
# Utilisation par pod
kubectl top pods -n production

# Utilisation par node
kubectl top nodes
```

## 15. Checklist de déploiement

- [ ] Namespaces créés (production, qualification)
- [ ] Secrets créés dans chaque namespace
- [ ] ResourceQuota appliqués
- [ ] Redis déployé avec PVC
- [ ] Service Users déployé
- [ ] Service Quotes déployé
- [ ] Service Search déployé
- [ ] Services Kubernetes créés
- [ ] HPA configurés
- [ ] Ingress configuré avec rate limiting
- [ ] Tests des endpoints réussis
- [ ] Test du rate limiting réussi
- [ ] Health checks fonctionnels
- [ ] Logs accessibles
- [ ] Documentation à jour
- [ ] Bonus : Helm chart créé (optionnel)

## Annexes

### Annexe A : Commandes utiles

```bash
# Tout voir dans un namespace
kubectl get all -n production

# Redémarrer un deployment
kubectl rollout restart deployment/users -n production

# Scaler manuellement
kubectl scale deployment/users --replicas=3 -n production

# Entrer dans un pod
kubectl exec -it <pod-name> -n production -- sh

# Port-forward pour debug
kubectl port-forward svc/users 5000:5000 -n production

# Supprimer tout un namespace (ATTENTION)
kubectl delete namespace production
```

### Annexe B : NetworkPolicy (optionnel)

Pour renforcer la sécurité, limiter les communications entre namespaces :

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-from-other-namespaces
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector: {}
```
