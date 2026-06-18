# Batch 3 — Cryptography & Keys
> The mathematical security layer underneath every blockchain transaction.

Blockchain security is not magic — it's applied math. Every wallet address, every signed transaction, every zero-knowledge proof rests on the concepts below. This batch gives you the practical mental models you need to work with cryptographic primitives confidently.

---

## 1. Public Key Cryptography

**One-line definition:** A system where two mathematically linked keys (one public, one private) replace the need for a shared secret password.

### Real-World Dev Example
When you send ETH, you don't send a password. You prove ownership with a private key signature; anyone can verify it using only your public key.

```
Alice's wallet → signs tx with private key → broadcasts tx
Network nodes  → verify sig with public key → accept tx
```

### ASCII Diagram
```
  [Private Key] ──────────────► [Sign Data]
                                      │
  [Public Key]  ◄── derived ──  verify│ ── ► Valid / Invalid
```

### Gotchas & Dev Context
- The private → public derivation is **one-way** (trapdoor function); you can never reverse it.
- "Asymmetric" = two different keys. "Symmetric" = same key for both sides (e.g., AES).
- Ethereum uses **secp256k1** curve; SSH typically uses **RSA** or **Ed25519** — not the same!
- Never confuse authentication (proving identity) with encryption (hiding data). Blockchain mostly uses the former.

### Production FAQ
**Q: Can two people accidentally generate the same key pair?**  
A: Theoretically yes, practically impossible. The key space is 2²⁵⁶ ≈ 10⁷⁷ — more than atoms in the observable universe.

**Q: Is public key cryptography used to encrypt blockchain transactions?**  
A: No. Transactions are **signed** (not encrypted) — they're public by design. Encryption is a separate use case (e.g., private messaging protocols like ECIES).

---

## 2. Private Key

**One-line definition:** A secret 256-bit number that proves you own an address and authorizes transactions — your blockchain master password.

### Real-World Dev Example
```python
from eth_account import Account
import secrets

# Generate a random private key
private_key = "0x" + secrets.token_hex(32)
account = Account.from_key(private_key)
print(account.address)  # Your Ethereum address
```

### ASCII Diagram
```
  Private Key (256-bit random number)
  e.g.: 0x4c0883a69102...

        │
        ▼
  [secp256k1 EC math]
        │
        ▼
  Public Key  ──► Address (last 20 bytes of keccak256 hash)
```

### Gotchas & Dev Context
- **Losing your private key = losing your funds permanently.** No recovery mechanism exists on-chain.
- Never store in plaintext, `.env` files committed to git, or clipboard history.
- A private key is just a number in range `[1, n-1]` where `n` is the curve order (~1.16 × 10⁷⁷).
- Hardware wallets keep the private key inside a secure chip — it never touches your OS.
- `ethers.js`: `new ethers.Wallet(privateKey)` — wraps a raw key in a signer object.

### Production FAQ
**Q: Can I change my private key without changing my address?**  
A: No. The address is derived from the public key which is derived from the private key. Change one, you change all.

**Q: Why is 256 bits the standard length?**  
A: It matches the security level of secp256k1 and provides ~128-bit post-collision resistance — overkill by current compute, but future-aware.

---

## 3. Public Key

**One-line definition:** A shareable value mathematically derived from your private key — used to verify your signatures and derive your wallet address.

### Real-World Dev Example
```js
const { ethers } = require("ethers");
const wallet = new ethers.Wallet(privateKey);

console.log(wallet.publicKey);  // 0x04 + 128 hex chars (uncompressed)
console.log(wallet.address);    // derived from publicKey via keccak256
```

### ASCII Diagram
```
  Private Key (32 bytes)
        │
        │  EC Point Multiplication: pubKey = privKey × G
        ▼
  Public Key (64 bytes uncompressed / 33 bytes compressed)
        │
        │  keccak256(pubKey) → last 20 bytes
        ▼
  Ethereum Address (20 bytes / 40 hex chars)
```

### Gotchas & Dev Context
- Ethereum addresses are NOT public keys — they're a **hash of** the public key.
- Uncompressed public key: `0x04 + x + y` (65 bytes). Compressed: `0x02/03 + x` (33 bytes).
- Your public key is revealed the **first time you send** a transaction (not when you receive).
- In EIP-712, `ecrecover()` is used to extract the public key/address from a signature.
- You can share your public key freely — it cannot be used to reverse-engineer your private key.

