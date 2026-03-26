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

## Current runnable scope

The project already supports a lightweight local flow where you can:

- view real world state on `/`
- advance the world from the frontend
- read and post in the default group chat on `/chat`
- read and post in the default moments feed on `/moments`
- inspect director data on `/director`

## Docker deployment

The repository now includes a cloud-oriented `docker-compose.yml` for:

- `web`
- `api`
- `postgres`
- `redis`

For Ubuntu server deployment:

1. Copy `.env.example` to `.env`
2. Run `docker compose up -d --build`
3. Open `/`, `/chat`, `/moments`, `/director` from the server domain or IP

Detailed instructions are in [docs/ubuntu-docker-deployment.md](docs/ubuntu-docker-deployment.md).

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
- explicit frontend API base URL pointing to `http://127.0.0.1:8000/api`

### Recommended local startup

For the current “basic runnable” state, the fastest path is:

```powershell
./scripts/local/start-light-dev.ps1 -WithWeb
```

After startup, open:

- `http://127.0.0.1:3000/` for world overview and world advance
- `http://127.0.0.1:3000/chat` for the minimal group chat page
- `http://127.0.0.1:3000/moments` for the minimal moments page
- `http://127.0.0.1:3000/director` for the director panel

### Frontend API base URL

The frontend defaults to `http://127.0.0.1:8000/api` in lightweight local mode.

If you need to override it manually, copy:

- `apps/web/.env.local.example`

to `apps/web/.env.local` and adjust `NEXT_PUBLIC_API_BASE_URL`.
