from aws_cdk import Stack, aws_ec2 as ec2, aws_ssm as ssm
from constructs import Construct
import yaml
from yaml.loader import SafeLoader


class VPCStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, environment: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        with open(f'configuration_{environment}.yaml') as f:
            data = yaml.load(f, Loader=SafeLoader)

            vpc = data['VPC']
            vpc_cidr = vpc['VPC_CIDR']
            vpc_max_azs = vpc['VPC_MAX_AZS']
            vpc_nat_gateway_quantity = vpc['VPC_NAT_GATEWAY_QUANTITY']

            self.vpc = ec2.Vpc(self, construct_id,
                               cidr=vpc_cidr,
                               max_azs=vpc_max_azs,
                               enable_dns_hostnames=True,
                               enable_dns_support=True,
                               subnet_configuration=[
                                   ec2.SubnetConfiguration(
                                       name=f'{construct_id}-Public',
                                       subnet_type=ec2.SubnetType.PUBLIC,
                                       cidr_mask=24
                                   ),
                                   ec2.SubnetConfiguration(
                                       name=f'{construct_id}-Private',
                                       subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT,
                                       cidr_mask=24
                                   ),
                                   ec2.SubnetConfiguration(
                                       name=f'{construct_id}-Isolated',
                                       subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                                       cidr_mask=24
                                   ),
                               ],
                               nat_gateways=vpc_nat_gateway_quantity
                               )

            private_subnets = [subnet.subnet_id for subnet in self.vpc.private_subnets]

            count = 1
            for ps in private_subnets:
                ssm.StringParameter(self, f'{construct_id}-private-subnet-' + str(count),
                                    string_value=ps,
                                    parameter_name='/' + construct_id + '/private_subnet' + str(count)
                                    )
                count += 1
