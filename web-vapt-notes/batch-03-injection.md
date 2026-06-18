# Batch 3 — Injection Attacks & Patching
> How attackers trick applications into executing malicious commands and how to stop them.

## 1. SQL Injection (SQLi)
### Definition
Tricking a database into executing malicious SQL code by abusing unsanitized user input. Types include **Error** (database errors leak data), **Blind** (guessing data by asking true/false questions), and **Time-based** (measuring database delay to extract data).

### Real-World Dev/Testing Example
An attacker types `' OR '1'='1` into a login password field. The backend query becomes `SELECT * FROM users WHERE password = '' OR '1'='1'`, which always evaluates to true, logging them in without a password.

### ASCII Diagram
```text
[Input: '; DROP TABLE users--] 
      |
      v
[Query: SELECT * FROM data WHERE id='; DROP TABLE users--] 
      |
      v
(╯°□°)╯︵ ┻━┻ (Database Deleted)
```

### Gotchas & Dev Context
*   **Time-based SQLi** is slow but deadly—attackers extract databases one character at a time by making the database `sleep(5)` if a guess is correct.
*   Frameworks hide SQL, but raw queries often bypass these protections.

### Production FAQ
*   **Q: Will escaping quotes (`\'`) stop SQLi?**
    *   **A:** Not reliably. Use Parameterized Queries (Prepared Statements) instead.

---

## 2. NoSQL Injection
### Definition
Exploiting NoSQL databases (like MongoDB or CouchDB) by injecting malicious logic or structural operators (like JSON objects) instead of traditional SQL syntax.

### Real-World Dev/Testing Example
An application expects a JSON login: `{"username": "admin", "password": "123"}`. The attacker intercepts the request and sends `{"username": "admin", "password": {"$ne": null}}`. Because `$ne` (not equal) is a MongoDB operator, the query matches a valid password without knowing it.

### Gotchas & Dev Context
*   Developers often falsely assume NoSQL means "no SQL injection".
*   Common in JavaScript/Node.js stacks where request JSON is directly passed to the database driver.

### Production FAQ
*   **Q: How do we patch NoSQL injections?**
    *   **A:** Enforce strict schema validation (e.g., using Mongoose in Node.js) and reject payloads where strings are unexpectedly replaced by objects/arrays.

---

## 3. Command Injection (OS Injection)
### Definition
Executing arbitrary system-level commands on the host server because an application passes unsafe user input directly to a system shell.

### Real-World Dev/Testing Example
A network diagnostic app allows users to ping an IP. An attacker inputs `8.8.8.8; cat /etc/passwd`. The server runs `ping -c 4 8.8.8.8; cat /etc/passwd`, exposing sensitive system user data.

### Gotchas & Dev Context
*   Often leads to instant **Remote Code Execution (RCE)** and full server compromise.
*   Functions like `exec()`, `system()`, or `os.popen()` are major red flags in code reviews.

