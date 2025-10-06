// src/components/ResultsList.tsx
import ResultCard from "./ResultCard";
import type { ResearchResult } from "../types/research";

export default function ResultsList({ results }: { results: ResearchResult[] }) {
  if (!results?.length) {
    return (
      <p className="text-center text-slate-400 mt-10">
        No research results found.
      </p>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      <h2 className="text-2xl font-bold mb-6 text-slate-100">
        🔍 Research Results
      </h2>
      {results.map((r, i) => (
        <ResultCard key={i} result={r} />
      ))}
    </div>
  );
}
