import { describe, it, expect, vi, beforeEach } from "vitest";
import { createHmac } from "crypto";
import { readFileSync } from "fs";
import { join } from "path";
import { fileURLToPath } from "url";

const __dirname = fileURLToPath(new URL(".", import.meta.url));
const fixture = JSON.parse(readFileSync(join(__dirname, "fixtures/pr-webhook.json"), "utf-8"));

vi.mock("../db/queries/installations.js", () => ({
  upsertInstallation: vi.fn().mockResolvedValue({ id: 1, githubInstallId: 99 }),
  getInstallationByGithubId: vi.fn(),
}));
vi.mock("../db/queries/repos.js", () => ({
  upsertRepository: vi.fn().mockResolvedValue({ id: 1, fullName: "testorg/testrepo", config: null }),
  getRepositoryByFullName: vi.fn(),
}));
vi.mock("../db/queries/jobs.js", () => ({
  createJob: vi.fn().mockResolvedValue({ id: 7, repositoryId: 1, sourcePrNumber: 42 }),
  listRecentJobs: vi.fn().mockResolvedValue([]),
  getJobById: vi.fn(),
  updateJobRunning: vi.fn(),
  updateJobCompleted: vi.fn(),
  updateJobFailed: vi.fn(),
}));
vi.mock("../queue/client.js", () => ({
  docQueue: { add: vi.fn().mockResolvedValue({ id: "bullmq-1" }) },
  connection: {},
}));

process.env.GITHUB_WEBHOOK_SECRET = "test-secret";

const { default: app } = await import("../webhook/index.js");

function makeSignature(body: string): string {
  return "sha256=" + createHmac("sha256", "test-secret").update(body).digest("hex");
}

describe("webhook ingestion", () => {
  it("enqueues a job when a merged PR webhook arrives", async () => {
    const body = JSON.stringify(fixture);
    const res = await app.request("/webhooks/github", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-github-event": "pull_request",
        "x-hub-signature-256": makeSignature(body),
      },
      body,
    });

    expect(res.status).toBe(200);
    const json = await res.json() as { queued: boolean; jobId: number };
    expect(json.queued).toBe(true);
    expect(json.jobId).toBe(7);

    const { docQueue } = await import("../queue/client.js");
    expect(docQueue.add).toHaveBeenCalledWith(
      "generate-docs",
      expect.objectContaining({ prNumber: 42, repoFullName: "testorg/testrepo" })
    );
  });

  it("rejects webhooks with invalid signatures", async () => {
    const body = JSON.stringify(fixture);
    const res = await app.request("/webhooks/github", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-github-event": "pull_request",
        "x-hub-signature-256": "sha256=invalidsignature",
      },
      body,
    });
    expect(res.status).toBe(401);
  });
});
