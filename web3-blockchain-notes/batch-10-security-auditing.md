# Batch 10 — Security & Auditing
> The most critical batch — how contracts get exploited and how to prevent it.

Security is the hardest part of smart contract development. Unlike traditional software, deployed contracts are immutable, hold real money, and are readable by every attacker on the planet. This batch covers the most common exploits, defensive patterns, and auditing tools used in production.

---

## 1. Reentrancy Attack

**One-line definition:** A malicious contract calls back into the victim contract before the first execution finishes, draining funds.

### Real-World Dev Example
The DAO hack (2016) — $60M drained. A vulnerable `withdraw()` sent ETH *before* updating the balance, letting attacker's fallback loop back in.

```
Attacker Contract          Victim Contract
─────────────────          ───────────────
withdraw()        ──────►  send ETH  (balance not updated yet)
  fallback()      ◄──────  receive ETH
  withdraw()      ──────►  send ETH again! (balance still old)
  fallback()      ◄──────  ...repeats until drained
```

**Vulnerable:**
```solidity
function withdraw() external {
    uint bal = balances[msg.sender];
    (bool ok,) = msg.sender.call{value: bal}(""); // ← ETH sent first
    balances[msg.sender] = 0;                      // ← update AFTER (too late)
}
```

**Fixed (Checks-Effects-Interactions pattern):**
```solidity
function withdraw() external {
    uint bal = balances[msg.sender];
    balances[msg.sender] = 0;                      // ← update first
    (bool ok,) = msg.sender.call{value: bal}("");  // ← then send
}
```
Or use OpenZeppelin's `ReentrancyGuard` (`nonReentrant` modifier).

### Gotchas & Dev Context
- Cross-function reentrancy is subtler: attacker enters via a *different* function
- Read-only reentrancy (via view functions) can still corrupt state in some DeFi protocols
- ERC-777 tokens have hooks that enable reentrancy even with CEI pattern

### Production FAQ
**Q: Does `nonReentrant` from OZ cover cross-contract reentrancy?**
A: Yes — it uses a shared lock on the contract, blocking any reentrant call regardless of which external function triggers it.

**Q: Is CEI always sufficient?**
A: Not if you have multiple state variables that must stay in sync. Prefer `ReentrancyGuard` in complex DeFi contracts.

---

## 2. Front-Running / Sandwich Attack

**One-line definition:** A bot sees your pending transaction in the mempool and inserts its own transaction before (and sometimes after) yours to profit at your expense.

### Real-World Dev Example
DEX trades: You submit a swap of ETH→USDC. A MEV bot:
1. **Front-runs** you — buys USDC (price goes up)
2. Your trade executes at the worse price
3. Bot **back-runs** you — sells USDC for profit

```
Mempool (public)
─────────────────────────────────────────
[Bot BUY tx, gas+1] → [Your SWAP tx] → [Bot SELL tx]
     ↑ inserted before                      ↑ inserted after
         ──────────── You're the sandwich filling ────────────
```

### Gotchas & Dev Context
- Any on-chain action with predictable value is front-runnable: NFT mints, liquidations, oracle updates
- Slippage tolerance in AMMs is your only direct defense for swaps
- Commit-reveal schemes hide intent: commit a hash first, reveal later
- Flashbots / private mempools (MEV Blocker, Flashbots Protect) route transactions off the public mempool

### Production FAQ
**Q: Can I prevent front-running in my contract?**
A: Fully? No. Mitigations: tight slippage limits, commit-reveal, batch auctions (Cowswap model), or private RPC endpoints.

**Q: What's the difference between front-running and sandwich attacks?**
A: Front-running is only one insertion before your tx. A sandwich wraps you with both a buy-before and sell-after for maximum extraction.

---

## 3. Flash Loan Attack

**One-line definition:** Borrowing a massive amount of uncollateralized funds within a single transaction to manipulate prices or exploit vulnerable contracts, then repaying before the tx ends.

### Real-World Dev Example
Beanstalk hack (2022) — $182M. Attacker flash-loaned enough governance tokens to pass a malicious proposal in a single tx and drain the treasury.

