# Case Study 2 — ZTNA Implementation
> Securing remote access with identity-aware proxies and device health checks.

## 1. Project Overview
As modern workforces shift to fully remote or hybrid models, traditional perimeter-based VPNs fall short. They provide broad network access once authenticated, making lateral movement easy for attackers if a single credential is compromised. 

This project implements Zero Trust Network Access (ZTNA) to replace our legacy corporate VPN. The new system enforces the principle of "never trust, always verify." It continuously authenticates user identity and verifies the security posture of their endpoint device before granting granular, micro-segmented access to internal assets—specifically, our internal Git repositories (GitLab) and CI/CD pipelines (Jenkins).

**Who Uses It:** 
- **Engineering Teams:** Secure access to code repositories and build servers.
- **DevOps/SREs:** Elevated access to pipeline configurations and deployment infrastructure.
- **Contractors:** Highly restricted, time-bound access to specific project repositories without broad network visibility.

## 2. Architecture Diagram

The architecture shifts away from a centralized VPN concentrator. Instead, we use an Identity-Aware Proxy (IAP) acting as a secure access gateway. 

```text
                     +-------------------+
                     |                   |
                     |  Identity Provider|
                     |    (Okta / Azure) |
                     |                   |
                     +--------+----------+
                              | (1) SAML / OIDC Auth
                              v
+---------------+    +-------------------+    +---------------------+
|               |    |                   |    |                     |
|  Remote User  +--->+  Access Gateway   +--->+ Device Posture Check|
|   (Laptop)    |    | (Cloudflare /     |    | (CrowdStrike /      |
|               |    |  Tailscale)       |    |  Intune)            |
+---------------+    +---------+---------+    +---------------------+
     (2) Request               |
         Access                | (3) Context verified, policy evaluated
                               v
                     +-------------------+
                     |                   |
                     | Internal Network  |
                     |                   |
                     |  +-------------+  |
                     |  |  GitLab     |  |
                     |  |  (Code)     |  |
                     |  +-------------+  |
                     |                   |
                     |  +-------------+  |
                     |  | Jenkins     |  |
                     |  | (CI/CD)     |  |
                     |  +-------------+  |
                     |                   |
                     +-------------------+
```

**Flow:**
1. User attempts to access `git.internal.corp.com`.
2. The Access Gateway intercepts the request and redirects the user to the Identity Provider (IdP) for strong authentication (MFA).
3. The Gateway queries the Device Posture provider to ensure the endpoint is compliant (e.g., firewall enabled, OS patched, EDR running).
4. If both Identity and Device Posture pass the defined policy, a micro-tunnel is established specifically to the GitLab server—no other internal lateral access is granted.

## 3. Tech Stack

| Component | Tool / Technology | Purpose |
| :--- | :--- | :--- |
| **Identity Provider (IdP)** | Okta | Centralized user authentication, MFA, and role assignment. |
| **Access Gateway** | Cloudflare Access (Zero Trust) | Identity-aware proxy edge network that enforces access policies. |
| **Device Posture** | Microsoft Intune / CrowdStrike | Evaluates endpoint health (OS version, disk encryption, EDR presence). |
| **Gateway Agent** | `cloudflared` (Docker) | Lightweight daemon installed on internal servers to create outbound-only secure tunnels to the edge. |
| **Internal Apps** | GitLab CE, Jenkins | Target applications hosted on internal private subnets. |
| **Infrastructure as Code** | Terraform | Managing ZTNA policies and tunnel configurations. |

## 4. Step-by-Step Build

### Phase 1: Identity & Authentication Foundation
1. Integrate Cloudflare Zero Trust with Okta using OIDC.
2. Synchronize user groups (e.g., `Engineering`, `DevOps`, `Contractors`) from Okta to the Access Gateway.
3. Enforce mandatory hardware-based MFA (e.g., YubiKey) for all technical staff in Okta.

### Phase 2: Secure Tunnel Deployment
1. Deploy the `cloudflared` daemon alongside internal applications (GitLab, Jenkins) using Docker.
2. Configure the daemon to establish outbound connections to the Cloudflare edge, eliminating the need to open inbound firewall ports.
3. Map internal IP/ports to external proxy hostnames (e.g., `gitlab.corp.com`).

### Phase 3: Device Posture Integration
1. Integrate the endpoint management system (Intune) with the Access Gateway via API.
2. Define a posture profile: endpoints must have BitLocker/FileVault enabled, run OS version X or higher, and have CrowdStrike Falcon active.

### Phase 4: Policy Enforcement & Micro-segmentation
1. Create granular access policies. 
2. Ensure `Engineering` can reach GitLab, but only `DevOps` can reach the Jenkins admin interface.
3. Apply the device posture check as an absolute prerequisite for all access.

## 5. Config Snippets

### Cloudflare Access Policy (Terraform)
This snippet creates an access policy allowing only the Engineering group to access GitLab, provided their device passes the posture check.

