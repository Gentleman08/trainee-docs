[🏠 Home](../README.md) · [Labs](README.md)

# 🌐 Networking Practice Lab — Build a Multi-Tier Network from Scratch

> **Objective:** Build a complete multi-tier network environment using Linux networking tools, from isolated network namespaces to a fully routed, firewalled, load-balanced, and monitored setup.  
> **Difficulty:** Progressive (Easy → Hard)  
> **Time Estimate:** 4–6 hours  
> **Prerequisites:** Linux VM (Ubuntu 22.04+), root access, Docker installed

---

## Table of Contents

1. [Lab Overview & Architecture](#1-lab-overview--architecture)
2. [Phase 1 — Network Foundation (Namespaces & Bridges)](#2-phase-1--network-foundation-namespaces--bridges)
3. [Phase 2 — IP Addressing & Routing](#3-phase-2--ip-addressing--routing)
4. [Phase 3 — DNS Resolution](#4-phase-3--dns-resolution)
5. [Phase 4 — Firewall & NAT](#5-phase-4--firewall--nat)
6. [Phase 5 — Load Balancing with Nginx](#6-phase-5--load-balancing-with-nginx)
7. [Phase 6 — TLS & Secure Communication](#7-phase-6--tls--secure-communication)
8. [Phase 7 — Monitoring & Troubleshooting](#8-phase-7--monitoring--troubleshooting)
9. [Phase 8 — Docker Networking Integration](#9-phase-8--docker-networking-integration)
10. [Cleanup](#10-cleanup)
11. [Lab Validation Checklist](#11-lab-validation-checklist)

---

## 1. Lab Overview & Architecture

### What You Will Build
```
                        ┌─────────────────┐
                        │   Host Machine   │
                        │   (Router/FW)    │
                        └───────┬─────────┘
                                │ br-main (10.10.0.1/24)
                ┌───────────────┼───────────────┐
                │               │               │
         ┌──────┴──────┐ ┌─────┴──────┐ ┌──────┴──────┐
         │  NS: web1    │ │  NS: web2   │ │  NS: web3   │
         │ 10.10.0.11   │ │ 10.10.0.12  │ │ 10.10.0.13  │
         │ (HTTP:80)    │ │ (HTTP:80)   │ │ (HTTP:80)   │
         └─────────────┘ └────────────┘ └─────────────┘
                │               │               │
                └───────────────┼───────────────┘
                                │
                         ┌──────┴──────┐
                         │  NS: db1    │
                         │ 10.10.1.10  │
                         │ (TCP:5432)  │
                         └─────────────┘
                           br-data (10.10.1.1/24)
```

### Skills Practiced
- Network namespaces and veth pairs
- Linux bridges
- IP routing and subnetting
- iptables firewall rules and NAT
- DNS server configuration
- Nginx load balancing
- TLS certificate management
- tcpdump packet analysis

---

## 2. Phase 1 — Network Foundation (Namespaces & Bridges)

### Step 1.1 — Create the Linux bridge for the web tier
```bash
# Create the bridge
sudo ip link add br-main type bridge
sudo ip addr add 10.10.0.1/24 dev br-main
sudo ip link set br-main up

# Verify
ip addr show br-main
```

### Step 1.2 — Create the bridge for the data tier
```bash
sudo ip link add br-data type bridge
sudo ip addr add 10.10.1.1/24 dev br-data
sudo ip link set br-data up
```

### Step 1.3 — Create the web server namespaces
```bash
for i in 1 2 3; do
    # Create namespace
    sudo ip netns add web${i}
    
    # Create veth pair
    sudo ip link add veth-web${i} type veth peer name veth-br-web${i}
    
    # Move one end into the namespace
    sudo ip link set veth-web${i} netns web${i}
    
    # Attach the other end to the bridge
    sudo ip link set veth-br-web${i} master br-main
    sudo ip link set veth-br-web${i} up
    
    # Configure IP inside namespace
    sudo ip netns exec web${i} ip addr add 10.10.0.1${i}/24 dev veth-web${i}
    sudo ip netns exec web${i} ip link set veth-web${i} up
    sudo ip netns exec web${i} ip link set lo up
    
    # Set default route
    sudo ip netns exec web${i} ip route add default via 10.10.0.1
    
    echo "Created web${i} namespace with IP 10.10.0.1${i}"
done
```

### Step 1.4 — Create the database namespace
```bash
sudo ip netns add db1

sudo ip link add veth-db1 type veth peer name veth-br-db1
sudo ip link set veth-db1 netns db1
sudo ip link set veth-br-db1 master br-data
sudo ip link set veth-br-db1 up

sudo ip netns exec db1 ip addr add 10.10.1.10/24 dev veth-db1
sudo ip netns exec db1 ip link set veth-db1 up
sudo ip netns exec db1 ip link set lo up
sudo ip netns exec db1 ip route add default via 10.10.1.1

echo "Created db1 namespace with IP 10.10.1.10"
```

### Step 1.5 — Verify all namespaces
```bash
sudo ip netns list
for ns in web1 web2 web3 db1; do
    echo "=== $ns ==="
    sudo ip netns exec $ns ip addr show | grep "inet "
done
```

> **✅ Checkpoint:** You should see 4 namespaces with correct IP addresses.

---

## 3. Phase 2 — IP Addressing & Routing

### Step 2.1 — Enable IP forwarding on the host (router)
```bash
sudo sysctl -w net.ipv4.ip_forward=1
echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.d/99-lab.conf
```

### Step 2.2 — Test web tier connectivity
```bash
# From host to web namespaces
ping -c 2 10.10.0.11
ping -c 2 10.10.0.12
ping -c 2 10.10.0.13

# Between web namespaces (via bridge)
sudo ip netns exec web1 ping -c 2 10.10.0.12
sudo ip netns exec web2 ping -c 2 10.10.0.13
```

### Step 2.3 — Test data tier connectivity
```bash
ping -c 2 10.10.1.10
```

### Step 2.4 — Add inter-tier routing
```bash
# Web namespaces need a route to the data tier
for i in 1 2 3; do
    sudo ip netns exec web${i} ip route add 10.10.1.0/24 via 10.10.0.1
done

# Data namespace needs a route to the web tier
sudo ip netns exec db1 ip route add 10.10.0.0/24 via 10.10.1.1
```

### Step 2.5 — Verify cross-tier connectivity
```bash
# Web to DB
sudo ip netns exec web1 ping -c 2 10.10.1.10

# DB to Web
sudo ip netns exec db1 ping -c 2 10.10.0.11
```

> **✅ Checkpoint:** All namespaces can ping each other across both tiers.

---

## 4. Phase 3 — DNS Resolution

### Step 3.1 — Install dnsmasq as a lightweight DNS server
```bash
sudo apt install dnsmasq -y
sudo systemctl stop systemd-resolved 2>/dev/null || true
```

### Step 3.2 — Configure dnsmasq
```bash
sudo tee /etc/dnsmasq.d/lab.conf << 'EOF'
# Listen on both bridges
listen-address=10.10.0.1
listen-address=10.10.1.1
listen-address=127.0.0.1

# Custom DNS records
address=/web1.lab.local/10.10.0.11
address=/web2.lab.local/10.10.0.12
address=/web3.lab.local/10.10.0.13
address=/db1.lab.local/10.10.1.10
address=/lb.lab.local/10.10.0.1

# Forward external DNS
server=8.8.8.8
EOF

sudo systemctl restart dnsmasq
```

### Step 3.3 — Configure DNS in namespaces
```bash
for ns in web1 web2 web3 db1; do
    sudo mkdir -p /etc/netns/${ns}
    echo "nameserver 10.10.0.1" | sudo tee /etc/netns/${ns}/resolv.conf
done
```

### Step 3.4 — Test DNS resolution
```bash
# From a web namespace
sudo ip netns exec web1 nslookup db1.lab.local 10.10.0.1
sudo ip netns exec web1 nslookup web2.lab.local 10.10.0.1

# From the db namespace
sudo ip netns exec db1 nslookup web1.lab.local 10.10.1.1
```

> **✅ Checkpoint:** All namespaces can resolve each other by hostname.

---

## 5. Phase 4 — Firewall & NAT

### Step 5.1 — Set up basic iptables rules on the host (router)
```bash
# Flush existing rules
sudo iptables -F
sudo iptables -t nat -F

# Default policies
sudo iptables -P INPUT ACCEPT
sudo iptables -P FORWARD DROP    # Default deny forwarding
sudo iptables -P OUTPUT ACCEPT
```

### Step 5.2 — Allow web-tier traffic
```bash
# Allow web namespaces to communicate with each other
sudo iptables -A FORWARD -s 10.10.0.0/24 -d 10.10.0.0/24 -j ACCEPT

# Allow established/related connections
sudo iptables -A FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
```

### Step 5.3 — Allow web → DB but not DB → web (initiated)
```bash
# Web tier can initiate connections to DB tier
sudo iptables -A FORWARD -s 10.10.0.0/24 -d 10.10.1.0/24 -p tcp --dport 5432 -j ACCEPT

# Log and drop everything else
sudo iptables -A FORWARD -j LOG --log-prefix "FW-DROP: "
sudo iptables -A FORWARD -j DROP
```

### Step 5.4 — Set up NAT for internet access from namespaces
```bash
# Masquerade outbound traffic
sudo iptables -t nat -A POSTROUTING -s 10.10.0.0/24 -o eth0 -j MASQUERADE
sudo iptables -t nat -A POSTROUTING -s 10.10.1.0/24 -o eth0 -j MASQUERADE

# Allow forwarding for NAT
sudo iptables -I FORWARD -s 10.10.0.0/24 -o eth0 -j ACCEPT
sudo iptables -I FORWARD -s 10.10.1.0/24 -o eth0 -j ACCEPT
```

### Step 5.5 — Test the firewall
```bash
# This should WORK (web → DB on port 5432)
sudo ip netns exec web1 nc -zv 10.10.1.10 5432 2>&1 || echo "Connection refused (expected - no listener yet)"

# This should FAIL (DB → web not allowed to initiate)
sudo ip netns exec db1 ping -c 2 -W 2 10.10.0.11 && echo "FAIL: DB should not reach web" || echo "PASS: DB cannot reach web"
```

### Step 5.6 — View firewall rules and counters
```bash
sudo iptables -L FORWARD -v -n --line-numbers
sudo iptables -t nat -L -v -n
```

> **✅ Checkpoint:** Web can reach DB port 5432, DB cannot initiate to web, all other forwarding is dropped.

---

## 6. Phase 5 — Load Balancing with Nginx

### Step 6.1 — Start HTTP servers in web namespaces
```bash
for i in 1 2 3; do
    sudo ip netns exec web${i} bash -c "
        mkdir -p /tmp/web${i}
        echo '<h1>Response from web${i} (10.10.0.1${i})</h1>' > /tmp/web${i}/index.html
        cd /tmp/web${i} && python3 -m http.server 80 &
    "
    echo "Started HTTP server in web${i}"
done
```

### Step 6.2 — Verify individual servers
```bash
curl -s http://10.10.0.11/
curl -s http://10.10.0.12/
curl -s http://10.10.0.13/
```

### Step 6.3 — Install and configure Nginx as load balancer
```bash
sudo apt install nginx -y

sudo tee /etc/nginx/conf.d/lab-lb.conf << 'EOF'
upstream web_backends {
    server 10.10.0.11:80;
    server 10.10.0.12:80;
    server 10.10.0.13:80;
}

server {
    listen 8080;
    server_name lb.lab.local;

    location / {
        proxy_pass http://web_backends;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /health {
        access_log off;
        return 200 "OK\n";
        add_header Content-Type text/plain;
    }
}
EOF

# Remove default site to avoid port conflicts
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
```

### Step 6.4 — Test load balancing
```bash
echo "=== Testing round-robin load balancing ==="
for i in {1..9}; do
    echo -n "Request $i: "
    curl -s http://localhost:8080/ | grep -o 'web[0-9]'
done
```

### Step 6.5 — Test health endpoint
```bash
curl -s http://localhost:8080/health
```

> **✅ Checkpoint:** Requests to port 8080 are distributed across web1, web2, web3.

---

## 7. Phase 6 — TLS & Secure Communication

### Step 7.1 — Generate a self-signed CA
```bash
sudo mkdir -p /etc/lab-certs

# Generate CA key and certificate
sudo openssl req -x509 -newkey rsa:4096 -keyout /etc/lab-certs/ca.key \
  -out /etc/lab-certs/ca.crt -days 365 -nodes \
  -subj "/CN=Lab CA/O=DevOps Training"
```

### Step 7.2 — Generate a server certificate for the load balancer
```bash
# Generate server key
sudo openssl genrsa -out /etc/lab-certs/lb.key 2048

# Generate CSR
sudo openssl req -new -key /etc/lab-certs/lb.key \
  -out /etc/lab-certs/lb.csr \
  -subj "/CN=lb.lab.local/O=DevOps Training"

# Sign with CA
sudo openssl x509 -req -in /etc/lab-certs/lb.csr \
  -CA /etc/lab-certs/ca.crt -CAkey /etc/lab-certs/ca.key \
  -CAcreateserial -out /etc/lab-certs/lb.crt -days 365
```

### Step 7.3 — Configure Nginx with TLS
```bash
sudo tee /etc/nginx/conf.d/lab-lb-tls.conf << 'EOF'
server {
    listen 8443 ssl;
    server_name lb.lab.local;

    ssl_certificate     /etc/lab-certs/lb.crt;
    ssl_certificate_key /etc/lab-certs/lb.key;
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://web_backends;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

sudo nginx -t && sudo systemctl reload nginx
```

### Step 7.4 — Test HTTPS
```bash
# Using the CA cert for verification
curl -s --cacert /etc/lab-certs/ca.crt https://lb.lab.local:8443/ || \
curl -sk https://localhost:8443/

# Inspect the certificate
echo | openssl s_client -connect localhost:8443 -servername lb.lab.local 2>/dev/null | openssl x509 -noout -text | head -15
```

> **✅ Checkpoint:** HTTPS works on port 8443 with your self-signed certificate.

---

## 8. Phase 7 — Monitoring & Troubleshooting

### Step 7.1 — Capture traffic with tcpdump
```bash
# Capture HTTP traffic on the bridge
sudo tcpdump -i br-main 'tcp port 80' -nn -c 20 &

# Generate traffic
for i in {1..5}; do curl -s http://localhost:8080/ > /dev/null; done

# Wait and view captures
wait
```

### Step 7.2 — Monitor connections in real-time
```bash
# Watch active connections
watch -n 1 'ss -tnp | grep -E "8080|80"'
```

### Step 7.3 — Check iptables counters
```bash
sudo iptables -L FORWARD -v -n --line-numbers
# Note the packet/byte counters for each rule
```

### Step 7.4 — Simulate a failure and observe
```bash
# Kill one web server
sudo ip netns exec web2 pkill -f "python3 -m http.server"

# Test — Nginx should route around the failed backend
for i in {1..6}; do
    echo -n "Request $i: "
    curl -s --max-time 2 http://localhost:8080/ | grep -o 'web[0-9]' || echo "TIMEOUT"
done

# Restart the server
sudo ip netns exec web2 bash -c "cd /tmp/web2 && python3 -m http.server 80 &"
```

### Step 7.5 — Troubleshooting exercise
```bash
# Break something intentionally
sudo iptables -I FORWARD -s 10.10.0.12 -j DROP

# Diagnose: Why can't web2 respond?
sudo ip netns exec web2 ping -c 2 10.10.0.1   # Should fail
sudo iptables -L FORWARD -v -n | head -10       # Find the DROP rule

# Fix it
sudo iptables -D FORWARD -s 10.10.0.12 -j DROP
```

> **✅ Checkpoint:** You can capture packets, monitor connections, and diagnose firewall issues.

---

## 9. Phase 8 — Docker Networking Integration

### Step 8.1 — Create a Docker network
```bash
docker network create --driver bridge --subnet 172.20.0.0/24 lab-net
```

### Step 8.2 — Run containers on the network
```bash
docker run -d --name lab-web1 --network lab-net nginx:alpine
docker run -d --name lab-web2 --network lab-net nginx:alpine
docker run -d --name lab-redis --network lab-net redis:alpine
```

### Step 8.3 — Explore Docker networking internals
```bash
# Container IPs
docker inspect lab-web1 --format '{{.NetworkSettings.Networks.lab_net.IPAddress}}'

# DNS resolution between containers
docker exec lab-web1 ping -c 2 lab-redis

# Examine the Docker bridge
ip link show | grep docker
bridge link show
```

### Step 8.4 — Inspect the network namespace Docker creates
```bash
# Find the container's PID
PID=$(docker inspect lab-web1 --format '{{.State.Pid}}')

# Examine its network namespace
sudo nsenter -t $PID -n ip addr show
sudo nsenter -t $PID -n ip route show
sudo nsenter -t $PID -n cat /etc/resolv.conf
```

### Step 8.5 — Connect containers to multiple networks
```bash
docker network create --driver bridge --subnet 172.21.0.0/24 lab-data-net
docker network connect lab-data-net lab-redis

# Redis now has IPs in both networks
docker inspect lab-redis --format '{{range .NetworkSettings.Networks}}{{.IPAddress}} {{end}}'
```

### Step 8.6 — Clean up Docker resources
```bash
docker stop lab-web1 lab-web2 lab-redis
docker rm lab-web1 lab-web2 lab-redis
docker network rm lab-net lab-data-net
```

> **✅ Checkpoint:** You understand how Docker networking maps to Linux bridges and network namespaces.

---

## 10. Cleanup

```bash
echo "=== Cleaning up lab environment ==="

# Kill HTTP servers in namespaces
for i in 1 2 3; do
    sudo ip netns exec web${i} pkill -f "python3 -m http.server" 2>/dev/null || true
done

# Remove Nginx config
sudo rm -f /etc/nginx/conf.d/lab-lb.conf /etc/nginx/conf.d/lab-lb-tls.conf
sudo systemctl reload nginx

# Remove dnsmasq config
sudo rm -f /etc/dnsmasq.d/lab.conf
sudo systemctl restart dnsmasq 2>/dev/null || true

# Remove network namespaces
for ns in web1 web2 web3 db1; do
    sudo ip netns del $ns 2>/dev/null || true
    sudo rm -rf /etc/netns/${ns}
done

# Remove bridges
sudo ip link del br-main 2>/dev/null || true
sudo ip link del br-data 2>/dev/null || true

# Flush iptables rules
sudo iptables -F
sudo iptables -t nat -F
sudo iptables -P FORWARD ACCEPT

# Remove certificates
sudo rm -rf /etc/lab-certs

# Remove sysctl changes
sudo rm -f /etc/sysctl.d/99-lab.conf

echo "=== Cleanup complete ==="
```

---

## 11. Lab Validation Checklist

| Phase | Test | Expected Result | Pass? |
|-------|------|-----------------|-------|
| 1 | `ip netns list` shows 4 namespaces | web1, web2, web3, db1 | ☐ |
| 2 | web1 can ping web2 | `0% packet loss` | ☐ |
| 2 | web1 can ping db1 | `0% packet loss` | ☐ |
| 3 | DNS resolves `web1.lab.local` | Returns `10.10.0.11` | ☐ |
| 4 | web1 can reach db1:5432 | Connection attempt works | ☐ |
| 4 | db1 cannot ping web1 | `100% packet loss` | ☐ |
| 5 | `curl localhost:8080` cycles backends | web1, web2, web3 | ☐ |
| 6 | HTTPS works on :8443 | Valid TLS response | ☐ |
| 7 | tcpdump captures HTTP packets | Visible SYN/ACK | ☐ |
| 7 | Killing web2 doesn't break LB | Traffic routes around | ☐ |
| 8 | Docker containers resolve by name | Ping by container name | ☐ |

---

> **Lab Complete!** You've built a multi-tier network from scratch using Linux primitives.  
> **Related:** [Networking Handbook](../networking/networking_handbook.md) · [Networking Tasks](../tasks/networking/level_1.md)

[🏠 Home](../README.md) · [Labs](README.md)
