from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_redshift as redshift,
    aws_iam as iam, CfnOutput
)
from constructs import Construct
import yaml
from yaml.loader import SafeLoader
from aws_cdk.aws_iam import ManagedPolicy
import os


class RedshiftStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, environment: str, org: str, vpc: ec2.Vpc,
                 sg: ec2.SecurityGroup, account_id: str, region: str,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        with open(f'configuration_{environment}.yaml') as f:
            data = yaml.load(f, Loader=SafeLoader)

            redshift_config = data['REDSHIFT']
            master_username = redshift_config['MASTER_USERNAME']
            master_password = redshift_config['MASTER_PASSWORD']
            instance_type = redshift_config['EC2_INSTANCE_TYPE']
            managed_policy = redshift_config['MANAGED_POLICY']
            custom_managed_policy_name = redshift_config['CUSTOM_MANAGED_POLICY_NAME']

            environment = environment.lower()
            org = org.lower()

            # TODO - Increase Redshift Security
            # TODO - Create Redshift Spectrum(federated queries) for AURORA(Waymark Core and LightHouse)

            self.custom_spectrum_policy = iam.Policy(self,
                                                     custom_managed_policy_name + f"-{org}-construct",
                                                     policy_name=custom_managed_policy_name + f"-{org}",
                                                     statements=[iam.PolicyStatement(
                                                         effect=iam.Effect.ALLOW,
                                                         resources=["*"],
                                                         actions=[
                                                             "glue:CreateDatabase",
                                                             "glue:GetDatabase",
                                                             "glue:GetDatabases",
                                                             "glue:UpdateDatabase",
                                                             "glue:CreateTable",
                                                             "glue:UpdateTable",
                                                             "glue:GetTable",
                                                             "glue:GetTables",
                                                             "glue:BatchCreatePartition",
                                                             "glue:CreatePartition",
                                                             "glue:UpdatePartition",
                                                             "glue:GetPartition",
                                                             "glue:GetPartitions",
                                                             "glue:BatchGetPartition"
                                                         ]
                                                     ), iam.PolicyStatement(
                                                         effect=iam.Effect.ALLOW,
                                                         resources=["*"],
                                                         actions=[
                                                             "s3:GetObject",
                                                             "s3:GetBucketAcl",
                                                             "s3:GetBucketCors",
                                                             "s3:GetEncryptionConfiguration",
                                                             "s3:GetBucketLocation",
                                                             "s3:ListBucket",
                                                             "s3:ListAllMyBuckets",
                                                             "s3:ListMultipartUploadParts",
                                                             "s3:ListBucketMultipartUploads",
                                                             "s3:PutObject",
                                                             "s3:PutBucketAcl",
                                                             "s3:PutBucketCors",
                                                             "s3:DeleteObject",
                                                             "s3:AbortMultipartUpload",
                                                             "s3:CreateBucket"
                                                         ]
                                                     )])

            self.redshift_role = iam.Role(self, "Role",
                                          assumed_by=iam.ServicePrincipal("redshift.amazonaws.com"),
                                          role_name=f"AWSRedshiftRole-{org}",
                                          description="Provides Redshift with the proper permissions to execute queries",
                                          managed_policies=[
                                              ManagedPolicy.from_managed_policy_arn(
                                                  self,
                                                  f"redshift-service-policy-{org}",
                                                  managed_policy
                                              ),
                                          ],
                                          )

            self.redshift_role.attach_inline_policy(self.custom_spectrum_policy)

            selection = vpc.select_subnets(
                subnet_type=ec2.SubnetType.PUBLIC
            )

            subnet_group = redshift.CfnClusterSubnetGroup(self, id=f"RedshiftSubnetGroup-{org}",
                                                          subnet_ids=selection.subnet_ids,
                                                          description="redshift_subnets-{org}")

            self.cluster = redshift.CfnCluster(self,
                                               f"{environment}-Redshift-{org}",
                                               cluster_identifier=f"{environment}-Redshift-{org}",
                                               db_name=f"{org}_cluster",
                                               node_type=f"{instance_type}",
                                               cluster_type="single-node",
                                               master_username=master_username,
                                               master_user_password=master_password,
                                               iam_roles=[f"arn:aws:iam::{account_id}:role/AWSRedshiftRole-{org}"],
                                               cluster_subnet_group_name=subnet_group.ref,
                                               )



