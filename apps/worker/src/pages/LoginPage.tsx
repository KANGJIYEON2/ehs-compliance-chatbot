import { useState } from "react";
import { useNavigate, Navigate } from "react-router-dom";
import { useAuthStore } from "../stores/authStore";
import { API_BASE } from "../lib/api";
import { Shield, Loader2 } from "lucide-react";

export default function LoginPage() {
  const navigate = useNavigate();
  const setAuth = useAuthStore((s) => s.setAuth);
  const accessToken = useAuthStore((s) => s.accessToken);
  if (accessToken) return <Navigate to="/" replace />;

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const r = await fetch(`${API_BASE}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      if (!r.ok) throw new Error((await r.json()).detail || "로그인 실패");
      const tokens = await r.json();
      const me = await fetch(`${API_BASE}/api/auth/me`, {
        headers: { Authorization: `Bearer ${tokens.access_token}` },
      });
      if (!me.ok) throw new Error("사용자 정보 조회 실패");
      setAuth(tokens, await me.json());
      navigate("/");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-6">
      <div className="w-12 h-12 bg-emerald-500 rounded-2xl flex items-center justify-center mb-4">
        <Shield size={26} className="text-white" />
      </div>
      <h1 className="text-xl font-bold text-white mb-1">SafetyAI</h1>
      <p className="text-slate-500 text-sm mb-8">작업자 로그인</p>

      <form onSubmit={handleSubmit} className="w-full max-w-sm space-y-4">
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)}
          className="w-full px-4 py-3 bg-slate-900 text-white rounded-2xl border border-slate-800 focus:border-emerald-500 focus:outline-none"
          placeholder="이메일" required />
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)}
          className="w-full px-4 py-3 bg-slate-900 text-white rounded-2xl border border-slate-800 focus:border-emerald-500 focus:outline-none"
          placeholder="비밀번호" required />
        {error && <p className="text-red-400 text-sm text-center">{error}</p>}
        <button type="submit" disabled={loading}
          className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-2xl font-medium disabled:opacity-50 transition-all">
          {loading ? <Loader2 size={18} className="animate-spin mx-auto" /> : "로그인"}
        </button>
      </form>
    </div>
  );
}
