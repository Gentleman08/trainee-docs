# Batch 13 — Infrastructure & DevOps
> Deploying, monitoring, and maintaining Web3 systems in production.

---

## 1. Running an Ethereum Node

**A self-hosted Ethereum node** is a program that downloads, validates, and stores the full blockchain, letting you interact with the network without trusting a third party.

### Real-World Dev Example
```bash
# Install and run Geth (execution client)
geth --mainnet --http --http.api eth,net,web3 --datadir ~/.ethereum
```
Your dApp can then point `ethers.js` at `http://localhost:8545` instead of Infura.

### ASCII Diagram
```
 Your App
    │
    ▼
 localhost:8545
    │
 ┌──┴──────────────┐
 │  Ethereum Node  │
 │  (Geth / Reth)  │
 └──┬──────────────┘
    │  P2P network
    ▼
 Other Nodes
```

### Gotchas & Dev Context
- **Disk space**: A full node needs ~1 TB+ (mainnet). Start on a fast NVMe SSD.
- **Sync time**: First sync (snap sync) takes 8–24 hours.
- **Pruning**: Running `--gcmode=full` keeps disk usage lower but disables historical state queries.
- **Firewall**: Expose port `30303` (P2P) but **never** expose `8545` publicly — no auth by default.
- Reth and Erigon are modern alternatives to Geth with lower resource usage.

### Production FAQ
**Q: Do I need to run my own node?**
A: Only if you need reliability, privacy, or archive queries. For most dApps, a paid RPC provider (Alchemy, Infura) is cheaper than ops overhead.

**Q: My node keeps dropping peers. Why?**
A: Check that TCP/UDP port `30303` is open in your firewall/security-group. Also verify your system clock is synced (`ntpd`/`chronyc`) — clock drift kills peer connections.

---

## 2. Execution Client + Consensus Client Setup

**Post-Merge Ethereum** requires two separate programs running in tandem: an **execution client** (EL) that processes transactions, and a **consensus client** (CL) that drives proof-of-stake finality.

### Real-World Dev Example
```bash
# Terminal 1 — Execution client (Geth)
geth --mainnet --authrpc.addr localhost \
     --authrpc.port 8551 \
     --authrpc.jwtsecret /tmp/jwt.hex

# Terminal 2 — Consensus client (Lighthouse)
lighthouse bn --network mainnet \
  --execution-endpoint http://localhost:8551 \
  --execution-jwt /tmp/jwt.hex \
  --checkpoint-sync-url https://mainnet.checkpoint.sigp.io
```

### ASCII Diagram
```
 ┌─────────────────────┐      Engine API (JWT)      ┌──────────────────────┐
 │  Consensus Client   │ ◄──────────────────────── ► │  Execution Client    │
 │  (Lighthouse/Prysm) │    localhost:8551 (auth)    │  (Geth/Reth/Erigon)  │
 └─────────────────────┘                             └──────────────────────┘
         │ Beacon chain / PoS                                │ EVM / txn pool
         ▼                                                   ▼
    Validators                                          eth_sendRawTransaction
```

### Gotchas & Dev Context
- **JWT secret** must be identical on both sides — generate once with `openssl rand -hex 32 > /tmp/jwt.hex`.
- Never run both clients as root; use a dedicated `ethereum` system user.
- Checkpoint sync (CL) massively speeds up initial sync — skip genesis replay.
- Mix and match: Geth + Lighthouse, Reth + Nimbus, Erigon + Prysm all work.
- Monitor via Grafana dashboards (both clients expose Prometheus metrics).

### Production FAQ
**Q: One client crashed — does the node stop working?**
A: Yes. Both must be online. Set up `systemd` with `Restart=always` for both services.

**Q: Can I use the same JWT on testnet and mainnet?**
A: Technically yes, but keep separate data directories and separate JWT files per network to avoid confusion.

---

## 3. RPC Endpoints (Public vs Private)

**An RPC (Remote Procedure Call) endpoint** is a URL your app calls to read/write blockchain data — think of it as the node's API surface.

