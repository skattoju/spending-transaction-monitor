# Contributing

Thank you for contributing! This monorepo uses a few conventions and guardrails to keep quality high and changes easy to review.

## Branching

- Use conventional branch names:
  - Allowed prefixes: `feat/`, `fix/`, `chore/`, `docs/`, `refactor/`, `test/`, `ci/`, `build/`, `perf/`
  - Examples: `feat/user-endpoints`, `fix/health-timeout`
- Branch name is enforced in hooks (prepare-commit-msg and pre-push).

## Commit messages

- Follow Conventional Commits. Examples:
  - `feat(api): add transactions POST`
  - `fix(db): correct Alembic URL driver`
  - `chore(ui): update deps`
- Constraints:
  - Subject header max length: 100 characters
- Enforced by commitlint (commit-msg hook) and also re-checked on pre-push for all commits since upstream.

## Pre-commit and pre-push hooks

- pre-commit (only runs on staged changes):
  - UI: Prettier write and ESLint on changed files
  - API: Ruff format and Ruff check on changed Python files
- pre-push (repo-wide checks and policy checks):
  - Rejects non-conventional branch names
  - Runs commitlint over commit range since upstream
  - Runs `pnpm format:check`, `pnpm lint`, and `pnpm test`

## Local setup

- Requirements: Node 18+, pnpm 9+, Python 3.11+, uv, Docker
- Install everything:
```bash
pnpm setup
```

## Running the stack

- Database
```bash
pnpm db:start
pnpm db:upgrade
pnpm db:seed
```
- API
```bash
pnpm --filter @spending-monitor/api dev
```
- UI
```bash
pnpm --filter @spending-monitor/ui dev
```

## Tests

- Run all tests:
```bash
pnpm test
```

## Migrations

- Create a migration:
```bash
pnpm db:revision -m "add table xyz"
pnpm db:upgrade
```

## Releases

- Releases are automated with semantic-release in CI based on commit messages.
- Branches: `main` (stable), `next` (pre-release).

## Pull Requests

- Keep PRs scoped and small where possible
- Ensure CI checks pass
- Include context in the description (what/why)
- If UI changes, include screenshots

Thanks again for helping improve the project!
