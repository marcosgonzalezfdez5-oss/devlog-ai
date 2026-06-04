import type { PRMetadata, AnalysisResult } from "../types/agents.js";

export function buildWriterPrompt(pr: PRMetadata, analysis: AnalysisResult): string {
  return `You are a technical writer generating documentation updates for a merged pull request.

## PR #${pr.number}: ${pr.title}

**Author:** ${pr.authorLogin}
**Merged at:** ${pr.mergedAt}

## Analysis Summary
- Affected APIs: ${analysis.affected_apis.join(", ") || "none"}
- Config changes: ${analysis.config_changes.join(", ") || "none"}
- Interface changes: ${analysis.public_interface_changes.join(", ") || "none"}
- Confidence: ${analysis.confidence_score}
- Reasoning: ${analysis.reasoning}

## Task
Generate two documentation outputs:

1. **changelog_entry**: A concise Keep-a-Changelog style entry (one or two bullet points under the appropriate heading: Added/Changed/Fixed/Removed/Deprecated). Use present tense. Be specific about what changed, not how.

2. **release_notes**: A brief user-facing release note (1–3 sentences). Written for end users, not developers. No jargon. State what they can now do, or what was fixed.

Return a JSON object matching the provided schema.`;
}
