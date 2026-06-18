# Batch 6 — Tokens & Standards
> How fungible and non-fungible assets are created and managed on-chain.

---

## 1. ERC-20 (Fungible Tokens)

**One-line definition:** A standard interface for interchangeable tokens where every unit is identical and equal in value.

### Real-World Dev Example
USDC, LINK, and UNI are all ERC-20 tokens. Any wallet or DEX knows how to handle them without custom integration.

```solidity
// Minimal ERC-20 interface
interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function approve(address spender, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}
```

### ASCII Diagram
```
Alice (100 DAI) ──transfer(Bob, 40)──► Bob (40 DAI)
                                        Alice (60 DAI)
```

### Gotchas & Dev Context
- `transfer` returns a `bool` — some tokens (e.g. USDT) don't and will silently fail; always use `SafeERC20`
- Decimals are **not** enforced by the standard; most use 18, but USDC uses 6
- `approve` + `transferFrom` is the two-step pattern for letting contracts spend your tokens
- No hook on receive — the contract receiving tokens won't know unless it also checks

### Production FAQ
**Q: Why does my token transfer revert on some tokens but not others?**  
A: Non-compliant tokens (like USDT) return no value from `transfer`. Use OpenZeppelin's `SafeERC20.safeTransfer()` to handle both cases.

**Q: Should I set allowance to 0 before re-approving?**  
A: Yes. Some tokens revert if you approve from a non-zero value directly. Always reset to 0 first.

---

## 2. ERC-721 (NFTs)

**One-line definition:** A standard for unique, non-interchangeable tokens — each token has a distinct `tokenId` and owner.

### Real-World Dev Example
CryptoPunks, Bored Apes, and on-chain art are ERC-721 tokens. Token #42 is not the same as token #43.

```solidity
// Mint a new NFT
function mint(address to, uint256 tokenId) external {
    _safeMint(to, tokenId);
}

// Fetch owner
ownerOf(uint256 tokenId) external view returns (address);
```

### ASCII Diagram
```
Collection: "BoredApes"
  tokenId: 1 ──► owner: Alice
  tokenId: 2 ──► owner: Bob
  tokenId: 3 ──► owner: Carol
  (each is unique, cannot be split)
```

### Gotchas & Dev Context
- `_safeMint` checks if recipient is a contract and calls `onERC721Received` — prevents tokens being locked
- `tokenURI(tokenId)` returns metadata location — often an IPFS URL, not on-chain data
- Approvals are per-token or per-operator (`setApprovalForAll`)
- Sequential `tokenId` exposes mint order — use randomized IDs for fair drops

### Production FAQ
**Q: My NFT metadata disappeared after mint. Why?**  
A: You pointed `tokenURI` to a centralized server. Use IPFS or on-chain SVG for permanence.

**Q: What's the difference between `approve` and `setApprovalForAll`?**  
A: `approve` delegates a single token; `setApprovalForAll` lets an operator manage your entire collection — use it cautiously.

---

## 3. ERC-1155 (Multi-Token Standard)

**One-line definition:** A single contract that can manage multiple token types — both fungible and non-fungible — simultaneously.

### Real-World Dev Example
A blockchain game uses one ERC-1155 contract: token ID `1` = Gold (fungible, qty: 10,000), token ID `2` = Legendary Sword (NFT, qty: 1).

```solidity
// Transfer 50 units of token ID 1 to Bob
safeTransferFrom(alice, bob, tokenId: 1, amount: 50, data: "");

// Batch transfer multiple token types at once
safeBatchTransferFrom(alice, bob, [1, 2, 3], [50, 1, 200], "");
```

### ASCII Diagram
```
Contract 0xABC
  ├── ID 1 (GOLD)   → fungible, supply: 10000
  ├── ID 2 (SWORD)  → semi-fungible, supply: 5
  └── ID 3 (TICKET) → fungible, supply: 500
```

### Gotchas & Dev Context
- Batch transfers save significant gas vs multiple ERC-20/721 calls
- Requires `onERC1155Received` / `onERC1155BatchReceived` on receiver contracts
- Less tooling support than ERC-20/721 — some marketplaces don't fully support it
- `uri(id)` can use `{id}` substitution in the URL string

### Production FAQ
**Q: Should I use ERC-1155 instead of ERC-721 for my NFT collection?**  
A: If you have multiple editions or mixed fungible/non-fungible needs, yes. For 1-of-1 art, ERC-721 has broader marketplace support.