```hcl
# Access Application for internal GitLab
resource "cloudflare_access_application" "gitlab" {
  zone_id          = var.cloudflare_zone_id
  name             = "Internal GitLab"
  domain           = "git.corp.com"
  session_duration = "12h"
}

# Policy allowing Engineering group, requiring healthy device
resource "cloudflare_access_policy" "gitlab_engineering" {
  application_id = cloudflare_access_application.gitlab.id
  zone_id        = var.cloudflare_zone_id
  name           = "Allow Engineering - Healthy Devices"
  precedence     = 1
  decision       = "allow"

  # Include users in the Okta "Engineering" group
  include {
    okta {
      name                 = "Engineering"
      identity_provider_id = var.okta_idp_id
    }
  }

  # Require the device to pass the Intune posture check
  require {
    device_posture = [cloudflare_device_posture_rule.intune_compliant.id]
  }
}
```

### Docker Compose for Gateway Agent (`cloudflared`)
Deploying the lightweight tunnel daemon next to the internal GitLab instance. Notice there are no exposed ports.

```yaml
version: '3.8'

services:
  # Internal Application
  gitlab:
    image: 'gitlab/gitlab-ce:latest'
    restart: always
    environment:
      GITLAB_OMNIBUS_CONFIG: |
        external_url 'https://git.corp.com'

  # ZTNA Gateway Agent (Tunnel)
  cloudflared:
    image: cloudflare/cloudflared:latest
    restart: always
    command: tunnel run
    environment:
      - TUNNEL_TOKEN=${CLOUDFLARE_TUNNEL_TOKEN}
    depends_on:
      - gitlab
```

## 6. Deployment Steps

1. **IdP Integration:** Navigate to the Zero Trust dashboard -> Settings -> Authentication. Add Okta via OIDC by providing the Client ID, Client Secret, and Okta domain.
2. **Device Posture Setup:** In the dashboard, add an Intune integration. Provide the Azure AD Tenant ID and Client credentials with `DeviceManagementManagedDevices.Read.All` graph permissions.
3. **Tunnel Creation:** 
   - Run `cloudflared tunnel create gitlab-tunnel` to generate credentials.
   - Route traffic: `cloudflared tunnel route dns gitlab-tunnel git.corp.com`.
4. **Deploy Agent:** Inject the generated `TUNNEL_TOKEN` into the deployment pipeline and spin up the Docker compose stack on the internal DMZ host.
5. **Testing:** Attempt to access `git.corp.com` from an unmanaged personal device (should be blocked). Attempt from a managed, compliant device (should redirect to Okta, then grant access).

## 7. Evaluation & Monitoring

- **Monitoring Tools:** Datadog integration with Cloudflare Logpush.
- **Key Metrics:**
  - **Access Denies vs. Allows:** Spikes in denies may indicate a misconfigured posture rule or an active credential stuffing attack.
  - **Posture Failure Reasons:** Tracking which devices fail and why (e.g., missing patches) helps IT proactively reach out to users.
  - **Session Latency:** TTFB (Time to First Byte) through the proxy to ensure developers aren't experiencing slowdowns during `git clone` operations.

## 8. Cost Analysis

*Rough estimates based on a 200-person engineering team:*

| Expense Category | Estimated Cost | Notes |
| :--- | :--- | :--- |
| **Cloudflare Zero Trust** | ~$7/user/month | Covers Access and Gateway features. |
| **Okta SSO & MFA** | ~$6/user/month | Varies based on exact SKU. |
| **Compute (Agent hosting)** | ~$40/month | Small VM (t3.medium) for running Dockerized `cloudflared`. |
| **Total Estimated Monthly** | **~$2,640** | Significantly cheaper and easier to manage than enterprise VPN appliances and dedicated leased lines. |

## 9. Production Gotchas

- **Break-Glass Procedures:** If Okta goes down, nobody can access infrastructure to fix it. *Solution:* Maintain an isolated, heavily-audited break-glass local admin account with emergency YubiKeys stored in a physical safe.
- **Latency Overhead:** Routing SSH traffic (for Git over SSH) through a web proxy can sometimes increase latency. *Solution:* Use the edge provider's optimized routing paths and ensure the access gateway agent is hosted geographically close to the application server.
- **User Friction During Onboarding:** Device posture checks can fail for obscure reasons (e.g., a background service disabled a firewall). *Solution:* Provide extremely clear, self-service error pages detailing *exactly* which posture check failed and how the user can fix it, rather than a generic "Access Denied."
- **CLI/API Access:** Web browsers handle OIDC redirects gracefully; CLI tools do not. *Solution:* Configure short-lived service tokens for CI/CD pipelines, and use local agent helpers (e.g., `cloudflared access ssh-config`) to seamlessly wrap terminal connections.

## 10. Lessons Learned

- **Micro-segmentation is hard but worth it:** Moving from "everyone on the VPN can see everything" to "users can only see specific apps" requires a deep understanding of application dependencies. We initially broke several internal build scripts that relied on undocumented lateral API calls.
- **Device posture is a moving target:** OS updates frequently change registry keys or configurations that posture checks rely on. Building a robust process to test posture rules against beta OS releases is critical to prevent Monday-morning lockouts.
- **User experience improved:** Despite the initial friction of device health requirements, users ultimately preferred the ZTNA approach. Not having to remember to "turn on the VPN" and experiencing faster, localized application access via the edge proxy led to positive feedback from the engineering organization.
