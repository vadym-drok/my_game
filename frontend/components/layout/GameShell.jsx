import Sidebar from "./Sidebar";
import ResourceBar from "./ResourceBar";

export default function GameShell({ children, actions }) {
  return <div className="game-shell"><Sidebar /><div className="game-main"><ResourceBar actions={actions} /><div className="game-content">{children}</div></div></div>;
}
