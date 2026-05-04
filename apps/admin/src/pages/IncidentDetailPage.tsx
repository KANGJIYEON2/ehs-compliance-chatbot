import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { apiFetch } from "../lib/api";
import { ArrowLeft, Trash2, Brain, Shield, Scale, Loader2, CheckCircle2, Circle, AlertTriangle } from "lucide-react";

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

interface AIAnalysis {
  root_cause_analysis?: string;
  contributing_factors?: string[];
  prevention_checklist?: { item: string; priority: string; category: string }[];
  recurrence_prevention?: string;
  related_regulations?: string[];
  risk_level?: string;
  immediate_actions?: string[];
  error?: string;
}

interface LegalBasis {
  primary_laws?: { law: string; article: string; summary: string; relevance: string }[];
  employer_obligations?: string[];
  penalties?: string;
  compliance_checklist?: string[];
  error?: string;
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
const PRIORITY_COLORS: Record<string, string> = {
  high: "text-red-400", medium: "text-amber-400", low: "text-slate-400",
};
const RISK_COLORS: Record<string, string> = {
  high: "bg-red-600", medium: "bg-amber-500", low: "bg-emerald-500",
};

export default function IncidentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [incident, setIncident] = useState<Incident | null>(null);
  const [loading, setLoading] = useState(true);

