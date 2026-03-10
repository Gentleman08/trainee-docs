[🏠 Home](../../README.md) · [Tasks](../README.md) · [Networking Tasks](.)

# 🌐 Networking Tasks — Level 2 (🟡 Medium)

> **Objective:** Intermediate networking — packet capture, firewall management, DNS server setup, load balancing, and VPN.  
> **Prerequisites:** Completed Level 1, access to 2+ Linux VMs or Docker  
> **Time Estimate:** 5–6 hours total

---

## Table of Contents

1. [Packet Capture & Analysis with tcpdump](#1-packet-capture--analysis-with-tcpdump)
2. [Advanced DNS — Running Your Own DNS Server](#2-advanced-dns--running-your-own-dns-server)
3. [Firewall Zones with firewalld](#3-firewall-zones-with-firewalld)
4. [Network Namespaces & Virtual Networking](#4-network-namespaces--virtual-networking)
5. [Setting Up Nginx as a Reverse Proxy & Load Balancer](#5-setting-up-nginx-as-a-reverse-proxy--load-balancer)
6. [WireGuard VPN Tunnel Setup](#6-wireguard-vpn-tunnel-setup)
7. [TLS Certificate Inspection & Troubleshooting](#7-tls-certificate-inspection--troubleshooting)
8. [Network Performance Testing with iperf3](#8-network-performance-testing-with-iperf3)
9. [Docker Container Networking Deep Dive](#9-docker-container-networking-deep-dive)
10. [DHCP Server Setup & Troubleshooting](#10-dhcp-server-setup--troubleshooting)

---

## 1. Packet Capture & Analysis with tcpdump

### Objective
Capture and analyze network traffic to understand protocol flows.

### Key Files

| File / Tool | Purpose |
|-------------|---------|
| `tcpdump` | Command-line packet analyzer |
| `wireshark` | GUI packet analyzer (optional) |
| `.pcap` | Packet capture file format |

### Tasks

**1.1** Capture HTTP traffic on a specific interface:
```bash
sudo tcpdump -i eth0 'tcp port 80' -nn -c 20
```
- In another terminal, `curl http://example.com`
- Identify the TCP handshake (SYN → SYN-ACK → ACK) in the output

**1.2** Capture DNS queries:
```bash
sudo tcpdump -i eth0 'udp port 53' -nn -c 10
```
- In another terminal, `dig google.com`
- Identify the DNS query and response packets

**1.3** Save capture to a file for later analysis:
```bash
sudo tcpdump -i eth0 -w /tmp/capture.pcap -c 100
```
- Read the capture back:
```bash
tcpdump -r /tmp/capture.pcap -nn | head -20
```

**1.4** Capture only SYN packets (new connections):
```bash
sudo tcpdump -i eth0 'tcp[tcpflags] & (tcp-syn) != 0 and tcp[tcpflags] & (tcp-ack) == 0' -nn -c 10
```

**1.5** Capture traffic between two specific hosts:
```bash
sudo tcpdump -i eth0 'host 10.0.1.5 and host 10.0.1.10' -nn
```

**1.6** Filter and display HTTP GET requests:
```bash
sudo tcpdump -i eth0 -A 'tcp port 80 and (((ip[2:2] - ((ip[0]&0xf)<<2)) - ((tcp[12]&0xf0)>>2)) != 0)' | grep "GET"
```

### Verification
- You can capture a complete TCP handshake and identify SYN, SYN-ACK, ACK
- You can save captures to .pcap files and read them back
- You understand tcpdump filter syntax

---

## 2. Advanced DNS — Running Your Own DNS Server

### Objective
Set up a local DNS server using BIND9 and create custom DNS zones.

### Key Files

| File | Purpose |
|------|---------|
| `/etc/bind/named.conf.local` | BIND zone definitions |
| `/etc/bind/named.conf.options` | BIND server options |
| `/etc/bind/db.*` | Zone data files |

### Tasks

**2.1** Install BIND9:
```bash
sudo apt update && sudo apt install bind9 bind9-utils -y
```

**2.2** Configure a forward lookup zone for `devops.lab`:
```bash
# Edit zone configuration
sudo tee /etc/bind/named.conf.local << 'EOF'
zone "devops.lab" {
    type master;
    file "/etc/bind/db.devops.lab";
};
EOF
```

**2.3** Create the zone file:
```bash
sudo tee /etc/bind/db.devops.lab << 'EOF'
$TTL    604800
@       IN      SOA     ns1.devops.lab. admin.devops.lab. (
                              2024010101 ; Serial
                              604800     ; Refresh
                              86400      ; Retry
                              2419200    ; Expire
                              604800 )   ; Negative Cache TTL
;
@       IN      NS      ns1.devops.lab.
ns1     IN      A       10.0.1.5
app     IN      A       10.0.1.10
db      IN      A       10.0.1.20
web     IN      CNAME   app.devops.lab.
@       IN      MX  10  mail.devops.lab.
mail    IN      A       10.0.1.30
EOF
```

**2.4** Verify configuration and restart BIND:
```bash
sudo named-checkconf
sudo named-checkzone devops.lab /etc/bind/db.devops.lab
sudo systemctl restart bind9
```

**2.5** Test your DNS server:
```bash
dig @localhost app.devops.lab
dig @localhost web.devops.lab
dig @localhost devops.lab MX
```

**2.6** Configure a client to use your DNS server:
```bash
# Temporarily add to resolv.conf
echo "nameserver 10.0.1.5" | sudo tee /etc/resolv.conf
dig app.devops.lab +short
```

### Verification
- Your DNS server resolves A, CNAME, and MX records for `devops.lab`
- `dig` queries against your server return correct responses

---

## 3. Firewall Zones with firewalld

### Objective
Use firewalld's zone-based approach for more advanced firewall management.

### Tasks

**3.1** Install and start firewalld:
```bash
sudo apt install firewalld -y    # Debian/Ubuntu
sudo systemctl start firewalld
sudo systemctl enable firewalld
```

**3.2** List available zones:
```bash
sudo firewall-cmd --get-zones
sudo firewall-cmd --get-active-zones
```

**3.3** Add services to the default zone:
```bash
sudo firewall-cmd --zone=public --add-service=http --permanent
sudo firewall-cmd --zone=public --add-service=https --permanent
sudo firewall-cmd --zone=public --add-service=ssh --permanent
sudo firewall-cmd --reload
```

**3.4** Create a custom zone for database servers:
```bash
sudo firewall-cmd --new-zone=database --permanent
sudo firewall-cmd --reload
sudo firewall-cmd --zone=database --add-port=3306/tcp --permanent
sudo firewall-cmd --zone=database --add-port=5432/tcp --permanent
sudo firewall-cmd --zone=database --add-source=10.0.3.0/24 --permanent
sudo firewall-cmd --reload
```

**3.5** List all rules in a zone:
```bash
sudo firewall-cmd --zone=public --list-all
sudo firewall-cmd --zone=database --list-all
```

**3.6** Set up port forwarding:
```bash
sudo firewall-cmd --zone=public --add-forward-port=port=8080:proto=tcp:toport=80 --permanent
sudo firewall-cmd --reload
```

### Verification
- You have configured at least 2 zones with different rules
- You can add/remove services and ports to zones
- You understand the difference between `--permanent` and runtime rules

---

## 4. Network Namespaces & Virtual Networking

### Objective
Create isolated network environments using Linux network namespaces.

### Architecture
```
  ┌── Namespace: red ──┐    veth pair    ┌── Namespace: blue ─┐
  │  veth-red           │◄──────────────►│  veth-blue          │
  │  10.0.0.1/24       │                │  10.0.0.2/24        │
  └────────────────────┘                └─────────────────────┘
```

### Tasks

**4.1** Create two network namespaces:
```bash
sudo ip netns add red
sudo ip netns add blue
sudo ip netns list
```

**4.2** Create a veth pair and connect the namespaces:
```bash
sudo ip link add veth-red type veth peer name veth-blue
sudo ip link set veth-red netns red
sudo ip link set veth-blue netns blue
```

**4.3** Assign IP addresses inside each namespace:
```bash
sudo ip netns exec red ip addr add 10.0.0.1/24 dev veth-red
sudo ip netns exec red ip link set veth-red up
sudo ip netns exec red ip link set lo up

sudo ip netns exec blue ip addr add 10.0.0.2/24 dev veth-blue
sudo ip netns exec blue ip link set veth-blue up
sudo ip netns exec blue ip link set lo up
```

**4.4** Test connectivity between namespaces:
```bash
sudo ip netns exec red ping -c 4 10.0.0.2
sudo ip netns exec blue ping -c 4 10.0.0.1
```

**4.5** Verify isolation — host cannot reach namespace IPs:
```bash
ping -c 2 10.0.0.1    # Should fail from host
```

**4.6** Run a web server in one namespace and access from the other:
```bash
# Start a simple HTTP server in "red"
sudo ip netns exec red python3 -m http.server 8080 &

# Access from "blue"
sudo ip netns exec blue curl http://10.0.0.1:8080
```

**4.7** Clean up:
```bash
sudo ip netns del red
sudo ip netns del blue
```

### Verification
- Two namespaces can ping each other but are isolated from the host
- You understand that Docker containers use this same mechanism

---

## 5. Setting Up Nginx as a Reverse Proxy & Load Balancer

### Objective
Configure Nginx to load balance between multiple backend servers.

### Architecture
```
  Client ──► Nginx (LB on :80) ──┬──► Backend 1 (127.0.0.1:8081)
                                  ├──► Backend 2 (127.0.0.1:8082)
                                  └──► Backend 3 (127.0.0.1:8083)
```

### Tasks

**5.1** Start 3 simple backend servers:
```bash
# Terminal 1
python3 -c "
from http.server import HTTPServer, BaseHTTPRequestHandler
class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Backend 1')
HTTPServer(('127.0.0.1', 8081), H).serve_forever()
" &

# Terminal 2
python3 -c "
from http.server import HTTPServer, BaseHTTPRequestHandler
class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Backend 2')
HTTPServer(('127.0.0.1', 8082), H).serve_forever()
" &

# Terminal 3
python3 -c "
from http.server import HTTPServer, BaseHTTPRequestHandler
class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Backend 3')
HTTPServer(('127.0.0.1', 8083), H).serve_forever()
" &
```

**5.2** Install and configure Nginx as load balancer:
```bash
sudo apt install nginx -y

sudo tee /etc/nginx/conf.d/loadbalancer.conf << 'EOF'
upstream backends {
    server 127.0.0.1:8081;
    server 127.0.0.1:8082;
    server 127.0.0.1:8083;
}

server {
    listen 80;
    server_name localhost;
    
    location / {
        proxy_pass http://backends;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

sudo nginx -t && sudo systemctl reload nginx
```

**5.3** Test round-robin load balancing:
```bash
for i in {1..9}; do curl -s http://localhost; echo; done
```
- You should see responses cycling through Backend 1, 2, 3

**5.4** Try weighted load balancing:
```bash
# Edit the upstream block:
upstream backends {
    server 127.0.0.1:8081 weight=3;
    server 127.0.0.1:8082 weight=2;
    server 127.0.0.1:8083 weight=1;
}
```

**5.5** Add a health check endpoint (basic):
```bash
# Add to the server block:
location /health {
    access_log off;
    return 200 "OK";
}
```

### Verification
- Requests to port 80 are distributed across 3 backends
- Weighted distribution works as expected
- Health endpoint returns 200

---

## 6. WireGuard VPN Tunnel Setup

### Objective
Create a simple WireGuard VPN tunnel between two hosts (or namespaces).

### Tasks

**6.1** Install WireGuard:
```bash
sudo apt install wireguard -y
```

**6.2** Generate key pairs for both peers:
```bash
# Peer A
wg genkey | tee /tmp/peerA_private | wg pubkey > /tmp/peerA_public

# Peer B
wg genkey | tee /tmp/peerB_private | wg pubkey > /tmp/peerB_public
```

**6.3** Configure Peer A:
```bash
sudo tee /etc/wireguard/wg0.conf << EOF
[Interface]
PrivateKey = $(cat /tmp/peerA_private)
Address = 10.200.0.1/24
ListenPort = 51820

[Peer]
PublicKey = $(cat /tmp/peerB_public)
AllowedIPs = 10.200.0.2/32
EOF
```

**6.4** Configure Peer B (on second host):
```bash
sudo tee /etc/wireguard/wg0.conf << EOF
[Interface]
PrivateKey = $(cat /tmp/peerB_private)
Address = 10.200.0.2/24

[Peer]
PublicKey = $(cat /tmp/peerA_public)
AllowedIPs = 10.200.0.1/32
Endpoint = <PeerA_IP>:51820
EOF
```

**6.5** Start the tunnel on both peers:
```bash
sudo wg-quick up wg0
sudo wg show
```

**6.6** Test connectivity through the tunnel:
```bash
# From Peer A
ping -c 4 10.200.0.2

# From Peer B
ping -c 4 10.200.0.1
```

**6.7** Stop the tunnel:
```bash
sudo wg-quick down wg0
```

### Verification
- Both peers can ping each other through the VPN tunnel (10.200.0.x)
- `wg show` displays transfer statistics

---

## 7. TLS Certificate Inspection & Troubleshooting

### Objective
Inspect, verify, and troubleshoot TLS/SSL certificates.

### Tasks

**7.1** Check the TLS certificate of a website:
```bash
echo | openssl s_client -connect google.com:443 -servername google.com 2>/dev/null | openssl x509 -noout -text | head -30
```

**7.2** Check certificate expiry:
```bash
echo | openssl s_client -connect google.com:443 -servername google.com 2>/dev/null | openssl x509 -noout -dates
```

**7.3** View the full certificate chain:
```bash
echo | openssl s_client -connect google.com:443 -servername google.com -showcerts 2>/dev/null
```

**7.4** Generate a self-signed certificate:
```bash
openssl req -x509 -newkey rsa:2048 -keyout /tmp/key.pem -out /tmp/cert.pem -days 365 -nodes \
  -subj "/CN=myapp.local/O=DevOps Lab"
```

**7.5** Verify the self-signed certificate:
```bash
openssl x509 -in /tmp/cert.pem -noout -text
openssl x509 -in /tmp/cert.pem -noout -fingerprint
```

**7.6** Test TLS version support:
```bash
# Test TLS 1.2
openssl s_client -connect google.com:443 -tls1_2

# Test TLS 1.3
openssl s_client -connect google.com:443 -tls1_3
```

### Verification
- You can inspect any website's TLS certificate
- You can generate and verify self-signed certificates
- You understand certificate expiry dates and chain of trust

---

## 8. Network Performance Testing with iperf3

### Objective
Measure network bandwidth and throughput between two hosts.

### Tasks

**8.1** Install iperf3:
```bash
sudo apt install iperf3 -y
```

**8.2** Start an iperf3 server:
```bash
iperf3 -s
```

**8.3** Run a client test (from another host or terminal):
```bash
iperf3 -c <server-ip>
```
- Note the bandwidth achieved (Mbits/sec)

**8.4** Test with UDP traffic:
```bash
iperf3 -c <server-ip> -u -b 100M
```
- Note: packet loss percentage and jitter

**8.5** Test with multiple parallel streams:
```bash
iperf3 -c <server-ip> -P 4
```

**8.6** Test in reverse mode (server sends to client):
```bash
iperf3 -c <server-ip> -R
```

### Verification
- You can measure TCP and UDP throughput
- You understand bandwidth, jitter, and packet loss metrics

---

## 9. Docker Container Networking Deep Dive

### Objective
Explore Docker's networking model and connect containers across networks.

### Tasks

**9.1** List Docker networks:
```bash
docker network ls
```

**9.2** Inspect the default bridge network:
```bash
docker network inspect bridge
```

**9.3** Create a custom bridge network:
```bash
docker network create --driver bridge --subnet 172.20.0.0/24 mynet
```

**9.4** Run two containers on the custom network:
```bash
docker run -d --name web --network mynet nginx
docker run -d --name app --network mynet alpine sleep 3600
```

**9.5** Test container DNS resolution (custom networks have built-in DNS):
```bash
docker exec app ping -c 3 web    # Resolves by container name!
docker exec app nslookup web
```

**9.6** Inspect the container's network namespace:
```bash
docker exec web ip addr show
docker exec web ip route show
docker exec web cat /etc/resolv.conf
```

**9.7** Connect a container to multiple networks:
```bash
docker network create --driver bridge --subnet 172.21.0.0/24 mynet2
docker network connect mynet2 app
docker exec app ip addr show  # Now has IPs in both networks
```

**9.8** Clean up:
```bash
docker stop web app && docker rm web app
docker network rm mynet mynet2
```

### Verification
- Containers on the same custom network can resolve each other by name
- You understand bridge, host, and custom Docker networks
- You can connect a container to multiple networks

---

## 10. DHCP Server Setup & Troubleshooting

### Objective
Set up a DHCP server and understand the DORA process.

### Key Concepts
```
  DHCP DORA Process:
  D — Discover (client broadcasts "Who can give me an IP?")
  O — Offer    (server offers an IP address)
  R — Request  (client requests the offered IP)
  A — Acknowledge (server confirms the lease)
```

### Tasks

**10.1** Install ISC DHCP Server:
```bash
sudo apt install isc-dhcp-server -y
```

**10.2** Configure the DHCP server:
```bash
sudo tee /etc/dhcp/dhcpd.conf << 'EOF'
# DHCP Server Configuration
default-lease-time 600;
max-lease-time 7200;

subnet 10.0.1.0 netmask 255.255.255.0 {
    range 10.0.1.100 10.0.1.200;
    option routers 10.0.1.1;
    option domain-name-servers 8.8.8.8, 8.8.4.4;
    option domain-name "devops.lab";
}

# Static assignment for a specific MAC
host webserver {
    hardware ethernet AA:BB:CC:DD:EE:FF;
    fixed-address 10.0.1.50;
}
EOF
```

**10.3** Start the DHCP server:
```bash
sudo systemctl start isc-dhcp-server
sudo systemctl status isc-dhcp-server
```

**10.4** View DHCP leases:
```bash
cat /var/lib/dhcp/dhcpd.leases
```

**10.5** On a client, request an IP from the DHCP server:
```bash
sudo dhclient -v eth0
```

**10.6** Capture DHCP traffic to observe the DORA process:
```bash
sudo tcpdump -i eth0 'port 67 or port 68' -nn -vvv
```

### Verification
- DHCP server assigns IPs from the configured range
- You can observe the DORA process in packet captures
- Static reservations work for specified MAC addresses

---

> **Level 2 Complete!** You now have intermediate networking skills.  
> **Next:** [Level 3 — Advanced Networking Tasks](level_3.md)

[🏠 Home](../../README.md) · [Tasks](../README.md)
