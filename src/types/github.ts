export interface GitHubWebhookPayload {
  action: string;
  pull_request: {
    number: number;
    title: string;
    body: string | null;
    merged: boolean;
    merged_at: string | null;
    labels: Array<{ name: string }>;
    user: { login: string };
    head: { ref: string; sha: string };
    base: { ref: string; repo: { full_name: string } };
  };
  repository: {
    id: number;
    full_name: string;
    private: boolean;
  };
  installation: {
    id: number;
  };
}
