import { createBandOrchestrator } from "../agents/band.js";
import { updateJobRunning, updateJobCompleted, updateJobFailed } from "../db/queries/jobs.js";
import type { JobPayload } from "../queue/types.js";

const orchestrator = createBandOrchestrator();

export async function processDocJob(payload: JobPayload): Promise<void> {
  await updateJobRunning(payload.jobId);

  const agentRuns = [] as NonNullable<Parameters<typeof updateJobCompleted>[1]["agentRuns"]>;

  try {
    const result = await orchestrator.runPipeline(payload);
    await updateJobCompleted(payload.jobId, {
      agentRuns: result.agent_runs,
      docPrNumber: result.doc_pr_number,
    });
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    await updateJobFailed(payload.jobId, { agentRuns, error: message });
    throw err;
  }
}
