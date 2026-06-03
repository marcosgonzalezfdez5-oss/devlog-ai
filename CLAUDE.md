# DevLogAI

Automatically keeps project documentation up to date by monitoring GitHub pull requests and generating documentation updates as reviewable pull requests. "DevLogAI keeps your docs honest."

Built for the **Gemini for XPRIZE Hackathon** (deadline: August 17, 2026). Must use at least one Google Cloud product → Gemini API is the AI engine.

---

## Architecture

Hybrid: a webhook receiver responds to GitHub immediately (enqueues a job), and a separate long-running worker processes jobs asynchronously. Both services are deployed on Railway from the same repo with different start commands.

```
GitHub webhook → Hono receiver → BullMQ queue → Worker → Gemini 2.5 Flash → GitHub PR
```

Three Railway services: `web` (Hono), `worker` (BullMQ), plus managed `Postgres` and `Redis` addons.
Frontend (Next.js) is deployed separately on Vercel.

---

## Stack

| Layer | Choice |
|---|---|
| Backend | TypeScript + Node.js + Hono |
| Frontend | Next.js (App Router) + Tailwind CSS + shadcn/ui |
| Database | PostgreSQL + Drizzle ORM |
| Queue | BullMQ + Redis |
| AI | Gemini 2.5 Flash (`@google/generative-ai`) |
| GitHub | GitHub App + Octokit (`@octokit/app`, `@octokit/rest`) |
| Payments | Stripe Checkout |
| Hosting (backend) | Railway |
| Hosting (frontend) | Vercel |
| Testing | Vitest |

---

## Project Structure

```
src/
  webhook/     # Hono routes + GitHub webhook verification + event routing
  worker/      # BullMQ worker + job processors
  github/      # Octokit client, PR creation, repo cloning
  ai/          # Gemini prompt builder + structured output parsing
  db/          # Drizzle schema + query functions
  config/      # devlogai.yml parser + defaults
frontend/
  app/         # Next.js App Router pages (landing, dashboard)
  components/  # shadcn/ui components
```

---

## Development Commands

```bash
# Install dependencies
npm install

# Start webhook receiver (dev)
npm run dev:web

# Start worker (dev)
npm run dev:worker

# Run database migrations
npm run db:migrate

# Run tests
npm test

# Type check
npm run typecheck
```

---

## Database Schema

Three tables — no users table (identity comes from GitHub App installation):

- **installations** — `id`, `github_install_id`, `account_login`, `account_type`, `created_at`
- **repositories** — `id`, `installation_id` (FK), `full_name`, `config` (JSONB), `active`, `created_at`
- **jobs** — `id`, `repository_id` (FK), `source_pr_number`, `status`, `gemini_response` (JSONB), `doc_pr_number`, `error`, `created_at`, `completed_at`

The `jobs` table is the audit log and the source for product metrics (acceptance rate, time saved).

---

## AI Analysis Engine

One Gemini 2.5 Flash call per job. Use structured output (response schema) to enforce a typed JSON response:

```ts
{
  changelog_entry: string;
  release_notes: string;
  readme_updates: Array<{ section_tag: string; content: string }>;
  confidence_score: number; // 0–1
  affected_files: string[];
  reasoning: string;
}
```

Never chain multiple LLM calls in a single job — one call, one structured response.

For large PRs, apply diff trimming: prioritize changed public interfaces, API routes, config files, and CLI entry points over internal implementation files.

---

## GitHub App

Permissions required:
- `contents: write` (scoped to `.md` files only)
- `pull_requests: write`
- `metadata: read`

Webhook events: `pull_request: closed` (merged only).

On install: open a PR adding a default `devlogai.yml` to the repo root.
If `devlogai.yml` is missing when a webhook fires: fall back to defaults (per-PR mode, `CHANGELOG.md`, no ignored labels) — never fail.

---

## Configuration (`devlogai.yml`)

Auto-generated on GitHub App install. Example:

```yaml
changelog: CHANGELOG.md
release_notes: RELEASE_NOTES.md
batching: per-pr
ignore_labels:
  - chore
  - docs
  - test
ignore_paths:
  - "tests/**"
  - "*.lock"
```

MVP supports `batching: per-pr` only. Daily digest and release candidate modes are post-MVP.

---

## Trigger Filtering

Skip job creation when:
- Merged PR has an ignored label
- All changed files match ignored path patterns
- PR title matches a conventional commit prefix in the ignore list

This avoids unnecessary Gemini calls.

---

## README Maintenance Constraint

README updates are limited to DocPilot-tagged sections only. Never modify untagged content.

```markdown
<!-- devlogai-env-vars-start -->
...
<!-- devlogai-env-vars-end -->
```

---

## Documentation PR Format

PR title: `docs: update documentation for merged PR #<number>`

PR body must include:
- Summary of changes
- Files modified
- Confidence score
- Source code snippets used as the basis for each change (traceability)

Each Doc PR targets a unique branch (`devlogai/docs-pr-<source-pr-number>`).

---

## Payments

Stripe Checkout with a single paid tier ($19/mo, unlimited repos). Free tier: first repo only.
GitHub App install flow → post-install redirect → Stripe paywall after free repo limit.

---

## Testing

Vitest only. Three integration tests covering the critical path:

1. Webhook ingestion → job enqueued
2. Job processor → correct Gemini prompt built from PR data
3. GitHub PR creation → correct files modified

No unit tests for helpers. No coverage thresholds. Use recorded fixtures for GitHub/Gemini responses so tests run offline.

---

## Environment Variables

```
# GitHub App
GITHUB_APP_ID=
GITHUB_APP_PRIVATE_KEY=
GITHUB_WEBHOOK_SECRET=

# Gemini
GEMINI_API_KEY=

# Database
DATABASE_URL=

# Redis
REDIS_URL=

# Stripe
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
STRIPE_PRICE_ID=

# App
APP_URL=
```

---

## MVP Scope

In scope:
- Changelog generation
- Release notes generation
- README maintenance (tagged sections only)
- Documentation PRs (per-PR mode)
- Shadow Mode comment on source PR
- Landing page + pricing
- Post-install dashboard (repos, job history, Doc PR status)
- Stripe billing

Post-MVP:
- Batching modes (daily digest, release candidate)
- Shadow Mode approval flow
- Broken link detection
- Style voice matching
- API documentation generation
- Confluence / Notion / Jira integrations
