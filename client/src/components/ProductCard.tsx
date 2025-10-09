import { motion } from "framer-motion";
import { ExternalLink, Star, Check } from "lucide-react";
import type { Product } from "../types/product";

type ProductCardProps = {
  p: Product;
  i: number;
  selected: boolean;
  selectionMode: boolean;
  onSelect: (index: number) => void;
};

export default function ProductCard({
  p,
  i,
  selected,
  selectionMode,
  onSelect,
}: ProductCardProps) {
  const handleSelectClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.stopPropagation();
    e.preventDefault();
    onSelect(i);
  };

  return (
    <motion.div
      className={`relative group overflow-hidden flex flex-col transition-shadow rounded-2xl border ${
        selected
          ? "border-cyan-400 shadow-[0_0_20px_rgba(56,189,248,0.25)]"
          : "border-white/10 hover:border-cyan-400/40"
      }`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: i * 0.05 }}
    >
      {/* Show select toggle only in selection mode */}
      {selectionMode && (
        <button
          onClick={handleSelectClick}
          className={`absolute top-3 right-3 z-20 w-6 h-6 rounded-full border-2 flex items-center justify-center transition ${
            selected
              ? "bg-cyan-400 border-cyan-400 text-white"
              : "bg-gray-900/60 border-gray-300/60 text-transparent hover:text-white"
          }`}
          title={selected ? "Deselect" : "Select"}
        >
          <Check size={14} />
        </button>
      )}

      {/* Product Card */}
      <a
        href={p.link}
        target="_blank"
        rel="noreferrer"
        className="block relative h-48 overflow-hidden"
      >
        <img
          src={p.image || "/assets/sample-product.jpg"}
          alt={p.title}
          className="object-cover w-full h-full group-hover:scale-105 transition-transform duration-500"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover:opacity-100 transition" />
      </a>

      <div className="p-4 flex flex-col gap-1">
        <div className="text-xs uppercase text-slate-500 dark:text-slate-400">
          {p.site || "Store"}
        </div>
        <div className="font-semibold line-clamp-2">{p.title}</div>
        <div className="text-lg font-bold text-cyan-400">{p.price}</div>
        <div className="flex items-center gap-1 text-sm text-yellow-400">
          <Star size={14} fill="currentColor" className="text-yellow-400" />
          <span>{p.rating || "No rating"}</span>
        </div>
        <div className="inline-flex items-center gap-1 text-cyan-500 text-sm mt-1">
          <ExternalLink size={14} /> View
        </div>
      </div>
    </motion.div>
  );
}
