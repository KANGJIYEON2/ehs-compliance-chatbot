import { useState } from "react";
import { useNavigate, Link, Navigate } from "react-router-dom";
import { useAuthStore } from "../stores/authStore";
import { API_BASE } from "../lib/api";
import { Shield, ArrowRight, Loader2 } from "lucide-react";

export default function LoginPage() {
  const navigate = useNavigate();
  const setAuth = useAuthStore((s) => s.setAuth);
  const accessToken = useAuthStore((s) => s.accessToken);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  if (accessToken) return <Navigate to="/dashboard" replace />;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const loginRes = await fetch(`${API_BASE}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      if (!loginRes.ok) {
        const data = await loginRes.json();
        throw new Error(data.detail || "로그인 실패");
      }
      const tokens = await loginRes.json();
      const meRes = await fetch(`${API_BASE}/api/auth/me`, {
        headers: { Authorization: `Bearer ${tokens.access_token}` },
      });
      if (!meRes.ok) throw new Error("사용자 정보 조회 실패");
      setAuth(tokens, await meRes.json());
      navigate("/dashboard");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-emerald-950 flex">
      {/* 왼쪽 브랜딩 */}
      <div className="hidden lg:flex lg:w-1/2 flex-col justify-between p-12">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-emerald-500 rounded-xl flex items-center justify-center">
            <Shield size={22} className="text-white" />
          </div>
          <span className="text-xl font-bold text-white">SafetyAI</span>
        </div>

        <div className="space-y-6">
          <h1 className="text-4xl font-bold text-white leading-tight">
            AI 기반<br />
            산업안전 리스크 관리<br />
            <span className="text-emerald-400">플랫폼</span>
          </h1>
          <p className="text-slate-400 text-lg max-w-md">
            사고 데이터 분석, AI 예방 조치, 법령 근거 자동 생성까지.
            산업 현장의 안전을 데이터로 관리하세요.
          </p>
          <div className="flex gap-6 text-sm">
            <div className="space-y-1">
              <p className="text-2xl font-bold text-emerald-400">40+</p>
              <p className="text-slate-500">API 엔드포인트</p>
            </div>
            <div className="space-y-1">
              <p className="text-2xl font-bold text-emerald-400">4</p>
              <p className="text-slate-500">AI 에이전트</p>
            </div>
            <div className="space-y-1">
              <p className="text-2xl font-bold text-emerald-400">5</p>
              <p className="text-slate-500">다국어 지원</p>
            </div>
          </div>
        </div>

        <p className="text-slate-600 text-xs">EHS Risk Management Platform v2.0</p>
      </div>

      {/* 오른쪽 로그인 폼 */}
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-sm">
          {/* 모바일 로고 */}
          <div className="lg:hidden flex items-center gap-3 mb-8 justify-center">
            <div className="w-10 h-10 bg-emerald-500 rounded-xl flex items-center justify-center">
              <Shield size={22} className="text-white" />
            </div>
            <span className="text-xl font-bold text-white">SafetyAI</span>
          </div>

          <h2 className="text-2xl font-bold text-white mb-1">로그인</h2>
          <p className="text-slate-400 text-sm mb-8">계정에 로그인하여 관리 시스템에 접속하세요.</p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">이메일</label>
              <input
                type="email" value={email} onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-2.5 bg-slate-800/50 text-white rounded-xl border border-slate-700 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500/30 focus:outline-none transition-all placeholder-slate-500"
                placeholder="admin@company.kr" required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">비밀번호</label>
              <input
                type="password" value={password} onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-2.5 bg-slate-800/50 text-white rounded-xl border border-slate-700 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500/30 focus:outline-none transition-all placeholder-slate-500"
                placeholder="6자 이상" required
              />
            </div>

            {error && (
              <div className="bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-2.5">
                <p className="text-red-400 text-sm">{error}</p>
              </div>
            )}

            <button
              type="submit" disabled={loading}
              className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-medium disabled:opacity-50 transition-all flex items-center justify-center gap-2 shadow-lg shadow-emerald-600/20"
            >
              {loading ? <Loader2 size={18} className="animate-spin" /> : <>로그인 <ArrowRight size={16} /></>}
            </button>
          </form>

          <div className="mt-8 text-center">
            <p className="text-slate-500 text-sm">
              계정이 없으신가요?{" "}
              <Link to="/signup" className="text-emerald-400 hover:text-emerald-300 font-medium transition-colors">
                기업 회원가입
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
