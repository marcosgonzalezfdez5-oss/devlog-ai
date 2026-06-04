export interface PRMetadata {
  number: number;
  title: string;
  body: string;
  labels: string[];
  commitMessages: string[];
  authorLogin: string;
  mergedAt: string;
}

export interface PRDiff {
  files: DiffFile[];
  totalAdditions: number;
  totalDeletions: number;
}

export interface DiffFile {
  filename: string;
  status: "added" | "removed" | "modified" | "renamed";
  additions: number;
  deletions: number;
  patch: string;
}

export interface AnalysisResult {
  affected_apis: string[];
  config_changes: string[];
  public_interface_changes: string[];
  confidence_score: number;
  reasoning: string;
}

export interface DocContent {
  changelog_entry: string;
  release_notes: string;
}

export interface AgentRun {
  agent_name: "coordinator" | "analyzer" | "writer";
  started_at: string;
  completed_at: string;
  input_summary: string;
  output_summary: string;
  status: "completed" | "failed";
  error?: string;
}

export interface PipelineResult {
  doc_pr_number: number;
  doc_pr_url: string;
  agent_runs: AgentRun[];
}

export interface JobPayload {
  jobId: string;
  repoId: number;
  installationId: number;
  repoFullName: string;
  prNumber: number;
}