```
Block N — single transaction:
┌─────────────────────────────────────────────────────┐
│ 1. Borrow $100M USDC (flash loan, Aave)             │
│ 2. Manipulate oracle / buy governance power         │
│ 3. Exploit target protocol                          │
│ 4. Repay $100M + fee                                │
│ 5. Keep profit                                      │
└─────────────────────────────────────────────────────┘
  If step 4 fails → entire tx reverts (no risk to attacker)
```

### Gotchas & Dev Context
- Flash loans themselves are legitimate (arbitrage, collateral swaps); the exploit is in vulnerable protocols
- Spot price oracles (single DEX) are trivially manipulated; use Chainlink or TWAP
- Single-block governance votes are dangerous — require a time delay between proposal and execution
- Reentrancy guards don't help here since it's not reentrancy — it's economic manipulation

### Production FAQ
**Q: How do I protect my protocol from flash loan price manipulation?**
A: Use TWAP (time-weighted average price) oracles or Chainlink feeds instead of DEX spot price.

**Q: Can you block flash loans directly?**
A: You can check `tx.origin == msg.sender` but this breaks composability and is bypassable. Better to fix the underlying oracle/governance vulnerability.

---

## 4. Integer Overflow / Underflow (pre-Solidity 0.8)

**One-line definition:** Arithmetic that wraps around silently — a number past its max flips to 0, or below 0 flips to the max value.

### Real-World Dev Example
BEC token hack (2018) — $900M paper loss. A `batchTransfer` multiplied `uint256` values that overflowed to near-zero, minting billions of tokens.

**Vulnerable (Solidity < 0.8):**
```solidity
uint8 x = 255;
x += 1; // x == 0  ← silent overflow, no error!

uint8 y = 0;
y -= 1; // y == 255 ← silent underflow!
```

**Fixed (Solidity ≥ 0.8):**
```solidity
// Arithmetic reverts automatically on overflow/underflow
uint8 x = 255;
x += 1; // ← reverts with panic error
```

**Fixed (Solidity < 0.8 with SafeMath):**
```solidity
using SafeMath for uint256;
uint256 result = a.add(b); // reverts on overflow
```

### Gotchas & Dev Context
- Solidity 0.8+ makes SafeMath redundant for standard arithmetic
- `unchecked { }` blocks in 0.8+ skip overflow checks — use only when you've manually verified safety (e.g., loop counters)
- Casting between types (`uint256` → `uint8`) can still silently truncate in all versions

### Production FAQ
**Q: Should I still import SafeMath in new 0.8+ contracts?**
A: No — it wastes gas and adds no safety. Built-in checks are better.

**Q: When is `unchecked` acceptable?**
A: Loop counters where you've proven the value can't overflow (e.g., `i < array.length`), to save gas.

---

## 5. Access Control Vulnerabilities

**One-line definition:** Critical functions lack proper permission checks, letting any address call them.

### Real-World Dev Example
Parity Wallet hack (2017) — $30M. The `initWallet()` function on the library contract had no `onlyOwner` guard, letting an attacker become owner and self-destruct the library.

**Vulnerable:**
```solidity
function setOwner(address newOwner) public {
    owner = newOwner; // ← anyone can call this!
}
```

**Fixed:**
```solidity
function setOwner(address newOwner) external onlyOwner {
    owner = newOwner;
}

modifier onlyOwner() {
    require(msg.sender == owner, "Not owner");
    _;
}
```

Use OpenZeppelin `Ownable` or `AccessControl` for role-based permissions.

```
Roles (OZ AccessControl):
ADMIN_ROLE  → can grant/revoke roles
MINTER_ROLE → can mint tokens
PAUSER_ROLE → can pause contract
```

### Gotchas & Dev Context
- Initializer functions on upgradeable proxies must call `_disableInitializers()` in the constructor to prevent re-initialization
- `DEFAULT_ADMIN_ROLE` in OZ `AccessControl` can grant itself anything — protect it carefully
- Role renouncement should be a two-step process to avoid accidental lockout
- Off-chain signature-based auth (`permit`) can bypass `msg.sender` checks — verify signer carefully

