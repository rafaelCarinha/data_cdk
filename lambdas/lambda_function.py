import json
import boto3
import os

glue_client = boto3.client('glue')


def lambda_handler(event, context):

    org_name = os.environ['organization']
    glue_client.start_workflow_run(Name=f'{org_name}_workflow')

    return {
        'statusCode': 200,
        'body': json.dumps(f'Workflow {org_name} started!')
    }