### Production FAQ
*   **Q: How can we safely run OS commands?**
    *   **A:** Never pass user input to a shell. Use language-native APIs (e.g., Python's `ipaddress` module to ping, or `os.listdir()` instead of `ls`). If you must execute external binaries, pass arguments as an array, not a single concatenated string.

---

## 4. LDAP Injection
### Definition
Manipulating LDAP (Lightweight Directory Access Protocol) statements using malicious characters to alter active directory queries, allowing attackers to bypass authentication or extract corporate directory information.

### Real-World Dev/Testing Example
A company portal queries LDAP for a username: `(&(USER=input)(PASSWORD=input))`. An attacker enters `admin)(&)`. The query becomes `(&(USER=admin)(&))(PASSWORD=input))`, short-circuiting the logic to log in as admin without a password.

### Gotchas & Dev Context
*   Extremely common in internal corporate web apps that integrate with Active Directory (AD).
*   LDAP uses different control characters than SQL, primarily `*`, `(`, `)`, `\`, and `&`.

### Production FAQ
*   **Q: What is the patching strategy for LDAP?**
    *   **A:** Employ LDAP-specific escaping functions. Standard SQL sanitization will not stop an LDAP injection.

---

## 5. XPATH Injection
### Definition
Exploiting applications that use user input to construct XPath queries for parsing XML data. This allows attackers to navigate the XML document structure and read sensitive nodes.

### Real-World Dev/Testing Example
An app uses XML for a user database. The XPath query is `//users/user[username/text()='input']`. The attacker sends `' or '1'='1`, changing the query to `//users/user[username/text()='' or '1'='1']`, dumping the entire XML file.

### Gotchas & Dev Context
*   A legacy vulnerability. As REST/JSON replaced SOAP/XML, XPath injection became rarer, but it still haunts old enterprise codebases.
*   XPath 1.0 lacks built-in parameterized queries, making it inherently risky.

### Production FAQ
*   **Q: How do we fix legacy XPath vulnerabilities?**
    *   **A:** Use precompiled XPath variables if your library supports them (like `XPathVariableResolver` in Java), or strictly validate input against an allow-list before concatenation.

---

## 6. Server-Side Template Injection (SSTI)
### Definition
Injecting malicious template directives into a web framework's template engine (like Jinja2, Twig, or FreeMarker) that execute arbitrary code on the server.

### Real-World Dev/Testing Example
An email marketing app allows custom greetings: `Hello {{ name }}`. An attacker sets their name to `{{ 7 * 7 }}`. If the email reads `Hello 49`, the server evaluated the math. The attacker then escalates to `{{ system('whoami') }}` to compromise the server.

### Gotchas & Dev Context
*   Often mistaken for Cross-Site Scripting (XSS). XSS executes in the *browser* (client-side); SSTI executes on the *server* (RCE).
*   Occurs when developers pass user input as the *template itself*, rather than as a *variable* to a static template.

### Production FAQ
*   **Q: How do we prevent SSTI?**
    *   **A:** Use "logic-less" templates (like Mustache). If using Jinja/Twig, strictly pass input via context variables, never concatenate strings into the template file.

---

## 7. Parameterized Queries / Prepared Statements (Patching)
### Definition
A core defense against SQLi where the database compiles the SQL query structure first, and treats user inputs strictly as literal data, completely neutralizing malicious code.

### Real-World Dev/Testing Example
Instead of `db.query(f"SELECT * FROM logs WHERE id = {user_id}")`, a developer writes `db.query("SELECT * FROM logs WHERE id = ?", (user_id,))`.

### ASCII Diagram
```text
[SQL Engine]
1. Compile: SELECT * FROM users WHERE name = [BLANK]
2. Insert:  "'; DROP TABLE users--"
3. Execute: Safely searches for a user literally named "'; DROP TABLE users--"
```

### Gotchas & Dev Context
*   They only protect *values*. You cannot parameterize table names or column names (e.g., `SELECT * FROM ?`).
*   Missing just one parameterized query in a massive app leaves a backdoor open.

### Production FAQ
*   **Q: Do I still need input validation if I use parameterized queries?**
    *   **A:** Yes! Parameterization stops DB deletion, but won't stop a user from setting their age to `-999` or putting an XSS payload in their bio. Defense-in-depth is key.

---

## 8. Input Validation / Sanitization (Patching)
### Definition
**Validation** ensures incoming data strictly matches expected formats (e.g., an email looks like an email). **Sanitization** cleans or strips dangerous characters from the input before processing.

### Real-World Dev/Testing Example
A web form expects a 5-digit zip code. Validation rejects `12345; rm -rf /`. Sanitization strips HTML tags `<script>` from a blog comment before saving it to the database.

### Gotchas & Dev Context
*   **Allow-listing** (only permitting known-good characters) is infinitely safer than **Block-listing** (trying to guess and ban all bad characters).
*   Validation should happen on the *server*. Client-side (HTML/JS) validation is just for UX and easily bypassed by an attacker.

### Production FAQ
*   **Q: Is sanitization enough to prevent injections?**
    *   **A:** No. Sanitization is a fallback. It is highly prone to bypasses (e.g., blocking `script` but forgetting `img onerror`). Always combine it with contextual escaping and parameterized queries.

---

## 9. ORM (Object-Relational Mapping) Security
### Definition
Using libraries (like SQLAlchemy, Django ORM, or Prisma) to interact with databases using application objects rather than writing raw SQL. ORMs natively use parameterized queries under the hood.

### Real-World Dev/Testing Example
Using `User.objects.filter(username=input)` instead of `SELECT * FROM User WHERE username = input`. The ORM handles the secure translation to SQL automatically.

### Gotchas & Dev Context
*   ORMs are excellent for security, but developers frequently break this protection by using ORM "escape hatches" like `.raw()`, `RawSQL()`, or passing unsanitized input to `.order_by()`.
*   Complex queries sometimes push developers back to raw SQL, re-introducing risks.

### Production FAQ
*   **Q: Can an app using an ORM still get SQL Injection?**
    *   **A:** Absolutely. If a developer concatenates strings into an ORM's raw execution method (e.g., `db.session.execute(f"SELECT * FROM {table_name}")`), the app is instantly vulnerable.
