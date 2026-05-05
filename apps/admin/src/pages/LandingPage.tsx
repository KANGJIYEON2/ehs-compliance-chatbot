import { Link } from "react-router-dom";
import { Navigate } from "react-router-dom";
import { useAuthStore } from "../stores/authStore";
import {
  Shield, AlertTriangle, Brain, Mic, Globe, Trophy,
  ArrowRight, BarChart3, FileText, MessageSquareWarning,
  CheckCircle2, TrendingDown, Scale, Zap,
} from "lucide-react";

export default function LandingPage() {
  const accessToken = useAuthStore((s) => s.accessToken);
  if (accessToken) return <Navigate to="/dashboard" replace />;

  return (
    <div className="min-h-screen bg-white">
      {/* Nav */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-slate-100">
        <div className="max-w-6xl mx-auto px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 bg-emerald-500 rounded-lg flex items-center justify-center">
              <Shield size={16} className="text-white" />
            </div>
            <span className="text-lg font-bold text-slate-900">SafetyAI</span>
          </div>
          <div className="flex items-center gap-3">
            <Link to="/login" className="text-sm text-slate-600 hover:text-slate-900 transition-colors px-3 py-1.5">
              로그인
            </Link>
            <Link to="/signup" className="text-sm bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-1.5 rounded-lg transition-colors">
              무료 시작
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-32 pb-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-emerald-50 text-emerald-700 rounded-full text-xs font-medium mb-6">
            <Zap size={12} /> AI 기반 산업안전 관리 플랫폼
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-slate-900 leading-tight mb-6">
            사고가 터진 후에<br />
            엑셀을 여시나요?
          </h1>
          <p className="text-lg text-slate-500 max-w-2xl mx-auto mb-10 leading-relaxed">
            매년 산업재해로 <span className="text-slate-900 font-semibold">2,000명 이상</span>이 사망합니다.
            대부분의 사업장은 아직도 엑셀과 수기 장부로 안전을 관리합니다.<br />
            <span className="text-emerald-600 font-semibold">SafetyAI</span>는 사고 데이터를 AI로 분석하고, 다음 사고를 예방합니다.
          </p>
          <div className="flex items-center justify-center gap-4">
            <Link to="/signup"
              className="flex items-center gap-2 px-6 py-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-medium transition-all shadow-lg shadow-emerald-600/20">
              무료로 시작하기 <ArrowRight size={16} />
            </Link>
            <a href="#features"
              className="flex items-center gap-2 px-6 py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl font-medium transition-all">
              기능 살펴보기
            </a>
          </div>
        </div>
      </section>

      {/* Problem */}
      <section className="py-20 px-6 bg-slate-50">
        <div className="max-w-5xl mx-auto">
          <p className="text-sm font-semibold text-red-500 mb-3 text-center">현실</p>
          <h2 className="text-3xl font-bold text-slate-900 text-center mb-12">
            지금 이렇게 관리하고 있지 않으신가요?
          </h2>
          <div className="grid md:grid-cols-3 gap-6">
            {[
              { icon: FileText, title: "엑셀로 사고 기록", desc: "파일이 어디 있는지도 모르고, 분석은 불가능. 같은 사고가 반복돼도 모릅니다." },
              { icon: AlertTriangle, title: "사후 대응만 반복", desc: "사고가 터져야 움직이고, 예방은 형식적. 체크리스트는 종이에 체크만." },
              { icon: Scale, title: "법령 확인은 검색 지옥", desc: "산안법, 중대재해처벌법... 어떤 조문이 적용되는지 찾는 데만 반나절." },
            ].map(({ icon: Icon, title, desc }, i) => (
              <div key={i} className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
                <div className="w-10 h-10 bg-red-50 rounded-xl flex items-center justify-center mb-4">
                  <Icon size={20} className="text-red-500" />
                </div>
                <h3 className="text-lg font-semibold text-slate-900 mb-2">{title}</h3>
                <p className="text-sm text-slate-500 leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Solution */}
      <section className="py-20 px-6">
        <div className="max-w-5xl mx-auto">
          <p className="text-sm font-semibold text-emerald-600 mb-3 text-center">솔루션</p>
          <h2 className="text-3xl font-bold text-slate-900 text-center mb-4">
            SafetyAI가 바꿔드립니다
          </h2>
          <p className="text-slate-500 text-center mb-12 max-w-xl mx-auto">
            사고 등록부터 AI 분석, 법령 근거, 예방 조치, 리포트까지 — 하나의 플랫폼에서.
          </p>
          <div className="grid md:grid-cols-2 gap-4">
            {[
              { icon: Brain, color: "purple", title: "AI 원인 분석", desc: "사고를 등록하면 AI가 근본 원인, 기여 요인, 재발 방지 대책을 자동 분석합니다." },
              { icon: CheckCircle2, color: "emerald", title: "예방 체크리스트", desc: "사고 유형별 맞춤 예방 체크리스트를 AI가 생성하고, 조치 완료를 추적합니다." },
              { icon: Scale, color: "amber", title: "법령 근거 자동 매칭", desc: "관련 법조문, 사업주 의무, 위반 시 처벌까지 — 검색 없이 자동으로." },
              { icon: BarChart3, color: "blue", title: "실시간 대시보드", desc: "사고 통계, 유형별 트렌드, 심각도 분포를 차트로 한눈에. 위험 패턴이 보입니다." },
              { icon: TrendingDown, color: "red", title: "위험 예측 스코어링", desc: "공정별 위험도를 가중 점수로 산정. 사고가 터지기 전에 경고합니다." },
              { icon: FileText, color: "cyan", title: "월간 리포트 자동 생성", desc: "매월 사고 현황 + AI 분석 요약을 PDF로 생성. 보고서 작성 시간 제로." },
            ].map(({ icon: Icon, color, title, desc }, i) => {
              const bgColors: Record<string, string> = {
                purple: "bg-purple-50", emerald: "bg-emerald-50", amber: "bg-amber-50",
                blue: "bg-blue-50", red: "bg-red-50", cyan: "bg-cyan-50",
              };
              const iconColors: Record<string, string> = {
                purple: "text-purple-600", emerald: "text-emerald-600", amber: "text-amber-600",
                blue: "text-blue-600", red: "text-red-600", cyan: "text-cyan-600",
              };
              return (
                <div key={i} className="flex gap-4 p-5 rounded-2xl border border-slate-100 hover:border-slate-200 hover:shadow-sm transition-all">
                  <div className={`w-10 h-10 ${bgColors[color]} rounded-xl flex items-center justify-center shrink-0`}>
                    <Icon size={20} className={iconColors[color]} />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-900 mb-1">{title}</h3>
                    <p className="text-sm text-slate-500 leading-relaxed">{desc}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Worker Track */}
      <section id="features" className="py-20 px-6 bg-slate-900">
        <div className="max-w-5xl mx-auto">
          <p className="text-sm font-semibold text-emerald-400 mb-3 text-center">현장 작업자용</p>
          <h2 className="text-3xl font-bold text-white text-center mb-4">
            현장에서 바로 씁니다
          </h2>
          <p className="text-slate-400 text-center mb-12 max-w-xl mx-auto">
            장갑 끼고, 헬멧 쓰고, 손에 기름 묻어있어도. 폼 10개 채우는 대신 한 마디면 됩니다.
          </p>
          <div className="grid md:grid-cols-4 gap-4">
            {[
              { icon: Mic, title: "음성 보고", desc: "말로 보고하면 AI가 자동 분류·등록" },
              { icon: MessageSquareWarning, title: "익명 제보", desc: "신원 비저장. 불이익 걱정 없이 위험 신고" },
              { icon: Globe, title: "다국어 안내", desc: "QR 스캔 → 5개 언어로 안전수칙 표시" },
              { icon: Trophy, title: "안전 게이미피케이션", desc: "퀴즈·포인트·랭킹으로 안전 행동 유도" },
            ].map(({ icon: Icon, title, desc }, i) => (
              <div key={i} className="bg-slate-800 rounded-2xl p-5 border border-slate-700">
                <Icon size={24} className="text-emerald-400 mb-3" />
                <h3 className="font-semibold text-white mb-1 text-sm">{title}</h3>
                <p className="text-xs text-slate-400 leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-slate-900 mb-12">숫자로 보는 SafetyAI</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {[
              { value: "40+", label: "API 엔드포인트" },
              { value: "4", label: "AI 에이전트" },
              { value: "5", label: "다국어 지원" },
              { value: "18", label: "DB 테이블" },
            ].map(({ value, label }, i) => (
              <div key={i}>
                <p className="text-4xl font-bold text-emerald-600">{value}</p>
                <p className="text-sm text-slate-500 mt-1">{label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-6 bg-emerald-600">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            다음 사고를 기다리시겠습니까?
          </h2>
          <p className="text-emerald-100 mb-8 max-w-lg mx-auto">
            SafetyAI로 사고를 기록하고, AI로 분석하고, 다음 사고를 예방하세요.
            무료로 시작할 수 있습니다.
          </p>
          <Link to="/signup"
            className="inline-flex items-center gap-2 px-8 py-3 bg-white text-emerald-700 rounded-xl font-semibold hover:bg-emerald-50 transition-all shadow-lg">
            무료로 시작하기 <ArrowRight size={16} />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-6 border-t border-slate-100">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-emerald-500 rounded-md flex items-center justify-center">
              <Shield size={12} className="text-white" />
            </div>
            <span className="text-sm font-semibold text-slate-700">SafetyAI</span>
          </div>
          <p className="text-xs text-slate-400">AI 기반 산업안전 리스크 관리 플랫폼</p>
        </div>
      </footer>
    </div>
  );
}
