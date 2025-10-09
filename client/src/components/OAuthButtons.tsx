const API_URL = "http://localhost:8000";

export default function OAuthButtons() {
  return (
    <div className="flex flex-col gap-3 mt-4">
      <a
        href={`${API_URL}/api/auth/google/login`}
        className="w-full text-center px-4 py-2 rounded-lg border border-gray-700 hover:bg-gray-800 transition"
      >
        Continue with Google
      </a>
      <a
        href={`${API_URL}/api/auth/github/login`}
        className="w-full text-center px-4 py-2 rounded-lg border border-gray-700 hover:bg-gray-800 transition"
      >
        Continue with GitHub
      </a>
    </div>
  );
}
