import { Moon, Sun } from "lucide-react";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";

export default function ThemeToggle() {
  const [theme, setTheme] = useState(localStorage.getItem("theme") ?? "light");

  useEffect(() => {
    const html = document.documentElement;
    html.classList.toggle("dark", theme === "dark");
    document.body.style.backgroundColor =
      theme === "dark" ? "#0f172a" : "#f9fafb"; // ✅ prevent scrollbar flash
    localStorage.setItem("theme", theme);
  }, [theme]);

  return (
    <motion.button
      whileTap={{ scale: 0.9 }}
      onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
      className="p-2 rounded-xl bg-white/70 dark:bg-slate-800/70 shadow hover:shadow-md"
    >
      {theme === "dark" ? (
        <Sun className="text-yellow-400" size={18} />
      ) : (
        <Moon className="text-slate-700" size={18} />
      )}
    </motion.button>
  );
}