### Real-World Dev Example
```js
// Public (rate-limited, unreliable for prod)
const provider = new ethers.JsonRpcProvider("https://cloudflare-eth.com");

// Private (paid, dedicated, reliable)
const provider = new ethers.JsonRpcProvider(
  `https://eth-mainnet.g.alchemy.com/v2/${process.env.ALCHEMY_KEY}`
);
```

### ASCII Diagram
```
 dApp / Script
     │
     ├──► Public RPC  (free, rate-limited, shared)
     │        e.g. publicnode.com, cloudflare-eth.com
     │
     └──► Private RPC (paid, dedicated throughput)
              e.g. Alchemy, Infura, QuickNode
```

### Gotchas & Dev Context
- **Public RPCs** hit rate limits fast under load — never use in production frontends.
- **Never hardcode private RPC keys** in client-side JS — they'll be scraped from bundles.
- Use **allowlists** (domain/IP restrictions) on your Alchemy/Infura dashboard.
- WebSocket endpoints (`wss://`) are needed for `eth_subscribe` (real-time events).
- Self-hosted nodes are the most private option — no third party sees your queries.

### Production FAQ
**Q: My RPC calls are failing intermittently in production. What's the fix?**
A: Implement retry logic with exponential backoff, and add a fallback provider (e.g., primary = Alchemy, fallback = QuickNode).

**Q: Can an RPC provider censor my transactions?**
A: Yes. Public RPCs may filter certain addresses. For censorship resistance, send directly to your own node or use multiple providers in parallel.

---

## 4. Archive Node vs Full Node (Costs & Storage)

**A full node** stores current blockchain state; **an archive node** also stores every historical state snapshot at every block — letting you query "what was Alice's balance at block 8,000,000?"

### Real-World Dev Example
```bash
# Archive node query (only works on archive nodes)
cast call 0xTokenAddress "balanceOf(address)(uint256)" \
  0xWallet --block 8000000 --rpc-url $ARCHIVE_RPC
```

### ASCII Diagram
```
 Full Node             Archive Node
 ┌──────────────┐      ┌──────────────────────────────┐
 │ Current State│      │ State @ Block 1              │
 │ (latest only)│      │ State @ Block 2              │
 │              │      │ ...                          │
 │  ~1 TB       │      │ State @ Block N (latest)     │
 └──────────────┘      │  ~14+ TB                     │
                        └──────────────────────────────┘
```

