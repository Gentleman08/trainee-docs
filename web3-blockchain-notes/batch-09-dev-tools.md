# Batch 9 — Development Tools & Frameworks
> The full Web3 developer toolkit — from writing contracts to deploying dApps.

---

## 1. Hardhat

**A Node.js-based Ethereum development environment for compiling, testing, and deploying smart contracts.**

### Real-World Dev Example
```bash
npm install --save-dev hardhat
npx hardhat init          # scaffold project
npx hardhat compile       # compile contracts
npx hardhat test          # run tests
npx hardhat node          # spin up local blockchain
npx hardhat run scripts/deploy.js --network localhost
```

```javascript
// hardhat.config.js
require("@nomicfoundation/hardhat-toolbox");
module.exports = {
  solidity: "0.8.24",
  networks: {
    sepolia: { url: process.env.RPC_URL, accounts: [process.env.PRIVATE_KEY] }
  }
};
```

### ASCII Diagram
```
hardhat.config.js
       |
  ┌────┴────────────┐
  │   Hardhat Core  │
  ├────────┬────────┤
compile  test    deploy
  │        │        │
 artifacts mocha  ethers.js
```

### Gotchas & Dev Context
- Uses `ethers.js` under the hood by default (v6 now)
- `console.log()` inside Solidity works via `hardhat/console.sol` import — removed in production builds
- `hardhat_impersonateAccount` lets you fork mainnet and act as any wallet
- Plugin ecosystem is mature: gas reporter, coverage, etherscan verify

### Production FAQ
**Q: Hardhat vs Foundry — which to use?**  
A: Hardhat is better for JS/TS-heavy teams. Foundry is faster for pure Solidity testing. Many prod teams use both.

**Q: How do I verify a contract on Etherscan?**  
A: Add `@nomicfoundation/hardhat-verify` plugin, then run `npx hardhat verify --network mainnet <address> <constructor-args>`.

---

## 2. Foundry (Forge, Cast, Anvil, Chisel)

**A blazing-fast, Rust-based Solidity development toolkit — tests are written in Solidity itself.**

### Real-World Dev Example
```bash
forge init my-project       # scaffold
forge build                 # compile
forge test -vvv             # run tests (verbose)
forge test --match-test testTransfer  # run one test

cast call 0xContractAddr "balanceOf(address)" 0xWallet  # read on-chain
cast send 0xContractAddr "transfer(address,uint256)" 0xTo 1000 --private-key $PK

anvil                        # local node, 10 pre-funded accounts
chisel                       # interactive Solidity REPL
```

```solidity
// test/MyToken.t.sol
contract MyTokenTest is Test {
    function testMint() public {
        token.mint(alice, 100);
        assertEq(token.balanceOf(alice), 100);
    }
}
```

### ASCII Diagram
```
Foundry Toolkit
├── forge   → compile / test / deploy
├── cast    → CLI wallet & RPC calls
├── anvil   → local EVM node
└── chisel  → Solidity REPL
```

### Gotchas & Dev Context
- Tests run in Solidity — no JS context switching; much faster CI
- `vm.prank(addr)` spoofs `msg.sender`; `vm.warp(ts)` sets block timestamp — great for time-lock testing
- `forge snapshot` tracks gas usage per test over time
- `foundry.toml` is config; uses `remappings.txt` for imports

### Production FAQ
**Q: Can I use Foundry with OpenZeppelin contracts?**  
A: Yes. Run `forge install OpenZeppelin/openzeppelin-contracts` and add remappings.

**Q: What is `forge script` vs `forge deploy`?**  
A: `forge script` runs a Solidity script file for deployment/interaction; there is no `forge deploy` command — scripts handle it all.

---

## 3. Remix IDE

**A browser-based Solidity IDE — zero setup, great for prototyping and learning.**

