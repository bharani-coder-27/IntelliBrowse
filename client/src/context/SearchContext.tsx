import { createContext, useContext, useState, useEffect } from "react";
import type { ProductRecord } from "../types/product";
import type { SearchResponse } from "../types/api";

/* eslint-disable react-refresh/only-export-components */
interface SearchContextType {
  products: ProductRecord[];
  setProducts: (p: ProductRecord[]) => void;
  hasResults: boolean;
  setHasResults: (b: boolean) => void;
  isSessionActive: boolean;
  setIsSessionActive: (b: boolean) => void;
  lastResponse: SearchResponse | null;
  setLastResponse: (data: SearchResponse | null) => void;
}

const SearchContext = createContext<SearchContextType | null>(null);

export const SearchProvider = ({ children }: { children: React.ReactNode }) => {
  const [products, setProducts] = useState<ProductRecord[]>([]);
  const [hasResults, setHasResults] = useState(false);
  const [isSessionActive, setIsSessionActive] = useState<boolean>(
    () => sessionStorage.getItem("isSessionActive") === "true"
  );
  const [lastResponse, setLastResponse] = useState<SearchResponse | null>(null);

  // persist session state
  useEffect(() => {
    sessionStorage.setItem("isSessionActive", String(isSessionActive));
  }, [isSessionActive]);

  return (
    <SearchContext.Provider
      value={{
        products,
        setProducts,
        hasResults,
        setHasResults,
        isSessionActive,
        setIsSessionActive,
        lastResponse,
        setLastResponse,
      }}
    >
      {children}
    </SearchContext.Provider>
  );
};

export const useSearch = () => {
  const ctx = useContext(SearchContext);
  if (!ctx) throw new Error("useSearch must be used within SearchProvider");
  return ctx;
};
