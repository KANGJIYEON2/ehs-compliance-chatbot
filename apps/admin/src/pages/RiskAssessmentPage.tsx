import { useState, useEffect } from "react";
import { apiFetch } from "../lib/api";
import { FileSearch, Plus, Loader2, AlertTriangle, CheckCircle2, Shield } from "lucide-react";

interface Site { id: string; name: string; }
interface Assessment {
  id: string; process_name: string; task_name: string; task_description: string;
  risk_level: string; status: string; created_at: string;
  hazards: { factor: string; type: string; description: string }[];
  risk_matrix: { factor: string; frequency: number; severity: number; risk_score: number; level: string }[];
  measures: { factor: string; measure: string; type: string; priority: string }[];
  legal_basis: { law: string; article: string; requirement: string }[];
}

const RISK_COLORS: Record<string, string> = { high: "text-red-500", medium: "text-amber-500", low: "text-emerald-500" };
const RISK_BG: Record<string, string> = { high: "bg-red-50 border-red-200", medium: "bg-amber-50 border-amber-200", low: "bg-emerald-50 border-emerald-200" };
const STATUS_LABELS: Record<string, string> = { draft: "초안", reviewed: "검토완료", approved: "승인" };

export default function RiskAssessmentPage() {
  const [sites, setSites] = useState<Site[]>([]);
  const [siteId, setSiteId] = useState("");
  const [items, setItems] = useState<Assessment[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [selected, setSelected] = useState<Assessment | null>(null);
  const [form, setForm] = useState({ process_name: "", task_name: "", task_description: "" });

  useEffect(() => {
    apiFetch("/api/sites").then(async r => {
      if (r.ok) { const d = await r.json(); setSites(d); if (d.length > 0) setSiteId(d[0].id); }
    });
  }, []);

  const fetchList = async () => {
    if (!siteId) return;
    setLoading(true);
    const r = await apiFetch(`/api/risk-assessment?site_id=${siteId}`);
    if (r.ok) setItems(await r.json());
    setLoading(false);
  };

  useEffect(() => { fetchList(); }, [siteId]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!siteId) return;
    setGenerating(true);
    const r = await apiFetch("/api/risk-assessment", {
      method: "POST", body: JSON.stringify({ ...form, site_id: siteId }),
    });
    if (r.ok) {
      setSelected(await r.json());
      setShowForm(false);
      setForm({ process_name: "", task_name: "", task_description: "" });
      fetchList();
    }
    setGenerating(false);
  };

  if (selected) return (
    <div className="space-y-5">
      <button onClick={() => setSelected(null)} className="text-sm text-slate-500 hover:text-slate-700">← 목록으로</button>

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900">{selected.task_name}</h1>
          <p className="text-sm text-slate-500">{selected.process_name}</p>
        </div>
        <span className={`px-3 py-1 rounded-lg text-sm font-semibold ${RISK_COLORS[selected.risk_level]}`}>
          위험도: {selected.risk_level.toUpperCase()}
        </span>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
        <p className="text-xs font-semibold text-slate-500 mb-2">작업 내용</p>
        <p className="text-sm text-slate-700">{selected.task_description}</p>
      </div>

      {/* 유해위험요인 */}
      {selected.hazards.length > 0 && (
        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
          <p className="text-xs font-semibold text-red-500 mb-3 flex items-center gap-1"><AlertTriangle size={14}/>유해위험요인</p>
          <div className="space-y-2">
            {selected.hazards.map((h, i) => (
              <div key={i} className="bg-red-50 rounded-xl p-3 border border-red-100">
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 bg-red-100 text-red-600 rounded text-[10px] font-medium">{h.type}</span>
                  <span className="text-sm font-medium text-slate-800">{h.factor}</span>
                </div>
                <p className="text-xs text-slate-500 mt-1">{h.description}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 위험도 매트릭스 */}
      {selected.risk_matrix.length > 0 && (
        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
          <p className="text-xs font-semibold text-amber-600 mb-3">위험도 매트릭스</p>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-xs text-slate-500 border-b border-slate-100">
                  <th className="text-left py-2 pr-4">위험요인</th>
                  <th className="text-center px-2">빈도</th>
                  <th className="text-center px-2">강도</th>
                  <th className="text-center px-2">점수</th>
                  <th className="text-center px-2">등급</th>
                </tr>
              </thead>
              <tbody>
                {selected.risk_matrix.map((r, i) => (
                  <tr key={i} className="border-b border-slate-50">
                    <td className="py-2 pr-4 text-slate-700">{r.factor}</td>
                    <td className="text-center text-slate-600">{r.frequency}</td>
                    <td className="text-center text-slate-600">{r.severity}</td>
                    <td className="text-center font-semibold">{r.risk_score}</td>
                    <td className={`text-center font-semibold ${RISK_COLORS[r.level]}`}>{r.level}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* 감소대책 */}
      {selected.measures.length > 0 && (
        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
          <p className="text-xs font-semibold text-emerald-600 mb-3 flex items-center gap-1"><Shield size={14}/>감소대책</p>
          <div className="space-y-2">
            {selected.measures.map((m, i) => (
              <div key={i} className="flex items-start gap-3 p-3 bg-emerald-50 rounded-xl border border-emerald-100">
                <CheckCircle2 size={16} className="text-emerald-500 mt-0.5 shrink-0" />
                <div>
                  <p className="text-sm text-slate-800">{m.measure}</p>
                  <div className="flex gap-2 mt-1">
                    <span className="text-[10px] text-emerald-600 bg-emerald-100 px-1.5 py-0.5 rounded">{m.type}</span>
                    <span className="text-[10px] text-slate-400">{m.factor}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 법령 근거 */}
      {selected.legal_basis.length > 0 && (
        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
          <p className="text-xs font-semibold text-amber-600 mb-3">관련 법령</p>
          {selected.legal_basis.map((l, i) => (
            <div key={i} className="mb-2">
              <p className="text-sm font-medium text-slate-800">{l.law} {l.article}</p>
              <p className="text-xs text-slate-500">{l.requirement}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <FileSearch className="text-amber-500" size={24} />
          <h1 className="text-2xl font-bold text-slate-900">위험성평가</h1>
        </div>
        <div className="flex items-center gap-3">
          <select value={siteId} onChange={e => setSiteId(e.target.value)}
            className="px-3 py-2 bg-white text-slate-700 rounded-xl border border-slate-200 text-sm">
            {sites.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
          <button onClick={() => setShowForm(!showForm)}
            className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-sm transition-colors">
            <Plus size={16} /> 새 평가
          </button>
        </div>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-slate-600 mb-1">공정명 *</label>
              <input value={form.process_name} onChange={e => setForm({ ...form, process_name: e.target.value })}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm" required placeholder="프레스 공정" />
            </div>
            <div>
              <label className="block text-sm text-slate-600 mb-1">작업명 *</label>
              <input value={form.task_name} onChange={e => setForm({ ...form, task_name: e.target.value })}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm" required placeholder="금형 교체 작업" />
            </div>
          </div>
          <div>
            <label className="block text-sm text-slate-600 mb-1">작업 내용 *</label>
            <textarea value={form.task_description} onChange={e => setForm({ ...form, task_description: e.target.value })}
              rows={3} className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm resize-none" required
              placeholder="구체적인 작업 절차와 사용 장비를 기술하세요" />
          </div>
          <button type="submit" disabled={generating}
            className="flex items-center gap-2 px-6 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-sm disabled:opacity-50 transition-colors">
            {generating ? <><Loader2 size={16} className="animate-spin" /> AI 분석 중...</> : "위험성평가 실시"}
          </button>
        </form>
      )}

      {loading ? <p className="text-slate-400">로딩 중...</p> : items.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center shadow-sm">
          <FileSearch className="mx-auto text-slate-300 mb-4" size={48} />
          <p className="text-slate-500">위험성평가 기록이 없습니다.</p>
          <p className="text-slate-400 text-sm mt-1">위 버튼으로 AI 기반 위험성평가를 시작하세요.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {items.map(a => (
            <button key={a.id} onClick={() => setSelected(a)}
              className="w-full text-left bg-white rounded-xl border border-slate-200 p-4 hover:border-slate-300 hover:shadow-sm transition-all">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-slate-800">{a.task_name}</p>
                  <p className="text-xs text-slate-400">{a.process_name} · {new Date(a.created_at).toLocaleDateString("ko-KR")}</p>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`text-xs px-2 py-0.5 rounded ${RISK_BG[a.risk_level]}`}>{a.risk_level}</span>
                  <span className="text-[10px] text-slate-400">{STATUS_LABELS[a.status]}</span>
                </div>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
