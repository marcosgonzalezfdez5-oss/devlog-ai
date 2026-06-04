import { eq, desc } from "drizzle-orm";
import { db } from "../client.js";
import { jobs } from "../schema.js";
import type { AgentRun } from "../../types/agents.js";

export async function createJob(data: {
  repositoryId: number;
  sourcePrNumber: number;
}) {
  const [row] = await db.insert(jobs).values(data).returning();
  return row!;
}

export async function updateJobRunning(id: number) {
  const [row] = await db
    .update(jobs)
    .set({ status: "running" })
    .where(eq(jobs.id, id))
    .returning();
  return row!;
}

export async function updateJobCompleted(id: number, data: {
  agentRuns: AgentRun[];
  docPrNumber: number;
}) {
  const [row] = await db
    .update(jobs)
    .set({ status: "completed", agentRuns: data.agentRuns, docPrNumber: data.docPrNumber, completedAt: new Date() })
    .where(eq(jobs.id, id))
    .returning();
  return row!;
}

export async function updateJobFailed(id: number, data: {
  agentRuns: AgentRun[];
  error: string;
}) {
  const [row] = await db
    .update(jobs)
    .set({ status: "failed", agentRuns: data.agentRuns, error: data.error, completedAt: new Date() })
    .where(eq(jobs.id, id))
    .returning();
  return row!;
}

export async function getJobById(id: number) {
  return db.query.jobs.findFirst({ where: eq(jobs.id, id) });
}

export async function listRecentJobs(limit = 50) {
  return db.query.jobs.findMany({
    orderBy: [desc(jobs.createdAt)],
    limit,
    with: { repository: true },
  });
}
