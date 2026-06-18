# Batch 14 — Frontend & dApp Architecture
> Building user-facing applications that interact with smart contracts.

---

## 1. dApp Architecture Overview

**One-line definition:** A dApp (decentralized application) pairs a normal web frontend with a blockchain backend instead of a centralized server.

### Real-World Dev Example
A DEX like Uniswap: React UI → wallet signs a swap → transaction hits an EVM smart contract → state is stored on-chain forever.

### ASCII Diagram
```
[ Browser / React App ]
        |
   [ Wallet (signer) ]
        |
 [ JSON-RPC Provider ]   ←── Infura / Alchemy / public node
        |
  [ Smart Contract ]  ←── on-chain logic & storage
        |
  [ Event Logs / IPFS / The Graph ]  ←── data layer
```

### Gotchas & Dev Context
- There is no "backend server" — the node RPC endpoint IS your backend.
- The frontend is still hosted somewhere (Vercel, Fleek, IPFS); only the *logic* is decentralized.
- Contract ABI must stay in sync with the deployed bytecode or calls silently fail.
- Rate-limit your RPC calls; free tiers on Alchemy/Infura cap at ~300 req/s.

### Production FAQ
**Q: Can I still use a REST API alongside a dApp?**
A: Yes — hybrid architectures (off-chain compute + on-chain settlement) are common for performance-critical features.

**Q: Who pays for storage in a dApp?**
A: On-chain storage costs gas (paid by users/contracts). Off-chain storage (IPFS, Arweave) is paid separately by the developer or pinning service.

---

## 2. Connecting Wallet (MetaMask, WalletConnect)

**One-line definition:** Wallet connection hands the frontend a *signer* — an object that can authorize transactions on behalf of the user's address.

### Real-World Dev Example
```tsx
// wagmi v2 + React
import { useConnect } from 'wagmi';
import { injected } from 'wagmi/connectors';

function ConnectBtn() {
  const { connect } = useConnect();
  return (
    <button onClick={() => connect({ connector: injected() })}>
      Connect MetaMask
    </button>
  );
}
```

### ASCII Diagram
```
User clicks "Connect"
       ↓
  MetaMask popup  ←── injected provider (window.ethereum)
       ↓ approve
  Frontend gets { address, chainId, signer }
       ↓
  All tx calls use signer.sendTransaction(...)
```

### Gotchas & Dev Context
- `window.ethereum` is MetaMask's injected provider; WalletConnect uses a QR/deep-link relay — no `window.ethereum` needed.
- Always handle the `chainChanged` and `accountsChanged` events or your UI will show stale data.
- WalletConnect v2 requires a project ID from `cloud.walletconnect.com`.
- Never store the private key — you only ever hold the address and a signer reference.

### Production FAQ
**Q: How do I support mobile wallets without MetaMask?**
A: Use WalletConnect — it works via a relay server that mobile wallets scan with a QR code or deep link.

**Q: What's `wagmi` vs raw `ethers.js`?**
A: wagmi is a React hooks layer built on top of viem; it manages connection state, caching, and re-renders. ethers.js is the lower-level library underneath.

---

## 3. Reading On-Chain Data (View Functions, Events)

**One-line definition:** Reading on-chain data is free (no gas) and done by calling `view`/`pure` functions or querying past event logs from a node.

### Real-World Dev Example
```tsx
// wagmi v2
import { useReadContract } from 'wagmi';

const { data: balance } = useReadContract({
  address: '0xToken...',
  abi: erc20Abi,
  functionName: 'balanceOf',
  args: ['0xUser...'],
});
```

### ASCII Diagram
```
Frontend  ──eth_call──▶  RPC Node  ──▶  EVM (read state)
                ◀── return value (no tx, no gas) ──
```

### Gotchas & Dev Context
- `eth_call` is a simulation; it reads the *current* block state. Data can be stale by seconds.
- Fetching historical events uses `eth_getLogs` — filter by `fromBlock`/`toBlock` and indexed topics.
- Very old logs may be pruned on archive-less nodes; use Alchemy/QuickNode for deep history.
- Polling every block (12 s on mainnet) works, but WebSocket subscriptions are more efficient.

### Production FAQ
**Q: Can I read data without a wallet connected?**
A: Yes — use a *public provider* (e.g., `createPublicClient` in viem). Reading never requires a signer.

**Q: Why does my `balanceOf` return a BigInt that looks wrong in the UI?**
A: ERC-20 tokens use 18 decimals. Divide by `10n ** 18n` or use `formatUnits(balance, 18)` from viem/ethers.

