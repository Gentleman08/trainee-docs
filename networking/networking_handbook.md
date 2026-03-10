[🏠 Home](../README.md) · [Networking](README.md)

# 🌐 Computer Networking — Comprehensive DevOps/Cloud Handbook

> **Audience:** DevOps / Cloud Engineers & Trainees | **Focus:** Architecture, Mental Models, Production Troubleshooting  
> **Covers:** OSI/TCP-IP, Subnetting, DNS, HTTP, Firewalls, Load Balancers, VPNs, SDN, Container Networking, Cloud Networking  
> **Tip:** Sections build on each other — read sequentially first, then use TOC for reference.

---

## Table of Contents

1. [Why Networking Matters for DevOps](#1-why-networking-matters-for-devops)
2. [OSI Model & TCP/IP Model](#2-osi-model--tcpip-model)
3. [Physical & Data Link Layer — Ethernet, MAC, Switching](#3-physical--data-link-layer--ethernet-mac-switching)
4. [IP Addressing & Subnetting](#4-ip-addressing--subnetting)
5. [Routing Fundamentals](#5-routing-fundamentals)
6. [Transport Layer — TCP, UDP & Ports](#6-transport-layer--tcp-udp--ports)
7. [DNS — The Internet's Phone Book](#7-dns--the-internets-phone-book)
8. [HTTP/HTTPS Protocol Deep Dive](#8-httphttps-protocol-deep-dive)
9. [Firewalls & Network Security](#9-firewalls--network-security)
10. [Load Balancers & Reverse Proxies](#10-load-balancers--reverse-proxies)
11. [VPNs, Tunneling & Network Overlays](#11-vpns-tunneling--network-overlays)
12. [Network Troubleshooting Toolkit](#12-network-troubleshooting-toolkit)
13. [Cloud Networking — VPC, Subnets & Peering](#13-cloud-networking--vpc-subnets--peering)
14. [Container Networking — Docker & Kubernetes](#14-container-networking--docker--kubernetes)
15. [Network Monitoring & Observability](#15-network-monitoring--observability)
16. [Production Gotchas & Scenario-Based FAQ](#16-production-gotchas--scenario-based-faq)

---

## 1. Why Networking Matters for DevOps

### 1.1 Networking Is DevOps Infrastructure

As a DevOps/Cloud engineer, networking is **not optional — it's foundational**:

- Every microservice communicates over the network (HTTP, gRPC, message queues)
- Cloud infrastructure (VPCs, subnets, security groups) **is** networking
- CI/CD pipelines transfer artifacts, pull images, deploy across networks
- Kubernetes Services, Ingress, and CNI plugins are all networking abstractions
- Production incidents are frequently **network issues** (DNS, timeouts, MTU, firewalls)
- Zero-trust security models depend on deep networking understanding

> **Bottom line:** A DevOps engineer who can't troubleshoot networking is blind to 60% of production incidents.

### 1.2 What You'll Be Able to Do After This Handbook

```
  ┌─────────────────────────────────────────────────────────────────┐
  │  NETWORKING COMPETENCY PROGRESSION                              │
  │                                                                 │
  │  BEGINNER (Sections 1–6)                                        │
  │  ├── Explain OSI/TCP-IP layers with examples                    │
  │  ├── Calculate subnets and CIDR ranges from memory              │
  │  ├── Understand how packets traverse the internet               │
  │  └── Explain TCP handshake, UDP, and port allocation            │
  │                                                                 │
  │  INTERMEDIATE (Sections 7–11)                                   │
  │  ├── Debug DNS resolution issues in production                  │
  │  ├── Configure firewalls (iptables, security groups)            │
  │  ├── Design load balancer architectures (L4 vs L7)              │
  │  ├── Set up VPN tunnels and understand overlays                 │
  │  └── Analyze HTTP headers and TLS handshakes                    │
  │                                                                 │
  │  ADVANCED (Sections 12–16)                                      │
  │  ├── Troubleshoot any network issue systematically              │
  │  ├── Design cloud VPCs, peering, and transit gateways           │
  │  ├── Understand container networking (Docker bridge, K8s CNI)   │
  │  └── Monitor and observe network health in production           │
  └─────────────────────────────────────────────────────────────────┘
```

---

## 2. OSI Model & TCP/IP Model

### 2.1 The OSI 7-Layer Model — Mental Model

The OSI model is a **conceptual framework** that breaks network communication into 7 layers. Each layer has a specific job and communicates only with the layers directly above and below it.

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │                    OSI 7-LAYER MODEL                                 │
  │                                                                      │
  │  Layer  Name           Data Unit    Key Protocols/Devices            │
  │  ─────  ─────────────  ──────────   ─────────────────────────────    │
  │    7    Application    Data         HTTP, HTTPS, FTP, SSH, DNS,      │
  │                                     SMTP, SNMP, LDAP                 │
  │    6    Presentation   Data         SSL/TLS, JPEG, ASCII, JSON,      │
  │                                     Encryption, Compression          │
  │    5    Session        Data         NetBIOS, RPC, SOCKS,             │
  │                                     Session management               │
  │    4    Transport      Segment      TCP, UDP, QUIC                   │
  │                                     Port numbers                     │
  │    3    Network        Packet       IP (v4/v6), ICMP, ARP,           │
  │                                     Routers, Routing protocols       │
  │    2    Data Link      Frame        Ethernet, Wi-Fi (802.11),        │
  │                                     MAC addresses, Switches          │
  │    1    Physical       Bits         Cables, Fiber, Radio waves,      │
  │                                     Hubs, NICs                       │
  └──────────────────────────────────────────────────────────────────────┘
  
  Mnemonic: "All People Seem To Need Data Processing"
  (Application → Physical, top to bottom)
  
  Or reverse: "Please Do Not Throw Sausage Pizza Away"
  (Physical → Application, bottom to top)
```

### 2.2 How Data Flows Through the Layers — Encapsulation

```
  ┌─────────────────────────────────────────────────────────────────────┐
  │                     ENCAPSULATION / DE-ENCAPSULATION                │
  │                                                                     │
  │  SENDER (Encapsulation — adding headers)                            │
  │                                                                     │
  │  Application:  [HTTP Data: "GET /index.html"]                       │
  │       │                                                             │
  │  Transport:    [TCP Header | HTTP Data]              ← Segment      │
  │       │         src:52341 dst:80                                     │
  │  Network:      [IP Header | TCP Header | Data]       ← Packet      │
  │       │         src:10.0.1.5 dst:93.184.216.34                      │
  │  Data Link:    [Eth Header | IP | TCP | Data | FCS]  ← Frame       │
  │       │         src:AA:BB:CC dst:FF:EE:DD                           │
  │  Physical:     10110100101110010101011...             ← Bits        │
  │                                                                     │
  │  ═══════════════════ NETWORK (wire/wireless) ═══════════════════    │
  │                                                                     │
  │  RECEIVER (De-encapsulation — stripping headers)                    │
  │                                                                     │
  │  Physical:     10110100101110010101011...                            │
  │       │                                                             │
  │  Data Link:    [Eth Header | IP | TCP | Data | FCS]                 │
  │       │         ↳ check MAC, strip frame header                     │
  │  Network:      [IP Header | TCP Header | Data]                      │
  │       │         ↳ check IP, strip IP header                         │
  │  Transport:    [TCP Header | HTTP Data]                             │
  │       │         ↳ check port, reassemble, strip TCP                 │
  │  Application:  [HTTP Data: "GET /index.html"]                       │
  │                ↳ process request                                    │
  └─────────────────────────────────────────────────────────────────────┘
```

### 2.3 TCP/IP Model (The Practical Model)

The TCP/IP model is what the internet **actually uses**. It collapses the OSI model into 4 layers.

```
  ┌─────────────────────────────────────────────────────────────┐
  │   OSI Model (7 layers)          TCP/IP Model (4 layers)     │
  │   ──────────────────            ────────────────────────    │
  │                                                             │
  │   7. Application  ─┐                                        │
  │   6. Presentation  ├──────►  4. Application                 │
  │   5. Session      ─┘            (HTTP, DNS, SSH, FTP)       │
  │                                                             │
  │   4. Transport    ─────────► 3. Transport                   │
  │                                  (TCP, UDP)                 │
  │                                                             │
  │   3. Network      ─────────► 2. Internet                    │
  │                                  (IP, ICMP, ARP)            │
  │                                                             │
  │   2. Data Link    ─┐                                        │
  │   1. Physical     ─┴──────► 1. Network Access               │
  │                                  (Ethernet, Wi-Fi)          │
  └─────────────────────────────────────────────────────────────┘
```

> **DevOps Relevance:** You'll hear "Layer 4 load balancer" (TCP/transport) vs "Layer 7 load balancer" (HTTP/application). This is OSI terminology used daily in cloud infrastructure.

### 2.4 Which Layer Does What? — DevOps Quick Map

| When you're dealing with... | OSI Layer | Tool/Tech |
|---|---|---|
| Broken cable, NIC down | L1 Physical | `ethtool`, `ip link` |
| MAC address issues, VLAN tagging | L2 Data Link | `arp`, `bridge`, switch config |
| IP addressing, routing, subnets | L3 Network | `ip route`, VPC, security groups |
| TCP connections, ports, firewalls | L4 Transport | `ss`, `netstat`, `iptables`, NLB |
| TLS handshake, cert issues | L5-6 Session/Presentation | `openssl s_client`, `curl -v` |
| HTTP errors, DNS, API issues | L7 Application | `curl`, `dig`, `nslookup`, ALB |

> **⚠️ Gotcha:** When troubleshooting, **always start from the bottom** (L1 → L7). Is the cable plugged in? Is the interface up? Can you ping the gateway? Can you reach the IP? Is the port open? Is the service responding? Many engineers jump straight to L7 and waste hours debugging "application issues" that are really L3 routing problems.

---

## 3. Physical & Data Link Layer — Ethernet, MAC, Switching

### 3.1 Physical Layer — Cables, Signals & NICs

The physical layer deals with the actual transmission of raw bits over a medium.

| Medium | Speed | Max Distance | Use Case |
|--------|-------|-------------|----------|
| Cat5e (Copper) | 1 Gbps | 100m | Office, DC short runs |
| Cat6/6a (Copper) | 10 Gbps | 55-100m | DC server connections |
| Single-mode Fiber | 100 Gbps+ | 80+ km | Inter-DC, WAN links |
| Multi-mode Fiber | 10-100 Gbps | 300-550m | Intra-DC backbone |
| Wi-Fi 6 (802.11ax) | 9.6 Gbps theoretical | ~30m indoor | Client access |

### 3.2 MAC Addresses

Every network interface has a **MAC (Media Access Control) address** — a 48-bit hardware identifier burned into the NIC.

```
  MAC Address Structure:
  
  AA:BB:CC:DD:EE:FF
  ├──────┤├──────┤
  OUI       Device ID
  (Vendor)  (Unique per NIC)
  
  Example: 00:1A:2B:3C:4D:5E
           ├──────┤
           Intel Corp (OUI = 00:1A:2B)
  
  Special MACs:
  ┌──────────────────────────────────────────────┐
  │  FF:FF:FF:FF:FF:FF  =  Broadcast (all hosts)│
  │  01:xx:xx:xx:xx:xx  =  Multicast            │
  └──────────────────────────────────────────────┘
```

### 3.3 ARP — Address Resolution Protocol

ARP bridges Layer 2 (MAC) and Layer 3 (IP). It answers: "What MAC address has IP 10.0.1.5?"

```
  ┌──────────────┐                              ┌──────────────┐
  │  Host A       │                              │  Host B       │
  │  IP: 10.0.1.5│                              │  IP: 10.0.1.10│
  │  MAC: AA:AA   │                              │  MAC: BB:BB   │
  └──────┬───────┘                              └──────┬───────┘
         │                                             │
         │  1. ARP Request (broadcast):                │
         │  "Who has 10.0.1.10? Tell 10.0.1.5"        │
         │─────────────────────────────────────────────►│
         │                                             │
         │  2. ARP Reply (unicast):                    │
         │  "10.0.1.10 is at MAC BB:BB"                │
         │◄─────────────────────────────────────────────│
         │                                             │
         │  3. Host A caches: 10.0.1.10 → BB:BB        │
         │     Now sends frames directly to BB:BB      │
         │─────────────────────────────────────────────►│
```

```bash
# View ARP cache
arp -a
ip neigh show

# Clear ARP cache
sudo ip neigh flush all
```

> **⚠️ Gotcha (ARP Spoofing):** Attackers can send fake ARP replies to redirect traffic. This is a classic man-in-the-middle attack on LANs. Mitigation: Dynamic ARP Inspection (DAI) on switches, static ARP entries for critical servers.

### 3.4 Switches & VLANs

**Switches** operate at Layer 2 — they learn MAC addresses and forward frames only to the correct port (unlike hubs that flood all ports).

```
  ┌─────────────────────────────────────────────────────────────────┐
  │                    LAYER 2 SWITCH                                │
  │                                                                  │
  │  MAC Address Table:                                              │
  │  ┌──────────────┬──────────┐                                     │
  │  │ MAC Address   │ Port    │                                     │
  │  ├──────────────┼──────────┤                                     │
  │  │ AA:AA:AA      │ Port 1  │──── Host A (10.0.1.5)              │
  │  │ BB:BB:BB      │ Port 2  │──── Host B (10.0.1.10)             │
  │  │ CC:CC:CC      │ Port 3  │──── Host C (10.0.1.15)             │
  │  │ (unknown)     │ FLOOD   │──── all ports                      │
  │  └──────────────┴──────────┘                                     │
  │                                                                  │
  │  Frame for BB:BB → only sent to Port 2 (not flooded)            │
  │  Frame for unknown MAC → flooded to all ports (learn & forward) │
  └─────────────────────────────────────────────────────────────────┘
```

**VLANs (Virtual LANs)** — Logically segment a single physical switch into multiple broadcast domains:

```
  ┌─────────────────────────────────────────────────────────┐
  │  SINGLE PHYSICAL SWITCH — TWO VLANs                     │
  │                                                         │
  │  VLAN 10 (Engineering)        VLAN 20 (Finance)         │
  │  ┌─────────────────────┐      ┌─────────────────────┐   │
  │  │ Port 1: Host A      │      │ Port 5: Host D      │   │
  │  │ Port 2: Host B      │      │ Port 6: Host E      │   │
  │  │ Port 3: Host C      │      │ Port 7: Host F      │   │
  │  └─────────────────────┘      └─────────────────────┘   │
  │                                                         │
  │  ❌ Host A CANNOT reach Host D (different VLANs)        │
  │  ✅ Need a ROUTER (Layer 3) to communicate between them │
  │                                                         │
  │  Trunk Port (carries multiple VLANs with 802.1Q tags):  │
  │  Port 24 ──── to another switch (tagged frames)         │
  └─────────────────────────────────────────────────────────┘
```

> **DevOps Relevance:** Cloud VPCs are essentially VLANs on steroids. Understanding VLANs helps you design subnet isolation in AWS/Azure/GCP.

---

## 4. IP Addressing & Subnetting

### 4.1 IPv4 Address Structure

An IPv4 address is a **32-bit number** written in dotted-decimal notation: `192.168.1.100`

```
  IPv4 Address: 192.168.1.100
  
  Decimal:  192      .  168      .  1        .  100
  Binary:   11000000 .  10101000 .  00000001 .  01100100
            ├─ 8 bits ──┤─ 8 bits ──┤─ 8 bits ──┤─ 8 bits ─┤
            └──────────── 32 bits total ─────────────────────┘
  
  Network Part  │  Host Part
  (identifies   │  (identifies the specific
   the network) │   device on that network)
```

### 4.2 IP Address Classes (Legacy — Still Tested)

```
  ┌─────────────────────────────────────────────────────────────────┐
  │  CLASS   RANGE                MASK          NETWORKS   HOSTS    │
  │  ─────   ──────────────────   ────────────  ────────   ─────    │
  │  A       1.0.0.0–126.x.x.x   255.0.0.0     126        16.7M   │
  │  B       128.0.0.0–191.x.x.x 255.255.0.0   16,384     65,534  │
  │  C       192.0.0.0–223.x.x.x 255.255.255.0 2.1M       254     │
  │  D       224.0.0.0–239.x.x.x (multicast — no host addresses)  │
  │  E       240.0.0.0–255.x.x.x (experimental — reserved)        │
  │                                                                 │
  │  Special:                                                       │
  │  127.0.0.0/8    = Loopback (localhost)                          │
  │  0.0.0.0        = Default route / unspecified                   │
  │  255.255.255.255 = Limited broadcast                            │
  └─────────────────────────────────────────────────────────────────┘
```

### 4.3 Private IP Ranges (RFC 1918) — MUST MEMORIZE

```
  ┌─────────────────────────────────────────────────────────────────┐
  │  PRIVATE IP RANGES — Not routable on the public internet        │
  │                                                                 │
  │  Class A:  10.0.0.0    – 10.255.255.255    (10.0.0.0/8)       │
  │            = 16,777,216 addresses                               │
  │            Used: Cloud VPCs, large enterprises                  │
  │                                                                 │
  │  Class B:  172.16.0.0  – 172.31.255.255   (172.16.0.0/12)     │
  │            = 1,048,576 addresses                                │
  │            Used: Docker default (172.17.0.0/16)                 │
  │                                                                 │
  │  Class C:  192.168.0.0 – 192.168.255.255  (192.168.0.0/16)    │
  │            = 65,536 addresses                                   │
  │            Used: Home routers, small networks                   │
  │                                                                 │
  │  Also private (link-local):                                     │
  │  169.254.0.0/16  = APIPA (self-assigned when no DHCP)          │
  │  100.64.0.0/10   = Carrier-grade NAT (CGNAT)                   │
  └─────────────────────────────────────────────────────────────────┘
```

### 4.4 CIDR & Subnet Masks — The Critical Skill

**CIDR (Classless Inter-Domain Routing)** replaced classful addressing. The `/N` notation tells you how many bits are the network portion.

```
  192.168.1.0/24
  
  /24 means: first 24 bits = network, remaining 8 bits = hosts
  
  Subnet Mask: 255.255.255.0
  Binary:      11111111.11111111.11111111.00000000
               ├── network (24 bits) ────┤├ host ─┤
  
  Hosts available: 2^8 - 2 = 254
  (-2 because: network address = .0, broadcast = .255)
```

### 4.5 Subnet Cheat Sheet — MEMORIZE THIS

```
  ┌──────────────────────────────────────────────────────────────┐
  │  CIDR   Mask              Hosts   Usable   Block Size       │
  │  ────   ───────────────   ──────  ──────   ──────────       │
  │  /32    255.255.255.255   1       1        Single host      │
  │  /31    255.255.255.254   2       2*       Point-to-point   │
  │  /30    255.255.255.252   4       2        Smallest subnet  │
  │  /29    255.255.255.248   8       6        Small server grp │
  │  /28    255.255.255.240   16      14                        │
  │  /27    255.255.255.224   32      30                        │
  │  /26    255.255.255.192   64      62                        │
  │  /25    255.255.255.128   128     126                       │
  │  /24    255.255.255.0     256     254       Standard "C"    │
  │  /23    255.255.254.0     512     510                       │
  │  /22    255.255.252.0     1024    1022                      │
  │  /21    255.255.248.0     2048    2046                      │
  │  /20    255.255.240.0     4096    4094                      │
  │  /16    255.255.0.0       65536   65534     Standard "B"    │
  │  /8     255.0.0.0         16.7M   16.7M-2  Standard "A"    │
  │                                                              │
  │  Formula: Hosts = 2^(32 - prefix) - 2                       │
  │  Block size = 256 - last non-zero mask octet                │
  └──────────────────────────────────────────────────────────────┘
```

### 4.6 Subnetting Worked Example

**Problem:** Given `10.0.0.0/16`, create 4 subnets.

```
  Need 4 subnets → need 2 extra bits (2^2 = 4)
  Original: /16 → New: /16 + 2 = /18
  
  Subnet 1:  10.0.0.0/18    (10.0.0.1    – 10.0.63.254)
  Subnet 2:  10.0.64.0/18   (10.0.64.1   – 10.0.127.254)
  Subnet 3:  10.0.128.0/18  (10.0.128.1  – 10.0.191.254)
  Subnet 4:  10.0.192.0/18  (10.0.192.1  – 10.0.255.254)
  
  Each subnet: 2^(32-18) - 2 = 16,382 usable hosts
  
  Visual:
  10.0.0.0/16  ─────┬──── 10.0.0.0/18    (0–63)
                     ├──── 10.0.64.0/18   (64–127)
                     ├──── 10.0.128.0/18  (128–191)
                     └──── 10.0.192.0/18  (192–255)
```

### 4.7 IPv6 — The Future (And Present)

```
  IPv6 Address: 2001:0db8:85a3:0000:0000:8a2e:0370:7334
  
  ┌──────────────────────────────────────────────────────────────┐
  │  IPv4 vs IPv6                                                │
  │  ─────────────────────────────────────────────────────────   │
  │  IPv4: 32 bits  = 4.3 billion addresses (exhausted!)        │
  │  IPv6: 128 bits = 340 undecillion addresses                  │
  │                                                              │
  │  IPv4: 192.168.1.1                                          │
  │  IPv6: 2001:db8:85a3::8a2e:370:7334                        │
  │        (:: means consecutive zero groups omitted)            │
  │                                                              │
  │  Special IPv6:                                               │
  │  ::1          = loopback (like 127.0.0.1)                    │
  │  ::           = unspecified (like 0.0.0.0)                   │
  │  fe80::/10    = link-local (like 169.254.x.x)               │
  │  fc00::/7     = unique-local (like RFC 1918 private)        │
  │  2000::/3     = global unicast (public internet)            │
  └──────────────────────────────────────────────────────────────┘
```

> **DevOps Relevance:** AWS VPCs support dual-stack (IPv4 + IPv6). Kubernetes pods can be IPv6-only. You'll encounter IPv6 in production — don't ignore it.

### 4.8 NAT — Network Address Translation

```
  ┌───────────────────────────────────────────────────────────────────┐
  │  NAT — Private IPs ↔ Public IPs                                   │
  │                                                                   │
  │  Private Network              NAT Device            Internet      │
  │  ┌──────────────┐            ┌──────────┐          ┌──────────┐  │
  │  │ 10.0.1.5     │──┐        │          │          │          │  │
  │  │ (port 52341) │  │        │  Public  │          │  Server  │  │
  │  └──────────────┘  ├───────►│  IP:     │─────────►│  93.184  │  │
  │  ┌──────────────┐  │        │  203.0.  │          │  .216.34 │  │
  │  │ 10.0.1.10    │──┤        │  113.5   │          │          │  │
  │  │ (port 48832) │  │        │          │◄─────────│          │  │
  │  └──────────────┘  ├───────►│  NAT     │          └──────────┘  │
  │  ┌──────────────┐  │        │  Table:  │                        │
  │  │ 10.0.1.15    │──┘        │ 10.0.1.5│                        │
  │  │ (port 33210) │           │ :52341  →│                        │
  │  └──────────────┘           │ 203.0.  │                        │
  │                             │ 113.5   │                        │
  │  3 private IPs share        │ :61234  │                        │
  │  1 public IP (PAT/NAPT)     └──────────┘                        │
  └───────────────────────────────────────────────────────────────────┘
  
  Types:
  • SNAT (Source NAT)  — outbound: private → public (most common)
  • DNAT (Destination NAT) — inbound: public → private (port forwarding)
  • PAT/NAPT (Port Address Translation) — many-to-one using ports
```

> **DevOps Relevance:** AWS NAT Gateway, Azure NAT Gateway — these are managed SNAT services. When your Lambda or private EC2 instance needs internet access, it goes through NAT.

---

## 5. Routing Fundamentals

### 5.1 What Is Routing?

Routing is the process of selecting a path for traffic across networks. Routers operate at **Layer 3** and make forwarding decisions based on the **destination IP address**.

```
  ┌──────────────────────────────────────────────────────────────────┐
  │                  ROUTING DECISION PROCESS                        │
  │                                                                  │
  │  Packet arrives at router with destination: 10.20.30.40          │
  │                                                                  │
  │  Router checks routing table:                                    │
  │  ┌─────────────────┬───────────────┬─────────────┬─────────────┐ │
  │  │ Destination      │ Mask          │ Next Hop    │ Interface   │ │
  │  ├─────────────────┼───────────────┼─────────────┼─────────────┤ │
  │  │ 10.20.30.0      │ /24           │ 10.0.0.2    │ eth1        │ │ ← Match!
  │  │ 10.20.0.0       │ /16           │ 10.0.0.3    │ eth2        │ │
  │  │ 0.0.0.0         │ /0            │ 10.0.0.1    │ eth0        │ │ ← Default
  │  └─────────────────┴───────────────┴─────────────┴─────────────┘ │
  │                                                                  │
  │  Longest prefix match wins: /24 is more specific than /16        │
  │  → Forward to 10.0.0.2 via eth1                                 │
  └──────────────────────────────────────────────────────────────────┘
```

### 5.2 Static vs Dynamic Routing

```
  ┌──────────────────────────────────┬──────────────────────────────────┐
  │  STATIC ROUTING                  │  DYNAMIC ROUTING                  │
  │                                  │                                  │
  │  Manually configured             │  Routers exchange info           │
  │  ip route add 10.0.2.0/24       │  automatically via protocols     │
  │    via 10.0.1.1                  │                                  │
  │                                  │  ┌──────────────────────────┐    │
  │  ✅ Simple, predictable          │  │ Interior (within AS):    │    │
  │  ✅ Low overhead                 │  │ • OSPF (link-state)      │    │
  │  ❌ Doesn't scale               │  │ • RIP (distance-vector)  │    │
  │  ❌ No failover                  │  │ • EIGRP (Cisco hybrid)   │    │
  │  ❌ Manual updates               │  │                          │    │
  │                                  │  │ Exterior (between AS):   │    │
  │  Use: small networks,            │  │ • BGP (path-vector)      │    │
  │  default routes, cloud VPCs      │  │   (runs the internet!)   │    │
  │                                  │  └──────────────────────────┘    │
  │                                  │                                  │
  │                                  │  ✅ Auto-adapts to failures     │
  │                                  │  ✅ Scales to large networks    │
  │                                  │  ❌ Complex configuration       │
  │                                  │  ❌ CPU/memory overhead         │
  └──────────────────────────────────┴──────────────────────────────────┘
```

### 5.3 Default Gateway — The Exit Door

Every host has a **default gateway** — the router it sends packets to when the destination is not on the local network.

```bash
# View routing table
ip route show
# Output example:
# default via 10.0.1.1 dev eth0      ← default gateway
# 10.0.1.0/24 dev eth0 proto kernel  ← local network (direct)
# 172.17.0.0/16 dev docker0          ← Docker bridge network

# Add a static route
sudo ip route add 10.20.0.0/16 via 10.0.1.254

# Delete a route
sudo ip route del 10.20.0.0/16

# Show route for a specific destination
ip route get 8.8.8.8
```

### 5.4 BGP — The Protocol That Runs the Internet

```
  ┌─────────────────────────────────────────────────────────────────┐
  │  BGP — BORDER GATEWAY PROTOCOL                                  │
  │                                                                 │
  │  The internet is a network of Autonomous Systems (AS)           │
  │  Each AS has a unique number (ASN)                              │
  │  BGP is how AS's tell each other which IP ranges they own       │
  │                                                                 │
  │  ┌──────────┐     eBGP     ┌──────────┐     eBGP     ┌────────┐│
  │  │  AS 64501│◄────────────►│  AS 64502│◄────────────►│AS 64503││
  │  │  (ISP A) │              │  (ISP B) │              │(Google)││
  │  │ 203.0.   │    iBGP      │  198.51. │              │8.8.8.0 ││
  │  │ 113.0/24 │   (within    │  100.0/24│              │/24     ││
  │  └──────────┘    same AS)  └──────────┘              └────────┘│
  │                                                                 │
  │  When AS 64503 announces 8.8.8.0/24:                           │
  │  → ISP B learns: "To reach 8.8.8.0/24, go through AS 64503"   │
  │  → ISP A learns: "To reach 8.8.8.0/24, go through AS 64502    │
  │                    then AS 64503" (AS path: 64502 64503)        │
  └─────────────────────────────────────────────────────────────────┘
```

> **DevOps Relevance:** AWS Direct Connect, Azure ExpressRoute, and GCP Cloud Interconnect all use BGP to peer with your on-premises network. Understanding BGP path selection matters for hybrid cloud architectures.

---

## 6. Transport Layer — TCP, UDP & Ports

### 6.1 TCP vs UDP — The Fundamental Choice

```
  ┌──────────────────────────────────────────────────────────────────┐
  │              TCP vs UDP — Head-to-Head                            │
  │                                                                  │
  │  TCP (Transmission Control Protocol)   UDP (User Datagram Proto) │
  │  ────────────────────────────────────  ───────────────────────── │
  │  ✅ Reliable (guaranteed delivery)     ❌ Unreliable (best effort)│
  │  ✅ Ordered (sequence numbers)         ❌ No ordering             │
  │  ✅ Error-checked (checksums + retx)   ✅ Checksums only         │
  │  ✅ Flow control (window sizing)       ❌ No flow control        │
  │  ✅ Congestion control                 ❌ No congestion control  │
  │  ❌ Slower (overhead of guarantees)    ✅ Fast (minimal overhead)│
  │  ❌ Higher latency (handshake)         ✅ Low latency            │
  │                                                                  │
  │  Used for:                             Used for:                 │
  │  • HTTP/HTTPS (web)                    • DNS (queries)           │
  │  • SSH, FTP                            • DHCP                    │
  │  • SMTP (email)                        • Video streaming         │
  │  • Database connections                • VoIP / gaming           │
  │  • Any data that MUST arrive           • SNMP monitoring         │
  │                                        • NTP (time sync)         │
  │                                        • Any data where speed    │
  │                                          beats reliability       │
  └──────────────────────────────────────────────────────────────────┘
```

### 6.2 TCP Three-Way Handshake

```
  ┌──────────────┐                              ┌──────────────┐
  │   Client     │                              │    Server    │
  │              │                              │ (listening   │
  │              │   1. SYN (seq=100)           │  on port 80) │
  │  CLOSED →    │─────────────────────────────►│              │
  │  SYN_SENT    │                              │  LISTEN →    │
  │              │   2. SYN-ACK (seq=300,       │  SYN_RCVD    │
  │              │      ack=101)                │              │
  │  ESTABLISHED │◄─────────────────────────────│              │
  │              │                              │              │
  │              │   3. ACK (ack=301)           │              │
  │              │─────────────────────────────►│  ESTABLISHED │
  │              │                              │              │
  │              │   Data transfer begins...    │              │
  │              │◄────────────────────────────►│              │
  └──────────────┘                              └──────────────┘
  
  The "three-way handshake":
  1. Client → Server:  SYN         "I want to connect"
  2. Server → Client:  SYN-ACK    "OK, I acknowledge"
  3. Client → Server:  ACK         "Confirmed, let's talk"
```

### 6.3 TCP Connection Termination (Four-Way)

```
  ┌──────────────┐                              ┌──────────────┐
  │   Client     │                              │    Server    │
  │              │   1. FIN                     │              │
  │              │─────────────────────────────►│              │
  │  FIN_WAIT_1  │                              │  CLOSE_WAIT  │
  │              │   2. ACK                     │              │
  │  FIN_WAIT_2  │◄─────────────────────────────│              │
  │              │                              │              │
  │              │   3. FIN                     │              │
  │              │◄─────────────────────────────│  LAST_ACK    │
  │  TIME_WAIT   │                              │              │
  │              │   4. ACK                     │              │
  │              │─────────────────────────────►│  CLOSED      │
  │              │                              │              │
  │  (wait 2×MSL)│                              │              │
  │  CLOSED      │                              │              │
  └──────────────┘                              └──────────────┘
```

> **⚠️ Gotcha (TIME_WAIT):** The `TIME_WAIT` state lasts 60 seconds (2×MSL) by default. On busy servers handling many short connections, this can exhaust available ports. You'll see this as "address already in use" errors. Fix: `net.ipv4.tcp_tw_reuse = 1` in sysctl, or use connection pooling.

### 6.4 Well-Known Ports — MUST MEMORIZE

```
  ┌──────────────────────────────────────────────────────────────┐
  │  PORT RANGES                                                 │
  │  0–1023:     Well-known (system) — need root to bind        │
  │  1024–49151: Registered (applications)                       │
  │  49152–65535: Dynamic/ephemeral (client-side, auto-assigned)│
  │                                                              │
  │  PORT    SERVICE           PROTOCOL    DevOps Context        │
  │  ────    ────────────────  ──────────  ─────────────────     │
  │  20/21   FTP (data/ctrl)   TCP         Legacy file transfer  │
  │  22      SSH                TCP         Remote access, SCP   │
  │  25      SMTP               TCP         Email sending        │
  │  53      DNS                TCP/UDP     Name resolution      │
  │  67/68   DHCP (srv/cli)    UDP         IP assignment         │
  │  80      HTTP               TCP         Web traffic          │
  │  110     POP3               TCP         Email retrieval      │
  │  123     NTP                UDP         Time sync            │
  │  143     IMAP               TCP         Email retrieval      │
  │  161/162 SNMP (query/trap) UDP         Monitoring            │
  │  389     LDAP               TCP         Directory services   │
  │  443     HTTPS              TCP         Encrypted web        │
  │  465     SMTPS              TCP         Encrypted email      │
  │  514     Syslog             UDP         Centralized logging  │
  │  636     LDAPS              TCP         Encrypted LDAP       │
  │  993     IMAPS              TCP         Encrypted IMAP       │
  │  995     POP3S              TCP         Encrypted POP3       │
  │  3306    MySQL              TCP         Database             │
  │  3389    RDP                TCP         Windows remote       │
  │  5432    PostgreSQL         TCP         Database             │
  │  5672    RabbitMQ (AMQP)   TCP         Message queue        │
  │  6379    Redis              TCP         Cache/DB             │
  │  6443    K8s API Server     TCP         Kubernetes           │
  │  8080    HTTP Alt           TCP         Dev servers, proxies │
  │  8443    HTTPS Alt          TCP         Dev/admin HTTPS      │
  │  9090    Prometheus         TCP         Monitoring           │
  │  27017   MongoDB            TCP         Database             │
  └──────────────────────────────────────────────────────────────┘
```

---

## 7. DNS — The Internet's Phone Book

### 7.1 What DNS Does

DNS (Domain Name System) translates human-readable domain names to IP addresses.

```
  User types: www.example.com
       │
       ▼
  DNS resolves: www.example.com → 93.184.216.34
       │
       ▼
  Browser connects to 93.184.216.34:443
```

### 7.2 DNS Record Types

| Record | Purpose | Example |
|--------|---------|---------|
| **A** | Domain → IPv4 address | `example.com → 93.184.216.34` |
| **AAAA** | Domain → IPv6 address | `example.com → 2606:2800:220:1:...` |
| **CNAME** | Alias → another domain | `www.example.com → example.com` |
| **MX** | Mail server for domain | `example.com → mail.example.com (priority 10)` |
| **NS** | Authoritative nameserver | `example.com → ns1.example.com` |
| **TXT** | Arbitrary text | SPF, DKIM, DMARC, domain verification |
| **SOA** | Start of Authority | Zone serial, refresh, retry, expire |
| **SRV** | Service locator | `_sip._tcp.example.com → sip.example.com:5060` |
| **PTR** | Reverse DNS (IP → domain) | `34.216.184.93 → example.com` |
| **CAA** | Certificate Authority Authorization | Which CAs can issue certs |

### 7.3 DNS Resolution Flow

```
  ┌─────────────────────────────────────────────────────────────────────┐
  │  DNS RESOLUTION: www.example.com                                    │
  │                                                                     │
  │  ┌──────────┐  1. Query       ┌──────────────────┐                  │
  │  │  Client   │────────────────►│ Recursive Resolver│                  │
  │  │ (Browser) │                 │ (ISP or 8.8.8.8) │                  │
  │  └──────────┘  8. Answer      └──────┬───────────┘                  │
  │       ▲         93.184.216.34        │                              │
  │       └──────────────────────────────┤                              │
  │                                      │ 2. "Who handles .com?"       │
  │                                      ▼                              │
  │                               ┌──────────────┐                      │
  │                               │ Root Servers  │  (13 clusters, a-m) │
  │                               │ . (root zone) │                      │
  │                               └──────┬───────┘                      │
  │                                      │ 3. "Ask .com TLD servers"    │
  │                                      ▼                              │
  │                               ┌──────────────┐                      │
  │                               │ TLD Servers   │                      │
  │                               │ (.com, .org,  │                      │
  │                               │  .io, .dev)   │                      │
  │                               └──────┬───────┘                      │
  │                                      │ 4. "Ask ns1.example.com"     │
  │                                      ▼                              │
  │                               ┌──────────────────┐                  │
  │                               │ Authoritative NS  │                  │
  │                               │ ns1.example.com   │                  │
  │                               │ (knows the answer)│                  │
  │                               └──────┬───────────┘                  │
  │                                      │ 5. "93.184.216.34"           │
  │                                      ▼                              │
  │                               (flows back through resolver)         │
  └─────────────────────────────────────────────────────────────────────┘
  
  The resolver CACHES the result based on TTL (Time To Live).
  Subsequent queries for the same domain are answered from cache.
```

### 7.4 DNS Caching & TTL

```
  ┌──────────────────────────────────────────────────────────┐
  │  DNS TTL (Time To Live) — How long to cache              │
  │                                                          │
  │  High TTL (e.g., 86400 = 24h):                          │
  │  ✅ Less DNS traffic, faster resolution                  │
  │  ❌ Slow to update — changes take hours to propagate     │
  │                                                          │
  │  Low TTL (e.g., 60 = 1 min):                            │
  │  ✅ Fast updates — great for failover                    │
  │  ❌ More DNS queries, slightly slower first resolution   │
  │                                                          │
  │  DevOps Strategy:                                        │
  │  • Normal operation: TTL 300–3600 (5min–1hr)            │
  │  • Before migration: Lower TTL to 60s, wait 24h         │
  │  • During migration: Switch DNS record                   │
  │  • After migration: Raise TTL back up                    │
  └──────────────────────────────────────────────────────────┘
```

### 7.5 DNS Troubleshooting Commands

```bash
# Basic lookup
dig example.com
dig +short example.com

# Query specific record types
dig example.com A
dig example.com MX
dig example.com TXT
dig example.com NS

# Query a specific DNS server
dig @8.8.8.8 example.com

# Trace full resolution path
dig +trace example.com

# Reverse DNS lookup
dig -x 93.184.216.34

# Check propagation from multiple resolvers
dig @8.8.8.8 example.com +short        # Google
dig @1.1.1.1 example.com +short        # Cloudflare
dig @208.67.222.222 example.com +short  # OpenDNS

# Check current resolver
cat /etc/resolv.conf
resolvectl status

# Flush local DNS cache
sudo systemd-resolve --flush-caches      # systemd-resolved
sudo resolvectl flush-caches              # newer syntax
```

> **⚠️ Gotcha (DNS Caching in Containers):** Alpine Linux (common in Docker images) uses `musl libc` which does NOT cache DNS. Each request triggers a full DNS lookup. In Kubernetes, this can overwhelm CoreDNS. Solution: Use `dnsPolicy: ClusterFirst` and tune CoreDNS caching, or use `ndots:2` to reduce search domain queries.

---

## 8. HTTP/HTTPS Protocol Deep Dive

### 8.1 HTTP Request/Response Cycle

```
  ┌──────────────┐                              ┌──────────────┐
  │   Client     │     HTTP Request              │    Server    │
  │   (Browser)  │─────────────────────────────►│  (Nginx)     │
  │              │                              │              │
  │              │  GET /api/users HTTP/1.1      │              │
  │              │  Host: api.example.com        │              │
  │              │  Accept: application/json     │              │
  │              │  Authorization: Bearer xxx    │              │
  │              │                              │              │
  │              │     HTTP Response             │              │
  │              │◄─────────────────────────────│              │
  │              │                              │              │
  │              │  HTTP/1.1 200 OK              │              │
  │              │  Content-Type: application/   │              │
  │              │    json                       │              │
  │              │  Cache-Control: max-age=60    │              │
  │              │                              │              │
  │              │  {"users": [...]}             │              │
  └──────────────┘                              └──────────────┘
```

### 8.2 HTTP Methods

| Method | Idempotent | Safe | Body | Purpose |
|--------|-----------|------|------|---------|
| **GET** | ✅ | ✅ | No | Retrieve resource |
| **HEAD** | ✅ | ✅ | No | Like GET but headers only |
| **POST** | ❌ | ❌ | Yes | Create resource |
| **PUT** | ✅ | ❌ | Yes | Replace entire resource |
| **PATCH** | ❌ | ❌ | Yes | Partial update |
| **DELETE** | ✅ | ❌ | Optional | Remove resource |
| **OPTIONS** | ✅ | ✅ | No | Discover allowed methods (CORS preflight) |

### 8.3 HTTP Status Codes — DevOps Must-Know

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  STATUS CODE FAMILIES                                            │
  │                                                                  │
  │  1xx — Informational                                             │
  │  ├── 100 Continue                                                │
  │  └── 101 Switching Protocols (WebSocket upgrade)                 │
  │                                                                  │
  │  2xx — Success                                                   │
  │  ├── 200 OK                                                      │
  │  ├── 201 Created (POST success)                                  │
  │  ├── 202 Accepted (async processing started)                     │
  │  └── 204 No Content (DELETE success)                             │
  │                                                                  │
  │  3xx — Redirection                                               │
  │  ├── 301 Moved Permanently (SEO — update links)                  │
  │  ├── 302 Found (temporary redirect)                              │
  │  ├── 304 Not Modified (cache hit — no body sent)                 │
  │  └── 307 Temporary Redirect (preserves method)                   │
  │                                                                  │
  │  4xx — Client Error                                              │
  │  ├── 400 Bad Request (malformed syntax)                          │
  │  ├── 401 Unauthorized (no/invalid credentials)                   │
  │  ├── 403 Forbidden (authenticated but not authorized)            │
  │  ├── 404 Not Found                                               │
  │  ├── 405 Method Not Allowed                                      │
  │  ├── 408 Request Timeout                                         │
  │  ├── 413 Payload Too Large                                       │
  │  ├── 429 Too Many Requests (rate limited)                        │
  │  └── 499 Client Closed Request (Nginx-specific)                  │
  │                                                                  │
  │  5xx — Server Error                                              │
  │  ├── 500 Internal Server Error (generic crash)                   │
  │  ├── 502 Bad Gateway (upstream returned invalid response)        │
  │  ├── 503 Service Unavailable (overloaded/maintenance)            │
  │  ├── 504 Gateway Timeout (upstream didn't respond in time)       │
  │  └── 520-527 Cloudflare-specific errors                          │
  └──────────────────────────────────────────────────────────────────┘
```

### 8.4 HTTPS & TLS Handshake

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │  TLS 1.3 HANDSHAKE (simplified — 1 round trip!)                      │
  │                                                                      │
  │  Client                                         Server               │
  │    │                                              │                   │
  │    │  1. ClientHello                              │                   │
  │    │  ├── Supported TLS versions                  │                   │
  │    │  ├── Cipher suites supported                 │                   │
  │    │  ├── Client random                           │                   │
  │    │  └── Key share (ECDHE public key)            │                   │
  │    │─────────────────────────────────────────────►│                   │
  │    │                                              │                   │
  │    │  2. ServerHello + Certificate + Verify       │                   │
  │    │  ├── Selected cipher suite                   │                   │
  │    │  ├── Server random                           │                   │
  │    │  ├── Key share (ECDHE public key)            │                   │
  │    │  ├── Certificate (proves server identity)    │                   │
  │    │  └── Finished (encrypted verification)       │                   │
  │    │◄─────────────────────────────────────────────│                   │
  │    │                                              │                   │
  │    │  Both sides now compute the same session key │                   │
  │    │  (from ECDHE key exchange)                   │                   │
  │    │                                              │                   │
  │    │  3. Client Finished (encrypted)              │                   │
  │    │─────────────────────────────────────────────►│                   │
  │    │                                              │                   │
  │    │  ═══ Encrypted Application Data ════════════ │                   │
  │    │◄────────────────────────────────────────────►│                   │
  └──────────────────────────────────────────────────────────────────────┘
  
  TLS 1.2: 2 round trips (separate key exchange + cipher negotiation)
  TLS 1.3: 1 round trip  (key exchange in ClientHello — faster!)
           0-RTT resumption possible (but replay risk)
```

### 8.5 HTTP/1.1 vs HTTP/2 vs HTTP/3

```
  ┌────────────────────┬────────────────────┬────────────────────┐
  │  HTTP/1.1           │  HTTP/2             │  HTTP/3             │
  │  (1997)             │  (2015)             │  (2022)             │
  ├────────────────────┼────────────────────┼────────────────────┤
  │  Text-based         │  Binary framing     │  Binary framing     │
  │  1 request per      │  Multiplexed        │  Multiplexed        │
  │  connection         │  (many streams on   │  (QUIC over UDP)    │
  │  (head-of-line      │   1 TCP connection)  │  (no TCP HOL       │
  │   blocking)         │  Server push        │   blocking)         │
  │  No compression     │  Header compression │  Header compression │
  │  of headers         │  (HPACK)            │  (QPACK)            │
  │                     │  Still has TCP HOL  │  Connection          │
  │                     │  blocking           │  migration (IP      │
  │                     │                     │  change survival)   │
  ├────────────────────┼────────────────────┼────────────────────┤
  │  Transport: TCP     │  Transport: TCP     │  Transport: QUIC    │
  │                     │                     │  (over UDP)         │
  └────────────────────┴────────────────────┴────────────────────┘
```

> **DevOps Relevance:** Modern load balancers (ALB, Cloudflare, Nginx) support HTTP/2 and HTTP/3. When you see `QUIC` or `Alt-Svc` headers, that's HTTP/3. Ensure your firewalls allow UDP 443 for HTTP/3.

---

## 9. Firewalls & Network Security

### 9.1 Firewall Types

```
  ┌─────────────────────────────────────────────────────────────────┐
  │  FIREWALL CLASSIFICATION                                        │
  │                                                                 │
  │  By Layer:                                                      │
  │  ├── Packet Filter (L3/L4) — iptables, nftables, ACLs         │
  │  │   Inspects: src/dst IP, src/dst port, protocol              │
  │  │   Fast but no application awareness                         │
  │  │                                                              │
  │  ├── Stateful Firewall (L3/L4) — firewalld, AWS SG             │
  │  │   Tracks connection state (NEW, ESTABLISHED, RELATED)       │
  │  │   Most common in production                                 │
  │  │                                                              │
  │  └── Application Firewall (L7) — WAF, ModSecurity              │
  │      Inspects HTTP content, SQL injection, XSS                 │
  │      AWS WAF, Cloudflare WAF, Azure Front Door                 │
  │                                                                 │
  │  By Deployment:                                                 │
  │  ├── Host-based: iptables, firewalld, Windows Firewall         │
  │  ├── Network-based: Hardware appliances, cloud security groups │
  │  └── Cloud-native: Security Groups, NACLs, NSGs               │
  └─────────────────────────────────────────────────────────────────┘
```

### 9.2 iptables — Linux Packet Filter

```
  ┌─────────────────────────────────────────────────────────────────┐
  │  IPTABLES — CHAIN PROCESSING                                    │
  │                                                                 │
  │  Incoming Packet                                                │
  │       │                                                         │
  │       ▼                                                         │
  │  ┌──────────┐     ┌───────────┐     ┌──────────┐               │
  │  │ PREROUTING│────►│  ROUTING  │────►│  INPUT   │──► Local     │
  │  │ (NAT,     │     │ DECISION  │     │ (filter) │    Process   │
  │  │  mangle)  │     └─────┬─────┘     └──────────┘               │
  │  └──────────┘           │                                       │
  │                         │ (not for us)                          │
  │                         ▼                                       │
  │                    ┌──────────┐     ┌───────────┐               │
  │                    │ FORWARD  │────►│POSTROUTING│──► Network    │
  │                    │ (filter) │     │ (NAT,     │               │
  │                    └──────────┘     │  mangle)  │               │
  │                                    └───────────┘               │
  │  Local Process                                                  │
  │       │                                                         │
  │       ▼                                                         │
  │  ┌──────────┐     ┌───────────┐                                 │
  │  │  OUTPUT  │────►│POSTROUTING│──► Network                      │
  │  │ (filter) │     │ (NAT)     │                                 │
  │  └──────────┘     └───────────┘                                 │
  └─────────────────────────────────────────────────────────────────┘
```

```bash
# List all rules
sudo iptables -L -n -v --line-numbers

# Allow SSH (port 22)
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Allow HTTP/HTTPS
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# Allow established connections (stateful)
sudo iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow loopback
sudo iptables -A INPUT -i lo -j ACCEPT

# Drop all other incoming traffic
sudo iptables -A INPUT -j DROP

# Allow outgoing
sudo iptables -A OUTPUT -j ACCEPT

# Save rules (RHEL)
sudo iptables-save > /etc/sysconfig/iptables
# Save rules (Debian)
sudo apt install iptables-persistent
sudo netfilter-persistent save
```

### 9.3 Cloud Security Groups vs NACLs

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  CLOUD FIREWALLS — AWS EXAMPLE (Azure NSG / GCP Firewall Rules) │
  │                                                                  │
  │  Security Group (SG)            Network ACL (NACL)               │
  │  ────────────────────            ──────────────────              │
  │  Operates at: Instance level    Operates at: Subnet level       │
  │  Stateful: ✅ (return traffic   Stateless: ❌ (must allow       │
  │   auto-allowed)                  both inbound AND outbound)     │
  │  Rules: ALLOW only              Rules: ALLOW and DENY           │
  │  Evaluation: All rules          Evaluation: In order (numbered) │
  │  Default: Deny all inbound      Default: Allow all              │
  │                                                                  │
  │  Example SG Rule:                                                │
  │  ┌──────────┬────────┬────────┬─────────────────────┐            │
  │  │ Type     │Protocol│Port    │Source                │            │
  │  ├──────────┼────────┼────────┼─────────────────────┤            │
  │  │ SSH      │TCP     │22      │10.0.0.0/8           │            │
  │  │ HTTP     │TCP     │80      │0.0.0.0/0            │            │
  │  │ HTTPS    │TCP     │443     │0.0.0.0/0            │            │
  │  │ Custom   │TCP     │3306    │sg-0abc1234 (another │            │
  │  │          │        │        │ SG — reference!)     │            │
  │  └──────────┴────────┴────────┴─────────────────────┘            │
  │                                                                  │
  │  Pro tip: SGs can reference OTHER SGs as source/destination.    │
  │  This is the foundation of least-privilege cloud networking.    │
  └──────────────────────────────────────────────────────────────────┘
```

> **⚠️ Gotcha:** Security Groups are **stateful** — if you allow inbound on port 80, return traffic is automatically allowed. NACLs are **stateless** — you must explicitly allow ephemeral ports (1024–65535) outbound for return traffic. Forgetting this causes "connection timeout" on HTTP but SG looks fine.

---

## 10. Load Balancers & Reverse Proxies

### 10.1 Why Load Balance?

```
  WITHOUT Load Balancer:              WITH Load Balancer:
  
  ┌──────────┐                        ┌──────────┐
  │ Clients  │                        │ Clients  │
  └────┬─────┘                        └────┬─────┘
       │                                   │
       ▼                                   ▼
  ┌──────────┐                        ┌──────────┐
  │ Server 1 │ ← single point        │   Load   │
  │ (all     │    of failure!         │ Balancer │
  │  traffic)│                        └──┬───┬───┘
  └──────────┘                           │   │
                                    ┌────▼┐ ┌▼────┐
                                    │Srv 1│ │Srv 2│  ← distributed
                                    └─────┘ └─────┘     + failover
```

### 10.2 L4 vs L7 Load Balancing

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  L4 (Transport) LOAD BALANCER     L7 (Application) LOAD BALANCER│
  │  ─────────────────────────────    ──────────────────────────────│
  │                                                                  │
  │  Sees: IP + Port                  Sees: Full HTTP request       │
  │  Decisions based on:              Decisions based on:            │
  │  • Source IP                      • URL path (/api/* → backend1)│
  │  • Destination port               • Host header (multi-tenant)  │
  │  • Protocol (TCP/UDP)             • HTTP method                 │
  │                                   • Headers, cookies            │
  │  ┌──────────────┐                • Request body                │
  │  │  TCP Packet   │                                              │
  │  │  src: 1.2.3.4 │                ┌──────────────────────────┐  │
  │  │  dst: 10.0.1.5│                │  GET /api/users HTTP/1.1 │  │
  │  │  port: 443    │                │  Host: app.example.com   │  │
  │  └──────────────┘                │  Cookie: session=abc123  │  │
  │                                   └──────────────────────────┘  │
  │  ✅ Fast (minimal processing)    ✅ Smart routing              │
  │  ✅ Protocol agnostic            ✅ SSL termination            │
  │  ❌ No content-based routing     ✅ Path-based routing         │
  │  ❌ No SSL termination           ✅ Header manipulation        │
  │                                   ❌ Higher latency            │
  │  AWS: NLB                         AWS: ALB                     │
  │  Azure: Azure LB                  Azure: App Gateway           │
  │  GCP: TCP/UDP LB                  GCP: HTTP(S) LB             │
  │  On-prem: HAProxy (TCP mode)     On-prem: Nginx, HAProxy      │
  └──────────────────────────────────────────────────────────────────┘
```

### 10.3 Load Balancing Algorithms

| Algorithm | How It Works | Best For |
|-----------|-------------|----------|
| **Round Robin** | Cycle through backends sequentially | Equal-capacity servers |
| **Weighted Round Robin** | More traffic to higher-weight servers | Mixed-capacity servers |
| **Least Connections** | Send to server with fewest active connections | Variable response times |
| **IP Hash** | Hash client IP → always same backend | Session persistence without cookies |
| **Random** | Random selection | Large, uniform pools |
| **Least Response Time** | Send to fastest responding backend | Performance-sensitive apps |

### 10.4 Health Checks

```
  ┌─────────────────────────────────────────────────────────────────┐
  │  HEALTH CHECK TYPES                                             │
  │                                                                 │
  │  L3/L4 (Ping/TCP):            L7 (HTTP):                       │
  │  ┌────────────────────┐       ┌─────────────────────────────┐   │
  │  │ Can I connect to   │       │ Does GET /health return     │   │
  │  │ port 80? (SYN-ACK) │       │ 200 OK with correct body?  │   │
  │  │                     │       │                             │   │
  │  │ Fast but shallow — │       │ Deeper but slower —         │   │
  │  │ port open ≠ app    │       │ verifies app is actually    │   │
  │  │ working             │       │ working correctly           │   │
  │  └────────────────────┘       └─────────────────────────────┘   │
  │                                                                 │
  │  Typical config:                                                │
  │  • Interval: 30 seconds (check every 30s)                      │
  │  • Threshold: 3 failures before marking unhealthy              │
  │  • Timeout: 5 seconds per check                                │
  │  • Path: /health or /healthz (Kubernetes convention)           │
  └─────────────────────────────────────────────────────────────────┘
```

> **⚠️ Gotcha (Health Check Cascading):** If your health check endpoint queries the database, and the DB is slow, ALL instances get marked unhealthy simultaneously → total outage. Design health checks in layers: `/health` = process alive, `/health/ready` = dependencies checked.

---

## 11. VPNs, Tunneling & Network Overlays

### 11.1 VPN Types

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  VPN TYPES                                                       │
  │                                                                  │
  │  Site-to-Site VPN:                                               │
  │  ┌──────────┐    Encrypted Tunnel (IPSec)    ┌──────────┐       │
  │  │ Office   │◄═══════════════════════════════►│  Cloud   │       │
  │  │ Network  │    (over public internet)       │  VPC     │       │
  │  │ 10.1.0.0 │                                │ 10.2.0.0 │       │
  │  └──────────┘                                └──────────┘       │
  │  Used for: Hybrid cloud, branch office connectivity             │
  │                                                                  │
  │  Client-to-Site VPN (Remote Access):                            │
  │  ┌──────────┐    Encrypted Tunnel             ┌──────────┐      │
  │  │ Laptop   │◄═══════════════════════════════►│  VPN     │      │
  │  │ (remote  │    (OpenVPN, WireGuard,         │  Gateway │      │
  │  │  worker) │     IPSec IKEv2)                │ → Corp   │      │
  │  └──────────┘                                └──────────┘      │
  │  Used for: Remote work, accessing private resources            │
  │                                                                  │
  │  Mesh VPN (Modern):                                             │
  │  ┌──────┐      ┌──────┐      ┌──────┐                           │
  │  │Node A│◄════►│Node B│◄════►│Node C│                           │
  │  └──┬───┘      └──────┘      └───┬──┘                           │
  │     └═══════════════════════════►┘                               │
  │  Every node connects to every other node directly               │
  │  Tools: WireGuard, Tailscale, Nebula, ZeroTier                 │
  └──────────────────────────────────────────────────────────────────┘
```

### 11.2 VPN Protocols Comparison

| Protocol | Speed | Security | Port | Use Case |
|----------|-------|----------|------|----------|
| **IPSec (IKEv2)** | Fast | Strong | UDP 500, 4500 | Site-to-site, enterprise |
| **OpenVPN** | Medium | Strong | TCP 443 or UDP 1194 | Client VPN, flexible |
| **WireGuard** | Very fast | Strong | UDP 51820 | Modern replacement for all above |
| **L2TP/IPSec** | Medium | Good | UDP 500, 1701, 4500 | Legacy, widely supported |
| **SSTP** | Medium | Good | TCP 443 | Windows environments |

> **DevOps Relevance:** AWS VPN uses IPSec. WireGuard is increasingly used for DevOps tooling (Tailscale for zero-trust access to staging environments).

### 11.3 Network Overlay — VXLAN

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  VXLAN (Virtual Extensible LAN)                                  │
  │                                                                  │
  │  Problem: VLANs are limited to 4,096 IDs (12-bit).             │
  │  VXLAN: 16 million virtual networks (24-bit VNI).              │
  │                                                                  │
  │  How it works: encapsulate L2 Ethernet frames inside L3 UDP    │
  │                                                                  │
  │  ┌─────────────────────────────────────────────────────────┐    │
  │  │  Outer IP │ Outer UDP │ VXLAN   │ Inner    │ Inner     │    │
  │  │  Header   │ Header    │ Header  │ Ethernet │ IP Packet │    │
  │  │           │ (dst:4789)│ (VNI:   │ Frame    │           │    │
  │  │           │           │  1001)  │          │           │    │
  │  └─────────────────────────────────────────────────────────┘    │
  │                                                                  │
  │  Used by: Docker overlay networks, Kubernetes CNI plugins       │
  │  (Flannel VXLAN mode, Calico VXLAN mode)                       │
  └──────────────────────────────────────────────────────────────────┘
```

---

## 12. Network Troubleshooting Toolkit

### 12.1 The Systematic Approach

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  NETWORK TROUBLESHOOTING — BOTTOM-UP METHODOLOGY                │
  │                                                                  │
  │  Step 1: Physical (L1)                                          │
  │  ├── Is the cable plugged in? Is the link light on?             │
  │  ├── ip link show — is the interface UP?                        │
  │  └── ethtool eth0 — link detected? speed? duplex?              │
  │                                                                  │
  │  Step 2: Data Link (L2)                                         │
  │  ├── arp -a — can we see the gateway's MAC?                     │
  │  └── Is VLAN tagging correct?                                   │
  │                                                                  │
  │  Step 3: Network (L3)                                           │
  │  ├── ip addr — do we have an IP?                                │
  │  ├── ping gateway — can we reach the default gateway?           │
  │  ├── ping 8.8.8.8 — can we reach the internet?                 │
  │  └── ip route — is the routing table correct?                   │
  │                                                                  │
  │  Step 4: Transport (L4)                                         │
  │  ├── ss -tlnp — is the service listening?                       │
  │  ├── telnet/nc host port — can we connect to the port?          │
  │  └── iptables -L — is the firewall blocking?                    │
  │                                                                  │
  │  Step 5: Application (L7)                                       │
  │  ├── curl -v http://host — does the service respond?            │
  │  ├── dig domain — does DNS resolve?                             │
  │  └── openssl s_client — is TLS working?                         │
  └──────────────────────────────────────────────────────────────────┘
```

### 12.2 Essential Commands

```bash
# === CONNECTIVITY ===
ping -c 4 10.0.1.1              # Basic connectivity
traceroute 10.0.1.1             # Path tracing
mtr -r 10.0.1.1                 # Combined ping + traceroute

# === DNS ===
dig example.com                  # Full DNS query
dig +short example.com           # Just the IP
nslookup example.com             # Alternative DNS lookup
host example.com                 # Simple DNS lookup

# === PORTS & CONNECTIONS ===
ss -tlnp                         # Listening TCP ports
ss -ulnp                         # Listening UDP ports
ss -s                            # Socket statistics summary
netstat -an | grep ESTABLISHED   # Active connections

# Test port connectivity
nc -zv 10.0.1.5 80              # Check if port 80 is open
telnet 10.0.1.5 443             # Telnet to port (alt method)
curl -v http://10.0.1.5/        # Full HTTP verbose output

# === ROUTING ===
ip route show                    # Routing table
ip route get 8.8.8.8            # Which route for specific dest

# === INTERFACES ===
ip addr show                     # All interfaces and IPs
ip link show                     # Interface status (up/down)
ethtool eth0                     # NIC details (speed, duplex)

# === PACKET CAPTURE ===
sudo tcpdump -i eth0 -n port 80            # Capture HTTP traffic
sudo tcpdump -i eth0 -n host 10.0.1.5      # Capture traffic to/from host
sudo tcpdump -i any -nn -w capture.pcap     # Capture to file for Wireshark

# === BANDWIDTH ===
iperf3 -s                        # Start iperf server
iperf3 -c 10.0.1.5              # Test bandwidth to server

# === TLS ===
openssl s_client -connect example.com:443 -servername example.com
# Shows: certificate chain, TLS version, cipher suite
```

### 12.3 tcpdump — The Swiss Army Knife

```bash
# Capture HTTP traffic on eth0
sudo tcpdump -i eth0 'tcp port 80' -nn -A

# Capture DNS queries
sudo tcpdump -i eth0 'udp port 53' -nn

# Capture SYN packets only (connection attempts)
sudo tcpdump -i eth0 'tcp[tcpflags] & (tcp-syn) != 0' -nn

# Capture traffic between two hosts
sudo tcpdump -i eth0 'host 10.0.1.5 and host 10.0.1.10' -nn

# Save to file for Wireshark analysis
sudo tcpdump -i eth0 -w /tmp/capture.pcap -c 1000
# Open in Wireshark: wireshark /tmp/capture.pcap
```

> **⚠️ Gotcha (tcpdump on production):** Running tcpdump without a filter (`sudo tcpdump -i eth0`) on a busy production server can overwhelm the terminal and potentially impact performance. ALWAYS use filters and limit captures with `-c` (count) or `-w` (write to file).

---

## 13. Cloud Networking — VPC, Subnets & Peering

### 13.1 VPC Architecture — Mental Model

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │  AWS VPC (Virtual Private Cloud) — Typical Production Layout        │
  │  CIDR: 10.0.0.0/16                                                 │
  │                                                                      │
  │  ┌─ Availability Zone A ──────────────────────────────────────────┐  │
  │  │                                                                │  │
  │  │  Public Subnet (10.0.1.0/24)      Private Subnet (10.0.3.0/24)│  │
  │  │  ┌─────────────────────────┐      ┌─────────────────────────┐  │  │
  │  │  │ • ALB (load balancer)   │      │ • App servers (EC2/ECS) │  │  │
  │  │  │ • NAT Gateway           │      │ • Containers            │  │  │
  │  │  │ • Bastion host          │      │ • No direct internet    │  │  │
  │  │  │ → Route: 0.0.0.0/0     │      │ → Route: 0.0.0.0/0     │  │  │
  │  │  │   via Internet Gateway  │      │   via NAT Gateway       │  │  │
  │  │  └─────────────────────────┘      └─────────────────────────┘  │  │
  │  │                                                                │  │
  │  │  Data Subnet (10.0.5.0/24)                                     │  │
  │  │  ┌─────────────────────────┐                                    │  │
  │  │  │ • RDS (databases)       │                                    │  │
  │  │  │ • ElastiCache (Redis)   │                                    │  │
  │  │  │ • No internet access    │                                    │  │
  │  │  │ → Route: local only     │                                    │  │
  │  │  └─────────────────────────┘                                    │  │
  │  └────────────────────────────────────────────────────────────────┘  │
  │                                                                      │
  │  ┌─ Availability Zone B ──────────────────────────────────────────┐  │
  │  │  (Mirror of AZ-A for high availability)                        │  │
  │  │  Public: 10.0.2.0/24 | Private: 10.0.4.0/24 | Data: 10.0.6.0 │  │
  │  └────────────────────────────────────────────────────────────────┘  │
  │                                                                      │
  │  ┌────────────────────────────┐                                      │
  │  │  Internet Gateway (IGW)    │── attached to VPC (one per VPC)     │
  │  └────────────────────────────┘                                      │
  └──────────────────────────────────────────────────────────────────────┘
```

### 13.2 Public vs Private Subnets

```
  ┌──────────────────────────────┬──────────────────────────────┐
  │  PUBLIC SUBNET               │  PRIVATE SUBNET               │
  │                              │                              │
  │  Has route to IGW:           │  No route to IGW:            │
  │  0.0.0.0/0 → igw-xxx        │  0.0.0.0/0 → nat-xxx        │
  │                              │  (goes through NAT GW)       │
  │  Instances get public IPs    │  Instances have private IPs  │
  │  (or Elastic IPs)           │  only                        │
  │                              │                              │
  │  Accessible from internet    │  NOT accessible from internet │
  │  (if SG allows)             │  (only from within VPC)      │
  │                              │                              │
  │  Place here:                 │  Place here:                 │
  │  • Load balancers            │  • Application servers       │
  │  • Bastion/jump hosts        │  • Databases                 │
  │  • NAT Gateways              │  • Internal services         │
  └──────────────────────────────┴──────────────────────────────┘
```

### 13.3 VPC Peering & Transit Gateway

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  VPC CONNECTIVITY OPTIONS                                        │
  │                                                                  │
  │  VPC Peering (1:1):            Transit Gateway (hub-and-spoke): │
  │                                                                  │
  │  ┌──────┐    ┌──────┐         ┌──────┐  ┌──────┐  ┌──────┐     │
  │  │VPC A │◄──►│VPC B │         │VPC A │  │VPC B │  │VPC C │     │
  │  └──────┘    └──────┘         └──┬───┘  └──┬───┘  └──┬───┘     │
  │  ┌──────┐    ┌──────┐            │         │         │          │
  │  │VPC A │◄──►│VPC C │         ┌──▼─────────▼─────────▼──┐       │
  │  └──────┘    └──────┘         │    Transit Gateway       │       │
  │  ┌──────┐    ┌──────┐         │    (centralized router)  │       │
  │  │VPC B │◄──►│VPC C │         └──────────┬───────────────┘       │
  │  └──────┘    └──────┘                    │                       │
  │                                     ┌────▼────┐                  │
  │  3 peering connections               │ On-prem │                  │
  │  for 3 VPCs!                         │  (VPN)  │                  │
  │  Not transitive!                     └─────────┘                  │
  │  (A↔B, B↔C ≠ A↔C)                                               │
  │                                  1 TGW for all connectivity      │
  │  Scales: O(n²) connections       Scales: O(n) attachments        │
  └──────────────────────────────────────────────────────────────────┘
```

> **DevOps Relevance:** Most multi-account AWS organizations use Transit Gateway. For simple two-VPC connectivity, peering is cheaper. Always plan CIDR ranges to avoid overlap — you cannot peer VPCs with overlapping CIDRs.

---

## 14. Container Networking — Docker & Kubernetes

### 14.1 Docker Networking Modes

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  DOCKER NETWORK DRIVERS                                          │
  │                                                                  │
  │  1. bridge (default):                                            │
  │  ┌───────────────────────────────────────┐                       │
  │  │  Host Machine                         │                       │
  │  │  ┌──────────────────────────────────┐  │                       │
  │  │  │  docker0 bridge (172.17.0.1)     │  │                       │
  │  │  │  ┌──────────┐  ┌──────────┐      │  │                       │
  │  │  │  │Container1│  │Container2│      │  │                       │
  │  │  │  │172.17.0.2│  │172.17.0.3│      │  │                       │
  │  │  │  └──────────┘  └──────────┘      │  │                       │
  │  │  └──────────────────────────────────┘  │                       │
  │  │  Containers talk to each other via bridge                     │
  │  │  Host talks to containers via docker0                         │
  │  │  External access via port mapping (-p 8080:80)               │
  │  └───────────────────────────────────────┘                       │
  │                                                                  │
  │  2. host: Container uses host's network stack directly          │
  │     No isolation. Container binds to host ports.                │
  │     Best for: performance-sensitive apps (no NAT overhead)      │
  │                                                                  │
  │  3. none: No networking at all. Complete isolation.              │
  │                                                                  │
  │  4. overlay: Multi-host networking (Docker Swarm / Compose)     │
  │     Uses VXLAN to create virtual L2 network across hosts        │
  │                                                                  │
  │  5. macvlan: Container gets its own MAC address on the LAN      │
  │     Appears as a physical device to the network                 │
  └──────────────────────────────────────────────────────────────────┘
```

### 14.2 Kubernetes Networking Model

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │  KUBERNETES NETWORKING — THE FOUR REQUIREMENTS                       │
  │                                                                      │
  │  1. Pod-to-Pod: All pods can communicate without NAT                 │
  │  2. Pod-to-Service: Services provide stable virtual IPs              │
  │  3. External-to-Service: Ingress/LoadBalancer for external access    │
  │  4. Pod-to-External: Pods can reach the internet (via node NAT)     │
  │                                                                      │
  │  ┌─ Node 1 ────────────────────┐  ┌─ Node 2 ────────────────────┐   │
  │  │                             │  │                             │   │
  │  │  Pod A         Pod B        │  │  Pod C         Pod D        │   │
  │  │  10.244.0.5    10.244.0.6   │  │  10.244.1.5    10.244.1.6  │   │
  │  │      │              │       │  │      │              │       │   │
  │  │  ┌───▼──────────────▼───┐   │  │  ┌───▼──────────────▼───┐  │   │
  │  │  │  cbr0 (virtual bridge)│   │  │  │  cbr0 (virtual bridge)│  │   │
  │  │  │  10.244.0.1           │   │  │  │  10.244.1.1           │  │   │
  │  │  └──────────┬────────────┘   │  │  └──────────┬────────────┘  │   │
  │  │             │                │  │             │               │   │
  │  └─────────────┼────────────────┘  └─────────────┼───────────────┘   │
  │                │    CNI Plugin (Flannel,          │                   │
  │                │    Calico, Cilium) handles       │                   │
  │                └────── cross-node routing ────────┘                   │
  │                                                                      │
  │  Service: ClusterIP 10.96.0.10:80 → Pod A (10.244.0.5:8080)        │
  │           (kube-proxy manages iptables/IPVS rules for routing)      │
  └──────────────────────────────────────────────────────────────────────┘
```

### 14.3 Kubernetes Service Types

| Service Type | Access | Use Case |
|-------------|--------|----------|
| **ClusterIP** | Internal only | Service-to-service within cluster |
| **NodePort** | External via `node_ip:port` | Dev/testing, simple exposure |
| **LoadBalancer** | External via cloud LB | Production external services |
| **ExternalName** | DNS CNAME alias | Point to external service (e.g., RDS) |

### 14.4 CNI Plugins Comparison

| Plugin | Network Mode | Encryption | Network Policy | Best For |
|--------|-------------|------------|----------------|----------|
| **Flannel** | VXLAN, host-gw | ❌ (use WireGuard) | ❌ (basic) | Simple clusters |
| **Calico** | BGP, VXLAN, eBPF | ✅ (WireGuard) | ✅ (powerful) | Production, security |
| **Cilium** | eBPF (no iptables!) | ✅ (WireGuard) | ✅ (L3-L7) | Performance, observability |
| **Weave** | VXLAN mesh | ✅ (built-in) | ✅ | Easy multi-cloud |

> **⚠️ Gotcha (Pod CIDR vs Service CIDR):** Kubernetes has TWO internal IP ranges — the Pod CIDR (10.244.0.0/16 default) and the Service CIDR (10.96.0.0/12 default). Make sure neither overlaps with your VPC CIDR or on-premises networks. Overlapping CIDRs = routing chaos.

---

## 15. Network Monitoring & Observability

### 15.1 What to Monitor

```
  ┌─────────────────────────────────────────────────────────────────┐
  │  NETWORK MONITORING — KEY METRICS                               │
  │                                                                 │
  │  Availability:                                                  │
  │  ├── Host reachability (ping/ICMP)                              │
  │  ├── Port availability (TCP check)                              │
  │  └── Service health (HTTP /health)                              │
  │                                                                 │
  │  Performance:                                                   │
  │  ├── Latency (round-trip time)                                  │
  │  ├── Bandwidth utilization (% of capacity)                      │
  │  ├── Packet loss (%)                                            │
  │  ├── Jitter (latency variation)                                 │
  │  └── TCP retransmissions                                        │
  │                                                                 │
  │  Errors:                                                        │
  │  ├── DNS failures / timeouts                                    │
  │  ├── Connection resets (RST)                                    │
  │  ├── TLS handshake failures                                     │
  │  ├── 5xx error rates                                            │
  │  └── Connection timeouts                                        │
  │                                                                 │
  │  Security:                                                      │
  │  ├── Firewall deny logs                                         │
  │  ├── ARP anomalies                                              │
  │  ├── Port scan detection                                        │
  │  └── Unexpected traffic patterns                                │
  └─────────────────────────────────────────────────────────────────┘
```

### 15.2 Monitoring Tools

| Tool | Type | Protocol | Best For |
|------|------|----------|----------|
| **Prometheus + Grafana** | Metrics | HTTP pull | Cloud-native monitoring |
| **Nagios/Icinga** | Checks | NRPE, SNMP | Traditional infra monitoring |
| **Zabbix** | Full-stack | SNMP, agent | Enterprise network monitoring |
| **Datadog** | SaaS | Agent | Multi-cloud observability |
| **Wireshark** | Packet capture | Any | Deep packet analysis |
| **ntopng** | Flow analysis | NetFlow/sFlow | Traffic pattern analysis |
| **Blackbox Exporter** | Probing | ICMP, TCP, HTTP | Endpoint monitoring (Prometheus) |
| **VPC Flow Logs** | Cloud-native | N/A | AWS/Azure/GCP traffic analysis |

### 15.3 VPC Flow Logs — Cloud Network Forensics

```
  VPC Flow Log Record (AWS):
  
  2 123456789012 eni-abc123 10.0.1.5 52.94.76.10 49152 443 6 20 4096 
  1620000000 1620000060 ACCEPT OK
  
  ┌────────────────────────────────────────────────────────────────┐
  │  Field         Value          Meaning                          │
  │  ──────        ──────         ────────                         │
  │  version       2              Log format version               │
  │  account-id    123456789012   AWS account                      │
  │  interface-id  eni-abc123     Network interface                │
  │  srcaddr       10.0.1.5       Source IP                        │
  │  dstaddr       52.94.76.10    Destination IP                   │
  │  srcport       49152          Source port (ephemeral)          │
  │  dstport       443            Destination port (HTTPS)         │
  │  protocol      6              TCP (6=TCP, 17=UDP, 1=ICMP)     │
  │  packets       20             Packet count                     │
  │  bytes         4096           Byte count                       │
  │  start         1620000000     Start time (Unix epoch)          │
  │  end           1620000060     End time                         │
  │  action        ACCEPT         Allowed by SG/NACL               │
  │  log-status    OK             Logging status                   │
  └────────────────────────────────────────────────────────────────┘
  
  Use cases:
  • "Why can't Pod X reach RDS?" → Check flow logs for REJECT
  • "What's making outbound calls?" → Filter by source IP
  • "Is someone port scanning?" → Look for many dstport values
```

---

## 16. Production Gotchas & Scenario-Based FAQ

### Q1: Our application works locally but gets "connection refused" in the cloud. What's happening?

**Scenario:** App listens on port 3000, you've confirmed the EC2 instance is running, but `curl http://<public-ip>:3000` fails with "connection refused."

```
  Troubleshooting checklist:
  
  1. Is the app binding to 0.0.0.0 (not just 127.0.0.1)?
     ┌──────────────────────────────────────────────────────┐
     │  ❌ app.listen(3000, '127.0.0.1')  ← localhost only │
     │  ✅ app.listen(3000, '0.0.0.0')    ← all interfaces │
     │  ✅ app.listen(3000)                ← default: all   │
     └──────────────────────────────────────────────────────┘
  
  2. Security Group allows inbound on port 3000?
  3. NACL allows inbound on port 3000 AND outbound ephemeral (1024-65535)?
  4. OS firewall (iptables/firewalld) allows port 3000?
  5. App is actually running? (ss -tlnp | grep 3000)
```

---

### Q2: DNS resolution works on my machine but fails inside Kubernetes pods. Why?

```
  Common causes:
  
  1. CoreDNS pods are down or OOMKilled
     kubectl get pods -n kube-system -l k8s-app=kube-dns
  
  2. ndots setting causing excessive lookups:
     Default ndots:5 means "api.example.com" becomes:
     → api.example.com.default.svc.cluster.local  (fail)
     → api.example.com.svc.cluster.local          (fail)
     → api.example.com.cluster.local               (fail)
     → api.example.com.<search-domain>              (fail)
     → api.example.com.                             (finally works!)
     
     Fix: Add a trailing dot: "api.example.com." 
     Or set dnsConfig.options: [{name: ndots, value: "2"}]
  
  3. Pod dnsPolicy is wrong:
     • ClusterFirst (default): use CoreDNS
     • Default: use node's /etc/resolv.conf
     • None: custom dnsConfig only
```

---

### Q3: We're seeing intermittent TCP connection resets between microservices. How do we diagnose?

```
  ┌──────────────────────────────────────────────────────────┐
  │  DIAGNOSING TCP RESETS (RST)                             │
  │                                                          │
  │  1. Capture packets:                                     │
  │     tcpdump -i eth0 'tcp[tcpflags] & tcp-rst != 0' -nn  │
  │                                                          │
  │  2. Common causes:                                       │
  │     a. Connection pool timeout mismatch:                 │
  │        Client keepalive: 60s                             │
  │        Server/LB timeout: 30s ← server closes first!    │
  │        Fix: client timeout < server timeout              │
  │                                                          │
  │     b. Conntrack table full (Linux):                     │
  │        dmesg | grep "nf_conntrack: table full"           │
  │        Fix: sysctl net.netfilter.nf_conntrack_max        │
  │                                                          │
  │     c. ALB idle timeout (AWS default: 60s):              │
  │        If backend keepalive < ALB idle timeout → RST     │
  │        Fix: app keepalive > ALB idle timeout             │
  │                                                          │
  │     d. iptables REJECT vs DROP confusion:                │
  │        REJECT → sends RST → fast failure                 │
  │        DROP → silently discards → timeout (slow failure) │
  └──────────────────────────────────────────────────────────┘
```

---

### Q4: What's MTU and why does it cause issues with VPNs and containers?

```
  MTU (Maximum Transmission Unit) = max packet size before fragmentation
  
  Standard Ethernet MTU: 1500 bytes
  
  Problem with encapsulation:
  ┌────────────────────────────────────────────────────────┐
  │  Original packet: 1500 bytes                           │
  │  + VPN/VXLAN overhead: ~50-70 bytes                    │
  │  = 1550-1570 bytes → exceeds 1500 MTU!                │
  │                                                        │
  │  Result: Fragmentation or dropped packets              │
  │  Symptom: "Small requests work, large transfers fail"  │
  │  (SSH works, SCP hangs. Ping works, HTTP fails.)      │
  │                                                        │
  │  Fix: Lower the inner MTU:                             │
  │  • VPN tunnel interface: MTU 1400-1420                 │
  │  • Docker containers: --mtu 1450                       │
  │  • Kubernetes pods: CNI MTU config                     │
  │  • AWS VPC (jumbo frames): MTU 9001                    │
  └────────────────────────────────────────────────────────┘
  
  Check current MTU:
  ip link show eth0 | grep mtu
  
  Test MTU path discovery:
  ping -c 4 -M do -s 1472 destination  (1472 + 28 = 1500)
```

---

### Q5: How do I troubleshoot "504 Gateway Timeout" on our load balancer?

```
  504 = Load balancer reached backend, but backend didn't respond in time
  
  ┌──────────────────────────────────────────────────────────────┐
  │  Diagnosis path:                                             │
  │                                                              │
  │  1. Check LB timeout settings:                               │
  │     AWS ALB: idle timeout (default 60s)                      │
  │     Nginx: proxy_read_timeout (default 60s)                  │
  │                                                              │
  │  2. Check backend response time:                             │
  │     curl -o /dev/null -s -w "time_total: %{time_total}\n"   │
  │       http://backend:port/slow-endpoint                      │
  │                                                              │
  │  3. Check backend health:                                    │
  │     • CPU maxed out? (top, htop)                             │
  │     • Database queries slow? (slow query log)                │
  │     • Thread/connection pool exhausted?                       │
  │     • External API calls timing out? (cascade failure)       │
  │                                                              │
  │  4. Check network path:                                      │
  │     • Security group allows health check port?               │
  │     • NACL allows return traffic?                            │
  │     • Route table has path to backend subnet?                │
  │                                                              │
  │  Quick fixes:                                                │
  │  • Increase LB timeout (band-aid)                            │
  │  • Fix slow queries (root cause)                             │
  │  • Add circuit breakers (resilience)                         │
  │  • Scale backend horizontally (capacity)                     │
  └──────────────────────────────────────────────────────────────┘
```

---

### Q6: What's the difference between a TCP reset and a timeout, and how do I tell which one I'm seeing?

```
  TCP Reset (RST):                     TCP Timeout:
  ┌──────────────────────────────┐     ┌──────────────────────────────┐
  │ Immediate rejection           │     │ Waiting... waiting... fail   │
  │ Server sends RST packet       │     │ No response at all          │
  │ Error: "Connection refused"   │     │ Error: "Connection timed out"│
  │ Cause: port not listening,    │     │ Cause: firewall DROPping,   │
  │   firewall REJECT,            │     │   packet loss, host down,   │
  │   connection pool full         │     │   routing black hole        │
  │ Time: instant                 │     │ Time: 20-120 seconds        │
  └──────────────────────────────┘     └──────────────────────────────┘
  
  Diagnosing with tcpdump:
  RST:     SYN → RST,ACK    (immediate response)
  Timeout: SYN → ... → SYN (retransmit) → ... → SYN → give up
```

---

### Q7: Our app runs fine with 100 users but falls apart at 10,000. What network limits hit first?

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  SCALING BOTTLENECKS (in order of likelihood)                    │
  │                                                                  │
  │  1. Ephemeral port exhaustion:                                  │
  │     Linux default range: 32768–60999 = ~28K ports               │
  │     Each outbound connection uses one port                       │
  │     10K connections to DB + 10K to cache + 10K to APIs = out!  │
  │     Fix: sysctl net.ipv4.ip_local_port_range = "1024 65535"    │
  │          + connection pooling                                   │
  │                                                                  │
  │  2. Conntrack table full:                                       │
  │     Default: 65536 entries                                      │
  │     Each connection = 1 entry                                   │
  │     Fix: sysctl net.netfilter.nf_conntrack_max = 1048576       │
  │                                                                  │
  │  3. File descriptor limit:                                      │
  │     Default: 1024 per process (ulimit -n)                       │
  │     Each socket = 1 fd                                          │
  │     Fix: ulimit -n 65535 + /etc/security/limits.conf           │
  │                                                                  │
  │  4. TCP TIME_WAIT accumulation:                                 │
  │     Short-lived connections pile up in TIME_WAIT (60s each)    │
  │     Fix: net.ipv4.tcp_tw_reuse = 1                             │
  │                                                                  │
  │  5. Socket backlog:                                             │
  │     net.core.somaxconn (default 128, set to 65535)             │
  │     net.ipv4.tcp_max_syn_backlog (default 128)                 │
  └──────────────────────────────────────────────────────────────────┘
```

---

### Q8: How do we do zero-downtime DNS migration from old server to new server?

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  ZERO-DOWNTIME DNS MIGRATION                                     │
  │                                                                  │
  │  Day 1 (Preparation):                                           │
  │  ├── Lower DNS TTL from 3600s (1h) to 60s (1min)              │
  │  ├── Wait at least current-TTL time (1h) for propagation       │
  │  └── Verify low TTL: dig +short example.com (check TTL value) │
  │                                                                  │
  │  Day 2 (Migration):                                             │
  │  ├── Set up new server, verify it works                         │
  │  ├── Run both old and new servers simultaneously                │
  │  ├── Switch DNS A record from old-IP to new-IP                 │
  │  ├── Wait ~60s (the low TTL)                                   │
  │  ├── Most clients now hitting new server                        │
  │  └── Monitor error rates on both servers                       │
  │                                                                  │
  │  Day 3 (Cleanup):                                               │
  │  ├── Verify no traffic to old server (check access logs)       │
  │  ├── Raise TTL back to 3600s                                   │
  │  └── Decommission old server after 24-48h                      │
  │                                                                  │
  │  Why wait 24-48h? Some resolvers IGNORE low TTL and cache      │
  │  for their own minimum (often 300s or more). Enterprise        │
  │  networks may cache even longer.                                │
  └──────────────────────────────────────────────────────────────────┘
```

---

### Q9: Explain the difference between Security Groups and NACLs with a real-world incident scenario.

```
  Scenario: Web app stopped working after adding a new NACL rule.
  
  ┌──────────────────────────────────────────────────────────────┐
  │  What happened:                                              │
  │                                                              │
  │  SG (stateful):     NACL (stateless):                       │
  │  Inbound: port 80 ✅  Inbound rule 100: port 80 ALLOW ✅   │
  │  Return traffic:      Outbound rule 100: port 80 ALLOW ✅   │
  │    auto-allowed ✅    Outbound ephemeral: ??? ❌            │
  │                                                              │
  │  The return traffic from the server to client uses           │
  │  an ephemeral port (e.g., 52341), NOT port 80!             │
  │                                                              │
  │  Fix: Add NACL outbound rule:                                │
  │  Allow TCP ports 1024-65535 outbound (ephemeral ports)      │
  │                                                              │
  │  Lesson: SG handles this automatically (stateful).          │
  │  NACL does NOT (stateless — you must explicitly allow       │
  │  both directions including ephemeral port ranges).          │
  └──────────────────────────────────────────────────────────────┘
```

---

### Q10: We have microservices in different VPCs. What's the best way to connect them?

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  VPC CONNECTIVITY DECISION TREE                                  │
  │                                                                  │
  │  How many VPCs?                                                 │
  │  ├── 2 VPCs: VPC Peering (simple, free data transfer*)         │
  │  ├── 3+ VPCs: Transit Gateway (centralized, scalable)          │
  │  └── Cross-region: Inter-region peering or TGW peering         │
  │                                                                  │
  │  Need private access to AWS services?                           │
  │  └── VPC Endpoints (Interface/Gateway) — no internet needed    │
  │                                                                  │
  │  Need on-premises connectivity?                                 │
  │  ├── Quick/cheap: Site-to-site VPN (over internet)              │
  │  └── Production: Direct Connect (dedicated fiber)               │
  │                                                                  │
  │  Cross-account service access?                                  │
  │  └── AWS PrivateLink — expose service without VPC peering      │
  │      (keeps traffic on AWS backbone, no CIDR overlap issues)   │
  │                                                                  │
  │  *VPC Peering: data transfer charges between AZs still apply   │
  └──────────────────────────────────────────────────────────────────┘
```

---

### Q11: What is CORS and why does it break our frontend-backend communication?

```
  CORS (Cross-Origin Resource Sharing):
  
  Browser at: https://app.example.com
  API at:     https://api.example.com  ← different origin!
  
  Browser enforces Same-Origin Policy:
  ┌──────────────────────────────────────────────────────────────┐
  │  1. Browser sends OPTIONS request (preflight):               │
  │     Origin: https://app.example.com                          │
  │     Access-Control-Request-Method: POST                      │
  │                                                              │
  │  2. Server must respond with:                                │
  │     Access-Control-Allow-Origin: https://app.example.com     │
  │     Access-Control-Allow-Methods: GET, POST, PUT             │
  │     Access-Control-Allow-Headers: Content-Type, Authorization│
  │                                                              │
  │  3. If headers are missing or wrong → browser blocks request │
  │     Error: "CORS policy: No 'Access-Control-Allow-Origin'"  │
  │                                                              │
  │  Fix (Nginx):                                                │
  │  add_header 'Access-Control-Allow-Origin' 'https://app.example.com';│
  │  add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT';│
  │                                                              │
  │  ⚠️ NEVER use: Access-Control-Allow-Origin: *                │
  │     in production with credentials!                          │
  └──────────────────────────────────────────────────────────────┘
```

---

### Q12: How do we handle SSL/TLS certificate expiry without downtime?

```
  ┌──────────────────────────────────────────────────────────────┐
  │  TLS CERT RENEWAL — ZERO DOWNTIME                            │
  │                                                              │
  │  Automated (recommended):                                    │
  │  ├── Let's Encrypt + Certbot (auto-renew cron)              │
  │  ├── AWS ACM (auto-renew, free for AWS resources)           │
  │  ├── Azure Key Vault (auto-renew integration)               │
  │  └── cert-manager (Kubernetes — auto-renew with ACME)       │
  │                                                              │
  │  Manual renewal process:                                     │
  │  1. Generate new CSR + key BEFORE expiry (30 days ahead)    │
  │  2. Submit to CA, get new cert                               │
  │  3. Install new cert on server                               │
  │  4. Reload (not restart!) web server:                        │
  │     nginx -s reload  ← graceful, zero downtime              │
  │     systemctl reload httpd                                   │
  │  5. Verify: openssl s_client -connect host:443              │
  │                                                              │
  │  Monitoring:                                                 │
  │  • Prometheus blackbox exporter: probe_ssl_earliest_cert_    │
  │    expiry (alert when < 30 days)                             │
  │  • curl: echo | openssl s_client -connect host:443 2>/dev/  │
  │    null | openssl x509 -noout -dates                         │
  └──────────────────────────────────────────────────────────────┘
```

---

### Q13: What's the difference between TCP keepalive and HTTP keep-alive?

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  THEY ARE DIFFERENT THINGS!                                      │
  │                                                                  │
  │  TCP Keepalive (Layer 4):            HTTP Keep-Alive (Layer 7): │
  │  ────────────────────────            ────────────────────────── │
  │  OS-level TCP socket option          HTTP/1.1 connection reuse  │
  │  Sends tiny probe packets            "Don't close this TCP     │
  │  to detect dead connections           connection after each    │
  │  Default: 2h idle timeout             HTTP request"            │
  │                                                                  │
  │  Purpose: detect dead peers          Purpose: avoid TCP         │
  │  (half-open connections)              handshake overhead         │
  │                                       for multiple requests     │
  │  sysctl:                                                        │
  │  net.ipv4.tcp_keepalive_time=600     Nginx:                     │
  │  net.ipv4.tcp_keepalive_intvl=60     keepalive_timeout 65s;    │
  │  net.ipv4.tcp_keepalive_probes=5     keepalive_requests 1000;  │
  │                                                                  │
  │  Common production issue:                                       │
  │  AWS NLB idle timeout: 350s                                     │
  │  App TCP keepalive: 7200s (2h default)                          │
  │  → NLB closes connection silently after 350s                   │
  │  → App sends data on dead connection → RST                     │
  │  Fix: Set TCP keepalive < NLB idle timeout                     │
  └──────────────────────────────────────────────────────────────────┘
```

---

### Q14: We're getting "no route to host" errors intermittently. What causes this?

```
  "No route to host" = Layer 3 issue — the kernel has no route
  
  Common causes:
  1. Firewall REJECT (sends ICMP unreachable → "no route to host")
     vs ICMP filtering or actual routing gap
  
  2. Route table missing entry:
     ip route show  ← check if destination subnet has a route
  
  3. Cloud: route table not associated with subnet
     AWS: check subnet → route table association
  
  4. VPN tunnel down:
     ip tunnel show  ← is the tunnel interface up?
     
  5. Asymmetric routing:
     Request goes path A, response tries path B
     Stateful firewalls see response as "new" → drop
     
  Debug:
  traceroute -n <dest>  ← where does it stop?
  ip route get <dest>   ← which route would be used?
  sudo iptables -L -v   ← any REJECT rules?
```

---

### Q15: How do container networking namespaces work under the hood?

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  LINUX NETWORK NAMESPACES — What Docker uses internally          │
  │                                                                  │
  │  Each container gets its own network namespace with:             │
  │  • Its own network interfaces                                   │
  │  • Its own routing table                                        │
  │  • Its own iptables rules                                       │
  │  • Its own /proc/net                                            │
  │                                                                  │
  │  ┌─ Host Namespace ────────────────────────────────────┐         │
  │  │                                                     │         │
  │  │  eth0 (physical)    docker0 (bridge: 172.17.0.1)    │         │
  │  │      │                  │                           │         │
  │  │      │              ┌───┴───┐                       │         │
  │  │      │              │ veth  │ (virtual ethernet pair)│         │
  │  │      │              │ host  │                       │         │
  │  │      │              │ end   │                       │         │
  │  └──────┼──────────────┼───────┼───────────────────────┘         │
  │         │              │       │                                  │
  │         │         ┌────┼───────┼──── Container Namespace ────┐   │
  │         │         │    │ veth  │                             │   │
  │         │         │    │ cont  │                             │   │
  │         │         │    │ end   │                             │   │
  │         │         │    │       │                             │   │
  │         │         │    │  eth0 (172.17.0.2)                 │   │
  │         │         │    │  routing: default via 172.17.0.1   │   │
  │         │         └─────────────────────────────────────────┘   │
  │                                                                  │
  │  Traffic flow: Container eth0 → veth pair → docker0 → NAT →     │
  │  host eth0 → internet                                           │
  └──────────────────────────────────────────────────────────────────┘
  
  Manual exploration:
  # List network namespaces
  sudo ip netns list
  
  # Execute command in container's namespace
  sudo nsenter -t $(docker inspect -f '{{.State.Pid}}' <container>) -n ip addr
```

---

> **Handbook complete.** This covers networking from physical layer to container orchestration — the full spectrum a DevOps engineer encounters daily.  
> **Next:** Try the [Networking Practice Lab](../labs/networking_practice_lab.md) or the [Data Centers & Cloud Computing Handbook](../cloud/cloud_handbook.md).

[🏠 Home](../README.md) · [Networking](README.md)
