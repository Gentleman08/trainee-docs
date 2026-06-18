# Batch 12 — DAOs, Governance & Identity
> Building organizations and identity systems that no one controls alone.

---

## 1. DAO (Decentralized Autonomous Organization)

**Definition:** A group that makes decisions via smart contracts and token votes — no CEO, no HR, just code and consensus.

### Real-World Dev Example
Compound Finance is a DAO. COMP token holders vote on interest rate changes. When a vote passes, the smart contract *automatically* executes the change — no admin needed.

```
DAO = Smart Contracts + Token Voting + Treasury
```

### ASCII Diagram
```
Members (token holders)
        |
        v
  [Governance Contract]
        |
   Vote Passes?
   /           \
 YES            NO
  |              |
Execute        Discard
Proposal       Proposal
```

### Gotchas & Dev Context
- DAOs can still be controlled by whales (large token holders)
- Code bugs = permanent loss of funds (no "undo" button)
- Legal status is murky in most countries — Wyoming is an exception
- Participation rates are notoriously low (often <10%)
- Front-end can be shut down; contract always lives on-chain

### Production FAQ
**Q: Can a DAO be hacked?**
A: Yes. The infamous 2016 "The DAO" hack drained $60M by exploiting a re-entrancy bug, which caused the Ethereum hard fork.

**Q: Do all DAOs need a token?**
A: No. Some use NFTs for membership, multi-sig wallets for execution, or reputation scores — tokens are just the most common mechanism.

**Q: How do DAOs pay contributors?**
A: Via treasury grants — members submit proposals, the DAO votes, and the smart contract releases funds automatically on approval.

---

## 2. Governance Proposal Lifecycle

**Definition:** The structured journey a change request takes from idea → vote → execution inside a DAO.

### Real-World Dev Example
On Uniswap DAO: a dev posts on the forum → community debates → formal on-chain proposal submitted → 7-day voting window → if passes, 2-day timelock → auto-execute.

### ASCII Diagram
```
[Idea / Forum Post]
        |
  [Temperature Check]  ← informal poll (Snapshot)
        |
  [Formal Proposal]    ← on-chain, requires token threshold
        |
  [Voting Period]      ← e.g., 7 days
        |
   Quorum met?
   /        \
 YES         NO
  |           |
[Timelock]  [Defeated]
  |
[Execution]
```

### Gotchas & Dev Context
- Most DAOs require a **minimum token threshold** to submit proposals (spam prevention)
- **Quorum** = minimum % of total supply that must vote; low quorum = easy manipulation
- Timelock delay is a security buffer — gives community time to react to malicious proposals
- Proposal IDs are deterministic hashes of proposal content on-chain

### Production FAQ
**Q: What happens if quorum isn't reached?**
A: The proposal is defeated by default, regardless of how votes split — even if 100% of voters said yes.

**Q: Can a proposal be cancelled after submission?**
A: Usually only by the proposer (or guardian role) before execution. Once in timelock, it's very hard to stop.

**Q: How long should a voting period be?**
A: 3–7 days is standard. Too short = low participation. Too long = blockers on urgent changes.

---

## 3. On-Chain vs Off-Chain Governance

**Definition:** On-chain governance executes decisions via smart contracts automatically; off-chain governance uses social consensus — humans still push the button.

### Real-World Dev Example
- **On-chain:** Compound Governor — vote recorded on Ethereum, execution is automatic.
- **Off-chain:** Uniswap uses Snapshot for signalling, then a multi-sig executes the result manually.

### ASCII Diagram
```
OFF-CHAIN                     ON-CHAIN
─────────────────────         ────────────────────────
Forum post → Snapshot poll    Proposal tx → Vote tx
     ↓                              ↓
Human reads result            Smart contract reads result
     ↓                              ↓
Multi-sig manually executes   Auto-executes after timelock
```

### Gotchas & Dev Context
- On-chain voting costs gas per vote — discourages small holders
- Off-chain is gasless but relies on trust (multi-sig could ignore result)
- Hybrid is most common: Snapshot for signalling, on-chain for execution
- On-chain provides cryptographic proof; off-chain is just signatures
- "Governance minimization" is a design philosophy — minimize what needs votes

