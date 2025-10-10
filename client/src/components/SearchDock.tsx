import { useState } from "react";
import { motion } from "framer-motion";
import LoadingDots from "./LoadingDots";
import { Search } from "lucide-react";
import type { SearchResponse } from "../types/api";
import { orchestrate } from "../lib/api/orchestrate";
import axios, { AxiosError } from "axios";
import { toast } from "sonner";
import { useSearch } from "../context/SearchContext";
import type { Product, ProductRecord } from "../types/product";

export default function SearchDock({
  onResults,
  docked,
}: {
  onResults: (data: SearchResponse) => void;
  docked?: boolean;
}) {
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(false);

  const { setProducts, setHasResults, setLastResponse } = useSearch();

  const submit = async () => {
    if (!q.trim()) {
      toast.warning("Please enter something to search.");
      return;
    }

    setLoading(true);
    const loadingToast = toast.loading("Fetching results...");

    try {
      // 🔹 Call backend
      const res = await orchestrate(q);
      const data: SearchResponse = res;

      // ------------------------------
      // ✅ Type-safe array extraction
      // ------------------------------
      const rawIds: number[] = data.product_ids ?? [];

      const isProductArray = (arr: unknown): arr is Product[] =>
        Array.isArray(arr) &&
        arr.length > 0 &&
        typeof (arr[0] as Product).title === "string" &&
        typeof (arr[0] as Product).price === "string";

      const rawItems: Product[] = isProductArray(data.items)
        ? data.items
        : isProductArray(data.results)
        ? data.results
        : [];

      const mergedProducts: ProductRecord[] = rawItems.map((item, i) => ({
        ...item,
        id: rawIds[i] ?? i + 1,
      }));

      console.log("✅ Merged products:", mergedProducts);

      setLastResponse(data);
      setProducts(mergedProducts);
      setHasResults(mergedProducts.length > 0);

      onResults(data);

      toast.success("✅ Results loaded successfully!", { id: loadingToast });
    } catch (err: unknown) {
      const error = err as AxiosError<{ detail?: string }>;

      if (axios.isAxiosError(error)) {
        const msg =
          error.response?.data?.detail ||
          error.message ||
          "❌ Something went wrong.";
        toast.error(msg, { id: loadingToast });
      } else if (err instanceof Error) {
        toast.error(`❌ ${err.message}`, { id: loadingToast });
        console.error("Non-Axios error:", err);
      } else {
        toast.error("❌ Unknown error occurred.", { id: loadingToast });
        console.error("Unrecognized error:", err);
      }
    } finally {
      // ✅ Always stop the loading spinner
      setLoading(false);
    }
  };

  return (
    <motion.div
      className={`fixed left-1/2 -translate-x-1/2 z-50 w-[90vw] max-w-2xl ${
        docked ? "relative" : "top-[45vh]"
      }`}
      transition={{ type: "spring", stiffness: 120, damping: 14 }}
    >
      <div className="card px-6 py-5 flex flex-col gap-4 items-center backdrop-blur-md">
        <div className="flex items-center gap-2 w-full">
          <Search className="text-brand-600" size={20} />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && submit()}
            placeholder="What do you want to find today?"
            className="input-base flex-1 px-2 py-1 text-sm sm:text-base"
          />

          {loading ? (
            <div className="flex items-center justify-center px-4 py-2">
              <LoadingDots />
            </div>
          ) : (
            <button
              className="btn-primary px-4 py-2"
              onClick={submit}
              disabled={loading}
            >
              Search
            </button>
          )}
        </div>
      </div>
    </motion.div>
  );
}
