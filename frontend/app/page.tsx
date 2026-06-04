import Link from "next/link";

export default function LandingPage() {
  return (
    <div className="max-w-3xl mx-auto px-6 py-24 space-y-12">
      <div className="space-y-4">
        <div className="inline-block text-xs font-medium bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded px-2 py-1">
          Band of Agents Hackathon
        </div>
        <h1 className="text-5xl font-bold tracking-tight">
          DevLogAI keeps your docs honest.
        </h1>
        <p className="text-xl text-gray-400">
          When you merge a pull request, a 3-agent AI pipeline automatically generates changelog entries,
          release notes, and opens a documentation PR for your team to review.
        </p>
      </div>

      <div className="flex gap-4">
        <a
          href="https://github.com/apps/devlogai"
          className="bg-white text-gray-900 font-medium px-5 py-2.5 rounded-lg hover:bg-gray-100 transition-colors"
        >
          Install on GitHub
        </a>
        <Link
          href="/dashboard"
          className="border border-gray-700 text-gray-300 font-medium px-5 py-2.5 rounded-lg hover:border-gray-500 hover:text-white transition-colors"
        >
          View Dashboard
        </Link>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {[
          { label: "Coordinator Agent", desc: "Fetches PR data and orchestrates the pipeline" },
          { label: "Analyzer Agent", desc: "Uses Gemini to understand what changed and why" },
          { label: "Writer Agent", desc: "Generates changelog and release notes" },
        ].map((agent, i) => (
          <div key={i} className="border border-gray-800 rounded-lg p-4 space-y-2">
            <div className="text-xs text-blue-400 font-medium">Agent {i + 1}</div>
            <div className="font-medium">{agent.label}</div>
            <div className="text-sm text-gray-500">{agent.desc}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
