# Batch 6 — Misconfigurations & Advanced Flaws
> Complex server-side vulnerabilities and architectural missteps.

## 1. Server-Side Request Forgery (SSRF)

**Definition:**
SSRF occurs when an attacker tricks a web server into making network requests on their behalf, often targeting internal systems the attacker cannot reach directly.

**Real-World Dev/Testing Example:**
A web app accepts a URL to fetch an avatar image. An attacker inputs `http://169.254.169.254/latest/meta-data/` to make the server fetch sensitive AWS IAM credentials instead of an image.

**ASCII Diagram:**
```text
[Attacker] --(url=http://internal-db)--> [Web Server] --(fetches data)--> [Internal DB]
                                              |
[Attacker] <---------(returns DB data)--------+
```

**Gotchas & Dev Context:**
*   **Cloud Metadata:** Cloud environments (AWS, GCP, Azure) expose sensitive metadata on local IPs (e.g., `169.254.169.254`).
*   **Blind SSRF:** Sometimes the server makes the request but doesn't return the output to the attacker, making detection harder.
*   **Protocol Smuggling:** Attackers might use `file://`, `dict://`, or `gopher://` schemas, not just `http://`.

**Production FAQ:**
*   *How do we fix SSRF effectively?*
    Never use blacklists (they can be bypassed). Use strict allow-lists for domains/IPs, disable unused URI schemas, and block internal IP ranges using network-level rules.

## 2. XML External Entity (XXE)

**Definition:**
XXE is a flaw where a poorly configured XML parser processes malicious external entities within an XML document, allowing attackers to read local files or scan internal networks.

**Real-World Dev/Testing Example:**
A B2B application accepts SOAP/XML invoices. An attacker submits an XML file defining an external entity pointing to `file:///etc/passwd`. When the server parses the XML, it embeds the file contents into the response.

**ASCII Diagram:**
```text
XML Input: <!ENTITY xxe SYSTEM "file:///etc/passwd">
                         |
                   [XML Parser] ---> Reads /etc/passwd
                         |
                   [Response] ---> Attacker sees file contents
```

**Gotchas & Dev Context:**
*   **SVG Uploads:** SVG images are XML-based. Uploading a malicious SVG can trigger XXE.
*   **Out-of-Band (OOB) XXE:** If the app doesn't reflect the output, attackers can force the server to send the file contents to their own external server.

**Production FAQ:**
*   *How do I patch XXE across my application?*
    Completely disable Document Type Definitions (DTDs) and external entities in your XML parser configuration. Modern frameworks usually disable them by default, but legacy systems are prime targets.

## 3. Insecure Deserialization

**Definition:**
This vulnerability happens when untrusted data is used to reconstruct (deserialize) an object. Attackers manipulate the serialized data to alter app logic or execute arbitrary code.

**Real-World Dev/Testing Example:**
A PHP application stores user session data as a base64-encoded serialized object in a cookie. An attacker modifies the cookie to inject a malicious "magic method" payload, leading to Remote Code Execution (RCE) when the server deserializes it.

