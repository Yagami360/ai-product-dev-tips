import json

def lambda_handler(event, context):
    print("Hellow ")
    return {
        'statusCode': 200,
        'body': json.dumps('Hello!')
    }