import { useState } from "react";
import { motion } from "framer-motion";
import LoadingDots from "./LoadingDots";
import { Search } from "lucide-react";
import type { SearchResponse } from "../types/api";
import { orchestrate } from "../lib/api";
import axios, { AxiosError } from "axios";
import { toast } from "sonner";

export default function SearchDock({
  onResults,
  docked,
}: {
  onResults: (data: SearchResponse) => void;
  docked?: boolean;
}) {
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(false);

const submit = async () => {
  if (!q.trim()) {
    toast.warning("Please enter something to search.");
    return;
  }

  setLoading(true);
  const loadingToast = toast.loading("Fetching results...");

  try {
    const res = await orchestrate(q); // ← This internally calls axios
    const data: SearchResponse = res;
    onResults(data);

    toast.success("✅ Results loaded successfully!", { id: loadingToast });
  } catch (err: unknown) {
    // ✅ Proper AxiosError handling
    const error = err as AxiosError<{ detail?: string }>;

    if (axios.isAxiosError(error)) {
      if (error.response?.status === 503) {
        toast.error("⚠️ Network is down or target sites unreachable.", {
          id: loadingToast,
        });
      } else if (error.response?.status === 500) {
        toast.error("❌ Server error — please try again later.", {
          id: loadingToast,
        });
      } else {
        const msg =
          error.response?.data?.detail ||
          error.message ||
          "❌ Something went wrong.";
        toast.error(msg, { id: loadingToast });
      }
    } else {
      toast.error("❌ Unknown error occurred.", { id: loadingToast });
    }

    console.error("Search error:", error);
  } finally {
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

          {/* Hide blue button when loading */}
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