### Production FAQ
**Q: Is off-chain governance less secure?**
A: It's less *trustless* — it introduces human execution risk. But it's cheaper and sees higher participation.

**Q: Can off-chain and on-chain results conflict?**
A: Yes, and it has happened. If the multi-sig ignores a Snapshot vote, there's no smart contract to enforce the outcome.

---

## 4. Snapshot (Off-Chain Voting)

**Definition:** A gasless voting tool that uses signed messages and token balances at a specific block to record votes — nothing hits the chain.

### Real-World Dev Example
A DAO posts a proposal on snapshot.org. Voters sign a message with their wallet (free). Snapshot checks their token balance at block #19,200,000 — the "snapshot block" — and tallies weighted votes.

```js
// No transaction — just a signature
const sig = await wallet.signMessage(proposalHash);
```

### ASCII Diagram
```
Voter Wallet ──signs──▶ Snapshot Server
                               |
                    Check token balance
                    at snapshot block
                               |
                    Store signed vote
                    (IPFS / off-chain DB)
                               |
                    Tally & display result
```

### Gotchas & Dev Context
- Votes are NOT enforced by code — a centralized server aggregates them
- Snapshot block prevents buying tokens after proposal to vote
- Supports many voting strategies: ERC-20 balance, NFT holdings, LP tokens, etc.
- IPFS storage means results are permanent but execution isn't automatic
- Custom "spaces" let any project set their own voting rules

### Production FAQ
**Q: Can someone fake a Snapshot vote?**
A: They'd need to forge a wallet signature — cryptographically infeasible. But the *execution* of the result can be ignored by whoever controls the multi-sig.

**Q: What's a voting strategy in Snapshot?**
A: Logic that determines voting power. E.g., "1 token = 1 vote" or "square root of staked balance" for quadratic voting.

---

## 5. Governor Contract (OpenZeppelin)

**Definition:** A battle-tested smart contract template from OpenZeppelin that implements the full on-chain governance lifecycle out of the box.

### Real-World Dev Example
```solidity
// Minimal Governor setup
contract MyDAO is Governor, GovernorVotes, GovernorTimelockControl {
    constructor(IVotes _token, TimelockController _timelock)
        Governor("MyDAO")
        GovernorVotes(_token)
        GovernorTimelockControl(_timelock) {}

    function votingDelay() public pure override returns (uint256) { return 1; }
    function votingPeriod() public pure override returns (uint256) { return 50400; } // ~1 week
    function quorumNumerator() public pure override returns (uint256) { return 4; } // 4%
}
```

### Gotchas & Dev Context
- Governor is **modular** — mix in `GovernorVotesQuorumFraction`, `GovernorSettings`, etc.
- Token must implement `IVotes` interface (use `ERC20Votes` wrapper)
- `propose()` requires caller to hold minimum token threshold (`proposalThreshold`)
- Governor alone doesn't hold funds — pair with `TimelockController` as executor
- Use OZ Wizard (wizard.openzeppelin.com) to scaffold configs safely

### Production FAQ
**Q: Can I change voting parameters after deployment?**
A: Yes, if you inherit `GovernorSettings` — parameters like `votingPeriod` become proposal-governed themselves.

**Q: What's the difference between `Governor` and `GovernorBravo`?**
A: GovernorBravo is Compound's own implementation. OZ Governor is cleaner, more modular, and widely preferred for new projects.

**Q: Does the Governor need upgradeability?**
A: It's intentionally non-upgradeable by default. Changing governance logic itself should go through a governance vote.

---

## 6. Timelock Controller

**Definition:** A smart contract that enforces a mandatory waiting period between a governance vote passing and its on-chain execution.

### Real-World Dev Example
MakerDAO uses a 48-hour governance delay. After a vote to change the DAI stability fee passes, no one — not even core devs — can execute it for 48 hours.

