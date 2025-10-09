export type Product = {
  title: string;
  price: string;
  price_value?: number;
  rating?: string;
  link: string;
  site?: "amazon" | "flipkart";
  image?: string | null;
};

// ✅ DB version (with id + optional extras)
export type ProductRecord = Product & {
  id: number;
  source?: string;
  specs?: string | null;
  url?: string | null;
};

// ✅ Compare API response type
export type CompareResponse = {
  total_compared: number;
  products: ProductRecord[];
  summary?: string;
  message?: string;
};
