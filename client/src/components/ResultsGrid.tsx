// src/components/ResultsGrid.tsx
import { useState } from "react";
import { motion } from "framer-motion";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";
import ProductCard from "./ProductCard";
import type { Product, ProductRecord } from "../types/product";
import { useSearch } from "../context/SearchContext";

interface ResultsGridProps {
  items?: (Product | ProductRecord)[];
}

export default function ResultsGrid({ items }: ResultsGridProps) {
  const { products } = useSearch();
  const navigate = useNavigate();

  // use items from props if given, else from context
  const productList = items && items.length ? items : products;

  const [selectionMode, setSelectionMode] = useState(false);
  const [selectedIdxs, setSelectedIdxs] = useState<number[]>([]);

  const toggleSelect = (idx: number) => {
    setSelectedIdxs((prev) =>
      prev.includes(idx) ? prev.filter((x) => x !== idx) : [...prev, idx]
    );
  };

  const handleSelectionMode = () => {
    setSelectionMode((prev) => !prev);
    setSelectedIdxs([]);
  };

  const handleCompare = () => {
    if (selectedIdxs.length < 2) {
      toast.error("Select at least two products to compare.");
      return;
    }

    // ✅ Extract product IDs (if present) or use index fallback
    const idsToSend = selectedIdxs.map((i) => {
      const product = productList[i] as ProductRecord;
      return product.id ?? i; // fallback if no DB id
    });

    navigate("/compare", { state: { selectedIds: idsToSend } });
  };

  if (!productList.length) {
    return (
      <div className="flex items-center justify-center h-[60vh] text-slate-400">
        <p>No products available. Try searching again.</p>
      </div>
    );
  }

  return (
    <div className="mt-10">
      <div className="flex justify-between items-center mb-4">
        <div className="flex items-center gap-3">
          <button
            onClick={handleSelectionMode}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
              selectionMode
                ? "bg-red-500 hover:bg-red-600 text-white"
                : "bg-cyan-500 hover:bg-cyan-600 text-white"
            }`}
          >
            {selectionMode ? "Cancel Selection" : "Select for Compare"}
          </button>
          {selectionMode && (
            <p className="text-sm text-slate-400">
              {selectedIdxs.length} selected
            </p>
          )}
        </div>

        {selectionMode && (
          <button
            onClick={handleCompare}
            disabled={selectedIdxs.length < 2}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
              selectedIdxs.length < 2
                ? "bg-gray-700 text-gray-400 cursor-not-allowed"
                : "bg-emerald-500 hover:bg-emerald-600 text-white"
            }`}
          >
            Compare
          </button>
        )}
      </div>

      <motion.div
        layout
        className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6 }}
      >
        {productList.map((p, i) => (
          <ProductCard
            key={(p as ProductRecord).id ?? i}
            p={p}
            i={i}
            selected={selectedIdxs.includes(i)}
            selectionMode={selectionMode}
            onSelect={toggleSelect}
          />
        ))}
      </motion.div>
    </div>
  );
}
