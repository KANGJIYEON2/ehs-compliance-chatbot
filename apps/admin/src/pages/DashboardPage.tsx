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
  Clock, Eye, FileDown, TrendingUp, TrendingDown, Info, Plus,
  Mic, MessageSquareWarning, ClipboardCheck,
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
interface Insight { type: string; title: string; desc: string; }

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
  const [insights, setInsights] = useState<Insight[]>([]);

  useEffect(() => {
    apiFetch("/api/news?limit=4").then(async (r) => { if (r.ok) setNews(await r.json()); setNewsLoading(false); });
    apiFetch("/api/analytics/summary").then(async (r) => { if (r.ok) setSummary(await r.json()); });
    apiFetch("/api/analytics/by-type").then(async (r) => { if (r.ok) setByType(await r.json()); });
    apiFetch("/api/analytics/insights").then(async (r) => { if (r.ok) { const d = await r.json(); setInsights(d.insights || []); } });
  }, []);

  const downloadPdf = async () => {
    setPdfLoading(true);
    const res = await apiFetch("/api/reports/monthly");
    if (res.ok) {
      const blob = await res.blob();
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = `safety_report_${new Date().getFullYear()}_${String(new Date().getMonth() + 1).padStart(2, "0")}.pdf`;
      a.click();
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
  const pending = summary ? (summary.by_status.reported || 0) + (summary.by_status.investigating || 0) : 0;

  return (
    <div className="space-y-6">
      {/* 퀵 액션 바 */}
      <div className="flex items-center gap-3 bg-white rounded-2xl border border-slate-200 shadow-sm p-3">
        <Link to="/dashboard/voice"
          className="flex items-center gap-2 px-5 py-2.5 bg-red-600 hover:bg-red-500 text-white rounded-xl text-sm font-medium transition-colors shadow-sm">
          <Mic size={16} /> 음성 보고
        </Link>
        <Link to="/dashboard/incidents/new"
          className="flex items-center gap-2 px-4 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-sm transition-colors">
          <Plus size={16} /> 사고 등록
        </Link>
        <Link to="/dashboard/tbm"
          className="flex items-center gap-2 px-4 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-sm transition-colors">
          <ClipboardCheck size={16} /> TBM
        </Link>
        <div className="flex-1" />
        <button onClick={downloadPdf} disabled={pdfLoading}
          className="flex items-center gap-2 px-4 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-sm transition-colors disabled:opacity-50">
          <FileDown size={15} /> {pdfLoading ? "생성 중..." : "월간 리포트"}
        </button>
      </div>

      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">대시보드</h1>
          <p className="text-slate-500 text-sm mt-0.5">
            {user?.name}님, {new Date().toLocaleDateString("ko-KR", { month: "long", day: "numeric" })} 기준
          </p>
        </div>
      </div>

      {/* KPI 카드 */}
      {summary && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard label="전체 사고" value={summary.total} icon={AlertTriangle} color="slate" link="/dashboard/incidents" />
          <StatCard label="미조치" value={pending} icon={Clock} color={pending > 0 ? "amber" : "slate"} link="/dashboard/incidents" badge={pending > 0 ? "주의" : undefined} />
          <StatCard label="조치완료" value={summary.by_status.resolved || 0} icon={CheckCircle2} color="emerald" />
          <StatCard label="재발관리" value={summary.by_status.monitoring || 0} icon={Eye} color="purple" />
        </div>
      )}

      {/* AI 인사이트 */}
      {insights.length > 0 && (
        <div className="space-y-2">
          {insights.map((ins, i) => {
            const styles: Record<string, { bg: string; border: string; icon: any; iconColor: string }> = {
              danger: { bg: "bg-red-50", border: "border-red-200", icon: TrendingUp, iconColor: "text-red-500" },
              warning: { bg: "bg-amber-50", border: "border-amber-200", icon: AlertTriangle, iconColor: "text-amber-500" },
              success: { bg: "bg-emerald-50", border: "border-emerald-200", icon: TrendingDown, iconColor: "text-emerald-500" },
              info: { bg: "bg-blue-50", border: "border-blue-200", icon: Info, iconColor: "text-blue-500" },
              empty: { bg: "bg-slate-50", border: "border-slate-200", icon: Info, iconColor: "text-slate-400" },
            };
            const s = styles[ins.type] || styles.info;
            const Icon = s.icon;
            return (
              <div key={i} className={`${s.bg} ${s.border} border rounded-xl px-5 py-3 flex items-start gap-3`}>
                <Icon size={18} className={`${s.iconColor} mt-0.5 shrink-0`} />
                <div>
                  <p className="text-sm font-semibold text-slate-800">{ins.title}</p>
                  <p className="text-xs text-slate-500 mt-0.5">{ins.desc}</p>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* 빈 상태 온보딩 */}
      {summary && summary.total === 0 && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-8">
          <h3 className="text-lg font-bold text-slate-900 mb-2">시작하기</h3>
          <p className="text-sm text-slate-500 mb-6">SafetyAI를 활용하려면 먼저 데이터가 필요합니다. 아래 단계를 따라해보세요.</p>
          <div className="grid md:grid-cols-3 gap-4">
            <Link to="/dashboard/incidents/new" className="flex items-center gap-3 p-4 rounded-xl border border-slate-200 hover:border-emerald-300 hover:bg-emerald-50/50 transition-all group">
              <div className="w-10 h-10 bg-emerald-100 rounded-xl flex items-center justify-center group-hover:bg-emerald-200 transition-colors">
                <Plus size={20} className="text-emerald-600" />
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-800">첫 사고 등록</p>
                <p className="text-xs text-slate-400">아차사고도 등록하세요</p>
              </div>
            </Link>
            <Link to="/dashboard/voice" className="flex items-center gap-3 p-4 rounded-xl border border-slate-200 hover:border-red-300 hover:bg-red-50/50 transition-all group">
              <div className="w-10 h-10 bg-red-100 rounded-xl flex items-center justify-center group-hover:bg-red-200 transition-colors">
                <Mic size={20} className="text-red-600" />
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-800">음성으로 보고</p>
                <p className="text-xs text-slate-400">말로 간편하게</p>
              </div>
            </Link>
            <Link to="/dashboard/sites" className="flex items-center gap-3 p-4 rounded-xl border border-slate-200 hover:border-blue-300 hover:bg-blue-50/50 transition-all group">
              <div className="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center group-hover:bg-blue-200 transition-colors">
                <MessageSquareWarning size={20} className="text-blue-600" />
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-800">사업장 설정</p>
                <p className="text-xs text-slate-400">부서/공정/장비 등록</p>
              </div>
            </Link>
          </div>
        </div>
      )}

      {/* 차트 */}
      {(typeData.length > 0 || sevData.length > 0) && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {typeData.length > 0 && (
            <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
              <h3 className="text-sm font-semibold text-slate-700 mb-4">사고 유형별</h3>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={typeData} barCategoryGap="20%">
                  <XAxis dataKey="name" tick={{ fill: "#64748b", fontSize: 11 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: "#64748b", fontSize: 11 }} axisLine={false} tickLine={false} allowDecimals={false} />
                  <Tooltip contentStyle={{ backgroundColor: "#fff", border: "1px solid #e2e8f0", borderRadius: 12, fontSize: 13 }} cursor={{ fill: "rgba(0,0,0,0.03)" }} />
                  <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                    {typeData.map((_, i) => <Cell key={i} fill={BAR_COLORS[i % BAR_COLORS.length]} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
          {sevData.length > 0 && (
            <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
              <h3 className="text-sm font-semibold text-slate-700 mb-4">심각도 분포</h3>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie data={sevData} cx="50%" cy="50%" innerRadius={55} outerRadius={80} dataKey="value" strokeWidth={0}>
                    {sevData.map((_, i) => <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}
                  </Pie>
                  <Tooltip contentStyle={{ backgroundColor: "#fff", border: "1px solid #e2e8f0", borderRadius: 12, fontSize: 13 }} />
                </PieChart>
              </ResponsiveContainer>
              <div className="flex justify-center gap-4 mt-2">
                {sevData.map((d, i) => (
                  <div key={i} className="flex items-center gap-1.5">
                    <div className="w-2.5 h-2.5 rounded-full" style={{ background: PIE_COLORS[i] }} />
                    <span className="text-[11px] text-slate-500">{d.name} {d.value}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* 뉴스 */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
          <div className="flex items-center gap-2">
            <Newspaper size={16} className="text-emerald-600" />
            <h2 className="text-sm font-semibold text-slate-700">산업안전 뉴스</h2>
          </div>
          <Link to="/dashboard/news" className="flex items-center gap-1 text-xs text-slate-400 hover:text-emerald-600 transition-colors">
            전체 보기 <ArrowRight size={12} />
          </Link>
        </div>
        <div className="divide-y divide-slate-50">
          {newsLoading ? (
            <p className="text-slate-400 text-sm p-6">AI 분석 중...</p>
          ) : news.map((item, idx) => (
            <div key={idx} className="px-6 py-3.5 hover:bg-slate-50/50 transition-colors">
              <div className="flex items-center gap-2 mb-1">
                {item.incident_type && (
                  <span className="px-1.5 py-0.5 bg-emerald-50 text-emerald-700 rounded text-[10px] font-medium">
                    {TYPE_LABELS[item.incident_type] || item.incident_type}
                  </span>
                )}
                <span className="text-[10px] text-slate-400">{item.source} {formatDate(item.pub_date)}</span>
              </div>
              <a href={item.link} target="_blank" rel="noopener noreferrer"
                className="text-[13px] text-slate-700 hover:text-emerald-600 transition-colors leading-snug line-clamp-1 font-medium">
                {item.title}
              </a>
              {item.prevention_tips?.[0] && (
                <div className="flex items-start gap-1.5 mt-1.5">
                  <Shield size={11} className="text-emerald-500 mt-0.5 shrink-0" />
                  <p className="text-[11px] text-slate-400 line-clamp-1">{item.prevention_tips[0]}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, icon: Icon, color, link, badge }: {
  label: string; value: number; icon: any; color: string; link?: string; badge?: string;
}) {
  const borderColors: Record<string, string> = {
    slate: "border-slate-200", amber: "border-amber-200", emerald: "border-emerald-200", purple: "border-purple-200",
  };
  const iconColors: Record<string, string> = {
    slate: "text-slate-500", amber: "text-amber-500", emerald: "text-emerald-500", purple: "text-purple-500",
  };
  const Wrapper = link ? Link : "div";
  const props = link ? { to: link } : {};

  return (
    <Wrapper {...(props as any)}
      className={`bg-white rounded-2xl p-5 border ${borderColors[color]} shadow-sm hover:shadow-md transition-all`}>
      <div className="flex items-center justify-between mb-3">
        <Icon size={18} className={iconColors[color]} />
        {badge && <span className="px-1.5 py-0.5 bg-amber-100 text-amber-700 rounded text-[10px] font-semibold">{badge}</span>}
      </div>
      <p className="text-3xl font-bold text-slate-900">{value}</p>
      <p className="text-xs text-slate-400 mt-1">{label}</p>
    </Wrapper>
  );
}
