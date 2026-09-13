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
