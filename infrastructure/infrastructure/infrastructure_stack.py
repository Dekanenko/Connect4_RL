from aws_cdk import (
    CfnOutput,
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecr as ecr,
    aws_elasticloadbalancingv2 as elbv2,
    aws_logs as logs,
)
from constructs import Construct

class Connect4CdkStack(Stack):
    """
    Defines the complete AWS infrastructure for the Connect4 application.
    This stack creates a VPC, an ECS Fargate cluster, an Application Load Balancer,
    and deploys the frontend and backend services, routing traffic appropriately.
    """
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Part 1: Networking and Cluster Foundation
        vpc = ec2.Vpc(self, "Connect4Vpc", max_azs=2)
        cluster = ecs.Cluster(self, "Connect4Cluster", vpc=vpc)

        # Part 2: Load Balancer
        # Create the ALB first, as its DNS name is needed by the frontend container.
        lb = elbv2.ApplicationLoadBalancer(
            self, "Connect4ALB",
            vpc=vpc,
            internet_facing=True
        )

        # Part 3: Referencing Existing ECR Repositories
        backend_repo = ecr.Repository.from_repository_name(self, "BackendRepo", "connect4-backend")
        frontend_repo = ecr.Repository.from_repository_name(self, "FrontendRepo", "connect4-frontend")

        # Part 4: Task Definitions (Blueprints for our Services)
        # Backend Task Definition
        backend_task_definition = ecs.FargateTaskDefinition(
            self, "BackendTaskDef",
            memory_limit_mib=1024,
            cpu=512,
        )
        backend_task_definition.add_container(
            "BackendContainer",
            image=ecs.ContainerImage.from_ecr_repository(backend_repo, "latest"),
            port_mappings=[ecs.PortMapping(container_port=8000)],
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="Connect4Backend",
                log_retention=logs.RetentionDays.ONE_WEEK
            ),
            environment={
                # Allow the deployed frontend to make requests to this backend.
                "CORS_ALLOWED_ORIGINS": f"http://{lb.load_balancer_dns_name}"
            }
        )

        # Frontend Task Definition (now safely referencing the ALB)
        frontend_task_definition = ecs.FargateTaskDefinition(
            self, "FrontendTaskDef",
            memory_limit_mib=1024,
            cpu=512,
        )
        frontend_task_definition.add_container(
            "FrontendContainer",
            image=ecs.ContainerImage.from_ecr_repository(frontend_repo, "latest"),
            port_mappings=[ecs.PortMapping(container_port=8501)],
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="Connect4Frontend",
                log_retention=logs.RetentionDays.ONE_WEEK
            ),
            environment={
                "BACKEND_URL": f"http://{lb.load_balancer_dns_name}/api"
            }
        )

        # Part 5: ECS Services
        # Create the services that will run the tasks.
        backend_service = ecs.FargateService(
            self, "BackendService",
            cluster=cluster,
            task_definition=backend_task_definition,
            desired_count=1,
        )

        frontend_service = ecs.FargateService(
            self, "FrontendService",
            cluster=cluster,
            task_definition=frontend_task_definition,
            desired_count=1,
        )

        # Part 6: ALB Listener and Routing Rules
        listener = lb.add_listener("PublicListener", port=80)

        # Default rule: Route traffic to the frontend
        listener.add_targets(
            "FrontendTarget",
            port=80,
            targets=[frontend_service],
            health_check=elbv2.HealthCheck(
                path="/api/healthz",
                port="8501"
            )
        )

        # Path-based rule for the backend
        backend_target_group = elbv2.ApplicationTargetGroup(
            self, "BackendTargetGroup",
            vpc=vpc,
            port=8000,
            targets=[backend_service],
            health_check=elbv2.HealthCheck(
                path="/api/health",
                port="8000",
            )
        )

        listener.add_action(
            "BackendRule",
            priority=1,
            conditions=[
                elbv2.ListenerCondition.path_patterns(["/api/*"])
            ],
            action=elbv2.ListenerAction.forward(
                target_groups=[backend_target_group]
            )
        )

        # Part 7: Stack Outputs
        CfnOutput(
            self, "LoadBalancerDNS",
            value=f"http://{lb.load_balancer_dns_name}"
        )