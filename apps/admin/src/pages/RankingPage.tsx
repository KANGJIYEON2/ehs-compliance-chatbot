import { useState, useEffect } from "react";
import { apiFetch } from "../lib/api";
import { Trophy, Medal, TrendingUp } from "lucide-react";

interface RankItem {
  user_id: string;
  name: string;
  points: number;
  rank: number;
}

interface MyPoints {
  total: number;
  history: { points: number; reason: string; created_at: string }[];
}

const REASON_LABELS: Record<string, string> = {
  report: "위험 제보", tbm: "TBM 참석", quiz: "퀴즈 정답",
  qr_check: "안전수칙 확인", no_accident: "무사고 달성", violation: "안전 위반",
};

const RANK_STYLES = [
  "text-amber-400",   // 1등
  "text-slate-300",   // 2등
  "text-orange-400",  // 3등
];

export default function RankingPage() {
  const [ranking, setRanking] = useState<RankItem[]>([]);
  const [myPoints, setMyPoints] = useState<MyPoints | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      apiFetch("/api/gamification/ranking").then((r) => r.ok ? r.json() : []),
      apiFetch("/api/gamification/my-points").then((r) => r.ok ? r.json() : null),
    ]).then(([rank, points]) => {
      setRanking(rank);
      setMyPoints(points);
      setLoading(false);
    });
  }, []);

  if (loading) return <p className="text-slate-400 p-6">로딩 중...</p>;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Trophy className="text-amber-400" size={24} />
        <h1 className="text-2xl font-bold text-white">안전 랭킹</h1>
      </div>

      {/* 내 포인트 */}
      {myPoints && (
        <div className="bg-gradient-to-r from-emerald-900/40 to-slate-800 rounded-xl p-6 border border-emerald-600/30">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-400 text-sm">내 안전 포인트</p>
              <p className="text-4xl font-bold text-white mt-1">{myPoints.total}<span className="text-lg text-slate-400 ml-1">점</span></p>
            </div>
            <TrendingUp size={40} className="text-emerald-400 opacity-50" />
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* 랭킹 보드 */}
        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
          <h3 className="text-sm font-medium text-slate-300 mb-4">전체 랭킹</h3>
          {ranking.length === 0 ? (
            <p className="text-slate-500 text-sm">아직 포인트 기록이 없습니다.</p>
          ) : (
            <div className="space-y-2">
              {ranking.map((item) => (
                <div key={item.user_id} className="flex items-center gap-3 p-3 rounded-lg bg-slate-900/50">
                  <span className={`text-lg font-bold w-8 text-center ${RANK_STYLES[item.rank - 1] || "text-slate-400"}`}>
                    {item.rank <= 3 ? ["🥇", "🥈", "🥉"][item.rank - 1] : item.rank}
                  </span>
                  <span className="text-white text-sm flex-1">{item.name}</span>
                  <span className="text-emerald-400 font-medium text-sm">{item.points}점</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* 내 포인트 히스토리 */}
        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
          <h3 className="text-sm font-medium text-slate-300 mb-4">내 활동 내역</h3>
          {!myPoints || myPoints.history.length === 0 ? (
            <p className="text-slate-500 text-sm">활동 내역이 없습니다.</p>
          ) : (
            <div className="space-y-2">
              {myPoints.history.map((h, i) => (
                <div key={i} className="flex items-center justify-between p-2 rounded-lg">
                  <div>
                    <p className="text-white text-sm">{REASON_LABELS[h.reason] || h.reason}</p>
                    <p className="text-slate-500 text-xs">{new Date(h.created_at).toLocaleDateString("ko-KR")}</p>
                  </div>
                  <span className={`font-medium text-sm ${h.points > 0 ? "text-emerald-400" : "text-red-400"}`}>
                    {h.points > 0 ? "+" : ""}{h.points}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
