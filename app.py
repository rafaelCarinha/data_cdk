#!/usr/bin/env python3
import json
import os
import sys

import aws_cdk as cdk

from data_cdk.athena_stack import AthenaStack
import yaml
from yaml.loader import SafeLoader

from data_cdk.glue_stack import GlueStack
from data_cdk.redshift_stack import RedshiftStack
from data_cdk.s3_stack import S3Stack
from data_cdk.lambda_stack import LambdaStack
from data_cdk.security_stack import SecurityStack
from data_cdk.vpc_stack import VPCStack

app = cdk.App()

environment = app.node.try_get_context("environment")

deployment_name = 'Waymark-Data'

if environment is None:
    print('Environment parameter is required!')
    print('Example: cdk deploy --all --context environment=PROD')
    print('Exiting program...')
    exit(app)
elif environment != 'PROD' and environment != 'STAGE' and environment != 'DEV':
    print('The allowed values for environment are: DEV/STAGE/PROD')
    print('Exiting program...')
    exit(app)

accounts = []
with open(f'configuration_accounts_{environment}.yaml') as f:
    data = yaml.load(f, Loader=SafeLoader)
    accounts = data['ACCOUNTS']
    print(accounts)

with open(f'configuration_{environment}.yaml') as f:
    config_data = yaml.load(f, Loader=SafeLoader)


organization_account_list = []
organization_account_names = ['claims', 'claims-post', 'eligibility', 'hl7']  # TODO - Externalize property

for organization_account_name in organization_account_names:
    account_dict = {'account_name': f"{organization_account_name}"}
    organization_account_list.append(account_dict)

# VPC, S3, Athena, Glue, IAM, Redshift
for account in accounts:
    account_id = str(accounts[account]['ACCOUNT_ID'])
    account_region = accounts[account]['REGION']
    account_name = accounts[account]['ACCOUNT_NAME']

    vpc_stack = VPCStack(
        app,
        f"{environment}-{deployment_name}-VPCStack",
        environment=environment,
        env=cdk.Environment(account=account_id, region=account_region)
    )
    S3Stack(
        app,
        f"{environment}-{deployment_name}-S3Stack",
        environment=environment,
        organization_account_list=organization_account_list,
        env=cdk.Environment(account=account_id, region=account_region)
    )
    LambdaStack(
        app,
        f"{environment}-{deployment_name}-LambdaStack",
        environment=environment,
        organization_account_list=organization_account_list,
        env=cdk.Environment(account=account_id, region=account_region)
    )
    GlueStack(
        app,
        f"{environment}-{deployment_name}-GlueStack",
        environment=environment,
        org=account_name,
        org_id=account_id,
        organization_account_list=organization_account_list,
        env=cdk.Environment(account=account_id, region=account_region)
    )
    AthenaStack(
        app,
        f"{environment}-{deployment_name}-AthenaStack",
        environment=environment,
        org=account_name,
        env=cdk.Environment(account=account_id, region=account_region)
    )
    # SecurityStack
    security_stack = SecurityStack(
        app,
        f"{environment}-{deployment_name}-SecurityStack",
        vpc=vpc_stack.vpc,
        environment=environment,
        org=account_name,
        env=cdk.Environment(account=account_id, region=account_region)
    )
    RedshiftStack(
        app,
        f"{environment}-{deployment_name}-RedshiftStack",
        environment=environment,
        org=account_name,
        vpc=vpc_stack.vpc,
        sg=security_stack.redshift_sg,
        account_id=account_id,
        region=account_region,
        env=cdk.Environment(account=account_id, region=account_region)
    )

app.synth()
