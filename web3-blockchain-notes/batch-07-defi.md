# Batch 7 — DeFi (Decentralized Finance)
> Rebuilding the financial system with open, permissionless smart contracts.

DeFi replaces banks, brokers, and exchanges with on-chain code. Anyone with a wallet can lend, borrow, trade, or earn yield — 24/7, without permission.

---

## 1. DeFi Overview

### Definition
DeFi (Decentralized Finance) is the umbrella term for financial services — trading, lending, saving, insurance — built on public blockchains using smart contracts instead of institutions.

### Real-World Dev Example
A developer deploys a lending contract on Ethereum. Alice deposits ETH as collateral, borrows USDC, all without a credit check or bank account.

```
Traditional Finance          DeFi
─────────────────────────    ──────────────────────────
Bank holds your funds   →    Smart contract holds funds
KYC / credit check      →    Wallet address is identity
9–5 business hours      →    24/7, always-on
Opaque terms            →    Open-source code
```

### Gotchas & Dev Context
- Smart contract bugs = irreversible losses (no "call your bank")
- Gas costs can make small transactions uneconomical
- "Permissionless" means scammers can also deploy freely
- DeFi protocols are composable — one bug can cascade across many

### Production FAQ
**Q: Is DeFi the same as crypto?**  
A: No. Crypto is the asset layer; DeFi is the application layer built on top of it.

**Q: Are DeFi protocols regulated?**  
A: Largely unregulated today, but under increasing scrutiny. Front-ends can be geo-blocked even if contracts can't.

**Q: What's the biggest DeFi risk?**  
A: Smart contract exploits — billions have been lost to reentrancy bugs, oracle manipulation, and logic errors.

---

## 2. AMM (Automated Market Maker)

### Definition
An AMM is a smart contract that sets token prices algorithmically using a mathematical formula instead of matching buyers with sellers via an order book.

### Real-World Dev Example
Uniswap v2 uses `x * y = k`. If a pool has 100 ETH and 200,000 USDC, buying ETH raises its price automatically — no human market maker needed.

```
      x * y = k   (constant product formula)

  ETH pool (x)   USDC pool (y)      k (constant)
  ─────────────  ─────────────      ────────────
      100            200,000         20,000,000

  Buy 10 ETH →  x becomes 90
                y becomes 222,222   (price went up!)
```

### Gotchas & Dev Context
- Large trades move price significantly (price impact)
- `x * y = k` is simple but capital-inefficient for stable pairs
- Uniswap v3 introduced **concentrated liquidity** to fix efficiency
- Price from AMM ≠ real-world market price without arbitrageurs

### Production FAQ
**Q: Who sets the initial price in an AMM pool?**  
A: The first liquidity provider sets it by the ratio they deposit. If wrong, arbitrageurs instantly correct it.

**Q: Why do AMMs still work without buyers/sellers?**  
A: Arbitrage traders continuously keep AMM prices aligned with global market prices, making the system self-correcting.

**Q: Can AMMs be gamed?**  
A: Yes — sandwich attacks exploit predictable price movement in the mempool. MEV (Miner Extractable Value) is a whole field around this.

---

## 3. Liquidity Pool

### Definition
A liquidity pool is a smart contract holding reserves of two (or more) tokens that traders swap against, funded by users who deposit assets.

### Real-World Dev Example
A WBTC/ETH pool on Uniswap holds locked tokens. Every swap fee (e.g., 0.3%) goes to the pool, accruing to depositors proportionally.

```
         ┌──────────────────────────┐
         │      Liquidity Pool       │
         │   [  WBTC  |   ETH  ]    │
         │    50 WBTC | 1000 ETH    │
         └────────────┬─────────────┘
              ↑ deposit│ ↓ swap
         LP provides  │  Trader swaps
         both tokens  │  WBTC → ETH
```

### Gotchas & Dev Context
- Pools need **both** tokens — you can't provide just one (in v2)
- Thin pools = high slippage — avoid trading in low-TVL pools
- Pool reserves are public — large deposits/withdrawals are visible
- Some protocols use single-sided liquidity (e.g., Bancor, Uni v4 hooks)

