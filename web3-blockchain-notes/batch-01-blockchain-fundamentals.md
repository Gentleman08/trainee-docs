# Batch 1 — Blockchain Fundamentals
> The core building blocks that every blockchain developer must understand first.

---

## 1. Blockchain

### Definition
A blockchain is a continuously growing list of records (blocks) that are cryptographically linked together and stored across many computers simultaneously — making tampering practically impossible.

### Real-World Dev Example
When you deploy an ERC-20 token on Ethereum, every transfer you make gets packed into a block and appended to Ethereum's chain. You can verify any transfer using its block number and transaction hash — no bank or central authority needed.

```js
// Reading a block in ethers.js
const block = await provider.getBlock("latest");
console.log(block.number, block.hash);
```

### ASCII Diagram
```
[Block 0 (Genesis)] <-- [Block 1] <-- [Block 2] <-- [Block 3]
   hash: 0x000...       hash: 0xabc    hash: 0xdef    hash: 0x123
                        prevHash: 0x000 prevHash: 0xabc prevHash: 0xdef
```
Each block points back to its parent via `prevHash`, forming a tamper-evident chain.

### Gotchas & Dev Context
- "Blockchain" ≠ database — reads are free, writes (transactions) cost gas on Ethereum.
- Blockchains are append-only; you cannot delete or edit past data.
- Not all blockchains are public — private/consortium chains (Hyperledger) exist for enterprise.
- A chain is only as secure as its consensus mechanism — a small chain is vulnerable to 51% attacks.

### Production FAQ
**Q: Can I store large files on a blockchain?**
A: No. On-chain storage is extremely expensive. Store a file's hash on-chain and the file itself on IPFS or Arweave.

**Q: How is blockchain different from a regular database?**
A: A database has an admin who can edit or delete rows. A blockchain has no admin — data is append-only and verified by thousands of nodes.

**Q: Is every blockchain public?**
A: No. Bitcoin and Ethereum are public. Hyperledger Fabric and Quorum are permissioned/private blockchains used in enterprise settings.

---

## 2. Distributed Ledger

### Definition
A distributed ledger is a database that is replicated and synchronized across many computers (nodes) with no single point of control. A blockchain is one specific type of distributed ledger.

### Real-World Dev Example
When your Solidity contract emits an event, that event is recorded in a transaction stored in the ledger. Every node on the network holds a copy — so if 1,000 nodes exist, 1,000 copies of that transaction exist simultaneously.

### ASCII Diagram
```
  Node A          Node B          Node C
 [Ledger]  <-->  [Ledger]  <-->  [Ledger]
  copy 1          copy 2          copy 3
      (All copies are identical)
```

### Gotchas & Dev Context
- Not all distributed ledgers use blocks or chains — DAGs (Directed Acyclic Graphs) like IOTA are also distributed ledgers.
- "Distributed" means spread across nodes; "decentralized" means no single entity controls those nodes — these are different properties.
- Syncing a new node means downloading the entire ledger history — this can take days for mature chains.
- Read performance from a local node is fast; write confirmations require network-wide propagation.

### Production FAQ
**Q: If I run my own Ethereum node, do I get my own copy of the ledger?**
A: Yes. Your node stores the full ledger and validates every block independently — you don't have to trust anyone else's data.

**Q: Can two nodes have different versions of the ledger temporarily?**
A: Yes — this is called a temporary fork. Consensus rules resolve it, and the longer chain wins (in PoW) or the finalized chain is kept (in PoS).

---

## 3. Decentralization

### Definition
Decentralization means no single entity controls the network — decisions, data, and execution are distributed across independent participants so no one can unilaterally censor, alter, or shut down the system.

### Real-World Dev Example
A Uniswap liquidity pool runs as a smart contract on Ethereum. Even if Uniswap Labs disappears tomorrow, the contract keeps running — anyone with ETH can interact with it. No central server to take down.

### ASCII Diagram
```
Centralized:         Decentralized:
   [Server]            [Node] [Node]
   /  |  \            /    \  /    \
[U] [U] [U]        [Node] [Node] [Node]
                        (no center)
```

