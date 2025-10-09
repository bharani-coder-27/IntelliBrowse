import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { useAuth } from "../context/AuthContext";
import FormField from "../components/FormField";
import OAuthButtons from "../components/OAuthButtons";
import { AxiosError } from "axios";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    setErr(null);
    try {
      await register(form.name, form.email, form.password);
      navigate("/");
    } catch (error) {
      const axiosError = error as AxiosError<{ detail?: string }>;
      const message =
        axiosError.response?.data?.detail ??
        axiosError.message ??
        "Registration failed";
      setErr(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-black text-white px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md bg-gray-900 border border-gray-800 rounded-2xl p-6 shadow-xl"
      >
        <h1 className="text-2xl font-semibold mb-1">Create Account</h1>
        <p className="text-gray-400 mb-6">Join IntelliBrowse</p>

        {err && <div className="text-red-400 mb-3 text-sm">{err}</div>}

        <form onSubmit={submit} className="flex flex-col gap-4">
          <FormField
            label="Name"
            value={form.name}
            onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
            required
          />
          <FormField
            label="Email"
            type="email"
            value={form.email}
            onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
            required
          />
          <FormField
            label="Password"
            type="password"
            value={form.password}
            onChange={(e) =>
              setForm((f) => ({ ...f, password: e.target.value }))
            }
            required
          />
          <button
            disabled={loading}
            className="mt-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 py-2 transition"
          >
            {loading ? "Creating..." : "Register"}
          </button>
        </form>

        <div className="mt-6 flex items-center gap-3">
          <div className="flex-1 h-px bg-gray-700"></div>
          <span className="text-xs text-gray-400">or</span>
          <div className="flex-1 h-px bg-gray-700"></div>
        </div>

        <OAuthButtons />

        <p className="text-sm text-gray-400 mt-6 text-center">
          Already have an account?{" "}
          <Link to="/login" className="text-indigo-400 hover:underline">
            Login
          </Link>
        </p>
      </motion.div>
    </div>
  );
}
