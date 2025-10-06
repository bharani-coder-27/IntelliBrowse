// src/lib/api.ts
import type { SearchResponse } from "../types/api";

export const orchestrate = async (query: string): Promise<SearchResponse> => {
  const res = await fetch("http://localhost:8000/orchestrate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ instruction: query }),
  });

  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: ${res.statusText}`);
  }

  const data = await res.json();
  return data as SearchResponse; // ✅ fully typed
};