---

## 4. Writing On-Chain Data (Transactions, Gas UX)

**One-line definition:** Writing to the chain means submitting a signed transaction that changes state — it costs gas and takes time to confirm.

### Real-World Dev Example
```tsx
import { useWriteContract } from 'wagmi';

const { writeContract } = useWriteContract();

writeContract({
  address: '0xContract...',
  abi,
  functionName: 'transfer',
  args: ['0xRecipient...', parseEther('1.0')],
});
```

### ASCII Diagram
```
User signs tx  →  Mempool  →  Miner/Validator picks up  →  Block confirmed
     ↑                                                           ↓
  wallet popup                                         State changes on-chain
```

### Gotchas & Dev Context
- Always show a gas estimate *before* the user signs — use `estimateGas()`.
- EIP-1559 txs have `maxFeePerGas` + `maxPriorityFeePerGas`; legacy txs use `gasPrice`.
- Never hardcode gas limits; contracts can change and your hardcoded value may cause OOG errors.
- Reverted transactions still consume gas — make this clear in your UI error messages.

### Production FAQ
**Q: How do I let users set gas speed (slow/standard/fast)?**
A: Fetch the current `baseFee` and offer multipliers for `maxPriorityFeePerGas` (e.g., 1 gwei = slow, 2 gwei = fast).

**Q: What's the difference between `eth_sendTransaction` and `eth_sendRawTransaction`?**
A: `eth_sendTransaction` asks the node to sign (only for unlocked accounts); `eth_sendRawTransaction` sends a pre-signed tx from the wallet — this is what MetaMask always uses.

---

## 5. Transaction State Management (Pending, Confirmed, Failed)

**One-line definition:** After submission, a transaction moves through defined states — your UI must track each one to give users meaningful feedback.

### Real-World Dev Example
```tsx
import { useWaitForTransactionReceipt } from 'wagmi';

const { isLoading, isSuccess, isError } = useWaitForTransactionReceipt({
  hash: txHash,
});
// isLoading → "Pending…", isSuccess → "Done ✓", isError → "Reverted ✗"
```

### ASCII Diagram
```
[Submitted] → [Pending in mempool] → [Mined in block]
                      ↓                     ↓
               [Dropped/Replaced]   [Success | Revert]
```

### Gotchas & Dev Context
- A tx can be *pending* for minutes if gas is too low — let users speed up (replace-by-fee).
- `receipt.status === 1` = success; `status === 0` = reverted (tx was included but logic failed).
- Store `txHash` in local state immediately after submission so you can poll even after page refresh.
- Nonce gaps (missing intermediate nonces) can stall all subsequent txs from the same wallet.

### Production FAQ
**Q: How long should I wait before calling a tx "failed"?**
A: There's no protocol timeout — poll the mempool. After ~5 minutes without inclusion, surface a "stuck" warning and offer a replace-by-fee option.

**Q: Can I recover a dropped transaction?**
A: Resubmit with the same nonce and higher gas. The new tx replaces the old one if accepted by miners.

---

## 6. Optimistic Updates in dApps

**One-line definition:** Show the expected result in the UI *before* the transaction confirms, then reconcile when the chain responds.

### Real-World Dev Example
```tsx
// Immediately update local state
setLikeCount(prev => prev + 1);

writeContract({ functionName: 'likePost', args: [postId] }, {
  onError: () => setLikeCount(prev => prev - 1), // rollback on failure
});
```

### ASCII Diagram
```
User action
    ↓
UI updates immediately  (optimistic state)
    ↓
Tx submitted  →  pending…
    ↓               ↓
  confirmed      reverted
  (keep UI)     (rollback UI + show error)
```

### Gotchas & Dev Context
- Only use optimistic updates when failure is unlikely (e.g., social actions, not financial transfers).
- Always implement a rollback path — don't assume success.
- Chain re-orgs can flip a "confirmed" tx back to pending; for high-value actions wait for 2-3 block confirmations before treating as final.
- Tag optimistic items visually (e.g., greyed out, spinner) so users know it's not yet final.

### Production FAQ
**Q: Is optimistic UI safe for token transfers?**
A: No — show the pending state instead. The risk of showing a wrong balance and having users act on it is too high.

**Q: How do I reconcile optimistic state with on-chain data after confirmation?**
A: Invalidate your cache (e.g., `queryClient.invalidateQueries()` in wagmi/TanStack) after the receipt arrives to re-fetch fresh on-chain data.

