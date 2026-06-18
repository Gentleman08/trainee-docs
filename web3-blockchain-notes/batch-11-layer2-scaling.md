# Batch 11 — Layer 2 & Scaling
> Making blockchains fast and cheap without sacrificing decentralization.

Layer 2 is the umbrella term for any system built *on top of* an existing blockchain to increase throughput and cut costs. This batch covers every major scaling approach you'll encounter in production Web3 development.

---

## 1. Layer 1 vs Layer 2

**Definition:** Layer 1 (L1) is the base blockchain (Ethereum, Bitcoin). Layer 2 (L2) is a separate system that processes transactions off the main chain and periodically posts results back to L1.

### Real-World Dev Example
Your dApp deploys on Arbitrum (L2). Users pay ~$0.01/tx instead of Ethereum's ~$2–10. Arbitrum batches thousands of those transactions and posts one compressed summary to Ethereum every few minutes.

```
L2 (Arbitrum)  →  batch tx data  →  L1 (Ethereum)
   cheap & fast                       slow & secure
```

### Gotchas & Dev Context
- L2 **inherits L1 security** — that's the point. Sidechains don't (see §11).
- Withdrawing from L2 to L1 takes time (7 days on Optimistic Rollups).
- L1 is the final **settlement layer**; L2 is the **execution layer**.
- Not all "L2s" are equal — some are sidechains marketed as L2.

### Production FAQ
**Q: Can I deploy any Ethereum contract on an L2?**
A: Almost always yes — most L2s are EVM-compatible. Edge cases: gas cost differences can break contracts with hardcoded gas limits.

**Q: What happens if an L2 goes down?**
A: Users can typically force-exit funds directly through L1 contracts. True L2s guarantee this; custodial chains don't.

---

## 2. Rollups (Optimistic vs ZK)

**Definition:** A rollup bundles (rolls up) many transactions into one batch, executes them off-chain, and posts the compressed data + a proof to L1.

### Real-World Dev Example
Think of rollups like a restaurant submitting one summarized end-of-day report to the health inspector instead of logging every single meal. L1 only stores the report; the rollup keeps the receipts.

```
100 tx   →  [Rollup Engine]  →  1 batch tx on L1
$200 gas                        $2 gas (split 100 ways)
```

### Gotchas & Dev Context
- Two flavors: **Optimistic** (assume valid, challenge if wrong) and **ZK** (prove valid immediately with math).
- Both post **calldata / blobs** to L1 for data availability.
- Gas savings come from **compression** + **amortization** across users.
- Rollups need a **sequencer** to order transactions (see §6).

### Production FAQ
**Q: Which rollup type is better?**
A: ZK rollups have faster finality and stronger security guarantees. Optimistic rollups are easier to build EVM-compatible systems on — though ZK-EVMs are closing this gap fast.

**Q: Do rollups increase L1 congestion?**
A: No — they reduce it. EIP-4844 introduced "blobs" specifically to give rollups a cheaper lane (see §17).

---

## 3. Optimistic Rollups (Arbitrum, Optimism, Base)

**Definition:** An optimistic rollup assumes all submitted transactions are valid ("optimistic") and only runs verification if someone files a fraud proof within a challenge window.

### Real-World Dev Example
Arbitrum One posts batches to Ethereum. During the 7-day challenge window, any validator can submit a **fraud proof** if they detect a bad state transition. After 7 days, the batch is final.

```
Sequencer posts batch
       ↓
  7-day window open
       ↓
  No challenge? → FINALIZED on L1
  Challenge?    → Fraud proof resolves on L1
```

