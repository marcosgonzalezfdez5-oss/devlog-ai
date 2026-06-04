import { Hono } from "hono";
import { verifyGitHubWebhook } from "../middleware/verify-github.js";
import { upsertInstallation, getInstallationByGithubId } from "../../db/queries/installations.js";
import { upsertRepository, getRepositoryByFullName } from "../../db/queries/repos.js";
import { createJob } from "../../db/queries/jobs.js";
import { docQueue } from "../../queue/client.js";
import { parseConfig, shouldSkipPR } from "../../config/parser.js";
import { DEFAULT_CONFIG } from "../../config/defaults.js";
import type { GitHubWebhookPayload } from "../../types/github.js";

const github = new Hono();

github.post("/", verifyGitHubWebhook, async (c) => {
  const event = c.req.header("x-github-event");
  if (event !== "pull_request") return c.text("ok");

  const payload: GitHubWebhookPayload = JSON.parse(c.get("rawBody") as string);
  if (payload.action !== "closed" || !payload.pull_request.merged) return c.text("ok");

  const { installation, repository, pull_request: pr } = payload;

  const installRow = await upsertInstallation({
    githubInstallId: installation.id,
    accountLogin: repository.full_name.split("/")[0]!,
    accountType: "Organization",
  });

  const repoRow = await upsertRepository({
    installationId: installRow.id,
    fullName: repository.full_name,
  });

  const config = repoRow.config
    ? parseConfig(JSON.stringify(repoRow.config))
    : DEFAULT_CONFIG;

  const labels = pr.labels.map((l) => l.name);
  if (shouldSkipPR(config, labels, [])) return c.text("ok");

  const job = await createJob({ repositoryId: repoRow.id, sourcePrNumber: pr.number });

  await docQueue.add("generate-docs", {
    jobId: job.id,
    repoId: repoRow.id,
    installationId: installation.id,
    repoFullName: repository.full_name,
    prNumber: pr.number,
  });

  return c.json({ queued: true, jobId: job.id });
});

export default github;
