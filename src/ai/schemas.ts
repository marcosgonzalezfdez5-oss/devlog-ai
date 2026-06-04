import { z } from "zod";

export const AnalysisResultSchema = z.object({
  affected_apis: z.array(z.string()),
  config_changes: z.array(z.string()),
  public_interface_changes: z.array(z.string()),
  confidence_score: z.number().min(0).max(1),
  reasoning: z.string(),
});

export const DocContentSchema = z.object({
  changelog_entry: z.string(),
  release_notes: z.string(),
});

export type AnalysisResultSchema = z.infer<typeof AnalysisResultSchema>;
export type DocContentSchema = z.infer<typeof DocContentSchema>;

export const geminiAnalysisSchema = {
  type: "object",
  properties: {
    affected_apis: { type: "array", items: { type: "string" } },
    config_changes: { type: "array", items: { type: "string" } },
    public_interface_changes: { type: "array", items: { type: "string" } },
    confidence_score: { type: "number" },
    reasoning: { type: "string" },
  },
  required: ["affected_apis", "config_changes", "public_interface_changes", "confidence_score", "reasoning"],
};

export const geminiDocSchema = {
  type: "object",
  properties: {
    changelog_entry: { type: "string" },
    release_notes: { type: "string" },
  },
  required: ["changelog_entry", "release_notes"],
};
