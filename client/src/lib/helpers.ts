import axios, { AxiosError } from "axios";
import type { SearchResponse } from "../types/api";

const API_BASE = "http://localhost:8000/api";

export const orchestrate = async (instruction: string): Promise<SearchResponse> => {
  try {
    const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsImV4cCI6MTc1OTgzNDY5Mn0.-4tRT5BTQ8pS-zxOPJllxjzOr-AVj7gw_rLW2zTTMOc";
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const response = await axios.post<SearchResponse>(
      `${API_BASE}/orchestrate`,
      { instruction },
      { headers }
    );

    return response.data;
  } catch (error) {
    // ✅ Properly typed error handling
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<{ detail?: string }>;
      const message =
        axiosError.response?.data?.detail ||
        axiosError.message ||
        "Failed to fetch results.";
      console.error("❌ Orchestrate API error:", message);
      throw new Error(message);
    } else {
      // eslint-disable-next-line @typescript-eslint/restrict-template-expressions
      throw new Error(`Unexpected error: ${String(error)}`);
    }
  }
};
