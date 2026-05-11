import { useState } from "react";
import { apiFetch } from "../lib/api";
import { QrCode, Globe, Loader2, BookOpen, CheckCircle2 } from "lucide-react";

const LANGS: Record<string, string> = {
  ko: "한국어", vi: "Tiếng Việt", en: "English",
  km: "ភាសាខ្មែរ", ne: "नेपाली", my: "မြန်မာ",
};

export default function SafetyGuidePage() {
  const [guideId, setGuideId] = useState("");
  const [lang, setLang] = useState("ko");
  const [guide, setGuide] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [acked, setAcked] = useState(false);
  const [error, setError] = useState("");

  const loadGuide = async () => {
    if (!guideId.trim()) return;
    setLoading(true);
    setError("");
    setGuide(null);
    setAcked(false);
    try {
      const r = await apiFetch(`/api/safety-guide/${guideId.trim()}?lang=${lang}`);
      if (r.ok) {
        setGuide(await r.json());
      } else {
        setError("안전수칙을 찾을 수 없습니다");
      }
    } catch {
      setError("네트워크 오류");
    }
    setLoading(false);
  };

  const acknowledge = async () => {
    if (!guide) return;
    const r = await apiFetch(`/api/safety-guide/${guide.id}/ack?lang=${lang}`, { method: "POST" });
    if (r.ok) setAcked(true);
  };

  const changeLang = async (newLang: string) => {
    setLang(newLang);
    if (!guide) return;
    setLoading(true);
    try {
      const r = await apiFetch(`/api/safety-guide/${guide.id}?lang=${newLang}`);
      if (r.ok) setGuide(await r.json());
    } catch { /* ignore */ }
    setLoading(false);
  };

  return (
    <div className="space-y-5">
      <h1 className="text-xl font-bold text-white">안전수칙 조회</h1>

      {/* 가이드 ID 입력 (QR 스캔 결과) */}
      <div className="bg-slate-900 rounded-2xl p-4 border border-slate-800 space-y-3">
        <div className="flex items-center gap-2 text-slate-400 text-sm">
          <QrCode size={16} />
          <span>QR코드 스캔 또는 가이드 ID 입력</span>
        </div>
        <input
          value={guideId}
          onChange={(e) => setGuideId(e.target.value)}
          placeholder="가이드 ID"
          className="w-full bg-slate-800 text-white rounded-xl px-4 py-3 border border-slate-700 focus:border-emerald-500 focus:outline-none text-sm"
        />
        <button
          onClick={loadGuide}
          disabled={!guideId.trim() || loading}
          className="w-full py-3 bg-cyan-600 text-white rounded-2xl font-medium disabled:opacity-50 active:scale-95 transition-transform"
        >
          {loading ? <Loader2 size={18} className="animate-spin mx-auto" /> : "조회"}
        </button>
      </div>

      {error && <p className="text-red-400 text-sm text-center">{error}</p>}

      {/* 안전수칙 표시 */}
      {guide && (
        <div className="space-y-4">
          {/* 언어 선택 */}
          <div className="flex items-center gap-2 flex-wrap">
            <Globe size={16} className="text-slate-400" />
            {(guide.available_languages || ["ko"]).map((l: string) => (
              <button
                key={l}
                onClick={() => changeLang(l)}
                className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
                  lang === l
                    ? "bg-cyan-600 text-white"
                    : "bg-slate-800 text-slate-400 border border-slate-700"
                }`}
              >
                {LANGS[l] || l}
              </button>
            ))}
          </div>

          {/* 내용 */}
          <div className="bg-slate-900 rounded-2xl p-5 border border-slate-800">
            <div className="flex items-center gap-2 mb-3">
              <BookOpen size={18} className="text-cyan-400" />
              <p className="text-white font-medium text-sm">
                {guide.target_name || "안전수칙"}
              </p>
            </div>
            <div className="text-slate-300 text-sm leading-relaxed whitespace-pre-wrap">
              {guide.content}
            </div>
          </div>

          {/* 교육 이수 확인 */}
          {acked ? (
            <div className="flex items-center justify-center gap-2 py-3 bg-emerald-900/20 border border-emerald-700/30 rounded-2xl">
              <CheckCircle2 size={18} className="text-emerald-400" />
              <span className="text-emerald-400 font-medium text-sm">교육 이수 완료</span>
            </div>
          ) : (
            <button
              onClick={acknowledge}
              className="w-full py-3 bg-emerald-600 text-white rounded-2xl font-medium active:scale-95 transition-transform"
            >
              이해했습니다 (교육 이수 확인)
            </button>
          )}
        </div>
      )}
    </div>
  );
}
