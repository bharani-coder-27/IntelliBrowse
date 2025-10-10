// src/components/ResultsList.tsx
import { motion } from "framer-motion";
import ResultCard from "./ResultCard";
import type { ResearchResult } from "../types/research";

interface ResultsListProps {
  results: ResearchResult[];
}

export default function ResultsList({ results }: ResultsListProps) {
  if (!results || results.length === 0) {
    return (
      <div className="text-center text-slate-400 mt-20">
        No research results found. Try another search ✨
      </div>
    );
  }

  return (
    <motion.div
      layout
      className="max-w-6xl mx-auto mt-10 grid grid-cols-1 md:grid-cols-2 gap-6 px-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6 }}
    >
      {results.map((res, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.05 }}
        >
          <ResultCard result={res} />
        </motion.div>
      ))}
    </motion.div>
  );
}
