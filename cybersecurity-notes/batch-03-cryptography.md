# Batch 3 — Cryptography & Data Security
> The mathematical foundation of modern digital security.

## 1. Symmetric vs Asymmetric Encryption

### Definition
Symmetric encryption uses a single shared key to both lock and unlock data. Asymmetric encryption uses a mathematically linked pair of keys: a public key to lock data, and a private key to unlock it.

### Real-World Dev/IT Example
Symmetric is like locking a hard drive with a password (AES). Asymmetric is like a mailbox: anyone can drop a message in the public slot (public key), but only the owner has the key to open the box (private key).

### ASCII Diagram
```text
Symmetric:   [Plaintext] -> (Shared Key) -> [Ciphertext] -> (Shared Key) -> [Plaintext]
Asymmetric:  [Plaintext] -> (Public Key) -> [Ciphertext] -> (Private Key) -> [Plaintext]
```

### Gotchas & Dev Context
*   **Speed:** Symmetric is significantly faster and uses less CPU, making it ideal for bulk data.
*   **The Key Distribution Problem:** Symmetric encryption requires you to securely share the secret key beforehand. Asymmetric solves this, as the public key can be shared openly.

### Production FAQ
*   **Q: Why not use asymmetric encryption for everything?**
    A: It is computationally heavy and slow. Large files would take forever to encrypt.
*   **Q: How do modern systems combine them?**
    A: Through hybrid encryption. We use asymmetric encryption just to securely exchange a symmetric key, then use the fast symmetric key to encrypt the actual data.

---

## 2. RSA Algorithm

### Definition
RSA is a widely used asymmetric encryption algorithm based on the mathematical difficulty of factoring the product of two very large prime numbers.

### Real-World Dev/IT Example
Used heavily in secure web browsing to exchange AES keys at the start of an HTTPS connection, or by developers connecting to GitHub via SSH (`id_rsa`).

