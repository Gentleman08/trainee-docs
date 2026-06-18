# Batch 5 — Authentication & Authorization
> Securing user identities and ensuring they only access what they should.

## 1. Broken Authentication
### Definition
Flaws in how a system verifies user identity, allowing attackers to compromise passwords, keys, or session tokens to assume the identities of other users.

### Real-World Dev/Testing Example
An API endpoint `/api/login` allows unlimited password attempts without rate limiting, or session tokens are entirely predictable (e.g., base64-encoded user IDs like `dXNlcjE=`).

### ASCII Diagram
```text
[Attacker]
   |--(10,000 password guesses)--> [Login API]
   |--(No Rate Limit)------------> [Access Granted!]
```

### Gotchas & Dev Context
- Don't reinvent the wheel; use your framework's built-in authentication mechanisms.
- Avoid passing session IDs in URLs (e.g., `?session=123`), as they get logged in browser history and server logs.
- Treat authentication like a locked door; if the lock is weak, all interior security measures are moot.

### Production FAQ
- **Q: How do we fix predictable session tokens?**
  **A:** Use a cryptographically secure pseudorandom number generator (CSPRNG) to generate session IDs with high entropy (at least 128 bits).

## 2. Insecure Direct Object References (IDOR)
### Definition
An access control flaw where an application exposes a reference to an internal object (like a file or database ID) and fails to verify if the user is actually authorized to access it.

### Real-World Dev/Testing Example
A user accesses their invoice at `/invoice?id=1001`. By simply changing the URL to `id=1002`, the server returns another customer's private invoice because it didn't check ownership.

### Gotchas & Dev Context
- Hiding links in the UI doesn't work; the backend API *must* enforce permissions.
- Sequential numeric IDs (1, 2, 3) make enumeration trivial.
- IDOR is the digital equivalent of asking a coat check attendant for jacket #42 and getting it without showing your ticket.

### Production FAQ
- **Q: Should we just use UUIDs instead of sequential IDs to prevent this?**
  **A:** UUIDs prevent attackers from easily guessing IDs, but you *must* still implement server-side authorization checks. UUIDs are obfuscation, not authorization.

## 3. Privilege Escalation (Vertical vs Horizontal)
### Definition
When a user gains access to rights or privileges beyond what is intended. Vertical escalation means gaining higher-level rights (User to Admin), while horizontal means accessing a peer's data.

### Real-World Dev/Testing Example
**Vertical:** An attacker intercepts an API request during profile update and injects `"role": "admin"`. The server blindly saves it.
**Horizontal:** Exploiting an IDOR vulnerability to view a colleague's private messages.

### Gotchas & Dev Context
- Never trust client-side data for privilege levels.
- Mass assignment vulnerabilities in ORMs are the most common cause of vertical escalation.
- Always validate actions against the server-side session object, not user-submitted parameters.

### Production FAQ
- **Q: How do we stop users from tampering with role assignments?**
  **A:** Strictly define allowed parameters in your controllers. Strip sensitive fields (like `role`, `is_admin`, `permissions`) from incoming request bodies before updating database records.

## 4. Session Hijacking / Fixation
### Definition
Session hijacking is stealing a valid session token to impersonate a user. Session fixation occurs when an attacker forces a known session token onto a user's browser *before* they log in.

### Real-World Dev/Testing Example
An attacker sends a phishing link with `?session_id=BAD123`. The victim logs in, the server uses that exact session ID for the authenticated state, and the attacker subsequently uses `BAD123` to hijack the account.

### ASCII Diagram
```text
[Attacker] --(Sets Session ID to 'XYZ')--> [Victim Browser]
[Victim]   --(Logs in with 'XYZ')--------> [Server]
[Attacker] --(Uses 'XYZ' to access)------> [Full Account Access!]
```

### Gotchas & Dev Context
- Setting long session timeouts increases the window of opportunity for hijacking.
- Cookies lacking proper flags are highly vulnerable to cross-site scripting (XSS) and network interception.

### Production FAQ
- **Q: How do we prevent session fixation?**
  **A:** Always regenerate the session ID immediately upon a successful login. 
- **Q: Are standard cookies safe?**
  **A:** Always set the `HttpOnly` flag (prevents JS access) and `Secure` flag (ensures HTTPS only) on session cookies.

## 5. Password Reset Flaws
### Definition
Weaknesses in the password recovery flow that allow attackers to bypass security checks and take over accounts they do not own.

