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
- `requirements.txt` — Python dependencies (unpinned)
- `RESPONSIBLE_AI.md` — responsible AI implementation plan and status tracker

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

- CLI-only (no web server yet)
- All tool data is mocked (no real APIs connected)
- No tests, no logging, no error handling
- Responsible AI safeguards are being implemented (see RESPONSIBLE_AI.md)

## Conventions

- Single-file application for now; will modularize as complexity grows
- Mock tools return hardcoded data — will be replaced with real API calls later
- Environment variables stored in `.env` (git-ignored)