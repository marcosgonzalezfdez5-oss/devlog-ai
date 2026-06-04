import { runCoordinatorAgent } from "./coordinator.js";
import type { JobPayload, PipelineResult } from "../types/agents.js";

export interface BandOrchestrator {
  runPipeline(payload: JobPayload): Promise<PipelineResult>;
}

export function createBandOrchestrator(): BandOrchestrator {
  const mode = process.env.BAND_MODE ?? "mock";
  return mode === "live" ? createLiveOrchestrator() : createMockOrchestrator();
}

function createMockOrchestrator(): BandOrchestrator {
  return {
    async runPipeline(payload: JobPayload): Promise<PipelineResult> {
      return runCoordinatorAgent(payload);
    },
  };
}

function createLiveOrchestrator(): BandOrchestrator {
  // TODO: Fill in Band SDK live integration after June 12 kick-off.
  // Band SDK will wrap each agent function (coordinator, analyzer, writer) as a
  // registered Band agent, with message-passing and context propagation handled by Band.
  // Until then, fall back to mock mode.
  console.warn("[band] BAND_MODE=live not yet configured — falling back to mock");
  return createMockOrchestrator();
}