### Production FAQ
**Q: `Ownable` vs `AccessControl` — when to use which?**
A: `Ownable` for simple single-admin contracts. `AccessControl` for multiple distinct roles (minter, pauser, upgrader).

**Q: How do I avoid locking myself out of ownership?**
A: Use `Ownable2Step` (OZ) — requires new owner to explicitly accept, preventing accidental transfer to wrong address.

---

## 6. tx.origin vs msg.sender

**One-line definition:** `tx.origin` is always the original EOA that started the transaction chain; `msg.sender` is the immediate caller (could be a contract).

### Real-World Dev Example
A phishing contract tricks you into calling it. If your contract uses `tx.origin` for auth, the phishing contract passes the check because *you* started the tx.

```
You (EOA) → PhishingContract.attack() → YourContract.withdraw()
                                              ↑
tx.origin == You (EOA)  ← passes tx.origin check!
msg.sender == PhishingContract ← would fail msg.sender check ✓
```

**Vulnerable:**
```solidity
function withdraw() external {
    require(tx.origin == owner, "Not owner"); // ← phishable!
    payable(tx.origin).transfer(address(this).balance);
}
```

**Fixed:**
```solidity
function withdraw() external {
    require(msg.sender == owner, "Not owner"); // ← safe
    payable(msg.sender).transfer(address(this).balance);
}
```

### Gotchas & Dev Context
- Account Abstraction (ERC-4337) can make `tx.origin` even less reliable — smart wallets may set it differently
- The *only* valid use of `tx.origin` is to check "was this initiated by an EOA, not a contract?" — but even this is fragile
- Never use `tx.origin` for authentication or authorization

### Production FAQ
**Q: Is there any legitimate use of `tx.origin`?**
A: Extremely rare. It's sometimes used to block contract-to-contract calls (anti-bot), but `msg.sender == tx.origin` is more explicit and less risky.

**Q: Does this affect ERC-2771 (meta-transactions)?**
A: Yes — meta-transaction relayers break `msg.sender` assumptions. Use `_msgSender()` from OZ's `Context` which handles trusted forwarders.

---

## 7. Denial of Service (DoS) in Contracts

**One-line definition:** An attacker makes a contract permanently or temporarily unusable — without stealing funds.

### Real-World Dev Example
GovernorBravo-style contracts where a for-loop iterates over unbounded arrays of voters — an attacker adds thousands of entries, making the function hit the block gas limit and revert forever.

**Vulnerable patterns:**

```solidity
// DoS via unbounded loop
function payAll() external {
    for (uint i = 0; i < recipients.length; i++) { // attacker bloats array
        payable(recipients[i]).transfer(shares[i]);
    }
}

// DoS via revert in loop (one bad recipient blocks everyone)
// If recipients[i] is a contract that reverts on receive → whole tx fails
```

**Fixed — pull-payment pattern:**
```solidity
mapping(address => uint) public pendingWithdrawals;

function withdraw() external {
    uint amount = pendingWithdrawals[msg.sender];
    pendingWithdrawals[msg.sender] = 0;
    payable(msg.sender).transfer(amount);
}
```

### Gotchas & Dev Context
- Sending ETH to a contract that has no `receive()`/`fallback()` reverts — chain this with a loop = DoS
- Self-destruct can force-send ETH to any contract, breaking `address(this).balance == 0` assumptions
- Gas limits are your friend in detecting DoS: if a function can exceed 30M gas, it's attackable

### Production FAQ
**Q: How do I protect against unbounded loop DoS?**
A: Paginate iteration with start/end indices, or switch to pull-payment (recipients claim individually).

**Q: Can DoS drain funds?**
A: Rarely directly, but it can prevent liquidations, block withdrawals during a crisis, or freeze governance — all economically damaging.

---

## 8. Storage Collision (Proxy Pattern)

**One-line definition:** In upgradeable proxy patterns, storage slots of the proxy and logic contract overlap, causing one to overwrite the other's variables.