### Real-World Dev/Testing Example
A reset link is sent via email, but the token is derived directly from the user's predictable username. Alternatively, the application relies on the `Host` header to build the reset link, allowing an attacker to inject their own domain (Host Header Injection) and steal the token.

### Gotchas & Dev Context
- Emailing new plain-text passwords is an anti-pattern.
- Displaying "User not found" on a reset form allows attackers to enumerate registered users. Always show a generic "If the email exists, a link was sent" message.

### Production FAQ
- **Q: What is the correct way to handle password reset tokens?**
  **A:** Generate a large, random, single-use token. Tie it to the specific user account in the database and enforce a strict expiration time (e.g., 15-30 minutes).

## 6. Brute Force & Credential Stuffing
### Definition
Brute force involves systematically guessing passwords until successful. Credential stuffing utilizes massive lists of leaked username/password pairs from other data breaches to hijack accounts.

### Real-World Dev/Testing Example
An attacker runs an automated script to test 50,000 common passwords against an admin portal. Or, they take a 10-million row database from a leaked forum and test those exact credentials against a banking app.

### Gotchas & Dev Context
- Simple CAPTCHAs can often be bypassed by human "click farms" or advanced AI bots.
- Strict account lockout policies (e.g., lock after 3 tries) can be abused to lock out legitimate users, causing a Denial of Service (DoS).

### Production FAQ
- **Q: What's the most robust defense against credential stuffing?**
  **A:** Enforce Multi-Factor Authentication (MFA). Additionally, implement rate limiting by IP and track anomalous login locations to challenge suspicious attempts.

## 7. OAuth 2.0 / OpenID Connect Misconfigurations
### Definition
Flaws in integrating third-party logins (like "Sign in with Google" or "Login with GitHub") that allow attackers to steal authorization codes or bypass authentication entirely.

### Real-World Dev/Testing Example
The application fails to strictly validate the `redirect_uri`. An attacker crafts a malicious OAuth link, and when the victim logs in, their authorization code is sent back to `https://attacker.com/callback` instead of the legitimate application.

### Gotchas & Dev Context
- OAuth is complex; rolling your own implementation instead of using proven libraries is extremely risky.
- Treat OAuth tokens with the same sensitivity as passwords.

### Production FAQ
- **Q: Why is the `state` parameter so important?**
  **A:** The `state` parameter prevents Cross-Site Request Forgery (CSRF). Without it, an attacker could force a victim to log into the attacker's account, potentially capturing the victim's sensitive data when they interact with the app.

## 8. Role-Based Access Control (RBAC) (Patching)
### Definition
A security design paradigm where access to resources is granted based on the user's assigned role within the system, rather than checking individual permissions for every single user.

### Real-World Dev/Testing Example
Instead of writing `if (user.can_edit_post && user.can_delete_post)` everywhere, the system checks `if (user.role == 'EDITOR' || user.role == 'ADMIN')`. 

### Gotchas & Dev Context
- Avoid "role explosion" where you end up with hundreds of ultra-specific roles that are impossible to manage.
- Hardcoding role checks in every UI component and API endpoint is brittle; rely on central middleware.

### Production FAQ
- **Q: How do we implement RBAC cleanly in our codebase?**
  **A:** Define a centralized policy matrix. Use decorators or middleware to enforce roles at the route or controller level (e.g., `@RequireRole('ADMIN')`), keeping business logic separate from authorization logic.

## 9. Secure Password Storage (Bcrypt/Argon2) (Patching)
### Definition
Protecting stored user passwords using slow, memory-hard cryptographic hashing algorithms paired with unique salts, making offline database cracking impractically slow and expensive.

### Real-World Dev/Testing Example
Instead of storing a fast hash like `MD5("password123")`, the backend stores a slow hash string like `$argon2id$v=19$m=65536,t=3,p=4$salt...`.

### Gotchas & Dev Context
- Standard hash functions (SHA-256, MD5) are designed for speed. Modern GPUs can crack billions of fast hashes per second.
- Never write your own hashing logic. Always use well-vetted, standard libraries.
- "Salting" ensures that identical passwords have completely different hashes, thwarting pre-computed rainbow table attacks.

### Production FAQ
- **Q: Why should we use Argon2 over Bcrypt?**
  **A:** While Bcrypt is great, Argon2 is "memory-hard," meaning it requires a significant amount of RAM to compute. This makes it highly resistant to cracking attempts by specialized hardware (like ASICs or GPU clusters) compared to Bcrypt.
