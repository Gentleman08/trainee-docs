# Batch 11 — AI Agents & Orchestration
> Building AI systems that can plan, act, and use tools to complete complex tasks autonomously.

---

## 1. AI Agent

**Definition**  
An AI agent is a program that uses an LLM as its "brain" to perceive its environment, make decisions, and take actions to achieve a goal — without being told every step to take.

**Real-World Dev Example**  
A customer support agent autonomously reads a ticket, queries the orders database, checks shipping status, and drafts a reply — all without human scripting of each step.

```
User Goal → [LLM Brain] → decides actions → executes them → returns result
```

**Gotchas & Dev Context**
- Agents are non-deterministic; the same prompt can produce different action sequences
- Cost spirals fast — every LLM call in the loop adds latency and tokens
- Agents need clear exit conditions or they can loop indefinitely
- "Agent" is overloaded — a simple chatbot is NOT an agent; tool use + autonomy = agent

**Production FAQ**

> **Q: When should I use an agent vs. a fixed pipeline?**  
> A: Fixed pipelines when steps are known and stable. Agents when the path to the goal varies per input.

> **Q: How do I limit an agent's blast radius?**  
> A: Scope tools narrowly (read-only first), set max-iteration limits, and sandbox side-effecting actions.

> **Q: Are agents reliable enough for production?**  
> A: For narrow, well-scoped tasks yes. For open-ended tasks, add human-in-the-loop checkpoints.

---

## 2. Agent Loop (Observe → Think → Act)

**Definition**  
The core execution cycle of an agent: it **observes** its current state/environment, **thinks** (calls the LLM to reason about what to do next), then **acts** (calls a tool or produces output), repeating until the goal is met.

**ASCII Diagram**
```
         ┌──────────────────────────────┐
         │                              │
   ──► Observe ──► Think (LLM) ──► Act ─┘
         │                              │
         └────── Goal met? ─────────────► STOP
```

**Real-World Dev Example**  
A research agent: Observe = "I need to find recent papers on transformers." Think = "I'll call the `search_arxiv` tool." Act = runs the search, observes the results, thinks about what to read next, repeats.

**Gotchas & Dev Context**
- Each loop iteration = at least one LLM call; 10 iterations = 10x cost
- LLMs can "think" they're done prematurely (false termination)
- Log every observe/think/act step — debugging without logs is nearly impossible
- Set a hard `max_iterations` ceiling (e.g., 15) to prevent infinite loops

**Production FAQ**

> **Q: How do I detect if an agent is stuck in a loop?**  
> A: Track action history; if the last N actions are identical, force-stop and surface the error.

> **Q: Should the Think step always use the most powerful model?**  
> A: Not necessarily — use a cheaper model for simple action choices; escalate to a powerful one only for complex reasoning.

---

## 3. Tool Use / Function Calling

**Definition**  
Giving an LLM the ability to call external functions (search, database queries, APIs, calculators) at runtime so it can fetch real-world data or trigger actions beyond text generation.

**Real-World Dev Example**  
You define a `get_weather(city: str)` function. The LLM receives the user query "Is it raining in Berlin?" and responds with a structured JSON call `{"name": "get_weather", "arguments": {"city": "Berlin"}}` — your code executes it and feeds results back.

```python
tools = [{"name": "get_weather", "parameters": {"city": {"type": "string"}}}]
response = openai.chat.completions.create(model="gpt-4o", messages=msgs, tools=tools)
# response.choices[0].message.tool_calls → parse & execute
```

**Gotchas & Dev Context**
- The LLM doesn't execute the function — your code does; the LLM only decides to call it
- Always validate/sanitize tool arguments before execution (injection risk)
- Tools should be idempotent where possible; avoid tools with irreversible side effects
- Describe tools precisely — vague descriptions cause wrong tool selection

**Production FAQ**

> **Q: What if the LLM calls a tool with wrong arguments?**  
> A: Return a structured error string back to the LLM; it usually self-corrects on the next turn.

> **Q: How many tools can I give an agent?**  
> A: Practically keep it under ~20; too many tools confuses routing and inflates the system prompt.

---

## 4. Planning (ReAct, Plan-and-Execute)

**Definition**  
Planning strategies determine *how* an agent breaks down a goal and sequences its actions. The two dominant patterns are **ReAct** (interleaved reasoning + acting) and **Plan-and-Execute** (make a full plan first, then execute each step).

