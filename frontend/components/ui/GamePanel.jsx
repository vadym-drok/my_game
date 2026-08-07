export default function GamePanel({ as: Component = "section", className = "", variant = "default", children, ...props }) {
  return <Component className={`game-panel game-panel-${variant} ${className}`.trim()} {...props}>{children}</Component>;
}
