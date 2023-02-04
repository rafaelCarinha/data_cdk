from aws_cdk import (
    Stack,
    aws_iam as iam,
    aws_lambda as lambda_,
)
from constructs import Construct
import yaml
from yaml.loader import SafeLoader


class LambdaStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, environment: str, organization_account_list: [],
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        __role_name = 'DEV_waymark_lambda_power_role'

        role = iam.Role.from_role_name(self, __role_name, role_name=__role_name)

        with open(f'configuration_{environment}.yaml') as f:
            data = yaml.load(f, Loader=SafeLoader)

            s3_config = data['S3']
            staged_bucket_name = s3_config['STAGED_BUCKET']
            bucket_list = [staged_bucket_name]

            environment = environment.lower()

            for organizations_account in organization_account_list:
                organization_account_name = organizations_account['account_name'].lower()

                for bucket in bucket_list:
                    self.create_bucket_lambda_trigger(f"{environment}-waymark-{organization_account_name}-{bucket}",
                                                      f"{environment}-waymark-{organization_account_name}-{bucket}",
                                                      role)

    def create_bucket_lambda_trigger(self, name: str, construct_id: str, role: str):

        lambda_.Function(self, name,
                         function_name=name,
                         runtime=lambda_.Runtime.PYTHON_3_9,
                         handler="lambda_function.lambda_handler",
                         code=lambda_.Code.from_asset(
                             "./lambdas"),
                         role=role,
                         )
