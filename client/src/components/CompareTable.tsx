import { motion } from "framer-motion";
import type { ProductRecord } from "../types/product";

export default function CompareTable({ products }: { products: ProductRecord[] }) {
  const attributes: (keyof ProductRecord)[] = [
    "price",
    "rating",
    "site",
    "source",
    "specs",
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="overflow-x-auto rounded-2xl border border-gray-800 bg-white/5 backdrop-blur-md shadow-lg"
    >
      <table className="min-w-full border-collapse text-left">
        <thead className="bg-slate-800/40 text-slate-300">
          <tr>
            <th className="px-4 py-3 border-b border-gray-700 text-sm font-semibold">
              Attribute
            </th>
            {products.map((p) => (
              <th
                key={p.id}
                className="px-4 py-3 border-b border-gray-700 text-center text-sm font-semibold"
              >
                <div className="flex flex-col items-center">
                  <img
                    src={p.image || "/assets/sample-product.jpg"}
                    alt={p.title}
                    className="w-20 h-20 object-cover rounded-lg mb-2 border border-gray-700"
                  />
                  <p className="text-slate-100 text-sm font-medium line-clamp-2">
                    {p.title}
                  </p>
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {attributes.map((attr) => (
            <tr key={attr} className="border-t border-gray-800">
              <td className="px-4 py-3 font-semibold text-slate-400 capitalize">
                {attr}
              </td>
              {products.map((p) => (
                <td key={`${p.id}-${attr}`} className="px-4 py-3 text-center">
                  {attr === "specs" ? (
                    <div className="text-xs text-slate-300 text-left whitespace-pre-wrap max-w-[250px] mx-auto">
                      {p.specs || "—"}
                    </div>
                  ) : attr === "source" || attr === "site" ? (
                    <span className="capitalize text-cyan-400 font-medium">
                      {p[attr] || "—"}
                    </span>
                  ) : attr === "rating" ? (
                    <span className="text-yellow-400 font-medium">
                      ⭐ {p.rating || "—"}
                    </span>
                  ) : (
                    <span className="text-slate-200">{p[attr] || "—"}</span>
                  )}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </motion.div>
  );
}
