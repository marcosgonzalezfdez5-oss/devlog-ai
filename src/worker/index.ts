import { Worker } from "bullmq";
import { connection } from "../queue/client.js";
import { processDocJob } from "./processor.js";
import type { JobPayload } from "../queue/types.js";

const worker = new Worker<JobPayload>(
  "doc-generation",
  async (job) => processDocJob(job.data),
  { connection, concurrency: 3 }
);

worker.on("completed", (job) => {
  console.log(`[worker] job ${job.id} completed`);
});

worker.on("failed", (job, err) => {
  console.error(`[worker] job ${job?.id} failed:`, err.message);
});

console.log("[worker] DevLogAI doc-generation worker started");
