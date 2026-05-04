import { NavLink } from "react-router-dom";
import { useAuthStore } from "../../stores/authStore";
import {
  LayoutDashboard,
  Search,
  Building2,
  AlertTriangle,
  Newspaper,
  MessageSquareWarning,
  LogOut,
} from "lucide-react";

const navItems = [
  { to: "/", icon: LayoutDashboard, label: "대시보드" },
  { to: "/incidents", icon: AlertTriangle, label: "사고 관리" },
  { to: "/reports", icon: MessageSquareWarning, label: "익명 제보" },
  { to: "/news", icon: Newspaper, label: "안전 뉴스" },
  { to: "/chat", icon: Search, label: "법령 검색" },
  { to: "/sites", icon: Building2, label: "사업장 관리" },
];

export default function Sidebar() {
  const { user, logout } = useAuthStore();

  return (
    <aside className="w-60 bg-slate-900 border-r border-slate-700 flex flex-col h-screen">
      {/* Logo */}
      <div className="p-4 border-b border-slate-700">
        <h1 className="text-lg font-bold text-white">EHS 리스크 관리</h1>
        <p className="text-xs text-slate-400 mt-1">관리자 콘솔</p>
      </div>

      {/* Nav */}
      <nav className="flex-1 p-3 space-y-1">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                isActive
                  ? "bg-emerald-600/20 text-emerald-400"
                  : "text-slate-300 hover:bg-slate-800"
              }`
            }
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* User */}
      <div className="p-4 border-t border-slate-700">
        <div className="flex items-center justify-between">
          <div className="min-w-0">
            <p className="text-sm text-white truncate">{user?.name}</p>
            <p className="text-xs text-slate-400 truncate">{user?.email}</p>
          </div>
          <button
            onClick={logout}
            className="p-2 text-slate-400 hover:text-red-400 transition-colors"
            title="로그아웃"
          >
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </aside>
  );
}
