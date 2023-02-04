from aws_cdk import (
    Stack,
    aws_athena as athena,
    aws_s3 as s3
)
from constructs import Construct
import yaml
from yaml.loader import SafeLoader


class AthenaStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, environment: str, org: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        with open(f'configuration_{environment}.yaml') as f:
            data = yaml.load(f, Loader=SafeLoader)

            athena_config = data['ATHENA']
            s3_query_output_bucket = athena_config['S3_QUERY_OUTPUT_BUCKET']
            query_encryption_option = athena_config['QUERY_ENCRYPTION_OPTION']
            org = org.lower()
            environment = environment.lower()

            bucket = s3.Bucket(self,
                               construct_id,
                               bucket_name=f"{environment}-{org}-{s3_query_output_bucket}",
                               block_public_access=s3.BlockPublicAccess.BLOCK_ALL)

            cfn_work_group = athena.CfnWorkGroup(self, "MyCfnWorkGroup",
                                                 name=f"workgroup-{org}",
                                                 work_group_configuration=athena.CfnWorkGroup.WorkGroupConfigurationProperty(
                                                     result_configuration=athena.CfnWorkGroup.ResultConfigurationProperty(
                                                         encryption_configuration=athena.CfnWorkGroup.EncryptionConfigurationProperty(
                                                             encryption_option=query_encryption_option,
                                                         ),
                                                         output_location=f"s3://{environment}-{org}-{s3_query_output_bucket}/"
                                                     )
                                                 ),
                                                 )

