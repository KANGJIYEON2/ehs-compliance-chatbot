import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { apiFetch } from "../lib/api";
import { ArrowLeft, Trash2 } from "lucide-react";

interface Attachment {
  id: string;
  file_name: string;
  file_type: string | null;
  file_size: number | null;
}

interface Incident {
  id: string;
  site_id: string;
  reporter_id: string;
  incident_type: string;
  severity: string;
  occurred_at: string;
  description: string;
  cause_estimate: string | null;
  action_taken: string | null;
  status: string;
  created_at: string;
  updated_at: string;
  attachments: Attachment[];
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
const STATUS_FLOW = ["reported", "investigating", "resolved", "monitoring"];

export default function IncidentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [incident, setIncident] = useState<Incident | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchIncident = async () => {
    const res = await apiFetch(`/api/incidents/${id}`);
    if (res.ok) setIncident(await res.json());
    else navigate("/incidents");
    setLoading(false);
  };

  useEffect(() => { fetchIncident(); }, [id]);

  const changeStatus = async (newStatus: string) => {
    const res = await apiFetch(`/api/incidents/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ status: newStatus }),
    });
    if (res.ok) setIncident(await res.json());
  };

  const handleDelete = async () => {
    if (!confirm("정말 삭제하시겠습니까? 복구할 수 없습니다.")) return;
    const res = await apiFetch(`/api/incidents/${id}`, { method: "DELETE" });
    if (res.ok) navigate("/incidents");
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    const res = await apiFetch(`/api/incidents/${id}/files`, {
      method: "POST",
      body: formData,
      headers: {},  // let browser set content-type for FormData
    });
    if (res.ok) fetchIncident();
    e.target.value = "";
  };

  const handleFileDelete = async (fileId: string) => {
    const res = await apiFetch(`/api/incidents/${id}/files/${fileId}`, { method: "DELETE" });
    if (res.ok) fetchIncident();
  };

  if (loading) return <p className="text-slate-400">로딩 중...</p>;
  if (!incident) return null;

  const currentIdx = STATUS_FLOW.indexOf(incident.status);

  return (
    <div className="max-w-3xl space-y-6">
      {/* 헤더 */}
      <div className="flex items-center gap-3">
        <button onClick={() => navigate("/incidents")} className="text-slate-400 hover:text-white">
          <ArrowLeft size={20} />
        </button>
        <h1 className="text-2xl font-bold text-white">사고 상세</h1>
        <button
          onClick={handleDelete}
          className="ml-auto p-2 text-slate-400 hover:text-red-400 transition-colors"
          title="삭제"
        >
          <Trash2 size={18} />
        </button>
      </div>

      {/* 상태 진행바 */}
      <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm text-slate-300">상태</span>
        </div>
        <div className="flex gap-2">
          {STATUS_FLOW.map((s, i) => (
            <button
              key={s}
              onClick={() => changeStatus(s)}
              className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
                i <= currentIdx
                  ? "bg-emerald-600 text-white"
                  : "bg-slate-700 text-slate-400 hover:bg-slate-600"
              }`}
            >
              {STATUS_LABELS[s]}
            </button>
          ))}
        </div>
      </div>

      {/* 사고 정보 */}
      <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <Field label="사고 유형" value={TYPE_LABELS[incident.incident_type] || incident.incident_type} />
          <Field label="심각도" value={SEVERITY_LABELS[incident.severity] || incident.severity} />
          <Field label="발생 일시" value={new Date(incident.occurred_at).toLocaleString("ko-KR")} />
          <Field label="등록일" value={new Date(incident.created_at).toLocaleString("ko-KR")} />
        </div>

        <div>
          <span className="text-xs text-slate-400">사고 설명</span>
          <p className="text-white text-sm mt-1 whitespace-pre-wrap">{incident.description}</p>
        </div>

        {incident.cause_estimate && (
          <div>
            <span className="text-xs text-slate-400">원인 추정</span>
            <p className="text-white text-sm mt-1 whitespace-pre-wrap">{incident.cause_estimate}</p>
          </div>
        )}

        {incident.action_taken && (
          <div>
            <span className="text-xs text-slate-400">조치 내용</span>
            <p className="text-white text-sm mt-1 whitespace-pre-wrap">{incident.action_taken}</p>
          </div>
        )}
      </div>

      {/* 첨부파일 */}
      <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
        <div className="flex items-center justify-between mb-4">
          <span className="text-sm text-slate-300">첨부파일 ({incident.attachments.length})</span>
          <label className="px-3 py-1 bg-slate-700 hover:bg-slate-600 text-white rounded-lg text-sm cursor-pointer transition-colors">
            파일 추가
            <input type="file" className="hidden" accept="image/*,.pdf" onChange={handleFileUpload} />
          </label>
        </div>
        {incident.attachments.length === 0 ? (
          <p className="text-slate-500 text-sm">첨부된 파일이 없습니다.</p>
        ) : (
          <div className="space-y-2">
            {incident.attachments.map((att) => (
              <div key={att.id} className="flex items-center justify-between bg-slate-700 rounded-lg px-3 py-2">
                <span className="text-sm text-white truncate">{att.file_name}</span>
                <div className="flex items-center gap-2">
                  {att.file_size && (
                    <span className="text-xs text-slate-400">{(att.file_size / 1024).toFixed(0)}KB</span>
                  )}
                  <button onClick={() => handleFileDelete(att.id)} className="text-slate-400 hover:text-red-400">
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <span className="text-xs text-slate-400">{label}</span>
      <p className="text-white text-sm mt-0.5">{value}</p>
    </div>
  );
}
