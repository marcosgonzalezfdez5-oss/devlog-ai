import { App } from "@octokit/app";
import { Octokit } from "@octokit/rest";

const app = new App({
  appId: process.env.GITHUB_APP_ID!,
  privateKey: process.env.GITHUB_APP_PRIVATE_KEY!.replace(/\\n/g, "\n"),
  webhooks: { secret: process.env.GITHUB_WEBHOOK_SECRET! },
});

export async function getInstallationOctokit(installationId: number): Promise<Octokit> {
  return app.getInstallationOctokit(installationId) as unknown as Octokit;
}
