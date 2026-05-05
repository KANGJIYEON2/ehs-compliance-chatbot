import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { apiFetch } from "../lib/api";
import { Plus, AlertTriangle, ChevronLeft, ChevronRight } from "lucide-react";

interface Incident {
  id: string;
  incident_type: string;
  severity: string;
  status: string;
  description: string;
  occurred_at: string;
  site_id: string;
}

const TYPE_LABELS: Record<string, string> = {
  caught: "끼임", fall: "추락", collision: "충돌", electric: "감전",
  fire: "화재", suffocation: "질식", falling_object: "낙하물",
  chemical: "화학물질", other: "기타",
};

const SEVERITY_LABELS: Record<string, string> = {
  death: "사망", serious: "중상", minor: "경상", near_miss: "아차사고",
};

const STATUS_LABELS: Record<string, string> = {
  reported: "접수", investigating: "조치중", resolved: "조치완료", monitoring: "재발관리",
};

const SEVERITY_COLORS: Record<string, string> = {
  death: "bg-red-600", serious: "bg-orange-500", minor: "bg-yellow-500", near_miss: "bg-blue-500",
};

const STATUS_COLORS: Record<string, string> = {
  reported: "bg-slate-500", investigating: "bg-amber-500", resolved: "bg-emerald-500", monitoring: "bg-purple-500",
};

export default function IncidentListPage() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState("");
  const [filterStatus, setFilterStatus] = useState("");
  const size = 20;

  const fetchIncidents = async () => {
    setLoading(true);
    const params = new URLSearchParams({ page: String(page), size: String(size) });
    if (filterType) params.set("incident_type", filterType);
    if (filterStatus) params.set("status", filterStatus);

    const res = await apiFetch(`/api/incidents?${params}`);
    if (res.ok) {
      const data = await res.json();
      setIncidents(data.items);
      setTotal(data.total);
    }
    setLoading(false);
  };

  useEffect(() => { fetchIncidents(); }, [page, filterType, filterStatus]);

  const totalPages = Math.ceil(total / size);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">사고/아차사고 관리</h1>
        <Link
          to="/dashboard/incidents/new"
          className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm transition-colors"
        >
          <Plus size={16} />
          사고 등록
        </Link>
      </div>

      {/* 필터 */}
      <div className="flex gap-3">
        <select
          value={filterType}
          onChange={(e) => { setFilterType(e.target.value); setPage(1); }}
          className="px-3 py-2 bg-slate-800 text-white rounded-lg border border-slate-700 text-sm"
        >
          <option value="">전체 유형</option>
          {Object.entries(TYPE_LABELS).map(([k, v]) => (
            <option key={k} value={k}>{v}</option>
          ))}
        </select>
        <select
          value={filterStatus}
          onChange={(e) => { setFilterStatus(e.target.value); setPage(1); }}
          className="px-3 py-2 bg-slate-800 text-white rounded-lg border border-slate-700 text-sm"
        >
          <option value="">전체 상태</option>
          {Object.entries(STATUS_LABELS).map(([k, v]) => (
            <option key={k} value={k}>{v}</option>
          ))}
        </select>
        <span className="text-slate-400 text-sm self-center ml-auto">
          총 {total}건
        </span>
      </div>

      {/* 목록 */}
      {loading ? (
        <p className="text-slate-400">로딩 중...</p>
      ) : incidents.length === 0 ? (
        <div className="bg-slate-800 rounded-xl p-12 border border-slate-700 text-center">
          <AlertTriangle className="mx-auto text-slate-500 mb-3" size={40} />
          <p className="text-slate-400">등록된 사고가 없습니다.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {incidents.map((inc) => (
            <Link
              key={inc.id}
              to={`/dashboard/incidents/${inc.id}`}
              className="block bg-slate-800 rounded-xl p-4 border border-slate-700 hover:border-slate-500 transition-colors"
            >
              <div className="flex items-center gap-3">
                <span className={`px-2 py-0.5 rounded text-xs text-white ${SEVERITY_COLORS[inc.severity] || "bg-slate-500"}`}>
                  {SEVERITY_LABELS[inc.severity] || inc.severity}
                </span>
                <span className={`px-2 py-0.5 rounded text-xs text-white ${STATUS_COLORS[inc.status] || "bg-slate-500"}`}>
                  {STATUS_LABELS[inc.status] || inc.status}
                </span>
                <span className="text-sm text-emerald-400">
                  {TYPE_LABELS[inc.incident_type] || inc.incident_type}
                </span>
                <span className="text-xs text-slate-500 ml-auto">
                  {new Date(inc.occurred_at).toLocaleDateString("ko-KR")}
                </span>
              </div>
              <p className="text-white text-sm mt-2 line-clamp-1">
                {inc.description}
              </p>
            </Link>
          ))}
        </div>
      )}

      {/* 페이징 */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-4">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="p-2 text-slate-400 hover:text-white disabled:opacity-30"
          >
            <ChevronLeft size={20} />
          </button>
          <span className="text-sm text-slate-400">
            {page} / {totalPages}
          </span>
          <button
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="p-2 text-slate-400 hover:text-white disabled:opacity-30"
          >
            <ChevronRight size={20} />
          </button>
        </div>
      )}
    </div>
  );
}
