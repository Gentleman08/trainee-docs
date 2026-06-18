# PROMPT — Software Development Notes

Write me new notes on Software Development & Engineering in a new directory such that it explains each of the term below in beginner friendly language.

For each term:
- Write real world development example
- ASCII diagram if applicable
- Add gotchas and developer-related context
- Add production scenario based FAQ

Additionally, after the glossary, write **2 full project case studies** (described at the bottom) with architecture, code snippets, design decisions, and lessons learned.

Write me a markdown file with index at the starting, create it by yourself after analysing the content. If required divide the notes generation into batches and maintain a batch file to continue from next batch if context window is finished.

Also make the notes as short as possible without degrading quality and without degrading beginner friendly language.

---

## PART 1 — Complete Software Development Glossary

### Batch 1 — Programming Fundamentals
Compiled vs Interpreted Languages
Statically Typed vs Dynamically Typed
Strong vs Weak Typing
Variables, Constants, Literals
Data Types (Primitive & Composite)
Control Flow (if/else, switch, loops)
Functions / Methods
Parameters vs Arguments (Pass by Value vs Reference)
Scope & Lifetime
Recursion
Error Handling (Exceptions, Try/Catch, Error Codes)
Call Stack
Stack Overflow
Memory Management (Stack vs Heap)
Garbage Collection
Pointers & References
Immutability
Concurrency vs Parallelism
Threads & Processes
Race Conditions & Deadlocks

### Batch 2 — Object-Oriented Programming
OOP Overview
Classes & Objects
Encapsulation
Abstraction
Inheritance (Single, Multiple, Multilevel)
Polymorphism (Compile-time vs Runtime)
Method Overloading vs Overriding
Interfaces
Abstract Classes
Composition vs Inheritance
Coupling & Cohesion
SOLID Principles
Single Responsibility Principle (SRP)
Open/Closed Principle (OCP)
Liskov Substitution Principle (LSP)
Interface Segregation Principle (ISP)
Dependency Inversion Principle (DIP)
Dependency Injection (DI)
Inversion of Control (IoC)
DI Containers

### Batch 3 — Design Patterns
Design Pattern Overview (Gang of Four)
Creational Patterns:
- Singleton
- Factory Method
- Abstract Factory
- Builder
- Prototype
Structural Patterns:
- Adapter
- Decorator
- Facade
- Proxy
- Bridge
- Composite
- Flyweight
Behavioral Patterns:
- Observer
- Strategy
- Command
- State
- Template Method
- Iterator
- Chain of Responsibility
- Mediator

### Batch 4 — Data Structures
Arrays & Dynamic Arrays
Linked Lists (Singly, Doubly, Circular)
Stack
Queue (Regular, Priority, Deque)
Hash Table / Hash Map
Sets
Trees (Binary Tree, BST, AVL, Red-Black)
Heaps (Min Heap, Max Heap)
Tries
Graphs (Directed, Undirected, Weighted)
Adjacency Matrix vs Adjacency List
Big O Notation (Time & Space Complexity)
O(1), O(log n), O(n), O(n log n), O(n²)
Amortized Analysis
Space-Time Tradeoff

### Batch 5 — Algorithms
Sorting (Bubble, Selection, Insertion, Merge, Quick, Heap, Radix)
Searching (Linear, Binary, Interpolation)
BFS (Breadth-First Search)
DFS (Depth-First Search)
Dijkstra's Algorithm
Dynamic Programming (Memoization vs Tabulation)
Greedy Algorithms
Divide and Conquer
Backtracking
Two Pointers
Sliding Window
Recursion vs Iteration
Hashing Algorithms
String Matching (KMP, Rabin-Karp)
Graph Algorithms (Topological Sort, MST, Shortest Path)

### Batch 6 — Software Architecture
Monolithic Architecture
Microservices Architecture
Service-Oriented Architecture (SOA)
Event-Driven Architecture
Hexagonal Architecture (Ports & Adapters)
Clean Architecture
Layered Architecture (Presentation, Business, Data)
Domain-Driven Design (DDD) — Entity, Value Object, Aggregate, Repository
CQRS (Command Query Responsibility Segregation)
Event Sourcing
Saga Pattern
API Gateway
Service Mesh
Backend for Frontend (BFF)
Strangler Fig Pattern
12-Factor App
Serverless Architecture
Edge Computing

### Batch 7 — APIs & Communication
REST API Design (Resources, Verbs, Status Codes)
RESTful Constraints (Stateless, Cacheable, Uniform Interface)
GraphQL (Schema, Query, Mutation, Subscription)
gRPC (Protocol Buffers, Streaming, Service Definition)
WebSocket
Server-Sent Events (SSE)
Long Polling
Message Queue (RabbitMQ, Kafka, SQS)
Pub/Sub Pattern
Event Bus
API Versioning Strategies
API Documentation (OpenAPI / Swagger)
API Gateway (Kong, AWS API Gateway)
Pagination (Offset, Cursor, Keyset)
Idempotency Keys
HATEOAS
Content Negotiation

### Batch 8 — Databases & Storage
Relational Database (RDBMS)
SQL Fundamentals (SELECT, JOIN, GROUP BY, HAVING, Subquery)
Normalization (1NF, 2NF, 3NF, BCNF)
Denormalization
Indexes (B-Tree, Hash, Composite, Covering)
Transactions (ACID)
Isolation Levels (Read Uncommitted, Read Committed, Repeatable Read, Serializable)
Locks (Shared, Exclusive, Deadlocks)
NoSQL (Document, Key-Value, Column-Family, Graph)
CAP Theorem
BASE (Basically Available, Soft State, Eventually Consistent)
Sharding / Partitioning (Horizontal vs Vertical)
Replication (Leader-Follower, Multi-Leader, Leaderless)
Connection Pooling
ORM (Object-Relational Mapping)
Database Migration
Stored Procedures / Triggers / Views
Time-Series Databases
Full-Text Search Engines

