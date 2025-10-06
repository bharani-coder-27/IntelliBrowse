// src/App.tsx
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import ThemeToggle from "./components/ThemeToggle";
import SearchDock from "./components/SearchDock";
import ResultsGrid from "./components/ResultsGrid";
import ResultsList from "./components/ResultsList";
import type { Product } from "./types/product";
import type { ResearchResult } from "./types/research";
import type { SearchResponse } from "./types/api";

type SearchMode = "product" | "research";

export default function App() {
  const [mode, setMode] = useState<SearchMode>("product");
  const [items, setItems] = useState<Product[]>([]);
  const [researchItems, setResearchItems] = useState<ResearchResult[]>([]);

  const hasResults =
    (mode === "product" && items.length > 0) ||
    (mode === "research" && researchItems.length > 0);

  const messages = [
    "Ask anything, learn everything 🌍",
    "Explore smarter with IntelliBrowse ✨",
    "Curiosity leads to discovery 🚀",
    "Dream. Search. Achieve. 💡",
  ];

  const [index, setIndex] = useState(0);
  useEffect(() => {
    const interval = setInterval(
      () => setIndex((i) => (i + 1) % messages.length),
      3000
    );
    return () => clearInterval(interval);
  }, []);

  // ✅ handle backend data properly
  const handleResults = (data: SearchResponse) => {
    console.log("📥 Full backend response:", data);
    const intent = data?.plan?.intent;
    const results = (data.items || data.results || []) as
      | ResearchResult[]
      | Product[];

    if (intent === "explore" || intent === "learn") {
      setMode("research");
      setResearchItems(results as ResearchResult[]);
    } else {
      setMode("product");
      setItems(results as Product[]);
    }
  };

  return (
    <div className="relative min-h-screen flex flex-col items-center overflow-hidden bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-slate-100">
      {/* 🌙 Theme toggle */}
      <div className="fixed top-4 right-4 z-50">
        <ThemeToggle />
      </div>

      {/* 💫 Animated glow */}
      <motion.div
        className="absolute w-[900px] h-[900px] rounded-full blur-[180px] bg-gradient-to-tr from-indigo-500 via-fuchsia-500 to-cyan-400 opacity-25 top-1/3 left-1/2 -translate-x-1/2"
        animate={{ y: [0, -20, 0] }}
        transition={{ repeat: Infinity, duration: 8 }}
      />

      {/* 🌈 HERO SECTION */}
      <motion.div
        className="relative flex flex-col items-center justify-center mt-28 space-y-8 text-center"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        {/* IntelliBrowse shimmer text */}
        <motion.div
          className={`flex items-center gap-2 z-40 ${
            hasResults ? "fixed top-6 left-10" : "relative"
          }`}
          initial={{ scale: 1, y: 0 }}
          animate={hasResults ? { scale: 0.7 } : { scale: 1, y: 0 }}
          transition={{ type: "spring", stiffness: 120, damping: 16 }}
        >
          <h1 className="font-extrabold shimmer-text text-4xl sm:text-6xl select-none">
            IntelliBrowse
          </h1>
        </motion.div>

        {/* Headline */}
        <AnimatePresence mode="wait">
          {!hasResults && (
            <motion.h2
              key={messages[index]}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.6 }}
              className="text-2xl sm:text-3xl font-semibold text-slate-200"
            >
              {messages[index]}
            </motion.h2>
          )}
        </AnimatePresence>

        <div className="flex flex-col items-center space-y-8 z-40 relative">
          <SearchDock onResults={handleResults} docked={hasResults} />

          {!hasResults && (
            <motion.div
              className="text-center space-y-3 mt-60"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4 }}
            >
              <p className="text-xl text-slate-300">
                “Discover, learn, and explore the world around you.”
              </p>
              <p className="text-sm text-slate-400 italic">
                Try “Best learning resources for data science” or “Top laptops
                under 60k”
              </p>
            </motion.div>
          )}
        </div>
      </motion.div>

      {/* 🧾 RESULTS SECTION */}
      <motion.main
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className={`relative z-10 w-full max-w-7xl px-4 transition-all duration-700 ${
          hasResults ? "mt-[14vh]" : "mt-[60vh]"
        } pb-32`}
      >
        {mode === "product" && items.length > 0 && <ResultsGrid items={items} />}
        {mode === "research" && researchItems.length > 0 && (
          <ResultsList results={researchItems} />
        )}
      </motion.main>
    </div>
  );
}
