"use client";

import { useState } from "react";

export default function GameIconFrame({ src, alt, code, size, variant = "default", className = "" }) {
  const [missing, setMissing] = useState(!src);
  return <span className={`game-icon-frame game-icon-frame-${variant} ${className}`.trim()} style={size ? { "--icon-size": `${size}px` } : undefined}>{missing ? <span className="game-art-fallback">{code}</span> : <img src={src} alt={alt} onError={() => setMissing(true)} />}</span>;
}