### Gotchas & Dev Context
- Decentralization is a spectrum, not binary — Ethereum is more decentralized than a private Hyperledger network, but less so than Bitcoin (by some metrics).
- "Decentralized app (dApp)" is misleading if the frontend is on a centralized server — the contract is decentralized, the UI might not be.
- More decentralization = slower consensus and harder upgrades (no sudo).
- Upgrading a decentralized protocol requires governance votes or hard forks.

### Production FAQ
**Q: My dApp's smart contract is on Ethereum, but the UI is on AWS. Is it decentralized?**
A: Partially. The on-chain logic is decentralized, but if AWS goes down, users lose the UI. Host frontends on IPFS for fuller decentralization.

**Q: Can the Ethereum Foundation freeze my smart contract?**
A: No. Once deployed, a contract runs autonomously. The Foundation cannot freeze individual contracts (though validators could theoretically censor transactions, which is a separate concern).

---

## 4. Nodes (Full Node, Light Node, Archive Node)

### Definition
A node is a computer that participates in a blockchain network. Different node types trade off between storage, bandwidth, and trust requirements.

### Real-World Dev Example
When you use MetaMask with Infura, you're relying on Infura's full nodes. If you run your own `geth` instance, you are the node.

```bash
# Run a full Ethereum node (geth)
geth --syncmode "snap" --http --http.api eth,net,web3
```

### ASCII Diagram
```
Archive Node     Full Node        Light Node
[All states]    [Current state]  [Block headers only]
[All history]   [All blocks]     [Trusts full nodes]
   ~14 TB          ~1 TB            ~MBs
```

### Gotchas & Dev Context
- **Full Node**: Stores all blocks + current state. Validates independently. Gold standard for trust.
- **Light Node**: Only downloads block headers. Verifies via Merkle proofs. Good for mobile wallets.
- **Archive Node**: Stores every historical state snapshot. Required for `eth_call` at old block numbers. Very expensive to run (~14 TB+).
- Infura / Alchemy run archive nodes — that's why historical queries work via their APIs.
- Running your own node avoids third-party trust, improves privacy, and avoids rate limits.

### Production FAQ
**Q: Do I need an archive node to query past `balanceOf` calls?**
A: Yes. `eth_getBalance` at a historical block requires an archive node. Full nodes only keep current state.

**Q: Can a light node be tricked into accepting invalid transactions?**
A: Theoretically, yes — it trusts full nodes for state. Use a full node for high-security applications.

---

## 5. Blocks

### Definition
A block is a batch of validated transactions bundled together with metadata (header) and appended to the chain at regular intervals.

### Real-World Dev Example
When you call `sendTransaction()` in ethers.js, your transaction sits in the mempool until a validator picks it up, bundles it with ~100–500 other transactions, and mines/proposes a block.

```js
const tx = await contract.transfer(recipient, amount);
const receipt = await tx.wait(); // waits for block inclusion
console.log("Included in block:", receipt.blockNumber);
```

### ASCII Diagram
```
┌─────────────────────────────┐
│         BLOCK HEADER        │
│  prevHash | merkleRoot |    │
│  timestamp | nonce | ...    │
├─────────────────────────────┤
│  TX_1: Alice → Bob 1 ETH   │
│  TX_2: Bob → Carol 0.5 ETH │
│  TX_3: Deploy Contract      │
│         ... more TXs        │
└─────────────────────────────┘
```

### Gotchas & Dev Context
- Block size is limited (by gas limit on Ethereum, by byte size on Bitcoin).
- Transactions in a block are ordered — miners/validators can reorder them (MEV risk).
- A transaction is not "final" just because it's in a block — it can be reversed by a reorg (see Reorg section).
- `receipt.blockNumber` gives the block your tx landed in; use `confirmations` to track safety.

### Production FAQ
**Q: What happens if my transaction is never included in a block?**
A: It stays in the mempool until it expires (usually ~3 days) or you replace it with a higher-fee transaction using the same nonce.

**Q: Can two valid blocks exist for the same height simultaneously?**
A: Yes — briefly. This is called an uncle (Ethereum) or orphan (Bitcoin) block. The chain eventually picks one and discards the other.

---

## 6. Block Header

