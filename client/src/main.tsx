// src/main.tsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import "./index.css";
import App from "./App.tsx";
import { Toaster } from "sonner";

import Login from "./pages/Login.tsx";
import Register from "./pages/Register.tsx";
import Navbar from "./components/Navbar.tsx";
import ComparePage from "./pages/ComparePage.tsx";

import { AuthProvider } from "./context/AuthContext.tsx";
import { SearchProvider } from "./context/SearchContext.tsx"; // ✅ import added

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <SearchProvider> {/* ✅ wrap everything inside SearchProvider */}
          <Navbar />
          <Routes>
            <Route path="/" element={<App />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/compare" element={<ComparePage />} />
          </Routes>
          <Toaster position="top-right" richColors expand />
        </SearchProvider>
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>
);
