# Batch 8 — Wallets & Transactions
> How users sign, send, and track transactions on-chain.

---

## Table of Contents
1. [Wallet Types](#1-wallet-types-hot-cold-hardware-multisig)
2. [MetaMask](#2-metamask)
3. [WalletConnect](#3-walletconnect)
4. [Account Abstraction (ERC-4337)](#4-account-abstraction-erc-4337)
5. [Bundler & Paymaster](#5-bundler--paymaster)
6. [Smart Contract Wallet (Safe, Biconomy)](#6-smart-contract-wallet-safe-biconomy)
7. [Transaction Lifecycle](#7-transaction-lifecycle-create--sign--broadcast--mine--confirm)
8. [Transaction Receipt](#8-transaction-receipt)
9. [Event Logs / Topics](#9-event-logs--topics)
10. [Etherscan / Block Explorer](#10-etherscan--block-explorer)
11. [Gas Estimation](#11-gas-estimation)
12. [Transaction Simulation](#12-transaction-simulation)
13. [Nonce Management](#13-nonce-management)
14. [Stuck / Pending Transactions](#14-stuck--pending-transactions)
15. [Speed Up / Cancel Transaction (Replace-by-Fee)](#15-speed-up--cancel-transaction-replace-by-fee)

---

## 1. Wallet Types (Hot, Cold, Hardware, Multisig)

**A crypto wallet stores private keys — not coins — and comes in several security/convenience trade-off flavours.**

### Real-World Dev Example
Your dApp needs to support both a browser extension wallet (hot) for casual users and a Ledger (hardware) for treasury signers.

```
Hot Wallet      — Online, convenient, higher risk
                  e.g. MetaMask, Coinbase Wallet

Cold Wallet     — Offline, harder to access
                  e.g. paper key, air-gapped PC

Hardware Wallet — Physical USB device (cold + UI)
                  e.g. Ledger, Trezor

Multisig Wallet — N-of-M signatures required
                  e.g. Safe (Gnosis), 2-of-3 signers
```

### ASCII Diagram
```
         Risk ◄──────────────────────► Security
  Hot (browser) ──── Hardware ──── Cold (paper)
         ▲                               ▲
    Fast & easy                  Slow but safe
```

### Gotchas & Dev Context
- **Hot wallets** are fine for end users; never use them for protocol treasuries.
- **Hardware wallets** sign locally — the private key never leaves the device.
- **Multisig** requires multiple confirmations; great for DAOs and shared funds.
- Losing a seed phrase = losing funds permanently. No recovery exists.
- "Wallet address" is the public key hash — safe to share.

### Production FAQ
**Q: Should my protocol's treasury be a hot wallet?**
A: Never. Use a multisig (Safe) with ≥ 3-of-5 signers spread across different devices and owners.

**Q: Can a hardware wallet interact with dApps?**
A: Yes — pair it with MetaMask via USB or Bluetooth. MetaMask handles the UI; Ledger signs the payload.

**Q: What's the difference between a wallet and an account?**
A: An account is the on-chain address. A wallet is the software/hardware that holds the private key that controls that account.

---

## 2. MetaMask

**MetaMask is a browser extension and mobile app that injects an Ethereum provider (`window.ethereum`) into web pages, letting dApps request signatures and transactions.**

### Real-World Dev Example
A user visits Uniswap. MetaMask injects `window.ethereum`. Uniswap calls `eth_requestAccounts` to connect, then `eth_sendTransaction` to swap tokens.

```js
// Connect MetaMask
const [account] = await window.ethereum.request({
  method: 'eth_requestAccounts',
});

// Send ETH with ethers.js v6
import { BrowserProvider } from 'ethers';
const provider = new BrowserProvider(window.ethereum);
const signer   = await provider.getSigner();
const tx = await signer.sendTransaction({
  to:    '0xRecipient...',
  value: parseEther('0.01'),
});
```

### Gotchas & Dev Context
- `window.ethereum` may be `undefined` — always check before using.
- Multiple wallet extensions can conflict; use EIP-6963 for multi-wallet discovery.
- MetaMask does **not** store funds — it only stores keys.
- Network switching must be triggered by the dApp via `wallet_switchEthereumChain`.
- Mobile MetaMask uses its built-in browser — deep links required for mobile dApps.

### Production FAQ
**Q: How do I detect which network the user is on?**
A: Listen to the `chainChanged` event and read `window.ethereum.chainId`. Always validate the chain matches your contract's deployment.

**Q: My dApp works in MetaMask but not Coinbase Wallet — why?**
A: Each wallet implements EIP-1193 slightly differently. Use a wallet abstraction library like `wagmi` or `web3-onboard` to normalise behaviour.

**Q: Can MetaMask sign messages without sending a transaction?**
A: Yes — use `eth_signTypedData_v4` (EIP-712) for structured off-chain signatures (e.g. permit approvals, gasless relays).

---

## 3. WalletConnect

**WalletConnect is an open protocol that lets mobile wallets connect to desktop dApps by scanning a QR code — no extension needed.**

### Real-World Dev Example
A user opens your dApp on a laptop. They click "Connect Wallet" → choose "WalletConnect" → scan the QR with their Trust Wallet → approve on mobile. All signing then happens on the phone.

### ASCII Diagram
```
  Desktop dApp                    Mobile Wallet
  ┌──────────┐   QR / deep link   ┌───────────┐
  │  Browser │ ─────────────────► │  Wallet   │
  │   dApp   │ ◄───────── sign ── │  App      │
  └──────────┘                    └───────────┘
          Both connected via WalletConnect relay
```

### How It Works
1. dApp generates a session URI and shows a QR code.
2. Wallet scans, establishes encrypted WebSocket tunnel via a relay server.
3. dApp sends JSON-RPC requests; wallet approves/rejects on device.

```js
// Using wagmi + WalletConnect v2
import { WalletConnectConnector } from 'wagmi/connectors/walletConnect';
const connector = new WalletConnectConnector({
  options: { projectId: 'YOUR_WC_PROJECT_ID' },
});
```

### Gotchas & Dev Context
- WalletConnect **v1 is deprecated** — always use v2 with a project ID from cloud.walletconnect.com.
- The relay server is centralised — a relay outage can break connections.
- Session persistence: v2 sessions can survive page refreshes.
- Mobile deep-linking (for mobile-to-mobile) needs extra config.

### Production FAQ
**Q: Do I need a backend to use WalletConnect?**
A: No — the relay server is provided by WalletConnect. You only need a free project ID.

**Q: WalletConnect QR expired before my user scanned it — what happened?**
A: Sessions have a TTL (~5 min for the pairing). Re-generate the QR on expiry. Implement a "Refresh QR" button.

---

## 4. Account Abstraction (ERC-4337)

**Account Abstraction (AA) lets smart contracts act as wallets — enabling features like gas sponsorship, batch transactions, and social recovery without changing Ethereum's core protocol.**

### Real-World Dev Example
A gaming dApp uses AA so new players can sign up with email (no seed phrase), pay gas in USDC, and batch 10 in-game actions into one transaction.

### ASCII Diagram
```
  User Action
      │
      ▼
  UserOperation  ──►  Bundler  ──►  EntryPoint Contract
  (pseudo-tx)                       │
                                    ▼
                              Smart Account
                              (your wallet contract)
                                    │
                                    ▼
                              Target Contract
```

### Core Concepts
| Term | Meaning |
|---|---|
| UserOperation | AA's version of a transaction |
| EntryPoint | Singleton contract that validates & executes ops |
| Smart Account | The user's contract wallet |
| Bundler | Collects UserOps and submits them on-chain |
| Paymaster | Optional contract that pays gas for users |

### Gotchas & Dev Context
- ERC-4337 requires **no consensus changes** — it works on Ethereum today.
- Each `UserOperation` goes through a **validation** then **execution** phase.
- `initCode` in the UserOp deploys the smart account on first use.
- Not all bundlers are compatible — use a provider like Alchemy/Pimlico.

### Production FAQ
**Q: Does AA replace EOAs (regular wallets)?**
A: No — EOAs still exist. AA adds smart contract wallets as a complementary option.

**Q: Is ERC-4337 live on mainnet?**
A: Yes — the EntryPoint v0.6 and v0.7 are deployed on Ethereum mainnet and major L2s.

---

## 5. Bundler & Paymaster

**A Bundler collects multiple UserOperations and submits them on-chain as one transaction; a Paymaster is a smart contract that sponsors (pays) the gas for users.**

### Real-World Dev Example
Your NFT minting dApp uses Pimlico as a Bundler and a Paymaster so users can mint for free (you absorb gas costs). The Paymaster debits your deposited ETH in the EntryPoint.

### ASCII Diagram
```
  Users                 Bundler                EntryPoint
  ─────                 ───────                ──────────
  UserOp A ──►          Collects A, B, C  ──►  Validates all
  UserOp B ──►                                  Calls Paymaster
  UserOp C ──►          Submits as 1 tx         Executes ops
                                                Pays Bundler fee
                        ▲
                   Paymaster
                (covers user gas)
```

### Gotchas & Dev Context
- Bundlers earn the `maxFeePerGas` - `baseFee` spread, like miners.
- Paymasters must deposit ETH into the EntryPoint as a stake.
- A Paymaster can require ERC-20 payment from the user off-chain, then pay gas in ETH.
- Simulation (`eth_estimateUserOperationGas`) must pass before a bundler accepts the op.
- Bundler mempool is separate from the regular Ethereum mempool.

### Production FAQ
**Q: Can I run my own Bundler?**
A: Yes — open-source bundlers exist (Skandha, Alto, Stackup). In practice, use a managed provider (Alchemy, Pimlico, Biconomy) in production.

**Q: What happens if my Paymaster runs out of stake?**
A: UserOps requiring that Paymaster will be rejected by the bundler. Monitor stake balance and top up proactively.

---

## 6. Smart Contract Wallet (Safe, Biconomy)

**A smart contract wallet is an Ethereum account controlled by code instead of a single private key — enabling multisig, spending limits, recovery, and programmable rules.**

### Real-World Dev Example
A DAO uses a **Safe** (formerly Gnosis Safe) 4-of-7 multisig as its treasury. Any transaction requires 4 of 7 board members to sign before execution.

```
Safe Multisig Flow:
  Signer 1 ──┐
  Signer 2 ──┤ Propose & collect sigs
  Signer 3 ──┤ (off-chain)
  Signer 4 ──┘
              │
              ▼
         Safe Contract  ──►  Execute on-chain
```

### Popular Implementations

| Wallet | Key Feature |
|---|---|
| **Safe** | Battle-tested multisig, DAO standard |
| **Biconomy** | AA-native, gasless UX, SDK-friendly |
| **Kernel (ZeroDev)** | Modular AA, plugins system |
| **Coinbase Smart Wallet** | Passkey auth, no seed phrase |

### Gotchas & Dev Context
- Smart wallets have a **deployment cost** (~100k gas for first use).
- Counterfactual deployment: the address exists before the contract is deployed (using `CREATE2`).
- Safe's `execTransaction` needs threshold signatures collected and concatenated.
- ERC-4337 compatibility varies — check if your chosen wallet implements `IAccount`.

### Production FAQ
**Q: Is a Safe address deterministic across chains?**
A: Yes — same deployer + salt + bytecode = same address on every EVM chain. Use Safe's multi-chain deployment tool to ensure consistency.

**Q: Can a smart wallet receive ETH before it's deployed?**
A: Yes — funds sent to the counterfactual address are safe. They'll be accessible once the wallet is deployed on first use.

---

## 7. Transaction Lifecycle (Create → Sign → Broadcast → Mine → Confirm)

**A transaction goes through five stages from intent to irreversible settlement on the blockchain.**

### Real-World Dev Example
Alice sends 1 ETH to Bob using her dApp.

### ASCII Diagram
```
  1. CREATE        2. SIGN         3. BROADCAST
  ┌──────────┐    ┌──────────┐    ┌──────────┐
  │ Build tx │───►│ Sign with│───►│ Send to  │
  │ object   │    │ priv key │    │ mempool  │
  └──────────┘    └──────────┘    └──────────┘
                                       │
                                       ▼
                  5. CONFIRM    4. MINE
                  ┌──────────┐ ┌──────────┐
                  │ 12+ blocks│◄│ Validator│
                  │ = final  │ │ picks up │
                  └──────────┘ └──────────┘
```

### Stage Breakdown
| Stage | What Happens |
|---|---|
| **Create** | Build tx object: `to`, `value`, `data`, `gasLimit`, `nonce` |
| **Sign** | ECDSA sign with private key → produces `v`, `r`, `s` |
| **Broadcast** | Submit raw signed tx to an RPC node → enters mempool |
| **Mine** | A validator includes tx in a block |
| **Confirm** | Each subsequent block adds a "confirmation"; ~12 = finality |

### Gotchas & Dev Context
- A tx in the mempool is **not confirmed** — it can be dropped or replaced.
- On Ethereum PoS, 1 confirmation ≈ ~12 seconds; finality ≈ 2 epochs (~12 min).
- L2s (Arbitrum, OP) have near-instant "soft" confirmation but inherit Ethereum finality later.
- Always wait for enough confirmations before releasing funds or assets.

### Production FAQ
**Q: How many confirmations should I wait for before crediting a deposit?**
A: For low-value: 1–3. For high-value (CEXes, bridges): 12–64. L2s vary — check chain-specific guidance.

**Q: Can a transaction be reversed after mining?**
A: Not on PoS Ethereum without a chain reorganisation (extremely rare post-Merge). Treat mined transactions as final after a few blocks.

---

## 8. Transaction Receipt

**A transaction receipt is the on-chain record returned after a transaction is mined — it contains the outcome (success/fail), gas used, and all events emitted.**

### Real-World Dev Example
After minting an NFT, your frontend checks the receipt to confirm success and extract the token ID from the `Transfer` event.

```js
// ethers.js v6
const tx      = await contract.mint(recipient);
const receipt = await tx.wait(); // waits for 1 confirmation

console.log(receipt.status);    // 1 = success, 0 = reverted
console.log(receipt.gasUsed);   // actual gas consumed
console.log(receipt.logs);      // raw event logs
```

### Key Fields
| Field | Description |
|---|---|
| `transactionHash` | Unique tx identifier |
| `blockNumber` | Block it was included in |
| `status` | `1` = success, `0` = revert |
| `gasUsed` | Actual gas consumed (not limit) |
| `logs` | Array of emitted events |
| `contractAddress` | Set if tx deployed a contract |

### Gotchas & Dev Context
- `status: 0` means the tx **reverted but gas was still spent** — never refunded.
- `tx.wait(n)` waits for `n` confirmations (default: 1).
- A receipt only exists after mining — if the tx is pending, `getTransactionReceipt()` returns `null`.
- Logs are raw ABI-encoded — decode them with your contract's ABI to read values.

### Production FAQ
**Q: The receipt shows `status: 0` — how do I see why it reverted?**
A: Call the tx via `eth_call` at the same block height — it will return the revert reason string. Tools like Tenderly do this automatically.

**Q: Can a receipt have `status: 1` but the user's action still failed?**
A: Yes — if an internal call fails silently (old Solidity patterns without `revert`). Always check emitted events, not just `status`.

---

## 9. Event Logs / Topics

**Event logs are structured data emitted by smart contracts during execution — the primary way to observe what happened inside a transaction.**

### Real-World Dev Example
The ERC-20 `Transfer` event is emitted every time tokens move. Your indexer listens for it to update user balances in your database.

```solidity
// Solidity
event Transfer(address indexed from, address indexed to, uint256 value);
emit Transfer(msg.sender, recipient, amount);
```

```js
// ethers.js: query past events
const filter = token.filters.Transfer(null, userAddress);
const events = await token.queryFilter(filter, fromBlock, toBlock);
events.forEach(e => console.log(e.args.value.toString()));
```

### Anatomy of a Log
```
Log {
  address:  "0xTokenContract",   // who emitted it
  topics: [
    "0xddf252...",  // [0] keccak256("Transfer(address,address,uint256)")
    "0x000...alice",// [1] indexed param: from
    "0x000...bob",  // [2] indexed param: to
  ],
  data: "0x000...100"  // non-indexed params (value)
}
```

### Gotchas & Dev Context
- Up to **3 indexed params** per event (each becomes a `topic`).
- Non-indexed params go into `data` — must be ABI-decoded.
- Events are **not accessible from other smart contracts** — they're for off-chain consumers only.
- `topic[0]` is always the event signature hash — use it to identify the event type.
- Logs are pruned by some nodes — use an archive node or The Graph for historical queries.

### Production FAQ
**Q: How do I listen for events in real time?**
A: Use `contract.on('EventName', handler)` with a WebSocket provider (e.g. `wss://` endpoint). HTTP polling also works via `queryFilter` with a block interval.

**Q: Why can't I filter by a non-indexed parameter?**
A: Non-indexed params are ABI-encoded in `data` — the EVM doesn't index them for lookup. Make fields `indexed` if you need to filter by them.

---

## 10. Etherscan / Block Explorer

**A block explorer is a web interface that lets anyone inspect transactions, addresses, blocks, and contracts on a blockchain — Etherscan is the most popular for Ethereum.**

### Real-World Dev Example
A user reports a failed transaction. You paste the tx hash into Etherscan to see the revert reason, gas used, and which internal call failed — all without running any code.

### Key Features Used in Dev

| Feature | URL Pattern | Use Case |
|---|---|---|
| Tx details | `/tx/0x...` | Debug failures, check status |
| Address page | `/address/0x...` | View token balances, tx history |
| Contract tab | `/address/0x...#code` | Verify & read source code |
| Event logs | `/tx/0x...#eventlog` | Inspect emitted events |
| Gas tracker | `/gastracker` | Estimate current gas price |

### Gotchas & Dev Context
- **Verify your contracts** on Etherscan so users can read and interact with the ABI directly.
- Etherscan has a free API (`api.etherscan.io`) — rate-limited to 5 req/s on free tier.
- "Internal transactions" on Etherscan are ETH transfers via contract calls — not native txs.
- Each chain has its own explorer: Polygonscan, Arbiscan, Basescan, etc.
- Unverified contracts show only bytecode — a red flag for users.

### Production FAQ
**Q: How do I verify a contract deployed with a constructor argument?**
A: Use Etherscan's "Verify & Publish" with ABI-encoded constructor args, OR use `hardhat-etherscan` / `foundry`'s `forge verify-contract` which handles it automatically.

**Q: Can Etherscan show why my tx reverted?**
A: Yes — on the tx page, Etherscan decodes the revert reason if it's a standard string. For complex failures, use Tenderly's trace debugger.

---

## 11. Gas Estimation

**Gas estimation predicts how much computational work (gas) a transaction will consume before it is actually sent — preventing out-of-gas failures.**

### Real-World Dev Example
Before calling `stake()` on a contract, your dApp calls `estimateGas` so it can set the `gasLimit` 20% above the estimate for safety.

```js
// viem
import { createPublicClient, http } from 'viem';
const client = createPublicClient({ transport: http(RPC_URL) });

const gas = await client.estimateGas({
  account: userAddress,
  to:      contractAddress,
  data:    encodedCallData,
});
// Add 20% buffer
const gasLimit = (gas * 120n) / 100n;
```

### How It Works
```
  eth_estimateGas RPC call
        │
        ▼
  Node runs the tx in EVM  ──► Returns gas consumed
  (simulation, no broadcast)    (or throws if it reverts)
```

### Gotchas & Dev Context
- `estimateGas` **reverts** if the transaction would revert — useful for early validation.
- The estimate is not guaranteed: on-chain state can change between estimation and mining.
- Always add a **10–20% buffer** to the raw estimate.
- L2s have additional L1 data fees not captured by `estimateGas` — use chain-specific SDKs.
- ERC-20 `approve` + contract call estimation requires the approval to be set first, or the estimate will be wrong.

### Production FAQ
**Q: My estimation keeps reverting even though the tx looks correct — why?**
A: The estimating node sees the current state. Check: insufficient token allowance, wrong `msg.sender` context, or a require/revert in the contract for your inputs.

**Q: Should I hardcode gas limits?**
A: No — contract logic can change after upgrades. Always estimate dynamically and add a buffer.

---

## 12. Transaction Simulation

**Transaction simulation dry-runs a transaction against the current (or a forked) blockchain state to predict its outcome — without spending gas or submitting it on-chain.**

### Real-World Dev Example
Before a whale executes a 10 000 ETH DeFi position, your dApp simulates it via Tenderly to verify slippage, token flows, and that it won't revert.

```js
// Using Tenderly Simulation API
const response = await fetch('https://api.tenderly.co/api/v1/simulate', {
  method: 'POST',
  headers: { 'X-Access-Key': TENDERLY_KEY },
  body: JSON.stringify({
    network_id: '1',
    from:       userAddress,
    to:         contractAddress,
    input:      encodedData,
    gas:        500000,
    save:       true,
  }),
});
const { simulation } = await response.json();
console.log(simulation.status); // true = success
```

### Tools
| Tool | What It Offers |
|---|---|
| **Tenderly** | Full trace, state diff, shareable links |
| **eth_call** | Basic simulation via any RPC node |
| **Alchemy Simulate** | Asset changes, approvals preview |
| **Foundry fork** | Local anvil fork for test simulation |

### Gotchas & Dev Context
- Simulation uses a **snapshot of current state** — results may differ at actual mining time.
- MEV bots simulate txs to find profitable sandwich opportunities against your tx.
- Showing users a "preview" of token changes (via simulation) dramatically reduces support tickets.
- `eth_call` is the free baseline; Tenderly/Alchemy add human-readable traces.

### Production FAQ
**Q: Is simulation 100% accurate?**
A: No — frontrunning, state changes in the same block, or oracle price movements can alter the real outcome. Treat simulation as a strong signal, not a guarantee.

**Q: Can I simulate with a different `block.timestamp` or state?**
A: Yes — use a local Foundry/Anvil fork with `vm.warp()` and `vm.store()` to manipulate state in tests.

---

## 13. Nonce Management

**A nonce is a per-account counter that must increment by exactly 1 for each transaction — it prevents replay attacks and enforces transaction ordering.**

### Real-World Dev Example
A backend service sends 5 reward payouts simultaneously. Without managing nonces, all 5 transactions get the same nonce and only 1 executes; the others are dropped.

```js
// ethers.js: manual nonce management
const nonce = await provider.getTransactionCount(wallet.address, 'pending');

const txs = await Promise.all([
  wallet.sendTransaction({ to: addr1, value: v, nonce: nonce }),
  wallet.sendTransaction({ to: addr2, value: v, nonce: nonce + 1 }),
  wallet.sendTransaction({ to: addr3, value: v, nonce: nonce + 2 }),
]);
```

### Nonce Rules
```
  Account Nonce = 5

  Send tx with nonce 5  → accepted, queued
  Send tx with nonce 6  → accepted, queued (gap if 5 pending)
  Send tx with nonce 4  → REJECTED (too low / replay)
  Send tx with nonce 5  → replaces existing nonce-5 tx (if higher gas)
```

### Gotchas & Dev Context
- Use `'pending'` tag in `getTransactionCount` to include mempool txs in the count.
- A **nonce gap** (e.g. nonces 5 and 7 submitted, 6 missing) stalls all subsequent txs.
- For high-throughput backends, maintain a nonce counter in Redis to avoid race conditions.
- Hardware wallets and dApps auto-manage nonces — manual control is mostly a backend concern.

### Production FAQ
**Q: My backend sent the wrong nonce and now transactions are stuck — how do I fix it?**
A: Send a filler transaction (e.g. send 0 ETH to yourself) with the missing nonce and sufficient gas to unblock the queue.

**Q: Two server instances incremented the nonce simultaneously — how do I prevent this?**
A: Use a distributed lock (Redis `SET NX`) around nonce fetch + tx broadcast, or use a dedicated signing queue/service.

---

## 14. Stuck / Pending Transactions

**A pending transaction is one that has been broadcast to the mempool but not yet mined — usually because its gas price is too low for validators to prioritise it.**

### Real-World Dev Example
A user sent a transaction during a gas spike with 20 gwei but the network requires 80 gwei. The transaction sits in the mempool for hours.

### ASCII Diagram
```
  User sends tx (20 gwei)
          │
          ▼
       Mempool
    ┌─────────────┐
    │ tx: 20 gwei │ ◄── Validators skip (too cheap)
    │ (pending)   │
    └─────────────┘
          │
    Replace with same nonce + higher fee
          │
          ▼
    ┌─────────────┐
    │ tx: 90 gwei │ ──► Mined ✓
    └─────────────┘
```

### Why Transactions Get Stuck
- `maxFeePerGas` set below `baseFee` → node won't accept it.
- Network congestion spiked after submission.
- Nonce gap (previous nonce unresolved).
- RPC node broadcast silently failed.

### Gotchas & Dev Context
- A transaction in the mempool is **not guaranteed to be mined** — it can be evicted after hours.
- Nodes limit mempool slots — very old low-fee txs are eventually dropped.
- The sender's ETH is **not locked** while the tx is pending (balance is checked at mining time).
- EIP-1559 txs with `maxFeePerGas` < current `baseFee` are immediately rejected by the node.

### Production FAQ
**Q: How long before a stuck tx is dropped from the mempool?**
A: Varies by node — Geth defaults to ~3 hours. After that it's simply gone and you can reuse the nonce.

**Q: Can I cancel a pending transaction?**
A: Yes — replace it with the same nonce sending 0 ETH to yourself with a higher gas price. If it mines first, the original is cancelled. See RBF below.

---

## 15. Speed Up / Cancel Transaction (Replace-by-Fee)

**Replace-by-Fee (RBF) is a mechanism to replace a pending transaction by broadcasting a new transaction with the same nonce but a higher gas price — either to speed it up or cancel it.**

### Real-World Dev Example
Your user minted an NFT 10 minutes ago but it's stuck. They click "Speed Up" in your dApp, which rebroadcasts the same transaction with gas bumped by 20%.

```js
// ethers.js: speed up (same data, higher gas)
const pendingTx = await provider.getTransaction(txHash);
const newTx = await signer.sendTransaction({
  to:                  pendingTx.to,
  data:                pendingTx.data,
  value:               pendingTx.value,
  nonce:               pendingTx.nonce,          // same nonce
  maxFeePerGas:        pendingTx.maxFeePerGas * 130n / 100n, // +30%
  maxPriorityFeePerGas: pendingTx.maxPriorityFeePerGas * 130n / 100n,
});

// Cancel: same nonce, no data, higher gas
const cancelTx = await signer.sendTransaction({
  to:    signer.address,  // send to self
  value: 0n,
  nonce: pendingTx.nonce,
  maxFeePerGas: pendingTx.maxFeePerGas * 130n / 100n,
});
```

### Speed Up vs Cancel
```
  Speed Up  → same nonce + same data + higher gas
                If mined: original intent executes faster

  Cancel    → same nonce + empty data + higher gas
                If mined: original tx is replaced with a no-op
```

### Gotchas & Dev Context
- The replacement must be at least **10% higher** gas than the original (node policy).
- There's a **race**: if the original mines before the replacement, the replacement is dropped.
- Cancellation is **not guaranteed** — if the original mines first, the cancel never executes.
- MetaMask's "Speed Up" and "Cancel" buttons do exactly this under the hood.
- EIP-1559: bump **both** `maxFeePerGas` and `maxPriorityFeePerGas` by ≥10%.

### Production FAQ
**Q: The cancel transaction also got stuck — what now?**
A: The cancel tx itself needs a higher fee than your original cancel attempt. Keep bumping by 20–30% until it mines. If the original mines first, you spent gas for nothing.

**Q: Can validators ignore my replacement and mine the original?**
A: Yes — if the original tx was already propagated to many nodes, some validators may have it cached. This is a race condition inherent to RBF. Use Flashbots or private mempools to get more control.

**Q: Is there a way to guarantee cancellation?**
A: Not on a public mempool. Private transaction services (Flashbots Protect, MEV Blocker) give you more control by keeping txs off the public mempool until confirmed.

---

*Batch 8 complete — 15 terms covering wallets, signing, and the full transaction lifecycle.*
