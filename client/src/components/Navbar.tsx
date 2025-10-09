import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useSearch } from "../context/SearchContext";
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Folder, X, Clock } from "lucide-react";
import ResultsGrid from "./ResultsGrid";
import type { Product } from "../types/product";
import { api } from "../lib/api"; // ✅ make sure this import is at top

export default function Navbar() {
  const { user, logout } = useAuth();
  const { hasResults, setHasResults } = useSearch();
  const navigate = useNavigate();

  const [menuOpen, setMenuOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const [history, setHistory] = useState<{ id: number; query: string; created_at: string }[]>([]);
  const [historyResults, setHistoryResults] = useState<Product[]>([]);

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  useEffect(() => {
    if (menuOpen) fetchHistory();
  }, [menuOpen]);


// 🧠 Fetch search history
const fetchHistory = async () => {
  try {
    const res = await api.get("/history");
    setHistory(res.data || []);
  } catch (err) {
    console.error("❌ Failed to fetch history:", err);
  }
};

// 🧠 Fetch products for a specific history entry
const handleHistoryClick = async (searchId: number) => {
  try {
    const res = await api.get(`/products/${searchId}`);
    const data = res.data;
    setHistoryResults(data.products || []);
    setHasResults(true);
    setMenuOpen(false);
    window.scrollTo({ top: 0, behavior: "smooth" });
  } catch (err) {
    console.error("❌ Failed to fetch products from history:", err);
  }
};


  return (
    <>
      {/* Navbar */}
      <nav className="fixed top-0 left-0 w-full z-50 bg-black/30 backdrop-blur-md border-b border-slate-800/60 transition-all duration-300">
        <div className="max-w-7xl mx-auto flex items-center justify-between px-6 py-3">
          {/* 🗂️ History Button */}
          <button
            onClick={() => setMenuOpen(true)}
            className="flex items-center gap-2 text-slate-300 hover:text-white transition"
          >
            <Folder size={22} className="text-indigo-400" />
          </button>

          {/* 🌈 IntelliBrowse Logo */}
          <AnimatePresence>
            {hasResults && (
              <motion.div
                key="logo"
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.3 }}
              >
                <Link
                  to="/"
                  className="font-extrabold text-2xl text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-fuchsia-400 hover:opacity-90 transition"
                >
                  IntelliBrowse
                </Link>
              </motion.div>
            )}
          </AnimatePresence>

          {/* 👤 Auth/Profile */}
          {!user ? (
            <div className="flex items-center gap-3">
              <Link
                to="/login"
                className="px-4 py-2 rounded-full border border-indigo-500 text-indigo-300 hover:bg-indigo-500/10 transition"
              >
                Login
              </Link>
              <Link
                to="/register"
                className="px-4 py-2 rounded-full bg-indigo-600 hover:bg-indigo-500 text-white transition"
              >
                Register
              </Link>
            </div>
          ) : (
            <div className="relative">
              <button
                onClick={() => setProfileOpen(!profileOpen)}
                className="relative w-10 h-10 rounded-full overflow-hidden border border-slate-700 shadow-sm hover:scale-105 transition-transform"
              >
                <img
                  src="/profile.png"
                  alt="Profile"
                  className="w-full h-full object-cover"
                />
              </button>

              <AnimatePresence>
                {profileOpen && (
                  <motion.div
                    key="dropdown"
                    initial={{ opacity: 0, y: -8 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -8 }}
                    transition={{ duration: 0.2 }}
                    className="absolute right-0 top-12 w-44 bg-slate-900/95 text-slate-100 rounded-lg shadow-lg border border-slate-700"
                  >
                    <div className="px-4 py-2 text-sm border-b border-slate-700">
                      Hi, {user.name.split(" ")[0]}
                    </div>
                    <button
                      onClick={handleLogout}
                      className="w-full text-left px-4 py-2 text-sm hover:bg-slate-800 rounded-b-lg transition"
                    >
                      Logout
                    </button>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          )}
        </div>
      </nav>

      {/* 🗂️ History Drawer */}
      <AnimatePresence>
        {menuOpen && (
          <>
            <motion.div
              key="overlay"
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.5 }}
              exit={{ opacity: 0 }}
              onClick={() => setMenuOpen(false)}
              className="fixed inset-0 bg-black/50 z-40 backdrop-blur-sm"
            />

            <motion.aside
              key="drawer"
              initial={{ x: "-100%" }}
              animate={{ x: 0 }}
              exit={{ x: "-100%" }}
              transition={{ type: "spring", stiffness: 120, damping: 18 }}
              className="fixed top-0 left-0 h-full w-80 bg-slate-900 text-slate-100 shadow-2xl border-r border-slate-800 z-50 flex flex-col"
            >
              <div className="flex items-center justify-between px-5 py-4 border-b border-slate-800">
                <h2 className="text-lg font-semibold text-indigo-400">
                  Search History
                </h2>
                <button
                  onClick={() => setMenuOpen(false)}
                  className="text-slate-400 hover:text-slate-200 transition"
                >
                  <X size={22} />
                </button>
              </div>

              <div className="flex-1 overflow-y-auto px-5 py-4 space-y-3 text-sm text-slate-300">
                {history.length > 0 ? (
                  history.map((h) => (
                    <button
                      key={h.id}
                      onClick={() => handleHistoryClick(h.id)}
                      className="flex items-center gap-2 w-full text-left p-2 rounded-md hover:bg-slate-800 transition"
                    >
                      <Clock size={16} className="text-cyan-400" />
                      <span className="truncate">{h.query}</span>
                    </button>
                  ))
                ) : (
                  <p className="text-slate-500">No search history yet.</p>
                )}
              </div>
            </motion.aside>
          </>
        )}
      </AnimatePresence>

      {/* 🧾 History Results */}
      {historyResults.length > 0 && (
        <div className="pt-20">
          <ResultsGrid items={historyResults} />
        </div>
      )}
    </>
  );
}
