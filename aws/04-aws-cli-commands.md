[🏠 Home](../README.md) · [☁️ AWS](README.md)

# ⌨️ AWS CLI Commands — Practical Reference

> The **AWS CLI v2** commands you'll actually use, grouped by service, with explanations for
> beginners and copy-paste recipes for common tasks. Every command assumes AWS CLI **v2**.
>
> Concepts are explained in [01 — Terms](01-aws-terms.md), services in [02 — Services](02-aws-services.md).

> ⚠️ **Safety first:** many commands below **create, change or delete real resources and cost
> money**. Try them in a sandbox account with a budget alert. Read-only commands (`list-*`,
> `describe-*`, `get-*`) are safe to explore with.

---

## 📑 Table of Contents

1. [Install & verify](#1--install--verify)
2. [Authentication, profiles & SSO](#2--authentication-profiles--sso)
3. [CLI essentials: output, `--query`, filters, pagination, waiters](#3--cli-essentials)
4. [IAM & STS](#4--iam--sts)
5. [EC2, AMIs, Security Groups & EBS](#5--ec2-amis-security-groups--ebs)
6. [VPC Networking](#6--vpc-networking)
7. [Systems Manager (SSM)](#7--systems-manager-ssm)
8. [S3](#8--s3)
9. [Lambda](#9--lambda)
10. [ECR, ECS & EKS](#10--ecr-ecs--eks)
11. [RDS, Aurora & DynamoDB](#11--rds-aurora--dynamodb)
12. [CloudFormation (and CDK/SAM CLIs)](#12--cloudformation-and-cdksam-clis)
13. [CloudWatch Metrics, Alarms & Logs](#13--cloudwatch-metrics-alarms--logs)
14. [Secrets Manager, Parameter Store & KMS](#14--secrets-manager-parameter-store--kms)
15. [Load Balancers & Auto Scaling](#15--load-balancers--auto-scaling)
16. [Route 53, ACM & CloudFront](#16--route-53-acm--cloudfront)
17. [SQS, SNS, EventBridge & Step Functions](#17--sqs-sns-eventbridge--step-functions)
18. [Security & Governance: CloudTrail, Organizations, GuardDuty, Config](#18--security--governance)
19. [Cost, Billing & Service Quotas](#19--cost-billing--service-quotas)
20. [Bedrock (Generative AI)](#20--bedrock-generative-ai)
21. [Handy recipes & one-liners](#21--handy-recipes--one-liners)
22. [Windows PowerShell notes & troubleshooting](#22--windows-powershell-notes--troubleshooting)

---

# 1 — Install & Verify

```powershell
# Windows (PowerShell, admin) — official MSI installer
msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi
# or with winget
winget install -e --id Amazon.AWSCLI
```

```bash
# Linux (x86_64) / WSL2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o awscliv2.zip
unzip awscliv2.zip && sudo ./aws/install
# macOS
brew install awscli          # or the official .pkg installer
```

```bash
aws --version                # aws-cli/2.x.x ...
aws help                     # top-level help;  aws s3 help / aws ec2 run-instances help
aws --cli-auto-prompt        # interactive prompt that autocompletes commands and parameters
```

> 💡 **Session Manager plugin** (needed for `aws ssm start-session` and `aws ecs execute-command`)
> is a separate install. See the Systems Manager docs.

---

# 2 — Authentication, Profiles & SSO

### Recommended: IAM Identity Center (SSO) — short-lived credentials

```bash
aws configure sso                       # one-time wizard: SSO start URL, region, account, role → saves a profile
aws sso login --profile dev-admin       # opens browser; caches temporary credentials
aws sts get-caller-identity --profile dev-admin     # "who am I?" — ALWAYS check before changing things
aws sso logout
```

### Access keys (only for legacy/personal sandbox use)

```bash
aws configure                           # prompts for Access Key ID, Secret, default region, output format
aws configure --profile sandbox         # a named profile
```

### Profiles, config and environment variables

```bash
aws configure list                      # what credentials/region are in effect, and where they come from
aws configure list-profiles
aws configure get region --profile prod
aws configure set region ap-south-1 --profile dev-admin

export AWS_PROFILE=dev-admin            # PowerShell: $env:AWS_PROFILE = "dev-admin"
export AWS_REGION=ap-south-1            # PowerShell: $env:AWS_REGION  = "ap-south-1"
```

Files (`~` = `C:\Users\<you>` on Windows):

```ini
# ~/.aws/config
[profile dev-admin]
sso_session = acme
sso_account_id = 111111111111
sso_role_name = AdministratorAccess
region = ap-south-1
output = json

[profile prod-readonly]
sso_session = acme
sso_account_id = 222222222222
sso_role_name = ReadOnlyAccess
region = ap-south-1

[profile prod-deploy]                   # assume a role using another profile's credentials
role_arn = arn:aws:iam::222222222222:role/deploy
source_profile = dev-admin

[sso-session acme]
sso_start_url = https://acme.awsapps.com/start
sso_region = ap-south-1
sso_registration_scopes = sso:account:access
```

**Credential lookup order (first match wins):** command-line options → environment variables
(`AWS_ACCESS_KEY_ID`, `AWS_PROFILE`…) → SSO/credentials/config files → container credentials
(ECS task role) → EC2 instance profile (IMDS).

> ⚠️ **Never commit `~/.aws/credentials`** or paste access keys anywhere. If a key leaks:
> deactivate it immediately (`aws iam update-access-key --status Inactive`), then investigate CloudTrail.

---

# 3 — CLI Essentials

### Command shape

```
aws <service> <operation> [--parameters] [--global-options]
aws ec2       describe-instances --instance-ids i-0abc --region ap-south-1 --output table
```

### Global options you'll use constantly

| Option | Purpose |
|--------|---------|
| `--profile NAME` | Which credentials/account to use |
| `--region REGION` | Override the region |
| `--output json\|yaml\|text\|table` | Output format (`text` is best for shell scripts) |
| `--query 'JMESPath'` | Filter/reshape output **client-side** |
| `--no-cli-pager` | Don't open output in a pager (or set `AWS_PAGER=""`) |
| `--dry-run` | (EC2 only) check permissions without making changes |
| `--debug` | Full request/response debug logs |
| `--cli-input-json file://x.json` / `--generate-cli-skeleton` | Drive complex commands from JSON files |
| `--max-items`, `--page-size`, `--starting-token` | Pagination control |

### `--query` (JMESPath) cheat sheet

```bash
# Pick fields from a list → table
aws ec2 describe-instances \
  --query 'Reservations[].Instances[].{ID:InstanceId,Type:InstanceType,State:State.Name,Name:Tags[?Key==`Name`]|[0].Value}' \
  --output table

# Filter a list client-side
aws ec2 describe-volumes --query 'Volumes[?State==`available`].[VolumeId,Size]' --output text

# First item / count
aws s3api list-buckets --query 'Buckets[0].Name' --output text
aws lambda list-functions --query 'length(Functions)'

# Sort by a field, take last 5
aws ec2 describe-snapshots --owner-ids self --query 'reverse(sort_by(Snapshots,&StartTime))[:5].[SnapshotId,StartTime]' --output table
```

### `--filters` (server-side, for EC2-style APIs) vs `--query` (client-side)

```bash
aws ec2 describe-instances \
  --filters "Name=tag:Environment,Values=prod" "Name=instance-state-name,Values=running" \
  --query 'Reservations[].Instances[].InstanceId' --output text
```

> 💡 Use `--filters` to reduce what AWS returns, then `--query` to shape it.

### Waiters: block until a resource reaches a state

```bash
aws ec2 wait instance-running --instance-ids i-0abc123
aws cloudformation wait stack-create-complete --stack-name my-stack
aws ecs wait services-stable --cluster prod --services orders-api
aws rds wait db-instance-available --db-instance-identifier orders-db
```

### Files as input

```bash
--policy-document file://policy.json       # text file
--zip-file fileb://function.zip            # binary file (fileb://)
```

### Aliases (`~/.aws/cli/alias`)

```ini
[toplevel]
whoami = sts get-caller-identity
running = ec2 describe-instances --filters Name=instance-state-name,Values=running --query "Reservations[].Instances[].[InstanceId,InstanceType,Tags[?Key=='Name']|[0].Value]" --output table
```

Then run `aws whoami` or `aws running`.

---

# 4 — IAM & STS

```bash
# Identity
aws sts get-caller-identity                                  # account, user/role ARN — use before every risky change

# Assume a role manually (returns temporary credentials)
aws sts assume-role --role-arn arn:aws:iam::222222222222:role/ReadOnly --role-session-name me

# Users, groups, roles, policies (read)
aws iam list-users --query 'Users[].[UserName,CreateDate]' --output table
aws iam list-roles --query 'Roles[?contains(RoleName,`deploy`)].RoleName'
aws iam list-attached-role-policies --role-name app-role
aws iam get-role --role-name app-role --query 'Role.AssumeRolePolicyDocument'
aws iam list-access-keys --user-name legacy-user
aws iam get-access-key-last-used --access-key-id AKIA...

# Create a role for EC2 with a trust policy, attach a managed policy
aws iam create-role --role-name app-ec2-role --assume-role-policy-document file://trust-ec2.json
aws iam attach-role-policy --role-name app-ec2-role --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore
aws iam create-instance-profile --instance-profile-name app-ec2-profile
aws iam add-role-to-instance-profile --instance-profile-name app-ec2-profile --role-name app-ec2-role

# Customer-managed policy
aws iam create-policy --policy-name read-reports --policy-document file://read-reports.json

# Test what a principal can do (policy simulator)
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::111111111111:role/app-ec2-role \
  --action-names s3:GetObject s3:DeleteObject \
  --resource-arns arn:aws:s3:::acme-reports/*

# Deactivate a leaked key immediately
aws iam update-access-key --user-name legacy-user --access-key-id AKIA... --status Inactive

# Credential report (security audit)
aws iam generate-credential-report && aws iam get-credential-report --query Content --output text | base64 -d > cred-report.csv
```

`trust-ec2.json`:

```json
{
  "Version": "2012-10-17",
  "Statement": [{ "Effect": "Allow", "Principal": { "Service": "ec2.amazonaws.com" }, "Action": "sts:AssumeRole" }]
}
```

---

# 5 — EC2, AMIs, Security Groups & EBS

```bash
# Find the latest Amazon Linux 2023 AMI via public SSM parameter (no hard-coded AMI IDs!)
AMI=$(aws ssm get-parameter --name /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 \
      --query Parameter.Value --output text)

# Launch an instance (private subnet, SSM role, IMDSv2 required, encrypted gp3 root, tags)
aws ec2 run-instances \
  --image-id "$AMI" --instance-type t3.micro \
  --subnet-id subnet-0abc --security-group-ids sg-0abc \
  --iam-instance-profile Name=app-ec2-profile \
  --metadata-options HttpTokens=required,HttpEndpoint=enabled \
  --block-device-mappings 'DeviceName=/dev/xvda,Ebs={VolumeSize=20,VolumeType=gp3,Encrypted=true}' \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=web-1},{Key=Environment,Value=dev}]' \
  --query 'Instances[0].InstanceId' --output text

# Permission check without launching
aws ec2 run-instances --dry-run --image-id "$AMI" --instance-type t3.micro

# List / inspect
aws ec2 describe-instances --instance-ids i-0abc --query 'Reservations[0].Instances[0].[State.Name,PrivateIpAddress,PublicIpAddress]'
aws ec2 describe-instance-status --instance-ids i-0abc        # system/instance status checks

# Lifecycle
aws ec2 stop-instances --instance-ids i-0abc
aws ec2 start-instances --instance-ids i-0abc
aws ec2 reboot-instances --instance-ids i-0abc
aws ec2 terminate-instances --instance-ids i-0abc               # ⚠️ permanent (unless termination protection)
aws ec2 modify-instance-attribute --instance-id i-0abc --disable-api-termination   # turn ON termination protection

# Change instance type (must be stopped)
aws ec2 modify-instance-attribute --instance-id i-0abc --instance-type Value=t3.small

# Console output (debug boot problems)
aws ec2 get-console-output --instance-id i-0abc --latest --output text

# Security groups
aws ec2 create-security-group --group-name web-sg --description "Web tier" --vpc-id vpc-0abc
aws ec2 authorize-security-group-ingress --group-id sg-0web --protocol tcp --port 443 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id sg-0app --protocol tcp --port 8080 --source-group sg-0web   # SG referencing
aws ec2 revoke-security-group-ingress --group-id sg-0web --protocol tcp --port 22 --cidr 0.0.0.0/0
aws ec2 describe-security-groups --group-ids sg-0web --query 'SecurityGroups[0].IpPermissions'

# Key pairs (prefer Session Manager instead of SSH)
aws ec2 create-key-pair --key-name dev-key --key-type ed25519 --query KeyMaterial --output text > dev-key.pem

# AMIs from an instance
aws ec2 create-image --instance-id i-0abc --name "web-golden-$(date +%F)" --no-reboot
aws ec2 describe-images --owners self --query 'Images[].[ImageId,Name,CreationDate]' --output table
aws ec2 deregister-image --image-id ami-0old

# EBS volumes & snapshots
aws ec2 create-volume --availability-zone ap-south-1a --size 50 --volume-type gp3 --encrypted
aws ec2 attach-volume --volume-id vol-0abc --instance-id i-0abc --device /dev/sdf
aws ec2 modify-volume --volume-id vol-0abc --size 100              # grow online (then extend the filesystem in the OS)
aws ec2 create-snapshot --volume-id vol-0abc --description "pre-upgrade backup"
aws ec2 copy-snapshot --source-region ap-south-1 --source-snapshot-id snap-0abc --region ap-southeast-1
aws ec2 enable-ebs-encryption-by-default                          # account/region-level default encryption

# Elastic IPs
aws ec2 allocate-address --domain vpc
aws ec2 associate-address --instance-id i-0abc --allocation-id eipalloc-0abc
aws ec2 release-address --allocation-id eipalloc-0abc
```

---

# 6 — VPC Networking

```bash
# Build a minimal VPC with one public subnet
VPC=$(aws ec2 create-vpc --cidr-block 10.20.0.0/16 --query Vpc.VpcId --output text)
aws ec2 modify-vpc-attribute --vpc-id $VPC --enable-dns-hostnames
SUBNET=$(aws ec2 create-subnet --vpc-id $VPC --cidr-block 10.20.1.0/24 --availability-zone ap-south-1a --query Subnet.SubnetId --output text)
IGW=$(aws ec2 create-internet-gateway --query InternetGateway.InternetGatewayId --output text)
aws ec2 attach-internet-gateway --internet-gateway-id $IGW --vpc-id $VPC
RT=$(aws ec2 create-route-table --vpc-id $VPC --query RouteTable.RouteTableId --output text)
aws ec2 create-route --route-table-id $RT --destination-cidr-block 0.0.0.0/0 --gateway-id $IGW
aws ec2 associate-route-table --route-table-id $RT --subnet-id $SUBNET

# NAT Gateway for private subnets (⚠️ hourly + per-GB cost)
EIP=$(aws ec2 allocate-address --domain vpc --query AllocationId --output text)
aws ec2 create-nat-gateway --subnet-id $SUBNET --allocation-id $EIP

# Gateway endpoint for S3 (free) on a private route table
aws ec2 create-vpc-endpoint --vpc-id $VPC --service-name com.amazonaws.ap-south-1.s3 \
  --vpc-endpoint-type Gateway --route-table-ids rtb-0private

# Interface endpoint (e.g. Secrets Manager) with private DNS
aws ec2 create-vpc-endpoint --vpc-id $VPC --vpc-endpoint-type Interface \
  --service-name com.amazonaws.ap-south-1.secretsmanager \
  --subnet-ids subnet-0a subnet-0b --security-group-ids sg-0endpoints --private-dns-enabled

# Inspect
aws ec2 describe-vpcs --query 'Vpcs[].[VpcId,CidrBlock,Tags[?Key==`Name`]|[0].Value]' --output table
aws ec2 describe-subnets --filters Name=vpc-id,Values=$VPC --query 'Subnets[].[SubnetId,AvailabilityZone,CidrBlock,AvailableIpAddressCount]' --output table
aws ec2 describe-route-tables --filters Name=vpc-id,Values=$VPC
aws ec2 describe-nat-gateways --query 'NatGateways[].[NatGatewayId,State,SubnetId]'

# VPC Flow Logs to CloudWatch Logs
aws ec2 create-flow-logs --resource-type VPC --resource-ids $VPC --traffic-type ALL \
  --log-destination-type cloud-watch-logs --log-group-name /vpc/flow-logs \
  --deliver-logs-permission-arn arn:aws:iam::111111111111:role/flow-logs-role

# Peering
aws ec2 create-vpc-peering-connection --vpc-id vpc-0a --peer-vpc-id vpc-0b
aws ec2 accept-vpc-peering-connection --vpc-peering-connection-id pcx-0abc
```

> 💡 For real environments, build VPCs with **IaC** (Terraform/CloudFormation). CLI-built networks are
> great for learning but hard to reproduce.

---

# 7 — Systems Manager (SSM)

```bash
# Shell into an instance with NO SSH, NO open ports (needs the Session Manager plugin)
aws ssm start-session --target i-0abc

# Port-forward to a private RDS database through an instance
aws ssm start-session --target i-0abc \
  --document-name AWS-StartPortForwardingSessionToRemoteHost \
  --parameters '{"host":["orders-db.abc.ap-south-1.rds.amazonaws.com"],"portNumber":["5432"],"localPortNumber":["15432"]}'

# Which instances are managed by SSM?
aws ssm describe-instance-information --query 'InstanceInformationList[].[InstanceId,PingStatus,PlatformName]' --output table

# Run a command on many instances by tag
aws ssm send-command --document-name AWS-RunShellScript \
  --targets Key=tag:Environment,Values=dev \
  --parameters 'commands=["uptime","df -h"]' \
  --comment "health check" --query Command.CommandId --output text
aws ssm list-command-invocations --command-id <id> --details --query 'CommandInvocations[].[InstanceId,Status]'

# Patch now (or schedule with maintenance windows)
aws ssm send-command --document-name AWS-RunPatchBaseline --targets Key=tag:PatchGroup,Values=web --parameters Operation=Install
```

---

# 8 — S3

### High-level `aws s3` commands (file-like)

```bash
aws s3 ls                                          # list buckets
aws s3 ls s3://acme-reports/2026/ --recursive --human-readable --summarize
aws s3 mb s3://acme-reports-unique-name --region ap-south-1     # make bucket
aws s3 cp report.csv s3://acme-reports/2026/oct/report.csv
aws s3 cp s3://acme-reports/2026/oct/report.csv .
aws s3 cp ./dist s3://acme-web/ --recursive
aws s3 sync ./dist s3://acme-web --delete --exclude "*.map"       # mirror folder (⚠️ --delete removes extra remote files)
aws s3 sync s3://acme-web ./backup                                # download everything
aws s3 mv s3://acme-reports/tmp/a.csv s3://acme-reports/archive/a.csv
aws s3 rm s3://acme-reports/tmp/ --recursive                      # ⚠️ deletes all objects under prefix
aws s3 rb s3://old-bucket --force                                 # ⚠️ deletes bucket and all objects
aws s3 presign s3://acme-reports/2026/oct/report.csv --expires-in 3600   # temporary download link

# Upload with storage class / server-side encryption / cache headers
aws s3 cp backup.tar.gz s3://acme-backups/ --storage-class GLACIER_IR
aws s3 cp secret.pdf s3://acme-docs/ --sse aws:kms --sse-kms-key-id alias/docs
aws s3 cp ./dist/assets s3://acme-web/assets --recursive --cache-control "public,max-age=31536000,immutable"
```

### Low-level `aws s3api` (bucket configuration)

```bash
# Security baseline for a bucket
aws s3api put-public-access-block --bucket acme-reports \
  --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
aws s3api put-bucket-versioning --bucket acme-reports --versioning-configuration Status=Enabled
aws s3api put-bucket-encryption --bucket acme-reports --server-side-encryption-configuration \
  '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"aws:kms","KMSMasterKeyID":"alias/reports"},"BucketKeyEnabled":true}]}'

# Account-wide Block Public Access (s3control)
aws s3control put-public-access-block --account-id 111111111111 \
  --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

# Policies & lifecycle
aws s3api get-bucket-policy --bucket acme-reports --query Policy --output text
aws s3api put-bucket-policy --bucket acme-reports --policy file://bucket-policy.json
aws s3api put-bucket-lifecycle-configuration --bucket acme-logs --lifecycle-configuration file://lifecycle.json

# Object versions (recover deleted/overwritten files)
aws s3api list-object-versions --bucket acme-reports --prefix 2026/oct/report.csv
aws s3api get-object --bucket acme-reports --key 2026/oct/report.csv --version-id <versionId> restored.csv

# Object metadata & size of a bucket
aws s3api head-object --bucket acme-reports --key 2026/oct/report.csv
aws s3 ls s3://acme-reports --recursive --summarize | tail -2
```

`lifecycle.json` (logs → IA → Glacier → delete; clean up failed multipart uploads):

```json
{
  "Rules": [{
    "ID": "logs-tiering",
    "Status": "Enabled",
    "Filter": { "Prefix": "logs/" },
    "Transitions": [
      { "Days": 30, "StorageClass": "STANDARD_IA" },
      { "Days": 90, "StorageClass": "GLACIER" }
    ],
    "Expiration": { "Days": 400 },
    "AbortIncompleteMultipartUpload": { "DaysAfterInitiation": 7 }
  }]
}
```

---

# 9 — Lambda

```bash
aws lambda list-functions --query 'Functions[].[FunctionName,Runtime,MemorySize,Timeout]' --output table
aws lambda get-function --function-name orders-api --query 'Configuration.[Runtime,Handler,LastModified]'

# Create a function from a zip (role must trust lambda.amazonaws.com)
zip function.zip app.py
aws lambda create-function --function-name hello \
  --runtime python3.12 --handler app.handler \
  --role arn:aws:iam::111111111111:role/lambda-basic-exec \
  --zip-file fileb://function.zip --timeout 10 --memory-size 256 --architectures arm64

# Update code / configuration
aws lambda update-function-code --function-name hello --zip-file fileb://function.zip
aws lambda update-function-configuration --function-name hello \
  --environment 'Variables={LOG_LEVEL=info,TABLE=orders}' --timeout 30
aws lambda wait function-updated --function-name hello

# Invoke (synchronous) — v2 needs raw-in-base64-out for JSON payloads
aws lambda invoke --function-name hello --cli-binary-format raw-in-base64-out \
  --payload '{"name":"Asha"}' response.json && cat response.json

# Async invoke
aws lambda invoke --function-name hello --invocation-type Event --cli-binary-format raw-in-base64-out --payload '{}' /dev/null

# Logs (live tail)
aws logs tail /aws/lambda/hello --follow --since 10m

# Versions, aliases, concurrency
aws lambda publish-version --function-name hello
aws lambda create-alias --function-name hello --name live --function-version 3
aws lambda update-alias --function-name hello --name live --function-version 4 \
  --routing-config 'AdditionalVersionWeights={"3"=0.9}'        # canary: v4 (main) gets 10%, v3 (additional) keeps 90%
aws lambda put-function-concurrency --function-name hello --reserved-concurrent-executions 50

# Trigger from SQS
aws lambda create-event-source-mapping --function-name worker \
  --event-source-arn arn:aws:sqs:ap-south-1:111111111111:jobs --batch-size 10 \
  --function-response-types ReportBatchItemFailures
```

> ⚠️ In the alias example, `AdditionalVersionWeights` sends the given weight to the **additional**
> version (here 90% to v3 and 10% to v4, the alias's main version). Double-check weights before shifting traffic.

---

# 10 — ECR, ECS & EKS

### ECR (container registry)

```bash
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
REGION=ap-south-1
REGISTRY=$ACCOUNT.dkr.ecr.$REGION.amazonaws.com

aws ecr create-repository --repository-name orders-api \
  --image-scanning-configuration scanOnPush=true --image-tag-mutability IMMUTABLE
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $REGISTRY
docker build -t $REGISTRY/orders-api:1.4.2 . && docker push $REGISTRY/orders-api:1.4.2

aws ecr describe-images --repository-name orders-api --query 'reverse(sort_by(imageDetails,&imagePushedAt))[:5].[imageTags[0],imagePushedAt]' --output table
aws ecr describe-image-scan-findings --repository-name orders-api --image-id imageTag=1.4.2 --query 'imageScanFindings.findingSeverityCounts'
aws ecr put-lifecycle-policy --repository-name orders-api --lifecycle-policy-text file://ecr-lifecycle.json
aws ecr batch-delete-image --repository-name orders-api --image-ids imageTag=old-tag
```

### ECS

```bash
aws ecs list-clusters
aws ecs list-services --cluster prod
aws ecs describe-services --cluster prod --services orders-api \
  --query 'services[0].{desired:desiredCount,running:runningCount,taskDef:taskDefinition,events:events[:3].message}'

# Register a new task definition revision from JSON, then deploy it
aws ecs register-task-definition --cli-input-json file://taskdef.json
aws ecs update-service --cluster prod --service orders-api --task-definition orders-api:42
aws ecs update-service --cluster prod --service orders-api --force-new-deployment    # redeploy same revision (e.g. pull new :latest… better: use immutable tags)
aws ecs update-service --cluster prod --service orders-api --desired-count 4
aws ecs wait services-stable --cluster prod --services orders-api

# Tasks
aws ecs list-tasks --cluster prod --service-name orders-api
aws ecs describe-tasks --cluster prod --tasks <task-arn> --query 'tasks[0].[lastStatus,stoppedReason,containers[0].reason]'
aws ecs list-tasks --cluster prod --desired-status STOPPED       # why did tasks die? then describe-tasks → stoppedReason

# One-off task on Fargate (e.g. DB migration)
aws ecs run-task --cluster prod --launch-type FARGATE --task-definition migrate:7 \
  --network-configuration 'awsvpcConfiguration={subnets=[subnet-0a,subnet-0b],securityGroups=[sg-0app],assignPublicIp=DISABLED}'

# Shell into a running container (ECS Exec must be enabled on the service)
aws ecs execute-command --cluster prod --task <task-id> --container orders-api --interactive --command "/bin/sh"
```

### EKS

```bash
aws eks list-clusters
aws eks describe-cluster --name prod --query 'cluster.[version,status,endpoint]'
aws eks update-kubeconfig --name prod --region ap-south-1 --alias prod     # writes ~/.kube/config entry
kubectl get nodes

aws eks list-nodegroups --cluster-name prod
aws eks describe-nodegroup --cluster-name prod --nodegroup-name default --query 'nodegroup.[status,scalingConfig]'
aws eks list-addons --cluster-name prod

# Grant an IAM role cluster access (access entries)
aws eks create-access-entry --cluster-name prod --principal-arn arn:aws:iam::111111111111:role/ci-deploy
aws eks associate-access-policy --cluster-name prod \
  --principal-arn arn:aws:iam::111111111111:role/ci-deploy \
  --policy-arn arn:aws:eks::aws:cluster-access-policy/AmazonEKSEditPolicy \
  --access-scope type=namespace,namespaces=orders

# Upgrade planning
aws eks describe-cluster-versions --query 'clusterVersions[].[clusterVersion,status]' --output table
```

---

# 11 — RDS, Aurora & DynamoDB

### RDS / Aurora

```bash
aws rds describe-db-instances --query 'DBInstances[].[DBInstanceIdentifier,Engine,DBInstanceClass,DBInstanceStatus,Endpoint.Address,MultiAZ]' --output table
aws rds describe-db-clusters --query 'DBClusters[].[DBClusterIdentifier,Engine,Status,Endpoint,ReaderEndpoint]' --output table

# Snapshots & restore (restore creates a NEW instance)
aws rds create-db-snapshot --db-instance-identifier orders-db --db-snapshot-identifier orders-db-pre-release-2026-10-18
aws rds describe-db-snapshots --db-instance-identifier orders-db --query 'DBSnapshots[].[DBSnapshotIdentifier,SnapshotCreateTime,Status]'
aws rds restore-db-instance-to-point-in-time --source-db-instance-identifier orders-db \
  --target-db-instance-identifier orders-db-restore --restore-time 2026-10-18T09:30:00Z

# Changes
aws rds modify-db-instance --db-instance-identifier orders-db --db-instance-class db.r7g.large --apply-immediately
aws rds modify-db-instance --db-instance-identifier orders-db --deletion-protection
aws rds reboot-db-instance --db-instance-identifier orders-db --force-failover     # test Multi-AZ failover
aws rds failover-db-cluster --db-cluster-identifier orders-aurora                  # Aurora failover test

# Logs & IAM auth token
aws rds describe-db-log-files --db-instance-identifier orders-db
aws rds generate-db-auth-token --hostname orders-db.abc.ap-south-1.rds.amazonaws.com --port 5432 --username app_iam
aws rds describe-db-engine-versions --engine postgres --query 'DBEngineVersions[-5:].EngineVersion'
```

### DynamoDB

```bash
aws dynamodb list-tables
aws dynamodb describe-table --table-name orders --query 'Table.[TableStatus,ItemCount,BillingModeSummary.BillingMode,KeySchema]'

aws dynamodb create-table --table-name orders \
  --attribute-definitions AttributeName=pk,AttributeType=S AttributeName=sk,AttributeType=S \
  --key-schema AttributeName=pk,KeyType=HASH AttributeName=sk,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST

# Items (DynamoDB JSON uses type descriptors: S=string, N=number, BOOL, M=map, L=list)
aws dynamodb put-item --table-name orders --item '{"pk":{"S":"CUSTOMER#42"},"sk":{"S":"ORDER#A12"},"total":{"N":"499"}}'
aws dynamodb get-item --table-name orders --key '{"pk":{"S":"CUSTOMER#42"},"sk":{"S":"ORDER#A12"}}'
aws dynamodb query --table-name orders \
  --key-condition-expression "pk = :p AND begins_with(sk, :s)" \
  --expression-attribute-values '{":p":{"S":"CUSTOMER#42"},":s":{"S":"ORDER#"}}'
aws dynamodb update-item --table-name orders --key '{"pk":{"S":"CUSTOMER#42"},"sk":{"S":"ORDER#A12"}}' \
  --update-expression "SET #st = :s" --expression-attribute-names '{"#st":"status"}' \
  --expression-attribute-values '{":s":{"S":"SHIPPED"}}'
aws dynamodb delete-item --table-name orders --key '{"pk":{"S":"CUSTOMER#42"},"sk":{"S":"ORDER#A12"}}'
aws dynamodb scan --table-name orders --max-items 10          # ⚠️ scans read the whole table — costly on big tables

# Protection
aws dynamodb update-continuous-backups --table-name orders --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true
aws dynamodb update-table --table-name orders --deletion-protection-enabled
aws dynamodb update-time-to-live --table-name sessions --time-to-live-specification Enabled=true,AttributeName=expiresAt
```

---

# 12 — CloudFormation (and CDK/SAM CLIs)

```bash
aws cloudformation validate-template --template-body file://template.yaml

# Create or update in one command (creates a change set and executes it)
aws cloudformation deploy --template-file template.yaml --stack-name orders-network-dev \
  --parameter-overrides Environment=dev VpcCidr=10.20.0.0/16 \
  --capabilities CAPABILITY_NAMED_IAM --tags Owner=platform CostCenter=1234 \
  --no-fail-on-empty-changeset

# Preview only (review before executing)
aws cloudformation deploy --template-file template.yaml --stack-name orders-network-prod --no-execute-changeset
aws cloudformation describe-change-set --stack-name orders-network-prod --change-set-name <name> \
  --query 'Changes[].ResourceChange.[Action,LogicalResourceId,ResourceType,Replacement]' --output table

# Inspect
aws cloudformation describe-stacks --stack-name orders-network-dev --query 'Stacks[0].Outputs' --output table
aws cloudformation describe-stack-events --stack-name orders-network-dev \
  --query 'StackEvents[?contains(ResourceStatus,`FAILED`)].[LogicalResourceId,ResourceStatusReason]' --output table   # why did it fail?
aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE --query 'StackSummaries[].StackName'

# Drift & protection
aws cloudformation detect-stack-drift --stack-name orders-network-prod
aws cloudformation describe-stack-resource-drifts --stack-name orders-network-prod --stack-resource-drift-status-filters MODIFIED DELETED
aws cloudformation update-termination-protection --stack-name orders-network-prod --enable-termination-protection

# Delete (⚠️ deletes resources unless DeletionPolicy: Retain)
aws cloudformation delete-stack --stack-name orders-network-dev
aws cloudformation wait stack-delete-complete --stack-name orders-network-dev
```

**Related CLIs:**

```bash
# AWS CDK
npx cdk bootstrap aws://111111111111/ap-south-1     # once per account/region
npx cdk synth && npx cdk diff && npx cdk deploy --all

# AWS SAM
sam init && sam build && sam local invoke HelloFunction --event events/event.json
sam deploy --guided            # first time; afterwards: sam deploy
sam logs -n HelloFunction --tail
```

---

# 13 — CloudWatch Metrics, Alarms & Logs

```bash
# Logs
aws logs describe-log-groups --query 'logGroups[].[logGroupName,retentionInDays,storedBytes]' --output table
aws logs put-retention-policy --log-group-name /aws/lambda/hello --retention-in-days 30     # stop paying for "never expire"
aws logs tail /ecs/orders-api --follow --since 30m --filter-pattern ERROR
aws logs filter-log-events --log-group-name /ecs/orders-api --filter-pattern '"timeout"' --start-time $(($(date +%s) - 3600))000

# Logs Insights query (async: start, then fetch results)
QID=$(aws logs start-query --log-group-name /ecs/orders-api \
  --start-time $(($(date +%s) - 3600)) --end-time $(date +%s) \
  --query-string 'fields @timestamp, @message | filter @message like /ERROR/ | sort @timestamp desc | limit 20' \
  --query queryId --output text)
sleep 5; aws logs get-query-results --query-id $QID

# Metrics
aws cloudwatch list-metrics --namespace AWS/EC2 --dimensions Name=InstanceId,Value=i-0abc
aws cloudwatch get-metric-statistics --namespace AWS/EC2 --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=i-0abc --statistics Average Maximum --period 300 \
  --start-time 2026-10-18T00:00:00Z --end-time 2026-10-18T06:00:00Z
aws cloudwatch put-metric-data --namespace Acme/Orders --metric-name OrdersPlaced --value 1 --unit Count   # custom metric

# Alarms
aws cloudwatch put-metric-alarm --alarm-name orders-api-5xx-high \
  --namespace AWS/ApplicationELB --metric-name HTTPCode_Target_5XX_Count \
  --dimensions Name=LoadBalancer,Value=app/orders-alb/0123456789abcdef \
  --statistic Sum --period 60 --evaluation-periods 5 --threshold 10 \
  --comparison-operator GreaterThanThreshold --treat-missing-data notBreaching \
  --alarm-actions arn:aws:sns:ap-south-1:111111111111:oncall
aws cloudwatch describe-alarms --state-value ALARM --query 'MetricAlarms[].[AlarmName,StateReason]' --output table
aws cloudwatch set-alarm-state --alarm-name orders-api-5xx-high --state-value ALARM --state-reason "testing notifications"
```

---

# 14 — Secrets Manager, Parameter Store & KMS

```bash
# Secrets Manager
aws secretsmanager create-secret --name prod/orders/db --secret-string '{"username":"app","password":"CHANGE_ME"}'
aws secretsmanager get-secret-value --secret-id prod/orders/db --query SecretString --output text
aws secretsmanager put-secret-value --secret-id prod/orders/db --secret-string file://new-secret.json
aws secretsmanager rotate-secret --secret-id prod/orders/db       # requires rotation configured (Lambda / managed rotation)
aws secretsmanager list-secrets --query 'SecretList[].[Name,LastRotatedDate]' --output table

# Parameter Store
aws ssm put-parameter --name /orders/dev/log_level --value info --type String
aws ssm put-parameter --name /orders/dev/api_key --value 'xyz' --type SecureString --overwrite
aws ssm get-parameter --name /orders/dev/api_key --with-decryption --query Parameter.Value --output text
aws ssm get-parameters-by-path --path /orders/dev --recursive --with-decryption --query 'Parameters[].[Name,Value]' --output table

# KMS
aws kms create-key --description "orders data key" --query KeyMetadata.KeyId --output text
aws kms create-alias --alias-name alias/orders --target-key-id <key-id>
aws kms enable-key-rotation --key-id alias/orders
aws kms encrypt --key-id alias/orders --plaintext fileb://secret.txt --query CiphertextBlob --output text > secret.b64
base64 -d secret.b64 > secret.enc && aws kms decrypt --ciphertext-blob fileb://secret.enc --query Plaintext --output text | base64 -d
aws kms schedule-key-deletion --key-id <key-id> --pending-window-in-days 30     # ⚠️ data encrypted with it becomes unrecoverable after deletion
```

> ⚠️ Secrets typed on the command line end up in **shell history**. Prefer `file://` inputs or
> prompts, and clear history if you slip.

---

# 15 — Load Balancers & Auto Scaling

```bash
# ELBv2 (ALB/NLB)
aws elbv2 describe-load-balancers --query 'LoadBalancers[].[LoadBalancerName,Type,DNSName,State.Code]' --output table
aws elbv2 describe-target-groups --load-balancer-arn <alb-arn> --query 'TargetGroups[].[TargetGroupName,Port,HealthCheckPath]'
aws elbv2 describe-target-health --target-group-arn <tg-arn> \
  --query 'TargetHealthDescriptions[].[Target.Id,TargetHealth.State,TargetHealth.Reason]' --output table   # "why is my target unhealthy?"
aws elbv2 describe-listeners --load-balancer-arn <alb-arn>
aws elbv2 deregister-targets --target-group-arn <tg-arn> --targets Id=i-0abc     # take out of rotation

# Auto Scaling groups
aws autoscaling describe-auto-scaling-groups --query 'AutoScalingGroups[].[AutoScalingGroupName,MinSize,DesiredCapacity,MaxSize]' --output table
aws autoscaling set-desired-capacity --auto-scaling-group-name web-asg --desired-capacity 6
aws autoscaling update-auto-scaling-group --auto-scaling-group-name web-asg --min-size 2 --max-size 10
aws autoscaling start-instance-refresh --auto-scaling-group-name web-asg \
  --preferences '{"MinHealthyPercentage":90,"InstanceWarmup":120}'      # roll to the new launch template version
aws autoscaling describe-scaling-activities --auto-scaling-group-name web-asg --max-items 5
aws autoscaling put-scaling-policy --auto-scaling-group-name web-asg --policy-name cpu50 \
  --policy-type TargetTrackingScaling \
  --target-tracking-configuration '{"PredefinedMetricSpecification":{"PredefinedMetricType":"ASGAverageCPUUtilization"},"TargetValue":50}'
```

---

# 16 — Route 53, ACM & CloudFront

```bash
# Route 53
aws route53 list-hosted-zones --query 'HostedZones[].[Name,Id,Config.PrivateZone]' --output table
aws route53 list-resource-record-sets --hosted-zone-id Z0123456789 --query 'ResourceRecordSets[?Type==`A`||Type==`CNAME`]'
aws route53 change-resource-record-sets --hosted-zone-id Z0123456789 --change-batch file://upsert-record.json
aws route53 get-change --id <change-id>        # PENDING → INSYNC

# ACM (certificate for CloudFront must be requested in us-east-1)
aws acm request-certificate --domain-name www.acme.com --subject-alternative-names acme.com \
  --validation-method DNS --region us-east-1
aws acm describe-certificate --certificate-arn <arn> --region us-east-1 \
  --query 'Certificate.DomainValidationOptions[].ResourceRecord'      # CNAMEs to add in DNS
aws acm list-certificates --query 'CertificateSummaryList[].[DomainName,Status,NotAfter]' --output table

# CloudFront
aws cloudfront list-distributions --query 'DistributionList.Items[].[Id,DomainName,Aliases.Items[0]]' --output table
aws cloudfront create-invalidation --distribution-id E123ABC --paths "/index.html" "/"
aws cloudfront get-invalidation --distribution-id E123ABC --id <invalidation-id>
```

`upsert-record.json`:

```json
{
  "Comment": "point api to ALB",
  "Changes": [{
    "Action": "UPSERT",
    "ResourceRecordSet": {
      "Name": "api.acme.com",
      "Type": "A",
      "AliasTarget": {
        "HostedZoneId": "<ALB-hosted-zone-id>",
        "DNSName": "orders-alb-123456.ap-south-1.elb.amazonaws.com",
        "EvaluateTargetHealth": true
      }
    }
  }]
}
```

---

# 17 — SQS, SNS, EventBridge & Step Functions

```bash
# SQS
Q=$(aws sqs create-queue --queue-name jobs --attributes VisibilityTimeout=60 --query QueueUrl --output text)
aws sqs send-message --queue-url $Q --message-body '{"job":"resize","key":"img/1.jpg"}'
aws sqs receive-message --queue-url $Q --max-number-of-messages 5 --wait-time-seconds 10
aws sqs delete-message --queue-url $Q --receipt-handle <handle>
aws sqs get-queue-attributes --queue-url $Q --attribute-names ApproximateNumberOfMessages ApproximateNumberOfMessagesNotVisible
aws sqs purge-queue --queue-url $Q                    # ⚠️ deletes all messages
# DLQ redrive back to source
aws sqs start-message-move-task --source-arn arn:aws:sqs:ap-south-1:111111111111:jobs-dlq

# SNS
T=$(aws sns create-topic --name oncall --query TopicArn --output text)
aws sns subscribe --topic-arn $T --protocol email --notification-endpoint oncall@acme.com   # confirm via email
aws sns subscribe --topic-arn $T --protocol sqs --notification-endpoint arn:aws:sqs:ap-south-1:111111111111:jobs
aws sns publish --topic-arn $T --subject "Test" --message "Hello from the CLI"

# EventBridge
aws events put-events --entries '[{"Source":"acme.orders","DetailType":"OrderPlaced","Detail":"{\"orderId\":\"A12\",\"total\":499}","EventBusName":"default"}]'
aws events list-rules --query 'Rules[].[Name,State,ScheduleExpression]' --output table
aws events put-rule --name order-placed --event-pattern '{"source":["acme.orders"],"detail-type":["OrderPlaced"]}'
aws events put-targets --rule order-placed --targets 'Id=1,Arn=arn:aws:lambda:ap-south-1:111111111111:function:notify'

# EventBridge Scheduler (cron with time zone)
aws scheduler create-schedule --name nightly-report \
  --schedule-expression "cron(0 2 * * ? *)" --schedule-expression-timezone "Asia/Kolkata" \
  --flexible-time-window Mode=OFF \
  --target '{"Arn":"arn:aws:lambda:ap-south-1:111111111111:function:report","RoleArn":"arn:aws:iam::111111111111:role/scheduler-invoke"}'

# Step Functions
aws stepfunctions list-state-machines --query 'stateMachines[].[name,stateMachineArn]' --output table
aws stepfunctions start-execution --state-machine-arn <arn> --input '{"orderId":"A12"}'
aws stepfunctions list-executions --state-machine-arn <arn> --status-filter FAILED --max-items 5
aws stepfunctions describe-execution --execution-arn <exec-arn> --query '[status,error,cause]'
```

---

# 18 — Security & Governance

```bash
# CloudTrail: "who deleted / changed this?"
aws cloudtrail lookup-events --lookup-attributes AttributeKey=EventName,AttributeValue=DeleteBucket --max-results 10 \
  --query 'Events[].[EventTime,Username,EventName]' --output table
aws cloudtrail lookup-events --lookup-attributes AttributeKey=ResourceName,AttributeValue=i-0abc --max-results 20
aws cloudtrail describe-trails --query 'trailList[].[Name,IsMultiRegionTrail,IsOrganizationTrail,S3BucketName]'
aws cloudtrail get-trail-status --name org-trail --query IsLogging

# Organizations
aws organizations describe-organization
aws organizations list-accounts --query 'Accounts[].[Name,Id,Status]' --output table
aws organizations list-roots && aws organizations list-organizational-units-for-parent --parent-id r-abcd
aws organizations list-policies --filter SERVICE_CONTROL_POLICY

# GuardDuty
DET=$(aws guardduty list-detectors --query 'DetectorIds[0]' --output text)
aws guardduty list-findings --detector-id $DET --finding-criteria '{"Criterion":{"severity":{"Gte":7}}}'
aws guardduty get-findings --detector-id $DET --finding-ids <id> --query 'Findings[].[Type,Severity,Title]'

# Security Hub / Config / Access Analyzer
aws securityhub get-findings --filters '{"SeverityLabel":[{"Value":"CRITICAL","Comparison":"EQUALS"}],"RecordState":[{"Value":"ACTIVE","Comparison":"EQUALS"}]}' --max-items 10
aws configservice describe-compliance-by-config-rule --compliance-types NON_COMPLIANT
aws accessanalyzer list-analyzers
aws accessanalyzer list-findings --analyzer-arn <arn> --filter '{"status":{"eq":["ACTIVE"]}}'

# Inspector (vulnerabilities)
aws inspector2 list-findings --filter-criteria '{"severity":[{"comparison":"EQUALS","value":"CRITICAL"}]}' --max-results 10
```

---

# 19 — Cost, Billing & Service Quotas

```bash
# Cost by service this month (Cost Explorer API is served from us-east-1)
aws ce get-cost-and-usage --region us-east-1 \
  --time-period Start=2026-10-01,End=2026-10-18 --granularity MONTHLY --metrics UnblendedCost \
  --group-by Type=DIMENSION,Key=SERVICE \
  --query 'ResultsByTime[0].Groups[].[Keys[0],Metrics.UnblendedCost.Amount]' --output table

# Cost by tag (e.g. Owner)
aws ce get-cost-and-usage --region us-east-1 --time-period Start=2026-10-01,End=2026-10-18 \
  --granularity MONTHLY --metrics UnblendedCost --group-by Type=TAG,Key=Owner

# Forecast
aws ce get-cost-forecast --region us-east-1 --time-period Start=2026-10-18,End=2026-11-01 --metric UNBLENDED_COST --granularity MONTHLY

# Budgets
aws budgets describe-budgets --account-id 111111111111
aws budgets create-budget --account-id 111111111111 --budget file://budget.json --notifications-with-subscribers file://notifications.json

# Find waste: unattached volumes, unassociated Elastic IPs, old snapshots
aws ec2 describe-volumes --filters Name=status,Values=available --query 'Volumes[].[VolumeId,Size,CreateTime]' --output table
aws ec2 describe-addresses --query 'Addresses[?AssociationId==null].[PublicIp,AllocationId]' --output table
aws ec2 describe-snapshots --owner-ids self --query 'Snapshots[?StartTime<=`2026-01-01`].[SnapshotId,VolumeSize,StartTime]' --output table

# Service Quotas
aws service-quotas list-service-quotas --service-code ec2 --query 'Quotas[].[QuotaName,Value]' --output table
aws service-quotas get-service-quota --service-code ec2 --quota-code L-1216C47A    # Running On-Demand Standard instances (vCPUs)
aws service-quotas request-service-quota-increase --service-code ec2 --quota-code L-1216C47A --desired-value 256
```

`budget.json` + `notifications.json` (monthly $100 budget, email at 80% actual):

```json
{ "BudgetName": "monthly-100", "BudgetLimit": { "Amount": "100", "Unit": "USD" },
  "TimeUnit": "MONTHLY", "BudgetType": "COST" }
```

```json
[{ "Notification": { "NotificationType": "ACTUAL", "ComparisonOperator": "GREATER_THAN", "Threshold": 80, "ThresholdType": "PERCENTAGE" },
   "Subscribers": [{ "SubscriptionType": "EMAIL", "Address": "me@example.com" }] }]
```

---

# 20 — Bedrock (Generative AI)

```bash
# Which models are available in this region?
aws bedrock list-foundation-models --region us-east-1 \
  --query 'modelSummaries[].[modelId,providerName,modelName]' --output table

# Send a prompt with the Converse API (same request shape across models)
aws bedrock-runtime converse --region us-east-1 \
  --model-id <model-id-or-inference-profile-id> \
  --messages '[{"role":"user","content":[{"text":"Explain an AWS VPC to a beginner in 3 sentences."}]}]' \
  --inference-config '{"maxTokens":300,"temperature":0.3}' \
  --query 'output.message.content[0].text' --output text
```

> Model access and IDs vary by region/account, and many newer models are invoked through
> **inference profiles** (IDs like `us.<provider>.<model>…`). Copy the exact ID from
> `list-foundation-models` / `list-inference-profiles` or the Bedrock console.

---

# 21 — Handy Recipes & One-Liners

```bash
# Who am I and where am I?
aws sts get-caller-identity --query '[Account,Arn]' --output text; aws configure get region

# All running instances in ALL regions
for r in $(aws ec2 describe-regions --query 'Regions[].RegionName' --output text); do
  echo "== $r"; aws ec2 describe-instances --region $r --filters Name=instance-state-name,Values=running \
    --query 'Reservations[].Instances[].[InstanceId,InstanceType]' --output text
done

# Stop all dev instances (by tag) at the end of the day
aws ec2 stop-instances --instance-ids $(aws ec2 describe-instances \
  --filters Name=tag:Environment,Values=dev Name=instance-state-name,Values=running \
  --query 'Reservations[].Instances[].InstanceId' --output text)

# Public S3 buckets check (any bucket without full Block Public Access)
for b in $(aws s3api list-buckets --query 'Buckets[].Name' --output text); do
  aws s3api get-public-access-block --bucket $b >/dev/null 2>&1 || echo "⚠️ no public access block: $b"
done

# Security groups open to the world on SSH/RDP
aws ec2 describe-security-groups \
  --query 'SecurityGroups[?IpPermissions[?(FromPort==`22`||FromPort==`3389`) && IpRanges[?CidrIp==`0.0.0.0/0`]]].[GroupId,GroupName]' --output table

# Log groups without retention (cost leak)
aws logs describe-log-groups --query 'logGroups[?!retentionInDays].logGroupName' --output text

# Latest ECS deployment events (why is my service not stable?)
aws ecs describe-services --cluster prod --services orders-api --query 'services[0].events[:10].[createdAt,message]' --output table

# Find which stack owns a resource
aws cloudformation describe-stack-resources --physical-resource-id i-0abc --query 'StackResources[0].StackName'

# Copy a secret value into an env var without printing it
export DB_PASSWORD=$(aws secretsmanager get-secret-value --secret-id prod/orders/db --query SecretString --output text | jq -r .password)

# Tail all logs for an ECS service and grep
aws logs tail /ecs/orders-api --since 1h --format short | grep -i error
```

---

# 22 — Windows PowerShell Notes & Troubleshooting

### PowerShell quoting differences

Most examples above use Bash syntax (Linux/macOS/WSL/Git Bash). In **PowerShell**:

| Bash | PowerShell |
|------|-----------|
| `export AWS_PROFILE=dev` | `$env:AWS_PROFILE = "dev"` |
| `VAR=$(aws ... --output text)` | `$VAR = aws ... --output text` |
| Line continuation `\` | Backtick `` ` `` at line end |
| `'{"a":"b"}'` inline JSON | Escaping is painful. Use **`file://payload.json`** instead |
| `$(date +%s)` | `[DateTimeOffset]::UtcNow.ToUnixTimeSeconds()` |

```powershell
# PowerShell example
$env:AWS_PROFILE = "dev-admin"
$ids = aws ec2 describe-instances --filters "Name=tag:Environment,Values=dev" `
        --query "Reservations[].Instances[].InstanceId" --output text
aws ec2 stop-instances --instance-ids $ids.Split()
```

> 💡 **AWS Tools for PowerShell** (`Install-Module AWS.Tools.Installer`) offers native cmdlets
> (`Get-EC2Instance`, `Get-S3Object`) that return objects. Nice if you live in PowerShell.

### Common errors

| Error | Meaning | Fix |
|-------|---------|-----|
| `Unable to locate credentials` | No credentials found | `aws configure sso` / `aws sso login --profile X`; check `AWS_PROFILE` |
| `The SSO session associated with this profile has expired` | SSO token expired | `aws sso login --profile X` |
| `An error occurred (AccessDenied / UnauthorizedOperation)` | Missing IAM permission (or SCP/boundary denies) | Check `sts get-caller-identity`; read the action in the message; the EC2 encoded message can be decoded with `aws sts decode-authorization-message --encoded-message <msg>` |
| `ExpiredToken` / `RequestExpired` | Temporary credentials expired or **clock skew** | Re-login; sync your system clock |
| `Could not connect to the endpoint URL` | Wrong region/service name, or no network/proxy | Check `--region`; corporate proxy (`HTTPS_PROXY`) |
| `InvalidParameterValue` with JSON | Quoting/escaping problem (often PowerShell) | Use `file://` JSON files |
| Output opens in a pager and "hangs" in scripts | CLI pager | `--no-cli-pager` or `AWS_PAGER=""` |
| `Invalid base64` on `lambda invoke` | CLI v2 treats blobs as base64 | Add `--cli-binary-format raw-in-base64-out` |
| Results seem incomplete | Pagination | Remove `--max-items`, or loop with `--starting-token` |
| SSL certificate errors behind a corporate proxy | TLS inspection | Set `AWS_CA_BUNDLE` to the corporate CA bundle |

### Debugging

```bash
aws s3 ls --debug 2>&1 | less          # full request/response, credential resolution chain
aws configure list                      # where credentials and region are coming from
```

---

[⬅️ Back to AWS Index](README.md) · [01 — Terms](01-aws-terms.md) · [02 — Services](02-aws-services.md) · [03 — Scenarios](03-aws-scenarios.md)