### Real-World Dev Example
Early EIP-1967 violators: a proxy stored `implementation` at slot 0; the logic contract also stored `owner` at slot 0 — upgrading overwrote the owner address.

```
Proxy Storage Layout:    Logic Contract Layout:
Slot 0: _implementation  Slot 0: owner          ← COLLISION!
Slot 1: _admin           Slot 1: totalSupply
```

**Fixed — EIP-1967 Unstructured Storage:**
```solidity
// Implementation address stored at a pseudo-random slot
bytes32 private constant _IMPL_SLOT =
    bytes32(uint256(keccak256("eip1967.proxy.implementation")) - 1);
```

**Fixed — use OpenZeppelin's `TransparentUpgradeableProxy` or `UUPSUpgradeable`** which handle slot management for you.

### Gotchas & Dev Context
- Never use regular storage variables in proxy contracts — only EIP-1967 or diamond storage (EIP-2535)
- Changing variable *order* in a logic contract upgrade causes collisions with existing stored data
- Adding new variables must always be appended at the end of storage layout
- Use `@openzeppelin/hardhat-upgrades` plugin to detect storage layout conflicts automatically

### Production FAQ
**Q: What's the difference between Transparent and UUPS proxies?**
A: Transparent: upgrade logic in proxy (admin vs user split). UUPS: upgrade logic in implementation (leaner, but must remember to include upgrade function).

**Q: Can I reorder struct fields between upgrades?**
A: Absolutely not — each field maps to a fixed storage slot. Reordering corrupts all stored data.

---

## 9. Signature Replay Attack

**One-line definition:** A valid signed message is re-submitted by an attacker to execute the same authorized action multiple times.

### Real-World Dev Example
A gasless transfer approval: user signs "transfer 100 USDC to Alice." Without a nonce, attacker rebroadcasts the signature repeatedly, draining the account.

```
User signs: {to: Alice, amount: 100, nonce: 0}  ← valid
Attacker replays same sig                        ← should fail!
```

**Vulnerable:**
```solidity
function execute(address to, uint amount, bytes memory sig) external {
    bytes32 hash = keccak256(abi.encodePacked(to, amount));
    require(recoverSigner(hash, sig) == owner, "bad sig");
    // No nonce → replay possible!
    token.transfer(to, amount);
}
```

**Fixed:**
```solidity
mapping(address => uint) public nonces;

function execute(address to, uint amount, bytes memory sig) external {
    uint nonce = nonces[owner]++;
    bytes32 hash = keccak256(abi.encodePacked(to, amount, nonce, block.chainid));
    require(recoverSigner(hash, sig) == owner, "bad sig");
    token.transfer(to, amount);
}
```

**Also include `block.chainid` to prevent cross-chain replay (e.g., same sig works on mainnet and testnet).**

### Gotchas & Dev Context
- EIP-712 structured typing + EIP-191 prefix protects against cross-domain and cross-chain replay
- `permit()` (EIP-2612) uses deadline + nonce to expire signatures safely
- Always hash with `chainId` — a valid mainnet signature works on a fork if you forget this

### Production FAQ
**Q: Does EIP-712 solve replay attacks?**
A: Yes, when implemented correctly with nonce + chainId + domain separator. Never skip any of those fields.

**Q: What's a domain separator?**
A: A hash of (contract name, version, chainId, contract address) that scopes signatures to exactly one contract on one chain.

---

## 10. Phishing / Approval Exploits

**One-line definition:** Tricking users into signing transactions that grant unlimited token approvals to a malicious contract, which then drains their wallet.

### Real-World Dev Example
Unlimited `approve()` phishing: a fake NFT mint site prompts you to `approve(attackerContract, type(uint256).max)`. The attacker's contract immediately calls `transferFrom` to sweep all tokens.

```
User visits fake site
        │
        ▼
MetaMask popup: "Approve USDC spending"
(user thinks it's $10 mint fee — it's actually unlimited)
        │
        ▼
approve(0xAttacker, 115792...max)  ← signed & sent
        │
        ▼
Attacker calls transferFrom(user, attacker, userBalance)
        │
        ▼
🏴‍☠️ Drained
```

