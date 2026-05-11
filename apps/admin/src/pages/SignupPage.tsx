import { useState } from "react";
import { useNavigate, Link, Navigate } from "react-router-dom";
import { useAuthStore } from "../stores/authStore";
import { API_BASE } from "../lib/api";
import { Shield, ArrowRight, Loader2 } from "lucide-react";

export default function SignupPage() {
  const navigate = useNavigate();
  const setAuth = useAuthStore((s) => s.setAuth);
  const accessToken = useAuthStore((s) => s.accessToken);
  const [form, setForm] = useState({
    company_name: "", business_number: "", email: "", password: "", name: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  if (accessToken) return <Navigate to="/dashboard" replace />;

  const update = (k: string, v: string) => setForm((p) => ({ ...p, [k]: v }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const registerRes = await fetch(`${API_BASE}/api/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      if (!registerRes.ok) {
        const data = await registerRes.json();
        throw new Error(data.detail || "회원가입 실패");
      }
      const tokens = await registerRes.json();
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

  const fields = [
    { key: "company_name", label: "기업명", required: true, placeholder: "주식회사 OO" },
    { key: "business_number", label: "사업자등록번호", required: false, placeholder: "000-00-00000" },
    { key: "name", label: "담당자 이름", required: true, placeholder: "홍길동" },
    { key: "email", label: "이메일", required: true, placeholder: "admin@company.kr", type: "email" },
    { key: "password", label: "비밀번호", required: true, placeholder: "6자 이상", type: "password" },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-emerald-950 flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        <div className="flex items-center gap-3 mb-8 justify-center">
          <div className="w-10 h-10 bg-emerald-500 rounded-xl flex items-center justify-center">
            <Shield size={22} className="text-white" />
          </div>
          <span className="text-xl font-bold text-white">SafetyAI</span>
        </div>

        <h2 className="text-2xl font-bold text-white mb-1 text-center">기업 회원가입</h2>
        <p className="text-slate-400 text-sm mb-8 text-center">기업 정보를 등록하고 안전 관리를 시작하세요.</p>

        <form onSubmit={handleSubmit} className="space-y-3.5">
          {fields.map(({ key, label, required, placeholder, type }) => (
            <div key={key}>
              <label className="block text-sm font-medium text-slate-300 mb-1">
                {label} {required && <span className="text-emerald-400">*</span>}
              </label>
              <input
                type={type || "text"}
                value={(form as any)[key]}
                onChange={(e) => update(key, e.target.value)}
                className="w-full px-4 py-2.5 bg-slate-800/50 text-white rounded-xl border border-slate-700 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500/30 focus:outline-none transition-all placeholder-slate-500"
                placeholder={placeholder}
                required={required}
                minLength={key === "password" ? 6 : undefined}
              />
            </div>
          ))}

          {error && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-2.5">
              <p className="text-red-400 text-sm">{error}</p>
            </div>
          )}

          <button type="submit" disabled={loading}
            className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-medium disabled:opacity-50 transition-all flex items-center justify-center gap-2 shadow-lg shadow-emerald-600/20 mt-2">
            {loading ? <Loader2 size={18} className="animate-spin" /> : <>회원가입 <ArrowRight size={16} /></>}
          </button>
        </form>

        <p className="text-slate-500 text-sm text-center mt-8">
          이미 계정이 있으신가요?{" "}
          <Link to="/login" className="text-emerald-400 hover:text-emerald-300 font-medium transition-colors">
            로그인
          </Link>
        </p>
      </div>
    </div>
  );
}
