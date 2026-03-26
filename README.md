# MutilAgentsRolePlay

MutilAgentsRolePlay is a modular multi-AI roleplay and social simulation project. The V1 goal is to let 6-10 AI characters live inside a single-user world where they can talk in groups, send private messages, post moments, update plans, and react to the user.

## Repository layout

```text
docs/                     Project docs and V1 blueprint
apps/web/                 Next.js web client
services/api/             FastAPI backend
packages/shared-contracts/ Shared TypeScript contracts
```

## V1 architecture

- Web + single-user single-world
- Next.js + TypeScript frontend
- Python + FastAPI backend
- PostgreSQL + Redis + WebSocket runtime plan
- State-driven AI runtime with interchangeable thinking and permission policies

## Main extension points

- `ThinkingEngine`: change how AI decides and reacts
- `PermissionPolicy`: change what the user can see and control
- `WorkflowRunner`: future hook for LangGraph or other orchestration layers
- `LLMClient`: future hook for model provider integrations

## Next steps

1. Install frontend dependencies in `apps/web`
2. Create a Python virtual environment for `services/api`
3. Start PostgreSQL and Redis with `docker compose up -d postgres redis`
4. Start implementing domain logic from the V1 blueprint in `docs/v1-solution-and-blueprint.md`

## Infrastructure

The repository includes a `docker-compose.yml` file for PostgreSQL, Redis, and the API service. Copy `.env.example` to `.env` before starting containers on a server or local machine.

## Lightweight local mode

For a low-resource personal machine workflow, use the local scripts in `scripts/local`:

```powershell
./scripts/local/start-light-dev.ps1
./scripts/local/start-light-dev.ps1 -WithWeb
./scripts/local/stop-light-dev.ps1
./scripts/local/run-backend-tests.ps1
```

This mode uses:

- Python 3.12 virtual environment in `.venv`
- SQLite database in `.local`
- local API process instead of Dockerized backend
