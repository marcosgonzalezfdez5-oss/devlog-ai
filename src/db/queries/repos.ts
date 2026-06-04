import { eq } from "drizzle-orm";
import { db } from "../client.js";
import { repositories } from "../schema.js";

export async function upsertRepository(data: {
  installationId: number;
  fullName: string;
  config?: unknown;
}) {
  const [row] = await db
    .insert(repositories)
    .values(data)
    .onConflictDoUpdate({
      target: repositories.fullName,
      set: { installationId: data.installationId, active: true },
    })
    .returning();
  return row!;
}

export async function getRepositoryByFullName(fullName: string) {
  return db.query.repositories.findFirst({
    where: eq(repositories.fullName, fullName),
  });
}