### Gotchas & Dev Context
- `permit()` (EIP-2612) approval phishing: signing an off-chain message still grants approval — users don't realize signing = approval
- Revoke approvals with tools like revoke.cash or Etherscan token approval checker
- ERC-20 `approve` race condition: changing approval from 100→50 can allow spending 150 total if attacker is fast
- Use `increaseAllowance` / `decreaseAllowance` (OZ) instead of raw `approve` to avoid race condition
- Wallet UI improvements (Metamask snaps, permit2 by Uniswap) help communicate intent more clearly

### Production FAQ
**Q: How do I protect my users from approval phishing in my dApp?**
A: Request exact amounts needed, not `uint256.max`. Use Uniswap's Permit2 for scoped, time-limited approvals.

**Q: Is `setApprovalForAll` (ERC-721/1155) more dangerous than ERC-20 approve?**
A: Yes — it grants control over *all* NFTs in the collection. One phishing signature = entire collection drained.

---

## 11. Audit Process (Manual Review, Formal Verification)

**One-line definition:** Systematic examination of smart contract code by security experts to find vulnerabilities before deployment.

### Real-World Dev Example
Trail of Bits, OpenZeppelin, ConsenSys Diligence, Spearbit — top firms charge $20K–$200K+ per audit. Compound, Uniswap, and Aave publish their audit reports publicly.

```
Audit Pipeline:
─────────────────────────────────────────────────────
  Code Freeze
      │
      ▼
  Automated Tools (Slither, Mythril, Aderyn)
      │
      ▼
  Manual Review (business logic, economic attacks)
      │
      ▼
  Formal Verification (Certora, Halmos) — optional
      │
      ▼
  Report → Dev Fixes → Re-audit
      │
      ▼
  Public Report + Deployment
```

**Levels of assurance:**
| Method | Speed | Depth | Cost |
|---|---|---|---|
| Automated (Slither) | Fast | Shallow | Free |
| Manual review | Slow | Deep | $$$$ |
| Formal verification | Slowest | Provably correct | $$$$$|

### Gotchas & Dev Context
- Audits find bugs — they do NOT make contracts "hack-proof"
- Business logic bugs (economic exploits) are often missed by automated tools
- One audit is rarely enough for high-TVL protocols — multiple firms = better coverage
- Audit scope matters: unaudited code added after an audit invalidates previous findings

### Production FAQ
**Q: When should I get an audit?**
A: Before mainnet deployment, after code freeze. Budget 4–8 weeks of lead time with top firms.

**Q: What does formal verification actually prove?**
A: That a specific mathematical property (invariant) holds for *all* possible inputs — e.g., "total supply always equals sum of balances."

---

## 12. Bug Bounty Programs (Immunefi)

**One-line definition:** Rewards paid to ethical hackers (white-hats) who responsibly disclose vulnerabilities before they're exploited.

### Real-World Dev Example
Immunefi is the largest Web3 bug bounty platform. Severity tiers determine payouts:
- **Critical** (fund loss): up to $10M+
- **High** (temporary fund lock): $10K–$100K
- **Medium/Low** (minor issues): $1K–$10K

Real payout: A researcher found a critical bug in Wormhole's bridge and received $10M — the largest bounty in history.

```
White-hat finds bug
        │
        ▼
Submit via Immunefi (private, encrypted)
        │
        ▼
Protocol triages (24–72 hrs)
        │
        ▼
Valid? → Fix + Patch + Pay bounty
Invalid? → Rejected with explanation
        │
        ▼
Disclosure (after fix, optional)
```

### Gotchas & Dev Context
- No bug bounty = white-hats have no incentive to disclose responsibly
- Bounty must be commensurate with TVL — $50K bounty on a $500M protocol is not credible
- Out-of-scope issues (front-end bugs, centralization risks) often rejected
- Bug bounties do NOT replace audits — they're a second line of defense
- Immunefi deducts 10% fee; self-hosted programs save cost but lose discoverability

