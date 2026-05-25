import { useState, useEffect } from "react";
import { apiFetch } from "../lib/api";
import { MessageSquareWarning, CheckCircle2, Clock } from "lucide-react";

interface Report {
  id: string;
  site_id: string;
  content: string;
  location_hint: string | null;
  risk_level: string;
  ai_category: string | null;
  status: string;
  admin_response: string | null;
  created_at: string;
  resolved_at: string | null;
}

const RISK_LABELS: Record<string, string> = {
  critical: "긴급", warning: "주의", improvement: "개선",
};
const RISK_COLORS: Record<string, string> = {
  critical: "bg-red-600", warning: "bg-amber-500", improvement: "bg-blue-500",
};
const STATUS_LABELS: Record<string, string> = {
  received: "접수", reviewing: "검토중", resolved: "조치완료",
};
const TYPE_LABELS: Record<string, string> = {
  caught: "끼임", fall: "추락", collision: "충돌", electric: "감전",
  fire: "화재", suffocation: "질식", falling_object: "낙하물",
  chemical: "화학물질", other: "기타",
};

export default function AnonymousReportsPage() {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [response, setResponse] = useState("");
  const [filterStatus, setFilterStatus] = useState("");

  const fetchReports = async () => {
    const params = filterStatus ? `?status=${filterStatus}` : "";
    const res = await apiFetch(`/api/anonymous-reports/admin${params}`);
    if (res.ok) setReports(await res.json());
    setLoading(false);
  };

  useEffect(() => { fetchReports(); }, [filterStatus]);

  const handleAction = async (reportId: string, status: string) => {
    const body: any = { status };
    if (response.trim()) body.admin_response = response;

    const res = await apiFetch(`/api/anonymous-reports/admin/${reportId}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    });
    if (res.ok) {
      setSelectedId(null);
      setResponse("");
      fetchReports();
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <MessageSquareWarning className="text-amber-400" size={24} />
        <h1 className="text-2xl font-bold text-white">익명 제보 관리</h1>
      </div>

      {/* 필터 */}
      <div className="flex gap-3">
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="px-3 py-2 bg-slate-800 text-white rounded-lg border border-slate-700 text-sm"
        >
          <option value="">전체 상태</option>
          {Object.entries(STATUS_LABELS).map(([k, v]) => (
            <option key={k} value={k}>{v}</option>
          ))}
        </select>
        <span className="text-slate-400 text-sm self-center ml-auto">{reports.length}건</span>
      </div>

      {loading ? (
        <p className="text-slate-400">로딩 중...</p>
      ) : reports.length === 0 ? (
        <div className="bg-slate-800 rounded-xl p-12 border border-slate-700 text-center">
          <MessageSquareWarning className="mx-auto text-slate-500 mb-3" size={40} />
          <p className="text-slate-400">접수된 제보가 없습니다.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {reports.map((r) => (
            <div key={r.id} className="bg-slate-800 rounded-xl border border-slate-700 p-5 space-y-3">
              {/* 헤더 */}
              <div className="flex items-center gap-2 flex-wrap">
                <span className={`px-2 py-0.5 rounded text-xs text-white ${RISK_COLORS[r.risk_level] || "bg-slate-500"}`}>
                  {RISK_LABELS[r.risk_level] || r.risk_level}
                </span>
                {r.ai_category && (
                  <span className="px-2 py-0.5 bg-emerald-600/20 text-emerald-400 rounded text-xs">
                    {TYPE_LABELS[r.ai_category] || r.ai_category}
                  </span>
                )}
                <span className="flex items-center gap-1 text-xs text-slate-400">
                  {r.status === "resolved" ? <CheckCircle2 size={12} className="text-emerald-400" /> : <Clock size={12} />}
                  {STATUS_LABELS[r.status]}
                </span>
                <span className="text-xs text-slate-500 ml-auto">
                  {new Date(r.created_at).toLocaleString("ko-KR")}
                </span>
              </div>

              {/* 내용 */}
              <p className="text-white text-sm whitespace-pre-wrap">{r.content}</p>
              {r.location_hint && (
                <p className="text-slate-400 text-xs">위치: {r.location_hint}</p>
              )}

              {/* 관리자 응답 (이미 있으면) */}
              {r.admin_response && (
                <div className="bg-emerald-900/20 border border-emerald-700/30 rounded-lg p-3">
                  <p className="text-xs text-emerald-400 mb-1">관리자 응답</p>
                  <p className="text-sm text-slate-300">{r.admin_response}</p>
                </div>
              )}

              {/* 조치 입력 */}
              {r.status !== "resolved" && (
                <>
                  {selectedId === r.id ? (
                    <div className="space-y-2">
                      <textarea
                        value={response}
                        onChange={(e) => setResponse(e.target.value)}
                        placeholder="조치 내용을 입력하세요 (제보자에게 전달됩니다)"
                        rows={2}
                        className="w-full px-3 py-2 bg-slate-700 text-white rounded-lg border border-slate-600 text-sm resize-none focus:outline-none focus:border-emerald-500"
                      />
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleAction(r.id, "reviewing")}
                          className="px-3 py-1.5 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-xs transition-colors"
                        >
                          검토중으로 변경
                        </button>
                        <button
                          onClick={() => handleAction(r.id, "resolved")}
                          className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs transition-colors"
                        >
                          조치 완료
                        </button>
                        <button
                          onClick={() => { setSelectedId(null); setResponse(""); }}
                          className="px-3 py-1.5 bg-slate-700 text-white rounded-lg text-xs transition-colors"
                        >
                          취소
                        </button>
                      </div>
                    </div>
                  ) : (
                    <button
                      onClick={() => setSelectedId(r.id)}
                      className="text-sm text-emerald-400 hover:underline"
                    >
                      조치 입력
                    </button>
                  )}
                </>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