**Q: Can I make an ERC-1155 token non-transferable?**  
A: Yes — override `safeTransferFrom` to revert. This is used for soulbound-style items.

---

## 4. ERC-777 (Advanced Fungible)

**One-line definition:** An improved fungible token standard that adds send/receive hooks, eliminating the need for the `approve` + `transferFrom` two-step.

### Real-World Dev Example
Instead of `approve` then `transferFrom`, a contract can react when tokens are sent to it via `tokensReceived`.

```solidity
// Receiver hook — triggered automatically when tokens arrive
function tokensReceived(
    address operator, address from, address to,
    uint256 amount, bytes calldata userData, bytes calldata operatorData
) external override { /* handle incoming tokens */ }
```

### Gotchas & Dev Context
- **Reentrancy risk**: hooks execute during transfer — always use `ReentrancyGuard`
- Backward-compatible with ERC-20 interfaces
- Uses the ERC-1820 registry to look up hook implementations
- Largely **abandoned in practice** due to reentrancy exploits (imBTC + Uniswap hack, 2020)
- OpenZeppelin deprecated ERC-777 in v5 — treat as legacy

### Production FAQ
**Q: Should I build with ERC-777 today?**  
A: No. The reentrancy vector is well-documented. Use ERC-20 with explicit callbacks (e.g., ERC-4626 patterns) instead.

**Q: Why do some protocols still have ERC-777 in their audits?**  
A: Older protocols deployed pre-2021 often included it. Modern audits flag ERC-777 interactions as a risk.

---

## 5. Token Approval / Allowance

**One-line definition:** Permission you grant to a contract (or address) to spend up to a set amount of your tokens on your behalf.

### Real-World Dev Example
When you swap on Uniswap, you first approve the router to pull your USDC, then call `swap`. Without approval, the router can't touch your funds.

```solidity
// Step 1: User approves DEX router for 100 USDC
IERC20(usdc).approve(routerAddress, 100e6);

// Step 2: Router pulls tokens during swap
IERC20(usdc).transferFrom(user, pool, 100e6);
```

### ASCII Diagram
```
User ──approve(Router, 100)──► Allowance mapping updated
User ──calls swap()──────────► Router calls transferFrom(User, Pool, 100) ✓
```

### Gotchas & Dev Context
- **Infinite approval** (`type(uint256).max`) is common but dangerous — if the contract is exploited, all approved tokens are at risk
- `allowance(owner, spender)` lets you check current approval
- ERC-20 Permit (EIP-2612) allows gasless approval via signature
- Revoke unused approvals with tools like revoke.cash

### Production FAQ
**Q: A contract drained my wallet after I approved it. How?**  
A: You gave infinite approval. The contract (or attacker) called `transferFrom` up to your full balance. Always approve exact amounts.

**Q: What is Permit / EIP-2612?**  
A: An extension that lets users sign an off-chain message to authorize spending — no on-chain approval tx needed, saving gas.

---

## 6. SafeTransfer vs Transfer

**One-line definition:** `safeTransfer` wraps `transfer` with checks for non-standard token behavior; `transfer` is the raw ERC-20 call that can silently fail.

### Real-World Dev Example
```solidity
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

using SafeERC20 for IERC20;

// ❌ Risky — USDT returns no bool, this may silently fail
token.transfer(to, amount);

// ✅ Safe — reverts if transfer fails or returns false
token.safeTransfer(to, amount);
```

### Gotchas & Dev Context
- USDT (Tether), BNB, and several other major tokens are non-compliant ERC-20s
- `SafeERC20` uses low-level `call` and checks return data length
- For ERC-721: `safeTransferFrom` triggers `onERC721Received` on contracts; `transferFrom` skips it — tokens can get locked
- Always use `safeTransfer` / `safeTransferFrom` in production code

### Production FAQ
**Q: My unit tests pass but mainnet transfer silently fails. Why?**  
A: Your test token is compliant; the mainnet token (e.g., USDT) isn't. Test with a USDT fork or use `SafeERC20` everywhere.

**Q: When would I prefer `transferFrom` over `safeTransferFrom` for NFTs?**  
A: Almost never in production. The only exception is gas optimization in contracts you fully control on both ends.

---

## 7. Minting & Burning

**One-line definition:** Minting creates new tokens and adds them to supply; burning destroys tokens and removes them from supply.

