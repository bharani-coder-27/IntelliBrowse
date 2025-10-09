import React, { createContext, useState, useEffect, useContext } from "react";
import { api } from "../lib/api/index";
import type { User } from "../types/user";

/* eslint-disable react-refresh/only-export-components */
interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  fetchMe: () => Promise<void>;
}

// ✅ Fix: use undefined for initial context (no `any`)
const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchMe = async () => {
    try {
      const res = await api.get("/auth/me");
      setUser(res.data.user || null);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void fetchMe();
  }, []);

  const login = async (email: string, password: string) => {
    await api.post("/auth/login", { email, password });
    await fetchMe();
  };

  const register = async (name: string, email: string, password: string) => {
    await api.post("/auth/register", { name, email, password });
    await fetchMe();
  };

  const logout = async () => {
    await api.post("/auth/logout");
    setUser(null);
  };

  const value: AuthContextType = { user, loading, login, register, logout, fetchMe };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// ✅ Strict, type-safe hook
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
