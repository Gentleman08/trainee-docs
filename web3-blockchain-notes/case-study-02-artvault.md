# Case Study 2 — ArtVault: NFT Marketplace with Royalty Enforcement
> A production-grade NFT marketplace with on-chain royalties, lazy minting, and multi-chain deployment.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture Diagram](#2-architecture-diagram)
3. [Tech Stack](#3-tech-stack)
4. [Smart Contract Architecture](#4-smart-contract-architecture)
5. [Step-by-Step Build](#5-step-by-step-build)
6. [Testing Strategy](#6-testing-strategy)
7. [Deployment Pipeline](#7-deployment-pipeline)
8. [Frontend Integration](#8-frontend-integration)
9. [IPFS Pinning Strategy](#9-ipfs-pinning-strategy)
10. [Enforced Royalties Debate](#10-enforced-royalties-debate)
11. [Production Gotchas](#11-production-gotchas)
12. [Lessons Learned](#12-lessons-learned)

---

## 1. Project Overview

### What Is ArtVault?

**ArtVault** is a production-grade NFT marketplace purpose-built for digital artists who want guaranteed, automatic royalty payments on every secondary sale — forever. Unlike platforms such as OpenSea or Blur that treat royalties as optional social contracts, ArtVault enforces them at the **smart-contract layer**, making bypass economically and technically impossible within the platform ecosystem.

### Core Value Proposition

| Feature | Description |
|---|---|
| **Guaranteed Royalties** | EIP-2981 royalty info read on-chain; split executed before funds reach seller |
| **Lazy Minting** | Artists sign a voucher off-chain; NFT is minted only when first purchased (zero upfront gas) |
| **Multi-Chain** | Deployed on Ethereum mainnet, Base (L2), and Polygon for different price points |
| **Collection Support** | Artists can create collections; buyers can bid on entire collections |
| **Metadata Freezing** | IPFS CIDs are locked on-chain after reveal to prevent rug-pulls |
| **Auction Engine** | English auction with reserve price, time extensions, and anti-sniping |

### Who Uses It?

- **Artists / Creators** — mint collections with zero upfront cost, earn royalties passively
- **Collectors** — buy and bid on verified digital art with transparent provenance
- **Collection Curators** — manage curated drops with allow-lists and phased reveals
- **Secondary Traders** — list, re-list, and make offers; royalties handled automatically

### Scale Targets

- 10,000 NFTs per collection (ERC-721 standard)
- 100 concurrent auctions
- Sub-5-second frontend load via The Graph indexing
- Multi-chain with shared metadata on IPFS

---

## 2. Architecture Diagram

### System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           ArtVault Platform                             │
│                                                                         │
│  ┌───────────────┐    ┌──────────────────┐    ┌─────────────────────┐  │
│  │  Next.js 14   │    │   The Graph      │    │     IPFS / Pinata   │  │
│  │  Frontend     │◄───│   (Indexer)      │    │  (Metadata/Images)  │  │
│  │  wagmi + viem │    │  GraphQL API     │    │                     │  │
│  └──────┬────────┘    └──────────────────┘    └──────────┬──────────┘  │
│         │                                                │              │
│         │  RPC calls / tx signing                        │ IPFS CID     │
│         ▼                                                │              │
│  ┌──────────────────────────────────────────────────┐    │              │
│  │              Blockchain Layer                     │    │              │
│  │                                                   │    │              │
│  │  ┌─────────────┐   ┌──────────────┐   ┌────────┐ │    │              │
│  │  │  ArtVault   │   │  Marketplace │   │Royalty │ │    │              │
│  │  │  NFT.sol    │◄──│  .sol        │──►│Engine  │ │    │              │
│  │  │ (ERC-721 +  │   │  (List/Buy/  │   │.sol    │ │    │              │
│  │  │  EIP-2981)  │   │   Auction)   │   │        │ │    │              │
│  │  └──────┬──────┘   └──────────────┘   └────────┘ │    │              │
│  │         │                                         │    │              │
│  │         │ tokenURI → IPFS CID ────────────────────┼────┘              │
│  │         │                                         │                   │
│  │  Ethereum Mainnet / Base L2 / Polygon             │                   │
│  └──────────────────────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────────────────┘
```

### Lazy Mint Flow (Key Innovation)

```
ARTIST (off-chain)                  BUYER                    BLOCKCHAIN
─────────────────                  ──────                   ──────────
1. Upload art to IPFS
   → receives CID
   
2. Sign a "LazyMint Voucher":
   { tokenId, price,              3. Buyer selects NFT
     royaltyBps, metadataCID,        on gallery
     creator, nonce }
   (EIP-712 typed signature)
                                   4. Calls marketplace
                                      .buyLazy(voucher, sig)
                                                              5. Marketplace verifies
                                                                 EIP-712 signature
                                                                 (recovers signer ==
                                                                  creator address)
                                                              
                                                              6. Checks nonce not used
                                                                 (replay prevention)
                                                              
                                                              7. NFT.mint(buyer, tokenId,
                                                                  metadataCID)
                                                                 → NFT exists on-chain now
                                                              
                                                              8. RoyaltyEngine.split():
                                                                 → creator gets royalty%
                                                                 → platform gets fee%
                                                                 → (no seller here: first sale)
                                                              
                                                              9. Emit LazyMinted event
                                                                 → The Graph indexes it
```

### Royalty Enforcement Flow (Secondary Sale)

```
SELLER                         BUYER                       CONTRACTS
──────                         ──────                      ─────────
list(tokenId, price)
→ Marketplace.createListing()
  escrows NFT from seller
                               buy(listingId, value)
                               sends ETH/MATIC/etc.
                                                           Marketplace.buy():
                                                           ┌───────────────────┐
                                                           │ 1. Get royalty info│
                                                           │    from NFT.sol    │
                                                           │    (EIP-2981)      │
                                                           │                    │
                                                           │ 2. RoyaltyEngine   │
                                                           │    .distribute():  │
                                                           │    ├─ creator: X%  │
                                                           │    ├─ platform: Y% │
                                                           │    └─ seller: rest │
                                                           │                    │
                                                           │ 3. NFT.safeTransfer│
                                                           │    To(buyer)       │
                                                           └───────────────────┘
```

### Auction Flow

```
 Creator / Seller                  Bidders                  Blockchain
 ─────────────────                ─────────                 ──────────
 createAuction(
   tokenId,
   reservePrice,
   duration=24h,
   minBidIncrement=5%)
                                  bid(auctionId, value)
                                  ─────────────────────►   • Check value ≥ reserve
                                                           • Check increment met
                                                           • Refund prev highest bidder
                                                           • If bid in last 15 min:
                                                             extend by 15 min (anti-snipe)
                                                           • Store new highest bid

                                  (time passes...)

                                  finalizeAuction()        • Call RoyaltyEngine.distribute()
                                  ────────────────►        • Transfer NFT to winner
                                                           • Emit AuctionFinalized event
```

---

## 3. Tech Stack

### Smart Contracts

| Layer | Tool / Library | Version | Purpose |
|---|---|---|---|
| Language | Solidity | 0.8.24 | Smart contract language |
| Framework | Foundry (forge + cast) | latest | Compile, test, deploy |
| Token Standard | ERC-721 | OpenZeppelin 5.x | NFT standard |
| Royalty Standard | EIP-2981 | OpenZeppelin 5.x | On-chain royalty info |
| Signature Verification | EIP-712 | OpenZeppelin 5.x | Typed structured data signing |
| Reentrancy Guard | ReentrancyGuard | OpenZeppelin 5.x | Security |
| Upgradability | UUPS Proxy | OpenZeppelin 5.x | Marketplace upgrades |
| Access Control | Ownable + AccessControl | OpenZeppelin 5.x | Admin functions |

### Backend & Indexing

| Layer | Tool | Version | Purpose |
|---|---|---|---|
| Indexer | The Graph (Subgraph) | graph-cli 0.73 | Index events → GraphQL |
| Node | AssemblyScript | 0.27 | Subgraph mapping logic |
| IPFS Pinning | Pinata SDK | 2.x | Upload + pin metadata |
| Metadata API | Next.js API Routes | 14.x | Serve vouchers, metadata |
| Signature Backend | Node.js + ethers.js | 6.x | Generate EIP-712 vouchers |

### Frontend

| Layer | Tool | Version | Purpose |
|---|---|---|---|
| Framework | Next.js (App Router) | 14.2 | React SSR/SSG frontend |
| Wallet | wagmi + viem | wagmi 2.x / viem 2.x | Wallet connection, tx |
| Wallet UI | ConnectKit | 1.x | Polished connect modal |
| State | Zustand | 4.x | Client state management |
| Styling | Tailwind CSS | 3.x | Utility-first CSS |
| Data Fetching | TanStack Query | 5.x | Cache + async data |
| File Upload | react-dropzone | 14.x | Drag-and-drop uploads |
| Animation | Framer Motion | 11.x | NFT card animations |

### DevOps & Infrastructure

| Layer | Tool | Purpose |
|---|---|---|
| CI/CD | GitHub Actions | Lint, test, deploy |
| Multi-chain Deploy | Foundry scripts | Deterministic addresses via CREATE2 |
| Secret Management | Doppler | API keys, private keys |
| Monitoring | Tenderly | Transaction simulation, alerts |
| RPC Provider | Alchemy | Reliable multi-chain RPC |
| CDN | Vercel | Frontend hosting + edge functions |

---

## 4. Smart Contract Architecture

### 4.1 `ArtVaultNFT.sol` — ERC-721 + EIP-2981 + Lazy Mint Support

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/interfaces/IERC2981.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/cryptography/EIP712.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title ArtVaultNFT
 * @notice ERC-721 NFT contract with EIP-2981 royalties and lazy minting.
 *         Only the trusted Marketplace contract can call `lazyMint()`.
 */
contract ArtVaultNFT is
    ERC721URIStorage,
    IERC2981,
    EIP712,
    Ownable,
    ReentrancyGuard
{
    // ─── Types ───────────────────────────────────────────────────────────────

    /// @dev The signed voucher an artist creates off-chain for lazy minting.
    struct MintVoucher {
        uint256 tokenId;       // Must be unique; artist picks this
        uint256 price;         // Minimum purchase price in wei
        uint96  royaltyBps;    // Royalty in basis points (e.g. 1000 = 10%)
        address creator;       // Artist's wallet address
        string  metadataCID;   // IPFS CID for metadata JSON
        uint256 nonce;         // Prevents replay attacks
    }

    // EIP-712 typehash for MintVoucher — must match frontend signing schema exactly
    bytes32 public constant VOUCHER_TYPEHASH = keccak256(
        "MintVoucher(uint256 tokenId,uint256 price,uint96 royaltyBps,"
        "address creator,string metadataCID,uint256 nonce)"
    );

    // ─── State ───────────────────────────────────────────────────────────────

    address public marketplace;        // Only address allowed to call lazyMint()

    // Per-token royalty info (EIP-2981)
    mapping(uint256 => address) private _royaltyReceivers;
    mapping(uint256 => uint96)  private _royaltyBps;

    // Nonce tracking: creator => nonce => used?
    mapping(address => mapping(uint256 => bool)) public usedNonces;

    // Metadata freeze: tokenId => frozen?
    mapping(uint256 => bool) public metadataFrozen;

    // ─── Events ──────────────────────────────────────────────────────────────

    event LazyMinted(uint256 indexed tokenId, address indexed creator, address indexed buyer);
    event MetadataFrozen(uint256 indexed tokenId, string metadataCID);
    event MarketplaceUpdated(address indexed newMarketplace);

    // ─── Modifiers ───────────────────────────────────────────────────────────

    modifier onlyMarketplace() {
        require(msg.sender == marketplace, "NFT: caller is not marketplace");
        _;
    }

    // ─── Constructor ─────────────────────────────────────────────────────────

    constructor(address _marketplace)
        ERC721("ArtVault", "ARTV")
        EIP712("ArtVaultNFT", "1")
        Ownable(msg.sender)
    {
        marketplace = _marketplace;
    }

    // ─── Lazy Mint ───────────────────────────────────────────────────────────

    /**
     * @notice Called by Marketplace when a buyer purchases an unminted NFT.
     * @dev Verifies EIP-712 signature, checks nonce, mints, sets royalty info.
     * @param voucher   The signed MintVoucher from the artist
     * @param signature The artist's EIP-712 signature over the voucher
     * @param buyer     Address to mint the NFT to
     */
    function lazyMint(
        MintVoucher calldata voucher,
        bytes calldata signature,
        address buyer
    ) external onlyMarketplace nonReentrant {
        // 1. Reconstruct the EIP-712 digest
        bytes32 digest = _hashTypedDataV4(keccak256(abi.encode(
            VOUCHER_TYPEHASH,
            voucher.tokenId,
            voucher.price,
            voucher.royaltyBps,
            voucher.creator,
            keccak256(bytes(voucher.metadataCID)),
            voucher.nonce
        )));

        // 2. Recover signer from signature
        address signer = ECDSA.recover(digest, signature);
        require(signer == voucher.creator, "NFT: invalid signature");

        // 3. Prevent replay — each nonce can only be used once per creator
        require(!usedNonces[voucher.creator][voucher.nonce], "NFT: nonce already used");
        usedNonces[voucher.creator][voucher.nonce] = true;

        // 4. Validate royalty doesn't exceed 50% (contract-level safety cap)
        require(voucher.royaltyBps <= 5000, "NFT: royalty exceeds 50%");

        // 5. Mint to buyer and set token URI
        _safeMint(buyer, voucher.tokenId);
        _setTokenURI(voucher.tokenId, string.concat("ipfs://", voucher.metadataCID));

        // 6. Store royalty info for this token (EIP-2981)
        _royaltyReceivers[voucher.tokenId] = voucher.creator;
        _royaltyBps[voucher.tokenId]       = voucher.royaltyBps;

        emit LazyMinted(voucher.tokenId, voucher.creator, buyer);
    }

    // ─── EIP-2981 Royalty Info ────────────────────────────────────────────────

    /**
     * @notice Returns royalty payment info for a given sale price.
     *         Called by Marketplace before distributing funds.
     * @param tokenId   The NFT being sold
     * @param salePrice The sale price in the payment token's smallest unit
     * @return receiver Address that should receive royalty
     * @return royaltyAmount Amount in wei to send to receiver
     */
    function royaltyInfo(uint256 tokenId, uint256 salePrice)
        external
        view
        override
        returns (address receiver, uint256 royaltyAmount)
    {
        receiver      = _royaltyReceivers[tokenId];
        royaltyAmount = (salePrice * _royaltyBps[tokenId]) / 10_000;
    }

    // ─── Metadata Freezing ────────────────────────────────────────────────────

    /**
     * @notice Creator calls this to permanently lock the token URI.
     *         After freezing, tokenURI cannot be changed (rug-pull prevention).
     */
    function freezeMetadata(uint256 tokenId) external {
        require(ownerOf(tokenId) == msg.sender, "NFT: not token owner");
        require(!metadataFrozen[tokenId], "NFT: already frozen");
        metadataFrozen[tokenId] = true;
        emit MetadataFrozen(tokenId, tokenURI(tokenId));
        // EIP-4906: signal metadata freeze to marketplaces
        emit MetadataUpdate(tokenId);
    }

    /**
     * @dev Override to prevent URI changes after freeze.
     */
    function _setTokenURI(uint256 tokenId, string memory _tokenURI)
        internal
        override
    {
        require(!metadataFrozen[tokenId], "NFT: metadata is frozen");
        super._setTokenURI(tokenId, _tokenURI);
    }

    // ─── Supports Interface ───────────────────────────────────────────────────

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721URIStorage, IERC165)
        returns (bool)
    {
        // Advertise EIP-2981 support so marketplaces can query royalties
        return interfaceId == type(IERC2981).interfaceId
            || super.supportsInterface(interfaceId);
    }

    // ─── Admin ────────────────────────────────────────────────────────────────

    function setMarketplace(address _marketplace) external onlyOwner {
        marketplace = _marketplace;
        emit MarketplaceUpdated(_marketplace);
    }
}
```

---

### 4.2 `RoyaltyEngine.sol` — Payment Splitter

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/interfaces/IERC2981.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title RoyaltyEngine
 * @notice Reads EIP-2981 royalty info from any NFT contract and splits
 *         an incoming payment between creator, platform, and seller.
 *         All ETH flows through this contract atomically — no intermediate state.
 */
contract RoyaltyEngine is Ownable, ReentrancyGuard {

    // ─── State ───────────────────────────────────────────────────────────────

    address public platformFeeRecipient;
    uint96  public platformFeeBps;    // e.g. 200 = 2%

    // Authorized callers (only Marketplace contracts)
    mapping(address => bool) public authorizedCallers;

    // ─── Events ──────────────────────────────────────────────────────────────

    event RoyaltyPaid(
        address indexed nftContract,
        uint256 indexed tokenId,
        address indexed creator,
        uint256 royaltyAmount
    );
    event SaleDistributed(
        address indexed nftContract,
        uint256 indexed tokenId,
        address seller,
        uint256 sellerProceeds,
        uint256 platformFee,
        uint256 royaltyPaid
    );

    // ─── Constructor ─────────────────────────────────────────────────────────

    constructor(address _platformFeeRecipient, uint96 _platformFeeBps)
        Ownable(msg.sender)
    {
        require(_platformFeeBps <= 1000, "Engine: platform fee > 10%");
        platformFeeRecipient = _platformFeeRecipient;
        platformFeeBps       = _platformFeeBps;
    }

    // ─── Core: distribute() ──────────────────────────────────────────────────

    /**
     * @notice Distribute `msg.value` for a sale of `tokenId` from `nftContract`.
     *         Order of operations:
     *         1. Calculate platform fee
     *         2. Query EIP-2981 royalty (from remaining after platform fee)
     *         3. Remainder goes to seller
     *         All transfers happen atomically in this call.
     *
     * @param nftContract Address of the NFT contract (must support EIP-2981)
     * @param tokenId     The token being sold
     * @param seller      Address of the current seller
     */
    function distribute(
        address nftContract,
        uint256 tokenId,
        address seller
    ) external payable nonReentrant {
        require(authorizedCallers[msg.sender], "Engine: unauthorized caller");
        require(msg.value > 0, "Engine: no value sent");

        uint256 salePrice    = msg.value;
        uint256 remaining    = salePrice;

        // ── 1. Platform fee ──────────────────────────────────────────────────
        uint256 platformFee  = (salePrice * platformFeeBps) / 10_000;
        remaining           -= platformFee;

        // ── 2. Royalty (calculated on total sale price per EIP-2981 spec) ────
        uint256 royaltyAmount = 0;
        address royaltyReceiver;

        // supportsInterface check before calling royaltyInfo (not all NFTs have it)
        if (IERC165(nftContract).supportsInterface(type(IERC2981).interfaceId)) {
            (royaltyReceiver, royaltyAmount) = IERC2981(nftContract)
                .royaltyInfo(tokenId, salePrice);

            // Safety: royalty cannot exceed remaining after platform fee
            if (royaltyAmount > remaining) {
                royaltyAmount = remaining;
            }
            remaining -= royaltyAmount;
        }

        // ── 3. Seller proceeds ───────────────────────────────────────────────
        uint256 sellerProceeds = remaining;

        // ── 4. Execute transfers (checks-effects-interactions: state is final) ─
        // Platform fee
        if (platformFee > 0) {
            _sendEth(platformFeeRecipient, platformFee);
        }

        // Royalty to creator
        if (royaltyAmount > 0 && royaltyReceiver != address(0)) {
            _sendEth(royaltyReceiver, royaltyAmount);
            emit RoyaltyPaid(nftContract, tokenId, royaltyReceiver, royaltyAmount);
        }

        // Seller proceeds
        if (sellerProceeds > 0) {
            _sendEth(seller, sellerProceeds);
        }

        emit SaleDistributed(
            nftContract, tokenId, seller,
            sellerProceeds, platformFee, royaltyAmount
        );
    }

    // ─── Helpers ─────────────────────────────────────────────────────────────

    /**
     * @dev Safe ETH transfer using low-level call.
     *      Reverts if transfer fails (e.g., recipient is a rejecting contract).
     */
    function _sendEth(address recipient, uint256 amount) internal {
        (bool success, ) = payable(recipient).call{value: amount}("");
        require(success, "Engine: ETH transfer failed");
    }

    // ─── Admin ────────────────────────────────────────────────────────────────

    function setAuthorizedCaller(address caller, bool authorized) external onlyOwner {
        authorizedCallers[caller] = authorized;
    }

    function updatePlatformFee(address recipient, uint96 bps) external onlyOwner {
        require(bps <= 1000, "Engine: fee > 10%");
        platformFeeRecipient = recipient;
        platformFeeBps       = bps;
    }
}
```

---

### 4.3 `Marketplace.sol` — Listing, Buying, and Auction

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "./ArtVaultNFT.sol";
import "./RoyaltyEngine.sol";

/**
 * @title ArtVaultMarketplace
 * @notice Handles fixed-price listings, lazy-mint purchases, and English auctions.
 *         Royalties are automatically enforced via RoyaltyEngine on every sale.
 */
contract ArtVaultMarketplace is Ownable, ReentrancyGuard {

    // ─── Types ───────────────────────────────────────────────────────────────

    struct Listing {
        address seller;
        address nftContract;
        uint256 tokenId;
        uint256 price;          // In wei
        bool    active;
    }

    struct Auction {
        address seller;
        address nftContract;
        uint256 tokenId;
        uint256 reservePrice;
        uint256 highestBid;
        address highestBidder;
        uint256 endTime;        // Unix timestamp
        bool    finalized;
        uint256 minBidIncrementBps; // e.g. 500 = 5%
    }

    // ─── State ───────────────────────────────────────────────────────────────

    ArtVaultNFT   public nftContract;
    RoyaltyEngine public royaltyEngine;

    uint256 public nextListingId;
    uint256 public nextAuctionId;

    mapping(uint256 => Listing) public listings;
    mapping(uint256 => Auction) public auctions;

    // Auction anti-sniping: if bid comes in last N seconds, extend by N seconds
    uint256 public constant ANTI_SNIPE_WINDOW   = 15 minutes;
    uint256 public constant ANTI_SNIPE_EXTENSION = 15 minutes;

    // ─── Events ──────────────────────────────────────────────────────────────

    event Listed(uint256 indexed listingId, address indexed seller, uint256 tokenId, uint256 price);
    event Sale(uint256 indexed listingId, address indexed buyer, uint256 price);
    event LazyMintSale(uint256 indexed tokenId, address indexed buyer, uint256 price);
    event AuctionCreated(uint256 indexed auctionId, uint256 tokenId, uint256 reservePrice, uint256 endTime);
    event BidPlaced(uint256 indexed auctionId, address indexed bidder, uint256 amount);
    event AuctionFinalized(uint256 indexed auctionId, address winner, uint256 amount);
    event ListingCanceled(uint256 indexed listingId);

    // ─── Constructor ─────────────────────────────────────────────────────────

    constructor(address _nftContract, address _royaltyEngine)
        Ownable(msg.sender)
    {
        nftContract   = ArtVaultNFT(_nftContract);
        royaltyEngine = RoyaltyEngine(_royaltyEngine);
    }

    // ─── Fixed-Price Listing ─────────────────────────────────────────────────

    /**
     * @notice Seller lists an already-minted NFT at a fixed price.
     *         NFT is escrowed in this contract until sold or canceled.
     */
    function createListing(
        address _nftContract,
        uint256 tokenId,
        uint256 price
    ) external nonReentrant returns (uint256 listingId) {
        require(price > 0, "Market: price must be > 0");
        IERC721 nft = IERC721(_nftContract);
        require(nft.ownerOf(tokenId) == msg.sender, "Market: not token owner");
        require(
            nft.isApprovedForAll(msg.sender, address(this)) ||
            nft.getApproved(tokenId) == address(this),
            "Market: marketplace not approved"
        );

        listingId = nextListingId++;
        listings[listingId] = Listing({
            seller:      msg.sender,
            nftContract: _nftContract,
            tokenId:     tokenId,
            price:       price,
            active:      true
        });

        // Pull NFT into escrow
        nft.transferFrom(msg.sender, address(this), tokenId);

        emit Listed(listingId, msg.sender, tokenId, price);
    }

    /**
     * @notice Buy a fixed-price listing. Royalties auto-enforced.
     * @dev    CEI pattern: all state changes before external calls.
     *         ReentrancyGuard as belt-and-suspenders.
     */
    function buy(uint256 listingId) external payable nonReentrant {
        Listing storage listing = listings[listingId];
        require(listing.active, "Market: listing not active");
        require(msg.value >= listing.price, "Market: insufficient payment");

        // ── Checks-Effects: deactivate listing BEFORE any transfers ──────────
        listing.active = false;
        address seller = listing.seller;

        // Refund overpayment to buyer
        if (msg.value > listing.price) {
            uint256 overpay = msg.value - listing.price;
            (bool refunded, ) = payable(msg.sender).call{value: overpay}("");
            require(refunded, "Market: refund failed");
        }

        // ── Interactions: transfer NFT, then distribute payment ───────────────
        IERC721(listing.nftContract).transferFrom(
            address(this),
            msg.sender,
            listing.tokenId
        );

        // RoyaltyEngine handles: platform fee + creator royalty + seller proceeds
        royaltyEngine.distribute{value: listing.price}(
            listing.nftContract,
            listing.tokenId,
            seller
        );

        emit Sale(listingId, msg.sender, listing.price);
    }

    // ─── Lazy Mint Purchase ──────────────────────────────────────────────────

    /**
     * @notice Purchase an unminted NFT using a creator's signed voucher.
     *         The NFT is minted directly to the buyer in the same transaction.
     * @param voucher   Signed MintVoucher from the artist
     * @param signature Artist's EIP-712 signature
     */
    function buyLazy(
        ArtVaultNFT.MintVoucher calldata voucher,
        bytes calldata signature
    ) external payable nonReentrant {
        require(msg.value >= voucher.price, "Market: insufficient payment");

        // Refund overpayment
        if (msg.value > voucher.price) {
            uint256 overpay = msg.value - voucher.price;
            (bool refunded, ) = payable(msg.sender).call{value: overpay}("");
            require(refunded, "Market: refund failed");
        }

        // Mint NFT directly to buyer (ArtVaultNFT verifies signature + nonce)
        nftContract.lazyMint(voucher, signature, msg.sender);

        // On first sale, seller IS the creator (no secondary royalty needed)
        // Platform fee + creator payment distributed via RoyaltyEngine
        // creator acts as "seller" to receive remaining after platform fee
        royaltyEngine.distribute{value: voucher.price}(
            address(nftContract),
            voucher.tokenId,
            voucher.creator
        );

        emit LazyMintSale(voucher.tokenId, msg.sender, voucher.price);
    }

    // ─── Auction ─────────────────────────────────────────────────────────────

    /**
     * @notice Start an English auction for an NFT.
     * @param _nftContract    Address of NFT contract
     * @param tokenId         Token to auction
     * @param reservePrice    Minimum winning bid (in wei)
     * @param duration        Auction length in seconds
     * @param minBidIncrBps   Minimum bid increment in basis points (e.g. 500 = 5%)
     */
    function createAuction(
        address _nftContract,
        uint256 tokenId,
        uint256 reservePrice,
        uint256 duration,
        uint256 minBidIncrBps
    ) external nonReentrant returns (uint256 auctionId) {
        require(duration >= 1 hours && duration <= 7 days, "Market: invalid duration");
        require(reservePrice > 0, "Market: reserve must be > 0");

        IERC721 nft = IERC721(_nftContract);
        require(nft.ownerOf(tokenId) == msg.sender, "Market: not owner");

        auctionId = nextAuctionId++;
        auctions[auctionId] = Auction({
            seller:             msg.sender,
            nftContract:        _nftContract,
            tokenId:            tokenId,
            reservePrice:       reservePrice,
            highestBid:         0,
            highestBidder:      address(0),
            endTime:            block.timestamp + duration,
            finalized:          false,
            minBidIncrementBps: minBidIncrBps
        });

        // Pull NFT into escrow
        nft.transferFrom(msg.sender, address(this), tokenId);

        emit AuctionCreated(auctionId, tokenId, reservePrice, block.timestamp + duration);
    }

    /**
     * @notice Place a bid on an active auction.
     *         Previous highest bidder is refunded immediately.
     *         Anti-sniping: bids in last 15 minutes extend auction by 15 minutes.
     */
    function placeBid(uint256 auctionId) external payable nonReentrant {
        Auction storage auction = auctions[auctionId];
        require(block.timestamp < auction.endTime, "Market: auction ended");
        require(!auction.finalized, "Market: already finalized");
        require(msg.value >= auction.reservePrice, "Market: below reserve");

        // Check minimum increment if there's already a bid
        if (auction.highestBid > 0) {
            uint256 minBid = auction.highestBid
                + (auction.highestBid * auction.minBidIncrementBps / 10_000);
            require(msg.value >= minBid, "Market: bid increment too small");
        }

        // Refund previous highest bidder BEFORE updating state
        address prevBidder = auction.highestBidder;
        uint256 prevBid    = auction.highestBid;

        // Update state
        auction.highestBid    = msg.value;
        auction.highestBidder = msg.sender;

        // Anti-sniping: extend if bid comes in near end
        if (auction.endTime - block.timestamp < ANTI_SNIPE_WINDOW) {
            auction.endTime += ANTI_SNIPE_EXTENSION;
        }

        // Refund previous bidder
        if (prevBidder != address(0) && prevBid > 0) {
            (bool refunded, ) = payable(prevBidder).call{value: prevBid}("");
            require(refunded, "Market: refund failed");
        }

        emit BidPlaced(auctionId, msg.sender, msg.value);
    }

    /**
     * @notice Finalize an ended auction. Can be called by anyone.
     *         Distributes payment and transfers NFT to winner.
     */
    function finalizeAuction(uint256 auctionId) external nonReentrant {
        Auction storage auction = auctions[auctionId];
        require(block.timestamp >= auction.endTime, "Market: auction not ended");
        require(!auction.finalized, "Market: already finalized");

        auction.finalized = true;

        if (auction.highestBidder == address(0)) {
            // No bids: return NFT to seller
            IERC721(auction.nftContract).transferFrom(
                address(this),
                auction.seller,
                auction.tokenId
            );
            return;
        }

        // Transfer NFT to winner
        IERC721(auction.nftContract).transferFrom(
            address(this),
            auction.highestBidder,
            auction.tokenId
        );

        // Distribute payment with royalties
        royaltyEngine.distribute{value: auction.highestBid}(
            auction.nftContract,
            auction.tokenId,
            auction.seller
        );

        emit AuctionFinalized(auctionId, auction.highestBidder, auction.highestBid);
    }

    /**
     * @notice Cancel a listing (only seller, only if active).
     */
    function cancelListing(uint256 listingId) external nonReentrant {
        Listing storage listing = listings[listingId];
        require(listing.active, "Market: not active");
        require(listing.seller == msg.sender, "Market: not seller");

        listing.active = false;

        // Return NFT to seller
        IERC721(listing.nftContract).transferFrom(
            address(this),
            msg.sender,
            listing.tokenId
        );

        emit ListingCanceled(listingId);
    }
}
```

---

### 4.4 Security Notes

| Attack Vector | Mitigation |
|---|---|
| **Reentrancy on `buy()`** | `ReentrancyGuard` + CEI pattern (state set inactive before transfers) |
| **Signature Replay (Lazy Mint)** | Per-creator nonce mapping; nonce marked used before mint |
| **Cross-chain Replay** | EIP-712 domain includes `chainId` — signature invalid on other chains |
| **Auction Sniping** | 15-minute extension window when bid placed near end |
| **Royalty Bypass** | Engine reads live `royaltyInfo()` on every sale — no off-chain trust |
| **Overpayment Drain** | Excess ETH refunded immediately in `buy()` and `buyLazy()` |
| **Fake NFT Contracts** | `supportsInterface(IERC2981)` checked before reading royalty info |
| **Admin Key Compromise** | Multisig (Gnosis Safe) as owner; `setMarketplace` is time-locked |

---

## 5. Step-by-Step Build

### Phase 1: Environment Setup (Day 1–2)

```bash
# Install Foundry
curl -L https://foundry.paradigm.xyz | bash
foundryup

# Init project
mkdir artvault && cd artvault
forge init --no-git

# Install OpenZeppelin v5
forge install OpenZeppelin/openzeppelin-contracts@v5.0.2 --no-git

# Project structure
artvault/
├── src/
│   ├── ArtVaultNFT.sol
│   ├── Marketplace.sol
│   └── RoyaltyEngine.sol
├── test/
│   ├── unit/
│   ├── invariant/
│   └── integration/
├── script/
│   ├── Deploy.s.sol
│   └── DeployMultiChain.s.sol
├── frontend/           # Next.js app
├── subgraph/           # The Graph subgraph
└── foundry.toml
```

**`foundry.toml` configuration:**

```toml
[profile.default]
src     = "src"
out     = "out"
libs    = ["lib"]
solc    = "0.8.24"
optimizer        = true
optimizer_runs   = 200
via_ir           = false    # enable for complex contracts if needed

# Use Alchemy for fork tests
[rpc_endpoints]
mainnet = "${ALCHEMY_MAINNET_URL}"
base    = "${ALCHEMY_BASE_URL}"
polygon = "${ALCHEMY_POLYGON_URL}"

[etherscan]
mainnet = { key = "${ETHERSCAN_API_KEY}" }
base    = { key = "${BASESCAN_API_KEY}", url = "https://api.basescan.org/api" }
polygon = { key = "${POLYGONSCAN_API_KEY}", url = "https://api.polygonscan.com/api" }
```

---

### Phase 2: Core Smart Contracts (Day 3–7)

Write `ArtVaultNFT.sol`, `RoyaltyEngine.sol`, `Marketplace.sol` as shown in Section 4. Key implementation decisions:

- **EIP-712 domain name versioning**: Use `"1"` as version, bump to `"2"` if contract logic changes (invalidates all outstanding vouchers — communicate to users)
- **Pull vs push payments**: RoyaltyEngine uses push (calls `.call{value:}()`) — acceptable since recipients are EOAs or simple wallets. For complex recipient contracts, use a pull-payment pattern instead.
- **Nonce design**: Per-creator nonces allow creators to invalidate vouchers by burning a nonce range without affecting others.

---

### Phase 3: The Graph Subgraph (Day 8–10)

```bash
npm install -g @graphprotocol/graph-cli
graph init --product hosted-service artvault/artvault-mainnet
```

**`schema.graphql`:**

```graphql
type NFT @entity {
  id: ID!                    # "{nftContract}-{tokenId}"
  tokenId: BigInt!
  creator: Bytes!
  owner: Bytes!
  metadataCID: String!
  royaltyBps: Int!
  frozen: Boolean!
  listings: [Listing!]! @derivedFrom(field: "nft")
  auctions: [Auction!]! @derivedFrom(field: "nft")
  createdAt: BigInt!
}

type Listing @entity {
  id: ID!
  nft: NFT!
  seller: Bytes!
  price: BigInt!
  active: Boolean!
  soldAt: BigInt
  buyer: Bytes
  createdAt: BigInt!
}

type Auction @entity {
  id: ID!
  nft: NFT!
  seller: Bytes!
  reservePrice: BigInt!
  highestBid: BigInt!
  highestBidder: Bytes
  endTime: BigInt!
  finalized: Boolean!
  winner: Bytes
  createdAt: BigInt!
}

type RoyaltyPayment @entity {
  id: ID!
  nft: NFT!
  creator: Bytes!
  amount: BigInt!
  blockTimestamp: BigInt!
  txHash: Bytes!
}
```

**`src/marketplace.ts` (AssemblyScript mapping):**

```typescript
import { LazyMinted, Sale, AuctionFinalized } from "../generated/Marketplace/Marketplace"
import { NFT, Listing, RoyaltyPayment } from "../generated/schema"
import { BigInt, Bytes } from "@graphprotocol/graph-ts"

// Handle lazy mint event — create NFT entity from on-chain data
export function handleLazyMinted(event: LazyMinted): void {
  let id = event.address.toHex() + "-" + event.params.tokenId.toString()
  let nft = new NFT(id)
  nft.tokenId    = event.params.tokenId
  nft.creator    = event.params.creator
  nft.owner      = event.params.buyer
  nft.metadataCID = ""  // fetched via tokenURI call or separate event
  nft.royaltyBps = 0    // fetched from contract call
  nft.frozen     = false
  nft.createdAt  = event.block.timestamp
  nft.save()
}

// Handle fixed-price sale — update listing, record royalty payment
export function handleSale(event: Sale): void {
  let listing = Listing.load(event.params.listingId.toString())
  if (listing == null) return

  listing.active  = false
  listing.buyer   = event.params.buyer
  listing.soldAt  = event.block.timestamp
  listing.save()

  // Update NFT owner
  let nft = NFT.load(listing.nft)
  if (nft != null) {
    nft.owner = event.params.buyer
    nft.save()
  }
}
```

---

### Phase 4: Frontend (Day 11–18)

```bash
cd frontend
npx create-next-app@14 . --typescript --tailwind --app
npm install wagmi viem @tanstack/react-query connectkit zustand
```

---

### Phase 5: IPFS Integration (Day 15–18, parallel)

See Section 9 for detailed IPFS strategy.

---

### Phase 6: Testing (Day 19–23)

See Section 6 for comprehensive testing.

---

### Phase 7: Audit Preparation & Deployment (Day 24–30)

- Slither static analysis
- Manual review of all ETH transfer paths
- Testnet deployment (Sepolia, Base Sepolia, Mumbai)
- Community testnet period (1–2 weeks)
- Mainnet deployment with multisig

---

## 6. Testing Strategy

### Foundry Test Structure

```
test/
├── unit/
│   ├── ArtVaultNFT.t.sol       # Unit tests for NFT contract
│   ├── RoyaltyEngine.t.sol     # Payment split math
│   └── Marketplace.t.sol       # Listing, buying, auction logic
├── invariant/
│   └── MarketplaceInvariant.t.sol  # Property-based tests
└── integration/
    └── FullFlow.t.sol          # End-to-end flows across all 3 contracts
```

### Unit Tests — `Marketplace.t.sol`

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Test.sol";
import "../src/ArtVaultNFT.sol";
import "../src/RoyaltyEngine.sol";
import "../src/Marketplace.sol";

contract MarketplaceTest is Test {
    ArtVaultNFT   nft;
    RoyaltyEngine engine;
    Marketplace   market;

    // Test actors
    address platform = makeAddr("platform");
    address creator  = makeAddr("creator");
    address seller   = makeAddr("seller");
    address buyer    = makeAddr("buyer");

    // EIP-712 signing key for creator (for lazy mint tests)
    uint256 creatorPk;

    function setUp() public {
        // Deploy in dependency order
        market  = new Marketplace(address(0), address(0)); // temp
        engine  = new RoyaltyEngine(platform, 200);        // 2% platform fee
        nft     = new ArtVaultNFT(address(market));

        // Update marketplace with real addresses
        market  = new Marketplace(address(nft), address(engine));
        engine.setAuthorizedCaller(address(market), true);

        // Fund actors
        vm.deal(buyer, 100 ether);
        vm.deal(seller, 10 ether);

        // Creator key for signing lazy mint vouchers
        creatorPk = 0xBEEF;
        creator   = vm.addr(creatorPk);
    }

    // ─── Listing Tests ────────────────────────────────────────────────────────

    function test_CreateListing_Success() public {
        // Mint NFT to seller directly (simulating already-minted)
        _mintNFTToSeller(1);

        vm.startPrank(seller);
        nft.approve(address(market), 1);
        uint256 listingId = market.createListing(address(nft), 1, 1 ether);
        vm.stopPrank();

        (address lSeller,, uint256 tokenId, uint256 price, bool active) = market.listings(listingId);
        assertEq(lSeller, seller);
        assertEq(tokenId, 1);
        assertEq(price, 1 ether);
        assertTrue(active);
        // NFT should be in escrow
        assertEq(nft.ownerOf(1), address(market));
    }

    function test_Buy_DistributesRoyaltiesCorrectly() public {
        _mintNFTToSeller(1);

        vm.startPrank(seller);
        nft.approve(address(market), 1);
        uint256 listingId = market.createListing(address(nft), 1, 1 ether);
        vm.stopPrank();

        uint256 platformBefore = platform.balance;
        uint256 creatorBefore  = creator.balance;
        uint256 sellerBefore   = seller.balance;

        vm.prank(buyer);
        market.buy{value: 1 ether}(listingId);

        // Platform: 2% of 1 ETH = 0.02 ETH
        assertEq(platform.balance - platformBefore, 0.02 ether, "Platform fee wrong");
        // Royalty: 10% of 1 ETH = 0.1 ETH (set in _mintNFTToSeller)
        assertEq(creator.balance - creatorBefore, 0.1 ether, "Royalty wrong");
        // Seller: 100% - 2% - 10% = 88% = 0.88 ETH
        assertEq(seller.balance - sellerBefore, 0.88 ether, "Seller proceeds wrong");
        // Buyer owns NFT
        assertEq(nft.ownerOf(1), buyer);
    }

    function test_Buy_RevertsIf_InsufficientPayment() public {
        _mintNFTToSeller(1);

        vm.startPrank(seller);
        nft.approve(address(market), 1);
        uint256 listingId = market.createListing(address(nft), 1, 1 ether);
        vm.stopPrank();

        vm.prank(buyer);
        vm.expectRevert("Market: insufficient payment");
        market.buy{value: 0.5 ether}(listingId);
    }

    function test_Buy_RefundsOverpayment() public {
        _mintNFTToSeller(1);

        vm.startPrank(seller);
        nft.approve(address(market), 1);
        uint256 listingId = market.createListing(address(nft), 1, 1 ether);
        vm.stopPrank();

        uint256 buyerBefore = buyer.balance;

        vm.prank(buyer);
        market.buy{value: 2 ether}(listingId); // overpay by 1 ETH

        // Buyer paid 1 ETH (price) + got 1 ETH back. Net: -1 ETH spent on NFT
        assertApproxEqAbs(buyerBefore - buyer.balance, 1 ether, 0.001 ether);
    }

    // ─── Lazy Mint Tests ─────────────────────────────────────────────────────

    function test_BuyLazy_MintsNFT_ToCorrectBuyer() public {
        ArtVaultNFT.MintVoucher memory voucher = ArtVaultNFT.MintVoucher({
            tokenId:     42,
            price:       0.5 ether,
            royaltyBps:  1000,    // 10%
            creator:     creator,
            metadataCID: "QmTestCID123",
            nonce:       0
        });

        bytes memory sig = _signVoucher(voucher, creatorPk);

        vm.prank(buyer);
        market.buyLazy{value: 0.5 ether}(voucher, sig);

        // NFT minted directly to buyer
        assertEq(nft.ownerOf(42), buyer);
    }

    function test_BuyLazy_RejectsReplayedSignature() public {
        ArtVaultNFT.MintVoucher memory voucher = ArtVaultNFT.MintVoucher({
            tokenId:     42,
            price:       0.5 ether,
            royaltyBps:  1000,
            creator:     creator,
            metadataCID: "QmTestCID123",
            nonce:       0
        });

        bytes memory sig = _signVoucher(voucher, creatorPk);

        vm.prank(buyer);
        market.buyLazy{value: 0.5 ether}(voucher, sig);

        // Second attempt with same voucher must fail
        address buyer2 = makeAddr("buyer2");
        vm.deal(buyer2, 10 ether);
        vm.prank(buyer2);
        vm.expectRevert("NFT: nonce already used");
        market.buyLazy{value: 0.5 ether}(voucher, sig);
    }

    // ─── Auction Tests ────────────────────────────────────────────────────────

    function test_Auction_AntiSnipe_ExtendsEndTime() public {
        _mintNFTToSeller(1);

        vm.startPrank(seller);
        nft.approve(address(market), 1);
        uint256 auctionId = market.createAuction(address(nft), 1, 0.1 ether, 1 hours, 500);
        vm.stopPrank();

        // Warp to 10 minutes before end (within anti-snipe window)
        (, , , , , , uint256 originalEnd, , ) = market.auctions(auctionId);
        vm.warp(originalEnd - 10 minutes);

        vm.prank(buyer);
        market.placeBid{value: 0.1 ether}(auctionId);

        (, , , , , , uint256 newEnd, , ) = market.auctions(auctionId);
        // End time should have been extended by 15 minutes
        assertGt(newEnd, originalEnd, "End time not extended");
    }

    // ─── Helpers ─────────────────────────────────────────────────────────────

    function _mintNFTToSeller(uint256 tokenId) internal {
        // Direct mint bypassing marketplace for setup purposes
        // In real tests, use vm.prank with owner
        vm.prank(address(market));
        nft.lazyMint(
            ArtVaultNFT.MintVoucher({
                tokenId:     tokenId,
                price:       1 ether,
                royaltyBps:  1000,   // 10% royalty
                creator:     creator,
                metadataCID: "QmSetupCID",
                nonce:       tokenId  // unique nonce per token for setup
            }),
            _signVoucherAsCreator(tokenId),
            seller   // mint to seller for resale tests
        );
    }

    function _signVoucher(
        ArtVaultNFT.MintVoucher memory voucher,
        uint256 privateKey
    ) internal view returns (bytes memory) {
        bytes32 domainSeparator = nft.DOMAIN_SEPARATOR();
        bytes32 structHash = keccak256(abi.encode(
            nft.VOUCHER_TYPEHASH(),
            voucher.tokenId,
            voucher.price,
            voucher.royaltyBps,
            voucher.creator,
            keccak256(bytes(voucher.metadataCID)),
            voucher.nonce
        ));
        bytes32 digest = keccak256(abi.encodePacked("\x19\x01", domainSeparator, structHash));
        (uint8 v, bytes32 r, bytes32 s) = vm.sign(privateKey, digest);
        return abi.encodePacked(r, s, v);
    }

    function _signVoucherAsCreator(uint256 tokenId) internal view returns (bytes memory) {
        return _signVoucher(
            ArtVaultNFT.MintVoucher({
                tokenId:     tokenId,
                price:       1 ether,
                royaltyBps:  1000,
                creator:     creator,
                metadataCID: "QmSetupCID",
                nonce:       tokenId
            }),
            creatorPk
        );
    }
}
```

### Invariant Tests — `MarketplaceInvariant.t.sol`

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Test.sol";
import "../src/Marketplace.sol";

/**
 * @notice Invariant tests — properties that must ALWAYS hold
 *         regardless of what sequence of calls is made.
 *         Foundry fuzzes call sequences to find violations.
 */
contract MarketplaceInvariantTest is Test {
    Marketplace market;

    function setUp() public {
        // ... deploy contracts ...
        // Target the marketplace for fuzzing
        targetContract(address(market));
    }

    /// @notice The marketplace contract should never accumulate ETH.
    ///         All ETH received must be forwarded in the same transaction.
    function invariant_marketplaceHoldsNoETH() public {
        assertEq(address(market).balance, 0, "Marketplace accumulated ETH");
    }

    /// @notice Once a listing is marked inactive, it should stay inactive.
    function invariant_inactiveListingStaysInactive() public {
        // Check a known listing ID that was deactivated
        // Foundry tracks state across fuzz runs
        for (uint256 i = 0; i < market.nextListingId(); i++) {
            (, , , , bool active) = market.listings(i);
            // If we've seen it inactive, it must remain inactive
            // (Ghost variable tracking in a full implementation)
        }
    }
}
```

### Integration Test — Fork Test Against Real Chains

```solidity
// Test against real Ethereum state using a fork
contract ForkIntegrationTest is Test {
    // Real WETH on mainnet
    address constant WETH = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;

    function setUp() public {
        // Fork Ethereum mainnet at latest block
        vm.createSelectFork(vm.envString("ALCHEMY_MAINNET_URL"));
    }

    function test_InteractsWithRealERC721() public {
        // Test that our RoyaltyEngine correctly handles real NFTs
        // that do NOT implement EIP-2981 (graceful fallback)
        // ...
    }
}
```

**Run tests:**

```bash
# Unit + integration tests
forge test -vvv

# Invariant tests (10,000 runs)
forge test --match-contract Invariant --fuzz-runs 10000

# Gas snapshots (track optimization regressions)
forge snapshot

# Coverage report
forge coverage --report lcov
genhtml lcov.info --output-directory coverage-report
```

---

## 7. Deployment Pipeline

### Multi-Chain Deployment Strategy

ArtVault targets three chains for different user segments:

| Chain | Target Users | Avg Gas Cost (buy) | Token |
|---|---|---|---|
| **Ethereum Mainnet** | High-value drops, 1/1 art | ~$15–50 | ETH |
| **Base L2** | Mid-market, generative | ~$0.10–0.50 | ETH |
| **Polygon PoS** | Accessible entry-level | ~$0.01–0.05 | MATIC |

### Deterministic Addresses via CREATE2

Use `CREATE2` to get **the same contract address on all chains** — critical for cross-chain NFT provenance verification.

**`script/Deploy.s.sol`:**

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Script.sol";
import "../src/ArtVaultNFT.sol";
import "../src/RoyaltyEngine.sol";
import "../src/Marketplace.sol";

contract DeployArtVault is Script {
    // Deterministic salt — same across all chains for CREATE2
    bytes32 constant SALT = keccak256("artvault.v1.production.2024");

    function run() external {
        uint256 deployerPk = vm.envUint("DEPLOYER_PRIVATE_KEY");
        address platform   = vm.envAddress("PLATFORM_FEE_RECIPIENT");

        vm.startBroadcast(deployerPk);

        // 1. Deploy RoyaltyEngine first (no deps)
        RoyaltyEngine engine = new RoyaltyEngine{salt: SALT}(platform, 200); // 2% fee

        // 2. Deploy Marketplace (needs engine address; NFT address set after)
        // Use a placeholder, update after NFT deploy
        Marketplace market = new Marketplace{salt: SALT}(address(0), address(engine));

        // 3. Deploy NFT with marketplace address
        ArtVaultNFT nftContract = new ArtVaultNFT{salt: SALT}(address(market));

        // 4. Wire up: update marketplace's NFT reference
        //    (Marketplace.setNFTContract() — add this function for deploy)
        // market.setNFTContract(address(nftContract));

        // 5. Authorize marketplace in engine
        engine.setAuthorizedCaller(address(market), true);

        vm.stopBroadcast();

        // Log addresses for verification
        console.log("Chain ID:      ", block.chainid);
        console.log("RoyaltyEngine: ", address(engine));
        console.log("Marketplace:   ", address(market));
        console.log("ArtVaultNFT:   ", address(nftContract));
    }
}
```

**`script/DeployMultiChain.sh`:**

```bash
#!/bin/bash
set -e

# Load secrets via Doppler
export $(doppler secrets download --no-file --format env)

echo "══════════════════════════════════════════"
echo "Deploying ArtVault to all chains"
echo "══════════════════════════════════════════"

# ── Ethereum Mainnet ──────────────────────────
echo "→ Deploying to Ethereum Mainnet..."
forge script script/Deploy.s.sol \
  --rpc-url $ALCHEMY_MAINNET_URL \
  --broadcast \
  --verify \
  --etherscan-api-key $ETHERSCAN_API_KEY \
  -vvvv

# ── Base L2 ───────────────────────────────────
echo "→ Deploying to Base..."
forge script script/Deploy.s.sol \
  --rpc-url $ALCHEMY_BASE_URL \
  --broadcast \
  --verify \
  --verifier-url https://api.basescan.org/api \
  --etherscan-api-key $BASESCAN_API_KEY \
  -vvvv

# ── Polygon ───────────────────────────────────
echo "→ Deploying to Polygon..."
forge script script/Deploy.s.sol \
  --rpc-url $ALCHEMY_POLYGON_URL \
  --broadcast \
  --verify \
  --verifier-url https://api.polygonscan.com/api \
  --etherscan-api-key $POLYGONSCAN_API_KEY \
  -vvvv

echo "✓ All chains deployed successfully"
```

### GitHub Actions CI/CD

**`.github/workflows/ci.yml`:**

```yaml
name: ArtVault CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    name: Foundry Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: recursive

      - name: Install Foundry
        uses: foundry-rs/foundry-toolchain@v1
        with:
          version: nightly

      - name: Run forge build
        run: forge build --sizes

      - name: Run forge test
        run: forge test -vvv
        env:
          ALCHEMY_MAINNET_URL: ${{ secrets.ALCHEMY_MAINNET_URL }}

      - name: Run invariant tests
        run: forge test --match-contract Invariant --fuzz-runs 5000

      - name: Check gas snapshots
        run: forge snapshot --check  # Fails if gas increases unexpectedly

      - name: Slither static analysis
        uses: crytic/slither-action@v0.3.0
        with:
          target: src/
          slither-args: '--exclude naming-convention,solc-version'

  deploy-testnet:
    name: Deploy to Testnets
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: recursive

      - name: Install Foundry
        uses: foundry-rs/foundry-toolchain@v1

      - name: Deploy to Sepolia
        run: |
          forge script script/Deploy.s.sol \
            --rpc-url ${{ secrets.ALCHEMY_SEPOLIA_URL }} \
            --broadcast \
            --verify \
            --etherscan-api-key ${{ secrets.ETHERSCAN_API_KEY }}

      - name: Deploy to Base Sepolia
        run: |
          forge script script/Deploy.s.sol \
            --rpc-url ${{ secrets.ALCHEMY_BASE_SEPOLIA_URL }} \
            --broadcast \
            --verify \
            --verifier-url https://api-sepolia.basescan.org/api \
            --etherscan-api-key ${{ secrets.BASESCAN_API_KEY }}
```

---

## 8. Frontend Integration

### Wallet Setup — `wagmi.config.ts`

```typescript
// frontend/src/lib/wagmi.ts
import { createConfig, http } from "wagmi";
import { mainnet, base, polygon } from "wagmi/chains";
import { getDefaultConfig } from "connectkit";

export const wagmiConfig = createConfig(
  getDefaultConfig({
    // Supported chains — matches our deployment
    chains: [mainnet, base, polygon],
    transports: {
      [mainnet.id]: http(process.env.NEXT_PUBLIC_ALCHEMY_MAINNET_URL!),
      [base.id]:    http(process.env.NEXT_PUBLIC_ALCHEMY_BASE_URL!),
      [polygon.id]: http(process.env.NEXT_PUBLIC_ALCHEMY_POLYGON_URL!),
    },
    walletConnectProjectId: process.env.NEXT_PUBLIC_WALLETCONNECT_ID!,
    appName:  "ArtVault",
    appDescription: "NFT marketplace with enforced royalties",
  })
);
```

### Lazy Mint — Signing a Voucher (Artist Flow)

```typescript
// frontend/src/hooks/useLazyMintVoucher.ts
import { useSignTypedData, useAccount } from "wagmi";
import { type Address } from "viem";

// EIP-712 domain — must match ArtVaultNFT.sol constructor args exactly
const DOMAIN = {
  name:              "ArtVaultNFT",
  version:           "1",
  chainId:           8453,           // Base chain ID
  verifyingContract: "0xYourNFTContractAddress" as Address,
} as const;

// EIP-712 types — must match VOUCHER_TYPEHASH in Solidity exactly
const TYPES = {
  MintVoucher: [
    { name: "tokenId",     type: "uint256" },
    { name: "price",       type: "uint256" },
    { name: "royaltyBps",  type: "uint96"  },
    { name: "creator",     type: "address" },
    { name: "metadataCID", type: "string"  },
    { name: "nonce",       type: "uint256" },
  ],
} as const;

export interface MintVoucher {
  tokenId:     bigint;
  price:       bigint;
  royaltyBps:  number;
  creator:     Address;
  metadataCID: string;
  nonce:       bigint;
}

/**
 * Hook: artist signs a MintVoucher off-chain.
 * The resulting signature + voucher is stored in your DB
 * and displayed in the gallery for buyers to purchase.
 */
export function useLazyMintVoucher() {
  const { address } = useAccount();
  const { signTypedDataAsync } = useSignTypedData();

  const createVoucher = async (params: {
    tokenId:     bigint;
    price:       bigint;    // in wei
    royaltyBps:  number;    // e.g. 1000 for 10%
    metadataCID: string;    // IPFS CID
    nonce:       bigint;
  }): Promise<{ voucher: MintVoucher; signature: `0x${string}` }> => {
    if (!address) throw new Error("Wallet not connected");

    const voucher: MintVoucher = {
      ...params,
      creator: address,
    };

    // This opens the user's wallet for signing (no gas required)
    const signature = await signTypedDataAsync({
      domain: DOMAIN,
      types:  TYPES,
      primaryType: "MintVoucher",
      message: voucher,
    });

    return { voucher, signature };
  };

  return { createVoucher };
}
```

### Buy NFT Hook — Buyer Flow

```typescript
// frontend/src/hooks/useBuyNFT.ts
import { useWriteContract, useWaitForTransactionReceipt } from "wagmi";
import { parseEther } from "viem";
import { MARKETPLACE_ABI } from "@/abis/marketplace";
import { MARKETPLACE_ADDRESS } from "@/constants/contracts";

export function useBuyNFT() {
  const { writeContractAsync, data: txHash, isPending } = useWriteContract();
  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash: txHash,
  });

  /**
   * Purchase a fixed-price listing
   */
  const buyListing = async (listingId: bigint, priceWei: bigint) => {
    return writeContractAsync({
      address: MARKETPLACE_ADDRESS,
      abi:     MARKETPLACE_ABI,
      functionName: "buy",
      args:    [listingId],
      value:   priceWei,  // ETH sent with transaction
    });
  };

  /**
   * Purchase a lazy-mint NFT (first sale, NFT minted in tx)
   */
  const buyLazy = async (
    voucher: {
      tokenId:     bigint;
      price:       bigint;
      royaltyBps:  number;
      creator:     `0x${string}`;
      metadataCID: string;
      nonce:       bigint;
    },
    signature: `0x${string}`
  ) => {
    return writeContractAsync({
      address:      MARKETPLACE_ADDRESS,
      abi:          MARKETPLACE_ABI,
      functionName: "buyLazy",
      args:         [voucher, signature],
      value:        voucher.price,
    });
  };

  return { buyListing, buyLazy, txHash, isPending, isConfirming, isSuccess };
}
```

### The Graph Query Hook

```typescript
// frontend/src/hooks/useNFTGallery.ts
import { useQuery } from "@tanstack/react-query";
import { request, gql } from "graphql-request";

const SUBGRAPH_URL = process.env.NEXT_PUBLIC_SUBGRAPH_URL!;

// GraphQL query — fetch active listings with NFT metadata
const ACTIVE_LISTINGS_QUERY = gql`
  query GetActiveListings($first: Int!, $skip: Int!) {
    listings(
      where: { active: true }
      orderBy: createdAt
      orderDirection: desc
      first: $first
      skip: $skip
    ) {
      id
      price
      seller
      createdAt
      nft {
        id
        tokenId
        creator
        metadataCID
        royaltyBps
        frozen
      }
    }
  }
`;

interface Listing {
  id:        string;
  price:     string;
  seller:    string;
  createdAt: string;
  nft: {
    id:          string;
    tokenId:     string;
    creator:     string;
    metadataCID: string;
    royaltyBps:  number;
    frozen:      boolean;
  };
}

export function useNFTGallery(page: number = 0, pageSize: number = 24) {
  return useQuery({
    queryKey: ["nft-gallery", page, pageSize],
    queryFn:  async () => {
      const data = await request<{ listings: Listing[] }>(
        SUBGRAPH_URL,
        ACTIVE_LISTINGS_QUERY,
        { first: pageSize, skip: page * pageSize }
      );
      return data.listings;
    },
    staleTime: 30_000,  // Treat data as fresh for 30s (The Graph can lag slightly)
    refetchInterval: 60_000,
  });
}
```

### NFT Card Component

```tsx
// frontend/src/components/NFTCard.tsx
"use client";

import { useBuyNFT } from "@/hooks/useBuyNFT";
import { formatEther } from "viem";
import Image from "next/image";

interface NFTCardProps {
  listing: {
    id:    string;
    price: string;
    nft: {
      tokenId:     string;
      metadataCID: string;
      creator:     string;
      royaltyBps:  number;
    };
  };
}

export function NFTCard({ listing }: NFTCardProps) {
  const { buyListing, isPending, isConfirming, isSuccess } = useBuyNFT();

  const handleBuy = async () => {
    await buyListing(BigInt(listing.id), BigInt(listing.price));
  };

  const royaltyPercent = (listing.nft.royaltyBps / 100).toFixed(1);
  const ipfsGateway    = "https://gateway.pinata.cloud/ipfs/";

  return (
    <div className="rounded-2xl border border-zinc-800 bg-zinc-900 overflow-hidden
                    hover:border-violet-500 transition-colors">
      {/* NFT Image from IPFS */}
      <div className="relative aspect-square">
        <Image
          src={`${ipfsGateway}${listing.nft.metadataCID}`}
          alt={`NFT #${listing.nft.tokenId}`}
          fill
          className="object-cover"
          // Fallback to placeholder on error
          onError={(e) => { (e.target as HTMLImageElement).src = "/placeholder.png"; }}
        />
      </div>

      <div className="p-4 space-y-3">
        <div className="flex justify-between items-center">
          <span className="text-white font-semibold">
            #{listing.nft.tokenId}
          </span>
          {/* Royalty badge — shows buyers the creator gets % */}
          <span className="text-xs bg-violet-900/50 text-violet-300 px-2 py-1 rounded-full">
            {royaltyPercent}% royalty
          </span>
        </div>

        <div className="flex justify-between items-center">
          <span className="text-zinc-400 text-sm">Price</span>
          <span className="text-white font-bold">
            {formatEther(BigInt(listing.price))} ETH
          </span>
        </div>

        <button
          onClick={handleBuy}
          disabled={isPending || isConfirming}
          className="w-full py-2 bg-violet-600 hover:bg-violet-500 disabled:opacity-50
                     text-white rounded-xl font-medium transition-colors"
        >
          {isPending   ? "Confirm in wallet..." :
           isConfirming ? "Confirming..." :
           isSuccess    ? "✓ Purchased!" :
           "Buy Now"}
        </button>
      </div>
    </div>
  );
}
```

---

## 9. IPFS Pinning Strategy

### Why IPFS + Pinning?

NFT metadata must be **permanently accessible**. HTTP URLs can go down (project dies, server costs). IPFS content-addresses data by its hash — the same CID always points to the same content, forever, as long as someone pins it.

### Upload Flow — Pinata SDK

```typescript
// backend/src/services/ipfs.ts
import PinataSDK from "@pinata/sdk";
import { Readable } from "stream";

const pinata = new PinataSDK({
  pinataApiKey:    process.env.PINATA_API_KEY!,
  pinataSecretApiKey: process.env.PINATA_SECRET_KEY!,
});

/**
 * Step 1: Upload the raw image file to IPFS.
 * Returns the IPFS CID of the image.
 */
export async function uploadImage(
  fileBuffer: Buffer,
  filename:   string,
  mimeType:   string
): Promise<string> {
  const stream = Readable.from(fileBuffer);

  const result = await pinata.pinFileToIPFS(stream, {
    pinataMetadata: {
      name: filename,
    },
    pinataOptions: {
      cidVersion: 1,     // Use CIDv1 (base32) — more future-proof than CIDv0
    },
  });

  return result.IpfsHash; // e.g. "bafybeig..."
}

/**
 * Step 2: Upload metadata JSON referencing the image CID.
 * Returns the metadata CID — this is what goes into the NFT contract.
 *
 * Follows ERC-721 metadata standard:
 * https://eips.ethereum.org/EIPS/eip-721
 */
export async function uploadMetadata(params: {
  name:        string;
  description: string;
  imageCID:    string;
  attributes?: Array<{ trait_type: string; value: string | number }>;
  creatorAddress: string;
}): Promise<string> {
  const metadata = {
    name:        params.name,
    description: params.description,
    image:       `ipfs://${params.imageCID}`,   // ipfs:// URI — NOT a gateway URL
    external_url: `https://artvault.io/nft/${params.creatorAddress}`,
    attributes:  params.attributes ?? [],

    // ArtVault custom fields
    artvault: {
      creator: params.creatorAddress,
      version: "1.0",
    },
  };

  const result = await pinata.pinJSONToIPFS(metadata, {
    pinataMetadata: {
      name: `${params.name} - Metadata`,
    },
    pinataOptions: {
      cidVersion: 1,
    },
  });

  return result.IpfsHash;
}

/**
 * Step 3: Verify both CIDs are accessible before allowing creator to sign voucher.
 * Prevents "I minted but metadata is missing" support tickets.
 */
export async function verifyCIDAccessible(cid: string): Promise<boolean> {
  try {
    const url = `https://gateway.pinata.cloud/ipfs/${cid}`;
    const response = await fetch(url, { method: "HEAD", signal: AbortSignal.timeout(10000) });
    return response.ok;
  } catch {
    return false;
  }
}
```

### Metadata Freeze Workflow

```typescript
// backend/src/services/metadataFreeze.ts
/**
 * After reveal, call NFT.freezeMetadata() on-chain.
 * Once frozen:
 *   1. tokenURI cannot change (on-chain enforcement)
 *   2. Pinata "permanent pin" set (API-level durability)
 *   3. We additionally pin to web3.storage as backup
 */
export async function freezeAndBackupMetadata(
  tokenId:     bigint,
  metadataCID: string,
  imageCID:    string
): Promise<void> {
  // 1. Set permanent pin label in Pinata (prevents auto-unpinning)
  await pinata.hashPinPolicy(metadataCID, {
    regions: [
      { id: "FRA1", desiredReplicationCount: 2 },
      { id: "NYC1", desiredReplicationCount: 2 },
    ],
  });
  await pinata.hashPinPolicy(imageCID, {
    regions: [
      { id: "FRA1", desiredReplicationCount: 2 },
      { id: "NYC1", desiredReplicationCount: 2 },
    ],
  });

  // 2. Log freeze event to database for audit trail
  await db.nftFreezeLog.create({
    data: {
      tokenId:     tokenId.toString(),
      metadataCID,
      imageCID,
      frozenAt:    new Date(),
    },
  });
}
```

### Gateway Selection Strategy

| Gateway | Use Case | Notes |
|---|---|---|
| `ipfs://` URI | Smart contract `tokenURI` | Native IPFS — let wallets/apps resolve |
| `https://gateway.pinata.cloud/ipfs/` | Frontend image display | Fastest for Pinata-pinned content |
| `https://cloudflare-ipfs.com/ipfs/` | Fallback gateway | High availability, cached globally |
| `https://dweb.link/ipfs/` | Developer / API access | Protocol Labs gateway |
| `https://nftstorage.link/ipfs/` | Long-term archival | NFT.Storage, free permanent storage |

**Rule**: Always store `ipfs://CID` in the contract. Resolve to HTTP gateways only in the frontend, with fallback logic:

```typescript
// frontend/src/lib/ipfs.ts
const GATEWAYS = [
  "https://gateway.pinata.cloud/ipfs/",
  "https://cloudflare-ipfs.com/ipfs/",
  "https://dweb.link/ipfs/",
];

export function resolveIPFS(uri: string): string {
  if (!uri.startsWith("ipfs://")) return uri;
  const cid = uri.replace("ipfs://", "");
  // Primary gateway — fallback handled by Next.js Image onError
  return `${GATEWAYS[0]}${cid}`;
}

// Try multiple gateways with Promise.any — return whichever responds first
export async function fetchFromIPFS(cid: string): Promise<Response> {
  const requests = GATEWAYS.map(gw =>
    fetch(`${gw}${cid}`, { signal: AbortSignal.timeout(5000) })
  );
  return Promise.any(requests);
}
```

---

## 10. Enforced Royalties Debate

### Background: The OpenSea vs. Blur Wars (2022–2023)

The NFT royalty landscape was fundamentally disrupted by a price war between marketplaces:

- **August 2022**: Blur launches with **0% royalties** as default, attracting high-volume traders
- **October 2022**: OpenSea, under pressure, makes royalties optional on secondary sales
- **February 2023**: Blur achieves dominant market share over OpenSea
- **Result**: Creator royalties plummeted from ~$500M/year to near zero on major platforms

The core problem: **royalties were a social contract, not a technical enforcement**.

---

### Comparison: Enforcement Approaches

| Approach | Example | Mechanism | Bypassable? | Creator UX | Trader UX |
|---|---|---|---|---|---|
| **Off-chain (social)** | OpenSea (2023+) | Marketplace chooses to pay | ✅ Yes — trade on Blur | Easy | Flexible |
| **Blocklist approach** | Manifold/LooksRare | NFT blocks transfers to non-royalty-paying contracts | ⚠️ Partial | Complex | Restrictive |
| **Operator filter** | OpenSea OS Filter | Allowlist of approved operators | ✅ Bypassable via wrapper | Moderate | Restrictive |
| **On-chain enforced** | ArtVault | Marketplace reads EIP-2981 + splits before releasing funds | ❌ Not on ArtVault | Best | Less flexible |
| **ERC-721C** | LimitBreak | Token-level transfer restrictions by role | ⚠️ Walled garden | Complex | Very restrictive |
| **No royalties** | Blur | No royalty mechanism | N/A | Worst | Maximum |

---

### The Arguments

**🟢 For Enforced Royalties (ArtVault's position):**

1. **Creator sustainability**: Long-tail income from secondary sales funds continued art creation
2. **Trust**: Collectors know the creator benefit they're supporting is real, not optional
3. **Smart contract integrity**: The rule is transparent, immutable, and auditable
4. **Level playing field**: Removes marketplace-level political games around royalties
5. **Better for emerging artists**: Famous artists can absorb royalty losses; newcomers can't

**🔴 Against Enforced Royalties (Blur / traders' position):**

1. **Liquidity suffers**: High friction → lower trading volume → lower floor prices
2. **Creator sets royalties too high**: No market mechanism to price-correct a 20% royalty
3. **Walled garden risk**: Enforced royalties = platform lock-in (must use ArtVault to trade)
4. **Gas overhead**: On-chain enforcement adds computation costs
5. **Wash trading bypass**: Determined actors use OTC (over-the-counter) trades to bypass

---

### ArtVault's Design Choice & Trade-offs

ArtVault enforces royalties **within its marketplace** but cannot enforce them on external platforms. The design accepts this:

```
ArtVault's Enforcement Perimeter:
┌─────────────────────────────────────┐
│  ArtVault Marketplace Contract      │
│  • buy()       → royalty enforced   │  ✅
│  • buyLazy()   → royalty enforced   │  ✅
│  • finalizeAuction() → enforced     │  ✅
└─────────────────────────────────────┘

Outside ArtVault (cannot control):
  • OpenSea listing   → royalty optional  ⚠️
  • Peer-to-peer tx   → no royalty        ❌
  • Blur listing      → no royalty        ❌
```

**The pragmatic solution**: Pair on-chain enforcement with **creator incentives** to stay on ArtVault:
- Lower platform fees (1% vs OpenSea's 2.5%) in exchange for royalty compliance
- Verified creator badges and featured placement
- Collection analytics dashboard exclusive to ArtVault-minted NFTs

---

### EIP-2981 Adoption Status (as of 2024)

| Platform | Respects EIP-2981 | Notes |
|---|---|---|
| OpenSea | ⚠️ Partial | Optional, depends on collection settings |
| Blur | ❌ No | 0% default, optional 0.5% |
| Zora | ✅ Yes | Full enforcement on-platform |
| Foundation | ✅ Yes | Strong creator-royalty culture |
| SuperRare | ✅ Yes | Curated, 10% royalties standard |
| ArtVault | ✅ Yes | Full on-chain enforcement |

---

## 11. Production Gotchas

- **IPFS CID stability before mint**: CIDs are set at voucher-signing time. If you re-upload the image with any modification (even metadata change), you get a new CID. The old voucher becomes permanently linked to the old CID. Build a strict immutable upload workflow — once signed, never re-upload.

- **EIP-712 `chainId` in domain separator**: The domain separator includes `chainId`. Your signing backend must use the exact chain ID of the deployment target. Signing on Base (8453) and submitting to Polygon (137) will always revert. Frontend must also use the right chain when calling `useChainId()`.

- **`_setTokenURI` gas on first mint**: Setting a long IPFS CID string on-chain costs significant gas (~40,000 gas per character over 32 bytes). Long CIDv1 strings (base32, ~59 chars) cost more than CIDv0 (base58, ~46 chars). Either store only the CID hash and reconstruct the URI in `tokenURI()`, or accept the cost.

- **The Graph indexing lag**: Subgraph can lag 2–30 blocks behind chain tip. A user who just bought an NFT won't see it in their profile immediately. Always show optimistic UI updates locally (write to local state on tx success) and refresh from subgraph after a delay. Never block the success screen on subgraph confirmation.

- **Royalty receiver is immutable after first sale**: In the current design, royalty info is set at `lazyMint()` time and never updated. If the creator changes wallets, they lose royalties. Plan: store royalty receiver as a mutable registry mapping (creator address → payment address), separable from the token.

- **Auction finalization gas wars**: Anyone can call `finalizeAuction()` but it's expensive. Neither party may be incentivized to finalize if the gas cost exceeds the benefit. Solution: build a backend keeper bot (Gelato Network or Chainlink Automation) that monitors ended auctions and calls finalize with sponsored gas.

- **Platform fee recipient update timing**: If `platformFeeRecipient` is a multisig and the multisig is compromised, all future platform fees are at risk. Use a time-lock delay (e.g., 48 hours) on `updatePlatformFee()` so the team can respond before a malicious update takes effect.

- **`call{value: x}()` to contract recipients**: If the royalty receiver or seller is a smart contract that reverts on ETH receive (e.g., a contract with no `receive()` function), the entire sale will revert. Mitigation: use a **pull-payment pattern** where failed pushes queue funds into a claimable mapping, and recipients call `withdraw()` themselves.

- **Nonce gap attacks**: If a creator signs vouchers 0, 1, 2, 3 and voucher 1 sells out, the creator cannot "re-use" nonce 1 — it's used. But if the creator intended to cancel unsold voucher 2, they need to mark nonce 2 as used on-chain (burns gas). Add a `invalidateNonce(nonce)` function so creators can cancel unsigned or unsold vouchers efficiently.

- **Metadata reveal timing attack**: For blind mint collections (placeholder CIDs before reveal), if the reveal transaction is visible in the mempool before it's included in a block, MEV bots can see the CID mapping and front-run to buy the rarest tokens. Use commit-reveal: hash the final CIDs in phase 1, reveal in phase 2 after mint closes.

- **ETH price volatility on lazy mint vouchers**: A voucher signed at 0.5 ETH may feel expensive or cheap days later due to ETH price swings. Vouchers have no expiry by default. Add an `expiry` field to `MintVoucher` and check `block.timestamp < voucher.expiry` in `lazyMint()`. Let creators set 30-day voucher lifetimes.

- **Multi-chain address confusion**: ArtVault on Base and ArtVault on Polygon have different deployed contract addresses for ERC-721 tokens. Token #42 on Base is NOT the same as Token #42 on Polygon. Wallets and UIs may confuse these. Always display the chain name prominently next to every NFT and make the chain part of the canonical NFT identifier.

---

## 12. Lessons Learned

### What Worked Well

**Lazy minting was transformative for artist adoption.** The single biggest friction point for new artists was gas costs. When we removed the upfront minting cost, creator signups increased 4x in the first week of the feature. The EIP-712 signing flow is smooth in MetaMask and WalletConnect — users understand "sign a message" much better than "pay gas to upload."

**Foundry made testing fast and honest.** Coming from Hardhat, the fork-test capability of Foundry was a game-changer. We could test against real Ethereum state with one flag change. The invariant fuzzer caught a royalty calculation overflow edge case (salePrice × royaltyBps overflowing uint96) that unit tests missed entirely — it was in the fuzzer's first 500 runs.

**The Graph subgraph made the frontend simple.** Without indexing, we'd need a centralized backend to track listings and ownership. The subgraph meant the frontend could be purely a GraphQL consumer — no custom indexing infrastructure to maintain.

**EIP-2981 being a standard pays dividends.** External tools (wallets, portfolio trackers, other marketplaces) automatically display royalty info because we implement the standard interface. No custom integration needed. This is what good standards-based design looks like.

### What We'd Do Differently

**Should have used ERC-721C from day one for collection-level enforcement.** EIP-2981 tells other platforms what royalty to pay — it doesn't force them to. LimitBreak's ERC-721C allows the token itself to restrict which contracts can transfer it. For new collections that want maximum creator protection, ERC-721C + ArtVault allowlisting is stronger than EIP-2981 alone.

**The `_sendEth` push-payment pattern was a mistake for royalty receivers.** We had three support tickets in the first month from creators whose multisig wallets couldn't receive ETH (missing `receive()` fallback). We should have built pull-payments (accumulate in contract, let users withdraw) from day one. Rewiring this post-deploy required a contract upgrade.

**Underestimated The Graph's deployment complexity.** The subgraph worked fine in development but required significant iteration on the `subgraph.yaml` configuration for multi-chain support. Each chain needs a separate subgraph deployment with different startBlock values and RPC endpoints. Budget extra time for this.

**Should have added voucher expiry from the start.** We shipped without expiry on `MintVoucher`. Two creators had vouchers circulating for months at prices they considered outdated (ETH had rallied). We had to add an off-chain "voucher invalidation" API (that marks nonces server-side) as a stopgap — messy, and defeats the trustless nature of the system.

**Monitoring was an afterthought.** We set up Tenderly alerts only after a deployment bug went undetected for 6 hours. For every production deployment: immediately set up alerts for `Revert` events, unusual gas usage, and large ETH movements. Tenderly Web3 Actions can trigger within seconds of a suspicious transaction.

### Numbers from Production (First 3 Months)

| Metric | Value |
|---|---|
| Total NFTs minted | 14,200 |
| Lazy-minted (% of total) | 89% |
| Total royalties distributed | ~$43,000 |
| Avg platform fee collected | 2% |
| Auctions created | 318 |
| Anti-snipe extensions triggered | 67 (21% of auctions) |
| Support tickets (ETH stuck) | 3 (all pull-payment issue) |
| Subgraph lag incidents (>1 min) | 4 |
| Gas saved via lazy minting | ~210 ETH equivalent |

---

*Case study authored as part of the ArtVault post-mortem documentation. Contract addresses and specific financial figures are illustrative for educational purposes.*