---

## 7. Multicall (Batched RPC Calls)

**One-line definition:** Multicall bundles multiple contract reads into a single RPC request, dramatically reducing latency and provider rate-limit usage.

### Real-World Dev Example
```tsx
// wagmi's useReadContracts uses Multicall3 under the hood
import { useReadContracts } from 'wagmi';

const { data } = useReadContracts({
  contracts: tokens.map(addr => ({
    address: addr,
    abi: erc20Abi,
    functionName: 'balanceOf',
    args: [userAddress],
  })),
});
// One RPC call fetches ALL balances
```

### ASCII Diagram
```
Without Multicall:   call1 → call2 → call3  (3 round-trips)
With Multicall:      [call1, call2, call3] → one eth_call to Multicall3 contract
                                           ← [result1, result2, result3]
```

### Gotchas & Dev Context
- Multicall3 is deployed at the same address on most EVM chains: `0xcA11bde05977b3631167028862bE2a173976CA11`.
- Individual call failures in a multicall can be silent — check each `result.status` field.
- Multicall reads are atomic per block; all results come from the same block snapshot.
- Don't use multicall for *writes* — each write must be its own signed transaction.

### Production FAQ
**Q: Does multicall work on every chain?**
A: Multicall3 is deployed on 50+ chains. Check `multicall3.com` for a full list. For unsupported chains, fall back to individual `eth_call`s.

**Q: How many calls can I batch?**
A: Technically hundreds, but keep batches under ~100 to avoid hitting block gas limits in the simulation.

---

## 8. ENS Resolution in Frontend

**One-line definition:** ENS (Ethereum Name Service) maps human-readable names like `vitalik.eth` to wallet addresses — your frontend should both resolve and reverse-resolve them.

### Real-World Dev Example
```tsx
import { useEnsAddress, useEnsName } from 'wagmi';

// Name → Address
const { data: address } = useEnsAddress({ name: 'vitalik.eth' });

// Address → Name (reverse lookup)
const { data: name } = useEnsName({ address: '0xd8dA...' });
```

### ASCII Diagram
```
"vitalik.eth"  →  ENS Registry (on-chain)  →  0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045
                                                           ↑
0xd8dA...  →  Reverse Registrar  →  "vitalik.eth"  ←──────┘
```

### Gotchas & Dev Context
- ENS is on Ethereum mainnet only; L2s / other chains use their own name services (e.g., Lens handles, Unstoppable Domains).
- Always fall back to displaying a truncated address (`0xd8dA…6045`) if ENS resolution fails or returns null.
- ENS avatars are stored in the `avatar` text record — fetch with `getEnsAvatar()`.
- Caching is important: ENS resolution is slow (~200 ms). Cache results in memory or localStorage.

### Production FAQ
**Q: Can a user update their ENS name after I've cached it?**
A: Yes — ENS records can change. Don't cache indefinitely; treat ENS like a DNS TTL (refresh hourly or on re-connect).

**Q: Is ENS resolution free?**
A: Resolution (reading) is free. *Registering* or *updating* an ENS name costs gas.

---

## 9. IPFS Gateway Integration

**One-line definition:** IPFS stores files by content hash; a *gateway* is an HTTP bridge that lets browsers fetch IPFS content without running a node.

### Real-World Dev Example
```tsx
function resolveIpfs(uri: string): string {
  if (uri.startsWith('ipfs://')) {
    return uri.replace('ipfs://', 'https://cloudflare-ipfs.com/ipfs/');
  }
  return uri; // already an HTTP URL
}

// NFT metadata image field often returns: "ipfs://Qm..."
<img src={resolveIpfs(nft.image)} alt={nft.name} />
```

### ASCII Diagram
```
ipfs://QmXyz...
     ↓  (gateway rewrite)
https://cloudflare-ipfs.com/ipfs/QmXyz...
     ↓
Browser fetches normal HTTPS request
```

### Gotchas & Dev Context
- Public gateways (`ipfs.io`, `cloudflare-ipfs.com`) can be slow or rate-limited — use a dedicated gateway (Pinata, Infura IPFS) in production.
- Content addressed by CID is **immutable** — the same CID always returns the same bytes. This is a feature, not a bug.
- IPFS content is only available if at least one node is *pinning* it. Unpinned content disappears.
- `ipfs://` URIs won't work natively in most browsers — always rewrite to HTTP gateway URLs.

