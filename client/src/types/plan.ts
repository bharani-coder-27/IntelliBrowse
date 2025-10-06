// src/types/plan.ts
export type Plan = {
  sources: ('amazon' | 'flipkart')[];
  query: string;
  max_results: number;
  max_price?: number | null;
};