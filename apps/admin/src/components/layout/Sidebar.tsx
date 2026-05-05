import { NavLink } from "react-router-dom";
import { useAuthStore } from "../../stores/authStore";
import {
  LayoutDashboard, AlertTriangle, Mic, MessageSquareWarning,
  Newspaper, HelpCircle, Trophy, Activity,
  Search, Building2, BookOpen, LogOut,
} from "lucide-react";

const navGroups = [
  {
    label: null,
    items: [
      { to: "/", icon: LayoutDashboard, label: "대시보드" },
    ],
  },
  {
    label: "사고 관리",
    items: [
      { to: "/incidents", icon: AlertTriangle, label: "사고 목록" },
      { to: "/voice", icon: Mic, label: "음성 보고" },
      { to: "/reports", icon: MessageSquareWarning, label: "익명 제보" },
    ],
  },
  {
    label: "안전 활동",
    items: [
      { to: "/quiz", icon: HelpCircle, label: "안전 퀴즈" },
      { to: "/ranking", icon: Trophy, label: "안전 랭킹" },
      { to: "/risk", icon: Activity, label: "위험 예측" },
      { to: "/news", icon: Newspaper, label: "안전 뉴스" },
    ],
  },
  {
    label: "설정",
    items: [
      { to: "/safety-guide", icon: BookOpen, label: "다국어 안내" },
      { to: "/chat", icon: Search, label: "법령 검색" },
      { to: "/sites", icon: Building2, label: "사업장 관리" },
    ],
  },
];

export default function Sidebar() {
  const { user, logout } = useAuthStore();

  return (
    <aside className="w-56 bg-slate-900 border-r border-slate-700 flex flex-col h-screen">
      {/* Logo */}
      <div className="p-4 border-b border-slate-700">
        <h1 className="text-lg font-bold text-white">EHS 리스크 관리</h1>
        <p className="text-xs text-slate-400 mt-0.5">관리자 콘솔</p>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto p-3 space-y-4">
        {navGroups.map((group, gi) => (
          <div key={gi}>
            {group.label && (
              <p className="text-[10px] uppercase tracking-wider text-slate-500 px-3 mb-1">{group.label}</p>
            )}
            <div className="space-y-0.5">
              {group.items.map(({ to, icon: Icon, label }) => (
                <NavLink
                  key={to}
                  to={to}
                  end={to === "/"}
                  className={({ isActive }) =>
                    `flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors ${
                      isActive
                        ? "bg-emerald-600/20 text-emerald-400"
                        : "text-slate-300 hover:bg-slate-800"
                    }`
                  }
                >
                  <Icon size={16} />
                  {label}
                </NavLink>
              ))}
            </div>
          </div>
        ))}
      </nav>

      {/* User */}
      <div className="p-3 border-t border-slate-700">
        <div className="flex items-center justify-between px-1">
          <div className="min-w-0">
            <p className="text-sm text-white truncate">{user?.name}</p>
            <p className="text-[11px] text-slate-500 truncate">{user?.email}</p>
          </div>
          <button onClick={logout} className="p-1.5 text-slate-400 hover:text-red-400 transition-colors" title="로그아웃">
            <LogOut size={15} />
          </button>
        </div>
      </div>
    </aside>
  );
}
