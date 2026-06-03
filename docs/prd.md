# Product Requirements Document (PRD)

## Product Name

DevLogAI (Working Title)

## Vision

Engineering teams frequently neglect documentation because maintaining it is manual, repetitive, and disconnected from development workflows.

DevLogAI automatically keeps project documentation up to date by monitoring GitHub pull requests and generating documentation updates as reviewable pull requests.

The goal is not to generate documentation from scratch, but to ensure documentation never falls behind the codebase.

**Positioning:** "DevLogAI keeps your docs honest." DevLogAI is a maintenance tool, not a generation tool — this is the defensible differentiator against GitHub Copilot and similar incumbents.

---

# Competitive Landscape

## Direct Competitors

* Mintlify
* Swimm
* Stenography

## Primary Threat

GitHub Copilot is the biggest risk. If GitHub builds "Generate Documentation" natively into the merge flow, DevLogAI loses its primary moat.

## Differentiation

DevLogAI must understand how a PR changes the *existing* documentation structure, not just summarize the PR in isolation. Surgical, context-aware updates beat generic summaries.

---

# Problem Statement

Developers regularly merge features, bug fixes, and API changes without updating documentation.

This leads to:

* Outdated README files
* Missing release notes
* Incomplete changelogs
* Difficult onboarding
* Increased support burden
* Reduced knowledge sharing

Documentation maintenance is considered important but is rarely prioritized.

---

# Target Users

## Primary Users

* Software engineers
* Engineering managers
* Technical leads

## Secondary Users

* Software consultancies
* Startup engineering teams
* Open-source maintainers

---

# MVP Objective

Automatically generate and maintain project documentation after pull requests are merged.

The MVP focuses exclusively on GitHub repositories.

No Confluence.
No Jira.
No Notion.
No architecture diagrams.

---

# User Journey

## Installation

1. User installs GitHub App
2. User selects repositories
3. Documentation rules are initialized

---

## Development Flow

1. Developer merges PR
2. GitHub webhook triggers DevLogAI
3. Agent analyzes:

   * PR title
   * PR description
   * Commit history
   * Changed files
4. Agent generates documentation updates
5. Agent opens a Documentation PR
6. Team reviews and merges

---

# Core Features

## Feature 1: Automated Changelog Generation

### Description

Generate changelog entries based on merged pull requests.

### Input

* PR title
* PR description
* Commit messages

### Output

Update:

```markdown
## Added
- Visitor pre-registration workflow

## Fixed
- Vehicle validation issue
```

### Success Criteria

Generated changelog accepted with minimal edits.

---

## Feature 2: Release Notes Generation

### Description

Generate release notes for each merged feature.

### Output

```markdown
# Release Notes

## New Features
- Visitor pre-registration

## Improvements
- Improved vehicle validation
```

### Success Criteria

Can be directly used in GitHub releases.

---

## Feature 3: README Maintenance

### Description

Detect changes affecting public project usage and suggest README updates.

### Scope Constraint

README updates are limited to **DevLogAI-tagged sections** only. The AI must not modify untagged content, to avoid formatting destruction and reduce hallucination risk.

Teams opt in by adding tags to their README:

```markdown
<!-- DevLogAI-env-vars-start -->
| Variable | Description |
|---|---|
<!-- DevLogAI-env-vars-end -->
```

### Examples

Detect:

* New API endpoints
* New configuration variables
* New installation steps
* New CLI commands

### Success Criteria

README tagged sections remain aligned with current functionality. No untagged content is ever modified.

---

## Feature 5: Shadow Mode

### Description

Before opening a Documentation PR, post a comment on the *original* feature PR with the proposed documentation changes.

The developer can review and approve the doc update before the code is even merged, tightening the feedback loop.

### Requirements

* Comment is posted on the source PR when the documentation analysis is complete
* Comment includes a preview of proposed changes and a confidence score
* If the PR is merged without approval, DevLogAI opens the Doc PR as normal

### Success Criteria

Developers engage with shadow mode comments, reducing edit cycles on the resulting Doc PR.

---

## Feature 6: Batching Mode

### Description

Instead of opening a Documentation PR for every merged PR, allow teams to aggregate changes into a single batched update.

### Modes

* **Per-PR mode** (default): One Doc PR per merged feature PR
* **Daily Digest mode**: One Doc PR per day, aggregating all merges
* **Release Candidate mode**: One Doc PR per GitHub Release, compiling all Doc PRs since the last release into polished release notes

### Requirements

When a Doc PR is already open and another feature merges, the bot updates the *existing* Doc PR rather than creating a new one (in batching modes).

### Success Criteria

