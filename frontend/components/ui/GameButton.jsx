export default function GameButton({ variant = "primary", className = "", children, ...props }) {
  return <button className={`button-${variant} ${className}`.trim()} {...props}>{children}</button>;
}