### Production FAQ
**Q: What's the difference between IPFS and Arweave for NFT storage?**
A: IPFS requires ongoing pinning (content can disappear); Arweave is a pay-once permanent storage network. Arweave is preferred for long-term NFT metadata.

**Q: Can I self-host an IPFS gateway?**
A: Yes — run an IPFS node and expose port 8080. But a managed gateway (Pinata, Filebase) is more reliable for production.

---

## 10. Decentralized Hosting (Fleek, 4EVERLAND)

**One-line definition:** Decentralized hosting deploys your frontend static files to IPFS/Arweave so no single company can take your dApp offline.

### Real-World Dev Example
```bash
# Fleek CLI deployment
npm install -g @fleek-platform/cli
fleek login
fleek sites init      # configure: build dir = dist/, framework = React
fleek sites deploy    # pushes build to IPFS, returns IPFS CID + .on.fleek.app URL
```

### ASCII Diagram
```
Git push  →  Fleek CI  →  Build (npm run build)
                               ↓
                         IPFS / Filecoin pinning
                               ↓
              yourapp.on.fleek.app  (HTTPS via CDN)
              yourapp.eth           (ENS + IPFS hash)
```

### Gotchas & Dev Context
- The ENS `contenthash` record pointing to your IPFS CID must be updated on every deploy — Fleek can automate this.
- IPFS-hosted SPAs need a redirect rule so all routes point back to `index.html` (use `_redirects` file or hash-based routing).
- 4EVERLAND is an alternative to Fleek with similar IPFS + Arweave support and cheaper pricing tiers.
- Centralized CDN edge nodes (Cloudflare) are often used *in front* of IPFS gateways for speed — you're still partially centralized.

### Production FAQ
**Q: If Fleek shuts down, is my dApp gone?**
A: No — your files live on IPFS. Point your ENS `contenthash` to a new gateway or run your own IPFS node to keep serving it.

**Q: Do I need a custom domain with decentralized hosting?**
A: No — Fleek gives you a `*.on.fleek.app` subdomain. For a `.eth` domain, configure ENS + IPFS hash manually or via Fleek's ENS integration.

---

## 11. Progressive Decentralization Strategy

**One-line definition:** Start with a working product using some centralized components, then systematically replace them with decentralized alternatives as the protocol matures.

### Real-World Dev Example
```
Stage 1 (Launch)     → Centralized backend + smart contracts for core logic
Stage 2 (Growth)     → Replace DB reads with The Graph subgraph
Stage 3 (Maturity)   → Move frontend to IPFS, governance on-chain via DAO
Stage 4 (Full dApp)  → Protocol owned by token holders, no admin keys
```

### ASCII Diagram
```
[Centralized]                              [Decentralized]
     ├─ Hosted API ──────────────────────▶  The Graph
     ├─ Vercel hosting ─────────────────▶  IPFS / Fleek
     ├─ Multisig admin ─────────────────▶  DAO governance
     └─ Off-chain auth ─────────────────▶  Sign-in with Ethereum
```

### Gotchas & Dev Context
- Moving too fast causes user experience regressions — prioritize decentralizing *data* before *hosting*.
- Keep admin upgrade keys (proxy patterns) until you are confident in contract security. Removing them is irreversible.
- Document your roadmap publicly — users want to know when/if the protocol will be fully trustless.
- Regulatory pressure often forces teams to keep some centralized components even late-stage.

### Production FAQ
**Q: When should I hand over admin keys to a DAO?**
A: After a security audit, significant TVL/usage, and a tested governance process. Premature decentralization is a security risk.

**Q: Can I decentralize just parts of my dApp?**
A: Absolutely — partial decentralization is the norm. Even Uniswap v3 uses a centralized frontend hosted on Vercel (with an IPFS fallback).

---

## 12. Hybrid Architecture (Off-Chain Compute + On-Chain Settlement)

**One-line definition:** Heavy computation runs off-chain (cheap, fast), but the final result or proof is committed on-chain (trustless, permanent).

### Real-World Dev Example
```
Chainlink Functions: your JS runs on Chainlink's DON (off-chain),
result is written to your contract via an oracle callback.

Order books (dYdX): matching happens off-chain on a server,
final trade settlement recorded on-chain.
```

### ASCII Diagram
```
User request
     ↓
Off-chain service  (API, ZK prover, oracle node)
     ↓  computes result / generates proof
Smart contract  ←──  result + proof submitted on-chain
     ↓
Settlement / state change stored immutably
```

