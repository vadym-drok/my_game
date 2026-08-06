"use client";

import { useEffect } from "react";

export default function Toast({ message, setMessage }) {
  useEffect(() => {
    if (!message) return;
    const timeout = setTimeout(() => setMessage(""), 4000);
    return () => clearTimeout(timeout);
  }, [message, setMessage]);
  return message && <div className="toast" role="status">{message}</div>;
}