### Production FAQ
**Q: When should I launch a bug bounty?**
A: After your audit is complete and the code is deployed — not before, as it's not final.

**Q: What if someone exploits rather than discloses?**
A: That's a blackhat. Many protocols offer "after-the-fact" bounties (e.g., 10% of funds returned) to incentivize return of stolen assets.

---

## 13. Circuit Breaker / Pause Pattern

**One-line definition:** An emergency switch that halts sensitive contract functions when an anomaly is detected, buying time to fix or upgrade.

### Real-World Dev Example
Aave, Compound, and Uniswap v3 all have pause guardians. During the Euler Finance hack (2023, $197M), the team paused remaining pools to prevent further loss.

**Implementation (OpenZeppelin `Pausable`):**
```solidity
import "@openzeppelin/contracts/security/Pausable.sol";

contract MyVault is Pausable {
    address public guardian;

    function deposit(uint amount) external whenNotPaused {
        // normal logic
    }

    function pause() external {
        require(msg.sender == guardian, "Not guardian");
        _pause();
    }

    function unpause() external onlyOwner {
        _unpause();
    }
}
```

```
Normal Operation:  deposit/withdraw ✓
During Incident:   guardian.pause() → all whenNotPaused fns blocked
Post-Fix:          owner.unpause()  → resumes
```

### Gotchas & Dev Context
- Pause should be callable by a fast multisig (3-of-5), not a slow DAO vote — emergencies are time-critical
- Unpause should require a higher threshold or a timelock to prevent abuse
- Document clearly: what's paused vs what keeps running (e.g., read functions usually exempt)
- Centralization risk: a compromised guardian key can maliciously pause the protocol

### Production FAQ
**Q: Should the same key that can pause also be able to unpause?**
A: No best practice here, but separating pause (guardian, fast) and unpause (DAO/timelock, slow) is safer.

**Q: What if I don't want a centralized pause guardian?**
A: Use on-chain monitoring bots (OpenZeppelin Defender Sentinels) that can auto-pause via multisig when anomalies are detected.

---

## 14. Timelock

**One-line definition:** A mandatory delay between when a privileged action is proposed and when it can be executed, giving users time to react.

### Real-World Dev Example
Compound's Governor uses a 48-hour timelock. After a governance vote passes, there's a 2-day window before execution — users who disagree can exit the protocol.

```
Day 0: Proposal created & queued
   │
   │  ← 48-hour delay (timelock)
   │     Users can observe, react, exit
   ▼
Day 2: Transaction can be executed
```

**OpenZeppelin `TimelockController`:**
```solidity
// Deploy with 2-day delay
TimelockController timelock = new TimelockController(
    2 days,          // minDelay
    proposers,       // who can queue
    executors,       // who can execute
    admin
);
```

### Gotchas & Dev Context
- Timelock delay should match user withdrawal speed — if users need 3 days to exit, delay should be ≥ 3 days
- Timelocks are only as good as their delay — 5-minute timelocks are security theater
- `cancel()` function on timelocks lets a multisig abort a malicious queued tx
- Combine timelock with multisig: multisig proposes → timelock delays → multisig (or DAO) executes

### Production FAQ
**Q: What's a reasonable timelock duration for a DeFi protocol?**
A: 24–72 hours for most protocols. High-TVL protocols (Uniswap, Aave) use 48–72 hours minimum.

**Q: Can a timelock be bypassed?**
A: Only if the admin key is compromised. Use a multisig as the timelock admin to distribute key risk.

---

## 15. Multi-Sig Governance

**One-line definition:** A wallet requiring M-of-N key signatures to authorize any transaction, removing single-point-of-failure control.

### Real-World Dev Example
Gnosis Safe (now "Safe") is the industry standard. A 4-of-7 multisig means any 4 of 7 keyholders must approve. Used by Uniswap, MakerDAO, and virtually every major DeFi protocol treasury.

