"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Background, ConnectionMode, Controls, Handle, Position, ReactFlow, addEdge, reconnectEdge, useEdgesState, useNodesState } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { MapPin, Maximize, Pencil, Save } from "lucide-react";
import { useTranslations } from "next-intl";
import PageHeader from "../../components/layout/PageHeader";
import Toast from "../../components/Toast";
import GameButton from "../../components/ui/GameButton";
import "./locations.css";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010";

function LocationNode({ data }) {
  const positions = [Position.Top, Position.Right, Position.Bottom, Position.Left];
  return <div className={`location-map-node ${data.editing ? "is-editing" : ""} ${data.discovered ? "is-discovered" : ""}`} title={data.description}>
    {positions.map((position) => <span key={position} className={`location-map-marker location-map-handle-${position}`} aria-hidden="true" />)}
    {positions.map((position) => <Handle key={position} id={position} className={`location-map-handle location-map-handle-${position}`} type="source" position={position} isConnectable={data.editing} />)}
    {data.imagePath ? <img src={data.imagePath} alt="" /> : <span className="location-map-art-slot" aria-hidden="true" />}
    <strong>{data.name}</strong>
    <Handle className="location-map-handle" type="source" position={Position.Right} isConnectable={data.editing} />
  </div>;
}

const nodeTypes = { location: LocationNode };

function toNode(location, position, editing) {
  return { id: location.code, type: "location", position, data: { name: location.name, description: location.description, imagePath: location.image_path, editing, discovered: location.is_discovered } };
}

function closestHandle(from, to) {
  const x = to.x - from.x; const y = to.y - from.y;
  return Math.abs(x) >= Math.abs(y) ? (x >= 0 ? Position.Right : Position.Left) : (y >= 0 ? Position.Bottom : Position.Top);
}

export default function LocationsPage() {
  const t = useTranslations("Locations");
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [locations, setLocations] = useState([]);
  const [editing, setEditing] = useState(false);
  const [flow, setFlow] = useState(null);
  const [message, setMessage] = useState("");
  const reconnectSucceeded = useRef(false);

  const syncEditing = useCallback((value) => setNodes((current) => current.map((node) => ({ ...node, draggable: value, data: { ...node.data, editing: value } }))), [setNodes]);

  useEffect(() => {
    Promise.all([fetch(`${API_URL}/locations`).then((response) => response.json()), fetch(`${API_URL}/locations/map`).then((response) => response.json())])
      .then(([definitions, layout]) => {
        setLocations(definitions);
        const byCode = new Map(definitions.map((location) => [location.code, location]));
        const positions = Object.fromEntries(layout.nodes.map((node) => [node.location_code, { x: node.x, y: node.y }]));
        setNodes(layout.nodes.map((node) => toNode(byCode.get(node.location_code), positions[node.location_code], false)).filter(Boolean));
        setEdges(layout.connections.map(({ source, target, source_handle, target_handle }) => ({ id: `${source}-${target}`, source, target, sourceHandle: source_handle || closestHandle(positions[source], positions[target]), targetHandle: target_handle || closestHandle(positions[target], positions[source]), type: "straight" })));
      })
      .catch(() => setMessage(t("saveFailed")));
  }, [setEdges, setNodes, t]);

  const unplaced = useMemo(() => locations.filter((location) => !nodes.some((node) => node.id === location.code)), [locations, nodes]);
  const onConnect = useCallback((connection) => editing && setEdges((current) => current.some((edge) => (edge.source === connection.source && edge.target === connection.target) || (edge.source === connection.target && edge.target === connection.source)) ? current : addEdge({ ...connection, id: `${connection.source}-${connection.target}`, type: "straight" }, current)), [editing, setEdges]);
  const onReconnectStart = useCallback(() => { reconnectSucceeded.current = false; }, []);
  const onReconnect = useCallback((oldEdge, connection) => { reconnectSucceeded.current = true; setEdges((current) => reconnectEdge(oldEdge, connection, current)); }, [setEdges]);
  const onReconnectEnd = useCallback((_, edge) => { if (!reconnectSucceeded.current) setEdges((current) => current.filter((item) => item.id !== edge.id)); }, [setEdges]);
  const onDragOver = useCallback((event) => { if (editing) { event.preventDefault(); event.dataTransfer.dropEffect = "move"; } }, [editing]);
  const onDrop = useCallback((event) => {
    event.preventDefault();
    if (!editing || !flow) return;
    const code = event.dataTransfer.getData("application/location-code");
    const location = locations.find((item) => item.code === code);
    if (!location || nodes.some((node) => node.id === code)) return;
    setNodes((current) => [...current, toNode(location, flow.screenToFlowPosition({ x: event.clientX, y: event.clientY }), true)]);
  }, [editing, flow, locations, nodes, setNodes]);
  const fitView = useCallback(() => flow?.fitView({ padding: .25, duration: 250 }), [flow]);
  const toggleEdit = async () => {
    if (!editing) { setEditing(true); syncEditing(true); return; }
    try {
      const response = await fetch(`${API_URL}/locations/map`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ nodes: nodes.map((node) => ({ location_code: node.id, x: node.position.x, y: node.position.y })), connections: edges.map((edge) => ({ source: edge.source, target: edge.target, source_handle: edge.sourceHandle, target_handle: edge.targetHandle })) }) });
      if (!response.ok) throw new Error();
      setEditing(false); syncEditing(false); setMessage(t("saved"));
    } catch { setMessage(t("saveFailed")); }
  };

  return <main className="locations-map-page"><Toast message={message} setMessage={setMessage} /><PageHeader title={t("title")} actions={<div className="locations-map-actions"><GameButton variant="secondary" type="button" onClick={fitView}><Maximize aria-hidden="true" />{t("fitView")}</GameButton><GameButton type="button" onClick={toggleEdit}>{editing ? <Save aria-hidden="true" /> : <Pencil aria-hidden="true" />}{editing ? t("save") : t("edit")}</GameButton></div>} /><section className={`locations-map-shell ${editing ? "is-editing" : ""}`}><aside className="locations-map-stash" aria-hidden={!editing}><h2>{t("unplaced")}</h2><p>{t("dragHint")}</p><p>{t("connectionHint")}</p>{unplaced.map((location) => <button key={location.code} type="button" draggable onDragStart={(event) => event.dataTransfer.setData("application/location-code", location.code)}><MapPin aria-hidden="true" /><span>{location.name}</span></button>)}</aside><div className="locations-map-canvas" onDrop={onDrop} onDragOver={onDragOver}>{nodes.length === 0 && <p className="locations-map-empty">{t("emptyMap")}</p>}<ReactFlow nodes={nodes} edges={edges} nodeTypes={nodeTypes} onNodesChange={editing ? onNodesChange : undefined} onEdgesChange={editing ? onEdgesChange : undefined} onConnect={onConnect} onReconnectStart={onReconnectStart} onReconnect={onReconnect} onReconnectEnd={onReconnectEnd} onInit={setFlow} fitView fitViewOptions={{ padding: .25 }} connectionMode={ConnectionMode.Loose} nodesDraggable={editing} nodesConnectable={editing} nodesFocusable={editing} edgesFocusable={editing} edgesReconnectable={editing} elementsSelectable={editing} deleteKeyCode={editing ? ["Backspace", "Delete"] : null} panOnDrag={!editing ? true : [1, 2]}><Background gap={32} size={1} color="#9a6a2f66" /><Controls showInteractive={false} /></ReactFlow></div></section></main>;
}
