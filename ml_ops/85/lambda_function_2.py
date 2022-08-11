import json

def lambda_handler(event, context):
    print("World!")
    return {
        'statusCode': 200,
        'body': json.dumps('World!')
    }