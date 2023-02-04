import json
import boto3

glue_client = boto3.client('glue')


def lambda_handler(event, context):
    glue_client.start_crawler(Name='claims-crawler')

    return {
        'statusCode': 200,
        'body': json.dumps('Crawler started!')
    }
