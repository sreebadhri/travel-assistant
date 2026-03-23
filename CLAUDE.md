# Travel Assistant — AI Agent

## Overview

A multi-agent travel assistant powered by LangChain and OpenAI. Uses an orchestrator
pattern to route user queries to specialist agents (weather, hotel). Currently a CLI
application with plans to go to production.

## Architecture

- **Orchestrator agent** — classifies user intent and routes to the right specialist
- **Weather agent** — handles weather queries (currently returns mock data)
- **Hotel agent** — handles hotel search and booking (currently returns mock data)
- All agents use OpenAI `gpt-4o-mini` via LangChain

## Key Files

- `agent.py` — entire application (agents, tools, routing, CLI loop)
- `requirements.txt` — Python dependencies (pinned)
- `requirements.lock` — full dependency tree lockfile
- `ARCHITECTURE.md` — roadmap, decisions log, and implementation details
- `RESPONSIBLE_AI.md` — responsible AI safeguard reference (risks + mitigations)
- `notes/` — personal study notes (git-ignored)

## Tech Stack

- Python 3.12
- LangChain + LangGraph (agent framework)
- OpenAI API (LLM provider)
- python-dotenv (env config)

## Running

```bash
source venv/bin/activate
python agent.py
```

## Current State

- Phase 1 complete — all 10 responsible AI safeguards implemented
- CLI-only (no web server yet)
- All tool data is mocked (no real APIs connected)
- Structured logging, error handling with retry, PII redaction all in place
- See ARCHITECTURE.md for full roadmap and status

## Conventions

- Single-file application for now; will modularize as complexity grows
- Mock tools return hardcoded data — will be replaced with real API calls later
- Environment variables stored in `.env` (git-ignored)