import { AxiosError } from "axios";
import { api } from "./index";
import type { SearchResponse } from "../../types/api";

export const orchestrate = async (instruction: string): Promise<SearchResponse> => {
  try {
    const token =
      "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsImV4cCI6MTc1OTgzNDY5Mn0.-4tRT5BTQ8pS-zxOPJllxjzOr-AVj7gw_rLW2zTTMOc";

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const res = await api.post<SearchResponse>("/orchestrate", { instruction }, { headers });
    return res.data;
  } catch (error) {
    if (error instanceof AxiosError) {
      const msg =
        error.response?.data?.detail ||
        error.message ||
        "Failed to fetch results.";
      console.error("❌ Orchestrate API error:", msg);
      throw new Error(msg);
    }
    throw new Error(`Unexpected error: ${String(error)}`);
  }
};
