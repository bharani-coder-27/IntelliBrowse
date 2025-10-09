import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import { useState } from "react";

export default function UserMenu() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  if (!user) {
    // 🧭 Not logged in: show Login and Register buttons
    return (
      <div className="flex items-center gap-3">
        <button
          onClick={() => navigate("/login")}
          className="px-4 py-2 rounded-full bg-indigo-500 hover:bg-indigo-600 text-white font-medium transition"
        >
          Login
        </button>
        <button
          onClick={() => navigate("/register")}
          className="px-4 py-2 rounded-full border border-fuchsia-500 text-fuchsia-400 hover:bg-fuchsia-500/10 font-medium transition"
        >
          Register
        </button>
      </div>
    );
  }

  // ✅ Logged in: show avatar circle
  const initial = user.name ? user.name.charAt(0).toUpperCase() : "?";

  return (
    <div className="relative">
      <div
        className="w-10 h-10 rounded-full bg-gradient-to-r from-indigo-500 to-fuchsia-500 flex items-center justify-center text-white font-semibold cursor-pointer select-none"
        onClick={() => setOpen(!open)}
      >
        {user.avatar_url ? (
          <img
            src={user.avatar_url}
            alt={user.name}
            className="w-10 h-10 rounded-full object-cover border border-slate-700"
          />
        ) : (
          initial
        )}
      </div>

      {open && (
        <div className="absolute right-0 mt-2 w-40 bg-slate-800 text-slate-100 rounded-lg shadow-lg border border-slate-700">
          <div className="px-4 py-2 text-sm border-b border-slate-700">
            Hi, {user.name.split(" ")[0]}
          </div>
          <button
            onClick={handleLogout}
            className="w-full text-left px-4 py-2 text-sm hover:bg-slate-700 rounded-b-lg"
          >
            Logout
          </button>
        </div>
      )}
    </div>
  );
}
