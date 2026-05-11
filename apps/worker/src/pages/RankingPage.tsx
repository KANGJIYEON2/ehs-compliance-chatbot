import { useState, useEffect } from "react";
import { apiFetch } from "../lib/api";
import { useAuthStore } from "../stores/authStore";
import { Trophy, Loader2 } from "lucide-react";

const MEDAL = ["text-amber-400", "text-slate-300", "text-orange-400"];

export default function RankingPage() {
  const user = useAuthStore((s) => s.user);
  const [ranking, setRanking] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch("/api/gamification/ranking").then(async (r) => {
      if (r.ok) setRanking(await r.json());
      setLoading(false);
    });
  }, []);

  if (loading)
    return (
      <div className="flex items-center justify-center py-16">
        <Loader2 size={24} className="animate-spin text-slate-400" />
      </div>
    );

  const myRank = ranking.find((r: any) => r.user_id === user?.id);

  return (
    <div className="space-y-5">
      <h1 className="text-xl font-bold text-white">안전 랭킹</h1>

      {/* 내 순위 배너 */}
      {myRank && (
        <div className="bg-gradient-to-br from-purple-900/40 to-slate-900 rounded-2xl p-4 border border-purple-800/30 flex items-center gap-4">
          <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-500 to-purple-700 flex items-center justify-center text-lg font-bold text-white">
            {myRank.rank}
          </div>
          <div className="flex-1">
            <p className="text-white font-medium">{user?.name}</p>
            <p className="text-slate-500 text-xs">내 순위</p>
          </div>
          <p className="text-2xl font-bold text-purple-400">{myRank.points}점</p>
        </div>
      )}

      {/* 전체 랭킹 */}
      {ranking.length === 0 ? (
        <div className="text-center py-12">
          <Trophy size={40} className="text-slate-600 mx-auto mb-3" />
          <p className="text-slate-400">아직 랭킹 데이터가 없습니다</p>
        </div>
      ) : (
        <div className="space-y-2">
          {ranking.map((item: any) => {
            const isMe = item.user_id === user?.id;
            return (
              <div
                key={item.user_id}
                className={`flex items-center gap-3 rounded-2xl px-4 py-3 border transition-all ${
                  isMe
                    ? "bg-emerald-900/20 border-emerald-700/30"
                    : "bg-slate-900 border-slate-800"
                }`}
              >
                <span
                  className={`w-8 text-center font-bold text-lg ${
                    item.rank <= 3 ? MEDAL[item.rank - 1] : "text-slate-500"
                  }`}
                >
                  {item.rank <= 3
                    ? ["🥇", "🥈", "🥉"][item.rank - 1]
                    : item.rank}
                </span>
                <div className="flex-1 min-w-0">
                  <p className={`text-sm font-medium truncate ${isMe ? "text-emerald-300" : "text-white"}`}>
                    {item.name}
                    {isMe && <span className="text-emerald-500 text-xs ml-1">(나)</span>}
                  </p>
                </div>
                <span className="text-sm font-bold text-slate-300">
                  {item.points}점
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
