import { Queue } from "bullmq";
import IORedis from "ioredis";
import type { JobPayload } from "./types.js";

export const connection = new IORedis(process.env.REDIS_URL!, {
  maxRetriesPerRequest: null,
});

export const docQueue = new Queue<JobPayload>("doc-generation", { connection });