### Real-World Dev Example
- Visit [remix.ethereum.org](https://remix.ethereum.org)
- Write contract → click **Compile** → click **Deploy & Run**
- Switch environment to "Injected Provider - MetaMask" to deploy to testnet
- Use the built-in debugger to step through transactions

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract Hello {
    string public greet = "Hello, Web3!";
}
```

### Gotchas & Dev Context
- Default environment is the in-browser JavaScript VM — not a real blockchain
- Plugin system supports Slither analysis, unit testing, and ETHERSCAN verification
- Great for auditors to quickly inspect and test a single contract file
- Not suitable for multi-file projects or production CI/CD pipelines
- Remixd plugin lets you sync with your local filesystem via daemon

### Production FAQ
**Q: Can I use Remix for production deployment?**  
A: Technically yes, but not recommended. Use Hardhat/Foundry for reproducible, version-controlled deployments.

**Q: Does Remix support Hardhat console.log?**  
A: No. Use Remix's own logger or `emit` events to debug instead.

---

## 4. Truffle (Legacy)

**One of the first Ethereum development frameworks — now largely deprecated in favor of Hardhat/Foundry.**

### Real-World Dev Example
```bash
npm install -g truffle
truffle init
truffle compile
truffle migrate --network ropsten
truffle test
```

```javascript
// migrations/2_deploy.js
const MyToken = artifacts.require("MyToken");
module.exports = function (deployer) {
  deployer.deploy(MyToken, 1000000);
};
```

### Gotchas & Dev Context
- ConsenSys announced Truffle's sunset in late 2023 — it is no longer actively maintained
- `Ganache` (Truffle's local blockchain) is also deprecated; use `anvil` or `hardhat node` instead
- Existing codebases may still use Truffle — worth knowing for maintenance work
- Migrations system (`truffle migrate`) was influential; Hardhat's Ignition and Foundry scripts replaced it
- Mocha + Chai used for testing in JS

### Production FAQ
**Q: Should I start a new project with Truffle?**  
A: No. Use Hardhat or Foundry. Truffle is only relevant for maintaining legacy projects.

**Q: What replaced Ganache?**  
A: Hardhat's built-in `hardhat node` and Foundry's `anvil` both provide fast local EVM nodes with better tooling.

---

## 5. OpenZeppelin Contracts

**A battle-tested, audited Solidity library providing standard implementations of ERC tokens, access control, and security utilities.**

### Real-World Dev Example
```bash
npm install @openzeppelin/contracts
# or with Foundry:
forge install OpenZeppelin/openzeppelin-contracts
```

```solidity
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract MyToken is ERC20, Ownable {
    constructor() ERC20("MyToken", "MTK") Ownable(msg.sender) {
        _mint(msg.sender, 1_000_000 * 10**18);
    }
    function mint(address to, uint256 amt) external onlyOwner {
        _mint(to, amt);
    }
}
```

### Gotchas & Dev Context
- OZ v5 introduced breaking changes: `Ownable` now requires constructor argument
- Never copy-paste OZ code and modify internals — extend via inheritance
- `ReentrancyGuard`, `Pausable`, `AccessControl` are must-knows for production
- `Upgrades` plugin (`@openzeppelin/hardhat-upgrades`) manages proxy patterns
- OZ Defender is the enterprise ops/monitoring product layer

### Production FAQ
**Q: Are OZ contracts safe to use without an audit?**  
A: The OZ library itself is audited, but *your usage and extensions* still need review.

**Q: What's the difference between `Ownable` and `AccessControl`?**  
A: `Ownable` = single admin. `AccessControl` = role-based (e.g., MINTER_ROLE, PAUSER_ROLE) — use it when you need multiple permission levels.

---

## 6. Ethers.js vs Web3.js vs Viem

**JavaScript/TypeScript libraries for interacting with the Ethereum blockchain from a frontend or Node.js backend.**

### Real-World Dev Example
```typescript
// Ethers.js v6
import { ethers } from "ethers";
const provider = new ethers.JsonRpcProvider(RPC_URL);
const contract = new ethers.Contract(addr, abi, provider);
const bal = await contract.balanceOf(wallet);

// Viem
import { createPublicClient, http } from "viem";
import { mainnet } from "viem/chains";
const client = createPublicClient({ chain: mainnet, transport: http(RPC_URL) });
const bal = await client.readContract({ address: addr, abi, functionName: "balanceOf", args: [wallet] });
```

### Comparison Table
| Feature       | Web3.js       | Ethers.js v6  | Viem          |
|---------------|---------------|---------------|---------------|
| TypeScript    | Partial       | Good          | Excellent     |
| Bundle size   | Large         | Medium        | Small         |
| Maintenance   | Slowing       | Active        | Very active   |
| Used by       | Legacy dApps  | Most dApps    | Wagmi/modern  |

### Gotchas & Dev Context
- Web3.js v4 exists but ecosystem momentum has shifted to Viem
- Ethers.js v5 → v6 has breaking API changes (`providers` → `JsonRpcProvider`, etc.)
- Viem is tree-shakeable and built for TypeScript-first workflows
- Viem is the engine under Wagmi v2

### Production FAQ
**Q: Which should I use for a new project in 2024+?**  
A: Viem + Wagmi for React frontends. Ethers.js for Node.js scripts/backends.

**Q: Can I use multiple libraries in one project?**  
A: Technically yes, but it bloats bundle size — pick one and stick with it.

---

## 7. Wagmi (React Hooks for Ethereum)

**A collection of React hooks that abstract wallet connection, contract reads/writes, and chain switching — built on top of Viem.**

### Real-World Dev Example
```typescript
// wagmi v2
import { useReadContract, useWriteContract, useAccount } from "wagmi";

function TokenBalance() {
  const { address } = useAccount();
  const { data: balance } = useReadContract({
    address: TOKEN_ADDR, abi, functionName: "balanceOf", args: [address],
  });
  const { writeContract } = useWriteContract();

  return (
    <button onClick={() => writeContract({
      address: TOKEN_ADDR, abi, functionName: "transfer", args: [recipient, amount]
    })}>
      Send Tokens (Balance: {balance?.toString()})
    </button>
  );
}
```

### Gotchas & Dev Context
- Wagmi v2 is a full rewrite — v1 APIs are not compatible
- Built on TanStack Query: loading/error/refetch states are free
- Configure once with `WagmiProvider` + `QueryClientProvider` at app root
- Supports 20+ connectors: MetaMask, WalletConnect, Coinbase Wallet, etc.
- SSR-safe with Next.js using `cookieStorage` for hydration

### Production FAQ
**Q: Does Wagmi handle transaction state (pending, confirmed)?**  
A: Yes. `useWaitForTransactionReceipt` hook polls until the tx is mined and returns receipt.

**Q: Can I use Wagmi without RainbowKit?**  
A: Yes. Wagmi is the logic layer; RainbowKit/ConnectKit are the UI layer on top.

---

## 8. RainbowKit / ConnectKit

**Pre-built wallet connection UI components that plug into Wagmi — no need to design your own "Connect Wallet" modal.**

### Real-World Dev Example
```typescript
// RainbowKit setup
import { RainbowKitProvider, ConnectButton } from "@rainbow-me/rainbowkit";
import "@rainbow-me/rainbowkit/styles.css";

// In component:
<ConnectButton />  // That's it — full modal, multi-wallet, ENS display
```

```typescript
// ConnectKit (alternative)
import { ConnectKitButton } from "connectkit";
<ConnectKitButton />
```

### ASCII Diagram
```
User clicks "Connect Wallet"
         │
    ┌────┴────┐
    │ Modal   │  ← RainbowKit/ConnectKit
    │ UI      │
    └────┬────┘
         │
    Wagmi hooks → Viem → RPC Provider
```

### Gotchas & Dev Context
- RainbowKit: more customizable themes, avatars, chain selector built-in
- ConnectKit: cleaner default UI, simpler setup, Family ecosystem
- Both require WalletConnect Project ID (get free at cloud.walletconnect.com)
- Dark/light mode, custom themes supported out of the box
- Mobile wallet deep-links handled automatically

### Production FAQ
**Q: RainbowKit vs ConnectKit — which to pick?**  
A: RainbowKit has a larger community and more examples. ConnectKit has a slightly simpler API. Either works for production.

**Q: Can I add custom wallets to RainbowKit?**  
A: Yes, via the `wallet` API — you can add any EIP-1193-compatible wallet connector.

---

## 9. Alchemy / Infura / QuickNode (RPC Providers)

**Managed node services that give your app an RPC endpoint to talk to the blockchain — without running your own node.**

### Real-World Dev Example
```bash
# Alchemy endpoint
https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY

# Use in code
const provider = new ethers.JsonRpcProvider(
  "https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY"
);
```

### ASCII Diagram
```
Your dApp
    │
    │  HTTPS / WSS
    ▼
[Alchemy / Infura / QuickNode]
    │
    │  Internal P2P
    ▼
Ethereum Full Node (archive)
    │
    ▼
Blockchain State
```

### Comparison Table
| Provider   | Free Tier       | Standout Feature         |
|------------|-----------------|--------------------------|
| Alchemy    | 300M CU/month   | Enhanced APIs, webhooks  |
| Infura     | 100K req/day    | Oldest, most integrations|
| QuickNode  | 10M credits     | Fastest latency, addons  |

### Gotchas & Dev Context
- Never expose API keys in frontend code — use environment variables + backend proxy
- Free tiers rate-limit: archive node access often costs extra
- Use WebSocket (`wss://`) for event subscriptions, HTTP for regular calls
- Alchemy's `alchemy_getAssetTransfers` and NFT APIs go beyond standard JSON-RPC

### Production FAQ
**Q: What if the RPC provider goes down?**  
A: Use a fallback provider: `ethers.FallbackProvider([alchemyProvider, infuraProvider])`.

**Q: Should I run my own node?**  
A: Only if you have very high volume, compliance needs, or need custom archive data. Otherwise, managed providers are more cost-effective.

---

## 10. JSON-RPC API (eth_call, eth_sendTransaction, eth_getLogs)

**The standard communication protocol between clients and Ethereum nodes — all libraries (ethers, viem, web3) use JSON-RPC under the hood.**

### Real-World Dev Example
```bash
# eth_call — read contract state (no gas, no tx)
curl https://eth-mainnet.g.alchemy.com/v2/KEY \
  -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_call","params":[{"to":"0xContract","data":"0x70a08231000...walletEncoded"},"latest"],"id":1}'

# eth_getLogs — fetch events
curl ... -d '{"method":"eth_getLogs","params":[{"address":"0x...","fromBlock":"0x1","toBlock":"latest","topics":["0xEventSig"]}]}'
```

### Key Methods
| Method                  | Purpose                              |
|-------------------------|--------------------------------------|
| `eth_call`              | Read contract (no state change)      |
| `eth_sendRawTransaction`| Broadcast signed tx                  |
| `eth_getLogs`           | Fetch historical events              |
| `eth_getBalance`        | Get ETH balance                      |
| `eth_blockNumber`       | Current block height                 |
| `eth_getTransactionReceipt` | Tx status + gas used           |

### Gotchas & Dev Context
- `eth_call` uses no gas but still needs a valid call; reverts return error data
- `eth_getLogs` can time-out on very large block ranges — paginate with `fromBlock`/`toBlock`
- `eth_sendTransaction` is for nodes with unlocked accounts; `eth_sendRawTransaction` is for pre-signed txs from wallets

### Production FAQ
**Q: Why does `eth_call` return `0x` for my function?**  
A: Usually the ABI encoding of `data` is wrong, or the contract address is incorrect.

**Q: How do I decode `eth_getLogs` data?**  
A: Use `ethers.Interface.parseLog(log)` with your ABI to decode topics and data fields.

---

## 11. Subgraph (The Graph Protocol)

**A decentralized indexing protocol that lets you query blockchain event data via GraphQL — like a read-optimized database for on-chain events.**

### Real-World Dev Example
```bash
npm install -g @graphprotocol/graph-cli
graph init --product hosted-service my-org/my-subgraph
graph codegen && graph build
graph deploy --product hosted-service my-org/my-subgraph
```

```yaml
# subgraph.yaml (excerpt)
dataSources:
  - name: MyToken
    source:
      address: "0xTokenAddress"
      abi: ERC20
      startBlock: 18000000
    mapping:
      eventHandlers:
        - event: Transfer(indexed address, indexed address, uint256)
          handler: handleTransfer
```

### ASCII Diagram
```
Smart Contract emits Events
         │
    The Graph Node
    (indexes events)
         │
    Subgraph Store
         │
   GraphQL Endpoint
         │
     Your dApp
```

### Gotchas & Dev Context
- Only indexes events — not arbitrary state; design contracts with rich events in mind
- Hosted Service is being sunset; migrate to The Graph's decentralized network
- `startBlock` matters — wrong block = missing historical data
- Local testing: use `graph-node` Docker image with `graph test` (Matchstick framework)

### Production FAQ
**Q: Can I query data not emitted as events?**  
A: Limitedly — you can use `call handlers` for function calls or `block handlers`, but events are the primary pattern.

**Q: How long does a subgraph sync take?**  
A: Depends on `startBlock` distance and event density — minutes to hours on mainnet.

---

## 12. GraphQL for Blockchain Data

**A query language used to fetch structured on-chain data from subgraphs and indexers — you request exactly the fields you need.**

### Real-World Dev Example
```graphql
# Query a subgraph for last 10 transfers
{
  transfers(first: 10, orderBy: timestamp, orderDirection: desc) {
    id
    from
    to
    value
    timestamp
  }
}
```

```typescript
// In React with urql or Apollo
import { useQuery } from "urql";
const TRANSFERS = `{ transfers(first:10) { from to value } }`;
const [result] = useQuery({ query: TRANSFERS });
```

### ASCII Diagram
```
REST approach:         GraphQL approach:
GET /transfers         POST /subgraph
GET /users/:id    vs   { transfers { from to value } }
GET /tokens            ← single request, exact fields
(3 round trips)        (1 round trip)
```

### Gotchas & Dev Context
- No real-time subscriptions on most subgraph endpoints — poll or use WebSockets separately
- Pagination uses `first`, `skip`, or cursor-based `where: {id_gt: lastId}` pattern
- Data may lag 1–5 blocks behind chain tip (indexing delay)
- Use `@skip` and `@include` directives for conditional fields

### Production FAQ
**Q: Can I use GraphQL to write data on-chain?**  
A: No — GraphQL here is read-only. Writes still go through ethers/viem and the JSON-RPC API.

**Q: What's the difference between The Graph and a centralized GraphQL API?**  
A: The Graph is decentralized and trustless; a centralized API (like Alchemy's) is faster but you trust the provider.

---

## 13. IPFS (InterPlanetary File System)

**A peer-to-peer distributed file system where content is addressed by its hash (CID), not a URL — "content-addressed storage."**

### Real-World Dev Example
```bash
# Upload a file
ipfs add my-nft-metadata.json
# Returns: QmXyz123...  (CID)

# Access via gateway
https://ipfs.io/ipfs/QmXyz123...
https://gateway.pinata.cloud/ipfs/QmXyz123...
```

```json
// NFT metadata stored on IPFS
{
  "name": "Cool NFT #1",
  "description": "A cool NFT",
  "image": "ipfs://QmImageHash..."
}
```

### ASCII Diagram
```
Upload file → Hash(content) = CID
                  │
       Store on IPFS nodes globally
                  │
Anyone with CID can retrieve from nearest node
(content never changes — same CID = same file)
```

### Gotchas & Dev Context
- Files are NOT permanent by default — nodes garbage-collect unpinned content
- You must **pin** files (via Pinata, NFT.Storage, or your own node) to keep them available
- `ipfs://` URIs don't work in regular browsers — need gateway or IPFS-aware browser
- CID v0 starts with `Qm`, CID v1 starts with `bafy` (different hashing/encoding)
- Large files can be slow to retrieve; not suitable for frequently-updated content

### Production FAQ
**Q: Is IPFS the same as a blockchain?**  
A: No. IPFS is just distributed file storage — no consensus, no immutability guarantees without pinning.

**Q: Can I update a file on IPFS?**  
A: Not in-place. You upload a new version (new CID). Use IPNS for a mutable pointer to the latest CID.

---

## 14. Arweave (Permanent Storage)

**A blockchain-like protocol where you pay once and files are stored permanently — the "permaweb."**

### Real-World Dev Example
```bash
npm install arweave
```

```typescript
import Arweave from "arweave";
const arweave = Arweave.init({ host: "arweave.net", port: 443, protocol: "https" });
const tx = await arweave.createTransaction({ data: JSON.stringify(metadata) });
tx.addTag("Content-Type", "application/json");
await arweave.transactions.sign(tx, jwk);
await arweave.transactions.post(tx);
// Access: https://arweave.net/<txId>
```

### IPFS vs Arweave
| Feature         | IPFS                  | Arweave               |
|-----------------|-----------------------|-----------------------|
| Permanence      | Requires pinning      | Guaranteed permanent  |
| Cost            | Ongoing (pinning)     | One-time upfront      |
| Speed           | Variable              | ~2 min confirmation   |
| Mutability      | IPNS for updates      | Immutable always      |

### Gotchas & Dev Context
- Payment is in AR tokens — factor cost into dApp UX (users may not want to pay)
- Bundlr (now Irys) is a Layer 2 for Arweave — instant uploads, batched AR payments
- `ar://txId` URI scheme; accessed via `arweave.net` gateway
- Good fit for NFT metadata, legal docs, and anything needing provable permanence

### Production FAQ
**Q: How much does it cost to store on Arweave?**  
A: Roughly $0.005–$0.01 per MB; a standard NFT JSON is fractions of a cent.

**Q: Can data on Arweave be deleted?**  
A: No — that's the point. Don't upload anything you'd want removed (PII, sensitive data).

---

## 15. Pinata / NFT.Storage

**Managed IPFS pinning services — they host your files on IPFS nodes so content stays available without running your own node.**

### Real-World Dev Example
```typescript
// Pinata SDK
import { PinataSDK } from "pinata";
const pinata = new PinataSDK({ pinataJwt: process.env.PINATA_JWT });

const upload = await pinata.upload.json({
  name: "NFT #1", description: "My NFT", image: "ipfs://QmImage..."
});
console.log(upload.IpfsHash); // QmMetadataHash...
```

```bash
# Or via Pinata API directly
curl -X POST https://api.pinata.cloud/pinning/pinJSONToIPFS \
  -H "Authorization: Bearer $PINATA_JWT" \
  -H "Content-Type: application/json" \
  -d '{"pinataContent": {"name":"NFT #1"}}'
```

### Gotchas & Dev Context
- **NFT.Storage** (built by Protocol Labs) was free but sunset its free tier in 2024 — check current pricing
- Pinata free tier: 1GB storage — fine for development, paid plans for production
- Both return IPFS CIDs — your contract stores the CID, not the Pinata URL
- Always use `ipfs://CID` in NFT metadata, not `https://gateway.pinata.cloud/ipfs/CID` — gateways can go down
- Pinata also offers its own gateway with faster response times on paid plans

### Production FAQ
**Q: What happens to my NFT files if Pinata goes down?**  
A: The files live on IPFS — anyone else pinning the same CID keeps it alive. Consider dual-pinning with two services.

**Q: Should I store images on IPFS or Arweave for NFTs?**  
A: Arweave for true permanence guarantees; IPFS + Pinata for most NFT projects (cheaper, simpler, widely supported).

---

## 16. Tenderly (Debugging & Simulation)

**A smart contract development platform for transaction simulation, debugging, alerting, and gas profiling — without touching mainnet.**

### Real-World Dev Example
```bash
npm install @tenderly/hardhat-tenderly
```

```typescript
// Simulate a transaction before sending
const sim = await tenderly.simulate({
  network_id: "1",
  from: "0xSender",
  to: "0xContract",
  input: encodedCalldata,
  gas: 500000,
  value: "0",
  save: true,
});
console.log(sim.transaction.status); // "true" = success
```

Or use the Tenderly Dashboard:
- Paste any tx hash → full execution trace, stack frames, variable state at each step

### Gotchas & Dev Context
- **Virtual TestNets**: fork mainnet at any block, simulate sequences of txs — team-shareable
- **Alerts**: trigger webhooks/email when a contract function is called or value changes
- **Gas Profiler**: see which line of Solidity costs the most gas
- Free tier has limited simulations; production teams use paid plans
- Integrates with Hardhat for automatic contract verification

### Production FAQ
**Q: Can Tenderly debug a failed transaction that already happened on mainnet?**  
A: Yes — paste the failed tx hash in the dashboard for a full revert reason and call trace.

**Q: What's the difference between Tenderly simulation and `eth_call`?**  
A: `eth_call` just returns success/fail. Tenderly simulation gives full execution traces, state diffs, event logs, and gas per opcode.

---

## 17. Slither / Mythril / Echidna (Security Tools)

**Static analysis and fuzzing tools to detect vulnerabilities in Solidity contracts before deployment.**

### Real-World Dev Example
```bash
# Slither — static analysis (fast, many detectors)
pip install slither-analyzer
slither . --detect reentrancy-eth,unprotected-upgrade
slither contracts/MyToken.sol

# Mythril — symbolic execution (deeper but slower)
pip install mythril
myth analyze contracts/MyToken.sol --solv 0.8.24

# Echidna — property-based fuzzing
# Write invariant functions, Echidna tries to break them
echidna . --contract MyTokenTest --config echidna.yaml
```

```solidity
// Echidna invariant example
function echidna_balance_never_negative() public view returns (bool) {
    return token.balanceOf(address(this)) >= 0;
}
```

### Tool Comparison
| Tool     | Type              | Speed  | Depth    | Best For                |
|----------|-------------------|--------|----------|-------------------------|
| Slither  | Static analysis   | Fast   | Medium   | CI pipeline, quick scan |
| Mythril  | Symbolic execution| Slow   | Deep     | Complex logic bugs      |
| Echidna  | Fuzzing           | Medium | Property | Invariant verification  |

### Gotchas & Dev Context
- Slither has 80+ built-in detectors — run it in CI on every PR
- False positives are common — triage carefully; add `//slither-disable-next-line` where needed
- Echidna requires writing test invariants in Solidity — investment pays off for complex protocols
- None of these replace a manual audit for high-value contracts
- Foundry's `forge fuzz` is a lighter alternative to Echidna for basic fuzzing

### Production FAQ
**Q: Should I run all three tools on every contract?**  
A: Run Slither always (it's fast). Use Mythril/Echidna for critical, complex contracts or pre-audit preparation.

**Q: What's the most common vulnerability Slither catches?**  
A: Reentrancy, unchecked return values, unprotected `selfdestruct`, and missing access control on sensitive functions.

---

*Batch 9 complete — you now have the full Web3 dev stack from local tooling to security auditing.*
