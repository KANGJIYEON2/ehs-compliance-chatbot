import { Link } from "react-router-dom";
import { useAuthStore } from "../stores/authStore";
import { Mic, MessageSquareWarning, HelpCircle, Trophy, QrCode, Activity } from "lucide-react";

const actions = [
  { to: "/voice", icon: Mic, label: "음성 보고", desc: "말로 사고 보고", color: "from-red-600 to-red-700" },
  { to: "/report", icon: MessageSquareWarning, label: "익명 제보", desc: "위험 상황 신고", color: "from-amber-600 to-amber-700" },
  { to: "/quiz", icon: HelpCircle, label: "안전 퀴즈", desc: "오늘의 문제 풀기", color: "from-blue-600 to-blue-700" },
  { to: "/ranking", icon: Trophy, label: "안전 랭킹", desc: "팀 순위 확인", color: "from-purple-600 to-purple-700" },
  { to: "/scan", icon: QrCode, label: "QR 스캔", desc: "장비 안전수칙", color: "from-cyan-600 to-cyan-700" },
  { to: "/risk", icon: Activity, label: "위험 예측", desc: "내 구역 위험도", color: "from-emerald-600 to-emerald-700" },
];

export default function HomePage() {
  const user = useAuthStore((s) => s.user);

  return (
    <div className="space-y-6">
      <div>
        <p className="text-slate-500 text-sm">안녕하세요,</p>
        <h1 className="text-xl font-bold text-white">{user?.name}님</h1>
      </div>

      <div className="grid grid-cols-2 gap-3">
        {actions.map(({ to, icon: Icon, label, desc, color }) => (
          <Link key={to} to={to}
            className={`bg-gradient-to-br ${color} rounded-2xl p-4 flex flex-col gap-2 active:scale-95 transition-transform`}>
            <Icon size={24} className="text-white/80" />
            <div>
              <p className="text-white font-semibold text-sm">{label}</p>
              <p className="text-white/60 text-[11px]">{desc}</p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