**ASCII Diagram**
```
ReAct:
  Thought → Action → Observation → Thought → Action → ...

Plan-and-Execute:
  [Planner LLM] → Plan: [Step1, Step2, Step3]
       ↓
  [Executor] → runs Step1 → Step2 → Step3 sequentially
```

**Real-World Dev Example**  
ReAct: A coding agent reasons "I need to read the file first" → reads it → reasons "now I'll write the fix" → writes it.  
Plan-and-Execute: A report agent plans ["search topic", "summarize sources", "write report"] upfront, then executes each step.

**Gotchas & Dev Context**
- ReAct is flexible but can drift; Plan-and-Execute is more predictable but brittle if the plan is wrong
- Plans become stale — if step 2 fails, a rigid plan has no fallback
- Add a "replan" capability: if execution fails, regenerate the plan
- ReAct works best with strong models (GPT-4o, Claude 3.5+); weaker models lose the thread

**Production FAQ**

> **Q: Which should I use for production?**  
> A: Plan-and-Execute for multi-step workflows with known structure; ReAct for exploratory tasks.

> **Q: How do I prevent plan hallucinations?**  
> A: Constrain the planner to only use available tools; validate each planned step against your tool registry.

---

## 5. Memory (Short-term, Long-term, Episodic)

**Definition**  
Agent memory refers to how information is stored and retrieved across an agent's lifetime — within a session (short-term), across sessions (long-term), or as records of past task runs (episodic).

**ASCII Diagram**
```
┌─────────────────────────────────────────────┐
│  SHORT-TERM  │  LONG-TERM    │  EPISODIC    │
│  (context    │  (vector DB / │  (past run   │
│   window)    │   key-value)  │   summaries) │
└─────────────────────────────────────────────┘
```

**Real-World Dev Example**  
A personal assistant agent: short-term = current conversation, long-term = user's stored preferences in a vector DB, episodic = "Last time you asked about hotels, you chose budget options."

**Gotchas & Dev Context**
- Context window IS short-term memory — it's finite and expensive; summarize aggressively
- Long-term memory via vector DB introduces retrieval errors — garbage in, garbage out
- Episodic memory is powerful but requires a well-designed storage schema
- Memory poisoning is a real attack vector — validate what gets written to long-term memory
- Don't store PII in long-term memory without explicit user consent and encryption

**Production FAQ**

> **Q: How do I handle context window overflow in long sessions?**  
> A: Summarize older turns with a compression LLM call and retain only the summary.

> **Q: What's the simplest long-term memory setup?**  
> A: A key-value store (Redis) for structured facts + a vector DB (Chroma/Pinecone) for semantic retrieval.

---

## 6. Multi-Agent Systems

**Definition**  
A multi-agent system is a setup where multiple AI agents collaborate (or compete) to solve a task — each agent specializes in a subtask and communicates results to others.

**ASCII Diagram**
```
          ┌─────────────┐
          │ Orchestrator│
          └──────┬──────┘
        ┌────────┼────────┐
        ▼        ▼        ▼
   [Researcher] [Coder] [Reviewer]
        └────────┼────────┘
                 ▼
           Final Output
```

**Real-World Dev Example**  
A software dev system: an Orchestrator agent receives a feature request → delegates to a Coder agent → passes output to a Reviewer agent → Reviewer sends feedback back to Coder → Orchestrator collects the approved code.

**Gotchas & Dev Context**
- Communication between agents adds latency — every handoff is an LLM call
- Agents can disagree or produce conflicting outputs — define a "tiebreaker" mechanism
- Shared state (e.g., a shared scratchpad) helps but can cause race conditions in parallel execution
- Start with 2-3 agents; more agents = exponentially harder to debug

**Production FAQ**

> **Q: How do agents communicate?**  
> A: Usually via message passing — structured text or JSON handed off through an orchestrator or a shared message queue.

> **Q: Should agents share the same LLM?**  
> A: Not necessarily; use cheap models for simple agents, expensive ones only for reasoning-heavy roles.

---

## 7. Agent Frameworks (LangGraph, CrewAI, AutoGen, Semantic Kernel)

**Definition**  
Agent frameworks are libraries that provide scaffolding for building multi-step, multi-agent AI systems — handling the loop, memory, tool calling, and agent communication so you don't build it from scratch.

**Real-World Dev Example**

| Framework | Best For |
|---|---|
| **LangGraph** | Stateful, graph-based workflows with explicit control flow |
| **CrewAI** | Role-based multi-agent teams (researcher, writer, critic) |
| **AutoGen** | Conversational multi-agent back-and-forth (Microsoft) |
| **Semantic Kernel** | Enterprise .NET/Python apps with plugin architecture |

