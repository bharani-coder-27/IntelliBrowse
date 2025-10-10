// src/components/ResultCard.tsx
import { motion } from "framer-motion";
import type { ResearchResult } from "../types/research";

export default function ResultCard({ result }: { result: ResearchResult }) {
  const link = result.url?.startsWith("http")
    ? result.url
    : `https://${result.url}`;

  let domain = "Wikipedia";
  try {
    domain = new URL(link).hostname.replace("www.", "");
  } catch {
    /* ignore */
  }

  return (
    <motion.div
      whileHover={{ scale: 1.01 }}
      className="card w-full p-5 mb-5 hover:bg-white/10 dark:hover:bg-slate-800/60 transition"
    >
      {/* Title */}
      <a
        href={link}
        target="_blank"
        rel="noopener noreferrer"
        className="font-semibold text-lg text-cyan-400 hover:underline"
      >
        {result.title}
      </a>

      {/* Snippet */}
      <p className="text-slate-300 text-sm leading-relaxed mt-2">
        {result.text}
      </p>

      {/* Source */}
      <p className="text-xs text-slate-500 mt-3 border-t border-white/10 pt-2">
        🌐 {domain}
      </p>
    </motion.div>
  );
}
