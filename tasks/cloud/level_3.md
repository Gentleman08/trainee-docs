[🏠 Home](../../README.md) · [Tasks](../README.md) · [Cloud Tasks](.)

# ☁️ Cloud & Data Center Tasks — Level 3 (🔴 Hard)

> **Objective:** Advanced cloud — multi-region HA, Kubernetes on cloud, IaC modules, DR planning, cost optimization, and security hardening.  
> **Prerequisites:** Completed Levels 1 and 2, Terraform proficiency, kubectl experience  
> **Time Estimate:** 10–12 hours total

---

## Table of Contents

1. [Multi-Region High Availability Architecture](#1-multi-region-high-availability-architecture)
2. [EKS Cluster Deployment & Management](#2-eks-cluster-deployment--management)
3. [Terraform Modules & Remote State](#3-terraform-modules--remote-state)
4. [Disaster Recovery — Pilot Light Setup](#4-disaster-recovery--pilot-light-setup)
5. [Zero-Downtime Deployment Strategies](#5-zero-downtime-deployment-strategies)
6. [Cloud Security Hardening & Audit](#6-cloud-security-hardening--audit)
7. [FinOps — Cost Optimization Challenge](#7-finops--cost-optimization-challenge)
8. [Service Mesh with AWS App Mesh / Istio](#8-service-mesh-with-aws-app-mesh--istio)
9. [Observability Stack on Cloud](#9-observability-stack-on-cloud)
10. [Production Architecture Design Challenge](#10-production-architecture-design-challenge)

---

## 1. Multi-Region High Availability Architecture

### Objective
Design and implement a multi-region active-passive architecture with Route 53 failover.

### Architecture
```
  ┌──────────────────────────────────────────────────┐
  │              Route 53 (Failover DNS)              │
  │    app.company.com → Primary (us-east-1)          │
  │                    → Secondary (eu-west-1)        │
  └─────────┬───────────────────────┬────────────────┘
            ▼                       ▼
  ┌── us-east-1 (PRIMARY) ──┐  ┌── eu-west-1 (SECONDARY) ──┐
  │  ALB → ASG (active)      │  │  ALB → ASG (standby)       │
  │  RDS Primary              │  │  RDS Read Replica           │
  │  ElastiCache              │  │  ElastiCache (cold)         │
  │  S3 (cross-region repl)   │  │  S3 (replica bucket)        │
  └──────────────────────────┘  └────────────────────────────┘
```

### Tasks

**1.1** Create Route 53 health check for primary region:
```bash
HC_ID=$(aws route53 create-health-check --caller-reference $(date +%s) \
  --health-check-config '{
    "IPAddress": "<primary-alb-ip>",
    "Port": 443,
    "Type": "HTTPS",
    "ResourcePath": "/health",
    "RequestInterval": 10,
    "FailureThreshold": 3
  }' --query 'HealthCheck.Id' --output text)
```

**1.2** Create failover DNS records:
```bash
# Primary record
aws route53 change-resource-record-sets --hosted-zone-id <zone-id> \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "app.company.com",
        "Type": "A",
        "SetIdentifier": "primary",
        "Failover": "PRIMARY",
        "AliasTarget": {
          "HostedZoneId": "<alb-zone-id>",
          "DNSName": "<primary-alb-dns>",
          "EvaluateTargetHealth": true
        },
        "HealthCheckId": "'$HC_ID'"
      }
    }]
  }'

# Secondary record (same pattern with Failover: SECONDARY)
```

**1.3** Set up RDS cross-region read replica:
```bash
aws rds create-db-instance-read-replica \
  --db-instance-identifier dr-replica \
  --source-db-instance-identifier arn:aws:rds:us-east-1:<account>:db:primary-db \
  --region eu-west-1 \
  --db-instance-class db.t3.medium
```

**1.4** Set up S3 cross-region replication:
```bash
# Enable versioning on source and destination buckets (required)
aws s3api put-bucket-versioning --bucket source-bucket --versioning-configuration Status=Enabled
aws s3api put-bucket-versioning --bucket dest-bucket --versioning-configuration Status=Enabled

# Create replication configuration
aws s3api put-bucket-replication --bucket source-bucket --replication-configuration '{
  "Role": "arn:aws:iam::<account>:role/S3ReplicationRole",
  "Rules": [{
    "Status": "Enabled",
    "Destination": {
      "Bucket": "arn:aws:s3:::dest-bucket",
      "StorageClass": "STANDARD"
    }
  }]
}'
```

**1.5** Simulate failover:
- Manually fail the primary health check
- Verify Route 53 switches DNS to the secondary region
- Promote the RDS read replica to standalone: `aws rds promote-read-replica`

### Verification
- Health checks monitor both regions
- DNS failover triggers automatically when primary is unhealthy
- RDS replica can be promoted in < 10 minutes

---

## 2. EKS Cluster Deployment & Management

### Objective
Deploy and manage an EKS (Kubernetes) cluster with managed node groups.

### Tasks

**2.1** Create an EKS cluster using eksctl:
```bash
# Install eksctl
curl --silent --location "https://github.com/eksctl-io/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin

# Create cluster
eksctl create cluster \
  --name devops-lab-eks \
  --region us-east-1 \
  --version 1.28 \
  --nodegroup-name workers \
  --node-type t3.medium \
  --nodes 2 \
  --nodes-min 2 \
  --nodes-max 4 \
  --managed
```

**2.2** Verify cluster access:
```bash
kubectl get nodes
kubectl get pods -A
kubectl cluster-info
```

**2.3** Deploy a sample application:
```yaml
# app.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: web
        image: nginx:alpine
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 250m
            memory: 256Mi
---
apiVersion: v1
kind: Service
metadata:
  name: web-svc
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: nlb
spec:
  type: LoadBalancer
  selector:
    app: web
  ports:
  - port: 80
    targetPort: 80
```

```bash
kubectl apply -f app.yaml
kubectl get svc web-svc   # Get the LoadBalancer URL
```

**2.4** Set up Horizontal Pod Autoscaler:
```bash
kubectl autoscale deployment web-app --cpu-percent=50 --min=3 --max=10
kubectl get hpa
```

**2.5** Install the AWS Load Balancer Controller:
```bash
# This enables ALB Ingress
helm repo add eks https://aws.github.io/eks-charts
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=devops-lab-eks
```

**2.6** Clean up:
```bash
eksctl delete cluster --name devops-lab-eks --region us-east-1
```

> **⚠️ Gotcha:** EKS control plane costs ~$0.10/hour ($73/month) regardless of worker nodes. Always delete lab clusters when done.

### Verification
- EKS cluster is running with managed node groups
- Application is accessible via LoadBalancer
- HPA is configured and monitoring

---

## 3. Terraform Modules & Remote State

### Objective
Create reusable Terraform modules and configure remote state with locking.

### Tasks

**3.1** Set up remote state backend:
```bash
# Create S3 bucket for state
aws s3 mb s3://devops-lab-terraform-state-$(aws sts get-caller-identity --query Account --output text)

# Create DynamoDB table for locking
aws dynamodb create-table \
  --table-name terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

**3.2** Configure the backend:
```hcl
# backend.tf
terraform {
  backend "s3" {
    bucket         = "devops-lab-terraform-state-123456789012"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}
```

**3.3** Create a reusable VPC module:
```
modules/
└── vpc/
    ├── main.tf
    ├── variables.tf
    └── outputs.tf
```

```hcl
# modules/vpc/variables.tf
variable "name" { type = string }
variable "cidr" { type = string }
variable "azs" { type = list(string) }
variable "public_subnets" { type = list(string) }
variable "private_subnets" { type = list(string) }
variable "environment" { type = string }
```

```hcl
# modules/vpc/main.tf
resource "aws_vpc" "this" {
  cidr_block           = var.cidr
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags = { Name = var.name, Environment = var.environment }
}

resource "aws_subnet" "public" {
  count             = length(var.public_subnets)
  vpc_id            = aws_vpc.this.id
  cidr_block        = var.public_subnets[count.index]
  availability_zone = var.azs[count.index]
  map_public_ip_on_launch = true
  tags = { Name = "${var.name}-public-${count.index}" }
}

resource "aws_subnet" "private" {
  count             = length(var.private_subnets)
  vpc_id            = aws_vpc.this.id
  cidr_block        = var.private_subnets[count.index]
  availability_zone = var.azs[count.index]
  tags = { Name = "${var.name}-private-${count.index}" }
}
```

```hcl
# modules/vpc/outputs.tf
output "vpc_id" { value = aws_vpc.this.id }
output "public_subnet_ids" { value = aws_subnet.public[*].id }
output "private_subnet_ids" { value = aws_subnet.private[*].id }
```

**3.4** Use the module:
```hcl
# main.tf
module "vpc" {
  source = "./modules/vpc"

  name            = "prod"
  cidr            = "10.0.0.0/16"
  azs             = ["us-east-1a", "us-east-1b"]
  public_subnets  = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnets = ["10.0.3.0/24", "10.0.4.0/24"]
  environment     = "prod"
}
```

**3.5** Manage workspaces:
```bash
terraform workspace new staging
terraform workspace new prod
terraform workspace list
terraform workspace select prod
```

### Verification
- Remote state is stored in S3 with DynamoDB locking
- VPC module is reusable across environments
- Workspaces separate state for staging/prod

---

## 4. Disaster Recovery — Pilot Light Setup

### Objective
Implement a Pilot Light DR strategy with automated recovery.

### DR Strategy Comparison
```
  ┌─────────────┬─────────┬──────────┬──────────────────────┐
  │ Strategy     │ RTO     │ Cost     │ Description          │
  ├─────────────┼─────────┼──────────┼──────────────────────┤
  │ Backup/Rest  │ Hours   │ $        │ Restore from backups │
  │ Pilot Light  │ 10-30m  │ $$       │ Core infra running   │
  │ Warm Standby │ Minutes │ $$$      │ Scaled-down copy     │
  │ Active-Active│ ~0      │ $$$$     │ Full copy in both    │
  └─────────────┴─────────┴──────────┴──────────────────────┘
```

### Tasks

**4.1** Document the Pilot Light components:

| Component | Primary Region | DR Region | Status |
|-----------|---------------|-----------|--------|
| VPC/Network | Full | Full | Always running |
| RDS | Primary | Read Replica | Always running |
| App Servers (ASG) | 4 instances | 0 instances (ASG exists) | Scaled to 0 |
| ALB | Active | Created but no targets | Standby |
| Route 53 | Primary record | Secondary record | Failover routing |

**4.2** Create a DR runbook script:
```bash
#!/bin/bash
# dr-failover.sh — Pilot Light Activation
set -euo pipefail

DR_REGION="eu-west-1"
ASG_NAME="dr-app-asg"
RDS_REPLICA="dr-db-replica"

echo "=== DISASTER RECOVERY FAILOVER ==="
echo "Timestamp: $(date -u)"

# Step 1: Scale up DR ASG
echo "[1/4] Scaling up DR application servers..."
aws autoscaling update-auto-scaling-group \
  --auto-scaling-group-name $ASG_NAME \
  --min-size 2 --desired-capacity 4 \
  --region $DR_REGION

# Step 2: Promote RDS read replica
echo "[2/4] Promoting RDS read replica to primary..."
aws rds promote-read-replica \
  --db-instance-identifier $RDS_REPLICA \
  --region $DR_REGION

# Step 3: Wait for instances to be healthy
echo "[3/4] Waiting for instances to pass health checks..."
aws autoscaling wait group-in-service \
  --auto-scaling-group-name $ASG_NAME \
  --region $DR_REGION

# Step 4: Verify
echo "[4/4] Verifying DR environment..."
aws elbv2 describe-target-health \
  --target-group-arn $DR_TG_ARN \
  --region $DR_REGION

echo "=== FAILOVER COMPLETE ==="
echo "DNS will update automatically via Route 53 health checks"
```

**4.3** Create a DR test plan:
```markdown
## DR Test Plan

### Pre-Test Checklist
- [ ] Notify stakeholders
- [ ] Verify RDS replica lag < 1 second
- [ ] Confirm S3 replication is current
- [ ] Have rollback procedure ready

### Test Steps
1. Trigger failover script
2. Monitor Route 53 health check status
3. Verify application responds from DR region
4. Run smoke tests against DR environment
5. Measure actual RTO (target: < 30 minutes)

### Post-Test
- [ ] Document actual RTO achieved
- [ ] Scale DR back to pilot light (ASG → 0)
- [ ] Re-establish RDS replication
- [ ] Update runbook with lessons learned
```

### Verification
- DR script executes without errors
- RTO is within the 30-minute target
- All components are documented

---

## 5. Zero-Downtime Deployment Strategies

### Objective
Implement blue-green and canary deployments on AWS.

### Blue-Green Deployment
```
  ┌────────────────────────────────────────────┐
  │              ALB (Production)               │
  │                                              │
  │  Before:  100% ──► Blue (v1.0) ✅          │
  │                    Green (v2.0) 🔄 deploying │
  │                                              │
  │  After:   100% ──► Green (v2.0) ✅          │
  │                    Blue (v1.0) 🔴 standby    │
  └────────────────────────────────────────────┘
```

### Tasks

**5.1** Blue-Green with ALB target group switching:
```bash
# Create two target groups
BLUE_TG=$(aws elbv2 create-target-group --name blue-tg --protocol HTTP --port 80 --vpc-id $VPC_ID --query 'TargetGroups[0].TargetGroupArn' --output text)
GREEN_TG=$(aws elbv2 create-target-group --name green-tg --protocol HTTP --port 80 --vpc-id $VPC_ID --query 'TargetGroups[0].TargetGroupArn' --output text)

# Deploy v2 to green target group
# Register new instances to GREEN_TG...

# Switch traffic (instant cutover)
aws elbv2 modify-listener --listener-arn $LISTENER_ARN \
  --default-actions Type=forward,TargetGroupArn=$GREEN_TG

# Rollback if needed
aws elbv2 modify-listener --listener-arn $LISTENER_ARN \
  --default-actions Type=forward,TargetGroupArn=$BLUE_TG
```

**5.2** Canary with weighted target groups:
```bash
# Send 10% to canary (green), 90% to stable (blue)
aws elbv2 modify-listener --listener-arn $LISTENER_ARN \
  --default-actions '[{
    "Type": "forward",
    "ForwardConfig": {
      "TargetGroups": [
        {"TargetGroupArn": "'$BLUE_TG'", "Weight": 90},
        {"TargetGroupArn": "'$GREEN_TG'", "Weight": 10}
      ]
    }
  }]'

# Gradually increase: 10% → 25% → 50% → 100%
```

**5.3** Rolling update with CodeDeploy:
```yaml
# appspec.yml
version: 0.0
os: linux
files:
  - source: /
    destination: /var/www/html
hooks:
  BeforeInstall:
    - location: scripts/stop_server.sh
      timeout: 300
  AfterInstall:
    - location: scripts/start_server.sh
      timeout: 300
  ValidateService:
    - location: scripts/health_check.sh
      timeout: 60
```

### Verification
- Blue-green switch is instant (< 1 second)
- Canary gradually shifts traffic
- Rollback is immediate

---

## 6. Cloud Security Hardening & Audit

### Objective
Audit and harden the security posture of an AWS account.

### Tasks

**6.1** Run a security audit:
```bash
# Check for public S3 buckets
aws s3api list-buckets --query 'Buckets[].Name' --output text | while read bucket; do
  acl=$(aws s3api get-bucket-acl --bucket $bucket --query 'Grants[?Grantee.URI==`http://acs.amazonaws.com/groups/global/AllUsers`]' --output text 2>/dev/null)
  if [ -n "$acl" ]; then echo "PUBLIC BUCKET: $bucket"; fi
done

# Check for unencrypted EBS volumes
aws ec2 describe-volumes --query 'Volumes[?!Encrypted].{ID:VolumeId,Size:Size,State:State}' --output table

# Check for IAM users with console access but no MFA
aws iam generate-credential-report
aws iam get-credential-report --query 'Content' --output text | base64 -d | \
  awk -F, '$4=="true" && $8=="false" {print "NO MFA:", $1}'
```

**6.2** Enable CloudTrail:
```bash
aws cloudtrail create-trail --name devops-audit-trail \
  --s3-bucket-name devops-audit-logs \
  --is-multi-region-trail \
  --enable-log-file-validation

aws cloudtrail start-logging --name devops-audit-trail
```

**6.3** Enable GuardDuty:
```bash
aws guardduty create-detector --enable --finding-publishing-frequency FIFTEEN_MINUTES
```

**6.4** Enable AWS Config:
```bash
aws configservice put-configuration-recorder \
  --configuration-recorder name=default,roleARN=arn:aws:iam::<account>:role/ConfigRole \
  --recording-group allSupported=true,includeGlobalResourceTypes=true
```

**6.5** Security checklist:

| Control | Status | Command to Verify |
|---------|--------|-------------------|
| Root MFA enabled | ? | Console only |
| CloudTrail enabled | ? | `aws cloudtrail get-trail-status` |
| S3 public access blocked | ? | `aws s3api get-public-access-block` |
| EBS default encryption | ? | `aws ec2 get-ebs-encryption-by-default` |
| VPC flow logs enabled | ? | `aws ec2 describe-flow-logs` |
| GuardDuty enabled | ? | `aws guardduty list-detectors` |
| Password policy strong | ? | `aws iam get-account-password-policy` |

### Verification
- No public S3 buckets
- CloudTrail is logging across all regions
- All IAM users with console access have MFA
- Security services (GuardDuty, Config) are active

---

## 7. FinOps — Cost Optimization Challenge

### Objective
Analyze cloud spending and implement cost reduction strategies.

### Tasks

**7.1** Analyze current costs by service:
```bash
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-02-01 \
  --granularity DAILY \
  --metrics "UnblendedCost" \
  --group-by Type=DIMENSION,Key=SERVICE \
  --output json > /tmp/cost-report.json

# Find top 5 cost drivers
cat /tmp/cost-report.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
costs = {}
for day in data['ResultsByTime']:
    for group in day['Groups']:
        svc = group['Keys'][0]
        cost = float(group['Metrics']['UnblendedCost']['Amount'])
        costs[svc] = costs.get(svc, 0) + cost
for svc, cost in sorted(costs.items(), key=lambda x: -x[1])[:5]:
    print(f'{cost:>10.2f} USD  {svc}')
"
```

**7.2** Find idle resources:
```bash
# Find instances with < 5% CPU over 7 days
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=$INSTANCE_ID \
  --start-time $(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 86400 \
  --statistics Average

# Find unattached EBS volumes
aws ec2 describe-volumes --filters "Name=status,Values=available" \
  --query 'Volumes[].{ID:VolumeId,Size:Size,Created:CreateTime}' --output table

# Find unused Elastic IPs
aws ec2 describe-addresses --query 'Addresses[?!InstanceId].{IP:PublicIp,AllocID:AllocationId}' --output table
```

**7.3** Implement Savings Plans analysis:
```bash
aws ce get-savings-plans-purchase-recommendation \
  --savings-plans-type COMPUTE_SP \
  --term-in-years ONE_YEAR \
  --payment-option NO_UPFRONT \
  --lookback-period-in-days SIXTY_DAYS
```

**7.4** Create a cost optimization report:

| Resource | Current Cost | Optimization | Savings |
|----------|-------------|--------------|---------|
| EC2 m5.xlarge | $140/mo | Right-size to m5.large | $70/mo |
| Unused EBS | $50/mo | Delete 500GB unused | $50/mo |
| NAT Gateway | $45/mo | Use VPC endpoints | $30/mo |
| S3 Standard | $230/mo | Move to S3-IA | $115/mo |
| No Savings Plan | $500/mo | 1yr Compute SP | $150/mo |
| **Total** | **$965/mo** | | **$415/mo saved** |

### Verification
- Cost report identifies top spending services
- Idle resources are documented
- Cost reduction plan saves > 30% of current spend

---

## 8. Service Mesh with AWS App Mesh / Istio

### Objective
Implement a service mesh for microservice communication.

### Architecture
```
  ┌──────────────── Service Mesh ──────────────────┐
  │                                                  │
  │  ┌─ Pod ────────────┐   ┌─ Pod ────────────┐   │
  │  │ App Container     │   │ App Container     │   │
  │  │                   │   │                   │   │
  │  │ Envoy Sidecar ◄──┼───┼─► Envoy Sidecar  │   │
  │  └──────────────────┘   └──────────────────┘   │
  │                                                  │
  │  Features: mTLS, traffic splitting, retries,    │
  │  circuit breaking, observability                 │
  └──────────────────────────────────────────────────┘
```

### Tasks

**8.1** Install Istio on EKS:
```bash
curl -L https://istio.io/downloadIstio | sh -
cd istio-*
export PATH=$PWD/bin:$PATH

istioctl install --set profile=demo -y
kubectl label namespace default istio-injection=enabled
```

**8.2** Deploy a sample app with sidecars:
```bash
kubectl apply -f samples/bookinfo/platform/kube/bookinfo.yaml
kubectl get pods   # Each pod should have 2/2 containers (app + envoy)
```

**8.3** Configure traffic splitting (canary):
```yaml
# virtual-service.yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: reviews
spec:
  hosts:
  - reviews
  http:
  - route:
    - destination:
        host: reviews
        subset: v1
      weight: 90
    - destination:
        host: reviews
        subset: v2
      weight: 10
```

**8.4** Enable mutual TLS:
```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: default
spec:
  mtls:
    mode: STRICT
```

### Verification
- Sidecar proxies inject automatically
- Traffic splitting works between versions
- mTLS encrypts all inter-service traffic

---

## 9. Observability Stack on Cloud

### Objective
Set up a full observability stack: metrics, logs, and traces.

### Tasks

**9.1** Deploy Prometheus + Grafana on EKS:
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts

helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace \
  --set grafana.adminPassword=devops123

# Access Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
```

**9.2** Deploy Loki for log aggregation:
```bash
helm install loki grafana/loki-stack \
  --namespace monitoring \
  --set promtail.enabled=true \
  --set loki.persistence.enabled=true
```

**9.3** Deploy Jaeger for distributed tracing:
```bash
kubectl apply -f https://github.com/jaegertracing/jaeger-operator/releases/download/v1.51.0/jaeger-operator.yaml -n observability

cat << 'EOF' | kubectl apply -f -
apiVersion: jaegertracing.io/v1
kind: Jaeger
metadata:
  name: simple-prod
  namespace: observability
spec:
  strategy: production
  storage:
    type: elasticsearch
    options:
      es:
        server-urls: http://elasticsearch:9200
EOF
```

**9.4** Create a unified dashboard in Grafana:
- Panel 1: Request rate (Prometheus — `rate(http_requests_total[5m])`)
- Panel 2: Error rate (Prometheus — `rate(http_requests_total{status=~"5.."}[5m])`)
- Panel 3: P99 latency (Prometheus — `histogram_quantile(0.99, ...)`)
- Panel 4: Log errors (Loki — `{app="web"} |= "ERROR"`)
- Panel 5: Trace count (Jaeger)

**9.5** Create alerting rules:
```yaml
groups:
- name: sla-alerts
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.01
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "Error rate > 1% for {{ $labels.service }}"
      
  - alert: HighLatency
    expr: histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) > 2
    for: 5m
    labels:
      severity: warning
```

### Verification
- Prometheus collects metrics from all services
- Loki aggregates logs from all pods
- Grafana dashboard shows all three pillars

---

## 10. Production Architecture Design Challenge

### Objective
Design a complete production-grade cloud architecture for a SaaS application.

### Requirements
- Multi-tenant SaaS platform
- 50,000 DAU, 500 req/sec peak
- 99.95% SLA
- SOC 2 Type II compliance
- Budget: $15,000/month

### Tasks

**10.1** Architecture document must include:

| Section | Content |
|---------|---------|
| System Overview | High-level architecture diagram |
| Compute | EKS vs ECS vs EC2 — justification |
| Database | RDS vs Aurora vs DynamoDB — justification |
| Caching | ElastiCache strategy |
| Storage | S3 tiering + lifecycle policies |
| Networking | VPC design, subnets, security |
| CDN | CloudFront configuration |
| Auth | Cognito vs custom — justification |
| CI/CD | Pipeline design |
| Monitoring | Observability stack |
| Security | Encryption, WAF, Shield |
| DR | Strategy and RTO/RPO |
| Cost | Monthly estimate breakdown |

**10.2** Create the cost estimate:

| Service | Config | Monthly Cost |
|---------|--------|-------------|
| EKS Control Plane | 1 cluster | $73 |
| EC2 (nodes) | 6x m5.large (3 RI) | $400 |
| RDS Aurora | db.r5.large Multi-AZ | $500 |
| ElastiCache | cache.r5.large × 2 | $350 |
| ALB | 1 ALB | $20 |
| S3 | 1 TB | $23 |
| CloudFront | 5 TB transfer | $425 |
| NAT Gateway | 2 (multi-AZ) | $90 |
| Route 53 | 1 hosted zone | $1 |
| CloudWatch | Logs + Metrics | $100 |
| WAF | Standard | $40 |
| Secrets Manager | 10 secrets | $5 |
| **Total** | | **$2,027/mo** |

**10.3** Create the security controls matrix:

| Control | Implementation | Evidence |
|---------|---------------|----------|
| Encryption at rest | RDS: KMS, S3: SSE-S3, EBS: KMS | Config rule |
| Encryption in transit | TLS 1.2+ everywhere, mTLS mesh | Cert Manager |
| Access control | IAM roles, RBAC, least privilege | IAM Analyzer |
| Audit logging | CloudTrail, VPC Flow Logs, K8s audit | S3 + CloudWatch |
| Vulnerability scanning | ECR image scanning, Inspector | Weekly reports |
| DDoS protection | CloudFront + Shield Standard + WAF | Auto-enabled |
| Secret management | Secrets Manager, rotate every 90d | Rotation Lambda |

**10.4** Peer review checklist:
- [ ] Architecture handles the stated load (500 req/sec)
- [ ] 99.95% SLA achievable with multi-AZ design
- [ ] Cost is within $15,000/month budget
- [ ] SOC 2 controls are mapped
- [ ] DR strategy achieves stated RTO/RPO
- [ ] Network segmentation prevents lateral movement
- [ ] All data encrypted at rest and in transit
- [ ] Auto-scaling handles traffic spikes
- [ ] Monitoring covers all SLA metrics

### Verification
- Complete architecture document
- Cost estimate within budget
- Security controls mapped to SOC 2

---

> **Level 3 Complete!** You now have advanced cloud architecture skills.  
> **Review:** [Level 1](level_1.md) · [Level 2](level_2.md) · [Cloud Handbook](../../cloud/cloud_handbook.md)

[🏠 Home](../../README.md) · [Tasks](../README.md)