  // AI 분석 상태
  const [analysis, setAnalysis] = useState<AIAnalysis | null>(null);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [legalBasis, setLegalBasis] = useState<LegalBasis | null>(null);
  const [legalLoading, setLegalLoading] = useState(false);
  const [checklist, setChecklist] = useState<{ item: string; priority: string; category: string }[]>([]);
  const [checklistLoading, setChecklistLoading] = useState(false);
  const [checkedItems, setCheckedItems] = useState<Set<number>>(new Set());

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
    if (!confirm("정말 삭제하시겠습니까?")) return;
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
      headers: {},
    });
    if (res.ok) fetchIncident();
    e.target.value = "";
  };

  const handleFileDelete = async (fileId: string) => {
    const res = await apiFetch(`/api/incidents/${id}/files/${fileId}`, { method: "DELETE" });
    if (res.ok) fetchIncident();
  };

  // AI 분석 실행
  const runAnalysis = async () => {
    setAnalysisLoading(true);
    const res = await apiFetch(`/api/ai/incidents/${id}/analyze`, { method: "POST" });
    if (res.ok) {
      const data = await res.json();
      setAnalysis(data.analysis);
    }
    setAnalysisLoading(false);
  };

  const runChecklist = async () => {
    setChecklistLoading(true);
    const res = await apiFetch(`/api/ai/incidents/${id}/checklist`, { method: "POST" });
    if (res.ok) {
      const data = await res.json();
      setChecklist(data.checklist || []);
    }
    setChecklistLoading(false);
  };

  const runLegalBasis = async () => {
    if (!incident) return;
    setLegalLoading(true);
    const res = await apiFetch("/api/ai/legal-basis", {
      method: "POST",
      body: JSON.stringify({
        incident_type: incident.incident_type,
        description: incident.description,
      }),
    });
    if (res.ok) setLegalBasis(await res.json());
    setLegalLoading(false);
  };

  const toggleCheck = (idx: number) => {
    setCheckedItems((prev) => {
      const next = new Set(prev);
      next.has(idx) ? next.delete(idx) : next.add(idx);
      return next;
    });
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
        <button onClick={handleDelete} className="ml-auto p-2 text-slate-400 hover:text-red-400 transition-colors" title="삭제">
          <Trash2 size={18} />
        </button>
      </div>

      {/* 상태 진행바 */}
      <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
        <span className="text-sm text-slate-300 mb-3 block">상태</span>
        <div className="flex gap-2">
          {STATUS_FLOW.map((s, i) => (
            <button key={s} onClick={() => changeStatus(s)}
              className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
                i <= currentIdx ? "bg-emerald-600 text-white" : "bg-slate-700 text-slate-400 hover:bg-slate-600"
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

      {/* AI 분석 버튼 그룹 */}
      <div className="flex gap-3">
        <button onClick={runAnalysis} disabled={analysisLoading}
          className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm disabled:opacity-50 transition-colors">
          {analysisLoading ? <Loader2 size={16} className="animate-spin" /> : <Brain size={16} />}
          AI 원인 분석
        </button>
        <button onClick={runChecklist} disabled={checklistLoading}
          className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm disabled:opacity-50 transition-colors">
          {checklistLoading ? <Loader2 size={16} className="animate-spin" /> : <Shield size={16} />}
          예방 체크리스트
        </button>
        <button onClick={runLegalBasis} disabled={legalLoading}
          className="flex items-center gap-2 px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-sm disabled:opacity-50 transition-colors">
          {legalLoading ? <Loader2 size={16} className="animate-spin" /> : <Scale size={16} />}
          법령 근거
        </button>
      </div>

      {/* AI 원인 분석 결과 */}
      {analysis && !analysis.error && (
        <div className="bg-slate-800 rounded-xl p-6 border border-purple-600/30 space-y-4">
          <div className="flex items-center gap-2">
            <Brain size={18} className="text-purple-400" />
            <h3 className="text-lg font-semibold text-white">AI 원인 분석</h3>
            {analysis.risk_level && (
              <span className={`ml-auto px-2 py-0.5 rounded text-xs text-white ${RISK_COLORS[analysis.risk_level] || "bg-slate-500"}`}>
                위험도: {analysis.risk_level.toUpperCase()}
              </span>
            )}
          </div>

          {analysis.root_cause_analysis && (
            <div>
              <span className="text-xs text-purple-300">근본 원인</span>
              <p className="text-white text-sm mt-1">{analysis.root_cause_analysis}</p>
            </div>
          )}

          {analysis.contributing_factors && analysis.contributing_factors.length > 0 && (
            <div>
              <span className="text-xs text-purple-300">기여 요인</span>
              <ul className="mt-1 space-y-1">
                {analysis.contributing_factors.map((f, i) => (
                  <li key={i} className="text-sm text-slate-300 flex items-start gap-2">
                    <span className="text-purple-400 mt-0.5">•</span>{f}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {analysis.immediate_actions && analysis.immediate_actions.length > 0 && (
            <div>
              <span className="text-xs text-red-300">즉시 조치 사항</span>
              <ul className="mt-1 space-y-1">
                {analysis.immediate_actions.map((a, i) => (
                  <li key={i} className="text-sm text-slate-300 flex items-start gap-2">
                    <AlertTriangle size={14} className="text-red-400 mt-0.5 shrink-0" />{a}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {analysis.recurrence_prevention && (
            <div>
              <span className="text-xs text-purple-300">재발 방지 대책</span>
              <p className="text-white text-sm mt-1">{analysis.recurrence_prevention}</p>
            </div>
          )}
        </div>
      )}

      {/* 예방 체크리스트 */}
      {checklist.length > 0 && (
        <div className="bg-slate-800 rounded-xl p-6 border border-emerald-600/30 space-y-3">
          <div className="flex items-center gap-2 mb-2">
            <Shield size={18} className="text-emerald-400" />
            <h3 className="text-lg font-semibold text-white">예방 체크리스트</h3>
            <span className="ml-auto text-xs text-slate-400">
              {checkedItems.size}/{checklist.length} 완료
            </span>
          </div>
          {checklist.map((item, idx) => (
            <button key={idx} onClick={() => toggleCheck(idx)}
              className="w-full flex items-start gap-3 p-3 rounded-lg bg-slate-900/50 hover:bg-slate-700/50 text-left transition-colors">
              {checkedItems.has(idx)
                ? <CheckCircle2 size={18} className="text-emerald-400 mt-0.5 shrink-0" />
                : <Circle size={18} className="text-slate-500 mt-0.5 shrink-0" />}
              <div className="flex-1">
                <p className={`text-sm ${checkedItems.has(idx) ? "text-slate-500 line-through" : "text-white"}`}>
                  {item.item}
                </p>
                <div className="flex gap-2 mt-1">
                  <span className={`text-xs ${PRIORITY_COLORS[item.priority] || "text-slate-400"}`}>
                    {item.priority === "high" ? "높음" : item.priority === "medium" ? "보통" : "낮음"}
                  </span>
                  <span className="text-xs text-slate-500">{item.category}</span>
                </div>
              </div>
            </button>
          ))}
        </div>
      )}

      {/* 법령 근거 */}
      {legalBasis && !legalBasis.error && (
        <div className="bg-slate-800 rounded-xl p-6 border border-amber-600/30 space-y-4">
          <div className="flex items-center gap-2">
            <Scale size={18} className="text-amber-400" />
            <h3 className="text-lg font-semibold text-white">관련 법령 근거</h3>
          </div>

          {legalBasis.primary_laws && legalBasis.primary_laws.map((law, i) => (
            <div key={i} className="bg-slate-900/50 rounded-lg p-4 space-y-1">
              <p className="text-amber-300 text-sm font-medium">{law.law} {law.article}</p>
              <p className="text-white text-sm">{law.summary}</p>
              <p className="text-slate-400 text-xs">{law.relevance}</p>
            </div>
          ))}

          {legalBasis.employer_obligations && legalBasis.employer_obligations.length > 0 && (
            <div>
              <span className="text-xs text-amber-300">사업주 의무</span>
              <ul className="mt-1 space-y-1">
                {legalBasis.employer_obligations.map((o, i) => (
                  <li key={i} className="text-sm text-slate-300 flex items-start gap-2">
                    <span className="text-amber-400 mt-0.5">•</span>{o}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {legalBasis.penalties && (
            <div>
              <span className="text-xs text-red-300">위반 시 처벌</span>
              <p className="text-white text-sm mt-1">{legalBasis.penalties}</p>
            </div>
          )}
        </div>
      )}

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
                  {att.file_size && <span className="text-xs text-slate-400">{(att.file_size / 1024).toFixed(0)}KB</span>}
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
