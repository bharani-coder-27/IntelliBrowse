import { motion } from "framer-motion";
import { Sparkles } from "lucide-react";

export default function CompareSummary({ summary }: { summary: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.2 }}
      className="mt-10 p-6 rounded-2xl bg-gradient-to-br from-emerald-600/10 via-slate-800/30 to-slate-900/50 border border-emerald-600/30 backdrop-blur-md shadow-lg"
    >
      <div className="flex items-center gap-3 mb-4">
        <Sparkles className="text-emerald-400 w-5 h-5" />
        <h2 className="text-lg font-semibold text-emerald-300">
          AI Comparison Summary
        </h2>
      </div>
      <p className="text-slate-200 leading-relaxed whitespace-pre-wrap">
        {summary}
      </p>
    </motion.div>
  );
}
