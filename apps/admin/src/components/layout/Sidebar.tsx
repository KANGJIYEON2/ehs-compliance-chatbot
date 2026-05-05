import { NavLink } from "react-router-dom";
import { useAuthStore } from "../../stores/authStore";
import {
  LayoutDashboard, AlertTriangle, Mic, MessageSquareWarning,
  Newspaper, HelpCircle, Trophy, Activity,
  Search, Building2, BookOpen, LogOut, Shield,
} from "lucide-react";

const navGroups = [
  {
    label: null,
    items: [
      { to: "/dashboard", icon: LayoutDashboard, label: "대시보드" },
    ],
  },
  {
    label: "사고 관리",
    items: [
      { to: "/dashboard/incidents", icon: AlertTriangle, label: "사고 목록" },
      { to: "/dashboard/voice", icon: Mic, label: "음성 보고" },
      { to: "/dashboard/reports", icon: MessageSquareWarning, label: "익명 제보" },
    ],
  },
  {
    label: "안전 활동",
    items: [
      { to: "/dashboard/quiz", icon: HelpCircle, label: "안전 퀴즈" },
      { to: "/dashboard/ranking", icon: Trophy, label: "안전 랭킹" },
      { to: "/dashboard/risk", icon: Activity, label: "위험 예측" },
      { to: "/dashboard/news", icon: Newspaper, label: "안전 뉴스" },
    ],
  },
  {
    label: "관리",
    items: [
      { to: "/dashboard/safety-guide", icon: BookOpen, label: "다국어 안내" },
      { to: "/dashboard/chat", icon: Search, label: "법령 검색" },
      { to: "/dashboard/sites", icon: Building2, label: "사업장 관리" },
    ],
  },
];

export default function Sidebar() {
  const { user, logout } = useAuthStore();

  return (
    <aside className="w-[220px] bg-slate-900 border-r border-slate-800 flex flex-col h-screen shrink-0">
      {/* Brand */}
      <div className="px-5 py-4 border-b border-slate-800">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 bg-emerald-500 rounded-lg flex items-center justify-center">
            <Shield size={16} className="text-white" />
          </div>
          <div>
            <p className="text-sm font-bold text-white leading-none">SafetyAI</p>
            <p className="text-[10px] text-slate-500 mt-0.5">EHS Risk Management</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto py-3 px-3 space-y-5">
        {navGroups.map((group, gi) => (
          <div key={gi}>
            {group.label && (
              <p className="text-[10px] uppercase tracking-widest text-slate-600 font-semibold px-2 mb-1.5">{group.label}</p>
            )}
            <div className="space-y-0.5">
              {group.items.map(({ to, icon: Icon, label }) => (
                <NavLink
                  key={to} to={to} end={to === "/dashboard"}
                  className={({ isActive }) =>
                    `flex items-center gap-2.5 px-2.5 py-[7px] rounded-lg text-[13px] transition-all duration-150 ${
                      isActive
                        ? "bg-emerald-500/15 text-emerald-400 font-medium"
                        : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
                    }`
                  }
                >
                  <Icon size={15} />
                  {label}
                </NavLink>
              ))}
            </div>
          </div>
        ))}
      </nav>

      {/* User */}
      <div className="px-3 py-3 border-t border-slate-800">
        <div className="flex items-center gap-2.5 px-2">
          <div className="w-7 h-7 rounded-full bg-gradient-to-br from-emerald-500 to-emerald-700 flex items-center justify-center text-[11px] font-bold text-white shrink-0">
            {user?.name?.[0] || "?"}
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-[12px] text-white font-medium truncate">{user?.name}</p>
            <p className="text-[10px] text-slate-500 truncate">{user?.role === "admin" ? "관리자" : user?.role}</p>
          </div>
          <button onClick={logout} className="p-1 text-slate-500 hover:text-red-400 transition-colors" title="로그아웃">
            <LogOut size={14} />
          </button>
        </div>
      </div>
    </aside>
  );
}
