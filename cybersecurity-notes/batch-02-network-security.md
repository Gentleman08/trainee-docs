# Batch 2 — Network Security
> Protecting data in transit and securing the perimeter.

## 1. Firewall (Stateful vs Stateless)

### Definition
A firewall is a network security device that monitors and filters traffic based on established policies. Stateless firewalls inspect individual packets in isolation, while stateful firewalls track the operating state and context of active connections.

### Real-World Dev/IT Example
You configure an AWS Security Group (a stateful firewall) to allow incoming traffic on port 443; the return traffic is automatically allowed. A Network ACL (a stateless firewall) requires explicit rules for both inbound and outbound traffic.

### ASCII Diagram
```text
[Internet] --> (Stateless FW: header checks) --> (Stateful FW: connection checks) --> [Server]
```

### Gotchas & Dev Context
- Stateful firewalls are easier to manage but consume more memory tracking connections.
- Stateless firewalls are faster and better for mitigating high-volume attacks like DDoS.
- Misconfiguring egress (outbound) rules is a common rookie mistake—always restrict outbound traffic.

### Production FAQ
**Q: Why would I ever use a stateless firewall?**
A: For raw performance at the network edge, handling massive traffic bursts where tracking connection states would exhaust router memory.

**Q: Does a firewall protect against malware?**
A: Traditional firewalls only block ports/IPs. Next-Generation Firewalls (NGFWs) include Deep Packet Inspection to block malware.

## 2. Intrusion Detection System (IDS) vs Intrusion Prevention System (IPS)

### Definition
An IDS is a passive monitoring system that detects malicious activity and generates alerts. An IPS is an active system that sits inline with traffic and can block malicious connections in real-time.

### Real-World Dev/IT Example
Your Suricata IDS detects an SQL injection signature in an HTTP request and logs an alert. If configured as an IPS, Suricata actively drops those malicious packets before they reach your database.

