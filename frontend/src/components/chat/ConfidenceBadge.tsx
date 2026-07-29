const styles: Record<string, string> = {
  high: "bg-green-100 text-green-700",
  medium: "bg-yellow-100 text-yellow-700",
  low: "bg-orange-100 text-orange-700",
  insufficient: "bg-red-100 text-red-700",
};

const labels: Record<string, string> = {
  high: "High confidence",
  medium: "Medium confidence",
  low: "Low confidence",
  insufficient: "Insufficient — used web",
};

export function ConfidenceBadge({ level }: { level: string }) {
  return (
    <span className={`text-[11px] font-medium px-2 py-0.5 rounded-full ${styles[level] ?? styles.medium}`}>
      {labels[level] ?? level}
    </span>
  );
}