### Real-World Dev Example
```solidity
// Mint: create 100 tokens to Alice
function mint(address to, uint256 amount) external onlyOwner {
    _mint(to, amount);  // increases totalSupply
}

// Burn: destroy 50 tokens from Alice's balance
function burn(uint256 amount) external {
    _burn(msg.sender, amount);  // decreases totalSupply
}
```

### ASCII Diagram
```
MINT:  Supply: 1000 ──_mint(Alice, 100)──► Supply: 1100, Alice +100
BURN:  Supply: 1100 ──_burn(Alice, 50)───► Supply: 1050, Alice -50
```

### Gotchas & Dev Context
- `_mint` and `_burn` are internal — expose them carefully with access control
- Burning to `address(0)` is a common pattern but differs from `_burn` — `_burn` properly updates `totalSupply`
- Deflationary tokens auto-burn a % on each transfer — watch for fee-on-transfer logic in integrations
- NFT burns should also clear approvals and metadata

### Production FAQ
**Q: Should I mint all tokens at deploy or on-demand?**  
A: Depends on the model. Fixed supply = mint all at deploy. Dynamic supply = on-demand with access control. Hybrid = cap + on-demand.

**Q: Can burned tokens be recovered?**  
A: No. Burning is irreversible. Always double-check burn logic in audits.

---

## 8. Token URI / Metadata (On-chain vs Off-chain)

**One-line definition:** `tokenURI` is a function that returns a URL (or data string) pointing to an NFT's metadata like name, image, and attributes.

### Real-World Dev Example
```solidity
// Off-chain IPFS metadata
function tokenURI(uint256 id) public view returns (string memory) {
    return string(abi.encodePacked("ipfs://QmXyz/", id.toString(), ".json"));
}

// On-chain SVG metadata (base64-encoded)
function tokenURI(uint256 id) public view returns (string memory) {
    string memory svg = "<svg>...</svg>";
    return string(abi.encodePacked(
        "data:application/json;base64,", Base64.encode(bytes(json))
    ));
}
```

### ASCII Diagram
```
tokenURI(42) ──► "ipfs://QmXyz/42.json"
                        │
                        ▼
              { name: "Ape #42",
                image: "ipfs://...",
                attributes: [...] }
```

### Gotchas & Dev Context
- Off-chain metadata can be changed or deleted by the host — **not truly permanent**
- IPFS is content-addressed (hash-based) but still requires a pinning service
- On-chain metadata is permanent but expensive in gas
- OpenSea uses `name`, `description`, `image`, and `attributes` fields in metadata JSON

### Production FAQ
**Q: My NFT image broke after launch. What happened?**  
A: Your metadata was on a centralized server that went down. Migrate to IPFS or encode on-chain.

**Q: What's the difference between IPFS and Arweave for metadata?**  
A: IPFS requires active pinning to keep data available; Arweave is pay-once, store-forever — preferred for permanent NFT assets.

---

## 9. Soulbound Tokens (SBTs / ERC-5192)

**One-line definition:** Non-transferable tokens permanently bound to a wallet, representing identity, credentials, or reputation.

### Real-World Dev Example
A university issues a degree as an SBT. The token proves you graduated — it can't be sold or transferred to anyone else.

```solidity
// ERC-5192 — lock token on mint
function locked(uint256 tokenId) external view returns (bool) {
    return true; // always locked
}

// Override transfer to revert
function transferFrom(address, address, uint256) public override {
    revert("SBT: non-transferable");
}
```

### Gotchas & Dev Context
- ERC-5192 extends ERC-721 with a `locked(tokenId)` view function
- Wallets can be lost — consider a recovery mechanism (social recovery or revoke + reissue)
- SBTs raise privacy concerns — permanent on-chain credentials are public
- Not yet widely standardized; some teams use custom non-transferable ERC-721s

### Production FAQ
**Q: How do you revoke an SBT?**  
A: The issuer can burn it and reissue a corrected one — build burn access control for the issuing address.

**Q: Can SBTs work with pseudonymous wallets?**  
A: Yes, but it weakens the identity guarantee. Real-world SBT use-cases usually pair with a KYC step off-chain.

---

## 10. Wrapped Tokens (WETH, WBTC)

**One-line definition:** A wrapped token is an ERC-20 representation of a native asset (like ETH or BTC) that enables it to work with DeFi protocols expecting the ERC-20 interface.