### Definition
The block header is a compact summary of a block's metadata — it contains the cryptographic fingerprint of all transactions and links the block to its parent.

### Real-World Dev Example
When a light node verifies a payment, it only downloads block headers and uses Merkle proofs against the `merkleRoot` in the header — it never needs the full block body.

### ASCII Diagram
```
┌─────────────────────────────────────────┐
│              BLOCK HEADER               │
│  previousBlockHash: 0xabc123...         │
│  merkleRoot:        0xdef456...         │
│  timestamp:         1700000000          │
│  nonce:             3928471             │
│  difficulty:        0x1bc...            │
│  gasLimit:          30000000            │
│  gasUsed:           14823901            │
└─────────────────────────────────────────┘
```

### Gotchas & Dev Context
- The block hash is derived from the header only — NOT from the transaction list directly.
- Changing even one transaction changes the `merkleRoot`, which changes the header hash — invalidating the block.
- In Ethereum PoS, the header also includes `withdrawalsRoot` and `parentBeaconBlockRoot` (post-Merge fields).
- `blockhash(blockNumber)` in Solidity only works for the last 256 blocks — store important hashes yourself.

### Production FAQ
**Q: Can I verify a specific transaction without downloading the entire block?**
A: Yes. Use the `merkleRoot` in the header + a Merkle proof for your transaction. This is how SPV (Simple Payment Verification) works.

**Q: Why does the block hash change if I alter one transaction?**
A: Because the `merkleRoot` (a hash of all transactions) is in the header, and changing any transaction changes the merkleRoot, which changes the header hash.

---

## 7. Block Height

### Definition
Block height is the sequential number of a block in the chain, starting from 0 (genesis). It tells you how many blocks have been added before it.

### Real-World Dev Example
On Ethereum, you can pin a smart contract deployment to a specific block height for reproducibility or auditing.

```js
// Get current block height
const height = await provider.getBlockNumber();
console.log("Current height:", height); // e.g., 19500000

// Fetch state at a specific historical height
const balance = await provider.getBalance(address, 18000000);
```

### Gotchas & Dev Context
- Block height ≠ block hash. Two chains can have the same height but different hashes (during a fork).
- Don't use block height as a reliable timer — block times vary. Use timestamps for time-sensitive logic.
- After a reorg, the "current" block height can temporarily decrease before climbing again.
- Solidity exposes current block height via `block.number` — but it returns the height of the block being mined, not real-time.

### Production FAQ
**Q: I'm using `block.number` for a lock-up period in my contract. Is that safe?**
A: Risky. Block times can change (Ethereum averages ~12s but varies). Use `block.timestamp` + seconds for time-based logic instead.

**Q: Two chains both claim block height 5,000,000 — which is real?**
A: Both are real chains; one is the canonical chain (more total work or finalized) and one is a stale fork. Nodes follow the canonical chain.

---

## 8. Block Time

### Definition
Block time is the average interval between consecutive blocks being added to the chain — it's a measure of how fast the network produces new blocks.

### Real-World Dev Example
Ethereum targets ~12 seconds per block. If you call `provider.getBlockNumber()` in a loop, you'll see it increment roughly every 12 seconds.

```js
// Poll every block
provider.on("block", (blockNumber) => {
  console.log("New block:", blockNumber);
  // fires ~every 12s on Ethereum mainnet
});
```

### Gotchas & Dev Context
- **Bitcoin**: ~10 min | **Ethereum**: ~12 sec | **Solana**: ~400 ms | **BSC**: ~3 sec
- Shorter block time = faster UX, but increases uncle/orphan block rate (less propagation time).
- Block time ≠ transaction confirmation time. You usually wait 6+ blocks on Bitcoin (~60 min) for high-value transfers.
- Using `block.number` as a timer in Solidity is unreliable because block times fluctuate.
- The difficulty adjustment algorithm (PoW) or slot timing (PoS) controls block time.

### Production FAQ
**Q: My dApp shows "pending" for 2 minutes. Is block time the cause?**
A: Possibly — but also check gas price. Low-fee transactions wait longer in the mempool even if the chain produces blocks quickly.

