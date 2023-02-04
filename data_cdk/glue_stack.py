import yaml
from aws_cdk import \
    (Stack,
     aws_glue as glue,
     aws_iam as iam
     )
from aws_cdk.aws_iam import ManagedPolicy, Effect
from constructs import Construct
from yaml.loader import SafeLoader


class GlueStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, environment: str, org: str, org_id: str,
                 organization_account_list: [], **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        with open(f'configuration_{environment}.yaml') as f:
            data = yaml.load(f, Loader=SafeLoader)

            s3_config = data['S3']
            staged_bucket_name = s3_config['STAGED_BUCKET']
            glue_config = data['GLUE']
            service_principal = glue_config['SERVICE_PRINCIPAL']
            managed_policy = glue_config['MANAGED_POLICY']
            crawler_delete_behavior = glue_config['CRAWLER_DELETE_BEHAVIOR']

            environment = environment.lower()
            org = org.lower()

            glue_managed_policies = []

            for policy in managed_policy.split(","):
                glue_managed_policy = ManagedPolicy.from_managed_policy_arn(
                    self,
                    f"glue-service-policy-{org}-{policy.split('/')[-1]}",
                    policy
                )
                glue_managed_policies.append(glue_managed_policy)

            # create glue database
            glue_db = glue.CfnDatabase(self, "MyCfnDatabase",
                                       catalog_id=org_id,
                                       database_input=glue.CfnDatabase.DatabaseInputProperty(
                                           name=f"redshift-database-{org}",
                                       )
                                       )

            glue_crawler_role = iam.Role(self, "Role",
                                         assumed_by=iam.ServicePrincipal(service_principal),
                                         role_name=f"AWSGlueServiceRole-{org}",
                                         description="Assigns the managed policy AWSGlueServiceRole to AWS Glue "
                                                     "Crawler so it can crawl S3 buckets",
                                         managed_policies=glue_managed_policies,
                                         )

            # add policy to role to grant access to S3 asset bucket and public buckets
            iam_policy_for_assets = iam.Policy(self, "iam-policy-forAssets",
                                               force=True,
                                               policy_name=f"glue-policy-workflowAssetAccess-{org}",
                                               roles=[glue_crawler_role],
                                               statements=[
                                                   iam.PolicyStatement(
                                                       effect=Effect.ALLOW,
                                                       actions=[
                                                           "s3:*",
                                                       ],
                                                       resources=[
                                                           f"arn:aws:s3:::{environment}-waymark*"],
                                                   )
                                               ]
                                               )

            # Define paths for scripts and data
            staged = f"s3://{environment}-waymark-{org}-{staged_bucket_name}"

            glue_crawler_s3 = glue.CfnCrawler(self, "glue-crawler-s3",
                                              database_name=f"redshift-database-{org}",
                                              name=f"{org}-crawler",
                                              table_prefix="redshift/",
                                              role=glue_crawler_role.role_name,
                                              schema_change_policy=glue.CfnCrawler.SchemaChangePolicyProperty(
                                                  delete_behavior=crawler_delete_behavior
                                              ),
                                              targets=glue.CfnCrawler.TargetsProperty(
                                                  s3_targets=[glue.CfnCrawler.S3TargetProperty(
                                                      path=staged,
                                                  )]
                                              ),
                                              )

            # Create Crawlers/Databases for the associated Organizations
            for organizations_account in organization_account_list:
                organization_account_name = organizations_account['account_name'].lower()

                # create glue database
                glue_db = glue.CfnDatabase(self, f"MyCfnDatabase{organization_account_name}",
                                           catalog_id=org_id,
                                           database_input=glue.CfnDatabase.DatabaseInputProperty(
                                               name=f"database-{organization_account_name}",
                                           )
                                           )

                # Define paths for scripts and data
                staged = f"s3://{environment}-waymark-{organization_account_name}-{staged_bucket_name}"

                glue_crawler_s3 = glue.CfnCrawler(self, f"glue-crawler-s3-{organization_account_name}",
                                                  database_name=f"database-{organization_account_name}",
                                                  name=f"{organization_account_name}-crawler",
                                                  role=glue_crawler_role.role_name,
                                                  schema_change_policy=glue.CfnCrawler.SchemaChangePolicyProperty(
                                                      delete_behavior=crawler_delete_behavior
                                                  ),
                                                  targets=glue.CfnCrawler.TargetsProperty(
                                                      s3_targets=[glue.CfnCrawler.S3TargetProperty(
                                                          path=staged,
                                                      )]
                                                  ),
                                                  )
