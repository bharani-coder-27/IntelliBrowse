import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { toast } from "sonner";
import { api } from "../lib/api/index"; // ✅ using your axios instance
import CompareTable from "../components/CompareTable";
import CompareSummary from "../components/CompareSummary";
import type { CompareResponse } from "../types/product";

export default function ComparePage() {
  const location = useLocation();
  const navigate = useNavigate();
  const selectedIds = location.state?.selectedIds as number[] | undefined;

  const [data, setData] = useState<CompareResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!selectedIds || selectedIds.length < 2) {
      toast.error("Please select at least two products to compare.");
      navigate(-1);
      return;
    }

    const fetchComparison = async (): Promise<void> => {
      try {
        setLoading(true);
        const res = await api.post<CompareResponse>("/compare", {
          ids: selectedIds,
        });
        setData(res.data);
        // console.log("The Product Link arrrrrreee:    ",data?.products[0].link);
      } catch (err: unknown) {
        if (err instanceof Error) {
          console.error("Compare error:", err.message);
        } else {
          console.error("Compare error:", err);
        }
        toast.error("Failed to load comparison data.");
      } finally {
        setLoading(false);
      }
    };

    fetchComparison();
  }, [selectedIds, navigate]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-screen text-slate-300">
        <p className="animate-pulse text-lg">
          🔄 Comparing selected products...
        </p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex flex-col items-center justify-center h-screen text-slate-300">
        <p>Comparison data unavailable.</p>
        <button
          onClick={() => navigate(-1)}
          className="mt-4 px-4 py-2 bg-cyan-600 hover:bg-cyan-700 rounded-lg text-white"
        >
          ← Back
        </button>
      </div>
    );
  }

  const { products, summary } = data;
  console.log("The Products is: ", products[0]);

  return (
    <motion.div
      className="min-h-screen pt-20 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-slate-100 px-8 py-10"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      {/* 🏷️ Header */}
      <div className="flex justify-between items-center mb-10">
        <h1 className="text-2xl font-bold tracking-wide">
          Compare Products ({products.length})
        </h1>
        <button
          onClick={() => navigate(-1)}
          className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 rounded-lg text-white font-medium"
        >
          ← Back to Results
        </button>
      </div>

      {/* 🧾 Table */}
      <CompareTable products={products} />

      {/* 🧠 Summary */}
      {summary && <CompareSummary summary={summary} />}
    </motion.div>
  );
}
