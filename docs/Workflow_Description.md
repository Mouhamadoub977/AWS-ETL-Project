# Description du Workflow Step Functions

Ce fichier décrit le flux de travail orchestré par AWS Step Functions, qui exécute plusieurs jobs AWS Glue et envoie une notification finale via AWS Lambda.

## Étapes du Workflow

1. **Job1** : 
   - **Description** : Exécute le premier job Glue pour préparer les données.
   - **Entrées** : Données initiales chargées depuis `Retal.csv`.
   - **Sorties** : Données nettoyées et enrichies pour l’étape suivante.

2. **Job2** : 
   - **Description** : Effectue une transformation supplémentaire sur les données.
   - **Entrées** : Données issues de Job1.
   - **Sorties** : Données prêtes pour la dernière transformation.

3. **Job3** : 
   - **Description** : Finalise la transformation et stocke les résultats.
   - **Entrées** : Données issues de Job2.
   - **Sorties** : Données prêtes pour l'analyse ou l'archivage.

4. **SendNotification** :
   - **Description** : Utilise une fonction Lambda pour envoyer une notification indiquant que le processus ETL est terminé.
   - **Détails** : La fonction Lambda utilise Amazon SNS pour envoyer une notification à un numéro de téléphone ou un endpoint défini.

5. **HandleFailure** :
   - **Description** : Gestion des erreurs pour chaque étape. Si un job échoue, cette étape est déclenchée, et le workflow est stoppé.
   - **Détails** : Fournit une cause d’échec dans les logs pour faciliter le dépannage.

## Logique de Rattrapage des Erreurs
Chaque job comporte une stratégie de rattrapage (`Catch`) pour rediriger les erreurs vers l’étape `HandleFailure`. Cela garantit une gestion robuste des erreurs et arrête le workflow en cas d’échec.
