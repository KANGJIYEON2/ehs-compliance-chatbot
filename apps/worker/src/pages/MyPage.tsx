import { useState, useEffect } from "react";
import { useAuthStore } from "../stores/authStore";
import { apiFetch } from "../lib/api";
import { Trophy, TrendingUp, LogOut } from "lucide-react";

const REASON_LABELS: Record<string,string> = {
  report:"위험 제보",tbm:"TBM 참석",quiz:"퀴즈 정답",
  qr_check:"안전수칙 확인",no_accident:"무사고",violation:"위반",
};

export default function MyPage() {
  const {user,logout} = useAuthStore();
  const [points, setPoints] = useState<{total:number;history:{points:number;reason:string;created_at:string}[]}|null>(null);
  const [ranking, setRanking] = useState<{rank:number}|null>(null);

  useEffect(() => {
    apiFetch("/api/gamification/my-points").then(async r=>{if(r.ok)setPoints(await r.json());});
    apiFetch("/api/gamification/ranking").then(async r=>{
      if(r.ok){
        const data = await r.json();
        const me = data.find((d:any)=>d.user_id===user?.id);
        if(me) setRanking({rank:me.rank});
      }
    });
  },[]);

  return (
    <div className="space-y-6">
      {/* 프로필 */}
      <div className="flex items-center gap-4">
        <div className="w-14 h-14 rounded-full bg-gradient-to-br from-emerald-500 to-emerald-700 flex items-center justify-center text-xl font-bold text-white">
          {user?.name?.[0]}
        </div>
        <div>
          <p className="text-white font-bold text-lg">{user?.name}</p>
          <p className="text-slate-500 text-sm">{user?.email}</p>
        </div>
      </div>

      {/* 포인트 + 랭킹 */}
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-gradient-to-br from-emerald-900/40 to-slate-900 rounded-2xl p-4 border border-emerald-800/30">
          <TrendingUp size={20} className="text-emerald-400 mb-2"/>
          <p className="text-3xl font-bold text-white">{points?.total||0}</p>
          <p className="text-slate-500 text-xs">안전 포인트</p>
        </div>
        <div className="bg-gradient-to-br from-amber-900/40 to-slate-900 rounded-2xl p-4 border border-amber-800/30">
          <Trophy size={20} className="text-amber-400 mb-2"/>
          <p className="text-3xl font-bold text-white">{ranking?`${ranking.rank}위`:"-"}</p>
          <p className="text-slate-500 text-xs">전체 랭킹</p>
        </div>
      </div>

      {/* 히스토리 */}
      <div>
        <p className="text-sm font-medium text-slate-400 mb-3">활동 내역</p>
        {!points||points.history.length===0?(
          <p className="text-slate-600 text-sm">활동 내역이 없습니다</p>
        ):(
          <div className="space-y-2">
            {points.history.map((h,i)=>(
              <div key={i} className="flex items-center justify-between bg-slate-900 rounded-xl px-4 py-3 border border-slate-800">
                <div>
                  <p className="text-white text-sm">{REASON_LABELS[h.reason]||h.reason}</p>
                  <p className="text-slate-600 text-[11px]">{new Date(h.created_at).toLocaleDateString("ko-KR")}</p>
                </div>
                <span className={`font-bold text-sm ${h.points>0?"text-emerald-400":"text-red-400"}`}>
                  {h.points>0?"+":""}{h.points}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      <button onClick={logout}
        className="w-full py-3 bg-slate-900 border border-slate-800 text-slate-400 rounded-2xl flex items-center justify-center gap-2 active:scale-95 transition-transform">
        <LogOut size={16}/> 로그아웃
      </button>
    </div>
  );
}
