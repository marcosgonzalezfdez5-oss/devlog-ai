import type { PRMetadata, PRDiff, DiffFile } from "../types/agents.js";

const PRIORITY_PATTERNS = [/routes?\//i, /api\//i, /\.config\./i, /index\.[tj]sx?$/, /cli\.[tj]sx?$/];
const SKIP_PATTERNS = [/\.lock$/, /\.snap$/, /tests?\//i, /__tests__\//i, /\.test\.[tj]sx?$/];
const MAX_PATCH_CHARS = 3000;

function trimDiff(diff: PRDiff): DiffFile[] {
  const prioritized = diff.files.filter((f) => !SKIP_PATTERNS.some((p) => p.test(f.filename)));
  const sorted = [
    ...prioritized.filter((f) => PRIORITY_PATTERNS.some((p) => p.test(f.filename))),
    ...prioritized.filter((f) => !PRIORITY_PATTERNS.some((p) => p.test(f.filename))),
  ];
  return sorted.map((f) => ({
    ...f,
    patch: f.patch.length > MAX_PATCH_CHARS ? f.patch.slice(0, MAX_PATCH_CHARS) + "\n... [trimmed]" : f.patch,
  }));
}

export function buildAnalyzerPrompt(pr: PRMetadata, diff: PRDiff): string {
  const files = trimDiff(diff);
  const diffText = files
    .map((f) => `### ${f.filename} (${f.status}, +${f.additions}/-${f.deletions})\n\`\`\`diff\n${f.patch}\n\`\`\``)
    .join("\n\n");

  return `You are a senior engineer analyzing a merged pull request to identify what changed for documentation purposes.

## PR #${pr.number}: ${pr.title}

**Author:** ${pr.authorLogin}
**Description:** ${pr.body || "(no description)"}
**Commits:**
${pr.commitMessages.map((m) => `- ${m}`).join("\n")}

## Changed Files (${diff.files.length} total, ${diff.totalAdditions} additions, ${diff.totalDeletions} deletions)

${diffText}

## Task
Analyze the diff above and identify:
1. Affected public APIs or endpoints (list specific names/routes, empty array if none)
2. Configuration variable changes (new/removed/renamed env vars or config keys, empty array if none)
3. Public interface changes (exported types, function signatures, CLI flags, empty array if none)
4. Confidence score (0–1): how certain you are this PR has user-facing documentation impact
5. Reasoning: one paragraph explaining what changed and why it matters for docs

Return a JSON object matching the provided schema.`;
}
