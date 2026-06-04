import type { Octokit } from "@octokit/rest";

export async function readFile(octokit: Octokit, owner: string, repo: string, path: string): Promise<string> {
  try {
    const { data } = await octokit.repos.getContent({ owner, repo, path });
    if (Array.isArray(data) || !("content" in data)) return "";
    return Buffer.from(data.content, "base64").toString("utf-8");
  } catch {
    return "";
  }
}
