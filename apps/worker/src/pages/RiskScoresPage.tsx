import { useState, useEffect } from "react";
import { apiFetch } from "../lib/api";
import { useAuthStore } from "../stores/authStore";
import { Activity, Loader2, ShieldAlert } from "lucide-react";

function scoreColor(score: number) {
  if (score >= 70) return { bg: "bg-red-900/30", border: "border-red-700/40", text: "text-red-400", bar: "bg-red-500" };
  if (score >= 40) return { bg: "bg-amber-900/30", border: "border-amber-700/40", text: "text-amber-400", bar: "bg-amber-500" };
  return { bg: "bg-emerald-900/30", border: "border-emerald-700/40", text: "text-emerald-400", bar: "bg-emerald-500" };
}

function riskLabel(score: number) {
  if (score >= 70) return "위험";
  if (score >= 40) return "주의";
  return "안전";
}

export default function RiskScoresPage() {
  const user = useAuthStore((s) => s.user);
  const [scores, setScores] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user?.site_id) { setLoading(false); return; }
    apiFetch(`/api/gamification/risk-scores?site_id=${user.site_id}`).then(async (r) => {
      if (r.ok) setScores(await r.json());
      setLoading(false);
    });
  }, [user?.site_id]);

  if (loading)
    return (
      <div className="flex items-center justify-center py-16">
        <Loader2 size={24} className="animate-spin text-slate-400" />
      </div>
    );

  return (
    <div className="space-y-5">
      <h1 className="text-xl font-bold text-white">위험 예측</h1>

      {scores.length === 0 ? (
        <div className="text-center py-12">
          <Activity size={40} className="text-slate-600 mx-auto mb-3" />
          <p className="text-slate-400">위험도 데이터가 없습니다</p>
          <p className="text-slate-600 text-xs mt-1">관리자가 위험도를 계산하면 여기에 표시됩니다</p>
        </div>
      ) : (
        <div className="space-y-3">
          {scores.map((item: any) => {
            const c = scoreColor(item.score);
            return (
              <div
                key={item.id || item.target_id}
                className={`${c.bg} rounded-2xl p-4 border ${c.border}`}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <ShieldAlert size={18} className={c.text} />
                    <div>
                      <p className="text-white font-medium text-sm">{item.target_name}</p>
                      <p className="text-slate-500 text-[11px]">
                        {item.target_type === "process" ? "공정" : "작업구역"}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className={`text-2xl font-bold ${c.text}`}>{item.score}</p>
                    <p className={`text-xs font-medium ${c.text}`}>{riskLabel(item.score)}</p>
                  </div>
                </div>

                {/* 위험도 바 */}
                <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${c.bar} rounded-full transition-all`}
                    style={{ width: `${item.score}%` }}
                  />
                </div>

                {/* 요인 상세 */}
                {item.factors && (
                  <div className="mt-3 flex gap-4 text-xs text-slate-400">
                    {item.factors.incident_count_90d != null && (
                      <span>최근 사고 <strong className="text-slate-300">{item.factors.incident_count_90d}건</strong></span>
                    )}
                    {item.factors.unresolved_count != null && (
                      <span>미조치 <strong className="text-slate-300">{item.factors.unresolved_count}건</strong></span>
                    )}
                  </div>
                )}

                {item.calculated_at && (
                  <p className="text-slate-600 text-[10px] mt-2">
                    {new Date(item.calculated_at).toLocaleDateString("ko-KR")} 기준
                  </p>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
