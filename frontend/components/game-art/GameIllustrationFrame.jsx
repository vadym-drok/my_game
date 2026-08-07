"use client";

import { useState } from "react";

export default function GameIllustrationFrame({ src, alt, code, ratio = "4:3", size, className = "" }) {
  const [missing, setMissing] = useState(!src);
  return <span className={`game-illustration-frame ${className}`.trim()} style={{ "--illustration-ratio": ratio, ...(size ? { "--illustration-width": `${size}px` } : {}) }}>{missing ? <span className="game-art-fallback">{code}</span> : <img src={src} alt={alt} onError={() => setMissing(true)} />}</span>;
}
