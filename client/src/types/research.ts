// src/types/research.ts
export interface ResearchResult {
  title: string;
  url: string;        // ✅ Wikipedia or info source link
  text: string;       // ✅ Extracted main content
  site?: string;      // optional for labeling
}
