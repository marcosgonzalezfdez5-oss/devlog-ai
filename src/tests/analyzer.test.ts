import { describe, it, expect, vi } from "vitest";
import { readFileSync } from "fs";
import { join } from "path";
import { fileURLToPath } from "url";
import { AnalysisResultSchema } from "../ai/schemas.js";

const __dirname = fileURLToPath(new URL(".", import.meta.url));
const diffFixture = JSON.parse(readFileSync(join(__dirname, "fixtures/pr-diff.json"), "utf-8"));

const mockAnalysis = {
  affected_apis: ["/api/users"],
  config_changes: ["JWT_SECRET"],
  public_interface_changes: ["authMiddleware"],
  confidence_score: 0.9,
  reasoning: "PR adds JWT authentication middleware and applies it to API routes.",
};

vi.mock("../ai/client.js", () => ({
  getGeminiModel: () => ({
    generateContent: vi.fn().mockResolvedValue({
      response: { text: () => JSON.stringify(mockAnalysis) },
    }),
  }),
}));

const prMetadata = {
  number: 42,
  title: "Add user authentication",
  body: "Implements JWT-based auth",
  labels: [],
  commitMessages: ["feat: add JWT auth middleware"],
  authorLogin: "testuser",
  mergedAt: "2026-06-12T10:00:00Z",
};

describe("AnalyzerAgent", () => {
  it("returns a valid AnalysisResult matching the schema", async () => {
    const { runAnalyzerAgent } = await import("../agents/analyzer.js");
    const result = await runAnalyzerAgent(prMetadata, diffFixture);

    expect(() => AnalysisResultSchema.parse(result)).not.toThrow();
    expect(result.confidence_score).toBeGreaterThan(0);
    expect(result.affected_apis).toContain("/api/users");
  });
});
