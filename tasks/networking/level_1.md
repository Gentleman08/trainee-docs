[🏠 Home](../../README.md) · [Tasks](../README.md) · [Networking Tasks](.)

# 🌐 Networking Tasks — Level 1 (🟢 Easy)

> **Objective:** Build foundational networking skills — IP addressing, basic connectivity, DNS, and port awareness.  
> **Prerequisites:** Access to a Linux VM (Ubuntu/CentOS), basic terminal knowledge  
> **Time Estimate:** 3–4 hours total

---

## Table of Contents

1. [Network Interface Exploration](#1-network-interface-exploration)
2. [IP Address and Subnet Calculation](#2-ip-address-and-subnet-calculation)
3. [Connectivity Testing with Ping & Traceroute](#3-connectivity-testing-with-ping--traceroute)
4. [DNS Resolution Practice](#4-dns-resolution-practice)
5. [Port Discovery and Service Identification](#5-port-discovery-and-service-identification)
6. [ARP Table Exploration](#6-arp-table-exploration)
7. [Routing Table Analysis](#7-routing-table-analysis)
8. [Basic Firewall Rules (iptables)](#8-basic-firewall-rules-iptables)
9. [HTTP Request Analysis with curl](#9-http-request-analysis-with-curl)
10. [Network Configuration Files](#10-network-configuration-files)

---

## 1. Network Interface Exploration

### Objective
Learn to identify and understand your system's network interfaces.

### Key Concepts

| Concept | Description |
|---------|-------------|
| `lo` | Loopback interface (127.0.0.1 — talks to itself) |
| `eth0/ens33` | Ethernet interface (wired network) |
| `wlan0` | Wireless interface |
| `docker0` | Docker bridge interface |
| `veth*` | Virtual ethernet (container connections) |

### Tasks

**1.1** List all network interfaces with their IP addresses:
```bash
ip addr show
```
- Note down: interface name, IPv4 address, IPv6 address, MAC address, and state (UP/DOWN)

**1.2** Check the status and link details of your primary interface:
```bash
ip link show eth0
# or
ethtool eth0
```
- Record the speed, duplex mode, and link state

**1.3** View only IPv4 addresses (concise):
```bash
ip -4 addr show
```

**1.4** Bring an interface down and back up (use with caution — not on SSH!):
```bash
sudo ip link set eth0 down
# Verify it's down
ip link show eth0
# Bring it back up
sudo ip link set eth0 up
```

### Verification
- You should be able to identify at least 2 interfaces (loopback + physical)
- You should know the IP address, subnet mask, and MAC of each interface

---

## 2. IP Address and Subnet Calculation

### Objective
Practice CIDR notation and subnet calculation by hand and with tools.

### Key Concepts

| CIDR | Subnet Mask | Hosts | Block Size |
|------|-------------|-------|------------|
| /24 | 255.255.255.0 | 254 | 256 |
| /25 | 255.255.255.128 | 126 | 128 |
| /26 | 255.255.255.192 | 62 | 64 |
| /27 | 255.255.255.224 | 30 | 32 |
| /28 | 255.255.255.240 | 14 | 16 |

### Tasks

**2.1** Calculate the following by hand (write down your answers):
```
Given: 192.168.10.0/26
- Network address: ?
- Broadcast address: ?
- First usable IP: ?
- Last usable IP: ?
- Total usable hosts: ?
```

**2.2** Verify with `ipcalc` (install if needed):
```bash
sudo apt install ipcalc -y    # Debian/Ubuntu
# OR
sudo yum install ipcalc -y    # CentOS/RHEL

ipcalc 192.168.10.0/26
```

**2.3** Given `10.0.0.0/16`, calculate subnets for 4 departments:
```
Department A: needs 500 hosts → /? subnet
Department B: needs 200 hosts → /? subnet
Department C: needs 50 hosts  → /? subnet
Department D: needs 10 hosts  → /? subnet
```
- Find the smallest subnet that fits each department
- Ensure no overlapping ranges

**2.4** Determine if two IPs are on the same subnet:
```
IP 1: 10.0.5.100/22
IP 2: 10.0.7.200/22
Are they on the same subnet? Why or why not?
```

### Verification
- Answers for 2.1: Network=192.168.10.0, Broadcast=192.168.10.63, First=192.168.10.1, Last=192.168.10.62, Hosts=62
- Compare your hand calculations with `ipcalc` output

---

## 3. Connectivity Testing with Ping & Traceroute

### Objective
Use ping and traceroute to test network connectivity and diagnose path issues.

### Tasks

**3.1** Ping your default gateway:
```bash
# Find your gateway first
ip route | grep default

# Ping it
ping -c 4 <gateway-ip>
```
- Record: packets sent/received, min/avg/max RTT

**3.2** Ping an external host (Google DNS):
```bash
ping -c 4 8.8.8.8
```
- If this fails but gateway ping works, what does that tell you?

**3.3** Ping with specific packet size to test MTU:
```bash
# Standard packet
ping -c 4 -s 1472 8.8.8.8

# Large packet (may fail — MTU issue)
ping -c 4 -s 1500 8.8.8.8 -M do
```

**3.4** Trace the route to google.com:
```bash
traceroute google.com
# OR (uses ICMP)
traceroute -I google.com
```
- How many hops? Where do you see the biggest latency jump?

**3.5** Use `mtr` for a combined ping + traceroute:
```bash
sudo apt install mtr -y
mtr -r -c 10 google.com
```

### Verification
- You can reach your gateway, a public IP (8.8.8.8), and a domain (google.com)
- You understand why these 3 tests isolate different problems

---

## 4. DNS Resolution Practice

### Objective
Query DNS records and understand the resolution process.

### Tasks

**4.1** Look up the A record for google.com:
```bash
dig google.com A +short
```

**4.2** Look up MX (mail) records:
```bash
dig google.com MX
```
- What mail servers handle google.com email?

**4.3** Look up NS (nameserver) records:
```bash
dig google.com NS +short
```

**4.4** Query a specific DNS server:
```bash
# Query Google's DNS
dig @8.8.8.8 example.com

# Query Cloudflare's DNS
dig @1.1.1.1 example.com
```
- Do they return the same IP? Why or why not?

**4.5** Perform a reverse DNS lookup:
```bash
dig -x 8.8.8.8
```
- What domain name does 8.8.8.8 resolve to?

**4.6** Check your system's DNS resolver configuration:
```bash
cat /etc/resolv.conf
resolvectl status 2>/dev/null || systemd-resolve --status 2>/dev/null
```

**4.7** Trace the full DNS resolution path:
```bash
dig +trace example.com
```
- Identify: root servers, TLD servers, authoritative servers

### Verification
- You can query A, MX, NS, and PTR records
- You understand `/etc/resolv.conf` and which DNS server your system uses

---

## 5. Port Discovery and Service Identification

### Objective
Discover which services are running and on which ports.

### Tasks

**5.1** List all listening TCP ports:
```bash
ss -tlnp
```
- Identify at least 3 services and their ports

**5.2** List all listening UDP ports:
```bash
ss -ulnp
```

**5.3** Check if a specific port is open on a remote host:
```bash
# Check if SSH is open on your gateway
nc -zv <gateway-ip> 22

# Check if HTTP is open on google.com
nc -zv google.com 80
nc -zv google.com 443
```

**5.4** View all established connections:
```bash
ss -tpn state established
```
- What remote IPs are you connected to? What ports?

**5.5** Map common ports to services from memory:
```
Fill in the service for each port:
22  → ?
53  → ?
80  → ?
443 → ?
3306 → ?
5432 → ?
6379 → ?
```

### Verification
- You know the difference between `ss` and `netstat`
- You can identify at least 5 common port numbers and their services

---

## 6. ARP Table Exploration

### Objective
Understand ARP and how MAC addresses map to IP addresses.

### Tasks

**6.1** View the current ARP table:
```bash
ip neigh show
# or
arp -a
```
- How many entries are there? What state are they in (REACHABLE, STALE)?

**6.2** Ping a local host, then check ARP again:
```bash
ping -c 2 <local-ip>
ip neigh show | grep <local-ip>
```
- A new ARP entry should appear

**6.3** Clear a specific ARP entry and watch it re-learn:
```bash
sudo ip neigh del <ip> dev eth0
ip neigh show
ping -c 1 <ip>
ip neigh show
```

**6.4** Find the MAC address of your default gateway:
```bash
ip neigh show | grep $(ip route | grep default | awk '{print $3}')
```

### Verification
- You understand that ARP maps Layer 3 (IP) to Layer 2 (MAC)
- You can view, clear, and observe ARP learning

---

## 7. Routing Table Analysis

### Objective
Read and interpret the system routing table.

### Tasks

**7.1** Display the full routing table:
```bash
ip route show
```
- Identify: default route, local network routes, any special routes

**7.2** Find which route a specific destination would use:
```bash
ip route get 8.8.8.8
ip route get 10.0.1.5
ip route get 127.0.0.1
```

**7.3** Add a static route (temporary):
```bash
# Route traffic for 10.20.0.0/16 via gateway 10.0.1.1
sudo ip route add 10.20.0.0/16 via 10.0.1.1
ip route show | grep 10.20
```

**7.4** Remove the static route:
```bash
sudo ip route del 10.20.0.0/16
```

**7.5** Explain the output of `ip route show` for each line:
```
What does each part mean?
default via 10.0.1.1 dev eth0 proto dhcp metric 100
10.0.1.0/24 dev eth0 proto kernel scope link src 10.0.1.5
```

### Verification
- You can read and explain every field in the routing table
- You can add and remove static routes

---

## 8. Basic Firewall Rules (iptables)

### Objective
Create simple iptables rules to allow/deny traffic.

### Tasks

**8.1** View current firewall rules:
```bash
sudo iptables -L -n -v --line-numbers
```

**8.2** Allow SSH (port 22) from any source:
```bash
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
```

**8.3** Allow HTTP and HTTPS:
```bash
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
```

**8.4** Allow established connections:
```bash
sudo iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
```

**8.5** Allow loopback traffic:
```bash
sudo iptables -A INPUT -i lo -j ACCEPT
```

**8.6** Drop all other incoming traffic:
```bash
sudo iptables -A INPUT -j DROP
```

**8.7** List rules again to see the complete firewall:
```bash
sudo iptables -L -n -v --line-numbers
```

**8.8** Flush all rules (reset — important for recovery!):
```bash
sudo iptables -F
```

> **⚠️ Warning:** Always have console access (not just SSH) when experimenting with iptables, or ensure you have a rule allowing SSH BEFORE adding a DROP rule.

### Verification
- You can create, list, and flush iptables rules
- You understand the difference between ACCEPT, DROP, and REJECT

---

## 9. HTTP Request Analysis with curl

### Objective
Use curl to inspect HTTP requests and responses.

### Tasks

**9.1** Make a simple GET request:
```bash
curl http://example.com
```

**9.2** See full request/response headers:
```bash
curl -v http://example.com
```
- Identify: HTTP version, status code, content-type, server header

**9.3** See only response headers:
```bash
curl -I http://example.com
```

**9.4** Measure response time:
```bash
curl -o /dev/null -s -w "DNS: %{time_namelookup}s\nConnect: %{time_connect}s\nTLS: %{time_appconnect}s\nTotal: %{time_total}s\n" https://example.com
```

**9.5** Follow redirects:
```bash
curl -L http://google.com
# vs
curl http://google.com  # shows 301 redirect
```

**9.6** Make a POST request with JSON data:
```bash
curl -X POST https://httpbin.org/post \
  -H "Content-Type: application/json" \
  -d '{"name": "devops", "role": "engineer"}'
```

### Verification
- You can read HTTP status codes, headers, and response bodies
- You understand the difference between GET and POST requests

---

## 10. Network Configuration Files

### Objective
Understand the key network configuration files on Linux.

### Tasks

**10.1** Examine the hosts file:
```bash
cat /etc/hosts
```
- What does this file do? Add a custom entry:
```bash
echo "10.0.1.5 myserver.local" | sudo tee -a /etc/hosts
ping myserver.local
```

**10.2** Examine DNS resolver configuration:
```bash
cat /etc/resolv.conf
```
- What nameservers are configured?

**10.3** Check the hostname:
```bash
hostname
hostname -f
cat /etc/hostname
hostnamectl
```

**10.4** View the network interface configuration (varies by distro):
```bash
# Ubuntu/Debian (Netplan)
cat /etc/netplan/*.yaml

# CentOS/RHEL
cat /etc/sysconfig/network-scripts/ifcfg-eth0

# Newer systemd
networkctl list
networkctl status eth0
```

**10.5** Check the nsswitch configuration (name resolution order):
```bash
cat /etc/nsswitch.conf | grep hosts
```
- What order does the system check? (files → DNS?)

### Verification
- You know the purpose of `/etc/hosts`, `/etc/resolv.conf`, `/etc/hostname`, and `/etc/nsswitch.conf`
- You can add custom host entries

---

> **Level 1 Complete!** You now have foundational networking skills.  
> **Next:** [Level 2 — Intermediate Networking Tasks](level_2.md)

[🏠 Home](../../README.md) · [Tasks](../README.md)
