# Batch 1 — Web Application Basics
> The foundation of how modern web applications communicate and operate.

## HTTP / HTTPS Protocols
### Definition
HTTP (Hypertext Transfer Protocol) is the fundamental rulebook for sending data over the web. HTTPS is the secure version, wrapping that data in encryption (TLS/SSL) so interceptors only see gibberish.

### Real-World Dev/Testing Example
When you log into a banking app, the browser uses HTTPS to send your password. A VAPT (Vulnerability Assessment & Penetration Testing) tester will intercept the traffic. If it's HTTP, the password is in plain text. If HTTPS, it's encrypted.

### ASCII Diagram
```text
[Browser] --- (Plain Text HTTP) ---> [Hacker sees: password123] ---> [Server]
[Browser] --- (Encrypted HTTPS) ---> [Hacker sees: x#9@k$1z...] ---> [Server]
```

### Gotchas & Dev Context
- Mixed content (loading HTTP scripts on an HTTPS page) breaks the secure lock icon.
- HTTPS relies on certificates; expired certificates throw scary browser warnings.
- HSTS (HTTP Strict Transport Security) forces browsers to only use HTTPS.

### Production FAQ
**Q: We enabled HTTPS. Are we secure from attacks?**
A: No. HTTPS encrypts data *in transit*. It doesn't protect against SQL injection, XSS, or poor logic. *Patch:* Ensure secure coding practices and WAFs are in place alongside HTTPS.

## HTTP Request / Response Cycle
### Definition
The standard conversation of the web: a client (browser) asks for something (Request), and the server replies with data or an error (Response).

### Real-World Dev/Testing Example
A user clicks "Buy." The browser sends a `POST` Request to `/checkout`. The server checks inventory, charges the card, and sends back a `200 OK` Response with a receipt.

### ASCII Diagram
```text
  Client                 Server
    | --- Request -------> |
    |                      | (Processes)
    | <------ Response --- |
```

### Gotchas & Dev Context
- `GET` requests append data in the URL (bad for secrets). Use `POST` for sensitive data.
- Headers are easily manipulated. Never trust `User-Agent` or `Referer` blindly.
- Status codes matter: `4xx` is client error, `5xx` is server error.

### Production FAQ
**Q: How do attackers exploit the request cycle?**
A: They tamper with hidden fields or parameters in the request before it reaches the server (e.g., changing price=100 to price=1). *Patch:* Always validate and sanitize all incoming request data on the server-side.

## Cookies & Sessions
### Definition
Because HTTP is "stateless" (amnesiac), servers use Sessions to remember you, handing your browser a temporary ID badge called a Cookie to prove who you are on the next request.

### Real-World Dev/Testing Example
You log into Amazon. The server creates Session #999, stores your cart there, and sends your browser a Cookie `session_id=999`. Your browser sends this cookie back every time you click a new page.

### Gotchas & Dev Context
- `HttpOnly` flag prevents JavaScript from reading the cookie (mitigates XSS).
- `Secure` flag ensures the cookie only travels over HTTPS.
- `SameSite` attribute helps prevent Cross-Site Request Forgery (CSRF).

### Production FAQ
**Q: An attacker stole an active session cookie. What happens?**
A: They can impersonate the user completely (Session Hijacking). *Patch:* Set short session timeouts, regenerate session IDs on login/privilege change, and tie sessions to user metadata (like IP/device) to detect anomalies.

## JSON Web Tokens (JWT)
### Definition
A self-contained digital passport. Instead of the server remembering your session, it gives you a cryptographically signed JSON object (JWT) containing your user data.

### Real-World Dev/Testing Example
A mobile app logs in and receives a JWT: `Header.Payload.Signature`. The app sends this token in the `Authorization` header. The server verifies the signature without needing to look up a session database.

### ASCII Diagram
```text
eyJhbG... (Header: algorithm)
.eyJzdW... (Payload: user data/roles)
.SflKxw... (Signature: verify me)
```

### Gotchas & Dev Context
- JWTs are *encoded*, not encrypted. Anyone can read the payload. Don't put SSNs in them.
- Invalidation is hard. Unlike sessions, you can't just delete them from the server to log a user out instantly without a blacklist.
- The `none` algorithm vulnerability allowed attackers to bypass signature checks.

### Production FAQ
**Q: Can a user modify their JWT to become an admin?**
A: Only if the server fails to verify the cryptographic signature. *Patch:* Always use strong signing keys, enforce the expected algorithm (e.g., HS256/RS256), and explicitly reject the `none` algorithm.

## Cross-Origin Resource Sharing (CORS)
### Definition
CORS is a security mechanism that tells the browser whether a web application running at one origin (domain) is allowed to access resources from a different origin.

### Real-World Dev/Testing Example
Your frontend on `cool-app.com` tries to fetch data from `api.backend.com`. If `api.backend.com` doesn't explicitly send a CORS header saying "I allow cool-app.com," the browser blocks the read.

### Gotchas & Dev Context
- CORS is enforced by the *browser*, not the server. Postman or cURL will bypass CORS entirely.
- Wildcards `Access-Control-Allow-Origin: *` are dangerous if the API deals with authenticated user data.
- "Preflight" `OPTIONS` requests happen automatically to check permissions before sending `PUT` or `DELETE`.

