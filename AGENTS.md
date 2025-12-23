# Repository Guidelines

## Project Structure & Module Organization
- `backend/` holds the FastAPI service; core code lives in `backend/app/` with `routes/`, `services/`, `models.py`, and `schemas.py`.
- `frontend/` is a React + Vite app; pages live in `frontend/src/pages/` and API calls in `frontend/src/api.js`.
- `database/init.sql` initializes PostgreSQL.
- `docs/` contains product and integration guides.
- Utility scripts `start`, `stop`, `status`, and `update` wrap Docker Compose workflows.
- `docker-compose.yml` wires services; `images/` is used for stored coin images.

## Build, Test, and Development Commands
- `./start` starts the full stack; use `./start -b` to rebuild images.
- `./stop` stops containers; `./stop -v` also removes volumes (data loss).
- `./status` shows service state; `./update` syncs submodules.
- `./test` runs tests in Docker; use `./test -t frontend|backend|e2e|api` for specific suites.
- Backend dev: `cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && uvicorn app.main:app --reload`.
- Frontend dev: `cd frontend && npm install && npm run dev`.
- Frontend build check: `cd frontend && npm run build`.

## Coding Style & Naming Conventions
- Indentation is 4 spaces in both Python and JSX; follow existing formatting and avoid reformatting unrelated files.
- Python uses `snake_case` for modules/functions; keep route handlers in `backend/app/routes/`.
- React components use `PascalCase` and live under `frontend/src/pages/` or `frontend/src/components/` (when added).
- TailwindCSS classes are used for styling; keep class lists readable and grouped logically.

## Testing Guidelines
- Backend tests use pytest: `cd backend && pytest`.
- Frontend unit tests use Vitest: `cd frontend && npm run test`.
- E2E tests use Playwright: `cd frontend && npx playwright install && npm run test:e2e`.
- The `./test` script runs tests in Docker and stores results under `backend/.test-results` and `frontend/.test-results`.
- For manual verification, run `./start` and hit `http://localhost:8000/health` plus the UI at `http://localhost:3000`.
- Keep test names descriptive (e.g., `test_coins_api.py`).

## Commit & Pull Request Guidelines
- Commit messages generally follow a conventional style like `chore: update ...`; keep them short and imperative.
- PRs should include a concise description, testing notes, and screenshots for UI changes; link relevant issues when possible.

## Configuration & Secrets
- Use `.env` for local configuration; start from `.env.example`.
- Never commit API keys (Gemini, eBay); verify required keys are documented in `README.md`.
