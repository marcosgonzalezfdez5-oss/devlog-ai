const styles: Record<string, string> = {
  pending: "bg-gray-800 text-gray-400",
  running: "bg-blue-900/50 text-blue-300 animate-pulse",
  completed: "bg-green-900/50 text-green-400",
  failed: "bg-red-900/50 text-red-400",
};

export default function StatusBadge({ status }: { status: string }) {
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${styles[status] ?? styles["pending"]}`}>
      {status}
    </span>
  );
}
