# Batch 1 — Internet & Web Fundamentals
> How the web works under the hood — what every developer must know before writing a single line of code.

---

## 1. How the Internet Works

### Definition
The Internet is a global network of computers that communicate by passing data packets through physical cables, fibre, and wireless signals. Think of it as a postal system — data is broken into small "letters" (packets), each addressed and routed independently to reach the destination.

### Real-World Dev Example
When you visit `https://github.com`, your device sends packets through several routers across the world before GitHub's servers receive your request and send back the page.

### ASCII Diagram
```
Your PC ──► Router ──► ISP ──► Backbone Network ──► GitHub Server
                                   (many hops)
```

### Gotchas & Dev Context
- Data doesn't travel in one chunk — it's split into packets that may take *different routes* and reassemble at the destination.
- Latency (delay) is physical — servers in another continent will always be slower. CDNs exist to fix this.
- "The Internet" ≠ "The Web" — the Web (HTTP) is just one service running *on top of* the Internet (others: email, FTP, SSH).
- Packet loss is real — protocols like TCP handle retransmission automatically.

### Production FAQ
**Q: My API is slow for users in Southeast Asia but fast locally. Why?**
A: Your server is likely hosted in the US. Physical distance adds ~150ms of round-trip time. Use a CDN or deploy a regional server.

**Q: Can packets be intercepted in transit?**
A: Yes — this is why HTTPS (TLS encryption) exists. Plain HTTP packets are readable by anyone on the same network path.

---

## 2. Client-Server Model

### Definition
A **client** is any device that *requests* data (browser, mobile app, curl). A **server** is a machine that *responds* with data. Every web interaction follows this ask-and-answer pattern.

### Real-World Dev Example
```js
// Client (browser) asks for user data
fetch('https://api.example.com/users/42')
  .then(res => res.json())
  .then(data => console.log(data));

// Server responds with JSON
// { "id": 42, "name": "Priya", "role": "admin" }
```

### ASCII Diagram
```
 [Client]                          [Server]
 Browser  ──── HTTP Request ────►  Node.js / Django / Rails
          ◄─── HTTP Response ────  (sends back JSON / HTML)
```

### Gotchas & Dev Context
- One server can handle thousands of clients simultaneously (via threads or async I/O).
- The client only gets what the server explicitly sends — it cannot access the server's filesystem directly.
- Mobile apps are clients too, not just browsers.
- Peer-to-Peer (P2P) is a different model where both sides are client *and* server (e.g., BitTorrent).

### Production FAQ
**Q: My frontend and backend are on different machines. Is that a problem?**
A: No — that's the standard setup. Just ensure CORS is configured correctly (see #20).

**Q: Can a server call another server?**
A: Absolutely. In microservices, servers constantly call each other's APIs — a server acts as a *client* to downstream services.

---

## 3. HTTP / HTTPS

### Definition
**HTTP** (HyperText Transfer Protocol) is the rulebook for how clients and servers exchange data on the web. **HTTPS** is HTTP with a TLS encryption layer — so data in transit is scrambled and unreadable to eavesdroppers.

### Real-World Dev Example
```bash
# Plain HTTP — data visible in transit (never use for sensitive data)
curl http://api.example.com/login

# HTTPS — encrypted channel
curl https://api.example.com/login
```

### ASCII Diagram
```
HTTP:   Client ──── plain text ────► Server   (anyone can read)
HTTPS:  Client ──── 🔒 encrypted ──► Server   (only endpoints can read)
```

### Gotchas & Dev Context
- HTTPS requires an SSL/TLS certificate. Free certs via **Let's Encrypt**; managed certs via AWS ACM / Cloudflare.
- HTTP/2 and HTTP/3 are newer versions — they support multiplexing (multiple requests over one connection) and are faster.
- Browsers mark HTTP sites as "Not Secure" since 2018 — always use HTTPS in production.
- `http://localhost` is an exception — browsers allow it without warnings during local dev.

### Production FAQ
**Q: Does HTTPS slow down my API?**
A: The TLS handshake adds ~1 round trip on first connection, but modern TLS 1.3 and session resumption make this negligible. The security benefit vastly outweighs it.

