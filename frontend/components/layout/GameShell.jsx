import Sidebar from "./Sidebar";
import ResourceBar from "./ResourceBar";
import NationHeader from "../nation/NationHeader";

export default function GameShell({ children, actions }) {
  return <div className="game-shell"><Sidebar /><div className="game-main"><ResourceBar actions={actions} /><NationHeader /><div className="game-content">{children}</div></div></div>;
}
