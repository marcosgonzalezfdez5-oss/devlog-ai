import type { AgentRun } from "../lib/api";
import StatusBadge from "./status-badge";

const AGENT_LABELS: Record<string, string> = {
  coordinator: "Coordinator Agent",
  analyzer: "Analyzer Agent",
  writer: "Writer Agent",
};

function durationMs(run: AgentRun): string {
  const ms = new Date(run.completed_at).getTime() - new Date(run.started_at).getTime();
  return ms >= 1000 ? `${(ms / 1000).toFixed(1)}s` : `${ms}ms`;
}

export default function AgentTimeline({ agentRuns }: { agentRuns: AgentRun[] }) {
  const ordered: AgentRun[] = ["coordinator", "analyzer", "writer"].map(
    (name) => agentRuns.find((r) => r.agent_name === name) ?? {
      agent_name: name as AgentRun["agent_name"],
      started_at: "",
      completed_at: "",
      input_summary: "",
      output_summary: "Waiting...",
      status: "completed" as const,
    }
  );

  return (
    <div className="space-y-3">
      {ordered.map((run, i) => (
        <div key={run.agent_name} className="border border-gray-800 rounded-lg p-4 space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-xs text-gray-600 font-mono w-5">[{i + 1}]</span>
              <span className="font-medium">{AGENT_LABELS[run.agent_name]}</span>
              <StatusBadge status={agentRuns.find((r) => r.agent_name === run.agent_name) ? run.status : "pending"} />
            </div>
            {run.started_at && (
              <span className="text-xs text-gray-500">{durationMs(run)}</span>
            )}
          </div>
          {run.output_summary && (
            <p className="text-sm text-gray-400 pl-8">{run.output_summary}</p>
          )}
          {run.error && (
            <p className="text-xs text-red-400 pl-8">{run.error}</p>
          )}
        </div>
      ))}
    </div>
  );
}