**Q: Can block time be 0 on a private chain?**
A: Yes. Some private chains (like Hardhat's `--mining` auto-mine mode) produce a block per transaction — great for testing, unrealistic for production.

---

## 9. Merkle Tree

### Definition
A Merkle tree is a binary tree where every leaf node holds a transaction hash, and every parent node holds the hash of its two children — creating a single root hash that represents the entire set of transactions.

### Real-World Dev Example
Ethereum uses a Merkle Patricia Trie for transactions, receipts, and state. OpenZeppelin's `MerkleProof` library lets you do allowlist checks on-chain using a root stored in the contract.

```solidity
// Verify a merkle proof on-chain (OpenZeppelin)
bool valid = MerkleProof.verify(proof, merkleRoot, leaf);
```

### ASCII Diagram
```
            [Root Hash]
           /            \
      [Hash AB]        [Hash CD]
      /      \          /      \
  [Hash A] [Hash B] [Hash C] [Hash D]
    TX_A     TX_B     TX_C     TX_D
```
Change TX_B → Hash B changes → Hash AB changes → Root changes.

### Gotchas & Dev Context
- A Merkle proof lets you prove one transaction exists in a block with `O(log n)` hashes — no need to share all transactions.
- NFT/allowlist minting commonly uses Merkle trees: store only the root on-chain, verify proofs off-chain.
- An odd number of leaves means the last leaf is duplicated — handle this in your Merkle tree library.
- The Ethereum state trie is a more complex Merkle Patricia Trie, not a simple binary tree.

### Production FAQ
**Q: I have 10,000 allowlisted wallets. Should I store them all on-chain?**
A: No — store only the Merkle root (32 bytes). Users submit a proof at mint time; `MerkleProof.verify()` checks it on-chain for a few thousand gas.

**Q: Can a Merkle proof be faked?**
A: Not without breaking SHA-256/Keccak-256. If the root matches, the proof is valid with cryptographic certainty.

---

## 10. Merkle Root

### Definition
The Merkle root is the single top-level hash of a Merkle tree — it's a cryptographic fingerprint of every transaction in a block, stored in the block header.

### Real-World Dev Example
When an Ethereum validator proposes a block, the `transactionsRoot` in the header is the Merkle root of all transactions in that block. Change one transaction → root changes → block is invalid.

```python
# Conceptual Python: computing a simple merkle root
import hashlib

def hash_pair(a, b):
    return hashlib.sha256((a + b).encode()).hexdigest()

leaves = ["tx1_hash", "tx2_hash", "tx3_hash", "tx3_hash"]  # pad to even
level = leaves
while len(level) > 1:
    level = [hash_pair(level[i], level[i+1]) for i in range(0, len(level), 2)]
merkle_root = level[0]
```

### Gotchas & Dev Context
- The Merkle root is stored in the **block header**, not in the block body — this is what makes light client verification possible.
- Ethereum has three separate roots in each block: `transactionsRoot`, `receiptsRoot`, `stateRoot`.
- A changed transaction anywhere in the block produces a completely different Merkle root (avalanche effect).
- `stateRoot` is the root of the state trie — capturing all account balances and contract storage at that block.

### Production FAQ
**Q: What's the difference between `transactionsRoot` and `stateRoot` in an Ethereum block?**
A: `transactionsRoot` proves which transactions are in the block. `stateRoot` proves the entire world state (all accounts, balances, contract storage) after executing those transactions.

**Q: If I know the Merkle root, can I reconstruct all transactions?**
A: No. The root is a one-way hash. You need the actual transaction data; the root just lets you verify that data's integrity.

---

## 11. Hashing (SHA-256, Keccak-256)

### Definition
Hashing is a one-way function that converts any input into a fixed-length string of bytes. The same input always produces the same output; even a tiny change produces a completely different hash.

### Real-World Dev Example
Bitcoin uses SHA-256 for Proof-of-Work mining. Ethereum uses Keccak-256 (a SHA-3 variant) for everything — address derivation, function selectors, event topics.

```solidity
// Keccak-256 in Solidity
bytes32 hash = keccak256(abi.encodePacked(msg.sender, amount, nonce));

// Function selector = first 4 bytes of keccak256 of signature
// keccak256("transfer(address,uint256)") → 0xa9059cbb...
```

```python
# SHA-256 in Python
import hashlib
h = hashlib.sha256(b"hello").hexdigest()
# → "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
```

### Gotchas & Dev Context
- **SHA-256** ≠ **Keccak-256** — Ethereum does NOT use standard SHA-3; it uses the pre-standardization Keccak variant. Don't mix them up in off-chain tooling.
- Hashes are deterministic but not reversible — you cannot get the input from the hash.
- Collision resistance: finding two inputs with the same hash is computationally infeasible.
- `abi.encode` vs `abi.encodePacked`: packed encoding can cause hash collisions with dynamic types — prefer `abi.encode` for security-critical hashing.

### Production FAQ
**Q: Can I use `keccak256` as a random number in a smart contract?**
A: No. Miners/validators can manipulate `block.timestamp` and `blockhash`. Use Chainlink VRF for on-chain randomness.

**Q: Why does Ethereum use Keccak-256 instead of standard SHA-256?**
A: Ethereum was designed before SHA-3 was finalized. It uses the original Keccak submission, which differs slightly from NIST's final SHA-3 standard.

---

## 12. Nonce

### Definition
A nonce ("number used once") serves two purposes in blockchain: in PoW mining it's the number miners iterate to find a valid block hash; in Ethereum accounts it's a counter tracking how many transactions an address has sent.

### Real-World Dev Example
```js
// Account nonce — prevents replay attacks
const nonce = await provider.getTransactionCount(myAddress);
// Every new transaction must use nonce + 1

// If you send two txs simultaneously:
tx1 = { nonce: 42, ... }
tx2 = { nonce: 43, ... } // must be sequential
```

### ASCII Diagram
```
Mining nonce (PoW):
Hash(blockData + nonce=0)   = 0xf3a9... ❌ (too high)
Hash(blockData + nonce=1)   = 0xc12b... ❌
...
Hash(blockData + nonce=8291)= 0x0000a3... ✅ (below target)
```

### Gotchas & Dev Context
- **Account nonce**: If you skip a nonce (e.g., send nonce 5 before nonce 4 confirms), nonce 5 is stuck until nonce 4 is included.
- **Nonce too low error**: you're reusing a nonce that was already mined — increment it.
- Replay attack protection: a transaction signed for chain A cannot be replayed on chain B if chain IDs differ (EIP-155).
- In PoS Ethereum, the mining nonce concept is gone — blocks don't require PoW. Account nonces remain.

### Production FAQ
**Q: My transaction is stuck "pending" — how do I fix it?**
A: Send a replacement transaction with the same nonce but a higher gas price. This replaces the pending tx in the mempool.

**Q: Can I send multiple transactions at once from the same wallet?**
A: Yes — assign sequential nonces (N, N+1, N+2…) manually. Most wallets handle this automatically, but scripts must manage nonces explicitly.

---

## 13. Genesis Block

### Definition
The genesis block is the very first block in a blockchain (block height 0). It is hardcoded — not mined or produced through consensus — and every other block in the chain descends from it.

### Real-World Dev Example
When you spin up a private Ethereum chain with Hardhat or Geth, you provide a `genesis.json` file that defines the genesis block: initial balances, chain ID, gas limits.

```json
// genesis.json (simplified)
{
  "config": { "chainId": 1337 },
  "difficulty": "0x1",
  "gasLimit": "0x8000000",
  "alloc": {
    "0xYourAddress": { "balance": "1000000000000000000000" }
  }
}
```

```bash
geth init genesis.json --datadir ./mychain
```

### Gotchas & Dev Context
- The genesis block has no `previousBlockHash` (or it's set to all zeros).
- Bitcoin's genesis block (Jan 3, 2009) contains a hidden message: "Chancellor on brink of second bailout for banks."
- Ethereum mainnet genesis block was created on July 30, 2015.
- If two nodes have different genesis blocks, they will never sync — they're on entirely different networks.
- `chainId` in genesis is critical — it's used in EIP-155 transaction signing.

### Production FAQ
**Q: Can I change the genesis block after my chain is running?**
A: No. The genesis block is immutable by definition. Changing it creates a completely separate chain incompatible with existing nodes.

**Q: Why does `chainId` matter in the genesis block?**
A: It's embedded in every signed transaction (EIP-155) to prevent replay attacks across different chains (e.g., mainnet vs testnet).

---

## 14. Chain Reorganization (Reorg)

### Definition
A chain reorganization (reorg) happens when a node switches from its current chain to a longer/heavier competing chain, effectively "un-including" some recent blocks and replacing them with different ones.

### Real-World Dev Example
If your app shows 3 block confirmations and accepts a payment, a reorg of depth 4 could reverse that payment. Most exchanges require 6–30 confirmations specifically to survive reorgs.

### ASCII Diagram
```
Original view:        After reorg:
A → B → C → D        A → B → E → F → G  ← canonical (longer)
              ↑            ↑
           (tip)      C → D  ← orphaned (discarded)
```

### Gotchas & Dev Context
- Shallow reorgs (1–2 blocks) happen occasionally even on Ethereum mainnet.
- Deep reorgs (>6 blocks) are rare on major chains but can happen on smaller chains with low hash rate.
- A reorg can reverse transactions — money that appeared confirmed can "un-confirm."
- In Ethereum PoS, blocks are "finalized" after ~2 epochs (~13 min) — finalized blocks cannot be reorged without slashing ⅓ of all staked ETH.
- Indexers and analytics tools must handle reorgs by rolling back and re-indexing orphaned blocks.

### Production FAQ
**Q: My block explorer shows a transaction as confirmed, but it disappeared. What happened?**
A: A reorg discarded the block your transaction was in. The transaction went back to the mempool and will be re-mined (likely in the next few blocks).

**Q: How many confirmations should my dApp require?**
A: For small amounts: 1–3 blocks. For high value: 6+ on Ethereum (or wait for finality). On Bitcoin, 6 confirmations is the standard.

---

## 15. Finality

### Definition
Finality is the guarantee that a confirmed transaction can never be reversed, altered, or removed from the blockchain. Different chains achieve this differently — and some never achieve absolute finality.

### Real-World Dev Example
On Ethereum PoS, you can check if a block has been finalized before releasing goods in a payment contract:

```js
const block = await provider.getBlock("finalized");
console.log("Finalized block:", block.number);
// Only blocks at or below this height are irreversible
```

### ASCII Diagram
```
PoW (Probabilistic):          PoS Ethereum (Economic):
[B1][B2][B3]...[B100]        [B1][B2]...[B32] → FINALIZED
  ↑ harder to revert as        (requires destroying 1/3 of
  more blocks pile on top       all staked ETH to reverse)
```

### Gotchas & Dev Context
- **Probabilistic finality** (Bitcoin/PoW): the more confirmations, the less likely a reorg — but never 100%.
- **Economic finality** (Ethereum PoS): reversing a finalized block requires slashing >⅓ of all validators — billions of dollars of ETH.
- **Absolute/instant finality** (Tendermint/Cosmos): finalized in one round; no forks after consensus.
- Ethereum finalizes in ~2 epochs = ~12.8 minutes. For most dApps, 1–2 block confirmations is "good enough."
- The `"finalized"` block tag in Ethereum JSON-RPC is safer than `"latest"` for mission-critical reads.

### Production FAQ
**Q: Should I use the `"latest"` or `"finalized"` block tag when querying balances for settlement?**
A: Use `"finalized"` for settlement to avoid reading state that could be reversed. Use `"latest"` only for real-time UX.

**Q: Does Solana have finality?**
A: Yes — Solana uses "confirmed" (~400ms) and "finalized" (~32 slots, ~13s). Use "finalized" for irreversible guarantees.

---

## 16. Fork (Soft Fork, Hard Fork)

### Definition
A fork is a change to a blockchain's protocol rules. A **soft fork** is backward-compatible (old nodes still work). A **hard fork** is not — nodes must upgrade or they follow a separate chain.

### Real-World Dev Example
- **Soft fork**: Bitcoin's SegWit (2017) — old nodes saw SegWit transactions as valid (they just didn't understand the witness data).
- **Hard fork**: Ethereum Classic (2016) — the DAO hack response split Ethereum into ETH and ETC because not everyone agreed.

### ASCII Diagram
```
Soft Fork:                    Hard Fork:
                              
[Old] ─── [Old] ─┐           [ETH]─[ETH]─[ETH]──→ (Ethereum)
                  │             ↑
[New] ─── [New] ─┘           [ETC]─[ETC]─[ETC]──→ (Ethereum Classic)
(one chain, all valid)        (two separate chains)
```

### Gotchas & Dev Context
- Hard forks require ecosystem coordination — wallets, exchanges, and dApps must all upgrade.
- After a hard fork, your private keys work on BOTH chains — be careful of replay attacks unless the new chain implements replay protection (different chainId).
- Ethereum's major upgrades (Merge, Shanghai, Dencun) were all hard forks coordinated via scheduled block height/slot.
- "Fork" also informally means copying a GitHub repo — don't confuse the two in blockchain conversations.

### Production FAQ
**Q: My wallet shows the same balance on two chains after a hard fork. Can I spend both?**
A: Yes, but beware replay attacks. A transaction signed for one chain might be valid on the other. Always use a chain that implements EIP-155 replay protection.

**Q: How do I deploy my dApp to survive a network hard fork?**
A: Specify `chainId` in your ethers.js provider and contract calls. Monitor governance proposals so you can update your frontend in time.

---

## 17. Immutability

### Definition
Immutability means that once data is written to the blockchain, it cannot be changed or deleted — ever. Every transaction in history is permanently preserved.

### Real-World Dev Example
A bug in a deployed Solidity contract cannot be "patched" — the bytecode at that address is frozen. You must deploy a new contract and migrate users (or use an upgradeable proxy pattern beforehand).

```solidity
// Proxy pattern for upgradeable contracts (EIP-1967)
// The proxy's address is permanent; the logic contract can be swapped
contract TransparentUpgradeableProxy {
    address implementation; // can be updated by admin
    // all calls are delegated to implementation
}
```

### Gotchas & Dev Context
- Immutability ≠ uncrackable — a bug in your contract logic is also permanent. Audit before deploying.
- The `SELFDESTRUCT` opcode could remove contract code (deprecated post-Dencun EIP-6049), but transaction history remains.
- On-chain data (including private values) is public forever — never store passwords, secrets, or PII on-chain.
- "Upgradeability" patterns (proxies) work around immutability at the logic level but the proxy address stays the same.
- Storing illegal content on-chain is a real legal risk that some jurisdictions are grappling with.

### Production FAQ
**Q: I found a critical bug in my deployed contract. What do I do?**
A: Pause the contract (if you built in a pause mechanism), deploy a fixed version, and migrate. This is why upgradeable proxy patterns and circuit breakers are production best practices.

**Q: Is immutability a good thing or a bad thing?**
A: Both. It guarantees no one can alter history (good for trust), but it also means bugs are permanent (bad for mistakes). Smart contract audits exist precisely because of this.

---

## 18. Peer-to-Peer (P2P) Network

### Definition
A peer-to-peer (P2P) network is a system where each participant (peer) communicates directly with other peers — with no central server coordinating messages. Every node is both a client and a server.

### Real-World Dev Example
When you broadcast a transaction using ethers.js, your provider sends it to one or more Ethereum nodes, which then gossip it to their peers until the entire network knows about it.

```js
// Broadcasting a tx — it propagates via P2P gossip
const tx = await wallet.sendTransaction({ to: recipient, value: amount });
// Your node tells ~10 peers, each tells ~10 more...
```

### ASCII Diagram
```
      [Node A]─────[Node B]
        │  ╲           │
        │   ╲       [Node C]
     [Node D] ╲      /
               [Node E]
  (no central server — all peers)
```

### Gotchas & Dev Context
- Ethereum uses the **devp2p** protocol (and libp2p for the consensus layer) for node discovery and communication.
- P2P networks are resilient — removing any node doesn't break the network.
- Transaction propagation isn't instant — it can take 1–3 seconds to reach most nodes via gossip.
- Eclipse attacks: a malicious actor surrounds your node with adversarial peers, feeding you false data. Running multiple connections to known nodes mitigates this.

### Production FAQ
**Q: What if my transaction doesn't propagate and no one mines it?**
A: Re-broadcast it. If you're using a provider like Infura, they handle rebroadcasting. If running a private node, use `eth_sendRawTransaction` again.

**Q: How many peers does an Ethereum node connect to?**
A: Typically 25–50 peers by default (configurable). More peers = better propagation but more bandwidth.

---

## 19. Mempool

### Definition
The mempool (memory pool) is a waiting room of unconfirmed transactions. Nodes hold valid transactions here until a miner/validator picks them up and includes them in a block.

### Real-World Dev Example
When gas prices spike (e.g., during an NFT mint), the mempool floods. You can monitor it to detect congestion and set an appropriate gas price.

```js
// Watch pending transactions in ethers.js
provider.on("pending", (txHash) => {
  provider.getTransaction(txHash).then(console.log);
});

// Or use Alchemy/Mempool-specific APIs
// GET https://mempool.space/api/mempool (Bitcoin)
```

### ASCII Diagram
```
User sends TX
     ↓
[MEMPOOL] ← unconfirmed, ordered by gas fee
  TX_A (100 gwei) ← mined first (high fee)
  TX_B (80 gwei)
  TX_C (5 gwei)  ← waits (low fee)
     ↓
 Validator picks top-fee TXs → Block
```

### Gotchas & Dev Context
- **Mempool is public** — anyone can see pending transactions. This enables front-running and MEV (Miner Extractable Value).
- A transaction dropped from the mempool (e.g., after a node restart) must be rebroadcast.
- Each node has its own mempool — they're not perfectly synchronized, but they share data via gossip.
- Use **Flashbots** or **private mempools** (e.g., MEV Blocker) to hide sensitive transactions from bots.
- `maxFeePerGas` and `maxPriorityFeePerGas` (EIP-1559) determine your position in the queue.

### Production FAQ
**Q: My transaction has been in the mempool for hours. Will it ever get mined?**
A: Eventually, if gas prices drop to your set level. Or you can speed it up by resubmitting with the same nonce and a higher gas fee.

**Q: Can MEV bots copy and front-run my transaction from the mempool?**
A: Yes — this is a real risk for DEX trades, liquidations, and arbitrage. Use slippage protection and consider private transaction services like Flashbots Protect.

---

## 20. State vs History

### Definition
**History** is the immutable log of all past transactions. **State** is the current snapshot of all accounts and contract storage — the present outcome after applying all historical transactions.

### Real-World Dev Example
When you call `balanceOf(address)` on an ERC-20 contract, you're reading **state** (current balance). When you look at Transfer events, you're reading **history** (the record of past transfers that produced this balance).

```js
// Reading STATE (current)
const balance = await token.balanceOf(userAddress);

// Reading HISTORY (past events)
const transfers = await token.queryFilter(
  token.filters.Transfer(null, userAddress),
  fromBlock,
  toBlock
);
```

### ASCII Diagram
```
HISTORY (append-only log):
[TX: Alice→Bob 10] [TX: Bob→Carol 5] [TX: Carol→Alice 2]

STATE (current snapshot):
Alice: 92 ETH | Bob: 5 ETH | Carol: 3 ETH
(derived from replaying all history from genesis)
```

### Gotchas & Dev Context
- State is stored in the state trie (Merkle Patricia Trie) — its root (`stateRoot`) is in each block header.
- History is stored in block bodies — every full node has it, but only archive nodes expose historical state.
- Deleting state is impossible without a hard fork. "State bloat" is a real scalability concern — Ethereum's state grows with every new contract and account.
- `eth_call` at a past block requires archive-node access — it replays state to that block height.
- EIP-4444 (History Expiry) proposes that full nodes can eventually prune old history — archive nodes would become more important.

### Production FAQ
**Q: My contract emits events — is that history or state?**
A: History. Events (logs) are stored in transaction receipts — they're part of the historical record but are NOT accessible from within smart contracts via `SLOAD`. They're off-chain queryable only.

**Q: Why does my indexer (The Graph) slow down on historical queries but fast on current state?**
A: Indexers read history (events) to build a queryable state. Heavy historical queries require replaying many blocks. Current-state reads from the subgraph's database are much faster since they're pre-indexed.

---

*End of Batch 1 — Blockchain Fundamentals*