**Gotchas & Dev Context**
- Frameworks abstract complexity but also hide bugs — know the underlying agent loop
- LangGraph gives the most control; CrewAI is the fastest to prototype
- AutoGen excels at agent-to-agent dialogue but can be verbose
- Semantic Kernel is Microsoft's bet — integrates tightly with Azure OpenAI
- All frameworks are evolving fast; pin versions in production

**Production FAQ**

> **Q: Which framework should a beginner start with?**  
> A: CrewAI for speed-to-demo; LangGraph once you need fine-grained control over state.

> **Q: Can I mix frameworks?**  
> A: Technically yes, but avoid it — inter-framework glue code becomes a maintenance burden.

---

## 8. Agentic RAG

**Definition**  
Agentic RAG extends standard Retrieval-Augmented Generation by having an agent *decide* when to retrieve, *what* to retrieve, and *how many times* to retrieve — rather than a single fixed retrieval step before generation.

**ASCII Diagram**
```
Standard RAG:  Query → Retrieve → Generate (one shot)

Agentic RAG:   Query → Think → Retrieve? → Read results
                           ↑                      │
                           └──── Need more? ───────┘
                                       │
                                  Generate Answer
```

**Real-World Dev Example**  
A legal research agent: gets a question → retrieves case law → reads it → realizes it needs a specific precedent → retrieves again with a refined query → synthesizes the answer.

**Gotchas & Dev Context**
- Multiple retrieval rounds multiply latency and cost
- Agents can over-retrieve ("just one more search") — cap retrieval iterations
- Query rewriting between rounds significantly improves recall
- Combine with re-ranking for better precision at each retrieval step

**Production FAQ**

> **Q: When does agentic RAG outperform standard RAG?**  
> A: When the answer requires multi-hop reasoning across documents or when the first retrieval is insufficient.

> **Q: How do I prevent retrieval loops?**  
> A: Set a `max_retrieval_steps` limit and require the agent to justify each retrieval call.

---

## 9. Human-in-the-Loop (HITL)

**Definition**  
Human-in-the-Loop is a design pattern where a human is inserted into the agent's execution at critical decision points to review, approve, or correct the agent's planned actions before they run.

**ASCII Diagram**
```
Agent plans action
        │
   [HIGH RISK?] ──Yes──► Pause → Human Review → Approve/Reject
        │                                              │
       No                                        Resume / Abort
        │
   Execute directly
```

**Real-World Dev Example**  
A DevOps agent proposes to delete unused cloud resources. Before executing `terraform destroy`, it pauses and sends a Slack message to an engineer: "I plan to delete 3 EC2 instances. Approve? [Yes/No]"

**Gotchas & Dev Context**
- HITL adds latency — not suitable for real-time workflows
- Define *which* actions require human approval upfront (irreversible, high-cost, external-facing)
- Approval interfaces need context — show the agent's reasoning, not just the action
- Async approval (Slack, email) is more practical than blocking UI approvals

**Production FAQ**

> **Q: How do I decide what needs HITL?**  
> A: Use a risk matrix: irreversible + high-impact = always HITL; reversible + low-impact = auto-execute.

> **Q: What if the human doesn't respond?**  
> A: Set a timeout with a safe default (e.g., auto-reject after 1 hour of no response).

---

## 10. Guardrails for Agents

**Definition**  
Guardrails are safety and policy controls placed around an agent to prevent harmful, incorrect, or out-of-scope actions — including input validation, output filtering, action whitelisting, and rate limiting.

**Real-World Dev Example**  
An e-commerce agent is constrained: it can only call refund APIs for amounts under $500, can't access competitor data, and all generated customer emails are filtered through a toxicity classifier before sending.

```
User Input → [Input Guard] → Agent → [Action Whitelist] → Tool
                                            │
                            Output ← [Output Filter] ←──┘
```

**Gotchas & Dev Context**
- Guardrails ≠ prompts — a prompt saying "don't do X" is not a guardrail; code enforcement is
- Use allowlists (only permitted actions) over denylists (block known bad actions)
- Prompt injection via tool outputs can bypass LLM-level guards — sanitize tool return values
- Monitor for guardrail bypass attempts in production logs

**Production FAQ**

> **Q: What's the minimum guardrail set for a production agent?**  
> A: Input sanitization, tool action allowlist, max-iterations cap, output content filter, and cost/rate limits.