### Production FAQ
**Q: What happens to pool funds when there's a hack?**  
A: They can be drained instantly. Pools have no insurance by default unless covered by a protocol like Nexus Mutual.

**Q: How are swap fees distributed?**  
A: Proportionally to each LP's share of the pool, accrued in real-time within the pool's token balances.

**Q: Can a liquidity pool go to zero?**  
A: Yes — if one token collapses to zero value, the pool effectively holds only the worthless token. LPs lose.

---

## 4. Liquidity Provider (LP)

### Definition
A Liquidity Provider is any user who deposits token pairs into an AMM pool in exchange for a share of trading fees (and often additional token rewards).

### Real-World Dev Example
You deposit $5,000 of ETH and $5,000 of USDC into a Uniswap pool. You receive LP tokens representing your ~1% share. Every swap in that pool earns you 0.3% × your share.

### Gotchas & Dev Context
- LP tokens are ERC-20 tokens — they can be staked elsewhere for extra yield
- Removing liquidity = burning LP tokens to reclaim underlying assets
- Your share is denominated in **pool %**, not fixed token amounts
- Fees compound inside the pool automatically (no manual claiming in v2)
- Uniswap v3 LPs receive NFTs (not fungible ERC-20s) representing their position range

### Production FAQ
**Q: Is being an LP always profitable?**  
A: No. Impermanent loss can outpace fee income. You need to model both before depositing.

**Q: What's the minimum to be an LP?**  
A: Technically $1, but gas costs make it impractical below ~$500–$1,000 on mainnet Ethereum.

**Q: Are LP tokens transferable?**  
A: Yes. They're standard ERC-20 (or ERC-721 for v3). Losing them = losing your liquidity position.

---

## 5. Impermanent Loss

### Definition
Impermanent Loss (IL) is the temporary loss LPs experience when the price ratio of their deposited tokens diverges from when they deposited — compared to just holding the tokens.

### Real-World Dev Example
You deposit 1 ETH + 1,000 USDC (ETH = $1,000). ETH pumps to $4,000. The AMM rebalances your pool position. You now effectively hold less ETH than if you'd just held.

```
  Deposit:     1 ETH + 1,000 USDC  → Pool value $2,000
  ETH 4x →    AMM rebalances to ~0.5 ETH + 2,000 USDC
  Pool value:  $4,000 (2x)

  Just HODL:   1 ETH + 1,000 USDC = $5,000 (2.5x)

  Impermanent Loss ≈ $1,000 (20% vs holding)
```

### Gotchas & Dev Context
- "Impermanent" because if prices revert, loss disappears
- It becomes **permanent** when you withdraw at a diverged price
- Stablecoin/stablecoin pools (USDC/USDT) have near-zero IL
- IL worsens with higher price divergence — 5x move = ~25% IL

### Production FAQ
**Q: Can fees offset impermanent loss?**  
A: Yes, in high-volume pools with tight ranges (Uni v3). It requires active management.

**Q: Is there a formula for IL?**  
A: Yes: `IL = 2√r/(1+r) − 1` where `r` is the price ratio change. At r=4, IL ≈ 20%.

**Q: Do all DeFi protocols have IL?**  
A: Only AMM-based ones. Order book DEXes and lending protocols don't have IL.

---

## 6. DEX (Decentralized Exchange) — Uniswap, SushiSwap

### Definition
A DEX is an exchange that runs entirely on smart contracts, allowing peer-to-contract token swaps without custody, KYC, or a central operator.

### Real-World Dev Example
Swapping LINK for DAI on Uniswap: your wallet signs a transaction, the AMM contract executes the swap atomically, and tokens land in your wallet. No account needed.

```
  User Wallet
      │
      ▼ approve + swap tx
  ┌───────────────────────┐
  │   Uniswap Router      │
  │   (finds best path)   │
  └─────────┬─────────────┘
            │ routes through pool(s)
  ┌─────────▼──────────┐  ┌──────────────────────┐
  │  LINK/ETH Pool     │→ │  ETH/DAI Pool         │
  └────────────────────┘  └──────────────────────┘
            DAI lands in user wallet
```

