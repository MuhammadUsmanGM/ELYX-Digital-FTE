"use client";

import { useState, useEffect } from "react";

export default function LoadingDots() {
  const [dots, setDots] = useState("");

  useEffect(() => {
    const interval = setInterval(() => {
      setDots((prev) => (prev.length >= 3 ? "" : prev + "."));
    }, 400);
    return () => clearInterval(interval);
  }, []);

  return <span className="inline-block min-w-[24px] text-left">{dots}</span>;
}