### Real-World Dev Example
ETH is not ERC-20 compliant. To use ETH in Uniswap pools or Aave, you wrap it into WETH (1:1 peg).

```solidity
// Wrap ETH → WETH (deposit ETH, get WETH)
IWETH(wethAddress).deposit{value: 1 ether}();

// Unwrap WETH → ETH (burn WETH, get ETH back)
IWETH(wethAddress).withdraw(1 ether);
```

### ASCII Diagram
```
User sends 1 ETH ──► WETH Contract ──► Mints 1 WETH to User
User sends 1 WETH ──► WETH Contract ──► Burns WETH, returns 1 ETH
```

### Gotchas & Dev Context
- WBTC is custodied — a centralized entity (BitGo) holds the real BTC; trust is required
- WETH is trustless — the contract holds the ETH, fully auditable
- Always unwrap before sending to EOAs that expect native ETH
- Many protocols auto-wrap/unwrap internally (e.g., Uniswap V3 router)

### Production FAQ
**Q: Why can't DeFi just use native ETH?**  
A: Native ETH requires special handling (`payable`, `msg.value`). ERC-20 standardizes the interface, making protocol integration much simpler.

**Q: Is WBTC decentralized?**  
A: No. It's an ERC-20 token backed by BTC held by a centralized custodian. Decentralized BTC bridges (like tBTC) aim to solve this.

---

## 11. Stablecoins (USDC, DAI, USDT)

**One-line definition:** Tokens designed to maintain a stable value (usually $1 USD) via collateral or algorithmic mechanisms.

### Real-World Dev Example
Paying a contractor in ETH is risky due to price swings. Paying in USDC ensures they receive $500, not "$500 worth of ETH that's now $310."

### ASCII Diagram
```
Type            | Collateral          | Example  | Trust Level
----------------|---------------------|----------|-------------
Fiat-backed     | USD in bank         | USDC     | Centralized
Crypto-backed   | ETH/BTC over-coll.  | DAI      | Decentralized
Algorithmic     | None (seigniorage)  | UST ❌   | Trustless (risky)
```

### Gotchas & Dev Context
- USDC/USDT can **freeze or blacklist** addresses — they're centralized and regulatable
- DAI is overcollateralized (you lock $150 of ETH to mint $100 DAI) — liquidation risk exists
- Stablecoins often have 6 decimals (USDC, USDT), not 18 — hardcoding `1e18` for "$1" will break things
- Peg can temporarily deviate in market stress — don't assume perfect $1 in price-sensitive logic

### Production FAQ
**Q: Can my protocol freeze if USDC depegs?**  
A: Yes. If you hardcode price = $1, a depeg breaks liquidations. Always use a price oracle (Chainlink) even for stablecoins.

**Q: What makes DAI safer than algorithmic stablecoins?**  
A: DAI holds real collateral (ETH, USDC). Algorithmic stablecoins rely on incentives alone — when confidence breaks, they spiral to zero.

---

## 12. Algorithmic Stablecoins

**One-line definition:** A stablecoin that maintains its peg through algorithm-controlled token supply mechanics rather than holding real-world collateral.

### Real-World Dev Example
TerraUSD (UST) maintained its $1 peg by letting users burn $1 of LUNA to mint 1 UST, and vice versa. When confidence collapsed in May 2022, it hyperinflated LUNA to worthlessness.

### ASCII Diagram
```
UST > $1 ──► Mint UST (burn LUNA) ──► UST supply ↑ ──► Price ↓
UST < $1 ──► Burn UST (mint LUNA) ──► UST supply ↓ ──► Price ↑
             (requires confidence in LUNA value)
```

### Gotchas & Dev Context
- **Death spiral risk**: if the backing token loses value, the mechanism amplifies the collapse
- Frax (FRAX) uses a hybrid model — partially collateralized + algorithmic — considered more robust
- Protocol revenues or reserve funds can act as a buffer but don't guarantee stability
- Regulatory scrutiny is increasing; treat as high-risk

### Production FAQ
**Q: Are all algorithmic stablecoins doomed to fail?**  
A: Not necessarily, but purely endogenous (no external collateral) models have a poor track record. Hybrid approaches (Frax-style) show more resilience.

**Q: How do I identify an algorithmic stablecoin risk in a DeFi protocol?**  
A: Check if the stablecoin's collateral is the protocol's own governance token. If yes — red flag.

