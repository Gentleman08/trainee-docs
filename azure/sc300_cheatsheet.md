[🏠 Home](../README.md) · [Azure](README.md)

# 🔐 SC-300 Identity & Access Administrator — Cheatsheet

> **Audience:** AZ-104 passed, beginner to SC-300
> **Format:** Term → one-liner plain English definition
> **Exam Domains:** Identity Management · Authentication & Access · App Access · Identity Governance

---

## How to Read This

If you've done AZ-104, you know Azure resources and RBAC. SC-300 is about **who gets in, how they prove it, and who decides**. Think of it as the "bouncer + guest list + ID check" layer of Azure.

```
  AZ-104 = "Set up the building (VMs, VNets, storage)"
  SC-300 = "Control who enters, how they prove identity, and review the guest list"
```

---

## Domain Weights

| Domain | Weight |
|--------|--------|
| 1. Implement an identity management solution | ~25–30% |
| 2. Implement authentication & access management | ~25–30% |
| 3. Implement access management for apps | ~15–20% |
| 4. Plan & implement identity governance | ~25–30% |

---

# Domain 1 — Identity Management

---

## 1.1 Core Concepts

| Term | One-liner Definition |
|------|----------------------|
| **Microsoft Entra ID** | Microsoft's cloud identity service — the "login system" for Azure, M365, and your apps. Previously called Azure Active Directory (Azure AD). |
| **Tenant** | Your organization's private slice of Entra ID — like your own walled-off directory in the cloud. |
| **Directory** | The database inside your tenant that stores users, groups, and apps. |
| **Subscription** | Your Azure billing account — linked to a tenant but different from it. One tenant can have many subscriptions. |
| **Identity** | Anything that can be identified and authenticated — a user, app, device, or service. |
| **Principal** | An identity that has been granted permissions (user principal, service principal, managed identity). |
| **Object** | Any entity stored in Entra ID — users, groups, apps, devices are all "objects." |
| **UPN (User Principal Name)** | The login username format — looks like an email: `alice@company.com`. |
| **Object ID** | A unique GUID that Entra ID assigns to every object (user, group, app). Never changes even if the name changes. |

---

## 1.2 User Types

| Term | One-liner Definition |
|------|----------------------|
| **Member user** | A regular employee/internal user who lives in YOUR tenant's directory. |
| **Guest user** | An external person (from another org or personal email) invited into your tenant via B2B. They live in their own tenant but get limited access to yours. |
| **Cloud-only user** | A user that exists ONLY in Entra ID — not synced from on-premises AD. Created directly in the portal or via PowerShell. |
| **Synced user** | A user that was created in on-premises Active Directory and synced up to Entra ID via Entra Connect (formerly Azure AD Connect). |
| **Break-glass account** | An emergency admin account kept outside of normal Conditional Access policies — used only when all other admin access is locked out. Must have MFA method different from regular admins. |
| **Service account** | A non-human account used by an application or service to authenticate and perform tasks. |

---

## 1.3 Authentication Methods (Who You Are)

| Term | One-liner Definition |
|------|----------------------|
| **Password Hash Sync (PHS)** | Copies a hashed version of your on-prem AD passwords to Entra ID so users log in directly in the cloud — no on-prem server needed at sign-in time. |
| **Pass-through Authentication (PTA)** | At sign-in time, Entra ID forwards the password check to your on-premises AD via a lightweight agent — password never stored in cloud. |
| **Federation (AD FS)** | Your on-prem AD FS server handles ALL authentication. Entra ID trusts whatever AD FS says. Most complex, most control. |
| **Managed Domain** | An Entra ID domain you own and control (e.g., `company.com` added and verified in Entra ID). |
| **Verified domain** | A domain name you've proven ownership of in Entra ID by adding a DNS TXT record. Required before users can have UPNs on that domain. |
| **Primary domain** | The default domain used for new users if no other domain is specified. |

---

## 1.4 Entra Connect & Hybrid Identity

| Term | One-liner Definition |
|------|----------------------|
| **Entra Connect (Azure AD Connect)** | The on-premises software that syncs users, groups, and passwords from your Windows Server AD to Entra ID. |
| **Entra Connect Sync** | The classic sync engine inside Entra Connect — runs on a server you manage. |
| **Entra Cloud Sync** | A newer, lighter sync agent — runs without a dedicated sync server, managed fully from the cloud. Good for simpler scenarios. |
| **Hybrid Identity** | The state of having identities that exist BOTH on-premises AD and in Entra ID at the same time. |
| **Seamless SSO** | Users on domain-joined machines are automatically logged in without typing credentials again — works with PHS or PTA. |
| **Writeback** | Sync direction from Entra ID BACK to on-prem AD. E.g., password writeback lets users reset passwords in the cloud and have it apply on-prem too. |
| **Password Writeback** | When a user resets their password via SSPR in Entra ID, that new password is written back to on-prem AD automatically. Requires Entra Connect. |
| **Group Writeback** | M365 Groups or Entra ID groups can be written back to on-premises AD as distribution or security groups. |
| **Device Writeback** | Devices registered in Entra ID are written back to on-prem AD — enables on-prem resources to recognize cloud-registered devices. |
| **Staging Mode** | An Entra Connect server that syncs and imports data but does NOT export to Entra ID — used for testing a second sync server before making it active. |
| **Source Anchor** | The attribute that uniquely identifies an object and links the on-prem AD object to the Entra ID object — usually `objectGUID` or `mS-DS-ConsistencyGuid`. |

---

## 1.5 Groups

| Term | One-liner Definition |
|------|----------------------|
| **Security group** | Used to manage access to resources (assign RBAC roles, app access, Conditional Access). No email inbox. |
| **Microsoft 365 group** | Has an email inbox, shared calendar, Teams, SharePoint — for collaboration. Can also be used for some access scenarios. |
| **Assigned group** | You manually add/remove members. Simple, full control. |
| **Dynamic group** | Membership is auto-managed by rules (e.g., "all users where Department = Engineering"). Members added/removed automatically when attributes change. |
| **Dynamic membership rule** | The query that defines who belongs to a dynamic group — e.g., `user.department -eq "Sales"`. Requires Entra ID P1. |
| **Nested group** | A group inside another group. Entra ID supports nesting but dynamic groups cannot be nested inside other dynamic groups. |
| **Bulk operations** | Creating/inviting/deleting many users at once via a CSV file upload in the portal. |

---

## 1.6 External Identities

