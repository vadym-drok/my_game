import GameIllustrationFrame from "../game-art/GameIllustrationFrame";

export default function PageHeader({ eyebrow, title, subtitle, actions, artwork, artworkAlt = "", artworkPosition, className = "" }) {
  return <header className={`page-header ${artwork ? "page-header-with-artwork" : ""} ${className}`.trim()}>
    {artwork && <GameIllustrationFrame src={artwork} alt={artworkAlt} code={title} ratio="5 / 1" objectPosition={artworkPosition} className="page-header-artwork" />}
    <div className="page-header-content"><div>{eyebrow && <p className="eyebrow">{eyebrow}</p>}<h1>{title}</h1>{subtitle && <p className="page-subtitle">{subtitle}</p>}</div>{actions && <div className="page-header-actions">{actions}</div>}</div>
  </header>;
}
