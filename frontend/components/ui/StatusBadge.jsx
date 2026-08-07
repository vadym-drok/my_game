export default function StatusBadge({ tone = "neutral", className = "", children }) {
  return <span className={`status-badge status-${tone} ${className}`.trim()}>{children}</span>;
}
