"use client";

import { useState } from "react";

export default function GameIllustrationFrame({ src, alt, code, ratio = "4:3", className = "" }) {
  const [missing, setMissing] = useState(!src);
  return <span className={`game-illustration-frame ${className}`.trim()} style={{ "--illustration-ratio": ratio }}>{missing ? <span className="game-art-fallback">{code}</span> : <img src={src} alt={alt} onError={() => setMissing(true)} />}</span>;
}