### Production FAQ
**Q: Is my Ethereum address the same as my public key?**  
A: No. The address is `"0x" + last_20_bytes(keccak256(publicKey))`. They're related but not equal.

**Q: Does Solana use the same public key format?**  
A: No. Solana uses **Ed25519** — a different curve. Public keys are 32 bytes and directly serve as the wallet address (no extra hashing step).

---

## 4. Key Pair

**One-line definition:** The inseparable duo — a private key and its mathematically derived public key — that together enable signing and verification.

### Real-World Dev Example
```js
// ethers.js — generate a fresh key pair
const wallet = ethers.Wallet.createRandom();
console.log("Private:", wallet.privateKey);
console.log("Public:",  wallet.publicKey);
console.log("Address:", wallet.address);
```

### ASCII Diagram
```
  ┌─────────────────────────────────────────┐
  │              KEY PAIR                   │
  │                                         │
  │  Private Key ──EC math──► Public Key   │
  │  (keep secret)            (share freely)│
  │                                         │
  │  Signs data               Verifies sig  │
  │  Derives address          IS the address│
  └─────────────────────────────────────────┘
```

### Gotchas & Dev Context
- You generate the **private key first** (random); public key is computed — never the other way.
- Key pairs in HD wallets (BIP-32) are derived deterministically from a seed — same seed = same infinite pairs.
- "Wallet" is a colloquial term; technically a wallet manages one or many key pairs.
- In multi-sig setups, multiple key pairs collectively control a single on-chain address (smart contract wallet).

### Production FAQ
**Q: Should I generate key pairs offline?**  
A: Yes, for high-value wallets. Air-gapped machines or hardware wallets prevent key exfiltration during generation.

**Q: Can I reuse a key pair across Ethereum and Bitcoin?**  
A: Both use secp256k1, so yes technically — but never do this. Cross-chain reuse creates correlated risk and complicates key management.

---

## 5. Digital Signature (ECDSA, EdDSA)

**One-line definition:** A cryptographic proof attached to data proving it was created by the holder of a specific private key — the blockchain equivalent of a handwritten signature, but unforgeable.

### Real-World Dev Example
```js
// Sign a message with ethers.js (ECDSA / secp256k1)
const wallet = new ethers.Wallet(privateKey);
const sig = await wallet.signMessage("authorize withdrawal");
// sig = 0x... (65-byte: r + s + v)

// Verify:
const signer = ethers.verifyMessage("authorize withdrawal", sig);
// signer === wallet.address ✓
```

### ASCII Diagram
```
  [Message] + [Private Key] ──ECDSA──► [Signature: r, s, v]
                                                │
  [Message] + [Signature]  + [Public Key] ──►  Valid?
                                                Yes/No
```

### Gotchas & Dev Context
- **ECDSA** (secp256k1): Used by Bitcoin & Ethereum. Requires a random nonce `k` per signature — reusing `k` leaks your private key (the PS3 hack!).
- **EdDSA** (Ed25519): Used by Solana, Cardano, Polkadot. Deterministic — no random nonce, so no nonce-reuse vulnerability.
- Ethereum's `v` component (27 or 28) enables public key recovery via `ecrecover`.
- `eth_sign` vs `personal_sign` vs `eth_signTypedData` — use EIP-712 (`signTypedData`) in production to prevent phishing.
- Signatures do NOT encrypt the message — the message stays visible.

### Production FAQ
**Q: What happens if two transactions have the same signature?**  
A: Impossible by design — signatures include a nonce (account transaction count), preventing replay attacks.

**Q: Why does Ethereum include a `v` value in signatures?**  
A: To allow full public key recovery from the signature alone, since EC math gives two possible public keys for any `(r, s)` pair. `v` disambiguates.

---

## 6. Elliptic Curve Cryptography (ECC)

**One-line definition:** A branch of public-key cryptography based on the algebraic structure of elliptic curves over finite fields — giving strong security with much smaller key sizes than RSA.

