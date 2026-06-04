export interface DevLogAIConfig {
  changelog: string;
  release_notes: string;
  batching: "per-pr";
  ignore_labels: string[];
  ignore_paths: string[];
}

export const DEFAULT_CONFIG: DevLogAIConfig = {
  changelog: "CHANGELOG.md",
  release_notes: "RELEASE_NOTES.md",
  batching: "per-pr",
  ignore_labels: ["chore", "docs", "test"],
  ignore_paths: ["tests/**", "*.lock"],
};
