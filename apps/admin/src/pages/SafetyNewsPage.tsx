import { useState, useEffect } from "react";
import { apiFetch } from "../lib/api";
import { Newspaper, ExternalLink, Shield, AlertTriangle, RefreshCw } from "lucide-react";

interface NewsItem {
  title: string;
  link: string;
  pub_date: string;
  source: string;
  incident_type: string | null;
  severity_hint: string | null;
  summary: string | null;
  prevention_tips: string[] | null;
  related_law: string | null;
}

const TYPE_LABELS: Record<string, string> = {
  caught: "끼임", fall: "추락", collision: "충돌", electric: "감전",
  fire: "화재", suffocation: "질식", falling_object: "낙하물",
  chemical: "화학물질", other: "기타",
};

const SEVERITY_COLORS: Record<string, string> = {
  death: "bg-red-600", serious: "bg-orange-500", minor: "bg-yellow-500", near_miss: "bg-blue-500",
};

const SEVERITY_LABELS: Record<string, string> = {
  death: "사망", serious: "중상", minor: "경상", near_miss: "아차사고",
};

export default function SafetyNewsPage() {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<number | null>(null);

  const fetchNews = async () => {
    setLoading(true);
    const res = await apiFetch("/api/news?limit=20");
    if (res.ok) setNews(await res.json());
    setLoading(false);
  };

  useEffect(() => { fetchNews(); }, []);

  const formatDate = (dateStr: string) => {
    if (!dateStr) return "";
    try {
      return new Date(dateStr).toLocaleDateString("ko-KR", {
        month: "short", day: "numeric", hour: "2-digit", minute: "2-digit",
      });
    } catch {
      return dateStr;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Newspaper className="text-emerald-400" size={24} />
          <h1 className="text-2xl font-bold text-white">산업안전 뉴스</h1>
        </div>
        <button
          onClick={fetchNews}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-sm transition-colors disabled:opacity-50"
        >
          <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
          새로고침
        </button>
      </div>

      <p className="text-slate-400 text-sm">
        최신 산업재해/안전 뉴스를 AI가 분석하여 사고 유형, 유의점, 관련 법령을 제공합니다.
      </p>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="text-center">
            <RefreshCw className="mx-auto text-emerald-400 animate-spin mb-3" size={32} />
            <p className="text-slate-400">뉴스를 불러오고 AI 분석 중...</p>
          </div>
        </div>
      ) : news.length === 0 ? (
        <div className="bg-slate-800 rounded-xl p-12 border border-slate-700 text-center">
          <p className="text-slate-400">뉴스를 불러올 수 없습니다.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {news.map((item, idx) => (
            <div
              key={idx}
              className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden transition-colors hover:border-slate-600"
            >
              {/* 헤더 */}
              <button
                onClick={() => setExpandedId(expandedId === idx ? null : idx)}
                className="w-full p-4 text-left"
              >
                <div className="flex items-start gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                      {item.incident_type && (
                        <span className="px-2 py-0.5 bg-emerald-600/20 text-emerald-400 rounded text-xs">
                          {TYPE_LABELS[item.incident_type] || item.incident_type}
                        </span>
                      )}
                      {item.severity_hint && (
                        <span className={`px-2 py-0.5 rounded text-xs text-white ${SEVERITY_COLORS[item.severity_hint] || "bg-slate-500"}`}>
                          {SEVERITY_LABELS[item.severity_hint] || item.severity_hint}
                        </span>
                      )}
                      <span className="text-xs text-slate-500">
                        {item.source && `${item.source} · `}{formatDate(item.pub_date)}
                      </span>
                    </div>
                    <p className="text-white text-sm font-medium leading-snug">
                      {item.title}
                    </p>
                    {item.summary && (
                      <p className="text-slate-400 text-xs mt-1">{item.summary}</p>
                    )}
                  </div>
                </div>
              </button>

              {/* 확장 영역 — AI 분석 */}
              {expandedId === idx && (item.prevention_tips || item.related_law) && (
                <div className="px-4 pb-4 space-y-3 border-t border-slate-700 pt-3">
                  {item.prevention_tips && item.prevention_tips.length > 0 && (
                    <div>
                      <div className="flex items-center gap-1.5 mb-2">
                        <Shield size={14} className="text-emerald-400" />
                        <span className="text-xs font-medium text-emerald-400">예방 유의점</span>
                      </div>
                      <ul className="space-y-1">
                        {item.prevention_tips.map((tip, i) => (
                          <li key={i} className="text-sm text-slate-300 flex items-start gap-2">
                            <span className="text-emerald-500 mt-0.5">•</span>
                            {tip}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {item.related_law && (
                    <div className="flex items-center gap-1.5">
                      <AlertTriangle size={14} className="text-amber-400" />
                      <span className="text-xs text-amber-400">관련 법령:</span>
                      <span className="text-xs text-slate-300">{item.related_law}</span>
                    </div>
                  )}

                  <a
                    href={item.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-xs text-slate-400 hover:text-white transition-colors"
                  >
                    원문 보기 <ExternalLink size={12} />
                  </a>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