### Gotchas & Dev Context
- **Uniswap v2**: simple, battle-tested, constant product AMM
- **Uniswap v3**: concentrated liquidity, capital-efficient, requires active management
- **SushiSwap**: forked from Uni v2, added SUSHI token rewards; "vampire attack" on Uni liquidity
- Front-running and MEV are significant issues on public mempools
- Always check token approval limits — `approve(MAX_UINT256)` is a risk

### Production FAQ
**Q: What's the difference between Uniswap v2 and v3?**  
A: v3 lets LPs provide liquidity within a specific price range, dramatically improving capital efficiency but requiring active management.

**Q: Can I list any token on a DEX?**  
A: Yes — anyone can create a pool for any ERC-20 token pair. This is also why scam tokens proliferate.

**Q: Are DEX transactions reversible?**  
A: No. Once confirmed on-chain, swaps are final. Always double-check slippage settings.

---

## 7. Order Book DEX (dYdX)

### Definition
An Order Book DEX matches buy and sell orders like a traditional exchange, but settles trades on-chain (or via a verifiable off-chain system), without a centralized custodian.

### Real-World Dev Example
On dYdX v4, traders place limit orders for perpetual contracts. The matching engine runs off-chain (on its own Cosmos appchain), but settlement is cryptographically verified.

```
  Traditional CEX Order Book     dYdX Order Book DEX
  ─────────────────────────      ──────────────────────────
  Orders on private server   →   Orders on dYdX chain
  Custodial funds            →   Self-custody (non-custodial)
  Trust the exchange         →   Trust the smart contract
  Fast matching              →   Fast matching (off-chain engine)
                                 + on-chain settlement proof
```

### Gotchas & Dev Context
- Order book DEXes are better for **limit orders and derivatives**; AMMs dominate spot trading
- dYdX v3 used StarkWare ZK-rollup; v4 is a standalone Cosmos chain
- Liquidity depth on order book DEXes is typically lower than centralized peers
- Maker/taker fee model vs. AMM's flat swap fee

### Production FAQ
**Q: Why don't all DEXes use order books?**  
A: On-chain order books are gas-prohibitive. Every order placement/cancellation is a transaction. AMMs are far cheaper.

**Q: Is dYdX really decentralized?**  
A: Partially. dYdX v4 has decentralized matching and settlement but the company still maintains significant infrastructure.

**Q: Who provides liquidity on order book DEXes?**  
A: Professional market makers, not retail LPs as in AMMs.

---

## 8. Lending / Borrowing (Aave, Compound)

### Definition
DeFi lending protocols let users deposit assets to earn interest, and borrow assets by posting collateral — all governed by smart contracts with no credit checks.

### Real-World Dev Example
Alice deposits 10 ETH on Aave → receives `aETH` tokens (interest-bearing). Bob deposits WBTC as collateral → borrows USDC at a variable APR determined by pool utilization.

```
  Depositor Alice              Borrower Bob
       │                             │
       │ deposits ETH                │ deposits WBTC collateral
       ▼                             ▼
  ┌────────────────────────────────────────┐
  │          Aave Lending Pool             │
  │  Supply APY ←── Utilization ──→ Borrow APR │
  └────────────────────────────────────────┘
       │                             │
       │ earns interest              │ borrows USDC
       ▼                             ▼
    aETH tokens                  USDC in wallet
```

### Gotchas & Dev Context
- Interest rates are algorithmic — spike with high utilization (Kink model)
- **Aave**: more assets, flash loans, stable borrow rates, v3 has efficiency mode
- **Compound**: simpler, pioneered liquidity mining with COMP token
- Over-collateralization is mandatory — you can never borrow 100% of collateral value
- Smart contract risk: protocol bugs = drained funds

### Production FAQ
**Q: What interest rate do I get?**  
A: It's dynamic, based on supply/demand in the pool. High utilization → high borrow rate → incentivizes more deposits.

