// src/types/product.ts
export type Product = {
  title: string;
  price: string;
  price_value?: number;
  rating?: string;
  link: string;
  site?: "amazon" | "flipkart";
  image?: string | null; // ✅ added optional image field
};