---

## 13. Governance Tokens

**One-line definition:** Tokens that grant holders voting rights over a protocol's decisions — parameters, upgrades, treasury spending.

### Real-World Dev Example
UNI (Uniswap) and COMP (Compound) holders vote on protocol proposals. Hold more tokens → more voting power.

```solidity
// Simple on-chain vote tally
mapping(address => uint256) public votes;

function vote(uint256 proposalId) external {
    uint256 weight = governanceToken.balanceOf(msg.sender);
    votes[proposalId] += weight;
}
```

### Gotchas & Dev Context
- Voting power ≠ economic value — governance can be separate from fee revenue
- **Voter apathy** is real — most governance tokens sit idle; a small group can pass proposals
- Flash loan attacks can temporarily inflate voting power — use snapshot-based voting (ERC-20Votes / checkpoints)
- Governance delay (timelock) is critical — prevents malicious instant execution of proposals

### Production FAQ
**Q: Can someone buy governance control of a protocol?**  
A: Yes — a "governance attack." Mitigate with timelocks, quorum requirements, and delegation systems.

**Q: What is vote delegation?**  
A: Token holders can delegate their votes to an active participant without transferring tokens. Reduces apathy while preserving decentralization (used in Compound, Uniswap).

---

## 14. Utility Tokens vs Security Tokens

**One-line definition:** Utility tokens grant access to a product/service; security tokens represent ownership or investment in an asset and are subject to securities law.

### Real-World Dev Example
- **Utility**: Filecoin's FIL buys storage. Chainlink's LINK pays for oracle services.  
- **Security**: A tokenized share of a real estate fund that pays dividends — this is a security token, regulated like a stock.

### ASCII Diagram
```
Utility Token                 Security Token
──────────────────────────    ──────────────────────────
Grants access/service         Represents ownership/profit
Unregulated (mostly)          SEC/FCA regulated
No expectation of profit      Expectation of profit
Example: API3, FIL, LINK      Example: tZERO, Polymath
```

### Gotchas & Dev Context
- The **Howey Test** (US) determines if a token is a security: investment of money + common enterprise + expectation of profit from others' efforts = security
- Many "utility" tokens are borderline — regulatory risk is real
- Security tokens require KYC/AML, whitelisting, and compliance infrastructure
- Launching a governance token with profit-sharing mechanics = likely a security

### Production FAQ
**Q: How do I know if my token is a security?**  
A: Consult a crypto-specialized lawyer and apply the Howey Test. If your marketing promises returns or profits, it's high risk.

**Q: What happens if a utility token is reclassified as a security?**  
A: Regulatory action, fines, or shutdown. See the SEC vs. Ripple (XRP) case as a cautionary example.

---

## 15. Token Vesting & Cliff

**One-line definition:** Vesting releases tokens gradually over time; a cliff is the minimum waiting period before any tokens are released at all.

### Real-World Dev Example
A dev gets 1,000,000 tokens: 1-year cliff, 4-year total vesting. After 12 months they receive 25% (250,000). Then ~17,361 tokens unlock monthly for 3 more years.

```solidity
// Simplified vesting check
function releasable() public view returns (uint256) {
    if (block.timestamp < start + cliff) return 0; // cliff not reached
    uint256 elapsed = block.timestamp - start;
    uint256 vested = (totalAmount * elapsed) / duration;
    return vested - released; // subtract already claimed
}
```

### ASCII Diagram
```
Timeline:
Month 0 ──────── Month 12 ─────── Month 48
   │    (cliff)      │  (linear)      │
   0 tokens      25% unlocks    100% unlocked
                 then ~2% / month
```

### Gotchas & Dev Context
- Always lock team/investor tokens — unvested team tokens are a major red flag in audits and community trust
- Vesting contracts should be non-upgradeable and audited separately
- Use block timestamp, not block number — block times vary across chains
- Cliff + linear vesting is the industry standard for team allocations; investors often get shorter cliffs

### Production FAQ
**Q: What if a team member leaves before the cliff?**  
A: Standard vesting contracts include a `revoke` function allowing the company to reclaim unvested tokens.

**Q: Should vesting be on-chain or handled off-chain?**  
A: On-chain vesting is trustless and transparent — strongly preferred for team/investor allocations in DeFi projects. Off-chain is only acceptable in fully centralized setups.
