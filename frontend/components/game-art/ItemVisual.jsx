import GameIconFrame from "./GameIconFrame";
import GameIllustrationFrame from "./GameIllustrationFrame";

export default function ItemVisual({ item, className = "" }) {
  return item.visual_type === "illustration"
    ? <GameIllustrationFrame src={item.image_path} alt={item.name} code={item.code} className={className} />
    : <GameIconFrame src={item.image_path} alt={item.name} code={item.code} size={48} className={className} />;
}
