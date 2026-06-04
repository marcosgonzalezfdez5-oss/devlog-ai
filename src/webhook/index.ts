import { serve } from "@hono/node-server";
import { Hono } from "hono";
import githubRoutes from "./routes/github.js";
import healthRoutes from "./routes/health.js";

const app = new Hono();

app.route("/health", healthRoutes);
app.route("/webhooks/github", githubRoutes);

app.get("/api/jobs", async (c) => {
  const { listRecentJobs } = await import("../db/queries/jobs.js");
  const jobList = await listRecentJobs(50);
  return c.json(jobList);
});

app.get("/api/jobs/:id", async (c) => {
  const { getJobById } = await import("../db/queries/jobs.js");
  const id = parseInt(c.req.param("id"), 10);
  const job = await getJobById(id);
  if (!job) return c.notFound();
  return c.json(job);
});

const port = parseInt(process.env.PORT ?? "3000", 10);
serve({ fetch: app.fetch, port }, () => {
  console.log(`[web] DevLogAI webhook receiver running on port ${port}`);
});

export default app;