### Gotchas & Dev Context
- The off-chain component is still a trust assumption — use decentralized oracle networks (Chainlink, API3) to reduce it.
- ZK proofs let you verify off-chain computation trustlessly on-chain (used in zkRollups, zkML).
- Latency: off-chain compute is fast (ms), but on-chain settlement adds block time (seconds to minutes).
- Build circuit-breakers: if the off-chain service is down, your on-chain contract should degrade gracefully, not lock funds.

### Production FAQ
**Q: Is a hybrid dApp still a real dApp?**
A: Yes — most production dApps are hybrid. "Fully decentralized" is a spectrum, not a binary.

**Q: What stops the off-chain service from lying?**
A: Cryptographic proofs (ZK), economic incentives (staking/slashing), or decentralized oracle consensus (Chainlink DON). Choose based on your threat model.

---

## 13. The Graph Subgraph Integration

**One-line definition:** The Graph indexes blockchain event logs into a queryable GraphQL API so you don't have to scan millions of blocks yourself.

### Real-World Dev Example
```tsx
import { gql, useQuery } from '@apollo/client';

const TRADES = gql`
  query RecentTrades($user: String!) {
    trades(where: { trader: $user }, orderBy: timestamp, orderDirection: desc, first: 10) {
      id
      amountIn
      amountOut
      timestamp
    }
  }
`;

const { data } = useQuery(TRADES, { variables: { user: address } });
```

### ASCII Diagram
```
Smart Contract emits events
         ↓
   Graph Node listens  (subgraph mapping transforms events → entities)
         ↓
   Subgraph store  (Postgres under the hood)
         ↓
   GraphQL API  ←── your frontend queries here
```

### Gotchas & Dev Context
- Subgraphs have indexing lag — typically 1-5 blocks behind the chain tip. Don't rely on them for real-time confirmation status.
- The hosted service is deprecated; migrate to **The Graph Network** (decentralized, pay with GRT).
- Subgraph mappings are written in AssemblyScript — not TypeScript, even though they look similar.
- Use `_meta { block { number } }` in queries to check how far behind the subgraph is.

### Production FAQ
**Q: Can I query The Graph without a subgraph I wrote myself?**
A: Yes — many popular protocols (Uniswap, Aave, Compound) publish their subgraphs on The Graph Explorer. Query them directly.

**Q: What if The Graph is down?**
A: Fall back to direct `eth_getLogs` RPC calls. It's slower but always available as long as your RPC node is up.

---

## 14. Real-Time Events (WebSocket Subscriptions)

**One-line definition:** WebSocket connections let your frontend listen to new blocks and contract events as they happen, instead of polling the node repeatedly.

### Real-World Dev Example
```tsx
// viem WebSocket transport
import { createPublicClient, webSocket } from 'viem';
import { mainnet } from 'viem/chains';

const client = createPublicClient({
  chain: mainnet,
  transport: webSocket('wss://eth-mainnet.g.alchemy.com/v2/YOUR_KEY'),
});

// Watch for Transfer events in real time
const unwatch = client.watchContractEvent({
  address: '0xToken...',
  abi: erc20Abi,
  eventName: 'Transfer',
  onLogs: (logs) => console.log('New transfer:', logs),
});

// Cleanup on component unmount
useEffect(() => () => unwatch(), []);
```

### ASCII Diagram
```
RPC Node ──wss://──▶ persistent connection ──▶ Frontend
                          ↑
               pushes events as they're mined
               (no polling, low latency ~1-2s)
```

### Gotchas & Dev Context
- WebSocket connections drop silently — implement reconnect logic with exponential backoff.
- Free-tier WebSocket limits are strict (Alchemy: 50 concurrent connections). Monitor usage.
- `eth_subscribe` is not supported on HTTP endpoints — you must use a WebSocket or IPC transport.
- Always call the returned `unwatch()` / `unsubscribe()` function on component unmount to prevent memory leaks.

### Production FAQ
**Q: Should I use WebSocket subscriptions or polling for production?**
A: WebSockets for low-latency UX (live price feeds, tx status). Polling (every 12 s) is simpler and sufficient for dashboards that don't need sub-second updates.

**Q: Do WebSocket subscriptions work on L2s?**
A: Yes — most L2 RPC providers (Alchemy, QuickNode) support `wss://` endpoints for Arbitrum, Optimism, Base, etc.

---

*End of Batch 14 — Frontend & dApp Architecture*