**Q: What's the difference between Aave and a bank savings account?**  
A: No FDIC insurance, no fixed rates, rates can change per block, but potentially much higher yields.

**Q: Can I borrow forever?**  
A: Yes, as long as your health factor stays above 1. Let it fall below and you get liquidated.

---

## 9. Collateralization Ratio

### Definition
The Collateralization Ratio (CR) is the percentage of a loan's value covered by collateral. DeFi requires over-collateralization (CR > 100%) because borrowers are pseudonymous.

### Real-World Dev Example
You deposit $1,500 of ETH and borrow $1,000 USDC → CR = 150%. If ETH drops and CR hits 110% (Aave's liquidation threshold for ETH), you get liquidated.

```
  Collateral Value   $1,500
  ────────────────── ────── = 150% CR  ← Safe zone
  Borrowed Value     $1,000

  ETH price drops ↓
  Collateral Value   $1,100
  ────────────────── ────── = 110% CR  ← Liquidation threshold!
  Borrowed Value     $1,000
```

### Gotchas & Dev Context
- Each asset has its own Loan-To-Value (LTV) and liquidation threshold
- Stablecoins have higher LTVs than volatile assets (less price risk)
- MakerDAO mints DAI against ETH at a 150% minimum CR
- Monitor your CR during volatile markets — gas spikes can prevent timely repayment
- Aave's "Health Factor" = your CR / liquidation threshold (< 1.0 = liquidated)

### Production FAQ
**Q: Why over-collateralize? Banks don't require 150%.**  
A: Banks can sue defaulters. DeFi contracts can't — over-collateralization is the enforcement mechanism.

**Q: What assets can be collateral?**  
A: Protocol-specific. Aave supports ETH, WBTC, LINK, and others. Exotic assets often have lower LTVs.

**Q: How do I improve my CR?**  
A: Repay debt, add more collateral, or swap borrowed assets for less risky ones.

---

## 10. Liquidation

### Definition
Liquidation is the forced sale of a borrower's collateral to repay their loan when their collateralization ratio drops below the protocol's safety threshold.

### Real-World Dev Example
Bob borrowed 1,000 USDC against 1,500 USDC worth of ETH (150% CR). ETH crashes; CR drops to 108%. A liquidation bot repays part of Bob's USDC debt and claims his ETH at a 5-10% discount (liquidation bonus).

```
  Health Factor < 1.0
         │
         ▼
  Liquidation Bot sees opportunity
         │
         ▼
  Bot repays X USDC of Bob's debt
         │
         ▼
  Bot receives Bob's ETH + 5% bonus
  (collateral sold below market price)
         │
         ▼
  Bob keeps remaining collateral
  (if any) after penalty
```

### Gotchas & Dev Context
- Liquidation bots are highly competitive — MEV searchers optimize gas for fastest execution
- Partial liquidation is common — protocols often liquidate only 50% of debt per event
- The borrower pays the liquidation penalty, which is a % of seized collateral
- Aave's "liquidation close factor" caps how much can be liquidated per tx
- ETH gas spikes during market crashes — liquidations and repayments compete for blockspace

### Production FAQ
**Q: Can I avoid liquidation?**  
A: Yes — set up alerts (DeBank, Aave dashboard) and maintain a healthy buffer above minimum CR.

**Q: Who are liquidators?**  
A: Bots (and sometimes humans) that profit from the liquidation bonus. It's a competitive MEV strategy.

**Q: What happens if collateral value crashes faster than liquidation bots respond?**  
A: The protocol incurs "bad debt." Aave has a Safety Module (staked AAVE) as a backstop for this scenario.

---

## 11. Flash Loans

### Definition
A flash loan is an uncollateralized loan that must be borrowed AND repaid within a single blockchain transaction — if repayment fails, the entire transaction reverts.

### Real-World Dev Example
Arbitrage with a flash loan: borrow 1M USDC → buy ETH cheap on DEX A → sell ETH high on DEX B → repay 1M USDC + fee → pocket the spread. All in one tx.

```
  ┌─────────────────────────────────────────────────────┐
  │                  ONE TRANSACTION                    │
  │                                                     │
  │  1. Borrow 1,000,000 USDC from Aave (no collateral) │
  │  2. Buy ETH on Uniswap  (price: $2,000)             │
  │  3. Sell ETH on Sushi   (price: $2,050)             │
  │  4. Repay 1,000,000 USDC + 0.09% fee to Aave        │
  │  5. Keep $500 profit                                │
  │                                                     │
  │  If step 4 fails → ENTIRE tx reverts, no loss       │
  └─────────────────────────────────────────────────────┘
```

### Gotchas & Dev Context
- Flash loans don't require capital — a powerful primitive for arbitrage, liquidations, collateral swaps
- Same-block atomicity is the repayment guarantee — not magic, just Ethereum's transaction model
- Aave charges 0.09% fee; some protocols offer free flash loans
- Used in many famous exploits — attackers flash-borrow huge sums to manipulate prices

### Production FAQ
**Q: Are flash loans only for attackers?**  
A: No — legitimate uses include arbitrage, self-liquidation, collateral swaps, and protocol debt refinancing.

**Q: Do flash loans need any capital?**  
A: Only enough ETH for gas. The loan itself is uncollateralized.

**Q: Can flash loans be blocked by a protocol?**  
A: A protocol can choose not to offer them. Read-only reentrancy guards and TWAP oracles also reduce exploit surface.

---

## 12. Yield Farming

### Definition
Yield Farming is the practice of strategically deploying crypto across DeFi protocols to maximize returns — stacking LP fees, token rewards, and lending interest.

### Real-World Dev Example
"DeFi Summer" 2020: Compound introduced COMP token rewards. Users deposited USDC → earned interest + COMP → sold COMP for more USDC → re-deposited. APYs briefly hit 100%+.

```
  Deposit USDC to Compound
        │
        ├──→ Earn interest (supply APY)
        │
        └──→ Earn COMP tokens (liquidity mining)
                    │
                    ▼
              Sell COMP for more USDC
                    │
                    ▼
              Re-deposit → repeat
              (compounding yield)
```

### Gotchas & Dev Context
- APY figures are often annualized from daily snapshots — not guaranteed
- Token rewards dilute as more farmers join — first-mover advantage is significant
- "Rug pulls" — teams drain liquidity and disappear — are common in farm tokens
- Multi-hop farming increases smart contract risk surface exponentially
- Gas costs on mainnet Ethereum can erase yields on positions < $10,000

### Production FAQ
**Q: Is yield farming sustainable?**  
A: Token-incentivized yields typically drop over time as emissions decrease and competition increases. Fee-only yields (Uni v3) are more sustainable.

**Q: How do I compare yields across protocols?**  
A: Use aggregators: DeFiLlama, Beefy Finance, or Zapper show APR/APY with TVL context.

**Q: What's the difference between APR and APY in DeFi?**  
A: APR is simple interest; APY compounds. DeFi protocols display both — always check which one to avoid being misled.

---

## 13. Staking vs Liquid Staking (Lido, Rocket Pool)

### Definition
**Staking**: Locking ETH to validate Ethereum PoS and earn rewards, but capital is illiquid.  
**Liquid Staking**: A protocol stakes on your behalf and gives you a liquid token (stETH, rETH) representing your staked position.

### Real-World Dev Example
- **Lido**: Deposit ETH → receive `stETH` (rebasing token, balance grows daily) → use stETH in DeFi while earning ~4% APY staking rewards.
- **Rocket Pool**: Deposit ETH → receive `rETH` (value-accruing token, price increases) → decentralized node operators run validators.

```
  Direct Staking            Liquid Staking (Lido)
  ──────────────────        ──────────────────────────────
  32 ETH minimum        →   Any amount (0.01 ETH)
  Illiquid until exit   →   stETH is tradeable immediately
  Run your own node     →   Lido operators run nodes
  Solo validator risk   →   Pooled / diversified risk
```

### Gotchas & Dev Context
- **stETH** pegs to ETH via arbitrage but can de-peg under stress (e.g., Terra collapse)
- Lido is centralized in validator set — governance risk and regulatory risk
- **Rocket Pool** is more decentralized; node operators bond 8 ETH minimum
- Liquid staking tokens can be used as collateral on Aave, Compound — amplifying yield
- Withdrawal delays from Ethereum still apply when Lido/RP redeem underlying ETH

### Production FAQ
**Q: Is stETH always worth 1 ETH?**  
A: Not guaranteed. It trades on secondary markets and can de-peg during crises.

**Q: Which is safer — Lido or Rocket Pool?**  
A: Rocket Pool is more decentralized (permissionless node operators) but Lido has more liquidity.

**Q: Can I use liquid staking tokens in DeFi?**  
A: Yes — stETH/rETH are widely accepted as collateral. This is a core liquid staking use case.

---

## 14. Restaking (EigenLayer)

### Definition
Restaking lets ETH stakers re-use their staked ETH security to validate additional services (called AVSs — Actively Validated Services) and earn extra yield on top of Ethereum staking rewards.

### Real-World Dev Example
You stake ETH via Lido → get stETH → deposit stETH into EigenLayer → opt into an AVS (e.g., a new oracle network or rollup DA layer) → earn additional rewards from that AVS, using the same staked ETH as security.

```
  ETH Staker
      │
      ├── Ethereum PoS validation → ~4% APY
      │
      └── EigenLayer Restaking
              │
              ├── AVS 1 (Oracle)     → +2% APY
              ├── AVS 2 (DA Layer)   → +1.5% APY
              └── AVS 3 (Rollup)     → +1% APY

  Total potential yield: ~8.5% (with added slashing risk)
```

### Gotchas & Dev Context
- Restaking introduces **additional slashing risk** — misbehave on an AVS and you can lose your staked ETH
- EigenLayer is a middleware layer; it doesn't validate Ethereum itself
- "Liquid Restaking Tokens" (LRTs) like eETH (ether.fi) add another layer of complexity
- Yield expectations are often speculative — AVS payments depend on demand
- Systemic risk: if a major restaked AVS is exploited, cascading slashing could affect many stakers

### Production FAQ
**Q: Is restaking safe?**  
A: It adds slashing risk from AVS operators. You're now staking the same ETH for multiple commitments — each with its own risk.

**Q: What is an AVS?**  
A: Actively Validated Service — any system that needs decentralized validation (oracles, bridges, rollup sequencers, etc.).

**Q: Can I restake without running infrastructure?**  
A: Yes — liquid restaking protocols like ether.fi, Renzo, or Kelp DAO handle AVS delegation on your behalf.

---

## 15. TVL (Total Value Locked)

### Definition
TVL is the total dollar value of crypto assets deposited/locked in a DeFi protocol's smart contracts at any given time.

### Real-World Dev Example
Aave's TVL = sum of all deposits across all asset pools (ETH, WBTC, USDC, etc.) in USD terms. A TVL of $10B means $10B worth of tokens are sitting in Aave's contracts.

```
  Protocol TVL Breakdown (simplified Aave example):

  ETH pool:    50,000 ETH × $3,000  =  $150M
  WBTC pool:   1,000 WBTC × $60,000 =  $ 60M
  USDC pool:   200,000,000 USDC      =  $200M
  ...
  ─────────────────────────────────────────────
  Total TVL                           =  $410M+
```

### Gotchas & Dev Context
- TVL can be misleading: double-counted TVL is common (stETH deposited in Aave counts in both Lido and Aave TVL)
- Price-driven changes: ETH price up 10% → TVL up 10% with no new deposits
- TVL ≠ revenue. High TVL with low fees = vanity metric
- Use **DeFiLlama** for cross-protocol, cross-chain TVL with deduplication
- TVL crashed 70%+ from peak in the 2022 bear market

### Production FAQ
**Q: Is higher TVL always better?**  
A: Generally signals trust and adoption, but not always. Some protocols have high TVL via token incentives that mask low organic usage.

**Q: How is TVL calculated?**  
A: Sum of all token balances in protocol contracts × their current USD prices. On-chain, aggregated by tools like DeFiLlama.

**Q: What's a healthy TVL/Market Cap ratio?**  
A: Below 1.0 (TVL > Market Cap) is often considered undervalued. Above 3–5x can signal overvaluation or mercenary capital.

---

## 16. Slippage & Price Impact

### Definition
**Price Impact**: How much your trade moves the pool's price (larger trade = bigger move).  
**Slippage**: The difference between expected trade price and actual execution price (includes price impact + market movement during tx).

### Real-World Dev Example
You want to swap $100K USDC for ETH in a pool with $500K liquidity. Your trade is 20% of the pool — it will move the price significantly. You set 1% slippage tolerance; if the price moves more, the tx reverts.

```
  Pool before swap:   100 ETH | 200,000 USDC  (price = $2,000/ETH)
  You sell 20,000 USDC
  Pool after swap:    ~90.9 ETH | 220,000 USDC (price = $2,420/ETH)

  You received ~9.1 ETH at avg price $2,198 — NOT $2,000
  Price impact: ~9.9%
```

### Gotchas & Dev Context
- High slippage tolerance = susceptible to sandwich attacks (MEV bots front-run you)
- Low slippage tolerance = tx might revert in volatile conditions
- Uniswap and other DEXes show estimated price impact before confirming
- Deep liquidity pools have less slippage for the same trade size
- For large trades, split into smaller chunks or use a DEX aggregator (1inch, Paraswap)

### Production FAQ
**Q: What's a safe slippage setting?**  
A: 0.5% for stablecoins, 0.5–1% for majors (ETH/BTC), up to 3–5% for low-liquidity tokens.

**Q: Why did I receive fewer tokens than expected?**  
A: Slippage occurred — price moved between estimation and execution. Check your slippage settings.

**Q: How do DEX aggregators reduce slippage?**  
A: They split your trade across multiple pools and routes to minimize price impact on any single pool.

---

## 17. Oracle (Chainlink, Pyth)

### Definition
An oracle is a system that brings real-world off-chain data (prices, weather, sports results) onto the blockchain, since smart contracts cannot fetch external data themselves.

### Real-World Dev Example
Aave needs ETH's USD price to calculate collateralization ratios. It queries a Chainlink Price Feed — a decentralized network of nodes that aggregate prices from multiple sources and publish them on-chain.

```
  Off-Chain World           On-Chain World
  ─────────────────         ────────────────────────────
  Binance price: $3,010
  Coinbase:      $3,008  → Chainlink Node Network
  Kraken:        $3,012        │ aggregates + signs
                               ▼
                    Chainlink Price Feed Contract
                    ETH/USD = $3,010 (on-chain)
                               │
                    Aave reads this price to check
                    borrower health factors
```

### Gotchas & Dev Context
- **Chainlink**: decentralized, battle-tested, expensive (LINK fees), slightly slow update frequency
- **Pyth**: high-frequency (sub-second), pull-based oracle — consumers pay to update price on-chain
- Oracle latency: prices update every heartbeat (e.g., 1 hour or 0.5% deviation trigger)
- Never use DEX spot prices as oracles — they're instantly manipulable
- TWAP (Time-Weighted Average Price) provides manipulation-resistance over a time window

### Production FAQ
**Q: What's the difference between push and pull oracles?**  
A: Push oracles (Chainlink) update prices on-chain on a schedule. Pull oracles (Pyth) update only when a user triggers it, saving gas.

**Q: Can I use a single oracle for a production protocol?**  
A: Risky. Use multiple oracles or a TWAP as fallback to reduce single-point-of-failure risk.

**Q: Are oracle updates instant?**  
A: No. Chainlink has heartbeat intervals (often 1hr or on 0.5% price deviation). Use Pyth for latency-sensitive apps.

---

## 18. Oracle Manipulation Attack

### Definition
An oracle manipulation attack is when an attacker artificially moves a price on-chain (usually a DEX spot price used as an oracle) to trick a protocol into making incorrect decisions — like allowing under-collateralized borrows.

### Real-World Dev Example
The Mango Markets hack (2022, $116M): Attacker bought MNGO tokens to pump their price, then borrowed massively against inflated collateral value (which the protocol read from on-chain spot price). Drained the treasury.

```
  Attack Flow:
  ┌──────────────────────────────────────────────────┐
  │ 1. Attacker flash-borrows huge capital            │
  │ 2. Buys token X on a thin DEX → price spikes     │
  │ 3. Protocol reads this spot price as "real"       │
  │ 4. Attacker's collateral value = inflated         │
  │ 5. Attacker borrows against inflated value        │
  │ 6. Flash loan repaid; protocol left with bad debt │
  └──────────────────────────────────────────────────┘
```

### Gotchas & Dev Context
- **Mitigation 1**: Use Chainlink or Pyth (not DEX spot prices) for collateral pricing
- **Mitigation 2**: Use TWAP oracles — harder to manipulate over time
- **Mitigation 3**: Circuit breakers — pause protocol if price deviates too fast
- Many billion-dollar DeFi hacks are oracle manipulation + flash loan combos
- Even Chainlink feeds have been manipulated in edge cases (low liquidity pairs)

### Production FAQ
**Q: How can a TWAP resist manipulation?**  
A: A TWAP averages price over time (e.g., 30 min). Maintaining a fake price for 30 minutes is enormously expensive in capital and gas.

**Q: Are flash loans required for oracle attacks?**  
A: Not always, but flash loans amplify attacks by providing enormous temporary capital at zero cost.

**Q: Which protocols are most vulnerable?**  
A: Protocols using DEX spot price as oracle and handling large TVL with illiquid collateral tokens.

---

## 19. Composability / Money Legos

### Definition
Composability is DeFi's ability to combine protocols like building blocks — output of one protocol becomes input to another — creating complex financial instruments from simple primitives.

### Real-World Dev Example
A single Ethereum transaction can: borrow ETH via Aave flash loan → swap to stETH on Curve → deposit stETH into Yearn vault → use Yearn vault token as collateral on MakerDAO → mint DAI → repay flash loan. All atomically.

```
  "Money Legos" Stack:

  ┌─────────────┐
  │  Yearn Vault│  ← automated yield strategy
  └──────┬──────┘
         │ deposits into
  ┌──────▼──────┐
  │  Curve Pool │  ← stablecoin AMM
  └──────┬──────┘
         │ swap from
  ┌──────▼──────┐
  │    Aave     │  ← flash loan provider
  └──────┬──────┘
         │ borrowed from
  ┌──────▼──────┐
  │  Your Wallet│
  └─────────────┘
  All in one atomic tx — composability in action
```

### Gotchas & Dev Context
- Composability is a superpower AND a risk multiplier — one broken protocol can cascade
- "DeFi dominoes": Protocol A is hacked → stablecoin B loses its peg → Protocol C's collateral crashes
- **Re-entrancy** attacks exploit composability — always use checks-effects-interactions pattern
- Gas costs compound across hops — deep stacks are expensive
- Protocol upgrades can break integrations — monitor dependency changelogs

### Production FAQ
**Q: What's the biggest risk of composability?**  
A: Systemic contagion. When Terra collapsed, protocols holding UST as collateral across DeFi all failed together.

**Q: Can I build on top of Uniswap or Aave?**  
A: Yes — they expose interfaces and are explicitly designed for integration. Yearn Finance is essentially a composability layer on top of existing protocols.

**Q: How do I audit a composable system?**  
A: Audit each integration point, not just your own contract. Assume dependencies can fail and build fallbacks.

---

*Batch 7 complete — 19 DeFi concepts from protocol primitives to systemic risks.*  
*Next: Batch 8 — NFTs & Token Standards (ERC-721, ERC-1155, Metadata, Royalties)*
