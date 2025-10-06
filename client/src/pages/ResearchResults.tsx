// src/pages/ResearchResults.tsx
import { useState } from "react";
import SearchDock from "../components/SearchDock";
import ResultsList from "../components/ResultsList";
import type { ResearchResult } from "../types/research";
import type { SearchResponse } from "../types/api";

export default function ResearchResults() {
  const [results, setResults] = useState<ResearchResult[]>([]);

  // ✅ extract items or results safely
  const handleResults = (data: SearchResponse) => {
    const resultArray = (data.items || data.results || []) as ResearchResult[];
    setResults(resultArray);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-slate-100">
      <div className="flex flex-col items-center pt-28">
        <SearchDock onResults={handleResults} docked={true} />
        <ResultsList results={results} />
      </div>
    </div>
  );
}