```
Keyholders: Alice, Bob, Carol, Dave, Eve, Frank, Grace (7 total)
Required signatures: 4 of 7

Transaction proposed by Alice
  │
  ├─ Alice signs  ✓
  ├─ Bob signs    ✓
  ├─ Carol signs  ✓
  ├─ Dave signs   ✓  ← 4/7 reached → executes
  ├─ Eve          (not needed)
  ...
```

### Gotchas & Dev Context
- Threshold too low (2-of-3) = low security. Too high (7-of-7) = operational paralysis if one person is unavailable
- Geographically distribute keyholders — all keys in one country = regulatory risk
- Hardware wallets (Ledger, Trezor) for all signers — software wallets are vulnerable
- Safe on L2s: verify your Safe deployment address matches across chains (different salts can give different addresses)
- Multisig ≠ decentralization. A 2-of-3 team multisig is still highly centralized

### Production FAQ
**Q: What's the recommended Safe threshold for a protocol treasury?**
A: 4-of-7 or 5-of-9 is common. Fewer than 3-of-5 is considered under-secured for significant TVL.

**Q: Can multisig signers be smart contracts?**
A: Yes — Gnosis Safe supports contract signers, useful for adding DAO-controlled modules as signers.

---

## 16. Invariant Testing

**One-line definition:** Testing that certain mathematical properties (invariants) always hold true, no matter what sequence of operations is performed.

### Real-World Dev Example
ERC-20 invariant: `sum(balances) == totalSupply` must always be true. If any sequence of `mint`, `burn`, `transfer` calls breaks this — your contract is buggy.

**Foundry invariant test:**
```solidity
contract TokenInvariantTest is StdInvariant, Test {
    MyToken token;

    function setUp() public {
        token = new MyToken();
        targetContract(address(token));
    }

    // Foundry calls random sequences of token functions
    // then checks this invariant after each call
    function invariant_totalSupplyEqualsSumOfBalances() public {
        uint sum = token.balanceOf(alice) + token.balanceOf(bob);
        assertEq(token.totalSupply(), sum);
    }
}
```

### Gotchas & Dev Context
- Invariants must be stateless properties — don't reference call-specific data
- Use `targetContract()` to limit which contracts Foundry fuzzes
- `targetSelector()` whitelists which functions are called — exclude view-only functions to save time
- Invariant failures give you a counter-example call sequence — invaluable for debugging
- Ghost variables (tracked separately in test harness) help define complex invariants

### Production FAQ
**Q: What's the difference between invariant testing and fuzz testing?**
A: Fuzz testing randomizes inputs to a single function. Invariant testing randomizes entire *sequences* of function calls and checks global properties hold throughout.

**Q: How many runs should I configure for invariant testing?**
A: Start with 256 runs, 64 depth (calls per run). Increase for high-value contracts before deployment.

---

## 17. Fuzz Testing (Foundry, Echidna)

**One-line definition:** Automatically generating random inputs to find edge cases that break your functions — replacing hand-crafted unit test inputs.

### Real-World Dev Example
You write a `deposit(uint amount)` function. Fuzz testing discovers that `amount = type(uint256).max` causes an overflow in your fee calculation — something you'd never write as a manual test case.

**Foundry fuzz test:**
```solidity
contract VaultTest is Test {
    Vault vault;

    function setUp() public { vault = new Vault(); }

    // `amount` is randomly generated by Foundry (1000s of values)
    function testFuzz_depositNeverOverflows(uint96 amount) public {
        vm.assume(amount > 0);          // filter invalid inputs
        vault.deposit(amount);
        assertGe(vault.totalDeposits(), amount); // invariant holds?
    }
}
```

**Echidna (property-based fuzzer in Haskell):**
```solidity
// Echidna looks for functions starting with `echidna_`
function echidna_balance_never_negative() public returns (bool) {
    return address(this).balance >= 0; // always true for uint
}
```

```
Fuzzer → random inputs → run function → check assertions
   └─ if assertion fails → shrink to minimal failing case
```