### Production FAQ
**Q: We get a CORS error. Should we just set it to `*` to fix it quickly?**
A: Absolutely not. Setting `*` allows any malicious website to read your users' data via their browsers. *Patch:* Maintain a strict whitelist of trusted origins and reflect the specific origin if it matches the whitelist.

## Same-Origin Policy (SOP)
### Definition
The browser's strictest bouncer. It dictates that scripts from one website cannot read or modify data from another website unless explicitly permitted.

### Real-World Dev/Testing Example
If you are logged into `bank.com` in one tab and visit `evil.com` in another, SOP prevents `evil.com`'s JavaScript from reading your `bank.com` DOM or session cookies.

### Gotchas & Dev Context
- "Origin" means the exact combination of Scheme (http/https), Host (domain), and Port.
- SOP restricts reading data, but often allows *embedding* (like `<img>` or `<script>`) or *sending* (like submitting a form, which leads to CSRF).
- CORS is the authorized loophole designed to relax SOP when necessary.

### Production FAQ
**Q: Since SOP protects us, are we safe from cross-site attacks?**
A: Not completely. SOP doesn't stop an attacker from tricking the browser into sending a state-changing request (CSRF). *Patch:* Implement Anti-CSRF tokens to verify the request intentionally originated from your actual frontend.

## Document Object Model (DOM)
### Definition
The DOM is a tree-like representation of a webpage that the browser creates. It allows JavaScript to dynamically read, change, or delete HTML elements and styles on the fly.

### Real-World Dev/Testing Example
When you get a notification, JavaScript finds the notification icon node in the DOM and changes its text from "0" to "1".

### ASCII Diagram
```text
      Document
         |
       <html>
      /      \
  <head>    <body>
    |         |
 <title>    <h1>
```

### Gotchas & Dev Context
- If user input is written directly into the DOM without sanitization, it leads to DOM-based XSS.
- Modern frameworks (React, Vue) use a "Virtual DOM" to update the actual DOM safely and efficiently.
- Using properties like `innerHTML` is risky; `innerText` or `textContent` are safer.

### Production FAQ
**Q: How do we prevent DOM-based XSS?**
A: Attackers manipulate sources (like URL fragments) that flow into unsafe sinks (like `eval()` or `innerHTML`). *Patch:* Avoid direct DOM manipulation with untrusted data. Use strict context-aware sanitization libraries like DOMPurify.

## RESTful APIs vs GraphQL
### Definition
REST gives you multiple fixed URLs (endpoints) that return specific chunks of data. GraphQL gives you one endpoint and lets the client precisely query only the data it needs.

### Real-World Dev/Testing Example
In REST, getting a user's profile and their posts requires calling `/users/1` and `/users/1/posts`. In GraphQL, you send one query asking exactly for `user { name, posts { title } }`.

### Gotchas & Dev Context
- REST relies heavily on HTTP methods (GET, POST, PUT, DELETE) and status codes.
- GraphQL typically uses only POST and returns `200 OK` even if there are errors (errors are inside the JSON payload).
- GraphQL is vulnerable to nested query attacks (asking for user -> friends -> friends -> friends) that can crash the server.

### Production FAQ
**Q: What is a major security risk unique to GraphQL?**
A: Deeply nested or massively batched queries causing Denial of Service (DoS). *Patch:* Implement query depth limiting, query complexity analysis, and strict rate limiting on your GraphQL resolvers.

## WebSockets
### Definition
A persistent, two-way communication channel between the client and server. Unlike HTTP's "ask and wait," WebSockets allow both sides to instantly push messages at any time.

### Real-World Dev/Testing Example
A live chat application or a multiplayer game. The server pushes new messages to all connected browsers instantly without the browsers having to constantly ask, "Are there new messages?"

### Gotchas & Dev Context
- Starts as an HTTP request, then "upgrades" to a WebSocket (`ws://` or `wss://`).
- They do not strictly adhere to Same-Origin Policy, making them vulnerable to Cross-Site WebSocket Hijacking (CSWSH).
- Firewalls or load balancers might drop long-idle connections.

### Production FAQ
**Q: How do we secure WebSocket connections?**
A: WebSockets don't automatically validate origins or handle authentication natively after the handshake. *Patch:* Always validate the `Origin` header during the handshake, use WSS (TLS), and verify user authentication tokens before accepting the connection.

## Microservices Architecture (Security perspective)
### Definition
Breaking a massive, monolithic application into smaller, independent services (e.g., Auth Service, Payment Service) that talk to each other over a network.

### Real-World Dev/Testing Example
An e-commerce site uses a Cart microservice and an Inventory microservice. When a user adds an item, the Cart service sends an internal API request to the Inventory service to check stock.

### Gotchas & Dev Context
- Attack surface multiplies. Every service-to-service communication is a potential interception point.
- Hard to trace requests across dozens of services without centralized logging.
- "Zero Trust" is required. Services shouldn't blindly trust a request just because it came from another internal service.

### Production FAQ
**Q: If an attacker breaches a low-priority microservice, are the others safe?**
A: Often no, due to overly permissive internal networks. *Patch:* Implement Mutual TLS (mTLS) for service-to-service encryption, enforce least privilege IAM roles, and require internal authentication tokens (like JWT) to verify the originating user context.
