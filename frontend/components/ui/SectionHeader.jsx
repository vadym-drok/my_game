export default function SectionHeader({ icon: Icon, title, children, className = "" }) {
  return <div className={`section-header ${className}`.trim()}><div className="section-header-title">{Icon && <Icon aria-hidden="true" />}<h2>{title}</h2></div>{children && <div className="section-header-actions">{children}</div>}</div>;
}
