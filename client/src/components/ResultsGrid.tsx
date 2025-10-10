import { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";
import { Download } from "lucide-react";
import ProductCard from "./ProductCard";
import type { Product, ProductRecord } from "../types/product";
import { useSearch } from "../context/SearchContext";
import { api } from "../lib/api"; // axios instance with baseURL + token

interface ResultsGridProps {
  items?: (Product | ProductRecord)[];
}

export default function ResultsGrid({ items }: ResultsGridProps) {
  const { products, lastResponse } = useSearch();
  const navigate = useNavigate();

  const productList = items && items.length ? items : products;

  const [selectionMode, setSelectionMode] = useState(false);
  const [selectedIdxs, setSelectedIdxs] = useState<number[]>([]);
  const [downloadMenuOpen, setDownloadMenuOpen] = useState(false);
  const [downloading, setDownloading] = useState(false);

  const menuRef = useRef<HTMLDivElement | null>(null);

  // ✅ Close dropdown if user clicks outside
  useEffect(() => {
    const handleOutsideClick = (e: MouseEvent) => {
      if (
        menuRef.current &&
        !menuRef.current.contains(e.target as Node)
      ) {
        setDownloadMenuOpen(false);
      }
    };

    if (downloadMenuOpen) {
      document.addEventListener("mousedown", handleOutsideClick);
    }

    return () => {
      document.removeEventListener("mousedown", handleOutsideClick);
    };
  }, [downloadMenuOpen]);

  const toggleSelect = (idx: number) => {
    setSelectedIdxs((prev) =>
      prev.includes(idx)
        ? prev.filter((x) => x !== idx)
        : [...prev, idx]
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

    const idsToSend = selectedIdxs.map((i) => {
      const product = productList[i] as ProductRecord;
      return product.id ?? i;
    });

    navigate("/compare", { state: { selectedIds: idsToSend } });
  };

  // 🧩 Handle Download (JSON / CSV)
  const handleDownload = async (format: "json" | "csv") => {
    try {
      setDownloading(true);
      setDownloadMenuOpen(false); // ✅ Close menu immediately when clicked

      const searchId = lastResponse?.search_id;
      if (!searchId) {
        toast.error("No search session found to download.");
        return;
      }

      const res = await api.get(`/download/${format}`, {
        params: { search_id: searchId },
        responseType: "blob",
      });

      const disposition = res.headers["content-disposition"];
      const match = disposition && disposition.match(/filename="?([^"]+)"?/);
      const filename = match ? match[1] : `results.${format}`;

      const blob = new Blob([res.data], {
        type: format === "csv" ? "text/csv" : "application/json",
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);

      toast.success(`✅ ${format.toUpperCase()} file downloaded successfully!`);
    } catch (err: unknown) {
      if (err instanceof Error) {
        console.error("Download error:", err.message);
      } else {
        console.error("Unknown download error:", err);
      }
      toast.error("❌ Failed to download file.");
    } finally {
      setDownloading(false);
    }
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
      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        {/* Left controls */}
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

        {/* Right controls */}
        <div className="flex items-center gap-3">
          {/* Download dropdown */}
          <div ref={menuRef} className="relative">
            <button
              onClick={() => setDownloadMenuOpen((p) => !p)}
              disabled={downloading}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-500 hover:bg-indigo-600 text-white text-sm font-medium transition"
            >
              <Download size={16} />
              {downloading ? "Downloading..." : "Download"}
            </button>

            {downloadMenuOpen && (
              <motion.div
                initial={{ opacity: 0, y: -5 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -5 }}
                transition={{ duration: 0.2 }}
                className="absolute right-0 mt-2 w-36 bg-slate-900 text-slate-100 rounded-lg border border-slate-700 shadow-lg z-50"
              >
                <button
                  onClick={() => handleDownload("json")}
                  className="block w-full text-left px-4 py-2 hover:bg-slate-800 transition"
                >
                  📄 JSON File
                </button>
                <button
                  onClick={() => handleDownload("csv")}
                  className="block w-full text-left px-4 py-2 hover:bg-slate-800 transition rounded-b-lg"
                >
                  📊 CSV File
                </button>
              </motion.div>
            )}
          </div>

          {/* Compare */}
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
      </div>

      {/* Grid */}
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