| Term | One-liner Definition |
|------|----------------------|
| **B2B (Business to Business)** | Inviting users from OTHER organizations or personal emails into YOUR tenant as guests so they can access your apps/resources. |
| **B2B Collaboration** | The specific feature that lets you invite external users — they authenticate with their OWN identity provider (their company's Azure AD, Google, etc.). |
| **B2B Direct Connect** | A deeper trust between two Entra ID tenants — users from Org B can access Org A's Teams channels directly without being a guest. Uses cross-tenant access settings. |
| **B2C (Business to Consumer)** | A SEPARATE tenant type for consumer apps — lets external users (public, with Gmail/Facebook) self-register and log in to YOUR app. NOT the same as B2B. |
| **Cross-tenant access settings** | Rules that control what external Entra ID tenants can do in your tenant — can block/allow MFA trust, device compliance trust, and B2B direct connect per tenant. |
| **External collaboration settings** | Tenant-wide settings that control whether your users can invite guests, and from which domains. |
| **Guest invite settings** | Controls WHO in your org can invite guests — Admins only, Members and Admins, or Anyone. |
| **Email OTP** | One-time passcode sent via email — allows guests without a Microsoft account or supported social identity to authenticate. |

---

# Domain 2 — Authentication & Access Management

---

## 2.1 MFA (Multi-Factor Authentication)

| Term | One-liner Definition |
|------|----------------------|
| **MFA** | Requiring TWO forms of verification to sign in: something you know (password) + something you have/are (phone, fingerprint). |
| **Authenticator app** | Microsoft Authenticator — the recommended MFA method. Sends push notifications or generates TOTP codes. |
| **TOTP (Time-based One-Time Password)** | A 6-digit code from an authenticator app that changes every 30 seconds — works offline. |
| **FIDO2 security key** | A physical USB/NFC key (e.g., YubiKey) that provides passwordless, phishing-resistant authentication. |
| **Windows Hello for Business** | Biometric (face/fingerprint) or PIN on a Windows device that replaces password — the PIN/biometric unlocks a device-bound key, not a password sent over the network. |
| **Passwordless authentication** | Sign in WITHOUT a password — using the Authenticator app, FIDO2 key, or Windows Hello. Phishing-resistant. |
| **Authentication strength** | A policy that defines WHICH MFA methods are acceptable for a particular access scenario — e.g., require FIDO2 for admin roles. |
| **Per-user MFA** | The old way of forcing MFA on individual accounts — being replaced by Conditional Access. Still exists but not recommended. |
| **Security defaults** | A set of baseline security settings Microsoft turns on by default for free tenants — forces MFA for all users, blocks legacy auth. Cannot be customized. |
| **Combined registration** | A single page where users register BOTH SSPR methods and MFA methods at once — reduces two separate registration experiences to one. |
| **MFA registration policy** | A policy (in Identity Protection) that requires users to register for MFA — can be targeted to specific users/groups. |
| **Number matching** | A security feature for Authenticator push notifications — user must type the number shown on the login screen into the app to approve, preventing MFA fatigue attacks. |
| **MFA fatigue attack** | An attacker spams a user with MFA push requests hoping they approve one by accident — number matching and additional context prevent this. |

---

## 2.2 Self-Service Password Reset (SSPR)

| Term | One-liner Definition |
|------|----------------------|
| **SSPR** | Lets users reset their OWN password without calling the helpdesk — they verify identity using pre-registered methods (phone, email, authenticator). |
| **SSPR registration** | The process of a user pre-registering their reset methods before they need to use SSPR — must be done before any reset attempt. |
| **Authentication methods for SSPR** | The verification options users register: email, mobile phone, office phone, security questions, authenticator app, app code. |
| **Number of methods required** | How many methods a user must verify before resetting — typically 1 or 2. |
| **Security questions** | A fallback SSPR method — users answer pre-set questions. Least secure SSPR method; not recommended for high-security orgs. |
| **SSPR + Password Writeback** | When SSPR resets a cloud password AND also updates the on-premises AD password — requires Entra Connect with Password Writeback enabled. |
| **SSPR scope** | Who SSPR is enabled for: None (disabled), Selected (specific group), All (everyone). |

---

## 2.3 Conditional Access

| Term | One-liner Definition |
|------|----------------------|
| **Conditional Access (CA)** | "If [conditions are met], then [require this / block this]" — it's the policy engine for access decisions after a user tries to sign in. |
| **CA Policy** | A rule that has: Assignments (who, what app, what conditions) + Access controls (grant/block/session). |
| **Signal** | The information CA uses to make decisions — user identity, device state, location, app being accessed, sign-in risk. |
| **Conditions** | The "IF" part of a CA policy — user/group, cloud app, device platform, location, client app, sign-in risk, user risk. |
| **Grant control** | The "THEN" part — what to enforce when conditions match: Require MFA, require compliant device, require hybrid AD join, block access. |
| **Session control** | Limits what a user can DO after sign-in — e.g., disable file download, sign-in frequency, persistent browser session. |
| **Named location** | A defined IP range or country/region — used in CA conditions to say "if signing in from [location]." |
| **Trusted location** | Named locations marked as trusted (e.g., your office IP range) — MFA can be skipped for trusted locations. |
| **Block legacy authentication** | A CA policy that blocks old auth protocols (Basic Auth, SMTP, IMAP, POP3, older Office clients) that don't support MFA. Critical security baseline. |
| **Sign-in frequency** | A session control that forces re-authentication after X hours/days, even if the session is still active. |
| **Persistent browser session** | Controls whether "Stay signed in?" is allowed — session can persist across browser restarts. |
| **Compliant device** | A device that meets your Intune compliance policies — CA can require this before granting access. |
| **Hybrid Azure AD joined device** | A Windows device joined to both on-prem AD AND Entra ID — CA can require this as a condition. |
| **App-enforced restriction** | A session control that passes the device/compliance state to the app (SharePoint/Exchange) — the APP enforces restrictions (e.g., no download on unmanaged device). |
| **MCAS session control** | Routes the session through Microsoft Defender for Cloud Apps proxy — enables real-time monitoring and controls on app activity. |
| **Report-only mode** | A CA policy that runs but doesn't ENFORCE — logs what WOULD have happened. Used for testing policies before enabling. |
| **What If tool** | A tool in the CA portal — you simulate a specific sign-in scenario to see which CA policies would apply. |
| **CA policy exclusions** | Specific users/groups/roles excluded from a policy — break-glass accounts should always be excluded from all CA policies. |

---

## 2.4 Identity Protection

| Term | One-liner Definition |
|------|----------------------|
| **Entra ID Identity Protection** | A service that automatically detects suspicious sign-in behaviors and compromised users using Microsoft's threat intelligence. Requires P2. |
| **Risk** | The probability that something bad has happened — either with a specific sign-in (sign-in risk) or with a user account overall (user risk). |
| **Sign-in risk** | The probability that THIS specific sign-in wasn't performed by the legitimate user — based on signals like impossible travel, anonymous IP, unfamiliar location. |
| **User risk** | The probability that THIS user's account is compromised — based on leaked credentials (dark web), unusual patterns across sign-ins. |
| **Risk level** | Low / Medium / High — how confident Identity Protection is that something bad happened. |
| **Sign-in risk policy** | Triggered per sign-in — if this specific attempt looks risky, block it or require MFA before allowing. |
| **User risk policy** | Triggered for a user account — if this user is flagged as compromised, require them to change their password before accessing anything. |
| **Risk remediation** | Resolving a risk: user completes MFA (remediates sign-in risk), or user changes password (remediates user risk). |
| **Risk dismissal** | An admin manually marks a detected risk as "dismissed" — tells Identity Protection this was a false positive. |
| **Risky users report** | A report listing all users currently flagged with a risk level — admins can investigate, confirm compromise, or dismiss. |
| **Risky sign-ins report** | A report of all sign-ins that were detected as potentially risky — useful for investigation. |
| **Risk detection** | A specific signal that triggered a risk — e.g., "Anonymous IP address," "Atypical travel," "Password spray." |
| **Leaked credentials** | Microsoft monitors dark web/paste sites for username+password combos and flags matching accounts — triggers user risk. |
| **Impossible travel** | Sign-in from Paris then New York within 2 hours — physically impossible, so it's flagged as a risk. |

---

## 2.5 Privileged Identity Management (PIM)

| Term | One-liner Definition |
|------|----------------------|
| **PIM** | A feature that makes privilege TEMPORARY — instead of always having admin roles, you REQUEST them when needed and they expire. Requires P2. |
| **Eligible assignment** | A user is ELIGIBLE for a role but doesn't have it yet — they must activate it when they need it. |
| **Active assignment** | A user has the role RIGHT NOW and can use it — could be always-active (permanent) or a temporary activation. |
| **Role activation** | The act of a user turning their "eligible" role into an "active" one — may require MFA, justification, approval. |
| **Activation duration** | How long an activated role stays active — e.g., max 8 hours. After that it expires automatically. |
| **Approval requirement** | When a role activation requires ANOTHER admin to approve before it becomes active — adds a human check. |
| **Justification** | A reason the user types when activating a role — "I need owner access to fix incident ticket #1234." |
| **PIM notifications** | Emails/alerts sent to admins when someone activates a role, when an eligible assignment is about to expire, etc. |
| **Access review in PIM** | A recurring review of who has eligible/active role assignments — reviewers confirm they still need the access or it's removed. |
| **Permanent active** | A user has an always-on role assignment with no expiry — risky, not recommended for sensitive roles. |
| **Time-bound assignment** | An assignment that automatically expires after a set date — e.g., eligible for Owner role for 6 months. |
| **PIM for Groups** | PIM extended to group membership — users activate their membership in a security group instead of a role. The group can then be assigned to apps or resources. |
| **PIM for Azure resources** | PIM applied to Azure RBAC roles (like Contributor, Owner on subscriptions/resource groups) — not just Entra ID roles. |
| **PIM audit history** | A log of all activations, approvals, and assignment changes — critical for compliance. |

---

## 2.6 Entra ID Roles

| Term | One-liner Definition |
|------|----------------------|
| **Entra ID roles** | Control WHO can manage the DIRECTORY — users, groups, apps, policies. Examples: Global Admin, User Admin, Security Admin. |
| **Global Administrator** | The most powerful Entra ID role — can manage everything in the directory and take over any Azure subscription. |
| **User Administrator** | Can create, update, delete users and groups — but NOT global admins or other admins above their level. |
| **Authentication Administrator** | Can reset authentication methods (MFA methods, passwords) for non-admin users. |
| **Privileged Role Administrator** | Can manage PIM and role assignments — a very sensitive role. |
| **Security Administrator** | Can read and manage security policies, Identity Protection, Defender, and Secure Score settings. |
| **Security Reader** | Read-only access to all security information — can't change anything. |
| **Application Administrator** | Can manage app registrations and enterprise apps — but NOT consent to permissions on behalf of the organization. |
| **Cloud Application Administrator** | Same as Application Administrator but CANNOT manage on-premises app proxy. |
| **Conditional Access Administrator** | Can create and manage Conditional Access policies. |
| **Least privilege principle** | Give users ONLY the permissions they need for their job — nothing more. Core security principle throughout SC-300. |
| **Custom role (Entra ID)** | A custom-built Entra ID role with specific permissions — requires Entra ID P1 or P2. |
| **Administrative unit (AU)** | A container that scopes admin roles to a SUBSET of the directory — e.g., a User Admin who can only manage users in the "India" AU. |

---

# Domain 3 — Access Management for Applications

---

## 3.1 App Registration vs Enterprise App

| Term | One-liner Definition |
|------|----------------------|
| **App Registration** | The definition of an application in Entra ID — its identity, what permissions it needs, where to redirect after login. Created by developers. |
| **Enterprise Application (Service Principal)** | The "local instance" of an app in YOUR tenant — controls who can use it, what consent was granted. Created automatically when you add an app or register one. |
| **Application ID (Client ID)** | The unique identifier for an app registration — like the app's username. |
| **Client Secret** | A password for an app to authenticate to Entra ID — must be rotated before expiry. |
| **Certificate** | A more secure alternative to client secret for app authentication — uses public/private key pair. |
| **Redirect URI** | The URL Entra ID sends the user back to after authentication — must be pre-registered to prevent token hijacking. |
| **Single-tenant app** | An app that only accepts sign-ins from users in YOUR tenant. |
| **Multi-tenant app** | An app that can accept sign-ins from users in ANY Entra ID tenant — like SaaS products. |
| **Publisher verification** | A verified checkmark on an app showing the publisher's identity has been confirmed by Microsoft via their Microsoft Partner Network ID. |

---

## 3.2 Permissions & Consent

| Term | One-liner Definition |
|------|----------------------|
| **Permission** | What an app is allowed to do — e.g., "Read user profiles," "Send mail as user," "Read all groups." |
| **Scope** | The specific permission string used in OAuth requests — e.g., `User.Read`, `Mail.Send`. |
| **Delegated permission** | The app acts ON BEHALF OF a signed-in user — it can do what the user is allowed to do. User must consent. |
| **Application permission** | The app acts AS ITSELF with no user present (daemon/service) — much higher privilege. ADMIN must consent, not the user. |
| **Consent** | A user or admin saying "Yes, this app is allowed to access this data." |
| **User consent** | An individual user grants an app access to their own data. Only works for low-risk delegated permissions. |
| **Admin consent** | An admin grants an app access to data across the WHOLE org — required for application permissions and some high-privilege delegated permissions. |
| **Tenant-wide admin consent** | Admin consent granted for ALL users in the tenant — nobody else needs to consent individually. |
| **Consent policy** | A setting that controls whether users can consent at all, and to which types of apps — can restrict to verified publishers only. |
| **Pre-authorized application** | An application explicitly listed in another app's registration as allowed — it gets access without user consent. |

---

## 3.3 OAuth 2.0 & OpenID Connect (OIDC)

| Term | One-liner Definition |
|------|----------------------|
| **OAuth 2.0** | The authorization framework — defines how an app gets ACCESS tokens to call APIs on a user's or app's behalf. |
| **OpenID Connect (OIDC)** | Built on top of OAuth 2.0 — adds AUTHENTICATION (who you are) via an ID token. Most sign-in flows use OIDC. |
| **Access token** | A short-lived token proving an app has permission to call an API — presented in the Authorization header. |
| **ID token** | A token containing claims about WHO the user is (name, email, object ID) — used by the APP to know who logged in. |
| **Refresh token** | A longer-lived token used to get new access tokens without re-prompting the user to log in. |
| **Authorization code flow** | The standard login flow for web apps — user logs in, gets an authorization code, app exchanges code for tokens. |
| **PKCE** | Proof Key for Code Exchange — security extension to auth code flow for apps that can't keep a client secret (SPAs, mobile apps). |
| **Client credentials flow** | An app authenticates as ITSELF (no user) using client ID + secret/certificate — for daemons and backend services. |
| **Claim** | A piece of information in a token — e.g., `name`, `email`, `roles`, `oid` (object ID), `tid` (tenant ID). |
| **Token lifetime** | How long a token is valid — access tokens default to 1 hour; can be customized via Token Lifetime Policy. |

---

## 3.4 App Proxy & SSO

| Term | One-liner Definition |
|------|----------------------|
| **Application Proxy** | Lets you publish on-premises web apps securely to external users WITHOUT opening firewall ports — a reverse proxy in the cloud. |
| **App Proxy Connector** | A lightweight agent installed on-premises that connects outbound to Entra ID — no inbound firewall rules needed. |
| **SSO (Single Sign-On)** | Log in once, access many apps without logging in again — the holy grail of identity. |
| **SAML SSO** | A standard for enterprise app SSO — the app and Entra ID exchange XML-based tokens. Common for legacy SaaS apps. |
| **OIDC/OAuth SSO** | Modern SSO standard — uses JSON tokens. Used by most new apps and Microsoft's own apps. |
| **Password-based SSO** | Entra ID stores the app's username/password and fills them in automatically — for apps that only support basic login forms. |
| **Linked SSO** | Just adds an app to My Apps portal with a link — no actual SSO, just a bookmark. |
| **My Apps portal** | The portal at `myapps.microsoft.com` where users see all their assigned apps and can launch them with SSO. |
| **SAML Assertion** | The XML document sent from Entra ID to the app during SAML SSO — contains the user's identity and attributes. |
| **App Roles** | Custom roles defined within an app registration — users/groups assigned to these roles get the role claim in their token. |
| **Claims mapping** | Customizing what information (claims) is included in the token sent to an app — e.g., send `employeeID` as a custom claim. |

---

## 3.5 Managed Identities

| Term | One-liner Definition |
|------|----------------------|
| **Managed Identity** | An identity that Azure manages for you — an Azure resource (VM, Function, App Service) gets an automatic identity without you needing to store credentials anywhere. |
| **System-assigned managed identity** | Tied to ONE specific resource — created and deleted with the resource. One resource = one identity. |
| **User-assigned managed identity** | A standalone identity you create separately and can assign to MULTIPLE resources. Survives resource deletion. |
| **IMDS (Instance Metadata Service)** | The Azure endpoint (`169.254.169.254`) that a VM or resource calls to get a token for its managed identity — only accessible from inside Azure. |

---

# Domain 4 — Identity Governance

---

## 4.1 Entitlement Management

| Term | One-liner Definition |
|------|----------------------|
| **Entitlement Management** | A system for packaging access (apps, groups, SharePoint sites) into "access packages" that users can REQUEST — with approvals, expiry, and auto-removal. Requires P2. |
| **Access package** | A bundle of resources (group membership + app access + SharePoint site) that a user can request as a single unit. |
| **Catalog** | A container that holds access packages and the resources they reference — like a folder for related access packages. |
| **Policy (Entitlement)** | Rules for WHO can request an access package, WHO must approve, and HOW LONG access lasts. |
| **Requestor** | The person asking for an access package — could be an employee, a guest, or a manager on behalf of someone. |
| **Approver** | The person who approves or denies an access package request. Can be a manager, a specific person, or the resource owner. |
| **Access package assignment** | When a user's request is approved — they now have the access defined in the package. |
| **Assignment expiry** | Access packages can have an expiry date — access is automatically removed when it expires unless renewed. |
| **Connected organization** | An external org (another Entra tenant or a domain) that you allow to request access packages — enables B2B guest access requests. |
| **Auto-assignment policy** | Access is automatically granted (no request needed) based on user attributes — e.g., "All Sales department users get this access package." |

---

## 4.2 Access Reviews

| Term | One-liner Definition |
|------|----------------------|
| **Access Review** | A scheduled check where reviewers confirm "does this person still need this access?" — and access is removed if not confirmed. Requires P2. |
| **Reviewer** | Who does the review — can be the manager, the resource owner, the user themselves (self-review), or specific people. |
| **Review scope** | What is being reviewed — group members, app assignments, role assignments (in PIM), guest users. |
| **Self-review** | Users review their OWN access — they confirm they still need it or it gets removed. |
| **Auto-apply results** | When a review ends, results are automatically applied — no-response = access removed (based on policy). No manual admin action needed. |
| **Recommendations** | Access Reviews can show reviewers a recommendation (based on sign-in activity) — "this user hasn't signed in for 90 days, suggest removing." |
| **Multi-stage review** | A review with multiple rounds — e.g., manager reviews first, then security team reviews what the manager approved. |
| **Inactive users** | Users who haven't signed in for a long time — Access Reviews can target these specifically to clean up stale accounts. |

---

## 4.3 Lifecycle Workflows

| Term | One-liner Definition |
|------|----------------------|
| **Lifecycle Workflows** | Automated processes that trigger at key moments in an employee's lifecycle — onboarding (joiner), role change (mover), offboarding (leaver). Requires P2/Governance. |
| **Joiner workflow** | Runs when a new employee joins — e.g., send welcome email, add to groups, generate temp access pass. |
| **Mover workflow** | Runs when an employee changes department/role — update group memberships to reflect new role. |
| **Leaver workflow** | Runs when an employee leaves — disable account, remove group memberships, revoke sessions. |
| **Trigger** | What starts a lifecycle workflow — attribute changes (like `employeeHireDate`) or schedule. |
| **Task** | An action performed by a workflow — "Add user to group," "Send email," "Disable account," "Generate TAP." |
| **TAP (Temporary Access Pass)** | A time-limited passcode that lets a new user (or user who lost MFA device) set up their MFA methods without needing a password. Very useful for onboarding. |

---

## 4.4 Terms of Use & Compliance

| Term | One-liner Definition |
|------|----------------------|
| **Terms of Use (ToU)** | A document users must accept before accessing a resource — set up in Entra ID and enforced via Conditional Access. |
| **Audit logs** | A record of ALL changes made in Entra ID — who created/modified/deleted what, when. Retained for 30 days (longer with Log Analytics). |
| **Sign-in logs** | A record of all sign-in attempts — succeeded, failed, risky, MFA prompted. Retained for 30 days. |
| **Provisioning logs** | Logs showing automatic user provisioning/deprovisioning activity (via SCIM or HR-driven provisioning). |
| **SIEM integration** | Sending Entra ID logs (sign-in, audit, risk) to a SIEM like Microsoft Sentinel for long-term storage and threat detection. |

---

## 4.5 HR-Driven Provisioning

| Term | One-liner Definition |
|------|----------------------|
| **HR-driven provisioning** | Automatically create/update/disable user accounts in Entra ID based on an HR system (Workday, SAP SuccessFactors) — employee joins HR system, account created automatically. |
| **SCIM (System for Cross-domain Identity Management)** | A standard API protocol for automatically provisioning and deprovisioning users between identity providers and apps. |
| **Provisioning agent** | A lightweight on-premises agent that enables cloud HR provisioning to write accounts to on-premises AD (not just cloud). |
| **Attribute mapping** | Defines which HR system field maps to which Entra ID attribute — e.g., HR `WorkEmail` → Entra `userPrincipalName`. |
| **Inbound provisioning** | Users created IN Entra ID from an external source (HR system) — "users flow IN." |
| **Outbound provisioning** | Users provisioned FROM Entra ID TO target apps (Salesforce, ServiceNow) — "users flow OUT." |

---

# Common Confusions — Side by Side

---

## Authentication vs Authorization

| | Authentication | Authorization |
|---|---|---|
| **Question** | WHO are you? | What are you ALLOWED to do? |
| **Proves** | Identity | Permission |
| **Example** | Logging in with password + MFA | RBAC role says you can read this storage account |
| **In SC-300** | MFA, SSPR, Identity Protection | RBAC roles, CA policies, app permissions |

---

## PIM vs Access Reviews vs Entitlement Management

| | PIM | Access Reviews | Entitlement Management |
|---|---|---|---|
| **What it controls** | Privileged ROLES (admin roles) | Existing access — is it still needed? | Access REQUESTS and lifecycle |
| **Who uses it** | Admins needing temp elevated access | Reviewers auditing group/role membership | Employees requesting app/group access |
| **Key concept** | Activate roles on-demand | Periodic re-certification | Request → Approve → Expire |
| **License** | P2 | P2 | P2 |

---

## Guest (B2B) vs Consumer (B2C)

| | B2B Guest | B2C |
|---|---|---|
| **Who** | Corporate users from other orgs | Public consumers (Gmail, Facebook) |
| **How they sign in** | With their OWN org's identity | Social identity or email OTP |
| **Where they live** | As guests in YOUR tenant | In a SEPARATE B2C tenant |
| **Use case** | Partner portal, shared Teams | E-commerce, public-facing app |

---

## Managed Identity vs Service Principal vs App Registration

| | App Registration | Service Principal | Managed Identity |
|---|---|---|---|
| **What** | Definition of an app — client ID, permissions | Local instance of an app in your tenant | Identity for an Azure RESOURCE (VM, Function) |
| **Credentials** | Client secret or certificate (you manage) | Inherits from app registration | None — Azure manages tokens automatically |
| **Use case** | Custom apps authenticating to APIs | SaaS apps, all apps in your tenant | Azure services calling Key Vault, Storage, etc. |

---

## Sign-in Risk vs User Risk

| | Sign-in Risk | User Risk |
|---|---|---|
| **About** | THIS specific sign-in attempt | This USER's overall account |
| **Example trigger** | Sign in from anonymous Tor IP | User's password found on dark web |
| **Remediation** | Complete MFA | Change password |
| **Policy response** | Require MFA or block | Require password change |

---

## Eligible vs Active (PIM)

| | Eligible | Active |
|---|---|---|
| **State** | Can request the role | Has the role RIGHT NOW |
| **To use it** | Must activate (MFA + justification) | Can use it immediately |
| **Duration** | Indefinite or time-bound membership | Time-limited activation (e.g., 4 hours) |
| **Risk** | Lower — not always privileged | Higher — always has elevated access |

---

## PHS vs PTA vs Federation

| | PHS | PTA | Federation (AD FS) |
|---|---|---|---|
| **Where auth happens** | Entra ID (cloud) | On-premises AD | On-premises AD FS |
| **On-prem dependency at login** | None | Yes (PTA agent) | Yes (AD FS server) |
| **Complexity** | Low | Medium | High |
| **Offline resilience** | Yes (cloud handles it) | No (agent must be up) | No (AD FS must be up) |
| **Recommended** | Yes (Microsoft's recommendation) | For specific compliance needs | Legacy/complex scenarios |

---

# License Requirements Quick Reference

| Feature | License Required |
|---------|-----------------|
| Basic Entra ID (users, groups, SSO for apps) | **Free** |
| SSPR (cloud-only) | **Free (limited)** |
| MFA via Security Defaults | **Free** |
| Conditional Access | **Entra ID P1** |
| Dynamic groups | **Entra ID P1** |
| Hybrid identity (Entra Connect) | **Entra ID P1** |
| Custom Entra ID roles | **Entra ID P1** |
| Administrative Units | **Entra ID P1** |
| PIM | **Entra ID P2** |
| Identity Protection | **Entra ID P2** |
| Access Reviews | **Entra ID P2** |
| Entitlement Management | **Entra ID P2** |
| Lifecycle Workflows | **Entra ID P2 / Governance** |
| B2C tenant | **Separate product** |

> **Tip:** Microsoft 365 E3 = P1 included. Microsoft 365 E5 = P2 included.

---

# Key Numbers to Remember

| Item | Value |
|------|-------|
| Audit log retention (default, no Log Analytics) | **30 days** |
| Sign-in log retention (default) | **30 days** |
| Access token default lifetime | **1 hour** |
| Refresh token default lifetime | **90 days sliding / 1 year max** |
| Max SSPR authentication methods to require | **2** |
| Smart lockout threshold (Entra ID default) | **10 failed attempts** |
| Global Admin PIM max activation duration | **Configurable, up to 24 hours** |
| Guest default permissions level | **Limited** (can't enumerate tenant users/groups) |

---

# SC-300 Exam Tips

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │  SC-300 THINKING FRAMEWORK                                            │
  │                                                                       │
  │  1. LEAST PRIVILEGE — Always pick the answer that grants            │
  │     the MINIMUM access needed. More access = almost never correct.   │
  │                                                                       │
  │  2. P1 vs P2 — Know which features need which license.              │
  │     If scenario says "no P2" → PIM and Identity Protection are out. │
  │                                                                       │
  │  3. THE BIG THREE work together:                                     │
  │     Conditional Access = POLICY engine (who, what, how)             │
  │     Identity Protection = RISK detection (suspicious behavior)       │
  │     PIM = PRIVILEGE management (just-in-time admin access)          │
  │                                                                       │
  │  4. MANAGED IDENTITY > SERVICE PRINCIPAL > CLIENT SECRET             │
  │     "Minimize credential management" → always Managed Identity.     │
  │                                                                       │
  │  5. BREAK-GLASS ACCOUNTS must ALWAYS be excluded from:              │
  │     - All Conditional Access policies                                │
  │     - PIM requirements                                               │
  │     - Identity Protection risk policies                             │
  │                                                                       │
  │  6. B2B ≠ B2C. Partner/corporate = B2B. Public consumer = B2C.    │
  │     This is the #1 most common exam trap.                           │
  │                                                                       │
  │  7. ADMIN CONSENT vs USER CONSENT:                                  │
  │     Application permissions = admin consent ALWAYS.                 │
  │     Delegated (low-risk) = user can consent.                        │
  │                                                                       │
  │  8. REPORT-ONLY MODE first → test CA policies without breaking      │
  │     anyone's access. Then enable when confident.                    │
  │                                                                       │
  │  9. JOINER-MOVER-LEAVER = Lifecycle Workflows                       │
  │     WHO gets what = Entitlement Management                          │
  │     STILL needs it? = Access Reviews                                │
  │     TOO MUCH privilege? = PIM                                       │
  │                                                                       │
  │  10. SCIM = outbound auto-provisioning TO apps                      │
  │      HR-driven = inbound FROM Workday/SAP into Entra ID             │
  └──────────────────────────────────────────────────────────────────────┘
```

---

*Cross-reference: [AZ-104 Exam Handbook](az104_exam_handbook.md) · [Azure RBAC Notes](../quick-reference/azure_rbac_notes.md)*


---

# Prerequisites — Windows Active Directory (AD DS)

> SC-300 is deeply tied to on-premises Windows AD. If you don't understand these terms, hybrid identity topics won't make sense.

---

## P1 — Active Directory Fundamentals

| Term | One-liner Definition |
|------|----------------------|
| **Active Directory (AD DS)** | Microsoft's on-premises directory service — the database that stores all your organization's users, computers, and policies on Windows Server. Think of it as Entra ID's older, on-prem cousin. |
| **Domain** | A logical grouping of AD objects (users, computers, groups) sharing the same AD database and security boundary — e.g., `company.local` or `company.com`. |
| **Domain Controller (DC)** | A Windows Server running AD DS — stores the directory database and handles all authentication (logins) for the domain. Every AD environment needs at least one. |
| **Forest** | The top-level container in AD — a collection of one or more domains sharing a common schema and global catalog. One forest = one AD organization. |
| **Tree** | A group of domains sharing a contiguous DNS namespace within a forest — e.g., `company.com`, `sales.company.com`, `hr.company.com`. |
| **Schema** | The blueprint of AD — defines what attributes every object type (user, computer, group) can have. Extending the schema adds custom attributes. |
| **Global Catalog (GC)** | A partial replica of ALL objects in ALL domains in the forest — lets users and apps search the entire forest from one DC. Every forest needs at least one GC server. |
| **FSMO Roles** | Five special roles only ONE DC can hold at a time — PDC Emulator, RID Master, Infrastructure Master, Schema Master, Domain Naming Master. |
| **PDC Emulator** | The most important FSMO role — handles password changes, account lockouts, time sync, and Group Policy updates. If this DC is slow, logins are slow. |
| **NTDS.dit** | The actual AD database file on every DC — contains all users, hashed passwords, groups, and objects. Protecting this file = protecting the entire domain. |
| **SYSVOL** | A shared folder on every DC storing Group Policy files and login scripts — replicated between all DCs so policies are consistent everywhere. |

---

## P2 — AD Objects

| Term | One-liner Definition |
|------|----------------------|
| **User account** | An AD object representing a person — has a username (sAMAccountName), password, and attributes like department, email, manager. |
| **Computer account** | An AD object representing a domain-joined Windows computer — like a user account but for machines. Computers authenticate to AD too. |
| **Security group (AD)** | Used to assign permissions to resources (file shares, printers) — adding a user to the group grants those permissions. |
| **Distribution group** | An email mailing list in AD — used for sending emails, NOT for assigning permissions to resources. |
| **Organizational Unit (OU)** | A folder inside AD for organizing users, computers, and groups — Group Policies are applied at the OU level, and admin delegation can be scoped per OU. |
| **Container** | A built-in AD folder (like "Users" or "Computers") — similar to OU but you CANNOT apply Group Policy to a container. Always move objects to OUs instead. |
| **sAMAccountName** | The old-style Windows login name — e.g., `alice` (no domain). Used for legacy compatibility. Often different from the UPN. |
| **Distinguished Name (DN)** | The full LDAP path to an object — e.g., `CN=Alice Smith,OU=Sales,DC=company,DC=com`. Uniquely identifies every object in the directory. |
| **SID (Security Identifier)** | A unique number assigned to every AD object — Windows uses SIDs internally for permissions, never the display name. |
| **GUID** | A 128-bit unique ID assigned to every AD object at creation — never changes even if the object is renamed or moved. |
| **userAccountControl** | A special AD attribute (a bitmask) controlling account state — whether disabled, locked out, password never expires, etc. |
| **Attribute** | A property of an AD object — users have attributes like `givenName`, `mail`, `department`, `telephoneNumber`. |

---

## P3 — Authentication Protocols

| Term | One-liner Definition |
|------|----------------------|
| **Kerberos** | The PRIMARY authentication protocol in Windows AD — uses tickets instead of sending passwords over the network. Much more secure than NTLM. |
| **KDC (Key Distribution Center)** | The service on every DC that issues Kerberos tickets — split into AS (Authentication Service) and TGS (Ticket Granting Service). |
| **TGT (Ticket Granting Ticket)** | The first Kerberos ticket a user gets after logging in — proves identity and is used to request service tickets without re-entering the password. |
| **Service Ticket (ST)** | A Kerberos ticket for a specific resource (file server, web app, SQL) — obtained from the KDC by presenting your TGT. |
| **SPN (Service Principal Name)** | A unique identifier for a service in Kerberos — tells Kerberos which account runs a specific service (e.g., `HTTP/webserver.company.com`). Misconfigured SPNs break SSO. |
| **Kerberoasting** | Attack: request service tickets for accounts with SPNs then crack them offline to get service account passwords. |
| **Unconstrained Delegation** | DANGEROUS — a service can impersonate ANY user to access ANY other service. Never use in production. |
| **Constrained Delegation** | SAFER — a service can only impersonate users to access SPECIFIC, pre-approved services. |
| **NTLM** | The older legacy authentication protocol — used when Kerberos isn't available. Sends a challenge/response. Weaker than Kerberos. |
| **Pass-the-Hash (PtH)** | Attack against NTLM — attacker steals an NTLM password hash and uses it to authenticate without knowing the actual password. |
| **Pass-the-Ticket (PtT)** | Attack against Kerberos — attacker steals a TGT from memory (e.g., Mimikatz) and uses it to authenticate as that user. |
| **Golden Ticket** | Attacker forges a TGT using the `krbtgt` account hash — gives domain admin access for up to 10 years. The most severe AD attack. |
| **Silver Ticket** | A forged service ticket created without touching the KDC — more limited than Golden Ticket but harder to detect. |
| **LDAP** | Protocol for querying and modifying AD — apps use LDAP to look up user info and check group membership. Port 389 (plain), 636 (LDAPS/TLS). |
| **LDAPS** | LDAP over TLS/SSL — encrypted LDAP. Always prefer LDAPS. Entra Connect uses LDAP to communicate with on-prem AD. |

---

## P4 — Group Policy

| Term | One-liner Definition |
|------|----------------------|
| **Group Policy (GPO)** | Settings applied to users and computers in AD — controls password policy, software installation, firewall rules, desktop settings, mapped drives. |
| **Group Policy Object (GPO)** | The container holding a set of Group Policy settings — you link GPOs to sites, domains, or OUs to apply them. |
| **GPO Link** | Connecting a GPO to an OU, domain, or site — without a link, a GPO does nothing even if settings are configured. |
| **GPO Inheritance** | Settings flow DOWN the OU hierarchy — a GPO at domain level applies to all OUs inside (unless blocked or overridden). |
| **LSDOU precedence** | Order policies are applied: Local to Site to Domain to OU. Lower in hierarchy wins for the same setting. |
| **Enforced GPO** | A GPO marked "Enforced" — its settings CANNOT be overridden by lower-level GPOs. Used for critical security baselines. |
| **Block Inheritance** | An OU setting that blocks parent GPOs from applying — useful for isolating test environments. |
| **Security Filtering** | Restricts a GPO to only specific users/computers within the linked OU — not everyone in the OU gets the policy. |
| **WMI Filter** | An extra condition on a GPO — applies the policy only if the computer matches a WMI query (e.g., only Windows 11 machines). |
| **Default Domain Policy** | Built-in GPO linked to the domain root — by convention, ONLY password and account lockout policies go here. |
| **Fine-Grained Password Policy (PSO)** | Allows different password rules for different user groups — e.g., admins need 16-char passwords, regular users need 10. |
| **Account Lockout Policy** | Locks an account after X failed attempts — threshold, duration, and observation window are the three key settings. |
| **gpupdate /force** | Immediately re-applies all Group Policies on a machine — without it, policies refresh on a ~90-minute background cycle. |
| **RSoP (Resultant Set of Policy)** | Report showing exactly which GPOs apply to a user/computer — `gpresult /h report.html` generates it. |

---

## P5 — AD Trusts and DNS

| Term | One-liner Definition |
|------|----------------------|
| **Trust** | A relationship between two AD domains/forests — allows users from one to access resources in the other. Without a trust, they are completely isolated. |
| **One-way trust** | Domain A trusts Domain B — B's users can access A's resources, but NOT the reverse. |
| **Two-way trust** | Both domains trust each other — users from either can access resources in both. |
| **Transitive trust** | If A trusts B and B trusts C, then A also trusts C — all domains in a forest have automatic transitive trusts. |
| **Forest trust** | A trust between two entire forests — needed to share resources between completely separate AD organizations. |
| **External trust** | A trust between a domain in your forest and a domain in another forest — non-transitive, limited scope. |
| **AD-integrated DNS** | DNS zones stored IN AD (not text files) — automatically replicated between DCs, more secure and resilient. |
| **SRV record** | A DNS record type telling clients WHERE to find a service — AD relies heavily on SRV records so clients can locate Domain Controllers. |
| **Forwarder** | A DNS server configured to send unresolved queries to another DNS server — corporate DNS often forwards to public resolvers (8.8.8.8) for internet names. |

---

## P6 — Device Identity and Management

| Term | One-liner Definition |
|------|----------------------|
| **Domain Join (Classic)** | A Windows PC joined to on-prem AD — gets an AD computer account, Group Policies, authenticates via Kerberos. The traditional enterprise join. |
| **Azure AD Join (Entra Join)** | A Windows device joined ONLY to Entra ID — no on-prem AD required. For cloud-first organizations. Users sign in with Entra ID accounts. |
| **Hybrid Azure AD Join** | A Windows device joined to BOTH on-prem AD AND Entra ID — gets Group Policy from AD AND Conditional Access/Intune from Entra. The migration middle ground. |
| **Azure AD Registered** | A device simply "registered" with Entra ID — typically personal/BYOD devices. Lower trust level than Azure AD Join. |
| **Intune** | Microsoft's cloud MDM/MAM service — enrolls, configures, and manages Windows, iOS, Android, macOS devices from the cloud. |
| **MDM (Mobile Device Management)** | Full device management — can wipe devices, push certificates, enforce encryption. Intune is Microsoft's MDM. |
| **MAM (Mobile Application Management)** | Manages only specific apps on a device — useful for BYOD where you only control corporate apps, not the whole phone. |
| **Device Compliance Policy** | An Intune rule defining what a device must have to be "compliant" — e.g., BitLocker on, OS updated, no jailbreak. Conditional Access checks this. |
| **Co-management** | A Windows device managed by BOTH on-prem SCCM AND Intune simultaneously — a common migration stepping stone. |
| **Windows Autopilot** | Pre-configures new Windows devices in the cloud — IT registers device hardware IDs; when user powers on, it auto-enrolls in Intune. Zero-touch deployment. |
| **Primary Refresh Token (PRT)** | A special token on an Azure AD joined or registered device enabling SSO — used to silently get app tokens without re-prompting the user. |

---

## P7 — PKI and Certificates

| Term | One-liner Definition |
|------|----------------------|
| **PKI (Public Key Infrastructure)** | The system for issuing, managing, and revoking digital certificates — organizations run their own PKI (AD CS) or use public CAs. |
| **Certificate** | A digital document proving an identity — contains a public key, who it was issued to, and is signed by a trusted CA. Used for HTTPS, smart card login, device auth. |
| **CA (Certificate Authority)** | The entity that issues and signs certificates — browsers/systems trust certificates because they trust the CA that signed them. |
| **AD CS (Active Directory Certificate Services)** | Microsoft's on-prem PKI role — lets organizations issue their own certificates for LDAPS, smart cards, device authentication. |
| **Root CA** | The top-level CA whose certificate is explicitly trusted — signs intermediate CA certificates. Usually kept OFFLINE for security. |
| **Intermediate CA** | A CA signed by the root CA — the one that actually issues end-user certificates. If compromised, only the intermediate needs revoking. |
| **Certificate template** | A blueprint in AD CS defining what certificates can be issued — who can request them, what they're for, and how long they're valid. |
| **Self-signed certificate** | Signed by itself, not by a trusted CA — not trusted by default. Use only for testing, NEVER in production. |
| **CRL (Certificate Revocation List)** | A downloadable list of revoked certificates — clients check this to ensure a certificate is still valid. |
| **OCSP** | Online Certificate Status Protocol — real-time alternative to CRL. Client asks "is THIS specific certificate still valid?" and gets a yes/no response. |
| **Smart card login** | Users authenticate using a physical smart card + PIN — the card contains a certificate. Very secure, phishing-resistant. The on-prem equivalent of FIDO2. |
| **Certificate-based authentication (CBA)** | Using a certificate (on smart card, device, or YubiKey) to authenticate to Entra ID — phishing-resistant, natively supported in Entra ID. |
| **TLS/SSL** | The protocol encrypting data in transit — HTTPS is HTTP + TLS. Certificates are what make TLS work (server proves its identity). |

---

## P8 — Security Protocols and Standards

| Term | One-liner Definition |
|------|----------------------|
| **SAML 2.0** | An XML-based SSO standard — the identity provider (Entra ID) sends a signed XML "assertion" to the app proving who the user is. Common for enterprise SaaS. |
| **WS-Federation** | An older Microsoft SSO standard — still used by legacy services and AD FS. Being replaced by OIDC. |
| **JWT (JSON Web Token)** | The token FORMAT used by Entra ID — a Base64-encoded JSON object with header, claims, and a signature. Decode and inspect at `jwt.ms`. |
| **Claims** | The data fields inside a JWT — e.g., `sub` (user ID), `name`, `email`, `roles`, `tid` (tenant ID), `aud` (intended audience). |
| **Audience (aud claim)** | The intended recipient of a token — an app should reject tokens not addressed to it. Prevents token reuse across apps. |
| **Issuer (iss claim)** | Who signed the token — for Entra ID: `https://login.microsoftonline.com/{tenantId}/v2.0`. Apps validate this to ensure the right tenant issued it. |
| **Token signing key** | Entra ID's private key used to sign tokens — apps verify the signature using the matching public key from Entra ID's OIDC config endpoint. |
| **Back channel** | Server-to-server communication not visible in the browser — token exchange happens here (more secure). |
| **Front channel** | Communication through the browser URL — only short-lived authorization codes should pass here, never tokens directly. |
| **Legacy authentication** | Old protocols without MFA support — Basic Auth over SMTP/IMAP/POP3, older Office clients. Must be BLOCKED via CA policies. |
| **Modern authentication** | OAuth 2.0/OIDC-based authentication — supports MFA, Conditional Access, and token-based sessions. All modern Office apps use this. |
| **NTLMv1 vs NTLMv2** | NTLMv1 is broken — always disable it. NTLMv2 is the minimum acceptable but still weaker than Kerberos. |

---

## P9 — Microsoft Graph

| Term | One-liner Definition |
|------|----------------------|
| **Microsoft Graph** | The single REST API for all Microsoft 365 and Azure data — users, groups, calendar, mail, Teams, Intune, SharePoint. Endpoint: `https://graph.microsoft.com`. |
| **Graph Explorer** | Interactive web tool at `developer.microsoft.com/graph/graph-explorer` — make Graph API calls to test queries and learn the API without writing code. |
| **Microsoft Graph PowerShell** | PowerShell module wrapping the Graph API — current replacement for old AzureAD and MSOnline modules. `Install-Module Microsoft.Graph`. |
| **Graph Permissions** | Scopes controlling what Graph API operations are allowed — e.g., `User.Read`, `User.ReadWrite.All`, `Group.Read.All`. Assigned as delegated or application permissions. |
| **`$filter`** | OData query parameter to filter Graph results — e.g., `GET /users?$filter=department eq 'Sales'` returns only Sales department users. |
| **`$select`** | OData parameter to choose which properties are returned — reduces response size. e.g., `GET /users?$select=displayName,mail`. |
| **Delta query** | Gets only CHANGES since your last query — instead of fetching all users every time, you get only new/modified/deleted objects. Critical for efficient provisioning. |

---

## P10 — Azure AD Domain Services

| Term | One-liner Definition |
|------|----------------------|
| **Azure AD DS** | Microsoft's MANAGED Active Directory in Azure — gives you a cloud DC WITHOUT managing servers. Provides LDAP, Kerberos, NTLM, Group Policy, and domain join as a PaaS service. |
| **Managed domain** | The AD domain Azure AD DS creates — you can't log in to the DCs directly or extend the schema, but you can join VMs and create OUs under a reserved parent. |
| **Sync from Entra ID** | Azure AD DS syncs users and groups FROM Entra ID (one-way only) — on-prem users flow through Entra Connect to Entra ID to Azure AD DS. |
| **Why use Azure AD DS?** | Legacy apps on Azure VMs that REQUIRE LDAP, Kerberos, or domain join — when you don't want to manage your own AD DCs on IaaS VMs. |
| **Azure AD DS vs Entra ID** | Entra ID = modern cloud identity (OAuth/OIDC). Azure AD DS = classic AD (Kerberos/NTLM/LDAP). Different purposes — use Azure AD DS to lift legacy apps. |
| **Azure AD DS vs self-managed AD** | Azure AD DS = Microsoft manages DCs (patching, HA, backups). Self-managed = you manage everything on VMs. Azure AD DS is simpler but less customizable. |

---

## P11 — Zero Trust and Security Concepts

| Term | One-liner Definition |
|------|----------------------|
| **Zero Trust** | "Never trust, always verify" — every access request is fully authenticated and authorized regardless of where it comes from (inside or outside the network). |
| **Zero Trust pillars** | Identities, Devices, Applications, Data, Infrastructure, Networks — all six must be secured. SC-300 focuses primarily on the Identities pillar. |
| **Assume breach** | Design your system AS IF attackers are already inside — minimize blast radius, segment access, monitor everything. |
| **Verify explicitly** | Always authenticate using ALL available signals: identity, location, device health, workload, data classification. |
| **Least privilege access** | Limit access to only what is needed, use JIT and JEA — PIM implements this in Entra ID. |
| **Lateral movement** | When an attacker moves from one compromised account/machine to others — Zero Trust and network segmentation limit this. |
| **Credential stuffing** | Attack using stolen username/password combos from one breach against other sites — targets password re-users. |
| **Password spray** | Attack trying ONE common password against MANY accounts — avoids triggering per-account lockout policies. |
| **Phishing** | Tricks users into entering credentials on a fake login page — MFA reduces impact; FIDO2/passkeys fully prevent it. |
| **MFA fatigue attack** | Spam a user with MFA push requests hoping they accidentally approve one — number matching in Authenticator prevents this. |
| **Token theft** | Attacker steals a valid access/refresh token and uses it without credentials — token protection (binding tokens to devices) prevents this. |
| **Privileged Access Workstation (PAW)** | A dedicated, hardened computer ONLY for admin tasks — no email, no web browsing. Reduces attack surface for privileged accounts. |
| **Tiered administration model** | Tier 0 = AD/DCs, Tier 1 = servers, Tier 2 = workstations — admins should only use accounts matching the tier of the resource they manage. |
| **JIT (Just-In-Time) access** | Admin access granted only when needed and expires automatically — PIM implements JIT for Entra ID and Azure roles. |
| **JEA (Just-Enough-Access)** | Access scoped to only the specific tasks needed — custom roles and Administrative Units implement JEA in Entra ID. |
| **Secure Score** | Microsoft's score (0-100%) measuring how well your tenant follows identity security best practices — each recommendation has a score value. |

---

## P12 — Networking Concepts Relevant to Identity

| Term | One-liner Definition |
|------|----------------------|
| **Proxy server** | An intermediary routing network traffic — Entra Connect, PTA agents, and App Proxy connectors must be configured to work through corporate proxies. |
| **Outbound-only connectivity** | Entra Connect, PTA Agent, and App Proxy Connector all make OUTBOUND connections to Azure — no inbound firewall rules needed on your network. |
| **Port 443** | HTTPS — almost all Entra ID and Microsoft 365 communication uses this outbound. Must be allowed in firewalls for hybrid identity to work. |
| **Port 389 / 636** | LDAP (389) and LDAPS (636) — Entra Connect uses these to communicate with on-premises AD. Port 636 (encrypted) preferred. |
| **Port 88** | Kerberos — used for authentication in AD. Must be open between DCs and clients. |
| **CA and Named Location** | Conditional Access uses the user's public IP to determine location — VPN changes this IP, which affects which CA policies apply. |
| **App Proxy networking** | Users hit Microsoft's cloud, which routes through the on-prem App Proxy connector — no VPN or inbound firewall rules required from the user's device. |

---

## P13 — PowerShell for Identity Admins

| Term | One-liner Definition |
|------|----------------------|
| **Microsoft Graph PowerShell SDK** | The current recommended module for managing Entra ID — replaces old AzureAD and MSOnline modules. `Install-Module Microsoft.Graph`. |
| **AzureAD module** | Old PowerShell module for Azure AD — still works but deprecated. Commands: `Get-AzureAD*`, `Set-AzureAD*`, `New-AzureAD*`. |
| **MSOnline module** | Even older PowerShell module (v1) — being retired. Commands start with `Get-Mso*`. |
| **Connect-MgGraph** | Graph PowerShell auth command — `Connect-MgGraph -Scopes "User.Read.All"`. Specify what permissions your session needs. |
| **Get-MgUser** | List/get Entra ID users — `Get-MgUser -All` returns all users; `Get-MgUser -UserId "alice@company.com"` gets one specific user. |
| **New-MgUser** | Creates a new user via Graph PowerShell — takes `DisplayName`, `MailNickname`, `UserPrincipalName`, `PasswordProfile` as parameters. |
| **Update-MgUser** | Updates a user's properties — `Update-MgUser -UserId $id -Department "Engineering"`. |
| **Get-MgGroup** | Lists groups in Entra ID — can filter by `DisplayName` or `GroupTypes`. |
| **Import-CSV + loop** | PowerShell pattern for bulk user management — read a CSV of users and create/update them in a loop. Essential real-world skill. |
| **Get-MgAuditLogSignIn** | Retrieves Entra ID sign-in logs via PowerShell — useful for investigating specific user sign-in history from the command line. |

---

# Extended Comparison Tables

---

## sAMAccountName vs UPN vs Email Address

| | sAMAccountName | UPN | Email (mail attribute) |
|---|---|---|---|
| **Format** | `alice` (short, no @) | `alice@company.com` | `alice.smith@company.com` |
| **Used for** | Legacy Windows/AD login | Modern cloud login | Email delivery |
| **Same as UPN?** | Often NO | The primary Entra ID login | May differ from UPN |
| **In Entra ID** | Mapped from on-prem synced accounts | The Entra ID login identifier | A separate profile attribute |

---

## AD DS vs Azure AD DS vs Entra ID

| | AD DS (on-prem) | Azure AD DS | Entra ID |
|---|---|---|---|
| **Location** | On-premises Windows Server | Azure PaaS (managed) | Microsoft cloud |
| **Auth protocols** | Kerberos, NTLM, LDAP | Kerberos, NTLM, LDAP | OAuth 2.0, OIDC, SAML |
| **Who manages DCs** | You (patch, backup, HA) | Microsoft | N/A (no DCs) |
| **Group Policy** | Full GPO support | Limited GPO support | No GPO (use Intune/CA) |
| **Schema extension** | Yes | No | No |
| **Use case** | Traditional on-prem enterprise | Legacy apps on Azure VMs | Modern cloud identity |

---

## Domain Join vs Azure AD Join vs Hybrid Join

| | Domain Join | Azure AD Join | Hybrid Join |
|---|---|---|---|
| **Joined to** | On-prem AD only | Entra ID only | Both on-prem AD + Entra ID |
| **Auth** | Kerberos to on-prem DC | Primary Refresh Token (PRT) | Both |
| **Group Policy** | Yes | No (use Intune) | Yes (from AD) + Intune |
| **Best for** | Pure on-prem orgs | Cloud-first orgs | Orgs migrating to cloud |
| **CA support** | Via hybrid join CA condition | Native | Native |

---

## GPO vs Intune Config Profile vs Conditional Access

| | Group Policy (GPO) | Intune Config Profile | Conditional Access |
|---|---|---|---|
| **Controls** | Device OS settings | Device OS settings | Access to apps and data |
| **Requires** | On-prem AD DC | Intune enrollment | Entra ID P1+ |
| **Applied to** | Domain-joined PCs only | Enrolled devices (any OS) | Any sign-in attempt |
| **Scope** | OU in AD | Device/User groups in Intune | Users/Apps in Entra ID |
| **Cloud-managed?** | No | Yes | Yes |
---

# 📦 Microsoft 365 E5 License — What It Can Do and Cannot Do

> **SC-300 Core Context:** Microsoft 365 E5 is Microsoft's top-tier enterprise bundle. In identity terms, **Microsoft 365 E3 includes Entra ID P1**, while **Microsoft 365 E5 includes Entra ID P2** plus the entire **Microsoft Defender** and **Microsoft Purview** security and compliance suites.

---

## E5 Licensing Hierarchy at a Glance

```
  ┌────────────────────────────────────────────────────────────────────────┐
  │ Microsoft 365 E5 (The Full Security & Identity Suite)                 │
  │  ├── Microsoft Entra ID P2 (Risk policies, PIM, Access Reviews)        │
  │  ├── Microsoft Defender for Identity (On-prem AD attack detection)     │
  │  ├── Microsoft Defender for Cloud Apps (CASB & Session CA policies)    │
  │  ├── Microsoft Defender for Endpoint P2 (Enterprise EDR)              │
  │  ├── Microsoft Defender for Office 365 P2 (Safe Links, Anti-phishing)  │
  │  ├── Microsoft Purview Information Protection (Full DLP, Labels)       │
  │  └── Microsoft Purview Insider Risk Management & Customer Lockbox      │
  └────────────────────────────────────────────────────────────────────────┘
                              ▲
                              │ includes everything in E3 +
  ┌────────────────────────────────────────────────────────────────────────┐
  │ Microsoft 365 E3                                                       │
  │  ├── Microsoft Entra ID P1 (Conditional Access, Dynamic Groups, SSPR)   │
  │  ├── Microsoft Intune Plan 1 (MDM & MAM)                              │
  │  └── Microsoft 365 Apps (Word, Excel, Exchange, SharePoint, Teams)     │
  └────────────────────────────────────────────────────────────────────────┘
                              ▲
                              │ includes everything in Free +
  ┌────────────────────────────────────────────────────────────────────────┐
  │ Microsoft Entra ID Free (Included with any Azure / M365 subscription)  │
  │  └── Basic users, groups, SSO (unlimited apps), Security Defaults      │
  └────────────────────────────────────────────────────────────────────────┘
```

---

## Feature Comparison: Free vs E3 (P1) vs E5 (P2) vs Governance Add-on

| Feature / Capability | Free | M365 E3 (P1) | M365 E5 (P2) | Entra ID Governance Add-on |
|---|:---:|:---:|:---:|:---:|
| **User & Group Management (cloud-only)** | ✅ | ✅ | ✅ | ✅ |
| **SSO to Cloud Apps** | ✅ (Unlimited) | ✅ | ✅ | ✅ |
| **Security Defaults (MFA for all or none)** | ✅ | ✅ | ✅ | ✅ |
| **Conditional Access Policies (CA)** | ❌ | ✅ | ✅ | ✅ |
| **Dynamic User & Device Groups** | ❌ | ✅ | ✅ | ✅ |
| **Hybrid Password Hash Sync (PHS) / PTA** | ✅ | ✅ | ✅ | ✅ |
| **Password Writeback to On-Prem AD (SSPR)** | ❌ | ✅ | ✅ | ✅ |
| **Application Proxy (Publish on-prem web apps)** | ❌ | ✅ | ✅ | ✅ |
| **Custom Security Attributes** | ❌ | ✅ | ✅ | ✅ |
| **Administrative Units (AUs)** | ❌ | ✅ | ✅ | ✅ |
| **Risk-Based Conditional Access (Sign-in Risk)** | ❌ | ❌ | ✅ | ✅ |
| **Risk-Based Password Reset (User Risk)** | ❌ | ❌ | ✅ | ✅ |
| **Identity Protection (Leaked credentials, anonymous IP)** | ❌ | ❌ | ✅ | ✅ |
| **Privileged Identity Management (PIM for Roles)** | ❌ | ❌ | ✅ | ✅ |
| **PIM for Groups & Azure Resources** | ❌ | ❌ | ✅ | ✅ |
| **Access Reviews (Group & App membership)** | ❌ | ❌ | ✅ | ✅ |
| **Entitlement Management (Access Packages)** | ❌ | ❌ | ✅ | ✅ |
| **Lifecycle Workflows (Standard built-in JML)** | ❌ | ❌ | ✅ | ✅ |
| **Lifecycle Workflows (Custom task extensions & Logic Apps)**| ❌ | ❌ | ❌ | ✅ |
| **Separation of Duties (SoD) Access Reviews** | ❌ | ❌ | ❌ | ✅ |
| **Machine Identity / Workload Identity Governance** | ❌ | ❌ | ❌ | ✅ |
| **Defender for Identity (On-prem AD DC sensor)** | ❌ | ❌ | ✅ | ✅ |
| **Defender for Cloud Apps (CASB & CA App Control)** | ❌ | ❌ | ✅ | ✅ |
| **Customer Lockbox (Approve MS engineer data access)** | ❌ | ❌ | ✅ | ✅ |
| **Insider Risk Management (Purview)** | ❌ | ❌ | ✅ | ✅ |

---

## What Microsoft 365 E5 CAN DO

| Capability Area | What E5 Allows You To Do | Exam & Real-World Context |
|---|---|---|
| **Identity Protection** | Detect real-time sign-in risk (e.g., anonymous IP, atypical travel) and user risk (e.g., leaked credentials on dark web). Automatically force password reset via SSPR when user risk is High. | Core SC-300 topic. P1 only allows static CA conditions (location, device); E5/P2 allows **dynamic risk-based** CA conditions. |
| **Privileged Identity Management (PIM)** | Eliminate permanent admin assignments. Admins must activate role on-demand (Just-In-Time), specify a reason, satisfy MFA, and await approval. Automatically revoke after *N* hours. | Core SC-300 topic. Covers Entra directory roles, Azure subscription RBAC roles, and PIM for Groups. |
| **Access Reviews** | Automatically schedule recurring reviews (e.g., quarterly) where managers or resource owners confirm if employees/guests still need access. Auto-remove access if reviewer fails to respond. | Critical for compliance (ISO 27001, SOC 2). Stale guest accounts can be auto-disabled or removed. |
| **Entitlement Management** | Bundle groups, apps, and SharePoint sites into a single **Access Package**. Allow internal users or external partners to request access via a self-service portal (`myaccess.microsoft.com`) with multi-stage approval. | Reduces IT ticket fatigue; sets automatic expiration dates for vendor and contractor access. |
| **Lifecycle Workflows (Built-in)** | Automate Joiner, Mover, Leaver (JML) processes using predefined templates (e.g., send welcome email 7 days before start, generate TAP, disable user on last day). | Streamlines HR-driven provisioning from Workday/SuccessFactors. |
| **Defender for Identity (MDI)** | Install lightweight sensors on on-prem Active Directory Domain Controllers to monitor Kerberos/NTLM traffic and detect attacks like Pass-the-Hash, DCSync, and Golden Ticket. | Bridges hybrid gap: brings cloud machine learning to on-prem domain controller security. |
| **Defender for Cloud Apps (MDCA)** | Real-time session monitoring and reverse proxy control via Conditional Access App Control. Block file downloads or block copy/paste on unmanaged/personal devices in real time. | Solves the BYOD dilemma without requiring full device MDM enrollment. |
| **Defender for Office 365 P2** | Safe Links (time-of-click URL scanning), Safe Attachments, automated attack investigation/remediation (AIR), and **Attack Simulation Training** (phishing tests). | SC-300 requires understanding phishing simulation and credential harvest training. |
| **Purview Customer Lockbox** | Explicitly approve or reject Microsoft support engineers accessing your tenant data during support tickets. Access is time-bound and logged. | High-security government and financial compliance requirement. |
| **Insider Risk Management** | Correlate user activity (e.g., an employee who submitted resignation downloading sensitive confidential files or emailing them to personal webmail) with DLP alerts. | Advanced Purview feature included in M365 E5 (not in E3). |

---

## What Microsoft 365 E5 CANNOT DO (Hard Limits & Gotchas)

> [!WARNING]
> E5 is comprehensive, but it is **not magic**. In the SC-300 exam and production architectures, Microsoft frequently tests boundaries where E5 **cannot** solve the problem alone.

| What E5 CANNOT Do | Why / What is Actually Required | Exam Trap / Clarification |
|---|---|---|
| **CANNOT replace on-premises Active Directory (AD DS)** | E5 is cloud-based. It does not provide Kerberos, NTLM, or LDAP services to on-prem servers and legacy apps. | You still need on-prem Windows Server DCs + **Microsoft Entra Connect** for hybrid sync. |
| **CANNOT replace Azure Cloud infrastructure subscriptions** | E5 is a per-user SaaS license. It does **not** pay for Azure VMs, Virtual Networks, Azure SQL, Key Vault, or Storage Accounts. | Azure resources require an **Azure Subscription** billed on consumption (pay-as-you-go / EA / CSP). |
| **CANNOT include unlimited Microsoft Sentinel (SIEM) ingestion** | Microsoft Sentinel is a consumption-based Azure service billed per GB of data ingested per day. | While E5 data connectors (Entra logs, Defender alerts) have free ingestion tiers, third-party logs (firewalls, AWS, syslog) incur Azure consumption charges. |
| **CANNOT license Consumer / B2C identities (External ID for Customers)** | E5 covers enterprise workforce users and B2B guests. It does **not** cover customer-facing consumer apps. | Entra External ID for Customers / Azure AD B2C uses separate billing based on **Monthly Active Users (MAU)** (first 50,000 MAU free, then tiered pricing). |
| **CANNOT provide Azure Active Directory Domain Services (Azure AD DS)** | Azure AD DS provides managed Kerberos/LDAP/domain join in Azure cloud, but it is a separate **hourly Azure PaaS service**. | E5 does NOT include Azure AD DS. Azure AD DS is charged to an Azure subscription. |
| **CANNOT provide PIM / JIT elevation for Classic on-prem AD Domain Admins** | Entra ID PIM manages cloud directory roles and Azure RBAC resources. It does **not** natively hook into on-prem AD to grant time-bound Domain Admin membership. | Requires on-prem Privileged Access Management (PAM), Microsoft Identity Manager (MIM), or third-party PAM solutions (CyberArk, BeyondTrust). |
| **CANNOT retain audit & sign-in logs forever out of the box** | Entra ID P2 included in E5 stores audit and sign-in logs for only **30 days** maximum. | To keep logs for 90 days, 1 year, or 7 years for compliance, you **must configure Diagnostic Settings** to stream logs to **Azure Log Analytics Workspace**, an Azure Storage Account, or Event Hub. |
| **CANNOT bypass RBAC or grant automatic admin rights** | Having an E5 license assigned to your user account does **not** make you an administrator. | Administrative privileges require explicit directory role assignment (e.g., Security Admin, User Admin) or PIM eligibility. |
| **CANNOT include advanced Entra ID Governance features** | E5 includes baseline Governance (Access Reviews, baseline Lifecycle Workflows). It does **not** include custom task extensions (Logic Apps), cross-tenant sync governance, or Machine Identity governance. | Requires the standalone **Microsoft Entra ID Governance Add-on** license. |
| **CANNOT manage full OS or wipe personal data on unenrolled BYOD** | Intune (included in E5) can wipe corporate data from corporate apps via MAM (Mobile Application Management), but cannot manage OS patches or wipe personal photos/data on un-enrolled personal phones. | Full device management requires complete **MDM Device Enrollment**. |

---

## SC-300 Exam Decision Matrix: E3 (P1) vs E5 (P2)

Use this table to immediately identify the required license from exam scenario keywords:

| If the scenario asks for... | Minimum License Needed | Reason |
|---|:---:|---|
| **"Block access from legacy authentication protocols"** | **E3 / Entra ID P1** | Requires Conditional Access (P1 feature). |
| **"Require MFA for users outside the corporate network"** | **E3 / Entra ID P1** | Named locations + Conditional Access (P1 feature). |
| **"Automatically populate group based on user department"** | **E3 / Entra ID P1** | Dynamic User Groups require P1 for each member. |
| **"Publish on-prem intranet web app without VPN"** | **E3 / Entra ID P1** | Microsoft Entra Application Proxy requires P1. |
| **"Write back password changes made in cloud to on-prem AD"** | **E3 / Entra ID P1** | SSPR with Password Writeback requires P1. |
| **"Require password change when credentials are leaked on dark web"** | **E5 / Entra ID P2** | User Risk detection is exclusive to Identity Protection (P2). |
| **"Require MFA when sign-in is from an unfamiliar or anonymous IP"** | **E5 / Entra ID P2** | Sign-in Risk policy is exclusive to Identity Protection (P2). |
| **"Ensure administrators do NOT hold permanent standing privileges"** | **E5 / Entra ID P2** | Just-In-Time role elevation requires PIM (P2). |
| **"Require approval before an admin can activate an Azure subscription role"** | **E5 / Entra ID P2** | PIM for Azure Resources requires P2. |
| **"Periodically verify that external contractors still require group access"** | **E5 / Entra ID P2** | Access Reviews require P2. |
| **"Allow partner organizations to request access via a self-service portal"** | **E5 / Entra ID P2** | Entitlement Management & Access Packages require P2. |
| **"Simulate phishing attacks to train users on identity security"** | **M365 E5** | Attack Simulation Training requires Defender for Office 365 P2. |

---

# 🛡️ Entra ID Important Roles — What Each CAN & CANNOT Do

> **SC-300 Core Principle:** Always adhere to the **Principle of Least Privilege (PoLP)**. If a role can achieve a task with fewer permissions, assigning a higher role (especially Global Administrator) is an **incorrect exam answer**.

---

## Entra ID Directory Roles vs Azure RBAC Roles

| Dimension | Entra ID Directory Roles | Azure RBAC Roles |
|---|---|---|
| **What they manage** | **Identity plane:** Users, groups, apps, domains, licenses, directory security. | **Resource plane:** VMs, VNets, Storage Accounts, Key Vaults, SQL databases. |
| **Examples** | Global Admin, User Admin, Security Admin, CA Admin. | Owner, Contributor, Reader, User Access Administrator. |
| **Scope hierarchy** | Tenant-wide (or scoped via Administrative Units). | Management Group → Subscription → Resource Group → Resource. |
| **Storage** | Stored inside Microsoft Entra ID directory database. | Stored inside Azure Resource Manager (ARM). |
| **Default cross-access** | A Global Admin **cannot** see or manage Azure VMs by default! | An Azure Subscription Owner **cannot** reset Entra ID user passwords! |
| **Elevation Bridge** | Global Admin can toggle **"Access management for Azure resources"** in Entra portal to grant themselves `User Access Administrator` at the root (`/`) management group. | Subscription Owner cannot elevate into Entra ID. |

---

## Important Entra ID Roles: Full "Can Do / Cannot Do" Reference

### 1. Super-Privileged & Global Governance Roles

| Role | One-liner Definition | What It CAN Do | What It CANNOT Do | SC-300 Least Privilege Rule |
|---|---|---|---|---|
| **Global Administrator** | The supreme administrative role; has full control over all directory features and services. | • Full read/write access to every administrative setting in Entra ID and M365 services.<br>• Reset passwords of ANY user, including all other Global Admins.<br>• Elevate access to manage all Azure subscriptions and management groups via root (`/`).<br>• Assign any role to any user. | • Cannot delete their own account if they are the last Global Admin in tenant.<br>• Cannot bypass Conditional Access unless explicitly excluded in policy.<br>• Does not have access to Azure resource data (VM files, database tables) unless access is elevated or granted via Azure RBAC. | Limit to **2 to 4 accounts maximum**. Must require PIM activation, break-glass exclusion, and FIDO2/phishing-resistant MFA. |
| **Privileged Role Administrator** | The role that controls all other roles and PIM assignments. | • Manage, activate, and assign all Entra ID directory roles and Azure RBAC roles.<br>• Configure PIM policies (activation duration, approval requirements, MFA requirement).<br>• Create and manage custom directory roles.<br>• Manage role-assignable groups. | • Cannot manage user attributes (e.g., change department, phone number) unless granted User Admin.<br>• Cannot manage non-role security policies (e.g. Defender, DLP) directly. | The **only role** (besides Global Admin) that can configure PIM settings and assign directory roles to users. |
| **Global Reader** | Complete read-only view across the entire Microsoft cloud environment. | • Read all settings, users, groups, apps, domains, logs, and licenses in Entra ID.<br>• Read all settings in M365 admin centers (Exchange, SharePoint, Teams, Defender, Purview). | • **Cannot make ANY modifications or changes**.<br>• Cannot reset any passwords or revoke sign-in sessions.<br>• Cannot approve PIM requests. | Ideal for auditors, SOC Tier 1 triage, planning assessments, and read-only monitoring tools. |

---

### 2. User, Group & Identity Lifecycle Roles

| Role | One-liner Definition | What It CAN Do | What It CANNOT Do | SC-300 Least Privilege Rule |
|---|---|---|---|---|
| **User Administrator** | Manages standard users, groups, and basic account lifecycles. | • Create, edit, and delete users and standard security/M365 groups.<br>• Manage user profile properties (department, job title, manager).<br>• Reset passwords for non-administrators and low-privilege roles (e.g., Helpdesk Admin, Guest Inviter).<br>• Manage Administrative Units (AUs). | • **Cannot reset passwords of Global Admins, Privileged Role Admins, Security Admins, or Billing Admins**.<br>• Cannot delete Global Admin accounts.<br>• Cannot manage role-assignable groups.<br>• Cannot configure Conditional Access or PIM. | Assign when someone needs to manage employee accounts and standard groups without security policy control. |
| **Helpdesk Administrator** *(Password Administrator)* | First-tier support role focused strictly on unlocking and resetting non-privileged users. | • Reset passwords for **non-administrators only**.<br>• Revoke user sign-in sessions (force re-authentication).<br>• View basic user profiles to verify identity. | • **Cannot reset passwords for ANY admin** (not even User Admin).<br>• Cannot create or delete user accounts.<br>• Cannot modify group memberships or licenses.<br>• Cannot view audit/sign-in logs. | Assign to Helpdesk / Service Desk Tier 1 staff who only answer calls to reset user passwords. |
| **Authentication Administrator** | Manages MFA methods and credentials for non-privileged users. | • View, register, and reset authentication methods (FIDO2, Microsoft Authenticator, phone numbers, Temporary Access Passes [TAP]) for non-admin users.<br>• Reset passwords for non-admin users.<br>• Require users to re-register for MFA. | • **Cannot view or reset authentication methods for ANY administrative role**.<br>• Cannot modify directory settings, create users, or manage groups. | Assign to support staff responsible for troubleshooting MFA lockouts and issuing TAPs for standard employees. |
| **Privileged Authentication Administrator** | Manages authentication methods and passwords for EVERYONE, including Global Admins. | • View, reset, and re-register MFA methods, credentials, and TAPs for **ALL users and all administrators** (including Global Admins).<br>• Force password resets for any admin.<br>• Revoke sessions for any user or admin. | • Cannot assign directory roles to users (needs Privileged Role Admin).<br>• Cannot modify Conditional Access policies or create users.<br>• Cannot modify tenant domain settings. | High-risk role. Use when senior IT must recover an administrator who lost their MFA device or hardware security key. |
| **Groups Administrator** | Dedicated manager for security groups and Microsoft 365 groups. | • Create, edit, and delete standard security groups and M365 groups.<br>• Manage group ownership, membership, and expiration policies.<br>• Configure dynamic group membership rules. | • **Cannot manage role-assignable groups** (groups that have Entra roles assigned to them).<br>• Cannot create, delete, or reset individual user accounts.<br>• Cannot manage directory security settings. | Assign to team leads or collaboration admins who organize group structures without needing user creation rights. |
| **Guest Inviter** | Grants permission to invite external B2B guests. | • Send B2B collaboration invitations to external users when tenant settings restrict standard users from inviting guests. | • Cannot create regular internal cloud users.<br>• Cannot reset passwords or manage group memberships.<br>• Cannot assign roles or licenses. | Assign when external collaboration is restricted to specific trusted project managers or HR personnel. |

---

### 3. Security, Access Control & Monitoring Roles

| Role | One-liner Definition | What It CAN Do | What It CANNOT Do | SC-300 Least Privilege Rule |
|---|---|---|---|---|
| **Security Administrator** | Full manager for all security configurations across Entra ID and Defender. | • Create, edit, and manage Conditional Access policies.<br>• Manage Identity Protection (configure user & sign-in risk policies).<br>• Manage Microsoft Defender suite (alerts, policies, incident response).<br>• View security reports, risky users, and Secure Score. | • **Cannot reset passwords of users directly** (unless paired with User Admin / Auth Admin).<br>• Cannot assign directory roles to users (needs Privileged Role Admin).<br>• Cannot manage M365 mailboxes or SharePoint content. | Assign to the lead Security Engineer / CISO team managing security posture without user provisioning duties. |
| **Security Operator** | Daily security triage and incident response role. | • View, investigate, and dismiss alerts in Microsoft Defender and Identity Protection.<br>• Confirm users as compromised or dismiss user risk.<br>• View sign-in logs and audit logs. | • **Cannot create or modify Conditional Access policies**.<br>• Cannot change security configurations or policy thresholds.<br>• Cannot reset passwords or manage user objects. | Assign to Tier 2 SOC analysts who investigate and triage alerts without changing tenant-wide policies. |
| **Security Reader** | Read-only auditor for security posture. | • Read all security configurations, Identity Protection reports, risky user lists, Defender dashboards, and Secure Score. | • **Cannot modify any security policy**.<br>• Cannot dismiss alerts or confirm user compromise.<br>• Cannot reset credentials or change user settings. | Assign to external compliance auditors or junior security analysts. |
| **Conditional Access Administrator** | Dedicated policy author for zero-trust Conditional Access. | • Create, edit, toggle (On/Off/Report-only), and delete Conditional Access policies.<br>• Manage Named Locations (trusted IPs, countries).<br>• Manage Custom Controls and Terms of Use (ToU). | • **Cannot manage user or group accounts**.<br>• Cannot manage Identity Protection risk detections directly.<br>• Cannot manage Intune device compliance policies.<br>• Cannot assign directory roles. | Assign to identity engineers tasked strictly with building and maintaining zero-trust access policies. |
| **Attack Simulation Administrator** | Specialized role for running simulated phishing tests. | • Create, launch, schedule, and review phishing simulation campaigns.<br>• Assign remediation training to users who fail simulations. | • Cannot modify security policies, spam filters, or email routing.<br>• Cannot view user emails or reset passwords. | Assign to security awareness trainers. |

---

### 4. Application & API Integration Roles

| Role | One-liner Definition | What It CAN Do | What It CANNOT Do | SC-300 Least Privilege Rule |
|---|---|---|---|---|
| **Application Administrator** | Complete manager for all applications (App Registrations + Enterprise Apps). | • Create, configure, update, and delete all App Registrations and Enterprise Applications.<br>• Manage SAML SSO configurations, reply URLs, certificates, and secrets.<br>• Manage **Application Proxy** connectors and published on-prem apps.<br>• Grant tenant-wide admin consent for delegated permissions (except high-privilege scopes). | • **Cannot grant admin consent to high-privilege application permissions** (e.g., `Directory.ReadWrite.All`, `RoleManagement.ReadWrite.Directory` require Global Admin).<br>• Cannot manage directory users, groups, or security policies. | Assign to identity/app integration leads managing SaaS SSO, SAML integrations, and on-prem App Proxy. |
| **Cloud Application Administrator** | Application manager *excluding* on-premises Application Proxy infrastructure. | • Create and manage App Registrations and Enterprise Apps (SSO, credentials, consent).<br>• Same permissions as Application Admin **EXCEPT** App Proxy. | • **Cannot manage on-premises Application Proxy connectors or connector groups**.<br>• Cannot grant high-privilege app-only Graph permissions. | Assign to app administrators in organizations that do not use on-premises App Proxy or want to restrict connector access. |
| **Application Developer** | Grants rights to register custom apps when standard user registration is blocked. | • Create App Registrations in the tenant even when the setting *"Users can register applications"* is set to **No**. | • Cannot manage Enterprise Applications owned by others.<br>• Cannot grant admin consent on behalf of the tenant.<br>• Cannot configure Application Proxy or edit other developers' apps. | Assign to software developers who need to register and test custom APIs/apps without administrative app rights. |

---

### 5. Hybrid, Infrastructure & Governance Roles

| Role | One-liner Definition | What It CAN Do | What It CANNOT Do | SC-300 Least Privilege Rule |
|---|---|---|---|---|
| **Hybrid Identity Administrator** | Dedicated manager for hybrid directory synchronization tools. | • Configure and manage **Microsoft Entra Connect** and **Entra Cloud Sync**.<br>• Monitor Entra Connect Health and synchronization status.<br>• Configure Seamless SSO, Pass-through Authentication (PTA), and Password Hash Sync (PHS). | • Cannot manage cloud-only Conditional Access policies.<br>• Cannot reset passwords for cloud-only users or cloud administrators.<br>• Cannot assign directory roles. | Assign to hybrid infrastructure engineers responsible for keeping on-prem AD and Entra ID in sync. |
| **Domain Name Administrator** | Manages custom domain names associated with the tenant. | • Add, verify (via DNS TXT/MX records), configure, and remove custom domain names (e.g. `contoso.com`).<br>• Configure domain federation (AD FS / Ping / Okta). | • **Cannot delete the primary `onmicrosoft.com` default domain**.<br>• Cannot create users, assign licenses, or modify security policies. | Assign to DNS / Infrastructure engineers when onboarding or migrating corporate domains. |
| **Intune Administrator** | Full manager for device management and mobile apps. | • Enroll, manage, wipe, and retire devices (Windows, iOS, Android, macOS).<br>• Configure device compliance policies and device configuration profiles.<br>• Deploy and manage corporate applications via Intune. | • Cannot create or edit Entra ID Conditional Access policies directly (requires CA Admin).<br>• Cannot reset passwords of Entra ID administrators.<br>• Cannot assign Entra ID directory roles. | Assign to endpoint management / MDM engineers. |
| **Identity Governance Administrator** | Full manager for identity governance lifecycles and entitlements. | • Configure **Entitlement Management** (catalogs, access packages, connected organizations).<br>• Create and manage **Access Reviews** across groups, apps, and roles.<br>• Configure **Lifecycle Workflows** (JML automation). | • Cannot assign directory roles outside of governed PIM workflows.<br>• Cannot manage core Conditional Access policies or network locations directly. | Assign to identity governance leads and compliance officers managing joiner/mover/leaver processes. |
| **Reports Reader** | Read-only viewer for audit, sign-in, and usage telemetry. | • View sign-in logs, audit logs, provisioning logs, and M365 usage reports. | • Cannot change any configuration, user, or policy.<br>• Cannot export diagnostic settings to Azure resources. | Assign to auditors, compliance officers, and reporting analysts. |

---

### 6. Workload & Business Roles

| Role | One-liner Definition | What It CAN Do | What It CANNOT Do | SC-300 Least Privilege Rule |
|---|---|---|---|---|
| **Exchange Administrator** | Full manager for Exchange Online and email infrastructure. | • Manage mailboxes, shared mailboxes, distribution lists, mail flow (transport rules), anti-spam policies, and quarantine. | • Cannot manage Entra ID Conditional Access, user identity creation, or reset passwords of Entra ID administrators. | Assign to messaging / email engineers. |
| **SharePoint Administrator** | Full manager for SharePoint Online and OneDrive for Business. | • Manage site collections, storage quotas, external sharing settings, and OneDrive tenant configurations. | • Cannot manage Entra ID directory settings or user credentials. | Assign to collaboration / intranet administrators. |
| **Teams Administrator** | Full manager for Microsoft Teams workload. | • Manage Teams settings, policies (calling, messaging, meetings), call queues, phone numbers, and Teams apps. | • Cannot manage underlying Entra ID identity or Conditional Access policies. | Assign to unified communications / Teams engineers. |
| **Billing Administrator** | Financial and procurement manager for Microsoft subscriptions. | • Purchase licenses, manage M365/Azure subscriptions, update credit card / billing info, open billing support tickets. | • **Cannot assign licenses to individual users** (needs License Admin).<br>• Cannot view security logs or modify user accounts. | Assign to procurement and accounting personnel. |
| **License Administrator** | Allocates and reassigns purchased licenses to users. | • Assign, reassign, and remove licenses from individual users and groups (group-based licensing).<br>• Configure license service plans (e.g. enable/disable Yammer on an E3 license). | • **Cannot purchase new licenses** (needs Billing Admin).<br>• Cannot create or delete user accounts.<br>• Cannot modify security policies. | Assign to IT provisioning staff who onboard users and allocate licenses. |

---

## The "Who Can Reset Whose Password?" Matrix (Crucial SC-300 Question)

A favorite SC-300 exam topic tests your knowledge of password reset boundaries. Higher-tier roles cannot have their passwords reset by lower-tier admins:

| Target User / Role to be Reset | Reset by Helpdesk Admin? | Reset by User Admin? | Reset by Auth Admin? | Reset by Priv Auth Admin? | Reset by Global Admin? |
|---|:---:|:---:|:---:|:---:|:---:|
| **Standard User (Non-admin)** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Guest User (External B2B)** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Helpdesk Admin** | ❌ | ✅ | ❌ | ✅ | ✅ |
| **User Admin** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Security Admin** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Billing Admin** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Conditional Access Admin** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Privileged Role Admin** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Global Admin** | ❌ | ❌ | ❌ | ✅ | ✅ |

> [!IMPORTANT]
> **Exam Golden Rules for Password Resets:**
> 1. **Helpdesk Admin** can **ONLY** reset non-administrators.
> 2. **User Admin** can reset non-administrators AND low-level admins (like Helpdesk Admin or Guest Inviter), but **NEVER** peers or higher admins (Billing, Security, CA, Privileged Role, Global).
> 3. **Authentication Admin** can reset MFA & passwords for **non-administrators only**.
> 4. **Privileged Authentication Admin** can reset passwords & MFA for **EVERYONE**, including Global Admins!

---

## The "Who Can Assign Roles?" Decision Tree

```
  Need to assign an Entra ID Directory Role?
       │
       ├── Is it via PIM (Privileged Identity Management)?
       │      └── Must be: Privileged Role Administrator OR Global Administrator
       │
       ├── Is it a direct static assignment in Entra portal?
       │      └── Must be: Privileged Role Administrator OR Global Administrator
       │
       └── Is it via a Role-Assignable Group?
              ├── To create/manage the group: Privileged Role Admin or Global Admin
              └── Group Owner can add/remove members (effectively granting the role without being an admin!)
                  *(Crucial exam technique: Delegating role management to group owners)*
```

---

## Global Administrator Elevation to Azure Resources

```
  [Global Administrator] in Entra ID
            │
            │ Toggles switch in Entra Portal:
            │ "Access management for Azure resources" = YES
            ▼
  Granted [User Access Administrator] at Root (/) Management Group in Azure ARM
            │
            │ Now can assign Azure RBAC permissions to ANY subscription:
            ▼
  Can grant [Owner] or [Contributor] on any Azure Subscription to themselves or others!
            │
            │ Once finished (Principle of Least Privilege):
            ▼
  Switch MUST be toggled back to NO!
```
