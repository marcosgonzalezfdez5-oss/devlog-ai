import { getGeminiModel } from "../ai/client.js";
import { buildWriterPrompt } from "../ai/writer-prompt.js";
import { DocContentSchema, geminiDocSchema } from "../ai/schemas.js";
import type { PRMetadata, AnalysisResult, DocContent } from "../types/agents.js";

export async function runWriterAgent(pr: PRMetadata, analysis: AnalysisResult): Promise<DocContent> {
  const model = getGeminiModel();
  const prompt = buildWriterPrompt(pr, analysis);

  const result = await model.generateContent({
    contents: [{ role: "user", parts: [{ text: prompt }] }],
    generationConfig: {
      responseMimeType: "application/json",
      responseSchema: geminiDocSchema as never,
    },
  });

  const raw = JSON.parse(result.response.text());
  return DocContentSchema.parse(raw);
}
