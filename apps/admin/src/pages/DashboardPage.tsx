import { useAuthStore } from "../stores/authStore";

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">
          대시보드
        </h1>
        <p className="text-slate-400 mt-1">
          {user?.name}님, 환영합니다.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
          <p className="text-slate-400 text-sm">이번 달 사고</p>
          <p className="text-3xl font-bold text-white mt-2">-</p>
          <p className="text-slate-500 text-xs mt-1">Phase 2에서 구현</p>
        </div>
        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
          <p className="text-slate-400 text-sm">아차사고</p>
          <p className="text-3xl font-bold text-white mt-2">-</p>
          <p className="text-slate-500 text-xs mt-1">Phase 2에서 구현</p>
        </div>
        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
          <p className="text-slate-400 text-sm">미조치 항목</p>
          <p className="text-3xl font-bold text-white mt-2">-</p>
          <p className="text-slate-500 text-xs mt-1">Phase 2에서 구현</p>
        </div>
      </div>

      <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
        <h2 className="text-lg font-semibold text-white mb-4">빠른 시작 가이드</h2>
        <div className="space-y-3 text-slate-300 text-sm">
          <p>1. 사이드바에서 <span className="text-emerald-400">사업장 관리</span>로 이동하여 사업장을 등록하세요.</p>
          <p>2. 사업장 하위에 부서, 공정, 장비, 작업구역을 설정하세요.</p>
          <p>3. <span className="text-emerald-400">법령 검색</span>에서 기존 RAG 챗봇을 사용할 수 있습니다.</p>
          <p className="text-slate-500 mt-4">사고 등록, 대시보드 통계, AI 분석은 Phase 2-4에서 추가됩니다.</p>
        </div>
      </div>
    </div>
  );
}
