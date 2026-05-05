import { NavLink } from "react-router-dom";
import { Home, Mic, MessageSquareWarning, HelpCircle, User } from "lucide-react";

const tabs = [
  { to: "/", icon: Home, label: "홈" },
  { to: "/voice", icon: Mic, label: "보고" },
  { to: "/report", icon: MessageSquareWarning, label: "제보" },
  { to: "/quiz", icon: HelpCircle, label: "퀴즈" },
  { to: "/my", icon: User, label: "MY" },
];

export default function BottomNav() {
  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-slate-900 border-t border-slate-800 safe-bottom z-50">
      <div className="flex items-center justify-around max-w-lg mx-auto">
        {tabs.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to} to={to} end={to === "/"}
            className={({ isActive }) =>
              `flex flex-col items-center py-2 px-3 transition-colors ${
                isActive ? "text-emerald-400" : "text-slate-500"
              }`
            }
          >
            <Icon size={20} />
            <span className="text-[10px] mt-0.5">{label}</span>
          </NavLink>
        ))}
      </div>
    </nav>
  );
}
