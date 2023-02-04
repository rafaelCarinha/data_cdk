from aws_cdk import (
    Stack,
    aws_s3 as s3
)
from constructs import Construct
import yaml
from yaml.loader import SafeLoader


class S3Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, environment: str, organization_account_list: [],
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        with open(f'configuration_{environment}.yaml') as f:
            data = yaml.load(f, Loader=SafeLoader)

            s3_config = data['S3']
            staged_bucket_name = s3_config['STAGED_BUCKET']
            shared_bucket_name = s3_config['SHARED_BUCKET']
            combined_bucket_name = s3_config['COMBINED_BUCKET']
            bucket_list = [staged_bucket_name, shared_bucket_name, combined_bucket_name]

            environment = environment.lower()

            for organizations_account in organization_account_list:
                organization_account_name = organizations_account['account_name'].lower()

                for bucket in bucket_list:
                    self.create_bucket(f"{environment}-waymark-{organization_account_name}-{bucket}",
                                       f"{environment}-waymark-{organization_account_name}-{bucket}")

    def create_bucket(self, name: str, construct_id: str):
        bucket = s3.Bucket(self,
                           construct_id,
                           bucket_name=name,
                           block_public_access=s3.BlockPublicAccess.BLOCK_ALL)

        return bucket
