from aws_cdk import (
    Stack,
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_s3 as s3
)
from aws_cdk.aws_lambda_event_sources import S3EventSource
from constructs import Construct
import yaml
from yaml.loader import SafeLoader


class LambdaStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, environment: str, organization_account_list: [],
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # TODO - Externalize property and Create IAM Role programmatically for Lambda Function
        __role_name = 'DEV_waymark_lambda_power_role'

        role = iam.Role.from_role_name(self, __role_name, role_name=__role_name)

        with open(f'configuration_{environment}.yaml') as f:
            data = yaml.load(f, Loader=SafeLoader)

            s3_config = data['S3']
            raw_bucket_name = s3_config['RAW_BUCKET']
            bucket_list = [raw_bucket_name]

            environment = environment.lower()

            for organizations_account in organization_account_list:
                organization_account_name = organizations_account['account_name'].lower()

                for bucket in bucket_list:
                    construct_name = f"{environment}-waymark-{organization_account_name}-{bucket}"
                    self.create_bucket_lambda_trigger(construct_name,
                                                      construct_name,
                                                      role, organization_account_name)

    def create_bucket_lambda_trigger(self, name: str, construct_id: str, role: str, organization: str):

        bucket = s3.Bucket(self, name, bucket_name=name)

        lambda_function = lambda_.Function(self, f'{name}-lambda',
                                           function_name=name,
                                           runtime=lambda_.Runtime.PYTHON_3_9,
                                           handler="lambda_function.lambda_handler",
                                           code=lambda_.Code.from_asset(
                                               "./lambdas"),
                                           role=role,
                                           environment={"organization": organization}
                                           )

        lambda_function.add_event_source(S3EventSource(bucket,
                                                       events=[s3.EventType.OBJECT_CREATED_PUT,
                                                               s3.EventType.OBJECT_CREATED_POST]))