Teams using Daily Digest or Release Candidate mode report lower notification fatigue than Per-PR mode.

---

## Feature 4: Documentation Pull Requests

### Description

All generated changes must be submitted through a dedicated PR.

### Requirements

PR title example:

```text
docs: update documentation for merged feature #184
```

PR body includes:

* Summary
* Files modified
* Confidence score
* Source code snippets used as the basis for each generated documentation change (for traceability and hallucination detection)

### Race Condition Handling

If multiple PRs are merged in quick succession, DevLogAI must not open conflicting Doc PRs. In Per-PR mode, each Doc PR targets a unique branch. In batching modes, subsequent merges update the existing open Doc PR rather than creating a new one.

### Success Criteria

No automatic commits to main branch.

Human review always required.

---

# Functional Requirements

## GitHub Integration

Must support:

* Repository installation
* Webhooks
* Pull request events
* Repository cloning
* PR creation

---

## Configuration

Each repository must include a `DevLogAI.yml` file (auto-generated on install) that defines:

* Changelog format (e.g., Keep a Changelog, conventional commits)
* File paths for CHANGELOG.md, RELEASE_NOTES.md
* Batching mode (per-pr / daily / release)
* Trigger filters (labels to ignore, file path patterns to skip)
* DevLogAI-tagged sections in README

Example:

```yaml
changelog: CHANGELOG.md
release_notes: RELEASE_NOTES.md
batching: daily
ignore_labels:
  - chore
  - docs
  - test
ignore_paths:
  - "tests/**"
  - "*.lock"
```

---

## AI Analysis Engine

Must:

* Understand code changes
* Summarize functionality
* Detect user-facing changes
* Generate Markdown
* Apply diff trimming for large PRs — when a PR exceeds a configurable file/line threshold, prioritize changed public interfaces, API routes, config files, and CLI entry points over internal implementation files

Must not:

* Modify source code
* Merge pull requests
* Edit README content outside DevLogAI-tagged sections

---

## Trigger Filtering

DevLogAI must skip documentation generation when:

* The merged PR has an ignored label (e.g., `chore`, `test`, `docs`)
* All changed files match ignored path patterns (e.g., `tests/**`, `*.lock`)
* The PR title matches a conventional commit prefix in the ignore list

This avoids unnecessary LLM calls and reduces notification noise.

---

## Documentation Engine

Supported files:

* README.md (tagged sections only)
* CHANGELOG.md
* RELEASE_NOTES.md

Excluded from MVP:

* Confluence
* Notion
* Architecture diagrams
* User manuals

---

# Non-Functional Requirements

## Performance

Documentation PR generated within:

* Target: < 2 minutes
* Maximum: 5 minutes

---

## Reliability

Target:

* 95% successful processing

**Definition of failure:** A processing attempt counts as failed if it results in a timeout, an unhandled exception, or an API error that prevents a Doc PR from being opened. Silent wrong output (plausible but incorrect documentation) is tracked separately via the Documentation Acceptance Rate metric.

---

## Security

* Read-only repository access where possible
* Write access scoped to `contents: write` on `.md` files and `pull-requests: write` only
* No code modifications outside documentation files
* Clear data retention policy: customer source code is not used for model training
* Enterprise data handling stance must be documented before beta launch

---

# Success Metrics

## Product Metrics

### Documentation Adoption Rate

Percentage of generated documentation PRs merged.

Target:

* > 60%

---

### Documentation Acceptance Rate

Percentage of generated text accepted without major edits.

Target:

* > 70%

---

### Time Saved

Estimated documentation effort saved.

Target:

* 10–30 minutes per merged PR

---

### Weekly Active Repositories

Repositories receiving at least one generated documentation update.

Target:

* 50 repositories during beta

---

# Out of Scope

The following are intentionally excluded from the MVP:

* Architecture diagrams
* Mermaid generation
* User manuals
* Confluence synchronization
* Notion synchronization
* Jira integration
* Slack integration
* Documentation search
* Knowledge base generation
* Multi-language documentation

---

# Future Roadmap

## V2

* Broken link and outdated info detection — scan README and flag sections that are no longer accurate based on recent code changes
* Style voice — analyze the team's last 10 changelog entries to learn writing style (tone, format, emoji usage) and match it in generated output
* API documentation generation
* Documentation quality scoring
* Mermaid diagrams

## V3

* User manual generation
* Confluence synchronization
* Notion synchronization
* Jira synchronization
* Architecture decision records (ADRs)

## V4

* Autonomous documentation maintenance
* Knowledge graph creation
* Organization-wide documentation intelligence
* Developer onboarding assistant