### Gotchas & Dev Context
- Foundry uses `uint96` (not `uint256`) by default for faster coverage — cast up if needed
- `vm.assume()` filters inputs but too many assumptions = fewer effective tests; prefer `vm.bound()`
- Echidna is stateful — it remembers promising inputs across runs (corpus)
- Neither tool replaces manual review for complex economic/business logic bugs

### Production FAQ
**Q: Foundry fuzz vs Echidna — which should I use?**
A: Foundry for quick integration with your existing test suite. Echidna for deeper stateful fuzzing on complex DeFi logic. Use both on critical code.

**Q: How many fuzz runs are enough?**
A: Default 256 in Foundry is fine for dev. Set `runs = 10000` in `foundry.toml` before final audit prep.

---

## 18. Common Solidity Pitfalls Checklist

**One-line definition:** A quick-reference list of the most frequently exploited mistakes in Solidity contracts.

> Use this as a pre-audit self-review before submitting code for professional review.

---

### ✅ Arithmetic & Types
- [ ] Using Solidity < 0.8 without SafeMath
- [ ] Unsafe type casting (e.g., `uint256` → `uint128` truncation)
- [ ] Using `unchecked` without careful bounds verification
- [ ] Division before multiplication (precision loss)

### ✅ Access Control
- [ ] Missing `onlyOwner` / role checks on sensitive functions
- [ ] Using `tx.origin` for authentication
- [ ] Unprotected initializer functions (upgradeable contracts)
- [ ] Admin private key is a single EOA (not multisig)

### ✅ External Calls
- [ ] Not following Checks-Effects-Interactions (CEI) pattern
- [ ] Not using `ReentrancyGuard` on state-changing external calls
- [ ] Ignoring return value of `.call()` (silent failure)
- [ ] Using `transfer()` or `send()` (2300 gas stipend can break)

### ✅ Oracles & Economics
- [ ] Using DEX spot price as oracle (manipulatable via flash loan)
- [ ] No slippage protection on AMM interactions
- [ ] Single-block governance voting (flash loan governance attack)

### ✅ Signatures & Replay
- [ ] Missing nonce in signed messages
- [ ] Missing `chainId` (cross-chain replay)
- [ ] Missing domain separator (cross-contract replay)
- [ ] Not using EIP-712 for structured signing

### ✅ Storage & Proxy
- [ ] Storage layout change between upgrades
- [ ] Implementation contract not initialized (front-runnable)
- [ ] `delegatecall` to untrusted contracts
- [ ] Missing `_disableInitializers()` in implementation constructor

### ✅ Gas & DoS
- [ ] Unbounded loops over user-controlled arrays
- [ ] Push-payment to arbitrary addresses (revert DoS)
- [ ] `block.gaslimit` dependence
- [ ] Relying on `address(this).balance` (force-feedable)

### ✅ Token Handling
- [ ] Assuming ERC-20 always returns true (some tokens don't)
- [ ] Not handling fee-on-transfer tokens
- [ ] Not handling rebasing tokens
- [ ] Unlimited `approve()` in UI without user awareness

### ✅ Tooling Checks (Run Before Audit)
```bash
# Static analysis
slither . --detect all

# Solidity compiler warnings
forge build --force 2>&1 | grep -i warning

# Coverage
forge coverage

# Fuzz tests
forge test --fuzz-runs 10000
```

---

### Production FAQ
**Q: Which checklist item causes the most hacks?**
A: Reentrancy and access control historically top the charts, but oracle manipulation (flash loan attacks) has become the leading cause of large losses since 2021.

**Q: Should I run Slither on every PR?**
A: Yes — integrate it in CI (GitHub Actions). Many critical bugs have been caught by automated tools before code review.

**Q: What's the fastest way to harden a new contract?**
A: Use OpenZeppelin's audited base contracts (`Ownable2Step`, `ReentrancyGuard`, `Pausable`, `AccessControl`), write invariant + fuzz tests, run Slither, then get an audit. Don't reinvent security primitives.

---

*End of Batch 10 — Security & Auditing*
*Next: Batch 11 — Layer 2s & Scaling Solutions*
