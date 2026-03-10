[🏠 Home](../../README.md) · [Tasks](../README.md) · [Cloud Tasks](.)

# ☁️ Cloud & Data Center Tasks — Level 1 (🟢 Easy)

> **Objective:** Foundational cloud skills — CLI setup, basic resource management, storage, and IAM.  
> **Prerequisites:** Free tier account on AWS (or Azure/GCP), CLI tools installed  
> **Time Estimate:** 3–4 hours total

---

## Table of Contents

1. [Cloud CLI Setup & Configuration](#1-cloud-cli-setup--configuration)
2. [Exploring Cloud Regions & Availability Zones](#2-exploring-cloud-regions--availability-zones)
3. [Launch & Manage a Virtual Machine](#3-launch--manage-a-virtual-machine)
4. [Object Storage Basics (S3)](#4-object-storage-basics-s3)
5. [IAM Users, Groups & Policies](#5-iam-users-groups--policies)
6. [Virtual Private Cloud (VPC) Basics](#6-virtual-private-cloud-vpc-basics)
7. [Security Groups & Network ACLs](#7-security-groups--network-acls)
8. [Cloud Monitoring Basics (CloudWatch)](#8-cloud-monitoring-basics-cloudwatch)
9. [Cost Explorer & Billing Alerts](#9-cost-explorer--billing-alerts)
10. [Resource Tagging & Organization](#10-resource-tagging--organization)

---

## 1. Cloud CLI Setup & Configuration

### Objective
Install and configure cloud CLI tools for AWS (primary) with Azure/GCP equivalents shown.

### Key Files

| Tool | Purpose |
|------|---------|
| `aws configure` | Set up AWS credentials |
| `~/.aws/credentials` | Stored access keys |
| `~/.aws/config` | Region and output preferences |

### Tasks

**1.1** Install the AWS CLI:
```bash
# Install AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Verify installation
aws --version
```

**1.2** Configure credentials:
```bash
aws configure
# AWS Access Key ID: <your-key>
# AWS Secret Access Key: <your-secret>
# Default region name: us-east-1
# Default output format: json
```

**1.3** Verify your identity:
```bash
aws sts get-caller-identity
```
Expected output:
```json
{
    "UserId": "AIDAEXAMPLE",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/your-username"
}
```

**1.4** Set up named profiles:
```bash
aws configure --profile dev
aws configure --profile staging

# Use a specific profile
aws s3 ls --profile dev
```

**1.5** Explore CLI auto-complete:
```bash
complete -C aws_completer aws
aws ec2 describe-<TAB>
```

### Cross-Cloud Reference

| Action | AWS | Azure | GCP |
|--------|-----|-------|-----|
| Install CLI | `aws install` | `az install` | `gcloud install` |
| Configure | `aws configure` | `az login` | `gcloud init` |
| Check identity | `aws sts get-caller-identity` | `az account show` | `gcloud auth list` |

### Verification
- `aws sts get-caller-identity` returns your account info
- You have at least one named profile configured

---

## 2. Exploring Cloud Regions & Availability Zones

### Objective
Understand cloud geography and how to list available regions and AZs.

### Tasks

**2.1** List all available regions:
```bash
aws ec2 describe-regions --output table
```

**2.2** List availability zones in your region:
```bash
aws ec2 describe-availability-zones --region us-east-1 --output table
```

**2.3** Understand the hierarchy:
```
  AWS Global Infrastructure:
  
  ┌─── Region: us-east-1 (N. Virginia) ──────────────┐
  │                                                    │
  │  ┌── AZ: us-east-1a ──┐  ┌── AZ: us-east-1b ──┐ │
  │  │  Data Center(s)     │  │  Data Center(s)     │ │
  │  └─────────────────────┘  └─────────────────────┘ │
  │  ┌── AZ: us-east-1c ──┐  ┌── AZ: us-east-1d ──┐ │
  │  │  Data Center(s)     │  │  Data Center(s)     │ │
  │  └─────────────────────┘  └─────────────────────┘ │
  └────────────────────────────────────────────────────┘
```

**2.4** Check service availability in a region:
```bash
# Check if a specific instance type is available
aws ec2 describe-instance-type-offerings --location-type availability-zone \
  --filters Name=instance-type,Values=t3.micro --region us-east-1 --output table
```

### Verification
- You can list regions and AZs from the CLI
- You understand that AZs are physically separate data centers within a region

---

## 3. Launch & Manage a Virtual Machine

### Objective
Launch an EC2 instance, connect to it, and manage its lifecycle.

### Tasks

**3.1** Find the latest Amazon Linux 2023 AMI:
```bash
AMI_ID=$(aws ec2 describe-images \
  --owners amazon \
  --filters "Name=name,Values=al2023-ami-2023*-x86_64" \
  --query 'sort_by(Images, &CreationDate)[-1].ImageId' \
  --output text)
echo "AMI: $AMI_ID"
```

**3.2** Create a key pair:
```bash
aws ec2 create-key-pair --key-name devops-lab-key \
  --query 'KeyMaterial' --output text > ~/.ssh/devops-lab-key.pem
chmod 400 ~/.ssh/devops-lab-key.pem
```

**3.3** Launch an instance:
```bash
INSTANCE_ID=$(aws ec2 run-instances \
  --image-id $AMI_ID \
  --instance-type t3.micro \
  --key-name devops-lab-key \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=devops-lab}]' \
  --query 'Instances[0].InstanceId' \
  --output text)
echo "Instance: $INSTANCE_ID"
```

**3.4** Check instance status:
```bash
aws ec2 describe-instances --instance-ids $INSTANCE_ID \
  --query 'Reservations[0].Instances[0].{State:State.Name,PublicIP:PublicIpAddress,PrivateIP:PrivateIpAddress}' \
  --output table
```

**3.5** Connect via SSH:
```bash
PUBLIC_IP=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID \
  --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)
ssh -i ~/.ssh/devops-lab-key.pem ec2-user@$PUBLIC_IP
```

**3.6** Stop and start the instance:
```bash
aws ec2 stop-instances --instance-ids $INSTANCE_ID
aws ec2 start-instances --instance-ids $INSTANCE_ID
```

**3.7** Terminate (delete) the instance:
```bash
aws ec2 terminate-instances --instance-ids $INSTANCE_ID
```

### Verification
- You can launch, connect, stop, start, and terminate an EC2 instance
- You understand the instance lifecycle: pending → running → stopping → stopped → terminated

---

## 4. Object Storage Basics (S3)

### Objective
Create and manage S3 buckets, upload/download objects, and set permissions.

### Tasks

**4.1** Create an S3 bucket:
```bash
BUCKET_NAME="devops-lab-$(date +%s)"
aws s3 mb s3://$BUCKET_NAME --region us-east-1
```

**4.2** Upload files:
```bash
echo "Hello from DevOps Lab!" > /tmp/test.txt
aws s3 cp /tmp/test.txt s3://$BUCKET_NAME/test.txt
```

**4.3** List bucket contents:
```bash
aws s3 ls s3://$BUCKET_NAME/
```

**4.4** Download a file:
```bash
aws s3 cp s3://$BUCKET_NAME/test.txt /tmp/downloaded.txt
cat /tmp/downloaded.txt
```

**4.5** Sync a directory:
```bash
mkdir -p /tmp/sync-test
echo "File 1" > /tmp/sync-test/file1.txt
echo "File 2" > /tmp/sync-test/file2.txt
aws s3 sync /tmp/sync-test s3://$BUCKET_NAME/sync/
```

**4.6** Enable versioning:
```bash
aws s3api put-bucket-versioning --bucket $BUCKET_NAME \
  --versioning-configuration Status=Enabled
```

**4.7** Check bucket size:
```bash
aws s3 ls s3://$BUCKET_NAME --recursive --summarize
```

**4.8** Clean up:
```bash
aws s3 rb s3://$BUCKET_NAME --force
```

### Verification
- You can create buckets, upload/download objects, and sync directories
- You understand S3 naming, versioning, and bucket operations

---

## 5. IAM Users, Groups & Policies

### Objective
Create and manage IAM identities and understand the principle of least privilege.

### Tasks

**5.1** Create an IAM user:
```bash
aws iam create-user --user-name dev-user-1
```

**5.2** Create an IAM group and add the user:
```bash
aws iam create-group --group-name developers
aws iam add-user-to-group --group-name developers --user-name dev-user-1
```

**5.3** Attach a managed policy to the group:
```bash
# Read-only access to S3
aws iam attach-group-policy --group-name developers \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
```

**5.4** Create a custom policy:
```bash
cat << 'EOF' > /tmp/custom-policy.json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::devops-lab-*",
                "arn:aws:s3:::devops-lab-*/*"
            ]
        }
    ]
}
EOF

aws iam create-policy --policy-name DevOpsLabS3Access \
  --policy-document file:///tmp/custom-policy.json
```

**5.5** List user permissions:
```bash
aws iam list-attached-group-policies --group-name developers
aws iam list-groups-for-user --user-name dev-user-1
```

**5.6** Clean up:
```bash
aws iam remove-user-from-group --group-name developers --user-name dev-user-1
aws iam detach-group-policy --group-name developers --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
aws iam delete-group --group-name developers
aws iam delete-user --user-name dev-user-1
```

### Verification
- You can create users, groups, and policies
- You understand the IAM hierarchy: Users belong to Groups, Policies attach to Groups
- You follow the principle of least privilege

---

## 6. Virtual Private Cloud (VPC) Basics

### Objective
Create a basic VPC with public and private subnets.

### Tasks

**6.1** Create a VPC:
```bash
VPC_ID=$(aws ec2 create-vpc --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=devops-lab-vpc}]' \
  --query 'Vpc.VpcId' --output text)
echo "VPC: $VPC_ID"
```

**6.2** Create a public subnet:
```bash
PUB_SUBNET=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.1.0/24 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=public-subnet}]' \
  --query 'Subnet.SubnetId' --output text)
echo "Public Subnet: $PUB_SUBNET"
```

**6.3** Create a private subnet:
```bash
PRIV_SUBNET=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.2.0/24 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=private-subnet}]' \
  --query 'Subnet.SubnetId' --output text)
echo "Private Subnet: $PRIV_SUBNET"
```

**6.4** Create and attach an Internet Gateway:
```bash
IGW_ID=$(aws ec2 create-internet-gateway --query 'InternetGateway.InternetGatewayId' --output text)
aws ec2 attach-internet-gateway --internet-gateway-id $IGW_ID --vpc-id $VPC_ID
```

**6.5** Create a route table for the public subnet:
```bash
RT_ID=$(aws ec2 create-route-table --vpc-id $VPC_ID --query 'RouteTable.RouteTableId' --output text)
aws ec2 create-route --route-table-id $RT_ID --destination-cidr-block 0.0.0.0/0 --gateway-id $IGW_ID
aws ec2 associate-route-table --route-table-id $RT_ID --subnet-id $PUB_SUBNET
```

**6.6** Describe your VPC:
```bash
aws ec2 describe-vpcs --vpc-ids $VPC_ID --output table
aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --output table
```

### Verification
- VPC exists with 10.0.0.0/16 CIDR
- Public subnet has a route to the Internet Gateway
- Private subnet has no route to the internet

---

## 7. Security Groups & Network ACLs

### Objective
Understand and configure Security Groups and NACLs.

### Key Concepts
```
  Security Groups vs NACLs:
  
  ┌─────────────────────┬────────────────────────────────┐
  │   Security Groups    │   Network ACLs                │
  ├─────────────────────┼────────────────────────────────┤
  │ Instance-level       │ Subnet-level                   │
  │ Stateful             │ Stateless                      │
  │ Allow rules only     │ Allow AND Deny rules           │
  │ All rules evaluated  │ Rules evaluated in order       │
  │ Must be assigned     │ Auto-applied to subnet         │
  └─────────────────────┴────────────────────────────────┘
```

### Tasks

**7.1** Create a Security Group for a web server:
```bash
WEB_SG=$(aws ec2 create-security-group --group-name web-sg \
  --description "Web Server SG" --vpc-id $VPC_ID \
  --query 'GroupId' --output text)

# Allow SSH from your IP
MY_IP=$(curl -s https://checkip.amazonaws.com)
aws ec2 authorize-security-group-ingress --group-id $WEB_SG \
  --protocol tcp --port 22 --cidr $MY_IP/32

# Allow HTTP from anywhere
aws ec2 authorize-security-group-ingress --group-id $WEB_SG \
  --protocol tcp --port 80 --cidr 0.0.0.0/0

# Allow HTTPS from anywhere
aws ec2 authorize-security-group-ingress --group-id $WEB_SG \
  --protocol tcp --port 443 --cidr 0.0.0.0/0
```

**7.2** View Security Group rules:
```bash
aws ec2 describe-security-groups --group-ids $WEB_SG --output table
```

**7.3** Create a NACL with explicit allow/deny:
```bash
NACL_ID=$(aws ec2 create-network-acl --vpc-id $VPC_ID --query 'NetworkAcl.NetworkAclId' --output text)

# Allow inbound HTTP (rule 100)
aws ec2 create-network-acl-entry --network-acl-id $NACL_ID \
  --rule-number 100 --protocol tcp --port-range From=80,To=80 \
  --cidr-block 0.0.0.0/0 --rule-action allow --ingress

# Allow inbound SSH (rule 110)
aws ec2 create-network-acl-entry --network-acl-id $NACL_ID \
  --rule-number 110 --protocol tcp --port-range From=22,To=22 \
  --cidr-block $MY_IP/32 --rule-action allow --ingress

# Allow outbound ephemeral ports (rule 100)
aws ec2 create-network-acl-entry --network-acl-id $NACL_ID \
  --rule-number 100 --protocol tcp --port-range From=1024,To=65535 \
  --cidr-block 0.0.0.0/0 --rule-action allow --egress
```

### Verification
- Security Group allows SSH, HTTP, HTTPS
- NACL has explicit allow rules with rule numbers
- You understand stateful (SG) vs stateless (NACL) filtering

---

## 8. Cloud Monitoring Basics (CloudWatch)

### Objective
View metrics, create alarms, and understand basic cloud monitoring.

### Tasks

**8.1** List available metrics for EC2:
```bash
aws cloudwatch list-metrics --namespace AWS/EC2 --output table | head -30
```

**8.2** Get CPU utilization for an instance:
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=$INSTANCE_ID \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average
```

**8.3** Create a CPU alarm:
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "HighCPU-devops-lab" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --dimensions Name=InstanceId,Value=$INSTANCE_ID
```

**8.4** List active alarms:
```bash
aws cloudwatch describe-alarms --output table
```

**8.5** Delete the alarm:
```bash
aws cloudwatch delete-alarms --alarm-names "HighCPU-devops-lab"
```

### Verification
- You can view CloudWatch metrics for EC2
- You can create and manage alarms
- You understand metrics, periods, and thresholds

---

## 9. Cost Explorer & Billing Alerts

### Objective
Understand cloud costs and set up billing alerts to avoid surprises.

### Tasks

**9.1** Check current month's estimated charges:
```bash
aws ce get-cost-and-usage \
  --time-period Start=$(date -u +%Y-%m-01),End=$(date -u +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics "BlendedCost"
```

**9.2** Break down costs by service:
```bash
aws ce get-cost-and-usage \
  --time-period Start=$(date -u +%Y-%m-01),End=$(date -u +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics "BlendedCost" \
  --group-by Type=DIMENSION,Key=SERVICE
```

**9.3** Create a budget alarm (via AWS Budgets):
```bash
cat << 'EOF' > /tmp/budget.json
{
    "BudgetName": "DevOpsLabBudget",
    "BudgetLimit": {
        "Amount": "10",
        "Unit": "USD"
    },
    "BudgetType": "COST",
    "TimeUnit": "MONTHLY"
}
EOF

aws budgets create-budget --account-id $(aws sts get-caller-identity --query Account --output text) \
  --budget file:///tmp/budget.json
```

> **⚠️ Gotcha:** Always set billing alerts on new accounts. A misconfigured resource can rack up hundreds of dollars overnight. The free tier has limits!

### Verification
- You can view current costs and cost breakdown by service
- You have a billing budget alert set up

---

## 10. Resource Tagging & Organization

### Objective
Implement a tagging strategy to organize and track cloud resources.

### Tasks

**10.1** Tag an existing resource:
```bash
aws ec2 create-tags --resources $INSTANCE_ID --tags \
  Key=Environment,Value=dev \
  Key=Project,Value=devops-lab \
  Key=Owner,Value=trainee \
  Key=CostCenter,Value=training
```

**10.2** List resources by tag:
```bash
aws ec2 describe-instances --filters "Name=tag:Environment,Values=dev" \
  --query 'Reservations[].Instances[].{ID:InstanceId,Name:Tags[?Key==`Name`]|[0].Value,Env:Tags[?Key==`Environment`]|[0].Value}' \
  --output table
```

**10.3** Find untagged resources:
```bash
aws ec2 describe-instances \
  --query 'Reservations[].Instances[?!not_null(Tags[?Key==`Environment`].Value | [0])].[InstanceId]' \
  --output text
```

**10.4** Recommended tagging strategy:

| Tag Key | Example Value | Purpose |
|---------|---------------|---------|
| `Name` | `web-prod-01` | Human-readable identifier |
| `Environment` | `dev/staging/prod` | Deployment stage |
| `Project` | `ecommerce-app` | Business project |
| `Owner` | `team-backend` | Responsible team |
| `CostCenter` | `CC-1234` | Cost allocation |
| `ManagedBy` | `terraform` | IaC tool tracking |
| `ExpiryDate` | `2024-06-30` | Auto-cleanup eligibility |

### Verification
- Resources have at least 4 tags (Name, Environment, Project, Owner)
- You can query resources by tag
- You understand the importance of tagging for cost allocation

---

> **Level 1 Complete!** You now have foundational cloud skills.  
> **Next:** [Level 2 — Intermediate Cloud Tasks](level_2.md)

[🏠 Home](../../README.md) · [Tasks](../README.md)
