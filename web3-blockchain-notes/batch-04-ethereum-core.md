# Batch 4 — Ethereum Core
> Understanding Ethereum's engine before writing a single line of Solidity.

---

## 1. Ethereum

**One-line definition:** A programmable blockchain that lets developers deploy and run code (smart contracts) in a decentralized, trustless environment.

### Real-World Dev Example
You deploy a crowdfunding contract to Ethereum. Anyone in the world can send ETH to it, and the contract automatically refunds everyone if the goal isn't met — no PayPal, no bank, no middleman.

### ASCII Diagram
```
Bitcoin:       [Send value A → B]

Ethereum:      [Send value A → B]
               [Run code A → Contract → B, C, D...]
               [Store state on-chain forever]
```

### Gotchas & Dev Context
- Ethereum is **Turing-complete** — it can compute anything, but computation costs gas (see §5).
- The native currency is **ETH (Ether)**, not "Ethereum."
- Ethereum is not a database — storing data on-chain is expensive; use it only for state that needs trustlessness.
- As of **The Merge (2022)**, Ethereum uses Proof of Stake, not Proof of Work.

### Production FAQ
**Q: Can I run Ethereum code off-chain to save fees?**
A: Yes — use Layer 2 rollups (Arbitrum, Optimism) that execute off-chain but post proofs/data to Ethereum for security.

**Q: Is Ethereum the same as ETH?**
A: No. Ethereum is the network/protocol; ETH is the token used to pay for computation on it.

---

## 2. Ethereum Virtual Machine (EVM)

**One-line definition:** The sandboxed, deterministic runtime engine that executes smart contract code on every Ethereum node identically.

### Real-World Dev Example
Think of the EVM as a universal Java Virtual Machine (JVM) — every node runs the same bytecode and must arrive at the exact same output, enforcing consensus.

### ASCII Diagram
```
Solidity code (.sol)
        │
        ▼
   [Compiler: solc]
        │
        ▼
   EVM Bytecode (hex)
        │
        ▼
┌───────────────────┐
│       EVM         │  ← runs on every node
│  Stack (1024)     │
│  Memory (temp)    │
│  Storage (perm)   │
└───────────────────┘
        │
        ▼
   New World State
```

### Gotchas & Dev Context
- EVM is **stack-based**, not register-based — max stack depth is 1024.
- Memory is wiped after each call; storage persists forever (and costs much more gas).
- EVM isolation means a buggy contract can't crash the node — it just reverts.
- Many chains (Polygon, Avalanche, BSC) are **EVM-compatible**, so your Solidity code runs there too.

### Production FAQ
**Q: Why does everyone target EVM compatibility?**
A: It inherits Ethereum's tooling ecosystem (Hardhat, Foundry, MetaMask, ethers.js) instantly.

**Q: Can the EVM run any language?**
A: Any language that compiles to EVM bytecode — Solidity, Vyper, Yul, and others.

---

## 3. EVM Bytecode

**One-line definition:** The low-level hexadecimal instruction set that the EVM actually executes — what your Solidity compiles down to.

### Real-World Dev Example
```solidity
// Solidity
function add(uint a, uint b) public pure returns (uint) {
    return a + b;
}
```
Compiles to something like: `6080604052...` — a sequence of opcodes encoded as bytes.

### ASCII Diagram
```
Solidity (human-readable)
         ↓  solc
Bytecode: 0x6001600201  (hex)
         ↓  decode
Opcodes:  PUSH1 0x01 | PUSH1 0x02 | ADD
```

### Gotchas & Dev Context
- Bytecode is split into **creation code** (runs once on deploy) and **runtime code** (stored on-chain, runs on every call).
- You can verify a contract by recompiling source and matching the resulting bytecode — Etherscan does this.
- **Bytecode != ABI.** The ABI is a JSON description of the interface; bytecode is the actual machine code.
- Decompilers like Dedaub or Panoramix can partially reverse-engineer bytecode when source isn't verified.

### Production FAQ
**Q: Why is my deployed bytecode different from what solc outputs locally?**
A: Compiler version, optimization settings, and metadata hashes all affect output. Always pin your exact `solc` version.

**Q: Can I deploy bytecode directly without Solidity?**
A: Yes — useful for gas-optimized contracts written in Huff or raw assembly (Yul).

---

## 4. Opcodes