### Gotchas & Dev Context
- **Archive nodes** cost ~14 TB+ for Ethereum mainnet and grow ~1 GB/day.
- Erigon archive mode is the most storage-efficient (~3 TB vs Geth's ~14 TB).
- For most dApps, **a full node is sufficient** — archive is only needed for analytics, indexing, or historical balance lookups.
- Providers charge a premium for archive-level calls (`eth_call` with old block numbers).
- Never use archive data APIs in hot paths — they're slow and expensive.

### Production FAQ
**Q: Can I upgrade a full node to an archive node?**
A: No — you must re-sync from scratch in archive mode. Plan ahead.

**Q: What's a cheaper alternative to running my own archive node?**
A: Use a paid provider's archive endpoint (Alchemy/QuickNode archive plans) or query The Graph for indexed historical data.

---

## 5. MEV-Boost / Flashbots

**MEV (Maximal Extractable Value)** is profit validators/searchers extract by reordering, inserting, or censoring transactions. **MEV-Boost** is a middleware that lets validators outsource block building to specialized builders to capture this value.

### Real-World Dev Example
```
 Searcher finds arbitrage opportunity →
 Bundles txns via Flashbots MEV-Share →
 Builder includes bundle in block →
 Validator earns bid, searcher earns profit
```

### ASCII Diagram
```
 Searcher
    │  bundle (txns + bid)
    ▼
 Relay (Flashbots/BloXroute)
    │  best block header
    ▼
 Validator (MEV-Boost)
    │  getPayload → full block
    ▼
 Block committed on-chain
```

### Gotchas & Dev Context
- **MEV-Boost** is opt-in for validators but ~90% of validators use it (it's free money).
- Relays are trusted intermediaries — they can censor transactions (OFAC filtering controversy).
- **Sandwich attacks** are a form of MEV targeting your users' swaps.
- Use **private mempools** (Flashbots Protect, MEV Blocker) to hide user txns from searchers.
- MEV is a protocol-level reality, not a bug — understanding it is essential for DeFi devs.

### Production FAQ
**Q: How do I protect my users from sandwich attacks?**
A: Route transactions through Flashbots Protect (`https://rpc.flashbots.net`) or set tight slippage limits.

**Q: Can MEV bots target my smart contract?**
A: Yes, any on-chain arbitrage opportunity can be targeted. Use commit-reveal schemes or private RPCs for sensitive operations.

---

## 6. Block Builder & Relay

**Block builders** are specialized entities that assemble the most profitable block from pending transactions and MEV bundles. **Relays** are trusted intermediaries that receive blocks from builders and pass them to validators — enforcing fair play between both parties.

### ASCII Diagram
```
 Mempool / Searcher Bundles
         │
         ▼
  ┌─────────────┐      full block      ┌──────────┐    best header   ┌───────────┐
  │Block Builder│ ───────────────────► │  Relay   │ ───────────────► │ Validator │
  └─────────────┘                      └──────────┘  (blind bidding) └───────────┘
   (Maximizes MEV)                   (escrow + verify)            (picks highest bid)
```

### Real-World Dev Example
Major block builders: **beaverbuild**, **Titan**, **rsync-builder**. Builders compete — the one offering the highest bid to the validator wins block inclusion.

### Gotchas & Dev Context
- Validators never see the full block before committing (PBS — Proposer-Builder Separation) — this prevents front-running by validators.
- Relays are currently **trusted** — a colluding relay could cheat. Enshrined PBS (future EIP) aims to fix this.
- **Block builders have massive power** — they decide transaction ordering within a block.
- Multiple relays can be configured in MEV-Boost for redundancy.
- Centralization risk: top 3 builders regularly build 80%+ of blocks.

### Production FAQ
**Q: Does my dApp need to worry about block builders?**
A: Indirectly yes. Builder ordering affects your users' transaction experience and MEV exposure on DeFi protocols.

**Q: What's the difference between a relay and a block explorer?**
A: A relay is a real-time trusted intermediary in the MEV pipeline. A block explorer (Etherscan) is a read-only historical data tool.

---

## 7. Blockchain Indexing (The Graph, Goldsky)

**Blockchain indexing** is the process of reading on-chain event logs and storing them in a queryable database so your frontend can fetch data efficiently via GraphQL instead of slow RPC calls.

### Real-World Dev Example
```graphql
# Query via The Graph subgraph
{
  transfers(where: { to: "0xAbc..." }, orderBy: timestamp, first: 10) {
    id
    from
    to
    value
    timestamp
  }
}
```

### ASCII Diagram
```
 Ethereum Node
      │  event logs
      ▼
 Indexer (subgraph / Goldsky pipeline)
      │  parsed + stored in Postgres
      ▼
 GraphQL API
      │
      ▼
 dApp Frontend
```

### Gotchas & Dev Context
- **The Graph** uses a decentralized network of indexers; **Goldsky** is a managed alternative with faster setup and SQL support.
- Subgraphs index specific contracts — you define which events to watch in `schema.graphql` + `mappings.ts`.
- Reorgs can cause indexed data to temporarily diverge — always handle `_meta { hasIndexingErrors }`.
- Indexing lags behind the chain tip by a few blocks — don't use it for real-time tx confirmation.
- Use `graph-node` self-hosted for full control in production.

### Production FAQ
**Q: My subgraph is returning stale data. What do I check?**
A: Check `_meta { block { number } }` in your query — compare it to current block. If lagging, check indexer health on The Graph Studio.

**Q: Can I index multiple chains in one subgraph?**
A: Not natively in one subgraph, but Goldsky supports multi-chain pipelines, and you can federate multiple subgraphs in your backend.

---

## 8. Event-Driven Architecture for dApps

**Event-driven architecture** means your backend reacts to on-chain events (emitted by smart contracts) rather than polling state — analogous to webhooks vs. REST polling.

### Real-World Dev Example
```js
// Listen for Transfer events via WebSocket
const contract = new ethers.Contract(TOKEN_ADDR, ABI, wsProvider);

contract.on("Transfer", (from, to, value, event) => {
  console.log(`Transfer: ${from} → ${to}, amount: ${value}`);
  updateDatabase(from, to, value);
});
```

### ASCII Diagram
```
 Smart Contract emits Transfer event
         │
         ▼
  WebSocket RPC (eth_subscribe)
         │
         ▼
  Backend Event Handler
    ├── Update DB
    ├── Send email/push notification
    └── Trigger downstream service
```

### Gotchas & Dev Context
- WebSocket connections drop — always implement reconnect logic with exponential backoff.
- Events are not guaranteed delivery — reorgs can replay or remove events.
- Use a **queue** (Redis/SQS) between event listener and handler to avoid dropped events during handler errors.
- `eth_getLogs` (polling) is more reliable than `eth_subscribe` for critical systems.
- Index events via The Graph for historical replay; use WebSockets only for live updates.

### Production FAQ
**Q: We missed some events during a backend outage. How do we recover?**
A: Use `eth_getLogs` with `fromBlock`/`toBlock` to replay missed events from the last processed block stored in your DB.

**Q: Should I trust a single WebSocket subscription in production?**
A: No. Combine subscriptions with periodic polling and cross-check against an indexer for data integrity.

---

## 9. CICD for Smart Contracts (Hardhat + GitHub Actions)

**CI/CD for smart contracts** automates compiling, testing, linting, and deploying contracts on every code push — the same way web devs automate frontend deployments.

### Real-World Dev Example
```yaml
# .github/workflows/ci.yml
name: Smart Contract CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
      - run: npx hardhat compile
      - run: npx hardhat test
      - run: npx hardhat coverage
```

### Gotchas & Dev Context
- Store `PRIVATE_KEY` and `RPC_URL` as **GitHub Secrets**, never in the repo.
- Run `slither` (static analysis) in CI to catch common vulnerabilities automatically.
- Use a **fork of mainnet** in tests (`hardhat_reset` with `forking`) for realistic integration tests.
- Separate CI (test on every push) from CD (deploy only on tagged releases).
- Pin exact Solidity compiler versions to avoid CI/local discrepancies.
- Add gas snapshot tests (`hardhat-gas-reporter`) to detect gas regressions in PRs.

### ASCII Diagram
```
 git push
    │
    ▼
 GitHub Actions
    ├── compile
    ├── lint (solhint)
    ├── test (hardhat test)
    ├── coverage (>80% gate)
    └── [on tag] deploy to testnet → mainnet
```

### Production FAQ
**Q: How do I prevent accidental mainnet deployment in CI?**
A: Add an environment protection rule in GitHub (Settings → Environments → mainnet) requiring manual approval before the deploy step runs.

**Q: Tests pass locally but fail in CI. Why?**
A: Usually a Solidity version mismatch or missing `.env` variables. Pin compiler versions in `hardhat.config.ts` and always mock secrets in CI via GitHub Secrets.

---

## 10. Contract Verification (Etherscan, Sourcify)

**Contract verification** is publishing your Solidity source code so that anyone can confirm the deployed bytecode was compiled from that source — it turns an opaque address into readable, auditable code.

### Real-World Dev Example
```bash
# Verify via Hardhat + Etherscan
npx hardhat verify --network mainnet \
  0xYourContractAddress \
  "Constructor Arg 1" "Constructor Arg 2"

# Verify via Foundry
forge verify-contract 0xYourContractAddress \
  src/MyContract.sol:MyContract \
  --chain mainnet \
  --etherscan-api-key $ETHERSCAN_KEY
```

### Gotchas & Dev Context
- **Exact compiler settings** must match: version, optimizer runs, via-IR flag — even a single difference produces different bytecode.
- **Sourcify** is decentralized and open-source; Etherscan is centralized but more widely recognized.
- ABI-encoded constructor arguments must be provided manually if not auto-detected.
- Proxy contracts: verify both the proxy AND the implementation; use Etherscan's "Is Proxy" feature.
- Flatten your source or use standard JSON input — both work with Etherscan.
- Verification is irreversible — once published, your source is permanent.

### Production FAQ
**Q: Verification keeps failing with "bytecode mismatch." What now?**
A: Double-check optimizer settings (`runs`, `enabled`) and Solidity version in `hardhat.config.ts` match exactly what was used at deploy time. Check for `viaIR` flag differences.

**Q: Is Sourcify better than Etherscan for verification?**
A: Sourcify is decentralized and stores metadata on IPFS — better for long-term trustlessness. Etherscan has better UX and wider adoption.

---

## 11. Monitoring (Forta, OpenZeppelin Defender)

**On-chain monitoring** watches contract activity in real time and alerts you when something suspicious happens — think of it as Datadog for your smart contracts.

### Real-World Dev Example
```js
// Forta detection bot (simplified)
async function handleTransaction(txEvent) {
  const findings = [];
  if (txEvent.filterFunction("withdraw(uint256)", VAULT_ADDRESS)) {
    if (txEvent.transaction.value > ethers.parseEther("100")) {
      findings.push(Finding.fromObject({
        name: "Large Withdrawal",
        severity: FindingSeverity.High,
      }));
    }
  }
  return findings;
}
```

### ASCII Diagram
```
 On-chain transactions
        │
        ▼
 Forta Bot / Defender Sentinel
        │  pattern match
        ├──► Alert: Slack / PagerDuty / email
        └──► Auto-action: pause contract (Defender)
```

### Gotchas & Dev Context
- **Forta** is a decentralized bot network — you deploy detection bots as Docker containers.
- **OpenZeppelin Defender** offers Sentinels (monitoring) + Relayer (gasless txns) + Autotasks (automated responses).
- Build pause/unpause mechanisms into contracts so monitors can trigger emergency stops.
- False positives are common — tune thresholds carefully before wiring to auto-pause.
- Monitor the ERC-20 `Approval` event for unlimited approvals — common exploit vector.

### Production FAQ
**Q: Our contract was exploited before our monitor fired. How do we improve response time?**
A: Use mempool monitoring (Defender Sentinels support pending txns) to catch attacks before they confirm, not just after.

**Q: Is Forta free to use?**
A: Running Forta bots has costs (FORT token staking for scan node operators), but subscribing to community bots is free.

---

## 12. Upgradeable Contract Deployment Pipeline

**Upgradeable contracts** use a proxy pattern so you can update business logic without changing the contract address users interact with.

### ASCII Diagram
```
 User
  │  calls
  ▼
Proxy Contract (stable address, stores state)
  │  delegatecall
  ▼
Implementation Contract v1 → v2 → v3
        (logic only, no state)
```

### Real-World Dev Example
```bash
# Deploy upgradeable proxy (OpenZeppelin Upgrades + Hardhat)
npx hardhat run scripts/deploy-proxy.ts --network mainnet

# Upgrade to new implementation
npx hardhat run scripts/upgrade.ts --network mainnet
```
```js
// deploy-proxy.ts
const MyContract = await ethers.getContractFactory("MyContractV1");
const proxy = await upgrades.deployProxy(MyContract, [initArg]);
await proxy.waitForDeployment();
```

### Gotchas & Dev Context
- **Storage layout must be preserved** across upgrades — never remove or reorder existing state variables.
- Use `upgrades.validateUpgrade()` in CI to catch storage collisions before deploying.
- **Transparent Proxy vs UUPS**: UUPS puts upgrade logic in the implementation (cheaper), Transparent Proxy puts it in the proxy (simpler).
- Timelocks on upgrades are a security best practice — give users time to exit before changes go live.
- Always verify the new implementation on Etherscan before upgrading.

### Production FAQ
**Q: Can I make a contract non-upgradeable after launch?**
A: Yes — call `upgrades.admin.renounceOwnership()` or use a UUPS contract and remove the `_authorizeUpgrade` function.

**Q: We introduced a new state variable but broke storage layout. What happens?**
A: The new variable overwrites an existing slot — data corruption and undefined behavior. Always run `hardhat-upgrades` validation in CI.

---

## 13. Multi-Chain Deployment Strategy

**Multi-chain deployment** means deploying the same (or adapted) smart contracts across several EVM-compatible networks and managing them consistently.

### Real-World Dev Example
```js
// hardhat.config.ts — multiple networks
networks: {
  mainnet:  { url: process.env.ETH_RPC,  chainId: 1     },
  polygon:  { url: process.env.POLY_RPC, chainId: 137   },
  arbitrum: { url: process.env.ARB_RPC,  chainId: 42161 },
  base:     { url: process.env.BASE_RPC, chainId: 8453  },
}
```
```bash
# Deploy to all chains via script loop
for NETWORK in mainnet polygon arbitrum base; do
  npx hardhat run scripts/deploy.ts --network $NETWORK
done
```

### Gotchas & Dev Context
- **Contract addresses differ per chain** unless using `CREATE2` with a deterministic deployer (same address everywhere).
- Track deployments in a `deployments/` JSON file per network — use Hardhat Deploy plugin.
- Gas prices and block times vary wildly: Ethereum mainnet is slow/expensive, L2s are fast/cheap.
- Chain IDs must be correct in every config — a wrong chain ID can drain funds to the wrong network.
- Use **Tenderly** or **Defender** multi-network dashboards for unified monitoring.

### Production FAQ
**Q: How do I get the same contract address on every chain?**
A: Use a `CREATE2` factory (e.g., `0x4e59b44847b379578588920cA78FbF26c0B4956C` — the canonical deterministic deployer) with identical salt and bytecode.

**Q: Should we deploy our own bridge or use existing ones?**
A: Almost always use existing, audited bridges (LayerZero, Wormhole, Axelar) — rolling your own bridge is extremely high risk.

---

## 14. Gas Optimization Techniques

**Gas optimization** is writing Solidity that executes with fewer EVM operations, reducing transaction costs for your users.

### Real-World Dev Example
```solidity
// ❌ Expensive: reading state var in loop
for (uint i = 0; i < items.length; i++) { ... }

// ✅ Cheap: cache in memory first
uint256 len = items.length;
for (uint256 i = 0; i < len; ) {
    // ...
    unchecked { ++i; } // skip overflow check
}
```

### Gotchas & Dev Context
- **`uint256` is cheapest** — EVM works in 32-byte slots, smaller types cost extra masking ops.
- **`storage` reads are expensive** (~2100 gas cold, 100 warm). Cache in local `memory` vars.
- Use `immutable` for values set once in constructor (~3x cheaper than `storage`).
- Use `calldata` instead of `memory` for external function parameters.
- `++i` is slightly cheaper than `i++` (no temp variable).
- `custom errors` are cheaper than `require("string message")` — string encoding wastes gas.
- Events are cheap (~375 gas base + 8 gas/byte) — prefer them over storage for historical data.

### Production FAQ
**Q: How do I measure gas savings quantitatively?**
A: Use `hardhat-gas-reporter` to print per-function gas costs in test output, and `forge snapshot` to track gas changes across commits.

**Q: Is premature gas optimization worth it?**
A: For core DeFi hot paths — yes. For infrequently called admin functions — no. Optimize for correctness first, then profile.

---

## 15. Storage Packing / Bit Manipulation

**Storage packing** is arranging Solidity struct fields so multiple small values share a single 32-byte storage slot, reducing SLOAD/SSTORE costs.

### Real-World Dev Example
```solidity
// ❌ Unpacked: 3 slots (3x SSTORE)
contract Bad {
    uint128 a; // slot 0
    uint256 b; // slot 1 (forces new slot)
    uint128 c; // slot 2
}

// ✅ Packed: 2 slots
contract Good {
    uint128 a; // slot 0 (bytes 0-15)
    uint128 c; // slot 0 (bytes 16-31) — packed!
    uint256 b; // slot 1
}
```

### Bit Manipulation Example
```solidity
// Pack a bool + uint8 + address into one slot manually
uint256 packed = (uint256(uint160(addr)) << 8) | flag;
address recovered = address(uint160(packed >> 8));
bool   flagOut   = (packed & 0xFF) != 0;
```

### Gotchas & Dev Context
- Solidity packs **right-to-left** within a slot — declare small types consecutively.
- Mappings and dynamic arrays always start a new slot (can't be packed).
- Reading a packed slot costs one SLOAD — but each value needs extra masking ops to extract.
- Use `struct` grouping for naturally related packed values.
- Be careful with `uint8`/`bool` in hot loops — packing saves SSTORE gas but can add masking overhead per read.

### Production FAQ
**Q: How do I verify my struct is actually packed?**
A: Use `forge inspect MyContract storage-layout` — it shows exact slot assignments and offsets for all variables.

**Q: Is bit manipulation in Solidity safe?**
A: Yes if done carefully. Prefer `uint` shifts over inline assembly for clarity; use assembly only for extreme optimization in audited code.

---

## 16. Assembly (Yul) Basics

**Yul** is an intermediate language embedded in Solidity via `assembly { }` blocks, giving you direct EVM opcode access for maximum gas efficiency and operations Solidity can't express natively.

### Real-World Dev Example
```solidity
// Return the address of `this` more cheaply
function getAddress() external view returns (address addr) {
    assembly {
        addr := address()
    }
}

// Efficient zero-check
function isZero(uint256 x) internal pure returns (bool result) {
    assembly {
        result := iszero(x)
    }
}

// Read arbitrary storage slot (used in proxy patterns)
function _getImplementation() internal view returns (address impl) {
    bytes32 slot = 0x360894a13ba1...;
    assembly {
        impl := sload(slot)
    }
}
```

### Gotchas & Dev Context
- Yul **bypasses Solidity's safety checks** — no overflow protection, no type checking.
- EVM stack depth limit is 1024 — Yul makes it easy to accidentally hit this.
- Proxy contracts (EIP-1967) use Yul for `delegatecall` and storage slot reads.
- Use `mload`/`mstore` for memory manipulation, `sload`/`sstore` for storage.
- Always comment Yul code extensively — it's unreadable without context.
- Security auditors scrutinize Yul blocks heavily — minimize surface area.

### Production FAQ
**Q: When should I actually use Yul in production?**
A: Rarely — only in hot paths (AMM math, token transfers in high-frequency contracts) or for proxy scaffolding. 95% of contracts never need it.

**Q: Can I test Yul code the same way as Solidity?**
A: Yes — write it inside a Solidity contract and test normally with Hardhat/Foundry. Foundry also supports pure Yul contract compilation.

---

## 17. Environment Variables & Secret Management for Web3

**Secret management** ensures private keys, RPC URLs, and API keys are never committed to source control or exposed in CI logs — a Web3 breach often means permanent fund loss.

### Real-World Dev Example
```bash
# .env (never commit — add to .gitignore)
PRIVATE_KEY=0xabc123...
ALCHEMY_KEY=your_key_here
ETHERSCAN_API_KEY=your_key_here

# hardhat.config.ts
import * as dotenv from "dotenv";
dotenv.config();

const config: HardhatUserConfig = {
  networks: {
    mainnet: {
      url: `https://eth-mainnet.g.alchemy.com/v2/${process.env.ALCHEMY_KEY}`,
      accounts: [process.env.PRIVATE_KEY!],
    }
  }
};
```

### Gotchas & Dev Context
- **Always** add `.env` to `.gitignore` — scan your git history with `git-secrets` or `trufflehog` if you suspect a leak.
- For production deployments, use a **hardware wallet** (Ledger + Hardhat Ledger plugin) instead of raw private keys in `.env`.
- Use **AWS Secrets Manager**, **HashiCorp Vault**, or **GitHub Secrets** for CI/CD — never plain env files on servers.
- Rotate RPC API keys immediately if exposed — they can be used to drain rate limits or spy on queries.
- Separate deployer keys (used once per deploy) from operational keys (used by relayers/bots) — minimize blast radius.
- Use **account abstraction** (ERC-4337) or **Defender Relayer** to avoid storing hot keys on servers at all.

### ASCII Diagram
```
 Dev Machine           CI/CD (GitHub Actions)     Production Server
 .env (local only)     GitHub Secrets             AWS Secrets Manager
       │                      │                         │
       └──────────────────────┴─────────────────────────┘
                        Never in git repo
```

### Production FAQ
**Q: Our deployer private key leaked in a public repo. What do we do immediately?**
A: Transfer all funds from that address NOW (it's likely being swept by bots within minutes). Rotate all keys, audit what that key had access to, and post-mortem the leak.

**Q: Can I use a multisig for deployments?**
A: Yes — use Gnosis Safe + the Hardhat Safe Deployer plugin. Deployments require M-of-N signatures, eliminating single-key risk entirely.

---

*End of Batch 13 — Infrastructure & DevOps*
