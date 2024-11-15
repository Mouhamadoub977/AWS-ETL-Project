import boto3
import json

# Créons un client SNS pour interagir avec le service SNS d'AWS
sns_client = boto3.client('sns')

def lambda_handler(event, context):
    # Elle va récupère le message depuis l'événement Step Functions,
    # ou utilise un message par défaut si aucun n'est fourni
    message = event.get("message", "Notification from Step Functions")
    
    # ARN de mon topic SNS où envoyer la notification
    sns_arn = "arn:aws:sns:eu-west-2:476561027603:Momo_sns" 

    # Puis on publie le message sur le topic SNS
    response = sns_client.publish(
        TopicArn=sns_arn,
        Message=message,
        Subject="Notification Workflow Step Function"  # Objet de la notification
    )

    return {
        'statusCode': 200,
        'body': json.dumps('Notification sent successfully')
    }