### ASCII Diagram
```
Vote Passes
     |
     v
[Timelock Queue]  ← proposal scheduled here
     |
  48 hours pass
     |
     v
[Anyone can call execute()]
     |
     v
Action performed on-chain
```

### Gotchas & Dev Context
- Timelock is the actual **owner** of protocol contracts — the Governor proposes *through* it
- The delay gives community time to exit (or fork) if a malicious proposal slips through
- `MinDelay` is set at deployment — changing it requires going through governance itself
- Two special roles: **Proposer** (Governor contract) and **Executor** (often open to anyone)
- Cancelling a queued action requires the `CANCELLER_ROLE`

### Production FAQ
**Q: What's a reasonable timelock delay?**
A: 24–72 hours for most protocols. High-value DeFi systems use up to 7 days. Too short defeats the purpose; too long blocks emergency fixes.

**Q: Can the timelock be bypassed in an emergency?**
A: Only if you add a guardian/admin role — which partially centralizes the system. Most protocols accept this tradeoff with a time-limited "Guardian" that can self-destruct its powers.

---

## 7. Quadratic Voting

**Definition:** A voting system where voting power scales with the *square root* of tokens held — making it cheaper for small holders to have proportional influence.

### Real-World Dev Example
If Alice holds 100 tokens and Bob holds 10,000 tokens:
- Token-weighted: Bob has 100× Alice's power
- Quadratic: Bob has only ~10× Alice's power (`√10000 = 100` vs `√100 = 10`)

```
Voting Power = √(tokens held)
```

### ASCII Diagram
```
Tokens:  1    4    9    16   100   10000
Power:   1    2    3     4    10     100
         ▲ quadratic curve flattens whale advantage
```

### Gotchas & Dev Context
- **Sybil attack vulnerability**: split tokens across 1,000 wallets to get √1 × 1000 = 1000 power vs √1000 = 31.6 power from one wallet
- Requires identity verification (e.g., Gitcoin Passport) to work properly
- Gitcoin Grants uses QV for funding allocation — most successful real-world implementation
- Computationally more complex to implement on-chain (requires square root math)
- Often used off-chain via Snapshot strategies to avoid gas complexity

### Production FAQ
**Q: Does quadratic voting actually stop whales?**
A: It reduces their power but doesn't eliminate it. Without Sybil resistance, it can be gamed by splitting wallets — identity layers are essential.

**Q: Where is QV used in production?**
A: Gitcoin Grants (funding), RadicalxChange experiments, some Snapshot spaces. Rare on-chain due to Sybil risk.

---

## 8. Token-Weighted Voting

**Definition:** The simplest governance model — 1 token = 1 vote. More tokens = more power. Full stop.

### Real-World Dev Example
Uniswap governance: hold 1 UNI = 1 vote. A16Z holds ~4% of UNI supply → ~4% of all votes on every proposal.

```solidity
// OZ ERC20Votes tracks historical balances for snapshot voting
token.getPastVotes(account, proposalSnapshot);
```

### Gotchas & Dev Context
- Most common model — simple to implement and audit
- **Plutocracy risk**: largest holders dominate; VC-backed projects face heavy criticism for this
- Delegation is key — token holders can delegate to representatives without transferring tokens
- Quorum requirements help but don't solve the whale problem
- "Vote buying" is legal in on-chain governance (controversial)
- Abstain vote is a distinct option in OZ Governor (`VoteType.Abstain`)

### Production FAQ
**Q: What's delegation and why does it matter?**
A: Delegation lets passive holders assign their votes to an active community member without losing custody of tokens. Critical for reaching quorum.

**Q: Can I vote with tokens locked in DeFi protocols?**
A: Not by default. Protocols like Aave issue "aTokens" or use vote-escrow (veTokens) to let you vote while staying in the protocol.

---

## 9. Rage Quit

**Definition:** A mechanism letting dissenting DAO members exit and take their proportional share of the treasury *before* a proposal they disagree with executes.

### Real-World Dev Example
MolochDAO popularized this. If a DAO votes to fund Project X and you hate it, you can rage quit *before* the transaction executes and walk away with your ETH share.

