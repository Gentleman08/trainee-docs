[🏠 Home](../README.md) · [Labs](README.md)

# ☁️ Cloud Practice Lab — Deploy a Production-Grade Web App on AWS

> **Objective:** Build a complete cloud infrastructure from scratch — VPC, compute, database, load balancer, monitoring, IaC, and CI/CD — using both CLI and Terraform.  
> **Difficulty:** Progressive (Easy → Hard)  
> **Time Estimate:** 6–8 hours  
> **Prerequisites:** AWS Free Tier account, AWS CLI configured, Terraform installed, Docker installed  
> **Cost Warning:** This lab uses AWS resources. Stay within free tier where possible. Estimated cost if everything runs for 4 hours: ~$2–5. **Always clean up!**

---

## Table of Contents

1. [Lab Overview & Architecture](#1-lab-overview--architecture)
2. [Phase 1 — VPC & Network Foundation](#2-phase-1--vpc--network-foundation)
3. [Phase 2 — Compute: Launch & Configure EC2](#3-phase-2--compute-launch--configure-ec2)
4. [Phase 3 — Database: RDS PostgreSQL](#4-phase-3--database-rds-postgresql)
5. [Phase 4 — Load Balancer & Auto Scaling](#5-phase-4--load-balancer--auto-scaling)
6. [Phase 5 — S3 & Static Assets](#6-phase-5--s3--static-assets)
7. [Phase 6 — Infrastructure as Code (Terraform)](#7-phase-6--infrastructure-as-code-terraform)
8. [Phase 7 — Monitoring & Alerting](#8-phase-7--monitoring--alerting)
9. [Phase 8 — Container Deployment (ECS Fargate)](#9-phase-8--container-deployment-ecs-fargate)
10. [Phase 9 — Security Hardening](#10-phase-9--security-hardening)
11. [Complete Cleanup](#11-complete-cleanup)
12. [Lab Validation Checklist](#12-lab-validation-checklist)

---

## 1. Lab Overview & Architecture

### What You Will Build
```
  ┌────────────────────── AWS Cloud ──────────────────────┐
  │                                                        │
  │  Route 53 (DNS)                                        │
  │       │                                                │
  │  ┌────▼────────────────────────────────────────────┐  │
  │  │            Application Load Balancer             │  │
  │  │               (Public Subnets)                   │  │
  │  └────┬──────────────────────────┬─────────────────┘  │
  │       │                          │                     │
  │  ┌────▼──────────┐  ┌───────────▼──────────┐         │
  │  │ EC2 / Fargate  │  │ EC2 / Fargate        │         │
  │  │  AZ-a          │  │  AZ-b                │         │
  │  │ (Private Sub)  │  │ (Private Sub)        │         │
  │  └────┬──────────┘  └───────────┬──────────┘         │
  │       │                          │                     │
  │  ┌────▼──────────────────────────▼─────────────────┐  │
  │  │        RDS PostgreSQL (Multi-AZ)                 │  │
  │  │           (Data Subnets)                         │  │
  │  └─────────────────────────────────────────────────┘  │
  │                                                        │
  │  S3 Bucket (Static Assets)   CloudWatch (Monitoring)  │
  └────────────────────────────────────────────────────────┘
```

### What You'll Learn
- VPC architecture with public, private, and data subnets
- EC2 instance lifecycle and user data scripts
- RDS managed database service
- ALB with health checks and target groups
- Auto Scaling Groups
- S3 for static asset hosting
- Terraform for IaC
- CloudWatch monitoring and alerting
- ECS Fargate for container deployments
- Security best practices

---

## 2. Phase 1 — VPC & Network Foundation

### Step 1.1 — Set environment variables
```bash
export AWS_REGION="us-east-1"
export PROJECT="devops-lab"
export VPC_CIDR="10.0.0.0/16"
```

### Step 1.2 — Create the VPC
```bash
VPC_ID=$(aws ec2 create-vpc \
  --cidr-block $VPC_CIDR \
  --tag-specifications "ResourceType=vpc,Tags=[{Key=Name,Value=${PROJECT}-vpc},{Key=Project,Value=${PROJECT}}]" \
  --query 'Vpc.VpcId' --output text)

aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-hostnames
aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-support

echo "VPC: $VPC_ID"
```

### Step 1.3 — Create subnets across 2 AZs
```bash
# Public Subnets
PUB_SUB_A=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.1.0/24 \
  --availability-zone ${AWS_REGION}a \
  --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=${PROJECT}-public-a}]" \
  --query 'Subnet.SubnetId' --output text)

PUB_SUB_B=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.2.0/24 \
  --availability-zone ${AWS_REGION}b \
  --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=${PROJECT}-public-b}]" \
  --query 'Subnet.SubnetId' --output text)

# Private Subnets (App Tier)
PRIV_SUB_A=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.3.0/24 \
  --availability-zone ${AWS_REGION}a \
  --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=${PROJECT}-private-a}]" \
  --query 'Subnet.SubnetId' --output text)

PRIV_SUB_B=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.4.0/24 \
  --availability-zone ${AWS_REGION}b \
  --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=${PROJECT}-private-b}]" \
  --query 'Subnet.SubnetId' --output text)

# Data Subnets (DB Tier)
DATA_SUB_A=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.5.0/24 \
  --availability-zone ${AWS_REGION}a \
  --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=${PROJECT}-data-a}]" \
  --query 'Subnet.SubnetId' --output text)

DATA_SUB_B=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.6.0/24 \
  --availability-zone ${AWS_REGION}b \
  --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=${PROJECT}-data-b}]" \
  --query 'Subnet.SubnetId' --output text)

echo "Public:  $PUB_SUB_A, $PUB_SUB_B"
echo "Private: $PRIV_SUB_A, $PRIV_SUB_B"
echo "Data:    $DATA_SUB_A, $DATA_SUB_B"
```

### Step 1.4 — Create Internet Gateway and NAT Gateway
```bash
# Internet Gateway
IGW_ID=$(aws ec2 create-internet-gateway \
  --tag-specifications "ResourceType=internet-gateway,Tags=[{Key=Name,Value=${PROJECT}-igw}]" \
  --query 'InternetGateway.InternetGatewayId' --output text)
aws ec2 attach-internet-gateway --internet-gateway-id $IGW_ID --vpc-id $VPC_ID

# Elastic IP for NAT Gateway
EIP_ALLOC=$(aws ec2 allocate-address --domain vpc --query 'AllocationId' --output text)

# NAT Gateway (in public subnet)
NAT_ID=$(aws ec2 create-nat-gateway --subnet-id $PUB_SUB_A --allocation-id $EIP_ALLOC \
  --tag-specifications "ResourceType=natgateway,Tags=[{Key=Name,Value=${PROJECT}-nat}]" \
  --query 'NatGateway.NatGatewayId' --output text)

echo "Waiting for NAT Gateway to become available..."
aws ec2 wait nat-gateway-available --nat-gateway-ids $NAT_ID
echo "NAT Gateway ready: $NAT_ID"
```

### Step 1.5 — Create Route Tables
```bash
# Public Route Table → Internet Gateway
PUB_RT=$(aws ec2 create-route-table --vpc-id $VPC_ID \
  --tag-specifications "ResourceType=route-table,Tags=[{Key=Name,Value=${PROJECT}-public-rt}]" \
  --query 'RouteTable.RouteTableId' --output text)
aws ec2 create-route --route-table-id $PUB_RT --destination-cidr-block 0.0.0.0/0 --gateway-id $IGW_ID
aws ec2 associate-route-table --route-table-id $PUB_RT --subnet-id $PUB_SUB_A
aws ec2 associate-route-table --route-table-id $PUB_RT --subnet-id $PUB_SUB_B

# Private Route Table → NAT Gateway
PRIV_RT=$(aws ec2 create-route-table --vpc-id $VPC_ID \
  --tag-specifications "ResourceType=route-table,Tags=[{Key=Name,Value=${PROJECT}-private-rt}]" \
  --query 'RouteTable.RouteTableId' --output text)
aws ec2 create-route --route-table-id $PRIV_RT --destination-cidr-block 0.0.0.0/0 --nat-gateway-id $NAT_ID
aws ec2 associate-route-table --route-table-id $PRIV_RT --subnet-id $PRIV_SUB_A
aws ec2 associate-route-table --route-table-id $PRIV_RT --subnet-id $PRIV_SUB_B

# Data Route Table → No internet access (local only)
DATA_RT=$(aws ec2 create-route-table --vpc-id $VPC_ID \
  --tag-specifications "ResourceType=route-table,Tags=[{Key=Name,Value=${PROJECT}-data-rt}]" \
  --query 'RouteTable.RouteTableId' --output text)
aws ec2 associate-route-table --route-table-id $DATA_RT --subnet-id $DATA_SUB_A
aws ec2 associate-route-table --route-table-id $DATA_RT --subnet-id $DATA_SUB_B
```

### Step 1.6 — Verify
```bash
aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" \
  --query 'Subnets[].{Name:Tags[?Key==`Name`]|[0].Value,AZ:AvailabilityZone,CIDR:CidrBlock}' \
  --output table
```

> **✅ Checkpoint:** 6 subnets across 2 AZs, public routes to IGW, private routes to NAT, data has no internet route.

---

## 3. Phase 2 — Compute: Launch & Configure EC2

### Step 2.1 — Create Security Groups
```bash
# ALB Security Group
ALB_SG=$(aws ec2 create-security-group --group-name ${PROJECT}-alb-sg \
  --description "ALB Security Group" --vpc-id $VPC_ID --query 'GroupId' --output text)
aws ec2 authorize-security-group-ingress --group-id $ALB_SG --protocol tcp --port 80 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $ALB_SG --protocol tcp --port 443 --cidr 0.0.0.0/0

# App Security Group (only from ALB)
APP_SG=$(aws ec2 create-security-group --group-name ${PROJECT}-app-sg \
  --description "App Security Group" --vpc-id $VPC_ID --query 'GroupId' --output text)
aws ec2 authorize-security-group-ingress --group-id $APP_SG --protocol tcp --port 80 --source-group $ALB_SG

# DB Security Group (only from App)
DB_SG=$(aws ec2 create-security-group --group-name ${PROJECT}-db-sg \
  --description "DB Security Group" --vpc-id $VPC_ID --query 'GroupId' --output text)
aws ec2 authorize-security-group-ingress --group-id $DB_SG --protocol tcp --port 5432 --source-group $APP_SG

echo "ALB SG: $ALB_SG | App SG: $APP_SG | DB SG: $DB_SG"
```

### Step 2.2 — Create a key pair
```bash
aws ec2 create-key-pair --key-name ${PROJECT}-key \
  --query 'KeyMaterial' --output text > ~/.ssh/${PROJECT}-key.pem
chmod 400 ~/.ssh/${PROJECT}-key.pem
```

### Step 2.3 — Find the latest AMI
```bash
AMI_ID=$(aws ec2 describe-images --owners amazon \
  --filters "Name=name,Values=al2023-ami-2023*-x86_64" \
  --query 'sort_by(Images, &CreationDate)[-1].ImageId' --output text)
echo "AMI: $AMI_ID"
```

### Step 2.4 — Launch an EC2 instance with user data
```bash
cat << 'USERDATA' > /tmp/userdata.sh
#!/bin/bash
yum update -y
yum install -y httpd
systemctl start httpd
systemctl enable httpd

TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
INSTANCE_ID=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/instance-id)
AZ=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/placement/availability-zone)

cat > /var/www/html/index.html << EOF
<h1>DevOps Lab</h1>
<p>Instance: ${INSTANCE_ID}</p>
<p>AZ: ${AZ}</p>
<p>Time: $(date)</p>
EOF

cat > /var/www/html/health << EOF
OK
EOF
USERDATA

INSTANCE_ID=$(aws ec2 run-instances \
  --image-id $AMI_ID \
  --instance-type t3.micro \
  --key-name ${PROJECT}-key \
  --subnet-id $PRIV_SUB_A \
  --security-group-ids $APP_SG \
  --user-data file:///tmp/userdata.sh \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=${PROJECT}-web-1},{Key=Project,Value=${PROJECT}}]" \
  --query 'Instances[0].InstanceId' --output text)

echo "Instance: $INSTANCE_ID"
aws ec2 wait instance-running --instance-ids $INSTANCE_ID
echo "Instance is running!"
```

> **✅ Checkpoint:** EC2 instance is running in the private subnet with Apache serving a health page.

---

## 4. Phase 3 — Database: RDS PostgreSQL

### Step 3.1 — Create a DB Subnet Group
```bash
aws rds create-db-subnet-group \
  --db-subnet-group-name ${PROJECT}-db-subnets \
  --db-subnet-group-description "Lab DB Subnets" \
  --subnet-ids $DATA_SUB_A $DATA_SUB_B
```

### Step 3.2 — Launch an RDS instance
```bash
aws rds create-db-instance \
  --db-instance-identifier ${PROJECT}-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15 \
  --master-username lab_admin \
  --master-user-password 'L@bP@ss2024!' \
  --allocated-storage 20 \
  --db-subnet-group-name ${PROJECT}-db-subnets \
  --vpc-security-group-ids $DB_SG \
  --no-publicly-accessible \
  --storage-encrypted \
  --backup-retention-period 7 \
  --tags Key=Name,Value=${PROJECT}-db Key=Project,Value=${PROJECT}

echo "Waiting for RDS to become available (this takes 5-10 minutes)..."
aws rds wait db-instance-available --db-instance-identifier ${PROJECT}-db
echo "RDS is ready!"
```

### Step 3.3 — Get the endpoint
```bash
DB_ENDPOINT=$(aws rds describe-db-instances --db-instance-identifier ${PROJECT}-db \
  --query 'DBInstances[0].Endpoint.Address' --output text)
echo "DB Endpoint: $DB_ENDPOINT"
```

### Step 3.4 — Test connectivity from EC2 (via bastion or SSM)
```bash
# If using SSM Session Manager:
aws ssm start-session --target $INSTANCE_ID

# Inside the instance:
sudo yum install -y postgresql15
psql -h $DB_ENDPOINT -U lab_admin -d postgres -c "SELECT version();"
```

> **✅ Checkpoint:** RDS is running in data subnets, accessible only from app-tier instances.

---

## 5. Phase 4 — Load Balancer & Auto Scaling

### Step 4.1 — Create the ALB
```bash
ALB_ARN=$(aws elbv2 create-load-balancer \
  --name ${PROJECT}-alb \
  --subnets $PUB_SUB_A $PUB_SUB_B \
  --security-groups $ALB_SG \
  --scheme internet-facing \
  --type application \
  --query 'LoadBalancers[0].LoadBalancerArn' --output text)

ALB_DNS=$(aws elbv2 describe-load-balancers --load-balancer-arns $ALB_ARN \
  --query 'LoadBalancers[0].DNSName' --output text)
echo "ALB DNS: $ALB_DNS"
```

### Step 4.2 — Create Target Group with health checks
```bash
TG_ARN=$(aws elbv2 create-target-group \
  --name ${PROJECT}-tg \
  --protocol HTTP --port 80 \
  --vpc-id $VPC_ID \
  --health-check-path /health \
  --health-check-interval-seconds 15 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 3 \
  --query 'TargetGroups[0].TargetGroupArn' --output text)
```

### Step 4.3 — Create ALB listener
```bash
aws elbv2 create-listener \
  --load-balancer-arn $ALB_ARN \
  --protocol HTTP --port 80 \
  --default-actions Type=forward,TargetGroupArn=$TG_ARN
```

### Step 4.4 — Create Launch Template
```bash
LT_ID=$(aws ec2 create-launch-template \
  --launch-template-name ${PROJECT}-lt \
  --launch-template-data "{
    \"ImageId\": \"${AMI_ID}\",
    \"InstanceType\": \"t3.micro\",
    \"KeyName\": \"${PROJECT}-key\",
    \"SecurityGroupIds\": [\"${APP_SG}\"],
    \"UserData\": \"$(base64 -w0 /tmp/userdata.sh)\",
    \"TagSpecifications\": [{
      \"ResourceType\": \"instance\",
      \"Tags\": [{\"Key\": \"Name\", \"Value\": \"${PROJECT}-asg-instance\"}]
    }]
  }" --query 'LaunchTemplate.LaunchTemplateId' --output text)
```

### Step 4.5 — Create Auto Scaling Group
```bash
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name ${PROJECT}-asg \
  --launch-template LaunchTemplateId=$LT_ID,Version='$Latest' \
  --min-size 2 --max-size 4 --desired-capacity 2 \
  --vpc-zone-identifier "${PRIV_SUB_A},${PRIV_SUB_B}" \
  --target-group-arns $TG_ARN \
  --health-check-type ELB \
  --health-check-grace-period 120
```

### Step 4.6 — Add scaling policy
```bash
aws autoscaling put-scaling-policy \
  --auto-scaling-group-name ${PROJECT}-asg \
  --policy-name ${PROJECT}-cpu-tracking \
  --policy-type TargetTrackingScaling \
  --target-tracking-configuration '{
    "TargetValue": 70.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ASGAverageCPUUtilization"
    }
  }'
```

### Step 4.7 — Verify
```bash
# Check target health
aws elbv2 describe-target-health --target-group-arn $TG_ARN --output table

# Test the ALB
curl -s http://$ALB_DNS/
```

> **✅ Checkpoint:** ALB distributes traffic to 2 EC2 instances via ASG. Health checks pass.

---

## 6. Phase 5 — S3 & Static Assets

### Step 5.1 — Create an S3 bucket for static assets
```bash
ASSETS_BUCKET="${PROJECT}-assets-$(date +%s)"
aws s3 mb s3://$ASSETS_BUCKET

# Block all public access (best practice)
aws s3api put-public-access-block --bucket $ASSETS_BUCKET \
  --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
```

### Step 5.2 — Enable versioning and lifecycle rules
```bash
aws s3api put-bucket-versioning --bucket $ASSETS_BUCKET \
  --versioning-configuration Status=Enabled

aws s3api put-bucket-lifecycle-configuration --bucket $ASSETS_BUCKET \
  --lifecycle-configuration '{
    "Rules": [{
      "ID": "move-to-ia",
      "Status": "Enabled",
      "Transitions": [
        {"Days": 30, "StorageClass": "STANDARD_IA"},
        {"Days": 90, "StorageClass": "GLACIER"}
      ],
      "NoncurrentVersionExpiration": {"NoncurrentDays": 30}
    }]
  }'
```

### Step 5.3 — Upload test assets
```bash
echo "body { font-family: sans-serif; }" > /tmp/style.css
echo "console.log('DevOps Lab');" > /tmp/app.js

aws s3 cp /tmp/style.css s3://$ASSETS_BUCKET/css/style.css --content-type text/css
aws s3 cp /tmp/app.js s3://$ASSETS_BUCKET/js/app.js --content-type application/javascript

aws s3 ls s3://$ASSETS_BUCKET/ --recursive
```

### Step 5.4 — Enable server-side encryption
```bash
aws s3api put-bucket-encryption --bucket $ASSETS_BUCKET \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "aws:kms"
      },
      "BucketKeyEnabled": true
    }]
  }'
```

> **✅ Checkpoint:** S3 bucket is private, versioned, encrypted, with lifecycle rules.

---

## 7. Phase 6 — Infrastructure as Code (Terraform)

### Step 6.1 — Create a Terraform project that replicates the manual setup
```bash
mkdir -p ~/terraform-cloud-lab && cd ~/terraform-cloud-lab
```

### Step 6.2 — Create the Terraform configuration
```bash
cat << 'EOF' > main.tf
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

variable "region" {
  default = "us-east-1"
}

variable "project" {
  default = "devops-lab-tf"
}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  tags = { Name = "${var.project}-vpc" }
}

# Public Subnet
resource "aws_subnet" "public_a" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "${var.region}a"
  map_public_ip_on_launch = true
  tags = { Name = "${var.project}-public-a" }
}

resource "aws_subnet" "public_b" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "${var.region}b"
  map_public_ip_on_launch = true
  tags = { Name = "${var.project}-public-b" }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  tags   = { Name = "${var.project}-igw" }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
  tags = { Name = "${var.project}-public-rt" }
}

resource "aws_route_table_association" "pub_a" {
  subnet_id      = aws_subnet.public_a.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "pub_b" {
  subnet_id      = aws_subnet.public_b.id
  route_table_id = aws_route_table.public.id
}

# Security Group
resource "aws_security_group" "web" {
  name_prefix = "${var.project}-web-"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# EC2 Instance
data "aws_ami" "al2023" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

resource "aws_instance" "web" {
  ami                    = data.aws_ami.al2023.id
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.public_a.id
  vpc_security_group_ids = [aws_security_group.web.id]

  user_data = <<-EOF
    #!/bin/bash
    yum install -y httpd
    systemctl start httpd
    echo "<h1>Hello from Terraform!</h1>" > /var/www/html/index.html
  EOF

  tags = { Name = "${var.project}-web" }
}

output "public_ip" {
  value = aws_instance.web.public_ip
}
EOF
```

### Step 6.3 — Deploy with Terraform
```bash
terraform init
terraform plan
terraform apply -auto-approve
terraform output
```

### Step 6.4 — Verify and destroy
```bash
curl http://$(terraform output -raw public_ip)
terraform destroy -auto-approve
```

> **✅ Checkpoint:** Terraform creates the same infrastructure reproducibly and cleans it up completely.

---

## 8. Phase 7 — Monitoring & Alerting

### Step 7.1 — Enable VPC Flow Logs
```bash
FLOW_LOG_GROUP="/vpc/${PROJECT}-flow-logs"
aws logs create-log-group --log-group-name $FLOW_LOG_GROUP

aws ec2 create-flow-logs \
  --resource-type VPC \
  --resource-ids $VPC_ID \
  --traffic-type ALL \
  --log-destination-type cloud-watch-logs \
  --log-group-name $FLOW_LOG_GROUP \
  --deliver-logs-permission-arn arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/VPCFlowLogRole
```

### Step 7.2 — Create a CloudWatch dashboard
```bash
aws cloudwatch put-dashboard --dashboard-name ${PROJECT}-dashboard \
  --dashboard-body '{
    "widgets": [
      {
        "type": "metric",
        "x": 0, "y": 0, "width": 12, "height": 6,
        "properties": {
          "metrics": [
            ["AWS/EC2", "CPUUtilization", "AutoScalingGroupName", "'${PROJECT}'-asg"]
          ],
          "period": 300,
          "stat": "Average",
          "title": "ASG CPU Utilization"
        }
      },
      {
        "type": "metric",
        "x": 12, "y": 0, "width": 12, "height": 6,
        "properties": {
          "metrics": [
            ["AWS/ApplicationELB", "RequestCount", "LoadBalancer", "'${PROJECT}'-alb"]
          ],
          "period": 60,
          "stat": "Sum",
          "title": "ALB Request Count"
        }
      }
    ]
  }'
```

### Step 7.3 — Create CPU alarm
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name ${PROJECT}-high-cpu \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --alarm-description "CPU > 80% for 10 minutes"
```

### Step 7.4 — Create an ALB 5xx alarm
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name ${PROJECT}-5xx-errors \
  --metric-name HTTPCode_Target_5XX_Count \
  --namespace AWS/ApplicationELB \
  --statistic Sum \
  --period 60 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 3 \
  --dimensions Name=LoadBalancer,Value=$(echo $ALB_ARN | cut -d'/' -f2-) \
  --alarm-description "More than 10 5xx errors in 3 minutes"
```

> **✅ Checkpoint:** Dashboard shows metrics, alarms configured for CPU and 5xx errors.

---

## 9. Phase 8 — Container Deployment (ECS Fargate)

### Step 8.1 — Create an ECR repository
```bash
REPO_URI=$(aws ecr create-repository --repository-name ${PROJECT}-app \
  --query 'repository.repositoryUri' --output text)
echo "ECR: $REPO_URI"
```

### Step 8.2 — Build and push a Docker image
```bash
mkdir -p /tmp/docker-lab && cd /tmp/docker-lab

cat << 'EOF' > Dockerfile
FROM nginx:alpine
COPY index.html /usr/share/nginx/html/
COPY health /usr/share/nginx/html/
EXPOSE 80
EOF

echo "<h1>DevOps Lab - Container Edition</h1>" > index.html
echo "OK" > health

# Login to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin $REPO_URI

docker build -t ${PROJECT}-app .
docker tag ${PROJECT}-app:latest $REPO_URI:latest
docker push $REPO_URI:latest
```

### Step 8.3 — Create ECS cluster and task definition
```bash
aws ecs create-cluster --cluster-name ${PROJECT}-cluster

cat << EOF > /tmp/task-def.json
{
  "family": "${PROJECT}-web",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/ecsTaskExecutionRole",
  "containerDefinitions": [{
    "name": "web",
    "image": "${REPO_URI}:latest",
    "portMappings": [{"containerPort": 80, "protocol": "tcp"}],
    "healthCheck": {
      "command": ["CMD-SHELL", "curl -f http://localhost/health || exit 1"],
      "interval": 15,
      "timeout": 5,
      "retries": 3
    }
  }]
}
EOF

aws ecs register-task-definition --cli-input-json file:///tmp/task-def.json
```

### Step 8.4 — Create ECS service
```bash
aws ecs create-service \
  --cluster ${PROJECT}-cluster \
  --service-name ${PROJECT}-web-svc \
  --task-definition ${PROJECT}-web \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[$PRIV_SUB_A,$PRIV_SUB_B],securityGroups=[$APP_SG],assignPublicIp=DISABLED}" \
  --load-balancers "targetGroupArn=$TG_ARN,containerName=web,containerPort=80"
```

### Step 8.5 — Verify
```bash
aws ecs describe-services --cluster ${PROJECT}-cluster --services ${PROJECT}-web-svc \
  --query 'services[0].{Status:status,Running:runningCount,Desired:desiredCount}' --output table

curl http://$ALB_DNS/
```

> **✅ Checkpoint:** Fargate tasks serving traffic through the ALB.

---

## 10. Phase 9 — Security Hardening

### Step 9.1 — Enable S3 Block Public Access at account level
```bash
aws s3control put-public-access-block --account-id $(aws sts get-caller-identity --query Account --output text) \
  --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
```

### Step 9.2 — Enable EBS default encryption
```bash
aws ec2 enable-ebs-encryption-by-default
```

### Step 9.3 — Create an IAM password policy
```bash
aws iam update-account-password-policy \
  --minimum-password-length 14 \
  --require-symbols \
  --require-numbers \
  --require-uppercase-characters \
  --require-lowercase-characters \
  --max-password-age 90 \
  --password-reuse-prevention 12
```

### Step 9.4 — Run a security audit
```bash
echo "=== Security Audit ==="

# Check for unencrypted volumes
echo "Unencrypted EBS volumes:"
aws ec2 describe-volumes --query 'Volumes[?!Encrypted].VolumeId' --output text

# Check for wide-open security groups
echo "Security groups with 0.0.0.0/0 on non-80/443:"
aws ec2 describe-security-groups --query 'SecurityGroups[].{ID:GroupId,Rules:IpPermissions[?IpRanges[?CidrIp==`0.0.0.0/0`]]}' --output json

# Check RDS encryption
echo "RDS encryption status:"
aws rds describe-db-instances --query 'DBInstances[].{ID:DBInstanceIdentifier,Encrypted:StorageEncrypted}' --output table
```

> **✅ Checkpoint:** All security hardening measures applied and verified.

---

## 11. Complete Cleanup

> **⚠️ IMPORTANT:** Run this to avoid unexpected charges!

```bash
echo "=== Starting Complete Cleanup ==="

# 1. Delete ECS service and cluster
aws ecs update-service --cluster ${PROJECT}-cluster --service ${PROJECT}-web-svc --desired-count 0
aws ecs delete-service --cluster ${PROJECT}-cluster --service ${PROJECT}-web-svc --force
aws ecs delete-cluster --cluster ${PROJECT}-cluster

# 2. Delete ECR repository
aws ecr delete-repository --repository-name ${PROJECT}-app --force

# 3. Delete Auto Scaling Group
aws autoscaling delete-auto-scaling-group --auto-scaling-group-name ${PROJECT}-asg --force-delete

# 4. Delete Launch Template
aws ec2 delete-launch-template --launch-template-name ${PROJECT}-lt

# 5. Delete ALB and Target Group
aws elbv2 delete-load-balancer --load-balancer-arn $ALB_ARN
sleep 30   # Wait for ALB to delete
aws elbv2 delete-target-group --target-group-arn $TG_ARN

# 6. Delete RDS
aws rds delete-db-instance --db-instance-identifier ${PROJECT}-db --skip-final-snapshot
aws rds wait db-instance-deleted --db-instance-identifier ${PROJECT}-db
aws rds delete-db-subnet-group --db-subnet-group-name ${PROJECT}-db-subnets

# 7. Delete S3 bucket
aws s3 rb s3://$ASSETS_BUCKET --force

# 8. Delete CloudWatch resources
aws cloudwatch delete-alarms --alarm-names ${PROJECT}-high-cpu ${PROJECT}-5xx-errors
aws cloudwatch delete-dashboards --dashboard-names ${PROJECT}-dashboard

# 9. Delete NAT Gateway and Elastic IP
aws ec2 delete-nat-gateway --nat-gateway-id $NAT_ID
sleep 60   # Wait for NAT to delete
aws ec2 release-address --allocation-id $EIP_ALLOC

# 10. Delete subnets, route tables, IGW, security groups, VPC
for sub in $PUB_SUB_A $PUB_SUB_B $PRIV_SUB_A $PRIV_SUB_B $DATA_SUB_A $DATA_SUB_B; do
    aws ec2 delete-subnet --subnet-id $sub
done

for rt in $PUB_RT $PRIV_RT $DATA_RT; do
    aws ec2 delete-route-table --route-table-id $rt
done

aws ec2 detach-internet-gateway --internet-gateway-id $IGW_ID --vpc-id $VPC_ID
aws ec2 delete-internet-gateway --internet-gateway-id $IGW_ID

for sg in $ALB_SG $APP_SG $DB_SG; do
    aws ec2 delete-security-group --group-id $sg
done

aws ec2 delete-vpc --vpc-id $VPC_ID

# 11. Delete key pair
aws ec2 delete-key-pair --key-name ${PROJECT}-key
rm -f ~/.ssh/${PROJECT}-key.pem

echo "=== Cleanup Complete ==="
```

---

## 12. Lab Validation Checklist

| Phase | Test | Expected Result | Pass? |
|-------|------|-----------------|-------|
| 1 | 6 subnets in 2 AZs | Correct CIDRs and routing | ☐ |
| 1 | Public subnet routes to IGW | `0.0.0.0/0 → igw-xxx` | ☐ |
| 1 | Private subnet routes to NAT | `0.0.0.0/0 → nat-xxx` | ☐ |
| 2 | EC2 running in private subnet | No public IP | ☐ |
| 2 | SG allows only ALB → App → DB | No direct internet to app/db | ☐ |
| 3 | RDS accessible from app tier | `psql` connects | ☐ |
| 3 | RDS NOT publicly accessible | `PubliclyAccessible: false` | ☐ |
| 4 | ALB health checks pass | All targets healthy | ☐ |
| 4 | ASG maintains 2 instances | Terminating one auto-replaces | ☐ |
| 5 | S3 bucket is private | No public access | ☐ |
| 6 | Terraform creates same infra | `terraform apply` succeeds | ☐ |
| 7 | CloudWatch alarms exist | CPU and 5xx alarms active | ☐ |
| 8 | Fargate tasks running | 2/2 tasks healthy | ☐ |
| 9 | EBS default encryption on | `aws ec2 get-ebs-encryption-by-default` | ☐ |
| 11 | All resources deleted | No unexpected charges | ☐ |

---

> **Lab Complete!** You've built a production-grade cloud infrastructure from scratch.  
> **Related:** [Cloud Handbook](../cloud/cloud_handbook.md) · [Cloud Tasks](../tasks/cloud/level_1.md)

[🏠 Home](../README.md) · [Labs](README.md)