### Gotchas & Dev Context
- IDS is out-of-band (doesn't impact traffic flow), while IPS is in-line (can become a bottleneck).
- False positives in an IPS can block legitimate user traffic, causing immediate outages.
- Usually deployed as Host-based agents (HIDS) or Network-based appliances (NIDS).

### Production FAQ
**Q: Should I deploy IDS or IPS first?**
A: Always deploy in IDS (monitoring) mode first to tune the rules and understand false positives before switching to IPS (blocking) mode.

**Q: How do they handle encrypted traffic?**
A: They can't inspect what they can't read. You need TLS termination before traffic hits the IDS/IPS to inspect the payload.

## 3. Virtual Private Network (VPN)

### Definition
A VPN creates a secure, encrypted tunnel over a less secure network (like the public internet) to connect remote users or sites to a private network.

### Real-World Dev/IT Example
A remote developer uses an OpenVPN client to connect to the corporate network, allowing them to securely access an internal GitLab server that has no public internet exposure.

### ASCII Diagram
```text
[Remote Dev] ===(Encrypted VPN Tunnel)=== [Corporate Gateway] ---> [Internal Servers]
```

### Gotchas & Dev Context
- "Split tunneling" routes only corporate traffic through the VPN, reducing bandwidth load but introducing security risks.
- IPsec (Network layer) and SSL/TLS (Application layer) are the most common VPN protocols.
- WireGuard is rapidly replacing older protocols due to modern cryptography and higher throughput.

### Production FAQ
**Q: Does a VPN make me completely anonymous?**
A: No. It hides traffic from your local ISP, but the VPN provider (or your company) can see everything.

**Q: Are traditional VPNs becoming obsolete?**
A: Perimeter VPNs are slowly being replaced by Zero Trust Network Access (ZTNA), which authenticates per-application rather than granting full network access.

## 4. SIEM (Security Information and Event Management)

### Definition
A SIEM is a centralized platform that aggregates, correlates, and analyzes log data from across an organization's IT infrastructure to identify security incidents.

### Real-World Dev/IT Example
You forward logs from AWS CloudTrail, Nginx, and Active Directory to Splunk. The SIEM correlates an unusual admin login at 3 AM with a massive database export and triggers a critical alert.

### Gotchas & Dev Context
- Log normalization is painful; logs from different systems format timestamps and IPs differently.
- Storage costs can skyrocket. You must filter out "noise" before ingestion.
- Poorly tuned SIEM rules will drown your security team in alert fatigue.

### Production FAQ
**Q: What's the difference between SIEM and a regular log manager?**
A: Log managers (like basic ELK) just store and search logs. SIEMs add threat intelligence feeds, cross-system correlation, and automated security alerting.

**Q: Which logs should we feed into the SIEM?**
A: Focus on high-value logs: authentication events, firewall blocks, and administrative actions. Avoid raw network traffic dumps.

## 5. SOC (Security Operations Center)

### Definition
A SOC is a centralized team of security professionals who continuously monitor, detect, analyze, and respond to cybersecurity incidents using tools like SIEM and SOAR.

### Real-World Dev/IT Example
When a developer accidentally commits AWS access keys to a public GitHub repo, an automated alert hits the SOC dashboard. An analyst immediately revokes the keys and checks CloudTrail for misuse.

### Gotchas & Dev Context
- SOCs rely heavily on automation tools to manage workflow and initial triage.
- Tier 1 analysts handle basic triage, Tier 2 do deeper investigations, and Tier 3 handle advanced threat hunting.
- 24/7 coverage requires substantial headcount and handoff procedures.

### Production FAQ
**Q: Should a startup build its own SOC?**
A: Rarely. Building an in-house 24/7 SOC is extremely expensive. Startups usually outsource to a Managed Security Service Provider (MSSP).

**Q: How does SOC differ from NOC (Network Operations Center)?**
A: A NOC focuses on system availability (is the server up?), while a SOC focuses on security (is the server compromised?).

## 6. Subnetting & VLANs

### Definition
Subnetting divides a large logical IP network into smaller segments to improve performance and routing. VLANs (Virtual LANs) isolate traffic at the data link layer, grouping devices as if they were on the same physical switch.

### Real-World Dev/IT Example
You use AWS VPC subnets to isolate infrastructure: a public subnet for load balancers and a private subnet for databases. Physically, you use VLANs to keep guest Wi-Fi separate from developer workstations.

### ASCII Diagram
```text
[Network 10.0.0.0/16]
   ├── [VLAN 10: Web - 10.0.1.0/24]
   └── [VLAN 20: DBs - 10.0.2.0/24]
```

### Gotchas & Dev Context
- Devices on different VLANs/subnets cannot communicate without a router or Layer 3 switch.
- VLAN Hopping is an attack bypassing isolation—always disable unused switch ports.
- Subnetting relies on CIDR notation (e.g., `/24` yields 256 IPs).

### Production FAQ
**Q: Why separate DB servers from Web servers?**
A: Network isolation prevents an attacker who compromises a web server from easily pivoting to attack the databases.

**Q: Can software-defined networking (SDN) replace VLANs?**
A: In modern cloud and Kubernetes environments, SDN overlay networks often replace traditional physical VLANs for micro-segmentation.

## 7. OSI Model (Security perspective)

### Definition
The OSI model is a conceptual framework standardizing network communication into seven layers. It helps security teams identify where specific threats occur and where defenses should be deployed.

### Real-World Dev/IT Example
A DDoS attack on Layer 4 tries to overwhelm your router with TCP SYN floods. A Layer 7 attack tries to crash your Node.js app by sending massive, complex JSON payloads.

### Gotchas & Dev Context
- **Layer 3/4 (Network/Transport):** IPsec, traditional firewalls, and port scanning happen here.
- **Layer 7 (Application):** HTTP/HTTPS, Web Application Firewalls (WAF), and API abuse happen here.
- Defenses must match the attack layer (e.g., a standard firewall won't stop an SQL injection).

### Production FAQ
**Q: Why does a WAF sit at Layer 7?**
A: Because it needs to understand HTTP semantics (headers, cookies, JSON bodies) to block web exploits, which lower-layer firewalls cannot inspect.

**Q: Which layer is the most targeted today?**
A: Layer 7. As network perimeters harden, attackers increasingly target application logic and APIs.

## 8. TCP/IP Handshake

### Definition
The TCP/IP three-way handshake is the process used by TCP to establish a reliable, connection-oriented session between a client and a server before any data is transmitted.

### Real-World Dev/IT Example
When a user visits your site, their browser sends a `SYN` packet. Your server replies with `SYN-ACK`. The browser sends an `ACK`, and then the HTTP request is transmitted.

### ASCII Diagram
```text
Client                    Server
  | ------- SYN -------->   |
  | <---- SYN-ACK -------   |
  | ------- ACK -------->   |
  | == Data Transfer ===>   |
```

### Gotchas & Dev Context
- Attackers exploit this with "SYN Floods": sending thousands of `SYN` packets but never completing the `ACK`, exhausting server resources.
- "SYN cookies" are a defense mechanism allowing servers to handle floods without dropping valid connections.
- UDP skips this handshake entirely, making it faster but easier to spoof.

### Production FAQ
**Q: How do load balancers handle TCP handshakes?**
A: Layer 4 LBs just forward the handshake. Layer 7 LBs terminate the connection locally, inspect the traffic, and open a separate handshake with the backend server.

**Q: Why is latency high on new connections?**
A: The TCP handshake plus the TLS handshake adds multiple round-trips before the first byte of payload data is sent.

## 9. Port Scanning

### Definition
Port scanning is the process of sending network requests to a target's IP address to discover open, closed, or filtered ports, identifying running services and potential vulnerabilities.

### Real-World Dev/IT Example
A security researcher uses `nmap` to scan your company's public IPs. They find port 22 (SSH) and 8080 (dev web server) left open, exposing a staging environment to the internet.

### Gotchas & Dev Context
- Scanners use varying techniques (e.g., SYN "stealth" scans) to map services without completing a full TCP handshake, bypassing basic firewall logging.
- Default to "deny all" inbound traffic to prevent discovery of management ports.
- Shodan is a search engine that actively port scans the entire internet to index vulnerable devices.

### Production FAQ
**Q: Is port scanning illegal?**
A: Scanning external networks you don't own resides in a legal gray area and often violates ISP terms of service.

**Q: How can we detect port scanning?**
A: Modern IDS/IPS systems have built-in thresholds to detect a single IP hitting multiple ports in rapid succession.

## 10. Man-in-the-Middle (MITM) Attack

### Definition
A MITM attack occurs when an attacker secretly intercepts, relays, and potentially alters communications between two parties who believe they are communicating directly.

### Real-World Dev/IT Example
An attacker sets up a rogue "Starbucks_WiFi" hotspot. A user connects, and the attacker intercepts their unencrypted HTTP traffic to steal session cookies and plain-text passwords.

### Gotchas & Dev Context
- TLS/SSL encryption is the primary defense, as it secures the payload and verifies server identity via certificates.
- Certificate pinning in mobile apps prevents attackers from using locally installed rogue CA certificates to intercept traffic.
- HSTS (HTTP Strict Transport Security) forces browsers to use HTTPS, preventing downgrade attacks.

### Production FAQ
**Q: Can MITM happen inside a secure corporate network?**
A: Yes, via internal techniques like ARP poisoning or DNS spoofing. Internal network encryption (Zero Trust) is crucial.

**Q: Does a VPN prevent MITM attacks?**
A: Yes, an encrypted VPN tunnel protects your traffic from local MITM attacks on untrusted networks.

## 11. DDoS Attack

### Definition
A Distributed Denial of Service (DDoS) attack disrupts a targeted server or network by overwhelming it with a flood of malicious internet traffic from multiple compromised sources.

### Real-World Dev/IT Example
A botnet of 100,000 compromised smart cameras sends massive amounts of garbage HTTP requests to your web server simultaneously, causing legitimate users to see a "503 Service Unavailable" error.

### Gotchas & Dev Context
- Volumetric attacks exhaust bandwidth (UDP reflection). Application-layer attacks exhaust server compute (HTTP floods).
- Traditional firewalls often fail against massive DDoS; you need edge protection like Cloudflare or AWS Shield.
- Auto-scaling absorbs small spikes but can cause massive cloud bills if traffic isn't mitigated.

### Production FAQ
**Q: How does Anycast help against DDoS?**
A: Anycast routing distributes incoming traffic across multiple geographically dispersed data centers, naturally absorbing volumetric attacks.

**Q: Can we just block the attacking IPs?**
A: Because attacks use highly distributed, spoofed, or rotating IPs, blocking them individually is futile. You need behavioral traffic analysis.

## 12. Honeypot

### Definition
A honeypot is a decoy system or network designed to mimic a legitimate target to attract cyberattackers, allowing security teams to monitor their tactics and gather intelligence.

### Real-World Dev/IT Example
You deploy an intentionally vulnerable SSH server with fake customer data. When an attacker breaches it, the honeypot silently logs their keystrokes, downloaded scripts, and IP addresses.

### Gotchas & Dev Context
- Low-interaction honeypots simulate basic services. High-interaction honeypots are full OS instances (richer data but riskier).
- Honeypots must be strictly isolated from your production network to prevent them from becoming a staging ground for real attacks.
- "Honeytokens" (like fake AWS keys in a database) are a lightweight alternative to full systems.

### Production FAQ
**Q: Are honeypots legal?**
A: Yes, as long as they are used defensively on your own network and do not actively "hack back" or entrap users.

**Q: Why spend resources on fake systems?**
A: Honeypots generate zero false positives. Since no legitimate user should ever access a honeypot, any interaction is a guaranteed sign of malicious activity.
