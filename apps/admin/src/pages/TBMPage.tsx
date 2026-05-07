import { useState, useEffect } from "react";
import { apiFetch } from "../lib/api";
import { ClipboardCheck, Plus, UserCheck, Loader2 } from "lucide-react";

interface Site { id: string; name: string; }
interface TBM {
  id: string; date: string; process_name: string | null;
  agenda: { cautions: string[]; checklist: string[]; special_notes: string[] };
  attendees: { name: string; acknowledged: boolean; at: string | null }[];
  attendee_count: number;
}

export default function TBMPage() {
  const [sites, setSites] = useState<Site[]>([]);
  const [siteId, setSiteId] = useState("");
  const [tbm, setTbm] = useState<TBM | null>(null);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [attendName, setAttendName] = useState("");

  useEffect(() => {
    apiFetch("/api/sites").then(async r => {
      if (r.ok) { const d = await r.json(); setSites(d); if (d.length > 0) setSiteId(d[0].id); }
    });
  }, []);

  useEffect(() => {
    if (!siteId) return;
    setLoading(true);
    apiFetch(`/api/tbm/today?site_id=${siteId}`).then(async r => {
      if (r.ok) { const d = await r.json(); setTbm(d.session || d.id ? d : null); }
      setLoading(false);
    });
  }, [siteId]);

  const generate = async () => {
    if (!siteId) return;
    setGenerating(true);
    const r = await apiFetch("/api/tbm/generate", {
      method: "POST", body: JSON.stringify({ site_id: siteId }),
    });
    if (r.ok) setTbm(await r.json());
    setGenerating(false);
  };

  const attend = async () => {
    if (!tbm || !attendName.trim()) return;
    await apiFetch(`/api/tbm/${tbm.id}/attend`, {
      method: "POST", body: JSON.stringify({ user_name: attendName }),
    });
    setAttendName("");
    // 재조회
    const r = await apiFetch(`/api/tbm/today?site_id=${siteId}`);
    if (r.ok) { const d = await r.json(); setTbm(d.session || d.id ? d : null); }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <ClipboardCheck className="text-emerald-600" size={24} />
          <h1 className="text-2xl font-bold text-slate-900">TBM (작업 전 안전미팅)</h1>
        </div>
        <select value={siteId} onChange={e => setSiteId(e.target.value)}
          className="px-3 py-2 bg-white text-slate-700 rounded-xl border border-slate-200 text-sm">
          {sites.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
        </select>
      </div>

      {loading ? <p className="text-slate-400">로딩 중...</p> : !tbm ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center shadow-sm">
          <ClipboardCheck className="mx-auto text-slate-300 mb-4" size={48} />
          <p className="text-slate-500 mb-4">오늘의 TBM이 아직 생성되지 않았습니다.</p>
          <button onClick={generate} disabled={generating}
            className="inline-flex items-center gap-2 px-6 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-medium disabled:opacity-50 transition-colors">
            {generating ? <Loader2 size={16} className="animate-spin" /> : <Plus size={16} />}
            {generating ? "AI 생성 중..." : "오늘의 TBM 생성"}
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {/* 안건 */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-5">
            <div className="flex items-center justify-between">
              <h2 className="font-semibold text-slate-800">{tbm.date} TBM 안건</h2>
              {tbm.process_name && <span className="text-xs text-slate-400">{tbm.process_name}</span>}
            </div>

            {tbm.agenda.cautions.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-red-500 mb-2">주의사항</p>
                {tbm.agenda.cautions.map((c, i) => (
                  <p key={i} className="text-sm text-slate-700 flex items-start gap-2 mb-1">
                    <span className="text-red-400 mt-0.5">!</span>{c}
                  </p>
                ))}
              </div>
            )}

            {tbm.agenda.checklist.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-emerald-600 mb-2">점검 체크리스트</p>
                {tbm.agenda.checklist.map((c, i) => (
                  <p key={i} className="text-sm text-slate-700 flex items-start gap-2 mb-1">
                    <span className="text-emerald-500">□</span>{c}
                  </p>
                ))}
              </div>
            )}

            {tbm.agenda.special_notes.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-blue-500 mb-2">특별 유의사항</p>
                {tbm.agenda.special_notes.map((c, i) => (
                  <p key={i} className="text-sm text-slate-700 flex items-start gap-2 mb-1">
                    <span className="text-blue-400">★</span>{c}
                  </p>
                ))}
              </div>
            )}
          </div>

          {/* 참석 서명 */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
            <h3 className="font-semibold text-slate-800 mb-3">참석 서명 ({tbm.attendee_count}명)</h3>
            <div className="flex gap-2 mb-3">
              <input value={attendName} onChange={e => setAttendName(e.target.value)}
                className="flex-1 px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm" placeholder="이름 입력"
                onKeyDown={e => e.key === "Enter" && attend()} />
              <button onClick={attend} disabled={!attendName.trim()}
                className="px-4 py-2 bg-emerald-600 text-white rounded-xl text-sm disabled:opacity-40">
                <UserCheck size={16} />
              </button>
            </div>
            {tbm.attendees.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {tbm.attendees.map((a, i) => (
                  <span key={i} className="px-3 py-1 bg-emerald-50 text-emerald-700 rounded-lg text-xs font-medium">
                    {a.name} ✓
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
