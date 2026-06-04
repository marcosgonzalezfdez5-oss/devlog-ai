import { fetchJob } from "../../../../lib/api";
import AgentTimeline from "../../../../components/agent-timeline";

export default async function JobDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const job = await fetchJob(id);

  return (
    <div className="max-w-3xl mx-auto px-6 py-10 space-y-8">
      <div className="space-y-1">
        <div className="text-sm text-gray-400">{job.repository?.fullName}</div>
        <h1 className="text-2xl font-semibold">Job #{job.id}</h1>
        <div className="text-gray-400 text-sm">Source PR #{job.sourcePrNumber}</div>
      </div>

      <AgentTimeline agentRuns={job.agentRuns ?? []} />

      {job.docPrNumber && (
        <div className="border border-green-900 bg-green-950/30 rounded-lg p-4 flex items-center justify-between">
          <div>
            <div className="text-sm text-gray-400">Documentation PR</div>
            <div className="font-medium">
              docs: update documentation for merged PR #{job.sourcePrNumber}
            </div>
          </div>
          <a
            href={`https://github.com/${job.repository?.fullName}/pull/${job.docPrNumber}`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-green-400 hover:underline whitespace-nowrap"
          >
            #{job.docPrNumber} View on GitHub ↗
          </a>
        </div>
      )}

      {job.error && (
        <div className="border border-red-900 bg-red-950/30 rounded-lg p-4">
          <div className="text-sm text-red-400 font-medium mb-1">Error</div>
          <pre className="text-xs text-gray-300 whitespace-pre-wrap">{job.error}</pre>
        </div>
      )}
    </div>
  );
}
