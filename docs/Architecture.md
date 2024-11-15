# Architecture du Projet

## Objectif du Projet
Ce projet utilise AWS Glue, Step Functions, et Lambda pour orchestrer un processus ETL avec notifications automatiques.

## Services Utilisés
- **AWS Glue** : Effectue les transformations de données en trois étapes.
- **AWS Step Functions** : Orchestration du workflow ETL, assurant la séquence d'exécution et la gestion des erreurs.
- **AWS Lambda** : Envoie une notification de fin de processus via Amazon SNS.
- **Amazon SNS** : Service de notification pour les alertes de fin de workflow.

## Schéma de l'Architecture
![Diagramme de l'Architecture](../architecture_diagram.png)

## Choix Techniques

1. **AWS Glue** :
   - Justification : Service de transformation de données entièrement géré, idéal pour les pipelines ETL.
   - Séparé en trois jobs pour modularité et débogage plus facile.

2. **AWS Step Functions** :
   - Justification : Orchestration sans serveur, permettant une gestion d'erreurs intégrée avec la stratégie `Catch`.
   - Avantage : Permet d'automatiser l'ETL sans créer de logique complexe de gestion d'étapes.

3. **AWS Lambda et SNS** :
   - Justification : Solution simple pour envoyer une notification de fin de processus. Le code Lambda utilise `boto3` pour interagir avec SNS.

## Résilience et Gestion des Erreurs
- Chaque job Glue est configuré pour passer à l’étape `HandleFailure` en cas d’erreur, évitant ainsi des problèmes d’incohérence.
- L'architecture permet d'identifier et de résoudre les erreurs plus rapidement grâce à la gestion centralisée des erreurs.

## Conclusion
Cette architecture utilise des services AWS entièrement gérés pour offrir un pipeline ETL automatisé, résilient, et facile à surveiller.
