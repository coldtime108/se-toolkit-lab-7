# Development Plan — Lab 7 Telegram Bot

## Overview

This document outlines the development plan for building a Telegram bot that allows users to interact with the LMS (Learning Management System) backend through natural language and commands. The bot uses an LLM (Large Language Model) for intent classification and routes user requests to appropriate backend endpoints.

## Architecture

The bot follows a layered architecture:

1. **Transport Layer** (`bot.py`): Handles Telegram API communication via aiogram framework
2. **Handler Layer** (`handlers/`): Pure functions that process commands and return responses
3. **Service Layer** (`services/`): API clients for LMS backend and LLM

This separation ensures that handlers are testable without Telegram API access, enabling the `--test` mode.

## Task Breakdown

### Task 1: Plan and Scaffold (P0)

**Goal:** Create project structure and implement testable architecture.

**Deliverables:**
- `bot/` directory with proper structure
- `bot.py` entry point with `--test` mode support
- `handlers/` module with command handlers
- `services/` module with API clients
- `config.py` for environment variable management
- `pyproject.toml` for dependency management
- `PLAN.md` (this document)

**Acceptance Criteria:**
- `cd bot && uv sync` succeeds
- `uv run bot.py --test "/start"` prints welcome message
- All P0 commands return placeholder responses

### Task 2: Backend Integration (P0)

**Goal:** Connect handlers to real LMS backend data.

**Implementation:**
- Implement `LMSClient` class with methods:
  - `health_check()` — GET /health
  - `get_labs()` — GET /items/ (filter by type="lab")
  - `get_scores(lab_id)` — GET /analytics/tasks/?lab_id=X
- Update handlers to use `LMSClient` instead of placeholders
- Add error handling for backend unavailability

**Acceptance Criteria:**
- `/health` reports actual backend status
- `/labs` lists real labs from the database
- `/scores lab-01` shows actual pass rates
- Backend down produces friendly error message

### Task 3: Intent-Based Natural Language Routing (P1)

**Goal:** Enable plain language interaction via LLM.

**Implementation:**
- Implement `LLMClient` class for LLM API communication
- Create intent classification prompt that maps user messages to commands
- Add message handler that:
  1. Receives plain text
  2. Sends to LLM for classification
  3. Routes to appropriate handler based on LLM response
- Add inline keyboard buttons for common actions

**Acceptance Criteria:**
- "What labs are available?" → triggers /labs
- "Check if the system is working" → triggers /health
- "Show me scores for lab 4" → triggers /scores lab-04
- All 9 backend endpoints accessible via natural language

### Task 4: Containerize and Document (P3)

**Goal:** Deploy bot on VM with Docker.

**Implementation:**
- Create `bot/Dockerfile` for containerization
- Add bot service to `docker-compose.yml`
- Configure environment variables for production
- Update README with deployment documentation

**Dockerfile Structure:**
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install uv && uv sync --frozen
COPY . .
CMD ["uv", "run", "bot.py"]
```

**Acceptance Criteria:**
- Bot runs as Docker service
- Accessible via Telegram
- README documents setup and deployment

## Development Workflow

1. **Plan**: Use AI coding agent to design each component
2. **Implement**: Write code with agent assistance
3. **Test**: Verify with `--test` mode locally
4. **Deploy**: Push to VM and test in Telegram
5. **Iterate**: Fix issues and add features

## Testing Strategy

### Local Testing
```bash
cd bot
uv sync
uv run bot.py --test "/start"
uv run bot.py --test "/help"
uv run bot.py --test "/health"
uv run bot.py --test "/labs"
uv run bot.py --test "/scores lab-01"
```

### Telegram Testing
1. Deploy bot on VM
2. Send commands via Telegram
3. Verify responses match expected behavior

### Integration Testing
- Backend down scenario
- Invalid lab ID for /scores
- Ambiguous natural language queries

## Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Scaffold | 1-2 hours | Project structure, --test mode |
| Backend Integration | 2-3 hours | Working P0 commands |
| LLM Integration | 3-4 hours | Natural language routing |
| Deployment | 1-2 hours | Docker container, VM deployment |

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| LLM API unavailable | Fallback to command-only mode |
| Backend connection fails | Friendly error messages, retry logic |
| Docker build fails | Use same base image as backend |
| Telegram rate limits | Implement request throttling |

## Success Metrics

1. All P0 commands work with real data
2. Natural language queries correctly routed >80% of time
3. Bot responds within 5 seconds
4. Zero crashes when backend is down
5. Successfully deployed and accessible via Telegram