> **Q: Can guardrails be implemented in the LLM's system prompt alone?**  
> A: No — system prompt instructions can be overridden by adversarial inputs. Always enforce with code-level checks.

---

## 11. Task Decomposition

**Definition**  
Task decomposition is the process of breaking a complex, high-level goal into smaller, manageable subtasks that can be executed sequentially or in parallel by an agent or multiple agents.

**ASCII Diagram**
```
"Write a market research report on EVs"
              │
    ┌─────────┼──────────┐
    ▼         ▼          ▼
[Search    [Gather    [Analyze
 news]      stats]    competitors]
    └─────────┼──────────┘
              ▼
        [Write report]
```

**Real-World Dev Example**  
A planner agent receives "Build a REST API for user auth." It decomposes this into: (1) design schema, (2) write endpoint stubs, (3) implement JWT logic, (4) write tests — assigning each to a specialized sub-agent.

**Gotchas & Dev Context**
- Decomposition quality determines everything — a bad plan produces bad results even with great execution
- Subtasks must have clear inputs/outputs and defined dependencies
- Overly granular decomposition creates unnecessary overhead; aim for meaningful chunks
- LLMs tend to decompose too optimistically — add a validation step to check feasibility

**Production FAQ**

> **Q: Should decomposition happen once or dynamically?**  
> A: Static decomposition for known workflows; dynamic (replanning) for exploratory tasks where subtasks reveal new requirements.

> **Q: How do I handle subtask failures?**  
> A: Design with retry + fallback at each node; don't let one failed subtask silently corrupt downstream results.

---

## 12. Code Interpreter / Sandbox Execution

**Definition**  
A code interpreter gives an agent the ability to write and execute code (usually Python) in a secure, isolated sandbox environment, enabling dynamic computation, data analysis, and file manipulation.

**Real-World Dev Example**  
A data analyst agent receives a CSV file. It writes Python code to clean the data, runs it in a sandbox, reads the output, then writes visualization code and executes it — all without any pre-written analysis logic.

```python
# Agent generates this, sandbox executes it
import pandas as pd
df = pd.read_csv("sales.csv")
print(df.groupby("region")["revenue"].sum())
```

**Gotchas & Dev Context**
- Always sandbox — never run LLM-generated code on the host machine directly
- Sandboxes should have: no network access, CPU/memory limits, execution timeouts
- Popular options: OpenAI's built-in Code Interpreter, E2B, Docker with seccomp
- Agents may generate inefficient code (O(n²) loops on large datasets) — add resource guardrails
- Output size from code execution can be massive; truncate before feeding back to LLM

**Production FAQ**

> **Q: What's the security risk of code execution in agents?**  
> A: Without isolation, LLM-generated code can read secrets, make network calls, or destroy files. Always use a hardened sandbox.

> **Q: Can I let agents install packages in the sandbox?**  
> A: Only from a pre-approved allowlist; never allow arbitrary `pip install` in production.

---

## 13. Browser Agents

**Definition**  
Browser agents can control a web browser programmatically — clicking, typing, navigating, and scraping — allowing them to interact with any website as a human would, even those without APIs.

**ASCII Diagram**
```
Agent ──► [Browser Controller] ──► Opens URL
                │                       │
           Screenshots/DOM ◄────────────┘
                │
          LLM interprets page → next action (click/type/navigate)
```

**Real-World Dev Example**  
A procurement agent logs into a supplier portal (no API), navigates to the order form, fills in quantities, verifies the total, and submits the order — autonomously.

Tools: Playwright + LLM vision, Selenium, Browserbase, Stagehand.

**Gotchas & Dev Context**
- Browser agents are brittle — a UI redesign breaks the agent
- CAPTCHAs, login walls, and bot detection are common blockers
- Vision-based approaches (screenshot → LLM) are more robust than DOM-selector-based ones
- Session management is tricky — handle auth tokens, cookies, and timeouts explicitly
- Rate-limit browser actions to avoid getting IP-banned

**Production FAQ**

> **Q: How is a browser agent different from web scraping?**  
> A: Scraping extracts static data; a browser agent reasons about pages and takes multi-step actions dynamically.

> **Q: What's the best stack for browser agents?**  
> A: Playwright for browser control + GPT-4o vision or Claude for page understanding. Browserbase for hosted sessions.

---

## 14. MCP (Model Context Protocol)

**Definition**  
MCP is an open standard (by Anthropic) that defines how AI models connect to external tools, data sources, and services — like a universal plugin interface so any model can talk to any tool using a common protocol.