### Real-World Dev Example
Ethereum uses the **secp256k1** curve: `y² = x³ + 7 (mod p)` where `p` is a large prime. Your private key is a scalar; your public key is a point on this curve.

### ASCII Diagram
```
  Elliptic Curve over real numbers (conceptual):

       *   *
     *       *
    *         *
    *          
     *       *
       *   *

  G = generator point (fixed, public)
  Public Key = Private Key × G  (scalar multiplication)
  Reverse (finding private key from public key) = ECDLP — computationally infeasible
```

### Gotchas & Dev Context
- **ECDLP** = Elliptic Curve Discrete Logarithm Problem — the hard math that keeps your key safe.
- secp256k1 was chosen by Satoshi; **not** a NIST curve (less trust concerns about backdoors).
- A 256-bit ECC key ≈ 3072-bit RSA key in security strength.
- Quantum computers (Shor's algorithm) could break ECC — post-quantum migration is an active area.
- Libraries: `noble-curves` (JS), `py_ecc` (Python), `k256` crate (Rust).

### Production FAQ
**Q: Why use ECC over RSA for blockchains?**  
A: Smaller keys (32 vs 384 bytes), faster signatures, and lower on-chain storage cost — critical when every byte costs gas.

**Q: Is secp256k1 the only curve used in Web3?**  
A: No. Ed25519 (Solana, near), BN254/BLS12-381 (ZK proofs, BLS signatures) are also common, each optimized for different use cases.

---

## 7. Seed Phrase / Mnemonic (BIP-39)

**One-line definition:** A human-readable backup of your wallet — 12 or 24 everyday words that encode the master secret from which all your keys are derived.

### Real-World Dev Example
```
abandon abandon abandon abandon abandon abandon
abandon abandon abandon abandon abandon about
```
(The above is the BIP-39 test vector — never use it for real funds!)

### ASCII Diagram
```
  [128-256 bits entropy]
          │
          ▼
  [+checksum bits]
          │
          ▼
  [split into 11-bit groups → map to BIP-39 wordlist]
          │
          ▼
  12/24 mnemonic words
          │
     PBKDF2-HMAC-SHA512 (2048 rounds + optional passphrase)
          │
          ▼
  512-bit Seed → HD Wallet Root Key
```

### Gotchas & Dev Context
- The wordlist has **2048 words** — 11 bits per word. 12 words = 128 bits entropy + 4-bit checksum.
- Adding a **passphrase** (the "25th word") creates a completely different wallet from the same mnemonic.
- Anyone with your seed phrase has full control of all derived wallets — treat it like cash in hand.
- `bip39` npm package or `mnemonic` in Python's `eth_account` generates/validates these.
- MetaMask stores your seed phrase encrypted with your password locally.

### Production FAQ
**Q: Are all 12-word phrases equally secure?**  
A: Only if generated with proper randomness (CSPRNG). Human-chosen words are NOT random — never make up your own phrase.

**Q: What's the passphrase (25th word) good for?**  
A: Plausible deniability — different passphrases reveal different wallets from the same mnemonic, letting you have a "decoy" wallet under duress.

---

## 8. HD Wallet (BIP-32/BIP-44)

**One-line definition:** A Hierarchical Deterministic wallet that generates an entire tree of key pairs from a single seed — one backup, infinite addresses.

### Real-World Dev Example
```js
const { ethers } = require("ethers");
const mnemonic = "test test test test test test test test test test test junk";
const hdNode = ethers.HDNodeWallet.fromPhrase(mnemonic);

// Derive child wallets
const child0 = hdNode.derivePath("m/44'/60'/0'/0/0");
const child1 = hdNode.derivePath("m/44'/60'/0'/0/1");
```

### ASCII Diagram
```
  Master Seed
      │
      ├── m/44'/60'/0'/0/0  ← ETH Account 0, Address 0
      ├── m/44'/60'/0'/0/1  ← ETH Account 0, Address 1
      ├── m/44'/60'/1'/0/0  ← ETH Account 1, Address 0
      └── m/44'/0'/0'/0/0   ← BTC Account 0, Address 0
```

### Gotchas & Dev Context
- **BIP-32**: Defines the tree derivation algorithm (HMAC-SHA512 chained).
- **BIP-44**: Defines the standard path structure: `m / purpose' / coin_type' / account' / change / index`.
- Hardened derivation (`'`) uses the private key in the HMAC — child keys can't compromise parent.
- Non-hardened derivation: knowing a child public key + parent chain code leaks the parent private key!
- Most wallets default to BIP-44; Ledger Live uses it; MetaMask does too.

### Production FAQ
**Q: Do I need a new seed phrase for each blockchain?**  
A: No — one seed works for all chains via different coin_type paths (60 = ETH, 0 = BTC, 501 = SOL, etc.).

**Q: What's the difference between BIP-32 and BIP-44?**  
A: BIP-32 is the raw derivation algorithm. BIP-44 is a convention on top of it — a standardized path structure so all wallets can interoperate.

---

## 9. Derivation Path

**One-line definition:** A slash-separated address in the HD wallet tree that pinpoints exactly which key pair to generate from the master seed.

### Real-World Dev Example
```
m / 44' / 60' / 0' / 0 / 5

m   = master seed
44' = BIP-44 purpose (hardened)
60' = Ethereum coin type (hardened)
0'  = account index 0 (hardened)
0   = external chain (0=receive, 1=change)
5   = address index 5
```

### ASCII Diagram
```
  m ──44'──► Purpose node
       └──60'──► Ethereum subtree
              └──0'──► Account 0
                    └──0──► External addresses
                          ├──0  (Address #0)
                          ├──1  (Address #1)
                          └──5  (Address #5)  ◄── this one
```

### Gotchas & Dev Context
- **Hardened (`'`) nodes**: Safer, but require the private key to derive children — xpub alone can't.
- **Non-hardened nodes**: Can derive children from the extended public key (xpub) — used for watch-only wallets.
- Mismatched paths = wrong address. If MetaMask shows `m/44'/60'/0'/0/0` but your app uses `m/44'/60'/0'/0`, you'll get different addresses from the same seed.
- Trezor and Ledger use slightly different defaults for some coins — always verify.

### Production FAQ
**Q: My wallet shows the right address on MetaMask but not in my dApp — why?**  
A: You're likely using a different derivation path. Compare the path used in MetaMask (legacy: `m/44'/60'/0'/x`) vs your library's default.

**Q: Can I use a custom derivation path?**  
A: Yes — any valid BIP-32 path works. Just document it; if you lose the path, you'll lose access even with the correct seed.

---

## 10. Keystore / Encrypted Key File

**One-line definition:** A JSON file that stores a private key encrypted with a password — a portable, password-protected backup format.

### Real-World Dev Example
```json
{
  "version": 3,
  "id": "uuid-here",
  "address": "0xabc123...",
  "crypto": {
    "cipher": "aes-128-ctr",
    "ciphertext": "...",
    "kdf": "scrypt",
    "kdfparams": { "n": 262144, "r": 8, "p": 1, "dklen": 32, "salt": "..." },
    "mac": "..."
  }
}
```

### Gotchas & Dev Context
- **KDF** (Key Derivation Function): `scrypt` or `pbkdf2` — stretches your password to resist brute-force.
- The keystore file is useless without the password; the password is useless without the keystore.
- `geth account import keystore.json` — Geth's CLI command to load a keystore.
- `ethers.js`: `Wallet.fromEncryptedJson(json, password)` — async, deliberately slow (scrypt).
- Default `n=262144` for scrypt makes brute-forcing expensive — but a weak password still gets cracked.
- Never store keystore + password in the same location.

### Production FAQ
**Q: Is a keystore safer than storing the raw private key?**  
A: Only if the password is strong. A keystore with `password123` is weaker than a raw key on an air-gapped machine.

**Q: Do hardware wallets use keystores?**  
A: No. Hardware wallets store keys in a tamper-resistant secure element — keystores are a software wallet concept.

---

## 11. Signing vs Encryption

**One-line definition:** Signing proves **who sent** a message (authentication); Encryption hides **what's in** a message (confidentiality) — blockchain primarily uses signing, not encryption.

### Real-World Dev Example
```
SIGNING (what Ethereum does):
  Alice signs a tx → anyone can read the tx → anyone can verify it's from Alice

ENCRYPTION (e.g., private messaging):
  Alice encrypts a message → only Bob (with his private key) can read it
  → no one else can verify it came from Alice unless she signs too
```

### ASCII Diagram
```
  ── SIGNING ────────────────────────────────
  Message + Private Key → Signature
  Message + Signature + Public Key → ✓ or ✗

  ── ENCRYPTION ─────────────────────────────
  Message + Recipient's Public Key → Ciphertext
  Ciphertext + Recipient's Private Key → Message
```

### Gotchas & Dev Context
- Ethereum transactions are **signed and public** — not encrypted.
- ECIES (Elliptic Curve Integrated Encryption Scheme) can encrypt for a recipient's public key — used in some messaging dApps.
- **TLS** uses both: encryption for privacy, signatures for authentication.
- Smart contracts cannot decrypt data — they only verify signatures (via `ecrecover`).
- Signing the same message twice with the same key yields the same signature in EdDSA; different in ECDSA (due to random nonce).

### Production FAQ
**Q: Can I hide transaction data on Ethereum with encryption?**  
A: Not natively — calldata is public. Use private mempools (Flashbots), ZK proofs, or L2s with data encryption for privacy.

**Q: What's `eth_decrypt` in MetaMask?**  
A: A legacy MetaMask API for ECIES decryption using your Ethereum key. Deprecated and discouraged for new dApps.

---

## 12. Zero-Knowledge Proofs (ZKP)

**One-line definition:** A method where one party (the prover) convinces another (the verifier) that a statement is true, without revealing any information beyond the truth of the statement itself.

### Real-World Dev Example
**Real-world analogy:** Prove you're over 18 to a bouncer without showing your birthday, name, or address — just the proof that the condition holds.

**Blockchain use case:** Prove you know a password for a private transaction without revealing the password or the transaction amount.

### ASCII Diagram
```
  Prover                          Verifier
    │                                │
    │── "I know secret X such ──►   │
    │    that f(X) = Y"              │
    │                                │
    │◄── Challenge ─────────────────│
    │                                │
    │── Response (no X revealed) ──►│
    │                                │
    │                           ✓ Convinced
    │                        (knows f(X)=Y)
    │                        (doesn't know X)
```

### Gotchas & Dev Context
- Three properties: **Completeness** (true proofs pass), **Soundness** (false proofs fail), **Zero-knowledge** (no info leaked).
- ZKPs are computationally expensive to generate (proving time) but fast to verify.
- Main blockchain applications: ZK rollups, private transactions (Zcash), identity proofs, voting.
- "Interactive" ZKPs require back-and-forth; "Non-interactive" (NIZK) use a single proof message — blockchains need NIZK.

### Production FAQ
**Q: Does ZKP mean my transaction is anonymous?**  
A: Privacy depends on the implementation. ZKP can hide amounts/data but not always sender/receiver without additional techniques (stealth addresses, mixers).

**Q: Are ZKPs only useful for privacy?**  
A: No — ZK rollups use them for **scalability** (prove 10,000 txs are valid in one proof) without privacy, verifying computation correctness off-chain.

---

## 13. zk-SNARKs

**One-line definition:** **S**uccinct **N**on-interactive **AR**guments of **K**nowledge — a type of ZKP that produces tiny proofs verified in milliseconds, at the cost of a trusted setup.

### Real-World Dev Example
Used in: **Zcash** (shielded transactions), **zkSync Era**, **Polygon zkEVM**, **Groth16** proofs in many DeFi protocols.

```
Proof size:    ~200 bytes  (constant, regardless of computation size)
Verify time:   ~10 ms
Prove time:    seconds to minutes
```

### ASCII Diagram
```
  Computation (e.g., 10,000 txs)
          │
          ▼ [Prover: expensive]
  zk-SNARK Proof (~200 bytes)
          │
          ▼ [Verifier: cheap]
  Valid ✓ or Invalid ✗
  (posted on L1 Ethereum)
```

### Gotchas & Dev Context
- **Trusted Setup required**: A ceremony generates a CRS (Common Reference String). If the ceremony is compromised, fake proofs can be generated.
- Common SNARK systems: **Groth16** (smallest proofs), **PLONK** (universal setup), **Marlin**.
- Not quantum-resistant — relies on elliptic curve pairings (BN254, BLS12-381).
- Circuit constraints define what you're proving — bugs in circuits can allow invalid proofs.
- Tools: **circom** (circuit language), **snarkjs** (JS prover/verifier), **bellman** (Rust).

### Production FAQ
**Q: What's a "circuit" in zk-SNARKs context?**  
A: An arithmetic circuit encoding your computation as a system of constraints — like a low-level program that the ZK system proves was executed correctly.

**Q: Why do zkSync and Polygon use SNARKs and not STARKs?**  
A: Smaller proof size = lower L1 verification cost (gas). STARKs are larger but don't need trusted setup — it's a tradeoff.

---

## 14. zk-STARKs

**One-line definition:** **S**calable **T**ransparent **AR**guments of **K**nowledge — a ZKP variant with no trusted setup, quantum resistance, and better scalability, at the cost of larger proof sizes.

### Real-World Dev Example
Used in: **StarkNet**, **StarkEx** (dYdX v3, Immutable X), **STARK proofs** on Ethereum L1 verification.

```
Proof size:    ~45-200 KB  (logarithmically scales with computation)
Verify time:   ~50-100 ms
Prove time:    faster than SNARKs at scale
```

### ASCII Diagram
```
  SNARKs vs STARKs:

  │ Property          │ SNARK         │ STARK         │
  ├───────────────────┼───────────────┼───────────────┤
  │ Proof size        │ ~200 bytes    │ ~45-200 KB    │
  │ Trusted setup     │ Required      │ Not required  │
  │ Quantum safe      │ No            │ Yes           │
  │ Prover speed      │ Slower        │ Faster        │
  │ Verifier cost     │ Lower gas     │ Higher gas    │
```

### Gotchas & Dev Context
- STARKs use **hash functions** (collision-resistant) instead of elliptic curve pairings — reason for quantum safety.
- Larger proofs = more calldata = higher gas on L1. StarkNet batches many proofs to amortize cost.
- **FRI** (Fast Reed-Solomon IOP of Proximity) is the key sub-protocol in STARKs.
- Cairo language (StarkNet's VM) compiles programs into STARK-provable execution traces.
- No trusted setup = transparent = no ceremony risk.

### Production FAQ
**Q: Should I build on a SNARK-based or STARK-based chain?**  
A: STARKs for long-term quantum safety and transparency; SNARKs for cheaper L1 verification today. Most new L2s pick based on ecosystem tooling and cost models.

**Q: Can SNARKs and STARKs be combined?**  
A: Yes — STARK proof generation + SNARK proof wrapping (STARK → SNARK "proof aggregation") gives small final proofs without trusted setup end-to-end. Used by some advanced ZK rollups.

---

## 15. ZK Rollup Circuits

**One-line definition:** The set of arithmetic constraints (the "circuit") that encode what a valid batch of L2 transactions looks like — the ZK proof proves these constraints were satisfied.

### Real-World Dev Example
A zkEVM circuit encodes every valid EVM opcode execution as constraints. The prover runs 10,000 transactions, satisfies all constraints, and generates one proof that L1 verifies.

### ASCII Diagram
```
  L2 Transactions (10,000 txs)
          │
          ▼
  [ZK Circuit / Constraint System]
  • Signature valid for each tx?
  • Balances updated correctly?
  • No double spend?
          │
          ▼ Witness (private inputs — the actual tx data)
  [Prover generates SNARK/STARK proof]
          │
          ▼
  Proof + New State Root
          │
          ▼ [L1 Smart Contract verifies proof]
  Ethereum accepts new state ✓
```

### Gotchas & Dev Context
- Circuits are **not Turing complete** by themselves — they're fixed computation shapes.
- A bug in the circuit (underconstrained) can allow a prover to cheat — circuit audits are critical.
- zkEVM circuits are enormous (millions of constraints for full EVM compatibility).
- Types of zkEVM: **Type 1** (full Ethereum equivalent) → **Type 4** (language equivalent only) — tradeoffs in proving speed vs compatibility.
- Circuit code is usually in Circom, Halo2, or Noir (higher-level ZK DSL).

### Production FAQ
**Q: Who generates the ZK proofs in a rollup?**  
A: A centralized **prover** (sequencer) in most current implementations — decentralized proving networks are being built (e.g., Succinct Labs, Gevulot).

**Q: What happens if the ZK circuit has a bug?**  
A: An attacker could submit a fake proof that passes verification, allowing theft of L2 funds. This is why circuit auditing is paramount.

---

## 16. Trusted Setup

**One-line definition:** A one-time ceremony that generates cryptographic parameters (CRS/SRS) required for certain ZK proof systems — if the ceremony is corrupted, the entire system is compromised.

### Real-World Dev Example
**Zcash's "Powers of Tau" ceremony (2017):** Six contributors sequentially added randomness. If **even one** contributor destroyed their "toxic waste" (secret randomness used during setup), the system is safe — because compromising it requires ALL contributors' secrets.

### ASCII Diagram
```
  Ceremony:
  Participant 1 → adds randomness → passes to #2
  Participant 2 → adds randomness → passes to #3
  ...
  Participant N → adds randomness → final CRS published

  "Toxic waste" (each participant's secret) must be destroyed.

  Security holds if ≥ 1 participant is honest.
  └── N = 1: You must trust that person fully.
  └── N = 100: Attacker needs all 100 secrets simultaneously.
```

### Gotchas & Dev Context
- Required for: **Groth16** (per-circuit setup), partially for **PLONK** (universal setup — one ceremony, many circuits).
- **Not required** for STARKs, FRI-based systems.
- The "toxic waste" must be cryptographically deleted — verifiable via multi-party computation (MPC).
- Ethereum KZG ceremony (EIP-4844 "Proto-Danksharding") had 140k+ contributors — the largest ever.
- PLONK's universal SRS (Structured Reference String) is reusable across circuits — a big improvement.

### Production FAQ
**Q: Can I trust a trusted setup I didn't participate in?**  
A: Yes, probabilistically. With 100+ independent participants, the probability that all acted maliciously is astronomically small — just verify the ceremony transcript is published.

**Q: What's the difference between CRS and SRS?**  
A: **CRS** (Common Reference String) = generic term. **SRS** (Structured Reference String) = a specific CRS format used in polynomial commitment schemes like KZG.

---

## 17. Commitment Schemes

**One-line definition:** A cryptographic primitive that lets you "commit" to a value now (hiding it) and "reveal" it later — proving you didn't change your answer after seeing others'.

### Real-World Dev Example
```
On-chain sealed bid auction:
1. Bidder commits: hash(bid_amount + secret_nonce) → stored on-chain
2. Bidding phase ends
3. Reveal phase: bidder posts (bid_amount, nonce)
4. Contract verifies: hash(bid_amount + nonce) == stored commitment ✓
```

### ASCII Diagram
```
  COMMIT phase:                  REVEAL phase:
  value + nonce                  value + nonce
       │                               │
       ▼                               ▼
  hash(value, nonce) ─ stored ─► verify hash matches? ✓
  (hides value)                  (reveals value, proves unchanged)
```

### Gotchas & Dev Context
- Two properties: **Hiding** (commitment reveals nothing) and **Binding** (can't change committed value).
- Hash-based commitments: simple but not ZK-friendly. **Pedersen commitments** (elliptic curve) are additively homomorphic — used in ZK proofs and confidential transactions.
- **KZG commitments** (polynomial commitments): used in EIP-4844 (blob transactions) and PLONK — allow proving properties of polynomials efficiently.
- Nonce/salt is critical — without it, a commitment to a small value space (e.g., yes/no) can be brute-forced.
- Verkle trees (Ethereum's future state tree) use vector commitments.

### Production FAQ
**Q: What's the difference between a commitment and a hash?**  
A: A hash is a one-way function; a commitment is a scheme with formal hiding + binding proofs and a structured reveal mechanism. Hashes are often used to *implement* commitments but aren't commitments themselves.

**Q: Where are KZG commitments used in Ethereum today?**  
A: EIP-4844 (Dencun upgrade, March 2024) — blob transactions use KZG commitments so L2s can post data cheaply and L1 can verify it without storing it permanently.

---

*End of Batch 3 — Cryptography & Keys*

> **Next up:** Batch 4 — Consensus Mechanisms & Network Security
