export default function GameProgressBar({ className = "", ...props }) {
  return <progress className={`game-progress ${className}`.trim()} {...props} />;
}
