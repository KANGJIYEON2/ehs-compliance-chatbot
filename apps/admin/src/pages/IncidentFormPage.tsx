import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch } from "../lib/api";

interface Site { id: string; name: string; }

const TYPES = [
  { value: "caught", label: "끼임" },
  { value: "fall", label: "추락" },
  { value: "collision", label: "충돌" },
  { value: "electric", label: "감전" },
  { value: "fire", label: "화재" },
  { value: "suffocation", label: "질식" },
  { value: "falling_object", label: "낙하물" },
  { value: "chemical", label: "화학물질" },
  { value: "other", label: "기타" },
];

const SEVERITIES = [
  { value: "death", label: "사망" },
  { value: "serious", label: "중상" },
  { value: "minor", label: "경상" },
  { value: "near_miss", label: "아차사고" },
];

export default function IncidentFormPage() {
  const navigate = useNavigate();
  const [sites, setSites] = useState<Site[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const [form, setForm] = useState({
    site_id: "",
    incident_type: "",
    severity: "",
    occurred_at: new Date().toISOString().slice(0, 16),
    description: "",
    cause_estimate: "",
    action_taken: "",
  });

  useEffect(() => {
    apiFetch("/api/sites").then(async (res) => {
      if (res.ok) {
        const data = await res.json();
        setSites(data);
        if (data.length === 1) setForm((f) => ({ ...f, site_id: data[0].id }));
      }
    });
  }, []);

  const update = (key: string, value: string) =>
    setForm((prev) => ({ ...prev, [key]: value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    const body = {
      ...form,
      occurred_at: new Date(form.occurred_at).toISOString(),
    };

    try {
      const res = await apiFetch("/api/incidents", {
        method: "POST",
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "등록 실패");
      }
      const incident = await res.json();
      navigate(`/incidents/${incident.id}`);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl">
      <h1 className="text-2xl font-bold text-white mb-6">사고/아차사고 등록</h1>

      <form onSubmit={handleSubmit} className="space-y-5">
        {/* 사업장 */}
        <div>
          <label className="block text-sm text-slate-300 mb-1">사업장 *</label>
          <select
            value={form.site_id}
            onChange={(e) => update("site_id", e.target.value)}
            className="w-full px-4 py-2 bg-slate-800 text-white rounded-lg border border-slate-700 focus:border-emerald-500 focus:outline-none"
            required
          >
            <option value="">선택</option>
            {sites.map((s) => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
          </select>
        </div>

        {/* 유형 + 심각도 */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-slate-300 mb-1">사고 유형 *</label>
            <select
              value={form.incident_type}
              onChange={(e) => update("incident_type", e.target.value)}
              className="w-full px-4 py-2 bg-slate-800 text-white rounded-lg border border-slate-700 focus:border-emerald-500 focus:outline-none"
              required
            >
              <option value="">선택</option>
              {TYPES.map((t) => (
                <option key={t.value} value={t.value}>{t.label}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm text-slate-300 mb-1">심각도 *</label>
            <select
              value={form.severity}
              onChange={(e) => update("severity", e.target.value)}
              className="w-full px-4 py-2 bg-slate-800 text-white rounded-lg border border-slate-700 focus:border-emerald-500 focus:outline-none"
              required
            >
              <option value="">선택</option>
              {SEVERITIES.map((s) => (
                <option key={s.value} value={s.value}>{s.label}</option>
              ))}
            </select>
          </div>
        </div>

        {/* 발생 일시 */}
        <div>
          <label className="block text-sm text-slate-300 mb-1">발생 일시 *</label>
          <input
            type="datetime-local"
            value={form.occurred_at}
            onChange={(e) => update("occurred_at", e.target.value)}
            className="w-full px-4 py-2 bg-slate-800 text-white rounded-lg border border-slate-700 focus:border-emerald-500 focus:outline-none"
            required
          />
        </div>

        {/* 사고 설명 */}
        <div>
          <label className="block text-sm text-slate-300 mb-1">사고 설명 *</label>
          <textarea
            value={form.description}
            onChange={(e) => update("description", e.target.value)}
            rows={4}
            className="w-full px-4 py-2 bg-slate-800 text-white rounded-lg border border-slate-700 focus:border-emerald-500 focus:outline-none resize-none"
            required
            placeholder="사고 발생 상황을 상세히 기술하세요"
          />
        </div>

        {/* 원인 추정 */}
        <div>
          <label className="block text-sm text-slate-300 mb-1">원인 추정</label>
          <textarea
            value={form.cause_estimate}
            onChange={(e) => update("cause_estimate", e.target.value)}
            rows={2}
            className="w-full px-4 py-2 bg-slate-800 text-white rounded-lg border border-slate-700 focus:border-emerald-500 focus:outline-none resize-none"
            placeholder="추정되는 사고 원인"
          />
        </div>

        {/* 조치 내용 */}
        <div>
          <label className="block text-sm text-slate-300 mb-1">조치 내용</label>
          <textarea
            value={form.action_taken}
            onChange={(e) => update("action_taken", e.target.value)}
            rows={2}
            className="w-full px-4 py-2 bg-slate-800 text-white rounded-lg border border-slate-700 focus:border-emerald-500 focus:outline-none resize-none"
            placeholder="현재까지 취한 조치 사항"
          />
        </div>

        {error && <p className="text-red-400 text-sm">{error}</p>}

        <div className="flex gap-3">
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm font-medium disabled:opacity-50 transition-colors"
          >
            {loading ? "등록 중..." : "사고 등록"}
          </button>
          <button
            type="button"
            onClick={() => navigate("/incidents")}
            className="px-6 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg text-sm transition-colors"
          >
            취소
          </button>
        </div>
      </form>
    </div>
  );
}