**ASCII Diagram**
```
  ┌─────────┐      MCP Protocol      ┌──────────────┐
  │  LLM /  │ ◄────────────────────► │  MCP Server  │
  │  Agent  │   (JSON-RPC over       │  (tool/data) │
  └─────────┘    stdio or HTTP)      └──────────────┘
```

**Real-World Dev Example**  
You build an MCP server that exposes your internal Jira instance. Any MCP-compatible agent (Claude, GPT via MCP adapter) can now query tickets, create issues, and update statuses — without custom integration code per model.

**Gotchas & Dev Context**
- MCP is gaining adoption fast but is not yet universally supported across all frameworks
- MCP servers run as local processes (stdio) or remote services (HTTP/SSE)
- Each MCP server declares its capabilities (tools, resources, prompts) via a manifest
- Security: MCP servers have real system access — treat them like any privileged service
- Not the same as OpenAI's function calling — MCP is model-agnostic

**Production FAQ**

> **Q: Do I need MCP if I already have function calling?**  
> A: If you're building reusable tools used across multiple agents/models, MCP's standardization saves integration work.

> **Q: Is MCP stable enough for production?**  
> A: The spec is maturing (v1.0 released late 2024); treat it as production-ready for greenfield, with versioning caution.

---

## 15. A2A (Agent-to-Agent Protocol)

**Definition**  
A2A is an open protocol (by Google) that defines how independent AI agents discover each other, communicate, and delegate tasks — enabling interoperability between agents built on different frameworks or by different vendors.

**ASCII Diagram**
```
  Agent A (LangGraph)          Agent B (CrewAI)
       │                             │
       │── A2A Task Request ────────►│
       │                        executes task
       │◄── A2A Response ───────────│
       │     (result + status)       │
```

**Real-World Dev Example**  
A legal firm's research agent (built on AutoGen) needs financial analysis. It discovers a specialist finance agent (built on CrewAI) via an A2A registry, delegates the sub-task, receives results, and continues — without either team modifying their agent's internals.

**Gotchas & Dev Context**
- A2A and MCP are complementary: MCP = agent-to-tool; A2A = agent-to-agent
- Agents expose an "Agent Card" (JSON) describing capabilities, input/output schemas
- Authentication between agents matters — don't assume agents are trusted by default
- Still early-stage (launched April 2025); major frameworks are adding support progressively

**Production FAQ**

> **Q: How is A2A different from just calling another agent's API?**  
> A: A2A provides discovery, capability negotiation, streaming, and task lifecycle management — not just a raw HTTP call.

> **Q: Should I adopt A2A now?**  
> A: Evaluate if you're building cross-team or cross-vendor agent ecosystems. For single-team systems, internal messaging is fine for now.

---

## 16. Workflow Orchestration vs. Autonomous Agents

**Definition**  
**Workflow orchestration** executes a predefined, deterministic sequence of steps (like a flowchart). **Autonomous agents** dynamically decide their own steps at runtime using LLM reasoning. The distinction is: hardcoded path vs. self-directed path.

**ASCII Diagram**
```
Workflow Orchestration:
  Step1 → Step2 → Step3 → Done   (fixed, predictable)

Autonomous Agent:
  Goal → Think → Act → Observe → Think → Act → ...  (dynamic, emergent)
```

**Real-World Dev Example**  
- **Workflow**: Airflow DAG that ETLs data nightly — always the same steps in the same order.  
- **Autonomous Agent**: A research agent that decides how many searches to run, which sources to trust, and when it has "enough" information — nobody hardcoded that logic.

**Gotchas & Dev Context**
- Most production "agents" are actually workflow + LLM hybrids (orchestrated agents)
- Pure autonomy = harder to test, audit, and predict; use it only where flexibility is genuinely needed
- LangGraph sits in the middle: graph-based (structured) but with LLM-driven routing
- For compliance-heavy domains (finance, healthcare), orchestration is preferred for auditability
- "Agentic" features can be added incrementally to existing orchestration pipelines

**Production FAQ**

> **Q: Which approach is more reliable in production?**  
> A: Workflow orchestration — it's deterministic and easier to monitor. Autonomous agents trade reliability for flexibility.

> **Q: Can I combine both?**  
> A: Yes — the sweet spot is an orchestrated outer workflow with autonomous agents handling unpredictable inner subtasks. This is called a "structured agentic" pattern.

---

*End of Batch 11 — AI Agents & Orchestration*
