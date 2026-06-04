# DevLogAI

Automatically keeps project documentation up to date by monitoring GitHub pull requests and generating documentation updates as reviewable pull requests. "DevLogAI keeps your docs honest."

Built for the **Band of Agents Hackathon** (lablab.ai, June 12–19, 2026). Multi-agent requirement: minimum 3 agents coordinating through Band SDK.
Also targeting **Gemini for XPRIZE Hackathon** (deadline: August 17, 2026) — Gemini API satisfies the Google Cloud requirement.

---

## Architecture

```
GitHub webhook → Hono receiver → BullMQ queue → Worker
                                                    ↓
                                         [Band SDK orchestration]
                                                    ↓
                                        CoordinatorAgent (fetches PR data)
                                                    ↓
                                        AnalyzerAgent (Gemini: what changed?)
                                                    ↓
                                         WriterAgent (Gemini: write the docs)
                                                    ↓
                                          GitHub Doc PR created
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
| Agent coordination | Band SDK (`BAND_MODE=mock` before kick-off, `BAND_MODE=live` after) |
| AI | Gemini 2.5 Flash (`@google/generative-ai`) |
| GitHub | GitHub App + Octokit (`@octokit/app`, `@octokit/rest`) |
| Hosting (backend) | Railway |
| Hosting (frontend) | Vercel |
| Testing | Vitest |

---

## Project Structure

```
src/
  webhook/
    index.ts                  # Hono app entry
    routes/github.ts          # POST /webhooks/github
    routes/health.ts
    middleware/verify-github.ts  # HMAC-SHA256 signature check
  worker/
    index.ts                  # BullMQ worker entry
    processor.ts              # calls band.runPipeline, updates DB
  agents/
    band.ts                   # Band SDK abstraction (mock + live, BAND_MODE env switch)
    coordinator.ts            # fetches PR data, orchestrates pipeline, creates Doc PR
    analyzer.ts               # Gemini: analyze diff → AnalysisResult
    writer.ts                 # Gemini: write docs → DocContent
  github/
    client.ts                 # Octokit per-installation auth
    pr.ts                     # fetchPRMetadata, fetchPRDiff, createDocPR
    files.ts                  # readFile, createOrUpdateFile
  ai/
    client.ts                 # Gemini client factory
    analyzer-prompt.ts        # prompt builder + diff trimming logic
    writer-prompt.ts          # prompt builder from AnalysisResult
    schemas.ts                # Zod schemas for structured Gemini output
  db/
    schema.ts                 # Drizzle: installations, repositories, jobs
    client.ts
    migrations/
    queries/
      jobs.ts
      repos.ts
      installations.ts
  queue/
    client.ts                 # BullMQ Queue instance
    types.ts                  # JobPayload type
  config/
    parser.ts                 # devlogai.yml parser (js-yaml)
    defaults.ts               # fallback config when .yml missing
  types/
    agents.ts                 # AnalysisResult, DocContent, AgentRun
    github.ts                 # webhook payload types

frontend/
  app/
    page.tsx                  # minimal landing page
    dashboard/page.tsx        # job list (last 50, auto-refresh 10s)
    dashboard/jobs/[id]/page.tsx  # agent timeline + Doc PR link
  components/
    job-list.tsx
    agent-timeline.tsx        # 3-step stepper: Coordinator → Analyzer → Writer
    status-badge.tsx
  lib/
    api.ts                    # fetch wrapper to backend
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
- **jobs** — `id`, `repository_id` (FK), `source_pr_number`, `status`, `agent_runs` (JSONB), `doc_pr_number`, `error`, `created_at`, `completed_at`

`agent_runs` shape:
```ts
Array<{
  agent_name: "coordinator" | "analyzer" | "writer";
  started_at: string;       // ISO timestamp
  completed_at: string;
  input_summary: string;    // one-line description of input
  output_summary: string;   // one-line description of output
  status: "completed" | "failed";
  error?: string;
}>
```

The `jobs` table is the audit log and the source for dashboard metrics.

---

## Agent Architecture

### Band SDK Abstraction (`src/agents/band.ts`)

Exports `createBandOrchestrator(config)` → `{ runPipeline(job): Promise<PipelineResult> }`.

- **`BAND_MODE=mock`** — runs the 3 agent functions sequentially in-process, passing typed objects. Used Days 1–4 before Band credentials arrive at the June 12 kick-off.
- **`BAND_MODE=live`** — wraps each function as a Band SDK agent. Band handles message-passing, retries, context propagation.

Both modes produce identical `agent_runs` log entries so the dashboard renders correctly in either mode.

### CoordinatorAgent (`src/agents/coordinator.ts`)

- Authenticate Octokit for the installation
- Fetch PR metadata (title, body, labels, commit messages)
- Fetch PR diff, apply diff trimming: prioritize `routes/`, `api/`, `*.config.*`, public interfaces; drop `*.lock`, `tests/`, `*.snap`
- Pass `{ prMetadata, diff }` → AnalyzerAgent
- Receive `AnalysisResult` → pass with `prMetadata` → WriterAgent
- Receive `DocContent` → read current `CHANGELOG.md` + `RELEASE_NOTES.md`, prepend entries, create branch `devlogai/docs-pr-<prNumber>`, commit, open Doc PR

### AnalyzerAgent (`src/agents/analyzer.ts`)

Calls Gemini 2.5 Flash with structured output. Returns:
```ts
{
  affected_apis: string[];
  config_changes: string[];
  public_interface_changes: string[];
  confidence_score: number; // 0–1
  reasoning: string;
}
```

### WriterAgent (`src/agents/writer.ts`)

Calls Gemini 2.5 Flash with structured output. Returns:
```ts
{
  changelog_entry: string;
  release_notes: string;
}
```

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

MVP supports `batching: per-pr` only.

---

## Trigger Filtering

Skip job creation when:
- Merged PR has an ignored label
- All changed files match ignored path patterns
- PR title matches a conventional commit prefix in the ignore list

This avoids unnecessary Gemini calls.

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

## Dashboard

**`/dashboard`** — job table: `Created | Repository | Source PR | Status | Doc PR link`. Auto-refresh every 10s (polling, no websockets).

**`/dashboard/jobs/[id]`** — agent timeline:
```
[1] Coordinator Agent  ✓ completed  1.2s   Fetched PR #42, 847 lines across 12 files
[2] Analyzer Agent     ✓ completed  8.4s   Confidence: 0.87 · 3 public APIs changed
[3] Writer Agent       ✓ completed  6.1s   changelog entry + release notes generated

Doc PR: #103 — docs: update documentation for merged PR #42  [View on GitHub ↗]
```

---

## Testing

Vitest only. Three integration tests covering the critical path:

1. Webhook ingestion → job enqueued
2. `runAnalyzerAgent` → returns `AnalysisResult` matching Zod schema (mock Gemini)
3. `createDocPR` → correct branch name + PR title format (mock Octokit)

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

# Band SDK
BAND_API_KEY=
BAND_MODE=mock   # or "live"

# App
APP_URL=
```

---

## MVP Scope

In scope:
- Changelog generation
- Release notes generation
- Documentation PRs (per-PR mode)
- 3-agent Band SDK pipeline (Coordinator → Analyzer → Writer)
- Landing page
- Post-install dashboard (repos, job history, agent timeline)

Post-MVP:
- README maintenance (tagged sections only)
- Shadow Mode comment on source PR
- Batching modes (daily digest, release candidate)
- Stripe billing
- Broken link detection
- Style voice matching
- API documentation generation
- Confluence / Notion / Jira integrations
