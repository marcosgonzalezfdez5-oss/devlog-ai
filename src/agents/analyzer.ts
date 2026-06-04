import { getGeminiModel } from "../ai/client.js";
import { buildAnalyzerPrompt } from "../ai/analyzer-prompt.js";
import { AnalysisResultSchema, geminiAnalysisSchema } from "../ai/schemas.js";
import type { PRMetadata, PRDiff, AnalysisResult } from "../types/agents.js";

export async function runAnalyzerAgent(pr: PRMetadata, diff: PRDiff): Promise<AnalysisResult> {
  const model = getGeminiModel();
  const prompt = buildAnalyzerPrompt(pr, diff);

  const result = await model.generateContent({
    contents: [{ role: "user", parts: [{ text: prompt }] }],
    generationConfig: {
      responseMimeType: "application/json",
      responseSchema: geminiAnalysisSchema as never,
    },
  });

  const raw = JSON.parse(result.response.text());
  return AnalysisResultSchema.parse(raw);
}
