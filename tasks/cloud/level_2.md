[🏠 Home](../../README.md) · [Tasks](../README.md) · [Cloud Tasks](.)

# ☁️ Cloud & Data Center Tasks — Level 2 (🟡 Medium)

> **Objective:** Intermediate cloud — infrastructure automation, container services, serverless, and multi-tier architecture.  
> **Prerequisites:** Completed Level 1, Terraform installed, Docker knowledge  
> **Time Estimate:** 6–8 hours total

---

## Table of Contents

1. [Infrastructure as Code with Terraform](#1-infrastructure-as-code-with-terraform)
2. [Auto Scaling Groups & Launch Templates](#2-auto-scaling-groups--launch-templates)
3. [Container Deployment with ECS/Fargate](#3-container-deployment-with-ecsfargate)
4. [Serverless Functions (Lambda)](#4-serverless-functions-lambda)
5. [RDS Database Setup & Management](#5-rds-database-setup--management)
6. [Application Load Balancer Configuration](#6-application-load-balancer-configuration)
7. [S3 Static Website Hosting with CloudFront](#7-s3-static-website-hosting-with-cloudfront)
8. [CloudFormation Stack Management](#8-cloudformation-stack-management)
9. [Secrets Management with AWS Secrets Manager](#9-secrets-management-with-aws-secrets-manager)
10. [CI/CD Pipeline with CodePipeline](#10-cicd-pipeline-with-codepipeline)

---

## 1. Infrastructure as Code with Terraform

### Objective
Use Terraform to provision a VPC with subnets, security groups, and an EC2 instance.

### Tasks

**1.1** Initialize a Terraform project:
```bash
mkdir -p ~/terraform-lab && cd ~/terraform-lab

cat << 'EOF' > providers.tf
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}
EOF

terraform init
```

**1.2** Define variables:
```bash
cat << 'EOF' > variables.tf
variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}
EOF
```

**1.3** Create the VPC and networking:
```bash
cat << 'EOF' > network.tf
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "${var.environment}-vpc"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.environment}-public-subnet"
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.environment}-igw"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "${var.environment}-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}
EOF
```

**1.4** Create a security group and EC2 instance:
```bash
cat << 'EOF' > compute.tf
resource "aws_security_group" "web" {
  name_prefix = "${var.environment}-web-"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Restrict in production!
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.environment}-web-sg"
  }
}

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

resource "aws_instance" "web" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.web.id]

  user_data = <<-USERDATA
    #!/bin/bash
    yum install -y httpd
    systemctl start httpd
    echo "<h1>Hello from Terraform!</h1>" > /var/www/html/index.html
  USERDATA

  tags = {
    Name        = "${var.environment}-web-server"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}
EOF
```

**1.5** Add outputs:
```bash
cat << 'EOF' > outputs.tf
output "vpc_id" {
  value = aws_vpc.main.id
}

output "instance_public_ip" {
  value = aws_instance.web.public_ip
}

output "instance_id" {
  value = aws_instance.web.id
}
EOF
```

**1.6** Plan and apply:
```bash
terraform plan
terraform apply -auto-approve
terraform output
```

**1.7** Clean up:
```bash
terraform destroy -auto-approve
```

### Verification
- `terraform plan` shows expected resources
- `terraform apply` provisions VPC + subnet + SG + EC2
- `terraform destroy` removes all resources cleanly

---

## 2. Auto Scaling Groups & Launch Templates

### Objective
Create an Auto Scaling Group that automatically scales instances based on CPU.

### Tasks

**2.1** Create a Launch Template:
```bash
aws ec2 create-launch-template \
  --launch-template-name devops-lab-lt \
  --launch-template-data '{
    "ImageId": "'$AMI_ID'",
    "InstanceType": "t3.micro",
    "UserData": "'$(echo '#!/bin/bash
yum install -y httpd
systemctl start httpd
HOSTNAME=$(hostname)
echo "<h1>Server: $HOSTNAME</h1>" > /var/www/html/index.html' | base64)'"
  }'
```

**2.2** Create an Auto Scaling Group:
```bash
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name devops-lab-asg \
  --launch-template LaunchTemplateName=devops-lab-lt,Version='$Latest' \
  --min-size 2 \
  --max-size 4 \
  --desired-capacity 2 \
  --vpc-zone-identifier "$PUB_SUBNET" \
  --tags Key=Name,Value=asg-instance,PropagateAtLaunch=true
```

**2.3** Create a scaling policy:
```bash
aws autoscaling put-scaling-policy \
  --auto-scaling-group-name devops-lab-asg \
  --policy-name cpu-scale-up \
  --policy-type TargetTrackingScaling \
  --target-tracking-configuration '{
    "TargetValue": 70.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ASGAverageCPUUtilization"
    }
  }'
```

**2.4** Check ASG status:
```bash
aws autoscaling describe-auto-scaling-groups --auto-scaling-group-names devops-lab-asg \
  --query 'AutoScalingGroups[0].{Min:MinSize,Max:MaxSize,Desired:DesiredCapacity,Instances:Instances[].InstanceId}' \
  --output table
```

**2.5** Clean up:
```bash
aws autoscaling delete-auto-scaling-group --auto-scaling-group-name devops-lab-asg --force-delete
aws ec2 delete-launch-template --launch-template-name devops-lab-lt
```

### Verification
- ASG launches 2 instances automatically
- Scaling policy targets 70% CPU

---

## 3. Container Deployment with ECS/Fargate

### Objective
Deploy a containerized application on AWS ECS with Fargate (serverless containers).

### Architecture
```
  Internet ──► ALB ──► ECS Service (Fargate) ──► Container (nginx)
                            │
                            ├── Task 1 (10.0.1.x)
                            └── Task 2 (10.0.2.x)
```

### Tasks

**3.1** Create an ECS cluster:
```bash
aws ecs create-cluster --cluster-name devops-lab-cluster
```

**3.2** Register a task definition:
```bash
cat << 'EOF' > /tmp/task-def.json
{
  "family": "devops-lab-web",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "web",
      "image": "nginx:alpine",
      "portMappings": [
        {
          "containerPort": 80,
          "protocol": "tcp"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/devops-lab",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "web"
        }
      }
    }
  ]
}
EOF

aws ecs register-task-definition --cli-input-json file:///tmp/task-def.json
```

**3.3** Create a service:
```bash
aws ecs create-service \
  --cluster devops-lab-cluster \
  --service-name web-service \
  --task-definition devops-lab-web \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[$PUB_SUBNET],securityGroups=[$WEB_SG],assignPublicIp=ENABLED}"
```

**3.4** Check service status:
```bash
aws ecs describe-services --cluster devops-lab-cluster --services web-service \
  --query 'services[0].{Status:status,Running:runningCount,Desired:desiredCount}'
```

**3.5** Clean up:
```bash
aws ecs update-service --cluster devops-lab-cluster --service web-service --desired-count 0
aws ecs delete-service --cluster devops-lab-cluster --service web-service
aws ecs delete-cluster --cluster devops-lab-cluster
```

### Verification
- ECS cluster runs 2 Fargate tasks
- Tasks are reachable via their public IPs on port 80

---

## 4. Serverless Functions (Lambda)

### Objective
Create and invoke an AWS Lambda function, integrate with API Gateway.

### Tasks

**4.1** Create a Lambda function:
```bash
cat << 'EOF' > /tmp/lambda_function.py
import json

def lambda_handler(event, context):
    name = event.get('queryStringParameters', {}).get('name', 'World')
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'message': f'Hello, {name}! From Lambda.',
            'event': event
        })
    }
EOF

cd /tmp && zip lambda.zip lambda_function.py
```

**4.2** Create the IAM role for Lambda:
```bash
cat << 'EOF' > /tmp/trust-policy.json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {"Service": "lambda.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

ROLE_ARN=$(aws iam create-role --role-name lambda-devops-lab \
  --assume-role-policy-document file:///tmp/trust-policy.json \
  --query 'Role.Arn' --output text)

aws iam attach-role-policy --role-name lambda-devops-lab \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

**4.3** Deploy the function:
```bash
aws lambda create-function \
  --function-name devops-lab-hello \
  --runtime python3.12 \
  --handler lambda_function.lambda_handler \
  --zip-file fileb:///tmp/lambda.zip \
  --role $ROLE_ARN \
  --timeout 10 \
  --memory-size 128
```

**4.4** Invoke the function:
```bash
aws lambda invoke --function-name devops-lab-hello \
  --payload '{"queryStringParameters": {"name": "DevOps"}}' \
  /tmp/lambda-output.json

cat /tmp/lambda-output.json | python3 -m json.tool
```

**4.5** Update the function code:
```bash
# Modify and repackage
cd /tmp && zip lambda.zip lambda_function.py
aws lambda update-function-code --function-name devops-lab-hello \
  --zip-file fileb:///tmp/lambda.zip
```

**4.6** Clean up:
```bash
aws lambda delete-function --function-name devops-lab-hello
aws iam detach-role-policy --role-name lambda-devops-lab \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam delete-role --role-name lambda-devops-lab
```

### Verification
- Lambda function deploys and invokes successfully
- You understand the execution model: handler, event, context

---

## 5. RDS Database Setup & Management

### Objective
Provision an RDS PostgreSQL instance and manage backups.

### Tasks

**5.1** Create a DB subnet group:
```bash
aws rds create-db-subnet-group \
  --db-subnet-group-name devops-lab-db-subnets \
  --db-subnet-group-description "DevOps Lab DB Subnets" \
  --subnet-ids $PRIV_SUBNET_A $PRIV_SUBNET_B
```

**5.2** Create an RDS instance:
```bash
aws rds create-db-instance \
  --db-instance-identifier devops-lab-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15 \
  --master-username devops_admin \
  --master-user-password 'Ch@ng3M3N0w!' \
  --allocated-storage 20 \
  --db-subnet-group-name devops-lab-db-subnets \
  --vpc-security-group-ids $DB_SG \
  --backup-retention-period 7 \
  --no-publicly-accessible \
  --storage-encrypted \
  --tags Key=Environment,Value=dev Key=ManagedBy,Value=cli
```

**5.3** Check instance status:
```bash
aws rds describe-db-instances --db-instance-identifier devops-lab-db \
  --query 'DBInstances[0].{Status:DBInstanceStatus,Endpoint:Endpoint.Address,Port:Endpoint.Port,AZ:AvailabilityZone}' \
  --output table
```

**5.4** Create a manual snapshot:
```bash
aws rds create-db-snapshot \
  --db-instance-identifier devops-lab-db \
  --db-snapshot-identifier devops-lab-db-manual-snap
```

**5.5** Connect and test (from an EC2 in the same VPC):
```bash
psql -h <endpoint> -U devops_admin -d postgres
```

**5.6** Clean up:
```bash
aws rds delete-db-instance --db-instance-identifier devops-lab-db \
  --skip-final-snapshot
```

> **⚠️ Gotcha:** RDS instances cost money even when idle. Always clean up lab resources. Use `--skip-final-snapshot` only in labs, NEVER in production.

### Verification
- RDS instance is running in a private subnet
- Encryption at rest is enabled
- Automated backups are configured for 7 days

---

## 6. Application Load Balancer Configuration

### Objective
Set up an ALB with target groups, health checks, and path-based routing.

### Tasks

**6.1** Create a target group:
```bash
TG_ARN=$(aws elbv2 create-target-group \
  --name devops-lab-tg \
  --protocol HTTP \
  --port 80 \
  --vpc-id $VPC_ID \
  --health-check-path /health \
  --health-check-interval-seconds 30 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 3 \
  --query 'TargetGroups[0].TargetGroupArn' --output text)
```

**6.2** Create the ALB:
```bash
ALB_ARN=$(aws elbv2 create-load-balancer \
  --name devops-lab-alb \
  --subnets $PUB_SUBNET_A $PUB_SUBNET_B \
  --security-groups $ALB_SG \
  --scheme internet-facing \
  --type application \
  --query 'LoadBalancers[0].LoadBalancerArn' --output text)
```

**6.3** Create a listener:
```bash
aws elbv2 create-listener \
  --load-balancer-arn $ALB_ARN \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=$TG_ARN
```

**6.4** Register targets:
```bash
aws elbv2 register-targets --target-group-arn $TG_ARN \
  --targets Id=$INSTANCE_ID_1 Id=$INSTANCE_ID_2
```

**6.5** Check target health:
```bash
aws elbv2 describe-target-health --target-group-arn $TG_ARN --output table
```

### Verification
- ALB is internet-facing and reachable
- Health checks pass for registered targets
- Traffic is distributed across targets

---

## 7. S3 Static Website Hosting with CloudFront

### Objective
Host a static website on S3 and serve it through CloudFront CDN.

### Tasks

**7.1** Create a website bucket:
```bash
SITE_BUCKET="devops-lab-site-$(date +%s)"
aws s3 mb s3://$SITE_BUCKET

aws s3 website s3://$SITE_BUCKET \
  --index-document index.html \
  --error-document error.html
```

**7.2** Upload website content:
```bash
cat << 'EOF' > /tmp/index.html
<!DOCTYPE html>
<html>
<head><title>DevOps Lab</title></head>
<body>
<h1>Welcome to DevOps Lab!</h1>
<p>Served from S3 + CloudFront</p>
</body>
</html>
EOF

aws s3 cp /tmp/index.html s3://$SITE_BUCKET/index.html --content-type text/html
```

**7.3** Create a CloudFront Origin Access Identity:
```bash
OAI_ID=$(aws cloudfront create-cloud-front-origin-access-identity \
  --cloud-front-origin-access-identity-config CallerReference=$(date +%s),Comment="DevOps Lab OAI" \
  --query 'CloudFrontOriginAccessIdentity.Id' --output text)
```

**7.4** Create a bucket policy for CloudFront:
```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

aws s3api put-bucket-policy --bucket $SITE_BUCKET --policy '{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"AWS": "arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity '$OAI_ID'"},
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::'$SITE_BUCKET'/*"
  }]
}'
```

**7.5** Create a CloudFront distribution:
```bash
aws cloudfront create-distribution \
  --origin-domain-name $SITE_BUCKET.s3.amazonaws.com \
  --default-root-object index.html
```

### Verification
- Website loads through the CloudFront URL (*.cloudfront.net)
- S3 bucket is NOT publicly accessible directly
- CloudFront caches and serves the content

---

## 8. CloudFormation Stack Management

### Objective
Deploy infrastructure using AWS CloudFormation templates.

### Tasks

**8.1** Create a CloudFormation template:
```bash
cat << 'EOF' > /tmp/stack.yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: DevOps Lab - Web Server Stack

Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues: [dev, staging, prod]
  InstanceType:
    Type: String
    Default: t3.micro

Resources:
  WebSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Web Server SG
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0

  WebServer:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: !Ref LatestAmiId
      InstanceType: !Ref InstanceType
      SecurityGroupIds:
        - !Ref WebSecurityGroup
      Tags:
        - Key: Name
          Value: !Sub ${Environment}-web-server
        - Key: Environment
          Value: !Ref Environment

  LatestAmiId:
    Type: AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>
    Default: /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64

Outputs:
  InstanceId:
    Value: !Ref WebServer
  PublicIP:
    Value: !GetAtt WebServer.PublicIp
EOF
```

**8.2** Deploy the stack:
```bash
aws cloudformation create-stack --stack-name devops-lab-web \
  --template-body file:///tmp/stack.yaml \
  --parameters ParameterKey=Environment,ParameterValue=dev
```

**8.3** Monitor stack creation:
```bash
aws cloudformation describe-stack-events --stack-name devops-lab-web \
  --query 'StackEvents[0:5].{Resource:LogicalResourceId,Status:ResourceStatus,Reason:ResourceStatusReason}' \
  --output table
```

**8.4** Get stack outputs:
```bash
aws cloudformation describe-stacks --stack-name devops-lab-web \
  --query 'Stacks[0].Outputs' --output table
```

**8.5** Clean up:
```bash
aws cloudformation delete-stack --stack-name devops-lab-web
```

### Verification
- Stack creates successfully with all resources
- Outputs display instance ID and public IP
- Stack deletes cleanly

---

## 9. Secrets Management with AWS Secrets Manager

### Objective
Securely store and retrieve application secrets.

### Tasks

**9.1** Create a secret:
```bash
aws secretsmanager create-secret --name devops-lab/db-credentials \
  --secret-string '{
    "username": "app_user",
    "password": "S3cur3P@ssw0rd!",
    "host": "db.devops.internal",
    "port": 5432,
    "dbname": "appdb"
  }'
```

**9.2** Retrieve the secret:
```bash
aws secretsmanager get-secret-value --secret-id devops-lab/db-credentials \
  --query 'SecretString' --output text | python3 -m json.tool
```

**9.3** Update the secret:
```bash
aws secretsmanager update-secret --secret-id devops-lab/db-credentials \
  --secret-string '{
    "username": "app_user",
    "password": "N3wP@ssw0rd!2024",
    "host": "db.devops.internal",
    "port": 5432,
    "dbname": "appdb"
  }'
```

**9.4** Enable automatic rotation:
```bash
# View rotation config (requires a Lambda rotation function)
aws secretsmanager describe-secret --secret-id devops-lab/db-credentials
```

**9.5** Clean up:
```bash
aws secretsmanager delete-secret --secret-id devops-lab/db-credentials --force-delete-without-recovery
```

> **⚠️ Gotcha:** Never hardcode secrets in code, environment variables, or config files checked into git. Always use a secrets manager.

### Verification
- Secrets are stored encrypted and retrievable via CLI
- You understand the difference between Secrets Manager and Parameter Store

---

## 10. CI/CD Pipeline with CodePipeline

### Objective
Create a basic CI/CD pipeline using AWS CodePipeline and CodeBuild.

### Architecture
```
  GitHub Repo ──► CodePipeline ──► CodeBuild ──► Deploy to S3/ECS
       │               │                │
       │         (Source Stage)   (Build Stage)   (Deploy Stage)
       │
  Push triggers pipeline
```

### Tasks

**10.1** Create a CodeBuild project:
```bash
cat << 'EOF' > /tmp/buildspec.yml
version: 0.2

phases:
  install:
    runtime-versions:
      python: 3.12
  pre_build:
    commands:
      - echo "Running tests..."
      - pip install -r requirements.txt
      - python -m pytest tests/
  build:
    commands:
      - echo "Building application..."
      - python setup.py sdist
  post_build:
    commands:
      - echo "Build completed on $(date)"

artifacts:
  files:
    - '**/*'
  discard-paths: no
EOF
```

**10.2** Create the CodeBuild project:
```bash
aws codebuild create-project \
  --name devops-lab-build \
  --source type=GITHUB,location=https://github.com/your-repo.git \
  --artifacts type=NO_ARTIFACTS \
  --environment type=LINUX_CONTAINER,computeType=BUILD_GENERAL1_SMALL,image=aws/codebuild/amazonlinux2-x86_64-standard:5.0 \
  --service-role arn:aws:iam::<account>:role/CodeBuildRole
```

**10.3** Start a manual build:
```bash
aws codebuild start-build --project-name devops-lab-build
```

**10.4** Check build status:
```bash
aws codebuild list-builds-for-project --project-name devops-lab-build
aws codebuild batch-get-builds --ids <build-id> \
  --query 'builds[0].{Status:buildStatus,Phase:currentPhase}'
```

### Verification
- CodeBuild project builds successfully
- You understand the buildspec.yml phases: install → pre_build → build → post_build

---

> **Level 2 Complete!** You now have intermediate cloud infrastructure skills.  
> **Next:** [Level 3 — Advanced Cloud Tasks](level_3.md)

[🏠 Home](../../README.md) · [Tasks](../README.md)
