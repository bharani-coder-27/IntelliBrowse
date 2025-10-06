import { motion } from "framer-motion";
import type { Product } from "../types/product";

export default function ResultsGrid({ items }: { items: Product[] }) {
  const fallbackImage = "/assets/sample-product.jpg";

  return (
    <motion.div
      layout
      className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 mt-10"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6 }}
    >
      {items.map((p, i) => (
        <motion.a
          key={i}
          href={p.link}
          target="_blank"
          rel="noreferrer"
          whileHover={{ y: -5, scale: 1.02 }}
          transition={{ type: "spring", stiffness: 200, damping: 10 }}
          className="group card overflow-hidden flex flex-col bg-white/5 dark:bg-slate-800/40 rounded-2xl border border-white/10 hover:border-cyan-400/40 hover:shadow-[0_0_20px_rgba(56,189,248,0.15)]"
        >
          <div className="relative h-48 overflow-hidden">
            <img
              src={p.image || fallbackImage}
              alt={p.title}
              className="object-cover w-full h-full group-hover:scale-105 transition-transform duration-500"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover:opacity-100 transition" />
          </div>

          <div className="p-4 flex flex-col gap-1">
            <div className="text-xs uppercase text-slate-400">
              {p.site || "Store"}
            </div>
            <div className="font-semibold text-slate-100 line-clamp-2 group-hover:text-cyan-400 transition">
              {p.title}
            </div>
            <div className="text-lg font-bold text-cyan-400">{p.price}</div>
            <div className="text-sm text-slate-400">
              {p.rating || "No rating"}
            </div>
          </div>
        </motion.a>
      ))}
    </motion.div>
  );
}