**Q: My cert expired and the site is down. How do I prevent this?**
A: Use auto-renewal via Certbot (Let's Encrypt) or managed cert services. Set a calendar alert 30 days before expiry as a backup.

---

## 4. HTTP Methods (GET, POST, PUT, PATCH, DELETE)

### Definition
HTTP methods tell the server *what action* to perform. They're the verbs of the web — GET means "give me data," POST means "create something," and so on.

### Real-World Dev Example
```bash
GET    /users/42        # Fetch user 42
POST   /users           # Create a new user (body has user data)
PUT    /users/42        # Replace user 42 entirely
PATCH  /users/42        # Update only specific fields of user 42
DELETE /users/42        # Delete user 42
```

### Gotchas & Dev Context
- **GET** requests should *never* modify data. Search engines crawl GET URLs — you don't want a bot deleting records.
- **POST vs PUT**: POST creates a *new* resource (server picks the ID); PUT replaces at a *known* URL.
- **PUT vs PATCH**: PUT sends the full object; PATCH sends only the changed fields — more efficient for large objects.
- **Idempotency**: GET, PUT, DELETE are idempotent (same call = same result). POST is not. PATCH technically isn't either.
- HTML forms only natively support GET and POST — frameworks fake PUT/DELETE with a hidden `_method` field.

### Production FAQ
**Q: Can I send a body with a GET request?**
A: Technically yes, but it's not standard. Most servers and proxies ignore or reject it. Use query parameters instead.

**Q: Why does our delete endpoint use POST instead of DELETE?**
A: Some older proxies and firewalls block non-GET/POST methods. It's a workaround, but not best practice — prefer DELETE with proper server config.

---

## 5. HTTP Status Codes (1xx–5xx)

### Definition
Status codes are 3-digit numbers the server returns to tell the client *what happened* with the request. They're grouped by the leading digit into five classes.

### Real-World Dev Example
```bash
200 OK              # Success — here's your data
201 Created         # Resource was created (after POST)
301 Moved Permanently # URL has changed, redirecting
400 Bad Request     # Client sent garbage (missing field, wrong type)
401 Unauthorized    # Not logged in
403 Forbidden       # Logged in but not allowed
404 Not Found       # Resource doesn't exist
422 Unprocessable   # Validation failed
429 Too Many Requests # Rate limited
500 Internal Server Error # Server crashed
503 Service Unavailable   # Server overloaded or down
```

### Gotchas & Dev Context
- **401 vs 403**: 401 = "who are you?" (auth missing); 403 = "I know who you are, but no" (permission denied).
- **200 vs 204**: Return 204 (No Content) for successful DELETEs — don't send an empty 200 body.
- Many APIs lazily return 200 with `{ "error": "not found" }` in the body — this breaks client error handling. Always use correct status codes.
- **1xx** (Informational) are rare in everyday dev but 101 is used to upgrade to WebSocket connections.

### Production FAQ
**Q: Our monitoring shows a spike in 503s. What does that mean?**
A: Your server is overwhelmed or unhealthy. Check CPU/memory, auto-scaling settings, and whether a downstream dependency is down.

**Q: Should I return 400 or 422 for validation errors?**
A: Prefer **422 Unprocessable Entity** for semantic validation failures (e.g., "email format is wrong") and 400 for syntactically broken requests (e.g., malformed JSON).

---

## 6. HTTP Headers

### Definition
Headers are key-value metadata attached to every HTTP request and response. They carry instructions about content format, authentication, caching, and access control — separate from the body payload.

### Real-World Dev Example
```bash
# Request headers
curl https://api.example.com/data \
  -H "Authorization: Bearer eyJhbGciOi..." \
  -H "Content-Type: application/json" \
  -H "Accept: application/json"

# Response headers (server sends back)
Content-Type: application/json
Cache-Control: max-age=3600
Access-Control-Allow-Origin: https://myfrontend.com
```

### Key Headers to Know

| Header | Purpose |
|---|---|
| `Content-Type` | Format of the request/response body (`application/json`, `text/html`) |
| `Authorization` | Carries auth token (`Bearer <token>`, `Basic <base64>`) |
| `Cache-Control` | How long clients/proxies should cache the response |
| `Access-Control-Allow-Origin` | CORS — which origins can read the response |
| `Accept` | What format the client *wants* back |

### Gotchas & Dev Context
- Forgetting `Content-Type: application/json` when POSTing JSON is a classic bug — the server reads it as plain text and fails to parse.
- Never log `Authorization` headers in plaintext production logs — it's a security leak.
- `Cache-Control: no-store` vs `no-cache`: `no-store` never saves; `no-cache` saves but always revalidates.

### Production FAQ
**Q: My POST request sends data but the server says the body is empty. Why?**
A: You're likely missing `Content-Type: application/json`. The server doesn't know how to parse the body without it.

**Q: How do I disable caching for an API endpoint?**
A: Set `Cache-Control: no-store, no-cache, must-revalidate` in the response header.

---

## 7. Request / Response Cycle

### Definition
Every web interaction is a complete loop: the client sends a **request** (with method, URL, headers, optional body) and the server sends back a **response** (status code, headers, optional body). This cycle is the heartbeat of the web.

### ASCII Diagram
```
Client                                    Server
  │                                          │
  │── 1. DNS lookup (example.com → IP) ─────►│
  │── 2. TCP handshake ──────────────────────►│
  │── 3. TLS handshake (HTTPS) ─────────────►│
  │                                          │
  │── 4. HTTP Request ───────────────────────►│
  │   GET /users/1 HTTP/1.1                  │
  │   Host: api.example.com                  │
  │   Authorization: Bearer ...              │
  │                                          │── 5. Process request
  │                                          │   (DB query, logic)
  │◄─ 6. HTTP Response ──────────────────────│
  │   HTTP/1.1 200 OK                        │
  │   Content-Type: application/json         │
  │   {"id":1,"name":"Alex"}                 │
```

### Gotchas & Dev Context
- Steps 1–3 happen *before* your app code runs — they add latency you can't eliminate but can reduce (keep-alive, CDN, DNS TTL tuning).
- HTTP/1.1 reuses TCP connections (`Connection: keep-alive`) to skip steps 1–3 on subsequent requests.
- HTTP/2 multiplexes multiple requests over one connection simultaneously.
- In DevTools → Network tab, you can inspect every step of this cycle in real time.

### Production FAQ
**Q: A specific API call takes 800ms. How do I know where the time is being spent?**
A: Use DevTools Network tab or server-side tracing (OpenTelemetry). Break it down: DNS, TCP, TLS, time to first byte (TTFB), content download.

---

## 8. URL Structure

### Definition
A URL (Uniform Resource Locator) is the full address to a specific resource on the web. Each part of a URL has a distinct job and understanding them prevents common routing and query bugs.

### ASCII Diagram
```
https://api.example.com:443/users/42?sort=asc&page=2#section3
│──────│ │──────────────│ │──│ │──────│ │──────────────│ │──────│
Protocol    Domain/Host  Port  Path     Query String    Fragment
```

| Part | Example | Purpose |
|---|---|---|
| Protocol | `https` | Transfer rulebook to use |
| Domain | `api.example.com` | Server address (resolved via DNS) |
| Port | `:443` | Network port (443=HTTPS, 80=HTTP — often implicit) |
| Path | `/users/42` | Specific resource on the server |
| Query | `?sort=asc&page=2` | Extra parameters, key=value pairs |
| Fragment | `#section3` | Client-side only; browser jumps to section |

### Gotchas & Dev Context
- **Fragment (`#`) is never sent to the server** — it's 100% client-side. Don't try to read it in your backend.
- URL-encode special characters: spaces become `%20` or `+`. Use `encodeURIComponent()` in JS.
- Path parameters (`/users/42`) vs query parameters (`?id=42`) — use path params for resource identity, query params for filtering/sorting.
- Maximum URL length is ~2000 characters in most browsers — don't shove large data into query strings.

### Production FAQ
**Q: My API returns 404 for `/users/42` but works for `/users/42/`. Why?**
A: Trailing slash matters in some frameworks. Configure your server to normalize URLs (redirect with/without slash consistently).

**Q: Should filters go in the path or query string?**
A: Query string — paths identify resources, queries filter/sort them. `GET /products?category=shoes&sort=price` ✅

---

## 9. DNS Resolution

### Definition
DNS (Domain Name System) translates human-readable domain names like `github.com` into IP addresses like `140.82.121.4` that computers use to connect. It's the phonebook of the Internet.

### ASCII Diagram
```
Browser asks: "What's the IP for github.com?"

Browser Cache → OS Cache → Resolving Resolver (ISP)
                                    │
                           ┌────────▼────────┐
                           │   Root Server   │  "Ask .com TLD server"
                           └────────┬────────┘
                                    │
                           ┌────────▼────────┐
                           │  .com TLD Server│  "Ask github.com's NS"
                           └────────┬────────┘
                                    │
                           ┌────────▼────────────┐
                           │ GitHub's Nameserver  │  "IP = 140.82.121.4"
                           └─────────────────────┘
```

### Gotchas & Dev Context
- DNS results are **cached** — TTL (Time to Live) controls how long. Lowering TTL before a migration speeds up propagation.
- DNS propagation after a change can take up to 48 hours globally (due to caching at every level).
- `nslookup github.com` or `dig github.com` — use these to debug DNS from terminal.
- Load balancers use DNS round-robin or health-check-aware DNS (AWS Route 53 failover) to distribute traffic.

### Production FAQ
**Q: We updated our DNS record but some users still see the old server. Why?**
A: Their ISP's resolver cached the old record. You must wait for the TTL to expire. Next time, lower TTL *before* the migration.

**Q: What's the difference between an A record and a CNAME?**
A: An A record maps domain → IP directly. A CNAME maps domain → another domain name (alias). Use CNAMEs for subdomains pointing to load balancers or CDNs.

---

## 10. TCP/IP

### Definition
**TCP/IP** is the foundational protocol pair that powers all Internet communication. **IP** handles addressing and routing packets to the right machine; **TCP** ensures those packets arrive in order and without loss.

### ASCII Diagram
```
TCP 3-Way Handshake (before any data flows):

Client ──── SYN ────────────────► Server
Client ◄─── SYN-ACK ─────────── Server
Client ──── ACK ────────────────► Server
              ↓
         Connection established — data transfer begins
```

### Gotchas & Dev Context
- TCP guarantees delivery — if a packet is lost, TCP retransmits it automatically. This is why it's used for HTTP.
- **UDP** skips the handshake and delivery guarantee — faster but lossy. Used for video streaming, gaming, DNS, and HTTP/3 (QUIC).
- The 3-way handshake adds ~1 round trip of latency before the first byte of data is sent.
- TCP has flow control and congestion control built in — it slows down if the network is congested.
- Each TCP connection uses a port on both ends (`client:54321 → server:443`).

### Production FAQ
**Q: Why do we see `ETIMEDOUT` or `ECONNRESET` errors in our Node.js API?**
A: ETIMEDOUT = TCP connection couldn't be established (server unreachable, firewall). ECONNRESET = connection was forcibly closed mid-transfer (server crash, load balancer timeout).

**Q: Our WebSocket connections drop after 60 seconds of inactivity. Fix?**
A: Send periodic **ping/pong frames** (heartbeat) to keep the TCP connection alive through NAT gateways and load balancers.

---

## 11. WebSockets

### Definition
WebSockets provide a **persistent, two-way communication channel** between client and server over a single TCP connection. Unlike HTTP, either side can send data at any time — no need to poll.

### Real-World Dev Example
```js
// Client-side
const ws = new WebSocket('wss://chat.example.com/room/42');

ws.onopen    = () => ws.send(JSON.stringify({ type: 'join', user: 'Alex' }));
ws.onmessage = (event) => console.log('Received:', event.data);
ws.onclose   = () => console.log('Disconnected');

// Server pushes a message anytime:
// ws.send('{"type":"message","text":"Hello!"}')
```

### ASCII Diagram
```
HTTP (polling):  Client ──request──► Server ──response──► (repeat every N sec)

WebSocket:       Client ◄══════════ persistent socket ══════════► Server
                         (either side sends anytime, no request needed)
```

### Gotchas & Dev Context
- Starts as an HTTP request (`GET /chat`) with `Upgrade: websocket` header — then the protocol switches.
- WebSocket connections are **stateful** — server must track each open connection. This complicates horizontal scaling (use Redis pub/sub to broadcast across instances).
- Use `wss://` (WebSocket Secure) in production, just like HTTPS.
- Not the right tool for simple data that changes occasionally — SSE or polling may be simpler.

### Production FAQ
**Q: WebSockets work locally but drop immediately behind our load balancer. Why?**
A: The load balancer is likely terminating the connection after a default timeout. Enable **sticky sessions** and increase the idle timeout (e.g., 3600s in AWS ALB).

**Q: When should I use WebSockets vs polling?**
A: WebSockets for real-time bidirectional needs (chat, multiplayer, live collaboration). Polling for infrequent updates where simplicity matters more than speed.

---

## 12. Server-Sent Events (SSE)

### Definition
SSE is a lightweight protocol where the **server streams data to the client** over a persistent HTTP connection — one direction only (server → client). Think of it as a live news ticker from the server.

### Real-World Dev Example
```js
// Client — browser EventSource API
const source = new EventSource('/api/live-prices');

source.onmessage = (e) => {
  console.log('Price update:', e.data);
};

source.addEventListener('alert', (e) => {
  console.log('Custom event:', e.data);
});
```

```js
// Server (Node.js/Express)
app.get('/api/live-prices', (req, res) => {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');

  const interval = setInterval(() => {
    res.write(`data: ${JSON.stringify({ price: Math.random() * 100 })}\n\n`);
  }, 1000);

  req.on('close', () => clearInterval(interval));
});
```

### Gotchas & Dev Context
- SSE is **unidirectional** (server → client only). Client can't send data through the same channel — use a separate API call.
- Browser auto-reconnects if the connection drops (built into `EventSource`).
- Max ~6 SSE connections per browser per domain over HTTP/1.1 (not an issue with HTTP/2).
- Much simpler than WebSockets for one-way streaming: notifications, live feeds, progress bars.

### Production FAQ
**Q: SSE vs WebSockets — which should I choose?**
A: SSE for server-push-only scenarios (notifications, live dashboard, progress). WebSockets when the client also needs to send real-time data (chat, gaming).

**Q: SSE connection drops every 30 seconds on our server. Why?**
A: A proxy or load balancer is closing idle connections. Add a heartbeat: `res.write(': ping\n\n')` every 15s (comments keep the connection alive).

---

## 13. REST API

### Definition
REST (Representational State Transfer) is an architectural style for designing APIs using standard HTTP methods and URLs to represent resources. It's the most widely used API pattern on the web.

### Real-World Dev Example
```bash
# RESTful endpoints for a "posts" resource
GET    /posts           # List all posts
GET    /posts/7         # Get post #7
POST   /posts           # Create a new post
PUT    /posts/7         # Replace post #7
PATCH  /posts/7         # Update fields on post #7
DELETE /posts/7         # Delete post #7

# Nested resource
GET    /posts/7/comments  # Comments on post #7
```

### Gotchas & Dev Context
- REST is a *style*, not a strict standard — "RESTful" is often misused. True REST includes statelessness, uniform interface, and client-server separation.
- **Stateless**: each request must contain all info needed — no server-side session memory between requests. Auth tokens handle this.
- Use nouns in URLs, not verbs: `/users/42` ✅, `/getUser?id=42` ❌.
- Versioning matters: breaking changes should increment the version (`/v2/users`).
- JSON is the de facto response format — always set `Content-Type: application/json`.

### Production FAQ
**Q: We need to support bulk delete of users. REST doesn't have a clean way to do this. What should we do?**
A: `DELETE /users` with a JSON body of IDs is one approach; or `POST /users/bulk-delete` (pragmatic, non-purist, widely used).

**Q: Should I return the updated object after a PATCH?**
A: Yes — return the full updated resource in the response body. Clients shouldn't need a second GET to see the result.

---

## 14. GraphQL

### Definition
GraphQL is a query language for APIs where the **client specifies exactly what data it needs** — no more, no less. Developed by Meta, it solves the over-fetching and under-fetching problems of REST.

### Real-World Dev Example
```graphql
# Client sends one query instead of multiple REST calls
query {
  user(id: "42") {
    name
    email
    posts(limit: 3) {
      title
      createdAt
    }
  }
}

# Server returns exactly that shape — nothing extra
```

```bash
# It's always a single POST endpoint
curl -X POST https://api.example.com/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ user(id:\"42\") { name email } }"}'
```

### Gotchas & Dev Context
- Single endpoint (`/graphql`) for all operations — no REST-style URL routing.
- **Over-fetching**: REST might return 30 fields when you need 3. GraphQL returns only what you ask.
- **N+1 problem**: naive GraphQL resolvers make one DB query per item in a list. Use **DataLoader** (batching) to fix.
- Caching is harder than REST — HTTP GET caching doesn't work because it's all POST.
- Mutations (write operations) and Subscriptions (real-time) are also part of the spec.

### Production FAQ
**Q: REST or GraphQL for our new API?**
A: GraphQL shines when clients have diverse data needs (mobile vs web fetching different fields), or when aggregating multiple data sources. REST is simpler for straightforward CRUD APIs.

**Q: How do we handle authorization in GraphQL?**
A: Don't authorize in resolvers field-by-field — use middleware or a dedicated permissions layer (like graphql-shield) to avoid accidentally exposing data.

---

## 15. gRPC

### Definition
gRPC is a high-performance RPC (Remote Procedure Call) framework by Google that uses **Protocol Buffers** (binary format) and HTTP/2. Instead of JSON over REST, you define typed function calls that work across languages.

### Real-World Dev Example
```protobuf
// user.proto — define the contract
service UserService {
  rpc GetUser (UserRequest) returns (UserResponse);
}

message UserRequest  { int32 id = 1; }
message UserResponse { string name = 1; string email = 2; }
```

```python
# Python client calling a Go server — seamlessly
stub = UserServiceStub(channel)
response = stub.GetUser(UserRequest(id=42))
print(response.name)  # "Priya"
```

### Gotchas & Dev Context
- **Binary format** (Protocol Buffers) → 3–10x smaller payload and faster than JSON.
- Requires HTTP/2 — not supported natively in browsers (use **gRPC-Web** proxy for browser clients).
- Strongly typed contract (`.proto` file) = breaking changes are explicit and versioned.
- 4 communication patterns: Unary, Server Streaming, Client Streaming, Bidirectional Streaming.
- Harder to debug than REST — can't just `curl` it. Use tools like `grpcurl` or Postman (gRPC support added).

### Production FAQ
**Q: When should I use gRPC instead of REST?**
A: Internal microservice communication where speed and strong typing matter. REST for public-facing APIs where developer experience and tooling flexibility are priorities.

**Q: Can I use gRPC from a React frontend?**
A: Not directly — browsers don't support HTTP/2 trailers required by gRPC. Use **gRPC-Web** with an Envoy proxy, or expose a REST/GraphQL gateway instead.

---

## 16. API Versioning

### Definition
API versioning lets you introduce **breaking changes** without breaking existing clients. You evolve your API while old consumers continue working on an older version.

### Real-World Dev Example
```bash
# URI versioning — most common
GET /v1/users/42   # Old format: { "full_name": "Alex" }
GET /v2/users/42   # New format: { "first_name": "Alex", "last_name": "Smith" }

# Header versioning
GET /users/42
Accept: application/vnd.example.v2+json

# Query param versioning
GET /users/42?api-version=2024-01-01
```

### Gotchas & Dev Context
- **URI versioning** (`/v1/`, `/v2/`) is the most visible and easiest to test — preferred by most teams.
- Never make breaking changes without bumping the version. Breaking changes include: removing fields, changing field types, changing URL structure.
- Deprecate, don't immediately delete — send `Deprecation` response headers with a sunset date.
- Maintain old versions *long enough* — typically 6–12 months after announcing deprecation.
- Azure and AWS APIs use date-based versioning (`2024-01-01`) — each date represents a stable snapshot.

### Production FAQ
**Q: How long should we support a deprecated API version?**
A: At minimum until all known consumers have migrated. Monitor version usage via logs/metrics. A common policy: 6-month deprecation notice, then hard cutoff.

**Q: Is versioning the URL or header better?**
A: URL versioning for public APIs (easy to test, document, and share). Header versioning for internal APIs where URL cleanliness matters to the team.

---

## 17. Rate Limiting & Throttling

### Definition
**Rate limiting** caps how many requests a client can make in a given window (e.g., 100 req/min). **Throttling** slows requests down when limits are approached rather than hard-blocking them. Both protect servers from abuse and overload.

### Real-World Dev Example
```bash
# Server responds when rate limit is hit
HTTP/1.1 429 Too Many Requests
Retry-After: 30
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1718360400

# Client should back off and retry after 30 seconds
```

```js
// Exponential backoff on 429
async function fetchWithRetry(url, retries = 3) {
  for (let i = 0; i < retries; i++) {
    const res = await fetch(url);
    if (res.status !== 429) return res;
    await new Promise(r => setTimeout(r, 2 ** i * 1000)); // 1s, 2s, 4s
  }
}
```

### Gotchas & Dev Context
- Common algorithms: **Token Bucket** (bursty allowed), **Leaky Bucket** (smooth flow), **Fixed Window**, **Sliding Window**.
- Scope your limits: by API key, by user, by IP, by endpoint — different limits for different needs.
- Always expose `X-RateLimit-*` headers so clients can self-throttle before hitting the wall.
- Use Redis for distributed rate limiting across multiple server instances.

### Production FAQ
**Q: Our API gateway is rate limiting our own internal services. How do we fix it?**
A: Whitelist internal IPs or use a separate API key with higher limits for internal callers. Separate external and internal rate limit tiers.

**Q: A user is hammering our expensive `/search` endpoint. How do we limit just that?**
A: Apply endpoint-specific limits (e.g., 10 req/min for `/search`, 1000 req/min for `/health`) in your gateway or middleware.

---

## 18. Idempotency

### Definition
An operation is **idempotent** if performing it multiple times produces the same result as performing it once. Critical for safe retries in unreliable networks.

### Real-World Dev Example
```bash
# Idempotent — deleting twice has same result as deleting once
DELETE /orders/99  → 200 OK (order deleted)
DELETE /orders/99  → 404 Not Found (already gone — same end state: it's gone)

# NOT idempotent by default — POST creates a duplicate
POST /orders  → 201 Created (order #100)
POST /orders  → 201 Created (order #101) ← duplicate!

# Fix: use an Idempotency-Key header
POST /orders
Idempotency-Key: client-uuid-abc123
→ 201 Created (order #100)

POST /orders
Idempotency-Key: client-uuid-abc123  ← same key
→ 200 OK (returns cached response — no duplicate created)
```

### Gotchas & Dev Context
- Stripe, Braintree, and most payment APIs require `Idempotency-Key` — implement it for any financial operation.
- Store idempotency keys in Redis with a TTL (e.g., 24 hours) — map key → response.
- GET, PUT, DELETE are naturally idempotent. POST and PATCH are not.
- Network retries without idempotency keys can cause duplicate charges, duplicate orders, etc.

### Production FAQ
**Q: Our payment service retried a timed-out request and the user was charged twice. How do we prevent this?**
A: Implement idempotency keys on your payment endpoint. Generate a UUID on the client before the first attempt and resend the same key on retries.

**Q: How long should we store idempotency keys?**
A: 24 hours is the Stripe standard. Match it to your retry window — there's no point keeping a key past when retries can reasonably happen.

---

## 19. Webhooks

### Definition
A webhook is an **HTTP callback** — instead of your app asking a service "did anything happen?" (polling), the service calls *your* endpoint when an event occurs. It's the web's push notification system.

### ASCII Diagram
```
Polling (bad for events):
Your Server ──GET /status?──► Stripe  (every 5 sec, mostly wasted)

Webhook (event-driven):
Stripe ──POST /webhook──► Your Server  (only when payment succeeds)
```

### Real-World Dev Example
```js
// Your Express endpoint that Stripe calls
app.post('/webhooks/stripe', express.raw({ type: 'application/json' }), (req, res) => {
  const sig = req.headers['stripe-signature'];

  // Always verify the signature — reject unsigned requests
  const event = stripe.webhooks.constructEvent(req.body, sig, process.env.STRIPE_SECRET);

  if (event.type === 'payment_intent.succeeded') {
    fulfillOrder(event.data.object.metadata.orderId);
  }

  res.json({ received: true }); // Respond quickly — do heavy work async
});
```

### Gotchas & Dev Context
- **Always verify webhook signatures** — anyone can POST to your endpoint otherwise.
- **Respond with 200 quickly** — providers retry if no response in ~5s. Queue the work and process async.
- Webhooks can **deliver events out of order** or **deliver duplicates** — design your handler to be idempotent.
- Use a tool like **ngrok** or **Stripe CLI** to test webhooks locally (your localhost isn't reachable by external services).

### Production FAQ
**Q: Stripe retried a webhook 5 times and our order was fulfilled 5 times. How do we fix this?**
A: Store the event ID and check for duplicates before processing. If already processed, return 200 immediately without side effects.

**Q: Our webhook handler takes 10 seconds to process. Stripe marks it as failed. Fix?**
A: Respond 200 immediately, then push the event to a job queue (Bull, SQS, etc.) and process asynchronously in a worker.

---

## 20. CORS (Cross-Origin Resource Sharing)

### Definition
CORS is a browser security mechanism that blocks JavaScript on one origin (e.g., `app.com`) from reading responses from a different origin (e.g., `api.com`) — unless the server explicitly permits it.

### ASCII Diagram
```
Same origin ✅ (browser allows):
app.com  ──fetch──►  app.com/api

Cross origin ❌ (browser blocks by default):
app.com  ──fetch──►  api.otherdomain.com
                          │
                    Server must send:
                    Access-Control-Allow-Origin: https://app.com
```

### Real-World Dev Example
```js
// Express — add CORS headers
const cors = require('cors');

app.use(cors({
  origin: ['https://app.com', 'https://admin.app.com'],
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  credentials: true,  // needed if sending cookies/auth headers
}));
```

```bash
# The dreaded browser error:
# "Access to fetch at 'https://api.com/data' from origin 'https://app.com'
#  has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header"
```

### Gotchas & Dev Context
- CORS is enforced **by the browser** — `curl` and Postman are never blocked by CORS. If your curl works but the browser doesn't, it's CORS.
- **Preflight request**: browsers send an `OPTIONS` request before any non-simple request (POST with JSON, custom headers). Your server must handle `OPTIONS` and respond with CORS headers.
- `Access-Control-Allow-Origin: *` allows all origins but **cannot be combined with `credentials: true`** — you must specify exact origins for authenticated requests.
- CORS misconfiguration is a security risk: don't echo back whatever `Origin` header you receive — whitelist explicitly.

### Production FAQ
**Q: My API works in Postman but not in the browser. Is it a backend bug?**
A: No — CORS is a browser-only restriction. Add the correct `Access-Control-Allow-Origin` header on your server for your frontend's origin.

**Q: We set `Access-Control-Allow-Origin: *` but cookies aren't being sent. Why?**
A: Wildcard `*` is incompatible with `credentials: true`. Switch to a specific origin: `Access-Control-Allow-Origin: https://app.com` and also set `Access-Control-Allow-Credentials: true`.

---

*End of Batch 1 — Internet & Web Fundamentals*

> **Next up → Batch 2:** HTML & CSS Fundamentals — structure, styling, and the box model.
