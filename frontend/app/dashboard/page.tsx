"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchJobs, type Job } from "../../lib/api";
import StatusBadge from "../../components/status-badge";

export default function DashboardPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = () => fetchJobs().then(setJobs).catch((e) => setError(e.message));
    load();
    const interval = setInterval(load, 10_000);
    return () => clearInterval(interval);
  }, []);

  if (error) return <div className="p-6 text-red-400">Error: {error}</div>;

  return (
    <div className="max-w-5xl mx-auto px-6 py-10 space-y-6">
      <h1 className="text-2xl font-semibold">Documentation Jobs</h1>

      <div className="border border-gray-800 rounded-lg overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-900 text-gray-400 text-left">
            <tr>
              <th className="px-4 py-3">Created</th>
              <th className="px-4 py-3">Repository</th>
              <th className="px-4 py-3">Source PR</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Doc PR</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800">
            {jobs.length === 0 && (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-gray-500">
                  No jobs yet. Merge a PR to get started.
                </td>
              </tr>
            )}
            {jobs.map((job) => (
              <tr key={job.id} className="hover:bg-gray-900/50 transition-colors">
                <td className="px-4 py-3 text-gray-400">
                  {new Date(job.createdAt).toLocaleString()}
                </td>
                <td className="px-4 py-3 font-mono text-xs">
                  {job.repository?.fullName ?? "—"}
                </td>
                <td className="px-4 py-3">
                  <Link href={`/dashboard/jobs/${job.id}`} className="text-blue-400 hover:underline">
                    #{job.sourcePrNumber}
                  </Link>
                </td>
                <td className="px-4 py-3">
                  <StatusBadge status={job.status} />
                </td>
                <td className="px-4 py-3">
                  {job.docPrNumber ? (
                    <span className="text-green-400">#{job.docPrNumber}</span>
                  ) : (
                    <span className="text-gray-600">—</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
