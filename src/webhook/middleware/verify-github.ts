import { createHmac, timingSafeEqual } from "crypto";
import type { Context, Next } from "hono";

export async function verifyGitHubWebhook(c: Context, next: Next) {
  const signature = c.req.header("x-hub-signature-256");
  if (!signature) return c.text("Missing signature", 401);

  const body = await c.req.text();
  const expected = "sha256=" + createHmac("sha256", process.env.GITHUB_WEBHOOK_SECRET!).update(body).digest("hex");

  const sigBuffer = Buffer.from(signature);
  const expBuffer = Buffer.from(expected);
  if (sigBuffer.length !== expBuffer.length || !timingSafeEqual(sigBuffer, expBuffer)) {
    return c.text("Invalid signature", 401);
  }

  c.set("rawBody", body);
  await next();
}
