import { useState, useEffect } from "react";
import { apiFetch } from "../lib/api";
import { Activity, RefreshCw, AlertTriangle } from "lucide-react";

interface Site { id: string; name: string; }

interface RiskItem {
  target_type: string;
  target_id: string;
  target_name: string;
  score: number;
  factors: { incident_count_90d?: number; unresolved_count?: number };
  calculated_at: string;
}

function scoreColor(score: number) {
  if (score >= 70) return "text-red-400";
  if (score >= 40) return "text-amber-400";
  return "text-emerald-400";
}

function scoreBg(score: number) {
  if (score >= 70) return "bg-red-600";
  if (score >= 40) return "bg-amber-500";
  return "bg-emerald-500";
}

export default function RiskScoresPage() {
  const [sites, setSites] = useState<Site[]>([]);
  const [siteId, setSiteId] = useState("");
  const [scores, setScores] = useState<RiskItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [calculating, setCalculating] = useState(false);

  useEffect(() => {
    apiFetch("/api/sites").then(async (res) => {
      if (res.ok) {
        const data = await res.json();
        setSites(data);
        if (data.length > 0) setSiteId(data[0].id);
      }
    });
  }, []);

  useEffect(() => {
    if (!siteId) return;
    setLoading(true);
    apiFetch(`/api/gamification/risk-scores?site_id=${siteId}`).then(async (res) => {
      if (res.ok) setScores(await res.json());
      setLoading(false);
    });
  }, [siteId]);

  const handleCalculate = async () => {
    if (!siteId) return;
    setCalculating(true);
    const res = await apiFetch(`/api/gamification/risk-scores/calculate?site_id=${siteId}`, { method: "POST" });
    if (res.ok) {
      // 재조회
      const r2 = await apiFetch(`/api/gamification/risk-scores?site_id=${siteId}`);
      if (r2.ok) setScores(await r2.json());
    }
    setCalculating(false);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Activity className="text-red-400" size={24} />
          <h1 className="text-2xl font-bold text-white">위험 예측</h1>
        </div>
        <button
          onClick={handleCalculate}
          disabled={calculating || !siteId}
          className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-sm border border-slate-700 disabled:opacity-50 transition-colors"
        >
          <RefreshCw size={14} className={calculating ? "animate-spin" : ""} />
          재계산
        </button>
      </div>

      {/* 사업장 선택 */}
      <select
        value={siteId}
        onChange={(e) => setSiteId(e.target.value)}
        className="px-3 py-2 bg-slate-800 text-white rounded-lg border border-slate-700 text-sm"
      >
        {sites.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
      </select>

      {loading ? (
        <p className="text-slate-400">로딩 중...</p>
      ) : scores.length === 0 ? (
        <div className="bg-slate-800 rounded-xl p-12 border border-slate-700 text-center">
          <Activity className="mx-auto text-slate-500 mb-3" size={40} />
          <p className="text-slate-400">위험도 데이터가 없습니다.</p>
          <p className="text-slate-500 text-sm mt-1">위의 "재계산" 버튼을 눌러 공정별 위험도를 산정하세요.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {scores.map((item) => (
            <div key={item.target_id} className="bg-slate-800 rounded-xl p-5 border border-slate-700">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  {item.score >= 70 && <AlertTriangle size={16} className="text-red-400" />}
                  <span className="text-white font-medium">{item.target_name}</span>
                  <span className="text-xs text-slate-500">{item.target_type === "process" ? "공정" : "구역"}</span>
                </div>
                <span className={`text-2xl font-bold ${scoreColor(item.score)}`}>{item.score}</span>
              </div>

              {/* 게이지 바 */}
              <div className="w-full h-2 bg-slate-700 rounded-full overflow-hidden mb-3">
                <div
                  className={`h-full rounded-full transition-all ${scoreBg(item.score)}`}
                  style={{ width: `${item.score}%` }}
                />
              </div>

              <div className="flex gap-4 text-xs text-slate-400">
                <span>90일 사고: {item.factors.incident_count_90d ?? 0}건</span>
                <span>미조치: {item.factors.unresolved_count ?? 0}건</span>
                <span className="ml-auto">
                  {new Date(item.calculated_at).toLocaleDateString("ko-KR")} 산정
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
