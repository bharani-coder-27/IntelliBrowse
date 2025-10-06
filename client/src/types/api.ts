// src/types/api.ts
import type { Product } from "./product";
import type { ResearchResult } from "./research";

export interface SearchPlan {
  intent: "explore" | "learn" | "buy" | "compare" | "find" | "shop" | string;
  sources: string[];
  query: string;
  max_results: number;
  max_price?: number | null;
}

export interface SearchResponse {
  plan: SearchPlan;
  total: number;
  json_path?: string;
  csv_path?: string;
  download_json?: string;
  download_csv?: string;
  results?: Product[] | ResearchResult[];
  items?: Product[] | ResearchResult[]; // ✅ backend returns items
}