### Gotchas & Dev Context
*   **Key Size:** 1024-bit RSA is considered broken. 2048-bit is the current minimum standard, while 4096-bit provides high security at the cost of performance.
*   **Quantum Threat:** RSA is theoretically vulnerable to future quantum computers (Shor's Algorithm). Post-quantum cryptography is being developed to replace it.
*   **Don't roll your own:** Never try to implement the math yourself; use established libraries like OpenSSL.

### Production FAQ
*   **Q: Should I encrypt user files directly with RSA?**
    A: No. RSA can only encrypt data smaller than its key size. Encrypt the file with a symmetric key, and encrypt the symmetric key with RSA.
*   **Q: Is 4096-bit RSA twice as secure as 2048-bit?**
    A: It's significantly more secure against brute force, but takes roughly 4-8 times longer to generate and compute.

---

## 3. AES (Advanced Encryption Standard)

### Definition
AES is the global standard algorithm for symmetric encryption, adopted by the US government. It processes data in fixed blocks of 128 bits using keys of 128, 192, or 256 bits.

### Real-World Dev/IT Example
Used by BitLocker or FileVault for full-disk encryption, and by messaging apps like WhatsApp to protect data in transit.

### Gotchas & Dev Context
*   **Modes of Operation:** Never use AES in ECB mode (it leaves visual patterns in the ciphertext). Always use authenticated modes like GCM (Galois/Counter Mode) or CBC with a randomized Initialization Vector (IV).
*   **Key Rotation:** Even strong AES keys should be rotated regularly in production to limit the blast radius of a potential key leak.

### Production FAQ
*   **Q: Is AES-256 unbreakable?**
    A: Against current classical computing brute-force attacks, yes. It would take billions of years to crack. Most AES "hacks" actually involve stealing the key, not breaking the math.
*   **Q: What is an Initialization Vector (IV)?**
    A: A random sequence injected into the encryption process so that encrypting the exact same plaintext twice yields completely different ciphertexts.

---

## 4. Public Key Infrastructure (PKI)

### Definition
PKI is the framework of policies, servers, and cryptographic algorithms that manages digital certificates and public-key encryption, establishing a chain of digital trust.

### Real-World Dev/IT Example
The ecosystem that allows your browser to trust that `github.com` is legitimately GitHub, rather than a man-in-the-middle attacker. 

### ASCII Diagram
```text
[Root CA] ---> (Signs) ---> [Intermediate CA] ---> (Signs) ---> [Server Certificate]
```

### Gotchas & Dev Context
*   **Root of Trust:** If a Root CA is compromised, every certificate it issued becomes untrustworthy.
*   **Revocation is Hard:** Checking if a certificate was revoked (via CRLs or OCSP) often fails open or causes latency, making real-time revocation a notorious industry challenge.

### Production FAQ
*   **Q: What is a Certificate Authority (CA)?**
    A: A trusted third-party organization (like Let's Encrypt or DigiCert) that validates identities and issues digital certificates.
*   **Q: What is self-signing?**
    A: Generating a certificate without a CA. It's fine for local development but will trigger massive red warning screens in browsers for production users.

---

## 5. Digital Signatures

### Definition
A cryptographic mechanism to verify the authenticity and integrity of a digital message. It is effectively asymmetric encryption in reverse: encrypting a hash with a private key.

### Real-World Dev/IT Example
Apple requiring iOS developers to "sign" their `.ipa` app packages. If the app is modified by malware after being signed, the signature breaks, and iOS refuses to install it.

### ASCII Diagram
```text
[Document] -> Hash -> (Private Key) -> [Signature]
```

### Gotchas & Dev Context
*   **No Secrecy:** Digital signatures do *not* encrypt the document's contents. Anyone can read it; they just can't alter it without detection.
*   **Key Protection:** If a developer's private signing key is stolen, attackers can sign malware that looks exactly like legitimate official software.

### Production FAQ
*   **Q: Can a digital signature be forged?**
    A: Not without the private key or a breakthrough in breaking the underlying hash algorithm (like SHA-256).
*   **Q: What is non-repudiation?**
    A: The concept that a sender cannot deny signing a message, because mathematically, only their unique private key could have produced that exact signature.

---

## 6. SSL / TLS Handshake

### Definition
The behind-the-scenes negotiation process where a client and server greet each other, agree on encryption algorithms, verify identities, and securely exchange session keys.

### Real-World Dev/IT Example
The invisible ~100-millisecond delay that occurs before the padlock icon appears when you navigate to your bank's login page.

### Gotchas & Dev Context
*   **Terminology:** SSL is dead and fully deprecated due to vulnerabilities. We use TLS (Transport Layer Security) 1.2 or 1.3 now, though the IT world still lazily calls them "SSL certificates."
*   **Performance Hit:** Handshakes require network round-trips. TLS 1.3 drastically reduced this to just 1-RTT (Round Trip Time), significantly speeding up secure web APIs.

### Production FAQ
*   **Q: Why does my initial API call take longer than subsequent ones?**
    A: The first call has to perform the DNS lookup, TCP handshake, and the TLS handshake. Subsequent calls reuse the established secure connection.
*   **Q: What is Mutual TLS (mTLS)?**
    A: An advanced setup where the server validates the client's certificate, AND the client validates the server's. Very common in Zero Trust microservice architectures.

---

## 7. Digital Certificates (X.509)

### Definition
An electronic document used to prove ownership of a public key. It functions as a digital passport, stamped and verified by a Certificate Authority (CA).

### Real-World Dev/IT Example
The `.pem` or `.crt` files you attach to an Nginx ingress controller or AWS Load Balancer to enable HTTPS traffic.

### Gotchas & Dev Context
*   **Expirations:** Certificates have strict expiration dates. Forgetting to renew them is one of the most common causes of massive production outages.
*   **Automation:** Modern infra relies on protocols like ACME (used by Let's Encrypt) to automatically rotate and renew certificates every 90 days to avoid human error.

### Production FAQ
*   **Q: What exactly is inside an X.509 certificate?**
    A: The owner's public key, the owner's identity (domain name), the issuer's identity, expiration dates, and the CA's digital signature.
*   **Q: What is a wildcard certificate?**
    A: A certificate valid for a domain and all its subdomains (e.g., `*.example.com` covers `api.example.com` and `app.example.com`).

---

## 8. Salting & Peppering

### Definition
A "salt" is random data added to a password before hashing it to ensure identical passwords have completely different hashes. A "pepper" is a global secret cryptographic key added to all hashes.

### Real-World Dev/IT Example
When storing user passwords in your Postgres database. If two users both use the password "letmein123", random salts ensure their database rows look entirely different.

### ASCII Diagram
```text
[Password] + [Salt (Random)] + [Pepper (Secret)] -> Hash Function -> [Stored Hash]
```

### Gotchas & Dev Context
*   **Salts are not secret:** The salt is stored in plaintext right next to the hash in the database. Its job is uniqueness, not secrecy.
*   **Peppers ARE secret:** The pepper is never stored in the database. It lives in a secure configuration or Key Management System (KMS).
*   **Right Tooling:** Never use fast algorithms like MD5 or SHA-256 for passwords. Use slow, memory-hard algorithms like `bcrypt` or `Argon2`.

### Production FAQ
*   **Q: Do salts protect against weak passwords like "password"?**
    A: No. A targeted attack on that specific user will still guess it quickly. Salts protect the *database as a whole* against pre-computed "rainbow table" mass-cracking.

---

## 9. Key Management (KMS)

### Definition
A centralized, highly secure system specifically designed to generate, store, distribute, and rotate cryptographic keys.

### Real-World Dev/IT Example
Using AWS KMS or HashiCorp Vault to store your database master password or encryption keys, rather than hardcoding them in your `config.yml`.

### Gotchas & Dev Context
*   **The Secret Zero Problem:** How does your app securely get the credentials needed to log into the KMS to get the rest of the secrets? (Usually solved via cloud IAM roles tied to the VM/Container).
*   **Envelope Encryption:** Instead of sending massive files to KMS to be encrypted (slow), KMS generates a local "Data Key" to encrypt the file, and KMS only encrypts the Data Key.

### Production FAQ
*   **Q: Why not just store encryption keys in Environment Variables?**
    A: Env vars frequently leak in crash logs, debugging screens, and CI/CD pipelines. A KMS provides strict audit logs and access controls.
*   **Q: What happens if I delete my master KMS key?**
    A: Any data encrypted by that key becomes permanently irrecoverable mathematically. It is gone forever.

---

## 10. Steganography

### Definition
The practice of hiding secret data within an ordinary, non-secret file or message to avoid drawing suspicion to the fact that communication is even occurring.

### Real-World Dev/IT Example
A malicious actor hiding a tiny executable script payload inside the least significant color pixels of a high-resolution `.jpg` image of a cat uploaded to an imageboard.

### Gotchas & Dev Context
*   **Obscurity, Not Security:** Steganography hides the *existence* of the message, but rarely encrypts it. It should always be combined with cryptography.
*   **Fragility:** Any modification to the carrier file—such as a social media site automatically compressing an uploaded image—usually destroys the hidden data entirely.

### Production FAQ
*   **Q: How is this different from cryptography?**
    A: Cryptography makes a message unreadable. Steganography makes the message invisible.
*   **Q: Can antivirus catch steganography?**
    A: It's extremely difficult. Analyzing every pixel of every image in a network stream is too computationally expensive for real-time firewalls.

---

## 11. Homomorphic Encryption

### Definition
A cutting-edge cryptographic method that allows mathematical computations to be performed directly on encrypted data, yielding an encrypted result without ever needing to decrypt the payload.

### Real-World Dev/IT Example
A hospital sending encrypted patient records to a cloud AI. The AI runs machine learning algorithms on the ciphertext blindly and returns encrypted predictions. Only the hospital can decrypt the result.

### ASCII Diagram
```text
[Encrypted Data] -> (Cloud processing on ciphertext) -> [Encrypted Result] -> (Decrypted locally)
```

### Gotchas & Dev Context
*   **Performance:** Fully Homomorphic Encryption (FHE) is currently thousands of times slower and requires vastly more memory than plaintext operations. 
*   **Bleeding Edge:** Not yet standard for high-volume web traffic. Libraries like Microsoft SEAL are pushing the boundaries, but it remains a specialized tool.

### Production FAQ
*   **Q: Why is this considered the "Holy Grail" of cryptography?**
    A: It enables true Zero-Trust cloud computing. You can utilize third-party cloud processors without ever exposing your sensitive raw data to them.
*   **Q: Is it used in production today?**
    A: Rarely, but its adoption is growing in highly regulated sectors (finance, healthcare) for secure multi-party computation and privacy-preserving machine learning.
