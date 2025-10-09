import { useEffect, useState } from "react";
import { useSearch } from "./context/SearchContext";
import { motion, AnimatePresence } from "framer-motion";
import ThemeToggle from "./components/ThemeToggle";
import SearchDock from "./components/SearchDock";
import ResultsGrid from "./components/ResultsGrid";
import ResultsList from "./components/ResultsList";
import type { Product, ProductRecord } from "./types/product";
import type { ResearchResult } from "./types/research";
import type { SearchResponse } from "./types/api";

type SearchMode = "product" | "research";

export default function App() {
  const [mode, setMode] = useState<SearchMode>("product");
  const [researchItems, setResearchItems] = useState<ResearchResult[]>([]);
  const {
    hasResults,
    setHasResults,
    products,
    setProducts,
    isSessionActive,
    setIsSessionActive,
  } = useSearch();

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

  // ✅ Reset only if it's first load in this session
  useEffect(() => {
    if (!isSessionActive) {
      setHasResults(false);
      setProducts([]);
    }
  }, [isSessionActive, setHasResults, setProducts]);

  // ✅ handle backend results
  const handleResults = (data: SearchResponse) => {
    const intent = data?.plan?.intent;
    const rawResults = (data.items || data.results || []) as
      | ResearchResult[]
      | Product[];
    const rawIds = data.product_ids ?? [];

    setHasResults(rawResults.length > 0);
    setIsSessionActive(true);

    if (intent === "explore" || intent === "learn") {
      setMode("research");
      setResearchItems(rawResults as ResearchResult[]);
    } else {
      setMode("product");

      // ✅ Merge product_ids with items
      const merged: ProductRecord[] = (rawResults as Product[]).map((p, i) => ({
        ...p,
        id: rawIds[i] ?? i + 1,
      }));

      console.log("✅ Merged products:", merged);
      setProducts(merged);
    }
  };

  return (
    <div className="relative min-h-screen flex flex-col items-center overflow-hidden bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-slate-100">
      <div className="fixed top-4 right-4 z-50 flex items-center gap-4">
        <ThemeToggle />
      </div>

      <motion.div
        className="absolute w-[900px] h-[900px] rounded-full blur-[180px] bg-gradient-to-tr from-indigo-500 via-fuchsia-500 to-cyan-400 opacity-25 top-1/3 left-1/2 -translate-x-1/2"
        animate={{ y: [0, -20, 0] }}
        transition={{ repeat: Infinity, duration: 8 }}
      />

      {/* HERO */}
      <motion.div
        className="relative flex flex-col items-center justify-center mt-28 space-y-8 text-center"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        {!hasResults && (
          <>
            <motion.div
              className="flex items-center gap-2 z-40 relative"
              initial={{ opacity: 0, scale: 0.9, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              transition={{ type: "spring", stiffness: 120, damping: 14 }}
            >
              <h1 className="font-extrabold shimmer-text text-4xl sm:text-6xl select-none">
                IntelliBrowse
              </h1>
            </motion.div>

            <AnimatePresence mode="wait">
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
            </AnimatePresence>
          </>
        )}

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

      {/* RESULTS */}
      <motion.main
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className={`relative z-10 w-full max-w-7xl px-4 transition-all duration-700 ${
          hasResults ? "mt-[14vh]" : "mt-[60vh]"
        } pb-32`}
      >
        {mode === "product" && products.length > 0 && (
          <ResultsGrid items={products} />
        )}
        {mode === "research" && researchItems.length > 0 && (
          <ResultsList results={researchItems} />
        )}
      </motion.main>
    </div>
  );
}
