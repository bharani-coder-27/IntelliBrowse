import { api } from "./index";
import type { User } from "../../types/user";

export const login = async (email: string, password: string) => {
  return await api.post("/auth/login", { email, password });
};

export const register = async (name: string, email: string, password: string) => {
  return await api.post("/auth/register", { name, email, password });
};

export const logout = async () => {
  return await api.post("/auth/logout");
};

export const getCurrentUser = async (): Promise<{ user: User | null }> => {
  const res = await api.get("/auth/me");
  return res.data;
};
