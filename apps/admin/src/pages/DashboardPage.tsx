import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useAuthStore } from "../stores/authStore";
import { apiFetch } from "../lib/api";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell,
} from "recharts";
import {
  Newspaper, Shield, ArrowRight, AlertTriangle, CheckCircle2,
  Clock, Eye, FileDown, TrendingUp, TrendingDown, Minus,
} from "lucide-react";

interface NewsItem {
  title: string; link: string; pub_date: string; source: string;
  incident_type: string | null; summary: string | null;
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
const BAR_COLORS = ["#10b981", "#06b6d4", "#8b5cf6", "#f59e0b", "#ef4444"];

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user);
  const [news, setNews] = useState<NewsItem[]>([]);
  const [newsLoading, setNewsLoading] = useState(true);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [byType, setByType] = useState<TypeCount[]>([]);
  const [pdfLoading, setPdfLoading] = useState(false);

  useEffect(() => {
    apiFetch("/api/news?limit=4").then(async (r) => { if (r.ok) setNews(await r.json()); setNewsLoading(false); });
    apiFetch("/api/analytics/summary").then(async (r) => { if (r.ok) setSummary(await r.json()); });
    apiFetch("/api/analytics/by-type").then(async (r) => { if (r.ok) setByType(await r.json()); });
  }, []);

  const downloadPdf = async () => {
    setPdfLoading(true);
    const res = await apiFetch("/api/reports/monthly");
    if (res.ok) {
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `safety_report_${new Date().getFullYear()}_${String(new Date().getMonth() + 1).padStart(2, "0")}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    }
    setPdfLoading(false);
  };

  const formatDate = (d: string) => {
    try { return new Date(d).toLocaleDateString("ko-KR", { month: "short", day: "numeric" }); }
    catch { return ""; }
  };

  const sevData = summary ? [
    { name: "사망", value: summary.by_severity.death },
    { name: "중상", value: summary.by_severity.serious },
    { name: "경상", value: summary.by_severity.minor },
    { name: "아차", value: summary.by_severity.near_miss },
  ].filter(d => d.value > 0) : [];

  const typeData = byType.map(d => ({ name: TYPE_LABELS[d.type] || d.type, count: d.count }));

  const pending = summary ? summary.by_status.reported + summary.by_status.investigating : 0;

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">대시보드</h1>
          <p className="text-slate-500 text-sm mt-0.5">
            {new Date().toLocaleDateString("ko-KR", { year: "numeric", month: "long", day: "numeric" })} 기준
          </p>
        </div>
        <button onClick={downloadPdf} disabled={pdfLoading}
          className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-xl text-sm border border-slate-700/50 transition-all disabled:opacity-50 shadow-sm">
          <FileDown size={15} />
          {pdfLoading ? "생성 중..." : "월간 리포트"}
        </button>
      </div>

      {/* KPI 카드 */}
      {summary && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            label="전체 사고" value={summary.total} icon={AlertTriangle}
            color="slate" link="/incidents"
          />
          <StatCard
            label="미조치" value={pending} icon={Clock}
            color={pending > 0 ? "amber" : "slate"} link="/incidents"
            badge={pending > 0 ? "주의" : undefined}
          />
          <StatCard
            label="조치완료" value={summary.by_status.resolved} icon={CheckCircle2}
            color="emerald"
          />
          <StatCard
            label="재발관리" value={summary.by_status.monitoring} icon={Eye}
            color="purple"
          />
        </div>
      )}

      {/* 차트 */}
      {(typeData.length > 0 || sevData.length > 0) && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {typeData.length > 0 && (
            <div className="bg-slate-900 rounded-2xl p-5 border border-slate-800">
              <h3 className="text-sm font-semibold text-white mb-4">사고 유형별</h3>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={typeData} barCategoryGap="20%">
                  <XAxis dataKey="name" tick={{ fill: "#64748b", fontSize: 11 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: "#64748b", fontSize: 11 }} axisLine={false} tickLine={false} allowDecimals={false} />
                  <Tooltip contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #334155", borderRadius: 12, fontSize: 13 }} cursor={{ fill: "rgba(255,255,255,0.03)" }} />
                  <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                    {typeData.map((_, i) => <Cell key={i} fill={BAR_COLORS[i % BAR_COLORS.length]} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {sevData.length > 0 && (
            <div className="bg-slate-900 rounded-2xl p-5 border border-slate-800">
              <h3 className="text-sm font-semibold text-white mb-4">심각도 분포</h3>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie data={sevData} cx="50%" cy="50%" innerRadius={55} outerRadius={80}
                    dataKey="value" nameKey="name" strokeWidth={0}>
                    {sevData.map((_, i) => <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}
                  </Pie>
                  <Tooltip contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #334155", borderRadius: 12, fontSize: 13 }} />
                </PieChart>
              </ResponsiveContainer>
              <div className="flex justify-center gap-4 mt-2">
                {sevData.map((d, i) => (
                  <div key={i} className="flex items-center gap-1.5">
                    <div className="w-2.5 h-2.5 rounded-full" style={{ background: PIE_COLORS[i] }} />
                    <span className="text-[11px] text-slate-400">{d.name} {d.value}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* 뉴스 */}
      <div className="bg-slate-900 rounded-2xl border border-slate-800">
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <Newspaper size={16} className="text-emerald-400" />
            <h2 className="text-sm font-semibold text-white">산업안전 뉴스</h2>
          </div>
          <Link to="/news" className="flex items-center gap-1 text-xs text-slate-400 hover:text-emerald-400 transition-colors">
            전체 보기 <ArrowRight size={12} />
          </Link>
        </div>
        <div className="divide-y divide-slate-800/50">
          {newsLoading ? (
            <p className="text-slate-500 text-sm p-5">AI 분석 중...</p>
          ) : news.length === 0 ? (
            <p className="text-slate-500 text-sm p-5">뉴스를 불러올 수 없습니다.</p>
          ) : (
            news.map((item, idx) => (
              <div key={idx} className="px-5 py-3.5 hover:bg-slate-800/30 transition-colors">
                <div className="flex items-center gap-2 mb-1">
                  {item.incident_type && (
                    <span className="px-1.5 py-0.5 bg-emerald-500/10 text-emerald-400 rounded text-[10px] font-medium">
                      {TYPE_LABELS[item.incident_type] || item.incident_type}
                    </span>
                  )}
                  <span className="text-[10px] text-slate-600">{item.source} {formatDate(item.pub_date)}</span>
                </div>
                <a href={item.link} target="_blank" rel="noopener noreferrer"
                  className="text-[13px] text-slate-200 hover:text-emerald-400 transition-colors leading-snug line-clamp-1">
                  {item.title}
                </a>
                {item.prevention_tips?.[0] && (
                  <div className="flex items-start gap-1.5 mt-1.5">
                    <Shield size={11} className="text-emerald-500 mt-0.5 shrink-0" />
                    <p className="text-[11px] text-slate-500 line-clamp-1">{item.prevention_tips[0]}</p>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, icon: Icon, color, link, badge }: {
  label: string; value: number; icon: any; color: string; link?: string; badge?: string;
}) {
  const colorMap: Record<string, string> = {
    slate: "from-slate-800 to-slate-900 border-slate-700/50",
    amber: "from-amber-950/40 to-slate-900 border-amber-700/30",
    emerald: "from-emerald-950/40 to-slate-900 border-emerald-700/30",
    purple: "from-purple-950/40 to-slate-900 border-purple-700/30",
  };
  const iconColorMap: Record<string, string> = {
    slate: "text-slate-400", amber: "text-amber-400", emerald: "text-emerald-400", purple: "text-purple-400",
  };

  const Wrapper = link ? Link : "div";
  const props = link ? { to: link } : {};

  return (
    <Wrapper {...(props as any)}
      className={`bg-gradient-to-br ${colorMap[color]} rounded-2xl p-5 border transition-all hover:scale-[1.02] cursor-pointer`}>
      <div className="flex items-center justify-between mb-3">
        <Icon size={18} className={iconColorMap[color]} />
        {badge && (
          <span className="px-1.5 py-0.5 bg-amber-500/20 text-amber-400 rounded text-[10px] font-semibold animate-pulse">
            {badge}
          </span>
        )}
      </div>
      <p className="text-3xl font-bold text-white">{value}</p>
      <p className="text-xs text-slate-500 mt-1">{label}</p>
    </Wrapper>
  );
}
