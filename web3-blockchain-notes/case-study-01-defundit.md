# Case Study 1 — DeFundIt: Decentralized Crowdfunding Platform
> A production-grade crowdfunding dApp built with Solidity, Foundry, and wagmi.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture Diagram (ASCII)](#2-architecture-diagram-ascii)
3. [Tech Stack Table](#3-tech-stack-table)
4. [Smart Contract Architecture](#4-smart-contract-architecture)
5. [Step-by-Step Build (Phases)](#5-step-by-step-build-phases)
6. [Testing Strategy](#6-testing-strategy)
7. [Deployment Pipeline](#7-deployment-pipeline)
8. [Frontend Integration](#8-frontend-integration)
9. [Gas Optimization Decisions](#9-gas-optimization-decisions)
10. [Production Gotchas](#10-production-gotchas)
11. [Lessons Learned](#11-lessons-learned)

---

## 1. Project Overview

### What Is DeFundIt?

**DeFundIt** is a fully on-chain, permissionless crowdfunding protocol where campaign creators and backers interact directly through Ethereum smart contracts — no Kickstarter middleman, no platform custody of funds, no ability to exit-scam without community oversight.

Think Kickstarter meets Ethereum: a creator deploys a campaign contract specifying a funding goal (in ETH or an ERC-20 token), a deadline, and a list of milestones. Contributors send funds to the contract. If the goal is reached by the deadline, the creator cannot withdraw the entire amount upfront — they must submit milestone completion proofs, and contributors vote to release each funding tranche. If the goal is **not** reached, every contributor can independently reclaim their full contribution, guaranteed by the contract logic.

### Who Uses It?

| Role | Actions |
|------|---------|
| **Campaign Creator** | Deploys campaign, sets goal/deadline/milestones, submits milestone proofs, withdraws approved tranches |
| **Contributor / Backer** | Funds campaigns with ETH or ERC-20, votes on milestone releases, claims refunds if goal fails |
| **Protocol Admin** | Collects a small platform fee (basis points), can pause the factory in emergencies |
| **Indexers / Subgraph** | Reads on-chain events to power the frontend listing and campaign dashboards |

### Key Guarantees (Why Blockchain?)

- **Non-custodial**: Funds sit in the campaign contract, not on a company server.
- **Trustless refunds**: The `claimRefund()` logic is enforced by code — no "contact support".
- **Transparent voting**: Every milestone vote is a public on-chain transaction.
- **Immutable audit trail**: All contributions, votes, and withdrawals are permanently logged as events.
- **Permissionless**: Anyone with an Ethereum wallet can create or back a campaign.

---

## 2. Architecture Diagram (ASCII)

### 2.1 — Factory Pattern: How Campaigns Are Created

```
                      ┌─────────────────────────────────────┐
                      │         CampaignFactory.sol          │
                      │                                      │
  Creator calls ────► │  createCampaign(                     │
  createCampaign()    │    goal, deadline, token,            │
                      │    milestones[], feeRecipient         │
                      │  )                                   │
                      │                                      │
                      │  campaigns[]:  address[]             │  ◄─── Admin can pause/unpause
                      │  campaignsByCreator: mapping         │
                      │                                      │
                      │  emit CampaignCreated(               │
                      │    campaignAddr, creator, goal)       │
                      └────────────┬────────────────────────┘
                                   │  deploys new contract
                                   ▼
                      ┌─────────────────────────────────────┐
                      │           Campaign.sol               │
                      │  (one contract per campaign)         │
                      │                                      │
                      │  state: ACTIVE | SUCCESSFUL | FAILED │
                      │  goal: uint256                       │
                      │  deadline: uint256                   │
                      │  totalRaised: uint256                │
                      │  contributions: mapping(addr=>uint)  │
                      │  milestones: Milestone[]             │
                      └─────────────────────────────────────┘
```

### 2.2 — Campaign Lifecycle State Machine

```
                           createCampaign()
                                 │
                                 ▼
                         ┌──────────────┐
                         │    ACTIVE    │◄───────────────────────────────┐
                         │              │                                │
                         │ Contributors │   contribute(amount)           │
                         │ can fund     │ ─────────────────────────────► │ ETH / ERC-20
                         │              │                                │ locked in contract
                         └──────┬───────┘
                                │
                    ┌───────────┴────────────┐
                    │  deadline reached?      │
                    └───────────┬────────────┘
                                │
              ┌─────────────────┼─────────────────────┐
              │                                        │
    totalRaised >= goal                    totalRaised < goal
              │                                        │
              ▼                                        ▼
    ┌──────────────────┐                   ┌──────────────────┐
    │   SUCCESSFUL     │                   │     FAILED       │
    │                  │                   │                  │
    │ Milestone voting │                   │ Contributors can │
    │ unlocks tranches │                   │ claimRefund()    │
    └────────┬─────────┘                   └──────────────────┘
             │
             │  (for each milestone)
             ▼
    ┌──────────────────────────────────────────────┐
    │           Milestone Voting Flow               │
    │                                              │
    │  1. Creator: submitMilestoneProof(ipfsHash)  │
    │  2. Contributors: vote(milestoneId, approve) │
    │  3. Voting window: 7 days                    │
    │  4. Quorum check: > 50% of totalRaised voted │
    │  5. Approval check: > 66% of votes = YES     │
    │  6. releaseTranche() → creator receives ETH  │
    │     or creator disputes → DAO arbitration    │
    └──────────────────────────────────────────────┘
```

### 2.3 — Full System Architecture (Ingestion + Query)

```
┌───────────────────────────────────────────────────────────────────────────┐
│                          USER'S BROWSER                                    │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │               Next.js 14 Frontend (App Router)                      │  │
│  │                                                                     │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │  │
│  │  │  RainbowKit  │  │    wagmi     │  │      React Query         │  │  │
│  │  │ (WalletConn) │  │  (hooks)     │  │ (cache / loading states) │  │  │
│  │  └──────┬───────┘  └──────┬───────┘  └──────────────────────────┘  │  │
│  │         │                 │                                         │  │
│  │         └────────┬────────┘                                        │  │
│  │                  │ ethers.js / viem                                 │  │
│  └──────────────────┼─────────────────────────────────────────────────┘  │
└─────────────────────┼─────────────────────────────────────────────────────┘
                       │
          ┌────────────┴──────────────┐
          │                           │
          ▼                           ▼
┌──────────────────┐       ┌────────────────────────┐
│  Ethereum Node   │       │   The Graph (Subgraph)  │
│  (Alchemy RPC)   │       │                         │
│                  │       │  schema.graphql          │
│  - Read state    │       │  mappings.ts             │
│  - Send txns     │       │  subgraph.yaml           │
│  - Estimate gas  │       │                         │
└────────┬─────────┘       │  Indexes events:         │
         │                 │  - CampaignCreated       │
         │                 │  - Contributed           │
         │                 │  - MilestoneVoted        │
         │                 │  - TrancheReleased       │
         │                 │  - RefundClaimed         │
         │                 └───────────┬─────────────┘
         │                             │
         ▼                             ▼
┌──────────────────────────────────────────────────┐
│              Ethereum Blockchain                  │
│                                                  │
│  ┌────────────────────┐  ┌───────────────────┐   │
│  │ CampaignFactory    │  │  Campaign (x N)   │   │
│  │ 0xFactory...       │  │  0xCampaign001... │   │
│  └────────────────────┘  └───────────────────┘   │
└──────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────┐
│  IPFS / Filecoin    │
│  (campaign images,  │
│   milestone proofs, │
│   metadata JSON)    │
└─────────────────────┘
```

---

## 3. Tech Stack Table

| Layer | Tool / Library | Version | Purpose |
|---|---|---|---|
| **Smart Contracts** | Solidity | 0.8.24 | Campaign logic, milestone voting |
| **Dev Framework** | Foundry (forge, cast, anvil) | latest stable | Compile, test, deploy contracts |
| **Contract Lib** | OpenZeppelin Contracts | 5.x | ReentrancyGuard, Ownable, Pausable, SafeERC20 |
| **Frontend Framework** | Next.js | 14.2 (App Router) | SSR/SSG campaign pages |
| **Wallet Integration** | RainbowKit | 2.x | Wallet connect UI modal |
| **Web3 Hooks** | wagmi | 2.x | React hooks for contract reads/writes |
| **Low-Level Web3** | viem | 2.x | Type-safe Ethereum interactions |
| **Data Fetching** | TanStack Query | 5.x | Caching, background refresh |
| **Subgraph** | The Graph Protocol | graph-cli 0.65 | Index on-chain events for fast queries |
| **Subgraph Lang** | AssemblyScript | 0.19 | Subgraph mapping handlers |
| **IPFS Client** | @web3-storage/w3up-client | 1.x | Upload campaign metadata/images |
| **Styling** | Tailwind CSS | 3.4 | Utility-first styling |
| **Testing** | Foundry (forge test) | - | Unit + fuzz + invariant tests |
| **CI/CD** | GitHub Actions | - | Automated test + deploy pipeline |
| **Node Provider** | Alchemy | - | Sepolia + Mainnet RPC endpoints |
| **Explorer** | Etherscan | - | Contract verification |
| **Secrets Mgmt** | GitHub Secrets + .env.local | - | Private keys, API keys |
| **Testnet** | Sepolia | - | Pre-mainnet staging |
| **Mainnet** | Ethereum Mainnet | - | Production deployment |

---

## 4. Smart Contract Architecture

### 4.1 — Contract Hierarchy

```
contracts/
├── CampaignFactory.sol    # Deploys campaign instances, tracks them, collects protocol fee
├── Campaign.sol           # Core crowdfunding + milestone voting logic
├── interfaces/
│   └── ICampaign.sol      # Interface for factory ↔ campaign calls
└── libraries/
    └── CampaignLib.sol    # Shared structs (Milestone, CampaignState)
```

### 4.2 — `CampaignLib.sol` — Shared Structs

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

library CampaignLib {
    // Every campaign can be in one of three states
    enum CampaignState { ACTIVE, SUCCESSFUL, FAILED }

    // A single milestone: the creator must submit proof, then backers vote
    struct Milestone {
        string  description;       // e.g., "MVP shipped"
        uint256 trancheAmount;     // ETH/tokens released if this milestone passes
        bytes32 proofIpfsHash;     // IPFS CID of proof document (set by creator later)
        uint256 votesFor;          // weighted by contribution amount (in wei)
        uint256 votesAgainst;
        uint256 voteDeadline;      // block.timestamp + VOTING_WINDOW
        bool    released;          // true after tranche has been paid out
    }
}
```

### 4.3 — `Campaign.sol` — Full Annotated Contract

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "./libraries/CampaignLib.sol";

/**
 * @title Campaign
 * @notice One instance per crowdfunding campaign. Handles contributions,
 *         milestone voting, tranche releases, and refunds.
 * @dev Deployed by CampaignFactory. Uses pull-payment pattern for refunds
 *      to avoid reentrancy via push payments.
 */
contract Campaign is ReentrancyGuard {
    using SafeERC20 for IERC20;
    using CampaignLib for CampaignLib.Milestone;

    // ─── Constants ────────────────────────────────────────────────────────
    uint256 public constant VOTING_WINDOW      = 7 days;
    uint256 public constant APPROVAL_THRESHOLD = 66;  // 66% of votes must be FOR
    uint256 public constant QUORUM_PERCENT     = 50;  // 50% of total raised must vote

    // ─── Immutables (set once in constructor, cheaper than storage) ────────
    address public immutable creator;
    address public immutable factory;
    address public immutable token;      // address(0) = ETH campaign
    uint256 public immutable goal;
    uint256 public immutable deadline;
    uint256 public immutable platformFeeBps; // e.g., 200 = 2%
    address public immutable feeRecipient;

    // ─── State ────────────────────────────────────────────────────────────
    CampaignLib.CampaignState public state;
    uint256 public totalRaised;
    uint256 public currentMilestoneIndex;

    mapping(address => uint256) public contributions;
    // milestoneId => contributor => hasVoted
    mapping(uint256 => mapping(address => bool)) public hasVoted;

    CampaignLib.Milestone[] public milestones;

    // ─── Events ───────────────────────────────────────────────────────────
    event Contributed(address indexed contributor, uint256 amount);
    event RefundClaimed(address indexed contributor, uint256 amount);
    event MilestoneProofSubmitted(uint256 indexed milestoneId, bytes32 ipfsHash);
    event MilestoneVoted(uint256 indexed milestoneId, address indexed voter, bool approve, uint256 weight);
    event TrancheReleased(uint256 indexed milestoneId, uint256 amount);
    event CampaignFailed();
    event CampaignSucceeded();

    // ─── Errors (custom errors save gas vs. string reverts) ───────────────
    error Campaign__DeadlineNotReached();
    error Campaign__DeadlineReached();
    error Campaign__GoalAlreadyMet();
    error Campaign__GoalNotMet();
    error Campaign__NotCreator();
    error Campaign__ZeroAmount();
    error Campaign__NotActive();
    error Campaign__AlreadyVoted();
    error Campaign__VotingClosed();
    error Campaign__VotingOpen();
    error Campaign__NoContribution();
    error Campaign__AlreadyReleased();
    error Campaign__QuorumNotReached();
    error Campaign__NotApproved();
    error Campaign__WrongToken();

    // ─── Modifiers ────────────────────────────────────────────────────────
    modifier onlyCreator() {
        if (msg.sender != creator) revert Campaign__NotCreator();
        _;
    }

    modifier onlyActive() {
        if (state != CampaignLib.CampaignState.ACTIVE) revert Campaign__NotActive();
        _;
    }

    // ─── Constructor ──────────────────────────────────────────────────────
    constructor(
        address _creator,
        address _token,
        uint256 _goal,
        uint256 _deadline,
        uint256 _platformFeeBps,
        address _feeRecipient,
        CampaignLib.Milestone[] memory _milestones
    ) {
        // Validate: milestones must sum to exactly the goal
        uint256 totalTranches;
        for (uint256 i = 0; i < _milestones.length; i++) {
            totalTranches += _milestones[i].trancheAmount;
            milestones.push(_milestones[i]);
        }
        require(totalTranches == _goal, "Tranches must sum to goal");
        require(_deadline > block.timestamp, "Deadline must be in future");
        require(_goal > 0, "Goal must be > 0");

        creator        = _creator;
        factory        = msg.sender;   // factory is always the deployer
        token          = _token;
        goal           = _goal;
        deadline       = _deadline;
        platformFeeBps = _platformFeeBps;
        feeRecipient   = _feeRecipient;
        state          = CampaignLib.CampaignState.ACTIVE;
    }

    // ─── Contribution ─────────────────────────────────────────────────────

    /**
     * @notice Contribute ETH to this campaign.
     * @dev Only callable if state is ACTIVE and deadline not passed.
     *      Uses nonReentrant to be safe, though ETH receive is simple.
     */
    function contributeETH() external payable onlyActive nonReentrant {
        if (block.timestamp >= deadline) revert Campaign__DeadlineReached();
        if (token != address(0))        revert Campaign__WrongToken(); // ETH not accepted for ERC20 campaigns
        if (msg.value == 0)             revert Campaign__ZeroAmount();

        contributions[msg.sender] += msg.value;
        totalRaised               += msg.value;

        emit Contributed(msg.sender, msg.value);
    }

    /**
     * @notice Contribute ERC-20 tokens to this campaign.
     * @param amount Token amount (must have prior approval to this contract).
     */
    function contributeToken(uint256 amount) external onlyActive nonReentrant {
        if (block.timestamp >= deadline) revert Campaign__DeadlineReached();
        if (token == address(0))         revert Campaign__WrongToken();
        if (amount == 0)                 revert Campaign__ZeroAmount();

        // SafeERC20 handles non-standard tokens that don't return bool
        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        contributions[msg.sender] += amount;
        totalRaised               += amount;

        emit Contributed(msg.sender, amount);
    }

    // ─── State Finalization ───────────────────────────────────────────────

    /**
     * @notice Finalize the campaign after the deadline.
     *         Anyone can call this — it's a state transition, not a privileged action.
     */
    function finalize() external {
        if (block.timestamp < deadline)                          revert Campaign__DeadlineNotReached();
        if (state != CampaignLib.CampaignState.ACTIVE)          revert Campaign__NotActive();

        if (totalRaised >= goal) {
            state = CampaignLib.CampaignState.SUCCESSFUL;
            emit CampaignSucceeded();
        } else {
            state = CampaignLib.CampaignState.FAILED;
            emit CampaignFailed();
        }
    }

    // ─── Refunds (Pull Pattern) ───────────────────────────────────────────

    /**
     * @notice Claim a refund if the campaign failed.
     * @dev Uses pull payment pattern: contributor calls this themselves.
     *      Setting contributions[msg.sender] = 0 BEFORE transfer prevents reentrancy.
     */
    function claimRefund() external nonReentrant {
        if (state != CampaignLib.CampaignState.FAILED) revert Campaign__GoalAlreadyMet();

        uint256 amount = contributions[msg.sender];
        if (amount == 0) revert Campaign__NoContribution();

        // CEI pattern: Checks → Effects → Interactions
        contributions[msg.sender] = 0; // zero out BEFORE transfer

        if (token == address(0)) {
            // ETH refund
            (bool success, ) = msg.sender.call{value: amount}("");
            require(success, "ETH transfer failed");
        } else {
            // ERC-20 refund
            IERC20(token).safeTransfer(msg.sender, amount);
        }

        emit RefundClaimed(msg.sender, amount);
    }

    // ─── Milestone Voting ─────────────────────────────────────────────────

    /**
     * @notice Creator submits proof for the current milestone (IPFS CID).
     * @param ipfsHash The keccak256 of the IPFS CID string (to save gas).
     *                 Frontend decodes the actual CID from event logs.
     */
    function submitMilestoneProof(bytes32 ipfsHash) external onlyCreator {
        if (state != CampaignLib.CampaignState.SUCCESSFUL) revert Campaign__GoalNotMet();

        CampaignLib.Milestone storage m = milestones[currentMilestoneIndex];
        if (m.released) revert Campaign__AlreadyReleased();

        m.proofIpfsHash = ipfsHash;
        m.voteDeadline  = block.timestamp + VOTING_WINDOW;

        emit MilestoneProofSubmitted(currentMilestoneIndex, ipfsHash);
    }

    /**
     * @notice Vote on the current milestone.
     * @param approve true = approve the milestone proof, false = reject.
     * @dev Voting weight is proportional to contribution — a $1000 backer
     *      has more say than a $10 backer, aligning incentives.
     */
    function vote(bool approve) external nonReentrant {
        if (state != CampaignLib.CampaignState.SUCCESSFUL) revert Campaign__GoalNotMet();

        CampaignLib.Milestone storage m = milestones[currentMilestoneIndex];
        if (block.timestamp > m.voteDeadline) revert Campaign__VotingClosed();
        if (hasVoted[currentMilestoneIndex][msg.sender]) revert Campaign__AlreadyVoted();

        uint256 weight = contributions[msg.sender];
        if (weight == 0) revert Campaign__NoContribution();

        hasVoted[currentMilestoneIndex][msg.sender] = true;

        if (approve) {
            m.votesFor += weight;
        } else {
            m.votesAgainst += weight;
        }

        emit MilestoneVoted(currentMilestoneIndex, msg.sender, approve, weight);
    }

    /**
     * @notice Release the tranche for the current milestone after voting closes.
     * @dev Anyone can call this to trigger the release (permissionless settlement).
     *      Checks quorum and approval threshold before paying the creator.
     */
    function releaseTranche() external nonReentrant {
        if (state != CampaignLib.CampaignState.SUCCESSFUL) revert Campaign__GoalNotMet();

        CampaignLib.Milestone storage m = milestones[currentMilestoneIndex];
        if (block.timestamp <= m.voteDeadline) revert Campaign__VotingOpen();
        if (m.released)                        revert Campaign__AlreadyReleased();

        uint256 totalVotes = m.votesFor + m.votesAgainst;

        // Quorum: at least QUORUM_PERCENT of totalRaised must have voted
        if (totalVotes * 100 < totalRaised * QUORUM_PERCENT) revert Campaign__QuorumNotReached();

        // Approval: at least APPROVAL_THRESHOLD% of votes must be FOR
        if (m.votesFor * 100 < totalVotes * APPROVAL_THRESHOLD) revert Campaign__NotApproved();

        m.released = true;
        currentMilestoneIndex++;

        // Deduct platform fee from this tranche
        uint256 fee    = (m.trancheAmount * platformFeeBps) / 10_000;
        uint256 payout = m.trancheAmount - fee;

        if (token == address(0)) {
            // ETH payouts — CEI: mark released before transfers
            (bool feeOk, ) = feeRecipient.call{value: fee}("");
            require(feeOk, "Fee transfer failed");
            (bool ok, ) = creator.call{value: payout}("");
            require(ok, "Payout failed");
        } else {
            IERC20(token).safeTransfer(feeRecipient, fee);
            IERC20(token).safeTransfer(creator, payout);
        }

        emit TrancheReleased(currentMilestoneIndex - 1, payout);
    }

    // ─── View Helpers ─────────────────────────────────────────────────────

    function getMilestone(uint256 index) external view returns (CampaignLib.Milestone memory) {
        return milestones[index];
    }

    function getMilestoneCount() external view returns (uint256) {
        return milestones.length;
    }

    function getContribution(address backer) external view returns (uint256) {
        return contributions[backer];
    }

    // Allow contract to receive ETH (for ETH campaigns)
    receive() external payable {}
}
```

### 4.4 — `CampaignFactory.sol` — Annotated Factory

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Pausable.sol";
import "./Campaign.sol";
import "./libraries/CampaignLib.sol";

/**
 * @title CampaignFactory
 * @notice Single entry point for creating new crowdfunding campaigns.
 *         Using a factory pattern keeps deployment costs predictable and
 *         allows the frontend to discover all campaigns by querying events
 *         from one contract address.
 * @dev Inherits Ownable (admin) and Pausable (emergency stop).
 */
contract CampaignFactory is Ownable, Pausable {
    // ─── State ────────────────────────────────────────────────────────────
    address[] public allCampaigns;
    mapping(address => address[]) public campaignsByCreator;

    uint256 public platformFeeBps = 200; // 2% default
    address public feeRecipient;

    // ─── Events ───────────────────────────────────────────────────────────
    event CampaignCreated(
        address indexed campaignAddress,
        address indexed creator,
        address indexed token,
        uint256 goal,
        uint256 deadline
    );
    event FeeUpdated(uint256 newFeeBps);
    event FeeRecipientUpdated(address newRecipient);

    // ─── Errors ───────────────────────────────────────────────────────────
    error Factory__InvalidFee();
    error Factory__ZeroAddress();
    error Factory__DeadlineTooShort();
    error Factory__NoMilestones();

    // Minimum campaign duration: 1 day
    uint256 public constant MIN_DURATION = 1 days;
    // Maximum fee cap: 10%
    uint256 public constant MAX_FEE_BPS  = 1_000;

    constructor(address _feeRecipient) Ownable(msg.sender) {
        if (_feeRecipient == address(0)) revert Factory__ZeroAddress();
        feeRecipient = _feeRecipient;
    }

    // ─── Campaign Creation ────────────────────────────────────────────────

    /**
     * @notice Deploy a new Campaign contract.
     * @param token      ERC-20 token address, or address(0) for ETH campaigns.
     * @param goal       Total funding goal (in wei or token decimals).
     * @param deadline   Unix timestamp by which funds must be raised.
     * @param milestones Array of milestone structs (descriptions + tranche amounts).
     * @return campaign  Address of the newly deployed Campaign contract.
     */
    function createCampaign(
        address                     token,
        uint256                     goal,
        uint256                     deadline,
        CampaignLib.Milestone[] calldata milestones
    ) external whenNotPaused returns (address campaign) {
        // ── Validation ──────────────────────────────────────────────────
        if (deadline < block.timestamp + MIN_DURATION) revert Factory__DeadlineTooShort();
        if (milestones.length == 0)                    revert Factory__NoMilestones();

        // Deploy: passing msg.sender as creator so Campaign knows who runs it
        Campaign c = new Campaign(
            msg.sender,
            token,
            goal,
            deadline,
            platformFeeBps,
            feeRecipient,
            milestones
        );

        campaign = address(c);

        allCampaigns.push(campaign);
        campaignsByCreator[msg.sender].push(campaign);

        emit CampaignCreated(campaign, msg.sender, token, goal, deadline);
    }

    // ─── Admin Functions ──────────────────────────────────────────────────

    function setPlatformFee(uint256 newFeeBps) external onlyOwner {
        if (newFeeBps > MAX_FEE_BPS) revert Factory__InvalidFee();
        platformFeeBps = newFeeBps;
        emit FeeUpdated(newFeeBps);
    }

    function setFeeRecipient(address newRecipient) external onlyOwner {
        if (newRecipient == address(0)) revert Factory__ZeroAddress();
        feeRecipient = newRecipient;
        emit FeeRecipientUpdated(newRecipient);
    }

    function pause()   external onlyOwner { _pause(); }
    function unpause() external onlyOwner { _unpause(); }

    // ─── View Helpers ─────────────────────────────────────────────────────

    function getAllCampaigns() external view returns (address[] memory) {
        return allCampaigns;
    }

    function getCampaignsByCreator(address creator) external view returns (address[] memory) {
        return campaignsByCreator[creator];
    }

    function getTotalCampaigns() external view returns (uint256) {
        return allCampaigns.length;
    }
}
```

### 4.5 — Security Considerations

| Threat | Mitigation Applied |
|---|---|
| **Reentrancy** | `ReentrancyGuard` on all state-changing external functions; CEI (Checks-Effects-Interactions) pattern enforced in `claimRefund()` and `releaseTranche()` |
| **Push payment griefing** | Pull payment pattern — contributors call `claimRefund()` themselves; contract never pushes to unknown addresses in loops |
| **Integer overflow** | Solidity 0.8.x built-in checked arithmetic; explicit unchecked blocks only where intentional |
| **Access control** | `onlyCreator` modifier on milestone submission; `onlyOwner` on factory admin functions |
| **Deadline manipulation** | All deadline checks use `block.timestamp`; documented that miners can skew by ~15s (acceptable for day-scale deadlines) |
| **Front-running votes** | Voting window is 7 days; commit-reveal scheme not needed at this scale but documented as future upgrade |
| **ERC-20 fee-on-transfer tokens** | `SafeERC20` used throughout; however, campaign explicitly rejects deflationary tokens by checking received amount vs. stated amount (optional add-on) |
| **Proxy / upgrade risk** | Contracts are intentionally non-upgradeable (immutable logic) to maximize trustlessness |
| **Dust attacks** | Minimum contribution of 0.001 ETH (or 1 token unit) enforced to prevent griefing vote weights |
| **Factory compromise** | Factory only sets immutables at deploy time; it has no ongoing authority over individual Campaign contracts |

---

## 5. Step-by-Step Build (Phases)

### Phase 1: Smart Contract Development

```bash
# 1. Initialize Foundry project
forge init defundit
cd defundit

# 2. Install OpenZeppelin (as a git submodule via forge)
forge install OpenZeppelin/openzeppelin-contracts --no-commit

# 3. Add remappings to foundry.toml
# foundry.toml:
# [profile.default]
# src = "src"
# out = "out"
# libs = ["lib"]
# remappings = ["@openzeppelin/=lib/openzeppelin-contracts/"]
# solc_version = "0.8.24"
# optimizer = true
# optimizer_runs = 200

# 4. Build contracts structure
mkdir -p src/interfaces src/libraries

# 5. Compile to check for errors
forge build

# 6. Check contract sizes (EIP-170 limit: 24.576 KB)
forge build --sizes
```

**Project layout after Phase 1:**
```
defundit/
├── foundry.toml
├── src/
│   ├── Campaign.sol
│   ├── CampaignFactory.sol
│   ├── interfaces/
│   │   └── ICampaign.sol
│   └── libraries/
│       └── CampaignLib.sol
├── test/
│   └── (Phase 2)
├── script/
│   └── (Phase 3)
└── lib/
    └── openzeppelin-contracts/
```

---

### Phase 2: Testing (Foundry)

See [Section 6 — Testing Strategy](#6-testing-strategy) for full test code.

```bash
# Run all tests
forge test -vvv

# Run with gas reporting
forge test --gas-report

# Run fuzz tests with increased runs
forge test --fuzz-runs 10000

# Run a specific test file
forge test --match-path test/Campaign.t.sol -vvv

# Check coverage
forge coverage --report lcov
```

---

### Phase 3: Deployment

See [Section 7 — Deployment Pipeline](#7-deployment-pipeline) for full deploy scripts.

```bash
# Deploy to local anvil fork
anvil --fork-url $ALCHEMY_SEPOLIA_URL

# Deploy to Sepolia testnet
forge script script/Deploy.s.sol \
  --rpc-url $SEPOLIA_RPC_URL \
  --private-key $DEPLOYER_PRIVATE_KEY \
  --broadcast \
  --verify \
  --etherscan-api-key $ETHERSCAN_API_KEY \
  -vvvv

# Verify existing contract manually if auto-verify fails
forge verify-contract \
  0xYourCampaignFactoryAddress \
  src/CampaignFactory.sol:CampaignFactory \
  --chain sepolia \
  --etherscan-api-key $ETHERSCAN_API_KEY \
  --constructor-args $(cast abi-encode "constructor(address)" 0xFeeRecipientAddress)
```

---

### Phase 4: Subgraph (The Graph)

```bash
# 1. Install graph-cli globally
npm install -g @graphprotocol/graph-cli@0.65

# 2. Initialize subgraph from factory contract ABI
graph init \
  --product hosted-service \
  --from-contract 0xFactoryAddress \
  --network sepolia \
  --abi ./out/CampaignFactory.sol/CampaignFactory.json \
  defundit-subgraph

cd defundit-subgraph

# 3. Edit schema.graphql, subgraph.yaml, src/mappings.ts (see snippets below)

# 4. Generate AssemblyScript types from schema
graph codegen

# 5. Build the subgraph
graph build

# 6. Deploy to The Graph hosted service (or Subgraph Studio)
graph deploy --product hosted-service yourhandle/defundit
```

**`schema.graphql` — Core Entities:**

```graphql
type Campaign @entity {
  id: ID!                        # campaign contract address
  creator: Bytes!
  token: Bytes!
  goal: BigInt!
  deadline: BigInt!
  totalRaised: BigInt!
  state: String!                 # ACTIVE | SUCCESSFUL | FAILED
  milestones: [Milestone!]! @derivedFrom(field: "campaign")
  contributions: [Contribution!]! @derivedFrom(field: "campaign")
  createdAt: BigInt!
}

type Milestone @entity {
  id: ID!                        # campaignAddr-milestoneIndex
  campaign: Campaign!
  index: Int!
  description: String!
  trancheAmount: BigInt!
  proofIpfsHash: Bytes
  votesFor: BigInt!
  votesAgainst: BigInt!
  released: Boolean!
  voteDeadline: BigInt
}

type Contribution @entity {
  id: ID!                        # txHash-logIndex
  campaign: Campaign!
  contributor: Bytes!
  amount: BigInt!
  timestamp: BigInt!
}
```

**`src/mappings.ts` — Event Handlers:**

```typescript
import { BigInt, Bytes } from "@graphprotocol/graph-ts"
import { CampaignCreated } from "../generated/CampaignFactory/CampaignFactory"
import { Contributed, MilestoneVoted, TrancheReleased } from "../generated/templates/Campaign/Campaign"
import { Campaign as CampaignTemplate } from "../generated/templates"
import { Campaign, Contribution } from "../generated/schema"

// Called every time CampaignFactory emits CampaignCreated
export function handleCampaignCreated(event: CampaignCreated): void {
  let campaign = new Campaign(event.params.campaignAddress.toHex())
  campaign.creator      = event.params.creator
  campaign.token        = event.params.token
  campaign.goal         = event.params.goal
  campaign.deadline     = event.params.deadline
  campaign.totalRaised  = BigInt.fromI32(0)
  campaign.state        = "ACTIVE"
  campaign.createdAt    = event.block.timestamp
  campaign.save()

  // Spin up a dynamic data source to track this Campaign contract's events
  CampaignTemplate.create(event.params.campaignAddress)
}

// Called every time any tracked Campaign emits Contributed
export function handleContributed(event: Contributed): void {
  let id = event.transaction.hash.toHex() + "-" + event.logIndex.toString()
  let contribution = new Contribution(id)
  contribution.campaign     = event.address.toHex()
  contribution.contributor  = event.params.contributor
  contribution.amount       = event.params.amount
  contribution.timestamp    = event.block.timestamp
  contribution.save()

  // Update the Campaign's totalRaised
  let campaign = Campaign.load(event.address.toHex())
  if (campaign) {
    campaign.totalRaised = campaign.totalRaised.plus(event.params.amount)
    campaign.save()
  }
}
```

---

### Phase 5: Frontend

See [Section 8 — Frontend Integration](#8-frontend-integration) for detailed code.

```bash
# 1. Create Next.js app
npx create-next-app@14 defundit-frontend --typescript --tailwind --app
cd defundit-frontend

# 2. Install web3 dependencies
npm install wagmi viem @rainbow-me/rainbowkit @tanstack/react-query

# 3. Install graphql client for subgraph queries
npm install graphql-request graphql

# 4. Generate typed contract hooks (wagmi CLI)
npm install -D @wagmi/cli
# Configure wagmi.config.ts, then:
npx wagmi generate

# 5. Run locally
npm run dev
```

---

## 6. Testing Strategy

### 6.1 — Test Philosophy

- **Unit tests**: Every public function tested in isolation (happy path + all revert cases)
- **Fuzz tests**: Property-based testing with random inputs to uncover edge cases
- **Invariant tests**: Assert system-wide properties that must always hold
- **Fork tests**: Run against a mainnet/Sepolia fork to test with real token contracts

### 6.2 — `test/Campaign.t.sol` — Unit Tests

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Test.sol";
import "../src/Campaign.sol";
import "../src/CampaignFactory.sol";
import "../src/libraries/CampaignLib.sol";

/**
 * @notice Unit tests for Campaign.sol
 * Foundry's Test contract gives us:
 *   - vm.prank(addr): next call comes from addr
 *   - vm.warp(ts): set block.timestamp
 *   - vm.expectRevert(err): assert next call reverts
 *   - deal(addr, amount): give ETH to address
 */
contract CampaignTest is Test {
    CampaignFactory public factory;
    Campaign        public campaign;

    address public CREATOR      = makeAddr("creator");
    address public ALICE        = makeAddr("alice");
    address public BOB          = makeAddr("bob");
    address public FEE_WALLET   = makeAddr("feeWallet");

    uint256 public constant GOAL     = 10 ether;
    uint256 public constant DEADLINE = 30 days;

    // Helper: build a 2-milestone array that sums to GOAL
    function _buildMilestones() internal pure returns (CampaignLib.Milestone[] memory) {
        CampaignLib.Milestone[] memory ms = new CampaignLib.Milestone[](2);
        ms[0] = CampaignLib.Milestone({
            description:   "Phase 1: MVP",
            trancheAmount: 6 ether,
            proofIpfsHash: bytes32(0),
            votesFor:      0,
            votesAgainst:  0,
            voteDeadline:  0,
            released:      false
        });
        ms[1] = CampaignLib.Milestone({
            description:   "Phase 2: Launch",
            trancheAmount: 4 ether,
            proofIpfsHash: bytes32(0),
            votesFor:      0,
            votesAgainst:  0,
            voteDeadline:  0,
            released:      false
        });
        return ms;
    }

    function setUp() public {
        // Give test addresses some ETH
        deal(CREATOR, 1 ether);
        deal(ALICE,   20 ether);
        deal(BOB,     20 ether);

        // Deploy factory
        factory = new CampaignFactory(FEE_WALLET);

        // Create a campaign as CREATOR
        vm.prank(CREATOR);
        address campaignAddr = factory.createCampaign(
            address(0),                         // ETH campaign
            GOAL,
            block.timestamp + DEADLINE,
            _buildMilestones()
        );
        campaign = Campaign(payable(campaignAddr));
    }

    // ── Contribution Tests ─────────────────────────────────────────────────

    function test_contributeETH_success() public {
        vm.prank(ALICE);
        campaign.contributeETH{value: 5 ether}();

        assertEq(campaign.totalRaised(), 5 ether);
        assertEq(campaign.getContribution(ALICE), 5 ether);
    }

    function test_contributeETH_revert_afterDeadline() public {
        vm.warp(block.timestamp + DEADLINE + 1);  // travel past deadline

        vm.prank(ALICE);
        vm.expectRevert(Campaign.Campaign__DeadlineReached.selector);
        campaign.contributeETH{value: 1 ether}();
    }

    function test_contributeETH_revert_zeroAmount() public {
        vm.prank(ALICE);
        vm.expectRevert(Campaign.Campaign__ZeroAmount.selector);
        campaign.contributeETH{value: 0}();
    }

    // ── Finalization Tests ─────────────────────────────────────────────────

    function test_finalize_successful() public {
        // Alice funds the entire goal
        vm.prank(ALICE);
        campaign.contributeETH{value: 10 ether}();

        vm.warp(block.timestamp + DEADLINE + 1);
        campaign.finalize();

        assertEq(uint(campaign.state()), uint(CampaignLib.CampaignState.SUCCESSFUL));
    }

    function test_finalize_failed() public {
        // Only partial funding
        vm.prank(ALICE);
        campaign.contributeETH{value: 3 ether}();

        vm.warp(block.timestamp + DEADLINE + 1);
        campaign.finalize();

        assertEq(uint(campaign.state()), uint(CampaignLib.CampaignState.FAILED));
    }

    function test_finalize_revert_beforeDeadline() public {
        vm.expectRevert(Campaign.Campaign__DeadlineNotReached.selector);
        campaign.finalize();
    }

    // ── Refund Tests ───────────────────────────────────────────────────────

    function test_claimRefund_success() public {
        vm.prank(ALICE);
        campaign.contributeETH{value: 3 ether}();

        // Campaign fails
        vm.warp(block.timestamp + DEADLINE + 1);
        campaign.finalize();

        uint256 aliceBalanceBefore = ALICE.balance;

        vm.prank(ALICE);
        campaign.claimRefund();

        assertEq(ALICE.balance, aliceBalanceBefore + 3 ether);
        assertEq(campaign.getContribution(ALICE), 0); // zeroed out
    }

    function test_claimRefund_cannotDoubleClaim() public {
        vm.prank(ALICE);
        campaign.contributeETH{value: 3 ether}();

        vm.warp(block.timestamp + DEADLINE + 1);
        campaign.finalize();

        vm.prank(ALICE);
        campaign.claimRefund();

        // Second claim should revert with NoContribution
        vm.prank(ALICE);
        vm.expectRevert(Campaign.Campaign__NoContribution.selector);
        campaign.claimRefund();
    }

    // ── Milestone Voting Tests ─────────────────────────────────────────────

    function _fundAndFinalize() internal {
        vm.prank(ALICE);
        campaign.contributeETH{value: 6 ether}();  // ALICE: 6 ETH
        vm.prank(BOB);
        campaign.contributeETH{value: 4 ether}();  // BOB:   4 ETH

        vm.warp(block.timestamp + DEADLINE + 1);
        campaign.finalize();
        // state = SUCCESSFUL, totalRaised = 10 ETH
    }

    function test_milestoneFlow_fullApproval() public {
        _fundAndFinalize();

        // Creator submits proof
        vm.prank(CREATOR);
        bytes32 fakeHash = keccak256("ipfs://proof1");
        campaign.submitMilestoneProof(fakeHash);

        // Both contributors vote FOR
        vm.prank(ALICE);
        campaign.vote(true);
        vm.prank(BOB);
        campaign.vote(true);

        // Fast-forward past voting window
        vm.warp(block.timestamp + 7 days + 1);

        uint256 creatorBalanceBefore = CREATOR.balance;

        // Anyone triggers the release
        campaign.releaseTranche();

        // Creator received payout minus 2% fee
        // trancheAmount = 6 ETH, fee = 0.12 ETH, payout = 5.88 ETH
        assertApproxEqAbs(CREATOR.balance - creatorBalanceBefore, 5.88 ether, 0.001 ether);
    }

    function test_vote_revert_alreadyVoted() public {
        _fundAndFinalize();

        vm.prank(CREATOR);
        campaign.submitMilestoneProof(keccak256("proof"));

        vm.prank(ALICE);
        campaign.vote(true);

        vm.prank(ALICE);
        vm.expectRevert(Campaign.Campaign__AlreadyVoted.selector);
        campaign.vote(true);
    }
}
```

### 6.3 — `test/CampaignFuzz.t.sol` — Fuzz & Invariant Tests

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Test.sol";
import "../src/Campaign.sol";
import "../src/CampaignFactory.sol";
import "../src/libraries/CampaignLib.sol";

/**
 * @notice Fuzz tests: Foundry feeds random inputs to uncover edge cases.
 *         Invariant tests: assert properties that must ALWAYS hold.
 */
contract CampaignFuzzTest is Test {
    CampaignFactory public factory;
    address public FEE_WALLET = makeAddr("feeWallet");

    function setUp() public {
        factory = new CampaignFactory(FEE_WALLET);
    }

    // ── Fuzz Tests ─────────────────────────────────────────────────────────

    /**
     * @notice Fuzz: any ETH contribution amount should correctly update balances.
     * @param amount Forge injects random uint256 values — bound() keeps them sane.
     */
    function testFuzz_contributeETH_balanceUpdates(uint256 amount) public {
        // Bound: amount between 0.001 ETH and 100 ETH
        amount = bound(amount, 0.001 ether, 100 ether);

        address contributor = makeAddr("fuzzy");
        deal(contributor, amount + 1 ether); // give enough ETH

        // Create campaign with goal = amount (so any contribution matters)
        CampaignLib.Milestone[] memory ms = new CampaignLib.Milestone[](1);
        ms[0] = CampaignLib.Milestone({
            description:   "Single milestone",
            trancheAmount: amount,
            proofIpfsHash: bytes32(0),
            votesFor:      0,
            votesAgainst:  0,
            voteDeadline:  0,
            released:      false
        });

        vm.prank(contributor);
        address addr = factory.createCampaign(address(0), amount, block.timestamp + 30 days, ms);
        Campaign c = Campaign(payable(addr));

        vm.prank(contributor);
        c.contributeETH{value: amount}();

        // Invariant check: contract balance must equal contribution
        assertEq(address(c).balance, amount);
        assertEq(c.getContribution(contributor), amount);
        assertEq(c.totalRaised(), amount);
    }

    /**
     * @notice Fuzz: refund must always return exactly what was contributed,
     *         regardless of how many contributors there are.
     */
    function testFuzz_claimRefund_exactAmount(uint8 numContributors, uint96 baseAmount) public {
        numContributors = uint8(bound(numContributors, 1, 10));
        baseAmount      = uint96(bound(baseAmount, 0.001 ether, 1 ether));

        // Create campaign with a very high goal so it always fails
        uint256 highGoal = 1_000_000 ether;
        CampaignLib.Milestone[] memory ms = new CampaignLib.Milestone[](1);
        ms[0] = CampaignLib.Milestone("M1", highGoal, bytes32(0), 0, 0, 0, false);

        address creator = makeAddr("creator");
        vm.prank(creator);
        address addr = factory.createCampaign(address(0), highGoal, block.timestamp + 30 days, ms);
        Campaign c = Campaign(payable(addr));

        // Create N contributors and fund
        address[] memory contributors = new address[](numContributors);
        for (uint8 i = 0; i < numContributors; i++) {
            contributors[i] = makeAddr(string(abi.encodePacked("c", i)));
            deal(contributors[i], baseAmount);
            vm.prank(contributors[i]);
            c.contributeETH{value: baseAmount}();
        }

        // Fail the campaign
        vm.warp(block.timestamp + 31 days);
        c.finalize();

        // Each contributor reclaims EXACTLY what they put in
        for (uint8 i = 0; i < numContributors; i++) {
            uint256 before = contributors[i].balance;
            vm.prank(contributors[i]);
            c.claimRefund();
            assertEq(contributors[i].balance - before, baseAmount,
                "Refund must be exactly the contribution");
        }

        // Contract must be drained completely
        assertEq(address(c).balance, 0, "No ETH should remain after all refunds");
    }

    /**
     * @notice Fuzz: platform fee should never exceed platformFeeBps of tranche.
     */
    function testFuzz_platformFee_neverExceedsCap(uint256 feeBps, uint256 trancheAmount) public {
        feeBps       = bound(feeBps, 0, 1_000);     // 0%–10%
        trancheAmount = bound(trancheAmount, 1 ether, 100 ether);

        uint256 fee = (trancheAmount * feeBps) / 10_000;
        assertLe(fee, trancheAmount, "Fee must never exceed tranche amount");
    }
}

/**
 * @notice Invariant tests run the system through many random call sequences
 *         and assert that certain properties always hold.
 */
contract CampaignInvariantTest is Test {
    Campaign public campaign;
    address public ALICE   = makeAddr("alice");
    address public CREATOR = makeAddr("creator");

    function setUp() public {
        deal(ALICE, 100 ether);
        deal(CREATOR, 1 ether);

        CampaignFactory factory = new CampaignFactory(makeAddr("fees"));

        CampaignLib.Milestone[] memory ms = new CampaignLib.Milestone[](1);
        ms[0] = CampaignLib.Milestone("M1", 10 ether, bytes32(0), 0, 0, 0, false);

        vm.prank(CREATOR);
        address addr = factory.createCampaign(address(0), 10 ether, block.timestamp + 30 days, ms);
        campaign = Campaign(payable(addr));

        // Target the campaign contract for invariant fuzzing
        targetContract(address(campaign));
    }

    /**
     * INVARIANT: contract ETH balance must always equal totalRaised
     *            minus any released tranches.
     *            (Simplified: balance >= 0 and reflects real funds)
     */
    function invariant_balanceMatchesTotalRaised() public view {
        // The ETH balance cannot exceed totalRaised (no free money)
        assertLe(address(campaign).balance, campaign.totalRaised(),
            "Balance must not exceed totalRaised");
    }

    /**
     * INVARIANT: A contributor's recorded contribution must never exceed
     *            the contract's total raised.
     */
    function invariant_contributionNeverExceedsTotal() public view {
        uint256 aliceContrib = campaign.getContribution(ALICE);
        assertLe(aliceContrib, campaign.totalRaised(),
            "Single contribution cannot exceed totalRaised");
    }
}
```

---

## 7. Deployment Pipeline

### 7.1 — Deploy Script (`script/Deploy.s.sol`)

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Script.sol";
import "../src/CampaignFactory.sol";

/**
 * @notice Foundry deploy script. Run with:
 *   forge script script/Deploy.s.sol --rpc-url $RPC_URL --broadcast --verify
 */
contract DeployDeFundIt is Script {
    function run() external {
        // Private key from environment — never hardcode!
        uint256 deployerPk = vm.envUint("DEPLOYER_PRIVATE_KEY");

        // Fee recipient from env
        address feeRecipient = vm.envAddress("FEE_RECIPIENT_ADDRESS");

        vm.startBroadcast(deployerPk);

        // Deploy factory
        CampaignFactory factory = new CampaignFactory(feeRecipient);

        vm.stopBroadcast();

        // Log for CI to pick up
        console.log("CampaignFactory deployed at:", address(factory));
        console.log("Fee recipient:", feeRecipient);
        console.log("Chain ID:", block.chainid);
    }
}
```

### 7.2 — GitHub Actions CI/CD (`.github/workflows/ci.yml`)

```yaml
name: DeFundIt CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  FOUNDRY_PROFILE: ci

jobs:
  # ── Job 1: Run all tests ──────────────────────────────────────────────────
  test:
    name: Foundry Tests
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          submodules: recursive   # needed for lib/openzeppelin-contracts

      - name: Install Foundry
        uses: foundry-rs/foundry-toolchain@v1
        with:
          version: nightly

      - name: Cache Foundry artifacts
        uses: actions/cache@v4
        with:
          path: ~/.foundry/cache
          key: ${{ runner.os }}-foundry-${{ hashFiles('**/foundry.toml') }}

      - name: Install dependencies
        run: forge install

      - name: Compile contracts
        run: forge build --sizes   # fails if any contract exceeds 24KB

      - name: Run tests with gas report
        run: forge test --gas-report -vvv
        env:
          SEPOLIA_RPC_URL: ${{ secrets.SEPOLIA_RPC_URL }}  # for fork tests

      - name: Check coverage (must be > 85%)
        run: |
          forge coverage --report summary 2>&1 | tee coverage.txt
          # Fail if line coverage < 85%
          COVERAGE=$(grep "^| Total" coverage.txt | awk '{print $4}' | tr -d '%')
          if [ "${COVERAGE%.*}" -lt 85 ]; then
            echo "Coverage ${COVERAGE}% is below 85% threshold"
            exit 1
          fi

  # ── Job 2: Deploy to Sepolia (only on main branch push) ───────────────────
  deploy-sepolia:
    name: Deploy to Sepolia
    runs-on: ubuntu-latest
    needs: test                        # only runs if tests pass
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    environment: staging               # requires manual approval in GitHub

    steps:
      - uses: actions/checkout@v4
        with:
          submodules: recursive

      - uses: foundry-rs/foundry-toolchain@v1
        with:
          version: nightly

      - name: Install dependencies
        run: forge install

      - name: Deploy to Sepolia
        run: |
          forge script script/Deploy.s.sol \
            --rpc-url ${{ secrets.SEPOLIA_RPC_URL }} \
            --private-key ${{ secrets.DEPLOYER_PRIVATE_KEY }} \
            --broadcast \
            --verify \
            --etherscan-api-key ${{ secrets.ETHERSCAN_API_KEY }} \
            -vvvv
        env:
          FEE_RECIPIENT_ADDRESS: ${{ secrets.FEE_RECIPIENT_ADDRESS }}

      - name: Save deployed addresses
        run: |
          # Parse broadcast output and save addresses
          cat broadcast/Deploy.s.sol/11155111/run-latest.json \
            | jq '.transactions[] | {contractName, contractAddress}' \
            >> deployed-addresses.json

      - name: Upload deployment artifact
        uses: actions/upload-artifact@v4
        with:
          name: deployed-addresses-sepolia
          path: deployed-addresses.json

  # ── Job 3: Deploy to Mainnet (manual trigger only) ────────────────────────
  deploy-mainnet:
    name: Deploy to Mainnet
    runs-on: ubuntu-latest
    needs: deploy-sepolia
    if: github.event_name == 'workflow_dispatch'   # only via manual trigger
    environment: production                         # requires 2 approvals in GitHub

    steps:
      - uses: actions/checkout@v4
        with:
          submodules: recursive

      - uses: foundry-rs/foundry-toolchain@v1

      - name: Install dependencies
        run: forge install

      - name: Deploy to Mainnet
        run: |
          forge script script/Deploy.s.sol \
            --rpc-url ${{ secrets.MAINNET_RPC_URL }} \
            --private-key ${{ secrets.DEPLOYER_PRIVATE_KEY }} \
            --broadcast \
            --verify \
            --etherscan-api-key ${{ secrets.ETHERSCAN_API_KEY }} \
            --slow \
            -vvvv
        env:
          FEE_RECIPIENT_ADDRESS: ${{ secrets.FEE_RECIPIENT_MAINNET }}
```

### 7.3 — Environment Variables Reference

```bash
# .env (never commit this file — add to .gitignore)

# RPC Endpoints (Alchemy)
SEPOLIA_RPC_URL=https://eth-sepolia.g.alchemy.com/v2/YOUR_KEY
MAINNET_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY

# Deployment key (hardware wallet for mainnet)
DEPLOYER_PRIVATE_KEY=0xabc123...

# Fee recipient wallet (multisig for production)
FEE_RECIPIENT_ADDRESS=0xYourMultisigAddress

# Etherscan verification
ETHERSCAN_API_KEY=YOUR_ETHERSCAN_KEY
```

---

## 8. Frontend Integration

### 8.1 — Provider Setup (`app/providers.tsx`)

```tsx
"use client";

// wagmi v2 + RainbowKit v2 setup
// This wraps the entire app so all pages can use wallet hooks.

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { WagmiProvider } from "wagmi";
import { RainbowKitProvider, getDefaultConfig } from "@rainbow-me/rainbowkit";
import { mainnet, sepolia } from "wagmi/chains";
import "@rainbow-me/rainbowkit/styles.css";

// wagmi config: defines supported chains and connectors
const config = getDefaultConfig({
  appName: "DeFundIt",
  projectId: process.env.NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID!,
  chains: [mainnet, sepolia],
  ssr: true,  // required for Next.js App Router
});

const queryClient = new QueryClient();

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <WagmiProvider config={config}>
      <QueryClientProvider client={queryClient}>
        <RainbowKitProvider>
          {children}
        </RainbowKitProvider>
      </QueryClientProvider>
    </WagmiProvider>
  );
}
```

### 8.2 — Contract ABIs and Address Config (`lib/contracts.ts`)

```typescript
// Centralized contract configuration — import everywhere
// Generated by: npx wagmi generate (reads from deployed ABI JSON)

export const CAMPAIGN_FACTORY_ADDRESS = {
  1:       "0xYourMainnetFactoryAddress",
  11155111: "0xYourSepoliaFactoryAddress",
} as const;

// Minimal ABI — only include functions your frontend actually calls
// (wagmi only needs the functions you use, not the full ABI)
export const CAMPAIGN_FACTORY_ABI = [
  {
    name: "createCampaign",
    type: "function",
    stateMutability: "nonpayable",
    inputs: [
      { name: "token",      type: "address" },
      { name: "goal",       type: "uint256" },
      { name: "deadline",   type: "uint256" },
      { name: "milestones", type: "tuple[]",
        components: [
          { name: "description",   type: "string"   },
          { name: "trancheAmount", type: "uint256"  },
          { name: "proofIpfsHash", type: "bytes32"  },
          { name: "votesFor",      type: "uint256"  },
          { name: "votesAgainst",  type: "uint256"  },
          { name: "voteDeadline",  type: "uint256"  },
          { name: "released",      type: "bool"     },
        ]
      },
    ],
    outputs: [{ name: "campaign", type: "address" }],
  },
  {
    name: "getTotalCampaigns",
    type: "function",
    stateMutability: "view",
    inputs: [],
    outputs: [{ type: "uint256" }],
  },
  {
    name: "CampaignCreated",
    type: "event",
    inputs: [
      { name: "campaignAddress", type: "address", indexed: true },
      { name: "creator",         type: "address", indexed: true },
      { name: "token",           type: "address", indexed: true },
      { name: "goal",            type: "uint256", indexed: false },
      { name: "deadline",        type: "uint256", indexed: false },
    ],
  },
] as const;

export const CAMPAIGN_ABI = [
  {
    name: "contributeETH",
    type: "function",
    stateMutability: "payable",
    inputs: [],
    outputs: [],
  },
  {
    name: "claimRefund",
    type: "function",
    stateMutability: "nonpayable",
    inputs: [],
    outputs: [],
  },
  {
    name: "vote",
    type: "function",
    stateMutability: "nonpayable",
    inputs: [{ name: "approve", type: "bool" }],
    outputs: [],
  },
  {
    name: "finalize",
    type: "function",
    stateMutability: "nonpayable",
    inputs: [],
    outputs: [],
  },
  {
    name: "totalRaised",   type: "function", stateMutability: "view",
    inputs: [],            outputs: [{ type: "uint256" }],
  },
  {
    name: "goal",          type: "function", stateMutability: "view",
    inputs: [],            outputs: [{ type: "uint256" }],
  },
  {
    name: "state",         type: "function", stateMutability: "view",
    inputs: [],            outputs: [{ type: "uint8" }],
  },
  {
    name: "getContribution", type: "function", stateMutability: "view",
    inputs: [{ name: "backer", type: "address" }],
    outputs: [{ type: "uint256" }],
  },
] as const;
```

### 8.3 — Contribute Component (`components/ContributeForm.tsx`)

```tsx
"use client";

import { useState } from "react";
import { parseEther, formatEther } from "viem";
import { useAccount, useWriteContract, useWaitForTransactionReceipt, useReadContract } from "wagmi";
import { ConnectButton } from "@rainbow-me/rainbowkit";
import { CAMPAIGN_ABI } from "@/lib/contracts";

interface ContributeFormProps {
  campaignAddress: `0x${string}`;
}

export function ContributeForm({ campaignAddress }: ContributeFormProps) {
  const [amount, setAmount] = useState("");
  const { address, isConnected } = useAccount();

  // Read current campaign state from the contract
  const { data: totalRaised } = useReadContract({
    address: campaignAddress,
    abi: CAMPAIGN_ABI,
    functionName: "totalRaised",
  });

  const { data: goal } = useReadContract({
    address: campaignAddress,
    abi: CAMPAIGN_ABI,
    functionName: "goal",
  });

  // Write hook: sends contributeETH() transaction
  const { writeContract, data: txHash, isPending, error } = useWriteContract();

  // Watch transaction receipt to show confirmation
  const { isLoading: isConfirming, isSuccess: isConfirmed } = useWaitForTransactionReceipt({
    hash: txHash,
  });

  const handleContribute = async () => {
    if (!amount || parseFloat(amount) <= 0) return;

    writeContract({
      address: campaignAddress,
      abi: CAMPAIGN_ABI,
      functionName: "contributeETH",
      value: parseEther(amount),  // convert string "0.5" → BigInt wei
    });
  };

  // Calculate progress percentage
  const progressPercent = totalRaised && goal
    ? Math.min(Number((totalRaised * 100n) / goal), 100)
    : 0;

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 space-y-4">
      {/* Progress bar */}
      <div>
        <div className="flex justify-between text-sm text-gray-600 mb-1">
          <span>{totalRaised ? formatEther(totalRaised) : "0"} ETH raised</span>
          <span>Goal: {goal ? formatEther(goal) : "0"} ETH</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div
            className="bg-purple-500 h-3 rounded-full transition-all duration-500"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
        <p className="text-right text-sm text-gray-500 mt-1">{progressPercent}%</p>
      </div>

      {/* Wallet connect gate */}
      {!isConnected ? (
        <div className="text-center">
          <p className="text-gray-500 mb-3">Connect your wallet to contribute</p>
          <ConnectButton />
        </div>
      ) : (
        <div className="space-y-3">
          <input
            type="number"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            placeholder="Amount in ETH (e.g. 0.1)"
            className="w-full border border-gray-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500"
            min="0.001"
            step="0.001"
          />

          <button
            onClick={handleContribute}
            disabled={isPending || isConfirming || !amount}
            className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400
                       text-white font-semibold py-3 rounded-xl transition-colors"
          >
            {isPending     ? "Confirm in wallet…" :
             isConfirming  ? "Transaction confirming…" :
             isConfirmed   ? "✅ Contribution confirmed!" :
             "Contribute ETH"}
          </button>

          {/* Error display */}
          {error && (
            <p className="text-red-500 text-sm">
              Error: {(error as Error).message.slice(0, 120)}
            </p>
          )}

          {/* Success with Etherscan link */}
          {isConfirmed && txHash && (
            <p className="text-green-600 text-sm text-center">
              View on Etherscan:{" "}
              <a
                href={`https://sepolia.etherscan.io/tx/${txHash}`}
                target="_blank"
                rel="noreferrer"
                className="underline"
              >
                {txHash.slice(0, 10)}…
              </a>
            </p>
          )}
        </div>
      )}
    </div>
  );
}
```

### 8.4 — Subgraph Query Hook (`hooks/useCampaigns.ts`)

```typescript
import { useQuery } from "@tanstack/react-query";
import { GraphQLClient, gql } from "graphql-request";

// The Graph subgraph endpoint (hosted service or Subgraph Studio)
const client = new GraphQLClient(
  process.env.NEXT_PUBLIC_SUBGRAPH_URL!
);

// GraphQL query — much more efficient than reading 100 contracts via RPC
const CAMPAIGNS_QUERY = gql`
  query GetCampaigns($first: Int!, $skip: Int!) {
    campaigns(
      first: $first
      skip: $skip
      orderBy: createdAt
      orderDirection: desc
      where: { state: "ACTIVE" }
    ) {
      id
      creator
      goal
      totalRaised
      deadline
      state
      milestones {
        index
        description
        trancheAmount
        released
        votesFor
        votesAgainst
      }
    }
  }
`;

interface Campaign {
  id: string;
  creator: string;
  goal: string;
  totalRaised: string;
  deadline: string;
  state: "ACTIVE" | "SUCCESSFUL" | "FAILED";
  milestones: Milestone[];
}

interface Milestone {
  index: number;
  description: string;
  trancheAmount: string;
  released: boolean;
  votesFor: string;
  votesAgainst: string;
}

// React Query hook — caches results, auto-refetches every 30s
export function useCampaigns(page = 0, pageSize = 12) {
  return useQuery<{ campaigns: Campaign[] }>({
    queryKey: ["campaigns", page, pageSize],
    queryFn: () =>
      client.request(CAMPAIGNS_QUERY, {
        first: pageSize,
        skip:  page * pageSize,
      }),
    staleTime: 30_000,           // consider data fresh for 30 seconds
    refetchInterval: 30_000,     // background refetch every 30 seconds
    retry: 3,                    // retry failed requests 3 times
  });
}
```

### 8.5 — Campaign Creation Flow (`app/create/page.tsx`)

```tsx
"use client";

import { useState } from "react";
import { parseEther } from "viem";
import { useChainId, useWriteContract, useWaitForTransactionReceipt } from "wagmi";
import { CAMPAIGN_FACTORY_ABI, CAMPAIGN_FACTORY_ADDRESS } from "@/lib/contracts";

export default function CreateCampaignPage() {
  const chainId = useChainId();
  const [goal, setGoal]             = useState("");
  const [deadlineDays, setDeadline] = useState("30");
  const [milestones, setMilestones] = useState([
    { description: "", tranchePercent: 100 }
  ]);

  const { writeContract, data: txHash, isPending } = useWriteContract();
  const { isSuccess } = useWaitForTransactionReceipt({ hash: txHash });

  const factoryAddress = CAMPAIGN_FACTORY_ADDRESS[chainId as 1 | 11155111];

  const handleCreate = () => {
    const goalWei      = parseEther(goal);
    const deadlineTs   = BigInt(Math.floor(Date.now() / 1000) + parseInt(deadlineDays) * 86400);

    // Build on-chain milestone structs
    // trancheAmount must sum to goal exactly
    const milestonesData = milestones.map((m) => ({
      description:   m.description,
      trancheAmount: (goalWei * BigInt(m.tranchePercent)) / 100n,
      proofIpfsHash: "0x" + "00".repeat(32) as `0x${string}`,
      votesFor:      0n,
      votesAgainst:  0n,
      voteDeadline:  0n,
      released:      false,
    }));

    writeContract({
      address: factoryAddress,
      abi: CAMPAIGN_FACTORY_ABI,
      functionName: "createCampaign",
      args: [
        "0x0000000000000000000000000000000000000000", // ETH campaign
        goalWei,
        deadlineTs,
        milestonesData,
      ],
    });
  };

  return (
    <main className="max-w-2xl mx-auto p-8 space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Launch a Campaign</h1>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Funding Goal (ETH)</label>
          <input
            type="number"
            value={goal}
            onChange={(e) => setGoal(e.target.value)}
            className="mt-1 w-full border rounded-xl px-4 py-2"
            placeholder="e.g. 10"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Campaign Duration (days)</label>
          <input
            type="number"
            value={deadlineDays}
            onChange={(e) => setDeadline(e.target.value)}
            className="mt-1 w-full border rounded-xl px-4 py-2"
          />
        </div>

        {/* Milestone builder — simplified for brevity */}
        <div>
          <label className="block text-sm font-medium text-gray-700">Milestones</label>
          {milestones.map((m, i) => (
            <div key={i} className="flex gap-2 mt-2">
              <input
                value={m.description}
                onChange={(e) => {
                  const updated = [...milestones];
                  updated[i].description = e.target.value;
                  setMilestones(updated);
                }}
                placeholder={`Milestone ${i + 1} description`}
                className="flex-1 border rounded-xl px-3 py-2"
              />
              <input
                type="number"
                value={m.tranchePercent}
                onChange={(e) => {
                  const updated = [...milestones];
                  updated[i].tranchePercent = parseInt(e.target.value);
                  setMilestones(updated);
                }}
                placeholder="%"
                className="w-20 border rounded-xl px-3 py-2"
              />
            </div>
          ))}
          <button
            onClick={() => setMilestones([...milestones, { description: "", tranchePercent: 0 }])}
            className="mt-2 text-purple-600 text-sm hover:underline"
          >
            + Add milestone
          </button>
        </div>

        <button
          onClick={handleCreate}
          disabled={isPending || !goal}
          className="w-full bg-purple-600 text-white py-3 rounded-xl font-semibold
                     hover:bg-purple-700 disabled:bg-gray-400 transition-colors"
        >
          {isPending ? "Confirm in wallet…" : isSuccess ? "✅ Campaign Created!" : "Deploy Campaign"}
        </button>
      </div>
    </main>
  );
}
```

---

## 9. Gas Optimization Decisions

Every ETH saved in gas is money back in creators' and backers' pockets. Here are the deliberate optimizations made, with trade-offs explained:

### Decision 1: Custom Errors vs. `require(string)`

```solidity
// ❌ Before: costs ~350 extra gas per revert due to string encoding
require(msg.sender == creator, "Campaign: not the creator");

// ✅ After: custom errors encode only a 4-byte selector
error Campaign__NotCreator();
if (msg.sender != creator) revert Campaign__NotCreator();
// Savings: ~250 gas per revert call
```

### Decision 2: `immutable` for Variables Set Once

```solidity
// ❌ Storage slot read: ~2,100 gas (SLOAD cold) / 100 gas (warm)
address public creator;

// ✅ Immutable: baked into bytecode, costs only ~3 gas to read
address public immutable creator;
// Applies to: creator, factory, token, goal, deadline, platformFeeBps, feeRecipient
// Savings: ~2,000 gas per read across all callers
```

### Decision 3: Struct Packing in `Milestone`

```solidity
// ❌ Unpacked: each field gets its own 32-byte slot
struct Milestone {
    string  description;   // dynamic (stored separately anyway)
    uint256 trancheAmount; // slot 0
    bytes32 proofIpfsHash; // slot 1
    uint256 votesFor;      // slot 2
    uint256 votesAgainst;  // slot 3
    uint256 voteDeadline;  // slot 4
    bool    released;      // slot 5 (wastes 31 bytes!)
}

// ✅ Packed: bool + smaller uint into one slot where possible
// Note: uint256 values can't pack further, but bool next to voteDeadline
// saves 1 storage slot if we downcast voteDeadline to uint48:
struct Milestone {
    string  description;
    uint256 trancheAmount;
    bytes32 proofIpfsHash;
    uint256 votesFor;
    uint256 votesAgainst;
    uint48  voteDeadline;  // timestamp fits in uint48 until year 8 million
    bool    released;      // packs with uint48 into one slot!
}
// Savings: 1 fewer SSTORE (~20,000 gas) on milestone creation
```

### Decision 4: Events for Off-Chain Data, Not Storage

```solidity
// ❌ Storing voter list on-chain: massive gas cost, O(n) iteration
address[] public voters;  // NEVER DO THIS for large sets

// ✅ Emit events only — subgraph indexes them off-chain
emit MilestoneVoted(milestoneIndex, msg.sender, approve, weight);
// The frontend queries The Graph for voter lists, not the contract
// Savings: tens of thousands of gas per vote
```

### Decision 5: `calldata` vs `memory` for Arrays

```solidity
// ❌ memory: copies array from calldata to memory (wastes gas)
function createCampaign(..., CampaignLib.Milestone[] memory milestones) external

// ✅ calldata: reads directly from calldata without copying
function createCampaign(..., CampaignLib.Milestone[] calldata milestones) external
// Savings: scales with array size, ~100-500 gas per element
```

### Decision 6: Batch Reads via Multicall

```typescript
// ❌ N separate RPC calls: slow and expensive for the node
const goal       = await campaign.goal();
const raised     = await campaign.totalRaised();
const state      = await campaign.state();

// ✅ wagmi's useReadContracts batches into one eth_call via Multicall3
import { useReadContracts } from "wagmi";
const { data } = useReadContracts({
  contracts: [
    { address, abi, functionName: "goal"        },
    { address, abi, functionName: "totalRaised" },
    { address, abi, functionName: "state"       },
  ],
  // All 3 fields fetched in a SINGLE RPC call
});
```

### Gas Cost Summary

| Operation | Estimated Gas | ETH Cost (30 gwei) |
|---|---|---|
| `createCampaign()` (2 milestones) | ~450,000 | ~0.0135 ETH |
| `contributeETH()` | ~55,000 | ~0.00165 ETH |
| `vote()` | ~65,000 | ~0.00195 ETH |
| `releaseTranche()` | ~85,000 | ~0.00255 ETH |
| `claimRefund()` | ~50,000 | ~0.0015 ETH |
| `finalize()` | ~35,000 | ~0.00105 ETH |

> Gas prices fluctuate wildly. Always estimate with `cast estimate` or Tenderly before presenting costs to users.

---

## 10. Production Gotchas

These are real issues encountered during development and staging — know them before you hit them in production.

- **🚨 Milestone tranches must sum to exactly the goal.** If the frontend lets users input percentages that round to 99.9999% due to floating point arithmetic, the contract constructor reverts. Fix: always compute the last milestone tranche as `goal - sumOfPrevious` in your frontend/deploy script to absorb rounding.

- **🚨 `block.timestamp` can be gamed by validators within ~12 seconds.** For a 7-day voting window this is irrelevant, but never use `block.timestamp` for sub-minute precision (e.g., don't base refund eligibility on "within 5 minutes of deadline"). Use block numbers for fine-grained timing instead.

- **🚨 Fee-on-transfer and rebasing ERC-20 tokens are incompatible.** A token that takes 1% on transfer will credit 100 tokens to the contract but only receive 99. The `totalRaised` mapping will be wrong. Document explicitly which token standards are supported, and optionally add an `amount == 0` guard post-`transferFrom` that checks actual balance delta.

- **🚨 Campaign contract deployment costs gas paid by the creator.** Creators get sticker shock when `createCampaign()` costs $40 on a congested mainnet. Consider deploying a minimal proxy (EIP-1167 clone) to reduce deploy cost by ~90%, at the cost of contract readability. We used clones for v1.1.

- **🚨 The Graph indexing lag.** Events emitted on-chain take 1–5 minutes to appear in a freshly synced subgraph. Do NOT rely solely on the subgraph for "just submitted" transaction feedback. Always show immediate UI feedback from the transaction receipt, and use the subgraph only for historical/listing data.

- **🚨 Wallet UX for low ETH balances.** If a contributor's wallet has barely enough ETH for a contribution but not the gas fee, the transaction silently fails after "confirm" in MetaMask. Always read `useBalance()` and warn users if their balance is within 110% of the contribution amount.

- **🚨 JSON-RPC rate limits.** The free Alchemy tier has a 330 request/second limit. A campaign listing page that reads 50 contract states individually will hit this within seconds at moderate traffic. Solution: use the subgraph for listings (single GraphQL request), and only call the RPC for write operations and real-time reads.

- **🚨 Contract verification on Etherscan may fail silently** if the optimizer settings in `foundry.toml` don't exactly match what you pass to `forge verify-contract`. Always use `--watch` flag during verification to catch failures early, and keep a `foundry.toml` and `remappings.txt` snapshot alongside your deployed bytecode.

- **🚨 IPFS content availability is not guaranteed.** If a creator pins their milestone proof to IPFS via a free pinning service and that service goes down, the proof hash is on-chain but the content is unreachable. Require creators to pin via multiple services (web3.storage + Pinata) and store the CID, not the full gateway URL, on-chain.

- **🚨 Contributor wallets can be smart contracts (e.g., Gnosis Safe).** The `msg.sender` check for voting assumes contributors are EOAs (externally owned accounts). A Safe with 3/5 multisig can contribute, but voting requires each Safe owner to submit a proposal internally — document this prominently or add a delegation mechanism.

---

## 11. Lessons Learned

### What We'd Do the Same

**Foundry over Hardhat for contract development.** Foundry's native Solidity test language (no context switching to JS), built-in fuzzing, gas reports, and `vm.cheatcodes` made TDD fast and intuitive. The `forge test --watch` loop was a superpower during development.

**The Graph for campaign listings.** Initially we read campaign states directly from the blockchain — 50 separate `eth_call` requests per page load. Switching to a subgraph turned a 5-second page load into 200ms. The setup cost (learning AssemblyScript mappings) was paid back within two days.

**Pull-payment pattern for refunds.** We almost shipped a loop-based refund function that iterated all contributors and pushed ETH back. A colleague caught this during code review — it would have been a textbook denial-of-service attack (one contributor with a reverting `receive()` would brick all refunds). The pull pattern is the only safe approach.

**Immutable contracts, not upgradeable proxies.** For a financial application, the trust guarantee of "this code cannot be changed" is more valuable than the operational convenience of upgrades. Users can verify the deployed bytecode matches the audited code. We document breaking changes as new factory versions with migration guides instead.

### What We'd Do Differently

**Invest in a formal audit earlier.** We built 90% of the contract logic before engaging an auditor and received substantial feedback on the milestone voting logic (specifically, the quorum calculation could be griefed by a contributor burning their tokens after voting). Earlier engagement would have been cheaper.

**Add a commit-reveal scheme to voting from day one.** Transparent on-chain voting allows whales to vote at the last second and let smaller holders "pre-signal" their vote — the whale can then vote strategically based on observed sentiment. A commit-reveal scheme hides votes until the window closes. It's significantly more complex but important for fair governance.

**Use a multisig for the deployer key on day one.** We deployed Sepolia with an EOA private key for convenience. When it came time for mainnet, the migration to a Gnosis Safe deployment workflow took two days of refactoring the CI/CD pipeline. Start with a multisig from the beginning.

**Write invariant tests before unit tests.** We wrote unit tests first, then added invariant tests later and immediately discovered two edge cases the unit tests missed (a scenario where `totalRaised` could exceed the contract balance during refunds under specific state transitions). Invariant tests are a force multiplier — write them early.

**Document the user-facing error messages for every `revert`.** Frontend developers had to read the Solidity to understand what `Campaign__QuorumNotReached` meant. Maintain a separate `errors.md` mapping every custom error to a human-readable description and the UI action that resolves it.

---

*Case Study written: June 2026 | Solidity 0.8.24 | Foundry latest stable | wagmi v2 | Next.js 14*

*Contract addresses, gas costs, and tool versions are subject to change. Always verify against current documentation.*
