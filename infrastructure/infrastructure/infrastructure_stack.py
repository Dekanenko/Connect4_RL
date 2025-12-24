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

        # Part 1: Networking Foundation (VPC)
        # We create a new Virtual Private Cloud to provide a logically isolated
        # network environment for the application. This is a best practice.
        vpc = ec2.Vpc(self, "Connect4Vpc", max_azs=2)

        # Part 2: Container Orchestration (ECS Cluster)
        # An ECS Cluster is a logical grouping for our containerized services.
        cluster = ecs.Cluster(self, "Connect4Cluster", vpc=vpc)

        # Part 3: Referencing Existing ECR Repositories
        # We get a reference to the Docker image repositories that our CI/CD
        # pipeline is already pushing to.
        backend_repo = ecr.Repository.from_repository_name(self, "BackendRepo", "connect4-backend")
        frontend_repo = ecr.Repository.from_repository_name(self, "FrontendRepo", "connect4-frontend")

        # Part 4: Task Definitions (Blueprints for our Services)
        # These define what Docker image to use, CPU/memory requirements,
        # and logging configuration for our containers.

        # Backend Task Definition
        backend_task_definition = ecs.FargateTaskDefinition(
            self, "BackendTaskDef",
            memory_limit_mib=512,
            cpu=256,
        )
        backend_task_definition.add_container(
            "BackendContainer",
            image=ecs.ContainerImage.from_ecr_repository(backend_repo, "latest"),
            port_mappings=[ecs.PortMapping(container_port=8000)],
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="Connect4Backend",
                log_retention=logs.RetentionDays.ONE_WEEK
            )
        )

        # Frontend Task Definition
        frontend_task_definition = ecs.FargateTaskDefinition(
            self, "FrontendTaskDef",
            memory_limit_mib=512,
            cpu=256,
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
                "BACKEND_URL": f"http://{lb.load_balancer_dns_name}"
            }
        )

        # Part 5: Application Load Balancer (ALB) and Services
        # We create ECS Services to run and maintain our tasks, and an ALB
        # to route public internet traffic to the correct service.
        
        # Create the ECS services
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

        # Create the Application Load Balancer
        lb = elbv2.ApplicationLoadBalancer(
            self, "Connect4ALB",
            vpc=vpc,
            internet_facing=True
        )
        
        # Create a listener on port 80 (HTTP)
        listener = lb.add_listener("PublicListener", port=80)

        # Add the frontend service as the default target for the listener.
        # This will create a default target group and route traffic to the frontend.
        listener.add_targets(
            "FrontendTarget",
            port=80,
            targets=[frontend_service],
            health_check=elbv2.HealthCheck(
                path="/healthz",
                port="8501"
            )
        )

        # Now, create a second, path-based rule for the backend service.
        # This rule will be checked first (due to priority 1). If the path matches
        # /api/*, traffic will be sent to the backend. Otherwise, it will fall through
        # to the default rule (the frontend).
        
        # First, create a target group for the backend
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

        # Part 6: Stack Outputs
        # This will print the public DNS name of the Load Balancer in the
        # terminal after a successful deployment.
        CfnOutput(
            self, "LoadBalancerDNS",
            value=f"http://{lb.load_balancer_dns_name}"
        )
