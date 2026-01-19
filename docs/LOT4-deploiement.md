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

[À compléter]

## 3. Manifestes Redis

[À compléter]

## 4. Manifestes Service Users

[À compléter]

## 5. Manifestes Service Quotes

[À compléter]

## 6. Manifestes Service Search

[À compléter]

## 7. Configuration par environnement

[À compléter]

## 8. Déploiement avec Kustomize

[À compléter]

## 9. Déploiement

[À compléter]

## 10. Option Helm (Bonus)

[À compléter]

## 11. Vérifications

[À compléter]

## 12. Troubleshooting

[À compléter]

## 13. Mise à jour de l'application

[À compléter]

## 14. Monitoring

[À compléter]

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

[À compléter]
