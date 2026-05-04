import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useAuthStore } from "../stores/authStore";
import { apiFetch } from "../lib/api";
import { Newspaper, Shield, ExternalLink, ArrowRight } from "lucide-react";

interface NewsItem {
  title: string;
  link: string;
  pub_date: string;
  source: string;
  incident_type: string | null;
  summary: string | null;
  prevention_tips: string[] | null;
  related_law: string | null;
}

interface IncidentStats {
  total: number;
}

const TYPE_LABELS: Record<string, string> = {
  caught: "끼임", fall: "추락", collision: "충돌", electric: "감전",
  fire: "화재", suffocation: "질식", falling_object: "낙하물",
  chemical: "화학물질", other: "기타",
};

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user);
  const [news, setNews] = useState<NewsItem[]>([]);
  const [newsLoading, setNewsLoading] = useState(true);
  const [incidentTotal, setIncidentTotal] = useState(0);

  useEffect(() => {
    // 뉴스 (상위 5개)
    apiFetch("/api/news?limit=5").then(async (res) => {
      if (res.ok) setNews(await res.json());
      setNewsLoading(false);
    });
    // 사고 건수
    apiFetch("/api/incidents?size=1").then(async (res) => {
      if (res.ok) {
        const data = await res.json();
        setIncidentTotal(data.total);
      }
    });
  }, []);

  const formatDate = (dateStr: string) => {
    if (!dateStr) return "";
    try {
      return new Date(dateStr).toLocaleDateString("ko-KR", { month: "short", day: "numeric" });
    } catch { return ""; }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">대시보드</h1>
        <p className="text-slate-400 mt-1">{user?.name}님, 환영합니다.</p>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Link to="/incidents" className="bg-slate-800 rounded-xl p-6 border border-slate-700 hover:border-slate-500 transition-colors">
          <p className="text-slate-400 text-sm">등록된 사고</p>
          <p className="text-3xl font-bold text-white mt-2">{incidentTotal}</p>
          <p className="text-emerald-400 text-xs mt-1">사고 관리 바로가기 →</p>
        </Link>
        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
          <p className="text-slate-400 text-sm">미조치 항목</p>
          <p className="text-3xl font-bold text-white mt-2">-</p>
          <p className="text-slate-500 text-xs mt-1">Phase 3에서 구현</p>
        </div>
        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
          <p className="text-slate-400 text-sm">AI 분석 대기</p>
          <p className="text-3xl font-bold text-white mt-2">-</p>
          <p className="text-slate-500 text-xs mt-1">Phase 3에서 구현</p>
        </div>
      </div>

      {/* 안전 뉴스 */}
      <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Newspaper size={18} className="text-emerald-400" />
            <h2 className="text-lg font-semibold text-white">최신 산업안전 뉴스</h2>
          </div>
          <Link to="/news" className="flex items-center gap-1 text-sm text-emerald-400 hover:underline">
            전체 보기 <ArrowRight size={14} />
          </Link>
        </div>

        {newsLoading ? (
          <p className="text-slate-500 text-sm py-4">AI 분석 중...</p>
        ) : news.length === 0 ? (
          <p className="text-slate-500 text-sm">뉴스를 불러올 수 없습니다.</p>
        ) : (
          <div className="space-y-3">
            {news.map((item, idx) => (
              <div key={idx} className="bg-slate-900/50 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      {item.incident_type && (
                        <span className="px-2 py-0.5 bg-emerald-600/20 text-emerald-400 rounded text-xs">
                          {TYPE_LABELS[item.incident_type] || item.incident_type}
                        </span>
                      )}
                      <span className="text-xs text-slate-500">
                        {item.source && `${item.source} · `}{formatDate(item.pub_date)}
                      </span>
                    </div>
                    <a
                      href={item.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-white text-sm font-medium hover:text-emerald-400 transition-colors"
                    >
                      {item.title}
                    </a>
                    {item.summary && (
                      <p className="text-slate-400 text-xs mt-1">{item.summary}</p>
                    )}
                    {item.prevention_tips && item.prevention_tips.length > 0 && (
                      <div className="mt-2 flex items-start gap-1.5">
                        <Shield size={12} className="text-emerald-400 mt-0.5 shrink-0" />
                        <p className="text-xs text-slate-300">
                          {item.prevention_tips[0]}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
