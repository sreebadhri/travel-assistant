# Travel Assistant — Architecture

A multi-agent AI travel assistant built incrementally, with a focus on production
patterns and responsible AI.

---

## Roadmap

| Phase | Focus                        | Status      |
|-------|------------------------------|-------------|
| 1     | Foundation & Responsible AI  | ✅ Complete  |
| 2     | Production Code Quality      | Not started |
| 3     | API Layer (FastAPI)          | Not started |
| 4     | Observability & Reliability  | Not started |
| 5     | Deployment & Infrastructure  | Not started |
| 6     | Advanced AI Patterns (RAG)   | Not started |

---

## Phase 1: Foundation & Responsible AI ✅

Built the core multi-agent system and implemented 10 responsible AI safeguards
before adding any other complexity. Establishes the security and safety baseline.

### What was implemented

#### 1.1 Multi-agent orchestrator
- Orchestrator pattern — central LLM classifies intent and delegates to
  specialist agents (weather, hotel).

#### 1.2 Responsible AI plan
- Created RESPONSIBLE_AI.md with 10 prioritized safeguards based on
  OWASP Top 10 for LLM Applications.

#### 1.3 Input validation & sanitization
- Max input length (500 chars) — prevents cost abuse
- Control character stripping + unicode normalization
- Tool-level validation: city names (alpha only), dates (YYYY-MM-DD)
- Defense in depth — validate at the entry point AND at each tool

#### 1.4 Prompt injection defense
- **3-layer defense model:**
  - **Layer 1 — Pattern detection (pre-LLM):** Regex scanner blocks known
    injection phrases before they reach the LLM
  - **Layer 2 — Hardened system prompts (in-LLM):** Explicit security
    instructions in all agents to resist role changes and instruction overrides
  - **Layer 3 — Output format verification (post-LLM):** Orchestrator output
    must match expected format — if not, treated as compromised
- Input boundary markers (`[USER_MESSAGE_START]...[USER_MESSAGE_END]`)

#### 1.5 Output validation
- Response length cap (2000 chars)
- PII redaction (credit cards, SSNs, emails, phone numbers)
- Hallucination disclaimer auto-appended to price/booking claims

#### 1.6 Content moderation
- Tier 1 — Harmful content: hard block (violence, weapons, drugs, fraud)
- Tier 2 — Off-topic categories: gentle redirect (medical, legal, financial)

#### 1.7 Error handling
- Sanitized error messages — never expose raw stack traces
- Retry with exponential backoff for transient failures
- Graceful degradation — partial failures don't discard good results

#### 1.8 Chat history limits
- Sliding window: last 20 user/assistant pairs
- History sanitization before storage

#### 1.9 Logging & audit trail
- Structured JSON logging with session IDs
- Logs events/timing/outcomes, never full user input or LLM responses (PII risk)
- Log levels: INFO (normal), WARNING (blocked), ERROR (failures)

#### 1.10 Fairness guardrails
- Bias-aware system prompts: equal quality for all destinations/demographics
- Diverse mock data across price points and property types

#### 1.11 Transparency & disclosure
- AI disclosure at startup with capability boundaries
- Hallucination disclaimers on specific claims
- Exit message reinforcement

#### 1.12 Dependency pinning
- Pinned `requirements.txt` + full `requirements.lock`

### Full safety pipeline

```
User Input
  → Input validation (length, encoding, characters)        ← 1.3
    → Prompt injection detection (pattern matching)        ← 1.4
      → Content moderation (harmful + off-topic)           ← 1.6
        → LLM call with hardened prompts + boundaries      ← 1.4
          → Retry with exponential backoff                 ← 1.7
            → Output format verification                  ← 1.4
              → Output validation (length, PII, disclaimer)← 1.5
                → Graceful degradation (BOTH: queries)     ← 1.7
                  → Chat history trim + sanitize           ← 1.8
                    → Structured logging at every step     ← 1.9
                      → Response to user

Cross-cutting: Fairness (1.10) · Transparency (1.11) · Dependency security (1.12)
```

---

## Phase 2: Production Code Quality (planned)

**Goal:** Refactor from a single-file prototype to a modular, testable, well-typed
codebase.

**Planned work:**
- Modular file structure (agents/, tools/, validation/, config/)
- Pydantic models for all data (replace hand-rolled validation)
- Unit tests with pytest (target: 80%+ coverage)
- Type hints throughout
- **Key concepts:** SOLID principles, dependency injection, test pyramid

---

## Phase 3: API Layer (planned)

**Goal:** Expose the agent as a web service. Shift from CLI to production-ready API.

**Planned work:**
- FastAPI web server with REST endpoints
- Pydantic request/response models
- API authentication (API keys → JWT)
- Async agent execution
- **Key concepts:** REST API design, async/await, authentication patterns

---

## Phase 4: Observability & Reliability (planned)

**Goal:** Make the system debuggable, monitorable, and resilient to failures.

**Planned work:**
- Structured JSON logging with correlation IDs
- LLM observability (LangSmith or OpenTelemetry)
- Retry with exponential backoff
- Circuit breaker pattern
- **Key concepts:** Observability vs. monitoring, distributed tracing, resilience patterns

---

## Phase 5: Deployment & Infrastructure (planned)

**Goal:** Containerize and automate deployment.

**Planned work:**
- Dockerfile (multi-stage build)
- docker-compose for local dev
- GitHub Actions CI/CD pipeline
- Environment management (dev/staging/prod)
- Rate limiting
- **Key concepts:** Containers, CI/CD, infrastructure-as-code, twelve-factor app

---

## Phase 6: Advanced AI Patterns (planned)

**Goal:** Add production AI capabilities that demonstrate deep understanding.

**Planned work:**
- RAG with vector database (travel knowledge base)
- Streaming responses (token-by-token)
- Session memory with Redis or SQLite
- Evaluation framework (how to measure agent quality)
- **Key concepts:** RAG architecture, embeddings, vector search, LLM evaluation

---

## Architecture Decisions Log

| # | Decision | Chosen | Alternative considered | Why |
|---|----------|--------|----------------------|-----|
| 1 | LLM framework | LangChain + LangGraph | Raw OpenAI SDK, LlamaIndex | LangChain has the richest agent tooling; LangGraph adds stateful workflows when needed |
| 2 | Agent routing | Orchestrator pattern (LLM-based classification) | Keyword matching, embeddings-based router | LLM classification handles ambiguous queries; keyword matching is brittle |
| 3 | Validation approach (Phase 1) | Hand-rolled functions | Pydantic from the start | Learn the fundamentals first, then refactor to framework in Phase 2 |
| 4 | Single file (Phase 1) | One agent.py | Modular from the start | Reduces complexity while learning; modularize in Phase 2 when patterns are clear |