### Gotchas & Dev Context
- **Arbitrum** uses multi-round fraud proofs (cheaper to verify on L1).
- **Optimism (OP Stack)** uses single-round fraud proofs; powers **Base** (Coinbase's L2).
- The 7-day withdrawal delay is a UX pain point — bridges work around it for a fee.
- **OP Stack** is open-source: teams can fork it to launch their own L2 ("OP Chains").

### Production FAQ
**Q: Why 7 days specifically?**
A: It's a practical balance — long enough for a honest validator anywhere on Earth to notice and submit a fraud proof; short enough to remain usable.

**Q: Is Base the same as Optimism?**
A: Base uses the OP Stack (same tech) but is operated by Coinbase. Separate chains, shared tech stack, both settle on Ethereum.

---

## 4. ZK Rollups (zkSync, StarkNet, Polygon zkEVM, Scroll)

**Definition:** A ZK rollup uses **zero-knowledge proofs** to cryptographically prove that all batched transactions are valid — no challenge window needed.

### Real-World Dev Example
zkSync Era posts a batch + a validity proof to Ethereum. Ethereum's smart contract verifies the proof in one transaction. If the proof checks out, the batch is immediately final.

```
Batch executed off-chain
       ↓
ZK proof generated (computationally heavy)
       ↓
Proof verified on L1 → INSTANT finality
```

### Gotchas & Dev Context
- **zkSync Era** and **Scroll** are ZK-EVMs — Solidity works natively.
- **StarkNet** uses Cairo (its own language) — higher performance, steeper learning curve.
- **Polygon zkEVM** aims for full EVM equivalence at the bytecode level.
- Proof generation is CPU/GPU intensive — centralized provers are a current reality.
- Finality is fast (minutes), but on-chain proof verification costs gas.

### Production FAQ
**Q: Do I need to learn Cairo to use StarkNet?**
A: For contracts, yes. But tooling like **Starknet Foundry** and **OpenZeppelin Cairo contracts** make it approachable.

**Q: Why are some ZK-EVMs "Type 1" vs "Type 4"?**
A: Vitalik's ZK-EVM type classification rates how close a ZK-EVM is to full Ethereum equivalence. Type 1 = identical to Ethereum; Type 4 = compiles Solidity to a custom VM (fastest proofs, least compatible).

---

## 5. Fraud Proof vs Validity Proof

**Definition:** A **fraud proof** proves that a state transition was *wrong*. A **validity proof** (ZK proof) proves that a state transition was *correct* — before anyone can dispute it.

### Real-World Dev Example
- **Fraud proof:** Like a bank statement audit. Assume it's correct; flag it only if you spot an error.
- **Validity proof:** Like a notarized document. The math signature *proves* correctness upfront.

```
Optimistic:  Post → Wait → [Challenge?] → Resolve
ZK:          Post + Proof → Verify → Done
```

### Gotchas & Dev Context
- Fraud proofs require **at least one honest verifier** watching the chain.
- Validity proofs require **no trust assumptions** — pure math.
- Generating ZK proofs is expensive; verifying them is cheap.
- Optimistic systems are simpler to implement but carry liveness risk (no verifiers online = no security).

### Production FAQ
**Q: What if no one challenges a fraudulent batch on an Optimistic Rollup?**
A: The batch finalizes. This is why the "1-of-N honest verifier" assumption is critical — at least one node must be watching.

**Q: Can validity proofs replace fraud proofs entirely?**
A: That's the industry direction. As ZK proof generation gets cheaper and ZK-EVMs mature, most rollups are expected to migrate to validity proofs.

---

## 6. Sequencer

**Definition:** The sequencer is the node (usually centralized today) that receives user transactions, orders them, and batches them for submission to L1.

### Real-World Dev Example
When you send a tx on Arbitrum, it goes to Arbitrum's sequencer first. The sequencer orders it, gives you instant "soft confirmation," and later posts the batch to Ethereum.

```
User Tx → Sequencer → Ordered Batch → L1 Submission
              ↑
     (centralized today, decentralizing soon)
```

### Gotchas & Dev Context
- Centralized sequencers = **single point of failure** and **MEV extraction** risk.
- If the sequencer goes down, users can still submit txs directly to L1 (escape hatch).
- **Decentralized sequencing** (multiple sequencers, leader rotation) is actively being built — e.g., Espresso, Astria.
- Sequencer order determines **transaction ordering** — front-running is possible.
- "Soft confirmation" from sequencer ≠ L1 finality.

### Production FAQ
**Q: Can the sequencer steal my funds?**
A: No — it can censor or reorder your tx, but fund security is enforced by L1 smart contracts. Worst case: delayed, not stolen.

**Q: What is a shared sequencer?**
A: A sequencer service shared across multiple rollups, enabling atomic cross-rollup transactions. Projects: Espresso Systems, Radius.

---

## 7. Data Availability (DA)

**Definition:** Data availability (DA) guarantees that the transaction data used to produce a block is actually published and retrievable by anyone who needs to verify it.

### Real-World Dev Example
An L2 posts a batch proof to Ethereum. But if the underlying transaction data isn't published anywhere, users can't reconstruct the state or exit their funds. DA ensures the data *is* out there.

```
Proof posted to L1 ✓
Data posted to DA layer ✓  ← both required
         ↓
Anyone can verify + reconstruct state
```

### Gotchas & Dev Context
- **DA ≠ Data Storage.** DA only guarantees data was available at post time, not forever.
- Ethereum calldata / blobs provide DA natively (expensive but very secure).
- Cheaper DA layers (Celestia, EigenDA) trade some security assumptions for cost.
- Rollups without proper DA are called **Validiums** (see §14).
- DA is one of the three pillars of the modular blockchain thesis (Execution / Consensus / DA).

### Production FAQ
**Q: What breaks if DA fails?**
A: Users can't prove their balances, can't exit funds, and the chain state can't be reconstructed. DA failure is catastrophic.

**Q: Does Ethereum itself provide DA for rollups?**
A: Yes — via calldata (legacy) and blobs (post-EIP-4844). Blobs are cheaper and purpose-built for rollup DA.

---

## 8. Data Availability Layer (Celestia, EigenDA, Avail)

**Definition:** A DA layer is a dedicated blockchain or service whose *sole job* is to store and guarantee availability of data — cheaper and more scalable than using Ethereum for this.

### Real-World Dev Example
A rollup posts transaction data to **Celestia** instead of Ethereum. Cost drops by 10–100×. The rollup still settles *proofs* on Ethereum. Celestia only stores the blob data.

```
Rollup Execution
      ↓
Data → Celestia / EigenDA / Avail   (cheap DA)
Proof → Ethereum                     (secure settlement)
```

### Gotchas & Dev Context
- **Celestia:** Uses Data Availability Sampling (DAS) — light nodes verify DA without downloading full data.
- **EigenDA:** Built on EigenLayer restaking — Ethereum validators provide DA, slashable if they lie.
- **Avail:** Polygon-incubated, uses KZG commitments + DAS for DA guarantees.
- Using an external DA layer means you're trusting that DA layer's security model — weaker than Ethereum DA.
- Most "modular rollups" use Celestia + Ethereum settlement.

### Production FAQ
**Q: Is using Celestia for DA safe?**
A: It depends on your security model. Celestia's DA security is strong but different from Ethereum's. For high-value DeFi, Ethereum DA is preferred.

**Q: Can one rollup use multiple DA layers?**
A: Yes — some designs post data to Celestia for cost but retain an Ethereum fallback for critical state roots.

---

## 9. Bridges (Lock & Mint, Burn & Mint)

**Definition:** A bridge moves assets between two separate chains. Two dominant patterns: **Lock & Mint** (lock on source, mint wrapped version on dest) and **Burn & Mint** (burn on source, mint native on dest).

### Real-World Dev Example
Bridging ETH from Ethereum → Arbitrum:
- Your ETH is **locked** in an L1 bridge contract.
- **WETH** (wrapped ETH) is **minted** on Arbitrum.
- To withdraw: WETH burned on Arbitrum → ETH unlocked on Ethereum.

```
Lock & Mint:
  ETH (L1) → LOCK → MINT wETH (L2)
  wETH (L2) → BURN → UNLOCK ETH (L1)
```

### Gotchas & Dev Context
- Bridges are the #1 hack target in crypto — $2B+ lost in bridge exploits.
- Trust assumptions vary: native bridges (rollup's own) are most secure; third-party bridges carry smart contract risk.
- **Canonical bridges** (Arbitrum, Optimism official bridges) have withdrawal delays.
- **Liquidity bridges** (Hop, Across) use LPs to give fast withdrawals — you pay a fee.

### Production FAQ
**Q: Which bridge should I recommend to users?**
A: For small amounts: use the official (canonical) bridge for max security. For speed: reputable liquidity bridges like Across or Stargate.

**Q: Why do bridge hacks happen so often?**
A: Bridges hold massive pooled funds and rely on complex cross-chain message verification. A single contract bug = catastrophic loss.

---

## 10. Cross-Chain Messaging (LayerZero, Axelar, Wormhole)

**Definition:** Cross-chain messaging protocols let smart contracts on Chain A send arbitrary messages (not just tokens) to smart contracts on Chain B.

### Real-World Dev Example
An NFT on Ethereum votes in a DAO on Polygon. LayerZero sends the vote message cross-chain. The Polygon contract receives it and records the vote — no bridge, no token transfer.

```
Contract A (Ethereum)
    ↓ send message via LayerZero
Contract B (Polygon)
    ↓ execute on receive
```

### Gotchas & Dev Context
- **LayerZero:** Uses ultra-light nodes + independent Oracle + Relayer to verify messages.
- **Axelar:** Runs its own validator set (PoS chain) to relay messages — adds a trust layer.
- **Wormhole:** Uses a "Guardian" multisig (19 nodes) to attest cross-chain messages.
- These aren't bridges per se — they're **general message passing (GMP)** layers.
- Security model differs: LayerZero trusts Oracle/Relayer pairs; Wormhole trusts Guardians.

### Production FAQ
**Q: What's the difference between a bridge and a cross-chain messaging protocol?**
A: Bridges move *tokens*. Cross-chain messaging moves *arbitrary data*. Token bridges are often built *on top of* messaging protocols.

**Q: What if the relayer goes down?**
A: Messages are queued — they'll eventually be relayed once the relayer is back. Protocols have retry mechanisms.

---

## 11. Sidechains (Polygon PoS)

**Definition:** A sidechain is a separate blockchain with its own consensus mechanism that runs *alongside* a mainchain, connected via a bridge — but does NOT inherit mainchain security.

### Real-World Dev Example
**Polygon PoS** is a sidechain to Ethereum. It has its own ~100 validators. Assets bridge from Ethereum to Polygon via a lock-and-mint bridge. Polygon blocks are faster and cheaper but rely on Polygon's validator set, not Ethereum's.

```
Ethereum (L1) ←→ Bridge ←→ Polygon PoS (Sidechain)
  Highly secure                 Own consensus, own security
```

### Gotchas & Dev Context
- **Sidechain ≠ L2.** L2s derive security from L1; sidechains don't.
- If Polygon's validators collude, they can steal bridged funds. Ethereum can't stop them.
- Polygon PoS is being progressively upgraded toward a ZK-based L2 (Polygon CDK).
- Sidechains are faster to build and deploy but carry higher trust assumptions.
- EVM-compatible sidechains (Polygon, BNB Chain, Gnosis) are easy to deploy on.

### Production FAQ
**Q: Is Polygon PoS an L2?**
A: Technically, no — it's a sidechain. Polygon itself is rebranding and migrating assets toward zkEVM-based L2s. The PoS chain will remain for now.

**Q: When should I choose a sidechain over a rollup?**
A: When you need ultra-low fees, don't need Ethereum-level security, and want simpler infrastructure. Good for gaming, social apps.

---

## 12. State Channels (Raiden, Lightning)

**Definition:** State channels let two or more parties transact off-chain by locking funds on-chain, exchanging signed state updates locally, and only settling the final state on-chain.

### Real-World Dev Example
Alice and Bob lock 1 ETH each into a channel contract. They send 1,000 micropayments off-chain (just signed messages). At the end, they submit the final balance to the contract — 2 on-chain txs total, 1,000 free off-chain txs.

```
Open channel (1 on-chain tx)
    ↓
Alice ←→ Bob (off-chain signed states, instant)
    ↓
Close channel (1 on-chain tx)
```

### Gotchas & Dev Context
- **Raiden:** Ethereum state channels for ERC-20 tokens.
- **Lightning Network:** Bitcoin state channels for BTC payments.
- Funds must be **locked upfront** — capital inefficient for variable payment amounts.
- Both parties must be **online** to respond to disputes.
- Best use case: high-frequency micropayments between known parties.
- Channels don't scale to arbitrary dApps — limited to predefined state machines.

### Production FAQ
**Q: Can state channels support smart contract logic?**
A: Only logic defined at channel open time. You can't run arbitrary Solidity in a channel.

**Q: What if my counterparty tries to submit an old state?**
A: You have a **dispute window** to submit a newer signed state and penalize the cheater.

---

## 13. Plasma

**Definition:** Plasma is an older L2 framework where child chains process transactions and periodically commit Merkle roots to Ethereum — but users must monitor the chain and exit if fraud is detected.

### Real-World Dev Example
Imagine a Plasma chain for payments. Alice's funds are represented in the Plasma chain. If the Plasma operator tries to steal funds, Alice submits a **Merkle proof** to Ethereum to reclaim her assets via a mass exit.

```
Plasma Chain (fast txs)
      ↓ Merkle root every N blocks
Ethereum (L1)
      ↑ Exit if fraud detected
```

### Gotchas & Dev Context
- Plasma is largely **deprecated** — superseded by rollups.
- Core problem: **data availability.** If the operator withholds data, users can't prove fraud.
- **Mass exit problem:** If everyone exits at once, Ethereum gets congested.
- **Plasma Cash** tried to fix this with non-fungible UTXOs — still too complex.
- Rollups solved Plasma's DA problem by posting all data to L1.

### Production FAQ
**Q: Should I build on Plasma today?**
A: No. Use rollups. Plasma is a historical reference — understanding it helps you appreciate why rollups post data to L1.

**Q: Is OMG Network (now BOBA) still Plasma?**
A: OMG originally used Plasma; it's largely migrated to optimistic rollup architecture.

---

## 14. Validium

**Definition:** A Validium uses ZK validity proofs for computation (like a ZK rollup) but stores transaction data *off-chain* (not on Ethereum) — trading security for lower costs.

### Real-World Dev Example
**StarkEx** (powers dYdX v3, Immutable X) uses Validium mode. ZK proofs guarantee correct execution, but trade data is stored off-chain with a **Data Availability Committee (DAC)** — a trusted set of signers who attest data is available.

```
ZK Proof → Ethereum (computation verified ✓)
Tx Data  → Off-chain DAC (NOT on Ethereum)
         ↑ Trust the DAC here
```

### Gotchas & Dev Context
- Cost: Validium < ZK Rollup (no on-chain data costs).
- Security: Validium < ZK Rollup (DAC can withhold data; users can't force-exit without data).
- Great for high-throughput apps (gaming, trading) where data loss risk is acceptable.
- **Volition** = hybrid: users choose per-tx whether data goes on-chain (rollup mode) or off-chain (Validium mode).
- If DAC colludes, users cannot exit funds. Rollups don't have this risk.

### Production FAQ
**Q: When should I choose Validium over a ZK Rollup?**
A: High-frequency, low-value transactions where throughput matters more than self-custody guarantees — e.g., NFT gaming items.

**Q: What's the difference between Validium and a sidechain?**
A: Validium uses ZK proofs verified on Ethereum (computation security). Sidechains have no such guarantee at all.

---

## 15. App-Specific Rollups (Rollup-as-a-Service)

**Definition:** An app-specific rollup (AppRollup) is a dedicated rollup chain built for a single application or protocol, using Rollup-as-a-Service (RaaS) platforms to deploy quickly.

### Real-World Dev Example
A DeFi protocol needs ultra-low latency and custom gas tokens. Instead of deploying on a shared L2, they spin up their own rollup using **Conduit** (OP Stack) or **AltLayer** in days — getting their own chain with custom rules.

```
Shared L2 (Arbitrum One):  All dApps compete for blockspace
AppRollup (your chain):    Dedicated blockspace, custom logic
```

### Gotchas & Dev Context
- **RaaS Providers:** Conduit, Caldera, AltLayer, Gelato, Syndicate.
- Built on: OP Stack, Arbitrum Orbit, Polygon CDK, ZK Stack (zkSync).
- Benefits: custom gas tokens, faster blocks, app-specific precompiles, no shared congestion.
- Downsides: you're responsible for sequencer uptime, bridge security, and ecosystem liquidity.
- **Superchain** (Optimism): a network of OP Stack chains sharing a sequencer and bridge.

### Production FAQ
**Q: How long does it take to launch an AppRollup?**
A: With RaaS providers, 1–5 days for testnet. Mainnet requires security audits and bridge setup — weeks.

**Q: Do AppRollups fragment liquidity?**
A: Yes — this is the core tradeoff. Shared liquidity layers (like Superchain or Arbitrum Orbit) aim to mitigate this.

---

## 16. Interoperability Protocols

**Definition:** Interoperability protocols are standards and systems that allow different blockchains to communicate, share state, and transfer assets seamlessly.

### Real-World Dev Example
A user holds assets on Ethereum, uses a dApp on Arbitrum, and earns rewards on Optimism — all without manually bridging each time. Interoperability protocols make this seamless via unified messaging and liquidity layers.

```
Ethereum ←→ Arbitrum ←→ Optimism ←→ Polygon
    ↑________LayerZero / CCIP / IBC_______↑
```

### Gotchas & Dev Context
- **IBC (Inter-Blockchain Communication):** Native to Cosmos — battle-tested, but EVM chains need adapters.
- **Chainlink CCIP:** Enterprise-grade cross-chain; audited, slower, more expensive.
- **Socket Protocol:** Aggregates multiple bridges + messaging into one interface.
- **ERC-7683:** Emerging standard for cross-chain intent-based swaps.
- The holy grail is **atomic cross-chain composability** — calling Contract A on Chain 1 and Contract B on Chain 2 in one transaction. Not solved yet.

### Production FAQ
**Q: What's the safest cross-chain protocol for moving large funds?**
A: Chainlink CCIP or native canonical bridges. Slower, but audited and backed by reputable validators.

**Q: What are "intents" in cross-chain context?**
A: Instead of specifying *how* to move funds cross-chain, you specify *what outcome you want* — solvers compete to fulfill it cheaply. See ERC-7683 / UniswapX.

---

## 17. Blob Space & Proto-Danksharding (EIP-4844)

**Definition:** EIP-4844 (proto-danksharding) introduced **blobs** — a new, cheap data storage type on Ethereum specifically designed for rollups, separate from calldata and automatically pruned after ~18 days.

### Real-World Dev Example
Before EIP-4844 (March 2024): Arbitrum paid ~$0.50–$2 per batch posting costs passed to users. After EIP-4844: blob costs dropped 10–100× — L2 fees fell below $0.01 per transaction overnight.

```
Pre-4844:   Rollup data → Ethereum calldata (expensive, permanent)
Post-4844:  Rollup data → Blobs (cheap, temporary, pruned ~18 days)
                ↓
         Users pay <$0.01 instead of $0.50+
```

### Gotchas & Dev Context
- Each block targets **3 blobs** (max 6) — ~384 KB of rollup data per block.
- Blobs have a **separate fee market** from calldata — rollups don't compete with regular txs.
- Data is pruned from nodes after ~18 days, but **commitments** (KZG) stay forever on L1.
- This is *proto*-danksharding — full **danksharding** will expand to ~64 blobs/block via DAS.
- L2s must upgrade their posting contracts to use blobs — all major L2s did this post-Cancun upgrade.

### Production FAQ
**Q: If blob data is pruned, how can anyone verify old L2 state?**
A: They'd need an archive node or DA service that stored the blob at the time. KZG commitments on L1 prove the data *existed*, but not what it was. For ongoing exits/proofs, data needs to be persisted externally.

**Q: What is full danksharding and when is it coming?**
A: Full danksharding expands blob capacity massively (~64 blobs) using Data Availability Sampling (DAS) — light nodes verify DA without downloading everything. ETA: likely 2026–2027 with PeerDAS as an intermediate step.

---

*End of Batch 11 — Layer 2 & Scaling*

> **Next up:** Batch 12 — MEV, Block Building & PBS (Proposer-Builder Separation)
