import { eq } from "drizzle-orm";
import { db } from "../client.js";
import { installations } from "../schema.js";

export async function upsertInstallation(data: {
  githubInstallId: number;
  accountLogin: string;
  accountType: string;
}) {
  const [row] = await db
    .insert(installations)
    .values(data)
    .onConflictDoUpdate({
      target: installations.githubInstallId,
      set: { accountLogin: data.accountLogin, accountType: data.accountType },
    })
    .returning();
  return row!;
}

export async function getInstallationByGithubId(githubInstallId: number) {
  return db.query.installations.findFirst({
    where: eq(installations.githubInstallId, githubInstallId),
  });
}