### ASCII Diagram
```
Proposal passes
      |
  [Grace Period]  ← window to rage quit
      |        \
   Stay in      Rage Quit
      |              |
  Participate   Burn your shares
  in outcome    Receive pro-rata
                treasury ETH
```

### Gotchas & Dev Context
- Only works if treasury is in **separable assets** (ETH, ERC-20) — not if funds are already deployed
- The grace period must be designed into the contract at launch — retrofitting is hard
- Protects minorities from "51% attacks" where a majority votes to drain the treasury
- Popularized by MolochDAO v2; also in DAOhaus, Moloch forks
- Limits how the DAO can use funds (can't easily lock capital long-term if rage quit looms)

### Production FAQ
**Q: Can rage quit bankrupt a DAO?**
A: If everyone disagrees with a proposal, a mass rage quit could drain the treasury. In practice, the *threat* of rage quit keeps proposals reasonable.

**Q: Does Compound or Uniswap have rage quit?**
A: No. Large token-weighted DAOs typically don't — it's more common in smaller, membership-based DAOs like Moloch forks.

---

## 10. Treasury Management

**Definition:** How a DAO stores, diversifies, and deploys its pooled funds — the lifeblood that funds contributors, grants, and protocol development.

### Real-World Dev Example
Uniswap DAO treasury holds billions in UNI tokens. The challenge: UNI price volatility = unpredictable runway. Governance voted to diversify into stablecoins to cover 4+ years of operating costs.

```
Treasury Health = Diversification + Runway + Yield Strategy
```

### ASCII Diagram
```
                [DAO Treasury]
               /       |       \
    [Native Token]  [Stables]  [ETH/BTC]
          |               |
    Price volatile    Stable runway
    (long-term)       (operations)
```

### Gotchas & Dev Context
- Treasury contract is usually the **Timelock** controller — only governed actions can spend it
- 100% native token treasury = existential risk if token price crashes
- **Gnosis Safe** is the standard multi-sig for interim/emergency treasury control
- DeFi yield strategies (Aave, Yearn) can generate passive income on idle stables
- Budget proposals must go through full governance — slow for recurring payments → use **streaming** (Sablier, Superfluid)

### Production FAQ
**Q: How do DAOs handle contributor salaries?**
A: Token streaming protocols like Sablier release funds per-second to contributors — approved once by governance, no recurring votes needed.

**Q: What's the biggest treasury risk?**
A: Governance attacks — an attacker accumulates tokens, passes a malicious proposal, drains the treasury. Timelock + rage quit are the main defenses.

---

## 11. Multi-Sig (Gnosis Safe)

**Definition:** A wallet that requires M-of-N signatures to execute a transaction — like a joint bank account where N people must agree before money moves.

### Real-World Dev Example
A 5-of-9 Gnosis Safe: 9 trusted signers (core team + community reps), any 5 must sign to move funds. Used by Uniswap, Aave, and most major protocols for treasury control.

### ASCII Diagram
```
Transaction Proposed
        |
   Signers notified (9 total)
        |
  5 approve → ✅ Execute
  4 approve → ❌ Blocked
  Threshold not met
```

### Gotchas & Dev Context
- Gnosis Safe = battle-tested, audited, used by $100B+ in assets
- Threshold is a tradeoff: too high → gridlock; too low → security risk
- Safe is controlled by **owners** (EOAs or contracts) — if keys are lost, funds are locked forever
- Module system lets you add custom logic (spending limits, role-based access)
- `safe-sdk` and `safe-core-api` for programmatic tx building
- Multi-sig ≠ fully decentralized — it's a trusted-committee model

### Production FAQ
**Q: Is a multi-sig as secure as a DAO governance contract?**
A: No — multi-sig requires trusting the signers; governance contracts require only trusting the code. Multi-sig is faster and cheaper; governance is more decentralized.

**Q: What happens if a signer loses their key?**
A: The remaining signers can use another transaction (with quorum) to replace the lost signer — as long as quorum is still achievable.

---

## 12. Decentralized Identity (DID)

**Definition:** A self-sovereign identity standard where *you* own and control your identity — no Google, no Facebook, no government required.

### Real-World Dev Example
A user creates a `did:ethr:0xABC...` identifier. They store a DID Document on IPFS pointing to their public key. Verifiers check signatures against that key — no central authority involved.

```
DID = did:method:method-specific-id
e.g. did:ethr:0x71C...Ba92
     did:key:z6Mk...
     did:web:example.com
```

### ASCII Diagram
```
[You] ──controls──▶ [DID Document]  (stored on IPFS/chain)
                          |
                    Public Keys
                    Service Endpoints
                    Authentication Methods
                          |
              [Verifier checks signature]
                    No central lookup
```

### Gotchas & Dev Context
- W3C DID spec is the standard — dozens of "methods" (did:ethr, did:key, did:web, etc.)
- DID Document is public; private keys stay with you
- **Key rotation** is critical — losing your private key = losing your identity
- Uport, Ceramic Network, and Spruce ID are key ecosystem players
- Different from ENS — ENS is a naming system, DID is an identity framework

### Production FAQ
**Q: Can I have multiple DIDs?**
A: Yes — you can have separate DIDs for work, personal, and pseudonymous contexts. That's a feature, not a bug.

**Q: How does DID relate to zero-knowledge proofs?**
A: ZK proofs let you *prove claims* about your DID (e.g., "I'm over 18") without revealing the underlying data — essential for privacy-preserving identity.

---

## 13. Verifiable Credentials (VCs)

**Definition:** Cryptographically signed digital certificates — like a diploma or driver's license — that you carry in your wallet and share selectively without the issuer being involved.

### Real-World Dev Example
A university issues a VC for your degree. You store it in your wallet app. An employer asks you to prove your degree — you present it. They verify the university's signature. No email to the registrar needed.

```json
{
  "type": ["VerifiableCredential", "UniversityDegree"],
  "issuer": "did:ethr:0xUniversity...",
  "credentialSubject": {
    "id": "did:ethr:0xYou...",
    "degree": "B.Sc. Computer Science"
  },
  "proof": { "type": "EcdsaSecp256k1Signature2019", ... }
}
```

### Gotchas & Dev Context
- W3C VC Data Model is the standard — JSON-LD format
- VCs live in your wallet (offline), not on-chain (unless anchored)
- **Revocation** is the hard part — issuer must publish revocation status without violating privacy
- Selective disclosure: share only "employed at X" without revealing full credential
- Gitcoin Passport aggregates VCs from multiple sources to build a Sybil-resistance score

### Production FAQ
**Q: What's the difference between a VC and an NFT?**
A: NFTs are public and transferable; VCs are private, non-transferable (ideally), and identity-bound. An NFT proves *ownership*; a VC proves *a claim about you*.

**Q: Do VCs require a blockchain?**
A: No. They're just signed JSON. Blockchain can anchor the DID for decentralized key resolution, but it's optional.

---

## 14. ENS (Ethereum Name Service)

**Definition:** DNS for Ethereum — maps human-readable names like `alice.eth` to wallet addresses, IPFS hashes, or any on-chain data.

### Real-World Dev Example
Instead of sending ETH to `0x71C7656EC7ab88b098defB751B7401B5f6d8976F`, you send to `alice.eth`. The ENS registry resolves it for you.

```js
const address = await provider.resolveName("alice.eth");
// returns "0x71C7656EC7ab88b098defB751B7401B5f6d8976F"
```

### ASCII Diagram
```
"alice.eth"
     |
[ENS Registry Contract]
     |
[Resolver Contract]
     |
Returns: wallet address, IPFS hash,
         Twitter handle, email, avatar...
```

### Gotchas & Dev Context
- `.eth` names are NFTs (ERC-721) — tradeable on OpenSea
- Renewal fees apply annually — forgotten renewals = domain squatted by others
- **Reverse resolution**: map address → name for display (require explicit setup)
- Subdomains: `dev.alice.eth` — the holder of `alice.eth` controls all subdomains
- ENS supports multi-chain addresses (BTC, SOL) stored in one `.eth` record
- Never hardcode resolved addresses — always resolve at runtime

### Production FAQ
**Q: Is ENS just for Ethereum addresses?**
A: No. ENS records can store Bitcoin addresses, content hashes (IPFS/Swarm), text records (social handles, email, avatar), and custom ABI data.

**Q: What happens when a name expires?**
A: There's a 90-day grace period to renew. After that, it goes to auction. Many valuable names have been lost to missed renewals.

---

## 15. Lens Protocol / Farcaster (Decentralized Social)

**Definition:** Blockchain-based social graph protocols where *you* own your followers, posts, and identity — not a platform company.

### Real-World Dev Example
**Lens:** Your profile is an NFT. Your posts are on-chain. If Lenster (a Lens app) shuts down, your content and followers still exist — any other Lens app can read them.

**Farcaster:** Posts ("casts") are stored on a decentralized network of "Hubs". Your identity is anchored to Ethereum, but content lives off-chain for speed.

### ASCII Diagram
```
LENS PROTOCOL                  FARCASTER
────────────────               ─────────────────
Profile NFT (ERC-721)          FID (on-chain ID)
  ↓ Publications               ↓ Casts (off-chain Hubs)
  ↓ Follows (on-chain)         ↓ Follows (on-chain)
  ↓ Mirrors/Comments           ↓ Frames (mini-apps)

Apps: Lenster, Phaver, Hey    Apps: Warpcast, Supercast
```

### Gotchas & Dev Context
- Lens posts gas fees per interaction — expensive at scale; Lens v2 uses gasless relayer
- Farcaster prioritizes off-chain speed but anchors identity on-chain (Optimism)
- Portability is the killer feature — users can switch apps without losing audience
- **Frames** (Farcaster) = interactive mini-apps embedded in posts — very popular for on-chain actions
- Both are still early-stage; social graph is sparse compared to Twitter/Instagram

### Production FAQ
**Q: Can I build my own app on Lens or Farcaster?**
A: Yes. Both expose open APIs/SDKs. Lens has `@lens-protocol/client`, Farcaster has `@farcaster/hub-nodejs`. Your app reads the shared social graph.

**Q: Who owns the data on these platforms?**
A: The user. That's the entire point — you can take your profile to any app built on the protocol.

---

## 16. Soulbound Tokens (SBTs) for Reputation

**Definition:** Non-transferable NFTs permanently bound to a wallet — they represent achievements, credentials, or reputation that can't be bought or sold.

### Real-World Dev Example
Gitcoin issues an SBT for completing a hackathon. You can't sell it. Employers or DAOs can see it in your wallet and trust it represents *your* achievement, not a purchased one.

```solidity
// SBT: block all transfers
function _beforeTokenTransfer(address from, address, uint256, uint256) 
    internal override {
    require(from == address(0), "Soulbound: non-transferable");
}
```

### ASCII Diagram
```
Issuer (DAO / Protocol / Uni)
        |
  Issues SBT to Wallet
        |
  [🔒 Locked to that wallet]
        |
  Proves: Achievements, Skills,
          Attendance, Reputation,
          Voting history
```

### Gotchas & Dev Context
- **Privacy risk**: a wallet full of SBTs is a permanent, public identity profile — can be used for discrimination
- No standard yet — implementations vary (ERC-5192 is a lightweight proposal, ERC-4973 is another)
- Revocation is tricky — issuer needs a mechanism to invalidate without transferring
- Can't be sold → can't be financialized → better signal of genuine achievement
- Vitalik Buterin co-authored the original "Decentralized Society" paper proposing SBTs (2022)

### Production FAQ
**Q: What if I lose my wallet? My SBTs are gone?**
A: Yes — this is the biggest UX problem. Solutions include social recovery wallets (EIP-4337) or issuer re-issuance mechanisms, but no universal standard exists yet.

**Q: Can SBTs replace resumes?**
A: Theoretically yes — on-chain proof of contributions, degrees, and skills. In practice, adoption is early and privacy concerns need solving first.

---

*End of Batch 12 — DAOs, Governance & Identity*
