const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:3000";

export interface Job {
  id: number;
  sourcePrNumber: number;
  status: "pending" | "running" | "completed" | "failed";
  docPrNumber: number | null;
  error: string | null;
  createdAt: string;
  completedAt: string | null;
  agentRuns: AgentRun[] | null;
  repository: { fullName: string } | null;
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

export async function fetchJobs(): Promise<Job[]> {
  const res = await fetch(`${BASE}/api/jobs`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch jobs");
  return res.json();
}

export async function fetchJob(id: string): Promise<Job> {
  const res = await fetch(`${BASE}/api/jobs/${id}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch job");
  return res.json();
}
