import { motion } from "framer-motion";
import type { Product } from "../types/product";
import { ExternalLink, Star } from "lucide-react";

export default function ProductCard({ p, i }: { p: Product; i: number }) {
  return (
    <motion.a
      href={p.link}
      target="_blank"
      rel="noreferrer"
      className="card group overflow-hidden flex flex-col hover:shadow-2xl transition-shadow"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: i * 0.05 }}
    >
      <div className="relative h-48 overflow-hidden">
        <img
          src={p.image || "/assets/sample-product.jpg"}
          alt={p.title}
          className="object-cover w-full h-full group-hover:scale-105 transition-transform duration-500"
        />

        <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover:opacity-100 transition" />
      </div>

      <div className="p-4 flex flex-col gap-1">
        <div className="text-xs uppercase text-slate-500 dark:text-slate-400">
          {p.site}
        </div>
        <div className="font-semibold line-clamp-2">{p.title}</div>
        <div className="text-lg font-bold text-brand-500">{p.price}</div>
        <div className="flex items-center gap-1 text-sm text-yellow-400">
          <Star size={14} fill="currentColor" className="text-yellow-400" />
          <span>{p.rating || "No rating"}</span>
        </div>
        <div className="inline-flex items-center gap-1 text-brand-600 text-sm mt-1">
          <ExternalLink size={14} /> View
        </div>
      </div>
    </motion.a>
  );
}
