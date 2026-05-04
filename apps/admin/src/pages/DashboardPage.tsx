import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useAuthStore } from "../stores/authStore";
import { apiFetch } from "../lib/api";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from "recharts";
import { Newspaper, Shield, ArrowRight, AlertTriangle, CheckCircle2, Clock, Eye } from "lucide-react";

interface NewsItem {
  title: string;
  link: string;
  pub_date: string;
  source: string;
  incident_type: string | null;
  summary: string | null;
  prevention_tips: string[] | null;
}

interface Summary {
  total: number;
  by_status: Record<string, number>;
  by_severity: Record<string, number>;
}

interface TypeCount { type: string; count: number; }

const TYPE_LABELS: Record<string, string> = {
  caught: "끼임", fall: "추락", collision: "충돌", electric: "감전",
  fire: "화재", suffocation: "질식", falling_object: "낙하물",
  chemical: "화학물질", other: "기타",
};

const PIE_COLORS = ["#ef4444", "#f97316", "#eab308", "#3b82f6"];
const BAR_COLOR = "#10b981";

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user);
  const [news, setNews] = useState<NewsItem[]>([]);
  const [newsLoading, setNewsLoading] = useState(true);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [byType, setByType] = useState<TypeCount[]>([]);

  useEffect(() => {
    apiFetch("/api/news?limit=5").then(async (res) => {
      if (res.ok) setNews(await res.json());
      setNewsLoading(false);
    });
    apiFetch("/api/analytics/summary").then(async (res) => {
      if (res.ok) setSummary(await res.json());
    });
    apiFetch("/api/analytics/by-type").then(async (res) => {
      if (res.ok) setByType(await res.json());
    });
  }, []);

  const formatDate = (d: string) => {
    try { return new Date(d).toLocaleDateString("ko-KR", { month: "short", day: "numeric" }); }
    catch { return ""; }
  };

  const severityData = summary ? [
    { name: "사망", value: summary.by_severity.death },
    { name: "중상", value: summary.by_severity.serious },
    { name: "경상", value: summary.by_severity.minor },
    { name: "아차사고", value: summary.by_severity.near_miss },
  ].filter(d => d.value > 0) : [];

  const typeChartData = byType.map(d => ({
    name: TYPE_LABELS[d.type] || d.type,
    count: d.count,
  }));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">대시보드</h1>
        <p className="text-slate-400 mt-1">{user?.name}님, 환영합니다.</p>
      </div>

      {/* 통계 카드 */}
      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Link to="/incidents" className="bg-slate-800 rounded-xl p-5 border border-slate-700 hover:border-slate-500 transition-colors">
            <div className="flex items-center gap-2 mb-2">
              <AlertTriangle size={16} className="text-slate-400" />
              <span className="text-slate-400 text-sm">전체 사고</span>
            </div>
            <p className="text-3xl font-bold text-white">{summary.total}</p>
          </Link>
          <Link to="/incidents?status=reported" className="bg-slate-800 rounded-xl p-5 border border-slate-700 hover:border-amber-500/50 transition-colors">
            <div className="flex items-center gap-2 mb-2">
              <Clock size={16} className="text-amber-400" />
              <span className="text-slate-400 text-sm">접수/조치중</span>
            </div>
            <p className="text-3xl font-bold text-amber-400">
              {summary.by_status.reported + summary.by_status.investigating}
            </p>
          </Link>
          <div className="bg-slate-800 rounded-xl p-5 border border-slate-700">
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle2 size={16} className="text-emerald-400" />
              <span className="text-slate-400 text-sm">조치완료</span>
            </div>
            <p className="text-3xl font-bold text-emerald-400">{summary.by_status.resolved}</p>
          </div>
          <div className="bg-slate-800 rounded-xl p-5 border border-slate-700">
            <div className="flex items-center gap-2 mb-2">
              <Eye size={16} className="text-purple-400" />
              <span className="text-slate-400 text-sm">재발관리</span>
            </div>
            <p className="text-3xl font-bold text-purple-400">{summary.by_status.monitoring}</p>
          </div>
        </div>
      )}

      {/* 차트 영역 */}
      {(typeChartData.length > 0 || severityData.length > 0) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* 유형별 바 차트 */}
          {typeChartData.length > 0 && (
            <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
              <h3 className="text-sm font-medium text-slate-300 mb-4">사고 유형별 현황</h3>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={typeChartData}>
                  <XAxis dataKey="name" tick={{ fill: "#94a3b8", fontSize: 12 }} />
                  <YAxis tick={{ fill: "#94a3b8", fontSize: 12 }} allowDecimals={false} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #334155", borderRadius: 8 }}
                    labelStyle={{ color: "#fff" }}
                  />
                  <Bar dataKey="count" fill={BAR_COLOR} radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* 심각도 파이 차트 */}
          {severityData.length > 0 && (
            <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
              <h3 className="text-sm font-medium text-slate-300 mb-4">심각도 분포</h3>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie data={severityData} cx="50%" cy="50%" innerRadius={50} outerRadius={80}
                    dataKey="value" nameKey="name" label={({ name, value }) => `${name}: ${value}`}>
                    {severityData.map((_, i) => (
                      <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Legend wrapperStyle={{ fontSize: 12, color: "#94a3b8" }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #334155", borderRadius: 8 }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}

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
                <a href={item.link} target="_blank" rel="noopener noreferrer"
                  className="text-white text-sm font-medium hover:text-emerald-400 transition-colors">
                  {item.title}
                </a>
                {item.summary && <p className="text-slate-400 text-xs mt-1">{item.summary}</p>}
                {item.prevention_tips && item.prevention_tips.length > 0 && (
                  <div className="mt-2 flex items-start gap-1.5">
                    <Shield size={12} className="text-emerald-400 mt-0.5 shrink-0" />
                    <p className="text-xs text-slate-300">{item.prevention_tips[0]}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
