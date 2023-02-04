from aws_cdk import (
    aws_ec2 as ec2,
    Stack,
)
from constructs import Construct
import yaml
from yaml.loader import SafeLoader


class SecurityStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.Vpc, environment: str, org: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        with open(f'configuration_{environment}.yaml') as f:
            data = yaml.load(f, Loader=SafeLoader)

            org = org.lower()

            # Redshift SG
            self.redshift_sg = ec2.SecurityGroup(
                self,
                id=f"redshift_security_group_{org}",
                vpc=vpc,
                security_group_name=f"redshift_security_group_{org}",
                description="Security Group for Redshift"
            )