### Batch 9 — Testing
Unit Testing
Integration Testing
End-to-End (E2E) Testing
Acceptance Testing
Regression Testing
Smoke Testing / Sanity Testing
Performance Testing (Load, Stress, Spike, Soak)
Testing Pyramid
Test Doubles (Mock, Stub, Spy, Fake, Dummy)
TDD (Test-Driven Development)
BDD (Behavior-Driven Development)
Property-Based Testing
Mutation Testing
Code Coverage (Line, Branch, Statement)
Contract Testing (Pact)
Chaos Engineering
Flaky Tests
Test Fixtures / Factories

### Batch 10 — DevOps & CI/CD
DevOps Overview
CI (Continuous Integration)
CD (Continuous Delivery vs Continuous Deployment)
Build Pipeline
Artifact Repository
Infrastructure as Code (IaC)
Configuration Management
Containerization (Docker)
Container Orchestration (Kubernetes)
GitOps
Feature Flags / Feature Toggles
Blue-Green Deployment
Canary Deployment
Rolling Deployment
A/B Testing
Trunk-Based Development
Semantic Versioning (SemVer)
Changelog / Release Notes
Incident Management (Runbooks, Postmortems)
SRE (Site Reliability Engineering)

### Batch 11 — Security Fundamentals
Authentication vs Authorization
Hashing vs Encryption vs Encoding
Symmetric vs Asymmetric Encryption
TLS / SSL Handshake
JWT (JSON Web Token) — Structure, Validation, Pitfalls
OAuth 2.0 Flows (Auth Code, PKCE, Client Credentials)
OIDC (OpenID Connect)
Session Management
OWASP Top 10
SQL Injection
XSS (Cross-Site Scripting)
CSRF (Cross-Site Request Forgery)
CORS
Input Validation & Sanitization
Secrets Management (Vault, Environment Variables)
Principle of Least Privilege
Defense in Depth
Security Headers
Rate Limiting / Brute Force Protection
Dependency Scanning (Supply Chain Security)

### Batch 12 — System Design Concepts
Scalability (Horizontal vs Vertical)
Load Balancing (Round Robin, Least Connections, Consistent Hashing)
Caching (In-Memory, CDN, Browser, Application, Database)
Cache Invalidation Strategies (TTL, Write-Through, Write-Behind)
CDN (Content Delivery Network)
Reverse Proxy
Rate Limiter (Token Bucket, Sliding Window)
Circuit Breaker
Retry with Exponential Backoff
Distributed Systems
Consensus (Raft, Paxos)
Leader Election
Distributed Locking
Consistent Hashing
Bloom Filter
UUID / ULID / Snowflake ID
Idempotency
Eventual Consistency
Back-of-the-Envelope Estimation
SLA / SLO / SLI

---

## PART 2 — Project Case Studies

### Case Study 1: URL Shortener System (TinyLink)

Design and build a production-grade URL shortener that:
- Generates short URLs from long URLs (Base62 encoding)
- Redirects short URLs to original with 301/302
- Tracks click analytics (count, referrer, geo, device)
- Supports custom aliases and expiration
- Rate limiting per user/IP
- Horizontal scaling for millions of URLs

**Cover in the case study:**
- System design diagram (ASCII): API → ID Generator → Database → Cache → Redirect
- Tech stack: Go/Python/Node.js, PostgreSQL, Redis, Kafka (for analytics)
- Code snippets: Base62 encoding, redirect handler, rate limiter middleware, analytics consumer
- Database schema: URLs table, Clicks table, partitioning strategy
- Scaling: read-heavy system, caching strategy, database sharding
- ID generation: auto-increment vs pre-generated ranges vs Snowflake
- Testing: unit tests, load testing (k6), chaos testing
- Deployment: Docker, Kubernetes, CI/CD
- Monitoring: latency percentiles, error rates, redirect SLOs
- Lessons learned & production gotchas

### Case Study 2: Event-Driven E-Commerce Backend (ShopStream)

Design and build a microservices e-commerce backend that:
- Services: User, Product Catalog, Cart, Order, Payment, Notification
- Event-driven communication (Kafka/RabbitMQ)
- Saga pattern for distributed transactions (Order → Payment → Inventory)
- API Gateway for routing and auth
- CQRS for product catalog (write store + read-optimized search)
- Idempotent payment processing

**Cover in the case study:**
- Architecture diagram (ASCII): API Gateway → Services → Event Bus → Consumers
- Tech stack: Node.js/Go microservices, PostgreSQL, MongoDB, Redis, Kafka, Elasticsearch
- Code snippets: Saga orchestrator, event producer/consumer, idempotency middleware, API Gateway config
- Database design: per-service DB, event store
- Communication: sync (gRPC between services) vs async (Kafka events)
- Testing: contract testing (Pact), integration tests with Testcontainers
- Deployment: Docker Compose (dev) → Kubernetes (prod)
- Observability: distributed tracing (OpenTelemetry), centralized logging, dashboards
- Failure handling: dead letter queues, retry policies, circuit breakers
- Lessons learned & production gotchas
