import type { Octokit } from "@octokit/rest";
import type { PRMetadata, PRDiff, DiffFile } from "../types/agents.js";

export async function fetchPRMetadata(octokit: Octokit, owner: string, repo: string, prNumber: number): Promise<PRMetadata> {
  const [{ data: pr }, { data: commits }] = await Promise.all([
    octokit.pulls.get({ owner, repo, pull_number: prNumber }),
    octokit.pulls.listCommits({ owner, repo, pull_number: prNumber, per_page: 50 }),
  ]);

  return {
    number: pr.number,
    title: pr.title,
    body: pr.body ?? "",
    labels: pr.labels.map((l) => l.name),
    commitMessages: commits.map((c) => c.commit.message),
    authorLogin: pr.user?.login ?? "unknown",
    mergedAt: pr.merged_at ?? "",
  };
}

export async function fetchPRDiff(octokit: Octokit, owner: string, repo: string, prNumber: number): Promise<PRDiff> {
  const { data: files } = await octokit.pulls.listFiles({
    owner,
    repo,
    pull_number: prNumber,
    per_page: 100,
  });

  const diffFiles: DiffFile[] = files.map((f) => ({
    filename: f.filename,
    status: f.status as DiffFile["status"],
    additions: f.additions,
    deletions: f.deletions,
    patch: f.patch ?? "",
  }));

  return {
    files: diffFiles,
    totalAdditions: diffFiles.reduce((sum, f) => sum + f.additions, 0),
    totalDeletions: diffFiles.reduce((sum, f) => sum + f.deletions, 0),
  };
}

export async function createDocPR(
  octokit: Octokit,
  owner: string,
  repo: string,
  sourcePrNumber: number,
  files: Array<{ path: string; content: string }>,
  prBody: string
): Promise<{ number: number; html_url: string }> {
  const branch = `devlogai/docs-pr-${sourcePrNumber}`;
  const title = `docs: update documentation for merged PR #${sourcePrNumber}`;

  const { data: refData } = await octokit.git.getRef({ owner, repo, ref: "heads/main" });
  const baseSha = refData.object.sha;

  await octokit.git.createRef({ owner, repo, ref: `refs/heads/${branch}`, sha: baseSha });

  for (const file of files) {
    let existingSha: string | undefined;
    try {
      const { data } = await octokit.repos.getContent({ owner, repo, path: file.path, ref: branch });
      if (!Array.isArray(data) && "sha" in data) existingSha = data.sha;
    } catch {}

    await octokit.repos.createOrUpdateFileContents({
      owner,
      repo,
      path: file.path,
      message: `docs: update ${file.path} for PR #${sourcePrNumber}`,
      content: Buffer.from(file.content).toString("base64"),
      branch,
      ...(existingSha ? { sha: existingSha } : {}),
    });
  }

  const { data: pr } = await octokit.pulls.create({
    owner,
    repo,
    title,
    body: prBody,
    head: branch,
    base: "main",
  });

  return { number: pr.number, html_url: pr.html_url };
}