**Gotchas & Dev Context:**
*   **Language Specific:** Highly dependent on the backend (Java, C#, PHP, Python's `pickle`).
*   **Gadget Chains:** Attackers often rely on "gadgets"—existing classes in the application's environment that can be chained together to achieve code execution.

**Production FAQ:**
*   *Can we secure native deserialization?*
    It's exceptionally difficult. The safest patch is to completely avoid serializing native objects. Use pure data formats like JSON or Protocol Buffers instead. If you must deserialize native objects, use strict type-checking and digital signatures (e.g., HMAC) to ensure data integrity.

## 4. Open Redirect

**Definition:**
An Open Redirect occurs when an application takes a user-supplied URL and redirects the user to it without validation, enabling phishing and token theft.

**Real-World Dev/Testing Example:**
A login portal uses a `next` parameter: `https://app.com/login?next=https://evil.com`. After logging in, the user is seamlessly redirected to a fake lookalike site that steals their session or prompts for payment.

**Gotchas & Dev Context:**
*   **OAuth Abuse:** Often chained with OAuth flows to steal authorization tokens by redirecting the callback to an attacker-controlled server.
*   **Bypass Tricks:** Attackers use tricks like `https://app.com/login?next=\\evil.com` or URL encoding to bypass weak regex filters.

**Production FAQ:**
*   *What is the best way to handle dynamic redirects safely?*
    Avoid taking absolute URLs from user input. If you must, map target URLs to an internal ID (e.g., `?next_id=1`). Alternatively, enforce that redirects only happen to relative paths (e.g., `/dashboard`) or strictly validate against an allow-list of trusted domains.

## 5. Directory Traversal / Path Traversal

**Definition:**
Directory Traversal allows attackers to access files and directories stored outside the intended web root folder by manipulating file path variables.

**Real-World Dev/Testing Example:**
An app loads templates via a URL parameter: `https://app.com/view?file=report.html`. An attacker changes it to `?file=../../../../etc/shadow` to escape the web directory and read system password hashes.

**ASCII Diagram:**
```text
Intended: /var/www/html/templates/report.html
Attacker: /var/www/html/templates/../../../../etc/shadow
          (Resolves to) --> /etc/shadow
```

**Gotchas & Dev Context:**
*   **Null Byte Injection:** Legacy systems might be vulnerable to appending `%00` to bypass file extension checks (e.g., `../../../etc/passwd%00.pdf`).
*   **Encoding:** Attackers use URL encoding (`%2e%2e%2f`) or double URL encoding to bypass basic WAFs or input filters looking for `../`.

**Production FAQ:**
*   *How do we securely serve dynamic files?*
    Do not let user input directly dictate file paths. Use an indirect reference map (e.g., `file=1` maps to `report.html`). If you must use file names, validate input strictly (alphanumeric only) and use path canonicalization functions (like `realpath()` in PHP) to ensure the resolved path stays inside the target directory.

## 6. Rate Limiting Bypass

**Definition:**
This occurs when an application fails to properly throttle repeated requests, allowing attackers to perform brute-force attacks, credential stuffing, or API scraping.

**Real-World Dev/Testing Example:**
An API limits logins to 5 attempts per IP. An attacker bypasses this by injecting a spoofed `X-Forwarded-For: 192.168.1.[dynamic]` header with each request, tricking the server into thinking every attempt comes from a different IP.

**Gotchas & Dev Context:**
*   **Distributed Attacks:** Attackers use botnets or proxy rotators to naturally distribute requests across thousands of real IPs.
*   **Endpoint Asymmetry:** Login might be rate-limited, but a "Forgot Password" or "Account Recovery" endpoint might not be, serving as an alternative brute-force entry point.

**Production FAQ:**
*   *How do we enforce robust rate limits?*
    Don't rely solely on IP addresses. Rate limit based on user accounts, API keys, or device fingerprints. Implement CAPTCHAs, progressive delays (exponential backoff), and ensure proxy headers (like `X-Forwarded-For`) are only trusted from known, internal load balancers.

## 7. Security Misconfiguration

**Definition:**
Security misconfigurations are insecure default settings, unpatched flaws, open administrative ports, or verbose error messages left exposed in production.

**Real-World Dev/Testing Example:**
A dev spins up a MongoDB instance and leaves the default port (27017) exposed to the internet without a password. An attacker scans for the port, connects, and deletes the database, leaving a ransom note.

**Gotchas & Dev Context:**
*   **Verbose Errors:** Frameworks in "Debug Mode" (like Django or Laravel) can dump sensitive environment variables, database credentials, and stack traces directly to the user.
*   **Orphaned Assets:** Old API versions (`/api/v1/`) left running alongside new ones, bypassing modern security checks.

**Production FAQ:**
*   *What is the best defense against misconfigurations?*
    Implement "Infrastructure as Code" (IaC) to standardize deployments. Run automated configuration scanners (like Trivy or Checkov), enforce CIS Benchmarks, and ensure debugging features are strictly disabled in CI/CD pipelines before production release.

## 8. Business Logic Vulnerabilities

**Definition:**
Business logic flaws occur when legitimate application features are manipulated in unintended sequences to achieve a malicious outcome, bypassing the rules of the system.

**Real-World Dev/Testing Example:**
An e-commerce site allows users to add items to a cart. An attacker intercepts the request and changes the item quantity to `-5`. The application calculates the total (`-5 * $10 = -$50`), effectively crediting the attacker's account.

**Gotchas & Dev Context:**
*   **Invisible to Scanners:** Automated vulnerability scanners (DAST/SAST) almost never catch these because they require understanding the specific context of the app.
*   **State Confusion:** Attackers might skip steps in a multi-step process (e.g., going straight from 'Cart' to 'Receipt' without hitting the 'Payment' endpoint).

**Production FAQ:**
*   *How do we test for and prevent logic flaws?*
    Rely on rigorous threat modeling, state management enforcement, and unit/integration testing that explicitly covers edge cases (e.g., negative numbers, out-of-order requests). Human penetration testing is crucial here.

## 9. Secure Headers (HSTS, X-Frame-Options)

**Definition:**
Secure headers are HTTP response headers that instruct the user's browser on how to behave securely, preventing attacks like Clickjacking or Man-in-the-Middle (MitM).

**Real-World Dev/Testing Example:**
A site lacks `X-Frame-Options`. An attacker embeds the site in a hidden `<iframe>` on a malicious page. When an authenticated user clicks a fake "Win a Prize" button on the attacker's site, they are actually clicking the hidden "Transfer Funds" button on the real site (Clickjacking).

**Gotchas & Dev Context:**
*   **HSTS Lockout:** If you enable `Strict-Transport-Security` (HSTS) with a long expiration and your SSL certificate expires, users will be completely locked out of the site—browsers won't allow bypassing the warning.
*   **Content Security Policy (CSP):** Highly effective against XSS, but notoriously difficult to configure without breaking legitimate inline scripts or external trackers.

**Production FAQ:**
*   *How do we roll out secure headers safely?*
    Start in report-only mode (especially for CSP). Implement `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, and roll out HSTS with a very short `max-age` initially (e.g., 5 minutes). Gradually increase the HSTS `max-age` as stability is confirmed.