**One-line definition:** The individual atomic instructions the EVM understands — like assembly instructions for the Ethereum computer.

### Real-World Dev Example
The opcode `SSTORE` writes a value to contract storage. Every time you update a mapping in Solidity, `SSTORE` runs under the hood — and it's one of the most expensive opcodes (~20,000 gas).

### Common Opcodes
| Opcode   | Hex  | What it does              |
|----------|------|---------------------------|
| `PUSH1`  | 0x60 | Push 1 byte onto stack    |
| `ADD`    | 0x01 | Pop 2 values, push sum    |
| `SSTORE` | 0x55 | Write to contract storage |
| `SLOAD`  | 0x54 | Read from contract storage|
| `CALL`   | 0xF1 | Call another contract     |
| `REVERT` | 0xFD | Abort and refund gas      |

### Gotchas & Dev Context
- Opcodes are the reason gas costs vary — each has a fixed gas cost defined in the [Ethereum Yellow Paper](https://ethereum.github.io/yellowpaper/paper.pdf).
- EIPs can reprice opcodes (e.g., EIP-2929 made `SLOAD` more expensive to prevent DoS).
- In Yul/assembly blocks in Solidity, you write opcodes directly — useful for gas golf.

### Production FAQ
**Q: Where do I find the full opcode list and costs?**
A: The [EVM Codes](https://www.evm.codes/) site is the go-to reference with costs, stack effects, and examples.

**Q: Can new opcodes be added?**
A: Yes, via EIPs — e.g., EIP-1153 added `TSTORE`/`TLOAD` (transient storage) in Cancun (2024).

---

## 5. Gas

**One-line definition:** The unit that measures computational work in Ethereum — every operation costs gas, preventing infinite loops and spam.

### Real-World Dev Example
Calling a simple `transfer()` costs ~21,000 gas. Running a complex DeFi swap might cost 150,000–300,000 gas. Gas is the "fuel" your transaction burns.

### ASCII Diagram
```
Transaction submitted
        │
        ▼
   [EVM executes opcodes]
   ADD     →  3 gas
   SSTORE  →  20,000 gas
   CALL    →  700 gas
        │
        ▼
   Total gas used: 21,203
        │
   ┌────┴─────────────┐
   │ Refund leftover  │  ← unused gas returned
   └──────────────────┘
```

### Gotchas & Dev Context
- Gas is **not ETH** — it's a unit of work. ETH cost = gas used × gas price.
- Out-of-gas → entire transaction reverts, but you still pay for gas already consumed.
- Writing to storage (`SSTORE`) dominates gas costs in most contracts — optimize it first.
- Gas is what stops the halting problem: the EVM can't loop forever if gas runs out.

### Production FAQ
**Q: If my tx reverts, do I get my gas back?**
A: No. Gas pays for computation performed before the revert. Only unused gas is refunded.

**Q: How do I estimate gas before sending a tx?**
A: Use `eth_estimateGas` RPC call or tools like Hardhat's gas reporter plugin.

---

## 6. Gas Limit

**One-line definition:** The maximum amount of gas a sender is willing to spend on a transaction — a safety cap to prevent runaway costs.

### Real-World Dev Example
You set `gasLimit: 100000` when calling a contract. If the contract uses 80,000 gas, you pay for 80,000. If it tries to use 120,000, it hits the limit, reverts, and you pay for 100,000 — you still lose the gas.

### ASCII Diagram
```
gasLimit = 100,000
             │
   ┌──────────▼──────────┐
   │  EVM starts running  │
   │  ... 80,000 gas used │ ✅ success — 20,000 refunded
   └──────────────────────┘

   ┌──────────▼──────────┐
   │  EVM starts running  │
   │  ... 100,001 used    │ ❌ OUT OF GAS — revert, 100,000 lost
   └──────────────────────┘
```

### Gotchas & Dev Context
- There is also a **block gas limit** — the maximum total gas all transactions in one block can consume (currently ~30M gas).
- Setting gasLimit too low = failed tx. Too high = overpaying (but you only pay what's used, minus refund).
- Wallets like MetaMask auto-estimate, but complex interactions may need manual overrides.
- Miners/validators won't include txs with gasLimit higher than the block gas limit.

### Production FAQ
**Q: Should I always set a high gas limit to be safe?**
A: You only pay for what you use, so setting it high is generally fine — but some wallets warn users with very high limits. Estimate precisely in production.

**Q: Who sets the block gas limit?**
A: Validators vote to adjust it gradually. It's a protocol-governed parameter, not fixed.

---

## 7. Gas Price (Gwei)

**One-line definition:** How much ETH you pay per unit of gas — denominated in Gwei (1 Gwei = 0.000000001 ETH).

### Real-World Dev Example
```
Gas used:    21,000
Gas price:   20 Gwei
Total cost:  21,000 × 20 Gwei = 420,000 Gwei = 0.00042 ETH
```

### Gwei Denominations
```
1 ETH = 1,000,000,000 Gwei (10^9)
1 Gwei = 1,000,000,000 Wei (10^9)
1 ETH = 10^18 Wei
```

### Gotchas & Dev Context
- Before EIP-1559, you set a single `gasPrice`. Post EIP-1559, you set `maxFeePerGas` and `maxPriorityFeePerGas` instead.
- During network congestion (NFT mint events, token launches), gas prices can spike 10–100×.
- Tools: [Etherscan Gas Tracker](https://etherscan.io/gastracker) and [blocknative.com](https://www.blocknative.com/) for live estimates.
- On L2s (Arbitrum, Optimism), gas prices are a fraction of Ethereum mainnet.

### Production FAQ
**Q: What's a "safe" gas price to use?**
A: It depends on urgency. "Slow" (<5 min) is cheapest; "fast" (<30s) costs more. Always check a gas tracker for current conditions.

**Q: Can I get my tx included with 0 gas price?**
A: No. Validators won't include free txs (they need economic incentive). Some L2s have near-zero gas, but not zero.

---

## 8. Base Fee / Priority Fee (EIP-1559)

**One-line definition:** EIP-1559 split gas pricing into a **base fee** (burned, set by the protocol) and a **priority fee** (tip paid to the validator).

### Real-World Dev Example
```
maxFeePerGas:         100 Gwei   ← your absolute ceiling
maxPriorityFeePerGas:  2 Gwei   ← tip to validator
Base fee (protocol):  90 Gwei   ← burned

You pay: 90 + 2 = 92 Gwei/gas
Refund:  100 - 92 = 8 Gwei/gas  ← returned to you
```

### ASCII Diagram
```
Your ETH payment per gas:
┌───────────────┬─────────────┐
│   Base Fee    │  Priority   │
│  (🔥 burned) │  Fee (tip)  │
└───────────────┴─────────────┘
    goes to 0x0    → validator
```

### Gotchas & Dev Context
- Base fee adjusts **automatically** — up 12.5% if last block was full, down 12.5% if empty.
- The burn mechanism makes ETH deflationary during high usage periods.
- Legacy txs (type 0) still work but are converted internally — avoid them in new code.
- Setting `maxFeePerGas` too low during a spike = tx sits pending until fees drop or you cancel.

### Production FAQ
**Q: Why burn the base fee instead of giving it to validators?**
A: To remove the incentive for validators to artificially inflate block usage to collect higher fees — it stabilizes fee markets.

**Q: How do I cancel a pending stuck transaction?**
A: Send a new tx with the same nonce, higher `maxPriorityFeePerGas`, and zero value to replace it.

---

## 9. Transaction Types (Legacy, EIP-1559, EIP-4844)

**One-line definition:** Ethereum has evolved its transaction format three times — each type is a versioned envelope with different fields and purposes.

### Types at a Glance
| Type | EIP | Key Fields | Use |
|------|-----|-----------|-----|
| **Type 0** | Legacy | `gasPrice` | Old-style txs |
| **Type 1** | EIP-2930 | + `accessList` | Pre-warm storage |
| **Type 2** | EIP-1559 | `maxFeePerGas`, `maxPriorityFeePerGas` | Standard post-London |
| **Type 3** | EIP-4844 | + `blobVersionedHashes`, `maxFeePerBlobGas` | L2 data blobs |

### ASCII Diagram
```
[Type 0]  nonce | gasPrice | gas | to | value | data | v | r | s
[Type 2]  chainId | nonce | maxPriorityFeePerGas | maxFeePerGas | gas | to | value | data | ...
[Type 3]  (Type 2 fields) + blobVersionedHashes + blob sidecar
```

### Gotchas & Dev Context
- Type 2 is the **default** you should use in production today.
- Type 1 exists mainly to help contracts pre-declare storage slots they'll access (cheaper reads).
- Type 3 (blobs) are only meaningful for L2 sequencers posting rollup data — don't use them for regular dapp txs.
- `chainId` in Type 2+ prevents replay attacks across chains.

### Production FAQ
**Q: Does ethers.js automatically use Type 2?**
A: Yes — ethers v6 defaults to EIP-1559 txs on supported networks.

**Q: Will Type 0 transactions eventually be deprecated?**
A: Not imminently, but Type 2 is strongly preferred. Some newer tooling may drop Type 0 support over time.

---

## 10. Accounts (EOA vs Contract Account)

**One-line definition:** Ethereum has two account types — **EOA** (Externally Owned Account, controlled by a private key) and **Contract Account** (controlled by code).

### Comparison Table
| Property          | EOA                  | Contract Account        |
|-------------------|----------------------|-------------------------|
| Controlled by     | Private key          | Code (bytecode)         |
| Can initiate tx   | ✅ Yes               | ❌ No (must be called)  |
| Has code          | ❌ No                | ✅ Yes                  |
| Has storage       | ❌ No                | ✅ Yes                  |
| Address derived from | Public key        | Deployer address + nonce|

### ASCII Diagram
```
User (EOA)
  │  signs tx
  ▼
Ethereum Network
  │
  ├──► ETH transfer → another EOA  (simple send)
  └──► Contract call → Contract Account
              │
              └──► runs code, may call other contracts
```

### Gotchas & Dev Context
- EOAs pay gas; contracts don't initiate — every tx chain starts from an EOA.
- EIP-4337 (Account Abstraction) blurs this boundary — lets contracts behave like wallets.
- A contract account's address is deterministic: `keccak256(rlp([sender, nonce]))[12:]`.
- Sending ETH to a contract without a `receive()` function will revert.

### Production FAQ
**Q: Can a contract call another contract?**
A: Yes — via `CALL`, `DELEGATECALL`, or `STATICCALL` opcodes. But the gas must originate from an EOA tx.

**Q: What's `CREATE2` and why does it matter?**
A: It deploys contracts to a deterministic address based on salt + bytecode — used in counterfactual deployments (e.g., Uniswap v3 pairs).

---

## 11. Nonce (Account Nonce vs Block Nonce)

**One-line definition:** A counter that prevents replay attacks — **account nonce** orders an EOA's transactions; **block nonce** (legacy PoW) was a mining puzzle answer.

### Real-World Dev Example
Your wallet nonce starts at 0. First tx = nonce 0, second tx = nonce 1. If you try to replay tx #0 on the same chain, it fails — nonce already used.

### ASCII Diagram
```
EOA Account State:
┌──────────────────────────┐
│ Address: 0xABC...        │
│ Balance: 1.5 ETH         │
│ Nonce:   7  ← next tx    │
│             must be 7    │
└──────────────────────────┘

Block (PoW, legacy):
┌──────────────────────────┐
│ ...                      │
│ Nonce: 0x00000000abc123  │ ← miners brute-forced this
└──────────────────────────┘
```

### Gotchas & Dev Context
- Txs are processed **in nonce order** — if nonce 5 is missing, nonces 6, 7, 8 queue up and won't process.
- Stuck pending txs: submit a replacement tx with the **same nonce** but higher priority fee.
- Block nonce is **irrelevant post-Merge** — PoS doesn't use mining nonces.
- Contract accounts also have a nonce (incremented on each `CREATE`/`CREATE2` call).

### Production FAQ
**Q: Can I submit two txs with the same nonce?**
A: Yes — but only one will be included. The one with higher priority fee wins; the other is dropped.

**Q: How do I get my account's current nonce?**
A: `eth_getTransactionCount(address, "pending")` — "pending" includes queued txs not yet mined.

---

## 12. State Trie / Storage Trie / Receipt Trie

**One-line definition:** Ethereum stores all its data in three cryptographic tree structures (Modified Merkle-Patricia Tries) that make state verifiable with a single root hash.

### The Three Tries
| Trie | What it stores | Root in |
|------|---------------|---------|
| **State Trie** | All accounts (balance, nonce, codeHash, storageRoot) | Block header |
| **Storage Trie** | Contract's key-value storage (one per contract) | Account's `storageRoot` |
| **Receipt Trie** | Tx receipts (logs, status, gas used) | Block header |

### ASCII Diagram
```
Block Header
├── stateRoot      ──→ [State Trie]
│                        ├── 0xABC... → {balance, nonce, storageRoot}
│                        │                    └──→ [Storage Trie]
│                        └── 0xDEF... → {balance, nonce, ...}
├── receiptsRoot   ──→ [Receipt Trie]
└── transactionsRoot → [Tx Trie]
```

### Gotchas & Dev Context
- Changing any leaf changes the root hash — enabling **Merkle proofs** (light clients verify state without full data).
- Storage tries are **per contract** — each contract has its own isolated key-value store.
- Tries use **RLP encoding** and keccak256 hashing at each node.
- Ethereum's state trie is massive and growing — state bloat is a core scaling concern.

### Production FAQ
**Q: Why does Ethereum use tries instead of a normal database?**
A: Tries give you a single root hash that cryptographically commits to all state, enabling trustless light client verification.

**Q: What is `eth_getProof`?**
A: An RPC method that returns a Merkle proof for an account/storage slot — used by bridges and light clients to verify state without syncing the full chain.

---

## 13. World State

**One-line definition:** The complete snapshot of all Ethereum accounts and their balances, nonces, code, and storage at a given block — the "current reality" of the chain.

### Real-World Dev Example
After block 20,000,000 is finalized, the world state is a mapping of every address to its account data. The state root in that block header is a hash of this entire map.

### ASCII Diagram
```
World State (at block N):
{
  0xAlice:    { balance: 5 ETH,  nonce: 12, code: ∅ }
  0xBob:      { balance: 2 ETH,  nonce: 3,  code: ∅ }
  0xContract: { balance: 0.1 ETH, nonce: 1,  code: 0x60806..., storage: {...} }
  ...millions more...
}
       ↓ hashed into
   stateRoot = 0x9fA3...
```

### Gotchas & Dev Context
- The world state is **not stored in blocks** — it's derived by replaying all transactions from genesis.
- Clients store a local copy in LevelDB/RocksDB — syncing from scratch is slow (weeks for full sync).
- **Snap sync** (Geth) downloads a recent state snapshot instead of replaying everything.
- EIP-4444 proposes pruning old historical data — clients won't need to store everything forever.

### Production FAQ
**Q: What's the difference between world state and blockchain state?**
A: The blockchain is the log of transactions; the world state is the outcome — think of it as a database vs. a ledger.

**Q: Why can't I just query historical world state cheaply?**
A: Archive nodes store every historical state, but they're large (>20TB). Regular nodes prune old states to save disk.

---

## 14. Ethereum Clients (Geth, Nethermind, Besu, Erigon)

**One-line definition:** Software implementations of the Ethereum protocol that sync the chain, execute transactions, and expose the JSON-RPC API.

### Client Comparison
| Client | Language | Notes |
|--------|----------|-------|
| **Geth** | Go | Reference client, most widely used |
| **Nethermind** | C# | High performance, popular among validators |
| **Besu** | Java | Enterprise-friendly, permissioning features |
| **Erigon** | Go | Optimized for archive nodes, minimal disk usage |

### ASCII Diagram
```
You / dApp
    │  JSON-RPC (eth_call, eth_sendRawTransaction...)
    ▼
[Ethereum Client]  ← syncs with P2P network
    │
    ├── Execution Engine (runs EVM, manages state)
    └── P2P Layer (gossips txs and blocks)
```

### Gotchas & Dev Context
- **Client diversity matters** — if 80% of nodes run Geth and Geth has a bug, the whole network is at risk. Run minority clients.
- Execution clients (above) now work alongside **consensus clients** post-Merge (see §15).
- Hardhat and Foundry run local in-process EVM forks — not a full client, but fine for testing.
- For production RPC, use managed providers (Alchemy, Infura, QuickNode) or run your own node.

### Production FAQ
**Q: Which client should I run as a validator?**
A: A minority client (Nethermind, Besu, Erigon) for safety. If Geth is the supermajority and it faults, minority-client validators stay safe.

**Q: What's an archive node?**
A: A node that stores every historical state, not just the latest. Required for queries like "what was Alice's balance at block 10M?" Erigon is the most disk-efficient archive client.

---

## 15. Execution Layer vs Consensus Layer

**One-line definition:** Post-Merge Ethereum is split into two layers — the **Execution Layer** (runs transactions, EVM) and the **Consensus Layer** (manages validators, PoS finality).

### ASCII Diagram
```
┌────────────────────────────────────────────┐
│           CONSENSUS LAYER (CL)             │
│   Beacon Chain — validators, attestations  │
│   Clients: Prysm, Lighthouse, Teku, Nimbus │
└────────────────────┬───────────────────────┘
                     │ Engine API (local HTTP)
┌────────────────────┴───────────────────────┐
│           EXECUTION LAYER (EL)             │
│   EVM, mempool, state, JSON-RPC            │
│   Clients: Geth, Nethermind, Erigon, Besu  │
└────────────────────────────────────────────┘
```

### Gotchas & Dev Context
- To run a full Ethereum node post-Merge, you must run **both** an EL client and a CL client — they communicate via the Engine API (`engine_newPayloadV*`).
- dApps talk to the EL via JSON-RPC. Validators talk to the CL.
- The CL decides block ordering; the EL executes what the CL tells it.
- This two-client design is a security feature — you need two separate software bugs to compromise a node.

### Production FAQ
**Q: Does my dApp need to care about the CL?**
A: Generally no. Your dApp hits EL endpoints (`eth_call`, `eth_sendRawTransaction`). The CL is invisible to application developers.

**Q: What is the Engine API?**
A: A private JSON-RPC interface (authenticated with JWT) that CL clients use to instruct EL clients to execute new blocks.

---

## 16. Beacon Chain

**One-line definition:** The Proof of Stake coordination chain that manages Ethereum's validator registry, randomness, and block finality — launched December 2020.

### Real-World Dev Example
Think of the Beacon Chain as the "parliament" that organizes when each validator gets to propose a block. It uses RANDAO (random number protocol) to fairly assign duties.

### ASCII Diagram
```
Time →  [Slot 1] [Slot 2] [Slot 3] ... [Slot 32]
                                              ↕
                                          [Epoch 1]

Each Slot (~12 sec):
  - One validator proposes a block
  - Committee of validators attests (votes) on it

Each Epoch (32 slots, ~6.4 min):
  - Finality checkpoint considered
  - Validator rewards/penalties computed
```

### Gotchas & Dev Context
- Validators must stake exactly **32 ETH** to participate.
- Slots and epochs replace "block time" as the temporal unit on Ethereum.
- **Finality** occurs after 2 epochs (~12.8 min) — before that, blocks can theoretically be reorged.
- `block.timestamp` in Solidity aligns with slot timing (~12s intervals).

### Production FAQ
**Q: What happens if a validator goes offline?**
A: They receive small **inactivity penalties** proportional to how long they're offline. No slash unless they double-vote.

**Q: What is slashing?**
A: A severe penalty (minimum 1 ETH, up to full 32 ETH) for provably malicious behavior — like signing two conflicting blocks at the same slot.

---

## 17. The Merge

**One-line definition:** The September 15, 2022 event where Ethereum's Proof of Work execution chain merged with the Proof of Stake Beacon Chain, eliminating mining forever.

### Real-World Dev Example
Before the Merge: GPU miners raced to solve puzzles to add blocks. After the Merge: 32-ETH stakers are randomly selected. Energy usage dropped ~99.95%.

### ASCII Diagram
```
Pre-Merge:
[PoW Chain] ← miners extend this
[Beacon Chain] ← validators run in parallel

The Merge (Terminal Total Difficulty reached):
[PoW Chain] ──────────────────────────────►
                                           ↓
                              [Beacon Chain takes over]
                              ← validators extend this now

Post-Merge:
[Beacon Chain] ← validators propose & attest to blocks
[EL] ← still runs EVM, unchanged from user's perspective
```

### Gotchas & Dev Context
- From a **developer perspective**, almost nothing changed — same JSON-RPC, same Solidity, same tooling.
- `DIFFICULTY` opcode was repurposed as `PREVRANDAO` (randomness from the beacon chain) — don't use it as a secure random source.
- ETH issuance dropped ~90% post-Merge (no miner block rewards).
- The Merge did NOT reduce gas fees — that's a Layer 2 problem.

### Production FAQ
**Q: Did the Merge affect smart contract behavior?**
A: Minimally. The main breaking change: `block.difficulty` now returns `block.prevrandao` — a weak randomness source that can be influenced by validators.

**Q: Where did miners go?**
A: Many migrated to other PoW chains (Ethereum Classic, Ravencoin) or exited the market.

---

## 18. Blob Transactions (EIP-4844 / Proto-Danksharding)

**One-line definition:** A new transaction type (Type 3) introduced in the Cancun upgrade (March 2024) that lets L2s post large data chunks ("blobs") to Ethereum cheaply, without storing them in the EVM.

### Real-World Dev Example
Before EIP-4844: Arbitrum posted compressed rollup data as calldata — expensive (~16 gas/byte). After EIP-4844: same data goes in a blob — ~10–100× cheaper. L2 fees for users dropped dramatically overnight.

### ASCII Diagram
```
Type 3 Transaction:
┌──────────────────────────────────────────┐
│  Standard tx fields (to, value, data...) │
│  + blobVersionedHashes[]: [0x01ba...]    │
│  + maxFeePerBlobGas                      │
└──────────────────────────────────────────┘
         │                  │
         ▼                  ▼
   Executed by EVM    Blob sidecar
   (on-chain)         (consensus layer, ~4096 field elements)
                       deleted after ~18 days
```

### Gotchas & Dev Context
- Blobs are **NOT accessible by the EVM** — you can't `SLOAD` blob data. Only the hash is on-chain.
- Blobs are pruned after ~18 days — not permanent storage. L2s must make their own data availability guarantees.
- Each blob is ~128 KB; currently up to 6 blobs/block (target: 3).
- A separate `blobBaseFee` market governs blob pricing, independent of regular gas.

### Production FAQ
**Q: Should regular dApp developers use blobs?**
A: No. Blobs are for L2 sequencers. If you need cheap data availability, use an L2 — it'll use blobs on your behalf.

**Q: How do I access blob data if it's not in the EVM?**
A: From the consensus layer — via the Beacon API (`/eth/v1/beacon/blob_sidecars/{block_id}`). Archival blob data is available from services like Blobscan.

---

## 19. Danksharding (Full)

**One-line definition:** The long-term Ethereum scaling roadmap that extends Proto-Danksharding (EIP-4844) to support massive blob capacity (~64 blobs/block) and Data Availability Sampling (DAS) — enabling ETH to scale to thousands of TPS via L2s.

### Real-World Dev Example
Today (proto-danksharding): 3–6 blobs/block, ~0.375–0.75 MB of cheap data. Full danksharding: ~64 blobs/block, ~8 MB/block — enough for hundreds of L2 rollups to post data simultaneously.

### ASCII Diagram
```
Proto-Danksharding (now):
Block → [ 3-6 blobs ] ← each node downloads all

Full Danksharding (future):
Block → [ 64 blobs ]
              │
    ┌─────────┴─────────┐
    │  Data Availability │
    │  Sampling (DAS)    │
    └────────────────────┘
    Each node downloads only a RANDOM SAMPLE
    of blob chunks — if enough nodes sample,
    the whole blob is proven available
    without anyone downloading everything.
```

### Key Concepts
| Concept | Meaning |
|---------|---------|
| **DAS** | Nodes verify data is available by sampling random chunks, not downloading all |
| **KZG Commitments** | Cryptographic proof that blobs match their hashes (polynomial commitments) |
| **Builder/Proposer Separation** | Specialized block builders handle large blobs; validators just propose |
| **PeerDAS** | Distributed version of DAS across the P2P network |

### Gotchas & Dev Context
- Full Danksharding is **years away** — the roadmap is: proto-danksharding → PeerDAS → full danksharding.
- KZG commitments require a trusted setup — Ethereum ran "The KZG Ceremony" in 2023 (140,000+ contributors).
- DAS is what allows even light nodes to verify data availability — a massive trust improvement for L2 users.

### Production FAQ
**Q: Do L2s need to change anything for full danksharding?**
A: Mostly not — they'll automatically get more blob space. The L2 sequencer may need to batch more aggressively to fill blobs optimally.

**Q: Why use KZG commitments instead of Merkle proofs for blobs?**
A: KZG proofs are much smaller and constant-size regardless of data size, making DAS sampling more bandwidth-efficient.

---

*End of Batch 4 — Ethereum Core*
