# Contributing to Spending Transaction Monitor

Thank you for your interest in contributing! Your help keeps this project strong, usable, and evolving.

This document outlines how to prepare your contributions, what conventions to follow, and how to get your changes merged.

---

## 🧰 Branching Strategy

- Use one of the allowed prefixes for branch names:  
  `feat/`, `fix/`, `chore/`, `docs/`, `refactor/`, `test/`, `ci/`, `build/`, `perf/`
- Examples:  
  `feat/user‑endpoints`  
  `fix/health‑timeout`
- Branch naming is enforced via Git hooks (`prepare-commit-msg` and `pre-push`).

---

## 📝 Commit Message Guidelines

- Follow **Conventional Commits** format.  
- Some examples:  
  - `feat(api): add transactions POST`  
  - `fix(db): correct alembic URL driver`  
  - `chore(ui): update dependencies`  
- Constraints:  
  - Subject header must be ≤ 100 characters.  
  - Commit linting is enforced via hook (commit-msg) and also on pre-push for all commits since upstream.

---

## 🔍 Pre‑commit and Pre‑push Hooks

- **pre-commit** (runs on staged changes only):  
  - UI: `Prettier --write` and `ESLint` on changed JavaScript/TypeScript/React files  
  - API: `ruff format` and `ruff check` for changed Python files
- **pre-push** (runs more extensive checks across the repo):  
  - Rejects non-conventional branch names  
  - Runs `commitlint` on all commits since upstream  
  - Runs formatting, linting, and tests via e.g.  
    ```bash
    pnpm format:check
    pnpm lint
    pnpm test
    ```

---

## 🛠 Local Setup

1. Requirements:  
   - Node.js (v18+)  
   - pnpm (v9+)  
   - Python 3.11+  
   - [Any other prerequisites: Docker, etc.]  
2. Install dependencies and prepare local dev environment:  
   ```bash
   pnpm setup
   ```

---

## ▶️ Running the Stack Locally

- Start the database & apply migrations / seed data:  
  ```bash
  pnpm db:start
  pnpm db:upgrade
  pnpm db:seed
  ```
- Run the API:  
  ```bash
  pnpm --filter @spending-monitor/api dev
  ```
- Run the UI:  
  ```bash
  pnpm --filter @spending-monitor/ui dev
  ```

---

## 🧪 Testing

- To run all tests:  
  ```bash
  pnpm test
  ```

---

## 🧮 Database Migrations

- To create a new migration:  
  ```bash
  pnpm db:revision -m "add table xyz"
  ```
- To apply migrations:  
  ```bash
  pnpm db:upgrade
  ```

---

## 🔄 Releases

- Releases are automated via `semantic-release` in CI, driven by commit messages.  
- Branches used:  
  - `main` (for stable / production releases)  
  - `next` (for pre‑release or upcoming changes)

---

## 🤝 Pull Requests

When submitting a PR, please:

- Keep PRs scoped and focused (small where possible).  
- Ensure all CI checks pass.  
- Provide context in the description: **What** you changed and **why**.  
- If your change affects the UI, include screenshots or screen recordings.  
- Reference related issues (if any), using `#<issue-number>`.

---

## 📜 Code of Conduct & Licensing

- Please follow the project’s **Code of Conduct** (if one exists).  
- Contributions are under the same license as this project. By submitting a contribution, you agree to license it under the project’s **Apache License 2.0** (or your relevant license).

---

Again, thanks for wanting to contribute—your work helps the project improve!  
